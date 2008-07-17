#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007      Thom Sturgill
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2008      Rob G. Healey <robhealey1@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Pubilc License as published by
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
Web Calendar generator.

Created 4/22/07 by Thom Sturgill based on Calendar.py (with patches) 
by Doug Blank with input dialog based on NarrativeWeb.py by Don Allingham.

2008-05-11 Jason Simanek
Improving markup for optimal separation of content and presentation.

2008-June-22 Rob G. Healey
*** Remove StyleEditor, make it css based as is NarrativeWeb, 
move title to first tab, re-word note tabs, complete re-write of 
calendar build, added year glance, and blank year, added easter and 
dst start/stop from Calendar.py, etc.

Reports/Web Page/Web Calendar
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
import datetime
import calendar
import math
import codecs
import shutil
from gettext import gettext as _
from xml.parsers import expat


try:
    set()
except:
    from sets import Set as set

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WebPage")

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import gen.lib
import const
import BaseDoc
from GrampsCfg import get_researcher
from PluginUtils import PluginManager
from ReportBase import (Report, ReportUtils, MenuReportOptions, CATEGORY_WEB, 
                        MODE_GUI)
from PluginUtils import FilterOption, EnumeratedListOption, PersonOption, \
    BooleanOption, NumberOption, StringOption, DestinationOption
import Utils
import GrampsLocale
from QuestionDialog import ErrorDialog
from Utils import probably_alive
from DateHandler import displayer as _dd
from DateHandler import parser as _dp

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_CALENDARSCREEN = "calendar-screen.css"
_CALENDARPRINT = "calendar-print.css"

# This information defines the list of styles in the Web calendar
# options dialog as well as the location of the corresponding SCREEN
# stylesheets.
_CSS_FILES = [
    # First is used as default selection.
    [_("Evergreen"),        'Web_Evergreen.css'],
    [_("Nebraska"),         'Web_Nebraska.css'],
    [_("Simply Red"),       'Web_Simply-Red.css'],
    [_("No style sheet"),   ''],
    ]

_CHARACTER_SETS = [
    [_('Unicode (recommended)'), 'utf-8'],
    ['ISO-8859-1',  'iso-8859-1' ],
    ['ISO-8859-2',  'iso-8859-2' ],
    ['ISO-8859-3',  'iso-8859-3' ],
    ['ISO-8859-4',  'iso-8859-4' ],
    ['ISO-8859-5',  'iso-8859-5' ],
    ['ISO-8859-6',  'iso-8859-6' ],
    ['ISO-8859-7',  'iso-8859-7' ],
    ['ISO-8859-8',  'iso-8859-8' ],
    ['ISO-8859-9',  'iso-8859-9' ],
    ['ISO-8859-10', 'iso-8859-10' ],
    ['ISO-8859-13', 'iso-8859-13' ],
    ['ISO-8859-14', 'iso-8859-14' ],
    ['ISO-8859-15', 'iso-8859-15' ],
    ['koi8_r',      'koi8_r',     ],
    ]

_CC = [
    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" title="Creative '
    'Commons License - By attribution" ',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" ',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" ',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" ',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No '
    'derivations" title="Creative Commons License - By attribution, '
    'Non-commercial, No derivations" ',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, '
    'Share-alike" title="Creative Commons License - By attribution, '
    'Non-commerical, Share-alike" '
    ]

_COPY_OPTIONS = [
        _('Standard copyright'),
        _('Creative Commons - By attribution'),
        _('Creative Commons - By attribution, No derivations'),
        _('Creative Commons - By attribution, Share-alike'),
        _('Creative Commons - By attribution, Non-commercial'),
        _('Creative Commons - By attribution, Non-commercial, No derivations'),
        _('Creative Commons - By attribution, Non-commercial, Share-alike'),
        _('No copyright notice'),
        ]

def make_date(year, month, day):
    """
    Return a Date object of the particular year/month/day.
    """
    retval = gen.lib.Date()
    retval.set_yr_mon_day(year, month, day)
    return retval

#------------------------------------------------------------------------
#
# WebCalReport
#
#------------------------------------------------------------------------
class WebCalReport(Report):
    """
    Create WebCalReport object that produces the report.
    """
    def __init__(self, database, options):
        Report.__init__(self, database, options)
        menu = options.menu
        
        self.database = database
        self.options = options
        
        self.html_dir = menu.get_option_by_name('target').get_value()
        filter_option =  menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.ext = menu.get_option_by_name('ext').get_value()
        self.copy = menu.get_option_by_name('cright').get_value()
        self.encoding = menu.get_option_by_name('encoding').get_value()
        self.css = menu.get_option_by_name('css').get_value()
        self.Country = menu.get_option_by_name('country').get_value()
        self.Year = menu.get_option_by_name('year').get_value()
        self.fullyear = menu.get_option_by_name('fullyear').get_value()
        self.blankyear = menu.get_option_by_name('blankyear').get_value()
        self.Surname = menu.get_option_by_name('surname').get_value()
        self.Alive = menu.get_option_by_name('alive').get_value()
        self.Birthday = menu.get_option_by_name('birthdays').get_value()
        self.Anniv = menu.get_option_by_name('anniversaries').get_value()
        self.Title_text  = menu.get_option_by_name('title').get_value()
        self.Home_link = menu.get_option_by_name('home_link').get_value()
        
        self.Note  = [ menu.get_option_by_name('note_jan').get_value(), 
                       menu.get_option_by_name('note_feb').get_value(),
                       menu.get_option_by_name('note_mar').get_value(),
                       menu.get_option_by_name('note_apr').get_value(),
                       menu.get_option_by_name('note_may').get_value(),
                       menu.get_option_by_name('note_jun').get_value(),
                       menu.get_option_by_name('note_jul').get_value(),
                       menu.get_option_by_name('note_aug').get_value(),
                       menu.get_option_by_name('note_sep').get_value(),
                       menu.get_option_by_name('note_oct').get_value(),
                       menu.get_option_by_name('note_nov').get_value(),
                       menu.get_option_by_name('note_dec').get_value()]
        
    def store_file(self, from_path, to_path):
        """
        Store the file in the destination.
        """
        dest = os.path.join(self.html_dir, to_path)
        dirname = os.path.dirname(dest)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        if from_path != dest:
            shutil.copyfile(from_path, dest)
        elif self.warn_dir:
            WarningDialog(
                _("Possible destination error") + "\n" +
                _("You appear to have set your target directory "
                  "to a directory used for data storage. This "
                  "could create problems with file management. "
                  "It is recommended that you consider using "
                  "a different directory to store your generated "
                  "web pages."))
            self.warn_dir = False

    # code snippets for east and Daylight saving start/ stop 
    # are borrowed from Calendar.py    
        
    def easter(self):
        """
        Computes the year/month/day of easter. Based on work by
        J.-M. Oudin (1940) and is reprinted in the "Explanatory Supplement
        to the Astronomical Almanac", ed. P. K.  Seidelmann (1992).  Note:
        Ash Wednesday is 46 days before Easter Sunday.
        """
        year = self.Year
        c = year / 100
        n = year - 19 * (year / 19)
        k = (c - 17) / 25
        i = c - c / 4 - (c - k) / 3 + 19 * n + 15
        i = i - 30 * (i / 30)
        i = i - (i / 28) * (1 - (i / 28) * (29 / (i + 1))
                           * ((21 - n) / 11))
        j = year + year / 4 + i + 2 - c + c / 4
        j = j - 7 * (j / 7)
        l = i - j
        month = 3 + (l + 40) / 44
        day = l + 28 - 31 * (month / 4)
        return (year, month, day)

    def dst(self, area="us"):
        """
        Return Daylight Saving Time start/stop in a given area ("us", "eu").
        US calculation valid 1976-2099; EU 1996-2099
        """
        year = self.Year        
        if area == "us":
            if year > 2006:
                start = (year, 3, 14 - (math.floor(1 + year * 5 / 4) % 7)) # March
                stop = (year, 11, 7 - (math.floor(1 + year * 5 / 4) % 7)) # November
            else:
                start = (year, 4, (2 + 6 * year - math.floor(year / 4)) % 7 + 1) # April
                stop =  (year, 10, (31 - (math.floor(year * 5 / 4) + 1) % 7)) # October
        elif area == "eu":
            start = (year, 3, (31 - (math.floor(year * 5 / 4) + 4) % 7)) # March
            stop =  (year, 10, (31 - (math.floor(year * 5 / 4) + 1) % 7)) # Oct
        return (start, stop)

    def get_short_name(self, person, maiden_name = None):
        """ Return person's name, unless maiden_name given, unless married_name listed. """
        # Get all of a person's names:
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for n in names:
            if int(n.get_type()) == gen.lib.NameType.MARRIED:
                married_name = n
        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                first_name, family_name = married_name.get_first_name(), married_name.get_surname()
                call_name = married_name.get_call_name()
            else:
                first_name, family_name = primary_name.get_first_name(), maiden_name
                call_name = primary_name.get_call_name()
        else:
            first_name, family_name = primary_name.get_first_name(), primary_name.get_surname()
            call_name = primary_name.get_call_name()
        # If they have a nickname use it
        if call_name is not None and call_name.strip() != "":
            first_name = call_name.strip()
        else: # else just get the first name:
            first_name = first_name.strip()
            if " " in first_name:
                first_name, rest = first_name.split(" ", 1) # just one split max
        return ("%s %s" % (first_name, family_name)).strip()

    def add_day_item(self, text, year, month, day):
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])
        day_list.append(text)
        month_dict[day] = day_list
        self.calendar[month] = month_dict

    def get_holidays(self, country = "United States"):
        """ Looks in multiple places for holidays.xml files 
        the holidays file will be used first if it exists in user's plugins, else
        the GRAMPS plugins will be checked.  No more of having duel holidays files being read.

        User directory is first choice if it exists, and does not use both holiday files any longer
        """

        year = self.Year
        holiday_file = 'holidays.xml'
        holiday_full_path = ""
        fname1 = os.path.join(const.USER_PLUGINS, holiday_file)
        fname2 = os.path.join(const.PLUGINS_DIR, holiday_file)
        if os.path.exists(fname1):
            holiday_full_path = fname1
        elif os.path.exists(fname2):
            holiday_full_path = fname2
        if holiday_full_path != "":
            self.process_holiday_file(holiday_full_path, country)

    def process_holiday_file(self, filename, country):
        """ This will process a holiday file """

        year = self.Year
        parser = Xml2Obj()
        element = parser.Parse(filename)
        calendar = Holidays(element, country)
        date = datetime.date(year, 1, 1)
        while date.year == year:
            holidays = calendar.check_date( date )
            for text in holidays:
                if text == "Easter":
                    date1 = self.easter()
                    self.add_day_item(text, date1[0], date1[1], date1[2])
                elif text == "Daylight Saving begins":
                    if Utils.xml_lang() == "en-US":
                        date2 = self.dst("us")
                    else:
                        date2 = self.dst("eu")
                    dst_start = date2[0]
                    dst_stop = date2[1]
                    self.add_day_item(text, dst_start[0], dst_start[1], dst_start[2])
                    self.add_day_item("Daylight Saving ends", dst_stop[0], dst_stop[1], dst_stop[2])
                elif text == "Daylight Saving ends":
                    pass
                self.add_day_item(text, date.year, date.month, date.day)
            date = date.fromordinal( date.toordinal() + 1)

    def copy_css(self):
        """
        Copies all the necessary files...
        """
        # Copy the _CALENDARSCREEN css
        if self.css != "":
            from_file = os.path.join(const.DATA_DIR, self.css)
            to_file = os.path.join("styles/", _CALENDARSCREEN)
            self.store_file(from_file, to_file)

        # copy calendar-print stylesheet
        from_file = os.path.join(const.DATA_DIR, "Web_Print-Default.css")
        to_file = os.path.join("styles/", _CALENDARPRINT)
        self.store_file(from_file, to_file) 

        # Copy GRAMPS favicon to target
        from_file = os.path.join(const.IMAGE_DIR, "favicon.ico")
        to_file = os.path.join("images/", "favicon.ico")
        self.store_file(from_file, to_file)

        # Copy arrow image if "Year At A Glance" is requested, 
        # and if the file exists
        if self.fullyear:
            from_file = os.path.join(const.IMAGE_DIR, "arrow102.gif")
            if os.path.exists(from_file):        
                to_file = os.path.join("images/", "arrow102.gif")
                self.store_file(from_file, to_file)

    def display_nav_links(self, of, currentsection, cal):

        # Check to see if home_link will be used???
        navs = [
            ('January',     _('Jan'),             True),
            ('February',    _('Feb'),             True),
            ('March',       _('Mar'),             True),
            ('April',       _('Apr'),             True),
            ('May',         _('May'),             True),
            ('June',        _('Jun'),             True),
            ('July',        _('Jul'),             True),
            ('August',      _('Aug'),             True),
            ('September',   _('Sep'),            True),
            ('October',     _('Oct'),             True),
            ('November',    _('Nov'),             True),
            ('December',    _('Dec'),             True),
            ('fullyear',    _('Year Glance'),     self.fullyear),
            ('blankyear',   _('Blank Calendar'),  self.blankyear)
                ]
        for url_fname, nav_text, cond in navs:
            if cond:
                new_dir = str(self.Year) + '/'
                if ((cal == "yg") or (cal == "by")):
                    url = self.subdirs("yg", new_dir, url_fname)
                elif cal == "ip":
                    url = self.subdirs("ip", new_dir, url_fname)
                else:
                    url = self.subdirs("wc", new_dir, url_fname)
                url += self.ext
                self.display_nav_link(of, url, nav_text, currentsection)

    def display_nav_link(self, of, url, title, currentsection):
        # Figure out if we need <li id="CurrentSection"> of just plain <li>
        cs = False
        if title == currentsection:
            cs = True

        cs = cs and ' id="CurrentSection"' or ''
        of.write('            <li%s><a href="%s">%s</a></li>\n' 
            % (cs, url, title))

    def calendar_build(self, of, cal, month):
        """
        This does the work of building the calendar
        """

        year = self.Year

        # Begin calendar head
        title = GrampsLocale.long_months[month]
        of.write('<!-- %s -->\n' % title)
        of.write('    <table id="%s" class="calendar">\n' % title)
        of.write('        <thead>\n')
        of.write('            <tr>\n')
        of.write('                <th colspan="7" class="monthName">')
        of.write('%s</th>\n' % title)
        of.write('            </tr>\n')

        # Calendar weekday names header
        of.write('            <tr>\n')
        of.write('                <th class="weekend sunday" />')
        if cal == "yg":
            of.write(GrampsLocale.short_days[1])
        else:
            of.write(GrampsLocale.long_days[1])
        of.write('</th>\n')
        for day_col in range(5):
            of.write('                <th class="weekday" />')
            if cal == "yg":
                of.write(GrampsLocale.short_days[day_col+2])
            else:
                of.write(GrampsLocale.long_days[day_col+2])
            of.write('</th>\n')
        of.write('                <th class="weekend saturday" />')
        if cal == "yg":
            of.write(GrampsLocale.short_days[7])
        else:
            of.write(GrampsLocale.long_days[7])
        of.write('</th>\n')
        of.write('            </tr>\n')
        of.write('        </thead>\n')

        of.write('        <tbody>\n')
        monthinfo = calendar.monthcalendar(year, month)
        nweeks = len(monthinfo)
        current_date = datetime.date(year, month, 1) # first day of the month
        if current_date.isoweekday() != 7: # start dow here is 7, sunday
            current_ord = current_date.toordinal() - current_date.isoweekday()
        else:
            current_ord = current_date.toordinal()

        # get last month's last week for previous days in the month
        if month == 1:
            prevmonth = calendar.monthcalendar(year-1, 12)
        else:
            prevmonth = calendar.monthcalendar(year, month-1)
        num_weeks = len(prevmonth)
        lastweek = prevmonth[num_weeks - 1]

        # get next month's first week for next days in the month
        if month == 12:
            nextmonth = calendar.monthcalendar(year+1, 1)
        else:
            nextmonth = calendar.monthcalendar(year, month + 1)
        nextweek = nextmonth[0]

        # Begin calendar
        for week_row in range(0, nweeks):
            week = monthinfo[week_row]
            of.write('             <tr class="week%d">\n' % week_row)
            for days_row in range(0, 7):
                if days_row == 0:
                    dayclass = "weekend sunday"
                elif days_row == 6:
                    dayclass = "weekend saturday"
                else:
                    dayclass = "weekday"
                day = week[days_row]
                if day == 0: # previous or next month day
                    if week_row == 0: # previous day
                        specday = lastweek[days_row]
                        specclass = "previous " + dayclass
                    elif week_row == nweeks-1:
                        specday = nextweek[days_row]
                        specclass = "next " + dayclass
                    of.write('                 <td id="specday%d" class="%s">\n'
                        % (specday, specclass))
                    of.write('                     <div class="date">%d</div>\n'
                        % specday)
                    of.write('                 </td>\n')
                else: # day number
                    if cal == "by":
                        of.write('                 <td id="day%d" class="%s">\n' 
                            % (day, dayclass))
                        of.write('                     <div class="date">%d</div>\n' % day)
                        of.write('                 </td>\n')
                    else:
                        of.write('                 <td id="day%d" ' % day)
                        thisday = current_date.fromordinal(current_ord)
                        if thisday.month == month: # Something this month
                            list = self.calendar.get(month, {}).get(thisday.day, {})
                            if ((thisday.day == day) and (list > [])):
                                specclass = "highlight " + dayclass
                                of.write('class="%s">\n' % specclass)
                                if cal == "yg": # Year at a Glance
                                    lng_month = GrampsLocale.long_months[month]
                                    shrt_month = GrampsLocale.short_months[month]
                                    of.write('                    <a href="%s/%s%d%s">\n' 
                                        % (lng_month, shrt_month, day, self.ext))
                                    of.write('                         <div class="date">%d'
                                        '</div></a>\n' % day)
                                    self.indiv_date(month, day, list)
                                else: # WebCal
                                    of.write('                         <div class="date">%d'
                                        '</div>\n' % day)
                                    of.write('                          <ul>\n')
                                    for p in list:
                                        lines = p.count("\n") + 1 # lines in the text
                                        for line in p.split("\n"):
                                            of.write('                            <li>')
                                            of.write(line)
                                            of.write('</li>\n')
                                    of.write('                         </ul>\n')
                            else:
                                of.write('class="%s">\n' % dayclass)
                                of.write('                         <div class="date">%d</div>\n' 
                                    % day)
                        else:
                            of.write('class="%s">\n' % dayclass)
                            of.write('                     <div class="date">%d</div>\n' % day)
                        of.write('                 </td>\n')
                current_ord += 1
            of.write('             </tr>\n')

        # Complete six weeks for proper styling
        of = self.six_weeks(of, nweeks)

        return of

    def write_header(self, of, title, cal, mystyle):
        """
        This creates the header for the Calendars iincluding style embedded for special purpose
        """

        of.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n ')
        of.write('     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n ')
        of.write('<html xmlns="http://www.w3.org/1999/xhtml" ')
        xmllang = Utils.xml_lang()
        of.write('xml:lang="%s" lang="%s">\n' % (xmllang, xmllang))
        of.write('<head>\n')
        of.write('     <title>%s</title>\n' % title)
        of.write('     <meta http-equiv="Content-Type" content="text/html;charset=%s" />\n' 
                % self.encoding)
        of.write('     <meta name="robots" content="noindex" />\n')
        of.write('     <meta name="generator" content="GRAMPS 3.1.x: http://www.gramps-project.org" '
                '/>\n')
        author = get_researcher().get_name()
        of.write('     <meta name="author" content="%s" />\n' % author)

        if ((cal == "yg") or (cal == "by")): # year glance and blank_year 
                                             # have same directory levels
            fname1 = self.subdirs("yg", "styles/", _CALENDARSCREEN)
            fname2 = self.subdirs("yg", "styles/", _CALENDARPRINT)
            fname3 = self.subdirs("yg", "images/", "favicon.ico")
        elif cal == "ip":
            fname1 = self.subdirs("ip", "styles/", _CALENDARSCREEN)
            fname2 = self.subdirs("ip", "styles/", _CALENDARPRINT)
            fname3 = self.subdirs("ip", "images/", "favicon.ico")
        else:
            fname1 = self.subdirs("wc", "styles/", _CALENDARSCREEN)
            fname2 = self.subdirs("wc", "styles/", _CALENDARPRINT)
            fname3 = self.subdirs("wc", "images/", "favicon.ico")

        # link to calendar-screen css
        of.write('     <link href="%s" rel="stylesheet" type="text/css" media="screen" />\n' % fname1)

        # link to calendar-print css
        if not cal == "yg":
            of.write('     <link href="%s" rel="stylesheet" type="text/css" media="print" />\n' 
                % fname2)

        # create a link to GRAMPS favicon
        of.write('     <link href="%s" rel="Shortcut Icon" />\n' % fname3)

        # Add calendar specific embedded style
        of.write(mystyle)
        of.write('</head>\n')

        return (of, author)

    def write_footer(self, of, cal):
        """
        Writes the footer section of the pages
        """

        # Display date as user set in preferences
        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)

        msg = _('Generated by <a href="http://gramps-project.org" target="_blank">'
                 'GRAMPS</a> on %(date)s') % { 'date' : value }

        author = get_researcher().get_name()
        if author:
            author = author.replace(',,,', '')
        of.write('     <div id="footer">\n')
        of.write('         <p id="createdate">%s</p>\n' % msg)

        # copyright license
        if ((cal == "yg") or (cal == "by")):
            fname = self.subdirs("yg", "images/", "somerights20.gif")
        elif cal == "ip":
            fname = self.subdirs("ip", "images/", "somerights20.gif")
        else:
            fname  = self.subdirs("wc", "images/", "somerights20.gif")
        if self.copy > 0 and self.copy <= 6:
            text = _CC[self.copy-1]
            text += 'src="%s"></a>' % fname
            from_file = os.path.join(const.IMAGE_DIR,"somerights20.gif")
            to_file = os.path.join("images/", "somerights20.gif")
            self.store_file(from_file, to_file)
        else:
            text = "&copy; %s %s" % (time.localtime()[0], author)
        of.write('         <p id="copyright">%s</p>\n' % text)
        of.write('         <p id="quality"><a href="http://validator.w3.org/check?uri=referer">')
        of.write('<img src="http://www.w3.org/Icons/valid-xhtml10" ')
        of.write('alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a></p>\n')
        of.write('     </div>\n')
        of.write('</body>\n')
        of.write('</html>\n')

    def create_file(self, name):
        page_name = os.path.join(self.html_dir, name)
        of = codecs.EncodedFile(open(page_name, "w"),'utf-8',self.encoding,'xmlcharrefreplace')
        return of

    def close_file(self, of):
        of.close()

    def indiv_date(self, month, day_num, list):
        """
        This method creates the indiv pages for "Year At A Glance"
        """

        year = self.Year
        dest_dir = self.html_dir + "/images"
        arrow = os.path.join(dest_dir, "arrow102.gif")

        # Create names for long and short month names
        lng_month = GrampsLocale.long_months[month]
        shrt_month = GrampsLocale.short_months[month]

        new_dir = self.html_dir + "/%d/%s" % (year, lng_month)
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        # Name the file, and create it
        cal_file = '%d/%s/%s%d%s' % (year, lng_month, shrt_month, day_num, self.ext)
        ip = self.create_file(cal_file)

        mystyle = """
        <style type="text/css">
        <!--
        """
        if os.path.isfile(arrow):
            mystyle += """
            ul#arrow li {
                font-size:16px;
                list-style-image: url("../../images/arrow102.gif"); }
            """
        else:
            mystyle += """
            ul li {
            font-size:16px; }
            """
        mystyle += """
        -->
        </style>
        """

        # Add Header to calendar
        title = "%d %s %d" % (day_num, lng_month, year)
        (ip, author) = self.write_header(ip, title, "ip", mystyle)

        ip.write('<body id="events-%s%d">\n' % (shrt_month, day_num))
        ip.write('    <div id="header">\n')
        if author:
            ip.write('         <div id="GRAMPSinfo">\n')
            msg = 'Created for %s' % author
            ip.write('             %s</div>\n' % msg)
	ip.write('      <h1 id="SiteTitle">A Peak into One Day</h1>\n')
        ip.write('    </div>\n')
        
        # Create navigation menu
        ip.write('    <div id="navigation">\n')
        ip.write('         <ul>\n')

        if self.Home_link.strip() != '':
            ip.write('                     <li>')
            ip.write('<a href="%s">HOME</a></li>\n' % self.Home_link)

        title = GrampsLocale.short_months[month]
        self.display_nav_links(ip, title, "ip")

        ip.write('         </ul>\n')
        ip.write('     </div>\n')

        ip.write('      <h2 class="monthName" style="display:block;">%s %d, %d</h2>\n' 
            % (lng_month, day_num, year))

        # if arrow file exists in IMAGE_DIR, use it
        arrow = os.path.join(const.IMAGE_DIR, "arrow102.gif")
        if os.path.isfile(arrow):
            ip.write('                  <ul id="arrow">\n')
        else:
            ip.write('                  <ul>\n')
        for p in list:
            lines = p.count("\n") + 1 # lines in the text
            for line in p.split("\n"):
                ip.write('                         <li>')
                ip.write(line)
                ip.write('</li>\n')
        ip.write('                      </ul>\n')

        self.write_footer(ip, "ip")
        self.close_file(ip)

    def six_weeks(self, of, nweeks):
        """
        Will complete the calendar out to six weeks for 
        proper styling of css sheets
        """

        if nweeks == 4: # four weeks, add two weeks
            for empty_weeks in range(1, 3):
                of.write('             <tr class="week%d">\n' % (nweeks + empty_weeks))
                of.write('                 <td id="emptyDays" colspan="7">\n')
                of.write('                 </td>\n') 
                of.write('             </tr>\n')
        elif nweeks == 5: # five weeks, add one week
            of.write('             <tr class="week6">\n')
            of.write('                 <td id="emptyDays" colspan="7">\n')
            of.write('                 </td>\n')
            of.write('             </tr>\n')
        return of

    def blank_year(self):
        """
        This method will create the Printable Full Year One Page Calendar...
        """

        year = self.Year
        # if year dir doesn't exist, create it
        new_dir = self.html_dir + "/%d" % year
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        # Name the file, and create it
        cal_file = '%d/blankyear%s' % (year, self.ext)
        by = self.create_file(cal_file)

        # Add specific styles for "Printable Full-Year Calendar" page
        mystyle = """
    <style type="text/css">
    <!--
    #header {
        height:2cm;
    #header h1#SiteTitle {
        color:#FFF;
        font-size:24px; }
    #footer {
        height:2cm;
        font-size:16px;
    -->
    </style>
    """

        # Add header to page
        title = str(year) + "Blank Calendar"
        (by, author) = self.write_header(by, title, "by", mystyle)

        by.write('<body id="blankca">\n')

        # Header Title
        by.write('    <div id="header">\n')
        if author:
            by.write('         <div id="GRAMPSinfo">\n')
            msg = 'Created for %s' % author
            by.write('             %s</div>\n' % msg)
        by.write('        <h1 id="SiteTitle">%d</h1>\n' % year)
        by.write('    </div>\n')

        # Create navigation menu
        by.write('    <div id="navigation">\n')
        by.write('         <ul>\n')

        if self.Home_link.strip() != '':
            by.write('                     <li>')
            by.write('<a href="%s">HOME</a></li>\n' % self.Home_link)

        self.display_nav_links(by, 'Blank Calendar', "by")

        by.write('         </ul>\n')
        by.write('     </div>\n')
        
        # Create progress bar for it
        self.progress.set_pass(_('Creating Printable Blank Full-Year Calendar Page'), 12)

        for month in range(1, 13): # Create full year
            self.progress.step()

            # build the calendar
            by = self.calendar_build(by, "by", month)

            # close table body
            by.write('         </tbody>\n')
            by.write('     </table>\n')

        # Write footer and close file
        self.write_footer(by, "by")
        self.close_file(by)

    def year_glance(self):
        """
        This method will create the Full Year At A Glance Page...
        """

        year = self.Year
        # if year dir doesn't exist, create it
        new_dir = self.html_dir + "/%d/" % year
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        # Name the file, and create it
        cal_file = '%d/fullyear%s' % (year, self.ext)
        yg = self.create_file(cal_file)

        # Add specific styles for "Year At A Glance" page
        mystyle = """
        <style type="text/css">
        <!--
        .calendar {
            float:left;
            width:30em;
            height:27em;
            font-size:.8em;
            margin:1em 1em 1em 4em;
            padding:1em 0 0 0;
            border-top:solid 1px #000;}
        .calendar thead tr th {
            height:1em;
            font-size:.8em; }
        .calendar thead tr th.monthName {
            background-color:#FFF;
            height:1.1em;
            font-size:1em; }
        .calendar tbody tr.week5 {
            border-top:solid 1px #000; }
        .calendar tbody tr.week6 {
            border-top:solid 1px #000; }
        .calendar tbody tr td {
            height:1.2cm; }
        .calendar tbody tr td.saturday {
            border-right:solid 1px #000; }
        .calendar tbody tr td.sunday {
            border-left:solid 1px #000; }
        .highlight div.date {
            background-color:#FA0E18;
            color:#FFF; }
        -->
        </style>
        """

        # Add header to page
        title = "%d, At A Glance" % year
        (yg, author) = self.write_header(yg, title, "yg", mystyle)

        yg.write('<body id="fullyear">\n')     # body will terminate in write_footer

        # Header Title
        yg.write('    <div id="header">\n')
        if author:
            yg.write('         <div id="GRAMPSinfo">\n')
            msg = 'Created for %s' % author
            yg.write('             %s</div>\n' % msg)
        yg.write('      <h1 id="SiteTitle">%s\n' % title)
        yg.write('    </div>\n')

        # Create navigation menu
        yg.write('         <div id="navigation">\n')
        yg.write('              <ul>\n')

        if self.Home_link.strip() != '':
            yg.write('                     <li>')
            yg.write('<a href="%s">HOME</a></li>\n' % self.Home_link)

        self.display_nav_links(yg, 'Year Glance', "yg")

        yg.write('         </ul>\n')
        yg.write('     </div>\n') # End Navigation Menu

        yg.write('        <p id="description">\n')
        yg.write('            This calendar is meant to give you access to all your data at a glance '
        'compressed into one page.  Clicking on a <b>red square</b> will take you to a '
        'page that shows all the events for that date!\n')
        yg.write('        </p>\n\n')

        # Create progress bar for it
        self.progress.set_pass(_('Creating Year At A Glance page'), 12)

        for month in range(1, 13): # Create full year
            self.progress.step()

            # build the calendar
            yg = self.calendar_build(yg, "yg", month)


            # close table body before writing note
            yg.write('         </tbody>\n')

            # create note section for each calendar month
            yg.write('        <tfoot>\n')
            yg.write('            <tr>\n')
            yg.write('                <td class="note" colspan="7">\n')
            if self.Note[month-1].strip() != '':
                yg.write('                     %s\n' % self.Note[month-1])
            else:
                yg.write('                     &nbsp;\n')
            yg.write('                 </td>\n')
            yg.write('            </tr>\n')
            yg.write('        </tfoot>\n')
            yg.write('     </table>\n\n')

        # write footer section, and close file
        self.write_footer(yg, "yg")
        self.close_file(yg)

    def write_report(self):
        """ The short method that runs through each month and creates a page. """
        if not os.path.isdir(self.html_dir):
            parent_dir = os.path.dirname(self.html_dir)
            if not os.path.isdir(parent_dir):
                ErrorDialog(_("Neither %s nor %s are directories") % \
                            (self.html_dir,parent_dir))
                return
            else:
                try:
                    os.mkdir(self.html_dir)
                except IOError, value:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                self.html_dir + "\n" + value[1])
                    return
                except:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                self.html_dir)
                    return
        
        # initialize the dict to fill:
        self.calendar = {}
        self.progress = Utils.ProgressMeter(_("Generate XHTML Calendars"),'')

        # Generate the CSS file
        self.copy_css()

        # get the information, first from holidays:
        if self.Country != 0: # Don't include holidays
            self.get_holidays(_COUNTRIES[self.Country]) # _country is currently global
            self.progress.set_pass(_("Getting information from holidays file"),'')

        # get data from database:
        self.collect_data()

        # generate the report:
        self.progress.set_pass(_("Creating Calendar pages"),12)

        for month in range(1, 13):
            self.progress.step()
            self.print_page(month)

        if self.fullyear:
            self.year_glance()

        if self.blankyear:
            self.blank_year()

        # Close the progress meter
        self.progress.close()

    def subdirs(self, cal, dir, name):
        """
        his will add the number of subdirs to the filename depending on which 
        calendar is being called
        "wc" = WebCal
        yg = Year At A Glance
        by = Printable Pocket Calendar
        ip = Indiv Pages
        """

        if cal == "wc":
            subdirs = '.././'
        elif ((cal == "yg") or (cal == "by")):
            subdirs = '.././'
        else:
            subdirs = '../.././'
        fname = subdirs + '%s%s' % (dir, name) 
        return fname

    def print_page(self, month):
        """
        This method provides information and header/ footer to the calendar month
        """

        year = self.Year
        # if year dir doesn't exist, create it
        new_dir = self.html_dir + "/%d" % year
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        # Name the file, and create it
        cal_file = "%d/%s%s" % (year, GrampsLocale.long_months[month], self.ext)
        of = self.create_file(cal_file)

        # Add specific styles to calendar head
        mystyle = """
        <style type="text/css">
        <! --
        .calendar thead tr th.monthName {
            height:1.5cm;
            font-size:.9cm; }
        -->
        </style>
            """

        # Add Header to calendar
        (of, author) = self.write_header(of, self.Title_text, "of", mystyle)

        of.write('<body id="WebCal">\n')   # terminated in write_footer

        # Header Title
        of.write('    <div id="header">\n')
        if author:
            of.write('         <div id="GRAMPSinfo">\n')
            msg = 'Created for %s' % author
            of.write('             %s</div>\n' % msg)
        of.write('        <h1 id="SiteTitle">%s</h1>\n' % self.Title_text)
        of.write('        <h1>%d</h1>\n' % year)
        of.write('    </div>\n')  # end header

        # Create Navigation Menu
        of.write('    <div id="navigation">\n')
        of.write('        <ul>\n') 

        if self.Home_link.strip() != '':
            of.write('                     <li>')
            of.write('<a href="%s">HOME</a></li>\n' % self.Home_link)

        highlight = GrampsLocale.short_months[month]
        self.display_nav_links(of, highlight, "wc")

        of.write('        </ul>\n\n')
        of.write('    </div>\n') # End Navigation Menu

        # Set first weekday according to Locale
        xmllang = Utils.xml_lang()
        if xmllang == "en-US":
            calendar.setfirstweekday(6) # USA calendar starts on a Sunday
                                        # European calendar starts on Monday, default

        # build the calendar
        of = self.calendar_build(of, "wc", month)

        # close table body before note section
        of.write('         </tbody>\n')

        # create note section for "WebCal"
        of.write('        <tfoot>\n')
        of.write('            <tr>\n')
        of.write('                <td class="note" colspan="7">')
        if self.Note[month-1].strip() != '':
            of.write(self.Note[month-1])
        else:
            of.write("&nbsp;")
        of.write('</td>\n')
        of.write('            </tr>\n')
        of.write('        </tfoot>\n')
        of.write('     </table>\n\n')

        # write footer section, and close file
        self.write_footer(of, "of")
        self.close_file(of)

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        self.progress.set_pass(_("Filtering"),'')
        people = self.filter.apply(self.database,
                                   self.database.get_person_handles(sort_handles=False))
        self.progress.set_pass(_("Reading database"),len(people))
        for person_handle in people:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.database.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            living = probably_alive(person, self.database, make_date(self.Year, 1, 1), 0)
            if self.Birthday and birth_date != None and ((self.Alive and living) or not self.Alive):
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()
                age = self.Year - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self.Surname == 0: # get husband's last name:
                    if person.get_gender() == gen.lib.Person.FEMALE:
                        family_list = person.get_family_handle_list()
                        if len(family_list) > 0:
                            fhandle = family_list[0] # first is primary
                            fam = self.database.get_family_from_handle(fhandle)
                            father_handle = fam.get_father_handle()
                            mother_handle = fam.get_mother_handle()
                            if mother_handle == person_handle:
                                if father_handle:
                                    father = self.database.get_person_from_handle(father_handle)
                                    if father != None:
                                        father_lastname = father.get_primary_name().get_surname()
                short_name = self.get_short_name(person, father_lastname)
                if age == 0: # person is 0 years old, display nothing
                    text= ""
                elif age == 1: # person is 1, and therefore display it correctly
                    text= '%s, <em>%d</em> year old' % (short_name, age)
                else:
                    text= '%s, <em>%d</em> years old' % (short_name, age)
                self.add_day_item(text, year, month, day)
            if self.Anniv and ((self.Alive and living) or not self.Alive):
                family_list = person.get_family_handle_list()
                for fhandle in family_list:
                    fam = self.database.get_family_from_handle(fhandle)
                    father_handle = fam.get_father_handle()
                    mother_handle = fam.get_mother_handle()
                    if father_handle == person.get_handle():
                        spouse_handle = mother_handle
                    else:
                        continue # with next person if this was the marriage event
                    if spouse_handle:
                        spouse = self.database.get_person_from_handle(spouse_handle)
                        if spouse:
                            spouse_name = self.get_short_name(spouse)
                            short_name = self.get_short_name(person)
                            if self.Alive:
                                if not probably_alive(spouse, self.database, make_date(self.Year, 1, 1), 0):
                                    continue
                            married = True
                            for event_ref in fam.get_event_ref_list():
                                event = self.database.get_event_from_handle(event_ref.ref)
                                if event and event.type in [gen.lib.EventType.DIVORCE,
                                                            gen.lib.EventType.ANNULMENT,
                                                            gen.lib.EventType.DIV_FILING]:
                                    married = False
                            if married:
                                for event_ref in fam.get_event_ref_list():
                                    event = self.database.get_event_from_handle(event_ref.ref)
                                    event_obj = event.get_date_object()
                                    year = event_obj.get_year()
                                    month = event_obj.get_month()
                                    day = event_obj.get_day()
                                    years = self.Year - year
                                    if years == 0:
                                        text = "" # zero year anniversary
                                                  # display nothing 
                                    else:
                                        text = _('<span class="yearsmarried">%(spouse)s and %(person)s, <em>%(nyears)d</em> year anniversary</span>') % { 
                                            'spouse' : spouse_name,
                                            'person' : short_name,
                                            'nyears' : years,
                                            }
                                    self.add_day_item(text, year, month, day)

#------------------------------------------------------------------------
#
# WebCalOptions
#
#------------------------------------------------------------------------
class WebCalOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web calendar.
        """
        self.__add_report_options(menu)
        self.__add_content_options(menu)
        self.__add_notes_options(menu)
    
    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")
        
        target = DestinationOption( _("Destination"), 
                                    os.path.join(const.USER_HOME,"WEBCAL"))
        target.set_help( _("The destination directory for the web files"))
        target.set_directory_entry(True)
        menu.add_option(category_name, "target", target)
        
        title = StringOption(_('Calendar Title'), _('My Family Calendar')) 
        title.set_help(_("The title of the calendar"))
        menu.add_option(category_name, "title", title)
        
        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on calendar"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)
        
        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)
        
        cright = EnumeratedListOption(_('Copyright'), 0 )
        index = 0
        for copt in _COPY_OPTIONS:
            cright.add_item(index, copt)
            index += 1
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)
        
        encoding = EnumeratedListOption(_('Character set encoding'), 'utf-8' )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)

        css = EnumeratedListOption(_('StyleSheet'), _CSS_FILES[0][1])
        for style in _CSS_FILES:
            css.add_item(style[1], style[0])
        css.set_help( _("The Style Sheet to be used for the web page"))
        menu.add_option(category_name, "css", css)
        
    def __add_content_options(self, menu):
        """
        Options on the "Content Options" tab.
        """
        category_name = _("Content Options")
        
        year = NumberOption(_("Year of calendar"), time.localtime()[0], 
                            1000, 3000)
        year.set_help(_("Year of calendar"))
        menu.add_option(category_name, "year", year)

        fullyear = BooleanOption(_('Create Year At A Glance'), False)
        fullyear.set_help(_('Wheather to create A Full Year High-lighted calendar'))
        menu.add_option(category_name, 'fullyear', fullyear)

        blankyear = BooleanOption(_('Create A Printable Blank Full- Year Calendar'), False)
        blankyear.set_help(_('Wheather to create A Full Year Printable calendar'))
        menu.add_option(category_name, 'blankyear', blankyear)

        country = EnumeratedListOption(_('Country for holidays'), 0 )
        index = 0
        for item in _COUNTRIES:
            country.add_item(index, item)
            index += 1
        country.set_help( _("Holidays will be included for the selected "
                            "country"))
        menu.add_option(category_name, "country", country)

        home_link = StringOption(_('Home link'), '../index.html') 
        home_link.set_help(_("The link to be included to direct the user to "
                         "the main page of the web site"))
        menu.add_option(category_name, "home_link", home_link)
        
        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", alive)

        birthdays = BooleanOption(_("Include birthdays"), True)
        birthdays.set_help(_("Include birthdays in the calendar"))
        menu.add_option(category_name, "birthdays", birthdays)

        anniversaries = BooleanOption(_("Include anniversaries"), True)
        anniversaries.set_help(_("Include anniversaries in the calendar"))
        menu.add_option(category_name, "anniversaries", anniversaries)
        
        surname = BooleanOption(_('Check for wives to use maiden name'), True)
        surname.set_help(_("Attempt to use maiden names of women"))
        menu.add_option(category_name, "surname", surname)

    def __add_notes_options(self, menu):
        """
        Options on the "Months Notes" tabs.
        """
        category_name = _("Jan - Jun Notes")

        note_jan = StringOption(_('Jan Note'), _('This prints in January')) 
        note_jan.set_help(_("The note for the month of January"))
        menu.add_option(category_name, "note_jan", note_jan)
        
        note_feb = StringOption(_('Feb Note'), _('This prints in February')) 
        note_feb.set_help(_("The note for the month of February"))
        menu.add_option(category_name, "note_feb", note_feb)
        
        note_mar = StringOption(_('Mar Note'), _('This prints in March')) 
        note_mar.set_help(_("The note for the month of March"))
        menu.add_option(category_name, "note_mar", note_mar)
        
        note_apr = StringOption(_('Apr Note'), _('This prints in April')) 
        note_apr.set_help(_("The note for the month of April"))
        menu.add_option(category_name, "note_apr", note_apr)
        
        note_may = StringOption(_('May Note'), _('This prints in May')) 
        note_may.set_help(_("The note for the month of May"))
        menu.add_option(category_name, "note_may", note_may)
        
        note_jun = StringOption(_('Jun Note'), _('This prints in June')) 
        note_jun.set_help(_("The note for the month of June"))
        menu.add_option(category_name, "note_jun", note_jun)
        
        category_name = _("Jul - Dec Notes")

        note_jul = StringOption(_('Jul Note'), _('This prints in July')) 
        note_jul.set_help(_("The note for the month of July"))
        menu.add_option(category_name, "note_jul", note_jul)
        
        note_aug = StringOption(_('Aug Note'), _('This prints in August')) 
        note_aug.set_help(_("The note for the month of August"))
        menu.add_option(category_name, "note_aug", note_aug)
        
        note_sep = StringOption(_('Sep Note'), _('This prints in September')) 
        note_sep.set_help(_("The note for the month of September"))
        menu.add_option(category_name, "note_sep", note_sep)
        
        note_oct = StringOption(_('Oct Note'), _('This prints in October')) 
        note_oct.set_help(_("The note for the month of October"))
        menu.add_option(category_name, "note_oct", note_oct)
        
        note_nov = StringOption(_('Nov Note'), _('This prints in November')) 
        note_nov.set_help(_("The note for the month of November"))
        menu.add_option(category_name, "note_nov", note_nov)
        
        note_dec = StringOption(_('Dec Note'), _('This prints in December')) 
        note_dec.set_help(_("The note for the month of December"))
        menu.add_option(category_name, "note_dec", note_dec)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)
        
    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class Element:
    """ A parsed XML element """
    def __init__(self, name,attributes):
        'Element constructor'
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []

    def AddChild(self,element):
        'Add a reference to a child element'
        self.children.append(element)

    def getAttribute(self,key):
        'Get an attribute value'
        return self.attributes.get(key)

    def getData(self):
        'Get the cdata'
        return self.cdata

    def getElements(self, name=''):
        'Get a list of child elements'
        #If no tag name is specified, return the all children
        if not name:
            return self.children
        else:
            # else return only those children with a matching tag name
            elements = []
            for element in self.children:
                if element.name == name:
                    elements.append(element)
            return elements

    def toString(self, level=0):
        retval = " " * level
        retval += "<%s" % self.name
        for attribute in self.attributes:
            retval += " %s=\"%s\"" % (attribute, self.attributes[attribute])
        c = ""
        for child in self.children:
            c += child.toString(level+1)
        if c == "":
            retval += "/>\n"
        else:
            retval += ">\n" + c + ("</%s>\n" % self.name)
        return retval


class Xml2Obj:
    """ XML to Object """
    def __init__(self):
        self.root = None
        self.nodeStack = []

    def StartElement(self, name,attributes):
        'SAX start element even handler'
        # Instantiate an Element object
        element = Element(name.encode(),attributes)
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.AddChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)

    def EndElement(self, name):
        'SAX end element event handler'
        self.nodeStack = self.nodeStack[:-1]

    def CharacterData(self,data):
        'SAX character data event handler'
        if data.strip():
            data = data.encode()
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self,filename):
        # Create a SAX parser
        Parser = expat.ParserCreate()
        # SAX event handlers
        Parser.StartElementHandler = self.StartElement
        Parser.EndElementHandler = self.EndElement
        Parser.CharacterDataHandler = self.CharacterData
        # Parse the XML File
        ParserStatus = Parser.Parse(open(filename,'r').read(), 1)
        return self.root

class Holidays:
    """ Class used to read XML holidays to add to calendar. """
    def __init__(self, elements, country="US"):
        self.debug = 0
        self.elements = elements
        self.Country = country
        self.dates = []
        self.initialize()
    def set_country(self, country):
        self.Country = country
        self.dates = []
        self.initialize()
    def initialize(self):
        # parse the date objects
        for country_set in self.elements.children:
            if country_set.name == "country" and country_set.attributes["name"] == self.Country:
                for date in country_set.children:
                    if date.name == "date":
                        data = {"value" : "",
                                "name" : "",
                                "offset": "",
                                "type": "",
                                "if": "",
                                } # defaults
                        for attr in date.attributes:
                            data[attr] = date.attributes[attr]
                        self.dates.append(data)
    def get_daynames(self, y, m, dayname):
        if self.debug: print "%s's in %d %d..." % (dayname, m, y)
        retval = [0]
        dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(dayname)
        for d in range(1, 32):
            try:
                date = datetime.date(y, m, d)
            except ValueError:
                continue
            if date.weekday() == dow:
                retval.append( d )
        if self.debug: print "dow=", dow, "days=", retval
        return retval
    def check_date(self, date):
        retval = []
        for rule in self.dates:
            if self.debug: print "Checking ", rule["name"], "..."
            offset = 0
            if rule["offset"] != "":
                if rule["offset"].isdigit():
                    offset = int(rule["offset"])
                elif rule["offset"][0] in ["-","+"] and rule["offset"][1:].isdigit():
                    offset = int(rule["offset"])
                else:
                    # must be a dayname
                    offset = rule["offset"]
            if rule["value"].count("/") == 3: # year/num/day/month, "3rd wednesday in april"
                y, num, dayname, mon = rule["value"].split("/")
                if y == "*":
                    y = date.year
                else:
                    y = int(y)
                if mon.isdigit():
                    m = int(mon)
                elif mon == "*":
                    m = date.month
                else:
                    m = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                         'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(mon) + 1
                dates_of_dayname = self.get_daynames(y, m, dayname)
                if self.debug: print "num =", num
                d = dates_of_dayname[int(num)]
            elif rule["value"].count("/") == 2: # year/month/day
                y, m, d = rule["value"].split("/")
                if y == "*":
                    y = date.year
                else:
                    y = int(y)
                if m == "*":
                    m = date.month
                else:
                    m = int(m)
                if d == "*":
                    d = date.day
                else:
                    d = int(d)
            ndate = datetime.date(y, m, d)
            if self.debug: print ndate, offset, type(offset)
            if isinstance(offset, int):
                if offset != 0:
                    ndate = ndate.fromordinal(ndate.toordinal() + offset)
            elif isinstance(offset, basestring):
                dir = 1
                if offset[0] == "-":
                    dir = -1
                    offset = offset[1:]
                if offset in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    # next tuesday you come to, including this one
                    dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(offset)
                    ord = ndate.toordinal()
                    while ndate.fromordinal(ord).weekday() != dow:
                        ord += dir
                    ndate = ndate.fromordinal(ord)
            if self.debug: print "ndate:", ndate, "date:", date
            if ndate == date:
                if rule["if"] != "":
                    if not eval(rule["if"]):
                        continue
                retval.append(rule["name"])
        return retval

def process_holiday_file(filename):
    """ This will process a holiday file for country names """
    parser = Xml2Obj()
    element = parser.Parse(filename)
    country_list = []
    for country_set in element.children:
        if country_set.name == "country":
            if country_set.attributes["name"] not in country_list:
                country_list.append(country_set.attributes["name"])
    return country_list

def _get_countries():
    """ Looks in multiple places for holidays.xml files """
    locations = [const.PLUGINS_DIR, const.USER_PLUGINS]
    holiday_file = 'holidays.xml'
    country_list = []
    for dir in locations:
        holiday_full_path = os.path.join(dir, holiday_file)
        if os.path.exists(holiday_full_path):
            cs = process_holiday_file(holiday_full_path)
            for c in cs:
                if c not in country_list:
                    country_list.append(c)
    country_list.sort()
    country_list.insert(0, _("Don't include holidays"))
    return country_list

# TODO: Only load this once the first time it is actually needed so Gramps 
# doesn't take so long to start up.
_COUNTRIES = _get_countries()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'WebCal',
    category = CATEGORY_WEB,
    report_class = WebCalReport,
    options_class = WebCalOptions,
    modes = MODE_GUI,
    translated_name = _("Web Calendar"),
    status = _("Stable"),
    author_name = "Thom Sturgill",
    author_email = "thsturgill@yahoo.com",
    description = _("Produces web (HTML) calendars."),
    )
