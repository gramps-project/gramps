#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
Secondary Object class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from abc import abstractmethod

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .baseobj import BaseObject


# -------------------------------------------------------------------------
#
# Secondary Object class
#
# -------------------------------------------------------------------------
class SecondaryObject(BaseObject):
    """
    The SecondaryObject is the base class for all secondary objects in the
    database.
    """

    @abstractmethod
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """

    @abstractmethod
    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """

    def is_equal(self, source):
        return self.serialize() == source.serialize()

    def is_equivalent(self, other):
        """
        Return if this object is equivalent to other.

        Should be overwritten by objects that inherit from this class.
        """
        pass
