"""The client-side kommune filter (#11) in the plugin, against the mock Bifrost."""

import pytest
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QPushButton

from conftest import SETTINGS_GROUP
from test_fetcher import wait_for

TYPE_KEYS = ("adr", "ste", "pos", "mat", "kom", "ops", "pol", "reg")


def known_kommuner(bifrost_mock, *codes):
    """Answer the kommune ref lookups the recordings lack.

    The plugin looks up every code's ref, also when no type needs /project
    membership, so a typo is reported. The case recordings only have refs when
    a type needs membership.
    """
    from geosearch_dk.bifrost.kommunefilter import kommune_ref_request

    for code in codes:
        code = code.zfill(4)
        match = {
            "ref": {"kind": "kommune", "id": "kommune-" + code},
            "components": {"kommuner": [{"kommunekode": code}]},
        }
        bifrost_mock.index.add(
            "search", kommune_ref_request(code).body, 200, {"matches": [match]}
        )


def use_filter(codes, types):
    s = QSettings()
    s.setValue(SETTINGS_GROUP + "/kommunefilter", codes)
    s.setValue(SETTINGS_GROUP + "/kommunefilter_enabled", True)
    s.setValue(SETTINGS_GROUP + "/kommunefilter_migrated", True)
    for key in TYPE_KEYS:
        s.setValue(SETTINGS_GROUP + "/search_" + key, key in types)


@pytest.fixture
def fetcher(bifrost_mock):
    from geosearch_dk.bifrost.fetcher import BifrostFetcher
    from geosearch_dk.config import Settings

    f = BifrostFetcher(Settings())
    f.events = []
    f.finished.connect(lambda: f.events.append("finished"))
    f.kommunefilter_error.connect(lambda msg: f.events.append(("error", msg)))
    yield f
    f.abort_all()


def search(fetcher, text):
    del fetcher.events[:]
    fetcher.fetch(text)
    wait_for(lambda: "finished" in fetcher.events)
    return fetcher.get_result()


def test_filter_is_off_by_default(fetcher, bifrost_mock):
    QSettings().setValue(SETTINGS_GROUP + "/kommunefilter", "615")
    assert fetcher.kommunefilter() == ""


def test_vestergade_1_in_koebenhavn(bifrost_mock, fetcher):
    known_kommuner(bifrost_mock, "101")
    use_filter("101", ["adr"])
    rows = search(fetcher, "vestergade 1")
    assert rows[0]["text"] == "Vestergade 1, 1456 København K"
    assert all(r["status"] == "ok" for r in rows)


def test_matrikel_1a_horsens_is_all_hidden(bifrost_mock, fetcher):
    # The documented loss (#2): no Horsens parcel in the national top 100
    known_kommuner(bifrost_mock, "615")
    use_filter("615", ["mat"])
    rows = search(fetcher, "1a")
    assert rows == []
    assert fetcher.hidden["mat"] > 0
    # The kommune ref is looked up once per session
    search(fetcher, "1a")
    refs = [e for e in bifrost_mock.request_log() if e["endpoint"] == "search"
            and any(b.get("target") == "kommune" for b in _bodies(e))]
    assert len(refs) == 1


def _bodies(entry):
    body = entry["body"]
    return body if isinstance(body, list) else [body]


def test_unknown_kommune_gives_an_error_row(bifrost_mock, fetcher):
    use_filter("999", ["adr"])
    rows = search(fetcher, "vestergade 1")
    assert [r["text"] for r in rows] == ["Ukendt kommunekode 999 i kommunefilteret"]
    assert rows[0]["status"] == "error"
    assert [e for e in fetcher.events if e != "finished"][0][0] == "error"


def test_hidden_row_in_the_popup(bifrost_mock, plugin, monkeypatch):
    known_kommuner(bifrost_mock, "101", "851")
    use_filter("101,851", ["ste"])
    plugin.searchwidget.readconfig()
    suggester = plugin.searchwidget.suggester
    explained = []
    monkeypatch.setattr(suggester, "hiddeninfo_func", lambda: explained.append(True))
    fetcher = suggester.fetcher
    done = []
    fetcher.finished.connect(lambda: done.append(True))
    plugin.searchwidget.searchEdit.setText("vor frue")
    suggester.invoke_fetcher()
    wait_for(lambda: done)

    tree = suggester.resultlistwidget
    count = tree.topLevelItemCount()
    last = tree.topLevelItem(count - 1)
    hidden = sum(fetcher.hidden.values())
    assert count > 1 and hidden > 0
    assert last.text(0) == "%d resultater uden for kommunefilteret er skjult" % hidden
    assert not last.flags() & Qt.ItemFlag.ItemIsSelectable
    assert all(
        tree.topLevelItem(i).flags() & Qt.ItemFlag.ItemIsSelectable
        for i in range(count - 1)
    )

    # Choosing the grey row explains the filter; it does not zoom anywhere
    suggester.onResultSelected(last, 0)
    assert explained == [True]
    assert plugin.searchwidget.markers == []


def test_migration_notice(iface, monkeypatch):
    from geosearch_dk import classFactory
    from geosearch_dk.searchbox import SearchBox

    QSettings().setValue(SETTINGS_GROUP + "/kommunefilter", "615")
    shown = []
    monkeypatch.setattr(
        SearchBox, "showKommunefilterMigrationNotice", lambda self: shown.append(self)
    )
    p = classFactory(iface)
    p.initGui()
    try:
        assert len(shown) == 1
        assert p.settings.value("kommunefilter_enabled") is True
    finally:
        p.unload()
    # Not again on the next start
    p = classFactory(iface)
    p.initGui()
    p.unload()
    assert len(shown) == 1


def test_migration_notice_buttons(plugin, monkeypatch):
    from geosearch_dk import kommunefilter_info, whatsnew

    box = plugin.searchwidget
    bar = box.qgisIface.messageBar()
    pushed = []
    monkeypatch.setattr(bar, "pushWidget", lambda w, *a, **kw: pushed.append(w))
    opened = []
    monkeypatch.setattr(box, "show_settings", lambda: opened.append("settings"))
    monkeypatch.setattr(
        whatsnew, "show_whats_new", lambda *a, **kw: opened.append(kw.get("anchor"))
    )
    box.showKommunefilterMigrationNotice()
    (widget,) = pushed
    assert kommunefilter_info.migration_text() in widget.text()
    buttons = {b.text(): b for b in widget.findChildren(QPushButton)}
    buttons["Åbn indstillinger"].pressed.emit()
    buttons["Hvad er nyt"].pressed.emit()
    assert opened == ["settings", "kommunefilter"]
