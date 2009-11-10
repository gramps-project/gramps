#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

"""
Non GUI/GTK related utility functions
"""

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
import shutil
import platform
import uuid

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from BasicUtils import name_displayer
import gen.lib
import Errors
from GrampsLocale import codeset

from const import TEMP_DIR, USER_HOME, WINDOWS, MACOS, LINUX, GRAMPS_UUID
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# Constants from config .ini keys
#
#-------------------------------------------------------------------------
# cache values; use refresh_constants() if they change
try:
    import config
    _MAX_AGE_PROB_ALIVE   = config.get('behavior.max-age-prob-alive')
    _MAX_SIB_AGE_DIFF     = config.get('behavior.max-sib-age-diff')
    _MIN_GENERATION_YEARS = config.get('behavior.min-generation-years')
    _AVG_GENERATION_GAP   = config.get('behavior.avg-generation-gap')
except ImportError:
    # Utils used as module not part of GRAMPS
    _MAX_AGE_PROB_ALIVE   = 110
    _MAX_SIB_AGE_DIFF     = 20
    _MIN_GENERATION_YEARS = 13
    _AVG_GENERATION_GAP   = 20

#-------------------------------------------------------------------------
#
# Integer to String  mappings for constants
#
#-------------------------------------------------------------------------
gender = {
    gen.lib.Person.MALE    : _("male"), 
    gen.lib.Person.FEMALE  : _("female"), 
    gen.lib.Person.UNKNOWN : _("unknown"), 
    }

def format_gender( type):
    return gender.get(type[0], _("Invalid"))

confidence = {
    gen.lib.SourceRef.CONF_VERY_HIGH : _("Very High"), 
    gen.lib.SourceRef.CONF_HIGH      : _("High"), 
    gen.lib.SourceRef.CONF_NORMAL    : _("Normal"), 
    gen.lib.SourceRef.CONF_LOW       : _("Low"), 
    gen.lib.SourceRef.CONF_VERY_LOW  : _("Very Low"), 
   }

family_rel_descriptions = {
    gen.lib.FamilyRelType.MARRIED     : _("A legal or common-law relationship "
                                         "between a husband and wife"), 
    gen.lib.FamilyRelType.UNMARRIED   : _("No legal or common-law relationship "
                                         "between man and woman"), 
    gen.lib.FamilyRelType.CIVIL_UNION : _("An established relationship between "
                                         "members of the same sex"), 
    gen.lib.FamilyRelType.UNKNOWN     : _("Unknown relationship between a man "
                                         "and woman"), 
    gen.lib.FamilyRelType.CUSTOM      : _("An unspecified relationship between "
                                         "a man and woman"), 
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
    if not isinstance(value, unicode):
        try:
            return unicode(value)
        except:
            try:
                codeset = locale.getpreferredencoding()
            except:
                codeset = "UTF-8"
            return unicode(value, codeset)
    else:
        return value

def xml_lang():
    loc = locale.getlocale()
    if loc[0] is None:
        return ""
    else:
        return loc[0].replace('_', '-')

#-------------------------------------------------------------------------
#
# force_unicode
#
#-------------------------------------------------------------------------

def force_unicode(n):
    if not isinstance(n, unicode):
        return (unicode(n).lower(), unicode(n))
    else:
        return (n.lower(), n)

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

def family_name(family, db, noname=_("unknown")):
    """Builds a name for the family from the parents names"""

    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = name_displayer.display(father)
        mname = name_displayer.display(mother)
        name = _("%(father)s and %(mother)s") % {
                    "father" : fname, 
                    "mother" : mname}
    elif father:
        name = name_displayer.display(father)
    elif mother:
        name = name_displayer.display(mother)
    else:
        name = noname
    return name

def family_upper_name(family, db):
    """Builds a name for the family from the parents names"""
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = father.get_primary_name().get_upper_name()
        mname = mother.get_primary_name().get_upper_name()
        name = _("%(father)s and %(mother)s") % {
            'father' : fname, 
            'mother' : mname 
            }
    elif father:
        name = father.get_primary_name().get_upper_name()
    else:
        name = mother.get_primary_name().get_upper_name()
    return name

#-------------------------------------------------------------------------
#
# Platform determination functions
#
#-------------------------------------------------------------------------

def lin():
    """
    Return True if a linux system
    Note: Normally do as linux in else statement of a check !
    """
    if platform.system() in LINUX:
        return True
    return False
    
def mac():
    """
    Return True if a Macintosh system
    """
    if platform.system() in MACOS:
        return True
    return False

def win():
    """
    Return True if a windows system
    """
    if platform.system() in WINDOWS:
        return True
    return False

#-------------------------------------------------------------------------
#
# String Encoding functions
#
#-------------------------------------------------------------------------

def encodingdefs():
    """
    4 functions are defined to obtain a byte string that can be used as 
    sort key and is locale aware. Do not print the sortkey, it is a sortable
    string, but is not a human readable correct string!
    When gtk is defined, one can avoid some function calls as then the default
    python encoding is not ascii but utf-8, so use the gtk functions in those
    cases.
    
    conv_utf8_tosrtkey: convert a utf8 encoded string to sortkey usable string
    
    conv_unicode_tosrtkey:  convert a unicode object to sortkey usable string
    
    conv_utf8_tosrtkey_ongtk: convert a utf8 encoded string to sortkey usable 
    string when gtk is loaded or utf-8 is default python encoding
    
    conv_unicode_tosrtkey_ongtk:  convert a unicode object to sortkey usable 
    string when gtk is loaded or utf-8 is default python encoding
    """
    pass

if platform.system() in WINDOWS:
    # python encoding is ascii, but C functions need to recieve the 
    # windows codeset, so convert over to it
    conv_utf8_tosrtkey = lambda x: locale.strxfrm(x.decode("utf-8").encode(
                                                        codeset))
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode(codeset))
    #when gtk is imported the python defaultencoding is utf-8, 
    #so no need to specify it
    conv_utf8_tosrtkey_ongtk = lambda x: locale.strxfrm(unicode(x).encode(
                                                                    codeset))
    conv_unicode_tosrtkey_ongtk = lambda x: locale.strxfrm(x.encode(codeset))
else:
    # on unix C functions need to recieve utf-8. Default conversion would
    # use ascii, so it is needed to be explicit about the resulting encoding 
    conv_utf8_tosrtkey = lambda x: locale.strxfrm(x)
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode("utf-8"))
    # when gtk loaded, default encoding (sys.getdefaultencoding ) is utf-8,
    # so default conversion happens with utf-8 
    conv_utf8_tosrtkey_ongtk = lambda x:  locale.strxfrm(x)
    conv_unicode_tosrtkey_ongtk = lambda x:  locale.strxfrm(x)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def find_file( filename):
    # try the filename we got
    try:
        fname = filename
        if os.path.isfile( filename):
            return( filename)
    except:
        pass
    
    # Build list of alternate encodings
    encodings = set()

    for enc in [sys.getfilesystemencoding, locale.getpreferredencoding]:
        try:
            encodings.add(enc)
        except:
            pass
    encodings.add('UTF-8')
    encodings.add('ISO-8859-1')

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
        encodings = [sys.getfilesystemencoding(), 
                     locale.getpreferredencoding(), 
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

def get_unicode_path(path):
    """
    Return the Unicode version of a path string.

    :type  path: str
    :param path: The path to be converted to Unicode
    :rtype:      unicode
    :returns:     The Unicode version of path.
    """
    if os.sys.platform == "win32":
        return unicode(path)
    else:
        return unicode(path,sys.getfilesystemencoding())


#-------------------------------------------------------------------------
#
#  Iterate over ancestors.
#
#-------------------------------------------------------------------------
def for_each_ancestor(db, start, func, data):
    """
    Recursively iterate (breadth-first) over ancestors of
    people listed in start.
    Call func(data, pid) for the Id of each person encountered.
    Exit and return 1, as soon as func returns true.
    Return 0 otherwise.
    """
    todo = start
    done_ids = set()
    while len(todo):
        p_handle = todo.pop()
        p = db.get_person_from_handle(p_handle)
        # Don't process the same handle twice.  This can happen
        # if there is a cycle in the database, or if the
        # initial list contains X and some of X's ancestors.
        if p_handle in done_ids:
            continue
        done_ids.add(p_handle)
        if func(data, p_handle):
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

def set_title_label(xmlobj, t):
    title_label = xmlobj.get_widget('title')
    title_label.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title_label.set_use_markup(True)

from warnings import warn
def set_titles(window, title, t, msg=None):
    warn('The Utils.set_titles is deprecated. Use ManagedWindow methods')

def search_for(name):
    if name.startswith( '"' ):
        name = name.split('"')[1]
    else:
        name = name.split()[0]
    if os.sys.platform == "win32":
        for i in os.environ['PATH'].split(';'):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
    else:
        for i in os.environ['PATH'].split(':'):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
    return 0

#-------------------------------------------------------------------------
#
# create_id
#
#-------------------------------------------------------------------------
rand = random.Random(time.time())

def create_id():
    return "%08x%08x" % ( int(time.time()*10000), 
                          rand.randint(0, sys.maxint))

def create_uid(self, handle=None):
    if handle:
        uid = uuid.uuid5(GRAMPS_UUID, handle)
    else:
        uid = uuid.uuid4()
    return uid.hex.upper()

#-------------------------------------------------------------------------
#
# probably_alive
#
#-------------------------------------------------------------------------
def probably_alive(person, db, current_date=None, limit=0):
    """Return true if the person may be alive on current_date.

    This works by a process of emlimination. If we can't find a good
    reason to believe that someone is dead then we assume they must
    be alive.

    :param current_date: a date object that is not estimated or modified
                   (defaults to today)
    :param limit:  number of years to check beyond death_date
    """
    if current_date is None:
        current_date = gen.lib.Date()
        # yr, mon, day:
        current_date.set_yr_mon_day(*time.localtime(time.time())[0:3])

    death_date = None
    # If the recorded death year is before current year then
    # things are simple.
    death_ref = person.get_death_ref()
    if death_ref and death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
        death = db.get_event_from_handle(death_ref.ref)
        if death.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
            death_date = death.get_date_object()
            if death_date.copy_offset_ymd(year=limit).match(current_date, "<<"):
                return False

    # Look for Cause Of Death, Burial or Cremation events.
    # These are fairly good indications that someone's not alive.
    for ev_ref in person.get_primary_event_ref_list():
        ev = db.get_event_from_handle(ev_ref.ref)
        if ev and ev.type in [gen.lib.EventType.CAUSE_DEATH, 
                              gen.lib.EventType.BURIAL, 
                              gen.lib.EventType.CREMATION]:
            if not death_date:
                death_date = ev.get_date_object()
            if ev.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
                if ev.get_date_object().copy_offset_ymd(year=limit).match(current_date,"<<"):
                    return False
        # For any other event of this person, check whether it happened
        # too long ago. If so then the person is likely dead now.
        elif ev and too_old(ev.get_date_object(), current_date.get_year()):
            return False

    birth_date = None
    # If they were born within 100 years before current year then
    # assume they are alive (we already know they are not dead).
    birth_ref = person.get_birth_ref()
    if birth_ref and birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
        birth = db.get_event_from_handle(birth_ref.ref)
        if (birth.get_date_object().get_start_date() != gen.lib.Date.EMPTY):
            if not birth_date:
                birth_date = birth.get_date_object()
            # Check whether the birth event is too old because the
            # code above did not look at birth, only at other events
            birth_obj = birth.get_date_object()
            if birth_obj.get_valid():
                # only if this is a valid birth date:
                if birth_obj.match(current_date,">>"):
                    return False
                if too_old(birth_obj, current_date.get_year()):
                    return False
                if not_too_old(birth_obj, current_date.get_year()):
                    return True
    
    if not birth_date and death_date:
        if death_date.match(current_date.copy_offset_ymd(year=_MAX_AGE_PROB_ALIVE), ">>"):
            # person died more than MAX after current year
            return False

    # Neither birth nor death events are available. Try looking
    # at siblings. If a sibling was born more than 120 years past, 
    # or more than 20 future, then probably this person is
    # not alive. If the sibling died more than 120 years
    # past, or more than 120 years future, then probably not alive.

    family_list = person.get_parent_family_handle_list()
    for family_handle in family_list:
        family = db.get_family_from_handle(family_handle)
        for child_ref in family.get_child_ref_list():
            child_handle = child_ref.ref
            child = db.get_person_from_handle(child_handle)
            child_birth_ref = child.get_birth_ref()
            if child_birth_ref:
                child_birth = db.get_event_from_handle(child_birth_ref.ref)
                dobj = child_birth.get_date_object()
                if dobj.get_start_date() != gen.lib.Date.EMPTY:
                    # if sibling birth date too far away, then not alive:
                    year = dobj.get_year()
                    if year != 0:
                        if not (current_date.copy_offset_ymd(-(_MAX_AGE_PROB_ALIVE + _MAX_SIB_AGE_DIFF)).match(dobj,"<<") and
                                dobj.match(current_date.copy_offset_ymd(_MAX_SIB_AGE_DIFF),"<<")):
                            return False
            child_death_ref = child.get_death_ref()
            if child_death_ref:
                child_death = db.get_event_from_handle(child_death_ref.ref)
                dobj = child_death.get_date_object()
                if dobj.get_start_date() != gen.lib.Date.EMPTY:
                    # if sibling death date too far away, then not alive:
                    year = dobj.get_year()
                    if year != 0:
                        if not (current_date.copy_offset_ymd(-(_MAX_AGE_PROB_ALIVE + _MAX_SIB_AGE_DIFF)).match(dobj,"<<") and
                                dobj.match(current_date.copy_offset_ymd(_MAX_AGE_PROB_ALIVE),"<<")):
                            return False

    # Try looking for descendants that were born more than a lifespan
    # ago.

    def descendants_too_old (person, years):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = db.get_person_from_handle(child_handle)
                child_birth_ref = child.get_birth_ref()
                if child_birth_ref:
                    child_birth = db.get_event_from_handle(child_birth_ref.ref)
                    dobj = child_birth.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        d = gen.lib.Date(dobj)
                        val = d.get_start_date()
                        val = d.get_year() - years
                        d.set_year(val)
                        if not not_too_old (d, current_date.get_year()):
                            return True

                child_death_ref = child.get_death_ref()
                if child_death_ref:
                    child_death = db.get_event_from_handle(child_death_ref.ref)
                    dobj = child_death.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        if not not_too_old (dobj, current_date.get_year()):
                            return True

                if descendants_too_old (child, years + _MIN_GENERATION_YEARS):
                    return True
                
        return False

    # If there are descendants that are too old for the person to have
    # been alive in the current year then they must be dead.

    try:
        age_too_old = descendants_too_old(person, _MIN_GENERATION_YEARS)
        # Set to None otherwise there is a memory leak as this function
        # is recursive
        descendants_too_old = None
        if age_too_old:
            return False
    except RuntimeError:
        raise Errors.DatabaseError(
            _("Database error: %s is defined as his or her own ancestor") %
            name_displayer.display(person))

    def ancestors_too_old(person, year):
        family_handle = person.get_main_parents_family_handle()
        
        if family_handle:                
            family = db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                father = db.get_person_from_handle(father_handle)
                father_birth_ref = father.get_birth_ref()
                if father_birth_ref and father_birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                    father_birth = db.get_event_from_handle(
                        father_birth_ref.ref)
                    dobj = father_birth.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        if not not_too_old (dobj, year - _AVG_GENERATION_GAP):
                            return True

                father_death_ref = father.get_death_ref()
                if father_death_ref and father_death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                    father_death = db.get_event_from_handle(
                        father_death_ref.ref)
                    dobj = father_death.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        if dobj.get_year() < year - _AVG_GENERATION_GAP:
                            return True

                if ancestors_too_old (father, year - _AVG_GENERATION_GAP):
                    return True

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = db.get_person_from_handle(mother_handle)
                mother_birth_ref = mother.get_birth_ref()
                if mother_birth_ref and mother_birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                    mother_birth = db.get_event_from_handle(mother_birth_ref.ref)
                    dobj = mother_birth.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        if not not_too_old (dobj, year - _AVG_GENERATION_GAP):
                            return True

                mother_death_ref = mother.get_death_ref()
                if mother_death_ref and mother_death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                    mother_death = db.get_event_from_handle(
                        mother_death_ref.ref)
                    dobj = mother_death.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        if dobj.get_year() < year - _AVG_GENERATION_GAP:
                            return True

                if ancestors_too_old (mother, year - _AVG_GENERATION_GAP):
                    return True

        return False

    # If there are ancestors that would be too old in the current year
    # then assume our person must be dead too.
    # Set to None otherwise there is a memory leak as this function
    # is recursive
    age_too_old = ancestors_too_old (person, current_date.get_year())
    ancestors_too_old = None
    if age_too_old:
        return False

    # If we can't find any reason to believe that they are dead we
    # must assume they are alive.
    return True

def not_too_old(date, current_year=None):
    if not current_year:
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]
    year = date.get_year()
    return (year != 0 and abs(current_year - year) < _MAX_AGE_PROB_ALIVE)

def too_old(date, current_year=None):
    if current_year:
        the_current_year = current_year
    else:
        time_struct = time.localtime(time.time())
        the_current_year = time_struct[0]
    year = date.get_year()
    return (year != 0 and abs(the_current_year - year) > _MAX_AGE_PROB_ALIVE)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_referents(handle, db, primary_objects):
    """ Find objects that refer to an object.
    
    This function is the base for other get_<object>_referents finctions.
    
    """
    # Use one pass through the reference map to grab all the references
    object_list = [item for item in db.find_backlink_handles(handle)]
    
    # Then form the object-specific lists
    the_lists = ()

    for primary in primary_objects:
        primary_list = [item[1] for item in object_list if item[0] == primary]
        the_lists = the_lists + (primary_list, )

    return the_lists

def get_source_referents(source_handle, db):
    """ Find objects that refer the source.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'MediaObject', 'Repository')
    
    return (get_referents(source_handle, db, _primaries))

def get_media_referents(media_handle, db):
    """ Find objects that refer the media object.

    This function finds all primary objects that refer
    to a given media handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 'Source')
    
    return (get_referents(media_handle, db, _primaries))

def get_note_referents(note_handle, db):
    """ Find objects that refer a note object.
    
    This function finds all primary objects that refer
    to a given note handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'MediaObject', 'Repository')
    
    return (get_referents(note_handle, db, _primaries))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_NEW_NAME_PATTERN = '%s%sUntitled_%d.%s'

def get_new_filename(ext, folder='~/'):
    ix = 1
    while os.path.isfile(os.path.expanduser(_NEW_NAME_PATTERN %
                                            (folder, os.path.sep, ix, ext))):
        ix = ix + 1
    return os.path.expanduser(_NEW_NAME_PATTERN % (folder, os.path.sep, ix, ext))

def get_empty_tempdir(dirname):
    """ Return path to TEMP_DIR/dirname, a guaranteed empty directory

    makes intervening directories if required
    fails if _file_ by that name already exists, 
    or for inadequate permissions to delete dir/files or create dir(s)

    """
    dirpath = os.path.join(TEMP_DIR,dirname)
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    return dirpath

def rm_tempdir(path):
    """Remove a tempdir created with get_empty_tempdir"""
    if path.startswith(TEMP_DIR) and os.path.isdir(path):
        shutil.rmtree(path)

def cast_to_bool(val):
    if val == str(True):
        return True
    return False

def get_type_converter(val):
    """
    Return function that converts strings into the type of val.
    """
    val_type = type(val)
    if val_type in (str, unicode):
        return unicode
    elif val_type == int:
        return int
    elif val_type == float:
        return float
    elif val_type == bool:
        return cast_to_bool
    elif val_type in (list, tuple):
        return list

def type_name(val):
    """
    Return the name the type of val.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    val_type = type(val)
    if val_type == int:
        return 'int'
    elif val_type == float:
        return 'float'
    elif val_type == bool:
        return 'bool'
    elif val_type in (str, unicode):
        return 'unicode'
    return 'unicode'

def get_type_converter_by_name(val_str):
    """
    Return function that converts strings into the type given by val_str.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    if val_str == 'int':
        return int
    elif val_str == 'float':
        return float
    elif val_str == 'bool':
        return cast_to_bool
    elif val_str in ('str', 'unicode'):
        return unicode
    return unicode

def relative_path(original, base):
    """
    Calculate the relative path from base to original, with base a directory,
    and original an absolute path
    On problems, original is returned unchanged
    """
    if not os.path.isdir(base):
        return original
    #original and base must be absolute paths
    if not os.path.isabs(base):
        return original
    if not os.path.isabs(original):
        return original
    original = os.path.normpath(original)
    base = os.path.normpath(base)
    
    # If the db_dir and obj_dir are on different drives (win only)
    # then there cannot be a relative path. Return original obj_path
    (base_drive, base) = os.path.splitdrive(base) 
    (orig_drive, orig_name) = os.path.splitdrive(original)
    if base_drive.upper() != orig_drive.upper():
        return original

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    base_list = (base).split(os.sep)
    target_list = (orig_name).split(os.sep)
    # make sure '/home/person' and 'c:/home/person' both give 
    #   list ['home', 'person']
    base_list = [word for word in base_list if word]
    target_list = [word for word in target_list if word]
    i = -1
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] <> target_list[i]: break
    else:
        #if break did not happen we are here at end, and add 1.
        i += 1
    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)

def media_path(db):
    """
    Given a database, return the mediapath to use as basedir for media
    """
    mpath = db.get_mediapath()
    if mpath is None:
        #use home dir
        mpath = USER_HOME
    return mpath

def media_path_full(db, filename):
    """
    Given a database and a filename of a media, return the media filename
    is full form, eg 'graves/tomb.png' becomes '/home/me/genea/graves/tomb.png
    """
    if os.path.isabs(filename):
        return filename
    mpath = media_path(db)
    return os.path.join(mpath, filename)

def profile(func, *args):
    import hotshot.stats

    prf = hotshot.Profile('mystats.profile')
    print "Start"
    prf.runcall(func, *args)
    print "Finished"
    prf.close()
    print "Loading profile"
    stats = hotshot.stats.load('mystats.profile')
    print "done"
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(100)
    stats.print_callers(100)
    
#-------------------------------------------------------------------------
#
# Keyword translation interface 
#
#-------------------------------------------------------------------------

# keyword, code, translated standard, translated upper
KEYWORDS = [("title",     "t", _("Person|Title"),     _("Person|TITLE")),
            ("given",     "f", _("Given"),     _("GIVEN")),
            ("prefix",    "p", _("Prefix"),    _("PREFIX")),
            ("surname",   "l", _("Surname"),   _("SURNAME")),
            ("suffix",    "s", _("Suffix"),    _("SUFFIX")),
            ("patronymic","y", _("Patronymic"),_("PATRONYMIC")),
            ("call",      "c", _("Call"),      _("CALL")),
            ("common",    "x", _("Common"),    _("COMMON")),
            ("initials",  "i", _("Initials"),  _("INITIALS"))
            ]
KEY_TO_TRANS = {}
TRANS_TO_KEY = {}
for (key, code, standard, upper) in KEYWORDS:
    KEY_TO_TRANS[key] = standard
    KEY_TO_TRANS[key.upper()] = upper
    KEY_TO_TRANS["%" + ("%s" % code)] = standard
    KEY_TO_TRANS["%" + ("%s" % code.upper())] = upper
    TRANS_TO_KEY[standard.lower()] = key
    TRANS_TO_KEY[standard] = key
    TRANS_TO_KEY[upper] = key.upper()

def get_translation_from_keyword(keyword):
    """ Return the translation of keyword """
    return KEY_TO_TRANS.get(keyword, keyword)

def get_keyword_from_translation(word):
    """ Return the keyword of translation """
    return TRANS_TO_KEY.get(word, word)

def get_keywords():
    """ Get all keywords, longest to shortest """
    keys = KEY_TO_TRANS.keys()
    keys.sort(lambda a,b: -cmp(len(a), len(b)))
    return keys

def get_translations():
    """ Get all translations, longest to shortest """
    trans = TRANS_TO_KEY.keys()
    trans.sort(lambda a,b: -cmp(len(a), len(b)))
    return trans

#-------------------------------------------------------------------------
#
# Config-based functions
#
#-------------------------------------------------------------------------
def get_researcher():
    import gen.lib
    import config
    
    n  = config.get('researcher.researcher-name')
    a  = config.get('researcher.researcher-addr')
    c  = config.get('researcher.researcher-city')
    s  = config.get('researcher.researcher-state')
    ct = config.get('researcher.researcher-country')
    p  = config.get('researcher.researcher-postal')
    ph = config.get('researcher.researcher-phone')
    e  = config.get('researcher.researcher-email')

    owner = gen.lib.Researcher()
    owner.set_name(n)
    owner.set_address(a)
    owner.set_city(c)
    owner.set_state(s)
    owner.set_country(ct)
    owner.set_postal_code(p)
    owner.set_phone(ph)
    owner.set_email(e)

    return owner

def update_constants():
    """
    Used to update the constants that are cached in this module.
    """
    import config
    global _MAX_AGE_PROB_ALIVE, _MAX_SIB_AGE_DIFF, _MIN_GENERATION_YEARS, \
        _AVG_GENERATION_GAP
    _MAX_AGE_PROB_ALIVE   = config.get('behavior.max-age-prob-alive')
    _MAX_SIB_AGE_DIFF     = config.get('behavior.max-sib-age-diff')
    _MIN_GENERATION_YEARS = config.get('behavior.min-generation-years')
    _AVG_GENERATION_GAP   = config.get('behavior.avg-generation-gap')

#-------------------------------------------------------------------------
#
# Function to return the name of the main participant of an event
#
#-------------------------------------------------------------------------

def get_participant_from_event(db, event_handle):
    """
    Obtain the first primary or family participant to an event we find in the 
    database. Note that an event can have more than one primary or 
    family participant, only one is returned, adding ellipses if there are
    more. 
    """
    participant = ""
    ellipses = False
    result_list = [i for i in db.find_backlink_handles(event_handle, 
                             include_classes=['Person', 'Family'])]
    #obtain handles without duplicates
    people = set([x[1] for x in result_list if x[0] == 'Person'])
    families = set([x[1] for x in result_list if x[0] == 'Family'])
    for personhandle in people: 
        person = db.get_person_from_handle(personhandle)
        for event_ref in person.get_event_ref_list():
            if event_handle == event_ref.ref and \
                    event_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                if participant:
                    ellipses = True
                else:
                    participant =  name_displayer.display(person)
                break
        if ellipses:
            break
    if ellipses:
        return _('%s, ...') % participant
    
    for familyhandle in families:
        family = db.get_family_from_handle(familyhandle)
        for event_ref in family.get_event_ref_list():
            if event_handle == event_ref.ref and \
                    event_ref.get_role() == gen.lib.EventRoleType.FAMILY:
                if participant:
                    ellipses = True
                else:
                    participant = family_name(family, db)
                break
        if ellipses:
            break
    
    if ellipses:
        return _('%s, ...') % participant
    else:
        return participant
