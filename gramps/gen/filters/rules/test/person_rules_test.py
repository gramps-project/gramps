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

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilter

from gramps.gen.filters.rules.person import (
    Disconnected, Everyone, FamilyWithIncompleteEvent, HasAlternateName,
    HasCommonAncestorWith, HasNickname, HasUnknownGender, HasSourceOf,
    HaveAltFamilies, HaveChildren, IncompleteNames, IsBookmarked,
    IsDuplicatedAncestorOf, IsRelatedWith, HasIdOf, IsDefaultPerson, IsFemale,
    IsMale, MissingParent, MultipleMarriages, NeverMarried, NoBirthdate,
    NoDeathdate, PeoplePrivate, PeoplePublic, PersonWithIncompleteEvent,
    RelationshipPathBetweenBookmarks)

class BaseTest(unittest.TestCase):
    """
    Person rule tests.
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
        filter_ = GenericFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_disconnected(self):
        """
        Test Disconnected rule.
        """
        rule = Disconnected([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'0PBKQCXHLAEIB46ZIA', b'QEVJQC04YO01UAWJ2N', b'UT0KQCMN7PC9XURRXJ',
            b'MZAKQCKAQLIQYWP5IW', b'Y7BKQC9CUXWQLGLPQM', b'OBBKQC8NJM5UYBO849',
            b'NPBKQCKEF0G7T4H312', b'423KQCGLT8UISDUM1Q', b'8S0KQCNORIWDL0X8SB',
            b'AP5KQC0LBXPM727OWB', b'AREKQC0VPBHNZ5R3IO', b'KU0KQCJ0RUTJTIUKSA',
            b'VC4KQC7L7KKH9RLHXN', b'0P3KQCRSIVL1A4VJ19', b'PK6KQCGEL4PTE720BL',
            b'YIKKQCSD2Z85UHJ8LX', b'KY8KQCMIH2HUUGLA3R', b'RD7KQCQ24B1N3OEC5X',
            b'NV0KQC7SIEH3SVDPP1', b'KIKKQCU2CJ543TLM5J', b'AT0KQC4P3MMUCHI3BK',
            b'J6BKQC1PMNBAYSLM9U', b'IXXJQCLKOUAJ5RSQY4', b'U4ZJQC5VR0QBIE8DU',
            b'F7BKQC4NXO9R7XOG2W', b'7U0KQC6PGZBNQATNOT', b'78AKQCI05U36T3E82O',
            b'H1GKQCWOUJHFSHXABA', b'ZWGKQCRFZAPC5PYJZ1', b'EZ0KQCF3LSM9PRSG0K',
            b'FHKKQC963NGSY18ZDZ', b'FJ9KQCRJ3RGHNBWW4S', b'S2EKQC9F4UR4R71IC3',
            b'1XBKQCX019BKJ0M9IH', b'Z62KQC706L0B0WTN3Q', b'O7EKQCEVZ7FBEWMNWE',
            b'XY8KQCULFPN4SR915Q', b'WQDKQCEULSD5G9XNFI', b'2Z0KQCSWKVFG7RPFD8',
            b'26BKQC0SJIJOH02H2A', b'262KQCH2RQKN0CBRLF', b'P5ZJQCMKO7EYV4HFCL',
            b'KXBKQC52JO3AP4GMLF', b'9IFKQC60JTDBV57N6S', b'TQ0KQCZ8LA7X9DIEAN',
            b'BAXJQCORQA5Q46FCDG', b'VR0KQC7LVANO83AL35', b'75CKQC4T617U2E5T5Y',
            b'LCTKQCZU3F94CEFSOM', b'WJYJQCPNJJI5JN07SD', b'3N6KQC6BE5EIXTRMDL',
            b'CM5KQCD57I15GKLAMB', b'cccbffffd3e69819cd8',
            b'BJKKQCVDA66528PDAU', b'QS0KQCLMIZFI8ZDLM3', b'UW0KQCRHBIYMA8LPZD',
            b'GJ7KQC7APJSAMHEK5Q', b'711KQCDXOQWB3KDWEP', b'PY0KQC77AJ3457A6C2',
            b'WZ0KQCYVMEJHDR4MV2', b'28EKQCQGM6NLLWFRG7', b'E33KQCRREJALRA715H',
            b'8HKKQCTEJAOBVH410L', b'IO6KQC70PMBQUDNB3L', b'1YBKQCWRBNB433NEMH',
            b'M01KQCF7KUWCDY67JD', b'CR0KQCOMV2QPPC90IF', b'85ZJQCMG38N7Q2WKIK',
            b'I9GKQCERACL8UZF2PY', b'BY0KQCOZUK47R2JZDE', b'7W0KQCYDMD4LTSY5JL',
            b'A0YJQC3HONEKD1JCPK',
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
            b'46WJQCIOLQ0KOX2XCC', b'GNUJQCL9MD64AM56OH',
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
            b'GNUJQCL9MD64AM56OH', b'SOFKQCBYAO18OWC0CS', b'EMEKQC02EOUF8H0SHM',
            b'3EXJQCVWOSQFGLYB6H', b'EMTJQCQU6TL4WAVSE4', b'QUEKQCZL61S8BJJ388',
            b'MKEKQCSBQGAVHAPCQT', b'MUFKQCMXUJ07MCDUNI', b'DBXJQCJCEZMO17WZ89',
            b'ORFKQC4KLWEGTGR19L', b'MG5KQC6ZKSVO4A63G2', b'N26KQCF3ASHMZ0HEW6',
            b'GNWJQC9NLVF2MZLHU9', b'ZFXJQCHAD8SLZZ7KRP', b'44WJQCLCQIPZUB0UH',
            b'B8TJQC53HJXOGXK8F7', b'D3WJQCCGV58IP8PNHZ', b'3LEKQCRF3FD2E1H73I',
            b'F06KQCZY1I4H4IFZM', b'VMTJQC49IGKLG2EQ5', b'9BXKQC1PVLPYFMD6IX',
            b'H1DKQC4YGZ5A61FGS', b'1GWJQCGOOZ8FJW3YK9', b'S16KQCX8XUO3EEL85N',
            b'OREKQCF34YE89RL8S6', b'RU5KQCQTPC9SJ5Q1JN', b'GYFKQCPH8Q0JDN94GR',
            b'9QFKQC54ET79K2SD57', b'MLEKQCH64557K610VR', b'AWFKQCJELLUWDY2PD3',
            b'ZDWJQC7TMS2AWAVF2Y', b'VJFKQCFO7WESWPNKHE', b'LV5KQCJCCR0S3DN5WW',
            b'CDTJQCVTVX7CNMY9YU', b'OX5KQCKE3I94MEPDC', b'JF5KQC2L6ABI0MVD3E',
            b'CH5KQCIEXSN1J5UEHB', b'4JEKQC22K5UTH9QHCU', b'EPFKQCETTDTEL3PYIR',
            b'D16KQCIZS56HVPW6DA', b'2TEKQCTSCRL4Z2AUHE', b'3WEKQCHXRH61E3CIKB',
            b'TDTJQCGYRS2RCCGQN3', b'SMWJQCXQ6I2GEXSPK9', b'PXFKQCXEHJX3W1Q1IV',
            b'Q9TJQCXDL1599L2B2Z', b'BFXJQCF1JBOXPRW2OS', b'6TFKQCUTO94WB2NHN',
            b'FNEKQCO239QSNK0R78', b'3RFKQCNKMX9HVLNSLW', b'W2DKQCV4H3EZUJ35DX',
            b'5IEKQCN37EFBK9EBUD', b'LW5KQCXSXRC2XV3T3D', b'ZNEKQCULV911DIXBK3',
            b'35WJQC1B7T7NPV8OLV', b'MPEKQC6TIP3SP1YF7I', b'DMFKQC5MHGYC6503F2',
            b'3KEKQC45RL87D4ZG86', b'KLTJQC70XVZJSPQ43U', b'LVEKQCP09W7JNFDAFC',
            b'DPUJQCUYKKDPT78JJV', b'JDXJQCR5L0NTR21SQA', b'UAXJQC6HC354V7Q6JA',
            b'XBXJQCS4QY316ZGHRN', b'HCXJQCRKB4K65V1C07', b'66TJQC6CC7ZWL9YZ64',
            b'XNFKQC6DN59LACS9IU', b'LL5KQCG687Y165GL5P', b'7X5KQC9ABK4T6AW7QF',
            b'HKTJQCIJD8RK9RJFO1', b'1LTJQCYQI1DXBLG6Z', b'0FWJQCLYEP736P3YZK',
            b'0DXJQC1T8P3CQKZIUO', b'ISEKQC97YI74A9VKWC', b'KGXJQCBQ39ON9VB37T',
            b'BZ5KQCD4KFI3BTIMZU', b'0HEKQCLINMQS4RB7B8', b'BBTJQCNT6N1H4X6TL4',
            b'COFKQCUXC2H4G3QBYT', b'DI5KQC3CLKWQI3I0CC', b'T8TJQCWWI8RY57YNTQ',
            b'46WJQCIOLQ0KOX2XCC', b'OEXJQCQJHF2BLSAAIS', b'GNFKQCH8AFJRJO9V4Y',
            b'8LFKQCQWXTJQJR4CXV', b'IGWJQCSVT8NXTFXOFJ', b'3PEKQC8ZDCYTSSIKZ9',
            b'5UEKQC8N8NEPSWU1QQ', b'NK5KQC1MAOU2BP35ZV', b'UZFKQCIHVT44DC9KGH',
            b'JJ5KQC83DT7VDMUYRQ', b'626KQC7C08H3UTM38E', b'XIFKQCLQOY645QTGP7',
            b'HEWJQCWQQ3K4BNRLIO', b'HDWJQCT361VOV2PQLP', b'XFKKQCGA4DVECEB48E',
            b'KWEKQCTNIIV9BROFFG',
            ]))

    def test_hasnickname(self):
        """
        Test HasNickname rule.
        """
        rule = HasNickname([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'cc8205d883763f02abd', b'GNUJQCL9MD64AM56OH',
            b'Q8HKQC3VMRM1M6M7ES',
            ]))

    def test_hasunknowngender(self):
        """
        Test HasUnknownGender rule.
        """
        rule = HasUnknownGender([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'OJOKQC83Y1EDBIMLJ6', b'8BHKQCFK9UZFRJYC2Y', b'PGFKQC1TUQMXFAMLMB',
            b'IHOKQCECRZYQDKW6KF', b'8HKKQCTEJAOBVH410L', b'AGFKQCO358R18LNJYV',
            b'1ENKQCBPFZTAQJSP4O', b'NUWKQCO7TVAOH0CHLV', b'P5IKQC88STY3FNTFZ3',
            b'7GXKQCMVFU8WR1LKZL', b'LGXKQCJ5OP6MKF9QLN', b'XNFKQC6DN59LACS9IU',
            b'7IOKQC1NVGUI1E55CQ', b'57PKQCFAWY7AM3JS4M', b'BNXKQCEBXC1RCOGJNF',
            b'TFFKQC1RMG8RRADKDH', b'FHKKQC963NGSY18ZDZ', b'WMXKQCDUJ4JKQQYCR7',
            b'PBHKQCHOAGTECRKT9L', b'OFXKQC8W0N3N6JP6YQ',
            ]))

    def test_hassourceof_empty(self):
        """
        Test empty HasSourceOf rule.
        """
        # when run with an empty string finds people with no sourc citations
        rule = HasSourceOf([''])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'cc82060512042f67e2c', b'cc8205d87831c772e87',
            b'cc82060516c6c141500', b'cc8205d87fd529000ff',
            b'cc82060504445ab6deb', b'cc8205d887376aacba2',
            b'cccbffffd3e69819cd8', b'cc8205d87c20350420b',
            b'cc8206050e541f79f92', b'cc8205d883763f02abd',
            b'cc8206050980ea622d0', b'cc8205d872f532ab14e',
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
            b'GNUJQCL9MD64AM56OH',
            ]))


    def test_havealtfamilies(self):
        """
        Test HaveAltFamilies rule.
        """
        rule = HaveAltFamilies([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'CH5KQCIEXSN1J5UEHB', b'MG5KQC6ZKSVO4A63G2',
            ]))

    def test_havechildren(self):
        """
        Test HaveChildren rule.
        """
        rule = HaveChildren([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 895)

    def test_incompletenames(self):
        """
        Test IncompleteNames rule.
        """
        rule = IncompleteNames([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'IHOKQCECRZYQDKW6KF', b'cc82060504445ab6deb',
            b'LCXKQCQZH5EH56NTCD', b'cc8205d87831c772e87',
            b'3RFKQCNKMX9HVLNSLW', b'cc8205d87fd529000ff',
            b'B1UKQCBR49WB3134PN', b'0TTKQCXXY59OCDPLV3',
            b'F3UKQC7ZV3EYVWTZ8O', b'1MXKQCJ2BR43910ZYX',
            b'cc8206050e541f79f92', b'FHKKQC963NGSY18ZDZ',
            b'R5HKQCIEPOY1DMQOWX', b'ZHMKQC50PFVAPI8PZ6', b'T4UKQCYGECXGVNBWMY',
            b'cc82060516c6c141500', b'UPWKQCYVFH7RZOSZ29',
            b'2AMKQCE67YOH3TBVYI', b'2CUKQCFDVN3EZE2E4C', b'7IOKQC1NVGUI1E55CQ',
            b'KSTKQC018GNA7HDCAS', b'WIVKQC4Q4FCQJT5M63', b'A4YKQCRYSI5FT5T38',
            b'BUNKQCO4HZHZP70F3K', b'YRTKQCNDP343OD5OQJ', b'7VEKQCV05EDK0625KI',
            b'cc8205d872f532ab14e', b'TPXKQCEGL04KHGMO2X',
            b'L9LKQCQ8KJRKHM4D2E', b'8QXKQCHJ2EUC7OV8EQ', b'W0XKQCKSFWWJWQ2OSN',
            b'I6QKQCFRDTV2LDC8M2', b'XTUKQC7WCIVA5F0NC4', b'F4UKQCPK572VWU2YZQ',
            b'JKDKQCF4ND92A088J2', b'COFKQCUXC2H4G3QBYT', b'BNXKQCEBXC1RCOGJNF',
            b'Q42KQCKJZGS4IZWHF5', b'P5IKQC88STY3FNTFZ3', b'7CXKQC59NSZFXIG1UE',
            b'cc8205d87c20350420b', b'FQUKQCWEHOAWUP4QWS',
            b'3YTKQCK2W63W0MQBJE', b'8HKKQCTEJAOBVH410L', b'HLQKQC0BJIZL0V4EK4',
            b'B0UKQC9A54F1GUB7NR', b'EPXKQCQRZP2PNPN7BE',
            b'cc82060512042f67e2c', b'XZLKQCRQA9EHPBNZPT',
            b'OQXKQC2Y5FVH9PK0JL', b'AXLKQC0YTFAWQ234YD', b'OFXKQC8W0N3N6JP6YQ',
            b'MWUKQCD2ZSCECQOCLG', b'1ENKQCBPFZTAQJSP4O', b'N7XKQCYD3VSCSZREGJ',
            b'2LQKQC62GJUQCJIOK8', b'QXXKQC9PT5FWNT140K', b'VAXKQC19HIFPX61J28',
            b'0PXKQCJ9S1M3NNASET', b'K8XKQCDSVLSK422A3K', b'52UKQCFYXMFTKIGNBS',
            b'7GXKQCMVFU8WR1LKZL', b'4UMKQCF07KL2K92CI5', b'LGXKQCJ5OP6MKF9QLN',
            b'FZTKQCSTPIQ3C9JC46', b'WMXKQCDUJ4JKQQYCR7', b'R6UKQC939L9FV62UGE',
            b'OIUKQCBHUWDGL7DNTI', b'FRTKQC3G6JBJAR2ZPX', b'PIEKQCKUL6OAMS8Q9R',
            b'cc8205d887376aacba2', b'LGMKQCQP5M5L18FVTN',
            b'8HUKQCRV8B3J2LLQ3B', b'LOUKQC45HUN532HOOM',
            b'cc8205d883763f02abd', b'TBXKQC7OHIN28PVCS3',
            ]))

    def test_isbookmarked(self):
        """
        Test IsBookmarked rule.
        """
        rule = IsBookmarked([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'35WJQC1B7T7NPV8OLV', b'AWFKQCJELLUWDY2PD3', b'Q8HKQC3VMRM1M6M7ES',
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
            b'I3VJQCUY5I6UR92507', b'D4VJQC09STQCWD393E',
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
            b'HWTKQCSM28EI6WFDHP', b'T4UKQCYGECXGVNBWMY', b'YOTKQCEX2PLG03LZQS',
            b'X8UKQCIDY21QIQBDVI', b'F3UKQC7ZV3EYVWTZ8O', b'0TTKQCXXY59OCDPLV3',
            b'EVTKQCHV2E2PODFD7C', b'BBUKQC5GPRPDJHJAWU', b'FRTKQC3G6JBJAR2ZPX',
            b'NDTKQCN95VFLGJ21L', b'SFTKQC26EJ2BYQCRIA', b'MYTKQCVCFOFM32H9GB',
            b'B0UKQC9A54F1GUB7NR', b'PTTKQCYN0JR3ZZJNWR', b'F4UKQCPK572VWU2YZQ',
            b'LLTKQCX39KCXFSX0U4', b'IXTKQC1BAU1F1WNXKB', b'3YTKQCK2W63W0MQBJE',
            b'TQTKQCO897BNA1H93B', b'DOTKQCP1MG3VC8D7V2', b'3NTKQCZKLMIM6HYFE1',
            b'WUTKQCVQCUPFFOGUT8', b'GETKQCPRC2W5YDUYM6', b'YRTKQCNDP343OD5OQJ',
            b'U0UKQCBZS0R6WW7LBS', b'J2UKQC897I42M9VHDD', b'7MTKQC1QNE4H5RF35S',
            b'5FTKQCKT9SDZ8TB03C', b'O1UKQCJD5YHDRW887V', b'EUTKQCFATXRU431YY6',
            b'UHTKQCORH3NTZ0FYL3', b'2CUKQCFDVN3EZE2E4C', b'RNTKQCMLGRRKQVKDPR',
            b'CGTKQC4WO8W3WSQRCX', b'WAUKQCOQ91QCJZWQ9U', b'FZTKQCSTPIQ3C9JC46',
            b'AHTKQCM2YFRW3AGSRL', b'WBTKQCC775IAAGIWZD', b'8KTKQC407A8CN5O68H',
            b'8QTKQCN8ZKY5OWWJZF', b'UKTKQCSL3AUJIWTD2A', b'HAUKQCM3GYGVTREGZS',
            b'52UKQCFYXMFTKIGNBS', b'U3UKQCO30PWAK6JQBA', b'R6UKQC939L9FV62UGE',
            b'TZTKQCR39A060AQ63C', b'X9UKQCFELSDAQ2TDP1', b'B1UKQCBR49WB3134PN',
            b'KSTKQC018GNA7HDCAS', b'FJTKQCJCMAHJOA9NHI', b'HITKQCWJSCZX2AN6NP',
            b'WVTKQCZC91I63LHEE7', b'0DTKQC6KBOS69LQJ35',
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
            b'GNUJQCL9MD64AM56OH',
            ]))

    def test_isdefaultperson(self):
        """
        Test IsDefaultPerson rule.
        """
        rule = IsDefaultPerson([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'GNUJQCL9MD64AM56OH',
            ]))

    def test_isfemale(self):
        """
        Test IsFemale rule.
        """
        rule = IsFemale([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 928)

    def test_ismale(self):
        """
        Test IsMale rule.
        """
        rule = IsMale([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 1154)

    def test_missingparent(self):
        """
        Test MissingParent rule.
        """
        rule = MissingParent([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 849)

    def test_multiplemarriages(self):
        """
        Test MultipleMarriages rule.
        """
        rule = MultipleMarriages([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'R1VKQCJWNP24VN7BO', b'ZTVJQCTSMI85EGMXFM', b'ENTJQCZXQV1IRKJXUL',
            b'44WJQCLCQIPZUB0UH', b'SMWJQCXQ6I2GEXSPK9', b'DN3KQC1URTED410L3R',
            b'5FYJQC86G8EZ0L4E4B', b'5F4KQCJRU8ZKL6SILT', b'0YNKQC5U4EQGVNUZD8',
            b'YRYJQCE3RF4U8A59UB', b'APWKQCI6YXAXBLC33I', b'XSKKQC6GGKLAYANWAF',
            b'0FQKQCOQD0VRVJPTSD', b'B3UJQCZHDXII99AWW4',
            b'cc8205d872f532ab14e', b'SS1KQCWWF9488Q330U',
            b'OCYJQCS8YT7JO8KIMO', b'I6HKQCQF72V2N56JQ5', b'6YWJQC86FBVN0J6JS',
            b'KYNKQCVA6FE65ONFIQ', b'SHAKQCNY5IXO30GUAB', b'O5XKQC3V6BPJI13J24',
            b'ZN7KQC3RLB82EXF1QF', b'CIYJQCF3UK12DL0S2Y', b'H3XJQCFJ4FP4U2WGZC',
            b'cc82060504445ab6deb', b'4E4KQC1K4XUEX29IJO',
            b'0XVJQCJUNJY40WDSMA', b'1WUJQCHNH76G6YD3A', b'IH3KQCM1VZPRKLBLK7',
            b'242KQCBALBOD8ZK5VI', b'8G4KQCS6C1AOM6ZGR3', b'I1EKQCGGDSUD8ILUW4',
            b'X8BKQCSFF4AET5MY23', b'RJWJQCN1XKXRN5KMCP', b'ZWNKQC9DAZ3C6UHUAV',
            b'9QUJQCCSWRZNSAPCR', b'HI0KQCG9TGT5AAIPU', b'DI4KQC3S1AO27VWOLN',
            b'QBDKQCH2IU6N8IXMFE', b'DK2KQCJYW14VXUJ85', b'117KQCBB32RMTTV4G6',
            b'0QLKQCFTQMNVGCV4GM', b'D2OKQCGDNPT3BH4WH', b'CAYJQCKOL49OF7XWB3',
            b'ZQGKQCGHS67Q4IMHEG', b'OEXJQCQJHF2BLSAAIS', b'UKYJQC70LIZQ11BP89',
            b'FF2KQCRBSPCG1QY97', b'L6EKQCO8QYL2UO2MQO',
            ]))

    def test_nevermarried(self):
        """
        Test NeverMarried rule.
        """
        rule = NeverMarried([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 749)

    def test_nobirthdate(self):
        """
        Test NoBirthdate rule.
        """
        rule = NoBirthdate([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 966)

    def test_nodeathdate(self):
        """
        Test NoDeathdate rule.
        """
        rule = NoDeathdate([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 1581)

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
        self.assertEqual(len(self.filter_with_rule(rule)), 2102)

    def test_personwithincompleteevent(self):
        """
        Test PersonWithIncompleteEvent rule.
        """
        rule = PersonWithIncompleteEvent([])
        # too many to list out to test explicitly
        self.assertEqual(len(self.filter_with_rule(rule)), 740)

    def test_relationshipbookmarks(self):
        """
        Test RelationshipPathBetweenBookmarks rule.
        """
        rule = RelationshipPathBetweenBookmarks([])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'44WJQCLCQIPZUB0UH', b'35WJQC1B7T7NPV8OLV', b'AWFKQCJELLUWDY2PD3',
            b'D3WJQCCGV58IP8PNHZ', b'Q8HKQC3VMRM1M6M7ES',
            ]))


if __name__ == "__main__":
    unittest.main()
