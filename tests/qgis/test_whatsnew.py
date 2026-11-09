"""The "Hvad er nyt" dialog (whatsnew.py) and the banner and dot in the search panel (notice.py).

The dialog only opens when the user asks for it. Upgraders from 3.x get a
blue banner and a dot on ⓘ; everybody without a Bifrost key gets a yellow one.
"""

import time

import pytest
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt
from qgis.PyQt.QtWidgets import QApplication, QWidget

from conftest import MOCK_KEY, SETTINGS_GROUP

LONG_INFO = "Geosearch DK søger nu i Klimadatastyrelsens Bifrost"
SHORT_INFO = "Søgningen bruger nu Bifrost."


def wait_for(condition, timeout=5):
    end = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > end:
            raise TimeoutError("timed out")
        QCoreApplication.processEvents()
        time.sleep(0.01)


def process_events(seconds=0.2):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        QCoreApplication.processEvents()
        time.sleep(0.01)


def dialogs():
    return [
        w
        for w in QApplication.topLevelWidgets()
        if w.objectName() == "geosearchWhatsNew" and w.isVisible()
    ]


def seed(**values):
    s = QSettings()
    for name, value in values.items():
        s.setValue(SETTINGS_GROUP + "/" + name, value)
    s.sync()


def has_dot(box):
    return box.infoButton.icon().cacheKey() == box._infoIcons[True].cacheKey()


@pytest.fixture(autouse=True)
def no_env_key(monkeypatch):
    monkeypatch.delenv("BIFROST_KEY", raising=False)


@pytest.fixture
def whatsnew():
    from geosearch_dk import whatsnew

    yield whatsnew
    whatsnew.close_whats_new()
    process_events(0.05)


@pytest.fixture
def window(iface):
    window = iface.mainWindow()
    window.resize(1000, 600)
    window.show()
    yield window
    window.hide()


def start(iface):
    from geosearch_dk import classFactory

    plugin = classFactory(iface)
    plugin.initGui()
    return plugin


@pytest.fixture
def upgrader(iface, whatsnew):
    """A 3.x user (own token, saved types) with a Bifrost key entered."""
    seed(token="a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5", search_reg=False, bifrost_key=MOCK_KEY)
    plugin = start(iface)
    yield plugin
    plugin.unload()


def test_no_dialog_at_startup(iface, window, whatsnew):
    from geosearch_dk import notice

    seed(token="old", bifrost_key=MOCK_KEY)
    plugin = start(iface)
    try:
        process_events(1.0)
        assert dialogs() == []
        assert plugin.searchwidget.bannerState() == notice.INFO
        assert plugin.settings.value("notice_seen_version") == ""
    finally:
        plugin.unload()


def test_upgrader_gets_the_info_banner_and_the_dot(upgrader):
    from geosearch_dk import notice

    box = upgrader.searchwidget
    assert upgrader.settings.value("upgraded_from_3x") is True
    assert box.bannerState() == notice.INFO
    assert not box.bannerFrame.isHidden()
    assert not box.bannerCloseButton.isHidden()
    assert "Bifrost" in box.bannerLabel.text()
    assert has_dot(box)


def test_new_install_gets_no_banner_and_no_dot(iface, whatsnew):
    seed(bifrost_key=MOCK_KEY)
    plugin = start(iface)
    try:
        box = plugin.searchwidget
        assert plugin.settings.value("upgraded_from_3x") is False
        assert box.bannerState() is None
        assert box.bannerFrame.isHidden()
        assert not has_dot(box)
    finally:
        plugin.unload()
    # Saving settings later does not make a new user an upgrader
    seed(search_adr=True, kommunefilter="101")
    plugin = start(iface)
    try:
        assert plugin.searchwidget.bannerState() is None
    finally:
        plugin.unload()


def test_closing_the_banner_keeps_the_dot_until_the_dialog_is_opened(iface, whatsnew):
    seed(token="old", bifrost_key=MOCK_KEY)
    plugin = start(iface)
    try:
        box = plugin.searchwidget
        box.bannerCloseButton.click()
        assert box.bannerFrame.isHidden()
        assert has_dot(box)
        assert dialogs() == []
    finally:
        plugin.unload()

    # Still closed, and still a dot, at the next start
    plugin = start(iface)
    try:
        box = plugin.searchwidget
        assert box.bannerFrame.isHidden()
        assert has_dot(box)
        box.infoButton.click()
        wait_for(lambda: len(dialogs()) == 1)
        assert not has_dot(box)
    finally:
        plugin.unload()

    plugin = start(iface)
    try:
        assert plugin.searchwidget.bannerFrame.isHidden()
        assert not has_dot(plugin.searchwidget)
    finally:
        plugin.unload()


def test_a_new_notice_version_shows_the_banner_again(iface, whatsnew):
    seed(token="old", bifrost_key=MOCK_KEY, notice_seen_version="3.9.9", notice_closed_version="3.9.9")
    plugin = start(iface)
    try:
        assert not plugin.searchwidget.bannerFrame.isHidden()
        assert has_dot(plugin.searchwidget)
    finally:
        plugin.unload()


@pytest.mark.parametrize("route", ["link", "info_button", "kommunefilter"])
def test_opening_the_dialog_hides_banner_and_dot(upgrader, whatsnew, route):
    from geosearch_dk import notice

    box = upgrader.searchwidget
    if route == "link":
        box.bannerLabel.linkActivated.emit(notice.LINK_WHATS_NEW)
    elif route == "info_button":
        box.infoButton.click()
    else:  # e.g. from the settings page
        whatsnew.show_whats_new(anchor="kommunefilter")
    wait_for(lambda: len(dialogs()) == 1)
    assert box.bannerFrame.isHidden()
    assert not has_dot(box)
    assert upgrader.settings.value("notice_seen_version") == whatsnew.NOTICE_VERSION
    box.infoButton.click()  # a second click replaces it, it does not open another
    wait_for(lambda: len(dialogs()) == 1)


def test_key_banner_until_a_key_is_saved(iface, whatsnew):
    from geosearch_dk import notice

    seed(token="old")  # an upgrader, but the key banner wins
    plugin = start(iface)
    try:
        box = plugin.searchwidget
        assert box.bannerState() == notice.KEY
        assert not box.bannerFrame.isHidden()
        assert box.bannerCloseButton.isHidden()
        assert notice.LINK_ENTER_KEY in box.bannerLabel.text()
        assert notice.LINK_WHY_KEY in box.bannerLabel.text()
        assert notice.STYLES[notice.KEY]["background"] in box.bannerFrame.styleSheet()

        plugin.settings.set_value("bifrost_key", MOCK_KEY)
        plugin.settings.emit_updated()  # "Anvend"/OK in the settings
        assert box.bannerState() == notice.INFO
        assert notice.STYLES[notice.INFO]["background"] in box.bannerFrame.styleSheet()
        assert not box.bannerCloseButton.isHidden()

        plugin.settings.set_value("notice_closed_version", notice.NOTICE_VERSION)
        plugin.settings.emit_updated()
        assert box.bannerFrame.isHidden()
    finally:
        plugin.unload()


def test_key_from_the_environment_hides_the_key_banner(iface, whatsnew, monkeypatch):
    monkeypatch.setenv("BIFROST_KEY", "env-key")
    plugin = start(iface)
    try:
        assert plugin.searchwidget.bannerFrame.isHidden()
    finally:
        plugin.unload()


def test_missing_key_shows_no_message_bar(plugin, monkeypatch):
    box = plugin.searchwidget
    monkeypatch.setattr(
        box, "_pushSettingsMessage", lambda *a: pytest.fail("no message bar for a missing key")
    )
    box.handleMissingKey()
    assert not box.bannerFrame.isHidden()


def test_key_banner_links(plugin, whatsnew, monkeypatch):
    from geosearch_dk import notice

    box = plugin.searchwidget
    opened = []
    monkeypatch.setattr(
        box.qgisIface,
        "showOptionsDialog",
        lambda **kw: opened.append((kw.get("currentPage"), plugin.settings.focus_key_on_open)),
    )
    monkeypatch.setattr(whatsnew, "show_whats_new", lambda *a, **kw: opened.append(kw.get("anchor")))
    box.bannerLabel.linkActivated.emit(notice.LINK_ENTER_KEY)
    box.bannerLabel.linkActivated.emit(notice.LINK_WHY_KEY)
    box.settingsButton.click()
    assert opened == [("geosearchOptions", True), "noegle", ("geosearchOptions", False)]
    assert plugin.settings.focus_key_on_open is False


def test_settings_page_focuses_the_key_field(whatsnew):
    from geosearch_dk.config import Settings
    from geosearch_dk.config.settings_dialog import ConfigOptionsPage

    settings = Settings()
    settings.focus_key_on_open = True
    page = ConfigOptionsPage(None, settings)
    page.show()  # as the options dialog does when it opens at the page
    try:
        wait_for(lambda: page.config_widget.focusWidget() is page.config_widget.bifrost_key)
        assert settings.focus_key_on_open is False
    finally:
        page.hide()


def test_short_text_in_a_narrow_dock(iface, window, upgrader):
    box = upgrader.searchwidget
    dock = upgrader.searchdockwidget
    process_events()
    assert box.width() >= 300
    assert LONG_INFO in box.bannerLabel.text() and "<br>" not in box.bannerLabel.text()

    # pytest-qgis' window has no map canvas, so a side dock would get the
    # whole width; a floating dock is as narrow as a side dock.
    dock.setFloating(True)
    dock.resize(220, 200)
    wait_for(lambda: box.width() < 300)
    process_events()
    label = box.bannerLabel
    assert SHORT_INFO in label.text() and "<br>" in label.text()
    # The wrapped text is not cut off
    assert label.height() >= label.heightForWidth(label.width())
    narrow_height = label.minimumHeight()

    dock.resize(600, 200)
    wait_for(lambda: box.width() >= 300)
    process_events()
    assert LONG_INFO in box.bannerLabel.text()
    # The banner shrinks back to the wide text's height
    assert label.minimumHeight() == label.heightForWidth(label.width())
    assert label.minimumHeight() < narrow_height


def test_top_dock_fits_the_banner(iface, window, upgrader):
    # QGIS has a map canvas in the middle; pytest-qgis' window does not, so
    # its docks would fill the whole window.
    window.setCentralWidget(QWidget())
    try:
        dock = upgrader.searchdockwidget
        box = upgrader.searchwidget
        window.removeDockWidget(dock)
        window.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
        dock.show()
        process_events(0.5)
        label = box.bannerLabel
        with_banner = dock.height()
        # The label is as tall as its text, and the dock fits the panel
        assert label.height() == label.heightForWidth(label.width())
        assert dock.height() <= dock.sizeHint().height() + 2
        # A restored or moved dock is fitted to the banner
        window.resizeDocks([dock], [300], Qt.Orientation.Vertical)
        wait_for(lambda: dock.height() >= 290)
        dock.dockLocationChanged.emit(Qt.DockWidgetArea.TopDockWidgetArea)
        wait_for(lambda: dock.height() <= with_banner)

        box.bannerCloseButton.click()
        wait_for(lambda: dock.height() < with_banner)
        assert dock.height() <= dock.sizeHint().height() + 2
    finally:
        window.takeCentralWidget().deleteLater()


def test_anchor_and_links(whatsnew):
    dialog = whatsnew.show_whats_new(anchor="kommunefilter")
    browser = dialog.browser
    assert browser.openExternalLinks()
    assert "Bifrost" in browser.toPlainText()
    wait_for(lambda: browser.verticalScrollBar().value() > 0)
    top = whatsnew.show_whats_new()
    process_events()
    assert top.browser.verticalScrollBar().value() == 0
