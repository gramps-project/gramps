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

"Handle bookmarks for the gramps interface"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk 
import libglade

#-------------------------------------------------------------------------
#
# Local modules
#
#-------------------------------------------------------------------------
import const
import utils

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_TOPINST  = "top"
_NAMEINST = "namelist"

#-------------------------------------------------------------------------
#
# Interface to gramps' bookmarks. Handles building the bookmarks menu
# for the main window, and provides the bookmark editor.
#
#-------------------------------------------------------------------------
class Bookmarks :
    "Handle the bookmarks interface for Gramps"
    
    #---------------------------------------------------------------------
    #
    # __init__ - Creates a the bookmark editor
    #
    # arguments are:
    #    bookmarks - list of People
    #    menu - parent menu to attach users
    #    callback - task to connect to the menu item as a callback
    #
    #---------------------------------------------------------------------
    def __init__(self,bookmarks,menu,callback):
        self.menu = menu
        self.bookmarks = bookmarks
        self.callback = callback
        self.redraw()

    #---------------------------------------------------------------------
    #
    # redraw - (re)create the pulldown menu
    #
    #---------------------------------------------------------------------
    def redraw(self):
        if len(self.bookmarks) > 0:
            self.myMenu = gtk.GtkMenu()
            for person in self.bookmarks:
                self.add_to_menu(person)
            self.menu.set_submenu(self.myMenu)
            self.menu.set_sensitive(1)
        else:
            self.menu.remove_submenu()
            self.menu.set_sensitive(0)

    #---------------------------------------------------------------------
    #
    # add - adds the person to the bookmarks, appended to the botom
    #
    #---------------------------------------------------------------------
    def add(self,person):
        if person not in self.bookmarks:
            utils.modified()
            self.bookmarks.append(person)
            self.redraw()

    #---------------------------------------------------------------------
    #
    # add_to_menu - adds a person's name to the drop down menu
    #
    #---------------------------------------------------------------------
    def add_to_menu(self,person):
        item = gtk.GtkMenuItem(person.getPrimaryName().getName())
        item.connect("activate", self.callback, person)
        item.show()
        self.myMenu.append(item)
        
    #---------------------------------------------------------------------
    #
    # edit - display the bookmark editor.
    #
    # The current bookmarked people are inserted into the namelist,
    # attaching the person object to the corresponding row. The currently
    # selected row is attached to the name list. This is either 0 if the
    # list is not empty, or -1 if it is.
    #
    #---------------------------------------------------------------------
    def edit(self):
        top = libglade.GladeXML(const.bookFile,_TOPINST)
        self.namelist = top.get_widget(_NAMEINST)
        index = 0
        for person in self.bookmarks:
            self.namelist.append([person.getPrimaryName().getName()])
            self.namelist.set_row_data(index,person)
            index = index + 1

        top.signal_autoconnect({
            "on_ok_clicked"     : self.on_ok_clicked,
            "on_down_clicked"   : self.on_down_clicked,
            "on_up_clicked"     : self.on_up_clicked,
            "on_delete_clicked" : self.on_delete_clicked,
            "on_cancel_clicked" : self.on_cancel_clicked
            })

    def on_delete_clicked(self,obj):
        if len(obj.selection) > 0:
            index = obj.selection[0]
            obj.remove(index)

    def on_up_clicked(self,obj):
        if len(obj.selection) > 0:
            index = obj.selection[0]
            obj.swap_rows(index-1,index)

    def on_down_clicked(self,obj):
        if len(obj.selection) > 0:
            index = obj.selection[0]
            if index != obj.rows-1:
                obj.swap_rows(index+1,index)

    def on_ok_clicked(self,obj):
        del self.bookmarks[0:]
    
        for index in range(0,self.namelist.rows):
            person = self.namelist.get_row_data(index)
            if person:
                self.bookmarks.append(person)

        self.redraw()
        obj.destroy()
    
    def on_cancel_clicked(self,obj):
        obj.destroy()



