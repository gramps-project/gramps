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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Place
from ..editors import EditPlace
from ..views.treemodels.placemodel import PlaceTreeModel
from .baseselector import BaseSelector

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
        self.enable_new_button()

    def cb_new_button_clicked(self, obj: Gtk.Button) -> None:
        """
        Open the Edit Place dialog to create a new place.

        On save the tree is rebuilt and the new place is selected so
        the user can confirm with OK without closing the selector first.

        :param obj: The 'New' button that was clicked.
        :type obj: Gtk.Button
        """
        try:
            EditPlace(
                self.dbstate,
                self.uistate,
                self.track,
                Place(),
                self.cb_after_new_saved,
            )
        except WindowActiveError:
            pass

    def cb_after_new_saved(self, place: Place) -> None:
        """
        Rebuild the selector tree and select the newly created place.

        :param place: The newly created Place object.
        :type place: Place
        """
        handle = place.get_handle()
        self.build_tree()
        while Gtk.events_pending():
            Gtk.main_iteration()
        self.goto_handle(handle)
        # goto_handle expands parent rows then immediately calls
        # scroll_to_cell before GTK finishes the expansion.  Flush
        # events so the rows are realised, then scroll again.
        while Gtk.events_pending():
            Gtk.main_iteration()
        if self.model and self.tree:
            iter_ = self.model.get_iter_from_handle(handle)
            if iter_:
                self.tree.scroll_to_cell(self.model.get_path(iter_), None, True, 0.5, 0)

    def get_window_title(self) -> str:
        """
        Return the window title for this selector.

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
        column that includes alternate names as well as the primary name.
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
