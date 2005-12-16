import unittest
import logging
import os
import tempfile
import shutil

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


    def _add_person_and_source(self):
        # Add a Source
        
        tran = self._db.transaction_begin()
        source = RelLib.Source()
        self._db.add_source(source,tran)
        self._db.commit_source(source,tran)
        self._db.transaction_commit(tran, "Add Source")

        src_ref = RelLib.SourceRef()
        src_ref.set_base_handle(source.get_handle())

        # Add Person with reference to the Source

        tran = self._db.transaction_begin()
        person = RelLib.Person()

        person.add_source_reference(src_ref)
        self._db.add_person(person,tran)
        self._db.commit_person(person,tran)
        self._db.transaction_commit(tran, "Add Person")

        return (person,source)

    def test_simple_lookup(self):
        """insert a record and a reference and check that
        a lookup for the reference returns the original
        record."""

        person,source = self._add_person_and_source()
        
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 1
        assert references[0] == ('Person',person.get_handle())

    def test_delete_primary(self):
        """check that deleting a primary will remove the backreferences
        from the reference_map"""

        person,source = self._add_person_and_source()
        
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
        person,source = self._add_person_and_source()

        # Check that the reference map does not contain the reference.
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 0, "len(references) == %s " % str(len(references))

        # Reinstate the reference_map method and reindex the database
        self._db._update_reference_map = update_method
        self._db.reindex_reference_map()

        # Check that the reference now appears in the reference_map
        references = [ ref for ref in self._db.find_backlink_handles(source.get_handle()) ]

        assert len(references) == 1, "len(references) == %s " % str(len(references))

        
                       

        
def testSuite():
    return unittest.makeSuite(ReferenceMapTest,'test')

if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
