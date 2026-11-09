"""Replay every recorded case fixture (tests/fixtures/bifrost/cases/) through the core.

This catches core changes that alter the requests a case sends (the fixture
no longer answers them: re-record with ``record_bifrost.py --cases``) or that
turn a passing case into a failing one. The live suite (tests/live/) runs the
same cases against the real Bifrost.
"""

import pytest

import bifrost_cases as bc

CASES = bc.load_cases()


def test_every_case_is_recorded():
    missing = [c["id"] for c in CASES if bc.load_case_fixture(c["id"]) is None]
    assert not missing, "record them: record_bifrost.py --cases " + " ".join(missing)


def _param(case):
    marks = []
    if case["id"] in bc.KNOWN_FAILURES:
        marks.append(pytest.mark.xfail(reason=bc.KNOWN_FAILURES[case["id"]], strict=True))
    return pytest.param(case, id=case["id"], marks=marks)


@pytest.mark.parametrize("case", [_param(c) for c in CASES])
def test_replay(case):
    try:
        result = bc.replay_case(case)
    except KeyError as e:
        pytest.fail("the core sends a request that was not recorded (re-record the case): %s" % e)
    if result is None:
        pytest.skip("not recorded")
    assert result["outcome"] != bc.FAIL, result["why"]


def test_fixtures_hold_no_key():
    import glob
    import os

    for path in glob.glob(os.path.join(bc.CASES_FIXTURES, "*.json")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        assert "Bearer" not in text and "Authorization" not in text, path
