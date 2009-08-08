# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Douglas S. Blank
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
#
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import sqlite3 as sqlite
import re

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import gen.lib
from gen.plug import PluginManager, ExportPlugin
import DateHandler
from gui.utils import ProgressMeter
import ExportOptions
from Utils import create_id

def lookup(index, event_ref_list):
    if index < 0:
        return None
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            if index == count:
                return ref
            count += 1
        return None

def makeDB(db):
    db.query("""drop table note;""")
    db.query("""drop table person;""")
    db.query("""drop table event;""")
    db.query("""drop table family;""")
    db.query("""drop table repository;""")
    db.query("""drop table date;""")
    db.query("""drop table place;""") 
    db.query("""drop table source;""") 
    db.query("""drop table media;""")
    db.query("""drop table name;""")
    db.query("""drop table link;""")
    db.query("""drop table markup;""")
    db.query("""drop table event_ref;""")
    db.query("""drop table source_ref;""")
    db.query("""drop table child_ref;""")
    db.query("""drop table person_ref;""")
    db.query("""drop table lds;""")
    db.query("""drop table media_ref;""")
    db.query("""drop table address;""")
    db.query("""drop table attribute;""")
    db.query("""drop table url;""")
    # Completed
    db.query("""CREATE TABLE note (
                  handle CHARACTER(25),
                  gid    CHARACTER(25),
                  text   TEXT,
                  format INTEGER,
                  note_type1   INTEGER,
                  note_type2   TEXT,
                  change INTEGER,
                  marker0 INTEGER,
                  marker1 TEXT,
                  private BOOLEAN);""")
    
    db.query("""CREATE TABLE name (
                  from_handle CHARACTER(25),
                  handle CHARACTER(25),
                  primary_name BOOLEAN,
                  private BOOLEAN, 
                  first_name TEXT, 
                  surname TEXT, 
                  suffix TEXT, 
                  title TEXT, 
                  name_type0 INTEGER, 
                  name_type1 TEXT, 
                  prefix TEXT, 
                  patronymic TEXT, 
                  group_as TEXT, 
                  sort_as INTEGER,
                  display_as INTEGER, 
                  call TEXT);""")

    db.query("""CREATE TABLE date (
                  from_type CHARACTER(25),
                  from_handle CHARACTER(25),
                  calendar INTEGER, 
                  modifier INTEGER, 
                  quality INTEGER,
                  day1 INTEGER, 
                  month1 INTEGER, 
                  year1 INTEGER, 
                  slash1 BOOLEAN,
                  day2 INTEGER, 
                  month2 INTEGER, 
                  year2 INTEGER, 
                  slash2 BOOLEAN,
                  text TEXT, 
                  sortval INTEGER, 
                  newyear INTEGER);""")

    db.query("""CREATE TABLE person (
                  handle CHARACTER(25), 
                  gid CHARACTER(25), 
                  gender INTEGER, 
                  death_ref_handle TEXT, 
                  birth_ref_handle TEXT, 
                  change INTEGER, 
                  marker0 INTEGER, 
                  marker1 TEXT, 
                  private BOOLEAN);""")

    db.query("""CREATE TABLE family (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 father_handle CHARACTER(25), 
                 mother_handle CHARACTER(25), 
                 the_type0 INTEGER, 
                 the_type1 TEXT, 
                 change INTEGER, 
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE place (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 title TEXT, 
                 long FLOAT, 
                 lat FLOAT, 
                 change INTEGER, 
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE event (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 the_type0 INTEGER, 
                 the_type1 TEXT, 
                 description TEXT, 
                 change INTEGER, 
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE source (
                 from_type CHARACTER(25),
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 title TEXT, 
                 author TEXT, 
                 pubinfo TEXT, 
                 abbrev TEXT, 
                 change INTEGER,
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE media (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 path TEXT, 
                 mime TEXT, 
                 desc TEXT,
                 change INTEGER, 
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE repository (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 the_type0 INTEGER, 
                 the_type1 TEXT,
                 name TEXT, 
                 change INTEGER, 
                 marker0 INTEGER, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE link (
                 from_type CHARACTER(25), 
                 from_handle CHARACTER(25), 
                 to_type CHARACTER(25), 
                 to_handle CHARACTER(25));""")

    db.query("""CREATE TABLE markup (
                 handle CHARACTER(25), 
                 markup0 INTEGER, 
                 markup1 TEXT, 
                 value TEXT, 
                 start_stop_list TEXT);""")

    db.query("""CREATE TABLE event_ref (
                 from_type CHARACTER(25), 
                 from_handle CHARACTER(25), 
                 ref CHARACTER(25), 
                 role0 INTEGER, 
                 role1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE person_ref (
                 from_type CHARACTER(25), 
                 from_handle CHARACTER(25), 
                 handle CHARACTER(25), 
                 description TEXT,
                 private BOOLEAN);""")

    db.query("""CREATE TABLE source_ref (
                 type CHARACTER(25), 
                 handle CHARACTER(25), 
                 ref CHARACTER(25), 
                 confidence INTEGER,
                 page CHARACTER(25),
                 private BOOLEAN);""")

    db.query("""CREATE TABLE child_ref (
                 from_type CHARACTER(25), 
                 from_handle CHARACTER(25), 
                 ref CHARACTER(25), 
                 frel0 INTEGER,
                 frel1 CHARACTER(25),
                 mrel0 INTEGER,
                 mrel1 CHARACTER(25),
                 private BOOLEAN);""")

    db.query("""CREATE TABLE lds (
                 from_type CHARACTER(25), 
                 from_handle CHARACTER(25), 
                 handle CHARACTER(25), 
                 type CHARACTER(25), 
                 place TEXT, 
                 famc CHARACTER(25), 
                 temple TEXT, 
                 status TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE media_ref (
                 handle CHARACTER(25),
                 ref CHARACTER(25),
                 role TEXT,
                 private BOOLEAN);""")

    db.query("""CREATE TABLE address (
                 from_type CHARACTER(25),
                 from_handle CHARACTER(25),
                 handle CHARACTER(25),
                 street TEXT, 
                 city TEXT, 
                 county TEXT, 
                 state TEXT, 
                 country TEXT, 
                 postal TEXT, 
                 phone TEXT,
                 parish TEXT,
                 private BOOLEAN);""")

    db.query("""CREATE TABLE attribute (
                 handle CHARACTER(25),
                 from_type CHARACTER(25),
                 from_handle CHARACTER(25),
                 the_type0 INTEGER, 
                 the_type1 TEXT, 
                 value TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE url (
                 path TEXT, 
                 desc TXT, 
                 type CHARACTER(1),                  
                 private BOOLEAN);
                 """)

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

def export_place(db, from_type, from_handle, place_handle):
    export_link(db, from_type, from_handle, "place", place_handle)

def export_url_list(db, from_type, handle, urls):
    for url in urls:
        # (False, u'http://www.gramps-project.org/', u'loleach', (0, u'kaabgo'))
        private, path, desc, type = url
        db.query("""insert INTO url (
                 path, 
                 desc, 
                 type,                  
                 private) VALUES (?, ?, ?, ?);
                 """,
                 path,
                 desc,
                 type[0],
                 private)

def export_person_ref_list(db, from_type, from_handle, person_ref_list):
    for person_ref in person_ref_list:
        (private, 
         source_list,
         note_list,
         handle,
         desc) = person_ref
        db.query("""INSERT INTO person_ref (
                    from_type,
                    from_handle, 
                    handle,
                    description,
                    private) VALUES (?, ?, ?, ?, ?);""",
                 from_type,
                 from_handle,
                 handle,
                 desc,
                 private
                 )
        export_list(db, "person_ref", handle, "note", note_list)
        export_source_list(db, "person_ref", handle, source_list)


def export_event_ref(db, from_type, from_handle, ref, role, private):
    db.query("""insert INTO event_ref (
                 from_type,
                 from_handle, 
                 ref, 
                 role0, 
                 role1, 
                 private) VALUES (?, ?, ?,?,?,?);""",
             from_type, 
             from_handle, 
             ref, 
             role[0], 
             role[1], 
             private) 

def export_markup(db, handle, markup_code0, markup_code1, value, 
                  start_stop_list):
    db.query("""INSERT INTO markup (
                 handle, 
                 markup0, 
                 markup1, 
                 value, 
                 start_stop_list) VALUES (?,?,?,?,?);""",
             handle, markup_code0, markup_code1, value, 
             start_stop_list)

def export_lds(db, from_type, from_handle, handle, type, place, famc, temple, status, private):
    db.query("""INSERT into lds (from_type, from_handle, handle, type, place, famc, temple, status, private) 
             VALUES (?,?,?,?,?,?,?,?,?);""",
             from_type, from_handle, handle, type, place, famc, temple, status, private)
    # FIXME: remove place from here?
    
def export_media_ref(db, handle, ref, role, private):
    db.query("""INSERT into media_ref (
                 handle,
                 ref,
                 role,
                 private) VALUES (?,?,?,?);""",
             handle, ref, str(role), private) # FIXME: role with two parts

def export_source_ref(db, from_type, handle, ref, private, confidence, page):
    db.query("""INSERT into source_ref (
             type,
             handle, 
             ref, 
             confidence,
             page,
             private
             ) VALUES (?, ?,?,?,?,?);""",
             from_type,
             handle, 
             ref, 
             confidence,
             page,
             private)

def export_source(db, handle, gid, title, author, pubinfo, abbrev, change,
                   marker0, marker1, private):
    db.query("""INSERT into source (
             handle, 
             gid, 
             title, 
             author, 
             pubinfo, 
             abbrev, 
             change,
             marker0, 
             marker1, 
             private
             ) VALUES (?,?,?,?,?,?,?,?,?,?);""",
             handle, 
             gid, 
             title, 
             author, 
             pubinfo, 
             abbrev, 
             change,
             marker0, 
             marker1, 
             private)

def export_note(db, handle, gid, text, format, note_type0,
                note_type1, change, marker0, marker1, private):
    db.query("""INSERT into note (handle,
                  gid,
                  text,
                  format,
                  note_type1,
                  note_type2,
                  change,
                  marker0,
                  marker1,
                  private) values (?, ?, ?, ?, ?,
                                   ?, ?, ?, ?, ?);""", 
             handle, gid, text, format, note_type0,
             note_type1, change, marker0, marker1, private)

def export_name(db, from_handle, handle, primary, data):
    if data:
        (private, source_list, note_list, date,
         first_name, surname, suffix, title,
         name_type, prefix, patronymic,
         group_as, sort_as, display_as, call) = data

        db.query("""INSERT into name (
                  from_handle,
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
                  call
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                              ?, ?, ?, ?, ?, ?, ?);""",
                 from_handle, handle, primary, private, first_name, surname, suffix, title,
                 name_type[0], name_type[1], prefix, patronymic, group_as, 
                 sort_as, display_as, call)

        if date:
            export_date(db, "name", handle, date) 
        export_list(db, "name", handle, "note", note_list)
        export_source_list(db, "name", handle, source_list)

def export_date(db, date_type, handle, date):
    if True:
        (calendar, modifier, quality, dateval, text, sortval, newyear) = date
        if len(dateval) == 4:
            day1, month1, year1, slash1 = dateval
            day2, month2, year2, slash2 = 0, 0, 0, 0
        elif len(dateval) == 8:
            day1, month1, year1, slash1, day2, month2, year2, slash2 = dateval
        else:
            raise ("ERROR:", dateval)
        db.query("""INSERT INTO date (
                  from_type,
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
                  newyear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                   ?, ?, ?, ?, ?, ?, ?);""",
                 date_type, handle, calendar, modifier, quality, 
                 day1, month1, year1, slash1, 
                 day2, month2, year2, slash2,
                 text, sortval, newyear)

def export_attribute(db, from_type, from_handle, attr_handle, the_type, value, private):
    db.query("""INSERT INTO attribute (
                 handle,
                 from_type,
                 from_handle,
                 the_type0, 
                 the_type1, 
                 value, 
                 private) VALUES (?,?,?,?,?,?,?);""",
             attr_handle, from_type, from_handle, the_type[0], the_type[1], value, private)

def export_source_list(db, from_type, handle, source_list):
    # Event Sources
    for source in source_list:
        (date, private, note_list, confidence, ref, page) = source
        export_source_ref(db, from_type, handle, ref, private, confidence, page)
        if date:
            export_date(db, "source", ref, date)
        export_list(db, "source", ref, "note", note_list) 

def export_media_list(db, from_type, from_handle, media_list):
    # Media list
    for media in media_list:
        (private, source_list, note_list,attribute_list,ref,role) = media
        export_media_ref(db, from_handle, ref, role, private)
        export_list(db, "media", ref, "note", note_list)
        export_attribute_list(db, "media", ref, attribute_list)

def export_attribute_list(db, from_type, from_handle, attribute_list):
    for attribute in attribute_list:
        (private, source_list, note_list, the_type, value) = attribute
        attr_handle = create_id()
        export_attribute(db, from_type, from_handle, attr_handle, the_type, value, private)
        export_list(db, "attribute", attr_handle, "note", note_list)
        export_source_list(db, "atribute", attr_handle, source_list)

def export_child_ref_list(db, from_type, from_handle, to_type, ref_list):
    for child_ref in ref_list:
        # family -> child_ref
        # (False, [], [], u'b305e96e39652d8f08c', (1, u''), (1, u''))
        (private, source_list, note_list, ref, frel, mrel) = child_ref
        db.query("""INSERT INTO child_ref (from_type, from_handle, 
                     ref, frel0, frel1, mrel0, mrel1, private)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                 from_type, from_handle, ref, frel[0], frel[1], 
                 mrel[0], mrel[1], private)
        export_source_list(db, from_type, ref, source_list)
        export_list(db, from_type, ref, "note", note_list)

def export_list(db, from_type, from_handle, to_type, handle_list):
    for to_handle in handle_list:
        export_link(db, from_type, from_handle, to_type, to_handle)
            
def export_link(db, from_type, from_handle, to_type, to_handle):
    db.query("""insert into link (
                   from_type, 
                   from_handle, 
                   to_type, 
                   to_handle) values (?, ?, ?, ?)""",
             from_type, from_handle, to_type, to_handle)

def export_address(db, from_type, from_handle, handle, street, city, county, 
                   state, country, postal, phone, private, parish=None):
    db.query("""INSERT INTO address (
                 from_type,
                 from_handle,
                 handle,
                 street, 
                 city, 
                 county, 
                 state, 
                 country, 
                 postal, 
                 phone,
                 parish,
                 private) VALUES (?, ?, ?,?,?,?,?,?,?,?,?,?);""",
             from_type, from_handle, handle, street, city, county, state, country, postal, phone, parish, private)


def exportData(database, filename, option_box=None, callback=None):
    if not callable(callback): 
        callback = lambda (percent): None # dummy

    total = (len(database.note_map) + 
             len(database.person_map) +
             len(database.event_map) + 
             len(database.family_map) +
             len(database.repository_map) +
             len(database.place_map) +
             len(database.media_map) +
             len(database.source_map))
    count = 0.0

    db = Database(filename)
    makeDB(db)

    # ---------------------------------
    # Notes
    # ---------------------------------
    for note_handle in database.note_map.keys():
        note = database.note_map[note_handle]
        (handle, gid, styled_text, format, note_type,
         change, marker, private) = note
        text, markup_list = styled_text
        export_note(db, handle, gid, text, format, note_type[0],
                    note_type[1], change, marker[0], marker[1], private)
        for markup in markup_list:
            markup_code, value, start_stop_list = markup
            export_markup(db, handle, markup_code[0], markup_code[1], value, 
                          str(start_stop_list)) # Not normal form; use eval
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Event
    # ---------------------------------
    for event_handle in database.event_map.keys():
        event = database.event_map[event_handle]
        (handle, gid, the_type, date, description, place, 
         source_list, note_list, media_list, attribute_list,
         change, marker, private) = event
        if date:
            export_date(db, "event", event_handle, date)
        db.query("""INSERT INTO event (
                 handle, 
                 gid, 
                 the_type0, 
                 the_type1, 
                 description, 
                 change, 
                 marker0, 
                 marker1, 
                 private) VALUES (?,?,?,?,?,?,?,?,?);""",
                 handle, 
                 gid, 
                 the_type[0], 
                 the_type[1], 
                 description, 
                 change, 
                 marker[0], 
                 marker[1], 
                 private)

        if place:
            export_place(db, "event", handle, place)
        export_list(db, "event", handle, "note", note_list)
        export_attribute_list(db, "event", handle, attribute_list)
        export_media_list(db, "event", handle, media_list)
        export_source_list(db, "event", handle, source_list)

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Person
    # ---------------------------------
    for person_handle in database.person_map.keys():
        person = database.person_map[person_handle]
        (handle,        #  0
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
         marker,             # 18
         private,           # 19
         person_ref_list,    # 20
         ) = person
        db.query("""INSERT INTO person (
                  handle, 
                  gid, 
                  gender, 
                  death_ref_handle, 
                  birth_ref_handle, 
                  change, 
                  marker0, 
                  marker1, 
                  private) values (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                  handle, 
                  gid, 
                  gender, 
                  lookup(death_ref_index, event_ref_list),
                  lookup(birth_ref_index, event_ref_list),
                  change, 
                  marker[0], 
                  marker[1], 
                  private)

        # Event Reference information
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            export_event_ref(db, "person", handle, ref, role, private)
            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)
        export_list(db, "person", handle, "family", family_list) 
        export_list(db, "person", handle, "parent_family", parent_family_list)
        export_media_list(db, "person", handle, media_list)
        export_list(db, "person", handle, "note", pnote_list)
        export_attribute_list(db, "person", handle, attribute_list)
        export_url_list(db, "person", handle, urls) 
        export_person_ref_list(db, "person", handle, person_ref_list)
        export_source_list(db, "person", handle, psource_list)

        # -------------------------------------
        # Address
        # -------------------------------------
        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            (street, city, county, state, country, postal, phone) = location
            addr_handle = create_id()
            export_address(db, "person", handle, addr_handle, street, city, county, state, country, postal, phone, private)
            if date:
                export_date(db, "address", addr_handle, date)
            export_list(db, "address", addr_handle, "note", anote_list) 
            export_source_list(db, "address", addr_handle, source_list)

        # -------------------------------------
        # LDS ord
        # -------------------------------------
        for ldsord in lds_ord_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            lds_handle = create_id()
            # FIXME: place?
            export_lds(db, "person", handle, lds_handle, type, place, famc, temple, status, lprivate)
            if date:
                export_date(db, "lds", lds_handle, date)
            export_list(db, "lds", lds_handle, "note", lnote_list)
            export_source_list(db, "lds", lds_handle, lsource_list)

        # -------------------------------------
        # Names
        # -------------------------------------
        export_name(db, handle, create_id(), True, primary_name)
        map(lambda name: export_name(db, handle, create_id(), False, name), 
            alternate_names)
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Family
    # ---------------------------------
    for family_handle in database.family_map.keys():
        family = database.family_map[family_handle]
        (handle, gid, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, source_list, note_list,
         change, marker, private) = family
        # father_handle and/or mother_handle can be None
        db.query("""INSERT INTO family (
                 handle, 
                 gid, 
                 father_handle, 
                 mother_handle,
                 the_type0, 
                 the_type1, 
                 change, 
                 marker0, 
                 marker1, 
                 private) values (?,?,?,?,?,?,?,?,?,?);""",
                 handle, gid, father_handle, mother_handle,
                 the_type[0], the_type[1], change, marker[0], marker[1], 
                 private)

        export_child_ref_list(db, "family", handle, "child_ref", child_ref_list)
        export_list(db, "family", handle, "note", pnote_list)
        export_attribute_list(db, "family", handle, attribute_list)
        export_source_list(db, "family", handle, source_list)
        export_media_list(db, "family", handle, media_list)

        # Event Reference information
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            export_event_ref(db, "family", handle, ref, role, private)
            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)
            
        # -------------------------------------
        # LDS 
        # -------------------------------------
        for ldsord in lds_seal_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            lds_handle = create_id()
            # FIXME: place?
            export_lds(db, "family", handle, lds_handle, type, place, famc, temple, status, lprivate)
            if date:
                export_date(db, "lds", lds_handle, date)
            export_list(db, "lds", lds_handle, "note", lnote_list)
            export_source_list(db, "lds", lds_handle, lsource_list)

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Repository
    # ---------------------------------
    for repository_handle in database.repository_map.keys():
        repository = database.repository_map[repository_handle]
        (handle, gid, the_type, name, note_list,
         address_list, urls, change, marker, private) = repository

        db.query("""INSERT INTO repository (
                 handle, 
                 gid, 
                 the_type0, 
                 the_type1,
                 name, 
                 change, 
                 marker0, 
                 marker1, 
                 private) VALUES (?,?,?,?,?,?,?,?,?);""",
                 handle, gid, the_type[0], the_type[1],
                 name, change, marker[0], marker[1], private)
        
        export_list(db, "lds", lds_handle, "note", lnote_list)

        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            (street, city, county, state, country, postal, phone) = location
            addr_handle = create_id()
            export_address(db, "repository", handle, addr_handle, street, city, county, state, 
                           country, postal, phone, private)
            if date:
                export_date(db, "address", addr_handle, date)
            export_list(db, "address", addr_handle, "note", anote_list) 
            export_source_list(db, "address", addr_handle, asource_list)

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Place
    # ---------------------------------
    for place_handle in database.place_map.keys():
        place = database.place_map[place_handle]
        (handle, gid, title, long, lat,
         main_loc, alt_location_list,
         urls,
         media_list,
         source_list,
         note_list,
         change, marker, private) = place

        db.query("""INSERT INTO place (
                 handle, 
                 gid, 
                 title, 
                 long, 
                 lat, 
                 change, 
                 marker0, 
                 marker1, 
                 private) values (?,?,?,?,?,?,?,?,?);""",
                 handle, gid, title, long, lat,
                 change, marker[0], marker[1], private)

        export_url_list(db, "place", handle, urls)
        export_media_list(db, "place", handle, media_list)
        export_source_list(db, "place", handle, source_list)
        export_list(db, "place", handle, "note", note_list) 

        # FIX: losing link to places?
        for location in alt_location_list:
            ((street, city, county, state, country, postal, phone), parish) = location
            addr_handle = create_id()
            export_address(db, "place", handle, addr_handle, street, city, county, state, 
                           country, postal, phone, private, parish)

        (street, city, county, state, country, postal, phone, 
         private, parish) =  main_loc
        export_address(db, "place", handle, create_id(), street, city, 
                       county, state, country, postal, phone, private, 
                       parish)
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Source
    # ---------------------------------
    for source_handle in database.source_map.keys():
        source = database.source_map[source_handle]
        (handle, gid, title,
         author, pubinfo,
         note_list,
         media_list,
         abbrev,
         change, datamap,
         reporef_list,
         marker, private) = source

        export_source(db, handle, gid, title, author, pubinfo, abbrev, change,
                      marker[0], marker[1], private)
        export_list(db, "source", handle, "note", note_list) 
        export_media_list(db, "source", handle, media_list)
        # FIXME: reporef_list, datamap
        #print "FIXME: reporef_list", reporef_list
        #print "FIXME: datamap", datamap
#FIXME: reporef_list []
#FIXME: datamap {}
#FIXME: reporef_list [([], u'b2cfa6e37654b308559', '', (2, u''), False)]
#FIXME: datamap {}
        
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Media
    # ---------------------------------
    for media_handle in database.media_map.keys():
        media = database.media_map[media_handle]
        (handle, gid, path, mime, desc,
         attribute_list,
         source_list,
         note_list,
         change,
         date,
         marker,
         private) = media

        db.query("""INSERT INTO media (
            handle, 
            gid, 
            path, 
            mime, 
            desc,
            change, 
            marker0, 
            marker1, 
            private) VALUES (?,?,?,?,?,?,?,?,?);""",
                 handle, gid, path, mime, desc, 
                 change, marker[0], marker[1], private)
        if date:
            export_date(db, "media", handle, date)
        export_list(db, "media", handle, "note", note_list) 
        export_source_list(db, "media", handle, source_list)
        export_attribute_list(db, "media", handle, attribute_list)
        count += 1
        callback(100 * count/total)

    return True

    # Bookmarks
    # Header - researcher info
    # Name formats
    # Namemaps?

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_name = _('SQLite Export')
_description = _('SQLite is a common local database format')
_config = (_('SQLite options'), ExportOptions.WriterOptionBox)

pmgr = PluginManager.get_instance()
plugin = ExportPlugin(name            = _name, 
                      description     = _description,
                      export_function = exportData,
                      extension       = "sql",
                      config          = _config )
pmgr.register_plugin(plugin)
