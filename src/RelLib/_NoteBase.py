#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
NoteBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Note import Note

#-------------------------------------------------------------------------
#
# NoteBase class
#
#-------------------------------------------------------------------------
class NoteBase:
    """
    Base class for storing notes.
    """
    def __init__(self, source=None):
        """
        Create a new NoteBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: NoteBase
        """
        
        if source and source.note:
            text = source.note.get()
        else:
            text = ""
        self.note = Note(text)

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        if self.note == None:
            self.note = Note()
        return self.note.serialize()

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        if data is not None:
            self.note = Note().unserialize(data)

    def set_note(self, text):
        """
        Assigns the specified text to the associated note.

        @param text: Text of the note
        @type text: str
        """
        if not self.note:
            self.note = Note()
        self.note.set(text)

    def get_note(self):
        """
        Returns the text of the current note.

        @returns: the text of the current note
        @rtype: str
        """
        if self.note:
            return self.note.get()
        return ""

    def set_note_format(self, val):
        """
        Sets the note's format to the given value. The format indicates
        whether the text is flowed (wrapped) or preformatted.

        @param val: True indicates the text is flowed
        @type val: bool
        """
        if self.note:
            self.note.set_format(val)

    def get_note_format(self):
        """
        Returns the current note's format

        @returns: True indicates that the note should be flowed (wrapped)
        @rtype: bool
        """
        if self.note == None:
            return False
        else:
            return self.note.get_format()

    def set_note_object(self, note_obj):
        """
        Replaces the current L{Note} object associated with the object

        @param note_obj: New L{Note} object to be assigned
        @type note_obj: L{Note}
        """
        self.note = note_obj

    def get_note_object(self):
        """
        Returns the L{Note} instance associated with the object.

        @returns: L{Note} object assocated with the object
        @rtype: L{Note}
        """
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())
