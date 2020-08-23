#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017  Paul Culley
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

""" unittest for styledtext """

import unittest
from copy import deepcopy
from ..styledtext import StyledText
from ..styledtexttag import StyledTextTag
from ..styledtexttagtype import StyledTextTagType


class Test1(unittest.TestCase):
    T1 = StyledTextTag(StyledTextTagType(1), 'v1', [(0, 2), (2, 4), (4, 6)])
    T2 = StyledTextTag(StyledTextTagType(2), 'v2', [(1, 3), (3, 5), (0, 7)])
    T3 = StyledTextTag(StyledTextTagType(0), 'v3', [(0, 1)])
    T4 = StyledTextTag(StyledTextTagType(2), 'v2',
                       [(8, 10), (10, 12), (7, 14)])
    T5 = StyledTextTag(StyledTextTagType(2), 'v2',
                       [(19, 21), (21, 23), (18, 25)])

    A = StyledText('123X456', [T1])
    B = StyledText("abcXdef", [T2])

    C = StyledText('\n')

    S = 'cleartext'

    # some basic tests
    # because the StyledText.__eq__ method doesn't work very well (tags don't
    # compare when they are equivalent, but not equal) we have to use
    # serialize for comparisons.
    def test_join(self):
        C = self.C.join([self.A, self.S, deepcopy(self.B)])
        _C = StyledText('123X456\ncleartext\nabcXdef', [self.T1, self.T5])
        self.assertEqual(C.serialize(), _C.serialize())

    def test_split(self):
        C = self.C.join([self.A, self.S, deepcopy(self.B)])
        L = C.split()
        _L = [self.A, self.S, self.B]
        self.assertEqual(L[0].serialize(), self.A.serialize())
        self.assertEqual(str(L[1]), self.S)
        self.assertEqual(L[2].serialize(), self.B.serialize())

    def test_replace(self):
        C = self.C.join([self.A, self.S, deepcopy(self.B)])
        C = C.replace('X', StyledText('_', [self.T3]))
        _C = ('123_456\ncleartext\nabc_def',
              [((0, ''), 'v3', [(3, 4)]),
               ((0, ''), 'v3', [(21, 22)]),
               ((1, ''), 'v1', [(0, 2), (2, 3)]),
               ((1, ''), 'v1', [(4, 6)]),
               ((2, ''), 'v2', [(19, 21), (18, 21)]),
               ((2, ''), 'v2', [(22, 23), (22, 25)])])
        self.assertEqual(C.serialize(), _C)

    def test_add(self):
        A = deepcopy(self.A) + deepcopy(self.B)
        _A = StyledText('123X456abcXdef', [self.T1, self.T4])
        self.assertEqual(A.serialize(), _A.serialize())


if __name__ == "__main__":
    unittest.main()
