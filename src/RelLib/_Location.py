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
Location class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _LocationBase import LocationBase

#-------------------------------------------------------------------------
#
# Location class for Places
#
#-------------------------------------------------------------------------
class Location(SecondaryObject,LocationBase):
    """
    Provides information about a place.

    The data including city, county, state, and country.
    Multiple Location objects can represent the same place, since names
    of citys, countys, states, and even countries can change with time.
    """
    
    def __init__(self,source=None):
        """
        Creates a Location object, copying from the source object if it exists.
        """

        SecondaryObject.__init__(self)
        LocationBase.__init__(self,source)
        if source:
            self.parish = source.parish
        else:
            self.parish = ""

    def serialize(self):
        return (LocationBase.serialize(self),self.parish)

    def unserialize(self,data):
        (lb, self.parish) = data
        LocationBase.unserialize(self, lb)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.parish] + LocationBase.get_text_data_list(self)

    def is_empty(self):
        return not self.city and not self.county and not self.state and \
               not self.country and not self.postal and not self.phone
        
    def set_parish(self,data):
        """sets the religious parish name"""
        self.parish = data

    def get_parish(self):
        """gets the religious parish name"""
        return self.parish

    def set_county(self,data):
        """sets the county name of the Location object"""
        self.county = data

    def get_county(self):
        """returns the county name of the Location object"""
        return self.county
