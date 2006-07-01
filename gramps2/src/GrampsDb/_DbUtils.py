#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

# $Id: __init__.py 6086 2006-03-06 03:54:58Z dallingham $

from gettext import gettext as _

import RelLib
from BasicUtils import UpdateCallback

def remove_family_relationships(db, family_handle, trans=None):
    family = db.get_family_from_handle(family_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    for phandle in [ family.get_father_handle(),
                     family.get_mother_handle()]:
        if phandle:
            person = db.get_person_from_handle(phandle)
            person.remove_family_handle(family_handle)
            db.commit_person(person, trans)

    for ref in family.get_child_ref_list():
        phandle = ref.ref
        person = db.get_person_from_handle(phandle)
        person.remove_parent_family_handle(family_handle)
        db.commit_person(person, trans)

    db.remove_family(family_handle, trans)
    
    if need_commit:
        db.transaction_commit(trans, _("Remove Family"))

def remove_parent_from_family(db, person_handle, family_handle, trans=None):
    """
    Removes a person as either the father or mother of a family,
    deleting the family if it becomes empty.
    """
    person = db.get_person_from_handle(person_handle)
    family = db.get_family_from_handle(family_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    person.remove_family_handle(family_handle)
    if family.get_father_handle() == person_handle:
        family.set_father_handle(None)
        msg = _("Remove father from family")
    elif family.get_mother_handle() == person_handle:
        msg = _("Remove mother from family")
        family.set_mother_handle(None)

    child_list = family.get_child_ref_list()
    if (not family.get_father_handle() and not family.get_mother_handle() and
        len(child_list) <= 1):
        db.remove_family(family_handle, trans)
        if child_list:
            child = db.get_person_from_handle(child_list[0].ref)
            child.remove_parent_family_handle(family_handle)
            db.commit_person(child, trans)
    else:
        db.commit_family(family, trans)
    db.commit_person(person, trans)
    
    if need_commit:
        db.transaction_commit(trans,msg)

def remove_child_from_family(db, person_handle, family_handle, trans=None):
    """
    Removes a person as a child of the family, deleting the family if
    it becomes empty.
    """
    person = db.get_person_from_handle(person_handle)
    family = db.get_family_from_handle(family_handle)
    person.remove_parent_family_handle(family_handle)
    family.remove_child_handle(person_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False
        
    child_list = family.get_child_ref_list()
    if (not family.get_father_handle() and not family.get_mother_handle() and
        len(child_list) <= 1):
        db.remove_family(family_handle, trans)
        if child_list:
            child = db.get_person_from_handle(child_list[0].ref)
            child.remove_parent_family_handle(family_handle)
            db.commit_person(child, trans)
    else:
        db.commit_family(family, trans)
    db.commit_person(person, trans)
    
    if need_commit:
        db.transaction_commit(trans,_("Remove child from family"))


def add_child_to_family(db, family, child,
                        mrel=RelLib.ChildRefType(),
                        frel=RelLib.ChildRefType(),
                        trans=None):

    cref = RelLib.ChildRef()
    cref.ref = child.handle
    cref.set_father_relation(frel)
    cref.set_mother_relation(mrel)
    
    family.add_child_ref(cref)
    child.add_parent_family_handle(family.handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    db.commit_family(family,trans)
    db.commit_person(child,trans)

    if need_commit:
        db.transaction_commit(trans, _('Add child to family') )


def get_total(db):
    person_len = db.get_number_of_people()
    family_len = db.get_number_of_families()
    event_len = db.get_number_of_events()
    source_len = db.get_number_of_sources()
    place_len = db.get_number_of_places()
    repo_len = db.get_number_of_repositories()
    obj_len = db.get_number_of_media_objects()
        
    return person_len + family_len + event_len + \
           place_len + source_len + obj_len + repo_len
        
def db_copy(from_db,to_db,callback):
    """
    Copy all data in from_db into to_db.

    Both databases must be loaded.
    It is assumed that to_db is an empty database,
    so no care is taken to prevent handle collision or merge data.
    """

    uc = UpdateCallback(callback)
    uc.set_total(get_total(from_db))
    
    tables = {
        'Person': {'cursor_func': from_db.get_person_cursor,
                   'table': to_db.person_map,
                   'sec_table' : to_db.id_trans },
        'Family': {'cursor_func': from_db.get_family_cursor,
                   'table': to_db.family_map,
                   'sec_table' : to_db.fid_trans },
        'Event': {'cursor_func': from_db.get_event_cursor,
                  'table': to_db.event_map,
                  'sec_table' : to_db.eid_trans },
        'Place': {'cursor_func': from_db.get_place_cursor,
                  'table': to_db.place_map,
                  'sec_table' : to_db.pid_trans },
        'Source': {'cursor_func': from_db.get_source_cursor,
                   'table': to_db.source_map,
                   'sec_table' : to_db.sid_trans },
        'MediaObject': {'cursor_func': from_db.get_media_cursor,
                        'table': to_db.media_map,
                        'sec_table' : to_db.oid_trans },
        'Repository': {'cursor_func': from_db.get_repository_cursor,
                       'table': to_db.repository_map,
                       'sec_table' : to_db.rid_trans },
        }

    if to_db.__class__.__name__ == 'GrampsBSDDB':
        if to_db.UseTXN:
            add_data = add_data_txn
        else:
            add_data = add_data_notxn
        update_secondary = update_secondary_empty
    else:
        add_data = add_data_dict
        # For InMem databases, the secondary indices need to be
        # created as we copy objects
        update_secondary = update_secondary_inmem

    # Start batch transaction to use async TXN and other tricks
    trans = to_db.transaction_begin("",batch=True)

    for table_name in tables.keys():
        cursor_func = tables[table_name]['cursor_func']
        table = tables[table_name]['table']
        sec_table = tables[table_name]['sec_table']

        cursor = cursor_func()
        item = cursor.first()
        while item:
            (handle,data) = item
            add_data(to_db,table,handle,data)
            update_secondary(sec_table,handle,data)
            item = cursor.next()
            uc.update()
        cursor.close()

    # Commit batch transaction: does nothing, except undoing the tricks
    to_db.transaction_commit(trans,"")

    # Copy bookmarks over:
    # we already know that there's no overlap in handles anywhere
    to_db.bookmarks        = from_db.bookmarks
    to_db.family_bookmarks = from_db.family_bookmarks
    to_db.event_bookmarks  = from_db.event_bookmarks
    to_db.source_bookmarks = from_db.source_bookmarks
    to_db.place_bookmarks  = from_db.place_bookmarks
    to_db.media_bookmarks  = from_db.media_bookmarks
    to_db.repo_bookmarks   = from_db.repo_bookmarks

    # Copy gender stats
    to_db.genderStats = from_db.genderStats

    # Copy custom types
    to_db.family_event_names = from_db.family_event_names
    to_db.individual_event_names = from_db.individual_event_names
    to_db.family_attributes = from_db.family_attributes
    to_db.individual_attributes = from_db.individual_attributes
    to_db.marker_names = from_db.marker_names
    to_db.child_ref_types = from_db.child_ref_types
    to_db.family_rel_types = from_db.family_rel_types
    to_db.event_role_names = from_db.event_role_names
    to_db.name_types = from_db.name_types
    to_db.repository_types = from_db.repository_types
    to_db.source_media_types = from_db.source_media_types
    to_db.url_types = from_db.url_types
    to_db.media_attributes = from_db.media_attributes 

def add_data_txn(db,table,handle,data):
    the_txn = db.env.txn_begin()
    table.put(handle,data,txn=the_txn)
    the_txn.commit()

def add_data_notxn(db,table,handle,data):
    table.put(handle,data)

def add_data_dict(db,table,handle,data):
    table[handle] = data

def update_secondary_empty(sec_table,handle,data):
    pass

def update_secondary_inmem(sec_table,handle,data):
    sec_table[str(data[1])] = str(handle)

def set_birth_death_index(db, person):
    birth_ref_index = -1
    death_ref_index = -1
    event_ref_list = person.get_event_ref_list()
    for index in range(len(event_ref_list)):
        ref = event_ref_list[index]
        event = db.get_event_from_handle(ref.ref)
        if (int(event.get_type()) == RelLib.EventType.BIRTH) \
               and (int(ref.get_role()) == RelLib.EventRoleType.PRIMARY) \
               and (birth_ref_index == -1):
            birth_ref_index = index
        elif (int(event.get_type()) == RelLib.EventType.DEATH) \
                 and (int(ref.get_role()) == RelLib.EventRoleType.PRIMARY) \
                 and (death_ref_index == -1):
            death_ref_index = index

    person.birth_ref_index = birth_ref_index
    person.death_ref_index = death_ref_index
