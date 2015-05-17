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
RESOURCES = "Adresser,Stednavne,Postdistrikter,Matrikelnumre,Kommuner,Opstillingskredse,Politikredse,Regioner,Retskredse"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

from qgis.core import *
from qgis.gui import *

import microjson
import os

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
        self.marker = None
        self.readconfig()

        self.setFrameStyle(QFrame.StyledPanel + QFrame.Raised)

        self.completion = AutoSuggest(
            geturl_func=self.geturl,
            parseresult_func=self.parseresponse,
            parent=self.searchEdit
        )
        self.setupCrsTransform()

        self.searchEdit.returnPressed.connect(self.doSearch)
        # Listen to crs changes
        self.qgisIface.mapCanvas().mapRenderer().destinationSrsChanged.connect(self.setupCrsTransform)
        self.qgisIface.mapCanvas().mapRenderer().hasCrsTransformEnabled.connect(self.setupCrsTransform)

        self.adjustSize()
        self.resize(50, self.height())
        self.searchEdit.setFocus()

    def readconfig(self):
        s = QSettings()
        k = __package__
        self.config = {
            'username': str(s.value(k + "/username", "", type=str)),
            'password': str(s.value(k + "/password", "", type=str)),
            'resources': str(s.value(k + "/resources", RESOURCES, type=str)),
            'maxresults': s.value(k + "/maxresults", 25, type=int),
            'callback': str(s.value(k + "/callback", "callback", type=str)),
            'muncodes': s.value(k + "/muncodes", [])
        }

    def updateconfig(self):
        s = QSettings()
        k = __package__
        s.setValue(k + "/username",     self.config['username'])
        s.setValue(k + "/password",     self.config['password'])
        s.setValue(k + "/resources",    self.config['resources'])
        s.setValue(k + "/maxresults",   self.config['maxresults'])
        s.setValue(k + "/callback",     self.config['callback'])
        s.setValue(k + "/muncodes",     self.config['muncodes'])

    def geturl(self, searchterm):
        # TODO: prepare what can be prepared
        url = BASEURL.format(
            resources=self.config['resources'],
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
                QMessageBox.warning(
                    None,
                    'Bruger afvist af Kortforsyningen',
                    'Manglende eller ukorrekt brugernavn og password til Kortforsyningen.\n\n'
                    + 'Kortforsyningen svarede:\n'
                    + str(response)
                )
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

        data = obj['data']

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

        if geom.wkbType() == QGis.WKBPoint:
            m = QgsVertexMarker(self.qgisIface.mapCanvas())
            m.setCenter(geom.asPoint())
        elif geom.wkbType() == QGis.WKBLineString:
            m = QgsRubberBand(self.qgisIface.mapCanvas(), False)  # not polygon
            m.setToGeometry(geom, None)
        elif geom.wkbType() == QGis.WKBPolygon:
            m = QgsRubberBand(self.qgisIface.mapCanvas(), False)
            m.setToGeometry(
                QgsGeometry.fromPolyline(geom.asPolygon()[0]),
                None
            )

        m.setColor(QColor(255, 0, 0))
        self.marker = m

    def clearMarkerGeom(self):
        if self.marker is not None:
            self.qgisIface.mapCanvas().scene().removeItem(self.marker)
            self.marker = None

    def clear(self):
        self.clearMarkerGeom()
        self.ui.searchEdit.clear()

    def doSearch(self):
        self.completion.preventSuggest()

        o = self.completion.selectedObject
        # print o
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
        dlg = settingsdialog.SettingsDialog()
        dlg.loginLineEdit.setText(self.config['username'])
        dlg.passwordLineEdit.setText(self.config['password'])
        dlg.kommunekoderLineEdit.setText(
            ','.join(map(str, self.config['muncodes']))
        )
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        print "SettingsDialog result", result
        # See if OK was pressed
        if result == 1:
            # save settings
            self.config['username'] = str(dlg.loginLineEdit.text())
            self.config['password'] = str(dlg.passwordLineEdit.text())
            self.config['muncodes'] = [int(k) for k in dlg.kommunekoderLineEdit.text().split(',') if not k.strip() == '']
            self.updateconfig()

    def show_about_dialog(self):
        infoString = QCoreApplication.translate(
            'Geosearch DK',
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

if __name__ == "__main__":

    app = QApplication(sys.argv)

    suggest = SearchBox()
    suggest.show()

    sys.exit(app.exec_())
