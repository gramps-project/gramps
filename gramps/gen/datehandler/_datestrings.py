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

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateStrings")

#-------------------------------------------------------------------------
#
# DateStrings
#
#-------------------------------------------------------------------------
class DateStrings(object):
    """
    String tables for :class:`.DateDisplay` and :class:`.DateParser`.
    """

    # This table needs not be localized, it's only for parsing 
    # Swedish calendar dates using Swedish month names.
    # Display of these months uses the regular long_months.
    # TODO should we pack these into alt_long_months instead?
    swedish_SV = (
        "", "Januari", "Februari", "Mars",
        "April", "Maj", "Juni",
        "Juli", "Augusti", "September",
        "Oktober", "November", "December"
        )


    def __init__(self, locale):
        _ = locale.translation.lexgettext

        self.long_months = ( "",
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("localized lexeme inflections||January"), 
            _("localized lexeme inflections||February"), 
            _("localized lexeme inflections||March"), 
            _("localized lexeme inflections||April"), 
            _("localized lexeme inflections||May"), 
            _("localized lexeme inflections||June"), 
            _("localized lexeme inflections||July"), 
            _("localized lexeme inflections||August"), 
            _("localized lexeme inflections||September"), 
            _("localized lexeme inflections||October"), 
            _("localized lexeme inflections||November"), 
            _("localized lexeme inflections||December") )

        self.short_months = ( "",
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("localized lexeme inflections - short month form||Jan"), 
            _("localized lexeme inflections - short month form||Feb"), 
            _("localized lexeme inflections - short month form||Mar"), 
            _("localized lexeme inflections - short month form||Apr"), 
            _("localized lexeme inflections - short month form||May"), 
            _("localized lexeme inflections - short month form||Jun"), 
            _("localized lexeme inflections - short month form||Jul"), 
            _("localized lexeme inflections - short month form||Aug"), 
            _("localized lexeme inflections - short month form||Sep"), 
            _("localized lexeme inflections - short month form||Oct"), 
            _("localized lexeme inflections - short month form||Nov"), 
            _("localized lexeme inflections - short month form||Dec") )

        _ = locale.translation.sgettext
        self.alt_long_months = ( "",
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to add proper alternatives to be recognized in your localized
            # DateParser code!
            _("alternative month names for January||"), 
            _("alternative month names for February||"), 
            _("alternative month names for March||"), 
            _("alternative month names for April||"), 
            _("alternative month names for May||"), 
            _("alternative month names for June||"), 
            _("alternative month names for July||"), 
            _("alternative month names for August||"), 
            _("alternative month names for September||"), 
            _("alternative month names for October||"), 
            _("alternative month names for November||"), 
            _("alternative month names for December||") )

        self.calendar = (
# Must appear in the order indexed by Date.CAL_... numeric constants
                _("calendar|Gregorian"), 
                _("calendar|Julian"), 
                _("calendar|Hebrew"), 
                _("calendar|French Republican"), 
                _("calendar|Persian"), 
                _("calendar|Islamic"),
                _("calendar|Swedish") )
        _ = locale.translation.lexgettext

        self.hebrew = (
            "", 
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Hebrew month lexeme|Tishri"), 
            _("Hebrew month lexeme|Heshvan"), 
            _("Hebrew month lexeme|Kislev"), 
            _("Hebrew month lexeme|Tevet"), 
            _("Hebrew month lexeme|Shevat"), 
            _("Hebrew month lexeme|AdarI"), 
            _("Hebrew month lexeme|AdarII"), 
            _("Hebrew month lexeme|Nisan"), 
            _("Hebrew month lexeme|Iyyar"), 
            _("Hebrew month lexeme|Sivan"), 
            _("Hebrew month lexeme|Tammuz"), 
            _("Hebrew month lexeme|Av"), 
            _("Hebrew month lexeme|Elul")
            )

        self.french = (
            "", 
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("French month lexeme|Vendémiaire"), 
            _("French month lexeme|Brumaire"), 
            _("French month lexeme|Frimaire"), 
            _("French month lexeme|Nivôse"), 
            _("French month lexeme|Pluviôse"), 
            _("French month lexeme|Ventôse"), 
            _("French month lexeme|Germinal"), 
            _("French month lexeme|Floréal"), 
            _("French month lexeme|Prairial"), 
            _("French month lexeme|Messidor"), 
            _("French month lexeme|Thermidor"), 
            _("French month lexeme|Fructidor"), 
            _("French month lexeme|Extra"), 
            )

        self.islamic = (
            "", 
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Islamic month lexeme|Muharram"), 
            _("Islamic month lexeme|Safar"), 
            _("Islamic month lexeme|Rabi`al-Awwal"), 
            _("Islamic month lexeme|Rabi`ath-Thani"), 
            _("Islamic month lexeme|Jumada l-Ula"), 
            _("Islamic month lexeme|Jumada t-Tania"), 
            _("Islamic month lexeme|Rajab"), 
            _("Islamic month lexeme|Sha`ban"), 
            _("Islamic month lexeme|Ramadan"), 
            _("Islamic month lexeme|Shawwal"), 
            _("Islamic month lexeme|Dhu l-Qa`da"), 
            _("Islamic month lexeme|Dhu l-Hijja"),
            )

        self.persian = (
            "", 
            # TRANSLATORS: see 
            # http://gramps-project.org/wiki/index.php?title=Translating_Gramps#Translating_dates
            # to learn how to select proper inflection to be used in your localized
            # DateDisplayer code!
            _("Persian month lexeme|Farvardin"), 
            _("Persian month lexeme|Ordibehesht"), 
            _("Persian month lexeme|Khordad"), 
            _("Persian month lexeme|Tir"), 
            _("Persian month lexeme|Mordad"), 
            _("Persian month lexeme|Shahrivar"), 
            _("Persian month lexeme|Mehr"), 
            _("Persian month lexeme|Aban"), 
            _("Persian month lexeme|Azar"), 
            _("Persian month lexeme|Dey"), 
            _("Persian month lexeme|Bahman"), 
            _("Persian month lexeme|Esfand"),
            )

        self.modifiers = ("", 
                # TRANSLATORS: if the modifier is after the date
                # put the space ahead of the word instead of after it
                _("date modifier|before "), 
                # TRANSLATORS: if the modifier is after the date
                # put the space ahead of the word instead of after it
                _("date modifier|after "), 
                # TRANSLATORS: if the modifier is after the date
                # put the space ahead of the word instead of after it
                _("date modifier|about "), 
                "", "", "")

        self.qualifiers = ("", 
                _("date quality|estimated "), 
                _("date quality|calculated "), 
                )

        # 6753: localized day names. Eventually should sprout into 
        # a per-calendar type thing instead.
        self.long_days = ("",
                _("Sunday"),
                _("Monday"),
                _("Tuesday"),
                _("Wednesday"),
                _("Thursday"),
                _("Friday"),
                _("Saturday"),
            )

if __name__ == '__main__':
    import sys
    from ..utils.grampslocale import GrampsLocale
    from gramps.gen.const import GRAMPS_LOCALE as glocale
    from ._grampslocale import (_deprecated_long_months as old_long, 
            _deprecated_short_months as old_short,
            _deprecated_long_days as old_days)
    from ._datedisplay import DateDisplay
    import gettext
    lang = glocale.lang
    lang_short = lang[:2]
    available_langs = glocale.get_available_translations()
    if glocale.check_available_translations(lang) is None:
        print ("Translation for current language {lang} not available.\n" 
                "Available translations: {list}.\n"
                "Does po/{lang_short}*.po exist in gramps source tree?!\n"
                "Please set your LANG / LC_ALL environment to something else...\n".format(
                    lang=lang, list=available_langs, lang_short=lang_short), 
                file=sys.stderr)
        sys.exit(1)

    print ("# Generating snippets for {}*.po\n"
            "# Available languages: {}".format(
                    lang_short, available_langs))
    glocale = GrampsLocale(languages=(lang))
    dd = glocale.date_displayer
    ds = dd._ds
    glocale_EN = GrampsLocale(languages=('en'))
    ds_EN = DateStrings(glocale_EN)

    filename = __file__

    try:
        localized_months = dd.__class__.long_months
    except AttributeError:
        localized_months = old_long

    def print_po_snippet(en_loc_old_lists, context):
        for m,localized,old in zip(*en_loc_old_lists):
            if m == "":
                continue
            if m == localized:
                localized = old
            print ('#: {file}:{line}\n'
                   'msgid "{context}{en_month}"\n'
                   'msgstr "{localized_month}"\n'.format(
                       context = context,
                       file = filename,
                       line = print_po_snippet.line,
                       en_month = m,
                       localized_month = localized))
            print_po_snippet.line += 1
    print_po_snippet.line = 10000

    try:
        localized_months = dd.__class__.long_months
    except AttributeError:
        localized_months = old_long
    print_po_snippet((ds_EN.long_months, localized_months, old_long),
            "localized lexeme inflections||")
    try:
        localized_months = dd.__class__.short_months
    except AttributeError:
        localized_months = old_short
    print_po_snippet((ds_EN.short_months, localized_months, old_short),
            "localized lexeme inflections - short month form||")

    try:
        loc = dd.__class__.hebrew
        print_po_snippet((ds_EN.hebrew, loc, loc),
                "Hebrew month lexeme|")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.french
        print_po_snippet((ds_EN.french, loc, loc),
                "French month lexeme|")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.islamic
        print_po_snippet((ds_EN.islamic, loc, loc),
                "Islamic month lexeme|")
    except AttributeError:
        pass

    try:
        loc = dd.__class__.persian
        print_po_snippet((ds_EN.persian, loc, loc),
                "Persian month lexeme|")
    except AttributeError:
        pass

    try:
        loc = dd.__class__._mod_str
        print_po_snippet((ds_EN.modifiers, loc, loc),
                "date modifier|")
    except AttributeError:
        pass

    try:
        loc = dd.__class__._qual_str
        print_po_snippet((ds_EN.qualifiers, loc, loc),
                "date quality|")
    except AttributeError:
        pass

    print_po_snippet((ds_EN.long_days, old_days, old_days), "")
