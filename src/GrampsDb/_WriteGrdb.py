#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from _GrampsBSDDB import GrampsBSDDB
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
#
#-------------------------------------------------------------------------
def exportData(database, filename, person=None, callback=None, cl=False):

    if '__call__' in dir(callback): # callback is really callable
        update = update_real

        # Prepare length for the callback
        person_len = database.get_number_of_people()
        family_len = database.get_number_of_families()
        event_len = database.get_number_of_events()
        source_len = database.get_number_of_sources()
        place_len = database.get_number_of_places()
        repo_len = database.get_number_of_repositories()
        obj_len = database.get_number_of_media_objects()
        
        total = person_len + family_len + event_len + place_len + \
                source_len + obj_len + repo_len
    else:
        update = update_empty
        total = 0

    filename = os.path.normpath(filename)
    new_database = GrampsBSDDB()
    try:
        new_database.load(filename,callback)
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        return
    
    # copy all data from new_database to database

    # Need different adders depending on whether the new db is transactional
    if new_database.UseTXN:
        add_data = add_data_txn
    else:
        add_data = add_data_notxn

    primary_tables = {
        'Person': {'cursor_func': database.get_person_cursor,
                   'new_table': new_database.person_map },
        'Family': {'cursor_func': database.get_family_cursor,
                   'new_table': new_database.family_map },
        'Event': {'cursor_func': database.get_event_cursor,
                  'new_table': new_database.event_map },
        'Place': {'cursor_func': database.get_place_cursor,
                  'new_table': new_database.place_map },
        'Source': {'cursor_func': database.get_source_cursor,
                   'new_table': new_database.source_map },
        'MediaObject': {'cursor_func': database.get_media_cursor,
                        'new_table': new_database.media_map },
        'Repository': {'cursor_func': database.get_repository_cursor,
                       'new_table': new_database.repository_map },
        }

    count = 0
    oldval = 0

    for table_name in primary_tables.keys():
        cursor_func = primary_tables[table_name]['cursor_func']
        new_table = primary_tables[table_name]['new_table']

        cursor = cursor_func()
        item = cursor.first()
        while item:
            (handle,data) = item
            add_data(new_database,new_table,handle,data)
            item = cursor.next()
            count,oldval = update(callback,count,oldval,total)
        cursor.close()

    # The metadata is always transactionless,
    # and the table is small, so using key iteration is OK here.
    for handle in database.metadata.keys():
        new_database.metadata.put(handle,database.metadata.get(handle))

    new_database.close()


def add_data_txn(db,table,handle,data):
    the_txn = db.env.txn_begin()
    table.put(handle,data,txn=the_txn)
    the_txn.commit()

def add_data_notxn(db,table,handle,data):
    table.put(handle,data)

def update_empty(callback,count,oldval,total):
    pass

def update_real(callback,count,oldval,total):
    count += 1
    newval = int(100.0*count/total)
    if newval != oldval:
        callback(newval)
        oldval = newval
    return count,oldval
