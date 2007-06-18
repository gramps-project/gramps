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
SourceBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SourceRef import SourceRef

#-------------------------------------------------------------------------
#
# SourceBase classes
#
#-------------------------------------------------------------------------
class SourceBase:
    """
    Base class for storing source references
    """
    
    def __init__(self, source=None):
        """
        Create a new SourceBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: SourceBase
        """
        if source:
            self.source_list = [SourceRef(sref) for sref in source.source_list]
        else:
            self.source_list = []

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return [sref.serialize() for sref in self.source_list]

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.source_list = [SourceRef().unserialize(item) for item in data]

    def add_source_reference(self, src_ref) :
        """
        Adds a source reference to this object.

        @param src_ref: The source reference to be added to the
            SourceNote's list of source references.
        @type src_ref: L{SourceRef}
        """
        self.source_list.append(src_ref)

    def get_source_references(self) :
        """
        Returns the list of source references associated with the object.

        @return: Returns the list of L{SourceRef} objects assocated with
            the object.
        @rtype: list
        """
        return self.source_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return []

    def has_source_reference(self, src_handle) :
        """
        Returns True if the object or any of it's child objects has reference
        to this source handle.

        @param src_handle: The source handle to be checked.
        @type src_handle: str
        @return: Returns whether the object or any of it's child objects has reference to this source handle.
        @rtype: bool
        """
        for src_ref in self.source_list:
            # Using direct access here, not the getter method -- efficiency!
            if src_ref.ref == src_handle:
                return True

        for item in self.get_sourcref_child_list():
            if item.has_source_reference(src_handle):
                return True

        return False

    def remove_source_references(self, src_handle_list):
        """
        Removes references to all source handles in the list
        in this object and all child objects.

        @param src_handle_list: The list of source handles to be removed.
        @type src_handle_list: list
        """
        new_source_list = [ src_ref for src_ref in self.source_list \
                                    if src_ref.ref not in src_handle_list ]
        self.source_list = new_source_list

        for item in self.get_sourcref_child_list():
            item.remove_source_references(src_handle_list)

    def replace_source_references(self, old_handle, new_handle):
        """
        Replaces references to source handles in the list
        in this object and all child objects.

        @param old_handle: The source handle to be replaced.
        @type old_handle: str
        @param new_handle: The source handle to replace the old one with.
        @type new_handle: str
        """
        refs_list = [ src_ref.ref for src_ref in self.source_list ]
        n_replace = refs_list.count(old_handle)
        for ix_replace in xrange(n_replace):
            ix = refs_list.index(old_handle)
            self.source_list[ix].ref = new_handle
            refs_list[ix] = new_handle
            
        for item in self.get_sourcref_child_list():
            item.replace_source_references(old_handle, new_handle)

    def set_source_reference_list(self, src_ref_list) :
        """
        Assigns the passed list to the object's list of source references.

        @param src_ref_list: List of source references to ba associated
            with the object
        @type src_ref_list: list of L{SourceRef} instances
        """
        self.source_list = src_ref_list
