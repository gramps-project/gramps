#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007 Donald N. Allingham
# Copyright (C) 2007-2012 Brian G. Matherly
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2012-2016 Paul Franklin
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
Timeline Chart
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.plug.menu import PersonOption, FilterOption, EnumeratedListOption
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    GraphicsStyle,
    FONT_SANS_SERIF,
    DASHED,
    PARA_ALIGN_CENTER,
    IndexMark,
    INDEX_TYPE_TOC,
)
from gramps.gen.sort import Sort
from gramps.gen.config import config
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.lib import Date

# ------------------------------------------------------------------------
#
# private constants
#
# ------------------------------------------------------------------------


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value, context=""):  # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value


# ------------------------------------------------------------------------
#
# Private Functions
#
# ------------------------------------------------------------------------
def _get_sort_functions(sort):
    return [
        (_T_("Birth Date", "sorted by"), sort.by_birthdate_key),
        (_T_("Name", "sorted by"), sort.by_last_name_key),
    ]


# ------------------------------------------------------------------------
#
# TimeLine
#
# ------------------------------------------------------------------------
class TimeLine(Report):
    """TimeLine Report"""

    def __init__(self, database, options, user):
        """
        Create the Timeline object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - instance of gen.user.User()

        This report needs the following parameters (class variables)
        that come in the options class.

        filter    - Filter to be applied to the people of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        sortby        - Sorting method to be used.
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)
        self._user = user
        menu = options.menu

        self.set_locale(options.menu.get_option_by_name("trans").get_value())

        stdoptions.run_private_data_option(self, menu)
        living_opt = stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        self.filter = menu.get_option_by_name("filter").get_filter()
        self.fil_name = "(%s)" % self.filter.get_name(self._locale)

        living_value = menu.get_option_by_name("living_people").get_value()
        for value, description in living_opt.get_items(xml_items=True):
            if value == living_value:
                living_desc = self._(description)
                break
        self.living_desc = self._("(Living people: %(option_name)s)") % {
            "option_name": living_desc
        }

        stdoptions.run_name_format_option(self, menu)

        sort_func_num = menu.get_option_by_name("sortby").get_value()
        sort_functions = _get_sort_functions(Sort(self.database))
        self.sort_name = self._(sort_functions[sort_func_num][0])
        self.sort_func = sort_functions[sort_func_num][1]
        self.calendar = config.get("preferences.calendar-format-report")
        self.plist = []
        self.header = 2.6

    def write_report(self):
        # Apply the filter
        self.plist = self.filter.apply(
            self.database, self.database.iter_person_handles(), user=self._user
        )

        # Find the range of dates to include
        (low, high) = self.find_year_range()

        # Generate the actual timeline
        self.generate_timeline(low, high)

    def generate_timeline(self, low, high):
        """generate the timeline"""
        st_size = self.name_size()
        style_sheet = self.doc.get_style_sheet()
        font = style_sheet.get_paragraph_style("TLG-Name").get_font()
        incr = utils.pt2cm(font.get_size())
        pad = incr * 0.75
        _x1, _x2, _y1, _y2 = (0, 0, 0, 0)
        start = st_size + 0.5
        stop = self.doc.get_usable_width() - 0.5
        size = stop - start
        self.header = 2.6

        # Sort the people as requested
        with self._user.progress(_("Timeline"), _("Sorting dates..."), 0) as step:
            self.plist.sort(key=self.sort_func)

        self.doc.start_page()
        self.build_grid(low, high, start, stop, True)

        index = 1
        current = 1

        length = len(self.plist)

        with self._user.progress(
            _("Timeline"), _("Calculating timeline..."), length
        ) as step:
            for p_id in self.plist:
                person = self.database.get_person_from_handle(p_id)
                birth = get_birth_or_fallback(self.database, person)
                if birth:
                    bth = birth.get_date_object()
                    bth = bth.to_calendar(self.calendar).get_year()
                else:
                    bth = None

                death = get_death_or_fallback(self.database, person)
                if death:
                    dth = death.get_date_object()
                    dth = dth.to_calendar(self.calendar).get_year()
                else:
                    dth = None

                dname = self._name_display.display(person)
                mark = utils.get_person_mark(self.database, person)
                self.doc.draw_text(
                    "TLG-text",
                    dname,
                    incr + pad,
                    self.header + (incr + pad) * index,
                    mark,
                )

                _y1 = self.header + (pad + incr) * index
                _y2 = self.header + ((pad + incr) * index) + incr
                _y3 = (_y1 + _y2) / 2.0
                w05 = 0.05

                if bth:
                    start_offset = (float(bth - low) / float(high - low)) * size
                    _x1 = start + start_offset
                    path = [(_x1, _y1), (_x1 + w05, _y3), (_x1, _y2), (_x1 - w05, _y3)]
                    self.doc.draw_path("TLG-line", path)

                if dth:
                    start_offset = (float(dth - low) / float(high - low)) * size
                    _x1 = start + start_offset
                    path = [(_x1, _y1), (_x1 + w05, _y3), (_x1, _y2), (_x1 - w05, _y3)]
                    self.doc.draw_path("TLG-solid", path)

                if bth and dth:
                    start_offset = ((float(bth - low) / float(high - low)) * size) + w05
                    stop_offset = ((float(dth - low) / float(high - low)) * size) - w05

                    _x1 = start + start_offset
                    _x2 = start + stop_offset
                    self.doc.draw_line("open", _x1, _y3, _x2, _y3)

                if (_y2 + incr) >= self.doc.get_usable_height():
                    if current != length:
                        self.doc.end_page()
                        self.doc.start_page()
                        self.build_grid(low, high, start, stop)
                    index = 1
                    _x1, _x2, _y1, _y2 = (0, 0, 0, 0)
                else:
                    index += 1
                current += 1
                step()
            self.doc.end_page()

    def build_grid(self, year_low, year_high, start_pos, stop_pos, toc=False):
        """
        Draws the grid outline for the chart. Sets the document label,
        draws the vertical lines, and adds the year labels. Arguments
        are:

        year_low  - lowest year on the chart
        year_high - highest year on the chart
        start_pos - x position of the lowest leftmost grid line
        stop_pos  - x position of the rightmost grid line
        """
        self.draw_title(toc)
        self.draw_columns(start_pos, stop_pos)
        if year_high is not None and year_low is not None:
            self.draw_year_headings(year_low, year_high, start_pos, stop_pos)
        else:
            self.draw_no_date_heading()

    def draw_columns(self, start_pos, stop_pos):
        """
        Draws the columns out of vertical lines.

        start_pos - x position of the lowest leftmost grid line
        stop_pos  - x position of the rightmost grid line
        """
        top_y = self.header
        bottom_y = self.doc.get_usable_height()
        delta = (stop_pos - start_pos) / 5
        for val in range(0, 6):
            xpos = start_pos + (val * delta)
            self.doc.draw_line("TLG-grid", xpos, top_y, xpos, bottom_y)

    def draw_title(self, toc):
        """
        Draws the title for the page.
        """
        width = self.doc.get_usable_width()
        title = "%(str1)s -- %(str2)s" % {
            "str1": self._("Timeline Chart"),
            # feature request 2356: avoid genitive form
            "str2": self._("Sorted by %s") % self.sort_name,
        }
        title3 = self.living_desc
        mark = None
        if toc:
            mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.center_text("TLG-title", title, width / 2.0, 0, mark)
        style_sheet = self.doc.get_style_sheet()
        title_font = style_sheet.get_paragraph_style("TLG-Title").get_font()
        title_y = 1.2 - (utils.pt2cm(title_font.get_size()) * 1.2)
        self.doc.center_text("TLG-title", self.fil_name, width / 2.0, title_y)
        title_y = 1.8 - (utils.pt2cm(title_font.get_size()) * 1.2)
        self.doc.center_text("TLG-title", title3, width / 2.0, title_y)

    def draw_year_headings(self, year_low, year_high, start_pos, stop_pos):
        """
        Draws the column headings (years) for the page.
        """
        style_sheet = self.doc.get_style_sheet()
        label_font = style_sheet.get_paragraph_style("TLG-Label").get_font()
        label_y = self.header - (utils.pt2cm(label_font.get_size()) * 1.2)
        incr = (year_high - year_low) / 5
        delta = (stop_pos - start_pos) / 5
        for val in range(0, 6):
            xpos = start_pos + (val * delta)
            year_str = self._get_date(Date(year_low + int(incr * val)))
            self.doc.center_text("TLG-label", year_str, xpos, label_y)

    def draw_no_date_heading(self):
        """
        Draws a single heading that says "No Date Information"
        """
        width = self.doc.get_usable_width()
        style_sheet = self.doc.get_style_sheet()
        label_font = style_sheet.get_paragraph_style("TLG-Label").get_font()
        label_y = self.header - (utils.pt2cm(label_font.get_size()) * 1.2)
        self.doc.center_text(
            "TLG-label", self._("No Date Information"), width / 2.0, label_y
        )

    def find_year_range(self):
        """
        Finds the range of years that will be displayed on the chart.

        Returns a tuple of low and high years. If no dates are found, the
        function returns (None, None).
        """
        low = None
        high = None

        def min_max_year(low, high, year):
            """convenience function"""
            if year is not None and year != 0:
                if low is not None:
                    low = min(low, year)
                else:
                    low = year
                if high is not None:
                    high = max(high, year)
                else:
                    high = year
            return (low, high)

        with self._user.progress(
            _("Timeline"), _("Finding date range..."), len(self.plist)
        ) as step:
            for p_id in self.plist:
                person = self.database.get_person_from_handle(p_id)
                birth = get_birth_or_fallback(self.database, person)
                if birth:
                    bth = birth.get_date_object()
                    bth = bth.to_calendar(self.calendar).get_year()
                    (low, high) = min_max_year(low, high, bth)

                death = get_death_or_fallback(self.database, person)
                if death:
                    dth = death.get_date_object()
                    dth = dth.to_calendar(self.calendar).get_year()
                    (low, high) = min_max_year(low, high, dth)
                step()

            # round the dates to the nearest decade
            if low is not None:
                low = int((low / 10)) * 10
            else:
                low = high

            if high is not None:
                high = int(((high + 9) / 10)) * 10
            else:
                high = low

            # Make sure the difference is a multiple of 50 so
            # all year ranges land on a decade.
            if low is not None and high is not None:
                low -= 50 - ((high - low) % 50)

        return (low, high)

    def name_size(self):
        """get the length of the name"""
        self.plist = self.filter.apply(
            self.database, self.database.iter_person_handles(), user=self._user
        )

        style_sheet = self.doc.get_style_sheet()
        gstyle = style_sheet.get_draw_style("TLG-text")
        pname = gstyle.get_paragraph_style()
        pstyle = style_sheet.get_paragraph_style(pname)
        font = pstyle.get_font()

        size = 0
        for p_id in self.plist:
            person = self.database.get_person_from_handle(p_id)
            dname = self._name_display.display(person)
            size = max(self.doc.string_width(font, dname), size)
        return utils.pt2cm(size)


# ------------------------------------------------------------------------
#
# TimeLineOptions
#
# ------------------------------------------------------------------------
class TimeLineOptions(MenuReportOptions):
    """Options for the TimeLine Report"""

    def __init__(self, name, dbase):
        self.__pid = None
        self.__filter = None
        self.__db = dbase
        self._nf = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        return self.__filter.get_filter().get_name()

    def add_menu_options(self, menu):
        category_name = _("Report Options")

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(_("Determines what people are included in the report"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect("value-changed", self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect("value-changed", self.__update_filters)

        sortby = EnumeratedListOption(_("Sort by"), 0)
        idx = 0
        for item in _get_sort_functions(Sort(self.__db)):
            sortby.add_item(idx, _(item[0]))
            idx += 1
        sortby.set_help(_("Sorting method to use"))
        menu.add_option(category_name, "sortby", sortby)

        category_name = _("Report Options (2)")

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect("value-changed", self.__update_filters)

        self.__update_filters()

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        stdoptions.add_localization_option(menu, category_name)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = utils.get_person_filters(
            person, include_single=False, name_format=nfv
        )
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 0:  # "Entire Database" (as "include_single=False")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

    def make_default_style(self, default_style):
        """Make the default output style for the Timeline report."""
        # Paragraph Styles
        fstyle = FontStyle()
        fstyle.set_size(10)
        fstyle.set_type_face(FONT_SANS_SERIF)
        pstyle = ParagraphStyle()
        pstyle.set_font(fstyle)
        pstyle.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("TLG-Name", pstyle)

        fstyle = FontStyle()
        fstyle.set_size(8)
        fstyle.set_type_face(FONT_SANS_SERIF)
        pstyle = ParagraphStyle()
        pstyle.set_font(fstyle)
        pstyle.set_alignment(PARA_ALIGN_CENTER)
        pstyle.set_description(_("The style used for the section headers."))
        default_style.add_paragraph_style("TLG-Label", pstyle)

        fstyle = FontStyle()
        fstyle.set_size(14)
        fstyle.set_type_face(FONT_SANS_SERIF)
        pstyle = ParagraphStyle()
        pstyle.set_font(fstyle)
        pstyle.set_alignment(PARA_ALIGN_CENTER)
        pstyle.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("TLG-Title", pstyle)

        """
        Graphic Styles
            TLG-grid  - 0.5pt wide line dashed line. Used for the lines that
                        make up the grid.
            TLG-line  - 0.5pt wide line. Used for the line connecting two
                        endpoints and for the birth marker.
            TLG-solid - 0.5pt line with a black fill color. Used for the date of
                        death marker.
            TLG-text  - Contains the TLG-Name paragraph style used for the
                        individual's name.
            TLG-title - Contains the TLG-Title paragraph style used for the
                        title of the document.
            TLG-label - Contains the TLG-Label paragraph style used for the year
                        label's in the document.
        """
        gstyle = GraphicsStyle()
        gstyle.set_line_width(0.5)
        gstyle.set_color((0, 0, 0))
        default_style.add_draw_style("TLG-line", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_line_width(0.5)
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((0, 0, 0))
        default_style.add_draw_style("TLG-solid", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_line_width(0.5)
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        default_style.add_draw_style("open", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_line_width(0.5)
        gstyle.set_line_style(DASHED)
        gstyle.set_color((0, 0, 0))
        default_style.add_draw_style("TLG-grid", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("TLG-Name")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("TLG-text", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("TLG-Title")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("TLG-title", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("TLG-Label")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("TLG-label", gstyle)
