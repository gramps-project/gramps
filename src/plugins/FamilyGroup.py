#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Generate files/Family Group Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os

import gtk
#------------------------------------------------------------------------
#
# GRAMPS 
#
#------------------------------------------------------------------------
import RelLib
import Report
import BaseDoc
import Errors
import Utils
from gettext import gettext as _
from QuestionDialog import ErrorDialog

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup:

    def __init__(self,database,family_handle,doc,output,newpage=0):
        self.db = database
        
        if family_handle:
            self.family = self.db.find_family_from_handle(family_handle)
        else:
            self.family = None
        self.output = output
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0

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

    def end(self):
        if self.standalone:
            self.doc.close()
    
    def dump_parent(self,person_handle):

        if not person_handle:
            return
        
        person = self.db.get_person_from_handle(person_handle)
        
        if person.get_gender() == RelLib.Person.male:
            id = _("Husband")
        else:
            id = _("Wife")
        
        self.doc.start_table(id,'FGR-ParentTable')
        self.doc.start_row()
        self.doc.start_cell('FGR-ParentHead',3)
        self.doc.start_paragraph('FGR-ParentName')
        self.doc.write_text(id + ': ')
        self.doc.write_text(person.get_primary_name().get_regular_name())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        birth_handle = person.get_birth_handle()
        bdate = ""
        bplace = ""
        if birth_handle:
            birth = self.db.find_event_from_handle(birth_handle)
            bdate = birth.get_date()
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                bplace = self.db.get_place_from_handle(bplace_handle).get_title()
        
        death_handle = person.get_death_handle()
        ddate = ""
        dplace = ""
        if death_handle:
            death = self.db.find_event_from_handle(death_handle)
            ddate = death.get_date()
            dplace_handle = death.get_place_handle()
            if dplace_handle:
                dplace = self.db.get_place_from_handle(dplace_handle).get_title()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(bdate)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(bplace)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(ddate)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(dplace)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        family_handle = person.get_main_parents_family_handle()
        father_name = ""
        mother_name = ""
        if family_handle:
            family = self.db.find_family_from_handle(family_handle)
            father_handle = family.get_father_handle() 
            if father_handle:
                father_name = self.db.get_person_from_handle(father_handle).get_primary_name().get_regular_name()
            mother_handle = family.get_mother_handle() 
            if mother_handle:
                mother_name = self.db.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd",2)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(father_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd",2)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(mother_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.end_table()

    def dump_child_event(self,text,name,event):
        date = ""
        place = ""
        if event:
            date = event.get_date()
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.db.get_place_from_handle(place_handle).get_title()

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

        person = self.db.get_person_from_handle(person_handle)
        self.doc.start_row()
        self.doc.start_cell('FGR-TextChild1')
        self.doc.start_paragraph('FGR-ChildText')
        if person.get_gender() == RelLib.Person.male:
            self.doc.write_text("%dM" % index)
        else:
            self.doc.write_text("%dF" % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-ChildName',3)
        self.doc.start_paragraph('FGR-ChildText')
        self.doc.write_text(person.get_primary_name().get_regular_name())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        families = len(person.get_family_handle_list())
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self.db.find_event_from_handle(birth_handle)
        else:
            birth = None
        death_handle = person.get_death_handle()
        if death_handle:
            death = self.db.find_event_from_handle(death_handle)
        else:
            death = None
        self.dump_child_event('FGR-TextChild1',_('Birth'),birth)
        if families == 0:
            self.dump_child_event('FGR-TextChild2',_('Death'),death)
        else:
            self.dump_child_event('FGR-TextChild1',_('Death'),death)
            
        index = 1
        for family_handle in person.get_family_handle_list():
            family = self.db.find_family_from_handle(family_handle)
            for event_handle in family.get_event_list():
                if event_handle:
                    event = self.db.find_event_from_handle(event_handle)
                    if event.get_name() == "Marriage":
                        m = event
                        break
            else:
                m = None

            if person_handle == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
            self.doc.start_row()
            self.doc.start_cell('FGR-TextChild1')
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
            if spouse_id:
                spouse = self.db.get_person_from_handle(spouse_id)
                self.doc.write_text(spouse.get_primary_name().get_regular_name())
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if index == families:
                self.dump_child_event('FGR-TextChild2',_("Married"),m)
            else:
                self.dump_child_event('FGR-TextChild1',_("Married"),m)
            
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        if self.newpage:
            self.doc.page_break()

        self.doc.start_paragraph('FGR-Title')
        self.doc.write_text(_("Family Group Report"))
        self.doc.end_paragraph()

        if self.family:
            self.dump_parent(self.family.get_father_handle())
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()
            self.dump_parent(self.family.get_mother_handle())

            length = len(self.family.get_child_handle_list())
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
                for child_handle in self.family.get_child_handle_list():
                    self.dump_child(index,child_handle)
                    index = index + 1
                self.doc.end_table()
        self.end()


#------------------------------------------------------------------------
#
# FamilyGroupDialog
#
#------------------------------------------------------------------------
class FamilyGroupDialog(Report.TextReportDialog):

    report_options = {}

    def __init__(self,database,person):
        self.db = database
        Report.TextReportDialog.__init__(self,database,person,self.report_options)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Family Group Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Family Group Report for %s") % name
    
    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Family Group Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "family_group.xml"

    def doc_uses_tables(self):
        """This report requires table support."""
        return 1

    def get_report_generations(self):
        """No generation options."""
        return (0, 0)
    
    def get_report_extra_menu_info(self):
        spouse_map = _build_spouse_map(self.db,self.person)
        return (_("Spouse"), spouse_map, None, None)

    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = FamilyGroup(self.db, self.report_menu, 
                self.doc, self.target_path)
            MyReport.write_report()
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Standalone report function
#
#------------------------------------------------------------------------
def report(database,person):
    FamilyGroupDialog(database,person)
    
#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "family_group.xml"
_style_name = "default" 

_person_handle = ""
_spouse_name = ""
_options = ( _person_handle, _spouse_name )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class FamilyGroupBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person_from_handle(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.spouse_name = self.options[1]

        self.new_person = None

        self.spouse_map = _build_spouse_map(self.db,self.person)
        if self.extra_menu:
            myMenu = Utils.build_string_optmenu(self.spouse_map,self.spouse_name)
            self.extra_menu.set_menu(myMenu)
            self.extra_menu.set_sensitive(len(self.spouse_map) > 1)
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Family Group Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Family Group Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """No generation options."""
        return (0, 0)

    def doc_uses_tables(self):
        """This report requires table support."""
        return 1

    def get_report_extra_menu_info(self):
        self.spouse_map = _build_spouse_map(self.db,self.person)
        return (_("Spouse"), self.spouse_map, None, None)

    def on_center_person_change_clicked(self,obj):
        import SelectPerson
        sel_person = SelectPerson.SelectPerson(self.db,_('Select Person'))
        new_person = sel_person.run()
        if new_person:
            self.new_person = new_person
            self.new_spouse_map = _build_spouse_map(self.db,self.new_person)

            if self.new_spouse_map:
                if not self.extra_menu:
                    old_person = self.person
                    self.person = self.new_person
                    self.setup_report_options_frame()
                    self.window.show_all()
                    self.person = old_person
                myMenu = Utils.build_string_optmenu(self.new_spouse_map,None)
                self.extra_menu.set_menu(myMenu)
                self.extra_menu.set_sensitive(len(self.new_spouse_map) > 1)
            else:
                if self.extra_menu:
                    myMenu = Utils.build_string_optmenu(self.new_spouse_map,None)
                    self.extra_menu.set_menu(myMenu)
                    self.extra_menu.set_sensitive(gtk.FALSE)
                    self.window.show_all()
                    self.extra_menu = None

            new_name = new_person.get_primary_name().get_regular_name()
            if new_name:
                self.person_label.set_text( "<i>%s</i>" % new_name )
                self.person_label.set_use_markup(gtk.TRUE)

            
    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        if self.new_person:
            self.person = self.new_person
            self.spouse_map = self.new_spouse_map

        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.spouse_map:
            spouse_number = self.extra_menu.get_history()
            spouse_names = self.spouse_map.keys()
            spouse_names.sort()
            self.spouse_name = spouse_names[spouse_number]
        else:
            self.spouse_name = ""
            
        self.options = ( self.person.get_handle(), self.spouse_name )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Family Group Report using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person_from_handle(options[0])
        spouse_name = options[1]
        spouse_map = _build_spouse_map(database,person)
        if spouse_map:
            if spouse_map.has_key(spouse_name):
                family = spouse_map[spouse_name]
            else:
                spouse_names = spouse_map.keys()
                spouse_names.sort()
                family = spouse_map[spouse_names[0]]
        else:
            family = None
        return FamilyGroup(database, family, doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()


#------------------------------------------------------------------------
#
# Functions shared between the dialogs
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
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

def _build_spouse_map(database,person):
    """Create a mapping of all spouse names:families to be put
    into the 'extra' option menu in the report options box.  If
    the selected person has never been married then this routine
    will return a placebo label and disable the OK button."""
    spouse_map = {}
    family_list = person.get_family_handle_list()
    for family_handle in family_list:
        family = database.find_family_from_handle(family_handle)
        if person.get_handle() == family.get_father_handle():
            spouse_id = family.get_mother_handle()
        else:
            spouse_id = family.get_father_handle()
        if spouse_id:
            spouse = database.get_person_from_handle(spouse_id)
            name = spouse.get_primary_name().get_name()
        else:
            name= _("unknown")
        spouse_map[name] = family_handle
    return spouse_map

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Family Group Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description=_("Creates a family group report, showing information on a set of parents and their children."),
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Family Group Report"), 
    _("Text"),
    FamilyGroupBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
