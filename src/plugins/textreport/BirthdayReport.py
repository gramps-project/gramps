# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2009           Rob G. Healey <robhealey1@gmail.com>
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
# $Id$
#

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _
from gen.ggettext import ngettext
import datetime, time

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.display.name import displayer as _nd
from Errors import ReportError
from gen.lib import NameType, EventType, Name, Date, Person
import Relationship
from gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                             FONT_SERIF, PARA_ALIGN_RIGHT,
                             PARA_ALIGN_LEFT, PARA_ALIGN_CENTER)
from gen.plug.menu import (BooleanOption, StringOption, NumberOption, 
                         EnumeratedListOption, FilterOption, PersonOption)
from gui.utils import ProgressMeter
from ReportBase import Report, ReportUtils, MenuReportOptions
from Utils import probably_alive
import GrampsLocale
from DateHandler import displayer as _dd

import libholiday

#------------------------------------------------------------------------
#
# Calendar
#
#------------------------------------------------------------------------
class CalendarReport(Report):
    """
    Create the Calendar object that produces the report.
    """
    def __init__(self, database, options_class):
        Report.__init__(self, database, options_class)
        menu = options_class.menu
        mgobn = lambda name:options_class.menu.get_option_by_name(name).get_value()

        self.titletext = mgobn('titletext')
        self.relationships = mgobn('relationships')
        self.year = mgobn('year')
        self.name_format = mgobn('name_format')
        self.country = mgobn('country')
        self.anniversaries = mgobn('anniversaries')
        self.start_dow = mgobn('start_dow')
        self.maiden_name = mgobn('maiden_name')
        self.alive = mgobn('alive')
        self.birthdays = mgobn('birthdays')
        self.text1 = mgobn('text1')
        self.text2 = mgobn('text2')
        self.text3 = mgobn('text3')
        self.filter_option =  menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter()
        pid = mgobn('pid')
        self.center_person = database.get_person_from_gramps_id(pid)
        if (self.center_person == None) :
            raise ReportError(_("Person %s is not in the Database") % pid )        

    def get_name(self, person, maiden_name = None):
        """ 
        Return person's name, unless maiden_name given, unless married_name 
        listed. 
        """
        # Get all of a person's names:
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == NameType.MARRIED:
                married_name = name
                break # use first
        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = Name(married_name)
            else:
                name = Name(primary_name)
                name.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        name.set_display_as(self.name_format)
        return _nd.display_name(name)

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
        self.progress = ProgressMeter(_('Birthday and Anniversary Report'))
        self.calendar = {}
        # get the information, first from holidays:
        if self.country != 0:
            self.__get_holidays()
        # get data from database:
        self.collect_data()
        # generate the report:
        self.doc.start_paragraph('BIR-Title') 
        self.doc.write_text(str(self.titletext) + ": " + str(self.year))
        self.doc.end_paragraph()
        if self.text1.strip() != "":
            self.doc.start_paragraph('BIR-Text1style')
            self.doc.write_text(str(self.text1))
            self.doc.end_paragraph()
        if self.text2.strip() != "":
            self.doc.start_paragraph('BIR-Text2style')
            self.doc.write_text(str(self.text2))
            self.doc.end_paragraph()
        if self.text3.strip() != "":
            self.doc.start_paragraph('BIR-Text3style')
            self.doc.write_text(str(self.text3))
            self.doc.end_paragraph()
        if self.relationships:
            name = self.center_person.get_primary_name()
            self.doc.start_paragraph('BIR-Text3style')
            self.doc.write_text(_("Relationships shown are to %s") % _nd.display_name(name))
            self.doc.end_paragraph()
        self.progress.set_pass(_('Formatting months...'), 12)
        for month in range(1, 13):
            self.progress.step()
            self.print_page(month)
        self.progress.close()

    def print_page(self, month):
        """ Prints a month as a page """
        year = self.year
        self.doc.start_paragraph('BIR-Monthstyle')
        self.doc.write_text(_dd[month].capitalize())
        self.doc.end_paragraph(.long_months)
        current_date = datetime.date(year, month, 1)
        current_ord = current_date.toordinal()
        started_day = {}
        for i in range(31):
            thisday = current_date.fromordinal(current_ord)
            if thisday.month == month:
                list = self.calendar.get(month, {}).get(thisday.day, [])
                for p in list:
                    p = p.replace("\n", " ")
                    if thisday not in started_day:
                        self.doc.start_paragraph("BIR-Daystyle")
                        self.doc.write_text(str(thisday.day))
                        self.doc.end_paragraph()
                        started_day[thisday] = 1
                    self.doc.start_paragraph("BIR-Datastyle")
                    self.doc.write_text(p)
                    self.doc.end_paragraph()
            current_ord += 1

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        people = self.database.iter_person_handles()
        self.progress.set_pass(_('Applying Filter...'), 
            self.database.get_number_of_people())
        people = self.filter.apply(self.database, people, self.progress)
        rel_calc = Relationship.get_relationship_calculator()

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

                prob_alive_date = Date(self.year, month, day)

                nyears = self.year - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self.maiden_name in ['spouse_first', 'spouse_last']: # get husband's last name:
                    if person.get_gender() == Person.FEMALE:
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
                                        father_lastname = father.get_primary_name().surname
                short_name = self.get_name(person, father_lastname)

                alive = probably_alive(person, self.database, prob_alive_date)
                if ((self.alive and alive) or not self.alive):

                    comment = ""
                    if self.relationships:
                        relation = rel_calc.get_one_relationship(
                                                         self.database, 
                                                         self.center_person, 
                                                         person)
                        if relation:
                            comment = " --- %s" % relation
                    if nyears == 0:
                        text = _('%(person)s, birth%(relation)s') % {
                            'person'   : short_name,
                            'relation' : comment}
                    else:
                        text = (ngettext('%(person)s, %(age)d%(relation)s', 
                                         '%(person)s, %(age)d%(relation)s', nyears)
                                % {'person'   : short_name,
                                   'age'      : nyears,
                                   'relation' : comment})

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
                                if event.type in [EventType.MARRIAGE, 
                                                             EventType.MARR_ALT]:
                                    are_married = event
                                elif event.type in [EventType.DIVORCE, 
                                                               EventType.ANNULMENT, 
                                                               EventType.DIV_FILING]:
                                    are_married = None
                            if are_married is not None:
                                for event_ref in fam.get_event_ref_list():
                                    event = self.database.get_event_from_handle(event_ref.ref)
                                    event_obj = event.get_date_object()
                                    year = event_obj.get_year()
                                    month = event_obj.get_month()
                                    day = event_obj.get_day()
                                    nyears = self.year - year

                                    if event_obj.is_valid():
                                        if nyears == 0:
                                            text = _("%(spouse)s and\n %(person)s, wedding") % {
                                                     'spouse' : spouse_name, 
                                                     'person' : short_name}
                                        else:
                                            text = (ngettext("%(spouse)s and\n %(person)s, %(nyears)d",
                                                             "%(spouse)s and\n %(person)s, %(nyears)d", nyears)
                                                    % {'spouse' : spouse_name, 
                                                       'person' : short_name, 
                                                       'nyears' : nyears})
 
                                            prob_alive_date = Date(self.year, month, day)
                                            alive1 = probably_alive(person, self.database, \
                                                prob_alive_date)
                                            alive2 = probably_alive(spouse, self.database, \
                                                prob_alive_date)
                                            if (self.alive and alive1 and alive2) or not self.alive:
                                                self.add_day_item(text, month, day)

#------------------------------------------------------------------------
#
# CalendarOptions
#
#------------------------------------------------------------------------
class CalendarOptions(MenuReportOptions):
    """ Options for the Birthday/Anniversary Report """
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
        fmt_list = _nd.get_name_format()
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
        
        option = BooleanOption(_("Include relationships to center person"), 
                               False)
        option.set_help(_("Include relationships to center person (slower)"))
        menu.add_option(category_name, "relationships", option)

        category_name = _("Text Options")
        
        titletext = StringOption(_("Title text"), 
                                 _("Birthday and Anniversary Report"))
        titletext.set_help(_("Title of calendar"))
        menu.add_option(category_name, "titletext", titletext)

        text1 = StringOption(_("Text Area 1"), _("My Calendar")) 
        text1.set_help(_("First line of text at bottom of calendar"))
        menu.add_option(category_name, "text1", text1)

        text2 = StringOption(_("Text Area 2"), _("Produced with Gramps"))
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
        self.make_my_style(default_style, "BIR-Title", 
                           _('Title text style'), 14, 
                           bold=1, justified="center")
        self.make_my_style(default_style, "BIR-Datastyle", 
                           _('Data text display'), 12, indent=1.0)
        self.make_my_style(default_style, "BIR-Daystyle", 
                           _('Day text style'), 12, indent=.5, 
                           italic=1, bold=1)
        self.make_my_style(default_style, "BIR-Monthstyle", 
                           _('Month text style'), 14, bold=1)
        self.make_my_style(default_style, "BIR-Text1style", 
                           _('Text at bottom, line 1'), 12, justified="center")
        self.make_my_style(default_style, "BIR-Text2style", 
                           _('Text at bottom, line 2'), 12, justified="center")
        self.make_my_style(default_style, "BIR-Text3style", 
                           _('Text at bottom, line 3'), 12, justified="center")
