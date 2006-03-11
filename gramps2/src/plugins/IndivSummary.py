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

"Generate files/Individual Summary"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import RelLib
import const
import BaseDoc
from PluginUtils import Report, ReportOptions, register_report
import DateHandler

#------------------------------------------------------------------------
#
# IndivSummary
#
#------------------------------------------------------------------------
class IndivSummary(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the Ftm-Style Descendant object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        """

        Report.Report.__init__(self,database,person,options_class)

    def define_table_styles(self):
        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,80)
        self.doc.add_table_style("IVS-IndTable",tbl)

        cell = BaseDoc.TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        self.doc.add_cell_style("IVS-TableHead",cell)

        cell = BaseDoc.TableCellStyle()
        self.doc.add_cell_style("IVS-NormalCell",cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_longlist(1)
        self.doc.add_cell_style("IVS-ListCell",cell)

    def write_fact(self,event):
        if event == None:
            return
        name = const.display_event(event.get_name())
        date = DateHandler.get_date(event)
        place_handle = event.get_place_handle()
        if place_handle:
            place_obj = self.database.get_place_from_handle(place_handle)
            place = place_obj.get_title()
        else:
            place = ""
        
        description = event.get_description()
        if not date:
            if not place:
                return
            else:
                text = '%s. %s' % (place,description)
        else:
            if not place:
                text = '%s. %s' % (date,description)
            else:
                text = _('%(date)s in %(place)s.') % { 'date' : date,
                                                      'place' : place }
                text = '%s %s' % (text,description)

        self.doc.start_row()
        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):

        self.doc.start_paragraph("IVS-Normal")
        self.doc.end_paragraph()
        self.doc.start_table("three","IVS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IVS-TableHead",2)
        self.doc.start_paragraph("IVS-TableTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for family_handle in self.start_person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            if self.start_person.get_handle() == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
                
            self.doc.start_row()
            self.doc.start_cell("IVS-NormalCell",2)
            self.doc.start_paragraph("IVS-Spouse")
            if spouse_id:
                spouse = self.database.get_person_from_handle(spouse_id)
                self.doc.write_text(spouse.get_primary_name().get_regular_name())
            else:
                self.doc.write_text(_("unknown"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            for event_handle in family.get_event_list():
                event = self.database.get_event_from_handle(event_handle)
                self.write_fact(event)

            child_list = family.get_child_handle_list()
            if len(child_list):
                self.doc.start_row()
                self.doc.start_cell("IVS-NormalCell")
                self.doc.start_paragraph("IVS-Normal")
                self.doc.write_text(_("Children"))
                self.doc.end_paragraph()
                self.doc.end_cell()

                self.doc.start_cell("IVS-ListCell")
                self.doc.start_paragraph("IVS-Normal")
                
                first = 1
                for child_handle in child_list:
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    child = self.database.get_person_from_handle(child_handle)
                    self.doc.write_text(child.get_primary_name().get_regular_name())
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()

    def write_report(self):

        media_list = self.start_person.get_media_list()

        name = self.start_person.get_primary_name().get_regular_name()
        self.doc.start_paragraph("IVS-Title")
        self.doc.write_text(_("Summary of %s") % name)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IVS-Normal")
        self.doc.end_paragraph()

        if len(media_list) > 0:
            object_handle = media_list[0].get_reference_handle()
            object = self.database.get_object_from_handle(object_handle)
            mime_type = object.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                file = object.get_path()
                self.doc.start_paragraph("IVS-Normal")
                self.doc.add_media_object(file,"row",4.0,4.0)
                self.doc.end_paragraph()

        self.doc.start_table("one","IVS-IndTable")

        self.doc.start_row()
        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text("%s:" % _("Name"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text(self.start_person.get_primary_name().get_regular_name())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text("%s:" % _("Gender"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        if self.start_person.get_gender() == RelLib.Person.MALE:
            self.doc.write_text(_("Male"))
        else:
            self.doc.write_text(_("Female"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        fam_id = self.start_person.get_main_parents_family_handle()
        if fam_id:
            family = self.database.get_family_from_handle(fam_id)
            father_handle = family.get_father_handle()
            if father_handle:
                dad = self.database.get_person_from_handle(father_handle)
                father = dad.get_primary_name().get_regular_name()
            else:
                father = ""
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mom = self.database.get_person_from_handle(mother_handle)
                mother = mom.get_primary_name().get_regular_name()
            else:
                mother = ""
        else:
            father = ""
            mother = ""

        self.doc.start_row()
        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text("%s:" % _("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text(father)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text("%s:" % _("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("IVS-NormalCell")
        self.doc.start_paragraph("IVS-Normal")
        self.doc.write_text(mother)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_paragraph("IVS-Normal")
        self.doc.end_paragraph()
        
        self.doc.start_table("two","IVS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IVS-TableHead",2)
        self.doc.start_paragraph("IVS-TableTitle")
        self.doc.write_text(_("Individual Facts"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        event_list = [ self.start_person.get_birth_handle(),
                       self.start_person.get_death_handle() ]
        event_list = event_list + self.start_person.get_event_list()
        for event_handle in event_list:
            if event_handle:
                event = self.database.get_event_from_handle(event_handle)
                self.write_fact(event)
        self.doc.end_table()

        self.write_families()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndivSummaryOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def make_default_style(self,default_style):
        """Make the default output style for the Individual Summary Report."""
        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(16)
        p = BaseDoc.ParagraphStyle()
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_font(font)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_style("IVS-Title",p)
        
        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for category labels."))
        default_style.add_style("IVS-TableTitle",p)
    
        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the spouse's name."))
        default_style.add_style("IVS-Spouse",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("IVS-Normal",p)

#------------------------------------------------------------------------
#
# Register plugins
#
#------------------------------------------------------------------------
register_report(
    name = 'individual_summary',
    category = Report.CATEGORY_TEXT,
    report_class = IndivSummary,
    options_class = IndivSummaryOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Individual Summary"),
    status=(_("Stable")),
    description=_("Produces a detailed report on the selected person."),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org",
    unsupported = True
    )
