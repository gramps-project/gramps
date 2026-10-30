#
# Gramps - a GTK+/GNOME based genealogy program
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

"""Mantis 8850 — GEDCOM date qualifiers (CAL/EST/INT) recognised case-insensitively.

GEDCOM 5.5.1 specifies the approximate-date qualifier keywords ``CAL``
(calculated), ``EST`` (estimated) and ``INT`` (interpreted) in uppercase,
but real-world exporters emit them in mixed case (``2 DATE Cal 1847``).
libgedcom's ``MOD`` regex used to be case-sensitive, so ``Cal``/``Est``/
``Int`` never matched: the qualifier was left unrecognised and the value
passed through as a literal text (``MOD_TEXTONLY``) date, which the
Verify-the-Data tool then flags.  The same value in all-caps imported
correctly as a Calculated date.

These tests drive the real GEDCOM importer (``import_as_dict`` ->
``libgedcom``) and assert that mixed-case qualifiers resolve to the right
:class:`~gramps.gen.lib.date.Date` quality with the year parsed — matching
the all-uppercase behaviour — rather than falling back to a text date.
"""

import os
import tempfile
import unittest

from gramps.cli.user import User as CliUser
from gramps.gen.db.utils import import_as_dict
from gramps.gen.lib.date import Date

# Each individual carries a birth DATE using a qualifier keyword in a
# different case.  "Upper" is the all-uppercase control that already
# worked; the mixed-case variants are the regression cases.  Distinct
# surnames let the test key on the name instead of an importer-assigned
# gramps_id (whose padded format, e.g. ``I0001``, is configuration-driven).
GEDCOM_FIXTURE = """\
0 HEAD
1 SOUR Mantis 8850 fixture
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
1 SUBM @SUBM@
0 @SUBM@ SUBM
1 NAME Bug 8850 fixture
0 @I1@ INDI
1 NAME Mixed /Calc/
1 SEX M
1 BIRT
2 DATE Cal 1847
0 @I2@ INDI
1 NAME Mixed /Esti/
1 SEX F
1 BIRT
2 DATE Est 1850
0 @I3@ INDI
1 NAME Mixed /Inte/
1 SEX U
1 BIRT
2 DATE Int 1852
0 @I4@ INDI
1 NAME Upper /Calc/
1 SEX M
1 BIRT
2 DATE CAL 1847
0 TRLR
"""


class GedcomCalDateCaseInsensitiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fd, cls.path = tempfile.mkstemp(suffix=".ged", text=True)
        with os.fdopen(fd, "w") as f:
            f.write(GEDCOM_FIXTURE)
        # A plain CLI user that swallows callbacks; import_as_dict needs a
        # User.  Same construction as importgedcom_ambiguous_date_test.py.
        user = CliUser(callback=lambda *a, **k: None)
        cls.db = import_as_dict(cls.path, user)
        assert cls.db is not None, "import_as_dict returned None — import failed"
        # Map "<First> <Surname>" -> imported birth Date, so lookups do not
        # depend on the importer's gramps_id padding format.
        cls.dates = {}
        for person in cls.db.iter_people():
            name = person.get_primary_name()
            key = "%s %s" % (name.get_first_name(), name.get_surname())
            birth_ref = person.get_birth_ref()
            assert birth_ref is not None, "%s has no birth ref" % key
            event = cls.db.get_event_from_handle(birth_ref.ref)
            cls.dates[key] = event.get_date_object()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.path)

    def _assert_qualified(self, key, expected_qual, year):
        self.assertIn(key, self.dates, "person %s not imported" % key)
        date = self.dates[key]
        self.assertNotEqual(
            date.get_modifier(),
            Date.MOD_TEXTONLY,
            "%s imported as a text date, not a parsed qualified date" % key,
        )
        self.assertEqual(date.get_quality(), expected_qual)
        self.assertEqual(date.get_year(), year)

    def test_cal_mixed_case_is_calculated(self):
        # The reporter's case: "2 DATE Cal 1847".
        self._assert_qualified("Mixed Calc", Date.QUAL_CALCULATED, 1847)

    def test_est_mixed_case_is_estimated(self):
        self._assert_qualified("Mixed Esti", Date.QUAL_ESTIMATED, 1850)

    def test_int_mixed_case_is_calculated(self):
        self._assert_qualified("Mixed Inte", Date.QUAL_CALCULATED, 1852)

    def test_cal_upper_case_control_is_calculated(self):
        # All-caps already worked; pin it so the fix matches its behaviour.
        self._assert_qualified("Upper Calc", Date.QUAL_CALCULATED, 1847)


if __name__ == "__main__":
    unittest.main()
