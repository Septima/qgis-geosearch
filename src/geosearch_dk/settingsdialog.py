# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geosearch_dk
Description          : Search suggestions in QGIS using GST's geosearch service
Date                 : 24-05-2013
copyright            : (C) 2013 by Septima
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
from PyQt4.QtCore import QRegExp, Qt
from PyQt4.QtGui import QDialog, QRegExpValidator
from PyQt4 import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_settings.ui'))

MUNCODE_REGEX = '[0-9]{3}(,[0-9]{3})*'


class SettingsDialog (QDialog, FORM_CLASS):
    def __init__(self, qgisIface):
        QDialog.__init__(self, qgisIface.mainWindow())
        self.setupUi(self)

        regex = QRegExp(MUNCODE_REGEX, Qt.CaseInsensitive)
        self.muncodeValidator = QRegExpValidator(regex)
        self.kommunekoderLineEdit.setValidator(
            self.muncodeValidator
        )
