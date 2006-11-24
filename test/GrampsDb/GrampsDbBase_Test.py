import unittest
import logging
import os
import tempfile
import shutil
import time
import traceback
import sys

sys.path.append('../../src')

try:
    set()
except NameError:
    from sets import Set as set

import const
import RelLib

logger = logging.getLogger('Gramps.GrampsDbBase_Test')

from GrampsDbTestBase import GrampsDbBaseTest
import GrampsDb

class FactoryTest(unittest.TestCase):
    """Test the GrampsDb Factory classes."""

    def test_gramps_db_factory(self):
        """test than gramps_db_factory returns the correct classes."""
        
        cls = GrampsDb.gramps_db_factory(db_type = const.app_gramps)
        assert cls.__name__ == "GrampsBSDDB", \
               "Returned class is %s " % str(cls.__class__.__name__)

        cls = GrampsDb.gramps_db_factory(db_type = const.app_gramps_xml)
        assert cls.__name__ == "GrampsXMLDB", \
               "Returned class is %s " % str(cls.__class__.__name__)

        cls = GrampsDb.gramps_db_factory(db_type = const.app_gedcom)
        assert cls.__name__ == "GrampsGEDDB", \
               "Returned class is %s " % str(cls.__class__.__name__)

        self.assertRaises(GrampsDb.GrampsDbException, GrampsDb.gramps_db_factory, "gibberish")

    def test_gramps_db_writer_factory(self):
        """Test that gramps_db_writer_factory returns the correct method."""

        md = GrampsDb.gramps_db_writer_factory(db_type = const.app_gramps)
        assert callable(md), "Returned method is %s " % str(md)

        md = GrampsDb.gramps_db_writer_factory(db_type = const.app_gramps_xml)
        assert callable(md), "Returned method is %s " % str(md)

        md = GrampsDb.gramps_db_writer_factory(db_type = const.app_gedcom)
        assert callable(md), "Returned method is %s " % str(md)

        self.assertRaises(GrampsDb.GrampsDbException, GrampsDb.gramps_db_writer_factory, "gibberish")

    def test_gramps_db_reader_factory(self):
        """Test that gramps_db_reader_factory returns the correct method."""

        md = GrampsDb.gramps_db_reader_factory(db_type = const.app_gramps)
        assert callable(md), "Returned method is %s " % str(md)

        md = GrampsDb.gramps_db_reader_factory(db_type = const.app_gramps_xml)
        assert callable(md), "Returned method is %s " % str(md)

        md = GrampsDb.gramps_db_reader_factory(db_type = const.app_gedcom)
        assert callable(md), "Returned method is %s " % str(md)

        self.assertRaises(GrampsDb.GrampsDbException, GrampsDb.gramps_db_reader_factory, "gibberish")

        
        
class ReferenceMapTest (GrampsDbBaseTest):
    """Test methods on the GrampsDbBase class that are related to the reference_map
    index implementation."""

    def test_simple_lookup(self):
        """insert a record and a reference and check that
        a lookup for the reference returns the original
        record."""

        source = self._add_source()
        person = self._add_person_with_sources([source])
        
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 1
        assert references[0] == (RelLib.Person.__name__,person.get_handle())

    def test_backlink_for_repository(self):
        """check that the source / repos backlink lookup works."""

        repos = self._add_repository()
        source = self._add_source(repos=repos)
        
        references = [ ref for ref in self._db.find_backlink_handles(repos.get_handle()) ]

        assert len(references) == 1
        assert references[0] == (RelLib.Source.__name__,source.get_handle())

    def test_class_limited_lookup(self):
        """check that class limited lookups work."""

        source = self._add_source()
        person = self._add_person_with_sources([source])

        self._add_family_with_sources([source])
        self._add_event_with_sources([source])
        self._add_place_with_sources([source])
        self._add_media_object_with_sources([source])

        # make sure that we have the correct number of references (one for each object)
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 5, "len(references) == %s " % str(len(references))

        # should just return the person reference
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle(),(RelLib.Person.__name__,)) ]
        assert len(references) == 1, "len(references) == %s " % str(len(references))
        assert references[0][0] == RelLib.Person.__name__, "references = %s" % repr(references)

        # should just return the person  and event reference
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle(),(RelLib.Person.__name__,
                                                                                          RelLib.Event.__name__)) ]
        assert len(references) == 2, "len(references) == %s " % str(len(references))
        assert references[0][0] == RelLib.Person.__name__, "references = %s" % repr(references)
        assert references[1][0] == RelLib.Event.__name__, "references = %s" % repr(references)

        

    def test_delete_primary(self):
        """check that deleting a primary will remove the backreferences
        from the reference_map"""

        source = self._add_source()
        person = self._add_person_with_sources([source])
        
        assert self._db.get_person_from_handle(person.get_handle()) is not None
        
        tran = self._db.transaction_begin()
        self._db.remove_person(person.get_handle(),tran)
        self._db.transaction_commit(tran, "Del Person")

        assert self._db.get_person_from_handle(person.get_handle()) == None
        
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 0, "len(references) == %s " % str(len(references))


    def test_reindex_reference_map(self):
        """Test that the reindex function works."""

        # unhook the reference_map update function so that we
        # can insert some records without the reference_map being updated.
        update_method = self._db._update_reference_map
        self._db._update_reference_map = lambda x,y: 1

        # Insert a person/source pair.
        source = self._add_source()
        person = self._add_person_with_sources([source])

        # Check that the reference map does not contain the reference.
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 0, "len(references) == %s " % str(len(references))

        # Reinstate the reference_map method and reindex the database
        self._db._update_reference_map = update_method
        self._db.reindex_reference_map()

        # Check that the reference now appears in the reference_map
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 1, "len(references) == %s " % str(len(references))

        
    
    def perf_simple_search_speed(self):

        num_sources = 100
        num_persons = 1000
        num_families = 10
        num_events = 10
        num_places = 10
        num_media_objects = 10
        num_links = 10
        
        self._populate_database(num_sources,
                                num_persons,
                                num_families,
                                num_events,
                                num_places,
                                num_media_objects,
                                num_links)


        # time searching for source backrefs with and without reference_map
        cur = self._db.get_source_cursor()
        handle,data = cur.first()
        cur.close()

        start = time.time()
        references = [ ref for ref in self._db.find_backlink_handles(handle) ]
        end = time.time()

        with_reference_map = end - start

        remember = self._db.__class__.find_backlink_handles
        
        self._db.__class__.find_backlink_handles = self._db.__class__.__base__.find_backlink_handles

        start = time.time()
        references = [ ref for ref in self._db.find_backlink_handles(handle) ]
        end = time.time()

        without_reference_map = end - start
                
        self._db.__class__.find_backlink_handles = remember

        logger.info("search test with following data: \n"
                    "num_sources = %d \n"                    
                    "num_persons = %d \n"
                    "num_families = %d \n"
                    "num_events = %d \n"
                    "num_places = %d \n"
                    "num_media_objects = %d \n"
                    "num_links = %d" % (num_sources,
                                        num_persons,
                                        num_families,
                                        num_events,
                                        num_places,
                                        num_media_objects,
                                        num_links))
        logger.info("with refs %s\n", str(with_reference_map))
        logger.info("without refs %s\n", str(without_reference_map))

        assert with_reference_map < (without_reference_map / 10), "Reference_map should an order of magnitude faster."
        
def testSuite():
    suite = unittest.makeSuite(ReferenceMapTest,'test')
    suite.addTests(unittest.makeSuite(FactoryTest,'test'))
    return suite

def perfSuite():
    return unittest.makeSuite(ReferenceMapTest,'perf')

if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
