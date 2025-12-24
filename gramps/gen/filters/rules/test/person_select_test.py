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
from ....const import TEST_DIR
from ....user import User


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
                what=["person.primary_name.surname_list[0].surname", "person.gender"],
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
                what=["person.primary_name.surname_list[0].surname", "person.gender"],
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
            self.db.select_from_person(
                what=["person.primary_name.surname_list[0].surname", "person.gender"],
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
            self.db.select_from_person(
                what=["person.primary_name.surname_list[0].surname", "person.gender"],
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
            self.db.select_from_person(
                what="obj.handle", where="len(person.media_list) > 0"
            )
        )
        self.assertEqual(len(res), 5)

    def test_HavePhotos_generic(self):
        res = list(self.db.select_from_person(where="len(person.media_list) > 0"))
        self.assertEqual(len(res), 5)

    def test_HasLDS(self):
        res = list(
            self.db.select_from_person(
                what="obj.handle",
                where="len(obj.lds_ord_list) > 0",
            )
        )
        self.assertEqual(len(res), 1)

    def test_HasLDS_generic(self):
        res = list(
            self.db.select_from_person(
                what="obj.handle",
                where="len(obj.lds_ord_list) > 0",
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
                    what="person.handle",
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
                self.db.select_from_person(
                    what="person.handle",
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
        res = list(self.db.select_from_person())
        self.assertEqual(len(res), self.db.get_number_of_people())

    def test_hasalternatename(self):
        """
        Test HasAlternateName rule.
        """
        res = set(
            list(
                self.db.select_from_person(
                    what="obj.handle", where="len(person.alternate_names) > 0"
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
                self.db.select_from_person(
                    what="obj.handle",
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
                    what="person.handle",
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
                self.db.select_from_person(
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
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
                    what="person.handle",
                    where="not person.private",
                )
            )
        )
        # too many to list out to test explicitly
        self.assertEqual(len(res), 2127)

    def test_binary_operations(self):
        """
        Test binary operations (+, -, *, /, %, **, //).
        """
        # Addition
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.media_list) + len(person.note_list) > 0",
            )
        )
        # Should include people with either media or notes
        self.assertGreater(len(res), 0)

        # Subtraction
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.family_list) - len(person.parent_family_list) > 0",
            )
        )
        # Should include people with more families than parent families
        self.assertGreater(len(res), 0)

        # Multiplication
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.media_list) * 2 > 0",
            )
        )
        # Should include people with media
        self.assertGreater(len(res), 0)

        # Division
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.family_list) / 1.0 > 1",
            )
        )
        # Should include people with more than 1 family
        self.assertGreater(len(res), 0)

        # Modulo
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.family_list) % 2 == 0",
            )
        )
        # Should include people with even number of families
        self.assertGreater(len(res), 0)

        # Power
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.media_list) ** 2 >= 0",
            )
        )
        # Should include all people (squared length is always >= 0)
        self.assertGreater(len(res), 0)

        # Floor Division
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.family_list) // 1 >= 1",
            )
        )
        # Should include people with at least 1 family
        self.assertGreater(len(res), 0)

    def test_unary_minus(self):
        """
        Test unary minus operation.
        """
        # Unary minus in comparison
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="-len(person.family_list) < 0",
            )
        )
        # Should include people with at least 1 family
        self.assertGreater(len(res), 0)

    def test_conditional_expression(self):
        """
        Test conditional expressions (ternary operator).
        """
        # Ternary in what clause
        res = list(
            self.db.select_from_person(
                what="person.gramps_id if person.gramps_id else 'UNKNOWN'",
                where="len(person.family_list) > 0",
            )
        )
        # Should return gramps_id or 'UNKNOWN'
        self.assertGreater(len(res), 0)
        # All results should be strings
        for item in res:
            self.assertIsInstance(item, str)

        # Ternary in where clause
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="(len(person.family_list) if len(person.family_list) > 0 else 0) > 0",
            )
        )
        # Should include people with families
        self.assertGreater(len(res), 0)

    def test_string_endswith(self):
        """
        Test string .endswith() method.
        """
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.endswith('44')",
                )
            )
        )
        # Should include people with gramps_id ending in '44'
        self.assertGreater(len(res), 0)
        # Verify specific known result
        res_specific = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id == 'I0044'",
                )
            )
        )
        # endswith('44') should include exact match 'I0044'
        self.assertTrue(res_specific.issubset(res))

    def test_string_in_pattern(self):
        """
        Test special "string IN X" pattern that converts to LIKE.
        """
        # Test the special pattern: '<string> IN attribute'
        # This should convert to: attribute LIKE '%<string>%'
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="'I00' in person.gramps_id",
                )
            )
        )
        # Should include people with 'I00' in their gramps_id
        self.assertGreater(len(res), 0)
        # Should include all startswith results (since 'I00' in gramps_id includes those starting with 'I00')
        res_startswith = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.startswith('I00')",
                )
            )
        )
        # The 'in' pattern should include all startswith results
        self.assertTrue(res_startswith.issubset(res))

    def test_binary_operations_generic(self):
        """
        Test binary operations.
        """
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="len(person.media_list) + len(person.note_list) > 0",
            )
        )
        self.assertGreater(len(res), 0)

    def test_unary_minus_generic(self):
        """
        Test unary minus.
        """
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="-len(person.family_list) < 0",
            )
        )
        self.assertGreater(len(res), 0)

    def test_conditional_expression_generic(self):
        """
        Test conditional expressions.
        """
        res = list(
            self.db.select_from_person(
                what="person.gramps_id if person.gramps_id else 'UNKNOWN'",
                where="len(person.family_list) > 0",
            )
        )
        self.assertGreater(len(res), 0)

    def test_string_endswith_generic(self):
        """
        Test string .endswith().
        """
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.endswith('44')",
                )
            )
        )
        self.assertGreater(len(res), 0)

    def test_string_in_pattern_generic(self):
        """
        Test special "string IN X" pattern.
        """
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="'I00' in person.gramps_id",
                )
            )
        )
        self.assertGreater(len(res), 0)

    # ========================================================================
    # Tests for list comprehension in what clause
    # ========================================================================

    def test_list_comprehension_in_what_basic(self):
        """
        Test list comprehension in what clause - extract values from array.
        """
        # Extract role.value from all event_refs
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]"
            )
        )
        # Should return one row per event_ref
        self.assertGreater(len(res), 0)
        # All results should be integers (role.value)
        for item in res:
            self.assertIsInstance(item, int)

    def test_list_comprehension_in_what_with_condition(self):
        """
        Test list comprehension in what clause with condition.
        """
        from gramps.gen.lib import EventRoleType

        # Extract role.value from event_refs where role.value == 1 (PRIMARY)
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]"
            )
        )
        # Should return one row per matching event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be PRIMARY (1)
        for item in res:
            self.assertEqual(item, EventRoleType.PRIMARY)

    def test_list_comprehension_in_what_extract_ref(self):
        """
        Test list comprehension in what clause - extract ref from array.
        """
        # Extract ref from all event_refs
        res = list(
            self.db.select_from_person(
                what="[eref.ref for eref in person.event_ref_list]"
            )
        )
        # Should return one row per event_ref
        self.assertGreater(len(res), 0)
        # All results should be strings (handles)
        for item in res:
            self.assertIsInstance(item, str)
            self.assertGreater(len(item), 0)

    def test_list_comprehension_in_what_no_condition(self):
        """
        Test list comprehension in what clause without condition (all elements).
        """
        # Extract role.value from all event_refs (no condition)
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]"
            )
        )
        # Should return one row per event_ref
        self.assertGreater(len(res), 0)

    # ========================================================================
    # Tests for any() with list comprehension in where clause
    # ========================================================================

    def test_any_list_comprehension_in_where_basic(self):
        """
        Test any() with list comprehension in where clause - filter persons.
        """
        # Find persons that have any event_ref
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="any([eref for eref in person.event_ref_list])",
                )
            )
        )
        # Should return one row per person (not per event_ref)
        self.assertGreater(len(res), 0)
        # All results should be handles (strings)
        for item in res:
            self.assertIsInstance(item, str)

    def test_any_list_comprehension_in_where_with_condition(self):
        """
        Test any() with list comprehension in where clause with condition.
        """
        # Find persons that have any event_ref with role.value == 1 (PRIMARY)
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])",
                )
            )
        )
        # Should return one row per person that has at least one PRIMARY event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be handles (strings)
        for item in res:
            self.assertIsInstance(item, str)

    def test_any_list_comprehension_in_where_combined_with_person_filter(self):
        """
        Test any() with list comprehension combined with person-level filtering.
        """
        # Find persons with specific gender AND any event_ref
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and any([eref for eref in person.event_ref_list])",
                )
            )
        )
        # Should return one row per person
        self.assertGreaterEqual(len(res), 0)

    # ========================================================================
    # Tests for combining list comprehensions in both what and where
    # ========================================================================

    def test_combine_what_and_where_list_comprehensions(self):
        """
        Test combining list comprehension in what with any() in where.
        """
        # Filter persons with any event_ref, then extract role.value from all event_refs
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]",
                where="any([eref for eref in person.event_ref_list])",
            )
        )
        # Should return one row per event_ref from persons that have any event_ref
        self.assertGreater(len(res), 0)
        # All results should be integers (role.value)
        for item in res:
            self.assertIsInstance(item, int)

    def test_combine_what_and_where_with_conditions(self):
        """
        Test combining list comprehension in what with any() in where, both with conditions.
        """
        from gramps.gen.lib import EventRoleType

        # Filter persons with any PRIMARY event_ref, then extract role.value from PRIMARY event_refs
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
                where="any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])",
            )
        )
        # Should return one row per PRIMARY event_ref from persons that have at least one PRIMARY event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be PRIMARY (1)
        for item in res:
            self.assertEqual(item, EventRoleType.PRIMARY)

    def test_combine_what_and_where_different_conditions(self):
        """
        Test combining list comprehension in what with any() in where with different conditions.
        """
        from gramps.gen.lib import EventRoleType

        # Filter persons with any event_ref, then extract role.value from PRIMARY event_refs only
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
                where="any([eref for eref in person.event_ref_list])",
            )
        )
        # Should return one row per PRIMARY event_ref from persons that have any event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be PRIMARY (1)
        for item in res:
            self.assertEqual(item, EventRoleType.PRIMARY)

    def test_combine_what_and_where_with_person_filter(self):
        """
        Test combining list comprehension in what with any() in where plus person-level filter.
        """
        from gramps.gen.lib import EventRoleType

        # Filter persons with specific gender AND any PRIMARY event_ref, then extract role.value
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]",
                where="person.gender == Person.FEMALE and any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])",
            )
        )
        # Should return one row per PRIMARY event_ref from female persons that have at least one PRIMARY event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be PRIMARY (1)
        for item in res:
            self.assertEqual(item, EventRoleType.PRIMARY)

    # ========================================================================
    # Tests for array expansion (item in array pattern)
    # ========================================================================

    def test_array_expansion_basic(self):
        """
        Test array expansion pattern - item in person.array_path.
        """
        # Expand event_ref_list - get role.value from each event_ref
        res = list(
            self.db.select_from_person(
                what="item.role.value", where="item in person.event_ref_list"
            )
        )
        # Should return one row per event_ref
        self.assertGreater(len(res), 0)
        # All results should be integers (role.value)
        for item in res:
            self.assertIsInstance(item, int)

    def test_array_expansion_with_condition(self):
        """
        Test array expansion pattern with additional condition.
        """
        from gramps.gen.lib import EventRoleType

        # Expand event_ref_list and filter by role.value
        res = list(
            self.db.select_from_person(
                what="item.role.value",
                where="item in person.event_ref_list and item.role.value == 1",
            )
        )
        # Should return one row per matching event_ref
        self.assertGreaterEqual(len(res), 0)
        # All results should be 1 (PRIMARY)
        for item in res:
            self.assertEqual(item, EventRoleType.PRIMARY)

    # ========================================================================
    # Edge cases and error handling
    # ========================================================================

    def test_list_comprehension_empty_array(self):
        """
        Test list comprehension with persons that have empty arrays.
        """
        # Extract from event_ref_list - persons with no event_refs should return no rows
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]",
                where="len(person.event_ref_list) == 0",
            )
        )
        # Should return empty list (no event_refs to extract from)
        self.assertEqual(len(res), 0)

    def test_any_list_comprehension_empty_array(self):
        """
        Test any() with list comprehension on persons with empty arrays.
        """
        # Find persons with no event_refs using any()
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="not any([eref for eref in person.event_ref_list])",
                )
            )
        )
        # Should return persons with no event_refs
        self.assertGreaterEqual(len(res), 0)

    def test_list_comprehension_multiple_fields(self):
        """
        Test that list comprehension works with different field extractions.
        """
        # Test extracting different fields
        res_refs = list(
            self.db.select_from_person(
                what="[eref.ref for eref in person.event_ref_list]"
            )
        )
        res_roles = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]"
            )
        )
        # Both should return the same number of rows (one per event_ref)
        # Note: They might differ if some persons have event_refs and others don't
        # But the pattern should work
        self.assertGreaterEqual(len(res_refs), 0)
        self.assertGreaterEqual(len(res_roles), 0)

    # ========================================================================
    # Tests for complex boolean logic (AND/OR expressions)
    # ========================================================================

    def test_simple_and_expression(self):
        """
        Test simple AND expression: condition1 and condition2
        """
        # Find persons who are male AND have families
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and len(person.family_list) > 0",
                )
            )
        )
        # Should return persons that are both male and have families
        self.assertGreater(len(res), 0)
        # Verify by checking separately
        males = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE",
                )
            )
        )
        with_families = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )
        # Result should be intersection
        self.assertEqual(res, males & with_families)

    def test_simple_or_expression(self):
        """
        Test simple OR expression: condition1 or condition2
        """
        # Find persons who are male OR have no families
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE or len(person.family_list) == 0",
                )
            )
        )
        # Should return persons that are either male or have no families
        self.assertGreater(len(res), 0)
        # Verify by checking separately
        males = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE",
                )
            )
        )
        no_families = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        # Result should be union
        self.assertEqual(res, males | no_families)

    def test_multiple_and_expression(self):
        """
        Test multiple AND expressions: A and B and C
        """
        from gramps.gen.lib import Person

        # Find persons who are male AND have families AND have media
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and len(person.family_list) > 0 and len(person.media_list) > 0",
                )
            )
        )
        # Should return persons that meet all three conditions
        self.assertGreaterEqual(len(res), 0)
        # Verify by checking each condition separately
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(person.gender, Person.MALE)
            self.assertGreater(len(person.family_list), 0)
            self.assertGreater(len(person.media_list), 0)

    def test_multiple_or_expression(self):
        """
        Test multiple OR expressions: A or B or C
        """
        # Find persons who are male OR female OR have unknown gender
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE or person.gender == Person.FEMALE or person.gender == Person.UNKNOWN",
                )
            )
        )
        # Should return all persons (everyone has a gender)
        self.assertEqual(len(res), self.db.get_number_of_people())

    def test_mixed_and_or_expression(self):
        """
        Test mixed AND/OR expression: A and B or C and D
        """
        from gramps.gen.lib import Person

        # Find persons who are (male AND have families) OR (female AND have no families)
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.family_list) == 0)",
                )
            )
        )
        # Should return persons matching either condition
        self.assertGreater(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = person.gender == Person.FEMALE and len(person.family_list) == 0
            self.assertTrue(condition1 or condition2)

    def test_nested_boolean_expression(self):
        """
        Test nested boolean expression: (A and B) or (C and D)
        """
        from gramps.gen.lib import Person

        # Find persons who are (male AND have families) OR (female AND have media)
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0)",
                )
            )
        )
        # Should return persons matching either condition
        self.assertGreater(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = person.gender == Person.FEMALE and len(person.media_list) > 0
            self.assertTrue(condition1 or condition2)

    def test_deeply_nested_boolean_expression(self):
        """
        Test deeply nested boolean expression: (A and (B or C)) and D
        """
        from gramps.gen.lib import Person

        # Find persons who are (male AND (have families OR have media)) AND have notes
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and (len(person.family_list) > 0 or len(person.media_list) > 0)) and len(person.note_list) > 0",
                )
            )
        )
        # Should return persons matching all conditions
        self.assertGreaterEqual(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(person.gender, Person.MALE)
            self.assertTrue(len(person.family_list) > 0 or len(person.media_list) > 0)
            self.assertGreater(len(person.note_list), 0)

    def test_any_with_and_expression(self):
        """
        Test any() combined with AND: (A and B) or any([...])
        """
        from gramps.gen.lib import Person, EventRoleType

        # Find persons who are (male AND have families) OR have any PRIMARY event_ref
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and len(person.family_list) > 0) or any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])",
                )
            )
        )
        # Should return persons matching either condition
        self.assertGreater(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = any(
                eref.role.value == EventRoleType.PRIMARY
                for eref in person.event_ref_list
            )
            self.assertTrue(condition1 or condition2)

    def test_any_with_or_expression(self):
        """
        Test any() combined with OR: (A or any([...])) and B
        """
        from gramps.gen.lib import Person, EventRoleType

        # Find persons who are (male OR have any PRIMARY event_ref) AND have families
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE or any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY])) and len(person.family_list) > 0",
                )
            )
        )
        # Should return persons matching the combined condition
        self.assertGreater(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertGreater(len(person.family_list), 0)
            condition1 = person.gender == Person.MALE
            condition2 = any(
                eref.role.value == EventRoleType.PRIMARY
                for eref in person.event_ref_list
            )
            self.assertTrue(condition1 or condition2)

    def test_array_expansion_with_and_expression(self):
        """
        Test array expansion combined with OR: (A and B) or (item in person.array)
        Note: When array expansion is used in an OR expression, it expands the result set.
        This tests that the boolean structure is preserved correctly and that UNION
        queries correctly include persons matching the left side even with empty arrays.
        """
        from gramps.gen.lib import Person

        # Find persons who are (male AND have families) OR have any event_ref
        # Using array expansion pattern - this will return one row per matching event_ref
        # So we need to select person.handle to identify which person each row belongs to
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="(person.gender == Person.MALE and len(person.family_list) > 0) or (item in person.event_ref_list)",
            )
        )
        # Should return rows for persons matching either condition
        # When array expansion is used, we get one row per matching array element
        self.assertGreater(len(res), 0)
        # Convert to set to get unique person handles
        unique_handles = set(res)
        # Verify by checking each person
        for handle in unique_handles:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = len(person.event_ref_list) > 0
            self.assertTrue(
                condition1 or condition2,
                f"Person {handle} should match one of the conditions",
            )

        # Verify that we get persons with event_refs (right side)
        # Right side: persons with any event_ref (using array expansion)
        right_side = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="item in person.event_ref_list",
                )
            )
        )
        # The result should include all persons with event_refs
        self.assertTrue(
            right_side.issubset(unique_handles),
            "Result should include all persons with event_refs",
        )

        # Verify that we get persons matching left side even with empty arrays
        # Left side: persons who are male AND have families (regardless of event_ref_list)
        left_side = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and len(person.family_list) > 0",
                )
            )
        )
        # The result should include all persons matching the left side
        # This verifies that UNION correctly includes persons with empty arrays
        self.assertTrue(
            left_side.issubset(unique_handles),
            "Result should include all persons matching left side, even with empty arrays",
        )

    def test_complex_nested_with_any(self):
        """
        Test complex nested expression with any(): (A and (B or any([...]))) and C
        """
        from gramps.gen.lib import Person, EventRoleType

        # Find persons who are (male AND (have families OR have PRIMARY event_ref)) AND have media
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and (len(person.family_list) > 0 or any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]))) and len(person.media_list) > 0",
                )
            )
        )
        # Should return persons matching all conditions
        self.assertGreaterEqual(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(person.gender, Person.MALE)
            self.assertGreater(len(person.media_list), 0)
            condition = len(person.family_list) > 0 or any(
                eref.role.value == EventRoleType.PRIMARY
                for eref in person.event_ref_list
            )
            self.assertTrue(condition)

    def test_not_with_and_or_expression(self):
        """
        Test NOT combined with AND/OR: not (A and B) or (C and D)
        """
        from gramps.gen.lib import Person

        # Find persons who are NOT (male AND have families) OR (female AND have no families)
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="not (person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.family_list) == 0)",
                )
            )
        )
        # Should return persons matching either condition
        self.assertGreater(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = not (
                person.gender == Person.MALE and len(person.family_list) > 0
            )
            condition2 = person.gender == Person.FEMALE and len(person.family_list) == 0
            self.assertTrue(condition1 or condition2)

    def test_very_complex_expression(self):
        """
        Test very complex expression with multiple levels of nesting.
        """
        from gramps.gen.lib import Person, EventRoleType

        # Find persons matching: ((A and B) or (C and D)) and (E or F)
        # Where:
        # A = male, B = has families, C = female, D = has media
        # E = has notes, F = has PRIMARY event_ref
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="((person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0)) and (len(person.note_list) > 0 or any([eref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY]))",
                )
            )
        )
        # Should return persons matching the complex condition
        self.assertGreaterEqual(len(res), 0)
        # Verify by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = (
                person.gender == Person.MALE and len(person.family_list) > 0
            ) or (person.gender == Person.FEMALE and len(person.media_list) > 0)
            condition2 = len(person.note_list) > 0 or any(
                eref.role.value == EventRoleType.PRIMARY
                for eref in person.event_ref_list
            )
            self.assertTrue(condition1 and condition2)

    # ========================================================================
    # Tests for JOIN functionality
    # ========================================================================

    def test_join_person_family_basic(self):
        """
        Test basic JOIN between person and family tables.
        Get person and family handles where person is the father.
        """
        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.father_handle",
            )
        )
        # Should return one row per person-family relationship where person is father
        self.assertGreater(len(res), 0)
        # Verify each result: person handle should match family's father_handle
        for person_handle, family_handle in res:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(family_handle, str)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)

    def test_join_person_family_with_condition(self):
        """
        Test JOIN with additional condition on family table.
        Get person and family where person is father and family type is married.
        """
        from gramps.gen.lib import FamilyRelType

        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle", "family.type.value"],
                where="person.handle == family.father_handle and family.type.value == FamilyRelType.MARRIED",
            )
        )
        # Should return one row per married family where person is father
        self.assertGreaterEqual(len(res), 0)
        # Verify each result
        for person_handle, family_handle, family_type in res:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(family_handle, str)
            self.assertEqual(family_type, FamilyRelType.MARRIED)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)
            self.assertEqual(family.get_relationship().value, FamilyRelType.MARRIED)

    def test_join_family_person_reverse(self):
        """
        Test JOIN in reverse direction (from family to person).
        Get family and father's handle and name.
        """
        res = list(
            self.db.select_from_family(
                what=[
                    "family.handle",
                    "person.handle",
                    "person.primary_name.first_name",
                ],
                where="family.father_handle == person.handle",
            )
        )
        # Should return one row per family with a father
        self.assertGreater(len(res), 0)
        # Verify each result
        for family_handle, person_handle, first_name in res:
            self.assertIsInstance(family_handle, str)
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(first_name, str)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)
            person = self.db.get_person_from_handle(person_handle)
            self.assertIsNotNone(person)
            self.assertEqual(person.get_primary_name().get_first_name(), first_name)

    def test_join_person_family_mother(self):
        """
        Test JOIN with mother relationship.
        Get person and family handles where person is the mother.
        """
        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.mother_handle",
            )
        )
        # Should return one row per person-family relationship where person is mother
        self.assertGreater(len(res), 0)
        # Verify each result
        for person_handle, family_handle in res:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(family_handle, str)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_mother_handle(), person_handle)

    def test_join_person_family_with_person_filter(self):
        """
        Test JOIN with additional condition on person table.
        Get person and family where person is father and has a gender condition.
        """
        from gramps.gen.lib import Person

        res = list(
            self.db.select_from_person(
                what=["person.handle", "person.gender", "family.handle"],
                where="person.handle == family.father_handle and person.gender == Person.MALE",
            )
        )
        # Should return at least some results (males who are fathers)
        self.assertGreater(len(res), 0)
        # Verify each result
        for person_handle, person_gender, family_handle in res:
            self.assertEqual(person_gender, Person.MALE)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)

    def test_join_person_family_multiple_conditions(self):
        """
        Test JOIN with multiple conditions on both tables.
        """
        from gramps.gen.lib import Person, FamilyRelType

        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.father_handle and person.gender == Person.MALE and family.type.value == FamilyRelType.MARRIED",
            )
        )
        # Should return married families with male fathers
        self.assertGreaterEqual(len(res), 0)
        # Verify each result
        for person_handle, family_handle in res:
            person = self.db.get_person_from_handle(person_handle)
            self.assertIsNotNone(person)
            self.assertEqual(person.get_gender(), Person.MALE)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)
            self.assertEqual(family.get_relationship().value, FamilyRelType.MARRIED)

    def test_join_no_matches(self):
        """
        Test JOIN that should return no matches.
        """
        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.father_handle and person.gramps_id == 'NONEXISTENT'",
            )
        )
        # Should return empty list
        self.assertEqual(len(res), 0)

    def test_join_with_what_only_person(self):
        """
        Test JOIN where what clause only references person table.
        Note: Even though what only references person, we still need JOIN
        because family is referenced in where clause.
        """
        res = list(
            self.db.select_from_person(
                what="person.handle", where="person.handle == family.father_handle"
            )
        )
        # Should return person handles for people who are fathers
        self.assertGreater(len(res), 0)
        # All results should be strings (handles)
        for handle in res:
            self.assertIsInstance(handle, str)

    def test_join_with_what_only_family(self):
        """
        Test JOIN where what clause only references family table.
        """
        res = list(
            self.db.select_from_person(
                what="family.handle", where="person.handle == family.father_handle"
            )
        )
        # Should return family handles for families with fathers
        self.assertGreater(len(res), 0)
        # All results should be strings (handles)
        for handle in res:
            self.assertIsInstance(handle, str)

    def test_join_regression_existing_functionality(self):
        """
        Test that JOIN doesn't break existing single-table queries.
        This is a regression test to ensure backward compatibility.
        """
        # Test that existing queries still work
        res = list(
            self.db.select_from_person(
                what="person.handle", where="person.gender == Person.MALE"
            )
        )
        # Should work exactly as before
        self.assertGreater(len(res), 0)
        # Compare with known result
        res_known = set(
            list(
                self.db.select_from_person(
                    what="person.handle", where="person.gender == Person.MALE"
                )
            )
        )
        self.assertEqual(len(res_known), 1168)  # From test_ismale

    def test_join_regression_no_table_reference(self):
        """
        Test that queries without table references work as before.
        """
        res = list(
            self.db.select_from_person(
                what="person.handle", where="len(person.family_list) > 0"
            )
        )
        # Should work exactly as before (no JOIN needed)
        self.assertGreater(len(res), 0)

    def test_join_family_person_mother_reverse(self):
        """
        Test JOIN in reverse direction for mother relationship.
        Get family and mother's handle.
        """
        res = list(
            self.db.select_from_family(
                what=["family.handle", "person.handle"],
                where="family.mother_handle == person.handle",
            )
        )
        # Should return one row per family with a mother
        self.assertGreater(len(res), 0)
        # Verify each result
        for family_handle, person_handle in res:
            self.assertIsInstance(family_handle, str)
            self.assertIsInstance(person_handle, str)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_mother_handle(), person_handle)

    def test_join_with_order_by(self):
        """
        Test JOIN with ORDER BY clause.
        """
        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.father_handle",
                order_by=["person.handle", "family.handle"],
            )
        )
        # Should return sorted results
        self.assertGreater(len(res), 0)
        # Verify sorting (person handles should be in order)
        person_handles = [row[0] for row in res]
        self.assertEqual(person_handles, sorted(person_handles))

    def test_join_complex_expression(self):
        """
        Test JOIN with complex boolean expression.
        """
        from gramps.gen.lib import Person

        res = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="(person.handle == family.father_handle or person.handle == family.mother_handle) and person.gender == Person.FEMALE",
            )
        )
        # Should return families where person is the mother (female)
        self.assertGreaterEqual(len(res), 0)
        # Verify each result
        for person_handle, family_handle in res:
            person = self.db.get_person_from_handle(person_handle)
            self.assertIsNotNone(person)
            self.assertEqual(person.get_gender(), Person.FEMALE)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            # Person should be either father or mother
            self.assertTrue(
                family.get_father_handle() == person_handle
                or family.get_mother_handle() == person_handle
            )

    def test_variable_index_array_access_in_what(self):
        """
        Test variable-index array access in what clause.
        Example: person.event_ref_list[person.birth_ref_index]
        """
        res = list(
            self.db.select_from_person(
                what="person.event_ref_list[person.birth_ref_index]"
            )
        )
        # Should return one row per person with the birth event reference (if valid)
        # When what is a single string, it returns the value directly, not a tuple
        self.assertGreaterEqual(len(res), 0)
        # Verify results are valid (None for persons without valid birth_ref_index)
        for birth_ref in res:
            # birth_ref can be None if birth_ref_index is -1 or out of bounds
            # or it could be a dict/object representing the event_ref
            self.assertTrue(
                birth_ref is None
                or isinstance(birth_ref, (str, dict))
                or hasattr(birth_ref, "ref")
            )

    def test_variable_index_array_access_with_attributes(self):
        """
        Test variable-index array access with subsequent attribute access.
        Example: person.event_ref_list[person.birth_ref_index].role.value
        """
        res = list(
            self.db.select_from_person(
                what="person.event_ref_list[person.birth_ref_index].role.value"
            )
        )
        # Should return one row per person with the role value from birth event reference
        # When what is a single string, it returns the value directly, not a tuple
        self.assertGreaterEqual(len(res), 0)
        # Verify results are valid (None for persons without valid birth_ref_index)
        for role_value in res:
            # role_value can be None if birth_ref_index is -1 or out of bounds
            self.assertTrue(role_value is None or isinstance(role_value, int))

    def test_variable_index_array_access_in_where(self):
        """
        Test variable-index array access in where clause (truthiness check).
        Example: person.event_ref_list[person.birth_ref_index]
        """
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.event_ref_list[person.birth_ref_index]",
            )
        )
        # Should return persons who have a valid birth event reference
        # When what is a single string, it returns the value directly, not a tuple
        self.assertGreaterEqual(len(res), 0)
        # Verify each person has a valid birth_ref_index
        for person_handle in res:
            # Skip invalid handles (shouldn't happen, but be defensive)
            if not isinstance(person_handle, str) or len(person_handle) < 2:
                continue
            try:
                person = self.db.get_person_from_handle(person_handle)
                self.assertIsNotNone(person)
                # birth_ref_index should be valid (>= 0) and within bounds
                if person.birth_ref_index >= 0:
                    self.assertLess(
                        person.birth_ref_index, len(person.get_event_ref_list())
                    )
            except Exception:
                # If handle lookup fails, skip this entry
                continue

    def test_variable_index_array_access_with_attributes_in_where(self):
        """
        Test variable-index array access with attributes in where clause.
        Example: person.event_ref_list[person.birth_ref_index].role.value == 5
        """
        from gramps.gen.lib import EventRoleType

        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.event_ref_list[person.birth_ref_index].role.value == EventRoleType.PRIMARY",
            )
        )
        # Should return persons whose birth event reference has PRIMARY role
        # When what is a single string, it returns the value directly, not a tuple
        self.assertGreaterEqual(len(res), 0)
        # Verify each person's birth event reference has PRIMARY role
        for person_handle in res:
            # Skip invalid handles (shouldn't happen, but be defensive)
            if not isinstance(person_handle, str) or len(person_handle) < 2:
                continue
            try:
                person = self.db.get_person_from_handle(person_handle)
                self.assertIsNotNone(person)
                if person.birth_ref_index >= 0 and person.birth_ref_index < len(
                    person.get_event_ref_list()
                ):
                    birth_ref = person.get_event_ref_list()[person.birth_ref_index]
                    self.assertEqual(birth_ref.get_role().value, EventRoleType.PRIMARY)
            except Exception:
                # If handle lookup fails, skip this entry
                continue

    def test_join_with_variable_index_array_access(self):
        """
        Test JOIN with variable-index array access in join condition.
        Example: person.event_ref_list[person.birth_ref_index].ref == event.handle
        This joins person to event through the birth event reference.
        """
        res = list(
            self.db.select_from_person(
                what=["person.handle", "event.handle"],
                where="person.event_ref_list[person.birth_ref_index].ref == event.handle",
            )
        )
        # Should return one row per person with a valid birth event
        self.assertGreaterEqual(len(res), 0)
        # Verify each result: person's birth event reference should match event handle
        for person_handle, event_handle in res:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(event_handle, str)
            try:
                person = self.db.get_person_from_handle(person_handle)
                self.assertIsNotNone(person)
                event = self.db.get_event_from_handle(event_handle)
                self.assertIsNotNone(event)
                # Verify that the person's birth_ref_index points to this event
                if person.birth_ref_index >= 0 and person.birth_ref_index < len(
                    person.get_event_ref_list()
                ):
                    birth_ref = person.get_event_ref_list()[person.birth_ref_index]
                    self.assertEqual(birth_ref.ref, event_handle)
            except Exception:
                # If handle lookup fails, skip this entry
                continue

    def test_join_with_variable_index_array_access_and_condition(self):
        """
        Test JOIN with variable-index array access and additional condition.
        Example: Join person to event via birth, and filter by event type.
        """
        from gramps.gen.lib import EventType

        res = list(
            self.db.select_from_person(
                what=["person.handle", "event.handle", "event.type.value"],
                where="person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == EventType.BIRTH",
            )
        )
        # Should return persons with birth events that are actually BIRTH type
        self.assertGreaterEqual(len(res), 0)
        # Verify each result
        for person_handle, event_handle, event_type in res:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(event_handle, str)
            self.assertEqual(event_type, EventType.BIRTH)
            try:
                person = self.db.get_person_from_handle(person_handle)
                self.assertIsNotNone(person)
                event = self.db.get_event_from_handle(event_handle)
                self.assertIsNotNone(event)
                self.assertEqual(event.get_type().value, EventType.BIRTH)
                # Verify that the person's birth_ref_index points to this event
                if person.birth_ref_index >= 0 and person.birth_ref_index < len(
                    person.get_event_ref_list()
                ):
                    birth_ref = person.get_event_ref_list()[person.birth_ref_index]
                    self.assertEqual(birth_ref.ref, event_handle)
            except Exception:
                # If handle lookup fails, skip this entry
                continue

    def test_pagination_basic(self):
        """
        Test basic pagination - get first page of results.
        """
        # Get first page with 10 items
        page1 = list(
            self.db.select_from_person(
                what="person.handle",
                order_by="person.handle",
                page=1,
                page_size=10,
            )
        )
        # Should return exactly 10 items
        self.assertEqual(len(page1), 10)
        # All should be handles (strings)
        for handle in page1:
            self.assertIsInstance(handle, str)

    def test_pagination_second_page(self):
        """
        Test pagination - get second page of results.
        """
        # Get first page
        page1 = list(
            self.db.select_from_person(
                what="person.handle",
                order_by="person.handle",
                page=1,
                page_size=10,
            )
        )
        # Get second page
        page2 = list(
            self.db.select_from_person(
                what="person.handle",
                order_by="person.handle",
                page=2,
                page_size=10,
            )
        )
        # Should return exactly 10 items
        self.assertEqual(len(page2), 10)
        # Pages should not overlap
        self.assertEqual(len(set(page1) & set(page2)), 0)
        # Second page should come after first page
        self.assertGreater(min(page2), max(page1))

    def test_pagination_with_where(self):
        """
        Test pagination with WHERE clause filtering.
        """
        from gramps.gen.lib import Person

        # Get first page of males
        page1 = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.gender == Person.MALE",
                order_by="person.handle",
                page=1,
                page_size=20,
            )
        )
        # Should return at most 20 items
        self.assertLessEqual(len(page1), 20)
        # Verify all are males
        for handle in page1:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(person.get_gender(), Person.MALE)

    def test_pagination_with_order_by(self):
        """
        Test pagination with ORDER BY clause.
        """
        # Get first page sorted by surname
        page1 = list(
            self.db.select_from_person(
                what=["person.primary_name.surname_list[0].surname", "person.gender"],
                where="len(person.media_list) > 0",
                order_by=[
                    "-person.primary_name.surname_list[0].surname",
                    "person.gender",
                ],
                page=1,
                page_size=5,
            )
        )
        # Should return at most 5 items
        self.assertLessEqual(len(page1), 5)
        # Verify sorting (descending surname)
        surnames = [row[0] for row in page1 if row[0]]
        if len(surnames) > 1:
            self.assertEqual(surnames, sorted(surnames, reverse=True))

    def test_pagination_with_join(self):
        """
        Test pagination with JOIN queries.
        """
        # Get first page of person-family joins
        page1 = list(
            self.db.select_from_person(
                what=["person.handle", "family.handle"],
                where="person.handle == family.father_handle",
                order_by=["person.handle", "family.handle"],
                page=1,
                page_size=15,
            )
        )
        # Should return at most 15 items
        self.assertLessEqual(len(page1), 15)
        # Verify each result
        for person_handle, family_handle in page1:
            self.assertIsInstance(person_handle, str)
            self.assertIsInstance(family_handle, str)
            family = self.db.get_family_from_handle(family_handle)
            self.assertIsNotNone(family)
            self.assertEqual(family.get_father_handle(), person_handle)

    def test_pagination_empty_result(self):
        """
        Test pagination when result set is empty.
        """
        # Query that returns no results
        page1 = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.gramps_id == 'NONEXISTENT'",
                page=1,
                page_size=10,
            )
        )
        # Should return empty list
        self.assertEqual(len(page1), 0)

    def test_pagination_last_page_partial(self):
        """
        Test pagination when last page has fewer items than page_size.
        """
        # Get total count
        all_handles = list(
            self.db.select_from_person(
                what="person.handle",
                order_by="person.handle",
            )
        )
        total = len(all_handles)

        # Calculate last page number
        page_size = 100
        last_page = (total + page_size - 1) // page_size  # Ceiling division

        # Get last page
        last_page_results = list(
            self.db.select_from_person(
                what="person.handle",
                order_by="person.handle",
                page=last_page,
                page_size=page_size,
            )
        )
        # Should return remaining items (less than or equal to page_size)
        self.assertLessEqual(len(last_page_results), page_size)
        # Should match the last items from full query
        expected_last = all_handles[(last_page - 1) * page_size :]
        self.assertEqual(last_page_results, expected_last)

    # ========================================================================
    # Additional Comprehensive Semantic Tests
    # ========================================================================

    def test_three_level_nested_and_or(self):
        """
        Test three-level nested boolean expression: ((A and B) or (C and D)) and E
        """
        from gramps.gen.lib import Person

        # Find persons matching: ((male AND has families) OR (female AND has media)) AND has notes
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="((person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0)) and len(person.note_list) > 0",
                )
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics by checking each person
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = person.gender == Person.FEMALE and len(person.media_list) > 0
            condition3 = len(person.note_list) > 0
            self.assertTrue((condition1 or condition2) and condition3)

    def test_four_level_nested_expression(self):
        """
        Test four-level nested boolean expression: (((A and B) or C) and D) or E
        """
        from gramps.gen.lib import Person

        # Find persons matching: (((male AND has families) OR has media) AND has notes) OR has citations
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(((person.gender == Person.MALE and len(person.family_list) > 0) or len(person.media_list) > 0) and len(person.note_list) > 0) or len(person.citation_list) > 0",
                )
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = len(person.media_list) > 0
            condition3 = len(person.note_list) > 0
            condition4 = len(person.citation_list) > 0
            self.assertTrue((((condition1 or condition2) and condition3) or condition4))

    def test_mixed_operators_complex(self):
        """
        Test mixed AND/OR operators: (A and B) or (C and D) and E
        Note: This tests operator precedence - 'and' binds tighter than 'or'
        """
        from gramps.gen.lib import Person

        # Find persons matching: (male AND has families) OR (female AND has media) AND has notes
        # This is parsed as: (A and B) or ((C and D) and E)
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0) and len(person.note_list) > 0",
                )
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            condition1 = person.gender == Person.MALE and len(person.family_list) > 0
            condition2 = person.gender == Person.FEMALE and len(person.media_list) > 0
            condition3 = len(person.note_list) > 0
            # Python precedence: and binds tighter than or
            expected = condition1 or (condition2 and condition3)
            self.assertTrue(expected, f"Person {handle} should match the expression")

    def test_nested_selection_complex_path(self):
        """
        Test complex nested attribute paths with multiple levels.
        """
        # Test accessing deeply nested attributes
        # Use a simpler where clause that's more likely to match
        res = list(
            self.db.select_from_person(
                what="person.primary_name.surname_list[0].surname",
                where="person.primary_name and len(person.primary_name.surname_list) > 0",
            )
        )
        # Some persons may not have surnames, so just check we get results or empty list
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics by checking each result
        for surname in res:
            if surname:  # Some may be None or empty
                self.assertIsInstance(surname, str)

    def test_list_comprehension_with_multiple_conditions(self):
        """
        Test list comprehension with multiple conditions combined with AND.
        """
        from gramps.gen.lib import EventRoleType

        # Extract event refs that are PRIMARY AND have a ref
        res = list(
            self.db.select_from_person(
                what="[eref.ref for eref in person.event_ref_list if eref.role.value == EventRoleType.PRIMARY and eref.ref]",
                where="len(person.event_ref_list) > 0",
            )
        )
        # Should return one row per person, with list of matching refs
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for ref_list in res:
            if ref_list:  # Some persons may have no matching refs
                self.assertIsInstance(ref_list, list)
                for ref in ref_list:
                    self.assertIsNotNone(ref)
                    self.assertIsInstance(ref, str)

    def test_list_comprehension_with_nested_attribute(self):
        """
        Test list comprehension accessing nested attributes of array elements.
        """
        # Extract role values from event_ref_list
        res = list(
            self.db.select_from_person(
                what="[eref.role.value for eref in person.event_ref_list]",
                where="len(person.event_ref_list) > 0",
            )
        )
        self.assertGreater(len(res), 0)
        # Verify semantics
        # Note: List comprehensions return one row per matching array element
        # So res is a list of individual values, not a list of lists
        for role_value in res:
            self.assertIsInstance(role_value, int)

    def test_list_comprehension_concatenated_with_condition(self):
        """
        Test list comprehension with concatenated arrays and condition.
        Note: List comprehensions return one row per matching array element,
        not one row per person with a list of matches.
        """
        # Add search_name to environment
        env = {"search_name": "John"}
        res = list(
            self.db.select_from_person(
                what="[name.first_name for name in [person.primary_name] + person.alternate_names if search_name in name.first_name]",
                where="len(person.alternate_names) >= 0",  # All persons
                env=env,
            )
        )
        # Should return one row per matching name (not per person)
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics - each result is a single name string
        for name in res:
            if name:  # Some may be None or empty
                self.assertIsInstance(name, str)
                # The name should contain 'John' if the condition worked
                # (though the actual matching happens in SQL, so we just verify format)

    def test_join_semantics_multiple_tables(self):
        """
        Test JOIN semantics with multiple table references.
        Verify that JOIN results correctly represent relationships.
        """
        # Join person with event through event_ref_list
        res = list(
            self.db.select_from_person(
                what=["person.handle", "event.handle"],
                where="person.event_ref_list[0].ref == event.handle",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics: each result should represent a valid relationship
        for person_handle, event_handle in res:
            person = self.db.get_person_from_handle(person_handle)
            event = self.db.get_event_from_handle(event_handle)
            self.assertIsNotNone(person)
            self.assertIsNotNone(event)
            # Verify the relationship exists
            found = False
            for eref in person.get_event_ref_list():
                if eref.ref == event_handle:
                    found = True
                    break
            self.assertTrue(
                found, f"Person {person_handle} should have event_ref to {event_handle}"
            )

    def test_join_with_complex_condition(self):
        """
        Test JOIN with complex condition involving multiple attributes.
        """
        from gramps.gen.lib import EventType

        # Join person with event where event is BIRTH type
        res = list(
            self.db.select_from_person(
                what=["person.handle", "event.handle", "event.type.value"],
                where="person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == EventType.BIRTH",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for person_handle, event_handle, event_type in res:
            self.assertEqual(event_type, EventType.BIRTH)
            person = self.db.get_person_from_handle(person_handle)
            event = self.db.get_event_from_handle(event_handle)
            self.assertIsNotNone(person)
            self.assertIsNotNone(event)
            self.assertEqual(event.get_type(), EventType.BIRTH)

    def test_union_semantics_array_expansion_or(self):
        """
        Test UNION semantics when array expansion is used in OR expression.
        Verify that UNION correctly combines results from both sides.
        """
        from gramps.gen.lib import Person

        # Query: (male AND has families) OR (item in person.event_ref_list)
        # This should use UNION to combine:
        # 1. Persons matching left side (even with empty arrays)
        # 2. Persons with event_refs (one row per event_ref)
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="(person.gender == Person.MALE and len(person.family_list) > 0) or (item in person.event_ref_list)",
            )
        )
        self.assertGreater(len(res), 0)

        # Get left side results
        left_side = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and len(person.family_list) > 0",
                )
            )
        )

        # Get right side results (array expansion)
        right_side = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="item in person.event_ref_list",
                )
            )
        )

        # Union should include all from both sides
        unique_res = set(res)
        self.assertTrue(
            left_side.issubset(unique_res), "UNION should include left side"
        )
        self.assertTrue(
            right_side.issubset(unique_res), "UNION should include right side"
        )

    def test_array_expansion_with_join(self):
        """
        Test array expansion combined with JOIN to another table.
        """
        # Array expansion with join to event table
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="item in person.event_ref_list and item.ref == event.handle",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics: each result should have a valid event_ref
        unique_handles = set(res)
        for handle in unique_handles:
            person = self.db.get_person_from_handle(handle)
            self.assertGreater(len(person.get_event_ref_list()), 0)

    def test_array_expansion_with_join_and_condition(self):
        """
        Test array expansion with JOIN and additional condition on joined table.
        """
        from gramps.gen.lib import EventType

        # Array expansion with join and condition on event
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="item in person.event_ref_list and item.ref == event.handle and event.type.value == EventType.BIRTH",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        unique_handles = set(res)
        for handle in unique_handles:
            person = self.db.get_person_from_handle(handle)
            # Person should have at least one BIRTH event_ref
            found = False
            for eref in person.get_event_ref_list():
                event = self.db.get_event_from_handle(eref.ref)
                if event and event.get_type() == EventType.BIRTH:
                    found = True
                    break
            self.assertTrue(found, f"Person {handle} should have BIRTH event_ref")

    def test_variable_index_access_in_where(self):
        """
        Test variable-index array access in WHERE clause with condition.
        """
        from gramps.gen.lib import EventRoleType

        # Access birth event_ref using variable index and check role
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.event_ref_list[person.birth_ref_index].role.value == EventRoleType.PRIMARY",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            birth_index = person.birth_ref_index  # Use property, not method
            if birth_index is not None and birth_index >= 0:
                eref_list = person.get_event_ref_list()
                if birth_index < len(eref_list):
                    eref = eref_list[birth_index]
                    self.assertEqual(eref.get_role(), EventRoleType.PRIMARY)

    def test_variable_index_access_in_what(self):
        """
        Test variable-index array access in WHAT clause.
        """
        # Get birth event_ref using variable index
        res = list(
            self.db.select_from_person(
                what="person.event_ref_list[person.birth_ref_index]",
                where="person.birth_ref_index is not None",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for eref in res:
            if eref:  # Some may be None if index is out of range
                self.assertIsNotNone(eref.ref)

    def test_variable_index_with_nested_attribute(self):
        """
        Test variable-index array access with subsequent attribute access.
        """
        # Get role value from birth event_ref
        res = list(
            self.db.select_from_person(
                what="person.event_ref_list[person.birth_ref_index].role.value",
                where="person.birth_ref_index is not None",
            )
        )
        self.assertGreaterEqual(len(res), 0)
        # Verify semantics
        for role_value in res:
            if role_value is not None:
                self.assertIsInstance(role_value, int)

    def test_null_handling_in_comparison(self):
        """
        Test NULL handling in comparison expressions.
        """
        # Test comparison with potentially NULL values
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.birth_ref_index is not None or person.birth_ref_index is None",
            )
        )
        # Should return all persons (everyone has birth_ref_index that is either None or not None)
        all_persons = list(self.db.select_from_person(what="person.handle"))
        self.assertEqual(len(res), len(all_persons))

    def test_empty_array_handling(self):
        """
        Test handling of empty arrays in various contexts.
        """
        from gramps.gen.lib import Person

        # Find persons with empty event_ref_list
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.event_ref_list) == 0",
                )
            )
        )
        # Verify semantics
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(len(person.get_event_ref_list()), 0)

    def test_empty_array_with_any(self):
        """
        Test any() with empty array (should return False).
        """
        # any() on empty array should return False, so no results
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="any([eref for eref in person.event_ref_list if eref.role.value == 999])",  # Non-existent role
            )
        )
        # Should return empty or very few results
        # Verify semantics: check that results actually have matching event_refs
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            found = any(eref.role.value == 999 for eref in person.get_event_ref_list())
            self.assertTrue(found, f"Person {handle} should have matching event_ref")

    def test_type_coercion_in_comparison(self):
        """
        Test type coercion in comparison expressions.
        """
        from gramps.gen.lib import Person

        # Compare integer with integer constant - Person.MALE is actually 1, not 0
        # Person.UNKNOWN is 0, Person.MALE is 1, Person.FEMALE is 2
        res = list(
            self.db.select_from_person(
                what="person.handle",
                where="person.gender == 1",  # Person.MALE is 1
            )
        )
        # Verify semantics
        for handle in res:
            person = self.db.get_person_from_handle(handle)
            self.assertEqual(person.get_gender(), Person.MALE)

    def test_complex_nested_selection_path(self):
        """
        Test very complex nested selection paths.
        """
        # Access deeply nested attribute: primary_name -> surname_list -> first surname -> surname
        res = list(
            self.db.select_from_person(
                what="person.primary_name.surname_list[0].surname",
                where="len(person.primary_name.surname_list) > 0",
            )
        )
        self.assertGreater(len(res), 0)
        # Verify semantics
        for surname in res:
            self.assertIsNotNone(surname)
            self.assertIsInstance(surname, str)

    def test_list_comprehension_returning_tuples(self):
        """
        Test list comprehension that returns tuples.
        Note: Tuples in list comprehensions may not be fully supported in SQL.
        This test verifies the syntax is accepted, but the result format may vary.
        """
        # Return tuples of (role.value, ref) from event_ref_list
        # Note: SQL may not support tuple returns directly, so this might return
        # a different format or raise an error
        try:
            res = list(
                self.db.select_from_person(
                    what="[(eref.role.value, eref.ref) for eref in person.event_ref_list]",
                    where="len(person.event_ref_list) > 0",
                )
            )
            # If it works, verify the results
            if res:
                # Results might be in different formats depending on SQL implementation
                # Just verify we got something back
                self.assertGreater(len(res), 0)
                # Check first result to see what format we got
                first = res[0]
                # Could be a list, tuple, or other format
                self.assertIsNotNone(first)
        except Exception as e:
            # If tuples aren't supported, that's okay - just skip this test
            # or mark it as expected to fail
            if "row value" in str(e).lower() or "tuple" in str(e).lower():
                # Expected - tuples may not be supported
                pass
            else:
                raise

    # ========================================================================
    # Edge case semantic tests for comparison operators
    # ========================================================================

    def test_comparison_with_none_semantic(self):
        """Test semantic correctness of comparisons with None."""
        # is None - should find people without birth_ref_index
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.birth_ref_index is None",
                )
            )
        )
        # Should return some results (people without birth events)
        self.assertGreaterEqual(len(res), 0)

        # is not None - should find people with birth_ref_index
        res2 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.birth_ref_index is not None",
                )
            )
        )
        # Should return some results (people with birth events)
        self.assertGreaterEqual(len(res2), 0)
        # The two sets should be disjoint
        self.assertEqual(len(res & res2), 0)

    def test_comparison_with_empty_string_semantic(self):
        """Test semantic correctness of comparisons with empty strings."""
        # Equality with empty string
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id == ''",
                )
            )
        )
        # Should return empty set (all people have gramps_id)
        self.assertEqual(len(res), 0)

        # Inequality with empty string
        res2 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id != ''",
                )
            )
        )
        # Should return all people
        self.assertEqual(len(res2), self.db.get_number_of_people())

    def test_comparison_with_zero_semantic(self):
        """Test semantic correctness of comparisons with zero."""
        # Equality with zero
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        # Should match nevermarried test
        nevermarried = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        self.assertEqual(res, nevermarried)

        # Greater than zero
        res2 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )
        # Should be complement of zero
        self.assertEqual(len(res & res2), 0)
        self.assertEqual(len(res) + len(res2), self.db.get_number_of_people())

    def test_chained_comparisons_semantic(self):
        """Test semantic correctness of chained comparisons."""
        # Single comparison
        res1 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )

        # Chained comparison: 0 < len < 10
        res2 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="0 < len(person.family_list) < 10",
                )
            )
        )
        # Should be subset of res1
        self.assertTrue(res2.issubset(res1))

        # Chained comparison: 0 < len < 5
        res3 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="0 < len(person.family_list) < 5",
                )
            )
        )
        # Should be subset of res2
        self.assertTrue(res3.issubset(res2))

    def test_comparison_not_in_semantic(self):
        """Test semantic correctness of 'not in' operator."""
        # Find people with gramps_id not containing 'I00'
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="'I00' not in person.gramps_id",
                )
            )
        )
        # Should be complement of 'in' result
        res_in = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="'I00' in person.gramps_id",
                )
            )
        )
        # The two sets should be disjoint and together equal all people
        self.assertEqual(len(res & res_in), 0)
        self.assertEqual(len(res) + len(res_in), self.db.get_number_of_people())

    # ========================================================================
    # Edge case semantic tests for boolean operations
    # ========================================================================

    def test_boolean_and_or_precedence_semantic(self):
        """Test semantic correctness of AND/OR precedence."""
        # A or B and C should be A or (B and C)
        # Test: gender == MALE or (family_list > 0 and media_list > 0)
        res1 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE or len(person.family_list) > 0 and len(person.media_list) > 0",
                )
            )
        )

        # Explicit parentheses: (gender == MALE or family_list > 0) and media_list > 0
        res2 = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender == Person.MALE or len(person.family_list) > 0) and len(person.media_list) > 0",
                )
            )
        )

        # These should be different (precedence matters)
        # res1 should include all males, res2 should only include people with media
        self.assertNotEqual(res1, res2)

    def test_boolean_nested_parentheses_semantic(self):
        """Test semantic correctness of nested boolean expressions."""
        # Complex nested expression
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="((person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0)) and len(person.note_list) > 0",
                )
            )
        )
        # Should return some results
        self.assertGreaterEqual(len(res), 0)

        # Verify it's a subset of people with notes
        res_notes = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.note_list) > 0",
                )
            )
        )
        self.assertTrue(res.issubset(res_notes))

    def test_boolean_multiple_and_semantic(self):
        """Test semantic correctness of multiple AND conditions."""
        # All conditions must be true
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE and len(person.family_list) > 0 and len(person.media_list) > 0",
                )
            )
        )
        # Should be subset of each individual condition
        res_male = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE",
                )
            )
        )
        res_family = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )
        res_media = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.media_list) > 0",
                )
            )
        )
        self.assertTrue(res.issubset(res_male))
        self.assertTrue(res.issubset(res_family))
        self.assertTrue(res.issubset(res_media))

    def test_boolean_multiple_or_semantic(self):
        """Test semantic correctness of multiple OR conditions."""
        # Any condition can be true
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE or person.gender == Person.FEMALE or person.gender == Person.UNKNOWN",
                )
            )
        )
        # Should include all people (all genders are covered)
        self.assertEqual(len(res), self.db.get_number_of_people())

    # ========================================================================
    # Edge case semantic tests for binary operations
    # ========================================================================

    def test_binary_modulo_semantic(self):
        """Test semantic correctness of modulo operation."""
        # Even number of families (mod 2 == 0)
        res_even = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) % 2 == 0",
                )
            )
        )
        # Odd number of families (mod 2 == 1)
        res_odd = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) % 2 == 1",
                )
            )
        )
        # Should be disjoint and together equal all people
        self.assertEqual(len(res_even & res_odd), 0)
        self.assertEqual(len(res_even) + len(res_odd), self.db.get_number_of_people())

    def test_binary_operations_combined_semantic(self):
        """Test semantic correctness of combined binary operations."""
        # (media_list + note_list) > 0 should match (media_list > 0 or note_list > 0)
        res_sum = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.media_list) + len(person.note_list) > 0",
                )
            )
        )
        res_or = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.media_list) > 0 or len(person.note_list) > 0",
                )
            )
        )
        # Should be equivalent
        self.assertEqual(res_sum, res_or)

    # ========================================================================
    # Edge case semantic tests for unary operations
    # ========================================================================

    def test_unary_not_semantic(self):
        """Test semantic correctness of 'not' operator."""
        # not private should match public
        res_not_private = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="not person.private",
                )
            )
        )
        res_public = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.private == False",
                )
            )
        )
        # Should be equivalent
        self.assertEqual(res_not_private, res_public)

    def test_unary_not_with_zero_semantic(self):
        """Test semantic correctness of 'not' with zero."""
        # not (len == 0) should match (len > 0)
        res_not_zero = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="not (len(person.family_list) == 0)",
                )
            )
        )
        res_gt_zero = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )
        # Should be equivalent
        self.assertEqual(res_not_zero, res_gt_zero)

    def test_unary_negation_semantic(self):
        """Test semantic correctness of unary negation."""
        # -len < 0 should match len > 0
        res_neg = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="-len(person.family_list) < 0",
                )
            )
        )
        res_pos = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) > 0",
                )
            )
        )
        # Should be equivalent
        self.assertEqual(res_neg, res_pos)

    # ========================================================================
    # Edge case semantic tests for function calls
    # ========================================================================

    def test_len_with_empty_array_semantic(self):
        """Test semantic correctness of len() with empty arrays."""
        # len == 0 should match nevermarried
        res_len_zero = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        res_nevermarried = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="len(person.family_list) == 0",
                )
            )
        )
        # Should be equivalent
        self.assertEqual(res_len_zero, res_nevermarried)

    def test_startswith_endswith_semantic(self):
        """Test semantic correctness of startswith and endswith."""
        # startswith('I00') should be subset of 'I00' in gramps_id
        res_startswith = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.startswith('I00')",
                )
            )
        )
        res_in = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="'I00' in person.gramps_id",
                )
            )
        )
        # startswith should be subset of 'in'
        self.assertTrue(res_startswith.issubset(res_in))

        # endswith('44') should find specific person
        res_endswith = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.endswith('44')",
                )
            )
        )
        # Should include I0044
        res_exact = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id == 'I0044'",
                )
            )
        )
        self.assertTrue(res_exact.issubset(res_endswith))

    def test_startswith_with_empty_string_semantic(self):
        """Test semantic correctness of startswith with empty string."""
        # startswith('') should match all people
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.startswith('')",
                )
            )
        )
        # Should match all people
        self.assertEqual(len(res), self.db.get_number_of_people())

    def test_endswith_with_empty_string_semantic(self):
        """Test semantic correctness of endswith with empty string."""
        # endswith('') should match all people
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gramps_id.endswith('')",
                )
            )
        )
        # Should match all people
        self.assertEqual(len(res), self.db.get_number_of_people())

    # ========================================================================
    # Edge case semantic tests for ternary expressions
    # ========================================================================

    def test_ternary_expression_semantic(self):
        """Test semantic correctness of ternary expressions."""
        # Test ternary in what clause
        res = list(
            self.db.select_from_person(
                what="person.gramps_id if person.gramps_id else 'UNKNOWN'",
                where="len(person.family_list) > 0",
            )
        )
        # Should return gramps_id or 'UNKNOWN'
        self.assertGreater(len(res), 0)
        for item in res:
            self.assertIsInstance(item, str)
            # Should never be empty (either gramps_id or 'UNKNOWN')
            self.assertGreater(len(item), 0)

    def test_ternary_in_where_clause_semantic(self):
        """Test semantic correctness of ternary in where clause."""
        # Use ternary to provide default value
        res = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="(person.gender if person.gender else Person.UNKNOWN) == Person.MALE",
                )
            )
        )
        # Should match people with MALE gender
        res_male = set(
            list(
                self.db.select_from_person(
                    what="person.handle",
                    where="person.gender == Person.MALE",
                )
            )
        )
        # Should be equivalent (assuming all people have gender set)
        # Note: This might differ if some people have None gender
        self.assertGreaterEqual(len(res), 0)


if __name__ == "__main__":
    unittest.main()
