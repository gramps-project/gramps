#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010,2017  Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Family object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging
from collections.abc import Collection
from typing_extensions import override

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .attrbase import AttributeBase
from .childref import ChildRef
from .citationbase import CitationBase
from .const import DIFFERENT, EQUAL, IDENTICAL
from .eventbase import EventBase
from .eventref import EventRef
from .familyreltype import FamilyRelType
from .ldsordbase import LdsOrdBase
from .mediabase import MediaBase
from .notebase import NoteBase
from .primaryobj import PrimaryObject
from .tagbase import TagBase

_ = glocale.translation.gettext

LOG = logging.getLogger(".citation")


# -------------------------------------------------------------------------
#
# Family
#
# -------------------------------------------------------------------------
class Family(
    CitationBase,
    NoteBase,
    MediaBase,
    EventBase,
    AttributeBase,
    LdsOrdBase,
    PrimaryObject,
):
    """
    The Family record is the Gramps in-memory representation of the
    relationships between people. It contains all the information
    related to the relationship.

    Family objects are usually created in one of two ways.

    1. Creating a new Family object, which is then initialized and
       added to the database.
    2. Retrieving an object from the database using the records
       handle.

    Once a Family object has been modified, it must be committed
    to the database using the database object's commit_family function,
    or the changes will be lost.
    """

    def __init__(self):
        """
        Create a new Family instance.

        After initialization, most data items have empty or null values,
        including the database handle.
        """
        PrimaryObject.__init__(self)
        CitationBase.__init__(self)
        NoteBase.__init__(self)
        MediaBase.__init__(self)
        EventBase.__init__(self)
        AttributeBase.__init__(self)
        LdsOrdBase.__init__(self)
        self.father_handle = None
        self.mother_handle = None
        self.child_ref_list = []
        self.type = FamilyRelType()
        self.complete = 0

    def serialize(self):
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
        return (
            self.handle,
            self.gramps_id,
            self.father_handle,
            self.mother_handle,
            [cr.serialize() for cr in self.child_ref_list],
            self.type.serialize(),
            EventBase.serialize(self),
            MediaBase.serialize(self),
            AttributeBase.serialize(self),
            LdsOrdBase.serialize(self),
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
        # pylint: disable=import-outside-toplevel
        from .attribute import Attribute
        from .ldsord import LdsOrd
        from .mediaref import MediaRef

        return {
            "type": "object",
            "title": _("Family"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string", "maxLength": 50, "title": _("Handle")},
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "father_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Father"),
                },
                "mother_handle": {
                    "type": ["string", "null"],
                    "maxLength": 50,
                    "title": _("Mother"),
                },
                "child_ref_list": {
                    "type": "array",
                    "items": ChildRef.get_schema(),
                    "title": _("Children"),
                },
                "type": FamilyRelType.get_schema(),
                "event_ref_list": {
                    "type": "array",
                    "items": EventRef.get_schema(),
                    "title": _("Events"),
                },
                "media_list": {
                    "type": "array",
                    "items": MediaRef.get_schema(),
                    "title": _("Media"),
                },
                "attribute_list": {
                    "type": "array",
                    "items": Attribute.get_schema(),
                    "title": _("Attributes"),
                },
                "lds_ord_list": {
                    "type": "array",
                    "items": LdsOrd.get_schema(),
                    "title": _("LDS ordinances"),
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
        back into the data in a Family structure.
        """
        (
            self.handle,
            self.gramps_id,
            self.father_handle,
            self.mother_handle,
            child_ref_list,
            the_type,
            event_ref_list,
            media_list,
            attribute_list,
            lds_seal_list,
            citation_list,
            note_list,
            self.change,
            tag_list,
            self.private,
        ) = data

        self.type = FamilyRelType()
        self.type.unserialize(the_type)
        self.child_ref_list = [ChildRef().unserialize(cr) for cr in child_ref_list]
        MediaBase.unserialize(self, media_list)
        EventBase.unserialize(self, event_ref_list)
        AttributeBase.unserialize(self, attribute_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        LdsOrdBase.unserialize(self, lds_seal_list)
        TagBase.unserialize(self, tag_list)
        return self

    @override
    def _has_handle_reference(self, classname: str, handle: str) -> bool:
        if classname == "Event":
            return self._has_event_reference(handle)
        if classname == "Person":
            return handle in (
                [ref.ref for ref in self.child_ref_list]
                + [self.father_handle, self.mother_handle]
            )
        if classname == "Place":
            return handle in [x.place for x in self.lds_ord_list]
        return False

    @override
    def _remove_handle_references(
        self, classname: str, handle_list: Collection[str]
    ) -> None:
        if classname == "Event":
            self._remove_event_references(handle_list)
        elif classname == "Person":
            new_list = [
                ref for ref in self.child_ref_list if ref.ref not in handle_list
            ]
            self.child_ref_list = new_list
            if self.father_handle in handle_list:
                self.father_handle = None
            if self.mother_handle in handle_list:
                self.mother_handle = None
        elif classname == "Place":
            for lds_ord in self.lds_ord_list:
                if lds_ord.place in handle_list:
                    lds_ord.place = None

    @override
    def _replace_handle_reference(
        self, classname: str, old_handle: str, new_handle: str
    ) -> None:
        if classname == "Event":
            self._replace_event_references(old_handle, new_handle)
        elif classname == "Person":
            refs_list = [ref.ref for ref in self.child_ref_list]
            new_ref = None
            if new_handle in refs_list:
                new_ref = self.child_ref_list[refs_list.index(new_handle)]
            n_replace = refs_list.count(old_handle)
            for _ in range(n_replace):
                idx = refs_list.index(old_handle)
                self.child_ref_list[idx].ref = new_handle
                refs_list[idx] = new_handle
                if new_ref:
                    child_ref = self.child_ref_list[idx]
                    equi = new_ref.is_equivalent(child_ref)
                    if equi != DIFFERENT:
                        if equi == EQUAL:
                            new_ref.merge(child_ref)
                        self.child_ref_list.pop(idx)
                        refs_list.pop(idx)
            if self.father_handle == old_handle:
                self.father_handle = new_handle
            if self.mother_handle == old_handle:
                self.mother_handle = new_handle
        elif classname == "Place":
            for lds_ord in self.lds_ord_list:
                if lds_ord.place == old_handle:
                    lds_ord.place = new_handle

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        add_list = [_f for _f in self.lds_ord_list if _f]
        return self.media_list + self.attribute_list + add_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        check_list = (
            self.media_list
            + self.attribute_list
            + self.lds_ord_list
            + self.child_ref_list
            + self.event_ref_list
        )
        return check_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        check_list = (
            self.media_list
            + self.attribute_list
            + self.lds_ord_list
            + self.child_ref_list
            + self.event_ref_list
        )
        return check_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = (
            self.get_referenced_note_handles() + self.get_referenced_citation_handles()
        )
        ret += [
            ("Person", handle)
            for handle in (
                [ref.ref for ref in self.child_ref_list]
                + [self.father_handle, self.mother_handle]
            )
            if handle
        ]
        ret += self.get_referenced_tag_handles()
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects..

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return (
            self.media_list
            + self.attribute_list
            + self.lds_ord_list
            + self.child_ref_list
            + self.event_ref_list
        )

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this family.

        Lost: handle, id, relation, father, mother of acquisition.

        :param acquisition: The family to merge with the present family.
        :type acquisition: Family
        """
        if self.type != acquisition.type and self.type == FamilyRelType.UNKNOWN:
            self.set_relationship(acquisition.get_relationship())
        self._merge_privacy(acquisition)
        self._merge_event_ref_list(acquisition)
        self._merge_lds_ord_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_child_ref_list(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_relationship(self, relationship_type):
        """
        Set the relationship type between the people identified as the
        father and mother in the relationship.

        The type is a tuple whose first item is an integer constant and whose
        second item is the string. The valid values are:

        =========================  ============================================
        Type                       Description
        =========================  ============================================
        FamilyRelType.MARRIED      indicates a legally recognized married
                                   relationship between two individuals. This
                                   may be either an opposite or a same sex
                                   relationship.
        FamilyRelType.UNMARRIED    indicates a relationship between two
                                   individuals that is not a legally recognized
                                   relationship.
        FamilyRelType.CIVIL_UNION  indicates a legally recongnized, non-married
                                   relationship between two individuals of the
                                   same sex.
        FamilyRelType.UNKNOWN      indicates that the type of relationship
                                   between the two individuals is not know.
        FamilyRelType.CUSTOM       indicates that the type of relationship
                                   between the two individuals does not match
                                   any of the other types.
        =========================  ============================================

        :param relationship_type: (int,str) tuple of the relationship type
               between the father and mother of the relationship.
        :type relationship_type: tuple
        """
        self.type.set(relationship_type)

    def get_relationship(self):
        """
        Return the relationship type between the people identified as the
        father and mother in the relationship.
        """
        return self.type

    def set_father_handle(self, person_handle):
        """
        Set the database handle for :class:`~.person.Person` that corresponds
        to male of the relationship.

        For a same sex relationship, this can represent either of people
        involved in the relationship.

        :param person_handle: :class:`~.person.Person` database handle
        :type person_handle: str
        """
        self.father_handle = person_handle

    def get_father_handle(self):
        """
        Return the database handle of the :class:`~.person.Person` identified
        as the father of the Family.

        :returns: :class:`~.person.Person` database handle
        :rtype: str
        """
        return self.father_handle

    def set_mother_handle(self, person_handle):
        """
        Set the database handle for :class:`~.person.Person` that corresponds
        to male of the relationship.

        For a same sex relationship, this can represent either of people
        involved in the relationship.

        :param person_handle: :class:`~.person.Person` database handle
        :type person_handle: str
        """
        self.mother_handle = person_handle

    def get_mother_handle(self):
        """
        Return the database handle of the :class:`~.person.Person` identified
        as the mother of the Family.

        :returns: :class:`~.person.Person` database handle
        :rtype: str
        """
        return self.mother_handle

    def add_child_ref(self, child_ref):
        """
        Add the database handle for :class:`~.person.Person` to the Family's
        list of children.

        :param child_ref: Child Reference instance
        :type  child_ref: ChildRef
        """
        if not isinstance(child_ref, ChildRef):
            raise ValueError("expecting ChildRef instance")
        self.child_ref_list.append(child_ref)

    def remove_child_ref(self, child_ref):
        """
        Remove the database handle for :class:`~.person.Person` to the Family's
        list of children if the :class:`~.person.Person` is already in the list.

        :param child_ref: Child Reference instance
        :type child_ref: ChildRef
        :returns: True if the handle was removed, False if it was not
                  in the list.
        :rtype: bool
        """
        if not isinstance(child_ref, ChildRef):
            raise ValueError("expecting ChildRef instance")
        new_list = [ref for ref in self.child_ref_list if ref.ref != child_ref.ref]
        self.child_ref_list = new_list

    def remove_child_handle(self, child_handle):
        """
        Remove the database handle for :class:`~.person.Person` to the Family's
        list of children if the :class:`~.person.Person` is already in the list.

        :param child_handle: :class:`~.person.Person` database handle
        :type  child_handle: str
        :returns: True if the handle was removed, False if it was not
                  in the list.
        :rtype: bool
        """
        new_list = [ref for ref in self.child_ref_list if ref.ref != child_handle]
        self.child_ref_list = new_list

    def get_child_ref_list(self):
        """
        Return the list of :class:`~.childref.ChildRef` handles identifying the
        children of the Family.

        :returns: Returns the list of :class:`~.childref.ChildRef` handles
                  associated with the Family.
        :rtype: list
        """
        return self.child_ref_list

    def set_child_ref_list(self, child_ref_list):
        """
        Assign the passed list to the Family's list children.

        :param child_ref_list: List of Child Reference instances to be
                               associated as the Family's list of children.
        :type child_ref_list: list of :class:`~.childref.ChildRef` instances
        """
        self.child_ref_list = child_ref_list

    def _merge_child_ref_list(self, acquisition):
        """
        Merge the list of child references from acquisition with our own.

        :param acquisition: the childref list of this family will be merged
                            with the current childref list.
        :type acquisition: Family
        """
        childref_list = self.child_ref_list[:]
        for addendum in acquisition.get_child_ref_list():
            for childref in childref_list:
                equi = childref.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                if equi == EQUAL:
                    childref.merge(addendum)
                    break
            else:
                self.child_ref_list.append(addendum)

    def _merge_event_ref_list(self, acquisition):
        """
        Merge the list of event references from acquisition with our own.

        :param acquisition: the event references list of this object will be
                            merged with the current event references list.
        :type acquisition: Person
        """
        eventref_list = self.event_ref_list[:]
        for addendum in acquisition.get_event_ref_list():
            for eventref in eventref_list:
                equi = eventref.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                if equi == EQUAL:
                    eventref.merge(addendum)
                    break
            else:
                self.event_ref_list.append(addendum)
