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

"Generate files/Ahnentafel Report"

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
import FindDoc

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
        1 : _("First"),
        2 : _("Second"),
        3 : _("Third"),
        4 : _("Fourth"),
        5 : _("Fifth"),
        6 : _("Sixth"),
        7 : _("Seventh"),
        8 : _("Eighth"),
        9 : _("Ninth"),
        10: _("Tenth"),
        11: _("Eleventh"),
        12: _("Twelfth"),
        13: _("Thirteenth"),
        14: _("Fourteenth"),
        15: _("Fifteenth"),
        16: _("Sixteenth"),
        17: _("Seventeenth"),
        18: _("Eightteenth"),
        19: _("Nineteenth"),
        20: _("Twentieth"),
        21: _("Twenty-first"),
        22: _("Twenty-second"),
        23: _("Twenty-third"),
        24: _("Twenty-fourth"),
        25: _("Twenty-fifth"),
        26: _("Twenty-sixth"),
        27: _("Twenty-seventh"),
        28: _("Twenty-eighth"),
        29: _("Twenty-ninth")
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
        para.set_top_border(0.2)
        para.set_bottom_border(0.2)
        para.set_padding(1)
        self.doc.add_style("Title",para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(14)
        font.set_bold(1)
        font.set_italic(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_border(0.15)
        para.set_bottom_border(0.15)
        para.set_padding(1)
        self.doc.add_style("Header",para)

        para = ParagraphStyle()
        para.set_first_indent(-0.75)
        para.set_left_margin(1.0)
        para.set_padding(1)
        self.doc.add_style("ListEntry",para)
        try:
            self.doc.open(output)
        except IOError,msg:
            GnomeErrorDialog(_("Could not open %s") % output + "\n" + msg)
        
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
        title = _("Ahnentafel Report for %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        generation = 0
        need_header = 1

        for key in keys :
            if generation == 0 or key >= 2**generation:
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                self.doc.start_paragraph("Header")
                t = _("%s Generation") % AncestorReport.gen[generation+1]
                self.doc.write_text(t)
                self.doc.end_paragraph()
                generation = generation + 1

            self.doc.start_paragraph("ListEntry")
            person = self.map[key]
            name = person.getPrimaryName().getRegularName()
        
            self.doc.write_text(str(key) + ".\t")
            self.doc.start_bold()
            self.doc.write_text(name)
            self.doc.end_bold()
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Check birth record
        
            birth = person.getBirth()
            if birth:
                date = birth.getDateObj().get_start_date()
                place = birth.getPlace()
                if place[-1:] == '.':
                    place = place[:-1]
                if date.getDate() != "" or place != "":
                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            if place != "":
                                t = _("%s was born on %s in %s. ") % \
                                    (name,date.getDate(),place)
                            else:
                                t = _("%s was born on %s. ") % \
                                    (name,date.getDate())
                        else:
                            if place != "":
                                t = _("%s was born in the year %s in %s. ") % \
                                    (name,date.getDate(),place)
                            else:
                                t = _("%s was born in the year %s. ") % \
                                    (name,date.getDate())
                        self.doc.write_text(t)

            death = person.getDeath()
            buried = None
            for event in person.getEventList():
                if string.lower(event.getName()) == "burial":
                    buried = event
        
            if death:
                date = death.getDateObj().get_start_date()
                place = death.getPlace()
                if place[-1:] == '.':
                    place = place[:-1]
                if date.getDate() != "" or place != "":
                    if person.getGender() == RelLib.Person.male:
                        male = 1
                    else:
                        male = 0

                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            if male:
                                if place != "":
                                    t = _("He died on %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("He died on %s") % date.getDate()
                            else:
                                if place != "":
                                    t = _("She died on %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("She died on %s") % date.getDate()
                        else:
                            if male:
                                if place != "":
                                    t = _("He died in the year %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("He died in the year %s") % date.getDate()
                            else:
                                if place != "":
                                    t = _("She died in the year %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("She died in the year %s") % date.getDate()

                        self.doc.write_text(t)

                    if buried:
                        date = buried.getDateObj().get_start_date()
                        place = buried.getPlace()
                        if place[-1:] == '.':
                            place = place[:-1]
                        if date.getDate() != "" or place != "":
                            if date.getDate() != "":
                                if date.getDay() != -1 and date.getMonth() != -1:
                                    if place != "":
                                        t = _(", and was buried on %s in %s.") % \
                                            (date.getDate(),place)
                                    else:
                                        t = _(", and was buried on %s.") % \
                                            date.getDate()
                                else:
                                    if place != "":
                                        t = _(", and was buried in the year %s in %s.") % \
                                            (date.getDate(),place)
                                    else:
                                        t = _(", and was buried in the year %s.") % \
                                            date.getDate()
                            else:
                                t = _(" and was buried in %s." % place)
                        self.doc.write_text(t)
                    else:
                        self.doc.write_text(".")
                        
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

    name = person.getPrimaryName().getRegularName()

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))
    FindDoc.get_text_doc_menu(topDialog.get_widget("format"),0,option_switch)
        
    topDialog.get_widget("labelTitle").set_text("Ahnentafel Report for " + name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked
        })

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def option_switch(obj):
    val = obj.get_data("paper")
    notebook = topDialog.get_widget("option_notebook")
    if val == 1:
        notebook.set_page(0)
    else:
        notebook.set_page(1)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_save_clicked(obj):
    global active_person
    global db

    outputName = topDialog.get_widget("fileentry1").get_full_path(0)
    if not outputName:
        return

    max_gen = topDialog.get_widget("generations").get_value_as_int()
    pgbrk = topDialog.get_widget("pagebreak").get_active()
    template = topDialog.get_widget("htmltemplate").get_full_path(0)
    paper_obj = topDialog.get_widget("papersize").get_menu().get_active()
    paper = paper_obj.get_data("i")
    orien_obj = topDialog.get_widget("orientation").get_menu().get_active()
    orien = orien_obj.get_data("i")
    
    item = topDialog.get_widget("format").get_menu().get_active()
    format = item.get_data("name")
    
    doc = FindDoc.make_text_doc(format,paper,orien,template)

    MyReport = AncestorReport(db,active_person,outputName,max_gen,pgbrk,doc)
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Produces a textual ancestral report")

def get_name():
    return _("Generate files/Ahnentafel Report")

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







