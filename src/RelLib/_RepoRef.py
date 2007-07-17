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
Repository Reference class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _PrivacyBase import PrivacyBase
from _NoteBase import NoteBase
from _RefBase import RefBase
from _SourceMediaType import SourceMediaType

#-------------------------------------------------------------------------
#
# Repository Reference for Sources
#
#-------------------------------------------------------------------------
class RepoRef(SecondaryObject, PrivacyBase, NoteBase, RefBase):
    """
    Repository reference class.
    """

    def __init__(self, source=None):
        SecondaryObject.__init__(self)
        PrivacyBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        if source:
            self.call_number = source.call_number
            self.media_type = source.media_type
        else:
            self.call_number = ""
            self.media_type = SourceMediaType()

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (
            NoteBase.serialize(self),
            RefBase.serialize(self),
            self.call_number, self.media_type.serialize(),
            PrivacyBase.serialize(self),
            )

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (note_list, ref, self.call_number, media_type, privacy) = data
        self.media_type.unserialize(media_type)
        PrivacyBase.unserialize(self, privacy)
        NoteBase.unserialize(self, note_list)
        RefBase.unserialize(self, ref)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.call_number, str(self.media_type)]

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: List of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.ref:
            ret += [('Repository', self.ref)]
        return ret

    def set_call_number(self, number):
        self.call_number = number

    def get_call_number(self):
        return self.call_number

    def get_media_type(self):
        return self.media_type

    def set_media_type(self, media_type):
        self.media_type.set(media_type)
