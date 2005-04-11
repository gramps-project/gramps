#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import pango

try:
    from gnomecanvas import CanvasGroup, CanvasRect, CanvasText, CanvasWidget, CanvasLine
except:
    from gnome.canvas import CanvasGroup, CanvasRect, CanvasText, CanvasWidget, CanvasLine

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import GrampsCfg
import Relationship
import NameDisplay
import RelLib

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_PAD       = 3
_CANVASPAD = 3
_PERSON    = "p"
_BORN = _('b.')
_DIED = _('d.')
_BAPT = _('bap.')
_CHRI = _('chr.')
_BURI = _('bur.')
_CREM = _('crem.')


#-------------------------------------------------------------------------
#
# DispBox class
#
#-------------------------------------------------------------------------
class DispBox:
    """
    This class handles the person box, including its expanded and
    shrunk states, as well as the callbacks for events occurring in the box.
    """

    def __init__(self,root,style,x,y,w,h,person,db,change,edit,build_menu):
        shadow = _PAD
        xpad = _PAD
        
        self.db = db
        self.change = change
        self.edit = edit
        self.build_menu = build_menu
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.person = person
        self.root = root

        self.name = NameDisplay.displayer.display(person)
        
        self.exp = build_detail_string( db, person)

        self.group = self.root.add(CanvasGroup,x=x,y=y)
        self.shadow = self.group.add(
            CanvasRect, x1=shadow, y1=shadow, x2=w+shadow, y2=h+shadow,
            outline_color_gdk=style.dark[gtk.STATE_NORMAL],
            fill_color_gdk=style.dark[gtk.STATE_NORMAL])

        # draw the real box
        self.bkgnd = self.group.add(
            CanvasRect, x1=0, y1=0, x2=w, y2=h,
            outline_color_gdk=style.fg[gtk.STATE_NORMAL],
            fill_color_gdk=style.base[gtk.STATE_NORMAL])

        font = gtk.gdk.font_from_description(style.font_desc)
        self.textbox = self.group.add(
            CanvasText, x=xpad, y=h/2.0, text=self.name,
            fill_color_gdk=style.text[gtk.STATE_NORMAL],
            font=font, anchor=gtk.ANCHOR_WEST)
        self.group.connect('event',self.group_event)
        self.group.set_data(_PERSON,person.get_handle())

  
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
            self.edit(self.person)
            return 0
        elif event.type == gtk.gdk.ENTER_NOTIFY:
            self.expand()
            return 0
        elif event.type == gtk.gdk.LEAVE_NOTIFY:
            self.shrink()
            return 0
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_menu(event,self.person)
            return True
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
    def __init__(self,parent,canvas,update,status_bar,lp):
        self.parent = parent

        self.relcalc = Relationship.RelationshipCalculator(self.parent.db)
        self.parent.connect('database-changed',self.change_db)
        self.parent.connect('active-changed',self.active_changed)

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
        self.load_person = lp
        self.anchor = None
        self.canvas.parent.connect('button-press-event',self.on_canvas_press)
        self.change_db(self.parent.db)
        self.distance = self.relcalc.get_relationship_distance

    def change_db(self,db):
        # Reconnect signals
        self.db = db
        db.connect('person-add', self.person_updated_cb)
        db.connect('person-update', self.person_updated_cb)
        db.connect('person-delete', self.person_updated_cb)
        db.connect('person-rebuild', self.person_rebuild)
        self.relcalc.set_db(db)
        self.active_person = None

    def person_updated_cb(self,handle_list):
        self.load_canvas(self.active_person)

    def person_rebuild(self):
        self.load_canvas(self.active_person)

    def active_changed(self,handle):
        if handle:
            self.active_person = self.db.get_person_from_handle(handle)
            self.load_canvas(self.active_person)
        else:
            self.load_canvas(None)
        
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

        lst = [None]*31
        self.find_tree(self.active_person,0,1,lst)

        # determine the largest string width and height for calcuation
        # of box sizes.

        a = pango.Layout(self.canvas.get_pango_context())
        
        for t in lst:
            if t:
                boxtext = build_detail_string(self.db,t[0]).encode("UTF-8")
                for line in boxtext.split("\n"):
                    try:
                        a.set_text(line,len(line))
                    except TypeError:
                        a.set_text(line)
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

        self.anchor_txt = self.root.add(
            CanvasText, x=0, y=y2-12, font=font, text=self.make_anchor_label(),
            fill_color_gdk=style.fg[gtk.STATE_NORMAL],
            anchor=gtk.ANCHOR_WEST)
        self.canvas_items.append(self.anchor_txt)

        for family_handle in self.active_person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if not family:
                continue
            if len(family.get_child_handle_list()) > 0:
                button,arrow = self.make_arrow_button(gtk.ARROW_LEFT,
                                                      self.on_show_child_menu)
                item = self.root.add(CanvasWidget, widget=button,
                                     x=_CANVASPAD, y=ypts[0]+(h/2.0), 
                                     height=h, width=h,
                                     size_pixels=1, anchor=gtk.ANCHOR_WEST)
                self.canvas_items.append(item)
                self.canvas_items.append(button)
                self.canvas_items.append(arrow)
                break

        if lst[1]:
            p = lst[1]
            self.add_parent_button(p[0],x2-_PAD,ypts[1],h)
        
        if lst[2]:
            p = lst[2]
            self.add_parent_button(p[0],x2-_PAD,ypts[2],h)

        gen_no = 1
        if self.anchor:
            (firstRel,secondRel,common) = self.distance(self.active_person,
                                                        self.anchor)
            if not common or type(common) in [type(''),type(u'')]:
                self.remove_anchor()
            else:
                gen_no = len(firstRel)-len(secondRel)

        for i in range(int(xdiv)):
            item = self.root.add(CanvasText, x=(cw*i/xdiv + cpad), y=h,
                                 text=str(gen_no),
                                 font=font,
                                 anchor=gtk.ANCHOR_WEST)
            self.canvas_items.append(item)
            gen_no = gen_no + 1

        for i in range(gen):
            if lst[i]:
                if i < int(gen/2.0):
                    findex = (2*i)+1 
                    mindex = findex+1
                    if lst[findex]:
                        p = lst[findex]
                        self.draw_canvas_line(xpts[i], ypts[i], xpts[findex],
                                              ypts[findex], h, w, p[0], style,
                                              p[1])
                    if lst[mindex]:
                        p = lst[mindex]
                        self.draw_canvas_line(xpts[i],ypts[i], xpts[mindex],
                                              ypts[mindex], h, w, p[0], style,
                                              p[1])
                p = lst[i]
                box = DispBox(self.root,style,xpts[i],ypts[i],w,h,p[0],
                              self.db,
                              self.parent.change_active_person, 
                              self.load_person, self.build_full_nav_menu)
                self.boxes.append(box)

    def make_arrow_button(self,direction,function):
        """Make a button containing an arrow with the attached callback"""

        arrow = gtk.Arrow(direction,gtk.SHADOW_NONE)
        button = gtk.Button()
        button.add(arrow)
        button.connect("clicked",function)
        arrow.show()
        button.show()
        return (button, arrow)

    def set_anchor(self):
        if self.active_person:
            self.anchor = self.active_person
        else:
            self.anchor = None
        self.anchor_txt.set(text=self.make_anchor_label())

    def remove_anchor(self):
        self.anchor = None
        self.anchor_txt.set(text=self.make_anchor_label())

    def on_anchor_set(self,junk):
        self.set_anchor()
        self.load_canvas(self.active_person)
        
    def on_anchor_removed(self,junk):
        self.remove_anchor()
        self.load_canvas(self.active_person)

    def make_anchor_label(self):
        """Make a label containing the name of the anchored person"""
        if self.anchor:
            anchor_string = self.anchor.get_primary_name().get_regular_name()
            return "%s: %s" % (_("Anchor"),anchor_string)
        else:
            return ""

    def on_show_child_menu(self,obj):
        """User clicked button to move to child of active person"""

        if self.active_person:
            # Build and display the menu attached to the left pointing arrow
            # button. The menu consists of the children of the current root
            # person of the tree. Attach a child to each menu item.

            childlist = find_children(self.db,self.active_person)
            if len(childlist) == 1:
                child = self.db.get_person_from_handle(childlist[0])
                if child:
                    self.parent.change_active_person(child)
            elif len(childlist) > 1:
                myMenu = gtk.Menu()
                for child_handle in childlist:
                    child = self.db.get_person_from_handle(child_handle)
                    cname = NameDisplay.displayer.display(child)
                    menuitem = gtk.MenuItem(None)
                    if find_children(self.db,child):
                        label = gtk.Label('<b><i>%s</i></b>' % cname)
                    else:
                        label = gtk.Label(cname)
                    label.set_use_markup(True)
                    label.show()
                    label.set_alignment(0,0)
                    menuitem.add(label)
                    myMenu.append(menuitem)
                    menuitem.set_data(_PERSON,child_handle)
                    menuitem.connect("activate",self.on_childmenu_changed)
                    menuitem.show()
                myMenu.popup(None,None,None,0,0)
        return 1

    def on_childmenu_changed(self,obj):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""

        person_handle = obj.get_data(_PERSON)
        person = self.db.get_person_from_handle(person_handle)
        if person:
            self.parent.change_active_person(person)
        return 1
    
    def add_parent_button(self,parent,x,y,h):
        """Add a button with a right pointing button on the main group at
           the specified location. Attach the passed parent and the callback
           to the button."""

        button,arrow = self.make_arrow_button(gtk.ARROW_RIGHT,
                                              self.change_to_parent)
        button.set_data(_PERSON,parent.get_handle())

        item = self.root.add(CanvasWidget, widget=button, x=x, y=y+(h/2),
                             height=h, width=h, size_pixels=1,
                             anchor=gtk.ANCHOR_EAST)
        self.canvas_items.append(arrow)
        self.canvas_items.append(item)
        self.canvas_items.append(button)

    def change_to_parent(self,obj):
        """Callback to right pointing arrow button. Gets the person
           attached to the button and change the root person to that
           person, redrawing the view."""
        person_handle = obj.get_data(_PERSON)
        person = self.db.get_person_from_handle(person_handle)
        if self.active_person:
            self.active_person = person
        self.parent.change_active_person(person)
    
    def draw_canvas_line(self,x1,y1,x2,y2,h,w,data,style,ls):
        """Draw an two segment line between the x,y point pairs. Attach
           a event callback and data to the line."""
 
        startx = x1+(w/2.0)
        pts = [startx,y1, startx,y2+(h/2.0), x2,y2+(h/2.0)]
        item = self.root.add(CanvasLine, width_pixels=2,
                             points=pts, line_style=ls,
                             fill_color_gdk=style.fg[gtk.STATE_NORMAL])
        item.set_data(_PERSON,data.get_handle())
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

        person_handle = obj.get_data(_PERSON)
        if not person_handle:
            return 
        person = self.db.get_person_from_handle(person_handle)
        style = self.canvas.get_style()

        if event.type == gtk.gdk._2BUTTON_PRESS:
            if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
                self.parent.change_active_person(person)
        elif event.type == gtk.gdk.ENTER_NOTIFY:
            obj.set(fill_color_gdk=style.bg[gtk.STATE_SELECTED],
                    width_pixels=4)
            name = NameDisplay.displayer.display(person)
            msg = _("Double clicking will make %s the active person") % name
            self.sb.set_status(msg)
        elif event.type == gtk.gdk.LEAVE_NOTIFY:
            obj.set(fill_color_gdk=style.fg[gtk.STATE_NORMAL], width_pixels=2)
            self.update()

    def find_tree(self,person,index,depth,lst,val=0):
        """Recursively build a list of ancestors"""

        if depth > 5 or person == None:
            return
        lst[index] = (person,val)

        parent_families = person.get_parent_family_handle_list()
        if parent_families:
            (family_handle,m,f) = parent_families[0]
        else:
            return
        if family_handle:
            mrel = m != RelLib.Person.CHILD_REL_BIRTH
            frel = f != RelLib.Person.CHILD_REL_BIRTH

        family = self.db.get_family_from_handle(family_handle)
        if family != None:
            father_handle = family.get_father_handle()
            if father_handle != None:
                father = self.db.get_person_from_handle(father_handle)
                self.find_tree(father,(2*index)+1,depth+1,lst,frel)
            mother_handle = family.get_mother_handle()
            if mother_handle != None:
                mother = self.db.get_person_from_handle(mother_handle)
                self.find_tree(mother,(2*index)+2,depth+1,lst,mrel)

    def on_canvas1_event(self,obj,event):
        """Handle resize events over the canvas, redrawing if the size changes"""
        
        if event.type == gtk.gdk.EXPOSE:
            x1,y1,x2,y2 = self.canvas.get_allocation()
            if self.x1 != x1 or self.x2 != x2 or \
                   self.y1 != y1 or self.y2 != y2:
                self.x1 = x1; self.x2 = x2
                self.y1 = y1; self.y2 = y2
                self.canvas.set_size(x2,y2)
                self.load_canvas(self.active_person)
        return 0

    def on_canvas_press(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_nav_menu(event)
            return True
        return False

    def add_nav_portion_to_menu(self,menu):
        """
        This function adds a common history-navigation portion 
        to the context menu. Used by both build_nav_menu() and 
        build_full_nav_menu() methods. 
        """
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
            (_("Set anchor"),self.on_anchor_set,1),
            (_("Remove anchor"),self.on_anchor_removed,1),
        ]

        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

    def build_nav_menu(self,event):
        """Builds the menu with only history-based navigation."""
        
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        self.add_nav_portion_to_menu(menu)
        menu.popup(None,None,None,event.button,event.time)

    def build_full_nav_menu(self,event,person):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation.
        """
        
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))

        # Go over spouses and build their menu
        item = gtk.MenuItem(_("Spouses"))
        fam_list = person.get_family_handle_list()
        no_spouses = 1
        for fam_id in fam_list:
            family = self.db.get_family_from_handle(fam_id)
            if family.get_father_handle() == person.get_handle():
                sp_id = family.get_mother_handle()
            else:
                sp_id = family.get_father_handle()
            spouse = self.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(gtk.Menu())
                sp_menu = item.get_submenu()

            sp_item = gtk.MenuItem(NameDisplay.displayer.display(spouse))
            sp_item.set_data(_PERSON,sp_id)
            sp_item.connect("activate",self.on_childmenu_changed)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        menu.append(item)
        
        # Go over siblings and build their menu
        item = gtk.MenuItem(_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for (f,mrel,frel) in pfam_list:
            fam = self.db.get_family_from_handle(f)
            sib_list = fam.get_child_handle_list()
            for sib_id in sib_list:
                if sib_id == person.get_handle():
                    continue
                sib = self.db.get_person_from_handle(sib_id)
                if not sib:
                    continue

                if no_siblings:
                    no_siblings = 0
                    item.set_submenu(gtk.Menu())
                    sib_menu = item.get_submenu()

                sib_item = gtk.MenuItem(NameDisplay.displayer.display(sib))
                sib_item.set_data(_PERSON,sib_id)
                sib_item.connect("activate",self.on_childmenu_changed)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        
        # Go over children and build their menu
        item = gtk.MenuItem(_("Children"))
        no_children = 1
        childlist = find_children(self.db,person)
        for child_handle in childlist:
            child = self.db.get_person_from_handle(child_handle)
            if not child:
                continue
        
            if no_children:
                no_children = 0
                item.set_submenu(gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.db,child):
                label = gtk.Label('<b><i>%s</i></b>' % NameDisplay.displayer.display(child))
            else:
                label = gtk.Label(NameDisplay.displayer.display(child))

            child_item = gtk.MenuItem(None)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            child_item.add(label)
            child_item.set_data(_PERSON,child_handle)
            child_item.connect("activate",self.on_childmenu_changed)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = gtk.MenuItem(_("Parents"))
        no_parents = 1
        par_list = find_parents(self.db,person)
        for par_id in par_list:
            par = self.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.db,par):
                label = gtk.Label('<b><i>%s</i></b>' % NameDisplay.displayer.display(par))
            else:
                label = gtk.Label(NameDisplay.displayer.display(par))

            par_item = gtk.MenuItem(None)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            par_item.add(label)
            par_item.set_data(_PERSON,par_id)
            par_item.connect("activate",self.on_childmenu_changed)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
    
        # Add separator
        item = gtk.MenuItem(None)
        item.show()
        menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(menu)
        menu.popup(None,None,None,event.button,event.time)

#-------------------------------------------------------------------------
#
# Function to return children's list of a person
#
#-------------------------------------------------------------------------
def find_children(db,p):
    """
    Returns the list of all children's IDs for a person.
    """
    childlist = []
    for family_handle in p.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for child_handle in family.get_child_handle_list():
            childlist.append(child_handle)
    return childlist

#-------------------------------------------------------------------------
#
# Function to return parent's list of a person
#
#-------------------------------------------------------------------------
def find_parents(db,p):
    """
    Returns the unique list of all parents' IDs for a person.
    """
    parentlist = []
    for (f,mrel,frel) in p.get_parent_family_handle_list():
        family = db.get_family_from_handle(f)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if father_handle not in parentlist:
            parentlist.append(father_handle)
        if mother_handle not in parentlist:
            parentlist.append(mother_handle)
    return parentlist

#-------------------------------------------------------------------------
#
# Functions to build the text displayed in the details view of a DispBox
# aditionally used by PedigreeView to get the largest area covered by a DispBox
#
#-------------------------------------------------------------------------
def build_detail_string(db,person):

    detail_text = NameDisplay.displayer.display(person)

    def format_event(db, label, event):
        if not event:
            return u""
        ed = event.get_date()
        ep = None
        place_handle = event.get_place_handle()
        if place_handle:
            place_title = db.get_place_from_handle(place_handle).get_title()
            if place_title != "":
                if len(place_title) > 15:
                    ep = place_title[:14]+"..."
                else:
                    ep = place_title
        if ep:
            return u"\n%s %s, %s" % (label,ed,ep)
        return u"\n%s %s" % (label,ed)

    
    birth_handle = person.get_birth_handle()
    if birth_handle:
        detail_text += format_event(db, _BORN, db.get_event_from_handle(birth_handle))
    else:
        for event_handle in person.get_event_list():
            event = db.get_event_from_handle(event_handle)
            if event.get_name() == "Baptism":
                detail_text += format_event(db, _BAPT, event)
                break
            if event.get_name() == "Christening":
                detail_text += format_event(db, _CHRI, event)
                break

    death_handle = person.get_death_handle()
    if death_handle:
        detail_text += format_event(db, _DIED, db.get_event_from_handle(death_handle))
    else:
        for event_handle in person.get_event_list():
            event = db.get_event_from_handle(event_handle)
            if event.get_name() == "Burial":
                detail_text += format_event(db, _BURI, event)
                break
            if event.get_name() == "Cremation":
                detail_text += format_event(db, _CREM, event)
                break

    return detail_text
