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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Person object for Gramps.
"""

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
from .addressbase import AddressBase
from .ldsordbase import LdsOrdBase
from .urlbase import UrlBase
from .tagbase import TagBase
from .name import Name
from .eventref import EventRef
from .personref import PersonRef
from .attrtype import AttributeType
from .eventroletype import EventRoleType
from .attribute import Attribute
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Person class
#
#-------------------------------------------------------------------------
class Person(CitationBase, NoteBase, AttributeBase, MediaBase,
             AddressBase, UrlBase, LdsOrdBase, PrimaryObject):
    """
    The Person record is the Gramps in-memory representation of an
    individual person. It contains all the information related to
    an individual.

    Person objects are usually created in one of two ways.

    1. Creating a new person object, which is then initialized and added to
       the database.
    2. Retrieving an object from the database using the records handle.

    Once a Person object has been modified, it must be committed
    to the database using the database object's commit_person function,
    or the changes will be lost.

    """

    UNKNOWN = 2
    MALE = 1
    FEMALE = 0

    def __init__(self, data=None):
        """
        Create a new Person instance.

        After initialization, most data items have empty or null values,
        including the database handle.
        """
        PrimaryObject.__init__(self)
        CitationBase.__init__(self)
        NoteBase.__init__(self)
        MediaBase.__init__(self)
        AttributeBase.__init__(self)
        AddressBase.__init__(self)
        UrlBase.__init__(self)
        LdsOrdBase.__init__(self)
        self.primary_name = Name()
        self.event_ref_list = []
        self.family_list = []
        self.parent_family_list = []
        self.alternate_names = []
        self.person_ref_list = []
        self.__gender = Person.UNKNOWN
        self.death_ref_index = -1
        self.birth_ref_index = -1
        if data:
            self.unserialize(data)

        # We hold a reference to the GrampsDB so that we can maintain
        # its genderStats.  It doesn't get set here, but from
        # GenderStats.count_person.

    def __eq__(self, other):
        return isinstance(other, Person) and self.handle == other.handle

    def __ne__(self, other):
        return not self == other

    def serialize(self):
        """
        Convert the data held in the Person to a Python tuple that
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
            self.handle,                                         #  0
            self.gramps_id,                                      #  1
            self.__gender,                                       #  2
            self.primary_name.serialize(),                       #  3
            [name.serialize() for name in self.alternate_names], #  4
            self.death_ref_index,                                #  5
            self.birth_ref_index,                                #  6
            [er.serialize() for er in self.event_ref_list],      #  7
            self.family_list,                                    #  8
            self.parent_family_list,                             #  9
            MediaBase.serialize(self),                           # 10
            AddressBase.serialize(self),                         # 11
            AttributeBase.serialize(self),                       # 12
            UrlBase.serialize(self),                             # 13
            LdsOrdBase.serialize(self),                          # 14
            CitationBase.serialize(self),                        # 15
            NoteBase.serialize(self),                            # 16
            self.change,                                         # 17
            TagBase.serialize(self),                             # 18
            self.private,                                        # 19
            [pr.serialize() for pr in self.person_ref_list]      # 20
            )

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .mediaref import MediaRef
        from .address import Address
        from .url import Url
        from .ldsord import LdsOrd
        return {
            "type": "object",
            "title": _("Person"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string",
                           "maxLength": 50,
                           "title": _("Handle")},
                "gramps_id": {"type": "string",
                              "title": _("Gramps ID")},
                "gender": {"type": "integer",
                           "minimum": 0,
                           "maximum": 2,
                           "title": _("Gender")},
                "primary_name": Name.get_schema(),
                "alternate_names": {"type": "array",
                                    "items": Name.get_schema(),
                                    "title": _("Alternate names")},
                "death_ref_index": {"type": "integer",
                                    "title": _("Death reference index")},
                "birth_ref_index": {"type": "integer",
                                    "title": _("Birth reference index")},
                "event_ref_list": {"type": "array",
                                   "items": EventRef.get_schema(),
                                   "title": _("Event references")},
                "family_list": {"type": "array",
                                "items": {"type": "string",
                                          "maxLength": 50},
                                "title": _("Families")},
                "parent_family_list": {"type": "array",
                                       "items": {"type": "string",
                                                 "maxLength": 50},
                                       "title": _("Parent families")},
                "media_list": {"type": "array",
                               "items": MediaRef.get_schema(),
                               "title": _("Media")},
                "address_list": {"type": "array",
                                 "items": Address.get_schema(),
                                 "title": _("Addresses")},
                "attribute_list": {"type": "array",
                                   "items": Attribute.get_schema(),
                                   "title": _("Attributes")},
                "urls": {"type": "array",
                         "items": Url.get_schema(),
                         "title": _("Urls")},
                "lds_ord_list": {"type": "array",
                                 "items": LdsOrd.get_schema(),
                                 "title": _("LDS ordinances")},
                "citation_list": {"type": "array",
                                  "items": {"type": "string",
                                            "maxLength": 50},
                                  "title": _("Citations")},
                "note_list": {"type": "array",
                              "items": {"type": "string",
                                        "maxLength": 50},
                              "title": _("Notes")},
                "change": {"type": "integer",
                           "title": _("Last changed")},
                "tag_list": {"type": "array",
                             "items": {"type": "string",
                                       "maxLength": 50},
                             "title": _("Tags")},
                "private": {"type": "boolean",
                            "title": _("Private")},
                "person_ref_list": {"type": "array",
                                    "items": PersonRef.get_schema(),
                                    "title": _("Person references")}
            }
        }

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Person object.

        :param data: tuple containing the persistent data associated the
                     Person object
        :type data: tuple
        """
        (self.handle,             #  0
         self.gramps_id,          #  1
         self.__gender,           #  2
         primary_name,            #  3
         alternate_names,         #  4
         self.death_ref_index,    #  5
         self.birth_ref_index,    #  6
         event_ref_list,          #  7
         self.family_list,        #  8
         self.parent_family_list, #  9
         media_list,              # 10
         address_list,            # 11
         attribute_list,          # 12
         urls,                    # 13
         lds_ord_list,            # 14
         citation_list,           # 15
         note_list,               # 16
         self.change,             # 17
         tag_list,                # 18
         self.private,            # 19
         person_ref_list,         # 20
        ) = data

        self.primary_name = Name()
        self.primary_name.unserialize(primary_name)
        self.alternate_names = [Name().unserialize(name)
                                for name in alternate_names]
        self.event_ref_list = [EventRef().unserialize(er)
                               for er in event_ref_list]
        self.person_ref_list = [PersonRef().unserialize(pr)
                                for pr in person_ref_list]
        MediaBase.unserialize(self, media_list)
        LdsOrdBase.unserialize(self, lds_ord_list)
        AddressBase.unserialize(self, address_list)
        AttributeBase.unserialize(self, attribute_list)
        UrlBase.unserialize(self, urls)
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
        if classname == 'Event':
            return any(ref.ref == handle for ref in self.event_ref_list)
        elif classname == 'Person':
            return any(ref.ref == handle for ref in self.person_ref_list)
        elif classname == 'Family':
            return any(ref == handle
                       for ref in self.family_list + self.parent_family_list +
                       [ordinance.famc for ordinance in self.lds_ord_list])
        elif classname == 'Place':
            return any(ordinance.place == handle
                       for ordinance in self.lds_ord_list)
        return False

    def _remove_handle_references(self, classname, handle_list):
        if classname == 'Event':
            # Keep a copy of the birth and death references
            birth_ref = self.get_birth_ref()
            death_ref = self.get_death_ref()

            new_list = [ref for ref in self.event_ref_list
                        if ref.ref not in handle_list]
            # If deleting removing the reference to the event
            # to which birth or death ref_index points, unset the index
            if (self.birth_ref_index != -1
                    and self.event_ref_list[self.birth_ref_index].ref
                    in handle_list):
                self.set_birth_ref(None)
            if (self.death_ref_index != -1
                    and self.event_ref_list[self.death_ref_index].ref
                    in handle_list):
                self.set_death_ref(None)
            self.event_ref_list = new_list

            # Reset the indexes after deleting the event from even_ref_list
            if self.birth_ref_index != -1:
                self.set_birth_ref(birth_ref)
            if self.death_ref_index != -1:
                self.set_death_ref(death_ref)
        elif classname == 'Person':
            new_list = [ref for ref in self.person_ref_list
                        if ref.ref not in handle_list]
            self.person_ref_list = new_list
        elif classname == 'Family':
            new_list = [handle for handle in self.family_list
                        if handle not in handle_list]
            self.family_list = new_list
            new_list = [handle for handle in self.parent_family_list
                        if handle not in handle_list]
            self.parent_family_list = new_list
            for ordinance in self.lds_ord_list:
                if ordinance.famc in handle_list:
                    ordinance.famc = None
        elif classname == 'Place':
            for ordinance in self.lds_ord_list:
                if ordinance.place in handle_list:
                    ordinance.place = None

    def _replace_handle_reference(self, classname, old_handle, new_handle):
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
                        if idx < self.birth_ref_index:
                            self.birth_ref_index -= 1
                        elif idx == self.birth_ref_index:
                            self.birth_ref_index = -1
                            # birth_ref_index should be recalculated which
                            # needs database access!
                        if idx < self.death_ref_index:
                            self.death_ref_index -= 1
                        elif idx == self.death_ref_index:
                            self.death_ref_index = -1
                            # death_ref_index should be recalculated which
                            # needs database access!
        elif classname == 'Person':
            refs_list = [ref.ref for ref in self.person_ref_list]
            new_ref = None
            if new_handle in refs_list:
                new_ref = self.person_ref_list[refs_list.index(new_handle)]
            n_replace = refs_list.count(old_handle)
            for ix_replace in range(n_replace):
                idx = refs_list.index(old_handle)
                self.person_ref_list[idx].ref = new_handle
                refs_list[idx] = new_handle
                if new_ref:
                    person_ref = self.person_ref_list[idx]
                    equi = new_ref.is_equivalent(person_ref)
                    if equi != DIFFERENT:
                        if equi == EQUAL:
                            new_ref.merge(person_ref)
                        self.person_ref_list.pop(idx)
                        refs_list.pop(idx)
        elif classname == 'Family':
            while old_handle in self.family_list:
                ix = self.family_list.index(old_handle)
                self.family_list[ix] = new_handle
            while old_handle in self.parent_family_list:
                ix = self.parent_family_list.index(old_handle)
                self.parent_family_list[ix] = new_handle
            handle_list = [ordinance.famc for ordinance in self.lds_ord_list]
            while old_handle in handle_list:
                ix = handle_list.index(old_handle)
                self.lds_ord_list[ix].famc = new_handle
                handle_list[ix] = ''
        elif classname == "Place":
            handle_list = [ordinance.place for ordinance in self.lds_ord_list]
            while old_handle in handle_list:
                ix = handle_list.index(old_handle)
                self.lds_ord_list[ix].place = new_handle
                handle_list[ix] = ''

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
        check_list = self.lds_ord_list
        add_list = [_f for _f in check_list if _f]
        return ([self.primary_name] +
                self.media_list +
                self.alternate_names +
                self.address_list +
                self.attribute_list +
                self.urls +
                self.event_ref_list +
                add_list +
                self.person_ref_list
               )

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return ([self.primary_name] +
                self.media_list +
                self.alternate_names +
                self.address_list +
                self.attribute_list +
                self.lds_ord_list +
                self.person_ref_list +
                self.event_ref_list
               )

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return ([self.primary_name] +
                self.media_list +
                self.alternate_names +
                self.address_list +
                self.attribute_list +
                self.lds_ord_list +
                self.person_ref_list +
                self.event_ref_list
               )

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return [('Family', handle) for handle in
                (self.family_list + self.parent_family_list)] + (
                    self.get_referenced_note_handles() +
                    self.get_referenced_citation_handles() +
                    self.get_referenced_tag_handles()
                )

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return ([self.primary_name] +
                self.media_list +
                self.alternate_names +
                self.address_list +
                self.attribute_list +
                self.lds_ord_list +
                self.person_ref_list +
                self.event_ref_list
               )

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this person.

        :param acquisition: The person to merge with the present person.
        :type acquisition: Person
        """
        acquisition_id = acquisition.get_gramps_id()
        if acquisition_id:
            attr = Attribute()
            attr.set_type(_("Merged Gramps ID"))
            attr.set_value(acquisition.get_gramps_id())
            self.add_attribute(attr)

        self._merge_privacy(acquisition)
        acquisition.alternate_names.insert(0, acquisition.get_primary_name())
        self._merge_alternate_names(acquisition)
        self._merge_event_ref_list(acquisition)
        self._merge_lds_ord_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_address_list(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_url_list(acquisition)
        self._merge_person_ref_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_tag_list(acquisition)

        list(map(self.add_parent_family_handle,
                 acquisition.get_parent_family_handle_list()))
        list(map(self.add_family_handle, acquisition.get_family_handle_list()))

    def set_primary_name(self, name):
        """
        Set the primary name of the Person to the specified :class:`~.name.Name`
        instance.

        :param name: :class:`~.name.Name` to be assigned to the person
        :type name: :class:`~.name.Name`
        """
        self.primary_name = name

    def get_primary_name(self):
        """
        Return the :class:`~.name.Name` instance marked as the Person's primary
        name.

        :returns: Returns the primary name
        :rtype: :class:`~.name.Name`
        """
        return self.primary_name

    def get_alternate_names(self):
        """
        Return the list of alternate :class:`~.name.Name` instances.

        :returns: List of :class:`~.name.Name` instances
        :rtype: list
        """
        return self.alternate_names

    def set_alternate_names(self, alt_name_list):
        """
        Change the list of alternate names to the passed list.

        :param alt_name_list: List of :class:`~.name.Name` instances
        :type alt_name_list: list
        """
        self.alternate_names = alt_name_list

    def _merge_alternate_names(self, acquisition):
        """
        Merge the list of alternate names from acquisition with our own.

        :param acquisition: the list of alternate names of this object will be
                            merged with the current alternate name list.
        :rtype acquisition: Person
        """
        name_list = self.alternate_names[:]
        primary_name = self.get_primary_name()
        if primary_name and not primary_name.is_empty():
            name_list.insert(0, primary_name)
        for addendum in acquisition.get_alternate_names():
            for name in name_list:
                equi = name.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    name.merge(addendum)
                    break
            else:
                self.alternate_names.append(addendum)

    def add_alternate_name(self, name):
        """
        Add a :class:`~.name.Name` instance to the list of alternative names.

        :param name: :class:`~.name.Name` to add to the list
        :type name: :class:`~.name.Name`
        """
        self.alternate_names.append(name)

    def get_nick_name(self):
        for name in [self.get_primary_name()] + self.get_alternate_names():
            if name.get_nick_name():
                return name.get_nick_name()
        for attr in self.attribute_list:
            if int(attr.type) == AttributeType.NICKNAME:
                return attr.get_value()
        return ''

    def set_gender(self, gender):
        """
        Set the gender of the Person.

        :param gender: Assigns the Person's gender to one of the
                       following constants:

                       - Person.MALE
                       - Person.FEMALE
                       - Person.UNKNOWN
        :type gender: int
        """
        if gender not in (Person.MALE, Person.FEMALE, Person.UNKNOWN):
            raise ValueError('Attempt to assign invalid gender')
        self.__gender = gender

    def get_gender(self):
        """
        Return the gender of the Person.

        :returns: Returns one of the following constants:

                  - Person.MALE
                  - Person.FEMALE
                  - Person.UNKNOWN
        :rtype: int
        """
        return self.__gender

    gender = property(get_gender, set_gender, None,
                      'Returns or sets the gender of the person')

    def set_birth_ref(self, event_ref):
        """
        Assign the birth event to the Person object.

        This is accomplished by assigning the :class:`~.eventref.EventRef` of
        the birth event in the current database.

        :param event_ref: the :class:`~.eventref.EventRef` object associated
                          with the Person's birth.
        :type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")
        if event_ref is None:
            self.birth_ref_index = -1
            return

        # check whether we already have this ref in the list
        for self.birth_ref_index, ref in enumerate(self.event_ref_list):
            if event_ref.is_equal(ref):
                return    # Note: self.birth_ref_index already set

        self.event_ref_list.append(event_ref)
        self.birth_ref_index = len(self.event_ref_list)-1

    def set_death_ref(self, event_ref):
        """
        Assign the death event to the Person object.

        This is accomplished by assigning the :class:`~.eventref.EventRef` of
        the death event in the current database.

        :param event_ref: the :class:`~.eventref.EventRef` object associated
                          with the Person's death.
        :type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")
        if event_ref is None:
            self.death_ref_index = -1
            return

        # check whether we already have this ref in the list
        for self.death_ref_index, ref in enumerate(self.event_ref_list):
            if event_ref.is_equal(ref):
                return    # Note: self.death_ref_index already set

        self.event_ref_list.append(event_ref)
        self.death_ref_index = len(self.event_ref_list)-1

    def get_birth_ref(self):
        """
        Return the :class:`~.eventref.EventRef` for Person's birth event.

        This should correspond to an :class:`~.event.Event` in the database's
        :class:`~.event.Event` list.

        :returns: Returns the birth :class:`~.eventref.EventRef` or None if no
                  birth :class:`~.event.Event` has been assigned.
        :rtype: EventRef
        """

        if 0 <= self.birth_ref_index < len(self.event_ref_list):
            return self.event_ref_list[self.birth_ref_index]
        else:
            return None

    def get_death_ref(self):
        """
        Return the :class:`~.eventref.EventRef` for the Person's death event.

        This should correspond to an :class:`~.event.Event` in the database's
        :class:`~.event.Event` list.

        :returns: Returns the death :class:`~.eventref.EventRef` or None if no
                  death :class:`~.event.Event` has been assigned.
        :rtype: event_ref
        """

        if 0 <= self.death_ref_index < len(self.event_ref_list):
            return self.event_ref_list[self.death_ref_index]
        else:
            return None

    def add_event_ref(self, event_ref):
        """
        Add the :class:`~.eventref.EventRef` to the Person instance's
        :class:`~.eventref.EventRef` list.

        This is accomplished by assigning the :class:`~.eventref.EventRef` of a
        valid :class:`~.event.Event` in the current database.

        :param event_ref: the :class:`~.eventref.EventRef` to be added to the
                          Person's :class:`~.eventref.EventRef` list.
        :type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")

        # check whether we already have this ref in the list
        if not any(event_ref.is_equal(ref) for ref in self.event_ref_list):
            self.event_ref_list.append(event_ref)

    def get_event_ref_list(self):
        """
        Return the list of :class:`~.eventref.EventRef` objects associated with
        :class:`~.event.Event` instances.

        :returns: Returns the list of :class:`~.eventref.EventRef` objects
                  associated with the Person instance.
        :rtype: list
        """
        return self.event_ref_list

    def get_primary_event_ref_list(self):
        """
        Return the list of :class:`~.eventref.EventRef` objects associated with
        :class:`~.event.Event` instances that have been marked as primary
        events.

        :returns: Returns generator of :class:`~.eventref.EventRef` objects
                  associated with the Person instance.
        :rtype: generator
        """
        return (ref for ref in self.event_ref_list
                if ref.get_role() == EventRoleType.PRIMARY
               )

    def set_event_ref_list(self, event_ref_list):
        """
        Set the Person instance's :class:`~.eventref.EventRef` list to the
        passed list.

        :param event_ref_list: List of valid :class:`~.eventref.EventRef`
                               objects.
        :type event_ref_list: list
        """
        self.event_ref_list = event_ref_list

    def _merge_event_ref_list(self, acquisition):
        """
        Merge the list of event references from acquisition with our own.

        :param acquisition: the event references list of this object will be
                            merged with the current event references list.
        :rtype acquisition: Person
        """
        eventref_list = self.event_ref_list[:]
        for idx, addendum in enumerate(acquisition.get_event_ref_list()):
            for eventref in eventref_list:
                equi = eventref.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    eventref.merge(addendum)
                    break
            else:
                self.event_ref_list.append(addendum)
                if (self.birth_ref_index == -1 and
                        idx == acquisition.birth_ref_index):
                    self.birth_ref_index = len(self.event_ref_list) - 1
                if (self.death_ref_index == -1 and
                        idx == acquisition.death_ref_index):
                    self.death_ref_index = len(self.event_ref_list) - 1

    def add_family_handle(self, family_handle):
        """
        Add the :class:`~.family.Family` handle to the Person instance's
        :class:`~.family.Family` list.

        This is accomplished by assigning the handle of a valid
        :class:`~.family.Family` in the current database.

        Adding a :class:`~.family.Family` handle to a Person does not
        automatically update the corresponding :class:`~.family.Family`. The
        developer is responsible to make sure that when a
        :class:`~.family.Family` is added to Person, that the Person is assigned
        to either the father or mother role in the :class:`~.family.Family`.

        :param family_handle: handle of the :class:`~.family.Family` to be added
                              to the Person's :class:`~.family.Family` list.
        :type family_handle: str
        """
        if family_handle not in self.family_list:
            self.family_list.append(family_handle)

    def set_preferred_family_handle(self, family_handle):
        """
        Set the family_handle specified to be the preferred
        :class:`~.family.Family`.

        The preferred :class:`~.family.Family` is determined by the first
        :class:`~.family.Family` in the :class:`~.family.Family` list, and is
        typically used to indicate the preferred :class:`~.family.Family` for
        navigation or reporting.

        The family_handle must already be in the list, or the function
        call has no effect.

        :param family_handle: Handle of the :class:`~.family.Family` to make the
                              preferred :class:`~.family.Family`.
        :type family_handle: str
        :returns: True if the call succeeded, False if the family_handle
                  was not already in the :class:`~.family.Family` list.
        :rtype: bool
        """
        if family_handle in self.family_list:
            self.family_list.remove(family_handle)
            self.family_list = [family_handle] + self.family_list
            return True
        else:
            return False

    def get_family_handle_list(self):
        """
        Return the list of :class:`~.family.Family` handles in which the person
        is a parent or spouse.

        :returns: Returns the list of handles corresponding to the
                  :class:`~.family.Family` records with which the person
                  is associated.
        :rtype: list
        """
        return self.family_list

    def set_family_handle_list(self, family_list):
        """
        Assign the passed list to the Person's list of families in which it is
        a parent or spouse.

        :param family_list: List of :class:`~.family.Family` handles to be
                            associated with the Person
        :type family_list: list
        """
        self.family_list = family_list

    def clear_family_handle_list(self):
        """
        Remove all :class:`~.family.Family` handles from the
        :class:`~.family.Family` list.
        """
        self.family_list = []

    def remove_family_handle(self, family_handle):
        """
        Remove the specified :class:`~.family.Family` handle from the list of
        marriages/partnerships.

        If the handle does not exist in the list, the operation has no effect.

        :param family_handle: :class:`~.family.Family` handle to remove from
                              the list
        :type family_handle: str

        :returns: True if the handle was removed, False if it was not
                  in the list.
        :rtype: bool
        """
        if family_handle in self.family_list:
            self.family_list.remove(family_handle)
            return True
        else:
            return False

    def get_parent_family_handle_list(self):
        """
        Return the list of :class:`~.family.Family` handles in which the person
        is a child.

        :returns: Returns the list of handles corresponding to the
                  :class:`~.family.Family` records with which the person is a
                  child.
        :rtype: list
        """
        return self.parent_family_list

    def set_parent_family_handle_list(self, family_list):
        """
        Return the list of :class:`~.family.Family` handles in which the person
        is a child.

        :returns: Returns the list of handles corresponding to the
                  :class:`~.family.Family` records with which the person is a
                  child.
        :rtype: list
        """
        self.parent_family_list = family_list

    def add_parent_family_handle(self, family_handle):
        """
        Add the :class:`~.family.Family` handle to the Person instance's list of
        families in which it is a child.

        This is accomplished by assigning the handle of a valid
        :class:`~.family.Family` in the current database.

        Adding a :class:`~.family.Family` handle to a Person does not
        automatically update the corresponding :class:`~.family.Family`. The
        developer is responsible to make sure that when a
        :class:`~.family.Family` is added to Person, that the Person is
        added to the :class:`~.family.Family` instance's child list.

        :param family_handle: handle of the :class:`~.family.Family` to be added
                              to the Person's :class:`~.family.Family` list.
        :type family_handle: str
        """
        if not isinstance(family_handle, str):
            raise ValueError("Expecting handle, obtained %s" % str(family_handle))
        if family_handle not in self.parent_family_list:
            self.parent_family_list.append(family_handle)

    def clear_parent_family_handle_list(self):
        """
        Remove all :class:`~.family.Family` handles from the parent
        :class:`~.family.Family` list.
        """
        self.parent_family_list = []

    def remove_parent_family_handle(self, family_handle):
        """
        Remove the specified :class:`~.family.Family` handle from the list of
        parent families (families in which the parent is a child).

        If the handle does not exist in the list, the operation has no effect.

        :param family_handle: :class:`~.family.Family` handle to remove from the
                              list
        :type family_handle: str

        :returns: Returns a tuple of three strings, consisting of the
                  removed handle, relationship to mother, and relationship
                  to father. None is returned if the handle is not in the
                  list.
        :rtype: tuple
        """
        if family_handle in self.parent_family_list:
            self.parent_family_list.remove(family_handle)
            return True
        else:
            return False

    def set_main_parent_family_handle(self, family_handle):
        """
        Set the main :class:`~.family.Family` in which the Person is a child.

        The main :class:`~.family.Family` is the :class:`~.family.Family`
        typically used for reports and navigation. This is accomplished by
        moving the :class:`~.family.Family` to the beginning of the list. The
        family_handle must be in the list for this to have any effect.

        :param family_handle: handle of the :class:`~.family.Family` to be
                              marked as the main :class:`~.family.Family`
        :type family_handle: str
        :returns: Returns True if the assignment has successful
        :rtype: bool
        """
        if family_handle in self.parent_family_list:
            self.parent_family_list.remove(family_handle)
            self.parent_family_list = [family_handle] + self.parent_family_list
            return True
        else:
            return False

    def get_main_parents_family_handle(self):
        """
        Return the handle of the :class:`~.family.Family` considered to be the
        main :class:`~.family.Family` in which the Person is a child.

        :returns: Returns the family_handle if a family_handle exists,
                  If no :class:`~.family.Family` is assigned, None is returned
        :rtype: str
        """
        if self.parent_family_list:
            return self.parent_family_list[0]
        else:
            return None

    def add_person_ref(self, person_ref):
        """
        Add the :class:`~.personref.PersonRef` to the Person instance's
        :class:`~.personref.PersonRef` list.

        :param person_ref: the :class:`~.personref.PersonRef` to be added to the
                           Person's :class:`~.personref.PersonRef` list.
        :type person_ref: PersonRef
        """
        if person_ref and not isinstance(person_ref, PersonRef):
            raise ValueError("Expecting PersonRef instance")
        self.person_ref_list.append(person_ref)

    def get_person_ref_list(self):
        """
        Return the list of :class:`~.personref.PersonRef` objects.

        :returns: Returns the list of :class:`~.personref.PersonRef` objects.
        :rtype: list
        """
        return self.person_ref_list

    def set_person_ref_list(self, person_ref_list):
        """
        Set the Person instance's :class:`~.personref.PersonRef` list to the
        passed list.

        :param person_ref_list: List of valid :class:`~.personref.PersonRef`
                                objects
        :type person_ref_list: list
        """
        self.person_ref_list = person_ref_list

    def _merge_person_ref_list(self, acquisition):
        """
        Merge the list of person references from acquisition with our own.

        :param acquisition: the list of person references of this person will be
                            merged with the current person references list.
        :rtype acquisition: Person
        """
        personref_list = self.person_ref_list[:]
        for addendum in acquisition.get_person_ref_list():
            for personref in personref_list:
                equi = personref.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    personref.merge(addendum)
                    break
            else:
                self.person_ref_list.append(addendum)
