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
import json
import os
import re

from osgeo import ogr

from qgis.PyQt.QtWidgets import QFrame, QMessageBox, QPushButton
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtCore import QSettings, QSize
from qgis.PyQt import uic
from qgis.core import QgsApplication, QgsWkbTypes, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, Qgis
from qgis.gui import QgsVertexMarker, QgsRubberBand

from . import qgisutils
from .suggester import Suggester
from .config import Settings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_search.ui')
)

class SearchBox(QFrame, FORM_CLASS):

    def __init__(self, qgisIface, settings):
        QFrame.__init__(self, qgisIface.mainWindow())
        self.setupUi(self)

        self.qgisIface = qgisIface
        self.markers = []
        self.readconfig() # old config

        self.setFrameStyle(QFrame.StyledPanel + QFrame.Raised)

        self.suggester = Suggester(
            settings = settings,
            searchbox_widget=self.searchEdit,
            notauthorized_func = self.handleNotAuthorized
        )
        self.setupCrsTransform()

        self.searchEdit.returnPressed.connect(self.showSelected)
        self.searchEdit.cleared.connect( self.clearMarkerGeom )
        if hasattr(self.searchEdit, 'setPlaceholderText'):
            self.searchEdit.setPlaceholderText(self.tr(u"Søg adresse, stednavn, postnummer, matrikel m.m."))

        # Listen to crs changes
        self.qgisIface.mapCanvas().destinationCrsChanged.connect(self.setupCrsTransform)

        self.adjustSize()
        self.resize(50, self.height())
        self.searchEdit.setFocus()

        self.settingsButton = self.settingsButton
        settings_icon = QIcon(":images/themes/default/console/iconSettingsConsole.svg")
        self.settingsButton.setIcon(settings_icon)
        self.settingsButton.setIconSize(QSize(16, 16))
        #self.settingsButton.setStyleSheet('border: none;')
        self.settingsButton.setFixedSize( 20, 20 )

        self.settingsButton.clicked.connect(self.show_settings)

    def show_settings(self):
        self.qgisIface.showOptionsDialog(currentPage="geosearchOptions")

    def readconfig(self):
        settings = Settings() # new config
        # Old way was storing settings in global scope. Leave advanced options there for now
        s = QSettings()
        k = __package__

        # prefix muncodes
        #muncodes = re.findall(r'\d+', settings.value('kommunefilter'))
        #areafilter = ','.join(['muncode0'+str(k) for k in muncodes])

        self.config = {
            #'token' : settings.value('token'),
            #'resources': settings.resources,
            #'resourcesfilter': ",".join(settings.selected_resources()),
            'maxresults': s.value(k + "/maxresults", 25, type=int),
            #'callback': str(s.value(k + "/callback", "callback", type=str)),
            #'areafilter': areafilter,
            'rubber_color': str(s.value(k + "/rubber_color", "#FF0000", type=str)),
            'rubber_width': s.value(k + "/rubber_width", 4, type=int),
            'marker_color': str(s.value(k + "/marker_color", "#FF0000", type=str)),
            'marker_icon': s.value(k + "/marker_icon", QgsVertexMarker.ICON_CROSS, type=int),
            'marker_width': s.value(k + "/marker_width", 4, type=int),
            'marker_size': s.value(k + "/marker_size", 30, type=int)
        }

    def handleNotAuthorized(self):
        title = self.tr(u'Afvist af Kortforsyningen')
        message = self.tr(u'Manglende eller ukorrekt token til Kortforsyningen.')
        button_text = self.tr(u'Åbn settings')
        widget = self.qgisIface.messageBar().createMessage(title, message)
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(lambda : self.qgisIface.showOptionsDialog(currentPage='geosearchOptions'))
        widget.layout().addWidget(button)
        self.qgisIface.messageBar().pushWidget(widget, level=Qgis.Warning, duration=15)

    def setupCrsTransform(self):
        if QgsCoordinateReferenceSystem is not None:
            srcCrs = QgsCoordinateReferenceSystem.fromEpsgId(25832)
            dstCrs = qgisutils.getCurrentCrs(self.qgisIface)
            self.crsTransform = QgsCoordinateTransform(srcCrs, dstCrs, QgsProject.instance())

    def setMarkerGeom(self, geom):
        # Show geometry
        self.clearMarkerGeom()
        self._setMarkerGeom(geom)

    def _setMarkerGeom(self, geom):
        if geom.isMultipart():
            geometries = self._extractAsSingle(geom)
            for g in geometries:
                self._setMarkerGeom(g)
        else:
            if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.PointGeometry:
                m = self._setPointMarker(geom)
            elif QgsWkbTypes.geometryType(geom.wkbType()) in (QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry):
                m = self._setRubberBandMarker(geom)
            self.markers.append( m )

    def _setPointMarker(self, pointgeom):
        m = QgsVertexMarker(self.qgisIface.mapCanvas())
        m.setColor(QColor(self.config['marker_color']))
        m.setIconType(self.config['marker_icon'])
        m.setPenWidth(self.config['marker_width'])
        m.setIconSize(self.config['marker_size'])
        m.setCenter(pointgeom.asPoint())
        return m

    def _setRubberBandMarker(self, geom):
        m = QgsRubberBand(self.qgisIface.mapCanvas())  # not polygon
        if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.LineGeometry:
            linegeom = geom
        elif QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.PolygonGeometry:
            linegeom = QgsGeometry.fromPolylineXY(geom.asPolygon()[0])
        m.setToGeometry(linegeom, None)
        m.setColor(QColor(self.config['rubber_color']))
        m.setWidth(self.config['rubber_width'])
        return m

    def clearMarkerGeom(self):
        if self.markers:
            for m in self.markers:
                self.qgisIface.mapCanvas().scene().removeItem(m)
        self.markers = []

    def clear(self):
        self.clearMarkerGeom()
        self.ui.searchEdit.clear()

    def showSelected(self):
        try:
            self.suggester.preventSuggest()

            row = self.suggester.selectedObject[0]
            #print o
            if not row:
                return
            if row["status"] == "error":
                QMessageBox.information(
                    self.qgisIface.mainWindow(), "Geosearch DK - Fejl", row["response"]
                )
                return

            # Create a QGIS geom to represent object
            geom = None
            if 'geometri' in row:
                geometri = row['geometri']
                #Convert to qGisGeom
                geo_json = json.dumps(geometri)
                ogr_geom = ogr.CreateGeometryFromJson(geo_json)
                wkt = ogr_geom.ExportToWkt()
                geom = QgsGeometry.fromWkt(wkt)

                if geom:
                    # Zoom to feature
                    bufgeom = geom.buffer(200.0, 2)
                    bufgeom.transform(self.crsTransform)
                    rect = bufgeom.boundingBox()
                    mc = self.qgisIface.mapCanvas()
                    mc.setExtent(rect)

                    # Mark the spot
                    geom.transform(self.crsTransform)
                    self.setMarkerGeom(geom)

                    mc.refresh()
        except Exception as e:
            pass

    def show_about_dialog(self):
        infoString = self.tr(
            u"Geosearch DK lader brugeren zoome til navngivne steder i Danmark.<br />"
            u"Pluginet benytter tjenesten 'gsearch' fra <a href=\"http://kortforsyningen.dk/\">kortforsyningen.dk</a>"
            u" og kræver derfor et gyldigt login til denne tjeneste.<br />"
            u"Pluginets webside: <a href=\"http://github.com/Septima/qgis-geosearch\">github.com/Septima/qgis-geosearch</a><br />"
            u"Udviklet af: Septima<br />"
            u"Mail: <a href=\"mailto:kontakt@septima.dk\">kontakt@septima.dk</a><br />"
            u"Web: <a href=\"http://www.septima.dk\">www.septima.dk</a>\n"
        )
        QMessageBox.information(
            self.qgisIface.mainWindow(), "Om Geosearch DK", infoString
        )

    def unload(self):
        self.suggester.unload()
        self.clearMarkerGeom()


    def _extractAsSingle(self, geom):
        multiGeom = QgsGeometry()
        geometries = []
        if geom.type() == QgsWkbTypes.PointGeometry:
            if geom.isMultipart():
                multiGeom = geom.asMultiPoint()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPointXY(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolyline()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolylineXY(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.PolygonGeometry:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolygon()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolygonXY(i))
            else:
                geometries.append(geom)
        return geometries

if __name__ == "__main__":

    app = QApplication(sys.argv)

    suggest = SearchBox()
    suggest.show()

    sys.exit(app.exec_())
