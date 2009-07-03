# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Brian G. Matherly
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
# $Id: $
#
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
from gettext import ngettext
import datetime
import time

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                             FONT_SERIF, PARA_ALIGN_CENTER,
                             PARA_ALIGN_LEFT, PARA_ALIGN_RIGHT)
from gen.plug.docgen.fontscale import string_trim
from BasicUtils import name_displayer
from gen.plug import PluginManager
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_DRAW
from gen.plug.menu import BooleanOption, StringOption, NumberOption, \
                         EnumeratedListOption, FilterOption, PersonOption
import GrampsLocale
import gen.lib
from Utils import probably_alive
from gui.utils import ProgressMeter

import libholiday
from libholiday import g2iso

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
pt2cm = ReportUtils.pt2cm
cm2pt = ReportUtils.cm2pt

#------------------------------------------------------------------------
#
# Calendar
#
#------------------------------------------------------------------------
class Calendar(Report):
    """
    Create the Calendar object that produces the report.
    """
    def __init__(self, database, options_class):
        Report.__init__(self, database, options_class)
        menu = options_class.menu

        self.year = menu.get_option_by_name('year').get_value()
        self.name_format = menu.get_option_by_name('name_format').get_value()
        self.country = menu.get_option_by_name('country').get_value()
        self.anniversaries = menu.get_option_by_name('anniversaries').get_value()
        self.start_dow = menu.get_option_by_name('start_dow').get_value()
        self.maiden_name = menu.get_option_by_name('maiden_name').get_value()
        self.alive = menu.get_option_by_name('alive').get_value()
        self.birthdays = menu.get_option_by_name('birthdays').get_value()
        self.text1 = menu.get_option_by_name('text1').get_value()
        self.text2 = menu.get_option_by_name('text2').get_value()
        self.text3 = menu.get_option_by_name('text3').get_value()
        self.filter_option =  menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)

    def get_name(self, person, maiden_name = None):
        """ Return person's name, unless maiden_name given, 
            unless married_name listed. 
        """
        # Get all of a person's names:
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == gen.lib.NameType.MARRIED:
                married_name = name
                break # use first
        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = gen.lib.Name(married_name)
            else:
                name = gen.lib.Name(primary_name)
                name.set_surname(maiden_name)
        else:
            name = gen.lib.Name(primary_name)
        name.set_display_as(self.name_format)
        return name_displayer.display_name(name)
        
    def draw_rectangle(self, style, sx, sy, ex, ey):
        """ This should be in BaseDoc """
        self.doc.draw_line(style, sx, sy, sx, ey)
        self.doc.draw_line(style, sx, sy, ex, sy)
        self.doc.draw_line(style, ex, sy, ex, ey)
        self.doc.draw_line(style, sx, ey, ex, ey)

### The rest of these all have to deal with calendar specific things

    def add_day_item(self, text, month, day):
        """ Add an item to a day. """
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])
        day_list.append(text)
        month_dict[day] = day_list
        self.calendar[month] = month_dict

    def __get_holidays(self):
        """ Get the holidays for the specified country and year """
        holiday_table = libholiday.HolidayTable()
        country = holiday_table.get_countries()[self.country]
        holiday_table.load_holidays(self.year, country)
        for month in range(1, 13):
            for day in range(1, 32):
                holiday_names = holiday_table.get_holidays(month, day) 
                for holiday_name in holiday_names:
                    self.add_day_item(holiday_name, month, day)

    def write_report(self):
        """ The short method that runs through each month and creates a page. """
        # initialize the dict to fill:
        self.progress = ProgressMeter(_('Calendar Report'))
        self.calendar = {}
        
        # get the information, first from holidays:
        if self.country != 0:
            self.__get_holidays()
            
        # get data from database:
        self.collect_data()
        # generate the report:
        self.progress.set_pass(_('Formatting months...'), 12)
        for month in range(1, 13):
            self.progress.step()
            self.print_page(month)
        self.progress.close()

    def print_page(self, month):
        """
        This method actually writes the calendar page.
        """
        style_sheet = self.doc.get_style_sheet()
        ptitle = style_sheet.get_paragraph_style("CAL-Title")
        ptext = style_sheet.get_paragraph_style("CAL-Text")
        pdaynames = style_sheet.get_paragraph_style("CAL-Daynames")
        pnumbers = style_sheet.get_paragraph_style("CAL-Numbers")
        ptext1style = style_sheet.get_paragraph_style("CAL-Text1style")

        self.doc.start_page()
        width = self.doc.get_usable_width()
        height = self.doc.get_usable_height()
        header = 2.54 # one inch
        self.draw_rectangle("CAL-Border", 0, 0, width, height)
        self.doc.draw_box("CAL-Title", "", 0, 0, width, header)
        self.doc.draw_line("CAL-Border", 0, header, width, header)
        year = self.year
        title = "%s %d" % (GrampsLocale.long_months[month].capitalize(), year)
        font_height = pt2cm(ptitle.get_font().get_size())
        self.doc.center_text("CAL-Title", title, width/2, font_height * 0.25)
        cell_width = width / 7
        cell_height = (height - header)/ 6
        current_date = datetime.date(year, month, 1)
        spacing = pt2cm(1.25 * ptext.get_font().get_size()) # 158
        if current_date.isoweekday() != g2iso(self.start_dow + 1):
            # Go back to previous first day of week, and start from there
            current_ord = (current_date.toordinal() -
                           ((current_date.isoweekday() + 7) -
                            g2iso(self.start_dow + 1)) % 7)
        else:
            current_ord = current_date.toordinal()
        for day_col in range(7):
            font_height = pt2cm(pdaynames.get_font().get_size())
            self.doc.center_text("CAL-Daynames", 
                                 GrampsLocale.long_days[(day_col+
                                                         g2iso(self.start_dow + 1))
                                                        % 7 + 1].capitalize(), 
                                 day_col * cell_width + cell_width/2, 
                                 header - font_height * 1.5)
        for week_row in range(6):
            something_this_week = 0
            for day_col in range(7):
                thisday = current_date.fromordinal(current_ord)
                if thisday.month == month:
                    something_this_week = 1
                    self.draw_rectangle("CAL-Border", day_col * cell_width, 
                                        header + week_row * cell_height, 
                                        (day_col + 1) * cell_width, 
                                        header + (week_row + 1) * cell_height)
                    last_edge = (day_col + 1) * cell_width
                    self.doc.center_text("CAL-Numbers", str(thisday.day), 
                                         day_col * cell_width + cell_width/2, 
                                         header + week_row * cell_height)
                    list = self.calendar.get(month, {}).get(thisday.day, [])
                    position = 0.0 
                    for p in list:
                        lines = p.count("\n") + 1 # lines in the text
                        position += (lines  * spacing)
                        current = 0
                        for line in p.split("\n"):
                            # make sure text will fit:
                            numpos = pt2cm(pnumbers.get_font().get_size())
                            if position + (current * spacing) - 0.1 >= cell_height - numpos: # font daynums
                                continue
                            font = ptext.get_font()
                            line = string_trim(font, line, cm2pt(cell_width + 0.2))
                            self.doc.draw_text("CAL-Text", line, 
                                              day_col * cell_width + 0.1, 
                                              header + (week_row + 1) * cell_height - position + (current * spacing) - 0.1)
                            current += 1
                current_ord += 1
        if not something_this_week:
            last_edge = 0
        font_height = pt2cm(1.5 * ptext1style.get_font().get_size())
        self.doc.center_text("CAL-Text1style", self.text1, last_edge + (width - last_edge)/2, height - font_height * 3) 
        self.doc.center_text("CAL-Text2style", self.text2, last_edge + (width - last_edge)/2, height - font_height * 2) 
        self.doc.center_text("CAL-Text3style", self.text3, last_edge + (width - last_edge)/2, height - font_height * 1) 
        self.doc.end_page()

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        people = self.database.iter_person_handles()
        self.progress.set_pass(_('Applying Filter...'), self.database.get_number_of_people())
        people = self.filter.apply(self.database, people, self.progress)
        pmgr = PluginManager.get_instance()
        rel_calc = pmgr.get_relationship_calculator()

        self.progress.set_pass(_('Reading database...'), len(people))
        for person_handle in people:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.database.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()

            if (self.birthdays and birth_date is not None and birth_date.is_valid()):
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()

                prob_alive_date = gen.lib.Date(self.year, month, day)

                nyears = self.year - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self.maiden_name in ['spouse_first', 'spouse_last']: # get husband's last name:
                    if person.get_gender() == gen.lib.Person.FEMALE:
                        family_list = person.get_family_handle_list()
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
                                        father_lastname = father.get_primary_name().get_surname()
                short_name = self.get_name(person, father_lastname)
                alive = probably_alive(person, self.database, prob_alive_date)

                if (self.alive and alive) or not self.alive:
                    if nyears == 0:
                        text = _('%(person)s, birth%(relation)s') % {
                            'person' : short_name,
                            'relation' : ""}
                    else:
                        text = (ngettext('%(person)s, %(age)d%(relation)s',
                                          '%(person)s, %(age)d%(relation)s', nyears)
                                 % {'person'   : short_name,
                                    'age'      : nyears,  
                                    'relation' : ""})
                    self.add_day_item(text, month, day)
            if self.anniversaries:
                family_list = person.get_family_handle_list()
                for fhandle in family_list: 
                    fam = self.database.get_family_from_handle(fhandle)
                    father_handle = fam.get_father_handle()
                    mother_handle = fam.get_mother_handle()
                    if father_handle == person.get_handle():
                        spouse_handle = mother_handle
                    else:
                        continue # with next person if the father is not "person"
                                 # this will keep from duplicating the anniversary
                    if spouse_handle:
                        spouse = self.database.get_person_from_handle(spouse_handle)
                        if spouse:
                            spouse_name = self.get_name(spouse)
                            short_name = self.get_name(person)
                            # TEMP: this will hanlde ordered events
                            # GRAMPS 3.0 will have a new mechanism for start/stop events
                            are_married = None
                            for event_ref in fam.get_event_ref_list():
                                event = self.database.get_event_from_handle(event_ref.ref)
                                if event.type in [gen.lib.EventType.MARRIAGE, 
                                                             gen.lib.EventType.MARR_ALT]:
                                    are_married = event
                                elif event.type in [gen.lib.EventType.DIVORCE, 
                                                               gen.lib.EventType.ANNULMENT, 
                                                               gen.lib.EventType.DIV_FILING]:
                                    are_married = None
                            if are_married is not None:
                                for event_ref in fam.get_event_ref_list():
                                    event = self.database.get_event_from_handle(event_ref.ref)
                                    event_obj = event.get_date_object()

                                    if event_obj.is_valid():
                                        year = event_obj.get_year()
                                        month = event_obj.get_month()
                                        day = event_obj.get_day()

                                        prob_alive_date = gen.lib.Date(self.year, month, day)
    
                                        nyears = self.year - year
                                        if nyears == 0:
                                            text = _('%(spouse)s and\n %(person)s, wedding') % {
                                                     'spouse' : spouse_name, 
                                                     'person' : short_name, 
                                                    }
                                        else:
                                            text = (ngettext("%(spouse)s and\n %(person)s, %(nyears)d", 
                                                             "%(spouse)s and\n %(person)s, %(nyears)d", nyears)
                                                    % {'spouse' : spouse_name, 
                                                       'person' : short_name, 
                                                       'nyears' : nyears})

                                        alive1 = probably_alive(person, self.database, \
                                            prob_alive_date)
                                        alive2 = probably_alive(spouse, self.database, \
                                            prob_alive_date)
                                        if ((self.alive and alive1 and alive2) or not self.alive):
                                            self.add_day_item(text, month, day)

#------------------------------------------------------------------------
#
# CalendarOptions
#
#------------------------------------------------------------------------
class CalendarOptions(MenuReportOptions):
    """ Calendar options for graphic calendar """
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)
    
    def add_menu_options(self, menu):
        """ Add the options for the graphical calendar """
        category_name = _("Report Options")

        year = NumberOption(_("Year of calendar"), time.localtime()[0], 
                            1000, 3000)
        year.set_help(_("Year of calendar"))
        menu.add_option(category_name, "year", year)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on calendar"))
        menu.add_option(category_name, "filter", self.__filter)
        
        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()

        # We must figure out the value of the first option before we can
        # create the EnumeratedListOption
        fmt_list = name_displayer.get_name_format()
        name_format = EnumeratedListOption(_("Name format"), fmt_list[0][0])
        for num, name, fmt_str, act in fmt_list:
            name_format.add_item(num, name)
        name_format.set_help(_("Select the format to display names"))
        menu.add_option(category_name, "name_format", name_format)

        country = EnumeratedListOption(_("Country for holidays"), 0)
        holiday_table = libholiday.HolidayTable()
        count = 0
        for c in  holiday_table.get_countries():
            country.add_item(count, c)
            count += 1
        country.set_help(_("Select the country to see associated holidays"))
        menu.add_option(category_name, "country", country)

        start_dow = EnumeratedListOption(_("First day of week"), 1)
        for count in range(1, 8):
            # conversion between gramps numbering (sun=1) and iso numbering (mon=1) of weekdays below
            start_dow.add_item((count+5) % 7 + 1, GrampsLocale.long_days[count].capitalize()) 
        start_dow.set_help(_("Select the first day of the week for the calendar"))
        menu.add_option(category_name, "start_dow", start_dow) 

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item("spouse_first", _("Wives use husband's surname (from first family listed)"))
        maiden_name.add_item("spouse_last", _("Wives use husband's surname (from last family listed)"))
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)

        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", alive)

        birthdays = BooleanOption(_("Include birthdays"), True)
        birthdays.set_help(_("Include birthdays in the calendar"))
        menu.add_option(category_name, "birthdays", birthdays)

        anniversaries = BooleanOption(_("Include anniversaries"), True)
        anniversaries.set_help(_("Include anniversaries in the calendar"))
        menu.add_option(category_name, "anniversaries", anniversaries)

        category_name = _("Text Options")

        text1 = StringOption(_("Text Area 1"), _("My Calendar")) 
        text1.set_help(_("First line of text at bottom of calendar"))
        menu.add_option(category_name, "text1", text1)

        text2 = StringOption(_("Text Area 2"), _("Produced with GRAMPS"))
        text2.set_help(_("Second line of text at bottom of calendar"))
        menu.add_option(category_name, "text2", text2)

        text3 = StringOption(_("Text Area 3"), "http://gramps-project.org/",)
        text3.set_help(_("Third line of text at bottom of calendar"))
        menu.add_option(category_name, "text3", text3)
        
    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)

    def make_my_style(self, default_style, name, description, 
                      size=9, font=FONT_SERIF, justified ="left", 
                      color=None, align=PARA_ALIGN_CENTER, 
                      shadow = None, italic=0, bold=0, borders=0, indent=None):
        """ Create paragraph and graphic styles of the same name """
        # Paragraph:
        f = FontStyle()
        f.set_size(size)
        f.set_type_face(font)
        f.set_italic(italic)
        f.set_bold(bold)
        p = ParagraphStyle()
        p.set_font(f)
        p.set_alignment(align)
        p.set_description(description)
        p.set_top_border(borders)
        p.set_left_border(borders)
        p.set_bottom_border(borders)
        p.set_right_border(borders)
        if indent:
            p.set(first_indent=indent)
        if justified == "left":
            p.set_alignment(PARA_ALIGN_LEFT)       
        elif justified == "right":
            p.set_alignment(PARA_ALIGN_RIGHT)       
        elif justified == "center":
            p.set_alignment(PARA_ALIGN_CENTER)       
        default_style.add_paragraph_style(name, p)
        # Graphics:
        g = GraphicsStyle()
        g.set_paragraph_style(name)
        if shadow:
            g.set_shadow(*shadow)
        if color is not None:
            g.set_fill_color(color)
        if not borders:
            g.set_line_width(0)
        default_style.add_draw_style(name, g)
        
    def make_default_style(self, default_style):
        """ Add the styles used in this report """
        self.make_my_style(default_style, "CAL-Title", 
                           _('Title text and background color'), 20, 
                           bold=1, italic=1, 
                           color=(0xEA, 0xEA, 0xEA))
        self.make_my_style(default_style, "CAL-Numbers", 
                           _('Calendar day numbers'), 13, 
                           bold=1)
        self.make_my_style(default_style, "CAL-Text", 
                           _('Daily text display'), 9)
        self.make_my_style(default_style, "CAL-Daynames", 
                           _('Days of the week text'), 12, 
                           italic=1, bold=1, 
                           color = (0xEA, 0xEA, 0xEA))
        self.make_my_style(default_style, "CAL-Text1style", 
                           _('Text at bottom, line 1'), 12)
        self.make_my_style(default_style, "CAL-Text2style", 
                           _('Text at bottom, line 2'), 12)
        self.make_my_style(default_style, "CAL-Text3style", 
                           _('Text at bottom, line 3'), 9)
        self.make_my_style(default_style, "CAL-Border", 
                           _('Borders'), borders=True)

#------------------------------------------------------------------------
#
# Register the plugins
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'calendar', 
    category = CATEGORY_DRAW, 
    report_class = Calendar, 
    options_class = CalendarOptions, 
    modes = PluginManager.REPORT_MODE_GUI | \
            PluginManager.REPORT_MODE_BKI | \
            PluginManager.REPORT_MODE_CLI, 
    translated_name = _("Calendar"), 
    status = _("Stable"), 
    author_name = "Douglas S. Blank", 
    author_email = "dblank@cs.brynmawr.edu", 
    description = _("Produces a graphical calendar"), 
    )

