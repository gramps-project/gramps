# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013       Zissis Papadopoulos <zissis@mail.com>
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
Greek-specific classes for parsing and displaying dates.
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
# Greek parser class
#
# -------------------------------------------------------------------------
class DateParserEL(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        "προ του": Date.MOD_BEFORE,
        "πριν το": Date.MOD_BEFORE,
        "πριν από τις": Date.MOD_BEFORE,
        "πριν από την": Date.MOD_BEFORE,
        "πριν από το": Date.MOD_BEFORE,
        "πριν από τον": Date.MOD_BEFORE,
        "προ": Date.MOD_BEFORE,
        "πρ.": Date.MOD_BEFORE,
        "μετά το": Date.MOD_AFTER,
        "μετά από τις": Date.MOD_AFTER,
        "μετά από την": Date.MOD_AFTER,
        "μετά από το": Date.MOD_AFTER,
        "μετά από τον": Date.MOD_AFTER,
        "μετά": Date.MOD_AFTER,
        "μετ.": Date.MOD_AFTER,
        "γύρω στο": Date.MOD_ABOUT,
        "γύρω στον": Date.MOD_ABOUT,
        "γύρω στις": Date.MOD_ABOUT,
        "περίπου το": Date.MOD_ABOUT,
        "περ.": Date.MOD_ABOUT,
        "γυρ.": Date.MOD_ABOUT,
        "~": Date.MOD_ABOUT,
        "from": Date.MOD_FROM,
        "to": Date.MOD_TO,
    }

    bce = ["π.Χ.", "π.Κ.Χ.", "π.Κ.Ε.", "π.Χ"]

    calendar_to_int = {
        "γρηγοριανό": Date.CAL_GREGORIAN,
        "γ": Date.CAL_GREGORIAN,
        "ιουλιανό": Date.CAL_JULIAN,
        "ι": Date.CAL_JULIAN,
        "εβραϊκό": Date.CAL_HEBREW,
        "ε": Date.CAL_HEBREW,
        "ισλαμικό": Date.CAL_ISLAMIC,
        "ισλ": Date.CAL_ISLAMIC,
        "γαλλικό": Date.CAL_FRENCH,
        "γαλλικής δημοκρατίας": Date.CAL_FRENCH,
        "γ": Date.CAL_FRENCH,
        "περσικό": Date.CAL_PERSIAN,
        "π": Date.CAL_PERSIAN,
        "σουηδικό": Date.CAL_SWEDISH,
        "σ": Date.CAL_SWEDISH,
    }

    quality_to_int = {
        "κατʼ εκτίμηση": Date.QUAL_ESTIMATED,
        "εκτιμώμενη": Date.QUAL_ESTIMATED,
        "εκτ.": Date.QUAL_ESTIMATED,
        "εκτ": Date.QUAL_ESTIMATED,
        "υπολογ": Date.QUAL_CALCULATED,
        "υπολογ.": Date.QUAL_CALCULATED,
        "υπολογισμένη": Date.QUAL_CALCULATED,
        "με υπολογισμό": Date.QUAL_CALCULATED,
    }

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        """
        DateParser.init_strings(self)
        _span_1 = ["από"]
        _span_2 = ["έως"]
        _range_1 = ["μετ", r"μετ\.", "μεταξύ"]
        _range_2 = ["και"]
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
# Greek display
#
# -------------------------------------------------------------------------
class DateDisplayEL(DateDisplay):
    """
    Greek language date display class.
    """

    # this is used to display the 12 gregorian months
    long_months = (
        "",
        "Ιανουάριος",
        "Φεβρουάριος",
        "Μάρτιος",
        "Απρίλιος",
        "Μάιος",
        "Ιούνιος",
        "Ιούλιος",
        "Αύγουστος",
        "Σεπτέμβριος",
        "Οκτώβριος",
        "Νοέμβριος",
        "Δεκέμβριος",
    )

    short_months = (
        "",
        "Ιαν",
        "Φεβ",
        "Μαρ",
        "Απρ",
        "Μάι",
        "Ιουν",
        "Ιουλ",
        "Αύγ",
        "Σεπ",
        "Οκτ",
        "Νοε",
        "Δεκ",
    )

    _mod_str = ("", "προ του ", "μετά το ", "γύρω στο ", "", "", "")

    _qual_str = ("", "εκτιμώμενη ", "υπολογισμένη ")

    _bce_str = "%s π.Χ."

    formats = (
        "ΕΕΕΕ-ΜΜ-ΗΗ (ISO)",
        "ΗΗ-ΜΜ-ΕΕΕΕ",
        "ΗΗ/ΜΜ/ΕΕΕΕ",
        "ΗΗ Μήνας ΕΕΕΕ",
        "ΗΗ Μήν ΕΕΕΕ",
    )
    # this definition must agree with its "_display_gregorian" method

    def _display_gregorian(self, date_val, **kwargs):
        """
        display gregorian calendar date in different format
        """
        # this must agree with its locale-specific "formats" definition
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # day-month_number-year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s-%s" % (date_val[1], year)
            else:
                value = "%d-%s-%s" % (date_val[0], date_val[1], year)
        elif self.format == 2:
            # day/month_number/year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s/%s" % (date_val[1], year)
            else:
                value = "%d/%s/%s" % (date_val[0], date_val[1], year)
        elif self.format == 3:
            # day month_name year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.long_months[date_val[1]], year)
        else:
            # day month_abbreviation year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.short_months[date_val[1]], year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def display(self, date):
        """
        Return a text string representing the date.
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
            return "%s%s %s %s %s%s" % (qual_str, "από", d1, "έως", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "μεταξύ", d1, "και", d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("el_GR", "el_CY", "el", "Greek", "greek", ("%d/%m/%Y",)),
    DateParserEL,
    DateDisplayEL,
)
