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

"Generate files/Individual Summary"

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
from AbiWordDoc import *

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
class IndivSummary:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,document):
        self.d = document
        
        c = database.getResearcher().getName()
        self.d.creator(c)
        self.map = {}
        self.database = database
        self.person = person
        self.output = output
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        p = ParagraphStyle()
        p.set_alignment(PARA_ALIGN_CENTER)
        p.set_font(font)
        self.d.add_style("Title",p)

        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        p = ParagraphStyle()
        p.set_font(font)
        self.d.add_style("TableTitle",p)

        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
        self.d.add_style("Spouse",p)

        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
        self.d.add_style("Normal",p)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,80)
        self.d.add_table_style("IndTable",tbl)

        cell = TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        self.d.add_cell_style("TableHead",cell)

        cell = TableCellStyle()
        self.d.add_cell_style("NormalCell",cell)

        self.d.open(self.output)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.d.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_fact(self,event):
        if event == None:
            return
        name = event.getName()
        date = event.getDate()
        place = event.getPlace()
        description = event.getDescription()
        if date == "":
            if place == "":
                return
            else:
                val = place + ". " + description
        else:
            if place == "":
                val = date + ". " + description
            else:
                val = date + " in " + place + ". " +  description

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(name)
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(val)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()
        self.d.start_table("three","IndTable")
        self.d.start_row()
        self.d.start_cell("TableHead",2)
        self.d.start_paragraph("TableTitle")
        self.d.write_text("Marriages/Children")
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        
        for family in self.person.getFamilyList():
            if self.person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.d.start_row()
            self.d.start_cell("NormalCell",2)
            self.d.start_paragraph("Spouse")
            self.d.write_text(spouse.getPrimaryName().getRegularName())
            self.d.end_paragraph()
            self.d.end_cell()
            self.d.end_row()
            
            event_list = [ family.getMarriage(), family.getDivorce() ]
            event_list = event_list + family.getEventList()
            for event in event_list:
                self.write_fact(event)

            child_list = family.getChildList()
            if len(child_list) > 0:
                self.d.start_row()
                self.d.start_cell("NormalCell")
                self.d.start_paragraph("Normal")
                self.d.write_text("Children")
                self.d.end_paragraph()
                self.d.end_cell()

                self.d.start_cell("NormalCell")
                self.d.start_paragraph("Normal")
                
                first = 1
                for child in family.getChildList():
                    if first == 1:
                        first = 0
                    else:
                        self.d.write_text('\n')
                    self.d.write_text(child.getPrimaryName().getRegularName())
                self.d.end_paragraph()
                self.d.end_cell()
                self.d.end_row()
        self.d.end_table()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        photo_list = self.person.getPhotoList()
            
        self.d.start_paragraph("Title")
        self.d.write_text('Summary of ')
        self.d.write_text(self.person.getPrimaryName().getRegularName())
        self.d.end_paragraph()

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()

        if len(photo_list) > 0:
            file = photo_list[0].getPath()
            self.d.start_paragraph("Normal")
            self.d.add_photo(file,300,300)
            self.d.end_paragraph()

        self.d.start_table("one","IndTable")

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("Name:")
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(self.person.getPrimaryName().getRegularName())
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("Gender:")
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        if self.person.getGender() == RelLib.Person.male:
            self.d.write_text("Male")
        else:
            self.d.write_text("Female")
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        family = self.person.getMainFamily()
        if family:
            father = family.getFather().getPrimaryName().getRegularName()
            mother = family.getMother().getPrimaryName().getRegularName()
        else:
            father = ""
            mother = ""

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("Father:")
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(father)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("Mother:")
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(mother)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        self.d.end_table()

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()
        
        self.d.start_table("two","IndTable")
        self.d.start_row()
        self.d.start_cell("TableHead",2)
        self.d.start_paragraph("TableTitle")
        self.d.write_text("Individual Facts")
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        event_list = [ self.person.getBirth(), self.person.getDeath() ]
        event_list = event_list + self.person.getEventList()
        for event in event_list:
            self.write_fact(event)
        self.d.end_table()

        self.write_families()
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
    glade_file = base + os.sep + "indsum.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()
    label = topDialog.get_widget("labelTitle")
    
    label.set_text("Individual Summary for " + name)

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))

    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked,
        "on_html_toggled" : on_html_toggled
        })

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

    paper_obj = topDialog.get_widget("papersize")
    paper = paper_obj.get_menu().get_active().get_data("i")
    orien_obj = topDialog.get_widget("orientation")
    orien = orien_obj.get_menu().get_active().get_data("i")

    if topDialog.get_widget("html").get_active():
        template = topDialog.get_widget("htmlfile").get_text()
        doc = HtmlDoc(template)
    else:
        doc = OpenOfficeDoc(paper,orien)

    MyReport = IndivSummary(db,active_person,outputName,doc)

    MyReport.setup()
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Creates a family group report, showing information on ") +\
           _("a set of parents and their children.")









