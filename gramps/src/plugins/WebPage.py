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

"Web Site/Generate Web Site"

from RelLib import *
from TextDoc import *
from HtmlDoc import *

import const
import utils
import Config
import intl
_ = intl.gettext

import os
import re
import sort
import string
import time

from gtk import *
from gnome.ui import *
from libglade import *
from StyleEditor import *

active_person = None
db = None
topDialog = None

glade_file = os.path.dirname(__file__) + os.sep + "webpage.glade"

restrict = 1
private = 1
restrict_photos = 0
no_photos = 0
styles = StyleSheet()
style_sheet_list = None


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def by_date(a,b):
    return compare_dates(a.getDateObj(),b.getDateObj())

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HtmlLinkDoc(HtmlDoc):

    def start_link(self,path):
        self.f.write('<A HREF="%s">' % path)

    def end_link(self):
        self.f.write('</A>')

    def newline(self):
        self.f.write('<BR>\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,person,photos,restrict,private,link,list,dir_name,doc):
        self.person = person
        self.doc = doc
        self.list = list
        self.private = private
        self.alive = probably_alive(person) or restrict
        self.photos = (photos == 2) or (photos == 1 and not self.alive)
        self.dir = dir_name
        self.link = link
        self.slist = []
        self.scnt = 1

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_column_widths([15,85])
        self.doc.add_table_style("IndTable",tbl)

        cell = TableCellStyle()
        self.doc.add_cell_style("NormalCell",cell)

        name = person.getPrimaryName().getRegularName()
        self.doc.set_title(_("Summary of %s") % name)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_normal_row(self,label,data,sref):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(label)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        self.doc.write_text(data)
        if sref != None and sref.getBase() != None :
            self.doc.start_link("#s%d" % self.scnt)
            self.doc.write_text("<SUP>%d</SUP>" % self.scnt)
            self.doc.end_link()
            self.scnt = self.scnt + 1
            self.slist.append(sref)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_marriage_row(self,list):
        self.doc.start_row()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(list[0])
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        self.doc.write_text(list[1])
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_link_row(self,title,person):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(title)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        if person:
            if person in self.list:
                self.doc.start_link("%s.html" % person.getId())
            self.doc.write_text(person.getPrimaryName().getRegularName())
            if person in self.list:
                self.doc.end_link()

        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def write_sources(self):
        self.doc.start_paragraph("SourcesTitle")
        self.doc.write_text(_("Sources"))
        self.doc.end_paragraph()

        index = 1
        for sref in self.slist:
            self.doc.start_paragraph("SourceParagraph")
            self.doc.write_text('<A NAME="s%d">%d. ' % (index,index))
            index = index + 1
            self.doc.write_text("%s. " % sref.getBase().getTitle())
            author = sref.getBase().getAuthor()
            if author != "":
                self.doc.write_text("%s. " % author)
            pubinfo = sref.getBase().getPubInfo()
            if pubinfo != "":
                self.doc.write_text("%s. " % pubinfo)
            if sref.getDate() != "":
                self.doc.write_text("%s. " % sref.getDate())
            if sref.getPage() != "":
                self.doc.write_text("%s. " % sref.getPage())
            self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def create_page(self):
        filebase = "%s.html" % self.person.getId()
        self.doc.open("%s%s%s" % (self.dir,os.sep,filebase))

        photo_list = self.person.getPhotoList()
        name_obj = self.person.getPrimaryName()
        name = name_obj.getRegularName()

        self.doc.start_paragraph("Title")
        self.doc.write_text(_("Summary of %s") % name)
        self.doc.end_paragraph()

        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()

        if self.photos and len(photo_list) > 0:
            file = photo_list[0].getPath()
            self.doc.start_paragraph("Data")
            self.doc.add_photo(file,4.0,4.0)
            self.doc.end_paragraph()

        self.doc.start_table("one","IndTable")
        self.write_normal_row("%s:" % _("Name"), name, name_obj.getSourceRef())
        if self.person.getGender() == Person.male:
            self.write_normal_row("%s:" % _("Gender"), \
                                  _("Male"),None)
        else:
            self.write_normal_row("%s:" % _("Gender"), \
                                  _("Female"),None)

        family = self.person.getMainFamily()
        if family:
            self.write_link_row("%s:" % _("Father"), family.getFather())
            self.write_link_row("%s:" % _("Mother"), family.getMother())
        else:
            self.write_link_row("%s:" % _("Father"), None)
            self.write_link_row("%s:" % _("Mother"), None)
        self.doc.end_table()
        
        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()
        
        self.write_facts()
        self.write_notes()
        self.write_families()
        if self.scnt > 1:
            self.write_sources()

        if self.link:
            self.doc.start_paragraph("Data")
            self.doc.start_link("index.html")
            self.doc.write_text(_("Return to the index of people"))
            self.doc.end_link()
            self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def close(self):
        self.doc.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_facts(self):

        self.doc.start_paragraph("EventsTitle")
        self.doc.write_text(_("Facts and Events"))
        self.doc.end_paragraph()

        self.doc.start_table("two","IndTable")

        event_list = [ self.person.getBirth(), self.person.getDeath() ]
        event_list = event_list + self.person.getEventList()
        event_list.sort(by_date)
        for event in event_list:
            if event.getPrivacy():
                continue
            name = _(event.getName())
            date = event.getDate()
            if event.getPlace():
                place = event.getPlace().get_title()
            else:
                place = ""
            description = event.getDescription()
            if date == "":
                if place == "":
                    continue
                else:
                    val = "%s. %s" % (place,description)
            else:
                if place == "":
                    val = "%s. %s" % (date,description)
                else:
                    val = "%s, %s. %s" % (date,place,description)

            self.write_normal_row(name, val, event.getSourceRef())

        self.doc.end_table()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_notes(self):

        if self.person.getNote() == "":
            return
        
        self.doc.start_paragraph("NotesTitle")
        self.doc.write_text(_("Notes"))
        self.doc.end_paragraph()

        self.doc.start_paragraph("NotesParagraph")
        self.doc.write_text(self.person.getNote())
        self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_fam_fact(self,event):

        if event == None:
            return
        name = event.getName()
        date = event.getDate()
        if event.getPlace():
            place = event.getPlace().get_title()
        else:
            place = ""
        description = event.getDescription()
        if date == "":
            if place == "":
                return
            else:
                val = "%s. %s" % (place,description)
        else:
            if place == "":
                val = "%s. %s" % (date,description)
            else:
                val = "%s, %s. %s" % (date,place,description)

        self.write_marriage_row([name, val])

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):
        self.doc.start_paragraph("FamilyTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()

        self.doc.start_table("three","IndTable")
        
        for family in self.person.getFamilyList():
            if self.person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.doc.start_row()
            self.doc.start_cell("NormalCell",2)
            self.doc.start_paragraph("Spouse")
            if spouse:
                self.doc.start_link("%s.html" % spouse.getId())
                self.doc.write_text(spouse.getPrimaryName().getRegularName())
                self.doc.end_link()
            else:
                self.doc.write_text(_("unknown"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            for event in family.getEventList():
                if event.getPrivacy() == 0:
                    self.write_fam_fact(event)

            child_list = family.getChildList()
            if len(child_list) > 0:

                self.doc.start_cell("NormalCell")
                self.doc.start_paragraph("Label")
                self.doc.write_text(_("Children"))
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell("NormalCell")
                self.doc.start_paragraph("Data")
                
                first = 1
                for child in family.getChildList():
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    self.doc.start_link("%s.html" % child.getId())
                    self.doc.write_text(child.getPrimaryName().getRegularName())
                    self.doc.end_link()
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def individual_filter(database,person,list):
    list.append(person)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def ancestor_filter(database,person,list):

    if person == None:
        return
    if person not in list:
        list.append(person)
    family = person.getMainFamily()
    if family != None:
        ancestor_filter(database,family.getFather(),list)
        ancestor_filter(database,family.getMother(),list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def descendant_filter(database,person,list):

    if person == None or person in list:
        return
    if person not in list:
        list.append(person)
    for family in person.getFamilyList():
        for child in family.getChildList():
            descendant_filter(database,child,list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_filter(database,person,list):

    descendant_filter(database,person,list)
    ancestor_filter(database,person,list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def entire_db_filter(database,person,list):

    for entry in database.getPersonMap().values():
        list.append(entry)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_of_gparents_filter(database,person,list):

    my_list = []

    family = person.getMainFamily()
    if family == None:
        return

    for p in [ family.getMother(), family.getFather() ]:
	if p:
            pf = p.getMainFamily()
            if pf:
                if pf.getFather():
                    my_list.append(pf.getFather())
                if pf.getMother():
                    my_list.append(pf.getMother())

    for person in my_list:
        descendant_filter(database,person,list)
        ancestor_filter(database,person,list)

#------------------------------------------------------------------------
#
# Mams menu items to filter functions
#
#------------------------------------------------------------------------

filter_map = {
    _("Individual") : individual_filter,
    _("Ancestors") : ancestor_filter,
    _("Descendants") : descendant_filter,
    _("Ancestors and descendants") : an_des_filter,
    _("Grandparent's ancestors and descendants") : an_des_of_gparents_filter,
    _("Entire database") : entire_db_filter
    }
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def probably_alive(person):

    if person == None:
        return 1

    death = person.getDeath()
    birth = person.getBirth()

    if death.getDate() != "":
        return 0
    if birth.getDate() != "":
        year = birth.getDateObj().get_start_date().getYear()
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]
        if year != -1 and current_year - year > 110:
            return 0
    return 1

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    global active_person
    global topDialog
    global db
    global styles
    global style_sheet_list
    
    active_person = person
    db = database

    font = FontStyle()
    font.set(bold=1, face=FONT_SANS_SERIF, size=16)
    p = ParagraphStyle()
    p.set(align=PARA_ALIGN_CENTER,font=font)
    styles.add_style("Title",p)
    
    font = FontStyle()
    font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
    p = ParagraphStyle()
    p.set(font=font,bborder=1)
    styles.add_style("EventsTitle",p)

    font = FontStyle()
    font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
    p = ParagraphStyle()
    p.set(font=font,bborder=1)
    styles.add_style("NotesTitle",p)

    font = FontStyle()
    font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
    p = ParagraphStyle()
    p.set(font=font,bborder=1)
    styles.add_style("SourcesTitle",p)

    font = FontStyle()
    font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
    p = ParagraphStyle()
    p.set(font=font,bborder=1)
    styles.add_style("FamilyTitle",p)
    
    font = FontStyle()
    font.set(bold=1,face=FONT_SANS_SERIF,size=12)
    p = ParagraphStyle()
    p.set_font(font)
    styles.add_style("Spouse",p)

    font = FontStyle()
    font.set(size=12,italic=1)
    p = ParagraphStyle()
    p.set_font(font)
    styles.add_style("Label",p)

    font = FontStyle()
    font.set_size(12)
    p = ParagraphStyle()
    p.set_font(font)
    styles.add_style("Data",p)

    font = FontStyle()
    font.set_size(10)
    p = ParagraphStyle()
    p.set_font(font)
    styles.add_style("SourceParagraph",p)

    font = FontStyle()
    font.set_size(12)
    p = ParagraphStyle()
    p.set_font(font)
    styles.add_style("NotesParagraph",p)

    style_sheet_list = StyleSheetList("webpage.xml",styles)

    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_nophotos_toggled" : on_nophotos_toggled,
        "on_style_edit_clicked" : on_style_edit_clicked,
        "on_ok_clicked" : on_ok_clicked,
        }

    topDialog = GladeXML(glade_file,"top")
    topDialog.signal_autoconnect(dic)
    build_menu(None)
    
    top = topDialog.get_widget("top")
    topDialog.get_widget("targetDirectory").set_default_path(Config.web_dir)
    topDialog.get_widget("tgtdir").set_text(Config.web_dir)
    filterName = topDialog.get_widget("filterName")

    popdown_strings = filter_map.keys()
    popdown_strings.sort()
    filterName.set_popdown_strings(popdown_strings)

    name = person.getPrimaryName().getName()
    topDialog.get_widget("personName").set_text(name)

    top.show()
    
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
def on_nophotos_toggled(obj):
    if obj.get_active():
        topDialog.get_widget("restrict_photos").set_sensitive(0)
    else:
        topDialog.get_widget("restrict_photos").set_sensitive(1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_ok_clicked(obj):
    global active_person
    global filter_map
    global db

    filterName = topDialog.get_widget("filter").get_text()
    dir_name = topDialog.get_widget("targetDirectory").get_full_path(0)
    templ_name = topDialog.get_widget("htmlTemplate").get_full_path(0)

    restrict = topDialog.get_widget("restrict").get_active()
    privated = topDialog.get_widget("private").get_active()
    restrict_photos = topDialog.get_widget("restrict_photos").get_active()
    no_photos = topDialog.get_widget("nophotos").get_active()
    include_link = topDialog.get_widget("include_link").get_active()

    if dir_name == None:
        dir_name = os.getcwd()
    elif not os.path.isdir(dir_name):
        parent_dir = os.path.dirname(dir_name)
        if not os.path.isdir(parent_dir):
            GnomeErrorDialog(_("Neither %s nor %s are directories") % \
                             (dir_name,parent_dir))
            return
        else:
            try:
                os.mkdir(dir_name)
            except IOError, value:
                GnomeErrorDialog(_("Could not create the directory : %s") % \
                                 dir_name + "\n" + value[1])
                return
            except:
                GnomeErrorDialog(_("Could not create the directory : %s") % \
                                 dir_name)
                return

    filter = filter_map[filterName]
    ind_list = []

    filter(db,active_person,ind_list)
    styles = topDialog.get_widget("style_menu").get_menu().get_active().get_data("d")

    if no_photos == 1:
        photos = 0
    elif restrict_photos == 1:
        photos = 1
    else:
        photos = 2

    for person in ind_list:
        doc = HtmlLinkDoc(styles,templ_name)
        idoc = IndividualPage(person,photos,restrict,private,\
                              include_link, ind_list,dir_name,doc)
        idoc.create_page()
        idoc.close()
        
    if len(ind_list) > 1:
        dump_index(ind_list,styles,templ_name,dir_name)
        
    utils.destroy_passed_object(obj)
    
#------------------------------------------------------------------------
#
# Writes a index file, listing all people in the person list.
#
#------------------------------------------------------------------------
def dump_index(person_list,styles,template,html_dir):

    doc = HtmlLinkDoc(styles,template)
    doc.set_title(_("Family Tree Index"))

    doc.open(html_dir + os.sep + "index.html")
    doc.start_paragraph("Title")
    doc.write_text(_("Family Tree Index"))
    doc.end_paragraph()

    person_list.sort(sort.by_last_name)
    for person in person_list:
        name = person.getPrimaryName().getName()
        doc.start_link("%s.html" % person.getId())
        doc.write_text(name)
        doc.end_link()
        doc.newline()
    doc.close()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Generate Web Site"),
    category=_("Web Page"),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals.")
    )

