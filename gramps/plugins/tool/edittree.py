#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2022       Christopher Horn
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

"""Tools/Database Processing/Edit Tree Information"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os
from copy import copy

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.recentfiles import rename_filename
from gramps.gui.dialog import ErrorDialog
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.plug import tool
from gramps.gui.widgets import MonitoredEntry

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Tools" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Edit_Tree_Information", "manual")


# -------------------------------------------------------------------------
#
# TreeEditor
#
# -------------------------------------------------------------------------
class TreeEditor(tool.Tool, ManagedWindow):
    """
    Enables editing of tree metadata like copyright and description.
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        tool.Tool.__init__(self, dbstate, options_class, name)
        self.dbstate = dbstate
        self.db.refresh_cached_tree_name()
        self.tree = self.db.get_tree()
        self.edit = copy(self.tree)
        self.display()

    def display(self):
        """
        Display the edit dialog.
        """
        top_dialog = Glade()

        # Setup window
        window = top_dialog.toplevel
        self.set_window(
            window,
            top_dialog.get_object("title"),
            _("Tree Information Editor"),
        )
        self.setup_configs("interface.edit_tree", 500, 400)

        # Move help button to the left side
        action_area = top_dialog.get_object("action_area")
        help_button = top_dialog.get_object("help_button")
        action_area.set_child_secondary(help_button, True)

        # Connect signals
        top_dialog.connect_signals(
            {
                "on_ok_button_clicked": self.on_ok_button_clicked,
                "on_cancel_button_clicked": self.close,
                "on_help_button_clicked": on_help_button_clicked,
            }
        )

        # Setup inputs
        self.entries = []
        entry = [
            ("name", self.edit.set_name, self.edit.get_name),
            (
                "description",
                self.edit.set_description,
                self.edit.get_description,
            ),
            ("copyright", self.edit.set_copyright, self.edit.get_copyright),
            ("license", self.edit.set_license, self.edit.get_license),
            (
                "contributors",
                self.edit.set_contributors,
                self.edit.get_contributors,
            ),
        ]
        for (name, set_fn, get_fn) in entry:
            self.entries.append(
                MonitoredEntry(
                    top_dialog.get_object(name),
                    set_fn,
                    get_fn,
                    self.db.readonly,
                )
            )
        self.show()

    def build_menu_names(self, obj):
        """
        Return the menu names.
        """
        return (_("Main window"), _("Edit tree information"))

    def on_ok_button_clicked(self, _cb_obj):
        """
        Save the changes.
        """
        name = self.edit.get_name().strip()
        if name != self.tree.get_name():
            if self.rename_database():
                self.db.refresh_cached_tree_name()
                self.uistate.window.set_title(name)
        else:
            if self.edit != self.tree:
                self.db.set_tree(self.edit)
        self.close()

    def rename_database(self):
        """
        Renames the database by writing the new value to the name.txt file
        """
        name = self.edit.get_name().strip()
        dbman = CLIDbManager(self.dbstate)
        for (tree_name, dummy_dir_name) in dbman.family_tree_list():
            if name == tree_name:
                ErrorDialog(
                    _("Could not rename the Family Tree."),
                    _("Family Tree already exists, choose a unique name."),
                    parent=self,
                )
                return False

        filename = os.path.join(self.db.get_save_path(), "name.txt")
        old_text, new_text = dbman.rename_database(filename, name)
        if old_text is not None:
            rename_filename(old_text, new_text)
        return True


def on_help_button_clicked(_cb_obj):
    """
    Display the relevant portion of Gramps manual
    """
    display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)


# -------------------------------------------------------------------------
#
# TreeEditorOptions (None at the moment)
#
# -------------------------------------------------------------------------
class TreeEditorOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
