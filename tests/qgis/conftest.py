"""QGIS integration tests (pytest-qgis), run in Docker against QGIS 3 and 4.

    make test-qgis            # QGIS 4 (default)
    make test-qgis QGIS=3     # QGIS 3.44 LTR

Fixtures for plugin tests:

``plugin``
    The loaded plugin (``classFactory`` + ``initGui``), unloaded afterwards.
    Its dock is really added to pytest-qgis' main window.
``bifrost_mock``
    A mock Bifrost (tests/mock_bifrost.py) on a free port, with the plugin's
    ``bifrost_url``/``bifrost_key`` settings pointing at it. Use
    ``bifrost_mock.configure(error="503")`` to inject errors and
    ``bifrost_mock.request_log()`` to see what the plugin sent. Request it
    before ``plugin`` so the plugin reads the settings on load.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for path in (os.path.join(ROOT, "src"), os.path.join(ROOT, "tests"), os.path.join(ROOT, "tests", "tools")):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    import qgis.core  # noqa: F401
except ImportError:  # e.g. `uv run pytest tests`: QGIS is only in the Docker image
    collect_ignore_glob = ["test_*.py"]
else:
    import pytest
    from qgis.PyQt.QtCore import QSettings
    from qgis.PyQt.QtWidgets import QDockWidget

    import mock_bifrost

    SETTINGS_GROUP = "plugins/Geosearch DK"
    MOCK_KEY = "mock-key"

    def pytest_collection_modifyitems(items):
        for item in items:
            item.add_marker(pytest.mark.qgis)

    @pytest.fixture(autouse=True)
    def clean_settings():
        """Each test starts with the plugin's default settings."""
        s = QSettings()
        s.remove(SETTINGS_GROUP)
        s.remove("geosearch_dk")
        yield
        s.remove(SETTINGS_GROUP)
        s.remove("geosearch_dk")

    @pytest.fixture(scope="session")
    def mock_server():
        server = mock_bifrost.serve_in_thread(delay=1)
        yield server
        server.shutdown()

    @pytest.fixture
    def bifrost_mock(mock_server, clean_settings):
        mock_server.reset()
        mock_server.configure(delay=1)
        s = QSettings()
        s.setValue(SETTINGS_GROUP + "/bifrost_url", mock_server.url)
        s.setValue(SETTINGS_GROUP + "/bifrost_key", MOCK_KEY)
        return mock_server

    @pytest.fixture
    def iface(qgis_iface, monkeypatch):
        """pytest-qgis' iface, but docks really go into its main window."""
        window = qgis_iface.mainWindow()
        monkeypatch.setattr(qgis_iface, "addDockWidget", window.addDockWidget, raising=False)
        monkeypatch.setattr(qgis_iface, "removeDockWidget", window.removeDockWidget, raising=False)
        for name in ("registerOptionsWidgetFactory", "unregisterOptionsWidgetFactory"):
            getattr(qgis_iface, name).reset_mock()
        return qgis_iface

    def docks(iface, name="Geosearch DK"):
        window = iface.mainWindow()
        return [
            d
            for d in window.findChildren(QDockWidget)
            if d.objectName() == name and window.dockWidgetArea(d) != 0 and not d.isHidden()
        ]

    @pytest.fixture
    def plugin(iface):
        from geosearch_dk import classFactory

        p = classFactory(iface)
        p.initGui()
        yield p
        if getattr(p, "searchdockwidget", None) is not None and docks(iface):
            p.unload()
