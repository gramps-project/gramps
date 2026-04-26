#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Doug Blank <doug.blank@gmail.com>
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
GTK confirmation dialog for the quick place-hierarchy entry feature.

Usage::

    from gramps.gui.selectors.quickplacedialog import QuickPlaceDialog
    from gramps.gui.selectors.quickplaceparser import parse_place_hierarchy

    parsed = parse_place_hierarchy(db, "Springfield, Illinois, USA")
    dlg = QuickPlaceDialog(db, parsed, parent=parent_window)
    response = dlg.run()
    dlg.destroy()
    if response == Gtk.ResponseType.OK:
        # parsed entries now carry a 'place_type' key for every "new" row
        handle = commit_place_hierarchy(db, parsed, transaction)
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import PlaceType

if TYPE_CHECKING:
    from gramps.gen.db import DbGeneric

_ = glocale.translation.gettext

LOG = logging.getLogger(__name__)

# Map from combo row index → (int_value, translated label)
_TYPE_ROWS: list[tuple[int, str]] = [
    (val, label) for val, label, _xml in PlaceType._DATAMAP
]


# -------------------------------------------------------------------------
#
# QuickPlaceDialog
#
# -------------------------------------------------------------------------
class QuickPlaceDialog(Gtk.Dialog):
    """
    Confirmation dialog that shows a parsed place hierarchy.

    Rows marked ``"existing"`` are displayed read-only with the current
    place type.  Rows marked ``"new"`` have an editable PlaceType combo.

    After :meth:`run` returns ``Gtk.ResponseType.OK``, every ``"new"``
    entry in *parsed* will carry a ``place_type`` key set to a
    :class:`PlaceType` instance reflecting the user's selection.

    :param db: The Gramps database (used to look up existing place types).
    :type db: DbGeneric
    :param parsed: List of entry dicts from
        :func:`~gramps.gui.selectors.quickplaceparser.parse_place_hierarchy`.
    :type parsed: list[dict]
    :param parent: Optional transient parent window.
    :type parent: Gtk.Window | None
    """

    def __init__(
        self,
        db: "DbGeneric",
        parsed: list[dict],
        parent: Gtk.Window | None = None,
    ) -> None:
        """
        Initialise the dialog and build the place hierarchy table.

        :param db: The Gramps database.
        :type db: DbGeneric
        :param parsed: List of entry dicts from parse_place_hierarchy().
        :type parsed: list[dict]
        :param parent: Optional transient parent window.
        :type parent: Gtk.Window | None
        """
        super().__init__(
            title=_("Confirm Place Hierarchy"),
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
        )
        self._db = db
        self._parsed = parsed
        # Maps each combo widget to its 0-based index in _parsed.
        self._combos: dict[Gtk.ComboBoxText, int] = {}

        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_default_size(480, -1)

        content = self.get_content_area()
        content.set_spacing(6)
        content.set_margin_top(12)
        content.set_margin_bottom(6)
        content.set_margin_start(12)
        content.set_margin_end(12)

        intro = Gtk.Label(
            label=_(
                "The following places will be looked up or created.\n"
                "Choose a type for each new place."
            )
        )
        intro.set_xalign(0.0)
        intro.set_line_wrap(True)
        content.append(intro)

        grid = self._build_grid()
        content.append(grid)

        self.connect("response", self.cb_response)

    def _build_grid(self) -> Gtk.Grid:
        """
        Build and return the table widget showing each place in *parsed*.

        Existing places get read-only labels; new places get a PlaceType
        combo.

        :returns: Populated grid widget.
        :rtype: Gtk.Grid
        """
        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.set_margin_top(8)

        for col, text in enumerate((_("Place Name"), _("Status"), _("Type"))):
            lbl = Gtk.Label(label=f"<b>{text}</b>")
            lbl.set_use_markup(True)
            lbl.set_xalign(0.0)
            grid.attach(lbl, col, 0, 1, 1)

        for row_idx, entry in enumerate(self._parsed, start=1):
            name_lbl = Gtk.Label(label=entry["name"])
            name_lbl.set_xalign(0.0)
            name_lbl.set_hexpand(True)
            grid.attach(name_lbl, 0, row_idx, 1, 1)

            if entry["status"] == "existing":
                status_lbl = Gtk.Label(label=_("Existing"))
                status_lbl.set_xalign(0.0)
                grid.attach(status_lbl, 1, row_idx, 1, 1)

                place = self._db.get_place_from_handle(entry["handle"])
                type_lbl = Gtk.Label(label=str(place.get_type()))
                type_lbl.set_xalign(0.0)
                grid.attach(type_lbl, 2, row_idx, 1, 1)
            else:
                status_lbl = Gtk.Label(label=f"<b>{_('New')}</b>")
                status_lbl.set_use_markup(True)
                status_lbl.set_xalign(0.0)
                grid.attach(status_lbl, 1, row_idx, 1, 1)

                combo = self._make_type_combo()
                grid.attach(combo, 2, row_idx, 1, 1)
                self._combos[combo] = row_idx - 1

        return grid

    def _make_type_combo(self) -> Gtk.ComboBoxText:
        """
        Build and return a ComboBoxText populated with all PlaceType values.

        The first entry ("Unknown") is selected by default.

        :returns: Populated combo widget.
        :rtype: Gtk.ComboBoxText
        """
        combo = Gtk.ComboBoxText()
        for _val, label in _TYPE_ROWS:
            combo.append_text(label)
        combo.set_active(0)
        return combo

    def cb_response(self, _dialog: Gtk.Dialog, response_id: int) -> None:
        """
        Handle the dialog response.

        On ``Gtk.ResponseType.OK``, write the selected :class:`PlaceType`
        back into each ``"new"`` entry's dict so the caller can pass
        *parsed* directly to ``commit_place_hierarchy()``.

        :param _dialog: The dialog emitting the signal (unused).
        :type _dialog: Gtk.Dialog
        :param response_id: The response identifier.
        :type response_id: int
        """
        if response_id != Gtk.ResponseType.OK:
            return
        for combo, idx in self._combos.items():
            active = combo.get_active()
            if active < 0:
                active = 0
            int_val, _label = _TYPE_ROWS[active]
            self._parsed[idx]["place_type"] = PlaceType(int_val)
