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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsGconfKeys
import DateParser
import DateDisplay

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
_lang = os.environ.get('LANG','C')
    

_lang_to_parser = {
    'C'       : DateParser.DateParser,
    'en_US'   : DateParser.DateParser,
    'en_GB'   : DateParser.DateParser,
    }

_lang_to_display = {
    'C'       : DateDisplay.DateDisplay,
    'en_US'   : DateDisplay.DateDisplay,
    'en_GB'   : DateDisplay.DateDisplay,
    }

#-------------------------------------------------------------------------
#
# Functions 
#
#-------------------------------------------------------------------------
def create_parser():
    try:
        return _lang_to_parser[_lang]()
    except:
        return DateParser.DateParser()

def create_display():
    try:
        val = GrampsGconfKeys.get_date_format(_lang_to_display[_lang].formats)
        return _lang_to_display[_lang](val)
    except:
        return DateDisplay.DateDisplay(3)

def get_date_formats():
    try:
        return _lang_to_display[_lang].formats
    except:
        return DateDisplay.DateDisplay.formats

def set_format(val):
    try:
        _lang_to_display[_lang].format = val
    except:
        pass

def get_format():
    try:
        return _lang_to_display[_lang].format
    except:
        print "not found"
        return 0
