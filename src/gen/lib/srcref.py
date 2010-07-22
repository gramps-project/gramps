#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
Source Reference class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.secondaryobj import SecondaryObject
from gen.lib.datebase import DateBase
from gen.lib.privacybase import PrivacyBase
from gen.lib.notebase import NoteBase
from gen.lib.refbase import RefBase
from gen.lib.const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Source References for all primary objects
#
#-------------------------------------------------------------------------
class SourceRef(SecondaryObject, DateBase, PrivacyBase, NoteBase, RefBase):
    """
    Source reference, containing detailed information about how a referenced 
    source relates to it.
    """
    
    CONF_VERY_HIGH = 4
    CONF_HIGH      = 3
    CONF_NORMAL    = 2
    CONF_LOW       = 1
    CONF_VERY_LOW  = 0

    def __init__(self, source=None):
        """Create a new SourceRef, copying from the source if present."""
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
        Convert the object to a serialized tuple of data.
        """
        return (DateBase.serialize(self),
                PrivacyBase.serialize(self),
                NoteBase.serialize(self),
                self.confidence,
                RefBase.serialize(self),
                self.page)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
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
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.page]

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.ref:
            ret += [('Source', self.ref)]
        return ret

    def is_equivalent(self, other):
        """
        Return if this source reference is equivalent, that is agreees in
        reference, source page and date, to other.

        :param other: The source reference to compare this one to.
        :rtype other: SourceRef
        ;returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.ref != other.ref or \
            self.page != other.page or \
            self.get_date_object() != other.get_date_object():
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this source reference.

        :param acquisition: The source reference to merge with the present one.
        :rtype acquisition: SourceRef
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        # merge confidence
        level_priority = [0, 4, 1, 3, 2]
        idx = min(level_priority.index(self.confidence),
                  level_priority.index(acquisition.confidence))
        self.confidence = level_priority[idx]

    def set_confidence_level(self, val):
        """Set the confidence level."""
        self.confidence = val

    def get_confidence_level(self):
        """Return the confidence level."""
        return self.confidence
        
    def set_page(self, page):
        """Set the page indicator of the SourceRef."""
        self.page = page

    def get_page(self):
        """Get the page indicator of the SourceRef."""
        return self.page

    def are_equal(self, other):
        """Deprecated function - use is_equal instead."""
        warn( "Use is_equal instead of are_equal", DeprecationWarning, 2)
        return self.is_equal(other)
