#!/usr/bin/env python3
"""A mock Bifrost that serves the recorded fixtures in tests/fixtures/bifrost/.

    python3 tests/mock_bifrost.py                 # http://127.0.0.1:8766 (make mock)
    python3 tests/mock_bifrost.py --error 503     # every request fails

Point the plugin's Bifrost URL at ``http://127.0.0.1:8766``. Any non-empty
bearer key is accepted unless ``--key`` is given.

``POST /resolve``, ``/search`` and ``/project`` (also under a path prefix, e.g.
``/v1/search``) are answered from the recorded exchanges:

1. the exact request body was recorded (``X-Mock-Fixture: exact``);
2. a batch whose elements were recorded one by one (``partial``, unknown
   elements get no matches);
3. the same request with another ``limit`` or differently cased input: the
   recording with the most matches, cut to the requested limit (``fuzzy``);
4. otherwise no matches (``miss``), as Bifrost answers an unknown input.

Error injection, first match wins:

* query ``?mock_error=503`` or header ``X-Mock-Error: 503``
* the search input itself: ``mock-401``, ``mock-422``, ``mock-503``,
  ``mock-slow`` (so it can be typed into the plugin's search box)
* server config: ``--error`` or ``POST /_mock/config {"error": "503"}``

Errors are ``401``, ``422``, ``503`` (with ``Retry-After``), ``500`` and
``slow`` (answers normally after ``delay`` seconds; ``X-Mock-Delay`` or
``?mock_delay=`` override it). ``error_count`` in the config makes only the
next N requests fail, e.g. to test a retry.

Control endpoints: ``GET /_mock`` (config and counts), ``GET /_mock/requests``
(the request log), ``POST /_mock/config`` and ``POST /_mock/reset``.

In tests, ``serve_in_thread()`` starts a server on a free port.
Standard library only: it also runs inside the QGIS Docker images.
"""

import argparse
import copy
import json
import os
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FIXTURES = os.path.join(HERE, "fixtures", "bifrost")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
ENDPOINTS = ("resolve", "search", "project")
ERRORS = ("401", "422", "500", "503", "slow")
MAGIC_PREFIX = "mock-"

DEFAULT_CONFIG = {
    "key": None,  # accepted bearer key; None = any non-empty key
    "error": None,  # one of ERRORS, for every request
    "error_count": None,  # only fail the next N requests (None = all)
    "delay": 3.0,  # seconds, for "slow"
    "retry_after": 2,  # seconds, for 503
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _fuzzy_body(body):
    """The body without ``limit`` and with the input case-folded."""
    if not isinstance(body, dict):
        return None
    out = {k: v for k, v in body.items() if k != "limit"}
    if isinstance(out.get("input"), str):
        out["input"] = " ".join(out["input"].split()).casefold()
    return out


def _matches(response):
    return (response or {}).get("matches") or [] if isinstance(response, dict) else []


def iter_exchanges(data):
    """All recorded exchanges in a fixture file (see tests/tools/record_bifrost.py)."""
    for ex in data.get("requests") or []:
        yield ex
    for ex in (data.get("kommune_refs") or {}).values():
        yield ex
    for per_target in (data.get("memberships") or {}).values():
        for pages in per_target.values():
            for ex in pages:
                yield ex
    for ex in (data.get("geometry") or {}).get("attempts") or []:
        yield ex


class FixtureIndex:
    """Recorded ``(endpoint, body) -> (status, response)``."""

    def __init__(self, directory=DEFAULT_FIXTURES):
        self.directory = directory
        self.exact = {}
        self.fuzzy = {}
        self.files = 0
        for root, _dirs, files in os.walk(directory):
            for name in sorted(files):
                if name.endswith(".json"):
                    with open(os.path.join(root, name), encoding="utf-8") as f:
                        self.add_fixture(json.load(f))
                    self.files += 1

    def add_fixture(self, data):
        for ex in iter_exchanges(data):
            self.add(ex["endpoint"], ex["body"], ex.get("status", 200), ex["response"])

    def add(self, endpoint, body, status, response):
        self.exact.setdefault((endpoint, canonical(body)), (status, response))
        if status != 200:
            return
        if isinstance(body, list):
            if isinstance(response, list) and len(response) == len(body):
                for b, r in zip(body, response):
                    if not (isinstance(r, dict) and r.get("error")):
                        self.add(endpoint, b, status, r)
            return
        fuzzy = _fuzzy_body(body)
        if fuzzy is None:
            return
        key = (endpoint, canonical(fuzzy))
        best = self.fuzzy.get(key)
        if best is None or len(_matches(response)) > len(_matches(best)):
            self.fuzzy[key] = response

    def lookup(self, endpoint, body, strict=False):
        """``(status, response, how)``; ``how`` is exact, partial, fuzzy or miss.

        With ``strict`` only exact hits are returned, otherwise ``KeyError``.
        """
        hit = self.exact.get((endpoint, canonical(body)))
        if hit:
            return hit[0], copy.deepcopy(hit[1]), "exact"
        if strict:
            raise KeyError("not recorded: %s %s" % (endpoint, canonical(body)))
        if isinstance(body, list):
            parts = [self._single(endpoint, b) for b in body]
            how = "partial" if any(h != "miss" for _, h in parts) else "miss"
            return 200, [r for r, _ in parts], how
        response, how = self._single(endpoint, body)
        return 200, response, how

    def _single(self, endpoint, body):
        hit = self.exact.get((endpoint, canonical(body)))
        if hit and hit[0] == 200:
            return copy.deepcopy(hit[1]), "exact"
        fuzzy = _fuzzy_body(body)
        if fuzzy is not None:
            found = self.fuzzy.get((endpoint, canonical(fuzzy)))
            if found is not None:
                response = copy.deepcopy(found)
                limit = body.get("limit")
                if isinstance(limit, int) and isinstance(response, dict):
                    response["matches"] = _matches(response)[:limit]
                    if endpoint == "project" and len(_matches(found)) > limit:
                        response["next"] = None
                return response, "fuzzy"
        return empty_response(endpoint, body), "miss"


def empty_response(endpoint, body):
    body = body if isinstance(body, dict) else {}
    if endpoint == "project":
        return {"input": body.get("input"), "matches": [], "next": None}
    return {"input": body.get("input"), "matches": []}


def magic_error(body):
    """The error requested by a ``mock-...`` search input, or None."""
    for item in body if isinstance(body, list) else [body]:
        text = item.get("input") if isinstance(item, dict) else None
        if isinstance(text, str):
            word = text.strip().casefold()
            if word.startswith(MAGIC_PREFIX) and word[len(MAGIC_PREFIX) :] in ERRORS:
                return word[len(MAGIC_PREFIX) :]
    return None


def error_response(error, config, endpoint):
    """``(status, headers, body)`` for an injected error."""
    if error == "401":
        return 401, {"WWW-Authenticate": "Bearer"}, {"detail": "invalid credential"}
    if error == "422":
        return (
            422,
            {},
            {
                "detail": [
                    {
                        "type": "mock",
                        "loc": ["body", endpoint],
                        "msg": "Injected validation error (mock Bifrost)",
                        "input": None,
                    }
                ]
            },
        )
    if error == "503":
        return (
            503,
            {"Retry-After": str(config["retry_after"])},
            {"detail": "service unavailable (mock Bifrost)"},
        )
    return 500, {}, {"detail": "internal server error (mock Bifrost)"}


class Handler(BaseHTTPRequestHandler):
    server_version = "MockBifrost/1"
    protocol_version = "HTTP/1.1"

    # --- plumbing -----------------------------------------------------------

    def log_message(self, fmt, *args):
        if not self.server.quiet:
            super().log_message(fmt, *args)

    def _send(self, status, body, headers=None):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw.decode("utf-8")) if raw else None

    def _route(self):
        parsed = urllib.parse.urlsplit(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        return parts, urllib.parse.parse_qs(parsed.query)

    # --- methods ------------------------------------------------------------

    def do_GET(self):
        parts, _query = self._route()
        mock = self.server.mock
        if parts == ["_mock"] or parts == ["health"]:
            self._send(200, mock.status())
        elif parts == ["_mock", "requests"]:
            self._send(200, mock.request_log())
        else:
            self._send(405 if parts and parts[-1] in ENDPOINTS else 404, {"detail": "Not Found"})

    def do_POST(self):
        parts, query = self._route()
        mock = self.server.mock
        if parts[:1] == ["_mock"]:
            body = self._read_json() or {}
            if parts == ["_mock", "config"]:
                mock.configure(**body)
                self._send(200, mock.status())
            elif parts == ["_mock", "reset"]:
                mock.reset()
                self._send(200, mock.status())
            else:
                self._send(404, {"detail": "Not Found"})
            return
        if not parts or parts[-1] not in ENDPOINTS:
            self._send(404, {"detail": "Not Found"})
            return
        endpoint = parts[-1]
        try:
            body = self._read_json()
        except ValueError:
            self._send(422, {"detail": [{"type": "json_invalid", "msg": "Invalid JSON"}]})
            return
        status, headers, response = mock.answer(
            endpoint,
            body,
            self.headers.get("Authorization"),
            (query.get("mock_error") or [None])[0] or self.headers.get("X-Mock-Error"),
            (query.get("mock_delay") or [None])[0] or self.headers.get("X-Mock-Delay"),
        )
        self._send(status, response, headers)


class MockBifrost:
    """The mock's state; one per server."""

    def __init__(self, fixtures=DEFAULT_FIXTURES, **config):
        self.index = FixtureIndex(fixtures)
        self.lock = threading.Lock()
        self.config = dict(DEFAULT_CONFIG)
        self.requests = []
        # Bumped by reset(), so a request still running from an earlier test
        # (e.g. a "slow" one the client gave up on) stays out of the new log.
        self.generation = 0
        self.configure(**config)
        self.httpd = None
        self.thread = None

    # --- config -------------------------------------------------------------

    def configure(self, **config):
        unknown = set(config) - set(DEFAULT_CONFIG)
        if unknown:
            raise ValueError("unknown mock config: %s" % sorted(unknown))
        if config.get("error") is not None:
            config["error"] = str(config["error"])
            if config["error"] not in ERRORS:
                raise ValueError("error must be one of %s" % (ERRORS,))
        with self.lock:
            self.config.update(config)

    def reset(self):
        with self.lock:
            self.config = dict(DEFAULT_CONFIG)
            self.requests = []
            self.generation += 1

    def status(self):
        with self.lock:
            return {
                "fixtures": self.index.files,
                "recorded": len(self.index.exact),
                "requests": len(self.requests),
                "config": {k: v for k, v in self.config.items() if k != "key"},
            }

    def request_log(self):
        with self.lock:
            return list(self.requests)

    # --- answering ----------------------------------------------------------

    def _configured_error(self):
        with self.lock:
            error = self.config["error"]
            count = self.config["error_count"]
            if error and count is not None:
                if count <= 0:
                    return None
                self.config["error_count"] = count - 1
            return error

    def answer(self, endpoint, body, authorization=None, error=None, delay=None):
        """``(status, headers, body)`` for one request."""
        with self.lock:
            config = dict(self.config)
            generation = self.generation
        error = error or magic_error(body) or self._configured_error()
        entry = {"endpoint": endpoint, "body": body, "error": error, "_generation": generation}
        try:
            token = ""
            if authorization and authorization.lower().startswith("bearer "):
                token = authorization[7:].strip()
            if not token:
                return self._log(
                    entry,
                    (
                        401,
                        {"WWW-Authenticate": "Bearer"},
                        {"detail": "missing bearer credential"},
                    ),
                )
            if config["key"] and token != config["key"]:
                error = "401"
            if error == "slow":
                time.sleep(float(delay if delay is not None else config["delay"]))
            elif error:
                return self._log(entry, error_response(error, config, endpoint))
            if body is None or not isinstance(body, (dict, list)):
                return self._log(
                    entry,
                    (422, {}, {"detail": [{"type": "missing", "loc": ["body"], "msg": "Field required"}]}),
                )
            status, response, how = self.index.lookup(endpoint, body)
            entry["fixture"] = how
            return self._log(entry, (status, {"X-Mock-Fixture": how}, response))
        except Exception as e:  # pragma: no cover - keep the server alive
            return self._log(entry, (500, {}, {"detail": "mock error: %s" % e}))

    def _log(self, entry, result):
        entry["status"] = result[0]
        with self.lock:
            if entry.pop("_generation") == self.generation:
                self.requests.append(entry)
        return result

    # --- serving ------------------------------------------------------------

    def bind(self, host=DEFAULT_HOST, port=DEFAULT_PORT, quiet=False):
        self.httpd = ThreadingHTTPServer((host, port), Handler)
        self.httpd.daemon_threads = True
        self.httpd.mock = self
        self.httpd.quiet = quiet
        return self

    @property
    def url(self):
        host, port = self.httpd.server_address[:2]
        return "http://%s:%d" % (host, port)

    def serve_forever(self):
        self.httpd.serve_forever()

    def start(self):
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def shutdown(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread:
            self.thread.join(5)


def serve_in_thread(host=DEFAULT_HOST, port=0, fixtures=DEFAULT_FIXTURES, quiet=True, **config):
    """Start a mock in a daemon thread (``port=0`` = a free port); see ``MockBifrost.url``."""
    return MockBifrost(fixtures, **config).bind(host, port, quiet).start()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--key", help="only accept this bearer key")
    parser.add_argument("--error", choices=ERRORS, help="fail every request")
    parser.add_argument("--delay", type=float, default=DEFAULT_CONFIG["delay"])
    parser.add_argument("--retry-after", type=int, default=DEFAULT_CONFIG["retry_after"])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    mock = MockBifrost(
        args.fixtures,
        key=args.key,
        error=args.error,
        delay=args.delay,
        retry_after=args.retry_after,
    ).bind(args.host, args.port, args.quiet)
    print(
        "Mock Bifrost on %s (%d fixture files, %d recorded requests)"
        % (mock.url, mock.index.files, len(mock.index.exact)),
        flush=True,
    )
    try:
        mock.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        mock.shutdown()


if __name__ == "__main__":
    main()
