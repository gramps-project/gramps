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
Unittest that tests place-specific filter rules
"""
import unittest

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilterFactory

from gramps.gen.filters.rules.place import (
    AllPlaces, HasCitation, HasGallery, HasIdOf, RegExpIdOf, HasNote,
    HasNoteRegexp, HasReferenceCountOf, HasSourceCount, HasSourceOf,
    PlacePrivate, MatchesSourceConfidence, HasData, HasNoLatOrLon,
    InLatLonNeighborhood, ChangedSince, HasTag, HasTitle, IsEnclosedBy)

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
        cls.db = import_as_dict("example/gramps/example.gramps", User())

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
                         set([b'YNUJQC8YM5EGRG868J']))

    def test_hasgallery(self):
        """
        Test HasGallery rule.
        """
        rule = HasGallery(['0', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'YNUJQC8YM5EGRG868J']))

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(['P0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'c96587262e91149933fcea5f20a']))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(['P000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            b'c96587262e91149933fcea5f20a', b'c96587262ff262aaac31f6db7af',
            b'c96587262f24c33ab2420276737', b'c96587262e566596a225682bf53',
            b'c9658726302661576894508202d', b'c96587262f8329d37b252e1b9e5',
            b'c965872630664f33485fc18e75', b'c96587262fb7dbb954077cb1286',
            b'c96587262f4a44183c65ff1e52', b'c96587262ed43fdb37bf04bdb7f',
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
            b'c96587262e566596a225682bf53', b'MATJQCJYH8ULRIRYTH',
            b'5HTJQCSB91P69HY731', b'4ECKQCWCLO5YIHXEXC',
            b'c965872630a68ebd32322c4a30a']))

    def test_hassourcecount(self):
        """
        Test HasSourceCount rule.
        """
        rule = HasSourceCount(['1', 'equal to'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'YNUJQC8YM5EGRG868J']))

    def test_hassourceof(self):
        """
        Test HasSourceOf rule.
        """
        rule = HasSourceOf(['S0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'YNUJQC8YM5EGRG868J']))

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
                         set([b'YNUJQC8YM5EGRG868J']))

    def test_hasdata(self):
        """
        Test HasData rule.
        """
        rule = HasData(['Albany', 'County', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'c9658726d602acadb74e330116a']))

    def test_hasnolatorlon(self):
        """
        Test HasNoLatOrLon rule.
        """
        rule = HasNoLatOrLon([])
        self.assertEqual(len(self.filter_with_rule(rule)), 915)

    def test_inlatlonneighborhood(self):
        """
        Test InLatLonNeighborhood rule.
        """
        rule = InLatLonNeighborhood(['30N', '90W', '2', '2'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'C6WJQC0GDYP3HZDPR3', b'N88LQCRB363ES5WJ83',
            b'03EKQCC2KTNLHFLDRJ', b'M9VKQCJV91X0M12J8']))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(['2013-01-01', '2014-01-01'])
        self.assertEqual(len(self.filter_with_rule(rule)), 435)

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
            b'51VJQCXUP61H9JRL66', b'9XBKQCE1LZ7PMJE56G',
            b'c9658726d602acadb74e330116a', b'P9MKQCT08Z3YBJV5UB']))

    def test_isenclosedby(self):
        """
        Test IsEnclosedBy rule.
        """
        rule = IsEnclosedBy(['P0001', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'EAFKQCR0ED5QWL87EO', b'S22LQCLUZM135LVKRL', b'VDUJQCFP24ZV3O4ID2',
            b'V6ALQCZZFN996CO4D', b'OC6LQCXMKP6NUVYQD8', b'CUUKQC6BY5LAZXLXC6',
            b'PTFKQCKPHO2VC5SYKS', b'PHUJQCJ9R4XQO5Y0WS']))

    def test_isenclosedby_inclusive(self):
        """
        Test IsEnclosedBy rule with inclusive option.
        """
        rule = IsEnclosedBy(['P0001', '1'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'c96587262e91149933fcea5f20a', b'EAFKQCR0ED5QWL87EO',
            b'S22LQCLUZM135LVKRL', b'VDUJQCFP24ZV3O4ID2', b'V6ALQCZZFN996CO4D',
            b'OC6LQCXMKP6NUVYQD8', b'CUUKQC6BY5LAZXLXC6', b'PTFKQCKPHO2VC5SYKS',
            b'PHUJQCJ9R4XQO5Y0WS']))


if __name__ == "__main__":
    unittest.main()
