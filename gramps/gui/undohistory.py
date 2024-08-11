#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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

# Written by Alex Roitman

# ------------------------------------------------------------------------
#
# standard python modules
#
# ------------------------------------------------------------------------
import time
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from itertools import chain

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .dialog import QuestionDialog
from .managedwindow import ManagedWindow
from .display import display_help
from gramps.gen.const import URL_MANUAL_PAGE

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Keybindings" % URL_MANUAL_PAGE
WIKI_HELP_SEC = "11"


# -------------------------------------------------------------------------
#
# UndoHistory class
#
# -------------------------------------------------------------------------
class UndoHistory(ManagedWindow):
    """
    The UndoHistory provides a list view with all the editing
    steps available for undo/redo. Selecting a line in the list
    will revert/advance to the appropriate step in editing history.
    """

    def __init__(self, dbstate, uistate):
        self.title = _("Undo History")
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.db = dbstate.db
        self.undodb = self.db.undodb
        self.dbstate = dbstate

        window = Gtk.Dialog(
            title="", transient_for=uistate.window, destroy_with_parent=True
        )

        self.help_button = window.add_button(_("_Help"), Gtk.ResponseType.HELP)
        self.undo_button = window.add_button(_("_Undo"), Gtk.ResponseType.REJECT)
        self.redo_button = window.add_button(_("_Redo"), Gtk.ResponseType.ACCEPT)
        self.clear_button = window.add_button(_("_Clear"), Gtk.ResponseType.APPLY)
        self.close_button = window.add_button(_("_Close"), Gtk.ResponseType.CLOSE)

        self.set_window(window, None, self.title)
        self.setup_configs("interface.undohistory", 500, 200)
        self.window.connect("response", self._response)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.tree = Gtk.TreeView()
        self.model = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        self.selection = self.tree.get_selection()

        self.renderer = Gtk.CellRendererText()
        self.tree.set_model(self.model)
        # self.tree.append_column(
        # Gtk.TreeViewColumn(_('Original time'), self.renderer,
        # text=0, foreground=2, background=3))
        # self.tree.append_column(
        # Gtk.TreeViewColumn(_('Action'), self.renderer,
        # text=1, foreground=2, background=3))
        column = Gtk.TreeViewColumn(_("Original time"), self.renderer, text=0)
        column.set_cell_data_func(self.renderer, bug_fix)
        self.tree.append_column(column)
        column = Gtk.TreeViewColumn(_("Action"), self.renderer, text=1)
        column.set_cell_data_func(self.renderer, bug_fix)
        self.tree.append_column(column)

        scrolled_window.add(self.tree)
        self.window.vbox.pack_start(scrolled_window, True, True, 0)

        self.sel_chng_hndlr = self.selection.connect("changed", self._selection_changed)
        self._build_model()
        self._update_ui()

        self.show()

    def _selection_changed(self, obj):
        (model, node) = self.selection.get_selected()
        if not node or len(self.model) == 1:
            return
        path = self.model.get_path(node).get_indices()
        start = min(path[0], self.undodb.undo_count)
        end = max(path[0], self.undodb.undo_count)

        self._paint_rows(0, len(self.model) - 1, False)
        self._paint_rows(start, end, True)

        if path[0] < self.undodb.undo_count:
            # This transaction is an undo candidate
            self.redo_button.set_sensitive(False)
            self.undo_button.set_sensitive(self.undodb.undo_count)

        else:  # path[0] >= self.undodb.undo_count:
            # This transaction is an redo candidate
            self.undo_button.set_sensitive(False)
            self.redo_button.set_sensitive(self.undodb.redo_count)

    def _paint_rows(self, start, end, selected=False):
        if selected:
            (fg, bg) = get_colors(self.tree, Gtk.StateFlags.SELECTED)
        else:
            fg = bg = ""

        for idx in range(start, end + 1):
            the_iter = self.model.get_iter((idx,))
            self.model.set(the_iter, 2, fg)
            self.model.set(the_iter, 3, bg)

    def _response(self, obj, response_id):
        if response_id == Gtk.ResponseType.CLOSE:
            self.close(obj)

        elif response_id == Gtk.ResponseType.REJECT:
            # Undo the selected entries
            (model, node) = self.selection.get_selected()
            if not node:
                return
            path = self.model.get_path(node).get_indices()
            nsteps = path[0] - self.undodb.undo_count - 1
            self._move(nsteps or -1)

        elif response_id == Gtk.ResponseType.ACCEPT:
            # Redo the selected entries
            (model, node) = self.selection.get_selected()
            if not node:
                return
            path = self.model.get_path(node).get_indices()
            nsteps = path[0] - self.undodb.undo_count
            self._move(nsteps or 1)

        elif response_id == Gtk.ResponseType.APPLY:
            self._clear_clicked()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            self.close(obj)

        elif response_id == Gtk.ResponseType.HELP:
            display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_menu_names(self, obj):
        return (self.title, None)

    def _clear_clicked(self, obj=None):
        QuestionDialog(
            _("Delete confirmation"),
            _("Are you sure you want to clear the Undo history?"),
            _("Clear"),
            self.clear,
            parent=self.window,
        )

    def clear(self):
        self.undodb.clear()
        self.db.abort_possible = False
        self.update()
        if self.db.undo_callback:
            self.db.undo_callback(None)
        if self.db.redo_callback:
            self.db.redo_callback(None)

    def _move(self, steps=-1):
        if steps == 0:
            return
        func = self.db.undo if steps < 0 else self.db.redo

        for step in range(abs(steps)):
            func(False)
        self.update()

    def _update_ui(self):
        self._paint_rows(0, len(self.model) - 1, False)
        self.undo_button.set_sensitive(self.undodb.undo_count)
        self.redo_button.set_sensitive(self.undodb.redo_count)
        self.clear_button.set_sensitive(
            self.undodb.undo_count or self.undodb.redo_count
        )

    def _build_model(self):
        self.selection.handler_block(self.sel_chng_hndlr)
        self.model.clear()
        fg = bg = None

        if self.undodb.undo_history_timestamp:
            if self.db.abort_possible:
                mod_text = _("Database opened")
            else:
                mod_text = _("History cleared")
            time_text = time.ctime(self.undodb.undo_history_timestamp)
            self.model.append(row=[time_text, mod_text, fg, bg])

        # Add the undo and redo queues to the model
        for txn in chain(self.undodb.undoq, reversed(self.undodb.redoq)):
            time_text = time.ctime(txn.timestamp)
            mod_text = txn.get_description()
            self.model.append(row=[time_text, mod_text, fg, bg])
        path = (self.undodb.undo_count,)
        self.selection.handler_unblock(self.sel_chng_hndlr)
        self.selection.select_path(path)

    def update(self):
        self._build_model()
        self._update_ui()


def gdk_color_to_str(color):
    """
    Convert a Gdk.Color into a #rrggbb string.
    """
    color_str = "#%02x%02x%02x" % (
        int(color.red * 255),
        int(color.green * 255),
        int(color.blue * 255),
    )
    return color_str


def get_colors(obj, state):
    """
    Return the foreground and background colors for a given state.
    """
    context = obj.get_style_context()
    fg_color = gdk_color_to_str(context.get_color(state))
    bg_color = gdk_color_to_str(context.get_background_color(state))
    return (fg_color, bg_color)


def bug_fix(column, renderer, model, iter_, data):
    """
    Cell data function to set the column colors.

    There is a bug in pygobject which prevents us from setting a value to
    None using the TreeModel set_value method.  Instead we set it to an empty
    string and convert it to None here.
    """
    fg_color = model.get_value(iter_, 2)
    if fg_color == "":
        fg_color = None
    renderer.set_property("foreground", fg_color)

    bg_color = model.get_value(iter_, 3)
    if bg_color == "":
        bg_color = None
    renderer.set_property("background", bg_color)
