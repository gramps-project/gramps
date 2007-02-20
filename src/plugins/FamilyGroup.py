#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""Generate files/Family Group Report"""

#------------------------------------------------------------------------
#
# Gnome/GTK modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS 
#
#------------------------------------------------------------------------
import RelLib
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import DateHandler
import Utils
from TransUtils import sgettext as _
from BasicUtils.NameDisplay import displayer as _nd

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the DetAncestorReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        family_handle - Handle of the family to write report on.
        """
        Report.__init__(self,database,person,options_class)

        self.family_handle = None

        family_id = options_class.handler.options_dict['family_id']
        if family_id:
            family_list = person.get_family_handle_list()
            for family_handle in family_list:
                family = database.get_family_from_handle(family_handle)
                this_family_id = family.get_gramps_id()
                if this_family_id == family_id:
                    self.family_handle = family_handle
                    break

        self.recursive     = options_class.handler.options_dict['recursive']
        self.missingInfo   = options_class.handler.options_dict['missinginfo']
        self.generations   = options_class.handler.options_dict['generations']
        self.incParEvents  = options_class.handler.options_dict['incParEvents']
        self.incParAddr    = options_class.handler.options_dict['incParAddr']
        self.incParNotes   = options_class.handler.options_dict['incParNotes']
        self.incParNames   = options_class.handler.options_dict['incParNames']
        self.incParMar     = options_class.handler.options_dict['incParMar']
        self.incRelDates   = options_class.handler.options_dict['incRelDates']
        self.incChiMar     = options_class.handler.options_dict['incChiMar']

    def define_table_styles(self):
        """
        Define the table  styles used by the report. 
        """
        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-ParentHead',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-TextContents',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('FGR-TextChild1',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('FGR-TextChild2',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-TextContentsEnd',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-ChildName',cell)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,20)
        table.set_column_width(1,40)
        table.set_column_width(2,40)
        self.doc.add_table_style('FGR-ParentTable',table)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,7)
        table.set_column_width(1,18)
        table.set_column_width(2,35)
        table.set_column_width(3,40)
        self.doc.add_table_style('FGR-ChildTable',table)

    def dump_parent_event(self,name,event):
        place = ""
        date = ""
        descr = ""
        if event:
            date = DateHandler.get_date(event)
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database,place_handle)
            descr = event.get_description()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        if descr:
            self.doc.start_cell("FGR-TextContents",2)
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
        
    def dump_parent_parents(self,person):
        family_handle = person.get_main_parents_family_handle()
        father_name = ""
        mother_name = ""
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle() 
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                father_name = _nd.display(father)
                if self.incRelDates:
                    birth_ref = father.get_birth_ref()
                    birth = "  "
                    if birth_ref:
                        event = self.database.get_event_from_handle(birth_ref.ref)
                        birth = DateHandler.get_date( event )
                    death_ref = father.get_death_ref()
                    death = "  "
                    if death_ref:
                        event = self.database.get_event_from_handle(death_ref.ref)
                        death = DateHandler.get_date( event )
                    if birth_ref or death_ref:
                        father_name = "%s (%s - %s)" % (father_name,birth,death)
            mother_handle = family.get_mother_handle() 
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mother_name = _nd.display(mother)
                if self.incRelDates:
                    birth_ref = mother.get_birth_ref()
                    birth = "  "
                    if birth_ref:
                        event = self.database.get_event_from_handle(birth_ref.ref)
                        birth = DateHandler.get_date( event )
                    death_ref = mother.get_death_ref()
                    death = "  "
                    if death_ref:
                        event = self.database.get_event_from_handle(death_ref.ref)
                        death = DateHandler.get_date( event )
                    if birth_ref or death_ref:
                        mother_name = "%s (%s - %s)" % (mother_name,birth,death)
        
        if father_name != "":
            self.doc.start_row()
            self.doc.start_cell("FGR-TextContents")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(_("Father"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell("FGR-TextContentsEnd",2)
            self.doc.start_paragraph('FGR-Normal')
            mark = ReportUtils.get_person_mark(self.database,father)
            self.doc.write_text(father_name,mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
        elif self.missingInfo:
            self.dump_parent_line(_("Father"),"")

        if mother_name != "":
            self.doc.start_row()
            self.doc.start_cell("FGR-TextContents")
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(_("Mother"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell("FGR-TextContentsEnd",2)
            self.doc.start_paragraph('FGR-Normal')
            mark = ReportUtils.get_person_mark(self.database,mother)
            self.doc.write_text(mother_name,mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
        elif self.missingInfo:
            self.dump_parent_line(_("Mother"),"")

    def dump_parent_line(self,name,text):
        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd",2)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
            
    def dump_parent(self,title,person_handle):

        if not person_handle and not self.missingInfo:
            return
        elif not person_handle:
            person = RelLib.Person()
        else:
            person = self.database.get_person_from_handle(person_handle)
        name = _nd.display(person)
        
        self.doc.start_table(title,'FGR-ParentTable')
        self.doc.start_row()
        self.doc.start_cell('FGR-ParentHead',3)
        self.doc.start_paragraph('FGR-ParentName')
        self.doc.write_text(title + ': ')
        mark = ReportUtils.get_person_mark(self.database,person)
        self.doc.write_text(name,mark)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        birth_ref = person.get_birth_ref()
        birth = None
        evtName = str(RelLib.EventType())
        if birth_ref:
            birth = self.database.get_event_from_handle(birth_ref.ref)
        if birth or self.missingInfo:
            self.dump_parent_event(evtName,birth)

        death_ref = person.get_death_ref()
        death = None
        evtName = str(RelLib.EventType(RelLib.EventType.DEATH))
        if death_ref:
            death = self.database.get_event_from_handle(death_ref.ref)
        if death or self.missingInfo:
            self.dump_parent_event(evtName,death)

        self.dump_parent_parents(person)

        if self.incParEvents:
            for event_ref in person.get_primary_event_ref_list():
                if event_ref != birth_ref and event_ref != death_ref:
                    event = self.database.get_event_from_handle(event_ref.ref)
                    evtType = event.get_type()
                    name = str( evtType )
                    self.dump_parent_event(name,event)

        if self.incParAddr:
            addrlist = person.get_address_list()[:]
            for addr in addrlist:
                location = ReportUtils.get_address_str(addr)
                date = DateHandler.get_date( addr )
                
                self.doc.start_row()
                self.doc.start_cell("FGR-TextContents")
                self.doc.start_paragraph('FGR-Normal')
                self.doc.write_text(_("Address"))
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

        if self.incParNotes and (person.get_note() != ""):
            self.dump_parent_line(_("Notes"),person.get_note())

        if self.incParNames:
            for alt_name in person.get_alternate_names():
                name_type = str( alt_name.get_type() )
                name = _nd.display_name(alt_name)
                self.dump_parent_line(name_type,name)

        self.doc.end_table()

    def dump_marriage(self,family):
        if not family:
            return
        m = None
        family_ref_list = family.get_event_ref_list()
        for event_ref in family_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                    m = event
                    break

        if m or self.missingInfo:
            self.doc.start_table("MarriageInfo",'FGR-ParentTable')
            self.doc.start_row()
            self.doc.start_cell('FGR-ParentHead',3)
            self.doc.start_paragraph('FGR-ParentName')
            self.doc.write_text(_("Marriage:"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
        
            evtName = str(RelLib.EventType(RelLib.EventType.MARRIAGE))
            self.dump_parent_event(evtName,m)
            
            for event_ref in family_ref_list:
                if event_ref:
                    event = self.database.get_event_from_handle(event_ref.ref)
                    evtType = event.get_type()
                    if int(evtType) != RelLib.EventType.MARRIAGE:
                        name = Utils.format_event( evtType )
                        self.dump_parent_event(name,event)
            
            self.doc.end_table()

    def dump_marriage(self,family):

        if not family:
            return

        m = None
        family_list = family.get_event_ref_list()
        for event_ref in family_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event.get_type() == RelLib.EventType.MARRIAGE:
                    m = event
                    break

        if len(family_list) > 0 or self.missingInfo:
            self.doc.start_table("MarriageInfo",'FGR-ParentTable')
            self.doc.start_row()
            self.doc.start_cell('FGR-ParentHead',3)
            self.doc.start_paragraph('FGR-ParentName')
            self.doc.write_text(_("Marriage:"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            self.dump_parent_event(_("Marriage"),m)
            
            for event_ref in family_list:
                if event_ref:
                    event = self.database.get_event_from_handle(event_ref.ref)
                    if event.get_type() != RelLib.EventType.MARRIAGE:
                        self.dump_parent_event(str(event.get_type()),event)
            
            self.doc.end_table()

    def dump_child_event(self,text,name,event):
        date = ""
        place = ""
        if event:
            date = DateHandler.get_date(event)
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle).get_title()

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
        
    def dump_child(self,index,person_handle):

        person = self.database.get_person_from_handle(person_handle)
        families = len(person.get_family_handle_list())
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.database.get_event_from_handle(birth_ref.ref)
        else:
            birth = None
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.database.get_event_from_handle(death_ref.ref)
        else:
            death = None
        
        spouse_count = 0; 
        if self.incChiMar:   
            for family_handle in person.get_family_handle_list():
                family = self.database.get_family_from_handle(family_handle)
                spouse_id = None
                if person_handle == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()
                if spouse_id:
                    spouse_count = spouse_count + 1

        self.doc.start_row()
        if spouse_count != 0 or self.missingInfo or death != None or birth != None:
            self.doc.start_cell('FGR-TextChild1')
        else:
            self.doc.start_cell('FGR-TextChild2')
        self.doc.start_paragraph('FGR-ChildText')
        index_str = ("%d" % index)
        if person.get_gender() == RelLib.Person.MALE:
            self.doc.write_text(index_str + _("acronym for male|M"))
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.doc.write_text(index_str + _("acronym for female|F"))
        else:
            self.doc.write_text(_("%dU") % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        name = _nd.display(person)
        mark = ReportUtils.get_person_mark(self.database,person)
        self.doc.start_cell('FGR-ChildName',3)
        self.doc.start_paragraph('FGR-ChildText')
        self.doc.write_text(name,mark)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        if self.missingInfo or birth != None:
            if spouse_count != 0 or self.missingInfo or death != None:
                self.dump_child_event('FGR-TextChild1',_('Birth'),birth)
            else:
                self.dump_child_event('FGR-TextChild2',_('Birth'),birth)
                
        if self.missingInfo or death != None:
            if spouse_count == 0 or not self.incChiMar:
                self.dump_child_event('FGR-TextChild2',_('Death'),death)
            else:
                self.dump_child_event('FGR-TextChild1',_('Death'),death)

        if self.incChiMar:
            index = 0
            for family_handle in person.get_family_handle_list():
                m = None
                index = index + 1
                family = self.database.get_family_from_handle(family_handle)

                for event_ref in family.get_event_ref_list():
                    if event_ref:
                        event = self.database.get_event_from_handle(event_ref.ref)
                        if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                            m = event
                            break  
                
                spouse_id = None

                if person_handle == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()
    	    
                if spouse_id:
                    self.doc.start_row()
                    if m or index != families:
                        self.doc.start_cell('FGR-TextChild1')
                    else:
                        self.doc.start_cell('FGR-TextChild2')
                    self.doc.start_paragraph('FGR-Normal')
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.start_cell('FGR-TextContents')
                    self.doc.start_paragraph('FGR-Normal')
                    self.doc.write_text(_("Spouse"))
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.start_cell('FGR-TextContentsEnd',2)
                    self.doc.start_paragraph('FGR-Normal')

                    spouse = self.database.get_person_from_handle(spouse_id)
                    spouse_name = _nd.display(spouse)
                    if self.incRelDates:
                        birth = "  "
                        birth_ref = spouse.get_birth_ref()
                        if birth_ref:
                            event = self.database.get_event_from_handle(birth_ref.ref)
                            birth = DateHandler.get_date(event)
                        death = "  "
                        death_ref = spouse.get_death_ref()
                        if death_ref:
                            event = self.database.get_event_from_handle(death_ref.ref)
                            death = DateHandler.get_date(event)
                        if birth_ref or death_ref:
                            spouse_name = "%s (%s - %s)" % (spouse_name,birth,death)
                    mark = ReportUtils.get_person_mark(self.database,spouse)
                    self.doc.write_text(spouse_name,mark)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                    self.doc.end_row()
                  
                if m:
                    evtName = str(RelLib.EventType(RelLib.EventType.MARRIAGE))
                    if index == families:
                        self.dump_child_event('FGR-TextChild2',evtName,m)
                    else:
                        self.dump_child_event('FGR-TextChild1',evtName,m)
            
    def dump_family(self,family_handle,generation):
        self.doc.start_paragraph('FGR-Title')
        if self.recursive and self.generations:
            title=_("Family Group Report - Generation %d") % generation
        else:
            title=_("Family Group Report")
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.write_text( title, mark )
        self.doc.end_paragraph()
	
        family = self.database.get_family_from_handle(family_handle)

        self.dump_parent(_("Husband"),family.get_father_handle())
        self.doc.start_paragraph("FGR-blank")
        self.doc.end_paragraph()
        
        if self.incParMar:
            self.dump_marriage(family)
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()

        self.dump_parent(_("Wife"),family.get_mother_handle())

        length = len(family.get_child_ref_list())
        if length > 0:
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()
            self.doc.start_table('FGR-Children','FGR-ChildTable')
            self.doc.start_row()
            self.doc.start_cell('FGR-ParentHead',4)
            self.doc.start_paragraph('FGR-ParentName')
            self.doc.write_text(_("Children"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            index = 1
            for child_ref in family.get_child_ref_list():
                self.dump_child(index,child_ref.ref)
                index = index + 1
            self.doc.end_table()

        if self.recursive:
            for child_ref in family.get_child_ref_list():
                child = self.database.get_person_from_handle(child_ref.ref)
                for child_family_handle in child.get_family_handle_list():
                    if child_family_handle != family_handle:
                        self.doc.page_break()
                        self.dump_family(child_family_handle,(generation+1))

    def write_report(self):
        if self.family_handle:
            self.dump_family(self.family_handle,1)
        else:
            self.doc.start_paragraph('FGR-Title')
            self.doc.write_text(_("Family Group Report"))
            self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FamilyGroupOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'family_id'    : '',
            'recursive'    : 0,
            'missinginfo'  : 1,
            'generations'  : 1,
            'incParEvents' : 0,
            'incParAddr'   : 0,
            'incParNotes'  : 0,
            'incParNames'  : 0,
            'incParMar'    : 0,
            'incChiMar'    : 1,            
            'incRelDates'  : 0,
        }

        self.options_help = {
            'family_id'    : ("=ID","Gramps ID of the person's family.",
                            "Use show=id to get ID list.",
                            ),
            'recursive'    : ("=0/1","Create reports for all decendants of this family.",
                            ["Do not create reports for decendants","Create reports for decendants"],
                            False),

            'missinginfo'  : ("=0/1","Whether to include fields for missing information.",
                            ["Do not include missing info","Include missing info"],
                            True),

            'generations'  : ("=0/1","Whether to include the generation on each report (recursive only).",
                            ["Do not include the generation","Include the generation"],
                            True),

            'incParEvents' : ("=0/1","Whether to include events for parents.",
                            ["Do not include parental events","Include parental events"],
                            True),

            'incParAddr'   : ("=0/1","Whether to include addresses for parents.",
                            ["Do not include parental addresses","Include parental addresses"],
                            True),
                                     
            'incParNotes'  : ("=0/1","Whether to include notes for parents.",
                            ["Do not include parental notes","Include parental notes"],
                            True),
                                     
            'incParNames'  : ("=0/1","Whether to include alternate names for parents.",
                            ["Do not include parental names","Include parental names"],
                            True),
                            
            'incParMar'    : ("=0/1","Whether to include marriage information for parents.",
                            ["Do not include parental marriage info","Include parental marriage info"],
                            False),
                            
            'incChiMar'    : ("=0/1","Whether to include marriage information for children.",
                            ["Do not include children marriage info","Include children marriage info"],
                            True),

            'incRelDates'  : ("=0/1","Whether to include dates for relatives.",
                            ["Do not include dates of relatives","Include dates of relatives"],
                            True),
        }

    def get_families(self,database,person):
        """
        Create a mapping of all spouse names:families to be put
        into the 'extra' option menu in the report options box.  If
        the selected person has never been married then this routine
        will return a placebo label and disable the OK button.
        """
        families = []
        family_id = None
        family_list = person.get_family_handle_list()
        for family_handle in family_list:
            family = database.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            if person.get_handle() == family.get_father_handle():
                spouse_handle = family.get_mother_handle()
            else:
                spouse_handle = family.get_father_handle()
            if spouse_handle:
                spouse = database.get_person_from_handle(spouse_handle)
                name = spouse.get_primary_name().get_name()
            else:
                name = _("unknown")
            name = "%s (%s)" % (name,family_id)
            families.append((family_id,name))
        return families

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        
        families = self.get_families(dialog.db,dialog.person)
        family_id = self.options_dict['family_id']

        self.spouse_menu = gtk.combo_box_new_text()
        index = 0
        family_index = 0
        for item in families:
            self.spouse_menu.append_text(item[1])
            if item[0] == family_id:
                family_index = index
            index = index + 1
        self.spouse_menu.set_active(family_index)
	
        # Recursive
        self.recursive_option = gtk.CheckButton()
        self.recursive_option.set_active(self.options_dict['recursive'])
	
        # Missing Info
        self.missing_info_option = gtk.CheckButton(_("Print fields for missing information"))
        self.missing_info_option.set_active(self.options_dict['missinginfo'])
	
        # Generations
        self.include_generations_option = gtk.CheckButton(_("Generation numbers (recursive only)"))
        self.include_generations_option.set_active(self.options_dict['generations'])
	
        # Parental Events
        self.include_par_events_option = gtk.CheckButton(_("Parent Events"))
        self.include_par_events_option.set_active(self.options_dict['incParEvents'])
        
        # Parental Addresses
        self.include_par_addr_option = gtk.CheckButton(_("Parent Addresses"))
        self.include_par_addr_option.set_active(self.options_dict['incParAddr'])
	
        # Parental Notes
        self.include_par_notes_option = gtk.CheckButton(_("Parent Notes"))
        self.include_par_notes_option.set_active(self.options_dict['incParNotes'])
        
        # Parental Names
        self.include_par_names_option = gtk.CheckButton(_("Alternate Parent Names"))
        self.include_par_names_option.set_active(self.options_dict['incParNames'])
        
        # Parental Marriage
        self.include_par_marriage_option = gtk.CheckButton(_("Parent Marriage"))
        self.include_par_marriage_option.set_active(self.options_dict['incParMar'])
        
        # Relatives Dates
        self.include_rel_dates_option = gtk.CheckButton(_("Dates of Relatives (father, mother, spouse)"))
        self.include_rel_dates_option.set_active(self.options_dict['incRelDates'])

        # Children Marriages
        self.include_chi_marriage_option = gtk.CheckButton(_("Children Marriages"))
        self.include_chi_marriage_option.set_active(self.options_dict['incChiMar'])

        dialog.add_option(_("Spouse"),self.spouse_menu)
        dialog.add_option(_("Recursive"),self.recursive_option)
        dialog.add_frame_option(_('Include'),'',self.include_generations_option)
        dialog.add_frame_option(_('Include'),'',self.include_par_events_option)
        dialog.add_frame_option(_('Include'),'',self.include_par_addr_option)
        dialog.add_frame_option(_('Include'),'',self.include_par_notes_option)
        dialog.add_frame_option(_('Include'),'',self.include_par_names_option)
        dialog.add_frame_option(_('Include'),'',self.include_par_marriage_option)
        dialog.add_frame_option(_('Include'),'',self.include_chi_marriage_option)
        dialog.add_frame_option(_('Include'),'',self.include_rel_dates_option)
        dialog.add_frame_option(_('Missing Information'),'',self.missing_info_option)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        families = self.get_families(dialog.db,dialog.person)
        family_index = self.spouse_menu.get_active()
        if families:
            self.options_dict['family_id'] = families[family_index][0]
	    
        self.options_dict['recursive']    = int(self.recursive_option.get_active())
        self.options_dict['missinginfo']  = int(self.missing_info_option.get_active())
        self.options_dict['generations']  = int(self.include_generations_option.get_active())
        self.options_dict['incParEvents'] = int(self.include_par_events_option.get_active())
        self.options_dict['incParAddr']   = int(self.include_par_addr_option.get_active())
        self.options_dict['incParNotes']  = int(self.include_par_notes_option.get_active())
        self.options_dict['incParNames']  = int(self.include_par_names_option.get_active())
        self.options_dict['incParMar']    = int(self.include_par_marriage_option.get_active())
        self.options_dict['incChiMar']    = int(self.include_chi_marriage_option.get_active())
        self.options_dict['incRelDates']  = int(self.include_rel_dates_option.get_active())

    def make_default_style(self,default_style):
        """Make default output style for the Family Group Report."""
        para = BaseDoc.ParagraphStyle()
        font = BaseDoc.FontStyle()
        font.set_size(4)
        para.set_font(font)
        default_style.add_style('FGR-blank',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title of the page."))
        default_style.add_style('FGR-Title',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style('FGR-Normal',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for the text related to the children.'))
        default_style.add_style('FGR-ChildText',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_("The style used for the parent's name"))
        default_style.add_style('FGR-ParentName',para)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
register_report(
    name = 'family_group',
    category = CATEGORY_TEXT,
    report_class = FamilyGroup,
    options_class = FamilyGroupOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Family Group Report"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Creates a family group report, showing information "
                  "on a set of parents and their children."),
    )
