#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
import os
import locale
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import gnome

try:
    from gnomevfs import get_mime_type, mime_get_description
except:
    from gnome.vfs import get_mime_type, mime_get_description
    
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import GrampsMime
import NameDisplay
import Date

#-------------------------------------------------------------------------
#
# modified flag
#
#-------------------------------------------------------------------------
_history_brokenFlag = 0

def history_broken():
    global _history_brokenFlag
    _history_brokenFlag = 1

data_recover_msg = _('The data can only be recovered by Undo operation '
            'or by quitting with abandoning changes.')

#-------------------------------------------------------------------------
#
# force_unicode
#
#-------------------------------------------------------------------------

def force_unicode(n):
    if type(n) != unicode:
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

def family_name(family,db):
    """Builds a name for the family from the parents names"""
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = NameDisplay.displayer.display(father)
        mname = NameDisplay.displayer.display(mother)
        name = _("%(father)s and %(mother)s") % {
                    "father" : fname,
                    "mother" : mname}
    elif father:
        name = NameDisplay.displayer.display(father)
    elif mother:
        name = NameDisplay.displayer.display(mother)
    else:
        name = _("unknown")
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
    
    args = prog.split()
    args.append(photo.get_path())
    
    if os.fork() == 0:
        os.execvp(args[0],args)

_icon_theme = gtk.icon_theme_get_default()

def find_mime_type_pixbuf(mime_type):
    try:
        icontmp = mime_type.replace('/','-')
        newicon = "gnome-mime-%s" % icontmp
        try:
            return _icon_theme.load_icon(newicon,48,0)
        except:
            icontmp = mime_type.split('/')[0]
            try:
                newicon = "gnome-mime-%s" % icontmp
                return _icon_theme.load_icon(newicon,48,0)
            except:
                return gtk.gdk.pixbuf_new_from_file(const.icon)
    except:
        return gtk.gdk.pixbuf_new_from_file(const.icon)
    
def get_mime_description(mime_type):
    try:
        value = mime_get_description(mime_type)
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
            column.set_clickable(True)
            column.set_visible(False)
        cnum = cnum + 1
        tree.append_column(column)

#-------------------------------------------------------------------------
#
#  Iterate over ancestors.
#
#-------------------------------------------------------------------------
def for_each_ancestor(db, start, func, data):
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
        p_handle = todo.pop()
        p = db.get_person_from_handle(p_handle)
        # Don't process the same handle twice.  This can happen
        # if there is a cycle in the database, or if the
        # initial list contains X and some of X's ancestors.
        if doneIds.has_key(p_handle):
            continue
        doneIds[p_handle] = 1
        if func(data,p_handle):
            return 1
        for fam_handle, mrel, frel in p.get_parent_family_handle_list():
            fam = db.get_family_from_handle(fam_handle)
            if fam:
                f_handle = fam.get_father_handle()
                m_handle = fam.get_mother_handle()
                if f_handle: todo.append(f_handle)
                if m_handle: todo.append(m_handle)
    return 0

def title(n):
    return '<span weight="bold" size="larger">%s</span>' % n

def set_title_label(xmlobj,t):
    title_label = xmlobj.get_widget('title')
    title_label.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title_label.set_use_markup(True)

def set_titles(window,title,t,msg=None):
    title.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title.set_use_markup(True)
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
#  Change label appearance
#
#-------------------------------------------------------------------------
def bold_label(label,widget=None):
    text = unicode(label.get_text())
    text = text.replace('<i>','')
    text = text.replace('</i>','')
    label.set_text("<b>%s</b>" % text )
    label.set_use_markup(True)
    if widget:
        widget.window.set_cursor(None)

def unbold_label(label,widget=None):
    text = unicode(label.get_text())
    text = text.replace('<b>','')
    text = text.replace('</b>','')
    text = text.replace('<i>','')
    text = text.replace('</i>','')
    label.set_text(text)
    label.set_use_markup(False)
    if widget:
        widget.window.set_cursor(None)

def temp_label(label,widget=None):
    text = unicode(label.get_text())
    text = text.replace('<b>','')
    text = text.replace('</b>','')
    label.set_text("<i>%s</i>" % text )
    label.set_use_markup(True)
    if widget:
        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

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


def probably_alive(person,db,current_year=None):
    """Returns true if the person may be alive.

    This works by a process of emlimination. If we can't find a good
    reason to believe that someone is dead then we assume they must
    be alive.

    """

    death_year = None
    # If the recorded death year is before current year then
    # things are simple.
    if person.death_handle:
        if not current_year:
            # no current year and we have a death event -> person died
            return False
        death = db.get_event_from_handle(person.death_handle)
        if death.get_date_object().get_start_date() != Date.EMPTY:
            death_year = death.get_date_object().get_year()
            if death_year < current_year:
                return False
    
    # Look for Cause Of Death, Burial or Cremation events.
    # These are fairly good indications that someone's not alive.
    for ev_handle in person.event_list:
        ev = db.get_event_from_handle(ev_handle)
        if ev and ev.name in ["Cause Of Death", "Burial", "Cremation"]:
            if not current_year:
                # no current year and we have an event related to death
                return False
            if not death_year:
                death_year = ev.get_date_object().get_year()
            if ev.get_date_object().get_start_date() != Date.EMPTY:
                if ev.get_date_object().get_year() < current_year:
                    return False

    if not current_year:
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]

    birth_year = None
    # If they were born within 100 years before current year then
    # assume they are alive (we already know they are not dead).
    if person.birth_handle:
        birth = db.get_event_from_handle(person.birth_handle)
        if birth.get_date_object().get_start_date() != Date.EMPTY:
            if not birth_year:
                birth_year = birth.get_date_object().get_year()
            if birth.get_date_object().get_year() > current_year:
                # person is not yet born
                return False
            r = not_too_old(birth.get_date_object(),current_year)
            if r:
                #print person.get_primary_name().get_name(), " is alive because they were born late enough."
                return True
    
    
    if not birth_year and death_year:
        if death_year > current_year + 110:
            # person died more tha 110 after current year
            return False
            

    # Neither birth nor death events are available.  Try looking
    # for descendants that were born more than a lifespan ago.

    min_generation = 13
    max_generation = 60
    max_age_difference = 60

    def descendants_too_old (person, years):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            family_list = family.get_child_handle_list()
            
            for child_handle in family.get_child_handle_list():
                child = db.get_person_from_handle(child_handle)
                if child.birth_handle:
                    child_birth = db.get_event_from_handle(child.birth_handle)
                    dobj = child_birth.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        d = Date.Date(dobj)
                        val = d.get_start_date()
                        val = d.get_year() - years
                        d.set_year(val)
                        if not not_too_old (d,current_year):
                            return True

                if child.death_handle:
                    child_death = db.get_event_from_handle(child.death_handle)
                    dobj = child_death.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        if not not_too_old (dobj,current_year):
                            return True

                if descendants_too_old (child, years + min_generation):
                    return True
                
        return False

    # If there are descendants that are too old for the person to have
    # been alive in the current year then they must be dead.
    if descendants_too_old (person, min_generation):
        #print person.get_primary_name().get_name(), " is dead because descendants are too old."
        return False


    average_generation_gap = 20

    def ancestors_too_old (person, year):
        family_handle = person.get_main_parents_family_handle()
        
        if family_handle:                
            family = db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                father = db.get_person_from_handle(father_handle)
                if father.birth_handle:
                    father_birth = db.get_event_from_handle(father.birth_handle)
                    dobj = father_birth.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        if not not_too_old (dobj,year - average_generation_gap):
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap
                            return True
                        #else:
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is NOT too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap


                if father.death_handle:
                    father_death = db.get_event_from_handle(father.death_handle)
                    dobj = father_death.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        if dobj.get_year() < year - average_generation_gap:
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is too old by death."
                            return True

                if ancestors_too_old (father, year - average_generation_gap):
                    return True

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = db.get_person_from_handle(mother_handle)
                if mother.birth_handle:
                    mother_birth = db.get_event_from_handle(mother.birth_handle)
                    dobj = mother_birth.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        if not not_too_old (dobj,year - average_generation_gap):
                            #print mother.get_primary_name().get_name(), " mother of ", person.get_primary_name().get_name(), " is too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap
                            return True
                        #else:
                            #print mother.get_primary_name().get_name(), " mother of ", person.get_primary_name().get_name(), " is NOT too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap


                if mother.death_handle:
                    mother_death = db.get_event_from_handle(mother.death_handle)
                    dobj = mother_death.get_date_object()
                    if dobj.get_start_date() != Date.EMPTY:
                        if dobj.get_year() < year - average_generation_gap:
                            #print mother.get_primary_name().get_name(), " mother of ", person.get_primary_name().get_name(), " is too old by death."
                            return True

                if ancestors_too_old (mother, year - average_generation_gap):
                    return True

        return False


    # If there are ancestors that would be too old in the current year
    # then assume our person must be dead too.
    if ancestors_too_old (person, current_year):
        #print person.get_primary_name().get_name(), " is dead because ancestors are too old."
        return False

    # If we can't find any reason to believe that they are dead we
    # must assume they are alive.
    #print person.get_primary_name().get_name(), " is probably alive."
    return True

def not_too_old(date,current_year=None):
    if not current_year:
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]
    year = date.get_year()
    if year > current_year:
        return False
    return not( year != 0 and current_year - year > 110)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_source_referents(source_handle,db):
    """
    Find objects that refer the source.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.
    """

    # Persons
    person_list = [ handle \
            for handle in db.get_person_handles(sort_handles=False) \
            if db.get_person_from_handle(handle).has_source_reference(source_handle)
    ]

    # Families
    family_list = [ handle for handle in db.get_family_handles() \
            if db.get_family_from_handle(handle).has_source_reference(source_handle)
    ]

    # Events
    event_list = [ handle for handle in db.get_event_handles() \
            if db.get_event_from_handle(handle).has_source_reference(source_handle)
    ]

    # Places
    place_list = [ handle for handle in db.get_place_handles() \
            if db.get_place_from_handle(handle).has_source_reference(source_handle)
    ]

    # Sources
    source_list = [ handle for handle in db.get_source_handles() \
            if db.get_source_from_handle(handle).has_source_reference(source_handle)
    ]

    # Media Objects
    media_list = [ handle for handle in db.get_media_object_handles() \
            if db.get_object_from_handle(handle).has_source_reference(source_handle)
    ]

    return (person_list,family_list,event_list,
                place_list,source_list,media_list)

def get_media_referents(media_handle,db):
    """
    Find objects that refer the media object.

    This function finds all primary objects that refer
    to a given media handle in a given database.
    """

    # Persons
    person_list = [ handle \
            for handle in db.get_person_handles(sort_handles=False) \
            if media_handle in \
                    [photo.get_reference_handle() for photo \
                    in db.get_person_from_handle(handle).get_media_list()]
    ]

    # Families
    family_list = [ handle for handle in db.get_family_handles() \
            if media_handle in \
                    [photo.get_reference_handle() for photo \
                    in db.get_family_from_handle(handle).get_media_list()]
    ]

    # Events
    event_list = [ handle for handle in db.get_event_handles() \
            if media_handle in \
                    [photo.get_reference_handle() for photo \
                    in db.get_event_from_handle(handle).get_media_list()]
    ]

    # Places
    place_list = [ handle for handle in db.get_place_handles() \
            if media_handle in \
                    [photo.get_reference_handle() for photo \
                    in db.get_place_from_handle(handle).get_media_list()]
    ]

    # Sources
    source_list = [ handle for handle in db.get_source_handles() \
            if media_handle in \
                    [photo.get_reference_handle() for photo \
                    in db.get_source_from_handle(handle).get_media_list()]
    ]

    return (person_list,family_list,event_list,place_list,source_list)

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

def get_type_converter(val):
    """
    Returns function that converts strings into the type of val.
    """
    val_type = type(val)
    if val_type in (str,unicode):
        return unicode
    elif val_type == int:
        return int
    elif val_type == float:
        return float
    elif val_type in (list,tuple):
        return list

def type_name(val):
    """
    Returns the name the type of val.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    val_type = type(val)
    if val_type == int:
        return 'int'
    elif val_type == float:
        return 'float'
    elif val_type in (str,unicode):
        return 'unicode'
    return 'unicode'

def get_type_converter_by_name(val_str):
    """
    Returns function that converts strings into the type given by val_str.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    if val_str == 'int':
        return int
    elif val_str == 'float':
        return float
    elif val_str in ('str','unicode'):
        return unicode
    return unicode

def strip_context(msgid,sep='|'):
    """
    Strip the context used for resolving translation ambiguities.
    
    The translation of msgid is returned unless the translation is
    not available and the msgid contains the separator. In that case,
    the returned value is the portion of msgid following the last
    separator. Default separator is '|'.

    @param msgid: The string to translated.
    @type msgid: unicode
    @param sep: The separator marking the context.
    @type sep: unicode
    @return: Translation or the original with context stripped.
    @rtype: unicode

    """
    msgval = _(msgid)
    sep_idx = msgid.rfind(sep)
    if msgval == msgid and sep_idx != -1:
        msgval = msgid[sep_idx+1:]
    return msgval
