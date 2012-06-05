#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
import uuid
import logging
LOG = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
import gen.lib
import Errors
from gen.locale import codeset
import gen.datehandler

from const import TEMP_DIR, USER_HOME, GRAMPS_UUID, IMAGE_DIR
import constfunc
from gen.ggettext import sgettext as _

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
    _AVG_GENERATION_GAP   = config.get('behavior.avg-generation-gap')
except ImportError:
    # Utils used as module not part of GRAMPS
    _MAX_AGE_PROB_ALIVE   = 110
    _MAX_SIB_AGE_DIFF     = 20
    _AVG_GENERATION_GAP   = 20

#-------------------------------------------------------------------------
#
# Integer to String  mappings for constants
#
#-------------------------------------------------------------------------
gender = {
    gen.lib.Person.MALE    : _("male"), 
    gen.lib.Person.FEMALE  : _("female"), 
    gen.lib.Person.UNKNOWN : _("gender|unknown"), 
    }

def format_gender( type):
    return gender.get(type[0], _("Invalid"))

confidence = {
    gen.lib.Citation.CONF_VERY_HIGH : _("Very High"), 
    gen.lib.Citation.CONF_HIGH      : _("High"), 
    gen.lib.Citation.CONF_NORMAL    : _("Normal"), 
    gen.lib.Citation.CONF_LOW       : _("Low"), 
    gen.lib.Citation.CONF_VERY_LOW  : _("Very Low"), 
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

def fix_encoding(value, errors='strict'):
    # The errors argument specifies the response when the input string can't be
    # converted according to the encoding's rules. Legal values for this
    # argument are 'strict' (raise a UnicodeDecodeError exception), 'replace'
    # (add U+FFFD, 'REPLACEMENT CHARACTER'), or 'ignore' (just leave the
    # character out of the Unicode result).
    if not isinstance(value, unicode):
        try:
            return unicode(value)
        except:
            try:
                if constfunc.mac():
                    codeset = locale.getlocale()[1]
                else:
                    codeset = locale.getpreferredencoding()
            except:
                codeset = "UTF-8"
            return unicode(value, codeset, errors)
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
# Preset a name with a name of family member
#
#-------------------------------------------------------------------------

def preset_name(basepers, name, sibling=False):
    """Fill up name with all family common names of basepers. 
    If sibling=True, pa/matronymics are retained.
    """
    surnlist = []
    primname = basepers.get_primary_name()
    prim = False
    for surn in primname.get_surname_list():
        if (not sibling) and (surn.get_origintype().value in 
                        [gen.lib.NameOriginType.PATRONYMIC, 
                         gen.lib.NameOriginType.MATRONYMIC]):
            continue
        surnlist.append(gen.lib.Surname(source=surn))
        if surn.primary:
            prim=True
    if not surnlist:
        surnlist = [gen.lib.Surname()]
    name.set_surname_list(surnlist)
    if not prim:
        name.set_primary_surname(0)
    name.set_family_nick_name(primname.get_family_nick_name())
    name.set_group_as(primname.get_group_as())
    name.set_sort_as(primname.get_sort_as())

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

if constfunc.win():
    # python encoding is ascii, but C functions need to receive the 
    # windows codeset, so convert over to it
    conv_utf8_tosrtkey = lambda x: locale.strxfrm(x.decode("utf-8").encode(
                                                        codeset))
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode(codeset))
    #when gtk is imported the python defaultencoding is utf-8, 
    #so no need to specify it
    conv_utf8_tosrtkey_ongtk = lambda x: locale.strxfrm(unicode(x).encode(
                                                                    codeset))
    conv_unicode_tosrtkey_ongtk = lambda x: locale.strxfrm(x.encode(codeset,'replace'))
else:
    # on unix C functions need to receive utf-8. Default conversion would
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
    #Darwin returns "mac roman" for preferredencoding, but since it
    #returns "UTF-8" for filesystemencoding, and that's first, this
    #works.
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
    
    # Build list of alternate encodings
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

def get_unicode_path_from_file_chooser(path):
    """
    Return the Unicode version of a path string.

    :type  path: str
    :param path: The path to be converted to Unicode
    :rtype:      unicode
    :returns:    The Unicode version of path.
    """
    # make only unicode of path of type 'str'
    if not (isinstance(path,  str)):
        return path

    if constfunc.win():
        # in windows filechooser returns officially utf-8, not filesystemencoding
        try:
            return unicode(path)
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            return unicode(path, sys.getfilesystemencoding(), errors='replace')
    else:
        try:
            return unicode(path, sys.getfilesystemencoding())
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            return unicode(path, sys.getfilesystemencoding(), errors='replace')    

def get_unicode_path_from_env_var(path):
    """
    Return the Unicode version of a path string.

    :type  path: str
    :param path: The path to be converted to Unicode
    :rtype:      unicode
    :returns:    The Unicode version of path.
    """
    # make only unicode of path of type 'str'
    if not (isinstance(path,  str)):
        return path

    if constfunc.win():
        # In Windows path/filename returned from a environment variable is in filesystemencoding
        try:
            new_path = unicode(path, sys.getfilesystemencoding())
            return new_path
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            return unicode(path, sys.getfilesystemencoding(), errors='replace')
    else:
        try:
            return unicode(path)
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            return unicode(path, sys.getfilesystemencoding(), errors='replace')    



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
    if constfunc.win():
        for i in os.environ['PATH'].split(';'):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
        if os.access(name, os.X_OK) and not os.path.isdir(name):
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

class ProbablyAlive(object):
    """
    An object to hold the parameters for considering someone alive.
    """

    def __init__(self, 
                 db,
                 max_sib_age_diff=None, 
                 max_age_prob_alive=None, 
                 avg_generation_gap=None):
        self.db = db
        if max_sib_age_diff is None:
            max_sib_age_diff = _MAX_SIB_AGE_DIFF 
        if max_age_prob_alive is None:
            max_age_prob_alive = _MAX_AGE_PROB_ALIVE
        if avg_generation_gap is None:
            avg_generation_gap = _AVG_GENERATION_GAP
        self.MAX_SIB_AGE_DIFF = max_sib_age_diff
        self.MAX_AGE_PROB_ALIVE = max_age_prob_alive
        self.AVG_GENERATION_GAP = avg_generation_gap

    def probably_alive_range(self, person, is_spouse=False):
        # FIXME: some of these computed dates need to be a span. For
        #        example, if a person could be born +/- 20 yrs around
        #        a date then it should be a span, and yr_offset should
        #        deal with it as well ("between 1920 and 1930" + 10 =
        #        "between 1930 and 1940")
        if person is None:
            return (None, None, "", None)
        birth_ref = person.get_birth_ref()
        death_ref = person.get_death_ref()
        death_date = None
        birth_date = None
        explain = ""
        # If the recorded death year is before current year then
        # things are simple.
        if death_ref and death_ref.get_role().is_primary():
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if death and death.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
                    death_date = death.get_date_object()

        # Look for Cause Of Death, Burial or Cremation events.
        # These are fairly good indications that someone's not alive.
        if not death_date:
            for ev_ref in person.get_primary_event_ref_list():
                if ev_ref:
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_death_fallback():
                        death_date = ev.get_date_object()
                        explain = _("death-related evidence")

        # If they were born within X years before current year then
        # assume they are alive (we already know they are not dead).
        if not birth_date:
            if birth_ref and birth_ref.get_role().is_primary():
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth and birth.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
                    birth_date = birth.get_date_object()

        # Look for Baptism, etc events.
        # These are fairly good indications that someone's birth.
        if not birth_date:
            for ev_ref in person.get_primary_event_ref_list():
                ev = self.db.get_event_from_handle(ev_ref.ref)
                if ev and ev.type.is_birth_fallback():
                    birth_date = ev.get_date_object()
                    explain = _("birth-related evidence")

        if not birth_date and death_date:
            # person died more than MAX after current year
            birth_date = death_date.copy_offset_ymd(year=-self.MAX_AGE_PROB_ALIVE)
            explain = _("death date")
        
        if not death_date and birth_date:
            # person died more than MAX after current year
            death_date = birth_date.copy_offset_ymd(year=self.MAX_AGE_PROB_ALIVE)
            explain = _("birth date")
        
        if death_date and birth_date:
            return (birth_date, death_date, explain, person) # direct self evidence
        
        # Neither birth nor death events are available. Try looking
        # at siblings. If a sibling was born more than X years past, 
        # or more than Z future, then probably this person is
        # not alive. If the sibling died more than X years
        # past, or more than X years future, then probably not alive.

        family_list = person.get_parent_family_handle_list()
        for family_handle in family_list:
            family = self.db.get_family_from_handle(family_handle)
            if family is None:
                continue
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.db.get_person_from_handle(child_handle)
                if child is None:
                    continue
                # Go through once looking for direct evidence:
                for ev_ref in child.get_primary_event_ref_list():
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_birth():
                        dobj = ev.get_date_object() 
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            # if sibling birth date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling birth date
                                return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF),
                                        gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling birth date"),
                                        child)
                    elif ev and ev.type.is_death():
                        dobj = ev.get_date_object() 
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            # if sibling death date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling death date
                                return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE),
                                        gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE 
                                                                + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling death date"),
                                        child)
                # Go through again looking for fallback:
                for ev_ref in child.get_primary_event_ref_list():
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_birth_fallback():
                        dobj = ev.get_date_object() 
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            # if sibling birth date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling birth date
                                return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF),
                                        gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling birth-related date"),
                                        child)
                    elif ev and ev.type.is_death_fallback():
                        dobj = ev.get_date_object() 
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            # if sibling death date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling death date
                                return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE),
                                        gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling death-related date"),
                                        child)

        if not is_spouse: # if you are not in recursion, let's recurse:
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
                    mother_handle = family.get_mother_handle()
                    father_handle = family.get_father_handle()
                    if mother_handle == person.handle and father_handle:
                        father = self.db.get_person_from_handle(father_handle)
                        date1, date2, explain, other = self.probably_alive_range(father, is_spouse=True)
                        if date1 and date2:
                            return date1, date2, _("a spouse, ") + explain, other
                    elif father_handle == person.handle and mother_handle:
                        mother = self.db.get_person_from_handle(mother_handle)
                        date1, date2, explain, other = self.probably_alive_range(mother, is_spouse=True)
                        if date1 and date2:
                            return date1, date2, _("a spouse, ") + explain, other
                    # Let's check the family events and see if we find something
                    for ref in family.get_event_ref_list():
                        if ref:
                            event = self.db.get_event_from_handle(ref.ref)
                            if event:
                                date = event.get_date_object()
                                year = date.get_year()
                                if year != 0:
                                    other = None
                                    if person.handle == mother_handle and father_handle: 
                                        other = self.db.get_person_from_handle(father_handle)
                                    elif person.handle == father_handle and mother_handle: 
                                        other = self.db.get_person_from_handle(mother_handle)
                                    return (gen.lib.Date().copy_ymd(year - self.AVG_GENERATION_GAP),
                                            gen.lib.Date().copy_ymd(year - self.AVG_GENERATION_GAP + 
                                                                    self.MAX_AGE_PROB_ALIVE),
                                                                            
                                            _("event with spouse"), other)

        # Try looking for descendants that were born more than a lifespan
        # ago.

        def descendants_too_old (person, years):
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if not family: 
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    continue
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    child = self.db.get_person_from_handle(child_handle)
                    child_birth_ref = child.get_birth_ref()
                    if child_birth_ref:
                        child_birth = self.db.get_event_from_handle(child_birth_ref.ref)
                        dobj = child_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            d = gen.lib.Date(dobj)
                            val = d.get_start_date()
                            val = d.get_year() - years
                            d.set_year(val)
                            return (d, d.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE),
                                    _("descendant birth date"),
                                    child)
                    child_death_ref = child.get_death_ref()
                    if child_death_ref:
                        child_death = self.db.get_event_from_handle(child_death_ref.ref)
                        dobj = child_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP), 
                                    dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                    _("descendant death date"),
                                    child)
                    date1, date2, explain, other = descendants_too_old (child, years + self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return date1, date2, explain, other
                    # Check fallback data:
                    for ev_ref in child.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                d = gen.lib.Date(dobj)
                                val = d.get_start_date()
                                val = d.get_year() - years
                                d.set_year(val)
                                return (d, d.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE),
                                        _("descendant birth-related date"),
                                        child)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                return (dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP), 
                                        dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                        _("descendant death-related date"),
                                        child)

            return (None, None, "", None)

        # If there are descendants that are too old for the person to have
        # been alive in the current year then they must be dead.

        date1, date2, explain, other = None, None, "", None
        try:
            date1, date2, explain, other = descendants_too_old(person, self.AVG_GENERATION_GAP)
        except RuntimeError:
            raise Errors.DatabaseError(
                _("Database error: %s is defined as his or her own ancestor") %
                name_displayer.display(person))

        if date1 and date2:
            return (date1, date2, explain, other)

        def ancestors_too_old(person, year):
            family_handle = person.get_main_parents_family_handle()
            if family_handle:                
                family = self.db.get_family_from_handle(family_handle)
                if not family: 
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    return (None, None, "", None)
                father_handle = family.get_father_handle()
                if father_handle:
                    father = self.db.get_person_from_handle(father_handle)
                    father_birth_ref = father.get_birth_ref()
                    if father_birth_ref and father_birth_ref.get_role().is_primary():
                        father_birth = self.db.get_event_from_handle(
                            father_birth_ref.ref)
                        dobj = father_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year), 
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor birth date"),
                                    father)
                    father_death_ref = father.get_death_ref()
                    if father_death_ref and father_death_ref.get_role().is_primary():
                        father_death = self.db.get_event_from_handle(
                            father_death_ref.ref)
                        dobj = father_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor death date"),
                                    father)

                    # Check fallback data:
                    for ev_ref in father.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year), 
                                        dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor birth-related date"),
                                        father)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                        dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor death-related date"),
                                        father)

                    date1, date2, explain, other = ancestors_too_old (father, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return date1, date2, explain, other

                mother_handle = family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                    mother_birth_ref = mother.get_birth_ref()
                    if mother_birth_ref and mother_birth_ref.get_role().is_primary():
                        mother_birth = self.db.get_event_from_handle(mother_birth_ref.ref)
                        dobj = mother_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year), 
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor birth date"),
                                    mother)
                    mother_death_ref = mother.get_death_ref()
                    if mother_death_ref and mother_death_ref.get_role().is_primary():
                        mother_death = self.db.get_event_from_handle(
                            mother_death_ref.ref)
                        dobj = mother_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor death date"),
                                    mother)

                    # Check fallback data:
                    for ev_ref in mother.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year), 
                                        dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor birth-related date"),
                                        mother)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object() 
                            if dobj.get_start_date() != gen.lib.Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                        dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor death-related date"),
                                        mother)

                    date1, date2, explain, other = ancestors_too_old (mother, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return (date1, date2, explain, other)

            return (None, None, "", None)

        # If there are ancestors that would be too old in the current year
        # then assume our person must be dead too.
        date1, date2, explain, other = ancestors_too_old (person, - self.AVG_GENERATION_GAP)
        if date1 and date2:
            return (date1, date2, explain, other)

        # If we can't find any reason to believe that they are dead we
        # must assume they are alive.

        return (None, None, "", None)

#-------------------------------------------------------------------------
#
# probably_alive
#
#-------------------------------------------------------------------------
def probably_alive(person, db, 
                   current_date=None, 
                   limit=0,
                   max_sib_age_diff=None, 
                   max_age_prob_alive=None, 
                   avg_generation_gap=None,
                   return_range=False):
    """
    Return true if the person may be alive on current_date.

    This works by a process of elimination. If we can't find a good
    reason to believe that someone is dead then we assume they must
    be alive.

    :param current_date: a date object that is not estimated or modified
                   (defaults to today)
    :param limit:  number of years to check beyond death_date
    :param max_sib_age_diff: maximum sibling age difference, in years
    :param max_age_prob_alive: maximum age of a person, in years
    :param avg_generation_gap: average generation gap, in years
    """
    # First, get the real database to use all people
    # for determining alive status:
    basedb = db.basedb
    # Now, we create a wrapper for doing work:
    pb = ProbablyAlive(basedb, max_sib_age_diff, 
                       max_age_prob_alive, 
                       avg_generation_gap)
    birth, death, explain, relative = pb.probably_alive_range(person)
    if current_date is None:
        current_date = gen.lib.date.Today()
    if not birth or not death:
        # no evidence, must consider alive
        return (True, None, None, _("no evidence"), None)
    # must have dates from here:
    if limit:
        death += limit # add these years to death
    # Finally, check to see if current_date is between dates
    result = (current_date.match(birth, ">=") and 
              current_date.match(death, "<="))
    if return_range:
        return (result, birth, death, explain, relative)
    else:
        return result

def probably_alive_range(person, db, 
                         max_sib_age_diff=None, 
                         max_age_prob_alive=None, 
                         avg_generation_gap=None):
    """
    Computes estimated birth and death dates.
    Returns: (birth_date, death_date, explain_text, related_person)
    """
    # First, find the real database to use all people
    # for determining alive status:
    from gen.proxy.proxybase import ProxyDbBase
    basedb = db
    while isinstance(basedb, ProxyDbBase):
        basedb = basedb.db
    # Now, we create a wrapper for doing work:
    pb = ProbablyAlive(basedb, max_sib_age_diff, 
                       max_age_prob_alive, avg_generation_gap)
    return pb.probably_alive_range(person)

#-------------------------------------------------------------------------
#
# Other util functions
#
#-------------------------------------------------------------------------
def get_referents(handle, db, primary_objects):
    """ Find objects that refer to an object.
    
    This function is the base for other get_<object>_referents functions.
    
    """
    # Use one pass through the reference map to grab all the references
    object_list = list(db.find_backlink_handles(handle))
    
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
    
    Only Citations can refer to sources, so that is all we need to check
    """
    _primaries = ('Citation',)
    
    return (get_referents(source_handle, db, _primaries))

def get_citation_referents(citation_handle, db):
    """ Find objects that refer the citation.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given citation handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'MediaObject', 'Repository')
    
    return (get_referents(citation_handle, db, _primaries))

def get_source_and_citation_referents(source_handle, db):
    """ 
    Find all citations that refer to the sources, and recursively, all objects
    that refer to the sources.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.
    
    Objects -> Citations -> Source
    e.g.
    Media object M1  -> Citation C1 -> Source S1
    Media object M2  -> Citation C1 -> Source S1
    Person object P1 -> Citation C2 -> Source S1
    
    The returned structure is rather ugly, but provides all the information in
    a way that is consistent with the other Util functions.
    (
    tuple of objects that refer to the source - only first element is present
        ([C1, C2],),
    list of citations with objects that refer to them
        [
            (C1, 
                tuple of reference lists
                  P,  F,  E,  Pl, S,  M,        R
                ([], [], [], [], [], [M1, M2]. [])
            )
            (C2, 
                tuple of reference lists
                  P,    F,  E,  Pl, S,  M,  R
                ([P1], [], [], [], [], []. [])
            )
        ]
    )
#47738: DEBUG: citationtreeview.py: line 428: source referents [(['bfe59e90dbb555d0d87'],)]
#47743: DEBUG: citationtreeview.py: line 432: citation bfe59e90dbb555d0d87
#47825: DEBUG: citationtreeview.py: line 435: citation_referents_list [[('bfe59e90dbb555d0d87', ([], [], ['ba77932bf0b2d59eccb'], [], [], [], []))]]
#47827: DEBUG: citationtreeview.py: line 440: the_lists [((['bfe59e90dbb555d0d87'],), [('bfe59e90dbb555d0d87', ([], [], ['ba77932bf0b2d59eccb'], [], [], [], []))])]
    
    """
    the_lists = get_source_referents(source_handle, db)
    LOG.debug('source referents %s' % [the_lists])
    # now, for each citation, get the objects that refer to that citation
    citation_referents_list = []
    for citation in the_lists[0]:
        LOG.debug('citation %s' % citation)
        refs = get_citation_referents(citation, db)
        citation_referents_list += [(citation, refs)]
    LOG.debug('citation_referents_list %s' % [citation_referents_list])    
        
    (citation_list) = the_lists
    the_lists = (citation_list, citation_referents_list)

    LOG.debug('the_lists %s' % [the_lists])
    return the_lists 

def get_media_referents(media_handle, db):
    """ Find objects that refer the media object.

    This function finds all primary objects that refer
    to a given media handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 'Source', 'Citation')
    
    return (get_referents(media_handle, db, _primaries))

def get_note_referents(note_handle, db):
    """ Find objects that refer a note object.
    
    This function finds all primary objects that refer
    to a given note handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'Citation', 'MediaObject', 'Repository')
    
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
    dirpath = get_unicode_path_from_env_var(dirpath)
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
    base_list = filter(None, base_list)
    target_list = filter(None, target_list)
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
# in gen.display.name.py we find:
#        't' : title      = title
#        'f' : given      = given (first names)
#        'l' : surname    = full surname (lastname)
#        'c' : call       = callname
#        'x' : common     = nick name if existing, otherwise first first name (common name)
#        'i' : initials   = initials of the first names
#        'm' : primary    = primary surname (main)
#        '0m': primary[pre]= prefix primary surname (main)
#        '1m': primary[sur]= surname primary surname (main)
#        '2m': primary[con]= connector primary surname (main)
#        'y' : patronymic = pa/matronymic surname (father/mother) - assumed unique
#        '0y': patronymic[pre] = prefix      "  
#        '1y': patronymic[sur] = surname     "
#        '2y': patronymic[con] = connector   "
#        'o' : notpatronymic = surnames without pa/matronymic and primary
#        'r' : rest       = non primary surnames
#        'p' : prefix     = list of all prefixes
#        'q' : rawsurnames = surnames without prefixes and connectors
#        's' : suffix     = suffix
#        'n' : nickname   = nick name
#        'g' : familynick = family nick name
        
KEYWORDS = [("title",     "t", _("Person|Title"),     _("Person|TITLE")),
            ("given",     "f", _("Given"),     _("GIVEN")),
            ("surname",   "l", _("Surname"),    _("SURNAME")),
            ("call",      "c", _("Name|Call"),      _("Name|CALL")),
            ("common",    "x", _("Name|Common"),    _("Name|COMMON")),
            ("initials",  "i", _("Initials"),  _("INITIALS")),
            ("suffix",    "s", _("Suffix"),    _("SUFFIX")),
            ("primary",   "m", _("Name|Primary"), _("PRIMARY")),
            ("primary[pre]",    "0m", _("Primary[pre]"), _("PRIMARY[PRE]")),
            ("primary[sur]",    "1m", _("Primary[sur]"), _("PRIMARY[SUR]")),
            ("primary[con]",    "2m", _("Primary[con]"), _("PRIMARY[CON]")),
            ("patronymic",      "y",  _("Patronymic"), _("PATRONYMIC")),
            ("patronymic[pre]", "0y", _("Patronymic[pre]"), _("PATRONYMIC[PRE]")),
            ("patronymic[sur]", "1y", _("Patronymic[sur]"), _("PATRONYMIC[SUR]")),
            ("patronymic[con]", "2y", _("Patronymic[con]"), _("PATRONYMIC[CON]")),
            ("rawsurnames", "q", _("Rawsurnames"), _("RAWSURNAMES")),
            ("notpatronymic", "o", _("Notpatronymic"),_("NOTPATRONYMIC")),
            ("prefix",    "p", _("Prefix"),    _("PREFIX")),
            ("nickname",  "n", _("Nickname"),    _("NICKNAME")),
            ("familynick", "g", _("Familynick"),   _("FAMILYNICK")),
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
    """
    Return a new database owner with the default values from the config file.
    """
    name  = config.get('researcher.researcher-name')
    address  = config.get('researcher.researcher-addr')
    locality  = config.get('researcher.researcher-locality')
    city  = config.get('researcher.researcher-city')
    state  = config.get('researcher.researcher-state')
    country = config.get('researcher.researcher-country')
    post_code  = config.get('researcher.researcher-postal')
    phone = config.get('researcher.researcher-phone')
    email  = config.get('researcher.researcher-email')

    owner = gen.lib.Researcher()
    owner.set_name(name)
    owner.set_address(address)
    owner.set_locality(locality)
    owner.set_city(city)
    owner.set_state(state)
    owner.set_country(country)
    owner.set_postal_code(post_code)
    owner.set_phone(phone)
    owner.set_email(email)

    return owner

def update_constants():
    """
    Used to update the constants that are cached in this module.
    """
    import config
    global _MAX_AGE_PROB_ALIVE, _MAX_SIB_AGE_DIFF, _AVG_GENERATION_GAP
    _MAX_AGE_PROB_ALIVE   = config.get('behavior.max-age-prob-alive')
    _MAX_SIB_AGE_DIFF     = config.get('behavior.max-sib-age-diff')
    _AVG_GENERATION_GAP   = config.get('behavior.avg-generation-gap')

#-------------------------------------------------------------------------
#
# Function to return the name of the main participant of an event
#
#-------------------------------------------------------------------------
def get_participant_from_event(db, event_handle, all_=False):
    """
    Obtain the first primary or family participant to an event we find in the 
    database. Note that an event can have more than one primary or 
    family participant, only one is returned, adding ellipses if there are
    more. If the all_ parameter is true a comma-space separated string with
    the names of all primary participants is returned and no ellipses is used.
    """
    participant = ""
    ellipses = False
    result_list = list(db.find_backlink_handles(event_handle, 
                             include_classes=['Person', 'Family']))
    #obtain handles without duplicates
    people = set([x[1] for x in result_list if x[0] == 'Person'])
    families = set([x[1] for x in result_list if x[0] == 'Family'])
    for personhandle in people: 
        person = db.get_person_from_handle(personhandle)
        if not person:
            continue
        for event_ref in person.get_event_ref_list():
            if event_handle == event_ref.ref and \
                    event_ref.get_role().is_primary():
                if participant:
                    if all_:
                        participant += ', %s' % name_displayer.display(person)
                    else:
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
                    event_ref.get_role().is_family():
                if participant:
                    if all_:
                        participant += ', %s' % family_name(family, db)
                    else:
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

#-------------------------------------------------------------------------
#
# Function to return children's list of a person
#
#-------------------------------------------------------------------------
def find_children(db,p):
    """
    Return the list of all children's IDs for a person.
    """
    childlist = []
    for family_handle in p.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for child_ref in family.get_child_ref_list():
            childlist.append(child_ref.ref)
    return childlist

#-------------------------------------------------------------------------
#
# Function to return parent's list of a person
#
#-------------------------------------------------------------------------
def find_parents(db,p):
    """
    Return the unique list of all parents' IDs for a person.
    """
    parentlist = []
    for f in p.get_parent_family_handle_list():
        family = db.get_family_from_handle(f)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if father_handle not in parentlist:
            parentlist.append(father_handle)
        if mother_handle not in parentlist:
            parentlist.append(mother_handle)
    return parentlist

#-------------------------------------------------------------------------
#
# Function to return persons, that share the same event.
# This for example links witnesses to the tree
#
#-------------------------------------------------------------------------
def find_witnessed_people(db,p):
    people = []
    for event_ref in p.get_event_ref_list():
        for l in db.find_backlink_handles( event_ref.ref):
            if l[0] == 'Person' and l[1] != p.get_handle() and l[1] not in people:
                people.append(l[1])
            if l[0] == 'Family':
                fam = db.get_family_from_handle(l[1])
                if fam:
                    father_handle = fam.get_father_handle()
                    if father_handle and father_handle != p.get_handle() and father_handle not in people:
                        people.append(father_handle)
                    mother_handle = fam.get_mother_handle()
                    if mother_handle and mother_handle != p.get_handle() and mother_handle not in people:
                        people.append(mother_handle)
    for f in p.get_family_handle_list():
        family = db.get_family_from_handle(f)
        for event_ref in family.get_event_ref_list():
            for l in db.find_backlink_handles( event_ref.ref):
                if l[0] == 'Person' and l[1] != p.get_handle() and l[1] not in people:
                    people.append(l[1])
    for pref in p.get_person_ref_list():
        if pref.ref != p.get_handle and pref.ref not in people:
            people.append(pref.ref)
    return people

#-------------------------------------------------------------------------
#
# Function to return a label to display the active object in the status bar
# and to describe bookmarked objects.
#
#-------------------------------------------------------------------------
def navigation_label(db, nav_type, handle):

    label = None
    obj = None
    if nav_type == 'Person':
        obj = db.get_person_from_handle(handle)
        if obj:
            label = name_displayer.display(obj)
    elif nav_type == 'Family':
        obj = db.get_family_from_handle(handle)
        if obj:
            label = family_name(obj, db)
    elif nav_type == 'Event':
        obj = db.get_event_from_handle(handle)
        if obj:
            try:
                who = get_participant_from_event(db, handle)
            except:
                # get_participants_from_event fails when called during a magic
                # batch transaction because find_backlink_handles tries to
                # access the reference_map_referenced_map which doesn't exist
                # under those circumstances. Since setting the navigation_label
                # is inessential, just accept this and go on.
                who = ''
            desc = obj.get_description()
            label = obj.get_type()
            if desc:
                label = '%s - %s' % (label, desc)
            if who:
                label = '%s - %s' % (label, who)
    elif nav_type == 'Place':
        obj = db.get_place_from_handle(handle)
        if obj:
            label = obj.get_title()
    elif nav_type == 'Source':
        obj = db.get_source_from_handle(handle)
        if obj:
            label = obj.get_title()
    elif nav_type == 'Citation':
        obj = db.get_citation_from_handle(handle)
        if obj:
            label = obj.get_page()
            src = db.get_source_from_handle(obj.get_reference_handle())
            if src:
                label = src.get_title() + " "  + label
    elif nav_type == 'Repository':
        obj = db.get_repository_from_handle(handle)
        if obj:
            label = obj.get_name()
    elif nav_type == 'Media' or nav_type == 'MediaObject':
        obj = db.get_object_from_handle(handle)
        if obj:
            label = obj.get_description()
    elif nav_type == 'Note':
        obj = db.get_note_from_handle(handle)
        if obj:
            label = obj.get()
            # When strings are cut, make sure they are unicode
            #otherwise you may end of with cutting within an utf-8 sequence
            label = unicode(label)
            label = " ".join(label.split())
            if len(label) > 40:
                label = label[:40] + "..."

    if label and obj:
        label = '[%s] %s' % (obj.get_gramps_id(), label)

    return (label, obj)

#-------------------------------------------------------------------------
#
# Format the date and time displayed in the Last Changed column in views.
#
#-------------------------------------------------------------------------
def format_time(secs):
    """
    Format a time in seconds as a date in the preferred date format and a
    24 hour time as hh:mm:ss.
    """
    t = time.localtime(secs)
    d = gen.lib.Date(t.tm_year, t.tm_mon, t.tm_mday)
    return gen.datehandler.displayer.display(d) + time.strftime(' %X', t)

#-------------------------------------------------------------------------
#
# make_unknown
#
#-------------------------------------------------------------------------
def make_unknown(class_arg, explanation, class_func, commit_func, transaction,
                 **argv):
    """
    Make a primary object and set some property so that it qualifies as
    "Unknown".

    Some object types need extra parameters:
    Family: db, Event: type (optional),
    Citation: methods to create/store source.

    Some theoretical underpinning
    This function exploits the fact that all import methods basically do the
    same thing: Create an object of the right type, fill it with some
    attributes, store it in the database. This function does the same, so
    the observation is why not use the creation and storage methods that the 
    import routines use themselves, that makes nice reuse of code. To do this
    formally correct we would need to specify a interface (in the OOP sence)
    which the import methods would need to implement. For now, that is deemed
    too restrictive and here we just slip through because of the similarity in
    code of both GEDCOM and XML import methods.

    :param class_arg: The argument the class_func needs, typically a kind of id.
    :type class_arg: unspecified
    :param explanation: Handle of a note that explains the origin of primary obj
    :type explanation: str
    :param class_func: Method to create primary object.
    :type class_func: method
    :param commit_func: Method to store primary object in db.
    :type commit_func: method
    :param transactino: Database transaction handle
    :type transaction: str
    :param argv: Possible additional parameters
    :type param: unspecified
    :returns: List of newly created objects.
    :rtype: list
    """
    retval = []
    obj = class_func(class_arg)
    if isinstance(obj, gen.lib.Person):
        surname = gen.lib.Surname()
        surname.set_surname('Unknown')
        name = gen.lib.Name()
        name.add_surname(surname)
        name.set_type(gen.lib.NameType.UNKNOWN)
        obj.set_primary_name(name)
    elif isinstance(obj, gen.lib.Family):
        obj.set_relationship(gen.lib.FamilyRelType.UNKNOWN)
        handle = obj.handle
        if getattr(argv['db'].transaction, 'no_magic', False):
            backlinks = argv['db'].find_backlink_handles(
                    handle, [gen.lib.Person.__name__])
            for dummy, person_handle in backlinks:
                person = argv['db'].get_person_from_handle(person_handle)
                add_personref_to_family(obj, person)
        else:
            for person in argv['db'].iter_people():
                if person._has_handle_reference('Family', handle):
                    add_personref_to_family(obj, person)
    elif isinstance(obj, gen.lib.Event):
        if 'type' in argv:
            obj.set_type(argv['type'])
        else:
            obj.set_type(gen.lib.EventType.UNKNOWN)
    elif isinstance(obj, gen.lib.Place):
        obj.set_title(_('Unknown'))
    elif isinstance(obj, gen.lib.Source):
        obj.set_title(_('Unknown'))
    elif isinstance(obj, gen.lib.Citation):
        #TODO create a new source for every citation?
        obj2 = argv['source_class_func'](argv['source_class_arg'])
        obj2.set_title(_('Unknown'))
        obj2.add_note(explanation)
        argv['source_commit_func'](obj2, transaction, time.time())
        retval.append(obj2)
        obj.set_reference_handle(obj2.handle)
    elif isinstance(obj, gen.lib.Repository):
        obj.set_name(_('Unknown'))
        obj.set_type(gen.lib.RepositoryType.UNKNOWN)
    elif isinstance(obj, gen.lib.MediaObject):
        obj.set_path(os.path.join(IMAGE_DIR, "image-missing.png"))
        obj.set_mime_type('image/png')
        obj.set_description(_('Unknown'))
    elif isinstance(obj, gen.lib.Note):
        obj.set_type(gen.lib.NoteType.UNKNOWN);
        text = _('Unknown, created to replace a missing note object.')
        link_start = text.index(',') + 2
        link_end = len(text) - 1
        tag = gen.lib.StyledTextTag(gen.lib.StyledTextTagType.LINK,
                'gramps://Note/handle/%s' % explanation,
                [(link_start, link_end)])
        obj.set_styledtext(gen.lib.StyledText(text, [tag]))
    elif isinstance(obj, gen.lib.Tag):
        if not hasattr(make_unknown, 'count'):
            make_unknown.count = 1 #primitive static variable
        obj.set_name(_("Unknown, was missing %(time)s (%(count)d)") % {
                'time': time.strftime('%x %X', time.localtime()),
                'count': make_unknown.count})
        make_unknown.count += 1
    else:
        raise TypeError("Object if of unsupported type")

    if hasattr(obj, 'add_note'):
        obj.add_note(explanation)
    commit_func(obj, transaction, time.time())
    retval.append(obj)
    return retval

def create_explanation_note(dbase):
    """
    When creating objects to fill missing primary objects in imported files,
    those objects of type "Unknown" need a explanatory note. This funcion
    provides such a note for import methods.
    """
    note = gen.lib.Note( _('Objects referenced by this note '
                                    'were missing in a file imported on %s.') %
                                    time.strftime('%x %X', time.localtime()))
    note.set_handle(create_id())
    note.set_gramps_id(dbase.find_next_note_gramps_id())
    # Use defaults for privacy, format and type.
    return note

def add_personref_to_family(family, person):
    """
    Given a family and person, set the parent/child references in the family,
    that match the person.
    """
    handle = family.handle
    person_handle = person.handle
    if handle in person.get_family_handle_list():
        if ((person.get_gender() == gen.lib.Person.FEMALE) and
                (family.get_mother_handle() is None)):
            family.set_mother_handle(person_handle)
        else:
            # This includes cases of gen.lib.Person.UNKNOWN
            if family.get_father_handle() is None:
                family.set_father_handle(person_handle)
            else:
                family.set_mother_handle(person_handle)
    if handle in person.get_parent_family_handle_list():
        childref = gen.lib.ChildRef()
        childref.set_reference_handle(person_handle)
        childref.set_mother_relation(gen.lib.ChildRefType.UNKNOWN)
        childref.set_father_relation(gen.lib.ChildRefType.UNKNOWN)
        family.add_child_ref(childref)

