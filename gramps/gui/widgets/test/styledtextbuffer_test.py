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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Unit test for ``StyledTextBuffer._apply_style_to_selection`` — Mantis 3214.

Mantis 0003214: in the Note editor, changing a (preformatted) note's font
size away from the default (10) and then back to 10 does **not** clear the
FONTSIZE style. ``_apply_style_to_selection`` removed the old FONTSIZE tag
and then *unconditionally* applied a new explicit ``FONTSIZE=10`` tag — even
though 10 is ``StyledTextTagType.STYLE_DEFAULT[FONTSIZE]``. The note looks
fine in the editor, but reports apply that explicit size as an absolute
override on top of the report's Preformatted paragraph style, so the rendered
size differs from a note whose size was never touched, and the user can never
get back to the original.

The fix upholds the same invariant the buffer's own clear path already honours
(``clear_selection`` removes a tag only when ``value != STYLE_DEFAULT[style]``,
``gramps/gui/widgets/styledtextbuffer.py``): the apply path removes any prior
tag for the style and then applies an explicit tag **only** when the value
differs from the style default. Setting a value equal to the default therefore
leaves the selection in the same tagged state as if the style had never been
applied.

The test drives the production public apply path
(``StyledTextBuffer.apply_style`` → ``_apply_style_to_selection``) on a real
buffer and inspects the resulting :class:`.StyledText` tags. A ``StyledTextBuffer``
is a ``Gtk.TextBuffer`` subclass (not a widget), so it constructs without a
display; no GTK main loop or X server is required.
"""

from __future__ import annotations

import unittest

# Gramps targets GTK 3 throughout (see ``gramps/grampsapp.py``). Pin the
# introspected version BEFORE any ``gramps.gui`` import so the widgets module
# chain loads against the right ABI on a headless runner.
import gi  # noqa: E402

gi.require_version("Gtk", "3.0")  # noqa: E402

from gramps.gen.lib import StyledText, StyledTextTagType  # noqa: E402
from gramps.gui.widgets.styledtextbuffer import StyledTextBuffer  # noqa: E402

FONTSIZE = StyledTextTagType.FONTSIZE
FONTFACE = StyledTextTagType.FONTFACE


# -----------------------------------------------------------
#
# StyledTextBufferDefaultStyleTest
#
# -----------------------------------------------------------
class StyledTextBufferDefaultStyleTest(unittest.TestCase):
    """Regression test for Mantis 3214 — default value must leave no tag."""

    def _new_buffer(self, text: str = "hello world") -> StyledTextBuffer:
        buf = StyledTextBuffer()
        buf.set_text(StyledText(text))
        buf.select_range(buf.get_start_iter(), buf.get_end_iter())
        return buf

    def _tags_for(self, buf: StyledTextBuffer, style: int):
        """Explicit :class:`.StyledTextTag`s for ``style`` in the buffer's text."""
        return [tag for tag in buf.get_text().get_tags() if int(tag.name) == style]

    def test_fontsize_default_leaves_no_explicit_tag(self):
        """FONTSIZE bumped away and back to the default clears the tag (the bug)."""
        default = StyledTextTagType.STYLE_DEFAULT[FONTSIZE]
        buf = self._new_buffer()

        # Away from the default, then back to it — the Mantis 3214 sequence.
        buf.apply_style(FONTSIZE, 12)
        buf.apply_style(FONTSIZE, default)

        msg = (
            f"setting FONTSIZE back to its default ({default}) must leave no "
            "explicit FONTSIZE tag — an override that differs from an unchanged note"
        )
        self.assertEqual(self._tags_for(buf, FONTSIZE), [], msg)

    def test_fontsize_default_matches_untouched_note(self):
        """A back-to-default note carries the same tags as one never changed."""
        default = StyledTextTagType.STYLE_DEFAULT[FONTSIZE]

        touched = self._new_buffer()
        touched.apply_style(FONTSIZE, 18)
        touched.apply_style(FONTSIZE, default)

        untouched = self._new_buffer()

        self.assertEqual(
            [(int(t.name), t.value) for t in touched.get_text().get_tags()],
            [(int(t.name), t.value) for t in untouched.get_text().get_tags()],
        )

    def test_fontsize_nondefault_still_tagged(self):
        """A genuine (non-default) size is still recorded — no over-removal."""
        buf = self._new_buffer()
        buf.apply_style(FONTSIZE, 12)

        tags = self._tags_for(buf, FONTSIZE)
        self.assertEqual([(int(t.name), t.value) for t in tags], [(FONTSIZE, 12)])

    def test_fontface_default_leaves_no_explicit_tag(self):
        """The str-typed branch upholds the same invariant (FONTFACE)."""
        default = StyledTextTagType.STYLE_DEFAULT[FONTFACE]
        buf = self._new_buffer()

        buf.apply_style(FONTFACE, "Serif")
        buf.apply_style(FONTFACE, default)

        self.assertEqual(self._tags_for(buf, FONTFACE), [])


if __name__ == "__main__":
    unittest.main()
