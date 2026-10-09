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

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, Set
import calendar
import email.utils
import logging
import time

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

LOG = logging.getLogger(__name__)

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

    def _fetch_raw(self, fsid: str):
        """
        Fetch the raw HTTP response for a single FamilySearch person without deserializing.

        Returns (fsid, response, data) where data is the parsed JSON or None on failure.
        """
        if not _fs_session:
            return fsid, None, None
        url = f"/platform/tree/persons/{fsid}"
        r = _fs_session.get_url(url)
        if not r:
            return fsid, None, None
        try:
            data = r.json()
        except Exception as exc:
            LOG.warning("Corrupted response from %s: %s", url, exc)
            data = None
        return fsid, r, data

    def add_person(self, fsid: str) -> None:
        """
        Fetch and deserialize a single FamilySearch person into this tree.
        """
        fsid, r, data = self._fetch_raw(fsid)
        if not r or not data:
            return

        deserialize.deserialize_json(self, data)

        try:
            fs_person = deserialize.Person.index[fsid]
        except KeyError:
            return

        if "Last-Modified" in r.headers:
            try:
                parsed = email.utils.parsedate(r.headers["Last-Modified"])
                if parsed is not None:
                    fs_person._last_modified = calendar.timegm(parsed)
            except Exception:
                pass
        if "Etag" in r.headers:
            fs_person._etag = r.headers["Etag"]

        self._persons[fsid] = fs_person

    def add_persons(self, fids: Iterable[str]) -> None:
        """
        Add multiple FamilySearch persons, fetching HTTP responses concurrently
        and deserializing sequentially to avoid shared-state races.
        """
        requested_fids = list(fids)
        to_fetch = [fid for fid in requested_fids if fid not in self._persons]

        if to_fetch:
            raw_results: dict[str, tuple] = {}
            max_workers = min(8, len(to_fetch))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_raw, fid): fid for fid in to_fetch
                }
                for future in as_completed(futures):
                    try:
                        fsid, r, data = future.result()
                        if r is not None and data is not None:
                            raw_results[fsid] = (r, data)
                    except Exception:
                        LOG.warning(
                            "Failed to fetch FamilySearch person %s",
                            futures[future],
                            exc_info=True,
                        )

            for fid in to_fetch:
                if fid not in raw_results:
                    continue
                r, data = raw_results[fid]
                deserialize.deserialize_json(self, data)
                try:
                    fs_person = deserialize.Person.index[fid]
                except KeyError:
                    continue
                if "Last-Modified" in r.headers:
                    try:
                        parsed = email.utils.parsedate(r.headers["Last-Modified"])
                        if parsed is not None:
                            fs_person._last_modified = calendar.timegm(parsed)
                    except Exception:
                        pass
                if "Etag" in r.headers:
                    fs_person._etag = r.headers["Etag"]
                self._persons[fid] = fs_person

        for fid in requested_fids:
            if fid not in self._persons and fid in deserialize.Person.index:
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
            display = getattr(p, "display", None)
            for family in getattr(display, "familiesAsParent", []) or []:
                if getattr(family, "parent1", None):
                    rels.add(family.parent1.resourceId)
                if getattr(family, "parent2", None):
                    rels.add(family.parent2.resourceId)

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
            for cp_rel in getattr(p, "_childrenCP", []) or []:
                if getattr(cp_rel, "parent1", None):
                    rels.add(cp_rel.parent1.resourceId)
                if getattr(cp_rel, "parent2", None):
                    rels.add(cp_rel.parent2.resourceId)
                if getattr(cp_rel, "child", None):
                    rels.add(cp_rel.child.resourceId)
            display = getattr(p, "display", None)
            for family in getattr(display, "familiesAsParent", []) or []:
                for child in getattr(family, "children", []) or []:
                    if getattr(child, "resourceId", None):
                        rels.add(child.resourceId)

        rels.difference_update(fids)
        self.add_persons(rels)
        return set(filter(None, rels))


__all__ = ["Tree", "_fs_session", "DateFormal"]
