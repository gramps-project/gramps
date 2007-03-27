#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
from types import ClassType, InstanceType
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from BasicUtils import NameDisplay
import BaseDoc
import Utils

import ManagedWindow
from _StyleComboBox import StyleComboBox
from _StyleEditor import StyleListDisplay

import logging

log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# BareReportDialog class
#
#-------------------------------------------------------------------------
class BareReportDialog(ManagedWindow.ManagedWindow):
    """
    The BareReportDialog base class.  This is a base class for generating
    customized dialogs to solicit some options for a report.  This class 
    cannot be meaningfully used on its own since normally more options will 
    have to be solicited. The ReportDialog class adds this functionality.
    The intended use of this class is either for ReportDialog or for being 
    subclassed by Bare Reports that are part of the Book.
    """

    frame_pad = 5
    border_pad = 6
    HELP_TOPIC = None

    def __init__(self,dbstate,uistate,person,option_class,
                 name,translated_name,track=[]):
        """Initialize a dialog to request that the user select options
        for a basic *bare* report."""

        self.dbstate = dbstate
        self.uistate = uistate
        self.db = dbstate.db
        self.person = person
        self.report_name = translated_name
        self.raw_name = name

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        if type(option_class) == ClassType:
            self.options = option_class(name)
        elif type(option_class) == InstanceType:
            self.options = option_class

        self.init_interface()

    def build_window_key(self,obj):
        key = self.raw_name
        if self.person:
            key += self.person.get_handle()
        return key

    def build_menu_names(self,obj):
        return (_("Configuration"),self.report_name)

    def init_interface(self):
        self.extra_menu = None
        self.extra_textbox = None
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        self.format_menu = None
        self.style_button = None

        self.style_name = self.options.handler.get_default_stylesheet_name()

        window = gtk.Dialog('GRAMPS')
        self.set_window(window,None,self.get_title())
        self.window.set_has_separator(False)

        if self.HELP_TOPIC:
            self.help = self.window.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
            self.help.connect('clicked',self.on_help_clicked)

        self.cancel = self.window.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.cancel.connect('clicked',self.on_cancel)

        self.ok = self.window.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
        self.ok.connect('clicked',self.on_ok_clicked)

        self.window.set_default_size(600,-1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()
        self.tbl = gtk.Table(4,4,False)
        self.tbl.set_col_spacings(12)
        self.tbl.set_row_spacings(6)
        self.tbl.set_border_width(6)
        self.col = 0
        self.window.vbox.add(self.tbl)

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        self.add_user_options()

        self.setup_center_person()
        self.setup_target_frame()
        self.setup_format_frame()
        self.setup_style_frame()
        #self.setup_output_notebook()
        
        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.vbox.add(self.notebook)

        self.setup_paper_frame()
        self.setup_html_frame()
        self.setup_report_options_frame()
        self.setup_other_frames()
        self.notebook.set_current_page(0)
        self.window.show_all()

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % self.report_name

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        selected person.  Most subclasses will customize this to give
        some indication of what the report will be, i.e. 'Descendant
        Report for %s'."""
        return _("%(report_name)s for GRAMPS Book") % { 
                    'report_name' : self.report_name}
        
    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def get_stylesheet_savefile(self):
        """Where should new styles for this report be saved?  This is
        the name of an XML file that will be located in the ~/.gramps
        directory.  This file does not have to exist; it will be
        created when needed.  All subclasses should probably override
        this function."""
        return "basic_report.xml"
    
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
            log.error("Failed to parse user options.", exc_info=True)
            

    def add_option(self,label_text,widget,tooltip=None):
        """Takes a text string and a Gtk Widget, and stores them to be
        appended to the Options section of the dialog. The text string
        is used to create a label for the passed widget. This allows the
        subclass to extend the Options section with its own widgets. The
        subclass is reponsible for all managing of the widgets, including
        extracting the final value before the report executes. This task
        should only be called in the add_user_options task."""
        self.widgets.append((label_text,widget))
        if tooltip:
            self.add_tooltip(widget,tooltip)

    def add_frame_option(self,frame_name,label_text,widget,tooltip=None):
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
        if tooltip:
            self.add_tooltip(widget,tooltip)
        
    #------------------------------------------------------------------------
    #
    # Functions to create a default output style.
    #
    #------------------------------------------------------------------------

    def build_style_menu(self,default=None):
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
        self.style_menu.set(style_sheet_map,default)

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        if self.person:
            self.name = NameDisplay.displayer.display(self.person)
        else:
            self.name = ''
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""

        title = self.get_header(self.name)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        self.window.vbox.pack_start(label, True, True,
                                    BareReportDialog.border_pad)
        
    def setup_target_frame(self):
        """Bare report dialog only uses Doc Options header."""

        label = gtk.Label("<b>%s</b>" % _('Document Options'))
        label.set_use_markup(1)
        label.set_alignment(0.0,0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(label, 0, 4, self.col, self.col+1, gtk.FILL|gtk.EXPAND)
        self.col += 1

    def setup_center_person(self): 
        """Set up center person labels and change button. 
        Should be overwritten by standalone report dialogs. """

        center_label = gtk.Label("<b>%s</b>" % _("Center Person"))
        center_label.set_use_markup(True)
        center_label.set_alignment(0.0,0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(center_label,0,4,self.col,self.col+1)
        self.col += 1

        name = NameDisplay.displayer.display(self.person)
        self.person_label = gtk.Label( "%s" % name )
        self.person_label.set_alignment(0.0,0.5)
        self.tbl.attach(self.person_label,2,3,self.col,self.col+1)
        
        change_button = gtk.Button("%s..." % _('C_hange') )
        change_button.connect('clicked',self.on_center_person_change_clicked)
        self.tbl.attach(change_button,3,4,self.col,self.col+1,gtk.SHRINK)
        self.col += 1

    def setup_style_frame(self):
        """Set up the style frame of the dialog.  This function relies
        on other routines create the default style for this report,
        and to read in any user defined styles for this report.  It
        the builds a menu of all the available styles for the user to
        choose from."""

        # Styles Frame
        label = gtk.Label("%s:" % _("Style"))
        label.set_alignment(0.0,0.5)

        self.style_menu = StyleComboBox()
        self.style_button = gtk.Button("%s..." % _("Style Editor"))
        self.style_button.connect('clicked',self.on_style_edit_clicked)

        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.style_menu,2,3,self.col,self.col+1,
                        yoptions=gtk.SHRINK)
        self.tbl.attach(self.style_button,3,4,self.col,self.col+1,
                        xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK)
        self.col += 1
        
        # Build the default style set for this report.
        self.default_style = BaseDoc.StyleSheet()
        self.options.make_default_style(self.default_style)

        # Build the initial list of available styles sets.  This
        # includes the default style set and any style sets saved from
        # previous invocations of gramps.
        self.style_sheet_list = BaseDoc.StyleSheetList(
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

        table = gtk.Table(3,max_rows+1)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        
        label = gtk.Label("<b>%s</b>" % _("Report Options"))
        label.set_alignment(0.0,0.5)
        label.set_use_markup(True)
        
        table.set_border_width(6)
        self.notebook.append_page(table,label)
        row += 1

        # Setup requested widgets
        for (text,widget) in self.widgets:
            if text:
                text_widget = gtk.Label("%s:" % text)
                text_widget.set_alignment(0.0,0.0)
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
            flist = self.frames[key]
            table = gtk.Table(3,len(flist))
            table.set_col_spacings(12)
            table.set_row_spacings(6)
            table.set_border_width(6)
            l = gtk.Label("<b>%s</b>" % _(key))
            l.set_use_markup(True)
            self.notebook.append_page(table,l)

            row = 0
            for (text,widget) in flist:
                if text:
                    text_widget = gtk.Label('%s:' % text)
                    text_widget.set_alignment(0.0,0.5)
                    table.attach(text_widget, 1, 2, row, row+1,
                                 gtk.SHRINK|gtk.FILL, gtk.SHRINK)
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                else:
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                row = row + 1

    #------------------------------------------------------------------------
    #
    # Customization hooks for stand-alone reports (subclass ReportDialog)
    #
    #------------------------------------------------------------------------
    def setup_format_frame(self): 
        """Not used in bare report dialogs. Override in the subclass."""
        pass

    def setup_paper_frame(self):
        """Not used in bare report dialogs. Override in the subclass."""
        pass

    def setup_html_frame(self):
        """Not used in bare report dialogs. Override in the subclass."""
        pass

    def setup_output_notebook(self):
        """Not used in bare report dialogs. Override in the subclass."""
        pass
    
    #------------------------------------------------------------------------
    #
    # Functions related to retrieving data from the dialog window
    #
    #------------------------------------------------------------------------
    def parse_style_frame(self):
        """Parse the style frame of the dialog.  Save the user
        selected output style for later use.  Note that this routine
        retrieves a value whether or not the menu is displayed on the
        screen.  The subclass will know whether this menu was enabled.
        This is for simplicity of programming."""
        (style_name,self.selected_style) = self.style_menu.get_value()
        self.options.handler.set_default_stylesheet_name(style_name)

    def parse_report_options_frame(self):
        """Parse the report options frame of the dialog.  Save the
        user selected choices for later use.  Note that this routine
        retrieves a value from all fields in the frame, regardless of
        whether or not they are displayed on the screen.  The subclass
        will know which ones it has enabled.  This is for simplicity
        of programming."""
        if self.extra_menu:
            self.report_menu = self.extra_menu.get_menu().get_active().get_data("d")
        else:
            self.report_menu = None
        
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
    def on_cancel(self,*obj):
        pass

    def on_help_clicked(self, *obj):
        if self.HELP_TOPIC:
            import GrampsDisplay
            GrampsDisplay.help(self.HELP_TOPIC)
        print "HELP CLICKED"

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        self.parse_other_frames()
        self.parse_user_options()
        
        # Save options
        self.options.handler.save_options()

    def on_style_edit_clicked(self, *obj):
        """The user has clicked on the 'Edit Styles' button.  Create a
        style sheet editor object and let them play.  When they are
        done, the previous routine will be called to update the dialog
        menu for selecting a style."""
        StyleListDisplay(self.style_sheet_list,self.build_style_menu,
                         self.window)

    def on_center_person_change_clicked(self,*obj):
        from Selectors import selector_factory
        SelectPerson = selector_factory('Person')
        sel_person = SelectPerson(self.dbstate,self.uistate,self.track)
        new_person = sel_person.run()
        if new_person:
            self.new_person = new_person
            new_name = NameDisplay.displayer.display(new_person)
            if new_name:
                self.person_label.set_text( "<i>%s</i>" % new_name )
                self.person_label.set_use_markup(True)

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
        pass

    #------------------------------------------------------------------------
    #
    # Miscellaneous functions.
    #
    #------------------------------------------------------------------------
    def add_tooltip(self,widget,string):
        """Adds a tooltip to the specified widget"""
        if not widget or not string:
            return
        tip = gtk.Tooltips()
        tip.set_tip(widget,string)
