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

"Import from SQLite Database"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
from gettext import ngettext
import sqlite3 as sqlite
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
from Utils import create_id

#-------------------------------------------------------------------------
#
# Import functions
#
#-------------------------------------------------------------------------
def lookup(handle, event_ref_list):
    """
    Find the handle in a unserialized event_ref_list and return code.
    """
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
# SQLite DB Class
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

#-------------------------------------------------------------------------
#
# SQL Reader
#
#-------------------------------------------------------------------------
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

    # -----------------------------------------------
    # Get methods to retrieve data from the tables
    # -----------------------------------------------

    def get_address_list(self, sql, from_type, from_handle, with_parish):
        results = self.get_links(sql, from_type, from_handle, "address")
        retval = []
        for handle in results:
            result = sql.query("select * from address where handle = ?;",
                               handle)
            retval.append(self.pack_address(sql, result[0], with_parish))
        return retval

    def get_attribute_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "attribute")
        retval = []
        for handle in handles:
            rows = sql.query("select * from attribute where handle = ?;",
                             handle)
            for row in rows:
                (handle,
                 the_type0, 
                 the_type1, 
                 value, 
                 private) = row
                source_list = self.get_source_ref_list(sql, "attribute", handle)
                note_list = self.get_note_list(sql, "attribute", handle)
                retval.append((private, source_list, note_list, 
                               (the_type0, the_type1), value))
        return retval

    def get_child_ref_list(self, sql, from_type, from_handle):
        results = self.get_links(sql, from_type, from_handle, "child_ref")
        retval = []
        for handle in results:
            rows = sql.query("select * from child_ref where handle = ?;",
                             handle)
            for row in rows:
                (handle, ref, frel0, frel1, mrel0, mrel1, private) = row
                source_list = self.get_source_ref_list(sql, "child_ref", handle)
                note_list = self.get_note_list(sql, "child_ref", handle) 
                retval.append((private, source_list, note_list, ref, 
                               (frel0, frel1), (mrel0, mrel1)))
        return retval

    def get_datamap(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "datamap")
        datamap = {}
        for handle in handles:
            row = sql.query("select * from datamap where handle = ?;",
                            handle)
            if len(row) == 1:
                (handle, key_field, value_field) = row[0]
                datamap[key_field] = value_field
            else:
                print "ERROR: invalid datamap item '%s'" % handle
        return datamap

    def get_event_ref_list(self, sql, from_type, from_handle):
        results = self.get_links(sql, from_type, from_handle, "event_ref")
        retval = []
        for handle in results:
            result = sql.query("select * from event_ref where handle = ?;",
                               handle)
            retval.append(self.pack_event_ref(sql, result[0]))
        return retval

    def get_family_list(self, sql, from_type, from_handle):
        return self.get_links(sql, from_type, from_handle, "family") 

    def get_parent_family_list(self, sql, from_type, from_handle):
        return self.get_links(sql, from_type, from_handle, "parent_family") 

    def get_person_ref_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "person_ref")
        retval = []
        for ref_handle in handles:
            rows = sql.query("select * from person_ref where handle = ?;",
                             ref_handle)
            for row in rows:
                (handle,
                 description,
                 private) = row
                source_list = self.get_source_ref_list(sql, "person_ref", handle)
                note_list = self.get_note_list(sql, "person_ref", handle)
                retval.append((private, 
                               source_list,
                               note_list,
                               handle,
                               description))
        return retval

    def get_location_list(self, sql, from_type, from_handle, with_parish):
        handles = self.get_links(sql, from_type, from_handle, "location")
        results = []
        for handle in handles:
            results += sql.query("""select * from location where handle = ?;""",
                                 handle)
        return [self.pack_location(sql, result, with_parish) for result in results]

    def get_lds_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "lds")
        results = []
        for handle in handles:
            results += sql.query("""select * from lds where handle = ?;""",
                                 handle)
        return [self.pack_lds(sql, result) for result in results]

    def get_media_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "media_ref")
        results = []
        for handle in handles:
            results += sql.query("""select * from media_ref where handle = ?;""",
                                 handle)
        return [self.pack_media_ref(sql, result) for result in results]

    def get_note_list(self, sql, from_type, from_handle):
        return self.get_links(sql, from_type, from_handle, "note")

    def get_repository_ref_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "repository_ref")
        results = []
        for handle in handles:
            results += sql.query("""select * from repository_ref where handle = ?;""",
                                 handle)
        return [self.pack_repository_ref(sql, result) for result in results]

    def get_source_ref_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "source_ref")
        results = []
        for handle in handles:
            results += sql.query("""select * from source_ref where handle = ?;""",
                                 handle)
        return [self.pack_source_ref(sql, result) for result in results]

    def get_url_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "url")
        results = []
        for handle in handles:
            results += sql.query("""select * from url where handle = ?;""",
                                 handle)
        return [self.pack_url(sql, result) for result in results]

    # ---------------------------------
    # Helpers
    # ---------------------------------

    def pack_address(self, sql, data, with_parish):
        (handle, private) = data 
        source_list = self.get_source_ref_list(sql, "address", handle)
        date_handle = self.get_link(sql, "address", handle, "date")
        date = self.get_date(sql, date_handle)
        note_list = self.get_note_list(sql, "address", handle)
        location = self.get_location(sql, "address", handle, with_parish)
        return (private, source_list, note_list, date, location)

    def pack_lds(self, sql, data):
        (handle, type, place, famc, temple, status, private) = data
        source_list = self.get_source_ref_list(sql, "lds", handle)
        note_list = self.get_note_list(sql, "lds", handle)
        date_handle = self.get_link(sql, "lds", handle, "date")
        date = self.get_date(sql, date_handle)
        return (source_list, note_list, date, type, place,
                famc, temple, status, private)

    def pack_media_ref(self, sql, data):
        (handle,
         ref,
         role0,
         role1,
         role2,
         role3,
         private) = data
        source_list = self.get_source_ref_list(sql, "media_ref", handle)
        note_list = self.get_note_list(sql, "media_ref", handle)
        attribute_list = self.get_attribute_list(sql, "media_ref", handle)
        if role0 == role1 == role2 == role3 == -1:
            role = None
        else:
            role = (role0, role1, role2, role3)
        return (private, source_list, note_list, attribute_list, ref, role)

    def pack_repository_ref(self, sql, data):
        (handle, 
         ref, 
         call_number, 
         source_media_type0,
         source_media_type1,
         private) = data
        note_list = self.get_note_list(sql, "repository_ref", handle)
        return (note_list, 
                ref,
                call_number, 
                (source_media_type0, source_media_type1),
                private)

    def pack_url(self, sql, data):
        (handle, 
         path, 
         desc, 
         type0, 
         type1, 
         private) = data
        return  (private, path, desc, (type0, type1))

    def pack_event_ref(self, sql, data):
        (handle,
         ref,
         role0,
         role1,
         private) = data
        note_list = self.get_note_list(sql, "event_ref", handle)
        attribute_list = self.get_attribute_list(sql, "event_ref", handle)
        role = (role0, role1)
        return (private, note_list, attribute_list, ref, role)

    def pack_source_ref(self, sql, data):
        (handle, 
         ref, 
         confidence,
         page,
         private) = data
        date_handle = self.get_link(sql, "source_ref", handle, "date")
        date = self.get_date(sql, date_handle)
        note_list = self.get_note_list(sql, "source_ref", handle)
        return (date, private, note_list, confidence, ref, page)

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
        note_list = self.get_note_list(sql, "source", handle)
        media_list = self.get_media_list(sql, "source", handle)
        reporef_list = self.get_repository_ref_list(sql, "source", handle)
        datamap = {}
        return (handle, gid, title,
                author, pubinfo,
                note_list,
                media_list,
                abbrev,
                change, datamap,
                reporef_list,
                (marker0, marker1), private)

    def get_location(self, sql, from_type, from_handle, with_parish):
        handle = self.get_link(sql, from_type, from_handle, "location")
        if handle:
            results = sql.query("""select * from location where handle = ?;""",
                                handle)
            if len(results) == 1:
                return self.pack_location(sql, results[0], with_parish)

    def get_names(self, sql, from_type, from_handle, primary):
        handles = self.get_links(sql, from_type, from_handle, "name")
        names = []
        for handle in handles:
            results = sql.query("""select * from name where handle = ? and primary_name = ?;""",
                                handle, primary)
            if len(results) > 0:
                names += results
        result = [self.pack_name(sql, name) for name in names]
        if primary:
            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                return gen.lib.Name().serialize()
            else:
                raise Exception("too many primary names")
        else:
            return result
     
    def pack_name(self, sql, data):
        # unpack name from SQL table:
        (handle,
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
        # build up a GRAMPS object:
        source_list = self.get_source_ref_list(sql, "name", handle)
        note_list = self.get_note_list(sql, "name", handle)
        date_handle = self.get_link(sql, "name", handle, "date")
        date = self.get_date(sql, date_handle)
        return (private, source_list, note_list, date,
                first_name, surname, suffix, title,
                (name_type0, name_type1), prefix, patronymic,
                group_as, sort_as, display_as, call)

    def pack_location(self, sql, data, with_parish):
        (handle,
         street, 
         city, 
         county, 
         state, 
         country, 
         postal, 
         phone,
         parish) = data
        if with_parish:
            return ((street, city, county, state, country, postal, phone), parish)
        else:
            return (street, city, county, state, country, postal, phone)

    def get_place_from_handle(self, sql, ref_handle):
        if ref_handle: 
            place_row = sql.query("select * from place where handle = ?;",
                                  ref_handle)
            if len(place_row) == 1:
                # return just the handle here:
                return place_row[0][0]
            elif len(place_row) == 0:
                print "ERROR: get_place_from_handle('%s'), no such handle." % (ref_handle, )
            else:
                print "ERROR: get_place_from_handle('%s') should be unique; returned %d records." % (ref_handle, len(place_row))
        return ''

    def get_main_location(self, sql, from_handle, with_parish):
        ref_handle = self.get_link(sql, "place_main", from_handle, "location")
        if ref_handle: 
            place_row = sql.query("select * from location where handle = ?;",
                                  ref_handle)
            if len(place_row) == 1:
                return self.pack_location(sql, place_row[0], with_parish)
            elif len(place_row) == 0:
                print "ERROR: get_main_location('%s'), no such handle." % (ref_handle, )
            else:
                print "ERROR: get_main_location('%s') should be unique; returned %d records." % (ref_handle, len(place_row))
        return gen.lib.Location().serialize()

    def get_link(self, sql, from_type, from_handle, to_link):
        """
        Return a link, and return handle.
        """
        if from_handle is None: return
        assert type(from_handle) in [unicode, str], "from_handle is wrong type: %s is %s" % (from_handle, type(from_handle))
        rows = self.get_links(sql, from_type, from_handle, to_link)
        if len(rows) == 1:
            return rows[0]
        elif len(rows) > 1:
            print "ERROR: too many links %s:%s -> %s (%d)" % (from_type, from_handle, to_link, len(rows))
        return None

    def get_links(self, sql, from_type, from_handle, to_link):
        """
        Return a list of handles (possibly none).
        """
        results = sql.query("""select to_handle from link where from_type = ? and from_handle = ? and to_type = ?;""",
                            from_type, from_handle, to_link)
        return [result[0] for result in results]

    def get_date(self, sql, handle):
        assert type(handle) in [unicode, str, type(None)], "handle is wrong type: %s" % handle
        if handle: 
            rows = sql.query("select * from date where handle = ?;", handle)
            if len(rows) == 1:
                (handle,
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
                if slash1 == day2 == month2 == year2 == slash2 == 0:
                    dateval = day1, month1, year1, slash1
                return (calendar, modifier, quality, dateval, text, sortval, newyear)
            elif len(rows) == 0:
                return None
            else:
                print Exception("ERROR, wrong number of dates: %s" % rows)

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
        self.t = time.time()
        # ---------------------------------
        # Process note
        # ---------------------------------
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
            # direct connection with note handle
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

            note_list = self.get_note_list(sql, "event", handle)
            source_list = self.get_source_ref_list(sql, "event", handle)
            media_list = self.get_media_list(sql, "event", handle)
            attribute_list = self.get_attribute_list(sql, "event", handle)

            date_handle = self.get_link(sql, "event", handle, "date")
            date = self.get_date(sql, date_handle)

            place_handle = self.get_link(sql, "event", handle, "place")
            place = self.get_place_from_handle(sql, place_handle)

            data = (str(handle), gid, (the_type0, the_type1), date, description, place, 
                    source_list, note_list, media_list, attribute_list,
                    change, (marker0, marker1), private)

            self.db.event_map[str(handle)] = data

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
            primary_name = self.get_names(sql, "person", handle, True) # one
            alternate_names = self.get_names(sql, "person", handle, False) # list
            event_ref_list = self.get_event_ref_list(sql, "person", handle)
            family_list = self.get_family_list(sql, "person", handle)
            parent_family_list = self.get_parent_family_list(sql, "person", handle)
            media_list = self.get_media_list(sql, "person", handle)
            address_list = self.get_address_list(sql, "person", handle, with_parish=False)
            attribute_list = self.get_attribute_list(sql, "person", handle)
            urls = self.get_url_list(sql, "person", handle)
            lds_ord_list = self.get_lds_list(sql, "person", handle)
            psource_list = self.get_source_ref_list(sql, "person", handle)
            pnote_list = self.get_note_list(sql, "person", handle)
            person_ref_list = self.get_person_ref_list(sql, "person", handle)
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
        # Process family
        # ---------------------------------
        families = sql.query("""select * from family;""")
        for family in families:
            (handle,
             gid,
             father_handle,
             mother_handle,
             the_type0,
             the_type1,
             change,
             marker0,
             marker1,
             private) = family

            child_ref_list = self.get_child_ref_list(sql, "family", handle)
            event_ref_list = self.get_event_ref_list(sql, "family", handle)
            media_list = self.get_media_list(sql, "family", handle)
            attribute_list = self.get_attribute_list(sql, "family", handle)
            lds_seal_list = self.get_lds_list(sql, "family", handle)
            source_list = self.get_source_ref_list(sql, "family", handle)
            note_list = self.get_note_list(sql, "family", handle)

            self.db.family_map[str(handle)] = (str(handle), gid, 
                                               father_handle, mother_handle,
                                               child_ref_list, (the_type0, the_type1), 
                                               event_ref_list, media_list,
                                               attribute_list, lds_seal_list, 
                                               source_list, note_list,
                                               change, (marker0, marker1), private)

            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process repository
        # ---------------------------------
        repositories = sql.query("""select * from repository;""")
        for repo in repositories:
            (handle, 
             gid, 
             the_type0, 
             the_type1, 
             name, 
             change, 
             marker0, 
             marker1, 
             private) = repo

            note_list = self.get_note_list(sql, "repository", handle)
            address_list = self.get_address_list(sql, "repository", handle, with_parish=False)
            urls = self.get_url_list(sql, "repository", handle)

            self.db.repository_map[str(handle)] = (str(handle), gid, 
                                                   (the_type0, the_type1),
                                                   name, note_list,
                                                   address_list, urls, change, 
                                                   (marker0, marker1), private)
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process place
        # ---------------------------------
        places = sql.query("""select * from place;""")
        for place in places:
            count += 1
            (handle, 
             gid, 
             title, 
             main_loc,
             long, 
             lat, 
             change, 
             marker0, 
             marker1, 
             private) = place

            # We could look this up by "place_main", but we have the handle:
            main_loc = self.get_main_location(sql, handle, with_parish=True)
            alt_location_list = self.get_location_list(sql, "place_alt", handle, 
                                                       with_parish=True)
            urls = self.get_url_list(sql, "place", handle)
            media_list = self.get_media_list(sql, "place", handle)
            source_list = self.get_source_ref_list(sql, "place", handle)
            note_list = self.get_note_list(sql, "place", handle)
            self.db.place_map[str(handle)] = (str(handle), gid, title, long, lat,
                                              main_loc, alt_location_list,
                                              urls,
                                              media_list,
                                              source_list,
                                              note_list,
                                              change, (marker0, marker1), 
                                              private)
            self.callback(100 * count/total)
        # ---------------------------------
        # Process source
        # ---------------------------------
        sources = sql.query("""select * from source;""")
        for source in sources:
            (handle, 
             gid,
             title,
             author,
             pubinfo,
             abbrev,
             change,
             marker0,
             marker1,
             private) = source
            note_list = self.get_note_list(sql, "source", handle)
            media_list = self.get_media_list(sql, "source", handle)
            datamap = self.get_datamap(sql, "source", handle)
            reporef_list = self.get_repository_ref_list(sql, "source", handle)

            self.db.source_map[str(handle)] = (str(handle), gid, title,
                                               author, pubinfo,
                                               note_list,
                                               media_list,
                                               abbrev,
                                               change, datamap,
                                               reporef_list,
                                               (marker0, marker1), private)
            count += 1
            self.callback(100 * count/total)
        # ---------------------------------
        # Process media
        # ---------------------------------
        media = sql.query("""select * from media;""")
        for med in media:
            (handle, 
             gid,
             path,
             mime,
             desc,
             change,
             marker0,
             marker1,
             private) = med

            attribute_list = self.get_attribute_list(sql, "media", handle)
            source_list = self.get_source_ref_list(sql, "media", handle)
            note_list = self.get_note_list(sql, "media", handle)
            
            date_handle = self.get_link(sql, "media", handle, "date")
            date = self.get_date(sql, date_handle)

            self.db.media_map[str(handle)] = (str(handle), gid, path, mime, desc,
                                              attribute_list,
                                              source_list,
                                              note_list,
                                              change,
                                              date,
                                              (marker0, marker1),
                                              private)
            count += 1
            self.callback(100 * count/total)
        return None

    def cleanup(self):
        self.t = time.time() - self.t
        msg = ngettext('Import Complete: %d second','Import Complete: %d seconds', self.t ) % self.t
        self.db.transaction_commit(self.trans,_("SQL import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        print msg


def importData(db, filename, callback=None):
    g = SQLReader(db, filename, callback)
    g.process()
    g.cleanup()
