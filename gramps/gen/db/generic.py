#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Gramps Development Team
# Copyright (C) 2016      Nick Hall
# Copyright (C) 2024      Doug Blank
# Copyright (C) 2024,2025 Steve Youngs <steve@youngs.cc>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Gramps generic database handler
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from __future__ import annotations
import bisect
from collections.abc import Iterator
import logging
import os
import pickle
import random
import re
import time
from pathlib import Path
from typing import Any, Callable, cast, Literal, Type

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..errors import HandleError
from ..lib import (
    Citation,
    Event,
    Family,
    Media,
    NameOriginType,
    Note,
    Person,
    Place,
    Repository,
    Source,
    Tag,
)
from ..lib.serialize import BlobSerializer, JSONSerializer
from ..lib.genderstats import GenderStats
from ..lib.researcher import Researcher
from ..types import (
    AnyHandle,
    PersonHandle,
    EventHandle,
    FamilyHandle,
    PlaceHandle,
    SourceHandle,
    RepositoryHandle,
    CitationHandle,
    MediaHandle,
    NoteHandle,
    TagHandle,
    AnyObject,
    TableObjectType,
    PersonGrampsID,
    EventGrampsID,
    FamilyGrampsID,
    PlaceGrampsID,
    SourceGrampsID,
    RepositoryGrampsID,
    CitationGrampsID,
    MediaGrampsID,
    NoteGrampsID,
    PrimaryObjectGrampsID,
    PersonDataDict,
    EventDataDict,
    FamilyDataDict,
    PlaceDataDict,
    SourceDataDict,
    RepositoryDataDict,
    CitationDataDict,
    MediaDataDict,
    NoteDataDict,
    TagDataDict,
    AnyDataDict,
)
from ..updatecallback import UpdateCallback
from ..utils.callback import Callback
from ..utils.id import create_id
from . import (
    CITATION_KEY,
    DBLOGNAME,
    DBMODE_R,
    DBMODE_W,
    DBUNDOFN,
    EVENT_KEY,
    FAMILY_KEY,
    KEY_TO_NAME_MAP,
    MEDIA_KEY,
    NOTE_KEY,
    PERSON_KEY,
    PLACE_KEY,
    REFERENCE_KEY,
    REPOSITORY_KEY,
    SOURCE_KEY,
    TAG_KEY,
    TXNADD,
    TXNDEL,
    TXNUPD,
    DbReadBase,
    DbTxn,
    DbUndo,
    DbWriteBase,
)
from .bookmarks import DbBookmarks
from .exceptions import DbUpgradeRequiredError, DbVersionError
from .utils import clear_lock_file, write_lock_file

_ = glocale.translation.gettext

LOG = logging.getLogger(DBLOGNAME)

SIGBASE = (
    "person",
    "family",
    "source",
    "event",
    "media",
    "place",
    "repository",
    "reference",
    "note",
    "tag",
    "citation",
)


# ------------------------------------------------------------------------
#
# DbGenericUndo class
#
# ------------------------------------------------------------------------
class DbGenericUndo(DbUndo):
    """
    Generic undo/redo handler
    """

    undodb: list

    def __init__(self, grampsdb: DbGeneric, path) -> None:
        super().__init__(grampsdb)
        self.undodb = []

    def open(self, value=None) -> None:
        """
        Open the backing storage.  Needs to be overridden in the derived
        class.
        """

    def close(self) -> None:
        """
        Close the backing storage.  Needs to be overridden in the derived
        class.
        """

    def append(self, value) -> None:
        """
        Add a new entry on the end.  Needs to be overridden in the derived
        class.
        """
        self.undodb.append(value)

    def __getitem__(self, index: int):
        """
        Returns an entry by index number.  Needs to be overridden in the
        derived class.
        """
        return self.undodb[index]

    def __setitem__(self, index: int, value) -> None:
        """
        Set an entry to a value.  Needs to be overridden in the derived class.
        """
        self.undodb[index] = value

    def __len__(self) -> int:
        """
        Returns the number of entries.  Needs to be overridden in the derived
        class.
        """
        return len(self.undodb)

    def _redo(self, update_history: bool) -> bool:
        """
        Access the last undone transaction, and revert the data to the state
        before the transaction was undone.
        """
        txn = self.redoq.pop()
        self.undoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos()
        # sigs[obj_type][trans_type]
        sigs: list[list[list[AnyHandle]]] = [
            [[] for trans_type in range(3)] for key in range(11)
        ]

        # Process all records in the transaction
        try:
            self.db._txn_begin()
            for record_id in subitems:
                key, trans_type, handle, __, new_data = pickle.loads(
                    self.undodb[record_id]
                )

                if key == REFERENCE_KEY:
                    self.db.undo_reference(new_data, handle)
                else:
                    self.db.undo_data(new_data, handle, key)
                    sigs[key][trans_type].append(handle)
            # now emit the signals
            self.undo_sigs(sigs, False)

            self.db._txn_commit()
        except:
            self.db._txn_abort()
            raise

        # Notify listeners
        if db.undo_callback:
            db.undo_callback(_("_Undo %s") % transaction.get_description())

        if db.redo_callback:
            if self.redo_count > 1:
                new_transaction = self.redoq[-2]
                db.redo_callback(_("_Redo %s") % new_transaction.get_description())
            else:
                db.redo_callback(None)

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

    def _undo(self, update_history: bool) -> bool:
        """
        Access the last committed transaction, and revert the data to the
        state before the transaction was committed.
        """
        txn = self.undoq.pop()
        self.redoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos(reverse=True)
        # sigs[obj_type][trans_type]
        sigs: list[list[list[AnyHandle]]] = [
            [[] for trans_type in range(3)] for key in range(11)
        ]

        # Process all records in the transaction
        try:
            self.db._txn_begin()
            for record_id in subitems:
                key, trans_type, handle, old_data, x = pickle.loads(
                    self.undodb[record_id]
                )

                if key == REFERENCE_KEY:
                    self.db.undo_reference(old_data, handle)
                else:
                    self.db.undo_data(old_data, handle, key)
                    sigs[key][trans_type].append(handle)
            # now emit the signals
            self.undo_sigs(sigs, True)

            self.db._txn_commit()
        except:
            self.db._txn_abort()
            raise

        # Notify listeners
        if db.undo_callback:
            if self.undo_count > 0:
                db.undo_callback(_("_Undo %s") % self.undoq[-1].get_description())
            else:
                db.undo_callback(None)

        if db.redo_callback:
            db.redo_callback(_("_Redo %s") % transaction.get_description())

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

    def undo_sigs(self, sigs: list[list[list[AnyHandle]]], undo: bool) -> None:
        """
        Helper method to undo/redo the signals for changes made
        We want to do deletes and adds first
        Note that if 'undo' we swap emits
        """
        for trans_type in [TXNDEL, TXNADD, TXNUPD]:
            for obj_type in range(11):
                handles = sigs[obj_type][trans_type]
                if handles:
                    if (
                        not undo
                        and trans_type == TXNDEL
                        or undo
                        and trans_type == TXNADD
                    ):
                        typ = "-delete"
                    else:
                        # don't update a handle if its been deleted, and note
                        # that 'deleted' handles are in the 'add' list if we
                        # are undoing
                        handles = [
                            handle
                            for handle in handles
                            if handle not in sigs[obj_type][TXNADD if undo else TXNDEL]
                        ]
                        if ((not undo) and trans_type == TXNADD) or (
                            undo and trans_type == TXNDEL
                        ):
                            typ = "-add"
                        else:  # TXNUPD
                            typ = "-update"
                    if handles:
                        self.db.emit(KEY_TO_NAME_MAP[obj_type] + typ, (handles,))


# ------------------------------------------------------------------------
#
# Cursor class
#
# ------------------------------------------------------------------------
class Cursor:
    """
    Simple iteration handler
    """

    def __init__(self, iterator) -> None:
        self.iterator = iterator
        self._iter = self.__iter__()

    def __enter__(self) -> Cursor:
        return self

    def __iter__(self) -> Iterator[tuple[AnyHandle, AnyDataDict]]:
        for handle, data in self.iterator():
            yield (handle, data)

    def __next__(self) -> tuple[AnyHandle, AnyDataDict] | None:
        try:
            return self._iter.__next__()
        except StopIteration:
            return None

    def __exit__(self, *args, **kwargs):
        pass

    def iter(self) -> Iterator[tuple[AnyHandle, AnyDataDict]]:
        for handle, data in self.iterator():
            yield (handle, data)

    def first(self) -> tuple[AnyHandle, AnyDataDict] | None:
        self._iter = self.__iter__()
        try:
            return next(self._iter)
        except:
            return None

    def next(self) -> tuple[AnyHandle, AnyDataDict] | None:
        try:
            return next(self._iter)
        except:
            return None

    def close(self) -> None:
        pass


# ------------------------------------------------------------------------
#
# DbGeneric class
#
# ------------------------------------------------------------------------


class DbGeneric(DbWriteBase, DbReadBase, UpdateCallback, Callback):
    """
    A Gramps Database Backend. This replicates the grampsdb functions.
    """

    __signals__: dict[str, Any] = dict(
        (obj + "-" + op, signal)
        for obj in [
            "person",
            "family",
            "event",
            "place",
            "repository",
            "source",
            "citation",
            "media",
            "note",
            "tag",
        ]
        for op, signal in zip(
            ["add", "update", "delete", "rebuild"], [(list,), (list,), (list,), None]
        )
    )

    # 2. Signals for long operations
    __signals__.update(
        ("long-op-" + op, signal)
        for op, signal in zip(["start", "heartbeat", "end"], [(object,), None, None])
    )

    # 3. Special signal for change in home person
    __signals__["home-person-changed"] = None

    # 4. Signal for change in person group name, parameters are
    __signals__["person-groupname-rebuild"] = (str, str)

    __callback_map = {}

    VERSION = (22, 0, 0)

    serializer: type[BlobSerializer] | type[JSONSerializer]
    readonly: bool
    db_is_open: bool
    name_formats: list[tuple[int, str, str, bool]]
    bookmarks: DbBookmarks
    family_bookmarks: DbBookmarks
    event_bookmarks: DbBookmarks
    place_bookmarks: DbBookmarks
    citation_bookmarks: DbBookmarks
    source_bookmarks: DbBookmarks
    repo_bookmarks: DbBookmarks
    media_bookmarks: DbBookmarks
    note_bookmarks: DbBookmarks
    event_names: set[str]
    family_attributes: set[str]
    individual_attributes: set[str]
    source_attributes: set[str]
    marker_names: set[str]
    child_ref_types: set[str]
    family_rel_types: set[str]
    event_role_names: set[str]
    name_types: set[str]
    origin_types: set[str]
    repository_types: set[str]
    note_types: set[str]
    source_media_types: set[str]
    url_types: set[str]
    media_attributes: set[str]
    event_attributes: set[str]
    place_types: set[str]
    undodb: DbGenericUndo | None
    undolog: str | None
    cmap_index: int
    smap_index: int
    emap_index: int
    pmap_index: int
    fmap_index: int
    lmap_index: int
    omap_index: int
    rmap_index: int
    nmap_index: int
    undo_callback: Callable[[str | None], None] | None
    redo_callback: Callable[[str | None], None] | None
    undo_history_callback: Callable[[], None] | None
    modified: int
    transaction: DbTxn | None
    abort_possible: bool
    _bm_changes: int
    has_changed: int
    surname_list: list[str]
    genderStats: GenderStats
    owner: Researcher

    def __init__(self, directory: str | None = None) -> None:
        DbReadBase.__init__(self)
        DbWriteBase.__init__(self)
        Callback.__init__(self)
        self.__tables = {
            "Person": {
                "handle_func": self.get_person_from_handle,
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                "add_func": self.add_person,
                "commit_func": self.commit_person,
                "iter_func": self.iter_people,
                "ids_func": self.get_person_gramps_ids,
                "has_handle_func": self.has_person_handle,
                "has_gramps_id_func": self.has_person_gramps_id,
                "count_func": self.get_number_of_people,
                "raw_func": self.get_raw_person_data,
                "raw_id_func": self._get_raw_person_from_id_data,
                "del_func": self.remove_person,
            },
            "Family": {
                "handle_func": self.get_family_from_handle,
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                "add_func": self.add_family,
                "commit_func": self.commit_family,
                "iter_func": self.iter_families,
                "ids_func": self.get_family_gramps_ids,
                "has_handle_func": self.has_family_handle,
                "has_gramps_id_func": self.has_family_gramps_id,
                "count_func": self.get_number_of_families,
                "raw_func": self.get_raw_family_data,
                "raw_id_func": self._get_raw_family_from_id_data,
                "del_func": self.remove_family,
            },
            "Source": {
                "handle_func": self.get_source_from_handle,
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                "add_func": self.add_source,
                "commit_func": self.commit_source,
                "iter_func": self.iter_sources,
                "ids_func": self.get_source_gramps_ids,
                "has_handle_func": self.has_source_handle,
                "has_gramps_id_func": self.has_source_gramps_id,
                "count_func": self.get_number_of_sources,
                "raw_func": self.get_raw_source_data,
                "raw_id_func": self._get_raw_source_from_id_data,
                "del_func": self.remove_source,
            },
            "Citation": {
                "handle_func": self.get_citation_from_handle,
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                "add_func": self.add_citation,
                "commit_func": self.commit_citation,
                "iter_func": self.iter_citations,
                "ids_func": self.get_citation_gramps_ids,
                "has_handle_func": self.has_citation_handle,
                "has_gramps_id_func": self.has_citation_gramps_id,
                "count_func": self.get_number_of_citations,
                "raw_func": self.get_raw_citation_data,
                "raw_id_func": self._get_raw_citation_from_id_data,
                "del_func": self.remove_citation,
            },
            "Event": {
                "handle_func": self.get_event_from_handle,
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                "add_func": self.add_event,
                "commit_func": self.commit_event,
                "iter_func": self.iter_events,
                "ids_func": self.get_event_gramps_ids,
                "has_handle_func": self.has_event_handle,
                "has_gramps_id_func": self.has_event_gramps_id,
                "count_func": self.get_number_of_events,
                "raw_func": self.get_raw_event_data,
                "raw_id_func": self._get_raw_event_from_id_data,
                "del_func": self.remove_event,
            },
            "Media": {
                "handle_func": self.get_media_from_handle,
                "gramps_id_func": self.get_media_from_gramps_id,
                "class_func": Media,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_handles,
                "add_func": self.add_media,
                "commit_func": self.commit_media,
                "iter_func": self.iter_media,
                "ids_func": self.get_media_gramps_ids,
                "has_handle_func": self.has_media_handle,
                "has_gramps_id_func": self.has_media_gramps_id,
                "count_func": self.get_number_of_media,
                "raw_func": self.get_raw_media_data,
                "raw_id_func": self._get_raw_media_from_id_data,
                "del_func": self.remove_media,
            },
            "Place": {
                "handle_func": self.get_place_from_handle,
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                "add_func": self.add_place,
                "commit_func": self.commit_place,
                "iter_func": self.iter_places,
                "ids_func": self.get_place_gramps_ids,
                "has_handle_func": self.has_place_handle,
                "has_gramps_id_func": self.has_place_gramps_id,
                "count_func": self.get_number_of_places,
                "raw_func": self.get_raw_place_data,
                "raw_id_func": self._get_raw_place_from_id_data,
                "del_func": self.remove_place,
            },
            "Repository": {
                "handle_func": self.get_repository_from_handle,
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                "add_func": self.add_repository,
                "commit_func": self.commit_repository,
                "iter_func": self.iter_repositories,
                "ids_func": self.get_repository_gramps_ids,
                "has_handle_func": self.has_repository_handle,
                "has_gramps_id_func": self.has_repository_gramps_id,
                "count_func": self.get_number_of_repositories,
                "raw_func": self.get_raw_repository_data,
                "raw_id_func": self._get_raw_repository_from_id_data,
                "del_func": self.remove_repository,
            },
            "Note": {
                "handle_func": self.get_note_from_handle,
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                "add_func": self.add_note,
                "commit_func": self.commit_note,
                "iter_func": self.iter_notes,
                "ids_func": self.get_note_gramps_ids,
                "has_handle_func": self.has_note_handle,
                "has_gramps_id_func": self.has_note_gramps_id,
                "count_func": self.get_number_of_notes,
                "raw_func": self.get_raw_note_data,
                "raw_id_func": self._get_raw_note_from_id_data,
                "del_func": self.remove_note,
            },
            "Tag": {
                "handle_func": self.get_tag_from_handle,
                "gramps_id_func": None,
                "class_func": Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                "add_func": self.add_tag,
                "commit_func": self.commit_tag,
                "has_handle_func": self.has_tag_handle,
                "iter_func": self.iter_tags,
                "count_func": self.get_number_of_tags,
                "raw_func": self.get_raw_tag_data,
                "del_func": self.remove_tag,
            },
        }
        self._directory = None
        self.path = None
        self.full_name = None
        self.brief_name = None
        self.readonly = False
        self.db_is_open = False
        self.name_formats = []
        # Bookmarks:
        self.bookmarks = DbBookmarks()
        self.family_bookmarks = DbBookmarks()
        self.event_bookmarks = DbBookmarks()
        self.place_bookmarks = DbBookmarks()
        self.citation_bookmarks = DbBookmarks()
        self.source_bookmarks = DbBookmarks()
        self.repo_bookmarks = DbBookmarks()
        self.media_bookmarks = DbBookmarks()
        self.note_bookmarks = DbBookmarks()
        self.set_person_id_prefix("I%05d")
        self.set_media_id_prefix("O%05d")
        self.set_family_id_prefix("F%05d")
        self.set_citation_id_prefix("C%05d")
        self.set_source_id_prefix("S%05d")
        self.set_place_id_prefix("P%05d")
        self.set_event_id_prefix("E%05d")
        self.set_repository_id_prefix("R%05d")
        self.set_note_id_prefix("N%05d")
        # Custom type values
        self.event_names = set()
        self.family_attributes = set()
        self.individual_attributes = set()
        self.source_attributes = set()
        self.marker_names = set()
        self.child_ref_types = set()
        self.family_rel_types = set()
        self.event_role_names = set()
        self.name_types = set()
        self.origin_types = set()
        self.repository_types = set()
        self.note_types = set()
        self.source_media_types = set()
        self.url_types = set()
        self.media_attributes = set()
        self.event_attributes = set()
        self.place_types = set()
        # ----------------------------------
        self.undodb = None
        self.cmap_index = 0
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.rmap_index = 0
        self.nmap_index = 0
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified = 0
        self.transaction = None
        self.abort_possible = True
        self._bm_changes = 0
        self.has_changed = 0  # Also gives commits since startup
        self.surname_list = []
        self.genderStats = GenderStats()  # can pass in loaded stats as dict
        self.owner = Researcher()
        if directory:
            self.load(directory)

    def _initialize(self, directory, username, password) -> None:
        """
        Initialize database backend.
        """
        raise NotImplementedError

    def upgrade_table_for_json_data(self, table_name: str) -> None:
        """
        Overload this method to upgrade the table to store data in JSON format
        """
        raise NotImplementedError

    def use_json_data(self) -> bool:
        """
        Overload this method to check if the database stores objects in JSON format
        """
        raise NotImplementedError

    def __check_readonly(self, name: str) -> bool:
        """
        Return True if we don't have read/write access to the database,
        otherwise return False (that is, we DO have read/write access)
        """
        # In-memory databases always allow write access.
        if name == ":memory:":
            return False

        # See if we write to the target directory at all?
        if not os.access(name, os.W_OK):
            return True

        # See if we lack write access to the database file
        path = os.path.join(name, "sqlite.db")
        if os.path.isfile(path) and not os.access(path, os.W_OK):
            return True

        # All tests passed.  Inform caller that we are NOT read only
        return False

    def _schema_exists(self) -> bool:
        """
        Overload this method to see if the schema exists.
        """
        raise NotImplementedError

    def _create_schema(self, json_data: bool) -> None:
        """
        Overload this method to create and update the schema
        """
        raise NotImplementedError

    def load(
        self,
        directory,
        callback=None,
        mode: str = DBMODE_W,
        force_schema_upgrade: bool = False,
        force_bsddb_upgrade: bool = False,
        force_bsddb_downgrade: bool = False,
        force_python_upgrade: bool = False,
        update: bool = True,
        username: str | None = None,
        password: str | None = None,
        json_data: bool = True,
    ) -> None:
        """
        If update is False: then don't update any files
        """
        if self.__check_readonly(directory):
            mode = DBMODE_R

        self.readonly = mode == DBMODE_R

        if not self.readonly and directory != ":memory:":
            write_lock_file(directory)

        # run backend-specific code:
        self._initialize(directory, username, password)

        need_to_set_metadata = False
        if not self._schema_exists():
            self._create_schema(json_data)
            need_to_set_metadata = True

        if self.use_json_data():
            self.set_serializer("json")
        else:
            self.set_serializer("blob")

        if need_to_set_metadata:
            self._set_metadata("version", str(self.VERSION[0]))

        # Load metadata
        self.name_formats = self._get_metadata("name_formats")
        self.owner = self._get_metadata("researcher", default=Researcher())

        # Load bookmarks
        self.bookmarks.load(self._get_metadata("bookmarks"))
        self.family_bookmarks.load(self._get_metadata("family_bookmarks"))
        self.event_bookmarks.load(self._get_metadata("event_bookmarks"))
        self.source_bookmarks.load(self._get_metadata("source_bookmarks"))
        self.citation_bookmarks.load(self._get_metadata("citation_bookmarks"))
        self.repo_bookmarks.load(self._get_metadata("repo_bookmarks"))
        self.media_bookmarks.load(self._get_metadata("media_bookmarks"))
        self.place_bookmarks.load(self._get_metadata("place_bookmarks"))
        self.note_bookmarks.load(self._get_metadata("note_bookmarks"))

        # Custom type values
        self.event_names = self._get_metadata("event_names", set())
        self.family_attributes = self._get_metadata("fattr_names", set())
        self.individual_attributes = self._get_metadata("pattr_names", set())
        self.source_attributes = self._get_metadata("sattr_names", set())
        self.marker_names = self._get_metadata("marker_names", set())
        self.child_ref_types = self._get_metadata("child_refs", set())
        self.family_rel_types = self._get_metadata("family_rels", set())
        self.event_role_names = self._get_metadata("event_roles", set())
        self.name_types = self._get_metadata("name_types", set())
        self.origin_types = self._get_metadata("origin_types", set())
        self.repository_types = self._get_metadata("repo_types", set())
        self.note_types = self._get_metadata("note_types", set())
        self.source_media_types = self._get_metadata("sm_types", set())
        self.url_types = self._get_metadata("url_types", set())
        self.media_attributes = self._get_metadata("mattr_names", set())
        self.event_attributes = self._get_metadata("eattr_names", set())
        self.place_types = self._get_metadata("place_types", set())

        # surname list
        self.surname_list = self.get_surname_list()

        self._set_save_path(directory)

        if self._directory and self._directory != ":memory:":
            self.undolog = os.path.join(self._directory, DBUNDOFN)
        else:
            self.undolog = None
        self.undodb = self._create_undo_manager()
        self.undodb.open()

        # Other items to load
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)

        # Indexes:
        self.cmap_index = self._get_metadata("cmap_index", 0)
        self.smap_index = self._get_metadata("smap_index", 0)
        self.emap_index = self._get_metadata("emap_index", 0)
        self.pmap_index = self._get_metadata("pmap_index", 0)
        self.fmap_index = self._get_metadata("fmap_index", 0)
        self.lmap_index = self._get_metadata("lmap_index", 0)
        self.omap_index = self._get_metadata("omap_index", 0)
        self.rmap_index = self._get_metadata("rmap_index", 0)
        self.nmap_index = self._get_metadata("nmap_index", 0)

        if need_to_set_metadata:
            # for new db we always need blob metadata to allow prior Gramps versions
            # to make it to the downgrade version check
            # Note: downgrade check only works from v5.1.2 and later on sqlite
            self.set_serializer("blob")
            self.has_changed = 1  # to make sure genderstats gets saved
            self._set_all_metadata()
            if self.use_json_data():
                self.set_serializer("json")
                self._set_all_metadata()
            self.has_changed = 0  # number of commits

        self.db_is_open = True

        # Check on db version to see if we need upgrade or too new
        dbversion = int(self._get_metadata("version", default="0"))
        if dbversion > self.VERSION[0]:
            self.close()
            raise DbVersionError(dbversion, 18, self.VERSION[0])

        if not self.readonly and dbversion < self.VERSION[0]:
            LOG.debug(
                "Schema upgrade required from %s to %s", dbversion, self.VERSION[0]
            )
            if force_schema_upgrade:
                self._gramps_upgrade(dbversion, directory, callback)
            else:
                self.close(update=False)
                raise DbUpgradeRequiredError(dbversion, self.VERSION[0])

    def _create_undo_manager(self) -> DbGenericUndo:
        """
        Create the undo manager.
        """
        return DbGenericUndo(self, self.undolog)

    def _close(self) -> None:
        """
        Close database backend.
        """
        raise NotImplementedError

    def close(self, update: bool = True, user=None) -> None:
        """
        Close the database.
        if update is False, don't change access times, etc.
        """
        if self._directory is not None and self._directory != ":memory:":
            if update and not self.readonly:
                # This is just a dummy file to indicate last modified time of
                # the database for gramps.cli.clidbman:
                filename = os.path.join(self._directory, "meta_data.db")
                Path(filename).touch()
                self._set_all_metadata()

            self._close()

            try:
                clear_lock_file(self.get_save_path())
            except IOError:
                pass

        self.db_is_open = False
        self._directory = None

    def is_open(self) -> bool:
        return self.db_is_open

    def _set_all_metadata(self) -> None:
        """
        sets all the metadata
        """
        # Save metadata
        self._set_metadata("version", str(self.VERSION[0]))
        self._set_metadata("name_formats", self.name_formats)
        self._set_metadata("researcher", self.owner)

        # Bookmarks
        self._set_metadata("bookmarks", self.bookmarks.get())
        self._set_metadata("family_bookmarks", self.family_bookmarks.get())
        self._set_metadata("event_bookmarks", self.event_bookmarks.get())
        self._set_metadata("place_bookmarks", self.place_bookmarks.get())
        self._set_metadata("repo_bookmarks", self.repo_bookmarks.get())
        self._set_metadata("source_bookmarks", self.source_bookmarks.get())
        self._set_metadata("citation_bookmarks", self.citation_bookmarks.get())
        self._set_metadata("media_bookmarks", self.media_bookmarks.get())
        self._set_metadata("note_bookmarks", self.note_bookmarks.get())

        # Custom type values, sets
        self._set_metadata("event_names", self.event_names)
        self._set_metadata("fattr_names", self.family_attributes)
        self._set_metadata("pattr_names", self.individual_attributes)
        self._set_metadata("sattr_names", self.source_attributes)
        self._set_metadata("marker_names", self.marker_names)
        self._set_metadata("child_refs", self.child_ref_types)
        self._set_metadata("family_rels", self.family_rel_types)
        self._set_metadata("event_roles", self.event_role_names)
        self._set_metadata("name_types", self.name_types)
        self._set_metadata("origin_types", self.origin_types)
        self._set_metadata("repo_types", self.repository_types)
        self._set_metadata("note_types", self.note_types)
        self._set_metadata("sm_types", self.source_media_types)
        self._set_metadata("url_types", self.url_types)
        self._set_metadata("mattr_names", self.media_attributes)
        self._set_metadata("eattr_names", self.event_attributes)
        self._set_metadata("place_types", self.place_types)

        # Save misc items:
        if self.has_changed:
            self.save_gender_stats(self.genderStats)

        # Indexes:
        self._set_metadata("cmap_index", self.cmap_index)
        self._set_metadata("smap_index", self.smap_index)
        self._set_metadata("emap_index", self.emap_index)
        self._set_metadata("pmap_index", self.pmap_index)
        self._set_metadata("fmap_index", self.fmap_index)
        self._set_metadata("lmap_index", self.lmap_index)
        self._set_metadata("omap_index", self.omap_index)
        self._set_metadata("rmap_index", self.rmap_index)
        self._set_metadata("nmap_index", self.nmap_index)

    def get_dbid(self) -> str | None:
        """
        We use the file directory name as the unique ID for
        this database on this computer.
        """
        return self.brief_name

    def get_dbname(self) -> str | None:
        """
        In DbGeneric, the database is in a text file at the path
        """
        name = None
        if self._directory:
            filepath = os.path.join(self._directory, "name.txt")
            try:
                with open(filepath, "r", encoding="utf8") as name_file:
                    name = name_file.readline().strip()
            except (OSError, IOError) as msg:
                LOG.error(str(msg))
        return name

    def version_supported(self) -> bool:
        """Return True when the file has a supported version."""
        return True

    def _get_table_func(self, table=None, func=None):
        """
        Private implementation of get_table_func.
        """
        if table is None:
            return list(self.__tables.keys())
        if func is None:
            return self.__tables[table]  # dict of functions
        if func in self.__tables[table].keys():
            return self.__tables[table][func]
        return None

    def _txn_begin(self) -> None:
        """
        Lowlevel interface to the backend transaction.
        Executes a db BEGIN;
        """

    def _txn_commit(self) -> None:
        """
        Lowlevel interface to the backend transaction.
        Executes a db END;
        """

    def _txn_abort(self) -> None:
        """
        Lowlevel interface to the backend transaction.
        Executes a db ROLLBACK;
        """

    def transaction_begin(self, transaction: DbTxn) -> DbTxn:
        """
        Transactions are handled automatically by the db layer.
        """
        self.transaction = transaction
        return transaction

    def _get_metadata_keys(self) -> list[str]:
        """
        Get all of the metadata setting names from the
        database.
        """
        raise NotImplementedError

    def _get_metadata(self, key: str, default: Any = []) -> Any:
        """
        Get an item from the database.

        Default is an empty list, which is a mutable and
        thus a bad default (pylint will complain).

        However, it is just used as a value, and not altered, so
        its use here is ok.
        """
        raise NotImplementedError

    def _set_metadata(self, key, value, use_txn: bool = True) -> None:
        """
        key: string
        value: item, will be serialized here

        Note: if use_txn, then begin/commit txn
        """
        raise NotImplementedError

    ################################################################
    #
    # set_*_id_prefix methods
    #
    ################################################################

    @staticmethod
    def _validated_id_prefix(val, default: str) -> str:
        if isinstance(val, str) and val:
            try:
                _ = val % 1
            except TypeError:  # missing conversion specifier
                prefix_var = val + "%d"
            except ValueError:  # incomplete format
                prefix_var = default + "%05d"
            else:
                prefix_var = val  # OK as given
        else:
            prefix_var = default + "%05d"  # not a string or empty string
        return prefix_var

    @staticmethod
    def __id2user_format(id_pattern):
        """
        Return a method that accepts a Gramps ID and adjusts it to the users
        format.
        """
        pattern_match = re.match(r"(.*)%[0 ](\d+)[diu]$", id_pattern)
        if pattern_match:
            str_prefix = pattern_match.group(1)

            # nr_width = int(pattern_match.group(2))
            def closure_func(gramps_id):
                if gramps_id and gramps_id.startswith(str_prefix):
                    id_number = gramps_id[len(str_prefix) :]
                    if id_number.isdigit():
                        id_value = int(id_number, 10)
                        # if len(str(id_value)) > nr_width:
                        #    # The ID to be imported is too large to fit in the
                        #    # users format. For now just create a new ID,
                        #    # because that is also what happens with IDs that
                        #    # are identical to IDs already in the database. If
                        #    # the problem of colliding import and already
                        #    # present IDs is solved the code here also needs
                        #    # some solution.
                        #    gramps_id = id_pattern % 1
                        # else:
                        gramps_id = id_pattern % id_value
                return gramps_id

        else:

            def closure_func(gramps_id):
                return gramps_id

        return closure_func

    def set_person_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Person ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as I%d or I%05d.
        """
        self.person_prefix = self._validated_id_prefix(val, "I")
        self.id2user_format = self.__id2user_format(self.person_prefix)

    def set_citation_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Citation ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as C%d or C%05d.
        """
        self.citation_prefix = self._validated_id_prefix(val, "C")
        self.cid2user_format = self.__id2user_format(self.citation_prefix)

    def set_source_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Source ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as S%d or S%05d.
        """
        self.source_prefix = self._validated_id_prefix(val, "S")
        self.sid2user_format = self.__id2user_format(self.source_prefix)

    def set_media_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Media ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as O%d or O%05d.
        """
        self.media_prefix = self._validated_id_prefix(val, "O")
        self.oid2user_format = self.__id2user_format(self.media_prefix)

    def set_place_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Place ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as P%d or P%05d.
        """
        self.place_prefix = self._validated_id_prefix(val, "P")
        self.pid2user_format = self.__id2user_format(self.place_prefix)

    def set_family_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%05d.
        """
        self.family_prefix = self._validated_id_prefix(val, "F")
        self.fid2user_format = self.__id2user_format(self.family_prefix)

    def set_event_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Event ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as E%d or E%05d.
        """
        self.event_prefix = self._validated_id_prefix(val, "E")
        self.eid2user_format = self.__id2user_format(self.event_prefix)

    def set_repository_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Repository ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as R%d or R%05d.
        """
        self.repository_prefix = self._validated_id_prefix(val, "R")
        self.rid2user_format = self.__id2user_format(self.repository_prefix)

    def set_note_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Note ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as N%d or N%05d.
        """
        self.note_prefix = self._validated_id_prefix(val, "N")
        self.nid2user_format = self.__id2user_format(self.note_prefix)

    def set_prefixes(
        self,
        person: str,
        media: str,
        family: str,
        source: str,
        citation: str,
        place: str,
        event: str,
        repository: str,
        note: str,
    ) -> None:
        self.set_person_id_prefix(person)
        self.set_media_id_prefix(media)
        self.set_family_id_prefix(family)
        self.set_source_id_prefix(source)
        self.set_citation_id_prefix(citation)
        self.set_place_id_prefix(place)
        self.set_event_id_prefix(event)
        self.set_repository_id_prefix(repository)
        self.set_note_id_prefix(note)

    ################################################################
    #
    # find_next_*_gramps_id methods
    #
    ################################################################

    def _find_next_gramps_id(
        self, prefix: str, map_index: int, obj_key: int
    ) -> tuple[int, PrimaryObjectGrampsID]:
        """
        Helper function for find_next_<object>_gramps_id methods
        """
        index = cast(PrimaryObjectGrampsID, prefix % map_index)
        while self._has_gramps_id(obj_key, index):
            map_index += 1
            index = cast(PrimaryObjectGrampsID, prefix % map_index)
        map_index += 1
        return (map_index, index)

    def find_next_person_gramps_id(self) -> PersonGrampsID:
        """
        Return the next available GRAMPS' ID for a Person object based off the
        person ID prefix.
        """
        self.pmap_index, gid = self._find_next_gramps_id(
            self.person_prefix, self.pmap_index, PERSON_KEY
        )
        return cast(PersonGrampsID, gid)

    def find_next_place_gramps_id(self) -> PlaceGrampsID:
        """
        Return the next available GRAMPS' ID for a Place object based off the
        place ID prefix.
        """
        self.lmap_index, gid = self._find_next_gramps_id(
            self.place_prefix, self.lmap_index, PLACE_KEY
        )
        return cast(PlaceGrampsID, gid)

    def find_next_event_gramps_id(self) -> EventGrampsID:
        """
        Return the next available GRAMPS' ID for a Event object based off the
        event ID prefix.
        """
        self.emap_index, gid = self._find_next_gramps_id(
            self.event_prefix, self.emap_index, EVENT_KEY
        )
        return cast(EventGrampsID, gid)

    def find_next_media_gramps_id(self) -> MediaGrampsID:
        """
        Return the next available GRAMPS' ID for a Media object based
        off the media object ID prefix.
        """
        self.omap_index, gid = self._find_next_gramps_id(
            self.media_prefix, self.omap_index, MEDIA_KEY
        )
        return cast(MediaGrampsID, gid)

    def find_next_citation_gramps_id(self) -> CitationGrampsID:
        """
        Return the next available GRAMPS' ID for a Citation object based off the
        citation ID prefix.
        """
        self.cmap_index, gid = self._find_next_gramps_id(
            self.citation_prefix, self.cmap_index, CITATION_KEY
        )
        return cast(CitationGrampsID, gid)

    def find_next_source_gramps_id(self) -> SourceGrampsID:
        """
        Return the next available GRAMPS' ID for a Source object based off the
        source ID prefix.
        """
        self.smap_index, gid = self._find_next_gramps_id(
            self.source_prefix, self.smap_index, SOURCE_KEY
        )
        return cast(SourceGrampsID, gid)

    def find_next_family_gramps_id(self) -> FamilyGrampsID:
        """
        Return the next available GRAMPS' ID for a Family object based off the
        family ID prefix.
        """
        self.fmap_index, gid = self._find_next_gramps_id(
            self.family_prefix, self.fmap_index, FAMILY_KEY
        )
        return cast(FamilyGrampsID, gid)

    def find_next_repository_gramps_id(self) -> RepositoryGrampsID:
        """
        Return the next available GRAMPS' ID for a Respository object based
        off the repository ID prefix.
        """
        self.rmap_index, gid = self._find_next_gramps_id(
            self.repository_prefix, self.rmap_index, REPOSITORY_KEY
        )
        return cast(RepositoryGrampsID, gid)

    def find_next_note_gramps_id(self) -> NoteGrampsID:
        """
        Return the next available GRAMPS' ID for a Note object based off the
        note ID prefix.
        """
        self.nmap_index, gid = self._find_next_gramps_id(
            self.note_prefix, self.nmap_index, NOTE_KEY
        )
        return cast(NoteGrampsID, gid)

    ################################################################
    #
    # get_number_of_* methods
    #
    ################################################################

    def _get_number_of(self, obj_key: int) -> int:
        """
        Return the number of objects currently in the database.
        """
        raise NotImplementedError

    def get_number_of_people(self) -> int:
        """
        Return the number of people currently in the database.
        """
        return self._get_number_of(PERSON_KEY)

    def get_number_of_events(self) -> int:
        """
        Return the number of events currently in the database.
        """
        return self._get_number_of(EVENT_KEY)

    def get_number_of_places(self) -> int:
        """
        Return the number of places currently in the database.
        """
        return self._get_number_of(PLACE_KEY)

    def get_number_of_tags(self) -> int:
        """
        Return the number of tags currently in the database.
        """
        return self._get_number_of(TAG_KEY)

    def get_number_of_families(self) -> int:
        """
        Return the number of families currently in the database.
        """
        return self._get_number_of(FAMILY_KEY)

    def get_number_of_notes(self) -> int:
        """
        Return the number of notes currently in the database.
        """
        return self._get_number_of(NOTE_KEY)

    def get_number_of_citations(self) -> int:
        """
        Return the number of citations currently in the database.
        """
        return self._get_number_of(CITATION_KEY)

    def get_number_of_sources(self) -> int:
        """
        Return the number of sources currently in the database.
        """
        return self._get_number_of(SOURCE_KEY)

    def get_number_of_media(self) -> int:
        """
        Return the number of media objects currently in the database.
        """
        return self._get_number_of(MEDIA_KEY)

    def get_number_of_repositories(self) -> int:
        """
        Return the number of source repositories currently in the database.
        """
        return self._get_number_of(REPOSITORY_KEY)

    ################################################################
    #
    # get_*_gramps_ids methods
    #
    ################################################################

    def _get_gramps_ids(self, obj_key: int) -> list[PrimaryObjectGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each object in the
        database.
        """
        raise NotImplementedError

    def get_person_gramps_ids(self) -> list[PersonGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Person in the
        database.
        """
        return cast(list[PersonGrampsID], self._get_gramps_ids(PERSON_KEY))

    def get_family_gramps_ids(self) -> list[FamilyGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Family in the
        database.
        """
        return cast(list[FamilyGrampsID], self._get_gramps_ids(FAMILY_KEY))

    def get_source_gramps_ids(self) -> list[SourceGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Source in the
        database.
        """
        return cast(list[SourceGrampsID], self._get_gramps_ids(SOURCE_KEY))

    def get_citation_gramps_ids(self) -> list[CitationGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Citation in the
        database.
        """
        return cast(list[CitationGrampsID], self._get_gramps_ids(CITATION_KEY))

    def get_event_gramps_ids(self) -> list[EventGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Event in the
        database.
        """
        return cast(list[EventGrampsID], self._get_gramps_ids(EVENT_KEY))

    def get_media_gramps_ids(self) -> list[MediaGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Media in the
        database.
        """
        return cast(list[MediaGrampsID], self._get_gramps_ids(MEDIA_KEY))

    def get_place_gramps_ids(self) -> list[PlaceGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Place in the
        database.
        """
        return cast(list[PlaceGrampsID], self._get_gramps_ids(PLACE_KEY))

    def get_repository_gramps_ids(self) -> list[RepositoryGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Repository in the
        database.
        """
        return cast(list[RepositoryGrampsID], self._get_gramps_ids(REPOSITORY_KEY))

    def get_note_gramps_ids(self) -> list[NoteGrampsID]:
        """
        Return a list of Gramps IDs, one ID for each Note in the
        database.
        """
        return cast(list[NoteGrampsID], self._get_gramps_ids(NOTE_KEY))

    ################################################################
    #
    # get_*_from_handle methods
    #
    ################################################################

    def _get_from_handle(
        self, obj_key, obj_class: Type[TableObjectType], handle: AnyHandle
    ) -> TableObjectType:
        if handle is None:
            raise HandleError("Handle is None")
        if not handle:
            raise HandleError("Handle is empty")
        data = self._get_raw_data(obj_key, handle)
        if data:
            return self.serializer.data_to_object(data, obj_class)

        raise HandleError(f"Handle {handle} not found")

    def get_event_from_handle(self, handle: EventHandle) -> Event:
        return self._get_from_handle(EVENT_KEY, Event, handle)

    def get_family_from_handle(self, handle: FamilyHandle) -> Family:
        return self._get_from_handle(FAMILY_KEY, Family, handle)

    def get_repository_from_handle(self, handle: RepositoryHandle) -> Repository:
        return self._get_from_handle(REPOSITORY_KEY, Repository, handle)

    def get_person_from_handle(self, handle: PersonHandle) -> Person:
        return self._get_from_handle(PERSON_KEY, Person, handle)

    def get_place_from_handle(self, handle: PlaceHandle) -> Place:
        return self._get_from_handle(PLACE_KEY, Place, handle)

    def get_citation_from_handle(self, handle: CitationHandle) -> Citation:
        return self._get_from_handle(CITATION_KEY, Citation, handle)

    def get_source_from_handle(self, handle: SourceHandle) -> Source:
        return self._get_from_handle(SOURCE_KEY, Source, handle)

    def get_note_from_handle(self, handle: NoteHandle) -> Note:
        return self._get_from_handle(NOTE_KEY, Note, handle)

    def get_media_from_handle(self, handle: MediaHandle) -> Media:
        return self._get_from_handle(MEDIA_KEY, Media, handle)

    def get_tag_from_handle(self, handle: TagHandle) -> Tag:
        return self._get_from_handle(TAG_KEY, Tag, handle)

    ################################################################
    #
    # get_*_from_gramps_id methods
    #
    ################################################################

    def get_person_from_gramps_id(self, gramps_id: PersonGrampsID) -> Person | None:
        data = self._get_raw_person_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Person)

    def get_family_from_gramps_id(self, gramps_id: FamilyGrampsID) -> Family | None:
        data = self._get_raw_family_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Family)

    def get_citation_from_gramps_id(
        self, gramps_id: CitationGrampsID
    ) -> Citation | None:
        data = self._get_raw_citation_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Citation)

    def get_source_from_gramps_id(self, gramps_id: SourceGrampsID) -> Source | None:
        data = self._get_raw_source_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Source)

    def get_event_from_gramps_id(self, gramps_id: EventGrampsID) -> Event | None:
        data = self._get_raw_event_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Event)

    def get_media_from_gramps_id(self, gramps_id: MediaGrampsID) -> Media | None:
        data = self._get_raw_media_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Media)

    def get_place_from_gramps_id(self, gramps_id: PlaceGrampsID) -> Place | None:
        data = self._get_raw_place_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Place)

    def get_repository_from_gramps_id(
        self, gramps_id: RepositoryGrampsID
    ) -> Repository | None:
        data = self._get_raw_repository_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Repository)

    def get_note_from_gramps_id(self, gramps_id: NoteGrampsID) -> Note | None:
        data = self._get_raw_note_from_id_data(gramps_id)
        return self.serializer.data_to_object(data, Note)

    ################################################################
    #
    # has_*_handle methods
    #
    ################################################################

    def _has_handle(self, obj_key, handle: AnyHandle) -> bool:
        """
        Return True if the handle exists in the database.
        """
        raise NotImplementedError

    def has_person_handle(self, handle: PersonHandle) -> bool:
        return self._has_handle(PERSON_KEY, handle)

    def has_family_handle(self, handle: FamilyHandle) -> bool:
        return self._has_handle(FAMILY_KEY, handle)

    def has_source_handle(self, handle: SourceHandle) -> bool:
        return self._has_handle(SOURCE_KEY, handle)

    def has_citation_handle(self, handle: CitationHandle) -> bool:
        return self._has_handle(CITATION_KEY, handle)

    def has_event_handle(self, handle: EventHandle) -> bool:
        return self._has_handle(EVENT_KEY, handle)

    def has_media_handle(self, handle: MediaHandle) -> bool:
        return self._has_handle(MEDIA_KEY, handle)

    def has_place_handle(self, handle: PlaceHandle) -> bool:
        return self._has_handle(PLACE_KEY, handle)

    def has_repository_handle(self, handle: RepositoryHandle) -> bool:
        return self._has_handle(REPOSITORY_KEY, handle)

    def has_note_handle(self, handle: NoteHandle) -> bool:
        return self._has_handle(NOTE_KEY, handle)

    def has_tag_handle(self, handle: TagHandle) -> bool:
        return self._has_handle(TAG_KEY, handle)

    ################################################################
    #
    # has_*_gramps_id methods
    #
    ################################################################

    def _has_gramps_id(self, obj_key, gramps_id: PrimaryObjectGrampsID) -> bool:
        raise NotImplementedError

    def has_person_gramps_id(self, gramps_id: PersonGrampsID) -> bool:
        return self._has_gramps_id(PERSON_KEY, gramps_id)

    def has_family_gramps_id(self, gramps_id: FamilyGrampsID) -> bool:
        return self._has_gramps_id(FAMILY_KEY, gramps_id)

    def has_source_gramps_id(self, gramps_id: SourceGrampsID) -> bool:
        return self._has_gramps_id(SOURCE_KEY, gramps_id)

    def has_citation_gramps_id(self, gramps_id: CitationGrampsID) -> bool:
        return self._has_gramps_id(CITATION_KEY, gramps_id)

    def has_event_gramps_id(self, gramps_id: EventGrampsID) -> bool:
        return self._has_gramps_id(EVENT_KEY, gramps_id)

    def has_media_gramps_id(self, gramps_id: MediaGrampsID) -> bool:
        return self._has_gramps_id(MEDIA_KEY, gramps_id)

    def has_place_gramps_id(self, gramps_id: PlaceGrampsID) -> bool:
        return self._has_gramps_id(PLACE_KEY, gramps_id)

    def has_repository_gramps_id(self, gramps_id: RepositoryGrampsID) -> bool:
        return self._has_gramps_id(REPOSITORY_KEY, gramps_id)

    def has_note_gramps_id(self, gramps_id: NoteGrampsID) -> bool:
        return self._has_gramps_id(NOTE_KEY, gramps_id)

    ################################################################
    #
    # get_*_cursor methods
    #
    ################################################################

    def get_place_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_place_data)

    def get_place_tree_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_place_tree_data)

    def get_person_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_person_data)

    def get_family_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_family_data)

    def get_event_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_event_data)

    def get_note_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_note_data)

    def get_tag_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_tag_data)

    def get_repository_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_repository_data)

    def get_media_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_media_data)

    def get_citation_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_citation_data)

    def get_source_cursor(self) -> Cursor:
        return Cursor(self._iter_raw_source_data)

    ################################################################
    #
    # iter_*_handles methods
    #
    ################################################################

    def _iter_handles(self, obj_key: int) -> Iterator[AnyHandle]:
        raise NotImplementedError

    def iter_person_handles(self) -> Iterator[PersonHandle]:
        """
        Return an iterator over handles for Persons in the database
        """
        return cast(Iterator[PersonHandle], self._iter_handles(PERSON_KEY))

    def iter_family_handles(self) -> Iterator[FamilyHandle]:
        """
        Return an iterator over handles for Families in the database
        """
        return cast(Iterator[FamilyHandle], self._iter_handles(FAMILY_KEY))

    def iter_citation_handles(self) -> Iterator[CitationHandle]:
        """
        Return an iterator over database handles, one handle for each Citation
        in the database.
        """
        return cast(Iterator[CitationHandle], self._iter_handles(CITATION_KEY))

    def iter_event_handles(self) -> Iterator[EventHandle]:
        """
        Return an iterator over handles for Events in the database
        """
        return cast(Iterator[EventHandle], self._iter_handles(EVENT_KEY))

    def iter_media_handles(self) -> Iterator[MediaHandle]:
        """
        Return an iterator over handles for Media in the database
        """
        return cast(Iterator[MediaHandle], self._iter_handles(MEDIA_KEY))

    def iter_note_handles(self) -> Iterator[NoteHandle]:
        """
        Return an iterator over handles for Notes in the database
        """
        return cast(Iterator[NoteHandle], self._iter_handles(NOTE_KEY))

    def iter_place_handles(self) -> Iterator[PlaceHandle]:
        """
        Return an iterator over handles for Places in the database
        """
        return cast(Iterator[PlaceHandle], self._iter_handles(PLACE_KEY))

    def iter_repository_handles(self) -> Iterator[RepositoryHandle]:
        """
        Return an iterator over handles for Repositories in the database
        """
        return cast(Iterator[RepositoryHandle], self._iter_handles(REPOSITORY_KEY))

    def iter_source_handles(self) -> Iterator[SourceHandle]:
        """
        Return an iterator over handles for Sources in the database
        """
        return cast(Iterator[SourceHandle], self._iter_handles(SOURCE_KEY))

    def iter_tag_handles(self) -> Iterator[TagHandle]:
        """
        Return an iterator over handles for Tags in the database
        """
        return cast(Iterator[TagHandle], self._iter_handles(TAG_KEY))

    ################################################################
    #
    # iter_* methods
    #
    ################################################################

    def _iter_objects(self, class_: type[TableObjectType]) -> Iterator[TableObjectType]:
        """
        Iterate over items in a class.
        """
        cursor = self._get_table_func(class_.__name__, "cursor_func")
        for handle, data in cursor():
            yield self.serializer.data_to_object(data, class_)

    def iter_people(self) -> Iterator[Person]:
        """Iterate over Person objects."""
        return self._iter_objects(Person)

    def iter_families(self) -> Iterator[Family]:
        """Iterate over Family objects."""
        return self._iter_objects(Family)

    def iter_citations(self) -> Iterator[Citation]:
        """Iterate over Citation objects."""
        return self._iter_objects(Citation)

    def iter_events(self) -> Iterator[Event]:
        """Iterate over Event objects."""
        return self._iter_objects(Event)

    def iter_media(self) -> Iterator[Media]:
        """Iterate over Media objects."""
        return self._iter_objects(Media)

    def iter_notes(self) -> Iterator[Note]:
        """Iterate over Note objects."""
        return self._iter_objects(Note)

    def iter_places(self) -> Iterator[Place]:
        """Iterate over Place objects."""
        return self._iter_objects(Place)

    def iter_repositories(self) -> Iterator[Repository]:
        """Iterate over Repository objects."""
        return self._iter_objects(Repository)

    def iter_sources(self) -> Iterator[Source]:
        """Iterate over Source objects."""
        return self._iter_objects(Source)

    def iter_tags(self) -> Iterator[Tag]:
        """Iterate over Tag objects."""
        return self._iter_objects(Tag)

    ################################################################
    #
    # _iter_raw_*_data methods
    #
    ################################################################

    def _iter_raw_data(self, obj_key: int) -> Iterator[tuple[AnyHandle, AnyDataDict]]:
        raise NotImplementedError

    def _iter_raw_person_data(self) -> Iterator[tuple[PersonHandle, PersonDataDict]]:
        """
        Return an iterator over raw Person data.
        """
        return cast(
            Iterator[tuple[PersonHandle, PersonDataDict]],
            self._iter_raw_data(PERSON_KEY),
        )

    def _iter_raw_family_data(self) -> Iterator[tuple[FamilyHandle, FamilyDataDict]]:
        """
        Return an iterator over raw Family data.
        """
        return cast(
            Iterator[tuple[FamilyHandle, FamilyDataDict]],
            self._iter_raw_data(FAMILY_KEY),
        )

    def _iter_raw_event_data(self) -> Iterator[tuple[EventHandle, EventDataDict]]:
        """
        Return an iterator over raw Event data.
        """
        return cast(
            Iterator[tuple[EventHandle, EventDataDict]], self._iter_raw_data(EVENT_KEY)
        )

    def _iter_raw_place_data(self) -> Iterator[tuple[PlaceHandle, PlaceDataDict]]:
        """
        Return an iterator over raw Place data.
        """
        return cast(
            Iterator[tuple[PlaceHandle, PlaceDataDict]], self._iter_raw_data(PLACE_KEY)
        )

    def _iter_raw_repository_data(
        self,
    ) -> Iterator[tuple[RepositoryHandle, RepositoryDataDict]]:
        """
        Return an iterator over raw Repository data.
        """
        return cast(
            Iterator[tuple[RepositoryHandle, RepositoryDataDict]],
            self._iter_raw_data(REPOSITORY_KEY),
        )

    def _iter_raw_source_data(self) -> Iterator[tuple[SourceHandle, SourceDataDict]]:
        """
        Return an iterator over raw Source data.
        """
        return cast(
            Iterator[tuple[SourceHandle, SourceDataDict]],
            self._iter_raw_data(SOURCE_KEY),
        )

    def _iter_raw_citation_data(
        self,
    ) -> Iterator[tuple[CitationHandle, CitationDataDict]]:
        """
        Return an iterator over raw Citation data.
        """
        return cast(
            Iterator[tuple[CitationHandle, CitationDataDict]],
            self._iter_raw_data(CITATION_KEY),
        )

    def _iter_raw_media_data(self) -> Iterator[tuple[MediaHandle, MediaDataDict]]:
        """
        Return an iterator over raw Media data.
        """
        return cast(
            Iterator[tuple[MediaHandle, MediaDataDict]], self._iter_raw_data(MEDIA_KEY)
        )

    def _iter_raw_note_data(self) -> Iterator[tuple[NoteHandle, NoteDataDict]]:
        """
        Return an iterator over raw Note data.
        """
        return cast(
            Iterator[tuple[NoteHandle, NoteDataDict]], self._iter_raw_data(NOTE_KEY)
        )

    def _iter_raw_tag_data(self) -> Iterator[tuple[TagHandle, TagDataDict]]:
        """
        Return an iterator over raw Tag data.
        """
        return cast(
            Iterator[tuple[TagHandle, TagDataDict]], self._iter_raw_data(TAG_KEY)
        )

    def _iter_raw_place_tree_data(self):
        """
        Return an iterator over raw data in the place hierarchy.
        """
        raise NotImplementedError

    ################################################################
    #
    # get_raw_*_data methods
    #
    ################################################################

    def _get_raw_data(self, obj_key: int, handle: AnyHandle) -> AnyDataDict:
        """
        Return raw (serialized) object from handle.
        """
        raise NotImplementedError

    def get_raw_person_data(self, handle: PersonHandle) -> PersonDataDict:
        return cast(PersonDataDict, self._get_raw_data(PERSON_KEY, handle))

    def get_raw_family_data(self, handle: FamilyHandle) -> FamilyDataDict:
        return cast(FamilyDataDict, self._get_raw_data(FAMILY_KEY, handle))

    def get_raw_source_data(self, handle: SourceHandle) -> SourceDataDict:
        return cast(SourceDataDict, self._get_raw_data(SOURCE_KEY, handle))

    def get_raw_citation_data(self, handle: CitationHandle) -> CitationDataDict:
        return cast(CitationDataDict, self._get_raw_data(CITATION_KEY, handle))

    def get_raw_event_data(self, handle: EventHandle) -> EventDataDict:
        return cast(EventDataDict, self._get_raw_data(EVENT_KEY, handle))

    def get_raw_media_data(self, handle: MediaHandle) -> MediaDataDict:
        return cast(MediaDataDict, self._get_raw_data(MEDIA_KEY, handle))

    def get_raw_place_data(self, handle: PlaceHandle) -> PlaceDataDict:
        return cast(PlaceDataDict, self._get_raw_data(PLACE_KEY, handle))

    def get_raw_repository_data(self, handle: RepositoryHandle) -> RepositoryDataDict:
        return cast(RepositoryDataDict, self._get_raw_data(REPOSITORY_KEY, handle))

    def get_raw_note_data(self, handle: NoteHandle) -> NoteDataDict:
        return cast(NoteDataDict, self._get_raw_data(NOTE_KEY, handle))

    def get_raw_tag_data(self, handle: TagHandle) -> TagDataDict:
        return cast(TagDataDict, self._get_raw_data(TAG_KEY, handle))

    ################################################################
    #
    # get_raw_*_from_id_data methods
    #
    ################################################################

    def _get_raw_from_id_data(
        self, obj_key: int, gramps_id: PrimaryObjectGrampsID
    ) -> AnyDataDict | None:
        raise NotImplementedError

    def _get_raw_person_from_id_data(
        self, gramps_id: PersonGrampsID
    ) -> PersonDataDict | None:
        return cast(PersonDataDict, self._get_raw_from_id_data(PERSON_KEY, gramps_id))

    def _get_raw_family_from_id_data(
        self, gramps_id: FamilyGrampsID
    ) -> FamilyDataDict | None:
        return cast(FamilyDataDict, self._get_raw_from_id_data(FAMILY_KEY, gramps_id))

    def _get_raw_source_from_id_data(
        self, gramps_id: SourceGrampsID
    ) -> SourceDataDict | None:
        return cast(SourceDataDict, self._get_raw_from_id_data(SOURCE_KEY, gramps_id))

    def _get_raw_citation_from_id_data(
        self, gramps_id: CitationGrampsID
    ) -> CitationDataDict | None:
        return cast(
            CitationDataDict, self._get_raw_from_id_data(CITATION_KEY, gramps_id)
        )

    def _get_raw_event_from_id_data(
        self, gramps_id: EventGrampsID
    ) -> EventDataDict | None:
        return cast(EventDataDict, self._get_raw_from_id_data(EVENT_KEY, gramps_id))

    def _get_raw_media_from_id_data(
        self, gramps_id: MediaGrampsID
    ) -> MediaDataDict | None:
        return cast(MediaDataDict, self._get_raw_from_id_data(MEDIA_KEY, gramps_id))

    def _get_raw_place_from_id_data(
        self, gramps_id: PlaceGrampsID
    ) -> PlaceDataDict | None:
        return cast(PlaceDataDict, self._get_raw_from_id_data(PLACE_KEY, gramps_id))

    def _get_raw_repository_from_id_data(
        self, gramps_id: RepositoryGrampsID
    ) -> RepositoryDataDict | None:
        return cast(
            RepositoryDataDict, self._get_raw_from_id_data(REPOSITORY_KEY, gramps_id)
        )

    def _get_raw_note_from_id_data(
        self, gramps_id: NoteGrampsID
    ) -> NoteDataDict | None:
        return cast(NoteDataDict, self._get_raw_from_id_data(NOTE_KEY, gramps_id))

    ################################################################
    #
    # add_* methods
    #
    ################################################################

    def _add_base(
        self, obj, trans: DbTxn, set_gid: bool, find_func, commit_func
    ) -> AnyHandle:
        if not obj.handle:
            obj.handle = create_id()
        if (not obj.gramps_id) and set_gid:
            obj.gramps_id = find_func()
        if not obj.gramps_id:
            # give it a random value for the moment:
            obj.gramps_id = str(random.random())
        commit_func(obj, trans)
        return obj.handle

    def add_person(
        self, person: Person, transaction: DbTxn, set_gid: bool = True
    ) -> PersonHandle:
        return cast(
            PersonHandle,
            self._add_base(
                person,
                transaction,
                set_gid,
                self.find_next_person_gramps_id,
                self.commit_person,
            ),
        )

    def add_family(
        self, family: Family, transaction: DbTxn, set_gid: bool = True
    ) -> FamilyHandle:
        return cast(
            FamilyHandle,
            self._add_base(
                family,
                transaction,
                set_gid,
                self.find_next_family_gramps_id,
                self.commit_family,
            ),
        )

    def add_event(
        self, event: Event, transaction: DbTxn, set_gid: bool = True
    ) -> EventHandle:
        return cast(
            EventHandle,
            self._add_base(
                event,
                transaction,
                set_gid,
                self.find_next_event_gramps_id,
                self.commit_event,
            ),
        )

    def add_place(
        self, place: Place, transaction: DbTxn, set_gid: bool = True
    ) -> PlaceHandle:
        return cast(
            PlaceHandle,
            self._add_base(
                place,
                transaction,
                set_gid,
                self.find_next_place_gramps_id,
                self.commit_place,
            ),
        )

    def add_repository(
        self, repository: Repository, transaction: DbTxn, set_gid: bool = True
    ) -> RepositoryHandle:
        return cast(
            RepositoryHandle,
            self._add_base(
                repository,
                transaction,
                set_gid,
                self.find_next_repository_gramps_id,
                self.commit_repository,
            ),
        )

    def add_source(
        self, source: Source, transaction: DbTxn, set_gid: bool = True
    ) -> SourceHandle:
        return cast(
            SourceHandle,
            self._add_base(
                source,
                transaction,
                set_gid,
                self.find_next_source_gramps_id,
                self.commit_source,
            ),
        )

    def add_citation(
        self, citation: Citation, transaction: DbTxn, set_gid: bool = True
    ) -> CitationHandle:
        return cast(
            CitationHandle,
            self._add_base(
                citation,
                transaction,
                set_gid,
                self.find_next_citation_gramps_id,
                self.commit_citation,
            ),
        )

    def add_media(
        self, media: Media, transaction: DbTxn, set_gid: bool = True
    ) -> MediaHandle:
        return cast(
            MediaHandle,
            self._add_base(
                media,
                transaction,
                set_gid,
                self.find_next_media_gramps_id,
                self.commit_media,
            ),
        )

    def add_note(
        self, note: Note, transaction: DbTxn, set_gid: bool = True
    ) -> NoteHandle:
        return cast(
            NoteHandle,
            self._add_base(
                note,
                transaction,
                set_gid,
                self.find_next_note_gramps_id,
                self.commit_note,
            ),
        )

    def add_tag(self, tag: Tag, transaction: DbTxn) -> TagHandle:
        if not tag.handle:
            tag.handle = create_id()
        self.commit_tag(tag, transaction)
        return tag.handle

    ################################################################
    #
    # commit_* methods
    #
    ################################################################

    def _commit_base(
        self, obj: AnyObject, obj_key: int, trans: DbTxn, change_time: int | None
    ) -> AnyDataDict | None:
        """
        Commit the specified object to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_person(
        self, person: Person, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Person to the database, storing the changes as
        part of the transaction.
        """
        old_data = self._commit_base(person, PERSON_KEY, transaction, change_time)

        if old_data:
            old_person = self.serializer.data_to_object(old_data, Person)
            # Update gender statistics if necessary
            if old_person.gender != person.gender or (
                old_person.primary_name.first_name != person.primary_name.first_name
            ):
                self.genderStats.uncount_person(old_person)
                self.genderStats.count_person(person)
            # Update surname list if necessary
            if self._order_by_person_key(person) != self._order_by_person_key(
                old_person
            ):
                self.remove_from_surname_list(old_person)
                self.add_to_surname_list(person, transaction.batch)
        else:
            self.genderStats.count_person(person)
            self.add_to_surname_list(person, transaction.batch)

        # Other misc update tasks:
        self.individual_attributes.update(
            [
                str(attr.type)
                for attr in person.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )

        self.event_role_names.update(
            [str(eref.role) for eref in person.event_ref_list if eref.role.is_custom()]
        )

        self.name_types.update(
            [
                str(name.type)
                for name in ([person.primary_name] + person.alternate_names)
                if name.type.is_custom()
            ]
        )
        all_surn = []  # new list we will use for storage
        all_surn += person.primary_name.get_surname_list()
        for asurname in person.alternate_names:
            all_surn += asurname.get_surname_list()
        self.origin_types.update(
            [str(surn.origintype) for surn in all_surn if surn.origintype.is_custom()]
        )

        self.url_types.update(
            [str(url.type) for url in person.urls if url.type.is_custom()]
        )
        attr_list = []
        for mref in person.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)

    def commit_family(
        self, family: Family, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Family to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(family, FAMILY_KEY, transaction, change_time)

        # Misc updates:
        self.family_attributes.update(
            [
                str(attr.type)
                for attr in family.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )

        rel_list = []
        for ref in family.child_ref_list:
            if ref.frel.is_custom():
                rel_list.append(str(ref.frel))
            if ref.mrel.is_custom():
                rel_list.append(str(ref.mrel))
        self.child_ref_types.update(rel_list)

        self.event_role_names.update(
            [str(eref.role) for eref in family.event_ref_list if eref.role.is_custom()]
        )

        if family.type.is_custom():
            self.family_rel_types.add(str(family.type))

        attr_list = []
        for mref in family.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)

    def commit_citation(
        self, citation: Citation, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Citation to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(citation, CITATION_KEY, transaction, change_time)

        # Misc updates:
        attr_list = []
        for mref in citation.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)

        self.source_attributes.update(
            [
                str(attr.type)
                for attr in citation.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )

    def commit_source(
        self, source: Source, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Source to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(source, SOURCE_KEY, transaction, change_time)

        # Misc updates:
        self.source_media_types.update(
            [
                str(ref.media_type)
                for ref in source.reporef_list
                if ref.media_type.is_custom()
            ]
        )

        attr_list = []
        for mref in source.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)
        self.source_attributes.update(
            [
                str(attr.type)
                for attr in source.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )

    def commit_repository(
        self,
        repository: Repository,
        transaction: DbTxn,
        change_time: int | None = None,
    ):
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(repository, REPOSITORY_KEY, transaction, change_time)

        # Misc updates:
        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update(
            [str(url.type) for url in repository.urls if url.type.is_custom()]
        )

    def commit_note(
        self, note: Note, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Note to the database, storing the changes as part
        of the transaction.
        """
        self._commit_base(note, NOTE_KEY, transaction, change_time)

        # Misc updates:
        if note.type.is_custom():
            self.note_types.add(str(note.type))

    def commit_place(
        self, place: Place, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Place to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(place, PLACE_KEY, transaction, change_time)

        # Misc updates:
        if place.get_type().is_custom():
            self.place_types.add(str(place.get_type()))

        self.url_types.update(
            [str(url.type) for url in place.urls if url.type.is_custom()]
        )

        attr_list = []
        for mref in place.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)

    def commit_event(
        self, event: Event, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Event to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(event, EVENT_KEY, transaction, change_time)

        # Misc updates:
        self.event_attributes.update(
            [
                str(attr.type)
                for attr in event.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )
        if event.type.is_custom():
            self.event_names.add(str(event.type))
        attr_list = []
        for mref in event.media_list:
            attr_list += [
                str(attr.type)
                for attr in mref.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        self.media_attributes.update(attr_list)

    def commit_tag(self, tag: Tag, transaction: DbTxn, change_time: int | None = None):
        """
        Commit the specified Tag to the database, storing the changes as
        part of the transaction.
        """
        self._commit_base(tag, TAG_KEY, transaction, change_time)

    def commit_media(
        self, media: Media, transaction: DbTxn, change_time: int | None = None
    ):
        """
        Commit the specified Media to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(media, MEDIA_KEY, transaction, change_time)

        # Misc updates:
        self.media_attributes.update(
            [
                str(attr.type)
                for attr in media.attribute_list
                if attr.type.is_custom() and str(attr.type)
            ]
        )

    def _after_commit(self, transaction: DbTxn) -> None:
        """
        Post-transaction commit processing
        """
        # Reset callbacks if necessary
        if transaction.batch or not len(transaction):
            return
        if self.undo_callback:
            self.undo_callback(_("_Undo %s") % transaction.get_description())
        if self.redo_callback:
            self.redo_callback(None)
        if self.undo_history_callback:
            self.undo_history_callback()

    ################################################################
    #
    # remove_* methods
    #
    ################################################################

    def _do_remove(self, handle: AnyHandle, transaction: DbTxn, obj_key: int) -> None:
        raise NotImplementedError

    def remove_person(self, handle: PersonHandle, transaction: DbTxn) -> None:
        """
        Remove the Person specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, PERSON_KEY)

    def remove_source(self, handle: SourceHandle, transaction: DbTxn) -> None:
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, SOURCE_KEY)

    def remove_citation(self, handle: CitationHandle, transaction: DbTxn) -> None:
        """
        Remove the Citation specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, CITATION_KEY)

    def remove_event(self, handle: EventHandle, transaction: DbTxn) -> None:
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, EVENT_KEY)

    def remove_media(self, handle: MediaHandle, transaction: DbTxn) -> None:
        """
        Remove the MediaPerson specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, MEDIA_KEY)

    def remove_place(self, handle: PlaceHandle, transaction: DbTxn) -> None:
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, PLACE_KEY)

    def remove_family(self, handle: FamilyHandle, transaction: DbTxn) -> None:
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, FAMILY_KEY)

    def remove_repository(self, handle: RepositoryHandle, transaction: DbTxn) -> None:
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, REPOSITORY_KEY)

    def remove_note(self, handle: NoteHandle, transaction: DbTxn) -> None:
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, NOTE_KEY)

    def remove_tag(self, handle: TagHandle, transaction: DbTxn) -> None:
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, TAG_KEY)

    ################################################################
    #
    # get_*_types methods
    #
    ################################################################

    def get_event_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Event instances
        in the database.
        """
        return list(self.event_attributes)

    def get_event_types(self) -> list[str]:
        """
        Return a list of all event types in the database.
        """
        return list(self.event_names)

    def get_person_event_types(self) -> list[str]:
        """
        Deprecated:  Use get_event_types
        """
        return list(self.event_names)

    def get_person_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Person instances
        in the database.
        """
        return list(self.individual_attributes)

    def get_family_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Family instances
        in the database.
        """
        return list(self.family_attributes)

    def get_family_event_types(self) -> list[str]:
        """
        Deprecated:  Use get_event_types
        """
        return list(self.event_names)

    def get_media_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Media and MediaRef
        instances in the database.
        """
        return list(self.media_attributes)

    def get_family_relation_types(self) -> list[str]:
        """
        Return a list of all relationship types assocated with Family
        instances in the database.
        """
        return list(self.family_rel_types)

    def get_child_reference_types(self) -> list[str]:
        """
        Return a list of all child reference types assocated with Family
        instances in the database.
        """
        return list(self.child_ref_types)

    def get_event_roles(self) -> list[str]:
        """
        Return a list of all custom event role names assocated with Event
        instances in the database.
        """
        return list(self.event_role_names)

    def get_name_types(self) -> list[str]:
        """
        Return a list of all custom names types assocated with Person
        instances in the database.
        """
        return list(self.name_types)

    def get_origin_types(self) -> list[str]:
        """
        Return a list of all custom origin types assocated with Person/Surname
        instances in the database.
        """
        return list(self.origin_types)

    def get_repository_types(self) -> list[str]:
        """
        Return a list of all custom repository types assocated with Repository
        instances in the database.
        """
        return list(self.repository_types)

    def get_note_types(self) -> list[str]:
        """
        Return a list of all custom note types assocated with Note instances
        in the database.
        """
        return list(self.note_types)

    def get_source_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Source/Citation
        instances in the database.
        """
        return list(self.source_attributes)

    def get_source_media_types(self) -> list[str]:
        """
        Return a list of all custom source media types assocated with Source
        instances in the database.
        """
        return list(self.source_media_types)

    def get_url_types(self) -> list[str]:
        """
        Return a list of all custom url types assocated with Url instances
        in the database.
        """
        return list(self.url_types)

    def get_place_types(self) -> list[str]:
        """
        Return a list of all custom place types assocated with Place instances
        in the database.
        """
        return list(self.place_types)

    ################################################################
    #
    # get_*_bookmarks methods
    #
    ################################################################

    def get_bookmarks(self) -> DbBookmarks:
        return self.bookmarks

    def get_citation_bookmarks(self) -> DbBookmarks:
        return self.citation_bookmarks

    def get_event_bookmarks(self) -> DbBookmarks:
        return self.event_bookmarks

    def get_family_bookmarks(self) -> DbBookmarks:
        return self.family_bookmarks

    def get_media_bookmarks(self) -> DbBookmarks:
        return self.media_bookmarks

    def get_note_bookmarks(self) -> DbBookmarks:
        return self.note_bookmarks

    def get_place_bookmarks(self) -> DbBookmarks:
        return self.place_bookmarks

    def get_repo_bookmarks(self) -> DbBookmarks:
        return self.repo_bookmarks

    def get_source_bookmarks(self) -> DbBookmarks:
        return self.source_bookmarks

    ################################################################
    #
    # Other methods
    #
    ################################################################

    def get_default_handle(self) -> PersonHandle | None:
        return self._get_metadata("default-person-handle", None)

    def get_default_person(self) -> Person | None:
        handle = self.get_default_handle()
        if handle:
            return self.get_person_from_handle(handle)
        return None

    def set_default_person_handle(self, handle: PersonHandle | None) -> None:
        self._set_metadata("default-person-handle", handle)
        self.emit("home-person-changed")

    def get_mediapath(self) -> str | None:
        return self._get_metadata("media-path", None)

    def set_mediapath(self, mediapath: str | None) -> None:
        return self._set_metadata("media-path", mediapath)

    def get_surname_list(self) -> list[str]:
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        return self.surname_list

    def add_to_surname_list(self, person: Person, batch_transaction: bool) -> None:
        """
        Add surname to surname list
        """
        if batch_transaction:
            return
        name = None
        primary_name = person.get_primary_name()
        if primary_name:
            surname_list = primary_name.get_surname_list()
            if len(surname_list) > 0:
                name = surname_list[0].surname
        if name is None:
            return
        i = bisect.bisect(self.surname_list, name)
        if 0 < i <= len(self.surname_list):
            if self.surname_list[i - 1] != name:
                self.surname_list.insert(i, name)
        else:
            self.surname_list.insert(i, name)

    def remove_from_surname_list(self, person: Person):
        """
        Check whether there are persons with the same surname left in
        the database.

        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = None
        primary_name = person.get_primary_name()
        if primary_name:
            surname_list = primary_name.get_surname_list()
            if len(surname_list) > 0:
                name = surname_list[0].surname
        if name is None:
            return
        if name in self.surname_list:
            self.surname_list.remove(name)

    def get_gender_stats(self) -> dict[str, tuple[int, int, int]]:
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        """
        raise NotImplementedError

    def save_gender_stats(self, gstats: GenderStats):
        raise NotImplementedError

    def get_researcher(self) -> Researcher:
        return self.owner

    def set_researcher(self, owner: Researcher):
        self.owner.set_from(owner)

    def request_rebuild(self):
        self.emit("person-rebuild")
        self.emit("family-rebuild")
        self.emit("place-rebuild")
        self.emit("source-rebuild")
        self.emit("citation-rebuild")
        self.emit("media-rebuild")
        self.emit("event-rebuild")
        self.emit("repository-rebuild")
        self.emit("note-rebuild")
        self.emit("tag-rebuild")

    def get_save_path(self):
        return self._directory

    def _set_save_path(self, directory) -> None:
        self._directory = directory
        if self._directory:
            self.full_name = os.path.abspath(self._directory)
            self.path = self.full_name
            self.brief_name = os.path.basename(self._directory)
        else:
            self.full_name = None
            self.path = None
            self.brief_name = None

    def report_bm_change(self) -> None:
        """
        Add 1 to the number of bookmark changes during this session.
        """
        self._bm_changes += 1

    def db_has_bm_changes(self) -> bool:
        """
        Return whether there were bookmark changes during the session.
        """
        return self._bm_changes > 0

    def get_undodb(self):
        return self.undodb

    def undo(self, update_history: bool = True) -> bool:
        return self.undodb.undo(update_history) if self.undodb is not None else False

    def undo_reference(self, data, handle: AnyHandle) -> None:
        """
        Helper method to undo a reference map entry
        """
        raise NotImplementedError

    def undo_data(self, data, handle: AnyHandle, obj_key: int) -> None:
        """
        Helper method to undo/redo the changes made
        """
        raise NotImplementedError

    def redo(self, update_history: bool = True) -> bool:
        return self.undodb.redo(update_history) if self.undodb is not None else False

    def get_summary(self) -> dict[str, int | str]:
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Data version")
        """
        return {
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
            _("Schema version"): ".".join([str(v) for v in self.VERSION]),
        }

    def _order_by_person_key(self, person: Person):
        """
        All non pa/matronymic surnames are used in indexing.
        pa/matronymic not as they change for every generation!
        returns a byte string
        """
        order_by = ""
        if person.primary_name:
            order_by_list = [
                surname.surname + " " + person.primary_name.first_name
                for surname in person.primary_name.surname_list
                if (
                    int(surname.origintype)
                    not in [NameOriginType.PATRONYMIC, NameOriginType.MATRONYMIC]
                )
            ]
            order_by = " ".join(order_by_list)
        return glocale.sort_key(order_by)

    def _get_person_data(self, person: Person) -> tuple[str, str]:
        """
        Given a Person, return primary_name.first_name and surname.
        """
        given_name = ""
        surname = ""
        if person:
            primary_name = person.get_primary_name()
            if primary_name:
                given_name = primary_name.get_first_name()
                surname_list = primary_name.get_surname_list()
                if len(surname_list) > 0:
                    surname_obj = surname_list[0]
                    if surname_obj:
                        surname = surname_obj.surname
        return (given_name, surname)

    def _get_place_data(self, place: Place):
        """
        Given a Place, return the first PlaceRef handle.
        """
        enclosed_by = ""
        for placeref in place.get_placeref_list():
            enclosed_by = placeref.ref
            break
        return enclosed_by

    def _gramps_upgrade(self, version: int, directory, callback=None) -> None:
        """
        Here we do the calls for stepwise schema upgrades.
        We assume that we need to rebuild secondary and reference maps.
        """
        UpdateCallback.__init__(self, callback)

        start = time.time()

        from gramps.gen.db.upgrade import (
            gramps_upgrade_14,
            gramps_upgrade_15,
            gramps_upgrade_16,
            gramps_upgrade_17,
            gramps_upgrade_18,
            gramps_upgrade_19,
            gramps_upgrade_20,
            gramps_upgrade_21,
            gramps_upgrade_22,
        )

        if version < 14:
            gramps_upgrade_14(self)
        if version < 15:
            gramps_upgrade_15(self)
        if version < 16:
            gramps_upgrade_16(self)
        if version < 17:
            gramps_upgrade_17(self)
        if version < 18:
            gramps_upgrade_18(self)
        if version < 19:
            gramps_upgrade_19(self)
        if version < 20:
            gramps_upgrade_20(self)
        if version < 21:
            gramps_upgrade_21(self)
        if version < 22:
            gramps_upgrade_22(self)

        self.rebuild_secondary(callback)
        self.reindex_reference_map(callback)
        self.surname_list = self.get_surname_list()
        self.reset()

        self.set_schema_version(self.VERSION[0])
        LOG.debug("Upgrade time: %d seconds", int(time.time() - start))

    def get_schema_version(self) -> int:
        """Return current schema version as an int"""
        return int(self._get_metadata("version", default="0"))

    def set_schema_version(self, value: int) -> None:
        """set the current schema version"""
        self._set_metadata("version", str(value))

    def set_serializer(self, serializer_name: Literal["blob", "json"]) -> None:
        """
        Set the serializer to 'blob' or 'json'
        """
        if serializer_name == "blob":
            self.serializer = BlobSerializer
        elif serializer_name == "json":
            self.serializer = JSONSerializer


Database = DbGeneric
