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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tests for the Japanese Imperial (和暦) calendar helpers in gcalendar.py."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib.gcalendar import (
    gregorian_sdn,
    gregorian_to_japanese_era,
    japanese_era_to_gregorian,
    japanese_imperial_sdn,
    japanese_imperial_ymd,
)
from gramps.gen.lib.date import Date


class TestGregorianToJapaneseEra(unittest.TestCase):
    """Tests for gregorian_to_japanese_era()."""

    # --- Modern era anchor points ---

    def test_meiji_first_day(self):
        """1868-09-08 is Meiji 1."""
        self.assertEqual(gregorian_to_japanese_era(1868, 9, 8), ("明治", 1))

    def test_meiji_last_day(self):
        """1912-07-29 is Meiji 45."""
        self.assertEqual(gregorian_to_japanese_era(1912, 7, 29), ("明治", 45))

    def test_taisho_first_day(self):
        """1912-07-30 is Taishō 1."""
        self.assertEqual(gregorian_to_japanese_era(1912, 7, 30), ("大正", 1))

    def test_taisho_last_day(self):
        """1926-12-24 is Taishō 15."""
        self.assertEqual(gregorian_to_japanese_era(1926, 12, 24), ("大正", 15))

    def test_showa_first_day(self):
        """1926-12-25 is Shōwa 1."""
        self.assertEqual(gregorian_to_japanese_era(1926, 12, 25), ("昭和", 1))

    def test_showa_last_day(self):
        """1989-01-07 is Shōwa 64."""
        self.assertEqual(gregorian_to_japanese_era(1989, 1, 7), ("昭和", 64))

    def test_heisei_first_day(self):
        """1989-01-08 is Heisei 1."""
        self.assertEqual(gregorian_to_japanese_era(1989, 1, 8), ("平成", 1))

    def test_heisei_last_day(self):
        """2019-04-30 is Heisei 31."""
        self.assertEqual(gregorian_to_japanese_era(2019, 4, 30), ("平成", 31))

    def test_reiwa_first_day(self):
        """2019-05-01 is Reiwa 1."""
        self.assertEqual(gregorian_to_japanese_era(2019, 5, 1), ("令和", 1))

    def test_reiwa_current_year(self):
        """2026 is Reiwa 8."""
        self.assertEqual(gregorian_to_japanese_era(2026, 1, 1), ("令和", 8))

    def test_showa_40(self):
        """1965 is Shōwa 40."""
        self.assertEqual(gregorian_to_japanese_era(1965, 5, 15), ("昭和", 40))

    # --- Pre-Meiji era ---

    def test_ansei_5(self):
        """September 25, 1858 falls in Ansei (安政)."""
        era, year = gregorian_to_japanese_era(1858, 9, 25)
        self.assertEqual(era, "安政")
        self.assertEqual(year, 5)

    def test_pre_taika_returns_none(self):
        """Dates before the Taika era (645 CE) return None."""
        self.assertIsNone(gregorian_to_japanese_era(644, 12, 31))

    def test_taika_first_day(self):
        """645-07-17 is Taika 1."""
        result = gregorian_to_japanese_era(645, 7, 17)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "大化")
        self.assertEqual(result[1], 1)

    def test_before_era_start_in_same_year(self):
        """A date in 1868 before Sep 8 is not yet Meiji — it is in Keio."""
        era, _ = gregorian_to_japanese_era(1868, 9, 7)
        self.assertEqual(era, "慶応")

    def test_era_transition_boundary(self):
        """Taisho starts July 30, 1912; one day before is still Meiji."""
        self.assertEqual(gregorian_to_japanese_era(1912, 7, 29)[0], "明治")
        self.assertEqual(gregorian_to_japanese_era(1912, 7, 30)[0], "大正")


class TestJapaneseEraToGregorian(unittest.TestCase):
    """Tests for japanese_era_to_gregorian()."""

    def test_showa_40_kanji(self):
        """昭和40 → 1965."""
        self.assertEqual(japanese_era_to_gregorian("昭和", 40), 1965)

    def test_meiji_1_kanji(self):
        """明治1 → 1868."""
        self.assertEqual(japanese_era_to_gregorian("明治", 1), 1868)

    def test_reiwa_1_kanji(self):
        """令和1 → 2019."""
        self.assertEqual(japanese_era_to_gregorian("令和", 1), 2019)

    def test_romaji_showa(self):
        """'Showa' (ASCII) is accepted."""
        self.assertEqual(japanese_era_to_gregorian("Showa", 40), 1965)

    def test_romaji_lowercase(self):
        """'showa' (lower-case ASCII) is accepted."""
        self.assertEqual(japanese_era_to_gregorian("showa", 1), 1926)

    def test_romaji_with_macron(self):
        """'Shōwa' (with macron) is accepted via normalisation."""
        self.assertEqual(japanese_era_to_gregorian("Shōwa", 40), 1965)

    def test_romaji_meiji(self):
        """'Meiji' (romaji) → correct year."""
        self.assertEqual(japanese_era_to_gregorian("Meiji", 45), 1912)

    def test_romaji_reiwa(self):
        """'Reiwa' (romaji) → correct year."""
        self.assertEqual(japanese_era_to_gregorian("Reiwa", 6), 2024)

    def test_ansei_5(self):
        """安政5 → 1858."""
        self.assertEqual(japanese_era_to_gregorian("安政", 5), 1858)

    def test_unknown_era_returns_none(self):
        """Unrecognised era name returns None."""
        self.assertIsNone(japanese_era_to_gregorian("存在しない", 1))

    def test_year_zero_returns_none(self):
        """year_in_era < 1 returns None."""
        self.assertIsNone(japanese_era_to_gregorian("昭和", 0))

    def test_roundtrip_modern_eras(self):
        """gregorian_to_japanese_era and japanese_era_to_gregorian are inverses."""
        for kanji, _romaji, sy, sm, sd in [
            ("令和", "Reiwa", 2019, 5, 1),
            ("平成", "Heisei", 1989, 1, 8),
            ("昭和", "Showa", 1926, 12, 25),
            ("大正", "Taisho", 1912, 7, 30),
            ("明治", "Meiji", 1868, 9, 8),
        ]:
            era, y_in_era = gregorian_to_japanese_era(sy, sm, sd)
            self.assertEqual(era, kanji)
            self.assertEqual(y_in_era, 1)
            back = japanese_era_to_gregorian(kanji, y_in_era)
            self.assertEqual(back, sy)


class TestJapaneseImperialSDN(unittest.TestCase):
    """Tests for japanese_imperial_sdn() and japanese_imperial_ymd()."""

    def test_post_meiji_gregorian(self):
        """Post-1872 dates use Gregorian month/day.

        Shōwa 40 (1965), May 15 → SDN matches gregorian_sdn(1965, 5, 15).
        """
        sdn = japanese_imperial_sdn(1965, 5, 15)
        self.assertEqual(sdn, gregorian_sdn(1965, 5, 15))

    def test_post_meiji_round_trip(self):
        """SDN round-trip for a modern Gregorian date."""
        sdn = japanese_imperial_sdn(1965, 5, 15)
        self.assertEqual(japanese_imperial_ymd(sdn), (1965, 5, 15))

    def test_pre_meiji_ansei_anchor(self):
        """安政5年8月19日 (lunisolar) = Gregorian 1858-09-25.

        The SDN must equal gregorian_sdn(1858, 9, 25).
        """
        sdn = japanese_imperial_sdn(1858, 8, 19)
        self.assertEqual(sdn, gregorian_sdn(1858, 9, 25))

    def test_pre_meiji_round_trip(self):
        """SDN round-trip for a pre-1873 lunisolar date."""
        sdn = japanese_imperial_sdn(1858, 8, 19)
        self.assertNotEqual(sdn, 0)
        self.assertEqual(japanese_imperial_ymd(sdn), (1858, 8, 19))

    def test_threshold_post(self):
        """1873-01-01 (first Gregorian day) uses gregorian_sdn."""
        self.assertEqual(japanese_imperial_sdn(1873, 1, 1), gregorian_sdn(1873, 1, 1))

    def test_threshold_ymd_post(self):
        """japanese_imperial_ymd for 1873-01-01 SDN returns Gregorian tuple."""
        sdn = gregorian_sdn(1873, 1, 1)
        self.assertEqual(japanese_imperial_ymd(sdn), (1873, 1, 1))

    def test_out_of_range_returns_zero(self):
        """Year 0 is outside supported range → returns 0."""
        self.assertEqual(japanese_imperial_sdn(0, 1, 1), 0)

    def test_out_of_range_ymd(self):
        """SDN 0 is outside supported range → returns (0, 0, 0)."""
        self.assertEqual(japanese_imperial_ymd(0), (0, 0, 0))


class TestDateConstants(unittest.TestCase):
    """Tests for the Date class constants added for Japanese Imperial."""

    def test_cal_constant_value(self):
        """CAL_JAPANESE_IMPERIAL is 9."""
        self.assertEqual(Date.CAL_JAPANESE_IMPERIAL, 9)

    def test_calendars_range_includes(self):
        """CALENDARS range includes CAL_JAPANESE_IMPERIAL."""
        self.assertIn(Date.CAL_JAPANESE_IMPERIAL, Date.CALENDARS)

    def test_calendar_name(self):
        """calendar_names[9] is 'Japanese Imperial'."""
        self.assertEqual(Date.calendar_names[9], "Japanese Imperial")

    def test_calendar_convert_length(self):
        """_calendar_convert has an entry for every calendar."""
        self.assertEqual(len(Date._calendar_convert), len(Date.CALENDARS))

    def test_calendar_change_length(self):
        """_calendar_change has an entry for every calendar."""
        self.assertEqual(len(Date._calendar_change), len(Date.CALENDARS))


if __name__ == "__main__":
    unittest.main()
