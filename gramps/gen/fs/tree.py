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
from typing import Callable, Iterable, Set
import calendar
import email.utils
import logging
import time
import re

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs.session import FSException

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
_ = glocale.translation.gettext

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

    def fetch_person(self, fsid: str) -> deserialize.Person:
        """
        Download a fresh person while keeping merged-ID redirects on the API route.

        :param fsid: The linked FamilySearch person ID.
        :returns: The downloaded person, with its current FamilySearch ID.
        :raises FSException: If the service cannot return the requested person.
        """
        if _fs_session is None:
            raise FSException(
                _("Not connected to FamilySearch. Sign in and try again.")
            )
        current_id = fsid
        visited: set[str] = set()
        while current_id not in visited and len(visited) < 20:
            visited.add(current_id)
            endpoint = f"/platform/tree/persons/{current_id}"
            try:
                response = _fs_session.get_url(endpoint, allow_redirects=False)
            except Exception as error:
                raise FSException(
                    _(
                        "FamilySearch person download failed. Check your connection and sign in again."
                    )
                ) from error
            if response is None:
                raise FSException(
                    _("FamilySearch returned no response for this person.")
                )
            if response.status_code == 301:
                forwarded = response.headers.get("X-Entity-Forwarded-Id", "").strip()
                if not re.fullmatch(r"[A-Za-z0-9]{4}-[A-Za-z0-9]{3}", forwarded):
                    raise FSException(
                        _("FamilySearch returned an invalid merged person ID.")
                    )
                current_id = forwarded
                continue
            if response.status_code != 200:
                raise FSException(
                    _(
                        "FamilySearch person download failed (HTTP %s). Sign in again or check the linked person ID."
                    )
                    % response.status_code
                )
            try:
                data = response.json()
            except ValueError as error:
                raise FSException(
                    _("FamilySearch returned invalid person data.")
                ) from error
            payload = data.get("person", data) if isinstance(data, dict) else None
            people = payload.get("persons") if isinstance(payload, dict) else None
            if not isinstance(people, list) or not any(
                isinstance(person, dict) and person.get("id") == current_id
                for person in people
            ):
                raise FSException(
                    _(
                        "FamilySearch did not return the linked person. Check the person ID and selected server."
                    )
                )
            deserialize.Person.index.pop(current_id, None)
            self.persons = {
                cached for cached in (self.persons or set()) if cached.id != current_id
            }
            deserialize.deserialize_json(self, data)
            person = deserialize.Person.index.get(current_id)
            if person is None:
                raise FSException(_("FamilySearch person data could not be read."))
            self._persons[current_id] = person
            return person
        raise FSException(_("FamilySearch returned a circular merged person redirect."))

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

    def add_persons(
        self,
        fids: Iterable[str],
        progress_callback: Callable[[], None] | None = None,
    ) -> None:
        """
        Add multiple FamilySearch persons, fetching HTTP responses concurrently
        and deserializing sequentially to avoid shared-state races.

        :param progress_callback: optional callable invoked after each
            concurrent fetch completes, so a caller (e.g. the GUI layer) can
            report progress and keep the interface responsive during what
            may be a long-running batch of network requests.
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
                    if progress_callback is not None:
                        progress_callback()

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

    def add_parents(
        self,
        fids: Set[str],
        progress_callback: Callable[[], None] | None = None,
    ) -> Set[str]:
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
        self.add_persons(rels, progress_callback=progress_callback)
        return set(filter(None, rels))

    def add_spouses(
        self,
        fids: Set[str],
        progress_callback: Callable[[], None] | None = None,
    ) -> Set[str]:
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
        self.add_persons(rels, progress_callback=progress_callback)
        return set(filter(None, rels))

    def add_children(
        self,
        fids: Set[str],
        progress_callback: Callable[[], None] | None = None,
    ) -> Set[str]:
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
        self.add_persons(rels, progress_callback=progress_callback)
        return set(filter(None, rels))


__all__ = ["Tree", "_fs_session", "DateFormal"]
