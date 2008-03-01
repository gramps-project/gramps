"""test for GedcomParse empty notes and skipped subordinates 

Empty notes are discarded -- with a warning
Skipped subordinate data also produce warnings
"""

import os
import unittest as U
import logging

from test import test_util as tu
from test import gedread_util as gr


class Test(U.TestCase):
    """ this test verifies fix for bug 1851 """
    def setUp(self):
        # make a dir to hold an input gedcom file
        self.tdir = tu.make_subdir("gsn_test")

    def test1(self):
        test_fragment="""
0 @I1@ INDI
1 NAME Adam /TheFirst/
1 DEAT
2 DATE EST 2 FEB 2000
2 PLAC Bdorf
2 ADDR Haus Nr. 44
2 NOTE this one should stay
2 NOTE 
3 CONT this should stay too, but
3 CONT next one SB skipped (empty)
2 NOTE
0 @N101@ NOTE a real note
0 @N102@ NOTE
1 CONT a real continuation-only note
1 CONT should skip next (N103 empty)
2 JUNK2
3 JUNK3
0 @N103@ NOTE
0 @N199@ NOTE
1 SOUR @S987@
"""
        # expect warnings for discarded empty notes above
        wNotes=3 # lines 32,39,40 [here]
        # expect warnings for skipped subordinates (blocks) above
        # remember consececutive lines skipped give 1 message
        wSubs=2  # lines (37+38), 41 

        # create a gedcom input file
        #  from canned head/tail -- see gedread_util
        infil = os.path.join(self.tdir,"test_in.ged")
        gr.make_gedcom_input(infil, test_fragment)
        self.assertTrue(os.path.isfile(infil), 
            "create input file %s" % infil)

        # create an empty database
        dbpath = os.path.join(self.tdir,"test_db")
        db = gr.create_empty_db(dbpath)
        self.assertTrue(os.path.isdir(dbpath),
            "create database (dir) %s" % dbpath)

        # create logfile to test for read log-messages
        # (note: uses recently added test_util 
        log = os.path.join(self.tdir, "test_log")
        tl = tu.TestLogger()
        tl.logfile_init(log)
        # now read the gedcom
        gr.gread(db, infil)
        loglines = tl.logfile_getlines()
        #NB incorrect SUBM handling causes one extraneous warning
        xWarns = 1
        ll = len(loglines)
        tot = xWarns+wNotes+wSubs
        self.assertEquals(ll,tot, tu.msg(ll,tot,
            "log has expected warning content"))
        # verify notes that survive
        numNotes = 4
        nn = db.get_number_of_notes()
        self.assertEquals(nn,numNotes, 
            tu.msg(nn,numNotes, "db has right number of notes"))

if __name__ == "__main__":
    U.main()
