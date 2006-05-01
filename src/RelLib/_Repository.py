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
Repository object for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn

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
class Repository(PrimaryObject,NoteBase,AddressBase,UrlBase):
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
        return (self.handle, self.gramps_id, self.type.serialize(),
                unicode(self.name),
                NoteBase.serialize(self),
                AddressBase.serialize(self),
                UrlBase.serialize(self),
                self.marker.serialize(), self.private)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Repository structure.
        """
        (self.handle, self.gramps_id, the_type, self.name, note,
         address_list, urls, marker, self.private) = data

        self.marker.unserialize(marker)
        self.type.unserialize(the_type)
        NoteBase.unserialize(self,note)
        AddressBase.unserialize(self,address_list)
        UrlBase.unserialize(self,urls)
        
    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.name,str(self.type)]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.address_list + self.urls
        if self.note:
            check_list.append(self.note)
        return check_list

    def has_source_reference(self,src_handle) :
        """
        Returns True if any of the child objects has reference
        to this source handle.

        @param src_handle: The source handle to be checked.
        @type src_handle: str
        @return: Returns whether any of it's child objects has reference to this source handle.
        @rtype: bool
        """
        return False

    def remove_source_references(self,src_handle_list):
        """
        Removes references to all source handles in the list
        in all child objects.

        @param src_handle_list: The list of source handles to be removed.
        @type src_handle_list: list
        """
        pass

    def replace_source_references(self,old_handle,new_handle):
        """
        Replaces references to source handles in the list
        in this object and all child objects.

        @param old_handle: The source handle to be replaced.
        @type old_handle: str
        @param new_handle: The source handle to replace the old one with.
        @type new_handle: str
        """
        pass

    def set_type(self,the_type):
        """
        @param type: descriptive type of the Repository
        @type type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        @returns: the descriptive type of the Repository
        @rtype: str
        """
        return self.type

    def set_name(self,name):
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
