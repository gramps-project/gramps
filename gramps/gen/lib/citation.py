#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
Citation object for Gramps.
"""

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .mediabase import MediaBase
from .notebase import NoteBase
from .datebase import DateBase
from .tagbase import TagBase
from .attrbase import SrcAttributeBase
from .citationbase import IndirectCitationBase
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

LOG = logging.getLogger(".citation")


# -------------------------------------------------------------------------
#
# Citation class
#
# -------------------------------------------------------------------------
class Citation(
    MediaBase, NoteBase, SrcAttributeBase, IndirectCitationBase, DateBase, PrimaryObject
):
    """
    A record of a citation of a source of information.

    In GEDCOM this is called a SOURCE_CITATION.
    The data provided in the <<SOURCE_CITATION>> structure is source-related
    information specific to the data being cited.
    """

    CONF_VERY_HIGH = 4
    CONF_HIGH = 3
    CONF_NORMAL = 2
    CONF_LOW = 1
    CONF_VERY_LOW = 0

    def __init__(self):
        """Create a new Citation instance."""
        PrimaryObject.__init__(self)
        MediaBase.__init__(self)  #  7
        NoteBase.__init__(self)  #  6
        DateBase.__init__(self)  #  2
        self.source_handle = None  #  5
        self.page = ""  #  3
        self.confidence = Citation.CONF_NORMAL  #  4
        SrcAttributeBase.__init__(self)  #  8

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .srcattribute import SrcAttribute
        from .mediaref import MediaRef
        from .date import Date

        return {
            "type": "object",
            "title": _("Citation"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string", "maxLength": 50, "title": _("Handle")},
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "date": {
                    "oneOf": [{"type": "null"}, Date.get_schema()],
                    "title": _("Date"),
                },
                "page": {"type": "string", "title": _("Page")},
                "confidence": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 4,
                    "title": _("Confidence"),
                },
                "source_handle": {
                    "type": "string",
                    "maxLength": 50,
                    "title": _("Source"),
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
                    "items": SrcAttribute.get_schema(),
                    "title": _("Source Attributes"),
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

    def serialize(self, no_text_date=False):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.handle,  #  0
            self.gramps_id,  #  1
            DateBase.serialize(self, no_text_date),  #  2
            str(self.page),  #  3
            self.confidence,  #  4
            self.source_handle,  #  5
            NoteBase.serialize(self),  #  6
            MediaBase.serialize(self),  #  7
            SrcAttributeBase.serialize(self),  #  8
            self.change,  #  9
            TagBase.serialize(self),  # 10
            self.private,
        )  # 11

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Citation structure.
        """
        (
            self.handle,  #  0
            self.gramps_id,  #  1
            date,  #  2
            self.page,  #  3
            self.confidence,  #  4
            self.source_handle,  #  5
            note_list,  #  6
            media_list,  #  7
            srcattr_list,  #  8
            self.change,  #  9
            tag_list,  # 10
            self.private,  # 11
        ) = data

        DateBase.unserialize(self, date)
        NoteBase.unserialize(self, note_list)
        MediaBase.unserialize(self, media_list)
        TagBase.unserialize(self, tag_list)
        SrcAttributeBase.unserialize(self, srcattr_list)
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
        if classname == "Note":
            return handle in [ref.ref for ref in self.note_list]
        elif classname == "Media":
            return handle in [ref.ref for ref in self.media_list]
        elif classname == "Source":
            return handle == self.get_reference_handle()
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        if classname == "Source" and self.get_reference_handle() in handle_list:
            self.set_reference_handle(None)

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
        if classname == "Source" and self.get_reference_handle() == old_handle:
            self.set_reference_handle(new_handle)

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return self.media_list

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.page, self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
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
        return self.media_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.media_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles() + self.get_referenced_tag_handles()
        if self.get_reference_handle():
            ret += [("Source", self.get_reference_handle())]
        return ret

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this citation.

        :param acquisition: The citation to merge with the present citation.
        :type acquisition: Citation
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_tag_list(acquisition)
        # merge confidence
        level_priority = [0, 4, 1, 3, 2]
        idx = min(
            level_priority.index(self.confidence),
            level_priority.index(acquisition.confidence),
        )
        self.confidence = level_priority[idx]
        self._merge_attribute_list(acquisition)
        # N.B. a Citation can refer to only one 'Source', so the
        # 'Source' from acquisition cannot be merged in

    def set_confidence_level(self, val):
        """Set the confidence level."""
        self.confidence = val

    def get_confidence_level(self):
        """Return the confidence level."""
        return self.confidence

    def set_page(self, page):
        """Set the page indicator of the Citation."""
        self.page = page

    def get_page(self):
        """Get the page indicator of the Citation."""
        return self.page

    def set_reference_handle(self, val):
        self.source_handle = val

    def get_reference_handle(self):
        return self.source_handle
