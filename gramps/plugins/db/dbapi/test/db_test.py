#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016      Nick Hall
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import unittest

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (Person, Family, Event, Place, Repository, Source,
                            Citation, Media, Note, Tag, Researcher, Surname)

#-------------------------------------------------------------------------
#
# DbRandomTest class
#
#-------------------------------------------------------------------------
class DbRandomTest(unittest.TestCase):
    '''
    Tests with random objects.
    '''

    @classmethod
    def setUpClass(cls):
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        self.handles = {'Person': [], 'Family': [], 'Event': [], 'Place': [],
                        'Repository': [], 'Source': [], 'Citation': [],
                        'Media': [], 'Note': [], 'Tag': []}
        self.gids = {'Person': [], 'Family': [], 'Event': [], 'Place': [],
                        'Repository': [], 'Source': [], 'Citation': [],
                        'Media': [], 'Note': []}
        with DbTxn('Add test objects', self.db) as trans:
            for i in range(10):
                self.__add_object(Person, self.db.add_person, trans)
                self.__add_object(Family, self.db.add_family, trans)
                self.__add_object(Event, self.db.add_event, trans)
                self.__add_object(Place, self.db.add_place, trans)
                self.__add_object(Repository, self.db.add_repository, trans)
                self.__add_object(Source, self.db.add_source, trans)
                self.__add_object(Citation, self.db.add_citation, trans)
                self.__add_object(Media, self.db.add_media, trans)
                self.__add_object(Note, self.db.add_note, trans)
                self.__add_object(Tag, self.db.add_tag, trans)

    def tearDown(self):
        with DbTxn('Remove test objects', self.db) as trans:
            for handle in self.handles['Person']:
                self.db.remove_person(handle, trans)
            for handle in self.handles['Family']:
                self.db.remove_family(handle, trans)
            for handle in self.handles['Event']:
                self.db.remove_event(handle, trans)
            for handle in self.handles['Place']:
                self.db.remove_place(handle, trans)
            for handle in self.handles['Repository']:
                self.db.remove_repository(handle, trans)
            for handle in self.handles['Source']:
                self.db.remove_source(handle, trans)
            for handle in self.handles['Citation']:
                self.db.remove_citation(handle, trans)
            for handle in self.handles['Media']:
                self.db.remove_media(handle, trans)
            for handle in self.handles['Note']:
                self.db.remove_note(handle, trans)
            for handle in self.handles['Tag']:
                self.db.remove_tag(handle, trans)

    def __add_object(self, obj_class, add_func, trans):
        obj = obj_class()
        if obj_class == Tag:
            obj.name = 'Tag%s' % len(self.handles['Tag'])
        handle = add_func(obj, trans)
        self.handles[obj_class.__name__].append(handle)
        if obj_class != Tag:
            self.gids[obj_class.__name__].append(obj.gramps_id)

    ################################################################
    #
    # Test get_number_of_* methods
    #
    ################################################################

    def test_number_of_people(self):
        self.assertEqual(self.db.get_number_of_people(),
                         len(self.handles['Person']))
    def test_number_of_families(self):
        self.assertEqual(self.db.get_number_of_families(),
                         len(self.handles['Family']))
    def test_number_of_events(self):
        self.assertEqual(self.db.get_number_of_events(),
                         len(self.handles['Event']))
    def test_number_of_places(self):
        self.assertEqual(self.db.get_number_of_places(),
                         len(self.handles['Place']))
    def test_number_of_repositories(self):
        self.assertEqual(self.db.get_number_of_repositories(),
                         len(self.handles['Repository']))
    def test_number_of_sources(self):
        self.assertEqual(self.db.get_number_of_sources(),
                         len(self.handles['Source']))
    def test_number_of_citations(self):
        self.assertEqual(self.db.get_number_of_citations(),
                         len(self.handles['Citation']))
    def test_number_of_media(self):
        self.assertEqual(self.db.get_number_of_media(),
                         len(self.handles['Media']))
    def test_number_of_notes(self):
        self.assertEqual(self.db.get_number_of_notes(),
                         len(self.handles['Note']))
    def test_number_of_tags(self):
        self.assertEqual(self.db.get_number_of_tags(),
                         len(self.handles['Tag']))

    ################################################################
    #
    # Test get_*_handles methods
    #
    ################################################################
    def __get_handles_test(self, obj_type, handles_func, number_func,
                           sort_handles=False):
        if sort_handles:
            handles = handles_func(sort_handles=True)
        else:
            handles = handles_func()
        self.assertEqual(len(handles), number_func())
        for handle in handles:
            self.assertIn(handle, self.handles[obj_type])

    def test_get_person_handles(self):
        self.__get_handles_test('Person',
                                self.db.get_person_handles,
                                self.db.get_number_of_people)

    def test_get_family_handles(self):
        self.__get_handles_test('Family',
                                self.db.get_family_handles,
                                self.db.get_number_of_families)

    def test_get_event_handles(self):
        self.__get_handles_test('Event',
                                self.db.get_event_handles,
                                self.db.get_number_of_events)

    def test_get_place_handles(self):
        self.__get_handles_test('Place',
                                self.db.get_place_handles,
                                self.db.get_number_of_places)

    def test_get_repository_handles(self):
        self.__get_handles_test('Repository',
                                self.db.get_repository_handles,
                                self.db.get_number_of_repositories)

    def test_get_source_handles(self):
        self.__get_handles_test('Source',
                                self.db.get_source_handles,
                                self.db.get_number_of_sources)

    def test_get_citation_handles(self):
        self.__get_handles_test('Citation',
                                self.db.get_citation_handles,
                                self.db.get_number_of_citations)

    def test_get_media_handles(self):
        self.__get_handles_test('Media',
                                self.db.get_media_handles,
                                self.db.get_number_of_media)

    def test_get_note_handles(self):
        self.__get_handles_test('Note',
                                self.db.get_note_handles,
                                self.db.get_number_of_notes)

    def test_get_tag_handles(self):
        self.__get_handles_test('Tag',
                                self.db.get_tag_handles,
                                self.db.get_number_of_tags)

    def test_get_person_handles_sort(self):
        self.__get_handles_test('Person',
                                self.db.get_person_handles,
                                self.db.get_number_of_people,
                                sort_handles=True)

    def test_get_family_handles_sort(self):
        self.__get_handles_test('Family',
                                self.db.get_family_handles,
                                self.db.get_number_of_families,
                                sort_handles=True)

    def test_get_place_handles_sort(self):
        self.__get_handles_test('Place',
                                self.db.get_place_handles,
                                self.db.get_number_of_places,
                                sort_handles=True)

    def test_get_source_handles_sort(self):
        self.__get_handles_test('Source',
                                self.db.get_source_handles,
                                self.db.get_number_of_sources,
                                sort_handles=True)

    def test_get_citation_handles_sort(self):
        self.__get_handles_test('Citation',
                                self.db.get_citation_handles,
                                self.db.get_number_of_citations,
                                sort_handles=True)

    def test_get_media_handles_sort(self):
        self.__get_handles_test('Media',
                                self.db.get_media_handles,
                                self.db.get_number_of_media,
                                sort_handles=True)

    def test_get_tag_handles_sort(self):
        self.__get_handles_test('Tag',
                                self.db.get_tag_handles,
                                self.db.get_number_of_tags,
                                sort_handles=True)

    ################################################################
    #
    # Test get_*_gramps_ids methods
    #
    ################################################################
    def __get_gids_test(self, obj_type, gids_func, number_func):
        gids = gids_func()
        self.assertEqual(len(gids), number_func())
        for gid in gids:
            self.assertIn(gid, self.gids[obj_type])

    def test_get_person_gids(self):
        self.__get_gids_test('Person',
                             self.db.get_person_gramps_ids,
                             self.db.get_number_of_people)

    def test_get_family_gids(self):
        self.__get_gids_test('Family',
                             self.db.get_family_gramps_ids,
                             self.db.get_number_of_families)

    def test_get_event_gids(self):
        self.__get_gids_test('Event',
                             self.db.get_event_gramps_ids,
                             self.db.get_number_of_events)

    def test_get_place_gids(self):
        self.__get_gids_test('Place',
                             self.db.get_place_gramps_ids,
                             self.db.get_number_of_places)

    def test_get_repository_gids(self):
        self.__get_gids_test('Repository',
                             self.db.get_repository_gramps_ids,
                             self.db.get_number_of_repositories)

    def test_get_source_gids(self):
        self.__get_gids_test('Source',
                             self.db.get_source_gramps_ids,
                             self.db.get_number_of_sources)

    def test_get_citation_gids(self):
        self.__get_gids_test('Citation',
                             self.db.get_citation_gramps_ids,
                             self.db.get_number_of_citations)

    def test_get_media_gids(self):
        self.__get_gids_test('Media',
                             self.db.get_media_gramps_ids,
                             self.db.get_number_of_media)

    def test_get_note_gids(self):
        self.__get_gids_test('Note',
                             self.db.get_note_gramps_ids,
                             self.db.get_number_of_notes)

    ################################################################
    #
    # Test get_*_from_handle methods
    #
    ################################################################

    def __get_from_handle_test(self, obj_class, handles_func, get_func):
        for handle in handles_func():
            person = get_func(handle)
            self.assertIsInstance(person, obj_class)
            self.assertEqual(person.handle, handle)

    def test_get_person_from_handle(self):
        self.__get_from_handle_test(Person,
                                    self.db.get_person_handles,
                                    self.db.get_person_from_handle)

    def test_get_family_from_handle(self):
        self.__get_from_handle_test(Family,
                                    self.db.get_family_handles,
                                    self.db.get_family_from_handle)

    def test_get_event_from_handle(self):
        self.__get_from_handle_test(Event,
                                    self.db.get_event_handles,
                                    self.db.get_event_from_handle)

    def test_get_place_from_handle(self):
        self.__get_from_handle_test(Place,
                                    self.db.get_place_handles,
                                    self.db.get_place_from_handle)

    def test_get_repository_from_handle(self):
        self.__get_from_handle_test(Repository,
                                    self.db.get_repository_handles,
                                    self.db.get_repository_from_handle)

    def test_get_source_from_handle(self):
        self.__get_from_handle_test(Source,
                                    self.db.get_source_handles,
                                    self.db.get_source_from_handle)

    def test_get_citation_from_handle(self):
        self.__get_from_handle_test(Citation,
                                    self.db.get_citation_handles,
                                    self.db.get_citation_from_handle)

    def test_get_media_from_handle(self):
        self.__get_from_handle_test(Media,
                                    self.db.get_media_handles,
                                    self.db.get_media_from_handle)

    def test_get_note_from_handle(self):
        self.__get_from_handle_test(Note,
                                    self.db.get_note_handles,
                                    self.db.get_note_from_handle)

    def test_get_tag_from_handle(self):
        self.__get_from_handle_test(Tag,
                                    self.db.get_tag_handles,
                                    self.db.get_tag_from_handle)

    ################################################################
    #
    # Test get_*_from_gramps_id methods
    #
    ################################################################

    def __get_from_gid_test(self, obj_class, gids_func, get_func):
        for gid in gids_func():
            person = get_func(gid)
            self.assertIsInstance(person, obj_class)
            self.assertEqual(person.gramps_id, gid)

    def test_get_person_from_gid(self):
        self.__get_from_gid_test(Person,
                                 self.db.get_person_gramps_ids,
                                 self.db.get_person_from_gramps_id)

    def test_get_family_from_gid(self):
        self.__get_from_gid_test(Family,
                                 self.db.get_family_gramps_ids,
                                 self.db.get_family_from_gramps_id)

    def test_get_event_from_gid(self):
        self.__get_from_gid_test(Event,
                                 self.db.get_event_gramps_ids,
                                 self.db.get_event_from_gramps_id)

    def test_get_place_from_gid(self):
        self.__get_from_gid_test(Place,
                                 self.db.get_place_gramps_ids,
                                 self.db.get_place_from_gramps_id)

    def test_get_repository_from_gid(self):
        self.__get_from_gid_test(Repository,
                                 self.db.get_repository_gramps_ids,
                                 self.db.get_repository_from_gramps_id)

    def test_get_source_from_gid(self):
        self.__get_from_gid_test(Source,
                                 self.db.get_source_gramps_ids,
                                 self.db.get_source_from_gramps_id)

    def test_get_citation_from_gid(self):
        self.__get_from_gid_test(Citation,
                                 self.db.get_citation_gramps_ids,
                                 self.db.get_citation_from_gramps_id)

    def test_get_media_from_gid(self):
        self.__get_from_gid_test(Media,
                                 self.db.get_media_gramps_ids,
                                 self.db.get_media_from_gramps_id)

    def test_get_note_from_gid(self):
        self.__get_from_gid_test(Note,
                                 self.db.get_note_gramps_ids,
                                 self.db.get_note_from_gramps_id)

    def test_get_tag_from_name(self):
        tag = self.db.get_tag_from_name('Tag0')
        self.assertEqual(tag.handle, self.handles['Tag'][0])

    ################################################################
    #
    # Test has_*_handle methods
    #
    ################################################################
    def test_has_person_handle(self):
        for handle in self.handles['Person']:
            self.assertTrue(self.db.has_person_handle(handle))

    def test_has_family_handle(self):
        for handle in self.handles['Family']:
            self.assertTrue(self.db.has_family_handle(handle))

    def test_has_event_handle(self):
        for handle in self.handles['Event']:
            self.assertTrue(self.db.has_event_handle(handle))

    def test_has_place_handle(self):
        for handle in self.handles['Place']:
            self.assertTrue(self.db.has_place_handle(handle))

    def test_has_repository_handle(self):
        for handle in self.handles['Repository']:
            self.assertTrue(self.db.has_repository_handle(handle))

    def test_has_source_handle(self):
        for handle in self.handles['Source']:
            self.assertTrue(self.db.has_source_handle(handle))

    def test_has_citation_handle(self):
        for handle in self.handles['Citation']:
            self.assertTrue(self.db.has_citation_handle(handle))

    def test_has_media_handle(self):
        for handle in self.handles['Media']:
            self.assertTrue(self.db.has_media_handle(handle))

    def test_has_note_handle(self):
        for handle in self.handles['Note']:
            self.assertTrue(self.db.has_note_handle(handle))

    def test_has_tag_handle(self):
        for handle in self.handles['Tag']:
            self.assertTrue(self.db.has_tag_handle(handle))

    ################################################################
    #
    # Test has_*_gramps_id methods
    #
    ################################################################
    def test_has_person_gramps_id(self):
        for gramps_id in self.gids['Person']:
            self.assertTrue(self.db.has_person_gramps_id(gramps_id))

    def test_has_family_gramps_id(self):
        for gramps_id in self.gids['Family']:
            self.assertTrue(self.db.has_family_gramps_id(gramps_id))

    def test_has_event_gramps_id(self):
        for gramps_id in self.gids['Event']:
            self.assertTrue(self.db.has_event_gramps_id(gramps_id))

    def test_has_place_gramps_id(self):
        for gramps_id in self.gids['Place']:
            self.assertTrue(self.db.has_place_gramps_id(gramps_id))

    def test_has_repository_gramps_id(self):
        for gramps_id in self.gids['Repository']:
            self.assertTrue(self.db.has_repository_gramps_id(gramps_id))

    def test_has_source_gramps_id(self):
        for gramps_id in self.gids['Source']:
            self.assertTrue(self.db.has_source_gramps_id(gramps_id))

    def test_has_citation_gramps_id(self):
        for gramps_id in self.gids['Citation']:
            self.assertTrue(self.db.has_citation_gramps_id(gramps_id))

    def test_has_media_gramps_id(self):
        for gramps_id in self.gids['Media']:
            self.assertTrue(self.db.has_media_gramps_id(gramps_id))

    def test_has_note_gramps_id(self):
        for gramps_id in self.gids['Note']:
            self.assertTrue(self.db.has_note_gramps_id(gramps_id))

    ################################################################
    #
    # Test get_*_cursor methods
    #
    ################################################################
    def __get_cursor_test(self, cursor_func, raw_func):
        with cursor_func() as cursor:
            for handle, data1 in cursor:
                data2 = raw_func(handle)
                self.assertEqual(data1, data2)

    def test_get_person_cursor(self):
        self.__get_cursor_test(self.db.get_person_cursor,
                               self.db.get_raw_person_data)

    def test_get_family_cursor(self):
        self.__get_cursor_test(self.db.get_family_cursor,
                               self.db.get_raw_family_data)

    def test_get_event_cursor(self):
        self.__get_cursor_test(self.db.get_event_cursor,
                               self.db.get_raw_event_data)

    def test_get_place_cursor(self):
        self.__get_cursor_test(self.db.get_place_cursor,
                               self.db.get_raw_place_data)

    def test_get_repository_cursor(self):
        self.__get_cursor_test(self.db.get_repository_cursor,
                               self.db.get_raw_repository_data)

    def test_get_source_cursor(self):
        self.__get_cursor_test(self.db.get_source_cursor,
                               self.db.get_raw_source_data)

    def test_get_citation_cursor(self):
        self.__get_cursor_test(self.db.get_citation_cursor,
                               self.db.get_raw_citation_data)

    def test_get_media_cursor(self):
        self.__get_cursor_test(self.db.get_media_cursor,
                               self.db.get_raw_media_data)

    def test_get_note_cursor(self):
        self.__get_cursor_test(self.db.get_note_cursor,
                               self.db.get_raw_note_data)

    def test_get_tag_cursor(self):
        self.__get_cursor_test(self.db.get_tag_cursor,
                               self.db.get_raw_tag_data)

    ################################################################
    #
    # Test iter_*_handles methods
    #
    ################################################################

    def __iter_handles_test(self, obj_type, iter_func):
        for handle in iter_func():
            self.assertIn(handle, self.handles[obj_type])

    def test_iter_person_handles(self):
        self.__iter_handles_test('Person',
                                self.db.iter_person_handles)

    def test_iter_family_handles(self):
        self.__iter_handles_test('Family',
                                self.db.iter_family_handles)

    def test_iter_event_handles(self):
        self.__iter_handles_test('Event',
                                self.db.iter_event_handles)

    def test_iter_place_handles(self):
        self.__iter_handles_test('Place',
                                self.db.iter_place_handles)

    def test_iter_repository_handles(self):
        self.__iter_handles_test('Repository',
                                self.db.iter_repository_handles)

    def test_iter_source_handles(self):
        self.__iter_handles_test('Source',
                                self.db.iter_source_handles)

    def test_iter_citation_handles(self):
        self.__iter_handles_test('Citation',
                                self.db.iter_citation_handles)

    def test_iter_media_handles(self):
        self.__iter_handles_test('Media',
                                self.db.iter_media_handles)

    def test_iter_note_handles(self):
        self.__iter_handles_test('Note',
                                self.db.iter_note_handles)

    def test_iter_tag_handles(self):
        self.__iter_handles_test('Tag',
                                self.db.iter_tag_handles)

    ################################################################
    #
    # Test iter_* methods
    #
    ################################################################

    def __iter_objects_test(self, obj_class, iter_func):
        for obj in iter_func():
            self.assertIsInstance(obj, obj_class)

    def test_iter_people(self):
        self.__iter_objects_test(Person,
                                 self.db.iter_people)

    def test_iter_families(self):
        self.__iter_objects_test(Family,
                                 self.db.iter_families)

    def test_iter_events(self):
        self.__iter_objects_test(Event,
                                 self.db.iter_events)

    def test_iter_places(self):
        self.__iter_objects_test(Place,
                                 self.db.iter_places)

    def test_iter_repositories(self):
        self.__iter_objects_test(Repository,
                                 self.db.iter_repositories)

    def test_iter_sources(self):
        self.__iter_objects_test(Source,
                                 self.db.iter_sources)

    def test_iter_citations(self):
        self.__iter_objects_test(Citation,
                                 self.db.iter_citations)

    def test_iter_media(self):
        self.__iter_objects_test(Media,
                                 self.db.iter_media)

    def test_iter_notes(self):
        self.__iter_objects_test(Note,
                                 self.db.iter_notes)

    def test_iter_tags(self):
        self.__iter_objects_test(Tag,
                                 self.db.iter_tags)

    ################################################################
    #
    # Test default and initial person methods
    #
    ################################################################

    def test_no_default_handle(self):
        self.db.set_default_person_handle(None)
        handle = self.db.get_default_handle()
        self.assertIsNone(handle)
        person = self.db.get_default_person()
        self.assertIsNone(person)
        person = self.db.find_initial_person()
        self.assertIsInstance(person, Person)

    def test_default_handle(self):
        default_handle = self.handles['Person'][0]
        self.db.set_default_person_handle(default_handle)
        handle = self.db.get_default_handle()
        self.assertEqual(handle, default_handle)
        person = self.db.get_default_person()
        self.assertEqual(person.handle, default_handle)
        person = self.db.find_initial_person()
        self.assertEqual(person.handle, default_handle)

    ################################################################
    #
    # Test get_total method
    #
    ################################################################
    def test_get_total(self):
        total = sum([len(self.handles[obj_type])
                     for obj_type in self.handles.keys()])
        self.assertEqual(self.db.get_total(), total)

#-------------------------------------------------------------------------
#
# DbEmptyTest class
#
#-------------------------------------------------------------------------
class DbEmptyTest(unittest.TestCase):
    '''
    Tests with an empty database.
    '''

    @classmethod
    def setUpClass(cls):
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    ################################################################
    #
    # Test metadata methods
    #
    ################################################################

    def test_metadata(self):
        self.db._set_metadata('test-key', 'test-value')
        value = self.db._get_metadata('test-key')
        self.assertEqual(value, 'test-value')

    def test_metadata_missing(self):
        value = self.db._get_metadata('missing-key')
        self.assertEqual(value, [])

    def test_metadata_default(self):
        value = self.db._get_metadata('missing-key', default='default-value')
        self.assertEqual(value, 'default-value')

    ################################################################
    #
    # Test default and initial person methods
    #
    ################################################################

    def test_no_default_handle(self):
        handle = self.db.get_default_handle()
        self.assertIsNone(handle)
        person = self.db.get_default_person()
        self.assertIsNone(person)
        person = self.db.find_initial_person()
        self.assertIsNone(person)

    ################################################################
    #
    # Test researcher methods
    #
    ################################################################

    def test_researcher(self):
        res1 = Researcher()
        res1.street = 'street'
        res1.locality = 'locality'
        res1.city = 'city'
        res1.county = 'county'
        res1.state = 'state'
        res1.country = 'country'
        res1.postal = 'postal'
        res1.phone = 'phone'
        res1.name = 'name'
        res1.addr = 'addr'
        res1.email = 'email'
        self.db.set_researcher(res1)
        res2 = self.db.get_researcher()
        self.assertEqual(res1.serialize(), res2.serialize())

    ################################################################
    #
    # Test name group mapping
    #
    ################################################################

    def test_name_group_mapping(self):
        self.db.set_name_group_mapping('Clark', 'Clarke')

        self.assertTrue(self.db.has_name_group_key('Clark'))
        self.assertFalse(self.db.has_name_group_key('Baker'))

        for key in self.db.get_name_group_keys():
            self.assertTrue(self.db.has_name_group_key(key))

        mapping = self.db.get_name_group_mapping('Clark')
        self.assertEqual(mapping, 'Clarke')

    ################################################################
    #
    # Test get_total method
    #
    ################################################################
    def test_get_total(self):
        self.assertEqual(self.db.get_total(), 0)

#-------------------------------------------------------------------------
#
# DbPersonTest class
#
#-------------------------------------------------------------------------
class DbPersonTest(unittest.TestCase):
    '''
    Tests with some sample people.
    '''

    @classmethod
    def setUpClass(cls):
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def __add_person(self, gender, first_name, surname, trans):
        person = Person()
        person.gender = gender
        name = person.primary_name
        name.first_name = first_name
        surname1 = Surname()
        surname1.surname = surname
        name.set_surname_list([surname1])
        self.all_surnames.append(surname)
        self.db.add_person(person, trans)

    def setUp(self):
        self.all_surnames = []
        with DbTxn('Add test objects', self.db) as trans:
            self.__add_person(Person.MALE, 'John', 'Allen', trans)
            self.__add_person(Person.MALE, 'John', 'Baker', trans)
            self.__add_person(Person.MALE, 'John', 'Clark', trans)
            self.__add_person(Person.FEMALE, 'John', 'Davis', trans)
            self.__add_person(Person.UNKNOWN, 'John', 'Evans', trans)
            self.__add_person(Person.FEMALE, 'Mary', 'Allen', trans)
            self.__add_person(Person.FEMALE, 'Mary', 'Baker', trans)
            self.__add_person(Person.FEMALE, 'Mary', 'Clark', trans)
            self.__add_person(Person.MALE, 'Mary', 'Davis', trans)
            self.__add_person(Person.FEMALE, 'Mary', 'Evans', trans)

    def tearDown(self):
        with DbTxn('Remove test objects', self.db) as trans:
            for handle in self.db.get_person_handles():
                self.db.remove_person(handle, trans)

    ################################################################
    #
    # Test surname list
    #
    ################################################################

    def test_surname_list(self):
        surname_list = self.db.get_surname_list()
        for surname in surname_list:
            self.assertIn(surname, self.all_surnames)

    ################################################################
    #
    # Test gender stats
    #
    ################################################################

    def test_gender_stats(self):
        stats = self.db.genderStats
        self.assertEqual(stats.name_stats('John'), (3, 1, 1))
        self.assertEqual(stats.name_stats('Mary'), (1, 4, 0))
        self.db.save_gender_stats(stats)
        saved = self.db.get_gender_stats()
        self.assertEqual(saved['John'], (3, 1, 1))
        self.assertEqual(saved['Mary'], (1, 4, 0))


if __name__ == "__main__":
    unittest.main()
