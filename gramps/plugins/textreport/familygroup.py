#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2015       Gerald Kunzmann <gerald@gkunzmann.de>
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

"""Reports/Text Reports/Family Group Report"""

#------------------------------------------------------------------------
#
# Python Library
#
#------------------------------------------------------------------------
from functools import partial

#------------------------------------------------------------------------
#
# Gramps
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.lib import EventRoleType, EventType, NoteType, Person
from gramps.gen.plug.menu import BooleanOption, FamilyOption, FilterOption
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, FONT_SERIF,
                                    INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gramps.gen.display.place import displayer as _pd
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.errors import ReportError
from gramps.gen.utils.db import family_name

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup(Report):
    """ Family Group Report """

    def __init__(self, database, options, user):
        """
        Create the FamilyGroup object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        filter    - Filter to be applied to the families of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        incattrs      - Whether to include attributes
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)
        self._user = user
        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())
        self._ = self._locale.translation.sgettext # needed for English

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)
        self.db = self.database

        self.filter = menu.get_option_by_name('filter').get_filter()

        get_option_by_name = menu.get_option_by_name
        get_value = lambda name: get_option_by_name(name).get_value()
        self.gramps_ids = get_value('inc_id')
        self.recursive = get_value('recursive')
        self.missing_info = get_value('missinginfo')
        self.generations = get_value('generations')
        self.inc_fam_notes = get_value('incFamNotes')
        self.inc_par_events = get_value('incParEvents')
        self.inc_par_addr = get_value('incParAddr')
        self.inc_par_notes = get_value('incParNotes')
        self.inc_par_names = get_value('incParNames')
        self.inc_par_mar = get_value('incParMar')
        self.inc_rel_dates = get_value('incRelDates')
        self.inc_chi_mar = get_value('incChiMar')
        self.include_attrs = get_value('incattrs')

        stdoptions.run_name_format_option(self, menu)

        self.place_format = menu.get_option_by_name("place_format").get_value()

    def dump_parent_event(self, name, event):
        place = ""
        date = ""
        descr = ""
        if event:
            date = self._get_date(event.get_date_object())
            place = _pd.display_event(self.db, event, self.place_format)
            if place is None:
                place = ''
            descr = event.get_description()

            if self.include_attrs:
                for attr in event.get_attribute_list():
                    if descr:
                        # translators: needed for Arabic, ignore otherwise
                        descr += self._("; ")
                    attr_type = self._get_type(attr.get_type())
                    # translators: needed for French, ignore otherwise
                    descr += self._("%(str1)s: %(str2)s"
                                   ) % {'str1' : self._(attr_type),
                                        'str2' : attr.get_value()}

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()

        if descr:
            self.doc.start_cell("FGR-TextContentsEnd", 2)
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(descr)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if date or place:
                self.doc.start_row()
                self.doc.start_cell("FGR-TextContents")
                self.doc.start_paragraph('FGR-Normal')
                self.doc.end_paragraph()
                self.doc.end_cell()

        if (date or place) or not descr:
            self.doc.start_cell("FGR-TextContents")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(date)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell("FGR-TextContentsEnd")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(place)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

    def dump_parent_parents(self, person):
        family_handle = person.get_main_parents_family_handle()
        father_name = ""
        mother_name = ""
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.db.get_person_from_handle(father_handle)
                father_name = self._name_display.display(father)
                if self.gramps_ids:
                    gid = father.get_gramps_id()
                    if gid:
                        father_name += " (%s)" % gid
                if self.inc_rel_dates:
                    birth_ref = father.get_birth_ref()
                    birth = "  "
                    if birth_ref:
                        event = self.db.get_event_from_handle(birth_ref.ref)
                        birth = self._get_date(event.get_date_object())
                    death_ref = father.get_death_ref()
                    death = "  "
                    if death_ref:
                        event = self.db.get_event_from_handle(death_ref.ref)
                        death = self._get_date(event.get_date_object())
                    if birth_ref or death_ref:
                        father_name += " (%s - %s)" % (birth, death)
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.db.get_person_from_handle(mother_handle)
                mother_name = self._name_display.display(mother)
                if self.gramps_ids:
                    gid = mother.get_gramps_id()
                    if gid:
                        mother_name += " (%s)" % gid
                if self.inc_rel_dates:
                    birth_ref = mother.get_birth_ref()
                    birth = "  "
                    if birth_ref:
                        event = self.db.get_event_from_handle(birth_ref.ref)
                        birth = self._get_date(event.get_date_object())
                    death_ref = mother.get_death_ref()
                    death = "  "
                    if death_ref:
                        event = self.db.get_event_from_handle(death_ref.ref)
                        death = self._get_date(event.get_date_object())
                    if birth_ref or death_ref:
                        mother_name += " (%s - %s)" % (birth, death)

        if father_name != "":
            self.doc.start_row()
            self.doc.start_cell("FGR-TextContents")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(self._("Father"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell("FGR-TextContentsEnd", 2)
            self.doc.start_paragraph('FGR-Normal')
            mark = utils.get_person_mark(self.db, father)
            self.doc.write_text(father_name, mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
        elif self.missing_info:
            self.dump_parent_line(self._("Father"), "")

        if mother_name != "":
            self.doc.start_row()
            self.doc.start_cell("FGR-TextContents")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(self._("Mother"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell("FGR-TextContentsEnd", 2)
            self.doc.start_paragraph('FGR-Normal')
            mark = utils.get_person_mark(self.db, mother)
            self.doc.write_text(mother_name, mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
        elif self.missing_info:
            self.dump_parent_line(self._("Mother"), "")

    def dump_parent_line(self, name, text):
        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd", 2)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def dump_parent_noteline(self, name, note):
        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd", 2)
        self.doc.write_styled_note(
            note.get_styledtext(), note.get_format(), 'FGR-Note',
            contains_html=(note.get_type() == NoteType.HTML_CODE))
        self.doc.end_cell()
        self.doc.end_row()

    def dump_parent(self, title, person_handle):

        if not person_handle and not self.missing_info:
            return
        elif not person_handle:
            person = Person()
        else:
            person = self.db.get_person_from_handle(person_handle)
        name = self._name_display.display(person)

        self.doc.start_table(title, 'FGR-ParentTable')
        self.doc.start_row()
        self.doc.start_cell('FGR-ParentHead', 3)
        self.doc.start_paragraph('FGR-ParentName')
        mark = utils.get_person_mark(self.db, person)
        # translators: needed for French, ignore otherwise
        self.doc.write_text(self._("%(str1)s: %(str2)s"
                                  ) % {'str1' : title,
                                       'str2' : name},
                            mark)
        if self.gramps_ids:
            gid = person.get_gramps_id()
            if gid:
                self.doc.write_text(" (%s)" % gid)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        birth_ref = person.get_birth_ref()
        birth = None
        ev_name = self._("Birth")
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
        if birth or self.missing_info:
            self.dump_parent_event(ev_name, birth)

        death_ref = person.get_death_ref()
        death = None
        ev_name = self._("Death")
        if death_ref:
            death = self.db.get_event_from_handle(death_ref.ref)
        if death or self.missing_info:
            self.dump_parent_event(ev_name, death)

        self.dump_parent_parents(person)

        if self.inc_par_events:
            for event_ref in person.get_primary_event_ref_list():
                if event_ref != birth_ref and event_ref != death_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
                    event_type = self._get_type(event.get_type())
                    self.dump_parent_event(self._(event_type), event)

        if self.inc_par_addr:
            addrlist = person.get_address_list()[:]
            for addr in addrlist:
                location = utils.get_address_str(addr)
                date = self._get_date(addr.get_date_object())

                self.doc.start_row()
                self.doc.start_cell("FGR-TextContents")
                self.doc.start_paragraph('FGR-Normal')
                self.doc.write_text(self._("Address"))
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.start_cell("FGR-TextContents")
                self.doc.start_paragraph('FGR-Normal')
                self.doc.write_text(date)
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.start_cell("FGR-TextContentsEnd")
                self.doc.start_paragraph('FGR-Normal')
                self.doc.write_text(location)
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()

        if self.inc_par_notes:
            for notehandle in person.get_note_list():
                note = self.db.get_note_from_handle(notehandle)
                self.dump_parent_noteline(self._("Note"), note)

        if self.include_attrs:
            for attr in person.get_attribute_list():
                attr_type = self._get_type(attr.get_type())
                self.dump_parent_line(self._(attr_type), attr.get_value())

        if self.inc_par_names:
            for alt_name in person.get_alternate_names():
                name_type = self._get_type(alt_name.get_type())
                name = self._name_display.display_name(alt_name)
                self.dump_parent_line(self._(name_type), name)

        self.doc.end_table()

    def dump_marriage(self, family):

        if not family:
            return

        mrg = None
        family_list = family.get_event_ref_list()
        for event_ref in family_list:
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
                if (event.get_type() == EventType.MARRIAGE and
                        (event_ref.get_role() == EventRoleType.FAMILY or
                         event_ref.get_role() == EventRoleType.PRIMARY)):
                    mrg = event
                    break

        if len(family_list) > 0 or self.missing_info or self.include_attrs:
            self.doc.start_table("MarriageInfo", 'FGR-ParentTable')
            self.doc.start_row()
            self.doc.start_cell('FGR-ParentHead', 3)
            self.doc.start_paragraph('FGR-ParentName')
            header = self._("Marriage")
            if self.gramps_ids:
                header += " (%s)" % family.get_gramps_id()
            # translators: needed for French, ignore otherwise
            self.doc.write_text(self._("%s:") % header)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            self.dump_parent_event(self._("Marriage"), mrg)

            for event_ref in family_list:
                if event_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
                    if event.get_type() != EventType.MARRIAGE:
                        event_type = self._get_type(event.get_type())
                        self.dump_parent_event(self._(event_type), event)

            if self.include_attrs:
                for attr in family.get_attribute_list():
                    attr_type = self._get_type(attr.get_type())
                    self.dump_parent_line(self._(attr_type), attr.get_value())

            if self.inc_fam_notes:
                for notehandle in family.get_note_list():
                    note = self.database.get_note_from_handle(notehandle)
                    self.dump_parent_noteline(self._("Note"), note)

            self.doc.end_table()

    def dump_child_event(self, text, name, event):
        date = ""
        place = ""
        if event:
            date = self._get_date(event.get_date_object())
            place_handle = event.get_place_handle()
            if place_handle:
                place = _pd.display_event(self.db, event, self.place_format)
                if place is None:
                    place = ''

        self.doc.start_row()
        self.doc.start_cell(text)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContents')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContents')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(date)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContentsEnd')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(place)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def dump_child(self, index, person_handle):

        person = self.db.get_person_from_handle(person_handle)
        families = len(person.get_family_handle_list())
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
        else:
            birth = None
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.db.get_event_from_handle(death_ref.ref)
        else:
            death = None

        spouse_count = 0
        if self.inc_chi_mar:
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                spouse_id = None
                if person_handle == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()
                if spouse_id:
                    spouse_count += 1

        self.doc.start_row()
        if (spouse_count != 0
                or self.missing_info
                or death is not None
                or birth is not None):
            self.doc.start_cell('FGR-TextChild1')
        else:
            self.doc.start_cell('FGR-TextChild2')
        self.doc.start_paragraph('FGR-ChildText')
        index_str = ("%d" % index)
        if person.get_gender() == Person.MALE:
            self.doc.write_text(index_str + self._("M", "acronym for male"))
        elif person.get_gender() == Person.FEMALE:
            self.doc.write_text(index_str + self._("F", "acronym for female"))
        else:
            self.doc.write_text(self._("%dU", "acronym for unknown") % index)
        self.doc.end_paragraph()
        self.doc.end_cell()

        name = self._name_display.display(person)
        mark = utils.get_person_mark(self.db, person)
        self.doc.start_cell('FGR-ChildName', 3)
        self.doc.start_paragraph('FGR-ChildText')
        self.doc.write_text(name, mark)
        if self.gramps_ids:
            self.doc.write_text(" (%s)" % person.get_gramps_id())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        if self.missing_info or birth is not None:
            if spouse_count != 0 or self.missing_info or death is not None:
                self.dump_child_event('FGR-TextChild1', self._('Birth'), birth)
            else:
                self.dump_child_event('FGR-TextChild2', self._('Birth'), birth)

        if self.missing_info or death is not None:
            if spouse_count == 0 or not self.inc_chi_mar:
                self.dump_child_event('FGR-TextChild2', self._('Death'), death)
            else:
                self.dump_child_event('FGR-TextChild1', self._('Death'), death)

        if self.inc_chi_mar:
            index = 0
            for family_handle in person.get_family_handle_list():
                mrg = None
                index += 1
                family = self.db.get_family_from_handle(family_handle)

                for event_ref in family.get_event_ref_list():
                    if event_ref:
                        event = self.db.get_event_from_handle(event_ref.ref)
                        if event.type == EventType.MARRIAGE:
                            mrg = event
                            break

                spouse_id = None

                if person_handle == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()

                if spouse_id:
                    self.doc.start_row()
                    if mrg or index != families:
                        self.doc.start_cell('FGR-TextChild1')
                    else:
                        self.doc.start_cell('FGR-TextChild2')
                    self.doc.start_paragraph('FGR-Normal')
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.start_cell('FGR-TextContents')
                    self.doc.start_paragraph('FGR-Normal')
                    self.doc.write_text(self._("Spouse"))
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.start_cell('FGR-TextContentsEnd', 2)
                    self.doc.start_paragraph('FGR-Normal')

                    spouse = self.db.get_person_from_handle(spouse_id)
                    spouse_name = self._name_display.display(spouse)
                    if self.gramps_ids:
                        gid = spouse.get_gramps_id()
                        if gid:
                            spouse_name += " (%s)" % gid
                    if self.inc_rel_dates:
                        birth = "  "
                        birth_ref = spouse.get_birth_ref()
                        if birth_ref:
                            event = self.db.get_event_from_handle(birth_ref.ref)
                            birth = self._get_date(event.get_date_object())
                        death = "  "
                        death_ref = spouse.get_death_ref()
                        if death_ref:
                            event = self.db.get_event_from_handle(death_ref.ref)
                            death = self._get_date(event.get_date_object())
                        if birth_ref or death_ref:
                            spouse_name += " (%s - %s)" % (birth, death)
                    if self.gramps_ids:
                        fid = family.get_gramps_id()
                        if fid:
                            spouse_name += " (%s)" % fid
                    mark = utils.get_person_mark(self.db, spouse)
                    self.doc.write_text(spouse_name, mark)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.end_row()

                if mrg:
                    ev_name = self._("Marriage")
                    if index == families:
                        self.dump_child_event('FGR-TextChild2', ev_name, mrg)
                    else:
                        self.dump_child_event('FGR-TextChild1', ev_name, mrg)

    def dump_family(self, family_handle, generation):
        family = self.db.get_family_from_handle(family_handle)
        family_toc_name = family_name(family, self.db)

        self.doc.start_paragraph('FGR-Title')
        if self.recursive and self.generations:
            title = self._("Family Group Report - Generation %d") % generation
        else:
            title = self._("Family Group Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        mark = IndexMark(family_toc_name, INDEX_TYPE_TOC, 2)
        self.doc.write_text('', mark)
        self.doc.end_paragraph()

        self.dump_parent(self._("Husband"), family.get_father_handle())
        self.doc.start_paragraph("FGR-blank")
        self.doc.end_paragraph()

        if self.inc_par_mar:
            self.dump_marriage(family)
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()

        self.dump_parent(self._("Wife"), family.get_mother_handle())

        length = len(family.get_child_ref_list())
        if length > 0:
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()
            self.doc.start_table('FGR-Children', 'FGR-ChildTable')
            self.doc.start_row()
            self.doc.start_cell('FGR-ParentHead', 4)
            self.doc.start_paragraph('FGR-ParentName')
            self.doc.write_text(self._("Children"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            index = 1
            for child_ref in family.get_child_ref_list():
                self.dump_child(index, child_ref.ref)
                index += 1
            self.doc.end_table()

        if self.recursive:
            for child_ref in family.get_child_ref_list():
                child = self.db.get_person_from_handle(child_ref.ref)
                for child_family_handle in child.get_family_handle_list():
                    if child_family_handle != family_handle:
                        self.doc.page_break()
                        self.dump_family(child_family_handle, (generation+1))

    def write_report(self):
        flist = self.db.get_family_handles(sort_handles=True,
                                           locale=self._locale)
        if not self.filter:
            fam_list = flist
        else:
            fam_list = self.filter.apply(self.db, flist, user=self._user)
        if fam_list:
            with self._user.progress(_('Family Group Report'),
                                     _('Writing families'),
                                     len(fam_list)) as step:
                for family_handle in fam_list:
                    self.dump_family(family_handle, 1)
                    self.doc.page_break()
                    step()
        else:
            raise ReportError(_('Empty report'),
                              _('You did not specify anybody'))

#------------------------------------------------------------------------
#
# FamilyGroupOptions
#
#------------------------------------------------------------------------
class FamilyGroupOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__fid = None
        self.__filter = None
        self.__recursive = None
        self.__generations = None
        self._nf = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        return self.__filter.get_filter().get_name()

    def add_menu_options(self, menu):

        ##########################
        category_name = _("Report Options")
        add_option = partial(menu.add_option, category_name)
        ##########################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Select the filter to be applied to the report."))
        add_option("filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__fid = FamilyOption(_("Center Family"))
        self.__fid.set_help(_("The center family for the filter"))
        add_option("family_id", self.__fid)
        self.__fid.connect('value-changed', self.__update_filters)

        self.__recursive = BooleanOption(_('Recursive (down)'), False)
        self.__recursive.set_help(_("Create reports for all descendants "
                                    "of this family."))
        add_option("recursive", self.__recursive)
        self.__recursive.connect('value-changed', self.__recursive_changed)

        ##########################
        category_name = _("Report Options (2)")
        add_option = partial(menu.add_option, category_name)
        ##########################

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_place_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ##########################
        add_option = partial(menu.add_option, _("Include"))
        ##########################

        inc_par_mar = BooleanOption(_("Parent Marriage"), True)
        inc_par_mar.set_help(
            _("Whether to include marriage information for parents."))
        add_option("incParMar", inc_par_mar)

        inc_par_events = BooleanOption(_("Parent Events"), False)
        inc_par_events.set_help(_("Whether to include events for parents."))
        add_option("incParEvents", inc_par_events)

        inc_par_addr = BooleanOption(_("Parent Addresses"), False)
        inc_par_addr.set_help(_("Whether to include addresses for parents."))
        add_option("incParAddr", inc_par_addr)

        inc_par_notes = BooleanOption(_("Parent Notes"), False)
        inc_par_notes.set_help(_("Whether to include notes for parents."))
        add_option("incParNotes", inc_par_notes)

        incattrs = BooleanOption(_("Parent Attributes"), False)
        incattrs.set_help(_("Whether to include attributes."))
        add_option("incattrs", incattrs)

        inc_par_names = BooleanOption(_("Alternate Parent Names"), False)
        inc_par_names.set_help(
            _("Whether to include alternate names for parents."))
        add_option("incParNames", inc_par_names)

        ##########################
        category_name = _("Include (2)")
        add_option = partial(menu.add_option, category_name)
        ##########################

        stdoptions.add_gramps_id_option(menu, category_name)

        inc_fam_notes = BooleanOption(_("Family Notes"), False)
        inc_fam_notes.set_help(_("Whether to include notes for families."))
        add_option("incFamNotes", inc_fam_notes)

        inc_rel_dates = BooleanOption(_("Dates of Relatives"), False)
        inc_rel_dates.set_help(_("Whether to include dates for relatives "
                                 "(father, mother, spouse)."))
        add_option("incRelDates", inc_rel_dates)

        inc_chi_mar = BooleanOption(_("Children Marriages"), True)
        inc_chi_mar.set_help(
            _("Whether to include marriage information for children."))
        add_option("incChiMar", inc_chi_mar)

        self.__generations = BooleanOption(_("Generation numbers "
                                             "(recursive only)"), False)
        self.__generations.set_help(_("Whether to include the generation "
                                      "on each report (recursive only)."))
        add_option("generations", self.__generations)

        missinginfo = BooleanOption(_("Print fields for missing "
                                      "information"), True)
        missinginfo.set_help(_("Whether to include fields for missing "
                               "information."))
        add_option("missinginfo", missinginfo)

    def __update_filters(self):
        """
        Update the filter list based on the selected family
        """
        fid = self.__fid.get_value()
        family = self.__db.get_family_from_gramps_id(fid)
        nfv = self._nf.get_value()
        filter_list = utils.get_family_filters(self.__db, family,
                                               include_single=True,
                                               name_format=nfv)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change.
        If the filter is not family-specific, disable the family option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 1: # "Entire Database" (as "include_single=True")
            self.__fid.set_available(False)
        else:
            # The other filters need a center family (assume custom ones too)
            self.__fid.set_available(True)

        # only allow recursion if the center family is the only family
        if self.__recursive and filter_value == 0:
            self.__recursive.set_available(True)
        elif self.__recursive:
            self.__recursive.set_value(False)
            self.__recursive.set_available(False)

    def __recursive_changed(self):
        """
        Handle recursive change.
        """
        recursive_value = self.__recursive.get_value()
        self.__generations.set_available(recursive_value)

    def make_default_style(self, default_style):
        """Make default output style for the Family Group Report."""
        para = ParagraphStyle()
        #Paragraph Styles
        font = FontStyle()
        font.set_size(4)
        para.set_font(font)
        default_style.add_paragraph_style('FGR-blank', para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_header_level(1)
        para.set_description(_("The style used for the title."))
        default_style.add_paragraph_style('FGR-Title', para)

        font = FontStyle()
        font.set_type_face(FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style('FGR-Normal', para)

        para = ParagraphStyle()
        font = FontStyle()
        font.set_type_face(FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para.set_font(font)
        para.set(lmargin=0.0)
        para.set_top_margin(0.0)
        para.set_bottom_margin(0.0)
        para.set_description(_('The basic style used for the note display.'))
        default_style.add_paragraph_style("FGR-Note", para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(
            _('The style used for the text related to the children.'))
        default_style.add_paragraph_style('FGR-ChildText', para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(3)
        para.set_description(_("The style used for the parent's name"))
        default_style.add_paragraph_style('FGR-ParentName', para)

        #Table Styles
        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-ParentHead', cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_right_border(1) # for RTL
        default_style.add_cell_style('FGR-TextContents', cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_right_border(1) # for RTL
        cell.set_padding(0.1)
        default_style.add_cell_style('FGR-TextChild1', cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_right_border(1) # for RTL
        cell.set_padding(0.1)
        default_style.add_cell_style('FGR-TextChild2', cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-TextContentsEnd', cell)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-ChildName', cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0, 20)
        table.set_column_width(1, 40)
        table.set_column_width(2, 40)
        default_style.add_table_style('FGR-ParentTable', table)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 7)
        table.set_column_width(1, 18)
        table.set_column_width(2, 35)
        table.set_column_width(3, 40)
        default_style.add_table_style('FGR-ChildTable', table)
