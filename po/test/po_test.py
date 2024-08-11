#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
# Copyright (C) 2010 Jerome Rapinat
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

""" Unittest for testing POTFILES.in and Makefile contents """

# PYTHONPATH=/../gramps python po_test.py

import unittest
import os
import glob
from test import test_util

test_util.path_append_parent()


def get_potfile(filename):
    with open(filename, "r") as fp:
        retvals = []
        for line in fp:
            if line and line[0] != "#":
                retvals.append(line.strip())
    return retvals


# POTFILES.skip

excluded_files = get_potfile("../POTFILES.skip")


class TestPOT(unittest.TestCase):
    potfiles = get_potfile("../POTFILES.in")
    count = 1

    def __init__(self, method_name, dir, file, searches):
        method_name = method_name % self.count
        TestPOT.count += 1
        self.__dict__[method_name] = lambda: self.helper(dir, file, searches)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, dir, file, searches):
        realpath = dir + "/" + file
        pathfile = realpath[3:]
        if os.path.exists(realpath):
            with open(realpath, "r") as fp:
                lines = fp.read()
            found = False
            for search in searches:
                if search in lines:
                    found = True
            if found:
                self.assertFalse(
                    pathfile[3:] not in excluded_files
                    and pathfile[3:] not in self.potfiles,
                    "'%s' is not in POTFILES.in" % (pathfile[3:],),
                )
            else:
                self.assertTrue(True, "'%s' doesn't contain '%s'" % (file, search))
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
        realpath = dir + "/" + file
        pathfile = realpath[3:]
        path, filename = realpath.rsplit("/", 1)
        makefile = path + "/Makefile.in"
        if pathfile[3:] in excluded_files:
            self.assertTrue(True, "exclude '%s'" % pathfile)
        elif os.path.exists(makefile):
            with open(makefile, "r") as fp:
                lines = fp.read()
            self.assertTrue(
                filename in lines, "'%s' not in %s/Makefile.in" % (filename, path)
            )
        else:
            self.assertTrue(True, "no makefile in '%s'" % dir)


class TestGetText(unittest.TestCase):
    count = 1

    def __init__(self, method_name, pofile, searches):
        method_name = method_name % self.count
        TestGetText.count += 1
        self.__dict__[method_name] = lambda: self.helper(pofile, searches)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, pofile, searches):
        if not os.path.exists("../../" + pofile):
            self.assertTrue(False, "'%s' is in POTFILES.in and does not exist" % pofile)
        with open("../../" + pofile, "r") as fp:
            lines = fp.read()
        found = False
        for search in searches:
            found = (search in lines) or found
        self.assertTrue(
            found,
            "'%s' is in POTFILES.in but does not contain '%s'" % (pofile, searches),
        )


class TestDups(unittest.TestCase):
    potfiles = get_potfile("../POTFILES.in")
    count = 1

    def __init__(self, method_name, potfile):
        method_name = method_name % self.count
        TestPOT.count += 1
        self.__dict__[method_name] = lambda: self.helper(potfile)
        unittest.TestCase.__init__(self, method_name)

    def helper(self, potfile):
        self.assertTrue(
            self.potfiles.count(potfile) == 1,
            "'%s' is in POTFILE.in more than once." % potfile,
        )


def suite1():
    """
    Suite of tests designed to see if that if one of a set of phrases
    is in a file, then that file better be in POTFILES.in.
    """
    suite = unittest.TestSuite()
    for dir, subdir, files in os.walk("../../src"):
        for file in files:
            if glob.fnmatch.fnmatch(file, "*.py"):
                suite.addTest(
                    TestPOT(
                        "test_pot_py_%04d",
                        dir,
                        file,
                        ["import gettext", "import sgettext"],
                    )
                )
            elif glob.fnmatch.fnmatch(file, "*.glade"):
                suite.addTest(
                    TestPOT("test_pot_glade_%04d", dir, file, ['translatable="yes"'])
                )
            if glob.fnmatch.fnmatch(file, "*.py"):
                suite.addTest(TestMake("test_make_py_%04d", dir, file))
            elif glob.fnmatch.fnmatch(file, "*.glade"):
                suite.addTest(TestMake("test_make_glade_%04d", dir, file))
    return suite


def suite2():
    """
    Suite of tests that check for each file in POTFILES.in, then it
    should have an import gettext or sgettext.
    """
    suite = unittest.TestSuite()
    potfiles = get_potfile("../POTFILES.in")
    for potfile in potfiles:
        # do not call gettext
        if glob.fnmatch.fnmatch(potfile, "*.gpr.py"):
            continue
        # special case
        if glob.fnmatch.fnmatch(potfile, "src/plugins/lib/libnarrate.py"):
            continue
        if glob.fnmatch.fnmatch(potfile, "*.py"):
            suite.addTest(
                TestGetText(
                    "test_gettext_py_%04d",
                    potfile,
                    ["import gettext", "from gramps.gen.ggettext", "import sgettext"],
                )
            )
        elif glob.fnmatch.fnmatch(potfile, "*.glade"):
            suite.addTest(
                TestGetText("test_gettext_glade_%04d", potfile, ['translatable="yes"'])
            )
    return suite


def suite3():
    """
    Looks for duplicates in POTFILES.in.
    """
    suite = unittest.TestSuite()
    for potfile in set(get_potfile("../POTFILES.in")):
        if potfile:
            suite.addTest(TestDups("test_dups_%04d", potfile))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite1())
    unittest.TextTestRunner().run(suite2())
    unittest.TextTestRunner().run(suite3())
