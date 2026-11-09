# -*- coding: utf-8 -*-
"""
"Hvad er nyt" – what changed in Geosearch DK 4.0 (Bifrost), and why.

The text is help/hvad_er_nyt.html, or help/hvad_er_nyt.en.html when QGIS runs
in English (see language.py). Public API:

    show_whats_new(parent=None, anchor=None, settings=None)
        Open the dialog, optionally scrolled to an anchor in the text,
        e.g. "kommunefilter". Returns the dialog (non-modal).

The dialog only opens when the user asks for it (ⓘ, the banner in the search
panel, the kommunefilter links). Opening it marks this NOTICE_VERSION as seen
(setting ``notice_seen_version``) and emits ``notifier.opened``, so the search
panel can hide its banner and the dot on ⓘ, see notice.py.
"""

import os

from qgis.PyQt.QtCore import QObject, Qt, QTimer, QUrl, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextBrowser,
    QVBoxLayout,
)

from .language import localized_file, ui_language
from .notice import NOTICE_VERSION, SEEN_SETTING

HELP_FILE = os.path.join(os.path.dirname(__file__), "help", "hvad_er_nyt.html")


def help_file(language=None):
    """The text in ``language`` ("en" or "da"; default: the QGIS language)."""
    return localized_file(HELP_FILE, language or ui_language())


class _Notifier(QObject):
    opened = pyqtSignal()


notifier = _Notifier()
_dialog = None


class WhatsNewDialog(QDialog):
    def __init__(self, parent=None, anchor=None):
        super().__init__(parent)
        self.setObjectName("geosearchWhatsNew")
        self.setWindowTitle(self.tr("Geosearch DK – hvad er nyt"))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(600, 640)

        self.browser = QTextBrowser(self)
        self.browser.setObjectName("whatsNewBrowser")
        self.browser.setOpenExternalLinks(True)
        self.browser.setSource(QUrl.fromLocalFile(help_file()))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(self.tr("Luk"))
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)
        layout.addWidget(buttons)

        self.scroll_to(anchor)

    def scroll_to(self, anchor=None):
        # Deferred: the document has no layout before the dialog is shown.
        if anchor:
            QTimer.singleShot(0, lambda: self.browser.scrollToAnchor(anchor))
        else:
            QTimer.singleShot(
                0, lambda: self.browser.verticalScrollBar().setValue(0)
            )


def notice_seen(settings):
    return settings.value(SEEN_SETTING) == NOTICE_VERSION


def show_whats_new(parent=None, anchor=None, settings=None):
    """Open "Hvad er nyt", optionally at an anchor in the text (see help_file).

    From a modal dialog (e.g. the settings page), pass a widget in that dialog
    as parent, so the new dialog is not blocked by it.
    """
    global _dialog
    if settings is None:
        from .config import Settings

        settings = Settings()
    close_whats_new()
    _dialog = WhatsNewDialog(parent, anchor=anchor)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()
    settings.set_value(SEEN_SETTING, NOTICE_VERSION)
    notifier.opened.emit()
    return _dialog


def close_whats_new():
    global _dialog
    if _dialog is not None:
        try:
            _dialog.close()
        except RuntimeError:
            pass  # already deleted
    _dialog = None
