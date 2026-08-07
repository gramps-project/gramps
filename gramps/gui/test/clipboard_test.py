#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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

"""Unittest for clipboard.py module-load resilience."""

import importlib
import sys
import unittest
from unittest.mock import patch

# clipboard.py uses Gdk.atom_intern which is GTK-3-only (removed in
# GTK 4). Pin the GTK version before any test imports clipboard so
# the binding is available — matches what gramps.grampsapp does at
# startup. Skip cleanly if GTK 3 is not available.
try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
except (ImportError, ValueError) as err:
    raise unittest.SkipTest("GTK 3.0 / PyGObject not available: %s" % err)


# ------------------------------------------------------------
#
# TestClipboardImportsHeadless
#
# ------------------------------------------------------------
class TestClipboardImportsHeadless(unittest.TestCase):
    """Regression: clipboard.py must import cleanly when no default
    Gtk screen is available.

    ``Gtk.IconTheme.get_default()`` returns ``None`` in headless
    containers (no DISPLAY, plugin-registration smoke tests run
    outside an X server, etc.). Historically the module-level
    ``theme.load_icon(...)`` calls then raised
    ``AttributeError: 'NoneType' object has no attribute 'load_icon'``
    and the whole module failed to import — breaking every addon
    that did ``from gramps.gui.clipboard import ...``.
    """

    def test_loads_when_theme_is_none(self):
        """Force ``IconTheme.get_default`` to return ``None`` and
        verify the module still imports, with sane fallbacks for
        ``LINK_PIC`` and ``ICONS``."""
        # Drop any cached import so the module-level code re-runs
        # under the patched IconTheme.
        sys.modules.pop("gramps.gui.clipboard", None)
        with patch("gi.repository.Gtk.IconTheme") as mock_theme:
            mock_theme.get_default.return_value = None
            mod = importlib.import_module("gramps.gui.clipboard")
        self.assertIsNone(mod.LINK_PIC)
        # In headless mode every OBJ2ICON key is populated with None
        # so class-body lookups like ``ICON = ICONS["address"]``
        # do not KeyError during module load.
        self.assertEqual(set(mod.ICONS.keys()), set(mod.OBJ2ICON.keys()))
        self.assertTrue(all(v is None for v in mod.ICONS.values()))


if __name__ == "__main__":
    unittest.main()
