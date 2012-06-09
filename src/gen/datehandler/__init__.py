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

# $Id$

"""
Class handling language-specific selection for date parser and displayer.
"""

# import prerequisites for localized handlers
from _datehandler import (LANG, LANG_SHORT, LANG_TO_PARSER, LANG_TO_DISPLAY, 
                          register_datehandler)

# Import all the localized handlers
import _date_bg
import _date_ca
import _date_cs
import _date_da
import _date_de
import _date_es
import _date_fi
import _date_fr
import _date_hr
import _date_it
import _date_lt
import _date_nb
import _date_nl
import _date_pl
import _date_pt
import _date_ru
import _date_sk
import _date_sl
import _date_sr
import _date_sv

# Initialize global parser
try:
    if LANG in LANG_TO_PARSER:
        parser = LANG_TO_PARSER[LANG]()
    else:
        parser = LANG_TO_PARSER[LANG_SHORT]()
except:
    print "Date parser for", LANG, "not available, using default"
    parser = LANG_TO_PARSER["C"]()

# Initialize global displayer
try:
    from gen.config import config
    val = config.get('preferences.date-format')
except:
    val = 0

try:
    if LANG in LANG_TO_DISPLAY:
        displayer = LANG_TO_DISPLAY[LANG](val)
    else:
        displayer = LANG_TO_DISPLAY[LANG_SHORT](val)
except:
    print "Date displayer for", LANG, "not available, using default"
    displayer = LANG_TO_DISPLAY["C"](val)


# Import utility functions
from _dateutils import *
