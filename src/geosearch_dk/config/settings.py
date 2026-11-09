# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geosearch_dk
Description          : Search suggestions in QGIS using SDFI's Gsearch service
Date                 : 09-04-2019
copyright            : (C) 2019 by Septima
author               : asger@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QSettings

from .. import notice
from ..bifrost import settings_model as model
from ..bifrost.transport import DEFAULT_BASE_URL
from ..bifrost.types import TYPES
from .qgissettingmanager import *

# Bundled Bifrost key: used when neither the setting nor the BIFROST_KEY
# environment variable gives a key. Empty: Klimadatastyrelsen does not allow a
# shared key, so every user needs their own (#5).
DEFAULT_BIFROST_KEY = ""
# Used when the "Bifrost URL" setting is empty: production.
DEFAULT_BIFROST_URL = DEFAULT_BASE_URL
# How to get a key: Klimadatastyrelsen's page with the user guide. Pending #5.
BIFROST_KEY_HELP_URL = (
    "https://www.klimadatastyrelsen.dk/data/dataforsyningen/vi-fremtidssikrer-dataforsyningen"
)


class _QSettingsStore:
    """``contains``/``remove`` on QSettings, for ``settings_model.migrate``."""

    def __init__(self, qsettings, prefix=""):
        self.qsettings = qsettings
        self.prefix = prefix

    def contains(self, name):
        return self.qsettings.contains(self.prefix + name)

    def remove(self, name):
        self.qsettings.remove(self.prefix + name)


class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, "Geosearch DK")

        self.add_setting(String("kommunefilter", Scope.Global, ""))
        # The kommune filter is client-side and opt-in since Bifrost (#11).
        self.add_setting(Bool(model.KOMMUNEFILTER_ENABLED_SETTING, Scope.Global, False))
        # Set once the 3.x kommunefilter has been migrated (see _migratesettings).
        self.add_setting(Bool(model.KOMMUNEFILTER_MIGRATED_SETTING, Scope.Global, False))
        # Empty: DEFAULT_BIFROST_URL. The default is not stored, so a new
        # default (#5) reaches everyone who has not set a URL.
        self.add_setting(String(model.URL_SETTING, Scope.Global, ""))
        # Empty: the BIFROST_KEY environment variable, else DEFAULT_BIFROST_KEY.
        self.add_setting(String(model.KEY_SETTING, Scope.Global, ""))
        # The notice version (notice.NOTICE_VERSION) for which "Hvad er nyt"
        # was opened, and for which the banner in the search panel was closed.
        self.add_setting(String(notice.SEEN_SETTING, Scope.Global, ""))
        self.add_setting(String(notice.CLOSED_SETTING, Scope.Global, ""))
        # Whether this is an upgrade from 3.x, decided once (see _migratesettings).
        self.add_setting(Bool(model.UPGRADE_CHECKED_SETTING, Scope.Global, False))
        self.add_setting(Bool(model.UPGRADED_FROM_3X_SETTING, Scope.Global, False))
        # Set to put the cursor in the key field when the settings page opens.
        self.focus_key_on_open = False

        # The order of TYPES is the order results are displayed in
        for t in TYPES:
            self.add_setting(
                Bool(
                    model.type_setting(t.key),
                    Scope.Global,
                    model.type_default(t.key),
                )
            )

        self._migratesettings()

    def bifrost_url(self):
        return model.base_url(self.value(model.URL_SETTING))

    def bifrost_key(self, environ=None):
        return model.api_key(
            self.value(model.KEY_SETTING), DEFAULT_BIFROST_KEY, environ
        )

    def selected_type_keys(self):
        return model.selected_type_keys(self.value, TYPES)

    def emit_updated(self):
        self.settings_updated.emit()

    def _migratesettings(self):
        """Migrate settings from 3.x, see ``settings_model.migrate``."""
        # Where qgissettingmanager stores global settings, and where its
        # older versions did.
        stores = (
            _QSettingsStore(QSettings(), f"plugins/{self.plugin_name}/"),
            _QSettingsStore(QSettings(self.plugin_name, self.plugin_name)),
        )
        # Before migrate() deletes the token, which tells an upgrader.
        self.upgraded_from_3x = model.detect_3x_upgrade(
            lambda name: any(store.contains(name) for store in stores),
            self.value,
            self.set_value,
        )
        for store in stores:
            model.migrate(store)
        # True when this instance switched the kommune filter on for a 3.x
        # user; the plugin then tells the user once (SearchBox).
        self.kommunefilter_migrated_now = model.migrate_kommunefilter(
            self.value, self.set_value
        )
