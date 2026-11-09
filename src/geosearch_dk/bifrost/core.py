"""Bifrost search core: query parsing, request bodies, normalisation and ranking.

The network layer (Qt) sends the ``BifrostRequest``s this module builds and
hands the decoded JSON back. Nothing here does I/O.

Typical flow::

    plan = plan_search(text, selected_keys, kommunefilter_text)
    responses = [send(r) for r in plan.requests]          # JSON, or the exception
    members = {...}                                        # see kommunefilter, only
                                                           # for plan.membership_targets
    result = collect_rows(plan, responses, members)
    for row in result.rows: ...                            # see make_row for the contract

and when a row is chosen::

    attempt, geojson = 0, None
    while geojson is None and (req := geometry_request(row, attempt)):
        geojson = geometry_from_response(row, send(req))
        attempt += 1
    geojson = geojson or row["point"]

Pure Python: must not import qgis or PyQt.
"""

import re
from typing import Dict, List, NamedTuple, Optional, Tuple

from .display import display_text
from .kommunefilter import (
    UnknownKommune,
    apply_kommunefilter,
    membership_targets,
    parse_kommunekoder,
)
from .translation import tr
from .types import (
    PROJECT,
    RESOLVE,
    SEARCH,
    TYPES,
    BifrostRequest,
    SearchType,
    types_by_key,
)

SRID = 25832
DEFAULT_TOTAL_LIMIT = 40
RESOLVE_MAX_LIMIT = 20
SEARCH_MAX_LIMIT = 100

STATUS_OK = "ok"
STATUS_ERROR = "error"


class ParsedQuery(NamedTuple):
    term: str
    keys: Tuple[str, ...]
    """Type keys to search, in type order."""


class SearchPlan(NamedTuple):
    term: str
    types: Tuple[SearchType, ...]
    kommuner: Tuple[str, ...]
    limits: Dict[str, int]
    requests: List[BifrostRequest]
    membership_targets: Tuple[str, ...]
    """Targets that need /project memberships of ``kommuner`` before
    ``collect_rows`` (empty when not filtering)."""

    @property
    def keys(self):
        return tuple(t.key for t in self.types)


class SearchResult(NamedTuple):
    rows: list
    hidden: Dict[str, int]
    """Per type key: hits removed by the kommune filter (0 when not filtering)."""


# --- query ------------------------------------------------------------------


def parse_query(text, selected_keys, types=TYPES):
    """Split an optional type prefix off the search text.

    "mat: 3kg søll" searches only ``mat`` (even when it is not selected), like
    the GSearch plugin: the prefix is the first three letters before the first
    ":", case-insensitive. A type's ``prefix`` ("ejd:") works like its key.
    Otherwise ``selected_keys`` are searched.
    """
    text = text or ""
    known = types_by_key(types)
    if ":" in text:
        prefix, rest = text.split(":", 1)
        prefix = prefix[:3].lower()
        by_prefix = {t.prefix: k for k, t in known.items() if t.prefix}
        key = prefix if prefix in known else by_prefix.get(prefix)
        if key:
            return ParsedQuery(rest.strip(), (key,))
    selected = set(selected_keys)
    return ParsedQuery(text.strip(), tuple(k for k in known if k in selected))


def default_limits(keys, total=DEFAULT_TOTAL_LIMIT):
    """``total`` hits shared evenly by the types, as the GSearch plugin did."""
    keys = list(keys)
    if not keys:
        return {}
    per_type = max(1, total // len(keys))
    return {k: per_type for k in keys}


# --- requests ---------------------------------------------------------------


def _with_lifecycle(body, lifecycle):
    if lifecycle:
        body["lifecycle"] = list(lifecycle)
    return body


def build_requests(term, types, kommuner=(), limits=None):
    """The Bifrost requests for one search.

    * All ``RESOLVE`` types share one /resolve. Without a kommune filter the
      body is a single object; with one it is a batch with the kommune pinned
      per code (each at the maximum limit, as hits are merged afterwards).
    * All ``SEARCH`` types share one /search batch, ``body[i]`` for ``keys[i]``.
      With a kommune filter each asks for the maximum, since hits outside the
      kommuner are removed client-side.
    """
    types = list(types)
    if not term or not types:
        return []
    limits = limits or default_limits([t.key for t in types])
    filtering = bool(kommuner)
    requests = []

    resolve_types = [t for t in types if t.endpoint == RESOLVE]
    if resolve_types:
        lifecycle = sorted({lc for t in resolve_types for lc in (t.lifecycle or ())})
        if filtering:
            body = [
                _with_lifecycle(
                    {
                        "input": term,
                        "components": {"kommune": code},
                        "limit": RESOLVE_MAX_LIMIT,
                    },
                    lifecycle,
                )
                for code in kommuner
            ]
        else:
            limit = min(RESOLVE_MAX_LIMIT, max(limits[t.key] for t in resolve_types))
            body = _with_lifecycle({"input": term, "limit": limit}, lifecycle)
        requests.append(
            BifrostRequest(RESOLVE, body, tuple(t.key for t in resolve_types))
        )

    search_types = [t for t in types if t.endpoint == SEARCH]
    if search_types:
        body = [
            _with_lifecycle(
                {
                    "input": term,
                    "target": t.target,
                    "limit": SEARCH_MAX_LIMIT
                    if filtering
                    else min(SEARCH_MAX_LIMIT, limits[t.key]),
                },
                t.lifecycle,
            )
            for t in search_types
        ]
        requests.append(
            BifrostRequest(SEARCH, body, tuple(t.key for t in search_types))
        )
    return requests


def plan_search(
    text,
    selected_keys,
    kommunefilter="",
    total=DEFAULT_TOTAL_LIMIT,
    types=TYPES,
):
    """Parse the query and kommune filter setting and build the requests."""
    query = parse_query(text, selected_keys, types)
    known = types_by_key(types)
    chosen = tuple(known[k] for k in query.keys)
    kommuner = parse_kommunekoder(kommunefilter)
    limits = default_limits(query.keys, total)
    return SearchPlan(
        term=query.term,
        types=chosen,
        kommuner=kommuner,
        limits=limits,
        requests=build_requests(query.term, chosen, kommuner, limits),
        membership_targets=membership_targets(chosen) if kommuner else (),
    )


# --- rows -------------------------------------------------------------------


def _is_apartment(match):
    c = match.get("components") or {}
    return bool(c.get("floor") or c.get("door"))


def make_row(search_type, match, kind=None, ref=None):
    """A result row. The contract the plugin UI relies on:

    ``key``         type key ("adr", ...)
    ``title``       type title ("Husnumre", ...)
    ``status``      "ok" (or "error", see ``error_row``)
    ``text``        display text
    ``kind``        Bifrost kind of ``ref`` ("entrance", "unit", "ejendom", ...)
    ``ref``         ``{"kind", "id"}``, the /project input for this hit
    ``point``       GeoJSON Point in EPSG:25832, always present for ok rows
    ``geometry``    GeoJSON geometry in EPSG:25832 or None (search results
                    never carry it; fetch with ``geometry_request``)
    ``lifecycle``   "current", "retired", ...

    and for information: ``refs``, ``result``, ``components``, ``ejendom``
    and ``score``.
    """
    ref = dict(ref or match.get("ref") or {})
    kind = kind or ref.get("kind")
    geometry = match.get("geometry")
    return {
        "key": search_type.key,
        "title": search_type.title,
        "status": STATUS_OK,
        "text": display_text(match, kind),
        "kind": kind,
        "ref": ref,
        "point": match.get("point"),
        "geometry": geometry.get("geojson") if geometry else None,
        "lifecycle": match.get("lifecycle"),
        "refs": dict(match.get("refs") or {}),
        "result": match.get("result") or "",
        "components": match.get("components") or {},
        "ejendom": match.get("ejendom"),
        "score": (match.get("meta") or {}).get("score"),
    }


def normalize(match, search_type):
    """The row for a Bifrost match under ``search_type``, or None to drop it.

    For /resolve types (``adr``): an entrance is a husnummer. A unit that has
    no floor/door is its entrance (Bifrost then returns only the unit, with
    ``refs.entrance``), so it becomes the entrance row. Apartments are kept
    as ``unit`` rows when ``accept_units``, and streets as ``street`` rows when
    ``accept_streets`` (/resolve gives streets, not husnumre, for a bare street
    name). Postcodes etc. that /resolve also returns are dropped.
    """
    ref = match.get("ref") or {}
    kind = ref.get("kind")
    target = search_type.target
    if search_type.endpoint == RESOLVE and target == "entrance" and kind == "unit":
        entrance = (match.get("refs") or {}).get("entrance")
        if entrance and not _is_apartment(match):
            return make_row(
                search_type, match, "entrance", {"kind": "entrance", "id": entrance}
            )
        if search_type.accept_units:
            return make_row(search_type, match)
        return None
    if search_type.endpoint == RESOLVE and kind == "street":
        return make_row(search_type, match) if search_type.accept_streets else None
    if kind != target:
        return None
    return make_row(search_type, match)


def error_row(search_type, message=None):
    """The row shown when a type's request failed."""
    return {
        "key": search_type.key,
        "title": search_type.title,
        "status": STATUS_ERROR,
        "text": tr("bifrost", "%s - Der skete en fejl") % tr("bifrost", search_type.title),
        "message": message,
        "kind": None,
        "ref": None,
        "point": None,
        "geometry": None,
        "lifecycle": None,
    }


KOMMUNEFILTER_KEY = "kommunefilter"


def kommunefilter_error_row(error):
    """The only row shown when the kommune filter could not be applied.

    ``error`` is what ``KommunefilterCache.load`` reported: ``UnknownKommune``
    or the exception of a failed request.
    """
    if isinstance(error, UnknownKommune):
        code = error.code.lstrip("0") or "0"
        text = tr("bifrost", "Ukendt kommunekode %s i kommunefilteret") % code
        message = tr(
            "bifrost",
            "Kommunefilteret i indstillingerne indeholder kommunekoden %s, som "
            "Bifrost ikke kender. Ret eller fjern koden under Indstillinger > "
            "Geosearch DK.",
        ) % code
    else:
        text = tr("bifrost", "%s - Der skete en fejl") % tr("bifrost", "Kommunefilter")
        message = tr("bifrost", "Kommunefilteret kunne ikke hentes fra Bifrost: %s") % error
    return {
        "key": KOMMUNEFILTER_KEY,
        "title": "Kommunefilter",
        "status": STATUS_ERROR,
        "text": text,
        "message": message,
        "kind": None,
        "ref": None,
        "point": None,
        "geometry": None,
        "lifecycle": None,
    }


def _row_id(row):
    ref = row.get("ref") or {}
    return (ref.get("kind"), ref.get("id"))


def _term_tokens(term):
    tokens = [t for t in re.split(r"[\s,]+", (term or "").lower()) if t]
    joined = [a + b for a, b in zip(tokens, tokens[1:])]
    return set(tokens + joined)


def rank_rows(rows, term):
    """Exact matrikelnummer hits first, otherwise Bifrost's order (stable).

    Bifrost ranks "3kg søll" as 3kg, 2kg, 3g, ... but a near-miss can win when
    the ejerlav matches better. "20 a" also matches matrikelnummer "20a".
    """
    tokens = _term_tokens(term)

    def exact(row):
        nr = ((row.get("components") or {}).get("matrikelnummer") or "").lower()
        return bool(nr) and nr in tokens

    return sorted(rows, key=lambda r: 0 if exact(r) else 1)


def _words(text):
    return re.findall(r"\w+", (text or "").lower())


def matches_term(row, term):
    """True if every word of ``term`` starts a word of the row's text.

    "hovedstaden" matches "Region Hovedstaden", but not Bifrost's fuzzy hits
    such as "8732 Hovedgård" or "1a, Hovedejerlavet, Stadil".
    """
    tokens = _words(term)
    if not tokens or row.get("status") != STATUS_OK:
        return False
    words = _words(row.get("text"))
    return all(any(w.startswith(t) for w in words) for t in tokens)


def rank_types(groups, term):
    """Order ``[(key, rows)]`` so that types with only fuzzy hits go last.

    Bifrost returns fuzzy hits for every type, so with many types selected a
    real hit in a late type ends up below rows of near-misses (#22). When a
    type has a ``matches_term`` row, the types whose ok rows all fail to
    match move after the others; the order is otherwise kept. When no type
    matches, nothing moves.
    """

    def fuzzy(rows):
        ok = [r for r in rows if r.get("status") == STATUS_OK]
        return bool(ok) and not any(matches_term(r, term) for r in ok)

    if not any(matches_term(r, term) for _, rows in groups for r in rows):
        return list(groups)
    return sorted(groups, key=lambda g: 1 if fuzzy(g[1]) else 0)


def dedupe(rows):
    """Drop repeated hits (same kind and ref id); the first one wins."""
    seen = set()
    out = []
    for row in rows:
        if row.get("status") == STATUS_OK:
            rid = _row_id(row)
            if rid in seen:
                continue
            seen.add(rid)
        out.append(row)
    return out


def _response_items(request, response):
    """``[(keys, response_item)]`` for a request and its decoded response."""
    if isinstance(request.body, list):
        if not isinstance(response, list) or len(response) != len(request.body):
            raise ValueError("Bifrost batch response does not match the request")
        if request.endpoint == SEARCH:
            return [((k,), item) for k, item in zip(request.keys, response)]
        return [(request.keys, item) for item in response]
    return [(request.keys, response)]


def collect_rows(plan, responses, members=None):
    """Rows for a ``SearchPlan`` from its responses.

    ``responses[i]`` is the decoded JSON for ``plan.requests[i]``, or an
    exception if the request failed; the affected types then get an error
    row. A failed batch element (``error`` set) does the same. ``members``
    is required when ``plan.membership_targets`` is not empty (see
    ``kommunefilter.apply_kommunefilter``).

    Rows come grouped by type, each type sorted (``rank_rows``), filtered to
    the kommuner and cut to its limit, without duplicates. Types come in plan
    order, except that types with only fuzzy hits go last (``rank_types``).
    """
    known = {t.key: t for t in plan.types}
    matches = {k: [] for k in known}
    errors = {}

    for request, response in zip(plan.requests, responses):
        if isinstance(response, BaseException):
            for k in request.keys:
                errors.setdefault(k, str(response))
            continue
        try:
            items = _response_items(request, response)
        except (ValueError, TypeError) as e:
            for k in request.keys:
                errors.setdefault(k, str(e))
            continue
        for keys, item in items:
            item = item or {}
            if item.get("error"):
                for k in keys:
                    errors.setdefault(k, str(item["error"]))
            for k in keys:
                matches[k].extend(item.get("matches") or [])

    rows = []
    groups = []
    hidden = {}
    for key, search_type in known.items():
        type_matches = matches[key]
        if search_type.endpoint == RESOLVE and len(plan.kommuner) > 1:
            type_matches = sorted(
                type_matches,
                key=lambda m: -((m.get("meta") or {}).get("score") or 0),
            )
        type_rows = dedupe(
            r for r in (normalize(m, search_type) for m in type_matches) if r
        )
        type_rows, hidden[key] = apply_kommunefilter(
            type_rows, plan.kommuner, members, search_type
        )
        type_rows = rank_rows(type_rows, plan.term)[: plan.limits[key]]
        if key in errors:
            type_rows.append(error_row(search_type, errors[key]))
        groups.append((key, type_rows))
    for _, type_rows in rank_types(groups, plan.term):
        rows.extend(type_rows)
    return SearchResult(dedupe(rows), hidden)


# --- geometry ---------------------------------------------------------------


STEDNAVN_GEOMETRY_LIMITS = (10, SEARCH_MAX_LIMIT)


def geometry_request(row, attempt=0):
    """The request that fetches the full geometry of an ok row, or None.

    /project does not take stednavne, so a stednavn is searched again by its
    name with geometry, and ``geometry_from_response`` picks the same ref.
    Such a search returns whole geometries, so it first asks for 10 hits; if
    the stednavn is not among them, call again with ``attempt=1`` (100 hits).
    Returns None when there is nothing more to try.
    """
    ref = row["ref"]
    if ref["kind"] == "stednavn":
        if attempt >= len(STEDNAVN_GEOMETRY_LIMITS):
            return None
        body = {
            "input": row.get("result") or row["text"],
            "target": "stednavn",
            "limit": STEDNAVN_GEOMETRY_LIMITS[attempt],
            "geometry": True,
        }
        return BifrostRequest(SEARCH, body, (row["key"],))
    if attempt > 0:
        return None
    body = {"input": dict(ref), "target": ref["kind"], "limit": 1, "geometry": True}
    lifecycle = row.get("lifecycle")
    if lifecycle and lifecycle != "current":
        body["lifecycle"] = [lifecycle]
    return BifrostRequest(PROJECT, body, (row["key"],))


def geometry_from_response(row, response):
    """GeoJSON geometry (EPSG:25832) from a ``geometry_request`` response, or None.

    A /project of a ref returns that one feature, though possibly under a more
    specific ref (an entrance that is also a unit comes back as the unit), so
    its first match is used. A stednavn search must contain the same ref.
    """
    matches = (response or {}).get("matches") or []
    if row["ref"]["kind"] == "stednavn":
        matches = [
            m for m in matches if (m.get("ref") or {}).get("id") == row["ref"]["id"]
        ]
    for match in matches:
        geometry = match.get("geometry")
        return geometry.get("geojson") if geometry else None
    return None


def row_geometry(row) -> Optional[dict]:
    """The best geometry known for a row: its geometry, else its point."""
    return row.get("geometry") or row.get("point")
