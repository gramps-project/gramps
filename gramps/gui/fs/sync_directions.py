# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# Push rules:
# - Default is always keep FamilySearch.
# - No deletions.
# - Only overwrite an existing FS conclusion when we have its FS conclusion id.
# - Notes: create new notes, update existing FS notes by note id, never delete.
# - Sources: create new SourceDescriptions, then attach them as Person SourceReferences.
#
# Export rules:
# - Create new FS people when the Gramps person has no usable FSID.
# - Basic export only: primary name + birth/death facts when available.
# - Optionally do the same for parents, spouse, and children.
# - Then create relationships.
# - Write created FSIDs back into Gramps through _FSFTID.

"""
gtk-side helpers for pushing changes to FamilySearch and doing the basic export
the core payload/build/api work lives in gen.fs.sync_directions.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.fs import tree as fs_tree_mod
from gramps.gen.lib import Attribute, AttributeType, Person
from gramps.gui.dialog import WarningDialog
from gramps.gui.listmodel import COLOR, NOSORT, TOGGLE, ListModel

from gramps.gen.fs import sync_directions as fs_sync_core
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs.compare import compare_fs_to_gramps
import gramps.gen.fs.fs_import as fs_import_mod
import gramps.gui.fs.person.fsg_sync as fsg_sync

_ = glocale.translation.gettext


COL_PROP = 1
COL_GR_DATE = 2
COL_GR_VAL = 3
COL_FS_DATE = 4
COL_FS_VAL = 5
COL_XTYPE = 8
COL_XGR_ID = 9
COL_XFS_ID = 10
COL_XGR2 = 11
COL_XFS2 = 12


def _bind_global_session(session: Any) -> None:
    """Mirror the active session onto the shared fs tree module."""
    setattr(fs_tree_mod, "_fs_session", session)


def _ensure_fs_tree(session: Any) -> Optional[Any]:
    """Return the shared FS tree object used by the compare/sync UI."""
    _bind_global_session(session)

    existing_tree: Optional[Any] = getattr(fsg_sync.FSG_Sync, "fs_Tree", None)
    if existing_tree is not None:
        return existing_tree

    new_tree: Any = fs_tree_mod.Tree()
    try:
        setattr(new_tree, "_getsources", False)
    except Exception:
        pass

    fsg_sync.FSG_Sync.fs_Tree = new_tree
    return new_tree


def _prime_person_cache(session: Any, fsid: str, force: bool = False) -> Optional[Any]:
    """Load one FS person into the shared tree cache, optionally forcing refresh."""
    fsid = (fsid or "").strip()
    if not fsid:
        return None

    tree_obj = _ensure_fs_tree(session)
    if tree_obj is None:
        return None

    if force:
        idx = getattr(deserialize.Person, "_index", None)
        if isinstance(idx, dict):
            idx.pop(fsid, None)

        for attr_name in ("_persons", "persons", "_person", "_people"):
            cache = getattr(tree_obj, attr_name, None)
            if isinstance(cache, dict):
                cache.pop(fsid, None)

    add_persons = getattr(tree_obj, "add_persons", None)
    if callable(add_persons):
        try:
            add_persons({fsid})
            return tree_obj
        except TypeError:
            try:
                add_persons([fsid])
                return tree_obj
            except Exception:
                pass
        except Exception:
            pass

    for method_name in ("add_person", "add_persons"):
        method = getattr(tree_obj, method_name, None)
        if not callable(method):
            continue
        try:
            method(fsid)
            return tree_obj
        except Exception:
            continue

    return tree_obj


def _unwrap_tree_model(model: Any) -> Optional[Any]:
    """peel until real gtk tree model"""
    if model is None:
        return None

    def looks_like_tree_model(obj: Any) -> bool:
        return (
            obj is not None
            and callable(getattr(obj, "get_iter_first", None))
            and callable(getattr(obj, "get_value", None))
            and callable(getattr(obj, "iter_children", None))
            and callable(getattr(obj, "iter_next", None))
        )

    if looks_like_tree_model(model):
        return model

    for attr_name in ("model", "_model", "store", "treestore", "liststore"):
        raw = getattr(model, attr_name, None)
        if looks_like_tree_model(raw):
            return raw

    for attr_name in ("treeview", "_treeview", "widget", "view"):
        treeview = getattr(model, attr_name, None)
        if treeview is None or not callable(getattr(treeview, "get_model", None)):
            continue
        try:
            raw = treeview.get_model()
        except Exception:
            raw = None
        if looks_like_tree_model(raw):
            return raw

    return None


def _walk(model: Any) -> Iterable[Any]:
    """walk over the compare tree rows."""
    raw = _unwrap_tree_model(model)
    if raw is None:
        return

    try:
        current = raw.get_iter_first()
    except Exception:
        return

    stack = [current] if current else []
    while stack:
        current = stack.pop()
        yield current

        try:
            child = raw.iter_children(current)
        except Exception:
            child = None

        children = []
        while child:
            children.append(child)
            try:
                child = raw.iter_next(child)
            except Exception:
                child = None

        for entry in reversed(children):
            stack.append(entry)


def _debug_dump_compare_model(model: Any) -> None:
    """dump compare rows to stdout when FS debug mode is on"""
    if not fs_sync_core._debug_enabled():
        return

    raw = _unwrap_tree_model(model)
    if raw is None:
        print("[FS SYNC] compare model dump: could not unwrap model")
        return

    print("[FS SYNC] ----- compare model dump begin -----")
    index = 0

    for row_iter in _walk(raw):
        try:
            row = {
                "xtype": str(raw.get_value(row_iter, COL_XTYPE) or ""),
                "prop": str(raw.get_value(row_iter, COL_PROP) or ""),
                "gr_date": str(raw.get_value(row_iter, COL_GR_DATE) or ""),
                "gr_val": str(raw.get_value(row_iter, COL_GR_VAL) or ""),
                "fs_date": str(raw.get_value(row_iter, COL_FS_DATE) or ""),
                "fs_val": str(raw.get_value(row_iter, COL_FS_VAL) or ""),
                "xgr": str(raw.get_value(row_iter, COL_XGR_ID) or ""),
                "xfs": str(raw.get_value(row_iter, COL_XFS_ID) or ""),
                "xgr2": str(raw.get_value(row_iter, COL_XGR2) or ""),
                "xfs2": str(raw.get_value(row_iter, COL_XFS2) or ""),
            }
        except Exception as err:
            print(f"[FS SYNC] row {index} <error reading row: {err}>")
            index += 1
            continue

        print(
            "[FS SYNC] row %d xtype=%r prop=%r gr_date=%r gr_val=%r fs_date=%r fs_val=%r xgr=%r xfs=%r xgr2=%r xfs2=%r"
            % (
                index,
                row["xtype"],
                row["prop"],
                row["gr_date"],
                row["gr_val"],
                row["fs_date"],
                row["fs_val"],
                row["xgr"],
                row["xfs"],
                row["xgr2"],
                row["xfs2"],
            )
        )
        index += 1

    print("[FS SYNC] ----- compare model dump end -----")


def _make_overview_model() -> ListModel:
    """Build the temporary compare model used for the overview prompt."""
    treeview = Gtk.TreeView()
    titles = [
        (" ", 1, 18, COLOR),
        (_("Property"), 2, 180),
        (_("Gramps date"), 3, 115),
        (_("Gramps value"), 4, 420),
        (_("FS date"), 5, 115),
        (_("FamilySearch value"), 6, 420),
        (" ", NOSORT, 1),
        ("x", 8, 5, TOGGLE, True, lambda *_a, **_k: None),
        (_("xType"), NOSORT, 0),
        (_("xGr"), NOSORT, 0),
        (_("xFs"), NOSORT, 0),
        (_("xGr2"), NOSORT, 0),
        (_("xFs2"), NOSORT, 0),
    ]
    return ListModel(treeview, titles, list_mode="tree")


def _collect_overview_push_items(model: Any) -> List[Dict[str, Any]]:
    """Turn the compare model rows into pushable name/fact items."""
    raw = _unwrap_tree_model(model)
    if raw is None:
        return []

    items: List[Dict[str, Any]] = []

    def norm(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip()).lower()

    for row_iter in _walk(raw):
        try:
            x_type_raw = str(raw.get_value(row_iter, COL_XTYPE) or "").strip()
        except Exception:
            x_type_raw = ""

        x_type = x_type_raw.lower()
        label = str(raw.get_value(row_iter, COL_PROP) or "")
        label_norm = norm(label)

        gr_date = str(raw.get_value(row_iter, COL_GR_DATE) or "")
        gr_val = str(raw.get_value(row_iter, COL_GR_VAL) or "")
        fs_date = str(raw.get_value(row_iter, COL_FS_DATE) or "")
        fs_val = str(raw.get_value(row_iter, COL_FS_VAL) or "")
        xfs_id = str(raw.get_value(row_iter, COL_XFS_ID) or "").strip()

        is_name_row = x_type in (
            "primary_name",
            "name",
            "preferred_name",
            "primary name",
        ) or label_norm in ("name", "preferred name", "primary name")

        fact_type = fs_sync_core._fact_type_from_label(label)
        is_fact_row = x_type in ("fact", "event", "events") or bool(fact_type)

        # name rows are handled separately from fact rows.
        if is_name_row:
            if not gr_val.strip():
                continue
            if gr_val.strip() == fs_val.strip():
                continue

            items.append(
                {
                    "kind": "primary_name",
                    "label": label or _("Primary Name"),
                    "fs_id": xfs_id,
                    "gr_val": gr_val,
                    "fs_val": fs_val,
                    "gr_surname": str(raw.get_value(row_iter, COL_XGR2) or "").strip(),
                    "gr_given": str(raw.get_value(row_iter, COL_XFS2) or "").strip(),
                    "create": not bool(xfs_id),
                }
            )
            continue

        if is_fact_row:
            if not (gr_date.strip() or gr_val.strip()):
                continue
            if gr_date.strip() == fs_date.strip() and gr_val.strip() == fs_val.strip():
                continue

            items.append(
                {
                    "kind": "fact",
                    "label": label,
                    "fs_id": xfs_id,
                    "gr_date": gr_date,
                    "gr_val": gr_val,
                    "fs_date": fs_date,
                    "fs_val": fs_val,
                    "fact_type": fact_type,
                    "create": not bool(xfs_id),
                }
            )

    return items


def _collect_note_push_items(
    dbstate: Any, person: Any, session: Any, fsid: str
) -> List[Dict[str, Any]]:
    """Compare Gramps notes to FS notes and build create/update items."""
    _prime_person_cache(session, fsid)

    fs_notes = fs_sync_core._load_fs_person_notes(session, fsid)
    remaining = list(fs_notes)

    def take_matching(note_id: str, subject: str) -> Optional[Any]:
        if note_id:
            for note in remaining:
                if getattr(note, "id", None) == note_id:
                    remaining.remove(note)
                    return note

        if subject:
            for note in remaining:
                if (getattr(note, "subject", None) or "") == subject:
                    remaining.remove(note)
                    return note

        return None

    items: List[Dict[str, Any]] = []

    note_handles = list(person.get_note_list() or [])
    for handle in note_handles:
        gr_note = dbstate.db.get_note_from_handle(handle)
        if not gr_note:
            continue

        gr_subject = fs_sync_core._gramps_note_title(gr_note)
        gr_text = fs_sync_core._normalize_note_text(
            getattr(gr_note, "get", lambda: "")() or ""
        )
        note_id = fs_sync_core._extract_gramps_note_fsid(gr_note)

        fs_match = take_matching(note_id, gr_subject)
        if fs_match is None:
            if not (gr_subject.strip() or gr_text.strip()):
                continue

            items.append(
                {
                    "kind": "note_create",
                    "label": _("Note: {title}").format(
                        title=gr_subject or _("(untitled)")
                    ),
                    "fs_id": "",
                    "fs_val": _("(missing)"),
                    "gr_val": gr_text or _("(empty)"),
                    "gr_subject": gr_subject,
                    "gr_text": gr_text,
                }
            )
            continue

        fs_subject = getattr(fs_match, "subject", "") or ""
        fs_text = fs_sync_core._normalize_note_text(getattr(fs_match, "text", "") or "")
        fs_id = (getattr(fs_match, "id", "") or "").strip()

        if (
            fs_sync_core._normalize_note_text(gr_text)
            == fs_sync_core._normalize_note_text(fs_text)
            and gr_subject == fs_subject
        ):
            continue

        items.append(
            {
                "kind": "note_update",
                "label": _("Note: {title}").format(
                    title=gr_subject or fs_subject or _("(untitled)")
                ),
                "fs_id": fs_id,
                "fs_val": fs_text or _("(empty)"),
                "gr_val": gr_text or _("(empty)"),
                "gr_subject": gr_subject or fs_subject,
                "gr_text": gr_text,
                "fs_subject": fs_subject,
                "fs_text": fs_text,
            }
        )

    return items


def _collect_source_push_items(
    dbstate: Any, person: Any, session: Any, person_fsid: str
) -> List[Dict[str, Any]]:
    """Collect citations that still need source work on FamilySearch."""
    items: List[Dict[str, Any]] = []

    fs_import = fs_import_mod

    attached_person_sdids: Optional[Set[str]] = None
    if session is not None and person_fsid:
        attached_person_sdids = (
            fs_sync_core._load_attached_person_source_description_ids(
                session, person_fsid
            )
        )

    citation_handles: Set[str] = set()
    citation_scope: Dict[str, str] = {}

    for handle in list(person.get_citation_list() or []):
        citation_handles.add(handle)
        citation_scope.setdefault(handle, "person")

    for event_ref in list(person.get_event_ref_list() or []):
        event = dbstate.db.get_event_from_handle(event_ref.ref)
        if not event:
            continue
        for handle in list(event.get_citation_list() or []):
            citation_handles.add(handle)
            citation_scope.setdefault(handle, "event")

    for family_handle in list(person.get_family_handle_list() or []):
        family = dbstate.db.get_family_from_handle(family_handle)
        if not family:
            continue

        for handle in list(family.get_citation_list() or []):
            citation_handles.add(handle)
            citation_scope.setdefault(handle, "family")

        for event_ref in list(family.get_event_ref_list() or []):
            event = dbstate.db.get_event_from_handle(event_ref.ref)
            if not event:
                continue
            for handle in list(event.get_citation_list() or []):
                citation_handles.add(handle)
                citation_scope.setdefault(handle, "family_event")

    for citation_handle in sorted(citation_handles):
        citation = dbstate.db.get_citation_from_handle(citation_handle)
        if not citation:
            continue

        scope = citation_scope.get(citation_handle, "person")
        raw_sd_id = (fs_utilities.get_fsftid(citation) or "").strip()

        resolved_sd_id = raw_sd_id
        sd_state = "missing"
        is_attached_to_person: Optional[bool] = None

        if raw_sd_id:
            if session is not None:
                resolved_sd_id, sd_state = (
                    fs_sync_core._resolve_active_source_description(session, raw_sd_id)
                )
            else:
                sd_state = "unknown"

            if scope == "person" and attached_person_sdids is not None:
                is_attached_to_person = bool(
                    (raw_sd_id and raw_sd_id in attached_person_sdids)
                    or (resolved_sd_id and resolved_sd_id in attached_person_sdids)
                )

            if (
                scope == "person"
                and is_attached_to_person is True
                and sd_state == "merged"
                and resolved_sd_id
                and resolved_sd_id != raw_sd_id
            ):
                link_fn = getattr(fs_utilities, "link_gramps_fs_id", None)
                if callable(link_fn):
                    try:
                        link_fn(dbstate.db, citation, resolved_sd_id)
                    except Exception:
                        pass

            # person-level source refs can already exist even if the citation still
            # points at an older merged id locally.
            if scope == "person":
                if is_attached_to_person is True and sd_state in ("ok", "merged"):
                    continue

                if is_attached_to_person is None and sd_state in (
                    "ok",
                    "merged",
                    "unknown",
                ):
                    continue
            else:
                if sd_state in ("ok", "merged", "unknown"):
                    continue

        title = ""
        note_text = ""
        url = ""
        date = ""

        if fs_import is not None and hasattr(fs_import, "IntermediateSource"):
            try:
                source_model = getattr(fs_import, "IntermediateSource")()
                source_model.from_gramps(dbstate.db, citation)
                title = (getattr(source_model, "citation_title", "") or "").strip()
                note_text = (getattr(source_model, "note_text", "") or "").strip()
                url = (getattr(source_model, "url", "") or "").strip()
                date = str(getattr(source_model, "date", "") or "").strip()
            except Exception:
                pass

        if not title:
            title = (getattr(citation, "page", "") or "").strip()
        if not title:
            title = _("Source from Gramps")

        lines = [title]
        if url:
            lines.append(url)
        if date:
            lines.append(date)
        if note_text:
            lines.append(note_text)

        if raw_sd_id and sd_state == "deleted":
            fs_val = _("(deleted on FamilySearch)")
        elif raw_sd_id and sd_state == "missing":
            fs_val = _("(missing on FamilySearch)")
        elif scope == "person" and raw_sd_id and is_attached_to_person is False:
            fs_val = _("(not attached to this person on FamilySearch)")
        else:
            fs_val = _("(missing)")

        items.append(
            {
                "kind": "source_create",
                "label": _("Source: {title}").format(title=title),
                "fs_val": fs_val,
                "gr_val": "\n".join([entry for entry in lines if entry]),
                "citation_handle": citation_handle,
                "title": title,
                "url": url,
                "note_text": note_text,
                "date": date,
                "old_fs_id": raw_sd_id,
                "fs_state": sd_state,
                "scope": scope,
            }
        )

    return items


def _prompt(
    parent: Gtk.Window, items: List[Dict[str, Any]]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Show the sync picker and return the change message + chosen items."""
    dialog = Gtk.Dialog(title=_("Sync to FamilySearch"), transient_for=parent, flags=0)
    dialog.set_modal(True)
    dialog.set_default_size(820, 620)
    dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    dialog.add_button(_("Apply Selected"), Gtk.ResponseType.OK)
    dialog.set_default_response(Gtk.ResponseType.OK)

    box = dialog.get_content_area()
    box.set_border_width(10)
    box.set_spacing(8)

    intro = Gtk.Label()
    intro.set_xalign(0.0)
    intro.set_line_wrap(True)
    intro.set_markup(
        _(
            "<b>Choose what to change on FamilySearch</b>\n"
            "Default is to keep FamilySearch.\n"
            "<i>No deletions are performed.</i>"
        )
    )
    box.pack_start(intro, False, False, 0)

    message_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    message_row.pack_start(Gtk.Label(label=_("Change message:")), False, False, 0)

    change_entry = Gtk.Entry()
    change_entry.set_hexpand(True)
    change_entry.set_text(_("Updated from Gramps"))
    message_row.pack_start(change_entry, True, True, 0)
    box.pack_start(message_row, False, False, 0)

    button_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    select_all = Gtk.Button(label=_("Select all"))
    select_none = Gtk.Button(label=_("Select none"))
    button_row.pack_start(select_all, False, False, 0)
    button_row.pack_start(select_none, False, False, 0)
    button_row.set_halign(Gtk.Align.START)
    box.pack_start(button_row, False, False, 0)

    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.set_hexpand(True)
    scroll.set_vexpand(True)
    box.pack_start(scroll, True, True, 0)

    grid = Gtk.Grid()
    grid.set_column_spacing(12)
    grid.set_row_spacing(10)
    grid.set_border_width(4)
    scroll.add(grid)

    headings = [
        Gtk.Label(label=_("Field")),
        Gtk.Label(label=_("FamilySearch")),
        Gtk.Label(label=_("Gramps")),
        Gtk.Label(label=_("Action")),
    ]
    for heading in headings:
        heading.set_xalign(0.0)
        try:
            heading.get_style_context().add_class("heading")
        except Exception:
            pass

    grid.attach(headings[0], 0, 0, 1, 1)
    grid.attach(headings[1], 1, 0, 1, 1)
    grid.attach(headings[2], 2, 0, 1, 1)
    grid.attach(headings[3], 3, 0, 1, 1)

    combos: List[Gtk.ComboBoxText] = []
    effective_items: List[Dict[str, Any]] = []

    def fmt(value: str) -> str:
        text = (value or "").strip()
        return text if text else _("(empty)")

    row = 1
    for item in items:
        kind = item.get("kind", "")

        field_label = Gtk.Label(label=str(item.get("label") or ""))
        field_label.set_xalign(0.0)
        field_label.set_line_wrap(True)

        fs_label = Gtk.Label(label=fmt(str(item.get("fs_val") or "")))
        fs_label.set_xalign(0.0)
        fs_label.set_line_wrap(True)

        gr_label = Gtk.Label(label=fmt(str(item.get("gr_val") or "")))
        gr_label.set_xalign(0.0)
        gr_label.set_line_wrap(True)

        combo = Gtk.ComboBoxText()
        combo.append_text(_("Keep FamilySearch"))

        if kind in ("primary_name", "fact", "note_update"):
            combo.append_text(_("Overwrite with Gramps"))
        elif kind in ("note_create", "source_create", "memory_create"):
            combo.append_text(_("Add from Gramps"))
        else:
            combo.append_text(_("Apply from Gramps"))

        combo.set_active(0)

        grid.attach(field_label, 0, row, 1, 1)
        grid.attach(fs_label, 1, row, 1, 1)
        grid.attach(gr_label, 2, row, 1, 1)
        grid.attach(combo, 3, row, 1, 1)

        combos.append(combo)
        effective_items.append(item)
        row += 1

    def set_all(apply_changes: bool) -> None:
        index = 1 if apply_changes else 0
        for combo in combos:
            combo.set_active(index)

    select_all.connect("clicked", lambda *_: set_all(True))
    select_none.connect("clicked", lambda *_: set_all(False))

    dialog.show_all()
    response = dialog.run()

    change_message = (change_entry.get_text() or "").strip()
    chosen: List[Dict[str, Any]] = []

    if response == Gtk.ResponseType.OK:
        for item, combo in zip(effective_items, combos):
            if combo.get_active() == 1:
                chosen.append(item)

    dialog.destroy()
    return change_message, chosen


def sync_to_familysearch(
    dbstate: Any,
    uistate: Any,
    track: Any,
    person: Any,
    session: Any,
    parent: Any,
    editor: Any = None,
) -> None:
    try:
        if not (
            getattr(session, "logged", False)
            or getattr(session, "access_token", None)
            or getattr(session, "connected", False)
        ):
            WarningDialog(_("Not connected to FamilySearch."), parent=parent)
            return

        handle = fs_sync_core._person_handle(person)
        if handle:
            db_person = dbstate.db.get_person_from_handle(handle)
            if db_person is not None:
                person = db_person

        fsid_raw = fs_utilities.get_fsftid(person)
        if not fsid_raw:
            WarningDialog(
                _("No FamilySearch Person ID is set for this person."), parent=parent
            )
            return

        resolved_fsid, fs_state = fs_sync_core._resolve_active_person(session, fsid_raw)

        if fs_state == "deleted":
            WarningDialog(
                _(
                    "This linked FamilySearch person is deleted/inactive.\n\n"
                    "Clear or replace the saved FSID before exporting again, "
                    "or restore that FamilySearch person first."
                ),
                parent=parent,
            )
            return

        if fs_state == "missing":
            WarningDialog(
                _(
                    "This linked FamilySearch person could not be found.\n\n"
                    "Clear or replace the saved FSID before exporting again."
                ),
                parent=parent,
            )
            return

        fsid = resolved_fsid or fsid_raw

        if fs_state == "merged" and fsid and fsid != fsid_raw:
            with DbTxn(_("FamilySearch: Refresh merged ID"), dbstate.db) as txn:
                fs_sync_core._get_or_set_person_fsid(dbstate.db, txn, person, fsid)

            if handle:
                db_person = dbstate.db.get_person_from_handle(handle)
                if db_person is not None:
                    person = db_person

        _bind_global_session(session)
        _prime_person_cache(session, fsid, force=True)

        fs_person = deserialize.Person.index.get(fsid)
        if fs_person is None:
            WarningDialog(
                _(
                    "FamilySearch person could not be loaded fresh from the API.\n"
                    "Try 'Sync from FamilySearch' or clear the cache, then try again."
                ),
                parent=parent,
            )
            return

        # start with names/facts from the compare view, then add notes/sources/memories.
        compare_model = _make_overview_model()
        compare_fs_to_gramps(
            fs_person,
            person,
            dbstate.db,
            model=compare_model,
            dupdoc=True,
        )
        _debug_dump_compare_model(compare_model)
        overview_items = _collect_overview_push_items(compare_model)

        if fs_sync_core._debug_enabled():
            print(f"[FS SYNC] overview_items={overview_items!r}")

        note_items = _collect_note_push_items(dbstate, person, session, fsid)
        source_items = _collect_source_push_items(dbstate, person, session, fsid)
        memory_items = fs_sync_core._collect_memory_push_items(dbstate, person)

        all_items = overview_items + note_items + source_items + memory_items
        if not all_items:
            WarningDialog(_("No pushable differences found."), parent=parent)
            return

        change_message, chosen = _prompt(parent, all_items)
        if not chosen:
            return

        chosen_overview = [
            item for item in chosen if item.get("kind") in ("primary_name", "fact")
        ]
        chosen_notes = [
            item
            for item in chosen
            if item.get("kind") in ("note_create", "note_update")
        ]
        chosen_sources = [
            item for item in chosen if item.get("kind") == "source_create"
        ]
        chosen_memories = [
            item for item in chosen if item.get("kind") == "memory_create"
        ]

        if chosen_overview:
            payload = fs_sync_core._build_person_payload(
                fsid, chosen_overview, change_message
            )
            person_payload = (
                (payload.get("persons") or [])[0] if payload.get("persons") else {}
            )

            if not person_payload or (
                len(person_payload.keys()) <= 1 and "id" in person_payload
            ):
                WarningDialog(
                    _(
                        "Differences were found, but none could be converted into a valid "
                        "FamilySearch payload. This usually means the fact type could not be determined."
                    ),
                    parent=parent,
                )
                return

            fsid_head, head_resp = fs_sync_core._head_person(session, fsid)
            if fsid_head and fsid_head != fsid:
                fsid = fsid_head
                payload = fs_sync_core._build_person_payload(
                    fsid, chosen_overview, change_message
                )

            # use concurrency headers when we have them
            person_headers: Dict[str, str] = {}
            if head_resp is not None:
                response_headers = fs_sync_core._response_headers(head_resp)
                etag = str(
                    response_headers.get("Etag") or response_headers.get("ETag") or ""
                ).strip()
                last_modified = str(response_headers.get("Last-Modified") or "").strip()

                if etag:
                    person_headers["If-Match"] = etag
                if last_modified:
                    person_headers["If-Unmodified-Since"] = last_modified

            resp = fs_sync_core._session_post_json(
                session,
                f"/platform/tree/persons/{fsid}",
                payload,
                headers=person_headers,
            )
            if resp is None or fs_sync_core._response_status(resp) not in (
                200,
                201,
                204,
            ):
                message = fs_sync_core._err_text(resp) if resp is not None else ""
                WarningDialog(
                    _("FamilySearch update failed (names/facts).")
                    + (("\n" + message) if message else ""),
                    parent=parent,
                )
                return

            _prime_person_cache(session, fsid, force=True)

        if chosen_notes:
            notes_payload = fs_sync_core._build_notes_payload(
                fsid, chosen_notes, change_message
            )
            if notes_payload:
                resp = fs_sync_core._session_post_json(
                    session, f"/platform/tree/persons/{fsid}/notes", notes_payload
                )
                if resp is None or fs_sync_core._response_status(resp) not in (
                    200,
                    201,
                    204,
                ):
                    message = fs_sync_core._err_text(resp) if resp is not None else ""
                    WarningDialog(
                        _("FamilySearch update failed (notes).")
                        + (("\n" + message) if message else ""),
                        parent=parent,
                    )
                    return

        if chosen_sources:
            created_refs: List[Dict[str, Any]] = []
            default_tags = ["http://gedcomx.org/Name"]

            for item in chosen_sources:
                citation_handle = item.get("citation_handle")
                if not citation_handle:
                    continue

                citation = dbstate.db.get_citation_from_handle(citation_handle)
                if not citation:
                    continue

                title = str(item.get("title") or _("Source from Gramps"))
                url = str(item.get("url") or "")
                note_text = str(item.get("note_text") or "")
                date = str(item.get("date") or "")

                citation_text = title
                if date:
                    citation_text += f" ({date})"
                if note_text:
                    citation_text += "\n" + note_text

                sdid = fs_sync_core._create_source_description(
                    session, title, citation_text, url, change_message
                )
                if not sdid:
                    WarningDialog(
                        _("FamilySearch source creation failed for: {t}").format(
                            t=title
                        ),
                        parent=parent,
                    )
                    return

                created_refs.append(
                    fs_sync_core._build_source_ref(
                        session, sdid, default_tags, change_message
                    )
                )

                link_fn = getattr(fs_utilities, "link_gramps_fs_id", None)
                if callable(link_fn):
                    try:
                        link_fn(dbstate.db, citation, sdid)
                    except Exception:
                        pass

            if created_refs:
                fsid_head, head_resp = fs_sync_core._head_person(session, fsid)
                if fsid_head and fsid_head != fsid:
                    fsid = fsid_head

                source_headers: Dict[str, str] = {}
                if head_resp is not None:
                    response_headers = fs_sync_core._response_headers(head_resp)
                    etag = str(
                        response_headers.get("Etag")
                        or response_headers.get("ETag")
                        or ""
                    ).strip()
                    last_modified = str(
                        response_headers.get("Last-Modified") or ""
                    ).strip()

                    if etag:
                        source_headers["If-Match"] = etag
                    if last_modified:
                        source_headers["If-Unmodified-Since"] = last_modified

                payload = fs_sync_core._build_person_sources_payload(
                    session, fsid, created_refs, change_message
                )
                resp = fs_sync_core._session_post_json(
                    session,
                    f"/platform/tree/persons/{fsid}",
                    payload,
                    headers=source_headers,
                )
                if resp is None or fs_sync_core._response_status(resp) not in (
                    200,
                    201,
                    204,
                ):
                    message = fs_sync_core._err_text(resp) if resp is not None else ""
                    WarningDialog(
                        _("FamilySearch update failed (sources).")
                        + (("\n" + message) if message else ""),
                        parent=parent,
                    )
                    return

        if chosen_memories:
            try:
                person_name = str(name_displayer.display(person) or "").strip()
            except Exception:
                person_name = ""

            uploaded: List[Tuple[str, str]] = []
            memory_errors: List[str] = []

            for item in chosen_memories:
                file_path = str(item.get("file_path") or "").strip()
                media_handle = str(item.get("media_handle") or "").strip()
                if not media_handle or not file_path:
                    continue

                mem_id, _mem_ref_id, err = fs_sync_core._upload_person_memory(
                    session,
                    fsid,
                    file_path,
                    title=str(item.get("title") or "").strip(),
                    description=str(item.get("description") or "").strip(),
                    filename=str(item.get("filename") or "").strip(),
                    person_name=person_name,
                    artifact_type=str(item.get("artifact_type") or "").strip(),
                )

                if not mem_id:
                    memory_errors.append(
                        f"{os.path.basename(file_path) or '(file)'}: {err or 'upload failed'}"
                    )
                    continue

                uploaded.append((media_handle, mem_id))

            if uploaded:
                db = dbstate.db

                with DbTxn(_("FamilySearch: Link uploaded memories"), db) as txn:
                    for media_handle, mem_id in uploaded:
                        media_obj = None

                        for getter_name in (
                            "get_media_from_handle",
                            "get_media_object_from_handle",
                        ):
                            getter = getattr(db, getter_name, None)
                            if not callable(getter):
                                continue
                            media_obj = getter(media_handle)
                            if media_obj:
                                break

                        if not media_obj:
                            continue

                        link_fn = getattr(fs_utilities, "link_gramps_fs_id", None)
                        if callable(link_fn):
                            try:
                                link_fn(db, media_obj, mem_id)
                                continue
                            except Exception:
                                pass

                        attrs = list(media_obj.get_attribute_list() or [])

                        kept: List[Any] = []
                        for attr in attrs:
                            try:
                                attr_type = str(attr.get_type())
                            except Exception:
                                attr_type = ""

                            if attr_type in ("_FSFTID", "_FSTID", "FamilySearch ID"):
                                continue
                            kept.append(attr)

                        fs_attr = Attribute()
                        fs_attr.set_type(AttributeType("_FSFTID"))
                        fs_attr.set_value(mem_id)
                        kept.append(fs_attr)

                        media_obj.set_attribute_list(kept)

                        for commit_name in (
                            "commit_media_object",
                            "commit_media",
                            "commit_object",
                        ):
                            commit = getattr(db, commit_name, None)
                            if not callable(commit):
                                continue
                            try:
                                commit(media_obj, txn)
                                break
                            except Exception:
                                continue

            if memory_errors:
                WarningDialog(
                    _("Some memories failed to upload:\n\n%s")
                    % "\n".join(memory_errors[:12]),
                    parent=parent,
                )

        _prime_person_cache(session, fsid, force=True)
        WarningDialog(_("FamilySearch updated successfully."), parent=parent)

    except Exception as err:
        WarningDialog(
            _("FamilySearch sync failed: {e}").format(e=str(err)),
            parent=parent,
        )


def _export_picker_dialog(
    parent: Gtk.Window, db: Any, me: Person, session: Any
) -> Optional[Tuple[bool, bool, bool, List[str]]]:
    """Show export picker for the main person + close relatives."""
    parents, spouses, children, _families = fs_sync_core._collect_relatives(db, me)

    dialog = Gtk.Dialog(
        title=_("Export to FamilySearch (basic)"), transient_for=parent, flags=0
    )
    dialog.set_modal(True)
    dialog.set_default_size(760, 520)
    dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    dialog.add_button(_("Export"), Gtk.ResponseType.OK)
    dialog.set_default_response(Gtk.ResponseType.OK)

    box = dialog.get_content_area()
    box.set_border_width(10)
    box.set_spacing(8)

    info = Gtk.Label()
    info.set_xalign(0.0)
    info.set_line_wrap(True)
    info.set_markup(
        _(
            "<b>Create missing people on FamilySearch and link relationships.</b>\n"
            "Basic export only: name + birth/death facts.\n"
            "<i>No deletions. Existing active linked people are not overwritten here.</i>"
        )
    )
    box.pack_start(info, False, False, 0)

    chk_parents = Gtk.CheckButton(label=_("Include parents"))
    chk_spouses = Gtk.CheckButton(label=_("Include spouse(s)"))
    chk_children = Gtk.CheckButton(label=_("Include children"))

    chk_parents.set_active(True)
    chk_spouses.set_active(True)
    chk_children.set_active(True)

    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    row.pack_start(chk_parents, False, False, 0)
    row.pack_start(chk_spouses, False, False, 0)
    row.pack_start(chk_children, False, False, 0)
    box.pack_start(row, False, False, 0)

    box.pack_start(
        Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0
    )

    store = Gtk.ListStore(bool, str, str, bool)

    def display_label(prefix: str, person_obj: Any) -> Tuple[str, bool]:
        try:
            name = str(name_displayer.display(person_obj) or "")
        except Exception:
            name = _("(person)")

        raw_fsid = (fs_utilities.get_fsftid(person_obj) or "").strip()
        if not raw_fsid:
            return f"{prefix}{name}", False

        resolved, state = fs_sync_core._resolve_active_person(session, raw_fsid)

        if state == "ok":
            return f"{prefix}{name}  [{raw_fsid}]", True
        if state == "merged":
            return f"{prefix}{name}  [{raw_fsid} ? {resolved or raw_fsid}]", True
        if state == "deleted":
            return f"{prefix}{name}  [{raw_fsid}; deleted on FamilySearch]", False
        if state == "missing":
            return f"{prefix}{name}  [{raw_fsid}; not found on FamilySearch]", False

        return f"{prefix}{name}  [{raw_fsid}; status unknown]", True

    me_label, me_has_active = display_label(_("This person: "), me)
    store.append([not me_has_active, me_label, me.handle, me_has_active])

    def add_handles(title: str, handles: List[str]) -> None:
        for handle in handles:
            person_obj = db.get_person_from_handle(handle)
            if not person_obj:
                continue

            label, has_active = display_label(f"{title}: ", person_obj)
            store.append([not has_active, label, handle, has_active])

    add_handles(_("Parent"), parents)
    add_handles(_("Spouse"), spouses)
    add_handles(_("Child"), children)

    treeview = Gtk.TreeView(model=store)
    try:
        treeview.set_headers_visible(True)
        treeview.set_rules_hint(True)
    except Exception:
        pass

    toggle_renderer = Gtk.CellRendererToggle()
    toggle_renderer.connect(
        "toggled",
        lambda _w, path: store[path].__setitem__(0, not store[path][0]),
    )
    treeview.append_column(Gtk.TreeViewColumn(_("Create"), toggle_renderer, active=0))

    text_renderer = Gtk.CellRendererText()
    treeview.append_column(Gtk.TreeViewColumn(_("Person"), text_renderer, text=1))

    button_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_missing = Gtk.Button(label=_("Select all missing"))
    btn_none = Gtk.Button(label=_("Select none"))

    def select_missing(_button: Any) -> None:
        for row_data in store:
            row_data[0] = not bool(row_data[3])

    def select_none(_button: Any) -> None:
        for row_data in store:
            row_data[0] = False

    btn_missing.connect("clicked", select_missing)
    btn_none.connect("clicked", select_none)
    button_row.pack_start(btn_missing, False, False, 0)
    button_row.pack_start(btn_none, False, False, 0)
    box.pack_start(button_row, False, False, 0)

    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.set_hexpand(True)
    scroll.set_vexpand(True)
    scroll.add(treeview)
    box.pack_start(scroll, True, True, 0)

    dialog.show_all()
    response = dialog.run()

    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        return None

    do_parents = bool(chk_parents.get_active())
    do_spouses = bool(chk_spouses.get_active())
    do_children = bool(chk_children.get_active())

    chosen: List[str] = []
    for row_data in store:
        if bool(row_data[0]) and isinstance(row_data[2], str) and row_data[2]:
            chosen.append(row_data[2])

    dialog.destroy()
    return do_parents, do_spouses, do_children, chosen


def export_basic_people_to_familysearch(
    dbstate: Any,
    uistate: Any,
    track: Any,
    person: Any,
    session: Any,
    parent: Any,
    editor: Any = None,
) -> None:
    """create missing FS people and then try to wire up the relationships."""
    try:
        if not (
            getattr(session, "logged", False)
            or getattr(session, "access_token", None)
            or getattr(session, "connected", False)
        ):
            WarningDialog(_("Not connected to FamilySearch."), parent=parent)
            return

        db = dbstate.db
        me_handle = fs_sync_core._person_handle(person)

        if not me_handle:
            WarningDialog(_("Please save this person first."), parent=parent)
            return

        me = db.get_person_from_handle(me_handle)
        if not me:
            WarningDialog(
                _("Could not resolve this person from the database."), parent=parent
            )
            return

        _bind_global_session(session)

        picked = _export_picker_dialog(parent, db, me, session)
        if picked is None:
            return

        do_parents, do_spouses, do_children, create_handles = picked

        handle_to_fsid: Dict[str, str] = {}
        parents, spouses, children, family_handles = fs_sync_core._collect_relatives(
            db, me
        )
        change_message = _("Created from Gramps")

        def seed(handle: str, txn: Any) -> None:
            person_obj = db.get_person_from_handle(handle)
            if not person_obj:
                return

            raw_fsid = (fs_utilities.get_fsftid(person_obj) or "").strip()
            if not raw_fsid:
                return

            resolved_fsid, state = fs_sync_core._resolve_active_person(
                session, raw_fsid
            )
            if state in ("ok", "merged") and resolved_fsid:
                handle_to_fsid[handle] = resolved_fsid
                if state == "merged" and resolved_fsid != raw_fsid:
                    fs_sync_core._get_or_set_person_fsid(
                        db, txn, person_obj, resolved_fsid
                    )

        created_any = False
        attempted_relationships = False

        # first create or refresh ids, then do relationships after the txn closes.
        with DbTxn(_("FamilySearch: Export basic people"), db) as txn:
            seed(me.handle, txn)

            if do_parents:
                for handle in parents:
                    seed(handle, txn)

            if do_spouses:
                for handle in spouses:
                    seed(handle, txn)

            if do_children:
                for handle in children:
                    seed(handle, txn)

            for handle in create_handles:
                person_obj = db.get_person_from_handle(handle)
                if not person_obj:
                    continue

                raw_fsid = (fs_utilities.get_fsftid(person_obj) or "").strip()
                if raw_fsid:
                    resolved_fsid, state = fs_sync_core._resolve_active_person(
                        session, raw_fsid
                    )
                    if state in ("ok", "merged") and resolved_fsid:
                        handle_to_fsid[handle] = resolved_fsid
                        if state == "merged" and resolved_fsid != raw_fsid:
                            fs_sync_core._get_or_set_person_fsid(
                                db, txn, person_obj, resolved_fsid
                            )
                        continue

                fsid_new = fs_sync_core._fs_create_person_basic(
                    session, db, person_obj, change_message
                )
                if not fsid_new:
                    WarningDialog(
                        _(
                            "FamilySearch create failed for a person. Check name and connection."
                        ),
                        parent=parent,
                    )
                    return

                created_any = True
                handle_to_fsid[handle] = fsid_new
                fs_sync_core._get_or_set_person_fsid(db, txn, person_obj, fsid_new)

        me = db.get_person_from_handle(me_handle)
        raw_me_fsid = (fs_utilities.get_fsftid(me) or "").strip()

        me_fsid = ""
        if raw_me_fsid:
            resolved_me_fsid, me_state = fs_sync_core._resolve_active_person(
                session, raw_me_fsid
            )
            if me_state in ("ok", "merged") and resolved_me_fsid:
                me_fsid = resolved_me_fsid

        if not me_fsid and me.handle in handle_to_fsid:
            me_fsid = handle_to_fsid[me.handle]

        rel_errors: List[str] = []

        if me_fsid and do_parents and parents:
            parent1 = ""
            parent2 = ""

            parents_family_handle = me.get_main_parents_family_handle()
            family = (
                db.get_family_from_handle(parents_family_handle)
                if parents_family_handle
                else None
            )

            if family:
                father = family.get_father_handle()
                mother = family.get_mother_handle()

                if father:
                    parent1 = handle_to_fsid.get(father, "")
                if mother:
                    parent2 = handle_to_fsid.get(mother, "")

            if not parent1 and len(parents) > 0:
                parent1 = handle_to_fsid.get(parents[0], "")
            if not parent2 and len(parents) > 1:
                parent2 = handle_to_fsid.get(parents[1], "")

            if parent1 or parent2:
                attempted_relationships = True
                ok, err = fs_sync_core._post_child_and_parents(
                    session, me_fsid, parent1, parent2, change_message
                )
                if not ok:
                    rel_errors.append(f"Parent link failed for me={me_fsid}: {err}")

        if me_fsid and (do_spouses or do_children):
            for family_handle in family_handles:
                family = db.get_family_from_handle(family_handle)
                if not family:
                    continue

                spouse_handle = fs_sync_core._family_other_parent_handle(
                    family, me.handle
                )
                spouse_fsid = (
                    handle_to_fsid.get(spouse_handle or "", "") if spouse_handle else ""
                )

                if do_spouses and spouse_fsid:
                    attempted_relationships = True
                    ok, err = fs_sync_core._post_couple_relationship(
                        session, me_fsid, spouse_fsid, change_message
                    )
                    if not ok:
                        rel_errors.append(
                            f"Spouse link failed me={me_fsid} spouse={spouse_fsid}: {err}"
                        )

                if do_children:
                    child_refs = list(family.get_child_ref_list() or [])
                    for child_ref in child_refs:
                        child_handle = getattr(child_ref, "ref", None)
                        if not child_handle:
                            continue

                        child_fsid = handle_to_fsid.get(child_handle, "")
                        if not child_fsid:
                            continue

                        attempted_relationships = True
                        ok, err = fs_sync_core._post_child_and_parents(
                            session,
                            child_fsid,
                            me_fsid,
                            spouse_fsid,
                            change_message,
                        )
                        if not ok:
                            rel_errors.append(
                                f"Child link failed child={child_fsid} parent={me_fsid} spouse={spouse_fsid}: {err}"
                            )

        if rel_errors:
            WarningDialog(
                "Export completed, but some relationships failed to link on FamilySearch:\n\n%s"
                % "\n".join(rel_errors[:12]),
                parent=parent,
            )

        if me_fsid:
            try:
                _prime_person_cache(session, me_fsid, force=True)
            except Exception:
                pass

        if created_any:
            WarningDialog(
                _(
                    "Export complete: created people and linked relationships on FamilySearch."
                ),
                parent=parent,
            )
        elif attempted_relationships:
            WarningDialog(
                _(
                    "Export complete: no new people were created; relationships were attempted."
                ),
                parent=parent,
            )
        else:
            WarningDialog(_("Nothing was exported."), parent=parent)

    except Exception as err:
        WarningDialog(
            _("FamilySearch export failed: {e}").format(e=str(err)),
            parent=parent,
        )
