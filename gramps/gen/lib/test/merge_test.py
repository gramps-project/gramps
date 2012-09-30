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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

""" Unittest that tests the code involved in merging """

import unittest
import sys
import os
sys.path.append(os.curdir)

import gen.lib
from gen.lib.const import IDENTICAL, EQUAL, DIFFERENT

class PrivacyBaseTest:
    def test_privacy_merge(self):
        self.assertEqual(self.phoenix.serialize(), self.titanic.serialize())
        self.titanic.set_privacy(True)
        self.ref_obj.set_privacy(True)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class NoteBaseTest:
    def test_note_merge(self):
        note_handle = '123456'
        self.titanic.add_note(note_handle)
        self.ref_obj.add_note(note_handle)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class CitationBaseTest:
    def test_citation_merge(self):
        citation = gen.lib.Citation()
        citation.set_reference_handle('123456')
        citation.set_page('p.10')
        self.titanic.add_citation(citation.handle)
        self.ref_obj.add_citation(citation.handle)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class MediaBaseTest:
    def test_media_merge(self):
        mediaref = gen.lib.MediaRef()
        mediaref.set_reference_handle('123456')
        self.titanic.add_media_reference(mediaref)
        self.ref_obj.add_media_reference(mediaref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class AttrBaseTest:
    def test_attribute_merge(self):
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(10)
        self.titanic.add_attribute(attr)
        self.ref_obj.add_attribute(attr)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class UrlBaseTest:
    def test_url_merge(self):
        url = gen.lib.Url()
        url.set_path('http://example.com')
        self.titanic.add_url(url)
        self.ref_obj.add_url(url)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())
#===========================================================

class PrivacyCheck(unittest.TestCase):
    def test_privacy(self):
        known_values = ( (False, False, False),
                         (True, False, True),
                         (False, True, True),
                         (True, True, True) )
        phoenix = gen.lib.privacybase.PrivacyBase()
        titanic = gen.lib.privacybase.PrivacyBase()
        for value1, value2, value_merge in known_values:
            phoenix.set_privacy(value1)
            titanic.set_privacy(value2)
            phoenix._merge_privacy(titanic)
            self.assertEqual(phoenix.get_privacy(), value_merge)

class UrlCheck(unittest.TestCase, PrivacyBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Url()
        self.phoenix.set_path('http://example1.com')
        self.phoenix.set_description('hello world')
        self.phoenix.set_type(gen.lib.UrlType.WEB_HOME)
        self.titanic = gen.lib.Url(self.phoenix)
        self.ref_obj = gen.lib.Url(self.phoenix)

    def test_path_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_path('http://example2.com')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_type_equivalence(self):
        self.titanic.set_type(gen.lib.UrlType.UNKNOWN)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_desc_equivalence(self):
        self.titanic.set_description('goodby')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

    def test_merge_path(self):
        self.titanic.set_path('example2.com')
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.is_equal(self.ref_obj), True)

class UrlBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.urlbase.UrlBase()
        self.titanic = gen.lib.urlbase.UrlBase()
        url = gen.lib.Url()
        url.set_path('example.com')
        self.phoenix.add_url(url)

    def test_identical(self):
        ref_url_list = gen.lib.urlbase.UrlBase(self.phoenix)
        url = gen.lib.Url()
        url.set_path('example.com')
        self.titanic.add_url(url)
        self.phoenix._merge_url_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_url_list.serialize())

    def test_equal(self):
        ref_url_list = gen.lib.urlbase.UrlBase(self.phoenix)
        ref_url = ref_url_list.get_url_list()[0]
        ref_url.set_privacy(True)
        url = gen.lib.Url()
        url.set_path('example.com')
        url.set_privacy(True)
        self.titanic.add_url(url)
        self.phoenix._merge_url_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_url_list.serialize())

    def test_different(self):
        ref_url_list = gen.lib.urlbase.UrlBase(self.phoenix)
        url = gen.lib.Url()
        url.set_path('other.com')
        ref_url_list.add_url(url)
        self.titanic.add_url(url)
        self.phoenix._merge_url_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_url_list.serialize())

class AddressCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Address()
        self.phoenix.set_city('Amsterdam')
        self.titanic = gen.lib.Address(self.phoenix)
        self.ref_obj = gen.lib.Address(self.phoenix)

    def test_location_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_city('Rotterdam')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_date_equivalence(self):
        date = gen.lib.Date()
        date.set_yr_mon_day(1999,12,5)
        self.titanic.set_date_object(date)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

    def test_location_merge(self):
        self.titanic.set_city('Rotterdam')
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.is_equal(self.ref_obj), True)

class AddressBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.addressbase.AddressBase()
        self.titanic = gen.lib.addressbase.AddressBase()
        self.ref_list = gen.lib.addressbase.AddressBase()
        address = gen.lib.Address()
        address.set_city('Amsterdam')
        self.phoenix.add_address(address)

    def test_identical(self):
        address = gen.lib.Address()
        address.set_city('Amsterdam')
        self.ref_list.add_address(address)
        self.titanic.add_address(address)
        self.phoenix._merge_address_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_equal(self):
        note_handle = '123456'
        address = gen.lib.Address()
        address.set_city('Amsterdam')
        address.add_note(note_handle)
        self.titanic.add_address(address)
        self.ref_list.add_address(address)
        self.phoenix._merge_address_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        address = gen.lib.Address()
        address.set_country('Netherlands')
        self.titanic.add_address(address)
        self.ref_list = gen.lib.addressbase.AddressBase(self.phoenix)
        self.ref_list.add_address(address)
        self.phoenix._merge_address_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

class AttributeCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Attribute()
        self.phoenix.set_type(gen.lib.AttributeType.AGE)
        self.phoenix.set_value(10)
        self.titanic = gen.lib.Attribute(self.phoenix)
        self.ref_obj = gen.lib.Attribute(self.phoenix)

    def test_type_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_type(gen.lib.AttributeType.MOTHER_AGE)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_value_equivalence(self):
        self.titanic.set_value(12)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

    def test_value_merge(self):
        self.titanic.set_value(12)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.is_equal(self.ref_obj), True)

class AttributeBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.attrbase.AttributeBase()
        self.titanic = gen.lib.attrbase.AttributeBase()
        self.ref_list = gen.lib.attrbase.AttributeBase()
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(10)
        self.phoenix.add_attribute(attr)

    def test_identical(self):
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(10)
        self.ref_list.add_attribute(attr)
        self.titanic.add_attribute(attr)
        self.phoenix._merge_attribute_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_equal(self):
        note_handle = '123456'
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(10)
        attr.add_note(note_handle)
        self.titanic.add_attribute(attr)
        self.ref_list.add_attribute(attr)
        self.phoenix._merge_attribute_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(12)
        self.titanic.add_attribute(attr)
        self.ref_list = gen.lib.attrbase.AttributeBase(self.phoenix)
        self.ref_list.add_attribute(attr)
        self.phoenix._merge_attribute_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

class ChildRefCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.ChildRef()
        self.phoenix.set_reference_handle('123456')
        self.phoenix.set_father_relation(gen.lib.ChildRefType.UNKNOWN)
        self.phoenix.set_mother_relation(gen.lib.ChildRefType.UNKNOWN)
        self.titanic = gen.lib.ChildRef()
        self.titanic.set_reference_handle('123456')
        self.titanic.set_father_relation(gen.lib.ChildRefType.UNKNOWN)
        self.titanic.set_mother_relation(gen.lib.ChildRefType.UNKNOWN)
        self.ref_obj = gen.lib.ChildRef()
        self.ref_obj.set_reference_handle('123456')
        self.ref_obj.set_father_relation(gen.lib.ChildRefType.UNKNOWN)
        self.ref_obj.set_mother_relation(gen.lib.ChildRefType.UNKNOWN)

    def test_handle_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle('654321')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

    def test_mrel_merge(self):
        self.titanic.set_mother_relation(gen.lib.ChildRefType.BIRTH)
        self.ref_obj.set_mother_relation(gen.lib.ChildRefType.BIRTH)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.is_equal(self.ref_obj), True)

    def test_frel_merge(self):
        self.titanic.set_father_relation(gen.lib.ChildRefType.ADOPTED)
        self.ref_obj.set_father_relation(gen.lib.ChildRefType.ADOPTED)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.is_equal(self.ref_obj), True)

class EventCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest, MediaBaseTest, AttrBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Event()
        self.phoenix.set_description("hello world")
        self.titanic = gen.lib.Event(self.phoenix)
        self.ref_obj = gen.lib.Event(self.phoenix)

class EventRefCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        AttrBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.EventRef()
        self.phoenix.set_reference_handle('123456')
        self.titanic = gen.lib.EventRef(self.phoenix)
        self.ref_obj = gen.lib.EventRef(self.phoenix)

    def test_handle_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle('654321')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_role_equivalence(self):
        self.titanic.set_role(gen.lib.EventRoleType.WITNESS)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

    def test_replace(self):
        attr1 = gen.lib.Attribute()
        attr1.set_type(gen.lib.AttributeType.AGE)
        attr1.set_value(10)
        citation1 = gen.lib.Citation()
        citation1.set_reference_handle('123456')
        citation1.set_page('p.10')
        citation2 = gen.lib.Citation()
        citation2.set_reference_handle('234567')
        citation2.set_page('p.20')
        attr1.add_citation(citation1.handle)
        attr1.add_citation(citation2.handle)
        attr2 = gen.lib.Attribute()
        attr2.set_type(gen.lib.AttributeType.AGE)
        attr2.set_value(10)
        citation3 = gen.lib.Citation()
        citation3.set_reference_handle('123456')
        citation3.set_page('p.10')
        citation4 = gen.lib.Citation()
        citation4.set_reference_handle('654321')
        citation4.set_page('p.20')
        attr2.add_citation(citation3.handle)
        attr2.add_citation(citation4.handle)
        self.phoenix.add_attribute(attr1)
        self.ref_obj.add_attribute(attr2)
        self.phoenix.replace_citation_references('234567','654321')
        self.assert_(self.phoenix.is_equal(self.ref_obj))

class FamilyCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest, MediaBaseTest, AttrBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Family()
        self.phoenix.set_father_handle('123456')
        self.phoenix.set_mother_handle('654321')
        self.phoenix.set_relationship(gen.lib.FamilyRelType.MARRIED)
        self.titanic = gen.lib.Family()
        self.titanic.set_father_handle('123456')
        self.titanic.set_mother_handle('654321')
        self.titanic.set_relationship(gen.lib.FamilyRelType.MARRIED)
        self.ref_obj = gen.lib.Family()
        self.ref_obj.set_father_handle('123456')
        self.ref_obj.set_mother_handle('654321')
        self.ref_obj.set_relationship(gen.lib.FamilyRelType.MARRIED)

    def test_relation_merge(self):
        self.phoenix.set_relationship(gen.lib.FamilyRelType.UNKNOWN)
        self.titanic.set_relationship(gen.lib.FamilyRelType.UNMARRIED)
        self.ref_obj.set_relationship(gen.lib.FamilyRelType.UNMARRIED)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventref_merge(self):
        evtref = gen.lib.EventRef()
        evtref.set_role(gen.lib.EventRoleType.WITNESS)
        self.titanic.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_ldsord_merge(self):
        ldsord = gen.lib.LdsOrd()
        ldsord.set_temple('London')
        self.titanic.add_lds_ord(ldsord)
        self.ref_obj.add_lds_ord(ldsord)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_childref_merge(self):
        childref = gen.lib.ChildRef()
        childref.set_reference_handle('123456')
        self.titanic.add_child_ref(childref)
        self.ref_obj.add_child_ref(childref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergechildref_identical(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('123456')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('123456')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('123456')
        self.phoenix.add_child_ref(childref1)
        self.titanic.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.phoenix._merge_child_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergechildref_equal(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('123456')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('123456')
        childref2.add_note('N1')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('123456')
        childref3.add_note('N1')
        self.phoenix.add_child_ref(childref1)
        self.titanic.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.phoenix._merge_child_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergechildref_different(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('123456')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('654321')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('123456')
        childref4 = gen.lib.ChildRef()
        childref4.set_reference_handle('654321')
        self.phoenix.add_child_ref(childref1)
        self.titanic.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.ref_obj.add_child_ref(childref4)
        self.phoenix._merge_child_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_childref_absent(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('234567')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('345678')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('765432')
        childref4 = gen.lib.ChildRef()
        childref4.set_reference_handle('345678')
        self.phoenix.add_child_ref(childref1)
        self.phoenix.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.ref_obj.add_child_ref(childref4)
        self.phoenix.replace_handle_reference('Person', '234567', '765432')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_childref_identical(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('234567')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('765432')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('765432')
        self.phoenix.add_child_ref(childref1)
        self.phoenix.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.phoenix.replace_handle_reference('Person', '234567', '765432')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_childref_equal(self):
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('234567')
        childref1.set_privacy(True)
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('765432')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('765432')
        childref3.set_privacy(True)
        self.phoenix.add_child_ref(childref1)
        self.phoenix.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.phoenix.replace_handle_reference('Person', '234567', '765432')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_childref_different(self):
        # impossible, is_equivalent is only DIFFERENT if handles differ.
        childref1 = gen.lib.ChildRef()
        childref1.set_reference_handle('234567')
        childref1.set_mother_relation('Adopted')
        childref2 = gen.lib.ChildRef()
        childref2.set_reference_handle('765432')
        childref3 = gen.lib.ChildRef()
        childref3.set_reference_handle('765432')
        self.phoenix.add_child_ref(childref1)
        self.phoenix.add_child_ref(childref2)
        self.ref_obj.add_child_ref(childref3)
        self.phoenix.replace_handle_reference('Person', '234567', '765432')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergeeventref_identical(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_role(gen.lib.EventRoleType.WITNESS)
        eventref2 = gen.lib.EventRef()
        eventref2.set_role(gen.lib.EventRoleType.WITNESS)
        eventref3 = gen.lib.EventRef()
        eventref3.set_role(gen.lib.EventRoleType.WITNESS)
        self.phoenix.add_event_ref(eventref1)
        self.titanic.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergeeventref_equal(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_role(gen.lib.EventRoleType.WITNESS)
        eventref2 = gen.lib.EventRef()
        eventref2.set_role(gen.lib.EventRoleType.WITNESS)
        eventref2.add_note('N1')
        eventref3 = gen.lib.EventRef()
        eventref3.set_role(gen.lib.EventRoleType.WITNESS)
        eventref3.add_note('N1')
        self.phoenix.add_event_ref(eventref1)
        self.titanic.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_mergeeventref_different(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_role(gen.lib.EventRoleType.WITNESS)
        eventref2 = gen.lib.EventRef()
        eventref2.set_role(gen.lib.EventRoleType.CLERGY)
        eventref3 = gen.lib.EventRef()
        eventref3.set_role(gen.lib.EventRoleType.WITNESS)
        eventref4 = gen.lib.EventRef()
        eventref4.set_role(gen.lib.EventRoleType.CLERGY)
        self.phoenix.add_event_ref(eventref1)
        self.titanic.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.ref_obj.add_event_ref(eventref4)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_absent(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('234567')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        eventref4 = gen.lib.EventRef()
        eventref4.set_reference_handle('234567')
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.ref_obj.add_event_ref(eventref4)
        self.phoenix.replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_identical(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('654321')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.phoenix.replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_equal(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref1.set_privacy(True)
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('654321')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        eventref3.set_privacy(True)
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.phoenix.replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_different(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref1.set_role(gen.lib.EventRoleType.WITNESS)
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('654321')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        eventref3.set_role(gen.lib.EventRoleType.WITNESS)
        eventref4 = gen.lib.EventRef()
        eventref4.set_reference_handle('654321')
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.ref_obj.add_event_ref(eventref3)
        self.ref_obj.add_event_ref(eventref4)
        self.phoenix.replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_order_first(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('234567')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        eventref4 = gen.lib.EventRef()
        eventref4.set_reference_handle('123456')
        eventref5 = gen.lib.EventRef()
        eventref5.set_reference_handle('234567')
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.phoenix.add_event_ref(eventref3)
        self.ref_obj.add_event_ref(eventref4)
        self.ref_obj.add_event_ref(eventref5)
        self.phoenix.replace_handle_reference('Event', '654321', '123456')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_event_order_last(self):
        eventref1 = gen.lib.EventRef()
        eventref1.set_reference_handle('123456')
        eventref2 = gen.lib.EventRef()
        eventref2.set_reference_handle('234567')
        eventref3 = gen.lib.EventRef()
        eventref3.set_reference_handle('654321')
        eventref4 = gen.lib.EventRef()
        eventref4.set_reference_handle('234567')
        eventref5 = gen.lib.EventRef()
        eventref5.set_reference_handle('654321')
        self.phoenix.add_event_ref(eventref1)
        self.phoenix.add_event_ref(eventref2)
        self.phoenix.add_event_ref(eventref3)
        self.ref_obj.add_event_ref(eventref4)
        self.ref_obj.add_event_ref(eventref5)
        self.phoenix.replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


class LdsordCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.LdsOrd()
        self.phoenix.set_temple('London, England')
        self.titanic = gen.lib.LdsOrd(self.phoenix)
        self.ref_obj = gen.lib.LdsOrd(self.phoenix)

    def test_type_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_type(gen.lib.LdsOrd.CONFIRMATION)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_date_equivalence(self):
        date = gen.lib.Date()
        date.set_yr_mon_day(1999,12,5)
        self.titanic.set_date_object(date)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_temple_equivalence(self):
        self.titanic.set_temple('Baton Rouge, Louisiana')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_status_equivalence(self):
        self.titanic.set_status(gen.lib.LdsOrd.STATUS_CLEARED)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_famc_equivalence(self):
        self.titanic.set_family_handle('F1')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

class LdsordBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.ldsordbase.LdsOrdBase()
        self.titanic = gen.lib.ldsordbase.LdsOrdBase()
        self.ref_list = gen.lib.ldsordbase.LdsOrdBase()
        ldsord = gen.lib.LdsOrd()
        ldsord.set_temple('London, England')
        self.phoenix.add_lds_ord(ldsord)

    def test_identical(self):
        ldsord = gen.lib.LdsOrd()
        ldsord.set_temple('London, England')
        self.titanic.add_lds_ord(ldsord)
        self.ref_list.add_lds_ord(ldsord)
        self.phoenix._merge_lds_ord_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_equal(self):
        ldsord = gen.lib.LdsOrd()
        ldsord.set_temple('London, England')
        ldsord.set_privacy(True)
        self.titanic.add_lds_ord(ldsord)
        self.ref_list.add_lds_ord(ldsord)
        self.phoenix._merge_lds_ord_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        ldsord = gen.lib.LdsOrd()
        ldsord.set_temple('Baton Rouge, Louisiana')
        self.titanic.add_lds_ord(ldsord)
        self.ref_list = gen.lib.ldsordbase.LdsOrdBase(self.phoenix)
        self.ref_list.add_lds_ord(ldsord)
        self.phoenix._merge_lds_ord_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

class MediaBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.mediabase.MediaBase()
        self.titanic = gen.lib.mediabase.MediaBase()
        self.ref_list = gen.lib.mediabase.MediaBase()
        mediaref = gen.lib.MediaRef()
        mediaref.set_reference_handle('123456')
        mediaref.set_rectangle('10 10 90 90')
        self.phoenix.add_media_reference(mediaref)

    def test_merge_identical(self):
        mediaref = gen.lib.MediaRef()
        mediaref.set_reference_handle('123456')
        mediaref.set_rectangle('10 10 90 90')
        self.titanic.add_media_reference(mediaref)
        self.ref_list.add_media_reference(mediaref)
        self.phoenix._merge_media_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_merge_equal(self):
        mediaref = gen.lib.MediaRef()
        mediaref.set_reference_handle('123456')
        mediaref.set_rectangle('10 10 90 90')
        mediaref.set_privacy(True)
        self.titanic.add_media_reference(mediaref)
        self.ref_list.add_media_reference(mediaref)
        self.phoenix._merge_media_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_merge_different(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('123456')
        mediaref1.set_rectangle('10 10 90 90')
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('123456')
        mediaref2.set_rectangle('20 10 90 90')
        self.titanic.add_media_reference(mediaref2)
        self.ref_list.add_media_reference(mediaref1)
        self.ref_list.add_media_reference(mediaref2)
        self.phoenix._merge_media_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_absent(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('654321')
        mediaref1.set_rectangle('10 10 90 90')
        self.ref_list.add_media_reference(mediaref1)
        self.phoenix.replace_media_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_identical(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('654321')
        mediaref1.set_rectangle('10 10 90 90')
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('654321')
        mediaref2.set_rectangle('10 10 90 90')
        self.phoenix.add_media_reference(mediaref1)
        self.ref_list.add_media_reference(mediaref2)
        self.phoenix.replace_media_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_equal(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('654321')
        mediaref1.set_rectangle('10 10 90 90')
        mediaref1.set_privacy(True)
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('654321')
        mediaref2.set_rectangle('10 10 90 90')
        mediaref2.set_privacy(True)
        self.phoenix.add_media_reference(mediaref1)
        self.ref_list.add_media_reference(mediaref2)
        self.phoenix.replace_media_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_different(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('654321')
        mediaref1.set_rectangle('20 20 90 90')
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('654321')
        mediaref2.set_rectangle('10 10 90 90')
        mediaref3 = gen.lib.MediaRef()
        mediaref3.set_reference_handle('654321')
        mediaref3.set_rectangle('20 20 90 90')
        self.phoenix.add_media_reference(mediaref1)
        self.ref_list.add_media_reference(mediaref2)
        self.ref_list.add_media_reference(mediaref3)
        self.phoenix.replace_media_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_order_first(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('234567')
        mediaref1.set_rectangle('10 10 90 90')
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('654321')
        mediaref2.set_rectangle('10 10 90 90')
        mediaref3 = gen.lib.MediaRef()
        mediaref3.set_reference_handle('123456')
        mediaref3.set_rectangle('10 10 90 90')
        mediaref4 = gen.lib.MediaRef()
        mediaref4.set_reference_handle('234567')
        mediaref4.set_rectangle('10 10 90 90')
        self.phoenix.add_media_reference(mediaref1)
        self.phoenix.add_media_reference(mediaref2)
        self.ref_list.add_media_reference(mediaref3)
        self.ref_list.add_media_reference(mediaref4)
        self.phoenix.replace_media_references('654321','123456')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_replace_order_last(self):
        mediaref1 = gen.lib.MediaRef()
        mediaref1.set_reference_handle('234567')
        mediaref1.set_rectangle('10 10 90 90')
        mediaref2 = gen.lib.MediaRef()
        mediaref2.set_reference_handle('654321')
        mediaref2.set_rectangle('10 10 90 90')
        mediaref3 = gen.lib.MediaRef()
        mediaref3.set_reference_handle('234567')
        mediaref3.set_rectangle('10 10 90 90')
        mediaref4 = gen.lib.MediaRef()
        mediaref4.set_reference_handle('654321')
        mediaref4.set_rectangle('10 10 90 90')
        self.phoenix.add_media_reference(mediaref1)
        self.phoenix.add_media_reference(mediaref2)
        self.ref_list.add_media_reference(mediaref3)
        self.ref_list.add_media_reference(mediaref4)
        self.phoenix.replace_media_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

class MediaObjectCheck(unittest.TestCase, PrivacyBaseTest, AttrBaseTest,
        NoteBaseTest, CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.MediaObject()
        self.phoenix.set_path('example.png')
        self.titanic = gen.lib.MediaObject(self.phoenix)
        self.ref_obj = gen.lib.MediaObject(self.phoenix)

class MediaRefCheck(unittest.TestCase, PrivacyBaseTest, AttrBaseTest,
        CitationBaseTest, NoteBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.MediaRef()
        self.phoenix.set_rectangle("10 10 90 90")
        self.titanic = gen.lib.MediaRef(self.phoenix)
        self.ref_obj = gen.lib.MediaRef(self.phoenix)

    def test_ref_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle('123456')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_rect_equivalence(self):
        self.titanic.set_rectangle("20 20 80 80")
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

class NameCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Name()
        self.phoenix.set_first_name('Willem')
        surname = gen.lib.Surname()
        surname.set_surname("Oranje")
        self.phoenix.add_surname(surname)
        self.titanic = gen.lib.Name(self.phoenix)
        self.ref_obj = gen.lib.Name(self.phoenix)

    def test_datalist_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_first_name('Maurits')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_date_equivalence(self):
        date = gen.lib.Date()
        date.set_yr_mon_day(1999,12,5)
        self.titanic.set_date_object(date)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_surname_equivalence(self):
        surname = gen.lib.Surname()
        surname.set_surname("Nassau")
        self.titanic.add_surname(surname)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

class NoteCheck(unittest.TestCase, PrivacyBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Note("hello world")
        self.titanic = gen.lib.Note("hello world")
        self.ref_obj = gen.lib.Note("hello world")

class NoteBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.notebase.NoteBase()
        self.titanic = gen.lib.notebase.NoteBase()
        note = gen.lib.Note("hello world")
        note.set_handle('123456')
        self.phoenix.add_note(note.get_handle())

    def test_identical(self):
        ref_note_list = gen.lib.notebase.NoteBase(self.phoenix)
        self.titanic.add_note(self.phoenix.get_note_list()[0])
        self.phoenix._merge_note_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_different(self):
        ref_note_list = gen.lib.notebase.NoteBase(self.phoenix)
        note = gen.lib.Note("note other")
        self.titanic.add_note(note.get_handle())
        ref_note_list.add_note(note.get_handle())
        self.phoenix._merge_note_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_replace_nonew(self):
        note = gen.lib.Note("note other")
        note.set_handle('654321')
        ref_note_list = gen.lib.notebase.NoteBase()
        ref_note_list.add_note(note.get_handle())
        self.phoenix.replace_note_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def test_replace_newpresent(self):
        note = gen.lib.Note("note other")
        note.set_handle('654321')
        note2 = gen.lib.Note("yet another note")
        note2.set_handle('234567')
        self.phoenix.add_note(note2.get_handle())
        self.phoenix.add_note(note.get_handle())
        ref_note_list = gen.lib.notebase.NoteBase()
        ref_note_list.add_note(note2.get_handle())
        ref_note_list.add_note(note.get_handle())
        self.phoenix.replace_note_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

    def todo_test_replace_child(self):
        self.phoenix.replace_note_references('','')
        self.assertEqual(self.phoenix.serialize(), ref_note_list.serialize())

class PersonCheck(unittest.TestCase, PrivacyBaseTest, MediaBaseTest,
        AttrBaseTest, NoteBaseTest, CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Person()
        name = gen.lib.Name()
        name.set_first_name('Adam')
        self.phoenix.set_primary_name(name)
        self.titanic = gen.lib.Person()
        self.titanic.set_primary_name(name)
        self.ref_obj = gen.lib.Person()
        self.ref_obj.set_primary_name(name)

    def test_replace_eventhandle_nonew(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('654321')
        self.phoenix.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_identical(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        evtref3 = gen.lib.EventRef()
        evtref3.set_reference_handle('654321')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_equal(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        evtref3 = gen.lib.EventRef()
        evtref3.set_reference_handle('654321')
        evtref3.set_privacy(True)
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_eventhandle_different(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        evtref3 = gen.lib.EventRef()
        evtref3.set_reference_handle('654321')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_birth_lower(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('654321')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.birth_ref_index = 2
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.birth_ref_index = 1
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_birth_minusone(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('654321')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('123456')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.birth_ref_index = 1
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.birth_ref_index = -1
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_death_lower(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('654321')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.death_ref_index = 2
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.death_ref_index = 1
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_death_minusone(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('654321')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('123456')
        self.phoenix.add_event_ref(evtref)
        self.phoenix.add_event_ref(evtref2)
        self.phoenix.death_ref_index = 1
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.death_ref_index = -1
        self.phoenix._replace_handle_reference('Event', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_nonew(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        self.phoenix.add_person_ref(personref)
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('654321')
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._replace_handle_reference('Person', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_identical(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('234567')
        personref3 = gen.lib.PersonRef()
        personref3.set_reference_handle('654321')
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.phoenix.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref3)
        self.phoenix._replace_handle_reference('Person', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_equal(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        personref.set_privacy(True)
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('234567')
        personref3 = gen.lib.PersonRef()
        personref3.set_reference_handle('654321')
        personref4 = gen.lib.PersonRef()
        personref4.set_reference_handle('654321')
        personref4.set_privacy(True)
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.phoenix.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref4)
        self.phoenix._replace_handle_reference('Person', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_personhandle_different(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('234567')
        personref3 = gen.lib.PersonRef()
        personref3.set_reference_handle('654321')
        self.phoenix.add_person_ref(personref)
        self.phoenix.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref3)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._replace_handle_reference('Person', '123456', '654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_primaryname(self):
        name = gen.lib.Name()
        name.set_first_name('Abel')
        self.titanic.set_primary_name(name)
        self.ref_obj.add_alternate_name(name)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_altname(self):
        name = gen.lib.Name()
        name.set_first_name('Abel')
        self.titanic.add_alternate_name(name)
        self.ref_obj.add_alternate_name(name)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_eventref(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        self.titanic.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_ldsord(self):
        ldsord = gen.lib.LdsOrd()
        ldsord.set_type(gen.lib.LdsOrd.BAPTISM)
        self.titanic.add_lds_ord(ldsord)
        self.ref_obj.add_lds_ord(ldsord)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_address(self):
        address = gen.lib.Address()
        address.set_city('The Hague')
        self.titanic.add_address(address)
        self.ref_obj.add_address(address)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_person_personref(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        self.titanic.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def todo_test_merge_person_aschild(self):
        pass

    def todo_test_merge_person_asparent(self):
        pass

    def test_altname_identical(self):
        name = gen.lib.Name()
        name.set_first_name('Abel')
        name2 = gen.lib.Name()
        name2.set_first_name('Abel')
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_altname_equal(self):
        name = gen.lib.Name()
        name.set_first_name('Abel')
        name2 = gen.lib.Name()
        name2.set_first_name('Abel')
        name2.set_privacy(True)
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name2)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_altname_different(self):
        name = gen.lib.Name()
        name.set_first_name('Abel')
        name2 = gen.lib.Name()
        name2.set_first_name('Cain')
        self.phoenix.add_alternate_name(name)
        self.titanic.add_alternate_name(name2)
        self.ref_obj.add_alternate_name(name)
        self.ref_obj.add_alternate_name(name2)
        self.phoenix._merge_alternate_names(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_identical(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('123456')
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_equal(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('123456')
        evtref2.set_privacy(True)
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_different(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        self.phoenix.add_event_ref(evtref)
        self.titanic.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref)
        self.ref_obj.add_event_ref(evtref2)
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_birthref(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        evtref3 = gen.lib.EventRef()
        evtref3.set_reference_handle('123456')
        self.phoenix.add_event_ref(evtref2)
        self.titanic.add_event_ref(evtref)
        self.titanic.birth_ref_index = 0
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.birth_ref_index = 1
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_eventrefs_deathref(self):
        evtref = gen.lib.EventRef()
        evtref.set_reference_handle('123456')
        evtref2 = gen.lib.EventRef()
        evtref2.set_reference_handle('234567')
        evtref3 = gen.lib.EventRef()
        evtref3.set_reference_handle('123456')
        self.phoenix.add_event_ref(evtref2)
        self.titanic.add_event_ref(evtref)
        self.titanic.death_ref_index = 0
        self.ref_obj.add_event_ref(evtref2)
        self.ref_obj.add_event_ref(evtref3)
        self.ref_obj.death_ref_index = 1
        self.phoenix._merge_event_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_identical(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_equal(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('123456')
        personref2.set_privacy(True)
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_personrefs_different(self):
        personref = gen.lib.PersonRef()
        personref.set_reference_handle('123456')
        personref2 = gen.lib.PersonRef()
        personref2.set_reference_handle('234567')
        self.phoenix.add_person_ref(personref)
        self.titanic.add_person_ref(personref2)
        self.ref_obj.add_person_ref(personref)
        self.ref_obj.add_person_ref(personref2)
        self.phoenix._merge_person_ref_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class PlaceCheck(unittest.TestCase, PrivacyBaseTest, MediaBaseTest,
        UrlBaseTest, NoteBaseTest, CitationBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Place()
        self.phoenix.set_title('Place 1')
        self.titanic = gen.lib.Place(self.phoenix)
        self.ref_obj = gen.lib.Place(self.phoenix)

    def test_merge_primary_identical(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.set_main_location(loc)
        self.titanic.set_title('Place 2')
        loc2 = gen.lib.Location()
        loc2.set_city('Amsterdam')
        self.titanic.set_main_location(loc2)
        self.ref_obj.set_main_location(loc)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_primary_different(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.set_main_location(loc)
        self.titanic.set_title('Place 2')
        loc2 = gen.lib.Location()
        loc2.set_city('Rotterdam')
        self.titanic.set_main_location(loc2)
        self.ref_obj.set_main_location(loc)
        self.ref_obj.add_alternate_locations(loc2)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_primary_null(self):
        """
        Even if primary location of phoenix is null, still add titanics 
        primary to alternate locations.
        """
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.titanic.set_title('Place2')
        self.titanic.set_main_location(loc)
        self.ref_obj.add_alternate_locations(loc)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_alternate_identical(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.add_alternate_locations(loc)
        loc2 = gen.lib.Location()
        loc2.set_city('Amsterdam')
        self.titanic.add_alternate_locations(loc2)
        self.ref_obj.add_alternate_locations(loc)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_alternate_different(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.add_alternate_locations(loc)
        loc2 = gen.lib.Location()
        loc2.set_city('Rotterdam')
        self.titanic.add_alternate_locations(loc2)
        self.ref_obj.add_alternate_locations(loc)
        self.ref_obj.add_alternate_locations(loc2)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_prialt_identical(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.set_main_location(loc)
        loc2 = gen.lib.Location()
        loc2.set_city('Amsterdam')
        self.titanic.add_alternate_locations(loc2)
        self.ref_obj.set_main_location(loc)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_prialt2(self):
        loc = gen.lib.Location()
        loc.set_city('Amsterdam')
        self.phoenix.set_main_location(loc)
        loc2 = gen.lib.Location()
        loc2.set_city('Rotterdam')
        loc3 = gen.lib.Location()
        loc3.set_city('Rotterdam')
        self.phoenix.add_alternate_locations(loc2)
        self.titanic.set_main_location(loc3)
        self.ref_obj.set_main_location(loc)
        self.ref_obj.add_alternate_locations(loc2)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class RepoCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest, UrlBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Repository()
        self.phoenix.set_name('Repo 1')
        self.phoenix.set_type(gen.lib.RepositoryType.LIBRARY)
        self.titanic = gen.lib.Repository()
        self.titanic.set_name('Repo 1')
        self.titanic.set_type(gen.lib.RepositoryType.LIBRARY)
        self.ref_obj = gen.lib.Repository()
        self.ref_obj.set_name('Repo 1')
        self.ref_obj.set_type(gen.lib.RepositoryType.LIBRARY)

    def test_address(self):
        address = gen.lib.Address()
        address.set_city('Amsterdam')
        self.titanic.add_address(address)
        self.ref_obj.add_address(address)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace(self):
        address = gen.lib.Address()
        address.set_city('Utrecht')
        citation = gen.lib.Citation()
        citation.set_reference_handle('123456')
        address.add_citation(citation.handle)
        self.phoenix.add_address(address)
        address2 = gen.lib.Address()
        address2.set_city('Utrecht')
        citation2 = gen.lib.Citation()
        citation2.set_reference_handle('654321')
        address2.add_citation(citation2.handle)
        self.ref_obj.add_address(address2)
        self.phoenix.replace_citation_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class RepoRefCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.RepoRef()
        self.phoenix.set_reference_handle('123456')
        self.titanic = gen.lib.RepoRef(self.phoenix)
        self.ref_obj = gen.lib.RepoRef(self.phoenix)

    def test_handle_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_reference_handle('654321')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_callnr_equivalence(self):
        self.titanic.set_call_number('10')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_privacy_equivalence(self):
        self.titanic.set_privacy(True)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), EQUAL)

class SourceCheck(unittest.TestCase, PrivacyBaseTest, NoteBaseTest,
        MediaBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Source()
        self.phoenix.set_title("Source 1")
        self.titanic = gen.lib.Source()
        self.titanic.set_title("Source 1")
        self.ref_obj = gen.lib.Source()
        self.ref_obj.set_title("Source 1")

    def todo_test_replace(self):
        pass

    def test_merge_datamap(self):
        self.phoenix.set_data_item('A', 'a')
        self.phoenix.set_data_item('B', 'b')
        self.titanic.set_data_item('B', 'bb')
        self.titanic.set_data_item('C', 'c')
        self.ref_obj.set_data_item('A', 'a')
        self.ref_obj.set_data_item('B', 'b')
        self.ref_obj.set_data_item('C', 'c')
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        self.titanic.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef)
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef_identical(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_reporef_equal(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('123456')
        reporef2.set_privacy(True)
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())


    def test_merge_reporef_different(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('234567')
        self.phoenix.add_repo_reference(reporef)
        self.titanic.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix._merge_reporef_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_nonew(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('654321')
        self.phoenix.add_repo_reference(reporef)
        self.ref_obj.add_repo_reference(reporef2)
        self.phoenix.replace_repo_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_identical(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('234567')
        reporef3 = gen.lib.RepoRef()
        reporef3.set_reference_handle('654321')
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_equal(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('234567')
        reporef3 = gen.lib.RepoRef()
        reporef3.set_reference_handle('654321')
        reporef3.set_privacy(True)
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_replace_reporef_different(self):
        reporef = gen.lib.RepoRef()
        reporef.set_reference_handle('123456')
        reporef2 = gen.lib.RepoRef()
        reporef2.set_reference_handle('234567')
        reporef3 = gen.lib.RepoRef()
        reporef3.set_reference_handle('654321')
        reporef3.set_call_number('100')
        reporef4 = gen.lib.RepoRef()
        reporef4.set_reference_handle('654321')
        self.phoenix.add_repo_reference(reporef)
        self.phoenix.add_repo_reference(reporef2)
        self.phoenix.add_repo_reference(reporef3)
        self.ref_obj.add_repo_reference(reporef4)
        self.ref_obj.add_repo_reference(reporef2)
        self.ref_obj.add_repo_reference(reporef3)
        self.phoenix.replace_repo_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class CitationBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.citationbase.CitationBase()
        citation = gen.lib.Citation()
        citation.set_reference_handle('123456')
        self.phoenix.add_citation(citation.handle)
        self.titanic = gen.lib.citationbase.CitationBase()
        self.obj_list = gen.lib.citationbase.CitationBase()

    def test_replace_nonew(self):
        citation = gen.lib.Citation()
        citation.set_reference_handle('654321')
        self.obj_list.add_citation(citation.handle)
        self.phoenix.replace_citation_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

    def test_replace_newpresent(self):
        citation = gen.lib.Citation()
        citation.set_reference_handle('654321')
        citation.set_page('p.10')
        citation2 = gen.lib.Citation()
        citation2.set_reference_handle('234567')
        self.phoenix.add_citation(citation.handle)
        self.phoenix.add_citation(citation2.handle)
        self.obj_list.add_citation(citation2.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix.replace_citation_references('123456','654321')
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

    def todo_test_replace_child(self):
        pass

    def test_merge_identical(self):
        citation = gen.lib.Citation()
        citation.set_reference_handle('123456')
        self.titanic.add_citation(citation.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix._merge_citation_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())
            
    def test_merge_different(self):
        citation = gen.lib.Citation()
        citation.set_reference_handle('234567')
        citation2 = gen.lib.Citation()
        citation2.set_reference_handle('123456')
        self.titanic.add_citation(citation.handle)
        self.obj_list.add_citation(citation2.handle)
        self.obj_list.add_citation(citation.handle)
        self.phoenix._merge_citation_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.obj_list.serialize())

class CitationCheck(unittest.TestCase, PrivacyBaseTest, MediaBaseTest,
        NoteBaseTest):
    def setUp(self):
        self.phoenix = gen.lib.Citation()
        self.phoenix.set_reference_handle('123456')
        self.phoenix.set_page('p.10')
        self.titanic = gen.lib.Citation()
        self.titanic.set_reference_handle('123456')
        self.titanic.set_page('p.10')
        self.ref_obj = gen.lib.Citation()
        self.ref_obj.set_reference_handle('123456')
        self.ref_obj.set_page('p.10')

    def test_merge_confidence(self):
        known_values = ( (0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0), (0, 4, 0),
                         (1, 0, 0), (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 4),
                         (2, 0, 0), (2, 1, 1), (2, 2, 2), (2, 3, 3), (2, 4, 4),
                         (3, 0, 0), (3, 1, 1), (3, 2, 3), (3, 3, 3), (3, 4, 4),
                         (4, 0, 0), (4, 1, 4), (4, 2, 4), (4, 3, 4), (4, 4, 4))
        for val1, val2, val_merge in known_values:
            self.phoenix.set_confidence_level(val1)
            self.titanic.set_confidence_level(val2)
            self.ref_obj.set_confidence_level(val_merge)
            self.phoenix.merge(self.titanic)
            self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

    def test_merge_datamap(self):
        self.phoenix.set_data_item('A', 'a')
        self.phoenix.set_data_item('B', 'b')
        self.titanic.set_data_item('B', 'bb')
        self.titanic.set_data_item('C', 'c')
        self.ref_obj.set_data_item('A', 'a')
        self.ref_obj.set_data_item('B', 'b')
        self.ref_obj.set_data_item('C', 'c')
        self.phoenix.merge(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_obj.serialize())

class SurnameCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.Surname()
        self.phoenix.set_prefix('van')
        self.titanic = gen.lib.Surname(self.phoenix)

    def test_datalist_equivalence(self):
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), IDENTICAL)
        self.titanic.set_prefix('von')
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    def test_primary_equivalence(self):
        self.titanic.set_primary(False)
        self.assertEqual(self.phoenix.is_equivalent(self.titanic), DIFFERENT)

    # A Surname can never be EQUAL to another Surname.

    # There is no merge method to check.

class SurnameBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.surnamebase.SurnameBase()
        surname = gen.lib.Surname()
        surname.set_surname("Oranje")
        self.phoenix.add_surname(surname)
        self.titanic = gen.lib.surnamebase.SurnameBase()
        self.ref_list = gen.lib.surnamebase.SurnameBase()

    def test_identical(self):
        surname = gen.lib.Surname()
        surname.set_surname("Oranje")
        self.ref_list.add_surname(surname)
        self.titanic.add_surname(surname)
        self.phoenix._merge_surname_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        surname = gen.lib.Surname()
        surname.set_surname("Biesterfelt")
        self.titanic.add_surname(surname)
        self.ref_list = gen.lib.surnamebase.SurnameBase(self.phoenix)
        self.ref_list.add_surname(surname)
        self.phoenix._merge_surname_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

class TagBaseCheck(unittest.TestCase):
    def setUp(self):
        self.phoenix = gen.lib.tagbase.TagBase()
        tag_handle = '123456'
        self.phoenix.add_tag(tag_handle)
        self.titanic = gen.lib.tagbase.TagBase()

    def test_identical(self):
        self.ref_list = gen.lib.tagbase.TagBase(self.phoenix)
        self.titanic.add_tag(self.phoenix.get_tag_list()[0])
        self.phoenix._merge_tag_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())

    def test_different(self):
        self.titanic.set_tag_list([])
        tag_handle = '654321'
        self.titanic.add_tag(tag_handle)
        self.ref_list = gen.lib.tagbase.TagBase(self.phoenix)
        self.ref_list.add_tag(tag_handle)
        self.phoenix._merge_tag_list(self.titanic)
        self.assertEqual(self.phoenix.serialize(), self.ref_list.serialize())


if __name__ == "__main__":
    unittest.main()
