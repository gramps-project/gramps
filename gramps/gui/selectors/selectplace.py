#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Nick Hall
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

_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_SECT2
from gramps.gen.db import DbTxn
from ..views.treemodels.placemodel import PlaceTreeModel
from .baseselector import BaseSelector
from .quickplacedialog import QuickPlaceDialog
from .quickplaceparser import commit_place_hierarchy, parse_place_hierarchy

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# SelectPlace
#
# -------------------------------------------------------------------------
class SelectPlace(BaseSelector):
    def _local_init(self) -> None:
        """
        Perform local initialisation for this class.
        """
        self.setup_configs("interface.place-sel", 600, 450)
        self._build_quick_add_bar()

    def _build_quick_add_bar(self) -> None:
        """
        Add a 'Quick Add' entry bar below the place tree.

        The bar contains a label, a text entry with a placeholder hint,
        and a button.  Both the entry (on Enter) and the button trigger
        :meth:`cb_quick_add`.
        """
        vbox = self.glade.get_object("select_person_vbox")

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bar.set_margin_top(4)
        bar.set_margin_bottom(4)
        bar.set_margin_start(6)
        bar.set_margin_end(6)

        label = Gtk.Label(label=_("Quick Add:"))
        bar.pack_start(label, False, False, 0)

        self._quick_entry = Gtk.Entry()
        self._quick_entry.set_placeholder_text(_("Country, Region, City"))
        self._quick_entry.set_hexpand(True)
        self._quick_entry.connect("activate", self.cb_quick_add)
        bar.pack_start(self._quick_entry, True, True, 0)

        btn = Gtk.Button(label=_("Quick Add"))
        btn.connect("clicked", self.cb_quick_add)
        bar.pack_start(btn, False, False, 0)

        bar.show_all()
        vbox.pack_end(bar, False, False, 0)

    def cb_quick_add(self, _obj: Gtk.Widget) -> None:
        """
        Parse the quick-entry text, confirm with the user, then commit.

        Reads the text entry, calls
        :func:`~gramps.gui.selectors.quickplaceparser.parse_place_hierarchy`
        to resolve existing places, shows :class:`QuickPlaceDialog` for
        confirmation, then commits all new places in a single transaction,
        rebuilds the tree, and scrolls to the newly created leaf place.

        :param _obj: The widget that triggered the callback (unused).
        :type _obj: Gtk.Widget
        """
        text = self._quick_entry.get_text().strip()
        if not text:
            return

        parsed = parse_place_hierarchy(self.db, text)
        if not parsed:
            return

        dlg = QuickPlaceDialog(self.db, parsed, parent=self.window)
        response = dlg.run()
        dlg.destroy()

        if response != Gtk.ResponseType.OK:
            return

        leaf_name = parsed[0]["name"]
        with DbTxn(_("Quick add place: %s") % leaf_name, self.db) as trans:
            commit_place_hierarchy(self.db, parsed, trans)

        # Scroll to the most-specific newly created place (last new entry);
        # fall back to the last (most-specific) entry if all already existed.
        new_handle = (
            next((e["handle"] for e in reversed(parsed) if e["status"] == "new"), None)
            or parsed[-1]["handle"]
        )

        self._quick_entry.set_text("")
        self.build_tree()
        while Gtk.events_pending():
            Gtk.main_iteration()
        if new_handle:
            self.goto_handle(new_handle)
            # goto_handle expands parent rows and immediately calls
            # scroll_to_cell before GTK finishes the expansion.  Flush
            # events so the rows are realised, then scroll again.
            while Gtk.events_pending():
                Gtk.main_iteration()
            if self.model and self.tree:
                iter_ = self.model.get_iter_from_handle(new_handle)
                if iter_:
                    self.tree.scroll_to_cell(
                        self.model.get_path(iter_), None, True, 0.5, 0
                    )

    def get_window_title(self) -> str:
        """
        Return the window title for the Select Place dialog.

        :returns: Translated window title.
        :rtype: str
        """
        return _("Select Place")

    def get_model_class(self) -> type:
        """
        Return the tree model class used to populate the selector.

        :returns: PlaceTreeModel class.
        :rtype: type
        """
        return PlaceTreeModel

    def get_column_titles(self) -> list:
        """
        Return column definitions for the selector tree view.

        :returns: List of (header, width, type, model_column) tuples.
        :rtype: list
        """
        return [
            (_("Name"), 200, BaseSelector.TEXT, 0),
            (_("ID"), 75, BaseSelector.TEXT, 1),
            (_("Type"), 100, BaseSelector.TEXT, 3),
            (_("Title"), 300, BaseSelector.TEXT, 2),
            (_("Last Change"), 150, BaseSelector.TEXT, 9),
        ]

    def get_from_handle_func(self) -> object:
        """
        Return the database function for retrieving a place by handle.

        :returns: Callable that takes a handle and returns a Place.
        :rtype: callable
        """
        return self.db.get_place_from_handle

    def setup_searches(self) -> None:
        """
        Build the default searches and add them to the search bar.

        Overrides the base class method to use the hidden COL_SEARCH (11)
        column, which includes alternate names as well as the primary name.
        """
        cols = [
            (pair[3], pair[1] if pair[1] else 11, pair[0] in self.exact_search())
            for pair in self.column_order()
            if pair[0]
        ]
        self.search_bar.setup_searches(cols)

    def get_config_name(self) -> str:
        """
        Return the config key used to persist column widths and positions.

        :returns: Module name used as config key.
        :rtype: str
        """
        return __name__

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _("Select_Place_selector", "manual")
