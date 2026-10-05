#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
Regression test for bug #13532.

The fan chart views (Fan Chart, Descendant Fan Chart, 2-way Fan Chart) render
person names on two lines.  They used to do so through two hard-pinned name
formats ("%l" and "%f %s"), so the chart always showed surname / given-suffix
regardless of the user's active "Name format" preference.

The fix routes the two-line rendering through the name displayer's
``get_two_line_format`` / ``display_two_lines`` helpers, which split the
*active* name format at the surname/given comma.  This test drives those very
helpers -- the same production code the chart calls in
``gramps.gui.widgets.fanchart.FanChartBaseWidget.draw_person`` -- with no GUI
import, so it runs headlessly.
"""

import unittest

from gramps.gen.display.name import NameDisplay
from gramps.gen.lib import Name, Person, Surname


def _make_person():
    """A person whose name has a given name, a surname and a suffix."""
    name = Name()
    name.set_first_name("Avis")
    name.set_suffix("III")
    surname = Surname()
    surname.set_surname("Fernandez")
    name.add_surname(surname)
    person = Person()
    person.set_primary_name(name)
    return person


class FanChartNameFormatTest(unittest.TestCase):
    def setUp(self):
        self.nd = NameDisplay()
        self.person = _make_person()

    # -- get_two_line_format -------------------------------------------------

    def test_split_lnfn_at_comma(self):
        """'Surname, Given Suffix' splits into surname / given-suffix lines."""
        self.nd.set_default_format(Name.LNFN)
        self.assertEqual(("%l", "%f %s"), self.nd.get_two_line_format())

    def test_split_given_has_no_second_line(self):
        """'Given' has no comma, so it stays on the first line only."""
        self.nd.set_default_format(Name.FN)
        self.assertEqual(("%f", ""), self.nd.get_two_line_format())

    def test_split_fnln_has_no_second_line(self):
        """'Given Surname Suffix' has no comma -> single line."""
        self.nd.set_default_format(Name.FNLN)
        self.assertEqual(("%f %l %s", ""), self.nd.get_two_line_format())

    def test_explicit_num_overrides_default(self):
        """A passed-in format index is honoured over the active default."""
        self.nd.set_default_format(Name.FN)
        self.assertEqual(("%l", "%f %s"), self.nd.get_two_line_format(Name.LNFN))

    # -- display_two_lines (the rendered chart labels) -----------------------

    def test_two_lines_follow_lnfn(self):
        self.nd.set_default_format(Name.LNFN)
        self.assertEqual(
            ("Fernandez", "Avis III"), self.nd.display_two_lines(self.person)
        )

    def test_two_lines_follow_given(self):
        # The reporter's case: with "Given" the chart must show only "Avis",
        # not "Fernandez ... Avis III".
        self.nd.set_default_format(Name.FN)
        self.assertEqual(("Avis", ""), self.nd.display_two_lines(self.person))

    def test_two_lines_follow_fnln(self):
        self.nd.set_default_format(Name.FNLN)
        self.assertEqual(
            ("Avis Fernandez III", ""), self.nd.display_two_lines(self.person)
        )

    def test_changing_format_changes_labels(self):
        """The invariant: a format change is reflected in the chart labels."""
        self.nd.set_default_format(Name.LNFN)
        lnfn = self.nd.display_two_lines(self.person)
        self.nd.set_default_format(Name.FN)
        given = self.nd.display_two_lines(self.person)
        self.assertNotEqual(lnfn, given)


if __name__ == "__main__":
    unittest.main()
