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
import tempfile
import OpenOffice
import utils

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

    def __init__(self,database,family,output,template):
        pass
    
    def setup(self):
        pass
    
    def end(self):
        pass
    
    def write_header(self):
        pass
    
    def write_parent(self,type,name):
        pass
    
    def start_parent_stats(self):
        pass
    
    def end_parent_stats(self):
        pass
    
    def write_parent_stats(self,str1,str2,str3):
        pass
    
    def write_parent_parent(self,str1,str2):
        pass
    
    def start_child_stats(self):
        pass
    
    def end_child_stats(self):
        pass
        
    def write_child_stats(self,str1,str2,str3,str4,last):
        pass
    
    def write_child_name(self,index,child):
        pass
    
    def write_child_spouse(self,spouse):
        pass
    
    def dump_parent(self,person):
        self.start_parent_stats();
        if person.getGender() == RelLib.Person.male:
            self.write_parent("Husband:",person)
        else:
            self.write_parent("Wife:",person)
        birth = person.getBirth()
        death = person.getDeath()
        self.write_parent_stats("Birth",birth.getDate(),birth.getPlace())
        self.write_parent_stats("Death",death.getDate(),death.getPlace())
        family = person.getMainFamily()
        if family == None or family.getFather() == None:
            father_name = ""
        else:
            father_name = family.getFather().getPrimaryName().getRegularName()
        if family == None or family.getMother() == None:
            mother_name = ""
        else:
            mother_name = family.getMother().getPrimaryName().getRegularName()
        self.write_parent_parent("Father",father_name)
        self.write_parent_parent("Mother",mother_name)
        self.end_parent_stats();
    
    def dump_child(self,index,person):
        self.start_child_stats();
        birth = person.getBirth()
        death = person.getDeath()
        self.write_child_name(index,person)

        families = len(person.getFamilyList())
        self.write_child_stats("","Birth",birth.getDate(),\
                               birth.getPlace(),0)
        if families == 0:
            last = 1
        else:
            last = 0
        self.write_child_stats("","Death",death.getDate(),\
                               death.getPlace(),last)

        index = 1
        for family in person.getFamilyList():
            if person == family.getFather():
                self.write_child_spouse(family.getMother())
            else:
                self.write_child_spouse(family.getFather())
            m = family.getMarriage()
            if families == index:
                last = 1
            else:
                last = 0
            self.write_child_stats("","Married",m.getDate(),m.getPlace(),last)
            
        self.end_child_stats();

    def write_report(self):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class OpenOfficeFamilyGroup(FamilyGroup):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,family,output,template):
        self.map = {}
        self.database = database
        self.family = family
        creator = db.getResearcher().getName()
        self.open_office = OpenOffice.OpenOfficeCore(output,template,".sxw",creator)
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.file = self.open_office.setup()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.open_office.end()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_header(self):
        self.file.write('<text:h text:style-name="Heading 1" ')
        self.file.write('text:level="1">')
        self.file.write('Family Group Record')
        self.file.write('</text:h>\n')
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent(self,type,name):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell ")
        self.file.write("table:style-name=\"Table1.A3\" ")
        self.file.write("table:number-columns-spanned=\"3\" ")
        self.file.write("table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"ParentHead\">")
        self.file.write(type)
        self.file.write("<text:tab-stop/>")
        self.file.write(name.getPrimaryName().getRegularName())
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def start_parent_stats(self):
        self.file.write("<table:table table:name=\"Table1\""\
                        " table:style-name=\"Table1\">\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table1.A\"/>\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table1.B\"/>\n")
        self.file.write("<table:table-column table:style-name=\""
                        "Table1.C\"/>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end_parent_stats(self):
        self.file.write("</table:table>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent_stats(self,str1,str2,str3):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table1.A1\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str1 + \
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table1.A1\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str2 + \
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table1.A2\" table:value-type=\"string\">\n");
        self.file.write("<text:p text:style-name=\"P4\">" + str3 +
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent_parent(self,str1,str2):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table1.A1\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str1 + \
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell ")
        self.file.write("table:style-name=\"Table1.A1\" ")
        self.file.write("table:number-columns-spanned=\"2\" ")
        self.file.write("table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">")
        self.file.write(str2)
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def start_child_stats(self):
        self.file.write("<table:table table:name=\"Table3\" "
                        "table:style-name=\"Table3\">\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table3.A\"/>\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table3.B\"/>\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table3.C\"/>\n")
        self.file.write("<table:table-column table:style-name=\""\
                        "Table3.D\"/>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end_child_stats(self):
        self.file.write("</table:table>\n")
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_stats(self,str1,str2,str3,str4,last):
        self.file.write("<table:table-row>\n")
        if last == 1:
            self.file.write("<table:table-cell table:style-name=\""\
                            "Table3.A2\" table:value-type=\"string\">\n")
        else:
            self.file.write("<table:table-cell table:style-name=\""\
                            "Table3.A1\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str1 +\
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A4\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str2 +
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A4\" table:value-type=\"string\">\n");
        self.file.write("<text:p text:style-name=\"P4\">" + str3 +
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A4\" table:value-type=\"string\">\n");
        self.file.write("<text:p text:style-name=\"P4\">" + str4 +
                        "</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_name(self,index,child):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A3\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">" + str(index))
        if child.getGender() == RelLib.Person.male:
            self.file.write("M")
        else:
            self.file.write("F")
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:number-columns-spanned"\
                        "=\"3\" table:style-name=\""\
                        "Table3.A5\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P2\">")
        self.file.write(child.getPrimaryName().getRegularName())
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_spouse(self,spouse):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A1\" table:value-type=\"string\">\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:style-name=\""\
                        "Table3.A4\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">")
        self.file.write("Spouse")
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell table:number-columns-spanned"\
                        "=\"2\" table:style-name=\""\
                        "Table3.A4\" table:value-type=\"string\">\n")
        self.file.write("<text:p text:style-name=\"P4\">")
        self.file.write(spouse.getPrimaryName().getRegularName())
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell>\n")
        self.file.write("</table:covered-table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        self.write_header()
        self.dump_parent(self.family.getFather())
        self.dump_parent(self.family.getMother())
        if len(self.family.getChildList()) > 0:
            self.file.write("<text:p text:style-name=\"ParentHead\">")
            self.file.write("Children")
            self.file.write("<text:tab-stop/>")
            self.file.write("</text:p>\n")
            index = 1
            for child in self.family.getChildList():
                self.dump_child(index,child)
                index = index + 1
            
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HtmlFamilyGroup(FamilyGroup):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,family,output,template):
        self.map = {}
        self.database = database
        self.family = family
        self.output = output
        self.first = []
        self.last = []
        if template == "":
            template = const.dataDir + os.sep + "family.html"
        self.template = template
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def fix(self,str):
        if str=="":
            return "&nbsp;"
        else:
            return str

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        templateFile = open(self.template,"r")
        lines = templateFile.readlines()
        templateFile.close()
    
        in_last = 0
        for line in lines:
            if line[0:14] == "<!-- START -->":
                in_last = 1
                self.last.append(line);
            elif in_last == 0:
                self.first.append(line)
            else:
                self.last.append(line);

        self.file = open(self.output,"w")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_header(self):
        for line in self.first:
            self.file.write(line)
        self.file.write("<H1>")
        self.file.write("Family Group Record")
        self.file.write("</H1>\n")
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        for line in self.last:
            self.file.write(line)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent(self,type,name):
        self.file.write('<tr>\n')
        self.file.write('<td colspan="3" class="parent_name">')
        self.file.write(type)
        self.file.write(' ')
        self.file.write(name.getPrimaryName().getRegularName())
        self.file.write('</td>\n')
        self.file.write('</tr>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def start_parent_stats(self):
        self.file.write('<table cellspacing="1" width="100%" border="1">\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end_parent_stats(self):
        self.file.write("</table>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent_stats(self,str1,str2,str3):
        self.file.write('<tr>\n')
        self.file.write('<td width="20%">' + self.fix(str1) + '</td>\n')
        self.file.write('<td width="30%">' + self.fix(str2) + '</td>\n')
        self.file.write('<td>' + self.fix(str3) + '</td>\n')
        self.file.write('</tr>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_parent_parent(self,str1,str2):
        self.file.write('<tr>\n')
        self.file.write('<td>' + self.fix(str1) + '</td>\n')
        self.file.write('<td colspan="2" class="child_name">' + self.fix(str2) + '</td>\n')
        self.file.write('</tr>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def start_child_stats(self):
        self.file.write('<table cellspacing="1" width="100%" border="1">\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end_child_stats(self):
        self.file.write("</table>\n")
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_stats(self,str1,str2,str3,str4,last):
        self.file.write('<tr>\n')
        self.file.write('<td width="10%">' + self.fix(str1) + '</td>\n')
        self.file.write('<td width="20%">' + self.fix(str2) + '</td>\n')
        self.file.write('<td width="30%">' + self.fix(str3) + '</td>\n')
        self.file.write('<td>' + self.fix(str4) + '</td>\n')
        self.file.write('</tr>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_name(self,index,child):
        self.file.write("<tr>\n")
        self.file.write("<td>" + str(index))
        if child.getGender() == RelLib.Person.male:
            self.file.write("M")
        else:
            self.file.write("F")
        self.file.write("</td>\n")
        self.file.write("<td colspan=\"3\">")
        self.file.write(child.getPrimaryName().getRegularName())
        self.file.write("</td>\n")
        self.file.write("</tr>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_child_spouse(self,spouse):
        self.file.write("<tr>\n")
        self.file.write("<td>&nbsp;</td>\n")
        self.file.write("<td>Spouse</td>\n")
        self.file.write("<td colspan=\"2\">")
        self.file.write(spouse.getPrimaryName().getRegularName())
        self.file.write("</td>\n")
        self.file.write("</tr>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        self.write_header()
        self.dump_parent(self.family.getFather())
        self.dump_parent(self.family.getMother())
        if len(self.family.getChildList()) > 0:
            self.file.write("<H2>")
            self.file.write("Children")
            self.file.write("</H2>\n")
            index = 1
            for child in self.family.getChildList():
                self.dump_child(index,child)
                index = index + 1
            
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):

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
    
    label.set_text("Family Group chart for " + name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked,
        "on_html_toggled" : on_html_toggled
        })

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

    outputName = topDialog.get_widget("filename").get_text()
    if outputName == "":
        return

    menu = topDialog.get_widget("spouse_menu").get_menu()
    family = menu.get_active().get_data("f")

    if topDialog.get_widget("html").get_active():
        template = topDialog.get_widget("htmlfile").get_text()
        MyReport = HtmlFamilyGroup(db,family,outputName,template)
    else:
        template = const.dataDir + os.sep + "familygrp.sxw"
        MyReport = OpenOfficeFamilyGroup(db,family,outputName,template)

    MyReport.setup()
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Creates a family group report, showing information on "\
           "a set of parents and their children."









