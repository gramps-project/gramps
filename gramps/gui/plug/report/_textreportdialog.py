#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008-2009  Brian G. Matherly
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

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...pluginmanager import GuiPluginManager
from gramps.gen.plug.report._constants import CATEGORY_TEXT
from ._docreportdialog import DocReportDialog

#-------------------------------------------------------------------------
#
# _TextFormatComboBox
#
#-------------------------------------------------------------------------
class _TextFormatComboBox(Gtk.ComboBox):
    """
    This class is a combo box that allows the selection of a docgen plugin
    from all textdoc plugins.
    """
    def __init__(self, active):

        Gtk.ComboBox.__init__(self)

        pmgr = GuiPluginManager.get_instance()
        self.__textdoc_plugins = []
        for plugin in pmgr.get_docgen_plugins():
            if plugin.get_text_support():
                self.__textdoc_plugins.append(plugin)

        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        index = 0
        active_index = 0
        for plugin in self.__textdoc_plugins:
            name = plugin.get_name()
            self.store.append(row=[name])
            if plugin.get_extension() == active:
                active_index = index
            index += 1
        self.set_active(active_index)

    def get_active_plugin(self):
        """
        Get the plugin represented by the currently active selection.
        """
        return self.__textdoc_plugins[self.get_active()]

#-----------------------------------------------------------------------
#
# TextReportDialog
#
#-----------------------------------------------------------------------
class TextReportDialog(DocReportDialog):
    """
    A class of ReportDialog customized for text based reports.
    """
    def __init__(self, dbstate, uistate, options, name, translated_name):
        """
        Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information.
        """
        self.format_menu = None
        self.category = CATEGORY_TEXT
        DocReportDialog.__init__(self, dbstate, uistate, options,
                                 name, translated_name)

    def make_doc_menu(self, active=None):
        """
        Build a menu of document types that are appropriate for
        this text report.
        """
        self.format_menu = _TextFormatComboBox( active )
