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
Unit tests for gramps.gen.utils.translationoverride.
"""

import json
import os
import tempfile
import unittest

from ..translationoverride import (
    get_overrides_for_language,
    load_custom_translations,
    save_custom_translations,
)


class LoadCustomTranslationsTest(unittest.TestCase):
    def setUp(self):
        fd, self.filename = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.filename)  # start with a missing file

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_custom_translations(self.filename), [])

    def test_malformed_json_returns_empty_list(self):
        with open(self.filename, "w", encoding="utf-8") as fp:
            fp.write("not valid json")
        self.assertEqual(load_custom_translations(self.filename), [])

    def test_non_list_json_returns_empty_list(self):
        with open(self.filename, "w", encoding="utf-8") as fp:
            json.dump({"not": "a list"}, fp)
        self.assertEqual(load_custom_translations(self.filename), [])

    def test_round_trip(self):
        entries = [
            {
                "language": "fr",
                "context": "Hebrew month lexeme",
                "msgid": "Nisan",
                "msgstr": "Nissan",
            }
        ]
        save_custom_translations(entries, self.filename)
        self.assertEqual(load_custom_translations(self.filename), entries)


class GetOverridesForLanguageTest(unittest.TestCase):
    def setUp(self):
        fd, self.filename = tempfile.mkstemp(suffix=".json")
        os.close(fd)

    def tearDown(self):
        os.remove(self.filename)

    def _write(self, entries):
        save_custom_translations(entries, self.filename)

    def test_exact_language_match(self):
        self._write(
            [
                {
                    "language": "fr",
                    "context": "Hebrew month lexeme",
                    "msgid": "Nisan",
                    "msgstr": "Nissan",
                }
            ]
        )
        overrides = get_overrides_for_language("fr", self.filename)
        self.assertEqual(overrides[("Hebrew month lexeme", "Nisan")], "Nissan")

    def test_other_language_not_applied(self):
        self._write(
            [
                {
                    "language": "fr",
                    "context": "Hebrew month lexeme",
                    "msgid": "Nisan",
                    "msgstr": "Nissan",
                }
            ]
        )
        overrides = get_overrides_for_language("en", self.filename)
        self.assertNotIn(("Hebrew month lexeme", "Nisan"), overrides)

    def test_subtag_match(self):
        # An override registered for the bare "en" subtag should apply
        # when the active language is a region variant like "en_GB".
        self._write(
            [
                {
                    "language": "en",
                    "context": "Hebrew month lexeme",
                    "msgid": "Heshvan",
                    "msgstr": "Cheshvan",
                }
            ]
        )
        overrides = get_overrides_for_language("en_GB.UTF-8", self.filename)
        self.assertEqual(overrides[("Hebrew month lexeme", "Heshvan")], "Cheshvan")

    def test_exact_locale_wins_over_subtag(self):
        self._write(
            [
                {
                    "language": "en",
                    "context": "Hebrew month lexeme",
                    "msgid": "Heshvan",
                    "msgstr": "generic-en-spelling",
                },
                {
                    "language": "en_GB",
                    "context": "Hebrew month lexeme",
                    "msgid": "Heshvan",
                    "msgstr": "gb-specific-spelling",
                },
            ]
        )
        overrides = get_overrides_for_language("en_GB", self.filename)
        self.assertEqual(
            overrides[("Hebrew month lexeme", "Heshvan")], "gb-specific-spelling"
        )

    def test_malformed_entry_is_skipped(self):
        self._write([{"language": "en", "msgid": "Nisan"}])  # missing msgstr
        overrides = get_overrides_for_language("en", self.filename)
        self.assertEqual(overrides, {})

    def test_default_context_when_absent(self):
        self._write([{"language": "en", "msgid": "January", "msgstr": "Jan-uary"}])
        overrides = get_overrides_for_language("en", self.filename)
        self.assertEqual(overrides[("", "January")], "Jan-uary")


if __name__ == "__main__":
    unittest.main()
