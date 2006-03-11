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
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateHandler")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _DateParser import DateParser
from _DateDisplay import DateDisplay, DateDisplayEn

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
_lang = locale.getlocale(locale.LC_TIME)[0]
if _lang:
    _lang_short = _lang.split('_')[0]
else:
    _lang_short = "C"

_lang_to_parser = {
    'C'      : DateParser,
    'en'     : DateParser,
    }

_lang_to_display = {
    'C'      : DateDisplayEn,
    'en'     : DateDisplayEn,
    'zh_CN'  : DateDisplay,
    'zh_TW'  : DateDisplay,
    'zh_SG'  : DateDisplay,
    'zh_HK'  : DateDisplay,
    'ja_JP'  : DateDisplay,
    'ko_KR'  : DateDisplay,
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
from PluginUtils import load_plugins
from const import datesDir
load_plugins(datesDir)

#-------------------------------------------------------------------------
#
# Initialize global parser
#
#-------------------------------------------------------------------------

try:
    if _lang_to_parser.has_key(_lang):
        parser = _lang_to_parser[_lang]()
    else:
        parser = _lang_to_parser[_lang_short]()
except:
    print "Date parser for",_lang,"not available, using default"
    parser = _lang_to_parser["C"]()

try:
    import Config
    val = Config.get_date_format(_lang_to_display[_lang].formats)
except:
    try:
        val = Config.get_date_format(_lang_to_display["C"].formats)
    except:
        val = 0

try:
    if _lang_to_display.has_key(_lang):
        displayer = _lang_to_display[_lang](val)
    else:
        displayer = _lang_to_display[_lang_short](val)
except:
    print "Date displayer for",_lang,"not available, using default"
    displayer = _lang_to_display["C"](val)
    

#--------------------------------------------------------------
#
# Convenience functions
#
#--------------------------------------------------------------

def set_date(date_base, text) :
    """
    Sets the date of the DateBase instance.
    
    The date is parsed into a L{Date} instance.
    
    @param date: String representation of a date. The locale specific
        L{DateParser} is used to parse the string into a GRAMPS L{Date}
        object.
    @type date: str
    """
    parser.set_date(date_base.get_date_object(),text)

def get_date(date_base) :
    """
    Returns a string representation of the date of the DateBase instance.
    
    This representation is based off the default date display format
    determined by the locale's L{DateDisplay} instance.
    @return: Returns a string representing the DateBase date
    @rtype: str
    """
    return displayer.display(date_base.get_date_object())

def get_quote_date(self) :
    """
    Returns a string representation of the date of the DateBase instance.
    
    This representation is based off the default date display format
    determined by the locale's L{DateDisplay} instance. The date is
    enclosed in quotes if the L{Date} is not a valid date.
    
    @return: Returns a string representing the DateBase date
    @rtype: str
    """
    return displayer.quote_display(date_base.get_date_object())
