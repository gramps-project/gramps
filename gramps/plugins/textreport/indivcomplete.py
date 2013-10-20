#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007 Donald N. Allingham
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2009      Nick Hall
# Copyright (C) 2009      Benny Malengier
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2011      Tim G L Lyons
# Copyright (C) 2012      Mathieu MD
# Copyright (C) 2013      Paul Franklin
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
import copy
from collections import defaultdict

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventRoleType, EventType, Person, NoteType
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, INDEX_TYPE_TOC,
                                    PARA_ALIGN_CENTER)
from gramps.gen.datehandler import get_date
from gramps.gen.plug.menu import (BooleanOption, FilterOption, PersonOption,
                                  BooleanListOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import Bibliography
from gramps.gen.plug.report import endnotes as Endnotes
from gramps.gen.plug.report import stdoptions
from gramps.gen.display.name import displayer as global_name_display
from gramps.gen.utils.file import media_path_full

#------------------------------------------------------------------------
#
# Global variables (ones used in both classes here, that is)
#
#------------------------------------------------------------------------

def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
    return value
# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh

SECTION_CATEGORY = _("Sections") # only used in add_menu_options (so no _T_)
# headers for the sections
FACTS = _T_("Individual Facts")
EDUCATION = EventType.xml_str(EventType(EventType.EDUCATION))
CENSUS = EventType.xml_str(EventType(EventType.CENSUS))
ELECTED = EventType.xml_str(EventType(EventType.ELECTED))
MED_INFO = EventType.xml_str(EventType(EventType.MED_INFO))
MILITARY_SERV = EventType.xml_str(EventType(EventType.MILITARY_SERV))
NOB_TITLE = EventType.xml_str(EventType(EventType.NOB_TITLE))
OCCUPATION = EventType.xml_str(EventType(EventType.OCCUPATION))
PROPERTY = EventType.xml_str(EventType(EventType.PROPERTY))
RESIDENCE = EventType.xml_str(EventType(EventType.RESIDENCE))
FAMILY = _T_("Family")
CUSTOM = _T_("Custom")

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
                      EventType.UNKNOWN,
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
for event_group, type_list in GROUP_DICT.items():
    for event_type in type_list:
        TYPE2GROUP[event_type] = event_group

#------------------------------------------------------------------------
#
# IndivCompleteReport
#
#------------------------------------------------------------------------
class IndivCompleteReport(Report):

    def __init__(self, database, options, user):
        """
        Create the IndivCompleteReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter    - Filter to be applied to the people of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        cites     - Whether or not to include source information.
        sort      - Whether or not to sort events into chronological order.
        images    - Whether or not to include images.
        sections  - Which event groups should be given separate sections.
        name_format   - Preferred format to display names
        """

        Report.__init__(self, database, options, user)
        self._user = user

        menu = options.menu
        self.use_pagebreak = menu.get_option_by_name('pageben').get_value()
        self.use_srcs = menu.get_option_by_name('cites').get_value()
        self.use_srcs_notes = menu.get_option_by_name('incsrcnotes').get_value()
        
        self.sort = menu.get_option_by_name('sort').get_value()

        self.use_images = menu.get_option_by_name('images').get_value()
        self.use_gramps_id = menu.get_option_by_name('grampsid').get_value()

        filter_option = options.menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.bibli = None

        self.section_list = menu.get_option_by_name('sections').get_selected()

        # Copy the global NameDisplay so that we don't change application 
        # defaults.
        self._name_display = copy.deepcopy(global_name_display)
        name_format = menu.get_option_by_name("name_format").get_value()
        if name_format != 0:
            self._name_display.set_default_format(name_format)

        lang = menu.get_option_by_name('trans').get_value()
        self._locale = self.set_locale(lang)

    def write_fact(self, event_ref, event, event_group):
        """
        Writes a single event.
        """
        group_size = len(GROUP_DICT[event_group])
        role = event_ref.get_role()
        description = event.get_description()
        
        date = self._get_date(event.get_date_object())
        place = ''
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.database.get_place_from_handle(
                                            place_handle).get_title()
        date_place = combine(self._('%s in %s. '), '%s. ', date, place)

        if group_size != 1 or event_group == CUSTOM:
            # Groups with more than one type
            column_1 = self._(self._get_type(event.get_type()))
            if role not in (EventRoleType.PRIMARY, EventRoleType.FAMILY):
                column_1 = column_1 + ' (' + self._(role.xml_str()) + ')'
            column_2 = combine('%s, %s', '%s', description, date_place)
        else:
            # Groups with a single type (remove event type from first column)
            column_1 = date
            column_2 = combine('%s, %s', '%s', description, place)

        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli, self.database, event)

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
            self.doc.write_styled_note(text, note_format, 'IDS-Normal',
                        contains_html= note.get_type() == NoteType.HTML_CODE)
        
        self.doc.end_cell()
        self.doc.end_row()

    def write_p_entry(self, label, parent_name, rel_type, pmark=None):
        self.doc.start_row()
        self.normal_cell(label)
        if parent_name:
            # for example (a stepfather): John Smith, relationship: Step
            text = self._('%(parent-name)s, relationship: %(rel-type)s') % {
                                      'parent-name' : parent_name,
                                      'rel-type' : self._(rel_type)}
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
        self.doc.write_text(self._('Notes'))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        for notehandle in notelist:
            note = self.database.get_note_from_handle(notehandle)
            text = note.get_styledtext()
            note_format = note.get_format()
            self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell', 2)
            self.doc.write_styled_note(text, note_format, 'IDS-Normal',
                        contains_html= note.get_type() == NoteType.HTML_CODE)
            
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
        self.doc.write_text(self._("Alternate Parents"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        family_handle_list = self.person.get_parent_family_handle_list()
        for family_handle in family_handle_list:
            if (family_handle ==
                   self.person.get_main_parents_family_handle()):
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
                fname = self._name_display.display(father)
                mark = ReportUtils.get_person_mark(self.database, father)
                self.write_p_entry(self._('Father'), fname, frel, mark)
            else:
                self.write_p_entry(self._('Father'), '', '')

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mname = self._name_display.display(mother)
                mark = ReportUtils.get_person_mark(self.database, mother)
                self.write_p_entry(self._('Mother'), mname, mrel, mark)
            else:
                self.write_p_entry(self._('Mother'), '', '')
                
        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def get_name(self, person):
        name = self._name_display.display(person)
        if self.use_gramps_id:
            # RTL languages are the only reason for "translating" this
            return self._('%(name)s [%(gid)s]') % {
                                            'name': name, 
                                            'gid': person.get_gramps_id()}
        else:
            return name

    def write_alt_names(self):

        if len(self.person.get_alternate_names()) < 1:
            return
        
        self.doc.start_table("altnames","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(self._("Alternate Names"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for name in self.person.get_alternate_names():
            name_type = self._(self._get_type(name.get_type()))
            self.doc.start_row()
            self.normal_cell(name_type)
            text = self._name_display.display_name(name)
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli, self.database, name)
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
        self.doc.write_text(self._("Addresses"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for addr in alist:
            text = ReportUtils.get_address_str(addr)
            date = self._get_date(addr.get_date_object())
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli, self.database, addr)
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
        self.doc.write_text(self._("Marriages/Children"))
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
                text = self.get_name(spouse)
                mark = ReportUtils.get_person_mark(self.database, spouse)
            else:
                text = self._("unknown")
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
                self.normal_cell(self._("Children"))

                self.doc.start_cell("IDS-ListCell")

                for child_ref in child_ref_list:
                    self.doc.start_paragraph("IDS-Normal")
                    child = self.database.get_person_from_handle(child_ref.ref)
                    name = self.get_name(child)
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
        for ind, event_ref in enumerate(event_ref_list):
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event:
                    sort_value = event.get_date_object().get_sort_value()
                    #first sort on date, equal dates, then sort as in GUI.
                    event_list.append((str(sort_value) + "%04i"%ind, event_ref, event))

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
        self.doc.write_text(self._(event_group))
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
        event_dict = defaultdict(list)
        event_ref_list = self.person.get_event_ref_list()
        for event_ref in event_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                group = TYPE2GROUP[event.get_type().value]
                if _(group) not in self.section_list:
                    group = FACTS
                event_dict[group].append(event_ref)
                    
        # Write separate event group sections
        for group in SECTION_LIST:
            if group in event_dict:
                self.write_section(event_dict[group], group)

    def normal_cell(self, text, endnotes=None, mark=None):
        self.doc.start_cell('IDS-NormalCell')
        self.normal_paragraph(text, endnotes, mark)
        self.doc.end_cell()

    def normal_paragraph(self, text, endnotes=None, mark=None):
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text, mark)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()

    def write_report(self):
        plist = self.database.get_person_handles(sort_handles=True)
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
        self.bibli = Bibliography(Bibliography.MODE_DATE|Bibliography.MODE_PAGE)
        
        media_list = self.person.get_media_list()
        text = self._name_display.display(self.person)
        # feature request 2356: avoid genitive form
        title = self._("Summary of %s") % text
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        name = self.person.get_primary_name()
        text = self.get_name(self.person)
        mark = ReportUtils.get_person_mark(self.database, self.person)
        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli, self.database, name)

        family_handle = self.person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_inst_id = family.get_father_handle()
            if father_inst_id:
                father_inst = self.database.get_person_from_handle(
                    father_inst_id)
                father = self.get_name(father_inst)
                fmark = ReportUtils.get_person_mark(self.database, father_inst)
            else:
                father = ""
                fmark = None
            mother_inst_id = family.get_mother_handle()
            if mother_inst_id:
                mother_inst = self.database.get_person_from_handle(
                    mother_inst_id) 
                mother = self.get_name(mother_inst)
                mmark = ReportUtils.get_person_mark(self.database, mother_inst)
            else:
                mother = ""
                mmark = None
        else:
            father = ""
            fmark = None
            mother = ""
            mmark = None

        self.doc.start_table('person','IDS-PersonTable')
        self.doc.start_row()

        self.doc.start_cell('IDS-NormalCell')
        self.normal_paragraph("%s:" % self._("Name"))
        self.normal_paragraph("%s:" % self._("Gender"))
        self.normal_paragraph("%s:" % self._("Father"))
        self.normal_paragraph("%s:" % self._("Mother"))
        self.doc.end_cell()

        self.doc.start_cell('IDS-NormalCell')
        self.normal_paragraph(text, endnotes, mark)
        if self.person.get_gender() == Person.MALE:
            self.normal_paragraph(self._("Male"))
        elif self.person.get_gender() == Person.FEMALE:
            self.normal_paragraph(self._("Female"))
        else:
            self.normal_paragraph(self._("Unknown"))
        self.normal_paragraph(father, mark=fmark)
        self.normal_paragraph(mother, mark=mmark)
        self.doc.end_cell()

        self.doc.start_cell('IDS-NormalCell')
        if self.use_images and len(media_list) > 0:
            media0 = media_list[0]
            media_handle = media0.get_reference_handle()
            media = self.database.get_object_from_handle(media_handle)
            mime_type = media.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                filename = media_path_full(self.database, media.get_path())
                if os.path.exists(filename):
                    self.doc.add_media_object(filename, "right", 4.0, 4.0,
                                              crop=media0.get_rectangle())
                else:
                    self._user.warn(_("Could not add photo to page"),
                          "%s: %s" % (filename, _('File does not exist')))
        self.doc.end_cell()

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
            if self.use_pagebreak and self.bibli.get_citation_count():
                self.doc.page_break()
            Endnotes.write_endnotes(self.bibli, self.database, self.doc,
                                    printnotes=self.use_srcs_notes,
                                    elocale=self._locale)
            
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
                           _("Select the filter to be applied to the report."))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter."))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        stdoptions.add_name_format_option(menu, category_name)
        
        self.__update_filters()
        
        sort = BooleanOption(_("List events chronologically"), True)
        sort.set_help(_("Whether to sort events into chronological order."))
        menu.add_option(category_name, "sort", sort)

        pageben = BooleanOption(_("Page break before end notes"),False)
        pageben.set_help(
                     _("Whether to start a new page before the end notes."))
        menu.add_option(category_name, "pageben", pageben)
        
        cites = BooleanOption(_("Include Source Information"), True)
        cites.set_help(_("Whether to cite sources."))
        menu.add_option(category_name, "cites", cites)

        incsrcnotes = BooleanOption(_("Include sources notes"), False)
        incsrcnotes.set_help(_("Whether to include source notes in the "
            "Endnotes section. Only works if Include sources is selected."))
        menu.add_option(category_name, "incsrcnotes", incsrcnotes)

        images = BooleanOption(_("Include Photo/Images from Gallery"), True)
        images.set_help(_("Whether to include images."))
        menu.add_option(category_name, "images", images)

        grampsid = BooleanOption(_("Include Gramps ID"), False)
        grampsid.set_help(_("Whether to include Gramps ID next to names."))
        menu.add_option(category_name, "grampsid", grampsid)

        stdoptions.add_localization_option(menu, category_name)

        ################################
        category_name = SECTION_CATEGORY
        ################################
        opt = BooleanListOption(_("Event groups"))
        opt.set_help(_("Check if a separate section is required."))
        for section in SECTION_LIST:
            if section != FACTS:
                opt.add_button(_(section), True)

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
        
        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,40)
        tbl.set_column_width(2,40)
        default_style.add_table_style('IDS-PersonTable', tbl)

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
