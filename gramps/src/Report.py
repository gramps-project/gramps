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
import Plugins

_ = intl.gettext

from TextDoc import *
from StyleEditor import *

import Config
import PaperMenu

from gtk import *
from gnome.ui import *
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
        return (_("Progress Report - GRAMPS"), _("Working"))

    def progress_bar_setup(self,total):
        """Create a progress dialog.  This routine calls a
        customization function to find out how to fill out the dialog.
        The argument to this function is the maximum number of items
        that the report will progress; i.e. what's considered 100%,
        i.e. the maximum number of times this routine will be
        called."""
        
        # Customize the dialog for this report
        (title, header) = self.get_progressbar_data()
        self.ptop = GnomeDialog()
        self.ptop.set_title(title)
        self.ptop.vbox.add(GtkLabel(header))
        self.ptop.vbox.add(GtkHSeparator())
        self.ptop.vbox.set_spacing(10)
        self.pbar = GtkProgressBar()
        self.pbar.set_format_string(_("%v of %u (%P%%)"))
        self.pbar.configure(0.0,0.0,total)
        self.pbar.set_show_text(1)
        self.pbar.set_usize(350,20)
        self.pbar_max = total
        self.pbar_index = 0.0

        self.ptop.vbox.add(self.pbar)
        self.ptop.show_all()

    # Setup the progress bar limits

    def progress_bar_step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        self.pbar_index = self.pbar_index + 1.0
        if (self.pbar_index > self.pbar_max):
            self.pbar_index = self.pbar_max
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

    frame_pad = 5
    border_pad = 5

    def __init__(self,database,person):
        """Initialize a dialog to request that the user select options
        for a basic report."""

        # Save info about who the report is about.
        self.db = database
        self.person = person
        self.output_notebook = None
        self.notebook_page = 1
        self.pagecount_menu = None
        self.filter_combo = None
        self.extra_menu = None
        self.extra_textbox = None
        self.pagebreak_checkbox = None
        self.generations_spinbox = None
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        
        self.window = GnomeDialog('GRAMPS',STOCK_BUTTON_OK,STOCK_BUTTON_CANCEL)
        self.window.set_default(0)
        self.window.button_connect(0,self.on_ok_clicked)
        self.window.button_connect(1,self.on_cancel)
        self.window.set_resize_mode(0)

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        
        self.add_user_options()

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.
        self.setup_title()
        self.setup_header()
        self.setup_target_frame()
        self.setup_format_frame()
        self.setup_style_frame()
        self.setup_output_notebook()
        self.setup_paper_frame()
        self.setup_html_frame()
        self.setup_report_options_frame()
        self.setup_other_frames()
        self.window.show_all()

        # Allow for post processing of the format frame, since the
        # show_all task calls events that may reset values

    def setup_post_process(self):
        pass
    
    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog."""
        return(_("Base Report - GRAMPS"))

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
        return(_("Save Report As - GRAMPS"))

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
    
    def get_report_extra_menu_info(self):
        """Return the data used to fill out the 'extra' option menu in
        the report options box.  The first value is the string to be
        used as the label to the left of the menu.  The second value
        is a mapping of string:value pairs.  The strings will be used
        to label individual menu items, and the values are what will
        be returned if a given menu item is selected.  The third value
        is the name of menu item to pre-select, and the final value is
        a string to use as the tooltip for the textbox."""
        return (None, None, None, None)
    
    def get_report_extra_textbox_info(self):
        """Return the data used to fill out the 'extra' textbox in the
        report options dialog.  The first value is the string to be
        used as the label to the left of the textbox.  The second
        value is the string to use as the default contents of the
        textbox.  If None, then the text box will be hidden.  The
        final value is a string to use as the tooltip for the
        textbox."""
        return (None, None, None)
    
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
    # Functions related to extending the options
    #
    #------------------------------------------------------------------------
    def add_user_options(self):
        """Called to allow subclasses add widgets to the dialog form.
        It is called immediately before the window is displayed. All
        calls to add_option or add_frame_option should be called in
        this task."""
        pass

    def add_option(self,label_text,widget):
        """Takes a text string and a Gtk Widget, and stores them to be
        appended to the Options section of the dialog. The text string
        is used to create a label for the passed widget. This allows the
        subclass to extend the Options section with its own widgets. The
        subclass is reponsible for all managing of the widgets, including
        extracting the final value before the report executes. This task
        should only be called in the add_user_options task."""
        self.widgets.append((label_text,widget))

    def add_frame_option(self,frame_name,label_text,widget):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""
        
        if self.frames.has_key(frame_name):
            self.frames[frame_name].append((label_text,widget))
        else:
            self.frames[frame_name] = [(label_text,widget)]
            self.frame_names.append(frame_name)
            
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
            self.notebook_page = 0
        else:
            self.notebook_page = 1
            
        if self.output_notebook == None:
            return
        
        self.output_notebook.set_page(self.notebook_page)

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

        title = self.get_title()
        self.name = self.person.getPrimaryName().getRegularName()
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""

        title = self.get_header(self.name)
        label = GtkLabel(title)
        label.set_usize(450,10)
        self.window.vbox.pack_start(label,TRUE,TRUE,ReportDialog.border_pad)
        self.window.vbox.add(GtkHSeparator())
        
    def setup_target_frame(self):
        """Set up the target frame of the dialog.  This function
        relies on several target_xxx() customization functions to
        determine whether the target is a directory or file, what the
        title of any browser window should be, and what default
        directory should be used."""

        # Save Frame
        frame = GtkFrame(_("Save As"))
        frame.set_border_width(ReportDialog.frame_pad)
        hid = self.get_stylesheet_savefile()
        if hid[-4:]==".xml":
            hid = hid[0:-4]
        self.target_fileentry = GnomeFileEntry(hid,_("Save As"))

        hbox = GtkHBox()
        hbox.set_border_width(ReportDialog.border_pad)
        if (self.get_target_is_directory()):
            import _gnomeui
            _gnomeui.gnome_file_entry_set_directory(self.target_fileentry._o, 1)
            label = GtkLabel(_("Directory"))
        else:
            label = GtkLabel(_("Filename"))
        hbox.pack_start(label,0,0,5)
            
        hbox.add(self.target_fileentry)
        frame.add(hbox)
        self.window.vbox.add(frame)

        self.target_fileentry.set_default_path(self.get_default_directory())
        if (self.get_target_is_directory()):
            import _gnomeui
            _gnomeui.gnome_file_entry_set_directory(self.target_fileentry._o, 1)

        target_filename = self.target_fileentry.children()[0].entry
        target_filename.set_text(self.get_default_directory())

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

        self.format_menu = GtkOptionMenu()
        self.make_doc_menu()
        frame = GtkFrame(_("Output Format"))
        frame.add(self.format_menu)
        frame.set_border_width(ReportDialog.frame_pad)        
        self.window.vbox.add(frame)

    def setup_style_frame(self):
        """Set up the style frame of the dialog.  This function relies
        on other routines create the default style for this report,
        and to read in any user defined styles for this report.  It
        the builds a menu of all the available styles for the user to
        choose from."""

        # Styles Frame
        self.style_frame = GtkFrame(_("Styles"))
        hbox = GtkHBox()
        hbox.set_border_width(ReportDialog.border_pad)
        self.style_menu = GtkOptionMenu()
        hbox.pack_start(self.style_menu,TRUE,TRUE,2)
        style_button = GtkButton(_("Style Editor"))
        style_button.connect('clicked',self.on_style_edit_clicked)
        hbox.pack_end(style_button,0,0,2)
        self.style_frame.add(hbox)
        self.style_frame.set_border_width(ReportDialog.frame_pad)
        self.window.vbox.add(self.style_frame)
        
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

        self.output_notebook = GtkNotebook()
        self.paper_frame = GtkFrame(_("Paper Options"))
        self.paper_frame.set_border_width(ReportDialog.frame_pad)
        self.output_notebook.append_page(self.paper_frame,GtkLabel(_("Paper Options")))
        self.html_frame = GtkFrame(_("HTML Options"))
        self.html_frame.set_border_width(ReportDialog.frame_pad)
        self.output_notebook.append_page(self.html_frame,GtkLabel(_("HTML Options")))
        self.output_notebook.set_show_tabs(0)
        self.output_notebook.set_show_border(0)
        self.output_notebook.set_page(self.notebook_page)
        self.window.vbox.add(self.output_notebook)
        
    def setup_paper_frame(self):
        """Set up the paper selection frame of the dialog.  This
        function relies on a paper_xxx() customization functions to
        determine whether the pagecount menu should appear and what
        its strings should be."""

        (pagecount_map, start_text) = self.get_print_pagecount_map()
        if pagecount_map:
            table = GtkTable(2,4)
        else:
            table = GtkTable(1,4)
        self.paper_frame.add(table)
        self.papersize_menu = GtkOptionMenu()
        self.orientation_menu = GtkOptionMenu()
        l = GtkLabel(_("Size"))
        pad = ReportDialog.border_pad
        l.set_alignment(1.0,0.5)
        table.attach(l,0,1,0,1,FILL,FILL,pad,pad)
        table.attach(self.papersize_menu,1,2,0,1,xpadding=pad,ypadding=pad)
        l = GtkLabel(_("Orientation"))
        l.set_alignment(1.0,0.5)
        table.attach(l,2,3,0,1,FILL,FILL,pad,pad)
        table.attach(self.orientation_menu,3,4,0,1,xpadding=pad,ypadding=pad)
        PaperMenu.make_paper_menu(self.papersize_menu)
        PaperMenu.make_orientation_menu(self.orientation_menu)

        # The optional pagecount stuff.
        if pagecount_map:
            self.pagecount_menu = GtkOptionMenu()
            myMenu = utils.build_string_optmenu(pagecount_map, start_text)
            self.pagecount_menu.set_menu(myMenu)
            table.attach(GtkLabel(_("Page Count")),0,1,1,2,FILL,FILL,pad,pad)
            table.attach(self.pagecount_menu,1,2,1,2,xpadding=pad,ypadding=pad)

    def setup_html_frame(self):
        """Set up the html frame of the dialog.  This sole purpose of
        this function is to grab a pointer for later use in the parse
        html frame function."""

        hbox = GtkHBox()
        hbox.set_border_width(ReportDialog.border_pad)
        hbox.pack_start(GtkLabel("Template"),0,0,5)
        self.html_fileentry = GnomeFileEntry(_("HTML Template"),_("Choose File"))
        hbox.add(self.html_fileentry)
        self.html_frame.add(hbox)

    def setup_report_options_frame(self):
        """Set up the report options frame of the dialog.  This
        function relies on several report_xxx() customization
        functions to determine which of the items should be present in
        this box.  *All* of these items are optional, although the
        generations fields and the filter combo box are used in most
        (but not all) dialog boxes."""

        (use_gen, use_break) = self.get_report_generations()
        filter_strings = self.get_report_filter_strings()
        (em_label, extra_map, preset, em_tip) = self.get_report_extra_menu_info()
        (et_label, string, et_tip) = self.get_report_extra_textbox_info()

        row = 0
        max_rows = 0
        if use_gen:
            max_rows = max_rows + 1
            if use_break:
                max_rows = max_rows + 1
        if filter_strings:
            max_rows = max_rows + 1
        if extra_map:
            max_rows = max_rows + 1
        if string:
            max_rows = max_rows + 1

        max_rows = max_rows + len(self.widgets)

        if max_rows == 0:
            return

        frame = GtkFrame(_("Report Options"))
        frame.set_border_width(ReportDialog.frame_pad)
        self.window.vbox.add(frame)
        table = GtkTable(2,max_rows)
        frame.add(table)

        pad = ReportDialog.border_pad
        if filter_strings:
            self.filter_combo = GtkCombo()
            l = GtkLabel(_("Filter"))
            l.set_alignment(1.0,0.5)
            table.attach(l,0,1,row,row+1,FILL,FILL,pad,pad)
            table.attach(self.filter_combo,1,2,row,row+1,xpadding=pad,ypadding=pad)
            filter_strings.sort()
            self.filter_combo.set_popdown_strings(filter_strings)
            row = row + 1
            
        # Set up the generations spin and page break checkbox
        if use_gen:
            self.generations_spinbox = GtkSpinButton(digits=0)
            self.generations_spinbox.set_numeric(1)
            adjustment = GtkAdjustment(use_gen,1,31,1,0)
            self.generations_spinbox.set_adjustment(adjustment)
            adjustment.value_changed()
            l = GtkLabel(_("Generations"))
            l.set_alignment(1.0,0.5)
            table.attach(l,0,1,row,row+1,FILL,FILL,pad,pad)
            table.attach(self.generations_spinbox,1,2,row,row+1,xpadding=pad,ypadding=pad)
            row = row + 1

            if use_break:
                self.pagebreak_checkbox = GtkCheckButton(_("Page break between generations"))
                table.attach(self.pagebreak_checkbox,1,2,row,row+1,xpadding=pad,ypadding=pad)
                row = row + 1

        # Now the "extra" option menu
        if extra_map:
            self.extra_menu_label = GtkLabel(em_label)
            self.extra_menu_label.set_alignment(1.0,0.5)
            self.extra_menu = GtkOptionMenu()
            myMenu = utils.build_string_optmenu(extra_map, preset)
            self.extra_menu.set_menu(myMenu)
            self.extra_menu.set_sensitive(len(extra_map) > 1)
            self.add_tooltip(self.extra_menu,em_tip)
            table.attach(self.extra_menu_label,0,1,row,row+1,FILL,FILL,pad,pad)
            table.attach(self.extra_menu,1,2,row,row+1,xpadding=pad,ypadding=pad)
            row = row + 1
            
        # Now the "extra" text box
        if string:
            self.extra_textbox_label = GtkLabel(et_label)
            self.extra_textbox_label.set_alignment(1.0,0)
            self.extra_textbox = GtkText()
            self.extra_textbox.insert_defaults(string)
            self.extra_textbox.set_editable(1)
            self.add_tooltip(self.extra_textbox,et_tip)
            table.attach(self.extra_textbox_label,0,1,row,row+1,FILL,FILL,pad,pad)
            table.attach(self.extra_textbox,1,2,row,row+1,xpadding=pad,ypadding=pad)
            row = row + 1
#            self.topDialog.get_widget("extra_scrolledwindow").show()

        # Setup requested widgets
        for (text,widget) in self.widgets:
            if text == None:
                table.attach(widget,0,2,row,row+1,xpadding=pad,ypadding=pad)
            else:
                text_widget = GtkLabel(text)
                text_widget.set_alignment(1.0,0)
                table.attach(text_widget,0,1,row,row+1,FILL,FILL,pad,pad)
                table.attach(widget,1,2,row,row+1,xpadding=pad,ypadding=pad)
            row = row + 1
        
    def setup_other_frames(self):
        pad = ReportDialog.border_pad
        for key in self.frame_names:
            frame = GtkFrame(key)
            frame.set_border_width(ReportDialog.frame_pad)
            self.window.vbox.add(frame)
            list = self.frames[key]
            table = GtkTable(2,len(list))
            frame.add(table)

            row = 0
            for (text,widget) in list:
                if text == None:
                    table.attach(widget,0,2,row,row+1,xpadding=pad,ypadding=pad)
                else:
                    text_widget = GtkLabel(text)
                    text_widget.set_alignment(1.0,0)
                    table.attach(text_widget,0,1,row,row+1,FILL,FILL,pad,pad)
                    table.attach(widget,1,2,row,row+1,xpadding=pad,ypadding=pad)
                row = row + 1

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
        if self.pagecount_menu == None:
            self.pagecount = 0
        else:
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

        if self.generations_spinbox:
            self.max_gen = self.generations_spinbox.get_value_as_int()
        else:
            self.max_gen = 0
            
        if self.pagebreak_checkbox:
            self.pg_brk = self.pagebreak_checkbox.get_active()
        else:
            self.pg_brk = 0

        if self.filter_combo:
            self.filter = self.filter_combo.entry.get_text()
        else:
            self.filter = ""

        if self.extra_menu:
            self.report_menu = self.extra_menu.get_menu().get_active().get_data("d")
        else:
            self.report_menu = None

        if self.extra_textbox:
            self.report_text = string.split(self.extra_textbox.get_chars(0,-1),'\n')
        else:
            self.report_text = ""
        
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

    def on_cancel(self, obj):
        self.window.destroy()

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
        self.window.destroy()

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
    # Miscellaneous functions.
    #
    #------------------------------------------------------------------------
    def add_tooltip(self,widget,string):
        if not widget or not string:
            return
        tip = gtk.GtkTooltips()
        tip.set_tip(widget,string)

#------------------------------------------------------------------------
#
# TextReportDialog - A class of ReportDialog customized for text based
# reports.
#
#------------------------------------------------------------------------
class TextReportDialog(ReportDialog):
    def __init__(self,database,person):
        """Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information."""
        ReportDialog.__init__(self,database,person)

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
        Plugins.get_text_doc_menu(self.format_menu, self.doc_uses_tables(),
                                  self.doc_type_changed)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = self.format(self.selected_style,self.paper,
                               self.template_name,self.orien)

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
    def __init__(self,database,person):
        """Initialize a dialog to request that the user select options
        for a basic drawing report.  See the ReportDialog class for
        more information."""
        ReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this drawing report."""
        Plugins.get_draw_doc_menu(self.format_menu)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = self.format(self.selected_style,self.paper,self.orien)
