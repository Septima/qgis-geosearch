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
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QFileDialog
from qgis.gui import (QgsOptionsPageWidget)
from qgis.PyQt.QtWidgets import  QVBoxLayout
from qgis.PyQt.QtGui import QRegExpValidator
from qgis.PyQt.QtCore import QRegExp, Qt
from .qgissettingmanager import *

MUNCODE_REGEX = '[0-9]{3}(,[0-9]{3})*'

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'settings.ui')
)

class ConfigOptionsPage(QgsOptionsPageWidget):

    def __init__(self, parent, settings):
        super(ConfigOptionsPage, self).__init__(parent)
        self.settings = settings
        self.config_widget = ConfigDialog(self.settings)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(0)
        self.setLayout(layout)
        layout.addWidget(self.config_widget)
        self.setObjectName('geosearchOptions')

    def apply(self):
        self.config_widget.accept_dialog()
        self.settings.emit_updated()

class ConfigDialog(WIDGET, BASE, SettingDialog):
    def __init__(self, settings):
        super(ConfigDialog, self).__init__(None)
        self.setupUi(self)
        SettingDialog.__init__(self, settings)
        self.settings = settings
        regex = QRegExp(MUNCODE_REGEX, Qt.CaseInsensitive)
        self.muncodeValidator = QRegExpValidator(regex)
        self.kommunefilter.setValidator(
            self.muncodeValidator
        )

        





