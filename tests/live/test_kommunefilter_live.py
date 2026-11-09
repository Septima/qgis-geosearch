"""The kommune filter against the real Bifrost (#11, #2).

Runs the same code the plugin runs (``plan_search``, ``KommunefilterCache``,
``collect_rows``), with a urllib ``send`` instead of Qt. Skipped without a key:

    BIFROST_KEY=... uv run pytest -m live tests/live   # make test-live

``BIFROST_URL`` overrides the default test server.
"""

import json
import os
import urllib.error
import urllib.request

import pytest

from geosearch_dk.bifrost import (
    TYPES,
    KommunefilterCache,
    UnknownKommune,
    collect_rows,
    plan_search,
)
from geosearch_dk.bifrost import transport

import bifrost_cases as bc

KEY = os.environ.get(transport.KEY_ENV)
URL = os.environ.get("BIFROST_URL") or bc.DEFAULT_URL
ALL = [t.key for t in TYPES]

pytestmark = pytest.mark.skipif(not KEY, reason="set BIFROST_KEY to run live tests")


def _post(request):
    req = urllib.request.Request(
        transport.endpoint_url(URL, request.endpoint),
        data=transport.encode_body(request.body),
        headers=transport.request_headers(KEY),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return transport.decode_response(resp.status, resp.read())
    except urllib.error.HTTPError as e:
        return transport.decode_response(e.code, e.read())
    except Exception as e:
        return e


def send(requests, callback):
    callback([_post(r) for r in requests])


@pytest.fixture(scope="module")
def cache():
    return KommunefilterCache(send)


def search(cache, text, keys, kommunefilter):
    plan = plan_search(text, keys, kommunefilter=kommunefilter)
    responses = []
    send(plan.requests, responses.extend)
    loaded = []
    cache.load(plan.kommuner, plan.membership_targets, loaded.append)
    (members,) = loaded
    if isinstance(members, BaseException):
        raise members
    result = collect_rows(plan, responses, members)
    print(
        "\n%r / %s: %d rows, hidden %s"
        % (text, kommunefilter, len(result.rows), {k: n for k, n in result.hidden.items() if n})
    )
    for row in result.rows:
        print("  ", row["key"], row["text"])
    return result


def kommunekoder(row):
    return {k.get("kommunekode") for k in (row.get("components") or {}).get("kommuner") or []}


@pytest.mark.xfail(
    strict=True,
    reason="documented loss (#2): no Horsens parcel is in Bifrost's national top 100 for '1a'",
)
def test_matrikel_1a_horsens(cache):
    result = search(cache, "1a", ["mat"], "615")
    assert result.hidden["mat"] > 0
    assert result.rows


def test_vestergade_1_koebenhavn(cache):
    result = search(cache, "vestergade 1", ["adr"], "101")
    assert result.rows[0]["text"] == "Vestergade 1, 1456 København K"
    assert all(r["status"] == "ok" for r in result.rows)
    assert all(kommunekoder(r) == {"0101"} for r in result.rows)


def test_vor_frue_koebenhavn_aalborg(cache):
    # Partial: some hits survive, many are hidden.
    result = search(cache, "vor frue", ["ste"], "101,851")
    assert result.rows and result.hidden["ste"] > 0
    assert all(r["status"] == "ok" for r in result.rows)
    assert all(kommunekoder(r) & {"0101", "0851"} for r in result.rows)


def test_all_types_with_memberships(cache):
    result = search(cache, "aarhus", ALL, "751")
    assert all(r["status"] == "ok" for r in result.rows)
    assert [r["text"] for r in result.rows if r["key"] == "kom"] == ["Aarhus Kommune"]
    assert {r["text"] for r in result.rows if r["key"] == "reg"} <= {"Region Midtjylland"}
    assert result.hidden["ops"] > 0


def test_unknown_kommune(cache):
    with pytest.raises(UnknownKommune):
        search(cache, "vestergade 1", ["adr"], "999")
