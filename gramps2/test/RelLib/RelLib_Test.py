import unittest
import logging
import os
import tempfile
import shutil
import time
import traceback
import sys


try:
    set()
except NameError:
    from sets import Set as set


import RelLib

logger = logging.getLogger('Gramps.RelLib_Test')

    
class PrimaryObjectTest (unittest.TestCase):
    """Test methods on the PrimaryObject class"""
    

    pass
        
        
def testSuite():
    suite = unittest.makeSuite(PrimaryObjectTest,'test')
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
