# -*- coding: utf-8 -*-
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

import email.utils
import logging
import time
from typing import Any, Optional, Tuple

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType, Person

from gramps.gen.fs import db_familysearch
from gramps.gen.fs import tree
from gramps.gen.fs import utils as fs_utilities

from .comparators import (
    compare_fact,
    compare_gender,
    compare_names,
    compare_other_facts,
    compare_parents,
    compare_spouses,
)

logger = logging.getLogger(__name__)

_ = glocale.translation.gettext


_UI = {
    "green": "#D8F3DC",  # match
    "red": "#FFE3E3",  # critical mismatch
    "orange": "#FFE8CC",  # warning mismatch
    "yellow": "#FFF3BF",  # only in Gramps
    "yellow3": "#D0EBFF",  # only in FS
    "white": "#F8F9FA",  # neutral header
    "gray": "#E9ECEF",
}


def _ui_color(semantic: str) -> str:
    return _UI.get((semantic or "").strip(), semantic or "")


def _ui_row(row: Any) -> Any:
    # convert semantic color token in row[0] into a display tint (hex).
    if not row:
        return row
    r = list(row)
    r[0] = _ui_color(r[0])
    return r


def compare_fs_to_gramps(
    fs_person: Any, gr_person: Person, db: Any, model: Any = None, dupdoc: bool = False
):
    """
    stores comparison timestamps/flags on the Person
    via db_familysearch.FSStatusDB (JSON attribute blob).
    """
    db_state = db_familysearch.FSStatusDB(db, gr_person.handle)
    db_state.get()

    # if we already compared after both FS + Gramps changes, skip.
    if (
        model is None
        and hasattr(fs_person, "_datmod")
        and db_state.status_ts
        and db_state.status_ts > fs_person._datmod
        and db_state.status_ts > gr_person.change
    ):
        return

    if getattr(fs_person, "id", None):
        db_state.fsid = fs_person.id

    FS_Family = FS_Essentials = FS_Facts = FS_Parents = FS_Dup = FS_Dok = False

    tag_fs_dok = db.get_tag_from_name("FS_Dok")
    if tag_fs_dok and tag_fs_dok.handle in gr_person.tag_list:
        FS_Dok = True
    tag_fs_dup = db.get_tag_from_name("FS_Dup")
    if tag_fs_dup and tag_fs_dup.handle in gr_person.tag_list:
        FS_Dup = True

    # core comparisons
    rows: list[Any] = []

    Row = Tuple[Any, ...]
    row: Optional[Row]

    row = compare_gender(gr_person, fs_person)
    if row:
        rows.append(row)
        if row[0] != "green":
            FS_Essentials = True

    name_rows = compare_names(gr_person, fs_person)
    if name_rows:
        if name_rows[0][0] != "green":
            FS_Essentials = True
        rows.append(name_rows.pop(0))

    row = compare_fact(
        db, gr_person, fs_person, EventType.BIRTH, "http://gedcomx.org/Birth"
    )
    if row:
        rows.append(row)
        if row[0] != "green":
            FS_Essentials = True

    row = compare_fact(
        db, gr_person, fs_person, EventType.BAPTISM, "http://gedcomx.org/Baptism"
    )
    if row:
        rows.append(row)
        if row[0] != "green":
            FS_Essentials = True

    row = compare_fact(
        db, gr_person, fs_person, EventType.DEATH, "http://gedcomx.org/Death"
    )
    if row:
        rows.append(row)
        if row[0] != "green":
            FS_Essentials = True

    row = compare_fact(
        db, gr_person, fs_person, EventType.BURIAL, "http://gedcomx.org/Burial"
    )
    if row:
        rows.append(row)
        if row[0] != "green":
            FS_Essentials = True

    # mypy: session can be None
    fs_session = getattr(tree, "_fs_session", None)

    connected = fs_session is not None
    hdr_gr = _("Gramps")
    hdr_fs = _("FamilySearch") if connected else _("Not connected to FamilySearch")

    def add_section(
        title: str, semantic_color: str, node_key: str, children: Any
    ) -> None:
        """
        Adds header row + children rows to the tree model.
        The header row uses the color column as a section badge tint.
        """
        if not model or not children:
            return

        header = [
            semantic_color,
            title,
            "",  # Gramps date
            hdr_gr,  # Gramps value column carries label
            "",  # FS date
            hdr_fs,  # FS value column carries label/status
            "",  # spacer
            False,
            node_key,
            None,
            None,
            None,
            None,
        ]

        # mypy: model.add may return Optional[Tuple[...]]
        sec_id_opt: Optional[Tuple[Any, ...]] = model.add(_ui_row(header))
        if sec_id_opt is None:
            return
        sec_id = sec_id_opt

        for line in children:
            model.add(_ui_row(line), node=sec_id)

    if model and rows:
        sec_color = "white" if not connected else ("red" if FS_Essentials else "green")
        add_section(_("Essentials"), sec_color, "EssentialsKey", rows)

    if name_rows and model:
        any_non_green = any(line[0] != "green" for line in name_rows)
        sec_color = "white" if not connected else ("red" if any_non_green else "green")
        add_section(_("Other names"), sec_color, "OtherNamesKey", name_rows)

    # parents
    parent_rows = compare_parents(db, gr_person, fs_person)
    FS_Parents = any(line[0] != "green" for line in parent_rows)
    if model and parent_rows:
        sec_color = "white" if not connected else ("red" if FS_Parents else "green")
        add_section(_("Parents"), sec_color, "ParentsKey", parent_rows)

    # families (spouses/children/events)
    fam_rows = compare_spouses(db, gr_person, fs_person)
    FS_Family = any(line[0] != "green" for line in fam_rows)
    if model and fam_rows:
        sec_color = "white" if not connected else ("red" if FS_Family else "green")
        add_section(_("Families"), sec_color, "FamiliesKey", fam_rows)

    # other facts
    other_rows = compare_other_facts(db, gr_person, fs_person)
    FS_Facts = any(line[0] != "green" for line in other_rows)
    if model and other_rows:
        sec_color = "white" if not connected else ("red" if FS_Facts else "green")
        add_section(_("Facts"), sec_color, "FactsKey", other_rows)

    if not connected or fs_session is None:
        return

    # ensure we have Last-Modified/Etag for this person, FSID redirect
    if getattr(fs_person, "id", None) and (
        not hasattr(fs_person, "_last_modified")
        or not getattr(fs_person, "_last_modified", 0)
    ):
        path = "/platform/tree/persons/" + fs_person.id
        r = fs_session.head_url(path)

        while (
            r is not None
            and getattr(r, "status_code", 0) == 301
            and hasattr(r, "headers")
            and "X-Entity-Forwarded-Id" in r.headers
        ):
            fsid = r.headers["X-Entity-Forwarded-Id"]
            fs_utilities.link_gramps_fs_id(db, gr_person, fsid)
            fs_person.id = fsid
            path = "/platform/tree/persons/" + fs_person.id
            r = fs_session.head_url(path)

        if r is not None and hasattr(r, "headers"):
            if "Last-Modified" in r.headers:
                fs_person._last_modified = int(
                    time.mktime(email.utils.parsedate(r.headers["Last-Modified"]))
                )
            if "Etag" in r.headers:
                fs_person._etag = r.headers["Etag"]

    if not hasattr(fs_person, "_last_modified"):
        fs_person._last_modified = 0

    FS_Identical = not (FS_Family or FS_Essentials or FS_Facts or FS_Parents)

    # optionally query for potential duplicates/documents
    if getattr(fs_person, "id", None) and dupdoc and fs_session is not None:
        path = "/platform/tree/persons/" + fs_person.id + "/matches"
        r = fs_session.head_url(path, {"Accept": "application/x-gedcomx-atom+json"})
        if r and getattr(r, "status_code", 0) == 200:
            FS_Dup = True
        if r and getattr(r, "status_code", 0) != 200:
            FS_Dup = False

        path = (
            "https://www.familysearch.org/service/tree/tree-data/record-matches/"
            + fs_person.id
        )
        r = fs_session.get_url(path, {"Accept": "application/json"})
        if r and getattr(r, "status_code", 0) == 200:
            try:
                js = r.json()
                if (
                    js
                    and "data" in js
                    and "matches" in js["data"]
                    and len(js["data"]["matches"]) >= 1
                ):
                    FS_Dok = True
                else:
                    FS_Dok = False
            except Exception as e:
                logger.warning("WARNING: corrupted file from %s, error: %s", path, e)
                logger.debug("Response content: %s", getattr(r, "content", b""))

    # Update persistent status store
    now = int(time.time())
    db_state.status_ts = now

    # Track what we compared against (optional but useful)
    try:
        db_state.gramps_modified_ts = int(getattr(gr_person, "change", 0) or 0)
    except Exception:
        pass
    try:
        db_state.fs_modified_ts = int(getattr(fs_person, "_last_modified", 0) or 0)
    except Exception:
        pass

    # Conflict flags
    db_state.essential_conflict = bool(FS_Essentials)
    db_state.conflict = bool(not FS_Identical)

    # "confirmed" means identical as of now and newer than last confirmed baseline
    if FS_Identical and (
        not db_state.confirmed_ts
        or (gr_person.change > db_state.confirmed_ts)
        or (fs_person._last_modified > db_state.confirmed_ts)
    ):
        db_state.confirmed_ts = now

    # Persist the updated db_state
    try:
        db_state.commit()
    except Exception:
        pass

    return []
