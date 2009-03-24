#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007          Thom Sturgill
# Copyright (C) 2007-2009 Brian G. Matherly
# Copyright (C) 2008-2009 Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2008          Jason Simanek
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

# $Id: WebCal.py 12238 2009-03-07 09:51:27Z s_charette $

"""
Web Calendar generator.

Refactoring. This is an ongoing job until this plugin is in a better shape.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os, codecs, shutil
import time, datetime, calendar
from gettext import gettext as _
from gettext import ngettext

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
from QuestionDialog import WarningDialog
from Utils import probably_alive
from DateHandler import displayer as _dd
from DateHandler import parser as _dp

import libholiday
from libhtml import Html, newpage

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
# Web page filename extensions
_WEB_EXT = ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']

# Calendar stylesheet names
_CALENDARSCREEN = 'calendar-screen.css'
_CALENDARPRINT = 'calendar-print.css'

# Mainz stylesheet graphics
# will only be used if Mainz is slected as the stylesheet
_WEBBKGD = "Web_Mainz_Bkgd.png"
_WEBHEADER = "Web_Mainz_Header.png"
_WEBMID = "Web_Mainz_Mid.png"
_WEBMIDLIGHT = "Web_Mainz_MidLight.png"

# This information defines the list of styles in the Web calendar
# options dialog as well as the location of the corresponding
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
    # As seen on the internet, ISO-xxx are listed as capital letters
    [_('Unicode UTF-8 (recommended)'), 'UTF-8'],
    ['ISO-8859-1',  'ISO-8859-1' ],
    ['ISO-8859-2',  'ISO-8859-2' ],
    ['ISO-8859-3',  'ISO-8859-3' ],
    ['ISO-8859-4',  'ISO-8859-4' ],
    ['ISO-8859-5',  'ISO-8859-5' ],
    ['ISO-8859-6',  'ISO-8859-6' ],
    ['ISO-8859-7',  'ISO-8859-7' ],
    ['ISO-8859-8',  'ISO-8859-8' ],
    ['ISO-8859-9',  'ISO-8859-9' ],
    ['ISO-8859-10', 'ISO-8859-10' ],
    ['ISO-8859-13', 'ISO-8859-13' ],
    ['ISO-8859-14', 'ISO-8859-14' ],
    ['ISO-8859-15', 'ISO-8859-15' ],
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
        mgobn = lambda name:options.menu.get_option_by_name(name).get_value()

        self.database = database
        self.options = options

        self.html_dir = mgobn('target')
        self.title_text  = mgobn('title')
        filter_option =  options.menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.ext = mgobn('ext')
        self.copy = mgobn('cright')
        self.css = mgobn('css')

        self.country = mgobn('country')
        self.start_dow = mgobn('start_dow')

        self.multiyear = mgobn('multiyear')

        self.start_year = mgobn('start_year')
        self.end_year = mgobn('end_year')

        self.maiden_name = mgobn('maiden_name')

        self.alive = mgobn('alive')
        self.birthday = mgobn('birthdays')
        self.anniv = mgobn('anniversaries')
        self.home_link = mgobn('home_link')

        self.month_notes = [mgobn('note_' + month) \
            for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 
                'aug', 'sep', 'oct', 'nov', 'dec']]

        self.encoding = mgobn('encoding')
        self.fullyear = mgobn('fullyear')
        self.makeoneday = mgobn('makeoneday')

        # identify researcher name and e-mail address
        # as NarrativeWeb already does
        researcher = get_researcher()
        self.author = researcher.name
        if self.author:
            self.author = self.author.replace(',,,', '')
        self.email = researcher.email

        # set to today's date
        today = time.localtime()
        self.today = gen.lib.Date(today[0], today[1], today[2])

        self.warn_dir = True            # Only give warning once.

        # self.calendar is a dict; key is the month number
        # Each entry in the dict is also a dict; key is the day number.
        # The day dict is a list of things to display for that day.
        # These things are: birthdays and anniversaries
        self.calendar = {}

        calendar.setfirstweekday(dow_gramps2iso[self.start_dow])

# ---------------------------------------------------------------------------------------
#
#                        Copy files to their destination
#
# ---------------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------
#
#                         Adds Birthdays and Anniversaries
#
# ---------------------------------------------------------------------------------------

    def add_day_item(self, text, year, month, day, event):
        if day == 0:
            # This may happen for certain "about" dates.
            day = 1     # Use first day of the month
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])

        if month > 0:
            try:
                event_date = gen.lib.Date()
                event_date.set_yr_mon_day(year, month, day)
            except ValueError:
                event_date = '...'
        else:
            event_date = '...'            #Incomplete date as in about, circa, etc.

        day_list.append((text, event, event_date))
        month_dict[day] = day_list
        self.calendar[month] = month_dict

# ---------------------------------------------------------------------------------------
#
# Retrieves Holidays from the Holiday file, src/plugins/lib/holidays.xml
#
# ---------------------------------------------------------------------------------------

    def __get_holidays(self, year):

        self.progress.set_pass(_('Calculating Holidays for year %d' % year), 365)

        """ Get the holidays for the specified country and year """
        holiday_table = libholiday.HolidayTable()
        country = holiday_table.get_countries()[self.country]
        holiday_table.load_holidays(year, country)
        for month in range(1, 13):
            for day in range(1, 32):
                holiday_names = holiday_table.get_holidays(month, day) 
                for holiday_name in holiday_names:
                    self.add_holiday_item(holiday_name, month, day)

                # increment progress bar
                self.progress.step() 

# ---------------------------------------------------------------------------------------
#
#                                 Adds Holiday events
#
# ---------------------------------------------------------------------------------------

    def add_holiday_item(self, text, month, day):
        """
        add holiday to its dictionary 

        text -- holiday title
        month -- month of holiday
        day -- day of holiday
        """

        if day == 0:
            # This may happen for certain "about" dates.
            day = 1     # Use first day of the month
        month_dict = self.holidays.get(month, {})
        day_list = month_dict.get(day, [])

        day_list.append(text)
        month_dict[day] = day_list
        self.holidays[month] = month_dict

# ---------------------------------------------------------------------------------------
#
#          Copies all of the calendar files for all calendars
#
# ---------------------------------------------------------------------------------------

    def copy_calendar_files(self):
        """
        Copies all the necessary stylesheets and images for these calendars
        """
        # Copy the screen stylesheet
        if self.css:
            fname = os.path.join(const.DATA_DIR, self.css)
            self.copy_file(fname, _CALENDARSCREEN, "styles")

        # copy print stylesheet
        fname = os.path.join(const.DATA_DIR, "Web_Print-Default.css")
        self.copy_file(fname, _CALENDARPRINT, "styles")

        # set imgs to empty
        imgs = []

        if self.css == "Web_Mainz.css":
            # Copy Mainz Style Images
            imgs += [_WEBBKGD, _WEBHEADER, _WEBMID, _WEBMIDLIGHT]

        # Copy GRAMPS favicon
        imgs += ['favicon.ico']

        # copy copyright image
        if 0 < self.copy <= len(_CC):
            imgs += ['somerights20.gif']

        for fname in imgs:
            from_path = os.path.join(const.IMAGE_DIR, fname)
            self.copy_file(from_path, fname, "images")

# ---------------------------------------------------------------------------------------
#
#                     Creates file name passed to it
#
# ---------------------------------------------------------------------------------------

    def create_file(self, fname, subdir):
        """
        Create a file in the html_dir tree.
        If the directory does not exist, create it.

        fname -- filename to be created
        subdir -- any subdirs to be added
        """

        fname = os.path.join(self.html_dir, subdir, fname)

        if not _has_webpage_extension(fname):
            fname += self.ext

        destdir = os.path.dirname(fname)

        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        of = codecs.EncodedFile(open(fname, "w"), 'utf-8', self.encoding, 'xmlcharrefreplace')
        return of

# ---------------------------------------------------------------------------------------
#
#                             Closes all file name passed to it
#
# ---------------------------------------------------------------------------------------

    def close_file(self, of):
        """ will close whatever filename is passed to it """
        of.close()

# ---------------------------------------------------------------------------------------
#
#                       Beginning of Calendar Creation
# 
# ---------------------------------------------------------------------------------------

    def write_header(self, nr_up, body_id, title, add_print=True):
        """
        This creates the header for the Calendars
        'nr_up' - number of directory levels up, started from current page, to the
                  root of the directory tree (i.e. to self.html_dir).
        title -- to be inserted into page header section
        add_print -- whether to add printer stylesheet or not
            * only webcalendar() and one_day() only!
        """

        # number of subdirectories up to reach root
        subdirs = '../'*nr_up

        # Header contants
        xmllang = Utils.xml_lang()
        _META1 = 'name="generator" content="%s %s %s"' % (const.PROGRAM_NAME, const.VERSION,
             const.URL_HOMEPAGE)
        _META2 = 'name="author" content="%s"' % self.author

        page, head, body = newpage(title=title, encoding=self.encoding, lang=xmllang)

        # GRAMPS favicon
        fname1 =  '/'.join([subdirs] + ['images'] + ['favicon.ico'])

        # _CALENDARSCREEN stylesheet
        fname2 = '/'.join([subdirs] + ['styles'] + [_CALENDARSCREEN])

        # create additional meta tags
        meta = Html('meta', attr = _META1, indent = True) + (
            Html('meta', attr = _META2)
            )

        # add meta tags to head section
        head += meta

        # links for GRAMPS favicon and stylesheets
        links = Html('link',rel='shortcut icon', href=fname1,type='image/x-icon',indent=True) + (
            Html('link',rel='stylesheet', href=fname2,type='text/css',media='screen')
            )

        # add printer stylesheet to webcalendar() and one_day() only
        if add_print:
            fname = '/'.join([subdirs] + ['styles'] + [_CALENDARPRINT])
            links += Html('link',rel='stylesheet', href=fname,type='text/css',media='print')

        # add stylesheet links to head section
        head += links

        # begin page body
        new_body = Html('body', id = body_id)

        # replace standard body element with custom one
        page.replace(body, new_body)

        # start header division section
        headerdiv = Html('div', id="header", indent=True) + (

            # page title 
            Html('h1', title, id = "SiteTitle", indent=True, inline=True),
            )

        # Created for ?
        if self.author:
            if self.email:  
                msg = _('Created for <a href="mailto:%(email)s?'
                               'subject=WebCal">%(author)s</a>') % {'email'  : self.email,
                                                                                                 'author' : self.author}
            else:
                msg = _('Created for %(author)s') % {'author' : self.author}
            headerdiv += Html('p', msg, id="CreatorInfo", indent=True)

        # add header division to body
        new_body += headerdiv

        # return to its caller
        # either webcalendar(), year_glance(), or one_day()
        return page, new_body

# ---------------------------------------------------------------------------------------
#
#                        Creates year navigation, if multiyear
#
# ---------------------------------------------------------------------------------------

    def year_navigation(self, nr_up, currentsection):
        """
        This will create the year navigation menu bar

        nr_up = number of directories up to reach root directory
        currentsection = proper styling of this navigation bar
        """

        # creating more than one year
        if not self.multiyear:
            return

        num_years = (self.end_year - self.start_year)
        cal_year = self.start_year

        # stylesheets other than "Web_Visually.css" will hold 22 years in a row
        # otherwise, 18 years in a row 
        years_in_row = 22 if self.css is not 'Web_Visually.css' else 18

        # figure out number of rows  
        nrows = get_num_of_rows(num_years, years_in_row)

        for rows in range(0, nrows):
            yearnav = Html('div', id="navigation", indent=True)

            ul = Html('ul', indent=True)
            cols = 1
            while (cols <= years_in_row and cal_year <= self.end_year):
                url = ''

                # begin subdir level
                subdirs = ['..'] * nr_up
                subdirs.append(str(cal_year))

                # each year will link to current month.
                # this will always need an extension added
                full_month_name = get_full_month_name(self.today.get_month())

                # Note. We use '/' here because it is a URL, not a OS dependent 
                # pathname.
                url = '/'.join(subdirs + [full_month_name]) + self.ext

                # Figure out if we need <li class="CurrentSection"> or just plain <li>
                cs = str(cal_year) == currentsection and 'class="CurrentSection"' or ''
                li = Html('li',attr=cs , indent=True, inline=True)

                # create hyperlink
                ahref = Html('a', str(cal_year), href = url, inline=True)

                # add hyperlink to <li> cell
                li += ahref

                # add cell to unordered list
                ul += li

                # increase columns
                cols += 1

                # increase calendar year
                cal_year += 1

        # add ul to yearnav
        yearnav += ul

        # return yearnav to its caller
        return yearnav  

# ---------------------------------------------------------------------------------------
#
#                     Creates month navigation for all Calendars
#
# ---------------------------------------------------------------------------------------

    def month_navigation(self, nr_up, year, currentsection, add_home):
        """
        Will create and display the navigation menu bar

        of = calendar filename being created
        nr_up = number of directories up to reach root directory
        year = year being created
        currentsection = month name being created for proper CSS styling
        use_home = if creating a link to home 
            -- a link to root directory of website
        """

        navs = []

        # An optional link to a home page
        navs.append((self.home_link,  _('Home'),  add_home))

        for month in range(1, 13):
            navs.append((month, month, True))

        # Add a link for year_glance() if requested
        navs.append(('fullyearlinked', _('Year Glance'), self.fullyear))

        monthnav = Html('div', id="subnavigation", indent=True)
        ul = Html('ul', indent=True)

        navs = [(u, n) for u, n, c in navs if c]
        for url_fname, nav_text in navs:
            subdirs = ['..'] * nr_up
            subdirs.append(str(year)) 

            if type(url_fname) == int:
                url_fname = get_full_month_name(url_fname)

            if type(nav_text) == int:
                nav_text = get_short_month_name(nav_text)

            # Note. We use '/' here because it is a URL, not a OS dependent pathname
            # need to leave home link alone, so look for it ...
            url = url_fname
            add_subdirs = True
            if not (url.startswith('http:') or url.startswith('/')):
                for ext in _WEB_EXT:
                    if url_fname.endswith(ext):
                        add_subdirs = False
                         
            # whether to add subdirs or not???
            if add_subdirs: 
                url = '/'.join(subdirs + [url_fname])

            if not _has_webpage_extension(url):
                url += self.ext

            # Figure out if we need <li class="CurrentSection"> or just plain <li>
            cs = url_fname == currentsection and 'class="CurrentSection"' or ''
            li = Html('li', attr = cs, indent=True, inline=True)

            # create hyperlink
            ahref = Html('a', nav_text, href = url)

            # add hyperlink to <li> cell
            li += ahref

            # add <li> to <ul>
            ul += li

        # add ul to monthnav
        monthnav += ul

        # return monthnav to its caller
        return monthnav

# ---------------------------------------------------------------------------------------
#
#                            Creates the Calendar Table
#
# ---------------------------------------------------------------------------------------

    def calendar_build(self, cal, year, month):
        """
        This does the work of building the calendar
        'cal' - one of "yg" year_glance(), or "wc" webcalendar()
        'year' -- year being created
        'month' - month number 1, 2, .., 12
        """

        # define names for long and short month names
        full_month_name = get_full_month_name(month)
        abbr_month_name = get_short_month_name(month)

        # dow (day-of-week) uses Gramps numbering, sunday => 1, etc
        start_dow = self.start_dow
        col2day = [(x-1)%7+1 for x in range(start_dow, start_dow + 7)]

        def get_class_for_daycol(col):
            """ Translate a Gramps day number into a HTMLclass """
            day = col2day[col]
            if day == 1:
                return "weekend sunday"
            elif day == 7:
                return "weekend saturday"
            return "weekday"

        def get_name_for_daycol(col):
            """ Translate a Gramps day number into a HTMLclass """
            day = col2day[col]
            return day_names[day]

        # Note. GrampsLocale has sunday => 1, monday => 2, etc
        # We slice out the first empty element.
        day_names = GrampsLocale.long_days

        # Begin calendar head. We'll use the capitalized name, because here it 
        # seems appropriate for most countries.
        month_name = full_month_name.capitalize()
        th_txt = month_name
        if cal == 'wc': # webcalendar()
            if not self.multiyear:
                th_txt = '%s %d' % (month_name, year)

        # begin calendar table
        cal_table = Html('table', class_='calendar', id = month_name, indent=True)

        # begin table head, <thead>
        thead = Html('thead', indent=True)
        tr = Html('tr', indent=True)
        th = Html('th', th_txt, class_ ='monthName', colspan=7, indent=True, inline=True)

        # add them together now
        tr += th
        thead += tr  

        # Calendar weekday names header
        weekday_names = Html('tr', indent=True)
        for day_col in range(7):
            dayclass = get_class_for_daycol(day_col)
            dayname = get_name_for_daycol(day_col)
            th = Html('th', class_ =dayclass, indent=True, inline=True)
            abbr = Html('abbr', dayname[0], title=dayname)

            # now add it all together
            th += abbr
            weekday_names += th

        # add  weekdays names to table body
        thead += weekday_names

        # add table row to table head
        cal_table += thead  

        # begin table body
        tbody = Html('tbody', indent=True)

        # get first of the month and month information 
        current_date, current_ord, monthinfo = get_first_day_of_month(year, month)

        nweeks = len(monthinfo)
        for week_row in range(0, nweeks):
            week = monthinfo[week_row]

            # if you look this up in wikipedia, the first week is called week0
            tr = Html('tr', class_ = 'week%02d' % week_row, indent=True)

            for day_col in range(0, 7):
                dayclass = get_class_for_daycol(day_col)

                # day number, can also be a zero -- a day before or after month 
                day = week[day_col]

                # start the beginning variable for <td>, table cell
                tdid = "%s%02d" % (abbr_month_name, day)

                # adds date for all pieces of this calendar building
                datediv = Html('div', day, class_ ='date',indent=True,inline=True)

                if day == 0:               # a day in the previous or next month
                    if week_row == 0:      # a day in the previous month
                        specday = get_previous_day(year, month, day_col)
                        specclass = "previous " + dayclass
                    elif week_row == nweeks-1:         # a day in the next month
                        specday = get_next_day(year, month, day_col)   
                        specclass = "next " + dayclass

                    # continue table cell, <td>
                    td = Html('td', class_ = specclass, indent=True,inline=True)

                    # adds date for all pieces of this calendar building
                    datediv = Html('div', specday, class_ = 'date',indent=True,inline=True)

                    # add date to table cell, <td>
                    td += datediv

                    # add table cell, <td>, to table row, <tr> 
                    tr += td

                else:                # normal day number in current month
                    thisday = datetime.date.fromordinal(current_ord)

                    if thisday.month == month: # Something this month
                        holiday_list = self.holidays.get(month, {}).get(thisday.day, [])
                        bday_anniv_list = self.calendar.get(month, {}).get(thisday.day, [])

                        # date is an instance because of subtracting abilities in date.py
                        event_date = gen.lib.Date()
                        event_date.set_yr_mon_day(thisday.year, thisday.month, thisday.day)

                        # get events for this day
                        day_list = get_day_list(event_date, holiday_list, bday_anniv_list) 

                        # is there something this day?
                        if day_list: 

                            hilightday = 'highlight ' + dayclass
                            td = Html('td', id=tdid, class_ = hilightday, indent=True)

                            # Year at a Glance
                            if cal == "yg":

                                # make one day pages and hyperlink 
                                if self.makeoneday: 

                                    # create yyyymmdd date string for 
                                    # "One Day" calendar page filename
                                    fname_date = '%04d%02d%02d' % (year,month,day) + self.ext

                                    # create hyperlink to one_day()
                                    fname_date = full_month_name + '/' + fname_date 
                                    ahref = Html('a', datediv, href=fname_date, indent=True, inline=True)

                                    # add hyperlink to table cell, <td>
                                    td += ahref 

                                    # only year_glance() needs this to create the one_day() pages 
                                    self.one_day(event_date, fname_date, day_list)

                                # just year_glance(), but no one_day() pages
                                else:

                                    # date division section
                                    # show hilighted date, but no hyperlink   
                                    td += datediv

                            # WebCal
                            else:

                                # add date to table cell, <td>
                                td += datediv 

                                # list the events
                                ul = Html('ul', indent=True)
                                for nyears, date, text, event in day_list:
                                    ul += Html('li', text, indent=True, inline=False if event == 'Anniversary' 
                                        else True)

                                # add events to table cell, <td>
                                td += ul

                        # no events for this day
                        else: 

                            # create empty day with date 
                            td = Html('td', id=tdid, class_ = dayclass, indent=True)

                            # add date to table cell, <td>
                            td += datediv

                    # nothing for this month
                    else:
                        td = Html('td', id=tdid, class_ = dayclass, indent=True)

                        # add date to table cell, <td>
                        td += datediv 

                    # add table cell, <td>, to table row, <tr>
                    # close the day column
                    tr += td

                # change day number
                current_ord += 1

            # add table row, <tr>, to table body, <tbody>
            # close the week
            tbody += tr

        if cal == "yg":
            # Fill up till we have 6 rows, so that the months align properly
            for i in range(nweeks, 6):
                six_weeks = Html('tr', class_ = 'week%02d' % (i + 1), indent=True)

                # create table cell, <td>
                td = Html('td', colspan=7, indent=True)

                # add table cell, <td>, to six weeks
                six_weeks += td 

                # add extra weeks to tbody if needed
                tbody += six_weeks

        # close table body
        cal_table += tbody

        # return calendar table to its caller
        return cal_table

# ---------------------------------------------------------------------------------------
#
#   Creates the Web Calendars; the primary part of this plugin
#
# ---------------------------------------------------------------------------------------

    def webcalendar(self, year):
        """
        This method provides information and header/ footer to the calendar month

        year -- year being created
        """

        # do some error correcting if needed
        if self.multiyear:
            if self.end_year < self.start_year:
                self.end_year = self.start_year

        nr_up = 1                   # Number of directory levels up to get to self.html_dir / root

        # generate progress pass for "WebCal"
        self.progress.set_pass(_('Formatting months ...'), 12)

        for month in range(1, 13):

            # Name the file, and create it
            cal_fname = get_full_month_name(month)
            of = self.create_file(cal_fname, str(year))

            # Add xml, doctype, meta and stylesheets
            # body has already been added to webcal  already once
            webcal, body = self.write_header(nr_up, 'WebCal', self.title_text)

            # create Year Navigation menu
            if self.multiyear:
                body += self.year_navigation(nr_up, str(year))

            # Create Month Navigation Menu
            # identify currentsection for proper highlighting
            currentsection = get_full_month_name(month)
            body += self.month_navigation(nr_up, year, currentsection, True)

            # build the calendar
            monthly_calendar = self.calendar_build("wc", year, month)

            # create note section for webcalendar()
            note = self.month_notes[month-1].strip()
            note = note or "&nbsp;"

            # table foot  section 
            cal_note = Html('tfoot', indent=True)
            tr = Html('tr', indent=True)
            td = Html('td', note, colspan=7, indent=True, inline=True)

            # add table cell to table row
            # add table row to table foot section
            tr += td
            cal_note += tr

            # add calendar note to calendar
            monthly_calendar += cal_note

            # add calendar to body
            body += monthly_calendar 

            # create blank line for stylesheets
            body += Html('div', class_ = 'fullclear', indent=True, inline=True)

            # create footer division section
            footer = self.write_footer(nr_up)

            # add footer to WebCal
            body += footer

            # send calendar page to web output
            mywriter(webcal, of)

            # close the file  
            self.close_file(of)

            # increase progress bar
            self.progress.step()

# ---------------------------------------------------------------------------------------
#
#                    Creates Year At A Glance Calendar
#
# ---------------------------------------------------------------------------------------

    def year_glance(self, year):
        """
        This method will create the Full Year At A Glance Page...
        year -- year being created
        """

        nr_up = 1                       # Number of directory levels up to get to root

        # generate progress pass for "Year At A Glance"
        self.progress.set_pass(_('Creating Year At A Glance calendar'), 12)

        # Name the file, and create it
        of = self.create_file('fullyearlinked', str(year))

        # page title
        title = _("%(year)d, At A Glance") % {'year' : year}

        # Create page header
            # body has already been added to yearglance  already once
        yearglance, body = self.write_header(nr_up, 'fullyearlinked', title, False)

        # create Year Navigation menu
        if self.multiyear:
            body += self.year_navigation(nr_up, str(year))

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        body += self.month_navigation(nr_up, year, 'fullyearlinked', False)

        msg = (_('This calendar is meant to give you access '
                       'to all your data at a glance compressed into one page. Clicking '
                       'on a date will take you to a page that shows all the events for '
                       'that date, if there are any!\n'))

        # page description 
        descriptdiv = Html('div', class_ = 'content',indent=True) + (

            # message line
            Html('p', msg, id='description', indent=True)
            )

        # add description to body
        body += descriptdiv

        for month in range(1, 13):

            # build the calendar
            monthly_calendar = self.calendar_build("yg", year, month)

            # add calendar to body
            body += monthly_calendar 

            # increase progress bar
            self.progress.step()

        # create blank line for stylesheets
        body += Html('div', class_ = 'fullclear', indent=True, inline=True)

        # write footer section
        footer = self.write_footer(nr_up)

        # add footer to body
        body += footer

        # send calendar page to web output
        mywriter(yearglance, of)

        # close the file
        self.close_file(of)

# ---------------------------------------------------------------------------------------
#
#               Creates the individual days for year_glance()
#
# ---------------------------------------------------------------------------------------

    def one_day(self, event_date, fname_date, day_list):
        """
        This method creates the One Day page for "Year At A Glance"

        event_date -- date for this file and events

        fname_date -- filename date from calendar_build()

        day_list - a combination of both dictionaries to be able to create one day
             nyears, date, text, event --- are necessary for figuring the age or years married
             for each year being created...
        """

        nr_up = 2                    # number of directory levels up to get to root

        # break up event_date to get year, month, day for this day
        year = event_date.get_year()
        month = event_date.get_month()   

        # Name the file, and create it (see code in calendar_build)
        # chose 'od' as I will be opening and closing more than one file
        # at one time
        od = self.create_file(fname_date, str(year))

        # set date display as in user prevferences 
        pg_date = _dd.display(event_date)

        # page title
        title =  _('One Day Within A Year')

        # create page header
            # body has already been added to oneday  already once
        oneday, body = self.write_header(nr_up, 'OneDay', title)

        # create Year Navigation menu
        if self.multiyear:
            body += self.year_navigation(nr_up, str(year))

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        # connect it back to year_glance() calendar 
        currentsection = 'fullyearlinked'
        body += self.month_navigation(nr_up, year, currentsection, False)

        # page date
        h3 = Html('h3', pg_date, indent=True,inline=True)

        # add <h3> to body, <body>
        body += h3

        # list the events
        ol = Html('ol', indent=True)
        for nyears, date, text, event in day_list:
            ol += Html('li', text, indent=True, inline=False if event == 'Anniversary' 
            else True)

        # add unordered list to body
        body += ol

        # create blank line for stylesheets
        body += Html('div', class_ = 'fullclear', indent=True, inline=True)

        # write footer section
        footer = self.write_footer(nr_up)

        # add footer to WebCal
        body += footer

        # send calendar page to web output
        mywriter(oneday, od)

        # close the file  
        self.close_file(od)

# ---------------------------------------------------------------------------------------
#
#        The database slave; Gathers information for calendars
#
# ---------------------------------------------------------------------------------------

    def collect_data(self, this_year):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        people = self.database.get_person_handles(sort_handles=False)
        self.progress.set_pass(_('Applying Filter...'), len(people))
        people = self.filter.apply(self.database, people, self.progress)

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

            # determine birthday information???
            if (self.birthday and birth_date is not None and birth_date.is_valid()):

                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()

                prob_alive_date = gen.lib.Date(this_year, month, day)

                # add some things to handle maiden name:
                father_surname = None # husband, actually
                sex = person.gender
                if sex == gen.lib.Person.FEMALE:

                    # get husband's last name:
                    if self.maiden_name in ['spouse_first', 'spouse_last']: 
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
                                    if father is not None:
                                        father_name = father.primary_name
                                        father_surname = _get_regular_surname(sex, father_name)
                short_name = _get_short_name(person, father_surname)
                alive = probably_alive(person, self.database, prob_alive_date)
                if (self.alive and alive) or not self.alive:
                    text = _('%(short_name)s') % {'short_name' : short_name}
                    self.add_day_item(text, year, month, day, 'Birthday')

            # add anniversary if requested
            if self.anniv:
                for fhandle in family_list:
                    fam = self.database.get_family_from_handle(fhandle)
                    father_handle = fam.get_father_handle()
                    mother_handle = fam.get_mother_handle()
                    if father_handle == person.handle:
                        spouse_handle = mother_handle
                    else:
                        continue # with next person if this was the marriage event
                    if spouse_handle:
                        spouse = self.database.get_person_from_handle(spouse_handle)
                        if spouse:
                            spouse_name = _get_short_name(spouse)
                            short_name = _get_short_name(person)

                        # will return a marriage event or False if not married any longer 
                        marriage_event = get_marriage_event(self.database, fam)
                        if marriage_event:
                            event_obj = marriage_event.get_date_object()
                            year = event_obj.get_year()
                            month = event_obj.get_month()
                            day = event_obj.get_day()

                            prob_alive_date = gen.lib.Date(this_year, month, day)

                            if event_obj.is_valid():
                                text = _('%(spouse)s and %(person)s') % {
                                         'spouse' : spouse_name,
                                         'person' : short_name}

                                alive1 = probably_alive(person, self.database, prob_alive_date)
                                alive2 = probably_alive(spouse, self.database, prob_alive_date)
                                if ((self.alive and alive1 and alive2) or not self.alive):
                                    self.add_day_item(text, year, month, day, 'Anniversary')

# ---------------------------------------------------------------------------------------
#
#                                Closes the Calendars; the end
#
# ---------------------------------------------------------------------------------------

    def write_footer(self, nr_up):
        """
        Writes the footer section of the pages
        'nr_up' - number of directory levels up, started from current page, to the
        root of the directory tree (i.e. to self.html_dir).
        """

        # begin calendar footer 
        footer = Html('div', id = 'footer', indent=True)

        # Display date as user set in preferences
        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)
        msg = _('Generated by <a href="http://gramps-project.org">'
                      'GRAMPS</a> on %(date)s') % {'date' : value}
        p = Html('p', msg, id = 'createdate', indent=True)

        # add Generated by? to footer
        footer += p

        copy_nr = self.copy
        text = ''
        if copy_nr == 0:
            if self.author:
                text = "&copy; %s %s" % (self.today.get_year(), self.author)
        elif 0 < copy_nr < len(_CC):
            subdirs = ['..'] * nr_up
            # Note. We use '/' here because it is a URL, not a OS dependent pathname
            fname = '/'.join(subdirs + ['images'] + ['somerights20.gif'])
            text = _CC[copy_nr] % {'gif_fname' : fname}
        else:
            text = "&copy; %s %s" % (self.today.get_year(), self.author)

        p = Html('p', text, id = 'copyright', indent=True) 

        # add copyright to footer
        footer += p  

        # return footer to its caller
        return footer

# ---------------------------------------------------------------------------------------
#
#             The work horse of this plugin; stages everything
#
# ---------------------------------------------------------------------------------------

    def write_report(self):
        """
        The short method that runs through each month and creates a page. 
        """

        # Create progress meter bar
        self.progress = Utils.ProgressMeter(_("Web Calendar Report"), '')

        # get data from database for birthdays/ anniversaries
        self.collect_data(self.start_year)

        # Copy all files for the calendars being created
        self.copy_calendar_files()

        if self.multiyear:
            for cal_year in range(self.start_year, (self.end_year + 1)):

                # initialize the holidays dict to fill:
                self.holidays = {}

                # get the information, zero is equal to None
                if self.country != 0:
                    self.__get_holidays(cal_year)

                # create webcalendar() calendar pages
                self.webcalendar(cal_year)

                # create "Year At A Glance" and 
                # "One Day" calendar pages
                if self.fullyear:
                    self.year_glance(cal_year)

        # a single year
        else:
            cal_year = self.start_year

            self.holidays = {}
                
            # get the information, first from holidays:
            if self.country != 0:
                self.__get_holidays(cal_year)

            # create webcalendar() calendar pages
            self.webcalendar(cal_year)

            # create "Year At A Glance" and 
            # "One Day" calendar pages
            if self.fullyear:
                self.year_glance(cal_year)

        # Close the progress meter
        self.progress.close()

# ---------------------------------------------------------------------------------------
#
#                             WebCalOptions; Creates the Menu
#
#----------------------------------------------------------------------------------------
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
        self.__add_advanced_options(menu)

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

        css = EnumeratedListOption(_('StyleSheet'), _CSS_FILES[0][1])
        for style in _CSS_FILES:
            css.add_item(style[1], style[0])
        css.set_help( _('The Style Sheet to be used for the web page'))
        menu.add_option(category_name, "css", css)

    def __add_content_options(self, menu):
        """
        Options on the "Content Options" tab.
        """
        category_name = _("Content Options")

        # set to today's date for use in menu, etc.
        # 0 = year, 1 = month, 2 = day
        today = time.localtime()
        today = datetime.date(today[0], today[1], today[2]) 

        self.__multiyear = BooleanOption(_('Create multiple year '
                                           'calendars'), False)
        self.__multiyear.set_help(_('Whether to create Multiple year '
                                    'calendars or not.'))
        menu.add_option(category_name, 'multiyear', self.__multiyear)
        self.__multiyear.connect('value-changed', self.__multiyear_changed) 

        self.__start_year = NumberOption(_('Start Year for the '
                                           'Calendar(s)'), today.year, 1900, 3000)
        self.__start_year.set_help(_('Enter the starting year for the calendars '
                                     'between 1900 - 3000'))
        menu.add_option(category_name, 'start_year', self.__start_year)

        self.__end_year = NumberOption(_('End Year for the '
                                         'Calendar(s)'), today.year, 1900, 3000)
        self.__end_year.set_help(_('Enter the ending year for the calendars '
                                   'between 1900 - 3000.  if multiple years '
                                   'is selected, then only twenty years at any '
                                   'given time'))
        menu.add_option(category_name, 'end_year', self.__end_year)

        self.__multiyear_changed()

        country = EnumeratedListOption(_('Country for holidays'), 0 )
        holiday_table = libholiday.HolidayTable()
        for index, item in enumerate(holiday_table.get_countries()):
            country.add_item(index, item)
        country.set_help(_("Holidays will be included for the selected "
                            "country"))
        menu.add_option(category_name, "country", country)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item('spouse_first', _("Wives use husband's surname "
                             "(from first family listed)"))
        maiden_name.add_item('spouse_last', _("Wives use husband's surname "
                             "(from last family listed)"))
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

    def __add_advanced_options(self, menu):
        """
        Options for the advanced menu
        """

        category_name = _('Advanced Options')

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1])
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _('The encoding to be used for the web files'))
        menu.add_option(category_name, "encoding", encoding)

        fullyear = BooleanOption(_('Create "Year At A Glance" Calendar'), False)
        fullyear.set_help(_('Whether to create A one-page mini calendar '
                            'with dates highlighted'))
        menu.add_option(category_name, 'fullyear', fullyear)

        makeoneday = BooleanOption(_('Create one day event pages for'
                                                              'Year At A Glance calendar'), False)
        makeoneday.set_help(_('Whether to create one day pages or not'))
        menu.add_option(category_name, 'makeoneday', makeoneday)  

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

# ---------------------------------------------------------------------------------------
#
#              # Web Page Fortmatter and writer                   
#
# ---------------------------------------------------------------------------------------

def mywriter(page, of):
    """
    This function is simply to make the web page look pretty and readable
    It is not for the browser, but for us, humans
    """

    page.write(lambda line: of.write(line + '\n')) 

# ---------------------------------------------------------------------------------------
#
#                        Support Functions for this plugin
#
# ---------------------------------------------------------------------------------------

def _get_regular_surname(sex, name):
    """
    Returns a name string built from the components of the Name instance.
    """

    surname = name.get_surname()
    prefix = name.get_surname_prefix()
    if prefix:
        surname = prefix + " " + surname
    if sex is not gen.lib.Person.FEMALE:
        suffix = name.get_suffix()
        if suffix:
            surname = surname + ", " + suffix
    return surname

def _get_short_name(person, maiden_name=None):
    """ Return person's name, unless maiden_name given, 
    unless married_name listed. """
    # Get all of a person's names:
    primary_name = person.primary_name
    sex = person.gender

    call_name = None
    married_name = None
    names = [primary_name] + person.get_alternate_names()
    for name in names:
        if int(name.get_type()) == gen.lib.NameType.MARRIED:
            married_name = name

    # Now, decide which to use:
    if maiden_name:
        if married_name:
            first_name, family_name = married_name.get_first_name(), _get_regular_surname(sex, married_name)
            call_name = married_name.get_call_name()
        else:
            first_name, family_name = primary_name.get_first_name(), maiden_name
            call_name = primary_name.get_call_name()
    else:
        first_name, family_name = primary_name.get_first_name(), _get_regular_surname(sex, primary_name)
        call_name = primary_name.get_call_name()

    # If they have a nickname, use it?
    if call_name:
        first_name = call_name.strip()
    else: # else just get the first name:
        first_name = first_name.strip()
        if " " in first_name:
            # just one split max 
            first_name, rest = first_name.split(" ", 1)
    return ("%s %s" % (first_name, family_name)).strip()

# Simple utility list to convert Gramps day-of-week numbering 
# to calendar.firstweekday numbering
dow_gramps2iso = [ -1, calendar.SUNDAY, calendar.MONDAY, calendar.TUESDAY,
                   calendar.WEDNESDAY, calendar.THURSDAY, calendar.FRIDAY,
                   calendar.SATURDAY]

# define names for full and abbreviated month names in GrampsLocale
full_month_name = GrampsLocale.long_months
abbr_month_name = GrampsLocale.short_months

def get_full_month_name(month):
    """ returns full or long month name """
    return full_month_name[month]

def get_short_month_name(month):
    """ return short or abbreviated month name """
    return abbr_month_name[month]   

def get_marriage_event(db, family):
    """
    are_married will either be the marriage event or None
    """

    marriage_event = False
    for event_ref in family.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        if event.type in [gen.lib.EventType.MARRIAGE, 
                          gen.lib.EventType.MARR_ALT]:
            marriage_event = event
        elif event.type in [gen.lib.EventType.DIVORCE, 
                            gen.lib.EventType.ANNULMENT, 
                            gen.lib.EventType.DIV_FILING]:
            marriage_event = False
    return marriage_event

def get_first_day_of_month(year, month):
    """
    Compute the first day to display for this month.
    It can also be a day in the previous month.
    """

    # first day of the month
    current_date = datetime.date(year, month, 1)

    # monthinfo is filled using standard Python library 
    # calendar.monthcalendar. It fills a list of 7-day-lists. The first day 
    # of the 7-day-list is determined by calendar.firstweekday.
    monthinfo = calendar.monthcalendar(year, month)

    current_ord = current_date.toordinal() - monthinfo[0].count(0)
    return current_date, current_ord, monthinfo

def get_previous_day(year, month, day_col):
    """
    get last month's last week for previous days in the month
    """

    if month == 1:
        prevmonth = calendar.monthcalendar(year - 1, 12)
    else:
        prevmonth = calendar.monthcalendar(year, month-1)
    num_weeks = len(prevmonth)
    lastweek_prevmonth = prevmonth[num_weeks - 1]
    previous_month_day = lastweek_prevmonth[day_col]
    return previous_month_day

def get_next_day(year, month, day_col):  
    """
    get next month's first week for next days in the month
    """

    if month == 12:
        nextmonth = calendar.monthcalendar(year + 1, 1)
    else:
        nextmonth = calendar.monthcalendar(year, month + 1)
    firstweek_nextmonth = nextmonth[0]
    next_month_day = firstweek_nextmonth[day_col]
    return next_month_day

def _has_webpage_extension(url):
    """
    determine if a filename has an extension or not...

    url = filename to be checked
    """

    for ext in _WEB_EXT:
        if url.endswith(ext):
            return True
    return False

def get_num_of_rows(num_years, years_in_row):
    """
    This will return the number of weeks to be display in
    display_year_navs()
    """
    if num_years > years_in_row:
        rows = 1
        num_years -= years_in_row
    elif 1 <= num_years <= years_in_row:
        return 1
    if num_years > years_in_row:
        rows += 1
        num_years -= years_in_row
    elif 1 <= num_years <= years_in_row:
        rows += 1
        return rows
    if num_years > years_in_row:
        rows += 1
        num_years -= years_in_row
    elif 1 <= num_years <= years_in_row:
        rows += 1
        return rows
    return rows

# ---------------------------------------------------------------------------------------
#
#                   Gets individual events for each day
#
# ---------------------------------------------------------------------------------------

def get_day_list(event_date, holiday_list, bday_anniv_list):
    """
    Will fill day_list and return it to its caller: calendar_build()

    holiday_list -- list of holidays for event_date
    bday_anniv_list -- list of birthdays and anniversaries 
        for event_date

    event_date -- date for this day_list 

    'day_list' - a combination of both dictionaries to be able 
        to create one day nyears, date, text, event --- are 
        necessary for figuring the age or years married for 
        each day being created...
    """

    # initialize day_list
    day_list = []

    ##################################################################
    # holiday on this day
    # The 0 will force holidays to be first in the list
    for event_name in holiday_list:
        for line in event_name.splitlines():
            day_list.append((0, event_date, line, 'Holiday'))
    ##################################################################

    ##################################################################
    # birthday/ anniversary on this day
    # '...' signifies an incomplete date for an event. See add_day_item()
    bday_anniv_list = [(t, e, d) for t, e, d in bday_anniv_list
                       if d != '...']

    # number of years have to be at least zero
    bday_anniv_list = [(t, e, d) for t, e, d in bday_anniv_list
                       if (event_date.get_year() - d.get_year()) >= 0]
    for text, event, date in bday_anniv_list:

        # number of years married, ex: 10
        nyears = event_date.get_year() - date.get_year()

        txt_str = None

        # number of years for birthday, ex: 10 years
        age_str = event_date - date
        age_str.format(precision=1)

        # a birthday
        if event == 'Birthday':

            txt_str = _(text + ', <em>'
            + ('%s old' % str(age_str) if nyears else 'birth')
            + '</em>')

        # an anniversary
        elif event == 'Anniversary':

            if nyears == 0:
                txt_str = _('%(couple)s, <em>wedding</em>') % {
                            'couple' : text}
            else: 
                txt_str = (ngettext('%(couple)s, <em>%(years)d'
                                    '</em> year anniversary',
                                    '%(couple)s, <em>%(years)d'
                                    '</em> year anniversary', nyears)
                           % {'couple' : text, 'years'  : nyears})
            txt_str = '<span class="yearsmarried">%s</span>' % txt_str

        if txt_str is not None:
            day_list.append((nyears, date, txt_str, event))

    # sort them based on number of years
    # holidays will always be on top of day 
    day_list.sort()
 
    return day_list

# ---------------------------------------------------------------------------------------
#
#                                      Register Plugin
#
# ---------------------------------------------------------------------------------------
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
