# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
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
Bulgarian-specific classes for parsing and displaying dates.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler


# -------------------------------------------------------------------------
#
# Bulgarian parser
#
# -------------------------------------------------------------------------
class DateParserBG(DateParser):
    modifier_to_int = {
        "преди": Date.MOD_BEFORE,
        "пр.": Date.MOD_BEFORE,
        "пр": Date.MOD_BEFORE,
        "след": Date.MOD_AFTER,
        "сл.": Date.MOD_AFTER,
        "сл": Date.MOD_AFTER,
        "ок": Date.MOD_ABOUT,
        "ок.": Date.MOD_ABOUT,
        "около": Date.MOD_ABOUT,
        "примерно": Date.MOD_ABOUT,
        "прим": Date.MOD_ABOUT,
        "прим.": Date.MOD_ABOUT,
        "приблизително": Date.MOD_ABOUT,
        "приб.": Date.MOD_ABOUT,
        "прибл.": Date.MOD_ABOUT,
        "приб": Date.MOD_ABOUT,
        "прибл": Date.MOD_ABOUT,
        "from": Date.MOD_FROM,
        "to": Date.MOD_TO,
    }

    calendar_to_int = {
        "григориански": Date.CAL_GREGORIAN,
        "г": Date.CAL_GREGORIAN,
        "юлиански": Date.CAL_JULIAN,
        "ю": Date.CAL_JULIAN,
        "еврейски": Date.CAL_HEBREW,
        "е": Date.CAL_HEBREW,
        "ислямски": Date.CAL_ISLAMIC,
        "и": Date.CAL_ISLAMIC,
        "френски републикански": Date.CAL_FRENCH,
        "републикански": Date.CAL_FRENCH,
        "фр.реп.": Date.CAL_FRENCH,
        "р": Date.CAL_FRENCH,
        "френски": Date.CAL_FRENCH,
        "фр.": Date.CAL_FRENCH,
        "персийски": Date.CAL_PERSIAN,
        "п": Date.CAL_PERSIAN,
    }

    quality_to_int = {
        "приблизително": Date.QUAL_ESTIMATED,
        "прибл.": Date.QUAL_ESTIMATED,
        "изчислено": Date.QUAL_CALCULATED,
        "изчисл.": Date.QUAL_CALCULATED,
        "изч.": Date.QUAL_CALCULATED,
    }

    hebrew_to_int = {
        "тишрей": 1,
        "мархешван": 2,
        "кислев": 3,
        "тевет": 4,
        "шват": 5,
        "адар": 6,
        "адар бет": 7,
        "нисан": 8,
        "ияр": 9,
        "сиван": 10,
        "тамуз": 11,
        "ав": 12,
        "eлул": 13,
    }

    islamic_to_int = {
        "мухаррам": 1,
        "саффар": 2,
        "рабиу-л-ауал": 3,
        "рабиу-с-сани": 4,
        "джумадал-уля": 5,
        "джумада-с-сания": 6,
        "раджаб": 7,
        "шаабан": 8,
        "рамадан": 9,
        "шауал": 10,
        "зу-л-кида": 11,
        "зул-л-хиджа": 12,
    }

    persian_to_int = {
        "фарвардин": 1,
        "урдбихищ": 2,
        "хурдад": 3,
        "тир": 4,
        "мурдад": 5,
        "шахривар": 6,
        "михр": 7,
        "абан": 8,
        "азар": 9,
        "дай": 10,
        "бахман": 11,
        "исфаидармуз": 12,
    }

    french_to_int = {
        "вандемер": 1,
        "брюмер": 2,
        "фример": 3,
        "нивоз": 4,
        "плювиоз": 5,
        "вантоз": 6,
        "жерминал": 7,
        "флореал": 8,
        "прериал": 9,
        "месидор": 10,
        "термидор": 11,
        "фрюктидор": 12,
        "допълнителен": 13,
    }

    bce = ["преди Христа", "пр. Хр.", "пр.Хр."] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ["от"]
        _span_2 = ["до"]
        _range_1 = ["между"]
        _range_2 = ["и"]
        self._span = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
            % ("|".join(_range_1), "|".join(_range_2)),
            re.IGNORECASE,
        )


# -------------------------------------------------------------------------
#
# Bulgarian displayer
#
# -------------------------------------------------------------------------
class DateDisplayBG(DateDisplay):
    """
    Bulgarian language date display class.
    """

    long_months = (
        "",
        "януари",
        "февруари",
        "март",
        "април",
        "май",
        "юни",
        "юли",
        "август",
        "септември",
        "октомври",
        "ноември",
        "декември",
    )

    short_months = (
        "",
        "яну",
        "февр",
        "март",
        "апр",
        "май",
        "юни",
        "юли",
        "авг",
        "септ",
        "окт",
        "ное",
        "дек",
    )

    calendar = (
        "",
        "юлиански",
        "еврейски",
        "републикански",
        "персийски",
        "ислямски",
        "шведски",
    )

    _mod_str = ("", "преди ", "след ", "около ", "", "", "")

    _qual_str = ("", "приблизително ", "изчислено ")

    _bce_str = "%s пр. Хр."

    formats = (
        "ГГГГ-ММ-ДД (ISO)",
        "Числов",
        "Месец Ден, Година",
        "Мес. Ден, Година",
        "Ден Месец Година",
        "Ден Мес. Година",
    )
    # this must agree with DateDisplayEn's "formats" definition
    # (since no locale-specific _display_gregorian exists, here)

    hebrew = (
        "",
        "Тишрей",
        "Мархешван",
        "Кислев",
        "Тевет",
        "Шват",
        "Адар",
        "Адар бет",
        "Нисан",
        "Ияр",
        "Сиван",
        "Тамуз",
        "Ав",
        "Елул",
    )

    islamic = (
        "",
        "Мухаррам",
        "Саффар",
        "Рабиу-л-ауал",
        "Рабиу-с-сани",
        "Джумадал-уля",
        "Джумада-с-сания",
        "Раджаб",
        "Шаабан",
        "Рамадан",
        "Шауал",
        "Зу-л-кида",
        "Зул-л-хиджа",
    )

    persian = (
        "",
        "Фарвардин",
        "Урдбихищ",
        "Хурдад",
        "Тир",
        "Мурдад",
        "Шахривар",
        "Михр",
        "Абан",
        "Азар",
        "Дай",
        "Бахман",
        "Исфаидармуз",
    )

    french = (
        "",
        "Вандемер",
        "Брюмер",
        "Фример",
        "Нивоз",
        "Плювиоз",
        "Вантоз",
        "Жерминал",
        "Флореал",
        "Прериал",
        "Мессидор",
        "Термидор",
        "Фрюктидор",
        "Допълнителен",
    )

    def display(self, date):
        """
        Returns a text string representing the date.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = self._qual_str[qual]

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "от", d1, "до", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "между", d1, "и", d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

    def dd_dformat01(self, date_val):
        """
        numerical -- for Bulgarian dates
        """
        if date_val[3]:
            return self.display_iso(date_val)
        else:
            if date_val[0] == date_val[1] == 0:
                return str(date_val[2])
            else:
                value = self.dhformat.replace("%m", str(date_val[1]))
                # some locales have %b for the month, e.g. ar_EG, is_IS, nb_NO
                value = value.replace("%b", str(date_val[1]))
                if date_val[0] == 0:  # ignore the zero day and its delimiter
                    i_day = value.find("%e")  # Bulgarian uses %e and not %d
                    value = value.replace(value[i_day : i_day + 3], "")
                value = value.replace("%e", str(date_val[0]))
                value = value.replace("%Y", str(abs(date_val[2])))
                return value.replace("-", "/")


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("bg_BG", "bg", "bulgarian", "Bulgarian", ("%e.%m.%Y",)),
    DateParserBG,
    DateDisplayBG,
)
