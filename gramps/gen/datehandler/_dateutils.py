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
import time

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..lib.date import Date
from . import LANG_TO_DISPLAY, LANG, parser, displayer

#--------------------------------------------------------------
#
# Convenience functions
#
#--------------------------------------------------------------
def get_date_formats(flocale=glocale):
    """
    Return the list of supported formats for date parsers and displayers.
    The UI language formats will be used unless another locale is fed in.

    :param flocale: allow deferred translation of date formats
    :type flocale: a :class:`.GrampsLocale` instance
    """
    # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
    trans_text = flocale.translation.sgettext
    try:
        return tuple(trans_text(fmt)
                     for fmt in LANG_TO_DISPLAY[flocale.lang](0).formats)
    except:
        return tuple(trans_text(fmt)
                     for fmt in LANG_TO_DISPLAY['C'](0).formats)

def set_format(value):
    try:
        displayer.set_format(value)
    except:
        pass

def set_date(date_base, text):
    """
    Set the date of the :class:`.DateBase` instance.

    The date is parsed into a :class:`.Date` instance.

    :param date_base: The :class:`.DateBase` instance to set the date to.
    :type date_base: :class:`.DateBase`
    :param text: The text to use for the text string in date
    :type text: str
    """
    parser.set_date(date_base.get_date_object(), text)

def get_date(date_base):
    """
    Return a string representation of the date of the :class:`.DateBase`
    instance.

    This representation is based off the default date display format
    determined by the locale's :class:`.DateDisplay` instance.

    :return: Returns a string representing the :class:`.DateBase` date
    :rtype: str
    """
    return displayer.display(date_base.get_date_object())

def get_date_valid(date_base):
    date_obj = date_base.get_date_object()
    return date_obj.get_valid()

def format_time(secs):
    """
    Format a time in seconds as a date in the preferred date format and a
    24 hour time as hh:mm:ss.
    """
    t = time.localtime(secs)
    d = Date(t.tm_year, t.tm_mon, t.tm_mday)
    return displayer.display(d) + time.strftime(' %X', t)
