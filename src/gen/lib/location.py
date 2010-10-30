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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Location class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.secondaryobj import SecondaryObject
from gen.lib.locationbase import LocationBase
from gen.lib.const import IDENTICAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Location class for Places
#
#-------------------------------------------------------------------------
class Location(SecondaryObject, LocationBase):
    """
    Provide information about a place.

    The data including street, locality, city, county, state, and country.
    Multiple Location objects can represent the same place, since names
    of cities, counties, states, and even countries can change with time.
    """
    
    def __init__(self, source=None):
        """
        Create a Location object, copying from the source object if it exists.
        """
        LocationBase.__init__(self, source)
        if source:
            self.parish = source.parish
        else:
            self.parish = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (LocationBase.serialize(self), self.parish)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (lbase, self.parish) = data
        LocationBase.unserialize(self, lbase)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.parish] + LocationBase.get_text_data_list(self)

    def is_equivalent(self, other):
        """
        Return if this location is equivalent to other.

        :param other: The location to compare this one to.
        :rtype other: Location
        :returns: Constant inidicating degree of equivalence.
        :rtype: int
        """
        if self.is_equal(other):
            return IDENTICAL
        else:
            return DIFFERENT

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this location.

        Lost: everything of acquisition.

        :param acquisition: The location to merge with the present location.
        :rtype acquisition: Location
        """
        pass

    def is_empty(self):
        return not self.street and not self.locality and not self.city and \
               not self.county and not self.state and not self.country and \
               not self.postal and not self.phone
        
    def set_parish(self, data):
        """Set the religious parish name."""
        self.parish = data

    def get_parish(self):
        """Get the religious parish name."""
        return self.parish
