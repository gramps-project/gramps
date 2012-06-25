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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Utilities for getting information from the database.
"""
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
from gen.utils.name import family_name
from gen.ggettext import sgettext as _

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

def get_event_ref(db, family, event_type):
    """
    Return a reference to a primary family event of the given event type.
    """
    from gen.lib import EventRoleType
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
    from gen.lib import EventRoleType
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
    from gen.lib import EventType, EventRoleType
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
    from gen.lib import EventType, EventRoleType
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
