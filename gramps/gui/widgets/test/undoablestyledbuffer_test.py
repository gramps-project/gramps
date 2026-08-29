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
Regression test for bug 13268 — Undo in the Notes editor scrolls to the top.

A GtkTextView's scroll position cannot be asserted headlessly (it needs a
realized widget and a display, neither of which the C4 gate provides).  But the
*cause* of the scroll jump lives in the buffer, which is a plain Gtk.TextBuffer
subclass and so is fully exercisable with no display:

The notes-editor undo handlers used to call :meth:`set_text`, which replaces the
entire buffer content.  A full-buffer replace deletes the whole buffer, which
collapses *every* Gtk.TextMark to offset 0 — including the marks a bound
GtkTextView uses to track its scroll position.  That is exactly why the view
jumped to the top of the note after an Undo.

This test stands in for the viewport by placing an independent TextMark at the
edit site (where the user was working, well below the top) and asserting that an
Undo does **not** collapse it to offset 0.  It drives the real production
``UndoableStyledBuffer.undo()`` path, so it is red before the fix and green
after.
"""

import unittest

from gramps.gen.lib import StyledText
from gramps.gui.widgets.undoablestyledbuffer import UndoableStyledBuffer


class UndoViewportPreservationTest(unittest.TestCase):
    """Bug 13268: Undo must not reset the editor's viewport to the top."""

    def _long_buffer(self):
        """A note long enough to need scrolling, with undo history cleared."""
        buf = UndoableStyledBuffer()
        base = "\n".join(
            "This is line number %d of a long note." % i for i in range(400)
        )
        # Seed the note without recording it as an undoable action, so the only
        # thing on the undo stack is the edit we make below.
        with buf.undo_disabled():
            buf.set_text(StyledText(base))
        return buf, base

    def test_undo_of_insert_preserves_viewport_mark(self):
        buf, base = self._long_buffer()

        # The user, scrolled down into the note, types something at the end.
        buf.insert(buf.get_end_iter(), " and the user typed this at the bottom")

        # Stand in for the viewport: a mark at the edit site, deep in the note,
        # far from both the top and the just-typed text at the end.
        anchor_offset = len(base) // 2
        self.assertGreater(anchor_offset, 0)
        view_mark = buf.create_mark(
            "viewport", buf.get_iter_at_offset(anchor_offset), True
        )

        buf.undo()

        new_offset = buf.get_iter_at_mark(view_mark).get_offset()
        # Pre-fix the full-buffer set_text() rebuild collapses the mark to 0
        # (the view jumps to the top of the note); post-fix the mark survives.
        self.assertGreater(
            new_offset,
            0,
            "Undo collapsed the viewport mark to the top of the note (bug 13268)",
        )

    def test_undo_of_delete_preserves_viewport_mark(self):
        buf, base = self._long_buffer()

        # The user, scrolled down, deletes a run of text near the end.
        end = buf.get_char_count()
        start_iter = buf.get_iter_at_offset(end - 20)
        end_iter = buf.get_iter_at_offset(end)
        buf.delete(start_iter, end_iter)

        anchor_offset = len(base) // 2
        view_mark = buf.create_mark(
            "viewport", buf.get_iter_at_offset(anchor_offset), True
        )

        buf.undo()

        new_offset = buf.get_iter_at_mark(view_mark).get_offset()
        self.assertGreater(
            new_offset,
            0,
            "Undo collapsed the viewport mark to the top of the note (bug 13268)",
        )


if __name__ == "__main__":
    unittest.main()
