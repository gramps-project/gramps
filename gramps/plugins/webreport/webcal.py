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
# Copyright (C) 2015-     Serge Noiraud
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
import os
import shutil
import datetime
import time
import calendar # Python module

#------------------------------------------------------------------------
# Set up logging
#------------------------------------------------------------------------
import logging

#------------------------------------------------------------------------
# Gramps module
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Date, Name, NameType, Person
from gramps.gen.lib.date import Today
from gramps.gen.const import PROGRAM_NAME, URL_HOMEPAGE
from gramps.version import VERSION
from gramps.gen.constfunc import win
from gramps.gen.config import config
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.menu import (BooleanOption, NumberOption, StringOption,
                                  EnumeratedListOption, FilterOption,
                                  PersonOption, DestinationOption, NoteOption)
from gramps.gen.utils.config import get_researcher
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import get_death_or_fallback
from gramps.gen.utils.symbols import Symbols
from gramps.gen.datehandler import displayer as _dd

from gramps.gen.display.name import displayer as _nd

import gramps.plugins.lib.libholiday as libholiday
from gramps.plugins.lib.libhtml import Html, xml_lang
from gramps.plugins.lib.libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS
from gramps.gui.pluginmanager import GuiPluginManager
from gramps.plugins.webreport.common import html_escape

from gramps.gen.lib.date import gregorian

# import styled notes from
# src/plugins/lib/libhtmlbackend.py
from gramps.plugins.lib.libhtmlbackend import HtmlBackend
#------------------------------------------------------------------------
# constants
#------------------------------------------------------------------------
_ = glocale.translation.sgettext
_LOG = logging.getLogger(".WebPage")

# full clear line for proper styling

FULLCLEAR = Html("div", class_="fullclear", inline=True)

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

        mgobn = lambda name: options.menu.get_option_by_name(name).get_value()

        self.set_locale(options.menu.get_option_by_name('trans').get_value())
        stdoptions.run_date_format_option(self, options.menu)
        self.rlocale = self._locale
        self._ = self.rlocale.translation.sgettext

        self.html_dir = mgobn('target')
        self.title_text = html_escape(mgobn('title'))
        filter_option = options.menu.get_option_by_name('filter')
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
        self.after_year = mgobn('after_year')
        if not self.multiyear:
            self.end_year = self.start_year
        if self.end_year < self.start_year:
            self.end_year = self.start_year

        self.maiden_name = mgobn('maiden_name')

        self.alive = mgobn('alive')
        self.birthday = mgobn('birthdays')
        self.anniv = mgobn('anniversaries')
        self.death_anniv = mgobn('death_anniv')
        self.event_list = []

        self.month_notes = [mgobn('note_' + month)
                            for month in ['jan', 'feb', 'mar', 'apr', 'may',
                                          'jun', 'jul', 'aug', 'sep', 'oct',
                                          'nov', 'dec']]

        self.encoding = mgobn('encoding')
        self.fullyear = True
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
        self.holidays = {}

        calendar.setfirstweekday(DOW_GRAMPS2ISO[self.start_dow])
        self.head = []
        # An optional link to a home page
        self.head.append((self.narweb_prefix, self._('NarrativeWeb Home'),
                          self.link_to_narweb))

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
    def styled_note(self, styledtext, format_type):
        """
        styledtext : assumed a StyledText object to write
        format_type : = 0 : Flowed, = 1 : Preformatted
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
        if format_type == 1:
            #preformatted, retain whitespace.
            #so use \n\n for paragraph detection
            #FIXME: following split should be regex to match \n\s*\n instead?
            htmllist += Html('pre', indent=None, inline=True)
            for line in markuptext.split('\n\n'):
                htmllist += Html("p")
                for realline in line.split('\n'):
                    htmllist += realline
                    htmllist += Html('br')

        elif format_type == 0:
            #flowed
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                htmllist += Html("p")
                htmllist += line

        return htmllist

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

    def add_day_item(self, text, year, month, day,
                     event, age_at_death, dead_event_date):
        """
        adds birthdays, anniversaries, and holidays to their perspective lists

        text -- line to be added
        year, month, day -- date to add the text to

        event -- one of 'BirthDay', 'Anniversary', 'Death' or 'Holiday'
        age_at_death -- The age in text. ie : 68 years, 6 months
        dead_event_date -- The date of the event used to calculate
                           the age_at_death
        """

        if year <= self.after_year:
            return

        # This may happen for certain "about" dates.
        # Use first day of the month
        if day == 0:
            day = 1

        # determine which dictionary to use???
        if event in ['Birthday', 'Anniversary', 'Death']:
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

        day_list.append((text, event, event_date,
                         age_at_death, dead_event_date))
        month_dict[day] = day_list

        # determine which dictionary to add it to???
        if event in ['Birthday', 'Anniversary', 'Death']:
            self.calendar[month] = month_dict
        else:
            self.holidays[month] = month_dict

    def __get_holidays(self, year):
        """ Get the holidays for the specified country and year """

        # _('translation')
        with self._user.progress(_("Web Calendar Report"),
                                 _('Calculating Holidays for year %04d') % year,
                                 365) as step:

            holiday_table = libholiday.HolidayTable()
            country = holiday_table.get_countries()[self.country]
            holiday_table.load_holidays(year, country)
            for month in range(1, 13):
                for day in range(1, 32):
                    holiday_names = holiday_table.get_holidays(month, day)
                    for holiday_name in holiday_names:
                        self.add_day_item(holiday_name, year, month,
                                          day, 'Holiday', None, None)
                    step()

    def copy_calendar_files(self):
        """
        Copies all the necessary stylesheets and images for these calendars
        """
        imgs = []

        # copy all screen style sheet
        for css_f in CSS:
            already_done = False
            for css_fn in ("UsEr_", "Basic", "Mainz", "Nebraska", "Vis"):
                if css_fn in css_f and not already_done:
                    already_done = True
                    fname = CSS[css_f]["filename"]
                    # add images for this css
                    imgs += CSS[css_f]["images"]
                    css_f = css_f.replace("UsEr_", "")
                    self.copy_file(fname, css_f + ".css", "css")

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
            dummy_fdir, fname = os.path.split(from_path)
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

        output_file = open(fname, 'w', encoding=self.encoding,
                           errors='xmlcharrefreplace')
        return output_file

    def close_file(self, output_file):
        """ will close whatever filename is passed to it """
        output_file.close()

    def write_header(self, nr_up, title, body_id=None, add_print=True):
        """
        This creates the header for the Calendars
        'nr_up' - number of directory levels up, started from current page, to
                  the root of the directory tree (i.e. to self.html_dir).
        title -- to be inserted into page header section
        add_print -- whether to add printer stylesheet or not
            * only webcalendar() and one_day() only!
        """

        # number of subdirectories up to reach root
        subdirs = ['..'] * nr_up

        # Header contants
        xmllang = xml_lang()
        _meta1 = 'name ="viewport" content="width=device-width, '\
                 'initial-scale=1.0, maximum-scale=1.0, user-scalable=1"'
        _meta2 = 'name ="apple-mobile-web-app-capable" content="yes"'
        _meta3 = 'name="generator" content="%s %s %s"' % (
            PROGRAM_NAME, VERSION, URL_HOMEPAGE)
        _meta4 = 'name="author" content="%s"' % self.author

        # create additional meta tags
        meta = Html("meta", attr=_meta1) + (
            Html("meta", attr=_meta2, indent=False),
            Html("meta", attr=_meta3, indent=False),
            Html("meta", attr=_meta4, indent=False)
        )

        # begin each html page...
        page, head, body = Html.page(title,
                                     self.encoding,
                                     xmllang)

        # Add the script to control the menu
        menuscript = Html("<script>function navFunction() { "
                          "var x = document.getElementById(\"dropmenu\"); "
                          "if (x.className === \"nav\") { x.className += \""
                          " responsive\"; } else { x.className = \"nav\"; }"
                          " }</script>")
        head += menuscript

        # begin header section
        headerdiv = Html("div", id='header') + (
            Html("<button href=\"javascript:void(0);\" class=\"navIcon\""
                 " onclick=\"navFunction()\">&#8801;</button>")) + (
                     Html("h1", self.title_text,
                          id="SiteTitle", inline=True))
        body += headerdiv

        # add body id tag if not None
        if body_id is not None:
            body.attr = "id = '%(idtag)s'" % {'idtag' : body_id}

        # Gramps favicon
        fname1 = "/".join(subdirs + ["images", "favicon2.ico"])

        # _CALENDARSCREEN stylesheet
        fname2 = "/".join(subdirs + ["css", _CALENDARSCREEN])

        # links for Gramps favicon and stylesheets
        links = Html("link", rel='shortcut icon',
                     href=fname1, type="image/x-icon") + (
                         Html("link", href=fname2, type="text/css",
                              title=self._("Default"),
                              media="screen", rel="stylesheet", indent=False))
        # create all alternate stylesheets
        # Cannot use it on local files (file://)
        for css_f in CSS:
            already_done = False
            for css_fn in ("UsEr_", "Basic", "Mainz", "Nebraska"):
                if css_fn in css_f and not already_done:
                    css_f = css_f.replace("UsEr_", "")
                    fname = "/".join(subdirs + ["css", css_f + ".css"])
                    links += Html("link", rel="alternate stylesheet",
                                  title=css_f, indent=False,
                                  media="screen", type="text/css",
                                  href=fname)

        # add horizontal menu if css == Blue or Visually because
        # there is no menus?
        if CSS[self.css]["navigation"]:
            fname = "/".join(subdirs + ["css", "calendar-menus.css"])
            links.extend(
                Html("link", href=fname, type="text/css",
                     media="screen", rel="stylesheet", indent=False)
            )

        # add printer stylesheet to webcalendar() and one_day() only
        if add_print:
            fname = "/".join(subdirs + ["css", _CALENDARPRINT])
            links.extend(
                Html("link", href=fname, type="text/css",
                     media="print", rel="stylesheet", indent=False)
            )

        # add meta tags and links to head section
        head += (meta, links)

        # start header section and page title...
        script = """
<script type="text/javascript">
function currentmonth(y) {
var date = new Date();
var month = date.getMonth() + 1;
var url = y + "/" + month + "%s";
window.location.href = url;
return false;
}
</script>
""" % self.ext
        body += script
        return page, body

    def year_navigation(self, nr_up, currentsection):
        """
        This will create the year navigation menu bar for a total of
        seventeen (17) years

        nr_up = number of directories up to reach root directory
        currentsection = proper styling of this navigation bar
        """

        # limit number of years to eighteen (18) years and only one row of years
        nyears = ((self.end_year - self.start_year) + 1)
        num_years = nyears if 0 < nyears < 19 else 18
        self.end_year = (self.start_year + 17) if nyears > 18 else self.end_year

        # begin year division and begin unordered list
        with Html("div", class_="wrappernav",
                  id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:

                unordered = Html("ul", class_="nav", id="dropmenu")

                (url, nav_text, disp) = self.head[0]
                if disp:
                    if url[:1] == '/':
                        url = url + "index" + self.ext
                    else:
                        url_up = ['..'] * nr_up
                        url_up.append(url)
                        url = '/'.join(url_up) + "index" + self.ext
                    hyper = Html("a", nav_text, href=url, name=url,
                                 title=nav_text)
                    unordered.extend(Html("li", hyper, inline=True))

                for cal_year in range(self.start_year,
                                      (self.start_year + num_years)):
                    url = ''

                    # begin subdir level
                    subdirs = ['..'] * nr_up
                    subdirs.append(str(cal_year))

                    # Note. We use '/' here because it is a URL,
                    # not a OS dependent pathname.
                    url = '/'.join(subdirs)
                    onclic = "return currentmonth('" + url + "');"
                    hyper = Html("a", self.rlocale.get_date(Date(cal_year)),
                                 href="#", onclick=onclic, title=str(cal_year))

                    # Figure out if we need <li class="CurrentSection">
                    # or just plain <li>
                    if str(cal_year) == currentsection:
                        check_cs = 'class = "CurrentSection"'
                    else:
                        check_cs = False
                    if check_cs:
                        unordered.extend(
                            Html("li", hyper, attr=check_cs, inline=True)
                        )
                    else:
                        unordered.extend(
                            Html("li", hyper, inline=True)
                        )
                container += unordered
            navigation += container
        return navigation

    def month_navigation(self, nr_up, year, currentsection):
        """
        Will create and display the navigation menu bar

        nr_up = number of directories up to reach root directory
        year = year being created
        currentsection = month name being created for proper CSS styling
        """
        navs = []

        if not self.multiyear:
            (url, nav_text, disp) = self.head[0]
            if url[:1] == '/':
                url = url + "index" + self.ext
            else:
                url = "../" + url + "index" + self.ext
            navs.append((url, nav_text, disp))

        navs.extend((str(month),
                     self.rlocale.date_displayer.short_months[int(month)], True)
                    for month in range(1, 13))

        # Add a link for year_glance() if requested
        navs.append(('fullyearlinked', self._('Full year at a Glance'),
                     self.fullyear))

        # remove menu items if they are not True
        navs = [(u, n) for u, n, c in navs if c]

        # begin month subnavigation
        with Html("div", class_="wrapper",
                  id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:

                unordered = Html("ul", class_="menu")

                for url_fname, nav_text in navs:

                    # Note. We use '/' here because it is a URL, not a OS
                    # dependent pathname need to leave home link alone,
                    # so look for it ...
                    if nav_text != self._("NarrativeWeb Home"):
                        url_fname = url_fname.lower()
                    url = url_fname
                    add_subdirs = False
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

                    # Figure out if we need <li class="CurrentSection"> or
                    # just plain <li>
                    if url_fname == currentsection:
                        check_cs = 'class = "CurrentSection"'
                    else:
                        check_cs = False

                    if url_fname == 'fullyearlinked':
                        mytitle = self._('Full year at a Glance')
                    else:
                        mytitle = self._(url_fname)
                    hyper = Html("a", nav_text, href=url,
                                 name=url_fname, title=mytitle)

                    if check_cs:
                        unordered.extend(
                            Html("li", hyper, attr=check_cs, inline=True)
                        )
                    else:
                        unordered.extend(
                            Html("li", hyper, inline=True)
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

        date_displayer = self.rlocale.date_displayer
        # define names for long and short month names
        full_month_name = date_displayer.long_months[int(month)]
        abbr_month_name = date_displayer.short_months[int(month)]

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
        day_names = date_displayer.long_days # use self._ldd.long_days when
                                             # set_locale is used ...

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
                th_txt = '%s %s' % (month_name,
                                    self._get_date(Date(year))) # localized

        # begin calendar table and table head
        with Html("table", class_="calendar",
                  id=month_name, role="Calendar-Grid") as table:
            thead = Html("thead")
            table += thead

            if clickable:
                name = str(month) + self.ext
                linkable = Html("a", th_txt, href=name, name=name, title=th_txt)
                trow = Html("tr") + (
                    Html("th", linkable, class_='monthName',
                         colspan=7, inline=True)
                    )
                thead += trow
            else:
                if not self.multiyear:
                    self.end_year = self.start_year
                if month > 1:
                    full_month_name = str(month-1)
                    url = full_month_name.lower() + self.ext
                    prevm = Date(int(year), int(month-1), 0)
                    my_title = Html("a", "\u276e", href=url, close=True,
                                    title=date_displayer.display(prevm))
                elif self.multiyear and year > self.start_year:
                    full_month_name = str(12)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(year-1), url)
                    prevm = Date(int(year-1), 12, 0)
                    my_title = Html("a", "\u276e", href=dest, close=True,
                                    title=date_displayer.display(prevm))
                else:
                    full_month_name = str(12)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(self.end_year), url)
                    prevy = Date(self.end_year, 12, 0)
                    my_title = Html("a", "\u276e", href=dest, close=True,
                                    title=date_displayer.display(prevy))
                my_title += Html("</a>&nbsp;" + month_name + "&nbsp;")
                if month < 12:
                    full_month_name = str(month+1)
                    url = full_month_name.lower() + self.ext
                    nextd = Date(int(year), int(month+1), 0)
                    my_title += Html("a", "\u276f", href=url, close=True,
                                     title=date_displayer.display(nextd))
                elif self.multiyear and year < self.end_year:
                    full_month_name = str(1)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(year+1), url)
                    nextd = Date(int(year+1), 1, 0)
                    my_title += Html("a", "\u276f", href=dest, close=True,
                                     title=date_displayer.display(nextd))
                else:
                    full_month_name = str(1)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(self.start_year), url)
                    nexty = Date(self.start_year, 1, 0)
                    my_title += Html("a", "\u276f", href=dest, close=True,
                                     title=date_displayer.display(nexty))
                trow = Html("tr") + (
                    Html("th", my_title, class_='monthName',
                         colspan=7, inline=True)
                    )
                thead += trow
                trow = Html("tr") + (Html("th", "", colspan=7, inline=True))
                thead += trow

            # Calendar weekday names header
            trow = Html("tr")
            thead += trow

            for day_col in range(7):
                dayclass = get_class_for_daycol(day_col)
                dayname = self._(get_name_for_daycol(day_col))
                trow += Html("th", class_=dayclass, inline=True) + (
                    Html('abbr', dayname[0], title=dayname))

            # begin table body
            tbody = Html("tbody")
            table += tbody

            # get first of the month and month information
            (dummy_current_date,
             current_ord, monthinfo) = get_first_day_of_month(year, month)

            # begin calendar table rows, starting week0
            nweeks = len(monthinfo)
            for week_row in range(0, nweeks):
                week = monthinfo[week_row]

                # if you look this up in wikipedia, the first week
                # is called week0
                trow = Html("tr", class_="week%02d" % week_row)
                tbody += trow

                # begin calendar day column
                for day_col in range(0, 7):
                    dayclass = get_class_for_daycol(day_col)

                    # day number, can also be a zero -- a day before or
                    # after month
                    day = week[day_col]

                    # start the beginning variable for <td>, table cell
                    tcell_id = "%s%02d" % (abbr_month_name, day)

                    # add calendar date division
                    datediv = Html("div", day, class_="date", inline=True)
                    clickable = Html("div", datediv, class_="clickable",
                                     inline=True)

                    ### a day in the previous or next month ###
                    if day == 0:

                        # day in previous/ next month
                        specday = __get_previous_month_day(year, month, day_col
                                                          ) if week_row == 0 \
                            else __get_next_month_day(year, month, day_col)

                        specclass = "previous " if week_row == 0 else "next "
                        specclass += dayclass

                        # continue table cell, <td>, without id tag
                        tcell = Html("td", class_=specclass, inline=True) + (
                            Html("div", specday, class_="date", inline=True))

                    # normal day number in current month
                    else:
                        thisday = datetime.date.fromordinal(current_ord)

                        # Something this month
                        if thisday.month == month:
                            holiday_list = self.holidays.get(month,
                                                             {}).get(
                                                                 thisday.day,
                                                                 [])
                            bday_anniv_list = self.calendar.get(month,
                                                                {}).get(
                                                                    thisday.day,
                                                                    [])

                            # date is an instance because of subtracting
                            # abilities in date.py
                            event_date = Date(thisday.year, thisday.month,
                                              thisday.day)

                            # get events for this day
                            day_list = get_day_list(event_date, holiday_list,
                                                    bday_anniv_list,
                                                    rlocale=self.rlocale)

                            # is there something this day?
                            if day_list:

                                hilightday = 'highlight ' + dayclass
                                tcell = Html("td", id=tcell_id,
                                             class_=hilightday)

                                # Year at a Glance
                                if cal == "yg":

                                    # make one day pages and hyperlink
                                    if self.makeoneday:

                                        # create yyyymmdd date string for
                                        # "One Day" calendar page filename
                                        fname_date = '%04d%02d%02d' % (year,
                                                                       month,
                                                                       day)
                                        fname_date += self.ext

                                        # create hyperlink to one_day()
                                        tcell += Html("a", datediv,
                                                      href=fname_date,
                                                      inline=True)

                                        # only year_glance() needs this to
                                        # create the one_day() pages
                                        self.one_day(event_date, fname_date,
                                                     day_list)

                                    # just year_glance(), but no one_day() pages
                                    else:

                                        # continue table cell, <td>,
                                        # without id tag
                                        tcell = Html("td", class_=hilightday,
                                                     inline=True) + (
                                                         # adds date division
                                                         Html("div", day,
                                                              class_="date",
                                                              inline=True))

                                # WebCal
                                else:
                                    # add date to table cell
                                    tcell += clickable

                                    # list the events
                                    unordered = Html("ul")
                                    clickable += unordered

                                    for (dummy_nyears, dummy_date, text,
                                         event, dummy_notused,
                                         dummy_notused) in day_list:
                                        unordered += Html("li", text,
                                                          inline=False
                                                          if (event ==
                                                              'Anniversary')
                                                          else True)
                            # no events for this day
                            else:
                                # adds date division
                                date = Html("div", day, class_="date",
                                            inline=True)
                                # create empty day with date
                                tcell = Html("td", class_=dayclass,
                                             inline=True) + (
                                                 # adds date division
                                                 Html("div", date,
                                                      class_="empty",
                                                      inline=True))
                        # nothing for this month
                        else:
                            tcell = Html("td", class_=dayclass) + (
                                # adds date division
                                Html("div", day, class_="date", inline=True))

                    # attach table cell to table row
                    # close the day column
                    trow += tcell

                    # change day number
                    current_ord += 1

            if cal == "yg":
                for weeks in range(nweeks, 6):

                    # each calendar must have six weeks for proper styling
                    # and alignment
                    with Html("tr",
                              class_="week%02d" % (weeks + 1)) as six_weeks:
                        tbody += six_weeks

                        for dummy_emptydays in range(7):
                            six_weeks += Html("td", class_="emptyDays",
                                              inline=True)

        # return calendar table to its callers
        return table

    def webcalendar(self, year):
        """
        This method provides information and header/ footer
        to the calendar month

        year -- year being created
        """

        # do some error correcting if needed
        if self.multiyear:
            if self.end_year < self.start_year:
                self.end_year = self.start_year

        nr_up = 1 # Number of directory levels up to get to self.html_dir / root

        with self._user.progress(_("Web Calendar Report"),
                                 _('Formatting months ...'), 12) as step:

            for month in range(1, 13):
                cal_fname = str(month)
                open_file = self.create_file(cal_fname, str(year))

                # Add xml, doctype, meta and stylesheets
                # body has already been added to webcal  already once
                webcal, body = self.write_header(nr_up, self.title_text)

                # create Year Navigation menu
                if self.multiyear and ((self.end_year - self.start_year) > 0):
                    body += self.year_navigation(nr_up, str(year))

                # Create Month Navigation Menu
                # identify currentsection for proper highlighting
                currentsection = _dd.long_months[month]
                body += self.month_navigation(nr_up, year, currentsection)

                # build the calendar
                content = Html("div", class_="content", id="WebCal")
                body += content
                monthly_calendar = self.calendar_build("wc", year, month)
                content += monthly_calendar

                # create note section for webcalendar()
                # One has to be minused because the array starts at zero,
                # but January =1
                note = self.month_notes[month-1].strip()
                if note:
                    note = self.database.get_note_from_gramps_id(note)
                    note = self.get_note_format(note)

                # table foot section
                cal_foot = Html("tfoot")
                monthly_calendar += cal_foot

                trow = Html("tr") + (
                    Html("td", note, colspan=7, inline=True)
                    )
                cal_foot += trow

                # create blank line for stylesheets
                # create footer division section
                footer = self.write_footer(nr_up)
                body += (FULLCLEAR, footer)

                # send calendar page to web output
                # and close the file
                self.xhtmlwriter(webcal, open_file)

                step()

    def year_glance(self, year):
        """
        This method will create the Full Year At A Glance Page...
        year -- year being created
        """

        self.event_list = []
        prv = None
        nxt = None
        evdte = None
        for month in sorted(self.calendar):
            vals = sorted(self.calendar.get(month, {}))
            if month == 0: # why ?
                continue
            for day in vals:
                event_date = "%04d%02d%02d" % (year, month, day)
                if evdte is None:
                    evdte = event_date
                elif nxt is None:
                    nxt = event_date
                    self.event_list.append((evdte, prv, nxt))
                else:
                    prv = evdte
                    evdte = nxt
                    nxt = event_date
                    self.event_list.append((evdte, prv, nxt))
        self.event_list.append((nxt, evdte, None))

        nr_up = 1   # Number of directory levels up to get to root

        # generate progress pass for "Year At A Glance"
        with self._user.progress(_("Web Calendar Report"),
                                 _('Creating Year At A Glance calendar'),
                                 12) as step:

            open_file = self.create_file('fullyearlinked', str(year))

            # page title
            title = self._("%(year)d, At A Glance") % {'year' : year}

            # Create page header
            # body has already been added to yearglance  already once
            yearglance, body = self.write_header(nr_up, title,
                                                 "fullyearlinked", False)

            # create Year Navigation menu
            if self.multiyear and ((self.end_year - self.start_year) > 0):
                body += self.year_navigation(nr_up, str(year))

            # Create Month Navigation Menu
            # identify currentsection for proper highlighting
            body += self.month_navigation(nr_up, year, "fullyearlinked")

            msg = (self._('This calendar is meant to give you access '
                          'to all your data at a glance compressed into one '
                          'page. Clicking on a date will take you to a page '
                          'that shows all the events for that date, if there '
                          'are any.\n'))

            # page description
            content = Html("div", class_="content", id="YearGlance")
            body += content

            content += Html("p", msg, id='description')

            for month in range(1, 13):

                # build the calendar
                monthly_calendar = self.calendar_build("yg", year, month,
                                                       clickable=True)
                content += monthly_calendar

                # increase progress bar
                step()

            # create blank line for stylesheets
            # write footer section
            footer = self.write_footer(nr_up)
            body += (FULLCLEAR, footer)

            # send calendar page to web output
            # and close the file
            self.xhtmlwriter(yearglance, open_file)

    def one_day(self, event_date, fname_date, day_list):
        """
        This method creates the One Day page for "Year At A Glance"

        event_date -- date for the listed events

        fname_date -- filename date from calendar_build()

        day_list   -- a combination of both dictionaries to be able
                      to create one day
        nyears, date, text, event -- are necessary for figuring the age
        or years married for each year being created...
        """

        nr_up = 1 # number of directory levels up to get to root

        # get year and month from event_date for use in this section
        year = event_date.get_year()
        month = event_date.get_month()

        one_day_file = self.create_file(fname_date, str(year))

        # page title
        title = self._('One Day Within A Year')

        # create page header
        oneday, body = self.write_header(nr_up, title, "OneDay")

        # create Year Navigation menu
        if self.multiyear and ((self.end_year - self.start_year) > 0):
            body += self.year_navigation(nr_up, str(year))

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        currentsection = _dd.long_months[month]
        body += self.month_navigation(nr_up, year, currentsection)

        # set date display as in user preferences
        content = Html("div", class_="content", id="OneDay")
        body += content
        evt = fname_date[:8]
        found = (evt, None, None)
        for event in self.event_list:
            if event[0] == evt:
                found = event
                break
        my_title = Html()
        url = "#"
        if found[1] is not None:
            url = event[1] + self.ext
            prevd = Date(int(event[1][:4]), int(event[1][4:6]),
                         int(event[1][6:]))
            my_title = Html("a", "\u276e", href=url,
                            title=self.rlocale.get_date(prevd))
        else:
            my_title = Html('<em>&nbsp;&nbsp;</em>')
        my_title += Html("</a>")
        my_title += "&nbsp;&nbsp;"
        my_title += self.rlocale.date_displayer.display(event_date)
        my_title += "&nbsp;&nbsp;"
        if found[2] is not None:
            url = event[2] + self.ext
            nextd = Date(int(event[2][:4]), int(event[2][4:6]),
                         int(event[2][6:]))
            my_title += Html("a", "\u276f", href=url,
                             title=self.rlocale.get_date(nextd))
        else:
            my_title += Html('<b>&nbsp;&nbsp;</b>')
        content += Html("h3", my_title, inline=True)

        # list the events
        ordered = Html("ol")
        content += ordered
        for (dummy_nyears, dummy_date, text, event, dummy_age_at_death,
             dummy_dead_event_date) in day_list:
            ordered += Html("li", text,
                            inline=False if event == 'Anniversary' else True)

        # create blank line for stylesheets
        # write footer section
        footer = self.write_footer(nr_up)
        body += (FULLCLEAR, footer)

        # send calendar page to web output
        # and close the file
        self.xhtmlwriter(oneday, one_day_file)

    def build_url_fname_html(self, fname, subdir=None, prefix=None):
        """
        build the url for the file name with sub directories and extension
        """
        return self.build_url_fname(fname, subdir, prefix) + self.ext

    def build_url_fname(self, fname, subdir, prefix=None):
        """
        Create part of the URL given the filename and optionally
        the subdirectory. If the subdirectory is given, then two extra levels
        of subdirectory are inserted between 'subdir' and the filename.
        The reason is to prevent directories with too many entries.
        If 'prefix' is set, then is inserted in front of the result.

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        Imagine we run gramps on Windows (heaven forbits), we don't want to
        see backslashes in the URL.
        """
        if win():
            fname = fname.replace('\\', "/")
        subdirs = self.build_subdirs(subdir, fname)
        return (prefix or '') + "/".join(subdirs + [fname])

    def build_subdirs(self, subdir, fname):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename.
        The reason is to prevent directories with too many entries.

        For example,
        this may return ['ppl', '8', '1'] given 'ppl', "aec934857df74d36618"
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())
        return subdirs

    def get_name(self, person, maiden_name=None):
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
        people = self.filter.apply(db, people, user=self._user)

        with self._user.progress(_("Web Calendar Report"),
                                 _("Reading database..."), len(people)) as step:
            for person in map(db.get_person_from_handle, people):
                step()

                family_list = person.get_family_handle_list()
                birth_ref = person.get_birth_ref()
                birth_date = Date()
                if birth_ref:
                    birth_event = db.get_event_from_handle(birth_ref.ref)
                    birth_date = birth_event.get_date_object()

                death_ref = person.get_death_ref()
                person_death = Date()
                age_at_death = None
                if death_ref and birth_date:
                    death_event = db.get_event_from_handle(death_ref.ref)
                    death_date = death_event.get_date_object()
                    person_death = death_date
                    if (birth_date != Date() and birth_date.is_valid()
                            and death_date):
                        age_at_death = death_date - birth_date
                        age_at_death = age_at_death.format(dlocale=self.rlocale)

                # determine birthday information???
                if (self.birthday and birth_date is not Date()
                        and birth_date.is_valid()):
                    birth_date = gregorian(birth_date)

                    year = birth_date.get_year()
                    month = birth_date.get_month()
                    day = birth_date.get_day()

                    # date to figure if someone is still alive
                    # current year of calendar, month nd day is their birth
                    # month and birth day
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
                                        father = db.get_person_from_handle(
                                            father_handle)
                                        if father is not None:
                                            father_surname = _regular_surname(
                                                person.gender,
                                                father.get_primary_name())
                    short_name = self.get_name(person, father_surname)
                    alive = probably_alive(person, db, prob_alive_date)
                    if (self.alive and alive) or not self.alive:

                        # add link to NarrativeWeb
                        if self.link_to_narweb:
                            if self.narweb_prefix[:1] != '/':
                                prfx = "../" + self.narweb_prefix
                            else:
                                prfx = self.narweb_prefix
                            text = str(Html("a", short_name,
                                            href=self.build_url_fname_html(
                                                person.handle,
                                                "ppl",
                                                prefix=prfx)))
                        else:
                            text = short_name
                        if age_at_death is None:
                            self.add_day_item(text, year, month, day,
                                              'Birthday',
                                              age_at_death, birth_date)
                        else:
                            self.add_day_item(text, year, month, day,
                                              'Birthday',
                                              age_at_death, person_death)
                death_event = get_death_or_fallback(db, person)
                if death_event:
                    death_date = death_event.get_date_object()
                else:
                    death_date = None
                #primary_name = person.primary_name
                #name = Name(primary_name)
                if self.death_anniv and death_date:
                    year = death_date.get_year() or this_year
                    month = death_date.get_month()
                    day = death_date.get_day()

                    short_name = self.get_name(person)
                    prob_alive_date = Date(this_year, month, day)
                    alive = probably_alive(person, db, prob_alive_date)
                    if (self.alive and alive) or not self.alive:
                        # add link to NarrativeWeb
                        if self.link_to_narweb:
                            if self.narweb_prefix[:1] != '/':
                                prfx = "../" + self.narweb_prefix
                            else:
                                prfx = self.narweb_prefix
                            navpfx = self.build_url_fname_html(person.handle,
                                                               "ppl",
                                                               prefix=prfx)
                            text = str(Html("a", short_name, href=navpfx))
                        else:
                            text = short_name
                        self.add_day_item(text, year, month, day, 'Death',
                                          age_at_death, death_date)

                # add anniversary if requested
                if self.anniv:
                    for fhandle in family_list:
                        fam = db.get_family_from_handle(fhandle)
                        father_handle = fam.get_father_handle()
                        mother_handle = fam.get_mother_handle()
                        if father_handle == person.handle:
                            spouse_handle = mother_handle
                        else:
                            continue # with next person if this was
                                     # the marriage event
                        if spouse_handle:
                            spouse = db.get_person_from_handle(spouse_handle)
                            if spouse:
                                spouse_name = self.get_name(spouse)
                                short_name = self.get_name(person)
                                death_ref = spouse.get_death_ref()
                                spouse_death = Date()
                                if death_ref:
                                    death_event = db.get_event_from_handle(
                                        death_ref.ref)
                                    death_date = death_event.get_date_object()
                                    if (death_date != Date() and
                                            death_date.is_valid()):
                                        spouse_death = death_date
                            first_died = Date()
                            if person_death == Date():
                                first_died = spouse_death
                            elif spouse_death != Date():
                                first_died = person_death if spouse_death\
                                                > person_death else spouse_death
                            else:
                                first_died = person_death

                            # will return a marriage event or False if not
                            # married any longer
                            marriage_event = get_marriage_event(db, fam)
                            if marriage_event:
                                event_date = marriage_event.get_date_object()
                                if (event_date is not Date() and
                                        event_date.is_valid()):
                                    event_date = gregorian(event_date)
                                    year = event_date.get_year()
                                    month = event_date.get_month()
                                    day = event_date.get_day()

                                    # date to figure if someone is still alive
                                    prob_alive_date = Date(this_year,
                                                           month, day)
                                    wedding_age = None
                                    if first_died != Date():
                                        wedding_age = first_died - event_date
                                        wedding_age = wedding_age.format(
                                            dlocale=self.rlocale)
                                    divorce_event = get_divorce_event(db, fam)
                                    if divorce_event:
                                        d_date = divorce_event.get_date_object()
                                        if (d_date is not Date() and
                                                d_date.is_valid()):
                                            d_date = gregorian(d_date)
                                            if d_date != Date():
                                                w_age = d_date - event_date
                                                w_age = w_age.format(
                                                    dlocale=self.rlocale)
                                                wedding_age = w_age
                                                first_died = d_date

                                    if self.link_to_narweb:
                                        if self.narweb_prefix[:1] != '/':
                                            prefx = "../" + self.narweb_prefix
                                        else:
                                            prefx = self.narweb_prefix
                                        reference = self.build_url_fname_html(
                                            spouse_handle, 'ppl',
                                            prefix=prefx)
                                        spouse_name = str(Html("a", spouse_name,
                                                               href=reference))
                                        href1 = self.build_url_fname_html(
                                            person.handle, 'ppl', prefix=prefx)
                                        short_name = str(Html("a", short_name,
                                                              href=href1))

                                    alive1 = probably_alive(person, db,
                                                            prob_alive_date)
                                    alive2 = probably_alive(spouse, db,
                                                            prob_alive_date)
                                    if first_died == Date():
                                        first_died = Date(0, 0, 0)
                                    if ((self.alive and (alive1 or alive2))
                                            or not self.alive):

                                        spse = self._('%(spouse)s and'
                                                      ' %(person)s')
                                        text = spse % {'spouse' : spouse_name,
                                                       'person' : short_name}

                                        self.add_day_item(text, year, month,
                                                          day, 'Anniversary',
                                                          wedding_age,
                                                          first_died)

    def write_footer(self, nr_up):
        """
        Writes the footer section of the pages
        'nr_up' - number of directory levels up, started from current page,
                  to the root of the directory tree (i.e. to self.html_dir).
        """

        # begin calendar footer
        with Html("div", id="footer", role="Footer-End") as footer:

            amsg = None
            if self.author and self.email:
                bemail = '<a href="mailto:' + self.email + '?subject='
                eemail = '">' + self.author + '</a>'
                amsg = self._('%(html_email_author_start)s'
                              'WebCal%(html_email_author_end)s',
                              'the "WebCal" will be the potential-email'
                              ' Subject') % {
                                  'html_email_author_start' : bemail,
                                  'html_email_author_end' : eemail}
            elif self.author:
                amsg = '%(author)s' % {
                    'author' : self.author}

            # Display date as user set in preferences
            date = self.rlocale.date_displayer.display(Today())
            bhtml = '<a href="' + URL_HOMEPAGE + '">'
            msg = self._('Generated by %(gramps_home_html_start)s'
                         'Gramps%(html_end)s on %(date)s') % {
                             'gramps_home_html_start' : bhtml,
                             'html_end' : '</a>',
                             'date' : date}
            copy_nr = self.copy
            if copy_nr == 0:
                if self.author:
                    amsg = "&copy; %s" % amsg
            msg += " (%s)" % amsg
            footer += Html("p", msg, id='createdate')

            text = ''
            if 0 < copy_nr < len(_CC):
                subdirs = ['..'] * nr_up
                # Note. We use '/' here because it is a URL,
                # not a OS dependent pathname
                fname = '/'.join(subdirs + ['images'] + ['somerights20.gif'])
                text = _CC[copy_nr] % {'gif_fname' : fname}

            footer += Html("p", text, id='copyright')

        # return footer to its callers
        return footer

    def xhtmlwriter(self, page, open_file):
        """
        This function is simply to make the web page look pretty and readable
        It is not for the browser, but for us, humans
        """

        # writes the file out from the page variable; Html instance
        # This didn't work for some reason, but it does in NarWeb:
        #page.write(partial(print, file=of.write))
        page.write(lambda line: open_file.write(line + '\n'))
        # close the file now...
        self.close_file(open_file)

    def write_report(self):
        """
        The short method that runs through each month and creates a page.
        """
        # get data from database for birthdays/ anniversaries
        self.collect_data(self.start_year)

        # Copy all files for the calendars being created
        self.copy_calendar_files()

        if self.multiyear:

            # limit number of years to eighteen (18) years and only one row
            # of years
            nyears = ((self.end_year - self.start_year) + 1)
            num_years = nyears if 0 < nyears < 19 else 18

            for cal_year in range(self.start_year,
                                  (self.start_year + num_years)):

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

                self.create_page_index()

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

            if self.link_to_narweb:
                self.create_page_index()

    def create_page_index(self):
        """
        Create the page index called by the narrativeweb.
        """
        output_file = self.create_file('index', "")

        # page title
        title = self.title_text

        nr_up = 0

        # Create page header
        # body has already been added to yearglance  already once
        index, body = self.write_header(nr_up, title, "index", False)

        # create Year Navigation menu
        current_year = time.strftime("%Y", time.gmtime())
        body += self.year_navigation(nr_up, str(current_year))

        # create blank line for stylesheets
        # write footer section
        footer = self.write_footer(nr_up)
        body += (FULLCLEAR, footer)

        # send calendar page to web output
        # and close the file
        self.xhtmlwriter(index, output_file)

# -----------------------------------------------------------------------------
#                             WebCalOptions; Creates the Menu
#------------------------------------------------------------------------------
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
        db_options = name + ' ' + dbase.get_dbname()
        MenuReportOptions.__init__(self, db_options, dbase)
        self.__multiyear = None
        self.__start_year = None
        self.__end_year = None
        self.__after_year = None

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web calendar.
        """
        self.__add_report_options(menu)
        self.__add_report2_options(menu)
        self.__add_content_options(menu)
        self.__add_advanced_options(menu)
        self.__add_notes_options(menu)

    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")

        dbname = self.__db.get_dbname()
        default_dir = dbname + "_WEBCAL"
        target = DestinationOption(
            _("Destination"),
            os.path.join(config.get('paths.website-directory'), default_dir))
        target.set_help(_("The destination directory for the web files"))
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

        ext = EnumeratedListOption(_("File extension"), ".html")
        for etype in _WEB_EXT:
            ext.add_item(etype, etype)
        ext.set_help(_("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0)
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help(_("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        css_list = sorted([(CSS[key]["translation"], CSS[key]["id"])
                           for key in list(CSS.keys())
                           if CSS[key]["user"]])
        css = EnumeratedListOption(_('StyleSheet'), css_list[0][1])
        for css_item in css_list:
            css.add_item(css_item[1], css_item[0])
        css.set_help(_('The stylesheet to be used for the web pages'))
        menu.add_option(category_name, "css", css)

    def __add_report2_options(self, menu):
        """
        Options on the "Report Options (2)" tab.
        """
        category_name = _("Report Options (2)")

        # We must figure out the value of the first option before we can
        # create the EnumeratedListOption
        fmt_list = _nd.get_name_format()
        defaultnum = _nd.get_default_format()
        default = 0
        for ind, val in enumerate(fmt_list):
            if val[0] == defaultnum:
                default = ind
                break
        name_format = EnumeratedListOption(_("Name format"),
                                           fmt_list[default][0])
        for num, name, dummy_fmt_str, dummy_act in fmt_list:
            name_format.add_item(num, name)
        name_format.set_help(_("Select the format to display names"))
        menu.add_option(category_name, "name_format", name_format)

        stdoptions.add_private_data_option(menu, category_name, default=False)

        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", alive)

        locale_opt = stdoptions.add_localization_option(menu, category_name)
        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    def __add_content_options(self, menu):
        """
        Options on the "Content Options" tab.
        """
        category_name = _("Content Options")

        # set to today's date for use in menu, etc.
        today = Today()

        self.__multiyear = BooleanOption(_('Create multiple year calendars'),
                                         False)
        self.__multiyear.set_help(_('Whether to create Multiple year '
                                    'calendars or not.'))
        menu.add_option(category_name, 'multiyear', self.__multiyear)
        self.__multiyear.connect('value-changed', self.__multiyear_changed)

        self.__start_year = NumberOption(_('Start Year for the Calendar(s)'),
                                         today.get_year(), 1900, 3000)
        self.__start_year.set_help(_('Enter the starting year for the calendars'
                                     ' between 1900 - 3000'))
        menu.add_option(category_name, 'start_year', self.__start_year)

        self.__end_year = NumberOption(_('End Year for the Calendar(s)'),
                                       today.get_year(), 1900, 3000)
        self.__end_year.set_help(_('Enter the ending year for the calendars '
                                   'between 1900 - 3000.'))
        menu.add_option(category_name, 'end_year', self.__end_year)

        self.__multiyear_changed()

        country = EnumeratedListOption(_('Country for holidays'), 0)
        holiday_table = libholiday.HolidayTable()
        countries = holiday_table.get_countries()
        countries.sort()
        #if (len(countries) == 0 or
        #        (len(countries) > 0 and countries[0] != '')):
        if (not countries or
                (countries and countries[0] != '')):
            countries.insert(0, '')
        count = 0
        for cntry in countries:
            country.add_item(count, cntry)
            count += 1
        country.set_help(_("Holidays will be included for the selected "
                           "country"))
        menu.add_option(category_name, "country", country)

        # Default selection ????
        start_dow = EnumeratedListOption(_("First day of week"), 1)
        for count in range(1, 8):
            start_dow.add_item(count, _dd.long_days[count].capitalize())
        start_dow.set_help(_("Select the first day of the week "
                             "for the calendar"))
        menu.add_option(category_name, "start_dow", start_dow)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item('spouse_first', _("Wives use husband's surname "
                                               "(from first family listed)"))
        maiden_name.add_item('spouse_last', _("Wives use husband's surname "
                                              "(from last family listed)"))
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)

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

        encoding = EnumeratedListOption(_('Character set encoding'),
                                        _CHARACTER_SETS[0][1])
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help(_('The encoding to be used for the web files'))
        menu.add_option(category_name, "encoding", encoding)

        makeoneday = BooleanOption(_('Create one day event pages for'
                                     ' Year At A Glance calendar'), False)
        makeoneday.set_help(_('Whether to create one day pages or not'))
        menu.add_option(category_name, 'makeoneday', makeoneday)

        birthdays = BooleanOption(_("Include birthdays"), True)
        birthdays.set_help(_("Include birthdays in the calendar"))
        menu.add_option(category_name, "birthdays", birthdays)

        anniversaries = BooleanOption(_("Include anniversaries"), True)
        anniversaries.set_help(_("Include anniversaries in the calendar"))
        menu.add_option(category_name, "anniversaries", anniversaries)

        anniversaries = BooleanOption(_('Include death dates'), False)
        anniversaries.set_help(_('Include death anniversaries in the calendar'))
        menu.add_option(category_name, 'death_anniv', anniversaries)

        self.__links = BooleanOption(_('Link to Narrated Web Report'), False)
        self.__links.set_help(_('Whether to link data to web report or not'))
        menu.add_option(category_name, 'link_to_narweb', self.__links)
        self.__links.connect('value-changed', self.__links_changed)

        today = Today()
        default_before = config.get('behavior.max-age-prob-alive')
        self.__after_year = NumberOption(_('Show data only after year'),
                                         (today.get_year() - default_before),
                                         0, today.get_year())
        self.__after_year.set_help(_("Show data only after this year."
                                     " Default is current year - "
                                     " 'maximum age probably alive' which is "
                                     "defined in the dates preference tab."))
        menu.add_option(category_name, 'after_year', self.__after_year)

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
        filter_list = utils.get_person_filters(person, False)
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
        mgobn = lambda name: self.menu.get_option_by_name(name)
        self.__multiyear = mgobn('multiyear')
        self.__start_year = mgobn('start_year')
        self.__end_year = mgobn('end_year')

        if self.__start_year:
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

def _regular_surname(sex, name):
    """
    Returns a name string built from the components of the Name instance.
    """
    dummy_gender = sex
    surname = name.get_surname()
    suffix = name.get_suffix()
    if suffix:
        # TODO for Arabic, should the next line's comma be translated?
        surname = surname + ", " + suffix
    return surname

# Simple utility list to convert Gramps day-of-week numbering
# to calendar.firstweekday numbering
DOW_GRAMPS2ISO = [-1, calendar.SUNDAY, calendar.MONDAY, calendar.TUESDAY,
                  calendar.WEDNESDAY, calendar.THURSDAY, calendar.FRIDAY,
                  calendar.SATURDAY]

def get_marriage_event(db, family):
    """
    marriage_event will either be the marriage event or False
    """

    marriage_event = False
    for event_ref in family.get_event_ref_list():

        event = db.get_event_from_handle(event_ref.ref)
        if event.type.is_marriage():
            marriage_event = event
            break

    # return the marriage event or False to it caller
    return marriage_event

def get_divorce_event(db, family):
    """
    divorce will either be the divorce event or False
    """

    divorce_event = False
    for event_ref in family.get_event_ref_list():

        event = db.get_event_from_handle(event_ref.ref)
        if event.type.is_divorce():
            divorce_event = event
            break

    # return the divorce event or False to it caller
    return divorce_event

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

def get_day_list(event_date, holiday_list, bday_anniv_list, rlocale=glocale):
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
    rlocale -- the locale to use
    """

    trans_text = rlocale.translation.sgettext
    # initialize day_list
    day_list = []

    ##################################################################
    # birthday/ anniversary on this day
    # Date.EMPTY signifies an incomplete date for an event. See add_day_item()
    bday_anniv_list = [(t, e, d, n, x) for t, e, d, n, x in bday_anniv_list
                       if d != Date.EMPTY]

    # number of years have to be at least zero
    bday_anniv_list = [(t, e, d, n, x) for t, e, d, n, x in bday_anniv_list
                       if (event_date.get_year() - d.get_year()) >= 0]

    # a holiday
    # zero will force holidays to be first in list
    nyears = 0

    for text, event, date, notused, notused  in holiday_list:
        day_list.append((nyears, date, text, event, notused, notused))

    # birthday and anniversary list
    for text, event, date, age_at_death, dead_event_date in bday_anniv_list:

        # number of years married, ex: 10
        nyears = (event_date.get_year() - date.get_year())

        # number of years for birthday, ex: 10 years
        age_str = event_date - date
        #age_str.format(precision=1, as_age=False, dlocale=rlocale)
        age_str = age_str.format(precision=1, as_age=False, dlocale=rlocale)

        symbols = Symbols()
        death_idx = config.get('utf8.death-symbol')
        death_symbol = symbols.get_death_symbol_for_char(death_idx)

        # a birthday
        if event == 'Birthday':

            if age_at_death is not None:
                trans_date = trans_text("Died %(death_date)s.")
                translated_date = rlocale.get_date(dead_event_date)
                mess = trans_date % {'death_date' : translated_date}
                age = ", <font size='+1' ><b>%s</b></font> <em>%s (%s)" % (
                    death_symbol, mess, age_at_death)
            else:
                # TRANSLATORS: expands to smth like "12 years old",
                # where "12 years" is already localized to your language
                age = ', <em>'
                date_y = date.get_year()
                trans_date = trans_text("Born %(birth_date)s.")
                old_date = trans_text('%s old')
                translated_date = rlocale.get_date(dead_event_date)
                age += old_date % (str(age_str) if (date_y != 0)
                                   else trans_date % {
                                       'birth_date' : translated_date})
            txt_str = (text + age + '</em>')

        # a death
        if event == 'Death':
            txt_str = (text + ', ' + death_symbol + ' <em>'
                       + (_('%s since death') % str(age_str) if nyears
                          else _('death'))
                       + '</em>')

        # an anniversary
        elif event == "Anniversary":

            if nyears == 0:
                txt_str = trans_text('%(couple)s, <em>wedding</em>') % {
                    'couple' : text}
            else:
                if age_at_death is not None:
                    age = '%s %s' % (trans_text("Married"), age_at_death)
                    txt_str = "%s, <em>%s" % (text, age)
                    if isinstance(dead_event_date,
                                  Date) and dead_event_date.get_year() > 0:
                        txt_str += " (" + trans_text("Until") + " "
                        txt_str += rlocale.get_date(dead_event_date)
                        txt_str += ")</em>"
                    else:
                        txt_str += "</em>"
                else:
                    age = '<em>%s' % nyears
                    # translators: leave all/any {...} untranslated
                    ngettext = rlocale.translation.ngettext
                    txt_str = ngettext("{couple}, {years} year anniversary",
                                       "{couple}, {years} year anniversary",
                                       nyears).format(couple=text, years=age)
                    txt_str += "</em>"
            txt_str = Html('span', txt_str, class_="yearsmarried")

        day_list.append((nyears, date, txt_str, event,
                         age_at_death, dead_event_date))

    # sort them based on number of years
    # holidays will always be on top of event list
    day_list = sorted(day_list, key=lambda x: (isinstance(x[0], str), x[0]))

    # return to its caller calendar_build()
    return day_list
