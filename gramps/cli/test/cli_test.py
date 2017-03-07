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

""" CLI tests for gramps """

import sys
import os
import unittest
import re
import subprocess

from gramps.gen.const import TEMP_DIR
from gramps.gen.dbstate import DbState
from gramps.test.test_util import Gramps

test_ged = """0 HEAD
1 SOUR min1r.ged min 1-rec
1 SUBM @SUBM1@
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR ASCII
0 @I1@ INDI
0 TRLR
"""

ddir = os.path.dirname(__file__)
min1r = os.path.join(ddir, "min1r.ged")
out_ged = os.path.join(ddir, "test_out.ged")
example_copy = os.path.join(ddir, "copy.gramps")
example = os.path.join(ddir, "..", "..", "..",
                       "example", "gramps", "data.gramps")

class Test(unittest.TestCase):
    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(out_ged):
            os.remove(out_ged)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(min1r):
            with open(min1r, "w") as f:
                f.write(test_ged)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(min1r):
            os.remove(min1r)

    # silly test just to illustrate unittest setUp behavior
    def test1_setup_works(self):
        self.assertTrue(os.path.exists(ddir), "data dir %r exists" % ddir)
        self.assertTrue(os.path.exists(min1r), "data file %r exists" % min1r)
        self.assertFalse(os.path.exists(out_ged),
            "NO out file %r yet" % out_ged)

    # This tests the fix for bug #1331-1334
    # read trivial gedcom input, write gedcom output
    def test2_exec_CLI(self):
        ifile = min1r
        ofile = out_ged
        gcmd = [sys.executable, "Gramps.py", "-i", ifile, "-e", ofile]
        process = subprocess.Popen(gcmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        result_str, err_str = process.communicate()
        self.assertEqual(process.returncode, 0,
                         "executed CLI command %r" % gcmd)
        # simple validation o output
        self.assertTrue(os.path.isfile(ofile), "output file created")
        with open(ofile) as f:
            content = f.read()
        g = re.search("INDI", content)
        self.assertTrue(g, "found 'INDI' in output file")

    # this verifies that files in the temporary "import dir"
    # get cleaned before (and after) running a CLI
    # (eg cleanout stale files from prior crash-runs)
    def test3_files_in_import_dir(self):
        ddir = os.path.join(TEMP_DIR, "import_dbdir")
        try:
            os.makedirs(ddir)
        except:
            pass
        bogofiles = [os.path.join(ddir, fn) for fn in ("family.db", "lock")]
        for fn in bogofiles:
            with open(fn, "w") as f:
                f.write("garbage")

        # ~same as test 2
        ifile = min1r
        ofile = out_ged
        gcmd = [sys.executable, "Gramps.py", "-i", ifile, "-e", ofile]
        process = subprocess.Popen(gcmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        result_str, err_str = process.communicate()
        self.assertEqual(process.returncode, 0,
                         "executed CLI command %r" % gcmd)

        for fn in bogofiles:
            self.assertFalse(os.path.exists(fn))

class UnicodeTest(unittest.TestCase):

    def setUp(self):
        from gramps.cli.clidbman import CLIDbManager
        from gramps.gen.config import set as setconfig, get as getconfig
        from gramps.gen.dbstate import DbState
        self.newpath = os.path.join(os.path.dirname(__file__),
                                    '\u0393\u03c1\u03b1\u03bc\u03c3\u03c0')
        self.newtitle = 'Gr\u00e4mps T\u00e9st'
        os.makedirs(self.newpath)
        self.old_path = getconfig('database.path')
        setconfig('database.path', self.newpath)
        self.cli = CLIDbManager(DbState())

    def tearDown(self):
        from gramps.gen.config import set as setconfig
        for (dirpath, dirnames, filenames) in os.walk(self.newpath, False):
            for afile in filenames:
                os.remove(os.path.join(dirpath, afile))
            for adir in dirnames:
                os.rmdir(os.path.join(dirpath, adir))
        os.rmdir(self.newpath)
        setconfig('database.path', self.old_path)

    # Test that clidbman will open files in a path containing
    # arbitrary Unicode characters.
    def test4_arbitrary_uncode_path(self):
        (dbpath, title) = self.cli.create_new_db_cli(self.newtitle)

        self.assertEqual(self.newpath, os.path.dirname(dbpath),
                          "Compare paths %s and %s" % (repr(self.newpath),
                                                       repr(dbpath)))
        self.assertEqual(self.newtitle, title, "Compare titles %s and %s" %
                          (repr(self.newtitle), repr(title)))

class CLITest(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(example_copy):
            os.remove(example_copy)
        self.call("--remove", "Test: test1_cli")

    def setUp(self):
        self.gramps = Gramps()
        self.tearDown()

    def call(self, *args, stdin=None):
        self.gramps.run(*args, stdin=stdin)

    def test1a_cli(self):
        self.call("-C", "Test: test1_cli", "--import", example)

    def test1b_cli(self):
        self.call("-O", "Test: test1_cli", "--export", example_copy)

if __name__ == "__main__":
    unittest.main()

#===eof===
