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
OBJECT   = "o"
ROWS     = "r"
INDEX    = "i"
TOPINST  = "top"
NAMEINST = "namelist"

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Bookmarks :
    "Handle the bookmarks interface for Gramps"
    
    #---------------------------------------------------------------------
    #
    # __init__ - Creates a the bookmark editor
    #
    #---------------------------------------------------------------------
    def __init__(self,bookmarks,map,menu,callback):
        self.map = map
        self.menu = menu
        self.bookmarks = bookmarks
        self.callback = callback
        self.redraw()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def redraw(self):
        if len(self.bookmarks) > 0:
            self.myMenu = gtk.GtkMenu()
            for person in self.bookmarks:
                item = gtk.GtkMenuItem(person.getPrimaryName().getName())
                item.show()
                item.connect("activate", self.callback , person)
                self.myMenu.append(item)
            self.menu.set_submenu(self.myMenu)
            self.menu.set_sensitive(1)
        else:
            self.menu.remove_submenu()
            self.menu.set_sensitive(0)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def add(self,person):
        if person not in self.bookmarks:
            utils.modified()
            self.bookmarks.append(person)
            item = gtk.GtkMenuItem(person.getPrimaryName().getName())
            item.show()
            item.connect("activate", self.callback, person)
            self.redraw()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def edit(self):
        
        top = libglade.GladeXML(const.bookFile,TOPINST)
        namelist = top.get_widget(NAMEINST)

        namelist.clear()
        self.index = 0
        for val in self.bookmarks:
            namelist.append([val.getPrimaryName().getName()])
            namelist.set_row_data(self.index,val)
            self.index = self.index + 1

        if self.index > 0:
            namelist.select_row(0,0)
            namelist.set_data(INDEX,0)
        else:
            namelist.set_data(INDEX,-1)
        namelist.set_data(ROWS,self.index)
            
        top.signal_autoconnect({
            "on_ok_clicked" : on_ok_clicked,
            "on_down_clicked" : on_down_clicked,
            "on_up_clicked" : on_up_clicked,
            "on_namelist_select_row" : on_namelist_select_row,
            "on_delete_clicked" : on_delete_clicked,
            "on_cancel_clicked" : on_cancel_clicked
            })

        topBox = top.get_widget(TOPINST)
        topBox.set_data(OBJECT,self)
        topBox.set_data(NAMEINST,namelist)
        topBox.show()
        self.redraw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_namelist_select_row(obj,row,junk,junk2):
    obj.set_data(INDEX,row)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_clicked(obj):
    index = obj.get_data(INDEX)
    rows = obj.get_data(ROWS)
    if index >= 0:
        obj.remove(index)
        obj.set_data(ROWS,rows-1)
        if index != 0:
            obj.select_row(0,0)
        else:
            obj.unselect_all()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_up_clicked(obj):
    index = obj.get_data(INDEX)
    if index > 0:
        obj.swap_rows(index-1,index)
        obj.set_data(INDEX,index-1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_down_clicked(obj):
    index = obj.get_data(INDEX)
    rows = obj.get_data(ROWS)
    if index != rows-1:
        obj.swap_rows(index+1,index)
        obj.set_data(INDEX,index+1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    bmobj = obj.get_data(OBJECT)
    namelist = obj.get_data(NAMEINST)
    del bmobj.bookmarks[0:]
    
    bmobj.myMenu = gtk.GtkMenu()
    for index in range(0,bmobj.index):
        person = namelist.get_row_data(index)
        if person == None:
            break
        bmobj.bookmarks.append(person)
        item = gtk.GtkMenuItem(person.getPrimaryName().getName())
        item.show()
        item.connect("activate", bmobj.callback , person)
        bmobj.myMenu.append(item)
        bmobj.menu.set_submenu(bmobj.myMenu)
    bmobj.redraw()
    obj.destroy()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_cancel_clicked(obj):
    obj.destroy()



