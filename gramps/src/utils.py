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

import gtk
import gnome.mime
import string
import os
import const
import intl

_ = intl.gettext

_modifiedFlag  = 0

LISTOBJ = "s"
INDEX   = "i"

#-------------------------------------------------------------------------
#
# Sets the modified flag, which is used to determine if the database
# needs to be saved.  Anytime a routine modifies data, it should call
# this routine.
#
#-------------------------------------------------------------------------
def modified():
    global _modifiedFlag
    _modifiedFlag = 1

#-------------------------------------------------------------------------
#
# Clears the modified flag.  Should be called after data is saved.
#
#-------------------------------------------------------------------------
def clearModified():
    global _modifiedFlag
    _modifiedFlag = 0

#-------------------------------------------------------------------------
#
# Returns the modified flag
#
#-------------------------------------------------------------------------
def wasModified():
    return _modifiedFlag

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def phonebook_name(person):
    if person:
        return person.getPrimaryName().getName()
    else:
        return ""

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def phonebook_from_name(name,alt):
    if alt:
        return "%s *" % name.getName()
    else:
        return name.getName()

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def normal_name(person):
    if person:
        return person.getPrimaryName().getRegularName()
    else:
        return ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def destroy_passed_object(obj):
    obj.destroy()
    while gtk.events_pending():
        gtk.mainiteration()

#-------------------------------------------------------------------------
#
# Get around python's interpretation of commas/periods in floating
# point numbers
#
#-------------------------------------------------------------------------

if string.find("%.3f" % 1.2, ",") == -1:
    _use_comma = 0
else:
    _use_comma = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def txt2fl(st):
    if _use_comma:
        return string.atof(string.replace(st,'.',','))
    else:
        return string.atof(string.replace(st,',','.'))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fl2txt(fmt,val):
    return string.replace(fmt % val, ',', '.')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_flags(obj):
    import Config
    
    detail = ""
    if Config.show_detail:
        if obj.getNote() != "":
            detail = "N"
        if obj.getSourceRef().getBase():
            detail = detail + "S"
        if obj.getPrivacy():
            detail = detail + "P"
    return detail

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_text(obj):
    if obj.getNote() != "":
        details = "%s" % _("Note")
    else:
        details = ""
    if obj.getSourceRef().getBase() != None:
        if details == "":
            details = _("Source")
        else:
            details = "%s, %s" % (details,_("Source"))
    if obj.getPrivacy() == 1:
        if details == "":
            details = _("Private")
        else:
            details = "%s, %s" % (details,_("Private"))
    return details

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_confidence_menu(menu):
    myMenu = gtk.GtkMenu()
    index = 0
    for name in const.confidence:
        item = gtk.GtkMenuItem(name)
        item.set_data("a",index)
        item.show()
        myMenu.append(item)
        index = index + 1
    menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def redraw_list(dlist,clist,func):
    clist.freeze()
    clist.clear()
    
    index = 0
    for object in dlist:
        clist.append(func(object))
        clist.set_row_data(index,object)
        index = index + 1
    
    current_row = clist.get_data(INDEX)
    if index > 0:
        if current_row <= 0:
            current_row = 0
        elif index <= current_row:
            current_row = current_row - 1
        clist.select_row(current_row,0)
        clist.moveto(current_row,0)
    clist.set_data(INDEX,current_row)
    clist.thaw()
    return index

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_selected(obj,list):
    row = obj.get_data(INDEX)
    if row < 0:
        return 0
    del list[row]
    if row > len(list)-1:
        obj.set_data(INDEX,row-1)
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_menuitem(menu,msg,obj,func):
    item = gtk.GtkMenuItem(msg)
    item.set_data("m",obj)
    item.connect("activate",func)
    item.show()
    menu.append(item)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def view_photo(photo):
    type = gnome.mime.type(photo.getPath())
    prog = string.split(gnome.mime.get_value(type,'view'))
    args = []
    for val in prog:
        if val == "%f":
            args.append(photo.getPath())
        else:
            args.append(val)
    
    if os.fork() == 0:
        os.execvp(args[0],args)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def attach_places(values,combo,place):
    l = gtk.GtkLabel("")
    l.show()
    l.set_alignment(0,0.5)
    c = gtk.GtkListItem()
    c.add(l)
    c.set_data(LISTOBJ,None)
    c.show()
    sel_child = c
    list = [c]
    mymap = {}
    for src in values:
        l = gtk.GtkLabel("%s [%s]" % (src.get_title(),src.getId()))
        l.show()
        l.set_alignment(0,0.5)
        c = gtk.GtkListItem()
        c.add(l)
        c.set_data(LISTOBJ,src)
        c.show()
        list.append(c)
        if src == place:
            sel_child = c
        mymap[src] = c

    combo.list.append_items(list)
    combo.list.select_child(sel_child)

    for v in mymap.keys():
        combo.set_item_string(mymap[v],v.get_title())
        

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_place_from_list(obj):
    select = obj.list.get_selection()
    if len(select) == 0:
        return None
    else:
        return select[0].get_data(LISTOBJ)
