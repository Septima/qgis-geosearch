# -*- coding: utf-8 -*-
"""
Screenshots for README.md, taken in Danish in a fresh QGIS profile.

Run from a shell with ``make screenshots`` (QGIS=4 or 3). It starts QGIS with
the profile "geosearch-screenshots" (recreated every run, locale da_DK, no
Bifrost key), saves the images below and quits:

- docs/images/soegepanel.png: the search panel with the key banner, the
  wrench and the ⓘ button
- docs/images/indstillinger.png: the Geosearch DK page in the QGIS options
"""

import os
import traceback
from pathlib import Path

from qgis.PyQt.QtCore import QEventLoop, QTimer
from qgis.PyQt.QtWidgets import QApplication, QDockWidget, QScrollArea, QWidget
from qgis.core import QgsProject

DOCK_OBJECT_NAME = "Geosearch DK"
OPTIONS_PAGE = "geosearchOptions"
WINDOW_SIZE = (1200, 800)
DIALOG_WIDTH = 1000
DIALOG_MIN_HEIGHT = 500
DIALOG_MAX_HEIGHT = 1600


def log(msg):
    print(f"[readme_screenshots] {msg}", flush=True)


def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(int(ms), loop.quit)
    loop.exec()


def save(widget, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not widget.grab().save(str(path)):
        raise RuntimeError(f"could not save {path}")
    log(f"saved {path}")


def shoot_search_panel(iface, out):
    dock = iface.mainWindow().findChild(QDockWidget, DOCK_OBJECT_NAME)
    if dock is None:
        raise RuntimeError("the Geosearch DK panel was not found")
    dock.show()
    dock.raise_()
    wait(1000)
    save(dock, out / "soegepanel.png")


def shoot_options(iface, out):
    def grab_and_close():
        try:
            dialog = QApplication.activeModalWidget()
            if dialog is None:
                raise RuntimeError("the options dialog did not open")
            # Just tall enough to show the whole Geosearch DK page without scrolling
            ours = dialog.findChild(QWidget, OPTIONS_PAGE)
            page = ours.findChild(QScrollArea) if ours is not None else None
            height = DIALOG_MIN_HEIGHT
            dialog.resize(DIALOG_WIDTH, height)
            wait(300)
            while (
                page is not None
                and page.verticalScrollBar().maximum() > 0
                and height < DIALOG_MAX_HEIGHT
            ):
                height += 10
                dialog.resize(DIALOG_WIDTH, height)
                QApplication.processEvents()
            log(f"options dialog height {height}")
            wait(800)
            save(dialog, out / "indstillinger.png")
        except Exception:
            log(traceback.format_exc())
        finally:
            dialog = QApplication.activeModalWidget()
            if dialog is not None:
                dialog.reject()

    QTimer.singleShot(2000, grab_and_close)
    iface.showOptionsDialog(iface.mainWindow(), currentPage=OPTIONS_PAGE)


def main():
    from qgis.utils import iface

    out = Path(os.environ["SCREENSHOTS_OUT"])
    try:
        iface.mainWindow().resize(*WINDOW_SIZE)
        wait(1000)
        shoot_search_panel(iface, out)
        shoot_options(iface, out)
    except Exception:
        log(traceback.format_exc())
    finally:
        QgsProject.instance().setDirty(False)
        QTimer.singleShot(500, iface.actionExit().trigger)


if __name__ in ("__main__", "__console__"):
    # Started by `qgis --code`: start once QGIS and the plugin are up
    QTimer.singleShot(4000, main)
