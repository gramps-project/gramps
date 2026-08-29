#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Eduard Ralph
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
Unittest for the Media Manager "absolute to relative" help text (bug 13354).

The Convert2Rel batch-op's ``description`` is the tooltip/help shown for the
"Convert paths from absolute to relative" step. It contained the misspelling
"viz-a-viz"; the correct form is "vis-à-vis". This asserts the corrected word
on the production class attribute, so a regression that reintroduces the typo
fails the build.
"""

import unittest

from gramps.plugins.tool.mediamanager import Convert2Rel


# ------------------------------------------------------------
#
# Convert2RelHelpTextTest
#
# ------------------------------------------------------------
class Convert2RelHelpTextTest(unittest.TestCase):
    """The 'absolute -> relative' help text is spelled correctly (bug 13354)."""

    def test_no_viz_a_viz_typo(self):
        """The misspelling 'viz-a-viz' is gone from the help text."""
        self.assertNotIn("viz-a-viz", Convert2Rel.description)

    def test_uses_vis_a_vis(self):
        """The help text uses the correct word 'vis-à-vis'."""
        self.assertIn("vis-à-vis", Convert2Rel.description)


if __name__ == "__main__":
    unittest.main()
