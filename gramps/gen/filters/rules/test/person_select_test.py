#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
# Copyright (C) 2025 Doug Blank
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
Unittest that tests person-specific filter rules
"""
import unittest
import os
import sqlite3

from ....db.utils import import_as_dict
from ....const import DATA_DIR
from ....user import User
from gramps.gen.db import DbGeneric


TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")

DISCONNECTED_HANDLES = set(
    [
        "0PBKQCXHLAEIB46ZIA",
        "QEVJQC04YO01UAWJ2N",
        "UT0KQCMN7PC9XURRXJ",
        "MZAKQCKAQLIQYWP5IW",
        "Y7BKQC9CUXWQLGLPQM",
        "OBBKQC8NJM5UYBO849",
        "NPBKQCKEF0G7T4H312",
        "423KQCGLT8UISDUM1Q",
        "8S0KQCNORIWDL0X8SB",
        "AP5KQC0LBXPM727OWB",
        "AREKQC0VPBHNZ5R3IO",
        "KU0KQCJ0RUTJTIUKSA",
        "VC4KQC7L7KKH9RLHXN",
        "0P3KQCRSIVL1A4VJ19",
        "PK6KQCGEL4PTE720BL",
        "YIKKQCSD2Z85UHJ8LX",
        "KY8KQCMIH2HUUGLA3R",
        "RD7KQCQ24B1N3OEC5X",
        "NV0KQC7SIEH3SVDPP1",
        "KIKKQCU2CJ543TLM5J",
        "AT0KQC4P3MMUCHI3BK",
        "J6BKQC1PMNBAYSLM9U",
        "IXXJQCLKOUAJ5RSQY4",
        "U4ZJQC5VR0QBIE8DU",
        "F7BKQC4NXO9R7XOG2W",
        "7U0KQC6PGZBNQATNOT",
        "78AKQCI05U36T3E82O",
        "H1GKQCWOUJHFSHXABA",
        "ZWGKQCRFZAPC5PYJZ1",
        "EZ0KQCF3LSM9PRSG0K",
        "FHKKQC963NGSY18ZDZ",
        "FJ9KQCRJ3RGHNBWW4S",
        "S2EKQC9F4UR4R71IC3",
        "1XBKQCX019BKJ0M9IH",
        "Z62KQC706L0B0WTN3Q",
        "O7EKQCEVZ7FBEWMNWE",
        "XY8KQCULFPN4SR915Q",
        "WQDKQCEULSD5G9XNFI",
        "2Z0KQCSWKVFG7RPFD8",
        "26BKQC0SJIJOH02H2A",
        "262KQCH2RQKN0CBRLF",
        "P5ZJQCMKO7EYV4HFCL",
        "KXBKQC52JO3AP4GMLF",
        "9IFKQC60JTDBV57N6S",
        "TQ0KQCZ8LA7X9DIEAN",
        "BAXJQCORQA5Q46FCDG",
        "VR0KQC7LVANO83AL35",
        "75CKQC4T617U2E5T5Y",
        "LCTKQCZU3F94CEFSOM",
        "WJYJQCPNJJI5JN07SD",
        "3N6KQC6BE5EIXTRMDL",
        "CM5KQCD57I15GKLAMB",
        "cccbffffd3e69819cd8",
        "BJKKQCVDA66528PDAU",
        "QS0KQCLMIZFI8ZDLM3",
        "UW0KQCRHBIYMA8LPZD",
        "GJ7KQC7APJSAMHEK5Q",
        "711KQCDXOQWB3KDWEP",
        "PY0KQC77AJ3457A6C2",
        "WZ0KQCYVMEJHDR4MV2",
        "28EKQCQGM6NLLWFRG7",
        "E33KQCRREJALRA715H",
        "8HKKQCTEJAOBVH410L",
        "IO6KQC70PMBQUDNB3L",
        "1YBKQCWRBNB433NEMH",
        "M01KQCF7KUWCDY67JD",
        "CR0KQCOMV2QPPC90IF",
        "85ZJQCMG38N7Q2WKIK",
        "I9GKQCERACL8UZF2PY",
        "BY0KQCOZUK47R2JZDE",
        "7W0KQCYDMD4LTSY5JL",
        "A0YJQC3HONEKD1JCPK",
        "d5839c13b0541b7b8e6",
    ]
)


class BaseTest(unittest.TestCase):
    """
    Person rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict(EXAMPLE, User())

    def test_order_by_1(self):
        res = list(
            self.db.select_from_person(
                ["person.primary_name.surname_list[0].surname", "person.gender"],
                where="len(person.media_list) > 0",
                order_by=[
                    "-person.primary_name.surname_list[0].surname",
                    "person.gender",
                ],
            )
        )
        assert res == [
            ["Martel", 0],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
        ]

    def test_order_by_2(self):
        res = list(
            self.db.select_from_person(
                ["person.primary_name.surname_list[0].surname", "person.gender"],
                where="len(person.media_list) > 0",
                order_by=[
                    "person.primary_name.surname_list[0].surname",
                    "-person.gender",
                ],
            )
        )
        assert res == [
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Martel", 0],
        ]

    def test_order_by_1_generic(self):
        res = list(
            DbGeneric._select_from_table(
                self.db,
                "person",
                ["person.primary_name.surname_list[0].surname", "person.gender"],
                where="len(person.media_list) > 0",
                order_by=[
                    "-person.primary_name.surname_list[0].surname",
                    "person.gender",
                ],
            )
        )
        assert res == [
            ["Martel", 0],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
        ]

    def test_order_by_2_generic(self):
        res = list(
            DbGeneric._select_from_table(
                self.db,
                "person",
                ["person.primary_name.surname_list[0].surname", "person.gender"],
                where="len(person.media_list) > 0",
                order_by=[
                    "person.primary_name.surname_list[0].surname",
                    "-person.gender",
                ],
            )
        )
        assert res == [
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Garner", 1],
            ["Martel", 0],
        ]

    def test_HavePhotos(self):
        res = list(
            self.db.select_from_person("_.handle", where="len(person.media_list) > 0")
        )
        self.assertEqual(len(res), 5)

    def test_HavePhotos_generic(self):
        res = list(
            DbGeneric._select_from_table(
                self.db, "person", where="len(person.media_list) > 0"
            )
        )
        self.assertEqual(len(res), 5)

    def test_HasLDS(self):
        res = list(
            self.db.select_from_person(
                "_.handle",
                "len(_.lds_ord_list) > 0",
            )
        )
        self.assertEqual(len(res), 1)

    def test_HasLDS_generic(self):
        res = list(
            DbGeneric._select_from_table(
                self.db,
                "person",
                "_.handle",
                "len(_.lds_ord_list) > 0",
            )
        )
        self.assertEqual(len(res), 1)

    # def test_HasNameOriginType(self):
    #
    #    # SELECT json_data->>"$.handle", json_each.value->>"$.surname"
    #    # FROM person, json_each(json_data->>"$.primary_name.surname_list")
    #    # WHERE json_each.value->>"$.origintype.value" = 4;
    #
    #    [for surname in person.primary_name.surname_list if surname ...]

    #    rule = HasNameOriginType(["Patrilineal"])
    #    res = self.filter_with_rule(rule)
    #    self.assertEqual(len(res), 9)

    # def test_HasNameType(self):
    #
    # SELECT DISTINCT json_data->>"$.handle"
    # FROM person, json_each(json_data->>"$.alternate_names") as alternate_names
    # WHERE json_data->>"$.primary_name.type.value" = 3 or alternate_names.value->>"$.type.value" = 3;
    #
    # [name for name in person.alternate_names if name.type.value == 3] or person.primary_name.type.value == 3

    #     rule = HasNameType(["Married Name"])
    #     res = self.filter_with_rule(rule)
    #     self.assertEqual(len(res), 1)

    # def test_HasRelationship(self):
    #     rule = HasRelationship([0, "Married", 0])
    #     res = self.filter_with_rule(rule)
    #     self.assertEqual(len(res), 1377)

    # def test_HasTextMatchingRegexpOf(self):
    #     rule = HasTextMatchingRegexpOf(
    #         [".*(Dahl|Akron|Smith|Attic|" "of Lessard).*", False], use_regex=True
    #     )
    #     res = self.filter_with_rule(rule)
    #     self.assertEqual(len(res), 28)

    def test_disconnected(self):
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="len(person.family_list) == 0 and len(person.parent_family_list) == 0",
                )
            )
        )
        self.assertEqual(
            res,
            DISCONNECTED_HANDLES,
        )

    def test_disconnected_generic(self):
        res = set(
            list(
                DbGeneric._select_from_table(
                    self.db,
                    "person",
                    "person.handle",
                    where="len(person.family_list) == 0 and len(person.parent_family_list) == 0",
                )
            )
        )
        self.assertEqual(
            res,
            DISCONNECTED_HANDLES,
        )

    def test_everyone(self):
        """
        Test Everyone rule.
        """
        res = list(self.db.select_from_person())
        self.assertEqual(len(res), self.db.get_number_of_people())

    def test_everyone_generic(self):
        """
        Test Everyone rule.
        """
        res = list(DbGeneric._select_from_table(self.db, "person"))
        self.assertEqual(len(res), self.db.get_number_of_people())

    def test_hasalternatename(self):
        """
        Test HasAlternateName rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "_.handle", where="len(person.alternate_names) > 0"
                )
            )
        )
        self.assertEqual(
            res,
            set(
                [
                    "46WJQCIOLQ0KOX2XCC",
                    "GNUJQCL9MD64AM56OH",
                ]
            ),
        )

    def test_hasalternatename_generic(self):
        """
        Test HasAlternateName rule.
        """
        res = set(
            list(
                DbGeneric._select_from_table(
                    self.db,
                    "person",
                    "_.handle",
                    where="len(person.alternate_names) > 0",
                )
            )
        )
        self.assertEqual(
            res,
            set(
                [
                    "46WJQCIOLQ0KOX2XCC",
                    "GNUJQCL9MD64AM56OH",
                ]
            ),
        )

    def test_hasunknowngender(self):
        """
        Test HasUnknownGender rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gender == Person.UNKNOWN",
                )
            )
        )

        self.assertEqual(
            res,
            set(
                [
                    "OJOKQC83Y1EDBIMLJ6",
                    "8BHKQCFK9UZFRJYC2Y",
                    "PGFKQC1TUQMXFAMLMB",
                    "IHOKQCECRZYQDKW6KF",
                    "8HKKQCTEJAOBVH410L",
                    "AGFKQCO358R18LNJYV",
                    "1ENKQCBPFZTAQJSP4O",
                    "NUWKQCO7TVAOH0CHLV",
                    "P5IKQC88STY3FNTFZ3",
                    "7GXKQCMVFU8WR1LKZL",
                    "LGXKQCJ5OP6MKF9QLN",
                    "XNFKQC6DN59LACS9IU",
                    "7IOKQC1NVGUI1E55CQ",
                    "57PKQCFAWY7AM3JS4M",
                    "BNXKQCEBXC1RCOGJNF",
                    "TFFKQC1RMG8RRADKDH",
                    "FHKKQC963NGSY18ZDZ",
                    "WMXKQCDUJ4JKQQYCR7",
                    "PBHKQCHOAGTECRKT9L",
                    "OFXKQC8W0N3N6JP6YQ",
                ]
            ),
        )

    def test_hasunknowngender_generic(self):
        """
        Test HasUnknownGender rule.
        """
        res = set(
            list(
                DbGeneric._select_from_table(
                    self.db,
                    "person",
                    "person.handle",
                    where="person.gender == Person.UNKNOWN",
                )
            )
        )

        self.assertEqual(
            res,
            set(
                [
                    "OJOKQC83Y1EDBIMLJ6",
                    "8BHKQCFK9UZFRJYC2Y",
                    "PGFKQC1TUQMXFAMLMB",
                    "IHOKQCECRZYQDKW6KF",
                    "8HKKQCTEJAOBVH410L",
                    "AGFKQCO358R18LNJYV",
                    "1ENKQCBPFZTAQJSP4O",
                    "NUWKQCO7TVAOH0CHLV",
                    "P5IKQC88STY3FNTFZ3",
                    "7GXKQCMVFU8WR1LKZL",
                    "LGXKQCJ5OP6MKF9QLN",
                    "XNFKQC6DN59LACS9IU",
                    "7IOKQC1NVGUI1E55CQ",
                    "57PKQCFAWY7AM3JS4M",
                    "BNXKQCEBXC1RCOGJNF",
                    "TFFKQC1RMG8RRADKDH",
                    "FHKKQC963NGSY18ZDZ",
                    "WMXKQCDUJ4JKQQYCR7",
                    "PBHKQCHOAGTECRKT9L",
                    "OFXKQC8W0N3N6JP6YQ",
                ]
            ),
        )

    def test_hasidof_empty(self):
        """
        Test empty HasIdOf rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gramps_id == ''",
                )
            )
        )
        self.assertEqual(res, set([]))

    def test_hasidof_nonmatching(self):
        """
        Test non-matching HasIdOf rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gramps_id != 'I0000'",
                )
            )
        )
        self.assertEqual(len(res), 2127)

    def test_hasidof_irregular(self):
        """
        Test irregular HasIdOf rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gramps_id == 'ABCDEFG'",
                )
            )
        )
        self.assertEqual(res, set([]))

    def test_hasidof_matching(self):
        """
        Test matching HasIdOf rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gramps_id == 'I0044'",
                )
            )
        )
        self.assertEqual(res, set(["GNUJQCL9MD64AM56OH"]))

    def test_hasidof_startswith(self):
        """
        Test matching HasIdOf rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gramps_id.startswith('I00')",
                )
            )
        )
        self.assertEqual(len(res), 100)

    def test_isfemale(self):
        """
        Test IsFemale rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gender == Person.FEMALE",
                )
            )
        )
        # too many to list out to test explicitly
        self.assertEqual(len(res), 940)

    def test_ismale(self):
        """
        Test IsMale rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.gender == Person.MALE",
                )
            )
        )
        # too many to list out to test explicitly
        self.assertEqual(len(res), 1168)

    def test_multiplemarriages(self):
        """
        Test MultipleMarriages rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="len(person.family_list) > 1",
                )
            )
        )
        self.assertEqual(
            res,
            set(
                [
                    "R1VKQCJWNP24VN7BO",
                    "ZTVJQCTSMI85EGMXFM",
                    "ENTJQCZXQV1IRKJXUL",
                    "44WJQCLCQIPZUB0UH",
                    "SMWJQCXQ6I2GEXSPK9",
                    "DN3KQC1URTED410L3R",
                    "5FYJQC86G8EZ0L4E4B",
                    "5F4KQCJRU8ZKL6SILT",
                    "0YNKQC5U4EQGVNUZD8",
                    "YRYJQCE3RF4U8A59UB",
                    "APWKQCI6YXAXBLC33I",
                    "XSKKQC6GGKLAYANWAF",
                    "0FQKQCOQD0VRVJPTSD",
                    "B3UJQCZHDXII99AWW4",
                    "cc8205d872f532ab14e",
                    "SS1KQCWWF9488Q330U",
                    "OCYJQCS8YT7JO8KIMO",
                    "I6HKQCQF72V2N56JQ5",
                    "6YWJQC86FBVN0J6JS",
                    "KYNKQCVA6FE65ONFIQ",
                    "SHAKQCNY5IXO30GUAB",
                    "O5XKQC3V6BPJI13J24",
                    "ZN7KQC3RLB82EXF1QF",
                    "CIYJQCF3UK12DL0S2Y",
                    "H3XJQCFJ4FP4U2WGZC",
                    "cc82060504445ab6deb",
                    "4E4KQC1K4XUEX29IJO",
                    "0XVJQCJUNJY40WDSMA",
                    "1WUJQCHNH76G6YD3A",
                    "IH3KQCM1VZPRKLBLK7",
                    "242KQCBALBOD8ZK5VI",
                    "8G4KQCS6C1AOM6ZGR3",
                    "I1EKQCGGDSUD8ILUW4",
                    "X8BKQCSFF4AET5MY23",
                    "RJWJQCN1XKXRN5KMCP",
                    "ZWNKQC9DAZ3C6UHUAV",
                    "9QUJQCCSWRZNSAPCR",
                    "HI0KQCG9TGT5AAIPU",
                    "DI4KQC3S1AO27VWOLN",
                    "QBDKQCH2IU6N8IXMFE",
                    "DK2KQCJYW14VXUJ85",
                    "117KQCBB32RMTTV4G6",
                    "0QLKQCFTQMNVGCV4GM",
                    "D2OKQCGDNPT3BH4WH",
                    "CAYJQCKOL49OF7XWB3",
                    "ZQGKQCGHS67Q4IMHEG",
                    "OEXJQCQJHF2BLSAAIS",
                    "UKYJQC70LIZQ11BP89",
                    "FF2KQCRBSPCG1QY97",
                    "L6EKQCO8QYL2UO2MQO",
                ]
            ),
        )

    def test_nevermarried(self):
        """
        Test NeverMarried rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        # too many to list out to test explicitly
        self.assertEqual(len(res), 751)

    def test_peopleprivate(self):
        """
        Test PeoplePrivate rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="person.private",
                )
            )
        )
        self.assertEqual(len(res), 1)

    def test_peoplepublic(self):
        """
        Test PeoplePublic rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    "person.handle",
                    where="not person.private",
                )
            )
        )
        # too many to list out to test explicitly
        self.assertEqual(len(res), 2127)


if __name__ == "__main__":
    unittest.main()
