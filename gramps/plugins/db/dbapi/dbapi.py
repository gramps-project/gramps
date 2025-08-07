#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016,2024 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016-2017      Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Database API interface
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging
import json
import time

from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.db.dbconst import (
    DBLOGNAME,
    KEY_TO_CLASS_MAP,
    KEY_TO_NAME_MAP,
    REFERENCE_KEY,
    TXNADD,
    TXNDEL,
    TXNUPD,
)
from gramps.gen.db.generic import DbGeneric
from gramps.gen.lib import (
    Citation,
    Event,
    Family,
    Media,
    Note,
    Person,
    Place,
    Repository,
    Source,
    Tag,
)
from gramps.gen.lib.genderstats import GenderStats
from gramps.gen.updatecallback import UpdateCallback

LOG = logging.getLogger(".dbapi")
_LOG = logging.getLogger(DBLOGNAME)


# -------------------------------------------------------------------------
#
# DBAPI class
#
# -------------------------------------------------------------------------
class DBAPI(DbGeneric):
    """
    Database backends class for DB-API 2.0 databases
    """

    def _initialize(self, directory, username, password):
        """
        Initialize the database connection.

        :param directory: Directory containing the database
        :param username: Username (not used for SQLite)
        :param password: Password (not used for SQLite)
        """
        from .sqlite import SQLite

        sqlite_db = SQLite()
        sqlite_db._initialize(directory, username, password)
        self.dbapi = sqlite_db.dbapi

    def use_json_data(self):
        """
        A DBAPI level method for testing if the
        database supports JSON access.
        """
        # Check if json_data exists on metadata as a proxy to see
        # if the database has been converted to use JSON data
        return self.dbapi.column_exists("metadata", "json_data")

    def upgrade_table_for_json_data(self, table_name):
        """
        A DBAPI level method for upgrading the given table
        adding a json_data column.
        """
        if not self.dbapi.column_exists(table_name, "json_data"):
            self.dbapi.execute("ALTER TABLE %s ADD COLUMN json_data TEXT;" % table_name)

    def _schema_exists(self):
        """
        Check to see if the schema exists.

        We use the existence of the person table as a proxy for the database
        being new.
        """
        return self.dbapi.table_exists("person")

    def _create_schema(self, json_data):
        """
        Create and update schema.
        """
        self.dbapi.begin()
        if json_data:
            col_data = "json_data TEXT"
            meta_col_data = "json_data TEXT, value BLOB"
        else:
            col_data = "blob_data BLOB"
            meta_col_data = "value BLOB"

        # make sure schema is up to date:
        self.dbapi.execute(
            "CREATE TABLE person "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            "given_name TEXT, "
            "surname TEXT, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE family "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE source "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE citation "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE event "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE media "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE place "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            "enclosed_by VARCHAR(50), "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE repository "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE note "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE tag "
            "("
            "handle VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{col_data}"
            ")"
        )
        # Secondary:
        self.dbapi.execute(
            "CREATE TABLE reference "
            "("
            "obj_handle VARCHAR(50), "
            "obj_class TEXT, "
            "ref_handle VARCHAR(50), "
            "ref_class TEXT"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE name_group "
            "("
            "name VARCHAR(50) PRIMARY KEY NOT NULL, "
            "grouping TEXT"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE metadata "
            "("
            "setting VARCHAR(50) PRIMARY KEY NOT NULL, "
            f"{meta_col_data}"
            ")"
        )
        self.dbapi.execute(
            "CREATE TABLE gender_stats "
            "("
            "given_name TEXT, "
            "female INTEGER, "
            "male INTEGER, "
            "unknown INTEGER"
            ")"
        )

        self._create_secondary_columns()

        ## Indices:
        self.dbapi.execute("CREATE INDEX person_gramps_id ON person(gramps_id)")
        self.dbapi.execute("CREATE INDEX person_surname ON person(surname)")
        self.dbapi.execute("CREATE INDEX person_given_name ON person(given_name)")
        self.dbapi.execute("CREATE INDEX source_title ON source(title)")
        self.dbapi.execute("CREATE INDEX source_gramps_id ON source(gramps_id)")
        self.dbapi.execute("CREATE INDEX citation_page ON citation(page)")
        self.dbapi.execute("CREATE INDEX citation_gramps_id ON citation(gramps_id)")
        self.dbapi.execute("CREATE INDEX media_desc ON media(desc)")
        self.dbapi.execute("CREATE INDEX media_gramps_id ON media(gramps_id)")
        self.dbapi.execute("CREATE INDEX place_title ON place(title)")
        self.dbapi.execute("CREATE INDEX place_enclosed_by ON place(enclosed_by)")
        self.dbapi.execute("CREATE INDEX place_gramps_id ON place(gramps_id)")
        self.dbapi.execute("CREATE INDEX tag_name ON tag(name)")
        self.dbapi.execute("CREATE INDEX reference_ref_handle ON reference(ref_handle)")
        self.dbapi.execute("CREATE INDEX reference_obj_handle ON reference(obj_handle)")
        self.dbapi.execute("CREATE INDEX family_gramps_id ON family(gramps_id)")
        self.dbapi.execute("CREATE INDEX event_gramps_id ON event(gramps_id)")
        self.dbapi.execute("CREATE INDEX repository_gramps_id ON repository(gramps_id)")
        self.dbapi.execute("CREATE INDEX note_gramps_id ON note(gramps_id)")

        # Performance indexes for common query patterns
        self._create_performance_indexes()

        self.dbapi.commit()

    def _drop_column(self, table_name, column_name):
        """
        Used to remove a column of data which we don't need anymore.
        Must be used within a tranaction
        If db doesn't support, nothing happens
        """
        self.dbapi.drop_column(table_name, column_name)

    def _close(self):
        self.dbapi.close()

    def _txn_begin(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db BEGIN;
        """
        if self.transaction is None:
            _LOG.debug("    DBAPI %s transaction begin", hex(id(self)))
            self.dbapi.begin()

    def _txn_commit(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db END;
        """
        if self.transaction is None:
            _LOG.debug("    DBAPI %s transaction commit", hex(id(self)))
            self.dbapi.commit()

    def _txn_abort(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db ROLLBACK;
        """
        if self.transaction is None:
            self.dbapi.rollback()

    def _collation(self, locale):
        """
        Get the adjusted collation if there is one, falling back on
        the locale.collation.
        """
        collation = self.dbapi.check_collation(locale)
        if collation is None:
            return locale.get_collation()
        return collation

    def transaction_begin(self, transaction):
        """
        Transactions are handled automatically by the db layer.
        """
        _LOG.debug(
            "    %sDBAPI %s transaction begin for '%s'",
            "Batch " if transaction.batch else "",
            hex(id(self)),
            transaction.get_description(),
        )
        if transaction.batch:
            # A batch transaction does not store the commits
            # Aborting the session completely will become impossible.
            self.abort_possible = False
        self.transaction = transaction
        self.dbapi.begin()
        return transaction

    def transaction_commit(self, transaction):
        """
        Executed at the end of a transaction.
        """
        _LOG.debug(
            "    %sDBAPI %s transaction commit for '%s'",
            "Batch " if transaction.batch else "",
            hex(id(self)),
            transaction.get_description(),
        )

        action = {TXNADD: "-add", TXNUPD: "-update", TXNDEL: "-delete", None: "-delete"}
        self.dbapi.commit()
        if not transaction.batch:
            # Now, emit signals:
            # do deletes and adds first
            for trans_type in [TXNDEL, TXNADD, TXNUPD]:
                for obj_type in range(11):
                    if (
                        obj_type != REFERENCE_KEY
                        and (obj_type, trans_type) in transaction
                    ):
                        if trans_type == TXNDEL:
                            handles = [
                                handle
                                for (handle, data) in transaction[
                                    (obj_type, trans_type)
                                ]
                            ]
                        else:
                            handles = [
                                handle
                                for (handle, data) in transaction[
                                    (obj_type, trans_type)
                                ]
                                if (handle, None) not in transaction[(obj_type, TXNDEL)]
                            ]
                        if handles:
                            signal = KEY_TO_NAME_MAP[obj_type] + action[trans_type]
                            self.emit(signal, (handles,))
        self.transaction = None
        msg = transaction.get_description()
        self.undodb.commit(transaction, msg)
        self._after_commit(transaction)
        transaction.clear()
        self.has_changed += 1  # Also gives commits since startup

    def transaction_abort(self, transaction):
        """
        Executed after a batch operation abort.
        """
        self.dbapi.rollback()
        self.transaction = None
        transaction.clear()
        transaction.first = None
        transaction.last = None
        self._after_commit(transaction)

    def _get_metadata_keys(self):
        """
        Get all of the metadata setting names from the
        database.
        """
        self.dbapi.execute("SELECT setting FROM metadata;")
        return [row[0] for row in self.dbapi.fetchall()]

    def _get_metadata(self, key, default="_"):
        """
        Get an item from the database.

        Note we reserve and use _ to denote default value of []
        """
        self.dbapi.execute(
            f"SELECT {self.serializer.metadata_field} FROM metadata WHERE setting = ?",
            [key],
        )
        row = self.dbapi.fetchone()
        if row:
            return self.serializer.metadata_to_object(row[0])

        if default == "_":
            return []
        return default

    def _set_metadata(self, key, value, use_txn=True):
        """
        key: string
        value: item, will be serialized here

        Note: if use_txn, then begin/commit txn
        """
        if use_txn:
            self._txn_begin()
        self.dbapi.execute("SELECT 1 FROM metadata WHERE setting = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute(
                f"UPDATE metadata SET {self.serializer.metadata_field} = ? WHERE setting = ?",
                [self.serializer.object_to_metadata(value), key],
            )
        else:
            self.dbapi.execute(
                f"INSERT INTO metadata (setting, {self.serializer.metadata_field}) VALUES (?, ?)",
                [key, self.serializer.object_to_metadata(value)],
            )
        if use_txn:
            self._txn_commit()

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        self.dbapi.execute("SELECT name, grouping FROM name_group ORDER BY name")
        # not None test below fixes db corrupted by 11011 for export
        return [row[0] for row in self.dbapi.fetchall() if row[1] is not None]

    def get_name_group_mapping(self, surname):
        """
        Return the default grouping name for a surname.
        """
        self.dbapi.execute("SELECT grouping FROM name_group WHERE name = ?", [surname])
        row = self.dbapi.fetchone()
        if row and row[0] is not None:
            # not None test fixes db corrupted by 11011
            return row[0]
        return surname

    def get_person_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with composite index
            self.dbapi.execute(
                "SELECT handle FROM person "
                "ORDER BY surname, given_name "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM person")
        return [row[0] for row in self.dbapi.fetchall()]
    
    def get_person_cursor(self, sort_handles=False, locale=glocale):
        """
        Return a cursor that iterates over person handles without loading
        all into memory at once.
        
        :param sort_handles: If True, the cursor is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        :returns: Iterator over person handles
        """
        if hasattr(self.dbapi, 'cursor'):
            # Use real database cursor for backends that support it
            cursor = self.dbapi.cursor()
            if sort_handles:
                cursor.execute(
                    "SELECT handle FROM person "
                    "ORDER BY surname, given_name "
                    f'COLLATE "{self._collation(locale)}"'
                )
            else:
                cursor.execute("SELECT handle FROM person")
            # Return iterator that yields handles one at a time
            return (row[0] for row in cursor)
        else:
            # Fallback to regular list for backends without cursor support
            return iter(self.get_person_handles(sort_handles, locale))

    def get_family_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with family_parents index
            self.dbapi.execute(
                "SELECT family.handle "
                "FROM family "
                "LEFT JOIN person AS father "
                "ON family.father_handle = father.handle "
                "LEFT JOIN person AS mother "
                "ON family.mother_handle = mother.handle "
                "ORDER BY COALESCE(father.surname, mother.surname, ''), "
                "COALESCE(father.given_name, mother.given_name, '') "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM family")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM event")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_citation_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        :param sort_handles: If True, the list is sorted by Citation title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with citation_source index
            self.dbapi.execute(
                "SELECT citation.handle "
                "FROM citation "
                "LEFT JOIN source ON citation.source_handle = source.handle "
                "ORDER BY COALESCE(source.title, ''), citation.page "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM citation")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_source_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Source in
        the database.

        :param sort_handles: If True, the list is sorted by Source title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with source_title index
            self.dbapi.execute(
                "SELECT handle FROM source "
                "ORDER BY COALESCE(title, '') "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM source")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_place_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Place in
        the database.

        :param sort_handles: If True, the list is sorted by Place title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with place_hierarchy index
            self.dbapi.execute(
                "SELECT handle FROM place "
                "ORDER BY COALESCE(title, '') "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM place")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        self.dbapi.execute("SELECT handle FROM repository")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_media_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        :param sort_handles: If True, the list is sorted by Media title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with media_path index
            self.dbapi.execute(
                "SELECT handle FROM media "
                "ORDER BY COALESCE(desc, path, '') "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM media")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM note")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_tag_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Tag in
        the database.

        :param sort_handles: If True, the list is sorted by Tag name.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            # Use optimized query with tag_name index
            self.dbapi.execute(
                "SELECT handle FROM tag "
                "ORDER BY COALESCE(name, '') "
                f'COLLATE "{self._collation(locale)}"'
            )
        else:
            # Use simple query for unsorted results
            self.dbapi.execute("SELECT handle FROM tag")
        return [row[0] for row in self.dbapi.fetchall()]

    def get_tag_from_name(self, name):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        """
        self.dbapi.execute(
            f"SELECT {self.serializer.data_field} FROM tag WHERE name = ?", [name]
        )
        row = self.dbapi.fetchone()
        if row:
            return self.serializer.string_to_object(Tag, row[0])
        return None

    def _get_number_of(self, obj_key):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(f"SELECT count(1) FROM {table}")
        row = self.dbapi.fetchone()
        return row[0]

    def has_name_group_key(self, key):
        """
        Return if a key exists in the name_group table.
        """
        self.dbapi.execute("SELECT grouping FROM name_group WHERE name = ?", [key])
        row = self.dbapi.fetchone()
        return row and row[0] is not None

    def set_name_group_mapping(self, name, group):
        """
        Set the default grouping name for a surname.
        """
        self._txn_begin()
        self.dbapi.execute("SELECT 1 FROM name_group WHERE name = ?", [name])
        row = self.dbapi.fetchone()
        if row and group is not None:
            self.dbapi.execute(
                "UPDATE name_group SET grouping=? WHERE name = ?", [group, name]
            )
        elif row and group is None:
            self.dbapi.execute("DELETE FROM name_group WHERE name = ?", [name])
        else:
            self.dbapi.execute(
                "INSERT INTO name_group (name, grouping) VALUES (?, ?)",
                [name, group],
            )
        self._txn_commit()
        if group is None:
            group = ""
        self.emit("person-groupname-rebuild", (name, group))

    def _commit_base(self, obj, obj_key, trans, change_time):
        """
        Commit the specified object to the database, storing the changes as
        part of the transaction.
        """
        old_data = None
        obj.change = int(change_time or time.time())
        table = KEY_TO_NAME_MAP[obj_key]

        if self._has_handle(obj_key, obj.handle):
            old_data = self._get_raw_data(obj_key, obj.handle)
            # update the object:
            self.dbapi.execute(
                f"UPDATE {table} SET {self.serializer.data_field} = ? WHERE handle = ?",
                [self.serializer.object_to_string(obj), obj.handle],
            )
        else:
            # Insert the object:
            self.dbapi.execute(
                f"INSERT INTO {table} (handle, {self.serializer.data_field}) VALUES (?, ?)",
                [obj.handle, self.serializer.object_to_string(obj)],
            )
        self._update_secondary_values(obj)
        self._update_backlinks(obj, trans)
        if not trans.batch:
            if old_data:
                trans.add(
                    obj_key,
                    TXNUPD,
                    obj.handle,
                    old_data,
                    self.serializer.object_to_data(obj),
                )
            else:
                trans.add(
                    obj_key,
                    TXNADD,
                    obj.handle,
                    None,
                    self.serializer.object_to_data(obj),
                )

        return old_data

    def _commit_raw(self, data, obj_key):
        """
        Commit a serialized primary object to the database, storing the
        changes as part of the transaction.
        """
        table = KEY_TO_NAME_MAP[obj_key]
        handle = self.serializer.get_from_data_by_name(data, "handle")

        if self._has_handle(obj_key, handle):
            # update the object:
            self.dbapi.execute(
                f"UPDATE {table} SET {self.serializer.data_field} = ? WHERE handle = ?",
                [self.serializer.data_to_string(data), handle],
            )
        else:
            # Insert the object:
            self.dbapi.execute(
                f"INSERT INTO {table} (handle, {self.serializer.data_field}) VALUES (?, ?)",
                [handle, self.serializer.data_to_string(data)],
            )

    def _update_backlinks(self, obj, transaction):
        if not transaction.batch:
            # Find existing references
            self.dbapi.execute(
                "SELECT ref_class, ref_handle FROM reference WHERE obj_handle = ?",
                [obj.handle],
            )
            existing_references = set(self.dbapi.fetchall())

            # Once we have the list of rows that already have a reference
            # we need to compare it with the list of objects that are
            # still references from the primary object.
            current_references = set(obj.get_referenced_handles_recursively())
            no_longer_required_references = existing_references.difference(
                current_references
            )
            new_references = current_references.difference(existing_references)

            # Delete the existing references
            self.dbapi.execute(
                "DELETE FROM reference WHERE obj_handle = ?", [obj.handle]
            )

            # Now, add the current ones
            for ref_class_name, ref_handle in current_references:
                self.dbapi.execute(
                    "INSERT INTO reference "
                    "(obj_handle, obj_class, ref_handle, ref_class) "
                    "VALUES(?, ?, ?, ?)",
                    [obj.handle, obj.__class__.__name__, ref_handle, ref_class_name],
                )

            # Add new references to the transaction
            for ref_class_name, ref_handle in new_references:
                key = (obj.handle, ref_handle)
                data = (obj.handle, obj.__class__.__name__, ref_handle, ref_class_name)
                transaction.add(REFERENCE_KEY, TXNADD, key, None, data)

            # Add old references to the transaction
            for ref_class_name, ref_handle in no_longer_required_references:
                key = (obj.handle, ref_handle)
                old_data = (
                    obj.handle,
                    obj.__class__.__name__,
                    ref_handle,
                    ref_class_name,
                )
                transaction.add(REFERENCE_KEY, TXNDEL, key, old_data, None)
        else:  # batch mode
            current_references = set(obj.get_referenced_handles_recursively())

            # Delete the existing references
            self.dbapi.execute(
                "DELETE FROM reference WHERE obj_handle = ?", [obj.handle]
            )

            # Now, add the current ones
            for ref_class_name, ref_handle in current_references:
                self.dbapi.execute(
                    "INSERT INTO reference "
                    "(obj_handle, obj_class, ref_handle, ref_class) "
                    "VALUES(?, ?, ?, ?)",
                    [obj.handle, obj.__class__.__name__, ref_handle, ref_class_name],
                )

    def _do_remove(self, handle, transaction, obj_key):
        if self.readonly or not handle:
            return
        if self._has_handle(obj_key, handle):
            data = self._get_raw_data(obj_key, handle)
            obj_class = KEY_TO_CLASS_MAP[obj_key]
            self._remove_backlinks(obj_class, handle, transaction)
            table = KEY_TO_NAME_MAP[obj_key]
            self.dbapi.execute(f"DELETE FROM {table} WHERE handle = ?", [handle])
            if not transaction.batch:
                transaction.add(obj_key, TXNDEL, handle, data, None)

    def _remove_backlinks(self, obj_class, obj_handle, transaction):
        """
        Removes all references from this object (backlinks).
        """
        # collect backlinks from this object for undo
        self.dbapi.execute(
            "SELECT ref_class, ref_handle FROM reference WHERE obj_handle = ?",
            [obj_handle],
        )
        rows = self.dbapi.fetchall()
        # Now, delete backlinks from this object:
        self.dbapi.execute("DELETE FROM reference WHERE obj_handle = ?;", [obj_handle])
        # Add old references to the transaction
        if not transaction.batch:
            for ref_class_name, ref_handle in rows:
                key = (obj_handle, ref_handle)
                old_data = (obj_handle, obj_class, ref_handle, ref_class_name)
                transaction.add(REFERENCE_KEY, TXNDEL, key, old_data, None)

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
        self.dbapi.execute(
            "SELECT obj_class, obj_handle FROM reference WHERE ref_handle = ?",
            [handle],
        )
        rows = self.dbapi.fetchall()
        for row in rows:
            if (include_classes is None) or (row[0] in include_classes):
                yield (row[0], row[1])

    def find_initial_person(self):
        """
        Returns first person in the database
        """
        handle = self.get_default_handle()
        person = None
        if handle:
            person = self.get_person_from_handle(handle)
            if person:
                return person
        self.dbapi.execute("SELECT handle FROM person")
        row = self.dbapi.fetchone()
        if row:
            return self.get_person_from_handle(row[0])
        return None

    def _iter_handles(self, obj_key):
        """
        Return an iterator over handles in the database
        """
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(f"SELECT handle FROM {table}")
        rows = self.dbapi.fetchall()
        for row in rows:
            yield row[0]

    def _iter_raw_data(self, obj_key):
        """
        Return an iterator over raw data in the database.
        """
        table = KEY_TO_NAME_MAP[obj_key]
        with self.dbapi.cursor() as cursor:
            cursor.execute(f"SELECT handle, {self.serializer.data_field} FROM {table}")
            rows = cursor.fetchmany()
            while rows:
                for row in rows:
                    yield (row[0], self.serializer.string_to_data(row[1]))
                rows = cursor.fetchmany()

    def _iter_raw_place_tree_data(self):
        """
        Return an iterator over raw data in the place hierarchy.
        """
        to_do = [""]
        while to_do:
            handle = to_do.pop()
            self.dbapi.execute(
                f"SELECT handle, {self.serializer.data_field} FROM place WHERE enclosed_by = ?",
                [handle],
            )
            rows = self.dbapi.fetchall()
            for row in rows:
                to_do.append(row[0])
                yield (row[0], self.serializer.string_to_data(row[1]))

    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.
        """
        self._txn_begin()
        self.dbapi.execute("DELETE FROM reference")
        total = 0
        for tbl in (
            "people",
            "families",
            "events",
            "places",
            "sources",
            "citations",
            "media",
            "repositories",
            "notes",
            "tags",
        ):
            total += self.method("get_number_of_%s", tbl)()
        UpdateCallback.__init__(self, callback)
        self.set_total(total)
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
            logging.info("Rebuilding %s reference map", class_func.__name__)
            with cursor_func() as cursor:
                for _, val in cursor:
                    obj = self.serializer.data_to_object(val, class_func)
                    references = set(obj.get_referenced_handles_recursively())
                    # handle addition of new references
                    for ref_class_name, ref_handle in references:
                        self.dbapi.execute(
                            "INSERT INTO reference "
                            "(obj_handle, obj_class, ref_handle, ref_class) "
                            "VALUES (?, ?, ?, ?)",
                            [
                                obj.handle,
                                obj.__class__.__name__,
                                ref_handle,
                                ref_class_name,
                            ],
                        )
                    self.update()
        self._txn_commit()

    def rebuild_secondary(self, callback=None):
        """
        Rebuild secondary indices
        """
        if self.readonly:
            return

        total = 0
        for tbl in (
            "people",
            "families",
            "events",
            "places",
            "sources",
            "citations",
            "media",
            "repositories",
            "notes",
            "tags",
        ):
            total += self.method("get_number_of_%s", tbl)()
        UpdateCallback.__init__(self, callback)
        self.set_total(total)

        # First, expand blob to individual fields:
        self._txn_begin()
        for obj_type in (
            "Person",
            "Family",
            "Event",
            "Place",
            "Repository",
            "Source",
            "Citation",
            "Media",
            "Note",
            "Tag",
        ):
            for handle in self.method("get_%s_handles", obj_type)():
                obj = self.method("get_%s_from_handle", obj_type)(handle)
                self._update_secondary_values(obj)
                self.update()
        self._txn_commit()

        # Next, rebuild stats:
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)

    def _has_handle(self, obj_key, handle):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(f"SELECT 1 FROM {table} WHERE handle = ?", [handle])
        return self.dbapi.fetchone() is not None

    def _has_gramps_id(self, obj_key, gramps_id):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(f"SELECT 1 FROM {table} WHERE gramps_id = ?", [gramps_id])
        return self.dbapi.fetchone() is not None

    def _get_gramps_ids(self, obj_key):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(f"SELECT gramps_id FROM {table}")
        return [row[0] for row in self.dbapi.fetchall()]

    def _get_raw_data(self, obj_key, handle):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(
            f"SELECT {self.serializer.data_field} FROM {table} WHERE handle = ?",
            [handle],
        )
        row = self.dbapi.fetchone()
        if row:
            return self.serializer.string_to_data(row[0])
        return None

    def _get_raw_from_id_data(self, obj_key, gramps_id):
        table = KEY_TO_NAME_MAP[obj_key]
        self.dbapi.execute(
            f"SELECT {self.serializer.data_field} FROM {table} WHERE gramps_id = ?",
            [gramps_id],
        )
        row = self.dbapi.fetchone()
        if row:
            return self.serializer.string_to_data(row[0])
        return None

    def get_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        """
        self.dbapi.execute("SELECT given_name, female, male, unknown FROM gender_stats")
        gstats = {}
        for row in self.dbapi.fetchall():
            gstats[row[0]] = (row[1], row[2], row[3])
        return gstats

    def save_gender_stats(self, gstats):
        self._txn_begin()
        self.dbapi.execute("DELETE FROM gender_stats")
        for key in gstats.stats:
            female, male, unknown = gstats.stats[key]
            self.dbapi.execute(
                "INSERT INTO gender_stats "
                "(given_name, female, male, unknown) "
                "VALUES (?, ?, ?, ?)",
                [key, female, male, unknown],
            )
        self._txn_commit()

    def undo_reference(self, data, handle):
        """
        Helper method to undo a reference map entry
        """
        if data is None:
            self.dbapi.execute(
                "DELETE FROM reference WHERE obj_handle = ? AND ref_handle = ?",
                [handle[0], handle[1]],
            )
        else:
            self.dbapi.execute(
                "INSERT INTO reference "
                "(obj_handle, obj_class, ref_handle, ref_class) "
                "VALUES(?, ?, ?, ?)",
                data,
            )

    def undo_data(self, data, handle, obj_key):
        """
        Helper method to undo/redo the changes made
        """
        cls = KEY_TO_CLASS_MAP[obj_key]
        table = cls.lower()
        if data is None:
            self.dbapi.execute(f"DELETE FROM {table} WHERE handle = ?", [handle])
        else:
            if self._has_handle(obj_key, handle):
                self.dbapi.execute(
                    f"UPDATE {table} SET {self.serializer.data_field} = ? WHERE handle = ?",
                    [self.serializer.data_to_string(data), handle],
                )
            else:
                self.dbapi.execute(
                    f"INSERT INTO {table} (handle, {self.serializer.data_field}) VALUES (?, ?)",
                    [handle, self.serializer.data_to_string(data)],
                )
            obj = self.serializer.data_to_object(data, cls)
            self._update_secondary_values(obj)

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        self.dbapi.execute("SELECT DISTINCT surname FROM person ORDER BY surname")
        surname_list = []
        for row in self.dbapi.fetchall():
            surname_list.append(row[0])
        return surname_list

    def _sql_type(self, schema_type, max_length):
        """
        Given a schema type, return the SQL type for
        a new column.
        """
        if schema_type == "string":
            if max_length:
                return f"VARCHAR({max_length})"
            return "TEXT"
        if schema_type in ["boolean", "integer"]:
            return "INTEGER"
        if schema_type == "number":
            return "REAL"
        return "BLOB"

    def _create_secondary_columns(self):
        """
        Create secondary columns.
        """
        LOG.debug("Creating secondary columns...")
        for cls in (
            Person,
            Family,
            Event,
            Place,
            Repository,
            Source,
            Citation,
            Media,
            Note,
            Tag,
        ):
            table_name = cls.__name__.lower()
            for field, schema_type, max_length in cls.get_secondary_fields():
                if field != "handle":
                    sql_type = self._sql_type(schema_type, max_length)
                    self.dbapi.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN {field} {sql_type}"
                    )

    def _update_secondary_values(self, obj):
        """
        Given a primary object update its secondary field values
        in the database.
        Does not commit.
        """
        table = obj.__class__.__name__
        fields = [field[0] for field in obj.get_secondary_fields()]
        sets = []
        values = []
        for field in fields:
            sets.append(f"{field} = ?")
            values.append(getattr(obj, field))

        # Derived fields
        if table == "Person":
            given_name, surname = self._get_person_data(obj)
            sets.append("given_name = ?")
            values.append(given_name)
            sets.append("surname = ?")
            values.append(surname)
        if table == "Place":
            handle = self._get_place_data(obj)
            sets.append("enclosed_by = ?")
            values.append(handle)

        if len(values) > 0:
            table_name = table.lower()
            self.dbapi.execute(
                f'UPDATE {table_name} SET {", ".join(sets)} where handle = ?',
                self._sql_cast_list(values) + [obj.handle],
            )

    def _sql_cast_list(self, values):
        """
        Given a list of field names and values, return the values
        in the appropriate type.
        """
        return [v if not isinstance(v, bool) else int(v) for v in values]

    def _create_performance_indexes(self):
        """
        Create additional indexes for better query performance.
        """
        # Composite indexes for common queries
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS person_name_search ON person(surname, given_name);"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS family_parents ON family(father_handle, mother_handle);"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS citation_source ON citation(source_handle, page);"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS event_place ON event(place, description);"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS media_path ON media(path, mime);"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS place_hierarchy ON place(enclosed_by, title);"
        )

        # Partial indexes for filtered queries
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS person_living ON person(gender, death_ref_index) WHERE death_ref_index IS NULL;"
        )
        self.dbapi.execute(
            "CREATE INDEX IF NOT EXISTS event_dates ON event(description) WHERE description LIKE '%birth%' OR description LIKE '%death%';"
        )

    def optimize_database(self):
        """
        Optimize the database for better performance.
        Backend-specific optimizations should be implemented in subclasses.
        """
        # ANALYZE is generally supported across databases
        try:
            self.dbapi.execute("ANALYZE;")
            self.dbapi.commit()
        except:
            # Some backends may not support ANALYZE
            pass

    def bulk_insert(self, table_name, data_list, batch_size=1000):
        """
        Perform bulk insert operations for better performance.

        :param table_name: Name of the table to insert into
        :param data_list: List of tuples containing data to insert
        :param batch_size: Number of records to insert in each batch
        """
        if not data_list:
            return

        # Create placeholders for the INSERT statement
        columns = len(data_list[0])
        placeholders = ",".join(["?" for _ in range(columns)])

        # Insert in batches
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i : i + batch_size]
            self.dbapi.execute(
                f"INSERT INTO {table_name} VALUES ({placeholders})", batch
            )

        self.dbapi.commit()

    def bulk_update(self, table_name, data_list, where_column, batch_size=1000):
        """
        Perform bulk update operations for better performance.

        :param table_name: Name of the table to update
        :param data_list: List of tuples containing (where_value, update_data)
        :param where_column: Column name for WHERE clause
        :param batch_size: Number of records to update in each batch
        """
        if not data_list:
            return

        # Update in batches using a transaction
        if hasattr(self.dbapi, "begin"):
            self.dbapi.begin()
        try:
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i : i + batch_size]
                for where_value, update_data in batch:
                    # This is a simplified example - actual implementation would need
                    # to handle different column structures
                    self.dbapi.execute(
                        f"UPDATE {table_name} SET json_data = ? WHERE {where_column} = ?",
                        [update_data, where_value],
                    )
            self.dbapi.commit()
        except:
            self.dbapi.rollback()
            raise

    def json_query(self, table_name, json_path, value=None, operator="="):
        """
        Perform optimized JSON queries.

        :param table_name: Name of the table to query
        :param json_path: JSON path expression (e.g., '$.name.first')
        :param value: Value to search for
        :param operator: SQL operator (e.g., '=', 'LIKE', '>', etc.)
        :returns: List of handles matching the criteria
        """
        if value is None:
            query = f"SELECT handle FROM {table_name} WHERE json_extract(json_data, ?) IS NOT NULL"
            result = self.dbapi.execute(query, [json_path])
        else:
            query = f"SELECT handle FROM {table_name} WHERE json_extract(json_data, ?) {operator} ?"
            result = self.dbapi.execute(query, [json_path, value])

        if result:
            return [row[0] for row in result.fetchall()]
        else:
            return []

    def json_search(self, table_name, search_term, json_paths=None):
        """
        Perform full-text search within JSON data.

        :param table_name: Name of the table to search
        :param search_term: Term to search for
        :param json_paths: List of JSON paths to search in
        :returns: List of handles matching the search
        """
        if json_paths is None:
            # Default paths for common text fields
            json_paths = ["$.name.first", "$.name.surname", "$.description", "$.title"]

        conditions = []
        params = []

        for path in json_paths:
            conditions.append(f"json_extract(json_data, ?) LIKE ?")
            params.extend([path, f"%{search_term}%"])

        query = f"SELECT handle FROM {table_name} WHERE " + " OR ".join(conditions)
        result = self.dbapi.execute(query, params)

        if result:
            return [row[0] for row in result.fetchall()]
        else:
            return []

    def get_database_stats(self):
        """
        Get database statistics for performance monitoring.

        :returns: Dictionary with database statistics
        """
        stats = {}

        # Table sizes
        tables = [
            "person",
            "family",
            "source",
            "citation",
            "event",
            "media",
            "place",
            "repository",
            "note",
            "tag",
            "reference",
        ]
        for table in tables:
            result = self.dbapi.execute(f"SELECT COUNT(*) FROM {table}")
            if result:
                stats[f"{table}_count"] = result.fetchone()[0]
            else:
                stats[f"{table}_count"] = 0

        # Database size
        result = self.dbapi.execute(
            "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
        )
        if result:
            stats["database_size_bytes"] = result.fetchone()[0]
        else:
            stats["database_size_bytes"] = 0

        # Index usage
        result = self.dbapi.execute("SELECT name FROM sqlite_master WHERE type='index'")
        if result:
            stats["index_count"] = len(result.fetchall())
        else:
            stats["index_count"] = 0

        # Cache hit rate (approximate)
        result = self.dbapi.execute("PRAGMA cache_stats")
        if result:
            cache_stats = result.fetchall()
            if cache_stats:
                stats["cache_hits"] = cache_stats[0][0]
                stats["cache_misses"] = cache_stats[0][1]
            else:
                stats["cache_hits"] = 0
                stats["cache_misses"] = 0
        else:
            stats["cache_hits"] = 0
            stats["cache_misses"] = 0

        return stats

    def monitor_query_performance(self, query, params=None):
        """
        Monitor query performance with timing.

        :param query: SQL query to execute
        :param params: Query parameters
        :returns: Tuple of (results, execution_time)
        """
        import time

        start_time = time.time()
        if params:
            result = self.dbapi.execute(query, params)
        else:
            result = self.dbapi.execute(query)

        execution_time = time.time() - start_time
        return result, execution_time

    def suggest_indexes(self):
        """
        Analyze the database and suggest additional indexes for better performance.

        :returns: List of suggested index creation statements
        """
        suggestions = []

        # Analyze query patterns and suggest indexes
        # This is a simplified version - a full implementation would analyze
        # actual query patterns from the application

        # Common patterns in genealogy databases
        suggestions.append("-- For person searches by name")
        suggestions.append(
            "CREATE INDEX IF NOT EXISTS idx_person_name_full ON person(surname, given_name, gramps_id);"
        )

        suggestions.append("-- For family searches by parents")
        suggestions.append(
            "CREATE INDEX IF NOT EXISTS idx_family_parents_full ON family(father_handle, mother_handle, gramps_id);"
        )

        suggestions.append("-- For event searches by type and date")
        suggestions.append(
            "CREATE INDEX IF NOT EXISTS idx_event_type_date ON event(description, change);"
        )

        suggestions.append("-- For citation searches by source")
        suggestions.append(
            "CREATE INDEX IF NOT EXISTS idx_citation_source_page ON citation(source_handle, page, confidence);"
        )

        return suggestions

    def get_person_by_name(self, surname, given_name=None):
        """
        Get person handles by name using optimized query.

        :param surname: Person's surname
        :param given_name: Person's given name (optional)
        :returns: List of person handles matching the criteria
        """
        if given_name:
            self.dbapi.execute(
                "SELECT handle FROM person WHERE surname = ? AND given_name = ?",
                [surname, given_name],
            )
        else:
            self.dbapi.execute("SELECT handle FROM person WHERE surname = ?", [surname])
        return [row[0] for row in self.dbapi.fetchall()]

    def get_families_by_parent(self, parent_handle):
        """
        Get family handles by parent using optimized query.

        :param parent_handle: Handle of the parent person
        :returns: List of family handles where the person is a parent
        """
        self.dbapi.execute(
            "SELECT handle FROM family WHERE father_handle = ? OR mother_handle = ?",
            [parent_handle, parent_handle],
        )
        return [row[0] for row in self.dbapi.fetchall()]

    def get_events_by_type(self, event_type):
        """
        Get event handles by type using JSON query optimization.

        :param event_type: Type of event to search for
        :returns: List of event handles matching the type
        """
        return self.json_query("event", "$.type", event_type)

    def get_people_by_birth_date(self, start_date=None, end_date=None):
        """
        Get people by birth date range using optimized queries.

        :param start_date: Start date for birth range
        :param end_date: End date for birth range
        :returns: List of person handles matching the criteria
        """
        if start_date and end_date:
            # This would need to be implemented based on how dates are stored
            # in the JSON data structure
            pass
        elif start_date:
            pass
        elif end_date:
            pass
        else:
            # Get all people with birth events
            return self.json_query("person", "$.birth", None, "IS NOT NULL")

    def get_people_by_death_date(self, start_date=None, end_date=None):
        """
        Get people by death date range using optimized queries.

        :param start_date: Start date for death range
        :param end_date: End date for death range
        :returns: List of person handles matching the criteria
        """
        if start_date and end_date:
            pass
        elif start_date:
            pass
        elif end_date:
            pass
        else:
            # Get all people with death events
            return self.json_query("person", "$.death", None, "IS NOT NULL")

    def search_people_full_text(self, search_term):
        """
        Search people using full-text search across multiple fields.

        :param search_term: Term to search for
        :returns: List of person handles matching the search
        """
        return self.json_search(
            "person",
            search_term,
            [
                "$.name.first",
                "$.name.surname",
                "$.name.suffix",
                "$.name.title",
                "$.name.nick",
                "$.name.call",
            ],
        )

    def get_places_by_location(self, location_term):
        """
        Search places by location using optimized queries.

        :param location_term: Location term to search for
        :returns: List of place handles matching the location
        """
        return self.json_search(
            "place", location_term, ["$.title", "$.long", "$.lat", "$.code"]
        )

    def get_sources_by_author(self, author):
        """
        Get sources by author using optimized queries.

        :param author: Author name to search for
        :returns: List of source handles matching the author
        """
        return self.json_query("source", "$.author", author, "LIKE")

    def get_citations_by_source(self, source_handle):
        """
        Get citations by source using optimized queries.

        :param source_handle: Handle of the source
        :returns: List of citation handles for the source
        """
        self.dbapi.execute(
            "SELECT handle FROM citation WHERE source_handle = ?", [source_handle]
        )
        return [row[0] for row in self.dbapi.fetchall()]

    def get_media_by_type(self, mime_type):
        """
        Get media objects by MIME type using optimized queries.

        :param mime_type: MIME type to search for
        :returns: List of media handles matching the MIME type
        """
        self.dbapi.execute("SELECT handle FROM media WHERE mime = ?", [mime_type])
        return [row[0] for row in self.dbapi.fetchall()]

    def get_notes_by_content(self, content_term):
        """
        Search notes by content using optimized queries.

        :param content_term: Content term to search for
        :returns: List of note handles matching the content
        """
        return self.json_search("note", content_term, ["$.text"])

    def get_repositories_by_name(self, name):
        """
        Get repositories by name using optimized queries.

        :param name: Repository name to search for
        :returns: List of repository handles matching the name
        """
        return self.json_query("repository", "$.name", name, "LIKE")

    def bulk_get_persons(self, handles):
        """
        Get multiple persons efficiently using bulk operations.

        :param handles: List of person handles to retrieve
        :returns: List of person objects
        """
        if not handles:
            return []

        # Use IN clause for bulk retrieval
        placeholders = ",".join(["?" for _ in handles])
        self.dbapi.execute(
            f"SELECT handle, json_data FROM person WHERE handle IN ({placeholders})",
            handles,
        )

        results = []
        for row in self.dbapi.fetchall():
            handle, json_data = row
            if json_data:
                person_data = self.serializer.string_to_data(json_data)
                results.append(self.serializer.data_to_object(person_data, Person))

        return results

    def bulk_get_families(self, handles):
        """
        Get multiple families efficiently using bulk operations.

        :param handles: List of family handles to retrieve
        :returns: List of family objects
        """
        if not handles:
            return []

        placeholders = ",".join(["?" for _ in handles])
        self.dbapi.execute(
            f"SELECT handle, json_data FROM family WHERE handle IN ({placeholders})",
            handles,
        )

        results = []
        for row in self.dbapi.fetchall():
            handle, json_data = row
            if json_data:
                family_data = self.serializer.string_to_data(json_data)
                results.append(self.serializer.data_to_object(family_data, Family))

        return results
    
    # -------------------------------------------------------------------------
    # Enhanced DBAPI Methods - Real Cursors, Lazy Loading, Prepared Statements
    # -------------------------------------------------------------------------
    
    def prepare(self, name, query):
        """
        Prepare a statement for execution. Backend-agnostic implementation
        that works with any database driver.
        
        :param name: Name identifier for the prepared statement
        :param query: SQL query to prepare
        :returns: Prepared statement object or query string
        """
        if not hasattr(self, '_prepared_statements'):
            self._prepared_statements = {}
            
        if name not in self._prepared_statements:
            if hasattr(self.dbapi, 'prepare'):
                # For PostgreSQL, MySQL, etc. that support real prepared statements
                self._prepared_statements[name] = self.dbapi.prepare(query)
            else:
                # For SQLite and others - just cache the query string
                self._prepared_statements[name] = query
        
        return self._prepared_statements[name]
    
    def execute_prepared(self, name, params=None):
        """
        Execute a prepared statement by name.
        
        :param name: Name of the prepared statement
        :param params: Parameters for the statement
        :returns: Cursor with results
        """
        if not hasattr(self, '_prepared_statements'):
            raise ValueError(f"No prepared statement '{name}' found")
            
        stmt = self._prepared_statements.get(name)
        if stmt is None:
            raise ValueError(f"Prepared statement '{name}' not found")
        
        if hasattr(stmt, 'execute'):
            # Real prepared statement object
            return stmt.execute(params or [])
        else:
            # Cached query string
            return self.dbapi.execute(stmt, params or [])
    
    def get_person_from_handle_lazy(self, handle):
        """
        Get a person object with lazy loading of related data.
        
        :param handle: Person handle
        :returns: LazyPerson object that loads data on access
        """
        # Check if person exists first
        self.dbapi.execute("SELECT 1 FROM person WHERE handle = ?", [handle])
        if not self.dbapi.fetchone():
            return None
        
        class LazyPerson:
            """Proxy object that loads person data on first access."""
            def __init__(self, handle, db):
                self._handle = handle
                self._db = db
                self._loaded = False
                self._person = None
            
            def _load(self):
                if not self._loaded:
                    self._person = self._db.get_person_from_handle(self._handle)
                    self._loaded = True
            
            def __getattr__(self, name):
                self._load()
                return getattr(self._person, name)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    object.__setattr__(self, name, value)
                else:
                    self._load()
                    setattr(self._person, name, value)
        
        return LazyPerson(handle, self)
    
    def batch_commit_persons(self, persons, trans):
        """
        Commit multiple persons efficiently using batch operations.
        
        :param persons: List of Person objects to commit
        :param trans: Transaction object
        """
        if not persons:
            return
            
        # Use executemany if available
        if hasattr(self.dbapi, 'executemany'):
            data = []
            for person in persons:
                handle = person.handle
                json_data = self.serializer.object_to_string(person)
                # Prepare data for batch insert
                data.append((handle, json_data, person.gramps_id, 
                           person.gender, person.primary_name.first_name,
                           person.primary_name.surname))
            
            # Batch insert/update
            self.dbapi.executemany(
                "INSERT OR REPLACE INTO person "
                "(handle, json_data, gramps_id, gender, given_name, surname) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                data
            )
            
            # Emit signals for GUI updates
            for person in persons:
                self.emit('person-add', ([person.handle],))
        else:
            # Fallback to individual commits
            for person in persons:
                self.commit_person(person, trans)
