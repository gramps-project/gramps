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
from Utils import ProgressMeter
import ExportOptions

def makeDB(db):
    db.query("""drop table notes;""")
    db.query("""drop table people;""")
    db.query("""drop table events;""")
    db.query("""drop table family;""")
    db.query("""drop table repository;""")
    db.query("""drop table dates;""")
    db.query("""drop table places;""") 
    db.query("""drop table sources;""") 
    db.query("""drop table media;""")
    db.query("""drop table names;""")
    db.query("""drop table link;""")
    db.query("""drop table markup;""")
    db.query("""drop table event_ref;""")
    db.query("""drop table source_ref;""")
    db.query("""drop table lds;""")
    db.query("""drop table media_ref;""")
    db.query("""drop table address;""")
    db.query("""drop table attribute;""")

    db.query("""CREATE TABLE notes (
                  handle CHARACTER(25),
                  gid    CHARACTER(25),
                  text   TEXT,
                  format TEXT,
                  note_type1   INTEGER,
                  note_type2   TEXT,
                  change TEXT,
                  marker0 TEXT,
                  marker1 TEXT,
                  private BOOLEAN);""")

    db.query("""CREATE TABLE names (
                  private BOOLEAN, 
                  first_name TEXT, 
                  surname TEXT, 
                  suffix TEXT, 
                  title TEXT, 
                  name_type0 TEXT, 
                  name_type1 TEXT, 
                  prefix TEXT, 
                  patronymic TEXT, 
                  group_as TEXT, 
                  sort_as TEXT,
                  display_as TEXT, 
                  call TEXT);""")

    db.query("""CREATE TABLE dates (
                  type CHARACTER(10),
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

    db.query("""CREATE TABLE people (
                  handle CHARACTER(25), 
                  gid CHARACTER(25), 
                  gender CHAR(1), 
                  death_ref_index TEXT, 
                  birth_ref_index TEXT, 
                  change TEXT, 
                  marker0 TEXT, 
                  marker1 TEXT, 
                  private BOOLEAN);""")

    db.query("""CREATE TABLE family (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 father_handle CHARACTER(25), 
                 mother_handle CHARACTER(25), 
                 the_type0 TEXT, 
                 the_type1 TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE places (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 title TEXT, 
                 long FLOAT, 
                 lat FLOAT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE events (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 the_type0 TEXT, 
                 the_type1 TEXT, 
                 description TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE sources (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 title TEXT, 
                 author TEXT, 
                 pubinfo TEXT, 
                 abbrev TEXT, 
                 change TEXT,
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE media (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 path TEXT, 
                 mime TEXT, 
                 desc TEXT,
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE repository (
                 handle CHARACTER(25), 
                 gid CHARACTER(25), 
                 the_type0 TEXT, 
                 the_type1 TEXT,
                 name TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE link (
                 from_type CHARACTER(10), 
                 from_handle CHARACTER(25), 
                 to_type CHARACTER(10), 
                 to_handle CHARACTER(25));""")

    db.query("""CREATE TABLE markup (
                 handle CHARACTER(25), 
                 markup0 INTEGER, 
                 markup1 TEXT, 
                 value TEXT, 
                 start_stop_list TEXT);""")

    db.query("""CREATE TABLE event_ref (
                 handle CHARACTER(25), 
                 ref CHARACTER(25), 
                 role0 INTEGER, 
                 role1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE source_ref (
                 handle CHARACTER(25), 
                 ref CHARACTER(25), 
                 confidence INTEGER,
                 page CHARACTER(25),
                 private BOOLEAN);""")

    db.query("""CREATE TABLE lds (
                 handle CHARACTER(25), 
                 type CHARACTER(10), 
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
                 handle CHARACTER(25),
                 street TEXT, 
                 city TEXT, 
                 county TEXT, 
                 state TEXT, 
                 country TEXT, 
                 postal TEXT, 
                 phone TEXT,
                 private BOOLEAN);""")

    db.query("""CREATE TABLE attribute (
                 handle CHARACTER(25),
                 from_type CHARACTER(10),
                 from_handle CHARACTER(25),
                 the_type0 INTEGER, 
                 the_type1 TEXT, 
                 value TEXT, 
                 private BOOLEAN);""")

class Database:
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

def export_url_list(db, from_type, handle, urls):
    for url in urls:
        # (False, u'http://www.gramps-project.org/', u'loleach', (0, u'kaabgo'))
        print "FIX:", url

def export_person_ref_list(db, from_type, handle, person_ref_list):
    for person_ref in person_ref_list:
        # (False, [], ['b2c04e217fd4c3a6b35', 'b2c04e35b564b1b96b6'], 'b2c04e3741f13654287', u'chiduer')
        print "FIX:", person_ref

def export_event_ref(db, handle, ref, role, private):
    db.query("""insert INTO event_ref (
                 handle, 
                 ref, 
                 role0, 
                 role1, 
                 private) VALUES (?,?,?,?,?);""",
             handle, 
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

def export_lds(db, handle, type, place, famc, temple, status, private):
    db.query("""INSERT into lds (handle, type, place, famc, temple, status, private) 
             VALUES (?,?,?,?,?,?,?);""",
             handle, type, place, famc, temple, status, private)
    
def export_media_ref(db, handle, ref, role, private):
    db.query("""INSERT into media_ref (
                 handle,
                 ref,
                 role,
                 private) VALUES (?,?,?,?);""",
             handle, ref, str(role), private) # FIXME: role with two parts

def export_source_ref(db, handle, ref, private, confidence, page):
    db.query("""INSERT into source_ref (
             handle, 
             ref, 
             confidence,
             page,
             private
             ) VALUES (?,?,?,?,?);""",
             handle, 
             ref, 
             confidence,
             page,
             private)

def export_source(db, handle, gid, title, author, pubinfo, abbrev, change,
                   marker0, marker1, private):
    db.query("""INSERT into sources (
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
    db.query("""INSERT into notes (handle,
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

def export_name(db, handle, data):
    if data:
        (private, source_list, note_list, date,
         first_name, surname, suffix, title,
         name_type, prefix, patronymic,
         group_as, sort_as, display_as, call) = data

        db.query("""INSERT into names (
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
                    ) values (?, ?, ?, ?, ?, ?, 
                              ?, ?, ?, ?, ?, ?, ?);""",
                 private, first_name, surname, suffix, title,
                 name_type[0], name_type[1], prefix, patronymic, group_as, 
                 sort_as, display_as, call)

        export_date(db, "name", handle, date) 
        export_list(db, "names", handle, "notes", note_list)
        # Event Sources
        for source in source_list:
            (date, private, note_list, confidence, ref, page) = source
            export_source_ref(db, handle, ref, private, confidence, page)
            export_date(db, "source_ref", ref, date)
            export_list(db, "source_ref", ref, "note", note_list) 

def export_date(db, date_type, handle, data):
    if data:
        (calendar, modifier, quality, dateval, text, sortval, newyear) = data
        if len(dateval) == 4:
            day1, month1, year1, slash1 = dateval
            day2, month2, year2, slash2 = 0, 0, 0, 0
        elif len(dateval) == 8:
            day1, month1, year1, slash1, day2, month2, year2, slash2 = dateval
        else:
            raise ("ERROR:", dateval)
        db.query("""INSERT INTO dates (
                  type,
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
                  newyear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
                                   ?, ?, ?, ?, ?, ?, ?);""",
                 date_type, calendar, modifier, quality, 
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

def export_attribute_list(db, from_type, from_handle, attribute_list):
    for attribute in attribute_list:
        (private, source_list, note_list, the_type, value) = attribute
        attr_handle = "ATTRHANDLE" # FIXME
        export_attribute(db, from_type, from_handle, attr_handle, the_type, value, private)
        export_list(db, "attribute", attr_handle, "note", note_list)
        # Event Sources
        for source in source_list:
            (date, private, note_list, confidence, ref, page) = source
            export_source_ref(db, attr_handle, ref, private, confidence, page)
            export_date(db, "source_ref", ref, date)
            export_list(db, "source_ref", ref, "note", note_list) 


def export_list(db, from_type, from_handle, to_type, handle_list):
    for to_handle in handle_list:
        if type(to_handle) == type(""):
            export_link(db, from_type, from_handle, to_type, to_handle)
        else:
            print "FIX:", from_type, from_handle, "->", to_type, to_handle
            
def export_link(db, from_type, from_handle, to_type, to_handle):
    db.query("""insert into link (
                   from_type, 
                   from_handle, 
                   to_type, 
                   to_handle) values (?, ?, ?, ?)""",
             from_type, from_handle, to_type, to_handle)

def export_address(db, handle, street, city, county, state, country, postal, phone, private):
    db.query("""INSERT INTO address (
                 handle,
                 street, 
                 city, 
                 county, 
                 state, 
                 country, 
                 postal, 
                 phone,
                 private) VALUES (?,?,?,?,?,?,?,?,?);""",
             handle, street, city, county, state, country, postal, phone, private)


def exportData(database, filename, option_box=None, callback=None):
    if not callable(callback): 
        callback = lambda (percent): None # dummy

    total = (len(database.note_map) + 
             len(database.person_map) +
             len(database.event_map) + 
             len(database.family_map) +
             len(database.repository_map) +
             len(database.place_map) +
             len(database.source_map) +
             len(database.media_map))
    count = 0

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
        export_date(db, "event", event_handle, date)

        db.query("""INSERT INTO events (
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
            export_link(db, "event", handle, "place", place)
        export_list(db, "event", handle, "note", note_list)
        export_attribute_list(db, "event", handle, attribute_list)

        # Event Media list
        for media in media_list:
            (private, source_list, note_list,attribute_list,ref,role) = media
            export_media_ref(db, handle, ref, role, private)
            export_list(db, "media", ref, "note", note_list)
            export_attribute_list(db, "media", ref, attribute_list)

        # Event Sources
        for source in source_list:
            (date, private, note_list, confidence, ref, page) = source
            export_source_ref(db, handle, ref, private, confidence, page)
            export_date(db, "source_ref", ref, date)
            export_list(db, "source_ref", ref, "note", note_list) 

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

        db.query("""INSERT INTO people (
                  handle, 
                  gid, 
                  gender, 
                  death_ref_index, 
                  birth_ref_index, 
                  change, 
                  marker0, 
                  marker1, 
                  private) values (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                  handle, 
                  gid, 
                  gender, 
                  death_ref_index, 
                  birth_ref_index, 
                  change, 
                  marker[0], 
                  marker[1], 
                  private)

        export_list(db, "people", handle, "note", pnote_list)
        export_attribute_list(db, "people", handle, attribute_list)

        # Event Reference information
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            export_event_ref(db, handle, ref, role, private)

            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)
            
        export_list(db, "people", handle, "family", family_list) # handles
        export_list(db, "people", handle, "parent_family", parent_family_list) # handles
        export_list(db, "people", handle, "note", pnote_list) # handles
        export_url_list(db, "people", handle, urls) 
        export_person_ref_list(db, "people", handle, person_ref_list)

        for media in media_list:
            (private, source_list, note_list,attribute_list,ref,rect) = media
            export_media_ref(db, handle, ref, role, private)
            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)

        # -------------------------------------
        # Address
        # -------------------------------------
        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            (street, city, county, state, country, postal, phone) = location
            addr_handle = "ADDRHANDLE" # FIXME
            export_address(db, addr_handle, street, city, county, state, country, postal, phone, private)
            export_date(db, "address", addr_handle, date)
            export_list(db, "source_ref", addr_handle, "note", anote_list) 
            # Address Sources
            for source in asource_list:
                (date, private, note_list, confidence, ref, page) = source
                export_source_ref(db, addr_handle, ref, private, confidence, page)
                export_date(db, "source_ref", ref, date)
                export_list(db, "source_ref", ref, "note", note_list) 

        # -------------------------------------
        # LDS ord
        # -------------------------------------
        for ldsord in lds_ord_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            lds_handle = "LDSHANDLE" # FIXME: use db-generated handle?
            export_lds(db, lds_handle, type, place, famc, temple, status, lprivate)
            export_date(db, "lds", lds_handle, date)
            export_list(db, "lds", lds_handle, "note", lnote_list)
            for source in lsource_list:
                (date, private, note_list, confidence, ref, page) = source
                export_source_ref(db, lds_handle, ref, private, confidence, page)
                export_date(db, "source_ref", ref, date)
                export_list(db, "source_ref", ref, "note", note_list) 

        # -------------------------------------
        # Source
        # -------------------------------------
        for source in psource_list:
            (date, private, note_list, confidence, ref, page) = source
            export_source_ref(db, handle, ref, private, confidence, page)
            export_date(db, "source_ref", ref, date)
            export_list(db, "source_ref", ref, "note", note_list) 

        # -------------------------------------
        # Names
        # -------------------------------------
        export_name(db, handle, primary_name)
        map(lambda name: export_name(db, handle, name), alternate_names)
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
        #TODO: lists

        export_list(db, "family", handle, "note", pnote_list)
        export_attribute_list(db, "family", handle, attribute_list)

        # Event Reference information
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            export_event_ref(db, handle, ref, role, private)

            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)
            
        # -------------------------------------
        # LDS 
        # -------------------------------------
        for ldsord in lds_seal_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            lds_handle = "LDSHANDLE" # FIXME: use db-generated handle?
            export_lds(db, lds_handle, type, place, famc, temple, status, lprivate)
            export_date(db, "lds", lds_handle, date)
            export_list(db, "lds", lds_handle, "note", lnote_list)
            for source in lsource_list:
                (date, private, note_list, confidence, ref, page) = source
                export_source_ref(db, lds_handle, ref, private, confidence, page)
                export_date(db, "source_ref", ref, date)
                export_list(db, "source_ref", ref, "note", note_list) 

        # -------------------------------------
        # Source
        # -------------------------------------
        for source in source_list:
            (date, private, note_list, confidence, ref, page) = source
            export_source_ref(db, handle, ref, private, confidence, page)
            export_date(db, "source_ref", ref, date)
            export_list(db, "source_ref", ref, "note", note_list) 

        for media in media_list:
            (private, source_list, note_list,attribute_list,ref,rect) = media
            export_media_ref(db, handle, ref, role, private)
            export_list(db, "event_ref", ref, "note", note_list)
            export_attribute_list(db, "event_ref", ref, attribute_list)

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

        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            (street, city, county, state, country, postal, phone) = location
            addr_handle = "ADDRHANDLE" # FIXME
            export_address(db, addr_handle, street, city, county, state, country, postal, phone, private)
            export_date(db, "address", addr_handle, date)
            export_list(db, "address", addr_handle, "note", anote_list) 
            # Source
            for source in asource_list:
                (date, private, note_list, confidence, ref, page) = source
                export_source_ref(db, addr_handle, ref, private, confidence, page)
                export_date(db, "source_ref", ref, date)
                export_list(db, "source_ref", ref, "note", note_list) 

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Place
    # ---------------------------------
    for place_handle in database.place_map.keys():
        repository = database.place_map[place_handle]
        (handle, gid, title, long, lat,
         main_loc, alt_location_list,
         urls,
         medias,
         sources,
         notes,
         change, marker, private) = repository

        db.query("""INSERT INTO places (
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

        # TODO: alt_location_list, urls, medias, sources, notes
        # main_loc
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Source
    # ---------------------------------
    for source_handle in database.source_map.keys():
        source = database.source_map[source_handle]
        (handle, gid, title,
         author, pubinfo,
         notes,
         media_list,
         abbrev,
         change, datamap,
         reporef_list,
         marker, private) = source
        export_source(db, handle, gid, title, author, pubinfo, abbrev, change,
                      marker[0], marker[1], private)
        export_list(db, "source", handle, "note", note_list) 
        
        # TODO: notes, media_list
        # reporef_list, data_map
        
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Media
    # ---------------------------------
    for media_handle in database.media_map.keys():
        media = database.media_map[media_handle]
        (handle, gid, path, mime, desc,
         attrib_list,
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

        export_date(db, "media", handle, date)
        export_list(db, "media", handle, "note", note_list) 
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
