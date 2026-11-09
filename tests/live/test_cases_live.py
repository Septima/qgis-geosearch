"""Every case in tests/cases.yaml, through the core, against the real Bifrost.

A case passes when Bifrost meets the case's ``expect`` (or its
``bifrost.expect``). Cases with a ``known_gap`` are expected to fail
(xfail); an XPASS means Bifrost now does what the gap says it cannot.
Stednavne match on the name only (#1). See conftest.py for the report.
"""

import pytest

import bifrost_cases as bc

GAPS = {
    1: "#1 display text / stednavn subtype is lost",
    2: "#2 no server-side kommunefilter",
    3: "#3 no type-ahead on partial words",
    4: "#4 matrikel = ejendom (BFE), near-misses",
}


def _param(case):
    gap = case.get("known_gap")
    marks = []
    # #1 is accommodated by the name-only match, so such cases should pass;
    # they are xfailed at run time only if even the name is not found.
    if gap and gap != bc.DISPLAY_TEXT_GAP:
        marks.append(pytest.mark.xfail(reason=GAPS.get(gap, "#%s" % gap), strict=False))
    elif case["id"] in bc.KNOWN_FAILURES:
        marks.append(pytest.mark.xfail(reason="no issue yet: " + bc.KNOWN_FAILURES[case["id"]], strict=False))
    return pytest.param(case, id=case["id"], marks=marks)


@pytest.mark.parametrize("case", [_param(c) for c in bc.load_cases()])
def test_case(case, live_send, record_result):
    result = bc.run_case(case, live_send)
    record_result(case["id"], result)
    errors = [
        "%s %s: HTTP %s" % (ex["endpoint"], ex["keys"], ex["status"])
        for ex in result["requests"]
        if ex["status"] != 200
    ]
    top = ["%d %s: %s" % (r["rank"], r["key"], r["text"]) for r in result["display"][:10]]
    message = "%s\n  input: %r\n  %s\n  top rows:\n    %s" % (
        result["why"],
        case["input"],
        "; ".join(errors) or "no HTTP errors",
        "\n    ".join(top) or "(none)",
    )
    if result["outcome"] == bc.XFAIL and case.get("known_gap") == bc.DISPLAY_TEXT_GAP:
        pytest.xfail(GAPS[bc.DISPLAY_TEXT_GAP] + ": " + result["why"])
    assert result["ok"] is not False, message
