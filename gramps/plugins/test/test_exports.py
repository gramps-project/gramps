#! /usr/bin/env python3
"""
Gramps - a GTK+/GNOME based genealogy program

Copyright (c) 2016 Gramps Development Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""

import unittest
import os
import difflib

from gramps.test.test_util import Gramps
from gramps.gen.const import TEMP_DIR, DATA_DIR
from gramps.gen.datehandler import set_format
from gramps.cli.user import User

TREE_NAME = "Test_exporttest"
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))


def call(*args):
    """ Call Gramps to perform the action with out and err captured """
    print("call:", args)
    set_format(0)   # Use ISO date for test
    gramps = Gramps(user=User(auto_accept=True, quiet=True))
    out, err = gramps.run(*args)
    print("out:", out, "err:", err)
    return out, err


def do_it(tstfile):
    """ based on tstfile, prepare an result export and compare with
    expected.
    """
    fname = os.path.splitext(os.path.basename(tstfile))[0]

    tst_file = os.path.join(TEST_DIR, fname + ".gramps")
    expect_file = os.path.join(TEST_DIR, tstfile)
    result_file = os.path.join(TEMP_DIR, tstfile)
    err = call("-C", TREE_NAME, "-q",
               "--import", tst_file,
               "--export", result_file)[1]
    if "Cleaning up." not in err:
        return "Export failed, no 'Cleaning up.'"
    msg = compare(expect_file, result_file)
    if not msg:
        # we will leave the result_file in place if there was an error.
        try:
            os.remove(result_file)
        except OSError:
            pass
        return
    else:
        return msg


def compare(expect_file, result_file):
    """ This uses the diff library to compare two files
    """
    with open(expect_file, encoding='utf-8_sig') as exp_f, \
         open(result_file, encoding='utf-8_sig') as res_f:
        diff = difflib.unified_diff(exp_f.readlines(),
                                    res_f.readlines(),
                                    n=2, lineterm='\n')
        msg = ""
        for line in diff:
            if line == "--- \n" or line == "+++ \n":
                continue
            msg += line
        return msg


class ExportControl(unittest.TestCase):
    """ These tests compare various exported files with expected files,
    based on the matching '.gramps' test file as a source.
    As more types of exports are tested, we will need to provide some
    filters for the differences; some types of exports have Gramps versions,
    export dates, file names etc. that don't count as differences.
    """
    def setUp(self):
        self.tearDown()  # removes it if it existed

#        out, err = self.call("-C", TREE_NAME,
#                            "--import", example)

    def tearDown(self):
        call("-y -q", "--remove", TREE_NAME)

    def test_csv(self):
        """ Run a csv export test """
        tst_file = 'exp_sample_csv.csv'
        msg = do_it(tst_file)
        if msg:
            self.fail(tst_file + ': ' + msg)

if __name__ == "__main__":
    unittest.main()
