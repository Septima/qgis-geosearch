"""The mock Bifrost (tests/mock_bifrost.py), over HTTP."""

import json
import time
import urllib.error
import urllib.request

import pytest

import bifrost_cases as bc
import mock_bifrost
from geosearch_dk.bifrost import collect_rows, plan_search

KEY = "test-key"


@pytest.fixture(scope="module")
def server():
    mock = mock_bifrost.serve_in_thread(delay=0.3)
    yield mock
    mock.shutdown()


@pytest.fixture
def mock(server):
    server.reset()
    server.configure(delay=0.3)
    return server


def post(mock, path, body, key=KEY, headers=None, timeout=10):
    h = {"Content-Type": "application/json"}
    if key is not None:
        h["Authorization"] = "Bearer " + key
    h.update(headers or {})
    req = urllib.request.Request(
        mock.url + path, data=json.dumps(body).encode(), headers=h, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), json.loads(e.read())


def get(mock, path):
    with urllib.request.urlopen(mock.url + path, timeout=10) as resp:
        return json.loads(resp.read())


def recorded_case(case_id):
    case = next(c for c in bc.load_cases() if c["id"] == case_id)
    return case, bc.load_case_fixture(case_id)


# --- answers ------------------------------------------------------------------


def test_exact_hit_reproduces_the_recording(mock):
    case, fixture = recorded_case("adr-vestergade-21-aar")
    plan = bc.case_plan(case)
    responses = []
    for request in plan.requests:
        status, headers, response = post(mock, "/" + request.endpoint, request.body)
        assert status == 200
        assert headers["X-Mock-Fixture"] == "exact"
        responses.append(response)
    recorded = [ex["response"] for ex in fixture["requests"]]
    assert responses == recorded
    rows = collect_rows(plan, responses).rows
    assert any(r["text"] == "Vestergade 21, 8000 Aarhus C" for r in rows)


@pytest.mark.parametrize("case_id", ["adr-noeddebogade-1-st-th", "ste-vor-frue-kommunefilter", "mat-3kg"])
def test_a_whole_case_runs_against_the_mock(mock, case_id):
    case, _fixture = recorded_case(case_id)
    expected = bc.replay_case(case)
    result = bc.run_case(case, bc.LiveSender(mock.url, KEY))
    assert result["display"] == expected["display"]
    assert result["outcome"] == expected["outcome"]
    assert {e["fixture"] for e in mock.request_log()} == {"exact"}


def test_other_limit_and_case_is_fuzzy(mock):
    _case, fixture = recorded_case("adr-vestergade-21-aar")
    body = dict(fixture["requests"][0]["body"])
    if isinstance(body.get("input"), str):
        body["input"] = body["input"].upper()
    body["limit"] = 2
    status, headers, response = post(mock, "/" + fixture["requests"][0]["endpoint"], body)
    assert status == 200
    assert headers["X-Mock-Fixture"] == "fuzzy"
    assert 0 < len(response["matches"]) <= 2


def test_unknown_input_has_no_matches(mock):
    status, headers, response = post(mock, "/search", {"input": "qqq zzz 999", "limit": 5})
    assert (status, headers["X-Mock-Fixture"], response["matches"]) == (200, "miss", [])


def test_path_prefix_is_ignored(mock):
    status, headers, _ = post(mock, "/v1/search", {"input": "qqq", "limit": 5})
    assert (status, headers["X-Mock-Fixture"]) == (200, "miss")


def test_unknown_path_is_404(mock):
    assert post(mock, "/nothing", {})[0] == 404


# --- auth -------------------------------------------------------------------


def test_missing_key_is_401(mock):
    status, headers, response = post(mock, "/search", {"input": "x"}, key=None)
    assert status == 401
    assert response == {"detail": "missing bearer credential"}
    assert headers["WWW-Authenticate"] == "Bearer"


def test_configured_key_must_match(mock):
    mock.configure(key="right")
    assert post(mock, "/search", {"input": "x"}, key="wrong")[0] == 401
    assert post(mock, "/search", {"input": "x"}, key="right")[0] == 200


# --- error injection ------------------------------------------------------------


@pytest.mark.parametrize("how", ["query", "header", "magic", "config"])
@pytest.mark.parametrize("error", ["401", "422", "500", "503"])
def test_error_injection(mock, how, error):
    path, headers, body = "/search", {}, {"input": "vestergade", "limit": 5}
    if how == "query":
        path += "?mock_error=" + error
    elif how == "header":
        headers["X-Mock-Error"] = error
    elif how == "magic":
        body["input"] = "mock-" + error
    else:
        mock.configure(error=error)
    status, resp_headers, response = post(mock, path, body, headers=headers)
    assert status == int(error)
    assert "detail" in response
    if error == "503":
        assert resp_headers["Retry-After"] == "2"
    if error == "422":
        assert isinstance(response["detail"], list) and "msg" in response["detail"][0]


def test_magic_input_in_a_batch(mock):
    status, _, _ = post(mock, "/resolve", [{"input": "x"}, {"input": "MOCK-503"}])
    assert status == 503


def test_retry_after_is_configurable(mock):
    mock.configure(error="503", retry_after=7)
    assert post(mock, "/search", {"input": "x"})[1]["Retry-After"] == "7"


@pytest.mark.parametrize("how", ["header", "config"])
def test_slow(mock, how):
    headers = {}
    if how == "header":
        headers = {"X-Mock-Error": "slow", "X-Mock-Delay": "0.4"}
    else:
        mock.configure(error="slow", delay=0.4)
    t0 = time.monotonic()
    status, _, _ = post(mock, "/search", {"input": "qqq"}, headers=headers)
    assert status == 200
    assert time.monotonic() - t0 >= 0.4


def test_slow_request_times_out_the_client(mock):
    import socket

    with pytest.raises((socket.timeout, TimeoutError, urllib.error.URLError)):
        post(mock, "/search?mock_error=slow&mock_delay=1", {"input": "qqq"}, timeout=0.2)


def test_a_request_from_before_reset_is_not_logged(mock):
    import socket

    with pytest.raises((socket.timeout, TimeoutError, urllib.error.URLError)):
        post(mock, "/search?mock_error=slow&mock_delay=0.5", {"input": "qqq"}, timeout=0.1)
    mock.reset()
    time.sleep(0.8)  # the slow request finishes after the reset
    assert mock.request_log() == []


def test_error_count_fails_only_the_next_requests(mock):
    mock.configure(error="503", error_count=2)
    statuses = [post(mock, "/search", {"input": "qqq"})[0] for _ in range(3)]
    assert statuses == [503, 503, 200]


def test_bad_config_is_rejected(mock):
    with pytest.raises(ValueError):
        mock.configure(error="418")
    with pytest.raises(ValueError):
        mock.configure(nonsense=1)


# --- control endpoints ------------------------------------------------------------


def test_control_endpoints(mock):
    status = post(mock, "/_mock/config", {"error": "503", "key": "secret"})[2]
    assert status["config"]["error"] == "503"
    assert "key" not in status["config"]
    assert status["recorded"] > 0
    post(mock, "/search", {"input": "x"}, key="secret")
    log = get(mock, "/_mock/requests")
    assert [(e["endpoint"], e["status"], e["error"]) for e in log] == [("search", 503, "503")]
    assert get(mock, "/_mock")["requests"] == 1
    reset = post(mock, "/_mock/reset", {})[2]
    assert reset["config"]["error"] is None and reset["requests"] == 0
    assert get(mock, "/health")["requests"] == 0


def test_invalid_json_is_422(mock):
    req = urllib.request.Request(
        mock.url + "/search",
        data=b"{not json",
        headers={"Authorization": "Bearer x", "Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=5)
    assert e.value.code == 422
