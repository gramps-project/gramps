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

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlparse

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk  # noqa: F401 (Gdk used in some UI flows)

from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
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
from gramps.gui.dialog import ErrorDialog, OkDialog, QuestionDialog2

from . import sync_directions
from . import ui as fs_ui
from .compare.window import CompareWindow
from .fs_import.importer import FSToGrampsImporter
from .person import fsg_sync as FSG_Sync

_ = glocale.translation.gettext

_FS_ID_RE = re.compile(r"\b([A-Z0-9]{4}-[A-Z0-9]{3})\b", re.IGNORECASE)


# ------------------------------------------------------------
#
# _FamilySearchSearchResult
#
# ------------------------------------------------------------
@dataclass
class _FamilySearchSearchResult:
    """Small display model for a FamilySearch search result."""

    fsid: str
    name: str
    life: str = ""


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


def _familysearch_integration_enabled() -> bool:
    """Return whether FamilySearch integration is enabled in preferences."""
    try:
        return bool(config.get("familysearch.enable"))
    except Exception:
        return True


def _dbstate_is_empty_tree(dbstate: Any) -> bool:
    """Return whether a dbstate points at an open tree with no people."""
    if dbstate is None:
        return False

    is_open = getattr(dbstate, "is_open", None)
    if callable(is_open):
        try:
            if not is_open():
                return False
        except Exception:
            return False

    db = getattr(dbstate, "db", None)
    if db is None:
        return False

    count_people = getattr(db, "get_number_of_people", None)
    if callable(count_people):
        try:
            return int(count_people() or 0) == 0
        except Exception:
            pass

    get_person_handles = getattr(db, "get_person_handles", None)
    if callable(get_person_handles):
        try:
            return len(list(get_person_handles())) == 0
        except Exception:
            return False

    return False


def _familysearch_id_from_text(text: str) -> str:
    """Return a normalized FamilySearch person ID from pasted text or a URL."""
    text = (text or "").strip()
    if not text:
        return ""

    candidates = [text]
    if text.startswith(("http://", "https://")):
        try:
            parsed = urlparse(text)
            candidates.extend([parsed.path, parsed.query, parsed.fragment])
        except Exception:
            pass

    for candidate in candidates:
        match = _FS_ID_RE.search(candidate or "")
        if match:
            return match.group(1).upper()
    return ""


def _familysearch_id_from_links(links: Any) -> str:
    """Find a FamilySearch person ID in a GEDCOM X links object."""
    if isinstance(links, dict):
        values = list(links.values())
    elif isinstance(links, list):
        values = links
    else:
        values = []

    for value in values:
        if isinstance(value, dict):
            fsid = _familysearch_id_from_text(
                str(value.get("href") or value.get("resource") or "")
            )
            if fsid:
                return fsid
            fsid = _familysearch_id_from_links(value.get("links"))
            if fsid:
                return fsid
        elif isinstance(value, list):
            fsid = _familysearch_id_from_links(value)
            if fsid:
                return fsid
        else:
            fsid = _familysearch_id_from_text(str(value or ""))
            if fsid:
                return fsid
    return ""


def _search_entries(data: Any) -> list[dict[str, Any]]:
    """Return search entries from a FamilySearch Atom/GEDCOM X payload."""
    if not isinstance(data, dict):
        return []
    entries = data.get("entries")
    if entries is None:
        entries = (data.get("feed") or {}).get("entries")
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _first_search_person(entry: dict[str, Any]) -> dict[str, Any]:
    """Return the first GEDCOM X person embedded in a search entry."""
    content = entry.get("content") or {}
    gedcomx = content.get("gedcomx") or content.get("gedcomX") or {}
    persons = gedcomx.get("persons") or entry.get("persons") or []
    if isinstance(persons, list) and persons and isinstance(persons[0], dict):
        return persons[0]
    return {}


def _search_result_life(person_data: dict[str, Any]) -> str:
    """Return a compact life summary from FamilySearch display fields."""
    display = person_data.get("display") or {}
    lifespan = (display.get("lifespan") or display.get("lifeSpan") or "").strip()
    if lifespan:
        return lifespan

    birth = (display.get("birthDate") or display.get("birthPlace") or "").strip()
    death = (display.get("deathDate") or display.get("deathPlace") or "").strip()
    if birth and death:
        return _("%(birth)s - %(death)s") % {"birth": birth, "death": death}
    return birth or death


def _search_result_from_entry(
    entry: dict[str, Any],
) -> _FamilySearchSearchResult | None:
    """Build a display result from one FamilySearch search entry."""
    person_data = _first_search_person(entry)
    display = person_data.get("display") or {}
    fsid = (
        _familysearch_id_from_text(str(person_data.get("id") or ""))
        or _familysearch_id_from_links(person_data.get("links") or {})
        or _familysearch_id_from_text(str(entry.get("id") or ""))
        or _familysearch_id_from_links(entry.get("links") or {})
    )
    if not fsid:
        return None

    title = str(entry.get("title") or "").strip()
    name = (
        str(display.get("name") or display.get("fullName") or "").strip()
        or title
        or fsid
    )
    return _FamilySearchSearchResult(
        fsid=fsid, name=name, life=_search_result_life(person_data)
    )


def _search_familysearch_people(
    session: Any, query: str
) -> list[_FamilySearchSearchResult]:
    """Search FamilySearch Tree and return person choices for the dialog."""
    query = (query or "").strip()
    if not query:
        return []

    data = None
    headers = {"Accept": "application/x-gedcomx-atom+json"}
    get_url = getattr(session, "get_url", None)
    if callable(get_url):
        response = get_url(
            "/platform/tree/search",
            headers=headers,
            params={"q": query, "count": "25"},
        )
        if isinstance(response, dict):
            data = response
        else:
            status_code = getattr(response, "status_code", 200)
            if status_code and status_code >= 400:
                raise RuntimeError(
                    _("FamilySearch search failed (HTTP %(status)s).")
                    % {"status": status_code}
                )
            try:
                data = response.json()
            except Exception as err:
                raise RuntimeError(
                    _("FamilySearch search returned invalid data.")
                ) from err
    else:
        get_json = getattr(session, "get_jsonurl", None) or getattr(
            session, "get_json", None
        )
        if callable(get_json):
            endpoint = "/platform/tree/search?" + urlencode({"q": query, "count": "25"})
            data = get_json(endpoint, headers=headers)

    results: list[_FamilySearchSearchResult] = []
    seen: set[str] = set()
    for entry in _search_entries(data):
        result = _search_result_from_entry(entry)
        if result is None or result.fsid in seen:
            continue
        seen.add(result.fsid)
        results.append(result)
    return results


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


def _person_name_for_ui(person: Any) -> str:
    """Return a display name for the selected Gramps person."""
    display_name = str(getattr(person, "name", "") or "").strip()
    if display_name:
        return display_name
    try:
        return name_displayer.display(person)
    except Exception:
        return _("selected person")


def _new_generation_spin(default: int = 0) -> Gtk.SpinButton:
    """Create a spin button for a generation count."""
    adj = Gtk.Adjustment(
        value=default,
        lower=0,
        upper=99,
        step_increment=1,
        page_increment=5,
        page_size=0,
    )
    spinner = Gtk.SpinButton(adjustment=adj, climb_rate=0.0, digits=0)
    spinner.set_numeric(True)
    spinner.set_hexpand(True)
    return spinner


def _attach_grid_row(
    grid: Gtk.Grid,
    row: int,
    label_text: str,
    widget: Gtk.Widget,
    tooltip: str = "",
) -> None:
    """Attach a labeled row to an options grid."""
    label = Gtk.Label(label=_("%s: ") % label_text)
    label.set_xalign(0.0)
    label.set_halign(Gtk.Align.START)
    widget.set_halign(Gtk.Align.FILL)

    if tooltip:
        label.set_tooltip_text(tooltip)
        widget.set_tooltip_text(tooltip)

    grid.attach(label, 0, row, 1, 1)
    grid.attach(widget, 1, row, 1, 1)


def _bulk_import_options_dialog(
    parent: Gtk.Window,
    person: Any,
    fsid: str,
) -> dict[str, Any] | None:
    """Ask for FamilySearch bulk import options."""
    dlg = Gtk.Dialog(title=_("Bulk import relatives"), transient_for=parent, modal=True)
    dlg.get_style_context().add_class("fs-bulk-import-dialog")
    fs_ui.set_headerbar(dlg, _("Bulk import relatives"))

    dlg.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    import_button = dlg.add_button(_("Import"), Gtk.ResponseType.OK)
    import_button.get_style_context().add_class("suggested-action")

    box = dlg.get_content_area()
    box.set_spacing(10)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    selected_label = Gtk.Label(
        label=_("Starting person: %(name)s [%(fsid)s]")
        % {
            "name": _person_name_for_ui(person),
            "fsid": fsid,
        }
    )
    selected_label.set_xalign(0.0)
    selected_label.set_line_wrap(True)
    box.pack_start(selected_label, False, False, 0)

    grid = Gtk.Grid()
    grid.set_column_spacing(10)
    grid.set_row_spacing(8)
    grid.set_hexpand(True)
    box.pack_start(grid, False, False, 0)

    ancestor_spin = _new_generation_spin(default=1)
    descendant_spin = _new_generation_spin(default=0)

    _attach_grid_row(
        grid,
        0,
        _("Ancestor generations"),
        ancestor_spin,
        _("Number of generations to import upward from the starting person."),
    )
    _attach_grid_row(
        grid,
        1,
        _("Descendant generations"),
        descendant_spin,
        _("Number of generations to import downward from the starting person."),
    )

    checks = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.pack_start(checks, False, False, 0)

    include_spouses = Gtk.CheckButton(label=_("Include spouses"))
    include_spouses.set_tooltip_text(
        _("When off, import only the direct parent/child bloodline.")
    )

    noreimport = Gtk.CheckButton(label=_("Do not re-import existing people"))
    noreimport.set_active(True)
    noreimport.set_tooltip_text(
        _("Keep existing linked Gramps people unchanged during the import.")
    )

    include_sources = Gtk.CheckButton(label=_("Include sources"))
    include_sources.set_tooltip_text(_("Fetch and import FamilySearch sources."))

    include_notes = Gtk.CheckButton(label=_("Include notes"))
    include_notes.set_tooltip_text(_("Fetch and import FamilySearch notes."))

    import_cpr = Gtk.CheckButton(label=_("Link imported parent/child relationships"))
    import_cpr.set_active(True)
    import_cpr.set_tooltip_text(
        _("Create or reuse families so imported parents and children are connected.")
    )

    for check in (
        include_spouses,
        noreimport,
        include_sources,
        include_notes,
        import_cpr,
    ):
        checks.pack_start(check, False, False, 0)

    dlg.show_all()
    response = dlg.run()

    options = None
    if response == Gtk.ResponseType.OK:
        options = {
            "asc": ancestor_spin.get_value_as_int(),
            "desc": descendant_spin.get_value_as_int(),
            "include_spouses": include_spouses.get_active(),
            "noreimport": noreimport.get_active(),
            "include_sources": include_sources.get_active(),
            "include_notes": include_notes.get_active(),
            "import_cpr": import_cpr.get_active(),
        }

    dlg.destroy()
    return options


def _empty_tree_start_person_dialog(
    parent: Gtk.Window, session: Any
) -> _FamilySearchSearchResult | None:
    """Ask for the FamilySearch person that should seed an empty tree."""
    dlg = Gtk.Dialog(
        title=_("Start FamilySearch import"), transient_for=parent, modal=True
    )
    fs_ui.set_headerbar(dlg, _("Start FamilySearch import"))

    dlg.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
    import_button = dlg.add_button(_("Continue"), Gtk.ResponseType.OK)
    import_button.get_style_context().add_class("suggested-action")
    import_button.set_sensitive(False)
    dlg.set_default_response(Gtk.ResponseType.OK)

    box = dlg.get_content_area()
    box.set_spacing(10)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    intro = Gtk.Label(
        label=_(
            "Choose the FamilySearch person to use as the starting point for "
            "this new Gramps tree."
        )
    )
    intro.set_xalign(0.0)
    intro.set_line_wrap(True)
    box.pack_start(intro, False, False, 0)

    id_grid = Gtk.Grid()
    id_grid.set_column_spacing(10)
    id_grid.set_row_spacing(8)
    id_grid.set_hexpand(True)
    box.pack_start(id_grid, False, False, 0)

    id_entry = Gtk.Entry()
    id_entry.set_activates_default(True)
    id_entry.set_hexpand(True)
    id_entry.set_placeholder_text(_("FamilySearch ID or person URL"))
    _attach_grid_row(id_grid, 0, _("FamilySearch ID or URL"), id_entry)

    search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    search_entry = Gtk.Entry()
    search_entry.set_hexpand(True)
    search_entry.set_placeholder_text(_("Name, date, place, or FamilySearch ID"))
    search_button = Gtk.Button(label=_("Search"))
    search_box.pack_start(search_entry, True, True, 0)
    search_box.pack_start(search_button, False, False, 0)
    box.pack_start(search_box, False, False, 0)

    status_label = Gtk.Label(label="")
    status_label.set_xalign(0.0)
    status_label.set_line_wrap(True)
    box.pack_start(status_label, False, False, 0)

    store = Gtk.ListStore(str, str, str)
    treeview = Gtk.TreeView(model=store)
    treeview.set_headers_visible(True)
    treeview.set_vexpand(True)
    fs_ui.tune_treeview(treeview)

    for title, column_id, width in (
        (_("Name"), 1, 260),
        (_("Life"), 2, 220),
        (_("FamilySearch ID"), 0, 120),
    ):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)
        column.set_resizable(True)
        column.set_min_width(width)
        treeview.append_column(column)

    box.pack_start(fs_ui.wrap_scroller(treeview, min_h=220), True, True, 0)

    selection = treeview.get_selection()

    def selected_result() -> _FamilySearchSearchResult | None:
        """Return the selected result row, if any."""
        model, tree_iter = selection.get_selected()
        if tree_iter is None:
            return None
        return _FamilySearchSearchResult(
            fsid=model.get_value(tree_iter, 0),
            name=model.get_value(tree_iter, 1),
            life=model.get_value(tree_iter, 2),
        )

    def refresh_import_button() -> None:
        """Enable import when the ID entry contains a recognizable FSID."""
        import_button.set_sensitive(
            bool(_familysearch_id_from_text(id_entry.get_text()))
        )

    def cb_id_changed(_entry: Gtk.Entry) -> None:
        """Refresh the Continue button as the ID text changes."""
        refresh_import_button()

    def cb_selection_changed(_selection: Gtk.TreeSelection) -> None:
        """Copy the selected search result into the ID entry."""
        result = selected_result()
        if result is not None:
            id_entry.set_text(result.fsid)

    def cb_row_activated(
        _treeview: Gtk.TreeView, _path: Gtk.TreePath, _column: Gtk.TreeViewColumn
    ) -> None:
        """Continue when a search result is activated."""
        if _familysearch_id_from_text(id_entry.get_text()):
            dlg.response(Gtk.ResponseType.OK)

    def cb_search(*_args: Any) -> None:
        """Search FamilySearch and populate the result list."""
        raw_query = (search_entry.get_text() or "").strip()
        direct_fsid = _familysearch_id_from_text(raw_query)
        if direct_fsid:
            id_entry.set_text(direct_fsid)
            status_label.set_text(_("FamilySearch ID ready."))
            return

        if not raw_query:
            status_label.set_text(_("Enter a name, date, place, ID, or URL to search."))
            return

        store.clear()
        search_button.set_sensitive(False)
        status_label.set_text(_("Searching FamilySearch..."))
        while Gtk.events_pending():
            Gtk.main_iteration()

        try:
            results = _search_familysearch_people(session, raw_query)
        except Exception as err:
            status_label.set_text(_("Search failed: %(error)s") % {"error": str(err)})
            search_button.set_sensitive(True)
            return

        for result in results:
            store.append([result.fsid, result.name, result.life])

        if results:
            selection.select_path(0)
            status_label.set_text(
                _("Search results: %(count)d") % {"count": len(results)}
            )
        else:
            status_label.set_text(_("No FamilySearch people found."))

        search_button.set_sensitive(True)

    id_entry.connect("changed", cb_id_changed)
    selection.connect("changed", cb_selection_changed)
    treeview.connect("row-activated", cb_row_activated)
    search_entry.connect("activate", cb_search)
    search_button.connect("clicked", cb_search)

    dlg.show_all()
    response = dlg.run()
    fsid = _familysearch_id_from_text(id_entry.get_text())
    result = selected_result()
    dlg.destroy()

    if response != Gtk.ResponseType.OK or not fsid:
        return None

    if result is not None and result.fsid == fsid:
        return result

    return _FamilySearchSearchResult(fsid=fsid, name=_("FamilySearch person"))


def _run_bulk_import_from_options(
    dbstate: Any,
    uistate: Any,
    parent: Gtk.Window,
    fsid: str,
    options: dict[str, Any],
    session: Any = None,
) -> bool:
    """Run the GUI FamilySearch bulk importer from a raw FSID."""
    if session is not None:
        _bind_global_session(session)

    _ensure_status_schema(dbstate.db)

    class _Caller:
        """Minimal object expected by the GUI importer."""

        def __init__(self, dbstate: Any, uistate: Any) -> None:
            """Store the active database and UI state."""
            self.dbstate = dbstate
            self.uistate = uistate

    caller = _Caller(dbstate, uistate)

    importer = FSToGrampsImporter()
    importer.asc = int(options["asc"])
    importer.desc = int(options["desc"])
    importer.include_spouses = bool(options["include_spouses"])
    importer.noreimport = bool(options["noreimport"])
    importer.include_sources = bool(options["include_sources"])
    importer.include_notes = bool(options["include_notes"])
    importer.import_cpr = bool(options["import_cpr"])
    importer.verbosity = 0

    importer.import_tree(caller, fsid)
    tree_imp = getattr(importer, "fs_TreeImp", None)
    if tree_imp is None:
        return False

    if not list(getattr(tree_imp, "persons", []) or []):
        _error(
            parent,
            _("FamilySearch"),
            _(
                "No FamilySearch person was imported. Check the selected person "
                "ID and try again."
            ),
        )
        return False

    return True


def offer_empty_tree_import(
    dbstate: Any,
    uistate: Any,
    track: Any,
    session: Any,
    parent: Gtk.Window,
) -> None:
    """Offer a guided FamilySearch bulk import for an empty Gramps tree."""
    if not _familysearch_integration_enabled():
        return

    try:
        setattr(session, "_fs_empty_tree_import_prompted", True)
    except Exception:
        pass

    _bind_global_session(session)

    dialog = QuestionDialog2(
        _("FamilySearch"),
        _("Your tree is empty! Would you like to bulk import from " "FamilySearch?"),
        _("Choose Starting Person"),
        _("Not now"),
        parent=parent,
    )
    if not dialog.run():
        return

    start_person = _empty_tree_start_person_dialog(parent, session)
    if start_person is None:
        return

    options = _bulk_import_options_dialog(parent, start_person, start_person.fsid)
    if options is None:
        return

    if _run_bulk_import_from_options(
        dbstate, uistate, parent, start_person.fsid, options, session
    ):
        _info(parent, _("FamilySearch"), _("Bulk import complete."))


def offer_empty_tree_import_if_empty(
    dbstate: Any,
    uistate: Any,
    track: Any,
    session: Any,
    parent: Gtk.Window,
) -> bool:
    """Offer the starter import only when all activation conditions match."""
    if not _familysearch_integration_enabled():
        return False
    if getattr(session, "_fs_empty_tree_import_prompted", False) is True:
        return False
    if not _dbstate_is_empty_tree(dbstate):
        return False

    offer_empty_tree_import(dbstate, uistate, track, session, parent)
    return True


def bulk_import_relatives(
    dbstate: Any,
    uistate: Any,
    track: Any,
    person: Any,
    session: Any,
    parent: Gtk.Window,
    editor: Any = None,
) -> None:
    """Import multiple generations of relatives from FamilySearch."""
    _bind_global_session(session)

    fsid = _get_fs_id(person)
    if not fsid:
        _info(
            parent,
            _("FamilySearch"),
            _("No FamilySearch ID linked. Click 'Link FamilySearch ID' first."),
        )
        return

    if not _require_ready_person(dbstate, parent, person):
        return

    options = _bulk_import_options_dialog(parent, person, fsid)
    if options is None:
        return

    if not _run_bulk_import_from_options(
        dbstate, uistate, parent, fsid, options, session
    ):
        return

    if editor is not None and hasattr(editor, "_update_families"):
        try:
            editor._update_families()
        except Exception:
            pass

    _info(parent, _("FamilySearch"), _("Bulk import complete."))


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

    other_parent_ids = sorted(set(filter(None, (child_map.get(cid) for cid in chosen))))
    for other_parent_id in other_parent_ids:
        if _find_person_by_fsid(db, other_parent_id) is None:
            _import_full_person(dbstate, uistate, other_parent_id, verbosity=0)

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
            if other_parent_fsid and other_parent is None:
                continue

            fam = None
            if other_parent:
                for f in my_fams:
                    if _family_other_parent_handle(f, me.handle) == other_parent.handle:
                        fam = f
                        break

            if fam is None:
                for f in my_fams:
                    if _family_other_parent_handle(f, me.handle):
                        continue
                    if other_parent and list(f.get_child_ref_list() or []):
                        continue
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
                    if _family_other_parent_handle(f, me.handle):
                        continue
                    if list(f.get_child_ref_list() or []):
                        continue
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
