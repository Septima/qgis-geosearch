import pytest
from bifrost_fixtures import fixture_names, load, plan_for, result_for

from geosearch_dk.bifrost import (
    STATUS_ERROR,
    STATUS_OK,
    TYPES,
    build_requests,
    collect_rows,
    dedupe,
    error_row,
    matches_term,
    normalize,
    plan_search,
    rank_rows,
    rank_types,
    types_by_key,
)

BY_KEY = types_by_key()
ROW_KEYS = {
    "key",
    "title",
    "status",
    "text",
    "kind",
    "ref",
    "point",
    "geometry",
    "lifecycle",
}


def texts(rows, key=None):
    return [r["text"] for r in rows if key is None or r["key"] == key]


@pytest.mark.parametrize("name", fixture_names())
def test_recorded_requests_are_still_what_the_core_builds(name):
    data = load(name)
    plan = plan_for(data)
    recorded = [
        (ex["endpoint"], ex["body"], tuple(ex["keys"])) for ex in data["requests"]
    ]
    assert [tuple(r) for r in plan.requests] == recorded
    assert all(ex["status"] == 200 for ex in data["requests"])


@pytest.mark.parametrize("name", fixture_names())
def test_rows_satisfy_the_contract(name):
    plan = plan_for(load(name))
    rows = result_for(name).rows
    for row in rows:
        assert ROW_KEYS <= set(row)
        assert row["status"] == STATUS_OK
        assert row["key"] in plan.keys
        assert row["text"]
        assert row["ref"]["kind"] == row["kind"]
        assert row["point"]["type"] == "Point" and len(row["point"]["coordinates"]) == 2
        assert row["geometry"] is None
    for key in plan.keys:
        assert len([r for r in rows if r["key"] == key]) <= plan.limits[key]
    ids = [(r["kind"], r["ref"]["id"]) for r in rows]
    assert len(ids) == len(set(ids))
    keys = [r["key"] for r in rows]
    order = [k for i, k in enumerate(keys) if k not in keys[:i]]
    assert keys == sorted(keys, key=order.index)
    groups = [(k, [r for r in rows if r["key"] == k]) for k in plan.keys]
    ranked = [k for k, g in rank_types(groups, plan.term) if g]
    assert order == ranked


def test_single_address_unit_becomes_husnummer():
    data = load("adr_vangebovej_71")
    raw = data["requests"][0]["response"]["matches"][0]
    assert raw["ref"]["kind"] == "unit" and "entrance" in raw["refs"]
    row = result_for("adr_vangebovej_71").rows[0]
    assert row["text"] == "Vangebovej 71, Søllerød, 2840 Holte"
    assert row["kind"] == "entrance"
    assert row["ref"] == {"kind": "entrance", "id": raw["refs"]["entrance"]}


def test_apartments_are_shown_as_units():
    rows = result_for("adr_noeddebogade_1_st_th").rows
    assert rows[0]["text"] == "Nøddebogade 1, st. th, 2200 København N"
    assert rows[0]["kind"] == "unit"


def test_resolve_keeps_streets_and_drops_other_kinds():
    adr = BY_KEY["adr"]
    street = {
        "ref": {"kind": "street", "id": "s"},
        "refs": {"street": "s"},
        "result": "Nørrebrogade, 2200 København N",
        "components": {
            "street": "Nørrebrogade",
            "postcodes": [{"postcode": "2200", "city": "København N"}],
        },
    }
    row = normalize(street, adr)
    assert row["kind"] == "street" and row["ref"] == {"kind": "street", "id": "s"}
    assert row["text"] == "Nørrebrogade (2200 København N)"
    assert normalize(street, adr._replace(accept_streets=False)) is None
    postcode = {"ref": {"kind": "postcode", "id": "p"}, "result": "Aarhus C"}
    assert normalize(postcode, adr) is None
    no_units = adr._replace(accept_units=False)
    apartment = {
        "ref": {"kind": "unit", "id": "u"},
        "refs": {"unit": "u", "entrance": "e"},
        "components": {"floor": "1"},
        "result": "X 1, 1., 1000 By",
    }
    assert normalize(apartment, no_units) is None
    assert normalize(apartment, adr)["kind"] == "unit"


def test_search_drops_other_kinds():
    assert normalize({"ref": {"kind": "city", "id": "c"}}, BY_KEY["pos"]) is None


def test_all_types_aarhus():
    rows = result_for("all_aarhus").rows
    assert texts(rows, "pos")[:3] == ["8000 Aarhus C", "8200 Aarhus N", "8210 Aarhus V"]
    assert texts(rows, "kom")[0] == "Aarhus Kommune"
    assert "Aarhus Nordkredsen" in texts(rows, "ops")
    assert texts(rows, "ste")[1] == "Aarhus (bebyggelse, Aarhus)"


def test_postcode_prefix():
    assert texts(result_for("pos_8000").rows) == ["8000 Aarhus C"]


def test_kommune_prefix_without_space():
    assert texts(result_for("kom_koebenhavn").rows)[0] == "Københavns Kommune"


def test_mat_finds_the_exact_matrikel_first():
    rows = result_for("mat_3kg_soell").rows
    assert rows[0]["text"] == "3kg, Søllerød By, Søllerød"
    assert rows[0]["kind"] == "ejendom"
    assert all(r["key"] == "mat" for r in rows)


def test_proposed_types():
    assert texts(result_for("proposed_skodsborgvej").rows)[:2] == [
        "Skodsborgvej (2830 Virum, 2840 Holte, 2850 Nærum, 2942 Skodsborg)",
        "Skodsborgvej (9270 Klarup)",
    ]
    assert texts(result_for("proposed_lyngby_retskreds").rows) == ["Retten i Lyngby"]
    assert texts(result_for("proposed_vor_frue").rows)[0] == "Vor Frue sogn (Roskilde)"
    udg = result_for("proposed_1an_gentofte_udgaaet").rows[0]
    assert (udg["text"], udg["lifecycle"]) == ("1an, Gentofte (udgået)", "retired")


def _ejendom(nr, score=1.0):
    return {
        "ref": {"kind": "ejendom", "id": nr},
        "refs": {"ejendom": nr},
        "result": nr + ", Søllerød By, Søllerød",
        "components": {"matrikelnummer": nr},
        "meta": {"score": score},
        "point": {"type": "Point", "coordinates": [1.0, 2.0]},
    }


def test_rank_rows_puts_exact_matrikelnummer_first():
    rows = [
        normalize(_ejendom(nr), BY_KEY["mat"]) for nr in ("2kg", "3g", "3kg", "20a")
    ]
    assert [r["components"]["matrikelnummer"] for r in rank_rows(rows, "3KG søll")] == [
        "3kg",
        "2kg",
        "3g",
        "20a",
    ]
    assert rank_rows(rows, "20 a, søll")[0]["components"]["matrikelnummer"] == "20a"
    assert rank_rows(rows, "søllerød") == rows


def _row(key, text):
    return {"key": key, "status": STATUS_OK, "text": text}


def test_matches_term_needs_every_word_to_start_a_word():
    assert matches_term(_row("reg", "Region Hovedstaden"), "hovedstaden")
    assert matches_term(_row("reg", "Region Hovedstaden"), "region hoved")
    assert matches_term(_row("pos", "8000 Aarhus C"), "8000")
    assert not matches_term(_row("pos", "8732 Hovedgård"), "hovedstaden")
    assert not matches_term(_row("mat", "1a, Hovedejerlavet, Stadil"), "hovedstaden")
    assert not matches_term(_row("reg", "Region Hovedstaden"), "region sjælland")
    assert not matches_term(_row("reg", "Region Hovedstaden"), "")
    assert not matches_term(error_row(BY_KEY["reg"]), "regioner")


def test_rank_types_puts_types_with_only_fuzzy_hits_last():
    groups = [
        ("ste", [_row("ste", "Region Hovedstaden (bygning, Hillerød)")]),
        ("pos", [_row("pos", "8732 Hovedgård")]),
        ("mat", [error_row(BY_KEY["mat"])]),
        ("kom", [_row("kom", "Holbæk Kommune")]),
        ("reg", [_row("reg", "Region Hovedstaden")]),
    ]
    assert [k for k, _ in rank_types(groups, "hovedstaden")] == [
        "ste",
        "mat",
        "reg",
        "pos",
        "kom",
    ]
    assert rank_types(groups, "xyz") == groups
    assert [k for k, _ in rank_types(groups[1:], "hovedstaden")] == [
        "mat",
        "reg",
        "pos",
        "kom",
    ]


def test_dedupe_keeps_first_and_errors():
    a = normalize(_ejendom("1a"), BY_KEY["mat"])
    err = error_row(BY_KEY["mat"])
    assert dedupe([a, dict(a), err, dict(err)]) == [a, err, err]


def _plan(*keys, kommunefilter=""):
    return plan_search("3kg", keys, kommunefilter)


def test_failed_request_gives_error_rows_for_its_types():
    plan = _plan("adr", "mat", "kom")
    resolve_ok = {"matches": []}
    result = collect_rows(plan, [resolve_ok, OSError("timeout")])
    assert [(r["key"], r["status"], r["text"]) for r in result.rows] == [
        ("mat", STATUS_ERROR, "Ejendomme - Der skete en fejl"),
        ("kom", STATUS_ERROR, "Kommuner - Der skete en fejl"),
    ]
    assert result.rows[0]["message"] == "timeout"


def test_failed_batch_element_gives_an_error_row_for_that_type_only():
    plan = _plan("mat", "kom")
    response = [{"matches": [], "error": "boom"}, {"matches": []}]
    rows = collect_rows(plan, [response]).rows
    assert [(r["key"], r["status"], r["message"]) for r in rows] == [
        ("mat", STATUS_ERROR, "boom")
    ]


def test_malformed_batch_response_gives_error_rows():
    plan = _plan("mat", "kom")
    rows = collect_rows(plan, [{"matches": []}]).rows
    assert [(r["key"], r["status"]) for r in rows] == [
        ("mat", STATUS_ERROR),
        ("kom", STATUS_ERROR),
    ]


def test_error_row():
    row = error_row(BY_KEY["ste"], "HTTP 500")
    assert row["status"] == STATUS_ERROR
    assert row["text"] == "Stednavne - Der skete en fejl"
    assert row["geometry"] is None and row["point"] is None


def test_build_requests_accepts_any_type_sequence():
    assert build_requests("x", TYPES)[0].keys == ("adr",)
    assert build_requests("x", TYPES)[1].keys == tuple(t.key for t in TYPES[1:])
