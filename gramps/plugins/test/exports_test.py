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
from gramps.gen.user import User
from gramps.gen.utils.config import config

TREE_NAME = "Test_exporttest"
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))


def call(*args):
    """ Call Gramps to perform the action with out and err captured """
    #print("call:", args)
    gramps = Gramps(user=User())
    out, err = gramps.run(*args)
    #print("out:", out, "err:", err)
    return out, err


def do_it(srcfile, tstfile, dfilter=None):
    """ based on tstfile, prepare an result export and compare with
    expected.
    """
    tst_file = os.path.join(TEST_DIR, srcfile)
    expect_file = os.path.join(TEST_DIR, tstfile)
    result_file = os.path.join(TEMP_DIR, tstfile)
    err = call("-C", TREE_NAME, "-q",
               "--import", tst_file,
               "--export", result_file)[1]
    if "Cleaning up." not in err:
        return "Export failed, no 'Cleaning up.'"
    msg = compare(expect_file, result_file, dfilter)
    if not msg:
        # we will leave the result_file in place if there was an error.
        try:
            os.remove(result_file)
        except OSError:
            pass
        return
    else:
        return msg


def compare(expect_file, result_file, dfilter=None):
    """ This uses the diff library to compare two files
    """
    with open(expect_file, encoding='utf-8_sig', errors='surrogateescape')\
         as exp_f, \
         open(result_file, encoding='utf-8_sig', errors='surrogateescape')\
         as res_f:
        diff = difflib.unified_diff(exp_f.readlines(),
                                    res_f.readlines(),
                                    n=2, lineterm='\n')
        msg = ""
        fail = False
        for line in diff:
            if line == "--- \n" or line == "+++ \n":
                continue
            msg += line
            if dfilter:
                fail += dfilter(line)
        return msg if fail else ""


def gedfilt(line):
    """ A filter for Gedcom files.
    This implements a filter that allows some differences to be ignored.
    The differences are not functional, but are related to changes in Gramps
    version, file date/time and filename.
    """
    def get_prev_token(back):
        if back > gedfilt.indx:
            return None
        return gedfilt.prev[gedfilt.indx - back][0]
    #pylint: disable=unsubscriptable-object
    if line.startswith('@@'):
        gedfilt.prev = [None] * 8
        gedfilt.indx = 0
        return False
    retval = True
    diftyp = line[0]
    line = line[1:].partition(' ')
    level = int(line[0])
    token, toss, line = line[2].partition(' ')
    if diftyp == ' ':
        # save the line for later if needed to figure out the data element
        gedfilt.prev[gedfilt.indx] = token, level, line
        gedfilt.indx = (gedfilt.indx + 1) % 8
        retval = False
    elif diftyp == '-':
        # save the line for later if needed to figure out the data element
        gedfilt.prev[gedfilt.indx] = token, level, line
        gedfilt.indx = (gedfilt.indx + 1) % 8
        if token == "VERS" and get_prev_token(2) == "SOUR":
            # we must have a header with Gramps version
            retval = False
        elif token == "DATE" and get_prev_token(2) == "NAME":
            # we must have a header with file date
            retval = False
        elif token == "TIME" and get_prev_token(2) == "DATE":
            # probably have a header with file time
            retval = False
        elif token == "FILE" and line.endswith('.ged\n'):
            # probably have a header with file name
            retval = False
        elif token == "FILE" and "tests" in line:
            # probably have a media with file name
            retval = False
        elif token == "COPR" and "Copyright (c) " in line:
            # probably have a copyright line with year
            retval = False
    else:   # this is an addition
        if token == "VERS" and get_prev_token(1) == "VERS":
            # we must have a header with Gramps version
            retval = False
        elif token == "DATE" and (get_prev_token(2) == "NAME" or
                                  get_prev_token(3) == "NAME"):
            # we must have a header with file date
            retval = False
        elif token == "TIME" and (get_prev_token(2) == "DATE" or
                                  get_prev_token(3) == "DATE"):
            # probably have a header with file time
            retval = False
        elif token == "FILE" and line.endswith('.ged\n'):
            # probably have a header with file name
            retval = False
        elif token == "FILE" and "tests" in line:
            # probably have a media with file name
            retval = False
        elif token == "COPR" and "Copyright (c) " in line:
            # probably have a copyright line with year
            retval = False
    return retval


def vcffilt(line):
    """ A filter for VCard files.
    This implements a filter that allows some differences to be ignored.
    The differences are not functional, but are related to changes in Gramps
    version.
    """
    diftyp = line[0]
    if diftyp == '@':
        retval = False
    elif diftyp == ' ':
        retval = False
    elif 'PRODID:' in line:  # Gramps version is on these lines
        retval = False
    else:
        retval = True
    return retval


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
        call("-y", "-q", "--remove", TREE_NAME)

    def test_csv(self):
        """ Run a csv export test """
        set_format(0)   # Use ISO date for test
        src_file = 'exp_sample_csv.gramps'
        tst_file = 'exp_sample_csv.csv'
        msg = do_it(src_file, tst_file)
        if msg:
            self.fail(tst_file + ': ' + msg)

    def test_ged(self):
        """ Run a Gedcom export test """
        config.set('preferences.place-auto', True)
        src_file = 'exp_sample.gramps'
        tst_file = 'exp_sample_ged.ged'
        msg = do_it(src_file, tst_file, gedfilt)
        if msg:
            self.fail(tst_file + ': ' + msg)

    def test_vcard(self):
        """ Run a vcard export test """
        config.set('preferences.place-auto', True)
        src_file = 'exp_sample.gramps'
        tst_file = 'exp_sample.vcf'
        msg = do_it(src_file, tst_file, vcffilt)
        if msg:
            self.fail(tst_file + ': ' + msg)

    def test_vcs(self):
        """ Run a Vcalandar export test """
        config.set('preferences.place-auto', True)
        src_file = 'exp_sample.gramps'
        tst_file = 'exp_sample.vcs'
        msg = do_it(src_file, tst_file)
        if msg:
            self.fail(tst_file + ': ' + msg)

    def test_gw(self):
        """ Run a Geneweb export test """
        config.set('preferences.place-auto', True)
        src_file = 'exp_sample.gramps'
        tst_file = 'exp_sample.gw'
        msg = do_it(src_file, tst_file)
        if msg:
            self.fail(tst_file + ': ' + msg)

    def test_wft(self):
        """ Run a Web Family Tree export test """
        set_format(0)   # Use ISO date for test
        config.set('preferences.place-auto', True)
        src_file = 'exp_sample.gramps'
        tst_file = 'exp_sample.wft'
        msg = do_it(src_file, tst_file)
        if msg:
            self.fail(tst_file + ': ' + msg)

if __name__ == "__main__":
    unittest.main()
