#
# Graph.py - a graphical user interface for gramps
#
# Copyright (C) 2001  Jesper Zedlitz
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

"Graph/Graph"

from RelLib import *
import os
import posixpath
import re
import sort
import string
import Utils
import intl
_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

pixmap = None
sizeX = 20
sizeY = 20
boxes = []
lines = []
treffer = -1
distX = 0
distY = 0
spaceX = 10
spaceY = 40
popup_win = None
popped_up = FALSE
label = None
db = None
select = FALSE
old_selection= (0,0,0,0)
selected_boxes = {}
red_gc = None
lightgreen_gc = None
select_gc = None

sorted = {}
done = {}

# 
# This function is called recursivly to determin the generation a person belongs to
# If nothing is know about the person (i.e. first call to this function) generation #0 is used.
# First the ancestors of a person are followed. If there are no more ancestors (or already visited = entry in 
# map "done") the decendances (if any) are traced.
# The function returns imediately if the person has already been visited -> stop of recursion
#
def calc_gen( person, gen):
    global sorted, done
    
    id =   person.getId()
    if done.has_key(id):
        # stop the recursion
        return
    
    sorted[ id ] = gen
    done[ id ] = TRUE
    
    # going into the past...
    family = person.getMainParents()
    if family != None:
        father = family.getFather()
        mother = family.getMother()
	if( person!=father and person!=mother):
	    # person is a child of this family
	    if father != None:
	        calc_gen( father, gen-1 )
	    if mother != None:
                calc_gen( mother, gen-1 )
    # do I need getFamilyList() when I want to find the parents ?
    for family in person.getFamilyList():
        father = family.getFather()
        mother = family.getMother()
	if( person!=father and person!=mother):
	    # person is a child of this family
	    if father != None:
	        calc_gen( father, gen-1 )
	    if mother != None:
                calc_gen( mother, gen-1 )

    # going into the future...
    for family in person.getFamilyList():
        father = family.getFather()
        mother = family.getMother()
	if( person==father or person==mother):
            # person is a parent of this family
	    if person==father:
	        if mother != None:
		    calc_gen( mother, gen )
	    if person==mother:
	        if father != None:
		    calc_gen( father, gen )
            for child in family.getChildList():
	        calc_gen( child, gen+1 )


def report(database,person):
        global sorted, done
	sorted = {}
	done = {}
	global db
	db = database
	global boxes
	boxes = []
	global lines
	lines = []
        winSizeX = 400
        winSizeY = 400
	global selected_boxes
	selected_boxes = {}

	personList = database.getPersonMap()
	
	# loop over all persons in the database
	# usually a lot of persons will the in "done" after the first call of "calc_gen", but if there are
	# disjunct parts in the database (or completely seperated people) we have to check everyone
	for id in personList.keys():
	    if not done.has_key( id ):
	        calc_gen( personList[id], 0)
        
	# don't want to have negative generation numbers, so have to substract the lowest (negative) number
        mini = min( sorted.values() )

	# position the boxes 
	# this can be done much better - i.e. children should be put close to their parents...
	length = {}
	for id in sorted.keys():
	    y = ( sorted[id]-mini) * (sizeY +spaceY) + 10
	    x = length.get( sorted[id]-mini, 0 ) + spaceX
	    length[ sorted[id]-mini ] = x + sizeX
	    if personList.has_key( id ):
	        pos = personList[id].getPosition()
	        if pos != None:
		    boxes.append( (pos[0], pos[1], (personList[id].getGender() == Person.female), id ) )
		else:
	            boxes.append( (x, y, (personList[id].getGender() == Person.female), id ) )
		    personList[id].setPosition( (x,y) )
		    Utils.modified()
            else:
	        print "just lost person with key %s" % (id)

	# add lines between children and parents
        for i in range( len(boxes) ):
	    b = boxes[i]
	    id = b[3]
	    person = personList[id]
	    family = person.getMainParents()
	    if family != None:
	       father = family.getFather()
	       f=""
	       m=""
	       if father!=None:
	           f = father.getId()
	       mother = family.getMother()
	       if mother!=None:
	           m = mother.getId()
	       for j in range( len(boxes) ):
	          # does this box contain the id of the father or the mother?
	          if boxes[j][3] == f or boxes[j][3] == m:
		     lines.append( (j, i) )

	# logic is done - now the graphic

	win = GtkWindow()
	win.set_name("Test Input")
	win.set_border_width(5)

	vbox = GtkVBox(spacing=3)
	win.add(vbox)
	vbox.show()

	drawing_area = GtkDrawingArea()
	drawing_area.size(winSizeX, winSizeY)
	vbox.pack_start(drawing_area)
	drawing_area.show()
	
	drawing_area.connect("expose_event", expose_event)
	drawing_area.connect("configure_event", configure_event)
	drawing_area.connect("button_press_event", button_press_event)
	drawing_area.connect("button_release_event", button_release_event)
	drawing_area.connect("motion_notify_event", motion_notify_event)
	drawing_area.set_events(GDK.EXPOSURE_MASK |
				GDK.LEAVE_NOTIFY_MASK |
				GDK.BUTTON_PRESS_MASK |
				GDK.BUTTON_RELEASE_MASK |
				GDK.POINTER_MOTION_MASK |
				GDK.POINTER_MOTION_HINT_MASK)

	button = GtkButton(_("Quit"))
	hbox = GtkHBox(spacing=3)
	vbox.pack_start(button, expand=FALSE, fill=FALSE)
	button.connect("clicked", win.destroy)
	button.show()
	win.show()
	drawing_area.get_window().set_cursor(cursor_new(132))

def redraw_tree( widget, area = None ):
    global pixmap
    global red_gc, select_gc, lightgreen_gc
    if area == None:
        draw_rectangle(pixmap, widget.get_style().white_gc, TRUE, 0, 0, widget.get_window().width, widget.get_window().height)
    else:
        draw_rectangle(pixmap, widget.get_style().white_gc, TRUE, area[0], area[1], area[2], area[3])

    for i in range( len( boxes) ):
        b = boxes[i]
        if selected_boxes.has_key(i):
            draw_rectangle(pixmap, lightgreen_gc, TRUE, b[0], b[1], sizeX, sizeY)
        draw_rectangle(pixmap, widget.get_style().black_gc, FALSE, b[0], b[1], sizeX, sizeY)

    for l in lines:
        p1 = boxes[l[0]]
        p2 = boxes[l[1]]
        draw_line( pixmap, red_gc, p1[0]+sizeX/2, p1[1]+sizeY, p2[0]+sizeX/2, p2[1] )
    draw_rectangle(pixmap, select_gc, FALSE, old_selection[0], old_selection[1], old_selection[2], old_selection[3])
    widget.queue_draw()

def configure_event(widget, event):
	global pixmap
	global red_gc, select_gc, lightgreen_gc
	win = widget.get_window()
	pixmap = create_pixmap(win, win.width, win.height, -1)

	cm = widget.get_style().colormap
	if( red_gc == None ):
	    red_gc = win.new_gc()
	    red_gc.foreground = cm.alloc( 60000,0,0)
	if( lightgreen_gc == None ):
	    lightgreen_gc = win.new_gc()
	    lightgreen_gc.foreground = cm.alloc( 0,60000,0)
	if( select_gc == None ):
	    select_gc = win.new_gc()
	    select_gc.foreground = cm.alloc( 10000,10000,10000)
	    select_gc.line_style = 1

	redraw_tree( widget )
	return TRUE

def expose_event(widget, event):
	area = event.area
	gc = widget.get_style().fg_gc[STATE_NORMAL]
	widget.draw_pixmap(gc, pixmap, area[0], area[1], area[0], area[1],
			   area[2], area[3])
	return FALSE

#
#  close the popup-window for one person
#  it's not nice that the window closes imediately after leaving the window - a timer should be added here
#
def popdown_cb(widget, event):
	global popped_up
	global popup_win
	widget.hide()
	popped_up = FALSE
	return FALSE

def button_press_event(widget, event):
    global treffer
    global distY, distX
    global popped_up, popup_win, label
    global selX, selY, select, old_selection, selected_boxes
    state = event.window.pointer_state
    
    # which box has been hit?
    i = 0
    for b in boxes:
        if( b[0]<=event.x<=b[0]+sizeX and b[1]<=event.y<=b[1]+sizeY):
            treffer=i
	    distX = event.x - b[0]
	    distY = event.y - b[1]
        i=i+1

    # left mouse button -> drag 'n drop
    if (treffer > -1) and (state & GDK.BUTTON1_MASK):
        if not selected_boxes.has_key(treffer):
	    old_selection = (0,0,0,0)
            selected_boxes = { }
	    selected_boxes[treffer] = TRUE
        widget.get_window().set_cursor(cursor_new(58))

    # add a box to the current selection
    # this should be changes to work with BUTTON1 + CTRL
    if treffer>-1 and (state & GDK.BUTTON2_MASK):
        if not selected_boxes.has_key(treffer):
	    old_selection = (0,0,0,0)
	    selected_boxes[treffer] = TRUE
	treffer = -1

    # left mouse button outside a box -> selection
    if treffer==-1 and (state & GDK.BUTTON1_MASK):
        widget.get_window().set_cursor(cursor_new(30))
	select = TRUE
	old_selection = ( event.x, event.y, 0,0)
    
    # right mouse button -> infobox
    if (treffer > -1) and (state & GDK.BUTTON3_MASK) :
	if not popped_up:
		if not popup_win:
		    popup_win = GtkWindow(WINDOW_POPUP)
		    popup_win.set_position(WIN_POS_MOUSE)
		    popup_win.set_border_width(5)
		    label = GtkLabel("%s"% boxes[treffer][3])
		    label.show()
		    popup_win.add(label)
		    popup_win.connect("leave_notify_event", popdown_cb)
		person = db.findPersonNoMap(boxes[treffer][3])
		label.set_text( person.getPrimaryName().getName())
		popup_win.show()
		popped_up = TRUE
	treffer=-1
    redraw_tree( widget )
    return TRUE

#
#  returns a map of numbers
#  boxes is the map of all boxes - I could have used the global variable here...
#  "old_selection" has the following form: ( position x, position y, width, height )
#
def boxes_in_selection( boxes, old_selection ):
    global sizeY, sizeX
    res = {}
    for i in range( len(boxes) ):
        b = boxes[i]
        if( old_selection[0]<=b[0]<=old_selection[0]+old_selection[2]-sizeX  and   old_selection[1]<=b[1]<=old_selection[1]+old_selection[3]-sizeY):
	    res[i] = TRUE
    return res

def button_release_event(widget, event):
    global treffer
    global distY, distX
    global sizeY, sizeX
    global selX, selY, select, old_selection, selected_boxes
    state = event.state

    # draw a selection
    if select and (state & GDK.BUTTON1_MASK):
        select = FALSE
 	widget.get_window().set_cursor(cursor_new(132))
	selected_boxes = boxes_in_selection(boxes, old_selection)
        old_selection = (0,0,0,0)

    # drag n' drop
    if (treffer > -1) and (state & GDK.BUTTON1_MASK):
        treffer=-1
	widget.get_window().set_cursor(cursor_new(132))
	for k in selected_boxes.keys():
	        b = boxes[k]
 		id = b[3]
		person = db.findPersonNoMap(id)
		person.setPosition( (b[0], b[1]) )
                Utils.modified()
    redraw_tree( widget )
    return TRUE
    
def motion_notify_event(widget, event):
    global old_selection, selected_boxes, treffer
    global distY, distX
    state = event.window.pointer_state
    if select and (state & GDK.BUTTON1_MASK):
	old_selection = ( old_selection[0], old_selection[1], event.x-old_selection[0], event.y-old_selection[1] )
	selected_boxes = boxes_in_selection(boxes, old_selection)
        redraw_tree( widget)
	
    if (treffer > -1) and (state & GDK.BUTTON1_MASK):
        posX = event.x - distX
	posY = event.y - distY
	distance = ( posX-boxes[treffer][0], posY-boxes[treffer][1] )
	old_selection = (0,0,0,0)
	for k in selected_boxes.keys():
	        b = boxes[k]
 		boxes.pop(k)
		boxes.insert( k, (b[0]+distance[0], b[1]+distance[1], b[2], b[3]) )
        redraw_tree( widget)
    return TRUE
