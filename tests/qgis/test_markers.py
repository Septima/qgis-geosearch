"""Marking a hit on the map: point marker and rubber bands, in the canvas CRS."""

import json

import pytest
from osgeo import ogr
from qgis.core import QgsCoordinateReferenceSystem, QgsGeometry, QgsProject
from qgis.gui import QgsRubberBand, QgsVertexMarker

import bifrost_cases as bc
from geosearch_dk.bifrost import geometry_from_response


@pytest.fixture
def box(plugin, qgis_canvas):
    qgis_canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(25832))
    yield plugin.searchwidget
    plugin.searchwidget.clearMarkerGeom()


def _items(canvas, cls):
    return [i for i in canvas.scene().items() if isinstance(i, cls)]


def test_point_marker(box, qgis_canvas):
    box.setMarkerGeom(QgsGeometry.fromWkt("POINT (723000 6175000)"))
    assert len(box.markers) == 1
    assert isinstance(box.markers[0], QgsVertexMarker)
    assert box.markers[0] in _items(qgis_canvas, QgsVertexMarker)
    box.clearMarkerGeom()
    assert box.markers == []
    assert _items(qgis_canvas, QgsVertexMarker) == []


def test_multipolygon_gets_a_rubber_band_per_part(box, qgis_canvas):
    geom = QgsGeometry.fromWkt(
        "MULTIPOLYGON (((0 0, 10 0, 10 10, 0 0)), ((20 20, 30 20, 30 30, 20 20)))"
    )
    box.setMarkerGeom(geom)
    assert len(box.markers) == 2
    assert all(isinstance(m, QgsRubberBand) for m in box.markers)
    box.setMarkerGeom(QgsGeometry.fromWkt("LINESTRING (0 0, 5 5)"))
    assert len(box.markers) == 1


def test_crs_transform_follows_the_canvas(box, qgis_canvas):
    qgis_canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(4326))
    box.setupCrsTransform()
    geom = QgsGeometry.fromWkt("POINT (723000 6175000)")
    geom.transform(box.crsTransform)
    p = geom.asPoint()
    assert 12 < p.x() < 13 and 55 < p.y() < 56


@pytest.mark.parametrize(
    "case_id,kind",
    [("adr-noeddebogade-1-st-th", "Point"), ("pos-8000", "Polygon"), ("kom-101", "Polygon")],
)
def test_recorded_bifrost_geometry_can_be_marked(box, case_id, kind):
    """Bifrost's GeoJSON (EPSG:25832) converts to a QGIS geometry the way the plugin does it."""
    fixture = bc.load_case_fixture(case_id)
    if fixture is None or not fixture.get("geometry"):
        pytest.skip("no recorded geometry for %s" % case_id)
    recorded = fixture["geometry"]
    geojson = geometry_from_response({"ref": recorded["ref"]}, recorded["attempts"][-1]["response"])
    assert geojson and geojson["type"] == recorded["type"]
    geom = QgsGeometry.fromWkt(ogr.CreateGeometryFromJson(json.dumps(geojson)).ExportToWkt())
    assert not geom.isNull()
    assert kind.lower() in geom.asWkt().lower()
    box.setMarkerGeom(geom)
    assert box.markers
