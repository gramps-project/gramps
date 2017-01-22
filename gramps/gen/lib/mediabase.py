#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
MediaBase class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .mediaref import MediaRef
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# MediaBase class
#
#-------------------------------------------------------------------------
class MediaBase:
    """
    Base class for storing media references.
    """

    def __init__(self, source=None):
        """
        Create a new MediaBase, copying from source if not None.

        :param source: Object used to initialize the new object
        :type source: MediaBase
        """
        self.media_list = list(map(MediaRef, source.media_list)) if source else []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [mref.serialize() for mref in self.media_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.media_list = [MediaRef().unserialize(item) for item in data]
        return self

    def add_media_reference(self, media_ref):
        """
        Add a :class:`~.mediaref.MediaRef` instance to the object's media list.

        :param media_ref: :class:`~.mediaref.MediaRef` instance to be added to
                          the object's media list.
        :type media_ref: :class:`~.mediaref.MediaRef`
        """
        self.media_list.append(media_ref)

    def get_media_list(self):
        """
        Return the list of :class:`~.mediaref.MediaRef` instances associated
        with the object.

        :returns: list of :class:`~.mediaref.MediaRef` instances associated
                  with the object
        :rtype: list
        """
        return self.media_list

    def set_media_list(self, media_ref_list):
        """
        Set the list of :class:`~.mediaref.MediaRef` instances associated with
        the object. It replaces the previous list.

        :param media_ref_list: list of :class:`~.mediaref.MediaRef` instances
                               to be assigned to the object.
        :type media_ref_list: list
        """
        self.media_list = media_ref_list

    def _merge_media_list(self, acquisition):
        """
        Merge the list of media references from acquisition with our own.

        :param acquisition: the media list of this object will be merged with
                            the current media reference list.
        :rtype acquisition: MediaBase
        """
        media_list = self.media_list[:]
        for addendum in acquisition.get_media_list():
            for obj in media_list:
                equi = obj.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    obj.merge(addendum)
                    break
            else:
                self.media_list.append(addendum)

    def has_media_reference(self, obj_handle):
        """
        Return True if the object or any of it's child objects has reference
        to this media object handle.

        :param obj_handle: The media handle to be checked.
        :type obj_handle: str
        :returns: Returns whether the object or any of it's child objects has
                  reference to this media handle.
        :rtype: bool
        """
        return obj_handle in [media_ref.ref for media_ref in self.media_list]

    def remove_media_references(self, obj_handle_list):
        """
        Remove references to all media handles in the list.

        :param obj_handle_list: The list of media handles to be removed.
        :type obj_handle_list: list
        """
        new_media_list = [media_ref for media_ref in self.media_list
                          if media_ref.ref not in obj_handle_list]
        self.media_list = new_media_list

    def replace_media_references(self, old_handle, new_handle):
        """
        Replace all references to old media handle with the new handle and
        merge equivalent entries.

        :param old_handle: The media handle to be replaced.
        :type old_handle: str
        :param new_handle: The media handle to replace the old one with.
        :type new_handle: str
        """
        refs_list = [media_ref.ref for media_ref in self.media_list]
        new_ref = None
        if new_handle in refs_list:
            new_ref = self.media_list[refs_list.index(new_handle)]
        n_replace = refs_list.count(old_handle)
        for ix_replace in range(n_replace):
            idx = refs_list.index(old_handle)
            self.media_list[idx].ref = new_handle
            refs_list[idx] = new_handle
            if new_ref:
                media_ref = self.media_list[idx]
                equi = new_ref.is_equivalent(media_ref)
                if equi != DIFFERENT:
                    if equi == EQUAL:
                        new_ref.merge(media_ref)
                    self.media_list.pop(idx)
                    refs_list.pop(idx)
