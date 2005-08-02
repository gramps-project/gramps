#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Handle bookmarks for the gramps interface"

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gnome 

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import NameDisplay

#-------------------------------------------------------------------------
#
# Bookmarks
#
#-------------------------------------------------------------------------
class Bookmarks :
    "Handle the bookmarks interface for Gramps"
    
    def __init__(self,db,bookmarks,menu,callback):
        """
        Creates a the bookmark editor

        bookmarks - list of People
        menu - parent menu to attach users
        callback - task to connect to the menu item as a callback
        """
        self.db = db
        self.menu = menu
        self.bookmarks = bookmarks
        self.callback = callback
        self.redraw()

    def redraw(self):
        """Create the pulldown menu"""
        if len(self.bookmarks) > 0:
            self.myMenu = gtk.Menu()
            for person_handle in self.bookmarks:
                self.add_to_menu(person_handle)
            self.menu.set_submenu(self.myMenu)
            self.menu.set_sensitive(1)
        else:
            self.menu.remove_submenu()
            self.menu.set_sensitive(0)

    def add(self,person_handle):
        """appends the person to the bottom of the bookmarks"""
        if person_handle not in self.bookmarks:
            self.bookmarks.append(person_handle)
            self.redraw()

    def add_to_menu(self,person_handle):
        """adds a person's name to the drop down menu"""
        person = self.db.get_person_from_handle(person_handle)
        if person:
            name = NameDisplay.displayer.display(person)
            item = gtk.MenuItem(name)
            item.connect("activate", self.callback, person_handle)
            item.show()
            self.myMenu.append(item)

    def draw_window(self):
        """Draws the bookmark dialog box"""
        title = "%s - GRAMPS" % _("Edit Bookmarks")
        self.top = gtk.Dialog(title)
        self.top.set_default_size(400,350)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % _("Edit Bookmarks"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label,0,0,5)
        box = gtk.HBox()
        self.top.vbox.pack_start(box,1,1,5)
        self.namelist = gtk.CList(1)
        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(self.namelist)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        box.pack_start(slist,1,1,5)
        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        bbox.set_spacing(6)
        up = gtk.Button()
        up.set_label(gtk.STOCK_GO_UP)
        up.set_use_stock(1)
        down = gtk.Button()
        down.set_label(gtk.STOCK_GO_DOWN)
        down.set_use_stock(1)
        delete = gtk.Button()
        delete.set_label(gtk.STOCK_REMOVE)
        delete.set_use_stock(1)
        up.connect('clicked', self.up_clicked)
        down.connect('clicked',self.down_clicked)
        delete.connect('clicked',self.delete_clicked)
        self.top.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.top.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        bbox.add(up)
        bbox.add(down)
        bbox.add(delete)
        box.pack_start(bbox,0,0,5)
        self.top.show_all()
        
    def edit(self):
        """
        display the bookmark editor.

        The current bookmarked people are inserted into the namelist,
        attaching the person object to the corresponding row. The currently
        selected row is attached to the name list. This is either 0 if the
        list is not empty, or -1 if it is.
        """
        self.draw_window()
        index = 0
        for person_handle in self.bookmarks:
            person = self.db.get_person_from_handle(person_handle)
            if person:
                name = NameDisplay.displayer.display(person)
                self.namelist.append([name])
                self.namelist.set_row_data(index,person_handle)
                index = index + 1

        self.response = self.top.run()
        if self.response == gtk.RESPONSE_OK:
            self.ok_clicked()
        elif self.response == gtk.RESPONSE_HELP:
            self.help_clicked()
        self.top.destroy()

    def delete_clicked(self,obj):
        """Removes the current selection from the list"""
        if len(self.namelist.selection) > 0:
            self.namelist.remove(self.namelist.selection[0])

    def up_clicked(self,obj):
        """Moves the current selection up one row"""
        if len(self.namelist.selection) > 0:
            index = self.namelist.selection[0]
            self.namelist.swap_rows(index-1,index)

    def down_clicked(self,obj):
        """Moves the current selection down one row"""
        if len(self.namelist.selection) > 0:
            index = self.namelist.selection[0]
            if index != self.namelist.rows-1:
                self.namelist.swap_rows(index+1,index)

    def ok_clicked(self):
        """Saves the current bookmarks from the list"""
        del self.bookmarks[0:]
        for index in range(0,self.namelist.rows):
            person_handle = self.namelist.get_row_data(index)
            if person_handle:
                self.bookmarks.append(person_handle)
        self.redraw()

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-nav')
        self.response = self.top.run()

