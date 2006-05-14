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

# $Id: _DateHandler.py 6136 2006-03-11 04:58:58Z rshura $

"""
Class handling language-specific selection for date parser and displayer.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from DateHandler import _lang_to_display, _lang, parser, displayer

#--------------------------------------------------------------
#
# Convenience functions
#
#--------------------------------------------------------------
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

def get_quote_date(date_base):
    """
    Returns a string representation of the date of the DateBase instance.
    
    This representation is based off the default date display format
    determined by the locale's L{DateDisplay} instance. The date is
    enclosed in quotes if the L{Date} is not a valid date.
    
    @return: Returns a string representing the DateBase date
    @rtype: str
    """
    return displayer.quote_display(date_base.get_date_object())
