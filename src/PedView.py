#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2003  Donald N. Allingham
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

# $Id$

_PAD       = 3
_CANVASPAD = 3
_PERSON    = "p"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import gnome.canvas
import pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import GrampsCfg
from gettext import gettext as _

_BORN = _('b.')
_DIED = _('d.')

class DispBox:

    def __init__(self,root,style,x,y,w,h,person,change):
        shadow = _PAD
        xpad = _PAD
        
        self.change = change
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.person = person
        self.root = root

        self.name = GrampsCfg.nameof(person)
        bd = person.getBirth().getDate()
        dd = person.getDeath().getDate()
        if bd and dd:
            self.exp = "%s\n%s %s\n%s %s" % (self.name,_BORN,bd,_DIED,dd )
        elif bd:
            self.exp = "%s\n%s %s" % (self.name,_BORN,bd )
        elif dd:
            self.exp = "%s\n%s %s" % (self.name,_DIED,dd )
        else:
            self.exp = "%s" % self.name

        
        self.group = self.root.add(gnome.canvas.CanvasGroup,x=x,y=y)
        self.shadow = self.group.add(gnome.canvas.CanvasRect,
                                     x1=shadow,
                                     y1=shadow,
                                     x2=w+shadow,
                                     y2=h+shadow,
                                     outline_color_gdk=style.dark[gtk.STATE_NORMAL],
                                     fill_color_gdk=style.dark[gtk.STATE_NORMAL])

        # draw the real box
        self.bkgnd = self.group.add(gnome.canvas.CanvasRect,
                                    x1=0,
                                    y1=0,
                                    x2=w,
                                    y2=h,
                                    outline_color_gdk=style.fg[gtk.STATE_NORMAL],
                                    fill_color_gdk=style.base[gtk.STATE_NORMAL])

        font = gtk.gdk.font_from_description(style.font_desc)
        self.textbox = self.group.add(gnome.canvas.CanvasText,
                                      x=xpad,
                                      y=h/2.0,
                                      text=self.name,
                                      fill_color_gdk=style.text[gtk.STATE_NORMAL],
                                      font=font, anchor=gtk.ANCHOR_WEST)
        self.group.connect('event',self.group_event)
        self.group.set_data(_PERSON,person)

    def cleanup(self):
        self.shadow.destroy()
        self.bkgnd.destroy()
        self.textbox.destroy()
        self.group.destroy()
        return
    
    def group_event(self,obj,event):
        """Handle events over a drawn box. Doubleclick would edit,
           shift doubleclick would change the active person, entering
           the box expands it to display more information, leaving a
           box returns it to the original size and information"""

        if event.type == gtk.gdk._2BUTTON_PRESS:
            return 1
        elif event.type == gtk.gdk.ENTER_NOTIFY:
            self.expand()
            return 0
        elif event.type == gtk.gdk.LEAVE_NOTIFY:
            self.shrink()
            return 0
        return 0

    def expand(self):
        """Expand a box to include additional information"""
        self.textbox.set(text=self.exp)
        self.bkgnd.set(y1=-self.h,y2=self.h*2)
        self.shadow.set(y1=-self.h+_PAD,y2=self.h*2+_PAD)
        
    def shrink(self):
        """Expand a box to include additional information"""
        self.textbox.set(text=self.name)
        self.bkgnd.set(y1=0,y2=self.h)
        self.shadow.set(y1=_PAD,y2=self.h+_PAD)
        
#-------------------------------------------------------------------------
#
# PedigreeView
#
#-------------------------------------------------------------------------
class PedigreeView:
    def __init__(self,parent,canvas,update,status_bar,change_active,lp):
        self.parent = parent
        self.canvas = canvas
        self.canvas_items = []
        self.boxes = []
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
        self.anchor = None
        self.canvas.connect('button-press-event',self.on_canvas_press)

    def clear(self):
        for i in self.canvas_items:
            i.destroy()
        for i in self.boxes:
            i.cleanup()

    def load_canvas(self, person):
        """Redraws the pedigree view window, using the passed person
           as the root person of the tree."""

        self.clear()
        
        if person is not self.active_person:
            self.active_person = person
        if person == None:
            return

        h = 0
        w = 0
        (x2,y2) = self.canvas.get_size()
    
        self.canvas.set_scroll_region(0,0,x2,y2)
        
        style = self.canvas.get_style()
        font = gtk.gdk.font_from_description(style.font_desc)

        list = [None]*31
        self.find_tree(self.active_person,0,1,list)

	# determine the largest string width and height for calcuation
        # of box sizes.

        a = pango.Layout(self.canvas.get_pango_context())
        
        for t in list:
            if t:
                for n in [GrampsCfg.nameof(t[0]),
                          u'%s %s' % (_BORN,t[0].getBirth().getDate()),
                          u'%s %s' % (_DIED,t[0].getDeath().getDate())]:
                    try:
                        a.set_text(n,len(n))
                    except TypeError:
                        a.set_text(n)
                    (w1,h1) = a.get_pixel_size()
                    h = max(h,h1)
                    w = max(w,w1)
        cpad = 10
        w = w+_PAD
        
        cw = x2-(2*cpad)-10-h
        ch = y2-(2*cpad)

        if 5*w < cw and 24*h < ch:
            gen = 31
            xdiv = 5.0
        elif 4*w < cw and 12*h < ch:
            gen = 15
            xdiv = 4.0
        else:
            gen = 7
            xdiv = 3.0

        xpts = self.build_x_coords(cw/xdiv,_CANVASPAD+h)
        ypts = self.build_y_coords((ch-h)/32.0, h)

        anchor_button = self.make_anchor_button(self.on_anchor_clicked)
        an = pango.Layout(self.canvas.get_pango_context())
        an_text = anchor_button.get_label()
        try:
            an.set_text(an_text,len(an_text))
        except TypeError:
            an.set_text(an_text)
        (w_ab,h_ab) = an.get_pixel_size()

        item = self.root.add(gnome.canvas.CanvasWidget, widget=anchor_button,
                        x=0, y=y2-h_ab-12, 
                        height=h_ab+12, width=w_ab+12,
                        size_pixels=1, anchor=gtk.ANCHOR_WEST)
        self.canvas_items = [item, anchor_button]

        self.anchor_txt = self.root.add(gnome.canvas.CanvasText,
                                        x=w_ab+24,
                                        y=y2-h_ab-12, 
                                        font=font,
                                        text=self.make_anchor_label(),
                                        fill_color_gdk=style.fg[gtk.STATE_NORMAL],
                                        anchor=gtk.ANCHOR_WEST)
        self.canvas_items.append(self.anchor_txt)

        for family in self.active_person.getFamilyList():
            if len(family.getChildList()) > 0:
                button,arrow = self.make_arrow_button(gtk.ARROW_LEFT,
                                                      self.on_show_child_menu)
                item = self.root.add(gnome.canvas.CanvasWidget, widget=button,
                                     x=_CANVASPAD, y=ypts[0]+(h/2.0), 
                                     height=h, width=h,
                                     size_pixels=1, anchor=gtk.ANCHOR_WEST)
                self.canvas_items.append(item)
                self.canvas_items.append(button)
                self.canvas_items.append(arrow)
                break

        if list[1]:
            p = list[1]
            self.add_parent_button(p[0],x2-_PAD,ypts[1],h)
        
        if list[2]:
            p = list[2]
            self.add_parent_button(p[0],x2-_PAD,ypts[2],h)

        gen_no = 1
        for i in range(int(xdiv)):
            item = self.root.add(gnome.canvas.CanvasText, x=(cw*i/xdiv + cpad), y=h,
                                 text=str(gen_no),
                                 font=font,
                                 anchor=gtk.ANCHOR_WEST)
            self.canvas_items.append(item)
            gen_no = gen_no + 1

        for i in range(gen):
            if list[i]:
                if i < int(gen/2.0):
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
                box = DispBox(self.root,style,xpts[i],ypts[i],w,h,p[0],
                              self.change_active_person)
                self.boxes.append(box)
        self.change_active_person(person)


    def make_arrow_button(self,direction,function):
        """Make a button containing an arrow with the attached callback"""

        arrow = gtk.Arrow(direction,gtk.SHADOW_NONE)
        button = gtk.Button()
        button.add(arrow)
        button.connect("clicked",function)
        arrow.show()
        button.show()
        return (button, arrow)

    def on_anchor_clicked(self,junk):
        if self.active_person:
            self.anchor = self.active_person
            anchor_string = self.anchor.getPrimaryName().getRegularName()
        else:
            self.anchor = None
        self.anchor_txt.set(text=self.make_anchor_label())
        
    def make_anchor_button(self,function):
        """Make a button containing anchor text with the attached callback"""

        button = gtk.Button(_("Drop anchor here"))
        button.connect("clicked",function)
        button.show()
        return button

    def make_anchor_label(self):
        """Make a label containing the name of the anchored person"""
        if self.anchor:
            anchor_string = self.anchor.getPrimaryName().getRegularName()
        else:
            anchor_string = _("None")
        return "%s: %s" % (_("Anchor"),anchor_string)

    def on_show_child_menu(self,obj):
        """User clicked button to move to child of active person"""

        if self.active_person:
            # Build and display the menu attached to the left pointing arrow
            # button. The menu consists of the children of the current root
            # person of the tree. Attach a child to each menu item.

            def find_children(p):
                childlist = []
                for family in p.getFamilyList():
                    for child in family.getChildList():
                        childlist.append(child)
                return childlist

            childlist = find_children(self.active_person)
            if len(childlist) == 1:
                self.load_canvas(childlist[0])
            elif len(childlist) > 1:
                myMenu = gtk.Menu()
                for child in childlist:
                    cname = GrampsCfg.nameof(child)
                    menuitem = gtk.MenuItem(None)
                    if find_children(child):
                        label = gtk.Label('<b><i>%s</i></b>' % cname)
                    else:
                        label = gtk.Label(cname)
                    label.set_use_markup(gtk.TRUE)
                    label.show()
                    label.set_alignment(0,0)
                    menuitem.add(label)
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

	button,arrow = self.make_arrow_button(gtk.ARROW_RIGHT,self.change_to_parent)
        button.set_data(_PERSON,parent)

        item = self.root.add(gnome.canvas.CanvasWidget, widget=button, x=x, y=y+(h/2),
                             height=h, width=h, size_pixels=1,
                             anchor=gtk.ANCHOR_EAST)
        self.canvas_items.append(arrow)
        self.canvas_items.append(item)
        self.canvas_items.append(button)

    def change_to_parent(self,obj):
        """Callback to right pointing arrow button. Gets the person
           attached to the button and change the root person to that
           person, redrawing the view."""
        person = obj.get_data(_PERSON)
        if self.active_person:
            self.active_person = person
        self.load_canvas(person)
    
    def draw_canvas_line(self,x1,y1,x2,y2,h,w,data,style,ls):
        """Draw an two segment line between the x,y point pairs. Attach
           a event callback and data to the line."""
 
        startx = x1+(w/2.0)
        pts = [startx,y1, startx,y2+(h/2.0), x2,y2+(h/2.0)]
        item = self.root.add(gnome.canvas.CanvasLine, width_pixels=2,
                             points=pts, line_style=ls,
                             fill_color_gdk=style.fg[gtk.STATE_NORMAL])
        item.set_data(_PERSON,data)
        item.connect("event",self.line_event)
        self.canvas_items.append(item)

    def build_x_coords(self,x,cpad):
        """Build the array of x coordinates for the possible positions
           on the pedegree view."""
        return [cpad] + [x+cpad]*2 + [x*2+cpad]*4 + [x*3+cpad]*8 + [x*4+cpad]*16

    def build_y_coords(self, y, top_pad):
        """Build the array of y coordinates for the possible positions
           on the pedegree view."""
        res = [ y*16.0, y*8.0,  y*24.0, y*4.0,  y*12.0, y*20.0, y*28.0, y*2.0,  
                y*6.0,  y*10.0, y*14.0, y*18.0, y*22.0, y*26.0, y*30.0, y,    
                y*3.0,  y*5.0,  y*7.0,  y*9.0,  y*11.0, y*13.0, y*15.0, y*17.0, 
                y*19.0, y*21.0, y*23.0, y*25.0, y*27.0, y*29.0, y*31.0 ]
        return map(lambda coord, top_pad=top_pad: coord + top_pad, res)

    def line_event(self,obj,event):
        """Catch X events over a line and respond to the ones we care about"""

	person = obj.get_data(_PERSON)
        style = self.canvas.get_style()

        if event.type == gtk.gdk._2BUTTON_PRESS:
            if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
                self.load_canvas(person)
        elif event.type == gtk.gdk.ENTER_NOTIFY:
            obj.set(fill_color_gdk=style.bg[gtk.STATE_SELECTED],
                    width_pixels=4)
            name = GrampsCfg.nameof(person)
            msg = _("Double clicking will make %s the active person") % name
            self.sb.set_status(msg)
        elif event.type == gtk.gdk.LEAVE_NOTIFY:
            obj.set(fill_color_gdk=style.fg[gtk.STATE_NORMAL], width_pixels=2)
            self.update()

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

    def on_canvas1_event(self,obj,event):
        """Handle resize events over the canvas, redrawing if the size changes"""
        
        if event.type == gtk.gdk.EXPOSE:
            x1,y1,x2,y2 = self.canvas.get_allocation()
            if self.x1 != x1 or self.x2 != x2 or \
                   self.y1 != y1 or self.y2 != y2:
                self.x1 = x1; self.x2 = x2
                self.y1 = y1; self.y2 = y2
                self.load_canvas(self.active_person)
        return 0

    def on_canvas_press(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_nav_menu(event)

    def build_nav_menu(self,event):
        """Builds the menu with navigation."""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            ('gtk-go-back',self.parent.back_clicked,back_sensitivity),
            ('gtk-go-forward',self.parent.fwd_clicked,fwd_sensitivity),
            ('gtk-home',self.parent.on_home_clicked,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)
