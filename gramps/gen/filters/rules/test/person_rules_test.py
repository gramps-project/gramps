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
Unittest that tests person-specific filter rules
"""
import unittest
import os
from time import perf_counter
import inspect

from ....filters import reload_custom_filters
reload_custom_filters()
from ....db.utils import import_as_dict
from ....filters import GenericFilter, CustomFilters
from ....const import DATA_DIR
from ....user import User

from ..person import (
    Disconnected, Everyone, FamilyWithIncompleteEvent, HasAddress,
    HasAlternateName, HasAssociation, HasBirth, HasDeath, HasEvent,
    HasCommonAncestorWith, HasCommonAncestorWithFilterMatch,
    HasFamilyAttribute, HasFamilyEvent, HasIdOf, HasLDS,
    HasNameOf, HasNameOriginType, HasNameType, HasNickname, HasRelationship,
    HasSoundexName, HasSourceOf, HasTextMatchingRegexpOf, HasUnknownGender,
    HaveAltFamilies, HaveChildren, HavePhotos, IncompleteNames,
    IsAncestorOfFilterMatch, IsBookmarked, IsChildOfFilterMatch,
    IsDescendantFamilyOf, IsDescendantFamilyOfFilterMatch,
    IsDescendantOfFilterMatch, IsDefaultPerson, IsDescendantOf,
    IsDuplicatedAncestorOf, IsFemale,
    IsLessThanNthGenerationAncestorOf,
    IsLessThanNthGenerationAncestorOfDefaultPerson,
    IsLessThanNthGenerationAncestorOfBookmarked, IsMale,
    IsMoreThanNthGenerationAncestorOf, IsMoreThanNthGenerationDescendantOf,
    IsParentOfFilterMatch, IsRelatedWith, IsSiblingOfFilterMatch,
    IsSpouseOfFilterMatch, IsWitness, MissingParent, MultipleMarriages,
    NeverMarried, NoBirthdate, NoDeathdate, PeoplePrivate, PeoplePublic,
    PersonWithIncompleteEvent, ProbablyAlive, RegExpName,
    RelationshipPathBetweenBookmarks,
)

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")

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

    def filter_with_rule(self, rule, l_op='and', invert=False,
                         baserule=None, base_l_op='and', base_invert=False,
                         base_name='Base'):
        """
        Apply a filter with the given rule.  'baserule' can be used to stack
        filters when using filters that are of 'offiltermatch' type.
        """
        if baserule:
            filter_ = GenericFilter()
            if isinstance(baserule, list):
                filter_.set_rules(baserule)
            else:
                filter_.add_rule(baserule)
            filter_.set_logical_op(base_l_op)
            filter_.set_invert(base_invert)
            filter_.set_name(base_name)
            filters = CustomFilters.get_filters_dict('Person')
            filters[base_name] = filter_
        filter_ = GenericFilter()
        if isinstance(rule, list):
            filter_.set_rules(rule)
        else:
            filter_.add_rule(rule)
        filter_.set_logical_op(l_op)
        filter_.set_invert(invert)
        stime = perf_counter()
        results = filter_.apply(self.db)
        if __debug__:
            rulename = inspect.stack()[1][3]
            print("%s: %.2f\n" % (rulename, perf_counter() - stime))
        return set(results)

    def test_Complex_1(self):
        """ Test with two ancestor trees in base filter, and a complex
        'or' of a descendent tree, sibling of, """
        rule1 = IsLessThanNthGenerationAncestorOf(['I0005', 10])
        rule2 = IsLessThanNthGenerationAncestorOf(['I0006', 10])
        ruleA = IsDescendantOfFilterMatch(['Base'])
        ruleB = IsSiblingOfFilterMatch(['Base'])
        ruleC = IsSpouseOfFilterMatch(['Base'])
        res = self.filter_with_rule([ruleA, ruleB, ruleC], l_op='or',
                                    baserule=[rule1, rule2], base_l_op='or')
        self.assertEqual(len(res), 1277)

    def test_IsDescendantOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0610'])
        rule2 = HasIdOf(['I1804'])
        rule = IsDescendantOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 120)

    def test_IsDescendantFamilyOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0610'])
        rule2 = HasIdOf(['I1804'])
        rule = IsDescendantFamilyOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 171)

    def test_IsDescendantFamilyOf(self):
        """ Test the rule """
        rule = IsDescendantFamilyOf(['I0610', 1])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 118)

    def test_IsDescendantOf(self):
        """ Test the rule """
        rule = IsDescendantOf(['I0610', 0])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 85)

    def test_IsMoreThanNthGenerationDescendantOf(self):
        """ Test the rule """
        rule = IsMoreThanNthGenerationDescendantOf(['I0610', 3])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 83)

    def test_IsLessThanNthGenerationAncestorOfDefaultPerson(self):
        """ Test the rule """
        rule = IsLessThanNthGenerationAncestorOfDefaultPerson([5])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 7)

    def test_IsLessThanNthGenerationAncestorOfBookmarked(self):
        """ Test the rule """
        rule = IsLessThanNthGenerationAncestorOfBookmarked([5])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 8)

    def test_IsParentOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0010'])
        rule = IsParentOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 4)

    def test_IsSiblingOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0010'])
        rule = IsSiblingOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 7)

    def test_IsSpouseOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0010'])
        rule = IsSpouseOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 2)

    def test_isancestoroffiltermatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0005'])
        rule = IsAncestorOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 431)

    def test_HasCommonAncestorWithFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0005'])
        rule = HasCommonAncestorWithFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 1415)

    def test_IsChildOfFilterMatch(self):
        """ Test the rule with two persons in base filter """
        rule1 = HasIdOf(['I0006'])
        rule2 = HasIdOf(['I0010'])
        rule = IsChildOfFilterMatch(['Base'])
        res = self.filter_with_rule(rule, baserule=[rule1, rule2],
                                    base_l_op='or')
        self.assertEqual(len(res), 11)

    def test_HasAddress(self):
        """
        Test HasAddress rule.
        """
        rule = HasAddress([0, 'greater than'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 1)

    def test_HasAssociation(self):
        """
        Test rule.
        """
        rule = HasAssociation([0, 'greater than'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 2)

    def test_HasBirth(self):
        """
        Test rule.
        """
        rule = HasBirth(['between 1600 and 1700', 'akron', ''])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 2)

    def test_HasDeath(self):
        """
        Test HasDeath rule.
        """
        rule = HasDeath(['between 1600 and 1700', 'ashtabula', ''])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 2)

    def test_HasEvent(self):
        """
        Test rule.
        """
        rule = HasEvent(['Birth', 'between 1600 and 1700', 'akron',
                         '', '', 1])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 2)

    def test_HasFamilyAttribute(self):
        """
        Test rule.
        """
        rule = HasFamilyAttribute([5, '8'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 2)

    def test_HasFamilyEvent(self):
        """
        Test rule.
        """
        rule = HasFamilyEvent(['Marriage', 'after 1900', 'craw', ''])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 4)

    def test_HavePhotos(self):
        """
        Test rule.
        """
        rule = HavePhotos([0, 'greater than'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 5)

    def test_HasLDS(self):
        """
        Test rule.
        """
        rule = HasLDS([0, 'greater than'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 1)

    def test_HasNameOriginType(self):
        """
        Test rule.
        """
        rule = HasNameOriginType(['Patrilineal'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 9)

    def test_HasNameType(self):
        """
        Test rule.
        """
        rule = HasNameType(['Married Name'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 1)

    def test_HasRelationship(self):
        """
        Test rule.
        """
        rule = HasRelationship([0, 'Married', 0])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 1377)

    def test_HasTextMatchingRegexpOf(self):
        """
        Test rule.
        """
        rule = HasTextMatchingRegexpOf(['.*(Dahl|Akron|Smith|Attic|'
                                        'of Lessard).*', False],
                                       use_regex=True)
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 28)

    def test_IsMoreThanNthGenerationAncestorOf(self):
        """
        Test rule.
        """
        rule = IsMoreThanNthGenerationAncestorOf(['I0005', 3])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 322)

    def test_IsWitness(self):
        """
        Test rule.
        """
        rule = IsWitness(['Marriage'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 1)

    def test_ProbablyAlive(self):
        """
        Test rule.
        """
        rule = ProbablyAlive(['1900'])
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 766)

    def test_RegExpName(self):
        """
        Test rule.
        """
        rule = RegExpName(['.*(Garc|Amy).*'], use_regex=True)
        res = self.filter_with_rule(rule)
        self.assertEqual(len(res), 3)


    def test_disconnected(self):
        """
        Test Disconnected rule.
        """
        rule = Disconnected([])
        self.assertEqual(self.filter_with_rule(rule), set([
            '0PBKQCXHLAEIB46ZIA', 'QEVJQC04YO01UAWJ2N', 'UT0KQCMN7PC9XURRXJ',
            'MZAKQCKAQLIQYWP5IW', 'Y7BKQC9CUXWQLGLPQM', 'OBBKQC8NJM5UYBO849',
            'NPBKQCKEF0G7T4H312', '423KQCGLT8UISDUM1Q', '8S0KQCNORIWDL0X8SB',
            'AP5KQC0LBXPM727OWB', 'AREKQC0VPBHNZ5R3IO', 'KU0KQCJ0RUTJTIUKSA',
            'VC4KQC7L7KKH9RLHXN', '0P3KQCRSIVL1A4VJ19', 'PK6KQCGEL4PTE720BL',
            'YIKKQCSD2Z85UHJ8LX', 'KY8KQCMIH2HUUGLA3R', 'RD7KQCQ24B1N3OEC5X',
            'NV0KQC7SIEH3SVDPP1', 'KIKKQCU2CJ543TLM5J', 'AT0KQC4P3MMUCHI3BK',
            'J6BKQC1PMNBAYSLM9U', 'IXXJQCLKOUAJ5RSQY4', 'U4ZJQC5VR0QBIE8DU',
            'F7BKQC4NXO9R7XOG2W', '7U0KQC6PGZBNQATNOT', '78AKQCI05U36T3E82O',
            'H1GKQCWOUJHFSHXABA', 'ZWGKQCRFZAPC5PYJZ1', 'EZ0KQCF3LSM9PRSG0K',
            'FHKKQC963NGSY18ZDZ', 'FJ9KQCRJ3RGHNBWW4S', 'S2EKQC9F4UR4R71IC3',
            '1XBKQCX019BKJ0M9IH', 'Z62KQC706L0B0WTN3Q', 'O7EKQCEVZ7FBEWMNWE',
            'XY8KQCULFPN4SR915Q', 'WQDKQCEULSD5G9XNFI', '2Z0KQCSWKVFG7RPFD8',
            '26BKQC0SJIJOH02H2A', '262KQCH2RQKN0CBRLF', 'P5ZJQCMKO7EYV4HFCL',
            'KXBKQC52JO3AP4GMLF', '9IFKQC60JTDBV57N6S', 'TQ0KQCZ8LA7X9DIEAN',
            'BAXJQCORQA5Q46FCDG', 'VR0KQC7LVANO83AL35', '75CKQC4T617U2E5T5Y',
            'LCTKQCZU3F94CEFSOM', 'WJYJQCPNJJI5JN07SD', '3N6KQC6BE5EIXTRMDL',
            'CM5KQCD57I15GKLAMB', 'cccbffffd3e69819cd8',
            'BJKKQCVDA66528PDAU', 'QS0KQCLMIZFI8ZDLM3', 'UW0KQCRHBIYMA8LPZD',
            'GJ7KQC7APJSAMHEK5Q', '711KQCDXOQWB3KDWEP', 'PY0KQC77AJ3457A6C2',
            'WZ0KQCYVMEJHDR4MV2', '28EKQCQGM6NLLWFRG7', 'E33KQCRREJALRA715H',
            '8HKKQCTEJAOBVH410L', 'IO6KQC70PMBQUDNB3L', '1YBKQCWRBNB433NEMH',
            'M01KQCF7KUWCDY67JD', 'CR0KQCOMV2QPPC90IF', '85ZJQCMG38N7Q2WKIK',
            'I9GKQCERACL8UZF2PY', 'BY0KQCOZUK47R2JZDE', '7W0KQCYDMD4LTSY5JL',
            'A0YJQC3HONEKD1JCPK', 'd5839c13b0541b7b8e6',
            ]))

    def test_everyone(self):
        """
        Test Everyone rule.
        """
        rule = Everyone([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_people())

    def test_familywithincompleteevent(self):
        """
        Test FamilyWithIncompleteEvent rule.
        """
        rule = FamilyWithIncompleteEvent([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 775)

    def test_hasalternatename(self):
        """
        Test HasAlternateName rule.
        """
        rule = HasAlternateName([])
        self.assertEqual(self.filter_with_rule(rule), set([
            '46WJQCIOLQ0KOX2XCC', 'GNUJQCL9MD64AM56OH',
            ]))

    def test_commonancestor_empty(self):
        """
        Test empty HasCommonAncestorWith rule.
        """
        rule = HasCommonAncestorWith([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_commonancestor_nonmatching(self):
        """
        Test non-matching HasCommonAncestorWith rule.
        """
        rule = HasCommonAncestorWith(['I0000'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'd5839c1237765987724'
            ]))

    def test_commonancestor_irregular(self):
        """
        Test irregular HasCommonAncestorWith rule.
        """
        rule = HasCommonAncestorWith(['ABCDEFG'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_commonancestor_matching(self):
        """
        Test matching HasCommonAncestorWith rule.
        """
        rule = HasCommonAncestorWith(['I0044'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'GNUJQCL9MD64AM56OH', 'SOFKQCBYAO18OWC0CS', 'EMEKQC02EOUF8H0SHM',
            '3EXJQCVWOSQFGLYB6H', 'EMTJQCQU6TL4WAVSE4', 'QUEKQCZL61S8BJJ388',
            'MKEKQCSBQGAVHAPCQT', 'MUFKQCMXUJ07MCDUNI', 'DBXJQCJCEZMO17WZ89',
            'ORFKQC4KLWEGTGR19L', 'MG5KQC6ZKSVO4A63G2', 'N26KQCF3ASHMZ0HEW6',
            'GNWJQC9NLVF2MZLHU9', 'ZFXJQCHAD8SLZZ7KRP', '44WJQCLCQIPZUB0UH',
            'B8TJQC53HJXOGXK8F7', 'D3WJQCCGV58IP8PNHZ', '3LEKQCRF3FD2E1H73I',
            'F06KQCZY1I4H4IFZM', 'VMTJQC49IGKLG2EQ5', '9BXKQC1PVLPYFMD6IX',
            'H1DKQC4YGZ5A61FGS', '1GWJQCGOOZ8FJW3YK9', 'S16KQCX8XUO3EEL85N',
            'OREKQCF34YE89RL8S6', 'RU5KQCQTPC9SJ5Q1JN', 'GYFKQCPH8Q0JDN94GR',
            '9QFKQC54ET79K2SD57', 'MLEKQCH64557K610VR', 'AWFKQCJELLUWDY2PD3',
            'ZDWJQC7TMS2AWAVF2Y', 'VJFKQCFO7WESWPNKHE', 'LV5KQCJCCR0S3DN5WW',
            'CDTJQCVTVX7CNMY9YU', 'OX5KQCKE3I94MEPDC', 'JF5KQC2L6ABI0MVD3E',
            'CH5KQCIEXSN1J5UEHB', '4JEKQC22K5UTH9QHCU', 'EPFKQCETTDTEL3PYIR',
            'D16KQCIZS56HVPW6DA', '2TEKQCTSCRL4Z2AUHE', '3WEKQCHXRH61E3CIKB',
            'TDTJQCGYRS2RCCGQN3', 'SMWJQCXQ6I2GEXSPK9', 'PXFKQCXEHJX3W1Q1IV',
            'Q9TJQCXDL1599L2B2Z', 'BFXJQCF1JBOXPRW2OS', '6TFKQCUTO94WB2NHN',
            'FNEKQCO239QSNK0R78', '3RFKQCNKMX9HVLNSLW', 'W2DKQCV4H3EZUJ35DX',
            '5IEKQCN37EFBK9EBUD', 'LW5KQCXSXRC2XV3T3D', 'ZNEKQCULV911DIXBK3',
            '35WJQC1B7T7NPV8OLV', 'MPEKQC6TIP3SP1YF7I', 'DMFKQC5MHGYC6503F2',
            '3KEKQC45RL87D4ZG86', 'KLTJQC70XVZJSPQ43U', 'LVEKQCP09W7JNFDAFC',
            'DPUJQCUYKKDPT78JJV', 'JDXJQCR5L0NTR21SQA', 'UAXJQC6HC354V7Q6JA',
            'XBXJQCS4QY316ZGHRN', 'HCXJQCRKB4K65V1C07', '66TJQC6CC7ZWL9YZ64',
            'XNFKQC6DN59LACS9IU', 'LL5KQCG687Y165GL5P', '7X5KQC9ABK4T6AW7QF',
            'HKTJQCIJD8RK9RJFO1', '1LTJQCYQI1DXBLG6Z', '0FWJQCLYEP736P3YZK',
            '0DXJQC1T8P3CQKZIUO', 'ISEKQC97YI74A9VKWC', 'KGXJQCBQ39ON9VB37T',
            'BZ5KQCD4KFI3BTIMZU', '0HEKQCLINMQS4RB7B8', 'BBTJQCNT6N1H4X6TL4',
            'COFKQCUXC2H4G3QBYT', 'DI5KQC3CLKWQI3I0CC', 'T8TJQCWWI8RY57YNTQ',
            '46WJQCIOLQ0KOX2XCC', 'OEXJQCQJHF2BLSAAIS', 'GNFKQCH8AFJRJO9V4Y',
            '8LFKQCQWXTJQJR4CXV', 'IGWJQCSVT8NXTFXOFJ', '3PEKQC8ZDCYTSSIKZ9',
            '5UEKQC8N8NEPSWU1QQ', 'NK5KQC1MAOU2BP35ZV', 'UZFKQCIHVT44DC9KGH',
            'JJ5KQC83DT7VDMUYRQ', '626KQC7C08H3UTM38E', 'XIFKQCLQOY645QTGP7',
            'HEWJQCWQQ3K4BNRLIO', 'HDWJQCT361VOV2PQLP', 'XFKKQCGA4DVECEB48E',
            'KWEKQCTNIIV9BROFFG',
            ]))

    def test_hasnickname(self):
        """
        Test HasNickname rule.
        """
        rule = HasNickname([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'cc8205d883763f02abd', 'GNUJQCL9MD64AM56OH',
            'Q8HKQC3VMRM1M6M7ES',
            ]))

    def test_hasunknowngender(self):
        """
        Test HasUnknownGender rule.
        """
        rule = HasUnknownGender([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'OJOKQC83Y1EDBIMLJ6', '8BHKQCFK9UZFRJYC2Y', 'PGFKQC1TUQMXFAMLMB',
            'IHOKQCECRZYQDKW6KF', '8HKKQCTEJAOBVH410L', 'AGFKQCO358R18LNJYV',
            '1ENKQCBPFZTAQJSP4O', 'NUWKQCO7TVAOH0CHLV', 'P5IKQC88STY3FNTFZ3',
            '7GXKQCMVFU8WR1LKZL', 'LGXKQCJ5OP6MKF9QLN', 'XNFKQC6DN59LACS9IU',
            '7IOKQC1NVGUI1E55CQ', '57PKQCFAWY7AM3JS4M', 'BNXKQCEBXC1RCOGJNF',
            'TFFKQC1RMG8RRADKDH', 'FHKKQC963NGSY18ZDZ', 'WMXKQCDUJ4JKQQYCR7',
            'PBHKQCHOAGTECRKT9L', 'OFXKQC8W0N3N6JP6YQ',
            ]))

    def test_hassourceof_empty(self):
        """
        Test empty HasSourceOf rule.
        """
        # when run with an empty string finds people with no sourc citations
        rule = HasSourceOf([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            'cc82060512042f67e2c', 'cc8205d87831c772e87',
            'cc82060516c6c141500', 'cc8205d87fd529000ff',
            'cc82060504445ab6deb', 'cc8205d887376aacba2',
            'cccbffffd3e69819cd8', 'cc8205d87c20350420b',
            'cc8206050e541f79f92', 'cc8205d883763f02abd',
            'cc8206050980ea622d0', 'cc8205d872f532ab14e',
            'd5839c132b11d9e3632', 'd583a5ba0d50afbbaaf',
            'd5839c1352c64b924d9', 'd583a5b9fc864e3bf4e',
            'd583a5ba1bd083ce4c2', 'd583a5b9df71bceb48c',
            'd583a5b9ced473a7e6a', 'd583a5ba2bc7b9d1388',
            'd5839c12fec09785f6a', 'd5839c1237765987724',
            'd5839c137b3640ad776', 'd5839c126d11a754f46',
            'd5839c12d3b4d5e619b', 'd5839c13380462b246f',
            'd5839c12e9e08301ce2', 'd5839c1366b21411fb4',
            'd5839c13a282b51dd0d', 'd5839c12ac91650a72b',
            'd583a5b9edf6cb5d8d5', 'd583a5ba4be3acdd312',
            'd5839c131d560e06bac', 'd5839c13b0541b7b8e6',
            'd5839c1388e3ab6c87c', 'd583a5ba5ca6b698463',
            'd583a5ba3bc48c2002c', 'd583a5b90777391ea9a',
            ]))

    def test_hassourceof_nonmatching(self):
        """
        Test non-matching HasSourceOf rule.
        """
        rule = HasSourceOf(['S0004'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_hassourceof_irregular(self):
        """
        Test irregular HasSourceOf rule.
        """
        rule = HasSourceOf(['ABCDEFG'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_hassourceof_matching(self):
        """
        Test matching HasSourceOf rule.
        """
        rule = HasSourceOf(['S0000'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'GNUJQCL9MD64AM56OH',
            ]))


    def test_havealtfamilies(self):
        """
        Test HaveAltFamilies rule.
        """
        rule = HaveAltFamilies([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'CH5KQCIEXSN1J5UEHB', 'MG5KQC6ZKSVO4A63G2',
            ]))

    def test_havechildren(self):
        """
        Test HaveChildren rule.
        """
        rule = HaveChildren([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 905)

    def test_incompletenames(self):
        """
        Test IncompleteNames rule.
        """
        rule = IncompleteNames([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'IHOKQCECRZYQDKW6KF', 'cc82060504445ab6deb',
            'LCXKQCQZH5EH56NTCD', 'cc8205d87831c772e87',
            '3RFKQCNKMX9HVLNSLW', 'cc8205d87fd529000ff',
            'B1UKQCBR49WB3134PN', '0TTKQCXXY59OCDPLV3',
            'F3UKQC7ZV3EYVWTZ8O', '1MXKQCJ2BR43910ZYX',
            'cc8206050e541f79f92', 'FHKKQC963NGSY18ZDZ',
            'R5HKQCIEPOY1DMQOWX', 'ZHMKQC50PFVAPI8PZ6', 'T4UKQCYGECXGVNBWMY',
            'cc82060516c6c141500', 'UPWKQCYVFH7RZOSZ29',
            '2AMKQCE67YOH3TBVYI', '2CUKQCFDVN3EZE2E4C', '7IOKQC1NVGUI1E55CQ',
            'KSTKQC018GNA7HDCAS', 'WIVKQC4Q4FCQJT5M63', 'A4YKQCRYSI5FT5T38',
            'BUNKQCO4HZHZP70F3K', 'YRTKQCNDP343OD5OQJ', '7VEKQCV05EDK0625KI',
            'cc8205d872f532ab14e', 'TPXKQCEGL04KHGMO2X',
            'L9LKQCQ8KJRKHM4D2E', '8QXKQCHJ2EUC7OV8EQ', 'W0XKQCKSFWWJWQ2OSN',
            'I6QKQCFRDTV2LDC8M2', 'XTUKQC7WCIVA5F0NC4', 'F4UKQCPK572VWU2YZQ',
            'JKDKQCF4ND92A088J2', 'COFKQCUXC2H4G3QBYT', 'BNXKQCEBXC1RCOGJNF',
            'Q42KQCKJZGS4IZWHF5', 'P5IKQC88STY3FNTFZ3', '7CXKQC59NSZFXIG1UE',
            'cc8205d87c20350420b', 'FQUKQCWEHOAWUP4QWS',
            '3YTKQCK2W63W0MQBJE', '8HKKQCTEJAOBVH410L', 'HLQKQC0BJIZL0V4EK4',
            'B0UKQC9A54F1GUB7NR', 'EPXKQCQRZP2PNPN7BE',
            'cc82060512042f67e2c', 'XZLKQCRQA9EHPBNZPT',
            'OQXKQC2Y5FVH9PK0JL', 'AXLKQC0YTFAWQ234YD', 'OFXKQC8W0N3N6JP6YQ',
            'MWUKQCD2ZSCECQOCLG', '1ENKQCBPFZTAQJSP4O', 'N7XKQCYD3VSCSZREGJ',
            '2LQKQC62GJUQCJIOK8', 'QXXKQC9PT5FWNT140K', 'VAXKQC19HIFPX61J28',
            '0PXKQCJ9S1M3NNASET', 'K8XKQCDSVLSK422A3K', '52UKQCFYXMFTKIGNBS',
            '7GXKQCMVFU8WR1LKZL', '4UMKQCF07KL2K92CI5', 'LGXKQCJ5OP6MKF9QLN',
            'FZTKQCSTPIQ3C9JC46', 'WMXKQCDUJ4JKQQYCR7', 'R6UKQC939L9FV62UGE',
            'OIUKQCBHUWDGL7DNTI', 'FRTKQC3G6JBJAR2ZPX', 'PIEKQCKUL6OAMS8Q9R',
            'cc8205d887376aacba2', 'LGMKQCQP5M5L18FVTN',
            '8HUKQCRV8B3J2LLQ3B', 'LOUKQC45HUN532HOOM',
            'cc8205d883763f02abd', 'TBXKQC7OHIN28PVCS3',
            ]))

    def test_isbookmarked(self):
        """
        Test IsBookmarked rule.
        """
        rule = IsBookmarked([])
        self.assertEqual(self.filter_with_rule(rule), set([
            '35WJQC1B7T7NPV8OLV', 'AWFKQCJELLUWDY2PD3', 'Q8HKQC3VMRM1M6M7ES',
            ]))

    def test_dupancestor_empty(self):
        """
        Test empty IsDuplicatedAncestorOf rule.
        """
        rule = IsDuplicatedAncestorOf([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_dupancestor_nonmatching(self):
        """
        Test non-matching IsDuplicatedAncestorOf rule.
        """
        rule = IsDuplicatedAncestorOf(['I0000'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_dupancestor_irregular(self):
        """
        Test irregular IsDuplicatedAncestorOf rule.
        """
        rule = IsDuplicatedAncestorOf(['ABCDEFG'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_dupancestor_matching(self):
        """
        Test matching IsDuplicatedAncestorOf rule.
        """
        rule = IsDuplicatedAncestorOf(['I1631'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'I3VJQCUY5I6UR92507', 'D4VJQC09STQCWD393E',
            ]))

    def test_isrelatedwith_empty(self):
        """
        Test empty IsRelatedWith rule.
        """
        rule = IsRelatedWith([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_isrelatedwith_nonmatching(self):
        """
        Test non-matching IsRelatedWith rule.
        """
        rule = IsRelatedWith(['I0000'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'd5839c1237765987724', 'd5839c126d11a754f46',
            ]))

    def test_isrelatedwith_irregular(self):
        """
        Test irregular IsRelatedWith rule.
        """
        rule = IsRelatedWith(['ABCDEFG'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_isrelatedwith_matching(self):
        """
        Test matching IsRelatedWith rule.
        """
        rule = IsRelatedWith(['I1844'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'HWTKQCSM28EI6WFDHP', 'T4UKQCYGECXGVNBWMY', 'YOTKQCEX2PLG03LZQS',
            'X8UKQCIDY21QIQBDVI', 'F3UKQC7ZV3EYVWTZ8O', '0TTKQCXXY59OCDPLV3',
            'EVTKQCHV2E2PODFD7C', 'BBUKQC5GPRPDJHJAWU', 'FRTKQC3G6JBJAR2ZPX',
            'NDTKQCN95VFLGJ21L', 'SFTKQC26EJ2BYQCRIA', 'MYTKQCVCFOFM32H9GB',
            'B0UKQC9A54F1GUB7NR', 'PTTKQCYN0JR3ZZJNWR', 'F4UKQCPK572VWU2YZQ',
            'LLTKQCX39KCXFSX0U4', 'IXTKQC1BAU1F1WNXKB', '3YTKQCK2W63W0MQBJE',
            'TQTKQCO897BNA1H93B', 'DOTKQCP1MG3VC8D7V2', '3NTKQCZKLMIM6HYFE1',
            'WUTKQCVQCUPFFOGUT8', 'GETKQCPRC2W5YDUYM6', 'YRTKQCNDP343OD5OQJ',
            'U0UKQCBZS0R6WW7LBS', 'J2UKQC897I42M9VHDD', '7MTKQC1QNE4H5RF35S',
            '5FTKQCKT9SDZ8TB03C', 'O1UKQCJD5YHDRW887V', 'EUTKQCFATXRU431YY6',
            'UHTKQCORH3NTZ0FYL3', '2CUKQCFDVN3EZE2E4C', 'RNTKQCMLGRRKQVKDPR',
            'CGTKQC4WO8W3WSQRCX', 'WAUKQCOQ91QCJZWQ9U', 'FZTKQCSTPIQ3C9JC46',
            'AHTKQCM2YFRW3AGSRL', 'WBTKQCC775IAAGIWZD', '8KTKQC407A8CN5O68H',
            '8QTKQCN8ZKY5OWWJZF', 'UKTKQCSL3AUJIWTD2A', 'HAUKQCM3GYGVTREGZS',
            '52UKQCFYXMFTKIGNBS', 'U3UKQCO30PWAK6JQBA', 'R6UKQC939L9FV62UGE',
            'TZTKQCR39A060AQ63C', 'X9UKQCFELSDAQ2TDP1', 'B1UKQCBR49WB3134PN',
            'KSTKQC018GNA7HDCAS', 'FJTKQCJCMAHJOA9NHI', 'HITKQCWJSCZX2AN6NP',
            'WVTKQCZC91I63LHEE7', '0DTKQC6KBOS69LQJ35',
            ]))

    def test_hasidof_empty(self):
        """
        Test empty HasIdOf rule.
        """
        rule = HasIdOf([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_hasidof_nonmatching(self):
        """
        Test non-matching HasIdOf rule.
        """
        rule = HasIdOf(['I0000'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'd5839c1237765987724'
            ]))

    def test_hasidof_irregular(self):
        """
        Test irregular HasIdOf rule.
        """
        rule = HasIdOf(['ABCDEFG'])
        self.assertEqual(self.filter_with_rule(rule), set([
            ]))

    def test_hasidof_matching(self):
        """
        Test matching HasIdOf rule.
        """
        rule = HasIdOf(['I0044'])
        self.assertEqual(self.filter_with_rule(rule), set([
            'GNUJQCL9MD64AM56OH',
            ]))

    def test_isdefaultperson(self):
        """
        Test IsDefaultPerson rule.
        """
        rule = IsDefaultPerson([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'GNUJQCL9MD64AM56OH',
            ]))

    def test_isfemale(self):
        """
        Test IsFemale rule.
        """
        rule = IsFemale([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 940)

    def test_ismale(self):
        """
        Test IsMale rule.
        """
        rule = IsMale([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 1168)

    def test_missingparent(self):
        """
        Test MissingParent rule.
        """
        rule = MissingParent([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 868)

    def test_multiplemarriages(self):
        """
        Test MultipleMarriages rule.
        """
        rule = MultipleMarriages([])
        self.assertEqual(self.filter_with_rule(rule), set([
            'R1VKQCJWNP24VN7BO', 'ZTVJQCTSMI85EGMXFM', 'ENTJQCZXQV1IRKJXUL',
            '44WJQCLCQIPZUB0UH', 'SMWJQCXQ6I2GEXSPK9', 'DN3KQC1URTED410L3R',
            '5FYJQC86G8EZ0L4E4B', '5F4KQCJRU8ZKL6SILT', '0YNKQC5U4EQGVNUZD8',
            'YRYJQCE3RF4U8A59UB', 'APWKQCI6YXAXBLC33I', 'XSKKQC6GGKLAYANWAF',
            '0FQKQCOQD0VRVJPTSD', 'B3UJQCZHDXII99AWW4',
            'cc8205d872f532ab14e', 'SS1KQCWWF9488Q330U',
            'OCYJQCS8YT7JO8KIMO', 'I6HKQCQF72V2N56JQ5', '6YWJQC86FBVN0J6JS',
            'KYNKQCVA6FE65ONFIQ', 'SHAKQCNY5IXO30GUAB', 'O5XKQC3V6BPJI13J24',
            'ZN7KQC3RLB82EXF1QF', 'CIYJQCF3UK12DL0S2Y', 'H3XJQCFJ4FP4U2WGZC',
            'cc82060504445ab6deb', '4E4KQC1K4XUEX29IJO',
            '0XVJQCJUNJY40WDSMA', '1WUJQCHNH76G6YD3A', 'IH3KQCM1VZPRKLBLK7',
            '242KQCBALBOD8ZK5VI', '8G4KQCS6C1AOM6ZGR3', 'I1EKQCGGDSUD8ILUW4',
            'X8BKQCSFF4AET5MY23', 'RJWJQCN1XKXRN5KMCP', 'ZWNKQC9DAZ3C6UHUAV',
            '9QUJQCCSWRZNSAPCR', 'HI0KQCG9TGT5AAIPU', 'DI4KQC3S1AO27VWOLN',
            'QBDKQCH2IU6N8IXMFE', 'DK2KQCJYW14VXUJ85', '117KQCBB32RMTTV4G6',
            '0QLKQCFTQMNVGCV4GM', 'D2OKQCGDNPT3BH4WH', 'CAYJQCKOL49OF7XWB3',
            'ZQGKQCGHS67Q4IMHEG', 'OEXJQCQJHF2BLSAAIS', 'UKYJQC70LIZQ11BP89',
            'FF2KQCRBSPCG1QY97', 'L6EKQCO8QYL2UO2MQO',
            ]))

    def test_nevermarried(self):
        """
        Test NeverMarried rule.
        """
        rule = NeverMarried([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 751)

    def test_nobirthdate(self):
        """
        Test NoBirthdate rule.
        """
        rule = NoBirthdate([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 981)

    def test_nodeathdate(self):
        """
        Test NoDeathdate rule.
        """
        rule = NoDeathdate([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 1603)

    def test_peopleprivate(self):
        """
        Test PeoplePrivate rule.
        """
        # TODO: example.gramps has no people marked private
        rule = PeoplePrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_peoplepublic(self):
        """
        Test PeoplePublic rule.
        """
        rule = PeoplePublic([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 2128)

    def test_personwithincompleteevent(self):
        """
        Test PersonWithIncompleteEvent rule.
        """
        rule = PersonWithIncompleteEvent([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 745)

    def test_relationshipbookmarks(self):
        """
        Test RelationshipPathBetweenBookmarks rule.
        """
        rule = RelationshipPathBetweenBookmarks([])
        self.assertEqual(self.filter_with_rule(rule), set([
            '44WJQCLCQIPZUB0UH', '35WJQC1B7T7NPV8OLV', 'AWFKQCJELLUWDY2PD3',
            'D3WJQCCGV58IP8PNHZ', 'Q8HKQC3VMRM1M6M7ES',
            ]))

    def test_hassoundexname(self):
        """
        Test HasSoundexName rule.
        """
        rule = HasSoundexName(['garner'])
        self.assertEqual(len(self.filter_with_rule(rule)), 73)

    def test_hasnameof(self):
        """
        Test HasNameOf rule.
        """
        rule = HasNameOf(['Lewis', 'Garner', 'Dr.', 'Sr', 'Anderson',
                          'Big Louie', 'von', 'Zieliński', None, None, None])
        self.assertEqual(self.filter_with_rule(rule), set([
            'GNUJQCL9MD64AM56OH']))


if __name__ == "__main__":
    unittest.main()
