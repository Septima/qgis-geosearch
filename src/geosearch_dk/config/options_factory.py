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
from qgis.gui import (QgsOptionsWidgetFactory)
from qgis.core import QgsApplication
from PyQt5.QtGui import QIcon
from .settings_dialog import ConfigOptionsPage

class OptionsFactory(QgsOptionsWidgetFactory):

    def __init__(self, settings):
        super(QgsOptionsWidgetFactory, self).__init__()
        self.settings = settings

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        return QIcon (icon_path)

    def createWidget(self, parent):
        return ConfigOptionsPage(parent, self.settings)
