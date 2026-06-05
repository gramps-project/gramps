# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026 Gabriel Rios
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

"""
helpers for the FamilySearch integration layer.
some FS modules are still coupled through shared session state and thin wrapper calls.
"""

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import logging
import os
from typing import Any

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import HandleError
from gramps.gen.fs import tree as fs_tree
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.lib import Attribute, AttributeType, ChildRef, Family, Person

logger = logging.getLogger(__name__)

_ = glocale.translation.gettext

FS_ATTR_CANON = "_FSFTID"
FS_ATTR_OLD = "_FSTID"
FS_ATTR_HUMAN = "FamilySearch ID"


def _dbg(msg: str) -> None:
    """Log a debug message only when the FS debug env var is switched on."""
    if os.environ.get("GRAMPS_FS_DEBUG", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        logger.debug("%s", msg)


def _bind_global_session(session) -> None:
    """Mirror the active session onto `tree._fs_session` for shared FS helpers."""
    # gen.fs uses read tree._fs_session directly
    fs_tree._fs_session = session


def _get_fs_id(person) -> str:
    """Pull the first FamilySearch id we can find from a person's attrs."""
    if not person:
        return ""
    for attr in person.get_attribute_list() or []:
        atype = str(attr.get_type())
        if atype in (FS_ATTR_CANON, FS_ATTR_OLD, FS_ATTR_HUMAN):
            value = (attr.get_value() or "").strip()
            if value:
                return value
    return ""


def _set_fs_id(person, fsid: str) -> None:
    """replace any legacy FS id attrs w/ one canonical attr."""
    if not person:
        return

    fsid = (fsid or "").strip()

    attrs = person.get_attribute_list() or []
    attrs[:] = [
        attr
        for attr in attrs
        if str(attr.get_type()) not in (FS_ATTR_CANON, FS_ATTR_OLD, FS_ATTR_HUMAN)
    ]

    if fsid:
        attr = Attribute()
        attr.set_type(AttributeType(FS_ATTR_CANON))
        attr.set_value(fsid)
        attrs.append(attr)

    person.set_attribute_list(attrs)


def _platform_json(session, endpoint: str) -> dict:
    """
    Fetch GEDCOM X JSON from a `/platform/...` endpoint.

    Session already knows how to hit FS endpoints, attach auth,
    and decode JSON.
    """
    data = session.get_jsonurl(
        endpoint, headers={"Accept": "application/x-gedcomx-v1+json"}
    )
    return data if isinstance(data, dict) else {}


def _fs_display_name(person_data: dict) -> str:
    """Return the display/full name from FS person payload data."""
    display = (person_data or {}).get("display") or {}
    return (display.get("name") or display.get("fullName") or "").strip()


def _ensure_child_ref(child_handle: str) -> ChildRef:
    child_ref = ChildRef()
    if hasattr(child_ref, "set_reference_handle"):
        child_ref.set_reference_handle(child_handle)
    else:
        child_ref.ref = child_handle
    return child_ref


def _family_other_parent_handle(fam: Family, me_handle: str):
    """Given one parent handle, return the other parent if there is one."""
    father_handle = fam.get_father_handle()
    mother_handle = fam.get_mother_handle()
    if father_handle == me_handle:
        return mother_handle
    if mother_handle == me_handle:
        return father_handle
    return None


def _ensure_person_has_family_handle(db, txn, person: Person, fam_handle: str) -> None:
    """Add a family handle to the person's spouse-family list if missing."""
    fams = list(person.get_family_handle_list() or [])
    if fam_handle not in fams:
        fams.append(fam_handle)
        person.set_family_handle_list(fams)
        db.commit_person(person, txn)


def _ensure_person_has_parent_family_handle(
    db, txn, person: Person, fam_handle: str
) -> None:
    fams = list(person.get_parent_family_handle_list() or [])
    if fam_handle not in fams:
        fams.append(fam_handle)
        person.set_parent_family_handle_list(fams)
        db.commit_person(person, txn)


def _ensure_child_in_family(db, fam: Family, child_handle: str) -> bool:
    """Append the child ref only when the family does not already point to it."""
    for child_ref in fam.get_child_ref_list() or []:
        try:
            if getattr(child_ref, "ref", None) == child_handle:
                return False
            if (
                hasattr(child_ref, "get_reference_handle")
                and child_ref.get_reference_handle() == child_handle
            ):
                return False
        except Exception:
            logger.debug(
                "Failed to inspect child reference while checking family children",
                exc_info=True,
            )

    fam.add_child_ref(_ensure_child_ref(child_handle))
    return True


def _place_parent_in_family(db, fam: Family, parent_handle: str) -> None:
    """Drop a parent into the father/mother slot that fits best."""
    try:
        person = db.get_person_from_handle(parent_handle)
        gender = person.get_gender()
    except HandleError:
        gender = Person.UNKNOWN
    except Exception:
        logger.debug(
            "Failed to determine parent gender for handle=%s",
            parent_handle,
            exc_info=True,
        )
        gender = Person.UNKNOWN

    father_handle = fam.get_father_handle()
    mother_handle = fam.get_mother_handle()

    if gender == Person.MALE:
        if not father_handle:
            fam.set_father_handle(parent_handle)
        elif not mother_handle and father_handle != parent_handle:
            fam.set_mother_handle(parent_handle)
        return

    if gender == Person.FEMALE:
        if not mother_handle:
            fam.set_mother_handle(parent_handle)
        elif not father_handle and mother_handle != parent_handle:
            fam.set_father_handle(parent_handle)
        return

    # fallback for unknown gender: first open slot wins.
    if not father_handle:
        fam.set_father_handle(parent_handle)
    elif not mother_handle:
        fam.set_mother_handle(parent_handle)


def _family_parent_set(fam: Family) -> set[str]:
    """Return non-empty parent handles for quick set comparison."""
    return set(filter(None, [fam.get_father_handle(), fam.get_mother_handle()]))


def _find_existing_family_for_parents(db, parent_handles: set[str]) -> Family | None:
    """Look for a family that already has exactly this parent pair."""
    if not parent_handles:
        return None

    # this is usually cheaper than scanning every family in the db.
    for parent_handle in parent_handles:
        try:
            person = db.get_person_from_handle(parent_handle)
        except HandleError:
            continue
        except Exception:
            logger.debug(
                "Failed to load parent person for handle=%s",
                parent_handle,
                exc_info=True,
            )
            continue

        if not person:
            continue

        for fam_handle in person.get_family_handle_list() or []:
            if not fam_handle:
                continue
            try:
                fam = db.get_family_from_handle(fam_handle)
            except HandleError:
                fam = None
            except Exception:
                logger.debug(
                    "Failed to load family for handle=%s",
                    fam_handle,
                    exc_info=True,
                )
                fam = None

            if fam and _family_parent_set(fam) == parent_handles:
                return fam

    return None


def _find_person_by_fsid(db, fsid: str):
    """Find a person by FS id, using the cache first and a full scan second."""
    fsid = (fsid or "").strip()
    if not fsid:
        return None

    idx = getattr(fs_utilities, "FS_INDEX_PEOPLE", {})
    handle = idx.get(fsid) if hasattr(idx, "get") else None
    if handle:
        try:
            return db.get_person_from_handle(handle)
        except HandleError:
            idx.pop(fsid, None)
        except Exception:
            logger.debug(
                "Failed to load cached FamilySearch person for fsid=%s",
                fsid,
                exc_info=True,
            )

    # cache miss or stale cache
    get_fsftid = getattr(fs_utilities, "get_fsftid", None)

    for handle in db.get_person_handles():
        person = db.get_person_from_handle(handle)
        if not person:
            continue
        try:
            pid = get_fsftid(person) if callable(get_fsftid) else ""
        except Exception:
            logger.debug(
                "Failed to read FamilySearch ID while scanning person handle=%s",
                handle,
                exc_info=True,
            )
            pid = ""
        if pid == fsid:
            return person

    return None


def _strip_unknowns_inplace(data: Any) -> None:
    """Remove known FS visibility flags from nested payload data."""
    key = "PersonInfo:visibleToAllWhenUsingFamilySearchApps"
    if isinstance(data, dict):
        data.pop(key, None)
        for value in list(data.values()):
            _strip_unknowns_inplace(value)
    elif isinstance(data, list):
        for value in list(data):
            _strip_unknowns_inplace(value)


def _resolve_redirected_fsid(session, fsid: str) -> str:
    """Follow FamilySearch redirect headers until we land on the current id."""
    fsid = (fsid or "").strip()
    if not fsid:
        return fsid

    head = getattr(session, "head_url", None)
    if not callable(head):
        return fsid

    try:
        path = f"/platform/tree/persons/{fsid}"
        resp = head(path)
        while resp is not None and getattr(resp, "status_code", None) == 301:
            headers = getattr(resp, "headers", {}) or {}
            forwarded = headers.get("X-Entity-Forwarded-Id") or headers.get(
                "x-entity-forwarded-id"
            )
            if not forwarded:
                break
            fsid = str(forwarded).strip()
            path = f"/platform/tree/persons/{fsid}"
            resp = head(path)
    except Exception:
        logger.debug(
            "Failed to resolve redirected FamilySearch ID for fsid=%s",
            fsid,
            exc_info=True,
        )

    return fsid


def _ensure_status_schema(db) -> None:
    # status lives on Person now, not in a separate DB table.
    return


__all__ = [
    "FS_ATTR_CANON",
    "FS_ATTR_OLD",
    "FS_ATTR_HUMAN",
    "_dbg",
    "_bind_global_session",
    "_get_fs_id",
    "_set_fs_id",
    "_platform_json",
    "_fs_display_name",
    "_ensure_child_ref",
    "_family_other_parent_handle",
    "_ensure_person_has_family_handle",
    "_ensure_person_has_parent_family_handle",
    "_ensure_child_in_family",
    "_place_parent_in_family",
    "_family_parent_set",
    "_find_existing_family_for_parents",
    "_find_person_by_fsid",
    "_strip_unknowns_inplace",
    "_resolve_redirected_fsid",
    "_ensure_status_schema",
]
