#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010       Nick Hall
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
Family object for Gramps.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn
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
from .eventref import EventRef
from .ldsordbase import LdsOrdBase
from .tagbase import TagBase
from .childref import ChildRef
from .familyreltype import FamilyRelType
from .const import IDENTICAL, EQUAL, DIFFERENT
from .handle import Handle

LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# Family class
#
#-------------------------------------------------------------------------
class Family(CitationBase, NoteBase, MediaBase, AttributeBase, LdsOrdBase,
             PrimaryObject):
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
        AttributeBase.__init__(self)
        LdsOrdBase.__init__(self)
        self.father_handle = None
        self.mother_handle = None
        self.child_ref_list = []
        self.type = FamilyRelType()
        self.event_ref_list = []
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
        return (self.handle, self.gramps_id, self.father_handle,
                self.mother_handle,
                [cr.serialize() for cr in self.child_ref_list],
                self.type.serialize(),
                [er.serialize() for er in self.event_ref_list],
                MediaBase.serialize(self),
                AttributeBase.serialize(self),
                LdsOrdBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
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
        return {"_class": "Family",
                "handle": Handle("Family", self.handle),
                "gramps_id": self.gramps_id,
                "father_handle": Handle("Person", self.father_handle),
                "mother_handle": Handle("Person", self.mother_handle),
                "child_ref_list": [cr.to_struct() for cr in self.child_ref_list],
                "type": self.type.to_struct(),
                "event_ref_list": [er.to_struct() for er in self.event_ref_list],
                "media_list": MediaBase.to_struct(self),
                "attribute_list": AttributeBase.to_struct(self),
                "lds_ord_list": LdsOrdBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "change": self.change,
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Family()
        return (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("gramps_id", default.gramps_id),
                Handle.from_struct(struct.get("father_handle",
                                              default.father_handle)),
                Handle.from_struct(struct.get("mother_handle",
                                              default.mother_handle)),
                [ChildRef.from_struct(cr)
                 for cr in struct.get("child_ref_list",
                                      default.child_ref_list)],
                FamilyRelType.from_struct(struct.get("type", {})),
                [EventRef.from_struct(er)
                 for er in struct.get("event_ref_list",
                                      default.event_ref_list)],
                MediaBase.from_struct(struct.get("media_list",
                                                 default.media_list)),
                AttributeBase.from_struct(struct.get("attribute_list",
                                                     default.attribute_list)),
                LdsOrdBase.from_struct(struct.get("lds_ord_list",
                                                  default.lds_ord_list)),
                CitationBase.from_struct(struct.get("citation_list",
                                                    default.citation_list)),
                NoteBase.from_struct(struct.get("note_list",
                                                default.note_list)),
                struct.get("change", default.change),
                TagBase.from_struct(struct.get("tag_list", default.tag_list)),
                struct.get("private", default.private))

    @classmethod
    def get_schema(cls):
        from .mediaref import MediaRef
        from .ldsord import LdsOrd
        from .childref import ChildRef
        from .attribute import Attribute
        return {
            "handle": Handle("Family", "FAMILY-HANDLE"),
            "gramps_id": str,
            "father_handle": Handle("Person", "PERSON-HANDLE"),
            "mother_handle": Handle("Person", "PERSON-HANDLE"),
            "child_ref_list": [ChildRef],
            "type": FamilyRelType,
            "event_ref_list": [EventRef],
            "media_list": [MediaRef],
            "attribute_list": [Attribute],
            "lds_ord_list": [LdsOrd],
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "change": int,
            "tag_list": [Handle("Tag", "TAG-HANDLE")],
            "private": bool
        }

    @classmethod
    def get_labels(cls, _):
        return {
            "_class": _("Family"),
            "handle": _("Handle"),
            "gramps_id": _("Gramps ID"),
            "father_handle": _("Father"),
            "mother_handle": _("Mother"),
            "child_ref_list": _("Children"),
            "type": _("Relationship"),
            "event_ref_list": _("Events"),
            "media_list": _("Media"),
            "attribute_list": _("Attributes"),
            "lds_ord_list": _("LDS ordinances"),
            "citation_list": _("Citations"),
            "note_list": _("Notes"),
            "change": _("Last changed"),
            "tag_list": _("Tags"),
            "private": _("Private"),
        }

    @classmethod
    def field_aliases(cls):
        """
        Return dictionary of alias to full field names
        for this object class.
        """
        return {
            "mother_surname": "mother_handle.primary_name.surname_list.0.surname",
            "mother_given": "mother_handle.primary_name.first_name",
            "father_surname": "father_handle.primary_name.surname_list.0.surname",
            "father_given": "father_handle.primary_name.first_name",
        }

    @classmethod
    def get_extra_secondary_fields(cls):
        """
        Return a list of full field names and types for secondary
        fields that are not directly listed in the schema.
        """
        return [
            ("father_handle.primary_name.surname_list.0.surname", str),
            ("father_handle.primary_name.first_name", str),
            ("mother_handle.primary_name.surname_list.0.surname", str),
            ("mother_handle.primary_name.first_name", str),
        ]

    @classmethod
    def get_index_fields(cls):
        return [
            "father_handle.primary_name.surname_list.0.surname",
            "father_handle.primary_name.first_name",
            "mother_handle.primary_name.surname_list.0.surname",
            "mother_handle.primary_name.first_name",
        ]

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Family structure.
        """
        (self.handle, self.gramps_id, self.father_handle, self.mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, citation_list, note_list,
         self.change, tag_list, self.private) = data

        self.type = FamilyRelType()
        self.type.unserialize(the_type)
        self.event_ref_list = [EventRef().unserialize(er)
                               for er in event_ref_list]
        self.child_ref_list = [ChildRef().unserialize(cr)
                               for cr in child_ref_list]
        MediaBase.unserialize(self, media_list)
        AttributeBase.unserialize(self, attribute_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        LdsOrdBase.unserialize(self, lds_seal_list)
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
        if classname == 'Event':
            return handle in [ref.ref for ref in self.event_ref_list]
        elif classname == 'Person':
            return handle in ([ref.ref for ref in self.child_ref_list]
                              + [self.father_handle, self.mother_handle])
        elif classname == 'Place':
            return handle in [x.place for x in self.lds_ord_list]
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        if classname == 'Event':
            new_list = [ref for ref in self.event_ref_list
                        if ref.ref not in handle_list]
            self.event_ref_list = new_list
        elif classname == 'Person':
            new_list = [ref for ref in self.child_ref_list
                        if ref.ref not in handle_list]
            self.child_ref_list = new_list
            if self.father_handle in handle_list:
                self.father_handle = None
            if self.mother_handle in handle_list:
                self.mother_handle = None
        elif classname == 'Place':
            for lds_ord in self.lds_ord_list:
                if lds_ord.place in handle_list:
                    lds_ord.place = None

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
        if classname == 'Event':
            refs_list = [ref.ref for ref in self.event_ref_list]
            new_ref = None
            if new_handle in refs_list:
                new_ref = self.event_ref_list[refs_list.index(new_handle)]
            n_replace = refs_list.count(old_handle)
            for ix_replace in range(n_replace):
                idx = refs_list.index(old_handle)
                self.event_ref_list[idx].ref = new_handle
                refs_list[idx] = new_handle
                if new_ref:
                    evt_ref = self.event_ref_list[idx]
                    equi = new_ref.is_equivalent(evt_ref)
                    if equi != DIFFERENT:
                        if equi == EQUAL:
                            new_ref.merge(evt_ref)
                        self.event_ref_list.pop(idx)
                        refs_list.pop(idx)
        elif classname == 'Person':
            refs_list = [ref.ref for ref in self.child_ref_list]
            new_ref = None
            if new_handle in refs_list:
                new_ref = self.child_ref_list[refs_list.index(new_handle)]
            n_replace = refs_list.count(old_handle)
            for ix_replace in range(n_replace):
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
        elif classname == 'Place':
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
        check_list = self.media_list + self.attribute_list + \
            self.lds_ord_list + self.child_ref_list + self.event_ref_list
        return check_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        check_list = self.media_list + self.attribute_list + \
            self.lds_ord_list + self.child_ref_list + \
            self.event_ref_list
        return check_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles() + \
                self.get_referenced_citation_handles()
        ret += [('Person', handle) for handle
                in ([ref.ref for ref in self.child_ref_list] +
                    [self.father_handle, self.mother_handle])
                if handle]
        ret += self.get_referenced_tag_handles()
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects..

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.media_list + self.attribute_list + \
            self.lds_ord_list + self.child_ref_list + self.event_ref_list

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
        new_list = [ref for ref in self.child_ref_list
                    if ref.ref != child_ref.ref]
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
        new_list = [ref for ref in self.child_ref_list
                    if ref.ref != child_handle]
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
                elif equi == EQUAL:
                    childref.merge(addendum)
                    break
            else:
                self.child_ref_list.append(addendum)

    def add_event_ref(self, event_ref):
        """
        Add the :class:`~.eventref.EventRef` to the Family instance's
        :class:`~.eventref.EventRef` list.

        This is accomplished by assigning the :class:`~.eventref.EventRef` for
        the valid :class:`~.event.Event` in the current database.

        :param event_ref: the :class:`~.eventref.EventRef` to be added to the
                          Person's :class:`~.eventref.EventRef` list.
        :type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")
        self.event_ref_list.append(event_ref)

    def get_event_list(self):
        warn("Use get_event_ref_list instead of get_event_list",
             DeprecationWarning, 2)
        # Wrapper for old API
        # remove when transitition done.
        event_handle_list = []
        for event_ref in self.get_event_ref_list():
            event_handle_list.append(event_ref.get_reference_handle())
        return event_handle_list

    def get_event_ref_list(self):
        """
        Return the list of :class:`~.eventref.EventRef` objects associated with
        :class:`~.event.Event` instances.

        :returns: Returns the list of :class:`~.eventref.EventRef` objects
                  associated with the Family instance.
        :rtype: list
        """
        return self.event_ref_list

    def set_event_ref_list(self, event_ref_list):
        """
        Set the Family instance's :class:`~.eventref.EventRef` list to the
        passed list.

        :param event_ref_list: List of valid :class:`~.eventref.EventRef`
                               objects
        :type event_ref_list: list
        """
        self.event_ref_list = event_ref_list

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
                elif equi == EQUAL:
                    eventref.merge(addendum)
                    break
            else:
                self.event_ref_list.append(addendum)
