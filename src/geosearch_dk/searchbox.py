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
BASEURL = "http://kortforsyningen.kms.dk/Geosearch?service=GEO&resources={resources}&area={area}&limit={limit}&login={login}&password={password}&callback={callback}&search="
RESOURCES = "Adresser,Stednavne_v2,Postdistrikter,Matrikelnumre,Kommuner,Opstillingskredse,Politikredse,Regioner,Retskredse"

RESOURCESdic = {
                'adr': {'id':'Adresser', 'title':'Adresser', 'checkbox': 'adrCheckbox'},
                'ste': {'id':'Stednavne_v2', 'titel':'Stednavne', 'checkbox': 'steCheckbox'},
                'pos': {'id':'Postdistrikter', 'titel':'Postdistrikter', 'checkbox':'posCheckbox'},
                'mat': {'id':'Matrikelnumre', 'titel':'Matrikelnumre', 'checkbox': 'matCheckbox'},
                'kom': {'id':'Kommuner', 'titel':'Kommuner', 'checkbox': 'komCheckbox'},
                'ops': {'id':'Opstillingskredse', 'titel':'Opstillingskredse', 'checkbox': 'opsCheckbox'},
                'pol': {'id':'Politikredse', 'titel':'Politikredse', 'checkbox':'polCheckbox' },
                'reg': {'id':'Regioner', 'titel':'Regioner', 'checkbox':'regCheckbox'}
                }

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

from qgis.core import *
from qgis.gui import *

import microjson
import os
import re

import qgisutils
from autosuggest import AutoSuggest
# from ui_search import Ui_searchForm
import settingsdialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_search.ui')
)


class SearchBox(QFrame, FORM_CLASS):

    def __init__(self, qgisIface):
        QFrame.__init__(self, qgisIface.mainWindow())
        self.setupUi(self)

        self.qgisIface = qgisIface
        self.markers = []
        self.readconfig()

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
            self.searchEdit.setPlaceholderText(self.trUtf8(u"Søg adresse, stednavn, postnummer, matrikel m.m."))

        # Listen to crs changes
        self.qgisIface.mapCanvas().destinationCrsChanged.connect(self.setupCrsTransform)
        self.qgisIface.mapCanvas().hasCrsTransformEnabledChanged.connect(self.setupCrsTransform)

        self.adjustSize()
        self.resize(50, self.height())
        self.searchEdit.setFocus()

    def readconfig(self):
        s = QSettings()
        k = __package__

        # Handle old muncodes storage, where it was stored as a list
        muncodes = s.value(k + "/muncodes", "")
        if not isinstance(muncodes, basestring):
            muncodes = ""
        muncodes = re.findall(r'\d+', muncodes)

        self.config = {
            'username': str(s.value(k + "/username", "", type=str)),
            'password': str(s.value(k + "/password", "", type=str)),
            'resources': RESOURCES, #str(s.value(k + "/resources", RESOURCES, type=str)),
            'maxresults': s.value(k + "/maxresults", 25, type=int),
            'callback': str(s.value(k + "/callback", "callback", type=str)),
            'muncodes': muncodes,
            'rubber_color': str(s.value(k + "/rubber_color", "#FF0000", type=str)),
            'rubber_width': s.value(k + "/rubber_width", 30, type=int),
            'marker_color': str(s.value(k + "/marker_color", "#FF00FF", type=str)),
            'marker_icon': s.value(k + "/marker_icon", QgsVertexMarker.ICON_CROSS, type=int),
            'marker_width': s.value(k + "/marker_width", 33, type=int),
            'marker_size': s.value(k + "/marker_size", 30, type=int)
        }

    def updateconfig(self):
        s = QSettings()
        k = __package__
        s.setValue(k + "/username",     self.config['username'])
        s.setValue(k + "/password",     self.config['password'])
        s.setValue(k + "/resources",    self.config['resources'])
        s.setValue(k + "/maxresults",   self.config['maxresults'])
        s.setValue(k + "/callback",     self.config['callback'])
        s.setValue(k + "/muncodes",     ",".join(self.config['muncodes'])) # Store as string because of issue #24
        s.setValue(k + "/rubber_color",     self.config['rubber_color'])
        s.setValue(k + "/rubber_width",     self.config['rubber_width'])
        s.setValue(k + "/marker_color",     self.config['marker_color'])
        s.setValue(k + "/marker_icon",     self.config['marker_icon'])
        s.setValue(k + "/marker_width",     self.config['marker_width'])
        s.setValue(k + "/marker_size",     self.config['marker_size'])
        # This will write the settings to the platform specific storage. According to http://pyqt.sourceforge.net/Docs/PyQt4/pyqt_qsettings.html
        del s

    def geturl(self, searchterm):
        self.clearMarkerGeom()
        # List with shortcuts
        req_resources = self.config['resources']
        split = searchterm.split(':')
        if len(split)>1:
            first3letters_lowerCase = split[0][0:3].lower()
            if first3letters_lowerCase in RESOURCESdic.keys():
                req_resources = RESOURCESdic[first3letters_lowerCase]['id']
                searchterm = split[1].lstrip()
        if not searchterm:
            return None

        # TODO: prepare what can be prepared

        url = BASEURL.format(
            resources=req_resources,
            limit=self.config['maxresults'],
            login=self.config['username'],
            password=self.config['password'],
            callback=self.config['callback'],
            area=','.join(['muncode0'+str(k) for k in self.config['muncodes']])
        )

        url += searchterm
        return QUrl(url)

    def parseresponse(self, response):
        # Trim callback
        result = str(response)[len(self.config['callback']) + 1: -1]
        # print result
        try:
            obj = microjson.from_json(result)
        except microjson.JSONError:
            QgsMessageLog.logMessage(
                'Invalid JSON response from server: ' + result, __package__
            )
            # Check if we have an auth error
            if 'User not found' in response or \
                    'User not authenticated' in response:
                title = self.trUtf8(u'Bruger afvist af Kortforsyningen')
                msg = self.trUtf8(u'Manglende eller ukorrekt brugernavn og password til Kortforsyningen.\n\nKortforsyningen svarede:\n')
                QMessageBox.warning( None, title, msg + str(response))
                # Now show settings dialog
                self.show_settings_dialog()
            return None

        if 'status' not in obj:
            QgsMessageLog.logMessage(
                'Unexpected result from server: ' + result, __package__
            )
            return None

        if not obj['status'] == 'OK':
            QgsMessageLog.logMessage(
                'Server reported an error: ' + obj['message'], __package__
            )
            return None

        if not obj.has_key("data"):
            return None
        data = obj['data']
        if not data:
            return [(self.trUtf8("Ingen resultater"),None)]

        # Make tuple with ("text", object) for each result
        return [(e['presentationString'], e) for e in data]

    def setupCrsTransform(self):
        if QgsCoordinateReferenceSystem is not None:
            srcCrs = QgsCoordinateReferenceSystem(
                25832, QgsCoordinateReferenceSystem.EpsgCrsId
            )
            dstCrs = qgisutils.getCurrentCrs(self.qgisIface)
            self.crsTransform = QgsCoordinateTransform(srcCrs, dstCrs)

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
            if geom.wkbType() == QGis.WKBPoint:
                m = self._setPointMarker(geom)
            elif geom.wkbType() in (QGis.WKBLineString, QGis.WKBPolygon):
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
        if geom.wkbType() == QGis.WKBLineString:
            linegeom = geom
        elif geom.wkbType() == QGis.WKBPolygon:
            linegeom = QgsGeometry.fromPolyline(geom.asPolygon()[0])
        m.setToGeometry(linegeom, None)
        m.setBorderColor(QColor(self.config['rubber_color']))
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
            geom = QgsGeometry.fromPoint(QgsPoint(o['x'], o['y']))

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

    def show_settings_dialog(self):
        # create and show the dialog
        dlg = settingsdialog.SettingsDialog(self.qgisIface)
        dlg.loginLineEdit.setText(self.config['username'])
        dlg.passwordLineEdit.setText(self.config['password'])
        dlg.kommunekoderLineEdit.setText(','.join(map(str, self.config['muncodes'])))
        for dic in RESOURCESdic.values():
            cb = getattr(dlg,dic['checkbox'])
            if dic['id'] in self.config['resources']:
                cb.setCheckState(2)
            else:
                cb.setCheckState(0)
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # save settings
            self.config['username'] = str(dlg.loginLineEdit.text())
            self.config['password'] = str(dlg.passwordLineEdit.text())
            self.config['muncodes'] = [k for k in dlg.kommunekoderLineEdit.text().split(',') if not k.strip() == '']
            resources_list = []
            for dic in sorted(RESOURCESdic.values()):
                cb = getattr(dlg,dic['checkbox'])
                if cb.isChecked():
                    resources_list.append(dic['id'])
            self.config['resources'] = ', '.join(resources_list)
            # Write config
            self.updateconfig()

    def show_about_dialog(self):
        infoString = self.trUtf8(
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
        if geom.type() == QGis.Point:
            if geom.isMultipart():
                multiGeom = geom.asMultiPoint()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPoint(i))
            else:
                geometries.append(geom)
        elif geom.type() == QGis.Line:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolyline()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolyline(i))
            else:
                geometries.append(geom)
        elif geom.type() == QGis.Polygon:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolygon()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolygon(i))
            else:
                geometries.append(geom)
        return geometries

if __name__ == "__main__":

    app = QApplication(sys.argv)

    suggest = SearchBox()
    suggest.show()

    sys.exit(app.exec_())
