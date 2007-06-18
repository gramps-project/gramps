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
MediaBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _MediaRef import MediaRef

#-------------------------------------------------------------------------
#
# MediaBase class
#
#-------------------------------------------------------------------------
class MediaBase:
    """
    Base class for storing media references
    """
    
    def __init__(self, source=None):
        """
        Create a new MediaBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: MediaBase
        """
        
        if source:
            self.media_list = [ MediaRef(mref) for mref in source.media_list ]
        else:
            self.media_list = []

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return [mref.serialize() for mref in self.media_list]

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.media_list = [MediaRef().unserialize(item) for item in data]

    def add_media_reference(self, media_ref):
        """
        Adds a L{MediaRef} instance to the object's media list.

        @param media_ref: L{MediaRef} instance to be added to the object's
            media list.
        @type media_ref: L{MediaRef}
        """
        self.media_list.append(media_ref)

    def get_media_list(self):
        """
        Returns the list of L{MediaRef} instances associated with the object.

        @returns: list of L{MediaRef} instances associated with the object
        @rtype: list
        """
        return self.media_list

    def set_media_list(self, media_ref_list):
        """
        Sets the list of L{MediaRef} instances associated with the object.
        It replaces the previous list.

        @param media_ref_list: list of L{MediaRef} instances to be assigned
            to the object.
        @type media_ref_list: list
        """
        self.media_list = media_ref_list

    def has_media_reference(self, obj_handle) :
        """
        Returns True if the object or any of it's child objects has reference
        to this media object handle.

        @param obj_handle: The media handle to be checked.
        @type obj_handle: str
        @return: Returns whether the object or any of it's child objects has reference to this media handle.
        @rtype: bool
        """
        return obj_handle in [media_ref.ref for media_ref in self.media_list]

    def remove_media_references(self, obj_handle_list):
        """
        Removes references to all media handles in the list.

        @param obj_handle_list: The list of media handles to be removed.
        @type obj_handle_list: list
        """
        new_media_list = [ media_ref for media_ref in self.media_list \
                                    if media_ref.ref not in obj_handle_list ]
        self.media_list = new_media_list

    def replace_media_references(self, old_handle, new_handle):
        """
        Replaces all references to old media handle with the new handle.

        @param old_handle: The media handle to be replaced.
        @type old_handle: str
        @param new_handle: The media handle to replace the old one with.
        @type new_handle: str
        """
        refs_list = [ media_ref.ref for media_ref in self.media_list ]
        n_replace = refs_list.count(old_handle)
        for ix_replace in xrange(n_replace):
            ix = refs_list.index(old_handle)
            self.media_list[ix].ref = new_handle
            refs_list[ix] = new_handle
