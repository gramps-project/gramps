#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
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

import RelLib

def children_of_person(db, person):
    """
    Returns a list of Person instances which represents children of 
    the specified person.
    """
    families = [ db.get_family_from_handle(h) \
                     for h in person.get_family_handle_list() ]
    chandles = []
    for family in families:
        chandles += [ ref.ref for ref in family.get_child_ref_list() ]

    return [ db.get_person_from_handle(h) for h in chandles ]

def parents_of_person(db, person):
    """
    Returns a list of Person instances which represents the parents of 
    the specified person. Each element in the list is a tuple consisting
    of the (father, mother)
    """

    families = [ db.get_family_from_handle(h) \
                     for h in person.get_parent_family_handle_list() ]

    parents = []
    for family in families:
        fhandle = family.get_father_handle()
        mhandle = family.get_mother_handle()
        if fhandle:
            father = db.get_person_from_handle(fhandle)
        else:
            father = None
        if mhandle:
            mother = db.get_person_from_handle(mhandle)
        else:
            mother = None
        parents.append((father,mother))
    return parents

def children_of_family(db, family):
    """
    Returns a list of Person instances associated with the family.
    """
    return [ db.get_person_from_handle(ref.ref) \
                 for ref in family.get_child_ref_list() ]

def parents_of_family(db, family):
    """
    Returns a tuple of Person instances representing a father, mother pair.
    """
    fhandle = family.get_father_handle()
    mhandle = family.get_mother_handle()
    if fhandle:
        father = db.get_person_from_handle(fhandle)
    else:
        father = None
    if mhandle:
        mother = db.get_person_from_handle(mhandle)
    else:
        mother = None
    return (father,mother)

def primary_parents_of(db, person):
    handle = person.get_main_parents_family_handle()
    if not handle:
        return (None, None)
    family = db.get_family_from_handle(handle)
    mhandle = family.get_mother_handle()
    fhandle = family.get_father_handle()
    if mhandle:
        mother = db.get_person_from_handle(mhandle)
    else:
        mother = None
    if fhandle:
        father = db.get_person_from_handle(fhandle)
    else:
        father = None
    return (father, mother)

def primary_parent_family_of(db, person):
    handle = person.get_main_parents_family_handle()
    if not handle:
        return db.get_family_from_handle(handle)
    else:
        return None
    
#def events_of_person(db, person):
#    pass

#def events_of_family(db, family):
#    pass

def notes_of(db, obj):
    return [ db.get_note_from_handle(h) for h in obj.get_note_handle_list() ]

def sources_of(db, obj):
    return [ db.get_source_from_handle(h) for h in obj.get_source_handle_list() ]

def sources_of_event(db, event):
    pass

def sources_of_person(db, person):
    pass

def sources_of_note(db, note):
    pass
