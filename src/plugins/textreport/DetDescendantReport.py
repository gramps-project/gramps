#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2002 Bruce J. DeGrasse
# Copyright (C) 2000-2007 Donald N. Allingham
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2007      Robert Cawley  <rjc@cawley.id.au>
# Copyright (C) 2008-2009 James Friedmann <jfriedmannj@gmail.com>
# Copyright (C) 2009      Benny Malengier <benny.malengier@gramps-project.org>
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

"""Reports/Text Reports/Detailed Descendant Report"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import gen.lib
from gen.plug import PluginManager
from gen.plug.menu import BooleanOption, NumberOption, PersonOption
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_TEXT
from ReportBase import Bibliography, Endnotes
import BaseDoc
import DateHandler
from BasicUtils import name_displayer as _nd
import Utils

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
EMPTY_ENTRY = "_____________"
HENRY = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class DetDescendantReport(Report):

    def __init__(self, database, options_class):
        """
        Create the DetDescendantReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen           - Maximum number of generations to include.
        pagebgg       - Whether to include page breaks between generations.
        firstName     - Whether to use first names instead of pronouns.
        fulldate      - Whether to use full dates instead of just year.
        listchildren  - Whether to list children.
        inc_mates  - Whether to include information about spouses
        inc_notes  - Whether to include notes.
        inc_attrs  - Whether to include attributes
        blankPlace    - Whether to replace missing Places with ___________.
        blankDate     - Whether to replace missing Dates with ___________.
        calcageflag   - Whether to compute age.
        dubperson     - Whether to omit duplicate ancestors (e.g. when distant cousins mary).
        verbose       - Whether to use complete sentences
        record_num    - Whether to use Record-style numbering instead of Henry-style.
        childref      - Whether to add descendant references in child list.
        addimages     - Whether to include images.
        pid           - The Gramps ID of the center person for the report.
        """
        Report.__init__(self, database, options_class)

        self.map = {}

        menu = options_class.menu
        self.max_generations = menu.get_option_by_name('gen').get_value()
        self.pgbrk         = menu.get_option_by_name('pagebbg').get_value()
        self.fulldate      = menu.get_option_by_name('fulldates').get_value()
        self.listchildren  = menu.get_option_by_name('listc').get_value()
        self.inc_notes     = menu.get_option_by_name('incnotes').get_value()
        self.usecall       = menu.get_option_by_name('usecall').get_value()
        blankplace         = menu.get_option_by_name('repplace').get_value()
        blankdate          = menu.get_option_by_name('repdate').get_value()
        self.calcageflag   = menu.get_option_by_name('computeage').get_value()
        self.dubperson     = menu.get_option_by_name('omitda').get_value()
        self.verbose       = menu.get_option_by_name('verbose').get_value()
        self.record_num    = menu.get_option_by_name('record_num').get_value()
        self.childref      = menu.get_option_by_name('desref').get_value()
        self.addimages     = menu.get_option_by_name('incphotos').get_value()
        self.inc_names     = menu.get_option_by_name('incnames').get_value()
        self.inc_events    = menu.get_option_by_name('incevents').get_value()
        self.inc_addr      = menu.get_option_by_name('incaddresses').get_value()
        self.inc_sources   = menu.get_option_by_name('incsources').get_value()
        self.inc_mates     = menu.get_option_by_name('incmates').get_value()
        self.inc_attrs     = menu.get_option_by_name('incattrs').get_value()
        self.inc_paths     = menu.get_option_by_name('incpaths').get_value()
        pid                = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)

        self.gen_handles = {}
        self.prev_gen_handles = {}
        self.gen_keys = []
        self.dnumber = {}

        if blankdate:
            self.EMPTY_DATE = EMPTY_ENTRY
        else:
            self.EMPTY_DATE = ""

        if blankplace:
            self.EMPTY_PLACE = EMPTY_ENTRY
        else:
            self.EMPTY_PLACE = ""

        self.bibli = Bibliography(Bibliography.MODE_PAGE)

    def apply_henry_filter(self,person_handle, index, pid, cur_gen=1):
        if (not person_handle) or (cur_gen > self.max_generations):
            return
        self.dnumber[person_handle] = pid
        self.map[index] = person_handle

        if len(self.gen_keys) < cur_gen:
            self.gen_keys.append([index])
        else: 
            self.gen_keys[cur_gen-1].append(index)

        person = self.database.get_person_from_handle(person_handle)
        index = 0
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                ix = max(self.map.keys())
                self.apply_henry_filter(child_ref.ref, ix+1,
                                  pid+HENRY[index], cur_gen+1)
                index += 1

    # Filter for Record-style (Modified Register) numbering
    def apply_mod_reg_filter_aux(self, person_handle, index, cur_gen=1):
        if (not person_handle) or (cur_gen > self.max_generations):
            return
        self.map[index] = person_handle
                
        if len(self.gen_keys) < cur_gen:
            self.gen_keys.append([index])
        else: 
            self.gen_keys[cur_gen-1].append(index)

        person = self.database.get_person_from_handle(person_handle)

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                ix = max(self.map.keys())
                self.apply_mod_reg_filter_aux(child_ref.ref, ix+1, cur_gen+1)

    def apply_mod_reg_filter(self,person_handle):
        self.apply_mod_reg_filter_aux(person_handle, 1, 1)
        mod_reg_number = 1
        for generation in xrange(len(self.gen_keys)):
            for key in self.gen_keys[generation]:
                person_handle = self.map[key]
                self.dnumber[person_handle] = mod_reg_number
                mod_reg_number += 1

    def write_report(self):
        """
        This function is called by the report system and writes the report.
        """
        if self.record_num:
            self.apply_mod_reg_filter(self.center_person.get_handle())
        else:
            self.apply_henry_filter(self.center_person.get_handle(), 1, "1")

        name = _nd.display_name(self.center_person.get_primary_name())

        self.doc.start_paragraph("DDR-Title")

        title = _("Descendant Report for %(person_name)s") % {
                    'person_name' : name }
        mark = BaseDoc.IndexMark(title, BaseDoc.INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        keys = self.map.keys()
        keys.sort()
        generation = 0

        for generation in xrange(len(self.gen_keys)):
            if self.pgbrk and generation > 0:
                self.doc.page_break()
            self.doc.start_paragraph("DDR-Generation")
            text = _("Generation %d") % (generation+1)
            mark = BaseDoc.IndexMark(text, BaseDoc.INDEX_TYPE_TOC, 2)
            self.doc.write_text(text, mark)
            self.doc.end_paragraph()
            if self.childref:
                self.prev_gen_handles = self.gen_handles.copy()
                self.gen_handles.clear()

            for key in self.gen_keys[generation]:
                person_handle = self.map[key]
                self.gen_handles[person_handle] = key
                self.write_person(key)

        if self.inc_sources:
            Endnotes.write_endnotes(self.bibli, self.database, self.doc)

    def write_path(self, person):
        path = []
        while True:
            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = self.database.get_family_from_handle(family_handle)
                mother_handle = family.get_mother_handle()
                father_handle = family.get_father_handle()
                if mother_handle and mother_handle in self.dnumber:
                    person = self.database.get_person_from_handle(mother_handle)
                    person_name = _nd.display_name(person.get_primary_name())
                    path.append(person_name)
                elif father_handle and father_handle in self.dnumber:
                    person = self.database.get_person_from_handle(father_handle)
                    person_name = _nd.display_name(person.get_primary_name())
                    path.append(person_name)
                else:
                    break

        index = len(path)

        if index:
            self.doc.write_text("(")

        for name in path:
            if index == 1:
                self.doc.write_text(name + "-" + str(index) + ") ")
            else:
                self.doc.write_text(name + "-" + str(index) + "; ")
            index -= 1

    def write_person(self, key):
        """Output birth, death, parentage, marriage and notes information """

        person_handle = self.map[key]
        person = self.database.get_person_from_handle(person_handle)

        val = self.dnumber[person_handle]
        self.doc.start_paragraph("DDR-First-Entry","%s." % val)

        name = _nd.display_formal(person)
        mark = ReportUtils.get_person_mark(self.database, person)

        self.doc.start_bold()
        self.doc.write_text(name, mark)
        if name[-1:] == '.':
            self.doc.write_text_citation("%s " % self.endnotes(person))
        else:
            self.doc.write_text_citation("%s. " % self.endnotes(person))
        self.doc.end_bold()

        if self.inc_paths:
            self.write_path(person)
        
        if self.dubperson:
            # Check for duplicate record (result of distant cousins marrying)
            keys = self.map.keys()
            keys.sort()
            for dkey in keys:
                if dkey >= key: 
                    break
                if self.map[key] == self.map[dkey]:
                    self.doc.write_text(_("%(name)s is the same person as [%(id_str)s].") % 
                                        { 'name' : '', 'id_str' : str(dkey) })
                    self.doc.end_paragraph()
                    return

        self.doc.end_paragraph()
       
        self.write_person_info(person)

        if self.listchildren or self.inc_events or self.inc_mates:
            for family_handle in person.get_family_handle_list():
                family = self.database.get_family_from_handle(family_handle)
                if self.inc_mates:
                    self.__write_mate(person, family)
                if self.listchildren:
                    self.__write_children(family)
                if self.inc_events:
                    self.__write_family_events(family)

    def write_event(self, event_ref):
        text = ""
        event = self.database.get_event_from_handle(event_ref.ref)
        date = DateHandler.get_date(event)
        ph = event.get_place_handle()
        if ph:
            place = self.database.get_place_from_handle(ph).get_title()
        else:
            place = u''

        self.doc.start_paragraph('DDR-MoreDetails')
        event_name = str( event.get_type() )
        if date and place:
            text +=  _('%(date)s, %(place)s') % { 
                       'date' : date, 'place' : place }
        elif date:
            text += _('%(date)s') % {'date' : date}
        elif place:
            text += _('%(place)s') % { 'place' : place }

        if event.get_description():
            if text:
                text += ". "
            text += event.get_description()
            
        text += self.endnotes(event)
        
        if text:
            text += ". "
            
        text = _('%(event_name)s: %(event_text)s') % {
                 'event_name' : _(event_name),
                 'event_text' : text }
        
        self.doc.write_text_citation(text)
        
        if self.inc_attrs:
            text = ""
            attr_list = event.get_attribute_list()
            attr_list.extend(event_ref.get_attribute_list())
            for attr in attr_list:
                if text:
                    text += "; "
                text += _("%(type)s: %(value)s%(endnotes)s") % {
                    'type'     : attr.get_type(),
                    'value'    : attr.get_value(),
                    'endnotes' : self.endnotes(attr) }
            text = " " + text
            self.doc.write_text_citation(text)

        self.doc.end_paragraph()

        if self.inc_notes:
            # if the event or event reference has a note attached to it,
            # get the text and format it correctly
            notelist = event.get_note_list()
            notelist.extend(event_ref.get_note_list())
            for notehandle in notelist:
                note = self.database.get_note_from_handle(notehandle)
                self.doc.write_styled_note(note.get_styledtext(), 
                                           note.get_format(),"DDR-MoreDetails")

    def write_parents(self, person, firstName):
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            father_handle = family.get_father_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mother_name = _nd.display_name(mother.get_primary_name())
                mother_mark = ReportUtils.get_person_mark(self.database, mother)
            else:
                mother_name = ""
                mother_mark = ""
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                father_name = _nd.display_name(father.get_primary_name())
                father_mark = ReportUtils.get_person_mark(self.database, father)
            else:
                father_name = ""
                father_mark = ""
            alive = Utils.probably_alive(person, self.database)
            text = ReportUtils.child_str(person, father_name, mother_name,
                                         not alive,
                                         firstName,self.verbose)
            if text:
                self.doc.write_text(text)
                if father_mark:
                    self.doc.write_text("", father_mark)
                if mother_mark:
                    self.doc.write_text("", mother_mark)

    def write_marriage(self, person):
        """ 
        Output marriage sentence.
        """
        is_first = True
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(person, family)
            spouse = self.database.get_person_from_handle(spouse_handle)
            text = ""
            spouse_mark = ReportUtils.get_person_mark(self.database, spouse)
            
            text = ReportUtils.married_str(self.database, person, family,
                                            self.verbose,
                                            self.endnotes,
                                            self.EMPTY_DATE,self.EMPTY_PLACE,
                                            is_first)
            
            if text:
                self.doc.write_text_citation(text, spouse_mark)
                is_first = False
                
    def __write_mate(self, person, family):
        """
        Write information about the person's spouse/mate.
        """
        if person.get_gender() == gen.lib.Person.MALE:
            mate_handle = family.get_mother_handle()
        else:
            mate_handle = family.get_father_handle()
            
        if mate_handle:
            mate = self.database.get_person_from_handle(mate_handle)

            self.doc.start_paragraph("DDR-MoreHeader")
            name = _nd.display_formal(mate)
            mark = ReportUtils.get_person_mark(self.database, mate)
            if family.get_relationship() == gen.lib.FamilyRelType.MARRIED:
                self.doc.write_text(_("Spouse: %s") % name, mark)
            else:
                self.doc.write_text(_("Relationship with: %s") % name, mark)
            if name[-1:] != '.':
                self.doc.write_text(".")
            self.doc.write_text_citation(self.endnotes(mate))
            self.doc.end_paragraph()

            self.write_person_info(mate)

    def __write_children(self, family):
        """ 
        List the children for the given family.
        """
        if not family.get_child_ref_list():
            return

        mother_handle = family.get_mother_handle()
        if mother_handle:
            mother = self.database.get_person_from_handle(mother_handle)
            mother_name = _nd.display(mother)
        else:
            mother_name = _("unknown")

        father_handle = family.get_father_handle()
        if father_handle:
            father = self.database.get_person_from_handle(father_handle)
            father_name = _nd.display(father)
        else:
            father_name = _("unknown")

        self.doc.start_paragraph("DDR-ChildTitle")
        self.doc.write_text(
                        _("Children of %(mother_name)s and %(father_name)s") % 
                            {'father_name': father_name,
                             'mother_name': mother_name
                             } )
        self.doc.end_paragraph()

        cnt = 1
        for child_ref in family.get_child_ref_list():
            child_handle = child_ref.ref
            child = self.database.get_person_from_handle(child_handle)
            child_name = _nd.display(child)
            child_mark = ReportUtils.get_person_mark(self.database, child)

            if self.childref and self.prev_gen_handles.get(child_handle):
                value = str(self.prev_gen_handles.get(child_handle))
                child_name += " [%s]" % value

            self.doc.start_paragraph("DDR-ChildList",
                                     ReportUtils.roman(cnt).lower() + ".")
            cnt += 1

            if child_handle in self.dnumber:
                self.doc.write_text("%s [%s]. " % (child_name,
                                                   self.dnumber[child_handle]),
                                    child_mark )
            else:
                self.doc.write_text("%s. " % child_name, child_mark)
                
            self.doc.write_text(ReportUtils.born_str( self.database, child, 0, 
                          self.verbose, self.EMPTY_DATE, self.EMPTY_PLACE))
            self.doc.write_text(ReportUtils.died_str( self.database, child, 0, 
                          self.verbose, self.EMPTY_DATE, self.EMPTY_PLACE))
            self.doc.end_paragraph()

    def __write_family_events(self, family):
        """ 
        List the events for the given family.
        """
        if not family.get_event_ref_list():
            return

        mother_handle = family.get_mother_handle()
        if mother_handle:
            mother = self.database.get_person_from_handle(mother_handle)
            mother_name = _nd.display(mother)
        else:
            mother_name = _("unknown")

        father_handle = family.get_father_handle()
        if father_handle:
            father = self.database.get_person_from_handle(father_handle)
            father_name = _nd.display(father)
        else:
            father_name = _("unknown")

        first = 1
        for event_ref in family.get_event_ref_list():
            if first:
                self.doc.start_paragraph('DDR-MoreHeader')
                self.doc.write_text(
                    _('More about %(mother_name)s and %(father_name)s:') % { 
                    'mother_name' : mother_name,
                    'father_name' : father_name })
                self.doc.end_paragraph()
                first = 0
            self.write_event(event_ref)

    def write_person_info(self, person):
        name = _nd.display_formal(person)
        
        plist = person.get_media_list()
        if self.addimages and len(plist) > 0:
            photo = plist[0]
            ReportUtils.insert_image(self.database, self.doc, photo)
        
        self.doc.start_paragraph("DDR-Entry")
        # Check birth record
        first = ReportUtils.common_name(person, self.usecall)
        
        if not self.verbose:
            self.write_parents(person, first)

        text = ReportUtils.born_str(self.database, person, first, self.verbose,
                                    self.EMPTY_DATE, self.EMPTY_PLACE)
        if text:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.database.get_event_from_handle(birth_ref.ref)
                text = text.rstrip(". ")
                text = text + self.endnotes(birth) + ". "
            self.doc.write_text_citation(text)
            first = 0

        text = ReportUtils.baptised_str(self.database, person, first, 
                                        self.verbose, self.endnotes, 
                                        self.EMPTY_DATE, self.EMPTY_PLACE)
        if text:
            self.doc.write_text_citation(text)
            
        text = ReportUtils.christened_str(self.database, person, first, 
                                          self.verbose, self.endnotes, 
                                          self.EMPTY_DATE, self.EMPTY_PLACE)
        if text:
            self.doc.write_text_citation(text)
    
        span = self.calc_age(person)
        text = ReportUtils.died_str(self.database, person, first, self.verbose,
                                    self.EMPTY_DATE, self.EMPTY_PLACE, span)
        if text:
            death_ref = person.get_death_ref()
            if death_ref:
                death = self.database.get_event_from_handle(death_ref.ref)
                text = text.rstrip(". ")
                text = text + self.endnotes(death) + ". "
            self.doc.write_text_citation(text)
            first = 0

        text = ReportUtils.buried_str(self.database, person, first, 
                                      self.verbose, self.endnotes, 
                                      self.EMPTY_DATE, self.EMPTY_PLACE)
        if text:
            self.doc.write_text_citation(text)

        first = ReportUtils.common_name(person, self.usecall)

        if self.verbose:
            self.write_parents(person, first)
        self.write_marriage(person)
        self.doc.end_paragraph()

        notelist = person.get_note_list()
        if len(notelist) > 0 and self.inc_notes:
            self.doc.start_paragraph("DDR-NoteHeader")
            self.doc.write_text(_("Notes for %s") % name)
            self.doc.end_paragraph()
            for notehandle in notelist:
                note = self.database.get_note_from_handle(notehandle)
                self.doc.write_styled_note(note.get_styledtext(), 
                                           note.get_format(),"DDR-Entry")

        first = True
        if self.inc_names:
            for alt_name in person.get_alternate_names():
                if first:
                    self.doc.start_paragraph('DDR-MoreHeader')
                    self.doc.write_text(_('More about %(person_name)s:') % { 
                        'person_name' : name })
                    self.doc.end_paragraph()
                    first = False
                self.doc.start_paragraph('DDR-MoreDetails')
                atype = str( alt_name.get_type() )
                aname = alt_name.get_regular_name()
                self.doc.write_text_citation(_('%(name_kind)s: %(name)s%(endnotes)s') % {
                    'name_kind' : atype,
                    'name' : aname,
                    'endnotes' : self.endnotes(alt_name),
                    })
                self.doc.end_paragraph()

        if self.inc_events:
            for event_ref in person.get_primary_event_ref_list():
                if first:
                    self.doc.start_paragraph('DDR-MoreHeader')
                    self.doc.write_text(_('More about %(person_name)s:') % { 
                        'person_name' : _nd.display(person) })
                    self.doc.end_paragraph()
                    first = 0

                self.write_event(event_ref)
                
        if self.inc_addr:
            for addr in person.get_address_list():
                if first:
                    self.doc.start_paragraph('DDR-MoreHeader')
                    self.doc.write_text(_('More about %(person_name)s:') % { 
                        'person_name' : name })
                    self.doc.end_paragraph()
                    first = False
                self.doc.start_paragraph('DDR-MoreDetails')
                
                text = ReportUtils.get_address_str(addr)
                date = DateHandler.get_date(addr)
                self.doc.write_text(_('Address: '))
                if date:
                    self.doc.write_text( '%s, ' % date )
                self.doc.write_text( text )
                self.doc.write_text_citation( self.endnotes(addr) )
                self.doc.end_paragraph()
                
        if self.inc_attrs:
            attrs = person.get_attribute_list()
            if first and attrs:
                self.doc.start_paragraph('DDR-MoreHeader')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                    'person_name' : name })
                self.doc.end_paragraph()
                first = False

            for attr in attrs:
                self.doc.start_paragraph('DDR-MoreDetails')
                text = _("%(type)s: %(value)s%(endnotes)s") % {
                    'type'     : attr.get_type(),
                    'value'    : attr.get_value(),
                    'endnotes' : self.endnotes(attr) }
                self.doc.write_text_citation( text )
                self.doc.end_paragraph()

    def calc_age(self,ind):
        """
        Calulate age. 
        
        Returns a tuple (age,units) where units is an integer representing
        time units:
            no age info:    0
            years:          1
            months:         2
            days:           3
        """
        if self.calcageflag:
            return ReportUtils.old_calc_age(self.database, ind)
        else:
            return None

    def endnotes(self, obj):
        if not obj or not self.inc_sources:
            return ""
        
        txt = Endnotes.cite_source(self.bibli, obj)
        if txt:
            txt = '<super>' + txt + '</super>'
        return txt

#------------------------------------------------------------------------
#
# DetDescendantOptions
#
#------------------------------------------------------------------------
class DetDescendantOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the detailed descendant report.
        """
        category_name = _("Report Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", pid)
        
        generations = NumberOption(_("Generations"), 10, 1, 100)
        generations.set_help(_("The number of generations to include in the " \
                               "report"))
        menu.add_option(category_name, "gen", generations)
        
        pagebbg = BooleanOption(_("Page break between generations"), False)
        pagebbg.set_help(
                     _("Whether to start a new page after each generation."))
        menu.add_option(category_name, "pagebbg", pagebbg)

        record_num = BooleanOption(_("Use Record-style (Modified Register) " \
                                     "numbering"),
                                   False)
        record_num.set_help(_("Whether to use Record-style numbering instead" \
                              " of Henry-style."))
        menu.add_option(category_name, "record_num", record_num)
        
        category_name = _("Content")

        usecall = BooleanOption(_("Use callname for common name"), False)
        usecall.set_help(_("Whether to use the call name as the first name."))
        menu.add_option(category_name, "usecall", usecall)
        
        fulldates = BooleanOption(_("Use full dates instead of only the year"),
                                  True)
        fulldates.set_help(_("Whether to use full dates instead of just year."))
        menu.add_option(category_name, "fulldates", fulldates)
        
        listc = BooleanOption(_("List children"), True)
        listc.set_help(_("Whether to list children."))
        menu.add_option(category_name, "listc", listc)
        
        computeage = BooleanOption(_("Compute age"), True)
        computeage.set_help(_("Whether to compute age."))
        menu.add_option(category_name, "computeage", computeage)
        
        omitda = BooleanOption(_("Omit duplicate ancestors"), True)
        omitda.set_help(_("Whether to omit duplicate ancestors."))
        menu.add_option(category_name, "omitda", omitda)
        
        verbose = BooleanOption(_("Use Complete Sentences"), True)
        verbose.set_help(
                 _("Whether to use complete sentences or succinct language."))
        menu.add_option(category_name, "verbose", verbose)

        desref = BooleanOption(_("Add descendant reference in child list"),
                               True)
        desref.set_help(
                    _("Whether to add descendant references in child list."))
        menu.add_option(category_name, "desref", desref)

        category_name = _("Include")
        
        incnotes = BooleanOption(_("Include notes"), True)
        incnotes.set_help(_("Whether to include notes."))
        menu.add_option(category_name, "incnotes", incnotes)

        incattrs = BooleanOption(_("Include attributes"), False)
        incattrs.set_help(_("Whether to include attributes."))
        menu.add_option(category_name, "incattrs", incattrs)
        
        incphotos = BooleanOption(_("Include Photo/Images from Gallery"), False)
        incphotos.set_help(_("Whether to include images."))
        menu.add_option(category_name, "incphotos", incphotos)

        incnames = BooleanOption(_("Include alternative names"), False)
        incnames.set_help(_("Whether to include other names."))
        menu.add_option(category_name, "incnames", incnames)

        incevents = BooleanOption(_("Include events"), False)
        incevents.set_help(_("Whether to include events."))
        menu.add_option(category_name, "incevents", incevents)

        incaddresses = BooleanOption(_("Include addresses"), False)
        incaddresses.set_help(_("Whether to include addresses."))
        menu.add_option(category_name, "incaddresses", incaddresses)

        incsources = BooleanOption(_("Include sources"), False)
        incsources.set_help(_("Whether to include source references."))
        menu.add_option(category_name, "incsources", incsources)

        incmates = BooleanOption(_("Include spouses"), False)
        incmates.set_help(_("Whether to include detailed spouse information."))
        menu.add_option(category_name, "incmates", incmates)

        incpaths = BooleanOption(_("Include path to start-person"), False)
        incpaths.set_help(_("Whether to include the path of descendancy " \
                            "from the start-person to each descendant"))
        menu.add_option(category_name, "incpaths", incpaths)

        category_name = _("Missing information")        

        repplace = BooleanOption(_("Replace missing places with ______"), False)
        repplace.set_help(_("Whether to replace missing Places with blanks."))
        menu.add_option(category_name, "repplace", repplace)

        repdate = BooleanOption(_("Replace missing dates with ______"), False)
        repdate.set_help(_("Whether to replace missing Dates with blanks."))
        menu.add_option(category_name, "repdate", repdate)

    def make_default_style(self, default_style):
        """Make the default output style for the Detailed Ancestral Report"""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=16, bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_paragraph_style("DDR-Title", para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=14, italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_paragraph_style("DDR-Generation", para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=10, italic=0, bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_left_margin(1.5)   # in centimeters
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the children list title.'))
        default_style.add_paragraph_style("DDR-ChildTitle", para)

        font = BaseDoc.FontStyle()
        font.set(size=10)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-0.75, lmargin=2.25)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)
        para.set_description(_('The style used for the children list.'))
        default_style.add_paragraph_style("DDR-ChildList", para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=10, italic=0, bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        default_style.add_paragraph_style("DDR-NoteHeader", para)

        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("DDR-Entry", para)

        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)        
        para.set_description(_('The style used for the first personal entry.'))
        default_style.add_paragraph_style("DDR-First-Entry", para)

        font = BaseDoc.FontStyle()
        font.set(size=10, face=BaseDoc.FONT_SANS_SERIF, bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the More About header.'))
        default_style.add_paragraph_style("DDR-MoreHeader", para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF, size=10)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for additional detail data.'))
        default_style.add_paragraph_style("DDR-MoreDetails", para)

        Endnotes.add_endnote_styles(default_style)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'det_descendant_report',
    category = CATEGORY_TEXT,
    report_class = DetDescendantReport,
    options_class = DetDescendantOptions,
    modes = PluginManager.REPORT_MODE_GUI | \
            PluginManager.REPORT_MODE_BKI | \
            PluginManager.REPORT_MODE_CLI,
    translated_name = _("Detailed Descendant Report"),
    status = _("Stable"),
    description = _("Produces a detailed descendant report"),
    author_name = "Bruce DeGrasse",
    author_email = "bdegrasse1@attbi.com"
    )
