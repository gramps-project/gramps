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

# test/gramps_cli_test.py
# $Id$

""" CLI tests for gramps """

import os
import unittest
import re

from test import test_util as tu

pdir = tu.path_append_parent()
ddir = tu.make_subdir( "cli_test_data")

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
min1r = os.path.join(ddir,"min1r.ged")
out_ged = os.path.join(ddir,"test_out.ged")


class Test(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(min1r):
            open(min1r,"wb").write(test_ged)
        if os.path.exists(out_ged):
            os.remove(out_ged)

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
        gcmd = "./gramps.py -i%s -o%s" % (ifile, ofile)
        rc = os.system("cd %s &&  python %s" % (pdir, gcmd)) 
        self.assertEquals(rc,0, tu.msg(rc,0, "executed CLI cmmand %r" % gcmd))
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
        gcmd = "./gramps.py -i%s -o%s" % (ifile, ofile)
        rc = os.system("cd %s &&  python %s" % (pdir, gcmd)) 
        self.assertEquals(rc,0, tu.msg(rc,0, "executed CLI cmmand %r" % gcmd))

        for fn in bogofiles:
            self.assertFalse(os.path.exists(fn))


if __name__ == "__main__":
    unittest.main()

#===eof===
