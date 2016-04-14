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
Unittest that tests family-specific filter rules
"""
import unittest

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilterFactory

from gramps.gen.filters.rules.family import *

GenericFamilyFilter = GenericFilterFactory('Family')

class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = import_as_dict("example/gramps/example.gramps", User())

    def filter_with_rule(self, rule):
        filter_ = GenericFamilyFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_AllFamilies(self):
        rule = AllFamilies([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_families())

    def test_HasRelType(self):
        rule = HasRelType(['Married'])
        self.assertEqual(len(self.filter_with_rule(rule)), 738)

    def test_HasGallery(self):
        rule = HasGallery(['0', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasIdOf(self):
        rule = HasIdOf(['F0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'48TJQCGNNIR5SJRCAK']))

    def test_HasLDS(self):
        rule = HasLDS(['0', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasNote(self):
        rule = HasNote([])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_RegExpIdOf(self):
        rule = RegExpIdOf(['F000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            b'LOTJQC78O5B4WQGJRP', b'UPTJQC4VPCABZUDB75', b'NBTJQCIX49EKOCIHBP',
            b'C9UJQCF6ETBTV2MRRV', b'74UJQCKV8R4NBNHCB', b'4BTJQCL4CHNA5OUTKF',
            b'48TJQCGNNIR5SJRCAK', b'4YTJQCTEH7PQUU4AD', b'MTTJQC05LKVFFLN01A',
            ]))

    def test_HasNoteRegexp(self):
        rule = HasNoteRegexp(['.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasReferenceCountOf(self):
        rule = HasReferenceCountOf(['greater than', '12'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'29IKQCMUNFTIBV653N', b'8OUJQCUVZ0XML7BQLF', b'UPTJQC4VPCABZUDB75',
            b'9NWJQCJGLXUR3AQSFJ', b'5G2KQCGBTS86UVSRG5', b'WG2KQCSY9LEFDFQHMN',
            b'MTTJQC05LKVFFLN01A', b'C2VJQC71TNHO7RBBMX', b'QIDKQCJQ37SIUQ3UFU',
            b'DV4KQCX9OBVQ74H77F']))

    def test_HasSourceCount(self):
        rule = HasSourceCount(['1', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasSourceOf(self):
        rule = HasSourceOf(['S0001'])
        self.assertEqual(self.filter_with_rule(rule),
                        set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasCitation(self):
        rule = HasCitation(['page 10', '', '2'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_FamilyPrivate(self):
        rule = FamilyPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_HasEvent(self):
        rule = HasEvent(['Marriage', 'before 1900', 'USA', '', 'Garner'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'KSFKQCP4V0YXGM1LR9', b'8ZFKQC3FRSHACOJBOU', b'3XFKQCE7QUDJ99AVNV',
            b'OVFKQC51DX0OQUV3JB', b'9OUJQCBOHW9UEK9CNV']))

    def test_HasAttribute(self):
        rule = HasAttribute(['Number of Children', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_IsBookmarked(self):
        rule = IsBookmarked([])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_MatchesSourceConfidence(self):
        rule = MatchesSourceConfidence(['0'])
        self.assertEqual(len(self.filter_with_rule(rule)), 734)

    def test_FatherHasNameOf(self):
        rule = FatherHasNameOf(['', '', 'Dr.', '', '', '', '', '', '', '',
                                ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_FatherHasIdOf(self):
        rule = FatherHasIdOf(['I0106'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'8OUJQCUVZ0XML7BQLF']))

    def test_MotherHasNameOf(self):
        rule = MotherHasNameOf(['', 'Alvarado', '', '', '', '', '', '', '', '',
                                ''])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'EM3KQC48HFLA02TF8D', b'K9NKQCBG105ECXZ48D',
            b'2QMKQC5YWNAWZMG6VO', b'6JUJQCCAXGENRX990K']))

    def test_MotherHasIdOf(self):
        rule = MotherHasIdOf(['I0107'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'8OUJQCUVZ0XML7BQLF']))

    def test_ChildHasNameOf(self):
        rule = ChildHasNameOf(['Eugene', '', '', '', '', '', '', '', '', '',
                               ''])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'D1YJQCGLEIBPPLNL4B', b'5GTJQCXVYVAIQTBVKA', b'I42KQCM3S926FMJ91O',
            b'7CTJQCFJVBQSY076A6', b'9OUJQCBOHW9UEK9CNV', b'9IXJQCX18AHUFPQHEZ',
            b'9NWJQCJGLXUR3AQSFJ']))

    def test_ChildHasIdOf(self):
        rule = ChildHasIdOf(['I0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'48TJQCGNNIR5SJRCAK']))

    def test_ChangedSince(self):
        rule = ChangedSince(['2008-01-01', '2014-01-01'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasTag(self):
        rule = HasTag(['ToDo'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'9OUJQCBOHW9UEK9CNV']))

    def test_HasTwins(self):
        rule = HasTwins([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'SD6KQC7LB8MYGA7F5W', b'8OUJQCUVZ0XML7BQLF', b'1BVJQCNTFAGS8273LJ',
            b'5IUJQCRJY47YQ8PU7N', b'ZLUJQCPDV93OR8KHB7', b'4U2KQCBXG2VTPH6U1F',
            ]))

    def test_IsAncestorOf(self):
        rule = IsAncestorOf(['F0031', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'4AXJQC96KTN3WGPTVE', b'1RUJQCYX9QL1V45YLD', b'5GTJQCXVYVAIQTBVKA',
            b'X3WJQCSF48F6809142', b'NSVJQC89IHEEBIPDP2', b'9OUJQCBOHW9UEK9CNV',
            b'1RUJQCCL9MVRYLMTBO', b'RRVJQC5A8DDHQFPRDL', b'0SUJQCOS78AXGWP8QR',
            b'57WJQCTBJKR5QYPS6K', b'8OUJQCUVZ0XML7BQLF', b'7PUJQC4PPS4EDIVMYE'
            ]))

    def test_IsDescendantOf(self):
        rule = IsDescendantOf(['F0031', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'SFXJQCLE8PIG7PH38J', b'UCXJQCC5HS8VXDKWBM', b'IIEKQCRX89WYBHKB7R',
            b'XDXJQCMWU5EIV8XCRF', b'7BXJQCU22OCA4HN38A', b'3FXJQCR749H2H7G321',
            b'IEXJQCFUN95VENI6BO', b'4FXJQC7656WDQ3HJGW', b'FLEKQCRVG3O1UA9YUB',
            b'BCXJQC9AQ0DBXCVLEQ', b'9SEKQCAAWRUCIO7A0M', b'DDXJQCVT5X72TOXP0C',
            b'CGXJQC515QL9RLPQTU', b'XGXJQCNVZH2PWRMVAH', b'RBXJQCUYMQR2KRMDFY'
            ]))


if __name__ == "__main__":
    unittest.main()
