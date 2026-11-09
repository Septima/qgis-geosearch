# Development

This page describes how to run the plugin from this checkout inside QGIS 3
(Qt5) or QGIS 4 (Qt6). The plugin supports both.

The plugin is run in a **separate QGIS profile**, `geosearch-dev`. A released
Geosearch DK installed in your `default` profile is not touched.

## macOS: `make dev`

```sh
make dev            # QGIS 4 (default)
make dev QGIS=3     # QGIS 3
```

`make dev`:

1. creates the profile `geosearch-dev` if it does not exist
   (`~/Library/Application Support/QGIS/QGIS<n>/profiles/geosearch-dev`),
   and enables the plugin in a new profile;
2. symlinks `src/geosearch_dk` into the profile's `python/plugins/` folder;
3. starts QGIS with `open -n -a <QGIS.app> --args --profile geosearch-dev`.

QGIS remembers `--profile` as the last used profile. `make` restores the
previous value when QGIS quits, so starting QGIS normally still opens your
`default` profile.

`make help` lists all targets and prints the current values of the variables.

| Variable   | Default | Meaning |
|------------|---------|---------|
| `QGIS`     | `4`     | QGIS major version, `3` or `4` |
| `QGIS_APP` | newest `QGIS*.app` in `/Applications` or `~/Applications` with version `$(QGIS).x` | the QGIS app to start |
| `PROFILE`  | `geosearch-dev` | QGIS profile name |

Other targets:

- `make dev-link`: only create the profile and the symlink (does not start QGIS)
- `make dev-unlink`: remove the symlink (the profile is kept)
- `make visual`: run the visual run, see below

To remove the dev profile completely, delete its folder.

The plugin defaults to Bifrost production, `https://bifrost.dataforsyningen.dk`,
which is not live yet. A test key works only on the test server: set
*Bifrost URL* in the plugin settings to `https://bifrost.test42.dataforsyningen.dk`.
The live tests and the recording tools use the test server unless `BIFROST_URL`
is set.

## Linux

`make dev` works on Linux as well. The profile is created in
`~/.local/share/QGIS/QGIS<n>/profiles/geosearch-dev`, and QGIS is started with
`qgis --profile geosearch-dev`. If QGIS 3 and 4 are installed side by side, give
the binary explicitly:

```sh
make dev QGIS=3 QGIS_BIN=/usr/bin/qgis
make dev QGIS=4 QGIS_BIN=/opt/qgis4/bin/qgis
```

By hand:

```sh
P=~/.local/share/QGIS/QGIS4/profiles/geosearch-dev/python/plugins   # QGIS3 for QGIS 3
mkdir -p "$P"
ln -sfn "$PWD/src/geosearch_dk" "$P/geosearch_dk"
qgis --profile geosearch-dev
```

Enable *Geosearch DK* under *Plugins > Manage and Install Plugins > Installed*
the first time.

## Windows

There is no `make dev` for Windows. Do the same steps by hand in `cmd.exe`
(replace `QGIS4` with `QGIS3` for QGIS 3):

```bat
set P=%APPDATA%\QGIS\QGIS4\profiles\geosearch-dev\python\plugins
mkdir "%P%"
mklink /J "%P%\geosearch_dk" "C:\path\to\qgis-geosearch\src\geosearch_dk"
```

`mklink /J` creates a directory junction, which does not need an administrator
shell. (`mklink /D` creates a real symlink, but needs an administrator shell or
Developer Mode.)

Start QGIS with the profile. Use the command of the QGIS Start menu shortcut
(right-click > *More* > *Open file location*, then *Properties > Target*) and
add `--profile geosearch-dev`, for example:

```bat
"C:\Program Files\QGIS 3.44.8\bin\qgis-ltr-bin.exe" --profile geosearch-dev
"C:\OSGeo4W\bin\qgis.bat" --profile geosearch-dev
```

A copy of the shortcut with `--profile geosearch-dev` added to *Target* is
handy.

Enable *Geosearch DK* under *Plugins > Manage and Install Plugins > Installed*
the first time. To remove the link, run `rmdir "%P%\geosearch_dk"`; this
removes only the junction, not the source files.

## Fast reloads with Plugin Reloader

Because the profile uses a symlink, QGIS runs the code in the checkout
directly. Instead of restarting QGIS after each change, use the
[Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin:

1. In the `geosearch-dev` profile, install *Plugin Reloader* from
   *Plugins > Manage and Install Plugins*.
2. Open the menu of the Plugin Reloader toolbar button, choose *Configure*,
   and select `geosearch_dk`.
3. After a change, press **Ctrl+F5** (macOS: **Cmd+F5**) or click the toolbar
   button. The plugin is unloaded and loaded again from the checkout.

Restart QGIS when reloading is not enough, for example after changing
`metadata.txt`.

## README screenshots

`make screenshots` (QGIS=4 or 3) retakes the README's screenshots in
`docs/images/`: the search panel (`soegepanel.png`) and the plugin's page in the
QGIS options (`indstillinger.png`). It starts QGIS with its own profile,
`geosearch-screenshots`, which is recreated every run with Danish locale
(`da_DK`) and no Bifrost key, takes the images with
`tests/manual/readme_screenshots.py` and quits. The README is in Danish, so the
screenshots are always Danish. Retake them whenever the settings page or the
search panel changes noticeably, and check the images before committing.

## Visual run

`tests/manual/visual_run.py` drives the real plugin UI. For each case in the
case catalogue (`tests/cases.yaml`, see below) it:

1. types the input into the plugin's search box, key by key;
2. waits for the result popup and saves a screenshot of it;
3. moves to the expected hit with the arrow keys and presses Enter;
4. waits for the marker or outline on the map and saves an image of the map.

It only uses widgets (the dock *Geosearch DK*, its search field and the
popup), not plugin internals.

The result is `out/report.html`: a table with the status of every case, and
per case the popup and the map. Open it in a browser.
`out/report.json` has the same data.

### From a shell

```sh
make visual                      # QGIS 4, all cases
make visual QGIS=3               # QGIS 3
make visual ONLY=adr-vangebovej-71,kom-koege
make visual CASES=tests/manual/sample_cases.yaml OUT=out/sample
```

`make visual` starts QGIS with the `geosearch-dev` profile, runs the script,
quits QGIS and prints the result of each case. The QGIS log is in
`out/qgis.log`. Do not use the mouse or keyboard while it runs: the script
sends key presses to the search box.

Use `VISUAL_ARGS` for other options, e.g.
`make visual VISUAL_ARGS="--basemap none --no-filters"`.

### From the QGIS Python console

Start QGIS with `make dev`, open *Plugins > Python Console*, and run:

```python
import runpy; runpy.run_path("/path/to/qgis-geosearch/tests/manual/visual_run.py", run_name="__main__")
```

With options:

```python
import sys; sys.path.insert(0, "/path/to/qgis-geosearch/tests/manual")
import visual_run
visual_run.main(["--only", "adr-vangebovej-71", "--out", "/tmp/geosearch-out"])
visual_run.main(["--help"])     # all options
```

### Options

| Option | Default | Meaning |
|--------|---------|---------|
| `--cases` | `tests/cases.yaml`, or `tests/manual/sample_cases.yaml` if it does not exist | case catalogue |
| `--out` | `out` | output folder |
| `--only` | | comma separated case ids |
| `--basemap` | `auto` | `auto` adds a temporary OpenStreetMap layer when the project has no layers; `osm` always; `none` never |
| `--no-filters` | | do not apply the case's `types` and `kommuner` to the plugin settings |
| `--quit` | | quit QGIS when done (used by `make visual`) |

There are also timeouts (`--popup-timeout`, `--geometry-timeout`,
`--render-timeout`, ...). See `--help`.

### Cases and results

The case catalogue is a YAML list:

```yaml
- id: adr-vangebovej-71
  story: "Brugeren vil finde Vangebovej 71 ..."
  input: "Vangebovej 71"         # exactly what is typed
  types: [adr]                   # adr ste pos mat kom ops pol reg; omit = all
  kommuner: []                   # optional kommunefilter codes
  expect: { text: "...", within: 3, geometry: point }
  known_gap: 3                   # optional issue number in AsgerPetersen/qgis-geosearch
  notes: ""
```

`tests/manual/sample_cases.yaml` is a small example.

Unless `--no-filters` is given, the case's `types` and `kommuner` are written
to the plugin settings before the case. Your settings are restored when the
run ends, also when it fails. The project's CRS and extent are restored too.

Status per case:

- **PASS**: `expect.text` is among the first `within` hits, and selecting it
  showed a geometry of the expected kind on the map.
- **FAIL**: the hit was not found, or no geometry (or the wrong kind) was shown.
- **ERROR**: the script failed, e.g. the popup did not appear.
- **KNOWN GAP**: the case failed, but has `known_gap` (an open issue).
- **PASS (KNOWN GAP)**: the case passed although it has `known_gap`. The issue
  may be fixed.

## Automated tests

| Command | What | Needs |
| --- | --- | --- |
| `make test` | Unit tests: the Bifrost core, the mock Bifrost, and every case in `tests/cases.yaml` replayed from its recorded fixture | [uv](https://docs.astral.sh/uv/) |
| `make test-qgis` | `tests/qgis` in a real QGIS 4 in Docker (pytest-qgis): plugin load/unload, settings, options page, map markers, the Bifrost fetcher against the mock. `QGIS=3` uses QGIS 3.44 LTR, `make test-qgis-all` runs both | Docker |
| `make test-live` | Every case against the real Bifrost; writes a report to `out/bifrost-live-report.md` | `BIFROST_KEY` |
| `make mock` | A mock Bifrost on `http://127.0.0.1:8766` that answers from the recorded fixtures | Python 3 |

Pass pytest options with `PYTEST_ARGS`, e.g. `make test-qgis QGIS=3 PYTEST_ARGS="-k marker -x"`.
The QGIS images are linux/amd64 only and run emulated on Apple silicon.

In the live suite, a `known_gap` case is an expected failure (xfail) and an
XPASS means Bifrost now does what the issue says it cannot. Stednavne are
matched on the name before " (" because Bifrost has no subtype (#1). The
`expect` of a case was written from what GSearch showed; a `bifrost:` override
in `cases.yaml` gives Bifrost a different expectation. The GSearch recordings
and the comparison of the two services are in the fork
[AsgerPetersen/qgis-geosearch](https://github.com/AsgerPetersen/qgis-geosearch).

### Translations

The plugin's texts are Danish. QGIS in English (any `en*` locale, e.g.
`en_DK`) gets English everywhere; every other locale gets Danish
(`src/geosearch_dk/language.py`). The English texts are in
`src/geosearch_dk/i18n/en.qt.ts` and `help/hvad_er_nyt.en.html`. After adding
or changing a text, a `self.tr(...)` in a Qt class, a `<string>` in a `.ui`
file, or a `tr("bifrost"|"kommunefilter", ...)` in the pure modules
(`bifrost/translation.py`):

```sh
python3 scripts/update_ts.py      # adds new texts as unfinished, drops unused ones
# fill in the English <translation> of each unfinished text in en.qt.ts
/opt/homebrew/bin/lrelease -silent src/geosearch_dk/i18n/en.qt.ts -qm src/geosearch_dk/i18n/en.qt.qm
```

`make test` fails while a text has no English translation, a source text looks
English, or the two "Hvad er nyt" files have different anchors or links.
`make test-qgis` checks that the `.qm` matches the `.ts`. Use `lrelease` from
Qt 5 or 6 (`brew install qt`).

### Mock Bifrost

Point the plugin's Bifrost URL at `http://127.0.0.1:8766`; any key is accepted.
The mock answers from `tests/fixtures/bifrost/` (see the docstring in
`tests/mock_bifrost.py` for how requests are matched). To see the plugin's
error handling:

- type `mock-401`, `mock-422`, `mock-503` or `mock-slow` into the search box;
- or make every request fail: `make mock MOCK_ARGS="--error 503"`, or
  `curl -X POST localhost:8766/_mock/config -d '{"error": "503"}'`
  (`{"error": null}` turns it off, `"error_count": 2` fails only the next two).

`GET /_mock/requests` lists the requests the mock got.

### Recording fixtures

`make record-bifrost` (needs `BIFROST_KEY`, `ONLY=id1,id2` for some cases)
records every case to `tests/fixtures/bifrost/cases/<id>.json` and rewrites
`tests/fixtures/bifrost/cases/REPORT.md`. Re-record when a case is added or the
core sends different requests (`make test` tells you which). The unit test
fixtures are recorded with `uv run python tests/tools/record_bifrost.py`. The
recorder refuses to write a fixture that contains the key.

### CI

`.github/workflows/tests.yml` runs the unit tests, the QGIS tests (QGIS 3.44
and 4) and `make publish-check` on pushes and pull requests to `master` and `bifrost`, and the live
suite nightly (from `master`) or by hand (*Run workflow*). The live job needs
the repository secret `BIFROST_KEY`; without it, it is skipped.

## Publishing

```sh
make package          # dist/geosearch_dk.zip
make publish-check    # make package, then scripts/publish_check.py
```

`make package` zips the committed `src/geosearch_dk` at `HEAD` with
`git archive`, so the zip has a single folder `geosearch_dk/` and only
committed files. It fails if `src/` has uncommitted or untracked changes.
Files that are in the repository but not needed by the plugin (the old Plugin
Builder `Makefile`, the Sphinx `help/source`, `scripts/`, the tests of the
vendored qgissettingmanager) are marked `export-ignore` in
`src/.gitattributes`.

plugins.qgis.org scans every uploaded version with bandit, detect-secrets and
flake8. A critical bandit or detect-secrets finding blocks the
version, and scanning it again does not help: the only fix is to upload a new
version. `make publish-check` runs the same tools on the unpacked zip (with
`uvx`, so it needs [uv](https://docs.astral.sh/uv/)) and fails on:

- any bandit or detect-secrets finding, or a flake8 error from the critical
  rules (E901, E902, E999, F821, F823, F831); the other flake8 findings are
  only counted;
- a zip over 25 MB, more than one top-level folder, hidden files, `__pycache__`,
  executable files, scripts or unexpected binaries (only images and the `.qm`
  are allowed), generated `ui_*.py`/`*_rc.py`;
- a scanner config file (`.bandit`, `.secrets.baseline`, `.flake8`, ...). The
  site honours them, but the version then gets the status *Validated
  (configured)*. We ship none;
- `metadata.txt` without `homepage`, `tracker`, `repository` (https), version,
  or with a changelog whose first line does not mention the version.

Before uploading a release:

1. bump `version` in `metadata.txt` and add a changelog line for it at the top;
2. commit, then run `make publish-check` and fix every error;
3. upload `dist/geosearch_dk.zip` at plugins.qgis.org.
