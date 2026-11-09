"""Live case suite: tests/cases.yaml against the real Bifrost.

    BIFROST_KEY=... uv run pytest -m live tests/live      # make test-live

Environment:
    BIFROST_KEY          API key (required; the tests are skipped without it)
    BIFROST_URL          default https://bifrost.test42.dataforsyningen.dk
    BIFROST_LIVE_REPORT  where the report goes
                         (default out/bifrost-live-report.md)
"""

import os

import pytest

import bifrost_cases as bc

RESULTS = {}


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.live)


@pytest.fixture(scope="session")
def live_send():
    key = os.environ.get("BIFROST_KEY")
    if not key:
        pytest.skip("BIFROST_KEY is not set")
    return bc.LiveSender(os.environ.get("BIFROST_URL", bc.DEFAULT_URL), key)


@pytest.fixture
def record_result():
    def record(case_id, result):
        RESULTS[case_id] = result

    return record


def report_path():
    return os.environ.get(
        "BIFROST_LIVE_REPORT", os.path.join(bc.ROOT, "out", "bifrost-live-report.md")
    )


def pytest_sessionfinish(session):
    if not RESULTS:
        return
    cases = bc.load_cases()
    url = os.environ.get("BIFROST_URL", bc.DEFAULT_URL)
    counts = bc.write_report(
        [c for c in cases if c["id"] in RESULTS], RESULTS, report_path(), "live, %s" % url
    )
    session.config._bifrost_summary = (report_path(), counts)


def pytest_terminal_summary(terminalreporter, config):
    summary = getattr(config, "_bifrost_summary", None)
    if summary:
        path, counts = summary
        terminalreporter.write_sep("-", "Bifrost case catalogue")
        terminalreporter.write_line(
            "%(pass)d pass, %(xfail)d known gaps, %(xpass)d pass despite a known gap, "
            "%(fail)d fail, %(none)d without expectation" % counts
        )
        terminalreporter.write_line("Report: %s" % os.path.relpath(path))
