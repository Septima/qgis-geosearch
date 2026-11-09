"""The language of the plugin's user interface: English or Danish.

The source texts are Danish. QGIS running in English (any ``en*`` locale, e.g.
``en_DK``) gets English everywhere: i18n/en.qt.qm and help/hvad_er_nyt.en.html.
Every other locale gets Danish, so the user never sees a mix of the two.

``language_for`` is pure; ``ui_language`` reads the QGIS locale.
"""

import os

ENGLISH = "en"
DANISH = "da"

I18N_DIR = os.path.join(os.path.dirname(__file__), "i18n")


def language_for(locale_name):
    """``"en"`` for an English locale name (``en``, ``en_DK``, ``en-US``), else ``"da"``."""
    name = (locale_name or "").strip().lower()
    return ENGLISH if name[:2] == "en" else DANISH


def ui_language():
    """The language of the QGIS user interface, as ``language_for`` sees it."""
    from qgis.PyQt.QtCore import QSettings

    # QGIS sets locale/userLocale at startup (the system locale unless the user
    # overrides it), so it is the language QGIS itself is shown in.
    return language_for(str(QSettings().value("locale/userLocale", "") or ""))


def localized_file(path, language):
    """``name.en.html`` next to ``name.html`` for English, else ``path`` itself."""
    if language == DANISH:
        return path
    root, ext = os.path.splitext(path)
    return root + "." + language + ext


def translation_file(language):
    """The .qm file for ``language``, or None for Danish (the source language)."""
    if language == DANISH:
        return None
    return os.path.join(I18N_DIR, language + ".qt.qm")
