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
