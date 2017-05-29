#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
# Copyright (C) 2017 Serge Noiraud
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
Unittest that tests place-specific filter rules
"""
import unittest
import os

from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory
from ....const import DATA_DIR
from ....user import User

from ..place import (
    AllPlaces, HasCitation, HasGallery, HasIdOf, RegExpIdOf, HasNote,
    HasNoteRegexp, HasReferenceCountOf, HasSourceCount, HasSourceOf,
    PlacePrivate, MatchesSourceConfidence, HasData, HasNoLatOrLon,
    InLatLonNeighborhood, ChangedSince, HasTag, HasTitle, IsEnclosedBy,
    WithinArea
    )

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericPlaceFilter = GenericFilterFactory('Place')

class BaseTest(unittest.TestCase):
    """
    Place rule tests.
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
        filter_ = GenericPlaceFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allplaces(self):
        """
        Test AllPlaces rule.
        """
        rule = AllPlaces([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_places())

    def test_hascitation(self):
        """
        Test HasCitation rule.
        """
        rule = HasCitation(['page 23', '', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['YNUJQC8YM5EGRG868J']))

    def test_hasgallery(self):
        """
        Test HasGallery rule.
        """
        rule = HasGallery(['0', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['YNUJQC8YM5EGRG868J']))

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(['P0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['c96587262e91149933fcea5f20a']))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(['P000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            'c96587262e91149933fcea5f20a', 'c96587262ff262aaac31f6db7af',
            'c96587262f24c33ab2420276737', 'c96587262e566596a225682bf53',
            'c9658726302661576894508202d', 'c96587262f8329d37b252e1b9e5',
            'c965872630664f33485fc18e75', 'c96587262fb7dbb954077cb1286',
            'c96587262f4a44183c65ff1e52', 'c96587262ed43fdb37bf04bdb7f',
            ]))

    def test_hasnote(self):
        """
        Test HasNote rule.
        """
        rule = HasNote([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasnoteregexp(self):
        """
        Test HasNoteRegexp rule.
        """
        rule = HasNoteRegexp(['.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(['greater than', '35'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'c96587262e566596a225682bf53', 'MATJQCJYH8ULRIRYTH',
            '5HTJQCSB91P69HY731', '4ECKQCWCLO5YIHXEXC',
            'c965872630a68ebd32322c4a30a']))

    def test_hassourcecount(self):
        """
        Test HasSourceCount rule.
        """
        rule = HasSourceCount(['1', 'equal to'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['YNUJQC8YM5EGRG868J']))

    def test_hassourceof(self):
        """
        Test HasSourceOf rule.
        """
        rule = HasSourceOf(['S0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['YNUJQC8YM5EGRG868J']))

    def test_placeprivate(self):
        """
        Test PlacePrivate rule.
        """
        rule = PlacePrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_matchessourceconfidence(self):
        """
        Test MatchesSourceConfidence rule.
        """
        rule = MatchesSourceConfidence(['2'])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['YNUJQC8YM5EGRG868J']))

    def test_hasdata(self):
        """
        Test HasData rule.
        """
        rule = HasData(['Albany', 'County', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set(['c9658726d602acadb74e330116a']))

    def test_hasnolatorlon(self):
        """
        Test HasNoLatOrLon rule.
        """
        rule = HasNoLatOrLon([])
        self.assertEqual(len(self.filter_with_rule(rule)), 921)

    def test_inlatlonneighborhood(self):
        """
        Test InLatLonNeighborhood rule.
        """
        rule = InLatLonNeighborhood(['30N', '90W', '2', '2'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'C6WJQC0GDYP3HZDPR3', 'N88LQCRB363ES5WJ83',
            '03EKQCC2KTNLHFLDRJ', 'M9VKQCJV91X0M12J8']))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(['2013-01-01', '2014-01-01'])
        self.assertEqual(len(self.filter_with_rule(rule)), 419)

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(['ToDo'])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hastitle(self):
        """
        Test HasTitle rule.
        """
        rule = HasTitle(['Albany'])
        self.assertEqual(self.filter_with_rule(rule), set([
            '51VJQCXUP61H9JRL66', '9XBKQCE1LZ7PMJE56G',
            'c9658726d602acadb74e330116a', 'P9MKQCT08Z3YBJV5UB']))

    def test_isenclosedby(self):
        """
        Test IsEnclosedBy rule.
        """
        rule = IsEnclosedBy(['P0001', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'EAFKQCR0ED5QWL87EO', 'S22LQCLUZM135LVKRL', 'VDUJQCFP24ZV3O4ID2',
            'V6ALQCZZFN996CO4D', 'OC6LQCXMKP6NUVYQD8', 'CUUKQC6BY5LAZXLXC6',
            'PTFKQCKPHO2VC5SYKS', 'PHUJQCJ9R4XQO5Y0WS']))

    def test_withinarea(self):
        """
        Test within area rule.
        """
        rule = WithinArea(['P1339', 100, 0])
        self.assertEqual(self.filter_with_rule(rule), set([
            'KJUJQCY580EB77WIVO', 'TLVJQC4FD2CD9OYAXU', 'TE4KQCL9FDYA4PB6VW',
            'W9GLQCSRJIQ9N2TGDF']))

    def test_isenclosedby_inclusive(self):
        """
        Test IsEnclosedBy rule with inclusive option.
        """
        rule = IsEnclosedBy(['P0001', '1'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'c96587262e91149933fcea5f20a', 'EAFKQCR0ED5QWL87EO',
            'S22LQCLUZM135LVKRL', 'VDUJQCFP24ZV3O4ID2', 'V6ALQCZZFN996CO4D',
            'OC6LQCXMKP6NUVYQD8', 'CUUKQC6BY5LAZXLXC6', 'PTFKQCKPHO2VC5SYKS',
            'PHUJQCJ9R4XQO5Y0WS']))


if __name__ == "__main__":
    unittest.main()
