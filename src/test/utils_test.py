#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
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

""" Unittest for testing ... """

__author__   = "Douglas S. Blank <dblank@cs.brynmawr.edu>"
__revision__ = "$Revision: $"

import unittest
from test import test_util
test_util.path_append_parent() 
import Utils

class TestCase(unittest.TestCase):
    count = 1
    def __init__(self, *args):
        method_name = args[0] % self.count
        TestCase.count += 1
        self.__dict__[method_name] = lambda: self.helper(*args)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, *args):
        method_name, test_type, item1, item2 = args
        if test_type == "keyword":
            result = Utils.get_translation_from_keyword(item1)
            self.assertTrue(result == item2,
                            "get_translation_from_keyword('%s') returned '%s' rather than '%s'" % (item1, result, item2))
        elif test_type == "translation":
            result = Utils.get_keyword_from_translation(item1)
            self.assertTrue(result == item2,
                            "get_keyword_from_translation('%s') returned '%s' rather than '%s'" % (item1, result, item2))
        else:
            raise AttributeError, "test called incorrectly"

def suite1():
    """
    """
    suite = unittest.TestSuite()
    for line in Utils.KEYWORDS:
        keyword, code, standard, upper = line
        suite.addTest(TestCase('keyword-%04d', 'keyword', keyword, standard))
        suite.addTest(TestCase('translation-%04d', 'translation', standard, keyword))
        suite.addTest(TestCase('translation-%04d', 'translation', standard.lower(), keyword))
        suite.addTest(TestCase('translation-%04d', 'translation', upper, keyword.upper()))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite1())
