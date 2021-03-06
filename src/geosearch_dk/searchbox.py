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
from builtins import map
from builtins import str

from qgis.PyQt.QtWidgets import QFrame, QMessageBox, QPushButton
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt import uic
from qgis.core import QgsWkbTypes, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsApplication, Qgis
from qgis.gui import QgsVertexMarker, QgsRubberBand

import json
import os
import re

from . import qgisutils
from .autosuggest import AutoSuggest
from .config import Settings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_search.ui')
)


class SearchBox(QFrame, FORM_CLASS):

    def __init__(self, qgisIface):
        QFrame.__init__(self, qgisIface.mainWindow())
        self.setupUi(self)

        self.qgisIface = qgisIface
        self.markers = []
        self.readconfig() # old config

        self.setFrameStyle(QFrame.StyledPanel + QFrame.Raised)

        self.completion = AutoSuggest(
            geturl_func=self.geturl,
            parseresult_func=self.parseresponse,
            parent=self.searchEdit
        )
        self.setupCrsTransform()

        self.searchEdit.returnPressed.connect(self.doSearch)
        self.searchEdit.cleared.connect( self.clearMarkerGeom )
        if hasattr(self.searchEdit, 'setPlaceholderText'):
            self.searchEdit.setPlaceholderText(self.tr(u"Søg adresse, stednavn, postnummer, matrikel m.m."))

        # Listen to crs changes
        self.qgisIface.mapCanvas().destinationCrsChanged.connect(self.setupCrsTransform)
        # From 3 CRS transform is always enabled
        # self.qgisIface.mapCanvas().hasCrsTransformEnabledChanged.connect(self.setupCrsTransform)

        self.adjustSize()
        self.resize(50, self.height())
        self.searchEdit.setFocus()

    def readconfig(self):
        settings = Settings() # new config
        # Old way was storing settings in global scope. Leave advanced options there for now
        s = QSettings()
        k = __package__

        # prefix muncodes
        muncodes = re.findall(r'\d+', settings.value('kommunefilter'))
        areafilter = ','.join(['muncode0'+str(k) for k in muncodes])

        self.config = {
            'baseurl': settings.baseurl,
            'token' : settings.value('token'),
            'resources': settings.resources,
            'resourcesfilter': ",".join(settings.resourcesfilter()),
            'maxresults': s.value(k + "/maxresults", 25, type=int),
            'callback': str(s.value(k + "/callback", "callback", type=str)),
            'areafilter': areafilter,
            'rubber_color': str(s.value(k + "/rubber_color", "#FF0000", type=str)),
            'rubber_width': s.value(k + "/rubber_width", 4, type=int),
            'marker_color': str(s.value(k + "/marker_color", "#FF0000", type=str)),
            'marker_icon': s.value(k + "/marker_icon", QgsVertexMarker.ICON_CROSS, type=int),
            'marker_width': s.value(k + "/marker_width", 4, type=int),
            'marker_size': s.value(k + "/marker_size", 30, type=int)
        }

    def geturl(self, searchterm):
        self.clearMarkerGeom()
        # List with shortcuts
        req_resources = self.config['resourcesfilter']
        split = searchterm.split(':')
        if len(split)>1:
            first3letters_lowerCase = split[0][0:3].lower()
            if first3letters_lowerCase in self.config['resources']:
                req_resources = self.config['resources'][first3letters_lowerCase]['id']
                searchterm = split[1].lstrip()
        if not searchterm:
            return None

        url = self.config['baseurl'].format(
            resources=req_resources,
            limit=self.config['maxresults'],
            token = self.config['token'],
            area= self.config['areafilter'],
            callback=self.config['callback'],
        )

        url += searchterm
        return QUrl(url)

    def parseresponse(self, response):
        # Trim callback
        result = response[len(self.config['callback']) + 1: -1]
        try:
            obj = json.loads(result)
        except:
            QgsApplication.messageLog().logMessage(
                'Invalid JSON response from server: ' + result, __package__
            )
            # Check if we have an auth error
            if "User not authorized" in response:
                title = self.tr(u'Afvist af Kortforsyningen')
                message = self.tr(u'Manglende eller ukorrekt token til Kortforsyningen.')
                button_text = self.tr(u'Åbn settings')
                widget = self.qgisIface.messageBar().createMessage(title, message)
                button = QPushButton(widget)
                button.setText(button_text)
                button.pressed.connect(lambda : self.qgisIface.showOptionsDialog(currentPage='geosearchOptions'))
                widget.layout().addWidget(button)
                self.qgisIface.messageBar().pushWidget(widget, level=Qgis.Warning, duration=15)
            return None

        if 'status' not in obj:
            QgsApplication.messageLog().logMessage(
                'Unexpected result from server: ' + result, __package__
            )
            return None

        if not obj['status'] == 'OK':
            QgsApplication.messageLog().logMessage(
                'Server reported an error: ' + obj['message'], __package__
            )
            return None

        if "data" not in obj:
            return None
        data = obj['data']
        if not data:
            return [(self.tr("Ingen resultater"),None)]

        # Make tuple with ("text", object) for each result
        return [(e['presentationString'], e) for e in data]

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
        m = QgsRubberBand(self.qgisIface.mapCanvas(), False)  # not polygon
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

    def doSearch(self):
        self.completion.preventSuggest()

        o = self.completion.selectedObject
        #print o
        if not o:
            return

        # Create a QGIS geom to represent object
        geom = None
        if 'geometryWkt' in o:
            wkt = o['geometryWkt']
            # Fix invalid wkt
            if wkt.startswith('BOX'):
                wkt = 'LINESTRING' + wkt[3:]
                geom = QgsGeometry.fromRect(
                    QgsGeometry.fromWkt(wkt).boundingBox()
                )
            else:
                geom = QgsGeometry.fromWkt(wkt)
        elif 'xMin' in o:
            geom = QgsGeometry.fromRect(
                QgsRectangle(o['xMin'], o['yMin'], o['xMax'], o['yMax'])
            )
        else:
            geom = QgsGeometry.fromPointXY(QgsPointXY(o['x'], o['y']))

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

    def show_about_dialog(self):
        infoString = self.tr(
            u"Geosearch DK lader brugeren zoome til navngivne steder i Danmark.<br />"
            u"Pluginet benytter tjenesten 'geosearch' fra <a href=\"http://kortforsyningen.dk/\">kortforsyningen.dk</a>"
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
        self.completion.unload()
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
