import unittest
import logging
import os
import tempfile
import shutil
import time
import traceback
import sys

sys.path.append('../src')

try:
    set()
except NameError:
    from sets import Set as set


import RelLib

logger = logging.getLogger('Gramps.RelLib_Test')

from GrampsDbTestBase import GrampsDbBaseTest
    
class PrimaryObjectTest (GrampsDbBaseTest):
    """Test methods on the PrimaryObject class"""
    
    def test_get_backlink_handles(self):
        """Check that backlink lookup works."""

        source = self._add_source()
        person = self._add_person_with_sources([source])

        references = [ ref for ref in source.get_backlink_handles(self._db) ]

        assert len(references) == 1
        assert references[0] == (RelLib.Person.__name__,person.get_handle())

    def test_get_backlink_handles_with_class_list(self):
        """Check backlink lookup with class list."""
        
        source = self._add_source()
        person = self._add_person_with_sources([source])

        self._add_family_with_sources([source])
        self._add_event_with_sources([source])
        self._add_place_with_sources([source])
        self._add_media_object_with_sources([source])

        references = [ ref for ref in source.get_backlink_handles(self._db) ]

        # make sure that we have the correct number of references (one for each object)
        references = [ ref for ref in source.get_backlink_handles(self._db) ]

        assert len(references) == 5, "len(references) == %s " % str(len(references))

        # should just return the person reference
        references = [ ref for ref in source.get_backlink_handles(self._db,(RelLib.Person.__name__,)) ]
        assert len(references) == 1, "len(references) == %s " % str(len(references))
        assert references[0][0] == RelLib.Person.__name__, "references = %s" % repr(references)

        # should just return the person  and event reference
        references = [ ref for ref in  source.get_backlink_handles(self._db,(RelLib.Person.__name__,
                                                                             RelLib.Event.__name__)) ]
        assert len(references) == 2, "len(references) == %s " % str(len(references))
        assert references[0][0] == RelLib.Person.__name__, "references = %s" % repr(references)
        assert references[1][0] == RelLib.Event.__name__, "references = %s" % repr(references)

        
        
def testSuite():
    suite = unittest.makeSuite(PrimaryObjectTest,'test')
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
