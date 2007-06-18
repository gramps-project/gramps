import unittest
import logging
import sys

sys.path.append('../../src/GrampsLogger')

logger = logging.getLogger('Gramps.Tests.GrampsLogger')

import _RotateHandler

class RotateHandlerTest(unittest.TestCase):
    """Test the RotateHandler."""

    def test_buffer_recall(self):
        """Test that simple recall of messages works."""
        
        rh = _RotateHandler.RotateHandler(10)
        l = logging.getLogger("RotateHandlerTest")
        l.setLevel(logging.DEBUG)
        
        l.addHandler(rh)

        log_message = "Debug message"
        l.info(log_message)
        assert len(rh.get_buffer()) == 1, "Message buffer wrong size, should be '1' is '%d'" % (len(rh.get_buffer()))
        assert rh.get_buffer()[0].getMessage() == log_message, \
               "Message buffer content is wrong, should be '%s' is '%s'" \
               % (log_message, rh.get_buffer()[0].getMessage())

        l.removeHandler(rh)

        
    def test_buffer_rotation(self):
        """Test that buffer correctly rolls over when capacity is reached."""

        rh = _RotateHandler.RotateHandler(10)
        l = logging.getLogger("RotateHandlerTest")
        l.setLevel(logging.DEBUG)
        
        l.addHandler(rh)

        log_messages = 20 * [None]
        for i in xrange(0,20):
            log_messages[i] = "Message %d" % (i)

        
        [l.info(log_messages[i]) for i in xrange(0,10)]

        assert len(rh.get_buffer()) == 10, "Message buffer wrong size, should be '10' is '%d'" % (len(rh.get_buffer()))

        buffer = rh.get_buffer()
        
        for i in xrange(0,10):
            assert buffer[i].getMessage() == log_messages[i], \
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'" \
                   % (log_messages[i], buffer[i].getMessage(),i)


        l.info(log_messages[10])

        buffer = rh.get_buffer()

        for i in xrange(0,10):
            assert buffer[i].getMessage() == log_messages[i+1], \
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'" \
                   % (log_messages[i+1], buffer[i].getMessage(),i)


        [l.info(log_messages[i]) for i in xrange(11,20)]
        
        buffer = rh.get_buffer()
        for i in xrange(0,10):
            assert buffer[i].getMessage() == log_messages[i+10], \
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'" \
                   % (log_messages[i+10], buffer[i].getMessage(),i)
            
        l.removeHandler(rh)


        
def testSuite():
    suite = unittest.makeSuite(RotateHandlerTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
