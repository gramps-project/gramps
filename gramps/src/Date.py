#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Support for the dates"

import re
import string
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class Date:
    formatCode = 0
    entryCode = 0
    
    Error = "Illegal Date"

    range = 1
    normal = 0

    from_str = _("(from|between|bet|bet.)")
    to_str = _("(and|to|-)")
    
    efmt = re.compile(r"\s*(from|between|bet)\s+(.+)\s+(and|to)\s+(.+)\s*$",
                      re.IGNORECASE)

    fmt = re.compile(r"\s*" + from_str + r"\s+(.+)\s+" + to_str + r"\s+(.+)\s*$",
                     re.IGNORECASE)

    def __init__(self):
	self.start = SingleDate()
	self.stop = None
        self.range = 0
        self.text = ""

    def get_start_date(self):
        return self.start

    def get_stop_date(self):
        if self.stop == None:
            self.stop = SingleDate()
        return self.stop

    def getYear(self):
        return self.get_start_date().getYear()

    def getMonth(self):
        return self.get_start_date().getMonth()

    def getDay(self):
        return self.get_start_date().getDay()

    def getStopYear(self):
        if self.stop == None:
            self.stop = SingleDate()
        return self.get_stop_date().getYear()

    def getStopMonth(self):
        if self.stop == None:
            self.stop = SingleDate()
        return self.get_stop_date().getMonth()

    def getStopDay(self):
        if self.stop == None:
            self.stop = SingleDate()
        return self.get_stop_date().getDay()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def set(self,text):
        match = Date.fmt.match(text)
        try:
            if match:
                matches = match.groups()
                self.start.set(matches[1])
                if self.stop == None:
                    self.stop = SingleDate()
                self.stop.set(matches[3])
                self.range = 1
            else:
                self.start.set(text)
                self.range = 0
        except:
            self.range = -1
            self.text = text

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getDate(self):
	if self.range == 0:
	    return _func(self.start)
        elif self.range == -1:
            return self.text
	else:
	    return "%s %s %s %s" % ( _("from"),_func(self.start),_("to"), _func(self.stop))

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getQuoteDate(self):
	if self.range == 0:
	    return _func(self.start)
        elif self.range == -1:
            if self.text:
                return '"%s"' % self.text
            else:
                return ''
	else:
	    return "%s %s %s %s" % ( _("from"),_func(self.start),_("to"), _func(self.stop))

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getSaveDate(self):
	if self.range == 1:
	    return "FROM " + self.start.getSaveDate() + " TO " + self.stop.getSaveDate()
        elif self.range == -1:
            return self.text
	else:
            return self.start.getSaveDate()

    def isEmpty(self):
        if self.start.year == -1 and self.start.month == -1 and self.start.day == -1:
            return 1
        else:
            return 0

    def isValid(self):
        if self.range == -1:
            return 0
        else:
            return 1

    def isRange(self):
        if self.range == -1:
            return 0
        else:
            return 1
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def quick_set(self,text):
        try:
            match = Date.efmt.match(text)
            if match:
                matches = match.groups()
                self.start.set(matches[1])
                if self.stop == None:
                    self.stop = SingleDate()
                self.stop.set(matches[3])
                self.range = 1
            else:
                try:
                    self.start.quick_set(text)
                    self.range = 0
                except:
                    self.start.set(text)
                    self.range = 0
        except:
            self.range = -1
            self.text = text

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def set_format_code(code):
    global _func
    Date.formatCode = code
    _func = SingleDate.fmtFunc[code]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_format_code():
    return Date.formatCode

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class SingleDate:
    "Date handling"
    
    exact = 0
    about = 1
    before = 2
    after = 3
    
    mname = [ _("January"),
              _("February"),
              _("March"),
              _("April"),
              _("May"),
              _("June"),
              _("July"),
              _("August"),
              _("September"),
              _("October"),
              _("November"),
              _("December") ]

    emname =[ 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC' ]

    m2num = { string.lower(mname[0][0:3]) : 0,
              string.lower(mname[1][0:3]) : 1,
              string.lower(mname[2][0:3]) : 2,
              string.lower(mname[3][0:3]) : 3,
              string.lower(mname[4][0:3]) : 4,
              string.lower(mname[5][0:3]) : 5,
              string.lower(mname[6][0:3]) : 6,
              string.lower(mname[7][0:3]) : 7,
              string.lower(mname[8][0:3]) : 8,
              string.lower(mname[9][0:3]) : 9,
              string.lower(mname[10][0:3]) : 10,
              string.lower(mname[11][0:3]) : 11 }

    em2num ={ "jan" : 0, "feb" : 1, "mar" : 2, "apr" : 3,
              "may" : 4, "jun" : 5, "jul" : 6, "aug" : 7,
              "sep" : 8, "oct" : 9, "nov" : 10,"dec" : 11 }

    m2v = { _("abt")    : about ,
            _("about")  : about,
            _("abt.")   : about,
            _("est")    : about ,
            _("est.")   : about ,
            _("circa")  : about,
            _("around") : about,
            _("before") : before,
            _("bef")    : before,
            _("bef.")   : before,
            _("after")  : after,
            _("aft.")   : after,
            _("aft")    : after }

    modifiers = "(" + \
                _("abt") + '|' + \
                _("abt\.") + '|' + \
                _("about") + '|' + \
                _("est") + '|' + \
                _("est\.") + '|' + \
                _("circa") + '|' + \
                _("around") + '|' + \
                _("before") + '|' + \
                _("after") + '|' + \
                _("aft") + '|' + \
                _("aft\.") + '|' + \
                _("bef\.") + '|' + \
                _("bef") + ')'
    
    start = "^\s*" + modifiers + "?\s*"
    
    fmt1 = re.compile(start + "(\S+)(\s+\d+\s*,)?\s*(\d+)?\s*$",
                      re.IGNORECASE)
    fmt2 = re.compile(start + "(\d+)\.?\s+(\S+)(\s+\d+)?\s*$",
                      re.IGNORECASE)
    quick= re.compile(start + "(\d+)?\s(\S\S\S)?\s(\d+)?",
                      re.IGNORECASE)
    fmt3 = re.compile(start + r"([?\d]+)\s*[./-]\s*([?\d]+)\s*[./-]\s*([?\d]+)\s*$",
                      re.IGNORECASE)
    fmt7 = re.compile(start + r"([?\d]+)\s*[./-]\s*([?\d]+)\s*$",
                      re.IGNORECASE)
    fmt4 = re.compile(start + "(\S+)\s+(\d+)\s*$",
                      re.IGNORECASE)
    fmt5 = re.compile(start + "(\d+)\s*$",
                      re.IGNORECASE)
    fmt6 = re.compile(start + "(\S+)\s*$",
                      re.IGNORECASE)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self):
        self.month = -1
        self.day = -1
        self.year = -1
        self.mode = SingleDate.exact

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __cmp__(self,other):
        if other == None:
            return 0
        elif self.year != other.year:
            return cmp(self.year,other.year)
        elif self.month != other.month:
            return cmp(self.month,other.month)
        elif self.day != other.day:
            return cmp(self.day,other.day)
        elif self.mode != other.mode:
            if self.mode == SingleDate.exact:
                return -1
            else:
                return 1
        else:
            return 0
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setMode(self,val):
        if val == None:
            self.mode = SingleDate.exact
        else:
            val = string.lower(val)
            self.mode = SingleDate.m2v[val]

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setMonth(self,val):
        if val > 12:
            self.month = -1
        else:
            self.month = val - 1

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getMonth(self):
        return self.month + 1

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setDay(self,val):
        self.day = val

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getDay(self):
	return self.day

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setYear(self,val):
        self.year = val

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getYear(self):
        return self.year

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setMonthStr(self,text):
        try:
            self.month = SingleDate.m2num[string.lower(text[0:3])]
        except KeyError:
            self.month = -1

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setMonthStrEng(self,text):
        try:
            self.month = SingleDate.em2num[string.lower(text[0:3])]
        except KeyError:
            self.month = -1

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getMonthStr(self):
	return SingleDate.mname[self.month]

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getSaveDate(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                retval = SingleDate.emname[self.month]
            else:	
                retval = "%s %d" % (SingleDate.emname[self.month],self.year)
        elif self.month == -1:
            retval = str(self.year)
        else:
            month = SingleDate.emname[self.month]
            if self.year == -1:
                retval = "%d %s ????" % (self.day,month)
            else:
                retval = "%d %s %d" % (self.day,month,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT %s"  % retval

        if self.mode == SingleDate.before:
            retval = _("BEFORE") + " " + retval
        elif self.mode == SingleDate.after:
            retval = _("AFTER") + " " + retval

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt1(self):

        if self.month == -1 and self.day == -1 and self.year == -1 :
            return ""
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                retval = SingleDate.mname[self.month]
            else:	
                retval = "%s %d" % (SingleDate.mname[self.month],self.year)
        elif self.month == -1:
            retval = str(self.year)
        else:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%s %d, ????" % (month,self.day)
            else:
                retval = "%s %d, %d" % (month,self.day,self.year)

        if self.mode == SingleDate.about:
	    retval = _("about") + ' ' + retval

        if self.mode == SingleDate.before:
            retval = _("before") + ' ' + retval
        elif self.mode == SingleDate.after:
            retval = _("after") + ' ' + retval

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt2(self):
        if self.month == -1 and self.day == -1 and self.year == -1 :
            return ""
        elif self.month != -1 and self.month != -1:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%s %d, ????" % (string.upper(month[0:3]),self.day)
            else:
                retval = "%s %d, %d" % (string.upper(month[0:3]),self.day,self.year)
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                month = SingleDate.mname[self.month]
                retval = string.upper(month[0:3])
            else:	
                month = SingleDate.mname[self.month]
                retval = "%s %d" % (string.upper(month[0:3]),self.year)
        else:
            retval =  str(self.year)

        if self.mode == SingleDate.about:
            retval = "%s %s" % (_("abt"),retval)
        if self.mode == SingleDate.before:
            retval = "%s %s" % (_("before"),retval)
        elif self.mode == SingleDate.after:
            retval = "%s %s" % (_("after"),retval)

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt3(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                month = SingleDate.mname[self.month]
                retval = string.upper(month[0:3])
            else:
                month = SingleDate.mname[self.month]
                retval = "%s %d" % (string.upper(month[0:3]),self.year)
        elif self.month == -1:
            retval = str(self.year)
        else:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%d %s ????" % (self.day,string.upper(month[0:3]))
            else:
                retval = "%d %s %d" % (self.day,string.upper(month[0:3]),self.year)

        if self.mode == SingleDate.about:
            retval = "%s %s" % (_("ABT"),retval)
        if self.mode == SingleDate.before:
            retval = "%s %s" % (_("BEFORE"),retval)
        elif self.mode == SingleDate.after:
            retval = "%s %s" % (_("AFTER"),retval)

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt10(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                retval = SingleDate.mname[self.month]
            else:
                month = SingleDate.mname[self.month]
                retval = "%s %d" % (month,self.year)
        elif self.month == -1:
            retval = str(self.year)
        else:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%d. %s ????" % (self.day,month)
            else:
                retval = "%d. %s %d" % (self.day,month,self.year)

        if self.mode == SingleDate.about:
            retval = "%s %s" % (_("ABT"),retval)
        if self.mode == SingleDate.before:
            retval = "%s %s" % (_("BEFORE"),retval)
        elif self.mode == SingleDate.after:
            retval = "%s %s" % (_("AFTER"),retval)

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def get_mmddyyyy(self,sep):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                retval = "%d%s??%s??" % (self.month+1,sep,sep)
            else:
                retval = "%d%s??%s%d" % (self.month+1,sep,sep,self.year)
        elif self.month == -1:
            retval = "??%s%d%s%d" % (sep,self.day,sep,self.year)
        else:
            if self.year == -1:
                retval = "%d%s%d%s????" % (self.month+1,sep,self.day,sep)
            else:
                retval = "%d%s%d%s%d" % (self.month+1,sep,self.day,sep,self.year)

        if self.mode == SingleDate.about:
            retval = "%s %s" % (_("ABT"),retval)

        if self.mode == SingleDate.before:
            retval = "%s %s" % (_("BEFORE"),retval)
        elif self.mode == SingleDate.after:
            retval = "%s %s" % (_("AFTER"),retval)

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt4(self):
        return self.get_mmddyyyy("/")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt5(self):
        return self.get_mmddyyyy("-")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt8(self):
        return self.get_mmddyyyy(".")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def get_ddmmyyyy(self,sep):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = str(self.year)
            elif self.year == -1:
                retval = "??%s%d%s??" % (sep,self.month+1,sep)
            else:
                retval = "??%s%d%s%d" % (sep,self.month+1,sep,self.year)
        elif self.month == -1:
            retval = "%d%s??%s%d" % (self.day,sep,sep,self.year)
        else:
            if self.year == -1:
                retval = "%d%s%d%s????" % (self.day,sep,self.month+1,sep)
            else:
                retval = "%d%s%d%s%d" % (self.day,sep,self.month+1,sep,self.year)

        if self.mode == SingleDate.about:
            retval = "%s %s" % (_("ABT"),retval)
        if self.mode == SingleDate.before:
            retval = "%s %s" % (_("BEFORE"),retval)
        elif self.mode == SingleDate.after:
            retval = "%s %s" % (_("AFTER"),retval)

        return retval
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt6(self):
        return self.get_ddmmyyyy("/")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt7(self):
        return self.get_ddmmyyyy("-")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt9(self):
        return self.get_ddmmyyyy(".")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    fmtFunc = [ getFmt1, getFmt2, getFmt3, getFmt4, getFmt5, getFmt6,
                getFmt7, getFmt8, getFmt9, getFmt10 ]

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getDate(self):
        function = SingleDate.fmtFunc[Date.formatCode]
        return function(self)
    
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getMode(self,val):
        if val == None:
            self.mode = SingleDate.exact
        elif string.lower(val)[0:3] == "bef":
            self.mode = SingleDate.before
        elif string.lower(val)[0:3] == "aft":
            self.mode = SingleDate.after
        else:
            self.mode = SingleDate.about
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def set(self,text):
        match = SingleDate.fmt2.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonthStr(matches[2])
            if self.month == -1:
                raise Date.Error,text
            self.day = int(matches[1])
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?':
                    self.year = -1
                else:
                    self.year = int(val)
            else:
                self.year = -1
            return 1
        
        match = SingleDate.fmt5.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.month = -1
            self.day = -1
            self.year = int(matches[1])
            return 1

        match = SingleDate.fmt7.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            try:
                self.month = int(matches[1])-1
                if self.month > 11:
                    raise Date.Error,text
            except ValueError:
                self.month = -1
            try:
                self.year = int(matches[2])
            except ValueError:
                self.year = -1
            return 1

        match = SingleDate.fmt3.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            if Date.entryCode == 0:
                try:
                    self.month = int(matches[1])-1
                    if self.month > 11:
                        raise Date.Error,text
                except ValueError:
                    self.month = -1
                try:
                    self.day = int(matches[2])
                except ValueError:
                    self.day = -1
            else:
                try:
                    self.month = int(matches[2])-1
                    if self.month > 11:
                        raise Date.Error,text
                except ValueError:
                    self.month = -1
                try:
                    self.day = int(matches[1])
                except ValueError:
                    self.day = -1
            val = matches[3]
            if val == None or val[0] == '?':
                self.year = -1
            else:
                self.year = int(val)
            return 1

        match = SingleDate.fmt1.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonthStr(matches[1])
            if self.month == -1:
                raise Date.Error,text
            val = matches[2]
            if val:
                self.day = int(string.replace(val,',',''))
            else:
                self.day = -1
	    val = matches[3]
            if val == None or val[0] == '?':
                self.year = -1
            else:
                self.year = int(val)
            return 1

        match = SingleDate.fmt4.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonthStr(matches[1])
            if self.month == -1:
                raise Date.Error,text
            self.day = -1
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?' :
                    self.year = -1
                else:
                    self.year = int(val)
            return 1

        match = SingleDate.fmt6.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.month = int(matches[1])-1
            if self.month > 11:
                raise Date.Error,text
            self.day = -1
            self.year = -1
            return 1

        raise Date.Error,text

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def quick_set(self,text):
        match = SingleDate.quick.match(text)
        if match != None:
            matches = match.groups()
            self.setMode(matches[0])
            self.setMonthStrEng(matches[2])
            if self.month == -1:
                raise Date.Error,text
            self.day = int(matches[1])
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?':
                    self.year = -1
                else:
                    self.year = int(val)
            else:
                self.year = -1
        else:
            self.year = -1
            self.month = -1
            self.day = -1
            raise Date.Error,text
        
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def compare_dates(f,s):
    first = f.get_start_date()
    second = s.get_start_date()
    if first.year != second.year:
        return cmp(first.year,second.year)
    elif first.month != second.month:
        return cmp(first.month,second.month)
    else:
        return cmp(first.day,second.day)


_func = SingleDate.fmtFunc[0]

if __name__ == "__main__":

    def checkit(s):
        d = Date()
        d.set(s)
        print s, ':', d.getDate(), ':', d.getQuoteDate()

    for code in range(0,7):
        Date.formatCode = code
        Date.entryCode = 0
        print "\nFormat Code = %d\n" % code
        checkit("June 11")
        checkit("1923")
        checkit("11/12/1293")
        checkit("11 JAN 1923")
        checkit("11-1-1929")
        checkit("4/3/1203")
        checkit("3/1203")
        checkit("?/3/1203")
        checkit("January 4, 1923")
        checkit("before 3/3/1239")
        checkit("est 2-3-1023")
        checkit("between January 4, 1234 and NOV 4, 1245")
        checkit("from 3-2-1234 to 5-4-2345")
        Date.entryCode = 1
        checkit("1/12/1999")
        checkit("12/11/1999")
        checkit("summer")

    print "----------"
    checkit("BET. 1994 - 1999")

