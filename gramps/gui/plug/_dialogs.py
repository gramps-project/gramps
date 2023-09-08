#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from collections import defaultdict

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import PLUGINS_GLADE
from gramps.gen.plug.report._constants import standalone_categories
from . import tool
from gramps.gen.plug import REPORT
from .report import report
from ..pluginmanager import GuiPluginManager
from ..managedwindow import ManagedWindow

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
_REPORTS = 0
_TOOLS = 1
_UNSUPPORTED = _("Unsupported")


# -------------------------------------------------------------------------
#
# PluginDialog interface class
#
# -------------------------------------------------------------------------
class PluginDialog(ManagedWindow):
    """
    Displays the dialog box that allows the user to select the
    plugin that is desired.
    """

    def __init__(
        self,
        state,
        uistate,
        track,
        categories,
        msg,
        label=None,
        button_label=None,
        tool_tip=None,
        content=_REPORTS,
    ):
        """
        Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dialog box.
        """
        self.active = uistate.get_active("Person")
        self.imap = {}
        self.msg = msg
        self.content = content
        self._pmgr = GuiPluginManager.get_instance()

        ManagedWindow.__init__(self, uistate, track, self.__class__)

        self.state = state
        self.uistate = uistate

        self.dialog = Gtk.Builder()
        self.dialog.set_translation_domain(glocale.get_localedomain())
        self.dialog.add_from_file(PLUGINS_GLADE)
        self.dialog.connect_signals(
            {
                "on_report_apply_clicked": self.on_apply_clicked,
                "destroy_passed_object": self.close,
                "on_delete_event": self.close,
            }
        )

        self.tree = self.dialog.get_object("tree")
        window = self.dialog.get_object("report")
        self.title = self.dialog.get_object("title")

        self.set_window(window, self.title, msg)
        if content == _REPORTS:
            self.setup_configs("interface.reportplugindialog", 600, 400)
        elif content == _TOOLS:
            self.setup_configs("interface.toolplugindialog", 600, 400)
        else:
            raise ValueError("PluginDialog selection must be a report or tool")

        self.store = Gtk.TreeStore(str)
        self.selection = self.tree.get_selection()
        self.selection.connect("changed", self.on_node_selected)
        col = Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0)
        self.tree.append_column(col)
        self.tree.set_model(self.store)

        self.description = self.dialog.get_object("description")
        if label:
            self.description.set_text(label)
        self.status = self.dialog.get_object("report_status")

        self.author_name = self.dialog.get_object("author_name")
        self.author_email = self.dialog.get_object("author_email")

        self.apply_button = self.dialog.get_object("apply")
        if button_label:
            self.apply_button.set_label(button_label)
        else:
            self.apply_button.set_label(_("_Apply"))
        self.apply_button.set_use_underline(True)
        if tool_tip:
            self.apply_button.set_tooltip_text(tool_tip)

        self.item = None

        if content == _REPORTS:
            reg_list = self._pmgr.get_reg_reports()
        elif content == _TOOLS:
            reg_list = self._pmgr.get_reg_tools()
        else:
            reg_list = []
        self.build_plugin_tree(reg_list, categories)
        self.show()

    def rebuild(self):
        # This method needs to be overridden in the subclass
        assert False, "This method needs to be overridden in the subclass."

    def build_menu_names(self, obj):
        return (self.msg, None)

    def on_apply_clicked(self, obj):
        """Execute the selected report"""
        if not self.item:
            return
        self.run_plugin(self.item)

    def on_node_selected(self, obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store, node = self.selection.get_selected()
        if node:
            path = store.get_path(node).to_string()
        if not node or path not in self.imap:
            return
        pdata = self.imap[path]

        # (report_class, options_class, title, category, name,
        # doc,status,author,email,unsupported,require_active) = data
        self.description.set_text(pdata.description)
        if not pdata.supported:
            status = _UNSUPPORTED
        self.status.set_text(pdata.statustext())
        self.title.set_text('<span weight="bold" size="larger">%s</span>' % pdata.name)
        self.title.set_use_markup(1)
        # TODO for Arabic, should the next two lines' commas be translated?
        self.author_name.set_text(", ".join(pdata.authors))
        self.author_email.set_text(", ".join(pdata.authors_email))
        self.item = pdata

    def build_plugin_tree(self, reg_list, categories):
        """Populates a GtkTree with each menu item associated with a entry
        in the lists. The list consists of PluginData objects for reports or
        tools.

        old data was (item_class, options_class,title,category, name,
         doc,status,author,email)

        Items in the same category are grouped under the same submenu.
        The categories must be dicts from integer to string.
        """
        ilist = []
        self.store.clear()

        # build the tree items and group together based on the category name
        item_hash = defaultdict(list)
        for plugin in reg_list:
            if not plugin.supported:
                category = _UNSUPPORTED
            else:
                category = categories[plugin.category]
            item_hash[category].append(plugin)

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = [item for item in item_hash if item != _UNSUPPORTED]
        key_list.sort(reverse=True)

        prev = None
        if _UNSUPPORTED in item_hash:
            key = _UNSUPPORTED
            data = item_hash[key]
            node = self.store.insert_after(None, prev)
            self.store.set(node, 0, key)
            next = None
            data.sort(key=lambda x: x.name)
            for item in data:
                next = self.store.insert_after(node, next)
                ilist.append((next, item))
                self.store.set(next, 0, item.name)
        for key in key_list:
            data = item_hash[key]
            node = self.store.insert_after(None, prev)
            self.store.set(node, 0, key[1])
            next = None
            data.sort(key=lambda k: k.name)
            for item in data:
                next = self.store.insert_after(node, next)
                ilist.append((next, item))
                self.store.set(next, 0, item.name)
        for next, tab in ilist:
            path = self.store.get_path(next).to_string()
            self.imap[path] = tab

    def run_plugin(self, pdata):
        """
        run a plugin based on it's PluginData:
          1/ load plugin.
          2/ the report is run
        """
        mod = self._pmgr.load_plugin(pdata)
        if not mod:
            # import of plugin failed
            return

        if pdata.ptype == REPORT:
            report(
                self.state,
                self.uistate,
                self.uistate.get_active("Person"),
                getattr(mod, pdata.reportclass),
                getattr(mod, pdata.optionclass),
                pdata.name,
                pdata.id,
                pdata.category,
                pdata.require_active,
            )
        else:
            from ..user import User

            tool.gui_tool(
                dbstate=self.state,
                user=User(uistate=self.uistate),
                tool_class=getattr(mod, pdata.toolclass),
                options_class=getattr(mod, pdata.optionclass),
                translated_name=pdata.name,
                name=pdata.id,
                category=pdata.category,
                callback=self.state.db.request_rebuild,
            )


# -------------------------------------------------------------------------
#
# ReportPluginDialog
#
# -------------------------------------------------------------------------
class ReportPluginDialog(PluginDialog):
    """
    Displays the dialog box that allows the user to select the
    report that is desired.
    """

    def __init__(self, dbstate, uistate, track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""

        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            standalone_categories,
            _("Report Selection"),
            _("Select a report from those available on the left."),
            _("_Generate"),
            _("Generate selected report"),
            _REPORTS,
        )

        self._pmgr.connect("plugins-reloaded", self.rebuild)

    def rebuild(self):
        report_list = self._pmgr.get_reg_reports()
        self.build_plugin_tree(report_list, standalone_categories)


# -------------------------------------------------------------------------
#
# ToolPluginDialog
#
# -------------------------------------------------------------------------
class ToolPluginDialog(PluginDialog):
    """Displays the dialog box that allows the user to select the tool
    that is desired."""

    def __init__(self, dbstate, uistate, track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""

        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            tool.tool_categories,
            _("Tool Selection"),
            _("Select a tool from those available on the left."),
            _("_Run"),
            _("Run selected tool"),
            _TOOLS,
        )

    def rebuild(self):
        tool_list = self._pmgr.get_reg_tools()
        self.build_plugin_tree(tool_list, tool.tool_categories)
