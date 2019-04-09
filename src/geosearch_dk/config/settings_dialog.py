# -*- coding: utf-8 -*-
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

        





