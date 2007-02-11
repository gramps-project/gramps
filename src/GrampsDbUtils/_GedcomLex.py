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
from _GedcomTokens import *
import RelLib
from DateHandler._DateParser import DateParser

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

ged2attr = {}
for _val in personalConstantAttributes.keys():
    _key = personalConstantAttributes[_val]
    if _key != "":
        ged2attr[_key] = _val
    
#-------------------------------------------------------------------------
#
# GedLine
#
#-------------------------------------------------------------------------

intRE       = re.compile(r"\s*(\d+)\s*$")
modRegexp   = re.compile(r"\s*(INT|EST|CAL)\s+(.*)$")
calRegexp   = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D([^@]+)@\s*(.*)$")
rangeRegexp = re.compile(r"\s*BET\s+@#D([^@]+)@\s*(.*)\s+AND\s+@#D([^@]+)@\s*(.*)$")
spanRegexp  = re.compile(r"\s*FROM\s+@#D([^@]+)@\s*(.*)\s+TO\s+@#D([^@]+)@\s*(.*)$")
intRegexp   = re.compile(r"\s*INT\s+([^(]+)\((.*)\)$")
snameRegexp = re.compile(r"/([^/]*)/([^/]*)")

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

#-----------------------------------------------------------------------
#
# GedLine - represents a tokenized version of a GEDCOM line
#
#-----------------------------------------------------------------------
class GedcomDateParser(DateParser):

    month_to_int = {
        'jan' : 1,  'feb' : 2,  'mar' : 3,  'apr' : 4,
        'may' : 5,  'jun' : 6,  'jul' : 7,  'aug' : 8,
        'sep' : 9,  'oct' : 10, 'nov' : 11, 'dec' : 12,
        }

#-----------------------------------------------------------------------
#
# GedLine - represents a tokenized version of a GEDCOM line
#
#-----------------------------------------------------------------------
class GedLine:
    """
    GedLine is a class the represents a GEDCOM line. The form of a  GEDCOM line 
    is:
    
    <LEVEL> <TOKEN> <TEXT>

    This gets parsed into

    Line Number, Level, Token Value, Token Text, and Data

    Data is dependent on the context the Token Value. For most of tokens, this is
    just a text string. However, for certain tokens where we know the context, we
    can provide some value. The current parsed tokens are:

    TOKEN_DATE   - RelLib.Date
    TOKEN_SEX    - RelLib.Person gender item
    TOEKN_UKNOWN - Check to see if this is a known event
    """

    def __init__(self, data):
        """
        If the level is 0, then this is a top level instance. In this case, we may
        find items in the form of:

        <LEVEL> @ID@ <ITEM>

        If this is not the top level, we check the MAP_DATA array to see if there is
        a conversion function for the data.
        """
        self.line = data[4]
        self.level = data[0]
        self.token = data[1]
        self.token_text = data[3].strip()
        self.data = data[2]

        if self.level == 0:
            if self.token_text and self.token_text[0] == '@' and self.token_text[-1] == '@':
                self.token = TOKEN_ID
                self.token_text = self.token_text[1:-1]
                self.data = self.data.strip()
        else:
            f = MAP_DATA.get(self.token)
            if f:
                f(self)

    def calc_sex(self):
        """
        Converts the data field to a RelLib token indicating the gender
        """
        self.data = _sex_map.get(self.data.strip(),RelLib.Person.UNKNOWN)

    def calc_date(self):
        """
        Converts the data field to a RelLib.Date object
        """
        self.data = extract_date(self.data)

    def calc_unknown(self):
        """
        Checks to see if the token maps a known GEDCOM event. If so, we 
        change the type from UNKNOWN to TOKEN_GEVENT (gedcom event), and
        the data is assigned to the associated GRAMPS EventType
        """
        token = ged2gramps.get(self.token_text)
        if token:
            self.token = TOKEN_GEVENT
            self.data = token
        else:
            token = ged2attr.get(self.token_text)
            if token:
                attr = RelLib.Attribute()
                attr.set_value(self.data)
                attr.set_type(token)
                self.token = TOKEN_ATTR
                self.data = attr

    def calc_note(self):
        d = self.data.strip()
        if len(d) > 2 and d[0] == '@' and d[-1] == '@':
            self.token = TOKEN_RNOTE
            self.data = d[1:-1]

    def calc_nchi(self):
        attr = RelLib.Attribute()
        attr.set_value(self.data)
        attr.set_type(RelLib.AttributeType.NUM_CHILD)
        self.data = attr
        self.token = TOKEN_ATTR

    def calc_attr(self):
        attr = RelLib.Attribute()
        attr.set_value(self.data)
        attr.set_type((RelLib.AttributeType.CUSTOM, self.token_text))
        self.data = attr
        self.token = TOKEN_ATTR

    def calc_lds(self):
        self.data = _
        self.token = TOKEN_ATTR

    def __repr__(self):
        return "%d: %d (%d:%s) %s" % (self.line, self.level, self.token, 
                                      self.token_text, self.data)

#-------------------------------------------------------------------------
#
# MAP_DATA - kept as a separate table, so that it is static, and does not
#            have to be initialized every time in the GedLine constructor
#
#-------------------------------------------------------------------------
MAP_DATA = {
    TOKEN_UNKNOWN : GedLine.calc_unknown,
    TOKEN_DATE    : GedLine.calc_date,
    TOKEN_SEX     : GedLine.calc_sex,
    TOKEN_NOTE    : GedLine.calc_note,
    TOKEN_NCHI    : GedLine.calc_nchi,
    TOKEN__STAT   : GedLine.calc_attr,
    TOKEN__UID    : GedLine.calc_attr,
    TOKEN_AFN     : GedLine.calc_attr,
    }

#-------------------------------------------------------------------------
#
# extract_date
#
#-------------------------------------------------------------------------

_dp = GedcomDateParser()

def extract_date(text):
    """
    Converts the specified text to a RelLib.Date object.
    """
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
                    
            start = _dp.parse(data1)
            stop =  _dp.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_RANGE, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj

        # parse a span if we match
        match = spanRegexp.match(text)
        if match:
            (cal1,data1,cal2,data2) = match.groups()

            cal = _calendar_map.get(cal1, RelLib.Date.CAL_GREGORIAN)
                    
            start = _dp.parse(data1)
            stop =  _dp.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_SPAN, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj
        
        match = calRegexp.match(text)
        if match:
            (abt,cal,data) = match.groups()
            dateobj = _dp.parse("%s %s" % (abt, data))
            dateobj.set_calendar(_calendar_map.get(cal, RelLib.Date.CAL_GREGORIAN))
            dateobj.set_quality(qual)
            return dateobj

        dateobj = _dp.parse(text)
        dateobj.set_quality(qual)
        return dateobj
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
        self.cnt = 0
        self.index = 0
        self.func_map = {
            TOKEN_CONT : self._fix_token_cont,
            TOKEN_CONC : self._fix_token_conc,
            }

    def set_charset_fn(self,cnv):
        self.cnv = cnv

    def set_broken_conc(self,broken):
        self.func_map = {
            TOKEN_CONT : self._fix_token_cont,
            TOKEN_CONC : self._fix_token_broken_conc,
            }

    def readline(self):
        if len(self.current_list) <= 1 and not self.eof:
            self.readahead()
        try:
            return GedLine(self.current_list.pop())
        except:
            return None

    def _fix_token_cont(self, data):
        l = self.current_list[0]
        new_value = l[2]+'\n'+data[2]
        self.current_list[0] = (l[0], l[1], new_value, l[3], l[4])

    def _fix_token_conc(self, data):
        l = self.current_list[0]
        new_value = l[2] + data[2]
        self.current_list[0] = (l[0], l[1], new_value, l[3], l[4])

    def _fix_token_broken_conc(self, data):
        l = self.current_list[0]
        new_value = u"%s %s" % (l[2], data[2])
        self.current_list[0] = (l[0], l[1], new_value, l[3], l[4])

    def readahead(self):
        while len(self.current_list) < 5:
            line = self.f.readline()
            self.index += 1
            if not line:
                self.f.close()
                self.eof = True
                return

            if self.cnv:
                try:
                    line = self.cnv(line)
                except:
                    line = self.cnv(line.translate(_transtable2))
            else:
                line = unicode(line)

            line = line.split(None,2) + ['']

            val = line[2].rstrip('\r\n')
                
            try:
                level = int(line[0])
            except:
                level = 0

            data = (level, tokens.get(line[1], TOKEN_UNKNOWN), val, line[1], self.index)

            func = self.func_map.get(data[1])
            if func:
                func(data)
            else:
                self.current_list.insert(0, data)

if __name__ == "__main__":
    import sys

    def run():
        print "Reading", sys.argv[1]
        a = Reader(sys.argv[1])
        while True:
            line = a.readline()
            print line
            if not line: break

#    import Utils
#    Utils.profile(run)
    run()

    print extract_date("20 JAN 2000")
    print extract_date("EST 20 JAN 2000")
    print extract_date("CAL 20 JAN 2000")
    print extract_date("ABT 20 JAN 2000")
    print extract_date("INT 20 JAN 2000")
    print extract_date("BET 20 JAN 2000 AND FEB 2000")
    print extract_date("FROM 20 JAN 2000 TO FEB 2000")
