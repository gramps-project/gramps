#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
Media Reference class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.secondaryobj import SecondaryObject
from gen.lib.privacybase import PrivacyBase
from gen.lib.citationbase import CitationBase
from gen.lib.notebase import NoteBase
from gen.lib.refbase import RefBase
from gen.lib.attrbase import AttributeBase
from gen.lib.const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# MediaObject References for Person/Place/Source
#
#-------------------------------------------------------------------------
class MediaRef(SecondaryObject, PrivacyBase, CitationBase, NoteBase, RefBase,
               AttributeBase):
    """Media reference class."""
    def __init__(self, source=None):
        PrivacyBase.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        AttributeBase.__init__(self, source)

        if source:
            self.rect = source.rect
        else:
            self.rect = None

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                AttributeBase.serialize(self),
                RefBase.serialize(self),
                self.rect)

    def to_struct(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return {"private": PrivacyBase.serialize(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "attribute_list": AttributeBase.to_struct(self),
                "ref": RefBase.to_struct(self),
                "rect": self.rect}

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, citation_list, note_list,attribute_list,ref,self.rect) = data
        PrivacyBase.unserialize(self, privacy)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        AttributeBase.unserialize(self, attribute_list)
        RefBase.unserialize(self, ref)
        return self

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer Citations.

        :returns: Returns the list of child secondary child objects that may 
                refer Citations.
        :rtype: list
        """
        return self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.attribute_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles() + \
                self.get_referenced_citation_handles()
        if self.ref:
            ret += [('MediaObject', self.ref)]
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def is_equivalent(self, other):
        """
        Return if this object reference is equivalent, that is agrees in
        reference and region, to other.

        :param other: The object reference to compare this one to.
        :rtype other: MediaRef
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.ref != other.ref or self.rect != other.rect:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this object reference.

        Lost: hlink and region or acquisition.

        :param acquisition: The object reference to merge with the present one.
        :rtype acquisition: MediaRef
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_note_list(acquisition)

    def set_rectangle(self, coord):
        """Set subsection of an image."""
        self.rect = coord

    def get_rectangle(self):
        """Return the subsection of an image."""
        return self.rect
