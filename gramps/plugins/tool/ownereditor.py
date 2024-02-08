#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Tools/Database Processing/Edit Database Owner Information"""

# -------------------------------------------------------------------------
#
# gnome/gtk
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.config import config
from gramps.gen.utils.config import get_researcher
from gramps.gui.display import display_help
from gramps.gui.widgets import MonitoredEntry
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.plug import tool
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gui.glade import Glade
from gramps.gui.utils import is_right_click

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Tools" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Edit_Database_Owner_Information", "manual")

# -------------------------------------------------------------------------
#
# constants
#
# -------------------------------------------------------------------------
config_keys = (
    "researcher.researcher-name",
    "researcher.researcher-addr",
    "researcher.researcher-locality",
    "researcher.researcher-city",
    "researcher.researcher-state",
    "researcher.researcher-country",
    "researcher.researcher-postal",
    "researcher.researcher-phone",
    "researcher.researcher-email",
)


# -------------------------------------------------------------------------
#
# OwnerEditor
#
# -------------------------------------------------------------------------
class OwnerEditor(tool.Tool, ManagedWindow):
    """
    Allow editing database owner information.

    Provides a possibility to directly verify and edit the owner data of the
    current database. It also allows copying data from/to the preferences.
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        tool.Tool.__init__(self, dbstate, options_class, name)

        self.display()

    def display(self):
        # get the main window from glade
        topDialog = Glade()

        # set gramps style title for the window
        window = topDialog.toplevel
        self.set_window(
            window, topDialog.get_object("title"), _("Database Owner Editor")
        )
        self.setup_configs("interface.ownereditor", 500, 400)

        # move help button to the left side
        action_area = topDialog.get_object("action_area")
        help_button = topDialog.get_object("help_button")
        action_area.set_child_secondary(help_button, True)

        # connect signals
        topDialog.connect_signals(
            {
                "on_ok_button_clicked": self.on_ok_button_clicked,
                "on_cancel_button_clicked": self.close,
                "on_help_button_clicked": self.on_help_button_clicked,
                "on_eventbox_button_press_event": self.on_button_press_event,
                "on_menu_activate": self.on_menu_activate,
            }
        )

        # fetch the popup menu
        self.menu = topDialog.get_object("popup_menu")
        self.track_ref_for_deletion("menu")

        # topDialog.connect_signals({"on_menu_activate": self.on_menu_activate})

        # get current db owner and attach it to the entries of the window
        self.owner = self.db.get_researcher()

        self.entries = []
        entry = [
            ("name", self.owner.set_name, self.owner.get_name),
            ("address", self.owner.set_address, self.owner.get_address),
            ("locality", self.owner.set_locality, self.owner.get_locality),
            ("city", self.owner.set_city, self.owner.get_city),
            ("state", self.owner.set_state, self.owner.get_state),
            ("country", self.owner.set_country, self.owner.get_country),
            ("zip", self.owner.set_postal_code, self.owner.get_postal_code),
            ("phone", self.owner.set_phone, self.owner.get_phone),
            ("email", self.owner.set_email, self.owner.get_email),
        ]

        for name, set_fn, get_fn in entry:
            self.entries.append(
                MonitoredEntry(
                    topDialog.get_object(name), set_fn, get_fn, self.db.readonly
                )
            )
        # ok, let's see what we've done
        self.show()

    def on_ok_button_clicked(self, obj):
        """Update the current db's owner information from editor"""
        self.db.set_researcher(self.owner)
        self.menu.destroy()
        self.close()

    def on_help_button_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def on_button_press_event(self, obj, event):
        """Shows popup-menu for db <-> preferences copying"""
        if is_right_click(event):
            self.menu.popup_at_pointer(event)

    def build_menu_names(self, obj):
        return (_("Main window"), _("Edit database owner information"))

    def on_menu_activate(self, menuitem):
        """Copies the owner information from/to the preferences"""
        if menuitem.props.name == "copy_from_preferences_to_db":
            self.owner.set_from(get_researcher())
            for entry in self.entries:
                entry.update()

        elif menuitem.props.name == "copy_from_db_to_preferences":
            for i in range(len(config_keys)):
                config.set(config_keys[i], self.owner.get()[i])

    def clean_up(self):
        self.menu.destroy()


# -------------------------------------------------------------------------
#
# OwnerEditorOptions (None at the moment)
#
# -------------------------------------------------------------------------
class OwnerEditorOptions(tool.ToolOptions):
    """Defines options and provides handling interface."""

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
