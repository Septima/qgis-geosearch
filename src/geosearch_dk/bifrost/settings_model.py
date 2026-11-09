"""The parts of the plugin settings that need no Qt: setting names, defaults,
which types are selected, the type checkbox layout and the migration from 3.x.

``config/settings.py`` stores the settings with QSettings and
``config/settings_dialog.py`` shows them; both use this module.

Pure Python: must not import qgis or PyQt.
"""

from .transport import DEFAULT_BASE_URL, resolve_key
from .types import DEFAULT_ON_KEYS, TYPES
from .translation import tr

KEY_SETTING = "bifrost_key"
URL_SETTING = "bifrost_url"
TYPE_SETTING = "search_{}"
KOMMUNEFILTER_SETTING = "kommunefilter"
KOMMUNEFILTER_ENABLED_SETTING = "kommunefilter_enabled"
# Set once the 3.x kommunefilter has been migrated, so it happens only once.
KOMMUNEFILTER_MIGRATED_SETTING = "kommunefilter_migrated"

# Settings from 3.x (GSearch) that are deleted on upgrade.
# "token": a Dataforsyningen token, the bundled one or the user's own. It
# cannot be used with Bifrost, which needs its own key.
OBSOLETE_SETTINGS = ("token",)

# 3.x stored these only when the user saved the settings (or, for "token",
# when a bundled token was replaced), so any of them means an upgrade from 3.x.
# A 3.x user who never saved the settings cannot be told from a new user.
LEGACY_3X_TYPE_KEYS = ("adr", "ste", "pos", "mat", "kom", "ops", "pol", "reg")
LEGACY_3X_SETTINGS = ("token", KOMMUNEFILTER_SETTING) + tuple(
    TYPE_SETTING.format(k) for k in LEGACY_3X_TYPE_KEYS
)
# Set once the check for an upgrade from 3.x has run, and its result.
UPGRADE_CHECKED_SETTING = "upgrade_checked"
UPGRADED_FROM_3X_SETTING = "upgraded_from_3x"


def type_setting(key):
    """The bool setting that switches a type on: ``search_<key>``."""
    return TYPE_SETTING.format(key)


def type_default(key):
    """Whether a type is searched when the user has not chosen."""
    return key in DEFAULT_ON_KEYS


def selected_type_keys(value, types=TYPES):
    """The keys of the switched-on types, in display order.

    ``value(name)`` returns the value of a setting.
    """
    return tuple(t.key for t in types if value(type_setting(t.key)))


def checkbox_label(search_type):
    return f"{tr('bifrost', search_type.title)} ('{search_type.shown_prefix}')"


def checkbox_positions(types=TYPES, columns=2):
    """``(type, row, column)`` for each type checkbox, filled column by column."""
    types = tuple(types)
    rows = -(-len(types) // columns) if types else 0
    return [(t, i % rows, i // rows) for i, t in enumerate(types)]


def base_url(setting_value):
    """The Bifrost URL to use: the setting, else the default."""
    return (setting_value or "").strip() or DEFAULT_BASE_URL


def api_key(setting_value, default, environ=None):
    """The key to use: the setting, else ``BIFROST_KEY``, else ``default``."""
    return resolve_key(setting_value, environ, default)


def migrate(store):
    """Migrate settings from 3.x. Returns the names of the deleted settings.

    ``store`` has ``contains(name)`` and ``remove(name)``. Running it again
    changes nothing.

    - The Dataforsyningen ``token`` is deleted.
    - ``search_<key>`` values are kept as they are. Types without a stored
      value get ``type_default()``, so new types start switched off.
    - ``kommunefilter`` is migrated by ``migrate_kommunefilter``.
    """
    removed = []
    for name in OBSOLETE_SETTINGS:
        if store.contains(name):
            store.remove(name)
            removed.append(name)
    return tuple(removed)


def detect_3x_upgrade(contains, value, set_value):
    """Whether the user upgraded from 3.x, decided once and then remembered.

    Must run before ``migrate``, which deletes the token. ``contains(name)``
    tells whether a setting is stored; ``value`` and ``set_value`` read and
    write a setting by name. Later runs return the stored answer, so a new
    user who saves the settings is not taken for an upgrader.
    """
    if value(UPGRADE_CHECKED_SETTING):
        return bool(value(UPGRADED_FROM_3X_SETTING))
    upgraded = any(contains(name) for name in LEGACY_3X_SETTINGS)
    set_value(UPGRADED_FROM_3X_SETTING, upgraded)
    set_value(UPGRADE_CHECKED_SETTING, True)
    return upgraded


def migrate_kommunefilter(value, set_value):
    """Switch the kommune filter on once for users who had one in 3.x.

    3.x filtered on the server whenever ``kommunefilter`` was set. Now the
    filter is client-side and opt-in (``kommunefilter_enabled``). ``value`` and
    ``set_value`` read and write a setting by name. Returns True when the
    filter was switched on now, so the user can be told; running it again
    returns False and changes nothing.
    """
    if value(KOMMUNEFILTER_MIGRATED_SETTING):
        return False
    switched_on = bool((value(KOMMUNEFILTER_SETTING) or "").strip())
    if switched_on:
        set_value(KOMMUNEFILTER_ENABLED_SETTING, True)
    set_value(KOMMUNEFILTER_MIGRATED_SETTING, True)
    return switched_on
