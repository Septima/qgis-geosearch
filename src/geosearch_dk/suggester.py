# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Suggester
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
from qgis.PyQt.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame, QApplication, QFrame, QMessageBox, QPushButton
from qgis.PyQt.QtGui import QPalette, QKeyEvent
from qgis.PyQt.QtNetwork import QNetworkReply
from qgis.PyQt.uic import loadUi
from qgis.core import QgsApplication, QgsMessageLog, Qgis

from .gsearchfetcher import GSearchFetcher

# TODO: Add events to completer? http://www.valuedlessons.com/2008/04/events-in-python.html

class Suggester(QObject):

    def __init__(self, settings, searchbox_widget = None, notauthorized_func = None):
        QObject.__init__(self, searchbox_widget)
        self.notauthorized_func = notauthorized_func
        
        self.my_searchbox_widget = searchbox_widget
        self.gSearchFetcher = GSearchFetcher(settings)

        self.selectedObject = None
        self.isUnloaded = False

        self.resultlistwidget = QTreeWidget(searchbox_widget)
        #self.resultlistwidget.setColumnCount(2)
        self.resultlistwidget.setColumnCount(1)
        self.resultlistwidget.setUniformRowHeights(True)
        self.resultlistwidget.setRootIsDecorated(False)
        self.resultlistwidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.resultlistwidget.setSelectionBehavior(QTreeWidget.SelectRows)
        self.resultlistwidget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.resultlistwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.resultlistwidget.header().hide()
        self.resultlistwidget.installEventFilter(self)
        self.resultlistwidget.setMouseTracking(True)

        self.resultlistwidget.itemClicked.connect( self.onResultSelected )

        self.resultlistwidget.setWindowFlags(Qt.Popup)
        self.resultlistwidget.setFocusPolicy(Qt.NoFocus)
        self.resultlistwidget.setFocusProxy(searchbox_widget)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.timer.timeout.connect( self.invoke_fetcher )
        
        self.my_searchbox_widget.textEdited.connect( self.timer.start )

        self.gSearchFetcher.finished.connect( self.handleFetcherResults )
        self.last_query_id = 0

    def eventFilter(self, obj, ev):
        if obj != self.resultlistwidget:
            return False

        if ev.type() == QEvent.MouseButtonPress:
            self.resultlistwidget.hide()
            self.my_searchbox_widget.setFocus()
            return True

        if ev.type() == QEvent.KeyPress:
            consumed = False
            key = ev.key()
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                self.onResultSelected()
                consumed = True

            elif key == Qt.Key_Escape:
                self.my_searchbox_widget.setFocus()
                self.resultlistwidget.hide()
                consumed = True

            elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End,
                         Qt.Key_PageUp, Qt.Key_PageDown):
                pass

            else:
                self.my_searchbox_widget.setFocus()
                self.my_searchbox_widget.event(ev)
                self.resultlistwidget.hide()

            return consumed

        return False

    def showResultRows(self, rows):
        pal = self.my_searchbox_widget.palette()
        color = pal.color(QPalette.Disabled, QPalette.WindowText)

        self.resultlistwidget.setUpdatesEnabled(False)
        self.resultlistwidget.clear()
        if rows is None or len( rows ) < 1:
            return

        for row in rows:
            item = QTreeWidgetItem(self.resultlistwidget)
            text = ""
            if row["status"] == "error":
                text = row["resource"]["titel"] + " - Der skete en fejl"
            else:
                text = row["visningstekst"]
            item.setText(0, text)
            item.setTextAlignment(1, Qt.AlignRight)
            item.setForeground(1, color)
            item.setData(2, Qt.UserRole, (row,)) # Try immutable py obj #http://stackoverflow.com/questions/9257422/how-to-get-the-original-python-data-from-qvariant

        self.resultlistwidget.setCurrentItem(self.resultlistwidget.topLevelItem(0))
        self.resultlistwidget.resizeColumnToContents(0)
        self.resultlistwidget.adjustSize()
        self.resultlistwidget.setUpdatesEnabled(True)

        h = self.resultlistwidget.sizeHintForRow(0) * min(15, len(rows)) + 3
        w = max(self.resultlistwidget.width(), self.my_searchbox_widget.width())
        self.resultlistwidget.resize(w, h)

        self.resultlistwidget.move(self.my_searchbox_widget.mapToGlobal(QPoint(0, self.my_searchbox_widget.height())))
        self.resultlistwidget.setFocus()
        self.resultlistwidget.show()

    def onResultSelected(self):
        self.timer.stop()
        self.resultlistwidget.hide()
        self.my_searchbox_widget.setFocus()
        item = self.resultlistwidget.currentItem()
        if item:
            row =  item.data(2, Qt.UserRole) #.toPyObject()
            if row[0]["status"] != "error":
                self.my_searchbox_widget.setText(item.text(0) )
            self.selectedObject = row
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.my_searchbox_widget, e)
            e = QKeyEvent(QEvent.KeyRelease, Qt.Key_Enter, Qt.NoModifier)
            QApplication.postEvent(self.my_searchbox_widget, e)

    def preventSuggest(self):
        self.timer.stop()

    def invoke_fetcher(self):
        term = self.my_searchbox_widget.text()
        if term:
            self.last_query_id = self.gSearchFetcher.fetch(term)

    def handleFetcherResults(self):
        rows = self.gSearchFetcher.get_result()
        self.showResultRows( rows )
        return
        if (result["ok"]):
            self.showResultRows( rows )
        else:
            QgsApplication.messageLog().logMessage('Server returned: [' + result["errorString"] + '] ' + result["response"], __package__)
            if result["error"] == QNetworkReply.AuthenticationRequiredError:
                if self.notauthorized_func:
                    self.notauthorized_func()


    def unload( self ):
        # Avoid processing events after QGIS shutdown has begun
        self.resultlistwidget.removeEventFilter(self)
        self.isUnloaded = True