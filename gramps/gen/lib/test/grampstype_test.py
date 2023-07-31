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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" unittest for grampstype """

import unittest

from ..grampstype import GrampsType

# some simple map items to test with
vals = "zz ab cd ef".split()
keys = list(range(len(vals)))
MAP = [(k, v * 2, v) for (k, v) in zip(keys, vals)]
BLIST = [1, 3]


class GT0(GrampsType):
    _DEFAULT = 1  # just avoiding the pre-coded 0
    _CUSTOM = 3  # just avoiding the pre-coded 0
    _DATAMAP = MAP


# NOTE: this type of code might be used in a migration utility
#   to allow conversions or other handling of retired type-values
# A migration utility might instantiate several of these with
#   varying blacklist-specs
class GT1(GT0):
    _BLACKLIST = BLIST


class GT2(GT1):
    _BLACKLIST = None


class Test1(unittest.TestCase):
    # some basic tests
    def test_basic(self):
        self.gt = GT0()
        self.assertTrue(isinstance(self.gt, GrampsType))
        # spot-check that MAPs get built
        e = len(keys)
        g = len(self.gt._E2IMAP)
        self.assertEqual(g, e)

    # init sets values for int, str, tuple
    # (we ignore instance here -- maybe SB tested, too?)
    # this test depends on having _DEFAULT=1, _CUSTOM=3
    # NB: tuple tests w/ lengths < 2 fail before release 10403
    def test_init_value(self):
        for i, v, u in (
            (None, 1, "abab"),  # all DEFAULT
            (0, 0, "zzzz"),
            (1, 1, "abab"),
            ("efef", 3, "efef"),  # matches CUSTOM
            ("zzzz", 0, "zzzz"),
            ("x", 3, "x"),  # nomatch gives CUSTOM
            ("", 3, ""),  # nomatch gives CUSTOM
            ((0, "zero"), 0, "zzzz"),  # normal behavior
            ((2,), 2, "cdcd"),  # DEFAULT-string, just like int
            ((), 1, "abab"),  # DEFAULT-pair
        ):
            self.gt = GT0(i)
            g = self.gt.value
            self.assertEqual(g, v)
            g = self.gt.string
            self.assertEqual(g, u)


# test blacklist functionality added to enable fix of bug #1680
class Test2(unittest.TestCase):
    def test_blacklist(self):
        self.gt = GT1()
        # check that MAPs have lengths reduced by blacklist
        e = len(keys) - len(BLIST)
        g = len(self.gt._E2IMAP)
        self.assertEqual(g, e)

        self.ub = GT2()
        # check that these MAPS are now un-blacklisted
        e = len(keys)
        g = len(self.ub._E2IMAP)
        self.assertEqual(g, e)


if __name__ == "__main__":
    unittest.main()
