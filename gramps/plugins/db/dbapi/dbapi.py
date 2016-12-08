#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016      Nick Hall
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import shutil
import time
import sys
import pickle
from operator import itemgetter
import logging

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.db.dbconst import (DBLOGNAME, DBBACKEND, KEY_TO_NAME_MAP,
                                   TXNADD, TXNUPD, TXNDEL,
                                   PERSON_KEY, FAMILY_KEY, SOURCE_KEY,
                                   EVENT_KEY, MEDIA_KEY, PLACE_KEY, NOTE_KEY,
                                   TAG_KEY, CITATION_KEY, REPOSITORY_KEY,
                                   REFERENCE_KEY)
from gramps.gen.db.generic import DbGeneric
from gramps.gen.lib import (Tag, Media, Person, Family, Source,
                            Citation, Event, Place, Repository, Note)
from gramps.gen.lib.genderstats import GenderStats
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

LOG = logging.getLogger(".dbapi")
_LOG = logging.getLogger(DBLOGNAME)

class DBAPI(DbGeneric):
    """
    Database backends class for DB-API 2.0 databases
    """
    @classmethod
    def get_class_summary(cls):
        """
        Return a diction of information about this database.
        """
        summary = {
            "DB-API version": "2.0",
            "Database type": cls.__name__,
        }
        return summary

    def get_schema_version(self, directory=None):
        """
        Get the version of the schema that the database was created
        under. Assumes 18, if not found.
        """
        if directory is None:
            directory = self._directory
        version = 18
        if directory:
            versionpath = os.path.join(directory, "schemaversion.txt")
            if os.path.exists(versionpath):
                with open(versionpath, "r") as version_file:
                    version = version_file.read()
                version = int(version)
            else:
                LOG.info("Missing '%s'. Assuming version 18.", versionpath)
        return version

    def write_version(self, directory):
        """Write files for a newly created DB."""
        _LOG.debug("Write schema version file to %s", str(self.VERSION[0]))
        versionpath = os.path.join(directory, "schemaversion.txt")
        with open(versionpath, "w") as version_file:
            version_file.write(str(self.VERSION[0]))

        versionpath = os.path.join(directory, str(DBBACKEND))
        _LOG.debug("Write database backend file to 'dbapi'")
        with open(versionpath, "w") as version_file:
            version_file.write("dbapi")
        # Write settings.py and settings.ini:
        settings_py = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "settings.py")
        settings_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "settings.ini")
        LOG.debug("Copy settings.py from: " + settings_py)
        LOG.debug("Copy settings.ini from: " + settings_py)
        shutil.copy2(settings_py, directory)
        shutil.copy2(settings_ini, directory)

    def _initialize(self, directory):
        # Run code from directory
        from gramps.gen.utils.configmanager import ConfigManager
        config_file = os.path.join(directory, 'settings.ini')
        config_mgr = ConfigManager(config_file)
        config_mgr.register('database.dbtype', 'sqlite')
        config_mgr.register('database.dbname', 'gramps')
        config_mgr.register('database.host', 'localhost')
        config_mgr.register('database.user', 'user')
        config_mgr.register('database.password', 'password')
        config_mgr.register('database.port', 'port')
        config_mgr.load() # load from settings.ini
        settings = {
            "__file__":
            os.path.join(directory, "settings.py"),
            "config": config_mgr
        }
        settings_file = os.path.join(directory, "settings.py")
        with open(settings_file) as fp:
            code = compile(fp.read(), settings_file, 'exec')
            exec(code, globals(), settings)
        self.dbapi = settings["dbapi"]

        # We use the existence of the person table as a proxy for the database
        # being new
        if not self.dbapi.table_exists("person"):
            self._create_schema()

    def _create_schema(self):
        """
        Create and update schema.
        """
        # make sure schema is up to date:
        self.dbapi.execute('CREATE TABLE person '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'given_name TEXT, '
                           'surname TEXT, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE family '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'father_handle VARCHAR(50), '
                           'mother_handle VARCHAR(50), '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE source '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE citation '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE event '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE media '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE place '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'enclosed_by VARCHAR(50), '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE repository '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE note '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'gramps_id TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE tag '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        # Secondary:
        self.dbapi.execute('CREATE TABLE reference '
                           '('
                           'obj_handle VARCHAR(50), '
                           'obj_class TEXT, '
                           'ref_handle VARCHAR(50), '
                           'ref_class TEXT'
                           ')')
        self.dbapi.execute('CREATE TABLE name_group '
                           '('
                           'name VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'grouping TEXT'
                           ')')
        self.dbapi.execute('CREATE TABLE metadata '
                           '('
                           'setting VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'value BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE gender_stats '
                           '('
                           'given_name TEXT, '
                           'female INTEGER, '
                           'male INTEGER, '
                           'unknown INTEGER'
                           ')')

        self._create_secondary_columns()

        ## Indices:
        self.dbapi.execute('CREATE INDEX person_gramps_id '
                           'ON person(gramps_id)')
        self.dbapi.execute('CREATE INDEX person_surname '
                           'ON person(surname)')
        self.dbapi.execute('CREATE INDEX person_given_name '
                           'ON person(given_name)')
        self.dbapi.execute('CREATE INDEX source_title '
                           'ON source(title)')
        self.dbapi.execute('CREATE INDEX source_gramps_id '
                           'ON source(gramps_id)')
        self.dbapi.execute('CREATE INDEX citation_page '
                           'ON citation(page)')
        self.dbapi.execute('CREATE INDEX citation_gramps_id '
                           'ON citation(gramps_id)')
        self.dbapi.execute('CREATE INDEX media_desc '
                           'ON media(desc)')
        self.dbapi.execute('CREATE INDEX media_gramps_id '
                           'ON media(gramps_id)')
        self.dbapi.execute('CREATE INDEX place_title '
                           'ON place(title)')
        self.dbapi.execute('CREATE INDEX place_enclosed_by '
                           'ON place(enclosed_by)')
        self.dbapi.execute('CREATE INDEX place_gramps_id '
                           'ON place(gramps_id)')
        self.dbapi.execute('CREATE INDEX tag_name '
                           'ON tag(name)')
        self.dbapi.execute('CREATE INDEX reference_ref_handle '
                           'ON reference(ref_handle)')
        self.dbapi.execute('CREATE INDEX family_gramps_id '
                           'ON family(gramps_id)')
        self.dbapi.execute('CREATE INDEX event_gramps_id '
                           'ON event(gramps_id)')
        self.dbapi.execute('CREATE INDEX repository_gramps_id '
                           'ON repository(gramps_id)')
        self.dbapi.execute('CREATE INDEX note_gramps_id '
                           'ON note(gramps_id)')
        self.dbapi.execute('CREATE INDEX reference_obj_handle '
                           'ON reference(obj_handle)')


    def _close(self):
        self.dbapi.close()

    def _txn_begin(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db BEGIN;
        """
        _LOG.debug("    DBAPI %s transaction begin", hex(id(self)))
        self.dbapi.begin()

    def _txn_commit(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db END;
        """
        _LOG.debug("    DBAPI %s transaction commit", hex(id(self)))
        self.dbapi.commit()

    def _txn_abort(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db ROLLBACK;
        """
        self.dbapi.rollback()

    def transaction_begin(self, transaction):
        """
        Transactions are handled automatically by the db layer.
        """
        _LOG.debug("    %sDBAPI %s transaction begin for '%s'",
                   "Batch " if transaction.batch else "",
                   hex(id(self)), transaction.get_description())
        self.transaction = transaction
        self.dbapi.begin()
        return transaction

    def transaction_commit(self, txn):
        """
        Executed at the end of a transaction.
        """
        _LOG.debug("    %sDBAPI %s transaction commit for '%s'",
                   "Batch " if txn.batch else "",
                   hex(id(self)), txn.get_description())

        action = {TXNADD: "-add",
                  TXNUPD: "-update",
                  TXNDEL: "-delete",
                  None: "-delete"}
        if txn.batch:
            # FIXME: need a User GUI update callback here:
            self.reindex_reference_map(lambda percent: percent)
        self.dbapi.commit()
        if not txn.batch:
            # Now, emit signals:
            for (obj_type_val, txn_type_val) in list(txn):
                if obj_type_val == REFERENCE_KEY:
                    continue
                if txn_type_val == TXNDEL:
                    handles = [handle for (handle, data) in
                               txn[(obj_type_val, txn_type_val)]]
                else:
                    handles = [handle for (handle, data) in
                               txn[(obj_type_val, txn_type_val)]
                               if (handle, None)
                               not in txn[(obj_type_val, TXNDEL)]]
                if handles:
                    signal = KEY_TO_NAME_MAP[
                        obj_type_val] + action[txn_type_val]
                    self.emit(signal, (handles, ))
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

    def _get_metadata(self, key, default=[]):
        """
        Get an item from the database.

        Default is an empty list, which is a mutable and
        thus a bad default (pylint will complain).

        However, it is just used as a value, and not altered, so
        its use here is ok.
        """
        self.dbapi.execute(
            "SELECT value FROM metadata WHERE setting = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])
        elif default == []:
            return []
        else:
            return default

    def _set_metadata(self, key, value):
        """
        key: string
        value: item, will be serialized here
        """
        self.dbapi.execute("SELECT 1 FROM metadata WHERE setting = ?", [key])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute(
                "UPDATE metadata SET value = ? WHERE setting = ?",
                [pickle.dumps(value), key])
        else:
            self.dbapi.execute(
                "INSERT INTO metadata (setting, value) VALUES (?, ?)",
                [key, pickle.dumps(value)])

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        self.dbapi.execute("SELECT name FROM name_group ORDER BY name")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_name_group_mapping(self, key):
        """
        Return the default grouping name for a surname.
        """
        self.dbapi.execute(
            "SELECT grouping FROM name_group WHERE name = ?", [key])
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
            self.dbapi.execute("SELECT handle FROM person "
                               "ORDER BY surname COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle FROM person")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_family_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        If sort_handles is True, the list is sorted by surnames.
        """
        if sort_handles:
            sql = ("SELECT family.handle " +
                   "FROM family " +
                   "LEFT JOIN person AS father " +
                   "ON family.father_handle = father.handle " +
                   "LEFT JOIN person AS mother " +
                   "ON family.mother_handle = mother.handle " +
                   "ORDER BY (CASE WHEN father.handle IS NULL " +
                   "THEN mother.surname " +
                   "ELSE father.surname " +
                   "END), " +
                   "(CASE WHEN family.handle IS NULL " +
                   "THEN mother.given_name " +
                   "ELSE father.given_name " +
                   "END) " +
                   "COLLATE glocale")
            self.dbapi.execute(sql)
        else:
            self.dbapi.execute("SELECT handle FROM family")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM event")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_citation_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        If sort_handles is True, the list is sorted by Citation title.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM citation "
                               "ORDER BY page COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle FROM citation")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_source_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Source in
        the database.

        If sort_handles is True, the list is sorted by Source title.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM source "
                               "ORDER BY title COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle from source")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_place_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Place in
        the database.

        If sort_handles is True, the list is sorted by Place title.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM place "
                               "ORDER BY title COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle FROM place")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        self.dbapi.execute("SELECT handle FROM repository")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_media_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        If sort_handles is True, the list is sorted by title.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM media "
                               "ORDER BY desc COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle FROM media")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM note")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_tag_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Tag in
        the database.

        If sort_handles is True, the list is sorted by Tag name.
        """
        if sort_handles:
            self.dbapi.execute("SELECT handle FROM tag "
                               "ORDER BY name COLLATE glocale")
        else:
            self.dbapi.execute("SELECT handle FROM tag")
        rows = self.dbapi.fetchall()
        return [bytes(row[0], "utf-8") for row in rows]

    def get_tag_from_name(self, name):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        """
        self.dbapi.execute("SELECT blob_data FROM tag WHERE name = ?", [name])
        row = self.dbapi.fetchone()
        if row:
            return Tag.create(pickle.loads(row[0]))
        return None

    def get_number_of(self, obj_key):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT count(1) FROM %s" % table
        self.dbapi.execute(sql)
        row = self.dbapi.fetchone()
        return row[0]

    def has_name_group_key(self, key):
        """
        Return if a key exists in the name_group table.
        """
        self.dbapi.execute("SELECT grouping FROM name_group WHERE name = ?",
                           [key])
        row = self.dbapi.fetchone()
        return True if row else False

    def set_name_group_mapping(self, name, grouping):
        """
        Set the default grouping name for a surname.
        """
        self.dbapi.execute("SELECT 1 FROM name_group WHERE name = ?",
                           [name])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute("DELETE FROM name_group WHERE name = ?",
                               [name])
        self.dbapi.execute(
            "INSERT INTO name_group (name, grouping) VALUES(?, ?)",
            [name, grouping])

    def _commit_base(self, obj, obj_key, trans, change_time):
        """
        Commit the specified object to the database, storing the changes as
        part of the transaction.
        """
        old_data = None
        obj.change = int(change_time or time.time())
        table = KEY_TO_NAME_MAP[obj_key]

        if self.has_handle(obj_key, obj.handle):
            old_data = self.get_raw_data(obj_key, obj.handle)
            # update the object:
            sql = "UPDATE %s SET blob_data = ? WHERE handle = ?" % table
            self.dbapi.execute(sql,
                               [pickle.dumps(obj.serialize()),
                                obj.handle])
        else:
            # Insert the object:
            sql = ("INSERT INTO %s (handle, blob_data) VALUES (?, ?)") % table
            self.dbapi.execute(sql,
                               [obj.handle,
                                pickle.dumps(obj.serialize())])
        self._update_secondary_values(obj)
        if not trans.batch:
            self._update_backlinks(obj, trans)
            if old_data:
                trans.add(obj_key, TXNUPD, obj.handle,
                          old_data,
                          obj.serialize())
            else:
                trans.add(obj_key, TXNADD, obj.handle,
                          None,
                          obj.serialize())

        return old_data

    def _update_backlinks(self, obj, transaction):

        # Find existing references
        sql = ("SELECT ref_class, ref_handle " +
               "FROM reference WHERE obj_handle = ?")
        self.dbapi.execute(sql, [obj.handle])
        existing_references = set(self.dbapi.fetchall())

        # Once we have the list of rows that already have a reference
        # we need to compare it with the list of objects that are
        # still references from the primary object.
        current_references = set(obj.get_referenced_handles_recursively())
        no_longer_required_references = existing_references.difference(
                                                            current_references)
        new_references = current_references.difference(existing_references)

        # Delete the existing references
        self.dbapi.execute("DELETE FROM reference WHERE obj_handle = ?",
                           [obj.handle])

        # Now, add the current ones
        for (ref_class_name, ref_handle) in current_references:
            sql = ("INSERT INTO reference " +
                   "(obj_handle, obj_class, ref_handle, ref_class)" +
                   "VALUES(?, ?, ?, ?)")
            self.dbapi.execute(sql, [obj.handle, obj.__class__.__name__,
                                     ref_handle, ref_class_name])

        if not transaction.batch:
            # Add new references to the transaction
            for (ref_class_name, ref_handle) in new_references:
                key = (obj.handle, ref_handle)
                data = (obj.handle, obj.__class__.__name__,
                        ref_handle, ref_class_name)
                transaction.add(REFERENCE_KEY, TXNADD, key, None, data)

            # Add old references to the transaction
            for (ref_class_name, ref_handle) in no_longer_required_references:
                key = (obj.handle, ref_handle)
                old_data = (obj.handle, obj.__class__.__name__,
                            ref_handle, ref_class_name)
                transaction.add(REFERENCE_KEY, TXNDEL, key, old_data, None)

    def _do_remove(self, handle, transaction, obj_key):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        if self.readonly or not handle:
            return
        if self.has_handle(obj_key, handle):
            table = KEY_TO_NAME_MAP[obj_key]
            sql = "DELETE FROM %s WHERE handle = ?" % table
            self.dbapi.execute(sql, [handle])
            if not transaction.batch:
                data = self.get_raw_data(obj_key, handle)
                transaction.add(obj_key, TXNDEL, handle, data, None)

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
        self.dbapi.execute("SELECT obj_class, obj_handle "
                           "FROM reference "
                           "WHERE ref_handle = ?",
                           [handle])
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

    def _iter_handles(self, obj_key):
        """
        Return an iterator over handles in the database
        """
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT handle FROM %s" % table
        self.dbapi.execute(sql)
        rows = self.dbapi.fetchall()
        for row in rows:
            yield row[0]

    def _iter_raw_data(self, obj_key):
        """
        Return an iterator over raw data in the database.
        """
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT handle, blob_data FROM %s" % table
        with self.dbapi.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany()
            while rows:
                for row in rows:
                    yield (row[0].encode('utf8'), pickle.loads(row[1]))
                rows = cursor.fetchmany()

    def _iter_raw_place_tree_data(self):
        """
        Return an iterator over raw data in the place hierarchy.
        """
        to_do = ['']
        sql = 'SELECT handle, blob_data FROM place WHERE enclosed_by = ?'
        while to_do:
            handle = to_do.pop()
            self.dbapi.execute(sql, [handle])
            rows = self.dbapi.fetchall()
            for row in rows:
                to_do.append(row[0])
                yield (row[0].encode('utf8'), pickle.loads(row[1]))

    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.
        """
        callback(4)
        self.dbapi.execute("DELETE FROM reference")
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
                for found_handle, val in cursor:
                    obj = class_func.create(val)
                    references = set(obj.get_referenced_handles_recursively())
                    # handle addition of new references
                    for (ref_class_name, ref_handle) in references:
                        self.dbapi.execute(
                            "INSERT INTO reference "
                            "(obj_handle, obj_class, ref_handle, ref_class) "
                            "VALUES (?, ?, ?, ?)",
                            [obj.handle,
                             obj.__class__.__name__,
                             ref_handle,
                             ref_class_name])
        callback(5)

    def rebuild_secondary(self, update):
        """
        Rebuild secondary indices
        """
        # First, expand blob to individual fields:
        self._update_secondary_values()
        # Next, rebuild stats:
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)

    def has_handle(self, obj_key, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT 1 FROM %s WHERE handle = ?" % table
        self.dbapi.execute(sql, [handle])
        return self.dbapi.fetchone() is not None

    def has_gramps_id(self, obj_key, gramps_id):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT 1 FROM %s WHERE gramps_id = ?" % table
        self.dbapi.execute(sql, [gramps_id])
        return self.dbapi.fetchone() != None

    def get_gramps_ids(self, obj_key):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT gramps_id FROM %s" % table
        self.dbapi.execute(sql)
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_raw_data(self, obj_key, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT blob_data FROM %s WHERE handle = ?" % table
        self.dbapi.execute(sql, [handle])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def _get_raw_from_id_data(self, obj_key, gramps_id):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT blob_data FROM %s WHERE gramps_id = ?" % table
        self.dbapi.execute(sql, [gramps_id])
        row = self.dbapi.fetchone()
        if row:
            return pickle.loads(row[0])

    def get_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        """
        self.dbapi.execute("SELECT given_name, female, male, unknown "
                           "FROM gender_stats")
        gstats = {}
        for row in self.dbapi.fetchall():
            gstats[row[0]] = (row[1], row[2], row[3])
        return gstats

    def save_gender_stats(self, gstats):
        self.dbapi.execute("DELETE FROM gender_stats")
        for key in gstats.stats:
            female, male, unknown = gstats.stats[key]
            self.dbapi.execute("INSERT INTO gender_stats "
                               "(given_name, female, male, unknown) "
                               "VALUES (?, ?, ?, ?)",
                               [key, female, male, unknown])

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        self.dbapi.execute("SELECT DISTINCT surname "
                           "FROM person "
                           "ORDER BY surname")
        surname_list = []
        for row in self.dbapi.fetchall():
            surname_list.append(row[0])
        return surname_list

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

    def _create_secondary_columns(self):
        """
        Create secondary columns.
        """
        LOG.info("Creating secondary columns...")
        for table in self.get_table_func():
            if not hasattr(self.get_table_func(table, "class_func"),
                           "get_secondary_fields"):
                continue
            table_name = table.lower()
            for field_pair in self.get_table_func(
                    table, "class_func").get_secondary_fields():
                field, python_type = field_pair
                field = self._hash_name(table, field)
                sql_type = self._sql_type(python_type)
                try:
                    # test to see if it exists:
                    self.dbapi.execute("SELECT %s FROM %s LIMIT 1"
                                       % (field, table_name))
                    LOG.info("    Table %s, field %s is up to date",
                             table, field)
                except:
                    # if not, let's add it
                    LOG.info("    Table %s, field %s was added",
                             table, field)
                    self.dbapi.execute("ALTER TABLE %s ADD COLUMN %s %s"
                                       % (table_name, field, sql_type))

    def _update_secondary_values(self, obj):
        """
        Given a primary object update its secondary field values
        in the database.
        Does not commit.
        """
        table = obj.__class__.__name__
        fields = self.get_table_func(table, "class_func").get_secondary_fields()
        fields = [field for (field, direction) in fields]
        sets = []
        values = []
        for field in fields:
            value = obj.get_field(field, self, ignore_errors=True)
            field = self._hash_name(obj.__class__.__name__, field)
            sets.append("%s = ?" % field)
            values.append(value)

        # Derived fields
        if table == 'Person':
            given_name, surname = self._get_person_data(obj)
            sets.append("given_name = ?")
            values.append(given_name)
            sets.append("surname = ?")
            values.append(surname)
        if table == 'Place':
            handle = self._get_place_data(obj)
            sets.append("enclosed_by = ?")
            values.append(handle)

        if len(values) > 0:
            table_name = table.lower()
            self.dbapi.execute("UPDATE %s SET %s where handle = ?"
                               % (table_name, ", ".join(sets)),
                               self._sql_cast_list(table, sets, values)
                               + [obj.handle])

    def _sql_cast_list(self, table, fields, values):
        """
        Given a list of field names and values, return the values
        in the appropriate type.
        """
        return [v if not isinstance(v, bool) else int(v) for v in values]

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
