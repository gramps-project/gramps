#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Nick Hall
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
TagBase class for Gramps.
"""


# -------------------------------------------------------------------------
#
# TagBase class
#
# -------------------------------------------------------------------------
class TagBase:
    """
    Base class for tag-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a TagBase.

        If the source is not None, then object is initialized from values of
        the source object.

        :param source: Object used to initialize the new object
        :type source: TagBase
        """
        if source:
            self.tag_list = list(source.tag_list)
        else:
            self.tag_list = []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.tag_list

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.tag_list = data
        return self

    def add_tag(self, tag):
        """
        Add the tag to the object's list of tags.

        :param tag: unicode tag to add.
        :type tag: unicode
        """
        if tag not in self.tag_list:
            self.tag_list.append(tag)

    def remove_tag(self, tag):
        """
        Remove the specified tag from the tag list.

        If the tag does not exist in the list, the operation has no effect.

        :param tag: tag to remove from the list.
        :type tag: unicode

        :returns: True if the tag was removed, False if it was not in the list.
        :rtype: bool
        """
        if tag in self.tag_list:
            self.tag_list.remove(tag)
            return True
        else:
            return False

    def get_tag_list(self):
        """
        Return the list of tags associated with the object.

        :returns: Returns the list of tags.
        :rtype: list
        """
        return self.tag_list

    def set_tag_list(self, tag_list):
        """
        Assign the passed list to the objects's list of tags.

        :param tag_list: List of tags to ba associated with the object.
        :type tag_list: list
        """
        self.tag_list = tag_list

    def get_referenced_tag_handles(self):
        """
        Return the list of (classname, handle) tuples for all referenced tags.

        This method should be used to get the :class:`~.tag.Tag` portion
        of the list by objects that store tag lists.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return [("Tag", handle) for handle in self.tag_list]

    def _merge_tag_list(self, acquisition):
        """
        Merge the list of tag from acquisition with our own.

        :param acquisition: The tag list of this object will be merged with
                            the current tag list.
        :type acquisition: TagBase
        """
        for addendum in acquisition.get_tag_list():
            self.add_tag(addendum)

    def replace_tag_references(self, old_handle, new_handle):
        """
        Replace references to note handles in the list of this object and
        merge equivalent entries.

        :param old_handle: The note handle to be replaced.
        :type old_handle: str
        :param new_handle: The note handle to replace the old one with.
        :type new_handle: str
        """
        refs_list = self.tag_list[:]
        new_ref = None
        if new_handle in self.tag_list:
            new_ref = new_handle
        n_replace = refs_list.count(old_handle)
        for ix_replace in range(n_replace):
            idx = refs_list.index(old_handle)
            if new_ref:
                self.tag_list.pop(idx)
                refs_list.pop(idx)
            else:
                self.tag_list[idx] = new_handle
