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

import time
from typing import Any, TYPE_CHECKING

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.lib import Person

_ = glocale.translation.gettext

FS_DIRECT_TAGS = {
    "http://gedcomx.org/Birth",
    "http://gedcomx.org/Death",
    "http://gedcomx.org/Baptism",
    "http://gedcomx.org/Christening",
    "http://gedcomx.org/Burial",
    "http://gedcomx.org/Marriage",
    "http://gedcomx.org/Divorce",
}

FS_MENTION_ONLY = {"http://gedcomx.org/Name", "http://gedcomx.org/Gender"}


class HelpersMixin:
    """
    - this mixin is used with CacheMixin (provides
      _ensure_person_cached/_ensure_sources_cached)
    - and a host object that provides dbstate (Gramps DBState).
    """

    dbstate: Any

    if TYPE_CHECKING:

        def _ensure_sources_cached(self, fsid: str) -> None: ...

        def _ensure_person_cached(
            self, fsid: str, *, with_relatives: bool, force: bool = False
        ) -> Any: ...

    def _pretty_tags(self, tags: list[str]) -> str:
        labs: list[str] = []
        for t in tags:
            try:
                if t.startswith("http://gedcomx.org/"):
                    labs.append(t.split("/")[-1])
                else:
                    labs.append(t)
            except Exception:
                pass

        order = [
            "Birth",
            "Baptism",
            "Christening",
            "Marriage",
            "Divorce",
            "Death",
            "Burial",
            "Gender",
            "Name",
        ]
        labs = sorted(
            set(labs),
            key=lambda x: (order.index(x) if x in order else 99, x),
        )
        return ", ".join(labs)

    def _classify_simple(self, tags: list[str]) -> str:
        if not tags:
            return "Mention"
        if all(t in FS_MENTION_ONLY for t in tags):
            return "Mention"
        if any(t in FS_DIRECT_TAGS for t in tags):
            return "Direct"
        return "Direct"

    def _gather_sr_meta(self, fsid: str) -> dict[str, dict[str, Any]]:
        self._ensure_sources_cached(fsid)
        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()

        meta: dict[str, dict[str, Any]] = {}

        def add(sr: Any) -> None:
            sdid = getattr(sr, "descriptionId", None)
            if not sdid:
                return

            entry = meta.setdefault(
                sdid,
                {"tags": set(), "kind": "Mention", "contributor": "", "modified": ""},
            )

            try:
                for t in getattr(sr, "tags", []) or []:
                    val = getattr(t, "resource", None) or str(t)
                    if val:
                        entry["tags"].add(val)
            except Exception:
                pass

            try:
                attr = getattr(sr, "attribution", None)
                rid = (
                    getattr(getattr(attr, "contributor", None), "resourceId", "")
                    if attr
                    else ""
                )
                mod_ms = getattr(attr, "modified", None)
                mod_iso = ""
                if isinstance(mod_ms, (int, float)):
                    mod_iso = time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(mod_ms / 1000.0)
                    )

                def _to_ts(s: str) -> float:
                    try:
                        return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
                    except Exception:
                        return 0

                if _to_ts(mod_iso) >= _to_ts(str(entry["modified"])):
                    entry["contributor"] = rid or str(entry["contributor"])
                    entry["modified"] = mod_iso or str(entry["modified"])
            except Exception:
                pass

        for sr in getattr(fs_person, "sources", []) or []:
            add(sr)

        for rel in getattr(fs_person, "_spouses", []) or []:
            for sr in getattr(rel, "sources", []) or []:
                add(sr)

        for sdid, entry in meta.items():
            tags = list(entry["tags"])
            entry["kind"] = self._classify_simple(tags)
            entry["tags"] = tags

        return meta

    def _label_for_person_id(self, pid: str) -> str:
        try:
            self._ensure_person_cached(pid, with_relatives=False)
            person = deserialize.Person.index.get(pid)
            if person:
                name = person.preferred_name()
                return f"{name.akSurname()}, {name.akGiven()} [{pid}]"
        except Exception:
            pass
        return f"[{pid}]"

    def _find_person_by_fsid(self, fsid: str) -> Person | None:
        for handle in self.dbstate.db.iter_person_handles():
            person = self.dbstate.db.get_person_from_handle(handle)
            if fs_utilities.get_fsftid(person) == fsid:
                return person
        return None
