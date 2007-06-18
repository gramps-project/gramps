import unittest
import logging
import sys

log = logging.getLogger('Gramps.Tests.GrampsLogger')

sys.path.append('..')
try:
    from guitest.gtktest import GtkTestCase
    TestCaseBase = GtkTestCase
    log.info("Using guitest")
except:
    TestCaseBase = unittest.TestCase

sys.path.append('../../src')
sys.path.append('../../src/GrampsLogger')

import const
const.rootDir = "../../src"

from GrampsLogger import RotateHandler

import _ErrorReportAssistant

class ErrorReportAssistantTest(TestCaseBase):
    """Test the ErrorReportAssistant."""

    def test_buffer_recall(self):
        """Test that simple recall of messages works."""
        
        rh = RotateHandler(10)
        l = logging.getLogger("ErrorReportAssistantTest")
        l.setLevel(logging.DEBUG)
        
        l.addHandler(rh)
        l.info("info message")

        error_detail="Test error"
        as = _ErrorReportAssistant.ErrorReportAssistant(error_detail=error_detail,
                                                               rotate_handler=rh)

        assert as._error_detail == error_detail
        
        l.removeHandler(rh)
        
        
        
def testSuite():
    suite = unittest.makeSuite(ErrorReportAssistantTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
