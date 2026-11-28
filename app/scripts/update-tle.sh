#!/usr/bin/env bash
# Download the latest ISS orbit data (TLE) from CelesTrak into the app.
# CelesTrak updates this data a few times a day; please don't run this more than once every 2 hours.


DEST="$(dirname "$0")/../src/ground_station/data/iss.tle"
URL="https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

curl -fsS "$URL" -o "$TMP"

# Basic sanity check: 3 lines, with the two TLE lines starting "1 " and "2 ".
if [[ "$(grep -c . "$TMP")" -ne 3 ]] || ! sed -n '2p' "$TMP" | grep -q '^1 ' || ! sed -n '3p' "$TMP" | grep -q '^2 '; then
  echo "Downloaded data doesn't look like a TLE; keeping the old file." >&2
  cat "$TMP" >&2
  exit 1
fi

# CelesTrak uses Windows line endings and pads the name line with spaces; strip both.
tr -d '\r' < "$TMP" | sed 's/[[:space:]]*$//' > "$DEST"
echo "Updated $DEST:"
cat "$DEST"
