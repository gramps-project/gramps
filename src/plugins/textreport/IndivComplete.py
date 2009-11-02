#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007 Donald N. Allingham
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2009      Nick Hall
# Copyright (C) 2009      Benny Malengier
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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.lib import EventRoleType, EventType, Person
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle, TableStyle,
                             TableCellStyle, FONT_SANS_SERIF, INDEX_TYPE_TOC,
                             PARA_ALIGN_CENTER)
import DateHandler
from gen.plug.menu import BooleanOption, FilterOption, PersonOption, \
                          BooleanListOption
from ReportBase import Report, ReportUtils, MenuReportOptions
from ReportBase import Bibliography, Endnotes
from BasicUtils import name_displayer as _nd
from Utils import media_path_full
from QuestionDialog import WarningDialog

#------------------------------------------------------------------------
#
# Global variables
#
#------------------------------------------------------------------------


SECTION_CATEGORY = _("Sections")
# Translated headers for the sections
FACTS = _("Individual Facts")
EDUCATION = str(EventType(EventType.EDUCATION))
CENSUS = str(EventType(EventType.CENSUS))
ELECTED = str(EventType(EventType.ELECTED))
MED_INFO = str(EventType(EventType.MED_INFO))
MILITARY_SERV = str(EventType(EventType.MILITARY_SERV))
NOB_TITLE = str(EventType(EventType.NOB_TITLE))
OCCUPATION = str(EventType(EventType.OCCUPATION))
PROPERTY = str(EventType(EventType.PROPERTY))
RESIDENCE = str(EventType(EventType.RESIDENCE))
FAMILY = _("Family")
CUSTOM = _("Custom")

SECTION_LIST = [FACTS, CENSUS, EDUCATION, ELECTED, MED_INFO,
                MILITARY_SERV, NOB_TITLE, OCCUPATION, PROPERTY,
                RESIDENCE, CUSTOM]

#Grouping of eventtypes in sections
GROUP_DICT = {FACTS: [EventType.ADOPT,
                      EventType.ADULT_CHRISTEN,
                      EventType.BAPTISM,
                      EventType.BAR_MITZVAH,
                      EventType.BAS_MITZVAH,
                      EventType.BIRTH,
                      EventType.BURIAL,
                      EventType.CAUSE_DEATH,
                      EventType.CHRISTEN,
                      EventType.CONFIRMATION,
                      EventType.CREMATION,
                      EventType.DEATH,
                      EventType.EMIGRATION,
                      EventType.FIRST_COMMUN,
                      EventType.IMMIGRATION,
                      EventType.NATURALIZATION,
                      EventType.ORDINATION,
                      EventType.PROBATE,
                      EventType.RELIGION,
                      EventType.RETIREMENT,
                      EventType.WILL],
             FAMILY: [EventType.ANNULMENT,
                      EventType.BLESS,
                      EventType.ENGAGEMENT,
                      EventType.DIVORCE,
                      EventType.DIV_FILING,                      
                      EventType.MARRIAGE,
                      EventType.MARR_ALT,
                      EventType.MARR_BANNS,
                      EventType.MARR_CONTR,
                      EventType.MARR_LIC,
                      EventType.MARR_SETTL,
                      EventType.NUM_MARRIAGES],
          EDUCATION: [EventType.DEGREE,
                      EventType.EDUCATION,
                      EventType.GRADUATION],
             CENSUS: [EventType.CENSUS],
            ELECTED: [EventType.ELECTED],
           MED_INFO: [EventType.MED_INFO],
      MILITARY_SERV: [EventType.MILITARY_SERV],
          NOB_TITLE: [EventType.NOB_TITLE],
         OCCUPATION: [EventType.OCCUPATION],
           PROPERTY: [EventType.PROPERTY],
          RESIDENCE: [EventType.RESIDENCE],
             CUSTOM: [EventType.CUSTOM],
        }

#Construct type to group map
TYPE2GROUP = {}
for event_group, type_list in GROUP_DICT.iteritems():
    for event_type in type_list:
        TYPE2GROUP[event_type] = event_group

#------------------------------------------------------------------------
#
# IndivCompleteReport
#
#------------------------------------------------------------------------
class IndivCompleteReport(Report):

    def __init__(self, database, options_class):
        """
        Create the IndivCompleteReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter    - Filter to be applied to the people of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        cites     - Whether or not to include source information.
        sort      - Whether ot not to sort events into chronological order.
        sections  - Which event groups should be given separate sections.
        """

        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.use_srcs = menu.get_option_by_name('cites').get_value()
        
        self.sort = menu.get_option_by_name('sort').get_value()

        filter_option = options_class.menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.bibli = None

        self.section_list = menu.get_option_by_name('sections').get_selected()

    def write_fact(self, event_ref, event, event_group):
        """
        Writes a single event.
        """
        group_size = len(GROUP_DICT[event_group])
        role = event_ref.get_role()
        description = event.get_description()
        
        date = DateHandler.get_date(event)
        place = ''
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.database.get_place_from_handle(
                                            place_handle).get_title()
        date_place = combine(_('%s in %s. '), '%s. ', date, place)

        if group_size != 1 or event_group == CUSTOM:
            # Groups with more than one type
            column_1 = str(event.get_type())
            if role not in (EventRoleType.PRIMARY, EventRoleType.FAMILY):
                column_1 = column_1 + ' (' + str(role) + ')'
            column_2 = combine('%s, %s', '%s', description, date_place)
        else:
            # Groups with a single type (remove event type from first column)
            column_1 = date
            column_2 = combine('%s, %s', '%s', description, place)

        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli, event)

        self.doc.start_row()
        self.normal_cell(column_1)
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(column_2)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()
        
        for notehandle in event.get_note_list():
            note = self.database.get_note_from_handle(notehandle)
            text = note.get_styledtext()
            note_format = note.get_format()
            self.doc.write_styled_note(text, note_format, 'IDS-Normal')
        
        self.doc.end_cell()
        self.doc.end_row()

    def write_p_entry(self, label, parent, rel, pmark=None):
        self.doc.start_row()
        self.normal_cell(label)

        if parent:
            text = '%(parent)s, relationship: %(relation)s' % { 
                                                            'parent': parent, 
                                                            'relation': rel}
            self.normal_cell(text, mark=pmark)
        else:
            self.normal_cell('')
        self.doc.end_row()

    def write_note(self):
        notelist = self.person.get_note_list()
        if not notelist:
            return
        self.doc.start_table('note','IDS-IndTable')
        self.doc.start_row()
        self.doc.start_cell('IDS-TableHead', 2)
        self.doc.start_paragraph('IDS-TableTitle')
        self.doc.write_text(_('Notes'))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        for notehandle in notelist:
            note = self.database.get_note_from_handle(notehandle)
            text = note.get_styledtext()
            note_format = note.get_format()
            self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell', 2)
            self.doc.write_styled_note(text, note_format, 'IDS-Normal')
            
            self.doc.end_cell()
            self.doc.end_row()

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_alt_parents(self):

        if len(self.person.get_parent_family_handle_list()) < 2:
            return
        
        self.doc.start_table("altparents","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Alternate Parents"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        family_handle_list = self.person.get_parent_family_handle_list()
        for family_handle in family_handle_list:
            if family_handle == \
                   self.person.get_main_parents_family_handle():
                continue
            
            family = self.database.get_family_from_handle(family_handle)
            
            # Get the mother and father relationships
            frel = ""
            mrel = ""
            child_handle = self.person.get_handle()
            child_ref_list = family.get_child_ref_list()
            for child_ref in child_ref_list:
                if child_ref.ref == child_handle:
                    frel = str(child_ref.get_father_relation())
                    mrel = str(child_ref.get_mother_relation())
            
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                fname = _nd.display(father)
                mark = ReportUtils.get_person_mark(self.database, father)
                self.write_p_entry(_('Father'), fname, frel, mark)
            else:
                self.write_p_entry(_('Father'), '', '')

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mname = _nd.display(mother)
                mark = ReportUtils.get_person_mark(self.database, mother)
                self.write_p_entry(_('Mother'), mname, mrel, mark)
            else:
                self.write_p_entry(_('Mother'), '', '')
                
        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_alt_names(self):

        if len(self.person.get_alternate_names()) < 1:
            return
        
        self.doc.start_table("altnames","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Alternate Names"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for name in self.person.get_alternate_names():
            name_type = str( name.get_type() )
            self.doc.start_row()
            self.normal_cell(name_type)
            text = _nd.display_name(name)
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli, name)
            self.normal_cell(text, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()
        
    def write_addresses(self):
        
        alist = self.person.get_address_list()

        if len(alist) == 0:
            return
        
        self.doc.start_table("addresses","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Addresses"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for addr in alist:
            text = ReportUtils.get_address_str(addr)
            date = DateHandler.get_date(addr)
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli, addr)
            self.doc.start_row()
            self.normal_cell(date)
            self.normal_cell(text, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()
        
    def write_families(self):

        if not len(self.person.get_family_handle_list()):
            return
        
        self.doc.start_table("three","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for family_handle in self.person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            if self.person.get_handle() == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
            self.doc.start_row()
            self.doc.start_cell("IDS-NormalCell", 2)
            self.doc.start_paragraph("IDS-Spouse")
            if spouse_id:
                spouse = self.database.get_person_from_handle(spouse_id)
                text = _nd.display(spouse)
                mark = ReportUtils.get_person_mark(self.database, spouse)
            else:
                text = _("unknown")
                mark = None
            self.doc.write_text(text, mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            event_ref_list = family.get_event_ref_list()
            for event_ref, event in self.get_event_list(event_ref_list):
                self.write_fact(event_ref, event, FAMILY)

            child_ref_list = family.get_child_ref_list()
            if len(child_ref_list):
                self.doc.start_row()
                self.normal_cell(_("Children"))

                self.doc.start_cell("IDS-ListCell")

                for child_ref in child_ref_list:
                    self.doc.start_paragraph("IDS-Normal")
                    child = self.database.get_person_from_handle(child_ref.ref)
                    name = _nd.display(child)
                    mark = ReportUtils.get_person_mark(self.database, child)
                    self.doc.write_text(name, mark)
                    self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def get_event_list(self, event_ref_list):
        """
        Return a list of (EventRef, Event) pairs.  Order by event date
        if the user option is set.
        """
        event_list = []
        for event_ref in event_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event:
                    sort_value = event.get_date_object().get_sort_value()
                    event_list.append((sort_value, event_ref, event))

        if self.sort:
            event_list.sort()

        return [(item[1], item[2]) for item in event_list]

    def write_section(self, event_ref_list, event_group):
        """
        Writes events in a single event group.
        """
        self.doc.start_table(event_group,"IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(event_group)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        for event_ref, event in self.get_event_list(event_ref_list):
            self.write_fact(event_ref, event, event_group)

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_events(self):
        """
        Write events.  The user can create separate sections for a
        pre-defined set of event groups.  When an event has a type
        contained within a group it is moved from the Individual Facts
        section into its own section.
        """
        event_dict = {}
        event_ref_list = self.person.get_event_ref_list()
        for event_ref in event_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                group = TYPE2GROUP[event.get_type().value]
                if group not in self.section_list:
                    group = FACTS
                if group in event_dict:
                    event_dict[group].append(event_ref)
                else:
                    event_dict[group] = [event_ref]
                    
        # Write separate event group sections
        for group in SECTION_LIST:
            if group in event_dict:
                self.write_section(event_dict[group], group)

    def normal_cell(self, text, endnotes=None, mark=None):
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text, mark)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()
        self.doc.end_cell()

    def write_report(self):
        plist = self.database.iter_person_handles()
        if self.filter:
            ind_list = self.filter.apply(self.database, plist)
        else:
            ind_list = plist
            
        for count, person_handle in enumerate(ind_list):
            self.person = self.database.get_person_from_handle(
                person_handle)
            self.write_person(count)

    def write_person(self, count):
        if count != 0:
            self.doc.page_break()
        self.bibli = Bibliography(Bibliography.MODE_PAGE)
        
        media_list = self.person.get_media_list()
        name = _nd.display(self.person)
        title = _("Summary of %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        if len(media_list) > 0:
            media_handle = media_list[0].get_reference_handle()
            media = self.database.get_object_from_handle(media_handle)
            mime_type = media.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                filename = media_path_full(self.database, media.get_path())
                if os.path.exists(filename):
                    self.doc.start_paragraph("IDS-Normal")
                    self.doc.add_media_object(filename, "right", 4.0, 4.0)
                    self.doc.end_paragraph()
                else:
                    WarningDialog(_("Could not add photo to page"),
                          "%s: %s" % (filename, _('File does not exist')))

        self.doc.start_table("one","IDS-IndTable")

        self.doc.start_row()
        self.normal_cell("%s:" % _("Name"))
        name = self.person.get_primary_name()
        text = _nd.display_name(name)
        mark = ReportUtils.get_person_mark(self.database, self.person)
        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli, name)
        self.normal_cell(text, endnotes, mark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Gender"))
        if self.person.get_gender() == Person.MALE:
            self.normal_cell(_("Male"))
        elif self.person.get_gender() == Person.FEMALE:
            self.normal_cell(_("Female"))
        else:
            self.normal_cell(_("Unknown"))
        self.doc.end_row()

        family_handle = self.person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_inst_id = family.get_father_handle()
            if father_inst_id:
                father_inst = self.database.get_person_from_handle(
                    father_inst_id)
                father = _nd.display(father_inst)
                fmark = ReportUtils.get_person_mark(self.database, father_inst)
            else:
                father = ""
                fmark = None
            mother_inst_id = family.get_mother_handle()
            if mother_inst_id:
                mother_inst = self.database.get_person_from_handle(
                    mother_inst_id) 
                mother = _nd.display(mother_inst)
                mmark = ReportUtils.get_person_mark(self.database, mother_inst)
            else:
                mother = ""
                mmark = None
        else:
            father = ""
            fmark = None
            mother = ""
            mmark = None

        self.doc.start_row()
        self.normal_cell("%s:" % _("Father"))
        self.normal_cell(father, mark=fmark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Mother"))
        self.normal_cell(mother, mark=mmark)
        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        self.write_alt_names()
        self.write_events()
        self.write_alt_parents()
        self.write_families()
        self.write_addresses()
        self.write_note()
        if self.use_srcs:
            Endnotes.write_endnotes(self.bibli, self.database, self.doc)
            
#------------------------------------------------------------------------
#
# IndivCompleteOptions
#
#------------------------------------------------------------------------
class IndivCompleteOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        ################################
        category_name = _("Report Options")
        ################################
        
        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
                           _("Select the filter to be applied to the report"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()
        
        sort = BooleanOption(_("List events chonologically"), True)
        sort.set_help(_("Whether to sort events into chonological order."))
        menu.add_option(category_name, "sort", sort)
        
        cites = BooleanOption(_("Include Source Information"), True)
        cites.set_help(_("Whether to cite sources."))
        menu.add_option(category_name, "cites", cites)

        ################################
        category_name = SECTION_CATEGORY
        ################################
        opt = BooleanListOption(_("Event groups"))
        opt.set_help(_("Check if a separate section is required."))
        for section in SECTION_LIST:
            if section != FACTS:
                opt.add_button(section, True)

        menu.add_option(category_name, "sections", opt)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, True)
        self.__filter.set_filters(filter_list)
        
    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [0, 2, 3, 4, 5]:
            # Filters 0, 2, 3, 4 and 5 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def make_default_style(self, default_style):
        """Make the default output style for the Individual Complete Report."""
        # Paragraph Styles
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        para = ParagraphStyle()
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_top_margin(ReportUtils.pt2cm(8))
        para.set_bottom_margin(ReportUtils.pt2cm(8))
        para.set_font(font)
        para.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("IDS-Title", para)
    
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_("The style used for category labels."))
        default_style.add_paragraph_style("IDS-TableTitle", para)

        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_("The style used for the spouse's name."))
        default_style.add_paragraph_style("IDS-Spouse", para)

        font = FontStyle()
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("IDS-Normal", para)
        
        # Table Styles
        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0, 20)
        tbl.set_column_width(1, 80)
        default_style.add_table_style("IDS-IndTable", tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0, 50)
        tbl.set_column_width(1, 50)
        default_style.add_table_style("IDS-ParentsTable", tbl)

        cell = TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        default_style.add_cell_style("IDS-TableHead", cell)

        cell = TableCellStyle()
        default_style.add_cell_style("IDS-NormalCell", cell)

        cell = TableCellStyle()
        cell.set_longlist(1)
        default_style.add_cell_style("IDS-ListCell", cell)
        
        Endnotes.add_endnote_styles(default_style)

#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------
def combine(format_both, format_single, str1, str2):
    """ Combine two strings with a given format. """
    text = ""
    if str1 and str2:
        text = format_both % (str1, str2)
    elif str1 and not str2:
        text = format_single % str1
    elif str2 and not str1:
        text = format_single % str2
    return text
