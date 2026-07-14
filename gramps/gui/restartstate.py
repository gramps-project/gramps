#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       The Gramps Project
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
Capture and restore a Gramps session across a self-relaunch (``os.execv``).

Some preferences (UI language, date format, ...) only take effect on the
next process start. Rather than leave the user to close and reopen Gramps
manually and land on the welcome screen, these functions snapshot the
currently open tree, active view, selection and open editors to a small
JSON file, relaunch the process, and restore that state once the new
process has finished loading the tree.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

import json
import os
import sys
import tempfile
import logging
from typing import Any, TYPE_CHECKING

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.errors import HandleError

if TYPE_CHECKING:
    from gramps.gen.dbstate import DbState
    from .displaystate import DisplayState
    from .viewmanager import ViewManager

LOG = logging.getLogger(".gui.restartstate")

STATE_VERSION = 1


def capture_state(
    dbstate: "DbState", uistate: "DisplayState", viewmanager: "ViewManager"
) -> dict[str, Any]:
    """
    Snapshot the current session (open tree, active view, selection, and
    open primary-object editors) into a plain dict suitable for JSON export.
    """
    from .editors.editprimary import EditPrimary
    from gramps.gen.config import config

    state: dict[str, Any] = {
        "version": STATE_VERSION,
        "language": config.get("preferences.language"),
        "tree": None,
        "active_view": None,
        "selected": {},
        "open_editors": [],
    }

    if dbstate.is_open():
        state["tree"] = dbstate.db.get_save_path()

    state["active_view"] = viewmanager.get_active_view_id()

    for (nav_type, nav_group), history in uistate.history_lookup.items():
        if nav_group != 0:
            continue
        handle = history.present()
        if handle:
            state["selected"][nav_type] = handle

    for item in uistate.gwm.id2item.values():
        if not isinstance(item, EditPrimary):
            continue
        obj = item.obj
        handle = obj.get_handle() if obj else None
        if handle:
            state["open_editors"].append(
                {"object_type": obj.__class__.__name__, "handle": handle}
            )

    return state


def write_state_file(state: dict[str, Any]) -> str:
    """
    Write the given state dict to a temp JSON file and return its path.
    """
    handle, path = tempfile.mkstemp(prefix="gramps_restart_", suffix=".json")
    with os.fdopen(handle, "w", encoding="utf-8") as state_file:
        json.dump(state, state_file)
    return path


def restart_gramps(path: str, dbstate: "DbState | None" = None) -> None:
    """
    Relaunch the current Gramps process, passing it the restore-state file.

    Closes the open database first, if any, so its lock file is released
    and the relaunched process can reopen the same tree. Without this, the
    new process finds the tree locked by itself (``os.execv`` keeps the same
    pid but never runs the close/unlock code) and aborts while still inside
    GTK's application-activate callback.
    """
    if dbstate is not None and dbstate.is_open():
        dbstate.db.close()
    os.execv(sys.executable, [sys.executable] + sys.argv + ["--restore-state", path])


def apply_post_init_state(
    path: str, dbstate: "DbState", viewmanager: "ViewManager"
) -> None:
    """
    Restore active view, selection, and open editors from a restart-state
    file, once the tree named in that file has finished loading.

    Any handle that no longer resolves (the tree may have changed between
    the snapshot and this restart) is silently skipped rather than raised.
    """
    from .editors import EditObject

    try:
        with open(path, encoding="utf-8") as state_file:
            state = json.load(state_file)
    except (OSError, ValueError):
        return

    uistate = viewmanager.uistate

    active_view = state.get("active_view")
    if active_view:
        for cat_num, cat_views in enumerate(viewmanager.views):
            for view_num, (pdata, _page_def) in enumerate(cat_views):
                if pdata.id == active_view:
                    viewmanager.goto_page(cat_num, view_num)
                    break

    for nav_type, handle in state.get("selected", {}).items():
        has_handle = dbstate.db.method("has_%s_handle", nav_type)
        try:
            if has_handle and has_handle(handle):
                uistate.set_active(handle, nav_type)
        except HandleError:
            LOG.info("Skipping stale selection %s/%s on restart", nav_type, handle)

    for editor in state.get("open_editors", []):
        object_type = editor.get("object_type")
        handle = editor.get("handle")
        has_handle = dbstate.db.method("has_%s_handle", object_type)
        try:
            if has_handle and has_handle(handle):
                EditObject(
                    dbstate, uistate, [], object_type, prop="handle", value=handle
                )
        except HandleError:
            LOG.info("Skipping stale open editor %s/%s on restart", object_type, handle)
