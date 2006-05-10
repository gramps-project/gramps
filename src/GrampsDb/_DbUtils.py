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


import RelLib

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
    elif family.get_mother_handle() == person_handle:
        family.set_mother_handle(None)

    child_list = family.get_child_ref_list()
    if (not family.get_father_handle() and not family.get_mother_handle() and
        len(child_list) <= 1):
        db.remove_family(family_handle, trans)
        if child_list:
            child = db.get_person_from_handle(child_list[0].ref)
            child.remove_parent_family_handle(family_handle)
            db.commit_person(child, trans)
        msg = _("Remove father from family")
    else:
        db.commit_family(family, trans)
        msg = _("Remove mother from family")
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


def db_copy(from_db,to_db,callback):
    if '__call__' in dir(callback): # callback is really callable
        update = update_real

        # Prepare length for the callback
        person_len = from_db.get_number_of_people()
        family_len = from_db.get_number_of_families()
        event_len = from_db.get_number_of_events()
        source_len = from_db.get_number_of_sources()
        place_len = from_db.get_number_of_places()
        repo_len = from_db.get_number_of_repositories()
        obj_len = from_db.get_number_of_media_objects()
        
        total = person_len + family_len + event_len + place_len + \
                source_len + obj_len + repo_len
    else:
        update = update_empty
        total = 0

    primary_tables = {
        'Person': {'cursor_func': from_db.get_person_cursor,
                   'table': to_db.person_map },
        'Family': {'cursor_func': from_db.get_family_cursor,
                   'table': to_db.family_map },
        'Event': {'cursor_func': from_db.get_event_cursor,
                  'table': to_db.event_map },
        'Place': {'cursor_func': from_db.get_place_cursor,
                  'table': to_db.place_map },
        'Source': {'cursor_func': from_db.get_source_cursor,
                   'table': to_db.source_map },
        'MediaObject': {'cursor_func': from_db.get_media_cursor,
                        'table': to_db.media_map },
        'Repository': {'cursor_func': from_db.get_repository_cursor,
                       'table': to_db.repository_map },
        }


    if to_db.__class__.__name__ == 'GrampsBSDDB':
        if to_db.UseTXN:
            add_data = add_data_txn
        else:
            add_data = add_data_notxn
    else:
        add_data = add_data_dict

    oldval = 0
    count = 0

    # Start batch transaction to use async TXN and other tricks
    trans = to_db.transaction_begin("",batch=True)

    for table_name in primary_tables.keys():
        cursor_func = primary_tables[table_name]['cursor_func']
        table = primary_tables[table_name]['table']

        cursor = cursor_func()
        item = cursor.first()
        while item:
            (handle,data) = item
            add_data(to_db,table,handle,data)
            item = cursor.next()
            count,oldval = update(callback,count,oldval,total)
            update(callback,count,oldval,total)
        cursor.close()

    # Commit batch transaction: does nothing, except undoing the tricks
    to_db.transaction_commit(trans,"")

    # The metadata is always transactionless,
    # and the table is small, so using key iteration is OK here.
    for handle in from_db.metadata.keys():
        data = from_db.metadata.get(handle)
        to_db.metadata[handle] = data


def add_data_txn(db,table,handle,data):
    the_txn = db.env.txn_begin()
    table.put(handle,data,txn=the_txn)
    the_txn.commit()

def add_data_notxn(db,table,handle,data):
    table.put(handle,data)

def add_data_dict(db,table,handle,data):
    table[handle] = data

def update_empty(callback,count,oldval,total):
    pass

def update_real(callback,count,oldval,total):
    count += 1
    newval = int(100.0*count/total)
    if newval != oldval:
        callback(newval)
        oldval = newval
    return count,oldval
