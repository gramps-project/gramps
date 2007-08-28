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
Source Reference class for GRAMPS
"""

__revision__ = "$Revision$"

from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _DateBase import DateBase
from _PrivacyBase import PrivacyBase
from _NoteBase import NoteBase
from _RefBase import RefBase

#-------------------------------------------------------------------------
#
# Source References for all primary objects
#
#-------------------------------------------------------------------------
class SourceRef(SecondaryObject, DateBase, PrivacyBase, NoteBase, RefBase):
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    CONF_VERY_HIGH = 4
    CONF_HIGH      = 3
    CONF_NORMAL    = 2
    CONF_LOW       = 1
    CONF_VERY_LOW  = 0

    def __init__(self, source=None):
        """creates a new SourceRef, copying from the source if present"""
        DateBase.__init__(self, source)
        PrivacyBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        if source:
            self.confidence = source.confidence
            self.page = source.page
        else:
            self.confidence = SourceRef.CONF_NORMAL
            self.page = ""

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (DateBase.serialize(self),
                PrivacyBase.serialize(self),
                NoteBase.serialize(self),
                self.confidence,
                RefBase.serialize(self),
                self.page)

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (date, privacy, note_list,
         self.confidence, ref, self.page) = data
        DateBase.unserialize(self, date)
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
        return [self.page]

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: List of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.ref:
            ret += [('Source', self.ref)]
        return ret

    def set_confidence_level(self, val):
        """Sets the confidence level"""
        self.confidence = val

    def get_confidence_level(self):
        """Returns the confidence level"""
        return self.confidence
        
    def set_page(self, page):
        """sets the page indicator of the SourceRef"""
        self.page = page

    def get_page(self):
        """gets the page indicator of the SourceRef"""
        return self.page

    def are_equal(self, other):
        """deprecated function - use are_equal instead"""
        warn( "Use is_equal instead of are_equal", DeprecationWarning, 2)
        return self.is_equal(other)
