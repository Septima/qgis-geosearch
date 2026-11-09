# -*- coding: utf-8 -*-
"""
Visual run for Geosearch DK.

Drives the real plugin UI inside a running QGIS: for each case in the case
catalogue it types the input into the search box, waits for the popup,
screenshots it, selects the expected hit with the keyboard, waits for the map
and saves an image of the canvas. The result is a contact sheet in
out/report.html (plus out/report.json).

Only widgets are used (the dock "Geosearch DK", its line edit and the popup
item view), never plugin internals.

Run it from the QGIS Python console (Plugins > Python Console):

    import runpy; runpy.run_path("/path/to/qgis-geosearch/tests/manual/visual_run.py", run_name="__main__")

With arguments:

    import sys; sys.path.insert(0, "/path/to/qgis-geosearch/tests/manual")
    import visual_run; visual_run.main(["--only", "adr-vangebovej-71"])

or from a shell (starts QGIS, runs, quits): make visual [QGIS=4] [ONLY=id1,id2]
All options: visual_run.main(["--help"])
"""

import argparse
import datetime
import html
import json
import os
import shlex
import sys
import time
import traceback
import unicodedata
from pathlib import Path

from qgis.PyQt.QtCore import QEvent, QEventLoop, Qt, QTimer
from qgis.PyQt.QtGui import QKeyEvent
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDockWidget,
    QLineEdit,
)
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsMessageLog,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
)
from qgis.gui import QgsRubberBand, QgsVertexMarker

PLUGIN_NAME = "geosearch_dk"
DOCK_OBJECT_NAME = "Geosearch DK"
LOG_TAG = "Geosearch visual run"

# Settings used to apply a case's `types` and `kommuner` (see PluginSettings)
TYPE_KEYS = ("adr", "ste", "pos", "mat", "kom", "ops", "pol", "reg")
TYPE_SETTING = "search_{}"
KOMMUNEFILTER_SETTING = "kommunefilter"
# Bool settings that switch the kommunefilter on (opt-in since Step 5, #11).
KOMMUNEFILTER_SWITCH_SETTINGS = ("kommunefilter_enabled",)

# Denmark in EPSG:25832, used to reset the map before each case
DK_EXTENT_25832 = (440000, 6040000, 900000, 6410000)
OSM_URL = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0"


# --------------------------------------------------------------------------
# Small helpers


def log(msg):
    print(f"[visual_run] {msg}", flush=True)
    QgsMessageLog.logMessage(str(msg), LOG_TAG, Qgis.MessageLevel.Info)


def _exec(obj):
    return (getattr(obj, "exec", None) or getattr(obj, "exec_"))()


def _int(enum_value):
    return int(getattr(enum_value, "value", enum_value))


def wait(ms):
    """Process events for ms milliseconds without blocking the GUI."""
    loop = QEventLoop()
    QTimer.singleShot(int(ms), loop.quit)
    _exec(loop)


def wait_until(predicate, timeout_ms, poll_ms=50):
    deadline = time.monotonic() + timeout_ms / 1000.0
    while True:
        try:
            if predicate():
                return True
        except RuntimeError:  # wrapped C++ object deleted
            pass
        if time.monotonic() >= deadline:
            return False
        wait(poll_ms)


def send_key(widget, key, text=""):
    for event_type in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
        event = QKeyEvent(
            event_type, _int(key), Qt.KeyboardModifier.NoModifier, text
        )
        QApplication.sendEvent(widget, event)


def type_text(widget, text, delay_ms):
    """Type text into a widget one key press at a time, like a user."""
    for ch in text:
        if ch == " ":
            key = Qt.Key.Key_Space
        elif ord(ch) < 128 and ch.isalnum():
            key = ord(ch.upper())
        else:
            key = Qt.Key.Key_unknown
        send_key(widget, key, ch)
        wait(delay_ms)


def norm(text):
    return " ".join(unicodedata.normalize("NFC", str(text)).casefold().split())


def find_match(rows, expected):
    """Return (index, kind) of the best match for the expected text."""
    if not expected:
        return None, None
    e = norm(expected)
    normed = [norm(r) for r in rows]
    for kind, test in (
        ("exact", lambda r: r == e),
        ("prefix", lambda r: r.startswith(e)),
        ("contains", lambda r: e in r),
    ):
        for i, r in enumerate(normed):
            if test(r):
                return i, kind
    return None, None


def close_whats_new():
    """Close the "Hvad er nyt" dialog if it is open, so it does not take focus."""
    try:
        import qgis.utils

        module = sys.modules[type(qgis.utils.plugins[PLUGIN_NAME]).__module__]
        package = module.__name__.rpartition(".")[0]
        sys.modules[package + ".whatsnew"].close_whats_new()
    except Exception:
        pass


def find_repo_root(explicit=None):
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if "__file__" in globals():
        candidates.append(Path(__file__).resolve().parents[2])
    try:
        import qgis.utils

        module = sys.modules[type(qgis.utils.plugins[PLUGIN_NAME]).__module__]
        candidates.append(Path(module.__file__).resolve().parents[2])
    except Exception:
        pass
    candidates.append(Path.cwd())
    for c in candidates:
        if (c / "src" / PLUGIN_NAME).is_dir():
            return c.resolve()
    return candidates[0].resolve()


def load_cases(path):
    import yaml  # bundled with QGIS

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict):
        data = data.get("cases", [])
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list of cases")
    for c in data:
        if not isinstance(c, dict) or "id" not in c or "input" not in c:
            raise ValueError(f"{path}: every case needs 'id' and 'input': {c!r}")
    return data


# --------------------------------------------------------------------------
# UI access (widgets only, no plugin internals)


class PluginUI:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        mw = iface.mainWindow()
        dock = mw.findChild(QDockWidget, DOCK_OBJECT_NAME)
        if dock is None:
            for d in mw.findChildren(QDockWidget):
                if "geosearch" in d.windowTitle().lower():
                    dock = d
                    break
        if dock is None:
            raise RuntimeError(
                "Geosearch DK dock not found. Is the plugin enabled in this profile?"
            )
        self.dock = dock
        edit = dock.findChild(QLineEdit, "searchEdit")
        if edit is None:
            edits = dock.findChildren(QLineEdit)
            if not edits:
                raise RuntimeError("No search box found in the Geosearch DK dock")
            edit = edits[0]
        self.edit = edit

    @staticmethod
    def popup():
        """The visible popup item view (QTreeWidget, QCompleter popup, ...)."""
        for w in QApplication.topLevelWidgets():
            if (
                isinstance(w, QAbstractItemView)
                and w.isVisible()
                and w.windowType() == Qt.WindowType.Popup
            ):
                return w
        return None

    @staticmethod
    def popup_rows(popup):
        model = popup.model()
        root = popup.rootIndex()
        rows = []
        for r in range(model.rowCount(root)):
            value = model.index(r, 0, root).data()
            rows.append("" if value is None else str(value))
        return rows

    def close_popup(self):
        p = self.popup()
        if p is not None:
            send_key(p, Qt.Key.Key_Escape)
            wait(50)
            if p.isVisible():
                p.hide()

    def clear_search(self):
        self.close_popup()
        self.dock.show()
        self.edit.setFocus()
        if self.edit.text():
            self.edit.selectAll()
            send_key(self.edit, Qt.Key.Key_Backspace)
        wait(50)

    def markers(self):
        """Kinds of point markers and rubber bands on the map canvas."""
        found = []
        for item in self.canvas.scene().items():
            if not item.isVisible():
                continue
            if isinstance(item, QgsVertexMarker):
                found.append("point")
            elif isinstance(item, QgsRubberBand):
                try:
                    is_polygon = (
                        item.asGeometry().type() == Qgis.GeometryType.Polygon
                    )
                except Exception:
                    is_polygon = False
                found.append("polygon" if is_polygon else "line")
        return found


# --------------------------------------------------------------------------
# Per-case settings (types and kommuner), restored afterwards


class PluginSettings:
    def __init__(self, enabled=True):
        self.settings = None
        self.saved = {}
        if not enabled:
            return
        try:
            import qgis.utils

            plugin = qgis.utils.plugins[PLUGIN_NAME]
            self.settings = getattr(plugin, "settings", None)
        except Exception:
            self.settings = None

    def _exists(self, name):
        try:
            self.settings.value(name)
            return True
        except Exception:
            return False

    def _set(self, name, value):
        if name not in self.saved:
            self.saved[name] = self.settings.value(name)
        self.settings.set_value(name, value)

    def apply(self, case):
        """Apply the case's types/kommuner. Returns a short description."""
        if self.settings is None:
            return "not applied (plugin settings not available)"
        notes = []
        types = case.get("types") or []
        type_names = [TYPE_SETTING.format(k) for k in TYPE_KEYS]
        if all(self._exists(n) for n in type_names):
            for key, name in zip(TYPE_KEYS, type_names):
                self._set(name, (not types) or key in types)
            notes.append("types: " + (", ".join(types) if types else "all"))
        elif types:
            notes.append("types not applied (unknown settings)")
        kommuner = [str(k) for k in (case.get("kommuner") or [])]
        if self._exists(KOMMUNEFILTER_SETTING):
            self._set(KOMMUNEFILTER_SETTING, ",".join(kommuner))
            for switch in KOMMUNEFILTER_SWITCH_SETTINGS:
                if self._exists(switch):
                    self._set(switch, bool(kommuner))
            if kommuner:
                notes.append("kommuner: " + ", ".join(kommuner))
        elif kommuner:
            notes.append("kommuner not applied (unknown settings)")
        return "; ".join(notes)

    def restore(self):
        for name, value in self.saved.items():
            try:
                self.settings.set_value(name, value)
            except Exception as e:
                log(f"Could not restore setting {name}: {e}")
        if self.saved:
            log(f"Restored {len(self.saved)} plugin settings")
        self.saved = {}


# --------------------------------------------------------------------------
# The run


class VisualRun:
    def __init__(self, iface, args):
        self.iface = iface
        self.args = args
        self.ui = PluginUI(iface)
        self.canvas = self.ui.canvas
        self.out = Path(args.out)
        self.img = self.out / "img"
        self.img.mkdir(parents=True, exist_ok=True)
        self.settings = PluginSettings(enabled=not args.no_filters)
        self.renders = 0
        self.canvas.mapCanvasRefreshed.connect(self._on_refreshed)
        self.basemap_id = None
        self.project_state = None

    def _on_refreshed(self):
        self.renders += 1

    # -- map ---------------------------------------------------------------

    def setup_map(self):
        project = QgsProject.instance()
        self.project_state = (project.crs(), self.canvas.extent(), project.isDirty())
        want = self.args.basemap
        if want == "osm" or (want == "auto" and not project.mapLayers()):
            empty = not project.mapLayers()
            layer = QgsRasterLayer(OSM_URL, "OpenStreetMap (visual run)", "wms")
            if layer.isValid():
                project.addMapLayer(layer)
                self.basemap_id = layer.id()
                if empty:
                    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25832"))
                log("Added a temporary OpenStreetMap basemap")
            else:
                log("Could not add the OpenStreetMap basemap")

    def restore_map(self):
        if self.project_state is None:
            return
        crs, extent, dirty = self.project_state
        project = QgsProject.instance()
        if self.basemap_id:
            project.removeMapLayer(self.basemap_id)
            self.basemap_id = None
        project.setCrs(crs)
        self.canvas.setExtent(extent)
        self.canvas.refresh()
        project.setDirty(dirty)

    def wait_for_render(self, since, timeout_ms):
        ok = wait_until(
            lambda: self.renders > since and not self.canvas.isDrawing(),
            timeout_ms,
        )
        wait(self.args.settle)
        return ok

    def reset_map(self):
        src = QgsCoordinateReferenceSystem("EPSG:25832")
        dst = self.canvas.mapSettings().destinationCrs()
        rect = QgsRectangle(*DK_EXTENT_25832)
        if dst != src:
            rect = QgsCoordinateTransform(
                src, dst, QgsProject.instance()
            ).transformBoundingBox(rect)
        since = self.renders
        self.canvas.setExtent(rect)
        self.canvas.refresh()
        self.wait_for_render(since, self.args.render_timeout)

    # -- one case ------------------------------------------------------------

    def run_case(self, case):
        cid = str(case["id"])
        expect = case.get("expect") or {}
        within = int(expect.get("within") or 1)
        res = {
            "id": cid,
            "story": case.get("story", ""),
            "input": str(case["input"]),
            "types": case.get("types") or [],
            "kommuner": case.get("kommuner") or [],
            "expect": expect,
            "known_gap": case.get("known_gap"),
            "notes": case.get("notes", ""),
            "rows": [],
            "match_index": None,
            "match_kind": None,
            "markers": [],
            "problems": [],
            "popup_img": None,
            "map_img": None,
            "timings": {},
        }
        log(f"--- {cid}: typing {res['input']!r}")
        try:
            res["filters"] = self.settings.apply(case)
            self.ui.clear_search()
            self.reset_map()
            extent_before = self.canvas.extent()

            # Type, then wait for the popup to appear and settle
            type_text(self.ui.edit, res["input"], self.args.type_delay)
            t0 = time.monotonic()
            if not wait_until(
                lambda: self.ui.popup() is not None, self.args.popup_timeout
            ):
                res["problems"].append("no popup")
            else:
                self._wait_popup_stable()
            res["timings"]["popup_s"] = round(time.monotonic() - t0, 2)

            popup = self.ui.popup()
            if popup is not None:
                res["rows"] = self.ui.popup_rows(popup)
            idx, kind = find_match(res["rows"], expect.get("text"))
            res["match_index"], res["match_kind"] = idx, kind
            if expect.get("text") and idx is None:
                res["problems"].append("expected hit not in popup")
            elif idx is not None and idx >= within:
                res["problems"].append(
                    f"expected hit at #{idx + 1}, wanted top {within}"
                )

            if popup is not None and idx is not None:
                self._move_to(popup, idx)
            if popup is not None:
                res["popup_img"] = self._save(popup.grab(), f"{cid}-popup.png")

            if popup is not None and idx is not None:
                # Select with Enter and wait for geometry and map
                since = self.renders
                t1 = time.monotonic()
                send_key(popup, Qt.Key.Key_Return)
                got_marker = wait_until(
                    lambda: bool(self.ui.markers()), self.args.geometry_timeout
                )
                moved = wait_until(
                    lambda: self.canvas.extent() != extent_before, 1000
                )
                self.wait_for_render(since, self.args.render_timeout)
                res["timings"]["map_s"] = round(time.monotonic() - t1, 2)
                res["markers"] = self.ui.markers()
                if not got_marker:
                    res["problems"].append("no geometry drawn on the map")
                if not moved:
                    res["problems"].append("map did not move")
                self._check_geometry(expect.get("geometry"), res)
                res["map_img"] = self._save(self.canvas.grab(), f"{cid}-map.png")
            else:
                self.ui.close_popup()
        except Exception as e:
            res["problems"].append(f"error: {e}")
            res["error"] = traceback.format_exc()
            log(res["error"])
            self.ui.close_popup()

        res["status"] = self._status(res)
        log(f"{cid}: {res['status']} {'; '.join(res['problems'])}")
        return res

    def _wait_popup_stable(self):
        """Wait until the popup's rows have not changed for --stable ms."""
        last, since = None, time.monotonic()
        deadline = time.monotonic() + self.args.popup_timeout / 1000.0
        while time.monotonic() < deadline:
            p = self.ui.popup()
            rows = self.ui.popup_rows(p) if p is not None else None
            if rows != last:
                last, since = rows, time.monotonic()
            elif (time.monotonic() - since) * 1000 >= self.args.stable:
                return
            wait(50)

    def _move_to(self, popup, target):
        """Move to the target row with the arrow keys, as a user would."""
        for _ in range(len(self.ui.popup_rows(popup)) + 2):
            cur = popup.currentIndex().row()
            if cur == target:
                break
            send_key(popup, Qt.Key.Key_Down if cur < target else Qt.Key.Key_Up)
            wait(30)
        if popup.currentIndex().row() != target:
            popup.setCurrentIndex(popup.model().index(target, 0, popup.rootIndex()))
        wait(100)

    @staticmethod
    def _check_geometry(expected, res):
        if not expected or not res["markers"]:
            return
        expected = str(expected).lower()
        drawn = set(res["markers"])
        if "point" in expected:
            ok = "point" in drawn
        else:
            # The GSearch version draws polygons as outlines (line rubber bands)
            ok = bool(drawn & {"line", "polygon"})
        if not ok:
            res["problems"].append(
                f"expected {expected}, map shows {', '.join(sorted(drawn))}"
            )

    def _save(self, pixmap, name):
        pixmap.save(str(self.img / name), "PNG")
        return f"img/{name}"

    @staticmethod
    def _status(res):
        if res.get("error"):
            return "ERROR"
        if res["problems"]:
            return "KNOWN GAP" if res.get("known_gap") else "FAIL"
        # A known gap that passes: expected for GSearch, a fix for Bifrost
        return "PASS (KNOWN GAP)" if res.get("known_gap") else "PASS"

    # -- whole run -------------------------------------------------------------

    def run(self, cases):
        results = []
        started = datetime.datetime.now()
        close_whats_new()
        self.setup_map()
        try:
            for case in cases:
                results.append(self.run_case(case))
        finally:
            self.settings.restore()
            self.ui.clear_search()
            self.restore_map()
            try:
                self.canvas.mapCanvasRefreshed.disconnect(self._on_refreshed)
            except Exception:
                pass
        report = write_report(self.out, results, self.args, started)
        return results, report


# --------------------------------------------------------------------------
# Report

STATUS_CLASS = {
    "PASS": "pass",
    "FAIL": "fail",
    "ERROR": "fail",
    "KNOWN GAP": "gap",
    "PASS (KNOWN GAP)": "upass",
}
ISSUE_URL = "https://github.com/AsgerPetersen/qgis-geosearch/issues/{}"

CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:24px;color:#222}
h1{margin:0 0 4px}.meta{color:#666;font-size:13px;margin-bottom:16px}
table.sum{border-collapse:collapse;margin-bottom:24px;font-size:14px}
table.sum td,table.sum th{border-bottom:1px solid #ddd;padding:4px 10px;text-align:left}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600;color:#fff}
.pass{background:#2e7d32}.fail{background:#c62828}.gap{background:#ef6c00}.upass{background:#6a1b9a}
section.case{border:1px solid #ddd;border-radius:6px;padding:12px 16px;margin-bottom:20px}
section.case h2{font-size:18px;margin:0 0 6px}
.story{font-style:italic;color:#444}.facts{font-size:13px;color:#444;margin:6px 0}
code{background:#f3f3f3;padding:1px 4px;border-radius:3px}
.grid{display:grid;grid-template-columns:1fr 1.6fr;gap:16px;margin-top:10px}
.grid h3{font-size:13px;text-transform:uppercase;color:#777;margin:0 0 6px}
ol.rows{margin:6px 0 0;padding-left:26px;font-size:13px}
ol.rows li.hit{background:#fff59d;font-weight:600}ol.rows li.cut{border-top:2px dashed #999}
img{max-width:100%;border:1px solid #ccc}.problems{color:#c62828;font-size:13px}
pre{font-size:11px;background:#f7f7f7;padding:6px;overflow:auto;max-height:300px}
.muted{color:#999;font-size:13px}
"""


def _esc(v):
    return html.escape("" if v is None else str(v))


def _rows_html(rows, hit, within, limit=25):
    """Ordered list of rows; the hit is highlighted, a line marks top N."""
    if not rows:
        return '<p class="muted">(no rows)</p>'
    items = []
    for i, r in enumerate(rows[:limit]):
        cls = []
        if i == hit:
            cls.append("hit")
        if i == within:
            cls.append("cut")
        items.append(f'<li class="{" ".join(cls)}">{_esc(r)}</li>')
    more = (
        f'<p class="muted">… {len(rows) - limit} more</p>' if len(rows) > limit else ""
    )
    return f'<ol class="rows">{"".join(items)}</ol>{more}'


def _rank(index):
    return "–" if index is None else f"#{index + 1}"


def _case_html(r):
    expect = r["expect"] or {}
    within = int(expect.get("within") or 1)
    badge = f'<span class="badge {STATUS_CLASS.get(r["status"], "fail")}">{_esc(r["status"])}</span>'
    gap = (
        f' <a href="{ISSUE_URL.format(_esc(r["known_gap"]))}">#{_esc(r["known_gap"])}</a>'
        if r.get("known_gap")
        else ""
    )
    popup_html = f'<img src="{_esc(r["popup_img"])}" alt="popup">' if r["popup_img"] else ""
    popup_html += _rows_html(r["rows"], r["match_index"], within)
    map_html = (
        f'<img src="{_esc(r["map_img"])}" alt="map">'
        if r["map_img"]
        else '<p class="muted">(nothing selected)</p>'
    )

    facts = [
        f"typed <code>{_esc(r['input'])}</code>",
        f"types: {_esc(', '.join(map(str, r['types'])) or 'all')}",
    ]
    if r["kommuner"]:
        facts.append(f"kommuner: {_esc(', '.join(map(str, r['kommuner'])))}")
    geometry = f", geometry {_esc(expect['geometry'])}" if expect.get("geometry") else ""
    facts.append(f"expect <code>{_esc(expect.get('text'))}</code> in top {within}{geometry}")
    if r["match_kind"]:
        facts.append(f"matched ({_esc(r['match_kind'])}) at {_rank(r['match_index'])}")
    if r["markers"]:
        facts.append(f"map shows: {_esc(', '.join(sorted(set(r['markers']))))}")
    if r.get("filters"):
        facts.append(f"settings: {_esc(r['filters'])}")
    if r.get("timings"):
        facts.append(
            "timings: " + ", ".join(f"{_esc(k)} {_esc(v)}s" for k, v in r["timings"].items())
        )
    notes = f'<div class="facts">Notes: {_esc(r["notes"])}</div>' if r.get("notes") else ""
    err = f"<pre>{_esc(r['error'])}</pre>" if r.get("error") else ""
    section = f"""<section class="case" id="{_esc(r['id'])}">
<h2>{badge} {_esc(r['id'])}{gap}</h2>
<div class="story">{_esc(r['story'])}</div>
<div class="facts">{' · '.join(facts)}</div>{notes}
<div class="problems">{_esc('; '.join(r['problems']))}</div>{err}
<div class="grid">
<div><h3>Popup now</h3>{popup_html}</div>
<div><h3>Map now</h3>{map_html}</div>
</div></section>"""
    summary = (
        f'<tr><td><a href="#{_esc(r["id"])}">{_esc(r["id"])}</a></td>'
        f'<td><code>{_esc(r["input"])}</code></td><td>{badge}{gap}</td>'
        f'<td>{_rank(r["match_index"])}</td>'
        f'<td class="problems">{_esc("; ".join(r["problems"]))}</td></tr>'
    )
    return summary, section


def write_report(out, results, args, started):
    out = Path(out)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    try:
        import qgis.utils

        plugin_version = qgis.utils.pluginMetadata(PLUGIN_NAME, "version")
    except Exception:
        plugin_version = "?"
    meta = {
        "started": started.isoformat(timespec="seconds"),
        "qgis": Qgis.version(),
        "plugin_version": plugin_version,
        "cases_file": str(args.cases),
        "counts": counts,
    }
    (out / "report.json").write_text(
        json.dumps({"meta": meta, "results": results}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    parts = [_case_html(r) for r in results]
    count_html = " · ".join(
        f'<span class="badge {STATUS_CLASS.get(k, "fail")}">{_esc(k)}</span> {v}'
        for k, v in sorted(counts.items())
    )
    doc = f"""<!doctype html><html lang="da"><head><meta charset="utf-8">
<title>Geosearch DK visual run</title><style>{CSS}</style></head><body>
<h1>Geosearch DK visual run</h1>
<div class="meta">{_esc(meta['started'])} · QGIS {_esc(meta['qgis'])} · plugin {_esc(plugin_version)} · {_esc(meta['cases_file'])}</div>
<p>{count_html}</p>
<table class="sum"><tr><th>Case</th><th>Input</th><th>Status</th><th>Rank now</th><th>Problems</th></tr>
{''.join(s for s, _ in parts)}</table>
{''.join(c for _, c in parts)}
</body></html>"""
    path = out / "report.html"
    path.write_text(doc, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Entry points


def parse_args(argv, repo):
    default_cases = repo / "tests" / "cases.yaml"
    if not default_cases.exists():
        default_cases = repo / "tests" / "manual" / "sample_cases.yaml"
    p = argparse.ArgumentParser(
        prog="visual_run", description="Visual run for Geosearch DK."
    )
    p.add_argument("--cases", default=str(default_cases), help="case catalogue (YAML)")
    p.add_argument("--out", default=str(repo / "out"), help="output directory")
    p.add_argument("--only", default="", help="comma separated case ids")
    p.add_argument(
        "--basemap",
        choices=("auto", "osm", "none"),
        default="auto",
        help="auto: add a temporary OSM layer if the project is empty",
    )
    p.add_argument(
        "--no-filters",
        action="store_true",
        help="do not apply the cases' types/kommuner to the plugin settings",
    )
    p.add_argument("--type-delay", type=int, default=40, help="ms between key presses")
    p.add_argument("--popup-timeout", type=int, default=15000, help="ms")
    p.add_argument("--stable", type=int, default=800, help="ms the popup must stay unchanged")
    p.add_argument("--geometry-timeout", type=int, default=15000, help="ms")
    p.add_argument("--render-timeout", type=int, default=20000, help="ms")
    p.add_argument("--settle", type=int, default=600, help="ms to wait after rendering")
    p.add_argument("--quit", action="store_true", help="quit QGIS when done")
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        if e.code:
            raise ValueError("invalid arguments, see visual_run.main(['--help'])")
        return None  # --help
    for name in ("cases", "out"):
        path = Path(getattr(args, name))
        setattr(args, name, path if path.is_absolute() else repo / path)
    return args


def _quit_qgis(iface):
    QgsProject.instance().setDirty(False)
    QTimer.singleShot(500, iface.actionExit().trigger)


def main(argv=None, iface=None):
    """Run the visual run. argv defaults to $VISUAL_RUN_ARGS. Returns the report path."""
    if iface is None:
        from qgis.utils import iface
    repo = find_repo_root(os.environ.get("GEOSEARCH_REPO"))
    if argv is None:
        argv = shlex.split(os.environ.get("VISUAL_RUN_ARGS", ""))
    args = parse_args(argv, repo)
    if args is None:
        return None
    try:
        cases = load_cases(args.cases)
        if args.only:
            wanted = {s.strip() for s in args.only.split(",") if s.strip()}
            cases = [c for c in cases if str(c["id"]) in wanted]
        log(f"{len(cases)} cases from {args.cases}")
        _, report = VisualRun(iface, args).run(cases)
        log(f"Report written to {report}")
        iface.messageBar().pushMessage(
            LOG_TAG, f"Report: {report}", Qgis.MessageLevel.Success, 15
        )
        return report
    finally:
        if args.quit:
            _quit_qgis(iface)


def _main_deferred():
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        if "--quit" in os.environ.get("VISUAL_RUN_ARGS", ""):
            from qgis.utils import iface

            _quit_qgis(iface)


if __name__ in ("__main__", "__console__"):
    if "__file__" not in globals() and "VISUAL_RUN_ARGS" in os.environ:
        # Started by `qgis --code` (make visual): start once QGIS is up
        QTimer.singleShot(3000, _main_deferred)
    else:
        main()
