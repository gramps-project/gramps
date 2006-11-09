# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
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

# $Id: date_test.py,v 1.1.2.5 2006/04/20 04:04:31 rshura Exp $

"""Testscript for date displayer/parser"""


import os
import sys
import traceback
import locale
import gettext

import gtk

if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "/usr/share/locale"

try:
    locale.setlocale(locale.LC_ALL,'C')
    locale.setlocale(locale.LC_ALL,'')
except locale.Error:
    pass
except ValueError:
    pass

gettext.textdomain("gramps")
gettext.install("gramps",loc,unicode=1)

import DateHandler
from DateHandler import parser as _dp
from DateHandler import displayer as _dd
from RelLib import Date

print locale.getlocale(locale.LC_TIME)
print _dd
print _dp
print

date_tests = {}

# first the "basics".
testset = "basic test"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
        for month in range(1,13):
            d = Date()
            d.set(quality,modifier,calendar,(4,month,1789,False),"Text comment")
            dates.append( d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        for month1 in range(1,13):
            for month2 in range(1,13):
                d = Date()
                d.set(quality,modifier,calendar,(4,month1,1789,False,5,month2,1876,False),"Text comment")
                dates.append( d)
    modifier = Date.MOD_TEXTONLY
    d = Date()
    d.set(quality,modifier,calendar,Date.EMPTY,"This is a textual date")
    dates.append( d)
date_tests[testset] = dates

# incomplete dates (day or month missing)
testset = "partial date"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
        d = Date()
        d.set(quality,modifier,calendar,(0,11,1789,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,0,1789,False),"Text comment")
        dates.append( d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(quality,modifier,calendar,(4,10,1789,False,0,11,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(4,10,1789,False,0,0,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,10,1789,False,5,11,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,10,1789,False,0,11,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,10,1789,False,0,0,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,0,1789,False,5,11,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,0,1789,False,0,11,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(0,0,1789,False,0,0,1876,False),"Text comment")
        dates.append( d)
date_tests[testset] = dates

# slash-dates
testset = "slash-dates"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
        # normal date
        d = Date()
        d.set(quality,modifier,calendar,(4,11,1789,True),"Text comment")
        dates.append( d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(quality,modifier,calendar,(4,11,1789,True,5,10,1876,False),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(4,11,1789,False,5,10,1876,True),"Text comment")
        dates.append( d)
        d = Date()
        d.set(quality,modifier,calendar,(4,11,1789,True,5,10,1876,True),"Text comment")
        dates.append( d)
date_tests[testset] = dates

# BCE
testset = "B. C. E."
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
        # normal date
        d = Date()
        d.set(quality,modifier,calendar,(4,11,-90,False),"Text comment")
        dates.append( d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(quality,modifier,calendar,(5,10,-90,False,4,11,-90,False),"Text comment")
        dates.append( d)
        d = Date()
date_tests[testset] = dates

# test for all other different calendars
testset = "Non-gregorian"
dates = []
for calendar in (Date.CAL_JULIAN, Date.CAL_HEBREW, Date.CAL_ISLAMIC, Date.CAL_FRENCH, Date.CAL_PERSIAN):
    for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
        for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
            d = Date()
            d.set(quality,modifier,calendar,(4,11,1789,False),"Text comment")
            dates.append( d)
        for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
            d = Date()
            d.set(quality,modifier,calendar,(4,10,1789,False,5,11,1876,False),"Text comment")
            dates.append( d)
quality = Date.QUAL_NONE
modifier = Date.MOD_NONE
for calendar in (Date.CAL_JULIAN, Date.CAL_ISLAMIC, Date.CAL_PERSIAN):
    for month in range(1,13):
        d = Date()
        d.set(quality,modifier,calendar,(4,month,1789,False),"Text comment")
        dates.append( d)
for calendar in (Date.CAL_HEBREW, Date.CAL_FRENCH):
    for month in range(1,14):
        d = Date()
        d.set(quality,modifier,calendar,(4,month,1789,False),"Text comment")
        dates.append( d)
date_tests[testset] = dates

# now run the tests using all available date formats
cal_str = [ "CAL_GREGORIAN", "CAL_JULIAN", "CAL_HEBREW", "CAL_FRENCH", "CAL_PERSIAN", "CAL_ISLAMIC"]
mod_str = ["MOD_NONE", "MOD_BEFORE", "MOD_AFTER", "MOD_ABOUT", "MOD_RANGE", "MOD_SPAN", "MOD_TEXTONLY"]
qua_str = ["QUAL_NONE", "QUAL_ESTIMATED", "QUAL_CALCULATED"]
stats = {}
formats = DateHandler.get_date_formats()
for testset in date_tests.keys():
    print "\n##### %s:\n" % testset
    stats[testset] = [0,0,testset]
    for format in range( len( DateHandler.get_date_formats())):
        DateHandler.set_format(format)
        print "\n## %s:\n" % DateHandler.get_date_formats()[format]
        for dateval in date_tests[testset]:
            failed = True
            ex = None
            errmsg = ""
            datestr = None
            ndate = None
            ntxt = None
            if dateval.modifier != Date.MOD_TEXTONLY:
                dateval.text = "Comment. Format: %s" % DateHandler.get_date_formats()[format]
            try:
                datestr = _dd.display( dateval)
                try:
                    ndate = _dp.parse( datestr)
                    ntxt = _dd.display( ndate)
                    if ndate:
                        if dateval.is_equal( ndate):
                            failed = False
                        else:
                            if dateval.modifier != Date.MOD_TEXTONLY and ndate.modifier == Date.MOD_TEXTONLY:
                                errmsg = "FAILED! (was parsed as text)"
                            else:
                                errmsg = "FAILED!"
                    else:
                        errmsg = "FAILED: DateParser returned no Date"
                except:
                    ex = "Parser"
                    errmsg = "FAILED: DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),)
            except:
                ex = "Display"
                errmsg = "FAILED: DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),)
            if not failed:
                stats[testset][1] = stats[testset][1] + 1
                print datestr
                print ntxt
                print "ok"
            else:
                stats[testset][0] = stats[testset][0] + 1
                print "input was:"
                print "  calendar: %s" % cal_str[dateval.calendar]
                print "  modifier: %s" % mod_str[dateval.modifier]
                print "  quality:  %s" % qua_str[dateval.quality]
                print "  dateval:  %s" % str(dateval.dateval)
                print "  text:    '%s'" % dateval.text
                if ex == "Display":
                    print "This date is not displayable because of an Exception:"
                    print errmsg
                else:
                    print "DateDisplay gives: '%s'" % datestr
                    if ex == "Parser":
                        print "This date is not parsable because of an Exception:"
                        print errmsg
                    else:
                        print "parsed date was:"
                        print "  calendar: %s" % cal_str[ndate.calendar]
                        print "  modifier: %s" % mod_str[ndate.modifier]
                        print "  quality:  %s" % qua_str[ndate.quality]
                        print "  dateval:  %s" % str(ndate.dateval)
                        print "  text:    '%s'" % ndate.text
                        print "this gives:'%s'" % ntxt
            print

print "RESULT:"
for result in stats:
    print "% 13s: % 5d dates ok, % 4d failed." % (stats[result][2],stats[result][1],stats[result][0])
