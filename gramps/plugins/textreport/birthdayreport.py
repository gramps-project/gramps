# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008-2012  Brian G. Matherly
# Copyright (C) 2009       Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012-2014  Paul Franklin
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import datetime, time

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.const import URL_HOMEPAGE
from gramps.gen.errors import ReportError
from gramps.gen.lib import NameType, EventType, Name, Date, Person, Surname
from gramps.gen.lib.date import gregorian
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                                    FONT_SERIF, PARA_ALIGN_RIGHT,
                                    PARA_ALIGN_LEFT, PARA_ALIGN_CENTER,
                                    IndexMark, INDEX_TYPE_TOC)
from gramps.gen.plug.menu import (BooleanOption, StringOption, NumberOption,
                                  EnumeratedListOption, FilterOption,
                                  PersonOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.utils.alive import probably_alive

import gramps.plugins.lib.libholiday as libholiday

# localization for BirthdayOptions only!!
from gramps.gen.datehandler import displayer as date_displayer

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value, context=''): # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value

_TITLE0 = _T_("Birthday and Anniversary Report")
_TITLE1 = _T_("My Birthday Report")
_TITLE2 = _T_("Produced with Gramps")
_DEADTXT = _T_("✝")

#------------------------------------------------------------------------
#
# BirthdayReport
#
#------------------------------------------------------------------------
class BirthdayReport(Report):
    """
    Create the BirthdayReport object that produces the report.

    name_format   - Preferred format to display names
    incl_private  - Whether to include private data
    """
    def __init__(self, database, options, user):
        Report.__init__(self, database, options, user)
        self._user = user
        menu = options.menu
        mgobn = lambda name:options.menu.get_option_by_name(name).get_value()

        stdoptions.run_private_data_option(self, menu)
        # (this report has its own "living people" option ("alive") already)

        self.titletext = mgobn('titletext')
        self.relationships = mgobn('relationships')
        self.year = mgobn('year')
        self.country = mgobn('country')
        self.maiden_name = mgobn('maiden_name')
        self.alive = mgobn('alive')
        self.birthdays = mgobn('birthdays')
        self.anniversaries = mgobn('anniversaries')
        self.death_anniversaries = mgobn('death_anniversaries')
        self.text1 = mgobn('text1')
        self.text2 = mgobn('text2')
        self.text3 = mgobn('text3')
        self.deadtxt = mgobn('deadtxt')
        self.filter_option = menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter()
        self.showyear = mgobn('showyear')
        pid = mgobn('pid')

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_name_format_option(self, menu)

        self.center_person = self.database.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

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
                surname_obj = name.get_primary_surname()
                surname_obj.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        return self._name_display.display_name(name)

    def add_day_item(self, text, month, day, person=None):
        """ Add an item to a day. """
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])
        day_list.append((text, person))
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
                    self.add_day_item(self._(holiday_name), month, day)
                    # FIXME translation only works for a limited set of things
                    # (the right fix is to somehow feed the locale into the
                    # HolidayTable class in plugins/lib/libholiday.py and then
                    # probably changing all the holiday code to somehow defer
                    # the translation of holidays, until it can be based
                    # on the passed-in locale, but since that would probably
                    # also mean checking every use of holidays I don't think
                    # it is advisable to do, with a release so imminent)
                    # it is also debatable whether it is worth bothering at
                    # all, since it is hard for me to imagine why a user would
                    # be wanting to generate a translated report with holidays
                    # since I believe its main use will be for dates of people

    def write_report(self):
        """
        The short method that runs through each month and creates a page.
        """
        # initialize the dict to fill:
        self.calendar = {}
        # get the information, first from holidays:
        if self.country != 0:
            self.__get_holidays()
        # get data from database:
        self.collect_data()
        # generate the report:
        self.doc.start_paragraph('BIR-Title')
        if self.titletext == _(_TITLE0):
            title = self._("%(str1)s: %(str2)s") % {
                'str1' : self._(_TITLE0),
                'str2' : self._get_date(Date(self.year))} # localized year
        else:
            title = self._("%(str1)s: %(str2)s") % {
                'str1' : str(self.titletext),
                'str2' : self._get_date(Date(self.year))}
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        if self.text1.strip() != "":
            self.doc.start_paragraph('BIR-Text1style')
            text1 = str(self.text1)
            if text1 == _(_TITLE1):
                text1 = self._(_TITLE1)
            self.doc.write_text(text1)
            self.doc.end_paragraph()
        if self.text2.strip() != "":
            self.doc.start_paragraph('BIR-Text2style')
            text2 = str(self.text2)
            if text2 == _(_TITLE2):
                text2 = self._(_TITLE2)
            self.doc.write_text(text2)
            self.doc.end_paragraph()
        if self.text3.strip() != "":
            self.doc.start_paragraph('BIR-Text3style')
            self.doc.write_text(str(self.text3))
            self.doc.end_paragraph()
        if self.relationships:
            name = self.center_person.get_primary_name()
            self.doc.start_paragraph('BIR-Text3style')
            mark = utils.get_person_mark(self.database,
                                               self.center_person)
            # feature request 2356: avoid genitive form
            self.doc.write_text(self._("Relationships shown are to %s") %
                                self._name_display.display_name(name), mark)
            self.doc.end_paragraph()
        with self._user.progress(_('Birthday and Anniversary Report'),
                _('Formatting months...'), 12) as step:
            for month in range(1, 13):
                step()
                self.print_page(month)

    def print_page(self, month):
        """ Prints a month as a page """
        year = self.year
        dd = self._locale.date_displayer
        self.doc.start_paragraph('BIR-Monthstyle')
        self.doc.write_text(dd.long_months[month].capitalize())
        self.doc.end_paragraph()
        current_date = datetime.date(year, month, 1)
        current_ord = current_date.toordinal()
        started_day = {}
        for i in range(31):
            thisday = current_date.fromordinal(current_ord)
            if thisday.month == month:
                list = self.calendar.get(month, {}).get(thisday.day, [])
                for p, p_obj in list:
                    mark = utils.get_person_mark(self.database, p_obj)
                    p = p.replace("\n", " ")
                    if thisday not in started_day:
                        self.doc.start_paragraph("BIR-Daystyle")
                        self.doc.write_text(str(thisday.day))
                        self.doc.end_paragraph()
                        started_day[thisday] = 1
                    self.doc.start_paragraph("BIR-Datastyle")
                    self.doc.write_text(p, mark)
                    self.doc.end_paragraph()
            current_ord += 1

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        people = self.database.iter_person_handles()
        people = self.filter.apply(self.database, people, user=self._user)

        ngettext = self._locale.translation.ngettext # to see "nearby" comments
        rel_calc = get_relationship_calculator(reinit=True,
                                               clocale=self._locale)

        with self._user.progress(_('Birthday and Anniversary Report'),
                _('Reading database...'), len(people)) as step:
            for person_handle in people:
                step()
                person = self.database.get_person_from_handle(person_handle)
                birth_ref = person.get_birth_ref()
                birth_date = None
                if birth_ref:
                    birth_event = self.database.get_event_from_handle(birth_ref.ref)
                    birth_date = birth_event.get_date_object()

                if (self.birthdays and birth_date is not None and birth_date.is_valid()):
                    birth_date = gregorian(birth_date)

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
                                            primary_name = father.get_primary_name()
                                            if primary_name:
                                                father_lastname = Surname.get_surname(primary_name.get_primary_surname())

                    short_name = self.get_name(person, father_lastname)

                    alive = probably_alive(person, self.database, prob_alive_date)
                    if ((self.alive and alive) or not self.alive):

                        comment = ""
                        if self.relationships:
                            relation = rel_calc.get_one_relationship(
                                                             self.database,
                                                             self.center_person,
                                                             person,
                                                             olocale=self._locale)
                            if relation:
                                # FIXME this won't work for RTL languages
                                comment = " --- %s" % relation
                        deadtxt = ""
                        if (not alive):
                            deadtxt = self.deadtxt
                        yeartxt = ""
                        if self.showyear:
                            yeartxt = "(%s) " % year
                        if nyears == 0:
                            text = self._('* %(person)s, birth%(relation)s') % {
                                'person'   : short_name,
                                'relation' : comment}
                        else:
                            # translators: leave all/any {...} untranslated
                            text = ngettext('* {year}{person}{dead}, {age}{relation}',
                                            '* {year}{person}{dead}, {age}{relation}',
                                            nyears).format(year=yeartxt,
                                                           person=short_name,
                                                           dead=deadtxt,
                                                           age=nyears,
                                                           relation=comment)

                        self.add_day_item(text, month, day, person)
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
                                # TEMP: this will handle ordered events
                                # Gramps 3.0 will have a new mechanism for start/stop events
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
                                        if event_obj is not Date.EMPTY and event_obj.is_valid():
                                            event_obj = gregorian(event_obj)
                                        year = event_obj.get_year()
                                        month = event_obj.get_month()
                                        day = event_obj.get_day()
                                        nyears = self.year - year

                                        if event_obj.is_valid():
                                            prob_alive_date = Date(self.year, month, day)
                                            alive1 = probably_alive(person, self.database,
                                                                        prob_alive_date)
                                            alive2 = probably_alive(spouse, self.database,
                                                                        prob_alive_date)
                                            deadtxt1 = ""
                                            deadtxt2 = ""
                                            if (not alive1):
                                                deadtxt1 = self.deadtxt
                                            if (not alive2):
                                                deadtxt2 = self.deadtxt
                                            yeartxt = ""
                                            if self.showyear:
                                                yeartxt = "(%s) " % year
                                            if nyears == 0:
                                                text = self._("⚭ %(spouse)s and\n %(person)s, wedding") % {
                                                         'spouse' : spouse_name,
                                                         'person' : short_name}
                                            else:
                                                # translators: leave all/any {...} untranslated
                                                text = ngettext("⚭ {year}{spouse}{deadtxt2} and\n {person}{deadtxt1}, {nyears}",
                                                                "⚭ {year}{spouse}{deadtxt2} and\n {person}{deadtxt1}, {nyears}",
                                                                nyears).format(year=yeartxt, spouse=spouse_name, deadtxt2=deadtxt2, person=short_name, deadtxt1=deadtxt1, nyears=nyears)
                                                if (self.alive and alive1 and alive2) or not self.alive:
                                                    self.add_day_item(text, month, day, spouse)

                death_ref = person.get_death_ref()
                death_date = None
                if death_ref:
                    death_event = self.database.get_event_from_handle(death_ref.ref)
                    death_date = death_event.get_date_object()

                if (self.death_anniversaries and death_date is not None and death_date.is_valid()):
                    death_date = gregorian(death_date)

                    year = death_date.get_year()
                    month = death_date.get_month()
                    day = death_date.get_day()

                    nyears = self.year - year

                    comment = ""
                    if self.relationships:
                            relation = rel_calc.get_one_relationship(
                                                             self.database,
                                                             self.center_person,
                                                             person,
                                                             olocale=self._locale)
                            if relation:
                                # FIXME this won't work for RTL languages
                                comment = " --- %s" % relation
                    yeartxt = ""
                    if self.showyear:
                        yeartxt = "(%s) " % year
                    if nyears == 0:
                        text = _('✝ {person}, death {relation}').format(person=short_name,relation=comment)
                    else:
                        text = ngettext('✝ {year}{person}, {age}{relation}',
                                        '✝ {year}{person}, {age}{relation}',
                                        nyears).format(year=yeartxt,
                                                       person=short_name,
                                                       age=nyears,
                                                       relation=comment)
                    self.add_day_item(text, month, day, person)

#------------------------------------------------------------------------
#
# BirthdayOptions
#
#------------------------------------------------------------------------
class BirthdayOptions(MenuReportOptions):
    """ Options for the Birthday/Anniversary Report """
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        return self.__filter.get_filter().get_name()

    def add_menu_options(self, menu):
        """ Add the options for the text birthday report """
        category_name = _("Report Options")

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Select the filter to be applied to the report."))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter."))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        titletext = StringOption(_("Title text"), _(_TITLE0))
        titletext.set_help(_("Title of report"))
        menu.add_option(category_name, "titletext", titletext)

        text1 = StringOption(_("Text Area 1"), _(_TITLE1))
        text1.set_help(_("First line of text at bottom of report"))
        menu.add_option(category_name, "text1", text1)

        text2 = StringOption(_("Text Area 2"), _(_TITLE2))
        text2.set_help(_("Second line of text at bottom of report"))
        menu.add_option(category_name, "text2", text2)

        text3 = StringOption(_("Text Area 3"), URL_HOMEPAGE,)
        text3.set_help(_("Third line of text at bottom of report"))
        menu.add_option(category_name, "text3", text3)

        category_name = _("Report Options (2)")

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        stdoptions.add_private_data_option(menu, category_name)

        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the report"))
        menu.add_option(category_name, "alive", alive)

        deadtxt = StringOption(_("Dead Symbol"), _(_DEADTXT))
        deadtxt.set_help(_("This will show after name to indicate that person is dead"))
        menu.add_option(category_name, "deadtxt", deadtxt)

        self.__update_filters()

        stdoptions.add_localization_option(menu, category_name)

        showyear = BooleanOption(_("Show event year"), True)
        showyear.set_help(_("Prints the year the event took place in the report"))
        menu.add_option(category_name, "showyear", showyear)

        category_name = _("Content")

        year = NumberOption(_("Year of report"), time.localtime()[0],
                            1000, 3000)
        year.set_help(_("Year of report"))
        menu.add_option(category_name, "year", year)

        country = EnumeratedListOption(_("Country for holidays"), 0)
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
        country.set_help(_("Select the country to see associated holidays"))
        menu.add_option(category_name, "country", country)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item(
            "spouse_first",
            _("Wives use husband's surname (from first family listed)"))
        maiden_name.add_item(
            "spouse_last",
            _("Wives use husband's surname (from last family listed)"))
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)

        birthdays = BooleanOption(_("Include birthdays"), True)
        birthdays.set_help(_("Whether to include birthdays"))
        menu.add_option(category_name, "birthdays", birthdays)

        anniversaries = BooleanOption(_("Include anniversaries"), True)
        anniversaries.set_help(_("Whether to include anniversaries"))
        menu.add_option(category_name, "anniversaries", anniversaries)

        death_anniversaries = BooleanOption(_("Include death anniversaries"), True)
        death_anniversaries.set_help(_("Whether to include anniversaries of death"))
        menu.add_option(category_name, "death_anniversaries", death_anniversaries)

        show_relships = BooleanOption(
            _("Include relationship to center person"), False)
        show_relships.set_help(
            _("Whether to include relationships to the center person"))
        menu.add_option(category_name, "relationships", show_relships)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = utils.get_person_filters(person,
                                               include_single=False,
                                               name_format=nfv)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 0: # "Entire Database" (as "include_single=False")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

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
