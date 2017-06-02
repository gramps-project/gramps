#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
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

"""
Unittest that tests media-specific filter rules
"""
import unittest
import os

from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory
from ....const import DATA_DIR
from ....user import User

from ..media import (
    AllMedia, HasIdOf, RegExpIdOf, HasCitation, HasNoteRegexp,
    HasNoteMatchingSubstringOf, HasReferenceCountOf, HasSourceCount,
    HasSourceOf, MediaPrivate, MatchesSourceConfidence, HasMedia,
    HasAttribute, ChangedSince, HasTag)

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericMediaFilter = GenericFilterFactory('Media')

class BaseTest(unittest.TestCase):
    """
    Media rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict(EXAMPLE, User())

    def filter_with_rule(self, rule):
        """
        Apply a filter with the given rule.
        """
        filter_ = GenericMediaFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allmedia(self):
        """
        Test AllMedia rule.
        """
        rule = AllMedia([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_media())

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(['O0000'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['b39fe1cfc1305ac4a21']))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(['O000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            'F0QIGQFT275JFJ75E8', '78V2GQX2FKNSYQ3OHE',
            'b39fe1cfc1305ac4a21', 'F8JYGQFL2PKLSYH79X',
            'B1AUFQV7H8R9NR4SZM']))

    def test_hascitation(self):
        """
        Test HasCitation rule.
        """
        rule = HasCitation(['page 21', '', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['B1AUFQV7H8R9NR4SZM']))

    def test_hasnoteregexp(self):
        """
        Test HasNoteRegexp rule.
        """
        rule = HasNoteRegexp(['.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasnotematchingsubstringof(self):
        """
        Test HasNoteMatchingSubstringOf rule.
        """
        rule = HasNoteMatchingSubstringOf(['some text'])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(['greater than', '1'])
        self.assertEqual(self.filter_with_rule(rule), set([
            '238CGQ939HG18SS5MG', 'b39fe1cfc1305ac4a21']))

    def test_hassourcecount(self):
        """
        Test HasSourceCount rule.
        """
        rule = HasSourceCount(['1', 'equal to'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['B1AUFQV7H8R9NR4SZM']))

    def test_hassourceof(self):
        """
        Test HasSourceOf rule.
        """
        rule = HasSourceOf(['S0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['B1AUFQV7H8R9NR4SZM']))

    def test_mediaprivate(self):
        """
        Test MediaPrivate rule.
        """
        rule = MediaPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_matchessourceconfidence(self):
        """
        Test MatchesSourceConfidence rule.
        """
        rule = MatchesSourceConfidence(['2'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['B1AUFQV7H8R9NR4SZM']))

    def test_hasmedia(self):
        """
        Test HasMedia rule.
        """
        rule = HasMedia(['mannschaft', 'image/jpeg', '.jpg', '1897'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['238CGQ939HG18SS5MG']))

    def test_hasattribute(self):
        """
        Test HasAttribute rule.
        """
        rule = HasAttribute(['Description', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['B1AUFQV7H8R9NR4SZM']))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(['2010-01-01', '2016-01-01'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'b39fe1cfc1305ac4a21', 'B1AUFQV7H8R9NR4SZM',
            '238CGQ939HG18SS5MG', 'F0QIGQFT275JFJ75E8']))

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(['ToDo'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['238CGQ939HG18SS5MG']))


if __name__ == "__main__":
    unittest.main()
