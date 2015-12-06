# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007      Thom Sturgill
# Copyright (C) 2007-2009 Brian G. Matherly
# Copyright (C) 2008-2011 Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2008      Jason Simanek
# Copyright (C) 2010      Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Web Calendar generator.
"""

#------------------------------------------------------------------------
# python modules
#------------------------------------------------------------------------
from functools import partial
import os, codecs, shutil, re, sys
import datetime
import calendar # Python module

#------------------------------------------------------------------------
# Set up logging
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WebPage")

#------------------------------------------------------------------------
# GRAMPS module
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.lib import Date, Name, NameType, Person
from gramps.gen.lib.date import Today
from gramps.gen.const import PROGRAM_NAME, URL_HOMEPAGE, USER_HOME
from gramps.version import VERSION
from gramps.gen.constfunc import win
from gramps.gen.config import config
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.menu import (BooleanOption, NumberOption, StringOption,
                                  EnumeratedListOption, FilterOption,
                                  PersonOption, DestinationOption, NoteOption)
from gramps.gen.utils.config import get_researcher
from gramps.gen.utils.alive import probably_alive
from gramps.gen.datehandler import displayer as date_displayer

from gramps.gen.display.name import displayer as _nd

import gramps.plugins.lib.libholiday as libholiday
from gramps.plugins.lib.libhtml import Html, xml_lang
from gramps.plugins.lib.libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS
from gramps.gui.pluginmanager import GuiPluginManager

from gramps.gen.lib.date import gregorian

# import styled notes from
# src/plugins/lib/libhtmlbackend.py
from gramps.plugins.lib.libhtmlbackend import HtmlBackend
#------------------------------------------------------------------------
# constants
#------------------------------------------------------------------------
# full clear line for proper styling
fullclear = Html("div", class_ = "fullclear", inline = True)

# Web page filename extensions
_WEB_EXT = ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']

# Calendar stylesheet names
_CALENDARSCREEN = 'calendar-screen.css'
_CALENDARPRINT = 'calendar-print.css'

PLUGMAN = GuiPluginManager.get_instance()
CSS = PLUGMAN.process_plugin_data('WEBSTUFF')

#------------------------------------------------------------------------
#
# WebCalReport
#
#------------------------------------------------------------------------
class WebCalReport(Report):
    """
    Create WebCalReport object that produces the report.
    """
    def __init__(self, database, options, user):
        Report.__init__(self, database, options, user)
        self._user = user

        stdoptions.run_private_data_option(self, options.menu)

        # class to do conversion of styled notes to html markup
        self._backend = HtmlBackend()

        self.options = options

        mgobn = lambda name:options.menu.get_option_by_name(name).get_value()

        self.html_dir = mgobn('target')
        self.title_text  = mgobn('title')
        filter_option =  options.menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.name_format = mgobn('name_format')
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

        self.month_notes = [mgobn('note_' + month)
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
        self.today = Today()

        self.warn_dir = True            # Only give warning once.

        self.link_to_narweb = mgobn('link_to_narweb')
        self.narweb_prefix = mgobn('prefix')

        # self.calendar is a dict; key is the month number
        # Each entry in the dict is also a dict; key is the day number.
        # The day dict is a list of things to display for that day.
        # These things are: birthdays and anniversaries
        self.calendar = {}

        calendar.setfirstweekday(dow_gramps2iso[self.start_dow])

    def get_note_format(self, note):
        """
        will get the note from the database, and will return either the 
        styled text or plain note 
        """

        # retrieve the body of the note
        note_text = note.get()
 
        # styled notes
        htmlnotetext = self.styled_note(note.get_styledtext(),
                                                               note.get_format())
        text = htmlnotetext or Html("p", note_text)

        # return text of the note to its callers
        return text

    #################################################
    # Will produce styled notes for WebCal by using:
    # src/plugins/lib/libhtmlbackend.py
    #################################################
    def styled_note(self, styledtext, format):
        """
         styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        """
        text = str(styledtext)

        if not text:
            return ''

        s_tags = styledtext.get_tags()
        #FIXME: following split should be regex to match \n\s*\n instead?
        markuptext = self._backend.add_markup_from_styled(text, s_tags,
                                                         split='\n\n')
        htmllist = Html("div", id="grampsstylednote")
        if format == 1:
            #preformatted, retain whitespace.
            #so use \n\n for paragraph detection
            #FIXME: following split should be regex to match \n\s*\n instead?
            htmllist += Html('pre', indent=None, inline = True)
            for line in markuptext.split('\n\n'):
                htmllist += Html("p")
                for realline in line.split('\n'):
                    htmllist += realline
                    htmllist += Html('br')

        elif format == 0:
            #flowed
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                htmllist += Html("p")
                htmllist += line

        return htmllist

    def copy_file(self, from_fname, to_fname, to_dir = ''):
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
            self._user.warn(
                _("Possible destination error") + "\n" +
                _("You appear to have set your target directory "
                  "to a directory used for data storage. This "
                  "could create problems with file management. "
                  "It is recommended that you consider using "
                  "a different directory to store your generated "
                  "web pages."))
            self.warn_dir = False
        config.set('paths.website-directory',
                   os.path.dirname(self.html_dir) + os.sep)

    def add_day_item(self, text, year, month, day, event):
        """
        adds birthdays, anniversaries, and holidays to their perspective lists

        text -- line to be added
        year, month, day -- date to add the text to 

        event -- one of 'BirthDay', 'Anniversary', or 'Holiday'
        """

        # This may happen for certain "about" dates.
        # Use first day of the month
        if day == 0:
            day = 1

        # determine which dictionary to use???
        if event in ['Birthday', 'Anniversary']:
            month_dict = self.calendar.get(month, {})
        else:
            month_dict = self.holidays.get(month, {})
        day_list = month_dict.get(day, [])

        if month > 0:
            try:
                event_date = Date(year, month, day)
            except ValueError:
                event_date = Date.EMPTY
        else:
            event_date = Date.EMPTY            # Incomplete date....

        day_list.append((text, event, event_date))
        month_dict[day] = day_list

        # determine which dictionary to add it to???
        if event in ['Birthday', 'Anniversary']:
            self.calendar[month] = month_dict
        else:
            self.holidays[month] = month_dict

    def __get_holidays(self, year):

        # _('translation')
        with self._user.progress(_("Web Calendar Report"),
                                  (_('Calculating Holidays for year %04d') % year),
                                  365) as step:

            """ Get the holidays for the specified country and year """
            holiday_table = libholiday.HolidayTable()
            country = holiday_table.get_countries()[self.country]
            holiday_table.load_holidays(year, country)
            for month in range(1, 13):
                for day in range(1, 32):
                    holiday_names = holiday_table.get_holidays(month, day) 
                    for holiday_name in holiday_names:
                        self.add_day_item(holiday_name, year, month, day, 'Holiday')
                    step()

    def copy_calendar_files(self):
        """
        Copies all the necessary stylesheets and images for these calendars
        """
        # Copy the screen stylesheet
        if self.css and self.css != 'No style sheet':
            fname = CSS[self.css]["filename"]
            self.copy_file(fname, _CALENDARSCREEN, "css")

        # copy Navigation Menu Layout if Blue or Visually is being used
        if CSS[self.css]["navigation"]:

            # copy horizontal menus...
            fname = CSS["Horizontal-Menus"]["filename"]
            self.copy_file(fname, "calendar-menus.css", "css")

        # copy print stylesheet
        fname = CSS["Print-Default"]["filename"]
        self.copy_file(fname, _CALENDARPRINT, "css")

        imgs = []

        # Mainz stylesheet graphics
        # will only be used if Mainz is slected as the stylesheet
        imgs += CSS[self.css]["images"]

        # copy copyright image
        # the proper way would be to call "filename", but it is NOT working...
        if 0 < self.copy <= len(_CC):
            imgs += [CSS["Copyright"]["filename"]]

        # copy Gramps favicon #2
        imgs += [CSS["favicon2"]["filename"]]

        for from_path in imgs:
            fdir, fname = os.path.split(from_path)
            self.copy_file(from_path, fname, "images")

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

        of = open(fname, 'w', encoding=self.encoding,
                  errors='xmlcharrefreplace')
        return of

    def close_file(self, of):
        """ will close whatever filename is passed to it """
        of.close()

    def write_header(self, nr_up, title, body_id = None, add_print = True):
        """
        This creates the header for the Calendars
        'nr_up' - number of directory levels up, started from current page, to the
                  root of the directory tree (i.e. to self.html_dir).
        title -- to be inserted into page header section
        add_print -- whether to add printer stylesheet or not
            * only webcalendar() and one_day() only!
        """

        # number of subdirectories up to reach root
        subdirs = ['..'] * nr_up

        # Header contants
        xmllang = xml_lang()
        _META1 = 'name ="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=1"'
        _META2 = 'name ="apple-mobile-web-app-capable" content="yes"'
        _META3 = 'name="generator" content="%s %s %s"' % (
                    PROGRAM_NAME, VERSION, URL_HOMEPAGE)
        _META4 = 'name="author" content="%s"' % self.author

        # create additional meta tags
        meta = Html("meta", attr = _META1) + (
                Html("meta", attr = _META2, indent = False),
                Html("meta", attr = _META3, indent =False),
                Html("meta", attr = _META4, indent = False)
        )

        # begin each html page...
        page, head, body = Html.page(title,
                                     self.encoding,
                                     xmllang)

        # add body id tag if not None
        if body_id is not None:
            body.attr = "id = '%(idtag)s'" % { 'idtag' : body_id }

        # GRAMPS favicon
        fname1 = "/".join(subdirs + ["images", "favicon2.ico"])

        # _CALENDARSCREEN stylesheet
        fname2 = "/".join(subdirs + ["css", _CALENDARSCREEN])

        # links for GRAMPS favicon and stylesheets
        links = Html("link", rel = 'shortcut icon', href = fname1, type = "image/x-icon") + (
            Html("link",href = fname2, type = "text/css", media = "screen", rel = "stylesheet", indent = False)
        )

        # add horizontal menu if css == Blue or Visually because there is no menus?
        if CSS[self.css]["navigation"]:
            fname = "/".join(subdirs + ["css", "calendar-menus.css"])
            links.extend( 
                Html("link", href = fname, type = "text/css", media = "screen", rel = "stylesheet", indent = False)
            )

        # add printer stylesheet to webcalendar() and one_day() only
        if add_print:
            fname = "/".join(subdirs + ["css", _CALENDARPRINT])
            links.extend(
                Html("link",href = fname,type = "text/css", media = "print", rel = "stylesheet", indent = False)
            )

        # add meta tags and links to head section
        head += (meta, links)

        # start header section and page title...
        with Html("div", id = "header", role = "Title-n-Navigation") as header:
            header += Html("h1", title, id = "SiteTitle", inline = True)

            # Created for ?
            msg = None
            if self.author and self.email:  
                msg = _('the "WebCal" will be the potential-email Subject|'
                        'Created for %(html_email_author_start)s'
                        'WebCal%(html_email_author_end)s') % {
                            'html_email_author_start' :
                                '<a href="mailto:' + self.email + '?subject=' ,
                            'html_email_author_end' :
                                '">' + self.author + '</a>' }
            elif self.author:
                msg = _('Created for %(author)s') % {'author' : self.author}

            if msg:
                header += Html("p", msg, id = "CreatorInfo")

            body += header 
        return page, body

    def year_navigation(self, nr_up, currentsection):
        """
        This will create the year navigation menu bar for a total of seventeen (17) years

        nr_up = number of directories up to reach root directory
        currentsection = proper styling of this navigation bar
        """

        # limit number of years to eighteen (18) years and only one row of years
        nyears = ((self.end_year - self.start_year) + 1)
        num_years = nyears if 0 < nyears < 19 else 18

        # begin year division and begin unordered list
        with Html("div", id = "subnavigation", role = "subnavigation") as submenu:
            unordered = Html("ul")

            for cal_year in range(self.start_year, (self.start_year + num_years)):
                url = ''

                # begin subdir level
                subdirs = ['..'] * nr_up
                subdirs.append(str(cal_year))

                # each year will link to current month.
                # this will always need an extension added
                full_month_name = date_displayer.long_months[self.today.get_month() ]

                # Note. We use '/' here because it is a URL, not a OS dependent 
                # pathname.
                url = '/'.join(subdirs + [full_month_name]) + self.ext
                hyper = Html("a", str(cal_year), href = url, title = str(cal_year))

                # Figure out if we need <li class="CurrentSection"> or just plain <li>
                check_cs = str(cal_year) == currentsection and 'class = "CurrentSection"' or False
                if check_cs:
                    unordered.extend(
                        Html("li", hyper, attr = check_cs, inline = True)
                    )
                else:
                    unordered.extend(
                        Html("li", hyper, inline = True)
                    )
            submenu += unordered
        return submenu

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
        if self.home_link:
            navs.append((self.home_link,  _('Home'),  add_home))
        navs.extend((date_displayer.long_months[month],
                     date_displayer.short_months[month], True)
                             for month in range(1, 13) )

        # Add a link for year_glance() if requested
        navs.append(('fullyearlinked', _('Year Glance'), self.fullyear))

        # remove menu items if they are not True
        navs = [(u, n) for u, n, c in navs if c]

        # begin month subnavigation
        with Html("div", class_ = "wrapper", id = "nav", role = "navigation") as navigation:
            with Html("div", class_ = "container") as container:

                unordered = Html("ul", class_ = "menu")

                for url_fname, nav_text in navs:

                    # Note. We use '/' here because it is a URL, not a OS dependent pathname
                    # need to leave home link alone, so look for it ...
                    url = url_fname
                    add_subdirs = True
                    if not (url.startswith('http:') or url.startswith('/')):
                        add_subdirs = not any(url.endswith(ext)
                                                for ext in _WEB_EXT)
                         
                    # whether to add subdirs or not???
                    if add_subdirs: 
                        subdirs = ['..'] * nr_up
                        subdirs.append(str(year)) 
                        url = '/'.join(subdirs + [url_fname])

                    if not _has_webpage_extension(url):
                        url += self.ext

                    # Figure out if we need <li class="CurrentSection"> or just plain <li>
                    check_cs = url_fname == currentsection and 'class = "CurrentSection"' or False

                    if url == self.home_link:
                        myTitle = _("NarrativeWeb Home")
                    elif url_fname == 'fullyearlinked':
                        myTitle = _('Full year at a Glance')
                    else:
                        myTitle = _(url_fname)
                    hyper = Html("a", nav_text, href = url, name = url_fname, title = myTitle)

                    if check_cs:
                        unordered.extend(
                            Html("li", hyper, attr = check_cs, inline = True)
                        )
                    else:
                        unordered.extend(
                            Html("li", hyper, inline = True)
                        )
                container += unordered
            navigation += container
        return navigation

    def calendar_build(self, cal, year, month, clickable=False):
        """
        This does the work of building the calendar

        @param: cal - either "yg" year_glance(), or "wc" webcalendar()
        @param: year -- year being created
        @param: month - month number 1, 2, .., 12
        """

        # define names for long and short month names
        full_month_name = date_displayer.long_months[month]
        abbr_month_name = date_displayer.short_months[month]

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

        # Note. gen.datehandler has sunday => 1, monday => 2, etc
        # We slice out the first empty element.
        day_names = date_displayer.long_days # use self._ldd.long_days when set_locale is used ...

        def __get_previous_month_day(year, month, day_col):

            if month == 1:
                prevmonth = calendar.monthcalendar((year - 1), 12)
            else:
                prevmonth = calendar.monthcalendar(year, (month - 1))
            num_weeks = len(prevmonth)
            lastweek_prevmonth = prevmonth[(num_weeks - 1)]
            previous_month_day = lastweek_prevmonth[day_col]

            # return previous month day number based on day_col
            # day_col is based on range(0 - 6)
            return previous_month_day

        def __get_next_month_day(year, month, day_col):  

            if month == 12:
                nextmonth = calendar.monthcalendar((year + 1), 1)
            else:
                nextmonth = calendar.monthcalendar(year, (month + 1))
            firstweek_nextmonth = nextmonth[0]
            next_month_day = firstweek_nextmonth[day_col]

            # return next month day number based on day_col
            # day_col is based on range(0 - 6)
            return next_month_day

        # Begin calendar head. We'll use the capitalized name, because here it 
        # seems appropriate for most countries.
        month_name = full_month_name.capitalize()
        th_txt = month_name
        if cal == 'wc': # webcalendar()
            if not self.multiyear:
                th_txt = '%s %04d' % (month_name, year)

        # begin calendar table and table head
        with Html("table", class_ = "calendar", id = month_name, role = "Calendar-Grid") as table:
            thead = Html("thead")
            table += thead 

            if clickable:
                name = th_txt + self.ext
                url = name.lower()
                linkable = Html("a", th_txt, href = url, name = url, title = th_txt)
            else:
                linkable = th_txt
            trow = Html("tr") + (
                Html("th", linkable, class_ ='monthName', colspan=7, inline = True)
                )
            thead += trow    

            # Calendar weekday names header
            trow = Html("tr")
            thead += trow
  
            for day_col in range(7):
                dayclass = get_class_for_daycol(day_col)
                dayname = get_name_for_daycol(day_col)
                trow += Html("th", class_ =dayclass, inline = True) + (
                    Html('abbr', dayname[0], title = dayname) )

            # begin table body
            tbody = Html("tbody")
            table += tbody

            # get first of the month and month information 
            current_date, current_ord, monthinfo = get_first_day_of_month(year, month)

            # begin calendar table rows, starting week0 
            nweeks = len(monthinfo)
            for week_row in range(0, nweeks):
                week = monthinfo[week_row]

                # if you look this up in wikipedia, the first week is called week0
                trow = Html("tr", class_ = "week%02d" % week_row)
                tbody += trow

                # begin calendar day column
                for day_col in range(0, 7):
                    dayclass = get_class_for_daycol(day_col)

                    # day number, can also be a zero -- a day before or after month 
                    day = week[day_col]

                    # start the beginning variable for <td>, table cell
                    tcell_id = "%s%02d" % (abbr_month_name, day)

                    # add calendar date division
                    datediv = Html("div", day, class_ = "date", inline = True)

                    ### a day in the previous or next month ###
                    if day == 0:

                        # day in previous/ next month
                        specday = __get_previous_month_day(year, month, day_col) if week_row == 0 \
                            else __get_next_month_day(year, month, day_col) 

                        specclass = "previous " if week_row == 0 else "next "
                        specclass += dayclass

                        # continue table cell, <td>, without id tag
                        tcell = Html("td", class_ = specclass, inline = True) + (
                            Html("div", specday, class_ = "date", inline = True) )

                    # normal day number in current month
                    else: 
                        thisday = datetime.date.fromordinal(current_ord)

                        # Something this month
                        if thisday.month == month:
                            holiday_list = self.holidays.get(month, {}).get(thisday.day, [])
                            bday_anniv_list = self.calendar.get(month, {}).get(thisday.day, [])

                            # date is an instance because of subtracting abilities in date.py
                            event_date = Date(thisday.year, thisday.month, thisday.day)

                            # get events for this day
                            day_list = get_day_list(event_date, holiday_list, bday_anniv_list) 

                            # is there something this day?
                            if day_list: 

                                hilightday = 'highlight ' + dayclass
                                tcell = Html("td", id = tcell_id, class_ = hilightday)

                                # Year at a Glance
                                if cal == "yg":

                                    # make one day pages and hyperlink 
                                    if self.makeoneday: 

                                        # create yyyymmdd date string for 
                                        # "One Day" calendar page filename
                                        fname_date = '%04d%02d%02d' % (year,month,day) + self.ext

                                        # create hyperlink to one_day()
                                        tcell += Html("a", datediv, href = fname_date, inline = True)

                                        # only year_glance() needs this to create the one_day() pages 
                                        self.one_day(event_date, fname_date, day_list)

                                    # just year_glance(), but no one_day() pages
                                    else:

                                        # continue table cell, <td>, without id tag
                                        tcell = Html("td", class_ = hilightday, inline = True) + (

                                            # adds date division
                                            Html("div", day, class_ = "date", inline = True)
                                            ) 

                                # WebCal
                                else:

                                    # add date to table cell
                                    tcell += datediv 

                                    # list the events
                                    unordered = Html("ul")
                                    tcell += unordered

                                    for nyears, date, text, event in day_list:
                                        unordered += Html("li", text, inline = False 
                                            if event == 'Anniversary' else True)

                            # no events for this day
                            else: 

                                # create empty day with date 
                                tcell = Html("td", class_ = dayclass, inline = True) + (

                                    # adds date division
                                    Html("div", day, class_ = "date", inline = True)
                                    ) 

                        # nothing for this month
                        else:
                            tcell = Html("td", class_ = dayclass) + (

                                # adds date division
                                Html("div", day, class_ = "date", inline = True)
                                ) 

                    # attach table cell to table row
                    # close the day column
                    trow += tcell

                    # change day number
                    current_ord += 1

            if cal == "yg":
                for weeks in range(nweeks, 6):

                    # each calendar must have six weeks for proper styling and alignment
                    with Html("tr", class_ = "week%02d" % (weeks + 1)) as six_weeks:
                        tbody += six_weeks

                        for emptydays in range(7):
                            six_weeks += Html("td", class_ = "emptyDays", inline = True)

        # return calendar table to its callers
        return table

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

        with self._user.progress(_("Web Calendar Report"),
                _('Formatting months ...'), 12) as step:

            for month in range(1, 13):
                cal_fname = date_displayer.long_months[month]
                of = self.create_file(cal_fname, str(year))

                # Add xml, doctype, meta and stylesheets
                # body has already been added to webcal  already once
                webcal, body = self.write_header(nr_up, self.title_text)

                # create Year Navigation menu
                if (self.multiyear and ((self.end_year - self.start_year) > 0)):
                    body += self.year_navigation(nr_up, str(year))

                # Create Month Navigation Menu
                # identify currentsection for proper highlighting
                currentsection = date_displayer.long_months[month]
                body += self.month_navigation(nr_up, year, currentsection, True)

                # build the calendar
                content = Html("div", class_="content", id = "WebCal")
                body += content
                monthly_calendar = self.calendar_build("wc", year, month)
                content += monthly_calendar

                # create note section for webcalendar()
                # One has to be minused because the array starts at zero, but January =1
                note = self.month_notes[month-1].strip()
                if note:
                    note = self.database.get_note_from_gramps_id(note)
                    note = self.get_note_format(note)

                # table foot  section 
                cal_foot = Html("tfoot")
                monthly_calendar += cal_foot

                trow = Html("tr") + (
                    Html("td", note, colspan=7, inline = True)
                    ) 
                cal_foot += trow

                # create blank line for stylesheets
                # create footer division section
                footer = self.write_footer(nr_up)
                body += (fullclear, footer)

                # send calendar page to web output
                # and close the file
                self.XHTMLWriter(webcal, of)

                step()

    def year_glance(self, year):
        """
        This method will create the Full Year At A Glance Page...
        year -- year being created
        """

        nr_up = 1                       # Number of directory levels up to get to root

        # generate progress pass for "Year At A Glance"
        with self._user.progress(_("Web Calendar Report"),
                _('Creating Year At A Glance calendar'), 12) as step:

            of = self.create_file('fullyearlinked', str(year))

            # page title
            title = _("%(year)d, At A Glance") % {'year' : year}

            # Create page header
            # body has already been added to yearglance  already once
            yearglance, body = self.write_header(nr_up, title, "fullyearlinked", False)

            # create Year Navigation menu
            if (self.multiyear and ((self.end_year - self.start_year) > 0)):
                body += self.year_navigation(nr_up, str(year))

            # Create Month Navigation Menu
            # identify currentsection for proper highlighting
            body += self.month_navigation(nr_up, year, "fullyearlinked", True)

            msg = (_('This calendar is meant to give you access '
                           'to all your data at a glance compressed into one page. Clicking '
                           'on a date will take you to a page that shows all the events for '
                           'that date, if there are any.\n'))

            # page description 
            content = Html("div", class_ = "content", id = "YearGlance")
            body += content

            content += Html("p", msg, id='description')

            for month in range(1, 13):

                # build the calendar
                monthly_calendar = self.calendar_build("yg", year, month, clickable=True)
                content += monthly_calendar  

                # increase progress bar
                step()

            # create blank line for stylesheets
            # write footer section
            footer = self.write_footer(nr_up)
            body += (fullclear, footer)

            # send calendar page to web output
            # and close the file
            self.XHTMLWriter(yearglance, of)

    def one_day(self, event_date, fname_date, day_list):
        """
        This method creates the One Day page for "Year At A Glance"

        event_date -- date for the listed events

        fname_date -- filename date from calendar_build()

        day_list - a combination of both dictionaries to be able to create one day
             nyears, date, text, event --- are necessary for figuring the age or years married
             for each year being created...
        """

        nr_up = 1                    # number of directory levels up to get to root

        # get year and month from event_date for use in this section
        year = event_date.get_year()
        month = event_date.get_month()

        od = self.create_file(fname_date, str(year))

        # page title
        title =  _('One Day Within A Year')

        # create page header
        oneday, body = self.write_header(nr_up, title, "OneDay")

        # create Year Navigation menu
        if (self.multiyear and ((self.end_year - self.start_year) > 0)):
            body += self.year_navigation(nr_up, str(year))

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        currentsection = date_displayer.long_months[month]
        body += self.month_navigation(nr_up, year, currentsection, True)

        # set date display as in user prevferences 
        content = Html("div", class_="content", id = "OneDay")
        body += content
        content += Html("h3", date_displayer.display(event_date), inline = True)

        # list the events
        ordered = Html("ol")
        content += ordered  
        for nyears, date, text, event in day_list:
            ordered += Html("li", text, inline = False if event == 'Anniversary' else True)

        # create blank line for stylesheets
        # write footer section
        footer = self.write_footer(nr_up)
        body += (fullclear, footer)

        # send calendar page to web output
        # and close the file 
        self.XHTMLWriter(oneday, od)

    def build_url_fname_html(self, fname, subdir=None, prefix=None):
        return self.build_url_fname(fname, subdir, prefix) + self.ext

    def build_url_fname(self, fname, subdir, prefix = None):
        """
        Create part of the URL given the filename and optionally the subdirectory.
        If the subdirectory is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.
        If 'prefix' is set, then is inserted in front of the result. 

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        Imagine we run gramps on Windows (heaven forbits), we don't want to
        see backslashes in the URL.
        """
        if win():
            fname = fname.replace('\\',"/")
        subdirs = self.build_subdirs(subdir, fname)
        return (prefix or '') + "/".join(subdirs + [fname])

    def build_subdirs(self, subdir, fname):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.

        For example, this may return ['ppl', '8', '1'] given 'ppl', "aec934857df74d36618"
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())
        return subdirs

    def get_name(self, person, maiden_name = None):
        """ 
        Return person's name, unless maiden_name given, unless married_name 
        listed. 

        person -- person to get short name from
        maiden_name  -- either a woman's maiden name or man's surname
        """
        # Get all of a person's names:
        primary_name = person.primary_name
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == NameType.MARRIED:
                married_name = name
                break

        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = Name(married_name)
            else:
                name = Name(primary_name)
                surname_obj = name.get_primary_surname()
                surname_obj.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        name.set_display_as(self.name_format)
        return _nd.display_name(name)

    def collect_data(self, this_year):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        db = self.database

        people = db.iter_person_handles()
        with self._user.progress(_("Web Calendar Report"),
                                  _('Applying Filter...'), 
                                  db.get_number_of_people()) as step:
            people = self.filter.apply(db, people, step)

        with self._user.progress(_("Web Calendar Report"),
                _("Reading database..."), len(people)) as step:
            for person in map(db.get_person_from_handle, people):
                step()

                family_list = person.get_family_handle_list()
                birth_ref = person.get_birth_ref()
                birth_date = Date.EMPTY
                if birth_ref:
                    birth_event = db.get_event_from_handle(birth_ref.ref)
                    birth_date = birth_event.get_date_object()

                # determine birthday information???
                if (self.birthday and birth_date is not Date.EMPTY and birth_date.is_valid()):
                    birth_date = gregorian(birth_date)

                    year = birth_date.get_year() or this_year
                    month = birth_date.get_month()
                    day = birth_date.get_day()

                    # date to figure if someone is still alive
                    # current year of calendar, month nd day is their birth month and birth day 
                    prob_alive_date = Date(this_year, month, day)

                    # add some things to handle maiden name:
                    father_surname = None # husband, actually
                    if person.gender == Person.FEMALE:

                        # get husband's last name:
                        if self.maiden_name in ['spouse_first', 'spouse_last']: 
                            if family_list:
                                if self.maiden_name == 'spouse_first':
                                    fhandle = family_list[0]
                                else:
                                    fhandle = family_list[-1]
                                fam = db.get_family_from_handle(fhandle)
                                father_handle = fam.get_father_handle()
                                mother_handle = fam.get_mother_handle()
                                if mother_handle == person.handle:
                                    if father_handle:
                                        father = db.get_person_from_handle(father_handle)
                                        if father is not None:
                                            father_surname = _get_regular_surname(person.gender, 
                                                father.get_primary_name())
                    short_name = self.get_name(person, father_surname)
                    alive = probably_alive(person, db, prob_alive_date)
                    if (self.alive and alive) or not self.alive:

                        # add link to NarrativeWeb
                        if self.link_to_narweb:
                            text = str(Html("a", short_name, 
                                        href = self.build_url_fname_html(person.handle, "ppl", 
                                                                       prefix = self.narweb_prefix)))
                        else:
                            text = short_name
                        self.add_day_item(text, year, month, day, 'Birthday')

                # add anniversary if requested
                if self.anniv:
                    for fhandle in family_list:
                        fam = db.get_family_from_handle(fhandle)
                        father_handle = fam.get_father_handle()
                        mother_handle = fam.get_mother_handle()
                        if father_handle == person.handle:
                            spouse_handle = mother_handle
                        else:
                            continue # with next person if this was the marriage event
                        if spouse_handle:
                            spouse = db.get_person_from_handle(spouse_handle)
                            if spouse:
                                spouse_name = self.get_name(spouse)
                                short_name = self.get_name(person)

                            # will return a marriage event or False if not married any longer 
                            marriage_event = get_marriage_event(db, fam)
                            if marriage_event:
                                event_date = marriage_event.get_date_object()
                                if event_date is not Date.EMPTY and event_date.is_valid():
                                    event_date = gregorian(event_date)
                                    year = event_date.get_year()
                                    month = event_date.get_month()
                                    day = event_date.get_day()

                                    # date to figure if someone is still alive
                                    prob_alive_date = Date(this_year, month, day)

                                    if self.link_to_narweb:
                                        spouse_name = str(Html("a", spouse_name,
                                                      href = self.build_url_fname_html(spouse_handle, 'ppl', 
                                                      prefix = self.narweb_prefix)))
                                        short_name = str(Html("a", short_name,
                                                          href = self.build_url_fname_html(person.handle, 'ppl', 
                                                           prefix = self.narweb_prefix)))
                                    
                                    alive1 = probably_alive(person, db, prob_alive_date)
                                    alive2 = probably_alive(spouse, db, prob_alive_date)
                                    if ((self.alive and alive1 and alive2) or not self.alive):

                                        text = _('%(spouse)s and %(person)s') % {
                                            'spouse' : spouse_name,
                                            'person' : short_name}

                                        self.add_day_item(text, year, month, day, 'Anniversary')
        
    def write_footer(self, nr_up):
        """
        Writes the footer section of the pages
        'nr_up' - number of directory levels up, started from current page, to the
        root of the directory tree (i.e. to self.html_dir).
        """

        # begin calendar footer
        with Html("div", id = "footer", role = "Footer-End") as footer:

            # Display date as user set in preferences
            msg = _('Generated by %(gramps_home_html_start)s'
                    'Gramps%(html_end)s on %(date)s') % {
                        'gramps_home_html_start' :
                            '<a href="' + URL_HOMEPAGE + '">' ,
                        'html_end' : '</a>' ,
                        'date' : date_displayer.display(Today()) }
            footer += Html("p", msg, id = 'createdate')

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

            footer += Html("p", text, id = 'copyright') 

        # return footer to its callers
        return footer

    def XHTMLWriter(self, page, of):
        """
        This function is simply to make the web page look pretty and readable
        It is not for the browser, but for us, humans
        """

        # writes the file out from the page variable; Html instance
        # This didn't work for some reason, but it does in NarWeb:
        #page.write(partial(print, file=of.write))
        page.write(lambda line: of.write(line + '\n'))
        # close the file now...
        self.close_file(of)

    def write_report(self):
        """
        The short method that runs through each month and creates a page. 
        """
        # get data from database for birthdays/ anniversaries
        self.collect_data(self.start_year)

        # Copy all files for the calendars being created
        self.copy_calendar_files()

        if self.multiyear:

            # limit number of years to eighteen (18) years and only one row of years
            nyears = ((self.end_year - self.start_year) + 1)
            num_years = nyears if 0 < nyears < 19 else 18

            for cal_year in range(self.start_year, (self.start_year + num_years)):

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

# ---------------------------------------------------------------------------------------
#                             WebCalOptions; Creates the Menu
#----------------------------------------------------------------------------------------
class WebCalOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        self.__links = None
        self.__prefix = None
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

        dbname = self.__db.get_dbname()
        default_dir = dbname + "_WEBCAL"
        target = DestinationOption( _("Destination"),
                        os.path.join(config.get('paths.website-directory'),
                                     default_dir))
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

        # We must figure out the value of the first option before we can
        # create the EnumeratedListOption
        fmt_list = _nd.get_name_format()
        defaultnum = _nd.get_default_format()
        default = 0
        for ind,val in enumerate(fmt_list):
            if val[0] == defaultnum:
                default =  ind
                break
        name_format = EnumeratedListOption(_("Name format"), 
                            fmt_list[default][0])
        for num, name, fmt_str, act in fmt_list:
            name_format.add_item(num, name)
        name_format.set_help(_("Select the format to display names"))
        menu.add_option(category_name, "name_format", name_format)

        stdoptions.add_private_data_option(menu, category_name, default=False)

        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", alive)

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in _WEB_EXT:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        css_list = sorted([(CSS[key]["translation"], CSS[key]["id"]) 
                            for key in list(CSS.keys())
                            if CSS[key]["user"]])
        css = EnumeratedListOption(_('StyleSheet'), css_list[0][1])
        for css_item in css_list:                              
            css.add_item(css_item[1], css_item[0])
        css.set_help( _('The stylesheet to be used for the web pages'))
        menu.add_option(category_name, "css", css)

    def __add_content_options(self, menu):
        """
        Options on the "Content Options" tab.
        """
        category_name = _("Content Options")

        # set to today's date for use in menu, etc.
        today = Today()

        self.__multiyear = BooleanOption(_('Create multiple year calendars'), False)
        self.__multiyear.set_help(_('Whether to create Multiple year calendars or not.'))
        menu.add_option(category_name, 'multiyear', self.__multiyear)
        self.__multiyear.connect('value-changed', self.__multiyear_changed) 

        self.__start_year = NumberOption(_('Start Year for the Calendar(s)'), today.get_year(),
            1900, 3000)
        self.__start_year.set_help(_('Enter the starting year for the calendars '
                                     'between 1900 - 3000'))
        menu.add_option(category_name, 'start_year', self.__start_year)

        self.__end_year = NumberOption(_('End Year for the Calendar(s)'), today.get_year(),
             1900, 3000)
        self.__end_year.set_help(_('Enter the ending year for the calendars '
                                   'between 1900 - 3000.'))
        menu.add_option(category_name, 'end_year', self.__end_year)

        self.__multiyear_changed()

        country = EnumeratedListOption(_('Country for holidays'), 0 )
        holiday_table = libholiday.HolidayTable()
        countries = holiday_table.get_countries()
        countries.sort()
        if (len(countries) == 0 or 
            (len(countries) > 0 and countries[0] != '')):
            countries.insert(0, '')
        count = 0
        for c in countries:
            country.add_item(count, c)
            count += 1
        country.set_help(_("Holidays will be included for the selected "
                            "country"))
        menu.add_option(category_name, "country", country)

        # Default selection ????
        start_dow = EnumeratedListOption(_("First day of week"), 1)
        for count in range(1, 8):
            start_dow.add_item(count,
                               date_displayer.long_days[count].capitalize()) 
        start_dow.set_help(_("Select the first day of the week for the calendar"))
        menu.add_option(category_name, "start_dow", start_dow)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item('spouse_first', _("Wives use husband's surname "
                             "(from first family listed)"))
        maiden_name.add_item('spouse_last', _("Wives use husband's surname "
                             "(from last family listed)"))
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)

        dbname = self.__db.get_dbname()
        default_link = '../../' + dbname + "_NAVWEB/index.html"
        home_link = StringOption(_('Home link'), default_link)
        home_link.set_help(_("The link to be included to direct the user to "
                         "the main page of the web site"))
        menu.add_option(category_name, "home_link", home_link)

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

        note_jan = NoteOption(_('January Note'))
        note_jan.set_help(_("The note for the month of January"))
        menu.add_option(category_name, "note_jan", note_jan)

        note_feb = NoteOption(_('February Note'))
        note_feb.set_help(_("The note for the month of February"))
        menu.add_option(category_name, "note_feb", note_feb)

        note_mar = NoteOption(_('March Note'))
        note_mar.set_help(_("The note for the month of March"))
        menu.add_option(category_name, "note_mar", note_mar)

        note_apr = NoteOption(_('April Note'))
        note_apr.set_help(_("The note for the month of April"))
        menu.add_option(category_name, "note_apr", note_apr)

        note_may = NoteOption(_('May Note'))
        note_may.set_help(_("The note for the month of May"))
        menu.add_option(category_name, "note_may", note_may)

        note_jun = NoteOption(_('June Note'))
        note_jun.set_help(_("The note for the month of June"))
        menu.add_option(category_name, "note_jun", note_jun)

        category_name = _("Jul - Dec Notes")

        note_jul = NoteOption(_('July Note'))
        note_jul.set_help(_("The note for the month of July"))
        menu.add_option(category_name, "note_jul", note_jul)

        note_aug = NoteOption(_('August Note'))
        note_aug.set_help(_("The note for the month of August"))
        menu.add_option(category_name, "note_aug", note_aug)

        note_sep = NoteOption(_('September Note'))
        note_sep.set_help(_("The note for the month of September"))
        menu.add_option(category_name, "note_sep", note_sep)

        note_oct = NoteOption(_('October Note'))
        note_oct.set_help(_("The note for the month of October"))
        menu.add_option(category_name, "note_oct", note_oct)

        note_nov = NoteOption(_('November Note'))
        note_nov.set_help(_("The note for the month of November"))
        menu.add_option(category_name, "note_nov", note_nov)

        note_dec = NoteOption(_('December Note'))
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
                                     ' Year At A Glance calendar'), False)
        makeoneday.set_help(_('Whether to create one day pages or not'))
        menu.add_option(category_name, 'makeoneday', makeoneday)  

        self.__links = BooleanOption(_('Link to Narrated Web Report'), False)
        self.__links.set_help(_('Whether to link data to web report or not'))
        menu.add_option(category_name, 'link_to_narweb', self.__links)  
        self.__links.connect('value-changed', self.__links_changed)

        dbname = self.__db.get_dbname()
        default_prefix = '../../' + dbname + "_NAVWEB/"
        self.__prefix = StringOption(_('Link prefix'), default_prefix)
        self.__prefix.set_help(_("A Prefix on the links to take you to "
                                 "Narrated Web Report"))
        menu.add_option(category_name, "prefix", self.__prefix)

        self.__links_changed()

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
        if 1 <= filter_value <= 4:
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

    def __links_changed(self):
        """
        Handle checkbox change. 
        """
        if self.__links.get_value():
            self.__prefix.set_available(True)
        else:
            self.__prefix.set_available(False)

def _get_regular_surname(sex, name):
    """
    Returns a name string built from the components of the Name instance.
    """
    surname = name.get_surname()
    suffix = name.get_suffix()
    if suffix:
        surname = surname + ", " + suffix
    return surname

# Simple utility list to convert Gramps day-of-week numbering 
# to calendar.firstweekday numbering
dow_gramps2iso = [ -1, calendar.SUNDAY, calendar.MONDAY, calendar.TUESDAY,
                   calendar.WEDNESDAY, calendar.THURSDAY, calendar.FRIDAY,
                   calendar.SATURDAY]

def get_marriage_event(db, family):
    """
    marriage_event will either be the marriage event or False
    """

    marriage_event = False
    for event_ref in family.get_event_ref_list():

        event = db.get_event_from_handle(event_ref.ref)
        if event.type.is_marriage:
            marriage_event = event
        elif event.type.is_divorce:
            continue

    # return the marriage event or False to it caller
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

def _has_webpage_extension(url):
    """
    determine if a filename has an extension or not...

    url = filename to be checked
    """
    return any(url.endswith(ext) for ext in _WEB_EXT)

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
    # birthday/ anniversary on this day
    # Date.EMPTY signifies an incomplete date for an event. See add_day_item()
    bday_anniv_list = [(t, e, d) for t, e, d in bday_anniv_list
                       if d != Date.EMPTY]

    # number of years have to be at least zero
    bday_anniv_list = [(t, e, d) for t, e, d in bday_anniv_list
                       if (event_date.get_year() - d.get_year()) >= 0]

    # a holiday
    # zero will force holidays to be first in list
    nyears = 0

    for text, event, date in holiday_list:
        day_list.append((nyears, date, text, event))

    # birthday and anniversary list
    for text, event, date in bday_anniv_list:

        # number of years married, ex: 10
        nyears = (event_date.get_year() - date.get_year())

        # number of years for birthday, ex: 10 years
        age_str = event_date - date
        age_str.format(precision = 1, as_age=False)

        # a birthday
        if event == 'Birthday':

            txt_str = (text + ', <em>'
               # TRANSLATORS: expands to smth like "12 years old",
               # where "12 years" is already localized to your language
            + (_('%s old') % str(age_str) 
                if nyears else _('birth'))
            + '</em>')

        # an anniversary
        elif event == "Anniversary":

            if nyears == 0:
                txt_str = _('%(couple)s, <em>wedding</em>') % {
                            'couple' : text}
            else: 
                years_str = '<em>%s</em>' % nyears
                # translators: leave all/any {...} untranslated
                txt_str = ngettext("{couple}, {years} year anniversary",
                                   "{couple}, {years} year anniversary",
                                   nyears).format(couple=text, years=years_str)
            txt_str = Html('span', txt_str, class_ = "yearsmarried")

        day_list.append((nyears, date, txt_str, event))

    # sort them based on number of years
    # holidays will always be on top of event list
    day_list= sorted(day_list, key=lambda x: (isinstance(x[0], str), x[0]))
 
    # return to its caller calendar_build()
    return day_list
