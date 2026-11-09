"""One language at a time: Danish source texts, a complete English translation.

i18n/en.qt.ts must hold every translatable text (scripts/update_ts.py collects
them), each with a finished English translation. The source texts must be
Danish and the translations English, and the "Hvad er nyt" text must exist in
both languages with the same anchors and links.
"""

import importlib.util
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from geosearch_dk import language
from geosearch_dk.bifrost import settings_model, translation
from geosearch_dk.bifrost.core import error_row
from geosearch_dk.bifrost.types import TYPES
from geosearch_dk import kommunefilter_info

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "src" / "geosearch_dk"
HELP_DA = PLUGIN / "help" / "hvad_er_nyt.html"
HELP_EN = PLUGIN / "help" / "hvad_er_nyt.en.html"


def _load_update_ts():
    spec = importlib.util.spec_from_file_location("update_ts", ROOT / "scripts" / "update_ts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


update_ts = _load_update_ts()
COLLECTED = update_ts.collect()
TS = update_ts.read_ts()

# Words that give away English in a text that should be Danish, and the reverse.
ENGLISH_WORDS = {
    "the", "and", "search", "settings", "options", "error", "close", "open",
    "hide", "show", "about", "enter", "key", "you", "your", "what", "new",
    "results", "result", "municipality", "please", "with", "not", "why", "read",
}
DANISH_WORDS = {
    "og", "ikke", "på", "du", "der", "til", "af", "med", "er", "kan", "søg",
    "nøgle", "indstillinger", "kommune", "kommunefilter", "resultater", "fejl",
    "hvad", "nyt", "hvorfor", "læs", "luk", "åbn", "skjul",
}
# Names, the same in both languages.
SAME_IN_BOTH = {"Bifrost URL:"}


def _words(text):
    text = re.sub(r"<i>.*?</i>|<code>.*?</code>", " ", text)  # examples, e.g. "nørrebrog"
    # Tags, links, quoted examples and identifiers such as BIFROST_KEY
    text = re.sub(r"<[^>]+>|https?://\S+|\"[^\"]*\"|'[^']*'|\w+_\w+", " ", text)
    return {w.lower() for w in re.findall(r"[^\W\d_]+", text)}


def _placeholders(text):
    return sorted(re.findall(r"%[sd]", text))


def test_every_text_is_in_the_ts_file():
    """Run scripts/update_ts.py when this fails."""
    collected = {(c, s) for c in COLLECTED for s in COLLECTED[c]}
    assert collected == set(TS)


def test_every_text_has_a_finished_english_translation():
    missing = [key for key, (text, finished) in TS.items() if not (finished and text)]
    assert not missing


def test_translations_keep_the_placeholders():
    for (context, source), (text, _) in TS.items():
        assert _placeholders(text) == _placeholders(source), (context, source)


def test_sources_are_danish():
    for context, source in TS:
        english = _words(source) & ENGLISH_WORDS
        assert not english, (context, source, english)


def test_translations_are_english():
    for (context, source), (text, _) in TS.items():
        danish = _words(text) & DANISH_WORDS
        assert not danish, (context, source, danish)
        assert text != source or source in SAME_IN_BOTH, (context, source)


def test_ui_titles_are_danish_sources():
    # Seen in a Danish QGIS before: an English window title from the .ui file.
    assert ("geosearchConfigWidget", "Geosearch DK - Indstillinger") in TS
    assert ("searchForm", "Søg") in TS
    assert ("SearchBox", "Åbn indstillinger") in TS


def test_type_titles_are_translated():
    for search_type in TYPES:
        assert ("bifrost", search_type.title) in TS


def test_no_stale_dataforsyningen_strings():
    # Only the link text to Dataforsyningen's user signup may mention it.
    allowed = {"Sådan opretter du en bruger på Dataforsyningen"}
    for context, source in TS:
        if "ataforsyningen" in source and source not in allowed:
            assert "kan ikke bruges" in source, (context, source)


# The pure modules translate with the hook the plugin installs.


@pytest.fixture
def english():
    def translate(context, text):
        return TS[(context, text)][0]

    translation.set_translate(translate)
    yield
    translation.set_translate(None)


def test_pure_texts_are_danish_without_a_translator():
    assert settings_model.checkbox_label(TYPES[0]) == "Husnumre ('adr')"
    assert error_row(TYPES[1])["text"] == "Stednavne - Der skete en fejl"
    assert kommunefilter_info.hidden_row_text(2) == "2 resultater uden for kommunefilteret er skjult"


def test_pure_texts_follow_the_translator(english):
    assert settings_model.checkbox_label(TYPES[0]) == "Addresses ('adr')"
    assert error_row(TYPES[1])["text"] == "Place names - An error occurred"
    assert kommunefilter_info.hidden_row_text(1) == "1 result outside the municipality filter is hidden"
    assert kommunefilter_info.hidden_row_text(12) in kommunefilter_info.info_html()
    assert kommunefilter_info.migration_text().startswith("The municipality filter")


# Language and the "Hvad er nyt" text.


@pytest.mark.parametrize(
    "name, expected",
    [
        ("en_DK", "en"),
        ("en_US", "en"),
        ("en", "en"),
        ("EN-gb", "en"),
        ("da_DK", "da"),
        ("da", "da"),
        ("de_DE", "da"),
        ("C", "da"),
        ("", "da"),
        (None, "da"),
    ],
)
def test_language_for_locale(name, expected):
    assert language.language_for(name) == expected


def test_help_file_per_language():
    assert language.localized_file(str(HELP_DA), "da") == str(HELP_DA)
    assert language.localized_file(str(HELP_DA), "en") == str(HELP_EN)
    assert HELP_EN.exists()


def test_translation_file_per_language():
    assert language.translation_file("da") is None
    assert Path(language.translation_file("en")) == PLUGIN / "i18n" / "en.qt.qm"


class _Html(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.names, self.ids, self.hrefs, self.why = [], [], [], 0
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "name" in attrs:
            self.names.append(attrs["name"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if attrs.get("class") == "hvorfor":
            self.why += 1


def test_help_texts_have_the_same_anchors_and_links():
    da, en = _Html(HELP_DA), _Html(HELP_EN)
    assert en.names == da.names
    assert en.ids == da.ids
    assert en.hrefs == da.hrefs
    assert en.why == da.why == 3


def test_english_help_text_is_english():
    text = HELP_EN.read_text(encoding="utf-8")
    body = text[text.index("<body>"):]
    assert not _words(body) & DANISH_WORDS
    assert body.count("Why: Bifrost does not offer it.") == 3
    assert '<html lang="en">' in text
