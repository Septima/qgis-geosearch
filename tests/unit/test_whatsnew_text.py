"""The "Hvad er nyt" text (help/hvad_er_nyt.html) and the copies of its bullets."""

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "src" / "geosearch_dk" / "help" / "hvad_er_nyt.html"
WHY = "Hvorfor: Bifrost tilbyder det ikke."

# Used by whatsnew.show_whats_new(parent, anchor=...), e.g. from the kommunefilter (#11).
ANCHORS = [
    "noegle",
    "nyt",
    "anderledes",
    "visningstekst",
    "matrikel",
    "geometri",
    "kommunefilter",
    "virker-ikke",
    "delord",
    "kommunefilter-server",
    "undertype",
    "sammenlign",
]


class _Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names, self.ids, self.hrefs = set(), set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "name" in attrs:
            self.names.add(attrs["name"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])


def _parse():
    p = _Anchors()
    p.feed(HTML.read_text(encoding="utf-8"))
    return p


def test_anchors_exist_for_qtextbrowser_and_browsers():
    p = _parse()
    for anchor in ANCHORS:
        assert anchor in p.names, anchor  # QTextBrowser.scrollToAnchor
        assert anchor in p.ids, anchor


def test_internal_links_point_to_anchors():
    p = _parse()
    for href in p.hrefs:
        if href.startswith("#"):
            assert href[1:] in p.names, href
        else:
            assert href.startswith("https://"), href


def _flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_why_is_given_for_each_lost_feature_in_all_copies():
    for path in (HTML, ROOT / "README.md"):
        text = _flat(path)
        assert text.count(WHY) == 3, path
        for phrase in ("nørrebrog", "Stednavnets undertype", "Kommunefilter i søgetjenesten"):
            assert phrase in text, (path, phrase)


SETTINGS_PY = ROOT / "src" / "geosearch_dk" / "config" / "settings.py"
NO_BUILT_IN_KEY = "Pluginet har ingen indbygget nøgle"


def _settings_constant(name):
    # config/settings.py imports qgis, so read the constant from the source.
    match = re.search(name + r'\s*=\s*\(?\s*"([^"]*)"', SETTINGS_PY.read_text(encoding="utf-8"))
    assert match, name
    return match.group(1)


def test_key_text_matches_the_built_in_key():
    """#5: the text says there is no built-in key while DEFAULT_BIFROST_KEY is empty."""
    has_key = bool(_settings_constant("DEFAULT_BIFROST_KEY"))
    for path in (HTML, ROOT / "README.md"):
        text = _flat(path)
        assert "token til Dataforsyningen kan ikke bruges" in text, path
        assert (NO_BUILT_IN_KEY in text) is not has_key, (
            f"{path}: update the key text, DEFAULT_BIFROST_KEY has changed"
        )


def test_key_help_link_matches_the_settings_page():
    url = _settings_constant("BIFROST_KEY_HELP_URL")
    assert url in _parse().hrefs
    assert f"]({url})" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_no_longer_describes_the_token():
    text = _flat(ROOT / "README.md")
    assert "dataforsyningen.dk/user#token" not in text
    assert "fungerende token" not in text
