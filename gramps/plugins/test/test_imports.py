#! /usr/bin/env python3
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
import time


from gramps.gen.merge.diff import diff_dbs, import_as_dict
from gramps.gen.simple import SimpleAccess
from gramps.gen.utils.id import set_det_id
from gramps.cli import user
from gramps.gen.const import TEMP_DIR, DATA_DIR

# the following defines where to find the test import and result files
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))

# ------------------------------------------------------------------
#  Local Functions
# ------------------------------------------------------------------


def todate(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


class CompleteCheck(unittest.TestCase):
    """The test class cases will be dynamically created at import time from
    files to be tested.  The following defs are used by the test cases"""

    def prepare_result(self, diffs, added, missing):
        deltas = False
        if diffs:
            for diff in diffs:
                obj_type, item1, item2 = diff
                msg = self.report_diff(obj_type, item1.to_struct(),
                                       item2.to_struct())
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
            sa = SimpleAccess(self.database1)
            for pair in missing:
                obj_type, item = pair
                self.msg += "Missing %s: %s\n" % (obj_type, sa.describe(item))
        if added:
            deltas = True
            sa = SimpleAccess(self.database2)
            for pair in added:
                obj_type, item = pair
                self.msg += "Added %s: %s\n" % (obj_type, sa.describe(item))
        return deltas

    def format_struct_path(self, path):
        retval = ""
        parts = path.split(".")
        for part in parts:
            if retval:
                retval += ", "
            if "[" in part and "]" in part:
                part, index = re.match("(.*)\[(\d*)\]", part).groups()
                retval += "%s #%s" % (part.replace("_", " "), int(index) + 1)
            else:
                retval += part
        return retval

    def report_details(self, path, diff1, diff2):
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
        # we have to ignore these differeces
        if d1t == str: diff1 = diff1.strip()
        if d2t == str: diff2 = diff2.strip()
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
                (self.format_struct_path(path), d1t, d1l, desc1,
                 d2t, d2l, desc2)
            return msg
        return ""

    def report_diff(self, path, struct1, struct2):
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
                msg += self.report_diff(path + ("[%d]" % pos), value1, value2)
        elif isinstance(struct1, dict) or isinstance(struct2, dict):
            keys = struct1.keys() if isinstance(struct1, dict)\
                                  else struct2.keys()
            for key in keys:
                value1 = struct1[key] if struct1 is not None else None
                value2 = struct2[key] if struct2 is not None else None
                if key == "dict":  # a raw dict, not a struct
                    msg += self.report_details(path, value1, value2)
                else:
                    msg += self.report_diff(path + "." + key, value1, value2)
        else:
            msg += self.report_details(path, struct1, struct2)
        return msg


# The following make_test_function creates a test function (a method,
# to be precise) that compares the import file with the expected
# result '.gramps' file.
def make_tst_function(tstfile, fname):
    def tst(self):
        self._user = user.User(quiet=True)
        f1 = os.path.join(TEST_DIR, tstfile)
        f2 = os.path.join(TEST_DIR, (fname + ".gramps"))
        fres = os.path.join(TEMP_DIR, (fname + ".difs"))
        try:
            os.remove(fres)
        except OSError:
            pass
        print("\n**** %s ****" % tstfile)
        set_det_id(True)
        self.database1 = import_as_dict(f1, self._user)
        set_det_id(True)
        self.database2 = import_as_dict(f2, self._user)
        self.assertIsNotNone(self.database1,
                             "Unable to import file: %s" % f1)
        self.assertIsNotNone(self.database2,
                             "Unable to import expected result file: %s" % f2)
        if self.database2 is None or self.database1 is None:
            return
        diffs, added, missing = diff_dbs(self.database1,
                                         self.database2, self._user)
        self.msg = "Mismatch on file: %s\n" % tstfile
        deltas = self.prepare_result(diffs, added, missing)
        # We save a copy of any issues in the users Gramps TEMP_DIR in a file
        # with a '.difs' extension, as well as usual unittest report
        if deltas:
            hres = open(fres, mode='w', encoding='utf-8',
                        errors='replace')
            hres.write(self.msg)
            hres.close()
            # let's see if we have any allowed exception file
            fdif = os.path.join(TEST_DIR, (fname + ".difs"))
            try:
                hdif = open(fdif)
                msg = hdif.read()
                hdif.close()
            except:
                msg = ""
            # if exception file matches exactly, we are done.
            if self.msg != msg:
                self.fail(self.msg)
    return tst

# let's see if we have a single file to run, example;
#    "python test_import.py -i sample.ged"
# This only works for files in normal test directory, so don't add a path
tstfile = ""
if __name__ == "__main__":
    for i, option in enumerate(sys.argv):
        if option == '-i':
            tstfile = sys.argv[i+1]
            del sys.argv[i]
            del sys.argv[i]
# The following code dynamically creates the methods for each test file.
# The methods are inserted at load time into the 'CompleteCheck' class
# via the modules' globals, taking advantage that they are a dict.
if tstfile:                             # single file mode
    (fname, ext) = os.path.splitext(os.path.basename(tstfile))
    test_func = make_tst_function(tstfile, fname)
    clname = 'Import_{0}'.format(tstfile)
    globals()[clname] = type(clname,
                             (CompleteCheck,),
                             {"testit": test_func})
#                             {"test:" + fname: test_func})
else:
    for tstfile in os.listdir(TEST_DIR):
        (fname, ext) = os.path.splitext(os.path.basename(tstfile))
        if ext == ".gramps" or ext == ".difs" or ext == ".bak":
            continue
        test_func = make_tst_function(tstfile, fname)
        clname = 'Import_{0}'.format(tstfile)
        globals()[clname] = type(clname,
                                 (CompleteCheck,),
                                 {"testit": test_func})
#                                 {"test:" + fname: test_func})


if __name__ == "__main__":
    unittest.main()
