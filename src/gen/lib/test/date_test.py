#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
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

# $Id$

""" Unittest for testing dates """

import unittest
from test import test_util
test_util.path_append_parent() 

import Config
from DateHandler import parser as df

class Tester(unittest.TestCase):
    def __init__(self, method_name, part, testdata):
        self.__dict__[method_name + ("-%d" % part)] = lambda: self.helper(part, *testdata)
        unittest.TestCase.__init__(self, method_name + ("-%d" % part))

    def helper(self, part, d1, d2, expected1, expected2 = None):
        """
        Tests two GRAMPS dates to see if they match.
        """
        if expected2 == None:
            expected2 = expected1
        pos1 = 1
        if expected1 :
            pos1 = 0
        pos2 = 1
        if expected2 :
            pos2 = 0
        date1 = df.parse(d1)
        date2 = df.parse(d2)
        if part == 1:
            val = date2.match(date1)
            self.assertTrue(val == expected1, "'%s' and '%s' did not match" % (d1, d2))
        else:
            val = date1.match(date2)
            self.assertTrue(val == expected2, "'%s' and '%s' did not match" % (d2, d1))


def suite():
    """ interface to automated test runner test/regrtest.py """
    Config.set(Config.DATE_BEFORE_RANGE, 9999)
    Config.set(Config.DATE_AFTER_RANGE, 9999)
    Config.set(Config.DATE_ABOUT_RANGE, 10)
    # most are symmetric: #date1, date2, does d1 match d2? does d2 match d1?
    tests = [("before 1960", "before 1961", True),
             ("before 1960", "before 1960", True),
             ("before 1961", "before 1961", True),
             ("jan 1, 1960", "jan 1, 1960", True),
             ("dec 31, 1959", "dec 31, 1959", True),
             ("before 1960", "jan 1, 1960", False), 
             ("before 1960", "dec 31, 1959", True),
             ("abt 1960", "1960", True),
             ("abt 1960", "before 1960", True),
             ("1960", "1960", True),
             ("1960", "after 1960", False),
             ("1960", "before 1960", False),
             ("abt 1960", "abt 1960", True),
             ("before 1960", "after 1960", False),
             ("after jan 1, 1900", "jan 2, 1900", True),
             ("abt jan 1, 1900", "jan 1, 1900", True),
             ("from 1950 to 1955", "1950", True),
             ("from 1950 to 1955", "1951", True),
             ("from 1950 to 1955", "1952", True),
             ("from 1950 to 1955", "1953", True),
             ("from 1950 to 1955", "1954", True),
             ("from 1950 to 1955", "1955", True),
             ("from 1950 to 1955", "1956", False),
             ("from 1950 to 1955", "dec 31, 1955", True),
             ("from 1950 to 1955", "jan 1, 1955", True),
             ("from 1950 to 1955", "dec 31, 1949", False),
             ("from 1950 to 1955", "jan 1, 1956", False),
             ("after jul 4, 1980", "jul 4, 1980", False),
             ("after jul 4, 1980", "before jul 4, 1980", False),
             ("after jul 4, 1980", "about jul 4, 1980", True),
             ("after jul 4, 1980", "after jul 4, 1980", True),
             ("between 1750 and 1752", "1750", True),
             ("between 1750 and 1752", "about 1750", True),
             ("between 1750 and 1752", "between 1749 and 1750", True),
             ("between 1750 and 1752", "1749", False),
             ("invalid date", "invalid date", True),
             ("invalid date", "invalid", False, True),
             ("invalid date 1", "invalid date 2", False),
             ("abt jan 1, 2000", "dec 31, 1999", True),
             ("jan 1, 2000", "dec 31, 1999", False),
             ("aft jan 1, 2000", "dec 31, 1999", False),
             ("after jan 1, 2000", "after dec 31, 1999", True),
             ("after dec 31, 1999", "after jan 1, 2000", True),
             ("1 31, 2000", "jan 1, 2000", False),
             ("dec 31, 1999", "jan 1, 2000", False),
             ("jan 1, 2000", "before dec 31, 1999", False),
             ("aft jan 1, 2000", "before dec 31, 1999", False),
             ("before jan 1, 2000", "after dec 31, 1999", False),
             ("jan 1, 2000/1", "jan 1, 2000", False),
             ("jan 1, 2000/1", "jan 1, 2001", True),
             ("about 1984", "about 2005", False),
             ("about 1990", "about 2005", True), 
             ("about 2007", "about 2006", True), 
             ("about 1995", "after 2000", True), 
             ("about 1995", "after 2005", False),
             ("about 2007", "about 2003", True), 
             ("before 2007", "2000", True), 
             # different calendar, same date
             ("Aug 3, 1982", "14 Thermidor 190 (French Republican)", True),  
             ("after Aug 3, 1982", 
              "before 14 Thermidor 190 (French Republican)", False), 
             ("ab cd", "54 ab cd 2000", True, False),
             ]
    suite = unittest.TestSuite()            
    count = 1
    for test in tests:
        suite.addTest(Tester('test_match%04d' % count, 1, test))
        suite.addTest(Tester('test_match%04d' % count, 2, test))
        count += 1
    return suite

def assert_func(exp1, exp2):
    Date = date.Date
    e1 = eval(exp1)
    e2 = eval(exp2)
    assert e1 == e2, "%s should be %s but was %s" % (exp1, e2, e1)

class Assert(unittest.TestCase):
    def __init__(self, method_name, part, exp1, exp2):
        self.__dict__[method_name + ("-%d" % part)] = \
            lambda: assert_func(exp1, exp2)
        unittest.TestCase.__init__(self, method_name + ("-%d" % part))

def suite2():
    """ interface to automated test runner test/regrtest.py """
    Config.set(Config.DATE_BEFORE_RANGE, 9999)
    Config.set(Config.DATE_AFTER_RANGE, 9999)
    Config.set(Config.DATE_ABOUT_RANGE, 10)
    tests = [
        # Date +/- int/tuple -> Date
        ("Date(2008, 1, 1) - 1", "Date(2007, 1, 1)"),
        ("Date(2008, 1, 1) + 1", "Date(2009, 1, 1)"),
        ("Date(2008, 1, 1) - (0,0,1)", "Date(2007, 12, 31)"),
        ("Date(2008, 1, 1) - (0,0,2)", "Date(2007, 12, 30)"),
        ("Date(2008) - (0,0,1)", "Date(2007, 12, 31)"),
        ("Date(2008) - 1", "Date(2007, 1, 1)"),
        ("Date(2008, 12, 31) + (0, 0, 1)", "Date(2009, 1, 1)"),
        ("Date(2000,1,1) - (0,11,0)", "Date(1999,02,01)"),
        ("Date(2000,1,1) - (0,1,0)", "Date(1999, 12, 1)"),
        ("Date(2008, 1, 1) + (0, 0, 32)", "Date(2008, 02, 02)"),
        ("Date(2008, 2, 1) + (0, 0, 32)", "Date(2008, 03, 04)"),
        ("Date(2000) - (0, 1, 0)", "Date(1999, 12, 1)"),
        ("Date(2000) + (0, 1, 0)", "Date(2000, 1, 0)"), # Ok?
        ("Date(2000, 1, 1) - (0, 1, 0)", "Date(1999, 12, 1)"),
        ("Date(2000, 1, 1) - 1", "Date(1999, 1, 1)"),
        ("Date(2000) - 1", "Date(1999)"),
        ("Date(2000) + 1", "Date(2001)"),

#My great great grandfather died on 1876-05-07.
#He died at an age of 65 years, 5 month 17 days according to the books:
#> Date(1876,5,7)-(65,5,17)
#1811-12-21
#> Date(1876,5,7)-Date(1811,12,21)
#(64, 4, 17)
#But his correct birth date is 1810-11-20:
#("Date(1876,5,7)-Date(1810,11,20)", "(65, 5, 18)")
        ("Date(1876,5,7) - Date(1876,5,1)", "(0, 0, 6)"),
        ("Date(1876,5,7) - Date(1876,4,30)", "(0, 0, 7)"),
        ("Date(2000,1,1) - Date(1999,2,1)", "(0, 11, 0)"),
        ("Date(2000,1,1) - Date(1999,12,1)", "(0, 1, 0)"),
        # Date +/- Date -> tuple
        ("Date(2007, 12, 23) - Date(1963, 12, 4)", "(44, 0, 19)"),
        ]
    suite = unittest.TestSuite()            
    count = 1
    for (exp1, exp2) in tests:
        suite.addTest(Assert('test_assert%04d' % count, 1, exp1, exp2))
        count += 1
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
    unittest.TextTestRunner().run(suite2())
