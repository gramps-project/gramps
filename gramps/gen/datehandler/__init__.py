#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..utils.grampslocale import GrampsLocale
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
# import prerequisites for localized handlers
from ._datehandler import (LANG, LANG_SHORT, LANG_TO_PARSER, LANG_TO_DISPLAY,
                           locale_tformat, main_locale)
from . import _datestrings

# Import all the localized handlers
from . import _date_ar
from . import _date_bg
from . import _date_ca
from . import _date_cs
from . import _date_da
from . import _date_de
from . import _date_el
from . import _date_es
from . import _date_fi
from . import _date_fr
from . import _date_hr
from . import _date_hu
from . import _date_is
from . import _date_it
from . import _date_ja
from . import _date_lt
from . import _date_nb
from . import _date_nl
from . import _date_pl
from . import _date_pt
from . import _date_ru
from . import _date_sk
from . import _date_sl
from . import _date_sr
from . import _date_sv
from . import _date_uk
from . import _date_zh_CN
from . import _date_zh_TW

# the following makes sure we use the LC_TIME value for date display & parsing
dlocale = GrampsLocale(lang=glocale.calendar)


# Initialize global parser
try:
    if LANG in LANG_TO_PARSER:
        parser = LANG_TO_PARSER[LANG](plocale=dlocale)
    else:
        parser = LANG_TO_PARSER[LANG_SHORT](plocale=dlocale)
except:
    logging.warning(
        _("Date parser for '%s' not available, using default") % LANG)
    parser = LANG_TO_PARSER["C"](plocale=dlocale)

# Initialize global displayer
try:
    from ..config import config
    val = config.get('preferences.date-format')
except:
    val = 0

try:
    if LANG in LANG_TO_DISPLAY:
        displayer = LANG_TO_DISPLAY[LANG](val, blocale=dlocale)
    else:
        displayer = LANG_TO_DISPLAY[LANG_SHORT](val, blocale=dlocale)
except:
    logging.warning(
        _("Date displayer for '%s' not available, using default") % LANG)
    displayer = LANG_TO_DISPLAY["C"](val, blocale=dlocale)


# Import utility functions
from ._dateutils import *

# set GRAMPS_RESOURCES then: python3 -m gramps.gen.datehandler.__init__
if __name__ == "__main__":
    from ._datedisplay import DateDisplay
    m = 0
    date_handlers = sorted(LANG_TO_DISPLAY.items())
    for l,d in date_handlers:
        if len(l) != 2 and l not in ('zh_TW'): # Chinese has two date_handlers
            continue
        if l.upper() == l and (l.lower(),d) in date_handlers:
            continue # don't need to see the upper-case variant also
        m = max(m, len(d.formats))
        print("{}: {} {} own-f:{} own-dc:{} own-dg:{}".format(
            l, len(d.formats), d.formats,
            d.formats != DateDisplay.formats,
            d._display_calendar != DateDisplay._display_calendar,
            d._display_gregorian != DateDisplay._display_gregorian))
    print("MAX: ", m)
