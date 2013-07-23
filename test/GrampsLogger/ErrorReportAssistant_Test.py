import unittest
import logging
import sys
import os

log = logging.getLogger('Gramps.Tests.GrampsLogger')
import const
const.rootDir = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.append(os.path.join(const.rootDir, 'test'))
try:
    from guitest.gtktest import GtkTestCase
    TestCaseBase = GtkTestCase
    log.info("Using guitest")
except:
    TestCaseBase = unittest.TestCase

sys.path.append(const.rootDir)
sys.path.append(os.path.join(const.rootDir, 'GrampsLogger'))

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
        ass = _ErrorReportAssistant.ErrorReportAssistant(error_detail=error_detail,
                                                               rotate_handler=rh)

        assert ass._error_detail == error_detail

        l.removeHandler(rh)

def testSuite():
    suite = unittest.makeSuite(ErrorReportAssistantTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
