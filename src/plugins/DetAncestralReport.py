
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000 Bruce J. DeGrasse
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
        #print "Children= ", len(family.getChildList())
        if num_children > 0:
            self.doc.start_paragraph("ChildTitle")
            self.doc.write_text("Children:")
            self.doc.end_paragraph()

        for child in family.getChildList():
            self.doc.start_paragraph("ChildList")
            t= child.getPrimaryName().getRegularName()
            #print "getBirth()", child.getBirth().__dict__
            if child.getBirth().getDate() != "" and \
                    child.getBirth().getPlaceName() != "":
                #print child.getBirth().getPlace().__dict__
                t= t+ " Born: "+child.getBirth().getDate() + \
                    " "+child.getBirth().getPlaceName()
            #print "getDeath()", child.getDeath().__dict__
            if child.getDeath().getPlace() != None:
                #print child.getDeath().getPlace().__dict__
                if child.getDeath().getDate() != "" or \
                            child.getDeath().getPlaceName() != "":
                    t= t+ " Died: "+child.getDeath().getDate() + \
                            " "+child.getDeath().getPlaceName()
            self.doc.write_text(_(t))
            self.doc.end_paragraph()


    def write_person(self, key, rptOptions):
        """Output birth, death, parentage, marriage and notes information """

        self.doc.start_paragraph("Entry","%s." % str(key))
        person = self.map[key]
        name = person.getPrimaryName().getRegularName()

        if rptOptions.firstName == reportOptions.Yes:
            firstName= person.getPrimaryName().getFirstName()
        elif person.getGender() == RelLib.Person.male:
            firstName= "He"
        else:
            firstName= "She"

        self.doc.start_bold()
        self.doc.write_text(name)
        self.doc.end_bold()

        # Check birth record
        #print person.getPrimaryName().getRegularName()
        birth = person.getBirth()
        if birth:
            date = birth.getDateObj().get_start_date()
            if birth.getPlaceName() != "":
                place = birth.getPlaceName()
            else: place= ""
            if place[-1:] == '.':
                place = place[:-1]
            t= ""
            if date.getDate() != "":
                if date.getDay() != -1 and date.getMonth() != -1 and \
                    rptOptions.fullDate == reportOptions.Yes:
                    t= "on %s" % date.getDate()
                else:
                    t= "in the year %s" % date.getYear()
            elif rptOptions.blankDate == reportOptions.Yes:
                t= "on _______________"
            if place != "":
                t= t + " in %s" % place
            elif rptOptions.blankPlace == reportOptions.Yes:
                t= t + " in _____________________"

            if t != "":
                self.doc.write_text(_(" was born " + t + "."))
            else: self.doc.write_text(_("."))

        t= ""
        death = person.getDeath()
        buried = None
        for event in person.getEventList():
            if string.lower(event.getName()) == "burial":
                buried = event

            if death:
                date = death.getDateObj().get_start_date()
                place = death.getPlaceName()
                if place[-1:] == '.':
                    place = place[:-1]
                t= "  %s died " % firstName
                if date.getDate() != "":
                    if date.getDay() != -1 and date.getMonth() != -1 and \
                            rptOptions.fullDate == reportOptions.Yes:
                        t= t + ("on %s" % date.getDate())
                    else:
                        t= t + ("in the year %s" % date.getDate())
                elif rptOptions.blankDate == reportOptions.Yes:
                    t= "on ______________"

                if place != "":
                    t= t + (" in %s") % place
                elif rptOptions.blankPlace == reportOptions.Yes:
                    t= t + (" in _____________")

                if buried:
                    date = buried.getDateObj().get_start_date()
                    place = buried.getPlaceName()
                    if place[-1:] == '.':
                        place = place[:-1]
                    if date.getDate() != "" or place != "":
                        t= t + ", and was buried "
                        if date.getDate() != "":
                           if date.getDay() != -1 and date.getMonth() != -1 and \
                                        rptOptions.fullDate == reportOptions.Yes:
                               t= t + "on %s" % date.getDate()
                               if place != "":
                                   t = t + " in %s" % place
                           else:
                               t = t + "in the year %s" % date.getDate()
                        elif rptOptions.blankDate == reportOptions.Yes:
                               t= t + " on ___________"
                        if place != "":
                               t = t + " in %s" % place

                if rptOptions.calcAgeFlag == reportOptions.Yes:
                        t= t + rptOptions.calcAge(birth.date.start, death.date.start)
                if t != "":
                    self.doc.write_text(_(t+"."))

        ext_family= person.getMainFamily()
        if ext_family != None:
            if ext_family.getFather() != None:
                father= ext_family.getFather().getPrimaryName().getRegularName()
            else: father= ""
            if ext_family.getMother() != None:
                mother= ext_family.getMother().getPrimaryName().getRegularName()
            else: mother= ""

            if father != "" or mother != "":
                t = "  %s was the " % firstName
                if person.getGender() == RelLib.Person.male:
                    t= t + "son of"
                else:
                    t= t + "daughter of"
                if father != "":
                    t= t + " %s" % father
                if mother != "":
                    t= t + " and %s" % mother
                else: t= t + " %s" % mother

                self.doc.write_text(_(t + "."))
                t= ""

        famList= person.getFamilyList()
        #print "len of famList=", len(famList)
        if len(famList) > 0:
            for fam in famList:
                #print "fam", fam.__dict__
                spouse= ""
                if person.getGender() == RelLib.Person.male:
                    if fam.getMother() != None:
                        spouse= fam.getMother().getPrimaryName().getRegularName()
                        heshe= "He"
                    else:
                        heshe= "She"
                        if fam.getFather() != None:
                            spouse= fam.getFather().getPrimaryName().getRegularName()

                    marriage= fam.getMarriage()
                    if marriage != None:
                        #print "marriage", marriage.__dict__
                        if spouse != "":
                            t= "  %s married %s" % (heshe, spouse)
                        else:
                            t= "  %s was married" % heshe
                        date= marriage.getDateObj()
                        if date != None:
                            #print "date", date.__dict__
                            #print "date.start=", date.start.__dict__
                            if date.getYear() != -1:
                                if date.getDay() != -1 and \
                                            date.getMonth() != -1 and \
                                            rptOptions.fullDate == reportOptions.Yes:
                                    t= t + " on "+date.getDate()
                                else: t= t + " in the year %s" % date.getYear()
                            elif rptOptions.blankDate == reportOptions.Yes:
                                t= t + " on __________"
                        else: t= t + " on __________"

                        if marriage.getPlace() != None and \
                                marriage.getPlaceName() != "":
                            t= t + " in " + marriage.getPlaceName()
                        elif rptOptions.blankPlace == reportOptions.Yes:
                            t= t + " in ____________"
            self.doc.write_text(_(t+"."))


        if person.getNote() != "" and rptOptions.includeNotes == reportOptions.Yes:
            self.doc.end_paragraph()
            self.doc.start_paragraph("Entry")
            self.doc.write_text(_("Notes for %s" % name))
            self.doc.end_paragraph()
            self.doc.start_paragraph("Entry")
            self.doc.write_text(person.getNote())
            #print person.getNote()
        self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def write_report(self):

        self.filter(self.start,1)
        rptOpt= reportOptions()

        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("Title")
        title = _("Detailed Ancestral Report for %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()

        keys = self.map.keys()
        keys.sort()
        generation = 0
        need_header = 1

        rptOpt.blankDate = reportOptions.No
        rptOpt.blankPlace = reportOptions.No
        
        for key in keys :
            if generation == 0 or key >= 2**generation:
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                self.doc.start_paragraph("Generation")
                t = _("%s Generation") % AncestorReport.gen[generation+1]
                self.doc.write_text(t)
                self.doc.end_paragraph()
                generation = generation + 1

            self.write_person(key, rptOpt)

            person = self.map[key]
            if person.getGender() == RelLib.Person.female and  \
                     rptOpt.listChildren == reportOptions.Yes and  \
                     len(person.getFamilyList()) > 0:
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
#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Detailed Ancestral Report"),
    category=_("Generate Files"),
    description= _("Produces a detailed ancestral report"),
    xpm= get_xpm_image()
    )


#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class reportOptions:
    Yes=1
    No= 0
    Left= 2
    Right= 3

    def __init__(self):
        ### Initialize report options###

        #Use first name in place of he or she in text
        self.firstName= reportOptions.Yes

        #Use year only, not full date/month
        self.fullDate= reportOptions.Yes

        #Do not list children
        self.listChildren= reportOptions.Yes

        #Add stepchildren to the list of children
        #self.addStepChildren= reportOptions.Yes

        #Print notes
        self.includeNotes= reportOptions.Yes

        #Selectively print notes (omit private information)
        #self.omitPrivInfo= reportOptions.No

        #generate header for each page, specify text
        #self.noHeader= reportOptions.Yes

        #Inculde reference notes
        #self.noRefNotes= reportOptions.Yes

        #Include source notes
        #self.noSourceNotes= reportOptions.Yes

        #Replace missing Place with ___________
        self.blankPlace= reportOptions.Yes

        #Replace missing dates with __________
        self.blankDate= reportOptions.Yes

        #Omit country code
        #self.noCountryInfo= reportOptions.No

        #Put title before or after name (Dr., Lt., etc.)
        #self.titleAfter= reportOptions.Yes

        #Add "Died at the age of NN" in text
        self.calcAgeFlag= reportOptions.Yes

        #Omit sensitive information such as birth, christening, marriage
        #   for living after XXXXX date.

        #Add photos/images
        #self.images.append(key, kname, align, width, height)
        #self.images= []
        #self.images.append(1, "TMDeG_72.pjg", Right, 144, 205)

    #def addImages(self, key= 0, fname= "", align= Right, Width= none, height= None):
        #if key == 0 or fname == "" or (align != Left and align != Right):
            #print Invalid Image Specification: ke= %s, fname= %s width %s % key, fname, align
        #else:
            #self.images.append(key, fname, align, width, height)

    def calcAge(self, birth, death):
        ### Calulate age ###

        self.t= ""
        if birth.year != -1 and death.year != -1:
            self.age= death.year - birth.year
            self.units= "year"
            if birth.month != -1 and death.month != -1:
                if birth.month > death.month:
                    self.age= self.age -1
                if birth.day != -1 and death.day != -1:
                    if birth.month == death.month and birth.day > death.day:
                        self.age= self.age -1
                        self.units= "month"
                    if self.age == 0:
                        self.age= death.month - birth.month   # calc age in months
                        if birth.day > death.day:
                            self.age= self.age - 1
                        if self.age == 0:
                            self.age= death.day + 31 - birth.day # calc age in days
                            self.units= "day"
            self.t= " at the age of %d %s" % (self.age, self.units)
            if self.age > 1:  self.t= self.t + "s"
        return self.t
