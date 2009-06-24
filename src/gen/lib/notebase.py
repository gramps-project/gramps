#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
NoteBase class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# NoteBase class
#
#-------------------------------------------------------------------------
class NoteBase(object):
    """
    Base class for storing notes.

    Starting in 3.0 branch, the objects may have multiple notes.
    Internally, this class maintains a list of Note handles,
    as a note_list attribute of the NoteBase object.
    """
    def __init__(self, source=None):
        """
        Create a new NoteBase, copying from source if not None.
        
        :param source: Object used to initialize the new object
        :type source: NoteBase
        """
        
        if source:
            self.note_list = [handle for handle in source.note_list]
        else:
            self.note_list = []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.note_list

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.note_list = [handle for handle in data]

    def add_note(self, handle):
        """
        Add the :class:`~gen.lib.note.Note` handle to the list of note handles.

        :param handle: :class:`~gen.lib.note.Note` handle to add the list of notes
        :type handle: str

        :returns: True if handle was added, False if it already was in the list
        :rtype: bool
        """
        if handle in self.note_list:
            return False
        else:
            self.note_list.append(handle)
            return True

    def remove_note(self, handle):
        """
        Remove the specified handle from the list of note handles, and all
        secondary child objects.

        :param handle: :class:`~gen.lib.note.Note` handle to remove from the list of notes
        :type handle: str
        """
        if handle in self.note_list:
            self.note_list.remove(handle)
        for item in self.get_note_child_list():
            item.remove_note(handle)
    
    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.
        
        All methods which inherit from NoteBase and have other child objects
        with notes, should return here a list of child objects which are 
        NoteBase

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return []

    def get_note_list(self):
        """
        Return the list of :class:`~gen.lib.note.Note` handles associated with the object.

        :returns: The list of :class:`~gen.lib.note.Note` handles
        :rtype: list
        """
        return self.note_list

    def set_note_list(self, note_list):
        """
        Assign the passed list to be object's list of :class:`~gen.lib.note.Note` handles.

        :param note_list: List of :class:`~gen.lib.note.Note` handles to be set on the object
        :type note_list: list
        """
        self.note_list = note_list

    def get_referenced_note_handles(self):
        """
        Return the list of (classname, handle) tuples for all referenced notes.
        
        This method should be used to get the :class:`~gen.lib.note.Note` portion of the list
        by objects that store note lists.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return [('Note', handle) for handle in self.note_list]
