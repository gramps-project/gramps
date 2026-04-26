#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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
from gramps.gen.lib import Source
from ..views.treemodels import SourceModel
from .baseselector import BaseSelector

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# SelectSource
#
# -------------------------------------------------------------------------
class SelectSource(BaseSelector):
    def _local_init(self) -> None:
        """
        Perform local initialisation for this class.
        """
        self.setup_configs("interface.source-sel", 600, 450)
        self.enable_new_button()

    def cb_new_button_clicked(self, obj: Gtk.Button) -> None:
        """
        Open the Edit Source dialog to create a new source.

        On save the tree is rebuilt and the new source is selected so
        the user can confirm with OK without closing the selector first.

        :param obj: The 'New' button that was clicked.
        :type obj: Gtk.Button
        """
        from gramps.gui.editors import EditSource

        try:
            EditSource(
                self.dbstate,
                self.uistate,
                self.track,
                Source(),
                self.cb_after_new_saved,
            )
        except WindowActiveError:
            pass

    def cb_after_new_saved(self, source: Source) -> None:
        """
        Rebuild the selector tree and select the newly created source.

        :param source: The newly created Source object.
        :type source: Source
        """
        self.build_tree()
        self.goto_handle(source.get_handle())

    def get_window_title(self) -> str:
        """
        Return the window title for this selector.

        :returns: Translated window title.
        :rtype: str
        """
        return _("Select Source")

    def get_model_class(self) -> type:
        """
        Return the tree model class used to populate the selector.

        :returns: SourceModel class.
        :rtype: type
        """
        return SourceModel

    def get_column_titles(self) -> list:
        """
        Return column definitions for the selector tree view.

        :returns: List of (header, width, type, model_column) tuples.
        :rtype: list
        """
        return [
            (_("Title"), 350, BaseSelector.TEXT, 0),
            (_("Abbreviation"), 100, BaseSelector.TEXT, 3),
            (_("Author"), 200, BaseSelector.TEXT, 2),
            (_("ID"), 75, BaseSelector.TEXT, 1),
            (_("Last Change"), 150, BaseSelector.TEXT, 7),
        ]

    def get_from_handle_func(self) -> object:
        """
        Return the database function for retrieving a source by handle.

        :returns: Callable that takes a handle and returns a Source.
        :rtype: callable
        """
        return self.db.get_source_from_handle

    def get_config_name(self) -> str:
        """
        Return the config key used to persist column widths and positions.

        :returns: Module name used as config key.
        :rtype: str
        """
        return __name__

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _("Select_Source_selector", "manual")
