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

Menu selection: Reports -> Web Page -> Web Calendar

Created 4/22/07 by Thom Sturgill based on Calendar.py (with patches)
by Doug Blank with input dialog based on NarrativeWeb.py by Don Allingham.

2008-05-11 Jason Simanek
Improving markup for optimal separation of content and presentation.

2008-June-22 Rob G. Healey
*** Remove StyleEditor, make it css based as is NarrativeWeb,
move title to first tab, re-word note tabs, complete re-write of
calendar build, added year glance, and blank year, added easter and
dst start/stop from Calendar.py, etc.

2008 Kees Bakker
Refactoring. This is an ongoing job until this plugin is in a better shape.
TODO list:
 - change filename for one_day pages to yyyy/mm/dd.html (just numbers)
 - progress bar, rethink its usage
 - in year navigation, use month in link, or 'fullyear'
 - untangle calendar_build, it's too complex the way it is
 - use standard Gramps method to display surname, see _get_regular_surname
 - daylight saving not just for USA and Europe
 - move the close_file() from one_day() to caller
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
from GrampsCfg import get_researcher
from gen.plug import PluginManager
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_WEB
from gen.plug.menu import BooleanOption, NumberOption, StringOption, \
                          EnumeratedListOption, FilterOption, PersonOption, \
                          DestinationOption
import Utils
import GrampsLocale
from QuestionDialog import ErrorDialog, WarningDialog
from Utils import probably_alive
from DateHandler import displayer as _dd
from DateHandler import parser as _dp

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------

# This information defines the list of styles in the Web calendar
# options dialog as well as the location of the corresponding SCREEN
# stylesheets.
_CSS_FILES = [
    # First is used as default selection.
    [_("Basic-Ash"),            'Web_Basic-Ash.css'],
    [_("Basic-Cypress"),        'Web_Basic-Cypress.css'],
    [_("Basic-Lilac"),          'Web_Basic-Lilac.css'],
    [_("Basic-Peach"),          'Web_Basic-Peach.css'],
    [_("Basic-Spruce"),         'Web_Basic-Spruce.css'],
    [_("Mainz"),                'Web_Mainz.css'],
    [_("Nebraska"),             'Web_Nebraska.css'],
    [_("Visually Impaired"),    'Web_Visually.css'],
    [_("No style sheet"),       ''],
    ]

_CHARACTER_SETS = [
    # First is used as default selection.
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
    '',

    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" '
    'title="Creative Commons License - By attribution" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'title="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'title="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'src="%(gif_fname)s" /></a>'
    ]

_COPY_OPTIONS = [
        _('Standard copyright'),

        # This must match _CC
        _('Creative Commons - By attribution'),
        _('Creative Commons - By attribution, No derivations'),
        _('Creative Commons - By attribution, Share-alike'),
        _('Creative Commons - By attribution, Non-commercial'),
        _('Creative Commons - By attribution, Non-commercial, No derivations'),
        _('Creative Commons - By attribution, Non-commercial, Share-alike'),

        _('No copyright notice'),
        ]

def _make_date(year, month, day):
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
        self.title_text  = menu.get_option_by_name('title').get_value()
        filter_option =  menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.ext = menu.get_option_by_name('ext').get_value()
        self.copy = menu.get_option_by_name('cright').get_value()
        self.encoding = menu.get_option_by_name('encoding').get_value()
        self.css = menu.get_option_by_name('css').get_value()

        self.country = menu.get_option_by_name('country').get_value()
        self.start_dow = menu.get_option_by_name('start_dow').get_value()

        self.partyear = menu.get_option_by_name('partyear').get_value()
        self.multiyear = menu.get_option_by_name('multiyear').get_value()

        self.start_year = menu.get_option_by_name('start_year').get_value()
        self.end_year = menu.get_option_by_name('end_year').get_value()

        self.fullyear = menu.get_option_by_name('fullyear').get_value()
        self.blankyear = menu.get_option_by_name('blankyear').get_value()

        self.maiden_name = menu.get_option_by_name('maiden_name').get_value()

        self.alive = menu.get_option_by_name('alive').get_value()
        self.birthday = menu.get_option_by_name('birthdays').get_value()
        self.anniv = menu.get_option_by_name('anniversaries').get_value()
        self.home_link = menu.get_option_by_name('home_link').get_value().strip()

        self.month_notes  = [menu.get_option_by_name('note_jan').get_value(),
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

        # identify researcher name and e-mail address
        # as Narrated WebSite already does
        researcher = get_researcher()
        self.author = researcher.name
        if self.author:
            self.author = self.author.replace(',,,', '')
        self.email = researcher.email

        self.start_month = 1            # set to January, and it can change
        self.end_month = 12             # set to December, this value never changes

        today = time.localtime()        # set to today's date
        self.today = datetime.date(today[0], today[1], today[2])

        self.warn_dir = True            # Only give warning once.
        self.imgs = []

        # self.calendar is a dict; key is the month number
        # Each entry in the dict is also a dict; key is the day number.
        # The day dict is a list of things to display for that day.
        # These things are: birthdays and anniversaries
        self.calendar = {}

        calendar.setfirstweekday(_dow_gramps2iso[self.start_dow])

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present and if the target is not an archive,
        then the destination directory will be created.

        Normally 'to_fname' will be just a filename, without directory path.

        'to_dir' is the relative path name in the destination root. It will
        be prepended before 'to_fname'.
        """
        dest = os.path.join(self.html_dir, to_dir, to_fname)

        destdir = os.path.dirname(dest)
        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        if from_fname != dest:
            shutil.copyfile(from_fname, dest)
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

    def add_day_item(self, text, year, month, day, event):
        if day == 0:
            # This may happen for certain "about" dates.
            day = 1     # Use first day of the month
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])

        if month > 0:
            try:
                my_date = datetime.date(year, month, day)
            except ValueError:
                my_date = '...'
        else:
            my_date = '...'              #Incomplete date as in about, circa, etc.

        day_list.append((my_date, text, event))
        month_dict[day] = day_list
        self.calendar[month] = month_dict

    def get_holidays(self, year, country="United States"):
        """
        Looks in multiple places for holidays.xml file.
        the holidays file will be used first if it exists in user's plugins, otherwise,
        the GRAMPS plugins will be checked.
        """

        holiday_file = 'holidays.xml'
        holiday_full_path = ""
        fname1 = os.path.join(const.USER_PLUGINS, holiday_file)
        fname2 = os.path.join(const.PLUGINS_DIR, holiday_file)
        if os.path.exists(fname1):
            holiday_full_path = fname1
        elif os.path.exists(fname2):
            holiday_full_path = fname2
        if holiday_full_path != "":
            self.process_holiday_file(year, holiday_full_path, country)

    def process_holiday_file(self, year, filename, country):
        """
        This will process the holidays file for the selected country.
         
        All holidays, except Easter, and Daylight Saving start/ stop, will be
        processed from the holidays.xml file.  Easter and DST will be handled by
        specific mathematical formulas within this plugin ...

        "Easter" -- _easter()
        "Daylight Saving Time" -- _get_dst_start_stop() 
        0 = year, 1 = month, 2 = day  
        """

        parser = Xml2Obj()
        element = parser.Parse(filename)
        holidays_calendar = Holidays(element, country)
        date = datetime.date(year, 1, 1)
        while date.year == year:
            event_date = time.strptime('%d/%d/%d' % (date.year, date.month, date.day), '%Y/%m/%d')
            holidays = holidays_calendar.check_date(date)
            for text in holidays:
                if text == "Easter": # TODO. Verify if this needs translation, and how
                    easter = _easter(year)
                    self.add_holiday_item(_("Easter"), easter[0], easter[1], easter[2])
                elif text == "Daylight Saving begins":  # TODO. Verify if this needs translation, and how
                    # TODO. There is more than USA and Europe.
                    if Utils.xml_lang() == "en-US": # DST for United States of America
                        dst_start, dst_stop = _get_dst_start_stop(year)
                    else:                           # DST for Europe
                        dst_start, dst_stop = _get_dst_start_stop(year, "eu")
                    self.add_holiday_item(_("Daylight Saving begins"), \
                        dst_start[0], dst_start[1], dst_start[2])
                    self.add_holiday_item(_("Daylight Saving ends"), \
                        dst_stop[0], dst_stop[1], dst_stop[2])
                elif text == "Daylight Saving ends":
                    pass                # end is already done above
                else: # not easter, or Daylight Saving Time
                    # ???? Why do we need _(text)? Find out what is returned by holidays_calendar.check_date()
                    self.add_holiday_item(_(text), event_date[0], event_date[1], event_date[2])
            date = date.fromordinal( date.toordinal() + 1)

    def add_holiday_item(self, text, year, month, day):
        if day == 0:
            # This may happen for certain "about" dates.
            day = 1     # Use first day of the month
        month_dict = self.holidays.get(month, {})
        day_list = month_dict.get(day, [])

        day_list.append(text)
        month_dict[day] = day_list
        self.holidays[month] = month_dict

    def copy_calendar_files(self):
        """
        Copies all the necessary files
        """
        # Copy the normal stylesheet
        if self.css != "":
            fname = os.path.join(const.DATA_DIR, self.css)
            self.copy_file(fname, self.css, "styles")

        # copy print stylesheet
        fname = os.path.join(const.DATA_DIR, "Web_Print-Default.css")
        self.copy_file(fname, "Web_Print-Default.css", "styles")

        # Copy GRAMPS favicon
        fname = os.path.join(const.IMAGE_DIR, "favicon.ico")
        self.copy_file(fname, "favicon.ico", "images")

        # copy copyright image
        if 0 < self.copy < len(_CC):
            fname = os.path.join(const.IMAGE_DIR, 'somerights20.gif')
            self.copy_file(fname, 'somerights20.gif', 'images')

        for f in self.imgs:
            from_path = os.path.join(const.IMAGE_DIR, f)
            self.copy_file(from_path, f, "images")

    def display_month_navs(self, of, nr_up, year, currentsection, use_home=False):
        """
        Will create and display the navigation menu bar

        use_home will produce a link to wherever you specify as a home link

        cal is one of these:
        od = one_day(), wc = normal_cal(), yg = year_glance(), by = blank_year()
        """

        navs = []

        # check to see if we are using a home link???
        if use_home:
            navs.append((self.home_link,  _('Home'),  True))

        for month in range(self.start_month, self.end_month + 1):
            navs.append((month, month, True))

        # Add a link for year_glance() if requested
        navs.append(('fullyear', _('Year Glance'),    self.fullyear))

        # add a link to blank_year() if requested
        navs.append(('blankyear', _('Blank Calendar'), self.blankyear))

        of.write('<div id="subnavigation">\n')
        of.write('\t<ul>\n')

        for url_fname, nav_text, cond in navs:
            url = ''
            cs = False
            if cond:
             
                subdirs = ['..'] * nr_up
                subdirs.append(str(year)) 

                # Note. We use '/' here because it is a URL, not a OS dependent pathname
                if type(url_fname) == int:
                    url_fname = _get_long_month_name(url_fname)

                if type(nav_text) == int:
                    nav_text = _get_short_month_name(nav_text)

                # Figure out if we need <li id="CurrentSection"> or just plain <li>
                if url_fname == currentsection:
                    cs = True

                url = url_fname
                if not url.startswith('http:'):
                    url = '/'.join(subdirs + [url_fname])
                    if not _has_webpage_extension(url):
                        url += self.ext

                cs = cs and ' id="CurrentSection"' or ''
                of.write('\t\t<li%s><a href="%s">%s</a></li>\n' % (cs, url, nav_text))

        of.write('\t</ul>\n')
        of.write('</div>\n\n')

    def display_year_navs(self, of, nr_up, currentsection):
        """
        This will create the year navigation menu bar
        """

        of.write('<div id="navigation">\n')
        of.write('\t<ul>\n')
        cols = 0  
        cal_year = self.start_year
        while ((0 <= cols < 25) and (self.start_year <= cal_year <= self.end_year)):
            url = ''
            cs = False

            # begin subdir level
            subdirs = ['..'] * nr_up
            subdirs.append(str(cal_year))

            # each year will link to January, unless self.partyear is True,
            # then it will link to current month.
            # this will always need an extension added
            lng_month = _get_long_month_name(1)
            if self.partyear:
                if cal_year == self.today.year:
                    lng_month = _get_long_month_name(self.today.month)

            # Note. We use '/' here because it is a URL, not a OS dependent pathname
            url = '/'.join(subdirs + [lng_month]) + self.ext

            # determine if we need to highlight???
            if str(cal_year) == currentsection:
                cs = True

            # if True, highlight currentsection
            cs = cs and ' id="CurrentSection"' or ''

            of.write('\t\t<li%s><a href="%s">%s</a></li>\n'  % (cs, url, str(cal_year)))

            # increase year
            cal_year += 1

            # increase column
            cols += 1

        of.write('\t</ul>\n')
        of.write('</div>\n\n')

    def calendar_common(self, of, nr_up, year, currsec1, title, body_id, use_home=False, add_print=True):
        """
        Will create the common information for each calendar being created
        """

        # Add Header
        self.write_header(of, nr_up, title, add_print)

        of.write('<body id="%s">\n' % body_id)

        # Header Title
        of.write('<div id="header">\n')
        of.write('\t<h1 id="SiteTitle">%s</h1>\n' % title)
        if self.author != '':
            of.write('\t<p id="CreatorInfo">')
            if self.email != '':  
                msg = _('Created for <a href="mailto:%(email)s?subject=WebCal">%(author)s</a>\n') % {
                    'email'  : self.email,
                    'author' : self.author}
            else:
                msg = _('Created for %(author)s\n') % {'author' : self.author}
            of.write('%s</p>\n' % msg)
        of.write('</div>\n')  # end header

        if self.multiyear:
            # create Year Navigation menu
            self.display_year_navs(of, nr_up, str(year))

        # adjust the months being created if self.partyear is True
        # and year is eequal to current year, then start_month is current month
        self.start_month = 1
        if year == self.today.year:
            if self.partyear:
                self.start_month = self.today.month

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        self.display_month_navs(of, nr_up, year, currsec1, use_home)

        of.write('<div class="content">\n')

    def calendar_build(self, of, cal, year, month):
        """
        This does the work of building the calendar
        'cal' - one of "yg", "by", "wc"
        'month' - month number 1, 2, .., 12
        """

        # define names for long and short month names
        lng_month = _get_long_month_name(month)
        shrt_month = _get_short_month_name(month)

        # dow (day-of-week) uses Gramps numbering, sunday => 1, etc
        start_dow = self.start_dow
        col2day = [(x-1)%7+1 for x in range(start_dow, start_dow + 7)]

        # Note. GrampsLocale has sunday => 1, monday => 2, etc
        # We slice out the first empty element.
        day_names = GrampsLocale.long_days

        # Translate a Gramps day number into a HTMLclass
        def get_class_for_daycol(col):
            day = col2day[col]
            if day == 1:
                return "weekend sunday"
            elif day == 7:
                return "weekend saturday"
            return "weekday"

        def get_name_for_daycol(col):
            day = col2day[col]
            return day_names[day]

        # monthinfo is filled using standard Python library calendar.monthcalendar
        # It fills a list of 7-day-lists. The first day of the 7-day-list is
        # determined by calendar.firstweekday
        monthinfo = calendar.monthcalendar(year, month)

        # Begin calendar head. We'll use the capitalized name, because here it seems
        # appropriate for most countries.
        month_name = lng_month.capitalize()
        th_txt = month_name
        if cal == 'wc': # normal_cal()
            if not self.multiyear:
                th_txt = '%s %d' % (month_name, year)
        of.write('<!-- %s -->\n\n' % month_name)
        of.write('<table id="%s" class="calendar">\n' % month_name)
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th colspan="7" class="monthName">%s</th>\n' % th_txt)
        of.write('\t\t</tr>\n')

        # Calendar weekday names header
        of.write('\t\t<tr>\n')
        for day_col in range(7):
            dayclass = get_class_for_daycol(day_col)
            dayname = get_name_for_daycol(day_col)
            #of.write('\t\t\t<th class="%s">%s</th>\n' % (dayclass, get_name_for_daycol(day_col)))
            of.write('\t\t\t<th class="%s"><abbr title="%s">%s</abbr></th>\n' % (dayclass, dayname, dayname[0]))
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')

        # begin table body
        of.write('\t<tbody>\n')

        # Compute the first day to display for this month.
        # It can also be a day in the previous month.
        current_date = datetime.date(year, month, 1) # first day of the month
        current_ord = current_date.toordinal() - monthinfo[0].count(0)

        # get last month's last week for previous days in the month
        if month == 1:
            prevmonth = calendar.monthcalendar(year - 1, 12)
        else:
            prevmonth = calendar.monthcalendar(year, month-1)
        num_weeks = len(prevmonth)
        lastweek_prevmonth = prevmonth[num_weeks - 1]

        # get next month's first week for next days in the month
        if month == 12:
            nextmonth = calendar.monthcalendar(year + 1, 1)
        else:
            nextmonth = calendar.monthcalendar(year, month + 1)
        firstweek_nextmonth = nextmonth[0]

        nweeks = len(monthinfo)
        for week_row in range(0, nweeks):
            week = monthinfo[week_row]
            of.write('\t\t<tr class="week%d">\n' % (week_row+1))

            for day_col in range(0, 7):
                dayclass = get_class_for_daycol(day_col)
                hilightday = 'highlight ' + dayclass

                day = week[day_col]
                if day == 0:                                   # a day in the previous or next month
                    if week_row == 0:                          # a day in the previous month
                        specday = lastweek_prevmonth[day_col]
                        specclass = "previous " + dayclass
                    elif week_row == nweeks-1:                 # a day in the next month
                        specday = firstweek_nextmonth[day_col]
                        specclass = "next " + dayclass

                    #if specclass[0] == 'p': # previous day of last month
                    #    of.write('\t\t\t<td id="prevday%d" ' % specday)
                    #else:                   # next day of next month
                    #    of.write('\t\t\t<td id="nextday%d" ' % specday)
                    of.write('\t\t\t<td class="%s">\n' % specclass)
                    of.write('\t\t\t\t<div class="date">%d</div>\n' % specday)
                    of.write('\t\t\t</td>\n')

                else:                             # normal day number in current month
                    if cal == "by":               # blank_year() doesn't need any highlighting or hyperlinks
                        of.write('\t\t\t<td id="%s%02d" class="%s">\n' % (shrt_month, day, dayclass))
                        of.write('\t\t\t\t<div class="date">%d</div>\n' % day)
                        of.write('\t\t\t</td>\n')
                    else:
                        thisday = datetime.date.fromordinal(current_ord)
                        of.write('\t\t\t<td id="%s%02d" ' % (shrt_month, day))
                        if thisday.month == month: # Something this month
                            holiday_list = self.holidays.get(month, {}).get(thisday.day, [])
                            bday_anniv_list = self.calendar.get(month, {}).get(thisday.day, [])
                            if (holiday_list > []) or (bday_anniv_list > []):
                                evt_date = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')

                                # Year at a Glance
                                if cal == "yg":
                                    did_some = self.one_day(of, year, evt_date, cal, holiday_list, bday_anniv_list)
                                    if did_some:
                                        # Notice the code in one_day(): cal_fname = '%s%d%s' % (shrt_month, day, self.ext)
                                        # TODO. Create file for one_day()
                                        # The HREF is relative to the year path.
                                        fname = '%s%d%s' % (shrt_month, day, self.ext)
                                        fname = '/'.join([lng_month, fname])
                                        of.write('class="%s">\n' % hilightday)
                                        of.write('\t\t\t\t<a id="%s%d" href="%s" title="%s%d">\n'
                                                 % (shrt_month, day, fname, shrt_month, day))
                                        of.write('\t\t\t\t\t<div class="date">%d</div>\n' % day)
                                        of.write('\t\t\t\t</a>\n')
                                    else: 
                                        of.write('class="%s">\n' % dayclass)
                                        of.write('\t\t\t\t<div class="date">%d</div>\n' % day)

                                # WebCal
                                elif cal == 'wc':
                                    of.write('class="%s">\n' % hilightday)
                                    of.write('\t\t\t\t<div class="date">%d</div>\n' % day)
                                    self.one_day(of, year, evt_date, cal, holiday_list, bday_anniv_list)

                            # no holiday/ bday/ anniversary this day
                            else: 
                                of.write('class="%s">\n' % dayclass)
                                of.write('\t\t\t\t<div class="date">%d</div>\n' % day)

                        # no holiday/ bday/ anniversary this month 
                        else: 
                            of.write('class="%s">\n' % dayclass)
                            of.write('\t\t\t\t<div class="date">%d</div>\n' % day)

                        # close the day/ column
                        of.write('\t\t\t</td>\n')

                # change day number
                current_ord += 1

            # close the week/ row
            of.write('\t\t</tr>\n')

        if cal == "yg":
            # Fill up till we have 6 rows, so that the months align properly
            for i in range(nweeks, 6):
                of.write('\t\t<tr class="week%d">\n' % (i+1))
                of.write('\t\t\t<td colspan="7"></td>\n')
                of.write('\t\t</tr>\n')

        # close table body
        of.write('\t</tbody>\n')

    def write_header(self, of, nr_up, title, add_print=True):
        """
        This creates the header for the Calendars including style embedded for special purpose
        'nr_up' - number of directory levels up, started from current page, to the
        root of the directory tree (i.e. to self.html_dir).
        """

        of.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n')
        of.write('     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        of.write('<html xmlns="http://www.w3.org/1999/xhtml" ')
        xmllang = Utils.xml_lang()
        of.write('xml:lang="%s" lang="%s">\n' % (xmllang, xmllang))
        of.write('<head>\n')
        of.write('\t<title>%s</title>\n\n' % title)
        of.write('\t<meta http-equiv="Content-Type" content="text/html;charset=%s" />\n'
                % self.encoding)
        of.write('\t<meta name="robots" content="noindex" />\n')
        of.write('\t<meta name="generator" content="GRAMPS 3.1.x: http://www.gramps-project.org" />\n')
        of.write('\t<meta name="author" content="%s" />\n\n' % self.author)

        subdirs = ['..'] * nr_up

        # link to stylesheet
        fname = '/'.join(subdirs + ['styles'] + [self.css])
        of.write('\t<link rel="stylesheet" href="%s" type="text/css" media="screen" />\n' % fname)

        # link to _CALENDARPRINT stylesheet
        if add_print:
            fname = '/'.join(subdirs + ['styles'] + ["Web_Print-Default.css"])
            of.write('\t<link rel="stylesheet" href="%s" type="text/css" media="print" />\n' % fname)

        # link to GRAMPS favicon
        fname = '/'.join(subdirs + ['images'] + ['favicon.ico'])
        of.write('\t<link rel="shortcut icon" href="%s" type="image/icon" />\n' % fname)

        of.write('</head>\n\n')

    def write_footer(self, of, nr_up):
        """
        Writes the footer section of the pages
        'nr_up' - number of directory levels up, started from current page, to the
        root of the directory tree (i.e. to self.html_dir).
        """

        of.write('<div class="fullclear"></div>\n')
        of.write('</div>\n')            # Closing "content"

        of.write('<div id="footer">\n')

        # Display date as user set in preferences
        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)
        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % {'date' : value}
        of.write('\t<p id="createdate">%s</p>\n' % msg)

        copy_nr = self.copy
        text = ''
        if copy_nr == 0:
            if self.author:
                text = "&copy; %s %s" % (self.today.year, self.author)
        elif 0 < copy_nr < len(_CC):
            subdirs = ['..'] * nr_up
            # Note. We use '/' here because it is a URL, not a OS dependent pathname
            fname = '/'.join(subdirs + ['images'] + ['somerights20.gif'])
            text = _CC[copy_nr] % {'gif_fname' : fname}
            self.use_copyright = True
        else:
            text = "&copy; %s %s" % (self.today.year, self.author)
        of.write('\t<p id="copyright">%s</p>\n' % text)

        of.write('\t<p id="quality"><a href="http://validator.w3.org/check?uri=referer">')
        of.write('<img src="http://www.w3.org/Icons/valid-xhtml10" ')
        of.write('alt="Valid XHTML 1.0 Transitional" height="31" width="88" />')
        of.write('</a></p>\n')

        of.write('</div>\n')
        of.write('</body>\n')
        of.write('</html>\n')

    def create_file(self, fname, subdir):
        """
        Create a file in the html_dir tree.
        If the directory does not exist, create it.
        """

        fname = os.path.join(self.html_dir, subdir, fname)

        if not _has_webpage_extension(fname):
            fname += self.ext

        destdir = os.path.dirname(fname)

        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        of = codecs.EncodedFile(open(fname, "w"), 'utf-8', self.encoding, 'xmlcharrefreplace')
        return of

    def close_file(self, of):
        of.close()

    def one_day(self, of, year, event_date, cal, holiday_list, bday_anniv_list):
        """
        This method creates the One Day page for "Year At A Glance"

        'holiday_list' - list of holidays to display on this day
        'bday_anniv_list' - list of birthdays and anniversaries to display on this day

        one or both of these dictionaries will possibly hav something in it

        'day_list' - a combination of both dictionaries to be able to create one day
             date, text, event --- are necessary for figuring the age or years married
             for each year being created...
        """

        day_list = []

        # holiday on this day
        if holiday_list > []:
            for p in holiday_list:
                for line in p.splitlines():
                    day_list.append((event_date, line, _('Holiday')))

        # birthday/ anniversary on this day
        if bday_anniv_list > []:
            for date, text, event in bday_anniv_list:

                # '...' signifies an incomplete date for an event. See add_day_item()
                txt_str = None
                if date != '...':
                    years = year - date.year

                    # a birthday
                    if event == 'birthday':
                        if years == 1:
                            txt_str = _('%(short_name)s, <em>%(age)d</em> year old') % {
                                'short_name' : text,
                                'age'        : years}
                        elif 2 <= years <= 105:
                            txt_str = _('%(short_name)s, <em>%(age)d</em> years old') % {
                                'short_name' : text, 
                                'age'        : years}

                        # TODO. Think about this limit a bit more.
                        # if age is greater than 105, 
                        # STOP!  Do Nothing!!!
                        else:
                            txt_str = None

                    # an anniversary
                    elif event == 'anniversary':

                        # if married years is less than 76 years  
                        if 1 <= years < 75:
                            txt_str = _('%(couple)s, <em>%(nyears)d</em> year anniversary') % {
                                'couple' : text,
                                'nyears' : years}
                            txt_str = '<span class="yearsmarried">%s</span>' % txt_str

                        # TODO. Think about this limit a bit more.
                        # if married years is greater than 75 years, 
                        # STOP!  Do Nothing!!!
                        else:
                            txt_str = None

                # incomplete date
                else:
                    txt_str = None

                if txt_str is not None:
                    day_list.append((date, txt_str, event))

        # something for this day
        if day_list > []:

            if cal == 'yg':

                # This is a one_day in the year-at-a-glance calendar

                # slice up event_date to get year, month, and day
                year, month, day = event_date[0], event_date[1], event_date[2]

                # define names for long and short month
                lng_month = _get_long_month_name(month)
                shrt_month = _get_short_month_name(month)

                # Name the file, and create it (see code in calendar_build)
                cal_fname = '%s%d%s' % (shrt_month, day, self.ext)
                fpath = os.path.join(str(year), lng_month) 
                of = self.create_file(cal_fname, fpath)

                # set date display as in user prevferences 
                my_date = gen.lib.Date()
                my_date.set_yr_mon_day(year, month, day)
                my_date = _dd.display(my_date)

                self.calendar_common(of, 2, year, lng_month, _('One Day Within A Year'), my_date)

                of.write('\t<h3 id="OneDay">%s</h3>\n' % my_date)

            of.write('\t<ul>\n')
            for date, text, event in day_list:
                of.write('\t\t<li>%s</li>\n' % text)
            of.write('\t</ul>\n')

            # Only close the file for "Year At A Glance"
            if cal == 'yg':
                self.write_footer(of, 2)
                self.close_file(of)

        # Let caller know we did output something.
        return day_list > []

    def blank_year(self, year):
        """
        This method will create the Printable Full Year One Page Calendar...
        """

        nr_up = 1                       # Number of directory levels up to get to root

        # Name the file, and create it
        cal_fname = 'blankyear'
        of = self.create_file(cal_fname, str(year))

        # Page Title
        if not self.multiyear: 
            title = ' '.join([str(year), _(' Blank Calendar')])
        else:
            title = _('Blank Calendar')

        self.calendar_common(of, nr_up, year, 'blankyear', title, 'fullyear')

        # generate progress pass for "Blank Year"
        self.progress.set_pass(_('Creating Blank Year calendars'), self.end_month - self.start_month)

        for month in range(self.start_month, self.end_month + 1):

            # build the calendar
            self.calendar_build(of, "by", year, month)

            of.write('<tfoot>\n')
            of.write('\t<tr><td colspan="7"></td></tr>\n')
            of.write('</tfoot>\n')
            of.write('</table>\n\n')

            # increase progress bar
            self.progress.step()

        # Write footer and close file
        self.write_footer(of, nr_up)
        self.close_file(of)

    def year_glance(self, year):
        """
        This method will create the Full Year At A Glance Page...
        """

        nr_up = 1                       # Number of directory levels up to get to root

        # Name the file, and create it
        cal_fname = 'fullyear'
        of = self.create_file(cal_fname, str(year))

        # page title
        title = _("%(year)d, At A Glance") % {'year' : year}

        self.calendar_common(of, nr_up, year, 'fullyear', title, 'fullyearlinked')

        # page description 
        of.write('<div class="content">\n')
        of.write('<p id="description">\n')
        # TODO. The "red square" is only valid for some style sheets.
        of.write(_('This calendar is meant to give you access to all your data at a glance '
        'compressed into one page. Clicking on a date will take you to a '
        'page that shows all the events for that date, if there are any!\n'))
        of.write('</p>\n')
        of.write('</div>\n\n')

        # generate progress pass for "Year At A Glance"
        self.progress.set_pass(_('Creating Year At A Glance calendars'), self.end_month - self.start_month)

        for month in range(self.start_month, self.end_month + 1):

            # build the calendar
            self.calendar_build(of, "yg", year, month)

            # create note section for "Year At A Glance"
            note = self.month_notes[month-1].strip()
            note = note or "&nbsp;"
            of.write('\t<tfoot>\n')
            of.write('\t\t<tr>\n')
            of.write('\t\t\t<td colspan="7">%s</td>\n' % note)
            of.write('\t\t</tr>\n')
            of.write('\t</tfoot>\n')
            of.write('</table>\n\n')

            # increase progress bar
            self.progress.step()

        # write footer section, and close file
        self.write_footer(of, nr_up)
        self.close_file(of)

    def write_report(self):
        """
        The short method that runs through each month and creates a page. 

        if self.partyear, use will enter the start month, ending month, start year, and ending year
        else, year is equal to the current year, set by self.today 
        """

        # open progress meter bar
        self.progress = Utils.ProgressMeter(_("Generate XHTML Calendars"), '')

        # get data from database for birthdays/ anniversaries
        # TODO. Verify that we collect correct info based on start_year
        self.collect_data(self.start_year)

        if self.css == "Web_Mainz.css":
            # Copy Mainz Style Images
            self.imgs += ["Web_Mainz_Bkgd.png",
                     "Web_Mainz_Header.png",
                     "Web_Mainz_Mid.png",
                     "Web_Mainz_MidLight.png",
                     ]

        # Copy all files for the calendars being created
        self.copy_calendar_files()

        # create calendars with multiple years up to twenty-five years
        # navigation bar length will only support twenty-five years at any given time
        if self.multiyear:
            # Clip to max 25 years
            if ((self.end_year - self.start_year + 1) > 25):
                self.end_year = self.start_year + 25 - 1

            for cal_year in range(self.start_year, (self.end_year + 1)):

                 # generate progress pass for year ????
                self.progress.set_pass(_('Creating year %d calendars' % cal_year), '')

                # initialize the holidays dict to fill:
                self.holidays = {}

                # get the information from holidays for every year being created
                if self.country != 0: # Don't include holidays
                    self.get_holidays(cal_year, _COUNTRIES[self.country]) # _country is currently global

                # adjust the months being created if self.partyear is True,
                # and if the year is the current year, then start month is current month  
                self.start_month = 1
                if cal_year == self.today.year:
                    if self.partyear:
                        self.start_month = self.today.month

                # create "WebCal" calendar pages
                self.normal_cal(cal_year)

                # create "Blank Year" calendar page
                if self.blankyear:
                    self.blank_year(cal_year)

                # create "Year At A Glance" and "One Day" calendar pages
                if self.fullyear:
                    self.year_glance(cal_year)

        # a single year
        else:
            cal_year = self.start_year

            self.holidays = {}

            # get the information from holidays for each year being created
            if self.country != 0: # Don't include holidays
                self.get_holidays(cal_year, _COUNTRIES[self.country]) # _COUNTRIES is currently global

            # generate progress pass for single year 
            #self.progress.set_pass(_('Creating calendars'), self.end_month - self.start_month)

            # adjust the months being created if self.partyear is True,
            # and if the year is the current year, then start month is current month  
            self.start_month = 1
            if cal_year == self.today.year:
                if self.partyear:
                    self.start_month = self.today.month

            # create "WebCal" calendar pages
            self.normal_cal(cal_year)

            # create "Blank Year" calendar page
            if self.blankyear:
                self.blank_year(cal_year)

            # create "Year At A Glance"
            if self.fullyear:
                self.year_glance(cal_year)

        # Close the progress meter
        self.progress.close()

    def normal_cal(self, year):
        """
        This method provides information and header/ footer to the calendar month
        """

        # do some error correcting if needed
        if self.multiyear:
            if self.end_year < self.start_year:
                # Huh? Why start_year+1?
                self.end_year = self.start_year + 1

        nr_up = 1                   # Number of directory levels up to get to self.html_dir / root

        # generate progress pass for "WebCal"
        self.progress.set_pass(_('Creating WebCal calendars'), self.end_month - self.start_month)

        for month in range(self.start_month, self.end_month + 1):

            # Name the file, and create it
            cal_fname = _get_long_month_name(month)
            of = self.create_file(cal_fname, str(year))

            self.calendar_common(of, nr_up, year, cal_fname, self.title_text, 'WebCal', use_home=True)

            # build the calendar
            self.calendar_build(of, "wc", year, month)

            # create note section for "WebCal"
            note = self.month_notes[month-1].strip()
            note = note or "&nbsp;"
            of.write('\t<tfoot>\n')
            of.write('\t\t<tr>\n')
            of.write('\t\t\t<td colspan="7">%s</td>\n' % note)
            of.write('\t\t</tr>\n')
            of.write('\t</tfoot>\n')
            of.write('</table>\n\n')

            # write footer section, and close file
            self.write_footer(of, nr_up)
            self.close_file(of)

            # increase progress bar
            self.progress.step()

    def collect_data(self, year):
        """
        This method runs through the data, and collects the relevant dates
        and text.

        TODO The use of living variable is too loosely and too liberable to be 
        properly used.  It only checks to see i an individual was dead as of 
        January, 1, ????--see line 1147

        if person is dead, then do nothing more!!!
        """
        self.progress.set_pass(_('Applying Filter...'), '')
        people = self.filter.apply(self.database,
                                   self.database.get_person_handles(sort_handles=False))

        self.progress.set_pass(_("Reading database..."), len(people))
        for person_handle in people:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)
            family_list = person.get_family_handle_list()
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.database.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            death_ref = person.get_death_ref()
            death_date = None
            if death_ref:
                death_event = self.database.get_event_from_handle(death_ref.ref)
                death_date = death_event.get_date_object()

            # if person is dead, STOP! Nothing further to do
            if death_date == None: 
                living = probably_alive(person, self.database, _make_date(year, 1, 1), 0)

                # add birthday if requested
                if self.birthday and birth_date != None and ((self.alive and living) or not self.alive):
                    year = birth_date.get_year()
                    month = birth_date.get_month()
                    day = birth_date.get_day()

                    # add some things to handle maiden name:
                    father_lastname = None # husband, actually
                    sex = person.get_gender()
                    if sex == gen.lib.Person.FEMALE:
                        if self.maiden_name in ['spouse_first', 'spouse_last']: # get husband's last name:
                            if len(family_list) > 0:
                                if self.maiden_name == 'spouse_first':
                                    fhandle = family_list[0]
                                else:
                                    fhandle = family_list[-1]
                                fam = self.database.get_family_from_handle(fhandle)
                                father_handle = fam.get_father_handle()
                                mother_handle = fam.get_mother_handle()
                                if mother_handle == person_handle:
                                    if father_handle:
                                        father = self.database.get_person_from_handle(father_handle)
                                        if father != None:
                                            father_name = father.get_primary_name() 
                                            father_lastname = _get_regular_surname(sex, father_name)
                    short_name = _get_short_name(person, father_lastname)
                    # Huh? Why translate this?
                    text = _('%(short_name)s') % {'short_name' : short_name}
                    self.add_day_item(text, year, month, day, 'birthday')

                # add anniversary if requested
                if self.anniv and ((self.alive and living) or not self.alive):
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
                                death_ref = spouse.get_death_ref()
                                death_date = None
                                if death_ref:
                                    death_event = self.database.get_event_from_handle(death_ref.ref)
                                    death_date = death_event.get_date_object()

                                # if spouse is dead, STOP! Nothing more to do!
                                if death_date == None:
                                    spouse_name = _get_short_name(spouse)
                                    short_name = _get_short_name(person)
                                    if self.alive:
                                        if not probably_alive(spouse, self.database, _make_date(year, 1, 1), 0):
                                            continue
                                    are_married = _get_marrital_status(fam, self.database)
                                    if are_married is not None:
                                        for event_ref in fam.get_event_ref_list():
                                            event = self.database.get_event_from_handle(event_ref.ref)
                                            event_obj = event.get_date_object()
                                            year = event_obj.get_year()
                                            month = event_obj.get_month()
                                            day = event_obj.get_day()
                                            text = _('%(spouse)s and %(person)s') % {
                                                     'spouse' : spouse_name,
                                                     'person' : short_name}
                                            self.add_day_item(text, year, month, day, 'anniversary')

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
                                    os.path.join(const.USER_HOME, "WEBCAL"))
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
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1])
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

        # set to today's date for use in menu, etc.
        # 0 = year, 1 = month, 2 = day
        today = time.localtime()
        self.today = datetime.date(today[0], today[1], today[2]) 

        partyear = BooleanOption(_('Create Partial Year calendar'), False)
        partyear.set_help(_('Create a partial year calendar. The start month will be'
                              ' equal to the current month to the end of the year.'))
        menu.add_option(category_name, 'partyear', partyear)

        self.__multiyear = BooleanOption(_('Create multiple year calendars'), False)
        self.__multiyear.set_help(_('Whether to create Multiple year calendars or not.'))
        menu.add_option(category_name, 'multiyear', self.__multiyear)
        self.__multiyear.connect('value-changed', self.__multiyear_changed) 

        self.__start_year = NumberOption(_('Start Year for the Calendar(s)'), self.today.year, 1900, 3000)
        self.__start_year.set_help(_('Enter the starting year for the calendars between 1900 - 3000'))
        menu.add_option(category_name, 'start_year', self.__start_year)

        self.__end_year = NumberOption(_('End Year for the Calendar(s)'), self.today.year, 1900, 3000)
        self.__end_year.set_help(_('Enter the ending year for the calendars between 1900 - 3000.'
                                   '  if multiple years is selected, then only twenty years at any given time'))
        menu.add_option(category_name, 'end_year', self.__end_year)

        self.__multiyear_changed()

        fullyear = BooleanOption(_('Create "Year At A Glance" Calendar(s)'), False)
        fullyear.set_help(_('Whether to create A one-page mini calendar with dates highlighted'))
        menu.add_option(category_name, 'fullyear', fullyear)

        blankyear = BooleanOption(_('Create "Printable Blank" Calendar(s)'), False)
        blankyear.set_help(_('Whether to create A Full Year Printable calendar'))
        menu.add_option(category_name, 'blankyear', blankyear)

        country = EnumeratedListOption(_('Country for holidays'), 0 )
        for index, item in enumerate(_COUNTRIES):
            country.add_item(index, item)
        country.set_help(_("Holidays will be included for the selected "
                            "country"))
        menu.add_option(category_name, "country", country)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item("spouse_first", _("Wives use husband's surname (from first family listed)"))
        maiden_name.add_item("spouse_last", _("Wives use husband's surname (from last family listed)"))
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)

        # Default selection ????
        start_dow = EnumeratedListOption(_("First day of week"), 1)
        for count in range(1, 8):
            start_dow.add_item(count, GrampsLocale.long_days[count].capitalize()) 
        start_dow.set_help(_("Select the first day of the week for the calendar"))
        menu.add_option(category_name, "start_dow", start_dow)

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

    def __multiyear_changed(self):
        """
        Handles the ability to print multiple year calendars or not?
        """

        self.__start_year.set_available(True)
        if self.__multiyear.get_value():
            self.__end_year.set_available(True)
        else:
            self.__end_year.set_available(False)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class Element:
    """ A parsed XML element """
    def __init__(self, name, attributes):
        'Element constructor'
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []

    def addChild(self, element):
        'Add a reference to a child element'
        self.children.append(element)

    def getAttribute(self, key):
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

    def StartElement(self, name, attributes):
        'SAX start element even handler'
        # Instantiate an Element object
        element = Element(name.encode(), attributes)
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.addChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)

    def EndElement(self, name):
        'SAX end element event handler'
        self.nodeStack = self.nodeStack[:-1]

    def CharacterData(self, data):
        'SAX character data event handler'
        if data.strip():
            data = data.encode()
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self, filename):
        # Create a SAX parser
        Parser = expat.ParserCreate()
        # SAX event handlers
        Parser.StartElementHandler = self.StartElement
        Parser.EndElementHandler = self.EndElement
        Parser.CharacterDataHandler = self.CharacterData
        # Parse the XML File
        ParserStatus = Parser.Parse(open(filename, 'r').read(), 1)
        return self.root

class Holidays:
    """ Class used to read XML holidays to add to calendar. """
    def __init__(self, elements, country="US"):
        self.debug = 0
        self.elements = elements
        self.country = country
        self.dates = []
        self.initialize()

    def set_country(self, country):
        self.country = country
        self.dates = []
        self.initialize()

    def initialize(self):
        # parse the date objects
        for country_set in self.elements.children:
            if country_set.name == "country" and country_set.attributes["name"] == self.country:
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
        if self.debug:
            print "%s's in %d %d..." % (dayname, m, y)
        retval = [0]
        dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(dayname)
        for d in range(1, 32):
            try:
                date = datetime.date(y, m, d)
            except ValueError:
                continue
            if date.weekday() == dow:
                retval.append( d )
        if self.debug:
            print "dow=", dow, "days=", retval
        return retval

    def check_date(self, date):
        retval = []
        for rule in self.dates:
            if self.debug:
                print "Checking ", rule["name"], "..."
            offset = 0
            if rule["offset"] != "":
                if rule["offset"].isdigit():
                    offset = int(rule["offset"])
                elif rule["offset"][0] in ["-", "+"] and rule["offset"][1:].isdigit():
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
                if self.debug:
                    print "num =", num
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
            if self.debug:
                print ndate, offset, type(offset)
            if isinstance(offset, int):
                if offset != 0:
                    ndate = ndate.fromordinal(ndate.toordinal() + offset)
            elif isinstance(offset, basestring):
                dir_ = 1
                if offset[0] == "-":
                    dir_ = -1
                    offset = offset[1:]
                if offset in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    # next tuesday you come to, including this one
                    dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(offset)
                    ord_ = ndate.toordinal()
                    while ndate.fromordinal(ord_).weekday() != dow:
                        ord_ += dir_
                    ndate = ndate.fromordinal(ord_)
            if self.debug:
                print "ndate:", ndate, "date:", date
            if ndate == date:
                if rule["if"] != "":
                    if not eval(rule["if"]):
                        continue
                retval.append(rule["name"])
        return retval

def _get_countries_from_holiday_file(filename):
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
    for dir_ in locations:
        holiday_full_path = os.path.join(dir_, holiday_file)
        if os.path.exists(holiday_full_path):
            cs = _get_countries_from_holiday_file(holiday_full_path)
            for c in cs:
                if c not in country_list:
                    country_list.append(c)
    country_list.sort()
    country_list.insert(0, _("Don't include holidays"))
    return country_list

# TODO: Only load this once the first time it is actually needed so Gramps
# doesn't take so long to start up.
_COUNTRIES = _get_countries()

# code snippets for Easter and Daylight saving start/ stop
# are borrowed from Calendar.py
def _easter(year):
    """
    Computes the year/month/day of easter. Based on work by
    J.-M. Oudin (1940) and is reprinted in the "Explanatory Supplement
    to the Astronomical Almanac", ed. P. K.  Seidelmann (1992).  Note:
    Ash Wednesday is 46 days before Easter Sunday.
    """
    c = year / 100
    n = year - 19 * (year / 19)
    k = (c - 17) / 25
    i = c - c / 4 - (c - k) / 3 + 19 * n + 15
    i = i - 30 * (i / 30)
    i = i - (i / 28) * (1 - (i / 28) * (29 / (i + 1)) * ((21 - n) / 11))
    j = year + year / 4 + i + 2 - c + c / 4
    j = j - 7 * (j / 7)
    l = i - j
    month = 3 + (l + 40) / 44
    day = l + 28 - 31 * (month / 4)
    date = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
    return date

def _get_dst_start_stop(year, area="us"):
    """
    Return Daylight Saving Time start/stop in a given area ("us", "eu").
    US calculation valid 1976-2099; EU 1996-2099
    """
    if area == "us":
        if year > 2006:
            month = 3                                            # March  
            day = (14 - (math.floor(1 + year * 5 / 4) % 7))
            start = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
            month = 11                                           # November
            day = (7 - (math.floor(1 + year * 5 / 4) % 7))
            stop = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
        else:
            month = 4                                            # April
            day = (2 + 6 * year - math.floor(year / 4) % 7 + 1)
            start = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
            month =  10                                          # October  
            day = (31 - (math.floor(year * 5 / 4) + 1) % 7)
            stop = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
    elif area == "eu":
        month = 3                                                # March
        day = (31 - (math.floor(year * 5 / 4) + 4) % 7)
        start = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
        month = 10                                               # October
        day = (31 - (math.floor(year * 5 / 4) + 1) % 7)
        stop = time.strptime('%d/%d/%d' % (year, month, day), '%Y/%m/%d')
    return start, stop

def _get_regular_surname(sex, name):
    """
    Return a name string built from the components of the Name instance.
    """
    surname = name.get_surname()
    prefix = name.get_surname_prefix()
    if prefix:
        surname = prefix + " " + surname
    if sex == gen.lib.Person.FEMALE:
        pass
    else: 
        suffix = name.get_suffix()
        if suffix:
            surname = surname + ", " + suffix
    return surname

def _get_short_name(person, maiden_name=None):
    """ Return person's name, unless maiden_name given, unless married_name listed. """
    # Get all of a person's names:
    primary_name = person.get_primary_name()
    sex = person.get_gender()

    married_name = None
    names = [primary_name] + person.get_alternate_names()
    for n in names:
        if int(n.get_type()) == gen.lib.NameType.MARRIED:
            married_name = n

    # Now, decide which to use:
    if maiden_name is not None:
        if married_name is not None:
            first_name, family_name = married_name.get_first_name(), _get_regular_surname(sex, married_name)
            call_name = married_name.get_call_name()
        else:
            first_name, family_name = primary_name.get_first_name(), maiden_name
            call_name = primary_name.get_call_name()
    else:
        first_name, family_name = primary_name.get_first_name(), _get_regular_surname(sex, primary_name)
        call_name = primary_name.get_call_name()

    # If they have a nickname use it
    if call_name is not None and call_name.strip() != "":
        first_name = call_name.strip()
    else: # else just get the first name:
        first_name = first_name.strip()
        if " " in first_name:
            first_name, rest = first_name.split(" ", 1) # just one split max
    return ("%s %s" % (first_name, family_name)).strip()

def _get_marrital_status(family, db):
    """
    Returns the marital status of two people, a couple

    are_married will either be the marriage event or None if not married anymore
    """

    are_married = None
    for event_ref in family.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        if event.type in [gen.lib.EventType.MARRIAGE, 
                          gen.lib.EventType.MARR_ALT]:
            are_married = event
        elif event.type in [gen.lib.EventType.DIVORCE, 
                            gen.lib.EventType.ANNULMENT, 
                            gen.lib.EventType.DIV_FILING]:
            are_married = None
    return are_married

def _has_webpage_extension(fname):
    for ext in ('.html', '.htm' '.shtml', '.cgi', '.php', '.php3'):
        if fname.endswith(ext):
            return True
    return False

# Simple utility list to convert Gramps day-of-week numbering to calendar.firstweekday numbering
_dow_gramps2iso = [ -1, calendar.SUNDAY, calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY, calendar.THURSDAY, calendar.FRIDAY, calendar.SATURDAY ]

def _gramps2iso(dow):
    """ Convert GRAMPS day of week to ISO day of week """
    # GRAMPS: SUN = 1
    # ISO: MON = 1
    return (dow + 5) % 7 + 1

# define names for long and short month in GrampsLocale
_lng_month = GrampsLocale.long_months
_shrt_month = GrampsLocale.short_months

def _get_long_month_name(month):
    return _lng_month[month]

def _get_short_month_name(month):
    return _shrt_month[month]   

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
    modes = PluginManager.REPORT_MODE_GUI,
    translated_name = _("Web Calendar"),
    status = _("Stable"),
    author_name = "Thom Sturgill",
    author_email = "thsturgill@yahoo.com",
    description = _("Produces web (HTML) calendars."),
    )
