import pytest

from geosearch_dk.bifrost import settings_model as m
from geosearch_dk.bifrost.transport import DEFAULT_BASE_URL
from geosearch_dk.bifrost.types import PROPOSED_TYPES, TYPES

OLD_DEFAULT_TOKEN = "787484d3a8dfee7562ffd6eff1d6e0ee"
DEFAULT_3X_TOKEN = "0350b5341749c0970454474881173412"


class Store:
    """A dict standing in for QSettings."""

    def __init__(self, values=None):
        self.values = dict(values or {})

    def contains(self, name):
        return name in self.values

    def remove(self, name):
        del self.values[name]


def test_type_settings_keep_the_3x_names():
    assert [m.type_setting(t.key) for t in TYPES] == [
        "search_adr",
        "search_ste",
        "search_pos",
        "search_mat",
        "search_kom",
        "search_ops",
        "search_pol",
        "search_reg",
    ]


def test_3x_types_default_on_new_types_off():
    assert all(m.type_default(t.key) for t in TYPES)
    assert not any(m.type_default(t.key) for t in PROPOSED_TYPES)


def test_selected_type_keys_in_display_order():
    values = {m.type_setting(t.key): t.key in ("reg", "adr", "mat") for t in TYPES}
    assert m.selected_type_keys(values.get) == ("adr", "mat", "reg")
    assert m.selected_type_keys(lambda name: False) == ()


def test_checkbox_labels_and_positions():
    assert m.checkbox_label(TYPES[0]) == "Husnumre ('adr')"
    positions = [(t.key, row, col) for t, row, col in m.checkbox_positions(TYPES)]
    assert positions == [
        ("adr", 0, 0),
        ("ste", 1, 0),
        ("pos", 2, 0),
        ("mat", 3, 0),
        ("kom", 0, 1),
        ("ops", 1, 1),
        ("pol", 2, 1),
        ("reg", 3, 1),
    ]
    # An odd number fills the first column first; no cell is used twice.
    nine = m.checkbox_positions(TYPES + PROPOSED_TYPES[:1])
    assert [(r, c) for _, r, c in nine][4:6] == [(4, 0), (0, 1)]
    assert len({(r, c) for _, r, c in nine}) == 9
    assert m.checkbox_positions(()) == []


def test_base_url():
    assert m.base_url("") == DEFAULT_BASE_URL
    assert m.base_url(None) == DEFAULT_BASE_URL
    assert m.base_url("  ") == DEFAULT_BASE_URL
    assert m.base_url(" http://localhost:8000 ") == "http://localhost:8000"


@pytest.mark.parametrize(
    "setting, env, default, expected",
    [
        ("own", {"BIFROST_KEY": "env"}, "bundled", "own"),
        ("", {"BIFROST_KEY": "env"}, "bundled", "env"),
        ("", {}, "bundled", "bundled"),
        (" ", {"BIFROST_KEY": " "}, " bundled ", "bundled"),
        ("", {}, "", ""),
        (None, {}, None, ""),
    ],
)
def test_api_key_order(setting, env, default, expected):
    assert m.api_key(setting, default, env) == expected


@pytest.mark.parametrize("token", [OLD_DEFAULT_TOKEN, DEFAULT_3X_TOKEN, "users-own", ""])
def test_migrate_drops_any_token(token):
    store = Store({"token": token})
    assert m.migrate(store) == ("token",)
    assert store.values == {}


def test_migrate_keeps_types_and_other_settings():
    values = {
        "token": "users-own",
        "search_adr": False,
        "search_mat": True,
        "kommunefilter": "101,147",
        "bifrost_key": "k",
        "bifrost_url": "http://localhost:8000",
    }
    store = Store(values)
    m.migrate(store)
    del values["token"]
    assert store.values == values


def test_migrate_without_settings_and_twice():
    store = Store()
    assert m.migrate(store) == ()
    store = Store({"token": "x", "search_reg": False})
    m.migrate(store)
    assert m.migrate(store) == ()
    assert store.values == {"search_reg": False}


def test_new_type_starts_off_after_upgrade():
    # A 3.x user has search_* stored for the 3.x types only.
    stored = {m.type_setting(t.key): False for t in TYPES}
    stored["search_adr"] = True
    new = PROPOSED_TYPES[0]

    def value(name):
        if name in stored:
            return stored[name]
        return m.type_default(name[len("search_") :])

    assert m.selected_type_keys(value, TYPES + (new,)) == ("adr",)


def run_kommunefilter_migration(values):
    def set_value(name, value):
        values[name] = value

    return m.migrate_kommunefilter(values.get, set_value)


@pytest.mark.parametrize("codes", ["101", "101,147,157", " 615 "])
def test_kommunefilter_from_3x_is_switched_on_once(codes):
    values = {"kommunefilter": codes}
    assert run_kommunefilter_migration(values) is True
    assert values == {
        "kommunefilter": codes,
        "kommunefilter_enabled": True,
        "kommunefilter_migrated": True,
    }
    assert run_kommunefilter_migration(values) is False


@pytest.mark.parametrize("values", [{}, {"kommunefilter": ""}, {"kommunefilter": "  "}])
def test_no_kommunefilter_stays_off(values):
    assert run_kommunefilter_migration(values) is False
    assert "kommunefilter_enabled" not in values
    assert values["kommunefilter_migrated"] is True


def test_kommunefilter_switched_off_later_stays_off():
    # The user unticks the filter after the migration; a restart keeps it off.
    values = {"kommunefilter": "101"}
    run_kommunefilter_migration(values)
    values["kommunefilter_enabled"] = False
    assert run_kommunefilter_migration(values) is False
    assert values["kommunefilter_enabled"] is False
