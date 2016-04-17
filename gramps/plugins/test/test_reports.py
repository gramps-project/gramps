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

    def addtest(self, class_, report_name, test_function,
                files, **options):
        test_name = report_name.replace("-", "_")
        setattr(class_, test_name, dynamic_method(
            report_name,
            test_function,
            files,
            "--force",
            "-O", TREE_NAME,
            "--action", "report",
            "--options", "name=%s" % report_name,
            **options))

def dynamic_method(report_name, test_function,
                   files, *args, **options):
    args = list(args)
    args[-1] += "," + (",".join(["%s=%s" % (k, v) for (k,v) in options.items()]))
    options["files"] = files
    # This needs to have "test" in name:
    def test_method(self):
        out, err = self.call(*args)
        self.assertTrue(test_function(out, err, report_name, **options))
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

def report_contains(text):
    def test_output_file(out, err, report_name, **options):
        ext = options["off"]
        with open(report_name + "." + ext) as fp:
            contents = fp.read()
        print(contents)
        os.remove(report_name + "." + ext)
        for filename in options.get("files", []):
            os.remove(filename)
        return text in contents
    return test_output_file

def err_does_not_contain(text):
    def test_output_file(out, err, report_name, **options):
        ext = options["off"]
        print(err)
        os.remove(report_name + "." + ext)
        for filename in options.get("files", []):
            os.remove(filename)
        return text not in err
    return test_output_file

reports.addtest(TestDynamic, "tag_report",
                report_contains("I0037  Smith, Edwin Michael"),
                [],
                off="txt", tag="tag1")

#reports.addtest(TestDynamic, "navwebpage",
#                err_does_not_contain("Failed to write report."),
#                off="html")

### Three hashes: capture out/err seems to conflict with Travis/nose proxy:

report_list = [
    ##("ancestor_chart", "pdf", []), # Ancestor Tree
    ("ancestor_report", "txt", []), # Ahnentafel Report
    ("birthday_report", "txt", []), # Birthday and Anniversary Report
    # ("calendar", "svg", ["calendar-10.svg", "calendar-11.svg",
    #                      "calendar-12.svg", "calendar-2.svg",
    #                      "calendar-3.svg", "calendar-4.svg",
    #                      "calendar-5.svg", "calendar-6.svg",
    #                      "calendar-7.svg", "calendar-8.svg",
    #                      "calendar-9.svg"]), # Calendar
    ## ("d3-ancestralcollapsibletree", "txt"), # Ancestral Collapsible Tree
    ## ("d3-ancestralfanchart", "txt"), # Ancestral Fan Chart
    ## "d3-descendantindentedtree", # Descendant Indented Tree
    ### ("database-differences-report", "txt", []), # Database Differences Report
    ## "denominoviso", # DenominoViso
    ##("descend_chart", "svg", []), # Descendant Tree
    ("descend_report", "txt", []), # Descendant Report
    ### ("DescendantBook", "txt", []), # Descendant Book
    ## ("Descendants Lines", "txt"), # Descendants Lines
    ("det_ancestor_report", "txt", []), # Detailed Ancestral Report
    ("det_descendant_report", "txt", []), # Detailed Descendant Report
    ### ("DetailedDescendantBook", "txt", []), # Detailed Descendant Book
    ## ("DynamicWeb", "txt"), # Dynamic Web Report
    ("endofline_report", "txt", []), # End of Line Report
    ##("family_descend_chart", "svg", []), # Family Descendant Tree
    ("family_group", "txt", []), # Family Group Report
    ##("familylines_graph", "svg", []), # Family Lines Graph
    # ("FamilyTree", "svg", []), # Family Tree
    # ("fan_chart", "svg", []), # Fan Chart
    # ("hourglass_graph", "svg", []), # Hourglass Graph
    ("indiv_complete", "txt", []), # Complete Individual Report
    ("kinship_report", "txt", []), # Kinship Report
    ### ("LastChangeReport", "txt", []), # Last Change Report
    ### ("LinesOfDescendency", "txt", []), # Lines of Descendency Report
    ## "ListeEclair", # Tiny Tafel
    ("notelinkreport", "txt", []), # Note Link Report
    ("number_of_ancestors", "txt", []), # Number of Ancestors Report
    ##("PedigreeChart", "svg", ["PedigreeChart-2.svg"]), # Pedigree Chart
    ### ("PersonEverythingReport", "txt", []), # PersonEverything Report
    ## "place_report", # Place Report
    ("records", "txt", []), # Records Report
    ##("rel_graph", "pdf", []), # Relationship Graph
    ### ("Repositories Report", "txt", []), # Repositories Report
    ### ("Repositories Report Options", "txt", []), # Repositories Report Options
    # ("statistics_chart", "svg", ["statistics_chart-2.svg",
    #                              "statistics_chart-3.svg"]), # Statistics Charts
    ("summary", "txt", []), # Database Summary Report
    ##("timeline", "pdf", []), # Timeline Chart
    ### ("TodoReport", "txt", []), # Todo Report
    ## ("WebCal", "txt"), # Web Calendar
]

for (report_name, off, files) in report_list:
    reports.addtest(TestDynamic, report_name,
                    err_does_not_contain("Failed to write report."),
                    files=files,
                    off=off)

if __name__ == "__main__":
    unittest.main()
