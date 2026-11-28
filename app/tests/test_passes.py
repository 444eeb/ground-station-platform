"""Unit tests for pass prediction. Uses a fixed TLE and start time so results are repeatable."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ground_station.passes import find_passes, load_satellite, tle_epoch

FIXTURE = Path(__file__).parent / "fixtures_iss.tle"
START = datetime(2008, 9, 20, 12, 0, tzinfo=UTC)  # close to the fixture TLE's epoch
LONDON = (51.5072, -0.1276)


@pytest.fixture(scope="module")
def iss():
    return load_satellite(FIXTURE)


def test_loads_iss_from_tle(iss):
    assert iss.name == "ISS (ZARYA)"
    assert tle_epoch(iss).year == 2008


def test_london_gets_passes_in_24_hours(iss):
    passes = find_passes(iss, *LONDON, START, hours=24)
    assert len(passes) >= 1


def test_each_pass_is_in_order_and_inside_window(iss):
    passes = find_passes(iss, *LONDON, START, hours=24)
    for p in passes:
        assert START <= p.rise < p.culminate < p.set <= START + timedelta(hours=24)
        assert 10 <= p.max_elevation_deg <= 90
        assert p.set - p.rise < timedelta(minutes=15)  # ISS passes are short


def test_higher_minimum_elevation_gives_fewer_or_equal_passes(iss):
    low = find_passes(iss, *LONDON, START, hours=48, min_elevation_deg=10)
    high = find_passes(iss, *LONDON, START, hours=48, min_elevation_deg=45)
    assert len(high) <= len(low)


def test_no_passes_near_south_pole(iss):
    # ISS orbit is inclined 51.6 degrees, so it never gets high above the poles.
    assert find_passes(iss, -89.0, 0.0, START, hours=24, min_elevation_deg=10) == []


def test_naive_start_time_rejected(iss):
    with pytest.raises(ValueError):
        find_passes(iss, *LONDON, datetime(2008, 9, 20), hours=1)


def test_bad_tle_file_rejected(tmp_path):
    bad = tmp_path / "bad.tle"
    bad.write_text("only one line\n")
    with pytest.raises(ValueError):
        load_satellite(bad)
