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

import OpenOffice

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

    def __init__(self,database,family,output,template):
        pass
    
    def setup(self):
        return 1
    
    def end(self):
        pass
    
    def write_header(self):
        pass
    
    def write_trailer(self):
        pass
    
    def write_report(self):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class OpenOfficeIndivSummary(IndivSummary):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,template):
        c = database.getResearcher().getName()
        self.open_office = OpenOffice.OpenOfficeCore(output,template,".sxw",c)
        
        self.map = {}
        self.database = database
        self.person = person
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.file = self.open_office.setup()
        return 1

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
        self.file.write('Summary of ')
        self.file.write(self.person.getPrimaryName().getRegularName())
        self.file.write('</text:h>\n')

        if self.image != "":
            width = 46.0 * self.scale
            self.file.write('<text:p text:style-name="Text body"/>')
            self.file.write('<text:p text:style-name="Text body">')
            self.file.write('<draw:image draw:style-name="Individual Photo" ')
            self.file.write('draw:name="')
            self.file.write(self.person.getPrimaryName().getRegularName())
            self.file.write('" text:anchor-type=')
            self.file.write('"paragraph" svg:y="0mm" svg:height="46mm" ')
            val = "%6.2f" % width
            self.file.write('svg:width=' + string.strip('"%6.2fmm"' % width))
            self.file.write(' draw:z-index="0" xlink:href="#Pictures/')
            self.file.write(self.image)
            self.file.write('" xlink:type="simple" xlink:show="embed" ')
            self.file.write('xlink:actuate="onLoad"/>\n')
            self.file.write('</text:p>\n')
            
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_simple_row(self,field1,field2):
        self.file.write("<table:table-row>\n")
        self.file.write("<table:table-cell ")
        self.file.write("table:value-type=\"string\">\n")
        self.file.write('<text:p text:style-name="Table Contents">')
        self.file.write(field1)
        self.file.write('</text:p>\n')
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:table-cell ")
        self.file.write("table:value-type=\"string\">\n")
        self.file.write('<text:p text:style-name="Table Contents">')
        self.file.write(field2)
        self.file.write("</text:p>\n")
        self.file.write("</table:table-cell>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_header_row(self,field1):
        self.file.write('<table:table-row>\n')
        self.file.write('<table:table-cell ')
        self.file.write('table:number-columns-spanned="2" ')
        self.file.write('table:value-type=\"string\">\n')
        self.file.write('<text:p text:style-name="P1">')
        self.file.write(field1)
        self.file.write('</text:p>\n')
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell/>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_spouse(self,person):
        if person:
            name = person.getPrimaryName().getRegularName()
        else:
            name = "unknown"
        self.file.write('<table:table-row>\n')
        self.file.write('<table:table-cell ')
        self.file.write('table:number-columns-spanned="2" ')
        self.file.write('table:value-type=\"string\">\n')
        self.file.write('<text:p text:style-name="P2">')
        self.file.write(name)
        self.file.write('</text:p>\n')
        self.file.write("</table:table-cell>\n")
        self.file.write("<table:covered-table-cell/>\n")
        self.file.write("</table:table-row>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_general(self):

        self.file.write('<table:table table:name="Table1" table:style-name="Table1">\n')
        self.file.write('<table:table-column table:style-name="Table1.A"/>\n')
        self.file.write('<table:table-column table:style-name="Table1.B"/>\n')

        name = self.person.getPrimaryName().getRegularName()
        self.write_simple_row("Name:",name)
        if self.person.getGender() == RelLib.Person.male:
            self.write_simple_row("Gender:","Male")
        else:
            self.write_simple_row("Gender:","Female")
        family = self.person.getMainFamily()
        if family:
            father = family.getFather().getPrimaryName().getRegularName()
            mother = family.getMother().getPrimaryName().getRegularName()
        else:
            father = ""
            mother = ""
        self.write_simple_row("Father:",father)
        self.write_simple_row("Mother:",mother)
            
        self.file.write('</table:table>\n')

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
                self.write_simple_row(name,place + ". " + description)
        else:
            if place == "":
                self.write_simple_row(name,date + ". " + description)
            else:
                self.write_simple_row(name,date + " in " + place + ". " + \
                                      description)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_facts(self):

        self.file.write('<text:p text:style-name="Standard"/>')
        self.file.write('<table:table table:name="Table2" table:style-name="Table1">\n')
        self.file.write('<table:table-column table:style-name="Table1.A"/>\n')
        self.file.write('<table:table-column table:style-name="Table1.B"/>\n')

        self.write_header_row("Individual Facts")
        event_list = [ self.person.getBirth(), self.person.getDeath() ]
        event_list = event_list + self.person.getEventList()
        
        for event in event_list:
            self.write_fact(event)

        self.file.write('</table:table>\n')


    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):

        self.file.write('<text:p text:style-name="Standard"/>')
        self.file.write('<table:table table:name="Table2" table:style-name="Table1">\n')
        self.file.write('<table:table-column table:style-name="Table1.A"/>\n')
        self.file.write('<table:table-column table:style-name="Table1.B"/>\n')

        self.write_header_row("Marriages/Children")
        for family in self.person.getFamilyList():
            if self.person == family.getFather():
                self.write_spouse(family.getMother())
            else:
                self.write_spouse(family.getFather())
            event_list = [ family.getMarriage(), family.getDivorce() ]
            event_list = event_list + family.getEventList()
            for event in event_list:
                self.write_fact(event)
            child_list = family.getChildList()
            if len(child_list) > 0:
                self.file.write("<table:table-row>\n")
                self.file.write("<table:table-cell ")
                self.file.write("table:value-type=\"string\">\n")
                self.file.write('<text:p text:style-name="Table Contents">')
                self.file.write('Children')
                self.file.write('</text:p>\n')
                self.file.write("</table:table-cell>\n")
                self.file.write("<table:table-cell ")
                self.file.write("table:value-type=\"string\">\n")
                
                self.file.write('<text:p text:style-name="Table Contents">')
                first = 1
                for child in family.getChildList():
                    if first == 1:
                        first = 0
                    else:
                        self.file.write('<text:line-break/>')
                    self.file.write(child.getPrimaryName().getRegularName())
                self.file.write('</text:p>\n')
                self.file.write("</table:table-cell>\n")
                self.file.write("</table:table-row>\n")
        self.file.write('</table:table>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        photo_list = self.person.getPhotoList()
        if len(photo_list) > 0:
            import GdkImlib
            file = photo_list[0].getPath()
            image = GdkImlib.Image(file)
            height = image.rgb_height
            scale = float(height)/150.0
            width = int(image.rgb_width * scale)
            height = int(height * scale)
            base = os.path.basename(file)
            image_name = self.open_office.add_image(base)
            cmd = const.convert + " -size " + str(width) + "x150 "\
                  + file + " " + image_name
            os.system(cmd)
            self.scale = float(height)/float(width)
            self.image = base
        else:
            self.image = ""
            
        self.write_header()
        self.write_general()
        self.write_facts()
        self.write_families()
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HtmlIndivSummary(IndivSummary):

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

        if in_last == 0:
            GnomeErrorDialog("HTML template did not have a START comment")
            return 0

        self.file = open(self.output,"w")
        return 1

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
    def write_trailer(self):
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
            
        self.write_trailer()
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
    glade_file = base + os.sep + "indsum.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()
    label = topDialog.get_widget("labelTitle")
    
    label.set_text("Individual Summary for " + name)
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

    outputName = topDialog.get_widget("filename").get_text()
    if outputName == "":
        return

    if topDialog.get_widget("html").get_active():
        template = topDialog.get_widget("htmlfile").get_text()
        MyReport = HtmlIndivSummary(db,family,outputName,template)
    else:
        template = const.dataDir + os.sep + "indsum.sxw"
        MyReport = OpenOfficeIndivSummary(db,active_person,outputName,template)

    if MyReport.setup() == 0:
        return
    
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









