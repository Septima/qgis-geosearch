"""Check the plugin zip before it is uploaded to plugins.qgis.org.

    python3 scripts/publish_check.py [dist/geosearch_dk.zip]

(``make publish-check`` builds the zip and runs this.)

plugins.qgis.org scans every uploaded version with bandit, detect-secrets and
flake8. A critical bandit or detect-secrets finding blocks the version, and a
blocked version can only be replaced by uploading a new version. This script
runs the same three tools (through ``uvx``) on the unpacked zip, without any
configuration file, and checks the zip's structure and metadata.txt.

Errors make the script exit with 1. Warnings are printed only.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

PLUGIN = "geosearch_dk"
MAX_SIZE = 25 * 1024 * 1024
# flake8 rules plugins.qgis.org treats as critical (syntax errors, undefined names)
FLAKE8_CRITICAL = "E901,E902,E999,F821,F823,F831"
# Binary files the plugin needs: icons and the compiled translation
BINARY_OK = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".qm"}
SUSPICIOUS = {".exe", ".dll", ".so", ".dylib", ".pyd", ".pyc", ".pyo", ".bat",
              ".cmd", ".sh", ".ps1", ".jar", ".zip", ".whl", ".egg"}
# Config files the scanners honour; shipping one gives the status
# "Validated (configured)" instead of a plain pass.
SCANNER_CONFIG = {".bandit", ".secrets.baseline", ".flake8", "setup.cfg", "tox.ini"}
REQUIRED_KEYS = ("name", "qgisMinimumVersion", "description", "about", "version",
                 "author", "email", "repository", "homepage", "tracker")
LINK_KEYS = ("repository", "homepage", "tracker")

ROOT = Path(__file__).resolve().parent.parent


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"  ERROR    {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"  WARNING  {msg}")

    def ok(self, msg: str) -> None:
        print(f"  ok       {msg}")


def section(title: str) -> None:
    print(f"\n== {title}")


def check_structure(zf: zipfile.ZipFile, size: int, r: Report) -> None:
    section("Zip structure")
    if size > MAX_SIZE:
        r.error(f"zip is {size / 1e6:.1f} MB; the limit is 25 MB")
    else:
        r.ok(f"size {size / 1024:.0f} KB")

    infos = zf.infolist()
    tops = {PurePosixPath(i.filename).parts[0] for i in infos}
    if tops != {PLUGIN}:
        r.error(f"top-level entries must be the single folder {PLUGIN}/, got {sorted(tops)}")
    else:
        r.ok(f"single top-level folder {PLUGIN}/")

    names = {i.filename for i in infos}
    for required in ("metadata.txt", "__init__.py"):
        if f"{PLUGIN}/{required}" not in names:
            r.error(f"{PLUGIN}/{required} is missing")
    if not any(n.lower().startswith(f"{PLUGIN}/license") for n in names):
        r.warn(f"no LICENSE file in {PLUGIN}/ (recommended)")
    if not any(n.lower().startswith(f"{PLUGIN}/readme") for n in names):
        r.warn(f"no README in {PLUGIN}/ (recommended)")

    bad = 0
    for info in infos:
        path = PurePosixPath(info.filename)
        name = info.filename
        mode = info.external_attr >> 16
        if path.name in SCANNER_CONFIG:
            r.error(f"scanner config file: {name} (status would be 'Validated (configured)')")
            bad += 1
        elif any(p.startswith(".") for p in path.parts):
            r.error(f"hidden file or folder: {name}")
            bad += 1
        if any(p in ("__MACOSX", "__pycache__", ".git") for p in path.parts):
            r.error(f"build or VCS leftover: {name}")
            bad += 1
        if info.is_dir():
            continue
        if mode & 0o111:
            r.error(f"executable bit set: {name}")
            bad += 1
        suffix = path.suffix.lower()
        if suffix in SUSPICIOUS:
            r.error(f"script or binary file type: {name}")
            bad += 1
        if re.fullmatch(r"ui_.*\.py|resources_rc\.py|.*_rc\.py", path.name):
            r.error(f"generated Qt file: {name}")
            bad += 1
        if suffix not in BINARY_OK and b"\0" in zf.read(info)[:8192]:
            r.error(f"binary file: {name}")
            bad += 1
    if not bad:
        r.ok("no hidden, executable, generated or unexpected binary files")


def check_metadata(zf: zipfile.ZipFile, r: Report) -> None:
    section("metadata.txt")
    try:
        text = zf.read(f"{PLUGIN}/metadata.txt").decode("utf-8")
    except KeyError:
        r.error("metadata.txt is missing")
        return
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str  # keep camelCase keys
    cp.read_string(text)
    if not cp.has_section("general"):
        r.error("metadata.txt has no [general] section")
        return
    meta = cp["general"]

    missing = [k for k in REQUIRED_KEYS if not meta.get(k, "").strip()]
    if missing:
        r.error(f"missing or empty: {', '.join(missing)}")
    else:
        r.ok(f"required keys present ({', '.join(REQUIRED_KEYS)})")

    for key in LINK_KEYS:
        url = meta.get(key, "").strip()
        if url and not re.fullmatch(r"https://[^\s]+", url):
            r.error(f"{key} must be an https:// URL, got {url!r}")
        elif url:
            r.ok(f"{key} = {url}")

    version = meta.get("version", "").strip()
    if version and not re.fullmatch(r"\d+(\.\d+){1,3}", version):
        r.error(f"version {version!r} is not like 1.2.3")
    elif version:
        r.ok(f"version = {version}")

    changelog = [ln.strip() for ln in meta.get("changelog", "").splitlines() if ln.strip()]
    if not changelog:
        r.error("changelog is empty")
    elif version and not re.search(rf"(^|\s){re.escape(version)}(\s|$)", changelog[0]):
        r.error(f"the first changelog line does not mention version {version}: {changelog[0][:80]!r}")
    else:
        r.ok(f"changelog starts with: {changelog[0][:70]}")

    icon = meta.get("icon", "").strip()
    if icon and f"{PLUGIN}/{icon}" not in zf.namelist():
        r.error(f"icon {icon} is not in the zip")

    for key in ("description", "about"):
        value = meta.get(key, "")
        if re.search(r"[æøåÆØÅ]", value):
            r.warn(f"{key} contains Danish letters; it must be in English")

    if meta.get("experimental", "").strip().lower() == "true":
        r.warn("experimental=True")
    if meta.get("deprecated", "").strip().lower() == "true":
        r.warn("deprecated=True")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    print("  $ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def indent(text: str) -> str:
    return "\n".join("    " + ln for ln in text.rstrip().splitlines())


def check_scanners(workdir: Path, r: Report) -> None:
    uvx = shutil.which("uvx")
    if not uvx:
        section("Scanners")
        r.error("uvx not found; install uv (https://docs.astral.sh/uv/) to run the scanners")
        return

    section("bandit (a finding blocks the version)")
    p = run([uvx, "bandit", "-r", PLUGIN, "-f", "json", "-q"], workdir)
    try:
        results = json.loads(p.stdout)["results"]
    except (ValueError, KeyError):
        r.error(f"bandit failed:\n{indent(p.stdout + p.stderr)}")
    else:
        for res in results:
            r.error(f"bandit {res['test_id']} ({res['issue_severity']}) "
                    f"{res['filename']}:{res['line_number']}: {res['issue_text']}")
        if not results:
            r.ok("no findings")

    section("detect-secrets (a critical finding blocks the version)")
    p = run([uvx, "detect-secrets", "scan", "--all-files", PLUGIN], workdir)
    try:
        results = json.loads(p.stdout)["results"]
    except (ValueError, KeyError):
        r.error(f"detect-secrets failed:\n{indent(p.stdout + p.stderr)}")
    else:
        for filename, secrets in results.items():
            for s in secrets:
                r.error(f"detect-secrets {s['type']} {filename}:{s['line_number']}")
        if not results:
            r.ok("no findings")

    section(f"flake8 critical rules ({FLAKE8_CRITICAL})")
    p = run([uvx, "flake8", f"--select={FLAKE8_CRITICAL}", PLUGIN], workdir)
    if p.returncode != 0 or p.stdout.strip():
        r.error(f"flake8 critical findings:\n{indent(p.stdout + p.stderr)}")
    else:
        r.ok("no findings")

    section("flake8 all rules (informational)")
    p = run([uvx, "flake8", "--count", "--exit-zero", "-q", PLUGIN], workdir)
    lines = p.stdout.strip().splitlines()
    count = lines[-1] if lines and lines[-1].isdigit() else "?"
    print(f"  info     {count} findings in {len(lines) - 1} files (shown on plugins.qgis.org, do not block)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("zip", nargs="?", default=str(ROOT / "dist" / f"{PLUGIN}.zip"))
    ap.add_argument("--workdir", default=str(ROOT / "dist" / "publish-check"),
                    help="where the zip is unpacked (emptied first)")
    args = ap.parse_args(argv)

    zip_path = Path(args.zip)
    if not zip_path.is_file():
        print(f"{zip_path} not found; run make package first", file=sys.stderr)
        return 1
    print(f"Checking {zip_path}")
    r = Report()
    with zipfile.ZipFile(zip_path) as zf:
        check_structure(zf, zip_path.stat().st_size, r)
        check_metadata(zf, r)
        workdir = Path(args.workdir)
        shutil.rmtree(workdir, ignore_errors=True)
        workdir.mkdir(parents=True)
        zf.extractall(workdir)
    check_scanners(workdir, r)

    print(f"\n{len(r.errors)} error(s), {len(r.warnings)} warning(s)")
    if r.errors:
        print("Do not upload this zip.")
        return 1
    print("OK to upload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
