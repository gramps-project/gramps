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

"View/View an ancestor graph"


import RelLib
import os
import utils

from gtk import *
from gnome.ui import *
from libglade import *

import intl
_ = intl.gettext

col2person = {}
reportPerson = None
zoom = 1.0
boxwidth = 200
boxheight = 50
colsep = 30
shadow_offset = 5
topDialog = None

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def report(database,active_person):
    global glade_file
    global col2person
    global zoom
    global reportPerson
    global topDialog

    zoom = 1.0
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "ancestorgraph.glade"

    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked,
        "on_personList_select_row" : on_personList_select_row
        }

    topDialog = GladeXML(glade_file,"graph")
    topDialog.signal_autoconnect(dic)
    
    top = topDialog.get_widget("graph")
    topDialog.get_widget("backgroundcolor").set_i8(255,255,255,0)
    topDialog.get_widget("boxcolor").set_i8(255,255,255,0)
    topDialog.get_widget("textcolor").set_i8(0,0,0,0)
    topDialog.get_widget("bordercolor").set_i8(0,0,0,0)

    personList = topDialog.get_widget("personList")

    nameList = database.getPersonMap().values()
    nameList.sort(mysort)

    reportPerson = active_person
    if active_person != None:
        name = active_person.getPrimaryName().getName()
        topDialog.get_widget("selectedPerson").set_text(name)

    col2person = {}
    index = 0

    for person in nameList:
		
        name = person.getPrimaryName().getName()
        birth = person.getBirth()
        if birth != None:
            bdate = birth.getDate()
        else:
            bdate = ""

        personList.append([name,bdate])
        col2person[index] = person
        index = index + 1

    top.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_personList_select_row(obj,a,b,c):
    global reportPerson
    global col2person
    global topDialog
    
    reportPerson = col2person[a]
    name = reportPerson.getPrimaryName().getName()
    topDialog.get_widget("selectedPerson").set_text(name)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global reportPerson
    global colsep
    global boxwidth
    global shadow_offset
    global glade_file
    global topDialog

    if reportPerson == None:
        return

    req_depth = topDialog.get_widget("generations").get_value_as_int()
    font = topDialog.get_widget("fontpicker").get_font_name()

    dic = { "destroy_passed_object" : utils.destroy_passed_object,
            "on_zoomin_clicked" : on_zoomin_clicked,
            "on_zoomout_clicked" : on_zoomout_clicked
          }
    window = GladeXML(glade_file,"display")
    window.signal_autoconnect(dic)
    displayWindow = window.get_widget("display")
    canvas = window.get_widget("canvas")
    rootGroup = canvas.root()

    max_depth = min(determine_depth(reportPerson,0)+1,req_depth)

    max_size = (2 ** (max_depth-1)) * (boxheight+colsep+shadow_offset)

    x_size = (boxwidth + colsep + shadow_offset) * (max_depth)
    x_size = x_size + 3 * shadow_offset
    y_size = max_size + (2*boxheight)

    canvas.set_usize(x_size, y_size)
    canvas.set_scroll_region(0, 0,x_size, y_size)

#    bkgclr = topDialog.get_widget("backgroundcolor").get_i8()
#    txtclr = topDialog.get_widget("textcolor").get_i8()
#    bdrclr = topDialog.get_widget("bordercolor").get_i8()
#    boxclr = topDialog.get_widget("boxcolor").get_i8()

#    bkgcolor = GdkColor(bkgclr[0],bkgclr[1],bkgclr[2])
#    txtcolor = GdkColor(txtclr[0],txtclr[1],txtclr[2])
#    bdrcolor = GdkColor(bdrclr[0],bdrclr[1],bdrclr[2])
#    boxcolor = GdkColor(boxclr[0],boxclr[1],boxclr[2])

    bkgcolor = "white"
    txtcolor = "black"
    bdrcolor = "black"
    boxcolor = "white"

    border = rootGroup.add("rect",
                           x1=0,
                           y1=0,
                           x2=x_size,
                           y2=y_size,
                           fill_color=bkgcolor,
                           outline_color=txtcolor)

    draw(rootGroup,
         reportPerson,
         colsep,
         (max_size+boxheight+shadow_offset)/2.0,
         max_size/4.0,
         1,
         max_depth,
         boxcolor,
         txtcolor,
         bdrcolor,
         font)
    displayWindow.show()

    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# determine_depth
#
#-------------------------------------------------------------------------
def determine_depth(person, depth):

    family = person.getMainFamily()
    if family == None:
        return depth

    father = family.getFather()
    mother = family.getMother()
    father_depth = 0
    mother_depth = 0
    
    if father != None:
        father_depth = determine_depth(father,depth+1)
    if mother != None:    
        mother_depth = determine_depth(mother,depth+1)

    if father_depth > mother_depth:
        return father_depth
    else:
        return mother_depth

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_zoomin_clicked(obj):
    global zoom
    
    zoom = zoom * 1.5
    obj.set_pixels_per_unit(zoom)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_zoomout_clicked(obj):
    global zoom
    
    zoom = zoom * (2.0/3.0)
    obj.set_pixels_per_unit(zoom)


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def line(group,x1,y1,x2,y2):
    global colsep
    
    pts = []
    pts.append(x1)
    pts.append(y1)
    pts.append(x1+(colsep/2.0))
    pts.append(y1)
    pts.append(x1+(colsep/2.0))
    pts.append(y2)
    pts.append(x2)
    pts.append(y2)
    group.add("line", points=pts, fill_color="black")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def draw(group,reportPerson,x,y,incr,cur_depth,max_depth,bkg,txt,bdr,font):
    global boxwidth
    global colsep
    global shadow_offset
    
    name = reportPerson.getPrimaryName().getName()
    family = reportPerson.getMainFamily()

    add_box(group,name,x,y,bkg,txt,bdr,font)
    if family != None and cur_depth < max_depth:
        father = family.getFather()
        if father != None:
            line(group,
                 x+boxwidth+shadow_offset,
                 y+(boxheight/2.0),
                 x+boxwidth+colsep,
                 y-incr+(boxheight/2.0))
            
            draw(group,
                 father,
                 x+boxwidth+colsep,
                 y-incr,
                 incr/2.0,
                 cur_depth+1,
                 max_depth,
                 bkg,
                 txt,
                 bdr,
                 font)
            
        mother = family.getMother()
        if mother != None:
            line(group,
                 x+boxwidth+shadow_offset,
                 y+(boxheight/2.0),
                 x+boxwidth+colsep,
                 y+incr+(boxheight/2.0))

            draw(group,
                 mother,
                 x+boxwidth+colsep,
                 y+incr,
                 incr/2.0,
                 cur_depth+1,
                 max_depth,
                 bkg,
                 txt,
                 bdr,
                 font)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def add_box(parentgroup,mytext, x1, y1,bkg,txt,bdr,font):
    global boxheight
    global boxwidth
    global colsep
    global shadow_offset

    pad = 3
    
    group = parentgroup.add("group",x=x1,y=y1);
    shadow = group.add("rect");
    border = group.add("rect");

    text = group.add("text",
                     text=mytext,
                     font=font,
                     x=pad,
                     y=boxheight/2.0,
                     fill_color=txt,
                     anchor=ANCHOR_WEST)
    
    border.set(x1=0,
               y1=0,
               x2=boxwidth+pad, 
               y2=boxheight,
               fill_color=bkg,
               outline_color=bdr)

    shadow.set(x1=shadow_offset,
               y1=shadow_offset,
               x2=boxwidth+pad+shadow_offset, 
               y2=boxheight+shadow_offset,
               fill_color="gray",
               outline_color="gray")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def mysort(first, second) :
    name1 = first.getPrimaryName()
    name2 = second.getPrimaryName()
    
    if name1.getSurname() == name2.getSurname():
        if name1.getFirstName() == name2.getFirstName():
            return cmp(name1.getSuffix(), name2.getSuffix())
        else:
            return cmp(name1.getFirstName(), name2.getFirstName())
    else:
        return cmp(name1.getSurname(), name2.getSurname())

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Produces a graphical ancestral tree graph")

def get_name():
    return _("View/View an ancestor graph")

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

