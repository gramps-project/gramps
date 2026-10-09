#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Test package for gramps.gui.fs.person.mixins.

Bootstraps gi version declarations and sys.modules stubs that must be in
place before any module in the gramps.gui.fs.person package chain is
imported.  When unittest discovers this package it first imports all parent
``__init__.py`` files.  The parent ``gramps.gui.fs.person.__init__`` in turn
imports ``fsg_sync``, which pulls in ``compare_gtk`` and other GTK-using
modules.  On machines where both GTK 3 and GTK 4 are installed, importing
those modules without a prior ``gi.require_version("Gtk", "3.0")`` call
causes gi to load GTK 4, and later calls to ``gi.require_version("Gtk",
"3.0")`` in other modules raise a ValueError.  We address this by:

1. Making ``gi.require_version`` lenient (silently ignore an already-loaded
   version) before the parent package chain runs.
2. Pre-stubbing ``gramps.gui.grampsgui`` to prevent the ``sys.exit(1)``
   guard that fires when it cannot re-declare the GTK version.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import sys
from unittest.mock import MagicMock

# Protect headless / standalone CI runs from missing display.
os.environ.setdefault("GDK_BACKEND", "-")

# -------------------------------------------------------------------------
#
# GTK/Gnome bootstrap
#
# -------------------------------------------------------------------------
import gi as _gi

_original_require_version = _gi.require_version


def _lenient_require_version(namespace: str, version: str) -> None:
    """
    Call gi.require_version, ignoring conflicts with already-loaded versions.

    On systems with multiple GTK versions installed, importing any gi module
    without a prior require_version call loads the latest available version.
    Subsequent require_version calls for a different version then raise
    ValueError.  This wrapper silences that error so the test suite can
    proceed even when the GTK version preference was set by an earlier import.
    """
    try:
        _original_require_version(namespace, version)
    except ValueError:
        pass


_gi.require_version = _lenient_require_version

# Pre-stub gramps.gui.grampsgui so that the sys.exit(1) guard inside it
# never fires during test discovery.
if "gramps.gui.grampsgui" not in sys.modules:
    sys.modules["gramps.gui.grampsgui"] = MagicMock()
