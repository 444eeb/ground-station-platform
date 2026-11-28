"""Shared test setup.

Point the app at the fixed test TLE *before* it is imported, so the API tests
don't depend on whatever orbit data is currently bundled in the app.
"""

import os
from pathlib import Path

os.environ["TLE_PATH"] = str(Path(__file__).parent / "fixtures_iss.tle")
