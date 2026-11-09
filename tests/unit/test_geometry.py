from bifrost_fixtures import load, result_for

from geosearch_dk.bifrost import (
    PROJECT,
    SEARCH,
    geometry_from_response,
    geometry_request,
    row_geometry,
)


def _geometry_case(name):
    data = load(name)
    row = result_for(name).rows[data["geometry"]["row_index"]]
    return row, data["geometry"]["attempts"]


def _replay(row, attempts):
    """Run the documented retry loop against the recorded exchanges."""
    geojson, attempt = None, 0
    request = geometry_request(row, attempt)
    while geojson is None and request:
        recorded = attempts[attempt]
        assert (request.endpoint, request.body) == (
            recorded["endpoint"],
            recorded["body"],
        )
        geojson = geometry_from_response(row, recorded["response"])
        attempt += 1
        request = geometry_request(row, attempt)
    return geojson


def test_entrance_geometry_via_project():
    row, attempts = _geometry_case("adr_vangebovej_71")
    request = geometry_request(row)
    assert request.endpoint == PROJECT
    assert request.body == {
        "input": row["ref"],
        "target": "entrance",
        "limit": 1,
        "geometry": True,
    }
    assert geometry_request(row, 1) is None
    assert _replay(row, attempts)["type"] == "Point"


def test_ejendom_geometry_via_project():
    row, attempts = _geometry_case("mat_3kg_soell")
    assert geometry_request(row).body["target"] == "ejendom"
    assert _replay(row, attempts)["type"] in ("Polygon", "MultiPolygon")


def test_stednavn_geometry_via_search():
    row, attempts = _geometry_case("ste_skodsborg")
    request = geometry_request(row)
    assert request.endpoint == SEARCH
    assert request.body == {
        "input": "Skodsborg",
        "target": "stednavn",
        "limit": 10,
        "geometry": True,
    }
    assert geometry_request(row, 1).body["limit"] == 100
    assert geometry_request(row, 2) is None
    assert _replay(row, attempts)["type"] in ("Polygon", "MultiPolygon")


def test_stednavn_geometry_needs_the_same_ref():
    row = {
        "key": "ste",
        "ref": {"kind": "stednavn", "id": "a"},
        "result": "X",
        "text": "X",
    }
    other = {
        "matches": [
            {
                "ref": {"kind": "stednavn", "id": "b"},
                "geometry": {"geojson": {"type": "Point"}},
            }
        ]
    }
    assert geometry_from_response(row, other) is None


def test_retired_rows_ask_for_their_lifecycle():
    row = {"key": "udg", "ref": {"kind": "ejendom", "id": "e"}, "lifecycle": "retired"}
    assert geometry_request(row).body["lifecycle"] == ["retired"]
    row["lifecycle"] = "current"
    assert "lifecycle" not in geometry_request(row).body


def test_row_geometry_falls_back_to_point():
    point = {"type": "Point", "coordinates": [1.0, 2.0]}
    assert row_geometry({"geometry": None, "point": point}) == point
    poly = {"type": "Polygon", "coordinates": []}
    assert row_geometry({"geometry": poly, "point": point}) == poly
