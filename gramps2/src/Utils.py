#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import sys
import locale
import random
import time

from gettext import gettext as _

try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Mime
import NameDisplay
import RelLib
import Errors
from QuestionDialog import WarningDialog

#-------------------------------------------------------------------------
#
# Integer to String  mappings for constants
#
#-------------------------------------------------------------------------
gender = {
    RelLib.Person.MALE    : _("male"),
    RelLib.Person.FEMALE  : _("female"),
    RelLib.Person.UNKNOWN : _("unknown"),
    }
def format_gender( type):
    return gender.get(type[0],_("Invalid"))

confidence = {
    RelLib.SourceRef.CONF_VERY_HIGH : _("Very High"),
    RelLib.SourceRef.CONF_HIGH      : _("High"),
    RelLib.SourceRef.CONF_NORMAL    : _("Normal"),
    RelLib.SourceRef.CONF_LOW       : _("Low"),
    RelLib.SourceRef.CONF_VERY_LOW  : _("Very Low"),
   }
def format_confidence( type):
    return confidence.get(type[0],_("Invalid id %d ('%s')")%type)

family_rel_descriptions = {
    RelLib.FamilyRelType.MARRIED     : _("A legal or common-law relationship "
                                         "between a husband and wife"),
    RelLib.FamilyRelType.UNMARRIED   : _("No legal or common-law relationship "
                                         "between man and woman"),
    RelLib.FamilyRelType.CIVIL_UNION : _("An established relationship between "
                                         "members of the same sex"),
    RelLib.FamilyRelType.UNKNOWN     : _("Unknown relationship between a man "
                                         "and woman"),
    RelLib.FamilyRelType.CUSTOM      : _("An unspecified relationship "
                                         "a man and woman"),
    }


#-------------------------------------------------------------------------
#
# Integer to GEDCOM tag mappings for constants
#
#-------------------------------------------------------------------------
familyConstantEvents = {
    RelLib.EventType.ANNULMENT  : "ANUL",
    RelLib.EventType.DIV_FILING : "DIVF",
    RelLib.EventType.DIVORCE    : "DIV",
    RelLib.EventType.ENGAGEMENT : "ENGA",
    RelLib.EventType.MARR_BANNS : "MARB",
    RelLib.EventType.MARR_CONTR : "MARC",
    RelLib.EventType.MARR_LIC   : "MARL",
    RelLib.EventType.MARR_SETTL : "MARS",
    RelLib.EventType.MARRIAGE   : "MARR"
    }

personalConstantEvents = {
    RelLib.EventType.ADOPT            : "ADOP",
    RelLib.EventType.ADULT_CHRISTEN   : "CHRA",
    RelLib.EventType.BIRTH            : "BIRT",
    RelLib.EventType.DEATH            : "DEAT",
    RelLib.EventType.BAPTISM          : "BAPM",
    RelLib.EventType.BAR_MITZVAH      : "BARM",
    RelLib.EventType.BAS_MITZVAH      : "BASM",
    RelLib.EventType.BLESS            : "BLES",
    RelLib.EventType.BURIAL           : "BURI",
    RelLib.EventType.CAUSE_DEATH      : "CAUS",
    RelLib.EventType.ORDINATION       : "ORDI",
    RelLib.EventType.CENSUS           : "CENS",
    RelLib.EventType.CHRISTEN         : "CHR" ,
    RelLib.EventType.CONFIRMATION     : "CONF",
    RelLib.EventType.CREMATION        : "CREM",
    RelLib.EventType.DEGREE           : "_DEG", 
    RelLib.EventType.DIV_FILING       : "DIVF",
    RelLib.EventType.EDUCATION        : "EDUC",
    RelLib.EventType.ELECTED          : "",
    RelLib.EventType.EMIGRATION       : "EMIG",
    RelLib.EventType.FIRST_COMMUN     : "FCOM",
    RelLib.EventType.GRADUATION       : "GRAD",
    RelLib.EventType.MED_INFO         : "_MDCL", 
    RelLib.EventType.MILITARY_SERV    : "_MILT", 
    RelLib.EventType.NATURALIZATION   : "NATU",
    RelLib.EventType.NOB_TITLE        : "TITL",
    RelLib.EventType.NUM_MARRIAGES    : "NMR",
    RelLib.EventType.IMMIGRATION      : "IMMI",
    RelLib.EventType.OCCUPATION       : "OCCU",
    RelLib.EventType.PROBATE          : "PROB",
    RelLib.EventType.PROPERTY         : "PROP",
    RelLib.EventType.RELIGION         : "RELI",
    RelLib.EventType.RESIDENCE        : "RESI", 
    RelLib.EventType.RETIREMENT       : "RETI",
    RelLib.EventType.WILL             : "WILL",
    }

familyConstantAttributes = {
    RelLib.AttributeType.NUM_CHILD   : "NCHI",
    }

personalConstantAttributes = {
    RelLib.AttributeType.CASTE       : "CAST",
    RelLib.AttributeType.DESCRIPTION : "DSCR",
    RelLib.AttributeType.ID          : "IDNO",
    RelLib.AttributeType.NATIONAL    : "NATI",
    RelLib.AttributeType.NUM_CHILD   : "NCHI",
    RelLib.AttributeType.SSN         : "SSN",
    }

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

def fix_encoding(value):
    if type(value) != unicode:
        try:
            return unicode(value)
        except:
            codeset = locale.getpreferredencoding()
            if codeset == 'UTF-8':
                codeset = 'latin1'
            return unicode(value,codeset)
    else:
        return value

def xml_lang():
    (loc,enc) = locale.getlocale()
    if loc == None:
        return ""
    else:
        return loc.replace('_','-')

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

def family_name(family,db,noname=_("unknown")):
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
        name = noname
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
        data = Mime.get_application(mime_type)
        prog = data[0]
    except:
        return
    launch(prog,photo.get_path())

def find_file( filename):
    # try the filename we got
    try:
        fname = filename
        if os.path.isfile( filename):
            return( filename)
    except:
        pass
    
    # Build list of elternate encodings
    encodings = [sys.getfilesystemencoding(), locale.getpreferredencoding(), 'UTF-8', 'ISO-8859-1']
    encodings = list(set(encodings))
    for enc in encodings:
        try:
            fname = filename.encode(enc)
            if os.path.isfile( fname):
                return fname
        except:
            pass

    # not found
    return ''

def find_folder( filename):
    # try the filename we got
    try:
        fname = filename
        if os.path.isdir( filename):
            return( filename)
    except:
        pass
    
    # Build list of elternate encodings
    try:
        encodings = [sys.getfilesystemencoding(), locale.getpreferredencoding(),
                     'UTF-8', 'ISO-8859-1']
    except:
        encodings = [sys.getfilesystemencoding(), 'UTF-8', 'ISO-8859-1']
    encodings = list(set(encodings))
    for enc in encodings:
        try:
            fname = filename.encode(enc)
            if os.path.isdir( fname):
                return fname
        except:
            pass

    # not found
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
        for fam_handle in p.get_parent_family_handle_list():
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

from ManagedWindow import set_titles as _set_titles
from warnings import warn
def set_titles(window,title,t,msg=None):
    warn('The Utils.set_titles is deprecated. Use ManagedWindow methods')

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
    """Performs ('%.3f' % val) formatting with the resulting string always 
    using dot ('.') as a decimal point.
    
    Useful for writing float values into XML when under non-English locale.
    """

    decimal_point = locale.localeconv()['decimal_point']
    return_val = "%.3f" % val
    return return_val.replace(decimal_point,'.')

def search_for(name):
    name = name.split()[0]
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
    if label.__class__ == gtk.Label:
        text = unicode(label.get_text())
        text = text.replace('<i>','')
        text = text.replace('</i>','')
        label.set_text("<b>%s</b>" % text )
        label.set_use_markup(True)
    else:
        clist = label.get_children()
        text = unicode(clist[1].get_text())
        text = text.replace('<i>','')
        text = text.replace('</i>','')
        clist[0].show()
        clist[1].set_text("<b>%s</b>" % text )
        clist[1].set_use_markup(True)
    if widget:
        widget.window.set_cursor(None)
        
def unbold_label(label,widget=None):
    if label.__class__ == gtk.Label:
        text = unicode(label.get_text())
        text = text.replace('<b>','')
        text = text.replace('</b>','')
        text = text.replace('<i>','')
        text = text.replace('</i>','')
        label.set_text(text)
        label.set_use_markup(False)
    else:
        clist = label.get_children()
        text = unicode(clist[1].get_text())
        text = text.replace('<b>','')
        text = text.replace('</b>','')
        text = text.replace('<i>','')
        text = text.replace('</i>','')
        clist[0].hide()
        clist[1].set_text(text)
        clist[1].set_use_markup(False)
    if widget:
        widget.window.set_cursor(None)

def temp_label(label,widget=None):
    if label.__class__ == gtk.Label:
        text = unicode(label.get_text())
        text = text.replace('<b>','')
        text = text.replace('</b>','')
        label.set_text("<i>%s</i>" % text )
        label.set_use_markup(True)
    else:
        clist = label.get_children()
        text = unicode(clist[1].get_text())
        text = text.replace('<b>','')
        text = text.replace('</b>','')
        clist[0].hide()
        clist[1].set_text("<i>%s</i>" % text )
        clist[1].set_use_markup(True)
    if widget:
        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

#-------------------------------------------------------------------------
#
# create_id
#
#-------------------------------------------------------------------------
rand = random.Random(time.time())

def create_id():
    return "%08x%08x" % ( int(time.time()*10000),
                          rand.randint(0,sys.maxint))

def probably_alive(person,db,current_year=None,limit=0):
    """Returns true if the person may be alive.

    This works by a process of emlimination. If we can't find a good
    reason to believe that someone is dead then we assume they must
    be alive.

    """

    if not current_year:
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]

    death_year = None
    # If the recorded death year is before current year then
    # things are simple.
    if person.death_ref:
        death = db.get_event_from_handle(person.death_ref.ref)
        if death.get_date_object().get_start_date() != RelLib.Date.EMPTY:
            death_year = death.get_date_object().get_year()
            if death_year + limit < current_year:
                return False

    # Look for Cause Of Death, Burial or Cremation events.
    # These are fairly good indications that someone's not alive.
    for ev_ref in person.event_ref_list:
        ev = db.get_event_from_handle(ev_ref.ref)
        if ev and int(ev.get_type()) in [RelLib.EventType.CAUSE_DEATH,
                                         RelLib.EventType.BURIAL,
                                         RelLib.EventType.CREMATION]:
            if not death_year:
                death_year = ev.get_date_object().get_year()
            if ev.get_date_object().get_start_date() != RelLib.Date.EMPTY:
                if ev.get_date_object().get_year() + limit < current_year:
                    return False
        # For any other event of this person, check whether it happened
        # too long ago. If so then the person is likely dead now.
        elif ev and too_old(ev.get_date_object(),current_year):
            return False

    birth_year = None
    # If they were born within 100 years before current year then
    # assume they are alive (we already know they are not dead).
    if person.birth_ref:
        birth = db.get_event_from_handle(person.birth_ref.ref)
        if birth.get_date_object().get_start_date() != RelLib.Date.EMPTY:
            if not birth_year:
                birth_year = birth.get_date_object().get_year()
            # Check whether the birth event is too old because the
            # code above did not look at birth, only at other events
            if too_old(birth.get_date_object(),current_year):
                return False
            if not_too_old(birth.get_date_object(),current_year):
                return True
    
    if not birth_year and death_year:
        if death_year > current_year + 110:
            # person died more tha 110 after current year
            return False
            
    # Neither birth nor death events are available.  Try looking
    # for descendants that were born more than a lifespan ago.

    min_generation = 13

    def descendants_too_old (person, years):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = db.get_person_from_handle(child_handle)
                if child.birth_ref:
                    child_birth = db.get_event_from_handle(child.birth_ref.ref)
                    dobj = child_birth.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
                        d = RelLib.Date(dobj)
                        val = d.get_start_date()
                        val = d.get_year() - years
                        d.set_year(val)
                        if not not_too_old (d,current_year):
                            return True

                if child.death_ref:
                    child_death = db.get_event_from_handle(child.death_ref.ref)
                    dobj = child_death.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
                        if not not_too_old (dobj,current_year):
                            return True

                if descendants_too_old (child, years + min_generation):
                    return True
                
        return False

    # If there are descendants that are too old for the person to have
    # been alive in the current year then they must be dead.

    try:
        if descendants_too_old (person, min_generation):
            return False
    except RuntimeError:
        raise Errors.DatabaseError(
            _("Database error: %s is defined as his or her own ancestor") %
            NameDisplay.displayer.display(person))

    average_generation_gap = 20

    def ancestors_too_old (person, year):
        family_handle = person.get_main_parents_family_handle()
        
        if family_handle:                
            family = db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                father = db.get_person_from_handle(father_handle)
                if father.birth_ref:
                    father_birth = db.get_event_from_handle(father.birth_ref.ref)
                    dobj = father_birth.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
                        if not not_too_old (dobj,year - average_generation_gap):
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap
                            return True
                        #else:
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is NOT too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap


                if father.death_ref:
                    father_death = db.get_event_from_handle(father.death_ref.ref)
                    dobj = father_death.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
                        if dobj.get_year() < year - average_generation_gap:
                            #print father.get_primary_name().get_name(), " father of ", person.get_primary_name().get_name(), " is too old by death."
                            return True

                if ancestors_too_old (father, year - average_generation_gap):
                    return True

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = db.get_person_from_handle(mother_handle)
                if mother.birth_ref:
                    mother_birth = db.get_event_from_handle(mother.birth_ref.ref)
                    dobj = mother_birth.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
                        if not not_too_old (dobj,year - average_generation_gap):
                            #print mother.get_primary_name().get_name(), " mother of ", person.get_primary_name().get_name(), " is too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap
                            return True
                        #else:
                            #print mother.get_primary_name().get_name(), " mother of ", person.get_primary_name().get_name(), " is NOT too old by birth. birth year ", dobj.get_year(), " test year ", year - average_generation_gap


                if mother.death_ref:
                    mother_death = db.get_event_from_handle(mother.death_ref.ref)
                    dobj = mother_death.get_date_object()
                    if dobj.get_start_date() != RelLib.Date.EMPTY:
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
    return (year != 0 and current_year - year < 110)

def too_old(date,current_year=None):
    if current_year:
        the_current_year = current_year
    else:
        time_struct = time.localtime(time.time())
        the_current_year = time_struct[0]
    year = date.get_year()
    if year > the_current_year:
        return True
    return (year != 0 and the_current_year - year > 150)

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
_NEW_NAME_PATTERN = '%s%sUntitled_%d.%s'

def get_new_filename(ext,folder='~/'):
    ix = 1
    while os.path.isfile(os.path.expanduser(_NEW_NAME_PATTERN %
                                            (folder,os.path.sep,ix,ext))):
        ix = ix + 1
    return os.path.expanduser(_NEW_NAME_PATTERN % (folder,os.path.sep,ix,ext))

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

def relative_path(original, base):
    if not os.path.exists(original) or  not os.path.isdir(base):
        return original

    base_list = (os.path.abspath(base)).split(os.sep)
    target_list = (os.path.abspath(original)).split(os.sep)

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.

    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] <> target_list[i]: break
    else:
        i+=1
    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)

class ProgressMeter:
    """
    Progress meter class for GRAMPS.
    """
    def __init__(self,title,header=''):
        """
        Specify the title and the current pass header.
        """
        self.old_val = -1
        self.ptop = gtk.Dialog()
        self.ptop.connect('delete_event',self.warn)
        self.ptop.set_has_separator(False)
        self.ptop.set_title(title)
        self.ptop.set_border_width(12)
        self.ptop.vbox.set_spacing(10)
        lbl = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        lbl.set_use_markup(True)
        self.lbl = gtk.Label(header)
        self.lbl.set_use_markup(True)
        self.ptop.vbox.add(lbl)
        self.ptop.vbox.add(self.lbl)
        self.ptop.vbox.set_border_width(24)
        self.pbar = gtk.ProgressBar()

        self.ptop.set_size_request(350,125)
        self.ptop.vbox.add(self.pbar)
        self.ptop.show_all()
        if header == '':
            self.lbl.hide()

    def set_pass(self,header,total):
        """
        Reset for another pass. Provide a new header and define number
        of steps to be used.
        """
        if header == '':
            self.lbl.hide()
        else:
            self.lbl.show()
        self.pbar_max = total
        self.pbar_index = 0.0
        self.lbl.set_text(header)
        self.pbar.set_fraction(0.0)
        while gtk.events_pending():
            gtk.main_iteration()

    def step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        self.pbar_index = self.pbar_index + 1.0
        if (self.pbar_index > self.pbar_max):
            self.pbar_index = self.pbar_max

        val = int(100*self.pbar_index/self.pbar_max)

        if val != self.old_val:
            self.pbar.set_text("%d%%" % val)
            self.pbar.set_fraction(val/100.0)
            self.old_val = val
        while gtk.events_pending():
            gtk.main_iteration()

    def warn(self,*obj):
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog."),
            self.ptop)
        return True

    def close(self):
        """
        Close the progress meter
        """
        self.ptop.destroy()

def launch(prog_str,path):

    subval = {
        '%F'   : path,
        '%f'   : path,
        '%u'   : path,
        '%U'   : path,
        '%n'   : path,
        '%N'   : path,
        }
    
    prog_data = prog_str.split()
    prog = prog_data[0]
    prog_list = []
    need_path = True

    if len(prog_data) > 1:
        for item in prog_data:
            if subval.has_key(item):
                need_path = False
                value = subval[item]
            else:
                value = item
            prog_list.append(value)
    else:
        prog_list = [prog_data[0]]

    if need_path:
        prog_list.append(path)
    os.spawnvpe(os.P_NOWAIT, prog, prog_list, os.environ)
