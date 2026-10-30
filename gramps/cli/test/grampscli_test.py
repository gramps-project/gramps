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

"""Mantis 6085 — the CLI must show the database upgrade statistics.

``gramps_upgrade_16`` leaves its statistics on ``db.upgrade_summary`` for the
caller to display.  The GUI shows them in a dialog; the CLI prints them to
stderr, since a log message would not appear at the default log level.
"""

import contextlib
import io
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from gramps.gen.db.exceptions import DbVersionError

from ..grampscli import CLIDbLoader


class ReadFileUpgradeSummaryTest(unittest.TestCase):
    """What ``CLIDbLoader.read_file`` prints after loading a database."""

    def _read_file(self, summary, load_error=None):
        """Return the loaded mock db and whatever was written to stdout/stderr."""
        db = MagicMock(upgrade_summary=summary)
        db.load.side_effect = load_error
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            tempfile.TemporaryDirectory() as path,
            patch("gramps.cli.grampscli.make_database", return_value=db),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            loader = CLIDbLoader(MagicMock(db=db))
            try:
                loader.read_file(path, None, None)
            except SystemExit:
                pass
        return db, stdout.getvalue(), stderr.getvalue()

    def test_summary_goes_to_stderr_only(self):
        db, stdout, stderr = self._read_file("Number of new objects: 42")
        self.assertIn("Number of new objects: 42", stderr)
        self.assertEqual(stdout, "")
        self.assertIsNone(db.upgrade_summary)

    def test_nothing_printed_without_an_upgrade(self):
        _db, stdout, stderr = self._read_file(None)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    def test_summary_not_printed_when_load_fails(self):
        _db, _stdout, stderr = self._read_file(
            "Number of new objects: 42",
            load_error=DbVersionError("15", "16", "21"),
        )
        self.assertNotIn("Number of new objects", stderr)
        self.assertIn("ERROR", stderr)


if __name__ == "__main__":
    unittest.main()
