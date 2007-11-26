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
    def setUp(s):
        if not os.path.exists(min1r):
            open(min1r,"wb").write(test_ged)
        if os.path.exists(out_ged):
            os.remove(out_ged)

    # silly test just to illustrate unittest setUp behavior
    def test1_setup_works(s):
        s.assertTrue(os.path.exists(ddir), "data dir %r exists" % ddir)
        s.assertTrue(os.path.exists(min1r), "data file %r exists" % min1r)
        s.assertFalse(os.path.exists(out_ged), 
            "NO out file %r yet" % out_ged)
 
    # This tests the fix for bug #1331-1334
    # read trivial gedcom input, write gedcom output
    def test2_exec_CLI(s):
        ifile = min1r
        ofile = out_ged
        gcmd = "./gramps.py -i%s -o%s" % (ifile, ofile)
        rc = os.system("cd %s &&  python %s" % (pdir, gcmd)) 
        s.assertEquals(rc,0, tu.msg(rc,0, "executed CLI cmmand %r" % gcmd))
        # simple validation o output
        s.assertTrue(os.path.isfile(ofile), "output file created")
        content = open(ofile).read()
        g = re.search("INDI", content)
        s.assertTrue(g, "found 'INDI' in output file")

    # this verifies that files in the temporary "import dir" 
    # get cleaned before (and after) running a CLI
    # (eg cleanout stale files from prior crash-runs)
    def test3_files_in_import_dir(s):
        import const
        ddir = os.path.join(const.TEMP_DIR,"import_dbdir")
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
        s.assertEquals(rc,0, tu.msg(rc,0, "executed CLI cmmand %r" % gcmd))

        for fn in bogofiles:
            s.assertFalse(os.path.exists(fn))


if __name__ == "__main__":
    unittest.main()

#===eof===
