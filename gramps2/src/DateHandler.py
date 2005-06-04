#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Class handling language-specific selection for date parser and displayer.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import locale

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import DateParser
import DateDisplay

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
_lang = locale.getlocale(locale.LC_TIME)[0]

_lang_to_parser = {
    'C'      : DateParser.DateParser,
    'en_AU'  : DateParser.DateParser,
    'en_BW'  : DateParser.DateParser,
    'en_CA'  : DateParser.DateParser,
    'en_DK'  : DateParser.DateParser,
    'en_GB'  : DateParser.DateParser,
    'en_HK'  : DateParser.DateParser,
    'en_IE'  : DateParser.DateParser,
    'en_IN'  : DateParser.DateParser,
    'en_NZ'  : DateParser.DateParser,
    'en_PH'  : DateParser.DateParser,
    'en_SE'  : DateParser.DateParser,
    'en_SG'  : DateParser.DateParser,
    'en_US'  : DateParser.DateParser,
    'en_ZA'  : DateParser.DateParser,
    'en_ZW'  : DateParser.DateParser,
    'en'     : DateParser.DateParser,
    }

_lang_to_display = {
    'C'      : DateDisplay.DateDisplayEn,
    'en_AU'  : DateDisplay.DateDisplayEn,
    'en_BW'  : DateDisplay.DateDisplayEn,
    'en_CA'  : DateDisplay.DateDisplayEn,
    'en_DK'  : DateDisplay.DateDisplayEn,
    'en_GB'  : DateDisplay.DateDisplayEn,
    'en_HK'  : DateDisplay.DateDisplayEn,
    'en_IE'  : DateDisplay.DateDisplayEn,
    'en_IN'  : DateDisplay.DateDisplayEn,
    'en_NZ'  : DateDisplay.DateDisplayEn,
    'en_PH'  : DateDisplay.DateDisplayEn,
    'en_SE'  : DateDisplay.DateDisplayEn,
    'en_SG'  : DateDisplay.DateDisplayEn,
    'en_US'  : DateDisplay.DateDisplayEn,
    'en_ZA'  : DateDisplay.DateDisplayEn,
    'en_ZW'  : DateDisplay.DateDisplayEn,
    'en'     : DateDisplay.DateDisplayEn,
    'zh_CN'  : DateDisplay.DateDisplay,
    'zh_TW'  : DateDisplay.DateDisplay,
    'zh_SG'  : DateDisplay.DateDisplay,
    'zh_HK'  : DateDisplay.DateDisplay,
    'ja_JP'  : DateDisplay.DateDisplay,
    'ko_KR'  : DateDisplay.DateDisplay,
    }

def get_date_formats():
    """
    Returns the lists supported formats for date parsers and displayers
    """
    try:
        return _lang_to_display[_lang].formats
    except:
        return _lang_to_display["C"].formats

def set_format(value):
    try:
        displayer.set_format(value)
    except:
        pass

def register_datehandler(locales,parse_class,display_class):
    """
    Registers the passed date parser class and date displayer
    classes with the specfied language locales.

    @param locales: tuple of strings containing language codes.
        The character encoding is not included, so the langauge
        should be in the form of fr_FR, not fr_FR.utf8
    @type locales: tuple
    @param parse_class: Class to be associated with parsing
    @type parse_class: DateParse
    @param display_class: Class to be associated with displaying
    @type display_class: DateDisplay
    """
    for lang_str in locales:
        _lang_to_parser[lang_str] = parse_class
        _lang_to_display[lang_str] = display_class
    

#-------------------------------------------------------------------------
#
# Import localized date classes
#
#-------------------------------------------------------------------------
from PluginMgr import load_plugins
from const import datesDir
load_plugins(datesDir)

#-------------------------------------------------------------------------
#
# Initialize global parser
#
#-------------------------------------------------------------------------

try:
    parser = _lang_to_parser[_lang]()
except:
    print "Date parser for",_lang,"not available, using default"
    parser = _lang_to_parser["C"]()

try:
    import GrampsKeys
    val = GrampsKeys.get_date_format(_lang_to_display[_lang].formats)
except:
    try:
        val = GrampsKeys.get_date_format(_lang_to_display["C"].formats)
    except:
        val = 0

try:
    displayer = _lang_to_display[_lang](val)
except:
    print "Date displayer for",_lang,"not available, using default"
    displayer = _lang_to_display["C"](val)
    
