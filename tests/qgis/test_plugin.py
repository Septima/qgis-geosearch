"""The plugin in a real QGIS (3.44 LTR and 4.x): metadata, load/unload, settings, UI."""

import configparser
import os

import pytest
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QT_VERSION_STR, QSettings
from qgis.PyQt.QtWidgets import QDockWidget, QWidget

from conftest import ROOT, SETTINGS_GROUP, docks

PLUGIN_DIR = os.path.join(ROOT, "src", "geosearch_dk")
RESOURCES = ("adr", "ste", "pos", "mat", "kom", "ops", "pol", "reg")


def _version_int(text):
    parts = [int(p) for p in (text.split(".") + ["0", "0"])[:3]]
    return parts[0] * 10000 + parts[1] * 100 + parts[2]


def test_metadata_allows_this_qgis():
    meta = configparser.ConfigParser()
    meta.read(os.path.join(PLUGIN_DIR, "metadata.txt"), encoding="utf-8")
    general = meta["general"]
    running = Qgis.versionInt()
    assert _version_int(general["qgisMinimumVersion"]) <= running
    assert running <= _version_int(general["qgisMaximumVersion"]) + 99
    if QT_VERSION_STR.startswith("6"):
        assert general.getboolean("supportsQt6")


def test_plugin_package_metadata():
    import geosearch_dk

    assert geosearch_dk.name() == "Geosearch DK"
    assert geosearch_dk.version().startswith("Version ")


def test_load_and_unload(iface):
    from geosearch_dk import classFactory

    plugin = classFactory(iface)
    iface.registerOptionsWidgetFactory.assert_called_once_with(plugin.options_factory)
    plugin.initGui()
    assert len(docks(iface)) == 1
    assert docks(iface)[0].widget() is plugin.searchwidget
    plugin.unload()
    assert docks(iface) == []
    iface.unregisterOptionsWidgetFactory.assert_called_once_with(plugin.options_factory)


def test_reload(iface):
    """Plugin Reloader: unload, then load a fresh instance."""
    from geosearch_dk import classFactory

    for _ in range(2):
        plugin = classFactory(iface)
        plugin.initGui()
        assert len(docks(iface)) == 1
        plugin.unload()
        assert docks(iface) == []


def test_search_box_is_ready(plugin):
    box = plugin.searchwidget
    assert box.searchEdit.placeholderText().startswith("Søg adresse")
    assert box.markers == []
    assert box.config["maxresults"] == 25


def test_settings_defaults():
    from geosearch_dk.config import Settings

    settings = Settings()
    for key in RESOURCES:
        assert settings.value("search_" + key) is True, key
    assert settings.value("kommunefilter") == ""


def test_settings_are_stored_under_the_plugin_group():
    from geosearch_dk.config import Settings

    settings = Settings()
    settings.set_value("kommunefilter", "101,147")
    settings.set_value("search_mat", False)
    assert QSettings().value(SETTINGS_GROUP + "/kommunefilter") == "101,147"
    again = Settings()
    assert again.value("kommunefilter") == "101,147"
    assert again.value("search_mat") is False
    assert again.value("search_adr") is True


def test_settings_change_reaches_the_search_box(plugin):
    calls = []
    plugin.settings.settings_updated.connect(lambda: calls.append(True))
    plugin.settings.settings_updated.emit()
    assert calls == [True]


def test_options_page(qgis_parent):
    from geosearch_dk.config import OptionsFactory, Settings

    factory = OptionsFactory(Settings())
    assert not factory.icon().isNull()
    page = factory.createWidget(qgis_parent)
    assert isinstance(page, QWidget)
    page.apply()


def test_icon_resources_exist():
    for path in ("icon.png", "config/icon.png", "ui_search.ui", "config/settings.ui"):
        assert os.path.exists(os.path.join(PLUGIN_DIR, path)), path


def test_qgis_app_is_running(qgis_app):
    assert isinstance(qgis_app, QgsApplication)


def test_qgis_plugin_loader(iface, monkeypatch):
    """Load, start and unload through qgis.utils, as QGIS' plugin manager does."""
    import qgis.utils

    monkeypatch.setattr(qgis.utils, "iface", iface)
    assert qgis.utils.loadPlugin("geosearch_dk")
    try:
        assert qgis.utils.startPlugin("geosearch_dk")
        assert "geosearch_dk" in qgis.utils.active_plugins
        assert len(docks(iface)) == 1
    finally:
        assert qgis.utils.unloadPlugin("geosearch_dk")
    assert "geosearch_dk" not in qgis.utils.active_plugins
    assert docks(iface) == []
