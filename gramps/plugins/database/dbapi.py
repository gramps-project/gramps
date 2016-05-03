#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015 Douglas S. Blank <doug.blank@gmail.com>
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

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.db.generic import *
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import dbapi_support

import time
import pickle
from operator import itemgetter

import logging
LOG = logging.getLogger(".dbapi")

class DBAPI(DbGeneric):
    """
    Database backends class for DB-API 2.0 databases
    """
    @classmethod
    def get_class_summary(cls):
        summary = {
            "DB-API version": "2.0",
            "Database type": cls.__name__,
        }
        return summary

    def restore(self):
        """
        If you wish to support an optional restore routine, put it here.
        """
        pass

    def write_version(self, directory):
        """Write files for a newly created DB."""
        versionpath = os.path.join(directory, str(DBBACKEND))
        LOG.debug("Write database backend file to 'dbapi'")
        with open(versionpath, "w") as version_file:
            version_file.write("dbapi")
        versionpath = os.path.join(directory, "bdbversion.txt")
        with open(versionpath, "w") as version_file:
            version_file.write(str(self.VERSION))
        # Write default_settings, sqlite.db
        defaults = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "dbapi_support", "defaults")
        LOG.debug("Copy defaults from: " + defaults)
        for filename in os.listdir(defaults):
            if filename in ["__init__.py"]: # skip these
                continue
            fullpath = os.path.abspath(os.path.join(defaults, filename))
            if os.path.isfile(fullpath):
                shutil.copy2(fullpath, directory)

    def initialize_backend(self, directory):
        # Run code from directory
        default_settings = {"__file__":
                            os.path.join(directory, "default_settings.py"),
                            "dbapi_support": dbapi_support}
        settings_file = os.path.join(directory, "default_settings.py")
        with open(settings_file) as f:
            code = compile(f.read(), settings_file, 'exec')
            exec(code, globals(), default_settings)

        self.dbapi = default_settings["dbapi"]
        self.update_schema()

    def update_schema(self):
        """
        Create and update schema.
        """
        # make sure schema is up to date:
        self.dbapi.try_execute("""CREATE TABLE person (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    given_name     TEXT        ,
                                    surname        TEXT        ,
                                    gender_type    INTEGER     ,
                                    order_by  TEXT             ,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE family (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    father_handle VARCHAR(50),
                                    mother_handle VARCHAR(50),
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE source (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    order_by  TEXT             ,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE citation (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    order_by  TEXT             ,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE event (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE media (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    order_by  TEXT             ,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE place (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    order_by  TEXT             ,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE repository (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE note (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    gramps_id TEXT             ,
                                    blob_data      BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE tag (
                                    handle    VARCHAR(50) PRIMARY KEY NOT NULL,
                                    order_by  TEXT             ,
                                    blob_data      BLOB
        );""")
        # Secondary:
        self.dbapi.try_execute("""CREATE TABLE reference (
                                    obj_handle    VARCHAR(50),
                                    obj_class     TEXT,
                                    ref_handle    VARCHAR(50),
                                    ref_class     TEXT
        );""")
        self.dbapi.try_execute("""CREATE TABLE name_group (
                                    name     VARCHAR(50) PRIMARY KEY NOT NULL,
                                    grouping TEXT
        );""")
        self.dbapi.try_execute("""CREATE TABLE metadata (
                                    setting  VARCHAR(50) PRIMARY KEY NOT NULL,
                                    value    BLOB
        );""")
        self.dbapi.try_execute("""CREATE TABLE gender_stats (
                                    given_name TEXT,
                                    female     INTEGER,
                                    male       INTEGER,
                                    unknown    INTEGER
        );""")
        ## Indices:
        self.dbapi.try_execute("""CREATE INDEX
                                  person_order_by ON person(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  person_gramps_id ON person(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  person_surname ON person(surname);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  person_given_name ON person(given_name);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  source_order_by ON source(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  source_gramps_id ON source(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  citation_order_by ON citation(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  citation_gramps_id ON citation(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  media_order_by ON media(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  media_gramps_id ON media(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  place_order_by ON place(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  place_gramps_id ON place(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  tag_order_by ON tag(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  reference_ref_handle ON reference(ref_handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  name_group_name ON name_group(name);
        """)

        # Fixes:
        self.dbapi.try_execute("""CREATE INDEX
                                  place_handle ON place(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  citation_handle ON citation(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  media_handle ON media(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  person_handle ON person(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  family_handle ON family(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  event_handle ON event(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  repository_handle ON repository(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  tag_handle ON tag(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  note_handle ON note(handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  source_handle ON source(handle);
        """)

        self.dbapi.try_execute("""CREATE INDEX
                                  place_order_by ON place(order_by);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  tag_order_by ON tag(order_by);
        """)

        self.dbapi.try_execute("""CREATE INDEX
                                  family_gramps_id ON family(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  event_gramps_id ON event(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  repository_gramps_id ON repository(gramps_id);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  note_gramps_id ON note(gramps_id);
        """)

        self.dbapi.try_execute("""CREATE INDEX
                                  reference_obj_handle ON reference(obj_handle);
        """)
        self.dbapi.try_execute("""CREATE INDEX
                                  person_surname ON person(surname);
        """)
        self.rebuild_secondary_fields()

    def close_backend(self):
        self.dbapi.close()

    def transaction_begin(self, transaction):
        """
        Transactions are handled automatically by the db layer.
        """
        self.transaction = transaction
        self.dbapi.begin()
        return transaction

    def transaction_commit(self, txn):
        """
        Executed after a batch operation.
        """
        self.dbapi.commit()
        self.transaction = None
        msg = txn.get_description()
        self.undodb.commit(txn, msg)
        self._after_commit(txn)
        txn.clear()
        self.has_changed = True

    def transaction_abort(self, txn):
        """
        Executed after a batch operation abort.
        """
        self.dbapi.rollback()
        self.transaction = None
        txn.clear()
        txn.first = None
        txn.last = None
        self._after_commit(txn)

    def get_metadata(self, key, default=[]):
        """
        Get an item from the database.
        """
        self.dbapi.execute("SELECT value FROM metadata WHERE setting = ?;", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])
        elif default == []:
            return []
        else:
            return default

    def set_metadata(self, key, value):
        """
        key: string
        value: item, will be serialized here
        """
        self.dbapi.execute("SELECT 1 FROM metadata WHERE setting = ?;", [key])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute("UPDATE metadata SET value = ? WHERE setting = ?;",
                               [pickle.dumps(value), key])
        else:
            self.dbapi.execute("INSERT INTO metadata (setting, value) VALUES (?, ?);",
                               [key, pickle.dumps(value)])

    def get_name_group_keys(self):
        self.dbapi.execute("SELECT name FROM name_group ORDER BY name;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_name_group_mapping(self, key):
        self.dbapi.execute("SELECT grouping FROM name_group WHERE name = ?;",
                                 [key])
        row = self.dbapi.fetchone()
        if row:
            return row[0]
        else:
            return key

    def get_person_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        If sort_handles is True, the list is sorted by surnames.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM person ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle FROM person;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_family_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        If sort_handles is True, the list is sorted by surnames.
        """
        if sort_handles:
            self.dbapi.execute("""SELECT f.handle FROM
                                   (SELECT family.*
                                     FROM family LEFT JOIN
                                     person AS father
                                     ON family.father_handle = father.handle LEFT JOIN
                                     person AS mother
                                     on family.mother_handle = mother.handle
                                     order by (case when father.handle is null
                                                    then mother.primary_name__surname_list__0__surname
                                                    else father.primary_name__surname_list__0__surname
                                               end),
                                              (case when family.handle is null
                                                    then mother.primary_name__first_name
                                                    else father.primary_name__first_name
                                               end)) AS f;""")
        else:
            self.dbapi.execute("SELECT handle FROM family;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_event_handles(self):
        self.dbapi.execute("SELECT handle FROM event;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_citation_handles(self, sort_handles=False):
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM citation ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle FROM citation;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_source_handles(self, sort_handles=False):
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM source ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle from source;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_place_handles(self, sort_handles=False):
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM place ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle FROM place;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_repository_handles(self):
        self.dbapi.execute("SELECT handle FROM repository;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_media_handles(self, sort_handles=False):
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM media ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle FROM media;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_note_handles(self):
        self.dbapi.execute("SELECT handle FROM note;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_tag_handles(self, sort_handles=False):
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM tag ORDER BY order_by;")
        else:
            self.dbapi.execute("SELECT handle FROM tag;")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_tag_from_name(self, name):
        self.dbapi.execute("""select handle from tag where order_by = ?;""",
                                 [self._order_by_tag_key(name)])
        row = self.dbapi.fetchone()
        if row:
            return self.get_tag_from_handle(row[0])
        return None

    def get_number_of_people(self):
        self.dbapi.execute("SELECT count(1) FROM person;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_events(self):
        self.dbapi.execute("SELECT count(1) FROM event;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_places(self):
        self.dbapi.execute("SELECT count(1) FROM place;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_tags(self):
        self.dbapi.execute("SELECT count(1) FROM tag;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_families(self):
        self.dbapi.execute("SELECT count(1) FROM family;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_notes(self):
        self.dbapi.execute("SELECT count(1) FROM note;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_citations(self):
        self.dbapi.execute("SELECT count(1) FROM citation;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_sources(self):
        self.dbapi.execute("SELECT count(1) FROM source;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_media(self):
        self.dbapi.execute("SELECT count(1) FROM media;")
        row = self.dbapi.fetchone()
        return row[0]

    def get_number_of_repositories(self):
        self.dbapi.execute("SELECT count(1) FROM repository;")
        row = self.dbapi.fetchone()
        return row[0]

    def has_name_group_key(self, key):
        self.dbapi.execute("SELECT grouping FROM name_group WHERE name = ?;",
                                 [key])
        row = self.dbapi.fetchone()
        return True if row else False

    def set_name_group_mapping(self, name, grouping):
        self.dbapi.execute("SELECT 1 FROM name_group WHERE name = ?;",
                                 [name])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute("DELETE FROM name_group WHERE name = ?;",
                                     [name])
        self.dbapi.execute("INSERT INTO name_group (name, grouping) VALUES(?, ?);",
                                 [name, grouping])

    def commit_person(self, person, trans, change_time=None):
        emit = None
        old_person = None
        if person.handle in self.person_map:
            emit = "person-update"
            old_person = self.get_person_from_handle(person.handle)
            # Update gender statistics if necessary
            if (old_person.gender != person.gender or
                old_person.primary_name.first_name !=
                  person.primary_name.first_name):

                self.genderStats.uncount_person(old_person)
                self.genderStats.count_person(person)
            # Update surname list if necessary
            if (self._order_by_person_key(person) !=
                self._order_by_person_key(old_person)):
                self.remove_from_surname_list(old_person)
                self.add_to_surname_list(person, trans.batch)
            given_name, surname, gender_type = self.get_person_data(person)
            # update the person:
            self.dbapi.execute("""UPDATE person SET gramps_id = ?,
                                                    order_by = ?,
                                                    blob_data = ?,
                                                    given_name = ?,
                                                    surname = ?,
                                                    gender_type = ?
                                                WHERE handle = ?;""",
                               [person.gramps_id,
                                self._order_by_person_key(person),
                                pickle.dumps(person.serialize()),
                                given_name,
                                surname,
                                gender_type,
                                person.handle])
        else:
            emit = "person-add"
            self.genderStats.count_person(person)
            self.add_to_surname_list(person, trans.batch)
            given_name, surname, gender_type = self.get_person_data(person)
            # Insert the person:
            self.dbapi.execute("""INSERT INTO person (handle, order_by, gramps_id, blob_data,
                                                      given_name, surname, gender_type)
                            VALUES(?, ?, ?, ?, ?, ?, ?);""",
                               [person.handle,
                                self._order_by_person_key(person),
                                person.gramps_id,
                                pickle.dumps(person.serialize()),
                                given_name, surname, gender_type])
        self.update_secondary_values(person)
        if not trans.batch:
            self.update_backlinks(person)
            if old_person:
                trans.add(PERSON_KEY, TXNUPD, person.handle,
                          old_person.serialize(),
                          person.serialize())
            else:
                trans.add(PERSON_KEY, TXNADD, person.handle,
                          None,
                          person.serialize())
        # Other misc update tasks:
        self.individual_attributes.update(
            [str(attr.type) for attr in person.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        self.event_role_names.update([str(eref.role)
                                      for eref in person.event_ref_list
                                      if eref.role.is_custom()])

        self.name_types.update([str(name.type)
                                for name in ([person.primary_name]
                                             + person.alternate_names)
                                if name.type.is_custom()])
        all_surn = []  # new list we will use for storage
        all_surn += person.primary_name.get_surname_list()
        for asurname in person.alternate_names:
            all_surn += asurname.get_surname_list()
        self.origin_types.update([str(surn.origintype) for surn in all_surn
                                if surn.origintype.is_custom()])
        all_surn = None
        self.url_types.update([str(url.type) for url in person.urls
                               if url.type.is_custom()])
        attr_list = []
        for mref in person.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([person.handle],))
        self.has_changed = True

    def commit_family(self, family, trans, change_time=None):
        emit = None
        old_family = None
        if family.handle in self.family_map:
            emit = "family-update"
            old_family = self.get_family_from_handle(family.handle).serialize()
            self.dbapi.execute("""UPDATE family SET gramps_id = ?,
                                                    father_handle = ?,
                                                    mother_handle = ?,
                                                    blob_data = ?
                                                WHERE handle = ?;""",
                               [family.gramps_id,
                                family.father_handle,
                                family.mother_handle,
                                pickle.dumps(family.serialize()),
                                family.handle])
        else:
            emit = "family-add"
            self.dbapi.execute("""INSERT INTO family (handle, gramps_id, father_handle, mother_handle, blob_data)
                    VALUES(?, ?, ?, ?, ?);""",
                               [family.handle,
                                family.gramps_id,
                                family.father_handle,
                                family.mother_handle,
                                pickle.dumps(family.serialize())])
        self.update_secondary_values(family)
        if not trans.batch:
            self.update_backlinks(family)
            op = TXNUPD if old_family else TXNADD
            trans.add(FAMILY_KEY, op, family.handle,
                      old_family,
                      family.serialize())

        # Misc updates:
        self.family_attributes.update(
            [str(attr.type) for attr in family.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        rel_list = []
        for ref in family.child_ref_list:
            if ref.frel.is_custom():
                rel_list.append(str(ref.frel))
            if ref.mrel.is_custom():
                rel_list.append(str(ref.mrel))
        self.child_ref_types.update(rel_list)

        self.event_role_names.update(
            [str(eref.role) for eref in family.event_ref_list
             if eref.role.is_custom()])

        if family.type.is_custom():
            self.family_rel_types.add(str(family.type))

        attr_list = []
        for mref in family.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([family.handle],))
        self.has_changed = True

    def commit_citation(self, citation, trans, change_time=None):
        emit = None
        old_citation = None
        if citation.handle in self.citation_map:
            emit = "citation-update"
            old_citation = self.get_citation_from_handle(citation.handle).serialize()
            self.dbapi.execute("""UPDATE citation SET gramps_id = ?,
                                                      order_by = ?,
                                                      blob_data = ?
                                                WHERE handle = ?;""",
                               [citation.gramps_id,
                                self._order_by_citation_key(citation),
                                pickle.dumps(citation.serialize()),
                                citation.handle])
        else:
            emit = "citation-add"
            self.dbapi.execute("""INSERT INTO citation (handle, order_by, gramps_id, blob_data)
                     VALUES(?, ?, ?, ?);""",
                       [citation.handle,
                        self._order_by_citation_key(citation),
                        citation.gramps_id,
                        pickle.dumps(citation.serialize())])
        self.update_secondary_values(citation)
        if not trans.batch:
            self.update_backlinks(citation)
            op = TXNUPD if old_citation else TXNADD
            trans.add(CITATION_KEY, op, citation.handle,
                      old_citation,
                      citation.serialize())
        # Misc updates:
        attr_list = []
        for mref in citation.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

        self.source_attributes.update(
            [str(attr.type) for attr in citation.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        # Emit after added:
        if emit:
            self.emit(emit, ([citation.handle],))
        self.has_changed = True

    def commit_source(self, source, trans, change_time=None):
        emit = None
        old_source = None
        if source.handle in self.source_map:
            emit = "source-update"
            old_source = self.get_source_from_handle(source.handle).serialize()
            self.dbapi.execute("""UPDATE source SET gramps_id = ?,
                                                    order_by = ?,
                                                    blob_data = ?
                                                WHERE handle = ?;""",
                               [source.gramps_id,
                                self._order_by_source_key(source),
                                pickle.dumps(source.serialize()),
                                source.handle])
        else:
            emit = "source-add"
            self.dbapi.execute("""INSERT INTO source (handle, order_by, gramps_id, blob_data)
                    VALUES(?, ?, ?, ?);""",
                       [source.handle,
                        self._order_by_source_key(source),
                        source.gramps_id,
                        pickle.dumps(source.serialize())])
        self.update_secondary_values(source)
        if not trans.batch:
            self.update_backlinks(source)
            op = TXNUPD if old_source else TXNADD
            trans.add(SOURCE_KEY, op, source.handle,
                      old_source,
                      source.serialize())
        # Misc updates:
        self.source_media_types.update(
            [str(ref.media_type) for ref in source.reporef_list
             if ref.media_type.is_custom()])

        attr_list = []
        for mref in source.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        self.source_attributes.update(
            [str(attr.type) for attr in source.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        # Emit after added:
        if emit:
            self.emit(emit, ([source.handle],))
        self.has_changed = True

    def commit_repository(self, repository, trans, change_time=None):
        emit = None
        old_repository = None
        if repository.handle in self.repository_map:
            emit = "repository-update"
            old_repository = self.get_repository_from_handle(repository.handle).serialize()
            self.dbapi.execute("""UPDATE repository SET gramps_id = ?,
                                                    blob_data = ?
                                                WHERE handle = ?;""",
                               [repository.gramps_id,
                                pickle.dumps(repository.serialize()),
                                repository.handle])
        else:
            emit = "repository-add"
            self.dbapi.execute("""INSERT INTO repository (handle, gramps_id, blob_data)
                     VALUES(?, ?, ?);""",
                       [repository.handle, repository.gramps_id, pickle.dumps(repository.serialize())])
        self.update_secondary_values(repository)
        if not trans.batch:
            self.update_backlinks(repository)
            op = TXNUPD if old_repository else TXNADD
            trans.add(REPOSITORY_KEY, op, repository.handle,
                      old_repository,
                      repository.serialize())
        # Misc updates:
        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update([str(url.type) for url in repository.urls
                               if url.type.is_custom()])
        # Emit after added:
        if emit:
            self.emit(emit, ([repository.handle],))
        self.has_changed = True

    def commit_note(self, note, trans, change_time=None):
        emit = None
        old_note = None
        if note.handle in self.note_map:
            emit = "note-update"
            old_note = self.get_note_from_handle(note.handle).serialize()
            self.dbapi.execute("""UPDATE note SET gramps_id = ?,
                                                    blob_data = ?
                                                WHERE handle = ?;""",
                               [note.gramps_id,
                                pickle.dumps(note.serialize()),
                                note.handle])
        else:
            emit = "note-add"
            self.dbapi.execute("""INSERT INTO note (handle, gramps_id, blob_data)
                     VALUES(?, ?, ?);""",
                       [note.handle, note.gramps_id, pickle.dumps(note.serialize())])
        self.update_secondary_values(note)
        if not trans.batch:
            self.update_backlinks(note)
            op = TXNUPD if old_note else TXNADD
            trans.add(NOTE_KEY, op, note.handle,
                      old_note,
                      note.serialize())
        # Misc updates:
        if note.type.is_custom():
            self.note_types.add(str(note.type))
        # Emit after added:
        if emit:
            self.emit(emit, ([note.handle],))
        self.has_changed = True

    def commit_place(self, place, trans, change_time=None):
        emit = None
        old_place = None
        if place.handle in self.place_map:
            emit = "place-update"
            old_place = self.get_place_from_handle(place.handle).serialize()
            self.dbapi.execute("""UPDATE place SET gramps_id = ?,
                                                   order_by = ?,
                                                   blob_data = ?
                                                WHERE handle = ?;""",
                               [place.gramps_id,
                                self._order_by_place_key(place),
                                pickle.dumps(place.serialize()),
                                place.handle])
        else:
            emit = "place-add"
            self.dbapi.execute("""INSERT INTO place (handle, order_by, gramps_id, blob_data)
                    VALUES(?, ?, ?, ?);""",
                       [place.handle,
                        self._order_by_place_key(place),
                        place.gramps_id,
                        pickle.dumps(place.serialize())])
        self.update_secondary_values(place)
        if not trans.batch:
            self.update_backlinks(place)
            op = TXNUPD if old_place else TXNADD
            trans.add(PLACE_KEY, op, place.handle,
                      old_place,
                      place.serialize())
        # Misc updates:
        if place.get_type().is_custom():
            self.place_types.add(str(place.get_type()))

        self.url_types.update([str(url.type) for url in place.urls
                               if url.type.is_custom()])

        attr_list = []
        for mref in place.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([place.handle],))
        self.has_changed = True

    def commit_event(self, event, trans, change_time=None):
        emit = None
        old_event = None
        if event.handle in self.event_map:
            emit = "event-update"
            old_event = self.get_event_from_handle(event.handle).serialize()
            self.dbapi.execute("""UPDATE event SET gramps_id = ?,
                                                    blob_data = ?
                                                WHERE handle = ?;""",
                               [event.gramps_id,
                                pickle.dumps(event.serialize()),
                                event.handle])
        else:
            emit = "event-add"
            self.dbapi.execute("""INSERT INTO event (handle, gramps_id, blob_data)
                  VALUES(?, ?, ?);""",
                       [event.handle,
                        event.gramps_id,
                        pickle.dumps(event.serialize())])
        self.update_secondary_values(event)
        if not trans.batch:
            self.update_backlinks(event)
            op = TXNUPD if old_event else TXNADD
            trans.add(EVENT_KEY, op, event.handle,
                      old_event,
                      event.serialize())
        # Misc updates:
        self.event_attributes.update(
            [str(attr.type) for attr in event.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        if event.type.is_custom():
            self.event_names.add(str(event.type))
        attr_list = []
        for mref in event.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([event.handle],))
        self.has_changed = True

    def commit_tag(self, tag, trans, change_time=None):
        emit = None
        if tag.handle in self.tag_map:
            emit = "tag-update"
            self.dbapi.execute("""UPDATE tag SET blob_data = ?,
                                                 order_by = ?
                                         WHERE handle = ?;""",
                               [pickle.dumps(tag.serialize()),
                                self._order_by_tag_key(tag.name),
                                tag.handle])
        else:
            emit = "tag-add"
            self.dbapi.execute("""INSERT INTO tag (handle, order_by, blob_data)
                  VALUES(?, ?, ?);""",
                       [tag.handle,
                        self._order_by_tag_key(tag.name),
                        pickle.dumps(tag.serialize())])
        if not trans.batch:
            self.update_backlinks(tag)
        # Emit after added:
        if emit:
            self.emit(emit, ([tag.handle],))
        self.has_changed = True

    def commit_media(self, media, trans, change_time=None):
        emit = None
        old_media = None
        if media.handle in self.media_map:
            emit = "media-update"
            old_media = self.get_media_from_handle(media.handle).serialize()
            self.dbapi.execute("""UPDATE media SET gramps_id = ?,
                                                   order_by = ?,
                                                   blob_data = ?
                                                WHERE handle = ?;""",
                               [media.gramps_id,
                                self._order_by_media_key(media),
                                pickle.dumps(media.serialize()),
                                media.handle])
        else:
            emit = "media-add"
            self.dbapi.execute("""INSERT INTO media (handle, order_by, gramps_id, blob_data)
                  VALUES(?, ?, ?, ?);""",
                       [media.handle,
                        self._order_by_media_key(media),
                        media.gramps_id,
                        pickle.dumps(media.serialize())])
        self.update_secondary_values(media)
        if not trans.batch:
            self.update_backlinks(media)
            op = TXNUPD if old_media else TXNADD
            trans.add(MEDIA_KEY, op, media.handle,
                      old_media,
                      media.serialize())
        # Misc updates:
        self.media_attributes.update(
            [str(attr.type) for attr in media.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        # Emit after added:
        if emit:
            self.emit(emit, ([media.handle],))
        self.has_changed = True

    def update_backlinks(self, obj):
        # First, delete the current references:
        self.dbapi.execute("DELETE FROM reference WHERE obj_handle = ?;",
                           [obj.handle])
        # Now, add the current ones:
        references = set(obj.get_referenced_handles_recursively())
        for (ref_class_name, ref_handle) in references:
            self.dbapi.execute("""INSERT INTO reference
                       (obj_handle, obj_class, ref_handle, ref_class)
                       VALUES(?, ?, ?, ?);""",
                               [obj.handle,
                                obj.__class__.__name__,
                                ref_handle,
                                ref_class_name])
        # This function is followed by a commit.

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.
        """
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        if self.readonly or not handle:
            return
        if handle in self.person_map:
            person = Person.create(self.person_map[handle])
            self.dbapi.execute("DELETE FROM person WHERE handle = ?;", [handle])
            self.emit("person-delete", ([handle],))
            if not transaction.batch:
                transaction.add(PERSON_KEY, TXNDEL, person.handle,
                                person.serialize(), None)

    def _do_remove(self, handle, transaction, data_map, data_id_map, key):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        key2table = {
            PERSON_KEY:     "person",
            FAMILY_KEY:     "family",
            SOURCE_KEY:     "source",
            CITATION_KEY:   "citation",
            EVENT_KEY:      "event",
            MEDIA_KEY:      "media",
            PLACE_KEY:      "place",
            REPOSITORY_KEY: "repository",
            NOTE_KEY:       "note",
            TAG_KEY:        "tag",
            }
        if self.readonly or not handle:
            return
        if handle in data_map:
            self.dbapi.execute("DELETE FROM %s WHERE handle = ?;" % key2table[key],
                               [handle])
            self.emit(KEY_TO_NAME_MAP[key] + "-delete", ([handle],))
            if not transaction.batch:
                data = data_map[handle]
                transaction.add(key, TXNDEL, handle, data, None)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.

        Returns an interator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Default: None means include all classes.
        :type include_classes: list of class names

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        self.dbapi.execute("SELECT obj_class, obj_handle FROM reference WHERE ref_handle = ?;",
                                 [handle])
        rows = self.dbapi.fetchall()
        for row in rows:
            if (include_classes is None) or (row[0] in include_classes):
                yield (row[0], row[1])

    def find_initial_person(self):
        handle = self.get_default_handle()
        person = None
        if handle:
            person = self.get_person_from_handle(handle)
            if person:
                return person
        self.dbapi.execute("SELECT handle FROM person;")
        row = self.dbapi.fetchone()
        if row:
            return self.get_person_from_handle(row[0])

    def iter_items_order_by_python(self, order_by, class_):
        """
        This method is for those iter_items with a order_by, but
        can't be done with secondary fields.
        """
        # first build sort order:
        sorted_items = []
        query = "SELECT blob_data FROM %s;" % class_.__name__.lower()
        self.dbapi.execute(query)
        rows = self.dbapi.fetchall()
        for row in rows:
                obj = self.get_table_func(class_.__name__,"class_func").create(pickle.loads(row[0]))
                # just use values and handle to keep small:
                sorted_items.append((eval_order_by(order_by, obj, self), obj.handle))
        # next we sort by fields and direction
        pos = len(order_by) - 1
        for (field, order) in reversed(order_by): # sort the lasts parts first
            sorted_items.sort(key=itemgetter(pos), reverse=(order=="DESC"))
            pos -= 1
        # now we will look them up again:
        for (order_by_values, handle) in sorted_items:
            yield self.get_table_func(class_.__name__,"handle_func")(handle)

    def iter_items(self, order_by, class_):
        # check if order_by fields are secondary
        # if so, fine
        # else, use Python sorts
        if order_by:
            secondary_fields = class_.get_secondary_fields()
            if not self._check_order_by_fields(class_.__name__, order_by, secondary_fields):
                for item in self.iter_items_order_by_python(order_by, class_):
                    yield item
                return
        ## Continue with dbapi select
        if order_by is None:
            query = "SELECT blob_data FROM %s;" % class_.__name__.lower()
        else:
            order_phrases = ["%s %s" % (self._hash_name(class_.__name__, class_.get_field_alias(field)), direction)
                             for (field, direction) in order_by]
            query = "SELECT blob_data FROM %s ORDER BY %s;" % (class_.__name__.lower(), ", ".join(order_phrases))
        self.dbapi.execute(query)
        rows = self.dbapi.fetchall()
        for row in rows:
            yield class_.create(pickle.loads(row[0]))

    def iter_person_handles(self):
        self.dbapi.execute("SELECT handle FROM person;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_family_handles(self):
        self.dbapi.execute("SELECT handle FROM family;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_citation_handles(self):
        self.dbapi.execute("SELECT handle FROM citation;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_event_handles(self):
        self.dbapi.execute("SELECT handle FROM event;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_media_handles(self):
        self.dbapi.execute("SELECT handle FROM media;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_note_handles(self):
        self.dbapi.execute("SELECT handle FROM note;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_place_handles(self):
        self.dbapi.execute("SELECT handle FROM place;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_repository_handles(self):
        self.dbapi.execute("SELECT handle FROM repository;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_source_handles(self):
        self.dbapi.execute("SELECT handle FROM source;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def iter_tag_handles(self):
        self.dbapi.execute("SELECT handle FROM tag;")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield bytes(row[0], "utf-8")

    def reindex_reference_map(self, callback):
        callback(4)
        self.dbapi.execute("DELETE FROM reference;")
        primary_table = (
            (self.get_person_cursor, Person),
            (self.get_family_cursor, Family),
            (self.get_event_cursor, Event),
            (self.get_place_cursor, Place),
            (self.get_source_cursor, Source),
            (self.get_citation_cursor, Citation),
            (self.get_media_cursor, Media),
            (self.get_repository_cursor, Repository),
            (self.get_note_cursor, Note),
            (self.get_tag_cursor, Tag),
        )
        # Now we use the functions and classes defined above
        # to loop through each of the primary object tables.
        for cursor_func, class_func in primary_table:
            logging.info("Rebuilding %s reference map" %
                         class_func.__name__)
            with cursor_func() as cursor:
                for found_handle, val in cursor:
                    obj = class_func.create(val)
                    references = set(obj.get_referenced_handles_recursively())
                    # handle addition of new references
                    for (ref_class_name, ref_handle) in references:
                        self.dbapi.execute("""INSERT INTO reference (obj_handle, obj_class, ref_handle, ref_class)
                                                 VALUES(?, ?, ?, ?);""",
                                           [obj.handle,
                                            obj.__class__.__name__,
                                            ref_handle,
                                            ref_class_name])
        callback(5)

    def rebuild_secondary(self, update):
        # First, expand blob to individual fields:
        self.rebuild_secondary_fields()
        # Next, rebuild stats:
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)
        # Rebuild all order_by fields:
        ## Rebuild place order_by:
        self.dbapi.execute("""select blob_data from place;""")
        row = self.dbapi.fetchone()
        while row:
            place = Place.create(pickle.loads(row[0]))
            order_by = self._order_by_place_key(place)
            cur2 = self.dbapi.execute("""UPDATE place SET order_by = ? WHERE handle = ?;""",
                                      [order_by, place.handle])
            row = self.dbapi.fetchone()
        ## Rebuild person order_by:
        self.dbapi.execute("""select blob_data from person;""")
        row = self.dbapi.fetchone()
        while row:
            person = Person.create(pickle.loads(row[0]))
            order_by = self._order_by_person_key(person)
            cur2 = self.dbapi.execute("""UPDATE person SET order_by = ? WHERE handle = ?;""",
                                      [order_by, person.handle])
            row = self.dbapi.fetchone()
        ## Rebuild citation order_by:
        self.dbapi.execute("""select blob_data from citation;""")
        row = self.dbapi.fetchone()
        while row:
            citation = Citation.create(pickle.loads(row[0]))
            order_by = self._order_by_citation_key(citation)
            cur2 = self.dbapi.execute("""UPDATE citation SET order_by = ? WHERE handle = ?;""",
                                      [order_by, citation.handle])
            row = self.dbapi.fetchone()
        ## Rebuild source order_by:
        self.dbapi.execute("""select blob_data from source;""")
        row = self.dbapi.fetchone()
        while row:
            source = Source.create(pickle.loads(row[0]))
            order_by = self._order_by_source_key(source)
            cur2 = self.dbapi.execute("""UPDATE source SET order_by = ? WHERE handle = ?;""",
                                      [order_by, source.handle])
            row = self.dbapi.fetchone()
        ## Rebuild tag order_by:
        self.dbapi.execute("""select blob_data from tag;""")
        row = self.dbapi.fetchone()
        while row:
            tag = Tag.create(pickle.loads(row[0]))
            order_by = self._order_by_tag_key(tag.name)
            cur2 = self.dbapi.execute("""UPDATE tag SET order_by = ? WHERE handle = ?;""",
                                      [order_by, tag.handle])
            row = self.dbapi.fetchone()
        ## Rebuild media order_by:
        self.dbapi.execute("""select blob_data from media;""")
        row = self.dbapi.fetchone()
        while row:
            media = Media.create(pickle.loads(row[0]))
            order_by = self._order_by_media_key(media)
            cur2 = self.dbapi.execute("""UPDATE media SET order_by = ? WHERE handle = ?;""",
                                      [order_by, media.handle])
            row = self.dbapi.fetchone()

    def has_handle_for_person(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM person WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_family(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM family WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_source(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM source WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_citation(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM citation WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_event(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM event WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_media(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM media WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_place(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM place WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_repository(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM repository WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_note(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM note WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_handle_for_tag(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT 1 FROM tag WHERE handle = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_person(self, key):
        self.dbapi.execute("SELECT 1 FROM person WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_family(self, key):
        self.dbapi.execute("SELECT 1 FROM family WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_source(self, key):
        self.dbapi.execute("SELECT 1 FROM source WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_citation(self, key):
        self.dbapi.execute("SELECT 1 FROM citation WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_event(self, key):
        self.dbapi.execute("SELECT 1 FROM event WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_media(self, key):
        self.dbapi.execute("SELECT 1 FROM media WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_place(self, key):
        self.dbapi.execute("SELECT 1 FROM place WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_repository(self, key):
        self.dbapi.execute("SELECT 1 FROM repository WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def has_gramps_id_for_note(self, key):
        self.dbapi.execute("SELECT 1 FROM note WHERE gramps_id = ?", [key])
        return self.dbapi.fetchone() != None

    def get_person_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM person;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_family_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM family;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_source_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM source;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_citation_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM citation;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_event_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM event;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_media_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM media;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_place_gramps_ids(self):
        self.dbapi.execute("SELECT gramps FROM place;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_repository_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM repository;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_note_gramps_ids(self):
        self.dbapi.execute("SELECT gramps_id FROM note;")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def _get_raw_person_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM person WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_person_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM person WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_family_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM family WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_family_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM family WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_source_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM source WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_source_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM source WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_citation_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM citation WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_citation_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM citation WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_event_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM event WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_event_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM event WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_media_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM media WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_media_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM media WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_place_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM place WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_place_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM place WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_repository_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM repository WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_repository_from_id_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM repository WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_note_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM note WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_note_from_id_data(self, key):
        self.dbapi.execute("SELECT blob_data FROM note WHERE gramps_id = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_tag_data(self, key):
        if isinstance(key, bytes):
            key = str(key, "utf-8")
        self.dbapi.execute("SELECT blob_data FROM tag WHERE handle = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def rebuild_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        Not called: this is a database-efficient version
        """
        self.dbapi.execute("""SELECT given_name, gender_type FROM person;""")
        gstats = {}
        for row in self.dbapi.fetchall():
            first_name = row[0]
            if first_name not in gstats:
                gstats[first_name] = (0, 0, 0)
            if gender_type == Person.MALE:
                gstats[first_name] = (gstats[first_name][0] + 1,
                                      gstats[first_name][1],
                                      gstats[first_name][2])
            elif gender_type == Person.FEMALE:
                gstats[first_name] = (gstats[first_name][0],
                                      gstats[first_name][1] + 1,
                                      gstats[first_name][2])
            else:
                gstats[first_name] = (gstats[first_name][0],
                                      gstats[first_name][1],
                                      gstats[first_name][2] + 1)
        return gstats

    def get_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        """
        self.dbapi.execute("""SELECT given_name, female, male, unknown FROM gender_stats;""")
        gstats = {}
        for row in self.dbapi.fetchall():
            gstats[row[0]] = (row[1], row[2], row[3])
        return gstats

    def save_gender_stats(self, gstats):
        self.dbapi.execute("""DELETE FROM gender_stats;""")
        for key in gstats.stats:
            female, male, unknown = gstats.stats[key]
            self.dbapi.execute("""INSERT INTO gender_stats(given_name, female, male, unknown)
                                              VALUES(?, ?, ?, ?);""",
                               [key, female, male, unknown]);

    def get_surname_list(self):
        self.dbapi.execute("""SELECT DISTINCT surname FROM person ORDER BY surname;""")
        surname_list = []
        for row in self.dbapi.fetchall():
            surname_list.append(row[0])
        return surname_list

    def save_surname_list(self):
        """
        Save the surname_list into persistant storage.
        """
        # Nothing for DB-API to do; saves in person table
        pass

    def build_surname_list(self):
        """
        Rebuild the surname_list.
        """
        # Nothing for DB-API to do; saves in person table
        pass

    def drop_tables(self):
        """
        Useful in testing, reseting.
        """
        self.dbapi.try_execute("""DROP TABLE  person;""")
        self.dbapi.try_execute("""DROP TABLE  family;""")
        self.dbapi.try_execute("""DROP TABLE  source;""")
        self.dbapi.try_execute("""DROP TABLE  citation""")
        self.dbapi.try_execute("""DROP TABLE  event;""")
        self.dbapi.try_execute("""DROP TABLE  media;""")
        self.dbapi.try_execute("""DROP TABLE  place;""")
        self.dbapi.try_execute("""DROP TABLE  repository;""")
        self.dbapi.try_execute("""DROP TABLE  note;""")
        self.dbapi.try_execute("""DROP TABLE  tag;""")
        # Secondary:
        self.dbapi.try_execute("""DROP TABLE  reference;""")
        self.dbapi.try_execute("""DROP TABLE  name_group;""")
        self.dbapi.try_execute("""DROP TABLE  metadata;""")
        self.dbapi.try_execute("""DROP TABLE  gender_stats;""")

    def _sql_type(self, python_type):
        """
        Given a schema type, return the SQL type for
        a new column.
        """
        from gramps.gen.lib.handle import HandleClass
        if isinstance(python_type, HandleClass):
            return "VARCHAR(50)"
        elif python_type == str:
            return "TEXT"
        elif python_type in [bool, int]:
            return "INTEGER"
        elif python_type in [float]:
            return "REAL"
        else:
            return "BLOB"

    def rebuild_secondary_fields(self):
        """
        Add secondary fields, update, and create indexes.
        """
        LOG.info("Rebuilding secondary fields...")
        for table in self.get_table_func():
            if not hasattr(self.get_table_func(table,"class_func"), "get_secondary_fields"):
                continue
            # do a select on all; if it works, then it is ok; else, check them all
            table_name = table.lower()
            try:
                fields = [self._hash_name(table, field) for (field, ptype) in
                          self.get_table_func(table,"class_func").get_secondary_fields()]
                if fields:
                    self.dbapi.execute("select %s from %s limit 1;" % (", ".join(fields), table_name))
                # if no error, continue
                LOG.info("Table %s is up to date" % table)
                continue
            except:
                pass # got to add missing ones, so continue
            LOG.info("Table %s needs rebuilding..." % table)
            altered = False
            for field_pair in self.get_table_func(table,"class_func").get_secondary_fields():
                field, python_type = field_pair
                field = self._hash_name(table, field)
                sql_type = self._sql_type(python_type)
                try:
                    # test to see if it exists:
                    self.dbapi.execute("SELECT %s FROM %s LIMIT 1;" % (field, table_name))
                    LOG.info("    Table %s, field %s is up to date" % (table, field))
                except:
                    # if not, let's add it
                    LOG.info("    Table %s, field %s was added" % (table, field))
                    self.dbapi.execute("ALTER TABLE %s ADD COLUMN %s %s;" % (table_name, field, sql_type))
                    altered = True
            if altered:
                LOG.info("Table %s is being committed, rebuilt, and indexed..." % table)
                self.update_secondary_values_table(table)
                self.create_secondary_indexes_table(table)

    def create_secondary_indexes(self):
        """
        Create the indexes for the secondary fields.
        """
        for table in self.get_table_func():
            if not hasattr(self.get_table_func(table,"class_func"), "get_index_fields"):
                continue
            self.create_secondary_indexes_table(table)

    def create_secondary_indexes_table(self, table):
        """
        Create secondary indexes for just this table.
        """
        table_name = table.lower()
        for fields in self.get_table_func(table,"class_func").get_index_fields():
            for field in fields:
                field = self._hash_name(table, field)
                self.dbapi.try_execute("CREATE INDEX %s_%s ON %s(%s);" % (table, field, table_name, field))

    def update_secondary_values_all(self):
        """
        Go through all items in all tables, and update their secondary
        field values.
        """
        for table in self.get_table_func():
            self.update_secondary_values_table(table)

    def update_secondary_values_table(self, table):
        """
        Go through all items in a table, and update their secondary
        field values.
        table - "Person", "Place", "Media", etc.
        """
        if not hasattr(self.get_table_func(table,"class_func"), "get_secondary_fields"):
            return
        for item in self.get_table_func(table,"iter_func")():
            self.update_secondary_values(item)

    def update_secondary_values(self, item):
        """
        Given a primary object update its secondary field values in the database.
        Does not commit.
        """
        table = item.__class__.__name__
        fields = self.get_table_func(table,"class_func").get_secondary_fields()
        fields = [field for (field, direction) in fields]
        sets = []
        values = []
        for field in fields:
            value = item.get_field(field, self, ignore_errors=True)
            field = self._hash_name(item.__class__.__name__, field)
            sets.append("%s = ?" % field)
            values.append(value)
        if len(values) > 0:
            table_name = table.lower()
            self.dbapi.execute("UPDATE %s SET %s where handle = ?;" % (table_name, ", ".join(sets)),
                               self._sql_cast_list(table, sets, values) + [item.handle])

    def _sql_cast_list(self, table, fields, values):
        """
        Given a list of field names and values, return the values
        in the appropriate type.
        """
        return [v if type(v) is not bool else int(v) for v in values]

    def _sql_repr(self, value):
        """
        Given a Python value, turn it into a SQL value.
        """
        if value is True:
            return "1"
        elif value is False:
            return "0"
        elif isinstance(value, list):
            return repr(tuple(value))
        else:
            return repr(value)

    def _build_where_clause_recursive(self, table, where):
        """
        where - (field, op, value)
               - ["NOT", where]
               - ["AND", (where, ...)]
               - ["OR", (where, ...)]
        """
        if where is None:
            return ""
        elif len(where) == 3:
            field, op, value = where
            return "(%s %s %s)" % (self._hash_name(table, field), op, self._sql_repr(value))
        elif where[0] in ["AND", "OR"]:
            parts = [self._build_where_clause_recursive(table, part)
                     for part in where[1]]
            return "(%s)" % ((" %s " % where[0]).join(parts))
        else:
            return "(NOT %s)" % self._build_where_clause_recursive(table, where[1])

    def _build_where_clause(self, table, where):
        """
        where - a list in where format
        return - "WHERE conditions..."
        """
        parts = self._build_where_clause_recursive(table, where)
        if parts:
            return ("WHERE " + parts)
        else:
            return ""

    def _build_order_clause(self, table, order_by):
        """
        order_by - [(field, "ASC" | "DESC"), ...]
        """
        if order_by:
            order_clause = ", ".join(["%s %s" % (self._hash_name(table, field), dir)
                                     for (field, dir) in order_by])
            return "ORDER BY " + order_clause
        else:
            return ""

    def _build_select_fields(self, table, select_fields, secondary_fields):
        """
        fields - [field, ...]
        return: "field, field, field"
        """
        all_available = all([(field in secondary_fields) for field in select_fields])
        if all_available: # we can get them without expanding
            return select_fields
        else:
            return ["blob_data"] # nope, we'll have to expand blob to get all fields

    def _check_order_by_fields(self, table, order_by, secondary_fields):
        """
        Check to make sure all order_by fields are defined. If not, then
        we need to do the Python-based order.

        secondary_fields are hashed.
        """
        if order_by:
            for (field, dir) in order_by:
                if self._hash_name(table, field) not in secondary_fields:
                    return False
        return True

    def _check_where_fields(self, table, where, secondary_fields):
        """
        Check to make sure all where fields are defined. If not, then
        we need to do the Python-based select.

        secondary_fields are hashed.
        """
        if where is None:
            return True
        elif len(where) == 2: # ["AND" [...]] | ["OR" [...]] | ["NOT" expr]
            connector, exprs = where
            if connector in ["AND", "OR"]:
                for expr in exprs:
                    value = self._check_where_fields(table, expr, secondary_fields)
                    if value == False:
                        return False
                return True
            else: # "NOT"
                return self._check_where_fields(table, exprs, secondary_fields)
        elif len(where) == 3: # (name, op, value)
            (name, op, value) = where
            # just the ones we need for where
            return (self._hash_name(table, name) in secondary_fields)

    def _select(self, table, fields=None, start=0, limit=-1,
                where=None, order_by=None):
        """
        Default implementation of a select for those databases
        that don't support SQL. Returns a list of dicts, total,
        and time.

        table - Person, Family, etc.
        fields - used by object.get_field()
        start - position to start
        limit - count to get; -1 for all
        where - (field, SQL string_operator, value) |
                 ["AND", [where, where, ...]]      |
                 ["OR",  [where, where, ...]]      |
                 ["NOT",  where]
        order_by - [[fieldname, "ASC" | "DESC"], ...]
        """
        secondary_fields = ([self._hash_name(table, field) for (field, ptype) in
                             self.get_table_func(table,"class_func").get_secondary_fields()] +
                            ["handle"]) # handle is a sql field, but not listed in secondaries
        # If no fields, then we need objects:
        # Check to see if where matches SQL fields:
        table_name = table.lower()
        if ((not self._check_where_fields(table, where, secondary_fields)) or
            (not self._check_order_by_fields(table, order_by, secondary_fields))):
            # If not, then need to do select via Python:
            generator = super()._select(table, fields, start, limit, where, order_by)
            for item in generator:
                yield item
            return
        # Otherwise, we are SQL
        if fields is None:
            fields = ["blob_data"]
        get_count_only = False
        if fields[0] == "count(1)":
            hashed_fields = ["count(1)"]
            fields = ["count(1)"]
            select_fields = ["count(1)"]
            get_count_only = True
        else:
            hashed_fields = [self._hash_name(table, field) for field in fields]
            fields = hashed_fields
            select_fields = self._build_select_fields(table, fields, secondary_fields)
        where_clause = self._build_where_clause(table, where)
        order_clause = self._build_order_clause(table, order_by)
        if get_count_only:
            select_fields = ["1"]
        if start:
            query = "SELECT %s FROM %s %s %s LIMIT %s, %s " % (
                ", ".join(select_fields), table_name, where_clause, order_clause, start, limit
            )
        else:
            query = "SELECT %s FROM %s %s %s LIMIT %s" % (
                ", ".join(select_fields), table_name, where_clause, order_clause, limit
            )
        if get_count_only:
            self.dbapi.execute("SELECT count(1) from (%s) AS temp_select;" % query)
            rows = self.dbapi.fetchall()
            yield rows[0][0]
            return
        self.dbapi.execute(query)
        rows = self.dbapi.fetchall()
        for row in rows:
            if fields[0] != "blob_data":
                obj = None # don't build it if you don't need it
                data = {}
                for field in fields:
                    if field in select_fields:
                        data[field.replace("__", ".")] = row[select_fields.index(field)]
                    else:
                        if obj is None:  # we need it! create it and cache it:
                            obj = self.get_table_func(table,"class_func").create(pickle.loads(row[0]))
                        # get the field, even if we need to do a join:
                        # FIXME: possible optimize: do a join in select for this if needed:
                        field = field.replace("__", ".")
                        data[field] = obj.get_field(field, self, ignore_errors=True)
                yield data
            else:
                obj = self.get_table_func(table,"class_func").create(pickle.loads(row[0]))
                yield obj

    def get_summary(self):
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Schema version")
        """
        summary = super().get_summary()
        summary.update(self.dbapi.__class__.get_summary())
        return summary
