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
PredictedRelationship secondary object for Gramps.
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
# PredictedRelationship
#
# -------------------------------------------------------------------------
class PredictedRelationship(SecondaryObject, CitationBase, NoteBase):
    """
    A predicted relationship between the two test takers of a DNAMatch.

    Each entry describes a single way the two may be related, mainly useful
    for matches not yet placed in a genealogical relationship in the tree. A
    DNAMatch may hold several entries when the relationship is uncertain.
    """

    SIDE_UNKNOWN = 0
    SIDE_MATERNAL = 1
    SIDE_PATERNAL = 2
    SIDE_BOTH = 3

    FOH_UNKNOWN = 0
    FOH_HALF = 1
    FOH_FULL = 2

    def __init__(self, source=None):
        """
        Create a new PredictedRelationship, copying from source if present.

        :param source: A PredictedRelationship used to initialize the new
                       instance.
        :type source: PredictedRelationship
        """
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)

        if source:
            self.__description = source.__description
            self.__subject_mrca_gens = source.__subject_mrca_gens
            self.__subject_side = source.__subject_side
            self.__match_mrca_gens = source.__match_mrca_gens
            self.__match_side = source.__match_side
            self.__full_or_half = source.__full_or_half
            self.__probability = source.__probability
        else:
            self.__description = ""
            self.__subject_mrca_gens = 0
            self.__subject_side = PredictedRelationship.SIDE_UNKNOWN
            self.__match_mrca_gens = 0
            self.__match_side = PredictedRelationship.SIDE_UNKNOWN
            self.__full_or_half = PredictedRelationship.FOH_UNKNOWN
            self.__probability = 0.0

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.__description,
            self.__subject_mrca_gens,
            self.__subject_side,
            self.__match_mrca_gens,
            self.__match_side,
            self.__full_or_half,
            self.__probability,
            CitationBase.serialize(self),
            NoteBase.serialize(self),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (
            self.__description,
            self.__subject_mrca_gens,
            self.__subject_side,
            self.__match_mrca_gens,
            self.__match_side,
            self.__full_or_half,
            self.__probability,
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
        attr_dict["description"] = self.__description
        attr_dict["subject_mrca_gens"] = self.__subject_mrca_gens
        attr_dict["subject_side"] = self.__subject_side
        attr_dict["match_mrca_gens"] = self.__match_mrca_gens
        attr_dict["match_side"] = self.__match_side
        attr_dict["full_or_half"] = self.__full_or_half
        attr_dict["probability"] = self.__probability
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using the provided dictionary.
        """
        self.__description = attr_dict.pop("description")
        self.__subject_mrca_gens = attr_dict.pop("subject_mrca_gens")
        self.__subject_side = attr_dict.pop("subject_side")
        self.__match_mrca_gens = attr_dict.pop("match_mrca_gens")
        self.__match_side = attr_dict.pop("match_side")
        self.__full_or_half = attr_dict.pop("full_or_half")
        self.__probability = attr_dict.pop("probability")
        super().set_object_state(attr_dict)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.
        """
        return {
            "type": "object",
            "title": _("Predicted Relationship"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "description": {"type": "string", "title": _("Description")},
                "subject_mrca_gens": {
                    "type": "integer",
                    "title": _("Subject generations to MRCA"),
                },
                "subject_side": {"type": "integer", "title": _("Subject side")},
                "match_mrca_gens": {
                    "type": "integer",
                    "title": _("Match generations to MRCA"),
                },
                "match_side": {"type": "integer", "title": _("Match side")},
                "full_or_half": {"type": "integer", "title": _("Full or half")},
                "probability": {"type": "number", "title": _("Probability")},
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
        return (
            self.get_referenced_note_handles() + self.get_referenced_citation_handles()
        )

    def get_handle_referents(self):
        """
        Return the list of child objects which may reference primary objects.
        """
        return []

    def set_description(self, description):
        """Set the free-text description of the relationship."""
        self.__description = description

    def get_description(self):
        """Return the free-text description of the relationship."""
        return self.__description

    description = property(get_description, set_description)

    def set_subject_mrca_gens(self, gens):
        """Set the generations from the subject up to the possible MRCA."""
        self.__subject_mrca_gens = gens

    def get_subject_mrca_gens(self):
        """Return the generations from the subject up to the possible MRCA."""
        return self.__subject_mrca_gens

    subject_mrca_gens = property(get_subject_mrca_gens, set_subject_mrca_gens)

    def set_subject_side(self, side):
        """Set which side the subject is related to the match on."""
        self.__subject_side = side

    def get_subject_side(self):
        """Return which side the subject is related to the match on."""
        return self.__subject_side

    subject_side = property(get_subject_side, set_subject_side)

    def set_match_mrca_gens(self, gens):
        """Set the generations from the match up to the possible MRCA."""
        self.__match_mrca_gens = gens

    def get_match_mrca_gens(self):
        """Return the generations from the match up to the possible MRCA."""
        return self.__match_mrca_gens

    match_mrca_gens = property(get_match_mrca_gens, set_match_mrca_gens)

    def set_match_side(self, side):
        """Set which side the match is related to the subject on."""
        self.__match_side = side

    def get_match_side(self):
        """Return which side the match is related to the subject on."""
        return self.__match_side

    match_side = property(get_match_side, set_match_side)

    def set_full_or_half(self, full_or_half):
        """Set whether the relationship is full, half, or unknown."""
        self.__full_or_half = full_or_half

    def get_full_or_half(self):
        """Return whether the relationship is full, half, or unknown."""
        return self.__full_or_half

    full_or_half = property(get_full_or_half, set_full_or_half)

    def set_probability(self, probability):
        """Set the estimated probability of the relationship."""
        self.__probability = probability

    def get_probability(self):
        """Return the estimated probability of the relationship."""
        return self.__probability

    probability = property(get_probability, set_probability)
