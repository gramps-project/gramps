#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Generate files/Family Group Report"

import RelLib
import const
import os
import re
import sort
import string
import utils
import intl

_ = intl.gettext

from TextDoc import *
from OpenOfficeDoc import *
from HtmlDoc import *
try:
    import reportlab.platypus.tables
    from PdfDoc import *
    no_pdf = 0
except:
    no_pdf = 1

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
active_person = None
db = None

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FamilyGroup:

    def __init__(self,database,family,output,doc):
        self.db = database
        self.family = family
        self.output = output
        self.doc = doc

        para = ParagraphStyle()
        font = FontStyle()
        font.set_size(4)
        para.set_font(font)
        self.doc.add_style('blank',para)
        
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.doc.add_style('Title',para)

        font = FontStyle()
        font.set_type_face(FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para = ParagraphStyle()
        para.set_font(font)
        self.doc.add_style('Normal',para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.doc.add_style('ChildText',para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.doc.add_style('ParentName',para)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('ParentHead',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('TextContents',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('TextChild1',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('TextChild2',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('TextContentsEnd',cell)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('ChildName',cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,20)
        table.set_column_width(1,40)
        table.set_column_width(2,40)
        self.doc.add_table_style('ParentTable',table)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,5)
        table.set_column_width(1,15)
        table.set_column_width(2,40)
        table.set_column_width(3,40)
        self.doc.add_table_style('ChildTable',table)

    def setup(self):
        self.doc.open(self.output)
        self.doc.start_paragraph('Title')
        self.doc.write_text(_("Family Group Record"))
        self.doc.end_paragraph()
    
    def end(self):
        self.doc.close()
    
    def dump_parent(self,person):

        if person.getGender() == RelLib.Person.male:
            id = "Husband"
        else:
            id = "Wife"
        
        self.doc.start_table(id,'ParentTable')
        self.doc.start_row()
        self.doc.start_cell('ParentHead',3)
        self.doc.start_paragraph('ParentName')
        self.doc.write_text(id + ': ')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        birth = person.getBirth()
        death = person.getDeath()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(birth.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(birth.getPlace())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(death.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(death.getPlace())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        family = person.getMainFamily()
        if family == None or family.getFather() == None:
            father_name = ""
        else:
            father_name = family.getFather().getPrimaryName().getRegularName()
        if family == None or family.getMother() == None:
            mother_name = ""
        else:
            mother_name = family.getMother().getPrimaryName().getRegularName()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd",2)
        self.doc.start_paragraph('Normal')
        self.doc.write_text(father_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd",2)
        self.doc.start_paragraph('Normal')
        self.doc.write_text(mother_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.end_table()

    def dump_child_event(self,text,name,event):
        if event:
            date = event.getDate()
            place = event.getPlace()
        else:
            date = ""
            place = ""
        self.doc.start_row()
        self.doc.start_cell(text)
        self.doc.start_paragraph('Normal')
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContents')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContents')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(date)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContentsEnd')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(place)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    def dump_child(self,index,person):

        self.doc.start_row()
        self.doc.start_cell('TextChild1')
        self.doc.start_paragraph('ChildText')
        if person.getGender() == RelLib.Person.male:
            self.doc.write_text("%dM" % index)
        else:
            self.doc.write_text("%dF" % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('ChildName',3)
        self.doc.start_paragraph('ChildText')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        families = len(person.getFamilyList())
        self.dump_child_event('TextChild1','Birth',person.getBirth())
        if families == 0:
            self.dump_child_event('TextChild2','Death',person.getDeath())
        else:
            self.dump_child_event('TextChild1','Death',person.getDeath())
            
        index = 1
        for family in person.getFamilyList():
            m = family.getMarriage()
            if person == family.getFather():
                spouse =family.getMother()
            else:
                spouse = family.getFather()
            self.doc.start_row()
            self.doc.start_cell('TextChild1')
            self.doc.start_paragraph('Normal')
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('TextContents')
            self.doc.start_paragraph('Normal')
            self.doc.write_text(_("Spouse"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('TextContentsEnd',2)
            self.doc.start_paragraph('Normal')
            self.doc.write_text(spouse.getPrimaryName().getRegularName())
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if index == families:
                self.dump_child_event('TextChild2',_("Married"),m)
            else:
                self.dump_child_event('TextChild1',_("Married"),m)
            
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        self.dump_parent(self.family.getFather())
        self.doc.start_paragraph("blank")
        self.doc.end_paragraph()
        self.dump_parent(self.family.getMother())

        length = len(self.family.getChildList())
        if length > 0:
            self.doc.start_paragraph("blank")
            self.doc.end_paragraph()
            self.doc.start_table('Children','ChildTable')
            self.doc.start_row()
            self.doc.start_cell('ParentHead',4)
            self.doc.start_paragraph('ParentName')
            self.doc.write_text(_("Children"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            index = 1
            for child in self.family.getChildList():
                self.dump_child(index,child)
                index = index + 1
            self.doc.end_table()
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    import PaperMenu
    
    global active_person
    global topDialog
    global glade_file
    global db
    
    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "familygroup.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()
    family_list = person.getFamilyList()
    label = topDialog.get_widget("labelTitle")
    
    if no_pdf == 1:
        topDialog.get_widget("pdf").set_sensitive(0)
    
    label.set_text(_("Family Group chart for %s") % name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked,
        "on_html_toggled" : on_html_toggled
        })

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))

    frame = topDialog.get_widget("spouse")
    option_menu = topDialog.get_widget("spouse_menu")

    if len(family_list) > 1:
        frame.show()
    else:
        frame.hide()

    my_menu = GtkMenu()
    for family in family_list:
        if person == family.getFather():
            spouse = family.getMother()
        else:
            spouse = family.getFather()
        item = GtkMenuItem(spouse.getPrimaryName().getName())
        item.set_data("f",family)
        item.show()
        my_menu.append(item)
    option_menu.set_menu(my_menu)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_html_toggled(obj):
    topDialog.get_widget("htmltemplate").set_sensitive(obj.get_active())

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_save_clicked(obj):
    global active_person
    global db

    outputName = topDialog.get_widget("fileentry1").get_full_path(0)
    if outputName == "":
        return

    menu = topDialog.get_widget("spouse_menu").get_menu()
    family = menu.get_active().get_data("f")
    paper_obj = topDialog.get_widget("papersize")
    paper = paper_obj.get_menu().get_active().get_data("i")
    orien_obj = topDialog.get_widget("orientation")
    orien = orien_obj.get_menu().get_active().get_data("i")

    if topDialog.get_widget("html").get_active():
        template = topDialog.get_widget("htmlfile").get_text()
        doc = HtmlDoc(template)
    elif topDialog.get_widget("openoffice").get_active():
        doc = OpenOfficeDoc(paper,orien)
    else:
        doc = PdfDoc(paper,orien)

    MyReport = FamilyGroup(db,family,outputName,doc)

    MyReport.setup()
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Creates a family group report, showing information on a set of parents and their children.")

def get_name():
    return _("Generate files/Family Group Report")








