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
import os

from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory
from ....const import DATA_DIR
from ....user import User
from ....utils.unittest import localize_date

from ..family import (
    AllFamilies,
    HasRelType,
    HasGallery,
    HasIdOf,
    HasLDS,
    HasNote,
    RegExpIdOf,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSourceCount,
    HasSourceOf,
    HasCitation,
    FamilyPrivate,
    HasEvent,
    HasAttribute,
    IsBookmarked,
    MatchesSourceConfidence,
    FatherHasNameOf,
    FatherHasIdOf,
    MotherHasNameOf,
    MotherHasIdOf,
    ChildHasNameOf,
    ChildHasIdOf,
    ChangedSince,
    HasTag,
    HasTwins,
    IsAncestorOf,
    IsDescendantOf,
)

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericFamilyFilter = GenericFilterFactory("Family")


class BaseTest(unittest.TestCase):
    """
    Family rule tests.
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
        filter_ = GenericFamilyFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allfamilies(self):
        """
        Test AllFamilies rule.
        """
        rule = AllFamilies([])
        self.assertEqual(
            len(self.filter_with_rule(rule)), self.db.get_number_of_families()
        )

    def test_hasreltype(self):
        """
        Test HasRelType rule.
        """
        rule = HasRelType(["Married"])
        self.assertEqual(len(self.filter_with_rule(rule)), 750)

    def test_hasgallery(self):
        """
        Test HasGallery rule.
        """
        rule = HasGallery(["0", "greater than"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(["F0001"])
        self.assertEqual(self.filter_with_rule(rule), set(["48TJQCGNNIR5SJRCAK"]))

    def test_haslds(self):
        """
        Test HasLDS rule.
        """
        rule = HasLDS(["0", "greater than"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hasnote(self):
        """
        Test HasNote rule.
        """
        rule = HasNote([])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(["F000."], use_regex=True)
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "LOTJQC78O5B4WQGJRP",
                    "UPTJQC4VPCABZUDB75",
                    "NBTJQCIX49EKOCIHBP",
                    "C9UJQCF6ETBTV2MRRV",
                    "74UJQCKV8R4NBNHCB",
                    "4BTJQCL4CHNA5OUTKF",
                    "48TJQCGNNIR5SJRCAK",
                    "4YTJQCTEH7PQUU4AD",
                    "MTTJQC05LKVFFLN01A",
                    "d5839c123c034ef82ab",
                ]
            ),
        )

    def test_hasnoteregexp(self):
        """
        Test HasNoteRegexp rule.
        """
        rule = HasNoteRegexp(["."], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(["greater than", "12"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "29IKQCMUNFTIBV653N",
                    "8OUJQCUVZ0XML7BQLF",
                    "UPTJQC4VPCABZUDB75",
                    "9NWJQCJGLXUR3AQSFJ",
                    "5G2KQCGBTS86UVSRG5",
                    "WG2KQCSY9LEFDFQHMN",
                    "MTTJQC05LKVFFLN01A",
                    "C2VJQC71TNHO7RBBMX",
                    "QIDKQCJQ37SIUQ3UFU",
                    "DV4KQCX9OBVQ74H77F",
                ]
            ),
        )

    def test_hassourcecount(self):
        """
        Test HasSourceCount rule.
        """
        rule = HasSourceCount(["1", "greater than"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hassourceof(self):
        """
        Test HasSourceOf rule.
        """
        rule = HasSourceOf(["S0001"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hascitation(self):
        """
        Test HasCitation rule.
        """
        rule = HasCitation(["page 10", "", "2"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_familyprivate(self):
        """
        Test FamilyPrivate rule.
        """
        rule = FamilyPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasevent(self):
        """
        Test HasEvent rule.
        """
        date_str = localize_date("before 1900")
        rule = HasEvent(["Marriage", date_str, "USA", "", "Garner"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "KSFKQCP4V0YXGM1LR9",
                    "8ZFKQC3FRSHACOJBOU",
                    "3XFKQCE7QUDJ99AVNV",
                    "OVFKQC51DX0OQUV3JB",
                    "9OUJQCBOHW9UEK9CNV",
                ]
            ),
        )

    def test_hasattribute(self):
        """
        Test HasAttribute rule.
        """
        rule = HasAttribute(["Number of Children", ""])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_isbookmarked(self):
        """
        Test IsBookmarked rule.
        """
        rule = IsBookmarked([])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_matchessourceconfidence(self):
        """
        Test MatchesSourceConfidence rule.
        """
        rule = MatchesSourceConfidence(["0"])
        self.assertEqual(len(self.filter_with_rule(rule)), 734)

    def test_fatherhasnameof(self):
        """
        Test FatherHasNameOf rule.
        """
        rule = FatherHasNameOf(["", "", "Dr.", "", "", "", "", "", "", "", ""])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_fatherhasidof(self):
        """
        Test FatherHasIdOf rule.
        """
        rule = FatherHasIdOf(["I0106"])
        self.assertEqual(self.filter_with_rule(rule), set(["8OUJQCUVZ0XML7BQLF"]))

    def test_motherhasnameof(self):
        """
        Test MotherHasNameOf rule.
        """
        rule = MotherHasNameOf(["", "Alvarado", "", "", "", "", "", "", "", "", ""])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "EM3KQC48HFLA02TF8D",
                    "K9NKQCBG105ECXZ48D",
                    "2QMKQC5YWNAWZMG6VO",
                    "6JUJQCCAXGENRX990K",
                ]
            ),
        )

    def test_motherhasidof(self):
        """
        Test MotherHasIdOf rule.
        """
        rule = MotherHasIdOf(["I0107"])
        self.assertEqual(self.filter_with_rule(rule), set(["8OUJQCUVZ0XML7BQLF"]))

    def test_childhasnameof(self):
        """
        Test ChildHasNameOf rule.
        """
        rule = ChildHasNameOf(["Eugene", "", "", "", "", "", "", "", "", "", ""])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "D1YJQCGLEIBPPLNL4B",
                    "5GTJQCXVYVAIQTBVKA",
                    "I42KQCM3S926FMJ91O",
                    "7CTJQCFJVBQSY076A6",
                    "9OUJQCBOHW9UEK9CNV",
                    "9IXJQCX18AHUFPQHEZ",
                    "9NWJQCJGLXUR3AQSFJ",
                ]
            ),
        )

    def test_childhasidof(self):
        """
        Test ChildHasIdOf rule.
        """
        rule = ChildHasIdOf(["I0001"])
        self.assertEqual(self.filter_with_rule(rule), set(["48TJQCGNNIR5SJRCAK"]))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(["2008-01-01", "2014-01-01"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(["ToDo"])
        self.assertEqual(self.filter_with_rule(rule), set(["9OUJQCBOHW9UEK9CNV"]))

    def test_hastwins(self):
        """
        Test HasTwins rule.
        """
        rule = HasTwins([])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "SD6KQC7LB8MYGA7F5W",
                    "8OUJQCUVZ0XML7BQLF",
                    "1BVJQCNTFAGS8273LJ",
                    "5IUJQCRJY47YQ8PU7N",
                    "ZLUJQCPDV93OR8KHB7",
                    "4U2KQCBXG2VTPH6U1F",
                ]
            ),
        )

    def test_isancestorof(self):
        """
        Test IsAncestorOf rule.
        """
        rule = IsAncestorOf(["F0031", "0"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "4AXJQC96KTN3WGPTVE",
                    "1RUJQCYX9QL1V45YLD",
                    "5GTJQCXVYVAIQTBVKA",
                    "X3WJQCSF48F6809142",
                    "NSVJQC89IHEEBIPDP2",
                    "9OUJQCBOHW9UEK9CNV",
                    "1RUJQCCL9MVRYLMTBO",
                    "RRVJQC5A8DDHQFPRDL",
                    "0SUJQCOS78AXGWP8QR",
                    "57WJQCTBJKR5QYPS6K",
                    "8OUJQCUVZ0XML7BQLF",
                    "7PUJQC4PPS4EDIVMYE",
                ]
            ),
        )

    def test_isdescendantof(self):
        """
        Test IsDescendantOf rule.
        """
        rule = IsDescendantOf(["F0031", "0"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "SFXJQCLE8PIG7PH38J",
                    "UCXJQCC5HS8VXDKWBM",
                    "IIEKQCRX89WYBHKB7R",
                    "XDXJQCMWU5EIV8XCRF",
                    "7BXJQCU22OCA4HN38A",
                    "3FXJQCR749H2H7G321",
                    "IEXJQCFUN95VENI6BO",
                    "4FXJQC7656WDQ3HJGW",
                    "FLEKQCRVG3O1UA9YUB",
                    "BCXJQC9AQ0DBXCVLEQ",
                    "9SEKQCAAWRUCIO7A0M",
                    "DDXJQCVT5X72TOXP0C",
                    "CGXJQC515QL9RLPQTU",
                    "XGXJQCNVZH2PWRMVAH",
                    "RBXJQCUYMQR2KRMDFY",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
