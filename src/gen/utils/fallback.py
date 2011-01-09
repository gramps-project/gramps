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
Functional database interface for getting events, or fallback events.
"""

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
