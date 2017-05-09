#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import unittest
import logging
import time

from .. import DbTxn
from gramps.gen.lib import Person, Event, Source, Citation
from gramps.gen.errors import HandleError

logger = logging.getLogger('Gramps.GrampsDbBase_Test')

from .grampsdbtestbase import GrampsDbBaseTest

class ReferenceMapTest(GrampsDbBaseTest):
    """Test methods on the GrampsDbBase class that are related to the reference_map
    index implementation."""

    def test_simple_lookup(self):
        """insert a record and a reference and check that
        a lookup for the reference returns the original
        record."""

        citation = self._add_source()
        person = self._add_person_with_sources([citation])

        references = list(self._db.find_backlink_handles(citation.get_handle()))

        self.assertEqual(len(references), 1)
        self.assertEqual(references[0], (Person.__name__, person.get_handle()))

    def test_backlink_for_repository(self):
        """check that the citation /source / repos backlink lookup works."""

        repos = self._add_repository()
        citation = self._add_source(repos=repos)

        references = list(self._db.find_backlink_handles(repos.get_handle()))

        self.assertEqual(len(references), 1)
        self.assertEqual(references[0][0], Source.__name__)

        references = list(self._db.find_backlink_handles(references[0][1]))

        self.assertEqual(len(references), 1)
        self.assertEqual(references[0],
                        (Citation.__name__, citation.get_handle()))

    def test_class_limited_lookup(self):
        """check that class limited lookups work."""

        citation = self._add_source()
        person = self._add_person_with_sources([citation])

        self._add_family_with_sources([citation])
        self._add_event_with_sources([citation])
        self._add_place_with_sources([citation])
        self._add_media_with_sources([citation])

        # make sure that we have the correct number of references (one for each object)
        references = list(self._db.find_backlink_handles(citation.get_handle()))

        self.assertEqual(len(references), 5,
                         "len(references) == %s " % str(len(references)))

        # should just return the person reference
        references = [ref for ref in self._db.find_backlink_handles(citation.get_handle(), (Person.__name__,))]
        self.assertEqual(len(references), 1,
                         "len(references) == %s " % str(len(references)))
        self.assertEqual(references[0][0], Person.__name__,
                         "references = %s" % repr(references))

        # should just return the person  and event reference
        references = list(self._db.find_backlink_handles(citation.get_handle(),
                            (Person.__name__, Event.__name__)))
        self.assertEqual(len(references), 2,
                         "len(references) == %s " % str(len(references)))
        self.assertEqual(references[0][0], Person.__name__,
                         "references = %s" % repr(references))
        self.assertEqual(references[1][0], Event.__name__,
                         "references = %s" % repr(references))

    def test_delete_primary(self):
        """check that deleting a primary will remove the backreferences
        from the reference_map"""

        citation = self._add_source()
        person = self._add_person_with_sources([citation])

        self.assertIsNotNone(self._db.get_person_from_handle(person.get_handle()))

        with DbTxn("Del Person", self._db) as tran:
            self._db.remove_person(person.get_handle(),tran)

        self.assertRaises(HandleError, self._db.get_person_from_handle,
                          person.get_handle())

        references = list(self._db.find_backlink_handles(citation.get_handle()))

        self.assertEqual(len(references), 0,
                         "len(references) == %s " % str(len(references)))

    def test_reindex_reference_map(self):
        """Test that the reindex function works."""

        def cb(count):
            pass

        # unhook the reference_map update function so that we
        # can insert some records without the reference_map being updated.
        update_method = self._db._update_reference_map
        self._db._update_reference_map = lambda x,y,z: 1

        # Insert a person/source pair.
        citation = self._add_source()
        person = self._add_person_with_sources([citation])

        # Check that the reference map does not contain the reference.
        references = list(self._db.find_backlink_handles(citation.get_handle()))

        self.assertEqual(len(references), 0,
                         "len(references) == %s " % str(len(references)))

        # Reinstate the reference_map method and reindex the database
        self._db._update_reference_map = update_method
        self._db.reindex_reference_map(cb)

        # Check that the reference now appears in the reference_map
        references = list(self._db.find_backlink_handles(citation.get_handle()))

        self.assertEqual(len(references), 1,
                         "len(references) == %s " % str(len(references)))

    def perf_simple_search_speed(self):
        """
        This doesn't work any more due to multiply inheritance changes.
        """

        num_sources = 100
        num_persons = 1000
        num_families = 10
        num_events = 10
        num_places = 10
        num_media = 10
        num_links = 10

        self._populate_database(num_sources,
                                num_persons,
                                num_families,
                                num_events,
                                num_places,
                                num_media,
                                num_links)


        # time searching for source backrefs with and without reference_map
        cur = self._db.get_source_cursor()
        handle,data = cur.first()
        cur.close()

        start = time.time()
        references = list(self._db.find_backlink_handles(handle))
        end = time.time()

        with_reference_map = end - start

        remember = self._db.__class__.find_backlink_handles

        self._db.__class__.find_backlink_handles = self._db.__class__.__base__.find_backlink_handles

        start = time.time()
        references = list(self._db.find_backlink_handles(handle))
        end = time.time()

        without_reference_map = end - start

        self._db.__class__.find_backlink_handles = remember

        logger.info("search test with following data: \n"
                    "num_sources = %d \n"
                    "num_persons = %d \n"
                    "num_families = %d \n"
                    "num_events = %d \n"
                    "num_places = %d \n"
                    "num_media = %d \n"
                    "num_links = %d" % (num_sources,
                                        num_persons,
                                        num_families,
                                        num_events,
                                        num_places,
                                        num_media,
                                        num_links))
        logger.info("with refs %s\n", str(with_reference_map))
        logger.info("without refs %s\n", str(without_reference_map))

        self.assertLess(with_reference_map, without_reference_map / 10,
                        "Reference_map should an order of magnitude faster.")


if __name__ == '__main__':
    unittest.main()
