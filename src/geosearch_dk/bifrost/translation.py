"""Translation hook for the pure modules (bifrost/*, kommunefilter_info.py).

They must not import Qt, so they call ``tr(context, text)``, which returns the
Danish source text until the plugin installs ``QCoreApplication.translate``
with ``set_translate``. Call ``tr`` when a text is shown, not at import time:
the plugin installs its translator after the modules are imported.

scripts/update_ts.py collects the ``tr`` calls for i18n/en.qt.ts, so pass the
context ("bifrost" or "kommunefilter") and the text as string literals. The type
titles in types.py are collected too and translated with ``tr("bifrost", title)``.
"""

_translate = None


def set_translate(translate):
    """Install ``translate(context, text)``; None restores the Danish texts."""
    global _translate
    _translate = translate


def tr(context, text):
    if _translate is None:
        return text
    return _translate(context, text)
