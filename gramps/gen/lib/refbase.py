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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Base Reference class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

#-------------------------------------------------------------------------
#
# RefBase class
#
#-------------------------------------------------------------------------
class RefBase(metaclass=ABCMeta):
    """
    Base reference class to manage references to other objects.

    Any *Ref* classes should derive from this class.
    """

    def __init__(self, source=None):
        if source:
            self.ref = source.ref
        else:
            self.ref = None

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.ref

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.ref = data
        return self

    @abstractmethod
    def get_referenced_handles(self):
        """
        Returns the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: Returns the list of (classname, handle) tuples for referenced
                  objects.
        :rtype: list
        """

    def set_reference_handle(self, handle):
        """
        Set the reference handle.

        :param handle: The reference handle.
        :type handle: str
        """
        self.ref = handle

    def get_reference_handle(self):
        """
        Return the reference handle.

        :returns: The reference handle.
        :rtype: str
        """
        return self.ref
