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
Repository Reference class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BaseObject import BaseObject
from _NoteBase import NoteBase
from _RefBase import RefBase

#-------------------------------------------------------------------------
#
# Repository Reference for Sources
#
#-------------------------------------------------------------------------
class RepoRef(BaseObject,NoteBase,RefBase):
    """
    Repository reference class.
    """

    UNKNOWN    = -1
    CUSTOM     = 0
    AUDIO      = 1
    BOOK       = 2
    CARD       = 3
    ELECTRONIC = 4
    FICHE      = 5
    FILM       = 6
    MAGAZINE   = 7
    MANUSCRIPT = 8
    MAP        = 9
    NEWSPAPER  = 10
    PHOTO      = 11
    TOMBSTONE  = 12
    VIDEO      = 13

    def __init__(self,source=None):
        BaseObject.__init__(self)
        NoteBase.__init__(self)
        RefBase.__init__(self)
        if source:
            self.call_number = source.call_number
            self.media_type = source.media_type
        else:
            self.call_number = ""
            self.media_type = (RepoRef.CUSTOM,"")

    def serialize(self):
        return (
            NoteBase.serialize(self),
            RefBase.serialize(self),
            self.call_number,self.media_type)

    def unserialize(self,data):
        (note,ref,self.call_number,self.media_type) = data
        NoteBase.unserialize(self,note)
        RefBase.unserialize(self,ref)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.call_number,self.media_type[1]]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        if self.note:
            return [self.note]
        return []

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Repository',self.ref)]
        else:
            return []

    def set_call_number(self,number):
        self.call_number = number

    def get_call_number(self):
        return self.call_number

    def get_media_type(self):
        return self.media_type

    def set_media_type(self,media_type):
        self.media_type = media_type
