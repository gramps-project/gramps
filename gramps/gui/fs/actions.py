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
import os
from typing import Any

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk  # noqa: F401 (Gdk used in some UI flows)

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.fs import tags as fs_tags
from gramps.gen.fs import tree as fs_tree
from gramps.gen.lib import Family, Person, EventRef, EventRoleType, EventType
from gramps.gen.fs.actions import (
    _bind_global_session,
    _dbg,
    _ensure_child_in_family,
    _ensure_person_has_family_handle,
    _ensure_person_has_parent_family_handle,
    _ensure_status_schema,
    _family_other_parent_handle,
    _find_existing_family_for_parents,
    _find_person_by_fsid,
    _fs_display_name,
    _get_fs_id,
    _place_parent_in_family,
    _platform_json,
    _resolve_redirected_fsid,
    _set_fs_id,
    _strip_unknowns_inplace,
)
from gramps.gen.fs.compare import compare_fs_to_gramps
from gramps.gen.fs.fs_import.events import add_event
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs.fs_import.notes import add_note
import gramps.gen.fs.person.mixins.cache as cache_mod
from gramps.gui.dialog import ErrorDialog, OkDialog

from . import sync_directions
from . import ui as fs_ui
from .compare.window import CompareWindow
from .fs_import.importer import FSToGrampsImporter
from .person import fsg_sync as FSG_Sync

_ = glocale.translation.gettext


def _info(parent: Any, title: str, body: str) -> None:
    try:
        OkDialog(title, body, parent=parent)
        return
    except TypeError:
        try:
            OkDialog(title, body, parent)
            return
        except Exception:
            pass
    except Exception:
        pass

    try:
        fs_ui.info_dialog(parent, title, body)
    except Exception:
        dlg = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dlg.format_secondary_text(body)
        dlg.run()
        dlg.destroy()


def _error(parent: Any, title: str, body: str) -> None:
    try:
        ErrorDialog(title, body, parent=parent)
        return
    except TypeError:
        try:
            ErrorDialog(title, body, parent)
            return
        except Exception:
            pass
    except Exception:
        pass

    try:
        fs_ui.error_dialog(parent, title, body)
    except Exception:
        dlg = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dlg.format_secondary_text(body)
        dlg.run()
        dlg.destroy()


def _require_ready_person(dbstate, parent, person):
    db = dbstate.db
    handle = getattr(person, "get_handle", lambda: None)()
    if not handle or not getattr(db, "has_person_handle", lambda _h: True)(handle):
        _error(
            parent,
            _("FamilySearch"),
            _("Please save/commit this person to the database first, then try again."),
        )
        return None
    return handle


# ---------------
# Link/Compare
# ---------------


def link_familysearch_id(dbstate, uistate, track, person, session, parent, editor=None):
    _bind_global_session(session)
    edit_person = getattr(editor, "obj", None) if editor is not None else None
    target_person = edit_person or person

    dlg = Gtk.Dialog(title=_("Link FamilySearch ID"), transient_for=parent, modal=True)
    fs_ui.set_headerbar(dlg, _("Link FamilySearch ID"))
    dlg.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    dlg.add_button(_("OK"), Gtk.ResponseType.OK)

    box = dlg.get_content_area()
    box.set_spacing(8)
    box.set_border_width(10)

    lbl = Gtk.Label(label=_("Enter FamilySearch Person ID (e.g. GSVF-SGV):"))
    lbl.set_xalign(0.0)
    box.pack_start(lbl, False, False, 0)

    entry = Gtk.Entry()
    entry.set_text(_get_fs_id(target_person))
    box.pack_start(entry, False, False, 0)

    dlg.show_all()
    resp = dlg.run()
    if resp == Gtk.ResponseType.OK:
        _set_fs_id(target_person, entry.get_text())

        if editor is not None and hasattr(editor, "attr_list"):
            try:
                editor.attr_list.data = target_person.get_attribute_list()
                editor.attr_list.rebuild_callback()
            except Exception:
                pass

    dlg.destroy()


def compare_person(dbstate, uistate, track, person, session, parent, editor=None):
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked.\nClick 'Link FamilySearch ID' first."),
        )
        return

    _ensure_status_schema(dbstate.db)

    try:
        CompareWindow(
            dbstate,
            uistate,
            track,
            person,
            fsid=fsid,
            session=session,
            parent=parent,
            editor=editor,
        )
    except TypeError:
        CompareWindow(dbstate, uistate, track, person, fsid, session, parent)


# --------------------------
# Relatives chooser dialog
# --------------------------


def _pick_fsid_list(parent, title: str, rows: list[tuple[str, str, bool]]) -> list[str]:
    """
    rows: [(fsid, label, exists)]
    returns selected fsids
    """
    dlg = Gtk.Dialog(title=title, transient_for=parent, flags=0)
    dlg.get_style_context().add_class("fs-rel-import-dialog")
    fs_ui.set_headerbar(dlg, title)

    dlg.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    dlg.add_button(_("Import selected"), Gtk.ResponseType.OK)

    box = dlg.get_content_area()
    box.get_style_context().add_class("fs-rel-import-wrap")
    box.set_spacing(10)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)

    store = Gtk.ListStore(bool, str, str, bool)
    existing_ct = 0
    for fsid, label, exists in rows:
        if exists:
            existing_ct += 1
        store.append([not exists, label, fsid, bool(exists)])

    total = len(rows)
    new_ct = total - existing_ct

    top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    top.get_style_context().add_class("fs-rel-import-panel")

    lbl_counts = Gtk.Label(
        label=_("{total} found - {new} new - {existing} already in tree").format(
            total=total, new=new_ct, existing=existing_ct
        )
    )
    lbl_counts.set_xalign(0.0)
    top.pack_start(lbl_counts, True, True, 0)

    btn_none = Gtk.Button(label=_("Select none"))
    btn_new = Gtk.Button(label=_("Select all new"))

    def do_none(_btn):
        for row in store:
            row[0] = False

    def do_new(_btn):
        for row in store:
            row[0] = not row[3]

    btn_none.connect("clicked", do_none)
    btn_new.connect("clicked", do_new)

    top.pack_end(btn_new, False, False, 0)
    top.pack_end(btn_none, False, False, 0)

    tv = Gtk.TreeView(model=store)
    tv.get_style_context().add_class("fs-rel-import-treeview")
    fs_ui.tune_treeview(tv)

    cr_toggle = Gtk.CellRendererToggle()
    cr_toggle.connect(
        "toggled", lambda _w, path: store[path].__setitem__(0, not store[path][0])
    )
    col_toggle = Gtk.TreeViewColumn(_("Import"), cr_toggle, active=0)
    tv.append_column(col_toggle)

    cr_text = Gtk.CellRendererText()
    col_label = Gtk.TreeViewColumn(_("Person"), cr_text, text=1)

    def _label_cell_func(_col, cell, model, itr, _data=None):
        try:
            exists = bool(model.get_value(itr, 3))
        except Exception:
            exists = False

        if exists:
            fs_ui.set_cell_bg(cell, "green")
        else:
            fs_ui.clear_cell_bg(cell)

    col_label.set_cell_data_func(cr_text, _label_cell_func)
    tv.append_column(col_label)

    box.add(top)
    box.add(
        fs_ui.build_legend_row(
            [("green", _("Already in tree")), ("gray", _("New (will import)"))],
            hint=_("Tip: uncheck anything you don't want to import."),
            wrap_class="fs-rel-import-legend",
        )
    )
    box.add(fs_ui.wrap_scroller(tv, min_h=320))

    dlg.show_all()
    resp = dlg.run()
    chosen: list[str] = []
    if resp == Gtk.ResponseType.OK:
        chosen = [row[2] for row in store if row[0] and row[2]]
    dlg.destroy()
    return chosen


# ------------------------
# Import pipeline wrapper
# ------------------------


def _import_full_person(dbstate, uistate, fsid: str, verbosity: int = 0) -> None:
    _ensure_status_schema(dbstate.db)

    class _Caller:
        def __init__(self, dbstate, uistate):
            self.dbstate = dbstate
            self.uistate = uistate

    caller = _Caller(dbstate, uistate)

    importer = FSToGrampsImporter()
    importer.noreimport = False
    importer.asc = 0
    importer.desc = 0
    importer.include_spouses = False
    importer.include_notes = False
    importer.include_sources = False
    importer.refresh_signals = False
    importer.verbosity = verbosity
    importer.import_cpr = False  # avoid double relationship creation

    importer.import_tree(caller, fsid)


# ---------------------------------------
# Import: Parents / Children / Spouses
# ---------------------------------------


def import_parents(dbstate, uistate, track, person, session, parent, editor=None):
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return
    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    _ensure_status_schema(dbstate.db)

    try:
        data = _platform_json(session, f"/platform/tree/persons/{fsid}/parents")
    except Exception as err:
        _error(
            parent,
            _("FamilySearch"),
            _("Failed to fetch parents: {e}").format(e=err),
        )
        return

    persons = {p.get("id"): p for p in (data.get("persons") or []) if p.get("id")}
    caprs = data.get("childAndParentsRelationships") or []

    parent_ids: list[str] = []
    for rel in caprs:
        child = (rel.get("child") or {}).get("resourceId")
        if child != fsid:
            continue
        p1 = (rel.get("parent1") or {}).get("resourceId")
        p2 = (rel.get("parent2") or {}).get("resourceId")
        for pid in (p1, p2):
            if pid and pid != fsid and pid not in parent_ids:
                parent_ids.append(pid)

    if not parent_ids:
        _info(
            parent,
            _("FamilySearch"),
            _("No parents found on FamilySearch for this person."),
        )
        return

    db = dbstate.db
    rows = []
    for pid in parent_ids:
        nm = _fs_display_name(persons.get(pid, {}) or {}) or pid
        exists = _find_person_by_fsid(db, pid) is not None
        label = f"{nm} [{pid}]" + (_("  - already in tree") if exists else "")
        rows.append((pid, label, exists))

    chosen = _pick_fsid_list(parent, _("Import parents"), rows)
    if not chosen:
        return

    imported_parents: list[Person] = []
    for pid in chosen:
        _import_full_person(dbstate, uistate, pid, verbosity=0)
        pr = _find_person_by_fsid(db, pid)
        if pr:
            imported_parents.append(pr)

    if not imported_parents:
        _error(
            parent,
            _("FamilySearch"),
            _("Parents imported but could not be located in the local database."),
        )
        return

    with DbTxn(_("FamilySearch: Link parents"), db) as txn:
        child = db.get_person_from_handle(me_handle)

        fam = None
        fam_handle = None

        if not (child.get_parent_family_handle_list() or []):
            parent_handles = set(
                p.handle
                for p in imported_parents
                if p is not None and getattr(p, "handle", None)
            )
            if len(parent_handles) >= 2:
                fam = _find_existing_family_for_parents(db, parent_handles)
                if fam:
                    fam_handle = fam.handle
                    _ensure_person_has_parent_family_handle(db, txn, child, fam_handle)

        if fam is None:
            for fh in child.get_parent_family_handle_list() or []:
                f = db.get_family_from_handle(fh)
                if not f:
                    continue
                if (not f.get_father_handle()) or (not f.get_mother_handle()):
                    fam = f
                    fam_handle = fh
                    break

        if fam is None:
            fam = Family()
            db.add_family(fam, txn)
            fam_handle = fam.get_handle()
            _ensure_person_has_parent_family_handle(db, txn, child, fam_handle)

        if _ensure_child_in_family(db, fam, child.handle):
            db.commit_family(fam, txn)

        for p in imported_parents:
            _place_parent_in_family(db, fam, p.handle)
            _ensure_person_has_family_handle(db, txn, p, fam_handle)

        db.commit_family(fam, txn)

    if editor is not None and hasattr(editor, "_update_families"):
        try:
            editor._update_families()
        except Exception:
            pass

    _info(parent, _("FamilySearch"), _("Parent(s) imported and linked."))


def import_children(dbstate, uistate, track, person, session, parent, editor=None):
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return
    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    _ensure_status_schema(dbstate.db)

    try:
        data = _platform_json(session, f"/platform/tree/persons/{fsid}/children")
    except Exception as err:
        _error(
            parent,
            _("FamilySearch"),
            _("Failed to fetch children: {e}").format(e=err),
        )
        return

    persons = {p.get("id"): p for p in (data.get("persons") or []) if p.get("id")}
    caprs = data.get("childAndParentsRelationships") or []

    child_map: dict[str, str | None] = {}
    for rel in caprs:
        child = (rel.get("child") or {}).get("resourceId")
        p1 = (rel.get("parent1") or {}).get("resourceId")
        p2 = (rel.get("parent2") or {}).get("resourceId")
        if not child:
            continue
        if p1 == fsid:
            child_map[child] = p2 if p2 and p2 != fsid else None
        elif p2 == fsid:
            child_map[child] = p1 if p1 and p1 != fsid else None

    child_ids = [cid for cid in child_map.keys() if cid and cid != fsid]
    if not child_ids:
        _info(
            parent,
            _("FamilySearch"),
            _("No children found on FamilySearch for this person."),
        )
        return

    db = dbstate.db
    rows = []
    for cid in sorted(set(child_ids)):
        cn = _fs_display_name(persons.get(cid, {}) or {}) or cid
        other = child_map.get(cid)
        other_label = ""
        if other:
            other_name = _fs_display_name(persons.get(other, {}) or {}) or other
            other_label = _(" (other parent: {name})").format(name=other_name)
        exists = _find_person_by_fsid(db, cid) is not None
        label = f"{cn}{other_label} [{cid}]" + (
            _("  - already in tree") if exists else ""
        )
        rows.append((cid, label, exists))

    chosen = _pick_fsid_list(parent, _("Import children"), rows)
    if not chosen:
        return

    imported_children: list[Person] = []
    for cid in chosen:
        _import_full_person(dbstate, uistate, cid, verbosity=0)
        ch = _find_person_by_fsid(db, cid)
        if ch:
            imported_children.append(ch)

    if not imported_children:
        _error(
            parent,
            _("FamilySearch"),
            _("Children imported but could not be located in the local database."),
        )
        return

    with DbTxn(_("FamilySearch: Link children"), db) as txn:
        me = db.get_person_from_handle(me_handle)

        my_fams: list[Family] = []
        for fh in me.get_family_handle_list() or []:
            f = db.get_family_from_handle(fh)
            if f:
                my_fams.append(f)

        for ch in imported_children:
            other_parent_fsid = None
            for cid in chosen:
                p = _find_person_by_fsid(db, cid)
                if p and p.handle == ch.handle:
                    other_parent_fsid = child_map.get(cid)
                    break

            other_parent = (
                _find_person_by_fsid(db, other_parent_fsid)
                if other_parent_fsid
                else None
            )

            fam = None
            if other_parent:
                for f in my_fams:
                    if _family_other_parent_handle(f, me.handle) == other_parent.handle:
                        fam = f
                        break

            if fam is None:
                for f in my_fams:
                    if not _family_other_parent_handle(f, me.handle):
                        fam = f
                        break

            if fam is None:
                fam = Family()
                if me.get_gender() == Person.MALE:
                    fam.set_father_handle(me.handle)
                elif me.get_gender() == Person.FEMALE:
                    fam.set_mother_handle(me.handle)
                else:
                    fam.set_father_handle(me.handle)
                db.add_family(fam, txn)
                db.commit_family(fam, txn)
                my_fams.append(fam)
                _ensure_person_has_family_handle(db, txn, me, fam.handle)

            if other_parent:
                _place_parent_in_family(db, fam, other_parent.handle)
                _ensure_person_has_family_handle(db, txn, other_parent, fam.handle)

            if _ensure_child_in_family(db, fam, ch.handle):
                db.commit_family(fam, txn)
            _ensure_person_has_parent_family_handle(db, txn, ch, fam.handle)

    if editor is not None and hasattr(editor, "_update_families"):
        try:
            editor._update_families()
        except Exception:
            pass

    _info(parent, _("FamilySearch"), _("Child(ren) imported and linked."))


def import_spouse(dbstate, uistate, track, person, session, parent, editor=None):
    return import_spouses(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def import_spouses(dbstate, uistate, track, person, session, parent, editor=None):
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return
    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    _ensure_status_schema(dbstate.db)

    try:
        data = _platform_json(session, f"/platform/tree/persons/{fsid}/spouses")
    except Exception as err:
        _error(
            parent,
            _("FamilySearch"),
            _("Failed to fetch spouses: {e}").format(e=err),
        )
        return

    persons = {p.get("id"): p for p in (data.get("persons") or []) if p.get("id")}
    rels = data.get("relationships") or []
    caprs = data.get("childAndParentsRelationships") or []

    spouse_ids: set[str] = set()

    for rel in rels:
        p1 = (rel.get("person1") or {}).get("resourceId")
        p2 = (rel.get("person2") or {}).get("resourceId")
        if p1 == fsid and p2:
            spouse_ids.add(p2)
        elif p2 == fsid and p1:
            spouse_ids.add(p1)

    for rel in caprs:
        p1 = (rel.get("parent1") or {}).get("resourceId")
        p2 = (rel.get("parent2") or {}).get("resourceId")
        if p1 == fsid and p2:
            spouse_ids.add(p2)
        elif p2 == fsid and p1:
            spouse_ids.add(p1)

    spouse_ids.discard(fsid)
    if not spouse_ids:
        _info(
            parent,
            _("FamilySearch"),
            _("No spouses found on FamilySearch for this person."),
        )
        return

    db = dbstate.db
    rows = []
    for sid in sorted(spouse_ids):
        nm = _fs_display_name(persons.get(sid, {}) or {}) or sid
        exists = _find_person_by_fsid(db, sid) is not None
        label = f"{nm} [{sid}]" + (_("  - already in tree") if exists else "")
        rows.append((sid, label, exists))

    chosen = _pick_fsid_list(parent, _("Import spouse(s)"), rows)
    if not chosen:
        return

    imported_spouses: list[Person] = []
    for sid in chosen:
        _import_full_person(dbstate, uistate, sid, verbosity=0)
        sp = _find_person_by_fsid(db, sid)
        if sp:
            imported_spouses.append(sp)

    if not imported_spouses:
        _error(
            parent,
            _("FamilySearch"),
            _("Spouses imported but could not be located in the local database."),
        )
        return

    with DbTxn(_("FamilySearch: Link spouses"), db) as txn:
        me = db.get_person_from_handle(me_handle)

        my_fams: list[Family] = []
        for fh in me.get_family_handle_list() or []:
            f = db.get_family_from_handle(fh)
            if f:
                my_fams.append(f)

        for sp in imported_spouses:
            fam = None
            for f in my_fams:
                other = _family_other_parent_handle(f, me.handle)
                if other == sp.handle:
                    fam = f
                    break

            if fam is None:
                for f in my_fams:
                    if not _family_other_parent_handle(f, me.handle):
                        fam = f
                        break

            if fam is None:
                fam = Family()
                if me.get_gender() == Person.MALE:
                    fam.set_father_handle(me.handle)
                elif me.get_gender() == Person.FEMALE:
                    fam.set_mother_handle(me.handle)
                else:
                    fam.set_father_handle(me.handle)
                db.add_family(fam, txn)
                db.commit_family(fam, txn)
                my_fams.append(fam)

            _place_parent_in_family(db, fam, sp.handle)
            db.commit_family(fam, txn)

            _ensure_person_has_family_handle(db, txn, me, fam.handle)
            _ensure_person_has_family_handle(db, txn, sp, fam.handle)

    if editor is not None and hasattr(editor, "_update_families"):
        try:
            editor._update_families()
        except Exception:
            pass

    _info(parent, _("FamilySearch"), _("Spouse(s) imported and linked."))


def import_parent_family(dbstate, uistate, track, person, session, parent, editor=None):
    return import_parents(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def import_family_parents(
    dbstate, uistate, track, person, session, parent, editor=None
):
    return import_parents(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def import_child(dbstate, uistate, track, person, session, parent, editor=None):
    return import_children(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def import_family_children(
    dbstate, uistate, track, person, session, parent, editor=None
):
    return import_children(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def import_partner(dbstate, uistate, track, person, session, parent, editor=None):
    return import_spouses(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


# -------------------------------------
# clear json cache, tags, sync Person
# -------------------------------------


def clear_cache(dbstate, uistate, track, person, session, parent, editor=None) -> None:
    _bind_global_session(session)

    cleared_indexes = 0
    cleared_disk = False
    disk_path = ""

    try:
        for _name, obj in list(vars(deserialize).items()):
            idx = getattr(obj, "_index", None)
            if isinstance(idx, dict):
                idx.clear()
                cleared_indexes += 1
    except Exception as err:
        _dbg(f"clear_cache: gedcomx index clear failed: {err}")

    try:
        try:
            fs_tree._fs_session = session
        except Exception:
            pass

        new_tree: Any = fs_tree.Tree()
        try:
            setattr(new_tree, "_getsources", False)
        except Exception:
            pass

        setattr(FSG_Sync.FSG_Sync, "fs_Tree", new_tree)
    except Exception as err:
        _dbg(f"clear_cache: fs_Tree reset failed: {err}")

    try:
        cache_dir = os.path.dirname(cache_mod.__file__)
        disk_path = cache_dir
        FsCache = getattr(cache_mod, "_FsCache", None)
        if FsCache:
            cache = FsCache(cache_dir)
            for meth in ("clear", "clear_all", "purge", "wipe", "reset"):
                fn = getattr(cache, meth, None)
                if callable(fn):
                    fn()
                    cleared_disk = True
                    break
    except Exception as err:
        _dbg(f"clear_cache: disk cache clear failed: {err}")

    msg = []
    msg.append(_("Cleared GEDCOMX in-memory indices: {n}").format(n=cleared_indexes))
    msg.append(_("Reset shared FS Tree cache: yes"))
    if cleared_disk:
        msg.append(_("Cleared on-disk cache: yes ({path})").format(path=disk_path))
    else:
        msg.append(
            _("Cleared on-disk cache: (not available / not supported by cache helper)")
        )

    _info(parent, _("FamilySearch"), "\n".join(msg))


def tags_dialog(dbstate, uistate, track, person, session, parent, editor=None) -> None:
    _bind_global_session(session)

    dlg = Gtk.Dialog(title=_("FamilySearch Tags"), transient_for=parent, flags=0)
    fs_ui.set_headerbar(dlg, _("FamilySearch Tags"))
    dlg.add_button(_("Close"), Gtk.ResponseType.CLOSE)
    dlg.add_button(_("Retag all (Linked/NotLinked)"), Gtk.ResponseType.OK)

    box = dlg.get_content_area()
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)
    box.set_spacing(8)

    box.add(
        Gtk.Label(
            label=_(
                "This will scan your whole tree and apply FS_Linked / FS_NotLinked tags.\n"
                "It does NOT change any person data."
            )
        )
    )

    dlg.show_all()
    resp = dlg.run()
    dlg.destroy()

    if resp != Gtk.ResponseType.OK:
        return

    try:
        db = dbstate.db
        total, linked, not_linked, changed = fs_tags.retag_all_link_status(db)
        _info(
            parent,
            _("FamilySearch"),
            _(
                "Retag complete.\n\n"
                "Total persons: {total}\n"
                "Linked: {linked}\n"
                "Not linked: {not_linked}\n"
                "Changed: {changed}"
            ).format(
                total=total, linked=linked, not_linked=not_linked, changed=changed
            ),
        )
    except Exception as err:
        _error(parent, _("FamilySearch"), _("Retag failed: {e}").format(e=err))


def _refresh_editor_person_views(editor) -> None:
    if editor is None:
        return

    for name in (
        "_update_events",
        "_update_event_list",
        "_update_notebook",
        "_update_notes",
        "_update_facts",
        "_update_families",
        "update",
        "reload",
    ):
        fn = getattr(editor, name, None)
        if callable(fn):
            try:
                fn()
                return
            except Exception:
                pass


def sync_this_person(
    dbstate, uistate, track, person, session, parent, editor=None
) -> None:
    # Sync the *selected existing Gramps person* from FamilySearch - facts/events (dates + place) + notes
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return

    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    db = dbstate.db
    _ensure_status_schema(db)

    fsid2 = _resolve_redirected_fsid(session, fsid)
    if fsid2 and fsid2 != fsid:
        try:
            with DbTxn(_("FamilySearch: Update FSID after redirect"), db) as txn:
                gr = db.get_person_from_handle(me_handle)
                _set_fs_id(gr, fsid2)
                db.commit_person(gr, txn)
            fsid = fsid2
        except Exception:
            fsid = fsid2

    try:
        tmp = fs_tree.Tree()
        try:
            tmp._getsources = False
        except Exception:
            pass

        tmp.add_persons([fsid])

        notes_json = _platform_json(session, f"/platform/tree/persons/{fsid}/notes")
        _strip_unknowns_inplace(notes_json)
        try:
            deserialize.deserialize_json(tmp, notes_json)
        except Exception:
            pass

        fs_person = None
        try:
            fs_person = getattr(tmp, "_persons", {}).get(fsid)
        except Exception:
            fs_person = None

        if fs_person is None:
            try:
                for p in list(getattr(tmp, "persons", []) or []):
                    if getattr(p, "id", None) == fsid:
                        fs_person = p
                        break
            except Exception:
                pass

        if fs_person is None:
            _error(
                parent,
                _("FamilySearch"),
                _(
                    "Could not load this person from FamilySearch (no GEDCOMX person object)."
                ),
            )
            return

    except Exception as e:
        _error(
            parent,
            _("FamilySearch"),
            _("Failed to download from FamilySearch: {e}").format(e=e),
        )
        return

    try:
        with DbTxn(_("FamilySearch: Sync this person"), db) as txn:
            gr_person = db.get_person_from_handle(me_handle)

            for fs_fact in list(getattr(fs_person, "facts", []) or []):
                ev = add_event(db, txn, fs_fact, gr_person)
                if not ev or not getattr(ev, "handle", None):
                    continue

                already = False
                for _er in list(gr_person.get_event_ref_list() or []):
                    try:
                        if getattr(_er, "ref", None) == ev.handle:
                            already = True
                            link_er = _er
                            break
                    except Exception:
                        continue
                else:
                    link_er = None

                if not already:
                    link_er = EventRef()
                    link_er.set_role(EventRoleType.PRIMARY)
                    link_er.set_reference_handle(ev.get_handle())
                    try:
                        db.commit_event(ev, txn)
                    except Exception:
                        pass
                    gr_person.add_event_ref(link_er)

                try:
                    ev_type = int(ev.type) if hasattr(ev.type, "__int__") else ev.type
                    if ev_type == EventType.BIRTH:
                        gr_person.set_birth_ref(link_er)
                    elif ev_type == EventType.DEATH:
                        gr_person.set_death_ref(link_er)
                except Exception:
                    pass

                db.commit_person(gr_person, txn)

            existing_notes = set(gr_person.get_note_list() or [])
            for fs_note in list(getattr(fs_person, "notes", []) or []):
                note = add_note(db, txn, fs_note, gr_person.note_list)
                if (
                    note
                    and getattr(note, "handle", None)
                    and note.handle not in existing_notes
                ):
                    gr_person.add_note(note.handle)
                    existing_notes.add(note.handle)

            try:
                compare_fs_to_gramps(fs_person, gr_person, db, None)
            except Exception:
                pass

            db.commit_person(gr_person, txn)

    except Exception as e:
        _error(parent, _("FamilySearch"), _("Sync failed: {e}").format(e=e))
        return

    _refresh_editor_person_views(editor)
    _info(
        parent,
        _("FamilySearch"),
        _(
            "Sync complete: facts/events, dates/places, and notes updated for this person."
        ),
    )


def sync_person(dbstate, uistate, track, person, session, parent, editor=None):
    return sync_this_person(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


# --------------------------
# sync to FS
# --------------------------


def sync_from_familysearch(
    dbstate, uistate, track, person, session, parent, editor=None
) -> None:
    return sync_this_person(
        dbstate, uistate, track, person, session, parent, editor=editor
    )


def export_basic_to_familysearch(
    dbstate, uistate, track, person, session, parent, editor=None
) -> None:
    """
    Create missing people on FamilySearch (basic) and link relationships.
    This is the Gramps -> FamilySearch "create" path.
    """
    _bind_global_session(session)

    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    try:
        sync_directions.export_basic_people_to_familysearch(
            dbstate, uistate, track, person, session, parent, editor=editor
        )
    except Exception as err:
        _error(
            parent,
            _("FamilySearch"),
            _("Export to FamilySearch failed: {e}").format(e=err),
        )


def sync_to_familysearch(
    dbstate, uistate, track, person, session, parent, editor=None
) -> None:
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return

    me_handle = _require_ready_person(dbstate, parent, person)
    if not me_handle:
        return

    try:
        sync_directions.sync_to_familysearch(
            dbstate, uistate, track, person, session, parent, editor=editor
        )
    except Exception as err:
        _error(
            parent,
            _("FamilySearch"),
            _("Sync to FamilySearch failed: {e}").format(e=err),
        )
