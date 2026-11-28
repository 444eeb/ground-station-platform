"""Satellite pass prediction using Skyfield.

A "pass" is one trip of the satellite across the sky: it rises above a minimum
elevation, reaches its highest point (culmination), then sets again.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from skyfield.api import EarthSatellite, load, wgs84

# Skyfield ships the time-scale data it needs, so no network access is required.
TIMESCALE = load.timescale(builtin=True)

DEFAULT_TLE_PATH = Path(__file__).parent / "data" / "iss.tle"


@dataclass(frozen=True)
class Pass:
    rise: datetime
    culminate: datetime
    set: datetime
    max_elevation_deg: float


def load_satellite(tle_path: Path = DEFAULT_TLE_PATH) -> EarthSatellite:
    """Load a satellite from a 3-line TLE file (name, line 1, line 2)."""
    lines = [line.strip() for line in tle_path.read_text().splitlines() if line.strip()]
    if len(lines) != 3:
        raise ValueError(f"{tle_path} must contain exactly 3 non-empty lines (name + 2 TLE lines)")
    name, line1, line2 = lines
    return EarthSatellite(line1, line2, name, TIMESCALE)


def tle_epoch(satellite: EarthSatellite) -> datetime:
    """When the orbit data was measured. Predictions get less accurate as it ages."""
    return satellite.epoch.utc_datetime()


def find_passes(
    satellite: EarthSatellite,
    lat: float,
    lon: float,
    start: datetime,
    hours: float,
    min_elevation_deg: float = 10.0,
) -> list[Pass]:
    """Return complete passes (rise, culminate and set) within the time window."""
    if start.tzinfo is None:
        raise ValueError("start must be timezone-aware")

    observer = wgs84.latlon(lat, lon)
    t0 = TIMESCALE.from_datetime(start)
    t1 = TIMESCALE.tt_jd(t0.tt + hours / 24.0)
    times, events = satellite.find_events(observer, t0, t1, altitude_degrees=min_elevation_deg)

    passes: list[Pass] = []
    current: dict[int, object] = {}
    for t, event in zip(times, events, strict=True):
        if event == 0:  # rise: start a new pass
            current = {0: t}
        elif event == 1 and 0 in current:  # culmination
            current[1] = t
        elif event == 2 and 1 in current:  # set: pass complete
            culminate_t = current[1]
            alt, _, _ = (satellite - observer).at(culminate_t).altaz()
            passes.append(
                Pass(
                    rise=current[0].utc_datetime(),
                    culminate=culminate_t.utc_datetime(),
                    set=t.utc_datetime(),
                    max_elevation_deg=round(float(alt.degrees), 1),
                )
            )
            current = {}
    return passes


def now_utc() -> datetime:
    return datetime.now(UTC)
