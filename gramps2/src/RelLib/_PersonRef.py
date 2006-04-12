#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006  Donald N. Allingham
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

# $Id: _EventRef.py 6194 2006-03-22 23:03:57Z dallingham $

"""
Person Reference class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _PrivateSourceNote import PrivateSourceNote

#-------------------------------------------------------------------------
#
# Person References for Person/Family
#
#-------------------------------------------------------------------------
class PersonRef(PrivateSourceNote):
    """
    Person reference class.

    This class is for keeping information about how the person relates
    to another person from the database, if not through family.
    Examples would be: godparent, friend, etc.
    """

    def __init__(self,source=None):
        PrivateSourceNote.__init__(self,source)
        if source:
            self.ref = source.ref
            self.rel = source.rel
        else:
            self.ref = None
            self.rel = ''

    def serialize(self):
        return (PrivateSourceNote.serialize(self),self.ref,self.rel)

    def unserialize(self,data):
        (psn,self.ref,self.rel) = data
        PrivateSourceNote.unserialize(self,psn)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.rel]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Person',self.ref)]
        else:
            return []

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_relation(self,rel):
        """Sets relation to a person"""
        self.rel = rel

    def get_relation(self):
        """Returns the relation to a person"""
        return self.rel

    def set_reference_handle(self,obj_id):
        self.ref = obj_id

    def get_reference_handle(self):
        return self.ref
