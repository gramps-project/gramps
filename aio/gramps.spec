# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GrampsAIO Windows build.

Replaces setup.py (cx_Freeze).  Run from the aio/ directory:

    pyinstaller gramps.spec

Output lands in dist/grampsaio/.  The NSIS script is built separately
(see build.sh).
"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# ── Version ────────────────────────────────────────────────────────────────────
sys.path.insert(0, "dist")
import gramps
from gramps.version import VERSION_TUPLE

try:
    from gramps.version import VERSION_QUALIFIER
except ImportError:
    VERSION_QUALIFIER = ""

FULL_VERSION = ".".join(map(str, VERSION_TUPLE)) + VERSION_QUALIFIER

# ── Hidden imports (packages cx_Freeze used to enumerate) ─────────────────────
PACKAGES = [
    "gi",
    "cairo",
    "xml",
    "bsddb3",
    "lxml",
    "PIL",
    "json",
    "csv",
    "sqlite3",
    "cProfile",
    "networkx",
    "psycopg2",
    "requests",
    "logging",
    "html",
    "compileall",
    "graphviz",
    "pydotplus",
    "pygraphviz",
    "pydot",
    "orjson",
    "selenium",
]

hidden_imports = ["colorsys", "site"]
for _pkg in PACKAGES:
    try:
        hidden_imports += collect_submodules(_pkg)
    except Exception:
        pass

# ── Binaries: DLLs / exes not found by PyInstaller automatically ──────────────
_bin = os.path.join(sys.base_exec_prefix, "bin")

EXTRA_BINARIES = [
    "libgtk-3-0.dll",
    "libgspell-1-3.dll",
    "libgexiv2-2.dll",
    "libgoocanvas-3.0-9.dll",
    "libosmgpsmap-1.0-1.dll",
    "gswin64c.exe",
    "gswin32c.exe",
    "dot.exe",
    "libgvplugin_core-6.dll",
    "libgvplugin_dot_layout-6.dll",
    "libgvplugin_gd-6.dll",
    "libgvplugin_pango-6.dll",
    "libgvplugin_rsvg-6.dll",
    "glib-compile-schemas.exe",
    "gdk-pixbuf-query-loaders.exe",
    "gtk-update-icon-cache-3.0.exe",
    "fc-cache.exe",
    "fc-match.exe",
    "gspawn-win64-helper-console.exe",
    "gspawn-win64-helper.exe",
    "libgeocode-glib-2-0.dll",
    "gdbus.exe",
]

binaries = []
for _name in EXTRA_BINARIES:
    _path = os.path.join(_bin, _name)
    if os.path.exists(_path):
        binaries.append((_path, "."))

# ── Data files ─────────────────────────────────────────────────────────────────
# PyInstaller's gi hook (pyinstaller-hooks-contrib) handles:
#   - girepository-1.0/ typelibs
#   - lib/gdk-pixbuf-2.0/ loaders (and rewrites loaders.cache with relative paths)
#   - Icon themes configured via hooksconfig below
# Everything else is listed here.

datas = []

# Gramps package and shared data from the built wheel
datas.append(("dist/gramps", "gramps"))
datas.append(
    ("dist/gramps-" + FULL_VERSION + ".data/data/share", "share")
)

# GLib-ecosystem directories from MSYS2 that PyInstaller doesn't auto-detect.
# Source paths are relative to sys.base_prefix (/mingw64).
# Destination paths mirror the MSYS2 layout so existing env-var logic works.
_MSYS2_DATAS = [
    ("lib/enchant-2",                       "lib/enchant-2"),
    ("lib/gio",                             "lib/gio"),
    ("share/enchant",                       "share/enchant"),
    ("share/glib-2.0/schemas",              "share/glib-2.0/schemas"),
    ("share/xml/iso-codes",                 "share/xml/iso-codes"),
    ("etc/gtk-3.0",                         "etc/gtk-3.0"),
    ("etc/ssl",                             "etc/ssl"),
    ("etc/fonts",                           "etc/fonts"),
    ("share/icons/gnome",                   "share/icons/gnome"),
    ("share/icons/hicolor",                 "share/icons/hicolor"),
    ("share/locale",                        "share/locale"),
]

for _src_rel, _dst in _MSYS2_DATAS:
    _src = os.path.join(sys.base_prefix, _src_rel)
    if os.path.exists(_src):
        datas.append((_src, _dst))

# gramps.png icon (single file, not a directory)
_gramps_png = os.path.join(sys.base_prefix, "share/icons/gramps.png")
if os.path.exists(_gramps_png):
    datas.append((_gramps_png, "share/icons"))

# Adwaita icon theme subsets
for _subset in ["16x16", "scalable", "symbolic"]:
    _src = os.path.join(sys.base_prefix, "share/icons/Adwaita", _subset)
    if os.path.exists(_src):
        datas.append((_src, "share/icons/Adwaita/" + _subset))

# Adwaita index / cache
for _f in ["icon-theme.cache", "index.theme"]:
    _src = os.path.join(sys.base_prefix, "share/icons/Adwaita", _f)
    if os.path.exists(_src):
        datas.append((_src, "share/icons/Adwaita"))

# fontconfig cache dir placeholder
os.makedirs(
    os.path.join(sys.base_prefix, "var/cache/fontconfig"), exist_ok=True
)

# ── Excludes ───────────────────────────────────────────────────────────────────
excludes = [
    "tkinter",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "pyside",
    "sip",
    "PIL.ImageQt",
    "pip",
    "distlib",
]

# ── Shared hook configuration for all three analyses ──────────────────────────
_gi_hooksconfig = {
    "gi": {
        "module-versions": {"Gtk": "3.0"},
        "icons": ["Adwaita"],
        "themes": ["Adwaita", "Default"],
        "languages": [],          # collect all locales
    }
}

_common = dict(
    pathex=["dist"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig=_gi_hooksconfig,
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# ── Analysis for each executable ───────────────────────────────────────────────
a_w = Analysis(["grampsaiow.py"],  **_common)   # GUI, no console
a_c = Analysis(["grampsaioc.py"],  **_common)   # console
a_d = Analysis(["grampsaiocd.py"], **_common)   # debug console

pyz_w = PYZ(a_w.pure)
pyz_c = PYZ(a_c.pure)
pyz_d = PYZ(a_d.pure)

# ── Executables ────────────────────────────────────────────────────────────────
exe_w = EXE(
    pyz_w,
    a_w.scripts,
    [],
    exclude_binaries=True,
    name="grampsw",
    icon="gramps.ico",
    debug=False,
    strip=False,
    upx=False,
    console=False,        # GUI app — no console window
)

exe_c = EXE(
    pyz_c,
    a_c.scripts,
    [],
    exclude_binaries=True,
    name="gramps",
    icon="grampsc.ico",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)

exe_d = EXE(
    pyz_d,
    a_d.scripts,
    [],
    exclude_binaries=True,
    name="grampsd",
    icon="grampsd.ico",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)

# ── Collect everything into one directory ─────────────────────────────────────
# contents_directory='.' puts DLLs / Python extensions alongside the exes
# (flat layout, similar to the old cx_Freeze output) so the NSIS installer
# and the grampsaio*.py startup scripts can use simple relative paths.
coll = COLLECT(
    exe_w, a_w.binaries, a_w.datas,
    exe_c, a_c.binaries, a_c.datas,
    exe_d, a_d.binaries, a_d.datas,
    strip=False,
    upx=False,
    name="grampsaio",
    contents_directory=".",   # flat: everything next to the exes
)
