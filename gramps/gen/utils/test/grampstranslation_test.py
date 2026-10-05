# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""
Unit tests for the translation-override support in
gramps.gen.utils.grampstranslation.
"""

import unittest

from ..grampstranslation import GrampsNullTranslations, GrampsTranslations


class GrampsNullTranslationsOverrideTest(unittest.TestCase):
    def setUp(self):
        self.trans = GrampsNullTranslations()

    def test_no_overrides_passes_through(self):
        self.assertEqual(self.trans.gettext("Nisan", "Hebrew month lexeme"), "Nisan")

    def test_override_applied(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.gettext("Nisan", "Hebrew month lexeme"), "Nissan")

    def test_override_applied_via_pgettext(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.pgettext("Hebrew month lexeme", "Nisan"), "Nissan")

    def test_override_applied_via_sgettext(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.sgettext("Nisan", "Hebrew month lexeme"), "Nissan")

    def test_override_does_not_match_wrong_context(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.gettext("Nisan", "French month lexeme"), "Nisan")

    def test_override_does_not_match_wrong_msgid(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(
            self.trans.gettext("Heshvan", "Hebrew month lexeme"), "Heshvan"
        )

    def test_override_without_context(self):
        self.trans.set_overrides({("", "January"): "Jan-uary"})
        self.assertEqual(self.trans.gettext("January"), "Jan-uary")


class GrampsTranslationsOverrideTest(unittest.TestCase):
    def setUp(self):
        # An empty catalog: overrides must work even with no real .mo
        # loaded (falls back to returning the msgid itself when absent).
        self.trans = GrampsTranslations(fp=None)
        self.trans._catalog = {}

    def test_no_overrides_passes_through(self):
        self.assertEqual(self.trans.gettext("Nisan", "Hebrew month lexeme"), "Nisan")

    def test_override_applied(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.gettext("Nisan", "Hebrew month lexeme"), "Nissan")

    def test_override_applied_via_pgettext(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(self.trans.pgettext("Hebrew month lexeme", "Nisan"), "Nissan")

    def test_override_applied_via_lexgettext(self):
        self.trans.set_overrides({("Hebrew month lexeme", "Nisan"): "Nissan"})
        self.assertEqual(
            self.trans.lexgettext("Nisan", "Hebrew month lexeme"), "Nissan"
        )


if __name__ == "__main__":
    unittest.main()
