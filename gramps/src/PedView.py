#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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

_PAD       = 3
_CANVASPAD = 20
_PERSON    = "p"

import GTK
import GDK
import gtk

import GrampsCfg

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class PedigreeView:
    def __init__(self,canvas,update,status_bar,change_active,lp):
        self.canvas = canvas
        self.canvas_items = []
        self.root = self.canvas.root()
        self.active_person = None
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.update = update
        self.sb = status_bar
        self.change_active_person = change_active
        self.load_person = lp
        self.presel_descendants = []

    def load_canvas(self,person):
        """Redraws the pedigree view window, using the passed person
           as the root person of the tree."""

        for i in self.canvas_items:
            i.destroy()

        if person is not self.active_person:
            del self.presel_descendants[:]
            self.active_person = person
        if person == None:
            return

        h = 0
        w = 0

        x1,y1,x2,y2 = self.canvas.get_allocation()
        self.canvas.set_scroll_region(x1,y1,x2,y2)
        
        style = self.canvas['style']
        font = style.font

        list = [None]*31
        self.find_tree(self.active_person,0,1,list)

	# determine the largest string width and height for calcuation
        # of box sizes.

        for t in list:
            if t:
                n = t[0].getPrimaryName().getName()
                h = max(h,font.height(n)+2*_PAD)
                w = max(w,font.width(n)+2*_PAD)
                w = max(w,font.width("d. %s" % t[0].getDeath().getDate())+2*_PAD)
                w = max(w,font.width("b. %s" % t[0].getBirth().getDate())+2*_PAD)

        cpad = max(h+4,_CANVASPAD)
        cw = (x2-x1-(2*cpad))
        ch = (y2-y1-(2*cpad))

        if 5*w < cw and 24*h < ch:
            gen = 31
            xdiv = 5.0
        elif 4*w < cw and 12*h < ch:
            gen = 15
            xdiv = 4.0
        else:
            gen = 7
            xdiv = 3.0

        xpts = self.build_x_coords(cw/xdiv,cpad)
        ypts = self.build_y_coords((ch - h)/32.0, h)

        for family in self.active_person.getFamilyList():
            if len(family.getChildList()) > 0:
                button,arrow = self.make_arrow_button(GTK.ARROW_LEFT,
                                                      self.on_show_child_menu)
                item = self.root.add("widget", widget=button,
                                     x=x1, y=ypts[0]+(h/2.0), 
                                     height=h, width=h,
                                     size_pixels=1, anchor=GTK.ANCHOR_WEST)
                self.canvas_items = [item, button, arrow]
                break
        else:
            self.canvas_items = []

        if list[1]:
            p = list[1]
            self.add_parent_button(p[0],x2-_PAD,ypts[1],h)
        
        if list[2]:
            p = list[2]
            self.add_parent_button(p[0],x2-_PAD,ypts[2],h)

        gen_no = len(self.presel_descendants) + 1
        for i in range(int(xdiv)):
            item = self.root.add("text", x=(cw*i/xdiv + cpad), y=h,
                                 text=str(gen_no),
                                 font_gdk=style.font,
                                 anchor=GTK.ANCHOR_WEST)
            self.canvas_items.append(item)
            gen_no = gen_no + 1

        for i in range(gen):
            if list[i]:
                if i < int(gen/2):
                    findex = (2*i)+1 
                    mindex = findex+1
                    if list[findex]:
                        p = list[findex]
                        self.draw_canvas_line(xpts[i], ypts[i], xpts[findex],
                                              ypts[findex], h, w, p[0], style, p[1])
                    if list[mindex]:
                        p = list[mindex]
                        self.draw_canvas_line(xpts[i],ypts[i], xpts[mindex],
                                              ypts[mindex], h, w, p[0], style, p[1])
                p = list[i]
                self.add_box(xpts[i],ypts[i],w,h,p[0],style)
        self.change_active_person(person)

    def make_arrow_button(self,direction,function):
        """Make a button containing an arrow with the attached callback"""

        arrow = gtk.GtkArrow(at=direction)
        button = gtk.GtkButton()
        button.add(arrow)
        button.connect("clicked",function)
        arrow.show()
        button.show()
        return (button, arrow)

    def on_show_child_menu(self,obj):
        """User clicked button to move to child of active person"""

        if self.presel_descendants:
            # Go to a previously selected child.
            person = self.presel_descendants.pop(-1)
            self.active_person = person
            self.load_canvas(person)
        elif self.active_person:
            # Build and display the menu attached to the left pointing arrow
            # button. The menu consists of the children of the current root
            # person of the tree. Attach a child to each menu item.
            myMenu = gtk.GtkMenu()
            for family in self.active_person.getFamilyList():
                for child in family.getChildList():
                    menuitem = gtk.GtkMenuItem(GrampsCfg.nameof(child))
                    myMenu.append(menuitem)
                    menuitem.set_data(_PERSON,child)
                    menuitem.connect("activate",self.on_childmenu_changed)
                    menuitem.show()
            myMenu.popup(None,None,None,0,0)
        return 1

    def on_childmenu_changed(self,obj):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""

        person = obj.get_data(_PERSON)
        if person:
            self.load_canvas(person)
        return 1
    
    def add_parent_button(self,parent,x,y,h):
        """Add a button with a right pointing button on the main group at
           the specified location. Attach the passed parent and the callback
           to the button."""

	button,arrow = self.make_arrow_button(GTK.ARROW_RIGHT,self.change_to_parent)
        button.set_data(_PERSON,parent)

        item = self.root.add("widget", widget=button, x=x, y=y+(h/2),
                             height=h, width=h, size_pixels=1,
                             anchor=GTK.ANCHOR_EAST)
        self.canvas_items.append(arrow)
        self.canvas_items.append(item)
        self.canvas_items.append(button)

    def change_to_parent(self,obj):
        """Callback to right pointing arrow button. Gets the person
           attached to the button and change the root person to that
           person, redrawing the view."""
        person = obj.get_data(_PERSON)
        if self.active_person:
            self.presel_descendants.append(self.active_person)
            self.active_person = person
        self.load_canvas(person)
    
    def draw_canvas_line(self,x1,y1,x2,y2,h,w,data,style,ls):
        """Draw an two segment line between the x,y point pairs. Attach
           a event callback and data to the line."""
 
        startx = x1+(w/2.0)
        pts = [startx,y1, startx,y2+(h/2.0), x2,y2+(h/2.0)]
        item = self.root.add("line", width_pixels=2,
                             points=pts, line_style=ls,
                             fill_color_gdk=style.black)
        item.set_data(_PERSON,data)
        item.connect("event",self.line_event)
        self.canvas_items.append(item)

    def build_x_coords(self,x,cpad):
        """Build the array of x coordinates for the possible positions
           on the pedegree view."""
        return [cpad] + [x+cpad]*2 + [x*2+cpad]*4 + \
               [x*3+cpad]*8 + [x*4+cpad]*16

    def build_y_coords(self, y, top_pad):
        """Build the array of y coordinates for the possible positions
           on the pedegree view."""
        res = [ y*16, y*8,  y*24, y*4,  y*12, y*20, y*28, y*2,  
                y*6,  y*10, y*14, y*18, y*22, y*26, y*30, y,    
                y*3,  y*5,  y*7,  y*9,  y*11, y*13, y*15, y*17, 
                y*19, y*21, y*23, y*25, y*27, y*29, y*31 ]
        return map(lambda coord, top_pad=top_pad: coord + top_pad, res)
    
    def add_box(self,x,y,bwidth,bheight,person,style):
        """Draw a box of the specified size at the specified location.
           The box consists of a shadow box for effect, the real box
           that contains the information, and the basic text 
           information. For convience, the all the subelements are
           grouped into a GNOME canvas group."""

        shadow = _PAD
        xpad = _PAD
        
        name = person.getPrimaryName().getName()
        group = self.root.add("group",x=x,y=y)
        self.canvas_items.append(group)

        # draw the shadow box
        item = group.add("rect", x1=shadow, y1=shadow,
                         x2=bwidth+shadow, y2=bheight+shadow,
                         outline_color_gdk=style.dark[GTK.STATE_NORMAL],
                         fill_color_gdk=style.dark[GTK.STATE_NORMAL])
        self.canvas_items.append(item)

        # draw the real box
        item = group.add("rect", x1=0, y1=0, x2=bwidth, y2=bheight,
                         outline_color_gdk=style.bg[GTK.STATE_NORMAL],
                         fill_color_gdk=style.white)
        self.canvas_items.append(item)

        # Write the text 
        item = group.add("text", x=xpad, y=bheight/2.0, text=name,
                         fill_color_gdk=style.text[GTK.STATE_NORMAL],
                         font_gdk=style.font, anchor=GTK.ANCHOR_WEST)
        self.canvas_items.append(item)
        group.connect('event',self.box_event)
        group.set_data('p',person)

    def box_event(self,obj,event):
        """Handle events over a drawn box. Doubleclick would edit,
           shift doubleclick would change the active person, entering
           the box expands it to display more information, leaving a
           box returns it to the original size and information"""

        if event.type == GDK._2BUTTON_PRESS:
            if event.button == 1:
                person = obj.get_data(_PERSON)
                if (event.state & GDK.SHIFT_MASK) or (event.state & GDK.CONTROL_MASK):
                    self.change_active_person(person)
                    del self.presel_descendants[:]
                    self.load_canvas(person)
                else:
                    self.load_person(person)
                return 1
        elif event.type == GDK.ENTER_NOTIFY:
            self.expand_box(obj)
            return 0
        elif event.type == GDK.LEAVE_NOTIFY:
            self.shrink_box(obj)
            return 0
        return 0
    def shrink_box(self,obj):
        """Shrink an exanded box back down to normal size"""

        ch = obj.children()
        length = len(ch)
        if length <= 3:
            return 1
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h/3)
        box2 = obj.children()[0]
        x,y,w,h1 = box2.get_bounds()
        box2.set(x1=x,y1=y,x2=w,y2=(h/3)+_PAD)
        if length > 4:
            ch[4].destroy()
            if length > 3:
                ch[3].destroy()
        self.update()
        self.canvas.update_now()
        
    def expand_box(self,obj):
        """Expand a box to include additional information"""

        obj.raise_to_top()
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h*3)
        box2 = obj.children()[0]
        x,y,w,h1 = box2.get_bounds()
        box2.set(x1=x,y1=y,x2=w,y2=(3*h)+_PAD)
        person = obj.get_data('p')
        font = self.canvas['style'].font
        color = self.canvas['style'].text[GTK.STATE_NORMAL]
        obj.add("text", font_gdk=font, fill_color_gdk=color,
                text="b. %s" % person.getBirth().getDate(),
                anchor=GTK.ANCHOR_WEST, x=_PAD, y=h+(h/2))
        obj.add("text", font_gdk=font, fill_color_gdk=color,
                text="d. %s" % person.getDeath().getDate(),
                anchor=GTK.ANCHOR_WEST, x=_PAD, y=2*h+(h/2))
        msg = _("Doubleclick to edit, Shift-Doubleclick to make the active person")
        self.sb.set_status(msg)

    def line_event(self,obj,event):
        """Catch X events over a line and respond to the ones we care about"""

	person = obj.get_data(_PERSON)
        style = self.canvas['style']

        if event.type == GDK._2BUTTON_PRESS:
            if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
                self.load_canvas(person)
        elif event.type == GDK.ENTER_NOTIFY:
            obj.set(fill_color_gdk=style.bg[GTK.STATE_SELECTED],
                    width_pixels=4)
            name = GrampsCfg.nameof(person)
            msg = _("Double clicking will make %s the active person") % name
            self.sb.set_status(msg)
        elif event.type == GDK.LEAVE_NOTIFY:
            obj.set(fill_color_gdk=style.black, width_pixels=2)
            self.update()

    def on_canvas1_event(self,obj,event):
        """Handle resize events over the canvas, redrawing if the size changes"""

        if event.type == GDK.EXPOSE:
            x1,y1,x2,y2 = self.canvas.get_allocation()
            if self.x1 != x1 or self.x2 != x2 or \
               self.y1 != y1 or self.y2 != y2:
                self.x1 = x1; self.x2 = x2
                self.y1 = y1; self.y2 = y2
                self.load_canvas(self.active_person)
        return 0

    def find_tree(self,person,index,depth,list,val=0):
        """Recursively build a list of ancestors"""

        if depth > 5 or person == None:
            return
        (family,m,f) = person.getMainParentsRel()
        if family:
            mrel = (m != "Birth")
            frel = (f != "Birth")
            
        list[index] = (person,val)
        if family != None:
            father = family.getFather()
            if father != None:
                self.find_tree(father,(2*index)+1,depth+1,list,frel)
            mother = family.getMother()
            if mother != None:
                self.find_tree(mother,(2*index)+2,depth+1,list,mrel)

