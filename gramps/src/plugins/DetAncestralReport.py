
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

"Generate files/Detailed Ancestral Report"

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
from StyleEditor import *

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
styles = StyleSheet()
style_sheet_list = None

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


    def write_children(self, family):
        """ List children """
        num_children= len(family.getChildList())
        if num_children > 0:
            self.doc.start_paragraph("ChildTitle")
            self.doc.write_text("Children:")
            self.doc.end_paragraph()

        for child in family.getChildList():                     
            self.doc.start_paragraph("ChildList")
            t= child.getPrimaryName().getRegularName()
            if child.getBirth().getDate() != "" or child.getBirth().getPlace() != "":
                t= t+ "    Born: "+child.getBirth().getDate() + \
                                                             " "+child.getBirth().getPlace()
            if child.getDeath().getDate() != "" or child.getDeath().getPlace() != "":
                t= t+ "    Died: "+child.getDeath().getDate() + \
                                                              " "+child.getDeath().getPlace()  
            self.doc.write_text(_(t))
            self.doc.end_paragraph()
         
 
    def write_person(self, key):
        self.doc.start_paragraph("Entry","%s." % str(key))
        person = self.map[key]
        name = person.getPrimaryName().getRegularName()
        
        self.doc.start_bold()
        self.doc.write_text(name)
        self.doc.end_bold()

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
                            t = _(" was born on %s in %s. ") % \
                                    (date.getDate(),place)
                        else:
                            t = _(" was born on %s. ") % \
                                    (date.getDate())
                    else:
                            if place != "":
                                t = _(" was born in the year %s in %s. ") % \
                                    (date.getDate(),place)
                            else:
                                t = _(" was born in the year %s. ") % \
                                    (date.getDate())
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

            ext_family= person.getMainFamily()
            if ext_family != None:
                if ext_family.getFather() != "":
                    if person.getGender() == RelLib.Person.male:
                        t= "  He was the son of "
                    else:
                        t= "  She was the daughter of "
                    father= ext_family.getFather()
                    t= t+father.getPrimaryName().getRegularName()
                if ext_family.getMother() != "":
                    mother= ext_family.getMother()
                    if mother != None:
                        t= t + " and " + mother.getPrimaryName().getRegularName()
                    self.doc.write_text(_(t + "."))
 
            famList= person.getFamilyList()
            if len(famList) > 0:
                for family in famList:
                    famList= person.getFamilyList()
                    if len(famList) > 0:
                        spouse= ""
                        for fam in famList:
                            if person.getGender() == RelLib.Person.male:
                                if fam.getMother() != None:
                                    spouse= fam.getMother().getPrimaryName().getRegularName()
                                    heshe= "He"
                            else:
                                if fam.getFather() != None:
                                    spouse= fam.getFather().getPrimaryName().getRegularName()
                                    heshe= "She"
                            marriage= family.getMarriage()
                            if spouse != "":
                                t= "  %s married %s" % (heshe, spouse)
                                if marriage != None:
                                    if marriage.getDate() != "":
                                        t= t+ " on "+marriage.getDate()
                                    if marriage.getPlace() != "":
                                        t= t+ " in "+marriage.getPlace()
                                self.doc.write_text(_(t+"."))
                        
            if person.getNote() != "":
                self.doc.end_paragraph()
                self.doc.start_paragraph("Entry")
                st = _("Notes for %s" % name)
                self.doc.write_text(st)
                self.doc.write_text(person.getNote())

            self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):

        self.filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("Title")
        title = _("Detailed Ancestral Report for %s") % name
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
                self.doc.start_paragraph("Generation")
                t = _("%s Generation") % AncestorReport.gen[generation+1]
                self.doc.write_text(t)
                self.doc.end_paragraph()
                generation = generation + 1

            self.write_person(key)

            person = self.map[key]
            if person.getGender() == RelLib.Person.female:
                family= person.getFamilyList()[0]
                self.write_children(family)
            
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
    global style_sheet_list
    
    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "ancestorreport.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))
    FindDoc.get_text_doc_menu(topDialog.get_widget("format"),0,option_switch)
        
    styles.clear()
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF,size=16,bold=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set(pad=0.5)
    styles.add_style("Title",para)

    font = FontStyle()
    font.set(face=FONT_SANS_SERIF,size=14,italic=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    styles.add_style("Generation",para)

    font = FontStyle()
    font.set(face=FONT_SANS_SERIF,size=12,italic=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_header_level(3)
    para.set_left_margin(1.0)   # in centimeters
    para.set(pad=0.5)
    styles.add_style("ChildTitle",para)
 
    para = ParagraphStyle()
    para.set(first_indent=1.0,lmargin=0.0,pad=0.25)
    styles.add_style("ChildList",para)

    para = ParagraphStyle()
    para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
    styles.add_style("Entry",para)

    style_sheet_list = StyleSheetList("det_ancestor_report.xml",styles)
    build_menu(None)

    topDialog.get_widget("labelTitle").set_text("Detailed Ancestral Report for " + name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_style_edit_clicked" : on_style_edit_clicked,
        "on_save_clicked" : on_save_clicked
        })

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def build_menu(object):
    menu = topDialog.get_widget("style_menu")

    myMenu = GtkMenu()
    for style in style_sheet_list.get_style_names():
        menuitem = GtkMenuItem(style)
        menuitem.set_data("d",style_sheet_list.get_style_sheet(style))
        menuitem.show()
        myMenu.append(menuitem)
    menu.set_menu(myMenu)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def option_switch(obj):
    val = obj.get_data("paper")
    st = obj.get_data("styles")
    notebook = topDialog.get_widget("option_notebook")
    if val == 1:
        notebook.set_page(0)
    else:
        notebook.set_page(1)
    topDialog.get_widget("style_frame").set_sensitive(st)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_style_edit_clicked(obj):
    StyleListDisplay(style_sheet_list,build_menu,None)
    
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

    styles = topDialog.get_widget("style_menu").get_menu().get_active().get_data("d")
    
    doc = FindDoc.make_text_doc(styles,format,paper,orien,template)

    MyReport = AncestorReport(db,active_person,outputName,max_gen,pgbrk,doc)
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Produces a detailed textual ancestral report")

def get_name():
    return _("Generate files/Detailed Ancestral Report")

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
