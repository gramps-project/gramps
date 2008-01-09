"""test for test/gedread_util.py

also illustrates basic use
"""

import os
import unittest as U
import logging

from test import test_util as tu
from test import gedread_util as gr


class Test(U.TestCase):
    def setUp(self):
        # make a dir to hold an input gedcom file
        self.tdir = tu.make_subdir("gr_test")

    def test1(self):
        prec="""
0 @I1@ INDI
1 NAME GedRead TEST /Person/
"""

        # create a gedcom input file
        #  from canned head/tail -- see gedread_util
        infil = os.path.join(self.tdir,"test_in.ged")
        gr.make_gedcom_input(infil, prec)
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
        logging.warn("nothing here")
        loglines = tl.logfile_getlines()
        self.assertEquals(len(loglines),1, 
            "log has no unexpected content")
        # verify one person in database 
        np = db.get_number_of_people()
        self.assertEquals(np,1, 
            tu.msg(np,1, "db has exactly one person"))

if __name__ == "__main__":
    U.main()
