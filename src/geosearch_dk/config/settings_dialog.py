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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QCheckBox, QFileDialog
from qgis.gui import QgsOptionsPageWidget
from qgis.PyQt.QtWidgets import QVBoxLayout
from qgis.PyQt.QtGui import QRegularExpressionValidator
from qgis.PyQt.QtCore import QRegularExpression, Qt, QTimer
from ..bifrost import settings_model as model
from ..bifrost.types import TYPES
from .qgissettingmanager import *
from .settings import BIFROST_KEY_HELP_URL, DEFAULT_BIFROST_URL
from .. import kommunefilter_info, whatsnew

MUNCODE_REGEX = "[0-9]{3}(,[0-9]{3})*"

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "settings.ui")
)


class ConfigOptionsPage(QgsOptionsPageWidget):

    def __init__(self, parent, settings):
        super(ConfigOptionsPage, self).__init__(parent)
        self.settings = settings
        self.config_widget = ConfigDialog(self.settings)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.config_widget)
        self.setObjectName("geosearchOptions")

    def showEvent(self, event):
        super().showEvent(event)
        # "Indtast nøgle" in the search panel's key banner
        if getattr(self.settings, "focus_key_on_open", False):
            self.settings.focus_key_on_open = False
            QTimer.singleShot(0, self.config_widget.focus_key)

    def apply(self):
        self.config_widget.accept_dialog()
        self.settings.emit_updated()


class ConfigDialog(WIDGET, BASE, SettingDialog):
    def __init__(self, settings):
        super(ConfigDialog, self).__init__(None)
        self.setupUi(self)
        # Before SettingDialog.__init__, which binds widgets by setting name
        self._add_type_checkboxes()
        self.bifrostKeyLinkLabel.setText(
            '<a href="{}">{}</a>'.format(
                BIFROST_KEY_HELP_URL, self.bifrostKeyLinkLabel.text()
            )
        )
        self.bifrost_url.setPlaceholderText(DEFAULT_BIFROST_URL)
        SettingDialog.__init__(self, settings)
        self.settings = settings
        regex = QRegularExpression(MUNCODE_REGEX)
        self.muncodeValidator = QRegularExpressionValidator(regex)
        self.kommunefilter.setValidator(self.muncodeValidator)
        self.kommunefilterInfoLabel.setText(kommunefilter_info.info_html())
        self.kommunefilter_enabled.toggled.connect(self._update_kommunefilter_enabled)
        self._update_kommunefilter_enabled()
        self.kommunefilterWhatsNewLabel.linkActivated.connect(
            self._show_kommunefilter_whatsnew
        )

    def focus_key(self):
        self.scrollArea.ensureWidgetVisible(self.bifrost_key)
        self.bifrost_key.setFocus(Qt.FocusReason.OtherFocusReason)

    def _show_kommunefilter_whatsnew(self, *args):
        # A widget in the (modal) options dialog as parent, so the notice is
        # not blocked behind it.
        whatsnew.show_whats_new(
            self, anchor=kommunefilter_info.WHATSNEW_ANCHOR, settings=self.settings
        )

    def _update_kommunefilter_enabled(self, *args):
        enabled = self.kommunefilter_enabled.isChecked()
        self.kommunefilter.setEnabled(enabled)
        self.kommunekoderLabel.setEnabled(enabled)

    def _add_type_checkboxes(self):
        """One checkbox per type in TYPES, named after its setting."""
        for search_type, row, column in model.checkbox_positions(TYPES):
            checkbox = QCheckBox(model.checkbox_label(search_type), self)
            checkbox.setObjectName(model.type_setting(search_type.key))
            self.gridLayout_3.addWidget(checkbox, row, column)
