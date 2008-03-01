#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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

"""Reports/Text Reports/Family Group Report"""

#------------------------------------------------------------------------
#
# GRAMPS 
#
#------------------------------------------------------------------------
import gen.lib
from PluginUtils import register_report, BooleanOption, FamilyOption
from ReportBase import Report, ReportUtils, MenuReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import DateHandler
from TransUtils import sgettext as _
from BasicUtils import name_displayer as _nd

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup(Report):

    def __init__(self, database, options_class):
        """
        Create the DetAncestorReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        family_handle - Handle of the family to write report on.
        includeAttrs  - Whether to include attributes
        """
        Report.__init__(self, database, options_class)
        menu = options_class.menu

        self.family_handle = None

        family_id = menu.get_option_by_name('family_id').get_value()
        family = database.get_family_from_gramps_id(family_id)
        if family:
            self.family_handle = family.get_handle()
        else:
            self.family_handle = None

        self.recursive     = menu.get_option_by_name('recursive').get_value()
        self.missingInfo   = menu.get_option_by_name('missinginfo').get_value()
        self.generations   = menu.get_option_by_name('generations').get_value()
        self.incParEvents  = menu.get_option_by_name('incParEvents').get_value()
        self.incParAddr    = menu.get_option_by_name('incParAddr').get_value()
        self.incParNotes   = menu.get_option_by_name('incParNotes').get_value()
        self.incParNames   = menu.get_option_by_name('incParNames').get_value()
        self.incParMar     = menu.get_option_by_name('incParMar').get_value()
        self.incRelDates   = menu.get_option_by_name('incRelDates').get_value()
        self.incChiMar     = menu.get_option_by_name('incChiMar').get_value()
        self.includeAttrs  = menu.get_option_by_name('incattrs').get_value()

    def dump_parent_event(self, name,event):
        place = ""
        date = ""
        descr = ""
        if event:
            date = DateHandler.get_date(event)
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database,place_handle)
            descr = event.get_description()
            
            if self.includeAttrs:
                for attr in event.get_attribute_list():
                    if descr:
                        descr += "; "
                    descr += _("%(type)s: %(value)s") % {
                        'type'     : attr.get_type(),
                        'value'    : attr.get_value() }            

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

    def dump_parent_line(self, name,text):
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
            person = gen.lib.Person()
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
        evtName = str(gen.lib.EventType())
        if birth_ref:
            birth = self.database.get_event_from_handle(birth_ref.ref)
        if birth or self.missingInfo:
            self.dump_parent_event(evtName,birth)

        death_ref = person.get_death_ref()
        death = None
        evtName = str(gen.lib.EventType(gen.lib.EventType.DEATH))
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

        if self.incParNotes:
            for notehandle in person.get_note_list():
                note = self.database.get_note_from_handle(notehandle)
                self.dump_parent_line(_("Note"), note.get(False))
                
        if self.includeAttrs:
            for attr in person.get_attribute_list():
                self.dump_parent_line(str(attr.get_type()),attr.get_value())

        if self.incParNames:
            for alt_name in person.get_alternate_names():
                name_type = str( alt_name.get_type() )
                name = _nd.display_name(alt_name)
                self.dump_parent_line(name_type, name)

        self.doc.end_table()

    def dump_marriage(self,family):

        if not family:
            return

        m = None
        family_list = family.get_event_ref_list()
        for event_ref in family_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event.get_type() == gen.lib.EventType.MARRIAGE:
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
                    if event.get_type() != gen.lib.EventType.MARRIAGE:
                        self.dump_parent_event(str(event.get_type()),event)
            
            self.doc.end_table()

    def dump_child_event(self,text, name,event):
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
        if person.get_gender() == gen.lib.Person.MALE:
            self.doc.write_text(index_str + _("acronym for male|M"))
        elif person.get_gender() == gen.lib.Person.FEMALE:
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
                        if int(event.get_type()) == gen.lib.EventType.MARRIAGE:
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
                    evtName = str(gen.lib.EventType(gen.lib.EventType.MARRIAGE))
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
# MenuReportOptions
#
#------------------------------------------------------------------------
class FamilyGroupOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        
        ##########################
        category_name = _("Report Options")
        ##########################
        
        family_id = FamilyOption(_("Center Family"))
        family_id.set_help(_("The center family for the report"))
        menu.add_option(category_name, "family_id", family_id)
        
        recursive = BooleanOption(_('Recursive'),False)
        recursive.set_help(_("Create reports for all descendants "
                             "of this family."))
        menu.add_option(category_name,"recursive",recursive)
        
        ##########################
        category_name = _("Include")
        ##########################
        
        generations = BooleanOption(_("Generation numbers "
                                      "(recursive only)"),True)
        generations.set_help(_("Whether to include the generation on each "
                               "report (recursive only)."))
        menu.add_option(category_name,"generations",generations)
        
        incParEvents = BooleanOption(_("Parent Events"),False)
        incParEvents.set_help(_("Whether to include events for parents."))
        menu.add_option(category_name,"incParEvents",incParEvents)
        
        incParAddr = BooleanOption(_("Parent Addresses"),False)
        incParAddr.set_help(_("Whether to include addresses for parents."))
        menu.add_option(category_name,"incParAddr",incParAddr)
        
        incParNotes = BooleanOption(_("Parent Notes"),False)
        incParNotes.set_help(_("Whether to include notes for parents."))
        menu.add_option(category_name,"incParNotes",incParNotes)
        
        incattrs = BooleanOption(_("Parent Attributes"),False)
        incattrs.set_help(_("Whether to include attributes."))
        menu.add_option(category_name,"incattrs",incattrs)
        
        incParNames = BooleanOption(_("Alternate Parent Names"),False)
        incParNames.set_help(_("Whether to include alternate "
                               "names for parents."))
        menu.add_option(category_name,"incParNames",incParNames)
        
        incParMar = BooleanOption(_("Parent Marriage"),False)
        incParMar.set_help(_("Whether to include marriage information "
                             "for parents."))
        menu.add_option(category_name,"incParMar",incParMar)
        
        incRelDates = BooleanOption(_("Dates of Relatives"),False)
        incRelDates.set_help(_("Whether to include dates for relatives "
                               "(father, mother, spouse)."))
        menu.add_option(category_name,"incRelDates",incRelDates)
        
        incChiMar = BooleanOption(_("Children Marriages"),True)
        incChiMar.set_help(_("Whether to include marriage information "
                             "for children."))
        menu.add_option(category_name,"incChiMar",incChiMar)
        
        ##########################
        category_name = _("Missing Information")
        ##########################
                
        missinginfo = BooleanOption(_("Print fields for missing "
                                      "information"),True)
        missinginfo.set_help(_("Whether to include fields for missing "
                               "information."))
        menu.add_option(category_name,"missinginfo",missinginfo)

    def make_default_style(self,default_style):
        """Make default output style for the Family Group Report."""
        para = BaseDoc.ParagraphStyle()
        #Paragraph Styles
        font = BaseDoc.FontStyle()
        font.set_size(4)
        para.set_font(font)
        default_style.add_paragraph_style('FGR-blank',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style('FGR-Title',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style('FGR-Normal',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for the text related to the children.'))
        default_style.add_paragraph_style('FGR-ChildText',para)

        font = BaseDoc.FontStyle()
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_description(_("The style used for the parent's name"))
        default_style.add_paragraph_style('FGR-ParentName',para)
        
        #Table Styles
        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-ParentHead',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-TextContents',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        default_style.add_cell_style('FGR-TextChild1',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        default_style.add_cell_style('FGR-TextChild2',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-TextContentsEnd',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        default_style.add_cell_style('FGR-ChildName',cell)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,20)
        table.set_column_width(1,40)
        table.set_column_width(2,40)
        default_style.add_table_style('FGR-ParentTable',table)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,7)
        table.set_column_width(1,18)
        table.set_column_width(2,35)
        table.set_column_width(3,40)
        default_style.add_table_style('FGR-ChildTable',table)

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
    description = _("Produces a family group report showing information "
                    "on a set of parents and their children."),
    )
