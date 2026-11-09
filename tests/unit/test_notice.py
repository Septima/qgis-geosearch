"""The banner in the search panel and the dot on ⓘ (notice.py)."""

import pytest

from geosearch_dk import notice as n
from geosearch_dk.bifrost import settings_model as m

V = n.NOTICE_VERSION


@pytest.mark.parametrize(
    "has_key, upgraded, seen, closed, expected",
    [
        # No key: the key banner, for everyone, whatever was closed or seen
        (False, False, "", "", n.KEY),
        (False, True, "", "", n.KEY),
        (False, True, V, V, n.KEY),
        # Upgraders get the info banner until they open the dialog or close it
        (True, True, "", "", n.INFO),
        (True, True, "3.9.9", "3.9.9", n.INFO),
        (True, True, V, "", None),
        (True, True, "", V, None),
        # New users get no info banner
        (True, False, "", "", None),
    ],
)
def test_banner_state(has_key, upgraded, seen, closed, expected):
    assert n.banner_state(has_key, upgraded, seen, closed) == expected


@pytest.mark.parametrize(
    "upgraded, seen, expected",
    [(True, "", True), (True, "3.9.9", True), (True, V, False), (False, "", False)],
)
def test_dot_until_the_dialog_is_opened(upgraded, seen, expected):
    # Closing the banner (notice_closed_version) does not remove the dot.
    assert n.show_dot(upgraded, seen) is expected


def test_narrow_below_300_px():
    assert n.is_narrow(299)
    assert not n.is_narrow(300)


def test_banner_html_puts_the_links_on_their_own_line_when_narrow():
    links = [("#a", "Indtast nøgle"), ("#b", "Hvorfor?")]
    wide = n.banner_html("Søgning & mere.", links, False, "#000000")
    narrow = n.banner_html("Søgning & mere.", links, True, "#000000")
    assert wide.startswith("Søgning &amp; mere. <a ")
    assert narrow.startswith("Søgning &amp; mere.<br><a ")
    assert '<a href="#a" style="color: #000000">Indtast&nbsp;nøgle</a>' in wide
    assert '<a href="#b" style="color: #000000">Hvorfor?</a>' in narrow


@pytest.mark.parametrize("state", [n.INFO, n.KEY])
def test_stylesheet_sets_background_and_text_colour(state):
    sheet = n.stylesheet(state)
    assert n.STYLES[state]["background"] in sheet
    # A fixed text colour, so the banner reads in a dark theme too
    assert "color: " + n.STYLES[state]["text"] in sheet


class Settings(dict):
    def contains(self, name):
        return name in self

    def value(self, name):
        return self.get(name, False)

    def set_value(self, name, value):
        self[name] = value


@pytest.mark.parametrize(
    "stored",
    [{"token": "x"}, {"kommunefilter": ""}, {"search_reg": False}, {"search_adr": True}],
)
def test_3x_upgrade_is_detected_from_old_settings(stored):
    s = Settings(stored)
    assert m.detect_3x_upgrade(s.contains, s.value, s.set_value) is True
    assert s[m.UPGRADED_FROM_3X_SETTING] is True and s[m.UPGRADE_CHECKED_SETTING]


def test_a_new_install_is_not_an_upgrade():
    s = Settings()
    assert m.detect_3x_upgrade(s.contains, s.value, s.set_value) is False
    assert s[m.UPGRADED_FROM_3X_SETTING] is False and s[m.UPGRADE_CHECKED_SETTING]


def test_upgrade_is_decided_once():
    s = Settings()
    m.detect_3x_upgrade(s.contains, s.value, s.set_value)
    # A new user saves the settings later: still not an upgrader
    s["search_adr"] = True
    assert m.detect_3x_upgrade(s.contains, s.value, s.set_value) is False

    s = Settings({"token": "x"})
    m.detect_3x_upgrade(s.contains, s.value, s.set_value)
    del s["token"]  # migrate() deletes it
    assert m.detect_3x_upgrade(s.contains, s.value, s.set_value) is True


def test_new_4x_types_do_not_count_as_3x():
    s = Settings({"search_" + key: True for key in ("sog", "vej", "ejl", "udg")})
    assert m.detect_3x_upgrade(s.contains, s.value, s.set_value) is False
