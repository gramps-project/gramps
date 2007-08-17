#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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

# $Id: __init__.py 6133 2006-03-11 01:12:06Z rshura $

"""
Class handling language-specific selection for date parser and displayer.
"""

# import prerequisites for localized handlers
from _DateHandler import _lang, _lang_short, \
    _lang_to_parser, _lang_to_display, register_datehandler

# Import all the localized handlers
import _Date_de
import _Date_es
import _Date_fi
import _Date_fr
import _Date_lt
import _Date_nb
import _Date_nl
import _Date_ru
import _Date_sv
import _Date_sk
import _Date_pl

# Initialize global parser
try:
    if _lang_to_parser.has_key(_lang):
        parser = _lang_to_parser[_lang]()
    else:
        parser = _lang_to_parser[_lang_short]()
except:
    print "Date parser for",_lang,"not available, using default"
    parser = _lang_to_parser["C"]()

# Initialize global displayer
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


# Import utility functions
from _DateUtils import *
