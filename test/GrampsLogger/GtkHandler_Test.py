import unittest
import logging
import sys
import gtk


sys.path.append('../../src')
sys.path.append('../../src/GrampsLogger')

logger = logging.getLogger('Gramps.Tests.GrampsLogger')

import const
const.rootDir = "../../src"

import _GtkHandler


class GtkHandlerTest(unittest.TestCase):
    """Test the GtkHandler."""

    def test_window(self):
        """Test that the window appears."""
        
        rh = _GtkHandler.GtkHandler()
        l = logging.getLogger("GtkHandlerTest")
        l.setLevel(logging.ERROR)
        
        l.addHandler(rh)

        log_message = "Debug message"
        try:
            wibble
        except:
            l.error(log_message,exc_info=True)

        l.removeHandler(rh)

        gtk.main()


        
def testSuite():
    suite = unittest.makeSuite(GtkHandlerTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
