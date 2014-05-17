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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

""" CLI tests for gramps """

import os
import unittest
import re
import io
import sys

from gramps.gen.constfunc import cuni

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

# see gramps.grampsapp.py
## hack to avoid mentioning 'utf8' encoding everywhere unicode or str is is used
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')
##

ddir = os.path.dirname(__file__)
min1r = os.path.join(ddir,"min1r.ged")
out_ged = os.path.join(ddir,"test_out.ged")

class Test(unittest.TestCase):
    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(out_ged):
            os.remove(out_ged)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(min1r):
            open(min1r,"wb").write(test_ged)

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
        gcmd = "Gramps.py -i %s -e %s" % (ifile, ofile)
        rc = os.system("python %s" % gcmd)
        self.assertEquals(rc, 0, "executed CLI cmmand %r" % gcmd)
        # simple validation o output
        self.assertTrue(os.path.isfile(ofile), "output file created")
        content = open(ofile).read()
        g = re.search("INDI", content)
        self.assertTrue(g, "found 'INDI' in output file")

    # this verifies that files in the temporary "import dir" 
    # get cleaned before (and after) running a CLI
    # (eg cleanout stale files from prior crash-runs)
    def test3_files_in_import_dir(self):
        from gramps.gen.const import TEMP_DIR
        ddir = os.path.join(TEMP_DIR,"import_dbdir")
        os.makedirs(ddir)
        bogofiles = [os.path.join(ddir,fn) 
            for fn in ("family.db", "lock")]
        for fn in bogofiles:
            f = open(fn, "w").write("garbage")
        
        # ~same as test 2
        ifile = min1r
        ofile = out_ged
        gcmd = "Gramps.py -i %s -e %s" % (ifile, ofile)
        rc = os.system("python %s" % gcmd)
        self.assertEquals(rc, 0, "executed CLI cmmand %r" % gcmd)

        for fn in bogofiles:
            self.assertFalse(os.path.exists(fn))

class UnicodeTest(unittest.TestCase):

    @unittest.skipIf(sys.version_info[0] < 3 and sys.platform == 'win32',
                     "Python2 bsddb doesn't handle unicode paths")

    def setUp(self):
        from gramps.cli.clidbman import CLIDbManager
        from gramps.gen.config import set as setconfig
        from gramps.gen.dbstate import DbState
        self.newpath = os.path.join(os.path.dirname(__file__),
                                    cuni('\u0393\u03c1\u03b1\u03bc\u03c3\u03c0'))
        self.newtitle = cuni('Gr\u00e4mps T\u00e9st')
        os.makedirs(self.newpath)
        setconfig('behavior.database-path', self.newpath)
        self.cli = CLIDbManager(DbState())

    def tearDown(self):
        for (dirpath, dirnames, filenames) in os.walk(self.newpath, False):
            for afile in filenames:
                os.remove(os.path.join(dirpath, afile))
            for adir in dirnames:
                os.rmdir(os.path.join(dirpath, adir))
        os.rmdir(self.newpath)
        pass

    # Test that clidbman will open files in a path containing
    # arbitrary Unicode characters.
    def test4_arbitrary_uncode_path(self):
        (dbpath, title) = self.cli.create_new_db_cli(self.newtitle)

        self.assertEquals(self.newpath, os.path.dirname(dbpath),
                          "Compare paths %s and %s" % (repr(self.newpath),
                                                       repr(dbpath)))
        self.assertEquals(self.newtitle, title, "Compare titles %s and %s" %
                          (repr(self.newtitle), repr(title)))


if __name__ == "__main__":
    unittest.main()

#===eof===
