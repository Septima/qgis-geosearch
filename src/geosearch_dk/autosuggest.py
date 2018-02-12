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
from qgis.PyQt.QtCore import QObject, Qt, QEvent, QTimer, QPoint
from qgis.PyQt.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame, QApplication
from qgis.PyQt.QtGui import QPalette, QKeyEvent
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from qgis.PyQt.uic import loadUi
from qgis.core import QgsMessageLog

# TODO: Add events to completer? http://www.valuedlessons.com/2008/04/events-in-python.html

class AutoSuggest(QObject):

    def __init__(self, geturl_func, parseresult_func, parent = None):
        QObject.__init__(self, parent)
        self.geturl_func = geturl_func
        self.parseresult_func = parseresult_func
        
        self.editor = parent
        self.networkManager = QNetworkAccessManager()

        self.selectedObject = None
        self.isUnloaded = False

        self.popup = QTreeWidget(parent)
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

        #self.connect(self.popup, SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
        #             self.doneCompletion)
        self.popup.itemClicked.connect( self.doneCompletion )

        self.popup.setWindowFlags(Qt.Popup)
        self.popup.setFocusPolicy(Qt.NoFocus)
        self.popup.setFocusProxy(parent)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        #self.connect(self.timer, SIGNAL("timeout()"), self.autoSuggest)
        self.timer.timeout.connect( self.autoSuggest )
        
        #self.connect(self.editor, SIGNAL("textEdited(QString)"), self.timer, SLOT("start()"))
        #self.editor.textEdited.connect( self.timer.start )
        self.editor.textEdited.connect( self.timer.start )
        #self.editor.textChanged.connect( self.timer.start )

        #self.connect(self.networkManager, SIGNAL("finished(QNetworkReply*)"),
        #             self.handleNetworkData)
        self.networkManager.finished.connect( self.handleNetworkData )

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

    def showCompletion(self, rows):
        # Rows is an iterable of tuples like [("text",object1),("text2", object2),...]
        pal = self.editor.palette()
        color = pal.color(QPalette.Disabled, QPalette.WindowText)

        self.popup.setUpdatesEnabled(False)
        self.popup.clear()
        if rows is None or len( rows ) < 1:
            return

        for row in rows:
            item = QTreeWidgetItem(self.popup)
            item.setText(0, row[0])
            #item.setText(1, hit['type'])
            item.setTextAlignment(1, Qt.AlignRight)
            item.setForeground(1, color)
            item.setData(2, Qt.UserRole, (row[1],)) # Try immutable py obj #http://stackoverflow.com/questions/9257422/how-to-get-the-original-python-data-from-qvariant

        self.popup.setCurrentItem(self.popup.topLevelItem(0))
        self.popup.resizeColumnToContents(0)
        #self.popup.resizeColumnToContents(1)
        self.popup.adjustSize()
        self.popup.setUpdatesEnabled(True)

        h = self.popup.sizeHintForRow(0) * min(15, len(rows)) + 3
        w = max(self.popup.width(), self.editor.width())
        self.popup.resize(w, h)

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
            obj =  item.data(2, Qt.UserRole) #.toPyObject()
            self.selectedObject = obj[0]
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.editor, e)
            e = QKeyEvent(QEvent.KeyRelease, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.editor, e)

    def preventSuggest(self):
        self.timer.stop()

    def autoSuggest(self):
        term = self.editor.text()
        if term:
            qurl = self.geturl_func( term )
            if qurl:
                # TODO: Cancel existing requests: http://qt-project.org/forums/viewthread/18073
                self.networkManager.get(QNetworkRequest( qurl ))      #QUrl(url)))


    def handleNetworkData(self, networkReply):
        url = networkReply.url()
        #print "received url:", url.toString()
        if not networkReply.error():
            response = networkReply.readAll()
            pystring = str(response, 'utf-8')
            #print "Response: ", response
            rows = self.parseresult_func( pystring )
            self.showCompletion( rows )

        networkReply.deleteLater()

    def unload( self ):
        # Avoid processing events after QGIS shutdown has begun
        self.popup.removeEventFilter(self)
        self.isUnloaded = True