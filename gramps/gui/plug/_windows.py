#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
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
# Python modules
#
# -------------------------------------------------------------------------
import traceback
import os
from html import escape
import threading
import sys
import subprocess
import importlib

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".gui.plug")

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored
from ..managedwindow import ManagedWindow
from gramps.gen.errors import UnavailableError, WindowActiveError
from gramps.gen.plug import (
    PluginRegister,
    PTYPE_STR,
    load_addon_file,
    AUDIENCETEXT,
    STATUSTEXT,
)
from ..utils import open_file_with_default_application
from ..pluginmanager import GuiPluginManager
from . import tool
from ._guioptions import add_gui_options
from ..dialog import InfoDialog, OkDialog, QuestionDialog2
from ..editors import EditPerson
from ..glade import Glade
from ..listmodel import ListModel, NOSORT, TOGGLE
from gramps.gen.const import URL_WIKISTRING, USER_HOME, WIKI_EXTRAPLUGINS_RAWDATA, COLON
from gramps.gen.config import config
from ..widgets.progressdialog import LongOpStatus, ProgressMonitor, GtkProgressDialog

from gramps.gen.plug.utils import get_all_addons, available_updates
from ..display import display_help, display_url
from gramps.gui.widgets import BasicLabel, SimpleButton
from gramps.gen.utils.requirements import Requirements
from gramps.gen.const import USER_PLUGINS, LIB_PATH
from gramps.gen.constfunc import win


def display_message(message):
    """
    A default callback for displaying messages.
    """
    print(message)


RELOAD = 777  # A custom Gtk response_type for the Reload button


# -------------------------------------------------------------------------
#
# GetAddons
#
# -------------------------------------------------------------------------
class GetAddons(threading.Thread):
    """
    A class for retrieving a list of addons as a background task.
    """

    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.addon_list = []
        self.__pmgr = GuiPluginManager.get_instance()

    def emit_signal(self):
        self.callback(self.addon_list)

    def run(self):
        self.addon_list = self.__get_addon_list()
        GLib.idle_add(self.emit_signal)

    def __get_addon_list(self):
        return get_all_addons()


# -------------------------------------------------------------------------
#
# ProjectRow
#
# -------------------------------------------------------------------------
class ProjectRow(Gtk.ListBoxRow):
    """
    A class to display an external addons repository.
    """

    def __init__(self, manager, project):
        Gtk.ListBoxRow.__init__(self)
        self.manager = manager
        self.project = project

        hbox = Gtk.Box()
        hbox.set_spacing(12)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_spacing(6)

        self.check = Gtk.CheckButton()

        hbox.pack_start(self.check, False, False, 0)
        hbox.pack_start(vbox, True, True, 0)

        self.name = Gtk.Label()
        self.name.set_use_markup(True)
        self.name.set_halign(Gtk.Align.START)
        self.url = Gtk.Label()
        self.url.set_halign(Gtk.Align.START)
        vbox.pack_start(self.name, False, False, 0)
        vbox.pack_start(self.url, False, False, 0)

        self.add(hbox)
        self.show_all()

        self.update()
        self.check.connect("toggled", self.__check_toggled)

    def __check_toggled(self, check):
        self.project[2] = check.get_active()
        projects = [row.project for row in self.manager.project_list]
        config.set("behavior.addons-projects", projects)
        self.manager.refresh()

    def update(self):
        """
        Update the row when the project data has been updated.
        """
        text = self.project[0]
        self.name.set_markup('<span weight="bold">%s</span>' % text)
        self.url.set_text(self.project[1])
        self.check.set_active(self.project[2])


# -------------------------------------------------------------------------
#
# AddonManager
#
# -------------------------------------------------------------------------
class AddonRow(Gtk.ListBoxRow):
    """
    A class representing an addon in the Addon Manager.
    """

    def __init__(self, manager, addon, req, window):
        Gtk.ListBoxRow.__init__(self)
        self.manager = manager
        self.addon = addon
        self.req = req
        self.window = window

        context = self.get_style_context()
        context.add_class("addon-row")

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.set_spacing(6)
        self.__build_gui(self.vbox, self.addon, self.req)
        self.add(self.vbox)
        self.show_all()

    def __build_gui(self, vbox, addon, req):
        """
        Build the GUI for this addon row.
        """
        for child in vbox.get_children():
            vbox.remove(child)

        text = escape(addon["n"])
        title = Gtk.Label()
        title.set_text('<span size="larger" weight="bold">%s</span>' % text)
        title.set_use_markup(True)
        title.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(title, False, False, 0)

        hbox = Gtk.Box()
        hbox.set_spacing(6)
        lozenge = self.__create_lozenge(_("Project"), addon["_p"])
        hbox.pack_start(lozenge, False, False, 0)
        lozenge = self.__create_lozenge(_("Type"), PTYPE_STR[addon["t"]])
        hbox.pack_start(lozenge, False, False, 0)
        lozenge = self.__create_lozenge(_("Audience"), AUDIENCETEXT[addon["a"]])
        hbox.pack_start(lozenge, False, False, 0)
        lozenge = self.__create_lozenge(_("Status"), STATUSTEXT[addon["s"]])
        hbox.pack_start(lozenge, False, False, 0)
        lozenge = self.__create_lozenge(_("Version"), addon["v"])
        hbox.pack_start(lozenge, False, False, 0)
        if "_v" in addon:
            lozenge = self.__create_lozenge(_("Installed version"), addon["_v"])
            hbox.pack_end(lozenge, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)

        text = addon["d"]
        descr = Gtk.Label()
        descr.set_text(text)
        descr.set_halign(Gtk.Align.START)
        descr.set_hexpand(False)
        descr.set_line_wrap(True)
        descr.set_line_wrap_mode(Pango.WrapMode.WORD)
        vbox.pack_start(descr, False, False, 0)

        bb = Gtk.Box()
        bb.set_spacing(6)

        if "_v" not in addon and req.check_addon(addon, install=True):
            b1 = Gtk.Button(label=_("Install"))
            b1.set_label(_("Install"))
            b1.connect("clicked", self.__on_install_clicked, addon)
            bb.pack_end(b1, False, False, 0)

        if addon["h"]:
            b2 = Gtk.Button(label=_("Wiki"))
            b2.connect("clicked", self.__on_wiki_clicked, addon["h"])
            bb.pack_start(b2, False, False, 0)

        if not req.check_addon(addon):
            b3 = Gtk.Button(label=_("Requires"))
            b3.connect("clicked", self.__on_requires_clicked, addon)
            bb.pack_start(b3, False, False, 0)

        if "_v" in addon and addon["_v"] != addon["v"]:
            b4 = Gtk.Button(label=_("Update"))
            b4.connect("clicked", self.__on_update_clicked, addon)
            bb.pack_end(b4, False, False, 0)

        vbox.pack_start(bb, False, False, 0)
        vbox.show_all()

    def __on_install_clicked(self, button, addon):
        """
        Install the addon and possibly some required python modules.
        """
        # Install required modules
        for package in self.req.install(addon):
            try:
                subprocess.check_output(
                    [
                        "pip.exe" if win() else "pip",
                        "install",
                        "--target",
                        LIB_PATH,
                        package,
                    ],
                    stderr=subprocess.STDOUT,
                )
            except subprocess.CalledProcessError as err:
                button.set_sensitive(False)
                InfoDialog(
                    _("Module installation failed"),
                    err.output.decode("utf-8"),
                    parent=self.window,
                )
                return

        # Invalidate the caches to ensure that the new modules will be found.
        importlib.invalidate_caches()

        if not self.req.check_addon(addon):
            InfoDialog(
                _("Module installation failed"),
                _("Gramps was unable to install the required modules"),
                parent=self.window,
            )
            return

        # Install addon
        path = addon["_u"] + "/download/" + addon["z"]
        load_addon_file(path)
        self.manager.install_addon(addon["i"])

        # Refresh this row
        pmgr = GuiPluginManager.get_instance()
        plugin = pmgr.get_plugin(addon["i"])
        if plugin:
            self.addon["_v"] = plugin.version
        self.__build_gui(self.vbox, self.addon, self.req)

    def __on_wiki_clicked(self, button, url):
        """
        Display the wiki page for the addon.
        """
        if url.startswith(("http://", "https://")):
            display_url(url)
        else:
            display_help(url)

    def __on_requires_clicked(self, button, addon):
        """
        Display the requirements for the addon.
        """
        InfoDialog(_("Requirements"), self.req.info(addon), parent=self.window)

    def __on_update_clicked(self, button, addon):
        """
        Update the addon.
        """
        path = addon["_u"] + "/download/" + addon["z"]
        load_addon_file(path)
        self.manager.update_addon(addon["i"])
        self.manager.refresh()

    def __create_lozenge(self, description, text):
        """
        Create a lozenge shaped label to display addon information.
        """
        label = Gtk.Label()
        label.set_tooltip_text(description)
        context = label.get_style_context()
        context.add_class("lozenge")
        label.set_text(text)
        label.set_margin_start(6)
        return label


# -------------------------------------------------------------------------
#
# AddonManager
#
# -------------------------------------------------------------------------
class AddonManager(ManagedWindow):
    """
    A class to allow the user to easily select addons to install.
    """

    def __init__(self, dbstate, uistate, track):
        self.dbstate = dbstate
        self.title = _("Addon Manager")
        ManagedWindow.__init__(self, uistate, [], self)

        self.__pmgr = GuiPluginManager.get_instance()
        self.__preg = PluginRegister.get_instance()
        dialog = Gtk.Dialog(
            title="", transient_for=uistate.window, destroy_with_parent=True
        )
        dialog.add_button(_("Refresh"), RELOAD)
        dialog.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        dialog.add_button(_("_Help"), Gtk.ResponseType.HELP)
        self.set_window(dialog, None, self.title)

        self.req = Requirements()

        self.setup_configs("interface.addonmanager", 750, 400)
        self.window.connect("response", self.__on_dialog_button)

        book = Gtk.Notebook()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_spacing(6)
        vbox.set_margin_start(6)
        vbox.set_margin_end(6)
        vbox.set_margin_top(6)
        vbox.set_margin_bottom(6)

        self.search = Gtk.Entry()
        self.search.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, "system-search"
        )
        self.search.connect("changed", self.__combo_changed)
        vbox.pack_start(self.search, False, False, 0)

        hbox = Gtk.Box()
        hbox.set_spacing(6)
        self.lb = Gtk.ListBox()
        self.lb.set_activate_on_single_click(False)

        label = Gtk.Label(label=_("Filters") + COLON)
        label.set_margin_end(12)
        hbox.pack_start(label, False, False, 0)

        self.addon_combo = Gtk.ComboBoxText()
        self.addon_combo.set_entry_text_column(0)
        self.addon_combo.append_text(_("All addons"))
        self.addon_combo.append_text(_("Not installed"))
        self.addon_combo.append_text(_("Installed"))
        self.addon_combo.append_text(_("Updates"))
        self.addon_combo.set_active(0)
        self.addon_combo.connect("changed", self.__combo_changed)
        hbox.pack_start(self.addon_combo, False, False, 0)

        self.projects = config.get("behavior.addons-projects")
        self.project_combo = Gtk.ComboBoxText()
        self.project_combo.set_entry_text_column(0)
        self.project_combo.connect("changed", self.__combo_changed)
        hbox.pack_start(self.project_combo, False, False, 0)

        type_store = Gtk.ListStore(int, str)
        type_store.append([-1, _("All types")])
        entries = list(PTYPE_STR.items())
        for entry in sorted(entries, key=lambda item: item[1]):
            type_store.append(entry)
        self.type_combo = self.__create_filter_combo(type_store, 0)
        hbox.pack_start(self.type_combo, False, False, 0)

        audience_store = Gtk.ListStore(int, str)
        audience_store.append([-1, _("All audiences")])
        for key, value in AUDIENCETEXT.items():
            audience_store.append([key, value])
        self.audience_combo = self.__create_filter_combo(audience_store, 1)
        hbox.pack_start(self.audience_combo, False, False, 0)

        status_store = Gtk.ListStore(int, str)
        status_store.append([-1, _("All statuses")])
        entries = list(STATUSTEXT.items())
        for entry in sorted(entries, reverse=True):
            status_store.append(entry)
        self.status_combo = self.__create_filter_combo(status_store, 1)
        hbox.pack_start(self.status_combo, False, False, 0)

        clear = Gtk.Button.new_from_icon_name("edit-clear", Gtk.IconSize.BUTTON)
        clear.connect("clicked", self.__clear_filters)
        hbox.pack_start(clear, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.lb)
        vbox.pack_start(sw, True, True, 0)

        book.append_page(vbox, Gtk.Label(label=_("Addons")))

        grid = self.create_settings_panel()
        book.append_page(grid, Gtk.Label(label=_("Settings")))

        grid = self.create_projects_panel()
        book.append_page(grid, Gtk.Label(label=_("Projects")))

        for project in self.projects:
            self.project_list.add(ProjectRow(self, project))
        self.update_project_list()

        self.window.get_content_area().pack_start(book, True, True, 0)

        self.lb.set_sort_func(self.__sort_func)
        self.lb.set_filter_func(self.__filter_func)

        self.show()

        self.refresh()

    def help(self):
        """
        Display the Addon Manager help page.
        """
        display_help(
            "Gramps_5.2_Wiki_Manual_-_Navigation", "Using_the_Addon_Manager..."
        )

    def __create_filter_combo(self, store, default):
        """
        Create a ComboBox for filters.
        """
        combo = Gtk.ComboBox()
        combo.set_model(store)
        combo.set_entry_text_column(1)
        combo.connect("changed", self.__combo_changed)
        combo.set_active(default)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 1)
        return combo

    def update_project_list(self):
        """
        Update the project list after it has been changed.
        """
        self.projects = [row.project for row in self.project_list]
        config.set("behavior.addons-projects", self.projects)

        self.project_combo.remove_all()
        self.project_combo.append_text(_("All projects"))
        for project in self.projects:
            self.project_combo.append_text(project[0])
        self.project_combo.set_active(0)

    def refresh(self):
        """
        Refresh the addons list.
        """
        for child in self.lb.get_children():
            self.lb.remove(child)

        self.__placeholder(_("Loading..."))

        thread = GetAddons(self.load_addons)
        thread.start()

    def update_addon(self, addon_id):
        """
        Update the given addon.
        """
        pdata = self.__preg.get_plugin(addon_id)
        self.__pmgr.reg_plugin_dir(
            pdata.directory, self.dbstate, self.uistate, load_on_reg=True
        )
        pdata = self.__preg.get_plugin(addon_id)
        self.__pmgr.load_plugin(pdata)

    def install_addon(self, addon_id):
        """
        Install the given addon.
        """
        self.__pmgr.reg_plugins(
            USER_PLUGINS, self.dbstate, self.uistate, load_on_reg=True
        )
        pdata = self.__preg.get_plugin(addon_id)
        if pdata is None:
            OkDialog(
                _("Addon Registration Failed"),
                _("The addon will be unavailable in your current configuration."),
                parent=self.window,
            )
            return
        self.__pmgr.load_plugin(pdata)
        self.__pmgr.emit("plugins-reloaded")

    def build_menu_names(self, obj):
        return (self.title, self.title)

    def __placeholder(self, text):
        """
        A placeholder label if no addons are listed.
        """
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>' % text)
        label.set_use_markup(True)
        label.show()
        self.lb.set_placeholder(label)

    def load_addons(self, addon_list):
        """
        Populate the list box.
        """
        for addon in addon_list:
            self.lb.add(AddonRow(self, addon, self.req, self.window))
        self.__placeholder(_("No matching addons found."))

    def __clear_filters(self, combo):
        """
        Reset the filters back to their defaults.
        """
        self.search.set_text("")
        self.type_combo.set_active(0)
        self.addon_combo.set_active(0)
        self.project_combo.set_active(0)
        self.audience_combo.set_active(1)
        self.status_combo.set_active(1)

    def __combo_changed(self, combo):
        """
        Called when a filter is changed.
        """
        self.lb.invalidate_filter()

    def __sort_func(self, row1, row2):
        """
        Sort the addons by name.
        """
        value1 = row1.addon["n"]
        value2 = row2.addon["n"]
        if value1 > value2:
            return 1
        elif value1 < value2:
            return -1
        else:
            return 0

    def __filter_func(self, row):
        """
        Filter the addons list according to the user selection.
        """
        search_text = self.search.get_text()
        addon_text = self.addon_combo.get_active_text()
        project_text = self.project_combo.get_active_text()
        type_iter = self.type_combo.get_active_iter()
        audience_iter = self.audience_combo.get_active_iter()
        status_iter = self.status_combo.get_active_iter()

        if addon_text == _("Not installed"):
            if "_v" in row.addon:
                return False
        if addon_text == _("Installed"):
            if "_v" not in row.addon:
                return False
        if addon_text == _("Updates"):
            if "_v" not in row.addon:
                return False
            if row.addon["v"] == row.addon["_v"]:
                return False
        if project_text != _("All projects"):
            if row.addon["_p"] != project_text:
                return False
        model = self.type_combo.get_model()
        value = model.get_value(type_iter, 0)
        if value != -1 and row.addon["t"] != value:
            return False
        model = self.audience_combo.get_model()
        value = model.get_value(audience_iter, 0)
        if value != -1 and row.addon["a"] != value:
            return False
        model = self.status_combo.get_model()
        value = model.get_value(status_iter, 0)
        if value != -1 and row.addon["s"] != value:
            return False
        if search_text:
            search_text = search_text.lower()
            if (
                search_text not in row.addon["n"].lower()
                and search_text not in row.addon["d"].lower()
                and search_text not in row.addon["i"].lower()
            ):
                return False
        return True

    def __on_dialog_button(self, dialog, response_id):
        """
        Handle a main dialog button click.
        """
        if response_id == Gtk.ResponseType.CLOSE:
            self.close(dialog)
        elif response_id == RELOAD:
            self.refresh()
        elif response_id == Gtk.ResponseType.HELP:
            self.help()

    def create_projects_panel(self):
        """
        Configuration tab with addons projects.
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_spacing(6)
        vbox.set_margin_start(6)
        vbox.set_margin_end(6)
        vbox.set_margin_top(6)
        vbox.set_margin_bottom(6)

        self.project_list = Gtk.ListBox()
        self.project_list.set_activate_on_single_click(False)
        self.project_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.project_list.connect("row-activated", self.__edit_project)
        self.project_list.connect("row-selected", self.__project_selected)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.project_list)
        vbox.pack_start(sw, True, True, 0)

        hbox = Gtk.Box()
        add_btn = SimpleButton("list-add", self.__add_project)
        del_btn = SimpleButton("list-remove", self.__remove_project)
        up_btn = SimpleButton("go-up", self.__move_up)
        down_btn = SimpleButton("go-down", self.__move_down)
        restore_btn = SimpleButton("document-revert", self.__restore_defaults)
        self.buttons = [add_btn, del_btn, up_btn, down_btn, restore_btn]
        for button in self.buttons:
            hbox.pack_start(button, False, False, 0)
        self.buttons[1].set_sensitive(False)
        self.buttons[2].set_sensitive(False)
        self.buttons[3].set_sensitive(False)
        vbox.pack_start(hbox, False, False, 0)

        return vbox

    def create_settings_panel(self):
        """
        Configuration tab with addons settings.
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_spacing(6)
        vbox.set_margin_start(6)
        vbox.set_margin_end(6)
        vbox.set_margin_top(6)
        vbox.set_margin_bottom(6)

        heading1 = Gtk.Label()
        text = _("General")
        heading1.set_text('<span weight="bold">%s</span>' % text)
        heading1.set_use_markup(True)
        heading1.set_halign(Gtk.Align.START)
        vbox.pack_start(heading1, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_margin_start(6)
        grid.set_margin_bottom(12)
        vbox.pack_start(grid, False, False, 0)

        row = 1
        install = Gtk.CheckButton()
        install.set_label(_("Allow Gramps to install required Python modules"))
        active = config.get("behavior.addons-allow-install")
        install.set_active(active)
        install.connect("toggled", self.install_changed)
        grid.attach(install, 1, row, 1, 1)

        heading2 = Gtk.Label()
        text = _("Scheduled update checks")
        heading2.set_text('<span weight="bold">%s</span>' % text)
        heading2.set_use_markup(True)
        heading2.set_halign(Gtk.Align.START)
        vbox.pack_start(heading2, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_margin_start(6)
        vbox.pack_start(grid, False, False, 0)

        # Check for addon updates:
        row = 1
        obox = Gtk.ComboBoxText()
        formats = [
            _("Never"),
            _("Once a month"),
            _("Once a week"),
            _("Once a day"),
            _("Always"),
        ]
        list(map(obox.append_text, formats))
        active = config.get("behavior.check-for-addon-updates")
        obox.set_active(active)
        obox.connect("changed", self.check_for_updates_changed)
        lwidget = BasicLabel(_("%s: ") % _("Check for addon updates"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 1, 1)

        row += 1
        self.whattype_box = Gtk.ComboBoxText()
        formats = [
            _("Updated addons only"),
            _("New addons only"),
            _("New and updated addons"),
        ]
        list(map(self.whattype_box.append_text, formats))
        whattype = config.get("behavior.check-for-addon-update-types")
        if "new" in whattype and "update" in whattype:
            self.whattype_box.set_active(2)
        elif "new" in whattype:
            self.whattype_box.set_active(1)
        elif "update" in whattype:
            self.whattype_box.set_active(0)
        self.whattype_box.connect("changed", self.check_for_type_changed)
        lwidget = BasicLabel(_("%s: ") % _("What to check"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(self.whattype_box, 2, row, 1, 1)

        row += 1
        previous = Gtk.CheckButton()
        previous.set_label(_("Do not ask about previously notified addons"))
        active = config.get("behavior.do-not-show-previously-seen-addon-updates")
        previous.set_active(active)
        previous.connect("toggled", self.previous_changed)
        grid.attach(previous, 1, row, 1, 1)

        row += 1
        button = Gtk.Button(label=_("Check for updated addons now"))
        button.connect("clicked", self.check_for_updates)
        button.set_hexpand(False)
        button.set_halign(Gtk.Align.CENTER)
        grid.attach(button, 1, row, 2, 1)

        return vbox

    def edit_project(self, row):
        """
        Add or edit a project
        """
        if row.project[0] == "":
            title = _("New Project")
        else:
            title = _("Edit Project")
        dialog = Gtk.Dialog(title=title, transient_for=self.window, default_width=600)
        dialog.set_border_width(6)
        dialog.vbox.set_spacing(6)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        label = Gtk.Label(label=_("%s: ") % _("Project name"))
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, 0, 1, 1)
        name = Gtk.Entry()
        name.set_hexpand(True)
        name.set_text(row.project[0])
        name.set_activates_default(True)
        grid.attach(name, 1, 0, 1, 1)
        label = Gtk.Label(label=_("%s: ") % _("URL"))
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, 1, 1, 1)
        url = Gtk.Entry()
        url.set_hexpand(True)
        url.set_text(row.project[1])
        grid.attach(url, 1, 1, 1, 1)
        dialog.vbox.pack_start(grid, True, True, 0)

        dialog.add_buttons(
            _("_Cancel"), Gtk.ResponseType.CANCEL, _("_OK"), Gtk.ResponseType.OK
        )
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.vbox.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            if row.project[0] == "":
                self.project_list.add(row)
            row.project[0] = name.get_text()
            row.project[1] = url.get_text()
            row.update()
            self.update_project_list()
            self.refresh()
        dialog.destroy()

    def __add_project(self, button):
        """
        Add a project
        """
        self.edit_project(ProjectRow(self, ["", "", False]))

    def __remove_project(self, button):
        """
        Remove a project
        """
        row = self.project_list.get_selected_row()
        if row:
            self.project_list.remove(row)
            self.update_project_list()
            self.refresh()

    def __move_up(self, button):
        row = self.project_list.get_selected_row()
        index = row.get_index()
        if index > 1:
            self.project_list.unselect_row(row)
            self.project_list.remove(row)
            self.project_list.insert(row, index - 1)
            self.project_list.select_row(row)
            self.update_project_list()

    def __move_down(self, button):
        row = self.project_list.get_selected_row()
        index = row.get_index()
        if index > 0 and index < len(self.project_list) - 1:
            self.project_list.unselect_row(row)
            self.project_list.remove(row)
            self.project_list.insert(row, index + 1)
            self.project_list.select_row(row)
            self.update_project_list()

    def __project_selected(self, listbox, row):
        if row:
            index = row.get_index()
            if index == 0:
                self.buttons[1].set_sensitive(False)
                self.buttons[2].set_sensitive(False)
                self.buttons[3].set_sensitive(False)
            elif index == 1:
                self.buttons[1].set_sensitive(True)
                self.buttons[2].set_sensitive(False)
                self.buttons[3].set_sensitive(True)
            elif index < len(self.project_list) - 1:
                self.buttons[1].set_sensitive(True)
                self.buttons[2].set_sensitive(True)
                self.buttons[3].set_sensitive(True)
            else:
                self.buttons[1].set_sensitive(True)
                self.buttons[2].set_sensitive(True)
                self.buttons[3].set_sensitive(False)
        else:
            self.buttons[1].set_sensitive(False)
            self.buttons[2].set_sensitive(False)
            self.buttons[3].set_sensitive(False)

    def __restore_defaults(self, button):
        """
        Restore project defaults.
        """
        dlg = QuestionDialog2(
            _("Restore project defaults"),
            _("Are you sure?"),
            _("Yes"),
            _("No"),
            parent=self.window,
        )
        if dlg.run():
            for row in self.project_list.get_children():
                self.project_list.remove(row)
            projects = [["Gramps", config.get("behavior.addons-url"), True]]
            self.project_list.add(ProjectRow(self, projects[0]))
            self.update_project_list()
            self.refresh()

    def __edit_project(self, listbox, row):
        """
        Edit a project
        """
        self.edit_project(row)

    def check_for_updates(self, button):
        try:
            addon_update_list = available_updates()
        except:
            OkDialog(
                _("Checking Addons Failed"),
                _(
                    "The addon repository appears to be unavailable. "
                    "Please try again later."
                ),
                parent=self.window,
            )
            return

        if len(addon_update_list) > 0:
            rescan = UpdateAddons(self.uistate, self.track, addon_update_list).rescan
            self.uistate.viewmanager.do_reg_plugins(
                self.dbstate, self.uistate, rescan=rescan
            )
        else:
            check_types = config.get("behavior.check-for-addon-update-types")
            OkDialog(
                _("There are no available addons of this type"),
                _("Checked for '%s'") % _("' and '").join([_(t) for t in check_types]),
                parent=self.window,
            )

        # List of translated strings used here
        # Dead code for l10n
        _("new"), _("update")

    def check_for_type_changed(self, obj):
        active = obj.get_active()
        if active == 0:  # update
            config.set("behavior.check-for-addon-update-types", ["update"])
        elif active == 1:  # update
            config.set("behavior.check-for-addon-update-types", ["new"])
        elif active == 2:  # update
            config.set("behavior.check-for-addon-update-types", ["update", "new"])

    def check_for_updates_changed(self, obj):
        """
        Save "Check for addon updates" option.
        """
        active = obj.get_active()
        config.set("behavior.check-for-addon-updates", active)

    def previous_changed(self, obj):
        active = obj.get_active()
        config.set("behavior.do-not-show-previously-seen-addon-updates", active)

    def install_changed(self, obj):
        active = obj.get_active()
        config.set("behavior.addons-allow-install", active)


# -------------------------------------------------------------------------
#
# PluginStatus: overview of all plugins
#
# -------------------------------------------------------------------------
class PluginStatus(ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""

    HIDDEN = '<span color="red">%s</span>' % _("Hidden")
    AVAILABLE = '<span weight="bold" color="blue">%s</span>' % _("Visible")

    def __init__(self, dbstate, uistate, track=[]):
        self.dbstate = dbstate
        self.__uistate = uistate
        self.title = _("Plugin Manager")
        ManagedWindow.__init__(self, uistate, track, self.__class__)

        self.__pmgr = GuiPluginManager.get_instance()
        self.__preg = PluginRegister.get_instance()
        dialog = Gtk.Dialog(
            title="", transient_for=uistate.window, destroy_with_parent=True
        )
        dialog.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.set_window(dialog, None, self.title)

        self.setup_configs("interface.pluginstatus", 750, 400)
        self.window.connect("response", self.__on_dialog_button)

        notebook = Gtk.Notebook()

        # first page with all registered plugins
        vbox_reg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window_reg = Gtk.ScrolledWindow()
        self.list_reg = Gtk.TreeView()
        #  model: plugintype, hidden, pluginname, plugindescr, pluginid
        self.model_reg = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        self.selection_reg = self.list_reg.get_selection()
        self.list_reg.set_model(self.model_reg)
        self.list_reg.connect("button-press-event", self.button_press_reg)
        col0_reg = Gtk.TreeViewColumn(_("Type"), Gtk.CellRendererText(), text=0)
        col0_reg.set_sort_column_id(0)
        col0_reg.set_resizable(True)
        self.list_reg.append_column(col0_reg)
        col = Gtk.TreeViewColumn(_("Status"), Gtk.CellRendererText(), markup=1)
        col.set_sort_column_id(1)
        self.list_reg.append_column(col)
        col2_reg = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=2)
        col2_reg.set_sort_column_id(2)
        col2_reg.set_resizable(True)
        self.list_reg.append_column(col2_reg)
        col = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text=3)
        col.set_sort_column_id(3)
        col.set_resizable(True)
        self.list_reg.append_column(col)
        self.list_reg.set_search_column(2)

        scrolled_window_reg.add(self.list_reg)
        vbox_reg.pack_start(scrolled_window_reg, True, True, 0)
        hbutbox = Gtk.ButtonBox()
        hbutbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.__info_btn = Gtk.Button(label=_("Info"))
        hbutbox.add(self.__info_btn)
        self.__info_btn.connect("clicked", self.__info, self.list_reg, 4)  # id_col
        self.__hide_btn = Gtk.Button(label=_("Hide/Unhide"))
        hbutbox.add(self.__hide_btn)
        self.__hide_btn.connect(
            "clicked", self.__hide, self.list_reg, 4, 1
        )  # list, id_col, hide_col
        if __debug__:
            self.__edit_btn = Gtk.Button(label=_("Edit"))
            hbutbox.add(self.__edit_btn)
            self.__edit_btn.connect("clicked", self.__edit, self.list_reg, 4)  # id_col
            self.__load_btn = Gtk.Button(label=_("Load"))
            hbutbox.add(self.__load_btn)
            self.__load_btn.connect("clicked", self.__load, self.list_reg, 4)  # id_col
        vbox_reg.pack_start(hbutbox, False, False, 0)

        notebook.append_page(
            vbox_reg, tab_label=Gtk.Label(label=_("Registered Plugins"))
        )

        # second page with loaded plugins
        vbox_loaded = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window = Gtk.ScrolledWindow()
        self.list = Gtk.TreeView()
        self.model = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            object,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        self.selection = self.list.get_selection()
        self.list.set_model(self.model)
        self.list.connect("button-press-event", self.button_press)
        self.list.connect("cursor-changed", self.cursor_changed)
        col = Gtk.TreeViewColumn(_("Loaded"), Gtk.CellRendererText(), markup=0)
        col.set_sort_column_id(0)
        col.set_resizable(True)
        self.list.append_column(col)
        col1 = Gtk.TreeViewColumn(_("File"), Gtk.CellRendererText(), text=1)
        col1.set_sort_column_id(1)
        col1.set_resizable(True)
        self.list.append_column(col1)
        col = Gtk.TreeViewColumn(_("Status"), Gtk.CellRendererText(), markup=5)
        col.set_sort_column_id(5)
        self.list.append_column(col)
        col2 = Gtk.TreeViewColumn(_("Message"), Gtk.CellRendererText(), text=2)
        col2.set_sort_column_id(2)
        col2.set_resizable(True)
        self.list.append_column(col2)
        self.list.set_search_column(1)

        scrolled_window.add(self.list)
        vbox_loaded.pack_start(scrolled_window, True, True, 0)
        hbutbox = Gtk.ButtonBox()
        hbutbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.__info_btn = Gtk.Button(label=_("Info"))
        hbutbox.add(self.__info_btn)
        self.__info_btn.connect("clicked", self.__info, self.list, 4)  # id_col
        self.__hide_btn = Gtk.Button(label=_("Hide/Unhide"))
        hbutbox.add(self.__hide_btn)
        self.__hide_btn.connect(
            "clicked", self.__hide, self.list, 4, 5
        )  # list, id_col, hide_col

        if __debug__:
            self.__edit_btn = Gtk.Button(label=_("Edit"))
            hbutbox.add(self.__edit_btn)
            self.__edit_btn.connect("clicked", self.__edit, self.list, 4)  # id_col
            self.__load_btn = Gtk.Button(label=_("Load"))
            self.__load_btn.set_sensitive(False)
            hbutbox.add(self.__load_btn)
            self.__load_btn.connect("clicked", self.__load, self.list, 4)  # id_col
        vbox_loaded.pack_start(hbutbox, False, False, 5)
        notebook.append_page(
            vbox_loaded, tab_label=Gtk.Label(label=_("Loaded Plugins"))
        )

        # third page with method to install plugin
        install_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window = Gtk.ScrolledWindow()
        self.addon_list = Gtk.TreeView()
        # model: help_name, name, ptype, image, desc, use, rating, contact, download, url
        self.addon_model = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        self.addon_list.set_model(self.addon_model)
        # self.addon_list.connect('button-press-event', self.button_press)
        col = Gtk.TreeViewColumn(_("Addon Name"), Gtk.CellRendererText(), text=1)
        col.set_sort_column_id(1)
        self.addon_list.append_column(col)
        col = Gtk.TreeViewColumn(_("Type"), Gtk.CellRendererText(), text=2)
        col.set_sort_column_id(2)
        self.addon_list.append_column(col)
        col = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text=4)
        col.set_sort_column_id(4)
        self.addon_list.append_column(col)
        self.addon_list.connect("cursor-changed", self.button_press_addon)

        install_row = Gtk.Box()
        install_row.pack_start(Gtk.Label(label=_("Path to Addon:")), False, True, 0)
        self.install_addon_path = Gtk.Entry()

        button = Gtk.Button()
        img = Gtk.Image()
        img.set_from_icon_name("document-open", Gtk.IconSize.BUTTON)
        button.add(img)
        button.connect("clicked", self.__select_file)
        install_row.pack_start(self.install_addon_path, True, True, 0)
        install_row.pack_start(button, False, False, 0)

        scrolled_window.add(self.addon_list)
        install_page.pack_start(scrolled_window, True, True, 0)
        # add some spce under the scrollbar
        install_page.pack_start(Gtk.Label(label=""), False, False, 0)
        # path to addon path line
        install_page.pack_start(install_row, False, False, 0)

        hbutbox = Gtk.ButtonBox()
        hbutbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.__add_btn = Gtk.Button(label=_("Install Addon"))
        hbutbox.add(self.__add_btn)
        self.__add_btn.connect("clicked", self.__get_addon_top)
        self.__add_all_btn = Gtk.Button(label=_("Install All Addons"))
        hbutbox.add(self.__add_all_btn)
        self.__add_all_btn.connect("clicked", self.__get_all_addons)
        self.__refresh_btn = Gtk.Button(label=_("Refresh Addon List"))
        hbutbox.add(self.__refresh_btn)
        self.__refresh_btn.connect("clicked", self.__refresh_addon_list)
        install_page.pack_start(hbutbox, False, True, 5)
        # notebook.append_page(install_page,
        #                      tab_label=Gtk.Label(label=_('Install Addons')))

        # add the notebook to the window
        self.window.get_content_area().pack_start(notebook, True, True, 0)

        if __debug__:
            # Only show the "Reload" button when in debug mode
            # (without -O on the command line)
            self.window.add_button(_("Reload"), RELOAD)

        # obtain hidden plugins from the pluginmanager
        self.hidden = self.__pmgr.get_hidden_plugin_ids()

        self.window.show_all()
        self.__populate_lists()
        self.list_reg.columns_autosize()

    def __on_dialog_button(self, dialog, response_id):
        if response_id == Gtk.ResponseType.CLOSE:
            self.close(dialog)
        else:  # response_id == RELOAD
            self.__reload(dialog)

    def __refresh_addon_list(self, obj):
        """
        Reloads the addons from the wiki into the list.
        """
        from urllib.request import urlopen
        from ..utils import ProgressMeter

        URL = "%s%s" % (URL_WIKISTRING, WIKI_EXTRAPLUGINS_RAWDATA)
        try:
            fp = urlopen(URL)
        except:
            print("Error: cannot open %s" % URL)
            return
        pm = ProgressMeter(_("Refreshing Addon List"), parent=self.uistate.window)
        pm.set_pass(header=_("Reading gramps-project.org..."))
        state = "read"
        rows = []
        row = []
        lines = fp.readlines()
        pm.set_pass(total=len(lines), header=_("Reading gramps-project.org..."))
        for line in lines:
            pm.step()
            if line.startswith("|-") or line.startswith("|}"):
                if row != []:
                    rows.append(row)
                state = "row"
                row = []
            elif state == "row":
                if line.startswith("|"):
                    row.append(line[1:].strip())
            else:
                state = "read"
        fp.close()
        rows.sort(key=lambda row: (row[1], row[0]))
        self.addon_model.clear()
        # clear the config list:
        config.get("plugin.addonplugins")[:] = []
        pm.set_pass(total=len(rows), header=_("Checking addon..."))
        for row in rows:
            pm.step()
            try:
                # from wiki:
                help_name, ptype, image, desc, use, rating, contact, download = row
            except:
                continue
            help_url = _("Unknown Help URL")
            if help_name.startswith("[[") and help_name.endswith("]]"):
                name = help_name[2:-2]
                if "|" in name:
                    help_url, name = name.split("|", 1)
            elif help_name.startswith("[") and help_name.endswith("]"):
                name = help_name[1:-1]
                if " " in name:
                    help_url, name = name.split(" ", 1)
            else:
                name = help_name
            url = _("Unknown URL")
            if download.startswith("[[") and download.endswith("]]"):
                # Not directly possible to get the URL:
                url = download[2:-2]
                if "|" in url:
                    url, text = url.split("|", 1)
                # need to get a page that says where it is:
                fp = urlopen(
                    "%s%s%s"
                    % (URL_WIKISTRING, url, "&action=edit&externaledit=true&mode=file")
                )
                for line in fp:
                    if line.startswith("URL="):
                        junk, url = line.split("=", 1)
                        break
                fp.close()
            elif download.startswith("[") and download.endswith("]"):
                url = download[1:-1]
                if " " in url:
                    url, text = url.split(" ", 1)
            if (
                url.endswith(".zip")
                or url.endswith(".ZIP")
                or url.endswith(".tar.gz")
                or url.endswith(".tgz")
            ):
                # Then this is ok:
                self.addon_model.append(
                    row=[
                        help_name,
                        name,
                        ptype,
                        image,
                        desc,
                        use,
                        rating,
                        contact,
                        download,
                        url,
                    ]
                )
                config.get("plugin.addonplugins").append(
                    [
                        help_name,
                        name,
                        ptype,
                        image,
                        desc,
                        use,
                        rating,
                        contact,
                        download,
                        url,
                    ]
                )
        pm.close()
        config.save()

    def __get_all_addons(self, obj):
        """
        Get all addons from the wiki and install them.
        """
        from ..utils import ProgressMeter

        pm = ProgressMeter(
            _("Install all Addons"),
            _("Installing..."),
            message_area=True,
            parent=self.uistate.window,
        )
        pm.set_pass(total=len(self.addon_model))
        errors = []
        for row in self.addon_model:
            pm.step()
            (
                help_name,
                name,
                ptype,
                image,
                desc,
                use,
                rating,
                contact,
                download,
                url,
            ) = row
            load_addon_file(url, callback=pm.append_message)
        self.uistate.viewmanager.do_reg_plugins(self.dbstate, self.uistate)
        pm.message_area_ok.set_sensitive(True)
        self.__rebuild_load_list()
        self.__rebuild_reg_list()

    def __get_addon_top(self, obj):
        """
        Toplevel method to get an addon.
        """
        from ..utils import ProgressMeter

        pm = ProgressMeter(
            _("Installing Addon"), message_area=True, parent=self.uistate.window
        )
        pm.set_pass(total=2, header=_("Reading gramps-project.org..."))
        pm.step()
        self.__get_addon(obj, callback=pm.append_message)
        pm.step()
        pm.message_area_ok.set_sensitive(True)

    def __get_addon(self, obj, callback=display_message):
        """
        Get an addon from the wiki or file system and install it.
        """
        path = self.install_addon_path.get_text()
        load_addon_file(path, callback)
        self.uistate.viewmanager.do_reg_plugins(self.dbstate, self.uistate)
        self.__rebuild_load_list()
        self.__rebuild_reg_list()

    def __select_file(self, obj):
        """
        Select a file from the file system.
        """
        fcd = Gtk.FileChooserDialog(
            title=_("Load Addon"), transient_for=self.__uistate.window
        )
        fcd.add_buttons(
            _("_Cancel"), Gtk.ResponseType.CANCEL, _("_Open"), Gtk.ResponseType.OK
        )
        name = self.install_addon_path.get_text()
        dir = os.path.dirname(name)
        if not os.path.isdir(dir):
            dir = USER_HOME
            name = ""
        elif not os.path.isfile(name):
            name = ""
        fcd.set_current_folder(dir)
        if name:
            fcd.set_filename(name)

        status = fcd.run()
        if status == Gtk.ResponseType.OK:
            path = fcd.get_filename()
            if path:
                self.install_addon_path.set_text(path)
        fcd.destroy()

    def __populate_lists(self):
        """Build the lists of plugins"""
        self.__populate_load_list()
        self.__populate_reg_list()
        self.__populate_addon_list()

    def __populate_addon_list(self):
        """
        Build the list of addons from the config setting.
        """
        self.addon_model.clear()
        for row in config.get("plugin.addonplugins"):
            try:
                (
                    help_name,
                    name,
                    ptype,
                    image,
                    desc,
                    use,
                    rating,
                    contact,
                    download,
                    url,
                ) = row
            except:
                continue
            self.addon_model.append(
                row=[
                    help_name,
                    name,
                    ptype,
                    image,
                    desc,
                    use,
                    rating,
                    contact,
                    download,
                    url,
                ]
            )

    def __populate_load_list(self):
        """Build list of loaded plugins"""
        fail_list = self.__pmgr.get_fail_list()

        for i in fail_list:
            # i = (filename, (exception-type, exception, traceback), pdata)
            err = i[1][0]
            pdata = i[2]
            hidden = pdata.id in self.hidden
            if hidden:
                hiddenstr = self.HIDDEN
            else:
                hiddenstr = self.AVAILABLE
            if err == UnavailableError:
                self.model.append(
                    row=[
                        '<span color="blue">%s</span>' % _("Unavailable"),
                        i[0],
                        str(i[1][1]),
                        None,
                        pdata.id,
                        hiddenstr,
                    ]
                )
            else:
                self.model.append(
                    row=[
                        '<span weight="bold" color="red">%s</span>' % _("Fail"),
                        i[0],
                        str(i[1][1]),
                        i[1],
                        pdata.id,
                        hiddenstr,
                    ]
                )

        success_list = sorted(
            self.__pmgr.get_success_list(), key=lambda x: (x[0], x[2]._get_name())
        )
        for i in success_list:
            # i = (filename, module, pdata)
            pdata = i[2]
            modname = i[1].__name__
            hidden = pdata.id in self.hidden
            if hidden:
                hiddenstr = self.HIDDEN
            else:
                hiddenstr = self.AVAILABLE
            self.model.append(
                row=[
                    '<span weight="bold" color="#267726">%s</span>' % _("OK"),
                    i[0],
                    pdata.description,
                    None,
                    pdata.id,
                    hiddenstr,
                ]
            )

    def __populate_reg_list(self):
        """Build list of registered plugins"""
        for type, typestr in PTYPE_STR.items():
            registered_plugins = []
            for pdata in self.__preg.type_plugins(type):
                #  model: plugintype, hidden, pluginname, plugindescr, pluginid
                hidden = pdata.id in self.hidden
                if hidden:
                    hiddenstr = self.HIDDEN
                else:
                    hiddenstr = self.AVAILABLE
                registered_plugins.append(
                    [typestr, hiddenstr, pdata.name, pdata.description, pdata.id]
                )
            for row in sorted(registered_plugins):
                self.model_reg.append(row)

    def __rebuild_load_list(self):
        self.model.clear()
        self.__populate_load_list()

    def __rebuild_reg_list(self):
        self.model_reg.clear()
        self.__populate_reg_list()

    def cursor_changed(self, obj):
        if __debug__:
            selection = obj.get_selection()
            if selection:
                model, node = selection.get_selected()
                if node:
                    data = model.get_value(node, 3)
                    self.__load_btn.set_sensitive(data is not None)

    def button_press(self, obj, event):
        """Callback function from the user clicking on a line"""
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            model, node = self.selection.get_selected()
            data = model.get_value(node, 3)
            name = model.get_value(node, 1)
            if data:
                PluginTrace(self.uistate, [], data, name)

    def button_press_reg(self, obj, event):
        """Callback function from the user clicking on a line in reg plugin"""
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            self.__info(obj, self.list_reg, 4)

    def button_press_addon(self, obj):
        """Callback function from the user clicking on a line in reg plugin"""
        selection = self.addon_list.get_selection()
        if selection:
            model, node = selection.get_selected()
            if node:
                url = model.get_value(node, 9)
                self.install_addon_path.set_text(url)

    def build_menu_names(self, obj):
        return (self.title, "")

    def __reload(self, obj):
        """Callback function from the "Reload" button"""
        self.__pmgr.reload_plugins()
        self.__rebuild_load_list()
        self.__rebuild_reg_list()

    def __info(self, obj, list_obj, id_col):
        """Callback function from the "Info" button"""
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(id)
        typestr = pdata.ptype
        auth = " - ".join(pdata.authors)
        email = " - ".join(pdata.authors_email)
        if len(auth) > 60:
            auth = auth[:60] + "..."
        if len(email) > 60:
            email = email[:60] + "..."
        if pdata:
            infotxt = """%(plugnam)s: %(name)s [%(typestr)s]

%(plugdes)s: %(descr)s
%(plugver)s: %(version)s
%(plugaut)s: %(authors)s
%(plugmel)s: %(email)s
%(plugfil)s: %(fname)s
%(plugpat)s: %(fpath)s
""" % {
                "name": pdata.name,
                "typestr": typestr,
                "descr": pdata.description,
                "version": pdata.version,
                "authors": auth,
                "email": email,
                "fname": pdata.fname,
                "fpath": pdata.fpath,
                "plugnam": _("Plugin name"),
                "plugdes": _("Description"),
                "plugver": _("Version"),
                "plugaut": _("Authors"),
                "plugmel": _("Email"),
                "plugfil": _("Filename"),
                "plugpat": _("Location"),
            }
            InfoDialog(_("Detailed Info"), infotxt, parent=self.window)

    def __hide(self, obj, list_obj, id_col, hide_col):
        """Callback function from the "Hide" button"""
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        if id in self.hidden:
            # unhide
            self.hidden.remove(id)
            model.set_value(node, hide_col, self.AVAILABLE)
            self.__pmgr.unhide_plugin(id)
        else:
            # hide
            self.hidden.add(id)
            model.set_value(node, hide_col, self.HIDDEN)
            self.__pmgr.hide_plugin(id)

    def __load(self, obj, list_obj, id_col):
        """Callback function from the "Load" button"""
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        idv = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(idv)
        self.__pmgr.load_plugin(pdata)
        self.__rebuild_load_list()

    def __edit(self, obj, list_obj, id_col):
        """Callback function from the "Load" button"""
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(id)
        if pdata.fpath and pdata.fname:
            open_file_with_default_application(
                os.path.join(pdata.fpath, pdata.fname), self.uistate
            )


# -------------------------------------------------------------------------
#
# Details for an individual plugin that failed
#
# -------------------------------------------------------------------------
class PluginTrace(ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""

    def __init__(self, uistate, track, data, name):
        self.name = name
        title = _("%(str1)s: %(str2)s") % {"str1": _("Plugin Error"), "str2": name}
        ManagedWindow.__init__(self, uistate, track, self)

        dlg = Gtk.Dialog(
            title="", transient_for=uistate.window, destroy_with_parent=True
        )
        dlg.add_button(_("_Close"), Gtk.ResponseType.CLOSE),
        self.set_window(dlg, None, title)
        self.setup_configs("interface.plugintrace", 600, 400)
        self.window.connect("response", self.close)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.text = Gtk.TextView()
        scrolled_window.add(self.text)
        self.text.get_buffer().set_text(
            "".join(traceback.format_exception(data[0], data[1], data[2]))
        )

        self.window.get_content_area().add(scrolled_window)
        self.window.show_all()

    def build_menu_names(self, obj):
        return (self.name, None)


# -------------------------------------------------------------------------
#
# Classes for tools
#
# -------------------------------------------------------------------------
class LinkTag(Gtk.TextTag):
    def __init__(self, link, buffer):
        Gtk.TextTag.__init__(self, name=link)
        tag_table = buffer.get_tag_table()
        self.set_property("foreground", "#0000ff")
        self.set_property("underline", Pango.Underline.SINGLE)
        try:
            tag_table.add(self)
        except ValueError:
            pass  # already in table


class ToolManagedWindowBase(ManagedWindow):
    """
    Copied from src/ReportBase/_BareReportDialog.py BareReportDialog
    """

    border_pad = 6
    HELP_TOPIC = None

    def __init__(self, dbstate, uistate, option_class, name, callback=None):
        self.name = name
        ManagedWindow.__init__(self, uistate, [], self)

        self.extra_menu = None
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        self.format_menu = None
        self.style_button = None

        window = Gtk.Dialog(title="Tool")
        self.set_window(window, None, self.get_title())

        # self.window.connect('response', self.close)
        self.cancel = self.window.add_button(_("_Close"), Gtk.ResponseType.CANCEL)
        self.cancel.connect("clicked", self.close)

        self.ok = self.window.add_button(_("_Execute"), Gtk.ResponseType.OK)
        self.ok.connect("clicked", self.on_ok_clicked)

        self.window.set_default_size(600, -1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        self.add_user_options()

        self.notebook = Gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.get_content_area().pack_start(self.notebook, True, True, 0)

        self.results_text = Gtk.TextView()
        self.results_text.connect("button-press-event", self.on_button_press)
        self.results_text.connect("motion-notify-event", self.on_motion)
        self.tags = []
        self.link_cursor = Gdk.Cursor.new_for_display(
            Gdk.Display.get_default(), Gdk.CursorType.LEFT_PTR
        )
        self.standard_cursor = Gdk.Cursor.new_for_display(
            Gdk.Display.get_default(), Gdk.CursorType.XTERM
        )

        self.setup_other_frames()
        self.set_current_frame(self.initial_frame())
        self.show()

    # ------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    # ------------------------------------------------------------------------
    def on_cancel(self, *obj):
        pass  # cancel just closes

    def on_ok_clicked(self, obj):
        """
        The user is satisfied with the dialog choices. Parse all options
        and run the tool.
        """
        # Save options
        self.options.parse_user_options()
        self.options.handler.save_options()
        self.pre_run()
        self.run()  # activate results tab
        self.post_run()

    def initial_frame(self):
        return None

    def on_motion(self, view, event):
        buffer_location = view.window_to_buffer_coords(
            Gtk.TextWindowType.TEXT, int(event.x), int(event.y)
        )
        _iter = view.get_iter_at_location(*buffer_location)
        if isinstance(_iter, tuple):  # Gtk changed api in recent versions
            _iter = _iter[1]

        for tag, person_handle in self.tags:
            if _iter.has_tag(tag):
                _window = view.get_window(Gtk.TextWindowType.TEXT)
                _window.set_cursor(self.link_cursor)
                return False  # handle event further, if necessary
        view.get_window(Gtk.TextWindowType.TEXT).set_cursor(self.standard_cursor)
        return False  # handle event further, if necessary

    def on_button_press(self, view, event):
        buffer_location = view.window_to_buffer_coords(
            Gtk.TextWindowType.TEXT, int(event.x), int(event.y)
        )
        _iter = view.get_iter_at_location(*buffer_location)
        if isinstance(_iter, tuple):  # Gtk changed api in recent versions
            _iter = _iter[1]
        for tag, person_handle in self.tags:
            if _iter.has_tag(tag):
                person = self.db.get_person_from_handle(person_handle)
                if event.button == 1:
                    if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                        try:
                            EditPerson(self.dbstate, self.uistate, [], person)
                        except WindowActiveError:
                            pass
                    else:
                        self.uistate.set_active(person_handle, "Person")
                    return True  # handled event
        return False  # did not handle event

    def results_write_link(self, text, person, person_handle):
        self.results_write("   ")
        buffer = self.results_text.get_buffer()
        iter = buffer.get_end_iter()
        offset = buffer.get_char_count()
        self.results_write(text)
        start = buffer.get_iter_at_offset(offset)
        end = buffer.get_end_iter()
        self.tags.append((LinkTag(person_handle, buffer), person_handle))
        buffer.apply_tag(self.tags[-1][0], start, end)

    def results_write(self, text):
        buffer = self.results_text.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        self.results_text.scroll_to_mark(mark, 0.0, True, 0, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")

    def write_to_page(self, page, text):
        buffer = page.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        page.scroll_to_mark(mark, 0.0, True, 0, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")

    def clear(self, text):
        # Remove all tags and clear text
        buffer = text.get_buffer()
        tag_table = buffer.get_tag_table()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        for tag, handle in self.tags:
            buffer.remove_tag(tag, start, end)
            tag_table.remove(tag)
        self.tags = []
        buffer.set_text("")

    def results_clear(self):
        # Remove all tags and clear text
        buffer = self.results_text.get_buffer()
        tag_table = buffer.get_tag_table()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        for tag, handle in self.tags:
            buffer.remove_tag(tag, start, end)
            tag_table.remove(tag)
        self.tags = []
        buffer.set_text("")

    def pre_run(self):
        from ..utils import ProgressMeter

        self.progress = ProgressMeter(self.get_title(), parent=self.window)

    def run(self):
        raise NotImplementedError("tool needs to define a run() method")

    def post_run(self):
        self.progress.close()

    # ------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    # ------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "Tool"  # self.title

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        selected person.  Most subclasses will customize this to give
        some indication of what the report will be, i.e. 'Descendant
        Report for %s'."""
        return self.get_title()

    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""

        title = self.get_header(self.get_title())
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        self.window.get_content_area().pack_start(label, False, False, self.border_pad)

    def add_frame_option(self, frame_name, label_text, widget):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""

        if frame_name in self.frames:
            self.frames[frame_name].append((label_text, widget))
        else:
            self.frames[frame_name] = [(label_text, widget)]
            self.frame_names.append(frame_name)

    def set_current_frame(self, name):
        if name is None:
            self.notebook.set_current_page(0)
        else:
            for frame_name in self.frame_names:
                if name == frame_name:
                    if len(self.frames[frame_name]) > 0:
                        fname, child = self.frames[frame_name][0]
                        page = self.notebook.page_num(child)
                        self.notebook.set_current_page(page)
                        return

    def add_results_frame(self, frame_name="Results"):
        if frame_name not in self.frames:
            window = Gtk.ScrolledWindow()
            window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            window.add(self.results_text)
            window.set_shadow_type(Gtk.ShadowType.IN)
            self.frames[frame_name] = [[frame_name, window]]
            self.frame_names.append(frame_name)
            l = Gtk.Label(label="<b>%s</b>" % _(frame_name))
            l.set_use_markup(True)
            self.notebook.append_page(window, l)
            self.notebook.show_all()
        else:
            self.results_clear()
        return self.results_text

    def add_page(self, frame_name="Help"):
        if frame_name not in self.frames:
            text = Gtk.TextView()
            text.set_wrap_mode(Gtk.WrapMode.WORD)
            window = Gtk.ScrolledWindow()
            window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            window.add(text)
            window.set_shadow_type(Gtk.ShadowType.IN)
            self.frames[frame_name] = [[frame_name, window]]
            self.frame_names.append(frame_name)
            l = Gtk.Label(label="<b>%s</b>" % _(frame_name))
            l.set_use_markup(True)
            self.notebook.append_page(window, l)
            self.notebook.show_all()
        else:
            # FIXME: get text
            #
            text = self.frames[frame_name][0][1].something
        return text

    def setup_other_frames(self):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""
        for key in self.frame_names:
            flist = self.frames[key]
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.set_border_width(6)
            l = Gtk.Label(label="<b>%s</b>" % key)
            l.set_use_markup(True)
            self.notebook.append_page(grid, l)
            row = 0
            for text, widget in flist:
                widget.set_hexpand(True)
                if text:
                    text_widget = Gtk.Label(label="%s:" % text)
                    text_widget.set_halign(Gtk.Align.START)
                    grid.attach(text_widget, 1, row, 1, 1)
                    grid.attach(widget, 2, row, 1, 1)
                else:
                    grid.attach(widget, 2, row, 1, 1)
                row += 1
        self.notebook.show_all()

    # ------------------------------------------------------------------------
    #
    # Functions related to extending the options
    #
    # ------------------------------------------------------------------------
    def add_user_options(self):
        """Called to allow subclasses add widgets to the dialog form.
        It is called immediately before the window is displayed. All
        calls to add_option or add_frame_option should be called in
        this task."""
        add_gui_options(self)

    def build_menu_names(self, obj):
        return (_("Main window"), self.get_title())


class ToolManagedWindowBatch(tool.BatchTool, ToolManagedWindowBase):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        # This constructor will ask a question, set self.fail:
        self.dbstate = dbstate
        self.uistate = uistate
        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if not self.fail:
            ToolManagedWindowBase.__init__(
                self, dbstate, uistate, options_class, name, callback
            )


class ToolManagedWindow(tool.Tool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.dbstate = dbstate
        self.uistate = uistate
        tool.Tool.__init__(self, dbstate, options_class, name)
        ToolManagedWindowBase.__init__(
            self, dbstate, uistate, options_class, name, callback
        )


# -------------------------------------------------------------------------
#
# UpdateAddons
#
# -------------------------------------------------------------------------
class UpdateAddons(ManagedWindow):
    def __init__(self, uistate, track, addon_update_list):
        self.title = _("Available Gramps Updates for Addons")

        ManagedWindow.__init__(self, uistate, track, self, modal=True)
        glade = Glade("updateaddons.glade")
        self.set_window(glade.toplevel, None, None)
        self.window.set_title(self.title)
        self.setup_configs("interface.updateaddons", 750, 400)
        self.rescan = False

        apply_button = glade.get_object("apply")
        cancel_button = glade.get_object("cancel")
        select_all = glade.get_object("select_all")
        select_all.connect("clicked", self.select_all_clicked)
        select_none = glade.get_object("select_none")
        select_none.connect("clicked", self.select_none_clicked)
        apply_button.connect("clicked", self.install_addons)
        cancel_button.connect("clicked", self.close)

        self.list = ListModel(
            glade.get_object("list"),
            [
                # name, click?, width, toggle
                {
                    "name": _("Select"),
                    "width": 60,
                    "type": TOGGLE,
                    "visible_col": 6,
                    "editable": True,
                },  # 0 selected?
                (_("Type"), 1, 180),  # 1 new gramplet
                (_("Name"), 2, 200),  # 2 name (version)
                (_("Description"), 3, 200),  # 3 description
                ("", NOSORT, 0),  # 4 url
                ("", NOSORT, 0),  # 5 id
                {"name": "", "type": TOGGLE},  # 6 visible? bool
            ],
            list_mode="tree",
        )
        pos = None
        addon_update_list.sort(key=lambda x: "%s %s" % (x[0], x[2]["t"]))
        last_category = None
        for status, plugin_url, plugin_dict in addon_update_list:
            count = get_count(addon_update_list, plugin_dict["t"])
            # Translators: needed for French, ignore otherwise
            category = _("%(str1)s: %(str2)s") % {
                "str1": status,
                "str2": PTYPE_STR[plugin_dict["t"]],
            }
            if last_category != category:
                last_category = category
                node = self.list.add(
                    [False, category, "", "", "", "", False]  # initially selected?
                )  # checkbox visible?
            iter = self.list.add(
                [
                    False,  # initially selected?
                    "%s %s" % (status, PTYPE_STR[plugin_dict["t"]]),
                    "%s (%s)" % (plugin_dict["n"], plugin_dict["v"]),
                    plugin_dict["d"],
                    plugin_url,
                    plugin_dict["i"],
                    True,
                ],
                node=node,
            )
            if pos is None:
                pos = iter
        if pos:
            self.list.selection.select_iter(pos)

        self.show()
        self.window.run()

    def build_menu_names(self, obj):
        return (self.title, " ")

    def select_all_clicked(self, widget):
        """
        Select all of the addons for download.
        """
        self.list.model.foreach(update_rows, True)
        self.list.tree.expand_all()

    def select_none_clicked(self, widget):
        """
        Select none of the addons for download.
        """
        self.list.model.foreach(update_rows, False)
        self.list.tree.expand_all()

    def install_addons(self, obj):
        """
        Process all of the selected addons.
        """
        self.window.hide()
        model = self.list.model

        iter = model.get_iter_first()
        length = 0
        while iter:
            iter = model.iter_next(iter)
            if iter:
                length += model.iter_n_children(iter)

        longop = LongOpStatus(
            _("Downloading and installing selected addons..."),
            length,
            1,  # total, increment-by
            can_cancel=True,
        )
        pm = ProgressMonitor(
            GtkProgressDialog, ("Title", self.parent_window, Gtk.DialogFlags.MODAL)
        )
        pm.add_op(longop)
        count = 0
        if not config.get("behavior.do-not-show-previously-seen-addon-updates"):
            # reset list
            config.get("behavior.previously-seen-addon-updates")[:] = []

        iter = model.get_iter_first()
        errors = []
        while iter:
            for rowcnt in range(model.iter_n_children(iter)):
                child = model.iter_nth_child(iter, rowcnt)
                row = [model.get_value(child, n) for n in range(6)]
                if longop.should_cancel():
                    break
                elif row[0]:  # toggle on
                    ok = load_addon_file(row[4], callback=LOG.debug)
                    if ok:
                        count += 1
                    else:
                        errors.append(row[2])
                else:  # add to list of previously seen, but not installed
                    if row[5] not in config.get(
                        "behavior.previously-seen-addon-updates"
                    ):
                        config.get("behavior.previously-seen-addon-updates").append(
                            row[5]
                        )
                longop.heartbeat()
                pm._get_dlg()._process_events()
            iter = model.iter_next(iter)

        if not longop.was_cancelled():
            longop.end()
        if errors:
            OkDialog(
                _("Installation Errors"),
                _("The following addons had errors: ") +
                # TODO for Arabic, should the next comma be translated?
                ", ".join(errors),
                parent=self.parent_window,
            )
        if count:
            self.rescan = True
            OkDialog(
                _("Done downloading and installing addons"),
                # Translators: leave all/any {...} untranslated
                "%s %s"
                % (
                    ngettext(
                        "{number_of} addon was installed.",
                        "{number_of} addons were installed.",
                        count,
                    ).format(number_of=count),
                    _(
                        "If you have installed a 'View', you will need to restart Gramps."
                    ),
                ),
                parent=self.parent_window,
            )
        else:
            OkDialog(
                _("Done downloading and installing addons"),
                _("No addons were installed."),
                parent=self.parent_window,
            )
        self.close()


# -------------------------------------------------------------------------
#
# Local Functions
#
# -------------------------------------------------------------------------
def update_rows(model, path, iter, user_data):
    """
    Update the rows of a model.
    """
    # path: (8,)   iter: <GtkTreeIter at 0xbfa89fa0>
    # path: (8, 0) iter: <GtkTreeIter at 0xbfa89f60>
    if len(path.get_indices()) == 2:
        row = model[path]
        row[0] = user_data
        model.row_changed(path, iter)


def get_count(addon_update_list, category):
    """
    Get the count of matching category items.
    """
    count = 0
    for status, plugin_url, plugin_dict in addon_update_list:
        if plugin_dict["t"] == category and plugin_url:
            count += 1
    return count
