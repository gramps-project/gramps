#
# Gramps - a GTK+/GNOME based genealogy program
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Large top-level comparison window showing the incoming GEDCOM tree side by
side with the existing Gramps tree (destination on the right).
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import logging
from typing import Any

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Person
from gramps.gen.errors import HandleError
from gramps.gen.grizard.grizardgedcom import GedGrizard
from gramps.gen.grizard.grizard import (
    CandidateMatcher,
    safe_get_event,
    safe_get_family,
    safe_get_person,
    safe_get_place,
    safe_get_source,
)
from gramps.gen.soundex import soundex
from gramps.gen.types import PersonHandle
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.const import GRAMPS_LOCALE as glocale

try:
    from gramps.gen.fs.utils.attributes import get_fsftid
except ImportError:  # Gramps < 6.1 has no gramps.gen.fs package

    def get_fsftid(gr_obj: Any) -> str:
        """Return the ``_FSFTID`` attribute value, else ``""``."""
        if not gr_obj:
            return ""
        try:
            attrs = (
                gr_obj.get_attribute_list()
                if hasattr(gr_obj, "get_attribute_list")
                else getattr(gr_obj, "attribute_list", []) or []
            )
        except Exception:
            return ""
        for attr in attrs or []:
            try:
                type_names = []
                attr_type = attr.get_type()
                for getter in ("xml_str", "__str__"):
                    try:
                        value = (
                            attr_type.xml_str()
                            if getter == "xml_str"
                            else str(attr_type)
                        )
                        if value:
                            type_names.append(str(value))
                    except Exception:
                        continue
                if "_FSFTID" in type_names:
                    return attr.get_value() or ""
            except Exception:
                continue
        return ""


from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.dialog import ErrorDialog

# -------------------------------------------------------------------------
#
# Log
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(__name__)

_ = glocale.translation.gettext

# Category definitions: (key, title, iter method)
CATEGORIES = [
    ("person", _("People"), "iter_person_handles"),
    ("family", _("Families"), "iter_family_handles"),
    ("event", _("Events"), "iter_event_handles"),
    ("place", _("Places"), "iter_place_handles"),
    ("source", _("Sources"), "iter_source_handles"),
    ("repository", _("Repositories"), "iter_repository_handles"),
    ("media", _("Media"), "iter_media_handles"),
    ("note", _("Notes"), "iter_note_handles"),
]


# ------------------------------------------------------------
#
# GrizardCompareWindow
#
# ------------------------------------------------------------
class GrizardCompareWindow(ManagedWindow, Gtk.Window):
    """
    Side-by-side comparison of a loaded GEDCOM tree (left) against the
    current Gramps tree (destination, right), with Previous/Next
    navigation between records that contain differences and a Merge
    button that opens the existing "Compare Differences" merge wizard.
    """
    # Default match threshold – can be overridden by a configuration file or
    # command‑line option in the future. Raising it from the historic 0.5 to
    # 0.7 reduces false‑positive matches that rely solely on Soundex surname
    # similarity.
    match_threshold: float = 0.7

    def __init__(
        self,
        uistate: Any,
        dbstate: Any,
        grizard: GedGrizard,
        parent: Gtk.Window | None = None,
    ) -> None:
        """
        Initialize the comparison window.

        :param uistate: Active Gramps UI state manager.
        :param dbstate: Active Gramps DB state manager.
        :param grizard: A GedGrizard instance whose connect and load steps
            have already been run (source_db present in its context).
        :param parent: Parent window.
        """
        Gtk.Window.__init__(self)
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(self, None, _("Grizard Compare"), isWindow=True)

        self.dbstate = dbstate
        self.grizard = grizard
        source_db = grizard.context.get("source_db")
        if source_db is None:
            raise HandleError(_("No source database available for comparison"))
        self.source_db: Any = source_db
        self.current_category = "person"
        self.diff_list: list[dict[str, Any]] = []
        self.diff_index = -1
        self.source_index: dict[str, str] = {}
        self.target_index: dict[str, str] = {}
        self._syncing = False

        self.set_title(_("Grizard Compare"))
        self.set_default_size(1600, 900)
        if parent:
            self.set_transient_for(parent)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(outer)

        outer.pack_start(self._build_toolbar(), False, False, 0)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        main_box.set_border_width(6)
        outer.pack_start(main_box, True, True, 0)

        self.paned = Gtk.HPaned()
        main_box.pack_start(self.paned, True, True, 0)

        self.left_panel = self._build_panel(_("Incoming GEDCOM Tree"))
        self.right_panel = self._build_panel(_("Current Family Tree"))
        self.paned.pack1(self.left_panel["frame"], True, False)
        self.paned.pack2(self.right_panel["frame"], True, False)
        # Split the two panels exactly in half once the window has been
        # allocated its real size.
        self._paned_positioned = False
        self.paned.connect("size-allocate", self.cb_paned_size_allocate)

        # Selection-based sync: when a row is selected in one panel, sync the
        # other panel to show the matched counterpart (if any).
        self._syncing_selection = False
        self.left_panel["tree"].get_selection().connect(
            "changed", self.cb_left_selection_changed
        )
        self.right_panel["tree"].get_selection().connect(
            "changed", self.cb_right_selection_changed
        )

        # Scroll-based sync (debounced): sync after scrolling stops briefly
        # to avoid freezing on large databases.
        self._syncing_scroll = False
        self._scroll_debounce_id = None
        left_vadj = self.left_panel["scrolled"].get_vadjustment()
        right_vadj = self.right_panel["scrolled"].get_vadjustment()
        left_hadj = self.left_panel["scrolled"].get_hadjustment()
        right_hadj = self.right_panel["scrolled"].get_hadjustment()

        left_vadj.connect("value-changed", self.cb_left_vscroll_changed)
        right_vadj.connect("value-changed", self.cb_right_vscroll_changed)
        left_hadj.connect("value-changed", self.cb_left_hscroll_changed)
        right_hadj.connect("value-changed", self.cb_right_hscroll_changed)

        self.select_category("person")

    # ------------------------------------------------------------------
    # Data population
    # ------------------------------------------------------------------
    def select_category(self, category: str) -> None:
        """
        Switch both panels to the given category and repopulate them.

        :param category: One of the category keys in CATEGORIES.
        """
        self.current_category = category
        self.diff_list = []
        self.diff_index = -1

        left_store = self.left_panel["store"]
        right_store = self.right_panel["store"]
        left_store.clear()
        right_store.clear()

        try:
            if category == "person":
                self._populate_people(left_store, right_store)
            else:
                self._populate_generic(category, left_store, right_store)
        except Exception as e:
            LOG.error("Failed to populate category %s: %s", category, e)
            ErrorDialog(_("Populate Failed"), str(e), parent=self)

        self._update_diff_status()
        # Select and scroll to the first difference. The mirror logic in
        # _highlight_diff also positions the other panel (matched person,
        # or its alphabetical insertion point when missing).
        self._select_first_diff()

    def _scroll_trees_top(self) -> bool:
        """
        Scroll both panel tree views back to the top row.

        If the tree views are not realized yet (window still being
        mapped), reschedule until they are.

        :returns: False when done, True to reschedule the idle callback.
        """
        all_realized = True
        for panel in (self.left_panel, self.right_panel):
            tree = panel["tree"]
            if not tree.get_realized():
                all_realized = False
                continue
            try:
                tree.scroll_to_point(0, 0)
            except Exception:
                LOG.debug("scroll_to_point failed", exc_info=True)
        return not all_realized

    def _person_group_name(self, db: Any, person: Person) -> str:
        """
        Return the "Group As" surname for a person, the same way the main
        Gramps People view groups people.
        """
        try:
            group = name_displayer.name_grouping_data(db, person.primary_name)
        except Exception:
            group = ""
        if not group:
            surname_list = person.get_primary_name().surname_list
            group = surname_list[0].surname if surname_list else "???"
        return group

    @staticmethod
    def _row_sort_key(store: Gtk.TreeStore, iter_: Gtk.TreeIter) -> tuple[str, str]:
        """
        Return the (group, name) sort key of a row in a people TreeStore.
        Group rows get an empty second element so they sort before their
        own children.
        """
        name = store.get_value(iter_, 1) or ""
        parent = store.iter_parent(iter_)
        if parent is None:
            return (name, "")
        group = store.get_value(parent, 1) or ""
        return (group, name)

    def _scroll_to_position(
        self,
        panel: dict[str, Any],
        group: str = "",
        name_str: str = "",
    ) -> None:
        """
        Scroll to the alphabetical insertion point without selecting it.

        Leaves the panel's selection cleared so an unmatched person can
        be added as new instead of looking like a matched pair.
        """
        store = panel["store"]
        best_path: Gtk.TreePath | None = None
        last_path: Gtk.TreePath | None = None
        target = (group.lower(), name_str.lower())
        for row in store:
            last_path = row.path
            key = self._row_sort_key(store, store.get_iter(row.path))
            probe = (key[0].lower(), key[1].lower())
            if not best_path and probe >= target:
                best_path = row.path
        if best_path is None:
            best_path = last_path
        selection = panel["tree"].get_selection()
        selection.unselect_all()
        if best_path is not None:
            panel["tree"].scroll_to_cell(best_path, None, False, 0, 0)

    def _select_person_or_position(
        self,
        panel: dict[str, Any],
        handle: str | None,
        group: str = "",
        name_str: str = "",
    ) -> None:
        """
        Select the row for the given handle. When the handle is missing
        (or None), select the row at the alphabetical insertion point of
        (group, name_str) — the first row that sorts at or after it — so
        the viewer is positioned where the person would be added.
        """
        store = panel["store"]
        if handle and self._select_handle(panel, handle):
            return

        # The TreeStore is sorted, so iteration order matches the view.
        best_path: Gtk.TreePath | None = None
        last_path: Gtk.TreePath | None = None
        target = (group.lower(), name_str.lower())
        for row in store:
            last_path = row.path
            key = self._row_sort_key(store, store.get_iter(row.path))
            probe = (key[0].lower(), key[1].lower())
            if not best_path and probe >= target:
                best_path = row.path
        if best_path is None:
            best_path = last_path
        if best_path is not None:
            panel["tree"].set_cursor(best_path)
            panel["tree"].scroll_to_cell(best_path, None, False, 0, 0)

    def cb_paned_size_allocate(self, widget: Gtk.Widget, allocation: Any) -> None:
        """
        Centre the paned divider so both panels get the same width.
        """
        if not self._paned_positioned and allocation is not None:
            self._paned_positioned = True
            self.paned.set_position(allocation.width // 2)

    def _populate_people(
        self, left_store: Gtk.TreeStore, right_store: Gtk.TreeStore
    ) -> None:
        """
        Populate both people lists as surname-grouped trees (like the
        main Gramps People view) and compute the difference list.
        """
        target_db = self.dbstate.db
        source_db = self.source_db
        matcher = CandidateMatcher(target_db)

        for handle in source_db.iter_person_handles():
            person = safe_get_person(source_db, handle)
            if not person:
                continue
            name_str = name_displayer.display(person)
            self._add_person_row(left_store, source_db, person, name_str)
            self.source_index[handle] = name_str

        for handle in target_db.iter_person_handles():
            person = safe_get_person(target_db, handle)
            if not person:
                continue
            name_str = name_displayer.display(person)
            self._add_person_row(right_store, target_db, person, name_str)
            self.target_index.setdefault(handle, name_str)

        for store, tree in (
            (left_store, self.left_panel["tree"]),
            (right_store, self.right_panel["tree"]),
        ):
            store.set_sort_column_id(1, Gtk.SortType.ASCENDING)
            tree.expand_all()

        # Build a surname index over target people so that matching is
        # near-linear instead of a full scan per source person.
        self._build_target_index(matcher)

        # Compute records with differences: matched pairs where compare
        # produces non-matching rows, plus source-only (new) people.
        # The full pairing (including pairs with no differences) is kept
        # so panel mirroring can always find the counterpart person.
        self._pair_map: dict[str, PersonHandle | None] = {}
        self._pair_map_rev: dict[PersonHandle, str] = {}
        for handle in source_db.iter_person_handles():
            person = safe_get_person(source_db, handle)
            if not person:
                continue
            target_handle = self._best_match(matcher, person)
            self._pair_map[handle] = target_handle
            if target_handle:
                self._pair_map_rev[target_handle] = handle
            try:
                if target_handle is None:
                    self.diff_list.append(
                        {"source_handle": handle, "target_handle": None}
                    )
                else:
                    rows = self.grizard.run_step(
                        "compare",
                        source_person_handle=handle,
                        target_person_handle=target_handle,
                    )
                    if any(r.status != "match" for r in rows):
                        self.diff_list.append(
                            {
                                "source_handle": handle,
                                "target_handle": target_handle,
                            }
                        )
            except Exception as e:
                LOG.warning("Comparison failed for %s: %s", handle, e)

        # Mark people that have differences with '*' in the Diff column;
        # rows left at 'o' have not been identified as different.
        for entry in self.diff_list:
            if entry["target_handle"]:
                self._mark_row(right_store, entry["target_handle"])
            self._mark_row(left_store, entry["source_handle"])

    @staticmethod
    def _mark_row(store: Gtk.TreeStore, handle: str, value: str = "*") -> None:
        """
        Set the Diff column (index 7) of the row with the given handle.
        """

        def visit(parent: Gtk.TreeIter | None = None) -> bool:
            iter_ = store.iter_children(parent) if parent else store.get_iter_first()
            while iter_:
                if store.get_value(iter_, 0) == handle:
                    store.set_value(iter_, 7, value)
                    return True
                if visit(iter_):
                    return True
                iter_ = store.iter_next(iter_)
            return False

        visit()

    def _build_target_index(self, matcher: CandidateMatcher) -> None:
        """
        Index target people by soundex of surname plus first initial so
        that candidate lookup avoids scanning the whole database.
        """
        self._target_index: dict[tuple[str, str], list[PersonHandle]] = {}
        for handle in self.dbstate.db.iter_person_handles():
            person = safe_get_person(self.dbstate.db, handle)
            if not person:
                continue
            key = self._match_key(person)
            self._target_index.setdefault(key, []).append(PersonHandle(handle))
        self._matcher = matcher

    @staticmethod
    def _match_key(person: Person) -> tuple[str, str]:
        """
        Return the (soundex surname, first initial) lookup key of a person.
        """
        name = person.get_primary_name()
        surname = ""
        if name.surname_list:
            surname = name.surname_list[0].surname or ""
        try:
            sdx = soundex(surname)
        except Exception:
            sdx = ""
        initial = (name.first_name or " ").strip()[:1].lower()
        return (sdx, initial)

    def _best_match(
        self, matcher: CandidateMatcher, source: Person
    ) -> PersonHandle | None:
        """
        Return the handle of the best matching target person, or None.
        """
        key = self._match_key(source)
        candidate_handles = self._target_index.get(key, [])
        # Also consider a soundex-less fallback bucket keyed on initial only
        if not candidate_handles:
            candidate_handles = self._target_index.get(("", key[1]), [])
        best_handle: PersonHandle | None = None
        # Default match threshold – can be tuned later via a class attribute
        # or configuration. Raising it from 0.5 to 0.7 makes spurious
        # Soundex‑only matches less likely to be accepted.
        best_score = getattr(self, "match_threshold", 0.7)
        for handle in candidate_handles:
            target = safe_get_person(self.dbstate.db, handle)
            if not target:
                continue
            # Basic guard: require at least one strong similarity signal before
            # considering the numeric score. This prevents a pair that only
            # shares a Soundex surname and first‑initial from being accepted.
            # Signals:
            #   * Exact surname match (case‑insensitive)
            #   * Exact first name match (case‑insensitive)
            #   * Birth year match when both have a birth date
            source_name = source.get_primary_name()
            target_name = target.get_primary_name()
            source_surname = (source_name.surname_list[0].surname if source_name.surname_list else "").lower()
            target_surname = (target_name.surname_list[0].surname if target_name.surname_list else "").lower()
            source_first = (source_name.first_name or "").strip().lower()
            target_first = (target_name.first_name or "").strip().lower()
            surname_match = source_surname and source_surname == target_surname
            first_match = source_first and source_first == target_first
            # Birth year comparison
            def _birth_year(person: Person) -> str | None:
                """Return the birth year of *person* as a string.

                The original implementation accessed ``ev.get_date()`` on an
                ``EventRef`` object, which no longer exists.  We now use the
                safe helper ``_get_event_year`` that retrieves the referenced
                ``Event`` and extracts the year via ``get_date_object()``.
                """
                ev = person.get_birth_ref()
                if ev:
                    # ``_get_event_year`` returns an empty string when the
                    # event or its date is missing, so we treat that as None.
                    # Choose the correct database for the person whose birth year
                    # we are extracting. ``source`` lives in ``self.source_db``
                    # while ``target`` lives in the destination database
                    # ``self.dbstate.db``.
                    db_for_person = self.source_db if person is source else self.dbstate.db
                    year = GrizardCompareWindow._get_event_year(ev, db_for_person)
                    if year:
                        return year
                return None
            birth_match = False
            src_year = _birth_year(source)
            tgt_year = _birth_year(target)
            if src_year and tgt_year and src_year == tgt_year:
                birth_match = True
            if not (surname_match or first_match or birth_match):
                # Skip this candidate – not enough evidence despite a high
                # numeric score.
                continue
            score = matcher.score_match(source, target, source_db=self.source_db)
            if score > best_score:
                best_score = score
                best_handle = handle
        return best_handle

    @staticmethod
    def _add_person_row(
        store: Gtk.TreeStore, db: Any, person: Person, name_str: str
    ) -> None:
        """
        Add a person row under its "Group As" surname group row, the same
        way the main Gramps People view groups people.

        :param store: The panel's TreeStore.
        :param db: Database the person belongs to.
        :param person: The person object.
        :param name_str: Display name of the person.
        """
        try:
            group = name_displayer.name_grouping_data(db, person.primary_name)
        except Exception:
            group = ""
        if not group:
            surname_list = person.get_primary_name().surname_list
            group = surname_list[0].surname if surname_list else "???"
        born = GrizardCompareWindow._get_born_text(person, db)
        died = GrizardCompareWindow._get_died_text(person, db)
        parents = GrizardCompareWindow._get_parent_names(person, db)
        spouse = GrizardCompareWindow._get_spouse_names(person, db)

        # Find or create the group row (group rows carry handle '')
        group_iter = None
        for row in store:
            if row[0] == "" and row[1] == group:
                group_iter = store.get_iter(row.path)
                break
        if group_iter is None:
            group_iter = store.append(None, ["", group, "", "", "", "", "", ""])
        store.append(
            group_iter,
            [
                person.handle,
                name_str,
                born,
                died,
                ", ".join(parents),
                ", ".join(spouse),
                person.gramps_id or "",
                "o",
            ],
        )

    def _populate_generic(
        self, category: str, left_store: Gtk.TreeStore, right_store: Gtk.TreeStore
    ) -> None:
        """
        Populate both panels with generic records for the given category.
        """
        iter_methods = dict((key, method) for key, _t, method in CATEGORIES)
        method = iter_methods[category]
        for db, store in (
            (self.source_db, left_store),
            (self.dbstate.db, right_store),
        ):
            for handle in getattr(db, method)():
                obj = self._get_object(db, category, handle)
                if obj is None:
                    continue
                store.append(
                    None,
                    [
                        handle,
                        self._describe_object(obj),
                        obj.gramps_id or "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                )

    def show(self, *args) -> None:
        """
        Show the window and all of its child widgets.
        """
        self.show_all()
        # show_all() reveals even previously hidden widgets, so re-apply
        # the visibility of empty detail sections afterwards.
        self._apply_section_visibility(self.left_panel)
        self._apply_section_visibility(self.right_panel)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_toolbar(self) -> Gtk.Widget:
        """
        Build the top control bar with Previous, Next, Merge and Close.
        """
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bar.set_border_width(6)

        self.diff_label = Gtk.Label(label="")
        bar.pack_start(self.diff_label, True, True, 0)

        # pack_end adds from the right edge, so declare in reverse visual
        # order: Close (rightmost), then Merge, Next and Previous.
        btn_close = Gtk.Button(label=_("Close"))
        btn_close.connect("clicked", self.cb_close)
        bar.pack_end(btn_close, False, False, 0)

        self.btn_merge_dialog = Gtk.Button(label=_("Merge..."))
        self.btn_merge_dialog.set_tooltip_text(
            _("Open the field-by-field merge dialog for the selected pair")
        )
        self.btn_merge_dialog.connect("clicked", self.cb_merge_dialog)
        bar.pack_end(self.btn_merge_dialog, False, False, 0)

        self.btn_add_new = Gtk.Button(label=_("Add as New..."))
        self.btn_add_new.set_tooltip_text(
            _("Add the selected incoming person as a new person")
        )
        self.btn_add_new.connect("clicked", self.cb_add_new)
        bar.pack_end(self.btn_add_new, False, False, 0)

        self.btn_next = Gtk.Button(label=_("Next"))
        self.btn_next.connect("clicked", self.cb_next)
        bar.pack_end(self.btn_next, False, False, 0)

        self.btn_prev = Gtk.Button(label=_("Previous"))
        self.btn_prev.connect("clicked", self.cb_previous)
        bar.pack_end(self.btn_prev, False, False, 0)

        return bar

    def _build_panel(self, title: str) -> dict[str, Any]:
        """
        Build one side-by-side comparison panel.

        :param title: Panel heading.
        :returns: Dict with keys 'frame', 'store', 'tree', 'detail' (the
            sectioned detail box) and one label per section:
            'detail_individual', 'detail_family', 'detail_children',
            'detail_events'.
        """
        frame = Gtk.Frame(label=title)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_border_width(4)
        frame.add(box)

        # Record rows: handle, name, born, died, parents, spouse, id.
        # Group rows use handle '' and blanks for the other columns.
        # A TreeStore is used for all categories: flat for generic
        # categories, two-level (surname group -> person) for people.
        store = Gtk.TreeStore(str, str, str, str, str, str, str, str)
        tree = Gtk.TreeView(model=store)
        col_diff = Gtk.TreeViewColumn(_("Diff"), Gtk.CellRendererText(), text=7)
        col_diff.set_resizable(False)
        col_diff.set_min_width(30)
        col_diff.set_max_width(40)
        tree.append_column(col_diff)
        col_main = Gtk.TreeViewColumn(_("Record"), Gtk.CellRendererText(), text=1)
        col_main.set_resizable(True)
        col_main.set_min_width(150)
        col_main.set_max_width(205)
        tree.append_column(col_main)
        for title, col_index in (
            (_("Born"), 2),
            (_("Died"), 3),
            (_("Parents"), 4),
            (_("Spouse"), 5),
            (_("ID"), 6),
        ):
            col = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=col_index)
            col.set_resizable(True)
            if col_index == 2:
                # Born: keep narrow; places may still expand via resize
                col.set_min_width(60)
                col.set_max_width(120)
            elif col_index == 4:
                # Parents: roughly 20% narrower than the natural width
                col.set_min_width(60)
                col.set_max_width(200)
            elif col_index == 5:
                # Spouse: about half the natural width
                col.set_min_width(50)
                col.set_max_width(120)
            elif col_index == 6:
                # ID: short values, keep compact
                col.set_min_width(30)
                col.set_max_width(55)
            tree.append_column(col)
        tree.get_selection().connect("changed", self.cb_record_selected)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 500)
        scrolled.add(tree)
        box.pack_start(scrolled, True, True, 0)

        detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        detail_box.set_border_width(4)
        section_labels = {}
        section_boxes = {}
        for key, title in (
            ("individual", _("Individual Details")),
            ("family", _("Family Relations")),
            ("children", _("Children")),
            ("events", _("Events & Other Records")),
        ):
            section_label = Gtk.Label(label="")
            section_label.set_xalign(0.0)
            section_label.set_line_wrap(True)
            section_label.set_selectable(True)
            section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            header = Gtk.Label()
            header.set_xalign(0.5)
            header.set_markup("<b>%s</b>" % GLib.markup_escape_text(title))
            section_box.pack_start(header, False, False, 0)
            section_box.pack_start(section_label, False, False, 0)
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            detail_box.pack_start(separator, False, False, 0)
            detail_box.pack_start(section_box, False, False, 0)
            section_labels[key] = section_label
            section_boxes[key] = section_box
            # Hidden until content exists; avoids a blank line under
            # headers of empty sections.
            section_box.hide()
        detail_scrolled = Gtk.ScrolledWindow()
        detail_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        detail_scrolled.set_size_request(-1, 490)
        detail_scrolled.add(detail_box)
        box.pack_start(detail_scrolled, False, False, 0)

        return {
            "frame": frame,
            "store": store,
            "tree": tree,
            "scrolled": scrolled,
            "detail": detail_box,
            "detail_individual": section_labels["individual"],
            "detail_family": section_labels["family"],
            "detail_children": section_labels["children"],
            "detail_events": section_labels["events"],
            "detail_boxes": section_boxes,
            "detail_texts": {},
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_object(db: Any, category: str, handle: str) -> Any:
        """
        Fetch an object of the given category from the database by handle.
        """
        getters = {
            "family": "get_family_from_handle",
            "event": "get_event_from_handle",
            "place": "get_place_from_handle",
            "source": "get_source_from_handle",
            "repository": "get_repository_from_handle",
            "media": "get_media_from_handle",
            "note": "get_note_from_handle",
        }
        getter = getters.get(category)
        if getter is None:
            return None
        try:
            return getattr(db, getter)(handle)
        except Exception:
            return None

    @staticmethod
    def _describe_object(obj: Any) -> str:
        """
        Produce a short display string for any non-person primary object.
        """
        if hasattr(obj, "get_description"):
            return obj.get_description() or ""
        if hasattr(obj, "get_title"):
            return obj.get_title() or ""
        if hasattr(obj, "get_name"):
            name = obj.get_name()
            if name is None:
                return ""
            if isinstance(name, str):
                return name
            if hasattr(name, "get_value"):
                return name.get_value() or ""
            return name.get_name() if hasattr(name, "get_name") else str(name)
        return obj.__class__.__name__

    @staticmethod
    def _get_born_text(person: Person, db: Any) -> str:
        """
        Return the birth summary (``b.<year> <place>``) for the person.
        """
        parts = []
        try:
            birth_year = GrizardCompareWindow._get_event_year(person.get_birth_ref(), db)
        except Exception:
            birth_year = ""
        if birth_year:
            parts.append("b. " + birth_year)
        birth_place = GrizardCompareWindow._get_event_place(person.get_birth_ref(), db)
        if birth_place:
            parts.append(birth_place)
        return " ".join(parts)

    @staticmethod
    def _get_died_text(person: Person, db: Any) -> str:
        """
        Return the death summary (``d.<year>``) for the person.
        """
        try:
            death_year = GrizardCompareWindow._get_event_year(person.get_death_ref(), db)
        except Exception:
            death_year = ""
        return "d. " + death_year if death_year else ""

    @staticmethod
    def _get_parent_names(
        person: Person, db: Any, family_role: str | None = None
    ) -> list[str]:
        """
        Return the display names of the person's parents, or [].

        :param family_role: Restrict to 'father', 'mother' or None for
            all parents across the person's parent families. Duplicate
            names (from multiple parent families) are removed.
        """
        names = []
        try:
            for family_handle in person.get_parent_family_handle_list():
                family = safe_get_family(db, family_handle)
                if not family:
                    continue
                if family_role == "father":
                    handles = [family.get_father_handle()]
                elif family_role == "mother":
                    handles = [family.get_mother_handle()]
                else:
                    handles = [
                        family.get_father_handle(),
                        family.get_mother_handle(),
                    ]
                for handle in handles:
                    if not handle:
                        continue
                    parent = safe_get_person(db, handle)
                    if parent:
                        name = name_displayer.display(parent)
                        if name not in names:
                            names.append(name)
        except Exception:
            pass
        return names

    @staticmethod
    def _get_spouse_names(person: Person, db: Any) -> list[str]:
        """
        Return the display names of the person's spouses, or [].
        """
        names = []
        try:
            for family_handle in person.get_family_handle_list():
                family = safe_get_family(db, family_handle)
                if not family:
                    continue
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                person_handle = person.handle
                spouse_handle = None
                if father_handle and father_handle != person_handle:
                    spouse_handle = father_handle
                elif mother_handle and mother_handle != person_handle:
                    spouse_handle = mother_handle
                if spouse_handle:
                    spouse = safe_get_person(db, spouse_handle)
                    if spouse:
                        names.append(name_displayer.display(spouse))
        except Exception:
            pass
        return names

    @staticmethod
    def _get_event_year(event_ref: Any, db: Any) -> str:
        """
        Return the year of the event referenced by event_ref, or ''.
        """
        if not event_ref:
            return ""
        try:
            # Normal case: EventRef points to an Event object.
            event = safe_get_event(db, getattr(event_ref, "ref", None))
            if event:
                return str(event.get_date_object().get_year() or "")
        except Exception:
            # Any unexpected attribute access (e.g., missing ``ref`` or legacy
            # ``get_date``) falls back to an empty string.
            pass
        return ""

    @staticmethod
    def _get_event_place(event_ref: Any, db: Any) -> str:
        """
        Return the place name of the event referenced by event_ref, or ''.
        """
        if not event_ref:
            return ""
        try:
            event = safe_get_event(db, event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    place = safe_get_place(db, place_handle)
                    if place:
                        return place.get_name().get_value() or ""
        except Exception:
            pass
        return ""

    def _update_diff_status(self) -> None:
        """
        Update the diff position label and button sensitivity.
        """
        is_people = self.current_category == "person"
        has_diffs = is_people and bool(self.diff_list)
        pair = self._get_selected_pair() if is_people else None
        self.btn_prev.set_sensitive(has_diffs)
        self.btn_next.set_sensitive(has_diffs)
        # Enable merge when there is a target person.
        self.btn_merge_dialog.set_sensitive(pair is not None and pair[1] is not None)
        # Enable "Add as New" when there is no target (standard case) **or**
        # when a target exists but the name fields are a poor match.  A poor
        # match is indicated by a diff status other than "match" for either the
        # given name or surname fields.
        name_poor_match = False
        if pair is not None and pair[1] is not None:
            for row in self.diff_list:
                if row.field in (_("Given Name"), _("Surname")) and row.status != "match":
                    name_poor_match = True
                    break
        self.btn_add_new.set_sensitive(pair is not None and (pair[1] is None or name_poor_match))
        if is_people:
            total = len(self.diff_list)
            pos = (self.diff_index + 1) if has_diffs else 0
            self.diff_label.set_text(_("Differences: %d of %d") % (pos, total))
        else:
            self.diff_label.set_text("")

    def select_pair(self, source_handle: str, target_handle: str | None) -> bool:
        """
        Pre-select a (source, optional target) person pair.

        :param source_handle: Handle in the incoming GEDCOM (source) tree.
        :param target_handle: Handle in the current tree, or None for the
            Add-as-New case (source row selected, insertion point mirrored).
        :returns: True when the source row was found and selected.
        """
        if self.current_category != "person":
            self.select_category("person")
        found = self._select_handle(self.left_panel, source_handle)
        try:
            if target_handle:
                self._select_handle(self.right_panel, target_handle)
            else:
                person = safe_get_person(self.source_db, source_handle)
                if person is not None:
                    self._scroll_to_position(
                        self.right_panel,
                        group=self._person_group_name(self.source_db, person),
                        name_str=name_displayer.display(person),
                    )
        except Exception:
            LOG.debug("select_pair mirror failed", exc_info=True)
        self._update_diff_status()
        return found

    def _select_first_diff(self) -> None:
        """
        Select the first difference record when available.
        """
        if self.current_category == "person" and self.diff_list:
            self.diff_index = 0
            self._highlight_diff()

    def _highlight_diff(self) -> None:
        """
        Select the rows in both panels corresponding to the current diff.
        The right panel shows the matched person, or scrolls to the
        alphabetical insertion point (left unselected) when the person is
        missing from the tree.
        """
        if not (0 <= self.diff_index < len(self.diff_list)):
            return
        entry = self.diff_list[self.diff_index]
        self._syncing = True
        try:
            self._select_handle(self.left_panel, entry["source_handle"])
            if entry["target_handle"]:
                self._select_handle(self.right_panel, entry["target_handle"])
            else:
                person = safe_get_person(self.source_db, entry["source_handle"])
                if person:
                    self._scroll_to_position(
                        self.right_panel,
                        group=self._person_group_name(self.source_db, person),
                        name_str=name_displayer.display(person),
                    )
        finally:
            self._syncing = False
        # Ensure button states reflect the current selection, especially when
        # the counterpart panel is deselected (e.g., unmatched person). This
        # refreshes the "Merge..." and "Add as New..." sensitivities.
        self._update_diff_status()

    def _select_handle(self, panel: dict[str, Any], handle: str) -> bool:
        """
        Select the row with the given handle in a panel's tree view,
        searching depth-first through any group rows.

        :returns: True if the row was found and selected.
        """

        def visit(store: Gtk.TreeStore, parent: Gtk.TreeIter | None) -> bool:
            iter_ = store.iter_children(parent) if parent else store.get_iter_first()
            while iter_:
                if store.get_value(iter_, 0) == handle:
                    path = store.get_path(iter_)
                    panel["tree"].set_cursor(path)
                    panel["tree"].scroll_to_cell(path, None, False, 0, 0)
                    return True
                if visit(store, iter_):
                    return True
                iter_ = store.iter_next(iter_)
            return False

        return visit(panel["store"], None)

    def _get_selected_pair(self) -> tuple[str, str | None] | None:
        """
        Return (source_handle, target_handle) for the current selection,
        or None if nothing valid is selected. Group header rows carry an
        empty handle and are treated as no selection.
        """
        model, tree_iter = self.left_panel["tree"].get_selection().get_selected()
        if not tree_iter:
            return None
        source_handle = model.get_value(tree_iter, 0)
        if not source_handle:
            return None
        target_handle = None
        rmodel, rtree_iter = self.right_panel["tree"].get_selection().get_selected()
        if rtree_iter:
            target_handle = rmodel.get_value(rtree_iter, 0) or None
        return source_handle, target_handle

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def cb_record_selected(self, tree_selection: Gtk.TreeSelection) -> None:
        """
        Handle a record selection change; update the detail pane, mirror
        the selection to the other panel, and update the buttons.
        """
        model, tree_iter = tree_selection.get_selected()
        if not tree_iter:
            return
        handle = model.get_value(tree_iter, 0)
        if not handle:
            # Group header row (surname group); nothing to show
            return
        tree = tree_selection.get_tree_view()
        is_left = tree is self.left_panel["tree"]
        panel = self.left_panel if is_left else self.right_panel
        other = self.right_panel if is_left else self.left_panel

        self._set_detail_sections(panel, handle)
        self._update_diff_status()

        # Mirror the selection into the other panel: same handle when it
        # exists there, otherwise the matched counterpart person, and as a
        # last resort the alphabetical insertion point of the selected
        # person. Handles are per-database, so a plain handle lookup only
        # works when a person is present in both trees.
        if self._syncing or self.current_category != "person":
            return
        self._syncing = True
        try:
            db = self.source_db if is_left else self.dbstate.db
            person = safe_get_person(db, handle)
            if not person:
                return
            other_db = self.dbstate.db if is_left else self.source_db
            counterpart = self._get_counterpart(handle)
            mirrored = False
            if counterpart:
                other_person = safe_get_person(other_db, counterpart)
                if other_person:
                    self._select_person_or_position(
                        other,
                        counterpart,
                        group=self._person_group_name(other_db, other_person),
                        name_str=name_displayer.display(other_person),
                    )
                    mirrored = True
            if not mirrored:
                self._scroll_to_position(
                    other,
                    group=self._person_group_name(db, person),
                    name_str=name_displayer.display(person),
                )
        finally:
            self._syncing = False

    def _get_counterpart(self, handle: str) -> str | None:
        """
        Return the handle of the counterpart person in the other panel,
        or None when the person has no matched pair.

        Uses the full pairing map (matched pairs regardless of whether
        they differ), falling back to the difference list for robustness.
        """
        if handle in self.source_index:
            pair_map = getattr(self, "_pair_map", {})
            if handle in pair_map:
                return pair_map[handle]
            for entry in self.diff_list:
                if entry["source_handle"] == handle:
                    return entry["target_handle"]
        else:
            pair_map = getattr(self, "_pair_map_rev", {})
            if handle in pair_map:
                return pair_map[handle]
            for entry in self.diff_list:
                if entry["target_handle"] == handle:
                    return entry["source_handle"]
        return None

    def _set_detail_sections(self, panel: dict[str, Any], handle: str) -> None:
        """
        Build and display the detail sections beneath the record lists.
        Lines that differ from the counterpart person in the other panel
        are rendered bold and italic so they stand out.
        """
        individual_text = family_text = children_text = events_text = ""
        if self.current_category == "person":
            db = self.source_db if handle in self.source_index else self.dbstate.db
            person = safe_get_person(db, handle)
            if person:
                other_handle = self._get_counterpart(handle)
                other_person = None
                other_db = None
                if other_handle:
                    other_db = (
                        self.dbstate.db
                        if other_handle not in self.source_index
                        else self.source_db
                    )
                    other_person = safe_get_person(other_db, other_handle)
                # The ID line always differs between the source and the
                # target database, so it is excluded from highlighting.
                skip = (_("ID:"),)
                individual_text = self._build_section_markup(
                    self._individual_lines(person, db),
                    (
                        self._individual_lines(other_person, other_db)
                        if other_person
                        else None
                    ),
                    skip,
                )
                family_text = self._build_section_markup(
                    self._family_lines(person, db),
                    (
                        self._family_lines(other_person, other_db)
                        if other_person
                        else None
                    ),
                    skip,
                )
                children_text = self._build_section_markup(
                    self._children_lines(person, db),
                    (
                        self._children_lines(other_person, other_db)
                        if other_person
                        else None
                    ),
                    skip,
                )
                events_text = self._build_section_markup(
                    self._event_lines(person, db),
                    self._event_lines(other_person, other_db) if other_person else None,
                    skip,
                )
                if not events_text:
                    # Show the section with a placeholder when the person
                    # has no events or other records to list.
                    events_text = _("(none)")
        panel["detail_individual"].set_markup(individual_text)
        panel["detail_family"].set_markup(family_text)
        panel["detail_children"].set_markup(children_text)
        panel["detail_events"].set_markup(events_text)
        panel["detail_texts"] = {
            "individual": individual_text,
            "family": family_text,
            "children": children_text,
            "events": events_text,
        }
        self._apply_section_visibility(panel)

    def _apply_section_visibility(self, panel: dict[str, Any]) -> None:
        """
        Show a detail section only when it has content; hide it otherwise
        so empty sections do not leave a blank line under their header.
        """
        for key, box in panel["detail_boxes"].items():
            if panel["detail_texts"].get(key):
                box.show()
            else:
                box.hide()

    @staticmethod
    def _build_section_markup(
        lines: list[str],
        other_lines: list[str] | None,
        skip_prefixes: tuple[str, ...] = (),
    ) -> str:
        """
        Render section lines as Pango markup, marking lines that are not
        present in the counterpart's lines with italic styling, and bolding
        only the specific words that differ.

        :param lines: This side's plain-text section lines.
        :param other_lines: Counterpart's lines, or None for no comparison.
        :param skip_prefixes: Lines starting with any of these are never
            highlighted (e.g., IDs that always differ across databases).
        """
        if not lines:
            return ""
        # Drop blank/whitespace-only lines and collapse any embedded
        # newlines so stray line feeds can never appear in a section.
        cleaned = []
        for line in lines:
            line = " ".join(line.split())
            if line:
                cleaned.append(line)
        if not cleaned:
            return ""
        escaped = [GLib.markup_escape_text(line) for line in cleaned]
        if not other_lines:
            return "\n".join(escaped)
        other_cleaned = [" ".join(line.split()) for line in other_lines if line.strip()]
        other_set = set(other_cleaned)
        out = []
        for i, (line, esc) in enumerate(zip(cleaned, escaped)):
            if line in other_set or any(
                line.startswith(prefix) for prefix in skip_prefixes
            ):
                out.append(esc)
            else:
                # Find the counterpart line at the same position, if available
                other_line = other_cleaned[i] if i < len(other_cleaned) else None
                # Entire line is italic, but only the differing words are bold
                out.append(
                    GrizardCompareWindow._italicize_with_bold_diffs(
                        line, esc, other_line
                    )
                )
        return "\n".join(out)

    @staticmethod
    def _italicize_with_bold_diffs(
        line: str,
        escaped_line: str,
        other_line: str | None,
    ) -> str:
        """
        Render a line with italic styling for the entire line, and bold
        styling for individual words that differ from another line.

        :param line: The original unescaped line text.
        :param escaped_line: The Pango-escaped line text.
        :param other_line: The counterpart line to compare against, or None.
        :returns: Pango markup string with italic and bold spans.
        """
        if not other_line:
            # No counterpart to compare against; just italicize the whole line
            return "<i>%s</i>" % escaped_line

        # If the entire lines are identical, return plain text (no styling)
        if line == other_line:
            return escaped_line

        # Split both lines into words for word-level comparison
        words = line.split()
        other_words = other_line.split()

        # Build the markup with bold spans for differing words
        # IMPORTANT: We compare words using UNESCAPED content and strip
        # punctuation from the unescaped word BEFORE escaping, so that
        # entity characters like &quot; are not corrupted.
        def _strip_trailing_punct(word: str) -> tuple[str, str]:
            """Split an unescaped word into (word_part, trailing_punct).

            :param word: Unescaped word text.
            :returns: Tuple of (cleaned_word, trailing_punctuation).
            """
            idx = len(word)
            while idx > 0 and word[idx - 1] in ",.;:!?)}":
                idx -= 1
            return word[:idx], word[idx:]

        parts: list[str] = []
        for i, (word, other_word) in enumerate(zip(words, other_words)):
            # Strip punctuation from the UNESCAPED word
            left_content, left_punct = _strip_trailing_punct(word)
            right_content, _ = _strip_trailing_punct(other_word)

            # Compare unescaped content
            if left_content == right_content:
                # Word matches (ignoring trailing punctuation) - just italic
                parts.append("<i>%s</i>" % GLib.markup_escape_text(word))
            else:
                # Word differs or counterpart is missing - italic + bold,
                # but only bold the word content; escape content and keep
                # the original unescaped punctuation (escaped separately)
                parts.append(
                    "<i><b>%s</b></i>%s"
                    % (
                        GLib.markup_escape_text(left_content),
                        GLib.markup_escape_text(left_punct),
                    )
                )

        # Handle extra words in the current line (if current line is longer)
        if len(words) > len(other_words):
            for word in words[len(other_words) :]:
                left_content, left_punct = _strip_trailing_punct(word)
                parts.append(
                    "<i><b>%s</b></i>%s"
                    % (
                        GLib.markup_escape_text(left_content),
                        GLib.markup_escape_text(left_punct),
                    )
                )

        # Join with spaces and wrap entire result in italic
        return " ".join(parts)

    def _individual_lines(self, person: Person, db: Any) -> list[str]:
        """
        Build the Individual Details section lines: identity, gender, ID,
        a one-line vital summary (``b.<year> (<birth place>) d.<year>``)
        and the FamilySearch ID last. Events and other records are shown
        in the Events & Other Records section instead.
        """
        lines = [name_displayer.display(person)]
        gender = {
            Person.MALE: _("Male"),
            Person.FEMALE: _("Female"),
        }.get(person.get_gender(), _("Unknown"))
        lines.append(_("Gender: %s") % gender)
        if person.gramps_id:
            lines.append(_("ID: %s") % person.gramps_id)
        birth_year = GrizardCompareWindow._get_event_year(person.get_birth_ref(), db)
        death_year = GrizardCompareWindow._get_event_year(person.get_death_ref(), db)
        birth_place = GrizardCompareWindow._get_event_place(person.get_birth_ref(), db)
        birth_part = ""
        if birth_year:
            birth_part = "b. " + birth_year
            if birth_place:
                birth_part += " (%s)" % birth_place
        vitals = " ".join(
            part
            for part in (
                birth_part,
                "d." + death_year if death_year else "",
            )
            if part
        )
        if vitals:
            lines.append(vitals)
        fs_id = self._get_familysearch_id(person, db)
        if fs_id:
            lines.append(_("FamilySearch: %s") % fs_id)
        return lines

    def _event_lines(self, person: Person, db: Any) -> list[str]:
        """
        Build the Events & Other Records section lines: every event and
        fact of the person, such as birth, death, occupation, residence,
        etc. Empty ``_PPEXCLUDE`` marker events and ``_FSLINK`` events
        are not shown; the FamilySearch ID appears in the Individual
        Details section instead.
        """
        lines = []
        for ref in person.get_event_ref_list():
            try:
                event = safe_get_event(db, ref.ref)
                if not event:
                    continue
                type_name = str(event.get_type())
                if type_name in ("_PPEXCLUDE", "_FSLINK"):
                    continue
                lines.append(self._format_event_line(event, db))
            except Exception as e:
                LOG.warning("Detail lookup failed: %s", e)
        return lines

    def _get_familysearch_id(self, person: Person, db: Any) -> str:
        """
        Return the FamilySearch person ID for the person, or ''.

        The ID is taken from the canonical ``_FSFTID`` attribute, falling
        back to the person ID parsed from the tail of a ``_FSLINK`` event
        URL (``.../details/<id>``).
        """
        fs_id = get_fsftid(person)
        if fs_id:
            return fs_id
        try:
            for ref in person.get_event_ref_list():
                event = safe_get_event(db, ref.ref)
                if not event:
                    continue
                if str(event.get_type()) != "_FSLINK":
                    continue
                description = event.get_description() or ""
                tail = description.rstrip("/").split("/")[-1]
                if tail and tail != "details":
                    return tail
        except Exception as e:
            LOG.warning("FamilySearch ID lookup failed: %s", e)
        return ""

    def _format_event_line(self, event: Any, db: Any) -> str:
        """
        Format one event or fact as a ``Type: date, place (description)``
        line. Missing parts are omitted cleanly.
        """

        def clean(text: str) -> str:
            # Collapse embedded newlines/extra whitespace into spaces.
            return " ".join(text.split())

        type_name = clean(str(event.get_type()))
        date_str = clean(glocale.date_displayer.display(event.get_date_object()))
        place = ""
        place_handle = event.get_place_handle()
        if place_handle:
            try:
                place_obj = safe_get_place(db, place_handle)
                if place_obj:
                    place = clean(place_obj.get_name().get_value() or "")
            except Exception:
                pass
        description = clean(event.get_description() or "")
        parts = [part for part in (date_str, place) if part]
        line = _("%s: %s") % (type_name, ", ".join(parts))
        if description:
            line += " (%s)" % description
        return line

    def _family_lines(self, person: Person, db: Any) -> list[str]:
        """
        Build the Family Relations section lines: father and mother on
        separate lines with their vital years, then spouse(s) with theirs.
        """
        lines = []
        for label, relateds in (
            (_("Father"), self._get_parent_persons(person, db, family_role="father")),
            (_("Mother"), self._get_parent_persons(person, db, family_role="mother")),
        ):
            for related in relateds:
                lines.append(
                    _("%s: %s") % (label, self._related_name_with_vitals(related, db))
                )
        spouses = self._get_spouse_persons(person, db)
        if spouses:
            lines.append(
                _("Spouse: %s")
                % ", ".join(
                    self._related_name_with_vitals(spouse, db) for spouse in spouses
                )
            )
        return lines

    def _get_parent_persons(
        self, person: Person, db: Any, family_role: str | None = None
    ) -> list[Person]:
        """
        Return the Person objects of the person's parents, or [].

        :param family_role: Restrict to 'father', 'mother' or None for
            all parents across the person's parent families. Duplicate
            persons (from multiple parent families) are removed.
        """
        persons = []
        try:
            for family_handle in person.get_parent_family_handle_list():
                family = safe_get_family(db, family_handle)
                if not family:
                    continue
                if family_role == "father":
                    handles = [family.get_father_handle()]
                elif family_role == "mother":
                    handles = [family.get_mother_handle()]
                else:
                    handles = [
                        family.get_father_handle(),
                        family.get_mother_handle(),
                    ]
                for handle in handles:
                    if not handle:
                        continue
                    parent = safe_get_person(db, handle)
                    if parent and parent not in persons:
                        persons.append(parent)
        except Exception:
            pass
        return persons

    def _get_spouse_persons(self, person: Person, db: Any) -> list[Person]:
        """
        Return the Person objects of the person's spouses, or [].
        """
        persons = []
        try:
            for family_handle in person.get_family_handle_list():
                family = safe_get_family(db, family_handle)
                if not family:
                    continue
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                person_handle = person.handle
                spouse_handle = None
                if father_handle and father_handle != person_handle:
                    spouse_handle = father_handle
                elif mother_handle and mother_handle != person_handle:
                    spouse_handle = mother_handle
                if spouse_handle:
                    spouse = safe_get_person(db, spouse_handle)
                    if spouse and spouse not in persons:
                        persons.append(spouse)
        except Exception:
            pass
        return persons

    def _vitals_text(self, related: Person, db: Any) -> str:
        """
        Return the compact vital summary (``b.<year> d.<year>``) of a
        related person, or ''.
        """
        try:
            birth_year = GrizardCompareWindow._get_event_year(related.get_birth_ref(), db)
        except Exception:
            birth_year = ""
        try:
            death_year = GrizardCompareWindow._get_event_year(related.get_death_ref(), db)
        except Exception:
            death_year = ""
        return " ".join(
            part
            for part in (
                "b. " + birth_year if birth_year else "",
                "d. " + death_year if death_year else "",
            )
            if part
        )

    def _children_lines(self, person: Person, db: Any) -> list[str]:
        """
        Build the Children section lines: children of each of the person's
        families, one per line with their vital years.
        """
        lines = []
        try:
            for family_handle in person.get_family_handle_list():
                family = safe_get_family(db, family_handle)
                if not family:
                    continue
                for child_ref in family.get_child_ref_list():
                    child = safe_get_person(db, child_ref.ref)
                    if child:
                        lines.append(self._related_name_with_vitals(child, db))
        except Exception as e:
            LOG.warning("Children lookup failed: %s", e)
        return lines

    def _related_name_with_vitals(self, related: Person, db: Any) -> str:
        """
        Return ``<display name> (b.<year> d.<year>)`` for a related
        person, omitting the parenthetical when no vitals are known.
        """
        name = name_displayer.display(related)
        vitals = self._vitals_text(related, db)
        if vitals:
            return "%s (%s)" % (name, vitals)
        return name

    def cb_previous(self, _button: Gtk.Button) -> None:
        """
        Move to the previous record that has differences.
        """
        if not self.diff_list:
            return
        if self.diff_index <= 0:
            self.diff_index = len(self.diff_list) - 1
        else:
            self.diff_index -= 1
        self._highlight_diff()

    def cb_next(self, _button: Gtk.Button) -> None:
        """
        Move to the next record that has differences.
        """
        if not self.diff_list:
            return
        self.diff_index = (self.diff_index + 1) % len(self.diff_list)
        self._highlight_diff()

    def cb_merge_dialog(self, _button: Gtk.Button) -> None:
        """
        Open the modal field-by-field merge dialog for the currently
        selected record pair.
        """
        pair = self._get_selected_pair()
        if pair is None:
            return
        source_handle, target_handle = pair
        if target_handle is None:
            LOG.info("No existing target for this person; add as new.")
            return
        from .grizardmergedialog import GrizardMergeDialog

        dialog = GrizardMergeDialog(
            self.dbstate,
            self.grizard,
            source_handle,
            target_handle,
            parent=self,
        )
        try:
            dialog.run()
        finally:
            dialog.destroy()
        # Re-activate the compare window: it is the transient parent of
        # the merge dialog, so presenting it restores focus without
        # requiring a click.
        self.present()
        # Rebuild both panels so any merged data and the diff list
        # reflect the new state.
        self.select_category("person")

    def cb_add_new(self, _button: Gtk.Button) -> None:
        """
        Add the selected incoming person as a new person in the tree.
        """
        pair = self._get_selected_pair()
        if pair is None or pair[1] is not None:
            return
        source_handle = pair[0]
        try:
            self.grizard.run_step(
                "apply",
                source_person_handle=source_handle,
                target_person_handle=None,
                resolutions={},
            )
        except Exception as exc:  # pragma: no cover
            LOG.exception("Add as new failed: %s", exc)
            ErrorDialog(_("Add as New failed"), str(exc), parent=self)
            return
        self.present()
        self.select_category("person")

    def cb_close(self, _button: Gtk.Button) -> None:
        """
        Handle window close button.
        """
        self.close()

    def cb_left_selection_changed(self, selection: Gtk.TreeSelection) -> None:
        """
        Synchronize selection from left to right panel.

        When a person is selected in the left panel, scroll the right panel
        to show the matched counterpart (if any), or the alphabetical
        insertion point when no match exists.
        """
        if self._syncing_selection:
            return
        self._syncing_selection = True
        try:
            self._sync_selection(self.left_panel, self.right_panel)
        finally:
            self._syncing_selection = False

    def cb_right_selection_changed(self, selection: Gtk.TreeSelection) -> None:
        """
        Synchronize selection from right to left panel.

        When a person is selected in the right panel, scroll the left panel
        to show the matched counterpart (if any), or the alphabetical
        insertion point when no match exists.
        """
        if self._syncing_selection:
            return
        self._syncing_selection = True
        try:
            self._sync_selection(self.right_panel, self.left_panel)
        finally:
            self._syncing_selection = False

    def _sync_selection(
        self, source_panel: dict[str, Any], target_panel: dict[str, Any]
    ) -> None:
        """
        Sync the target panel to show the counterpart of the source selection.

        Uses the current selection in the source panel to look up the matched
        counterpart in the other database via the pairing map, then scrolls
        the target panel to show that counterpart's row.
        """
        source_tree = source_panel["tree"]
        target_tree = target_panel["tree"]

        # Get the current selection from the source tree
        selection = source_tree.get_selection()
        model, tree_iter = selection.get_selected()

        if not tree_iter:
            return

        # Get the handle of the selected row
        handle = model.get_value(tree_iter, 0)
        if not handle:
            # Empty handle means it's a group header; skip
            return

        # Determine which database the source handle belongs to
        is_source_left = source_panel is self.left_panel
        source_db = self.source_db if is_source_left else self.dbstate.db
        target_db = self.dbstate.db if is_source_left else self.source_db

        person = safe_get_person(source_db, handle)
        if not person:
            return

        group = self._person_group_name(source_db, person)
        name_str = name_displayer.display(person)

        # Look up counterpart in the pairing map
        counterpart = self._get_counterpart(handle)

        if counterpart:
            # Counterpart exists; select and scroll to it. The pairing map
            # can hold a handle that a merge has since deleted, in which
            # case there is no counterpart to select.
            counterpart_person = safe_get_person(target_db, counterpart)
            if counterpart_person is None:
                self._scroll_to_position(
                    target_panel,
                    group=group,
                    name_str=name_str,
                )
                return
            self._select_person_or_position(
                target_panel,
                counterpart,
                group=self._person_group_name(target_db, counterpart_person),
                name_str=name_str,
            )
        else:
            # No counterpart; scroll to alphabetical insertion point but
            # leave it unselected so the row can be added as new.
            self._scroll_to_position(
                target_panel,
                group=group,
                name_str=name_str,
            )

    def cb_left_vscroll_changed(self, adj: Gtk.Adjustment) -> None:
        """
        Debounced vertical scroll sync from left to right.

        Schedules a sync after scrolling stops (200ms debounce) to avoid
        excessive processing during continuous scroll operations.
        """
        if self._syncing_scroll:
            return
        self._schedule_scroll_sync(self.left_panel, self.right_panel)

    def cb_right_vscroll_changed(self, adj: Gtk.Adjustment) -> None:
        """
        Debounced vertical scroll sync from right to left.

        Schedules a sync after scrolling stops (200ms debounce) to avoid
        excessive processing during continuous scroll operations.
        """
        if self._syncing_scroll:
            return
        self._schedule_scroll_sync(self.right_panel, self.left_panel)

    def _schedule_scroll_sync(
        self, source_panel: dict[str, Any], target_panel: dict[str, Any]
    ) -> None:
        """
        Schedule a debounced scroll sync after scrolling stops.
        """
        # Cancel any pending sync
        if self._scroll_debounce_id is not None:
            GLib.source_remove(self._scroll_debounce_id)
            self._scroll_debounce_id = None

        # Schedule a new sync after 200ms of no scroll activity
        def do_sync() -> bool:
            self._sync_scroll_panel(source_panel, target_panel)
            self._scroll_debounce_id = None
            return False  # Remove the source

        self._scroll_debounce_id = GLib.timeout_add(200, do_sync)

    def _sync_scroll_panel(
        self, source_panel: dict[str, Any], target_panel: dict[str, Any]
    ) -> None:
        """
        Sync target panel to show the counterpart of the source panel's
        current selection.

        Uses the currently selected row in the source panel to find the
        matched counterpart, avoiding expensive iteration through all rows.
        """
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        try:
            source_tree = source_panel["tree"]
            target_tree = target_panel["tree"]

            # Use the current selection (fast O(1) lookup)
            selection = source_tree.get_selection()
            model, tree_iter = selection.get_selected()

            if not tree_iter:
                return

            handle = model.get_value(tree_iter, 0)
            if not handle:
                return

            # Determine which database the source handle belongs to
            is_source_left = source_panel is self.left_panel
            source_db = self.source_db if is_source_left else self.dbstate.db
            target_db = self.dbstate.db if is_source_left else self.source_db

            person = safe_get_person(source_db, handle)
            if not person:
                return

            group = self._person_group_name(source_db, person)
            name_str = name_displayer.display(person)

            # Look up counterpart in the pairing map
            counterpart = self._get_counterpart(handle)

            if counterpart:
                # Counterpart exists; select and scroll to it
                counterpart_person = safe_get_person(target_db, counterpart)
                self._select_person_or_position(
                    target_panel,
                    counterpart,
                    group=(
                        self._person_group_name(target_db, counterpart_person)
                        if counterpart_person
                        else group
                    ),
                    name_str=name_str,
                )
            else:
                # No counterpart; scroll to alphabetical insertion point but
                # leave it unselected so the row can be added as new.
                self._scroll_to_position(
                    target_panel,
                    group=group,
                    name_str=name_str,
                )
        finally:
            self._syncing_scroll = False

    def cb_left_hscroll_changed(self, adj: Gtk.Adjustment) -> None:
        """
        Debounced horizontal scroll sync from left to right.
        """
        if self._syncing_scroll:
            return
        self._schedule_scroll_sync(self.left_panel, self.right_panel)

    def cb_right_hscroll_changed(self, adj: Gtk.Adjustment) -> None:
        """
        Debounced horizontal scroll sync from right to left.
        """
        if self._syncing_scroll:
            return
        self._schedule_scroll_sync(self.right_panel, self.left_panel)
