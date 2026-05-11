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
"""
Tags created (English, stable identifiers):
  - FS_Linked     (default: white)
  - FS_NotLinked  (default: black)
  - FS_Synced     (default: green)
  - FS_OutOfSync  (default: yellow)

- Never opens a DbTxn inside another DbTxn.
- If a transaction is already open (db.transaction), reuses it.

Public API:
- ensure_fs_tags(db) -> None
- retag_all_link_status(db) -> (total, linked, not_linked, changed)
- set_sync_status_for_person(db, person, is_synced=bool) -> None
- compute_sync_from_payload(data) -> bool
- explain_out_of_sync(data) -> list[str]
- get_tag_color_ui_note() -> str
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.lib import Person, Tag

from gramps.gen.fs import utils as fs_utilities

_ = glocale.translation.gettext

TAG_LINKED = "FS_Linked"
TAG_NOT_LINKED = "FS_NotLinked"
TAG_SYNCED = "FS_Synced"
TAG_OUT_OF_SYNC = "FS_OutOfSync"

ALL_FS_TAGS: Tuple[str, str, str, str] = (
    TAG_LINKED,
    TAG_NOT_LINKED,
    TAG_SYNCED,
    TAG_OUT_OF_SYNC,
)

DEFAULT_TAG_COLORS: Dict[str, str] = {
    TAG_LINKED: "white",
    TAG_NOT_LINKED: "black",
    TAG_SYNCED: "green",
    TAG_OUT_OF_SYNC: "yellow",
}

EXCLUSIVE_SETS: Tuple[Tuple[str, str], Tuple[str, str]] = (
    (TAG_LINKED, TAG_NOT_LINKED),
    (TAG_SYNCED, TAG_OUT_OF_SYNC),
)


@contextmanager
def _txn(db, title: str) -> Iterator[DbTxn]:
    existing = getattr(db, "transaction", None)
    if existing:
        yield existing
        return
    with DbTxn(title, db) as txn:
        yield txn


def _ensure_tag(db, name: str, *, txn: DbTxn) -> Tag:
    tag = db.get_tag_from_name(name)
    if tag:
        return tag

    tag = Tag()
    tag.set_name(name)
    tag.set_color(DEFAULT_TAG_COLORS.get(name, "yellow"))

    db.add_tag(tag, txn)
    db.commit_tag(tag, txn)
    return tag


def ensure_fs_tags(db) -> None:
    """
    Ensure all FamilySearch tags exist. Does not override any user customizations.
    """
    with _txn(db, "Ensure FamilySearch tags") as txn:
        for name in ALL_FS_TAGS:
            _ensure_tag(db, name, txn=txn)


def _remove_tags_by_name(db, person: Person, names: Iterable[str]) -> bool:
    names_set = set(names or [])
    if not names_set:
        return False

    current_handles = set(person.get_tag_list() or [])
    if not current_handles:
        return False

    changed = False
    for nm in names_set:
        tag = db.get_tag_from_name(nm)
        if tag and tag.handle in current_handles:
            current_handles.remove(tag.handle)
            changed = True

    if changed:
        person.set_tag_list(list(current_handles))
    return changed


def _add_tag_by_name(db, person: Person, name: str, *, txn: DbTxn) -> bool:
    tag = _ensure_tag(db, name, txn=txn)
    handles = set(person.get_tag_list() or [])
    if tag.handle in handles:
        return False
    handles.add(tag.handle)
    person.set_tag_list(list(handles))
    return True


def _set_exclusive_tag(db, person: Person, target: str, *, txn: DbTxn) -> bool:
    changed = False
    for group in EXCLUSIVE_SETS:
        if target in group:
            changed |= _remove_tags_by_name(db, person, group)
            break
    changed |= _add_tag_by_name(db, person, target, txn=txn)
    return changed


def _extract_fsftid(person: Person) -> Optional[str]:
    """
    Return a normalized, stripped string if found.
    """
    try:
        fsid = fs_utilities.get_fsftid(person)
        if fsid:
            s = str(fsid).strip()
            return s or None
    except Exception:
        pass

    for attr in person.get_attribute_list() or []:
        try:
            atype = attr.get_type().get_string().strip().upper()
        except Exception:
            continue

        if atype in {"_FSFTID", "FSFTID", "FSID", "FS_FTID", "_FS_FTID"}:
            val = str(attr.get_value() or "").strip()
            if val:
                return val
    return None


def retag_all_link_status(db) -> Tuple[int, int, int, int]:
    """
    Tag everyone by FS link status
      - FS_Linked (default white) if person has an FSID
      - FS_NotLinked (default black) otherwise

    Returns: (total, linked_count, not_linked_count, changed_count)
    """
    total = linked = not_linked = changed = 0

    with _txn(db, "Retag all (FamilySearch link status)") as txn:
        _ensure_tag(db, TAG_LINKED, txn=txn)
        _ensure_tag(db, TAG_NOT_LINKED, txn=txn)

        for handle in db.iter_person_handles():
            total += 1
            person = db.get_person_from_handle(handle)
            if not person:
                continue

            fsid = _extract_fsftid(person)
            before = set(person.get_tag_list() or [])

            if fsid:
                _set_exclusive_tag(db, person, TAG_LINKED, txn=txn)
                linked += 1
            else:
                _set_exclusive_tag(db, person, TAG_NOT_LINKED, txn=txn)
                not_linked += 1

            after = set(person.get_tag_list() or [])
            if before != after:
                changed += 1
                db.commit_person(person, txn)

    return total, linked, not_linked, changed


def set_sync_status_for_person(db, person: Person, *, is_synced: bool) -> None:
    """
    Apply FS_Synced (default green) or FS_OutOfSync (default yellow) exclusively.

    - Respects existing transactions (no nesting).
    - Ensures the needed tag(s) exist.
    - Commits the person only if tag list changed.
    """
    target = TAG_SYNCED if is_synced else TAG_OUT_OF_SYNC

    with _txn(db, "Tag person FamilySearch sync state") as txn:
        changed = _set_exclusive_tag(db, person, target, txn=txn)
        if changed:
            db.commit_person(person, txn)


def _norm_color(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("color", value.get("status", ""))

    s = str(value).strip().lower()

    if s in {"green", "yellow", "red"}:
        return s

    if s in {
        "ok",
        "okay",
        "match",
        "matched",
        "equal",
        "same",
        "synced",
        "?",
        "?",
        "true",
        "yes",
        "y",
        "1",
    }:
        return "green"

    if s in {
        "warn",
        "warning",
        "diff",
        "different",
        "mismatch",
        "partial",
        "some",
        "changed",
    }:
        return "yellow"

    if s in {"error", "x", "no", "false", "n", "0", "bad"}:
        return "red"

    return s or "red"


def _all_green_simple_rows(rows: list) -> bool:
    if not rows:
        return True
    for r in rows:
        v = r[0] if isinstance(r, (list, tuple)) and r else r
        if _norm_color(v) != "green":
            return False
    return True


def compute_sync_from_payload(data: dict) -> bool:
    """
    Compute "synced" boolean from a compare payload structure.

    Expected structure:
    - data["overview"] = [{"title": "...", "rows": [row, ...]}, ...]
      Where each row may be dict with "columns", or list/tuple with first cell status
    - data["notes"] = [row, ...] with first cell status
    - data["sources"] = [row, ...] with first cell status
    """
    for group in data.get("overview") or []:
        for row in group.get("rows") or []:
            cols = row.get("columns") if isinstance(row, dict) else None
            v = (
                cols[0]
                if cols
                else (row[0] if isinstance(row, (list, tuple)) and row else row)
            )
            if _norm_color(v) != "green":
                return False

    if not _all_green_simple_rows(data.get("notes") or []):
        return False
    if not _all_green_simple_rows(data.get("sources") or []):
        return False

    return True


def explain_out_of_sync(data: dict) -> List[str]:
    reasons: List[str] = []

    for gi, group in enumerate(data.get("overview") or []):
        title = group.get("title", _("Group %(num)d") % {"num": gi + 1})
        for ri, row in enumerate(group.get("rows") or []):
            cols = row.get("columns") if isinstance(row, dict) else None
            v = (
                cols[0]
                if cols
                else (row[0] if isinstance(row, (list, tuple)) and row else row)
            )
            c = _norm_color(v)
            if c != "green":
                reasons.append(
                    _("Overview ? %(title)s ? row %(row)d not green (%(color)s)")
                    % {"title": title, "row": ri + 1, "color": c}
                )
                break

    for ri, row in enumerate(data.get("notes") or []):
        v = row[0] if isinstance(row, (list, tuple)) and row else row
        c = _norm_color(v)
        if c != "green":
            reasons.append(
                _("Notes ? row %(row)d not green (%(color)s)")
                % {"row": ri + 1, "color": c}
            )
            break

    for ri, row in enumerate(data.get("sources") or []):
        v = row[0] if isinstance(row, (list, tuple)) and row else row
        c = _norm_color(v)
        if c != "green":
            reasons.append(
                _("Sources ? row %(row)d not green (%(color)s)")
                % {"row": ri + 1, "color": c}
            )
            break

    return reasons


def get_tag_color_ui_note() -> str:
    return _(
        "FamilySearch status tag colors can be customized in Gramps via "
        "Edit Tags. This add-on only sets default colors when the tags "
        "are first created and will not override your custom choices."
    )


__all__ = [
    "TAG_LINKED",
    "TAG_NOT_LINKED",
    "TAG_SYNCED",
    "TAG_OUT_OF_SYNC",
    "ALL_FS_TAGS",
    "DEFAULT_TAG_COLORS",
    "EXCLUSIVE_SETS",
    "ensure_fs_tags",
    "retag_all_link_status",
    "set_sync_status_for_person",
    "compute_sync_from_payload",
    "explain_out_of_sync",
    "get_tag_color_ui_note",
]
