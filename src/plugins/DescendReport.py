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

"Generate files/Descendant Report"

import os
import sort
import string
import intl

_ = intl.gettext

import const
import Config
import utils
from TextDoc import *
from StyleEditor import *
import FindDoc

import gtk
import libglade

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantReport:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,name,person,db,doc):
        self.creator = db.getResearcher().getName()
        self.name = name
        self.person = person
        self.doc = doc
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.doc.open(self.name)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.doc.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump_dates(self, person):
        birth = person.getBirth().getDateObj().get_start_date()
        death = person.getDeath().getDateObj().get_start_date()
        if birth.getYearValid() or death.getYearValid():
            self.doc.write_text(' (')
            if birth.getYearValid():
                self.doc.write_text('b. ' + str(birth.getYear()))
            if death.getYearValid():
                if birth.getYearValid():
                    self.doc.write_text(', ')
                self.doc.write_text('d. ' + str(death.getYear()))
            self.doc.write_text(')')
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def report(self):
        self.doc.start_paragraph("Title")
        name = self.person.getPrimaryName().getRegularName()
        self.doc.write_text(_("Descendants of %s") % name)
        self.dump_dates(self.person)
        self.doc.end_paragraph()
        self.dump(0,self.person)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump(self,level,person):

        if level != 0:
            self.doc.start_paragraph("Level" + str(level))
            self.doc.write_text(str(level) + '. ')
            self.doc.write_text(person.getPrimaryName().getRegularName())
            self.dump_dates(person)
            self.doc.end_paragraph()

        childlist = []
        for family in person.getFamilyList():
            for child in family.getChildList():
                childlist.append(child)

        childlist.sort(sort.by_birthdate)
        for child in childlist:
            self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DesReportWindow:
    def __init__(self,person,db):
        import PaperMenu
        
        self.person = person

        glade_file = os.path.dirname(__file__) + os.sep + "desreport.glade"
        self.top = libglade.GladeXML(glade_file,"dialog1")
        self.top.get_widget("fileentry1").set_default_path(Config.report_dir)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_style_edit_clicked" : on_style_edit_clicked,
            "on_save_clicked": on_save_clicked
            })

        notebook = self.top.get_widget("option_notebook")
        notebook.set_data("frame",self.top.get_widget("style_frame"))
        PaperMenu.make_paper_menu(self.top.get_widget("papersize"))
        PaperMenu.make_orientation_menu(self.top.get_widget("orientation"))
        FindDoc.get_text_doc_menu(self.top.get_widget("format"),0,\
                                  option_switch,notebook)
        
        mytop = self.top.get_widget("dialog1")

        f = FontStyle()
        f.set_size(14)
        f.set_type_face(FONT_SANS_SERIF)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_header_level(1)
        p.set_font(f)
        
        sheet = StyleSheet()
        sheet.add_style("Title",p)

        f = FontStyle()
        for i in range(1,10):
            p = ParagraphStyle()
            p.set_font(f)
            p.set_left_margin(float(i-1))
            sheet.add_style("Level" + str(i),p)

        self.style_sheet_list = StyleSheetList("descend_report.xml",sheet)
        build_menu(self)

        mytop.set_data("o",self)
        mytop.set_data("d",db)
        mytop.show()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def build_menu(object):

    myMenu = gtk.GtkMenu()

    for style in object.style_sheet_list.get_style_names():
        menuitem = gtk.GtkMenuItem(style)
        menuitem.set_data("d",object.style_sheet_list.get_style_sheet(style))
        menuitem.show()
        myMenu.append(menuitem)

    object.top.get_widget("style_menu").set_menu(myMenu)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def option_switch(obj):
    val = obj.get_data("paper")
    st = obj.get_data("styles")
    notebook = obj.get_data("obj")
    frame = notebook.get_data("frame")
    if val == 1:
        notebook.set_page(0)
    else:
        notebook.set_page(1)
    frame.set_sensitive(st)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    DesReportWindow(person,database)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_style_edit_clicked(obj):
    myobj = obj.get_data("o")
    StyleListDisplay(myobj.style_sheet_list,build_menu,myobj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_clicked(obj):
    myobj = obj.get_data("o")
    db = obj.get_data("d")

    file = myobj.top.get_widget("fileentry1").get_full_path(0)
    if file == "":
        return

    paper_obj = myobj.top.get_widget("papersize")
    paper = paper_obj.get_menu().get_active().get_data("i")

    orien_obj = myobj.top.get_widget("orientation")
    orien = orien_obj.get_menu().get_active().get_data("i")

    template = myobj.top.get_widget("htmltemplate").get_full_path(0)

    item = myobj.top.get_widget("format").get_menu().get_active()
    format = item.get_data("name")
    
    styles = myobj.top.get_widget("style_menu").get_menu().get_active().get_data("d")
    doc = FindDoc.make_text_doc(styles,format,paper,orien,template)

    report = DescendantReport(file,myobj.person,db,doc)
    report.setup()
    report.report()
    report.end()

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
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@..................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +............@@@@@@@@@@@.........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
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
    _("Descendant Report"),
    category=_("Generate Files"),
    description=_("Generates a list of descendants of the active person"),
    xpm=get_xpm_image()
    )

