import pytest

from geosearch_dk.bifrost import (
    MAT_TITLE,
    PROPOSED_TYPES,
    RESOLVE,
    SEARCH,
    TYPES,
    BifrostRequest,
    build_requests,
    default_limits,
    parse_query,
    plan_search,
    types_by_key,
)

ALL = [t.key for t in TYPES]
BY_KEY = types_by_key()


def test_types_are_todays_eight_in_display_order():
    assert [(t.key, t.title) for t in TYPES] == [
        ("adr", "Husnumre"),
        ("ste", "Stednavne"),
        ("pos", "Postdistrikter"),
        ("mat", MAT_TITLE),
        ("kom", "Kommuner"),
        ("ops", "Opstillingskredse"),
        ("pol", "Politikredse"),
        ("reg", "Regioner"),
    ]


def test_type_table_targets():
    assert {t.key: (t.endpoint, t.target) for t in TYPES} == {
        "adr": (RESOLVE, "entrance"),
        "ste": (SEARCH, "stednavn"),
        "pos": (SEARCH, "postcode"),
        "mat": (SEARCH, "ejendom"),
        "kom": (SEARCH, "kommune"),
        "ops": (SEARCH, "opstillingskreds"),
        "pol": (SEARCH, "politikreds"),
        "reg": (SEARCH, "region"),
    }


def test_proposed_types_do_not_clash():
    keys = [t.key for t in TYPES + PROPOSED_TYPES]
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize(
    "text, selected, term, keys",
    [
        ("Vangebovej 71", ALL, "Vangebovej 71", tuple(ALL)),
        ("  aarhus ", ["reg", "adr"], "aarhus", ("adr", "reg")),
        ("mat: 3kg søll", ["adr"], "3kg søll", ("mat",)),
        ("MATRIKEL:3kg", ["adr"], "3kg", ("mat",)),
        ("ejd: 3kg søll", ["adr"], "3kg søll", ("mat",)),
        ("EJD:6033528", [], "6033528", ("mat",)),
        ("ste:a:b", [], "a:b", ("ste",)),
        ("xyz: aarhus", ["kom"], "xyz: aarhus", ("kom",)),
        ("aarhus", ["kom", "nope"], "aarhus", ("kom",)),
        ("aarhus", [], "aarhus", ()),
    ],
)
def test_parse_query(text, selected, term, keys):
    assert parse_query(text, selected) == (term, keys)


def test_parse_query_knows_proposed_types_only_when_given():
    assert parse_query("sog: vor frue", ALL).keys == tuple(ALL)
    assert parse_query("sog: vor frue", [], TYPES + PROPOSED_TYPES) == (
        "vor frue",
        ("sog",),
    )


def test_default_limits_share_forty():
    assert default_limits(ALL) == {k: 5 for k in ALL}
    assert default_limits(["adr", "ste", "pos"]) == {"adr": 13, "ste": 13, "pos": 13}
    assert default_limits(["mat"]) == {"mat": 40}
    assert default_limits([]) == {}


def test_requests_without_filter():
    types = [BY_KEY[k] for k in ("adr", "ste", "mat")]
    assert build_requests("skodsborg", types) == [
        BifrostRequest(RESOLVE, {"input": "skodsborg", "limit": 13}, ("adr",)),
        BifrostRequest(
            SEARCH,
            [
                {"input": "skodsborg", "target": "stednavn", "limit": 13},
                {"input": "skodsborg", "target": "ejendom", "limit": 13},
            ],
            ("ste", "mat"),
        ),
    ]


def test_resolve_limit_is_capped():
    (request,) = build_requests("Vangebovej 71", [BY_KEY["adr"]])
    assert request.body == {"input": "Vangebovej 71", "limit": 20}


def test_requests_with_kommune_filter():
    types = [BY_KEY[k] for k in ("adr", "reg")]
    assert build_requests("vestergade 1", types, ("0101", "0751")) == [
        BifrostRequest(
            RESOLVE,
            [
                {
                    "input": "vestergade 1",
                    "components": {"kommune": "0101"},
                    "limit": 20,
                },
                {
                    "input": "vestergade 1",
                    "components": {"kommune": "0751"},
                    "limit": 20,
                },
            ],
            ("adr",),
        ),
        BifrostRequest(
            SEARCH,
            [{"input": "vestergade 1", "target": "region", "limit": 100}],
            ("reg",),
        ),
    ]


def test_lifecycle_is_sent_from_the_type_table():
    udg = types_by_key(PROPOSED_TYPES)["udg"]
    (request,) = build_requests("1an gentofte", [udg])
    assert request.body == [
        {
            "input": "1an gentofte",
            "target": "ejendom",
            "limit": 40,
            "lifecycle": ["retired"],
        }
    ]


def test_no_requests_for_empty_term_or_types():
    assert build_requests("", TYPES) == []
    assert build_requests("aarhus", []) == []
    assert plan_search("mat:  ", ALL).requests == []


def test_plan_search():
    plan = plan_search("aarhus", ["kom", "ops", "reg"], "751, 0101 101")
    assert plan.term == "aarhus"
    assert plan.keys == ("kom", "ops", "reg")
    assert plan.kommuner == ("0751", "0101")
    assert plan.limits == {"kom": 13, "ops": 13, "reg": 13}
    assert plan.membership_targets == ("opstillingskreds", "region")
    assert plan_search("aarhus", ["kom", "ops"]).membership_targets == ()
