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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os
import locale

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk
import gnome

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import RelImage
import GrampsMime

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# modified flag
#
#-------------------------------------------------------------------------
_history_brokenFlag = 0

def history_broken():
    global _history_brokenFlag
    _history_brokenFlag = 1

#-------------------------------------------------------------------------
#
# force_unicode
#
#-------------------------------------------------------------------------
_t = type(u'')

def force_unicode(n):
    if type(n) != _t:
        return (unicode(n).lower(),unicode(n))
    else:
        return (n.lower(),n)

#-------------------------------------------------------------------------
#
# Clears the modified flag.  Should be called after data is saved.
#
#-------------------------------------------------------------------------
def clearHistory_broken():
    global _history_brokenFlag
    _history_brokenFlag = 0

def wasHistory_broken():
    return _history_brokenFlag

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def phonebook_name(person):
    if person:
        return person.get_primary_name().get_name()
    else:
        return u''

def phonebook_upper_name(person):
    if person:
        return person.get_primary_name().get_upper_name()
    else:
        return u''

def normal_name(person):
    if person:
        return person.get_primary_name().get_regular_name()
    else:
        return u''

def upper_name(person):
    if person:
        return person.get_primary_name().get_regular_upper_name()
    else:
        return u''

def family_name(family,db):
    """Builds a name for the family from the parents names"""
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = father.get_primary_name().get_name()
        mname = mother.get_primary_name().get_name()
        name = _("%s and %s") % (fname,mname)
    elif father:
        name = father.get_primary_name().get_name()
    else:
        name = mother.get_primary_name().get_name()
    return name

def family_upper_name(family,db):
    """Builds a name for the family from the parents names"""
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = father.get_primary_name().get_upper_name()
        mname = mother.get_primary_name().get_upper_name()
        name = _("%s and %s") % (fname,mname)
    elif father:
        name = father.get_primary_name().get_upper_name()
    else:
        name = mother.get_primary_name().get_upper_name()
    return name
        

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def destroy_passed_object(obj):
    obj.destroy()
    while gtk.events_pending():
        gtk.main_iteration()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_text(obj,priv=1):
    if obj.get_note() != "":
        details = "%s" % _("Note")
    else:
        details = ""
    if len(obj.get_source_references()) > 0:
        if details == "":
            details = _("Source")
        else:
            details = "%s, %s" % (details,_("Source"))
    if priv and obj.get_privacy() == 1:
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
    for obj in dlist:
        col = 0
        node = clist.append()
        for data in func(obj):
            clist.set_value(node,col,data)
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
    model,node = sel.get_selected()
    if node:
        index = model.get_path(node)[0]
        del list[index]
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_menuitem(menu,msg,obj,func):
    item = gtk.MenuItem(msg)
    item.set_data('o',obj)
    item.connect("activate",func)
    item.show()
    menu.append(item)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def view_photo(photo):
    mime_type = photo.get_mime_type()
    try:
        data = GrampsMime.get_application(mime_type)
        prog = data[0]
    except:
        return
    
    args = string.split(prog)
    args.append(photo.get_path())
    
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

def nautilus_icon(icon,mime_type):
    import GrampsGconfKeys
    
    theme = GrampsGconfKeys.client.get_string("/desktop/gnome/file_views/icon_theme")

    if icon :
        newicon = "%s/%s/%s.png" % (const.nautdir,theme,icon)
        if os.path.isfile(newicon):
            return newicon
        else:
            newicon = "%s/document-icons/%s.png" % (const.pixdir,icon)
            if os.path.isfile(newicon):
                return newicon
        return None
    elif mime_type == "x-directory/":
        if theme:
            newicon = "%s/%s/i-directory.png" % (const.nautdir,theme)
        else:
            newicon = "%s/gnome-folder.png" % const.pixdir
        if os.path.isfile(newicon):
            return newicon
        return None
    else:
        icontmp = mime_type.replace('/','-')
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
    try:
        return gnome.vfs.get_mime_type(file)
    except:
        return "unknown"

def get_mime_description(mime_type):
    try:
        value = gnome.vfs.mime_get_description(mime_type)
        if value:
            return value
        else:
            return ''
    except:
        return ''
    

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def thumb_path(dir,mobj):
    mime_type = mobj.get_mime_type()

    if mime_type[0:5] == "image":
        thumb = "%s/.thumb/%s.jpg" % (os.path.dirname(dir),mobj.get_gramps_id())
        try:
            if RelImage.check_thumb(mobj.get_path(),thumb,const.thumbScale):
                return thumb
            else:
                return find_icon(mime_type)
        except:
            return find_icon(mime_type)
    else:
        return find_icon(mime_type)

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
        menuitem.set_data("l", key)
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
        renderer.set_fixed_height_from_font(1)
        column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
        column.set_min_width(name[1])
        if name[2] >= 0:
            column.set_sort_column_id(name[2])
        if name[0] == '':
            column.set_clickable(gtk.TRUE)
            column.set_visible(gtk.FALSE)
        cnum = cnum + 1
        tree.append_column(column)

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
        pid = p.get_handle()
        # Don't process the same Id twice.  This can happen
        # if there is a cycle in the database, or if the
        # initial list contains X and some of X's ancestors.
        if doneIds.has_key(pid):
            continue
        doneIds[pid] = 1
        if func(data,pid):
            return 1
        for fam, mrel, frel in p.get_parent_family_handle_list():
            f = fam.get_father_handle()
            m = fam.get_mother_handle()
            if f: todo.append(f)
            if m: todo.append(m)
    return 0

def title(n):
    return '<span weight="bold" size="larger">%s</span>' % n

def set_title_label(xmlobj,t):
    title_label = xmlobj.get_widget('title')
    title_label.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title_label.set_use_markup(gtk.TRUE)

def set_titles(window,title,t,msg=None):
    title.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title.set_use_markup(gtk.TRUE)
    if msg:
        window.set_title('%s - GRAMPS' % msg)
    else:
        window.set_title('%s - GRAMPS' % t)

def gfloat(val):
    """Converts to floating number, taking care of possible locale differences.
    
    Useful for reading float values from text entry fields 
    while under non-English locale.
    """

    try:
        return float(val)
    except:
        try:
            return float(val.replace('.',','))
        except:
            return float(val.replace(',','.'))
    return 0.0

def gformat(val):
    """Performs ("%.3f" % val) formatting with the resulting string always 
    using dot ('.') as a decimal point.
    
    Useful for writing float values into XML when under non-English locale.
    """

    decimal_point = locale.localeconv()['decimal_point']
    return_val = "%.3f" % val
    return return_val.replace(decimal_point,'.')

def search_for(name):
    for i in os.environ['PATH'].split(':'):
        fname = os.path.join(i,name)
        if os.access(fname,os.X_OK) and not os.path.isdir(fname):
            return 1
    return 0
                  
#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    "Simple-and-dirty way to get roman numerals for small numbers."

    romans = {
        1 : 'I', 2 : 'II', 3 : 'III', 4 : 'IV', 5 : 'V', 
        6 : 'VI', 7 : 'VII', 8 : 'VIII', 9 : 'IX', 10 : 'X', 
        11 : 'XI', 12 : 'XII', 13 : 'XIII', 14 : 'XIV', 15 : 'XV', 
        16 : 'XVI', 17 : 'XVII', 18 : 'XVIII', 19 : 'XIX', 20 : 'XX', 
        21 : 'XXI', 22 : 'XXII', 23 : 'XXIII', 24 : 'XXIV', 25 : 'XXV', 
        26 : 'XXVI', 27 : 'XXVII', 28 : 'XXVIII', 29 : 'XXIX', 30 : 'XXX', 
        31 : 'XXXI', 32 : 'XXXII', 33 : 'XXXIII', 34 : 'XXXIV', 35 : 'XXXV', 
        36 : 'XXXVI', 37 : 'XXXVII', 38 : 'XXXVIII', 39 : 'XXXIX', 40 : 'XV' 
    }
    
    if isinstance(num,type(1)) and num<=41:
        rnum = romans[num]
        return rnum
    else:
        return '?'

#-------------------------------------------------------------------------
#
#  Change label apperance
#
#-------------------------------------------------------------------------
def bold_label(label):
    text = unicode(label.get_text())
    label.set_text("<b>%s</b>" % text )
    label.set_use_markup(1)

def unbold_label(label):
    text = unicode(label.get_text())
    text = string.replace(text,'<b>','')
    text = string.replace(text,'</b>','')
    label.set_text(text)
    label.set_use_markup(0)

#-------------------------------------------------------------------------
#
# create_id
#
#-------------------------------------------------------------------------
import random
import time
rand = random.Random(time.time())

def create_id():
    s = ""
    for val in [ int(time.time()*10000) & 0x7fffffff,
                 rand.randint(0,0x7fffffff),
                 rand.randint(0,0x7fffffff)]:
        while val != 0:
            rem = val % 36
            if rem <= 9:
                s += chr(48+rem)
            else:
                s += chr(rem+55)
            val = int(val/36)
    return s


def probably_alive(person,db):
    """Returns true if the person may be alive."""
    if person.death_handle:
        return False
    
    # Look for Cause Of Death, Burial or Cremation events.
    # These are fairly good indications that someone's not alive.
    for ev_handle in person.event_list:
        ev = db.get_event_from_handle(ev_handle)
        if ev.name in ["Cause Of Death", "Burial", "Cremation"]:
            return False

    if person.birth_handle:
        birth = db.get_event_from_handle(person.birth_handle)
        if birth.get_date_object().get_start_date() != Date.EMPTY:
            return not_too_old(birth.get_date_object())

    # Neither birth nor death events are available.  Try looking
    # for descendants that were born more than a lifespan ago.

    min_generation = 13
    max_generation = 60
    max_age_difference = 60

    def descendants_too_old (person, years):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                child = db.get_person_from_handle(child_handle)
                if child.birth_handle:
                    child_birth = db.get_event_from_handle(child.birth_handle)
                    dobj = child_birth.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        d = Date(dobj)
                        d.set_year(d.get_year() - years)
                        if not not_too_old (d):
                            return True

                if child.death_handle:
                    child_death = db.get_event_from_handle(child.death_handle)
                    dobj = child_death.get_date_object()
                    if dobj.get_start_date != Date.EMPTY:
                        if not not_too_old (dobj):
                            return True

                if descendants_too_old (child, years + min_generation):
                    return True

    if descendants_too_old (person, min_generation):
        return False

    return False
    
    # What about their parents?

    def parents_too_old (person, age_difference):
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = db.get_family_from_handle(family_handle)
            for parent_id in [family.get_father_handle(), family.get_mother_handle()]:
                if not parent_id:
                    continue

                parent = db.get_person_from_handle(parent_id)
                if parent.birth_handle:
                    parent_birth = db.get_event_from_handle(parent.birth_handle)
                    if parent_birth.get_date():
                        d = SingleDate (parent_birth.get_date_object().get_start_date())
                        d.set_year (d.get_year() + max_generation + age_difference)
                        if not not_too_old (d):
                            return True

                if parent.death_handle:
                    parent_death = db.get_event_from_handle(parent.death_handle)
                    if parent_death.get_date() != "":
                        d = SingleDate (parent_death.get_date_object().get_start_date())
                        d.set_year (d.get_year() + age_difference)
                        if not not_too_old (d):
                            return True

    if parents_too_old (person, 0):
        return False

    # As a last resort, trying seeing if their spouse's age gives
    # any clue.
    for family_handle in person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for spouse_id in [family.get_father_handle(), family.get_mother_handle()]:
            if not spouse_id or spouse_id == person.handle:
                continue
            spouse = db.get_person_from_handle(spouse_id)
            sp_birth_handle = spouse.get_birth_handle()
            sp_death_handle = spouse.get_death_handle()
            if sp_birth_handle:
                spouse_birth = db.get_event_from_handle(sp_birth_handle)
                if spouse_birth.get_date() != "":
                    d = SingleDate (spouse_birth.get_date_object().get_start_date())
                    d.set_year (d.get_year() + max_age_difference)
                    if not not_too_old (d):
                        return False

            if sp_death_handle:
                spouse_death = db.get_event_from_handle(sp_death_handle)
                if spouse_death.get_date() != "":
                    d = SingleDate (spouse_death.get_date_object().get_start_date())
                    d.set_year (d.get_year() - min_generation)
                    if not not_too_old (d):
                        return False

            if parents_too_old (spouse, max_age_difference):
                return False
    return True

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_NEW_NAME_PATTERN = '%sUntitled_%d.%s'

def get_new_filename(ext,folder='~/'):
    ix = 1
    while os.path.isfile(os.path.expanduser(_NEW_NAME_PATTERN % (folder,ix,ext) )):
        ix = ix + 1
    return os.path.expanduser(_NEW_NAME_PATTERN % (folder,ix,ext))
