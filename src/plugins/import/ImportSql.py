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

def lookup(handle, event_ref_list):
    if handle is None:
        return -1
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            if handle == ref:
                return count
            count += 1
        return -1


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
        if not callable(callback): 
            callback = lambda (percent): None # dummy
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

    def get_event_refs(self, sql, from_type, from_handle):
        results = sql.query("select * from event_ref where from_type = ? and from_handle = ?;",
                            from_type, 
                            from_handle)
        return [self.pack_event_ref(sql, result) for result in results]

    def pack_event_ref(self, sql, data):
        (from_type, 
         from_handle,
         ref,
         role0,
         role1,
         private) = data
        note_list = self.get_links(sql, "event_ref", from_handle, "note")
        attribute_list = self.get_attribute_list(sql, "event_ref", from_handle)
        return (private, note_list, attribute_list, ref, (role0, role1))

    def get_url_list(self, sql, from_type, from_handle):
        # FIXME
        return []

    def get_attribute_list(self, sql, from_type, from_handle):
        # FIXME
        return []

    def get_media_list(self, sql, from_type, from_handle):
        # FIXME
        return []

    def get_sources(self, sql, handle):
        results = sql.query("""select * from source where handle = ?;""",
                           handle)
        return [self.pack_source(sql, result) for result in results]

    def pack_source(self, sql, data):
        (handle, 
         gid, 
         title, 
         author,
         pubinfo,
         abbrev,
         change,
         marker0,
         marker1,
         private) = data

        # FIXME
        note_list = self.get_links(sql, "source", handle, "note")
        media_list = self.get_media_list(sql, "source", handle)
        reporef_list = []
        datamap = None

        return (handle, gid, title,
                author, pubinfo,
                note_list,
                media_list,
                abbrev,
                change, datamap,
                reporef_list,
                (marker0, marker1), private)

    def get_links(self, sql, from_type, from_handle, to_type):
        results = sql.query("""select to_handle from link where from_type = ? and from_handle = ? and to_type = ?;""",
                            from_type, from_handle, to_type)
        return [str(result) for result in results]

    def get_names(self, sql, handle, primary):
        result = sql.query("""select * from name where from_handle = ? and primary_name = ?;""",
                           handle, primary)
        return result

    def package_name(self, sql, handle, primary):
        names = self.get_names(sql, handle, primary)
        result = [self.pack(sql, name) for name in names]
        if primary:
            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                return None
            else:
                raise Exception("too many primary names")
        else:
            return result
     
    def pack(self, sql, data):
        # unpack name from SQL table:
        (from_handle,
        handle,
        primary_name,
        private, 
        first_name, 
        surname, 
        suffix, 
        title, 
        name_type0, 
        name_type1, 
        prefix, 
        patronymic, 
        group_as, 
        sort_as,
        display_as, 
        call) = data
        # FIXME
        source_list = self.get_links(sql, "name", from_handle, "source")
        note_list = self.get_links(sql, "name", from_handle, "note")
        date = self.get_date(sql, "name", from_handle)
        return (private, source_list, note_list, date,
                first_name, surname, suffix, title,
                (name_type0, name_type1), prefix, patronymic,
                group_as, sort_as, display_as, call)

    def get_date(self, sql, from_type, from_handle):
        rows = sql.query("select * from date where from_type = ? and from_handle = ?;",
                         from_type, from_handle)
        if len(rows) == 1:
            (from_type,
             from_handle,
             calendar, 
             modifier, 
             quality,
             day1, 
             month1, 
             year1, 
             slash1,
             day2, 
             month2, 
             year2, 
             slash2,
             text, 
             sortval, 
             newyear) = rows[0]
            dateval = day1, month1, year1, slash1, day2, month2, year2, slash2
            return (calendar, modifier, quality, dateval, text, sortval, newyear)
        elif len(rows) == 0:
            return None
        else:
            raise Exception("ERROR, wrong number of dates: %s" % rows)

    def process(self):
        sql = self.openSQL() 
        total = (sql.query("select count(*) from note;")[0][0] + 
                 sql.query("select count(*) from person;")[0][0] + 
                 sql.query("select count(*) from event;")[0][0] + 
                 sql.query("select count(*) from family;")[0][0] + 
                 sql.query("select count(*) from repository;")[0][0] + 
                 sql.query("select count(*) from place;")[0][0] + 
                 sql.query("select count(*) from media;")[0][0] + 
                 sql.query("select count(*) from source;")[0][0])
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        count = 0.0
        t = time.time()
        # ---------------------------------
        # Process note
        # ---------------------------------
        # FIXME: 11 note objects were referenced but not found
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
            styled_text = [text, []]
            markups = sql.query("""select * from markup where handle = ?""", handle)
            for markup in markups:
                (mhandle,
                 markup0,
                 markup1,
                 value, 
                 start_stop_list) = markup
                ss_list = eval(start_stop_list)
                styled_text[1] += [((markup0, markup1), value, ss_list)]
            self.db.note_map[str(handle)] = (str(handle), gid, styled_text, 
                                        format, (note_type1, note_type2), change, 
                                        (marker0, marker1), private)
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process person
        # ---------------------------------
        people = sql.query("""select * from person;""")
        for person in people:
            if person is None:
                continue
            (handle,        #  0
             gid,          #  1
             gender,             #  2
             death_ref_handle,    #  5
             birth_ref_handle,    #  6
             change,             # 17
             marker0,             # 18
             marker1,             # 18
             private,           # 19
             ) = person
            # primary_name,       #  3
            primary_name = self.package_name(sql, handle, True)
            # alternate_names,    #  4
            alternate_names = self.package_name(sql, handle, False) # list
            # event_ref_list,     #  7
            event_ref_list = self.get_event_refs(sql, "person", handle)
            # family_list,        #  8
            family_list = []
            # parent_family_list, #  9
            parent_family_list = []
            # media_list,         # 10
            media_list = []
            # address_list,       # 11
            address_list = []
            # attribute_list,     # 12
            attribute_list = []
            # urls,               # 13
            urls = self.get_url_list(sql, "person", handle)
            # lds_ord_list,       # 14
            lds_ord_list = []
            # psource_list,       # 15
            psource_list = self.get_links(sql, "person", handle, "source")
            # pnote_list,         # 16
            pnote_list = []
            # person_ref_list,    # 20
            person_ref_list = []
            death_ref_index = lookup(death_ref_handle, event_ref_list)
            birth_ref_index = lookup(birth_ref_handle, event_ref_list)
            self.db.person_map[str(handle)] = (str(handle),        #  0
                                               gid,          #  1
                                               gender,             #  2
                                               primary_name,       #  3
                                               alternate_names,    #  4
                                               death_ref_index,    #  5
                                               birth_ref_index,    #  6
                                               event_ref_list,     #  7
                                               family_list,        #  8
                                               parent_family_list, #  9
                                               media_list,         # 10
                                               address_list,       # 11
                                               attribute_list,     # 12
                                               urls,               # 13
                                               lds_ord_list,       # 14
                                               psource_list,       # 15
                                               pnote_list,         # 16
                                               change,             # 17
                                               (marker0, marker1), # 18
                                               private,            # 19
                                               person_ref_list,    # 20
                                               )
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process event
        # ---------------------------------
        events = sql.query("""select * from event;""")
        for event in events:
            (handle, 
             gid,
             the_type0,
             the_type1,
             description,
             change,
             marker0,
             marker1,
             private) = event

            # FIXME:
            source_list = self.get_links(sql, "event", handle, "source")
            note_list = self.get_links(sql, "event", handle, "note")
            media_list = self.get_links(sql, "event", handle, "media")
            attribute_list = self.get_links(sql, "event", handle, "attribute")

            date = self.get_date(sql, "event", handle)
            place = None # self.get_place()

            data = (str(handle), gid, (the_type0, the_type1), date, description, place, 
                    source_list, note_list, media_list, attribute_list,
                    change, (marker0, marker1), private)

            self.db.event_map[str(handle)] = data

            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process family
        # ---------------------------------
        people = sql.query("""select * from family;""")
        for person in people:
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process repository
        # ---------------------------------
        people = sql.query("""select * from repository;""")
        for person in people:
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process place
        # ---------------------------------
        people = sql.query("""select * from place;""")
        for person in people:
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process source
        # ---------------------------------
        people = sql.query("""select * from source;""")
        for person in people:
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process media
        # ---------------------------------
        people = sql.query("""select * from media;""")
        for person in people:
            count += 1
            self.callback(100 * count/total)

        t = time.time() - t
        msg = ngettext('Import Complete: %d second','Import Complete: %d seconds', t ) % t
        self.db.transaction_commit(self.trans,_("SQL import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        print msg
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

