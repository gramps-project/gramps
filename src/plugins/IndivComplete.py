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
from Filters import GenericFilter, Rules
import DateHandler
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
from ReportBase import Bibliography, Endnotes
from BasicUtils import name_displayer as _nd
from QuestionDialog import WarningDialog

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

        filter_num = options_class.handler.options_dict['filter']
        filters = ReportUtils.get_person_filters(person)
        self.filter = filters[filter_num]
        self.bibli = None

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
        if description:
            text = '%s%s. ' % (text,description)
        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli,event)

        self.doc.start_row()
        self.normal_cell(name)
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()
        
        for notehandle in event.get_note_list():
            note = self.database.get_note_from_handle(notehandle)
            text = note.get()
            format = note.get_format()
            self.doc.write_note(text,format,'IDS-Normal')
        
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
        notelist = self.start_person.get_note_list()
        if not notelist:
            return
        self.doc.start_table('note','IDS-IndTable')
        self.doc.start_row()
        self.doc.start_cell('IDS-TableHead',2)
        self.doc.start_paragraph('IDS-TableTitle')
        self.doc.write_text(_('Notes'))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        for notehandle in notelist:
            note = self.database.get_note_from_handle(notehandle)
            text = note.get()
            format = note.get_format()
            self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell',2)
            self.doc.write_note(text,format,'IDS-Normal')
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
                fname = _nd.display(father)
                mark = ReportUtils.get_person_mark(self.database,father)
                self.write_p_entry(_('Father'),fname,frel,mark)
            else:
                self.write_p_entry(_('Father'),'','')

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mname = _nd.display(mother)
                mark = ReportUtils.get_person_mark(self.database,mother)
                self.write_p_entry(_('Mother'),mname,mrel,mark)
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
            name_type = str( name.get_type() )
            self.doc.start_row()
            self.normal_cell(name_type)
            text = _nd.display_name(name)
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli,name)
            self.normal_cell(text,endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()
        
    def write_addresses(self):
        
        alist = self.start_person.get_address_list()

        if len(alist) == 0:
            return
        
        self.doc.start_table("addresses","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Addresses"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        for addr in alist:
            text = ReportUtils.get_address_str(addr)
            date = DateHandler.get_date(addr)
            endnotes = ""
            if self.use_srcs:
                endnotes = Endnotes.cite_source(self.bibli,addr)
            self.doc.start_row()
            self.normal_cell(date)
            self.normal_cell(text,endnotes)
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
                text = _nd.display(spouse)
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

                for child_ref in child_ref_list:
                    self.doc.start_paragraph("IDS-Normal")
                    child = self.database.get_person_from_handle(child_ref.ref)
                    name = _nd.display(child)
                    mark = ReportUtils.get_person_mark(self.database,child)
                    self.doc.write_text(name,mark)
                    self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_sources(self):
        keys = self.sref_map.keys()
        if not keys:
            return
        
        self.doc.start_table("three","IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead",2)
        self.doc.start_paragraph("IDS-TableTitle")
        self.doc.write_text(_("Sources"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        keys.sort()
        for key in keys:
            srcref = self.sref_map[key]
            base = self.database.get_source_from_handle(
                srcref.get_reference_handle())
            self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell',2)
            self.doc.start_paragraph("IDS-Normal","%d." % key)
            self.doc.write_text(base.get_title())
            self.doc.end_paragraph()
            self.doc.end_cell()
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

        event_ref_list = self.start_person.get_primary_event_ref_list()
        for event_ref in event_ref_list:
            if event_ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                self.write_fact(event)
        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def normal_cell(self,text,endnotes=None,mark=None):
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(text,mark)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
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
        self.bibli = Bibliography(Bibliography.MODE_PAGE)
        
        media_list = self.start_person.get_media_list()
        name = _nd.display(self.start_person)
        title = _("Summary of %s") % name
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        if len(media_list) > 0:
            object_handle = media_list[0].get_reference_handle()
            object = self.database.get_object_from_handle(object_handle)
            mime_type = object.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                filename = object.get_path()
                if os.path.exists(filename):
                    self.doc.start_paragraph("IDS-Normal")
                    self.doc.add_media_object(filename, "center", 4.0, 4.0)
                    self.doc.end_paragraph()
                else:
                    WarningDialog(_("Could not add photo to page"),
                          "%s: %s" % (filename, _('File does not exist')))

        self.doc.start_table("one","IDS-IndTable")

        self.doc.start_row()
        self.normal_cell("%s:" % _("Name"))
        name = self.start_person.get_primary_name()
        text = _nd.display_name(name)
        mark = ReportUtils.get_person_mark(self.database, self.start_person)
        endnotes = ""
        if self.use_srcs:
            endnotes = Endnotes.cite_source(self.bibli,name)
        self.normal_cell(text,endnotes,mark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Gender"))
        if self.start_person.get_gender() == RelLib.Person.MALE:
            self.normal_cell(_("Male"))
        elif self.start_person.get_gender() == RelLib.Person.FEMALE:
            self.normal_cell(_("Female"))
        else:
            self.normal_cell(_("Unknown"))
        self.doc.end_row()

        family_handle = self.start_person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_inst_id = family.get_father_handle()
            if father_inst_id:
                father_inst = self.database.get_person_from_handle(
                    father_inst_id)
                father = _nd.display(father_inst)
                fmark = ReportUtils.get_person_mark(self.database,father_inst)
            else:
                father = ""
                fmark = None
            mother_inst_id = family.get_mother_handle()
            if mother_inst_id:
                mother_inst = self.database.get_person_from_handle(
                    mother_inst_id) 
                mother = _nd.display(mother_inst)
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
        self.normal_cell(father,mark=fmark)
        self.doc.end_row()

        self.doc.start_row()
        self.normal_cell("%s:" % _("Mother"))
        self.normal_cell(mother,mark=mmark)
        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        self.write_alt_names()
        self.write_facts()
        self.write_alt_parents()
        self.write_families()
        self.write_addresses()
        self.write_note()
        if self.use_srcs:
            Endnotes.write_endnotes(self.bibli,self.database,self.doc)

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
            'filter'   : 0,
            'cites'    : 1,
        }
        filters = ReportUtils.get_person_filters(None)
        self.options_help = {
            'filter'   : ("=num","Filter number.",
                          [ filt.get_name() for filt in filters ],
                          True ),
            'cites'    : ("=0/1","Whether to cite sources.",
                          ["Do not cite sources","Cite sources"],
                          True),
        }

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        filter_index = self.options_dict['filter']
        filter_list = ReportUtils.get_person_filters(dialog.person)
        self.filter_menu = gtk.combo_box_new_text()
        for filter in filter_list:
            self.filter_menu.append_text(filter.get_name())
        if filter_index > len(filter_list):
            filter_index = 0
        self.filter_menu.set_active(filter_index)
        dialog.add_option('Filter',self.filter_menu)

        self.use_srcs = gtk.CheckButton(_('Include Source Information'))
        self.use_srcs.set_active(self.options_dict['cites'])
        dialog.add_option('',self.use_srcs)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['filter'] = int(self.filter_menu.get_active())
        self.options_dict['cites'] = int(self.use_srcs.get_active())

    def make_default_style(self,default_style):
        """Make the default output style for the Individual Complete Report."""
        # Paragraph Styles
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
        default_style.add_paragraph_style("IDS-Title",p)
    
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
        default_style.add_paragraph_style("IDS-TableTitle",p)

        font = BaseDoc.FontStyle()
        font.set_bold(1)
        font.set_type_face(BaseDoc.FONT_SANS_SERIF)
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_("The style used for the spouse's name."))
        default_style.add_paragraph_style("IDS-Spouse",p)

        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("IDS-Normal",p)
        
        # Table Styles
        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,80)
        default_style.add_table_style("IDS-IndTable",tbl)

        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,50)
        tbl.set_column_width(1,50)
        default_style.add_table_style("IDS-ParentsTable",tbl)

        cell = BaseDoc.TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        default_style.add_cell_style("IDS-TableHead",cell)

        cell = BaseDoc.TableCellStyle()
        default_style.add_cell_style("IDS-NormalCell",cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_longlist(1)
        default_style.add_cell_style("IDS-ListCell",cell)
        
        Endnotes.add_endnote_styles(default_style)

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
