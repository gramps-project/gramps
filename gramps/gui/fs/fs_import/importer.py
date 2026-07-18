#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026  Gabriel Rios
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
import json
import logging
import time
from typing import Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from gramps.gen.db import DbTxn
from gramps.gui.dialog import WarningDialog
from gramps.gui.utils import ProgressMeter

from . import _
from gramps.gen.fs import tree
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs.fs_import.sources import fetch_source_dates
from gramps.gen.fs.fs_import.places import add_place
from gramps.gen.fs.fs_import.importer import (
    FSToGrampsImporter as CoreFSToGrampsImporter,
)
from gramps.gen.fs import utils as fs_utilities

import gramps.gui.fs.person.fsg_sync as FSG_Sync
from gramps.gui.fs.utils.index import build_fs_index
from gramps.gen.fs.compare import compare_fs_to_gramps

LOG = logging.getLogger(__name__)

# Log (and print) any single person's comparison refresh that takes longer
# than this, to help pinpoint slow/stalled FamilySearch requests.
_SLOW_COMPARE_THRESHOLD_S = 1.0


def _pump_gtk_events() -> None:
    """
    Process pending GTK events.

    The bulk download phases block the main thread on network I/O in
    ThreadPoolExecutor batches, so without this the window manager sees an
    unresponsive main loop and offers to force-quit the app even though the
    download is progressing normally.
    """
    while Gtk.events_pending():
        Gtk.main_iteration()


class FSToGrampsImporter(CoreFSToGrampsImporter):
    """
    GUI wrapper around the core importer.

    Keeps progress meter, session bootstrap, UI busy cursor, signal management,
    compare refresh, and warning dialogs in the GUI layer.
    """

    def import_tree(self, caller, FSFTID):
        print("import ID :" + FSFTID)
        self.FS_ID = FSFTID
        self.dbstate = caller.dbstate

        active_handle = caller.uistate.get_active("Person")

        progress = ProgressMeter(
            _("FamilySearch Import"), _("Starting"), parent=caller.uistate.window
        )
        caller.uistate.set_busy_cursor(True)
        signals_disabled = False

        if self.refresh_signals:
            caller.dbstate.db.disable_signals()
            signals_disabled = True

        if not FSG_Sync.FSG_Sync.ensure_session(caller, self.verbosity):
            WarningDialog(_("Not connected to FamilySearch"))
            if signals_disabled:
                caller.dbstate.db.enable_signals()
            caller.uistate.set_busy_cursor(False)
            progress.close()
            if active_handle:
                caller.uistate.set_active(active_handle, "Person")
            return

        if not fs_utilities.FS_INDEX_PEOPLE:
            build_fs_index(caller, progress, 11)

        print("download")
        if self.fs_TreeImp:
            del self.fs_TreeImp
        self.fs_TreeImp = tree.Tree()

        if getattr(FSG_Sync.FSG_Sync, "fs_Tree", None) is None:
            FSG_Sync.FSG_Sync.fs_Tree = self.fs_TreeImp

        progress.set_pass(
            _("Downloading persons… (3/11)"), mode=ProgressMeter.MODE_ACTIVITY
        )
        print(_("Downloading person…"))
        if self.FS_ID:
            self.fs_TreeImp.add_persons(
                [self.FS_ID], progress_callback=_pump_gtk_events
            )
        else:
            if signals_disabled:
                caller.dbstate.db.enable_signals()
            caller.uistate.set_busy_cursor(False)
            progress.close()
            if active_handle:
                caller.uistate.set_active(active_handle, "Person")
            return

        # Each generation can involve fetching anywhere from a handful to
        # thousands of people, so a single progress.step() per generation
        # (the previous behavior) made the bar sit still for the entire
        # duration of a large generation's fetch. Use activity mode and
        # pulse/pump once per person actually fetched instead, via the
        # progress_callback Tree.add_parents/add_children/add_spouses
        # invoke for each completed network request.
        progress.set_pass(
            _("Downloading ancestors… (4/11)"), mode=ProgressMeter.MODE_ACTIVITY
        )
        todo = set(self.fs_TreeImp._persons.keys())
        done = set()
        for i in range(self.asc):
            if not todo:
                break
            done |= todo
            print(
                _(
                    "Downloading ancestor generation %(gen)d/%(total)d… (%(count)d people)"
                )
                % {"gen": i + 1, "total": self.asc, "count": len(todo)}
            )
            progress.set_header(
                _("Downloading ancestors… (4/11) — generation %(gen)d/%(total)d")
                % {"gen": i + 1, "total": self.asc}
            )
            todo = (
                self.fs_TreeImp.add_parents(set(todo), progress_callback=progress.step)
                - done
            )

        progress.set_pass(
            _("Downloading descendants… (5/11)"), mode=ProgressMeter.MODE_ACTIVITY
        )
        todo = set(self.fs_TreeImp._persons.keys())
        done = set()
        for i in range(self.desc):
            if not todo:
                break
            done |= todo
            print(
                _(
                    "Downloading descendant generation %(gen)d/%(total)d… (%(count)d people)"
                )
                % {"gen": i + 1, "total": self.desc, "count": len(todo)}
            )
            progress.set_header(
                _("Downloading descendants… (5/11) — generation %(gen)d/%(total)d")
                % {"gen": i + 1, "total": self.desc}
            )
            todo = (
                self.fs_TreeImp.add_children(set(todo), progress_callback=progress.step)
                - done
            )

        if self.include_spouses:
            progress.set_pass(
                _("Downloading spouses… (6/11)"), mode=ProgressMeter.MODE_ACTIVITY
            )
            todo = set(self.fs_TreeImp._persons.keys())
            print(_("Downloading spouses for %d people…") % len(todo))
            self.fs_TreeImp.add_spouses(set(todo), progress_callback=progress.step)

        if self.include_notes or self.include_sources:
            progress.set_pass(
                _("Downloading notes… (7/11)"),
                len(self.fs_TreeImp.persons) + len(self.fs_TreeImp.relationships),
            )
            print(_("Downloading notes and sources…"))

            def _fetch_raw(url_path: str) -> Any:
                sess = getattr(tree, "_fs_session", None)
                if sess is None:
                    return None

                fn = getattr(sess, "get_jsonurl", None) or getattr(
                    sess, "get_json", None
                )
                if not callable(fn):
                    return None

                return fn(url_path)

            fs_persons = list(self.fs_TreeImp.persons or [])
            fs_families = list(self.fs_TreeImp.relationships or [])
            total = len(fs_persons) + len(fs_families)

            # Group the URLs to fetch per person/family (for progress
            # reporting), but fetch all of them concurrently -- matching
            # the worker count Tree.add_persons already uses for the
            # ancestor/descendant/spouse phases. This was previously a
            # fully serial loop: 3 requests per person + 2 per couple,
            # one at a time, which was by far the slowest part of a bulk
            # import.
            work_items: list[list[str]] = [
                [
                    f"/platform/tree/persons/{fs_person.id}/notes",
                    f"/platform/tree/persons/{fs_person.id}/sources",
                    f"/platform/tree/persons/{fs_person.id}/memories",
                ]
                for fs_person in fs_persons
            ] + [
                [
                    f"/platform/tree/couple-relationships/{fs_family.id}/notes",
                    f"/platform/tree/couple-relationships/{fs_family.id}/sources",
                ]
                for fs_family in fs_families
            ]

            all_urls = [url for urls in work_items for url in urls]
            raw_payloads: dict[str, Any] = {}
            if all_urls:
                max_workers = min(8, len(all_urls))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(_fetch_raw, url): url for url in all_urls
                    }
                    for future in as_completed(futures):
                        url = futures[future]
                        try:
                            raw_payloads[url] = future.result()
                        except Exception as exc:
                            print(f"WARNING: failed to fetch {url}: {exc}")
                        _pump_gtk_events()

            # Deserializing mutates shared tree state, so do it sequentially
            # in the main thread even though the fetches above ran
            # concurrently.
            done = 0
            for urls in work_items:
                progress.step()
                for url in urls:
                    payload = raw_payloads.get(url)
                    if not payload:
                        continue
                    self._strip_unknowns(payload)
                    deserialize.deserialize_json(self.fs_TreeImp, payload)
                done += 1
                if done == 1 or done % 25 == 0 or done == total:
                    print(
                        _("  …notes/sources: %(done)d/%(total)d")
                        % {"done": done, "total": total}
                    )

            fetch_source_dates(self.fs_TreeImp)

        if self.verbosity >= 3:
            res = deserialize.to_string(self.fs_TreeImp)
            with open("import.out.json", "w", encoding="utf-8") as handle:
                json.dump(res, handle, indent=2)

        print(_("Importing…"))
        self.added_person = False

        existing_txn = caller.dbstate.db.transaction
        if existing_txn is not None:
            intr = True
            self.txn = existing_txn
        else:
            intr = False
            self.txn = DbTxn("FamilySearch import", caller.dbstate.db)
            caller.dbstate.db.transaction_begin(self.txn)

        progress.set_pass(_("Importing places… (8/11)"), len(self.fs_TreeImp.places))
        print(_("Importing places…"))
        for fs_place in list(self.fs_TreeImp.places or []):
            progress.step()
            add_place(caller.dbstate.db, self.txn, fs_place)

        progress.set_pass(_("Importing persons… (9/11)"), len(self.fs_TreeImp.persons))
        print(_("Importing persons…"))
        for fs_person in list(self.fs_TreeImp.persons or []):
            progress.step()
            self.add_person(caller.dbstate.db, self.txn, fs_person)

        progress.set_pass(
            _("Importing families… (10/11)"), len(self.fs_TreeImp.relationships)
        )
        print(_("Importing families…"))
        for fs_family in list(self.fs_TreeImp.relationships or []):
            progress.step()
            if fs_family.type == "http://gedcomx.org/Couple":
                self.add_family(fs_family)

        if self.import_cpr:
            progress.set_pass(
                _("Importing children… (11/11)"),
                len(getattr(self.fs_TreeImp, "childAndParentsRelationships", []) or []),
            )
            print(_("Importing children…"))
            for fs_cpr in list(
                getattr(self.fs_TreeImp, "childAndParentsRelationships", []) or []
            ):
                progress.step()
                self.add_child(fs_cpr)

            self._ensure_root_parent_link(self.FS_ID)
        else:
            progress.set_pass(_("Importing children… (11/11)"), 0)

        if not intr:
            caller.dbstate.db.transaction_commit(self.txn)
            del self.txn
        self.txn = None

        print("import done.")

        # Keep existing post-import compare refresh behavior in the GUI
        # layer, batched into a single transaction with signals suppressed.
        # Without this, compare_fs_to_gramps() opens its own DbTxn per
        # person, which for a large bulk import meant thousands of separate
        # commits, each firing a live GUI signal and growing the undo
        # history by one entry -- effectively O(N) commits/signals/undo
        # entries instead of one.
        #
        # This pass can be slow: compare_fs_to_gramps() may issue a
        # synchronous FamilySearch HEAD request per person if the person's
        # Last-Modified wasn't already captured during download. The
        # progress dialog is kept open (rather than closed before this
        # loop, as before) so progress.step() keeps pumping GTK events and
        # the app doesn't look hung while this runs.
        compare_people = list(self.fs_TreeImp.persons or [])
        progress.set_pass(
            _("Refreshing comparison status…"),
            len(compare_people) or 1,
        )
        print(_("Refreshing comparison status for %d people…") % len(compare_people))
        compare_start = time.monotonic()
        compared = 0
        failed = 0
        caller.dbstate.db.disable_signals()
        try:
            with DbTxn(
                "FamilySearch: refresh comparison status", caller.dbstate.db
            ) as compare_txn:
                for done, fs_person in enumerate(compare_people, start=1):
                    progress.step()
                    gr_handle = fs_utilities.FS_INDEX_PEOPLE.get(fs_person.id)
                    if not gr_handle:
                        continue
                    gr_person = caller.dbstate.db.get_person_from_handle(gr_handle)
                    if not gr_person:
                        continue

                    person_start = time.monotonic()
                    try:
                        compare_fs_to_gramps(
                            fs_person,
                            gr_person,
                            caller.dbstate.db,
                            None,
                            txn=compare_txn,
                        )
                        compared += 1
                    except Exception:
                        failed += 1
                        LOG.warning(
                            "Comparison refresh failed for FamilySearch id %s",
                            fs_person.id,
                            exc_info=True,
                        )

                    elapsed = time.monotonic() - person_start
                    if elapsed > _SLOW_COMPARE_THRESHOLD_S:
                        print(
                            _("  …comparison for %(fsid)s took %(elapsed).1fs")
                            % {"fsid": fs_person.id, "elapsed": elapsed}
                        )
                    if done == 1 or done % 25 == 0 or done == len(compare_people):
                        print(
                            _("  …comparison status: %(done)d/%(total)d")
                            % {"done": done, "total": len(compare_people)}
                        )
        except Exception:
            LOG.warning("Comparison refresh loop aborted early", exc_info=True)
        finally:
            caller.dbstate.db.enable_signals()

        print(
            _(
                "Comparison status refresh done in %(elapsed).1fs "
                "(%(compared)d compared, %(failed)d failed)"
            )
            % {
                "elapsed": time.monotonic() - compare_start,
                "compared": compared,
                "failed": failed,
            }
        )

        caller.uistate.set_busy_cursor(False)
        progress.close()

        if signals_disabled and self.added_person:
            caller.dbstate.db.request_rebuild()

        if active_handle:
            caller.uistate.set_active(active_handle, "Person")
