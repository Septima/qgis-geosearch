#!/usr/bin/env python3
"""Update src/geosearch_dk/i18n/en.qt.ts from the plugin's Danish source texts.

    python3 scripts/update_ts.py
    /opt/homebrew/bin/lrelease -silent src/geosearch_dk/i18n/en.qt.ts \
        -qm src/geosearch_dk/i18n/en.qt.qm

Collects, per translation context:
  - every <string> in the .ui files (not notr="true"), context = the .ui class
  - self.tr("...") in a class (context = the class name)
  - QCoreApplication.translate("context", "...")
  - tr("context", "...") from bifrost/translation.py (the pure modules)
  - the type titles in bifrost/types.py (context "bifrost")

Existing translations are kept; new texts get an empty translation marked
unfinished, and texts that are no longer used are dropped.
tests/unit/test_translations.py fails until every text has a translation.
pylupdate does not know the hook in the pure modules, hence this script.
"""

import ast
import os
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "src", "geosearch_dk")
TS_FILE = os.path.join(PLUGIN, "i18n", "en.qt.ts")
UI_FILES = ("ui_search.ui", os.path.join("config", "settings.ui"))
SKIP_DIRS = ("qgissettingmanager", "help", "scripts", "__pycache__")


def _rel(path):
    # Locations are relative to the .ts file, as lupdate writes them.
    return os.path.relpath(path, os.path.dirname(TS_FILE)).replace(os.sep, "/")


def _ui_strings(path):
    root = ET.parse(path).getroot()
    context = root.findtext("class")
    for element in root.iter("string"):
        text = element.text or ""
        if element.get("notr") == "true" or not text.strip():
            continue
        yield context, text, None


def _literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


class _PythonStrings(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.found = []

    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        self.generic_visit(node)
        self.classes.pop()

    def visit_Call(self, node):
        func = node.func
        args = [_literal(a) for a in node.args]
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "tr"
            and isinstance(func.value, ast.Name)
            and func.value.id == "self"
            and len(args) == 1
            and args[0] is not None
            and self.classes
        ):
            self.found.append((self.classes[-1], args[0], node.lineno))
        elif (
            (
                (isinstance(func, ast.Attribute) and func.attr == "translate")
                or (isinstance(func, ast.Name) and func.id == "tr")
            )
            and len(args) == 2
            and None not in args
        ):
            self.found.append((args[0], args[1], node.lineno))
        self.generic_visit(node)


def _python_strings(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    visitor = _PythonStrings()
    visitor.visit(tree)
    return visitor.found


def _type_titles():
    sys.path.insert(0, os.path.dirname(PLUGIN))
    try:
        from geosearch_dk.bifrost.types import PROPOSED_TYPES, TYPES
    finally:
        sys.path.pop(0)
    return [t.title for t in TYPES + PROPOSED_TYPES]


def collect():
    """``{context: {source: [(file, line), ...]}}`` in the order found."""
    contexts = OrderedDict()

    def add(context, source, path, line):
        locations = contexts.setdefault(context, OrderedDict()).setdefault(source, [])
        locations.append((_rel(path), line))

    for name in UI_FILES:
        path = os.path.join(PLUGIN, name)
        for context, source, line in _ui_strings(path):
            add(context, source, path, line)
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                path = os.path.join(dirpath, filename)
                for context, source, line in _python_strings(path):
                    add(context, source, path, line)
    types_py = os.path.join(PLUGIN, "bifrost", "types.py")
    for title in _type_titles():
        add("bifrost", title, types_py, None)
    return contexts


def read_ts(path=TS_FILE):
    """``{(context, source): (translation, finished)}``."""
    result = {}
    if not os.path.exists(path):
        return result
    for context in ET.parse(path).getroot().iter("context"):
        name = context.findtext("name")
        for message in context.iter("message"):
            element = message.find("translation")
            finished = element.get("type") not in ("unfinished", "obsolete", "vanished")
            result[(name, message.findtext("source"))] = (element.text or "", finished)
    return result


def write_ts(contexts, translations, path=TS_FILE):
    ts = ET.Element("TS", version="2.1", language="en_DK", sourcelanguage="da_DK")
    for name in sorted(contexts):
        context = ET.SubElement(ts, "context")
        ET.SubElement(context, "name").text = name
        for source, locations in contexts[name].items():
            message = ET.SubElement(context, "message")
            for filename, line in locations:
                location = ET.SubElement(message, "location", filename=filename)
                if line is not None:
                    location.set("line", str(line))
            ET.SubElement(message, "source").text = source
            text, finished = translations.get((name, source), ("", False))
            element = ET.SubElement(message, "translation")
            element.text = text
            if not finished or not text:
                element.set("type", "unfinished")
    ET.indent(ts, space="    ")
    body = ET.tostring(ts, encoding="unicode")
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n')
        f.write(body + "\n")


def main():
    contexts = collect()
    translations = read_ts()
    write_ts(contexts, translations)
    missing = [
        (c, s)
        for c in contexts
        for s in contexts[c]
        if not translations.get((c, s), ("", False))[1]
    ]
    for context, source in missing:
        print(f"untranslated [{context}]: {source}")
    print(f"{TS_FILE}: {sum(len(v) for v in contexts.values())} texts, "
          f"{len(missing)} untranslated")


if __name__ == "__main__":
    main()
