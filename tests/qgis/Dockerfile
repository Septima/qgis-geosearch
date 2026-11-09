# QGIS image with the test dependencies, used by `make test-qgis`.
#   docker build --build-arg QGIS_IMAGE=qgis/qgis:4.2 -f tests/qgis/Dockerfile tests/qgis
ARG QGIS_IMAGE=qgis/qgis:3.44
FROM ${QGIS_IMAGE}
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt
ENV QT_QPA_PLATFORM=offscreen \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
