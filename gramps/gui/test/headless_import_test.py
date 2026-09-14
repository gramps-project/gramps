#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps project
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

"""
Regression test: importing a Gramps GUI widget module must not crash the
interpreter when there is no display (headless).

Background
----------
``gramps/gui/widgets/grampletpane.py`` computed the theme link colour in the
body of ``class LinkTag`` -- code that runs at *import* time -- by constructing
a ``Gtk.Label`` and reading its style context::

    linkcolor = Gtk.Label(label="test")
    linkcolor = get_link_color(linkcolor.get_style_context())

With no display connection Gtk turns "can't create a GtkStyleContext" into a
fatal ``Gtk-ERROR``, which raises ``SIGTRAP`` and aborts the whole process
("Trace/breakpoint trap (core dumped)").  Any headless import of this module --
directly, or transitively via ``gramps.gui.views.listview`` /
``gramps.plugins.lib.libpersonview`` -- therefore killed the interpreter.  In a
``python3 -m unittest discover`` run that takes down the entire core unit suite.

A segfault/abort cannot be caught in-process, so this test spawns a child
``python3 -c "import ..."`` with the display stripped from its environment and
asserts the child exits cleanly (returncode 0).  Pre-fix the child dies on
``SIGTRAP`` (returncode -5 / 133); post-fix the colour is computed lazily on
first use, so nothing display-dependent runs at import and the child exits 0.

This module imports no ``gi``/``gramps.gui`` symbol itself, so it loads and runs
under a plain headless ``python3 -m unittest`` (the C4 verify / T3-unit env).
"""

import os
import subprocess
import sys
import unittest

# The module whose class-body widget construction triggered the abort. Importing
# it is the minimal reproduction of the crashing import chain that the headless
# core unit run hit (libpersonview -> listview -> pageview -> grampletbar ->
# grampletpane:LinkTag).
_TARGET_MODULES = (
    "gramps.gui.widgets.grampletpane",
    "gramps.plugins.lib.libpersonview",
)


def _import_headless(module_name):
    """
    Import *module_name* in a fresh interpreter with no display connection.

    Returns the completed ``subprocess.run`` result. ``returncode`` is 0 on a
    clean import, negative (``-signal``) or 128+signal if the child was killed
    by a signal such as ``SIGTRAP`` from a fatal ``Gtk-ERROR``.
    """
    env = dict(os.environ)
    # Force the headless condition regardless of how the suite is launched.
    for var in ("DISPLAY", "WAYLAND_DISPLAY"):
        env.pop(var, None)
    # gramps.gen imports need the resource root; default to the checkout cwd.
    env.setdefault("GRAMPS_RESOURCES", ".")
    return subprocess.run(
        [sys.executable, "-c", "import %s" % module_name],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )


class HeadlessImportTest(unittest.TestCase):
    """Importing GUI widget modules headless must not abort the interpreter."""

    def test_grampletpane_imports_headless(self):
        """The faulting module imports cleanly with no display."""
        result = _import_headless("gramps.gui.widgets.grampletpane")
        self.assertEqual(
            result.returncode,
            0,
            "Headless `import gramps.gui.widgets.grampletpane` did not exit 0 "
            "(returncode %r) -- the class-body Gtk widget construction aborts "
            "without a display.\n--- child output ---\n%s"
            % (result.returncode, result.stdout.decode("utf-8", "replace")),
        )

    def test_libpersonview_chain_imports_headless(self):
        """The transitive chain the unit suite hit imports cleanly headless."""
        result = _import_headless("gramps.plugins.lib.libpersonview")
        self.assertEqual(
            result.returncode,
            0,
            "Headless `import gramps.plugins.lib.libpersonview` did not exit 0 "
            "(returncode %r) -- it pulls in grampletpane, whose class-body "
            "widget construction aborts without a display.\n"
            "--- child output ---\n%s"
            % (result.returncode, result.stdout.decode("utf-8", "replace")),
        )


if __name__ == "__main__":
    unittest.main()
