#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Florian Heinle
# Copyright (C) 2010  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Benny Malengier
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
__all__ = ["UndoableBuffer"]

# Originally LGLP from:
# http://bitbucket.org/tiax/gtk-textbuffer-with-undo/
# Please send bugfixes and comments upstream to Florian

from gi.repository import Gtk

class Stack(list):
    """
    Very simple stack implementation that cannot grow beyond an at init
    determined size.
    Inherits from list.
    Only append checks if this is really the case!
    """
    def __init__(self, stack_size=None):
        super(Stack, self).__init__()
        self.stack_size = stack_size
    def append(self, item):
        if self.stack_size and len(self) == self.stack_size:
            self.pop(0)
        return super(Stack, self).append(item)

class UndoableInsert:
    """something that has been inserted into our textbuffer"""
    def __init__(self, text_iter, text, length, text_buffer):
        self.offset = text_iter.get_offset()
        self.text = str(text)
        #unicode char can have length > 1 as it points in the buffer
        charlength = len(str(text))
        self.length = charlength
        if charlength > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True
        self.tags = None

class UndoableDelete:
    """something that has been deleted from our textbuffer"""
    def __init__(self, text_buffer, start_iter, end_iter):
        self.text = str(text_buffer.get_text(start_iter, end_iter, True))
        self.start = start_iter.get_offset()
        self.end = end_iter.get_offset()
        # need to find out if backspace or delete key has been used
        # so we don't mess up during redo
        insert_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
        if insert_iter.get_offset() <= self.start:
            self.delete_key_used = True
        else:
            self.delete_key_used = False
        if self.end - self.start > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True
        self.tags = None

class UndoableBuffer(Gtk.TextBuffer):
    """text buffer with added undo capabilities

    designed as a drop-in replacement for gtksourceview,
    at least as far as undo is concerned"""
    insertclass = UndoableInsert
    deleteclass = UndoableDelete

    #how many undo's are remembered
    undo_stack_size = 700

    def __init__(self):
        """
        we'll need empty stacks for undo/redo and some state keeping
        """
        Gtk.TextBuffer.__init__(self)
        self.undo_stack = Stack(self.undo_stack_size)
        self.redo_stack = []
        self.not_undoable_action = False
        self.undo_in_progress = False
        self.connect('insert-text', self.on_insert_text_undoable)
        self.connect('delete-range', self.on_delete_range_undoable)

    @property
    def can_undo(self):
        return bool(self.undo_stack)

    @property
    def can_redo(self):
        return bool(self.redo_stack)

    def _empty_redo_stack(self):
        self.redo_stack = []

    def on_insert_text_undoable(self, textbuffer, text_iter, text, length):
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
            elif cur.offset != (prev.offset + prev.length):
                return False
            elif cur.text in WHITESPACE and not prev.text in WHITESPACE:
                return False
            elif prev.text in WHITESPACE and not cur.text in WHITESPACE:
                return False
            return True

        if not self.undo_in_progress:
            self._empty_redo_stack()
        if self.not_undoable_action:
            return
        undo_action = self.insertclass(text_iter, text, length, textbuffer)
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

    def on_delete_range_undoable(self, text_buffer, start_iter, end_iter):
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
            self._empty_redo_stack()
        if self.not_undoable_action:
            return
        undo_action = self.deleteclass(text_buffer, start_iter, end_iter)
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
        start = self.get_iter_at_offset(undo_action.offset)
        stop = self.get_iter_at_offset(
            undo_action.offset + undo_action.length
        )
        self.delete(start, stop)
        self.place_cursor(self.get_iter_at_offset(undo_action.offset))

    def _undo_delete(self, undo_action):
        start = self.get_iter_at_offset(undo_action.start)
        self.insert(start, undo_action.text)
        if undo_action.delete_key_used:
            self.place_cursor(self.get_iter_at_offset(undo_action.start))
        else:
            self.place_cursor(self.get_iter_at_offset(undo_action.end))

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
        self.place_cursor(self.get_iter_at_offset(redo_action.start))

    def _handle_redo(self, redo_action):
        raise NotImplementedError

## for test, run script as
## PYTHONPATH=$PYTHONPATH:~/gramps/trunk/src/ python gui/widgets/undoablebuffer.py
if __name__ == '__main__':
    test = Stack(5)
    if test:
        print('WRONG: test is empty')
    else:
        print('CORRECT: test is empty')

    test.append(0);test.append(1);test.append(2);test.append(3);test.append(4);
    print('5 inserts', test)
    test.append(5);test.append(6);test.append(7);test.append(8);test.append(9);
    print('5 more inserts', test)
    print('last element', test[-1])
