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

# Import the PyQt and QGIS libraries
from builtins import object
from qgis.PyQt.QtCore import QFileInfo, QSettings, QTranslator, qVersion, Qt
from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
# Initialize Qt resources from file resources.py
# from . import resources_rc
# Import the code for the dialog

from .searchbox import SearchBox


class SeptimaGeoSearch(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/" + __package__

        # config
        self.config = QSettings()

        # initialize locale. Default to Danish
        localePath = ""
        try:
            locale = self.config.value("locale/userLocale")[0:2]
        except:
            locale = 'da'

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QgsApplication.installTranslator(self.translator)

    def initGui(self):
        # create the widget to display information
        self.searchwidget = SearchBox(self.iface)
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

        # Menu items
        self.configAction = QAction(
            QIcon(),
            QgsApplication.translate('Geosearch DK', "&Indstillinger"),
            self.iface.mainWindow()
        )
        self.aboutAction = QAction(
            QIcon(),
            QgsApplication.translate('Geosearch DK', "&Om pluginet"),
            self.iface.mainWindow()
        )

        self.configAction.triggered.connect(
            self.searchwidget.show_settings_dialog
        )
        self.aboutAction.triggered.connect(self.searchwidget.show_about_dialog)

        self.iface.addPluginToMenu("Geosearch DK", self.configAction)
        self.iface.addPluginToMenu("Geosearch DK", self.aboutAction)

    def unload(self):
        self.searchwidget.unload() # try to avoid processing events, when QGIS is closing
        self.iface.removePluginMenu("Geosearch DK", self.configAction)
        self.iface.removePluginMenu("Geosearch DK", self.aboutAction)
        self.iface.removeDockWidget(self.searchdockwidget)
