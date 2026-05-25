#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Eduard Ralph
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

"""Architectural guard against the Mantis 6085 regression class.

bmcage's 2012 audit (Mantis 6085, "Import outside of the gen submodule")
listed five files under ``gramps/gen/`` that pulled symbols from
``gramps.gui`` or ``gramps.cli``.  Four of those — ``filters/rules/
_changedsincebase.py``, ``filters/rules/person/
_deeprelationshippathbetween.py``, ``plug/_gramplet.py`` and
``merge/diff.py`` — were cleared up over the years.  The fifth,
``gen/db/upgrade.py``, kept two imports until this commit:

  * ``from gramps.cli.clidbman import NAME_FILE``
  * ``from gramps.gui.dialog import InfoDialog``

Now ``NAME_FILE`` lives in ``gramps/gen/db/dbconst.py`` (re-exported
from ``gramps/cli/clidbman.py`` for the gui / bsddb-converter callers
that still pull it from there) and ``gramps_upgrade_16``'s upgrade-
statistics dialog text is stored on ``self.upgrade_summary`` so the
``gramps/gui/dbloader.py`` GUI caller can display it.

This test fails if any module under ``gramps/gen/`` re-introduces an
``import`` or ``from`` statement that references ``gramps.gui`` or
``gramps.cli``.  It is intentionally a source-grep — the architectural
invariant lives at the module-import level, and the diagnostic value
is in catching new violations early, not in exercising every code
path.
"""

import os
import re
import unittest

import gramps.gen

# Anchor to the actual ``gramps.gen`` package directory.  ``DATA_DIR``
# from ``gramps.gen.const`` points at the build-artifact data folder,
# not the source tree, so using ``gramps.gen.__file__`` is the only
# reliable way to find the .py files we want to grep.
GEN_DIR = os.path.dirname(os.path.abspath(gramps.gen.__file__))

# Match real import statements, not docstring mentions or comments.
# Examples that match:
#     from gramps.gui.dialog import InfoDialog
#     from gramps.cli.clidbman import NAME_FILE
#     import gramps.gui.utils
# Examples that do *not* match:
#     # See gramps.gui.dbloader for how this is consumed.
#     """GUI orchestration lives in gramps.gui.fs.fs_import."""
_FORBIDDEN_IMPORT = re.compile(
    r"^\s*(?:from\s+gramps\.(?:gui|cli)\b|import\s+gramps\.(?:gui|cli)\b)",
    re.MULTILINE,
)


# ------------------------------------------------------------
#
# GenImportBoundaryTest
#
# ------------------------------------------------------------
class GenImportBoundaryTest(unittest.TestCase):
    def test_gen_does_not_import_from_gui_or_cli(self):
        """No file under gramps/gen/ may import from gramps.gui or
        gramps.cli — gen is meant to be the GUI-agnostic core
        (Mantis 6085)."""
        offenders = []
        for dirpath, _dirnames, filenames in os.walk(GEN_DIR):
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                # Skip the per-module test directories — tests are free
                # to import GUI/CLI helpers if they need to drive them.
                # Match any path component named "test" so fixture sub-
                # directories under a test/ dir are skipped too, not just
                # the leaf.
                rel = os.path.relpath(dirpath, GEN_DIR)
                if "test" in rel.split(os.sep):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as fp:
                    source = fp.read()
                for match in _FORBIDDEN_IMPORT.finditer(source):
                    line_no = source.count("\n", 0, match.start()) + 1
                    rel = os.path.relpath(path, os.path.dirname(GEN_DIR))
                    offenders.append(f"{rel}:{line_no}: {match.group().strip()}")
        self.assertFalse(
            offenders,
            "Files under gramps/gen/ must not import from gramps.gui or "
            "gramps.cli (Mantis 6085).  Re-add by moving the symbol into "
            "gramps/gen/ and re-exporting it from the old location if "
            "third-party callers depend on the old path.\n  " + "\n  ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
