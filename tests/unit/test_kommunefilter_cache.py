"""``KommunefilterCache`` with a fake ``send``, the error row and the texts (#11)."""

import pytest

from geosearch_dk.bifrost import (
    PROJECT,
    STATUS_ERROR,
    KommunefilterCache,
    UnknownKommune,
    kommunefilter_error_row,
)
from geosearch_dk.kommunefilter_info import hidden_row_text, info_html, migration_text


def kommune_match(code):
    return {
        "ref": {"kind": "kommune", "id": "k" + code},
        "components": {"kommuner": [{"kommunekode": code}]},
    }


class FakeBifrost:
    """``send`` for the cache. Replies at once, or later with ``deliver()``."""

    def __init__(self, kommuner=("0101", "0851"), members=None, page_size=2):
        self.kommuner = kommuner
        # (code, target) -> ids
        self.members = members or {}
        self.page_size = page_size
        self.sent = []
        self.held = None
        self.fail = None

    def send(self, requests, callback):
        self.sent.extend(requests)
        if self.held is not None:
            self.held.append((requests, callback))
        else:
            callback([self.reply(r) for r in requests])

    def deliver(self):
        held, self.held = self.held, []
        for requests, callback in held:
            callback([self.reply(r) for r in requests])

    def reply(self, request):
        if self.fail:
            return self.fail
        body = request.body
        if request.endpoint != PROJECT:
            code = body["input"]
            return {"matches": [kommune_match(code)] if code in self.kommuner else []}
        code = body["input"]["id"][1:]
        ids = sorted(self.members.get((code, body["target"]), ()))
        start = int(body.get("cursor") or 0)
        page = ids[start : start + self.page_size]
        nxt = str(start + self.page_size) if start + self.page_size < len(ids) else None
        return {
            "matches": [{"ref": {"kind": body["target"], "id": i}} for i in page],
            "next": nxt,
        }


def load(cache, codes, targets):
    got = []
    cache.load(codes, targets, got.append)
    return got


def test_union_of_members_with_paging():
    fake = FakeBifrost(
        members={
            ("0101", "region"): {"r1"},
            ("0851", "region"): {"r2"},
            ("0101", "politikreds"): {"p1", "p2", "p3", "p4", "p5"},
        }
    )
    cache = KommunefilterCache(fake.send)
    got = load(cache, ("0101", "0851"), ("region", "politikreds"))
    assert got == [{"region": {"r1", "r2"}, "politikreds": {"p1", "p2", "p3", "p4", "p5"}}]
    project_pages = [r for r in fake.sent if r.endpoint == PROJECT]
    # 2 region lists (one page each), politikreds 3 pages for 0101 and 1 for 0851
    assert len(project_pages) == 6
    assert cache.refs["0101"] == {"kind": "kommune", "id": "k0101"}


def test_cached_for_the_session():
    fake = FakeBifrost(members={("0101", "region"): {"r1"}})
    cache = KommunefilterCache(fake.send)
    load(cache, ("0101",), ("region",))
    sent = len(fake.sent)
    assert load(cache, ("0101",), ("region",)) == [{"region": {"r1"}}]
    assert load(cache, ("0101",), ()) == [{}]
    assert len(fake.sent) == sent


def test_codes_are_checked_without_targets():
    fake = FakeBifrost()
    got = load(KommunefilterCache(fake.send), ("0101",), ())
    assert got == [{}]
    assert len(fake.sent) == 1


def test_unknown_kommune_is_reported_and_remembered():
    fake = FakeBifrost(kommuner=("0101",))
    cache = KommunefilterCache(fake.send)
    (error,) = load(cache, ("0101", "9999"), ("region",))
    assert isinstance(error, UnknownKommune) and error.code == "9999"
    assert not [r for r in fake.sent if r.endpoint == PROJECT]
    sent = len(fake.sent)
    (error,) = load(cache, ("9999",), ())
    assert isinstance(error, UnknownKommune)
    assert len(fake.sent) == sent


def test_failures_are_reported_and_not_cached():
    fake = FakeBifrost()
    fake.fail = OSError("netværk")
    cache = KommunefilterCache(fake.send)
    (error,) = load(cache, ("0101",), ("region",))
    assert error is fake.fail
    fake.fail = None
    assert load(cache, ("0101",), ("region",)) == [{"region": frozenset()}]


def test_running_lookups_are_shared():
    fake = FakeBifrost(members={("0101", "region"): {"r1"}})
    fake.held = []
    cache = KommunefilterCache(fake.send)
    first, second = [], []
    cache.load(("0101",), ("region",), first.append)
    cache.load(("0101",), ("region",), second.append)
    assert len(fake.sent) == 1
    fake.deliver()
    fake.deliver()
    assert first == second == [{"region": {"r1"}}]
    assert len(fake.sent) == 2


def test_abort_drops_running_lookups():
    fake = FakeBifrost()
    fake.held = []
    cache = KommunefilterCache(fake.send)
    got = []
    cache.load(("0101",), (), got.append)
    cache.abort()
    fake.deliver()
    assert got == [] and cache.refs == {}
    # A new load starts again instead of waiting for the dropped one.
    cache.load(("0101",), (), got.append)
    fake.deliver()
    assert got == [{}]


def test_clear_forgets_everything():
    fake = FakeBifrost()
    cache = KommunefilterCache(fake.send)
    load(cache, ("0101",), ())
    cache.clear()
    assert cache.refs == {}
    load(cache, ("0101",), ())
    assert len(fake.sent) == 2


def test_error_row_for_unknown_kommune():
    row = kommunefilter_error_row(UnknownKommune("0999"))
    assert row["status"] == STATUS_ERROR
    assert row["text"] == "Ukendt kommunekode 999 i kommunefilteret"
    assert "999" in row["message"] and "Indstillinger" in row["message"]
    assert row["ref"] is None and row["point"] is None


def test_error_row_for_failed_request():
    row = kommunefilter_error_row(OSError("timeout"))
    assert row["status"] == STATUS_ERROR
    assert row["text"] == "Kommunefilter - Der skete en fejl"
    assert "timeout" in row["message"]


@pytest.mark.parametrize(
    "count, text",
    [
        (0, None),
        (1, "1 resultat uden for kommunefilteret er skjult"),
        (12, "12 resultater uden for kommunefilteret er skjult"),
    ],
)
def test_hidden_row_text(count, text):
    assert hidden_row_text(count) == text


def test_info_texts():
    assert migration_text() == "Kommunefilteret virker nu anderledes – læs hvorfor"
    for part in ("100 bedste hits", "1a", "Horsens (615)", "vestergade 1 horsens"):
        assert part in info_html()
    assert hidden_row_text(12) in info_html()
