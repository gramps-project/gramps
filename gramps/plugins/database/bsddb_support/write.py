#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2008  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
Provide the Berkeley DB (DbBsddb) database backend for Gramps.
This is used since Gramps version 3.0
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import pickle
import os
import time
import bisect
from functools import wraps
import logging
from sys import maxsize, getfilesystemencoding, version_info
from ast import literal_eval as safe_eval

from bsddb3 import dbshelve, db
from bsddb3.db import DB_CREATE, DB_AUTO_COMMIT, DB_DUP, DB_DUPSORT, DB_RDONLY

DBFLAGS_O = DB_CREATE | DB_AUTO_COMMIT  # Default flags for database open
DBFLAGS_R = DB_RDONLY                   # Flags to open a database read-only
DBFLAGS_D = DB_DUP | DB_DUPSORT         # Default flags for duplicate keys

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib.person import Person
from gramps.gen.lib.family import Family
from gramps.gen.lib.src import Source
from gramps.gen.lib.citation import Citation
from gramps.gen.lib.event import Event
from gramps.gen.lib.place import Place
from gramps.gen.lib.repo import Repository
from gramps.gen.lib.media import Media
from gramps.gen.lib.note import Note
from gramps.gen.lib.tag import Tag
from gramps.gen.lib.genderstats import GenderStats
from gramps.gen.lib.researcher import Researcher

from . import (DbBsddbRead, DbWriteBase, BSDDBTxn,
                    DbTxn, BsddbBaseCursor, BsddbDowngradeError, DbVersionError,
                    DbEnvironmentError, DbUpgradeRequiredError, find_surname,
                    find_byte_surname, find_surname_name, DbUndoBSDDB as DbUndo)

from gramps.gen.db import exceptions
from gramps.gen.db.dbconst import *
from gramps.gen.utils.callback import Callback
from gramps.gen.utils.id import create_id
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.errors import DbError, HandleError
from gramps.gen.constfunc import win, get_env_var
from gramps.gen.const import HOME_DIR, GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

_LOG = logging.getLogger(DBLOGNAME)
LOG = logging.getLogger(".citation")
#_LOG.setLevel(logging.DEBUG)
#_hdlr = logging.StreamHandler()
#_hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
#_LOG.addHandler(_hdlr)
_MINVERSION = 9
_DBVERSION = 18

IDTRANS     = "person_id"
FIDTRANS    = "family_id"
PIDTRANS    = "place_id"
OIDTRANS    = "media_id"
EIDTRANS    = "event_id"
RIDTRANS    = "repo_id"
NIDTRANS    = "note_id"
SIDTRANS    = "source_id"
CIDTRANS    = "citation_id"
TAGTRANS    = "tag_name"
SURNAMES    = "surnames"
NAME_GROUP  = "name_group"
META        = "meta_data"
PPARENT     = "place_parent"

FAMILY_TBL  = "family"
PLACES_TBL  = "place"
SOURCES_TBL = "source"
CITATIONS_TBL = "citation"
MEDIA_TBL   = "media"
EVENTS_TBL  = "event"
PERSON_TBL  = "person"
REPO_TBL    = "repo"
NOTE_TBL    = "note"
TAG_TBL     = "tag"

REF_MAP     = "reference_map"
REF_PRI     = "primary_map"
REF_REF     = "referenced_map"

DBERRS      = (db.DBRunRecoveryError, db.DBAccessError,
               db.DBPageNotFoundError, db.DBInvalidArgError)

# The following two dictionaries provide fast translation
# between the primary class names and the keys used to reference
# these classes in the database tables. Beware that changing
# these maps or modifying the values of the keys will break
# existing databases.

#-------------------------------------------------------------------------
#
# Helper functions
#
#-------------------------------------------------------------------------

def find_idmap(key, data):
    """ return id for association of secondary index.
    returns a byte string
    """
    val = data[1]
    if isinstance(val, str):
        val = val.encode('utf-8')
    return val

def find_parent(key, data):
    if hasattr(data[5], '__len__') and len(data[5]) > 0:
        val = data[5][0][0]
    else:
        val = ''
    if isinstance(val, str):
        val = val.encode('utf-8')
    return val

# Secondary database key lookups for reference_map table
# reference_map data values are of the form:
#   ((primary_object_class_name, primary_object_handle),
#    (referenced_object_class_name, referenced_object_handle))

def find_primary_handle(key, data):
    """ return handle for association of indexes
    returns byte string
    """
    val = (data)[0][1]
    if isinstance(val, str):
        val = val.encode('utf-8')
    return val

def find_referenced_handle(key, data):
    """ return handle for association of indexes
    returns byte string
    """
    val = (data)[1][1]
    if isinstance(val, str):
        val = val.encode('utf-8')
    return val

#-------------------------------------------------------------------------
#
# BsddbWriteCursor
#
#-------------------------------------------------------------------------
class BsddbWriteCursor(BsddbBaseCursor):

    def __init__(self, source, txn=None, **kwargs):
        BsddbBaseCursor.__init__(self, txn=txn, **kwargs)
        self.cursor = source.db.cursor(txn)
        self.source = source

#-------------------------------------------------------------------------
#
# DbBsddbAssocCursor
#
#-------------------------------------------------------------------------
class DbBsddbAssocCursor(BsddbBaseCursor):

    def __init__(self, source, txn=None, **kwargs):
        BsddbBaseCursor.__init__(self, txn=txn, **kwargs)
        self.cursor = source.cursor(txn)
        self.source = source

#-------------------------------------------------------------------------
#
# DbBsddb
#
#-------------------------------------------------------------------------
class DbBsddb(DbBsddbRead, DbWriteBase, UpdateCallback):
    """
    Gramps database write access object.
    """

    @classmethod
    def get_class_summary(cls):
        """
        Return a diction of information about this database.
        """
        try:
            import bsddb3 as bsddb
            bsddb_str = bsddb.__version__
            bsddb_db_str = str(bsddb.db.version()).replace(', ', '.')\
                                                  .replace('(', '').replace(')', '')
        except:
            bsddb_str = 'not found'
            bsddb_db_str = 'not found'
        summary = {
            "DB-API version": "n/a",
            "Database type": cls.__name__,
            'Database version': bsddb_str,
            'Database db version': bsddb_db_str
        }
        return summary

    # Set up dictionary for callback signal handler
    # ---------------------------------------------
    # 1. Signals for primary objects
    __signals__ = dict((obj+'-'+op, signal)
            for obj in
                ['person', 'family', 'event', 'place',
                 'source', 'citation', 'media', 'note', 'repository', 'tag']
            for op, signal in zip(
                ['add',   'update', 'delete', 'rebuild'],
                [(list,), (list,),  (list,),   None]
                )
            )

    # 2. Signals for long operations
    __signals__.update(('long-op-'+op, signal) for op, signal in zip(
        ['start',  'heartbeat', 'end'],
        [(object,), None,       None]
        ))

    # 3. Special signal for change in home person
    __signals__['home-person-changed'] = None

    # 4. Signal for change in person group name, parameters are
    __signals__['person-groupname-rebuild'] = (str, str)

    def __init__(self):
        """Create a new GrampsDB."""

        self.txn = None
        DbBsddbRead.__init__(self)
        DbWriteBase.__init__(self)
        #UpdateCallback.__init__(self)
        self.__tables = {
            'Person':
            {
                "handle_func": self.get_person_from_handle,
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                "add_func": self.add_person,
                "commit_func": self.commit_person,
                "count_func": self.get_number_of_people,
                "del_func": self.remove_person,
                "iter_func": self.iter_people,
            },
            'Family':
            {
                "handle_func": self.get_family_from_handle,
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                "add_func": self.add_family,
                "commit_func": self.commit_family,
                "count_func": self.get_number_of_families,
                "del_func": self.remove_family,
                "iter_func": self.iter_families,
            },
            'Source':
            {
                "handle_func": self.get_source_from_handle,
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                "add_func": self.add_source,
                "commit_func": self.commit_source,
                "count_func": self.get_number_of_sources,
                "del_func": self.remove_source,
                "iter_func": self.iter_sources,
            },
            'Citation':
            {
                "handle_func": self.get_citation_from_handle,
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                "add_func": self.add_citation,
                "commit_func": self.commit_citation,
                "count_func": self.get_number_of_citations,
                "del_func": self.remove_citation,
                "iter_func": self.iter_citations,
            },
            'Event':
            {
                "handle_func": self.get_event_from_handle,
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                "add_func": self.add_event,
                "commit_func": self.commit_event,
                "count_func": self.get_number_of_events,
                "del_func": self.remove_event,
                "iter_func": self.iter_events,
            },
            'Media':
            {
                "handle_func": self.get_media_from_handle,
                "gramps_id_func": self.get_media_from_gramps_id,
                "class_func": Media,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_handles,
                "add_func": self.add_media,
                "commit_func": self.commit_media,
                "count_func": self.get_number_of_media,
                "del_func": self.remove_media,
                "iter_func": self.iter_media,
            },
            'Place':
            {
                "handle_func": self.get_place_from_handle,
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                "add_func": self.add_place,
                "commit_func": self.commit_place,
                "count_func": self.get_number_of_places,
                "del_func": self.remove_place,
                "iter_func": self.iter_places,
            },
            'Repository':
            {
                "handle_func": self.get_repository_from_handle,
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                "add_func": self.add_repository,
                "commit_func": self.commit_repository,
                "count_func": self.get_number_of_repositories,
                "del_func": self.remove_repository,
                "iter_func": self.iter_repositories,
            },
            'Note':
            {
                "handle_func": self.get_note_from_handle,
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                "add_func": self.add_note,
                "commit_func": self.commit_note,
                "count_func": self.get_number_of_notes,
                "del_func": self.remove_note,
                "iter_func": self.iter_notes,
            },
            'Tag':
            {
                "handle_func": self.get_tag_from_handle,
                "gramps_id_func": None,
                "class_func": Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                "add_func": self.add_tag,
                "commit_func": self.commit_tag,
                "count_func": self.get_number_of_tags,
                "del_func": self.remove_tag,
                "iter_func": self.iter_tags,
            }
        }

        self.secondary_connected = False
        self.has_changed = False
        self.brief_name = None
        self.update_env_version = False
        self.update_python_version = False
        self.update_pickle_version = False

    def get_table_func(self, table=None, func=None):
        """
        Private implementation of get_table_func.
        """
        if table is None:
            return list(self.__tables.keys())
        elif func is None:
            return self.__tables[table]
        elif func in self.__tables[table].keys():
            return self.__tables[table][func]
        else: 
            return super().get_table_func(table, func)

    def catch_db_error(func):
        """
        Decorator function for catching database errors.  If *func* throws
        one of the exceptions in DBERRS, the error is logged and a DbError
        exception is raised.
        """
        @wraps(func)
        def try_(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except DBERRS as msg:
                self.__log_error()
                raise DbError(msg)
        return try_

    def __open_db(self, file_name, table_name, dbtype=db.DB_HASH, flags=0):
        dbmap = db.DB(self.env)
        dbmap.set_flags(flags)

        fname = os.path.join(file_name, table_name + DBEXT)

        if self.readonly:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_R)
        else:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_O, DBMODE)
        return dbmap

    def __open_shelf(self, file_name, table_name, dbtype=db.DB_HASH):
        dbmap = dbshelve.DBShelf(self.env)

        fname = os.path.join(file_name, table_name + DBEXT)

        if self.readonly:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_R)
        else:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_O, DBMODE)
        return dbmap

    def __all_handles(self, table):
        return table.keys(self.txn)

    def __log_error(self):
        mypath = os.path.join(self.get_save_path(),DBRECOVFN)
        with open(mypath, "w") as ofile:
            pass
        try:
            clear_lock_file(self.get_save_path())
        except:
            pass

    _log_error = __log_error

    # Override get_cursor method from the superclass to add udpate
    # capability

    @catch_db_error
    def get_cursor(self, table, txn=None, update=False, commit=False):
        """ Helper function to return a cursor over a table """
        if update and not txn:
            txn = self.env.txn_begin(self.txn)
        return BsddbWriteCursor(table, txn=txn or self.txn,
                                    update=update, commit=commit)

    # cursors for lookups in the reference_map for back reference
    # lookups. The reference_map has three indexes:
    # the main index: a tuple of (primary_handle, referenced_handle)
    # the primary_handle index: the primary_handle
    # the referenced_handle index: the referenced_handle
    # the main index is unique, the others allow duplicate entries.

    @catch_db_error
    def get_reference_map_cursor(self):
        """
        Returns a reference to a cursor over the reference map
        """
        return DbBsddbAssocCursor(self.reference_map, self.txn)

    @catch_db_error
    def get_reference_map_primary_cursor(self):
        """
        Returns a reference to a cursor over the reference map primary map
        """
        return DbBsddbAssocCursor(self.reference_map_primary_map,
                                        self.txn)

    @catch_db_error
    def get_reference_map_referenced_cursor(self):
        """
        Returns a reference to a cursor over the reference map referenced map
        """
        return DbBsddbAssocCursor(self.reference_map_referenced_map,
                                        self.txn)

    @catch_db_error
    def get_place_parent_cursor(self):
        """
        Returns a reference to a cursor over the place parents
        """
        return DbBsddbAssocCursor(self.parents, self.txn)

    # These are overriding the DbBsddbRead's methods of saving metadata
    # because we now have txn-capable metadata table

    @catch_db_error
    def set_default_person_handle(self, handle):
        """Set the default Person to the passed instance."""
        #we store a byte string!
        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put(b'default', handle)
            self.emit('home-person-changed')

    @catch_db_error
    def get_default_person(self):
        """Return the default Person of the database."""
        person_handle = self.get_default_handle()
        if person_handle:
            person = self.get_person_from_handle(person_handle)
            if person:
                return person
            elif (self.metadata) and (not self.readonly):
                # Start transaction
                with BSDDBTxn(self.env, self.metadata) as txn:
                    txn.put(b'default', None)
                return None
        else:
            return None

    def set_mediapath(self, path):
        """Set the default media path for database, path should be utf-8."""
        if self.metadata and not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put(b'mediapath', path)

    def __make_zip_backup(self, dirname):
        import zipfile
        # In Windows resrved characters is "<>:"/\|?*"
        reserved_char = r':,<>"/\|?* '
        replace_char = "-__________"
        title = self.get_dbname()
        trans = title.maketrans(reserved_char, replace_char)
        title = title.translate(trans)

        if not os.access(dirname, os.W_OK):
            _LOG.warning("Can't write technical DB backup for %s" % title)
            return
        (grampsdb_path, db_code) = os.path.split(dirname)
        dotgramps_path = os.path.dirname(grampsdb_path)
        zipname = title + time.strftime("_%Y-%m-%d_%H-%M-%S") + ".zip"
        zippath = os.path.join(dotgramps_path, zipname)
        myzip = zipfile.ZipFile(zippath, 'w')
        for filename in os.listdir(dirname):
            pathname = os.path.join(dirname, filename)
            myzip.write(pathname, os.path.join(db_code, filename))
        myzip.close()
        _LOG.warning("If upgrade and loading the Family Tree works, you can "
                     "delete the zip file at %s" %
                     zippath)

    def __check_bdb_version(self, name, force_bsddb_upgrade=False,
                            force_bsddb_downgrade=False):
        """Older version of Berkeley DB can't read data created by a newer
        version."""
        bdb_version = db.version()
        versionpath = os.path.join(self.path, str(BDBVERSFN))
        # Compare the current version of the database (bsddb_version) with the
        # version of the database code (env_version). If it is a downgrade,
        # raise an exception because we can't do anything. If they are the same,
        # return. If it is an upgrade, raise an exception unless  the user has
        # already told us we can upgrade.
        if os.path.isfile(versionpath):
            with open(versionpath, "r") as version_file:
                bsddb_version = version_file.read().strip()
                env_version = tuple(map(int, bsddb_version[1:-1].split(', ')))
        else:
            # bsddb version is unknown
            bsddb_version = "Unknown"
            env_version = "Unknown"
#        _LOG.debug("db version %s, program version %s" % (bsddb_version, bdb_version))

        if env_version == "Unknown" or \
            (env_version[0] < bdb_version[0]) or \
            (env_version[0] == bdb_version[0] and
             env_version[1] < bdb_version[1]) or \
            (env_version[0] == bdb_version[0] and
             env_version[1] == bdb_version[1] and
             env_version[2] < bdb_version[2]):
            # an upgrade is needed
            if not force_bsddb_upgrade:
                _LOG.debug("Bsddb upgrade required from %s to %s" %
                           (bsddb_version, str(bdb_version)))
                clear_lock_file(name)
                raise exceptions.BsddbUpgradeRequiredError(bsddb_version,
                                                           str(bdb_version))
            if not self.readonly:
                _LOG.warning("Bsddb upgrade requested from %s to %s" %
                             (bsddb_version, str(bdb_version)))
                self.update_env_version = True
            # Make a backup of the database files anyway
            self.__make_zip_backup(name)
        elif (env_version[0] > bdb_version[0]) or \
            (env_version[0] == bdb_version[0] and
             env_version[1] > bdb_version[1]):
            clear_lock_file(name)
            raise BsddbDowngradeError(env_version, bdb_version)
        elif (env_version[0] == bdb_version[0] and
             env_version[1] == bdb_version[1] and
             env_version[2] > bdb_version[2]):
            # A down-grade may be possible
            if not force_bsddb_downgrade:
                _LOG.debug("Bsddb downgrade required from %s to %s" %
                           (bsddb_version, str(bdb_version)))
                clear_lock_file(name)
                raise exceptions.BsddbDowngradeRequiredError(bsddb_version,
                                                           str(bdb_version))
            # Try to do a down-grade
            if not self.readonly:
                _LOG.warning("Bsddb downgrade requested from %s to %s" %
                             (bsddb_version, str(bdb_version)))
                self.update_env_version = True
            # Make a backup of the database files anyway
            self.__make_zip_backup(name)
        elif env_version == bdb_version:
            # Bsddb version is OK
            pass
        else:
            # This can't happen
            raise "Comparison between Bsddb version failed"

    def __check_python_version(self, name, force_python_upgrade=False):
        """
        The 'pickle' format (may) change with each Python version, see
        http://docs.python.org/3.2/library/pickle.html#pickle. Code commits
        21777 and 21778 ensure that when going from python2 to python3, the old
        format can be read. However, once the data has been written in the
        python3 format, it will not be possible to go back to pyton2. This check
        test whether we are changing python versions. If going from 2 to 3 it
        warns the user, and allows it if he confirms. When going from 3 to 3, an
        error is raised. Because code for python2 did not write the Python
        version file, if the file is absent, python2 is assumed.
        """
        current_python_version = version_info[0]
        versionpath = os.path.join(self.path, "pythonversion.txt")
        if os.path.isfile(versionpath):
            with open(versionpath, "r") as version_file:
                db_python_version = int(version_file.read().strip())
        else:
            db_python_version = 2

        if db_python_version == 3 and current_python_version == 2:
            clear_lock_file(name)
            raise exceptions.PythonDowngradeError(db_python_version,
                                                  current_python_version)
        elif db_python_version == 2 and current_python_version > 2:
            if not force_python_upgrade:
                _LOG.debug("Python upgrade required from %s to %s" %
                           (db_python_version, current_python_version))
                clear_lock_file(name)
                raise exceptions.PythonUpgradeRequiredError(db_python_version,
                                                        current_python_version)
            # Try to do an upgrade
            if not self.readonly:
                _LOG.warning("Python upgrade requested from %s to %s" %
                             (db_python_version, current_python_version))
                self.update_python_version = True
            # Make a backup of the database files anyway
            self.__make_zip_backup(name)
        elif db_python_version == 2 and current_python_version == 2:
            pass

    @catch_db_error
    def version_supported(self):
        dbversion = self.metadata.get(b'version', default=0)
        return ((dbversion <= _DBVERSION) and (dbversion >= _MINVERSION))

    @catch_db_error
    def need_schema_upgrade(self):
        dbversion = self.metadata.get(b'version', default=0)
        return not self.readonly and dbversion < _DBVERSION

    def __check_readonly(self, name):
        """
        Return True if we don't have read/write access to the database,
        otherwise return False (that is, we DO have read/write access)
        """

        # See if we write to the target directory at all?
        if not os.access(name, os.W_OK):
            return True

        # See if we lack write access to any files in the directory
        for base in [FAMILY_TBL, PLACES_TBL, SOURCES_TBL, CITATIONS_TBL,
                     MEDIA_TBL,  EVENTS_TBL, PERSON_TBL, REPO_TBL,
                     NOTE_TBL, REF_MAP, META]:
            path = os.path.join(name, base + DBEXT)
            if os.path.isfile(path) and not os.access(path, os.W_OK):
                return True

        # All tests passed.  Inform caller that we are NOT read only
        return False

    @catch_db_error
    def load(self, name, callback=None, mode=DBMODE_W, force_schema_upgrade=False,
             force_bsddb_upgrade=False, force_bsddb_downgrade=False,
             force_python_upgrade=False, update=True):
        """
        If update is False: then don't update any files; open read-only
        """

        if self.__check_readonly(name):
            mode = DBMODE_R
        elif update:
            write_lock_file(name)
        else:
            mode = DBMODE_R

        if self.db_is_open:
            self.close()

        self.readonly = mode == DBMODE_R
        #super(DbBsddbRead, self).load(name, callback, mode)
        if callback:
            callback(12)

        # Save full path and base file name
        self.full_name = os.path.abspath(name)
        self.path = self.full_name
        self.brief_name = os.path.basename(name)

        # If we re-enter load with force_python_upgrade True, then we have
        # already checked the bsddb version, and then checked python version,
        # and are agreeing on the upgrade
        if not force_python_upgrade:
            self.__check_bdb_version(name, force_bsddb_upgrade,
                                     force_bsddb_downgrade)

        self.__check_python_version(name, force_python_upgrade)

        # Check for pickle upgrade
        versionpath = os.path.join(self.path, str(PCKVERSFN))
        # Up to gramps 3.4.x PCKVERSFN was not written
        # Gramps 4.2 incorrectly wrote PCKVERSFN = 'Yes' for Python2, so check
        # whether python is upgraded
        if ((not self.readonly and not self.update_pickle_version) and
            (not os.path.isfile(versionpath) or self.update_python_version)):
            _LOG.debug("Make backup in case there is a pickle upgrade")
            self.__make_zip_backup(name)
            self.update_pickle_version = True

        # Check for schema upgrade
        versionpath = os.path.join(self.path, str(SCHVERSFN))
        if os.path.isfile(versionpath):
            with open(versionpath, "r") as version_file:
                schema_version = int(version_file.read().strip())
        else:
            schema_version = 0
        if not self.readonly and schema_version < _DBVERSION and \
                                 force_schema_upgrade:
            _LOG.debug("Make backup in case there is a schema upgrade")
            self.__make_zip_backup(name)

        # Set up database environment
        self.env = db.DBEnv()
        self.env.set_cachesize(0, DBCACHE)

        # These env settings are only needed for Txn environment
        self.env.set_lk_max_locks(DBLOCKS)
        self.env.set_lk_max_objects(DBOBJECTS)

        # Set to auto remove stale logs
        self.set_auto_remove()

        # Set not to flush to disk synchronous, this greatly speeds up
        # database changes, but comes at the cause of loss of durability, so
        # power loss might cause a need to run db recovery, see BSDDB manual
        ## NOTE: due to pre 4.8 bsddb bug it is needed to set this flag before
        ## open of env, #16492 - http://download.oracle.com/docs/cd/E17076_02/html/installation/changelog_4_8.html
        self.env.set_flags(db.DB_TXN_WRITE_NOSYNC, 1)

        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE | db.DB_PRIVATE |\
                    db.DB_INIT_MPOOL |\
                    db.DB_INIT_LOG | db.DB_INIT_TXN

        # As opposed to before, we always try recovery on databases
        env_flags |= db.DB_RECOVER

        # Environment name is now based on the filename
        env_name = name

        try:
            self.env.open(env_name, env_flags)
        except Exception as msg:
            _LOG.warning("Error opening db environment: " + str(msg))
            try:
                self.__close_early()
            except:
                pass
            raise DbEnvironmentError(msg)

        self.env.txn_checkpoint()

        if callback:
            callback(25)

        # Process metadata
        self.metadata = self.__open_shelf(self.full_name, META)

        # If we cannot work with this DB version,
        # it makes no sense to go further
        if not self.version_supported():
            tree_vers = self.metadata.get(b'version', default=0)
            self.__close_early()
            raise DbVersionError(tree_vers, _MINVERSION, _DBVERSION)

        gstats = self.metadata.get(b'gender_stats', default=None)

        # Ensure version info in metadata
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                if gstats is None:
                    # New database. Set up the current version.
                    #self.metadata.put(b'version', _DBVERSION, txn=the_txn)
                    txn.put(b'version', _DBVERSION)
                    txn.put(b'upgraded', 'Yes')
                elif b'version' not in self.metadata:
                    # Not new database, but the version is missing.
                    # Use 0, but it is likely to fail anyway.
                    txn.put(b'version', 0)

        self.genderStats = GenderStats(gstats)

        # Open main tables in gramps database
        db_maps = [
                    ("family_map",     FAMILY_TBL,  db.DB_HASH),
                    ("place_map",      PLACES_TBL,  db.DB_HASH),
                    ("source_map",     SOURCES_TBL, db.DB_HASH),
                    ("citation_map",   CITATIONS_TBL, db.DB_HASH),
                    ("media_map",      MEDIA_TBL,   db.DB_HASH),
                    ("event_map",      EVENTS_TBL,  db.DB_HASH),
                    ("person_map",     PERSON_TBL,  db.DB_HASH),
                    ("repository_map", REPO_TBL,    db.DB_HASH),
                    ("note_map",       NOTE_TBL,    db.DB_HASH),
                    ("tag_map",        TAG_TBL,     db.DB_HASH),
                    ("reference_map",  REF_MAP,     db.DB_BTREE),
                  ]

        dbflags = DBFLAGS_R if self.readonly else DBFLAGS_O
        for (dbmap, dbname, dbtype) in db_maps:
            _db = self.__open_shelf(self.full_name, dbname, dbtype)
            setattr(self, dbmap, _db)

        if callback:
            callback(37)

        # Open name grouping database
        self.name_group = self.__open_db(self.full_name, NAME_GROUP,
                              db.DB_HASH, db.DB_DUP)

        # We have now successfully opened the database, so if the BSDDB version
        # has changed, we update the DBSDB version file.

        if self.update_env_version:
            versionpath = os.path.join(name, BDBVERSFN)
            with open(versionpath, "w") as version_file:
                version = str(db.version())
                version_file.write(version)
            _LOG.debug("Updated bsddb version file to %s" % str(db.version()))

        if self.update_python_version:
            versionpath = os.path.join(name, "pythonversion.txt")
            version = str(version_info[0])
            _LOG.debug("Updated python version file to %s" % version)
            with open(versionpath, "w") as version_file:
                version_file.write(version)

        # Here we take care of any changes in the tables related to new code.
        # If secondary indices change, then they should removed
        # or rebuilt by upgrade as well. In any case, the
        # self.secondary_connected flag should be set accordingly.
        if self.update_pickle_version:
            from . import upgrade
            UpdateCallback.__init__(self, callback)
            upgrade.gramps_upgrade_pickle(self)
            versionpath = os.path.join(name, str(PCKVERSFN))
            with open(versionpath, "w") as version_file:
                version = "Yes"
                version_file.write(version)
            _LOG.debug("Updated pickle version file to %s" % str(version))

        self.__load_metadata()

        if self.need_schema_upgrade():
            oldschema = self.metadata.get(b'version', default=0)
            newschema = _DBVERSION
            _LOG.debug("Schema upgrade required from %s to %s" %
                       (oldschema, newschema))
            if force_schema_upgrade == True:
                self.gramps_upgrade(callback)
                versionpath = os.path.join(name, str(SCHVERSFN))
                with open(versionpath, "w") as version_file:
                    version = str(_DBVERSION)
                    version_file.write(version)
                _LOG.debug("Updated schema version file to %s" % str(version))
            else:
                self.__close_early()
                clear_lock_file(name)
                raise DbUpgradeRequiredError(oldschema, newschema)

        if callback:
            callback(50)

        # Connect secondary indices
        if not self.secondary_connected:
            self.__connect_secondary()

        if callback:
            callback(75)

        # Open undo database
        self.__open_undodb()
        self.db_is_open = True

        if callback:
            callback(87)

        self.abort_possible = True
        return 1

    def __open_undodb(self):
        """
        Open the undo database
        """
        if not self.readonly:
            self.undolog = os.path.join(self.full_name, DBUNDOFN)
            self.undodb = DbUndo(self, self.undolog)
            self.undodb.open()

    def __close_undodb(self):
        if not self.readonly:
            try:
                self.undodb.close()
            except db.DBNoSuchFileError:
                pass

    def get_undodb(self):
        """
        Return the database that keeps track of Undo/Redo operations.
        """
        return self.undodb

    def __load_metadata(self):
        # name display formats
        self.name_formats = self.metadata.get(b'name_formats', default=[])
        # upgrade formats if they were saved in the old way
        for format_ix in range(len(self.name_formats)):
            format = self.name_formats[format_ix]
            if len(format) == 3:
                format = format + (True,)
                self.name_formats[format_ix] = format

        # database owner
        try:
            owner_data = self.metadata.get(b'researcher')
            if owner_data:
                if len(owner_data[0]) == 7: # Pre-3.3 format
                    owner_data = upgrade_researcher(owner_data)
                self.owner.unserialize(owner_data)
        except ImportError: #handle problems with pre-alpha 3.0
            pass

        # bookmarks
        def meta(key):
            return self.metadata.get(key, default=[])

        self.bookmarks.set(meta(b'bookmarks'))
        self.family_bookmarks.set(meta(b'family_bookmarks'))
        self.event_bookmarks.set(meta(b'event_bookmarks'))
        self.source_bookmarks.set(meta(b'source_bookmarks'))
        self.citation_bookmarks.set(meta(b'citation_bookmarks'))
        self.repo_bookmarks.set(meta(b'repo_bookmarks'))
        self.media_bookmarks.set(meta(b'media_bookmarks'))
        self.place_bookmarks.set(meta(b'place_bookmarks'))
        self.note_bookmarks.set(meta(b'note_bookmarks'))

        # Custom type values
        self.event_names = set(meta(b'event_names'))
        self.family_attributes = set(meta(b'fattr_names'))
        self.individual_attributes = set(meta(b'pattr_names'))
        self.source_attributes = set(meta(b'sattr_names'))
        self.marker_names = set(meta(b'marker_names'))
        self.child_ref_types = set(meta(b'child_refs'))
        self.family_rel_types = set(meta(b'family_rels'))
        self.event_role_names = set(meta(b'event_roles'))
        self.name_types = set(meta(b'name_types'))
        self.origin_types = set(meta(b'origin_types'))
        self.repository_types = set(meta(b'repo_types'))
        self.note_types = set(meta(b'note_types'))
        self.source_media_types = set(meta(b'sm_types'))
        self.url_types = set(meta(b'url_types'))
        self.media_attributes = set(meta(b'mattr_names'))
        self.event_attributes = set(meta(b'eattr_names'))
        self.place_types = set(meta(b'place_types'))

        # surname list
        self.surname_list = meta(b'surname_list')

    def __connect_secondary(self):
        """
        Connect or creates secondary index tables.

        It assumes that the tables either exist and are in the right
        format or do not exist (in which case they get created).

        It is the responsibility of upgrade code to either create
        or remove invalid secondary index tables.
        """

        # index tables used just for speeding up searches
        self.surnames = self.__open_db(self.full_name, SURNAMES, db.DB_BTREE,
                            db.DB_DUP | db.DB_DUPSORT)

        db_maps = [
            ("id_trans",  IDTRANS,  db.DB_HASH, 0),
            ("fid_trans", FIDTRANS, db.DB_HASH, 0),
            ("eid_trans", EIDTRANS, db.DB_HASH, 0),
            ("pid_trans", PIDTRANS, db.DB_HASH, 0),
            ("sid_trans", SIDTRANS, db.DB_HASH, 0),
            ("cid_trans", CIDTRANS, db.DB_HASH, 0),
            ("oid_trans", OIDTRANS, db.DB_HASH, 0),
            ("rid_trans", RIDTRANS, db.DB_HASH, 0),
            ("nid_trans", NIDTRANS, db.DB_HASH, 0),
            ("tag_trans", TAGTRANS, db.DB_HASH, 0),
            ("parents", PPARENT, db.DB_HASH, 0),
            ("reference_map_primary_map",    REF_PRI, db.DB_BTREE, 0),
            ("reference_map_referenced_map", REF_REF, db.DB_BTREE, db.DB_DUPSORT),
            ]

        for (dbmap, dbname, dbtype, dbflags) in db_maps:
            _db = self.__open_db(self.full_name, dbname, dbtype,
                db.DB_DUP | dbflags)
            setattr(self, dbmap, _db)

        if not self.readonly:

            assoc = [
                (self.person_map, self.surnames,  find_byte_surname),
                (self.person_map, self.id_trans,  find_idmap),
                (self.family_map, self.fid_trans, find_idmap),
                (self.event_map,  self.eid_trans, find_idmap),
                (self.place_map,  self.pid_trans, find_idmap),
                (self.place_map, self.parents, find_parent),
                (self.source_map, self.sid_trans, find_idmap),
                (self.citation_map, self.cid_trans, find_idmap),
                (self.media_map,  self.oid_trans, find_idmap),
                (self.repository_map, self.rid_trans, find_idmap),
                (self.note_map,   self.nid_trans, find_idmap),
                (self.tag_map,    self.tag_trans, find_idmap),
                (self.reference_map, self.reference_map_primary_map,
                    find_primary_handle),
                (self.reference_map, self.reference_map_referenced_map,
                    find_referenced_handle),
                ]

            flags = DBFLAGS_R if self.readonly else DBFLAGS_O
            for (dbmap, a_map, a_find) in assoc:
                dbmap.associate(a_map, a_find, flags=flags)

        self.secondary_connected = True
        self.smap_index = len(self.source_map)
        self.cmap_index = len(self.citation_map)
        self.emap_index = len(self.event_map)
        self.pmap_index = len(self.person_map)
        self.fmap_index = len(self.family_map)
        self.lmap_index = len(self.place_map)
        self.omap_index = len(self.media_map)
        self.rmap_index = len(self.repository_map)
        self.nmap_index = len(self.note_map)

    @catch_db_error
    def rebuild_secondary(self, callback=None):
        if self.readonly:
            return

        table_flags = DBFLAGS_O

        # remove existing secondary indices

        items = [
            ( self.id_trans,  IDTRANS ),
            ( self.surnames,  SURNAMES ),
            ( self.fid_trans, FIDTRANS ),
            ( self.pid_trans, PIDTRANS ),
            ( self.oid_trans, OIDTRANS ),
            ( self.eid_trans, EIDTRANS ),
            ( self.rid_trans, RIDTRANS ),
            ( self.nid_trans, NIDTRANS ),
            ( self.cid_trans, CIDTRANS ),
            ( self.tag_trans, TAGTRANS ),
            ( self.parents, PPARENT ),
            ( self.reference_map_primary_map, REF_PRI),
            ( self.reference_map_referenced_map, REF_REF),
            ]

        index = 1
        for (database, name) in items:
            database.close()
            _db = db.DB(self.env)
            try:
                _db.remove(_mkname(self.full_name, name), name)
            except db.DBNoSuchFileError:
                pass
            if callback:
                callback(index)
            index += 1

        if callback:
            callback(11)

        # Set flag saying that we have removed secondary indices
        # and then call the creating routine
        self.secondary_connected = False
        self.__connect_secondary()
        if callback:
            callback(12)

    @catch_db_error
    def find_place_child_handles(self, handle):
        """
        Find all child places having the given place as the primary parent.
        """
        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        parent_cur = self.get_place_parent_cursor()

        try:
            ret = parent_cur.set(handle)
        except:
            ret = None

        while (ret is not None):
            (key, data) = ret

            ### FIXME: this is a dirty hack that works without no
            ### sensible explanation. For some reason, for a readonly
            ### database, secondary index returns a primary table key
            ### corresponding to the data, not the data.
            if self.readonly:
                data = self.place_map.get(data)
            else:
                data = pickle.loads(data)

            yield data[0]
            ret = parent_cur.next_dup()

        parent_cur.close()

    @catch_db_error
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
        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        # Use the secondary index to locate all the reference_map entries
        # that include a reference to the object we are looking for.
        referenced_cur = self.get_reference_map_referenced_cursor()

        try:
            ret = referenced_cur.set(handle)
        except:
            ret = None

        while (ret is not None):
            (key, data) = ret

            # data values are of the form:
            #   ((primary_object_class_name, primary_object_handle),
            #    (referenced_object_class_name, referenced_object_handle))
            # so we need the first tuple to give us the type to compare

            ### FIXME: this is a dirty hack that works without no
            ### sensible explanation. For some reason, for a readonly
            ### database, secondary index returns a primary table key
            ### corresponding to the data, not the data.
            if self.readonly:
                data = self.reference_map.get(data)
            else:
                data = pickle.loads(data)

            key, handle = data[0][:2]
            name = KEY_TO_CLASS_MAP[key]
            assert name == KEY_TO_CLASS_MAP[data[0][0]]
            assert handle == data[0][1]
            if (include_classes is None or
                name in include_classes):
                    yield (name, handle)

            ret = referenced_cur.next_dup()

        referenced_cur.close()

    def delete_primary_from_reference_map(self, handle, transaction, txn=None):
        """
        Remove all references to the primary object from the reference_map.
        handle should be utf-8
        """
        primary_cur = self.get_reference_map_primary_cursor()

        try:
            ret = primary_cur.set(handle)
        except:
            ret = None

        remove_list = set()
        while (ret is not None):
            (key, data) = ret

            # data values are of the form:
            #   ((primary_object_class_name, primary_object_handle),
            #    (referenced_object_class_name, referenced_object_handle))

            # so we need the second tuple give us a reference that we can
            # combine with the primary_handle to get the main key.
            main_key = (handle.decode('utf-8'), pickle.loads(data)[1][1])

            # The trick is not to remove while inside the cursor,
            # but collect them all and remove after the cursor is closed
            remove_list.add(main_key)

            ret = primary_cur.next_dup()

        primary_cur.close()

        # Now that the cursor is closed, we can remove things
        for main_key in remove_list:
            self.__remove_reference(main_key, transaction, txn)

    def update_reference_map(self, obj, transaction, txn=None):
        """
        If txn is given, then changes are written right away using txn.
        """

        # Add references to the reference_map for all primary object referenced
        # from the primary object 'obj' or any of its secondary objects.
        handle = obj.handle
        existing_references = set()
        primary_cur = self.get_reference_map_primary_cursor()
        try:
            if isinstance(handle, str):
                key = handle.encode('utf-8')
            else:
                key = handle
            ret = primary_cur.set(key)
        except:
            ret = None

        while (ret is not None):
            (key, data) = ret
                # data values are of the form:
                #   ((primary_object_class_name, primary_object_handle),
                #    (referenced_object_class_name, referenced_object_handle))
                # so we need the second tuple give us a reference that we can
                # compare with what is returned from
                # get_referenced_handles_recursively

                # secondary DBs are not DBShelf's, so we need to do pickling
                # and unpickling ourselves here
            existing_reference = pickle.loads(data)[1]
            existing_references.add((KEY_TO_CLASS_MAP[existing_reference[0]],
                                     existing_reference[1]))
            ret = primary_cur.next_dup()
        primary_cur.close()

        # Once we have the list of rows that already have a reference
        # we need to compare it with the list of objects that are
        # still references from the primary object.
        current_references = set(obj.get_referenced_handles_recursively())
        no_longer_required_references = existing_references.difference(
                                                            current_references)
        new_references = current_references.difference(existing_references)

        # handle addition of new references
        for (ref_class_name, ref_handle) in new_references:
            data = ((CLASS_TO_KEY_MAP[obj.__class__.__name__], handle),
                    (CLASS_TO_KEY_MAP[ref_class_name], ref_handle),)
            self.__add_reference((handle, ref_handle), data, transaction, txn)

        # handle deletion of old references
        for (ref_class_name, ref_handle) in no_longer_required_references:
            try:
                self.__remove_reference((handle, ref_handle), transaction, txn)
            except:
                # ignore missing old reference
                pass

    def __remove_reference(self, key, transaction, txn):
        """
        Remove the reference specified by the key, preserving the change in
        the passed transaction.
        """
        if isinstance(key, tuple):
            #create a byte string key, first validity check in python 3!
            for val in key:
                if isinstance(val, bytes):
                    raise DbError(_('An attempt is made to save a reference key '
                                    'which is partly bytecode, this is not allowed.\n'
                                    'Key is %s') % str(key))
            key = str(key)
        if isinstance(key, str):
            key = key.encode('utf-8')
        if not self.readonly:
            if not transaction.batch:
                old_data = self.reference_map.get(key, txn=txn)
                transaction.add(REFERENCE_KEY, TXNDEL, key, old_data, None)
                #transaction.reference_del.append(str(key))
            self.reference_map.delete(key, txn=txn)

    def __add_reference(self, key, data, transaction, txn):
        """
        Add the reference specified by the key and the data, preserving the
        change in the passed transaction.
        """
        if isinstance(key, tuple):
            #create a string key
            key = str(key)
        if isinstance(key, str):
            key = key.encode('utf-8')
        if self.readonly or not key:
            return

        self.reference_map.put(key, data, txn=txn)
        if not transaction.batch:
            transaction.add(REFERENCE_KEY, TXNADD, key, None, data)
            #transaction.reference_add.append((str(key), data))

    @catch_db_error
    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.

        This will be a slow process for large databases.
        """

        # First, remove the reference map and related tables

        db_maps = [
                    ("reference_map_referenced_map", REF_REF),
                    ("reference_map_primary_map", REF_PRI),
                    ("reference_map", REF_MAP),
                  ]

        for index, (dbmap, dbname) in enumerate(db_maps):
            getattr(self, dbmap).close()
            _db = db.DB(self.env)
            try:
                _db.remove(_mkname(self.full_name, dbname), dbname)
            except db.DBNoSuchFileError:
                pass
            callback(index+1)

        # Open reference_map and primary map
        self.reference_map  = self.__open_shelf(self.full_name, REF_MAP,
                                  dbtype=db.DB_BTREE)

        self.reference_map_primary_map = self.__open_db(self.full_name,
                                            REF_PRI, db.DB_BTREE, db.DB_DUP)

        self.reference_map.associate(self.reference_map_primary_map,
                                     find_primary_handle, DBFLAGS_O)

        # Make a tuple of the functions and classes that we need for
        # each of the primary object tables.

        with DbTxn(_("Rebuild reference map"), self, batch=True,
                                    no_magic=True) as transaction:
            callback(4)

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
                        obj = class_func()
                        obj.unserialize(val)
                        with BSDDBTxn(self.env) as txn:
                            self.update_reference_map(obj, transaction, txn.txn)

            callback(5)

        self.reference_map_referenced_map = self.__open_db(self.full_name,
            REF_REF, db.DB_BTREE, db.DB_DUP|db.DB_DUPSORT)

        flags = DBFLAGS_R if self.readonly else DBFLAGS_O
        self.reference_map.associate(self.reference_map_referenced_map,
                                     find_referenced_handle, flags=flags)
        callback(6)

    def __close_metadata(self):
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:

            # name display formats
                txn.put(b'name_formats', self.name_formats)

                # database owner
                owner_data = self.owner.serialize()
                txn.put(b'researcher', owner_data)

                # bookmarks
                txn.put(b'bookmarks', self.bookmarks.get())
                txn.put(b'family_bookmarks', self.family_bookmarks.get())
                txn.put(b'event_bookmarks', self.event_bookmarks.get())
                txn.put(b'source_bookmarks', self.source_bookmarks.get())
                txn.put(b'citation_bookmarks', self.citation_bookmarks.get())
                txn.put(b'place_bookmarks', self.place_bookmarks.get())
                txn.put(b'repo_bookmarks', self.repo_bookmarks.get())
                txn.put(b'media_bookmarks', self.media_bookmarks.get())
                txn.put(b'note_bookmarks', self.note_bookmarks.get())

                # gender stats
                txn.put(b'gender_stats', self.genderStats.save_stats())

                # Custom type values
                txn.put(b'event_names', list(self.event_names))
                txn.put(b'fattr_names', list(self.family_attributes))
                txn.put(b'pattr_names', list(self.individual_attributes))
                txn.put(b'sattr_names', list(self.source_attributes))
                txn.put(b'marker_names', list(self.marker_names))
                txn.put(b'child_refs', list(self.child_ref_types))
                txn.put(b'family_rels', list(self.family_rel_types))
                txn.put(b'event_roles', list(self.event_role_names))
                txn.put(b'name_types', list(self.name_types))
                txn.put(b'origin_types', list(self.origin_types))
                txn.put(b'repo_types', list(self.repository_types))
                txn.put(b'note_types', list(self.note_types))
                txn.put(b'sm_types', list(self.source_media_types))
                txn.put(b'url_types', list(self.url_types))
                txn.put(b'mattr_names', list(self.media_attributes))
                txn.put(b'eattr_names', list(self.event_attributes))
                txn.put(b'place_types', list(self.place_types))

                # name display formats
                txn.put(b'surname_list', self.surname_list)

        self.metadata.close()

    def __close_early(self):
        """
        Bail out if the incompatible version is discovered:
        * close cleanly to not damage data/env
        """
        if hasattr(self, 'metadata') and self.metadata:
            self.metadata.close()
        self.env.close()
        self.metadata   = None
        self.env        = None
        self.db_is_open = False

    @catch_db_error
    def close(self, update=True, user=None):
        """
        Close the database.
        if update is False, don't change access times, etc.
        """
        if not self.db_is_open:
            return
        self.autobackup(user)
        if self.txn:
            self.transaction_abort(self.transaction)
        self.env.txn_checkpoint()

        self.__close_metadata()
        self.name_group.close()
        self.surnames.close()
        self.parents.close()
        self.id_trans.close()
        self.fid_trans.close()
        self.eid_trans.close()
        self.rid_trans.close()
        self.nid_trans.close()
        self.oid_trans.close()
        self.sid_trans.close()
        self.cid_trans.close()
        self.pid_trans.close()
        self.tag_trans.close()
        self.reference_map_primary_map.close()
        self.reference_map_referenced_map.close()
        self.reference_map.close()
        self.secondary_connected = False

        # primary databases must be closed after secondary indexes, or
        # we run into problems with any active cursors.
        self.person_map.close()
        self.family_map.close()
        self.repository_map.close()
        self.note_map.close()
        self.place_map.close()
        self.source_map.close()
        self.citation_map.close()
        self.media_map.close()
        self.event_map.close()
        self.tag_map.close()
        self.env.close()
        self.__close_undodb()

        self.person_map     = None
        self.family_map     = None
        self.repository_map = None
        self.note_map       = None
        self.place_map      = None
        self.source_map     = None
        self.citation_map   = None
        self.media_map      = None
        self.event_map      = None
        self.tag_map        = None
        self.surnames       = None
        self.env            = None
        self.metadata       = None
        self.db_is_open     = False
        self.surname_list = None

        DbBsddbRead.close(self)

        self.person_map = None
        self.family_map = None
        self.repository_map = None
        self.note_map = None
        self.place_map = None
        self.source_map = None
        self.citation_map = None
        self.media_map = None
        self.event_map = None
        self.tag_map = None
        self.reference_map_primary_map = None
        self.reference_map_referenced_map = None
        self.reference_map = None
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.undodb = None

        try:
            clear_lock_file(self.get_save_path())
        except IOError:
            pass

    def __add_object(self, obj, transaction, find_next_func, commit_func):
        if find_next_func and not obj.gramps_id:
            obj.gramps_id = find_next_func()
        if not obj.handle:
            obj.handle = create_id()
        commit_func(obj, transaction)
        return obj.handle

    def add_person(self, person, transaction, set_gid=True):
        """
        Add a Person to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        handle = self.__add_object(person, transaction,
                    self.find_next_person_gramps_id if set_gid else None,
                    self.commit_person)
        return handle

    def add_family(self, family, transaction, set_gid=True):
        """
        Add a Family to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(family, transaction,
                    self.find_next_family_gramps_id if set_gid else None,
                    self.commit_family)

    def add_source(self, source, transaction, set_gid=True):
        """
        Add a Source to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(source, transaction,
                    self.find_next_source_gramps_id if set_gid else None,
                    self.commit_source)

    def add_citation(self, citation, transaction, set_gid=True):
        """
        Add a Citation to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(citation, transaction,
                    self.find_next_citation_gramps_id if set_gid else None,
                    self.commit_citation)

    def add_event(self, event, transaction, set_gid=True):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        if event.type.is_custom():
            self.event_names.add(str(event.type))
        return self.__add_object(event, transaction,
                    self.find_next_event_gramps_id if set_gid else None,
                    self.commit_event)

    def add_person_event(self, event, transaction):
        """
        Deprecated:  Use add_event
        """
        return self.add_event(event, transaction)

    def add_family_event(self, event, transaction):
        """
        Deprecated:  Use add_event
        """
        return self.add_event(event, transaction)

    def add_place(self, place, transaction, set_gid=True):
        """
        Add a Place to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(place, transaction,
                    self.find_next_place_gramps_id if set_gid else None,
                    self.commit_place)

    def add_media(self, media, transaction, set_gid=True):
        """
        Add a Media to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(media, transaction,
                    self.find_next_media_gramps_id if set_gid else None,
                    self.commit_media)

    def add_repository(self, obj, transaction, set_gid=True):
        """
        Add a Repository to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(obj, transaction,
                    self.find_next_repository_gramps_id if set_gid else None,
                    self.commit_repository)

    def add_note(self, obj, transaction, set_gid=True):
        """
        Add a Note to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(obj, transaction,
                    self.find_next_note_gramps_id if set_gid else None,
                    self.commit_note)

    def add_tag(self, obj, transaction):
        """
        Add a Tag to the database, assigning a handle if it has not already
        been defined.
        """
        return self.__add_object(obj, transaction, None, self.commit_tag)

    def __do_remove(self, handle, transaction, data_map, key):
        if self.readonly or not handle:
            return

        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        if transaction.batch:
            with BSDDBTxn(self.env, data_map) as txn:
                self.delete_primary_from_reference_map(handle, transaction,
                                                        txn=txn.txn)
                txn.delete(handle)
        else:
            self.delete_primary_from_reference_map(handle, transaction,
                                                   txn=self.txn)
            old_data = data_map.get(handle, txn=self.txn)
            data_map.delete(handle, txn=self.txn)
            transaction.add(key, TXNDEL, handle, old_data, None)

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.
        """

        if self.readonly or not handle:
            return
        person = self.get_person_from_handle(handle)
        self.genderStats.uncount_person (person)
        self.remove_from_surname_list(person)
        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        if transaction.batch:
            with BSDDBTxn(self.env, self.person_map) as txn:
                self.delete_primary_from_reference_map(handle, transaction,
                                                       txn=txn.txn)
                txn.delete(handle)
        else:
            self.delete_primary_from_reference_map(handle, transaction,
                                                   txn=self.txn)
            self.person_map.delete(handle, txn=self.txn)
            transaction.add(PERSON_KEY, TXNDEL, handle, person.serialize(), None)

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.source_map,
                              SOURCE_KEY)

    def remove_citation(self, handle, transaction):
        """
        Remove the Citation specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.citation_map,
                              CITATION_KEY)

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.event_map,
                              EVENT_KEY)

    def remove_media(self, handle, transaction):
        """
        Remove the MediaPerson specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.media_map,
                              MEDIA_KEY)

    def remove_place(self, handle, transaction):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.place_map,
                              PLACE_KEY)

    def remove_family(self, handle, transaction):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.family_map,
                              FAMILY_KEY)

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.repository_map,
                              REPOSITORY_KEY)

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.note_map,
                              NOTE_KEY)

    def remove_tag(self, handle, transaction):
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self.__do_remove(handle, transaction, self.tag_map,
                              TAG_KEY)

    @catch_db_error
    def set_name_group_mapping(self, name, group):
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.name_group) as txn:
                sname = name.encode('utf-8')
                data = txn.get(sname)
                if data is not None:
                    txn.delete(sname)
                if group is not None:
                    txn.put(sname, group)
            if group is None:
                grouppar = ''
            else:
                grouppar = group
            self.emit('person-groupname-rebuild', (name, grouppar))

    def sort_surname_list(self):
        self.surname_list.sort(key=glocale.sort_key)

    @catch_db_error
    def build_surname_list(self):
        """
        Build surname list for use in autocompletion
        This is a list of unicode objects, which are decoded from the utf-8 in
        bsddb
        """
        self.surname_list = sorted(
                        [s.decode('utf-8') for s in self.surnames.keys()],
                        key=glocale.sort_key)

    def add_to_surname_list(self, person, batch_transaction):
        """
        Add surname to surname list
        """
        if batch_transaction:
            return
        name = find_surname_name(person.handle,
                                 person.get_primary_name().serialize())
        i = bisect.bisect(self.surname_list, name)
        if 0 < i <= len(self.surname_list):
            if self.surname_list[i-1] != name:
                self.surname_list.insert(i, name)
        else:
            self.surname_list.insert(i, name)

    @catch_db_error
    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database.

        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = find_surname_name(person.handle,
                                     person.get_primary_name().serialize())
        if isinstance(name, str):
            uname = name
            name = name.encode('utf-8')
        else:
            uname = str(name)
        try:
            cursor = self.surnames.cursor(txn=self.txn)
            cursor_position = cursor.set(name)
            if cursor_position is not None and cursor.count() == 1:
                #surname list contains unicode objects
                i = bisect.bisect(self.surname_list, uname)
                if 0 <= i-1 < len(self.surname_list):
                    del self.surname_list[i-1]
        except db.DBError as err:
            if str(err) == "(0, 'DB object has been closed')":
                pass # A batch transaction closes the surnames db table.
            else:
                raise
        finally:
            if 'cursor' in locals():
                cursor.close()

    def commit_base(self, obj, data_map, key, transaction, change_time):
        """
        Commit the specified object to the database, storing the changes as
        part of the transaction.
        """
        if self.readonly or not obj or not obj.handle:
            return

        obj.change = int(change_time or time.time())
        handle = obj.handle
        if isinstance(handle, str):
            handle = handle.encode('utf-8')

        self.update_reference_map(obj, transaction, self.txn)

        new_data = obj.serialize()
        old_data = None
        if not transaction.batch:
            old_data = data_map.get(handle, txn=self.txn)
            op = TXNUPD if old_data else TXNADD
            transaction.add(key, op, handle, old_data, new_data)
        data_map.put(handle, new_data, txn=self.txn)
        return old_data

    def commit_person(self, person, transaction, change_time=None):
        """
        Commit the specified Person to the database, storing the changes as
        part of the transaction.
        """
        old_data = self.commit_base(
            person, self.person_map, PERSON_KEY, transaction, change_time)

        if old_data:
            old_person = Person(old_data)

            # Update gender statistics if necessary
            if (old_person.gender != person.gender or
                old_person.primary_name.first_name !=
                  person.primary_name.first_name):

                self.genderStats.uncount_person(old_person)
                self.genderStats.count_person(person)

            # Update surname list if necessary
            if (find_surname_name(old_person.handle,
                                  old_person.primary_name.serialize()) !=
                    find_surname_name(person.handle,
                                  person.primary_name.serialize())):
                self.remove_from_surname_list(old_person)
                self.add_to_surname_list(person, transaction.batch)
        else:
            self.genderStats.count_person(person)
            self.add_to_surname_list(person, transaction.batch)

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

    def commit_media(self, obj, transaction, change_time=None):
        """
        Commit the specified Media to the database, storing the changes
        as part of the transaction.
        """
        self.commit_base(obj, self.media_map, MEDIA_KEY,
                            transaction, change_time)

        self.media_attributes.update(
            [str(attr.type) for attr in obj.attribute_list
             if attr.type.is_custom() and str(attr.type)])

    def commit_source(self, source, transaction, change_time=None):
        """
        Commit the specified Source to the database, storing the changes as
        part of the transaction.
        """
        self.commit_base(source, self.source_map, SOURCE_KEY,
                          transaction, change_time)

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

    def commit_citation(self, citation, transaction, change_time=None):
        """
        Commit the specified Citation to the database, storing the changes as
        part of the transaction.
        """
        self.commit_base(citation, self.citation_map, CITATION_KEY,
                          transaction, change_time)

        attr_list = []
        for mref in citation.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

        self.source_attributes.update(
            [str(attr.type) for attr in citation.attribute_list
             if attr.type.is_custom() and str(attr.type)])

    def commit_place(self, place, transaction, change_time=None):
        """
        Commit the specified Place to the database, storing the changes as
        part of the transaction.
        """
        self.commit_base(place, self.place_map, PLACE_KEY,
                          transaction, change_time)

        if place.get_type().is_custom():
            self.place_types.add(str(place.get_type()))

        self.url_types.update([str(url.type) for url in place.urls
                               if url.type.is_custom()])

        attr_list = []
        for mref in place.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_personal_event(self, event, transaction, change_time=None):
        """
        Deprecated:  Use commit_event
        """
        self.commit_event(event, transaction, change_time)

    def commit_family_event(self, event, transaction, change_time=None):
        """
        Deprecated:  Use commit_event
        """
        self.commit_event(event, transaction, change_time)

    def commit_event(self, event, transaction, change_time=None):
        """
        Commit the specified Event to the database, storing the changes as
        part of the transaction.
        """
        self.commit_base(event, self.event_map, EVENT_KEY,
                  transaction, change_time)

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

    def commit_family(self, family, transaction, change_time=None):
        """
        Commit the specified Family to the database, storing the changes as
        part of the transaction.
        """
        self.commit_base(family, self.family_map, FAMILY_KEY,
                          transaction, change_time)

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

    def commit_repository(self, repository, transaction, change_time=None):
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        self.commit_base(repository, self.repository_map, REPOSITORY_KEY,
                          transaction, change_time)

        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update([str(url.type) for url in repository.urls
                               if url.type.is_custom()])

    def commit_note(self, note, transaction, change_time=None):
        """
        Commit the specified Note to the database, storing the changes as part
        of the transaction.
        """
        self.commit_base(note, self.note_map, NOTE_KEY,
                          transaction, change_time)

        if note.type.is_custom():
            self.note_types.add(str(note.type))

    def commit_tag(self, tag, transaction, change_time=None):
        """
        Commit the specified Tag to the database, storing the changes as part
        of the transaction.
        """
        self.commit_base(tag, self.tag_map, TAG_KEY,
                          transaction, change_time)

    def get_from_handle(self, handle, class_type, data_map):
        if isinstance(handle, str):
            handle = handle.encode('utf-8')
        if handle is None:
            raise HandleError('Handle is None')
        if not handle:
            raise HandleError('Handle is empty')
        data = data_map.get(handle, txn=self.txn)
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        raise HandleError('Handle %s not found' % handle.decode('utf-8'))

    @catch_db_error
    def transaction_begin(self, transaction):
        """
        Prepare the database for the start of a new Transaction.

        Supported transaction parameters:

        no_magic
          Boolean, defaults to False, indicating if secondary indices should be
          disconnected.
        """
        if self.txn is not None:
            msg = self.transaction.get_description()
            self.transaction_abort(self.transaction)
            raise DbError(_('A second transaction is started while there'
                ' is still a transaction, "%s", active in the database.') % msg)

        if not isinstance(transaction, DbTxn) or len(transaction) != 0:
            raise TypeError("transaction_begin must be called with an empty "
                    "instance of DbTxn which typically happens by using the "
                    "DbTxn instance as a context manager.")

        self.transaction = transaction
        if transaction.batch:
            # A batch transaction does not store the commits
            # Aborting the session completely will become impossible.
            self.abort_possible = False
            # Undo is also impossible after batch transaction
            self.undodb.clear()
            self.env.txn_checkpoint()

            if (self.secondary_connected and
                    not getattr(transaction, 'no_magic', False)):
                # Disconnect unneeded secondary indices
                self.surnames.close()
                _db = db.DB(self.env)
                try:
                    _db.remove(_mkname(self.full_name, SURNAMES), SURNAMES)
                except db.DBNoSuchFileError:
                    pass

                self.reference_map_referenced_map.close()
                _db = db.DB(self.env)
                try:
                    _db.remove(_mkname(self.full_name, REF_REF), REF_REF)
                except db.DBNoSuchFileError:
                    pass
        else:
            self.bsddbtxn = BSDDBTxn(self.env)
            self.txn = self.bsddbtxn.begin()
        return transaction

    @catch_db_error
    def transaction_commit(self, transaction):
        """
        Make the changes to the database final and add the content of the
        transaction to the undo database.
        """
        msg = transaction.get_description()
        if self._LOG_ALL:
            _LOG.debug("%s: Transaction commit '%s'\n"
                       % (self.__class__.__name__, msg))

        if self.readonly:
            return

        if self.txn is not None:
            assert msg != ''
            self.bsddbtxn.commit()
            self.bsddbtxn = None
            self.txn = None
        self.env.log_flush()
        if not transaction.batch:
            emit = self.__emit
            for obj_type, obj_name in KEY_TO_NAME_MAP.items():
                emit(transaction, obj_type, TXNADD, obj_name, '-add')
                emit(transaction, obj_type, TXNUPD, obj_name, '-update')
                emit(transaction, obj_type, TXNDEL, obj_name, '-delete')
        self.transaction = None
        transaction.clear()
        self.undodb.commit(transaction, msg)
        self.__after_commit(transaction)
        self.has_changed = True

    def __emit(self, transaction, obj_type, trans_type, obj, suffix):
        """
        Define helper function to do the actual emits
        """
        if (obj_type, trans_type) in transaction:
            if trans_type == TXNDEL:
                handles = [handle.decode('utf-8') for handle, data in
                            transaction[(obj_type, trans_type)]]
            else:
                handles = [handle.decode('utf-8') for handle, data in
                            transaction[(obj_type, trans_type)]
                            if (handle, None) not in transaction[(obj_type,
                                                                  TXNDEL)]]
            if handles:
                self.emit(obj + suffix, (handles, ))

    def transaction_abort(self, transaction):
        """
        Revert the changes made to the database so far during the transaction.
        """
        if self._LOG_ALL:
            _LOG.debug("%s: Transaction abort '%s'\n" %
                    (self.__class__.__name__, transaction.get_description()))

        if self.readonly:
            return

        if self.txn is not None:
            self.bsddbtxn.abort()
            self.bsddbtxn = None
            self.txn = None
        if not transaction.batch:
            # It can occur that the listview is already updated because of
            # the "model-treeview automatic update" combined with a
            # "while Gtk.events_pending(): Gtk.main_iteration() loop"
            # (typically used in a progress bar), so emit rebuild signals
            # to correct that.
            object_types = set([x[0] for x in list(transaction.keys())])
            for object_type in object_types:
                if object_type == REFERENCE_KEY:
                    continue
                self.emit('%s-rebuild' % KEY_TO_NAME_MAP[object_type], ())
        self.transaction = None
        transaction.clear()
        transaction.first = None
        transaction.last = None
        self.__after_commit(transaction)

    def __after_commit(self, transaction):
        """
        Post-transaction commit processing
        """
        if transaction.batch:
            self.env.txn_checkpoint()

            if not getattr(transaction, 'no_magic', False):
                # create new secondary indices to replace the ones removed

                self.surnames = self.__open_db(self.full_name, SURNAMES,
                                    db.DB_BTREE, db.DB_DUP | db.DB_DUPSORT)

                self.person_map.associate(self.surnames, find_byte_surname,
                                          DBFLAGS_O)

                self.reference_map_referenced_map = self.__open_db(self.full_name,
                    REF_REF, db.DB_BTREE, db.DB_DUP|db.DB_DUPSORT)

                self.reference_map.associate(self.reference_map_referenced_map,
                                             find_referenced_handle, DBFLAGS_O)

            # Only build surname list after surname index is surely back
            self.build_surname_list()

        # Reset callbacks if necessary
        if transaction.batch or not len(transaction):
            return
        if self.undo_callback:
            self.undo_callback(_("_Undo %s") % transaction.get_description())
        if self.redo_callback:
            self.redo_callback(None)
        if self.undo_history_callback:
            self.undo_history_callback()

    def undo(self, update_history=True):
        return self.undodb.undo(update_history)

    def redo(self, update_history=True):
        return self.undodb.redo(update_history)

    def gramps_upgrade(self, callback=None):
        UpdateCallback.__init__(self, callback)

        version = self.metadata.get(b'version', default=_MINVERSION)

        t = time.time()

        from . import upgrade

        if version < 14:
            upgrade.gramps_upgrade_14(self)
        if version < 15:
            upgrade.gramps_upgrade_15(self)
        if version < 16:
            upgrade.gramps_upgrade_16(self)
        if version < 17:
            upgrade.gramps_upgrade_17(self)
        if version < 18:
            upgrade.gramps_upgrade_18(self)

            self.reset()
            self.set_total(6)
            self.__connect_secondary()
            self.rebuild_secondary()
            # Open undo database
            self.__open_undodb()
            self.db_is_open = True
            self.reindex_reference_map(self.update)
            self.reset()
            # Close undo database
            self.__close_undodb()
            self.db_is_open = False


        _LOG.debug("Upgrade time: %d seconds" % int(time.time()-t))

    def set_auto_remove(self):
        """
        BSDDB change log settings using new method with renamed attributes
        """
        autoremove_flag = None
        autoremove_method = None
        for flag in ["DB_LOG_AUTO_REMOVE", "DB_LOG_AUTOREMOVE"]:
            if hasattr(db, flag):
                autoremove_flag = getattr(db, flag)
                break
        for method in ["log_set_config", "set_flags"]:
            if hasattr(self.env, method):
                autoremove_method = getattr(self.env, method)
                break
        if autoremove_method and autoremove_flag:
            autoremove_method(autoremove_flag, 1)
        else:
            _LOG.debug("Failed to set autoremove flag")

    def write_version(self, name):
        """Write version number for a newly created DB."""
        full_name = os.path.abspath(name)

        self.env = db.DBEnv()
        self.env.set_cachesize(0, DBCACHE)

        # These env settings are only needed for Txn environment
        self.env.set_lk_max_locks(DBLOCKS)
        self.env.set_lk_max_objects(DBOBJECTS)

        # clean up unused logs
        self.set_auto_remove()

        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE | db.DB_PRIVATE |\
                    db.DB_INIT_MPOOL |\
                    db.DB_INIT_LOG | db.DB_INIT_TXN

        # As opposed to before, we always try recovery on databases
        env_flags |= db.DB_RECOVER

        # Environment name is now based on the filename
        env_name = name

        self.env.open(env_name, env_flags)
        self.env.txn_checkpoint()

        self.metadata  = self.__open_shelf(full_name, META)

        _LOG.debug("Write schema version %s" % _DBVERSION)
        with BSDDBTxn(self.env, self.metadata) as txn:
            txn.put(b'version', _DBVERSION)

        versionpath = os.path.join(name, BDBVERSFN)
        version = str(db.version())
        _LOG.debug("Write bsddb version %s" % version)
        with open(versionpath, "w") as version_file:
            version_file.write(version)

        versionpath = os.path.join(name, "pythonversion.txt")
        version = str(version_info[0])
        _LOG.debug("Write python version file to %s" % version)
        with open(versionpath, "w") as version_file:
            version_file.write(version)

        versionpath = os.path.join(name, str(PCKVERSFN))
        _LOG.debug("Write pickle version file to %s" % "Yes")
        with open(versionpath, "w") as version_file:
            version = "Yes"
            version_file.write(version)

        versionpath = os.path.join(name, str(SCHVERSFN))
        _LOG.debug("Write schema version file to %s" % str(_DBVERSION))
        with open(versionpath, "w") as version_file:
            version = str(_DBVERSION)
            version_file.write(version)

        versionpath = os.path.join(name, str(DBBACKEND))
        _LOG.debug("Write database backend file to 'bsddb'")
        with open(versionpath, "w") as version_file:
            version_file.write("bsddb")

        self.metadata.close()
        self.env.close()

    def get_dbid(self):
        """
        In BSDDB, we use the file directory name as the unique ID for
        this database on this computer.
        """
        return self.brief_name

    def get_transaction_class(self):
        """
        Get the transaction class associated with this database backend.
        """
        return DbTxn

    def backup(self, user=None):
        """
        Exports the database to a set of backup files. These files consist
        of the pickled database tables, one file for each table.

        The heavy lifting is done by the private :py:func:`__do__export` function.
        The purpose of this function is to catch any exceptions that occur.

        :param database: database instance to backup
        :type database: DbDir
        """
        try:
            do_export(self)
        except (OSError, IOError) as msg:
            raise DbException(str(msg))

    def restore(self):
        """
        Restores the database to a set of backup files. These files consist
        of the pickled database tables, one file for each table.

        The heavy lifting is done by the private :py:func:`__do__restore` function.
        The purpose of this function is to catch any exceptions that occur.

        :param database: database instance to restore
        :type database: DbDir
        """
        try:
            do_restore(self)
        except (OSError, IOError) as msg:
            raise DbException(str(msg))

    def get_summary(self):
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Schema version")
        """
        schema_version = self.metadata.get(b'version', default=None)
        bdbversion_file = os.path.join(self.path, BDBVERSFN)
        if os.path.isfile(bdbversion_file):
            with open(bdbversion_file) as vers_file:
                bsddb_version = vers_file.readline().strip()
                bsddb_version = ".".join([str(v) for v in safe_eval(bsddb_version)])
        else:
            bsddb_version = _("Unknown")
        return {
            _("DB-API version"): "n/a", 
            _("Number of people"): self.get_number_of_people(),
            _("Number of families"): self.get_number_of_families(),
            _("Number of sources"): self.get_number_of_sources(),
            _("Number of citations"): self.get_number_of_citations(),
            _("Number of events"): self.get_number_of_events(),
            _("Number of media"): self.get_number_of_media(),
            _("Number of places"): self.get_number_of_places(),
            _("Number of repositories"): self.get_number_of_repositories(),
            _("Number of notes"): self.get_number_of_notes(),
            _("Number of tags"): self.get_number_of_tags(),
            _("Data version"): schema_version,
            _("Database db version"): bsddb_version,
        }

def mk_backup_name(database, base):
    """
    Return the backup name of the database table

    :param database: database instance
    :type database: DbDir
    :param base: base name of the table
    :type base: str
    """
    return os.path.join(database.get_save_path(), base + ".gbkp")

def mk_tmp_name(database, base):
    """
    Return the temporary backup name of the database table

    :param database: database instance
    :type database: DbDir
    :param base: base name of the table
    :type base: str
    """
    return os.path.join(database.get_save_path(), base + ".gbkp.new")

def do_export(database):
    """
    Loop through each table of the database, saving the pickled data
    a file.

    :param database: database instance to backup
    :type database: DbDir
    """
    try:
        for (base, tbl) in build_tbl_map(database):
            backup_name = mk_tmp_name(database, base)
            with open(backup_name, 'wb') as backup_table:

                cursor = tbl.cursor()
                data = cursor.first()
                while data:
                    pickle.dump(data, backup_table, 2)
                    data = cursor.next()
                cursor.close()
    except (IOError,OSError):
        return

    for (base, tbl) in build_tbl_map(database):
        new_name = mk_backup_name(database, base)
        old_name = mk_tmp_name(database, base)
        if os.path.isfile(new_name):
            os.unlink(new_name)
        os.rename(old_name, new_name)

def do_restore(database):
    """
    Loop through each table of the database, restoring the pickled data
    to the appropriate database file.

    :param database: database instance to backup
    :type database: DbDir
    """
    for (base, tbl) in build_tbl_map(database):
        backup_name = mk_backup_name(database, base)
        with open(backup_name, 'rb') as backup_table:
            load_tbl_txn(database, backup_table, tbl)

    database.rebuild_secondary()

def load_tbl_txn(database, backup_table, tbl):
    """
    Return the temporary backup name of the database table

    :param database: database instance
    :type database: DbDir
    :param backup_table: file containing the backup data
    :type backup_table: file
    :param tbl: Berkeley db database table
    :type tbl: Berkeley db database table
    """
    try:
        while True:
            data = pickle.load(backup_table)
            txn = database.env.txn_begin()
            tbl.put(data[0], data[1], txn=txn)
            txn.commit()
    except EOFError:
        backup_table.close()

def build_tbl_map(database):
    """
    Builds a table map of names to database tables.

    :param database: database instance to backup
    :type database: DbDir
    """
    return [
        ( PERSON_TBL,  database.person_map.db),
        ( FAMILY_TBL,  database.family_map.db),
        ( PLACES_TBL,  database.place_map.db),
        ( SOURCES_TBL, database.source_map.db),
        ( CITATIONS_TBL, database.citation_map.db),
        ( REPO_TBL,    database.repository_map.db),
        ( NOTE_TBL,    database.note_map.db),
        ( MEDIA_TBL,   database.media_map.db),
        ( EVENTS_TBL,  database.event_map.db),
        ( TAG_TBL,     database.tag_map.db),
        ( META,        database.metadata.db),
        ]

def _mkname(path, name):
    return os.path.join(path, name + DBEXT)

def clear_lock_file(name):
    try:
        os.unlink(os.path.join(name, DBLOCKFN))
    except OSError:
        return

def write_lock_file(name):
    if not os.path.isdir(name):
        os.mkdir(name)
    with open(os.path.join(name, DBLOCKFN), "w", encoding='utf8') as f:
        if win():
            user = get_env_var('USERNAME')
            host = get_env_var('USERDOMAIN')
            if host is None:
                host = ""
        else:
            host = os.uname()[1]
            # An ugly workaround for os.getlogin() issue with Konsole
            try:
                user = os.getlogin()
            except:
                # not win, so don't need get_env_var.
                # under cron getlogin() throws and there is no USER.
                user = os.environ.get('USER', 'noUSER')
        if host:
            text = "%s@%s" % (user, host)
        else:
            text = user
        # Save only the username and host, so the massage can be
        # printed with correct locale in DbManager.py when a lock is found
        f.write(text)

def upgrade_researcher(owner_data):
    """
    Upgrade researcher data to include a locality field in the address.
    This should be called for databases prior to Gramps 3.3.
    """
    addr = tuple([owner_data[0][0], ''] + list(owner_data[0][1:]))
    return (addr, owner_data[1], owner_data[2], owner_data[3])

