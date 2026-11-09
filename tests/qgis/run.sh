#!/usr/bin/env bash
# Run the QGIS integration tests (tests/qgis) in Docker.
#
#   tests/qgis/run.sh [3|4|IMAGE] [pytest args...]
#
#   3  -> qgis/qgis:3.44 (LTR, Qt5)    4 -> qgis/qgis:4.2 (Qt6, default)
#   IMAGE: any qgis/qgis image, e.g. qgis/qgis:latest
#
# The images are linux/amd64 only; on Apple silicon they run emulated (slow).
# Override with DOCKER_PLATFORM=... . The checkout is mounted read-only and
# copied to /work in the container (pytest-qgis writes its QGIS profile there).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QGIS="${1:-4}"
shift || true

case "$QGIS" in
  3) IMAGE="qgis/qgis:3.44" ;;
  4) IMAGE="qgis/qgis:4.2" ;;
  *) IMAGE="$QGIS" ;;
esac
TAG="geosearch-qgis-test:${IMAGE##*:}"
PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"

echo "== QGIS tests in $IMAGE ($TAG, $PLATFORM)"
docker build --quiet --platform "$PLATFORM" --build-arg "QGIS_IMAGE=$IMAGE" \
  -t "$TAG" -f "$ROOT/tests/qgis/Dockerfile" "$ROOT/tests/qgis" >/dev/null

TTY=()
[ -t 1 ] && TTY=(-t)
exec docker run --rm ${TTY[@]+"${TTY[@]}"} --platform "$PLATFORM" \
  -v "$ROOT:/src:ro" "$TAG" bash -c '
    mkdir -p /work && cp -R /src/pyproject.toml /src/src /src/tests /work/ &&
    cd /work && exec python3 -m pytest tests/qgis -p no:cacheprovider "$@"' run-tests "$@"
