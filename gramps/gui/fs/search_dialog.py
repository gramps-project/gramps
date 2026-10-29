#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gabriel Rios
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

"""Reusable asynchronous search, canonical comparison and person selection."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
import threading
import weakref
from dataclasses import asdict
from typing import Any, Callable

from gi.repository import GLib, Gtk

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.fs.linking import (
    apply_link,
    plan_link,
    public_bindings,
    replace_binding,
)
from gramps.gen.fs.preview import FamilyPreview, PreviewService
from gramps.gen.fs.search import SearchPage, SearchQuery, SearchService
from gramps.gen.fs.search_prefill import person_query
from gramps.gen.fs.session import FSException
from gramps.gen.lib import Person
from gramps.gen.types import PersonHandle

from .ui import tool_section

_ = glocale.translation.gettext


def preview_text(preview: FamilyPreview) -> str:
    """Format actual facts and relationships without displaying internal JSON."""
    person = preview.person
    lines = [" / ".join(person.names) or person.person_id, person.person_id]
    if preview.redirected_ids:
        lines.append(_("Merged from: %s") % ", ".join(preview.redirected_ids))
    for fact in person.facts:
        lines.append(
            " · ".join(
                part
                for part in (
                    fact.kind.rsplit("/", 1)[-1],
                    fact.date or fact.formal_date,
                    fact.place,
                )
                if part
            )
        )
    roles = {"parent": _("Parent"), "spouse": _("Spouse"), "child": _("Child")}
    seen = set()
    for relation in preview.relatives:
        key = (relation.role, relation.person.person_id)
        text = " / ".join(relation.person.names) or relation.person.person_id
        if key not in seen:
            seen.add(key)
            lines.append(
                "%s: %s [%s]" % (roles[relation.role], text, relation.person.person_id)
            )
        for fact in relation.facts:
            lines.append("  " + fact.kind.rsplit("/", 1)[-1])
    return "\n".join(lines)


# ------------------------------------------------------------
# SearchDialog
# ------------------------------------------------------------
class SearchDialog:
    """Keep search requests pinned to their original tree, person and inputs."""

    def __init__(
        self,
        dbstate: Any,
        person: Person | None,
        session: Any,
        parent: Gtk.Window,
        editor: Any = None,
        *,
        on_selected: Callable[[FamilyPreview], None] | None = None,
    ) -> None:
        """Open a comparison window without changing any local or remote data."""
        self.dbstate = dbstate
        self.db: Any = dbstate.db
        if person is None and (on_selected is None or editor is not None):
            raise ValueError(_("Choose a local person or a person-selection action."))
        self.on_selected = on_selected
        self.subject = person
        self.handle = PersonHandle(person.handle) if person and person.handle else None
        self.saved_at_open = bool(
            self.handle and self.db.has_person_handle(self.handle)
        )
        self.editor_ref = weakref.ref(editor) if editor is not None else lambda: None
        self.had_editor = editor is not None
        self.session = session
        self.session_context = (
            session.auth_provider,
            session.api_url,
            getattr(session, "foundation_login_id", ""),
            getattr(session, "selected_tree_id", "GLOBAL"),
            getattr(session, "auth_generation", 0),
        )
        self.search_service = SearchService(session)
        self.preview_service = PreviewService(session)
        self.generation = 0
        self.busy = False
        self.closed = False
        self.next_url = ""
        self.query: SearchQuery | None = None
        self.preview: FamilyPreview | None = None
        self.initial_binding = public_bindings(person) if person is not None else ()
        self.entries: dict[str, Gtk.Entry] = {}
        self.window = Gtk.Window(title=_("Find on FamilySearch"), transient_for=parent)
        self.window.set_default_size(900, 680)
        self.window.set_border_width(12)
        self.window.connect("destroy", self.cb_destroy)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.window.add(outer)
        local = Gtk.Label(
            label=(
                _("Local person: %s") % name_displayer.display(person)
                if person is not None
                else _("Choose a FamilySearch person and review their family.")
            )
        )
        local.set_xalign(0)
        outer.pack_start(local, False, False, 0)
        local_details = Gtk.Label(
            label=self._local_summary(person) if person is not None else ""
        )
        local_details.set_xalign(0)
        local_details.set_selectable(True)
        local_details.set_line_wrap(True)
        outer.pack_start(local_details, False, False, 0)
        search_section, search_box = tool_section(_("Find a person"), "fs-sec-person")
        outer.pack_start(search_section, False, False, 0)
        grid = Gtk.Grid(column_spacing=10, row_spacing=6)
        search_box.pack_start(grid, False, False, 0)
        self.more_options = Gtk.Expander(label=_("More search options"))
        advanced_grid = Gtk.Grid(column_spacing=10, row_spacing=6)
        self.more_options.add(advanced_grid)
        search_box.pack_start(self.more_options, False, False, 0)
        lookup = Gtk.Expander(label=_("Look up a known ID or link"))
        lookup_row = Gtk.Box(spacing=8)
        lookup.add(lookup_row)
        search_box.pack_start(lookup, False, False, 0)
        fields = [
            ("given_name", _("Given name")),
            ("surname", _("Surname")),
            ("birth_from", _("Birth year from")),
            ("birth_to", _("Birth year to")),
            ("birth_place", _("Birth place")),
            ("death_place", _("Death place")),
            ("death_from", _("Death year from")),
            ("death_to", _("Death year to")),
            ("father_given", _("Father given name")),
            ("father_surname", _("Father surname")),
            ("mother_given", _("Mother given name")),
            ("mother_surname", _("Mother surname")),
            ("spouse_given", _("Spouse given name")),
            ("spouse_surname", _("Spouse surname")),
            ("advanced", _("Advanced query")),
            ("pid", _("Person ID or link")),
        ]
        basic_keys = {"given_name", "surname", "birth_from", "birth_to", "birth_place"}
        basic_index = advanced_index = 0
        for key, label in fields:
            widget = Gtk.Label(label=label)
            widget.set_xalign(0)
            entry = Gtk.Entry()
            entry.set_hexpand(True)
            self.entries[key] = entry
            if key == "pid":
                entry.set_placeholder_text(_("Person ID or FamilySearch person link"))
                lookup_row.pack_start(entry, True, True, 0)
                continue
            if key in basic_keys:
                target, index = grid, basic_index
                basic_index += 1
            else:
                target, index = advanced_grid, advanced_index
                advanced_index += 1
            column, row = (index % 2) * 2, index // 2
            target.attach(widget, column, row, 1, 1)
            target.attach(entry, column + 1, row, 1, 1)
        if person is not None:
            for key, value in asdict(person_query(self.db, person)).items():
                if key in self.entries:
                    self.entries[key].set_text("" if value is None else str(value))
        filled = sum(
            bool(entry.get_text())
            for key, entry in self.entries.items()
            if key not in basic_keys and key != "pid"
        )
        if filled:
            self.more_options.set_label(
                _("More search options (%d filled in)") % filled
            )
        for entry in self.entries.values():
            entry.connect("changed", self.cb_input_changed)
        buttons = Gtk.Box(spacing=8)
        search_box.pack_start(buttons, False, False, 0)
        self.search_button = Gtk.Button(label=_("Search"))
        self.pid_button = Gtk.Button(label=_("Look up ID"))
        self.next_button = Gtk.Button(label=_("Next page"))
        self.link_button = Gtk.Button(
            label=(
                _("Use this person")
                if on_selected is not None
                else _("Link this person")
            )
        )
        buttons.pack_start(self.search_button, False, False, 0)
        lookup_row.pack_start(self.pid_button, False, False, 0)
        review_section, review_box = tool_section(
            _("Review the person and family"), "fs-sec-import"
        )
        outer.pack_start(review_section, True, True, 0)
        if on_selected is not None:
            self.cancel_button = Gtk.Button(label=_("Cancel"))
            self.cancel_button.connect("clicked", self.cb_cancel)
            outer.pack_end(self.cancel_button, False, False, 0)
        self.search_button.connect("clicked", self.cb_search)
        self.pid_button.connect("clicked", self.cb_lookup)
        self.next_button.connect("clicked", self.cb_next)
        self.link_button.connect("clicked", self.cb_link)
        split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        review_box.pack_start(split, True, True, 0)
        self.results = Gtk.ListStore(str, str, str)
        tree = Gtk.TreeView(model=self.results)
        self.results_tree = tree
        for index, label in enumerate((_("Person"), _("ID"), _("Lifespan"))):
            tree.append_column(
                Gtk.TreeViewColumn(label, Gtk.CellRendererText(), text=index)
            )
        tree.get_selection().connect("changed", self.cb_select)
        scroll = Gtk.ScrolledWindow()
        scroll.add(tree)
        split.pack1(scroll, True, False)
        self.details = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.details)
        split.pack2(scroll, True, False)
        review_buttons = Gtk.Box(spacing=8)
        review_buttons.pack_start(self.next_button, False, False, 0)
        review_buttons.pack_end(self.link_button, False, False, 0)
        review_box.pack_start(review_buttons, False, False, 0)
        self.status = Gtk.Label(
            label=(
                _("Search results require identity review before choosing a person.")
                if on_selected is not None
                else (
                    _("Search results require identity review before linking.")
                    if self.saved_at_open
                    else _(
                        "Searching an unsaved person. Save the person normally, "
                        "then reopen this search before linking an ID."
                    )
                )
            )
        )
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        outer.pack_start(self.status, False, False, 0)
        self._sensitivity()
        self.window.show_all()

    def _context_valid(self) -> bool:
        """Pin saved identities or exact drafts, rejecting closed/changed contexts."""
        if self.closed or self.dbstate.db is not self.db:
            return False
        context = (
            self.session.auth_provider,
            self.session.api_url,
            getattr(self.session, "foundation_login_id", ""),
            getattr(self.session, "selected_tree_id", "GLOBAL"),
            getattr(self.session, "auth_generation", 0),
        )
        if context != self.session_context:
            return False
        if self.subject is None:
            return self.on_selected is not None and self.db is not None
        if self.had_editor:
            editor = self.editor_ref()
            if editor is None or getattr(editor, "db", None) is not self.db:
                return False
            subject = getattr(editor, "obj", None)
            if getattr(subject, "handle", None) != self.handle:
                return False
            if not self.saved_at_open and subject is not self.subject:
                return False
            if not editor.window.get_visible():
                return False
        if self.saved_at_open:
            return bool(
                self.db and self.handle and self.db.has_person_handle(self.handle)
            )
        # A draft remains a read-only search target. Saving it cannot turn an
        # in-flight result into permission to link a newly persisted person.
        return bool(
            self.db
            and self.subject.handle == self.handle
            and not (self.handle and self.db.has_person_handle(self.handle))
        )

    def _local_summary(self, person: Person) -> str:
        """Show available events and direct family context beside remote facts."""
        lines = []
        for reference in person.get_event_ref_list():
            event = self.db.get_event_from_handle(reference.ref)
            if event is None:
                continue
            place = self.db.get_place_from_handle(event.place) if event.place else None
            lines.append(
                " · ".join(
                    part
                    for part in (
                        str(event.get_type()),
                        str(event.get_date_object()),
                        place.get_title() if place else "",
                    )
                    if part
                )
            )
        parents: list[str] = []
        spouses: list[str] = []
        for family_handle in person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if family is not None:
                parents.extend(
                    handle
                    for handle in (
                        family.get_father_handle(),
                        family.get_mother_handle(),
                    )
                    if handle
                )
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if family is not None:
                spouses.extend(
                    handle
                    for handle in (
                        family.get_father_handle(),
                        family.get_mother_handle(),
                    )
                    if handle and handle != self.handle
                )
        for label, handles in [(_("Parent"), parents), (_("Spouse"), spouses)]:
            for handle in dict.fromkeys(handles):
                relative = self.db.get_person_from_handle(handle)
                if relative is not None:
                    lines.append(f"{label}: {name_displayer.display(relative)}")
        return "\n".join(lines)

    def _sensitivity(self) -> None:
        """Expose actions only when their required inputs are still current."""
        self.search_button.set_sensitive(not self.busy)
        self.results_tree.set_sensitive(not self.busy)
        self.pid_button.set_sensitive(not self.busy)
        self.next_button.set_sensitive(not self.busy and bool(self.next_url))
        self.link_button.set_sensitive(
            not self.busy
            and self.preview is not None
            and (
                self.on_selected is not None
                or (
                    self.saved_at_open
                    and self.handle is not None
                    and not self.db.readonly
                )
            )
            and self._context_valid()
        )

    def _launch(self, work: Callable[[], Any], done: Callable[[Any], None]) -> None:
        """Run HTTP work off the GUI thread; discard late or stale responses."""
        if self.busy or not self._context_valid():
            self.status.set_text(
                _("The person, tree or session changed. Reopen this search.")
            )
            return
        generation = self.generation
        self.busy = True
        self._sensitivity()
        self.status.set_text(_("Contacting FamilySearch…"))

        def deliver(value: Any, error: bool) -> bool:
            """Deliver only to the window and inputs that started this request."""
            if self.closed:
                return False
            self.busy = False
            self._sensitivity()
            if generation != self.generation or not self._context_valid():
                self.status.set_text(
                    _("Inputs or context changed; the old response was discarded.")
                )
                return False
            if error:
                self.status.set_text(value)
            else:
                done(value)
            self._sensitivity()
            return False

        def worker() -> None:
            """Keep GTK and the native database out of the network worker."""
            try:
                value = work()
            except (FSException, ValueError) as error:
                GLib.idle_add(deliver, str(error), True)
            except Exception:
                GLib.idle_add(
                    deliver,
                    _("The request failed. Check the connection and try again."),
                    True,
                )
            else:
                GLib.idle_add(deliver, value, False)

        threading.Thread(target=worker, name="fs-person-search", daemon=True).start()

    def cb_input_changed(self, *_args: Any) -> None:
        """Invalidate confirmation and pagination when any search input changes."""
        self.generation += 1
        self.preview = None
        self.next_url = ""
        self._sensitivity()

    def cb_search(self, *_args: Any) -> None:
        """Submit exactly the structured fields currently displayed."""
        values: dict[str, Any] = {}
        try:
            for key, entry in self.entries.items():
                if key == "pid":
                    continue
                text = entry.get_text().strip()
                values[key] = (
                    int(text)
                    if text and key.endswith(("_from", "_to"))
                    else (None if key.endswith(("_from", "_to")) else text)
                )
            query = SearchQuery(**values)
            query.parameters()
        except ValueError as error:
            self.status.set_text(str(error))
            return
        self.query = query
        self.preview = None
        self._launch(lambda: self.search_service.search(query), self._show_page)

    def _show_page(self, page: SearchPage) -> None:
        """Show retrieval results without treating rank as identity evidence."""
        self.results.clear()
        self.preview = None
        self.next_url = page.next_url
        for result in page.results:
            self.results.append((result.name, result.person_id, result.lifespan))
        self.details.get_buffer().set_text("")
        self.status.set_text(
            "\n".join(page.warnings)
            or (
                _("Select a result to compare its current person and family.")
                if page.results
                else _(
                    "No results for this query. This does not prove that no entry exists."
                )
            )
        )

    def cb_next(self, *_args: Any) -> None:
        """Retrieve one validated next page for the same frozen query."""
        query, next_url = self.query, self.next_url
        if query and next_url:
            self._launch(
                lambda: self.search_service.search(query, next_url=next_url),
                self._show_page,
            )

    def cb_select(self, selection: Gtk.TreeSelection) -> None:
        """Hydrate the selected PID rather than accepting a search display summary."""
        model, iterator = selection.get_selected()
        if iterator is None:
            return
        self.generation += 1
        self.preview = None
        pid = model.get_value(iterator, 1)
        self._launch(lambda: self.preview_service.preview(pid), self._show_preview)

    def cb_lookup(self, *_args: Any) -> None:
        """Resolve a supplied tree PID or person URL through the same preview."""
        value = self.entries["pid"].get_text()
        self.preview = None
        self._launch(lambda: self.preview_service.preview(value), self._show_preview)

    def _show_preview(self, preview: FamilyPreview) -> None:
        """Present canonical facts and graph before enabling explicit confirmation."""
        self.preview = preview
        self.details.get_buffer().set_text(preview_text(preview))
        self.status.set_text(
            _("Review this person and family before choosing them.")
            if self.on_selected is not None
            else (
                _("Compare this person and family with your evidence before linking.")
                if self.saved_at_open
                else _(
                    "Draft search only. Save the person normally, "
                    "then reopen this search to review and link the ID."
                )
            )
        )

    def cb_link(self, *_args: Any) -> None:
        """Recheck the selected PID before the final local-only confirmation."""
        if self.on_selected is not None:
            if self.preview is not None:
                pid = self.preview.person.person_id
                self._launch(
                    lambda: self.preview_service.preview(pid), self._confirm_selection
                )
            return
        if not self.saved_at_open or self.handle is None:
            self.status.set_text(
                _("Save the person and reopen this search before linking an ID.")
            )
            return
        if self.db.readonly:
            self.status.set_text(_("This tree is read-only; the ID cannot be changed."))
            return
        if self.preview is None:
            return
        pid = self.preview.person.person_id
        self._launch(lambda: self.preview_service.preview(pid), self._confirm_link)

    def _confirm_selection(self, preview: FamilyPreview) -> None:
        """Return fresh reviewed details to the caller; never write a local binding."""
        if self.on_selected is None or not self._context_valid():
            return
        if (
            self.preview is None
            or preview.person != self.preview.person
            or set(preview.relatives) != set(self.preview.relatives)
        ):
            self._show_preview(preview)
            self.status.set_text(
                _(
                    "The person or family changed. "
                    "Review the new comparison before choosing."
                )
            )
            return
        try:
            self.on_selected(preview)
        except (ValueError, FSException) as error:
            self.status.set_text(str(error))
            return
        except Exception:
            self.status.set_text(
                _("The selection could not be used. Recheck the current tree.")
            )
            return
        self.window.destroy()

    def _confirm_link(self, preview: FamilyPreview) -> None:
        """Apply only a current reviewed binding and reconcile the original editor."""
        if self.on_selected is not None:
            return
        if not self.saved_at_open or self.handle is None:
            self.status.set_text(
                _("Save the person and reopen this search before linking an ID.")
            )
            return
        if (
            self.preview is None
            or preview.person.person_id != self.preview.person.person_id
        ):
            self._show_preview(preview)
            self.status.set_text(
                _("The canonical person changed. Review it before linking.")
            )
            return
        if preview.person != self.preview.person or set(preview.relatives) != set(
            self.preview.relatives
        ):
            self._show_preview(preview)
            self.status.set_text(
                _(
                    "This person's details changed. Review the updated comparison before linking."
                )
            )
            return
        editor = self.editor_ref()
        try:
            if not self._context_valid():
                raise FSException(_("The person or tree changed. Reopen this search."))
            if (
                editor is not None
                and public_bindings(editor.obj) != self.initial_binding
            ):
                raise FSException(
                    _("The editor's FamilySearch link changed. Review it again.")
                )
            plan = plan_link(self.db, self.handle, preview.person.person_id)
            if plan.before != self.initial_binding:
                raise FSException(
                    _("The saved FamilySearch link changed. Review it again.")
                )
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=_("Link this local person to %s?") % preview.person.person_id,
            )
            dialog.format_secondary_text(
                _(
                    "Only the local FamilySearch ID changes. Existing facts and relationships are preserved."
                )
            )
            answer = dialog.run()
            dialog.destroy()
            if answer != Gtk.ResponseType.OK or not self._context_valid():
                return
            if (
                editor is not None
                and public_bindings(editor.obj) != self.initial_binding
            ):
                raise FSException(
                    _("The editor's FamilySearch link changed. Review it again.")
                )
            saved = apply_link(self.db, plan)
            if editor is not None:
                replace_binding(
                    editor.obj, self.initial_binding, preview.person.person_id
                )
                if (
                    editor.original is not None
                    and public_bindings(editor.original) == self.initial_binding
                ):
                    replace_binding(
                        editor.original, self.initial_binding, preview.person.person_id
                    )
                if hasattr(editor, "attr_list"):
                    editor.attr_list.data = editor.obj.get_attribute_list()
                    editor.attr_list.rebuild_callback()
            self.initial_binding = public_bindings(saved)
            self._show_preview(preview)
            self.status.set_text(_("FamilySearch ID saved locally."))
        except FSException as error:
            self.status.set_text(str(error))

    def cb_destroy(self, *_args: Any) -> None:
        """Invalidate pending work without touching another editor or tree."""
        self.closed = True
        self.generation += 1

    def cb_cancel(self, *_args: Any) -> None:
        """Close a selection window without returning a candidate or writing data."""
        self.window.destroy()


def choose_person(
    dbstate: Any,
    session: Any,
    parent: Gtk.Window,
    person: Person | None = None,
) -> FamilyPreview | None:
    """Run the shared read-only picker, optionally prefilled from a local person.

    :param dbstate: Native context pinned while the modal picker is open.
    :param session: Authorized transport whose account/tree cannot change.
    :param parent: Window blocked by the picker, without blocking GTK delivery.
    :param person: Optional local comparison subject; never saved or linked here.
    :returns: Fresh canonical comparison, or ``None`` after cancellation.
    """
    selected: list[FamilyPreview] = []
    dialog = SearchDialog(dbstate, person, session, parent, on_selected=selected.append)
    loop = GLib.MainLoop()
    dialog.window.set_modal(True)
    dialog.window.set_destroy_with_parent(True)
    dialog.window.connect("destroy", lambda *_args: loop.quit())
    loop.run()
    return selected[0] if selected else None
