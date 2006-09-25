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

"Text Reports/Ahnentafel Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import math
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import Errors
import NameDisplay

#------------------------------------------------------------------------
#
# log2val
#
#------------------------------------------------------------------------
def log2(val):
    return int(math.log10(val)/math.log10(2))

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class AncestorReport(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the AncestorReport object that produces the Ahnentafel report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.

        """

        Report.__init__(self,database,person,options_class)

        self.map = {}
        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()

    def apply_filter(self,person_handle,index,generation=1):
        if not person_handle or generation > self.max_generations:
            return
        self.map[index] = person_handle

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2,generation+1)
            self.apply_filter(family.get_mother_handle(),(index*2)+1,generation+1)

    def write_report(self):

        self.apply_filter(self.start_person.get_handle(),1)

        name = NameDisplay.displayer.display_formal(self.start_person)
        title = _("Ahnentafel Report for %s") % name
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)        
        self.doc.start_paragraph("AHN-Title")
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        generation = 0

        for key in keys :
            if generation == log2(key):
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                generation += 1
                mark =  BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,2)  
                self.doc.start_paragraph("AHN-Generation")
                self.doc.write_text(_("Generation %d") % generation,mark)
                self.doc.end_paragraph()

            self.doc.start_paragraph("AHN-Entry","%d." % key)
            person_handle = self.map[key]
            person = self.database.get_person_from_handle(person_handle)
            name = NameDisplay.displayer.display_formal(person)
            mark = ReportUtils.get_person_mark(self.database,person)
        
            self.doc.start_bold()
            self.doc.write_text(name.strip(),mark)
            self.doc.end_bold()
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Check birth record

            self.doc.write_text(ReportUtils.born_str(self.database,person))
            self.doc.write_text(ReportUtils.died_str(self.database,person,0))
            self.doc.write_text(ReportUtils.buried_str(self.database,person,0))
                        
            self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
        }

    def make_default_style(self,default_style):
        """Make the default output style for the Ahnentafel report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)       
        #para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("AHN-Title",para)
    
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)        
        #para.set(pad=0.5)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("AHN-Generation",para)
    
        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)        
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("AHN-Entry",para)

#------------------------------------------------------------------------
#
# Register the plugin
#
#------------------------------------------------------------------------
register_report(
    name = 'ancestor_report',
    category = CATEGORY_TEXT,
    report_class = AncestorReport,
    options_class = AncestorOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Ahnentafel Report"),
    status=(_("Stable")),
    description= _("Produces a textual ancestral report"),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )
