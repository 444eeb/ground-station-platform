"""API tests using FastAPI's test client (no real server needed)."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

import ground_station.main as main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def fixed_now(monkeypatch):
    # Freeze "now" near the bundled TLE's epoch so results are repeatable.
    monkeypatch.setattr(main, "now_utc", lambda: datetime(2008, 9, 20, 12, 0, tzinfo=UTC))


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_info_lists_endpoints():
    body = client.get("/").json()
    assert body["service"] == "ground-station-api"
    assert "/passes" in body["endpoints"]


def test_passes_for_london():
    r = client.get("/passes", params={"lat": 51.5072, "lon": -0.1276, "hours": 24})
    assert r.status_code == 200
    body = r.json()
    assert body["satellite"] == "ISS (ZARYA)"
    assert body["count"] == len(body["passes"]) >= 1
    assert {"rise", "culminate", "set", "max_elevation_deg"} <= body["passes"][0].keys()
    assert body["tle_stale"] is False  # "now" is frozen close to the TLE epoch


@pytest.mark.parametrize(
    "params",
    [
        {"lat": 91, "lon": 0},
        {"lat": 0, "lon": 181},
        {"lat": 0, "lon": 0, "hours": 0},
        {"lat": 0, "lon": 0, "hours": 500},
        {"lon": 0},
    ],
)
def test_invalid_input_rejected(params):
    assert client.get("/passes", params=params).status_code == 422


def test_metrics_exposed_and_counting():
    client.get("/healthz")
    text = client.get("/metrics").text
    assert "gs_http_requests_total" in text
    assert 'path="/healthz"' in text
