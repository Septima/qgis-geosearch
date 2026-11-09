import json

import pytest

from geosearch_dk.bifrost import transport as t


def test_resolve_key_prefers_setting_then_env():
    assert t.resolve_key(" abc ", {"BIFROST_KEY": "env"}) == "abc"
    assert t.resolve_key("", {"BIFROST_KEY": " env "}) == "env"
    assert t.resolve_key(None, {}) == ""
    assert t.resolve_key("", {}, default=" bundled ") == "bundled"
    assert t.resolve_key("", {"BIFROST_KEY": "env"}, default="bundled") == "env"


def test_endpoint_url():
    assert t.endpoint_url("https://x.dk/", "search") == "https://x.dk/search"
    assert t.endpoint_url("https://x.dk/api", "/project") == "https://x.dk/api/project"
    assert t.endpoint_url("", "resolve") == t.DEFAULT_BASE_URL + "/resolve"


def test_headers_and_body():
    h = t.request_headers("k")
    assert h["Authorization"] == "Bearer k"
    assert h["Content-Type"] == "application/json"
    body = [{"input": "Søllerød", "target": "stednavn"}]
    assert json.loads(t.encode_body(body).decode("utf-8")) == body


def test_decode_ok_and_errors():
    assert t.decode_response(200, b'{"matches": []}') == {"matches": []}
    with pytest.raises(t.BifrostNotAuthorized) as e:
        t.decode_response(401, b'{"detail":"invalid credential"}')
    assert e.value.status == 401 and "invalid credential" in str(e.value)
    with pytest.raises(t.BifrostHttpError) as e:
        t.decode_response(503, b"busy", b"2")
    assert e.value.status == 503 and e.value.retry_after == 2.0
    with pytest.raises(t.BifrostHttpError):
        t.decode_response(200, b"<html>")


def test_parse_retry_after():
    assert t.parse_retry_after(b"3") == 3.0
    assert t.parse_retry_after("-1") == 0.0
    assert t.parse_retry_after(None) is None
    assert t.parse_retry_after("soon") is None
    now = 1_000_000_000  # 2001-09-09T01:46:40Z
    assert t.parse_retry_after("Sun, 09 Sep 2001 01:46:45 GMT", now) == 5.0


def test_retry_delay_only_for_short_503():
    busy = t.BifrostHttpError(503, retry_after=2.0)
    assert t.retry_delay(busy, 0) == 2.0
    assert t.retry_delay(busy, t.MAX_RETRIES) is None
    assert t.retry_delay(t.BifrostHttpError(503), 0) is None
    assert t.retry_delay(t.BifrostHttpError(503, retry_after=600), 0) is None
    assert t.retry_delay(t.BifrostHttpError(500, retry_after=1), 0) is None
    assert t.retry_delay({"matches": []}, 0) is None
