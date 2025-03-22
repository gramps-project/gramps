#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Michiel D. Nauta
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

"""Unittest that tests the code involved in merging"""

import unittest

from .. import (
   Address,
    Attribute,
    AttributeType,
    ChildRef,
    ChildRefType,
    Citation,
    Date,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    FamilyRelType,
    LdsOrd,
    Media,
    MediaRef,
    Name,
    NameType,
    Note,
    NoteType,
    Person,
    PersonRef,
    Place,
    PlaceName,
    PlaceType,
    RepoRef,
    Repository,
    RepositoryType,
    Source,
    SrcAttribute,
    SrcAttributeType,
    StyledText,
    StyledTextTag,
    StyledTextTagType,
    Surname,
    Tag,
    Url,
    UrlType,
)
from ..addressbase import AddressBase
from ..attrbase import AttributeBase
from ..citationbase import CitationBase
from ..const import DIFFERENT, EQUAL, IDENTICAL
from ..ldsordbase import LdsOrdBase
from ..mediabase import MediaBase
from ..notebase import NoteBase
from ..privacybase import PrivacyBase
from ..surnamebase import SurnameBase
from ..tagbase import TagBase
from ..urlbase import UrlBase



class PrivacyBaseTest:
    def test_privacy_merge(self):
        self.assertEqual(self.phoenix.serialize(), self.titanic.serialize())
        self.titanic.set_privacy(True)
        self.ref_obj.set_privacy(True)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class NoteBaseTest:
    def test_note_merge(self):
        note_handle = "123456"
        self.titanic.add_note(note_handle)
        self.ref_obj.add_note(note_handle)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class CitationBaseTest:
    def test_citation_merge(self):
        citation = Citation()
        citation.set_reference_handle("123456")
        citation.set_page("p.10")
        self.titanic.add_citation(citation.handle)
        self.ref_obj.add_citation(citation.handle)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class MediaBaseTest:
    def test_media_merge(self):
        mediaref = MediaRef()
        mediaref.set_reference_handle("123456")
        self.titanic.add_media_reference(mediaref)
        self.ref_obj.add_media_reference(mediaref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class AttrBaseTest:
    def test_attribute_merge(self):
        attr = Attribute()
        attr.set_type(AttributeType.AGE)
        attr.set_value(10)
        self.titanic.add_attribute(attr)
        self.ref_obj.add_attribute(attr)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class UrlBaseTest:
    def test_url_merge(self):
        url = Url()
        url.set_path("http://example.com")
        self.titanic.add_url(url)
        self.ref_obj.add_url(url)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


# ):
    def setUp(self):
        self.phoenix = Media()
        self.phoenix.set_path("example.png")
        self.titanic = Media(self.phoenix)
        self.ref_obj = Media(self.phoenix)


class MediaRefCheck(
   unittest.TestCase,
    PrivacyBaseTest,
    AttrBaseTest,
    CitationBaseTest,
    NoteBaseTest,
):
    def setUp(self):
        self.phoenix = MediaRef()
        self.phoenix.set_rectangle("10 10 90 90")
        self.titanic = MediaRef(self.phoenix)
        self.ref_obj = MediaRef(self.phoenix)

    def test_ref_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle("123456")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_rect_equivalence(self):
        self.titanic.set_rectangle("20 20 80 80")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)


class NameCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest, CitationBaseTest):
    def setUp(self):
        self.phoenix = Name()
        self.phoenix.set_first_name("Willem")
        surname = Surname()
        surname.set_surname("Oranje")
        self.phoenix.add_surname(surname)
        self.titanic = Name(self.phoenix)
        self.ref_obj = Name(self.phoenix)

    def test_datalist_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_first_name("Maurits")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_date_equivalence(self):
        date = Date()
        date.set_yr_mon_day(1999, 12, 5)
        self.titanic.set_date_object(date)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_surname_equivalence(self):
        surname = Surname()
        surname.set_surname("Nassau")
        self.titanic.add_surname(surname)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)


class NoteCheck(unittest.TestCase, PrivacyBaseTest):
    def setUp(self):
        self.phoenix = Note("hello world")
        self.titanic = Note("hello world")
        self.ref_obj = Note("hello world")

   def test_note_replace_handle_reference(self):
        ptag = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Event/handle/e0000",
            ranges=[0, 3],
        )
        self.phoenix.text.set_tags([ptag])
        rtag = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Event/handle/e0001",
            ranges=[0, 3],
        )
        self.ref_obj.text.set_tags([rtag])
        self.phoenix.replace_handle_reference("Event", "e0000", "e0001")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_note_has_handle_reference(self):
        ptag = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Event/handle/e0000",
            ranges=[0, 3],
        )
        self.phoenix.text.set_tags([ptag])
        self.assertTrue(self.phoenix.has_handle_reference("Event", "e0000"))
        self.assertFalse(self.phoenix.has_handle_reference("Event", "e0001"))

    def test_note_get_referenced_handles(self):
        tag0 = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Event/handle/e0000",
            ranges=[0, 2],
        )
        tag1 = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Person/handle/i0001",
            ranges=[2, 3],
        )
        self.phoenix.text.set_tags([tag0, tag1])
        self.phoenix.add_tag("t1234")
        tag_list = self.phoenix.get_referenced_handles()
        self.assertEqual(
            tag_list,
            [("Event", "e0000"), ("Person", "i0001"), ("Tag", "t1234")],
        )
        self.assertFalse(self.phoenix.has_handle_reference("Event", "e0001"))

    def test_note_remove_handle_references(self):
        ptag = StyledTextTag(
            name=StyledTextTagType.LINK,
            value="gramps://Event/handle/e0000",
            ranges=[0, 3],
        )
        self.phoenix.text.set_tags([ptag])
        self.phoenix.remove_handle_references("Event", ["e0000"])
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class NoteBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = NoteBase()
        self.titanic = NoteBase()
        note = Note("hello world")
        note.set_handle("123456")
        self.phoenix.add_note(note.get_handle())

    def test_identical(self):
        ref_note_list = NoteBase(self.phoenix)
        self.titanic.add_note(self.phoenix.get_note_list()[0])
        self.phoenix._merge_note_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_different(self):
        ref_note_list = NoteBase(self.phoenix)
        note = Note("note other")
        note.set_handle("654321")
        self.titanic.add_note(note.get_handle())
        ref_note_list.add_note(note.get_handle())
        self.phoenix._merge_note_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_replace_nonew(self):
        note = Note("note other")
        note.set_handle("654321")
        ref_note_list = NoteBase()
        ref_note_list.add_note(note.get_handle())
        self.phoenix.replace_note_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_replace_newpresent(self):
        note = Note("note other")
        note.set_handle("654321")
        note2 = Note("yet another note")
        note2.set_handle("234567")
        self.phoenix.add_note(note2.get_handle())
        self.phoenix.add_note(note.get_handle())
        ref_note_list = NoteBase()
        ref_note_list.add_note(note2.get_handle())
        ref_note_list.add_note(note.get_handle())
        self.phoenix.replace_note_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_replace_child(self):
        ref_note_list = NoteBase()
        note = Note("")
        note.set_handle("123456")
        ref_note_list.add_note(note.get_handle())
        self.phoenix.replace_note_references("", "")
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

   def test_remove_note_references(self):
        note = Note("note other")
        note.set_handle("654321")
        self.phoenix.add_note(note.get_handle())
        self.phoenix.remove_note_references(["123456", "654321"])
        ref_note_list = NoteBase()
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())


class PersonCheck(
    unittest.TestCase,
    PrivacyBaseTest,
    MediaBaseTest,
    AttrBaseTest,
    NoteBaseTest,
    CitationBaseTest,
):
    def setUp(self):
        self.phoenix = Person()
        name = Name()
        name.set_first_name("Adam")
        self.phoenix.set_primary_name(name)
        self.titanic = Person()
        self.titanic.set_primary_name(name)
        self.ref_obj = Person()
        self.ref_obj.set_primary_name(name)

    def test_replace_eventhandle_nonew(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("654321")
        self.phoenix.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_identical(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        evtref3 = EventRef()
        evtref3.set_reference_handle("654321")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_equal(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        evtref3 = EventRef()
        evtref3.set_reference_handle("654321")
        evtref3.set_privacy(True)
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_different(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        evtref3 = EventRef()
        evtref3.set_reference_handle("654321")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_birth_lower(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("654321")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.birth_ref_index = 2
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.birth_ref_index = 1
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_birth_minusone(self):
        evtref = EventRef()
        evtref.set_reference_handle("654321")
        evtref2 = EventRef()
        evtref2.set_reference_handle("123456")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.birth_ref_index = 1
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.birth_ref_index = -1
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_death_lower(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("654321")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.death_ref_index = 2
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.death_ref_index = 1
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_death_minusone(self):
        evtref = EventRef()
        evtref.set_reference_handle("654321")
        evtref2 = EventRef()
        evtref2.set_reference_handle("123456")
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.death_ref_index = 1
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.death_ref_index = -1
        self.phoenix._replace_handle_reference("Event", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_nonew(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        self.phoenix.add_person_ref(personref)
        personref2 = PersonRef()
        personref2.set_reference_handle("654321")
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._replace_handle_reference("Person", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_identical(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        personref2 = PersonRef()
        personref2.set_reference_handle("234567")
        personref3 = PersonRef()
        personref3.set_reference_handle("654321")
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.phoenix.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref3)
        self.phoenix._replace_handle_reference("Person", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_equal(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        personref.set_privacy(True)
        personref2 = PersonRef()
        personref2.set_reference_handle("234567")
        personref3 = PersonRef()
        personref3.set_reference_handle("654321")
        personref4 = PersonRef()
        personref4.set_reference_handle("654321")
        personref4.set_privacy(True)
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.phoenix.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref4)
        self.phoenix._replace_handle_reference("Person", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_different(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        personref2 = PersonRef()
        personref2.set_reference_handle("234567")
        personref3 = PersonRef()
        personref3.set_reference_handle("654321")
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._replace_handle_reference("Person", "123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_primaryname(self):
        name = Name()
        name.set_first_name("Abel")
        self.titanic.set_primary_name(name)
        self.ref_obj.add_alternate_name(name)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_altname(self):
        name = Name()
        name.set_first_name("Abel")
        self.titanic.add_alternate_name(name)
        self.ref_obj.add_alternate_name(name)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_eventref(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        self.titanic.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_ldsord(self):
        ldsord = LdsOrd()
        ldsord.set_type(LdsOrd.BAPTISM)
        self.titanic.add_lds_ord(ldsord)
        self.ref_obj.add_lds_ord(ldsord)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_address(self):
        address = Address()
        address.set_city("The Hague")
        self.titanic.add_address(address)
        self.ref_obj.add_address(address)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_personref(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        self.titanic.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    # def todo_test_merge_person_aschild(self):
    # pass

    # def todo_test_merge_person_asparent(self):
    # pass

    def test_altname_identical(self):
        name = Name()
        name.set_first_name("Abel")
        name2 = Name()
        name2.set_first_name("Abel")
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_altname_equal(self):
        name = Name()
        name.set_first_name("Abel")
        name2 = Name()
        name2.set_first_name("Abel")
        name2.set_privacy(True)
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name2)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_altname_different(self):
        name = Name()
        name.set_first_name("Abel")
        name2 = Name()
        name2.set_first_name("Cain")
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name)
        self.ref_obj.add_alternate_name(name2)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_identical(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("123456")
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_equal(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("123456")
        evtref2.set_privacy(True)
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_different(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_birthref(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        evtref3 = EventRef()
        evtref3.set_reference_handle("123456")
        self.phoenix.add_event_ref(evtref2)
        self.titanic.add_event_ref(evtref)
        self.titanic.birth_ref_index = 0
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.birth_ref_index = 1
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_deathref(self):
        evtref = EventRef()
        evtref.set_reference_handle("123456")
        evtref2 = EventRef()
        evtref2.set_reference_handle("234567")
        evtref3 = EventRef()
        evtref3.set_reference_handle("123456")
        self.phoenix.add_event_ref(evtref2)
        self.titanic.add_event_ref(evtref)
        self.titanic.death_ref_index = 0
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.death_ref_index = 1
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_identical(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_equal(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        personref2 = PersonRef()
        personref2.set_reference_handle("123456")
        personref2.set_privacy(True)
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_different(self):
        personref = PersonRef()
        personref.set_reference_handle("123456")
        personref2 = PersonRef()
        personref2.set_reference_handle("234567")
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class PlaceCheck(
    unittest.TestCase,
    PrivacyBaseTest,
    MediaBaseTest,
    UrlBaseTest,
    NoteBaseTest,
    CitationBaseTest,
):
    def setUp(self):
        self.phoenix = Place()
        self.phoenix.set_title("Place 1")
        # __init__ copy has bad side effects, don't use it
        # self.titanic = Place(self.phoenix)
        self.titanic = Place()
        self.titanic.set_title("Place 1")
        # __init__ copy has bad side effects, don't use it
        # self.ref_obj = Place(self.phoenix)
        self.ref_obj = Place()
        self.ref_obj.set_title("Place 1")
        self.amsterdam = PlaceName()
        self.amsterdam.set_value("Amsterdam")
        self.rotterdam = PlaceName()
        self.rotterdam.set_value("Rotterdam")
        self.utrecht = PlaceName()
        self.utrecht.set_value("Utrecht")
        self.leiden = PlaceName()
        self.leiden.set_value("Leiden")

    def test_merge_primary_identical(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.amsterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_primary_different(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.rotterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_both_different(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.utrecht)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.rotterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.titanic.add_alternative_name(self.leiden)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        # Base name shouldn't be in alt_names list
        # self.ref_obj.add_alternative_name(self.amsterdam)
        # alt_names must be in correct order for test to pass
        self.ref_obj.add_alternative_name(self.utrecht)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.ref_obj.add_alternative_name(self.leiden)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_alternative_identical(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.rotterdam)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.amsterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.titanic.add_alternative_name(self.rotterdam)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_alternative_different(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.rotterdam)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.amsterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.titanic.add_alternative_name(self.utrecht)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.ref_obj.add_alternative_name(self.utrecht)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_prialt_identical(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.rotterdam)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.rotterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_prialt2(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.rotterdam)
        self.titanic.set_title("Place 2")
        self.titanic.set_name(self.rotterdam)
        self.titanic.set_type(PlaceType.CITY)
        self.titanic.add_alternative_name(self.amsterdam)
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_empty(self):
        self.phoenix.set_name(self.amsterdam)
        self.phoenix.set_type(PlaceType.CITY)
        self.phoenix.add_alternative_name(self.rotterdam)
        self.titanic.set_title("Place 2")
        # titanic gets empty name
        self.titanic.set_type(PlaceType.CITY)
        self.titanic.add_alternative_name(self.utrecht)
        self.titanic.add_alternative_name(PlaceName())  # empty alt_name
        self.ref_obj.set_name(self.amsterdam)
        self.ref_obj.set_type(PlaceType.CITY)
        self.ref_obj.add_alternative_name(self.rotterdam)
        self.ref_obj.add_alternative_name(self.utrecht)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class RepoCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest, UrlBaseTest):
    def setUp(self):
        self.phoenix = Repository()
        self.phoenix.set_name("Repo 1")
        self.phoenix.set_type(RepositoryType.LIBRARY)
        self.titanic = Repository()
        self.titanic.set_name("Repo 1")
        self.titanic.set_type(RepositoryType.LIBRARY)
        self.ref_obj = Repository()
        self.ref_obj.set_name("Repo 1")
        self.ref_obj.set_type(RepositoryType.LIBRARY)

    def test_address(self):
        address = Address()
        address.set_city("Amsterdam")
        self.titanic.add_address(address)
        self.ref_obj.add_address(address)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace(self):
        address = Address()
        address.set_city("Utrecht")
        citation = Citation()
        citation.set_reference_handle("123456")
        address.add_citation(citation.handle)
        self.phoenix.add_address(address)
        address2 = Address()
        address2.set_city("Utrecht")
        citation2 = Citation()
        citation2.set_reference_handle("654321")
        address2.add_citation(citation2.handle)
        self.ref_obj.add_address(address2)
        self.phoenix.replace_citation_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class RepoRefCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest):
    def setUp(self):
        self.phoenix = RepoRef()
        self.phoenix.set_reference_handle("123456")
        self.titanic = RepoRef(self.phoenix)
        self.ref_obj = RepoRef(self.phoenix)

    def test_handle_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle("654321")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_callnr_equivalence(self):
        self.titanic.set_call_number("10")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)


class SourceCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest, MediaBaseTest):
    def setUp(self):
        self.phoenix = Source()
        self.phoenix.set_title("Source 1")
        self.titanic = Source()
        self.titanic.set_title("Source 1")
        self.ref_obj = Source()
        self.ref_obj.set_title("Source 1")

    # def todo_test_replace(self):
    # pass

    def test_merge_datamap(self):
        attr1 = SrcAttribute()
        attr1.set_type("A")
        attr1.set_value("a")
        attr2 = SrcAttribute()
        attr2.set_type("B")
        attr2.set_value("b")
        attr3 = SrcAttribute()
        attr3.set_type("B")
        attr3.set_value("bb")
        attr4 = SrcAttribute()
        attr4.set_type("C")
        attr4.set_value("c")
        self.phoenix.set_attribute_list([attr1, attr2])
        self.titanic.set_attribute_list([attr3, attr4])
        self.ref_obj.set_attribute_list([attr1, attr2, attr3, attr4])
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        self.titanic.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef_identical(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef_equal(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("123456")
        reporef2.set_privacy(True)
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef_different(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("234567")
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_nonew(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("654321")
        self.phoenix.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix.replace_repo_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_identical(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("234567")
        reporef3 = RepoRef()
        reporef3.set_reference_handle("654321")
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_equal(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("234567")
        reporef3 = RepoRef()
        reporef3.set_reference_handle("654321")
        reporef3.set_privacy(True)
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_different(self):
        reporef = RepoRef()
        reporef.set_reference_handle("123456")
        reporef2 = RepoRef()
        reporef2.set_reference_handle("234567")
        reporef3 = RepoRef()
        reporef3.set_reference_handle("654321")
        reporef3.set_call_number("100")
        reporef4 = RepoRef()
        reporef4.set_reference_handle("654321")
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef4)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class CitationBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = CitationBase()
        citation = Citation()
        citation.set_reference_handle("123456")
        self.phoenix.add_citation(citation.handle)
        self.titanic = CitationBase()
        self.obj_list = CitationBase()

    def test_replace_nonew(self):
        citation = Citation()
        citation.set_reference_handle("654321")
        self.obj_list.add_citation(citation.handle)
        self.phoenix.replace_citation_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

    def test_replace_newpresent(self):
        citation = Citation()
        citation.set_reference_handle("654321")
        citation.set_page("p.10")
        citation2 = Citation()
        citation2.set_reference_handle("234567")
        self.phoenix.add_citation(citation.handle)
        self.phoenix.add_citation(citation2.handle)
        self.obj_list.add_citation(citation2.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix.replace_citation_references("123456", "654321")
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

    # def todo_test_replace_child(self):
    # pass

    def test_merge_identical(self):
        citation = Citation()
        citation.set_reference_handle("123456")
        self.titanic.add_citation(citation.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix._merge_citation_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

    def test_merge_different(self):
        citation = Citation()
        citation.set_reference_handle("234567")
        citation2 = Citation()
        citation2.set_reference_handle("123456")
        self.titanic.add_citation(citation.handle)
        self.obj_list.add_citation(citation2.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix._merge_citation_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())


class CitationCheck(unittest.TestCase, PrivacyBaseTest, MediaBaseTest, NoteBaseTest):
    def setUp(self):
        self.phoenix = Citation()
        self.phoenix.set_reference_handle("123456")
        self.phoenix.set_page("p.10")
        self.titanic = Citation()
        self.titanic.set_reference_handle("123456")
        self.titanic.set_page("p.10")
        self.ref_obj = Citation()
        self.ref_obj.set_reference_handle("123456")
        self.ref_obj.set_page("p.10")

    def test_merge_confidence(self):
        known_values = (
            (0, 0, 0),
            (0, 1, 0),
            (0, 2, 0),
            (0, 3, 0),
            (0, 4, 0),
            (1, 0, 0),
            (1, 1, 1),
            (1, 2, 1),
            (1, 3, 1),
            (1, 4, 4),
            (2, 0, 0),
            (2, 1, 1),
            (2, 2, 2),
            (2, 3, 3),
            (2, 4, 4),
            (3, 0, 0),
            (3, 1, 1),
            (3, 2, 3),
            (3, 3, 3),
            (3, 4, 4),
            (4, 0, 0),
            (4, 1, 4),
            (4, 2, 4),
            (4, 3, 4),
            (4, 4, 4),
        )
        for val1, val2, val_merge in known_values:
            self.phoenix.set_confidence_level(val1)
            self.titanic.set_confidence_level(val2)
            self.ref_obj.set_confidence_level(val_merge)
            self.phoenix.merge(self.titanic)
            self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_datamap(self):
        attr1 = SrcAttribute()
        attr1.set_type("A")
        attr1.set_value("a")
        attr2 = SrcAttribute()
        attr2.set_type("B")
        attr2.set_value("b")
        attr3 = SrcAttribute()
        attr3.set_type("B")
        attr3.set_value("bb")
        attr4 = SrcAttribute()
        attr4.set_type("C")
        attr4.set_value("c")
        self.phoenix.set_attribute_list([attr1, attr2])
        self.titanic.set_attribute_list([attr3, attr4])
        self.ref_obj.set_attribute_list([attr1, attr2, attr3, attr4])
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class SurnameCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = Surname()
        self.phoenix.set_prefix("van")
        self.titanic = Surname(self.phoenix)

    def test_datalist_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_prefix("von")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_primary_equivalence(self):
        self.titanic.set_primary(False)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    # A Surname can never be EQUAL to another Surname.

    # There is no merge method to check.


class SurnameBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = SurnameBase()
        surname = Surname()
        surname.set_surname("Oranje")
        self.phoenix.add_surname(surname)
        self.titanic = SurnameBase()
        self.ref_list = SurnameBase()

    def test_identical(self):
        surname = Surname()
        surname.set_surname("Oranje")
        self.ref_list.add_surname(surname)
        self.titanic.add_surname(surname)
        self.phoenix._merge_surname_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        surname = Surname()
        surname.set_surname("Biesterfelt")
        self.titanic.add_surname(surname)
        self.ref_list = SurnameBase(self.phoenix)
        self.ref_list.add_surname(surname)
        self.phoenix._merge_surname_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())


class TagBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = TagBase()
        tag_handle = "123456"
        self.phoenix.add_tag(tag_handle)
        self.titanic = TagBase()

    def test_identical(self):
        self.ref_list = TagBase(self.phoenix)
        self.titanic.add_tag(self.phoenix.get_tag_list()[0])
        self.phoenix._merge_tag_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        self.titanic.set_tag_list([])
        tag_handle = "654321"
        self.titanic.add_tag(tag_handle)
        self.ref_list = TagBase(self.phoenix)
        self.ref_list.add_tag(tag_handle)
        self.phoenix._merge_tag_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())


if __name__ == "__main__":
    unittest.main()
