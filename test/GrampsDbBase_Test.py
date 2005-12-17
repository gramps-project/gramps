import unittest
import logging
import os
import tempfile
import shutil
import time

import sys
sys.path.append('../src')

import GrampsBSDDB
import RelLib

logger = logging.getLogger('Gramps.GrampsDbBase_Test')

class ReferenceMapTest (unittest.TestCase):

    def setUp(self):        
        self._tmpdir = tempfile.mkdtemp()
        self._filename = os.path.join(self._tmpdir,'test.grdb')
        
        self._db = GrampsBSDDB.GrampsBSDDB()
        self._db.load(self._filename,
                      None, # callback
                      "w")

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def _populate_database(self,
                           num_sources = 1,
                           num_persons = 0,
                           num_families = 0,
                           num_events = 0,
                           num_places = 0,
                           num_media_objects = 0,
                           num_links = 1):

        # start with sources
        sources = []
        for i in xrange(0,num_sources):
            sources.append(self._add_source())

        # now for each of the other tables. Give each entry a link
        # to num_link sources, sources are chosen on a round robin
        # basis

        for num, add_func in ((num_persons, self._add_person_with_sources),
                              (num_families, self._add_family_with_sources),
                              (num_events, self._add_event_with_sources),
                              (num_places, self._add_place_with_sources),
                              (num_media_objects, self._add_media_object_with_sources)):
                                   
            source_idx = 1
            for person_idx in xrange(0,num):

                # Get the list of sources to link
                lnk_sources = set()
                for i in xrange(0,num_links):
                    lnk_sources.add(sources[source_idx-1])
                    source_idx = (source_idx+1) % len(sources)

                add_func(lnk_sources)

        return

    def _add_source(self):
        # Add a Source
        
        tran = self._db.transaction_begin()
        source = RelLib.Source()
        self._db.add_source(source,tran)
        self._db.commit_source(source,tran)
        self._db.transaction_commit(tran, "Add Source")

        return source

                           
    def _add_object_with_source(self,sources,object_class,add_method,commit_method):

        object = object_class()

        for source in sources:
            src_ref = RelLib.SourceRef()
            src_ref.set_base_handle(source.get_handle())
            object.add_source_reference(src_ref)


        tran = self._db.transaction_begin()
        add_method(object,tran)
        commit_method(object,tran)
        self._db.transaction_commit(tran, "Add Object")

        return object

    def _add_person_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            RelLib.Person,
                                            self._db.add_person,
                                            self._db.commit_person)

    def _add_family_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            RelLib.Family,
                                            self._db.add_family,
                                            self._db.commit_family)

    def _add_event_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            RelLib.Event,
                                            self._db.add_event,
                                            self._db.commit_event)

    def _add_place_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            RelLib.Place,
                                            self._db.add_place,
                                            self._db.commit_place)

    def _add_media_object_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            RelLib.MediaObject,
                                            self._db.add_object,
                                            self._db.commit_media_object)

        

    def test_simple_lookup(self):
        """insert a record and a reference and check that
        a lookup for the reference returns the original
        record."""

        source = self._add_source()
        person = self._add_person_with_sources([source])
        
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 1
        assert references[0] == ('Person',person.get_handle())

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

        
    def _timeit(func,*args,**kwargs):
        start = time.time()
        
        func(*args,**kwargs)
            
        end = time.time()

        return end - start
    
    def test_performance(self):
        
        self._populate_database(num_sources = 100,
                                num_persons = 80,
                                num_families = 10,
                                num_events = 10,
                                num_places = 10,
                                num_media_objects = 10,
                                num_links = 10)


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
        
        logger.info("with refs %s\n", str(with_reference_map))
        logger.info("without refs %s\n", str(without_reference_map))

        assert with_reference_map < (without_reference_map / 10), "Reference_map should an order of magnitude faster."
        
def testSuite():
    return unittest.makeSuite(ReferenceMapTest,'test')

if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
