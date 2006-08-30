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
Source Reference class for GRAMPS
"""

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
class SourceRef(SecondaryObject,DateBase,PrivacyBase,NoteBase,RefBase):
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    CONF_VERY_HIGH = 4
    CONF_HIGH      = 3
    CONF_NORMAL    = 2
    CONF_LOW       = 1
    CONF_VERY_LOW  = 0

    def __init__(self,source=None):
        """creates a new SourceRef, copying from the source if present"""
        SecondaryObject.__init__(self)
        DateBase.__init__(self,source)
        PrivacyBase.__init__(self,source)
        NoteBase.__init__(self,source)
        RefBase.__init__(self,source)
        if source:
            self.confidence = source.confidence
            self.page = source.page
            self.text = source.text
        else:
            self.confidence = SourceRef.CONF_NORMAL
            self.page = ""
            self.text = ""

    def serialize(self):
        return (DateBase.serialize(self),
                PrivacyBase.serialize(self),
                NoteBase.serialize(self),
                self.confidence,
                RefBase.serialize(self),
                self.page,self.text)

    def unserialize(self,data):
        (date,privacy,note,
         self.confidence,ref,self.page,self.text) = data
        DateBase.unserialize(self,date)
        PrivacyBase.unserialize(self,privacy)
        NoteBase.unserialize(self,note)
        RefBase.unserialize(self,ref)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.page,self.text]
        #return [self.page,self.text,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        return [self.note]

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Source',self.ref)]
        else:
            return []

    def set_confidence_level(self,val):
        """Sets the confidence level"""
        self.confidence = val

    def get_confidence_level(self):
        """Returns the confidence level"""
        return self.confidence
        
    def set_page(self,page):
        """sets the page indicator of the SourceRef"""
        self.page = page

    def get_page(self):
        """gets the page indicator of the SourceRef"""
        return self.page

    def set_text(self,text):
        """sets the text related to the SourceRef"""
        self.text = text

    def get_text(self):
        """returns the text related to the SourceRef"""
        return self.text

    def are_equal(self,other):
        warn( "Use is_equal instead of are_equal", DeprecationWarning, 2)
        return self.is_equal(other)
