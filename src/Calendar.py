#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2003  Donald N. Allingham
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
"""
Calendar conversion routines for GRAMPS. 

The original algorithms for this module came from Scott E. Lee's
C implementation. The original C source can be found at Scott's
web site at http://www.scottlee.com
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

from gettext import gettext as _
import re
import Errors

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
UNDEF = -999999
EXACT = 0
ABOUT = 1
BEFORE = 2
AFTER = 3

#-------------------------------------------------------------------------
#
# Regular expressions for parsing
#
#-------------------------------------------------------------------------
_modifiers = '(' + \
             _("abt\.?") + '|' + \
             _("about") + '|' + \
             _("est\.?") + '|' + \
             _("circa") + '|' + \
             _("around") + '|' + \
             _("before") + '|' + \
             _("after") + '|' + \
             _("aft\.?") + '|' + \
             _("bef\.?") + \
             '|abt|aft|after|before|bef)'
_start = "^\s*" + _modifiers + "?\s*"
fmt1 = re.compile(_start+"(\S+)(\s+\d+\s*,)?\s*([?\d]+)?\s*$", re.IGNORECASE)
fmt2 = re.compile(_start+"(\d+)\.?\s+([^\d]+)(\s+\d+)?\s*$", re.IGNORECASE)
fmt3 = re.compile(_start+r"([?\d]+)\s*[./-]\s*([?\d]+)\s*[./-]\s*([?\d]+)\s*$",
               re.IGNORECASE)
fmt7 = re.compile(_start+r"([?\d]+)\s*[./-]\s*([?\d]+)\s*$", re.IGNORECASE)
fmt4 = re.compile(_start+"(\S+)\s+(\d+)\s*$", re.IGNORECASE)
fmt5 = re.compile(_start+"(\d+)\s*$", re.IGNORECASE)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def set_format_code(code):
    Calendar.FORMATCODE = code
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_format_code():
    return Calendar.FORMATCODE

#-------------------------------------------------------------------------
#
# Calendar - base calendar
#
#-------------------------------------------------------------------------
class Calendar:

    ENTRYCODE = 0
    FORMATCODE = 0

    MONTHS = [
        _("January"),   _("February"),  _("March"),    _("April"),
        _("May"),       _("June"),      _("July"),     _("August"),
        _("September"), _("October"),   _("November"), _("December")]

    M2NUM = {
        (unicode(MONTHS[0])[0:3]).lower(): 1,   (unicode(MONTHS[1])[0:3]).lower(): 2,
        (unicode(MONTHS[2])[0:3]).lower(): 3,   (unicode(MONTHS[3])[0:3]).lower(): 4,
        (unicode(MONTHS[4])[0:3]).lower(): 5,   (unicode(MONTHS[5])[0:3]).lower(): 6,
        (unicode(MONTHS[6])[0:3]).lower(): 7,   (unicode(MONTHS[7])[0:3]).lower(): 8,
        (unicode(MONTHS[8])[0:3]).lower(): 9,   (unicode(MONTHS[9])[0:3]).lower(): 10,
        (unicode(MONTHS[10])[0:3]).lower(): 11, (unicode(MONTHS[11])[0:3]).lower(): 12
        }

    M2V = {
        _("abt")    : ABOUT,        _("about")  : ABOUT,
        _("abt.")   : ABOUT,        _("est")    : ABOUT,
        _("est.")   : ABOUT,        _("circa")  : ABOUT,
        _("around") : ABOUT,        _("before") : BEFORE,
        _("bef")    : BEFORE,       _("bef.")   : BEFORE,
        _("after")  : AFTER,        _("aft.")   : AFTER,
        _("aft")    : AFTER,
            # And the untranslated versions for reading saved data from XML.
        "abt"	    : ABOUT,        "about"	: ABOUT,
        "bef"       : BEFORE,       "bef."      : BEFORE,
        "aft."      : AFTER,        "abt."      : ABOUT,
        "est."      : ABOUT,        "est"       : ABOUT,
        "after"	    : AFTER,        "before"    : BEFORE,
        "aft"       : AFTER,
        }

    MODE = {
        ABOUT : _("about"),
        BEFORE : _("before"),
        AFTER : _("after")}

    EM2NUM ={
        "jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4,
        "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8,
        "sep" : 9, "oct" :10, "nov" : 11,"dec" : 12
        }

    NAME  = "Undefined Calendar"
    TNAME = _("Undefined Calendar")

    def mlen(self):
        return -1

    def __init__(self,source=None):
        if source:
            self.get_ymd(source.get_sdn())

    def month(self,val):
        try:
	    return unicode(Calendar.MONTHS[val-1])
        except:
            return u'Illegal Month'

    def check(self,year,month,day):
        return 1

    def quote_display(self,year,month,day,mode):
        return "%04d-%02d-%02d (%s)" % (year,month,day,Calendar.NAME)

    def display(self,year,month,day,mode):
        return _FMT_FUNC[Calendar.FORMATCODE](self,year,month,day,mode)

    def format_yymmdd(self,year,month,day,mode):
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "????-%02d-??" % (month)
            else:
                retval = "%04d-%02d" % (year,month)
        elif month == UNDEF:
            retval = "%04d-??-%02d" % (year,day)
        else:
            if year == UNDEF:
                retval = "????-%02d-%02d" % (month,day)
            else:
                retval = "%04d-%02d-%02d" % (year,month,day)
        return self.fmt_mode(retval,mode)

    def format_mon_dd_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        January 20, 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF:
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month)
            else:
                retval = "%s %d" % (self.month(month),year)
        elif month == UNDEF:
            retval = str(year)
        else:
            if year == UNDEF:
                retval = "%s %d, ????" % (self.month(month),day)
            else:
                retval = "%s %d, %d" % (self.month(month),day,year)

        return self.fmt_mode(retval,mode)


    def format_MON_dd_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        January 20, 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF:
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            if year == UNDEF:
                retval = "%s %d, ????" % (self.month(month).upper()[0:3],day)
            else:
                retval = "%s %d, %d" % (self.month(month).upper()[0:3],day,year)

        return self.fmt_mode(retval,mode)

    def format_dd_mon_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        20 January 2000
        """
        if year==UNDEF:
            if month == UNDEF:
                d = ""
            elif day == UNDEF:
                d = self.month(month)
            else:
                d = "%02d %s" % (day,self.month(month))
        elif month == UNDEF:
            d = str(year)
        elif day == UNDEF:
            d = "%s %d" % (self.month(month),year)
        else:
            d = "%02d %s %d" % (day,self.month(month),year)

        return self.fmt_mode(d,mode)

    def format_dd_MON_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD. Month Year, such as
        20. January 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            month_str = self.month(month).upper()[0:3]
            if year == UNDEF:
                retval = "%d %s ????" % (day,month_str)
            else:
                retval = "%d %s %d" % (day,month_str,year)

        return self.fmt_mode(retval,mode)

    def format_dd_dot_MON_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD. Month Year, such as
        20. January 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            month_str = self.month(month).upper()[0:3]
            if year == UNDEF:
                retval = "%d. %s ????" % (day,month_str)
            else:
                retval = "%d. %s %d" % (day,month_str,year)

        return self.fmt_mode(retval,mode)

    def format4(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,"/")

    def format5(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,"-")

    def format6(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,"/")

    def format7(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,"-")

    def format8(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,".")

    def format9(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,".")

    def format11(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,"/")

    def format12(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,"-")

    def format13(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,".")

    def _get_mmddyyyy(self,year,month,day,mode,sep):
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "%02d%s??%s??" % (month,sep,sep)
            else:
                retval = "%02d%s??%s%04d" % (month,sep,sep,year)
        elif month == UNDEF:
            retval = "??%s%02d%s%04d" % (sep,day,sep,year)
        else:
            if year == UNDEF:
                retval = "%02d%s%02d%s????" % (month,sep,day,sep)
            else:
                retval = "%02d%s%02d%s%04d" % (month,sep,day,sep,year)

        return self.fmt_mode(retval,mode)

    def _get_yyyymmdd(self,year,month,day,mode,sep):
        retval = ""
        
        if month == UNDEF and day == UNDEF and year == UNDEF :
            pass
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "????%s%02d%s??" % (sep,month,sep)
            else:
                retval = "%04d%s%02d" % (year,sep,month)
        elif month == UNDEF:
            retval = "%04d%s??%s%02d" % (year,sep,sep,day)
        else:
            if year == UNDEF:
                retval = "????%s%02d%s%02d" % (sep,month,sep,day)
            else:
                retval = "%02d%s%02d%s%02d" % (year,sep,month,sep,day)

        return self.fmt_mode(retval,mode)

    def _get_ddmmyyyy(self,year,month,day,mode,sep):
        retval = ""
        
        if month == UNDEF and day == UNDEF and year == UNDEF :
            pass
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "??%s%02d%s??" % (sep,month,sep)
            else:
                retval = "??%s%02d%s%04d" % (sep,month,sep,year)
        elif month == UNDEF:
            retval = "%02d%s??%s%04d" % (day,sep,sep,year)
        else:
            if year == UNDEF:
                retval = "%02d%s%02d%s????" % (day,sep,month,sep)
            else:
                retval = "%02d%s%02d%s%04d" % (day,sep,month,sep,year)

        return self.fmt_mode(retval,mode)

    def fmt_mode(self,val,mode):
        if Calendar.MODE.has_key(mode):
            return "%s %s" % (Calendar.MODE[mode],val)
        else:
            return val

    def get_ymd(self,val):
        return (0,0,0)

    def get_sdn(self,y,m,d):
        return 0

    def set_mode_value(self,val):
        if not val:
            return EXACT
        else:
            try:
                return Calendar.M2V[val.lower()]
            except KeyError:
                return EXACT

    def set_value(self,s):
        try:
            return int(s)
        except:
            return UNDEF

    def set_month_string(self,text):
        val = unicode(text)[0:3]
        val = val.lower()
        try:
            return Calendar.M2NUM[val]
        except KeyError:
            if Calendar.EM2NUM.has_key(val):
                return Calendar.EM2NUM[val]
            else:
                return UNDEF

    def set(self,text):
        mode = UNDEF
        year = UNDEF
        month = UNDEF
        day = UNDEF
        
        match = fmt2.match(text)
        if match != None:
	    matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(unicode(matches[2]))
            if month != UNDEF:
                day = self.set_value(matches[1])
                if len(matches) == 4 and matches[3] != None:
                    year = self.set_value(matches[3])
                return (year,month,day,mode)
        
        match = fmt5.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0]) 
            year = self.set_value(matches[1])
            return (year,month,day,mode)

        match = fmt7.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            if Calendar.ENTRYCODE == 2:
                month = self.set_value(matches[2])
                year = self.set_value(matches[1])
            else:
                month = self.set_value(matches[1])
                year = self.set_value(matches[2])
            return (year,month,day,mode)

        match = fmt3.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            if Calendar.ENTRYCODE == 0:
                month = self.set_value(matches[1])
                day = self.set_value(matches[2])
                year = self.set_value(matches[3])
            elif Calendar.ENTRYCODE == 1:
                month = self.set_value(matches[2])
                day = self.set_value(matches[1])
                year = self.set_value(matches[3])
            else:
                month = self.set_value(matches[2])
                day = self.set_value(matches[3])
                year = self.set_value(matches[1])
            return (year,month,day,mode)

        match = fmt1.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(unicode(matches[1]))
            if month != UNDEF:
                if matches[2]:
                    val = matches[2].replace(',','')
                    day = self.set_value(val)
                year = self.set_value(matches[3])
                return (year,month,day,mode)

        match = fmt4.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(unicode(matches[1]))
            if month != UNDEF:
                if len(matches) == 4:
                    year = self.set_value(matches[3])
                return (year,month,day,mode)

        raise Errors.DateError


_FMT_FUNC = [
    Calendar.format_mon_dd_year,
    Calendar.format_MON_dd_year,
    Calendar.format_dd_MON_year,
    Calendar.format4,
    Calendar.format5,
    Calendar.format6,
    Calendar.format7,
    Calendar.format8,
    Calendar.format9,
    Calendar.format_dd_dot_MON_year,
    Calendar.format11,
    Calendar.format12,
    Calendar.format13,
    ]

#-------------------------------------------------------------------------
#
# Calendar registration
#
#-------------------------------------------------------------------------

_calendars = {}

def register( class_obj ):
    _calendars[class_obj.NAME] = class_obj

def find_calendar(name):
    try:
        return _calendars[name]
    except:
        return None

def calendar_names():
    dlist = _calendars.values()
    dlist.sort()
    return dlist
