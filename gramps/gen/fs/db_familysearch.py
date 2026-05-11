# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
# Copyright (C) 2025-2026  Nick Hall
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

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from gramps.gen.db import DbTxn

LOG = logging.getLogger(__name__)

_STATUS_DEFAULTS = {
    "fsid": None,
    "is_root": False,
    "status_ts": None,
    "confirmed_ts": None,
    "gramps_modified_ts": None,
    "fs_modified_ts": None,
    "essential_conflict": False,
    "conflict": False,
}


def _as_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError, OverflowError):
        return None


def _as_bool(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("1", "true", "yes", "y", "on")


@contextmanager
def _txn_or_none(db, txn, label: str) -> Iterator[Any]:
    """
    Use caller-provided transaction when available, otherwise create one.
    """
    if txn is not None:
        yield txn
        return

    if db is None:
        yield None
        return

    with DbTxn(label, db) as t:
        yield t


class FSStatusDB:
    """
    FamilySearch sync status store backed by the core database API.

    Stored per Person handle via:
        db.get_familysearch_person_status(...)
        db.set_familysearch_person_status(...)
        db.delete_familysearch_person_status(...)
    """

    def __init__(self, db, p_handle: str | None = None):
        self.db = db
        self.p_handle = p_handle
        self._reset_fields()

    def _reset_fields(self) -> None:
        self.fsid: str | None = None
        self.is_root: bool = False
        self.status_ts: int | None = None
        self.confirmed_ts: int | None = None
        self.gramps_modified_ts: int | None = None
        self.fs_modified_ts: int | None = None
        self.essential_conflict: bool = False
        self.conflict: bool = False

    def _to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}

        if self.fsid:
            fsid = str(self.fsid).strip()
            if fsid:
                data["fsid"] = fsid

        if self.is_root:
            data["is_root"] = True

        for key, value in (
            ("status_ts", self.status_ts),
            ("confirmed_ts", self.confirmed_ts),
            ("gramps_modified_ts", self.gramps_modified_ts),
            ("fs_modified_ts", self.fs_modified_ts),
        ):
            iv = _as_int(value)
            if iv is not None and iv > 0:
                data[key] = iv

        if self.essential_conflict:
            data["essential_conflict"] = True

        if self.conflict:
            data["conflict"] = True

        return data

    def commit(self, txn=None) -> None:
        """
        Persist the current FamilySearch sync status for this person handle.
        """
        if not self.p_handle:
            LOG.warning("FSStatusDB.commit called without p_handle")
            return

        if self.db is None:
            LOG.warning("FSStatusDB.commit called without db")
            return

        data = self._to_dict()

        with _txn_or_none(self.db, txn, "FamilySearch: status update") as t:
            try:
                if data:
                    self.db.set_familysearch_person_status(self.p_handle, data, t)
                else:
                    self.db.delete_familysearch_person_status(self.p_handle, t)
            except Exception:
                LOG.debug(
                    "FSStatusDB.commit failed for handle=%s",
                    self.p_handle,
                    exc_info=True,
                )

    def get(self, person_handle: str | None = None) -> None:
        """
        Load FamilySearch sync status for the given person handle.
        """
        if not person_handle:
            person_handle = self.p_handle
        if not person_handle:
            LOG.warning("FSStatusDB.get called without person_handle")
            self._reset_fields()
            return

        self.p_handle = person_handle
        self._reset_fields()

        if self.db is None:
            LOG.warning("FSStatusDB.get called without db")
            return

        try:
            data = self.db.get_familysearch_person_status(self.p_handle, {})
        except Exception:
            LOG.debug(
                "FSStatusDB.get failed for handle=%s",
                self.p_handle,
                exc_info=True,
            )
            return

        if not isinstance(data, dict):
            data = {}

        self.fsid = str(data.get("fsid")).strip() if data.get("fsid") else None
        self.is_root = _as_bool(data.get("is_root"))
        self.status_ts = _as_int(data.get("status_ts"))
        self.confirmed_ts = _as_int(data.get("confirmed_ts"))
        self.gramps_modified_ts = _as_int(data.get("gramps_modified_ts"))
        self.fs_modified_ts = _as_int(data.get("fs_modified_ts"))
        self.essential_conflict = _as_bool(data.get("essential_conflict"))
        self.conflict = _as_bool(data.get("conflict"))


__all__ = ["FSStatusDB"]
