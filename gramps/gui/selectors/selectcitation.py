#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006 Donald N. Allingham
#               2009 Gary Burton
# Copyright (C) 2011       Tim G L Lyons, Nick Hall
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

"""
SelectCitation class for Gramps.
"""

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
from gramps.gen.lib import Citation, Source
from ..views.treemodels import CitationTreeModel
from .baseselector import BaseSelector

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# SelectCitation
#
# -------------------------------------------------------------------------
class SelectCitation(BaseSelector):
    def _local_init(self) -> None:
        """
        Perform local initialisation for this class.
        """
        self.setup_configs("interface.source-sel", 600, 450)
        self.enable_new_button()

    def cb_new_button_clicked(self, obj: Gtk.Button) -> None:
        """
        Ask the user whether to create a new Source or Citation, then
        open the appropriate editor.

        Citations are children of Sources, so the user must choose which
        kind of object to create.  After a successful save the tree is
        rebuilt and the new object is selected.

        :param obj: The 'New' button that was clicked.
        :type obj: Gtk.Button
        """
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=_("What would you like to create?"),
        )
        dialog.add_button(_("New _Source"), 1)
        dialog.add_button(_("New _Citation"), 2)
        dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        response = dialog.run()
        dialog.destroy()
        if response == 1:
            self._new_source()
        elif response == 2:
            self._new_citation()

    def _new_source(self) -> None:
        """
        Open the Edit Source dialog to create a new source.
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

    def _new_citation(self) -> None:
        """
        Open the Edit Citation dialog to create a new citation.
        """
        from gramps.gui.editors import EditCitation

        try:
            EditCitation(
                self.dbstate,
                self.uistate,
                self.track,
                Citation(),
                callback=self.cb_after_new_saved,
            )
        except WindowActiveError:
            pass

    def cb_after_new_saved(self, obj: Source | Citation) -> None:
        """
        Rebuild the selector tree and select the newly created object.

        :param obj: The newly created Source or Citation object.
        :type obj: Source | Citation
        """
        self.build_tree()
        self.goto_handle(obj.get_handle())

    def get_window_title(self) -> str:
        """
        Return the window title for this selector.

        :returns: Translated window title.
        :rtype: str
        """
        return _("Select Source or Citation")

    def get_model_class(self) -> type:
        """
        Return the tree model class used to populate the selector.

        :returns: CitationTreeModel class.
        :rtype: type
        """
        return CitationTreeModel

    def get_column_titles(self) -> list:
        """
        Return column definitions for the selector tree view.

        :returns: List of (header, width, type, model_column) tuples.
        :rtype: list
        """
        return [
            (_("Source: Title or Citation: Volume/Page"), 350, BaseSelector.TEXT, 0),
            (_("Abbreviation"), 100, BaseSelector.TEXT, 8),
            (_("ID"), 75, BaseSelector.TEXT, 1),
            (_("Last Change"), 150, BaseSelector.TEXT, 6),
        ]

    def get_from_handle_func(self) -> object:
        """
        Return the function used to retrieve a Source or Citation by handle.

        :returns: Callable that takes a handle and returns a Source or Citation.
        :rtype: callable
        """
        return self.get_source_or_citation

    def get_source_or_citation(self, handle: str) -> Source | Citation:
        """
        Return the Source or Citation object for the given handle.

        :param handle: The handle to look up.
        :type handle: str
        :returns: The Source or Citation identified by *handle*.
        :rtype: Source | Citation
        """
        if self.db.has_source_handle(handle):
            return self.db.get_source_from_handle(handle)
        else:
            return self.db.get_citation_from_handle(handle)

    def get_config_name(self) -> str:
        """
        Return the config key used to persist column widths and positions.

        :returns: Module name used as config key.
        :rtype: str
        """
        return __name__

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _("Select_Source_or_Citation_selector", "manual")
