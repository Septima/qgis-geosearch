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
BASEURL = "http://kortforsyningen.kms.dk/Geosearch?service=GEO&search=%1&resources={resources}&limit={limit}&login={login}&password={password}&callback={callback}"
RESOURCES = "Adresser,Stednavne,Postdistrikter,Matrikelnumre,Kommuner,Opstillingskredse,Politikredse,Regioner,Retskredse"

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from qgis.core import *
from qgis.gui import *

import microjson

import qgisutils
from autosuggest import AutoSuggest
from ui_search import Ui_searchForm
import settingsdialog


class SearchBox(QFrame):

    def __init__(self, qgisIface):
        QFrame.__init__(self, qgisIface.mainWindow())

        self.qgisIface = qgisIface
        self.marker = None
        self.readconfig()

        self.ui = Ui_searchForm()
        self.ui.setupUi(self)
        self.setFrameStyle(QFrame.StyledPanel + QFrame.Raised)

        self.completion = AutoSuggest(geturl_func = self.geturl, parseresult_func = self.parseresponse, parent = self.ui.searchEdit)
        self.setupCrsTransform()

        self.connect(self.ui.searchEdit, SIGNAL("returnPressed()"), self.doSearch)
        self.connect(self.ui.searchButton, SIGNAL("clicked()"), self.doSearch)
        self.connect(self.ui.clearButton, SIGNAL("clicked()"), self.clear)
        # Listen to crs changes
        self.connect( self.qgisIface.mapCanvas().mapRenderer(), SIGNAL("destinationSrsChanged()"), self.setupCrsTransform )
        self.connect( self.qgisIface.mapCanvas().mapRenderer(), SIGNAL("hasCrsTransformEnabled(bool)"), self.setupCrsTransform )
        #self.qgisIface.mapCanvas().mapRenderer().setProjectionsEnabled(True)

        self.adjustSize()
        self.resize(50, self.height())
        self.ui.searchEdit.setFocus()
    
    def readconfig(self):
        s = QSettings()
        k = __package__
        self.config = {
                'username': str(s.value( k + "/username", "").toString()),
                'password': str(s.value( k + "/password", "").toString()),
                'resources': str(s.value( k + "/resources", RESOURCES).toString()) ,
                'maxresults': s.value( k + "/maxresults", 25).toInt()[0],
                'callback': str(s.value( k + "/callback", "callback").toString()),
            }
    
    def updateconfig( self ):
        s = QSettings()
        k = __package__
        s.setValue(k + "/username",  self.config['username'])
        s.setValue(k + "/password",  self.config['password'])
        s.setValue(k + "/resources",  self.config['resources'])
        s.setValue(k + "/maxresults",  self.config['maxresults'])
        s.setValue(k + "/callback",  self.config['callback'])

    def geturl(self, searchterm):
        url = QString( BASEURL.format( 
                              resources = self.config['resources'], 
                              limit = self.config['maxresults'], 
                              login = self.config['username'], 
                              password = self.config['password'], 
                              callback = self.config['callback']))
        return QUrl( url.arg( searchterm ) )
            

    def parseresponse(self, response):
        # Trim callback
        result = str( response )[ len(self.config['callback']) + 1 : -1]
        #print result
        try:
            obj = microjson.from_json( result )
        except microjson.JSONError:
            QgsMessageLog.logMessage('Invalid JSON response from server: ' + result, __package__)
            # Check if we have an auth error
            if 'User not found' in response or 'User not authenticated' in response:
                QMessageBox.warning(None, 'Bruger afvist af Kortforsyningen', 
                                    'Manglende eller ukorrekt brugernavn og password til Kortforsyningen.\n\n'
                                    + 'Kortforsyningen svarede:\n'
                                    + str(response) )
                self.show_settings_dialog()
            return None
        
        if not obj.has_key('status'):
            QgsMessageLog.logMessage('Unexpected result from server: ' + result, __package__)
            return None
        
        if not obj['status'] == 'OK':
            QgsMessageLog.logMessage('Server reported an error: ' + obj['message'], __package__)
            return None
        
        data = obj['data']

        # Make tuple with ("text", object) for each result        
        return [(e['presentationString'], e) for e in data ]

    def setupCrsTransform(self):
        if not QgsCoordinateReferenceSystem is None:
            srcCrs = QgsCoordinateReferenceSystem( 25832, QgsCoordinateReferenceSystem.EpsgCrsId )
            dstCrs = qgisutils.getCurrentCrs( self.qgisIface )
            #print "CRS: ", dstCrs.toWkt()
            self.crsTransform = QgsCoordinateTransform( srcCrs, dstCrs )

    def setMarkerGeom( self, geom ):
        # Show geometry
        self.clearMarkerGeom()

        if geom.wkbType() == QGis.WKBPoint:
            m = QgsVertexMarker( self.qgisIface.mapCanvas() )
            m.setCenter( geom.asPoint() )
##        else:
##            m = QgsRubberBand(self.qgisIface.mapCanvas(), QGis.Line)
##            m.setToGeometry( geom , None)
##            m.setColor(QColor(255,0,0))
        elif geom.wkbType() == QGis.WKBLineString:
            m = QgsRubberBand(self.qgisIface.mapCanvas(), False)  # False = not a polygon
            m.setToGeometry( geom , None)
        elif geom.wkbType() == QGis.WKBPolygon:
            m = QgsRubberBand(self.qgisIface.mapCanvas(), False)
            m.setToGeometry( QgsGeometry.fromPolyline(geom.asPolygon()[0] ) , None)

        m.setColor(QColor(255,0,0))
        self.marker = m

    def clearMarkerGeom( self ):
        if not self.marker is None:
            self.qgisIface.mapCanvas().scene().removeItem( self.marker )
            self.marker = None

    def clear( self ):
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
        if o.has_key('geometryWkt'):
            wkt = o['geometryWkt']
            # Fix invalid wkt
            if wkt.startswith('BOX'):
                wkt = 'LINESTRING' + wkt[3:]
                geom = QgsGeometry.fromRect( QgsGeometry.fromWkt( wkt ).boundingBox() )
            else:
                geom = QgsGeometry.fromWkt( wkt )
        elif o.has_key('xMin'):
            geom = QgsGeometry.fromRect( QgsRectangle( o['xMin'], o['yMin'], o['xMax'], o['yMax']) )
        else:
            geom = QgsGeometry.fromPoint(QgsPoint(o['x'] , o['y']))

        # Zoom to feature
        bufgeom = geom.buffer(50.0, 2)
        #if self.qgisIface.mapCanvas().mapRenderer().hasCrsTransformEnabled():
        bufgeom.transform(self.crsTransform)
        rect= bufgeom.boundingBox()
        #print "BBOX: ", rect.toString()
        mc=self.qgisIface.mapCanvas()
        mc.setExtent( rect )

        # Mark the spot
        #print "Geom: ", geom.exportToWkt()
        #if self.qgisIface.mapCanvas().mapRenderer().hasCrsTransformEnabled():
        geom.transform( self.crsTransform )
        #print"Transformed geom: ", geom.exportToWkt()
        self.setMarkerGeom( geom )

        mc.refresh()

##        str = self.ui.searchEdit.text()
##        url = QString(GSEARCH_URL).arg(str)
##        QDesktopServices.openUrl(QUrl(url))
##
##    def keyPressEvent(self, event):
##        if event.key() == Qt.Key_Escape:
##            self.close()
    
    def show_settings_dialog(self):
        # create and show the dialog
        dlg = settingsdialog.SettingsDialog()
        dlg.loginLineEdit.setText(self.config['username'])
        dlg.passwordLineEdit.setText(self.config['password'])
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        print "SettingsDialog result", result
        # See if OK was pressed
        if result == 1:
            # save settings
            self.config['username'] = str(dlg.loginLineEdit.text())
            self.config['password'] = str(dlg.passwordLineEdit.text())
            self.updateconfig()
    
    def unload( self ):
        self.completion.unload()
        self.clearMarkerGeom()



if __name__ == "__main__":

    app = QApplication(sys.argv)

    suggest = SearchBox()
    #suggest.setWindowFlags(Qt.FramelessWindowHint)
    suggest.show()

    #charm = DragMoveCharm()
    #charm.activateOn(suggest)

    sys.exit(app.exec_())