#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012-2013  Paul Franklin
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

"""
    base class for generating dialogs for docgen-derived reports
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GTK+ modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.config import config
from ._reportdialog import ReportDialog
from ._papermenu import PaperFrame
from ...pluginmanager import GuiPluginManager

PLUGMAN = GuiPluginManager.get_instance()

#-------------------------------------------------------------------------
#
# DocReportDialog class
#
#-------------------------------------------------------------------------
class DocReportDialog(ReportDialog):
    """
    The DocReportDialog base class.  This is a base class for generating
    dialogs for docgen derived reports.
    """

    def __init__(self, dbstate, uistate, option_class, name, trans_name, track=[]):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""

        self.style_name = "default"
        self.firstpage_added = False
        self.css = PLUGMAN.process_plugin_data('WEBSTUFF')
        self.dbname = dbstate.db.get_dbname()
        ReportDialog.__init__(self, dbstate, uistate, option_class,
                              name, trans_name, track=track)

        self.basedocname = None # keep pylint happy
        self.css_filename = None
        self.doc = None
        self.doc_option_class = None
        self.format = None
        self.html_label = None
        self.paper_label = None

        # Allow for post processing of the format frame, since the
        # show_all task calls events that may reset values

    def init_interface(self):
        ReportDialog.init_interface(self)
        self.doc_type_changed(self.format_menu, preserve_tab=False)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self, active=None):
        """Build a menu of document types that are appropriate for
        this report.  This menu will be generated based upon the type
        of document (text, draw, graph, etc. - a subclass), whether or
        not the document requires table support, etc."""
        raise NotImplementedError

    def make_document(self):
        """Create a document of the type requested by the user.
        """
        pstyle = self.paper_frame.get_paper_style()

        if self.doc_options:
            self.doc = self.format(self.selected_style, pstyle,
                                   self.doc_options,
                                   uistate=self.uistate)
        else:
            self.doc = self.format(self.selected_style, pstyle,
                                   uistate=self.uistate)
        if not self.format_menu.get_active_plugin().get_paper_used():
            #set css filename
            self.doc.set_css_filename(self.css_filename)

        self.options.set_document(self.doc)

    def doc_type_changed(self, obj, preserve_tab=True):
        """This routine is called when the user selects a new file
        format for the report.  It adjusts the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, an HTML document doesn't need any
        paper size/orientation options, but it does need a css
        file.  Those changes are made here."""
        docgen_plugin = obj.get_active_plugin()
        if docgen_plugin.get_extension():
            self.open_with_app.set_sensitive(True)
        else:
            self.open_with_app.set_sensitive(False)

        # Is this to be a printed report or an electronic report
        # (i.e. a set of web pages)

        old_page = self.notebook.get_current_page()
        if self.firstpage_added:
            self.notebook.remove_page(0)
        if docgen_plugin.get_paper_used():
            self.paper_label = Gtk.Label(
                label='<b>%s</b>' % _("Paper Options"))
            self.paper_label.set_use_markup(True)
            self.notebook.insert_page(self.paper_frame, self.paper_label, 0)
            self.paper_frame.show_all()
        else:
            self.html_label = Gtk.Label(
                label='<b>%s</b>' % _("HTML Options"))
            self.html_label.set_use_markup(True)
            self.notebook.insert_page(self.html_grid, self.html_label, 0)
            self.html_grid.show_all()
        if preserve_tab:
            self.notebook.set_current_page(old_page)
        self.firstpage_added = True

        ext_val = docgen_plugin.get_extension()
        if ext_val:
            fname = self.target_fileentry.get_full_path(0)
            (spath, ext) = os.path.splitext(fname)

            fname = spath + "." + ext_val
            self.target_fileentry.set_filename(fname)
            self.target_fileentry.set_sensitive(True)
        else:
            self.target_fileentry.set_filename("")
            self.target_fileentry.set_sensitive(False)

        # Does this report format use styles?
        if self.style_button:
            self.style_button.set_sensitive(docgen_plugin.get_style_support())
            self.style_menu.set_sensitive(docgen_plugin.get_style_support())

        self.basedocname = docgen_plugin.get_basedocname()
        self.doc_option_class = docgen_plugin.get_doc_option_class()
        self.setup_doc_options_frame()
        self.show()

    def setup_format_frame(self):
        """Set up the format frame of the dialog.  This function
        relies on the make_doc_menu() function to do all the hard
        work."""

        self.make_doc_menu(self.options.handler.get_format_name())
        self.format_menu.connect('changed', self.doc_type_changed)
        label = Gtk.Label(label=_("%s:") % _("Output Format"))
        label.set_halign(Gtk.Align.START)
        self.grid.attach(label, 1, self.row, 1, 1)
        self.format_menu.set_hexpand(True)
        self.grid.attach(self.format_menu, 2, self.row, 2, 1)
        self.row += 1

        self.open_with_app = Gtk.CheckButton(
            label=_("Open with default viewer"))
        self.open_with_app.set_active(
            config.get('interface.open-with-default-viewer'))
        self.grid.attach(self.open_with_app, 2, self.row, 2, 1)
        self.row += 1

        ext = self.format_menu.get_active_plugin().get_extension()
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
                base = "%s.%s" % (default_name, ext)
            spath = os.path.normpath(os.path.join(spath, base))
            self.target_fileentry.set_filename(spath)

    def setup_report_options_frame(self):
        """ Set up the html/paper frame of the dialog """
        self.paper_frame = PaperFrame(
            self.options.handler.get_paper_metric(),
            self.options.handler.get_paper_name(),
            self.options.handler.get_orientation(),
            self.options.handler.get_margins(),
            self.options.handler.get_custom_paper_size())
        self.setup_html_frame()
        ReportDialog.setup_report_options_frame(self)

    def setup_html_frame(self):
        """Set up the html frame of the dialog.  This sole purpose of
        this function is to grab a pointer for later use in the parse
        html frame function."""

        self.html_grid = Gtk.Grid()
        self.html_grid.set_column_spacing(12)
        self.html_grid.set_row_spacing(6)
        self.html_grid.set_border_width(6)

        label = Gtk.Label(label=_("%s:") % _("CSS file"))
        label.set_halign(Gtk.Align.START)
        self.html_grid.attach(label, 1, 1, 1, 1)

        self.css_combo = Gtk.ComboBoxText()
        self.css_combo.set_hexpand(True)

        self.css_filename = self.options.handler.get_css_filename()
        active_index = 0
        index = 0
        for (name, _id) in sorted([(self.css[key]["translation"],
                                    self.css[key]["id"])
                                   for key in self.css]):
            if self.css[_id]["user"]:
                self.css_combo.append_text(self.css[_id]["translation"])
                # Associate this index number with CSS too:
                self.css[index] = self.css[_id]
                if self.css_filename == self.css[_id]["filename"]:
                    active_index = index
                index += 1

        self.html_grid.attach(self.css_combo, 2, 1, 1, 1)
        self.css_combo.set_active(active_index)

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        docgen_plugin = self.format_menu.get_active_plugin()
        self.basedocname = docgen_plugin.get_basedocname()
        self.format = docgen_plugin.get_basedoc()
        format_name = docgen_plugin.get_extension()
        self.options.handler.set_format_name(format_name)

    def parse_html_frame(self):
        """Parse the html frame of the dialog.  Save the user selected
        html template name for later use.  Note that this routine
        retrieves a value whether or not the file entry box is
        displayed on the screen.  The subclass will know whether this
        entry was enabled.  This is for simplicity of programming."""

        active = self.css_combo.get_active()
        if active == -1: # legal for "no active item" (see 7585, 8189, 9461)
            active = self.style_name
        if self.css:
            self.css_filename = self.css[active]["filename"]
        self.options.handler.set_css_filename(self.css_filename)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices.  Validate
        the output file name before doing anything else.  If there is
        a file name, gather the options and create the report."""

        # Is there a filename?  This should also test file permissions, etc.
        if not self.parse_target_frame():
            self.window.run()

        # Preparation
        self.parse_format_frame()
        self.parse_style_frame()
        self.parse_html_frame()

        self.options.handler.set_paper_metric(
            self.paper_frame.get_paper_metric())
        self.options.handler.set_paper_name(
            self.paper_frame.get_paper_name())
        self.options.handler.set_orientation(
            self.paper_frame.get_orientation())
        self.options.handler.set_margins(
            self.paper_frame.get_paper_margins())
        self.options.handler.set_custom_paper_size(
            self.paper_frame.get_custom_paper_size())

        self.parse_user_options()

        # Create the output document.
        self.make_document()

        self.parse_doc_options()

        # Save options
        self.options.handler.save_options()
        config.set('interface.open-with-default-viewer',
                   self.open_with_app.get_active())
