#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008,2011  Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Heinz Brinker
# Copyright (C) 2013-2014  Paul Franklin
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
_ = glocale.translation.gettext
from gramps.gen.plug.menu import (FilterOption, PlaceListOption,
                                  EnumeratedListOption, BooleanOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, FONT_SERIF,
                                    INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gramps.gen.sort import Sort
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import PlaceType
from gramps.gen.errors import ReportError

class PlaceReport(Report):
    """
    Place Report class
    """
    def __init__(self, database, options, user):
        """
        Create the PlaceReport object produces the Place report.

        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - instance of a gen.user.User class

        This report needs the following parameters (class variables)
        that come in the options class.

        places          - List of places to report on.
        center          - Center of report, person or event
        incl_private    - Whether to include private data
        name_format     - Preferred format to display names

        """

        Report.__init__(self, database, options, user)

        self._user = user
        menu = options.menu

        stdoptions.run_private_data_option(self, menu)

        places = menu.get_option_by_name('places').get_value()
        self.center  = menu.get_option_by_name('center').get_value()

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_name_format_option(self, menu)
        self._nd = self._name_display

        filter_option = menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()

        self.sort = Sort(self.database)

        if self.filter.get_name() != '':
            # Use the selected filter to provide a list of place handles
            plist = self.database.iter_place_handles()
            self.place_handles = self.filter.apply(self.database, plist)
        else:
            # Use the place handles selected without a filter
            self.place_handles = self.__get_place_handles(places)

        if not self.place_handles:
            raise ReportError(_('Place Report'),
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
        place = self.database.get_place_from_handle(handle)
        location = get_main_location(self.database, place)

        place_details = [
            self._("Gramps ID: %s ") % place.get_gramps_id(),
            self._("Street: %s ") % location.get(PlaceType.STREET, ''),
            self._("Parish: %s ") % location.get(PlaceType.PARISH, ''),
            self._("Locality: %s ") % location.get(PlaceType.LOCALITY, ''),
            self._("City: %s ") % location.get(PlaceType.CITY, ''),
            self._("County: %s ") % location.get(PlaceType.COUNTY, ''),
            self._("State: %s") % location.get(PlaceType.STATE, ''),
            self._("Country: %s ") % location.get(PlaceType.COUNTRY, '')]
        self.doc.start_paragraph("PLC-PlaceTitle")
        place_title = place_displayer.display(self.database, place)
        self.doc.write_text(("%(nbr)s. %(place)s") %
                                {'nbr' : place_nbr,
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
                         self.database.find_backlink_handles(handle, ['Event'])]
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
            event = self.database.get_event_from_handle(evt_handle)
            if event: # will be None if marked private
                date = self._get_date(event.get_date_object())
                descr = event.get_description()
                event_type = self._(self._get_type(event.get_type()))

                person_list = []
                ref_handles = [x for x in
                               self.database.find_backlink_handles(evt_handle)]
                if not ref_handles: # since the backlink may point to private
                    continue        # data, ignore an event with no backlinks
                for (ref_type, ref_handle) in ref_handles:
                    if ref_type == 'Person':
                        person_list.append(ref_handle)
                    else:
                        family = self.database.get_family_from_handle(ref_handle)
                        father = family.get_father_handle()
                        if father:
                            person_list.append(father)
                        mother = family.get_mother_handle()
                        if mother:
                            person_list.append(mother)

                people = ""
                person_list = list(set(person_list))
                for p_handle in person_list:
                    person = self.database.get_person_from_handle(p_handle)
                    if person:
                        if people == "":
                            people = "%(name)s (%(id)s)" \
                                     % {'name': self._nd.display(person),
                                        'id': person.get_gramps_id()}
                        else:
                            people = self._("%(persons)s and %(name)s "
                                            "(%(id)s)") \
                                     % {'persons': people,
                                        'name': self._nd.display(person),
                                        'id': person.get_gramps_id()}

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
                         self.database.find_backlink_handles(handle, ['Event'])]

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
                           self.database.find_backlink_handles(evt_handle)]
            for (ref_type, ref_handle) in ref_handles:
                if ref_type == 'Person':
                    person = self.database.get_person_from_handle(ref_handle)
                    nameEntry = "%s (%s)" % (self._nd.display(person),
                                             person.get_gramps_id())
                else:
                    family = self.database.get_family_from_handle(ref_handle)
                    f_handle = family.get_father_handle()
                    m_handle = family.get_mother_handle()
                    if f_handle and m_handle:
                        father = self.database.get_person_from_handle(f_handle)
                        mother = self.database.get_person_from_handle(m_handle)
                        nameEntry = self._("%(father)s (%(father_id)s) and "
                                           "%(mother)s (%(mother_id)s)") % \
                                        { 'father' : self._nd.display(father),
                                          'father_id' : father.get_gramps_id(),
                                          'mother' : self._nd.display(mother),
                                          'mother_id' : mother.get_gramps_id()}
                    elif f_handle or m_handle:
                        if f_handle:
                            p_handle = f_handle
                        else:
                            p_handle = m_handle
                        person = self.database.get_person_from_handle(p_handle)

                        nameEntry = "%s (%s)" % \
                                     (self._nd.display(person),
                                      person.get_gramps_id())
                    else:
                        # No parents - bug #7299
                        continue

                if nameEntry in person_dict:
                    person_dict[nameEntry].append(evt_handle)
                else:
                    person_dict[nameEntry] = []
                    person_dict[nameEntry].append(evt_handle)

        keys = list(person_dict.keys())
        keys.sort()

        for entry in keys:
            people = entry
            person_dict[entry].sort(key=self.sort.by_date_key)
            for evt_handle in person_dict[entry]:
                event = self.database.get_event_from_handle(evt_handle)
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
            place = self.database.get_place_from_gramps_id(place_gid)
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
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the place report.
        """
        category_name = _("Report Options")

        # Reload filters to pick any new ones
        CustomFilters = None
        from gramps.gen.filters import CustomFilters, GenericFilter

        opt = FilterOption(_("Select using filter"), 0)
        opt.set_help(_("Select places using a filter"))
        filter_list = []
        filter_list.append(GenericFilter())
        filter_list.extend(CustomFilters.get_filters('Place'))
        opt.set_filters(filter_list)
        menu.add_option(category_name, "filter", opt)

        places = PlaceListOption(_("Select places individually"))
        places.set_help(_("List of places to report on"))
        menu.add_option(category_name, "places", places)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_name_format_option(menu, category_name)

        center = EnumeratedListOption(_("Center on"), "Event")
        center.set_items([
                ("Event",   _("Event")),
                ("Person", _("Person"))])
        center.set_help(_("If report is event or person centered"))
        menu.add_option(category_name, "center", center)

        stdoptions.add_localization_option(menu, category_name)

    def make_default_style(self, default_style):
        """
        Make the default output style for the Place report.
        """
        self.default_style = default_style
        self.__report_title_style()
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
        para.set_description(_('The style used for the title of the report.'))
        self.default_style.add_paragraph_style("PLC-ReportTitle", para)

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
        para.set_description(_('The style used for place title.'))
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
        para.set_description(_('The style used for place details.'))
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
        para.set_description(_('The style used for a column title.'))
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
        para.set_description(_('The style used for each section.'))
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
        para.set_description(_('The style used for event and person details.'))
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
