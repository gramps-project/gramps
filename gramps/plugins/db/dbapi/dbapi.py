#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016-2017 Nick Hall
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import time
import pickle
import logging

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.db.dbconst import (DBLOGNAME, DBBACKEND, KEY_TO_NAME_MAP,
                                   KEY_TO_CLASS_MAP, TXNADD, TXNUPD, TXNDEL,
                                   PERSON_KEY, FAMILY_KEY, SOURCE_KEY,
                                   EVENT_KEY, MEDIA_KEY, PLACE_KEY, NOTE_KEY,
                                   TAG_KEY, CITATION_KEY, REPOSITORY_KEY,
                                   REFERENCE_KEY)
from gramps.gen.db.generic import DbGeneric
from gramps.gen.lib import (Tag, Media, Person, Family, Source,
                            Citation, Event, Place, Repository, Note)
from gramps.gen.lib.genderstats import GenderStats
from gramps.gen.const import GRAMPS_LOCALE as glocale

LOG = logging.getLogger(".dbapi")
_LOG = logging.getLogger(DBLOGNAME)

class DBAPI(DbGeneric):
    """
    Database backends class for DB-API 2.0 databases
    """
    def _initialize(self, directory, username, password):
        raise NotImplementedError

    def _schema_exists(self):
        """
        Check to see if the schema exists.

        We use the existence of the person table as a proxy for the database
        being new.
        """
        return self.dbapi.table_exists("person")

    def _create_schema(self):
        """
        Create and update schema.
        """
        self.dbapi.begin()

        # make sure schema is up to date:
        self.dbapi.execute('CREATE TABLE person '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'given_name TEXT, '
                           'surname TEXT, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE family '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE source '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE citation '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE event '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE media '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE place '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'enclosed_by VARCHAR(50), '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE repository '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
                           'blob_data BLOB'
                           ')')
        self.dbapi.execute('CREATE TABLE note '
                           '('
                           'handle VARCHAR(50) PRIMARY KEY NOT NULL, '
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

        self.dbapi.commit()

    def _close(self):
        self.dbapi.close()

    def _txn_begin(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db BEGIN;
        """
        if self.transaction == None:
            _LOG.debug("    DBAPI %s transaction begin", hex(id(self)))
            self.dbapi.begin()

    def _txn_commit(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db END;
        """
        if self.transaction == None:
            _LOG.debug("    DBAPI %s transaction commit", hex(id(self)))
            self.dbapi.commit()

    def _txn_abort(self):
        """
        Lowlevel interface to the backend transaction.
        Executes a db ROLLBACK;
        """
        if self.transaction == None:
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
            # do deletes and adds first
            for trans_type in [TXNDEL, TXNADD, TXNUPD]:
                for obj_type in range(11):
                    if obj_type != REFERENCE_KEY and \
                            (obj_type, trans_type) in txn:
                        if trans_type == TXNDEL:
                            handles = [handle for (handle, data) in
                                       txn[(obj_type, trans_type)]]
                        else:
                            handles = [handle for (handle, data) in
                                       txn[(obj_type, trans_type)]
                                       if (handle, None)
                                       not in txn[(obj_type, TXNDEL)]]
                        if handles:
                            signal = KEY_TO_NAME_MAP[
                                obj_type] + action[trans_type]
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
        self._txn_begin()
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
        self._txn_commit()

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM person '
                               'ORDER BY surname '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle FROM person")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            sql = ('SELECT family.handle ' +
                   'FROM family ' +
                   'LEFT JOIN person AS father ' +
                   'ON family.father_handle = father.handle ' +
                   'LEFT JOIN person AS mother ' +
                   'ON family.mother_handle = mother.handle ' +
                   'ORDER BY (CASE WHEN father.handle IS NULL ' +
                   'THEN mother.surname ' +
                   'ELSE father.surname ' +
                   'END), ' +
                   '(CASE WHEN family.handle IS NULL ' +
                   'THEN mother.given_name ' +
                   'ELSE father.given_name ' +
                   'END) ' +
                   'COLLATE "%s"' % locale.get_collation())
            self.dbapi.execute(sql)
        else:
            self.dbapi.execute("SELECT handle FROM family")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM event")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM citation '
                               'ORDER BY page '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle FROM citation")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM source '
                               'ORDER BY title '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle from source")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM place '
                               'ORDER BY title '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle FROM place")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        self.dbapi.execute("SELECT handle FROM repository")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_media_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        :param sort_handles: If True, the list is sorted by title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if sort_handles:
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM media '
                               'ORDER BY desc '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle FROM media")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.
        """
        self.dbapi.execute("SELECT handle FROM note")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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
            if locale != glocale:
                self.dbapi.check_collation(locale)

            self.dbapi.execute('SELECT handle FROM tag '
                               'ORDER BY name '
                               'COLLATE "%s"' % locale.get_collation())
        else:
            self.dbapi.execute("SELECT handle FROM tag")
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

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

    def _get_number_of(self, obj_key):
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
        self._txn_begin()
        self.dbapi.execute("SELECT 1 FROM name_group WHERE name = ?",
                           [name])
        row = self.dbapi.fetchone()
        if row:
            self.dbapi.execute("UPDATE name_group SET grouping=? "
                               "WHERE name = ?", [grouping, name])
        else:
            self.dbapi.execute(
                "INSERT INTO name_group (name, grouping) VALUES (?, ?)",
                [name, grouping])
        self._txn_commit()

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
        if self.readonly or not handle:
            return
        if self._has_handle(obj_key, handle):
            data = self._get_raw_data(obj_key, handle)
            obj_class = KEY_TO_CLASS_MAP[obj_key]
            self._remove_backlinks(obj_class, handle, transaction)
            table = KEY_TO_NAME_MAP[obj_key]
            sql = "DELETE FROM %s WHERE handle = ?" % table
            self.dbapi.execute(sql, [handle])
            if not transaction.batch:
                transaction.add(obj_key, TXNDEL, handle, data, None)

    def _remove_backlinks(self, obj_class, obj_handle, transaction):
        """
        Removes all references from this object (backlinks).
        """
        # collect backlinks from this object for undo
        self.dbapi.execute("SELECT ref_class, ref_handle " +
                           "FROM reference WHERE obj_handle = ?", [obj_handle])
        rows = self.dbapi.fetchall()
        # Now, delete backlinks from this object:
        self.dbapi.execute("DELETE FROM reference WHERE obj_handle = ?;",
                           [obj_handle])
        # Add old references to the transaction
        if not transaction.batch:
            for (ref_class_name, ref_handle) in rows:
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
                    yield (row[0], pickle.loads(row[1]))
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
                yield (row[0], pickle.loads(row[1]))

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

    def rebuild_secondary(self, callback=None):
        """
        Rebuild secondary indices
        """
        if self.readonly:
            return

        # First, expand blob to individual fields:
        self._txn_begin()
        index = 1
        for obj_type in ('Person', 'Family', 'Event', 'Place', 'Repository',
                         'Source', 'Citation', 'Media', 'Note', 'Tag'):
            for handle in self.method('get_%s_handles', obj_type)():
                obj = self.method('get_%s_from_handle', obj_type)(handle)
                self._update_secondary_values(obj)
            if callback:
                callback(index)
            index += 1
        self._txn_commit()
        if callback:
            callback(11)

        # Next, rebuild stats:
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)
        if callback:
            callback(12)

    def _has_handle(self, obj_key, handle):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT 1 FROM %s WHERE handle = ?" % table
        self.dbapi.execute(sql, [handle])
        return self.dbapi.fetchone() is not None

    def _has_gramps_id(self, obj_key, gramps_id):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT 1 FROM %s WHERE gramps_id = ?" % table
        self.dbapi.execute(sql, [gramps_id])
        return self.dbapi.fetchone() != None

    def _get_gramps_ids(self, obj_key):
        table = KEY_TO_NAME_MAP[obj_key]
        sql = "SELECT gramps_id FROM %s" % table
        self.dbapi.execute(sql)
        rows = self.dbapi.fetchall()
        return [row[0] for row in rows]

    def _get_raw_data(self, obj_key, handle):
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
        self._txn_begin()
        self.dbapi.execute("DELETE FROM gender_stats")
        for key in gstats.stats:
            female, male, unknown = gstats.stats[key]
            self.dbapi.execute("INSERT INTO gender_stats "
                               "(given_name, female, male, unknown) "
                               "VALUES (?, ?, ?, ?)",
                               [key, female, male, unknown])
        self._txn_commit()

    def undo_reference(self, data, handle):
        """
        Helper method to undo a reference map entry
        """
        if data is None:
            sql = ("DELETE FROM reference " +
                   "WHERE obj_handle = ? AND ref_handle = ?")
            self.dbapi.execute(sql, [handle[0], handle[1]])
        else:
            sql = ("INSERT INTO reference " +
                   "(obj_handle, obj_class, ref_handle, ref_class) " +
                   "VALUES(?, ?, ?, ?)")
            self.dbapi.execute(sql, data)

    def undo_data(self, data, handle, obj_key):
        """
        Helper method to undo/redo the changes made
        """
        cls = KEY_TO_CLASS_MAP[obj_key]
        table = cls.lower()
        if data is None:
            sql = "DELETE FROM %s WHERE handle = ?" % table
            self.dbapi.execute(sql, [handle])
        else:
            if self._has_handle(obj_key, handle):
                sql = "UPDATE %s SET blob_data = ? WHERE handle = ?" % table
                self.dbapi.execute(sql, [pickle.dumps(data), handle])
            else:
                sql = "INSERT INTO %s (handle, blob_data) VALUES (?, ?)" % table
                self.dbapi.execute(sql, [handle, pickle.dumps(data)])
            obj = self._get_table_func(cls)["class_func"].create(data)
            self._update_secondary_values(obj)

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

    def _sql_type(self, schema_type, max_length):
        """
        Given a schema type, return the SQL type for
        a new column.
        """
        if schema_type == 'string':
            if max_length:
                return "VARCHAR(%s)" % max_length
            else:
                return "TEXT"
        elif schema_type in ['boolean', 'integer']:
            return "INTEGER"
        elif schema_type == 'number':
            return "REAL"
        else:
            return "BLOB"

    def _create_secondary_columns(self):
        """
        Create secondary columns.
        """
        LOG.info("Creating secondary columns...")
        for cls in (Person, Family, Event, Place, Repository, Source,
                    Citation, Media, Note, Tag):
            table_name = cls.__name__.lower()
            for field, schema_type, max_length in cls.get_secondary_fields():
                if field != 'handle':
                    sql_type = self._sql_type(schema_type, max_length)
                    self.dbapi.execute("ALTER TABLE %s ADD COLUMN %s %s"
                                       % (table_name, field, sql_type))

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
            sets.append("%s = ?" % field)
            values.append(getattr(obj, field))

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
                               self._sql_cast_list(values)
                               + [obj.handle])

    def _sql_cast_list(self, values):
        """
        Given a list of field names and values, return the values
        in the appropriate type.
        """
        return [v if not isinstance(v, bool) else int(v) for v in values]
