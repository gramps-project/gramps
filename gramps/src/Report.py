#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
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

"Report Generation Framework"

import RelLib
import const
import os
import re
import sort
import string
import utils
import intl

_ = intl.gettext

from TextDoc import *
from StyleEditor import *

import Config
import FindDoc
import PaperMenu

import gtk
import gnome.ui
import libglade

#------------------------------------------------------------------------
#
# The Report base class.  This is a base class for generating
# customized reports.  It cannot be used as is, but it can be easily
# sub-classed to create a functional report generator.
#
#------------------------------------------------------------------------
class Report:

    # Ordinal generation names.  Used by multiple reports.
    gen = {
        1 : _("First"),
        2 : _("Second"),
        3 : _("Third"),
        4 : _("Fourth"),
        5 : _("Fifth"),
        6 : _("Sixth"),
        7 : _("Seventh"),
        8 : _("Eighth"),
        9 : _("Ninth"),
        10: _("Tenth"),
        11: _("Eleventh"),
        12: _("Twelfth"),
        13: _("Thirteenth"),
        14: _("Fourteenth"),
        15: _("Fifteenth"),
        16: _("Sixteenth"),
        17: _("Seventeenth"),
        18: _("Eighteenth"),
        19: _("Nineteenth"),
        20: _("Twentieth"),
        21: _("Twenty-first"),
        22: _("Twenty-second"),
        23: _("Twenty-third"),
        24: _("Twenty-fourth"),
        25: _("Twenty-fifth"),
        26: _("Twenty-sixth"),
        27: _("Twenty-seventh"),
        28: _("Twenty-eighth"),
        29: _("Twenty-ninth")
        }

    def get_progressbar_data(self):
        """The window title for this dialog, and the header line to
        put at the top of the contents of the dialog box."""
        return (_("Gramps - Progress Report"), _("Working"))

    def progress_bar_setup(self,total):
        """Create a progress dialog.  This routine calls a
        customization function to find out how to fill out the dialog.
        The argument to this function is the maximum number of items
        that the report will progress; i.e. what's considered 100%,
        i.e. the maximum number of times this routine will be
        called."""
        
        # Load the glade file
        base = os.path.dirname(__file__)
        self.glade_file = os.path.join(base, "plugins", "basicreport.glade")
        self.pxml = libglade.GladeXML(self.glade_file,"progress_dialog")

        # Customize the dialog for this report
        (title, header) = self.get_progressbar_data()
        self.ptop = self.pxml.get_widget("progress_dialog")
        self.ptop.set_title(title)
        self.pxml.get_widget("header_label").set_text(header)

        # Setup the progress bar limits
        self.pbar = self.pxml.get_widget("progressbar")
        self.pbar.configure(0.0,0.0,total)
        self.pbar_index = 0.0

    def progress_bar_step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        self.pbar_index = self.pbar_index + 1.0
        if (self.pbar_index > 100.0):
            self.pbar_index = 100.0
        self.pbar.set_value(self.pbar_index)

    def progress_bar_done(self):
        """Done with the progress bar.  It can be destroyed now."""
        utils.destroy_passed_object(self.ptop)


#------------------------------------------------------------------------
#
# The ReportDialog base class.  This is a base class for generating
# customized dialogs to solicit options for a report.  It cannot be
# used as is, but it can be easily sub-classed to create a functional
# dialog.
#
#------------------------------------------------------------------------
class ReportDialog:
    def __init__(self,database,person,filename="basicreport.glade"):
        """Initialize a dialog to request that the user select options
        for a basic report.  The glade filename is optional.  If
        provided it must reference a glade file that is either be a
        superset of the basic dialog, or the subclass must override
        most of the setup_xxx and parse_xxx functions."""

        # Save info about who the report is about.
        self.db = database
        self.person = person

        # Load the glade file
        base = os.path.dirname(__file__)
        self.glade_file = os.path.join(base, "plugins", filename)
        self.topDialog = libglade.GladeXML(self.glade_file,"report_dialog")

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.
        self.setup_title()
        self.setup_header()
        self.setup_output_notebook()
        self.setup_target_frame()
        self.setup_style_frame()
        self.setup_format_frame()
        self.setup_paper_frame()
        self.setup_html_frame()
        self.setup_report_options_frame()
        self.setup_other_frames()
        self.connect_signals()

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog."""
        return(_("Gramps - Base Report"))

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        selected person.  Most subclasses will customize this to give
        some indication of what the report will be, i.e. 'Descendant
        Report for %s'."""
        return(name)
        
    def get_target_browser_title(self):
        """The title of the window that will be created when the user
        clicks the 'Browse' button in the 'Save As' File Entry
        widget."""
        return(_("Gramps - Save Report As"))

    def get_target_is_directory(self):
        """Is the user being asked to input the name of a file or a
        directory in the 'Save As' File Entry widget.  This item
        currently only selects the Filename/Directory prompt, and
        whether or not the browser accepts filenames.  In the future it
        may also control checking of the selected filename."""
        return None
    
    def get_stylesheet_savefile(self):
        """Where should new styles for this report be saved?  This is
        the name of an XML file that will be located in the ~/.gramps
        directory.  This file does not have to exist; it will be
        created when needed.  All subclasses should probably override
        this function."""
        return "basic_report.xml"

    def get_print_pagecount_map(self):
        """Return the data used to fill out the 'pagecount' option
        menu in the print options box.  The first value is a mapping
        of string:value pairs.  The strings will be used to label
        individual menu items, and the values are what will be
        returned if a given menu item is selected.  The second value
        is the name of menu item to pre-select."""
        return (None, None)
    
    def get_report_filter_strings(self):
        """Return the data used to fill out the 'filter' combo box in
        the report options box.  The return value is the list of
        strings to be inserted into the pulldown."""
        return None
    
    def get_report_generations(self):
        """Return the default number of generations to start the
        spinbox (zero to disable) and whether or not to include the
        'page break between generations' check box"""
        return (10, 1)
    
    def get_report_extra_menu_map(self):
        """Return the data used to fill out the 'extra' option menu in
        the report options box.  The first value is the string to be
        used as the label to the left of the menu.  The second value
        is a mapping of string:value pairs.  The strings will be used
        to label individual menu items, and the values are what will
        be returned if a given menu item is selected.  The final value
        is the name of menu item to pre-select."""
        return (None, None, None)
    
    def get_report_extra_textbox_string(self):
        """Return the string to put into the 'extra' text box in
        the report options box.  If None, then the text box will be
        hidden."""
        return (None, None)
    
    #------------------------------------------------------------------------
    #
    # Functions related getting/setting the default directory for a dialog.
    #
    #------------------------------------------------------------------------
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return Config.report_dir

    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        Config.report_dir = value

    #------------------------------------------------------------------------
    #
    # Functions to create a default output style.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Create the default style to be used by the associated report.  This
        routine is a default implementation and should be overridden."""
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF,size=16,bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set(pad=0.5)
        self.default_style.add_style("Title",para)

    def build_style_menu(self,dummy):
        """Build a menu of style sets that are available for use in
        this report.  This menu will always have a default style
        available, and will have any other style set name that the
        user has previously created for this report.  This menu is
        created here instead of inline with the rest of the style
        frame, because it must be recreated to reflect any changes
        whenever the user closes the style editor dialog."""
        style_sheet_map = self.style_sheet_list.get_style_sheet_map()
        myMenu = utils.build_string_optmenu(style_sheet_map, "default")
        self.style_menu.set_menu(myMenu)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this report.  This menu will be generated based upon the type
        of document (text, draw, graph, etc. - a subclass), whether or
        not the document requires table support, etc."""
        assert 0, _("The make_doc_menu function must be overridden.")

    def make_document(self):
        """Create a document of the type selected by the user."""
        assert 0, _("The make_document function must be overridden.")

    def doc_type_changed(self, obj):
        """This routine is called when the user selects a new file
        formats for the report.  It adjust the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those chances are made here."""

        # Is this to be a printed report or an electronic report
        # (i.e. a set of web pages)
        if obj.get_data("paper") == 1:
            self.output_notebook.set_page(0)
        else:
            self.output_notebook.set_page(1)

        # Does this report format use styles?
        self.style_frame.set_sensitive(obj.get_data("styles"))

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        self.window = self.topDialog.get_widget("report_dialog")
        self.name = self.person.getPrimaryName().getRegularName()
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""
        name = self.person.getPrimaryName().getRegularName()
        self.header = self.topDialog.get_widget("header_label")
        self.header.set_text(self.get_header(name))
        
    def setup_target_frame(self):
        """Set up the target frame of the dialog.  This function
        relies on several target_xxx() customization functions to
        determine whether the target is a directory or file, what the
        title of any browser window should be, and what default
        directory should be used."""
        self.target_fileentry = self.topDialog.get_widget("fileentry1")
        self.target_fileentry.set_title(self.get_target_browser_title())
        self.target_fileentry.set_default_path(self.get_default_directory())
        if (self.get_target_is_directory()):
            import _gnomeui
            _gnomeui.gnome_file_entry_set_directory(self.target_fileentry._o, 1)
            self.topDialog.get_widget("saveas").set_text(_("Directory"))
        self.target_filename = self.topDialog.get_widget("filename")
        self.target_filename.set_text(self.get_default_directory())

        # Faugh! The following line of code would allow the 'Enter'
        # key in the file name box to close the dialog.  However there
        # is a bug (or is it?) in the closing of the Gnome FileEntry
        # browser that sends the same signal that is sent when the
        # 'Enter' key is pressed.  This causes the report to be run
        # when the browser window is closed instead of waiting for the
        # dialog window OK button to be clicked.  The user does not
        # have a chance to set any other options.
        #
        # self.window.editable_enters(self.target_filename)

    def setup_format_frame(self):
        """Set up the format frame of the dialog.  This function
        relies on the make_doc_menu() function to do all the hard
        work."""
        self.format_menu = self.topDialog.get_widget("format")
        self.make_doc_menu()

    def setup_style_frame(self):
        """Set up the style frame of the dialog.  This function relies
        on other routines create the default style for this report,
        and to read in any user defined styles for this report.  It
        the builds a menu of all the available styles for the user to
        choose from."""
        self.style_frame = self.topDialog.get_widget("style_frame")
        self.style_menu = self.topDialog.get_widget("style_menu")

        # Build the default style set for this report.
        self.default_style = StyleSheet()
        self.make_default_style()

        # Build the initial list of available styles sets.  This
        # includes the default style set and any style sets saved from
        # previous invocations of gramps.
        self.style_sheet_list = StyleSheetList(self.get_stylesheet_savefile(),
                                               self.default_style)

        # Now build the actual menu.
        self.build_style_menu(None)

    def setup_output_notebook(self):
        """Set up the output notebook of the dialog.  This sole
        purpose of this function is to grab a pointer for later use in
        the callback from when the file format is changed."""
        self.output_notebook = self.topDialog.get_widget("output_notebook")
        
    def setup_paper_frame(self):
        """Set up the paper selection frame of the dialog.  This
        function relies on a paper_xxx() customization functions to
        determine whether the pagecount menu should appear and what
        its strings should be."""
        # Paper size and orientation.  Always present in this frame.
        self.papersize_menu = self.topDialog.get_widget("papersize")
        PaperMenu.make_paper_menu(self.papersize_menu)
        self.orientation_menu = self.topDialog.get_widget("orientation")
        PaperMenu.make_orientation_menu(self.orientation_menu)

        # The optional pagecount stuff.
        self.pagecount_menu = self.topDialog.get_widget("pagecount_menu")
        self.pagecount_label = self.topDialog.get_widget("pagecount_label")
        (pagecount_map, start_text) = self.get_print_pagecount_map()
        if pagecount_map:
            myMenu = utils.build_string_optmenu(pagecount_map, start_text)
            self.pagecount_menu.set_menu(myMenu)
        else:
            self.pagecount_menu.hide()
            self.pagecount_label.hide()

    def setup_html_frame(self):
        """Set up the html frame of the dialog.  This sole purpose of
        this function is to grab a pointer for later use in the parse
        html frame function."""
        self.html_fileentry = self.topDialog.get_widget("htmltemplate")

    def setup_report_options_frame(self):
        """Set up the report options frame of the dialog.  This
        function relies on several report_xxx() customization
        functions to determine which of the items should be present in
        this box.  *All* of these items are optional, although the
        generations fields and the filter combo box are used in most
        (but not all) dialog boxes."""

        # Set up the generations spin and page break checkbox
        (use_gen, use_break) = self.get_report_generations()
        self.generations_spinbox = self.topDialog.get_widget("generations")
        self.pagebreak_checkbox = self.topDialog.get_widget("pagebreak")
        if use_gen:
            self.generations_spinbox.set_value(use_gen)
        else:
            self.topDialog.get_widget("gen_label").hide()
            self.generations_spinbox.hide()
            use_break = 0
        if not use_break:
            self.pagebreak_checkbox.hide()

        # Now the filter combo
        self.filter_combo = self.topDialog.get_widget("filter_combo")
        filter_strings = self.get_report_filter_strings()
        if filter_strings:
            filter_strings.sort()
            self.filter_combo.set_popdown_strings(filter_strings)
        else:
            self.topDialog.get_widget("filter_label").hide()
            self.filter_combo.hide()

        # Now the "extra" option menu
        self.extra_menu_label = self.topDialog.get_widget("extra_menu_label")
        self.extra_menu = self.topDialog.get_widget("extra_menu")
        (label, extra_map, preset) = self.get_report_extra_menu_map()
        if extra_map:
            self.extra_menu_label.set_text(label)
            myMenu = utils.build_string_optmenu(extra_map, preset)
            self.extra_menu.set_menu(myMenu)
            self.extra_menu.set_sensitive(len(extra_map) > 1)
        else:
            self.extra_menu_label.hide()
            self.extra_menu.hide()

        # Now the "extra" text box
        self.extra_textbox_label = self.topDialog.get_widget("extra_textbox_label")
        self.extra_textbox = self.topDialog.get_widget("extra_textbox")
        (label, string) = self.get_report_extra_textbox_string()
        if string:
            self.extra_textbox_label.set_text(label)
            self.extra_textbox.insert_defaults(string)
        else:
            self.extra_textbox_label.hide()
            self.topDialog.get_widget("extra_scrolledwindow").hide()
        
    def setup_other_frames(self):
        """Do nothing.  This sole purpose of this function is to give
        subclass a place to hang a routine to handle any other frames
        that are unique to that specific report."""
        pass

    def connect_signals(self):
        """Connect the signal handlers for this dialog.  The signal
        handlers in this default function will handle all of the items
        in the basic report dialog.  Most items do not interact with
        each other, and their vales will be read back when the user
        clicks the OK button.  This dialog only need be sub-classed if
        there is interaction between/within any additional frames
        added in a subclass."""
        self.topDialog.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_style_edit_clicked" : self.on_style_edit_clicked,
            "on_ok_clicked" : self.on_ok_clicked
            })

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
        self.set_default_directory(os.path.dirname(self.target_path) + os.sep)
        return 1

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_menu().get_active().get_data("name")

    def parse_style_frame(self):
        """Parse the style frame of the dialog.  Save the user
        selected output style for later use.  Note that this routine
        retrieves a value whether or not the menu is displayed on the
        screen.  The subclass will know whether this menu was enabled.
        This is for simplicity of programming."""
        self.selected_style = self.style_menu.get_menu().get_active().get_data("d")

    def parse_paper_frame(self):
        """Parse the paper frame of the dialog.  Save the user
        selected choices for later use.  Note that this routine
        retrieves a value from the pagecount menu, whether or not it
        is displayed on the screen.  The subclass will know which ones
        it has enabled.  This is for simplicity of programming."""
        self.paper = self.papersize_menu.get_menu().get_active().get_data("i")
        self.orien = self.orientation_menu.get_menu().get_active().get_data("i")
        self.pagecount = self.pagecount_menu.get_menu().get_active().get_data("d")

    def parse_html_frame(self):
        """Parse the html frame of the dialog.  Save the user selected
        html template name for later use.  Note that this routine
        retrieves a value whether or not the file entry box is
        displayed on the screen.  The subclass will know whether this
        entry was enabled.  This is for simplicity of programming."""
        self.template_name = self.html_fileentry.get_full_path(0)

    def parse_report_options_frame(self):
        """Parse the report options frame of the dialog.  Save the
        user selected choices for later use.  Note that this routine
        retrieves a value from all fields in the frame, regardless of
        whether or not they are displayed on the screen.  The subclass
        will know which ones it has enabled.  This is for simplicity
        of programming."""
        self.max_gen = self.generations_spinbox.get_value_as_int()
        self.pg_brk = self.pagebreak_checkbox.get_active()
        self.filter = self.filter_combo.entry.get_text()
        self.report_menu = self.extra_menu.get_menu().get_active().get_data("d")
        self.report_text = string.split(self.extra_textbox.get_chars(0,-1),'\n')
        
    def parse_other_frames(self):
        """Do nothing.  This sole purpose of this function is to give
        subclass a place to hang a routine to parser any other frames
        that are unique to that specific report."""
        pass

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def on_style_edit_clicked(self, obj):
        """The user has clicked on the 'Edit Styles' button.  Create a
        style sheet editor object and let them play.  When they are
        done, the previous routine will be called to update the dialog
        menu for selecting a style."""
        StyleListDisplay(self.style_sheet_list,self.build_style_menu,None)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices.  Validate
        the output file name before doing anything else.  If there is
        a file name, gather the options and create the report."""

        # Is there a filename?  This should also test file permissions, etc.
        if not self.parse_target_frame():
            return

        # Preparation
        self.parse_format_frame()
        self.parse_style_frame()
        self.parse_paper_frame()
        self.parse_html_frame()
        self.parse_report_options_frame()
        self.parse_other_frames()

        # Create the output document.
        self.make_document()

        # Create the report object and product the report.
        self.make_report()

        # Clean up the dialog object
        utils.destroy_passed_object(obj)

    #------------------------------------------------------------------------
    #
    # Functions related to creating the actual report document.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the contents of the report.  This is the meat and
        potatoes of reports.  The whole purpose of the dialog is to
        get to this routine so that data is written to a file.  This
        routine should either write the data directly to the file, or
        better yet, should create a subclass of a Report that will
        write the data to a file."""
        assert 0, _("The make_report function must be overridden.")

#------------------------------------------------------------------------
#
# TextReportDialog - A class of ReportDialog customized for text based
# reports.
#
#------------------------------------------------------------------------
class TextReportDialog(ReportDialog):
    def __init__(self,database,person,filename):
        """Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information."""
        ReportDialog.__init__(self,database,person,filename)

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def doc_uses_tables(self):
        """Does this report require the ability to generate tables in
        the file format.  Override this for documents that do need
        table support."""
        return 0

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        FindDoc.get_text_doc_menu(self.format_menu, self.doc_uses_tables(),
                                  self.doc_type_changed)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = FindDoc.make_text_doc(self.selected_style,self.format,
                                         self.paper,self.orien,
                                         self.template_name)

    #------------------------------------------------------------------------
    #
    # Functions related to creating the actual report document.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the contents of the report.  This is a simple
        default implementation suitable for testing.  Is should be
        overridden to produce a real report."""
        self.doc.start_paragraph("Title")
        title = "Basic Report for %s" % self.name
        self.doc.write_text(title)
        self.doc.end_paragraph()
            


#------------------------------------------------------------------------
#
# DrawReportDialog - A class of ReportDialog customized for drawing based
# reports.
#
#------------------------------------------------------------------------
class DrawReportDialog(ReportDialog):
    def __init__(self,database,person,filename):
        """Initialize a dialog to request that the user select options
        for a basic drawing report.  See the ReportDialog class for
        more information."""
        ReportDialog.__init__self,database,person,filename()

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this drawing report."""
        FindDoc.get_draw_doc_menu(self.format_menu)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = FindDoc.make_draw_doc(self.selected_style,self.format,
                                         self.paper,self.orien)
