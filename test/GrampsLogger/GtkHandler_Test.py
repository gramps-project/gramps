import unittest
import logging
import sys
import gtk
import os

log = logging.getLogger('Gramps.Tests.GrampsLogger')
import const
const.rootDir = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.append(os.path.join(const.rootDir, 'test'))
sys.path.append(const.rootDir)

from GrampsLogger import GtkHandler, RotateHandler

class GtkHandlerTest(unittest.TestCase):
    """Test the GtkHandler."""

    def test_window(self):
        """Test that the window appears."""

        rh = RotateHandler(capacity=20)
        rh.setLevel(logging.DEBUG)
        
        gtkh = GtkHandler(rotate_handler=rh)
        gtkh.setLevel(logging.ERROR)

        l = logging.getLogger("GtkHandlerTest")        
        l.setLevel(logging.DEBUG)

        l.addHandler(rh)
        l.addHandler(gtkh)

        l.info("An info message")
        l.warn("A warn message")
        l.debug("A debug message")
        log_message = "Debug message"
        try:
            wibble
        except:
            l.error(log_message,exc_info=True)

        while gtk.events_pending():
            gtk.main_iteration()


        
def testSuite():
    suite = unittest.makeSuite(GtkHandlerTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
