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
Repository object for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _PrimaryObject import PrimaryObject
from _NoteBase import NoteBase
from _AddressBase import AddressBase
from _UrlBase import UrlBase
from _RepositoryType import RepositoryType

#-------------------------------------------------------------------------
#
# Repository class
#
#-------------------------------------------------------------------------
class Repository(NoteBase, AddressBase, UrlBase, PrimaryObject):
    """A location where collections of Sources are found"""
    
    def __init__(self):
        """creates a new Repository instance"""
        PrimaryObject.__init__(self)
        NoteBase.__init__(self)
        AddressBase.__init__(self)
        UrlBase.__init__(self)
        self.type = RepositoryType()
        self.name = ""

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (self.handle, self.gramps_id, self.type.serialize(),
                unicode(self.name),
                NoteBase.serialize(self),
                AddressBase.serialize(self),
                UrlBase.serialize(self),
                self.change, self.marker.serialize(), self.private)

    def unserialize(self, data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Repository structure.
        """
        (self.handle, self.gramps_id, the_type, self.name, note_list,
         address_list, urls, self.change, marker, self.private) = data

        self.marker.unserialize(marker)
        self.type.unserialize(the_type)
        NoteBase.unserialize(self, note_list)
        AddressBase.unserialize(self, address_list)
        UrlBase.unserialize(self, urls)
        
    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.name, str(self.type)]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        return self.address_list + self.urls

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: List of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        return self.get_referenced_note_handles()

    def set_type(self, the_type):
        """
        @param the_type: descriptive type of the Repository
        @type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        @returns: the descriptive type of the Repository
        @rtype: str
        """
        return self.type

    def set_name(self, name):
        """
        @param name: descriptive name of the Repository
        @type name: str
        """
        self.name = name

    def get_name(self):
        """
        @returns: the descriptive name of the Repository
        @rtype: str
        """
        return self.name
