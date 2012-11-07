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
Place object for GRAMPS.
"""
from __future__ import unicode_literals

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .citationbase import CitationBase
from .notebase import NoteBase
from .mediabase import MediaBase
from .urlbase import UrlBase
from .location import Location

_EMPTY_LOC = Location().serialize()

#-------------------------------------------------------------------------
#
# Place class
#
#-------------------------------------------------------------------------
class Place(CitationBase, NoteBase, MediaBase, UrlBase, PrimaryObject):
    """
    Contains information related to a place, including multiple address
    information (since place names can change with time), longitude, latitude,
    a collection of images and URLs, a note and a source.
    """
    
    def __init__(self, source=None):
        """
        Create a new Place object, copying from the source if present.

        :param source: A Place object used to initialize the new Place
        :type source: Place
        """
        PrimaryObject.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        MediaBase.__init__(self, source)
        UrlBase.__init__(self, source)
        if source:
            self.long = source.long
            self.lat = source.lat
            self.title = source.title
            self.main_loc = Location(source.main_loc)
            self.alt_loc = list(map(Location, source.alt_loc))
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.main_loc = None
            self.alt_loc = []

    def serialize(self):
        """
        Convert the data held in the Place to a Python tuple that
        represents all the data elements. 
        
        This method is used to convert the object into a form that can easily 
        be saved to a database.

        These elements may be primitive Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
            be considered persistent.
        :rtype: tuple
        """

        if self.main_loc is None or self.main_loc.serialize() == _EMPTY_LOC:
            main_loc = None
        else:
            main_loc = self.main_loc.serialize()

        return (self.handle, self.gramps_id, self.title, self.long, self.lat,
                main_loc, [al.serialize() for al in self.alt_loc],
                UrlBase.serialize(self),
                MediaBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                self.change, self.private)

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        if self.main_loc is None or self.main_loc.serialize() == _EMPTY_LOC:
            main_loc = None
        else:
            main_loc = self.main_loc.to_struct()

        return {"handle": self.handle, 
                "gramps_id": self.gramps_id, 
                "title": self.title, 
                "long": self.long, 
                "lat": self.lat,
                "main_loc": main_loc, 
                "alt_loc": [al.to_struct() for al in self.alt_loc],
                "urls": UrlBase.to_struct(self),
                "media_list": MediaBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "change": self.change, 
                "private": self.private}

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Place object.

        :param data: tuple containing the persistent data associated the
            Person object
        :type data: tuple
        """
        (self.handle, self.gramps_id, self.title, self.long, self.lat,
         main_loc, alt_loc, urls, media_list, citation_list, note_list,
         self.change, self.private) = data

        if main_loc is None:
            self.main_loc = None
        else:
            self.main_loc = Location().unserialize(main_loc)
        self.alt_loc = [Location().unserialize(al) for al in alt_loc]
        UrlBase.unserialize(self, urls)
        MediaBase.unserialize(self, media_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.long, self.lat, self.title, self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """

        ret = self.media_list + self.alt_loc + self.urls
        if self.main_loc:
            ret.append(self.main_loc)
        return ret

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: List of child secondary child objects that may refer citations.
        :rtype: list
        """
        return self.media_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.media_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles() + \
                self.get_referenced_citation_handles()

    def merge(self, acquisition):
        """ Merge the content of acquisition into this place.

        :param acquisition: The place to merge with the present place.
        :rtype acquisition: Place
        """
        self._merge_privacy(acquisition)
        self._merge_locations(acquisition)
        self._merge_media_list(acquisition)
        self._merge_url_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)

    def set_title(self, title):
        """
        Set the descriptive title of the Place object.

        :param title: descriptive title to assign to the Place
        :type title: str
        """
        self.title = title

    def get_title(self):
        """
        Return the descriptive title of the Place object.

        :returns: Returns the descriptive title of the Place
        :rtype: str
        """
        return self.title

    def set_longitude(self, longitude):
        """
        Set the longitude of the Place object.

        :param longitude: longitude to assign to the Place
        :type longitude: str
        """
        self.long = longitude

    def get_longitude(self):
        """
        Return the longitude of the Place object.

        :returns: Returns the longitude of the Place
        :rtype: str
        """
        return self.long

    def set_latitude(self, latitude):
        """
        Set the latitude of the Place object.

        :param latitude: latitude to assign to the Place
        :type latitude: str
        """
        self.lat = latitude

    def get_latitude(self):
        """
        Return the latitude of the Place object.

        :returns: Returns the latitude of the Place
        :rtype: str
        """
        return self.lat

    def get_main_location(self):
        """
        Return the :class:`~gen.lib.location.Location` object representing the primary information for 
        the Place instance. 
        
        If a :class:`~gen.lib.location.Location` hasn't been assigned yet, an empty one is created.

        :returns: Returns the :class:`~gen.lib.location.Location` instance representing the primary 
                location information about the Place.
        :rtype: :class:`~gen.lib.location.Location`
        """
        if not self.main_loc:
            self.main_loc = Location()
        return self.main_loc

    def set_main_location(self, location):
        """
        Assign the main location information about the Place to the :class:`~gen.lib.location.Location`
        object passed.

        :param location: :class:`~gen.lib.location.Location` instance to assign to as the main 
                information for the Place.
        :type location: :class:`~gen.lib.location.Location`
        """
        self.main_loc = location

    def get_alternate_locations(self):
        """
        Return a list of alternate :class:`~gen.lib.location.Location` objects the present alternate 
        information about the current Place. 
        
        A Place can have more than one :class:`~gen.lib.location.Location`, since names and 
        jurisdictions can change over time for the same place.

        :returns: Returns the alternate :class:`~gen.lib.location.Location`\ s for the Place
        :rtype: list of :class:`~gen.lib.location.Location` objects
        """
        return self.alt_loc

    def set_alternate_locations(self, location_list):
        """
        Replace the current alternate :class:`~gen.lib.location.Location` object list with the new one.

        :param location_list: The list of :class:`~gen.lib.location.Location` objects to assign to the 
                Place's internal list.
        :type location_list: list of :class:`~gen.lib.location.Location` objects
        """
        self.alt_loc = location_list

    def add_alternate_locations(self, location):
        """
        Add a :class:`~gen.lib.location.Location` object to the alternate location list.

        :param location: :class:`~gen.lib.location.Location` instance to add
        :type location: :class:`~gen.lib.location.Location`
        """
        if location not in self.alt_loc:
            self.alt_loc.append(location)

    def _merge_locations(self, acquisition):
        """
        Add the main and alternate locations of acquisition to the alternate
        location list.

        :param acquisition: instance to merge
        :type acquisition: :class:'~gen.lib.place.Place
        """
        altloc_list = self.alt_loc[:]
        if self.main_loc and not self.main_loc.is_empty():
            altloc_list.insert(0, self.main_loc)
        add_list = acquisition.get_alternate_locations()
        acq_main_loc = acquisition.get_main_location()
        if acq_main_loc and not acq_main_loc.is_empty():
            add_list.insert(0, acquisition.get_main_location())
        for addendum in add_list:
            for altloc in altloc_list:
                if altloc.is_equal(addendum):
                    break
            else:
                self.alt_loc.append(addendum)

    def get_display_info(self):
        """
        Get the display information associated with the object.

        This includes the information that is used for display and for sorting.
        Returns a list consisting of 13 strings. These are:
        
        Place Title, Place ID, Main Location Parish, Main Location County,
        Main Location City, Main Location State/Province,
        Main Location Country, upper case Place Title, upper case Parish,
        upper case city, upper case county, upper case state,
        upper case country.
        """
        
        if self.main_loc:
            return [self.title, self.gramps_id, self.main_loc.parish,
                    self.main_loc.city, self.main_loc.county,
                    self.main_loc.state, self.main_loc.country,
                    self.title.upper(), self.main_loc.parish.upper(),
                    self.main_loc.city.upper(), self.main_loc.county.upper(),
                    self.main_loc.state.upper(), self.main_loc.country.upper()]
        else:
            return [self.title, self.gramps_id, '', '', '', '', '',
                    self.title.upper(), '', '', '', '', '']
