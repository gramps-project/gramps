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

from gramps.test.test_util import Gramps

ddir = os.path.dirname(__file__)
example = os.path.join(ddir, "..", "..", "..",
                       "example", "gramps", "data.gramps")

TREE_NAME = "Test_reporttest"

class ReportControl(object):
    def tearDown(self):
        out, err = self.call("-y", "--remove", TREE_NAME)

    def call(self, *args):
        print("call:", args)
        self.gramps = Gramps()
        out, err = self.gramps.run(*args)
        print("out:", out, "err:", err)
        return out, err

    def __init__(self):
        super().__init__()
        self.tearDown() # removes it if it existed
        out, err = self.call("-C", TREE_NAME, 
                             "--import", example)
        out, err = self.call("-O", TREE_NAME, 
                             "--action", "report", 
                             "--options", "show=all")
        self.reports = []
        for line in err.split("\n"):
            if line.startswith("   "):
                report_name, description = line.split("- ", 1)
                self.reports.append(report_name.strip())

    def testall(self, class_):
        count = 0
        print(self.reports)
        for report_name in self.reports:
            print("add attr:", report_name)
            setattr(class_, "test_%s" % count, dynamic_method(
                "--force",
                "-O", TREE_NAME, 
                "--action", "report", 
                "--options", "name=%s" % report_name))
            count += 1

    def addtest(self, class_, report_name, test_function, options):
        test_name = report_name.replace("-", "_")
        setattr(class_, test_name, dynamic_method(
            report_name,
            test_function,
            "--force",
            "-O", TREE_NAME, 
            "--action", "report", 
            "--options", "name=%s,%s" % (report_name, options)))

def dynamic_method(report_name, test_function, *args):
    # This needs to have "test" in name:
    def test_method(self):
        out, err = self.call(*args)
        self.assertTrue(test_function(out, err, report_name))
    return test_method

class TestDynamic(unittest.TestCase):
    @classmethod
    def call(cls, *args):
        print("call:", args)
        gramps = Gramps()
        out, err = gramps.run(*args)
        print("out:", out, "err:", err)
        return out, err

    @classmethod
    def tearDownClass(cls):
        out, err = cls.call("-y", "--remove", TREE_NAME)

reports = ReportControl()

# If you could run all reports in a standard way:
#reports.testall(TestDynamic)

def report_contains(text):
    def test_output_file(out, err, report_name):
        contents = open(report_name + ".txt").read()
        print(contents)
        return text in contents
    return test_output_file

def err_does_not_contain(text):
    def test_output_file(out, err, report_name):
        print(err)
        return text not in err
    return test_output_file

reports.addtest(TestDynamic, "tag_report", 
                report_contains("I0037  Smith, Edwin Michael"),
                'off=txt,tag=tag1')

reports.addtest(TestDynamic, "navwebpage", 
                err_does_not_contain("Failed to write report."),
                'off=html')

if __name__ == "__main__":
    unittest.main()
