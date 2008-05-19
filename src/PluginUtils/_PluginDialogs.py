#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
# $Id$

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
from ReportBase import report, standalone_categories
import _Tool
from PluginUtils import PluginManager
import ManagedWindow

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_REPORTS = 0
_TOOLS   = 1
_UNSUPPORTED = _("Unsupported")

#-------------------------------------------------------------------------
#
# PluginDialog interface class
#
#-------------------------------------------------------------------------
class PluginDialog(ManagedWindow.ManagedWindow):
    """
    Displays the dialog box that allows the user to select the
    plugin that is desired.
    """
    def __init__(self, state, uistate, track, item_list, categories, msg,
                 label=None, button_label=None, tool_tip=None, 
                 content=_REPORTS):
        """
        Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dialog box.
        """
        
        self.active = state.active
        self.imap = {}
        self.msg = msg
        self.content = content

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, 
                                             self.__class__)

        self.state = state
        self.uistate = uistate
        
        self.dialog = glade.XML(const.PLUGINS_GLADE, "report", "gramps")
        self.dialog.signal_autoconnect({
            "on_report_apply_clicked" : self.on_apply_clicked,
            "destroy_passed_object"   : self.close,
            })

        self.tree = self.dialog.get_widget("tree")
        window = self.dialog.get_widget("report")
        self.title = self.dialog.get_widget("title")

        self.set_window(window, self.title, msg )

        self.store = gtk.TreeStore(str)
        self.selection = self.tree.get_selection()
        self.selection.connect('changed', self.on_node_selected)
        col = gtk.TreeViewColumn('', gtk.CellRendererText(), text=0)
        self.tree.append_column(col)
        self.tree.set_model(self.store)
        
        self.description = self.dialog.get_widget("description")
        if label:
            self.description.set_text(label)
        self.status = self.dialog.get_widget("report_status")
        
        self.author_name = self.dialog.get_widget("author_name")
        self.author_email = self.dialog.get_widget("author_email")
        
        self.apply_button = self.dialog.get_widget("apply")
        if button_label:
            self.apply_button.set_label(button_label)
        else:
            self.apply_button.set_label(_("_Apply"))
        self.apply_button.set_use_underline(True)
        if tool_tip:
            try:
                tttips = gtk.tooltips_data_get(self.apply_button)
                if tttips:
                    tttips[0].set_tip(self.apply_button, tool_tip)
            except AttributeError:
                pass

        self.item = None
        self.build_plugin_tree(item_list, categories)
        self.show()

    def rebuild(self):
        # This method needs to be overridden in the subclass
        assert False, "This method needs to be overridden in the subclass."

    def build_menu_names(self, obj):
        return (self.msg, None)

    def on_apply_clicked(self, obj):
        """Execute the selected report"""
        try:
            (item_class, options_class, title, category,
             name, require_active) = self.item
            if self.content == _REPORTS:
                report(self.state, self.uistate, self.state.active,
                       item_class, options_class, title, name, 
                       category, require_active)
            else:
                _Tool.gui_tool(self.state, self.uistate, 
                              item_class, options_class,title, name,category,
                              self.state.db.request_rebuild)
        except TypeError:
            pass # ignore pressing apply without a plugin being selected
        
    def on_node_selected(self, obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store, node = self.selection.get_selected()
        if node:
            path = store.get_path(node)
        if not node or not self.imap.has_key(path):
            return 
        data = self.imap[path]

        (report_class, options_class, title, category, name,
         doc,status,author,email,unsupported,require_active) = data
        self.description.set_text(doc)
        if unsupported:
            status = _UNSUPPORTED
        self.status.set_text(status)
        self.title.set_text('<span weight="bold" size="larger">%s</span>' \
                            % title)
        self.title.set_use_markup(1)
        self.author_name.set_text(author)
        self.author_email.set_text(email)
        self.item = (report_class, options_class, title, category,
                     name, require_active)

    def build_plugin_tree(self, item_list, categories):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (item_class, options_class,title,category, name,
         doc,status,author,email)

        Items in the same category are grouped under the same submenu.
        The categories must be dicts from integer to string.
        """

        ilist = []
        self.store.clear()

        # build the tree items and group together based on the category name
        item_hash = {}
        for plugin in item_list:
            if plugin[9]:
                category = _UNSUPPORTED
            else:
                category = categories[plugin[3]]
            if item_hash.has_key(category):
                item_hash[category].append(plugin)
            else:
                item_hash[category] = [plugin]

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = [ item for item in item_hash.keys() if item != _UNSUPPORTED]
        key_list.sort()
        key_list.reverse()
        
        prev = None
        if item_hash.has_key(_UNSUPPORTED):
            key = _UNSUPPORTED
            data = item_hash[key]
            node = self.store.insert_after(None, prev)
            self.store.set(node, 0, key)
            next = None
            data.sort(lambda x, y: cmp(x[2], y[2]))
            for item in data:
                next = self.store.insert_after(node, next)
                ilist.append((next, item))
                self.store.set(next, 0, item[2])
        for key in key_list:
            data = item_hash[key]
            node = self.store.insert_after(None, prev)
            self.store.set(node, 0, key)
            next = None
            data.sort(lambda x, y: cmp(x[2], y[2]))
            for item in data:
                next = self.store.insert_after(node, next)
                ilist.append((next, item))
                self.store.set(next, 0, item[2])
        for next, tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab

#-------------------------------------------------------------------------
#
# ReportPluginDialog
#
#-------------------------------------------------------------------------
class ReportPluginDialog(PluginDialog):
    """
    Displays the dialog box that allows the user to select the
    report that is desired.
    """

    def __init__(self, dbstate, uistate, track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        self.__pmgr = PluginManager.get_instance()

        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            self.__pmgr.get_report_list(),
            standalone_categories,
            _("Report Selection"),
            _("Select a report from those available on the left."),
            _("_Generate"), _("Generate selected report"),
            _REPORTS)
        
        self.__pmgr.connect('plugins-reloaded', self.rebuild)

    def rebuild(self):
        report_list = self.__pmgr.get_report_list()
        self.build_plugin_tree(report_list, standalone_categories)

#-------------------------------------------------------------------------
#
# ToolPluginDialog
#
#-------------------------------------------------------------------------
class ToolPluginDialog(PluginDialog):
    """Displays the dialog box that allows the user to select the tool
    that is desired."""

    def __init__(self, dbstate, uistate, track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        self.__pmgr = PluginManager.get_instance()

        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            self.__pmgr.get_tool_list(),
            _Tool.tool_categories,
            _("Tool Selection"),
            _("Select a tool from those available on the left."),
            _("_Run"),
            _("Run selected tool"),
            _TOOLS)

    def rebuild(self):
        tool_list = self.__pmgr.get_tool_list()
        self.build_plugin_tree(tool_list, _Tool.tool_categories)
