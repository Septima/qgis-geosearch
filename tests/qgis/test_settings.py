"""Settings with real QSettings: migration from 3.x and the settings page."""

import pytest
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QCheckBox

from conftest import SETTINGS_GROUP

TYPE_KEYS = ("adr", "ste", "pos", "mat", "kom", "ops", "pol", "reg")
# Dataforsyningen tokens from 3.x (made up): none of them work with Bifrost
OLD_TOKEN = "a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"
OWN_TOKEN = "my-own-dataforsyningen-token"


@pytest.fixture
def legacy_settings():
    """Where older qgissettingmanager versions stored the settings."""
    s = QSettings("Geosearch DK", "Geosearch DK")
    s.clear()
    yield s
    s.clear()
    s.sync()


def stored(name):
    return QSettings().value(SETTINGS_GROUP + "/" + name)


def has(name):
    return QSettings().contains(SETTINGS_GROUP + "/" + name)


def seed(**values):
    s = QSettings()
    for name, value in values.items():
        s.setValue(SETTINGS_GROUP + "/" + name, value)
    s.sync()


@pytest.mark.parametrize("token", [OLD_TOKEN, OWN_TOKEN])
def test_migration_drops_the_token_and_keeps_the_rest(token, legacy_settings):
    from geosearch_dk.config import Settings

    seed(token=token, search_reg=False, search_adr=True, kommunefilter="101")
    settings = Settings()
    assert not has("token")
    assert stored("kommunefilter") == "101"
    assert settings.value("search_reg") is False
    assert settings.value("search_adr") is True
    assert settings.selected_type_keys() == tuple(k for k in TYPE_KEYS if k != "reg")
    # Nothing was set, so the defaults are not stored
    assert not has("bifrost_key") and not has("bifrost_url")


def test_migration_drops_the_legacy_token(legacy_settings):
    from geosearch_dk.config import Settings

    legacy_settings.setValue("token", OWN_TOKEN)
    legacy_settings.sync()
    Settings()
    assert not QSettings("Geosearch DK", "Geosearch DK").contains("token")


def test_migration_without_settings(legacy_settings):
    from geosearch_dk.config import Settings

    settings = Settings()
    assert not has("token")
    assert settings.selected_type_keys() == TYPE_KEYS
    assert settings.value("kommunefilter") == ""


def test_new_type_is_off_after_upgrade(monkeypatch):
    from geosearch_dk.bifrost.types import TYPES, SearchType
    from geosearch_dk.config import Settings, settings as settings_module

    new = SearchType("new", "Ny type", "search", "new")
    monkeypatch.setattr(settings_module, "TYPES", TYPES + (new,))
    seed(token=OWN_TOKEN, search_adr=True)
    settings = Settings()
    assert settings.value("search_new") is False
    assert settings.selected_type_keys() == TYPE_KEYS


def test_key_and_url_fallbacks(monkeypatch):
    from geosearch_dk.config import Settings
    from geosearch_dk.config import settings as settings_module

    monkeypatch.delenv("BIFROST_KEY", raising=False)
    settings = Settings()
    assert settings.bifrost_url() == settings_module.DEFAULT_BIFROST_URL
    assert settings.bifrost_key() == settings_module.DEFAULT_BIFROST_KEY == ""
    monkeypatch.setenv("BIFROST_KEY", "env-key")
    assert settings.bifrost_key() == "env-key"
    settings.set_value("bifrost_key", " own-key ")
    settings.set_value("bifrost_url", " http://localhost:1 ")
    assert settings.bifrost_key() == "own-key"
    assert settings.bifrost_url() == "http://localhost:1"


def page_widgets(page):
    dialog = page.config_widget
    boxes = [
        w
        for w in dialog.findChildren(QCheckBox)
        if w.objectName().startswith("search_")
    ]
    return dialog, boxes


def test_settings_page(qgis_parent):
    from geosearch_dk.config import OptionsFactory, Settings
    from geosearch_dk.config import settings as settings_module

    settings = Settings()
    page = OptionsFactory(settings).createWidget(qgis_parent)
    dialog, boxes = page_widgets(page)

    assert [b.objectName() for b in boxes] == ["search_" + k for k in TYPE_KEYS]
    assert all(b.isChecked() for b in boxes)
    assert boxes[0].text() in ("Husnumre ('adr')", "Addresses ('adr')")
    assert dialog.findChild(QCheckBox, "search_mat").text().endswith("('ejd')")
    assert dialog.bifrost_key.text() == ""
    assert dialog.bifrost_url.text() == ""
    assert dialog.bifrost_url.placeholderText() == settings_module.DEFAULT_BIFROST_URL
    assert settings_module.BIFROST_KEY_HELP_URL in dialog.bifrostKeyLinkLabel.text()
    assert dialog.advancedGroupBox.isCollapsed()
    assert not hasattr(dialog, "token")


def test_settings_page_round_trip(qgis_parent):
    from geosearch_dk.bifrost.fetcher import BifrostFetcher
    from geosearch_dk.config import OptionsFactory, Settings

    settings = Settings()
    updated = []
    settings.settings_updated.connect(lambda: updated.append(True))
    page = OptionsFactory(settings).createWidget(qgis_parent)
    dialog, _ = page_widgets(page)
    dialog.bifrost_key.setText("test-key")
    dialog.bifrost_url.setText("http://localhost:9999")
    dialog.findChild(QCheckBox, "search_pos").setChecked(False)
    page.apply()

    assert updated == [True]
    assert stored("bifrost_key") == "test-key"
    assert stored("bifrost_url") == "http://localhost:9999"
    expected = tuple(k for k in TYPE_KEYS if k != "pos")
    fetcher = BifrostFetcher(settings)
    assert fetcher.base_url() == "http://localhost:9999"
    assert fetcher.key() == "test-key"
    assert tuple(fetcher.selected_keys()) == expected

    again = OptionsFactory(Settings()).createWidget(qgis_parent)
    dialog2, boxes = page_widgets(again)
    assert dialog2.bifrost_key.text() == "test-key"
    assert dialog2.bifrost_url.text() == "http://localhost:9999"
    assert [b.objectName()[7:] for b in boxes if b.isChecked()] == list(expected)


def test_kommunefilter_from_3x_is_switched_on_once(legacy_settings):
    from geosearch_dk.config import Settings

    seed(kommunefilter="101,851")
    settings = Settings()
    assert settings.kommunefilter_migrated_now is True
    assert settings.value("kommunefilter_enabled") is True
    assert settings.value("kommunefilter") == "101,851"
    again = Settings()
    assert again.kommunefilter_migrated_now is False
    assert again.value("kommunefilter_enabled") is True


def test_kommunefilter_is_off_by_default(legacy_settings):
    from geosearch_dk.config import Settings

    settings = Settings()
    assert settings.kommunefilter_migrated_now is False
    assert settings.value("kommunefilter_enabled") is False
    # Typing codes later does not switch it on behind the user's back
    settings.set_value("kommunefilter", "101")
    assert Settings().value("kommunefilter_enabled") is False


def test_kommunefilter_page(qgis_parent, monkeypatch):
    from geosearch_dk import kommunefilter_info, whatsnew
    from geosearch_dk.config import OptionsFactory, Settings

    settings = Settings()
    page = OptionsFactory(settings).createWidget(qgis_parent)
    dialog = page.config_widget
    assert not dialog.kommunefilter_enabled.isChecked()
    assert not dialog.kommunefilter.isEnabled()
    info = dialog.kommunefilterInfoLabel
    assert info.wordWrap() and info.isEnabled()
    assert "100 bedste hits" in info.text() and "Horsens (615)" in info.text()

    dialog.kommunefilter_enabled.setChecked(True)
    assert dialog.kommunefilter.isEnabled()
    dialog.kommunefilter.setText("615")
    page.apply()
    assert stored("kommunefilter") == "615"
    assert settings.value("kommunefilter_enabled") is True

    dialog.kommunefilter_enabled.setChecked(False)
    assert not dialog.kommunefilter.isEnabled()

    calls = []
    monkeypatch.setattr(
        whatsnew, "show_whats_new", lambda *a, **kw: calls.append((a, kw))
    )
    dialog.kommunefilterWhatsNewLabel.linkActivated.emit("#kommunefilter")
    ((args, kwargs),) = calls
    assert args == (dialog,)
    assert kwargs["anchor"] == kommunefilter_info.WHATSNEW_ANCHOR == "kommunefilter"
