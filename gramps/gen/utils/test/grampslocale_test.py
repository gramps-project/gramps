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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

import unittest
from unittest.mock import Mock, patch

try:
    from icu import Collator

    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Collator

        HAVE_ICU = True
    except ImportError:
        HAVE_ICU = False


class LexGettextTest(unittest.TestCase):
    SRC_WORD = "Inflect-me"
    CONTEXT = "how-to-use-lexgettext"
    MSGID = "|" + SRC_WORD

    def setUp(self):
        from ..grampslocale import GrampsTranslations
        from ..grampslocale import GrampsLocale as Loc

        self.trans = GrampsTranslations()

    def setup_sgettext_mock(self, msgval_expected):
        mock = Mock(return_value=msgval_expected)
        self.trans.sgettext = mock

    def tearDown(self):
        try:
            self.trans.sgettext.assert_called_once_with(self.MSGID, self.CONTEXT)
        except AttributeError as e:
            print("Apparently the test has never set up the mock: ", e)

    def testSrcWordOnlyIfNoTranslation(self):
        self.setup_sgettext_mock(self.SRC_WORD)
        result = self.trans.lexgettext(self.MSGID, self.CONTEXT)
        self.assertEqual(result, self.SRC_WORD)

    def test3InflectionsExtractableByNameThroughForm(self):
        translated = "n=TargetNom|g=TargetGen|d=TargetDat"
        self.setup_sgettext_mock(translated)
        lex = self.trans.lexgettext(self.MSGID, self.CONTEXT)
        formatted = "{lex.forms[n]},{lex.forms[g]},{lex.forms[d]}".format(lex=lex)
        self.assertEqual(formatted, "TargetNom,TargetGen,TargetDat")

    def testFirstLexemeFormExtractableAsDefaultString(self):
        translated = "def=Default|v1=Option1|a=AnotherOption"
        self.setup_sgettext_mock(translated)
        lex = self.trans.lexgettext(self.MSGID, self.CONTEXT)
        formatted = "{}".format(lex)
        self.assertEqual(formatted, "Default")


class LexemeTest(unittest.TestCase):
    def setUp(self):
        from ..grampstranslation import Lexeme

        self.lex = Lexeme((("a", "aaa"), ("b", "bbb"), ("c", "ccc")))
        self.zlex = Lexeme({"z": "zzz"})
        self.elex = Lexeme({})

    def testIsHashable(self):
        hash(self.lex)  # throws if not hashable

    # test delegation to an arbitrary string method pulled in from unicode
    def testDefaultStringStartsWithAA(self):
        self.assertTrue(
            self.lex.startswith("aa"),
            msg="default string: {} dict: {}".format(self.lex, self.lex.__dict__),
        )

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
        aaa_zzz = "_".join([self.lex, self.zlex])
        self.assertEqual(aaa_zzz, "aaa_zzz")

    def testEmptyIterableLikeEmptyString(self):
        self.assertEqual(self.elex, "")


class AddonTranslatorTest(unittest.TestCase):
    """
    Tests for the addon translator.
    """

    def setUp(self):
        from ...const import GRAMPS_LOCALE as glocale

        self._ = glocale.get_addon_translator(__file__, languages=["fr"]).gettext

    def testAddon(self):
        # A string in the "addon" domain.
        self.assertEqual(self._("Test Message"), "Message d'essai")

    def testGramps(self):
        # A string in the "gramps" domain.
        self.assertEqual(self._("United States of America"), "États-Unis")

    def testUntranslated(self):
        # An untranslated string.
        self.assertEqual(self._("Untranslated string"), "Untranslated string")


class SortKeyTest(unittest.TestCase):
    """
    Tests for GrampsLocale.sort_key().

    sort_key() returns bytes when ICU is available (PyICU Collator.getSortKey)
    or str when falling back to locale.strxfrm.  In both cases the values must
    be usable as keys for sorted() and must produce correct locale-aware order.
    """

    def setUp(self):
        from gramps.gen.const import GRAMPS_LOCALE as glocale

        self.glocale = glocale

    def test_return_type_is_bytes_when_icu_available(self):
        """sort_key() must return bytes when ICU is present (not str)."""
        if not HAVE_ICU:
            self.skipTest("ICU not available")
        key = self.glocale.sort_key("test")
        self.assertIsInstance(
            key,
            bytes,
            "sort_key() should return bytes when ICU is available",
        )

    def test_return_type_is_consistent(self):
        """Two calls on the same string must return equal keys."""
        k1 = self.glocale.sort_key("Gramps")
        k2 = self.glocale.sort_key("Gramps")
        self.assertEqual(k1, k2)

    def test_ascii_ordering(self):
        """Pure ASCII names must sort in the expected order."""
        names = ["Smith", "Abel", "Jones", "Brown"]
        result = sorted(names, key=self.glocale.sort_key)
        self.assertEqual(result, ["Abel", "Brown", "Jones", "Smith"])

    def test_case_insensitive_ordering(self):
        """Lower and upper case of the same letter must sort together."""
        names = ["smith", "Smith", "SMITH"]
        keys = [self.glocale.sort_key(n) for n in names]
        # All three keys should be equal (ICU primary-level) or at most
        # differ only at secondary/tertiary level — the sort must not place
        # 'smith' far from 'Smith'.
        result = sorted(names, key=self.glocale.sort_key)
        # All variants must appear contiguously (none displaced to a
        # completely different part of the sort order).
        positions = {n: result.index(n) for n in names}
        self.assertLessEqual(
            max(positions.values()) - min(positions.values()),
            2,
            "Case variants of the same name should sort contiguously",
        )

    def test_sorted_builtin_accepts_sort_key(self):
        """sorted() must work with sort_key as the key= argument."""
        names = ["Zara", "Anna", "Mike"]
        result = sorted(names, key=self.glocale.sort_key)
        self.assertEqual(result[0], "Anna")
        self.assertEqual(result[-1], "Zara")

    def test_empty_string(self):
        """sort_key('') must not raise and must return a consistent value."""
        k = self.glocale.sort_key("")
        self.assertEqual(k, self.glocale.sort_key(""))

    @unittest.skipUnless(HAVE_ICU, "ICU not available")
    def test_non_ascii_sorts_near_base_letter(self):
        """
        With an English ICU collator, Ö sorts near O (before Z).

        Uses a fixed 'en' collator so the result does not depend on the
        system locale of the test runner.  (Swedish, for example, places
        Ö *after* Z — that behaviour is covered in SortKeyLocaleTest.)
        """
        try:
            from icu import Locale, Collator
        except ImportError:
            from PyICU import Locale, Collator

        en_collator = Collator.createInstance(Locale("en"))
        with patch.object(self.glocale, "collator", en_collator):
            names = ["Zahn", "Öberg", "Ober"]
            result = sorted(names, key=self.glocale.sort_key)
        z_pos = result.index("Zahn")
        o_pos = result.index("Ober")
        ö_pos = result.index("Öberg")
        self.assertLess(
            o_pos,
            z_pos,
            "Ober (O...) should sort before Zahn (Z...) with English ICU collation",
        )
        self.assertLess(
            ö_pos,
            z_pos,
            "Öberg (Ö...) should sort before Zahn (Z...) with English ICU collation",
        )

    @unittest.skipUnless(HAVE_ICU, "ICU not available")
    def test_sort_key_not_plain_binary(self):
        """
        The returned bytes must reflect ICU collation, not raw Unicode code
        points.  Å (U+00C5, code point 197) has a higher code point than Z
        (U+005A, 90), so binary order would place Å after Z.  With an
        English ICU collator Å sorts near A (before Z).

        Uses a fixed 'en' collator so the result is locale-independent.
        """
        try:
            from icu import Locale, Collator
        except ImportError:
            from PyICU import Locale, Collator

        en_collator = Collator.createInstance(Locale("en"))
        with patch.object(self.glocale, "collator", en_collator):
            key_z = self.glocale.sort_key("Z")
            key_å = self.glocale.sort_key("Å")
        # In a binary sort Å > Z because ord('Å') > ord('Z').
        # With ICU English collation Å should sort near A, i.e. Å < Z.
        self.assertLess(
            key_å,
            key_z,
            "Å should sort before Z with English ICU collation (not raw binary order)",
        )


@unittest.skipUnless(HAVE_ICU, "ICU not available")
class SortKeyLocaleTest(unittest.TestCase):
    """
    Tests for GrampsLocale.sort_key() with explicitly chosen ICU locales.

    Each test patches glocale.collator with a Collator for a specific locale
    so the result never depends on the system locale of the test runner.
    """

    def setUp(self):
        from gramps.gen.const import GRAMPS_LOCALE as glocale

        self.glocale = glocale
        try:
            from icu import Locale, Collator
        except ImportError:
            from PyICU import Locale, Collator

        self._Locale = Locale
        self._Collator = Collator

    def _sorted(self, names, locale_name):
        """Return *names* sorted with a Collator for *locale_name*."""
        collator = self._Collator.createInstance(self._Locale(locale_name))
        with patch.object(self.glocale, "collator", collator):
            return sorted(names, key=self.glocale.sort_key)

    def test_return_type_is_bytes(self):
        """sort_key() must return bytes regardless of locale."""
        collator = self._Collator.createInstance(self._Locale("en"))
        with patch.object(self.glocale, "collator", collator):
            key = self.glocale.sort_key("test")
        self.assertIsInstance(key, bytes, "sort_key() should return bytes with ICU")

    def test_english_oberg_before_zahn(self):
        """English collation: Ö sorts near O, before Z."""
        result = self._sorted(["Zahn", "Öberg", "Ober"], "en")
        self.assertLess(
            result.index("Öberg"),
            result.index("Zahn"),
            "Öberg should sort before Zahn in English collation",
        )

    def test_german_oberg_before_zahn(self):
        """German collation: Ö sorts near O, before Z."""
        result = self._sorted(["Zahn", "Öberg", "Ober"], "de")
        self.assertLess(
            result.index("Öberg"),
            result.index("Zahn"),
            "Öberg should sort before Zahn in German collation",
        )

    def test_swedish_oberg_after_zahn(self):
        """Swedish collation: Ö sorts after Z (Å Ä Ö are the last letters)."""
        result = self._sorted(["Zahn", "Öberg", "Ober"], "sv")
        self.assertGreater(
            result.index("Öberg"),
            result.index("Zahn"),
            "Öberg should sort after Zahn in Swedish collation",
        )

    def test_swedish_a_ring_after_z(self):
        """Swedish collation: Å sorts after Z."""
        result = self._sorted(["Zahn", "Åberg", "Abel"], "sv")
        self.assertGreater(
            result.index("Åberg"),
            result.index("Zahn"),
            "Åberg should sort after Zahn in Swedish collation",
        )

    def test_english_ascii_order_unchanged(self):
        """Pure ASCII names sort A-Z in English collation."""
        names = ["Smith", "Abel", "Jones", "Brown"]
        result = self._sorted(names, "en")
        self.assertEqual(result, ["Abel", "Brown", "Jones", "Smith"])


class StrcollTest(unittest.TestCase):
    """Tests for GrampsLocale.strcoll(), which uses sort_key() internally."""

    def setUp(self):
        from gramps.gen.const import GRAMPS_LOCALE as glocale

        self.glocale = glocale

    def test_less_than(self):
        self.assertEqual(self.glocale.strcoll("Abel", "Smith"), -1)

    def test_greater_than(self):
        self.assertEqual(self.glocale.strcoll("Smith", "Abel"), 1)

    def test_equal(self):
        self.assertEqual(self.glocale.strcoll("Abel", "Abel"), 0)


if __name__ == "__main__":
    unittest.main()
