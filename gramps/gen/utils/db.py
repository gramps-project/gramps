#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Utilities for getting information from the database.
"""
#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".gui.utils.db")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib.nameorigintype import NameOriginType
from ..lib.surname import Surname
from ..display.name import displayer as name_displayer
from ..display.place import displayer as place_displayer
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Fallback functions
#
#-------------------------------------------------------------------------
def get_birth_or_fallback(db, person, format=None):
    """
    Get BIRTH event from a person, or fallback to an event around
    the time of birth.
    """
    birth_ref = person.get_birth_ref()
    if birth_ref:   # regular birth found
        event = db.get_event_from_handle(birth_ref.ref)
        if event:
            return event
    # now search the event list for fallbacks
    for event_ref in person.get_primary_event_ref_list():
        if event_ref:
            event = db.get_event_from_handle(event_ref.ref)
            if (event
                and event.type.is_birth_fallback()
                and event_ref.role.is_primary()):
                if format:
                    event.date.format = format
                return event
    return None

def get_death_or_fallback(db, person, format=None):
    """
    Get a DEATH event from a person, or fallback to an
    event around the time of death.
    """
    death_ref = person.get_death_ref()
    if death_ref:   # regular death found
        event = db.get_event_from_handle(death_ref.ref)
        if event:
            return event
    # now search the event list for fallbacks
    for event_ref in person.get_primary_event_ref_list():
        if event_ref:
            event = db.get_event_from_handle(event_ref.ref)
            if (event
                and event.type.is_death_fallback()
                and event_ref.role.is_primary()):
                if format:
                    event.date.format = format
                return event
    return None

def get_age(db, person, fallback=True, calendar="gregorian"):
    """
    Compute the age of person.

    :param person: person handle or person object
    :param fallback: Allow fallback events if True
    :returns: tuple of year, month day if valid, None otherwise
    """
    birth = None
    death = None
    if isinstance(person, str):
        # a handle is passed
        person = db.get_person_from_handle(person)
    if fallback:
        birth = get_birth_or_fallback(db, person)
        death = get_death_or_fallback(db, person)
    else:
        birth_ref = person.get_birth_ref()
        if birth_ref:   # regular birth found
            event = db.get_event_from_handle(birth_ref.ref)
            if event:
                birth = event
        death_ref = person.get_death_ref()
        if death_ref:   # regular death found
            event = db.get_event_from_handle(death_ref.ref)
            if event:
                death = event
    age = None
    if birth is not None:
        birth_date = birth.get_date_object().to_calendar("gregorian")
        if (birth_date and birth_date.get_valid()
                        and not birth_date.is_empty()):
            if death is not None:
                death_date = death.get_date_object().to_calendar("gregorian")
                if (death_date and death_date.get_valid()
                        and not death_date.is_empty()):
                    age = death_date - birth_date
                    if not age.is_valid():
                        age = None
                    else:
                        age = age.tuple()
    return age

def get_timeperiod(db, person):
    """
    Compute the timeperiod a person lived in

    :param person: person handle or person object
    :returns: the year, None otherwise
    """
    if isinstance(person, str):
        # a handle is passed
        person = db.get_person_from_handle(person)
    # the period is the year of birth
    birth = get_birth_or_fallback(db, person)
    if birth is not None:
        birth_date = birth.get_date_object().to_calendar("gregorian")
        if (birth_date and birth_date.get_valid()
                        and not birth_date.is_empty()):
            return birth_date.get_year()
    death = get_death_or_fallback(db, person)
    # no birth, period is death - 20
    if death is not None:
        death_date = death.get_date_object().to_calendar("gregorian")
        if (death_date and death_date.get_valid()
                and not death_date.is_empty()):
            return death_date.get_year() - 20
    # no birth and death, look for another event date we can use
    for event_ref in person.get_primary_event_ref_list():
        if event_ref:
            event = db.get_event_from_handle(event_ref.ref)
            if event:
                event_date = event.get_date_object().to_calendar("gregorian")
                if (event_date and event_date.get_valid()
                        and not event_date.is_empty()):
                    return event_date.get_year()
    return None

def get_event_ref(db, family, event_type):
    """
    Return a reference to a primary family event of the given event type.
    """
    from ..lib.eventroletype import EventRoleType
    if family:
        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if (event and event.get_type() == event_type and
                (event_ref.get_role() == EventRoleType.FAMILY or
                 event_ref.get_role() == EventRoleType.PRIMARY)):
                return event_ref
    return None

def get_primary_event_ref_list(db, family):
    """
    Return a reference to the primary events of the family.
    """
    from ..lib.eventroletype import EventRoleType
    retval = []
    for event_ref in family.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        if (event and
            (event_ref.get_role() == EventRoleType.FAMILY or
             event_ref.get_role() == EventRoleType.PRIMARY)):
            retval.append(event_ref)
    return retval

def get_marriage_or_fallback(db, family, format=None):
    """
    Get a MARRIAGE event from a family, or fallback to an
    alternative event type.
    """
    from ..lib.eventroletype import EventRoleType
    from ..lib.eventtype import EventType
    marriage_ref = get_event_ref(db, family, EventType.MARRIAGE)
    if marriage_ref:   # regular marriage found
        event = db.get_event_from_handle(marriage_ref.ref)
        if event:
            return event
    # now search the event list for fallbacks
    for event_ref in get_primary_event_ref_list(db, family):
        if event_ref:
            event = db.get_event_from_handle(event_ref.ref)
            if (event
                and event.type.is_marriage_fallback()
                and (event_ref.role == EventRoleType.FAMILY or
                     event_ref.role == EventRoleType.PRIMARY)):
                if format:
                    event.date.format = format
                return event
    return None

def get_divorce_or_fallback(db, family, format=None):
    """
    Get a DIVORCE event from a family, or fallback to an
    alternative event type.
    """
    from ..lib.eventroletype import EventRoleType
    from ..lib.eventtype import EventType
    divorce_ref = get_event_ref(db, family, EventType.DIVORCE)
    if divorce_ref:   # regular marriage found
        event = db.get_event_from_handle(divorce_ref.ref)
        if event:
            return event
    # now search the event list for fallbacks
    for event_ref in get_primary_event_ref_list(db, family):
        if event_ref:
            event = db.get_event_from_handle(event_ref.ref)
            if (event
                and event.type.is_divorce_fallback()
                and (event_ref.role == EventRoleType.FAMILY or
                     event_ref.role == EventRoleType.PRIMARY)):
                if format:
                    event.date.format = format
                return event
    return None

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
    more. If the all\_ parameter is true a comma-space separated string with
    the names of all primary participants is returned and no ellipses is used.
    """
    participant = ""
    ellipses = False
    try:
        result_list = list(db.find_backlink_handles(event_handle,
                                 include_classes=['Person', 'Family']))
    except:
        # during a magic batch transaction find_backlink_handles tries to
        # access the reference_map_referenced_map which is closed
        # under those circumstances.
        return ''

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
            who = get_participant_from_event(db, handle)
            desc = obj.get_description()
            label = obj.get_type()
            if desc:
                label = '%s - %s' % (label, desc)
            if who:
                label = '%s - %s' % (label, who)
    elif nav_type == 'Place':
        obj = db.get_place_from_handle(handle)
        if obj:
            label = place_displayer.display(db, obj)
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
    elif nav_type == 'Media' or nav_type == 'Media':
        obj = db.get_media_from_handle(handle)
        if obj:
            label = obj.get_description()
    elif nav_type == 'Note':
        obj = db.get_note_from_handle(handle)
        if obj:
            label = obj.get()
            # When strings are cut, make sure they are unicode
            #otherwise you may end of with cutting within an utf-8 sequence
            label = str(label)
            label = " ".join(label.split())
            if len(label) > 40:
                label = label[:40] + "..."

    if label and obj:
        label = '[%s] %s' % (obj.get_gramps_id(), label)

    return (label, obj)

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
        if family:
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
                        [NameOriginType.PATRONYMIC,
                         NameOriginType.MATRONYMIC]):
            continue
        surnlist.append(Surname(source=surn))
        if surn.primary:
            prim=True
    if not surnlist:
        surnlist = [Surname()]
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

    father = None
    mother = None
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    if father_handle:
        father = db.get_person_from_handle(father_handle)
    if mother_handle:
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

#-------------------------------------------------------------------------
#
# Referents functions
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
                  'Source', 'Media', 'Repository')

    return (get_referents(citation_handle, db, _primaries))

def get_source_and_citation_referents(source_handle, db):
    """
    Find all citations that refer to the sources, and recursively, all objects
    that refer to the sources.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.

    | Objects -> Citations -> Source
    | e.g.
    | Media object M1  -> Citation C1 -> Source S1
    | Media object M2  -> Citation C1 -> Source S1
    | Person object P1 -> Citation C2 -> Source S1

    The returned structure is rather ugly, but provides all the information in
    a way that is consistent with the other Util functions.

    | (
    | tuple of objects that refer to the source - only first element is present
    |     ([C1, C2],),
    | list of citations with objects that refer to them
    |     [
    |         (C1,
    |             tuple of reference lists
    |               P,  F,  E,  Pl, S,  M,        R
    |             ([], [], [], [], [], [M1, M2]. [])
    |         )
    |         (C2,
    |             tuple of reference lists
    |               P,    F,  E,  Pl, S,  M,  R
    |             ([P1], [], [], [], [], []. [])
    |         )
    |     ]
    | )
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
                  'Source', 'Citation', 'Media', 'Repository')

    return (get_referents(note_handle, db, _primaries))
