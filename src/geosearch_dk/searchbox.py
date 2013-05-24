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
RESOURCES = ["Adresser","Stednavne","Postdistrikter","Matrikelnumre","Kommuner","Opstillingskredse","Politikredse","Regioner","Retskredse"]
PLUGINNAME = "geosearch_dk"

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from qgis.core import *
from qgis.gui import *

import microjson

import qgisutils
from autosuggest import AutoSuggest
from ui_search import Ui_searchForm


class SearchBox(QFrame):

    def __init__(self, qgisIface):
        QFrame.__init__(self, qgisIface.mainWindow())

        self.qgisIface = qgisIface
        self.marker = None

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
    
    def getconfig(self):
        self.username = 'septima'
        self.password = ''
        self.resources = RESOURCES
        self.maxresults = 25
        self.callback = 'callback'
#        if self.password is None or len(self.password) < 1 or self.username is None or len(self.username) < 1:
#            QMessageBox.warning(None, 'Manglende brugernavn og password', ' Pluginet mangler konfiguration af brugernavn og password til Kortforsyningen.')
    
    def setconfig(self):
        pass

    def geturl(self, searchterm):
        try:
            return QUrl( QString( BASEURL.format( 
                              resources = ','.join(self.resources), 
                              limit = self.maxresults, 
                              login = self.username, 
                              password = self.password, 
                              callback = self.callback)).arg( searchterm ) )
        except AttributeError:
            self.getconfig()
            return self.geturl( searchterm )

    def parseresponse(self, response):
        # Trim callback
        result = str( response )[ len(self.callback) + 1 : -1]
        #print result
        try:
            obj = microjson.from_json( result )
        except microjson.JSONError:
            QgsMessageLog.logMessage('Invalid JSON response from server: ' + result, PLUGINNAME)
            # Check if we have an auth error
            if 'User not found' in response or 'User not authenticated' in response:
                QMessageBox.warning(None, 'Manglende brugernavn og password', ' Pluginet mangler konfiguration af brugernavn og password til Kortforsyningen.')
            return None
        
        if not obj.has_key('status'):
            QgsMessageLog.logMessage('Unexpected result from server: ' + result, PLUGINNAME)
            return None
        
        if not obj['status'] == 'OK':
            QgsMessageLog.logMessage('Server reported an error: ' + obj['message'], PLUGINNAME)
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