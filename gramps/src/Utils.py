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
import gtk
import gnome.mime
import gnome.util
from gnome.ui import GnomeWarningDialog

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
from intl import gettext
_ = gettext

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
    import GrampsCfg
    
    detail = ""
    if GrampsCfg.show_detail:
        if obj.getNote() != "":
            detail = "N"
        if len(obj.getSourceRefList()) > 0:
            detail = detail + "S"
        if priv and obj.getPrivacy():
            detail = detail + "P"
    return detail

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
    
    if len(clist.selection) == 0:
        current_row = 0
    else:
        current_row = clist.selection[0]

    clist.select_row(current_row,0)
    clist.moveto(current_row,0)
    clist.thaw()
    return index

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_selected(obj,list):
    if len(obj.selection) == 0:
        return 0
    del list[obj.selection[0]]
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_menuitem(menu,msg,obj,func):
    item = gtk.GtkMenuItem(msg)
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
    prog = ""
    open = ""
    edit = ""
    for key in gnome.mime.get_keys(type):
        if key == 'view':
            prog = string.split(gnome.mime.get_value(type,key))
        if key == 'open':
            open = string.split(gnome.mime.get_value(type,key))
        if key == 'edit':
            edit = string.split(gnome.mime.get_value(type,key))
    if prog == "" and open == "" and edit == "":
        GnomeWarningDialog("Sorry, I cannot find a viewer for %s type" % type)
        return

    if prog == "" and open == "":
        prog = edit
    else:
        prog = open
    
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
    placenamemap = {}
    for src in values:
        placenamemap["%s [%s]" % (src.get_title(),src.getId())] = src
    placenames = placenamemap.keys()
    placenames.sort()
    for key in placenames:
        src = placenamemap[key]
        l = gtk.GtkLabel(key)
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

def find_icon(mtype):
    icon = None
    nicon = None
    for k in gnome.mime.get_keys(mtype):
        if k == "icon-filename":
            icon = gnome.mime.get_value(mtype,k)
        elif k == "icon_filename":
            nicon = gnome.mime.get_value(mtype,k)
    if nicon:
	p = "%s/%s" % (gnome.util.pixmap_file("nautilus"),nicon)
	if os.path.isfile(p):
            return p
	p = "%s.png" % p
	if os.path.isfile(p):
            return p
    if icon:
        return icon
    return ""

def get_mime_type(file):
    if os.path.isfile(file) or os.path.isdir(file):
	mtype = gnome.mime.type_of_file(file)
	if len(string.split(mtype,"/")) != 2:
            mtype = gnome.mime.type(file)
    else:
        mtype = gnome.mime.type(file)
    return mtype

def get_mime_description(type):
    for key in gnome.mime.get_keys(type):
        if key == "description":
            return gnome.mime.get_value(type,key)
    return type


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
        combo.entry.signal_connect("focus_out_event", combo_lost_focus, combo)

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
# public knowledge of the GtkCombo data structure, not on any private
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

    # Walk the GtkList in the combo box
    for item in combo.list.children():
        # Each item is a GtkListItem, whose first and only child is a
        # GtkLabel.  This is the magic.
        label = item.children()[0]
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
    myMenu = gtk.GtkMenu()

    for key in keys:
        if key == "default":
            menuitem = gtk.GtkMenuItem(_("default"))
        else:
            menuitem = gtk.GtkMenuItem(key)
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
#  Iterate over ancestors.
#
#-------------------------------------------------------------------------
def for_each_ancestor(start, func, data):
    """
    Recursively iterate (breadth-first) over ancestors of
    people listed in start.
    Call func(data,pid) for the Id of each person encountered.
    Exit and return 1, as soon as func returns true.
    Return 0 otherwise.
    """
    todo = start
    doneIds = {}
    while len(todo):
        p = todo.pop()
        pid = p.getId()
        # Don't process the same Id twice.  This can happen
        # if there is a cycle in the database, or if the
        # initial list contains X and some of X's ancestors.
        if doneIds.has_key(pid):
            continue
        doneIds[pid] = 1
        if func(data,pid):
            return 1
        for fam, mrel, frel in p.getParentList():
            f = fam.getFather()
            m = fam.getMother()
            if f: todo.append(f)
            if m: todo.append(m)
    return 0
