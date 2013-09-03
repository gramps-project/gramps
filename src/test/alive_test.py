#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

""" Unittest for Utils.probably_alive ... """

import sys
import unittest
try:
    if sys.version_info < (3,3):
        from mock import Mock, patch
    else:
        from unittest.mock import Mock, patch
        MOCKING = True
except:
    MOCKING = False
    print ("Mocking disabled", sys.exc_info()[0:2])

from test import test_util
test_util.path_append_parent() 
import Utils
from gen.lib import Person, Name, Date, Event, EventRef

class Test_probably_alive(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
    def tearDown(self):
        self.db.assert_has_calls([])

    def testAliveWithoutEvidence(self):
        person = Mock()
        with patch('Utils.probably_alive_range',
                                  # birth, death, explain, relative 
                Mock(return_value=(None, None, None, None)),
                ) as MockPAR:
            result = Utils.probably_alive(person, self.db)
        self.assertFalse(isinstance(result, tuple))
        self.assertTrue(result)
        MockPAR.assert_called_once()

    def testAliveWithoutEvidenceRange(self):
        person = Mock()
        with patch('Utils.probably_alive_range',
                                  # birth, death, explain, relative 
                Mock(return_value=(None, None, None, None)),
                ) as MockPAR:
            result = Utils.probably_alive(person, self.db, return_range=True)
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(len(result), 5)
        self.assertTrue(result[0])
        MockPAR.assert_called_once()

if __name__ == "__main__":
    unittest.main()
