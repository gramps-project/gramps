# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
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

# $Id$

## Based on the paper:
##   http://www.cs.utah.edu/~draperg/research/fanchart/draperg_FHT08.pdf
## and the applet:
##   http://www.cs.utah.edu/~draperg/research/fanchart/demo/

## Found by redwood:
## http://www.gramps-project.org/bugs/view.php?id=2611

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Pango
from gi.repository import Gtk
import math
from gi.repository import Gdk
from cgi import escape
try:
    import cairo
except ImportError:
    pass

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
from gen.ggettext import gettext as _
from gen.plug import Gramplet
from gen.utils.db import (find_children, find_parents, find_witnessed_people)
from libformatting import FormattingHelper
import gen.lib
from gen.errors import WindowActiveError
from gui.editors import EditPerson
import gui.utils
from gui.widgets.fanchart import FanChartWidget

class FanChartGramplet(Gramplet):
    """
    The Gramplet code that realizes the FanChartWidget. 
    """
    def init(self):
        self.set_tooltip(_("Click to expand/contract person\nRight-click for options\nClick and drag in open area to rotate"))
        self.generations = 6
        self.format_helper = FormattingHelper(self.dbstate)
        self.gui.fan = FanChartWidget(self.generations, 
                        context_popup_callback=self.on_popup)
        self.gui.fan.format_helper = self.format_helper
        # Replace the standard textview with the fan chart widget:
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.fan)
        # Make sure it is visible:
        self.gui.fan.show()

    def active_changed(self, handle):
        """
        Method called when active person changes.
        """
        # Reset everything but rotation angle (leave it as is)
        self.update()

    def have_parents(self, person):
        """
        Returns True if a person has parents.
        """
        if person:
            m = self.get_parent(person, "female")
            f = self.get_parent(person, "male")
            return not m is f is None
        return False
            
    def have_children(self, person):
        """
        Returns True if a person has children.
        """
        if person:
            for family_handle in person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and len(family.get_child_ref_list()) > 0:
                    return True
        return False
            
    def get_parent(self, person, gender):
        """
        Get the father if gender == "male", or get mother otherwise.
        """
        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbstate.db.get_family_from_handle(family_id)
                if family:
                    if gender == "male":
                        person_handle = gen.lib.Family.get_father_handle(family)
                    else:
                        person_handle = gen.lib.Family.get_mother_handle(family)
                    if person_handle:
                        return self.dbstate.db.get_person_from_handle(person_handle)
        return None

    def main(self):
        """
        Fill the data structures with the active data. This initializes all 
        data.
        """
        self.gui.fan.reset_generations()
        active_handle = self.get_active('Person')
        person = self.dbstate.db.get_person_from_handle(active_handle)
        if not person: 
            name = None
        else:
            name = name_displayer.display(person)
        parents = self.have_parents(person)
        child = self.have_children(person)
        self.gui.fan.data[0][0] = (name, person, parents, child)
        for current in range(1, self.generations):
            parent = 0
            # name, person, parents, children
            for (n,p,q,c) in self.gui.fan.data[current - 1]:
                # Get father's details:
                person = self.get_parent(p, "male")
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.gui.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.gui.fan.angle[current][parent][3] = self.gui.fan.COLLAPSED
                parent += 1
                # Get mother's details:
                person = self.get_parent(p, "female")
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.gui.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.gui.fan.angle[current][parent][3] = self.gui.fan.COLLAPSED
                parent += 1
        self.gui.fan.queue_draw()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""
        self.set_active('Person', person_handle)
        return True

    def edit_person_cb(self, obj,person_handle):
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
            return True
        return False

    def copy_person_to_clipboard_cb(self, obj,person_handle):
        """Renders the person data into some lines of text and puts that into the clipboard"""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            cb = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), 
                        Gdk.SELECTION_CLIPBOARD)
            cb.set_text( self.format_helper.format_person(person,11))
            return True
        return False

    def on_popup(self, obj, event, person_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation. Copied from PedigreeView.
        """
        
        menu = Gtk.Menu()
        menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
        go_image.show()
        go_item = Gtk.ImageMenuItem(name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate",self.on_childmenu_changed,person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = Gtk.ImageMenuItem(Gtk.STOCK_EDIT)
        edit_item.connect("activate",self.edit_person_cb,person_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = Gtk.ImageMenuItem(Gtk.STOCK_COPY)
        clipboard_item.connect("activate",self.copy_person_to_clipboard_cb,person_handle)
        clipboard_item.show()
        menu.append(clipboard_item)

        # collect all spouses, parents and children
        linked_persons = []
        
        # Go over spouses and build their menu
        item = Gtk.MenuItem(label=_("Spouses"))
        fam_list = person.get_family_handle_list()
        no_spouses = 1
        for fam_id in fam_list:
            family = self.dbstate.db.get_family_from_handle(fam_id)
            if family.get_father_handle() == person.get_handle():
                sp_id = family.get_mother_handle()
            else:
                sp_id = family.get_father_handle()
            spouse = self.dbstate.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(Gtk.Menu())
                sp_menu = item.get_submenu()

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
            go_image.show()
            sp_item = Gtk.ImageMenuItem(name_displayer.display(spouse))
            sp_item.set_image(go_image)
            linked_persons.append(sp_id)
            sp_item.connect("activate",self.on_childmenu_changed,sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        menu.append(item)
        
        # Go over siblings and build their menu
        item = Gtk.MenuItem(label=_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for f in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(f)
            sib_list = fam.get_child_ref_list()
            for sib_ref in sib_list:
                sib_id = sib_ref.ref
                if sib_id == person.get_handle():
                    continue
                sib = self.dbstate.db.get_person_from_handle(sib_id)
                if not sib:
                    continue

                if no_siblings:
                    no_siblings = 0
                    item.set_submenu(Gtk.Menu())
                    sib_menu = item.get_submenu()

                if find_children(self.dbstate.db,sib):
                    label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(sib)))
                else:
                    label = Gtk.Label(label=escape(name_displayer.display(sib)))

                go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
                go_image.show()
                sib_item = Gtk.ImageMenuItem(None)
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0,0)
                sib_item.add(label)
                linked_persons.append(sib_id)
                sib_item.connect("activate",self.on_childmenu_changed,sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        
        # Go over children and build their menu
        item = Gtk.MenuItem(label=_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db,person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue
        
            if no_children:
                no_children = 0
                item.set_submenu(Gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.dbstate.db,child):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(child)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
            go_image.show()
            child_item = Gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate",self.on_childmenu_changed,child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db,person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db,par):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(par)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
            go_image.show()
            par_item = Gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate",self.on_childmenu_changed,par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
    
        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db,person):
            #if p_id in linked_persons:
            #    continue    # skip already listed family members
            
            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(Gtk.Menu())
                per_menu = item.get_submenu()

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
            go_image.show()
            per_item = Gtk.ImageMenuItem(None)
            per_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            per_item.add(label)
            per_item.connect("activate",self.on_childmenu_changed,p_id)
            per_item.show()
            per_menu.append(per_item)
        
        if no_related:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        menu.popup(None, None, None, None, event.button, event.time)
        return 1
