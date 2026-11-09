"""The banner in the search panel and the dot on the ⓘ button.

The "Hvad er nyt" dialog (whatsnew.py) only opens when the user asks for it.
Instead the search panel shows one banner at a time:

- "key" (yellow, cannot be closed): no Bifrost key resolves, so search
  cannot work.
- "info" (blue, closable): the user upgraded from 3.x (GSearch) and has not
  yet opened the dialog or closed the banner for this NOTICE_VERSION.

Upgraders also get a dot on ⓘ until they have opened the dialog.

Pure Python: must not import qgis or PyQt.
"""

import html

# Bump to show the banner and the dot again after an upgrade (and update the text).
NOTICE_VERSION = "4.0.0"
# The NOTICE_VERSION for which the dialog was opened, and the banner closed (✕).
SEEN_SETTING = "notice_seen_version"
CLOSED_SETTING = "notice_closed_version"

INFO = "info"
KEY = "key"

# Below this panel width the short texts are used, with the links on a line of their own.
NARROW_WIDTH = 300

# Link targets in the banner text (QLabel.linkActivated).
LINK_WHATS_NEW = "#hvad-er-nyt"
LINK_ENTER_KEY = "#indtast-noegle"
LINK_WHY_KEY = "#hvorfor-noegle"

# QGIS's own message bar colours (QgsMessageBar, Info and Warning). They are
# fixed and set the text colour too, so they read in a dark theme as well.
STYLES = {
    INFO: {"background": "#e7f5fe", "border": "#b9cfe4", "text": "#2554a1"},
    KEY: {"background": "#ffc800", "border": "#e0aa00", "text": "#000000"},
}


def banner_state(has_key, upgraded, seen_version, closed_version, version=NOTICE_VERSION):
    """Which banner to show: KEY, INFO or None. The key banner wins."""
    if not has_key:
        return KEY
    if upgraded and version not in (seen_version, closed_version):
        return INFO
    return None


def show_dot(upgraded, seen_version, version=NOTICE_VERSION):
    """The dot on ⓘ: for upgraders until the dialog has been opened."""
    return bool(upgraded) and seen_version != version


def is_narrow(width):
    return width < NARROW_WIDTH


def banner_html(message, links, narrow, link_color):
    """``message`` followed by ``links`` ((href, text) pairs).

    Narrow: the links go on a line of their own. Link texts do not wrap.
    """
    anchors = "&nbsp;&nbsp;".join(
        '<a href="{}" style="color: {}">{}</a>'.format(
            href, link_color, html.escape(text).replace(" ", "&nbsp;")
        )
        for href, text in links
    )
    return html.escape(message) + ("<br>" if narrow else " ") + anchors


def stylesheet(state):
    """Style sheet for the banner frame (objectName ``bannerFrame``)."""
    return (
        "QFrame#bannerFrame {{ background-color: {background}; "
        "border: 1px solid {border}; border-radius: 3px; }} "
        "QFrame#bannerFrame QLabel {{ color: {text}; background: transparent; border: none; }} "
        "QFrame#bannerFrame QToolButton {{ color: {text}; background: transparent; "
        "border: none; padding: 0px 2px; }}"
    ).format(**STYLES[state])
