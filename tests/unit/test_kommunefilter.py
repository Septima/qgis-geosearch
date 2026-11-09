import pytest
from bifrost_fixtures import load, members_for, plan_for, result_for

from geosearch_dk.bifrost import (
    FILTER_PROJECT,
    PROJECT,
    SEARCH,
    BifrostRequest,
    MissingMembership,
    UnknownKommune,
    apply_kommunefilter,
    collect_rows,
    error_row,
    kommune_ref_from_response,
    kommune_ref_request,
    membership_from_response,
    membership_request,
    membership_targets,
    parse_kommunekoder,
    types_by_key,
)

BY_KEY = types_by_key()


@pytest.mark.parametrize(
    "text, codes",
    [
        ("", ()),
        (None, ()),
        ("101", ("0101",)),
        ("0101, 751;147 101", ("0101", "0751", "0147")),
        ("kommune 230", ("0230",)),
    ],
)
def test_parse_kommunekoder(text, codes):
    assert parse_kommunekoder(text) == codes


def test_kommune_ref_lookup():
    assert kommune_ref_request("0751") == BifrostRequest(
        SEARCH, {"input": "0751", "target": "kommune", "limit": 1}
    )
    data = load("all_aarhus_kommune_751")
    ref = kommune_ref_from_response("0751", data["kommune_refs"]["0751"]["response"])
    assert ref["kind"] == "kommune" and ref["id"]


def test_unknown_kommune():
    data = load("unknown_kommune")
    with pytest.raises(UnknownKommune) as e:
        kommune_ref_from_response("9999", data["kommune_refs"]["9999"]["response"])
    assert e.value.code == "9999"
    assert "9999" in str(e.value)
    with pytest.raises(UnknownKommune):
        kommune_ref_from_response("0101", {"matches": []})


def test_membership_paging():
    ref = {"kind": "kommune", "id": "k"}
    assert membership_request(ref, "region") == BifrostRequest(
        PROJECT, {"input": ref, "target": "region", "limit": 500}
    )
    assert membership_request(ref, "region", "c1").body["cursor"] == "c1"
    page = {"matches": [{"ref": {"kind": "region", "id": "r1"}}], "next": "c2"}
    assert membership_from_response(page) == ({"r1"}, "c2")
    assert membership_from_response({"matches": []}) == (set(), None)


def test_membership_targets_follow_the_type_table():
    assert membership_targets(BY_KEY.values()) == (
        "opstillingskreds",
        "politikreds",
        "region",
    )
    assert [t.key for t in BY_KEY.values() if t.kommune_filter == FILTER_PROJECT] == [
        "ops",
        "pol",
        "reg",
    ]


def test_resolve_pins_the_kommune():
    rows = result_for("adr_vestergade_1_kbh").rows
    assert rows[0]["text"] == "Vestergade 1, 1456 København K"
    assert all(r["text"].endswith("København K") for r in rows)


def test_resolve_with_two_kommuner_merges_by_score():
    rows = result_for("adr_vestergade_1_kbh_aarhus").rows
    cities = {r["text"].rsplit(", ", 1)[1] for r in rows}
    assert {"1456 København K", "8000 Aarhus C"} <= cities
    scores = [r["score"] for r in rows]
    assert scores == sorted(scores, reverse=True)
    assert len(rows) == 40


def test_components_filter():
    result = result_for("ste_pos_reg_skodsborg_rudersdal")
    ste = [r for r in result.rows if r["key"] == "ste"]
    assert ste[0]["text"] == "Skodsborg (bebyggelse, Rudersdal)"
    assert all(r["text"].endswith(", Rudersdal)") for r in ste)
    assert [r["text"] for r in result.rows if r["key"] == "pos"] == ["2942 Skodsborg"]
    assert result.hidden["ste"] > 0 and result.hidden["pos"] > 0


def test_membership_filter():
    result = result_for("all_aarhus_kommune_751")
    ops = [r["text"] for r in result.rows if r["key"] == "ops"]
    assert sorted(ops) == [
        "Aarhus Nordkredsen",
        "Aarhus Sydkredsen",
        "Aarhus Vestkredsen",
        "Aarhus Østkredsen",
    ]
    assert result.hidden["ops"] > 0
    assert [r["text"] for r in result.rows if r["key"] == "kom"] == ["Aarhus Kommune"]


def test_unfiltered_hides_nothing():
    assert set(result_for("all_aarhus").hidden.values()) == {0}


def test_membership_filter_needs_members():
    data = load("all_aarhus_kommune_751")
    plan = plan_for(data)
    responses = [ex["response"] for ex in data["requests"]]
    with pytest.raises(MissingMembership):
        collect_rows(plan, responses)
    members = members_for(data, plan)
    del members["region"]
    with pytest.raises(MissingMembership):
        collect_rows(plan, responses, members)


def test_apply_kommunefilter_keeps_error_rows():
    reg = BY_KEY["reg"]
    rows = [
        {"status": "ok", "ref": {"kind": "region", "id": "in"}},
        {"status": "ok", "ref": {"kind": "region", "id": "out"}},
        error_row(reg),
    ]
    kept, hidden = apply_kommunefilter(rows, ("0101",), {"region": {"in"}}, reg)
    assert [r["ref"] and r["ref"]["id"] for r in kept] == ["in", None]
    assert hidden == 1
    assert apply_kommunefilter(rows, (), None, reg) == (rows, 0)
