
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
    
    Error = _("Illegal Date")

    range = 1
    normal = 0

    from_str = _("(from|between|bet)")
    to_str = _("(and|to|-)")
    
    efmt = re.compile(r"\s*(from|between|bet)\.?\s+(.+)\s+(and|to)\s+(.+)\s*$",
                      re.IGNORECASE)

    fmt = re.compile(r"\s*" + from_str + r"\.?\s+(.+)\s+" + to_str + r"\s+(.+)\s*$",
                     re.IGNORECASE)

    def __init__(self):
	self.start = SingleDate()
	self.stop = SingleDate()
        self.range = 0
        self.text = ""

    def get_start_date(self):
        return self.start

    def get_stop_date(self):
        return self.stop

    def getYear(self):
        return self.get_start_date().getYear()

    def getMonth(self):
        return self.get_start_date().getMonth()

    def getDay(self):
        return self.get_start_date().getDay()

    def getStopYear(self):
        return self.get_stop_date().getYear()

    def getStopMonth(self):
        return self.get_stop_date().getMonth()

    def getStopDay(self):
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
        function = SingleDate.fmtFunc[Date.formatCode]

	if self.range == 1:
	    return _("from") + " " + function(self.start) + " " + \
                   _("to") + " " + function(self.stop)
        elif self.range == -1:
            return self.text
	else:
	    return function(self.start)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getQuoteDate(self):
        function = SingleDate.fmtFunc[Date.formatCode]

	if self.range == 1:
	    return _("from") + " " + function(self.start) + " " + \
                   _("to") + " " + function(self.stop)
        elif self.range == -1 and self.text:
            return '"' + self.text + '"'
	else:
	    return function(self.start)

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


    m2v = { _("abt")    : about ,
            _("about")  : about,
            _("est")    : about ,
            _("circa")  : about,
            _("around") : about,
            _("before") : before,
            _("bef")    : before,
            _("after")  : after,
            _("aft")    : after }

    modifiers = "(" + \
                _("abt") + '|' + \
                _("about") + '|' + \
                _("est") + '|' + \
                _("circa") + '|' + \
                _("around") + '|' + \
                _("before") + '|' + \
                _("after") + '|' + \
                _("aft") + '|' + \
                _("bef") + ')'
    
    start = "^\s*" + modifiers + "?\s*"
    
    fmt1 = re.compile(start + "(\S+)(\s+\d+\s*,)?\s*(\d+)?\s*$",
                      re.IGNORECASE)
    fmt2 = re.compile(start + "(\d+)\s+(\S+)(\s+\d+)?\s*$",
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
        if self.year != other.year:
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
        if val > 0 and val < 13:
            self.month = val - 1
        else:
            self.month = -1

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
        if val > 0 or val < 32:
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
        if SingleDate.m2num.has_key(string.lower(text[0:3])):
            self.month = SingleDate.m2num[string.lower(text[0:3])]
        else:
            self.month = -1

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setMonthStrEng(self,text):
        if SingleDate.em2num.has_key(string.lower(text[0:3])):
            self.month = SingleDate.em2num[string.lower(text[0:3])]
        else:
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
                retval = "%d" % self.year
            elif self.year == -1:
                retval = SingleDate.emname[self.month]
            else:	
                retval = "%s %d" % (SingleDate.emname[self.month],self.year)
        elif self.month == -1:
            retval = "%d" % self.year
        else:
            month = SingleDate.emname[self.month]
            if self.year == -1:
                retval = "%d %s ????" % (self.day,month)
            else:
                retval = "%d %s %d" % (self.day,month,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT " + retval

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
        retval = ""

        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                retval = SingleDate.mname[self.month]
            else:	
                retval = "%s %d" % (SingleDate.mname[self.month],self.year)
        elif self.month == -1:
            retval = "%d" % self.year
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
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                month = SingleDate.mname[self.month]
                retval = string.upper(month[0:3])
            else:	
                month = SingleDate.mname[self.month]
                retval = "%s %d" % (string.upper(month[0:3]),self.year)
        elif self.month == -1:
            retval =  "%d" % self.year
        else:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%s %d, ????" % (string.upper(month[0:3]),self.day)
            else:
                retval = "%s %d, %d" % (string.upper(month[0:3]),self.day,self.year)

	if self.mode == SingleDate.about:
            retval = "ABT" + ' ' + retval
            
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
    def getFmt3(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                month = SingleDate.mname[self.month]
                retval = string.upper(month[0:3])
            else:	
                month = SingleDate.mname[self.month]
                retval = "%s %d" % (string.upper(month[0:3]),self.year)
        elif self.month == -1:
            retval = "%d" % self.year
        else:
            month = SingleDate.mname[self.month]
            if self.year == -1:
                retval = "%d %s ????" % (self.day,string.upper(month[0:3]))
            else:
                retval = "%d %s %d" % (self.day,string.upper(month[0:3]),self.year)

        if self.mode == SingleDate.about:
            retval = "ABT " + retval

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
    def getFmt4(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                retval = "%d/??/??" % self.month+1
            else:
                retval = "%d/??/%d" % (self.month+1,self.year)
        elif self.month == -1:
            retval = "??-%d-%d" % (self.day,self.year)
        else:
            if self.year == -1:
                retval = "%d/%d/????" % (self.month+1,self.day)
            else:
                retval = "%d/%d/%d" % (self.month+1,self.day,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT" + ' ' + retval

        if self.mode == SingleDate.before:
            retval = "BEFORE " + retval
        elif self.mode == SingleDate.after:
            retval = "AFTER " + retval

        return retval

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def getFmt5(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                retval = "%d-??-??" % self.month+1
            else:
                retval = "%d-??-%d" % (self.month+1,self.year)
        elif self.month == -1:
            retval = "??-%d-%d" % (self.day,self.year)
        else:
            if self.year == -1:
                retval = "%d-%d-????" % (self.month+1,self.day)
            else:
                retval = "%d-%d-%d" % (self.month+1,self.day,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT" + ' ' + retval

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
    def getFmt6(self):
        retval = ""
        
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                retval = "??/%d/??" % self.month+1
            else:
                retval = "??/%d/%d" % (self.month+1,self.year)
        elif self.month == -1:
            retval = "%d/??/%d" % (self.day,self.year)
        else:
            if self.year == -1:
                retval = "%d/%d/????" % (self.day,self.month+1)
            else:
                retval = "%d/%d/%d" % (self.day,self.month+1,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT" + ' ' + retval

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
    def getFmt7(self):
        retval = ""
        if self.month == -1 and self.day == -1 and self.year == -1 :
            pass
        elif self.day == -1:
            if self.month == -1:
                retval = "%d" % self.year
            elif self.year == -1:
                retval = "??-%d-??" % self.month+1
            else:
                retval = "??-%d-%d" % (self.month+1,self.year)
        elif self.month == -1:
            retval = "%d-??-%d" % (self.day,self.year)
        elif self.year == -1:
            retval = "%d-%d-????" % (self.day,self.month+1)
        else:
            retval = "%d-%d-%d" % (self.day,self.month+1,self.year)

        if self.mode == SingleDate.about:
            retval = "ABT" + ' ' + retval

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
    fmtFunc = [ getFmt1, getFmt2, getFmt3, getFmt4, getFmt5, getFmt6, getFmt7 ]

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
            self.setDay(string.atoi(matches[1]))
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?':
                    self.setYear(-1)
                else:
                    self.setYear(string.atoi(val))
            else:
                self.setYear(-1)
            return 1
        
        match = SingleDate.fmt5.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonth(-1)
            self.setDay(-1)
            self.setYear(string.atoi(matches[1]))
            return 1

        match = SingleDate.fmt7.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            try:
                self.setMonth(string.atoi(matches[1]))
            except:
                self.setMonth(-1)
            try:
                self.setYear(string.atoi(matches[2]))
            except:
                self.setYear(-1)
            return 1

        match = SingleDate.fmt3.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            if Date.entryCode == 0:
                try:
                    self.setMonth(string.atoi(matches[1]))
                except:
                    self.setMonth(-1)
                try:
                    self.setDay(string.atoi(matches[2]))
                except:
                    self.setDay(-1)
            else:
                try:
                    self.setMonth(string.atoi(matches[2]))
                except:
                    self.setMonth(-1)
                try:
                    self.setDay(string.atoi(matches[1]))
                except:
                    self.setDay(-1)
            val = matches[3]
            if val == None or val[0] == '?':
                self.setYear(-1)
            else:
                self.setYear(string.atoi(val))
            return 1

        match = SingleDate.fmt1.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonthStr(matches[1])
            val = matches[2]
            if val:
                self.setDay(string.atoi(string.replace(val,',','')))
            else:
                self.setDay(-1)
	    val = matches[3]
            if val == None or val[0] == '?':
                self.setYear(-1)
            else:
                self.setYear(string.atoi(val))
            return 1

        match = SingleDate.fmt4.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonthStr(matches[1])
            self.setDay(-1)
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?' :
                    self.setYear(-1)
                else:
                    self.setYear(string.atoi(val))
            return 1

        match = SingleDate.fmt6.match(text)
        if match != None:
            matches = match.groups()
            self.getMode(matches[0])
            self.setMonth(matches[1])
            self.setDay(-1)
            self.setYear(-1)
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
            self.setDay(string.atoi(matches[1]))
            if len(matches) == 4:
                val = matches[3]
                if val == None or val[0] == '?':
                    self.setYear(-1)
                else:
                    self.setYear(string.atoi(val))
            else:
                self.setYear(-1)
        else:
            self.setYear(-1)
            self.setMonth(-1)
            self.setDay(-1)
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

		

