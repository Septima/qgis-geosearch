# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : autosuggest
Description          : Search suggestions in QT
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

import sys
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4.uic import loadUi
import microjson

from qgis.core import QgsMessageLog

PLUGINNAME = "Septima Geo Search"

BASEURL = "http://kortforsyningen.kms.dk/Geosearch?service=GEO&search=%1&resources={resources}&limit={limit}&login={login}&password={password}&callback={callback}"
RESOURCES = ["Adresser","Stednavne","Postdistrikter","Matrikelnumre","Kommuner","Opstillingskredse","Politikredse","Regioner","Retskredse"]

# TODO: Add events to completer? http://www.valuedlessons.com/2008/04/events-in-python.html

class AutoSuggest(QObject):

    def __init__(self, username, password, parent = None):
        QObject.__init__(self, parent)
        self.username = username
        self.password = password
        self.resources = RESOURCES
        self.maxresults = 25
        self.callback = 'callback'
        self.update_service_url()
        
        self.editor = parent
        self.networkManager = QNetworkAccessManager()

        self.selectedObject = None
        self.isUnloaded = False

        self.popup = QTreeWidget()
        #self.popup.setColumnCount(2)
        self.popup.setColumnCount(1)
        self.popup.setUniformRowHeights(True)
        self.popup.setRootIsDecorated(False)
        self.popup.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.popup.setSelectionBehavior(QTreeWidget.SelectRows)
        self.popup.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.popup.header().hide()
        self.popup.installEventFilter(self)
        self.popup.setMouseTracking(True)

        self.connect(self.popup, SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.doneCompletion)

        self.popup.setWindowFlags(Qt.Popup)
        self.popup.setFocusPolicy(Qt.NoFocus)
        self.popup.setFocusProxy(parent)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.connect(self.timer, SIGNAL("timeout()"), self.autoSuggest)
        self.connect(self.editor, SIGNAL("textEdited(QString)"), self.timer, SLOT("start()"))

        self.connect(self.networkManager, SIGNAL("finished(QNetworkReply*)"),
                     self.handleNetworkData)

    def update_service_url(self):
        if self.password is None or len(self.password) < 1 or self.username is None or len(self.username is None):
            QMessageBox.warning(None, 'Manglende brugernavn og password', PLUGINNAME + ' mangler konfiguration af brugernavn og password til Kortforsyningen.')
            
        self.serviceurl = BASEURL.format( 
                                         resources = ','.join(self.resources), 
                                         limit = self.maxresults, 
                                         login =self.username, 
                                         password = self.password, 
                                         callback = self.callback)

    def eventFilter(self, obj, ev):
        if obj != self.popup:
            return False

        if ev.type() == QEvent.MouseButtonPress:
            self.popup.hide()
            self.editor.setFocus()
            return True

        if ev.type() == QEvent.KeyPress:
            consumed = False
            key = ev.key()
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                self.doneCompletion()
                consumed = True

            elif key == Qt.Key_Escape:
                self.editor.setFocus()
                self.popup.hide()
                consumed = True

            elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End,
                         Qt.Key_PageUp, Qt.Key_PageDown):
                pass

            else:
                self.editor.setFocus()
                self.editor.event(ev)
                self.popup.hide()

            return consumed

        return False

    def showCompletion(self, choices, hits):
        if not choices or len(choices) != len(hits):
            return

        pal = self.editor.palette()
        color = pal.color(QPalette.Disabled, QPalette.WindowText)

        self.popup.setUpdatesEnabled(False)
        self.popup.clear()
        for choice, hit in zip(choices, hits):
            item = QTreeWidgetItem(self.popup)
            item.setText(0, choice)
            #item.setText(1, hit['type'])
            item.setTextAlignment(1, Qt.AlignRight)
            item.setTextColor(1, color)
            item.setData(2, Qt.UserRole, QVariant((hit,))) # Try immutable py obj #http://stackoverflow.com/questions/9257422/how-to-get-the-original-python-data-from-qvariant

        self.popup.setCurrentItem(self.popup.topLevelItem(0))
        self.popup.resizeColumnToContents(0)
        #self.popup.resizeColumnToContents(1)
        self.popup.adjustSize()
        self.popup.setUpdatesEnabled(True)

        h = self.popup.sizeHintForRow(0) * min(7, len(choices)) + 3
        self.popup.resize(self.popup.width(), h)

        self.popup.move(self.editor.mapToGlobal(QPoint(0, self.editor.height())))
        self.popup.setFocus()
        self.popup.show()

    def doneCompletion(self):
        self.timer.stop()
        self.popup.hide()
        self.editor.setFocus()
        item = self.popup.currentItem()
        if item:
            self.editor.setText(item.text(0) )
            o =  item.data(2, Qt.UserRole) #.toPyObject()
            #print o
            pyobj = o.toPyObject()
            #print pyobj
            self.selectedObject = pyobj[0]
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.editor, e)
            e = QKeyEvent(QEvent.KeyRelease, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.editor, e)

    def preventSuggest(self):
        self.timer.stop()

    def autoSuggest(self):
        term = self.editor.text()
        if not term.isEmpty():
            url = QString( self.serviceurl ).arg( term )
            print "URL: ", self.QstringToStr( url )
            # TODO: Cancel existing requests: http://qt-project.org/forums/viewthread/18073
            self.networkManager.get(QNetworkRequest(QUrl(url)))

    def handleNetworkData(self, networkReply):
        url = networkReply.url()
        print "received url:", self.QstringToStr( url.toString() )
        if not networkReply.error():
            choices = []
            objects = []

            response = networkReply.readAll()
            #print "Response: ", response
            #xml = QXmlStreamReader(response)
            #while not xml.atEnd():
            #    xml.readNext()
            #    if xml.tokenType() == QXmlStreamReader.StartElement:
            #        if xml.name() == "suggestion":
            #            str = xml.attributes().value("data")
            #            choices.append(str.toString())
            #        elif xml.name() == "num_queries":
            #            str = xml.attributes().value("int")
            #            hits.append(str.toString())


            result = str( response )[ 9 : -1]
            #print result

            try:
                obj = microjson.from_json( result )
            except microjson.JSONError:
                QgsMessageLog.logMessage('Invalid JSON response from server: ' + result, PLUGINNAME)
                return

            if not obj.has_key('status'):
                QgsMessageLog.logMessage('Unexpected result from server: ' + result, PLUGINNAME)
                return

            if not obj['status'] == 'OK':
                QgsMessageLog.logMessage('Server reported an error: ' + obj['message'], PLUGINNAME)
                return

            data = obj['data']

            for e in data:
                choices.append( e['presentationString'] )
                #hits.append( e['wkt'] )
                objects.append( e )

            self.showCompletion(choices, objects)

        networkReply.deleteLater()

    def unload( self ):
        # Avoid processing events after QGIS shutdown has begun
        self.popup.removeEventFilter(self)
        self.isUnloaded = True
        
    def QstringToStr(self, qstring):
        return unicode(qstring.toUtf8(),'utf-8').encode('latin_1', 'replace')

