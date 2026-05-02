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
DNATest object for Gramps.
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
from .datebase import DateBase
from .dnagenomebuildtype import DNAGenomeBuildType
from .dnaprovidertype import DNAProviderType
from .dnatesttype import DNATestType
from .mediabase import MediaBase
from .notebase import NoteBase
from .primaryobj import PrimaryObject
from .tagbase import TagBase

_ = glocale.translation.gettext

LOG = logging.getLogger(".dnatest")


# -------------------------------------------------------------------------
#
# DNATest
#
# -------------------------------------------------------------------------
class DNATest(
    CitationBase,
    NoteBase,
    MediaBase,
    DNAAttributeBase,
    DateBase,
    PrimaryObject,
):
    """
    A DNA test kit for a single person at a single provider.

    One DNATest record represents one kit. A person who has tested at
    multiple providers has one DNATest per provider. The kit may be
    unidentified (person_handle is None) when the kit owner has not yet
    been linked to a person in the tree.
    """

    def __init__(self, source=None):
        """
        Create a new DNATest instance, copying from source if present.

        :param source: A DNATest used to initialize the new instance.
        :type source: DNATest
        """
        PrimaryObject.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        MediaBase.__init__(self, source)
        DNAAttributeBase.__init__(self)
        DateBase.__init__(self, source)

        if source:
            self.__person_handle = source.__person_handle
            self.__account_name = source.__account_name
            self.__provider = DNAProviderType(source.__provider)
            self.__kit_id = source.__kit_id
            self.__test_type = DNATestType(source.__test_type)
            self.__genome_build = DNAGenomeBuildType(source.__genome_build)
            self.__haplogroup = source.__haplogroup
        else:
            self.__person_handle = None
            self.__account_name = ""
            self.__provider = DNAProviderType()
            self.__kit_id = ""
            self.__test_type = DNATestType()
            self.__genome_build = DNAGenomeBuildType()
            self.__haplogroup = ""

    def serialize(self, no_text_date=False):
        """
        Convert the data held in the DNATest to a Python tuple representing
        all persistent data elements.

        :returns: tuple of persistent data
        :rtype: tuple
        """
        return (
            self.handle,
            self.gramps_id,
            self.__person_handle,
            self.__account_name,
            self.__provider.serialize(),
            self.__kit_id,
            self.__test_type.serialize(),
            self.__genome_build.serialize(),
            DateBase.serialize(self, no_text_date),
            self.__haplogroup,
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
        attr_dict["person_handle"] = self.__person_handle
        attr_dict["account_name"] = self.__account_name
        attr_dict["provider"] = self.__provider
        attr_dict["kit_id"] = self.__kit_id
        attr_dict["test_type"] = self.__test_type
        attr_dict["genome_build"] = self.__genome_build
        attr_dict["haplogroup"] = self.__haplogroup
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using the provided dictionary.
        """
        self.__person_handle = attr_dict.pop("person_handle")
        self.__account_name = attr_dict.pop("account_name")
        self.__provider = attr_dict.pop("provider")
        self.__kit_id = attr_dict.pop("kit_id")
        self.__test_type = attr_dict.pop("test_type")
        self.__genome_build = attr_dict.pop("genome_build")
        self.__haplogroup = attr_dict.pop("haplogroup")
        super().set_object_state(attr_dict)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: dict containing the schema
        :rtype: dict
        """
        # pylint: disable=import-outside-toplevel
        from .date import Date
        from .dnaattr import DNAAttribute
        from .mediaref import MediaRef

        return {
            "type": "object",
            "title": _("DNA Test"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {
                    "type": "string",
                    "maxLength": 50,
                    "title": _("Handle"),
                },
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "person_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Person"),
                },
                "account_name": {"type": "string", "title": _("Account name")},
                "provider": DNAProviderType.get_schema(),
                "kit_id": {"type": "string", "title": _("Kit ID")},
                "test_type": DNATestType.get_schema(),
                "genome_build": DNAGenomeBuildType.get_schema(),
                "date": Date.get_schema(),
                "haplogroup": {"type": "string", "title": _("Haplogroup")},
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
        back into the data in a DNATest structure.

        :param data: tuple containing the persistent data
        :type data: tuple
        """
        (
            self.handle,
            self.gramps_id,
            self.__person_handle,
            self.__account_name,
            provider,
            self.__kit_id,
            test_type,
            genome_build,
            date,
            self.__haplogroup,
            citation_list,
            note_list,
            media_list,
            attribute_list,
            self.change,
            tag_list,
            self.private,
        ) = data

        self.__provider = DNAProviderType()
        self.__provider.unserialize(provider)
        self.__test_type = DNATestType()
        self.__test_type.unserialize(test_type)
        self.__genome_build = DNAGenomeBuildType()
        self.__genome_build.unserialize(genome_build)
        DateBase.unserialize(self, date)
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
        if classname == "Person":
            return self.__person_handle == handle
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references to handles in handle_list.
        """
        if classname == "Person" and self.__person_handle in handle_list:
            self.__person_handle = None

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old_handle with new_handle.
        """
        if classname == "Person" and self.__person_handle == old_handle:
            self.__person_handle = new_handle

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.
        """
        return [
            self.__account_name,
            self.__kit_id,
            self.__haplogroup,
            str(self.__provider),
            str(self.__test_type),
            self.gramps_id,
        ]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.
        """
        return self.media_list + self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.
        """
        return self.media_list + self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.
        """
        return self.media_list + self.attribute_list

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
        if self.__person_handle:
            ret.append(("Person", self.__person_handle))
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        """
        return self.get_citation_child_list()

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this DNATest.

        :param acquisition: The DNATest to merge with the present one.
        :type acquisition: DNATest
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_person_handle(self, handle):
        """Set the handle of the person who took this test."""
        self.__person_handle = handle

    def get_person_handle(self):
        """Return the handle of the person who took this test, or None."""
        return self.__person_handle

    person_handle = property(get_person_handle, set_person_handle)

    def set_account_name(self, name):
        """Set the account name as shown on the provider platform."""
        self.__account_name = name

    def get_account_name(self):
        """Return the account name as shown on the provider platform."""
        return self.__account_name

    account_name = property(get_account_name, set_account_name)

    def set_provider(self, provider):
        """Set the testing provider."""
        self.__provider.set(provider)

    def get_provider(self):
        """Return the testing provider."""
        return self.__provider

    provider = property(get_provider, set_provider)

    def set_kit_id(self, kit_id):
        """Set the provider-assigned kit identifier."""
        self.__kit_id = kit_id

    def get_kit_id(self):
        """Return the provider-assigned kit identifier."""
        return self.__kit_id

    kit_id = property(get_kit_id, set_kit_id)

    def set_test_type(self, test_type):
        """Set the test type."""
        self.__test_type.set(test_type)

    def get_test_type(self):
        """Return the test type."""
        return self.__test_type

    test_type = property(get_test_type, set_test_type)

    def set_genome_build(self, build):
        """Set the genome reference assembly."""
        self.__genome_build.set(build)

    def get_genome_build(self):
        """Return the genome reference assembly."""
        return self.__genome_build

    genome_build = property(get_genome_build, set_genome_build)

    def set_haplogroup(self, haplogroup):
        """Set the haplogroup."""
        self.__haplogroup = haplogroup

    def get_haplogroup(self):
        """Return the haplogroup."""
        return self.__haplogroup

    haplogroup = property(get_haplogroup, set_haplogroup)
