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

# $Id: $

""" Unittest for testing POTFILES.in and Makefile contents """

__author__   = "Douglas S. Blank <dblank@cs.brynmawr.edu>"
__revision__ = "$Revision: $"

import unittest
import os
import glob
from test import test_util
test_util.path_append_parent() 

excluded_files = ["src/DataViews/_MapView.py", 
                  "src/plugins/PHPGedViewConnector.py",
                  "src/plugins/phpgedview.glade",
                  "src/plugins/Ancestors.py",
                  "src/plugins/DesGraph.py",
                  "src/plugins/FtmStyleAncestors.py", 
                  "src/plugins/FtmStyleDescendants.py",
                  "src/plugins/IndivSummary.py",
                  "src/date_test.py",
                  "src/plugins/CmdRef.py",
                  "src/plugins/DumpGenderStats.py",
                  "src/plugins/Eval.py",
                  "src/plugins/Leak.py",
                  "src/plugins/TestcaseGenerator.py"
                  ]

def get_potfile(filename):
    fp = open(filename, "r")
    retvals = []
    for line in fp:
        if line and line[0] != "#":
            retvals.append(line.strip())
    fp.close()
    return retvals

class TestPOT(unittest.TestCase):
    potfiles = get_potfile("../POTFILES.in")
    count = 1
    def __init__(self, method_name, dir, file, search):
        method_name = method_name % self.count
        TestPOT.count += 1
        self.__dict__[method_name] = lambda: self.helper(dir, file, search)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, dir, file, search):
        realpath = (dir + "/" + file)
        pathfile = realpath[3:]
        if os.path.exists(realpath):
            fp = open(realpath, "r")
            lines = fp.read()
            fp.close()
            if search in lines:
                self.assertFalse(pathfile[3:] not in excluded_files and
                                 pathfile[3:] not in self.potfiles, 
                                 "'%s' is not in POTFILES.in" % (pathfile[3:],))
            else:
                self.assertTrue(True, "'%s' doesn't contain '%s'" % 
                                (file, search))
        else:
            self.assertTrue(True, "'%s' doesn't exist" % file)

class TestMake(unittest.TestCase):
    count = 1
    def __init__(self, method_name, dir, file):
        method_name = method_name % self.count
        TestMake.count += 1
        self.__dict__[method_name] = lambda: self.helper(dir, file)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, dir, file):
        realpath = (dir + "/" + file)
        pathfile = realpath[3:]
        path, filename = realpath.rsplit("/", 1)
        makefile = path + "/Makefile.in"
        if pathfile[3:] in excluded_files:
            self.assertTrue(True, "exclude '%s'" % pathfile)
        elif os.path.exists(makefile):
            fp = open(makefile, "r")
            lines = fp.read()
            fp.close()
            self.assertTrue(filename in lines, "'%s' not in %s/Makefile.in" % 
                            (filename, path))
        else:
            self.assertTrue(True, "no makefile in '%s'" % dir)

def suite1():
    suite = unittest.TestSuite()            
    for dir, subdir, files in os.walk('../../src'):
        for file in files:
            if glob.fnmatch.fnmatch(file,"*.py"):
                suite.addTest(TestPOT('test_pot_py_%04d', 
                                      dir, file, "import gettext"))
            elif glob.fnmatch.fnmatch(file,"*.glade"):
                suite.addTest(TestPOT('test_pot_glade_%04d', 
                                      dir, file, "translatable=\"yes\""))
            if glob.fnmatch.fnmatch(file,"*.py"):
                suite.addTest(TestMake('test_make_py_%04d', dir, file))
            elif glob.fnmatch.fnmatch(file,"*.glade"):
                suite.addTest(TestMake('test_make_glade_%04d', dir, file))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite1())
