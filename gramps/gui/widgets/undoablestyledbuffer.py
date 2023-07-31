#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Florian Heinle
# Copyright (C) 2010  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010  Benny Malengier
# Copyright (C) 2014  Vassilii Khachaturov
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

"""
gtk textbuffer with undo functionality
"""

__all__ = ["UndoableStyledBuffer"]

from contextlib import contextmanager

from gi.repository import Gtk

from gramps.gen.lib.styledtext import StyledText
from .undoablebuffer import UndoableInsert, UndoableDelete
from .styledtextbuffer import StyledTextBuffer


class UndoableInsertStyled(UndoableInsert):
    """something that has been inserted into our styledtextbuffer"""

    def __init__(self, text_iter, text, length, text_buffer):
        # we obtain the buffer before the text has been inserted
        UndoableInsert.__init__(self, text_iter, text, length, text_buffer)
        self.tags = text_buffer.get_text(
            text_buffer.get_start_iter(), text_buffer.get_end_iter(), True
        ).get_tags()
        self.tagsafter = None


class UndoableDeleteStyled(UndoableDelete):
    def __init__(self, text_buffer, start_iter, end_iter):
        # we obtain the buffer before the text has been deleted
        UndoableDelete.__init__(self, text_buffer, start_iter, end_iter)
        self.tags = text_buffer.get_text(
            text_buffer.get_start_iter(), text_buffer.get_end_iter(), True
        ).get_tags()


class UndoableApplyStyle:
    """a style has been applied to our textbuffer"""

    def __init__(self, text_buffer, tag, start, end):
        self.offset = text_buffer.get_iter_at_mark(
            text_buffer.get_insert()
        ).get_offset()

        self.mergeable = False
        self.tags = text_buffer.get_text(
            text_buffer.get_start_iter(), text_buffer.get_end_iter(), True
        ).get_tags()
        #
        self.tags_after = None
        self.offset_after = None

    def set_after(self, tags, offset):
        self.tags_after = tags
        self.offset_after = offset


class UndoableStyledBuffer(StyledTextBuffer):
    """text buffer with added undo capabilities for styledtextbuffer

    designed as a drop-in replacement for gtksourceview,
    at least as far as undo is concerned"""

    insertclass = UndoableInsertStyled
    deleteclass = UndoableDeleteStyled

    def __init__(self):
        StyledTextBuffer.__init__(self)
        self.connect("apply-tag", self.on_tag_insert_undoable)
        self.connect_after("apply-tag", self.on_tag_afterinsert_undoable)

    @contextmanager
    def undo_disabled(self):
        """
        Assures that not_undoable_action is False during the context.

        Usage example (see gramps/gui/widgets/styledtexteditor.py)::

            with self.buffer.undo_disabled():
                ... # heavy stuff like spell checking
        """
        oldflag = self.not_undoable_action
        self.not_undoable_action = True
        try:
            yield
        except:
            raise
        finally:
            self.not_undoable_action = oldflag

    def on_tag_insert_undoable(self, buffer, tag, start, end):
        if not self.undo_in_progress:
            self._empty_redo_stack()
        if self.not_undoable_action:
            return
        if end.get_offset() - start.get_offset() == 1:
            # only store this 1 character tag if in a different place
            if (
                self.undo_stack
                and isinstance(self.undo_stack[-1], UndoableInsertStyled)
                and self.undo_stack[-1].offset + self.undo_stack[-1].length
                == end.get_offset()
            ):
                return
        undo_action = UndoableApplyStyle(buffer, tag, start, end)
        self.undo_stack.append(undo_action)

    def on_tag_afterinsert_undoable(self, buffer, tag, start, end):
        if self.not_undoable_action:
            return
        if not self.undo_stack or not isinstance(
            self.undo_stack[-1], UndoableApplyStyle
        ):
            return
        self.undo_stack[-1].set_after(
            buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), True
            ).get_tags(),
            buffer.get_iter_at_mark(buffer.get_insert()).get_offset(),
        )

    def _undo_insert(self, undo_action):
        start = self.get_iter_at_offset(undo_action.offset)
        stop = self.get_iter_at_offset(undo_action.offset + undo_action.length)
        self.delete(start, stop)
        # the text is correct again, now we create correct styled text
        s_text = StyledText(
            Gtk.TextBuffer.get_text(
                self, self.get_start_iter(), self.get_end_iter(), True
            ),
            undo_action.tags,
        )
        self.set_text(s_text)
        self.place_cursor(self.get_iter_at_offset(undo_action.offset))

    def _undo_delete(self, undo_action):
        start = self.get_iter_at_offset(undo_action.start)
        self.insert(start, undo_action.text)
        # the text is correct again, now we create correct styled text
        s_text = StyledText(
            Gtk.TextBuffer.get_text(
                self, self.get_start_iter(), self.get_end_iter(), True
            ),
            undo_action.tags,
        )
        self.set_text(s_text)
        if undo_action.delete_key_used:
            self.place_cursor(self.get_iter_at_offset(undo_action.start))
        else:
            self.place_cursor(self.get_iter_at_offset(undo_action.end))

    def _redo_insert(self, redo_action):
        s_text = StyledText(
            Gtk.TextBuffer.get_text(
                self, self.get_start_iter(), self.get_end_iter(), True
            ),
            redo_action.tags,
        )
        self.set_text(s_text)
        start = self.get_iter_at_offset(redo_action.offset)
        self.insert(start, redo_action.text)
        new_cursor_pos = self.get_iter_at_offset(
            redo_action.offset + redo_action.length
        )
        self.place_cursor(new_cursor_pos)

    def _redo_delete(self, redo_action):
        start = self.get_iter_at_offset(redo_action.start)
        stop = self.get_iter_at_offset(redo_action.end)
        self.delete(start, stop)
        # the text is correct again, now we create correct styled text
        # s_text = StyledText(Gtk.TextBuffer.get_text(self,
        #    self.get_start_iter(), self.get_end_iter(), True), redo_action.tags)
        # self.set_text(s_text)
        self.place_cursor(self.get_iter_at_offset(redo_action.start))

    def _handle_undo(self, undo_action):
        """undo of apply of style"""
        s_text = StyledText(
            Gtk.TextBuffer.get_text(
                self, self.get_start_iter(), self.get_end_iter(), True
            ),
            undo_action.tags,
        )
        self.set_text(s_text)
        self.place_cursor(self.get_iter_at_offset(undo_action.offset))

    def _handle_redo(self, redo_action):
        """redo of apply of style"""
        s_text = StyledText(
            Gtk.TextBuffer.get_text(
                self, self.get_start_iter(), self.get_end_iter(), True
            ),
            redo_action.tags_after,
        )
        self.set_text(s_text)
        self.place_cursor(self.get_iter_at_offset(redo_action.offset_after))
