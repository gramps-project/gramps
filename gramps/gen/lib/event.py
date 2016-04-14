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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Event object for Gramps.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .citationbase import CitationBase
from .notebase import NoteBase
from .mediabase import MediaBase
from .attrbase import AttributeBase
from .datebase import DateBase
from .placebase import PlaceBase
from .tagbase import TagBase
from .eventtype import EventType
from .handle import Handle

LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# Event class
#
#-------------------------------------------------------------------------
class Event(CitationBase, NoteBase, MediaBase, AttributeBase,
            DateBase, PlaceBase, PrimaryObject):
    """
    The Event record is used to store information about some type of
    action that occurred at a particular place at a particular time,
    such as a birth, death, or marriage.

    A possible definition: Events are things that happen at some point in time
    (that we may not know precisely, though), at some place, may involve
    several people (witnesses, officers, notaries, priests, etc.) and may
    of course have sources, notes, media, etc.
    Compare this with attribute: :class:`~.attribute.Attribute`
    """

    def __init__(self, source=None):
        """
        Create a new Event instance, copying from the source if present.

        :param source: An event used to initialize the new event
        :type source: Event
        """

        PrimaryObject.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        MediaBase.__init__(self, source)
        AttributeBase.__init__(self)
        DateBase.__init__(self, source)
        PlaceBase.__init__(self, source)

        if source:
            self.__description = source.description
            self.__type = EventType(source.type)
        else:
            self.__description = ""
            self.__type = EventType()

    def serialize(self, no_text_date=False):
        """
        Convert the data held in the event to a Python tuple that
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
        return (self.handle, self.gramps_id, self.__type.serialize(),
                DateBase.serialize(self, no_text_date),
                self.__description, self.place,
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                MediaBase.serialize(self),
                AttributeBase.serialize(self),
                self.change, TagBase.serialize(self), self.private)

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
        return {"_class": "Event",
                "handle": Handle("Event", self.handle),
                "gramps_id": self.gramps_id,
                "type": self.__type.to_struct(),
                "date": DateBase.to_struct(self),
                "description": self.__description,
                "place": Handle("Place", self.place),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "media_list": MediaBase.to_struct(self),
                "attribute_list": AttributeBase.to_struct(self),
                "change": self.change,
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    @classmethod
    def get_schema(cls):
        """
        Return the schema as a dictionary for this class.
        """
        from .attribute import Attribute
        from .citation import Citation
        from .note import Note
        from .date import Date
        from .tag import Tag
        from .media import Media
        return {
            "handle": Handle("Event", "EVENT-HANDLE"),
            "gramps_id": str,
            "type": EventType,
            "date": Date,
            "description": str,
            "place": Handle("Place", "PLACE-HANDLE"),
            "citation_list": [Citation],
            "note_list": [Note],
            "media_list": [Media],
            "attribute_list": [Attribute],
            "change": float,
            "tag_list": [Tag],
            "private": bool,
        }

    @classmethod
    def get_labels(cls, _):
        return {
            "_class": _("Event"),
            "handle":  _("Handle"),
            "gramps_id": _("Gramps ID"),
            "type": _("Type"),
            "date": _("Date"),
            "description": _("Description"),
            "place":  _("Place"),
            "citation_list": _("Citations"),
            "note_list": _("Notes"),
            "media_list": _("Media"),
            "attribute_list": _("Attributes"),
            "change": _("Last changed"),
            "tag_list": _("Tags"),
            "private": _("Private"),
        }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Event()
        return (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("gramps_id", default.gramps_id),
                EventType.from_struct(struct.get("type", {})),
                DateBase.from_struct(struct.get("date", {})),
                struct.get("description", default.description),
                Handle.from_struct(struct.get("place", default.place)),
                CitationBase.from_struct(struct.get("citation_list", default.citation_list)),
                NoteBase.from_struct(struct.get("note_list", default.note_list)),
                MediaBase.from_struct(struct.get("media_list", default.media_list)),
                AttributeBase.from_struct(struct.get("attribute_list", default.attribute_list)),
                struct.get("change", default.change),
                TagBase.from_struct(struct.get("tag_list", default.tag_list)),
                struct.get("private", default.private))

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in an Event structure.

        :param data: tuple containing the persistent data associated with the
                     Event object
        :type data: tuple
        """
        (self.handle, self.gramps_id, the_type, date,
         self.__description, self.place,
         citation_list, note_list, media_list, attribute_list,
         self.change, tag_list, self.private) = data

        self.__type = EventType()
        self.__type.unserialize(the_type)
        DateBase.unserialize(self, date)
        MediaBase.unserialize(self, media_list)
        AttributeBase.unserialize(self, attribute_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        TagBase.unserialize(self, tag_list)
        return self

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
        if classname == 'Place':
            return self.place == handle
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        if classname == 'Place' and self.place in handle_list:
            self.place = ""

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
        if classname == 'Place' and self.place == old_handle:
            self.place = new_handle

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.__description, str(self.__type), self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.media_list + self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return self.media_list + self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return self.media_list + self.attribute_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = (self.get_referenced_note_handles() +
               self.get_referenced_citation_handles() +
               self.get_referenced_tag_handles())
        if self.place:
            ret.append(('Place', self.place))
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def is_empty(self):
        """
        Return True if the Event is an empty object (no values set).

        :returns: True if the Event is empty
        :rtype: bool
        """
        date = self.get_date_object()
        place = self.get_place_handle()
        description = self.__description
        the_type = self.__type
        return (the_type == EventType.CUSTOM and date.is_empty()
                and not place and not description)

    def are_equal(self, other):
        """
        Return True if the passed Event is equivalent to the current Event.

        :param other: Event to compare against
        :type other: Event
        :returns: True if the Events are equal
        :rtype: bool
        """
        if other is None:
            other = Event(None)

        if self.__type != other.type or \
           ((self.place or other.place) and (self.place != other.place)) or \
           self.__description != other.description \
           or self.private != other.private or \
           (not self.get_date_object().is_equal(other.get_date_object())) or \
           len(self.get_citation_list()) != \
                len(other.get_citation_list()):
            return False

        index = 0
        olist = other.get_citation_list()
        for handle in self.get_citation_list():
            # see comment in srefs_are_equal in gen/plug/report/_bibliography.py
            if handle != olist[index]:
                return False
            index += 1

        return True

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this event.

        Lost: handle, id, marker, type, date, place, description of acquisition.

        :param acquisition: The event to merge with the present event.
        :type acquisition: Event
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_type(self, the_type):
        """
        Set the type of the Event to the passed (int,str) tuple.

        :param the_type: Type to assign to the Event
        :type the_type: tuple
        """
        self.__type.set(the_type)

    def get_type(self):
        """
        Return the type of the Event.

        :returns: Type of the Event
        :rtype: tuple
        """
        return self.__type
    type = property(get_type, set_type, None,
                    'Returns or sets type of the event')

    def set_description(self, description):
        """
        Set the description of the Event to the passed string.

        The string may contain any information.

        :param description: Description to assign to the Event
        :type description: str
        """
        self.__description = description

    def get_description(self):
        """
        Return the description of the Event.

        :returns: Returns the description of the Event
        :rtype: str
        """
        return self.__description
    description = property(get_description, set_description, None,
                           'Returns or sets description of the event')

