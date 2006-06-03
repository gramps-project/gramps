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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gnome/GTK modules
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
import Utils
import BaseDoc
from Filters import GenericFilter, Rules, CustomFilters
import DateHandler
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI

#------------------------------------------------------------------------
#
# IndivComplete
#
#------------------------------------------------------------------------
class IndivCompleteReport(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the IndivCompleteReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter    - Filter to be applied to the people of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        cites     - Whether or not to include source informaiton.
        """

        Report.__init__(self,database,person,options_class)

        self.use_srcs = options_class.handler.options_dict['cites']

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(CustomFilters.get_filters())
        self.filter = filters[filter_num]
        
    def define_table_styles(self):
        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,80)
        self.doc.add_table_style("IDS-IndTable",tbl)

        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,50)
        tbl.set_column_width(1,50)
        self.doc.add_table_style("IDS-ParentsTable",tbl)

        cell = BaseDoc.TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        self.doc.add_cell_style("IDS-TableHead",cell)

        cell = BaseDoc.TableCellStyle()
        self.doc.add_cell_style("IDS-NormalCell",cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_longlist(1)
        self.doc.add_cell_style("IDS-ListCell",cell)

    def write_fact(self,event):
        if event == None:
            return
        text = ""
        name = str(event.get_type())

        date = DateHandler.get_date(event)
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.database.get_place_from_handle(
                place_handle).get_title()
        else:
            place = ""
        
        if place and date:
            text = _('%(date)s in %(place)s. ') % { 'date' : date,
                                                    'place' : place }
        elif place and not date:
            text = '%s. ' % place
        elif date and not place:
            text = '%s. ' % date

        description = event.get_description()
        text = '%s%s. ' % (text,description)

        if self.use_srcs:
            for s in event.get_source_references():
                src_handle = s.get_reference_handle()
                src = self.database.get_source_from_handle(src_handle)
                text = "%s [%s]" % (text,src.get_gramps_id())
                self.slist.append(s)

        self.doc.start_row()
        self.normal_cell(name)
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text)
        self.doc.end_paragraph()
        
        note = event.get_note()
        if note:
            format = event.get_note_format()
            self.doc.write_note(note,format,'IDS-Normal')
        
        self.doc.end_cell()
        self.doc.end_row()

    def write_p_entry(self,label,parent,rel,mark=None):
        self.doc.start_row()
        self.normal_cell(label)

        if parent:
            self.normal_cell('%(parent)s, relationship: %(relation)s' %
                               { 'parent' : parent, 'relation' : rel },mark)
        else:
            self.normal_cell('')
        self.doc.end_row()

    def write_note(self):
        note = self.start_person.get_note()
        if note == '':
            return
        self.doc.start_table('note','IDS-IndTable')
        self.doc.start_row()
        self.doc.start_cell('IDS-TableHead',2)
        self.doc.start_paragraph('IDS-TableTitle')
        self.doc.write_text(_('Notes'))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell('IDS-NormalCell',2)
        format = self.start_person.get_note_format()
        self.doc.write_note(note,format,'IDS-Normal')
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_alt_parents(self):

        if len(self.start_person.get_parent_family_handle_list()) < 2:
            return
        
        self.doc.start_table("altparents","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Alternate Parents"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        family_handle_list = self.start_person.get_parent_family_handle_list()
        for family_handle in family_handle_list:
            if family_handle == \
                   self.start_person.get_main_parents_family_handle():
                continue
            
            family = self.database.get_family_from_handle(family_handle)
            
            # Get the mother and father relationships
            frel = ""
            mrel = ""
            child_handle = self.start_person.get_handle()
            child_ref_list = family.get_child_ref_list()
            for child_ref in child_ref_list:
                if child_ref.ref == child_handle:
                    frel = str(child_ref.get_father_relation())
                    mrel = str(child_ref.get_mother_relation())
            
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                fname = father.get_primary_name().get_regular_name()
                mark = ReportUtils.get_person_mark(self.database,father)
                self.write_p_entry(_('Father'),fname,frel,mark)
            else:
                self.write_p_entry(_('Father'),'','')

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                fname = mother.get_primary_name().get_regular_name()
                mark = ReportUtils.get_person_mark(self.database,father)
                self.write_p_entry(_('Mother'),fname,frel,mark)
            else:
                self.write_p_entry(_('Mother'),'','')
                
        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_alt_names(self):

        if len(self.start_person.get_alternate_names()) < 1:
            return
        
        self.doc.start_table("altparents","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Alternate Names"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for name in self.start_person.get_alternate_names():
            type = str( name.get_type() )
            self.doc.start_row()
            self.normal_cell(type)
            text = name.get_regular_name()
            if self.use_srcs:
                for s in name.get_source_references():
                    src_handle = s.get_reference_handle()
                    src = self.database.get_source_from_handle(src_handle)
                    text = "%s [%s]" % (text,src.get_gramps_id())
                    self.slist.append(s)
            self.normal_cell(text)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()
        
    def write_families(self):

        if not len(self.start_person.get_family_handle_list()):
            return
        
        self.doc.start_table("three","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
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
            self.doc.start_cell("IDS-NormalCell",2)
            self.doc.start_paragraph("IDS-Spouse")
            if spouse_id:
                spouse = self.database.get_person_from_handle(spouse_id)
                text = spouse.get_primary_name().get_regular_name()
                mark = ReportUtils.get_person_mark(self.database,spouse)
            else:
                text = _("unknown")
                mark = None
            self.doc.write_text(text,mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            for event_ref in family.get_event_ref_list():
                if event_ref:
                    event = self.database.get_event_from_handle(event_ref.ref)
                    self.write_fact(event)

            child_ref_list = family.get_child_ref_list()
            if len(child_ref_list):
                self.doc.start_row()
                self.normal_cell(_("Children"))

                self.doc.start_cell("IDS-ListCell")
                self.doc.start_paragraph("IDS-Normal")
                
                first = 1
                for child_ref in child_ref_list:
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    child = self.database.get_person_from_handle(child_ref.ref)
                    name = child.get_primary_name().get_regular_name()
                    mark = ReportUtils.get_person_mark(self.database,child)
                    self.doc.write_text(name,mark)
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_sources(self):

        if len(self.slist) == 0:
            return
        
        self.doc.start_table("three","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Sources"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for source in self.slist:
            self.doc.start_row()
            s_handle = source.get_reference_handle()
            src = self.database.get_source_from_handle(s_handle)
            self.normal_cell(src.get_gramps_id())
            self.normal_cell(src.get_title())
            self.doc.end_row()
        self.doc.end_table()

    def write_facts(self):
        self.doc.start_table("two","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Individual Facts"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        event_ref_list = [ self.start_person.get_birth_ref(),                  \
                           self.start_person.get_death_ref() ]    +            \
                           self.start_person.get_event_ref_list()
        for event_ref in event_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                self.write_fact(event)
        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def normal_cell(self,text,mark=None):
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text,mark)
        self.doc.end_paragraph()
        self.doc.end_cell()

    def write_report(self):
        plist = self.database.get_person_handles(sort_handles=False)
        if self.filter:
            ind_list = self.filter.apply(self.database,plist)
        else:
            ind_list = plist
            
        count = 0
        for person_handle in ind_list:
            self.start_person = self.database.get_person_from_handle(
                person_handle)
            self.write_person(count)
            count = count + 1

    def write_person(self,count):
        if count != 0:
            self.doc.page_break()
        self.slist = []
        
        media_list = self.start_person.get_media_list()
        name = self.start_person.get_primary_name().get_regular_name()
        mark = ReportUtils.get_person_mark(self.database,self.start_person)
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(_("Summary of %s") % name,mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        if len(media_list) > 0:
            object_handle = media_list[0].get_reference_handle()
            object = self.database.get_object_from_handle(object_handle)
            mime_type = object.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                file = object.get_path()
                self.doc.start_paragraph("IDS-Normal")
                self.doc.add_media_object(file,"row",4.0,4.0)
                self.doc.end_paragraph()

        self.doc.start_table("one","IDS-IndTable")

        self.doc.start_row()
        self.normal_cell("%s:" % _("Name"))
        name = self.start_person.get_primary_name()
        text = name.get_regular_name()
        mark = ReportUtils.get_person_mark(self.database, self.start_person)
        if self.use_srcs:
            for s in name.get_source_references():
                self.slist.append(s)
                src_handle = s.get_reference_handle()
                src = self.database.get_source_from_handle(src_handle)
                text = "%s [%s]" % (text,src.get_gramps_id())
        self.normal_cell(text,mark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Gender"))
        if self.start_person.get_gender() == RelLib.Person.MALE:
            self.normal_cell(_("Male"))
        else:
            self.normal_cell(_("Female"))
        self.doc.end_row()

        family_handle = self.start_person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_inst_id = family.get_father_handle()
            if father_inst_id:
                father_inst = self.database.get_person_from_handle(
                    father_inst_id)
                father = father_inst.get_primary_name().get_regular_name()
                fmark = ReportUtils.get_person_mark(self.database,father_inst)
            else:
                father = ""
                fmark = None
            mother_inst_id = family.get_mother_handle()
            if mother_inst_id:
                mother_inst = self.database.get_person_from_handle(
                    mother_inst_id) 
                mother = mother_inst.get_primary_name().get_regular_name()
                mmark = ReportUtils.get_person_mark(self.database,mother_inst)
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
        self.normal_cell(father,fmark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Mother"))
        self.normal_cell(mother,mmark)
        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        self.write_alt_names()
        self.write_facts()
        self.write_alt_parents()
        self.write_families()
        self.write_note()
        self.write_sources()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndivCompleteOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'cites'    : 1,
        }
        self.options_help = {
            'cites'    : ("=0/1","Whether to cite sources.",
                            ["Do not cite sources","Cite sources"],
                            True),
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }

    def get_report_filters(self,person):
        """Set up the list of possible content filters."""
        if person:
            name = person.get_primary_name().get_name()
            gramps_id = person.get_gramps_id()
        else:
            name = 'PERSON'
            gramps_id = ''

        filt_id = GenericFilter()
        filt_id.set_name(name)
        filt_id.add_rule(Rules.Person.HasIdOf([gramps_id]))

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        des = GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(Rules.Person.IsDescendantOf([gramps_id,1]))

        ans = GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(Rules.Person.IsAncestorOf([gramps_id,1]))

        com = GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(Rules.Person.HasCommonAncestorWith([gramps_id]))

        return [filt_id,all,des,ans,com]

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        
        self.use_srcs = gtk.CheckButton(_('Include Source Information'))
        self.use_srcs.set_active(self.options_dict['cites'])
        dialog.add_option('',self.use_srcs)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['cites'] = int(self.use_srcs.get_active ())

    def make_default_style(self,default_style):
        """Make the default output style for the Individual Complete Report."""
        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(16)
        p = BaseDoc.ParagraphStyle()
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_top_margin(ReportUtils.pt2cm(8))
        p.set_bottom_margin(ReportUtils.pt2cm(8))
        p.set_font(font)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_style("IDS-Title",p)
    
        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_("The style used for category labels."))
        default_style.add_style("IDS-TableTitle",p)

        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_("The style used for the spouse's name."))
        default_style.add_style("IDS-Spouse",p)

        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("IDS-Normal",p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'indiv_complete',
    category = CATEGORY_TEXT,
    report_class = IndivCompleteReport,
    options_class = IndivCompleteOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Complete Individual Report"),
    status=(_("Stable")),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org",
    description=_("Produces a complete report on the selected people."),
    )
