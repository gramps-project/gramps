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

def export_source(db, handle, gramps_id, title, author, pubinfo, abbrev, change,
                   marker0, marker1, private):
    db.query("""INSERT into sources (
             handle, 
             gramps_id, 
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
             gramps_id, 
             title, 
             author, 
             pubinfo, 
             abbrev, 
             change,
             marker0, 
             marker1, 
             private)

def export_note(db, handle, gramps_id, text, format, note_type0,
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
             handle, gramps_id, text, format, note_type0,
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
        export_date(db, handle, date) 
        for source_handle in source_list:
            print "   source handle:", source_handle
        for note_handle in note_list:
            print "   note handle:", note_handle

def export_date(db, handle, data):
    if data:
        (calendar, modifier, quality, dateval, text, sortval, newyear) = data
        if len(dateval) == 4:
            day1, month1, year1, flag1 = dateval
            day2, month2, year2, flag2 = 0, 0, 0, 0
        elif len(dateval) == 8:
            day1, month1, year1, flag1, day2, month2, year2, flag2 = dateval
        else:
            raise ("ERROR:", dateval)
        db.query("""INSERT INTO dates (
                  calendar, 
                  modifier, 
                  quality,
                  day1, 
                  month1, 
                  year1, 
                  flag1,
                  day2, 
                  month2, 
                  year2, 
                  flag2,
                  text, 
                  sortval, 
                  newyear) VALUES (?, ?, ?, ?, ?, ?, ?, 
                                   ?, ?, ?, ?, ?, ?, ?);""",
                 calendar, modifier, quality, 
                 day1, month1, year1, flag1, 
                 day2, month2, year2, flag2,
                 text, sortval, newyear)

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

    db.query("""CREATE TABLE notes (
                  handle TEXT,
                  gid    TEXT,
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
                  calendar TEXT, 
                  modifier TEXT, 
                  quality TEXT,
                  day1 INTEGER, 
                  month1 INTEGER, 
                  year1 INTEGER, 
                  flag1 BOOLEAN,
                  day2 INTEGER, 
                  month2 INTEGER, 
                  year2 INTEGER, 
                  flag2 BOOLEAN,
                  text TEXT, 
                  sortval LONG, 
                  newyear INTEGER);""")

    db.query("""CREATE TABLE people (
                  handle TEXT, 
                  gramps_id TEXT, 
                  gender CHAR(1), 
                  death_ref_index TEXT, 
                  birth_ref_index TEXT, 
                  change TEXT, 
                  marker0 TEXT, 
                  marker1 TEXT, 
                  private BOOLEAN);""")

    db.query("""CREATE TABLE family (
                 handle TEXT, 
                 gramps_id TEXT, 
                 father_handle TEXT, 
                 mother_handle TEXT,
                 the_type0 TEXT, 
                 the_type1 TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE places (
                 handle TEXT, 
                 gramps_id TEXT, 
                 title TEXT, 
                 long FLOAT, 
                 lat FLOAT, 
                 main_loc TEXT,
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE events (
                 handle TEXT, 
                 gramps_id TEXT, 
                 the_type0 TEXT, 
                 the_type1 TEXT, 
                 description TEXT, 
                 place TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE sources (
                 handle TEXT, 
                 gramps_id TEXT, 
                 title TEXT, 
                 author TEXT, 
                 pubinfo TEXT, 
                 abbrev TEXT, 
                 change TEXT,
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE media (
                 handle TEXT, 
                 gramps_id TEXT, 
                 path TEXT, 
                 mime TEXT, 
                 desc TEXT,
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    db.query("""CREATE TABLE repository (
                 handle TEXT, 
                 gramps_id TEXT, 
                 the_type0 TEXT, 
                 the_type1 TEXT,
                 name TEXT, 
                 change TEXT, 
                 marker0 TEXT, 
                 marker1 TEXT, 
                 private BOOLEAN);""")

    # ---------------------------------
    # Notes
    # ---------------------------------

    for note_handle in database.note_map.keys():
        note = database.note_map[note_handle]
        (handle, gramps_id, styled_text, format, note_type,
         change, marker, private) = note
        text, text_list = styled_text
        export_note(db, handle, gramps_id, text, format, note_type[0],
                    note_type[1], change, marker[0], marker[1], private)
        #TODO: text_list
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Event
    # ---------------------------------
    # update dates with newyear
    for event_handle in database.event_map.keys():
        event = database.event_map[event_handle]
        (handle, gramps_id, the_type, date, description, place, 
         source_list, note_list, media_list, attribute_list,
         change, marker, private) = event
        export_date(db, event_handle, date)

        db.query("""INSERT INTO events (
                 handle, 
                 gramps_id, 
                 the_type0, 
                 the_type1, 
                 description, 
                 place, 
                 change, 
                 marker0, 
                 marker1, 
                 private) VALUES (?,?,?,?,?,?,?,?,?,?);""",
                 handle, 
                 gramps_id, 
                 the_type[0], 
                 the_type[1], 
                 description, 
                 place, 
                 change, 
                 marker[0], 
                 marker[1], 
                 private)

        # TODO: lists
        # source_list, note_list, media_list, attribute_list
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Person
    # ---------------------------------
    for person_handle in database.person_map.keys():
        person = database.person_map[person_handle]
        (handle,        #  0
         gramps_id,          #  1
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
                  gramps_id, 
                  gender, 
                  death_ref_index, 
                  birth_ref_index, 
                  change, 
                  marker0, 
                  marker1, 
                  private) values (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                  handle, 
                  gramps_id, 
                  gender, 
                  death_ref_index, 
                  birth_ref_index, 
                  change, 
                  marker[0], 
                  marker[1], 
                  private)

        # TODO: event_ref_list, 
        #family_list, 
        #parent_family_list,
        #media_list,       
        #address_list,      
        #attribute_list,   
        #urls,             
        #lds_ord_list,     
        #psource_list,     
        #pnote_list,       
        #person_ref_list,   

        # -------------------------------------
        # Address
        # -------------------------------------
        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            (street, city, county, state, country, postal, phone) = location
            print "address:", private, street, city, county, state, \
                country, postal, phone
            export_date(db, handle, date)
            # TODO: asource_list, anote_list

        # -------------------------------------
        # LDS ord
        # -------------------------------------
        for ldsord in lds_ord_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            print "ldsord:", type, place, famc, temple, status, lprivate
            export_date(db, handle, date)

            #TODO: lists

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
        (handle, gramps_id, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, source_list, note_list,
         change, marker, private) = family
        # father_handle and/or mother_handle can be None
        db.query("""INSERT INTO family (
                 handle, 
                 gramps_id, 
                 father_handle, 
                 mother_handle,
                 the_type0, 
                 the_type1, 
                 change, 
                 marker0, 
                 marker1, 
                 private) values (?,?,?,?,?,?,?,?,?,?);""",
                 handle, gramps_id, father_handle, mother_handle,
                 the_type[0], the_type[1], change, marker[0], marker[1], 
                 private)
        #TODO: lists

        for ldsord in lds_seal_list:
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            print "ldsord:", type, place, famc, temple, status, lprivate
            export_date(db, handle, date)

            #TODO: lists
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Repository
    # ---------------------------------

    for repository_handle in database.repository_map.keys():
        repository = database.repository_map[repository_handle]
        # address
        (handle, gramps_id, the_type, name, note_list,
         address_list, urls, change, marker, private) = repository

        db.query("""INSERT INTO repository (
                 handle, 
                 gramps_id, 
                 the_type0, 
                 the_type1,
                 name, 
                 change, 
                 marker0, 
                 marker1, 
                 private) VALUES (?,?,?,?,?,?,?,?,?);""",
                 handle, gramps_id, the_type[0], the_type[1],
                 name, change, marker[0], marker[1], private)

        print "repository:", handle, gramps_id, the_type[0], the_type[1], \
            name, change, marker[0], marker[1], private
        #TODO: lists

        for address in address_list:
            (private, asource_list, anote_list, date, location) = address
            print "address:", private, location
            export_date(db, handle, date)
            #TODO: lists

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Place
    # ---------------------------------

    for place_handle in database.place_map.keys():
        repository = database.place_map[place_handle]
        (handle, gramps_id, title, long, lat,
         main_loc, alt_location_list,
         urls,
         medias,
         sources,
         notes,
         change, marker, private) = repository

        db.query("""INSERT INTO places (
                 handle, 
                 gramps_id, 
                 title, 
                 long, 
                 lat, 
                 main_loc,
                 change, 
                 marker0, 
                 marker1, 
                 private) values (?,?,?,?,?,?,?,?,?,?);""",
                 handle, gramps_id, title, long, lat, main_loc,
                 change, marker[0], marker[1], private)

        # TODO: alt_location_list, urls, medias, sources, notes
        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Source
    # ---------------------------------

    for source_handle in database.source_map.keys():
        source = database.source_map[source_handle]
        (handle, gramps_id, title,
         author, pubinfo,
         notes,
         media_list,
         abbrev,
         change, datamap,
         reporef_list,
         marker, private) = source
        export_source(db, handle, gramps_id, title, author, pubinfo, abbrev, change,
                   marker[0], marker[1], private)
        for note in notes:
            export_note(db, handle, note)
         # TODO: notes, media_list
         # reporef_list, data_map

        count += 1
        callback(100 * count/total)

    # ---------------------------------
    # Media
    # ---------------------------------

    for media_handle in database.media_map.keys():
        media = database.media_map[media_handle]
        (handle, gramps_id, path, mime, desc,
         attrib_list,
         source_list,
         note_list,
         change,
         date,
         marker,
         private) = media

        db.query("""INSERT INTO media (
            handle, 
            gramps_id, 
            path, 
            mime, 
            desc,
            change, 
            marker0, 
            marker1, 
            private) VALUES (?,?,?,?,?,?,?,?,?);""",
                 handle, gramps_id, path, mime, desc, 
                 change, marker[0], marker[1], private)

        export_date(db, handle, date)
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
