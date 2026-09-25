#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Brian Caudill
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Unittests for the Grizard merge tool launcher."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.grizard.grizardlauncher import _case_insensitive_pattern


# ------------------------------------------------------------------
#
# GrizardMergeToolHelperTest
#
# ------------------------------------------------------------------
class GrizardMergeToolHelperTest(unittest.TestCase):
    """Test the GTK-free helpers used by the Grizard merge flow."""

    def test_case_insensitive_pattern(self) -> None:
        """Extension patterns match upper and lower case."""
        self.assertEqual(_case_insensitive_pattern("ged"), "*.[gG][eE][dD]")
        self.assertEqual(
            _case_insensitive_pattern("gramps"), "*.[gG][rR][aA][mM][pP][sS]"
        )

    def test_build_source_file_filters_fallback(self) -> None:
        """Filters always include genealogy types and an All files entry."""
        from gramps.gui.grizard.grizardlauncher import build_source_file_filters

        filters = build_source_file_filters()
        names = [f.get_name() for f in filters]
        self.assertTrue(any("All files" in name for name in names))
        self.assertTrue(len(filters) >= 2)


if __name__ == "__main__":
    unittest.main()
