"""FastAPI application for the Ground Station API."""

import os
import time
from pathlib import Path

from fastapi import FastAPI, Query, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from ground_station import __version__
from ground_station.passes import DEFAULT_TLE_PATH, find_passes, load_satellite, now_utc, tle_epoch

TLE_PATH = Path(os.environ.get("TLE_PATH", str(DEFAULT_TLE_PATH)))
SATELLITE = load_satellite(TLE_PATH)
STALE_AFTER_DAYS = 14

REQUESTS = Counter("gs_http_requests_total", "HTTP requests handled", ["method", "path", "status"])
LATENCY = Histogram("gs_http_request_duration_seconds", "Request latency in seconds", ["path"])
PASSES_RETURNED = Counter("gs_passes_returned_total", "Number of passes returned to callers")

app = FastAPI(title="Ground Station API", version=__version__)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    # Use the route template (e.g. /passes), not the raw URL, to keep metric labels few.
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    if path != "/metrics":
        REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        LATENCY.labels(path).observe(time.perf_counter() - start)
    return response


@app.get("/")
def info() -> dict:
    return {
        "service": "ground-station-api",
        "version": __version__,
        "satellite": SATELLITE.name,
        "endpoints": ["/passes", "/healthz", "/metrics", "/docs"],
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/passes")
def passes(
    lat: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude in degrees"),
    hours: float = Query(24, gt=0, le=72, description="How far ahead to look"),
    min_elevation: float = Query(10, ge=0, le=90, description="Minimum elevation in degrees"),
) -> dict:
    start = now_utc()
    found = find_passes(SATELLITE, lat, lon, start, hours, min_elevation)
    PASSES_RETURNED.inc(len(found))
    epoch = tle_epoch(SATELLITE)
    age_days = (start - epoch).total_seconds() / 86400
    return {
        "satellite": SATELLITE.name,
        "observer": {"lat": lat, "lon": lon},
        "window": {"start": start.isoformat(), "hours": hours, "min_elevation_deg": min_elevation},
        "tle_epoch": epoch.isoformat(),
        "tle_age_days": round(age_days, 1),
        # Orbit data older than about two weeks gives noticeably less accurate times.
        "tle_stale": abs(age_days) > STALE_AFTER_DAYS,
        "count": len(found),
        "passes": [
            {
                "rise": p.rise.isoformat(),
                "culminate": p.culminate.isoformat(),
                "set": p.set.isoformat(),
                "max_elevation_deg": p.max_elevation_deg,
            }
            for p in found
        ],
    }
