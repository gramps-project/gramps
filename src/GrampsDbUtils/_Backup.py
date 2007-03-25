#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id: _WriteXML.py 8144 2007-02-17 22:12:56Z hippy $

"""
Contains the interface to allow a database to get written using
GRAMPS' XML file format.
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
import cPickle as pickle

LOG = logging.getLogger(".Backukp")

def export(database):
    try:
        do_export(database)
    except (OSError, IOError), msg:
        ErrorDialog(
            _("Error saving backup data"),
            str(msg))

def do_export(database):

    tables = [
        ('person', database.person_map.db),
        ('family', database.family_map.db),
        ('place',  database.place_map.db),
        ('source', database.source_map.db),
        ('repo',   database.repository_map.db),
        ('note',   database.note_map.db),
        ('media',  database.media_map.db),
        ('event',  database.event_map.db),
        ('meta_data', database.metadata.db),
        ]
      
    for (base, db) in tables:
        backup_name = os.path.join(database.get_save_path(), base + ".gbkp")
        backup_table = open(backup_name, 'w')
    
        cursor = db.cursor()
        d = cursor.first()
        while d:
            pickle.dump(d[1], backup_table, 2)
            d = cursor.next()
        cursor.close()
        backup_table.close()

def restore(database):
    try:
        do_restore(database)
    except (OSError, IOError), msg:
        ErrorDialog(
            _("Error restoring backup data"),
            str(msg))

def do_restore(database):

    tables = [
        ('person', database.person_map),
        ('family', database.family_map),
        ('place',  database.place_map),
        ('source', database.place_map),
        ('repo',   database.repository_map),
        ('note',   database.note_map),
        ('media',  database.media_map),
        ('event',  database.media_map),
        ]
      
    for (base, db) in tables:
        backup_name = os.path.join(database.get_save_path(), base + ".gbkp")
        backup_table = open(backup_name, 'r')

        try:
            while True:
                db[data[0]] = pickle.load(backup_table)
        except EOFError:
            backup_table.close()

