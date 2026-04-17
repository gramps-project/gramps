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

import json

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

        if self.refresh_signals:
            caller.dbstate.db.disable_signals()

        if not FSG_Sync.FSG_Sync.ensure_session(caller, self.verbosity):
            WarningDialog(_("Not connected to FamilySearch"))
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
            self.fs_TreeImp.add_persons([self.FS_ID])
        else:
            caller.uistate.set_busy_cursor(False)
            progress.close()
            if active_handle:
                caller.uistate.set_active(active_handle, "Person")
            return

        progress.set_pass(_("Downloading ancestors… (4/11)"), self.asc)
        todo = set(self.fs_TreeImp._persons.keys())
        done = set()
        for i in range(self.asc):
            progress.step()
            if not todo:
                break
            done |= todo
            print(_("Downloading %d generations of ancestors…") % (i + 1))
            todo = self.fs_TreeImp.add_parents(set(todo)) - done

        progress.set_pass(_("Downloading descendants… (5/11)"), self.desc)
        todo = set(self.fs_TreeImp._persons.keys())
        done = set()
        for i in range(self.desc):
            progress.step()
            if not todo:
                break
            done |= todo
            print(_("Downloading %d generations of descendants…") % (i + 1))
            todo = self.fs_TreeImp.add_children(set(todo)) - done

        if self.include_spouses:
            progress.set_pass(
                _("Downloading spouses… (6/11)"), mode=ProgressMeter.MODE_ACTIVITY
            )
            print(_("Downloading spouses…"))
            todo = set(self.fs_TreeImp._persons.keys())
            self.fs_TreeImp.add_spouses(set(todo))

        if self.include_notes or self.include_sources:
            progress.set_pass(
                _("Downloading notes… (7/11)"),
                len(self.fs_TreeImp.persons) + len(self.fs_TreeImp.relationships),
            )
            print(_("Downloading notes and sources…"))

            def _fetch_into_tree(url_path: str) -> None:
                sess = getattr(tree, "_fs_session", None)
                if sess is None:
                    return

                fn = getattr(sess, "get_jsonurl", None) or getattr(
                    sess, "get_json", None
                )
                if not callable(fn):
                    return

                payload = fn(url_path)
                self._strip_unknowns(payload)
                deserialize.deserialize_json(self.fs_TreeImp, payload)

            def _load_person_extras(person_id: str) -> None:
                _fetch_into_tree(f"/platform/tree/persons/{person_id}/notes")
                _fetch_into_tree(f"/platform/tree/persons/{person_id}/sources")
                _fetch_into_tree(f"/platform/tree/persons/{person_id}/memories")

            def _load_couple_extras(rel_id: str) -> None:
                _fetch_into_tree(f"/platform/tree/couple-relationships/{rel_id}/notes")
                _fetch_into_tree(
                    f"/platform/tree/couple-relationships/{rel_id}/sources"
                )

            for fs_person in list(self.fs_TreeImp.persons or []):
                progress.step()
                _load_person_extras(fs_person.id)

            for fs_family in list(self.fs_TreeImp.relationships or []):
                progress.step()
                _load_couple_extras(fs_family.id)

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
        caller.uistate.set_busy_cursor(False)
        progress.close()

        if self.refresh_signals:
            caller.dbstate.db.enable_signals()
            if self.added_person:
                caller.dbstate.db.request_rebuild()

        # keep existing post-import compare refresh behavior in GUI layer
        try:
            for fs_person in list(self.fs_TreeImp.persons or []):
                gr_handle = fs_utilities.FS_INDEX_PEOPLE.get(fs_person.id)
                if not gr_handle:
                    continue
                gr_person = caller.dbstate.db.get_person_from_handle(gr_handle)
                if gr_person:
                    compare_fs_to_gramps(fs_person, gr_person, caller.dbstate.db, None)
        except Exception:
            pass

        if active_handle:
            caller.uistate.set_active(active_handle, "Person")
