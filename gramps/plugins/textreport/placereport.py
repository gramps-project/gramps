#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008,2011  Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Heinz Brinker
# Copyright (C) 2013-2016  Paul Franklin
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

"""Place Report"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.plug.menu import (FilterOption, PlaceListOption,
                                  EnumeratedListOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, FONT_SERIF,
                                    INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gramps.gen.sort import Sort
from gramps.gen.utils.location import get_location_list
from gramps.gen.display.place import displayer as _pd
from gramps.gen.errors import ReportError
from gramps.gen.proxy import LivingProxyDb, CacheProxyDb

class PlaceReport(Report):
    """
    Place Report class
    """
    def __init__(self, database, options, user):
        """
        Create the PlaceReport object produces the Place report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - instance of a gen.user.User class

        This report needs the following parameters (class variables)
        that come in the options class.

        places          - List of places to report on.
        center          - Center of report, person or event
        incl_private    - Whether to include private data
        name_format     - Preferred format to display names
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """

        Report.__init__(self, database, options, user)

        self._user = user
        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        living_opt = stdoptions.run_living_people_option(self, menu,
                                                         self._locale)
        self.database = CacheProxyDb(self.database)
        self._db = self.database

        self._lv = menu.get_option_by_name('living_people').get_value()
        for (value, description) in living_opt.get_items(xml_items=True):
            if value == self._lv:
                living_desc = self._(description)
                break
        self.living_desc = self._("(Living people: %(option_name)s)"
                                 ) % {'option_name': living_desc}

        places = menu.get_option_by_name('places').get_value()
        self.center = menu.get_option_by_name('center').get_value()

        stdoptions.run_name_format_option(self, menu)
        self._nd = self._name_display

        self.place_format = menu.get_option_by_name("place_format").get_value()

        filter_option = menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()

        self.sort = Sort(self._db)

        self.place_handles = []
        if self.filter.get_name() != '':
            # Use the selected filter to provide a list of place handles
            plist = self._db.iter_place_handles()
            self.place_handles = self.filter.apply(self._db, plist,
                                                   user=self._user)

        if places:
            # Add places selected individually
            self.place_handles += self.__get_place_handles(places)

        if not self.place_handles:
            raise ReportError(
                _('Place Report'),
                _('Please select at least one place before running this.'))

        self.place_handles.sort(key=self.sort.by_place_title_key)

    def write_report(self):
        """
        The routine that actually creates the report.
        At this point, the document is opened and ready for writing.
        """

        # Write the title line. Set in INDEX marker so that this section will be
        # identified as a major category if this is included in a Book report.

        title = self._("Place Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph("PLC-ReportTitle")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        if self._lv != LivingProxyDb.MODE_INCLUDE_ALL:
            self.doc.start_paragraph("PLC-ReportSubtitle")
            self.doc.write_text(self.living_desc)
            self.doc.end_paragraph()
        self.__write_all_places()

    def __write_all_places(self):
        """
        This procedure writes out each of the selected places.
        """
        place_nbr = 1

        with self._user.progress(_("Place Report"),
                                 _("Generating report"),
                                 len(self.place_handles)) as step:

            for handle in self.place_handles:
                self.__write_place(handle, place_nbr)
                if self.center == "Event":
                    self.__write_referenced_events(handle)
                elif self.center == "Person":
                    self.__write_referenced_persons(handle)
                else:
                    raise AttributeError("no such center: '%s'" % self.center)
                place_nbr += 1
                # increment progress bar
                step()


    def __write_place(self, handle, place_nbr):
        """
        This procedure writes out the details of a single place
        """
        place = self._db.get_place_from_handle(handle)

        place_details = [self._("Gramps ID: %s ") % place.get_gramps_id()]
        for level in get_location_list(self._db, place):
            # translators: needed for French, ignore otherwise
            place_details.append(self._("%(str1)s: %(str2)s"
                                       ) % {'str1': self._(level[1].xml_str()),
                                            'str2': level[0]})

        place_names = ''
        all_names = place.get_all_names()
        if len(all_names) > 1 or __debug__:
            for place_name in all_names:
                if place_names != '':
                    # translators: needed for Arabic, ignore otherwise
                    place_names += self._(", ")
                place_names += '%s' % place_name.get_value()
                if place_name.get_language() != '' or __debug__:
                    place_names += ' (%s)' % place_name.get_language()
            place_details += [self._("All Names: %s", "places") % place_names,]
        self.doc.start_paragraph("PLC-PlaceTitle")
        place_title = _pd.display(self._db, place, None, self.place_format)
        self.doc.write_text(("%(nbr)s. %(place)s") % {'nbr' : place_nbr,
                                                      'place' : place_title})
        self.doc.end_paragraph()

        for item in place_details:
            self.doc.start_paragraph("PLC-PlaceDetails")
            self.doc.write_text(item)
            self.doc.end_paragraph()

    def __write_referenced_events(self, handle):
        """
        This procedure writes out each of the events related to the place
        """
        event_handles = [event_handle for (object_type, event_handle) in
                         self._db.find_backlink_handles(handle, ['Event'])]
        event_handles.sort(key=self.sort.by_date_key)

        if event_handles:
            self.doc.start_paragraph("PLC-Section")
            title = self._("Events that happened at this place")
            self.doc.write_text(title)
            self.doc.end_paragraph()
            self.doc.start_table("EventTable", "PLC-EventTable")
            column_titles = [self._("Date"), self._("Type of Event"),
                             self._("Person"), self._("Description")]
            self.doc.start_row()
            for title in column_titles:
                self.doc.start_cell("PLC-TableColumn")
                self.doc.start_paragraph("PLC-ColumnTitle")
                self.doc.write_text(title)
                self.doc.end_paragraph()
                self.doc.end_cell()
            self.doc.end_row()

        for evt_handle in event_handles:
            event = self._db.get_event_from_handle(evt_handle)
            if event: # will be None if marked private
                date = self._get_date(event.get_date_object())
                descr = event.get_description()
                event_type = self._(self._get_type(event.get_type()))

                person_list = []
                ref_handles = [x for x in
                               self._db.find_backlink_handles(evt_handle)]
                if not ref_handles: # since the backlink may point to private
                    continue        # data, ignore an event with no backlinks
                for (ref_type, ref_handle) in ref_handles:
                    if ref_type == 'Person':
                        person_list.append(ref_handle)
                    else:
                        family = self._db.get_family_from_handle(ref_handle)
                        father = family.get_father_handle()
                        if father:
                            person_list.append(father)
                        mother = family.get_mother_handle()
                        if mother:
                            person_list.append(mother)

                people = ""
                person_list = list(set(person_list))
                for p_handle in person_list:
                    person = self._db.get_person_from_handle(p_handle)
                    if person:
                        person_name = self._nd.display(person)
                        if people == "":
                            people = "%(name)s (%(id)s)" % {
                                'name' : person_name,
                                'id'   : person.get_gramps_id()}
                        else:
                            people = self._("%(persons)s and %(name)s (%(id)s)"
                                           ) % {'persons' : people,
                                                'name'    : person_name,
                                                'id' : person.get_gramps_id()}

                event_details = [date, event_type, people, descr]
                self.doc.start_row()
                for detail in event_details:
                    self.doc.start_cell("PLC-Cell")
                    self.doc.start_paragraph("PLC-Details")
                    self.doc.write_text("%s " % detail)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                self.doc.end_row()

        if event_handles:
            self.doc.end_table()

    def __write_referenced_persons(self, handle):
        """
        This procedure writes out each of the people related to the place
        """
        event_handles = [event_handle for (object_type, event_handle) in
                         self._db.find_backlink_handles(handle, ['Event'])]

        if event_handles:
            self.doc.start_paragraph("PLC-Section")
            title = self._("People associated with this place")
            self.doc.write_text(title)
            self.doc.end_paragraph()
            self.doc.start_table("EventTable", "PLC-PersonTable")
            column_titles = [self._("Person"), self._("Type of Event"), \
                             self._("Description"), self._("Date")]
            self.doc.start_row()
            for title in column_titles:
                self.doc.start_cell("PLC-TableColumn")
                self.doc.start_paragraph("PLC-ColumnTitle")
                self.doc.write_text(title)
                self.doc.end_paragraph()
                self.doc.end_cell()
            self.doc.end_row()

        person_dict = {}
        for evt_handle in event_handles:
            ref_handles = [x for x in
                           self._db.find_backlink_handles(evt_handle)]
            for (ref_type, ref_handle) in ref_handles:
                if ref_type == 'Person':
                    person = self._db.get_person_from_handle(ref_handle)
                    name_entry = "%s (%s)" % (self._nd.display(person),
                                              person.get_gramps_id())
                else:
                    family = self._db.get_family_from_handle(ref_handle)
                    f_handle = family.get_father_handle()
                    m_handle = family.get_mother_handle()
                    if f_handle and m_handle:
                        father = self._db.get_person_from_handle(f_handle)
                        mother = self._db.get_person_from_handle(m_handle)
                        father_name = self._nd.display(father)
                        mother_name = self._nd.display(mother)
                        father_id = father.get_gramps_id()
                        mother_id = mother.get_gramps_id()
                        name_entry = self._("%(father)s (%(father_id)s) and "
                                            "%(mother)s (%(mother_id)s)"
                                           ) % {'father'    : father_name,
                                                'father_id' : father_id,
                                                'mother'    : mother_name,
                                                'mother_id' : mother_id}
                    elif f_handle or m_handle:
                        if f_handle:
                            p_handle = f_handle
                        else:
                            p_handle = m_handle
                        person = self._db.get_person_from_handle(p_handle)

                        name_entry = "%s (%s)" % (self._nd.display(person),
                                                  person.get_gramps_id())
                    else:
                        # No parents - bug #7299
                        continue

                if name_entry in person_dict:
                    person_dict[name_entry].append(evt_handle)
                else:
                    person_dict[name_entry] = []
                    person_dict[name_entry].append(evt_handle)

        keys = list(person_dict.keys())
        keys.sort()

        for entry in keys:
            people = entry
            person_dict[entry].sort(key=self.sort.by_date_key)
            for evt_handle in person_dict[entry]:
                event = self._db.get_event_from_handle(evt_handle)
                if event:
                    date = self._get_date(event.get_date_object())
                    descr = event.get_description()
                    event_type = self._(self._get_type(event.get_type()))
                else:
                    date = ''
                    descr = ''
                    event_type = ''
                event_details = [people, event_type, descr, date]
                self.doc.start_row()
                for detail in event_details:
                    self.doc.start_cell("PLC-Cell")
                    self.doc.start_paragraph("PLC-Details")
                    self.doc.write_text("%s " % detail)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                people = "" # do not repeat the name on the next event
                self.doc.end_row()

        if event_handles:
            self.doc.end_table()

    def __get_place_handles(self, places):
        """
        This procedure converts a string of place GIDs to a list of handles
        """
        place_handles = []
        for place_gid in places.split():
            place = self._db.get_place_from_gramps_id(place_gid)
            if place is not None:
                #place can be None if option is gid of other fam tree
                place_handles.append(place.get_handle())

        return place_handles

#------------------------------------------------------------------------
#
# PlaceOptions
#
#------------------------------------------------------------------------
class PlaceOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__filter = None
        self.__places = None
        self.__pf = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        subject = ""
        if self.__filter.get_filter().get_name():
            # Use the selected filter's name, if any
            subject += self.__filter.get_filter().get_name()
        if self.__places.get_value():
            # Add places selected individually, if any
            for place_id in self.__places.get_value().split():
                if subject:
                    subject += " + "
                place = self.__db.get_place_from_gramps_id(place_id)
                subject += _pd.display(self.__db, place, None,
                                       self.__pf.get_value())
        return subject

    def add_menu_options(self, menu):
        """
        Add options to the menu for the place report.
        """
        category_name = _("Report Options")

        # Reload filters to pick any new ones
        CustomFilters = None
        from gramps.gen.filters import CustomFilters, GenericFilter

        self.__filter = FilterOption(_("Select using filter"), 0)
        self.__filter.set_help(_("Select places using a filter"))
        filter_list = []
        filter_list.append(GenericFilter())
        filter_list.extend(CustomFilters.get_filters('Place'))
        self.__filter.set_filters(filter_list)
        menu.add_option(category_name, "filter", self.__filter)

        self.__places = PlaceListOption(_("Select places individually"))
        self.__places.set_help(_("List of places to report on"))
        menu.add_option(category_name, "places", self.__places)

        center = EnumeratedListOption(_("Center on"), "Event")
        center.set_items([("Event", _("Event")), ("Person", _("Person"))])
        center.set_help(_("If report is event or person centered"))
        menu.add_option(category_name, "center", center)

        category_name = _("Report Options (2)")

        stdoptions.add_name_format_option(menu, category_name)

        self.__pf = stdoptions.add_place_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    def make_default_style(self, default_style):
        """
        Make the default output style for the Place report.
        """
        self.default_style = default_style
        self.__report_title_style()
        self.__report_subtitle_style()
        self.__place_title_style()
        self.__place_details_style()
        self.__column_title_style()
        self.__section_style()
        self.__event_table_style()
        self.__details_style()
        self.__cell_style()
        self.__table_column_style()

    def __report_title_style(self):
        """
        Define the style used for the report title
        """
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title.'))
        self.default_style.add_paragraph_style("PLC-ReportTitle", para)

    def __report_subtitle_style(self):
        """
        Define the style used for the report subtitle
        """
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=12, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the subtitle.'))
        self.default_style.add_paragraph_style("PLC-ReportSubtitle", para)

    def __place_title_style(self):
        """
        Define the style used for the place title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.75)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the section headers.'))
        self.default_style.add_paragraph_style("PLC-PlaceTitle", para)

    def __place_details_style(self):
        """
        Define the style used for the place details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_description(_('The style used for details.'))
        self.default_style.add_paragraph_style("PLC-PlaceDetails", para)

    def __column_title_style(self):
        """
        Define the style used for the event table column title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_description(_('The basic style used for table headings.'))
        self.default_style.add_paragraph_style("PLC-ColumnTitle", para)

    def __section_style(self):
        """
        Define the style used for each section
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, italic=0, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.5)
        para.set_bottom_margin(0.25)
        para.set_description(_('The basic style used for the text display.'))
        self.default_style.add_paragraph_style("PLC-Section", para)

    def __event_table_style(self):
        """
        Define the style used for event table
        """
        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 25)
        table.set_column_width(1, 15)
        table.set_column_width(2, 35)
        table.set_column_width(3, 25)
        self.default_style.add_table_style("PLC-EventTable", table)
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 35)
        table.set_column_width(1, 15)
        table.set_column_width(2, 25)
        table.set_column_width(3, 25)
        self.default_style.add_table_style("PLC-PersonTable", table)

    def __details_style(self):
        """
        Define the style used for person and event details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for the items and values.'))
        self.default_style.add_paragraph_style("PLC-Details", para)

    def __cell_style(self):
        """
        Define the style used for cells in the event table
        """
        cell = TableCellStyle()
        self.default_style.add_cell_style("PLC-Cell", cell)

    def __table_column_style(self):
        """
        Define the style used for event table columns
        """
        cell = TableCellStyle()
        cell.set_bottom_border(1)
        self.default_style.add_cell_style('PLC-TableColumn', cell)
