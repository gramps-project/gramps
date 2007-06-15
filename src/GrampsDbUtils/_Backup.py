#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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

"""
Provides backup and restore functions for a database
"""

#-------------------------------------------------------------------------
#
# load standard python libraries
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gramps libs
#
#------------------------------------------------------------------------
from QuestionDialog import ErrorDialog

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
import os
from GrampsDb import _GrampsDBDir as GrampsDBDir
import cPickle as pickle

LOG = logging.getLogger(".Backup")

def export(database):
    """
    Exports the database to a set of backup files. These files consist
    of the pickled database tables, one file for each table.

    The heavy lifting is done by the private __do__export function. The 
    purpose of this function is to catch any exceptions that occur.

    @param database: database instance to backup
    @type database: GrampsDbDir
    """
    try:
        __do_export(database)
    except (OSError, IOError), msg:
        ErrorDialog(_("Error saving backup data"), str(msg))

def __do_export(database):
    """
    Loop through each table of the database, saving the pickled data
    a file.

    @param database: database instance to backup
    @type database: GrampsDbDir
    """
    try:
        for (base, tbl) in __build_tbl_map(database):
            backup_name = os.path.join(database.get_save_path(), base + ".gbkp.new")
            backup_table = open(backup_name, 'wb')
    
            cursor = tbl.cursor()
            data = cursor.first()
            while data:
                pickle.dump(data, backup_table, 2)
                data = cursor.next()
            cursor.close()
            backup_table.close()
    except (IOError,OSError):
        return

    for (base, tbl) in __build_tbl_map(database):
        new_name = os.path.join(database.get_save_path(), base + ".gbkp")
        old_name = new_name + ".new"
        if os.path.isfile(new_name):
            os.unlink(new_name)
        os.rename(old_name, new_name)

def restore(database):
    """
    Restores the database to a set of backup files. These files consist
    of the pickled database tables, one file for each table.

    The heavy lifting is done by the private __do__restore function. The 
    purpose of this function is to catch any exceptions that occur.

    @param database: database instance to restore
    @type database: GrampsDbDir
    """
    try:
        __do_restore(database)
    except (OSError, IOError), msg:
        ErrorDialog(_("Error restoring backup data"), str(msg))

def __do_restore(database):
    """
    Loop through each table of the database, restoring the pickled data
    to the appropriate database file.

    @param database: database instance to backup
    @type database: GrampsDbDir
    """
    for (base, tbl) in __build_tbl_map(database):
        backup_name = os.path.join(database.get_save_path(), base + ".gbkp")
        backup_table = open(backup_name, 'rb')

        try:
            while True:
                data = pickle.load(backup_table)
                if database.UseTXN:
                    txn = database.env.txn_begin()
                else:
                    txn = None
                tbl.put(data[0], data[1], txn=txn)
                if txn:
                    txn.commit()
        except EOFError:
            if not database.UseTXN:
                tbl.sync()
                
            backup_table.close()

    database.rebuild_secondary()

def __build_tbl_map(database):
    """
    Builds a table map of names to database tables.

    @param database: database instance to backup
    @type database: GrampsDbDir
    """
    return [
        ( GrampsDBDir.PERSON_TBL,  database.person_map.db),
        ( GrampsDBDir.FAMILY_TBL,  database.family_map.db),
        ( GrampsDBDir.PLACES_TBL,  database.place_map.db),
        ( GrampsDBDir.SOURCES_TBL, database.source_map.db),
        ( GrampsDBDir.REPO_TBL,    database.repository_map.db),
        ( GrampsDBDir.NOTE_TBL,    database.note_map.db),
        ( GrampsDBDir.MEDIA_TBL,   database.media_map.db),
        ( GrampsDBDir.EVENTS_TBL,  database.event_map.db),
        ( GrampsDBDir.META,        database.metadata.db),
        ]
