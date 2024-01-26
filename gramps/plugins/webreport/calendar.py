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
# Copyright (C) 2020-     Serge Noiraud
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

# ------------------------------------------------------------------------
# python modules
# ------------------------------------------------------------------------
import os
import datetime
import calendar  # Python module

# ------------------------------------------------------------------------
# Set up logging
# ------------------------------------------------------------------------
import logging

# ------------------------------------------------------------------------
# Gramps module
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.config import config
from gramps.gen.lib import Date, Name, NameType, Person
from gramps.gen.lib.date import Today
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import get_death_or_fallback
from gramps.gen.utils.symbols import Symbols
from gramps.gen.datehandler import displayer as _dd

from gramps.gen.display.name import displayer as _nd

import gramps.plugins.lib.libholiday as libholiday
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import do_we_have_holidays, _WEB_EXT
from gramps.plugins.lib.libhtml import Html  # , xml_lang
from gramps.gui.pluginmanager import GuiPluginManager

from gramps.gen.lib.date import gregorian

# from gramps.plugins.lib.libhtmlbackend import HtmlBackend
# ------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------
_ = glocale.translation.sgettext
_LOG = logging.getLogger(".WebPage")

# full clear line for proper styling

FULLCLEAR = Html("div", class_="fullclear", inline=True)

# Calendar stylesheet names
_CALENDARSCREEN = "calendar-screen.css"
_CALENDARPRINT = "calendar-print.css"

PLUGMAN = GuiPluginManager.get_instance()
CSS = PLUGMAN.process_plugin_data("WEBSTUFF")

SCRIPT = """<script type="text/javascript">function currentmonth(y) {
var date = new Date();
var month = date.getMonth() + 1;
var url = y + "/" + month + "%s";
window.location.replace(url);
}
</script>
"""

CURRENT_DAY = """
<script type="text/javascript">
function CurrentDay() {
var date = new Date();
var months = "00" + (date.getMonth() + 1);
var days = "00" + date.getDate();
var day = days.substr(days.length-2);
var month = months.substr(months.length-2);
// Get the DOM reference
var elem = month+day;
var contentId = document.getElementById(elem);
contentId.style.background = "GreenYellow";
}
</script>
"""


# ------------------------------------------------------------------------
#
# WebCalReport
#
# ------------------------------------------------------------------------
class CalendarPage(BasePage):
    """
    Create WebCalReport object that produces the report.
    """

    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)

        # class to do conversion of styled notes to html markup
        self.title_str = self._("Calendar")
        self.title_text = the_title
        self.name_format = report.options["name_format"]

        self.multiyear = False
        self.end_year = self.start_year = Today().get_year()

        self.maiden_name = report.options["maiden_name"]

        self.after_year = report.options["after_year"]
        self.alive = report.options["alive"]
        self.birthday = report.options["birthdays"]
        self.anniv = report.options["anniversaries"]
        self.death_anniv = report.options["death_anniv"]
        self.event_list = []
        self.current_month = None

        self._get_date = None
        self.fullyear = True
        self.makeoneday = report.options["makeoneday"]
        self.start_dow = report.options["start_dow"]

        self.warn_dir = True  # Only give warning once.

        self.link_to_narweb = True

        # self.calendar is a dict; key is the month number
        # Each entry in the dict is also a dict; key is the day number.
        # The day dict is a list of things to display for that day.
        # These things are: birthdays and anniversaries
        self.calendar = {}
        self.holidays = {}

        calendar.setfirstweekday(DOW_GRAMPS2ISO[self.start_dow])
        self.head = []

    def display_pages(self, the_lang, the_title):
        self.the_lang = the_lang
        self.the_title = the_title
        if the_lang:
            self.rlocale = self.report.set_locale(the_lang)
        else:
            self.rlocale = self.report.set_locale(self.report.options["trans"])
        self._ = self.rlocale.translation.sgettext
        self._get_date = self.rlocale.get_date
        self.title_text = the_title + " (" + self._("Calendar") + ")"
        self.title_str = self.title_text
        self.write_report()

    def add_day_item(
        self, text, year, month, day, event, age_at_death, dead_event_date
    ):
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
        if event in ["Birthday", "Anniversary", "Death"]:
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
            event_date = Date.EMPTY  # Incomplete date....

        day_list.append((text, event, event_date, age_at_death, dead_event_date))
        month_dict[day] = day_list

        # determine which dictionary to add it to???
        if event in ["Birthday", "Anniversary", "Death"]:
            self.calendar[month] = month_dict
        else:
            self.holidays[month] = month_dict

    def __get_holidays(self, year):
        """Get the holidays for the specified country and year"""

        # _('translation')
        with self.r_user.progress(
            _("Web Calendar Report"),
            _("Calculating Holidays for year %04d") % year,
            365,
        ) as step:
            index = do_we_have_holidays(self.the_lang)
            if index is not None:
                holiday_table = libholiday.HolidayTable()
                country = holiday_table.get_countries()[index]
                holiday_table.load_holidays(year, country)
                for month in range(1, 13):
                    for day in range(1, 32):
                        holiday_names = holiday_table.get_holidays(month, day)
                        for holiday_name in holiday_names:
                            self.add_day_item(
                                holiday_name, year, month, day, "Holiday", None, None
                            )
                        step()

    def month_navigation(self, nr_up, year, currentsection):
        """
        Will create and display the navigation menu bar

        nr_up = number of directories up to reach root directory
        year = year being created
        currentsection = month name being created for proper CSS styling
        """
        navs = []

        navs.extend(
            (str(month), self.rlocale.date_displayer.short_months[int(month)], True)
            for month in range(1, 13)
        )

        # Add a link for year_glance() if requested
        navs.append(("fullyearlinked", self._("Full year at a Glance"), self.fullyear))

        # remove menu items if they are not True
        navs = [(u, n) for u, n, c in navs if c]

        # begin month subnavigation
        with Html("div", class_="wrapper", id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:
                unordered = Html("ul", class_="menu " + self.dir)

                for url_fname, nav_text in navs:
                    # Note. We use '/' here because it is a URL, not a OS
                    # dependent pathname need to leave home link alone,
                    # so look for it ...
                    if nav_text != self._("NarrativeWeb Home"):
                        url_fname = url_fname.lower()
                    url = url_fname
                    add_subdirs = False
                    if not (url.startswith("http:") or url.startswith("/")):
                        add_subdirs = not any(url.endswith(ext) for ext in _WEB_EXT)

                    # whether to add subdirs or not???
                    if add_subdirs:
                        subdirs = [".."] * nr_up
                        subdirs.append("cal")
                        subdirs.append(str(year))
                        url = "/".join(subdirs + [url_fname])

                    if not _has_webpage_extension(url):
                        url += self.ext

                    # Figure out if we need <li class="CurrentSection"> or
                    # just plain <li>
                    check_cs = False
                    if url_fname == currentsection:
                        check_cs = 'class = "CurrentSection"'
                    elif url_fname == self.current_month:
                        check_cs = 'class = "CurrentSection"'

                    if url_fname == "fullyearlinked":
                        mytitle = self._("Full year at a Glance")
                    else:
                        mytitle = self._(url_fname)
                    hyper = Html("a", nav_text, href=url, name=url_fname, title=mytitle)

                    if check_cs:
                        unordered.extend(Html("li", hyper, attr=check_cs, inline=True))
                    else:
                        unordered.extend(Html("li", hyper, inline=True))
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
        col2day = [(x - 1) % 7 + 1 for x in range(start_dow, start_dow + 7)]

        def get_class_for_daycol(col):
            """Translate a Gramps day number into a HTMLclass"""
            day = col2day[col]
            if day == 1:
                return "weekend sunday"
            elif day == 7:
                return "weekend saturday"
            return "weekday"

        def get_name_for_daycol(col):
            """Translate a Gramps day number into a HTMLclass"""
            day = col2day[col]
            return day_names[day]

        # Note. gen.datehandler has sunday => 1, monday => 2, etc
        # We slice out the first empty element.
        day_names = date_displayer.long_days  # use self._ldd.long_days when
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
        if cal == "wc":  # webcalendar()
            if not self.multiyear:
                th_txt = "%s %s" % (month_name, self._get_date(Date(year)))  # localized

        # begin calendar table and table head
        with Html(
            "table", class_="calendar", id=month_name, role="Calendar-Grid"
        ) as table:
            thead = Html("thead")
            table += thead

            if clickable:
                name = str(month) + self.ext
                linkable = Html("a", th_txt, href=name, name=name, title=th_txt)
                trow = Html("tr") + (
                    Html("th", linkable, class_="monthName", colspan=7, inline=True)
                )
                thead += trow
            else:
                if not self.multiyear:
                    self.end_year = self.start_year
                if month > 1:
                    full_month_name = str(month - 1)
                    url = full_month_name.lower() + self.ext
                    prevm = Date(int(year), int(month - 1), 0)
                    my_title = Html(
                        "a",
                        "\u276e",
                        href=url,
                        close=True,
                        title=date_displayer.display(prevm),
                    )
                elif self.multiyear and year > self.start_year:
                    full_month_name = str(12)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(year - 1), url)
                    prevm = Date(int(year - 1), 12, 0)
                    my_title = Html(
                        "a",
                        "\u276e",
                        href=dest,
                        close=True,
                        title=date_displayer.display(prevm),
                    )
                else:
                    full_month_name = str(12)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(self.end_year), url)
                    prevy = Date(self.end_year, 12, 0)
                    my_title = Html(
                        "a",
                        "\u276e",
                        href=dest,
                        close=True,
                        title=date_displayer.display(prevy),
                    )
                my_title += Html("</a>&nbsp;" + month_name + "&nbsp;")
                if month < 12:
                    full_month_name = str(month + 1)
                    url = full_month_name.lower() + self.ext
                    nextd = Date(int(year), int(month + 1), 0)
                    my_title += Html(
                        "a",
                        "\u276f",
                        href=url,
                        close=True,
                        title=date_displayer.display(nextd),
                    )
                elif self.multiyear and year < self.end_year:
                    full_month_name = str(1)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(year + 1), url)
                    nextd = Date(int(year + 1), 1, 0)
                    my_title += Html(
                        "a",
                        "\u276f",
                        href=dest,
                        close=True,
                        title=date_displayer.display(nextd),
                    )
                else:
                    full_month_name = str(1)
                    url = full_month_name.lower() + self.ext
                    dest = os.path.join("../", str(self.start_year), url)
                    nexty = Date(self.start_year, 1, 0)
                    my_title += Html(
                        "a",
                        "\u276f",
                        href=dest,
                        close=True,
                        title=date_displayer.display(nexty),
                    )
                trow = Html("tr") + (
                    Html("th", my_title, class_="monthName", colspan=7, inline=True)
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
                    Html("abbr", dayname[0], title=dayname)
                )

            # begin table body
            tbody = Html("tbody")
            table += tbody

            # get first of the month and month information
            (dummy_current_date, current_ord, monthinfo) = get_first_day_of_month(
                year, month
            )

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
                    tcell_id = "%02d%02d" % (month, day)

                    # add calendar date division
                    datediv = Html("div", day, class_="date", inline=True)
                    clickable = Html("div", datediv, class_="clickable", inline=True)

                    ### a day in the previous or next month ###
                    if day == 0:
                        # day in previous/ next month
                        specday = (
                            __get_previous_month_day(year, month, day_col)
                            if week_row == 0
                            else __get_next_month_day(year, month, day_col)
                        )

                        specclass = "previous " if week_row == 0 else "next "
                        specclass += dayclass

                        # continue table cell, <td>, without id tag
                        tcell = Html("td", class_=specclass, inline=True) + (
                            Html("div", specday, class_="date", inline=True)
                        )

                    # normal day number in current month
                    else:
                        thisday = datetime.date.fromordinal(current_ord)

                        # Something this month
                        if thisday.month == month:
                            holiday_list = self.holidays.get(month, {}).get(
                                thisday.day, []
                            )
                            bday_anniv_list = self.calendar.get(month, {}).get(
                                thisday.day, []
                            )

                            # date is an instance because of subtracting
                            # abilities in date.py
                            event_date = Date(thisday.year, thisday.month, thisday.day)

                            # get events for this day
                            day_list = get_day_list(
                                event_date,
                                holiday_list,
                                bday_anniv_list,
                                rlocale=self.rlocale,
                            )

                            # is there something this day?
                            if day_list:
                                hilightday = "highlight " + dayclass
                                tcell = Html("td", id=tcell_id, class_=hilightday)

                                # Year at a Glance
                                if cal == "yg":
                                    # make one day pages and hyperlink
                                    if self.makeoneday:
                                        # create yyyymmdd date string for
                                        # "One Day" calendar page filename
                                        fname_date = "%04d%02d%02d" % (year, month, day)
                                        fname_date += self.ext

                                        # create hyperlink to one_day()
                                        tcell += Html(
                                            "a", datediv, href=fname_date, inline=True
                                        )

                                        # only year_glance() needs this to
                                        # create the one_day() pages
                                        self.one_day(event_date, fname_date, day_list)

                                    # just year_glance(), but no one_day() pages
                                    else:
                                        # continue table cell, <td>,
                                        # without id tag
                                        tcell = Html(
                                            "td", class_=hilightday, inline=True
                                        ) + (
                                            # adds date division
                                            Html("div", day, class_="date", inline=True)
                                        )

                                # WebCal
                                else:
                                    # add date to table cell
                                    tcell += clickable

                                    # list the events
                                    unordered = Html("ul")
                                    clickable += unordered

                                    for (
                                        dummy_nyears,
                                        dummy_date,
                                        text,
                                        event,
                                        dummy_notused,
                                        dummy_notused,
                                    ) in day_list:
                                        unordered += Html(
                                            "li",
                                            text,
                                            inline=(
                                                False
                                                if (event == "Anniversary")
                                                else True
                                            ),
                                        )
                            # no events for this day
                            else:
                                # adds date division
                                date = Html("div", day, class_="date", inline=True)
                                # create empty day with date
                                tcell = Html("td", class_=dayclass, inline=True) + (
                                    # adds date division
                                    Html("div", date, class_="empty", inline=True)
                                )
                        # nothing for this month
                        else:
                            tcell = Html("td", class_=dayclass) + (
                                # adds date division
                                Html("div", day, class_="date", inline=True)
                            )

                    # attach table cell to table row
                    # close the day column
                    trow += tcell

                    # change day number
                    current_ord += 1

            if cal == "yg":
                for weeks in range(nweeks, 6):
                    # each calendar must have six weeks for proper styling
                    # and alignment
                    with Html("tr", class_="week%02d" % (weeks + 1)) as six_weeks:
                        tbody += six_weeks

                        for dummy_emptydays in range(7):
                            six_weeks += Html("td", class_="emptyDays", inline=True)

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

        # Number of directory levels up to get to self.html_dir / root
        if self.the_lang:
            nr_up = 2
        else:
            nr_up = 2

        with self.r_user.progress(
            _("Web Calendar Report"), _("Formatting months ..."), 12
        ) as step:
            for month in range(1, 13):
                self.current_month = str(month)
                cal_fname = "cal/%s/%s" % (str(year), str(month))
                open_file, sio = self.report.create_file(cal_fname)

                # Add xml, doctype, meta and stylesheets
                # body has already been added to webcal  already once
                result = self.write_header(self.title_text, cal=nr_up)
                webcal, head, dummy_body, outerwrapper = result

                # Create Month Navigation Menu
                # identify currentsection for proper highlighting
                currentsection = _dd.long_months[month]
                outerwrapper += self.month_navigation(nr_up, year, currentsection)

                # Set the current day background to GreenYellow
                # To do this, we force to load a bad image
                head += CURRENT_DAY
                current_day = Html("img", src="", onerror="CurrentDay()")
                outerwrapper += current_day

                # build the calendar
                content = Html("div", class_="content", id="WebCal")
                outerwrapper += content
                monthly_calendar = self.calendar_build("wc", year, month)
                content += monthly_calendar

                # create blank line for stylesheets
                # create footer division section
                footer = self.write_footer(None, cal=nr_up)
                outerwrapper += (FULLCLEAR, footer)

                # send calendar page to web output
                # and close the file
                self.xhtml_writer(webcal, open_file, sio, 0)

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
            if month == 0:  # why ?
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

        # Number of directory levels up to get to root
        if self.the_lang:
            nr_up = 2
        else:
            nr_up = 2

        # generate progress pass for "Year At A Glance"
        with self.r_user.progress(
            _("Web Calendar Report"), _("Creating Year At A Glance calendar"), 12
        ) as step:
            cal_fname = "cal/%s/fullyearlinked" % str(year)
            open_file, sio = self.report.create_file(cal_fname)

            # page title
            title = self._("%(year)d, At A Glance") % {"year": year}
            self.title_text = self.the_title + " (" + title + ")"
            self.title_str = self.title_text

            # Create page header
            # body has already been added to yearglance  already once
            result = self.write_header(cal_fname, cal=nr_up)
            yearglance, dummy_head, dummy_body, outerwrapper = result

            # Create Month Navigation Menu
            # identify currentsection for proper highlighting
            self.current_month = "0"
            outerwrapper += self.month_navigation(nr_up, year, "fullyearlinked")

            msg = self._(
                "This calendar is meant to give you access "
                "to all your data at a glance compressed into one "
                "page. Clicking on a date will take you to a page "
                "that shows all the events for that date, if there "
                "are any.\n"
            )

            # page description
            content = Html("div", class_="content", id="YearGlance")
            outerwrapper += content

            content += Html("p", msg, id="description")

            sav_cur_fname = self.report.cur_fname
            for month in range(1, 13):
                # build the calendar
                monthly_calendar = self.calendar_build(
                    "yg", year, month, clickable=True
                )
                content += monthly_calendar

                # increase progress bar
                step()

            # create blank line for stylesheets
            # write footer section
            footer = self.write_footer(None, cal=nr_up)
            outerwrapper += (FULLCLEAR, footer)

            # send calendar page to web output
            # and close the file
            self.report.cur_fname = sav_cur_fname
            self.xhtml_writer(yearglance, open_file, sio, 0)

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

        # Number of directory levels up to get to root
        if self.the_lang:
            nr_up = 2
        else:
            nr_up = 2

        # get year and month from event_date for use in this section
        year = event_date.get_year()
        month = event_date.get_month()

        cal_fname = "cal/%s/%s" % (str(year), fname_date)
        one_day_file, sio = self.report.create_file(cal_fname, ext="")

        # page title
        title = self._("One Day Within A Year")
        self.title_text = self.the_title + " (" + title + ")"
        self.title_str = self.title_text

        # Don't create the language menu for holidays.
        # This is to avoid 404 errors.
        for (
            dummy_nyears,
            dummy_date,
            text,
            event,
            dummy_age_at_death,
            dummy_dead_event_date,
        ) in day_list:
            self.not_holiday = False if event == "Holiday" else True

        # create page header
        result = self.write_header(cal_fname, cal=nr_up)
        oneday, dummy_head, dummy_body, outerwrapper = result

        # Create Month Navigation Menu
        # identify currentsection for proper highlighting
        currentsection = _dd.long_months[month]
        outerwrapper += self.month_navigation(nr_up, year, currentsection)

        # set date display as in user preferences
        content = Html("div", class_="content", id="OneDay")
        outerwrapper += content
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
            prevd = Date(int(event[1][:4]), int(event[1][4:6]), int(event[1][6:]))
            my_title = Html("a", "\u276e", href=url, title=self.rlocale.get_date(prevd))
        else:
            my_title = Html("<em>&nbsp;&nbsp;</em>")
        my_title += Html("</a>")
        my_title += "&nbsp;&nbsp;"
        my_title += self.rlocale.date_displayer.display(event_date)
        my_title += "&nbsp;&nbsp;"
        if found[2] is not None:
            url = event[2] + self.ext
            nextd = Date(int(event[2][:4]), int(event[2][4:6]), int(event[2][6:]))
            my_title += Html(
                "a", "\u276f", href=url, title=self.rlocale.get_date(nextd)
            )
        else:
            my_title += Html("<b>&nbsp;&nbsp;</b>")
        content += Html("h3", my_title, inline=True)

        # list the events
        ordered = Html("ol")
        content += ordered
        for (
            dummy_nyears,
            dummy_date,
            text,
            event,
            dummy_age_at_death,
            dummy_dead_event_date,
        ) in day_list:
            ordered += Html(
                "li", text, inline=False if event == "Anniversary" else True
            )

        # create blank line for stylesheets
        # write footer section
        footer = self.write_footer(None, cal=nr_up)
        outerwrapper += (FULLCLEAR, footer)

        # send calendar page to web output
        # and close the file
        self.xhtml_writer(oneday, one_day_file, sio, 0)

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
        db = self.r_db

        with self.r_user.progress(
            _("Web Calendar Report"),
            _("Reading database..."),
            len(self.report.obj_dict[Person]) + 1,
        ) as step:
            for person_handle in sorted(self.report.obj_dict[Person]):
                step()
                person = db.get_person_from_handle(person_handle)

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
                    if birth_date != Date() and birth_date.is_valid() and death_date:
                        age_at_death = death_date - birth_date
                        age_at_death = age_at_death.format(dlocale=self.rlocale)

                # determine birthday information???
                if self.birthday and birth_date is not Date() and birth_date.is_valid():
                    birth_date = gregorian(birth_date)

                    year = birth_date.get_year()
                    month = birth_date.get_month()
                    day = birth_date.get_day()

                    # date to figure if someone is still alive
                    # current year of calendar, month nd day is their birth
                    # month and birth day
                    prob_alive_date = Date(this_year, month, day)
                    month, day = birth_date.anniversary(this_year)
                    # add some things to handle maiden name:
                    father_surname = None  # husband, actually
                    if person.gender == Person.FEMALE:
                        # get husband's last name:
                        if self.maiden_name in ["spouse_first", "spouse_last"]:
                            if family_list:
                                if self.maiden_name == "spouse_first":
                                    fhandle = family_list[0]
                                else:
                                    fhandle = family_list[-1]
                                fam = db.get_family_from_handle(fhandle)
                                father_handle = fam.get_father_handle()
                                mother_handle = fam.get_mother_handle()
                                if mother_handle == person.handle:
                                    if father_handle:
                                        father = db.get_person_from_handle(
                                            father_handle
                                        )
                                        if father is not None:
                                            father_surname = _regular_surname(
                                                person.gender, father.get_primary_name()
                                            )
                    short_name = self.get_name(person, father_surname)
                    alive = probably_alive(person, db, prob_alive_date)
                    if (self.alive and alive) or not self.alive:
                        # add link to NarrativeWeb
                        if self.link_to_narweb:
                            url = self.report.build_url_fname_html(
                                person.handle, "ppl", uplink=False
                            )
                            if self.usecms:
                                sub = ""
                            else:
                                sub = "/".join(([".."] * 2))
                            if sub:
                                url = url.replace("ppl", sub + "/ppl")
                            text = str(Html("a", short_name, href=url))
                        else:
                            text = short_name
                        if age_at_death is None:
                            self.add_day_item(
                                text,
                                year,
                                month,
                                day,
                                "Birthday",
                                age_at_death,
                                birth_date,
                            )
                        else:
                            self.add_day_item(
                                text,
                                year,
                                month,
                                day,
                                "Birthday",
                                age_at_death,
                                person_death,
                            )
                death_event = get_death_or_fallback(db, person)
                if death_event:
                    death_date = death_event.get_date_object()
                else:
                    death_date = None
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
                            hdle = person.handle
                            rbufh = self.report.build_url_fname_html
                            navpfx = rbufh(hdle, "ppl", uplink=False)
                            if self.usecms:
                                sub = ""
                            else:
                                sub = "/".join(([".."] * 2))
                            if sub:
                                navpfx = navpfx.replace("ppl", sub + "/ppl")
                            text = str(Html("a", short_name, href=navpfx))
                        else:
                            text = short_name
                        self.add_day_item(
                            text, year, month, day, "Death", age_at_death, death_date
                        )

                # add anniversary if requested
                if self.anniv:
                    for fhandle in family_list:
                        fam = db.get_family_from_handle(fhandle)
                        father_handle = fam.get_father_handle()
                        mother_handle = fam.get_mother_handle()
                        if father_handle == person.handle:
                            spouse_handle = mother_handle
                        else:
                            continue  # with next person if this was
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
                                        death_ref.ref
                                    )
                                    death_date = death_event.get_date_object()
                                    if death_date != Date() and death_date.is_valid():
                                        spouse_death = death_date
                            first_died = Date()
                            if person_death == Date():
                                first_died = spouse_death
                            elif spouse_death != Date():
                                first_died = (
                                    person_death
                                    if spouse_death > person_death
                                    else spouse_death
                                )
                            else:
                                first_died = person_death

                            # will return a marriage event or False if not
                            # married any longer
                            marriage_event = get_marriage_event(db, fam)
                            if marriage_event:
                                event_date = marriage_event.get_date_object()
                                if event_date is not Date() and event_date.is_valid():
                                    event_date = gregorian(event_date)
                                    year = event_date.get_year()
                                    month = event_date.get_month()
                                    day = event_date.get_day()

                                    month, day = event_date.anniversary(this_year)
                                    # date to figure if someone is still alive
                                    prob_alive_date = Date(this_year, month, day)
                                    wedding_age = None
                                    if first_died != Date():
                                        wedding_age = first_died - event_date
                                        wedding_age = wedding_age.format(
                                            dlocale=self.rlocale
                                        )
                                    divorce_event = get_divorce_event(db, fam)
                                    if divorce_event:
                                        d_date = divorce_event.get_date_object()
                                        if d_date is not Date() and d_date.is_valid():
                                            d_date = gregorian(d_date)
                                            if d_date != Date():
                                                w_age = d_date - event_date
                                                w_age = w_age.format(
                                                    dlocale=self.rlocale
                                                )
                                                wedding_age = w_age
                                                first_died = d_date

                                    if self.link_to_narweb:
                                        href = self.report.build_url_fname_html(
                                            spouse_handle, "ppl", uplink=False
                                        )
                                        if self.usecms:
                                            sub = ""
                                        else:
                                            sub = "/".join(([".."] * 2))
                                        if sub:
                                            href = href.replace("ppl", sub + "/ppl")
                                        spouse_name = str(
                                            Html("a", spouse_name, href=href)
                                        )
                                        href = self.report.build_url_fname_html(
                                            person.handle, "ppl", uplink=False
                                        )
                                        if sub:
                                            href = href.replace("ppl", sub + "/ppl")
                                        short_name = str(
                                            Html("a", short_name, href=href)
                                        )

                                    alive1 = probably_alive(person, db, prob_alive_date)
                                    alive2 = probably_alive(spouse, db, prob_alive_date)
                                    if first_died == Date():
                                        first_died = Date(0, 0, 0)
                                    if (
                                        self.alive and (alive1 or alive2)
                                    ) or not self.alive:
                                        spse = self._("%(spouse)s and" " %(person)s")
                                        text = spse % {
                                            "spouse": spouse_name,
                                            "person": short_name,
                                        }

                                        self.add_day_item(
                                            text,
                                            year,
                                            month,
                                            day,
                                            "Anniversary",
                                            wedding_age,
                                            first_died,
                                        )

    def write_report(self):
        """
        The short method that runs through each month and creates a page.
        """
        # get data from database for birthdays/ anniversaries
        self.collect_data(self.start_year)
        # initialize the holidays dict to fill:
        self.holidays = {}
        self.__get_holidays(self.start_year)

        if self.multiyear:
            # limit number of years to eighteen (18) years and only one row
            # of years
            nyears = (self.end_year - self.start_year) + 1
            num_years = nyears if 0 < nyears < 19 else 18

            for cal_year in range(self.start_year, (self.start_year + num_years)):
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

            # create webcalendar() calendar pages
            self.webcalendar(cal_year)

            # create "Year At A Glance" and
            # "One Day" calendar pages
            if self.fullyear:
                self.year_glance(cal_year)

            self.create_page_index()

    def create_page_index(self):
        """
        Create the page index called by the narrativeweb.
        """
        cal_fname = "cal/%s/index" % str(Today().get_year())
        output_file, sio = self.report.create_file(cal_fname)

        # Create page header
        # body has already been added to yearglance  already once
        result = self.write_header(cal_fname, cal=2)
        index, head, dummy_body, outerwrapper = result

        head += SCRIPT % self.ext

        # create blank line for stylesheets
        # write footer section
        footer = self.write_footer(None, cal=2)
        outerwrapper += (FULLCLEAR, footer)
        outerwrapper += "<script>currentmonth('.');</script>"

        # send calendar page to web output
        # and close the file
        self.xhtml_writer(index, output_file, sio, 0)


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
DOW_GRAMPS2ISO = [
    -1,
    calendar.SUNDAY,
    calendar.MONDAY,
    calendar.TUESDAY,
    calendar.WEDNESDAY,
    calendar.THURSDAY,
    calendar.FRIDAY,
    calendar.SATURDAY,
]


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
    bday_anniv_list = [
        (t, e, d, n, x) for t, e, d, n, x in bday_anniv_list if d != Date.EMPTY
    ]

    # number of years have to be at least zero
    bday_anniv_list = [
        (t, e, d, n, x)
        for t, e, d, n, x in bday_anniv_list
        if (event_date.get_year() - d.get_year()) >= 0
    ]

    # a holiday
    # zero will force holidays to be first in list
    nyears = 0

    for text, event, date, notused, notused in holiday_list:
        day_list.append((nyears, date, text, event, notused, notused))

    # birthday and anniversary list
    for text, event, date, age_at_death, dead_event_date in bday_anniv_list:
        # number of years married, ex: 10
        nyears = event_date.get_year() - date.get_year()

        # number of years for birthday, ex: 10 years
        age_str = event_date - date
        age_str = age_str.format(precision=1, as_age=False, dlocale=rlocale)

        symbols = Symbols()
        death_idx = config.get("utf8.death-symbol")
        death_symbol = symbols.get_death_symbol_for_char(death_idx)

        # a birthday
        if event == "Birthday":
            if age_at_death is not None:
                trans_date = trans_text("Died %(death_date)s.")
                translated_date = rlocale.get_date(dead_event_date)
                mess = trans_date % {"death_date": translated_date}
                age = ", <font size='+1' ><b>%s</b></font> <em>%s (%s)" % (
                    death_symbol,
                    mess,
                    age_at_death,
                )
            else:
                # Translators: expands to smth like "12 years old",
                # where "12 years" is already localized to your language
                age = ", <em>"
                date_y = date.get_year()
                trans_date = trans_text("Born %(birth_date)s.")
                old_date = trans_text("%s old")
                translated_date = rlocale.get_date(dead_event_date)
                age += old_date % (
                    str(age_str)
                    if (date_y != 0)
                    else trans_date % {"birth_date": translated_date}
                )
            txt_str = text + age + "</em>"

        # a death
        if event == "Death":
            txt_str = (
                text
                + ", "
                + death_symbol
                + " <em>"
                + (
                    trans_text("%s since death") % str(age_str)
                    if nyears
                    else trans_text("death")
                )
                + "</em>"
            )

        # an anniversary
        elif event == "Anniversary":
            if nyears == 0:
                txt_str = trans_text("%(couple)s, <em>wedding</em>") % {"couple": text}
            else:
                if age_at_death is not None:
                    age = "%s %s" % (trans_text("Married"), age_at_death)
                    txt_str = "%s, <em>%s" % (text, age)
                    if (
                        isinstance(dead_event_date, Date)
                        and dead_event_date.get_year() > 0
                    ):
                        txt_str += " (" + trans_text("Until") + " "
                        txt_str += rlocale.get_date(dead_event_date)
                        txt_str += ")</em>"
                    else:
                        txt_str += "</em>"
                else:
                    age = "<em>%s" % nyears
                    # Translators: leave all/any {...} untranslated
                    ngettext = rlocale.translation.ngettext
                    txt_str = ngettext(
                        "{couple}, {years} year anniversary",
                        "{couple}, {years} year anniversary",
                        nyears,
                    ).format(couple=text, years=age)
                    txt_str += "</em>"
            txt_str = Html("span", txt_str, class_="yearsmarried")

        day_list.append((nyears, date, txt_str, event, age_at_death, dead_event_date))

    # sort them based on number of years
    # holidays will always be on top of event list
    day_list = sorted(day_list, key=lambda x: (isinstance(x[0], str), x[0]))

    # return to its caller calendar_build()
    return day_list
