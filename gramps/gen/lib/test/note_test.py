#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps developers
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

"""unittest for Note.get_preview()

Regression coverage for bug 8597: the Note preview was truncated at a
hardcoded 79 characters.  It must instead honour the configurable
``interface.note-preview-length`` setting.
"""

import unittest

from gramps.gen.config import config
from ..note import Note


class NotePreviewTest(unittest.TestCase):
    """Exercise the production ``Note.get_preview`` truncation."""

    def setUp(self):
        self._saved = config.get("interface.note-preview-length")

    def tearDown(self):
        config.set("interface.note-preview-length", self._saved)

    def _note(self, text):
        note = Note()
        note.set(text)
        return note

    def test_honours_configured_length(self):
        """get_preview truncates at the configured length, not a constant."""
        config.set("interface.note-preview-length", 20)
        note = self._note("x" * 100)
        self.assertEqual(note.get_preview(), "x" * 20 + "...")

    def test_not_hardcoded_79(self):
        """A length above the old hardcoded 79 is respected (defect gone)."""
        config.set("interface.note-preview-length", 120)
        note = self._note("y" * 200)
        preview = note.get_preview()
        # Under the old hardcoded-79 behaviour this would have been
        # "y" * 79 + "..."; it must now follow the config value.
        self.assertEqual(preview, "y" * 120 + "...")

    def test_short_text_not_truncated(self):
        """Text shorter than the limit is returned unchanged."""
        config.set("interface.note-preview-length", 50)
        note = self._note("short note")
        self.assertEqual(note.get_preview(), "short note")

    def test_newlines_flattened(self):
        """Newlines are replaced by spaces in the preview."""
        config.set("interface.note-preview-length", 80)
        note = self._note("line one\nline two")
        self.assertEqual(note.get_preview(), "line one line two")


if __name__ == "__main__":
    unittest.main()
