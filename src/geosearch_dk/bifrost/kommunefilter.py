"""Client-side kommune filter (#11).

Bifrost has no filter parameter on /search, so the plugin filters the hits
itself:

* /resolve pins the kommune (``components.kommune``), one batch element per code.
* Types with ``kommune_filter == FILTER_COMPONENTS`` are kept when one of the
  hit's ``components.kommuner`` is selected.
* Types with ``kommune_filter == FILTER_PROJECT`` (regions, kredse, ...) carry
  no kommune in their components. They are kept when their ref id is a member
  of /project(kommune ref -> target). The caller fetches the members once per
  kommune and target and caches them; this module only builds the requests and
  reads the responses.

Pure Python: must not import qgis or PyQt.
"""

import re

from .types import FILTER_PROJECT, PROJECT, SEARCH, BifrostRequest

PROJECT_MAX_LIMIT = 500


class UnknownKommune(ValueError):
    """A kommunekode in the filter that Bifrost does not know."""

    def __init__(self, code):
        super().__init__("Ukendt kommunekode %s" % code)
        self.code = code


def parse_kommunekoder(text):
    """Kommunekoder in a free-text setting, as 4-digit strings in input order.

    Like the GSearch plugin, every group of digits is a code; separators are
    free. Three-digit codes are padded ("101" -> "0101"). Duplicates are dropped.
    """
    codes = []
    for group in re.findall(r"\d+", text or ""):
        code = group.zfill(4)
        if code not in codes:
            codes.append(code)
    return tuple(codes)


def kommune_ref_request(code):
    """Request that looks up the Bifrost ref of kommune ``code``."""
    return BifrostRequest(SEARCH, {"input": code, "target": "kommune", "limit": 1})


def kommune_ref_from_response(code, response):
    """The ``{"kind", "id"}`` ref from a ``kommune_ref_request`` response.

    Raises ``UnknownKommune`` when the top hit is not kommune ``code``.
    """
    matches = (response or {}).get("matches") or []
    if matches:
        match = matches[0]
        kommuner = (match.get("components") or {}).get("kommuner") or []
        if any(k.get("kommunekode") == code for k in kommuner):
            return dict(match["ref"])
    raise UnknownKommune(code)


def membership_request(ref, target, cursor=None, limit=PROJECT_MAX_LIMIT):
    """One page of the ``target`` refs inside the kommune ``ref``."""
    body = {"input": dict(ref), "target": target, "limit": limit}
    if cursor:
        body["cursor"] = cursor
    return BifrostRequest(PROJECT, body)


def membership_from_response(response):
    """``(ids, next_cursor)`` from a ``membership_request`` response.

    ``next_cursor`` is None on the last page; otherwise request the next page
    with ``membership_request(ref, target, cursor=next_cursor)``.
    """
    response = response or {}
    ids = {m["ref"]["id"] for m in response.get("matches") or []}
    return ids, response.get("next") or None


def membership_targets(types):
    """Targets whose filter needs /project memberships, in type order."""
    targets = []
    for t in types:
        if t.kommune_filter == FILTER_PROJECT and t.target not in targets:
            targets.append(t.target)
    return tuple(targets)


def in_kommuner_by_components(row, codes):
    kommuner = (row.get("components") or {}).get("kommuner") or []
    return any(k.get("kommunekode") in codes for k in kommuner)


def in_kommuner_by_membership(row, member_ids):
    return (row.get("ref") or {}).get("id") in member_ids


class MissingMembership(KeyError):
    """``apply_kommunefilter`` needs memberships for a target it was not given."""


def apply_kommunefilter(rows, codes, members, search_type):
    """Split ``rows`` of one type into ``(kept, hidden_count)``.

    ``members`` maps a target to the set of ref ids inside any of ``codes``
    (the union over the selected kommuner). It is only read for types with
    ``FILTER_PROJECT``. Error rows are always kept. With no codes, everything
    is kept.
    """
    if not codes:
        return list(rows), 0
    codes = set(codes)
    if search_type.kommune_filter == FILTER_PROJECT:
        if members is None or search_type.target not in members:
            raise MissingMembership(search_type.target)
        member_ids = members[search_type.target]

        def keep(row):
            return in_kommuner_by_membership(row, member_ids)

    else:

        def keep(row):
            return in_kommuner_by_components(row, codes)

    kept = []
    hidden = 0
    for row in rows:
        if row.get("status") != "ok" or keep(row):
            kept.append(row)
        else:
            hidden += 1
    return kept, hidden


MAX_MEMBERSHIP_PAGES = 200


class KommunefilterCache:
    """Kommune refs and /project memberships, fetched once per session.

    ``send(requests, callback)`` sends ``BifrostRequest``s and calls
    ``callback(responses)`` once, where ``responses[i]`` is the decoded JSON
    or the exception (the contract of ``BifrostClient.send``). Lookups that
    are already running are shared, not sent twice. Unknown codes are
    remembered; failed requests are not.
    """

    def __init__(self, send):
        self._send = send
        self.refs = {}
        self.unknown = set()
        self.members = {}
        self._waiting = {}
        self._generation = 0

    def load(self, codes, targets, callback):
        """Call ``callback(members)`` when everything for ``codes`` is known.

        ``members`` maps each of ``targets`` to the ids inside any of
        ``codes`` (the argument ``apply_kommunefilter`` takes). On failure
        ``callback(error)`` is called instead: ``UnknownKommune`` for the
        first unknown code, or the exception of the failed request. Every
        code is looked up, also when ``targets`` is empty, so a mistyped code
        is always reported. The callback may run before ``load`` returns.
        """
        codes = tuple(codes)
        targets = tuple(targets)

        def after_members(error):
            if error is not None:
                callback(error)
                return
            callback(
                {
                    t: frozenset().union(*(self.members[(c, t)] for c in codes))
                    for t in targets
                }
            )

        def after_refs(error):
            if error is not None:
                callback(error)
                return
            for code in codes:
                if code in self.unknown:
                    callback(UnknownKommune(code))
                    return
            self._ensure_all(
                [("members", c, t) for t in targets for c in codes], after_members
            )

        self._ensure_all([("ref", c) for c in codes], after_refs)

    def abort(self):
        """Forget running lookups; their callbacks are never called."""
        self._generation += 1
        self._waiting = {}

    def clear(self):
        """Forget everything, e.g. when the Bifrost URL changes."""
        self.abort()
        self.refs = {}
        self.unknown = set()
        self.members = {}

    # --- internals --------------------------------------------------------

    def _known(self, key):
        if key[0] == "ref":
            return key[1] in self.refs or key[1] in self.unknown
        return key[1:] in self.members

    def _ensure_all(self, keys, done):
        missing = [k for k in dict.fromkeys(keys) if not self._known(k)]
        if not missing:
            done(None)
            return
        state = {"pending": len(missing), "finished": False}

        def one_done(error):
            if state["finished"]:
                return
            state["pending"] -= 1
            if error is not None or state["pending"] == 0:
                state["finished"] = True
                done(error)

        for key in missing:
            self._ensure(key, one_done)

    def _ensure(self, key, callback):
        if key in self._waiting:
            self._waiting[key].append(callback)
            return
        self._waiting[key] = [callback]
        if key[0] == "ref":
            self._load_ref(key, self._generation)
        else:
            self._load_members(key, self._generation)

    def _finish(self, key, generation, error=None):
        if generation != self._generation:
            return
        for callback in self._waiting.pop(key, []):
            callback(error)

    def _load_ref(self, key, generation):
        code = key[1]

        def on_response(responses):
            if generation != self._generation:
                return
            response = responses[0]
            if isinstance(response, BaseException):
                self._finish(key, generation, response)
                return
            try:
                self.refs[code] = kommune_ref_from_response(code, response)
            except UnknownKommune:
                self.unknown.add(code)
            self._finish(key, generation)

        self._send([kommune_ref_request(code)], on_response)

    def _load_members(self, key, generation):
        _, code, target = key
        ref = self.refs[code]
        ids = set()

        def step(cursor, page):
            self._send(
                [membership_request(ref, target, cursor)],
                lambda responses: on_page(responses[0], page),
            )

        def on_page(response, page):
            if generation != self._generation:
                return
            if isinstance(response, BaseException):
                self._finish(key, generation, response)
                return
            page_ids, next_cursor = membership_from_response(response)
            ids.update(page_ids)
            if next_cursor and page + 1 < MAX_MEMBERSHIP_PAGES:
                step(next_cursor, page + 1)
                return
            self.members[(code, target)] = frozenset(ids)
            self._finish(key, generation)

        step(None, 0)
