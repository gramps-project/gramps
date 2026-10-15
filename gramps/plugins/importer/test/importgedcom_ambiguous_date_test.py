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

"""Mantis 9298 — GEDCOM importer must warn on bare-numeric DATE values.

GEDCOM 5.5.1 requires three-letter month abbreviations (``7 NOV 1959``),
but some tools (notably ancestry.com exports) emit bare numeric
``D/M/YYYY`` dates that the spec does not define.  ``libgedcom`` parses
them as ``MM/DD/YYYY`` per :class:`GedcomDateParser.dhformat_changed`,
which silently swaps day and month for sources that use ``DD/MM/YYYY``.
The fix adds a warning per affected event so the user can audit; it does
not change the parse direction (US users still get the same result they
always did).

Asserts:

  * Bare numeric date with day ≤ 12 (the silent-swap case) triggers an
    "Ambiguous numeric date" warning quoting the original GEDCOM text.
  * Spec-compliant ``5 MAR 1899`` is silent.
  * Bare numeric date with day > 12 falls back to text-only storage
    (already visually flagged in Events view) and stays silent — adding
    a second warning would be noise.
  * The warning is advisory: ``number_of_errors`` stays at 0 and the
    summary line remains "GEDCOM import report: No errors detected"."""

import io
import os
import tempfile
import unittest

from gramps.cli.user import User as CliUser
from gramps.gen.db.utils import import_as_dict

GEDCOM_FIXTURE = """\
0 HEAD
1 SOUR Ancestry.com Family Trees
2 VERS (2026.1)
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
1 SUBM @SUBM@
0 @SUBM@ SUBM
1 NAME Bug 9298 fixture
0 @I1@ INDI
1 NAME Day Less /Than Thirteen/
1 SEX M
1 BIRT
2 DATE 7/11/1959
0 @I2@ INDI
1 NAME Day Greater /Than Twelve/
1 SEX F
1 BIRT
2 DATE 25/3/1934
0 @I3@ INDI
1 NAME Spec Compliant /Date/
1 SEX U
1 BIRT
2 DATE 5 MAR 1899
0 TRLR
"""


class CapturingUser(CliUser):
    """CLI ``User`` whose ``info`` / ``error`` / ``warn`` output is
    captured into a :class:`io.StringIO` so tests can assert against it."""

    def __init__(self):
        self.buf = io.StringIO()
        super().__init__(error=self.buf, callback=lambda *a, **k: None)
        # ``info()`` writes through ``self._fileout`` which defaults to
        # sys.stdout — redirect into our buffer.
        self._fileout = self.buf


class GedcomAmbiguousNumericDateWarningTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".ged", text=True)
        with os.fdopen(fd, "w") as f:
            f.write(GEDCOM_FIXTURE)
        self.user = CapturingUser()

    def tearDown(self):
        os.unlink(self.path)

    def _import(self):
        db = import_as_dict(self.path, self.user)
        self.assertIsNotNone(db, "import_as_dict returned None — import failed")
        return db, self.user.buf.getvalue()

    def test_silent_swap_case_emits_warning(self):
        _, out = self._import()
        # The actionable phrase + the original text both have to land in
        # the user-visible report.
        self.assertIn("Ambiguous numeric date", out)
        self.assertIn("'7/11/1959'", out)
        self.assertIn("1959-07-11", out)

    def test_spec_compliant_date_is_silent(self):
        _, out = self._import()
        self.assertNotIn("'5 MAR 1899'", out)

    def test_textonly_fallback_is_silent(self):
        # 25/3/1934 — day > 12 — parser fails over to text-only storage,
        # which is already visually flagged in the Events view as a bold
        # date.  A second warning would be noise.
        _, out = self._import()
        self.assertNotIn("'25/3/1934'", out)

    def test_warning_does_not_count_as_error(self):
        _, out = self._import()
        self.assertIn("GEDCOM import report: No errors detected", out)


if __name__ == "__main__":
    unittest.main()
