# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023-2026  Gabriel Rios
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
import email.utils
import json
import os
import time
from typing import Any, ClassVar, Optional, Tuple

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs import tree
from gramps.gen.fs.fs_import import deserializer as deserialize

_ = glocale.translation.gettext


class _FsCacheEntry:
    """In-memory metadata for an FSID cached on disk."""

    def __init__(self, etag: Optional[str], last_mod: Optional[int]) -> None:
        self.etag: Optional[str] = etag
        self.last_modified: Optional[int] = last_mod
        self.loaded_notes: bool = False
        self.loaded_sources: bool = False


class _FsCache:
    """Simple JSON-on-disk cache: one file per FSID under <base>/fs_cache/."""

    def __init__(self, base_dir: str) -> None:
        self.mem: dict[str, _FsCacheEntry] = {}
        self.base_dir = os.path.join(base_dir, "fs_cache")
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, fsid: str) -> str:
        return os.path.join(self.base_dir, f"{fsid}.json")

    def get_meta(self, fsid: str) -> Optional[_FsCacheEntry]:
        return self.mem.get(fsid)

    def set_meta(self, fsid: str, etag: Optional[str], last_mod: Optional[int]) -> None:
        entry = self.mem.get(fsid) or _FsCacheEntry(etag, last_mod)
        entry.etag = etag
        entry.last_modified = last_mod
        self.mem[fsid] = entry

    def mark_loaded(
        self, fsid: str, *, notes: bool = False, sources: bool = False
    ) -> None:
        e = self.mem.get(fsid)
        if not e:
            e = _FsCacheEntry(None, None)
            self.mem[fsid] = e
        if notes:
            e.loaded_notes = True
        if sources:
            e.loaded_sources = True

    def write_json(
        self,
        fsid: str,
        data: dict[str, Any],
        etag: Optional[str],
        last_mod: Optional[int],
    ) -> None:
        """
        Atomically write the cache blob to disk (fsync + replace).
        File layout:
          {
            "etag": "...",
            "last_modified": 1690000000,
            "person": { "persons": [ <GedcomX Person JSON> ] }
          }
        """
        path = self._path(fsid)
        tmp_path = path + ".tmp"
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"etag": etag, "last_modified": last_mod, "person": data},
                    f,
                    ensure_ascii=False,
                )
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        except Exception as e:
            print(f"[FS Cache] failed to write {fsid}: {e}")
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    def read_json(
        self, fsid: str
    ) -> Optional[Tuple[dict[str, Any], Optional[str], Optional[int]]]:
        """
        Read cache file for FSID.
        Returns: (person_blob, etag, last_modified) or None on error/missing.
        """
        p = self._path(fsid)
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                blob = json.load(f)

            person_blob = blob.get("person")
            if not isinstance(person_blob, dict):
                return None

            return person_blob, blob.get("etag"), blob.get("last_modified")
        except Exception:
            return None

    def clear(self) -> None:
        """Clear all cached FS JSON files on disk and reset in-memory metadata."""
        self.mem.clear()
        try:
            for fname in os.listdir(self.base_dir):
                if not fname.endswith(".json"):
                    continue
                try:
                    os.remove(os.path.join(self.base_dir, fname))
                except Exception:
                    pass
        except Exception as e:
            print(f"[FS Cache] failed to clear cache dir {self.base_dir}: {e}")


class CacheMixin:
    """
    Mix-in that ensures a person (and optionally relatives) is available
    in the in-memory Tree, using a disk cache to avoid re-downloading.

    Typing note:
    `fs_Tree` and `_cache` are initialized by the addon at runtime (session/init).
    Declaring them here documents the contract and prevents mypy attr-defined errors.
    """

    fs_Tree: ClassVar[Any] = None
    _cache: ClassVar[Optional[_FsCache]] = None

    @classmethod
    def _get_fs_tree(cls) -> Any:
        fs_tree = cls.fs_Tree
        if fs_tree is None:
            raise RuntimeError("CacheMixin.fs_Tree was not initialized")
        return fs_tree

    @staticmethod
    def _get_fs_session() -> Any:
        fs_session = getattr(tree, "_fs_session", None)
        if fs_session is None:
            raise RuntimeError(
                "FamilySearch session (tree._fs_session) is not initialized"
            )
        return fs_session

    def _ensure_person_cached(
        self,
        fsid: str,
        *,
        with_relatives: bool,
        force: bool = False,
    ) -> deserialize.Person:
        fs_tree = self.__class__._get_fs_tree()
        fs_session = self._get_fs_session()
        cache = self.__class__._cache

        etag: Optional[str] = None
        last_mod: Optional[int] = None

        # Fetch headers for freshness checks (etag / last-modified)
        if force or (fsid not in fs_tree._persons):
            r = fs_session.head_url(f"/platform/tree/persons/{fsid}")
            if r and r.status_code == 301 and "X-Entity-Forwarded-Id" in r.headers:
                fsid = r.headers["X-Entity-Forwarded-Id"]
            if r:
                etag = r.headers.get("Etag")
                lm = r.headers.get("Last-Modified")
                last_mod = int(time.mktime(email.utils.parsedate(lm))) if lm else None

        ce = cache.get_meta(fsid) if cache else None
        up_to_date = (
            (not force)
            and ce
            and (
                (ce.etag and etag and ce.etag == etag)
                or (ce.last_modified and last_mod and ce.last_modified == last_mod)
            )
        )

        if not up_to_date:
            # Disk cache first
            disk = None if (force or not cache) else cache.read_json(fsid)
            if (
                disk
                and (etag is None or disk[1] == etag)
                and (last_mod is None or disk[2] == last_mod)
            ):
                try:
                    # disk[0] := {"persons":[ <person json> ]}
                    deserialize.deserialize_json(fs_tree, disk[0])
                except Exception as e:
                    print(f"[FS Cache] deserialize (disk) failed for {fsid}: {e}")

                p = deserialize.Person.index.get(fsid)
                if p:
                    # mypy dynamic attrs
                    setattr(p, "_etag", disk[1])
                    setattr(p, "_last_modified", disk[2])

                    fs_tree._persons[fsid] = p
                    if cache:
                        cache.set_meta(fsid, disk[1], disk[2])

            # If still not present, download and then write to disk cache
            if fsid not in fs_tree._persons:
                fs_tree.add_persons([fsid])
                p = deserialize.Person.index.get(fsid)
                if p:
                    fs_tree._persons[fsid] = p

                    if cache:
                        cache.set_meta(
                            fsid,
                            getattr(p, "_etag", None),
                            getattr(p, "_last_modified", None),
                        )

                        try:
                            full_tree: dict[str, Any] = deserialize.serialize_json(
                                fs_tree
                            )
                            persons: list[dict[str, Any]] = []

                            for pj in full_tree.get("persons") or []:
                                if not isinstance(pj, dict):
                                    continue
                                pid = pj.get("id") or pj.get("@id")
                                if pid == fsid:
                                    persons = [pj]
                                    break

                            if not persons and full_tree.get("persons"):
                                first = full_tree["persons"][0]
                                if isinstance(first, dict):
                                    persons = [first]

                            person_only: dict[str, Any] = {"persons": persons}
                            cache.write_json(
                                fsid,
                                person_only,
                                getattr(p, "_etag", None),
                                getattr(p, "_last_modified", None),
                            )
                        except Exception as e:
                            print(f"[FS Cache] serialize/write failed for {fsid}: {e}")

        if with_relatives:
            fs_tree.add_spouses({fsid})
            fs_tree.add_children({fsid})
            fs_tree.add_parents({fsid})

        return deserialize.Person.index.get(fsid) or deserialize.Person()

    def _ensure_notes_cached(self, fsid: str) -> None:
        cache = self.__class__._cache
        if cache:
            ce = cache.get_meta(fsid)
            if ce and ce.loaded_notes and deserialize.Person.index.get(fsid):
                return

        fs_session = self._get_fs_session()
        _get_json = getattr(fs_session, "get_jsonurl", None) or getattr(
            fs_session, "get_json", None
        )
        if _get_json:
            _get_json(f"/platform/tree/persons/{fsid}/notes")

        # compute spouses if not already present
        p0 = deserialize.Person.index.get(fsid)
        if not (p0 and getattr(p0, "_spouses", None) is not None):
            self.__class__._get_fs_tree().add_spouses({fsid})

        p = deserialize.Person.index.get(fsid)
        if p:
            for rel in getattr(p, "_spouses", []) or []:
                if _get_json:
                    _get_json(f"/platform/tree/couple-relationships/{rel.id}/notes")

        if cache:
            cache.mark_loaded(fsid, notes=True)

    def _ensure_sources_cached(self, fsid: str) -> None:
        cache = self.__class__._cache
        # loaded this session, dont fetch again
        if cache:
            ce = cache.get_meta(fsid)
            if ce and ce.loaded_sources and deserialize.Person.index.get(fsid):
                return

        fs_session = self._get_fs_session()
        _get_json = getattr(fs_session, "get_jsonurl", None) or getattr(
            fs_session, "get_json", None
        )
        if _get_json:
            _get_json(f"/platform/tree/persons/{fsid}/sources")

        # compute spouses if not already present
        p0 = deserialize.Person.index.get(fsid)
        if not (p0 and getattr(p0, "_spouses", None) is not None):
            self.__class__._get_fs_tree().add_spouses({fsid})

        p = deserialize.Person.index.get(fsid)
        if p:
            for rel in getattr(p, "_spouses", []) or []:
                try:
                    if _get_json:
                        _get_json(
                            f"/platform/tree/couple-relationships/{rel.id}/sources"
                        )
                except Exception:
                    pass

        if cache:
            cache.mark_loaded(fsid, sources=True)

    def _clear_fs_cache(self) -> None:
        """
        Clear disk + in-memory FS compare cache.
        (Used by the UI 'Clear cache' button.)
        """
        cache = self.__class__._cache
        if cache:
            cache.clear()
