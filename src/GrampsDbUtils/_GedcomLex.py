#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id: _ReadGedcom.py 8032 2007-02-03 17:11:05Z hippy $

"Import from GEDCOM"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import re
import string
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ansel_utf8 import ansel_to_utf8

from _GedcomInfo import *
from _GedTokens import *

#-------------------------------------------------------------------------
#
# latin/utf8 conversions
#
#-------------------------------------------------------------------------

def _empty_func(a,b):
    return

def utf8_to_latin(s):
    return s.encode('iso-8859-1','replace')

def latin_to_utf8(s):
    if type(s) == unicode:
        return s
    else:
        return unicode(s,'iso-8859-1')

def nocnv(s):
    return unicode(s)

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
ANSEL = 1
UNICODE = 2
UPDATE = 25

_transtable = string.maketrans('','')
_delc = _transtable[0:8] + _transtable[10:31]
_transtable2 = _transtable[0:128] + ('?' * 128)

ged2gramps = {}
for _val in personalConstantEvents.keys():
    _key = personalConstantEvents[_val]
    if _key != "":
        ged2gramps[_key] = _val

for _val in familyConstantEvents.keys():
    _key = familyConstantEvents[_val]
    if _key != "":
        ged2gramps[_key] = _val


#-------------------------------------------------------------------------
#
# GedLine
#
#-------------------------------------------------------------------------

intRE       = re.compile(r"\s*(\d+)\s*$")
nameRegexp  = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
snameRegexp = re.compile(r"/([^/]*)/([^/]*)")
modRegexp   = re.compile(r"\s*(INT|EST|CAL)\s+(.*)$")
calRegexp   = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D([^@]+)@\s*(.*)$")
rangeRegexp = re.compile(r"\s*BET\s+@#D([^@]+)@\s*(.*)\s+AND\s+@#D([^@]+)@\s*(.*)$")
spanRegexp  = re.compile(r"\s*FROM\s+@#D([^@]+)@\s*(.*)\s+TO\s+@#D([^@]+)@\s*(.*)$")
intRegexp   = re.compile(r"\s*INT\s+([^(]+)\((.*)\)$")

_calendar_map = {
    "FRENCH R" : RelLib.Date.CAL_FRENCH,
    "JULIAN"   : RelLib.Date.CAL_JULIAN,
    "HEBREW"   : RelLib.Date.CAL_HEBREW,
}

_quality_map = {
    'CAL' : RelLib.Date.QUAL_CALCULATED,
    'INT' : RelLib.Date.QUAL_CALCULATED,
    'EST' : RelLib.Date.QUAL_ESTIMATED,
}

_sex_map = {
    'F' : RelLib.Person.FEMALE,
    'M' : RelLib.Person.MALE,
}

class GedLine:

    def __init__(self, data):
        self.line = data[4]
        self.level = data[0]
        self.token = data[1]
        self.token_text = data[3]
        self.data = data[2]

        if self.level == 0:
            if self.token_text and self.token_text[0] == '@' and self.token_text[-1] == '@':
                self.token = TOKEN_ID
                self.token_text = self.token_text[1:-1]
        else:
            f = MAP_DATA.get(self.token)
            if f:
                f(self)

    def do_nothing(self):
        pass

    def calc_sex(self):
        self.data = _sex_map.get(self.data,RelLib.Person.UNKNOWN)

    def calc_date(self):
        self.data = extract_date(self.data)

    def calc_unknown(self):
        token = ged2gramps.get(self.token_text)
        if token:
            self.token = TOKEN_GEVENT
            self.data = token
        
    def __repr__(self):
        return "%d: %d (%d:%s) %s" % (self.line, self.level, self.token, 
                                      self.token_text, self.data)

MAP_DATA = {
    TOKEN_UNKNOWN : GedLine.calc_unknown,
    TOKEN_DATE    : GedLine.calc_date,
    TOKEN_SEX     : GedLine.calc_sex,
    }




#-------------------------------------------------------------------------
#
# extract_date
#
#-------------------------------------------------------------------------
import RelLib
import DateHandler

def extract_date(text):
    dateobj = RelLib.Date()
    try:
        # extract out the MOD line
        match = modRegexp.match(text)
        if match:
            (mod, text) = match.groups()
            qual = _quality_map.get(mod, RelLib.Date.QUAL_NONE)
        else:
            qual = RelLib.Date.QUAL_NONE

        # parse the range if we match, if so, return
        match = rangeRegexp.match(text)
        if match:
            (cal1,data1,cal2,data2) = match.groups()

            cal = _calendar_map.get(cal1, RelLib.Date.CAL_GREGORIAN)
                    
            start = DateHandler.parser.parse(data1)
            stop =  DateHandler.parser.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_RANGE, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj

        # parse a span if we match
        match = spanRegexp.match(text)
        if match:
            (cal1,data1,cal2,data2) = match.groups()

            cal = _calendar_map.get(cal1, RelLib.Date.CAL_GREGORIAN)
                    
            start = DateHandler.parser.parse(data1)
            stop =  DateHandler.parser.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_SPAN, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj
        
        match = calRegexp.match(text)
        if match:
            (abt,cal,data) = match.groups()
            dateobj = self.dp.parse("%s %s" % (abt, data))
            dateobj.set_calendar(_calendar_map.get(cal, RelLib.Date.CAL_GREGORIAN))
            dateobj.set_quality(qual)
            return dateobj
        else:
            dval = DateHandler.parser.parse(text)
            dval.set_quality(qual)
            return dval
    except IOError:
        return self.dp.set_text(text)

#-------------------------------------------------------------------------
#
# Reader - serves as the lexical analysis engine
#
#-------------------------------------------------------------------------
class Reader:

    def __init__(self,name):
        self.f = open(name,'rU')
        self.current_list = []
        self.eof = False
        self.cnv = None
        self.broken_conc = False
        self.cnt = 0
        self.index = 0

    def set_charset_fn(self,cnv):
        self.cnv = cnv

    def set_broken_conc(self,broken):
        self.broken_conc = broken

    def readline(self):
        if len(self.current_list) <= 1 and not self.eof:
            self.readahead()
        try:
            return GedLine(self.current_list.pop())
        except:
            return None

    def readahead(self):
        while len(self.current_list) < 5:
            old_line = self.f.readline()
            self.index += 1
            line = old_line.strip('\r\n')
            if not line:
                if line != old_line:
                    continue
                else:
                    self.f.close()
                    self.eof = True
                    break
            if self.cnv:
                try:
                    line = self.cnv(line)
                except:
                    line = self.cnv(line.translate(_transtable2))

            line = line.split(None,2) + ['']

            try:
                val = line[2].translate(_transtable,_delc)
            except IndexError:
                msg = _("Invalid GEDCOM syntax at line %d was ignored.") % self.index
                continue
                
            try:
                level = int(line[0])
            except:
                level = 0

            data = (level,tokens.get(line[1],TOKEN_UNKNOWN), val,
                    line[1], self.index)

            if data[1] == TOKEN_CONT:
                l = self.current_list[0]
                self.current_list[0] = (l[0],l[1],l[2]+'\n'+data[2],l[3],l[4])
            elif data[1] == TOKEN_CONC:
                l = self.current_list[0]
                if self.broken_conc:
                    new_value = u"%s %s" % (l[2],data[2])
                else:
                    new_value = l[2] + data[2]
                self.current_list[0] = (l[0],l[1],new_value,l[3],l[4])
            else:
                self.current_list.insert(0,data)

if __name__ == "__main__":
    import sys

    def run():
        print "Reading", sys.argv[1]
        a = Reader(sys.argv[1])
        while True:
            line = a.readline()
            #print line
            if not line: break

    import Utils
    Utils.profile(run)

    print extract_date("20 JAN 2000")
    print extract_date("EST 20 JAN 2000")
    print extract_date("CAL 20 JAN 2000")
    print extract_date("ABT 20 JAN 2000")
    print extract_date("INT 20 JAN 2000")
    print extract_date("BET 20 JAN 2000 AND FEB 2000")
    print extract_date("FROM 20 JAN 2000 TO FEB 2000")
