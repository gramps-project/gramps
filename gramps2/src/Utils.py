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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
try:
    import pygtk; pygtk.require('2.0')
except ImportError: # not set up for parallel install
    pass 
import gtk
import grampslib

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import RelImage

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext as _

#-------------------------------------------------------------------------
#
# modified flag
#
#-------------------------------------------------------------------------
_modifiedFlag = 0
_autotime_val = 1
_autosave_fun = None
_autosave_tim = None
_autosave_val = None

LISTOBJ = "s"
OBJECT  = "o"

#-------------------------------------------------------------------------
#
# Sets the modified flag, which is used to determine if the database
# needs to be saved.  Anytime a routine modifies data, it should call
# this routine.
#
#-------------------------------------------------------------------------
def modified():
    global _modifiedFlag, _autosave_tim
    if _autosave_fun and not _autosave_tim:
        _autosave_tim = gtk.timeout_add(60000*_autotime_val,_autosave_fun)
    _modifiedFlag = 1

def enable_autosave(fun,value):
    global _autosave_fun
    global _autosave_val
    if fun != None:
        _autosave_fun = fun
    _autosave_val = value

def disable_autosave():
    global _autosave_fun
    _autosave_fun = None

def clear_timer():
    global _autosave_tim
    if _autosave_tim:
        gtk.timeout_remove(_autosave_tim)
        _autosave_tim = None

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

def family_name(family):
    """Builds a name for the family from the parents names"""
    father = family.getFather()
    mother = family.getMother()
    if father and mother:
        fname = father.getPrimaryName().getName()
        mname = mother.getPrimaryName().getName()
        name = _("%s and %s") % (fname,mname)
    elif father:
        name = father.getPrimaryName().getName()
    else:
        name = mother.getPrimaryName().getName()
    return name
        
def phonebook_from_name(name,alt):
    if alt:
        return "%s *" % name.getName()
    else:
        return name.getName()

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
#
#
#-------------------------------------------------------------------------
def get_detail_flags(obj,priv=1):
    return ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_text(obj,priv=1):
    if obj.getNote() != "":
        details = "%s" % _("Note")
    else:
        details = ""
    if len(obj.getSourceRefList()) > 0:
        if details == "":
            details = _("Source")
        else:
            details = "%s, %s" % (details,_("Source"))
    if priv and obj.getPrivacy() == 1:
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
    myMenu = gtk.Menu()
    index = 0
    for name in const.confidence:
        item = gtk.MenuItem(name)
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
    clist.clear()
    
    index = 0
    for object in dlist:
        col = 0
        iter = clist.append()
        for data in func(object):
            clist.set_value(iter,col,data)
            col = col + 1
        index = index + 1
    return index

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_selected(obj,list):
    sel = obj.get_selection()
    model,iter = sel.get_selected()
    if iter:
        index = model.get_path(iter)[0]
        del list[index]
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_menuitem(menu,msg,obj,func):
    item = gtk.MenuItem(msg)
    item.set_data(OBJECT,obj)
    item.connect("activate",func)
    item.show()
    menu.append(item)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def view_photo(photo):
    type = photo.getMimeType()
    prog = grampslib.default_application_command(type)

    if not prog:
        return
    
    args = string.split(prog)
    args.append(photo.getPath())
    
    if os.fork() == 0:
        os.execvp(args[0],args)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def strip_id(text):
    index = string.rfind(text,'[')
    if (index > 0):
        text = text[:index]
        text = string.rstrip(text)
    return text

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def attach_places(values,combo,place):
    l = gtk.Label("")
    l.show()
    l.set_alignment(0,0.5)
    c = gtk.ListItem()
    c.add(l)
    c.set_data(LISTOBJ,None)
    c.show()
    sel_child = c
    list = [c]
    mymap = {}
    placenamemap = {}
    for src in values:
        placenamemap["%s [%s]" % (src.get_title(),src.getId())] = src
    placenames = placenamemap.keys()
    placenames.sort()
    for key in placenames:
        src = placenamemap[key]
        l = gtk.Label(key)
        l.show()
        l.set_alignment(0,0.5)
        c = gtk.ListItem()
        c.add(l)
        c.set_data(LISTOBJ,src)
        c.show()
        list.append(c)
        if src == place:
            sel_child = c
        mymap[src] = c

    combo.disable_activate()
    combo.list.clear_items(0,-1)
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

def nautilus_icon(icon,type):
    import GrampsCfg
    
    theme = GrampsCfg.client.get_string("/desktop/gnome/file_views/icon_theme")

    if icon :
        newicon = "%s/%s/%s.png" % (const.nautdir,theme,icon)
        if os.path.isfile(newicon):
            return newicon
        else:
            newicon = "%s/document-icons/%s.png" % (const.pixdir,icon)
            if os.path.isfile(newicon):
                return newicon
        return None
    elif type == "x-directory/":
        if theme:
            newicon = "%s/%s/i-directory.png" % (const.nautdir,theme)
        else:
            newicon = "%s/gnome-folder.png" % const.pixdir
        if os.path.isfile(newicon):
            return newicon
        return None
    else:
        icontmp = type.replace('/','-')
        if theme:
            newicon = "%s/%s/gnome-%s.png" % (const.nautdir,theme,icontmp)
            if os.path.isfile(newicon):
                return newicon
            else:
                newicon = "%s/document-icons/gnome-%s.png" % (const.nautdir,icontmp)
                if os.path.isfile(newicon):
                    return newicon
        return None

def find_icon(mtype):
    n = nautilus_icon(None,mtype)
    if n:
        return n
    else:
        return const.icon

def get_mime_type(file):
    type = grampslib.gnome_vfs_mime_type_from_name(file)
    if type:
        return type
    return "unknown"

def get_mime_description(type):
    value = grampslib.gnome_vfs_mime_get_description(type)
    if value:
        return value
    return ""

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's birthday, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def birthday(person):
    if person:
        return person.getBirth().getQuoteDate()
    else:
        return ""

def thumb_path(dir,mobj):
    type = mobj.getMimeType()
    if type[0:5] == "image":
        thumb = "%s/.thumb/%s.jpg" % (dir,mobj.getId()) 
        try:
            if RelImage.check_thumb(mobj.getPath(),thumb,const.thumbScale):
                return thumb
            else:
                return find_icon(type)
        except:
            return find_icon(type)
    else:
        return find_icon(type)

#-------------------------------------------------------------------------
#
# Sets up a delayed (0.005 sec) handler for text completion.  Text
# completion cannot be handled directly in this routine because, for
# some reason, the select_region() function doesn't work when called
# from signal handlers.  Go figure.
#
# Thanks to iain@nodata.demon.co.uk (in mail from 1999) for the idea
# to use a timer to get away from the problems with signal handlers
# and the select_region function.
#
#-------------------------------------------------------------------------
def combo_insert_text(combo,new_text,new_text_len,i_dont_care):
    # One time setup to clear selected region when user moves on
    if (not combo.get_data("signal_set")):
        combo.set_data("signal_set",1)
        combo.entry.connect("focus_out_event", combo_lost_focus, combo)

    # Nuke the current timer if the user types fast enough
    timer = combo.get_data("timer");
    if (timer):
        gtk.timeout_remove(timer)

    # Setup a callback timer so we can operate outside of a signal handler
    timer = gtk.timeout_add(5, combo_timer_callback, combo)
    combo.set_data("timer", timer);

#-------------------------------------------------------------------------
#
# The combo box entry field lost focus.  Go clear any selection.  Why
# this form of a select_region() call works in a signal handler and
# the other form doesn't is a mystery.
#
#-------------------------------------------------------------------------
def combo_lost_focus(entry,a,b):
    entry.select_region(0, 0)

#-------------------------------------------------------------------------
#
# The workhorse routine of file completion.  This routine grabs the
# current text of the entry box, and grubs through the list item
# looking for any case insensitive matches.  This routine relies on
# public knowledge of the Combo data structure, not on any private
# data.
#
# These three completion routines have only one gramps specific hook,
# and can be easily ported to any program.
#
#-------------------------------------------------------------------------
def combo_timer_callback(combo):
    # Clear any timer
    timer = combo.get_data("timer");
    if (timer):
        gtk.timeout_remove(timer)

    # Get the user's text
    entry = combo.entry
    typed = entry.get_text()
    if (not typed):
        return
    typed_lc = string.lower(typed)

    # Walk the List in the combo box
    for item in combo.list.get_children():
        # Each item is a ListItem, whose first and only child is a
        # Label.  This is the magic.
        label = item.get_children()[0]
        label_text = label.get()
        if (not label_text):
            continue

        # Gramps specific code to remove trailing '[id]' from the
        # label.
        index = string.rfind(label_text,'[')
        if (index > 0):
            label_text = label_text[:index]
            label_text = string.rstrip(label_text)

        # Back to the generic code.  Convert to lower case
        label_text_lc = string.lower(label_text)

        # If equal, no need to add any text
        if (typed_lc == label_text_lc):
            return

        # If typed text is a substring of the label text, then fill in
        # the entry field with the full text (and correcting
        # capitalization), and then select all the characters that
        # don't match.  With the user's enxt keystroke these will be
        # replaced if they are incorrect.
        if (string.find(label_text_lc,typed_lc) == 0):
            entry.set_text(label_text)
            entry.set_position(len(typed))
            entry.select_region(len(typed), -1)
            return

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_string_optmenu(mapping, start_val):
    index = 0
    start_index = 0
    keys = mapping.keys()
    keys.sort()
    myMenu = gtk.Menu()

    for key in keys:
        if key == "default":
            menuitem = gtk.MenuItem(_("default"))
        else:
            menuitem = gtk.MenuItem(key)
        menuitem.set_data("d", mapping[key])
        menuitem.show()
        myMenu.append(menuitem)
        if key == start_val:
            start_index = index
        index = index + 1
    
    if start_index:
        myMenu.set_active(start_index)
    return myMenu


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_columns(tree,list):
    cnum = 0
    for name in list:
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
        column.set_min_width(name[1])
        if name[2] >= 0:
            column.set_sort_column_id(name[2])
        if name[0] == '':
            column.set_clickable(gtk.TRUE)
            column.set_visible(gtk.FALSE)
        cnum = cnum + 1
        tree.append_column(column)
