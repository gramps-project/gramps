#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
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

from __future__ import annotations

import os
import logging
import email.utils
import time

from gramps.gen.config import config as _cfg
from gramps.gui.plug import PluginWindows
from gramps.gui.utils import ProgressMeter
from gramps.gui.dialog import WarningDialog

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn

from gramps.gen.fs import tree
import gramps.gui.fs.person.fsg_sync as FSG_Sync
from gramps.gen.fs import db_familysearch
from gramps.gen.fs.compare import compare_fs_to_gramps
from gramps.gen.fs import utils as fs_utilities
import gramps.gen.fs.person.mixins.cache as cache_mod
from gramps.gen.fs.person.mixins.cache import CacheMixin, _FsCache
from gramps.gen.fs.person.mixins.helpers import HelpersMixin
from gramps.gui.fs.manager import get_session
from gramps.gui.fs.person.mixins.compare_gtk import CompareGtkMixin
from gramps.gui.fs.person.mixins.source_import import SourceImportMixin
from gramps.gui.fs.person.mixins.sources_dialog import SourcesDialogMixin

logger = logging.getLogger(__name__)

_ = glocale.translation.gettext


# Person compare window used by actions.py


class CompareWindow:
    def __init__(
        self,
        dbstate,
        uistate,
        track,
        person,
        fsid=None,
        session=None,
        parent=None,
        editor=None,
    ):
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.person = person
        self.fsid = (fsid or "") if isinstance(fsid, str) else ""
        self.session = session
        self.parent = parent
        self.editor = editor

        self._open()

    def _open(self):
        # no schema/table  generated

        # ensure a session exists + wire it into tree._fs_session
        sess = self.session
        if not sess:
            try:
                sess = get_session(self.dbstate, self.uistate)
            except Exception:
                sess = None

        if not sess:
            WarningDialog(_("FamilySearch is not configured (no session)."))
            return

        try:
            tree._fs_session = sess
        except Exception:
            pass

        try:
            if self.fsid:
                try:
                    db = self.dbstate.db
                except Exception:
                    db = self.dbstate.get_database()
                fs_utilities.link_gramps_fs_id(db, self.person, self.fsid)
        except Exception:
            pass

        # parent window
        parent_win = self.parent or getattr(self.uistate, "window", None)

        # person handle
        person_handle = getattr(self.person, "handle", None) or self.person

        class _UistateProxy:
            """
            Proxy that forwards everything to the real uistate, but lets us override
            the transient parent window used for dialogs

            this must expose set_active/get_active so SourceImportMixin can
            re-pin the person after db.request_rebuild()
            """

            def __init__(self, real_uistate, window_override=None):
                self._real = real_uistate
                self.window = window_override or getattr(real_uistate, "window", None)

            def __getattr__(self, name):
                return getattr(self._real, name)

        class _Shim(
            CompareGtkMixin,
            SourcesDialogMixin,
            SourceImportMixin,
            CacheMixin,
            HelpersMixin,
        ):
            # CompareGtkMixin expects class vars like the Gramplet did back when this was a gramplet
            fs_Tree = None
            FSID = None
            _cache = None
            CONFIG = None

            def __init__(self, dbstate, real_uistate, person_handle, parent_win):
                self.dbstate = dbstate
                self.window = parent_win
                self.uistate = _UistateProxy(real_uistate, window_override=parent_win)
                self._active_person_handle = person_handle

            def get_active(self, what):
                if what == "Person":
                    return self._active_person_handle
                try:
                    return self.uistate.get_active(what)
                except Exception:
                    return None

            def set_active(self, what, handle):
                try:
                    if what == "Person":
                        self.uistate.set_active(handle, "Person")
                    else:
                        self.uistate.set_active(handle, what)
                except Exception:
                    try:
                        if what == "Person":
                            self.uistate.set_active("Person", handle)
                        else:
                            self.uistate.set_active(what, handle)
                    except Exception:
                        pass

            def _toggle_noop(self, *args, **kwargs):
                return None

        try:
            _Shim.CONFIG = FSG_Sync.FSG_Sync.CONFIG
        except Exception:
            try:
                cm = _cfg.register_manager("FSG_Sync")
                # register keys we use in SourcesDialogMixin
                cm.register("preferences.fs_image_download_dir", "")
                cm.load()
                _Shim.CONFIG = cm
            except Exception:
                _Shim.CONFIG = None

        # Ensure fs_Tree exists and is shared with other compare modules
        if not FSG_Sync.FSG_Sync.fs_Tree:
            FSG_Sync.FSG_Sync.fs_Tree = tree.Tree()
            FSG_Sync.FSG_Sync.fs_Tree._getsources = False

        _Shim.fs_Tree = FSG_Sync.FSG_Sync.fs_Tree

        # Ensure cache exists (CacheMixin uses self.__class__._cache)
        if not getattr(_Shim, "_cache", None):
            base_dir = os.path.dirname(cache_mod.__file__)
            _Shim._cache = _FsCache(base_dir)

        shim = _Shim(self.dbstate, self.uistate, person_handle, parent_win)
        try:
            shim._on_compare(None)
        except Exception as e:
            WarningDialog(_("Could not open compare window:\n{e}").format(e=str(e)))


class FSCompareWindow(PluginWindows.ToolManagedWindowBatch):
    """
    The main batch window that iterates through filtered persons and compares
    them against FamilySearch.
    """

    def get_title(self):
        return _("FamilySearch Compare")

    def initial_frame(self):
        return _("Options")

    def run(self):
        logger.info("FSCompareWindow.run: starting")

        # Ensure FamilySearch session
        if not FSG_Sync.FSG_Sync.ensure_session(self):
            WarningDialog(_("Not connected to FamilySearch"))
            return

        progress = ProgressMeter(
            _("FamilySearch: Compare"),
            _("Starting"),
            can_cancel=True,
            parent=self.uistate.window,
        )

        self.uistate.set_busy_cursor(True)
        self.dbstate.db.disable_signals()

        # Ensure FS tree/cache exists
        if not FSG_Sync.FSG_Sync.fs_Tree:
            FSG_Sync.FSG_Sync.fs_Tree = tree.Tree()
            FSG_Sync.FSG_Sync.fs_Tree._getsources = False

        self.db = self.dbstate.get_database()

        # Build ordered list of persons to process
        filter_ = self.options.menu.get_option_by_name("Person").get_filter()
        days = self.options.menu.get_option_by_name("gui_days").get_value()
        force = self.options.menu.get_option_by_name("gui_needed").get_value()
        max_date = int(time.time()) - days * 24 * 3600

        person_handles = set(filter_.apply(self.db, self.db.iter_person_handles()))
        ordered = []

        progress.set_pass(_("Building ordered list (1/2)"), len(person_handles))
        logger.debug("Filtered list size: %d", len(person_handles))

        for handle in person_handles:
            if progress.get_cancelled():
                self._cleanup(progress)
                return
            progress.step()
            person = self.db.get_person_from_handle(handle)
            fsid = fs_utilities.get_fsftid(person)
            if fsid == "":
                continue

            status_ts = 0
            try:
                st = db_familysearch.FSStatusDB(self.db, handle)
                st.get()
                status_ts = int(st.status_ts or 0)
            except Exception:
                status_ts = 0

            if status_ts:
                if force or status_ts < max_date:
                    ordered.append([status_ts, handle, fsid])
            else:
                ordered.append([0, handle, fsid])

        ordered.sort(key=lambda item: item[0])

        # process
        progress.set_pass(_("Processing list (2/2)"), len(ordered))
        logger.debug("Sorted list size: %d", len(ordered))

        def _prime_fetch(pair):
            fsid_local = pair[2]
            fs_person = None
            date_mod = None
            etag = None

            if fsid_local in FSG_Sync.FSG_Sync.fs_Tree._persons:
                fs_person = FSG_Sync.FSG_Sync.fs_Tree._persons.get(fsid_local)

            if (
                not fs_person
                or not hasattr(fs_person, "_last_modified")
                or not getattr(fs_person, "_last_modified", None)
            ):
                path = "/platform/tree/persons/" + fsid_local
                r = tree._fs_session.head_url(path)
                while (
                    r and r.status_code == 301 and "X-Entity-Forwarded-Id" in r.headers
                ):
                    fsid_local = r.headers["X-Entity-Forwarded-Id"]
                    logger.info("Redirected FS ID %s -> %s", pair[2], fsid_local)
                    pair[2] = fsid_local
                    path = "/platform/tree/persons/" + fsid_local
                    r = tree._fs_session.head_url(path)
                if r and "Last-Modified" in r.headers:
                    date_mod = int(
                        time.mktime(email.utils.parsedate(r.headers["Last-Modified"]))
                    )
                if r and "Etag" in r.headers:
                    etag = r.headers["Etag"]
                FSG_Sync.FSG_Sync.fs_Tree.add_person(fsid_local)
                fs_person = FSG_Sync.FSG_Sync.fs_Tree._persons.get(fsid_local)

            if not fs_person:
                logger.warning(_("FS ID %s not found"), fsid_local)
                return
            fs_person._datemod = date_mod
            fs_person._etag = etag

        def _compare_pair(pair):
            person = self.db.get_person_from_handle(pair[1])
            fsid_local = pair[2]
            fs_utilities.link_gramps_fs_id(self.dbstate.db, person, fsid_local)
            logger.info("Processing %s %s", person.gramps_id, fsid_local)
            if fsid_local in FSG_Sync.FSG_Sync.fs_Tree._persons:
                fs_person = FSG_Sync.FSG_Sync.fs_Tree._persons.get(fsid_local)
                compare_fs_to_gramps(fs_person, person, self.db, dupdoc=True)
            else:
                logger.warning("FS ID %s not found in cache", fsid_local)

        for pair in ordered:
            if progress.get_cancelled():
                self._cleanup(progress)
                return
            progress.step()
            _prime_fetch(pair)
            _compare_pair(pair)

        self._cleanup(progress)
        logger.info("FSCompareWindow.run: done")

    def _cleanup(self, progress):
        self.uistate.set_busy_cursor(False)
        progress.close()
        self.dbstate.db.enable_signals()
        self.dbstate.db.request_rebuild()
