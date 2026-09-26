#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Grizard Merge Dialog
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""
Modal merge dialog for Grizard.

Shows the incoming GEDCOM tree on the left and the current family tree
(destination) on the right, with a per-field arrow button (=>) between
them for any data that does not match exactly. Clicking Apply runs the
gen-side GedGrizard._apply for the collected field resolutions.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import logging
import os
from typing import Any

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Pango

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Person
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import HandleError
from gramps.gen.grizard.grizardgedcom import GedGrizard
from gramps.gen.grizard.grizard import (
    safe_get_event,
    safe_get_family,
    safe_get_person,
    safe_get_place,
    safe_get_source,
    surname_prefix_text,
    surname_text,
)

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


# -------------------------------------------------------------------------
#
# Log
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(__name__)

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Module level helpers
#
# -------------------------------------------------------------------------
_DIFF_CSS_INSTALLED = False

# CSS class applied to both cells of a row whose values differ.
DIFF_STYLE_CLASS = "diff-line"

# Semi-transparent orange tint so differing values stand out on light and
# dark themes without requiring changes to core Gramps stylesheets.
DIFF_CSS_DATA = b"""
.diff-line {
  background-color: alpha(#ffa726, 0.30);
  border-radius: 3px;
}
"""


def ensure_diff_styles_installed() -> bool:
    """
    Install the custom CSS provider so the ``diff-line`` row tint applies.

    Rows whose values differ are tagged with the ``diff-line`` CSS class.
    Loading this directly via a Gtk.CssProvider keeps the dialog self-contained
    and independent of core Gramps stylesheets.

    :returns: True when the ``diff-line`` style was successfully installed
        for the default screen, False when there is no screen.
    :rtype: bool
    """
    global _DIFF_CSS_INSTALLED
    if _DIFF_CSS_INSTALLED:
        return True

    screen = Gdk.Screen.get_default()
    if screen is None:
        return False

    try:
        provider = Gtk.CssProvider()
        provider.load_from_data(DIFF_CSS_DATA)
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    except Exception:  # pragma: no cover - depends on the GTK install
        LOG.warning("Unable to install diff styles", exc_info=True)
        return False

    _DIFF_CSS_INSTALLED = True
    return True


def create_diff_cell(markup: str, differs: bool, xalign: float) -> Gtk.Label:
    """
    Build one value cell of a merge dialog row.

    The ``diff-line`` CSS class is added when the two sides of the row
    differ, so the cell is tinted by the rule in ``data/gramps.css`` even
    when no push arrow applies (a value present on only one side).

    :param markup: Pango markup holding the cell text.
    :param differs: True when the two sides of the row differ.
    :param xalign: Horizontal alignment, 0.0 for the incoming side and
        1.0 for the current tree side.
    :returns: The configured cell label.
    :rtype: Gtk.Label
    """
    cell = Gtk.Label()
    cell.set_markup(markup)
    cell.set_xalign(xalign)
    cell.set_line_wrap(True)
    if differs:
        cell.get_style_context().add_class(DIFF_STYLE_CLASS)
    return cell


def field_values_differ(left_val: Any, right_val: Any) -> bool:
    """
    Return True when the two sides of a merge dialog row differ.

    ``None`` is treated as an empty string so that a value present on only
    one side is still reported as a difference.

    :param left_val: Value from the incoming GEDCOM (source) side.
    :param right_val: Value from the current family tree (target) side.
    :returns: True if the two values are considered different.
    :rtype: bool
    """
    left_str = "" if left_val is None else str(left_val)
    right_str = "" if right_val is None else str(right_val)
    return left_str != right_str


# -------------------------------------------------------------------------
#
# GrizardMergeDialog
#
# -------------------------------------------------------------------------
class GrizardMergeDialog(Gtk.Dialog):
    """
    Modal dialog to review one source/target person pair and move
    fields between the two trees before committing to the database.
    """

    def __init__(
        self,
        dbstate: Any,
        grizard: GedGrizard,
        source_handle: str,
        target_handle: str | None,
        parent: Gtk.Window | None = None,
    ) -> None:
        """
        Build the modal merge dialog for one source/target person pair.

        :param dbstate: Active Gramps DB state manager (target tree).
        :param grizard: A GedGrizard whose connect/load steps already ran.
        :param source_handle: Handle of the person in the GEDCOM (source) DB.
        :param target_handle: Handle of the person in the target DB, or None
            to add the source person as a new one.
        :param parent: Parent window (translates to a modal dialog).
        """
        Gtk.Dialog.__init__(self, transient_for=parent, modal=True)
        self.set_title(_("Grizard Merge"))
        self.set_default_size(620, 850)
        self.set_border_width(6)
        ensure_diff_styles_installed()

        self.grizard = grizard
        source_db = grizard.context.get("source_db")
        if source_db is None:
            raise HandleError(_("No source database available for merge"))
        self.source_db = source_db
        self.target_db = dbstate.db
        self.source_handle = source_handle
        self.target_handle = target_handle
        source_person = safe_get_person(self.source_db, source_handle)
        if source_person is None:
            # The caller may hold a handle that no longer resolves (the
            # comparison window keeps pairing data across merges).
            raise HandleError(_("Source person no longer exists: %s") % source_handle)
        self.source_person: Person = source_person
        self.target_person: Person | None = safe_get_person(
            self.target_db, target_handle
        )
        if target_handle and self.target_person is None:
            raise HandleError(_("Target person no longer exists: %s") % target_handle)

        self._resolutions: dict[str, str] = {}
        self._mergeable_count: int = 0

        box = self.get_content_area()
        self._people_row = self._build_people_row()
        box.pack_start(self._people_row, False, False, 0)
        self._fields_table = self._build_fields_table()
        box.pack_start(self._fields_table, True, True, 0)

        bar = self.get_action_area()
        btn_cancel = Gtk.Button(label=_("Cancel"))
        btn_cancel.connect("clicked", self.cb_cancel)
        bar.pack_start(btn_cancel, False, False, 0)
        self._btn_apply = Gtk.Button(label=_("Apply"))
        self._btn_apply.get_style_context().add_class("suggested-action")
        self._btn_apply.connect("clicked", self.cb_apply)
        self._btn_apply.set_sensitive(self._mergeable_count > 0)
        bar.pack_start(self._btn_apply, False, False, 0)

        self.show_all()

    # ------------------------------------------------------------------
    # Styling helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_diff_line(
        label: str,
        left_val: str,
        right_val: str,
        show_label: bool,
        is_left: bool,
    ) -> str:
        """
        Format a line with Pango markup for the merge dialog.

        The entire line is rendered in italic. Words that differ between
        the left and right values are rendered in bold.

        :param label: The field label (e.g., "Given Name").
        :param left_val: The value for this side.
        :param right_val: The value for the other side (for comparison).
        :param show_label: Whether to include the label in the display.
        :param is_left: True if this is the left cell, False for right.
        :returns: Pango markup string.
        """
        # If values are the same, just return plain text (no highlighting)
        if left_val == right_val:
            if show_label:
                return glocale.translation.gettext("%s: %s") % (label, left_val)
            else:
                return left_val

        # Split into words for word-level comparison
        left_words = left_val.split()
        right_words = right_val.split()

        def _strip_trailing_punct(word: str) -> tuple[str, str]:
            """Split an unescaped word into (word_part, trailing_punct).

            :param word: Unescaped word text.
            :returns: Tuple of (cleaned_word, trailing_punctuation).
            """
            idx = len(word)
            while idx > 0 and word[idx - 1] in ",.;:!?)}":
                idx -= 1
            return word[:idx], word[idx:]

        # Word-by-word comparison
        parts: list[str] = []
        for i, word in enumerate(left_words):
            # Strip punctuation from the UNESCAPED word
            left_content, left_punct = _strip_trailing_punct(word)

            if i < len(right_words):
                other_word = right_words[i]
                right_content, _ = _strip_trailing_punct(other_word)
                # Compare unescaped content
                if left_content == right_content:
                    # Word matches (ignoring trailing punctuation) - just italic
                    parts.append("<i>%s</i>" % GLib.markup_escape_text(word))
                else:
                    # Word differs - bold only the word content, keep punct in italic
                    parts.append(
                        "<i><b>%s</b></i>%s"
                        % (
                            GLib.markup_escape_text(left_content),
                            GLib.markup_escape_text(left_punct),
                        )
                    )
            else:
                # Extra word in left_val - bold the content, keep punct in italic
                parts.append(
                    "<i><b>%s</b></i>%s"
                    % (
                        GLib.markup_escape_text(left_content),
                        GLib.markup_escape_text(left_punct),
                    )
                )

        value_markup = " ".join(parts)

        if show_label:
            # Add the label in italic before the value
            label_esc = GLib.markup_escape_text(
                glocale.translation.gettext("%s:") % label
            )
            # Remove inner <i> tags since they're redundant when wrapped in outer <i>
            value_no_i = value_markup.replace("<i>", "").replace("</i>", "")
            return "<i>%s %s</i>" % (label_esc, value_no_i)
        else:
            return value_markup

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_people_row(self) -> Gtk.Widget:
        """
        Build the top bar with the two person names and a single
        right-pointing arrow (data always flows GEDCOM -> Gramps, so the
        source is on the left and the destination on the right).
        """
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left = Gtk.Label(label=name_displayer.display(self.source_person))
        left.set_xalign(0.0)
        dash = Gtk.Label(label=_("\u2192"))
        dash.set_xalign(0.5)
        right = Gtk.Label(
            label=(
                name_displayer.display(self.target_person)
                if self.target_person is not None
                else _("New person")
            )
        )
        right.set_xalign(1.0)
        row.pack_start(left, True, True, 0)
        row.pack_start(dash, False, False, 0)
        row.pack_start(right, True, True, 0)
        return row

    def _build_fields_table(self) -> Gtk.Widget:
        """
        Build the scrollable grid of field rows with arrow buttons.
        """
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._grid = Gtk.Grid(column_spacing=8, row_spacing=4)
        scrolled.add(self._grid)
        self._row_index = 0
        self._populate_fields()
        return scrolled

    def _populate_fields(self) -> None:
        """
        Fill the grid with the four sections used by the GrizardCompare
        details panel (Individual Details, Family Relations, Children,
        Events & Other Records), each row showing the source value on the
        left and the target (destination) value on the right with an
        arrow between.
        """
        left = self.source_person
        # The dialog also opens in "add as new" mode, where there is no
        # target person yet; the right column then shows placeholders.
        right = self.target_person if self.target_person is not None else Person()
        td = self.target_db
        sd = self.source_db
        grid = self._grid

        def header(text: str, xalign: float = 0.0) -> Gtk.Label:
            lab = Gtk.Label()
            lab.set_xalign(xalign)
            lab.set_markup("<b>%s</b>" % GLib.markup_escape_text(text))
            return lab

        # Column headers at the top (match the compare window panel titles).
        grid.attach(header(_("Incoming GEDCOM Tree")), 0, 0, 1, 1)
        grid.attach(Gtk.Label(label=""), 1, 0, 1, 1)
        grid.attach(header(_("Current Family Tree")), 2, 0, 1, 1)
        self._row_index = 1

        def section(title: str) -> None:
            """Add a bold section heading and a separator beneath it."""
            grid.attach(header(title, xalign=0.5), 0, self._row_index, 3, 1)
            self._row_index += 1
            grid.attach(
                Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
                0,
                self._row_index,
                3,
                1,
            )
            self._row_index += 1

        def add_row(
            key: str | None,
            label: str,
            left_val: Any,
            right_val: Any,
            is_nullable_identity: bool = False,
            show_label: bool = True,
        ) -> None:
            ls = "" if left_val is None else str(left_val)
            rs = "" if right_val is None else str(right_val)
            same = not field_values_differ(ls, rs)
            if is_nullable_identity:
                same = bool(ls) == bool(rs)

            # Build Pango markup with italic for entire line and bold for diffs
            left_text = self._format_diff_line(label, ls, rs, show_label, is_left=True)
            right_text = self._format_diff_line(
                label, rs, ls, show_label, is_left=False
            )

            left_cell = create_diff_cell(left_text, not same, 0.0)
            right_cell = create_diff_cell(right_text, not same, 1.0)
            btn = None
            if key is not None:
                if is_nullable_identity:
                    if ls and not rs:
                        btn = self._make_arrow(key, label)
                        self._mergeable_count += 1
                elif not same and ls:
                    btn = self._make_arrow(key, label)
                    self._mergeable_count += 1
            gap = btn if btn is not None else Gtk.Label(label="")
            grid.attach(left_cell, 0, self._row_index, 1, 1)
            grid.attach(gap, 1, self._row_index, 1, 1)
            grid.attach(right_cell, 2, self._row_index, 1, 1)
            self._row_index += 1

        def event_groups(db: Any, person: Person) -> dict[str, list[tuple[str, str]]]:
            """
            Group a person's non-birth/death events by type string,
            returning a list of (event_handle, display_line) per type.
            """
            groups: dict[str, list[tuple[str, str]]] = {}
            for ref in person.get_event_ref_list():
                try:
                    event = safe_get_event(db, ref.ref)
                    if not event:
                        continue
                    etype = str(event.get_type())
                    if etype in ("_PPEXCLUDE", "_FSLINK", "Birth", "Death"):
                        continue
                    groups.setdefault(etype, []).append(
                        (event.handle, self._event_line_from(db, event))
                    )
                except Exception:
                    continue
            return groups

        def rel_items(db: Any, person: Person, role: str) -> list[Person]:
            if role == "spouse":
                return self._spouses(db, person)
            if role == "child":
                return self._children(db, person)
            return self._parents(db, person, role)

        genders = {
            Person.MALE: _("Male"),
            Person.FEMALE: _("Female"),
            Person.OTHER: _("Other"),
            Person.UNKNOWN: _("Unknown"),
        }

        # ---------- Individual Details ----------
        section(_("Individual Details"))
        add_row(
            "given_name",
            _("Given Name"),
            left.get_primary_name().first_name,
            right.get_primary_name().first_name,
        )
        left_surname = surname_text(left.get_primary_name())
        right_surname = surname_text(right.get_primary_name())
        add_row("surname", _("Surname"), left_surname, right_surname)
        left_prefix = surname_prefix_text(left.get_primary_name())
        right_prefix = surname_prefix_text(right.get_primary_name())
        add_row("surname_prefix", _("Surname Prefix"), left_prefix, right_prefix)
        add_row(
            "gender",
            _("Gender"),
            genders.get(left.get_gender(), _("Unknown")),
            genders.get(right.get_gender(), _("Unknown")),
        )
        l_b = self._event_for(sd, left, "birth")
        r_b = self._event_for(td, right, "birth")
        add_row(
            "birth_event",
            _("Birth"),
            self._event_display_from(l_b),
            self._event_display_from(r_b),
        )
        l_d = self._event_for(sd, left, "death")
        r_d = self._event_for(td, right, "death")
        add_row(
            "death_event",
            _("Death"),
            self._event_display_from(l_d),
            self._event_display_from(r_d),
        )
        add_row(
            "fsid",
            _("FamilySearch ID"),
            get_fsftid(left),
            get_fsftid(right),
            is_nullable_identity=True,
        )

        # ---------- Family Relations ----------
        section(_("Family Relations"))
        for role, title in (
            ("father", _("Father")),
            ("mother", _("Mother")),
            ("spouse", _("Spouse")),
        ):
            t_items = rel_items(td, right, role)
            s_items = rel_items(sd, left, role)
            count = max(len(t_items), len(s_items))
            for i in range(count):
                t_rel = t_items[i] if i < len(t_items) else None
                s_rel = s_items[i] if i < len(s_items) else None
                t_text = self._related_text(t_rel, td) if t_rel else ""
                s_text = self._related_text(s_rel, sd) if s_rel else ""
                key = (role + ":" + s_rel.handle) if s_rel else None
                add_row(key, title, s_text, t_text)

        # ---------- Children ----------
        section(_("Children"))
        t_items = rel_items(td, right, "child")
        s_items = rel_items(sd, left, "child")
        count = max(len(t_items), len(s_items))
        for i in range(count):
            t_rel = t_items[i] if i < len(t_items) else None
            s_rel = s_items[i] if i < len(s_items) else None
            t_text = self._related_text(t_rel, td) if t_rel else ""
            s_text = self._related_text(s_rel, sd) if s_rel else ""
            key = ("child:" + s_rel.handle) if s_rel else None
            add_row(key, "", s_text, t_text, show_label=False)

        # ---------- Events & Other Records ----------
        section(_("Events & Other Records"))
        source_groups = event_groups(sd, left)
        target_groups = event_groups(td, right)
        for etype in dict.fromkeys(list(source_groups) + list(target_groups)):
            s_items = source_groups.get(etype, [])
            t_items = target_groups.get(etype, [])
            count = max(len(s_items), len(t_items))
            for i in range(count):
                s_handle, s_line = s_items[i] if i < len(s_items) else (None, "")
                t_handle, t_line = t_items[i] if i < len(t_items) else (None, "")
                key = ("event:" + s_handle) if s_handle else None
                add_row(key, etype, s_line, t_line)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _event_year(self, db: Any, person: Person, kind: str) -> str:
        """
        Return the year of the person's birth/death event, or ''.
        ``kind`` is 'birth' or 'death'.
        """
        try:
            _date, _place, handle = self._event_for(db, person, kind)
            if not handle:
                return ""
            event = safe_get_event(db, handle)
            if event:
                return str(event.get_date_object().get_year() or "")
        except Exception:
            pass
        return ""

    def _event_for(
        self, db: Any, person: Person, kind: str
    ) -> tuple[str, str | None, str | None]:
        """
        Return (date_display, place_name, event_handle) for the person's
        birth/death event, or ('', None, None). ``kind`` is 'birth' or
        'death'.
        """
        if kind == "birth":
            ref = person.get_birth_ref()
        else:
            ref = person.get_death_ref()
        if not ref:
            return "", None, None
        try:
            event = safe_get_event(db, ref.ref)
            if not event:
                return "", None, None
            date_str = glocale.date_displayer.display(event.get_date_object())
            place = ""
            ph = event.get_place_handle()
            if ph:
                place_obj = safe_get_place(db, ph)
                if place_obj:
                    place = place_obj.get_name().get_value()
            return date_str, place or None, event.handle
        except Exception:
            return "", None, None

    def _event_display_from(self, event: tuple[str, str | None, str | None]) -> str:
        """Format a birth/death event tuple for display."""
        date_str, place, _handle = event
        return ", ".join(p for p in (date_str, place or "") if p)

    def _event_line_from(self, db: Any, event: Any) -> str:
        """Return ``date, place`` for an event, trimming empty parts."""
        date_str = glocale.date_displayer.display(event.get_date_object())
        place = ""
        ph = event.get_place_handle()
        if ph:
            try:
                place_obj = safe_get_place(db, ph)
                if place_obj:
                    place = place_obj.get_name().get_value() or ""
            except Exception:
                pass
        return ", ".join(p for p in (date_str, place) if p)

    def _vitals_text(self, person: Person, db: Any) -> str:
        """
        Return the compact vital summary for a person in the form
        ``b.<year> (<birth place>) d.<year>``, or ''.
        """
        birth_year = self._event_year(db, person, "birth")
        death_year = self._event_year(db, person, "death")
        birth_place = ""
        try:
            _d, birth_place, _h = self._event_for(db, person, "birth")
        except Exception:
            pass
        birth_part = ""
        if birth_year:
            birth_part = "b. %s" % birth_year
            if birth_place:
                birth_part += " (%s)" % birth_place
        parts = [
            p for p in (birth_part, "d. %s" % death_year if death_year else "") if p
        ]
        return " ".join(parts)

    def _related_text(self, person: Person, db: Any) -> str:
        """
        Return ``<display name> (b.<year> ... d.<year>)`` for a related
        person, omitting the parenthetical when no vitals are known.
        """
        name = name_displayer.display(person)
        vitals = self._vitals_text(person, db)
        return "%s (%s)" % (name, vitals) if vitals else name

    def _parents(self, db: Any, person: Person, role: str) -> list[Person]:
        out = []
        seen = set()
        for fh in person.get_parent_family_handle_list():
            fam = safe_get_family(db, fh)
            if not fam:
                continue
            handle = (
                fam.get_father_handle() if role == "father" else fam.get_mother_handle()
            )
            if handle and handle not in seen:
                seen.add(handle)
                person_obj = safe_get_person(db, handle)
                if person_obj:
                    out.append(person_obj)
        return out

    def _spouses(self, db: Any, person: Person) -> list[Person]:
        out = []
        seen = set()
        for fh in person.get_family_handle_list():
            fam = safe_get_family(db, fh)
            if not fam:
                continue
            fh_ = fam.get_father_handle()
            mh = fam.get_mother_handle()
            handle = mh if fh_ == person.handle else fh_
            if handle and handle not in seen:
                seen.add(handle)
                person_obj = safe_get_person(db, handle)
                if person_obj:
                    out.append(person_obj)
        return out

    def _children(self, db: Any, person: Person) -> list[Person]:
        out = []
        seen = set()
        for fh in person.get_family_handle_list():
            fam = safe_get_family(db, fh)
            if not fam:
                continue
            for child_ref in fam.get_child_ref_list():
                handle = child_ref.ref
                if handle in seen:
                    continue
                seen.add(handle)
                child = safe_get_person(db, handle)
                if child:
                    out.append(child)
        return out

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _make_arrow(self, key: str, label: str) -> Gtk.Button:
        """
        Build a right-pointing arrow button that moves the source value
        (left) for this field into the current family tree (right) when
        clicked.
        """
        btn = Gtk.Button(label=_("=>"))
        btn.set_tooltip_text(_("Move %s to current family tree") % label)
        btn.connect("clicked", self.cb_field_clicked, key)
        return btn

    def cb_field_clicked(self, button: Gtk.Button, key: str) -> None:
        """
        Record the user's choice to take the source value for this field.
        """
        button.set_label(_("\u2713"))
        button.set_sensitive(False)
        self._resolutions[key] = "source"

    def _find_dangling_references(self) -> dict[str, list[str]]:
        """
        Scan selected resolutions to find referenced objects (Notes, Media,
        Citations, Sources, Repositories) that do not exist in target DB.
        """
        missing = {
            "note": set(),
            "media": set(),
            "source": set(),
            "citation": set(),
            "repository": set(),
        }

        # Gather the primary source objects that will be copied/merged
        events_to_scan = []
        people_to_scan = []

        if not self.target_handle:  # Adding as new person
            people_to_scan.append(self.source_person)
            # Birth / death
            sb_ref = self.source_person.get_birth_ref()
            if sb_ref:
                events_to_scan.append(sb_ref.ref)
            sd_ref = self.source_person.get_death_ref()
            if sd_ref:
                events_to_scan.append(sd_ref.ref)
        else:
            # Merging
            # Check birth_event
            if self._resolutions.get("birth_event") == "source":
                sb_ref = self.source_person.get_birth_ref()
                if sb_ref:
                    events_to_scan.append(sb_ref.ref)
            # Check death_event
            if self._resolutions.get("death_event") == "source":
                sd_ref = self.source_person.get_death_ref()
                if sd_ref:
                    events_to_scan.append(sd_ref.ref)
            # Check other custom events
            for key, val in self._resolutions.items():
                if val == "source" and key.startswith("event:"):
                    s_evt_h = key.split(":", 1)[1]
                    events_to_scan.append(s_evt_h)

        # Helper to check target DB existence
        def target_has_note(h):
            try:
                return bool(self.target_db.get_note_from_handle(h))
            except Exception:
                return False

        def target_has_media(h):
            try:
                return bool(self.target_db.get_media_from_handle(h))
            except Exception:
                return False

        def target_has_citation(h):
            try:
                return bool(self.target_db.get_citation_from_handle(h))
            except Exception:
                return False

        def target_has_source(h):
            try:
                return bool(safe_get_source(self.target_db, h))
            except Exception:
                return False

        def target_has_repo(h):
            try:
                return bool(self.target_db.get_repository_from_handle(h))
            except Exception:
                return False

        # Recursively resolve references
        def scan_notes(nh_list):
            for nh in nh_list:
                if nh and not target_has_note(nh):
                    missing["note"].add(nh)

        def scan_media(mref_list):
            for mref in mref_list:
                mh = mref.get_reference_handle()
                if mh and not target_has_media(mh):
                    missing["media"].add(mh)
                    # Scan media notes
                    try:
                        s_med = self.source_db.get_media_from_handle(mh)
                        if s_med:
                            scan_notes(s_med.get_note_list())
                    except Exception:
                        pass

        def scan_repository(rh):
            if rh and not target_has_repo(rh):
                missing["repository"].add(rh)
                # Scan repo notes
                try:
                    s_rep = self.source_db.get_repository_from_handle(rh)
                    if s_rep:
                        scan_notes(s_rep.get_note_list())
                except Exception:
                    pass

        def scan_source(sh):
            if sh and not target_has_source(sh):
                missing["source"].add(sh)
                try:
                    s_src = safe_get_source(self.source_db, sh)
                    if s_src:
                        scan_notes(s_src.get_note_list())
                        scan_media(s_src.media_list)
                        for rref in s_src.reporef_list:
                            scan_repository(rref.get_reference_handle())
                except Exception:
                    pass

        def scan_citation(ch):
            if ch and not target_has_citation(ch):
                missing["citation"].add(ch)
                try:
                    s_cit = self.source_db.get_citation_from_handle(ch)
                    if s_cit:
                        scan_notes(s_cit.get_note_list())
                        scan_media(s_cit.media_list)
                        scan_source(s_cit.get_reference_handle())
                except Exception:
                    pass

        for p_obj in people_to_scan:
            scan_notes(p_obj.get_note_list())
            scan_media(p_obj.media_list)
            for ch in p_obj.get_citation_list():
                scan_citation(ch)

        for eh in events_to_scan:
            try:
                s_evt = safe_get_event(self.source_db, eh)
                if s_evt:
                    scan_notes(s_evt.get_note_list())
                    scan_media(s_evt.media_list)
                    for ch in s_evt.get_citation_list():
                        scan_citation(ch)
            except Exception:
                pass

        return {k: list(v) for k, v in missing.items()}

    def cb_apply(self, _button: Gtk.Button) -> None:
        """
        Run the apply step for the collected resolutions and close.
        """
        missing = self._find_dangling_references()
        total_missing = sum(len(lst) for lst in missing.values())

        if total_missing > 0:
            details = []
            if missing["citation"]:
                details.append(_("%d Citations") % len(missing["citation"]))
            if missing["source"]:
                details.append(_("%d Sources") % len(missing["source"]))
            if missing["note"]:
                details.append(_("%d Notes") % len(missing["note"]))
            if missing["media"]:
                details.append(_("%d Media Records") % len(missing["media"]))
            if missing["repository"]:
                details.append(_("%d Repositories") % len(missing["repository"]))

            msg = _(
                "The data being merged contains references to external objects that "
                "do not exist in your family tree:\n\n"
                "%s\n\n"
                "To prevent broken links, these missing references must be imported "
                "along with your selected details. Do you confirm importing these "
                "missing references?"
            ) % ", ".join(details)

            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Confirm Importing Missing References"),
            )
            dialog.format_secondary_text(msg)
            response = dialog.run()
            dialog.destroy()

            if response != Gtk.ResponseType.YES:
                return

        try:
            self.grizard.run_step(
                "apply",
                source_person_handle=self.source_handle,
                target_person_handle=self.target_handle,
                resolutions=self._resolutions,
            )
        except Exception as e:  # pragma: no cover
            LOG.exception("Apply failed: %s", e)
        self.response(Gtk.ResponseType.OK)

    def cb_cancel(self, _button: Gtk.Button) -> None:
        """Close the dialog without applying anything."""
        self.response(Gtk.ResponseType.CANCEL)
