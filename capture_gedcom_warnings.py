#! /usr/bin/env python3
"""Capture the GEDCOM import warning text without the GUI.

Replicates the import path used by Gramps (importData -> GedcomParser ->
parse_gedcom_file -> user.info(..., "".join(errors), ...)) but with a
User subclass that records the info text instead of showing a dialog.

Usage:
    python capture_gedcom_warnings.py [input_file] [output_file]

Examples:
    python capture_gedcom_warnings.py
    python capture_gedcom_warnings.py imp_notetest_dfs.ged
    python capture_gedcom_warnings.py imp_notetest_dfs.ged report.txt
"""

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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import sys

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import TEST_DIR
from gramps.gen.db.utils import make_database
from gramps.gen.user import User
from gramps.gen.utils.config import config
from gramps.plugins.importer.importgedcom import importData


class CaptureUser(User):
    """A User that captures the info() text instead of displaying it."""

    def __init__(self):
        super().__init__()
        self.report_title = ""
        self.infotext = ""

    def info(self, msg1, infotext, parent=None, monospaced=False):
        self.report_title = msg1
        self.infotext = infotext


def main():
    """Import the GEDCOM and print the captured warning text."""
    input_file = (
        sys.argv[1] if len(sys.argv) > 1 else "imp_notetest_lds_in-out-in_dfs.ged"
    )
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    fn1 = os.path.join(TEST_DIR, input_file)

    # Same "_dfs" preferences as imports_test.py make_tst_function()
    config.set("preferences.default-source", True)
    config.set("preferences.tag-on-import-format", "Imported")
    config.set("preferences.tag-on-import", True)

    # Set up a fresh in-memory database like the test does.
    db = make_database("sqlite")
    db.load(":memory:")
    db.set_feature("skip-import-additions", False)

    user = CaptureUser()
    importData(db, fn1, user)

    print("REPORT TITLE:", user.report_title)
    print("REPORT TEXT:")
    print(user.infotext)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(user.report_title + "\n")
            out.write(user.infotext)
        print(f"Wrote {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
