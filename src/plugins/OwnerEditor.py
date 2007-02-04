#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id:

"Database Processing/Edit database owner information"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Config
import GrampsCfg
import GrampsDisplay
from GrampsWidgets import MonitoredEntry
import ManagedWindow
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
config_keys = (
    Config.RESEARCHER_NAME,
    Config.RESEARCHER_ADDR,
    Config.RESEARCHER_CITY,
    Config.RESEARCHER_STATE,
    Config.RESEARCHER_COUNTRY,
    Config.RESEARCHER_POSTAL,
    Config.RESEARCHER_PHONE,
    Config.RESEARCHER_EMAIL,
)

#-------------------------------------------------------------------------
#
# OwnerEditor
#
#-------------------------------------------------------------------------
class OwnerEditor(Tool.Tool, ManagedWindow.ManagedWindow):
    """
    Allow editing database owner information.

    Provides a possibility to direcly verify and edit the owner data of the
    current database. It also allows copying data from/to the preferences.
    """
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
        Tool.Tool.__init__(self, dbstate, options_class, name)
       
        self.display()

    def display(self):
        base = os.path.dirname(__file__)
        glade_file = os.path.join(base, "ownereditor.glade")

        # get the main window from glade
        top_xml = gtk.glade.XML(glade_file, "top", "gramps")

        # set gramps style title for the window
        window = top_xml.get_widget("top")
        self.set_window(window,
                        top_xml.get_widget("title"),
                        _("Database owner editor"))

        # move help button to the left side
        action_area = top_xml.get_widget("action_area")
        help_button = top_xml.get_widget("help_button")
        action_area.set_child_secondary(help_button, True)
        
        # connect signals
        top_xml.signal_autoconnect({
            "on_ok_button_clicked": self.on_ok_button_clicked,
            "on_cancel_button_clicked": self.close,
            "on_help_button_clicked": self.on_help_button_clicked,
            "on_eventbox_button_press_event": self.on_button_press_event,
        })

        # fetch the popup menu
        popup_xml = gtk.glade.XML(glade_file, "popup-menu", "gramps")
        self.menu = popup_xml.get_widget("popup-menu")
        popup_xml.signal_connect("on_menu_activate", self.on_menu_activate)

        # get current db owner and attach it to the entries of the window
        self.owner = self.db.get_researcher()
        
        self.entries = []
        entry = [
            ("entry1", self.owner.set_name, self.owner.get_name),
            ("entry2", self.owner.set_address, self.owner.get_address),
            ("entry3", self.owner.set_city, self.owner.get_city),
            ("entry4", self.owner.set_state, self.owner.get_state),
            ("entry5", self.owner.set_country, self.owner.get_country),
            ("entry6", self.owner.set_postal_code, self.owner.get_postal_code),
            ("entry7", self.owner.set_phone, self.owner.get_phone),
            ("entry8", self.owner.set_email, self.owner.get_email),
        ]

        for (name,set_fn,get_fn) in entry:
            self.entries.append(MonitoredEntry(top_xml.get_widget(name),
                                               set_fn,
                                               get_fn,
                                               self.db.readonly))
        # ok, let's see what we've done
        self.show()

    def on_ok_button_clicked(self, obj):
        """Update the current db's owner information from editor"""
        self.db.set_researcher(self.owner)
        self.close()

    def on_help_button_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-db')

    def on_button_press_event(self, obj, event):
        """Shows popup-menu for db <-> preferences copying"""
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            self.menu.popup(None,None,None,0,0)

    def on_menu_activate(self, menuitem):
        """Copies the owner information from/to the preferences"""
        if menuitem.name == 'copy_from_preferences_to_db':
            self.owner.set(*GrampsCfg.get_researcher().get())
            for entry in self.entries:
                entry.update()
                
        elif menuitem.name == 'copy_from_db_to_preferences':
            for i in range(len(config_keys)):
                Config.set(config_keys[i], self.owner.get()[i])
        
#-------------------------------------------------------------------------
#
# OwnerEditorOptions (None at the moment)
#
#-------------------------------------------------------------------------
class OwnerEditorOptions(Tool.ToolOptions):
    """Defines options and provides handling interface."""
    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
# Register the plugin tool to plugin manager
#
#-------------------------------------------------------------------------
register_tool(
    name = 'editowner',
    category = Tool.TOOL_DBPROC,
    tool_class = OwnerEditor,
    options_class = OwnerEditorOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Edit database owner information"),
    status = _("Beta"),
    author_name = "Zsolt Foldvari",
    author_email = "zfoldvar@users.sourceforge.net",
    description = _("Allow editing database owner information.")
)
