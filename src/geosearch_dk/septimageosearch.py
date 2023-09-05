# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geosearch_dk
Description          : Search suggestions in QGIS using SDFI's Gsearch service
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

from builtins import object

from qgis.PyQt.QtCore import QFileInfo, QSettings, QTranslator, qVersion, Qt
from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

from .config import Settings, OptionsFactory

from .searchbox import SearchBox

class SeptimaGeoSearch(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/" + __package__

        # initialize locale. Default to Danish
        self.config = QSettings()
        localePath = ""
        try:
            locale = self.config.value("locale/userLocale")[0:2]
        except:
            locale = 'da'

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/" + locale + ".qt.qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QgsApplication.installTranslator(self.translator)
        
        # new config method
        self.settings = Settings()
        self.options_factory = OptionsFactory(self.settings)
        self.options_factory.setTitle('Geosearch DK')
        iface.registerOptionsWidgetFactory(self.options_factory)

    def initGui(self):
        # create the widget to display information
        self.searchwidget = SearchBox(self.iface, self.settings)
        # create the dockwidget with the correct parent and add the valuewidget
        self.searchdockwidget = QDockWidget(
            "Geosearch DK", self.iface.mainWindow()
        )
        self.searchdockwidget.setObjectName("Geosearch DK")
        self.searchdockwidget.setWidget(self.searchwidget)
        # add the dockwidget to iface
        self.iface.addDockWidget(
            Qt.TopDockWidgetArea, self.searchdockwidget
        )
        # Make changed settings apply immediately
        self.settings.settings_updated.connect(self.searchwidget.readconfig)

    def unload(self):
        self.searchwidget.unload() # try to avoid processing events, when QGIS is closing
        self.iface.removeDockWidget(self.searchdockwidget)
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
