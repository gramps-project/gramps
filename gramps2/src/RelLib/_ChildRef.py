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

# $Id$

"""
Child Reference class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BaseObject import BaseObject
from _PrivacyBase import PrivacyBase
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _RefBase import RefBase
from _ChildRefType import ChildRefType

#-------------------------------------------------------------------------
#
# Person References for Person/Family
#
#-------------------------------------------------------------------------
class ChildRef(BaseObject,PrivacyBase,SourceBase,NoteBase,RefBase):
    """
    Person reference class.

    This class is for keeping information about how the person relates
    to another person from the database, if not through family.
    Examples would be: godparent, friend, etc.
    """

    def __init__(self,source=None):
        BaseObject.__init__(self)
        PrivacyBase.__init__(self,source)
        SourceBase.__init__(self,source)
        NoteBase.__init__(self,source)
        RefBase.__init__(self)
        if source:
            self.frel = source.frel
            self.mrel = source.mrel
        else:
            self.frel = ChildRefType()
            self.mrel = ChildRefType()

    def serialize(self):
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                RefBase.serialize(self),
                self.frel.serialize(),
                self.mrel.serialize())

    def unserialize(self,data):
        (privacy,source_list,note,ref,frel,mrel) = data
        PrivacyBase.unserialize(self,privacy)
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)
        RefBase.unserialize(self,ref)
        self.frel.unserialize(frel)
        self.mrel.unserialize(mrel)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [str(self.frel), str(self.mrel)]

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

    def set_mother_relation(self,rel):
        """Sets relation between the person and mother"""
        self.mrel.set(rel)

    def get_mother_relation(self):
        """Returns the relation between the person and mother"""
        return self.mrel

    def set_father_relation(self,frel):
        """Sets relation between the person and father"""
        self.frel.set(frel)

    def get_father_relation(self):
        """Returns the relation between the person and father"""
        return self.frel
