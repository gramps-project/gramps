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

"Generate files/Ahnentafel Chart"

import RelLib
import const
import os
import re
import sort
import string
import utils

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
class AncestorReport:

    gen = {
        1 : "First",
        2 : "Second",
        3 : "Third",
        4 : "Fourth",
        5 : "Fifth",
        6 : "Sixth",
        7 : "Seventh",
        8 : "Eighth",
        9 : "Ninth",
        10: "Tenth",
        11: "Eleventh",
        12: "Twelfth",
        13: "Thirteenth",
        14: "Fourteenth",
        15: "Fifteenth",
        16: "Sixteenth",
        17: "Seventeenth",
        18: "Eigthteenth",
        19: "Nineteenth",
        20: "Twentieth",
        21: "Twenty-first",
        22: "Twenty-second",
        23: "Twenty-third",
        24: "Twenty-fourth",
        25: "Twenty-fifth",
        26: "Twenty-sixth",
        27: "Twenty-seventh",
        28: "Twenty-eighth",
        29: "Twenty-ninth"
        }

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,max,pgbrk,doc):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        self.doc.add_style("Title",para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(14)
        font.set_bold(1)
        font.set_italic(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        self.doc.add_style("Header",para)

        para = ParagraphStyle()
        para.set_first_indent(-0.75)
        para.set_left_margin(1.0)
        self.doc.add_style("ListEntry",para)
        self.doc.open(output)
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def filter(self,person,index):
        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person
    
        family = person.getMainFamily()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):

        self.filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("Title")
        self.doc.write_text("Ahnentafel Chart for " + name)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        generation = 0
        need_header = 1

        for key in keys :
            if generation == 0 or key >= 2**generation:
                self.doc.start_paragraph("Header")
                self.doc.write_text(AncestorReport.gen[generation+1 ]+ " Generation")
                self.doc.end_paragraph()
                generation = generation + 1

            self.doc.start_paragraph("ListEntry")
            person = self.map[key]
            name = person.getPrimaryName().getRegularName()
        
            self.doc.write_text(str(key) + ".\t" + name )

            # Check birth record
        
            birth = person.getBirth()
            if birth:
                date = birth.getDateObj().get_start_date()
                place = birth.getPlace()
                if date.getDate() != "" or place != "":
                    self.doc.write_text(" was born")
                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            self.doc.write_text(" on ")
                        else:
                            self.doc.write_text(" in ")
                        self.doc.write_text(date.getDate())
                if place != "":
                    self.doc.write_text(" in " + place)
                if place == "" or place[-1] != '.':
                    self.doc.write_text(".")
                self.doc.write_text("\n")
            else:
                self.doc.write_text(".\n")

            death = person.getDeath()
            buried = None
            for event in person.getEventList():
                if string.lower(event.getName()) == "burial":
                    buried = event
        
            if death:
                date = death.getDateObj().get_start_date()
                place = death.getPlace()
                if date.getDate() != "" or place != "":
                    if person.getGender() == RelLib.Person.male:
                        self.doc.write_text("He")
                    else:
                        self.doc.write_text("She")
                    self.doc.write_text(" died")

                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            self.doc.write_text(" on ")
                        else:
                            self.doc.write_text(" in ")
                        self.doc.write_text(date.getDate())
                    if place != "":
                        self.doc.write_text(" in " + place)
                    if buried:
                        date = buried.getDateObj().get_start_date()
                        place = buried.getPlace()
                        if date.getDate() != "" or place != "":
                            self.doc.write_text(", and was buried")

                            if date.getDate() != "":
                                if date.getDay() != -1 and date.getMonth() != -1:
                                    self.doc.write_text(" on ")
                                else:
                                    self.doc.write_text(" in ")
                                self.doc.write_text(date.getDate())
                            if place != "":
                                self.doc.write_text(" in " + place)
                    
                    if place == "" or place[-1] != '.':
                        self.doc.write_text(".")
                    self.doc.write_text("\n")
            else:
                self.doc.write_text(".\n")

            self.doc.end_paragraph()

        self.doc.close()
 

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
    glade_file = base + os.sep + "ancestorreport.glade"
    topDialog = GladeXML(glade_file,"dialog1")
    topDialog.get_widget("htmltemplate").set_sensitive(0)

    name = person.getPrimaryName().getRegularName()

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))

    topDialog.get_widget("labelTitle").set_text("Ahnentafel Report for " + name)
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
    if obj.get_active():
        topDialog.get_widget("htmltemplate").set_sensitive(1)
        topDialog.get_widget("papersize").set_sensitive(0)
        topDialog.get_widget("orientation").set_sensitive(0)
    else:    
        topDialog.get_widget("htmltemplate").set_sensitive(0)
        topDialog.get_widget("papersize").set_sensitive(1)
        topDialog.get_widget("orientation").set_sensitive(1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_save_clicked(obj):
    global active_person
    global db

    outputName = topDialog.get_widget("filename").get_text()
    max_gen = topDialog.get_widget("generations").get_value_as_int()
    pgbrk = topDialog.get_widget("pagebreak").get_active()
    template = topDialog.get_widget("htmltemplate").get_full_path(0)
    paper_obj = topDialog.get_widget("papersize").get_menu().get_active()
    paper = paper_obj.get_data("i")
    orien_obj = topDialog.get_widget("orientation").get_menu().get_active()
    orien = orien_obj.get_data("i")
    
    if outputName == "":
        return

    if topDialog.get_widget("openoffice").get_active():
        document = OpenOfficeDoc(paper,orien)
    elif topDialog.get_widget("abiword").get_active():
        document = AbiWordDoc(paper,orien)
    else:
        document = HtmlDoc(template)

    MyReport = AncestorReport(db,active_person,outputName,\
                              max_gen, pgbrk, document)
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Produces a textual ancestral report"

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 4 1",
        " 	c None",
        ".	c #FFFFFF",
        "+	c #C0C0C0",
        "@	c #000000",
        "                                                ",
        "                                                ",
        "                                                ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]







