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

import json
import os
import re
import sys
import time

from osgeo import ogr

from qgis.PyQt.QtWidgets import (
    QWIDGETSIZE_MAX,
    QApplication,
    QDockWidget,
    QFrame,
    QMainWindow,
    QMessageBox,
    QPushButton,
)
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtCore import QEvent, QSettings, QSize, Qt, QTimer
from qgis.PyQt import uic
from qgis.core import (
    QgsApplication,
    QgsWkbTypes,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsRectangle,
    Qgis,
)
from qgis.gui import QgsVertexMarker, QgsRubberBand

from . import kommunefilter_info, notice, qgisutils, whatsnew
from .bifrost import settings_model
from .suggester import Suggester
from .config import Settings

# Seconds a not-authorised/missing-key message stays and is not repeated.
MESSAGE_DURATION = 15
ZOOM_BUFFER = 200.0
ICONS = os.path.join(os.path.dirname(__file__), "icons")

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui_search.ui")
)


class SearchBox(QFrame, FORM_CLASS):

    def __init__(self, qgisIface, settings):
        QFrame.__init__(self, qgisIface.mainWindow())
        self.setupUi(self)

        self.qgisIface = qgisIface
        self.settings = settings
        self.markers = []
        self._last_message = {}
        self._zoomed_extent = None
        self.readconfig()  # old config

        self.setFrameStyle(QFrame.Shape.StyledPanel + QFrame.Shadow.Raised)

        self.suggester = Suggester(
            settings=settings,
            searchbox_widget=self.searchEdit,
            notauthorized_func=self.handleNotAuthorized,
            missingkey_func=self.handleMissingKey,
            hiddeninfo_func=self.showKommunefilterInfo,
            kommunefiltererror_func=self.handleKommunefilterError,
        )
        self.setupCrsTransform()

        self.searchEdit.returnPressed.connect(self.showSelected)
        self.searchEdit.cleared.connect(self.clearSelection)
        self.searchEdit.textEdited.connect(self.clearSelection)
        if hasattr(self.searchEdit, "setPlaceholderText"):
            self.searchEdit.setPlaceholderText(
                self.tr("Søg adresse, stednavn, postnummer, matrikel m.m.")
            )

        # Listen to crs changes
        self.qgisIface.mapCanvas().destinationCrsChanged.connect(
            self.setupCrsTransform
        )

        self.infoButton.setIconSize(QSize(16, 16))
        self.infoButton.setFixedSize(20, 20)
        self.infoButton.clicked.connect(lambda: self.show_whats_new())
        self._setupBanner()

        self.adjustSize()
        self.resize(50, self.height())
        self.searchEdit.setFocus()

        self.settingsButton = self.settingsButton
        settings_icon = QIcon(
            ":images/themes/default/console/iconSettingsConsole.svg"
        )
        self.settingsButton.setIcon(settings_icon)
        self.settingsButton.setIconSize(QSize(16, 16))
        # self.settingsButton.setStyleSheet('border: none;')
        self.settingsButton.setFixedSize(20, 20)

        self.settingsButton.clicked.connect(lambda: self.show_settings())

    def show_whats_new(self, anchor=None):
        whatsnew.show_whats_new(
            self.qgisIface.mainWindow(), anchor=anchor, settings=self.settings
        )

    def show_settings(self, focus_key=False):
        self.settings.focus_key_on_open = focus_key
        try:
            self.qgisIface.showOptionsDialog(currentPage="geosearchOptions")
        finally:
            self.settings.focus_key_on_open = False

    # -- The banner below the search field and the dot on ⓘ (notice.py) -------

    def _setupBanner(self):
        self._infoIcons = {
            False: QIcon(os.path.join(ICONS, "info.svg")),
            True: QIcon(os.path.join(ICONS, "info-new.svg")),
        }
        self._bannerIcons = {
            notice.INFO: QgsApplication.getThemeIcon("/mIconInfo.svg"),
            notice.KEY: QgsApplication.getThemeIcon("/mIconWarning.svg"),
        }
        self._bannerShown = None  # (state, narrow) of the text shown
        self._bannerFitted = None  # (visible, label height) the dock was fitted to
        self.bannerCloseButton.setToolTip(self.tr("Skjul beskeden"))
        self.bannerCloseButton.clicked.connect(self.closeBanner)
        self.bannerLabel.linkActivated.connect(self._bannerLinkActivated)
        self.bannerLabel.installEventFilter(self)
        self.settings.settings_updated.connect(self.updateBanner)
        whatsnew.notifier.opened.connect(self.updateBanner)
        self.updateBanner()

    def bannerState(self):
        """notice.KEY, notice.INFO or None."""
        return notice.banner_state(
            has_key=bool(self.settings.bifrost_key()),
            upgraded=self.settings.value(settings_model.UPGRADED_FROM_3X_SETTING),
            seen_version=self.settings.value(notice.SEEN_SETTING),
            closed_version=self.settings.value(notice.CLOSED_SETTING),
        )

    def updateBanner(self, *args):
        dot = notice.show_dot(
            self.settings.value(settings_model.UPGRADED_FROM_3X_SETTING),
            self.settings.value(notice.SEEN_SETTING),
        )
        self.infoButton.setIcon(self._infoIcons[dot])
        state = self.bannerState()
        if state is None:
            self._bannerShown = None
            self.bannerFrame.hide()
            self._shrinkToContents()
            return
        narrow = notice.is_narrow(self.width())
        if self._bannerShown != (state, narrow):
            self._bannerShown = (state, narrow)
            self.bannerFrame.setStyleSheet(notice.stylesheet(state))
            self.bannerIcon.setPixmap(self._bannerIcons[state].pixmap(16, 16))
            self.bannerLabel.setText(self._bannerHtml(state, narrow))
            self.bannerCloseButton.setVisible(state == notice.INFO)
        self.bannerFrame.show()
        self._fitBannerHeight()

    def _bannerHtml(self, state, narrow):
        link_color = notice.STYLES[state]["text"]
        if state == notice.KEY:
            message = (
                self.tr("Søgning kræver en Bifrost-nøgle.")
                if narrow
                else self.tr("Bifrost kræver en API-nøgle, og der er ikke angivet nogen.")
            )
            links = [
                (notice.LINK_ENTER_KEY, self.tr("Indtast nøgle")),
                (notice.LINK_WHY_KEY, self.tr("Hvorfor?")),
            ]
        else:
            message = (
                self.tr("Søgningen bruger nu Bifrost. Noget virker anderledes.")
                if narrow
                else self.tr(
                    "Geosearch DK søger nu i Klimadatastyrelsens Bifrost i stedet "
                    "for GSearch. Noget virker anderledes."
                )
            )
            links = [(notice.LINK_WHATS_NEW, self.tr("Se hvad der er ændret"))]
        return notice.banner_html(message, links, narrow, link_color)

    def _bannerLinkActivated(self, link):
        if link == notice.LINK_ENTER_KEY:
            self.show_settings(focus_key=True)
        elif link == notice.LINK_WHY_KEY:
            self.show_whats_new(anchor="noegle")
        else:
            self.show_whats_new()

    def closeBanner(self):
        """✕: hide the "info" banner for this NOTICE_VERSION. The dot stays."""
        self.settings.set_value(notice.CLOSED_SETTING, notice.NOTICE_VERSION)
        self.updateBanner()

    def _fitBannerHeight(self):
        # A dock does not ask its widget for heightForWidth, and a wrapped
        # label's sizeHint assumes some other width, so fix the label's height:
        # it is neither cut off in a narrow dock nor too tall in a wide one.
        width = self.bannerLabel.width()
        if width > 0:
            # heightForWidth is bounded by the label's own min and max height
            self.bannerLabel.setMinimumHeight(0)
            self.bannerLabel.setMaximumHeight(QWIDGETSIZE_MAX)
            self.bannerLabel.setFixedHeight(self.bannerLabel.heightForWidth(width))
        self._shrinkToContents()

    def eventFilter(self, obj, event):
        # The label gets its new width after our resizeEvent; fit it then
        if (
            obj is self.bannerLabel
            and event.type() == QEvent.Type.Resize
            and event.size().width() != event.oldSize().width()
        ):
            self._fitBannerHeight()
        return super().eventFilter(obj, event)

    def _shrinkToContents(self):
        self.updateGeometry()
        fitted = (
            self.bannerFrame.isVisibleTo(self),
            self.bannerLabel.minimumHeight(),
        )
        if fitted != self._bannerFitted:
            self._bannerFitted = fitted
            QTimer.singleShot(0, self._fitDock)

    def fitDock(self, *args):
        if self.bannerFrame.isVisibleTo(self):
            QTimer.singleShot(0, self._fitDock)

    def _fitDock(self):
        # A top or bottom dock keeps its height when the banner appears or
        # disappears; give it the height the panel needs now.
        dock = self.parentWidget()
        if not isinstance(dock, QDockWidget) or dock.isFloating():
            return
        window = dock.parentWidget()
        if not isinstance(window, QMainWindow):
            return
        area = window.dockWidgetArea(dock)
        if area in (
            Qt.DockWidgetArea.TopDockWidgetArea,
            Qt.DockWidgetArea.BottomDockWidgetArea,
        ):
            window.resizeDocks(
                [dock], [dock.sizeHint().height()], Qt.Orientation.Vertical
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.bannerFrame.isVisible():
            self.updateBanner()

    def readconfig(self):
        settings = Settings()  # new config
        # Old way was storing settings in global scope. Leave advanced options there for now
        s = QSettings()
        k = __package__

        # prefix muncodes
        # muncodes = re.findall(r'\d+', settings.value('kommunefilter'))
        # areafilter = ','.join(['muncode0'+str(k) for k in muncodes])

        self.config = {
            "maxresults": s.value(k + "/maxresults", 25, type=int),
            #'callback': str(s.value(k + "/callback", "callback", type=str)),
            #'areafilter': areafilter,
            "rubber_color": str(
                s.value(k + "/rubber_color", "#FF0000", type=str)
            ),
            "rubber_width": s.value(k + "/rubber_width", 4, type=int),
            "marker_color": str(
                s.value(k + "/marker_color", "#FF0000", type=str)
            ),
            "marker_icon": s.value(
                k + "/marker_icon",
                QgsVertexMarker.IconType.ICON_CROSS,
                type=int,
            ),
            "marker_width": s.value(k + "/marker_width", 4, type=int),
            "marker_size": s.value(k + "/marker_size", 30, type=int),
        }

    def handleNotAuthorized(self):
        self._pushSettingsMessage(
            "notauthorized",
            self.tr("Afvist af Bifrost"),
            self.tr("Nøglen til Bifrost mangler eller er ugyldig."),
        )

    def handleMissingKey(self):
        # Said by the key banner, which stays until a key is entered.
        self.updateBanner()

    def handleKommunefilterError(self, message):
        self._pushSettingsMessage("kommunefilter", self.tr("Kommunefilter"), message)

    def showKommunefilterInfo(self):
        """Explain the kommune filter (the grey "skjult" row was chosen)."""
        box = QMessageBox(self.qgisIface.mainWindow())
        box.setWindowTitle(self.tr("Geosearch DK - Kommunefilter"))
        box.setIcon(QMessageBox.Icon.Information)
        # macOS renders message box text in bold; keep the explanation normal.
        box.setText(kommunefilter_info.info_title())
        box.setInformativeText(
            '<div style="font-weight: normal">'
            + kommunefilter_info.info_body_html()
            + "</div>"
        )
        settings_button = box.addButton(
            self.tr("Åbn indstillinger"), QMessageBox.ButtonRole.ActionRole
        )
        box.addButton(QMessageBox.StandardButton.Close)
        exec_func = getattr(box, "exec", None) or getattr(box, "exec_")
        exec_func()
        if box.clickedButton() is settings_button:
            self.show_settings()

    def showKommunefilterMigrationNotice(self):
        """Tell a 3.x user once that their kommune filter now works differently."""
        widget = self.qgisIface.messageBar().createMessage(
            "Geosearch DK", kommunefilter_info.migration_text()
        )
        button = QPushButton(widget)
        button.setText(self.tr("Åbn indstillinger"))
        button.pressed.connect(self.show_settings)
        widget.layout().addWidget(button)
        whatsnew_button = QPushButton(widget)
        whatsnew_button.setText(self.tr("Hvad er nyt"))
        whatsnew_button.pressed.connect(self.showKommunefilterWhatsNew)
        widget.layout().addWidget(whatsnew_button)
        self.qgisIface.messageBar().pushWidget(widget, level=Qgis.MessageLevel.Info)

    def showKommunefilterWhatsNew(self):
        whatsnew.show_whats_new(
            self.qgisIface.mainWindow(),
            anchor=kommunefilter_info.WHATSNEW_ANCHOR,
            settings=self.settings,
        )

    def _pushSettingsMessage(self, kind, title, message):
        # Searches run as the user types; show each message once per duration.
        now = time.monotonic()
        last = self._last_message.get(kind)
        if last is not None and now - last < MESSAGE_DURATION:
            return
        self._last_message[kind] = now
        button_text = self.tr("Åbn indstillinger")
        widget = self.qgisIface.messageBar().createMessage(title, message)
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: self.qgisIface.showOptionsDialog(
                currentPage="geosearchOptions"
            )
        )
        widget.layout().addWidget(button)
        self.qgisIface.messageBar().pushWidget(
            widget, level=Qgis.MessageLevel.Warning, duration=MESSAGE_DURATION
        )

    def setupCrsTransform(self):
        if QgsCoordinateReferenceSystem is not None:
            srcCrs = QgsCoordinateReferenceSystem.fromEpsgId(25832)
            dstCrs = qgisutils.getCurrentCrs(self.qgisIface)
            self.crsTransform = QgsCoordinateTransform(
                srcCrs, dstCrs, QgsProject.instance()
            )

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
            if (
                QgsWkbTypes.geometryType(geom.wkbType())
                == QgsWkbTypes.GeometryType.PointGeometry
            ):
                m = self._setPointMarker(geom)
            elif QgsWkbTypes.geometryType(geom.wkbType()) in (
                QgsWkbTypes.GeometryType.LineGeometry,
                QgsWkbTypes.GeometryType.PolygonGeometry,
            ):
                m = self._setRubberBandMarker(geom)
            self.markers.append(m)

    def _setPointMarker(self, pointgeom):
        m = QgsVertexMarker(self.qgisIface.mapCanvas())
        m.setColor(QColor(self.config["marker_color"]))
        m.setIconType(self.config["marker_icon"])
        m.setPenWidth(self.config["marker_width"])
        m.setIconSize(self.config["marker_size"])
        m.setCenter(pointgeom.asPoint())
        return m

    def _setRubberBandMarker(self, geom):
        m = QgsRubberBand(self.qgisIface.mapCanvas())  # not polygon
        if (
            QgsWkbTypes.geometryType(geom.wkbType())
            == QgsWkbTypes.GeometryType.LineGeometry
        ):
            linegeom = geom
        elif (
            QgsWkbTypes.geometryType(geom.wkbType())
            == QgsWkbTypes.GeometryType.PolygonGeometry
        ):
            linegeom = QgsGeometry.fromPolylineXY(geom.asPolygon()[0])
        m.setToGeometry(linegeom, None)
        m.setColor(QColor(self.config["rubber_color"]))
        m.setWidth(self.config["rubber_width"])
        return m

    def clearMarkerGeom(self):
        if self.markers:
            for m in self.markers:
                self.qgisIface.mapCanvas().scene().removeItem(m)
        self.markers = []

    def clearSelection(self):
        """A new search or a cleared box: drop the marker and any pending geometry."""
        self.suggester.fetcher.cancel_geometry()
        self._zoomed_extent = None
        self.clearMarkerGeom()

    def clear(self):
        self.clearSelection()
        self.ui.searchEdit.clear()

    def showSelected(self):
        try:
            self.suggester.preventSuggest()
            self.clearSelection()

            row = self.suggester.selectedObject[0]
            if not row:
                return
            if row["status"] == "error":
                QMessageBox.information(
                    self.qgisIface.mainWindow(),
                    self.tr("Geosearch DK - Fejl"),
                    row.get("message") or row["text"],
                )
                return

            # Zoom to the point now; the full geometry follows when fetched.
            point = self._geojsonToGeometry(row.get("point"))
            if point:
                self._zoomTo(point)
                self._showGeometry(point)
            self.suggester.fetcher.fetch_geometry(row, self._onGeometry)
        except Exception as e:
            QgsApplication.messageLog().logMessage(
                self.tr("Kunne ikke vise valgt objekt: %s") % e,
                "Geosearch DK",
                Qgis.MessageLevel.Warning,
            )

    def _onGeometry(self, row, geojson):
        # Only called for the current selection (see BifrostFetcher.fetch_geometry).
        geom = self._geojsonToGeometry(geojson)
        if not geom:
            if self._zoomed_extent is None:
                point = self._geojsonToGeometry(row.get("point"))
                if point:
                    self._zoomTo(point)
                    self._showGeometry(point)
            return
        # Follow with the zoom only if the user has not moved the map meanwhile.
        if self._zoomed_extent is None or self._mapUnmoved():
            self._zoomTo(geom)
        self._showGeometry(geom)

    def _geojsonToGeometry(self, geojson):
        """QgsGeometry in EPSG:25832 from a GeoJSON geometry, or None."""
        if not geojson:
            return None
        ogr_geom = ogr.CreateGeometryFromJson(json.dumps(geojson))
        if ogr_geom is None:
            return None
        geom = QgsGeometry.fromWkt(ogr_geom.ExportToWkt())
        return None if geom.isNull() else geom

    def _zoomTo(self, geom):
        bufgeom = geom.buffer(ZOOM_BUFFER, 2)
        bufgeom.transform(self.crsTransform)
        mc = self.qgisIface.mapCanvas()
        mc.setExtent(bufgeom.boundingBox())
        mc.refresh()
        self._zoomed_extent = QgsRectangle(mc.extent())

    def _mapUnmoved(self):
        current = self.qgisIface.mapCanvas().extent()
        tolerance = max(current.width(), current.height()) * 1e-6
        return (
            abs(current.xMinimum() - self._zoomed_extent.xMinimum()) <= tolerance
            and abs(current.yMinimum() - self._zoomed_extent.yMinimum()) <= tolerance
            and abs(current.xMaximum() - self._zoomed_extent.xMaximum()) <= tolerance
            and abs(current.yMaximum() - self._zoomed_extent.yMaximum()) <= tolerance
        )

    def _showGeometry(self, geom):
        geom = QgsGeometry(geom)
        geom.transform(self.crsTransform)
        self.setMarkerGeom(geom)
        self.qgisIface.mapCanvas().refresh()

    def show_about_dialog(self):
        infoString = self.tr(
            "Geosearch DK lader brugeren zoome til navngivne steder i Danmark.<br />"
            "Pluginet benytter Klimadatastyrelsens søgetjeneste Bifrost, som afløser GSearch.<br />"
            'Pluginets webside: <a href="http://github.com/Septima/qgis-geosearch">github.com/Septima/qgis-geosearch</a><br />'
            "Udviklet af: Septima<br />"
            'Mail: <a href="mailto:kontakt@septima.dk">kontakt@septima.dk</a><br />'
            'Web: <a href="http://www.septima.dk">www.septima.dk</a>\n'
        )
        QMessageBox.information(
            self.qgisIface.mainWindow(), self.tr("Om Geosearch DK"), infoString
        )

    def unload(self):
        for signal in (self.settings.settings_updated, whatsnew.notifier.opened):
            try:
                signal.disconnect(self.updateBanner)
            except (TypeError, RuntimeError):
                pass
        self.bannerLabel.removeEventFilter(self)
        self.suggester.unload()
        self.clearMarkerGeom()

    def _extractAsSingle(self, geom):
        multiGeom = QgsGeometry()
        geometries = []
        if geom.type() == QgsWkbTypes.GeometryType.PointGeometry:
            if geom.isMultipart():
                multiGeom = geom.asMultiPoint()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPointXY(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.GeometryType.LineGeometry:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolyline()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolylineXY(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.GeometryType.PolygonGeometry:
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

    exec_func = getattr(app, "exec", None) or getattr(app, "exec_")
    sys.exit(exec_func())
