# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013  Vassilii Khachaturov
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

import unittest
import sys

try:
    if sys.version_info < (3,3):
        from mock import Mock
    else:
        from unittest.mock import Mock

    MOCKING = True

except:
    MOCKING = False
    print ("Mocking disabled, some testing skipped", sys.exc_info()[0:2])

class LexGettextTest(unittest.TestCase):
    SRC_WORD = "Inflect-me"
    MSGID = "how-to-use-lexgettext||" + SRC_WORD

    def setUp(self):
        from ..grampslocale import GrampsTranslations
        from ..grampslocale import GrampsLocale as Loc
        self.trans = GrampsTranslations()

    def setup_sgettext_mock(self, msgval_expected):
        if MOCKING:
            mock = Mock(return_value=msgval_expected)
        else:
            mock = lambda msgid: msgval_expected
        self.trans.sgettext = mock

    def tearDown(self):
        if MOCKING:
            try:
                self.trans.sgettext.assert_called_once_with(
                        self.MSGID)
            except AttributeError as e:
                print ("Apparently the test has never set up the mock: ", e)

    def testSrcWordOnlyIfNoTranslation(self):
        self.setup_sgettext_mock(self.SRC_WORD)
        result = self.trans.lexgettext(self.MSGID)
        self.assertEqual(result, self.SRC_WORD)

    def test3InflectionsExtractableByNameThroughForm(self):
        translated = "n=TargetNom|g=TargetGen|d=TargetDat"
        self.setup_sgettext_mock(translated)
        lex = self.trans.lexgettext(self.MSGID)
        formatted = "{lex.f[n]},{lex.f[g]},{lex.f[d]}".format(lex=lex)
        self.assertEqual(formatted, "TargetNom,TargetGen,TargetDat")

    def testFirstLexemeFormExtractableAsDefaultString(self):
        translated = "def=Default|v1=Option1|a=AnotherOption"
        self.setup_sgettext_mock(translated)
        lex = self.trans.lexgettext(self.MSGID)
        formatted = "{}".format(lex)
        self.assertEqual(formatted, "Default")

class LexemeTest(unittest.TestCase):
    def setUp(self):
        from ..grampslocale import Lexeme
        self.lex = Lexeme((('a', 'aaa'), ('b', 'bbb'), ('c', 'ccc')))
        self.zlex = Lexeme({'z' : 'zzz'})
        self.elex = Lexeme({})

    def testIsHashable(self):
        hash(self.lex) # throws if not hashable

    # test delegation to an arbitrary string method pulled in from unicode
    def testDefaultStringStartsWithAA(self):
        self.assertTrue(self.lex.startswith('aa'),
                msg="default string: {} dict: {}".format(
                    self.lex, self.lex.__dict__))

    def testCanConcatenateStringAndLexeme(self):
        moo = "moo"
        self.assertEqual(moo + self.lex, "mooaaa")

    def testCanConcatenateStringAndLexemeInPlace(self):
        moo = "moo"
        moo += self.lex
        self.assertEqual(moo, "mooaaa")

    def testCanConcatenateLexemeAndStringInPlace(self):
        moo = "moo"
        self.lex += moo
        self.assertEqual(self.lex, "aaamoo")

    def testCanConcatenateTwoLexemes(self):
        aaazzz = self.lex + self.zlex
        self.assertEqual(aaazzz, "aaazzz")

    def testCanJoinTwoLexemes(self):
        aaa_zzz = "_".join([self.lex,self.zlex])
        self.assertEqual(aaa_zzz, "aaa_zzz")

    def testEmptyIterableLikeEmptyString(self):
        self.assertEqual(self.elex, "")

if __name__ == "__main__":
    unittest.main()
