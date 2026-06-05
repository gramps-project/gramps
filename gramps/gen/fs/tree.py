# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
from typing import Iterable, Set
import asyncio
import email.utils
import time

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs.fs_import.deserializer import deserialize_json, to_string, DateFormal
from gramps.gen.fs.fs_import.deserializer import all_annotations, init_class
from gramps.gen.fs.fs_import.deserializer import (
    deserialize_json,
    serialize_json,
    to_string,
    parse,
)

from .constants import MAX_PERSONS

_fs_session = None


class Tree(deserialize.Gedcomx):
    def __init__(self):
        deserialize.init_class(self)
        self._fam = dict()
        self._places = dict()
        self._persons: dict[str, deserialize.Person] = {}
        self._getsources = True
        self._sources = dict()
        self._notes = []

    def add_person(self, fsid: str) -> None:
        global _fs_session
        if not _fs_session:
            return

        url = f"/platform/tree/persons/{fsid}"
        r = _fs_session.get_url(url)
        if not r:
            return

        try:
            data = r.json()
        except Exception as e:
            print("WARNING: corrupted response from %s, error: %s" % (url, e))
            try:
                print(r.content)
            except Exception:
                pass
            data = None

        if not data:
            return

        deserialize.deserialize_json(self, data)

        try:
            fs_person = deserialize.Person.index[fsid]
        except KeyError:
            return

        if "Last-Modified" in r.headers:
            try:
                fs_person._last_modified = int(
                    time.mktime(email.utils.parsedate(r.headers["Last-Modified"]))
                )
            except Exception:
                pass
        if "Etag" in r.headers:
            fs_person._etag = r.headers["Etag"]

        self._persons[fsid] = fs_person

    def add_persons(self, fids: Iterable[str]) -> None:
        async def _load_many(loop, ids: Iterable[str]):
            tasks = set()
            for fid in ids:
                if fid not in self._persons:
                    tasks.add(loop.run_in_executor(None, self.add_person, fid))
            for t in tasks:
                await t

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_load_many(loop, fids))

        for fid in fids:
            if fid in deserialize.Person.index:
                self._persons[fid] = deserialize.Person.index[fid]

    def add_parents(self, fids: Set[str]) -> Set[str]:
        rels: Set[str] = set()
        for fid in fids & set(self._persons.keys()):
            p = self._persons[fid]
            for rel in getattr(p, "_parents", []) or []:
                if rel.person1:
                    rels.add(rel.person1.resourceId)
                if rel.person2:
                    rels.add(rel.person2.resourceId)
            for cp in getattr(p, "_parentsCP", []) or []:
                if cp.parent1:
                    rels.add(cp.parent1.resourceId)
                if cp.parent2:
                    rels.add(cp.parent2.resourceId)

        rels.difference_update(fids)
        self.add_persons(rels)
        return set(filter(None, rels))

    def add_spouses(self, fids: Set[str]) -> Set[str]:
        rels: Set[str] = set()
        for fid in fids & set(self._persons.keys()):
            p = self._persons[fid]
            if getattr(p, "_spouses", None):
                for rel in p._spouses:
                    if rel.person1:
                        rels.add(rel.person1.resourceId)
                    if rel.person2:
                        rels.add(rel.person2.resourceId)

        rels.difference_update(fids)
        self.add_persons(rels)
        return set(filter(None, rels))

    def add_children(self, fids: Set[str]) -> Set[str]:
        rels: Set[str] = set()
        for fid in fids & set(self._persons.keys()):
            p = self._persons[fid]
            if getattr(p, "_children", None):
                for rel in p._children:
                    if getattr(rel, "person1", None):
                        rels.add(rel.person1.resourceId)
                    if getattr(rel, "person2", None):
                        rels.add(rel.person2.resourceId)

        rels.difference_update(fids)
        self.add_persons(rels)
        return set(filter(None, rels))


__all__ = ["Tree", "_fs_session", "DateFormal"]
