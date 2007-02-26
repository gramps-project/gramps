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

__revision__ = "$Revision: $"
__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------

import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from _GedcomInfo import *
from _GedcomTokens import *
import RelLib
from DateHandler._DateParser import DateParser

#-------------------------------------------------------------------------
#
# constants #
#-------------------------------------------------------------------------

GED2GRAMPS = {}
for _val in personalConstantEvents.keys():
    _key = personalConstantEvents[_val]
    if _key != "":
        GED2GRAMPS[_key] = _val

for _val in familyConstantEvents.keys():
    _key = familyConstantEvents[_val]
    if _key != "":
        GED2GRAMPS[_key] = _val

GED2ATTR = {}
for _val in personalConstantAttributes.keys():
    _key = personalConstantAttributes[_val]
    if _key != "":
        GED2ATTR[_key] = _val
    
#-------------------------------------------------------------------------
#
# GedLine
#
#-------------------------------------------------------------------------

MOD   = re.compile(r"\s*(INT|EST|CAL)\s+(.*)$")
CAL   = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D([^@]+)@\s*(.*)$")
RANGE = re.compile(r"\s*BET\s+@#D([^@]+)@\s*(.*)\s+AND\s+@#D([^@]+)@\s*(.*)$")
SPAN  = re.compile(r"\s*FROM\s+@#D([^@]+)@\s*(.*)\s+TO\s+@#D([^@]+)@\s*(.*)$")

CALENDAR_MAP = {
    "FRENCH R" : RelLib.Date.CAL_FRENCH,
    "JULIAN"   : RelLib.Date.CAL_JULIAN,
    "HEBREW"   : RelLib.Date.CAL_HEBREW,
}

QUALITY_MAP = {
    'CAL' : RelLib.Date.QUAL_CALCULATED,
    'INT' : RelLib.Date.QUAL_CALCULATED,
    'EST' : RelLib.Date.QUAL_ESTIMATED,
}

SEX_MAP = {
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
            if self.token_text and self.token_text[0] == '@' \
                    and self.token_text[-1] == '@':
                self.token = TOKEN_ID
                self.token_text = self.token_text[1:-1]
                self.data = self.data.strip()
        else:
            func = MAP_DATA.get(self.token)
            if func:
                func(self)

    def calc_sex(self):
        """
        Converts the data field to a RelLib token indicating the gender
        """
        self.data = SEX_MAP.get(self.data.strip(), RelLib.Person.UNKNOWN)

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
        token = GED2GRAMPS.get(self.token_text)
        if token:
	    event = RelLib.Event()
	    event.set_description(self.data)
	    event.set_type(token)
            self.token = TOKEN_GEVENT
	    self.data = event
        else:
            token = GED2ATTR.get(self.token_text)
            if token:
                attr = RelLib.Attribute()
                attr.set_value(self.data)
                attr.set_type(token)
                self.token = TOKEN_ATTR
                self.data = attr

    def calc_note(self):
        gid = self.data.strip()
        if len(gid) > 2 and gid[0] == '@' and gid[-1] == '@':
            self.token = TOKEN_RNOTE
            self.data = gid[1:-1]

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

DATE_CNV = GedcomDateParser()

def extract_date(text):
    """
    Converts the specified text to a RelLib.Date object.
    """
    dateobj = RelLib.Date()
    try:
        # extract out the MOD line
        match = MOD.match(text)
        if match:
            (mod, text) = match.groups()
            qual = QUALITY_MAP.get(mod, RelLib.Date.QUAL_NONE)
        else:
            qual = RelLib.Date.QUAL_NONE

        # parse the range if we match, if so, return
        match = RANGE.match(text)
        if match:
            (cal1, data1, cal2, data2) = match.groups()

            cal = CALENDAR_MAP.get(cal1, RelLib.Date.CAL_GREGORIAN)
                    
            start = DATE_CNV.parse(data1)
            stop =  DATE_CNV.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_RANGE, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj

        # parse a span if we match
        match = SPAN.match(text)
        if match:
            (cal1, data1, cal2, data2) = match.groups()

            cal = CALENDAR_MAP.get(cal1, RelLib.Date.CAL_GREGORIAN)
                    
            start = DATE_CNV.parse(data1)
            stop =  DATE_CNV.parse(data2)
            dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_SPAN, cal,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj
        
        match = CAL.match(text)
        if match:
            (abt, cal, data) = match.groups()
            dateobj = DATE_CNV.parse("%s %s" % (abt, data))
            dateobj.set_calendar(CALENDAR_MAP.get(cal, 
                                                  RelLib.Date.CAL_GREGORIAN))
            dateobj.set_quality(qual)
            return dateobj

        dateobj = DATE_CNV.parse(text)
        dateobj.set_quality(qual)
        return dateobj
    except IOError:
        return DATE_CNV.set_text(text)

#-------------------------------------------------------------------------
#
# Reader - serves as the lexical analysis engine
#
#-------------------------------------------------------------------------
class Reader:

    def __init__(self, ifile):
        self.ifile = ifile
        self.current_list = []
        self.eof = False
        self.cnv = None
        self.cnt = 0
        self.index = 0
        self.func_map = {
            TOKEN_CONT : self._fix_token_cont,
            TOKEN_CONC : self._fix_token_conc,
            }

    def set_broken_conc(self, broken):
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
        line = self.current_list[0]
        new_value = line[2]+'\n'+data[2]
        self.current_list[0] = (line[0], line[1], new_value, line[3], line[4])

    def _fix_token_conc(self, data):
        line = self.current_list[0]
        new_value = line[2] + data[2]
        self.current_list[0] = (line[0], line[1], new_value, line[3], line[4])

    def _fix_token_broken_conc(self, data):
        line = self.current_list[0]
        new_value = u"%s %s" % (line[2], data[2])
        self.current_list[0] = (line[0], line[1], new_value, line[3], line[4])

    def readahead(self):
        while len(self.current_list) < 5:
            line = self.ifile.readline()
            self.index += 1
            if not line:
                self.eof = True
                return

            line = line.split(None, 2) + ['']

            val = line[2]
                
            try:
                level = int(line[0])
            except:
                level = 0

            data = (level, tokens.get(line[1], TOKEN_UNKNOWN), val, line[1], 
                    self.index)

            func = self.func_map.get(data[1])
            if func:
                func(data)
            else:
                self.current_list.insert(0, data)

