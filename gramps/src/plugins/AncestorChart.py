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

from TextDoc import *
from DrawDoc import *
from OpenDrawDoc import *

from gtk import *
from gnome.ui import *
from libglade import *

import intl
_ = intl.gettext

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

    def __init__(self,database,person,output,doc, max):
        self.doc = doc
        self.doc.creator(database.getResearcher().getName())
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.output = output
        self.width = 4.5
        self.height = 1.25

        start = self.doc.get_right_margin()
        delta = self.doc.get_usable_width() - (self.width + 0.5)
        delta = delta/3.0
        uh = self.doc.get_usable_height()
        ystart = self.doc.get_top_margin() - ((self.height+0.3)/2.0)
        self.x = [start, start + delta, start + (2*delta), start + (3*delta)]
        self.y = [ ystart + (uh/2.0),   ystart + (uh/4.0),
                   ystart + 3*(uh/4.0), ystart + (uh/8.0),
                   ystart + 3*(uh/8.0), ystart + 5*(uh/8.0),
                   ystart + 7*(uh/8.0), 
                   ystart + (uh/16.0),   ystart + 3*(uh/16.0),
                   ystart + 5*(uh/16.0), ystart + 7*(uh/16.0),
                   ystart + 9*(uh/16.0), ystart + 11*(uh/16.0),
                   ystart + 13*(uh/16.0), ystart + 15*(uh/16.0)]

    def setup(self):
        f = FontStyle()
        f.set_size(9)
        f.set_type_face(FONT_SANS_SERIF)
        p = ParagraphStyle()
        p.set_font(f)
        self.doc.add_paragraph_style("Normal",p)
        
        g = GraphicsStyle()
        g.set_height(self.height)
        g.set_width(self.width)
        g.set_paragraph_style("Normal")
        g.set_shadow(1)
        self.doc.add_draw_style("box",g)

        g = GraphicsStyle()
        self.doc.add_draw_style("line",g)

        self.doc.open(self.output)
        
    def end(self):
        self.doc.close()

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
        self.doc.start_page()
        self.draw_graph(1,start,0)
        self.doc.end_page()

    def draw_graph(self,index,start,level):
        if self.map.has_key(start) and index <= 15:
            person = self.map[start]
            name = person.getPrimaryName().getRegularName()

            birth = person.getBirth()
            if birth and birth.getDate() != "":
                name = name + "\nb. " + birth.getDate()

            death = person.getDeath()
            if death and death.getDate() != "":
                name = name + "\nd. " + death.getDate()

            self.doc.draw_box("box",name,self.x[level],self.y[index-1])
            if index > 1:
                old_index = int(index/2)-1
                x1 = self.x[level-1]+(self.width/2.0)
                x2 = self.x[level]
                if index % 2 == 1:
                    y1 = self.y[old_index]+self.height
                else:
                    y1 = self.y[old_index]
                y2 = self.y[index-1]+(self.height/2.0)
                self.doc.draw_line("line",x1,y1,x1,y2)
                self.doc.draw_line("line",x1,y2,x2,y2)
            self.draw_graph(index*2,start*2,level+1)
            self.draw_graph((index*2)+1,(start*2)+1,level+1)
        
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
    glade_file = base + os.sep + "ancestorchart.glade"
    topDialog = GladeXML(glade_file,"dialog1")

    name = person.getPrimaryName().getRegularName()

    PaperMenu.make_paper_menu(topDialog.get_widget("papersize"))
    PaperMenu.make_orientation_menu(topDialog.get_widget("orientation"))

    title = _("Ancestor chart for %s") % name
    topDialog.get_widget("labelTitle").set_text(title)
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

    outputName = topDialog.get_widget("fileentry1").get_full_path(0)
    if outputName == "":
        return
    
    paper_obj = topDialog.get_widget("papersize").get_menu().get_active()
    paper = paper_obj.get_data("i")
    orien_obj = topDialog.get_widget("orientation").get_menu().get_active()
    orien = orien_obj.get_data("i")
        
    max_gen = topDialog.get_widget("generations").get_value_as_int()

    document = OpenDrawDoc(paper,orien)

    MyReport = AncestorChart(db,active_person,outputName,document, max_gen)

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
    return _("Produces a graphical ancestral tree graph")


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_name():
    return _("Generate files/Ancestor Chart")
        
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









