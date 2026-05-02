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
DNAMatch object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .attrbase import DNAAttributeBase
from .citationbase import CitationBase
from .dnasegment import DNASegment
from .mediabase import MediaBase
from .notebase import NoteBase
from .primaryobj import PrimaryObject
from .sharedancestor import SharedAncestor
from .tagbase import TagBase

_ = glocale.translation.gettext

LOG = logging.getLogger(".dnamatch")


# -------------------------------------------------------------------------
#
# DNAMatch
#
# -------------------------------------------------------------------------
class DNAMatch(
    CitationBase,
    NoteBase,
    MediaBase,
    DNAAttributeBase,
    PrimaryObject,
):
    """
    A pairwise DNA match between two kits.

    subject_test_handle is the kit whose match list this came from.
    match_test_handle is the other kit; it always has a DNATest record.

    The match does not store a confirmed relationship. Once both
    DNATest records have person_handle set the relationship is computable
    from the tree. predicted_relationship retains the raw label reported
    by the testing platform.
    """

    def __init__(self, source=None):
        """
        Create a new DNAMatch instance, copying from source if present.

        :param source: A DNAMatch used to initialize the new instance.
        :type source: DNAMatch
        """
        PrimaryObject.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        MediaBase.__init__(self, source)
        DNAAttributeBase.__init__(self)

        if source:
            self.__subject_test_handle = source.__subject_test_handle
            self.__match_test_handle = source.__match_test_handle
            self.__shared_cm = source.__shared_cm
            self.__percent_shared = source.__percent_shared
            self.__segment_count = source.__segment_count
            self.__largest_segment_cm = source.__largest_segment_cm
            self.__predicted_relationship = source.__predicted_relationship
            self.__predicted_generations = source.__predicted_generations
            self.__shared_ancestor_list = [
                SharedAncestor(sa) for sa in source.__shared_ancestor_list
            ]
            self.__segment_list = [
                DNASegment(seg) for seg in source.__segment_list
            ]
        else:
            self.__subject_test_handle = None
            self.__match_test_handle = None
            self.__shared_cm = 0.0
            self.__percent_shared = 0.0
            self.__segment_count = 0
            self.__largest_segment_cm = 0.0
            self.__predicted_relationship = ""
            self.__predicted_generations = None
            self.__shared_ancestor_list = []
            self.__segment_list = []

    def serialize(self):
        """
        Convert the data held in the DNAMatch to a Python tuple representing
        all persistent data elements.

        :returns: tuple of persistent data
        :rtype: tuple
        """
        return (
            self.handle,
            self.gramps_id,
            self.__subject_test_handle,
            self.__match_test_handle,
            self.__shared_cm,
            self.__percent_shared,
            self.__segment_count,
            self.__largest_segment_cm,
            self.__predicted_relationship,
            self.__predicted_generations,
            [sa.serialize() for sa in self.__shared_ancestor_list],
            [seg.serialize() for seg in self.__segment_list],
            CitationBase.serialize(self),
            NoteBase.serialize(self),
            MediaBase.serialize(self),
            DNAAttributeBase.serialize(self),
            self.change,
            TagBase.serialize(self),
            self.private,
        )

    def get_object_state(self):
        """
        Get the current object state as a dictionary.
        """
        attr_dict = super().get_object_state()
        attr_dict["subject_test_handle"] = self.__subject_test_handle
        attr_dict["match_test_handle"] = self.__match_test_handle
        attr_dict["shared_cm"] = self.__shared_cm
        attr_dict["percent_shared"] = self.__percent_shared
        attr_dict["segment_count"] = self.__segment_count
        attr_dict["largest_segment_cm"] = self.__largest_segment_cm
        attr_dict["predicted_relationship"] = self.__predicted_relationship
        attr_dict["predicted_generations"] = self.__predicted_generations
        attr_dict["shared_ancestor_list"] = self.__shared_ancestor_list
        attr_dict["segment_list"] = self.__segment_list
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using the provided dictionary.
        """
        self.__subject_test_handle = attr_dict.pop("subject_test_handle")
        self.__match_test_handle = attr_dict.pop("match_test_handle")
        self.__shared_cm = attr_dict.pop("shared_cm")
        self.__percent_shared = attr_dict.pop("percent_shared")
        self.__segment_count = attr_dict.pop("segment_count")
        self.__largest_segment_cm = attr_dict.pop("largest_segment_cm")
        self.__predicted_relationship = attr_dict.pop("predicted_relationship")
        self.__predicted_generations = attr_dict.pop("predicted_generations")
        self.__shared_ancestor_list = attr_dict.pop("shared_ancestor_list")
        self.__segment_list = attr_dict.pop("segment_list")
        super().set_object_state(attr_dict)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: dict containing the schema
        :rtype: dict
        """
        # pylint: disable=import-outside-toplevel
        from .dnaattr import DNAAttribute
        from .mediaref import MediaRef

        return {
            "type": "object",
            "title": _("DNA Match"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {
                    "type": "string",
                    "maxLength": 50,
                    "title": _("Handle"),
                },
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "subject_test_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Subject kit"),
                },
                "match_test_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Match kit"),
                },
                "shared_cm": {"type": "number", "title": _("Shared cM")},
                "percent_shared": {
                    "type": "number",
                    "title": _("Percent shared"),
                },
                "segment_count": {
                    "type": "integer",
                    "title": _("Segment count"),
                },
                "largest_segment_cm": {
                    "type": "number",
                    "title": _("Largest segment cM"),
                },
                "predicted_relationship": {
                    "type": "string",
                    "title": _("Predicted relationship"),
                },
                "predicted_generations": {
                    "type": ["number", "null"],
                    "title": _("Predicted generations"),
                },
                "shared_ancestor_list": {
                    "type": "array",
                    "items": SharedAncestor.get_schema(),
                    "title": _("Shared ancestors"),
                },
                "segment_list": {
                    "type": "array",
                    "items": DNASegment.get_schema(),
                    "title": _("Segments"),
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
                "media_list": {
                    "type": "array",
                    "items": MediaRef.get_schema(),
                    "title": _("Media"),
                },
                "attribute_list": {
                    "type": "array",
                    "items": DNAAttribute.get_schema(),
                    "title": _("Attributes"),
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
        back into the data in a DNAMatch structure.

        :param data: tuple containing the persistent data
        :type data: tuple
        """
        (
            self.handle,
            self.gramps_id,
            self.__subject_test_handle,
            self.__match_test_handle,
            self.__shared_cm,
            self.__percent_shared,
            self.__segment_count,
            self.__largest_segment_cm,
            self.__predicted_relationship,
            self.__predicted_generations,
            shared_ancestor_list,
            segment_list,
            citation_list,
            note_list,
            media_list,
            attribute_list,
            self.change,
            tag_list,
            self.private,
        ) = data

        self.__shared_ancestor_list = [
            SharedAncestor().unserialize(sa) for sa in shared_ancestor_list
        ]
        self.__segment_list = [
            DNASegment().unserialize(seg) for seg in segment_list
        ]
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        MediaBase.unserialize(self, media_list)
        DNAAttributeBase.unserialize(self, attribute_list)
        TagBase.unserialize(self, tag_list)
        return self

    def _has_handle_reference(self, classname, handle):
        """
        Return True if the object has a reference to the given handle.
        """
        if classname == "DNATest":
            return (
                self.__subject_test_handle == handle
                or self.__match_test_handle == handle
            )
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references to handles in handle_list.
        """
        if classname == "DNATest":
            if self.__subject_test_handle in handle_list:
                self.__subject_test_handle = None
            if self.__match_test_handle in handle_list:
                self.__match_test_handle = None

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old_handle with new_handle.
        """
        if classname == "DNATest":
            if self.__subject_test_handle == old_handle:
                self.__subject_test_handle = new_handle
            if self.__match_test_handle == old_handle:
                self.__match_test_handle = new_handle

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.
        """
        return [self.__predicted_relationship, self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.
        """
        return (
            self.media_list
            + self.attribute_list
            + self.__shared_ancestor_list
        )

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.
        """
        return (
            self.media_list
            + self.attribute_list
            + self.__shared_ancestor_list
        )

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.
        """
        return (
            self.media_list
            + self.attribute_list
            + self.__shared_ancestor_list
        )

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        """
        ret = (
            self.get_referenced_note_handles()
            + self.get_referenced_citation_handles()
            + self.get_referenced_tag_handles()
        )
        if self.__subject_test_handle:
            ret.append(("DNATest", self.__subject_test_handle))
        if self.__match_test_handle:
            ret.append(("DNATest", self.__match_test_handle))
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        """
        return self.get_citation_child_list()

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this DNAMatch.

        :param acquisition: The DNAMatch to merge with the present one.
        :type acquisition: DNAMatch
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_subject_test_handle(self, handle):
        """Set the handle of the subject's DNATest kit."""
        self.__subject_test_handle = handle

    def get_subject_test_handle(self):
        """Return the handle of the subject's DNATest kit, or None."""
        return self.__subject_test_handle

    subject_test_handle = property(get_subject_test_handle, set_subject_test_handle)

    def set_match_test_handle(self, handle):
        """Set the handle of the match's DNATest kit."""
        self.__match_test_handle = handle

    def get_match_test_handle(self):
        """Return the handle of the match's DNATest kit, or None."""
        return self.__match_test_handle

    match_test_handle = property(get_match_test_handle, set_match_test_handle)

    def set_shared_cm(self, cm):
        """Set the total shared centimorgans."""
        self.__shared_cm = cm

    def get_shared_cm(self):
        """Return the total shared centimorgans."""
        return self.__shared_cm

    shared_cm = property(get_shared_cm, set_shared_cm)

    def set_percent_shared(self, percent):
        """Set the percentage of genome shared."""
        self.__percent_shared = percent

    def get_percent_shared(self):
        """Return the percentage of genome shared."""
        return self.__percent_shared

    percent_shared = property(get_percent_shared, set_percent_shared)

    def set_segment_count(self, count):
        """Set the number of shared segments."""
        self.__segment_count = count

    def get_segment_count(self):
        """Return the number of shared segments."""
        return self.__segment_count

    segment_count = property(get_segment_count, set_segment_count)

    def set_largest_segment_cm(self, cm):
        """Set the largest segment size in cM."""
        self.__largest_segment_cm = cm

    def get_largest_segment_cm(self):
        """Return the largest segment size in cM."""
        return self.__largest_segment_cm

    largest_segment_cm = property(get_largest_segment_cm, set_largest_segment_cm)

    def set_predicted_relationship(self, relationship):
        """Set the platform's predicted relationship label."""
        self.__predicted_relationship = relationship

    def get_predicted_relationship(self):
        """Return the platform's predicted relationship label."""
        return self.__predicted_relationship

    predicted_relationship = property(
        get_predicted_relationship, set_predicted_relationship
    )

    def set_predicted_generations(self, generations):
        """Set the platform's estimated generations to MRCA, or None."""
        self.__predicted_generations = generations

    def get_predicted_generations(self):
        """Return the platform's estimated generations to MRCA, or None."""
        return self.__predicted_generations

    predicted_generations = property(
        get_predicted_generations, set_predicted_generations
    )

    def set_shared_ancestor_list(self, ancestor_list):
        """Set the list of SharedAncestor objects."""
        self.__shared_ancestor_list = ancestor_list

    def get_shared_ancestor_list(self):
        """Return the list of SharedAncestor objects."""
        return self.__shared_ancestor_list

    shared_ancestor_list = property(
        get_shared_ancestor_list, set_shared_ancestor_list
    )

    def add_shared_ancestor(self, ancestor):
        """Append a SharedAncestor to the list."""
        self.__shared_ancestor_list.append(ancestor)

    def set_segment_list(self, segment_list):
        """Set the list of DNASegment objects."""
        self.__segment_list = segment_list

    def get_segment_list(self):
        """Return the list of DNASegment objects."""
        return self.__segment_list

    segment_list = property(get_segment_list, set_segment_list)

    def add_segment(self, segment):
        """Append a DNASegment to the list."""
        self.__segment_list.append(segment)
