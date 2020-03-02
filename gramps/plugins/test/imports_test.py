#! /usr/bin/env python3
""" Test program for import modules
"""
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2016 Gramps Development Team
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import unittest
import os
import sys
import re
import locale
from time import localtime, strptime
from unittest.mock import patch
#import logging

from gramps.gen.utils.config import config
config.set('preferences.date-format', 0)
from gramps.gen.db.utils import import_as_dict
from gramps.gen.merge.diff import diff_dbs, to_struct
from gramps.gen.simple import SimpleAccess
from gramps.gen.utils.id import set_det_id
from gramps.gen.user import User
from gramps.gen.const import TEMP_DIR, DATA_DIR
from gramps.test.test_util import capture
from gramps.plugins.export.exportxml import XmlWriter

#logger = logging.getLogger(__name__)

# the following defines where to find the test import and result files
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))

# ------------------------------------------------------------------
#  Local Functions
# ------------------------------------------------------------------

# These tests assume a US date and time format.
try:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except locale.Error:     # seems to fail on Windows system for some reason
    locale.setlocale(locale.LC_ALL, 'English_United States')


def mock_time(*args):
    """
    Mock up a dummy to replace the varying 'time string results'
    """
    return 946101600.

def mock_localtime(*args):
    """
    Mock up a dummy to replace the varying 'time string results'
    """
    return strptime("25 Dec 1999", "%d %b %Y")

class TestImports(unittest.TestCase):
    """The test class cases will be dynamically created at import time from
    files to be tested.  The following defs are used by the test cases
    """

    def prepare_result(self, diffs, added, missing):
        """ Looks through the diffs, added, and missing items and begins
        reporting process.  Returns True if there were significant errors.
        """
        # pylint: disable=E1101
        # pylint does not like dynamically created methods
        deltas = False
        if diffs:
            for diff in diffs:
                obj_type, item1, item2 = diff
                msg = self._report_diff(obj_type, to_struct(item1),
                                        to_struct(item2))
                if msg != "":
                    if hasattr(item1, "gramps_id"):
                        self.msg += "%s: %s  handle=%s\n" % \
                            (obj_type, item1.gramps_id,
                             getattr(item1, "handle"))
                    else:
                        self.msg += "%s: %s\n" % (obj_type, item1.get_name())
                    self.msg += msg
                    deltas = True
        if missing:
            deltas = True
            sac = SimpleAccess(self.database1)
            for pair in missing:
                obj_type, item = pair
                self.msg += "Missing %s: %s\n" % (obj_type, sac.describe(item))
        if added:
            deltas = True
            sac = SimpleAccess(self.database2)
            for pair in added:
                obj_type, item = pair
                self.msg += "Added %s: %s\n" % (obj_type, sac.describe(item))
        return deltas


    def _report_diff(self, path, struct1, struct2):
        """
        Compare two struct objects and report differences.
        """
        msg = ""
        if struct1 == struct2:
            return ""
        elif (isinstance(struct1, (list, tuple)) or
              isinstance(struct2, (list, tuple))):
            len1 = len(struct1) if isinstance(struct1, (list, tuple)) else 0
            len2 = len(struct2) if isinstance(struct2, (list, tuple)) else 0
            for pos in range(max(len1, len2)):
                value1 = struct1[pos] if pos < len1 else None
                value2 = struct2[pos] if pos < len2 else None
                msg += self._report_diff(path + ("[%d]" % pos), value1, value2)
        elif isinstance(struct1, dict) or isinstance(struct2, dict):
            keys = struct1.keys() if isinstance(struct1, dict)\
                                  else struct2.keys()
            for key in keys:
                value1 = struct1[key] if struct1 is not None else None
                value2 = struct2[key] if struct2 is not None else None
                if key == "dict":  # a raw dict, not a struct
                    msg += _report_details(path, value1, value2)
                else:
                    msg += self._report_diff(path + "." + key, value1, value2)
        else:
            msg += _report_details(path, struct1, struct2)
        return msg


def _report_details(path, diff1, diff2):
    """ Checks if a detail is significant, needs adjusting for xml filter
    effects, and returns a string describing the specific difference.
    """
    if isinstance(diff1, bool):
        desc1 = repr(diff1)
    else:
        desc1 = str(diff1) if diff1 else ""
    if isinstance(diff2, bool):
        desc2 = repr(diff2)
    else:
        desc2 = str(diff2) if diff2 else ""
    d1t = type(diff1)
    d2t = type(diff2)
    # the xml exporter edits the data base by stripping spaces, so
    # we have to ignore these differences
    if d1t == str:
        diff1 = diff1.strip()
    if d2t == str:
        diff2 = diff2.strip()
    d1l = len(diff1) if d1t == str else ""
    d2l = len(diff2) if d2t == str else ""
    # 'change' date is not significant for comparison
    if path.endswith(".change"):
        return ""
    # the xml exporter edits the data base by converting media path
    # to unix '/' conventions, so we have to ignore these differences
    if path == "Media.path":
        diff1 = diff1.replace('\\', '/')
    if diff1 != diff2:
        msg = "  Diff on: %s\n    %s%s: %s\n    %s%s: %s\n" % \
            (_format_struct_path(path), d1t, d1l, desc1,
             d2t, d2l, desc2)
        return msg
    return ""


def _format_struct_path(path):
    """ prepares a 'path' string for the report out of the structure.
    """
    retval = ""
    parts = path.split(".")
    for part in parts:
        if retval:
            retval += ", "
        if "[" in part and "]" in part:
            part, index = re.match(r"(.*)\[(\d*)\]", part).groups()
            retval += "%s #%s" % (part.replace("_", " "), int(index) + 1)
        else:
            retval += part
    return retval


def make_tst_function(tstfile, file_name):
    """ This is here to support the dynamic function creation.  This creates
    the test function (a method, to be precise).
    """

    @patch('gramps.plugins.db.dbapi.dbapi.time')
    @patch('gramps.gen.utils.unknown.localtime')
    @patch('gramps.gen.utils.unknown.time')
    @patch('time.localtime')
    def tst(self, mockptime, mocktime, mockltime, mockdtime):
        """ This compares the import file with the expected result '.gramps'
        file.
        """
        mockptime.side_effect = mock_localtime
        mocktime.side_effect = mock_time
        mockltime.side_effect = mock_localtime
        mockdtime.side_effect = mock_time
        fn1 = os.path.join(TEST_DIR, tstfile)
        fn2 = os.path.join(TEST_DIR, (file_name + ".gramps"))
        fres = os.path.join(TEMP_DIR, (file_name + ".difs"))
        fout = os.path.join(TEMP_DIR, (file_name + ".gramps"))
        if "_dfs" in tstfile:
            config.set('preferences.default-source', True)
            config.set('preferences.tag-on-import-format', "Imported")
            config.set('preferences.tag-on-import', True)
            skp_imp_adds = False
        else:
            skp_imp_adds = True
            config.set('preferences.default-source', False)
            config.set('preferences.tag-on-import', False)
        try:
            os.remove(fres)
            os.remove(fout)
        except OSError:
            pass
        #logger.info("\n**** %s ****", tstfile)
        set_det_id(True)
        with capture(None) as output:
            self.user = User()
            self.database1 = import_as_dict(fn1, self.user,
                                            skp_imp_adds=skp_imp_adds)
            set_det_id(True)
            self.database2 = import_as_dict(fn2, self.user)
        self.assertIsNotNone(self.database1,
                             "Unable to import file: %s" % fn1)
        self.assertIsNotNone(self.database2,
                             "Unable to import expected result file: %s" % fn2)
        if self.database2 is None or self.database1 is None:
            return
        diffs, added, missing = diff_dbs(self.database1,
                                         self.database2, self.user)
        self.msg = "Mismatch on file: %s\n" % tstfile
        deltas = self.prepare_result(diffs, added, missing)
        # We save a copy of any issues in the users Gramps TEMP_DIR in a file
        # with a '.difs' extension, as well as usual unittest report
        # Also we save the .gramps file from the import so user can perform
        # Diff himself for better context.
        if deltas:
            writer = XmlWriter(self.database1, self.user,
                               strip_photos=0, compress=0)
            writer.write(fout)
            hres = open(fres, mode='w', encoding='utf-8',
                        errors='replace')
            hres.write(self.msg)
            hres.close()
            # let's see if we have any allowed exception file
            fdif = os.path.join(TEST_DIR, (file_name + ".difs"))
            try:
                hdif = open(fdif)
                msg = hdif.read()
                hdif.close()
            except (FileNotFoundError, IOError):
                msg = ""
            # if exception file matches exactly, we are done.
            if self.msg != msg:
                self.msg = "\n****Captured Output****\n" + output[0] + \
                    "\n****Captured Err****\n" + output[1] + \
                    "\n****End Capture Err****\n" + self.msg
                self.fail(self.msg)
    return tst

# let's see if we have a single file to run, example;
#    "python test_import.py -i sample.ged"
# This only works for files in normal test directory, so don't add a path
#pylint: disable=invalid-name
_tstfile = ""
if __name__ == "__main__":
    for i, option in enumerate(sys.argv):
        if option == '-i':
            _tstfile = sys.argv[i+1]
            del sys.argv[i]
            del sys.argv[i]
# The following code dynamically creates the methods for each test file.
# The methods are inserted at load time into the 'TestImports' class
# via the modules' globals, taking advantage that they are a dict.
if _tstfile:                             # single file mode
    (fname, ext) = os.path.splitext(os.path.basename(_tstfile))
    test_func = make_tst_function(_tstfile, fname)
    tname = "test_" + _tstfile.replace("-", "_").replace(".", "_")
    test_func.__name__ = tname
    test_func.__doc__ = tname
    setattr(TestImports, tname, test_func)
else:
    for _tstfile in os.listdir(TEST_DIR):
        (fname, ext) = os.path.splitext(os.path.basename(_tstfile))
        if _tstfile != "SAMPLE.DEF" and (ext in (".gramps", ".difs", ".bak") \
                or not fname.startswith("imp_")):
            continue
        test_func = make_tst_function(_tstfile, fname)
        tname = "test_" + _tstfile.replace("-", "_").replace(".", "_")
        test_func.__name__ = tname
        test_func.__doc__ = tname
        setattr(TestImports, tname, test_func)
    test_func = None  # keep nosetest from finding last one again

if __name__ == "__main__":
    unittest.main()
