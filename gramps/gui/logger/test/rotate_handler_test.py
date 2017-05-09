#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import unittest
import logging

from .. import RotateHandler

class RotateHandlerTest(unittest.TestCase):
    """Test the RotateHandler."""

    def test_buffer_recall(self):
        """Test that simple recall of messages works."""

        rh = RotateHandler(10)
        l = logging.getLogger("RotateHandlerTest")
        l.setLevel(logging.DEBUG)
        l.propagate = False

        l.addHandler(rh)

        log_message = "Debug message"
        l.info(log_message)
        self.assertEqual(len(rh.get_buffer()), 1,
               "Message buffer wrong size, should be '1' is '%d'"
               % (len(rh.get_buffer())))
        self.assertEqual(rh.get_buffer()[0].getMessage(), log_message,
               "Message buffer content is wrong, should be '%s' is '%s'"
               % (log_message, rh.get_buffer()[0].getMessage()))

        l.removeHandler(rh)


    def test_buffer_rotation(self):
        """Test that buffer correctly rolls over when capacity is reached."""

        rh = RotateHandler(10)
        l = logging.getLogger("RotateHandlerTest")
        l.setLevel(logging.DEBUG)
        l.propagate = False

        l.addHandler(rh)

        log_messages = 20 * [None]
        for i in range(0,20):
            log_messages[i] = "Message %d" % (i)


        [l.info(log_messages[i]) for i in range(0,10)]

        self.assertEqual(len(rh.get_buffer()), 10,
               "Message buffer wrong size, should be '10' is '%d'" %
               (len(rh.get_buffer())))

        buffer = rh.get_buffer()

        for i in range(0,10):
            self.assertEqual(buffer[i].getMessage(), log_messages[i],
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'"
                   % (log_messages[i], buffer[i].getMessage(),i))


        l.info(log_messages[10])

        buffer = rh.get_buffer()

        for i in range(0,10):
            self.assertEqual(buffer[i].getMessage(), log_messages[i+1],
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'"
                   % (log_messages[i+1], buffer[i].getMessage(),i))


        [l.info(log_messages[i]) for i in range(11,20)]

        buffer = rh.get_buffer()
        for i in range(0,10):
            self.assertEqual(buffer[i].getMessage(), log_messages[i+10],
                   "Message buffer content is wrong, should be '%s' is '%s'. i = '%d'"
                   % (log_messages[i+10], buffer[i].getMessage(),i))

        l.removeHandler(rh)


if __name__ == '__main__':
    unittest.main()
