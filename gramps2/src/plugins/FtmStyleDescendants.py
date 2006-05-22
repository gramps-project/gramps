#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

# Written by Alex Roitman, largely based on the FtmStyleAncestors.py
# report by Don Allingham

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import cStringIO
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import Report, ReportOptions, ReportUtils, register_report
import BaseDoc
import RelLib
import DateHandler
import const

#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class FtmDescendantReport(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the Ftm-Style Descendant object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.
        """

        Report.Report.__init__(self,database,person,options_class)

        self.anc_map = {}
        self.gen_map = {}

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()

        self.sref_map = {}
        self.sref_index = 0
        
    def define_table_styles(self):
        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0,10)
        tbl.set_column_width(1,5)
        tbl.set_column_width(2,85)
        self.doc.add_table_style('FTD-ChildTable',tbl)

        cell = BaseDoc.TableCellStyle()
        self.doc.add_cell_style('FTD-Normal',cell)

    def apply_filter(self,person_handle,index,generation=1):

        if (not person_handle) or (generation > self.max_generations):
            return

        self.anc_map[index] = person_handle
        try:
            self.gen_map[generation].append(index)
        except:
            self.gen_map[generation] = []
            self.gen_map[generation].append(index)

        person = self.database.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                ix = max(self.anc_map.keys())
                self.apply_filter(child_handle,ix+1,generation+1)


    def write_report(self):

        self.apply_filter(self.start_person.get_handle(),1)
        
        name = self.start_person.get_primary_name().get_regular_name()
        self.doc.start_paragraph("FTD-Title")
        title = _("Descendants of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        generations = self.gen_map.keys()
        generations.sort()

        for generation in generations:
            if self.pgbrk and generation > 1:
                self.doc.page_break()
            self.doc.start_paragraph("FTD-Generation")
            t = _("Generation No. %d") % generation
            self.doc.write_text(t)
            self.doc.end_paragraph()

            indexlist = self.gen_map[generation]
            indexlist.sort()
            for key in indexlist:
                person_handle = self.anc_map[key]
                person = self.database.get_person_from_handle(person_handle)

                self.doc.start_paragraph("FTD-Entry","%d." % key)
                name = person.get_primary_name().get_regular_name()
                self.doc.start_bold()
                self.doc.write_text(name)
                self.doc.end_bold()

                text = ReportUtils.born_died_str(self.database,person,
                                                    self.endnotes,None,"")
                if text:
                    self.doc.write_text(text)
                    self.doc.write_text(' ')

                death_valid = bool(person.get_death_handle())
                self.print_parents(person,death_valid)
                self.print_spouse(person)
                self.doc.end_paragraph()

                self.print_notes(person)
                self.print_more_about(person)
                self.print_more_about_families(person)
                if generation < self.max_generations:
                    self.print_children(person)

        self.write_endnotes()

    def write_endnotes(self):
        keys = self.sref_map.keys()
        if not keys:
            return

        self.doc.start_paragraph('FTD-Generation')
        self.doc.write_text(_('Endnotes'))
        self.doc.end_paragraph()
        
        keys.sort()
        for key in keys:
            srcref = self.sref_map[key]
            base_handle = srcref.get_reference_handle()
            base = self.database.get_source_from_handle(base_handle)
            
            self.doc.start_paragraph('FTD-Endnotes',"%d." % key)
            self.doc.write_text(base.get_title())

            for item in [ base.get_author(), base.get_publication_info(),
                          base.get_abbreviation(),
                          DateHandler.get_date(srcref),]:
                if item:
                    self.doc.write_text('; %s' % item)

            item = srcref.get_text()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Text:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            item = srcref.get_note()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Comments:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            self.doc.write_text('.')
            self.doc.end_paragraph()

    def endnotes(self,obj):
        if not obj:
            return ""
        msg = cStringIO.StringIO()
        slist = obj.get_source_references()
        if slist:
            msg.write('<super>')
            first = 1
            for ref in slist:
                if not first:
                    msg.write(',')
                first = 0
                ref_base = ref.get_reference_handle()
                the_key = 0
                for key in self.sref_map.keys():
                    if ref_base == self.sref_map[key].get_reference_handle():
                        the_key = key
                        break
                if the_key:
                    msg.write("%d" % the_key)
                else:
                    self.sref_index += 1
                    self.sref_map[self.sref_index] = ref
                    msg.write("%d" % self.sref_index)
            msg.write('</super>')
        str = msg.getvalue()
        msg.close()
        return str

    def print_notes(self,person):
        note = person.get_note()
        if not note.strip():
            return
        self.doc.start_paragraph('FTD-SubEntry')
        self.doc.write_text(_('Notes for %(person)s:') % { 
            'person' : person.get_primary_name().get_regular_name()} )
        self.doc.end_paragraph()
        format = person.get_note_format()
        self.doc.write_note(note,format,'FTD-Details')
        
    def print_more_about(self,person):

        first = 1
        ncount = 1
        for name in person.get_alternate_names():
            if first:
                self.doc.start_paragraph('FTD-SubEntry')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                   'person_name' : person.get_primary_name().get_regular_name() })
                self.doc.end_paragraph()
                first = 0
            self.doc.start_paragraph('FTD-Details')
            self.doc.write_text(_('Name %(count)d: %(name)s%(endnotes)s') % {
                'count' : ncount, 'name' : name.get_regular_name(),
                'endnotes' : self.endnotes(name),
                })
            self.doc.end_paragraph()
            ncount += 1
            
        for event_handle in person.get_event_list():
            if not event_handle:
                continue
            event = self.database.get_event_from_handle(event_handle)
            date = DateHandler.get_date(event)
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle)
            else:
                place = None

            if not date and not place:
                continue
            if first:
                self.doc.start_paragraph('FTD-SubEntry')
                name = person.get_primary_name().get_regular_name()
                self.doc.write_text(_('More about %(person_name)s:') % { 'person_name' : name })
                self.doc.end_paragraph()
                first = 0

            self.doc.start_paragraph('FTD-Details')
            if date and place:
                self.doc.write_text(_('%(event_name)s: %(date)s, %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'date' : date,
                    'endnotes' : self.endnotes(event),
                    'place' : place.get_title() })
            elif date:
                self.doc.write_text(_('%(event_name)s: %(date)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'date' : date})
            else:
                self.doc.write_text(_('%(event_name)s: %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'place' : place.get_title() })
            if event.get_description():
                self.doc.write_text(event.get_description())
            self.doc.end_paragraph()


    def print_more_about_families(self,person):
        "More about husband and wife"
        
        first = 1

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if father_handle and mother_handle:
                husband = self.database.get_person_from_handle(father_handle).get_primary_name().get_regular_name()
                wife = self.database.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()
            else:
                continue
            for event_handle in family.get_event_list():
                if not event_handle:
                    continue
                event = self.database.get_event_from_handle(event_handle)
                date = DateHandler.get_date(event)
                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.database.get_place_from_handle(place_handle)
                else:
                    place = None

                if not date and not place:
                    continue
                if first:
                    self.doc.start_paragraph('FTD-SubEntry')
                    self.doc.write_text(_('More about %(husband)s and %(wife)s:') % { 'husband' : husband, 'wife' : wife })
                    self.doc.end_paragraph()
                    first = 0

                self.doc.start_paragraph('FTD-Details')
                if date and place:
                    self.doc.write_text(_('%(event_name)s: %(date)s, %(place)s%(endnotes)s. ') % {
                        'event_name' : _(event.get_name()),
                        'date' : date,
                        'endnotes' : self.endnotes(event),
                        'place' : place.get_title() })
                elif date:
                    self.doc.write_text(_('%(event_name)s: %(date)s%(endnotes)s. ') % {
                        'event_name' : _(event.get_name()),
                        'endnotes' : self.endnotes(event),
                        'date' : date})
                else:
                    self.doc.write_text(_('%(event_name)s: %(place)s%(endnotes)s. ') % {
                        'event_name' : _(event.get_name()),
                        'endnotes' : self.endnotes(event),
                        'place' : place.get_title() })
                if event.get_description():
                    self.doc.write_text(event.get_description())
                self.doc.end_paragraph()


    def print_children(self,person):
        "Children of such-and-such"

        name = person.get_primary_name().get_regular_name()
        
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            first = 1
        
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if father_handle == person.get_handle():
                spouse_id = mother_handle
            else:
                spouse_id = father_handle
            spouse = self.database.get_person_from_handle(spouse_id)

            child_index = 0
            for child_handle in family.get_child_handle_list():
                child = self.database.get_person_from_handle(child_handle)
                child_index = child_index + 1
                for (ind,p_id) in self.anc_map.items():
                    if p_id == child_handle:
                        index = ind

                if first:
                    first = 0
                    self.doc.start_paragraph('FTD-SubEntry')
                    if spouse:
                        self.doc.write_text(_('Children of %(person_name)s and %(spouse_name)s are:') % { 
                            'person_name' : name,  'spouse_name' : spouse.get_primary_name().get_regular_name() })
                    else:
                        self.doc.write_text(_('Children of %(person_name)s are:') % { 'person_name' : name })
                    self.doc.end_paragraph()
                    self.doc.start_table(family.get_handle(),'FTD-ChildTable')

                self.doc.start_row()
                self.doc.start_cell('FTD-Normal')
                self.doc.start_paragraph('FTD-Child-Num')
                self.doc.write_text("%d." % index)
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell('FTD-Normal')
                self.doc.start_paragraph('FTD-Child-Num')
                self.doc.write_text("%s." % ReportUtils.roman(child_index).lower())
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell('FTD-Normal')
                self.doc.start_paragraph('FTD-Details')
                
                text = ReportUtils.born_died_str(self.database,child,
                                                    self.endnotes)
                self.doc.write_text(text)

                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()

            if not first: 
                self.doc.end_table()
            first = 1

    def print_spouse(self,person):
        family_list = person.get_family_handle_list()
        if not family_list:
            return
        family_handle = family_list[0]
        family = self.database.get_family_from_handle(family_handle)
        if family.get_father_handle() == person.get_handle():
            spouse_id = family.get_mother_handle()
        else:
            spouse_id = family.get_father_handle()
        if not spouse_id:
            return
        spouse = self.database.get_person_from_handle(spouse_id)
        
        for event_handle in family.get_event_list():
            if event_handle:
                event = self.database.get_event_from_handle(event_handle)
                if event.get_name() == "Marriage":
                    break
        else:
            event = None

        if not event:
            return

        text = ReportUtils.married_str(self.database,person,spouse,event,
                                                    self.endnotes)
        if text:
            self.doc.write_text(text)
            self.doc.write_text(' ')

        text = ReportUtils.born_died_str(self.database,spouse,
                                                    self.endnotes,"",0)
        if text:
            self.doc.write_text(text)
            self.doc.write_text(' ')

        death_valid = bool(spouse.get_death_handle())
        self.print_parents(spouse,death_valid)


    def print_parents(self,person,dead):
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mother_name = mother.get_primary_name().get_regular_name()
            else:
                mother_name = ""
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                father_name = father.get_primary_name().get_regular_name()
            else:
                father_name = ""

            text = ReportUtils.child_str(person,
                                father_name,mother_name,dead)
            if text:
                self.doc.write_text(text)
                self.doc.write_text(' ')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FtmDescendantOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
        }

    def make_default_style(self,default_style):
        """Make the default output style for the FTM Style Descendant report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("FTD-Title",para)
    
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("FTD-Generation",para)
    
        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTD-Entry",para)
    
        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTD-Details",para)
    
        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=0.0,pad=0.05)
        para.set_description(_('The style used for numbering children.'))
        default_style.add_style("FTD-Child-Num",para)

        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTD-SubEntry",para)

        para = BaseDoc.ParagraphStyle()
        para.set(pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTD-Endnotes",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'ftm_descendant_report',
    category = Report.CATEGORY_TEXT,
    report_class = FtmDescendantReport,
    options_class = FtmDescendantOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("FTM Style Descendant Report"),
    status = _("Beta"),
    description= _("Produces a textual descendant report similar to Family Tree Maker."),
    author_name="Alex Roitman",
    author_email="shura@alex.neuro.umn.edu",
    unsupported=True
    )
