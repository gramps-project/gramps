#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Douglas S. Blank <doug.blank@gmail.com>
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

"Import from SQL Database"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
from gettext import ngettext
import sqlite3 as sqlite
import re
import time

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ImportSql")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp
from gen.plug import PluginManager, ImportPlugin
from Utils import gender as gender_map
from gui.utils import ProgressMeter
from Utils import create_id

#-------------------------------------------------------------------------
#
# SQL Reader
#
#-------------------------------------------------------------------------
class Database(object):
    """
    The db connection.
    """
    def __init__(self, database):
        self.database = database
        self.db = sqlite.connect(self.database)
        self.cursor = self.db.cursor()

    def query(self, q, *args):
        if q.strip().upper().startswith("DROP"):
            try:
                self.cursor.execute(q, args)
                self.db.commit()
            except:
                "WARN: no such table to drop: '%s'" % q
        else:
            try:
                self.cursor.execute(q, args)
                self.db.commit()
            except:
                print "ERROR: query :", q
                print "ERROR: values:", args
                raise
            return self.cursor.fetchall()

    def close(self):
        """ Closes and writes out tables """
        self.cursor.close()
        self.db.close()

class SQLReader(object):
    def __init__(self, db, filename, callback):
        print filename
        self.db = db
        self.filename = filename
        self.callback = callback
        self.debug = 0

    def openSQL(self):
        sql = None
        try:
            sql = Database(self.filename)
        except IOError, msg:
            errmsg = _("%s could not be opened\n") % self.filename
            ErrorDialog(errmsg,str(msg))
            return None
        return sql

    def process(self):
        progress = ProgressMeter(_('SQLite Import'))
        progress.set_pass(_('Reading data...'), 1)
        sql = self.openSQL() 
        progress.set_pass(_('Importing data...'), 100)
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        t = time.time()

        notes = sql.query("""select * from note;""")
        for note in notes:
            (handle,
             gid, 
             text,
             format,
             note_type1, 
             note_type2,
             change,
             marker0,
             marker1,
             private) = note
            markups = sql.query("""select * from markup where handle = ?""", handle)
            for markup in markups:
                (mhandle,
                 markup0,
                 markup1,
                 value, 
                 start_stop_list) = markup

        t = time.time() - t
        msg = ngettext('Import Complete: %d second','Import Complete: %d seconds', t ) % t
        self.db.transaction_commit(self.trans,_("CSV import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        print msg
        progress.close()
        return None

def importData(db, filename, callback=None):
    g = SQLReader(db, filename, callback)
    g.process()

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_name = _('SQLite Import')
_description = _('SQLite is a common local database format')

pmgr = PluginManager.get_instance()
plugin = ImportPlugin(name            = _('SQLite Database'), 
                      description     = _("Import data from SQLite database"),
                      import_function = importData,
                      extension       = "sql")
pmgr.register_plugin(plugin)

