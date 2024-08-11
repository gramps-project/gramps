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

"""
Date strings to translate per each language for display and parsing.

__main__
--------

Run this code with the appropriate ``LANG`` and ``LC_DATE`` set for your target
language, in order to generate the .po snippets initialized with the strings
from your locale (from the deprecated data provided in _grampslocale).

E.g., for French::

    LANG=fr_FR.utf8 LC_ALL=fr_FR.utf8 GRAMPS_RESOURCES=$PWD python -m gramps.gen.datehandler._datestrings

Then merge the output into your language's .po file, and further modify the
strings as needed. Then remove the strings from your language's
:class:`DateParserXX` and :class:`DateHandlerXX` classes.
"""

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".DateStrings")


# -------------------------------------------------------------------------
#
# DateStrings
#
# -------------------------------------------------------------------------
class DateStrings:
    """
    String tables for :class:`.DateDisplay` and :class:`.DateParser`.
    """

    # This table needs not be localized, it's only for parsing
    # Swedish calendar dates using Swedish month names.
    # Display of these months uses the regular long_months.
    # TODO should we pack these into alt_long_months instead?
    swedish_SV = (
        "",
        "Januari",
        "Februari",
        "Mars",
        "April",
        "Maj",
        "Juni",
        "Juli",
        "Augusti",
        "September",
        "Oktober",
        "November",
        "December",
    )

    def __init__(self, locale):
        _ = locale.translation.lexgettext

        self.long_months = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("January", "localized lexeme inflections"),
            _("February", "localized lexeme inflections"),
            _("March", "localized lexeme inflections"),
            _("April", "localized lexeme inflections"),
            _("May", "localized lexeme inflections"),
            _("June", "localized lexeme inflections"),
            _("July", "localized lexeme inflections"),
            _("August", "localized lexeme inflections"),
            _("September", "localized lexeme inflections"),
            _("October", "localized lexeme inflections"),
            _("November", "localized lexeme inflections"),
            _("December", "localized lexeme inflections"),
        )

        self.short_months = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Jan", "localized lexeme inflections - short month form"),
            _("Feb", "localized lexeme inflections - short month form"),
            _("Mar", "localized lexeme inflections - short month form"),
            _("Apr", "localized lexeme inflections - short month form"),
            _("May", "localized lexeme inflections - short month form"),
            _("Jun", "localized lexeme inflections - short month form"),
            _("Jul", "localized lexeme inflections - short month form"),
            _("Aug", "localized lexeme inflections - short month form"),
            _("Sep", "localized lexeme inflections - short month form"),
            _("Oct", "localized lexeme inflections - short month form"),
            _("Nov", "localized lexeme inflections - short month form"),
            _("Dec", "localized lexeme inflections - short month form"),
        )

        _ = locale.translation.sgettext
        self.alt_long_months = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to add proper alternatives to be recognized in your localized
            # DateParser code!
            _("", "alternative month names for January"),
            _("", "alternative month names for February"),
            _("", "alternative month names for March"),
            _("", "alternative month names for April"),
            _("", "alternative month names for May"),
            _("", "alternative month names for June"),
            _("", "alternative month names for July"),
            _("", "alternative month names for August"),
            _("", "alternative month names for September"),
            _("", "alternative month names for October"),
            _("", "alternative month names for November"),
            _("", "alternative month names for December"),
        )

        self.calendar = (
            # Must appear in the order indexed by Date.CAL_... numeric constants
            _("Gregorian", "calendar"),
            _("Julian", "calendar"),
            _("Hebrew", "calendar"),
            _("French Republican", "calendar"),
            _("Persian", "calendar"),
            _("Islamic", "calendar"),
            _("Swedish", "calendar"),
        )
        _ = locale.translation.lexgettext

        self.hebrew = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Tishri", "Hebrew month lexeme"),
            _("Heshvan", "Hebrew month lexeme"),
            _("Kislev", "Hebrew month lexeme"),
            _("Tevet", "Hebrew month lexeme"),
            _("Shevat", "Hebrew month lexeme"),
            _("AdarI", "Hebrew month lexeme"),
            _("AdarII", "Hebrew month lexeme"),
            _("Nisan", "Hebrew month lexeme"),
            _("Iyyar", "Hebrew month lexeme"),
            _("Sivan", "Hebrew month lexeme"),
            _("Tammuz", "Hebrew month lexeme"),
            _("Av", "Hebrew month lexeme"),
            _("Elul", "Hebrew month lexeme"),
        )

        self.french = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Vendémiaire", "French month lexeme"),
            _("Brumaire", "French month lexeme"),
            _("Frimaire", "French month lexeme"),
            _("Nivôse", "French month lexeme"),
            _("Pluviôse", "French month lexeme"),
            _("Ventôse", "French month lexeme"),
            _("Germinal", "French month lexeme"),
            _("Floréal", "French month lexeme"),
            _("Prairial", "French month lexeme"),
            _("Messidor", "French month lexeme"),
            _("Thermidor", "French month lexeme"),
            _("Fructidor", "French month lexeme"),
            _("Extra", "French month lexeme"),
        )

        self.islamic = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Muharram", "Islamic month lexeme"),
            _("Safar", "Islamic month lexeme"),
            _("Rabi`al-Awwal", "Islamic month lexeme"),
            _("Rabi`ath-Thani", "Islamic month lexeme"),
            _("Jumada l-Ula", "Islamic month lexeme"),
            _("Jumada t-Tania", "Islamic month lexeme"),
            _("Rajab", "Islamic month lexeme"),
            _("Sha`ban", "Islamic month lexeme"),
            _("Ramadan", "Islamic month lexeme"),
            _("Shawwal", "Islamic month lexeme"),
            _("Dhu l-Qa`da", "Islamic month lexeme"),
            _("Dhu l-Hijja", "Islamic month lexeme"),
        )

        self.persian = (
            "",
            # Translators: see
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Farvardin", "Persian month lexeme"),
            _("Ordibehesht", "Persian month lexeme"),
            _("Khordad", "Persian month lexeme"),
            _("Tir", "Persian month lexeme"),
            _("Mordad", "Persian month lexeme"),
            _("Shahrivar", "Persian month lexeme"),
            _("Mehr", "Persian month lexeme"),
            _("Aban", "Persian month lexeme"),
            _("Azar", "Persian month lexeme"),
            _("Dey", "Persian month lexeme"),
            _("Bahman", "Persian month lexeme"),
            _("Esfand", "Persian month lexeme"),
        )

        self.modifiers = (
            "",
            # Translators: if the modifier is after the date
            # put the space ahead of the word instead of after it
            _("before ", "date modifier"),
            # Translators: if the modifier is after the date
            # put the space ahead of the word instead of after it
            _("after ", "date modifier"),
            # Translators: if the modifier is after the date
            # put the space ahead of the word instead of after it
            _("about ", "date modifier"),
            "",
            "",
            "",
            # Translators: if the modifier is after the date
            # put the space ahead of the word instead of after it
            _("from ", "date modifier"),
            # Translators: if the modifier is after the date
            # put the space ahead of the word instead of after it
            _("to ", "date modifier"),
        )

        self.qualifiers = (
            "",
            _("estimated ", "date quality"),
            _("calculated ", "date quality"),
        )

        # 6753: localized day names. Eventually should sprout into
        # a per-calendar type thing instead.
        self.long_days = (
            "",
            _("Sunday"),
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
        )

        self.short_days = (
            "",  # Icelandic needs them
            _("Sun"),
            _("Mon"),
            _("Tue"),
            _("Wed"),
            _("Thu"),
            _("Fri"),
            _("Sat"),
        )


# set GRAMPS_RESOURCES then: python3 -m gramps.gen.datehandler._datestrings
if __name__ == "__main__":
    import sys
    from ..utils.grampslocale import GrampsLocale
    from ..const import GRAMPS_LOCALE as glocale
    from ._grampslocale import (
        _deprecated_long_months as old_long,
        _deprecated_short_months as old_short,
        _deprecated_short_days as old_short_days,  # Icelandic needs them
        _deprecated_long_days as old_days,
    )
    from ._datedisplay import DateDisplay
    import gettext

    lang = glocale.lang
    lang_short = lang[:2]
    available_langs = glocale.get_language_list()  # get the cached list
    if glocale.check_available_translations(lang) is None:
        print(
            "Translation for current language {lang} not available.\n"
            "Available translations: {list}.\n"
            "Does po/{lang_short}*.po exist in gramps source tree?!\n"
            "Please set your LANG / LC_ALL environment to something else...\n".format(
                lang=lang, list=available_langs, lang_short=lang_short
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        "# Generating snippets for {}*.po\n"
        "# Available languages: {}".format(lang_short, available_langs)
    )
    glocale = GrampsLocale(languages=(lang))  # in __main__
    dd = glocale.date_displayer
    ds = dd._ds
    glocale_EN = GrampsLocale(languages=("en"))  # in __main__
    ds_EN = DateStrings(glocale_EN)

    filename = __file__

    try:
        localized_months = dd.__class__.long_months
    except AttributeError:
        localized_months = old_long

    def print_po_snippet(en_loc_old_lists, context):
        for m, localized, old in zip(*en_loc_old_lists):
            if m == "":
                continue
            if m == localized:
                localized = old
            print("#: {file}:{line}".format(file=filename, line=print_po_snippet.line))
            if context:
                print('msgctxt "{context}"'.format(context=context))
            print(
                'msgid "{en_month}"\n'
                'msgstr "{localized_month}"\n'.format(
                    en_month=m, localized_month=localized
                )
            )
            print_po_snippet.line += 1

    print_po_snippet.line = 10000

    try:
        localized_months = dd.__class__.long_months
    except AttributeError:
        localized_months = old_long
    print_po_snippet(
        (ds_EN.long_months, localized_months, old_long),
        "localized lexeme inflections",
    )

    try:
        localized_months = dd.__class__.short_months
    except AttributeError:
        localized_months = old_short
    print_po_snippet(
        (ds_EN.short_months, localized_months, old_short),
        "localized lexeme inflections - short month form",
    )

    print_po_snippet((ds_EN.long_days, old_days, old_days), "")

    print_po_snippet((ds_EN.short_days, old_short_days, old_short_days), "")

    try:
        loc = dd.__class__.hebrew
        print_po_snippet((ds_EN.hebrew, loc, loc), "Hebrew month lexeme")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.french
        print_po_snippet((ds_EN.french, loc, loc), "French month lexeme")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.islamic
        print_po_snippet((ds_EN.islamic, loc, loc), "Islamic month lexeme")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.persian
        print_po_snippet((ds_EN.persian, loc, loc), "Persian month lexeme")
    except AttributeError:
        pass

    try:
        loc = dd.__class__._mod_str
        print_po_snippet((ds_EN.modifiers, loc, loc), "date modifier")
    except AttributeError:
        pass

    try:
        loc = dd.__class__._qual_str
        print_po_snippet((ds_EN.qualifiers, loc, loc), "date quality")
    except AttributeError:
        pass
