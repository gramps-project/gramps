#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2007-2009  Stephane Charette
# Copyright (C) 2009       Gary Burton
# Contribution 2009 by     Bob Ham <rah@bash.sh>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012-2013  Paul Franklin
# Copyright (C) 2017       Nick Hall
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

"""base class for generating dialogs for graph-based reports """

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import os

# -------------------------------------------------------------------------------
#
# GTK+ modules
#
# -------------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.config import config
from gramps.gen.plug.report import CATEGORY_GRAPHVIZ
from ._reportdialog import ReportDialog
from ._papermenu import PaperFrame
import gramps.gen.plug.docgen.graphdoc as graphdoc
from gramps.gen.plug.menu import Menu


# -------------------------------------------------------------------------------
#
# GraphvizFormatComboBox
#
# -------------------------------------------------------------------------------
class BaseFormatComboBox(Gtk.ComboBox):
    """
    Combo box base class for graph-based report format choices.
    """

    FORMATS = []

    def set(self, active=None):
        """initialize the Graphviz choices"""
        store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, "text", 0)

        index = 0
        active_index = 0
        for item in self.FORMATS:
            name = item["descr"]
            store.append(row=[name])
            if item["type"] == active:
                active_index = index
            index += 1
        self.set_active(active_index)

    def get_label(self):
        """get the format description"""
        return self.FORMATS[self.get_active()]["descr"]

    def get_reference(self):
        """get the format class"""
        return self.FORMATS[self.get_active()]["class"]

    def get_ext(self):
        """get the format extension"""
        return ".%s" % self.FORMATS[self.get_active()]["ext"]

    def get_clname(self):
        """get the report's output format type"""
        return self.FORMATS[self.get_active()]["type"]


# -----------------------------------------------------------------------
#
# GraphReportDialog
#
# -----------------------------------------------------------------------
class GraphReportDialog(ReportDialog, metaclass=ABCMeta):
    """A base class of ReportDialog customized for graph-based reports."""

    def __init__(self, dbstate, uistate, opt, name, translated_name):
        """Initialize a dialog to request that the user select options
        for a Graphviz report.  See the ReportDialog class for
        more information."""
        self.category = self.get_category()
        self._goptions = self.get_options()
        self.dbname = dbstate.db.get_dbname()
        ReportDialog.__init__(self, dbstate, uistate, opt, name, translated_name)

        self.doc = None  # keep pylint happy
        self.format = None
        self.paper_label = None

    def init_options(self, option_class):
        try:
            if issubclass(option_class, object):  # Old-style class
                self.options = option_class(self.raw_name, self.dbstate.get_database())
        except TypeError:
            self.options = option_class

        menu = Menu()
        self._goptions.add_menu_options(menu)

        for category in menu.get_categories():
            for name in menu.get_option_names(category):
                option = menu.get_option(category, name)
                self.options.add_menu_option(category, name, option)

        self.options.load_previous_values()

    def init_interface(self):
        ReportDialog.init_interface(self)
        self.doc_type_changed(self.format_menu)
        self.notebook.set_current_page(1)  # don't start on "Paper Options"

    def setup_format_frame(self):
        """Set up the format frame of the dialog."""
        self.make_doc_menu()
        self.format_menu.set(self.options.handler.get_format_name())
        self.format_menu.connect("changed", self.doc_type_changed)
        label = Gtk.Label(label=_("%s:") % _("Output Format"))
        label.set_halign(Gtk.Align.START)
        self.grid.attach(label, 1, self.row, 1, 1)
        self.format_menu.set_hexpand(True)
        self.grid.attach(self.format_menu, 2, self.row, 2, 1)
        self.row += 1

        self.open_with_app = Gtk.CheckButton(label=_("Open with default viewer"))
        self.open_with_app.set_active(config.get("interface.open-with-default-viewer"))
        self.grid.attach(self.open_with_app, 2, self.row, 2, 1)
        self.row += 1

        ext = self.format_menu.get_ext()
        if ext is None:
            ext = ""
        else:
            spath = self.get_default_directory()
            if self.options.get_output():
                base = os.path.basename(self.options.get_output())
            else:
                if self.dbname is None:
                    default_name = self.raw_name
                else:
                    default_name = self.dbname + "_" + self.raw_name
                base = "%s%s" % (default_name, ext)  # "ext" already has a dot
            spath = os.path.normpath(os.path.join(spath, base))
            self.target_fileentry.set_filename(spath)

    def setup_report_options_frame(self):
        self.paper_label = Gtk.Label(label="<b>%s</b>" % _("Paper Options"))
        self.paper_label.set_use_markup(True)
        handler = self.options.handler
        self.paper_frame = PaperFrame(
            handler.get_paper_metric(),
            handler.get_paper_name(),
            handler.get_orientation(),
            handler.get_margins(),
            handler.get_custom_paper_size(),
        )
        self.notebook.insert_page(self.paper_frame, self.paper_label, 0)
        self.paper_frame.show_all()

        ReportDialog.setup_report_options_frame(self)

    def doc_type_changed(self, obj):
        """
        This routine is called when the user selects a new file
        format for the report.  It adjusts the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those changes are made here.
        """
        self.open_with_app.set_sensitive(True)

        fname = self.target_fileentry.get_full_path(0)
        (spath, ext) = os.path.splitext(fname)

        ext_val = obj.get_ext()
        if ext_val:
            fname = spath + ext_val
        else:
            fname = spath
        self.target_fileentry.set_filename(fname)

    def make_document(self):
        """Create a document of the type requested by the user."""
        pstyle = self.paper_frame.get_paper_style()

        self.doc = self.format(self.options, pstyle)

        self.options.set_document(self.doc)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices.  Validate
        the output file name before doing anything else.  If there is
        a file name, gather the options and create the report."""

        # Is there a filename?  This should also test file permissions, etc.
        if not self.parse_target_frame():
            self.window.run()

        # Preparation
        self.parse_format_frame()
        self.parse_user_options()

        self.options.handler.set_paper_metric(self.paper_frame.get_paper_metric())
        self.options.handler.set_paper_name(self.paper_frame.get_paper_name())
        self.options.handler.set_orientation(self.paper_frame.get_orientation())
        self.options.handler.set_margins(self.paper_frame.get_paper_margins())
        self.options.handler.set_custom_paper_size(
            self.paper_frame.get_custom_paper_size()
        )

        # Create the output document.
        self.make_document()

        # Save options
        self.options.handler.save_options()
        config.set(
            "interface.open-with-default-viewer", self.open_with_app.get_active()
        )

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_reference()
        format_name = self.format_menu.get_clname()
        self.options.handler.set_format_name(format_name)

    def setup_style_frame(self):
        """Required by ReportDialog"""
        pass

    @abstractmethod
    def make_doc_menu(self):
        """
        Build a menu of document types that are appropriate for
        this graph report.
        """

    @abstractmethod
    def get_category(self):
        """
        Return the report category.
        """

    @abstractmethod
    def get_options(self):
        """
        Return the graph options.
        """
