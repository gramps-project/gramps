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

"Generate files/Ancestor Chart"

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
class AncestorChart:

    points = [
        # X    , Y         , Xold+3,Yold(+1.4),       Y+.7
        ( "1.5", "13.2700" ,     ""         "",        ""),
        ( "5.5",  "6.6600" ,  "4.5", "13.2700",  "7.3600"),
        ( "5.5", "19.8800" ,  "4.5", "14.6700", "20.5800"),
        ( "9.5",  "3.3550" ,  "8.5",  "6.6600",  "4.0550"),
        ( "9.5",  "9.9650" ,  "8.5",  "8.0600", "10.6650"),
        ( "9.5", "16.5750" ,  "8.5", "19.8800", "17.2750"),
        ( "9.5", "23.1850" ,  "8.5", "21.2800", "23.8850"),
        ("13.5",  "1.7025" , "12.5",  "3.3550",  "2.4025"),
        ("13.5",  "5.0075" , "12.5",  "4.7550",  "5.7075"),
        ("13.5",  "8.3125" , "12.5",  "9.9650",  "9.0125"),
        ("13.5", "11.6175" , "12.5", "11.3650", "12.3175"),
        ("13.5", "14.9225" , "12.5", "16.5750", "15.6225"),
        ("13.5", "18.2275" , "12.5", "17.9750", "18.9275"),
        ("13.5", "21.5325" , "12.5", "23.1850", "22.2325"),
        ("13.5", "24.8375" , "12.5", "24.5850", "25.5375")
        ]
    
    def __init__(self,database,person,output,template, max):
        creator = database.getResearcher().getName()
        self.open_office = OpenOffice.OpenOfficeCore(output,template,".sxd",creator)
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        
    def setup(self):
        self.file = self.open_office.setup()
        
    def end(self):
        self.open_office.end()

    def filter(self,person,index):
        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person
    
        family = person.getMainFamily()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    def write_report(self):

        self.filter(self.start,1)
        
        generation = 0
        need_header = 1

        generation = 1
        done = 0
        page = 1
        while done == 0:
            done = 1
            start = 2**(generation-1)
            for index in range(start, (start*2)):
                values = []
                self.get_numbers(index,1,values)
                if len(values) > 1 or generation == 1:
                    done = 0
                    self.print_page(index, generation, page)
                    page = page + 1
            generation = generation + 3
            
    def get_numbers(self,start,index,vals):
        if index > 4:
            return
        if self.map.has_key(start):
            vals.append(start)
        self.get_numbers(start*2,index+1,vals)
        self.get_numbers((start*2)+1,index+1,vals)

    def print_page(self,start,generation, page):
        self.file.write("<draw:page draw:name=\"")
        self.file.write("Generation %d, page %d\" " % (generation, page))
        self.file.write("draw:style-name=\"P0\" draw:master-page-name=\"Home\">")

        self.draw_graph(1,start,0)

        self.file.write("</draw:page>\n")

    def draw_graph(self,index,start,level):
        if self.map.has_key(start) and index <= 15:
            person = self.map[start]
            myPoints = AncestorChart.points[index-1]
            self.file.write("<draw:rect draw:style-name=\"gr1\" svg:x=\"" + myPoints[0])
            self.file.write("cm\" svg:y=\"" + myPoints[1] + "cm\" svg:width=\"5.5cm\"")
            self.file.write(" svg:height=\"1.4cm\">\n")

            self.file.write("<text:p text:style-name=\"P1\">")
            self.file.write("<text:span text:style-name=\"T1\">")
            self.file.write(person.getPrimaryName().getRegularName())
            self.file.write("</text:span></text:p>\n");

            birth = person.getBirth()
            if birth and birth.getDate() != "":
                self.file.write("<text:p text:style-name=\"P1\">")
                self.file.write("<text:span text:style-name=\"T1\">b. ")
                self.file.write(birth.getDate())
                self.file.write("</text:span></text:p>\n");

            death = person.getDeath()
            if death and death.getDate() != "":
                self.file.write("<text:p text:style-name=\"P1\">")
                self.file.write("<text:span text:style-name=\"T1\">d. ")
                self.file.write(death.getDate())
                self.file.write("</text:span></text:p>\n");
                    
            self.file.write("</draw:rect>\n")
            if myPoints[2] != "":
                self.file.write("<draw:line draw:style-name=\"gr3\" ")
                self.file.write("svg:x1=\"" + myPoints[2] + "cm\" svg:y1=\"")
                self.file.write(myPoints[3] + "cm\" svg:x2=\"")
                self.file.write(myPoints[2] + "cm\" svg:y2=\"" + myPoints[4] + "cm\">\n")
                self.file.write("<text:p text:style-name=\"P2\"/>\n")
                self.file.write("</draw:line>\n");

                self.file.write("<draw:line draw:style-name=\"gr3\" ")
                self.file.write("svg:x1=\"" + myPoints[2] + "cm\" svg:y1=\"")
                self.file.write(myPoints[4] + "cm\" svg:x2=\"")
                self.file.write(myPoints[0] + "cm\" svg:y2=\"" + myPoints[4] + "cm\">\n")
                self.file.write("<text:p text:style-name=\"P2\"/>\n")
                self.file.write("</draw:line>\n");

            self.draw_graph(index*2,start*2,level+1)
            self.draw_graph((index*2)+1,(start*2)+1,level+1)
        
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
    glade_file = base + os.sep + "ancestorchart.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()
    
    topDialog.get_widget("labelTitle").set_text("Ancestor chart for " + name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked
        })

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
    
    if outputName[-4:] != ".sxd":
        outputName = outputName + ".sxd"
        
    max_gen = topDialog.get_widget("generations").get_value_as_int()
    
    template = const.dataDir + os.sep + "chart.sxd"
    MyReport = AncestorChart(db,active_person,outputName,template, max_gen)

    MyReport.setup()
    MyReport.write_report()
    MyReport.end()

    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Produces a graphical ancestral tree graph"
        
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
        "       +....................@@@@@@......+       ",
        "       +.................@@@@@@@@@......+       ",
        "       +.................@..............+       ",
        "       +.............@@@@@@.............+       ",
        "       +...........@@@@@@@@.............+       ",
        "       +...........@.....@..............+       ",
        "       +...........@.....@@@@@@@@@......+       ",
        "       +...........@........@@@@@@......+       ",
        "       +.......@@@@@@...................+       ",
        "       +.....@@@@@@@@...................+       ",
        "       +.....@.....@........@@@@@@......+       ",
        "       +.....@.....@.....@@@@@@@@@......+       ",
        "       +.....@.....@.....@..............+       ",
        "       +.....@.....@@@@@@@@.............+       ",
        "       +.....@.......@@@@@@.............+       ",
        "       +.....@...........@..............+       ",
        "       +.....@...........@@@@@@@@@......+       ",
        "       +.....@..............@@@@@@......+       ",
        "       +.@@@@@@.........................+       ",
        "       +.@@@@@@.........................+       ",
        "       +.....@..............@@@@@@......+       ",
        "       +.....@...........@@@@@@@@@......+       ",
        "       +.....@...........@..............+       ",
        "       +.....@.......@@@@@@.............+       ",
        "       +.....@.....@@@@@@@@.............+       ",
        "       +.....@.....@.....@..............+       ",
        "       +.....@.....@.....@@@@@@@@@......+       ",
        "       +.....@.....@........@@@@@@......+       ",
        "       +.....@@@@@@@@...................+       ",
        "       +.......@@@@@@...................+       ",
        "       +...........@........@@@@@@......+       ",
        "       +...........@.....@@@@@@@@@......+       ",
        "       +...........@.....@..............+       ",
        "       +...........@@@@@@@@.............+       ",
        "       +.............@@@@@@.............+       ",
        "       +.................@..............+       ",
        "       +.................@@@@@@@@@......+       ",
        "       +....................@@@@@@......+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]









