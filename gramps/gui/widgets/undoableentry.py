#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
#
# based on undoablebuffer Copyright (C) 2009  Florian Heinle
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

__all__ = ["UndoableEntry"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import warnings
import logging
_LOG = logging.getLogger(".widgets.undoableentry")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .undoablebuffer import Stack

class UndoableInsertEntry:
    """something that has been inserted into our Gtk.editable"""
    def __init__(self, text, length, position, editable):
        self.offset = position
        self.text = text
        #unicode char can have length > 1 as it points in the buffer
        charlength = len(text)
        self.length = charlength
        if charlength > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True

class UndoableDeleteEntry:
    """something that has been deleted from our textbuffer"""
    def __init__(self, editable, start, end):
        self.text = editable.get_chars(start, end)
        self.start = start
        self.end = end
        # need to find out if backspace or delete key has been used
        # so we don't mess up during redo
        insert = editable.get_position()
        if insert <= start:
            self.delete_key_used = True
        else:
            self.delete_key_used = False
        if self.end - self.start > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True

class UndoableEntry(Gtk.Entry):
    """
    The UndoableEntry is an Entry subclass with additional features.

    Additional features:
      - Undo and Redo on CTRL-Z/CTRL-SHIFT-Z
    """
    __gtype_name__ = 'UndoableEntry'

    insertclass = UndoableInsertEntry
    deleteclass = UndoableDeleteEntry

    #how many undo's are remembered
    undo_stack_size = 50

    def __init__(self):
        Gtk.Entry.__init__(self)
        self.undo_stack = Stack(self.undo_stack_size)
        self.redo_stack = []
        self.not_undoable_action = False
        self.undo_in_progress = False

        self.connect('insert-text', self._on_insert_text)
        self.connect('delete-text', self._on_delete_text)
        self.connect('key-press-event', self._on_key_press_event)

    def set_text(self, text):
        with warnings.catch_warnings():
            # Suppress warnings.  See bug #8029.
            # https://bugzilla.gnome.org/show_bug.cgi?id=644927
            warnings.simplefilter('ignore')
            Gtk.Entry.set_text(self, text)
        self.reset()

    def _on_key_press_event(self, widget, event):
        """Signal handler.
        Handle formatting undo/redo key press.

        """
        if ((Gdk.keyval_name(event.keyval) == 'Z') and
            (event.get_state() & Gdk.ModifierType.CONTROL_MASK) and
            (event.get_state() & Gdk.ModifierType.SHIFT_MASK)):
            self.redo()
            return True
        elif ((Gdk.keyval_name(event.keyval) == 'z') and
              (event.get_state() & Gdk.ModifierType.CONTROL_MASK)):
            self.undo()
            return True

        return False

    def __empty_redo_stack(self):
        self.redo_stack = []

    def _on_insert_text(self, editable, text, length, positionptr):
        def can_be_merged(prev, cur):
            """
            see if we can merge multiple inserts here

            will try to merge words or whitespace
            can't merge if prev and cur are not mergeable in the first place
            can't merge when user set the input bar somewhere else
            can't merge across word boundaries
            """

            WHITESPACE = (' ', '\t')
            if not cur.mergeable or not prev.mergeable:
                return False
            # offset is char offset, not byte, so length is the char length!
            elif cur.offset != (prev.offset + prev.length):
                return False
            elif cur.text in WHITESPACE and not prev.text in WHITESPACE:
                return False
            elif prev.text in WHITESPACE and not cur.text in WHITESPACE:
                return False
            return True

        if not self.undo_in_progress:
            self.__empty_redo_stack()
        if self.not_undoable_action:
            return
        undo_action = self.insertclass(text, length, editable.get_position(),
                                       editable)
        try:
            prev_insert = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_insert, self.insertclass):
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_insert, undo_action):
            prev_insert.length += undo_action.length
            prev_insert.text += undo_action.text
            self.undo_stack.append(prev_insert)
        else:
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)

    def _on_delete_text(self, editable, start, end):
        def can_be_merged(prev, cur):
            """
            see if we can merge multiple deletions here

            will try to merge words or whitespace
            can't merge if prev and cur are not mergeable in the first place
            can't merge if delete and backspace key were both used
            can't merge across word boundaries
            """

            WHITESPACE = (' ', '\t')
            if not cur.mergeable or not prev.mergeable:
                return False
            elif prev.delete_key_used != cur.delete_key_used:
                return False
            elif prev.start != cur.start and prev.start != cur.end:
                return False
            elif cur.text not in WHITESPACE and \
               prev.text in WHITESPACE:
                return False
            elif cur.text in WHITESPACE and \
               prev.text not in WHITESPACE:
                return False
            return True

        if not self.undo_in_progress:
            self.__empty_redo_stack()
        if self.not_undoable_action:
            return
        undo_action = self.deleteclass(editable, start, end)
        try:
            prev_delete = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_delete, self.deleteclass):
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_delete, undo_action):
            if prev_delete.start == undo_action.start: # delete key used
                prev_delete.text += undo_action.text
                prev_delete.end += (undo_action.end - undo_action.start)
            else: # Backspace used
                prev_delete.text = "%s%s" % (undo_action.text,
                                                     prev_delete.text)
                prev_delete.start = undo_action.start
            self.undo_stack.append(prev_delete)
        else:
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)

    def begin_not_undoable_action(self):
        """don't record the next actions

        toggles self.not_undoable_action"""
        self.not_undoable_action = True

    def end_not_undoable_action(self):
        """record next actions

        toggles self.not_undoable_action"""
        self.not_undoable_action = False

    def reset(self):
        """
        Resets buffer to initial state.
        """
        self.undo_stack = Stack(self.undo_stack_size)
        self.redo_stack[:] = []
        self.not_undoable_action = False
        self.undo_in_progress = False

    def undo(self):
        """undo inserts or deletions

        undone actions are being moved to redo stack"""
        if not self.undo_stack:
            return
        self.begin_not_undoable_action()
        self.undo_in_progress = True
        undo_action = self.undo_stack.pop()
        self.redo_stack.append(undo_action)
        if isinstance(undo_action, self.insertclass):
            self._undo_insert(undo_action)
        elif isinstance(undo_action, self.deleteclass):
            self._undo_delete(undo_action)
        else:
            self._handle_undo(undo_action)
        self.end_not_undoable_action()
        self.undo_in_progress = False

    def _undo_insert(self, undo_action):
        start = undo_action.offset
        stop = undo_action.offset + undo_action.length
        self.delete_text(start, stop)
        self.set_position(undo_action.offset)

    def _undo_delete(self, undo_action):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.insert_text(undo_action.text, undo_action.start)
        if undo_action.delete_key_used:
            self.set_position(undo_action.start)
        else:
            self.set_position(undo_action.end)

    def _handle_undo(self, undo_action):
        raise NotImplementedError

    def redo(self):
        """redo inserts or deletions

        redone actions are moved to undo stack"""
        if not self.redo_stack:
            return
        self.begin_not_undoable_action()
        self.undo_in_progress = True
        redo_action = self.redo_stack.pop()
        self.undo_stack.append(redo_action)
        if isinstance(redo_action, self.insertclass):
            self._redo_insert(redo_action)
        elif isinstance(redo_action, self.deleteclass):
            self._redo_delete(redo_action)
        else:
            self._handle_redo(redo_action)
        self.end_not_undoable_action()
        self.undo_in_progress = False

    def _redo_insert(self, redo_action):
        self.insert_text(redo_action.text, redo_action.offset)
        new_cursor_pos = redo_action.offset + redo_action.length
        self.set_position(new_cursor_pos)

    def _redo_delete(self, redo_action):
        start = redo_action.start
        stop = redo_action.end
        self.delete_text(start, stop)
        self.set_position(redo_action.start)

    def _handle_redo(self, redo_action):
        raise NotImplementedError
