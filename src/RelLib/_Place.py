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
Place object for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _PrimaryObject import PrimaryObject
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _MediaBase import MediaBase
from _UrlBase import UrlBase
from _Location import Location

_EMPTY_LOC = Location().serialize()

#-------------------------------------------------------------------------
#
# Place class
#
#-------------------------------------------------------------------------
class Place(PrimaryObject, SourceBase, NoteBase, MediaBase, UrlBase):
    """
    Contains information related to a place, including multiple address
    information (since place names can change with time), longitude, latitude,
    a collection of images and URLs, a note and a source
    """
    
    def __init__(self, source=None):
        """
        Creates a new Place object, copying from the source if present.

        @param source: A Place object used to initialize the new Place
        @type source: Place
        """
        PrimaryObject.__init__(self, source)
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        MediaBase.__init__(self, source)
        UrlBase.__init__(self, source)
        if source:
            self.long = source.long
            self.lat = source.lat
            self.title = source.title
            self.main_loc = Location(source.main_loc)
            self.alt_loc = [Location(loc) for loc in source.alt_loc]
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.main_loc = None
            self.alt_loc = []

    def serialize(self):
        """
        Converts the data held in the Place to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.

        @returns: Returns a python tuple containing the data that should
            be considered persistent.
        @rtype: tuple
        """

        if self.main_loc == None or self.main_loc.serialize() == _EMPTY_LOC:
            main_loc = None
        else:
            main_loc = self.main_loc.serialize()

        return (self.handle, self.gramps_id, self.title, self.long, self.lat,
                main_loc, [al.serialize() for al in self.alt_loc],
                UrlBase.serialize(self),
                MediaBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                self.change, self.marker.serialize() ,self.private)

    def unserialize(self, data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in a Place object.

        @param data: tuple containing the persistent data associated the
            Person object
        @type data: tuple
        """
        (self.handle, self.gramps_id, self.title, self.long, self.lat,
         main_loc, alt_loc, urls, media_list, source_list, note,
         self.change, marker, self.private) = data

        if main_loc == None:
            self.main_loc = None
        else:
            self.main_loc = Location().unserialize(main_loc)
        self.alt_loc = [Location().unserialize(al) for al in alt_loc]
        self.marker.unserialize(marker)
        UrlBase.unserialize(self, urls)
        MediaBase.unserialize(self, media_list)
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note)

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.long, self.lat, self.title, self.gramps_id]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """

        check_list = [self.main_loc, self.note]
        add_list = [item for item in check_list if item]
        return self.media_list + self.source_list + self.alt_loc \
                + self.urls + add_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return self.media_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.media_list + self.source_list

    def set_title(self, title):
        """
        Sets the descriptive title of the Place object

        @param title: descriptive title to assign to the Place
        @type title: str
        """
        self.title = title

    def get_title(self):
        """
        Returns the descriptive title of the Place object

        @returns: Returns the descriptive title of the Place
        @rtype: str
        """
        return self.title

    def set_longitude(self, longitude):
        """
        Sets the longitude of the Place object

        @param longitude: longitude to assign to the Place
        @type longitude: str
        """
        self.long = longitude

    def get_longitude(self):
        """
        Returns the longitude of the Place object

        @returns: Returns the longitude of the Place
        @rtype: str
        """
        return self.long

    def set_latitude(self, latitude):
        """
        Sets the latitude of the Place object

        @param latitude: latitude to assign to the Place
        @type latitude: str
        """
        self.lat = latitude

    def get_latitude(self):
        """
        Returns the latitude of the Place object

        @returns: Returns the latitude of the Place
        @rtype: str
        """
        return self.lat

    def get_main_location(self):
        """
        Returns the L{Location} object representing the primary information for the
        Place instance. If a L{Location} hasn't been assigned yet, an empty one is
        created.

        @returns: Returns the L{Location} instance representing the primary location
            information about the Place
        @rtype: L{Location}
        """
        if not self.main_loc:
            self.main_loc = Location()
        return self.main_loc

    def set_main_location(self, location):
        """
        Assigns the main location information about the Place to the L{Location}
        object passed

        @param location: L{Location} instance to assign to as the main information for
            the Place
        @type location: L{Location}
        """
        self.main_loc = location

    def get_alternate_locations(self):
        """
        Returns a list of alternate L{Location} objects the present alternate information
        about the current Place. A Place can have more than one L{Location}, since names
        and jurisdictions can change over time for the same place.

        @returns: Returns the alternate L{Location}s for the Place
        @rtype: list of L{Location} objects
        """
        return self.alt_loc

    def set_alternate_locations(self, location_list):
        """
        Replaces the current alternate L{Location} object list with the new one.

        @param location_list: The list of L{Location} objects to assign to the Place's
            internal list
        @type location_list: list of L{Location} objects
        """
        self.alt_loc = location_list

    def add_alternate_locations(self, location):
        """
        Adds a L{Location} object to the alternate location list

        @param location: L{Location} instance to add
        @type location: L{Location}
        """
        if location not in self.alt_loc:
            self.alt_loc.append(location)

    def get_display_info(self):
        """
        Gets the display information associated with the object.

        This includes the information that is used for display and for sorting.
        Returns a list consisting of 13 strings. These are:
        
        Place Title, Place ID, Main Location Parish, Main Location County,
        Main Location City, Main Location State/Province,
        Main Location Country, upper case Place Title, upper case Parish,
        upper case city, upper case county, upper case state,
        upper case country
        """
        
        if self.main_loc:
            return [self.title, self.gramps_id, self.main_loc.parish,
                    self.main_loc.city, self.main_loc.county,
                    self.main_loc.state, self.main_loc.country,
                    self.title.upper(), self.main_loc.parish.upper(),
                    self.main_loc.city.upper(), self.main_loc.county.upper(),
                    self.main_loc.state.upper(), self.main_loc.country.upper()]
        else:
            return [self.title, self.gramps_id, u'', u'', u'', u'', u'',
                    self.title.upper(), u'', u'', u'', u'', u'']
