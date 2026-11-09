"""HTTP details of talking to Bifrost, without the network.

``client.py`` sends the requests with Qt; everything that can be decided
without a socket (URLs, headers, the key, decoding a reply, when to retry)
lives here so it can be unit tested.

Pure Python: must not import qgis or PyQt.
"""

import email.utils
import json
import os
import time

from .translation import tr

KEY_ENV = "BIFROST_KEY"
# Production, per https://confluence.kds.dk/display/Bifrost/FAQ. Not live until
# Dataforsyningen has moved to its new platform; until then use the test
# server https://bifrost.test42.dataforsyningen.dk (set "Bifrost URL").
DEFAULT_BASE_URL = "https://bifrost.dataforsyningen.dk"

SEARCH_TIMEOUT_MS = 15000
GEOMETRY_TIMEOUT_MS = 60000

# 503 handling: retry at most this many times, and only when Bifrost asks us
# to wait no longer than MAX_RETRY_AFTER seconds.
MAX_RETRIES = 1
MAX_RETRY_AFTER = 10.0


class BifrostError(Exception):
    """A Bifrost request that failed. ``str()`` is shown to the user."""


class BifrostNetworkError(BifrostError):
    """No HTTP answer: DNS, connection, TLS, timeout, ..."""


class BifrostHttpError(BifrostError):
    """An HTTP error status (4xx/5xx), or a 2xx with a body that is not JSON."""

    def __init__(self, status, detail="", retry_after=None):
        self.status = status
        self.detail = detail
        self.retry_after = retry_after
        super().__init__(status, detail)

    def __str__(self):
        text = tr("bifrost", "Bifrost svarede med HTTP %s") % self.status
        return f"{text}: {self.detail}" if self.detail else text


class BifrostNotAuthorized(BifrostHttpError):
    """401/403: the key is missing, wrong or not allowed."""


class BifrostMissingKey(BifrostError):
    """No key configured, so nothing was sent."""

    def __str__(self):
        return tr("bifrost", "Der er ikke angivet en nøgle til Bifrost")


def resolve_key(setting_value, environ=None, default=""):
    """The key to use: the setting, else the ``BIFROST_KEY`` environment
    variable, else ``default`` (the plugin's bundled key)."""
    key = (setting_value or "").strip()
    if key:
        return key
    environ = os.environ if environ is None else environ
    return (environ.get(KEY_ENV) or "").strip() or (default or "").strip()


def endpoint_url(base_url, endpoint):
    base = (base_url or DEFAULT_BASE_URL).strip().rstrip("/")
    return f"{base}/{endpoint.lstrip('/')}"


def request_headers(key):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {key}",
    }


def encode_body(body):
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def parse_retry_after(value, now=None):
    """Seconds to wait from a ``Retry-After`` header, or None.

    Accepts delta-seconds ("3") and HTTP dates. Never negative.
    """
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("latin-1")
    value = value.strip()
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if when is None:
        return None
    now = time.time() if now is None else now
    return max(0.0, when.timestamp() - now)


def _detail(body):
    """A short text from an error body (``{"detail": ...}`` or plain text)."""
    if not body:
        return ""
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    try:
        data = json.loads(body)
    except ValueError:
        return body.strip()[:300]
    if isinstance(data, dict):
        for k in ("detail", "error", "message", "title"):
            if data.get(k):
                v = data[k]
                return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)[:300]


def decode_response(status, body, retry_after=None):
    """The decoded JSON of a reply, or raises a ``BifrostHttpError``.

    ``status`` is the HTTP status, ``body`` the raw bytes and ``retry_after``
    the raw ``Retry-After`` header (or None).
    """
    status = int(status or 0)
    if status in (401, 403):
        raise BifrostNotAuthorized(status, _detail(body))
    if status >= 400 or status < 200:
        raise BifrostHttpError(status, _detail(body), parse_retry_after(retry_after))
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    try:
        return json.loads(body)
    except ValueError as e:
        raise BifrostHttpError(status, tr("bifrost", "Ugyldigt svar: %s") % e) from e


def retry_delay(error, retries_done):
    """Seconds to wait before retrying after ``error``, or None to give up.

    Only a 503 with a usable ``Retry-After`` is retried.
    """
    if not isinstance(error, BifrostHttpError) or error.status != 503:
        return None
    if error.retry_after is None or error.retry_after > MAX_RETRY_AFTER:
        return None
    if retries_done >= MAX_RETRIES:
        return None
    return error.retry_after
