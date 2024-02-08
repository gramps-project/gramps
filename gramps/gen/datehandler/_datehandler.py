#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2017       Paul Franklin
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
Class handling language-specific selection for date parser and displayer.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".gen.datehandler")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ._dateparser import DateParser
from ._datedisplay import DateDisplay, DateDisplayEn, DateDisplayGB
from ..constfunc import win
from ..const import GRAMPS_LOCALE as glocale
from ..utils.grampslocale import GrampsLocale

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
LANG = glocale.calendar

# If LANG contains ".UTF-8" use only the part to the left of "."
# Otherwise some date handler will not load.
if LANG and ".UTF-8" in LANG.upper():
    LANG = LANG.split(".")[0]

if not LANG:
    if "LANG" in os.environ:
        LANG = os.environ["LANG"]

if LANG:
    LANG_SHORT = LANG.split("_")[0]
else:
    LANG_SHORT = "C"

LANG = str(LANG)
LANG_SHORT = str(LANG_SHORT)

LANG_TO_PARSER = {
    "C": DateParser,
}

LANG_TO_DISPLAY = {
    "C": DateDisplayEn,
    "ko_KR": DateDisplay,
}

main_locale = {}  # this will be augmented by calls to register_datehandler

locale_tformat = {}  # locale "tformat" (date format) strings

for no_handler in (
    ("C", ("%d/%m/%Y",)),
    ("eo_EO", "eo", "Esperanto", ("%d/%m/%Y",)),  # 'eo_EO' is a placeholder
    ("sq_AL", "sq", "Albanian", ("%Y/%b/%d",)),
    ("ta_IN", "ta", "Tamil", ("%A %d %B %Y",)),
    ("tr_TR", "tr", "Turkish", ("%d/%m/%Y",)),
    ("vi_VN", "vi", "Vietnamese", ("%d/%m/%Y",)),
):
    format_string = ""
    for possible_format in no_handler:
        if isinstance(possible_format, tuple):
            format_string = possible_format[0]  # pre-seeded date format string
            # maintain legacy gramps transformations
            format_string = format_string.replace("%y", "%Y").replace("-", "/")
    for lang_str in no_handler:
        if isinstance(lang_str, tuple):
            continue
        main_locale[lang_str] = no_handler[0]
        locale_tformat[lang_str] = format_string  # locale's date format string


def register_datehandler(locales, parse_class, display_class):
    """
    Registers the passed date parser class and date displayer
    classes with the specified language locales.

    Set the parser_class and display_class ._locale attribute
    to the corresponding :class:`.GrampsLocale` object.

    :param locales: tuple of strings containing language codes.
                    The character encoding is not included, so the language
                    should be in the form of fr_FR, not fr_FR.utf8
    :type locales: tuple
    :param parse_class: Class to be associated with parsing
    :type parse_class: :class:`.DateParser`
    :param display_class: Class to be associated with displaying
    :type display_class: :class:`.DateDisplay`
    """
    format_string = ""
    for possible_format in locales:  # allow possibly embedding a date format
        if isinstance(possible_format, tuple):
            format_string = possible_format[0]  # pre-seeded date format string
            # maintain legacy gramps transformations
            format_string = format_string.replace("%y", "%Y").replace("-", "/")
    for lang_str in locales:
        if isinstance(lang_str, tuple):
            continue
        LANG_TO_PARSER[lang_str] = parse_class
        LANG_TO_DISPLAY[lang_str] = display_class
        main_locale[lang_str] = locales[0]
        locale_tformat[lang_str] = format_string  # locale's date format string

    parse_class._locale = display_class._locale = GrampsLocale(lang=locales[0])


register_datehandler(
    ("en_GB", "English_United Kingdom", ("%d/%m/%y",)), DateParser, DateDisplayGB
)

register_datehandler(
    ("en_US", "en", "English_United States", ("%m/%d/%y",)), DateParser, DateDisplayEn
)
