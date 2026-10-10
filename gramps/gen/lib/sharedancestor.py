#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
SharedAncestor secondary object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .citationbase import CitationBase
from .notebase import NoteBase
from .secondaryobj import SecondaryObject

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# SharedAncestor
#
# -------------------------------------------------------------------------
class SharedAncestor(SecondaryObject, CitationBase, NoteBase):
    """
    A working hypothesis or confirmed identification of the most recent
    common ancestor (MRCA) for a DNAMatch.

    person_handle is nullable to allow recording a hypothesis before the
    ancestor has been added to the tree. Multiple SharedAncestor entries
    on a DNAMatch represent parallel hypotheses or independently confirmed
    connections through separate lines.
    """

    CONF_POSSIBLE = 0
    CONF_PROBABLE = 1
    CONF_CONFIRMED = 2
    CONF_REJECTED = 3

    def __init__(self, source=None):
        """
        Create a new SharedAncestor instance, copying from source if present.

        :param source: A SharedAncestor used to initialize the new instance.
        :type source: SharedAncestor
        """
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)

        if source:
            self.__person_handle = source.__person_handle
            self.__description = source.__description
            self.__confidence = source.__confidence
        else:
            self.__person_handle = None
            self.__description = ""
            self.__confidence = SharedAncestor.CONF_POSSIBLE

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.__person_handle,
            self.__description,
            self.__confidence,
            CitationBase.serialize(self),
            NoteBase.serialize(self),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (
            self.__person_handle,
            self.__description,
            self.__confidence,
            citation_list,
            note_list,
        ) = data
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        return self

    def get_object_state(self):
        """
        Get the current object state as a dictionary.
        """
        attr_dict = super().get_object_state()
        attr_dict["person_handle"] = self.__person_handle
        attr_dict["description"] = self.__description
        attr_dict["confidence"] = self.__confidence
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using the provided dictionary.
        """
        self.__person_handle = attr_dict.pop("person_handle")
        self.__description = attr_dict.pop("description")
        self.__confidence = attr_dict.pop("confidence")
        super().set_object_state(attr_dict)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.
        """
        return {
            "type": "object",
            "title": _("Shared Ancestor"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "person_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Person"),
                },
                "description": {"type": "string", "title": _("Description")},
                "confidence": {"type": "integer", "title": _("Confidence")},
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
            },
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.
        """
        return [self.__description]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.
        """
        return []

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        """
        ret = (
            self.get_referenced_note_handles() + self.get_referenced_citation_handles()
        )
        if self.__person_handle:
            ret.append(("Person", self.__person_handle))
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may reference primary objects.
        """
        return []

    def set_person_handle(self, handle):
        """Set the handle of the shared ancestor person."""
        self.__person_handle = handle

    def get_person_handle(self):
        """Return the handle of the shared ancestor person, or None."""
        return self.__person_handle

    person_handle = property(get_person_handle, set_person_handle)

    def set_description(self, description):
        """Set the free-text description."""
        self.__description = description

    def get_description(self):
        """Return the free-text description."""
        return self.__description

    description = property(get_description, set_description)

    def set_confidence(self, confidence):
        """Set the confidence level."""
        self.__confidence = confidence

    def get_confidence(self):
        """Return the confidence level."""
        return self.__confidence

    confidence = property(get_confidence, set_confidence)
