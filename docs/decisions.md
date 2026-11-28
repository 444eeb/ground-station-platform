# Decisions

Short notes on why I chose one option over another.

## Docker Engine inside WSL2 instead of Docker Desktop
I installed Docker Engine directly in Ubuntu from Docker's official apt
repository. It uses less memory than Docker Desktop (which runs its own VM),
and it is set up the same way as on a real Linux server, so I also practised
managing it as a systemd service.

## Ubuntu 26.04 LTS
I checked the current releases before installing and chose the newest LTS.
I confirmed that Docker and HashiCorp both publish packages for it first.

## Verified downloads
For tools installed as single binaries (kubectl, kind, gitleaks) I verified
each download against the publisher's SHA-256 checksum before installing it.
Tools from apt repositories are verified automatically with the publisher's
GPG signing key.

## Secret scanning in two layers
Locally, a pre-commit hook runs gitleaks on every commit. On GitHub, secret
scanning with push protection is enabled as a second layer.

## uv for Python dependencies
uv replaces pip and venv and writes a lock file (uv.lock) that pins every
package version. Docker and CI install from the lock file, so builds are
repeatable.

## Multi-stage Docker image, non-root user
The first stage installs dependencies; the second copies only the finished
virtual environment into a clean python:3.14-slim image. The final image has
no source tree, tests or build tools, and runs as an unprivileged user (uid
999), which limits the damage if the app were compromised. The container
listens on $PORT (default 8080) because Cloud Run sets that variable.

## Orbit data baked into the image
The ISS TLE is downloaded by a script and included at build time, so the
service works without calling an external API. The trade-off is that the data
ages: the API reports `tle_age_days` and `tle_stale` (true after 14 days), and
the image needs rebuilding to refresh it. Automating that is a possible
later improvement.

## Deterministic tests
Tests use a fixed TLE and a frozen clock instead of live data, so they give
the same result every run and don't depend on the network.
EOF#

cat >> docs/build-log.md <<'EOF'

## Stage 2 — Ground Station API and Docker (28 Nov 2026)

**What I did**
- Added a FastAPI service that predicts ISS passes over a latitude/longitude
  using Skyfield, with `/passes`, `/healthz` and Prometheus `/metrics`.
  The application code was written with AI assistance; I reviewed it, ran
  it and can explain how it works.
- Wrote a script that downloads current ISS orbit data (TLE) from CelesTrak
  and checks it is valid before replacing the old file.
- Managed dependencies with uv and a lock file; 16 pytest tests pass, and
  ruff lint and format checks are clean.
- Built a multi-stage Docker image (331 MB) that runs as a non-root user and
  includes a HEALTHCHECK. I confirmed the container reported "healthy",
  that `id` showed uid 999 rather than root, and that /app contained only
  the virtual environment.

**What went wrong**
- The bundled orbit data was a 2008 placeholder, which gives meaningless
  predictions. I replaced it with current data and the API now reports how
  old the data is.

**What I learned**
- TLE orbit data goes out of date within days, so data freshness has to be
  part of the design.
- The container logs showed health checks from 127.0.0.1 (inside the
  container) and my request from 172.17.0.1 (Docker's bridge gateway).

## uv for Python dependencies
uv replaces pip and venv and writes a lock file (uv.lock) that pins every
package version. Docker and CI install from the lock file, so builds are
repeatable.

## Multi-stage Docker image, non-root user
The first stage installs dependencies; the second copies only the finished
virtual environment into a clean python:3.14-slim image. The final image has
no source tree, tests or build tools, and runs as an unprivileged user (uid
999), which limits the damage if the app were compromised. The container
listens on $PORT (default 8080) because Cloud Run sets that variable.

## Orbit data baked into the image
The ISS TLE is downloaded by a script and included at build time, so the
service works without calling an external API. The trade-off is that the data
ages: the API reports `tle_age_days` and `tle_stale` (true after 14 days), and
the image needs rebuilding to refresh it. Automating that is a possible
later improvement.

## Deterministic tests
Tests use a fixed TLE and a frozen clock instead of live data, so they give
the same result every run and don't depend on the network.

## uv for Python dependencies
uv replaces pip and venv and writes a lock file (uv.lock) that pins every
package version. Docker and CI install from the lock file, so builds are
repeatable.

## Multi-stage Docker image, non-root user
The first stage installs dependencies; the second copies only the finished
virtual environment into a clean python:3.14-slim image. The final image has
no source tree, tests or build tools, and runs as an unprivileged user (uid
999), which limits the damage if the app were compromised. The container
listens on $PORT (default 8080) because Cloud Run sets that variable.

## Orbit data baked into the image
The ISS TLE is downloaded by a script and included at build time, so the
service works without calling an external API. The trade-off is that the data
ages: the API reports `tle_age_days` and `tle_stale` (true after 14 days), and
the image needs rebuilding to refresh it. Automating that is a possible
later improvement.

## Deterministic tests
Tests use a fixed TLE and a frozen clock instead of live data, so they give
the same result every run and don't depend on the network.
