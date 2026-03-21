# -*- mode: python ; coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       The Gramps project
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# PyInstaller spec file for Gramps Windows AIO build.
#
# Three executables sharing a single COLLECT:
#   grampsw.exe  — GUI entry point (no console window)
#   gramps.exe   — console entry point
#   grampsd.exe  — debug console entry point
#
# Usage (from aio-pyinstaller/ directory):
#   pyinstaller gramps.spec

import sys
import os
import glob

# Path to the mingw64 prefix supplied by MSYS2.
_prefix = sys.base_prefix  # e.g. /mingw64

# hooksconfig for the gi (PyGObject) community hook.
# This controls which GTK version, icon themes, and Adwaita themes
# the hook bundles automatically.
_gi_hooksconfig = {
    "gi": {
        "module-versions": {
            "Gtk": "3.0",
            "GdkPixbuf": "2.0",
            "Pango": "1.0",
        },
        "icons": ["Adwaita"],
        "themes": ["Adwaita", "Default"],
    }
}

# Binaries that PyInstaller won't find automatically because they live
# in the MSYS2 prefix rather than next to the Python executable.
_extra_binaries = [
    # GraphViz
    (os.path.join(_prefix, "bin", "dot.exe"), "."),
    # GhostScript (64-bit name used in newer GhostScript versions)
    (os.path.join(_prefix, "bin", "gswin64c.exe"), "."),
    # GLib schema compiler
    (os.path.join(_prefix, "bin", "glib-compile-schemas.exe"), "."),
    # GDK-Pixbuf loader cache updater
    (os.path.join(_prefix, "bin", "gdk-pixbuf-query-loaders.exe"), "."),
    # Fontconfig cache builder
    (os.path.join(_prefix, "bin", "fc-cache.exe"), "."),
    (os.path.join(_prefix, "bin", "fc-match.exe"), "."),
    # GLib spawn helpers
    (os.path.join(_prefix, "bin", "gspawn-win64-helper.exe"), "."),
    (os.path.join(_prefix, "bin", "gspawn-win64-helper-console.exe"), "."),
    # GDBus
    (os.path.join(_prefix, "bin", "gdbus.exe"), "."),
]
# Filter out any that don't exist in the current environment.
_extra_binaries = [(src, dst) for src, dst in _extra_binaries if os.path.exists(src)]

# Extra data trees to include verbatim.
_extra_datas = [
    # SSL certificates
    (os.path.join(_prefix, "etc", "ssl"), "etc/ssl"),
    # Fontconfig configuration
    (os.path.join(_prefix, "etc", "fonts"), "etc/fonts"),
    # GTK-3 configuration (settings.ini etc.)
    (os.path.join(_prefix, "etc", "gtk-3.0"), "etc/gtk-3.0"),
    # GLib schemas (compiled by post-install step in NSIS)
    (os.path.join(_prefix, "share", "glib-2.0", "schemas"), "share/glib-2.0/schemas"),
    # ISO codes (country / language names used by Gramps)
    (os.path.join(_prefix, "share", "xml", "iso-codes"), "share/xml/iso-codes"),
    # GIO modules (network, TLS, …)
    (os.path.join(_prefix, "lib", "gio"), "lib/gio"),
    # Enchant dictionaries — downloaded during build, installed optionally
    (os.path.join(_prefix, "share", "enchant"), "share/enchant"),
    # Gramps application data (built wheel extracted into dist/)
    ("dist/gramps", "gramps"),
]
# Filter out any that don't exist in the current environment.
_extra_datas = [(src, dst) for src, dst in _extra_datas if os.path.exists(src)]

# Gramps share data lives in the wheel's .data/data/share/ tree.
# Add it to the bundle and set GRAMPS_RESOURCES so that ResourcePath()
# can import gramps successfully during PyInstaller's analysis phase.
_gramps_share_dirs = glob.glob(os.path.join("dist", "gramps-*.data", "data", "share"))
if _gramps_share_dirs:
    _gramps_share = os.path.abspath(_gramps_share_dirs[0])
    _extra_datas.append((_gramps_share, "share"))
    os.environ["GRAMPS_RESOURCES"] = _gramps_share
else:
    raise RuntimeError(
        "Could not find gramps-*.data/data/share in dist/. "
        "Make sure the Gramps wheel has been extracted into dist/ before running pyinstaller."
    )

# Force-collect packages that PyInstaller's isolated analysis subprocess
# may fail to find even when listed in hiddenimports.
from PyInstaller.utils.hooks import collect_all as _collect_all

# orjson is a hard Gramps dependency — abort if it cannot be collected.
_d, _b, _h = _collect_all("orjson")
_extra_datas += _d
_extra_binaries += _b

for _pkg in ("bsddb3", "lxml", "PIL", "cairo", "gi"):
    try:
        _d, _b, _h = _collect_all(_pkg)
        _extra_datas += _d
        _extra_binaries += _b
    except Exception:
        pass

# Packages that must be present even if not detected via import tracing.
_hidden_imports = [
    "gi",
    "gi.repository.Gtk",
    "gi.repository.GLib",
    "gi.repository.Gdk",
    "gi.repository.Pango",
    "gi.repository.PangoCairo",
    "gi.repository.GdkPixbuf",
    "gi.repository.Gio",
    "gi.repository.GObject",
    "gi.repository.GExiv2",
    "cairo",
    "bsddb3",
    "lxml",
    "lxml.etree",
    "PIL",
    "PIL.Image",
    "networkx",
    "psycopg2",
    "requests",
    "graphviz",
    "pydot",
    "pydotplus",
    "orjson",
    "colorsys",
    "cProfile",
    "compileall",
]

_excludes = [
    "tkinter",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "sip",
    "PIL.ImageQt",
    "pip",
]

# Common Analysis kwargs shared by all three entry points.
_common = dict(
    pathex=["dist"],        # so that 'import gramps' finds the extracted wheel
    binaries=_extra_binaries,
    datas=_extra_datas,
    hiddenimports=_hidden_imports,
    excludes=_excludes,
    hookspath=[],
    hooksconfig=_gi_hooksconfig,
    runtime_hooks=[],
    noarchive=False,
    optimize=1,
)

# ---------------------------------------------------------------------------
# Three Analysis objects — PyInstaller merges their graphs in COLLECT.
# ---------------------------------------------------------------------------

a_w = Analysis(["grampsaiow.py"], **_common)
a_c = Analysis(["grampsaioc.py"], **_common)
a_d = Analysis(["grampsaiocd.py"], **_common)

# ---------------------------------------------------------------------------
# PYZ archives (one per Analysis so imports resolve correctly)
# ---------------------------------------------------------------------------

pyz_w = PYZ(a_w.pure, a_w.zipped_data)
pyz_c = PYZ(a_c.pure, a_c.zipped_data)
pyz_d = PYZ(a_d.pure, a_d.zipped_data)

# ---------------------------------------------------------------------------
# EXE targets
# ---------------------------------------------------------------------------

exe_w = EXE(
    pyz_w,
    a_w.scripts,
    [],
    exclude_binaries=True,
    name="grampsw",
    icon="../aio/gramps.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,       # no console window — GUI entry point
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

exe_c = EXE(
    pyz_c,
    a_c.scripts,
    [],
    exclude_binaries=True,
    name="gramps",
    icon="../aio/grampsc.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,        # console entry point
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

exe_d = EXE(
    pyz_d,
    a_d.scripts,
    [],
    exclude_binaries=True,
    name="grampsd",
    icon="../aio/grampsd.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,        # debug console entry point
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

# ---------------------------------------------------------------------------
# Single COLLECT — all three executables share the same dependency tree.
# contents_directory='.' puts everything alongside the executables (flat
# layout), which is what the NSIS template expects.
# ---------------------------------------------------------------------------

coll = COLLECT(
    exe_w,
    a_w.binaries,
    a_w.zipfiles,
    a_w.datas,
    exe_c,
    a_c.binaries,
    a_c.zipfiles,
    a_c.datas,
    exe_d,
    a_d.binaries,
    a_d.zipfiles,
    a_d.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="grampsaio",
    contents_directory=".",
)
