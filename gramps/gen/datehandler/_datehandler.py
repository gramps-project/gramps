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
Class handling language-specific selection for date parser and displayer.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".gen.datehandler")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ._dateparser import DateParser
from ._datedisplay import DateDisplay, DateDisplayEn
from ..constfunc import win
from ..const import GRAMPS_LOCALE as glocale
from ..utils.grampslocale import GrampsLocale

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
LANG = glocale.calendar

# If LANG contains ".UTF-8" use only the part to the left of "."
# Otherwise some date handler will not load.
if LANG and ".UTF-8" in LANG.upper():
    LANG = LANG.split(".")[0]

if not LANG:
    if "LANG" in os.environ:
        LANG = os.environ["LANG"]

if LANG:
    LANG_SHORT = LANG.split('_')[0]
else:
    LANG_SHORT = "C"

LANG = str(LANG)
LANG_SHORT = str(LANG_SHORT)

LANG_TO_PARSER = {
    'C'                     : DateParser,
    'en'                    : DateParser,
    'English_United States' : DateParser,
    }

LANG_TO_DISPLAY = {
    'C'                     : DateDisplayEn,
    'en'                    : DateDisplayEn,
    'en_GB'                 : DateDisplayEn,
    'English_United States' : DateDisplayEn,
    'ko_KR'                 : DateDisplay,
    'nb_NO'                 : DateDisplay, # TODO this's in _date_nb, why here?
    }

def register_datehandler(locales,parse_class,display_class):
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
    for lang_str in locales:
        LANG_TO_PARSER[lang_str] = parse_class
        LANG_TO_DISPLAY[lang_str] = display_class

    parse_class._locale = display_class._locale = GrampsLocale(lang=locales[0])
