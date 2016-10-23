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
from gramps.gen.db import make_database, DbTxn
from gramps.gen.lib import (Person, Family, Event, Place, Repository, Source,
                            Citation, Media, Note, Tag)

#-------------------------------------------------------------------------
#
# DbTest class
#
#-------------------------------------------------------------------------
class DbTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = make_database("inmemorydb")
        cls.db.load(None)

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
    def __get_handles_test(self, obj_type, handles_func, number_func):
        handles = handles_func()
        self.assertEqual(len(handles), number_func())
        for handle in handles:
            self.assertIn(handle.decode('utf8'), self.handles[obj_type])

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

    ################################################################
    #
    # Test get_*_from_handle methods
    #
    ################################################################

    def __get_from_handle_test(self, obj_class, handles_func, get_func):
        for handle in handles_func():
            person = get_func(handle)
            self.assertIsInstance(person, obj_class)
            self.assertEqual(person.handle, handle.decode('utf8'))

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


if __name__ == "__main__":
    unittest.main()
