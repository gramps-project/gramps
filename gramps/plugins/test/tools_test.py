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

import os
import sys
import codecs
import unittest
import random

from gramps.test.test_util import Gramps
from gramps.gen.const import DATA_DIR
from gramps.gen.user import User
from gramps.gen.utils.id import set_det_id
from gramps.gen import const
from gramps.gen.utils.config import config

TREE_NAME = "Test_tooltest"
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
const.myrand = random.Random()


def call(*args):
    """Call Gramps to perform the action with out and err captured"""
    # if __debug__:
    # print ("call: %s", args)
    gramps = Gramps(user=User())
    out, err = gramps.run(*args)
    # print("out:", out, "err:", err)
    return out, err


def check_res(out, err, expected, do_out=True):
    """
    compare the output with the expected
    """
    # return all([(line in out) for line in expect])
    retval = True
    for line in expected:
        if line in (out if do_out else err):
            continue
        else:
            print("*** Expected: '%s', not found" % line)
            retval = False
    if not retval:
        if do_out:
            print(
                "*** The following was the actual stdout:\n%s"
                "*** The following was the stderr:\n%s"
                "*** End of stderr" % (out, err)
            )
        else:
            print(
                "*** The following was the actual stderr:\n%s"
                "*** The following was the stdout:\n%s"
                "*** End of stdout" % (err, out)
            )
    return retval


class ToolControl(unittest.TestCase):
    """
    These tests run some of the tools used to maintain Gramps db
    """

    def setUp(self):
        self.db_backend = config.get("database.backend")
        call("--config=database.backend:sqlite", "-y", "-q", "--remove", TREE_NAME)

    def tearDown(self):
        config.set("database.backend", self.db_backend)
        call("-y", "-q", "--remove", TREE_NAME)

    def test_tcg_and_check_and_repair(self):
        """
        Run a 'Test Case Generator' and 'Check & Repair Database' test.
        Note that the 'Test Case Generator" uses a lot of random numbers to
        generate its test cases.  This makes it less than ideal for a
        predictable unit test.  Still it contains good code for testing the
        'Check and Repair' tool.  So I force the random functions to be
        predictable by seeding it with a fixed number.  I also used the
        'Deterministic ID' function to make the usual db handle generation
        stop using random numbers and potentially reduce Gramps version to
        version issues.
        """
        # the TCG creates bad strings with illegal characters, so we need to
        # ignore them when we print the results
        try:
            sys.stderr = codecs.getwriter(sys.getdefaultencoding())(
                sys.stderr.buffer, "replace"
            )
            sys.stdout = codecs.getwriter(sys.getdefaultencoding())(
                sys.stdout.buffer, "replace"
            )
        except:
            pass
        tst_file = os.path.join(TEST_DIR, "data.gramps")
        set_det_id(True)
        # the following line assumes that TCG has run through init code, where
        # it puts 'myrand', a 'Random' class object, into the 'const' module so
        # we can access it here.
        const.myrand.seed(1234, version=1)
        # print(const.myrand.random())
        #         out, err = call("-s")
        #         expect = ["bsddb"]
        #         check_res(out, err, expect, do_out=True)
        out, err = call("-C", TREE_NAME, "-q", "--import", tst_file)
        expect = ["Opened successfully!", "data.gramps, format gramps.", "Cleaning up."]
        self.assertTrue(check_res(out, err, expect, do_out=False))
        self.assertEqual(out, "")
        out, err = call(
            "-O",
            TREE_NAME,
            "-y",
            "-q",
            "-a",
            "tool",
            "-p",
            "name=testcasegenerator,bugs=1,persons=1,"
            "add_linebreak=1,add_serial=1,"
            "long_names=1,lowlevel=0,person_count=50,"
            "specialchars=1",
        )
        expect = [
            "Opened successfully!",
            "Performing action: tool.",
            "Using options string: name=testcasegenerator,bugs=1",
            "Cleaning up.",
        ]
        self.assertTrue(check_res(out, err, expect, do_out=False))
        expect = ["person count 41"]
        self.assertTrue(check_res(out, err, expect, do_out=True))
        out, err = call("-O", TREE_NAME, "-y", "-a", "tool", "-p", "name=check")
        expect = [
            "7 broken child/family links were fixed",
            "4 broken spouse/family links were fixed",
            "1 corrupted family relationship fixed",
            "1 place alternate name fixed",
            "10 media objects were referenced, but not found",
            "References to 10 missing media objects were kept",
            "3 events were referenced, but not found",
            "1 invalid birth event name was fixed",
            "1 invalid death event name was fixed",
            "2 places were referenced, but not found",
            "12 citations were referenced, but not found",
            "15 sources were referenced, but not found",
            "9 Duplicated Gramps IDs fixed",
            "7 empty objects removed",
            "1 person objects",
            "1 family objects",
            "1 event objects",
            "1 source objects",
            "0 media objects",
            "0 place objects",
            "1 repository objects",
            "1 note objects",
        ]
        self.assertTrue(check_res(out, err, expect, do_out=True))
        expect = [
            "Opened successfully!",
            "Performing action: tool.",
            "Using options string: name=check",
            "Cleaning up.",
        ]
        self.assertTrue(check_res(out, err, expect, do_out=False))


if __name__ == "__main__":
    unittest.main()
