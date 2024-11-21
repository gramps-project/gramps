#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006 Donald N. Allingham
# Copyright (C) 2004-2005 Eero Tamminen
# Copyright (C) 2007-2012 Brian G. Matherly
# Copyright (C) 2008      Peter Landgren
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
#

"""Reports/Graphical Reports/Statistics Report"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import time
from functools import partial

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
# Person and relation types
from gramps.gen.lib import Person, FamilyRelType, EventType, EventRoleType
from gramps.gen.lib.date import Date

# gender and report type names
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    GraphicsStyle,
    FONT_SANS_SERIF,
    FONT_SERIF,
    PARA_ALIGN_CENTER,
    PARA_ALIGN_LEFT,
    IndexMark,
    INDEX_TYPE_TOC,
)
from gramps.gen.plug.menu import (
    BooleanOption,
    EnumeratedListOption,
    NumberOption,
    FilterOption,
    PersonOption,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.datehandler import parser
from gramps.gen.display.place import displayer as _pd
from gramps.gen.proxy import CacheProxyDb


# ------------------------------------------------------------------------
#
# Private Functions
#
# ------------------------------------------------------------------------
def draw_wedge(
    doc, style, centerx, centery, radius, start_angle, end_angle, short_radius=0
):
    """draw a wedge"""
    from math import pi, cos, sin

    while end_angle < start_angle:
        end_angle += 360

    path = []

    degreestoradians = pi / 180.0
    radiansdelta = degreestoradians / 2
    sangle = start_angle * degreestoradians
    eangle = end_angle * degreestoradians
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
    doc.draw_path(style, path)

    delta = (eangle - sangle) / 2.0
    rad = short_radius + (radius - short_radius) / 2.0

    return (
        (centerx + cos(sangle + delta) * rad),
        (centery + sin(sangle + delta) * rad),
    )


def draw_pie_chart(doc, center_x, center_y, radius, data, start=0):
    """
    Draws a pie chart in the specified document. The data passed is plotted as
    a pie chart. The data should consist of the actual data. Percentages of
    each slice are determined by the routine.

    @param doc: Document to which the pie chart should be added
    @type doc: BaseDoc derived class
    @param center_x: x coordinate in centimeters where the center of the pie
       chart should be. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the center of the pie
       chart should be. 0 is the top edge of the document
    @type center_y: float
    @param radius: radius of the pie chart. The pie charts width and height
       will be twice this value.
    @type radius: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    @param start: starting point in degrees, where the default of 0 indicates
       a start point extending from the center to right in a horizontal line.
    @type start: float
    """

    total = 0.0
    for item in data:
        total += item[1]

    for item in data:
        incr = 360.0 * (item[1] / total)
        draw_wedge(doc, item[0], center_x, center_y, radius, start, start + incr)
        start += incr


def draw_legend(doc, start_x, start_y, data, title, label_style):
    """
    Draws a legend for a graph in the specified document. The data passed is
    used to define the legend.  First item style is used for the optional
    Legend title.

    @param doc: Document to which the legend chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand corner
        of the legend is placed. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the legend
        should be. 0 is the top edge of the document
    @type start_y: float
    @param data: List of tuples containing the data to be used to create the
       legend. In order to be compatible with the graph plots, the first and
       third values of the tuple used. The format is (graphics_format, value,
       legend_description).
    @type data: list
    """
    style_sheet = doc.get_style_sheet()
    if title:
        gstyle = style_sheet.get_draw_style(label_style)
        pstyle_name = gstyle.get_paragraph_style()
        pstyle = style_sheet.get_paragraph_style(pstyle_name)
        size = utils.pt2cm(pstyle.get_font().get_size())
        doc.draw_text(label_style, title, start_x + (3 * size), start_y - (size * 0.25))
        start_y += size * 1.3

    for sformat, size, legend in data:
        gstyle = style_sheet.get_draw_style(sformat)
        pstyle_name = gstyle.get_paragraph_style()
        pstyle = style_sheet.get_paragraph_style(pstyle_name)
        size = utils.pt2cm(pstyle.get_font().get_size())
        doc.draw_box(sformat, "", start_x, start_y, (2 * size), size)
        doc.draw_text(
            label_style, legend, start_x + (3 * size), start_y - (size * 0.25)
        )
        start_y += size * 1.3


_TTT = time.localtime(time.time())
_TODAY = parser.parse("%04d-%02d-%02d" % _TTT[:3])


def estimate_age(dbase, person, end_handle=None, start_handle=None, today=_TODAY):
    """
    Estimates the age of a person based off the birth and death
    dates of the person. A tuple containing the estimated upper
    and lower bounds of the person's age is returned. If either
    the birth or death date is missing, a (-1, -1) is returned.

    @param dbase: Gramps database to which the Person object belongs
    @type dbase: DbBase
    @param person: Person object to calculate the age of
    @type person: Person
    @param end_handle: Determines the event handle that determines
       the upper limit of the age. If None, the death event is used
    @type end_handle: str
    @param start_handle: Determines the event handle that determines
       the lower limit of the event. If None, the birth event is
       used
    @type start_handle: str
    @returns: tuple containing the lower and upper bounds of the
       person's age, or (-1, -1) if it could not be determined.
    @rtype: tuple
    """

    calendar = config.get("preferences.calendar-format-report")

    bhandle = None
    if start_handle:
        bhandle = start_handle
    else:
        bref = person.get_birth_ref()
        if bref:
            bhandle = bref.get_reference_handle()

    dhandle = None
    if end_handle:
        dhandle = end_handle
    else:
        dref = person.get_death_ref()
        if dref:
            dhandle = dref.get_reference_handle()

    # if either of the events is not defined, return an error message
    if not bhandle:
        return (-1, -1)

    bdata = dbase.get_event_from_handle(bhandle).get_date_object()
    bdata = bdata.to_calendar(calendar)
    if dhandle:
        ddata = dbase.get_event_from_handle(dhandle).get_date_object()
        ddata = ddata.to_calendar(calendar)
    else:
        if today is not None:
            ddata = today
        else:
            return (-1, -1)

    # if the date is not valid, return an error message
    if not bdata.get_valid() or not ddata.get_valid():
        return (-1, -1)

    # if a year is not valid, return an error message
    if not bdata.get_year_valid() or not ddata.get_year_valid():
        return (-1, -1)

    bstart = bdata.get_start_date()
    bstop = bdata.get_stop_date()

    dstart = ddata.get_start_date()
    dstop = ddata.get_stop_date()

    def _calc_diff(low, high):
        if (low[1], low[0]) > (high[1], high[0]):
            return high[2] - low[2] - 1
        else:
            return high[2] - low[2]

    if bstop == dstop == Date.EMPTY:
        lower = _calc_diff(bstart, dstart)
        age = (lower, lower)
    elif bstop == Date.EMPTY:
        lower = _calc_diff(bstart, dstart)
        upper = _calc_diff(bstart, dstop)
        age = (lower, upper)
    elif dstop == Date.EMPTY:
        lower = _calc_diff(bstop, dstart)
        upper = _calc_diff(bstart, dstart)
        age = (lower, upper)
    else:
        lower = _calc_diff(bstop, dstart)
        upper = _calc_diff(bstart, dstop)
        age = (lower, upper)
    return age


# ------------------------------------------------------------------------
#
# Global options and their names
#
# ------------------------------------------------------------------------
class _options:
    # sort type identifiers
    SORT_VALUE = 0
    SORT_KEY = 1

    opt_sorts = [
        (SORT_VALUE, "Item count", _("Item count")),
        (SORT_KEY, "Item name", _("Item name")),
    ]
    opt_genders = [
        (Person.UNKNOWN, "All", _("All")),
        (Person.MALE, "Men", _("Men")),
        (Person.FEMALE, "Women", _("Women")),
        (Person.OTHER, "Other", _("Other")),
    ]


def _T_(value, context=""):  # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh


# ------------------------------------------------------------------------
#
# Data extraction methods from the database
#
# ------------------------------------------------------------------------
class Extract:
    """Class for extracting statistical data from the database"""

    def __init__(self):
        """Methods for extracting statistical data from the database"""
        # key, non-localized name, localized name, type method, data method
        self.extractors = {
            "data_title": (
                "Title",
                _T_("Title", "person"),
                self.get_person,
                self.get_title,
            ),
            "data_sname": (
                "Surname",
                _T_("Surname"),
                self.get_person,
                self.get_surname,
            ),
            "data_fname": (
                "Forename",
                _T_("Forename"),
                self.get_person,
                self.get_forename,
            ),
            "data_gender": ("Gender", _T_("Gender"), self.get_person, self.get_gender),
            "data_byear": (
                "Birth year",
                _T_("Birth year"),
                self.get_birth,
                self.get_year,
            ),
            "data_dyear": (
                "Death year",
                _T_("Death year"),
                self.get_death,
                self.get_year,
            ),
            "data_bmonth": (
                "Birth month",
                _T_("Birth month"),
                self.get_birth,
                self.get_month,
            ),
            "data_dmonth": (
                "Death month",
                _T_("Death month"),
                self.get_death,
                self.get_month,
            ),
            "data_bplace": (
                "Birth place",
                _T_("Birth place"),
                self.get_birth,
                self.get_place,
            ),
            "data_dplace": (
                "Death place",
                _T_("Death place"),
                self.get_death,
                self.get_place,
            ),
            "data_mplace": (
                "Marriage place",
                _T_("Marriage place"),
                self.get_marriage_handles,
                self.get_places,
            ),
            "data_mcount": (
                "Number of relationships",
                _T_("Number of relationships"),
                self.get_any_family_handles,
                self.get_handle_count,
            ),
            "data_fchild": (
                "Age when first child born",
                _T_("Age when first child born"),
                self.get_child_handles,
                self.get_first_child_age,
            ),
            "data_lchild": (
                "Age when last child born",
                _T_("Age when last child born"),
                self.get_child_handles,
                self.get_last_child_age,
            ),
            "data_ccount": (
                "Number of children",
                _T_("Number of children"),
                self.get_child_handles,
                self.get_handle_count,
            ),
            "data_mage": (
                "Age at marriage",
                _T_("Age at marriage"),
                self.get_marriage_handles,
                self.get_event_ages,
            ),
            "data_dage": (
                "Age at death",
                _T_("Age at death"),
                self.get_person,
                self.get_death_age,
            ),
            "data_age": ("Age", _T_("Age"), self.get_person, self.get_person_age),
            "data_etypes": (
                "Event type",
                _T_("Event type"),
                self.get_event_handles,
                self.get_event_type,
            ),
        }

    # ----------------- data extraction methods --------------------
    # take an object and return a list of strings

    def get_title(self, person):
        "return title for given person"
        # TODO: return all titles, not just primary ones...
        title = person.get_primary_name().get_title()
        if title:
            return [title]
        else:
            return [_T_("(Preferred) title missing")]

    def get_forename(self, person):
        "return forenames for given person"
        # TODO: return all forenames, not just primary ones...
        firstnames = person.get_primary_name().get_first_name().strip()
        if firstnames:
            return firstnames.split()
        else:
            return [_T_("(Preferred) forename missing")]

    def get_surname(self, person):
        "return surnames for given person"
        # TODO: return all surnames, not just primary ones...
        # TODO: have the surname formatted according to the name_format too
        surnames = person.get_primary_name().get_surname().strip()
        if surnames:
            return surnames.split()
        else:
            return [_T_("(Preferred) surname missing")]

    def get_gender(self, person):
        "return gender for given person"
        # TODO: why there's no Person.getGenderName?
        # It could be used by getDisplayInfo & this...
        if person.gender == Person.MALE:
            return [_T_("Men")]
        if person.gender == Person.FEMALE:
            return [_T_("Women")]
        if person.gender == Person.OTHER:
            return [_T_("Other")]
        return [_T_("Gender unknown")]

    def get_year(self, event):
        "return year for given event"
        date = event.get_date_object()
        date = date.to_calendar(self.calendar)
        if date:
            year = date.get_year()
            if year:
                return [self._get_date(Date(year))]  # localized year
        return [_T_("Date(s) missing")]

    def get_month(self, event):
        "return month for given event"
        date_displayer = self._locale.date_displayer
        CAL_TO_LONG_MONTHS_NAMES = {
            Date.CAL_GREGORIAN: date_displayer.long_months,
            Date.CAL_JULIAN: date_displayer.long_months,
            Date.CAL_HEBREW: date_displayer.hebrew,
            Date.CAL_FRENCH: date_displayer.french,
            Date.CAL_PERSIAN: date_displayer.persian,
            Date.CAL_ISLAMIC: date_displayer.islamic,
            Date.CAL_SWEDISH: date_displayer.swedish,
        }

        date = event.get_date_object()
        if date:
            month = date.get_month()
            if month:
                month_names = CAL_TO_LONG_MONTHS_NAMES[date.get_calendar()]
                return [month_names[month]]
        return [_T_("Date(s) missing")]

    def get_place(self, event):
        "return place for given event"
        place_handle = event.get_place_handle()
        if place_handle:
            place = _pd.display_event(self.db, event)
            if place:
                return [place]
        return [_T_("Place missing")]

    def get_places(self, data):
        "return places for given (person,event_handles)"
        places = []
        person, event_handles = data
        for event_handle in event_handles:
            event = self.db.get_event_from_handle(event_handle)
            place_handle = event.get_place_handle()
            if place_handle:
                place = _pd.display_event(self.db, event)
                if place:
                    places.append(place)
            else:
                places.append(_T_("Place missing"))
        return places

    def get_person_age(self, person):
        "return age for given person, if alive"
        death_ref = person.get_death_ref()
        if not death_ref:
            return [self.estimate_age(person)]
        return [_T_("Already dead")]

    def get_death_age(self, person):
        "return age at death for given person, if dead"
        death_ref = person.get_death_ref()
        if death_ref:
            return [self.estimate_age(person, death_ref.ref)]
        return [_T_("Still alive")]

    def get_event_ages(self, data):
        "return ages at given (person,event_handles)"
        person, event_handles = data
        ages = [self.estimate_age(person, h) for h in event_handles]
        if ages:
            return ages
        return [_T_("Events missing")]

    def get_event_type(self, data):
        "return event types at given (person,event_handles)"
        types = []
        person, event_handles = data
        for event_handle in event_handles:
            event = self.db.get_event_from_handle(event_handle)
            event_type = self._(self._get_type(event.get_type()))
            types.append(event_type)
        if types:
            return types
        return [_T_("Events missing")]

    def get_first_child_age(self, data):
        "return age when first child in given (person,child_handles) was born"
        ages, errors = self.get_sorted_child_ages(data)
        if ages:
            errors.append(ages[0])
            return errors
        return [_T_("Children missing")]

    def get_last_child_age(self, data):
        "return age when last child in given (person,child_handles) was born"
        ages, errors = self.get_sorted_child_ages(data)
        if ages:
            errors.append(ages[-1])
            return errors
        return [_T_("Children missing")]

    def get_handle_count(self, data):
        """
        return number of handles in given (person, handle_list)
        used for child count, family count
        """
        return ["%3d" % len(data[1])]

    # ------------------- utility methods -------------------------

    def get_sorted_child_ages(self, data):
        "return (sorted_ages,errors) for given (person,child_handles)"
        ages = []
        errors = []
        person, child_handles = data
        for child_handle in child_handles:
            child = self.db.get_person_from_handle(child_handle)
            birth_ref = child.get_birth_ref()
            if birth_ref:
                ages.append(self.estimate_age(person, birth_ref.ref))
            else:
                errors.append(_T_("Birth missing"))
                continue
        ages.sort()
        return (ages, errors)

    def estimate_age(self, person, end=None, begin=None):
        """return estimated age (range) for given person or error message.
        age string is padded with spaces so that it can be sorted"""
        age = estimate_age(self.db, person, end, begin)
        if age[0] < 0 or age[1] < 0:
            # inadequate information
            return _T_("Date(s) missing")
        if age[0] == age[1]:
            # exact year
            return "%3d" % age[0]
        else:
            # minimum and maximum
            return "%3d-%d" % (age[0], age[1])

    # ------------------- type methods -------------------------
    # take db and person and return suitable gramps object(s)

    def get_person(self, person):
        "return person"
        return person

    def get_birth(self, person):
        "return birth event for given person or None"
        birth_ref = person.get_birth_ref()
        if birth_ref:
            return self.db.get_event_from_handle(birth_ref.ref)
        return None

    def get_death(self, person):
        "return death event for given person or None"
        death_ref = person.get_death_ref()
        if death_ref:
            return self.db.get_event_from_handle(death_ref.ref)
        return None

    def get_child_handles(self, person):
        "return list of child handles for given person or None"
        children = []
        for fam_handle in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_handle)
            for child_ref in fam.get_child_ref_list():
                children.append(child_ref.ref)
        # TODO: it would be good to return only biological children,
        # but Gramps doesn't offer any efficient way to check that
        # (I don't want to check each children's parent family mother
        # and father relations as that would make this *much* slower)
        if children:
            return (person, children)
        return None

    def get_marriage_handles(self, person):
        "return list of marriage event handles for given person or None"
        marriages = []
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if int(family.get_relationship()) == FamilyRelType.MARRIED:
                for event_ref in family.get_event_ref_list():
                    event = self.db.get_event_from_handle(event_ref.ref)
                    if event.get_type() == EventType.MARRIAGE and (
                        event_ref.get_role() == EventRoleType.FAMILY
                        or event_ref.get_role() == EventRoleType.PRIMARY
                    ):
                        marriages.append(event_ref.ref)
        if marriages:
            return (person, marriages)
        return None

    def get_any_family_handles(self, person):
        "return list of family handles for given person or None"
        families = person.get_family_handle_list()

        if families:
            return (person, families)
        return None

    def get_event_handles(self, person):
        "return list of event handles for given person or None"
        events = [ref.ref for ref in person.get_event_ref_list()]

        if events:
            return (person, events)
        return None

    # ----------------- data collection methods --------------------

    def get_person_data(self, person, collect):
        """Add data from the database to 'collect' for the given person,
        using methods from the 'collect' data dict tuple
        """
        for chart in collect:
            # get the information
            type_func = chart[2]
            data_func = chart[3]
            obj = type_func(person)  # e.g. get_date()
            if obj:
                value = data_func(obj)  # e.g. get_year()
            else:
                value = [_T_("Personal information missing")]
            # list of information found
            for key in value:
                if key in chart[1]:
                    chart[1][key] += 1
                else:
                    chart[1][key] = 1

    def collect_data(
        self,
        dbase,
        people,
        menu,
        genders,
        year_from,
        year_to,
        no_years,
        cb_progress,
        rlocale,
    ):
        """goes through the database and collects the selected personal
        data persons fitting the filter and birth year criteria. The
        arguments are:
        dbase       - the Gramps database
        people      - a list of filtered people
        options     - report options_dict which sets which methods are used
        genders     - which gender(s) to include into statistics
        year_from   - use only persons who've born this year of after
        year_to     - use only persons who've born this year or before
        no_years    - use also people without known birth year
        cb_progress - callback to indicate progress
        rlocale     - a GrampsLocale instance

        Returns an array of tuple of:
        - Extraction method title
        - Dict of values with their counts
        (- Method)
        """
        self.db = dbase  # store for use by methods
        self._locale = rlocale
        self._ = rlocale.translation.sgettext
        self._get_type = rlocale.get_type
        self._get_date = rlocale.get_date
        self.calendar = config.get("preferences.calendar-format-report")

        data = []
        ext = self.extractors
        # which methods to use
        for name in self.extractors:
            option = menu.get_option_by_name(name)
            if option.get_value() == True:
                # localized data title, value dict, type and data method
                data.append((ext[name][1], {}, ext[name][2], ext[name][3]))

        # go through the people and collect data
        for person_handle in people:
            cb_progress()
            person = dbase.get_person_from_handle(person_handle)
            # check whether person has suitable gender
            if person.gender != genders and genders != Person.UNKNOWN:
                continue

            # check whether birth year is within required range
            birth = self.get_birth(person)
            if birth:
                birthdate = birth.get_date_object()
                if birthdate.get_year_valid():
                    birthdate = birthdate.to_calendar(self.calendar)

                    year = birthdate.get_year()
                    if not (year >= year_from and year <= year_to):
                        continue
                else:
                    # if death before range, person's out of range too...
                    death = self.get_death(person)
                    if death:
                        deathdate = death.get_date_object()
                        if deathdate.get_year_valid():
                            deathdate = deathdate.to_calendar(self.calendar)

                            if deathdate.get_year() < year_from:
                                continue
                        if not no_years:
                            # don't accept people not known to be in range
                            continue
                    else:
                        continue
            else:
                continue

            self.get_person_data(person, data)
        return data


# GLOBAL: required so that we get access to _Extract.extractors[]
# Unfortunately class variables cannot reference instance methods :-/
_Extract = Extract()


# ------------------------------------------------------------------------
#
# Statistics report
#
# ------------------------------------------------------------------------
class StatisticsChart(Report):
    """StatisticsChart report"""

    def __init__(self, database, options, user):
        """
        Create the Statistics object that produces the report.
        Uses the Extractor class to extract the data from the database.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance
        incl_private  - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)
        menu = options.menu
        self._user = user

        self.set_locale(menu.get_option_by_name("trans").get_value())
        # override default gettext, or English output will have "person|Title"
        self._ = self._locale.translation.sgettext

        stdoptions.run_private_data_option(self, menu)
        living_opt = stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        get_option_by_name = menu.get_option_by_name
        get_value = lambda name: get_option_by_name(name).get_value()

        filter_opt = get_option_by_name("filter")
        self.filter = filter_opt.get_filter()
        self.fil_name = "(%s)" % self.filter.get_name(self._locale)

        self.bar_items = get_value("bar_items")
        self.show_empty_information = get_value("show_empty_information")
        year_from = get_value("year_from")
        year_to = get_value("year_to")
        gender = get_value("gender")

        living_value = get_value("living_people")
        for value, description in living_opt.get_items(xml_items=True):
            if value == living_value:
                living_desc = self._(description)
                break
        self.living_desc = self._("(Living people: %(option_name)s)") % {
            "option_name": living_desc
        }

        # title needs both data extraction method name + gender name
        if gender == Person.MALE:
            genders = self._("Men")
        elif gender == Person.FEMALE:
            genders = self._("Women")
        elif gender == Person.OTHER:
            genders = self._("Other")
        else:
            genders = None

        if genders:
            span_string = self._("%s born") % genders
        else:
            span_string = self._("Persons born")
        span_string += " %s-%s" % (
            self._get_date(Date(year_from)),  # localized
            self._get_date(Date(year_to)),
        )

        people = self.filter.apply(
            self.database, self.database.iter_person_handles(), user=self._user
        )

        # extract requested items from the database and count them
        self._user.begin_progress(
            _("Statistics Charts"),
            _("Collecting data..."),
            self.database.get_number_of_people(),
        )
        tables = _Extract.collect_data(
            self.database,
            people,
            menu,
            gender,
            year_from,
            year_to,
            get_value("no_years"),
            self._user.step_progress,
            self._locale,
        )
        self._user.end_progress()

        self._user.begin_progress(
            _("Statistics Charts"), _("Sorting data..."), len(tables)
        )
        self.data = []
        sortby = get_value("sortby")
        reverse = get_value("reverse")
        for table in tables:
            # generate sorted item lookup index index
            lookup = self.index_items(table[1], sortby, reverse)
            # document heading
            heading = "%(str1)s -- %(str2)s" % {
                "str1": self._(table[0]),
                "str2": span_string,
            }
            self.data.append((heading, table[0], table[1], lookup))
            self._user.step_progress()
        self._user.end_progress()

    def index_items(self, data, sort, reverse):
        """creates & stores a sorted index for the items"""

        # sort by item keys
        index = sorted(data, reverse=True if reverse else False)

        if sort == _options.SORT_VALUE:
            # set for the sorting function
            self.lookup_items = data

            # then sort by value
            index.sort(
                key=lambda x: self.lookup_items[x], reverse=True if reverse else False
            )

        return index

    def write_report(self):
        "output the selected statistics..."

        mark = IndexMark(self._("Statistics Charts"), INDEX_TYPE_TOC, 1)
        self._user.begin_progress(
            _("Statistics Charts"), _("Saving charts..."), len(self.data)
        )
        for data in sorted(self.data):
            self.doc.start_page()
            if mark:
                self.doc.draw_text("SC-title", "", 0, 0, mark)  # put it in TOC
                mark = None  # crock, but we only want one of them
            if len(data[3]) < self.bar_items:
                self.output_piechart(*data[:4])
            else:
                self.output_barchart(*data[:4])
            self.doc.end_page()
            self._user.step_progress()
        self._user.end_progress()

    def output_piechart(self, title1, typename, data, lookup):
        # set layout variables
        middle_w = self.doc.get_usable_width() / 2
        middle_h = self.doc.get_usable_height() / 2
        middle = min(middle_w, middle_h)

        # start output
        style_sheet = self.doc.get_style_sheet()
        pstyle = style_sheet.get_paragraph_style("SC-Title")
        mark = IndexMark(title1, INDEX_TYPE_TOC, 2)
        self.doc.center_text("SC-title", title1, middle_w, 0, mark)
        yoffset = utils.pt2cm(pstyle.get_font().get_size())
        self.doc.center_text("SC-title", self.fil_name, middle_w, yoffset)
        yoffset = 2 * utils.pt2cm(pstyle.get_font().get_size())
        self.doc.center_text("SC-title", self.living_desc, middle_w, yoffset)

        # collect data for output
        color = 0
        chart_data = []
        for key in lookup:
            style = "SC-color-%d" % color
            text = "%s (%d)" % (self._(key), data[key])
            # graphics style, value, and it's label
            chart_data.append((style, data[key], text))
            color = (color + 1) % 7  # There are only 7 color styles defined

        margin = 1.0
        legendx = 2.0

        # output data...
        radius = middle - 2 * margin
        yoffset += margin + radius
        draw_pie_chart(self.doc, middle_w, yoffset, radius, chart_data, -90)
        yoffset += radius + 2 * margin
        if middle == middle_h:  # Landscape
            legendx = 1.0
            yoffset = margin

        text = self._("%s (persons):") % self._(typename)
        draw_legend(self.doc, legendx, yoffset, chart_data, text, "SC-legend")

    def output_barchart(self, title1, typename, data, lookup):
        pt2cm = utils.pt2cm
        style_sheet = self.doc.get_style_sheet()
        pstyle = style_sheet.get_paragraph_style("SC-Text")
        font = pstyle.get_font()

        # set layout variables
        width = self.doc.get_usable_width()
        row_h = pt2cm(font.get_size())
        max_y = self.doc.get_usable_height() - row_h
        pad = row_h * 0.5

        # the list of keys that represent "missing" information
        excluded_keys = [
            _T_("(Preferred) forename missing"),
            _T_("Date(s) missing"),
            _T_("Personal information missing"),
            _T_("Birth missing"),
            _T_("Children missing"),
        ]
        # hide empty information
        if not self.show_empty_information:
            lookup = [k for k in lookup if k not in excluded_keys]

        # check maximum value
        max_value = max(data[k] for k in lookup) if lookup else 0
        # horizontal area for the gfx bars
        margin = 1.0
        middle = width / 2.0
        textx = middle + margin / 2.0
        stopx = middle - margin / 2.0
        maxsize = stopx - margin

        # start output
        pstyle = style_sheet.get_paragraph_style("SC-Title")
        mark = IndexMark(title1, INDEX_TYPE_TOC, 2)
        self.doc.center_text("SC-title", title1, middle, 0, mark)
        yoffset = pt2cm(pstyle.get_font().get_size())
        self.doc.center_text("SC-title", self.fil_name, middle, yoffset)
        yoffset = 2 * pt2cm(pstyle.get_font().get_size())
        self.doc.center_text("SC-title", self.living_desc, middle, yoffset)
        yoffset = 3 * pt2cm(pstyle.get_font().get_size())

        # header
        yoffset += row_h + pad
        text = self._("%s (persons):") % self._(typename)
        self.doc.draw_text("SC-text", text, textx, yoffset)

        for key in lookup:
            yoffset += row_h + pad
            if yoffset > max_y:
                # for graphical report, page_break() doesn't seem to work
                self.doc.end_page()
                self.doc.start_page()
                yoffset = 0

            # right align bar to the text
            value = data[key]
            startx = stopx - (maxsize * value / max_value)
            self.doc.draw_box("SC-bar", "", startx, yoffset, stopx - startx, row_h)
            # text after bar
            text = "%s (%d)" % (self._(key), data[key])
            self.doc.draw_text("SC-text", text, textx, yoffset)

        return


# ------------------------------------------------------------------------
#
# StatisticsChartOptions
#
# ------------------------------------------------------------------------
class StatisticsChartOptions(MenuReportOptions):
    """Options for StatisticsChart report"""

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
        """
        Add options to the menu for the statistics report.
        """

        ################################
        category_name = _("Report Options")
        add_option = partial(menu.add_option, category_name)
        ################################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Determines what people are included " "in the report.")
        )
        add_option("filter", self.__filter)
        self.__filter.connect("value-changed", self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter."))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect("value-changed", self.__update_filters)

        sortby = EnumeratedListOption(_("Sort chart items by"), _options.SORT_VALUE)
        for item_idx, item in enumerate(_options.opt_sorts):
            sortby.add_item(item_idx, item[2])
        sortby.set_help(_("Select how the statistical data is sorted."))
        add_option("sortby", sortby)

        reverse = BooleanOption(_("Sort in reverse order"), False)
        reverse.set_help(_("Check to reverse the sorting order."))
        add_option("reverse", reverse)

        this_year = time.localtime()[0]
        year_from = NumberOption(_("People Born After"), 1700, 1, this_year)
        year_from.set_help(_("Birth year from which to include people."))
        add_option("year_from", year_from)

        year_to = NumberOption(_("People Born Before"), this_year, 1, this_year)
        year_to.set_help(_("Birth year until which to include people"))
        add_option("year_to", year_to)

        no_years = BooleanOption(_("Include people without known birth years"), False)
        no_years.set_help(_("Whether to include people without " "known birth years."))
        add_option("no_years", no_years)

        gender = EnumeratedListOption(_("Genders included"), Person.UNKNOWN)
        for first, second, third in _options.opt_genders:
            gender.add_item(first, third)
        gender.set_help(_("Select which genders are included into " "statistics."))
        add_option("gender", gender)

        bar_items = NumberOption(_("Max. items for a pie"), 8, 0, 20)
        bar_items.set_help(
            _(
                "With fewer items pie chart and legend will be "
                "used instead of a bar chart."
            )
        )
        add_option("bar_items", bar_items)

        show_empty_information = BooleanOption(
            _("Include counts of missing information"), False
        )
        show_empty_information.set_help(
            _(
                "Whether to include counts of the "
                "number of people who lack the given "
                "information."
            )
        )
        add_option("show_empty_information", show_empty_information)

        ################################
        category_name = _("Report Options (2)")
        add_option = partial(menu.add_option, category_name)
        ################################

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect("value-changed", self.__update_filters)

        self.__update_filters()

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        stdoptions.add_localization_option(menu, category_name)

        ################################
        # List of available charts on separate option tabs
        ################################

        idx = 0
        third = (len(_Extract.extractors) + 1) // 3
        chart_types = []
        for chart_opt, ctuple in _Extract.extractors.items():
            chart_types.append((_(ctuple[1]), chart_opt, ctuple))
        sorted_chart_types = sorted(chart_types, key=lambda x: glocale.sort_key(x[0]))
        for translated_option_name, opt_name, ctuple in sorted_chart_types:
            if idx >= (third * 2):
                category_name = _("Charts 3")
            elif idx >= third:
                category_name = _("Charts 2")
            else:
                category_name = _("Charts 1")
            opt = BooleanOption(translated_option_name, False)
            opt.set_help(_("Include charts with indicated data."))
            menu.add_option(category_name, opt_name, opt)
            idx += 1

        # Enable a couple of charts by default
        menu.get_option_by_name("data_gender").set_value(True)
        menu.get_option_by_name("data_ccount").set_value(True)
        menu.get_option_by_name("data_bmonth").set_value(True)

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
        """Make the default output style for the Statistics report."""
        # Paragraph Styles
        fstyle = FontStyle()
        fstyle.set_size(10)
        fstyle.set_type_face(FONT_SERIF)
        pstyle = ParagraphStyle()
        pstyle.set_font(fstyle)
        pstyle.set_alignment(PARA_ALIGN_LEFT)
        pstyle.set_description(_("The style used for the items and values."))
        default_style.add_paragraph_style("SC-Text", pstyle)

        fstyle = FontStyle()
        fstyle.set_size(14)
        fstyle.set_type_face(FONT_SANS_SERIF)
        pstyle = ParagraphStyle()
        pstyle.set_font(fstyle)
        pstyle.set_alignment(PARA_ALIGN_CENTER)
        pstyle.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("SC-Title", pstyle)

        """
        Graphic Styles:
            SC-title - Contains the SC-Title paragraph style used for
                       the title of the document
            SC-text  - Contains the SC-Name paragraph style used for
                       the individual's name
            SC-color-N - The colors for drawing pies.
            SC-bar - A red bar with 0.5pt black line.
        """
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Title")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("SC-title", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("SC-text", gstyle)

        width = 0.8
        # red
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 0, 0))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-0", gstyle)
        # orange
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 158, 33))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-1", gstyle)
        # green
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((0, 178, 0))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-2", gstyle)
        # violet
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((123, 0, 123))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-3", gstyle)
        # yellow
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 0))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-4", gstyle)
        # blue
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((0, 105, 214))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-5", gstyle)
        # gray
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((210, 204, 210))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-color-6", gstyle)

        gstyle = GraphicsStyle()
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 0, 0))
        gstyle.set_line_width(width)
        default_style.add_draw_style("SC-bar", gstyle)

        # legend
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style("SC-Text")
        gstyle.set_color((0, 0, 0))
        gstyle.set_fill_color((255, 255, 255))
        gstyle.set_line_width(0)
        default_style.add_draw_style("SC-legend", gstyle)
