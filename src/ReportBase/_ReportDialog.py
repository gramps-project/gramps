#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
# Python modules
#
#-------------------------------------------------------------------------
import os
from types import ClassType
from gettext import gettext as _

import logging
LOG = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK+ modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Config
import Errors
from QuestionDialog import ErrorDialog, OptionDialog
from ReportBase import (CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, 
                        CATEGORY_CODE, CATEGORY_WEB, CATEGORY_GRAPHVIZ, 
                        standalone_categories)
from gen.plug.docgen import StyleSheet, StyleSheetList
import ManagedWindow
from _StyleComboBox import StyleComboBox
from _StyleEditor import StyleListDisplay
from _FileEntry import FileEntry
from const import URL_MANUAL_PAGE

#-------------------------------------------------------------------------
#
# Private Constants
#
#-------------------------------------------------------------------------
URL_REPORT_PAGE = URL_MANUAL_PAGE + "_-_Reports"

#-------------------------------------------------------------------------
#
# ReportDialog class
#
#-------------------------------------------------------------------------
class ReportDialog(ManagedWindow.ManagedWindow):
    """
    The ReportDialog base class.  This is a base class for generating
    customized dialogs to solicit options for a report.  It cannot be
    used as is, but it can be easily sub-classed to create a functional
    dialog for a stand-alone report.
    """
    border_pad = 6

    def __init__(self, dbstate, uistate, option_class, name, trans_name,
                 track=[]):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""
        
        self.style_name = "default"
        self.page_html_added = False
        self.raw_name = name
        self.dbstate = dbstate
        self.db = dbstate.db
        self.report_name = trans_name
        
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.init_options(option_class)
        self.init_interface()
        
    def init_options(self, option_class):
        try:
            if (issubclass(option_class, object) or     # New-style class
                isinstance(option_class, ClassType)):   # Old-style class
                self.options = option_class(self.raw_name, self.db)
        except TypeError:
            self.options = option_class

        self.options.load_previous_values()

    def build_window_key(self, obj):
        key = self.raw_name
        return key

    def build_menu_names(self, obj):
        return (_("Configuration"), self.report_name)

    def init_interface(self):
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        self.format_menu = None
        self.style_button = None

        self.style_name = self.options.handler.get_default_stylesheet_name()

        window = gtk.Dialog('GRAMPS')
        self.set_window(window, None, self.get_title())
        self.window.set_has_separator(False)
        self.window.set_modal(True)

        self.help = self.window.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
        self.help.connect('clicked', self.on_help_clicked)

        self.cancel = self.window.add_button(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_CANCEL)
        self.cancel.connect('clicked', self.on_cancel)

        self.ok = self.window.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.ok.connect('clicked', self.on_ok_clicked)

        self.window.set_default_size(600, -1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()
        self.tbl = gtk.Table(4, 4, False)
        self.tbl.set_col_spacings(12)
        self.tbl.set_row_spacings(6)
        self.tbl.set_border_width(6)
        self.row = 0

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        self.add_user_options()

        self.setup_main_options()
        self.setup_init()
        self.setup_format_frame()
        self.setup_target_frame()
        self.setup_style_frame()

        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_border_width(6)
        self.window.vbox.add(self.notebook)

        self.setup_report_options_frame()
        self.setup_other_frames()
        self.notebook.set_current_page(0)

        self.window.vbox.add(self.tbl)
        self.show()

    def get_title(self):
        """The window title for this dialog"""
        name = self.report_name
        category = standalone_categories[self.category]
        return "%s - %s - GRAMPS" % (name, category)
    
    #------------------------------------------------------------------------
    #
    # Functions related to extending the options
    #
    #------------------------------------------------------------------------
    def add_user_options(self):
        """Called to allow subclasses add widgets to the dialog form.
        It is called immediately before the window is displayed. All
        calls to add_option or add_frame_option should be called in
        this task."""
        self.options.add_user_options(self)

    def parse_user_options(self):
        """Called to allow parsing of added widgets.
        It is called when OK is pressed in a dialog. 
        All custom widgets should provide a parsing code here."""
        try:
            self.options.parse_user_options(self)
        except:
            LOG.error("Failed to parse user options.", exc_info=True)
            
    def add_option(self, label_text, widget):
        """Takes a text string and a Gtk Widget, and stores them to be
        appended to the Options section of the dialog. The text string
        is used to create a label for the passed widget. This allows the
        subclass to extend the Options section with its own widgets. The
        subclass is responsible for all managing of the widgets, including
        extracting the final value before the report executes. This task
        should only be called in the add_user_options task."""
        self.widgets.append((label_text, widget))

    def add_frame_option(self, frame_name, label_text, widget):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is responsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""
        
        if frame_name in self.frames:
            self.frames[frame_name].append((label_text, widget))
        else:
            self.frames[frame_name] = [(label_text, widget)]
            self.frame_names.append(frame_name)
        
    #------------------------------------------------------------------------
    #
    # Functions to create a default output style.
    #
    #------------------------------------------------------------------------

    def build_style_menu(self, default=None):
        """Build a menu of style sets that are available for use in
        this report.  This menu will always have a default style
        available, and will have any other style set name that the
        user has previously created for this report.  This menu is
        created here instead of inline with the rest of the style
        frame, because it must be recreated to reflect any changes
        whenever the user closes the style editor dialog."""
        
        if default is None:
            default = self.style_name
            
        style_sheet_map = self.style_sheet_list.get_style_sheet_map()
        self.style_menu.set(style_sheet_map, default)
        
    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog."""
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % 
                          self.report_name)
        label.set_use_markup(True)
        self.window.vbox.pack_start(label, True, True, self.border_pad)
        
    def setup_style_frame(self):
        """Set up the style frame of the dialog.  This function relies
        on other routines create the default style for this report,
        and to read in any user defined styles for this report.  It
        the builds a menu of all the available styles for the user to
        choose from."""
        # Build the default style set for this report.
        self.default_style = StyleSheet()
        self.options.make_default_style(self.default_style)

        if self.default_style.is_empty():
            # Don't display the option of no styles are used
            return

        # Styles Frame
        label = gtk.Label("%s:" % _("Style"))
        label.set_alignment(0.0, 0.5)

        self.style_menu = StyleComboBox()
        self.style_button = gtk.Button("%s..." % _("Style Editor"))
        self.style_button.connect('clicked', self.on_style_edit_clicked)

        self.tbl.attach(label, 1, 2, self.row, self.row+1, gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.style_menu, 2, 3, self.row, self.row+1,
                        yoptions=gtk.SHRINK)
        self.tbl.attach(self.style_button, 3, 4, self.row, self.row+1,
                        xoptions=gtk.SHRINK|gtk.FILL, yoptions=gtk.SHRINK)
        self.row += 1
        
        # Build the initial list of available styles sets.  This
        # includes the default style set and any style sets saved from
        # previous invocations of gramps.
        self.style_sheet_list = StyleSheetList(
                            self.options.handler.get_stylesheet_savefile(),
                            self.default_style)

        # Now build the actual menu.
        style = self.options.handler.get_default_stylesheet_name()
        self.build_style_menu(style)

    def setup_report_options_frame(self):
        """Set up the report options frame of the dialog.  This
        function relies on several report_xxx() customization
        functions to determine which of the items should be present in
        this box.  *All* of these items are optional, although the
        generations fields is used in most
        (but not all) dialog boxes."""

        row = 0
        max_rows = len(self.widgets)

        if max_rows == 0:
            return

        table = gtk.Table(3, max_rows+1)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        
        label = gtk.Label("<b>%s</b>" % _("Report Options"))
        label.set_alignment(0.0, 0.5)
        label.set_use_markup(True)
        
        table.set_border_width(6)
        self.notebook.append_page(table, label)
        row += 1

        # Setup requested widgets
        for (text, widget) in self.widgets:
            if text:
                text_widget = gtk.Label("%s:" % text)
                text_widget.set_alignment(0.0, 0.0)
                table.attach(text_widget, 1, 2, row, row+1,
                             gtk.SHRINK|gtk.FILL, gtk.SHRINK)
                table.attach(widget, 2, 3, row, row+1,
                             yoptions=gtk.SHRINK)
            else:
                table.attach(widget, 2, 3, row, row+1,
                             yoptions=gtk.SHRINK)
            row += 1

    def setup_other_frames(self):
        for key in self.frame_names:
            if key == "":
                continue
            flist = self.frames[key]
            table = gtk.Table(3, len(flist))
            table.set_col_spacings(12)
            table.set_row_spacings(6)
            table.set_border_width(6)
            l = gtk.Label("<b>%s</b>" % _(key))
            l.set_use_markup(True)
            self.notebook.append_page(table, l)

            row = 0
            for (text, widget) in flist:
                if text:
                    text_widget = gtk.Label('%s:' % text)
                    text_widget.set_alignment(0.0, 0.5)
                    table.attach(text_widget, 1, 2, row, row+1,
                                 gtk.SHRINK|gtk.FILL, gtk.SHRINK)
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                else:
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                row = row + 1
                
    def setup_main_options(self):
        if "" in self.frames:
            flist = self.frames[""]
            for (text, widget) in flist:
                label = gtk.Label("<b>%s</b>" % text)
                label.set_use_markup(True)
                label.set_alignment(0.0, 0.5)
                
                self.tbl.set_border_width(12)
                self.tbl.attach(label, 0, 4, self.row, self.row+1)
                self.row += 1
    
                self.tbl.attach(widget, 2, 4, self.row, self.row+1)
                self.row += 1

    #------------------------------------------------------------------------
    #
    # Customization hooks for stand-alone reports (subclass ReportDialog)
    #
    #------------------------------------------------------------------------
    def setup_format_frame(self): 
        """Not used in bare report dialogs. Override in the subclass."""
        pass

    #------------------------------------------------------------------------
    #
    # Functions related getting/setting the default directory for a dialog.
    #
    #------------------------------------------------------------------------
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return Config.get(Config.REPORT_DIRECTORY)

    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        Config.set(Config.REPORT_DIRECTORY, value)

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_init(self):
        # add any elements that we are going to need:
        hid = self.style_name
        if hid[-4:] == ".xml":
            hid = hid[0:-4]
        self.target_fileentry = FileEntry(hid, _("Save As"))
        spath = self.get_default_directory()
        self.target_fileentry.set_filename(spath)
        # need any labels at top:
        label = gtk.Label("<b>%s</b>" % _('Document Options'))
        label.set_use_markup(1)
        label.set_alignment(0.0, 0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(label, 0, 4, self.row, self.row+1, gtk.FILL)
        self.row += 1
        
    def setup_target_frame(self):
        """Set up the target frame of the dialog.  This function
        relies on several target_xxx() customization functions to
        determine whether the target is a directory or file, what the
        title of any browser window should be, and what default
        directory should be used."""

        # Save Frame
        self.doc_label = gtk.Label("%s:" % _("Filename"))
        self.doc_label.set_alignment(0.0, 0.5)

        self.tbl.attach(self.doc_label, 1, 2, self.row, self.row+1,
                        xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK)
        self.tbl.attach(self.target_fileentry, 2, 4, self.row, self.row+1,
                        xoptions=gtk.EXPAND|gtk.FILL,yoptions=gtk.SHRINK)
        self.row += 1
        
    #------------------------------------------------------------------------
    #
    # Functions related to retrieving data from the dialog window
    #
    #------------------------------------------------------------------------
    def parse_target_frame(self):
        """Parse the target frame of the dialog.  If the target
        filename is empty this routine returns a special value of None
        to tell the calling routine to give up.  This function also
        saves the current directory so that any future reports will
        default to the most recently used directory."""
        self.target_path = self.target_fileentry.get_full_path(0)
        if not self.target_path:
            return None

        # First we check whether the selected path exists
        if os.path.exists(self.target_path):

            # selected path is an existing dir and we need a dir
            if os.path.isdir(self.target_path):

                # check whether the dir has rwx permissions
                if not os.access(self.target_path, os.R_OK|os.W_OK|os.X_OK):
                    ErrorDialog(_('Permission problem'),
                                _("You do not have permission to write "
                                  "under the directory %s\n\n"
                                  "Please select another directory or correct "
                                  "the permissions.") % self.target_path 
                                )
                    return None

            # selected path is an exsting file and we need a file
            if os.path.isfile(self.target_path):
                a = OptionDialog(_('File already exists'),
                                 _('You can choose to either overwrite the '
                                   'file, or change the selected filename.'),
                                 _('_Overwrite'), None,
                                 _('_Change filename'), None)
                             
                if a.get_response() == gtk.RESPONSE_YES:
                    return None

        # selected path does not exist yet
        else:
            # we will need to create the file/dir
            # need to make sure we can create in the parent dir
            parent_dir = os.path.dirname(os.path.normpath(self.target_path))
            if not os.access(parent_dir, os.W_OK):
                ErrorDialog(_('Permission problem'),
                            _("You do not have permission to create "
                              "%s\n\n"
                              "Please select another path or correct "
                              "the permissions.") % self.target_path 
                            )
                return None
        
        self.set_default_directory(os.path.dirname(self.target_path) + os.sep)
        self.options.handler.output = self.target_path
        return 1
    
    def parse_style_frame(self):
        """Parse the style frame of the dialog.  Save the user
        selected output style for later use.  Note that this routine
        retrieves a value whether or not the menu is displayed on the
        screen.  The subclass will know whether this menu was enabled.
        This is for simplicity of programming."""
        if not self.default_style.is_empty():
            (style_name, self.selected_style) = self.style_menu.get_value()
            self.options.handler.set_default_stylesheet_name(style_name)

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices.  Validate
        the output file name before doing anything else.  If there is
        a file name, gather the options and create the report."""

        # Is there a filename?  This should also test file permissions, etc.
        if not self.parse_target_frame():
            self.window.run()

        # Preparation
        self.parse_style_frame()
        self.parse_user_options()
        
        # Save options
        self.options.handler.save_options()
        
    def on_cancel(self, *obj):
        pass

    def on_help_clicked(self, *obj):
        import GrampsDisplay
        GrampsDisplay.help(URL_REPORT_PAGE, self.report_name.replace(" ", "_"))
        
    def on_style_edit_clicked(self, *obj):
        """The user has clicked on the 'Edit Styles' button.  Create a
        style sheet editor object and let them play.  When they are
        done, the previous routine will be called to update the dialog
        menu for selecting a style."""
        StyleListDisplay(self.style_sheet_list, self.build_style_menu,
                         self.window)

#------------------------------------------------------------------------
#
# Generic task function a standalone GUI report
#
#------------------------------------------------------------------------
def report(dbstate, uistate, person, report_class, options_class,
           trans_name, name, category, require_active):
    """
    report - task starts the report. The plugin system requires that the
    task be in the format of task that takes a database and a person as
    its arguments.
    """

    if require_active and not person:
        ErrorDialog(
            _('Active person has not been set'),
            _('You must select an active person for this report to work '
              'properly.'))
        return

    if category == CATEGORY_TEXT:
        from _TextReportDialog import TextReportDialog
        dialog_class = TextReportDialog
    elif category == CATEGORY_DRAW:
        from _DrawReportDialog import DrawReportDialog
        dialog_class = DrawReportDialog
    elif category == CATEGORY_GRAPHVIZ:
        from _GraphvizReportDialog import GraphvizReportDialog
        dialog_class = GraphvizReportDialog
    elif category == CATEGORY_WEB:
        from _WebReportDialog import WebReportDialog
        dialog_class = WebReportDialog
    elif category in (CATEGORY_BOOK, CATEGORY_CODE):
        try:
            report_class(dbstate, uistate)
        except Errors.WindowActiveError:
            pass
        return        
    else:
        dialog_class = ReportDialog

    dialog = dialog_class(dbstate, uistate, options_class, name, trans_name)

    while True:
        response = dialog.window.run()
        if response == gtk.RESPONSE_OK:
            dialog.close()
            try:
                MyReport = report_class(dialog.db, dialog.options)
                MyReport.doc.init()
                MyReport.begin_report()
                MyReport.write_report()
                MyReport.end_report()
            except Errors.FilterError, msg:
                (m1, m2) = msg.messages()
                ErrorDialog(m1, m2)
            except IOError, msg:
                ErrorDialog(_("Report could not be created"),str(msg))
            except Errors.ReportError, msg:
                (m1, m2) = msg.messages()
                ErrorDialog(m1, m2)
            except Errors.DatabaseError,msg:                
                ErrorDialog(_("Report could not be created"), str(msg))
#           The following except statement will catch all "NoneType" exceptions.
#           This is useful for released code where the exception is most likely
#           a corrupt database. But it is less useful for developing new reports
#           where the execption is most likely a report bug.                
#            except AttributeError,msg:
#                if str(msg).startswith("'NoneType' object has no attribute"):
#                    # "'NoneType' object has no attribute ..." usually means
#                    # database corruption
#                    RunDatabaseRepair(str(msg))
#                else:
#                    raise
                raise
            except:
                LOG.error("Failed to run report.", exc_info=True)
            break
        elif (response == gtk.RESPONSE_DELETE_EVENT or
              response == gtk.RESPONSE_CANCEL):
            dialog.close()
            break
