#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2017       Nick Hall
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
Place object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .placeref import PlaceRef
from .placename import PlaceName
from .placetype import PlaceType
from .citationbase import CitationBase
from .notebase import NoteBase
from .mediabase import MediaBase
from .urlbase import UrlBase
from .tagbase import TagBase
from .location import Location
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Place class
#
# -------------------------------------------------------------------------
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
            self.name = source.name
            self.alt_names = source.alt_names
            self.placeref_list = list(map(PlaceRef, source.placeref_list))
            self.place_type = source.place_type
            self.code = source.code
            self.alt_loc = list(map(Location, source.alt_loc))
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.name = PlaceName()
            self.alt_names = []
            self.placeref_list = []
            self.place_type = PlaceType()
            self.code = ""
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
        return (
            self.handle,
            self.gramps_id,
            self.title,
            self.long,
            self.lat,
            [pr.serialize() for pr in self.placeref_list],
            self.name.serialize(),
            [an.serialize() for an in self.alt_names],
            self.place_type.serialize(),
            self.code,
            [al.serialize() for al in self.alt_loc],
            UrlBase.serialize(self),
            MediaBase.serialize(self),
            CitationBase.serialize(self),
            NoteBase.serialize(self),
            self.change,
            TagBase.serialize(self),
            self.private,
        )

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .url import Url
        from .mediaref import MediaRef

        return {
            "type": "object",
            "title": _("Place"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string", "maxLength": 50, "title": _("Handle")},
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "title": {"type": "string", "title": _("Title")},
                "long": {"type": "string", "title": _("Longitude")},
                "lat": {"type": "string", "title": _("Latitude")},
                "placeref_list": {
                    "type": "array",
                    "items": PlaceRef.get_schema(),
                    "title": _("Places"),
                },
                "name": PlaceName.get_schema(),
                "alt_names": {
                    "type": "array",
                    "items": PlaceName.get_schema(),
                    "title": _("Alternate Names"),
                },
                "place_type": PlaceType.get_schema(),
                "code": {"type": "string", "title": _("Code")},
                "alt_loc": {
                    "type": "array",
                    "items": Location.get_schema(),
                    "title": _("Alternate Locations"),
                },
                "urls": {
                    "type": "array",
                    "items": Url.get_schema(),
                    "title": _("URLs"),
                },
                "media_list": {
                    "type": "array",
                    "items": MediaRef.get_schema(),
                    "title": _("Media"),
                },
                "citation_list": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "title": _("Citations"),
                },
                "note_list": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "title": _("Notes"),
                },
                "change": {"type": "integer", "title": _("Last changed")},
                "tag_list": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "title": _("Tags"),
                },
                "private": {"type": "boolean", "title": _("Private")},
            },
        }

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Place object.

        :param data: tuple containing the persistent data associated with the
                     Place object
        :type data: tuple
        """
        (
            self.handle,
            self.gramps_id,
            self.title,
            self.long,
            self.lat,
            placeref_list,
            name,
            alt_names,
            the_type,
            self.code,
            alt_loc,
            urls,
            media_list,
            citation_list,
            note_list,
            self.change,
            tag_list,
            self.private,
        ) = data

        self.place_type = PlaceType()
        self.place_type.unserialize(the_type)
        self.alt_loc = [Location().unserialize(al) for al in alt_loc]
        self.placeref_list = [PlaceRef().unserialize(pr) for pr in placeref_list]
        self.name = PlaceName().unserialize(name)
        self.alt_names = [PlaceName().unserialize(an) for an in alt_names]
        UrlBase.unserialize(self, urls)
        MediaBase.unserialize(self, media_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        TagBase.unserialize(self, tag_list)
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

        ret = self.media_list + self.alt_loc + self.urls + [self.name] + self.alt_names
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
        return self.get_citation_child_list() + self.placeref_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return (
            self.get_referenced_note_handles()
            + self.get_referenced_citation_handles()
            + self.get_referenced_tag_handles()
        )

    def merge(self, acquisition):
        """Merge the content of acquisition into this place.

        :param acquisition: The place to merge with the present place.
        :type acquisition: Place
        """
        self._merge_privacy(acquisition)
        self._merge_locations(acquisition)
        self._merge_alt_names(acquisition)
        self._merge_media_list(acquisition)
        self._merge_url_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_tag_list(acquisition)
        self._merge_placeref_list(acquisition)

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

    def set_name(self, name):
        """
        Set the name of the Place object.

        :param name: name to assign to the Place
        :type name: PlaceName
        """
        if not isinstance(name, PlaceName):
            raise ValueError("Place.set_name(name) requires a PlaceName()")
        self.name = name

    def get_name(self):
        """
        Return the name of the Place object.

        :returns: Returns the name of the Place
        :rtype: PlaceName
        """
        return self.name

    def get_all_names(self):
        """
        Return a list of all names of the Place object.

        :returns: Returns a list of all names of the Place
        :rtype: list of PlaceName
        """
        return [self.name] + self.alt_names

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

    def set_type(self, place_type):
        """
        Set the type of the Place object.

        :param type: type to assign to the Place
        :type type: PlaceType
        """
        self.place_type.set(place_type)

    def get_type(self):
        """
        Return the type of the Place object.

        :returns: Returns the type of the Place
        :rtype: PlaceType
        """
        return self.place_type

    def set_code(self, code):
        """
        Set the code of the Place object.

        :param code: code to assign to the Place
        :type code: str
        """
        self.code = code

    def get_code(self):
        """
        Return the code of the Place object.

        :returns: Returns the code of the Place
        :rtype: str
        """
        return self.code

    def add_placeref(self, placeref):
        """
        Add a place reference to the list of place references.

        :param code: place reference to append to the list
        :type code: PlaceRef
        """
        self.placeref_list.append(placeref)

    def get_placeref_list(self):
        """
        Return the place reference list for the Place object.

        :returns: Returns the place reference list for the Place
        :rtype: list
        """
        return self.placeref_list

    def set_placeref_list(self, placeref_list):
        """
        Set the place reference list for the Place object.

        :param code: place reference list to assign to the Place
        :type code: list
        """
        self.placeref_list = placeref_list

    def _merge_placeref_list(self, acquisition):
        """
        Add the main and alternate locations of acquisition to the alternate
        location list.

        :param acquisition: instance to merge
        :type acquisition: :class:'~.place.Place
        """
        placeref_list = self.placeref_list[:]
        add_list = acquisition.placeref_list
        for addendum in add_list:
            for placeref in placeref_list:
                if placeref.is_equal(addendum):
                    break
            else:
                self.placeref_list.append(addendum)

    def _has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given
        primary object type.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str
        :returns: Returns whether the object has reference to this handle of
                this object type.
        :rtype: bool
        """
        if classname == "Place":
            for placeref in self.placeref_list:
                if placeref.ref == handle:
                    return True
        return False

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        if classname == "Place":
            for placeref in self.placeref_list:
                if placeref.ref == old_handle:
                    placeref.ref = new_handle

    def get_alternative_names(self):
        """
        Return a list of alternative names for the current Place.

        :returns: Returns the alternative names for the Place
        :rtype: list of PlaceName
        """
        return self.alt_names

    def set_alternative_names(self, name_list):
        """
        Replace the current alternative names list with the new one.

        :param name_list: The list of names to assign to the Place's internal
                          list.
        :type name_list: list of PlaceName
        """
        self.alt_names = name_list

    def add_alternative_name(self, name):
        """
        Add a name to the alternative names list.

        :param name: name to add
        :type name: string
        """
        if name not in self.alt_names:
            self.alt_names.append(name)

    def get_alternate_locations(self):
        """
        Return a list of alternate :class:`~.location.Location` objects the
        present alternate information about the current Place.

        A Place can have more than one :class:`~.location.Location`, since
        names and jurisdictions can change over time for the same place.

        :returns: Returns the alternate :class:`~.location.Location` objects
                  for the Place
        :rtype: list of :class:`~.location.Location` objects
        """
        return self.alt_loc

    def set_alternate_locations(self, location_list):
        """
        Replace the current alternate :class:`~.location.Location` object list
        with the new one.

        :param location_list: The list of :class:`~.location.Location` objects
                              to assign to the Place's internal list.
        :type location_list: list of :class:`~.location.Location` objects
        """
        self.alt_loc = location_list

    def add_alternate_locations(self, location):
        """
        Add a :class:`~.location.Location` object to the alternate location
        list.

        :param location: :class:`~.location.Location` instance to add
        :type location: :class:`~.location.Location`
        """
        if location not in self.alt_loc:
            self.alt_loc.append(location)

    def _merge_locations(self, acquisition):
        """
        Add the main and alternate locations of acquisition to the alternate
        location list.

        :param acquisition: instance to merge
        :type acquisition: :class:'~.place.Place
        """
        altloc_list = self.alt_loc[:]
        add_list = acquisition.get_alternate_locations()
        for addendum in add_list:
            for altloc in altloc_list:
                if altloc.is_equal(addendum):
                    break
            else:
                self.alt_loc.append(addendum)

    def _merge_alt_names(self, acquisition):
        """
        Add the main and alternative names of acquisition to the alternative
        names list.

        :param acquisition: instance to merge
        :type acquisition: :class:'~.place.Place
        """
        if acquisition.name.value:
            if acquisition.name != self.name:
                if acquisition.name not in self.alt_names:
                    self.alt_names.append(acquisition.name)

        for addendum in acquisition.alt_names:
            if addendum.value:
                if addendum != self.name:
                    if addendum not in self.alt_names:
                        self.alt_names.append(addendum)
