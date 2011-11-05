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

# test/test/gedread_util_test.py
# $Id$

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
        #NB incorrect SUBM handling causes one extraneous warning
        xWarns = 1
        self.assertEquals(len(loglines),1 + xWarns, 
            "log has no unexpected content")
        # verify one person in database 
        np = db.get_number_of_people()
        self.assertEquals(np,1, 
            tu.msg(np,1, "db has exactly one person"))
        db.close()
        del tl

if __name__ == "__main__":
    U.main()
