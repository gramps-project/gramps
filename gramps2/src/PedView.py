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
import gobject
import gtk
import gtk.gdk

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
# PedigreeView
#
#-------------------------------------------------------------------------
class PedigreeView:
    def __init__(self,parent,canvas,update,status_bar,edit_person):
        self.parent = parent

        self.relcalc = Relationship.RelationshipCalculator(self.parent.db)
        self.parent.connect('database-changed',self.change_db)
        self.parent.connect('active-changed',self.active_changed)

        # FIXME: Hack to avoid changing the glade file
        # Replace canvas by notebook
        self.parent_container = canvas.get_parent()
        canvas.destroy()
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        self.parent_container.add_with_viewport(self.notebook)
        # ###
            
        self.table_2 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_2)

        self.table_3 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_3)

        self.table_4 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_4)

        self.table_5 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_5)

        self.parent_container.connect("size-allocate", self.size_request_cb)

        self.notebook.show_all()

        self.update = update
        self.sb = status_bar
        self.edit_person = edit_person
    
        self.change_db(self.parent.db)
        self.distance = self.relcalc.get_relationship_distance
        
        self.force_size = 0 # Automatic resize

    def add_table_to_notebook( self, table):
        frame = gtk.ScrolledWindow(None,None)
        frame.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        frame.add_with_viewport(table)
        try:
            self.notebook.append_page(frame,None)
        except:
            # for PyGtk < 2.4
            self.notebook.append_page(frame,gtk.Label(""))

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
        self.rebuild_trees(self.active_person)

    def person_rebuild(self):
        self.rebuild_trees(self.active_person)

    def active_changed(self,handle):
        if handle:
            self.active_person = self.db.get_person_from_handle(handle)
            self.rebuild_trees(self.active_person)
        else:
            self.rebuild_trees(None)
    
    def request_resize(self):
        self.size_request_cb(self.parent_container,None,None)
        
    def size_request_cb(self, widget, event, data=None):
        if self.force_size == 0:
            v = widget.get_allocation()
            page_list = range(0,self.notebook.get_n_pages())
            page_list.reverse()
            for n in page_list:
                p = self.notebook.get_nth_page(n).get_child().get_child().get_allocation()
                if v.width >= p.width and v.height > p.height:
                    self.notebook.set_current_page(n)
                    break;
        else:
            self.notebook.set_current_page(self.force_size-2)

    def rebuild_trees(self,person):
        pos_2 =((0,3,3,(3,4,5)),
                (2,0,3,None),
                (2,10,3,None))
        pos_3 =((0,4,5,(3,6,3)),
                (2,1,3,(5,2,3)),
                (2,9,3,(5,10,3)),
                (4,0,1,None),
                (4,4,1,None),
                (4,8,1,None),
                (4,12,1,None))
        pos_4 =((0, 5,5,(3, 7,5)),
                (2, 2,3,(5, 3,3)),
                (2,10,3,(5,11,3)),
                (4, 1,1,(7,1,1)),
                (4, 5,1,(7,5,1)),
                (4, 9,1,(7,9,1)),
                (4,13,1,(7,13,1)),
                (6, 0,1,None),
                (6, 2,1,None),
                (6, 4,1,None),
                (6, 6,1,None),
                (6, 8,1,None),
                (6,10,1,None),
                (6,12,1,None),
                (6,14,1,None),)
        pos_5 =((0,10,11,(3,15,3)),
                (2, 5,5,(5, 7,1)),
                (2,21,5,(5,23,1)),
                (4, 2,3,(7,3,1)),
                (4,10,3,(7,11,1)),
                (4,18,3,(7,19,1)),
                (4,26,3,(7,27,1)),
                (6, 1,1,(9,1,1)),
                (6, 5,1,(9,5,1)),
                (6, 9,1,(9,9,1)),
                (6,13,1,(9,13,1)),
                (6,17,1,(9,17,1)),
                (6,21,1,(9,21,1)),
                (6,25,1,(9,25,1)),
                (6,29,1,(9,29,1)),
                (8, 0,1,None),
                (8, 2,1,None),
                (8, 4,1,None),
                (8, 6,1,None),
                (8, 8,1,None),
                (8,10,1,None),
                (8,12,1,None),
                (8,14,1,None),
                (8,16,1,None),
                (8,18,1,None),
                (8,20,1,None),
                (8,22,1,None),
                (8,24,1,None),
                (8,26,1,None),
                (8,28,1,None),
                (8,30,1,None),)
        self.rebuild( self.table_2, pos_2, person)
        self.rebuild( self.table_3, pos_3, person)
        self.rebuild( self.table_4, pos_4, person)
        self.rebuild( self.table_5, pos_5, person)
        
        gobject.idle_add(self.request_resize)

    def rebuild( self, table_widget, positions, active_person):
        # Build ancestor tree
        lst = [None]*31
        self.find_tree(self.active_person,0,1,lst)

        # Purge current table content
        for child in table_widget.get_children():
            child.destroy()
        table_widget.resize(1,1)
        
        tooltip = gtk.Tooltips()
        
        debug = False
        if debug:
            xmax = 0
            ymax = 0
            for field in positions:
                x = field[0]+3
                if x > xmax:
                    xmax = x
                y = field[1]+field[2]
                if y > ymax:
                    ymax = y
            for x in range(0,xmax):
                for y in range(0,ymax):
                    label=gtk.Label("%d,%d"%(x,y))
                    frame = gtk.ScrolledWindow(None,None)
                    frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
                    frame.set_policy(gtk.POLICY_NEVER,gtk.POLICY_NEVER)
                    frame.add(label)
                    table_widget.attach(frame,x,x+1,y,y+1,0,0,0,0)          
        
        for i in range(0,31):
            try:
                # Table placement for person data
                x = positions[i][0]
                y = positions[i][1]
                w = 3
                h = positions[i][2]
                
                if not lst[i]:
                    # No person -> show empty box
                    label = gtk.Label(" ")
                    frame = gtk.ScrolledWindow(None,None)
                    frame.set_shadow_type(gtk.SHADOW_OUT)
                    frame.set_policy(gtk.POLICY_NEVER,gtk.POLICY_NEVER)
                    frame.add_with_viewport(label)
                    if positions[i][2] > 1:
                        table_widget.attach(frame,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,0)
                    else:
                        table_widget.attach(frame,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.FILL,0,0)
                else:
                    text = gtk.Button(self.format_person(lst[i][0], positions[i][2]))
                    if i > 0 and positions[i][2] < 3:
                        tooltip.set_tip(text, self.format_person(lst[i][0], 11))
                    text.set_alignment(0.0,0.0)
                    gender = lst[i][0].get_gender()
                    if gender == RelLib.Person.MALE:
                        text.modify_bg( gtk.STATE_NORMAL, text.get_colormap().alloc_color("#F5FFFF"))
                    elif gender == RelLib.Person.FEMALE:
                        text.modify_bg( gtk.STATE_NORMAL, text.get_colormap().alloc_color("#FFF5FF"))
                    else:
                        text.modify_bg( gtk.STATE_NORMAL, text.get_colormap().alloc_color("#FFFFF5"))
                    white = text.get_colormap().alloc_color("white")
                    text.modify_bg( gtk.STATE_ACTIVE, white)
                    text.modify_bg( gtk.STATE_PRELIGHT, white)
                    text.modify_bg( gtk.STATE_SELECTED, white)
                    text.set_data(_PERSON,lst[i][0].get_handle())
                    text.connect("button-press-event", self.build_full_nav_menu_cb)
                    if positions[i][2] > 1:
                        table_widget.attach(text,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,0)
                    else:
                        table_widget.attach(text,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.FILL,0,0)
                    
                    # Connection lines
                    if i > 0:
                        x = positions[i][0]-1
                        y = positions[i][1]
                        w = 1
                        h = positions[i][2]
                        line = gtk.DrawingArea()
                        line.connect("expose-event", self.line_expose_cb)
                        line.set_data("idx", i)
                        line.set_data("rela", lst[i][1])
                        table_widget.attach(line,x,x+w,y,y+h,gtk.FILL,gtk.FILL,0,0)
                    
                # Marriage data
                if positions[i][3]:
                    # An empty label is used as fallback, to allow it to EXPAND.
                    # This gives a nicer layout
                    text = " "
                    try:
                        if lst[i] and lst[i][2]:
                            text = self.format_relation( lst[i][2], positions[i][3][2])
                    except IndexError:
                        pass
                    label = gtk.Label(text)
                    label.set_justify(gtk.JUSTIFY_LEFT)
                    label.set_line_wrap(True)
                    label.set_alignment(0.1,0.0)
                    x = positions[i][3][0]
                    y = positions[i][3][1]
                    w = 2
                    h = 1
                    if positions[i][3][2] > 1:
                        table_widget.attach(label,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,0)
                    else:
                        table_widget.attach(label,x,x+w,y,y+h,gtk.EXPAND|gtk.FILL,gtk.FILL,0,0)
            except IndexError:
                pass
        table_widget.show_all()

    def line_expose_cb(self, area, event):
        style = area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        alloc = area.get_allocation()
        idx = area.get_data("idx")
        rela = area.get_data("rela")
        if rela:
            gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
        else:
            gc.line_style = gtk.gdk.LINE_SOLID
        gc.line_width = 3
        if idx %2 == 0:
            area.window.draw_line(gc, alloc.width, alloc.height/2, alloc.width/2, 0)
        else:
            area.window.draw_line(gc, alloc.width, alloc.height/2, alloc.width/2, alloc.height)
    
    def edit_person_cb(self,obj):
        person_handle = obj.get_data(_PERSON)
        person = self.db.get_person_from_handle(person_handle)
        if person:
            self.edit_person(person)
            return True
        return 0


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
        return 0

    def on_childmenu_changed(self,obj):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""

        person_handle = obj.get_data(_PERSON)
        if person_handle:
            self.parent.emit("active-changed", (person_handle,))
            return 1
        return 0
    
    def change_force_size_cb(self,event,data):
        if data in [0,2,3,4,5]:
            self.force_size = data
            self.size_request_cb(self.parent_container,None) # switch to matching size
    
    def find_tree(self,person,index,depth,lst,val=0):
        """Recursively build a list of ancestors"""

        if depth > 5 or person == None:
            return
        lst[index] = (person,val,None)

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
            lst[index] = (person,val,family)
            father_handle = family.get_father_handle()
            if father_handle != None:
                father = self.db.get_person_from_handle(father_handle)
                self.find_tree(father,(2*index)+1,depth+1,lst,frel)
            mother_handle = family.get_mother_handle()
            if mother_handle != None:
                mother = self.db.get_person_from_handle(mother_handle)
                self.find_tree(mother,(2*index)+2,depth+1,lst,mrel)

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
            #(_("Set anchor"),self.on_anchor_set,1),
            #(_("Remove anchor"),self.on_anchor_removed,1),
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

    def add_settings_to_menu(self,menu):
        item = gtk.MenuItem(_("Tree size"))
        item.set_submenu(gtk.Menu())
        size_menu = item.get_submenu()
        
        current_image = gtk.image_new_from_stock(gtk.STOCK_APPLY,gtk.ICON_SIZE_MENU)
        current_image.show()
        
        entry = gtk.ImageMenuItem(_("Automatic"))
        entry.connect("activate", self.change_force_size_cb,0)
        if self.force_size == 0:
            entry.set_image(current_image)
        entry.show()
        size_menu.append(entry)

        for n in range(2,6):
            entry = gtk.ImageMenuItem(_("%d generations") % n)
            if self.force_size == n:
                entry.set_image(current_image)
            entry.connect("activate", self.change_force_size_cb,n)
            entry.show()
            size_menu.append(entry)
        
        size_menu.show()
        item.show()
        menu.append(item)
        

    def build_full_nav_menu_cb(self,obj,event):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation.
        """
        
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))

        person_handle = obj.get_data(_PERSON)
        person = self.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
        go_image.show()
        go_item = gtk.ImageMenuItem(NameDisplay.displayer.display(person))
        go_item.set_image(go_image)
        go_item.set_data(_PERSON,person_handle)
        go_item.connect("activate",self.on_childmenu_changed)
        go_item.show()
        menu.append(go_item)

        #edit_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
        #edit_image.show()
        edit_item = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        #edit_item.set_image(edit_image)
        edit_item.set_data(_PERSON,person_handle)
        edit_item.connect("activate",self.edit_person_cb)
        edit_item.show()
        menu.append(edit_item)

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

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            sp_item = gtk.ImageMenuItem(NameDisplay.displayer.display(spouse))
            sp_item.set_image(go_image)
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

                go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
                go_image.show()
                sib_item = gtk.ImageMenuItem(NameDisplay.displayer.display(sib))
                sib_item.set_image(go_image)
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

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            child_item = gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
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

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            par_item = gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
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
        self.add_settings_to_menu(menu)
        menu.popup(None,None,None,event.button,event.time)
        return 1

    def format_relation( self, family, line_count):
        text = ""
        for event_handle in family.get_event_list():
            event = self.db.get_event_from_handle(event_handle)
            if event:
                if line_count < 3:
                    return event.get_date()
                text += _(event.get_name())
                text += "\n"
                text += event.get_date()
                text += "\n"
                text += self.get_place_name(event.get_place_handle())
                if line_count < 5:
                   return text;
                break
        return text

    def get_place_name( self, place_handle):
        text = ""
        place = self.db.get_place_from_handle(place_handle)
        if place:
            place_title = self.db.get_place_from_handle(place_handle).get_title()
            if place_title != "":
                if len(place_title) > 25:
                    text = place_title[:24]+"..."
                else:
                    text = place_title
        return text
        
    def format_person( self, person, line_count):
        if not person:
            return ""
        name = NameDisplay.displayer.display(person)
        if line_count < 3:
            return name
        birth_ref = person.get_birth_ref()
        bd=""
        bp=""
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
            bd = birth.get_date()
            bp = self.get_place_name(birth.get_place_handle())
        death_ref = person.get_death_ref()
        dd=""
        dp=""
        if death_ref:
            death = self.db.get_event_from_handle(death_ref.ref)
            dd = death.get_date()
            dp = self.get_place_name(death.get_place_handle())
        if line_count < 5:
            return "%s\n* %s\n+ %s" % (name,bd,dd)
        else:
            return "%s\n* %s\n  %s\n+ %s\n  %s" % (name,bd,bp,dd,dp)
            
            

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

    
    birth_ref = person.get_birth_ref()
    if birth_ref:
        detail_text += format_event(db, _BORN,
                                    db.get_event_from_handle(birth_ref.ref))
    else:
        for event_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if event and event.get_name() == "Baptism":
                detail_text += format_event(db, _BAPT, event)
                break
            if event and event.get_name() == "Christening":
                detail_text += format_event(db, _CHRI, event)
                break

    death_ref = person.get_death_ref()
    if death_ref:
        detail_text += format_event(db, _DIED,
                                    db.get_event_from_handle(death_ref.ref))
    else:
        for event_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if event and event.get_name() == "Burial":
                detail_text += format_event(db, _BURI, event)
                break
            if event and event.get_name() == "Cremation":
                detail_text += format_event(db, _CREM, event)
                break

    return detail_text
