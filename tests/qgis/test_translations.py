"""The English translation: en.qt.qm is up to date with en.qt.ts, and the
plugin shows one language at a time, following QGIS' locale/userLocale."""

import os
import xml.etree.ElementTree as ET

import pytest
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtWidgets import QCheckBox

from conftest import ROOT

I18N = os.path.join(ROOT, "src", "geosearch_dk", "i18n")


def test_qm_has_every_ts_translation():
    translator = QTranslator()
    assert translator.load(os.path.join(I18N, "en.qt.qm"))
    root = ET.parse(os.path.join(I18N, "en.qt.ts")).getroot()
    checked = 0
    for ctx in root.iter("context"):
        name = ctx.findtext("name")
        for message in ctx.iter("message"):
            source, translation = message.findtext("source"), message.findtext("translation")
            got = translator.translate(name.encode("utf-8"), source.encode("utf-8"))
            assert got == translation, (name, source)
            checked += 1
    assert checked > 0


EXPECTED = {
    "en_DK": {
        "placeholder": "Search address, place name, postal code, cadastral number etc.",
        "banner": "Why?</a>",
        "settings_title": "Geosearch DK - Settings",
        "checkbox": "Addresses ('adr')",
        "whatsnew_title": "Geosearch DK – what's new",
        "help": "hvad_er_nyt.en.html",
        "error_row": "Place names - An error occurred",
        "hidden_row": "3 results outside the municipality filter are hidden",
    },
    "da_DK": {
        "placeholder": "Søg adresse, stednavn, postnummer, matrikel m.m.",
        "banner": "Hvorfor?</a>",
        "settings_title": "Geosearch DK - Indstillinger",
        "checkbox": "Husnumre ('adr')",
        "whatsnew_title": "Geosearch DK – hvad er nyt",
        "help": "hvad_er_nyt.html",
        "error_row": "Stednavne - Der skete en fejl",
        "hidden_row": "3 resultater uden for kommunefilteret er skjult",
    },
}


@pytest.fixture
def user_locale():
    s = QSettings()
    old = s.value("locale/userLocale")

    def set_locale(name):
        s.setValue("locale/userLocale", name)

    yield set_locale
    if old is None:
        s.remove("locale/userLocale")
    else:
        s.setValue("locale/userLocale", old)


@pytest.mark.parametrize("locale", sorted(EXPECTED))
def test_plugin_speaks_one_language(locale, user_locale, iface, qgis_parent, monkeypatch):
    from geosearch_dk import classFactory, kommunefilter_info, whatsnew
    from geosearch_dk.bifrost.core import error_row
    from geosearch_dk.bifrost.types import TYPES
    from geosearch_dk.config import OptionsFactory

    monkeypatch.delenv("BIFROST_KEY", raising=False)
    expected = EXPECTED[locale]
    user_locale(locale)
    plugin = classFactory(iface)
    plugin.initGui()
    try:
        box = plugin.searchwidget
        assert box.searchEdit.placeholderText() == expected["placeholder"]
        box.updateBanner()
        assert expected["banner"] in box.bannerLabel.text()

        page = OptionsFactory(plugin.settings).createWidget(qgis_parent)
        dialog = page.config_widget
        assert dialog.windowTitle() == expected["settings_title"]
        assert dialog.findChild(QCheckBox, "search_adr").text() == expected["checkbox"]
        assert kommunefilter_info.info_title() in dialog.kommunefilterInfoLabel.text()

        assert error_row(TYPES[1])["text"] == expected["error_row"]
        assert kommunefilter_info.hidden_row_text(3) == expected["hidden_row"]

        shown = whatsnew.show_whats_new(qgis_parent, settings=plugin.settings)
        assert shown.windowTitle() == expected["whatsnew_title"]
        assert shown.browser.source().toLocalFile().endswith("/" + expected["help"])
        whatsnew.close_whats_new()
    finally:
        plugin.unload()

    # Unloading removes the translator again.
    assert error_row(TYPES[1])["text"] == "Stednavne - Der skete en fejl"
    assert QCoreApplication.translate("SearchBox", "Luk") == "Luk"


def test_untranslated_locale_is_danish(user_locale):
    from geosearch_dk.language import ui_language

    for name, expected in (("de_DE", "da"), ("en_GB", "en"), ("da_DK", "da")):
        user_locale(name)
        assert ui_language() == expected
