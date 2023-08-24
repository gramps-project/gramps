#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006 Donald N. Allingham
# Copyright (C) 2007-2012 Brian G. Matherly
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2012-2014 Paul Franklin
# Copyright (C) 2012      Nicolas Adenis-Lamarre
# Copyright (C) 2012      Benny Malengier
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

""" fanchart report """

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
from math import pi, cos, sin, log10, acos, asin, degrees, radians


def log2(val):
    """
    Calculate the log base 2 of a value.
    """
    return int(log10(val) / log10(2))


# ------------------------------------------------------------------------
#
# gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    GraphicsStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
    IndexMark,
    INDEX_TYPE_TOC,
)
from gramps.gen.plug.menu import (
    EnumeratedListOption,
    NumberOption,
    PersonOption,
    BooleanOption,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.config import config
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.lib import EventType, Date
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.name import displayer as _nd

# ------------------------------------------------------------------------
#
# private constants
#
# ------------------------------------------------------------------------
FULL_CIRCLE = 0
HALF_CIRCLE = 1
QUAR_CIRCLE = 2
OVERHANG = 3

BACKGROUND_WHITE = 0
BACKGROUND_GEN = 1

RADIAL_UPRIGHT = 0
RADIAL_ROUNDABOUT = 1

# minor offset just usefull for generation 11,
# to not a bit offset between the text and the polygon
# this can be considered as a bad hack
WEDGE_TEXT_BARRE_OFFSET = 0.0016


# ------------------------------------------------------------------------
#
# private functions
#
# ------------------------------------------------------------------------
def draw_wedge(
    doc,
    style,
    centerx,
    centery,
    radius,
    start_angle,
    end_angle,
    do_rendering,
    short_radius=0,
):
    """
    Draw a wedge shape.
    """
    while end_angle < start_angle:
        end_angle += 360

    path = []

    radiansdelta = radians(0.5)
    sangle = radians(start_angle)
    eangle = radians(end_angle)
    while eangle < sangle:
        eangle = eangle + 2 * pi
    angle = sangle

    if short_radius == 0:
        if (end_angle - start_angle) != 360:
            path.append((centerx, centery))
    else:
        origx = centerx + cos(angle) * short_radius
        origy = centery + sin(angle) * short_radius
        path.append((origx, origy))

    while angle < eangle:
        _x_ = centerx + cos(angle) * radius
        _y_ = centery + sin(angle) * radius
        path.append((_x_, _y_))
        angle = angle + radiansdelta
    _x_ = centerx + cos(eangle) * radius
    _y_ = centery + sin(eangle) * radius
    path.append((_x_, _y_))

    if short_radius:
        _x_ = centerx + cos(eangle) * short_radius
        _y_ = centery + sin(eangle) * short_radius
        path.append((_x_, _y_))

        angle = eangle
        while angle >= sangle:
            _x_ = centerx + cos(angle) * short_radius
            _y_ = centery + sin(angle) * short_radius
            path.append((_x_, _y_))
            angle -= radiansdelta
    if do_rendering:
        doc.draw_path(style, path)

    delta = (eangle - sangle) / 2.0
    rad = short_radius + (radius - short_radius) / 2.0

    return (
        (centerx + cos(sangle + delta + WEDGE_TEXT_BARRE_OFFSET) * rad),
        (centery + sin(sangle + delta + WEDGE_TEXT_BARRE_OFFSET) * rad),
    )


# ------------------------------------------------------------------------
#
# FanChart
#
# ------------------------------------------------------------------------
class FanChart(Report):
    def __init__(self, database, options, user):
        """
        Create the FanChart object that produces the report.

        The arguments are:

        database     - the Gramps database instance
        options      - instance of the Options class for this report
        user         - a gen.user.User instance

        This report needs the following parameters (class variables)
        that come in the options class.

        maxgen       - Maximum number of generations to include.
        circle       - Draw a full circle, half circle, half circle with
                       overhang or quarter circle.
        background   - Background color is generation dependent or white.
        radial       - Print radial texts roundabout or as upright as possible.
        draw_empty   - draw background when there is no information
        same_style   - use the same style for all generation
        flip_text    - flip names that are on the bottom half of the fan
        incl_private - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """

        Report.__init__(self, database, options, user)

        menu = options.menu

        self.set_locale(options.menu.get_option_by_name("trans").get_value())

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        self.max_generations = menu.get_option_by_name("maxgen").get_value()
        self.circle = menu.get_option_by_name("circle").get_value()
        self.background = menu.get_option_by_name("background").get_value()
        self.radial = menu.get_option_by_name("radial").get_value()
        pid = menu.get_option_by_name("pid").get_value()
        self.draw_empty = menu.get_option_by_name("draw_empty").get_value()
        self.same_style = menu.get_option_by_name("same_style").get_value()
        self.flip_text = menu.get_option_by_name("flip_text").get_value()
        self.exclude_title = menu.get_option_by_name("exclude_title").get_value()
        self.center_person = self.database.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        self.graphic_style = []
        self.text_style = []
        for i in range(0, self.max_generations):
            self.graphic_style.append("FC-Graphic" + "%02d" % i)
            self.text_style.append("FC-Text" + "%02d" % i)

        self.calendar = 0

        self.height = 0
        self.map = [None] * 2**self.max_generations
        self.text = {}

    def apply_filter(self, person_handle, index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of
        generations that we want to deal with"""

        if (not person_handle) or (index >= 2**self.max_generations):
            return
        self.map[index - 1] = person_handle
        self.text[index - 1] = self.get_info(person_handle, log2(index))

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(), index * 2)
            self.apply_filter(family.get_mother_handle(), (index * 2) + 1)

    def write_report(self):
        self.doc.start_page()

        self.apply_filter(self.center_person.get_handle(), 1)
        p_rn = self.center_person.get_primary_name().get_regular_name()

        chart_height = self.doc.get_usable_height()
        if self.exclude_title:
            title = ""
            title_nb_lines = 0
            title_height = 0
        else:
            # choose one line or two lines translation according to the width
            title = self._("%(generations)d Generation Fan Chart " "for %(person)s") % {
                "generations": self.max_generations,
                "person": p_rn,
            }
            title_nb_lines = 1
            title_height = 0
            style_sheet = self.doc.get_style_sheet()
            if style_sheet:
                p_style = style_sheet.get_paragraph_style("FC-Title")
                if p_style:
                    font = p_style.get_font()
                    if font:
                        title_width = utils.pt2cm(self.doc.string_width(font, title))
                        if title_width > self.doc.get_usable_width():
                            title = self._(
                                "%(generations)d Generation Fan Chart "
                                "for\n%(person)s"
                            ) % {"generations": self.max_generations, "person": p_rn}
                            title_nb_lines = 2
                        fontsize = utils.pt2cm(font.get_size())
                        title_height = fontsize * title_nb_lines * 1.5
            chart_height -= title_height

        if self.circle == FULL_CIRCLE:
            max_angle = 360.0
            start_angle = 90
            max_circular = 5
            _x_ = self.doc.get_usable_width() / 2.0
            _y_ = chart_height / 2.0
            min_xy = min(_x_, _y_)

        elif self.circle == HALF_CIRCLE:
            max_angle = 180.0
            start_angle = 180
            max_circular = 3
            _x_ = self.doc.get_usable_width() / 2.0
            _y_ = chart_height
            min_xy = min(_x_, _y_)

        elif self.circle == OVERHANG:
            if (
                chart_height < self.doc.get_usable_width()
                and chart_height > self.doc.get_usable_width() / 2
            ):
                # Determine overhang angle to fill the paper
                radius = self.doc.get_usable_width() / 2
                _overhang_height_ = chart_height - radius
                overhang_angle = degrees(asin(_overhang_height_ / radius))
            else:
                overhang_angle = 25.0
            max_angle = 180 + 2 * overhang_angle
            start_angle = 180 - overhang_angle
            max_circular = 3
            _x_ = self.doc.get_usable_width() / 2.0
            _overhang_height_ = sin(radians(overhang_angle)) * _x_
            _y_ = chart_height - _overhang_height_
            min_xy = min(_x_, _y_)

        else:  # quarter circle
            max_angle = 90.0
            start_angle = 270
            max_circular = 2
            _x_ = 0
            _y_ = chart_height
            min_xy = min(self.doc.get_usable_width(), _y_)

        if self.max_generations > max_circular:
            block_size = min_xy / (self.max_generations * 2 - max_circular)
        else:
            block_size = min_xy / self.max_generations

        # adaptation of the fonts (title and others)
        optimized_style_sheet = self.get_optimized_style_sheet(
            title,
            max_circular,
            block_size,
            self.same_style,
            not self.same_style,
            # if same_style, use default generated colors
            self.background == BACKGROUND_WHITE,
        )

        if optimized_style_sheet:
            self.doc.set_style_sheet(optimized_style_sheet)

        # title
        if title_height:
            mark = IndexMark(title, INDEX_TYPE_TOC, 1)
            titlex = self.doc.get_usable_width() / 2
            titley = 0
            self.doc.center_text("FC-Graphic-title", title, titlex, titley, mark)
            _y_ += title_height

        # wheel
        for generation in range(0, min(max_circular, self.max_generations)):
            self.draw_circular(_x_, _y_, start_angle, max_angle, block_size, generation)
        for generation in range(max_circular, self.max_generations):
            self.draw_radial(_x_, _y_, start_angle, max_angle, block_size, generation)
        self.doc.end_page()

    def get_info(self, person_handle, generation):
        """get info about a person"""
        person = self.database.get_person_from_handle(person_handle)
        p_pn = person.get_primary_name()
        self.calendar = config.get("preferences.calendar-format-report")

        birth = get_birth_or_fallback(self.database, person)
        bth = ""
        if birth:
            bth = birth.get_date_object()
            bth = self._get_date(
                Date(bth.to_calendar(self.calendar).get_year())
            )  # localized
            if bth == 0:
                bth = ""
            elif birth.get_type() != EventType.BIRTH:
                bth += "*"

        death = get_death_or_fallback(self.database, person)
        dth = ""
        if death:
            dth = death.get_date_object()
            dth = self._get_date(
                Date(dth.to_calendar(self.calendar).get_year())
            )  # localized
            if dth == 0:
                dth = ""
            elif death.get_type() != EventType.DEATH:
                dth += "*"
        if bth and dth:
            val = "%s - %s" % (str(bth), str(dth))
        elif bth:
            val = "* %s" % (str(bth))
        elif dth:
            val = "+ %s" % (str(dth))
        else:
            val = ""

        if generation > 7:
            if (p_pn.get_first_name() != "") and (p_pn.get_surname() != ""):
                name = p_pn.get_first_name() + " " + p_pn.get_surname()
            else:
                name = p_pn.get_first_name() + p_pn.get_surname()
            if (name != "") and (val != ""):
                string = name + self._(", ") + val  # Arabic OK
            else:
                string = name + val
            return [string]
        elif generation == 7:
            if (p_pn.get_first_name() != "") and (p_pn.get_surname() != ""):
                name = p_pn.get_first_name() + " " + p_pn.get_surname()
            else:
                name = p_pn.get_first_name() + p_pn.get_surname()

            if self.circle == FULL_CIRCLE:
                return [name, val]
            elif self.circle in (HALF_CIRCLE, OVERHANG):
                return [name, val]
            else:
                if (name != "") and (val != ""):
                    string = name + self._(", ") + val  # Arabic OK
                else:
                    string = name + val
                return [string]
        elif generation == 6:
            if self.circle == FULL_CIRCLE:
                return [p_pn.get_first_name(), p_pn.get_surname(), val]
            elif self.circle in (HALF_CIRCLE, OVERHANG):
                return [p_pn.get_first_name(), p_pn.get_surname(), val]
            else:
                if (p_pn.get_first_name() != "") and (p_pn.get_surname() != ""):
                    name = p_pn.get_first_name() + " " + p_pn.get_surname()
                else:
                    name = p_pn.get_first_name() + p_pn.get_surname()
                return [name, val]
        else:
            return [p_pn.get_first_name(), p_pn.get_surname(), val]

    def get_max_width_for_circles(self, rad1, rad2, max_centering_proportion):
        r"""
        (the "r" in the above line is to keep pylint happy)
           __
          /__\ <- compute the line width which is drawable between 2 circles.
         /  _ \   max_centering_proportion : 0, touching the circle1, 1,
        |  |_| |   touching the circle2, 0.5 : middle between the 2 circles
        |      |
         \    /
          \__/
                 basically, max_centering_proportion is
                 max_centering_proportion/nb_lines
        """
        # radius at the center of the 2 circles
        rmid = rad2 - (rad2 - rad1) * max_centering_proportion
        return sin(acos(rmid / rad2)) * rad2 * 2

    def get_max_width_for_circles_line(
        self, rad1, rad2, line, nb_lines, centering=False
    ):
        r"""
        (the "r" in the above line is to keep pylint happy)
           __
          /__\ <- compute the line width which is drawable between 2 circles.
         /  _ \   instead of a max_centering_proportion, you get a
        |  |_| |  line/nb_lines position.  (we suppose that lines have the
        |      |  same heights.) for example, if you've 2 lines to draw,
         \    /   line 2 max width is at the 2/3 between the 2 circles
          \__/
        """
        if centering:
            return self.get_max_width_for_circles(rad1, rad2, 1.0)
        else:
            return self.get_max_width_for_circles(
                rad1, rad2, line / float(nb_lines + 1)
            )

    def get_optimized_font_size_for_text(self, rad1, rad2, text, font, centering=False):
        """
        a text can be several lines
        find the font size equals or lower than font.get_size() which fit
        between rad1 and rad2 to display the text.
        centering is a special case when you've the full circle
        available to draw the text in the middle of it
        """
        min_font_size = font.get_size()
        i = 1
        nb_lines = len(text)
        for line in text:
            font_size = self.get_optimized_font_size(
                line,
                font,
                self.get_max_width_for_circles_line(rad1, rad2, i, nb_lines, centering),
            )
            i += 1
            if min_font_size > font_size:
                min_font_size = font_size
        return min_font_size

    def get_optimized_font_size(self, line, font, max_width):
        """
        for a given width, guess the best font size which is equals
        or smaller than font which make line fit into max_width
        """
        test_font = FontStyle(font)
        width = utils.pt2cm(self.doc.string_width(test_font, line))
        while width > max_width and test_font.get_size() > 1:
            test_font.set_size(test_font.get_size() - 1)
            width = utils.pt2cm(self.doc.string_width(test_font, line))
        return test_font.get_size()

    def get_optimized_style_sheet(
        self,
        title,
        max_circular,
        block_size,
        map_style_from_single,
        map_paragraphs_colors_to_graphics,
        make_background_white,
    ):
        """
        returns an optimized (modified) style sheet which make fanchart
        look nicer
        """
        new_style_sheet = self.doc.get_style_sheet()
        if not new_style_sheet:
            return self.doc.get_style_sheet()

        # update title font size
        pstyle_name = "FC-Title"
        p_style = new_style_sheet.get_paragraph_style(pstyle_name)
        if p_style:
            title_font = p_style.get_font()
            if title_font:
                title_width = utils.pt2cm(
                    self.doc.string_multiline_width(title_font, title)
                )
                while (
                    title_width > self.doc.get_usable_width()
                    and title_font.get_size() > 1
                ):
                    title_font.set_size(title_font.get_size() - 1)
                    title_width = utils.pt2cm(
                        self.doc.string_multiline_width(title_font, title)
                    )
                new_style_sheet.add_paragraph_style(pstyle_name, p_style)

        # biggest font allowed is the one of the fist generation, after,
        # always lower than the previous one
        p_style = new_style_sheet.get_paragraph_style(self.text_style[0])
        font = None
        if p_style:
            font = p_style.get_font()
        if font:
            previous_generation_font_size = font.get_size()

            for generation in range(0, self.max_generations):
                gstyle_name = self.graphic_style[generation]
                pstyle_name = self.text_style[generation]
                g_style = new_style_sheet.get_draw_style(gstyle_name)

                # p_style is a copy of 'FC-Text' - use different style
                # to be able to auto change some fonts for some generations
                if map_style_from_single:
                    p_style = new_style_sheet.get_paragraph_style("FC-Text")
                else:
                    p_style = new_style_sheet.get_paragraph_style(pstyle_name)

                if g_style and p_style:
                    # set graphic colors to paragraph colors,
                    # while it's functionnaly
                    # the same for fanchart or make backgrounds white
                    if make_background_white:
                        g_style.set_fill_color((255, 255, 255))
                        new_style_sheet.add_draw_style(gstyle_name, g_style)
                    elif map_paragraphs_colors_to_graphics:
                        pstyle = new_style_sheet.get_paragraph_style(pstyle_name)
                        if pstyle:
                            g_style.set_fill_color(pstyle.get_background_color())
                            new_style_sheet.add_draw_style(gstyle_name, g_style)

                    # adapt font size if too big
                    segments = 2**generation
                    if generation < min(max_circular, self.max_generations):
                        # adpatation for circular fonts
                        rad1, rad2 = self.get_circular_radius(
                            block_size, generation, self.circle
                        )
                        font = p_style.get_font()
                        if font:
                            min_font_size = font.get_size()
                            # find the smallest font required
                            for index in range(segments - 1, 2 * segments - 1):
                                if self.map[index]:
                                    font_size = self.get_optimized_font_size_for_text(
                                        rad1,
                                        rad2,
                                        self.text[index],
                                        p_style.get_font(),
                                        (
                                            self.circle == FULL_CIRCLE
                                            and generation == 0
                                        ),
                                    )
                                if font_size < min_font_size:
                                    min_font_size = font_size
                            font.set_size(
                                min(previous_generation_font_size, min_font_size)
                            )
                    else:
                        # adaptation for radial fonts

                        # find the largest string for the generation
                        longest_line = ""
                        longest_width = 0
                        for index in range(segments - 1, 2 * segments - 1):
                            if self.map[index]:
                                for line in self.text[index]:
                                    width = utils.pt2cm(
                                        self.doc.string_multiline_width(
                                            p_style.get_font(), line
                                        )
                                    )
                                    if width > longest_width:
                                        longest_line = line
                                        longest_width = width

                        # determine maximum width allowed for this generation
                        rad1, rad2 = self.get_radial_radius(
                            block_size, generation, self.circle
                        )
                        max_width = rad2 - rad1

                        # reduce the font so that longest_width
                        # fit into max_width
                        font = p_style.get_font()
                        if font:
                            font.set_size(
                                min(
                                    previous_generation_font_size,
                                    self.get_optimized_font_size(
                                        longest_line, p_style.get_font(), max_width
                                    ),
                                )
                            )

                    # redefine the style
                    new_style_sheet.add_paragraph_style(pstyle_name, p_style)
                    font = p_style.get_font()
        if font:
            previous_generation_font_size = font.get_size()

        # finished
        return new_style_sheet

    def draw_circular(self, _x_, _y_, start_angle, max_angle, size, generation):
        segments = 2**generation
        delta = max_angle / segments
        end_angle = start_angle
        text_angle = start_angle - 270 + (delta / 2.0)
        rad1, rad2 = self.get_circular_radius(size, generation, self.circle)
        graphic_style = self.graphic_style[generation]

        for index in range(segments - 1, 2 * segments - 1):
            start_angle = end_angle
            end_angle = start_angle + delta
            (_xc, _yc) = draw_wedge(
                self.doc,
                graphic_style,
                _x_,
                _y_,
                rad2,
                start_angle,
                end_angle,
                self.map[index] or self.draw_empty,
                rad1,
            )
            if self.map[index]:
                if (generation == 0) and self.circle == FULL_CIRCLE:
                    _yc = _y_
                person = self.database.get_person_from_handle(self.map[index])
                mark = utils.get_person_mark(self.database, person)

                if (
                    self.flip_text == True
                    and generation >= 2
                    and (
                        start_angle >= 360 or (start_angle >= 90 and start_angle < 180)
                    )
                ):
                    self.doc.rotate_text(
                        graphic_style,
                        self.text[index],
                        _xc,
                        _yc,
                        text_angle + 180,
                        mark,
                    )
                else:
                    self.doc.rotate_text(
                        graphic_style, self.text[index], _xc, _yc, text_angle, mark
                    )
            text_angle += delta

    def get_radial_radius(self, size, generation, circle):
        """determine the radius"""
        if circle == FULL_CIRCLE:
            rad1 = size * ((generation * 2) - 5)
            rad2 = size * ((generation * 2) - 3)
        elif circle in (HALF_CIRCLE, OVERHANG):
            rad1 = size * ((generation * 2) - 3)
            rad2 = size * ((generation * 2) - 1)
        else:  # quarter circle
            rad1 = size * ((generation * 2) - 2)
            rad2 = size * (generation * 2)
        return rad1, rad2

    def get_circular_radius(self, size, generation, circle):
        """determine the radius"""
        return size * generation, size * (generation + 1)

    def draw_radial(self, _x_, _y_, start_angle, max_angle, size, generation):
        segments = 2**generation
        delta = max_angle / segments
        end_angle = start_angle
        text_angle = start_angle - delta / 2.0
        graphic_style = self.graphic_style[generation]

        rad1, rad2 = self.get_radial_radius(size, generation, self.circle)
        for index in range(segments - 1, 2 * segments - 1):
            start_angle = end_angle
            end_angle = start_angle + delta
            (_xc, _yc) = draw_wedge(
                self.doc,
                graphic_style,
                _x_,
                _y_,
                rad2,
                start_angle,
                end_angle,
                self.map[index] or self.draw_empty,
                rad1,
            )
            text_angle += delta
            if self.map[index]:
                person = self.database.get_person_from_handle(self.map[index])
                mark = utils.get_person_mark(self.database, person)
                if (
                    self.radial == RADIAL_UPRIGHT
                    and (start_angle >= 90)
                    and (start_angle < 270)
                ):
                    self.doc.rotate_text(
                        graphic_style,
                        self.text[index],
                        _xc,
                        _yc,
                        text_angle + 180,
                        mark,
                    )
                else:
                    self.doc.rotate_text(
                        graphic_style, self.text[index], _xc, _yc, text_angle, mark
                    )


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class FanChartOptions(MenuReportOptions):
    """options for fanchart report"""

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.max_generations = 11
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        return _nd.display(person)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the fan chart.
        """
        category_name = _("Report Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)

        max_gen = NumberOption(_("Generations"), 5, 1, self.max_generations)
        max_gen.set_help(_("The number of generations " "to include in the report"))
        menu.add_option(category_name, "maxgen", max_gen)

        circle = EnumeratedListOption(_("Type of graph"), HALF_CIRCLE)
        circle.add_item(FULL_CIRCLE, _("full circle"))
        circle.add_item(HALF_CIRCLE, _("half circle"))
        circle.add_item(OVERHANG, _("overhang"))
        circle.add_item(QUAR_CIRCLE, _("quarter circle"))
        circle.set_help(
            _(
                "The form of the graph: full circle, half circle,"
                " half circle with overhang or quarter circle."
            )
        )
        menu.add_option(category_name, "circle", circle)

        background = EnumeratedListOption(_("Background color"), BACKGROUND_GEN)
        background.add_item(BACKGROUND_WHITE, _("white"))
        background.add_item(BACKGROUND_GEN, _("generation dependent"))
        background.set_help(
            _("Background color is either white or generation" " dependent")
        )
        menu.add_option(category_name, "background", background)

        radial = EnumeratedListOption(_("Orientation of radial texts"), RADIAL_UPRIGHT)
        radial.add_item(RADIAL_UPRIGHT, _("upright"))
        radial.add_item(RADIAL_ROUNDABOUT, _("roundabout"))
        radial.set_help(_("Print radial texts upright or roundabout"))
        menu.add_option(category_name, "radial", radial)
        draw_empty = BooleanOption(_("Draw empty boxes"), True)
        draw_empty.set_help(
            _("Draw the background " "although there is no information")
        )
        menu.add_option(category_name, "draw_empty", draw_empty)

        same_style = BooleanOption(_("Use one font style " "for all generations"), True)
        same_style.set_help(
            _(
                "You can customize font and color "
                "for each generation in the style editor"
            )
        )
        menu.add_option(category_name, "same_style", same_style)

        flip_text = BooleanOption(
            _("Flip names that are on the " "bottom half of the fan"), True
        )
        flip_text.set_help(
            _("Flip names for generations 2, 3 and 4 " "i.e. those found in circles")
        )
        menu.add_option(category_name, "flip_text", flip_text)

        exclude_title = BooleanOption(_("Exclude the title of the chart"), False)
        exclude_title.set_help(_("Exclude the title to make more room for the chart"))
        menu.add_option(category_name, "exclude_title", exclude_title)

        category_name = _("Report Options (2)")

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        stdoptions.add_localization_option(menu, category_name)

    def make_default_style(self, default_style):
        """Make the default output style for the Fan Chart report."""
        background_colors = [
            (255, 63, 0),
            (255, 175, 15),
            (255, 223, 87),
            (255, 255, 111),
            (159, 255, 159),
            (111, 215, 255),
            (79, 151, 255),
            (231, 23, 255),
            (231, 23, 221),
            (210, 170, 124),
            (189, 153, 112),
        ]

        # Paragraph Styles
        f_style = FontStyle()
        f_style.set_size(18)
        f_style.set_bold(1)
        f_style.set_type_face(FONT_SANS_SERIF)
        p_style = ParagraphStyle()
        p_style.set_font(f_style)
        p_style.set_alignment(PARA_ALIGN_CENTER)
        p_style.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("FC-Title", p_style)

        f_style = FontStyle()
        f_style.set_size(9)
        f_style.set_type_face(FONT_SANS_SERIF)
        p_style = ParagraphStyle()
        p_style.set_font(f_style)
        p_style.set_alignment(PARA_ALIGN_CENTER)
        p_style.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("FC-Text", p_style)

        for i in range(0, self.max_generations):
            f_style = FontStyle()
            f_style.set_size(9)
            f_style.set_type_face(FONT_SANS_SERIF)
            p_style = ParagraphStyle()
            p_style.set_font(f_style)
            p_style.set_alignment(PARA_ALIGN_CENTER)
            p_style.set_description(
                _('The style used for the text display of generation "%d"') % i
            )
            default_style.add_paragraph_style("FC-Text" + "%02d" % i, p_style)

        # GraphicsStyles
        g_style = GraphicsStyle()
        g_style.set_paragraph_style("FC-Title")
        default_style.add_draw_style("FC-Graphic-title", g_style)

        for i in range(0, self.max_generations):
            g_style = GraphicsStyle()
            g_style.set_paragraph_style("FC-Text" + "%02d" % i)
            g_style.set_fill_color(background_colors[i])
            default_style.add_draw_style("FC-Graphic" + "%02d" % i, g_style)
