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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import cStringIO
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
import RelLib
import DateHandler
import const
from PluginUtils import Report, ReportOptions, ReportUtils, register_report

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class FtmAncestorReport(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the Ftm-Style Ancestor object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen     - Maximum number of generations to include.
        pagebgg - Whether to include page breaks between generations.
        """
        Report.Report.__init__(self,database,person,options_class)

        self.map = {}

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()

        self.sref_map = {}
        self.sref_index = 0
        
    def apply_filter(self,person_handle,index,generation=1):
        if not person_handle or generation >= self.max_generations:
            return
        self.map[index] = (person_handle,generation)

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2,generation+1)
            self.apply_filter(family.get_mother_handle(),(index*2)+1,generation+1)

    def write_report(self):

        self.apply_filter(self.start_person.get_handle(),1)
        
        name = self.start_person.get_primary_name().get_regular_name()
        self.doc.start_paragraph("FTA-Title")
        title = _("Ancestors of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        old_gen = 0
        for key in keys :
            (person_handle,generation) = self.map[key]
            if old_gen != generation:
                if self.pgbrk and generation > 1:
                    self.doc.page_break()
                self.doc.start_paragraph("FTA-Generation")
                t = _("Generation No. %d") % generation
                self.doc.write_text(t)
                self.doc.end_paragraph()
                old_gen = generation

            person = self.database.get_person_from_handle(person_handle)
            pri_name = person.get_primary_name()
            self.doc.start_paragraph("FTA-Entry","%d." % key)
            name = pri_name.get_regular_name()
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

        self.write_endnotes()

    def write_endnotes(self):
        keys = self.sref_map.keys()
        if not keys:
            return

        self.doc.start_paragraph('FTA-Generation')
        self.doc.write_text(_('Endnotes'))
        self.doc.end_paragraph()
        
        keys.sort()
        for key in keys:
            srcref = self.sref_map[key]
            base = self.database.get_source_from_handle(srcref.get_base_handle())
            
            self.doc.start_paragraph('FTA-Endnotes',"%d." % key)
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
                ref_base = ref.get_base_handle()
                the_key = 0
                for key in self.sref_map.keys():
                    if ref_base == self.sref_map[key].get_base_handle():
                        the_key = key
                        break
                if the_key:
                    msg.write("%d" % the_key)
                else:
                    self.sref_index += 1
                    self.sref_map[self.sref_index] = ref
                    msg.write("%d" % self.sref_index)
            msg.write('</super>')
        value = msg.getvalue()
        msg.close()
        return value

    def print_notes(self,person):
        note = person.get_note()
        if not note.strip():
            return
        self.doc.start_paragraph('FTA-SubEntry')
        self.doc.write_text(_('Notes for %(person)s:') % { 
                'person' : person.get_primary_name().get_regular_name()} )
        self.doc.end_paragraph()
        format = person.get_note_format()
        self.doc.write_note(note,format,'FTA-Details')
        
    def print_more_about(self,person):

        first = 1
        ncount = 0
        for name in person.get_alternate_names():
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                        'person_name' : person.get_primary_name().get_regular_name() })
                self.doc.end_paragraph()
                first = 0
            self.doc.start_paragraph('FTA-Details')
            self.doc.write_text(_('Name %(count)d: %(name)s%(endnotes)s') % {
                'count' : ncount, 'name' : name.get_regular_name(),
                'endnotes' : self.endnotes(name),
                })
            self.doc.end_paragraph()
            ncount += 1
            
        for event_handle in person.get_event_list():
            event = self.database.get_event_from_handle(event_handle)
            date = DateHandler.get_date(event)
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle).get_title()
            else:
                place = u''
                
            if not date and not place_handle:
                continue
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                name = person.get_primary_name().get_regular_name()
                self.doc.write_text(_('More about %(person_name)s:') % { 
                        'person_name' : name })
                self.doc.end_paragraph()
                first = 0

            self.doc.start_paragraph('FTA-Details')
            if date and place:
                self.doc.write_text(_('%(event_name)s: %(date)s, %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'date' : date,
                    'endnotes' : self.endnotes(event),
                    'place' : place })
            elif date:
                self.doc.write_text(_('%(event_name)s: %(date)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'date' : date})
            else:
                self.doc.write_text(_('%(event_name)s: %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'place' : place })
            if event.get_description():
                self.doc.write_text(event.get_description())
            self.doc.end_paragraph()

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
        spouse_name = spouse.get_primary_name().get_regular_name()

        for event_handle in family.get_event_list():
            if event_handle:
                event = self.database.get_event_from_handle(event_handle)
                if event.get_name() == "Marriage":
                    break
        else:
            return

        date = DateHandler.get_date(event)
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.database.get_place_from_handle(place_handle).get_title()
        else:
            place = u''

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
            father_handle = family.get_father_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mother_name = mother.get_primary_name().get_regular_name()
            else:
                mother_name = ""
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
class FtmAncestorOptions(ReportOptions.ReportOptions):

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
        """Make the default output style for the FTM Style Ancestor report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("FTA-Title",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("FTA-Generation",para)
        
        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTA-Entry",para)

        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTA-Details",para)

        para = BaseDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTA-SubEntry",para)

        para = BaseDoc.ParagraphStyle()
        para.set(pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FTA-Endnotes",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'ftm_ancestor_report',
    category = Report.CATEGORY_TEXT,
    report_class = FtmAncestorReport,
    options_class = FtmAncestorOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("FTM Style Ancestor Report"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report similar to Family Tree Maker."),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net",
    unsupported=True
    )
