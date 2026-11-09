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
import os

from qgis.PyQt.QtCore import QCoreApplication, QTranslator, Qt
from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

from .config import Settings, OptionsFactory

from .searchbox import SearchBox
from . import whatsnew
from .bifrost import translation
from .language import translation_file, ui_language


class SeptimaGeoSearch(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # English in an English QGIS, otherwise the Danish source texts.
        self.translator = None
        path = translation_file(ui_language())
        if path and os.path.exists(path):
            self.translator = QTranslator()
            if self.translator.load(path):
                QgsApplication.installTranslator(self.translator)
            else:
                self.translator = None
        translation.set_translate(QCoreApplication.translate)

        # new config method
        self.settings = Settings()
        self.options_factory = OptionsFactory(self.settings)
        self.options_factory.setTitle("Geosearch DK")
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
            Qt.DockWidgetArea.TopDockWidgetArea, self.searchdockwidget
        )
        # QGIS restores the saved dock size after initGui; fit it to the banner
        self.searchdockwidget.dockLocationChanged.connect(self.searchwidget.fitDock)
        self.iface.initializationCompleted.connect(self.searchwidget.fitDock)
        # Make changed settings apply immediately
        self.settings.settings_updated.connect(self.searchwidget.readconfig)
        if self.settings.kommunefilter_migrated_now:
            self.settings.kommunefilter_migrated_now = False
            self.searchwidget.showKommunefilterMigrationNotice()

    def unload(self):
        whatsnew.close_whats_new()
        try:
            self.iface.initializationCompleted.disconnect(self.searchwidget.fitDock)
        except TypeError:
            pass
        self.searchwidget.unload()  # try to avoid processing events, when QGIS is closing
        self.iface.removeDockWidget(self.searchdockwidget)
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        translation.set_translate(None)
        if self.translator is not None:
            QgsApplication.removeTranslator(self.translator)
            self.translator = None
