#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
# Copyright (C) 2001-2003  Donald N. Allingham
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

"Report Generation Framework"

__author__ =  "David R. Hampton, Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gnome
import gnome.ui

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Plugins
import GenericFilter
import BaseDoc
import StyleEditor
import GrampsCfg
import PaperMenu

from gettext import gettext as _
from QuestionDialog import  ErrorDialog, OptionDialog

#-------------------------------------------------------------------------
#
# Import XML libraries
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_default_template = _("Default Template")
_user_template = _("User Defined Template")

_template_map = {
    _user_template : None
    }

#-------------------------------------------------------------------------
#
# Support for printing generated files
#
#-------------------------------------------------------------------------
def get_print_dialog_app ():
    """Return the name of a program which sends stdin (or the program's
    arguments) to the printer."""
    for printdialog in ["/usr/bin/kprinter --stdin",
                        "/usr/share/printconf/util/print.py"]:
        if os.access (printdialog.split (' ')[0], os.X_OK):
            return printdialog

    return "lpr"

def run_print_dialog (filename):
    """Send file to the printer, possibly throwing up a dialog to
    ask which one etc."""
    os.environ["FILE"] = filename
    return os.system ('cat "$FILE" | %s &' % get_print_dialog_app ())

#-------------------------------------------------------------------------
#
# Report
#
#-------------------------------------------------------------------------
class Report:
    """
    The Report base class.  This is a base class for generating
    customized reports.  It cannot be used as is, but it can be easily
    sub-classed to create a functional report generator.
    """

    # Ordinal generation names.  Used by multiple reports.
    gen = {
        1 : _("First"),          2 : _("Second"),
        3 : _("Third"),          4 : _("Fourth"),
        5 : _("Fifth"),          6 : _("Sixth"),
        7 : _("Seventh"),        8 : _("Eighth"),
        9 : _("Ninth"),          10: _("Tenth"),
        11: _("Eleventh"),       12: _("Twelfth"),
        13: _("Thirteenth"),     14: _("Fourteenth"),
        15: _("Fifteenth"),      16: _("Sixteenth"),
        17: _("Seventeenth"),    18: _("Eighteenth"),
        19: _("Nineteenth"),     20: _("Twentieth"),
        21: _("Twenty-first"),   22: _("Twenty-second"),
        23: _("Twenty-third"),   24: _("Twenty-fourth"),
        25: _("Twenty-fifth"),   26: _("Twenty-sixth"),
        27: _("Twenty-seventh"), 28: _("Twenty-eighth"),
        29: _("Twenty-ninth")
        }

    def get_progressbar_data(self):
        """The window title for this dialog, and the header line to
        put at the top of the contents of the dialog box."""
        return ("%s - GRAMPS" % _("Progress Report"), _("Working"))

    def progress_bar_setup(self,total):
        """Create a progress dialog.  This routine calls a
        customization function to find out how to fill out the dialog.
        The argument to this function is the maximum number of items
        that the report will progress; i.e. what's considered 100%,
        i.e. the maximum number of times this routine will be
        called."""
        
        # Customize the dialog for this report
        (title, header) = self.get_progressbar_data()
        self.ptop = gtk.Dialog()
        self.ptop.set_has_separator(gtk.FALSE)
        self.ptop.set_title(title)
        self.ptop.vbox.add(gtk.Label(header))
        self.ptop.vbox.set_spacing(10)
        self.pbar = gtk.ProgressBar()
        self.pbar_max = total
        self.pbar_index = 0.0

        self.ptop.set_size_request(350,100)
        self.ptop.vbox.add(self.pbar)
        self.ptop.show_all()

    def progress_bar_step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        self.pbar_index = self.pbar_index + 1.0
        if (self.pbar_index > self.pbar_max):
            self.pbar_index = self.pbar_max

        val = self.pbar_index/self.pbar_max
        
        self.pbar.set_text("%d of %d (%.1f%%)" % (self.pbar_index,self.pbar_max,(val*100)))
        self.pbar.set_fraction(val)

    def progress_bar_done(self):
        """Done with the progress bar.  It can be destroyed now."""
        Utils.destroy_passed_object(self.ptop)


class BareReportDialog:
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

    def __init__(self,database,person,options={}):
        """Initialize a dialog to request that the user select options
        for a basic *bare* report."""

        # Save info about who the report is about.
        self.option_store = options
            
        self.style_name = "default"
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
        self.format_menu = None
        self.style_button = None
        
        self.window = gtk.Dialog('GRAMPS')
        self.window.set_has_separator(gtk.FALSE)
        self.cancel = self.window.add_button(gtk.STOCK_CANCEL,1)
        self.ok = self.window.add_button(gtk.STOCK_OK,0)

        self.ok.connect('clicked',self.on_ok_clicked)
        self.cancel.connect('clicked',self.on_cancel)

        self.window.set_response_sensitive(0,gtk.TRUE)
        self.window.set_response_sensitive(1,gtk.TRUE)
        self.window.set_resize_mode(0)

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        
        self.add_user_options()

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()
        self.tbl = gtk.Table(4,4,gtk.FALSE)
        self.tbl.set_col_spacings(12)
        self.tbl.set_row_spacings(6)
        self.tbl.set_border_width(6)
        self.col = 0
        self.window.vbox.add(self.tbl)
        self.setup_center_person()
        self.setup_target_frame()
        self.setup_format_frame()
        self.setup_style_frame()
        self.setup_output_notebook()
        self.setup_paper_frame()
        self.setup_html_frame()
        self.setup_report_options_frame()
        self.setup_other_frames()
        self.window.show_all()

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog."""
        return('')

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        selected person.  Most subclasses will customize this to give
        some indication of what the report will be, i.e. 'Descendant
        Report for %s'."""
        return(name)
        
    def get_stylesheet_savefile(self):
        """Where should new styles for this report be saved?  This is
        the name of an XML file that will be located in the ~/.gramps
        directory.  This file does not have to exist; it will be
        created when needed.  All subclasses should probably override
        this function."""
        return "basic_report.xml"

    def get_report_filters(self):
        """Return the data used to fill out the 'filter' combo box in
        the report options box.  The return value is the list of
        strings to be inserted into the pulldown."""
        return []
    
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
    # Functions related to extending the options
    #
    #------------------------------------------------------------------------
    def add_user_options(self):
        """Called to allow subclasses add widgets to the dialog form.
        It is called immediately before the window is displayed. All
        calls to add_option or add_frame_option should be called in
        this task."""
        pass

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
    def make_default_style(self):
        """Create the default style to be used by the associated report.  This
        routine is a default implementation and should be overridden."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set(pad=0.5)
        self.default_style.add_style("Title",para)

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
        myMenu = Utils.build_string_optmenu(style_sheet_map, default)
        self.style_menu.set_menu(myMenu)

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        self.name = self.person.getPrimaryName().getRegularName()
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""

        title = self.get_header(self.name)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        label.set_use_markup(gtk.TRUE)
        self.window.vbox.pack_start(label,gtk.TRUE,gtk.TRUE,ReportDialog.border_pad)
        
    def setup_target_frame(self):
        """Bare report dialog only uses Doc Options header."""

        label = gtk.Label("<b>%s</b>" % _('Document Options'))
        label.set_use_markup(1)
        label.set_alignment(0.0,0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(label,0,4,self.col,self.col+1)
        self.col += 1

    def setup_center_person(self): 
        """Set up center person labels and change button. 
        Should be overwritten by standalone report dialogs. """

        center_label = gtk.Label("<b>%s</b>" % _("Center Person"))
        center_label.set_use_markup(gtk.TRUE)
        center_label.set_alignment(0.0,0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(center_label,0,4,self.col,self.col+1)
        self.col += 1

        name = self.person.getPrimaryName().getRegularName()
        self.person_label = gtk.Label( "%s" % name )
        self.person_label.set_alignment(0.0,0.5)
        self.tbl.attach(self.person_label,2,3,self.col,self.col+1)
        
        change_button = gtk.Button("%s..." % _('C_hange') )
        change_button.connect('clicked',self.on_center_person_change_clicked)
        self.tbl.attach(change_button,3,4,self.col,self.col+1,gtk.SHRINK|gtk.SHRINK)
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

        self.style_menu = gtk.OptionMenu()
        self.style_button = gtk.Button("%s..." % _("Style Editor"))
        self.style_button.connect('clicked',self.on_style_edit_clicked)

        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.style_menu,2,3,self.col,self.col+1)
        self.tbl.attach(self.style_button,3,4,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.col += 1
        
        # Build the default style set for this report.
        self.default_style = BaseDoc.StyleSheet()
        self.make_default_style()

        # Build the initial list of available styles sets.  This
        # includes the default style set and any style sets saved from
        # previous invocations of gramps.
        self.style_sheet_list = BaseDoc.StyleSheetList(self.get_stylesheet_savefile(),
                                                       self.default_style)

        # Now build the actual menu.
        style = self.option_store.get('style',self.default_style.get_name())
        self.build_style_menu(style)

    def setup_report_options_frame(self):
        """Set up the report options frame of the dialog.  This
        function relies on several report_xxx() customization
        functions to determine which of the items should be present in
        this box.  *All* of these items are optional, although the
        generations fields and the filter combo box are used in most
        (but not all) dialog boxes."""

        (use_gen, use_break) = self.get_report_generations()
        local_filters = self.get_report_filters()
        (em_label, extra_map, preset, em_tip) = self.get_report_extra_menu_info()
        (et_label, string, et_tip) = self.get_report_extra_textbox_info()

        row = 0
        max_rows = 0
        if use_gen:
            max_rows = max_rows + 1
            if use_break:
                max_rows = max_rows + 1
        if len(local_filters):
            max_rows = max_rows + 1
        if extra_map:
            max_rows = max_rows + 1
        if string:
            max_rows = max_rows + 1

        max_rows = max_rows + len(self.widgets)

        if max_rows == 0:
            return

        table = gtk.Table(3,max_rows+1)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        
        label = gtk.Label("<b>%s</b>" % _("Report Options"))
        label.set_alignment(0.0,0.5)
        label.set_use_markup(gtk.TRUE)
        
        if len(self.frame_names) == 0:
            table.attach(label,0,3,0,1)
            table.set_border_width(12)
            self.window.vbox.add(table)
        else:
            table.set_border_width(6)
            self.notebook = gtk.Notebook()
            self.notebook.set_border_width(6)
            self.window.vbox.add(self.notebook)
            self.notebook.append_page(table,label)
        row += 1

        if len(local_filters):
            self.filter_combo = gtk.OptionMenu()
            l = gtk.Label("%s:" % _("Filter"))
            l.set_alignment(0.0,0.5)
            table.attach(l,1,2,row,row+1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
            table.attach(self.filter_combo,2,3,row,row+1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
            menu = GenericFilter.build_filter_menu(local_filters,self.option_store.get('filter',''))

            self.filter_combo.set_menu(menu)
            self.filter_menu = menu
            row += 1
            
        # Set up the generations spin and page break checkbox
        if use_gen:
            self.generations_spinbox = gtk.SpinButton(digits=0)
            self.generations_spinbox.set_numeric(1)
            adjustment = gtk.Adjustment(use_gen,1,31,1,0)
            self.generations_spinbox.set_adjustment(adjustment)
            adjustment.value_changed()
            l = gtk.Label("%s:" % _("Generations"))
            l.set_alignment(0.0,0.5)
            table.attach(l,1,2,row,row+1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
            table.attach(self.generations_spinbox,2,3,row,row+1,gtk.EXPAND|gtk.FILL,gtk.SHRINK|gtk.FILL)
            row += 1

            if use_break:
                msg = _("Page break between generations")
                self.pagebreak_checkbox = gtk.CheckButton(msg)
                table.attach(self.pagebreak_checkbox,2,3,row,row+1)
                row += 1

        # Now the "extra" option menu
        if extra_map:
            self.extra_menu_label = gtk.Label("%s:" % em_label)
            self.extra_menu_label.set_alignment(0.0,0.5)
            self.extra_menu = gtk.OptionMenu()
            myMenu = Utils.build_string_optmenu(extra_map, preset)
            self.extra_menu.set_menu(myMenu)
            self.extra_menu.set_sensitive(len(extra_map) > 1)
            self.add_tooltip(self.extra_menu,em_tip)
            table.attach(self.extra_menu_label,1,2,row,row+1,gtk.SHRINK|gtk.FILL)
            table.attach(self.extra_menu,2,3,row,row+1)
            row += 1
            
        # Now the "extra" text box
        if string:
            self.extra_textbox_label = gtk.Label("%s:" % et_label)
            self.extra_textbox_label.set_alignment(0.0,0)
            swin = gtk.ScrolledWindow()
            swin.set_shadow_type(gtk.SHADOW_IN)
            swin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
            self.extra_textbox = gtk.TextView()
            swin.add(self.extra_textbox)
            
            try:
                self.extra_textbox.get_buffer().set_text(string,len(string))
            except TypeError:
                self.extra_textbox.get_buffer().set_text(string)

            self.extra_textbox.set_editable(1)
            self.add_tooltip(self.extra_textbox,et_tip)
            table.attach(self.extra_textbox_label,1,2,row,row+1,gtk.SHRINK|gtk.FILL)
            table.attach(swin,2,3,row,row+1)
            row += 1

        # Setup requested widgets
        for (text,widget) in self.widgets:
            if text:
                text_widget = gtk.Label("%s:" % text)
                text_widget.set_alignment(0.0,0.0)
                table.attach(text_widget,1,2,row,row+1,gtk.SHRINK|gtk.FILL)
                table.attach(widget,2,3,row,row+1)
            else:
                table.attach(widget,2,3,row,row+1)
            row += 1

    def setup_other_frames(self):
        for key in self.frame_names:
            list = self.frames[key]
            table = gtk.Table(3,len(list))
            table.set_col_spacings(12)
            table.set_row_spacings(6)
            table.set_border_width(6)
            l = gtk.Label("<b>%s</b>" % _(key))
            l.set_use_markup(gtk.TRUE)
            self.notebook.append_page(table,l)

            row = 0
            for (text,widget) in list:
                if text:
                    text_widget = gtk.Label('%s:' % text)
                    text_widget.set_alignment(0.0,0.5)
                    table.attach(text_widget,1,2,row,row+1,gtk.SHRINK|gtk.FILL)
                    table.attach(widget,2,3,row,row+1)
                else:
                    table.attach(widget,2,3,row,row+1)
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
        item = self.style_menu.get_menu().get_active()
        self.selected_style = item.get_data("d")
        style_name = item.get_data('l')
        self.option_store['style'] = style_name

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
            self.filter = self.filter_menu.get_active().get_data("filter")
            self.option_store['filter'] = self.filter.get_name()
        else:
            self.filter = None

        if self.extra_menu:
            self.report_menu = self.extra_menu.get_menu().get_active().get_data("d")
        else:
            self.report_menu = None

        if self.extra_textbox:
            b = self.extra_textbox.get_buffer()
            text_val = unicode(b.get_text(b.get_start_iter(),b.get_end_iter(),gtk.FALSE))
            self.report_text = text_val.split('\n')
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
    def on_cancel(self,obj):
        self.window.destroy()

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        self.parse_other_frames()
        
        # Clean up the dialog object
        self.window.destroy()

    def on_style_edit_clicked(self, obj):
        """The user has clicked on the 'Edit Styles' button.  Create a
        style sheet editor object and let them play.  When they are
        done, the previous routine will be called to update the dialog
        menu for selecting a style."""
        StyleEditor.StyleListDisplay(self.style_sheet_list,self.build_style_menu)

    def on_center_person_change_clicked(self,obj):
        import SelectPerson
        sel_person = SelectPerson.SelectPerson(self.db,'Select Person')
        new_person = sel_person.run()
        if new_person:
            self.new_person = new_person
            new_name = new_person.getPrimaryName().getRegularName()
	    if new_name:
                self.person_label.set_text( "<i>%s</i>" % new_name )
                self.person_label.set_use_markup(gtk.TRUE)

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


class ReportDialog(BareReportDialog):
    """
    The ReportDialog base class.  This is a base class for generating
    customized dialogs to solicit options for a report.  It cannot be
    used as is, but it can be easily sub-classed to create a functional
    dialog for a stand-alone report.
    """

    def __init__(self,database,person,options={}):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""
        
        self.style_name = "default"
        BareReportDialog.__init__(self,database,person,options)

        # Allow for post processing of the format frame, since the
        # show_all task calls events that may reset values

        if self.format_menu:
            self.doc_type_changed(self.format_menu.get_menu().get_active())
        self.setup_post_process()

    def setup_post_process(self):
        pass

    def setup_center_person(self): pass

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def get_target_browser_title(self):
        """The title of the window that will be created when the user
        clicks the 'Browse' button in the 'Save As' File Entry
        widget."""
        return("%s - GRAMPS" % _("Save Report As"))

    def get_target_is_directory(self):
        """Is the user being asked to input the name of a file or a
        directory in the 'Save As' File Entry widget.  This item
        currently only selects the Filename/Directory prompt, and
        whether or not the browser accepts filenames.  In the future it
        may also control checking of the selected filename."""
        return None
    
    def get_default_basename(self):
        """What should the default name be?
        """
        spath = self.get_stylesheet_savefile()
        return spath.split('.')[0]

    def get_print_pagecount_map(self):
        """Return the data used to fill out the 'pagecount' option
        menu in the print options box.  The first value is a mapping
        of string:value pairs.  The strings will be used to label
        individual menu items, and the values are what will be
        returned if a given menu item is selected.  The second value
        is the name of menu item to pre-select."""
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
        return GrampsCfg.report_dir

    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        GrampsCfg.report_dir = value

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
        pass

    def make_document(self):
        """Create a document of the type selected by the user."""
        pass

    def doc_type_changed(self, obj):
        """This routine is called when the user selects a new file
        formats for the report.  It adjust the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those chances are made here."""

        label = obj.get_data("printable")
        if label:
            self.print_report.set_label (label)
            self.print_report.set_sensitive (gtk.TRUE)
        else:
            self.print_report.set_label (_("Print a copy"))
            self.print_report.set_sensitive (gtk.FALSE)

        # Is this to be a printed report or an electronic report
        # (i.e. a set of web pages)

        if obj.get_data("paper") == 1:
            self.notebook_page = 0
        else:
            self.notebook_page = 1
            
        if self.output_notebook == None:
            return
        
        self.output_notebook.set_current_page(self.notebook_page)

        if not self.get_target_is_directory():
            fname = self.target_fileentry.get_full_path(0)
            (spath,ext) = os.path.splitext(fname)

            ext_val = obj.get_data('ext')
            if ext_val:
                fname = spath + ext_val
            self.target_fileentry.set_filename(fname)

        # Does this report format use styles?
        if self.style_button:
            self.style_button.set_sensitive(obj.get_data("styles"))
            self.style_menu.set_sensitive(obj.get_data("styles"))

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def setup_target_frame(self):
        """Set up the target frame of the dialog.  This function
        relies on several target_xxx() customization functions to
        determine whether the target is a directory or file, what the
        title of any browser window should be, and what default
        directory should be used."""

        # Save Frame

        label = gtk.Label("<b>%s</b>" % _('Document Options'))
        label.set_use_markup(1)
        label.set_alignment(0.0,0.5)
        self.tbl.set_border_width(12)
        self.tbl.attach(label,0,4,self.col,self.col+1)
        self.col += 1
        
        hid = self.get_stylesheet_savefile()
        if hid[-4:]==".xml":
            hid = hid[0:-4]
        self.target_fileentry = gnome.ui.FileEntry(hid,_("Save As"))

        if self.get_target_is_directory():
            self.target_fileentry.set_directory_entry(1)
            label = gtk.Label("%s:" % _("Directory"))
        else:
            label = gtk.Label("%s:" % _("Filename"))
        label.set_alignment(0.0,0.5)

        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.target_fileentry,2,4,self.col,self.col+1)
        self.col += 1
        
        spath = self.get_default_directory()

        self.target_fileentry.set_default_path(spath)
        self.target_fileentry.set_filename(spath)
        self.target_fileentry.gtk_entry().set_position(len(spath))

    def setup_format_frame(self):
        """Set up the format frame of the dialog.  This function
        relies on the make_doc_menu() function to do all the hard
        work."""

        self.print_report = gtk.CheckButton (_("Print a copy"))
        self.tbl.attach(self.print_report,2,4,self.col,self.col+1)
        self.col += 1

        self.format_menu = gtk.OptionMenu()
        self.make_doc_menu()
        label = gtk.Label("%s:" % _("Output Format"))
        label.set_alignment(0.0,0.5)
        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.format_menu,2,4,self.col,self.col+1)
        self.col += 1

        type = self.format_menu.get_menu().get_active()
        ext = type.get_data('ext')
        if ext == None:
            ext = ""
        if type:
            spath = self.get_default_directory()
            if self.get_target_is_directory():
                self.target_fileentry.set_filename(spath)
            else:
                base = self.get_default_basename()
                spath = os.path.normpath("%s/%s%s" % (spath,base,ext))
                self.target_fileentry.set_filename(spath)


    def setup_output_notebook(self):
        """Set up the output notebook of the dialog.  This sole
        purpose of this function is to grab a pointer for later use in
        the callback from when the file format is changed."""

        self.output_notebook = gtk.Notebook()
        self.output_notebook.set_show_tabs(0)
        self.output_notebook.set_show_border(0)
        self.output_notebook.set_border_width(12)
        self.output_notebook.set_current_page(self.notebook_page)
        self.window.vbox.add(self.output_notebook)

    def size_changed(self,obj):
        paper = self.papersize_menu.get_menu().get_active().get_data('i')
        if paper.get_width() <= 0:
            self.pwidth.set_sensitive(1)
            self.pheight.set_sensitive(1)
        else:
            self.pwidth.set_sensitive(0)
            self.pheight.set_sensitive(0)
            self.pwidth.set_text("%.2f" % paper.get_width())
            self.pheight.set_text("%.2f" % paper.get_height())
        

    def setup_paper_frame(self):
        """Set up the paper selection frame of the dialog.  This
        function relies on a paper_xxx() customization functions to
        determine whether the pagecount menu should appear and what
        its strings should be."""

        (pagecount_map, start_text) = self.get_print_pagecount_map()

        if pagecount_map:
            self.paper_table = gtk.Table(3,6)
        else:
            self.paper_table = gtk.Table(4,6)
        self.paper_table.set_col_spacings(12)
        self.paper_table.set_row_spacings(6)
        self.paper_table.set_border_width(0)
        self.output_notebook.append_page(self.paper_table,gtk.Label(_("Paper Options")))
            
        paper_label = gtk.Label("<b>%s</b>" % _("Paper Options"))
        paper_label.set_use_markup(gtk.TRUE)
        paper_label.set_alignment(0.0,0.5)
        self.paper_table.attach(paper_label,0,6,0,1,gtk.SHRINK|gtk.FILL)

        self.papersize_menu = gtk.OptionMenu()
        self.papersize_menu.connect('changed',self.size_changed)
        
        self.orientation_menu = gtk.OptionMenu()
        l = gtk.Label("%s:" % _("Size"))
        l.set_alignment(0.0,0.5)
        
        self.paper_table.attach(l,1,2,1,2,gtk.SHRINK|gtk.FILL)
        self.paper_table.attach(self.papersize_menu,2,3,1,2)
        l = gtk.Label("%s:" % _("Height"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,3,4,1,2,gtk.SHRINK|gtk.FILL)

        self.pheight = gtk.Entry()
        self.pheight.set_sensitive(0)
        self.paper_table.attach(self.pheight,4,5,1,2)
        
        l = gtk.Label(_("cm"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,5,6,1,2,gtk.SHRINK|gtk.FILL)

        l = gtk.Label("%s:" % _("Orientation"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,1,2,2,3,gtk.SHRINK|gtk.FILL)
        self.paper_table.attach(self.orientation_menu,2,3,2,3)
        l = gtk.Label("%s:" % _("Width"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,3,4,2,3,gtk.SHRINK|gtk.FILL)

        self.pwidth = gtk.Entry()
        self.pwidth.set_sensitive(0)
        self.paper_table.attach(self.pwidth,4,5,2,3)

        l = gtk.Label(_("cm"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,5,6,2,3,gtk.SHRINK|gtk.FILL)

        PaperMenu.make_paper_menu(self.papersize_menu,
                                  self.option_store.get('paper',GrampsCfg.paper_preference))
        PaperMenu.make_orientation_menu(self.orientation_menu,
                                        self.option_store.get('orientation',BaseDoc.PAPER_PORTRAIT))

        # The optional pagecount stuff.
        if pagecount_map:
            self.pagecount_menu = gtk.OptionMenu()
            myMenu = Utils.build_string_optmenu(pagecount_map, start_text)
            self.pagecount_menu.set_menu(myMenu)
            l = gtk.Label("%s:" % _("Page Count"))
            l.set_alignment(0.0,0.5)
            self.paper_table.attach(l,1,2,3,4,gtk.SHRINK|gtk.FILL)
            self.paper_table.attach(self.pagecount_menu,2,3,3,4)


    def html_file_enable(self,obj):
        text = unicode(obj.get_text())
        if _template_map.has_key(text):
            if _template_map[text]:
                self.html_fileentry.set_sensitive(0)
            else:
                self.html_fileentry.set_sensitive(1)
        else:
            self.html_fileentry.set_sensitive(0)
            

    def setup_html_frame(self):
        """Set up the html frame of the dialog.  This sole purpose of
        this function is to grab a pointer for later use in the parse
        html frame function."""

        self.html_table = gtk.Table(3,3)
        self.html_table.set_col_spacings(12)
        self.html_table.set_row_spacings(6)
        self.html_table.set_border_width(0)
        html_label = gtk.Label("<b>%s</b>" % _("HTML Options"))
        html_label.set_alignment(0.0,0.5)
        html_label.set_use_markup(gtk.TRUE)
        self.html_table.attach(html_label,0,3,0,1)

        self.output_notebook.append_page(self.html_table,gtk.Label(_("HTML Options")))

        l = gtk.Label("%s:" % _("Template"))
        l.set_alignment(0.0,0.5)
        self.html_table.attach(l,1,2,1,2,gtk.SHRINK|gtk.FILL)

        self.template_combo = gtk.Combo()
        template_list = [ _default_template ]
        tlist = _template_map.keys()
        tlist.sort()
        
        for template in tlist:
            if template != _user_template:
                template_list.append(template)
        template_list.append(_user_template)
        
        self.template_combo.set_popdown_strings(template_list)
        self.template_combo.entry.set_editable(0)

        def_template = self.option_store.get('default_template','')
        if def_template in template_list:
            self.template_combo.entry.set_text(def_template)
        self.template_combo.entry.connect('changed',self.html_file_enable)
        
        self.html_table.attach(self.template_combo,2,3,1,2)
        l = gtk.Label("%s:" % _("User Template"))
        l.set_alignment(0.0,0.5)
        self.html_table.attach(l,1,2,2,3,gtk.SHRINK|gtk.FILL)
        self.html_fileentry = gnome.ui.FileEntry("HTML_Template",_("Choose File"))
        self.html_fileentry.set_sensitive(0)
        user_template = self.option_store.get('user_template','')
        if os.path.isfile(user_template):
            self.html_fileentry.set_filename(user_template)
        self.html_table.attach(self.html_fileentry,2,3,2,3)


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

        if not self.get_target_is_directory() and os.path.isdir(self.target_path):
            ErrorDialog(_("Invalid file name"),
                        _("The filename that you gave is a directory.\n"
                          "You need to provide a valid filename."))
            return None

        if os.path.isfile(self.target_path):
            a = OptionDialog(_('File already exists'),
                             _('You can choose to either overwrite the file, or change '
                               'the selected filename.'),
                             _('_Overwrite'),None,
                             _('_Change filename'),None)
                             
            if a.get_response() == gtk.RESPONSE_YES:
                return
        
        self.set_default_directory(os.path.dirname(self.target_path) + os.sep)
        return 1

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_menu().get_active().get_data("name")

    def parse_paper_frame(self):
        """Parse the paper frame of the dialog.  Save the user
        selected choices for later use.  Note that this routine
        retrieves a value from the pagecount menu, whether or not it
        is displayed on the screen.  The subclass will know which ones
        it has enabled.  This is for simplicity of programming."""
        self.paper = self.papersize_menu.get_menu().get_active().get_data("i")
        self.option_store['paper'] = self.paper.get_name()

        if self.paper.get_height() <= 0 or self.paper.get_width() <= 0:
            try:
                h = float(unicode(self.pheight.get_text()))
                w = float(unicode(self.pwidth.get_text()))
                
                if h <= 1.0 or w <= 1.0:
                    self.paper.set_height(29.7)
                    self.paper.set_width(21.0)
                else:
                    self.paper.set_height(h)
                    self.paper.set_width(w)
            except:
                self.paper.set_height(29.7)
                self.paper.set_width(21.0)
        
        self.orien = self.orientation_menu.get_menu().get_active().get_data("i")
        self.option_store['orientation'] = self.orien

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

        text = unicode(self.template_combo.entry.get_text())
        if _template_map.has_key(text):
            if text == _user_template:
                self.template_name = self.html_fileentry.get_full_path(0)
                self.option_store['default_template'] = text
                self.option_store['user_template'] = ''
            else:
                self.template_name = "%s/%s" % (const.template_dir,_template_map[text])
                self.option_store['default_template'] = text
                self.option_store['user_template'] = self.template_name
        else:
            self.template_name = None


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
        try:
            self.make_report()
        except (IOError,OSError),msg:
            ErrorDialog(str(msg))
            
        # Clean up the dialog object
        self.window.destroy()


class TextReportDialog(ReportDialog):
    """A class of ReportDialog customized for text based reports."""

    def __init__(self,database,person,options={}):
        """Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information."""
        ReportDialog.__init__(self,database,person, options)

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
        if self.print_report.get_active ():
            self.doc.print_requested ()

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

class DrawReportDialog(ReportDialog):
    """A class of ReportDialog customized for drawing based reports."""
    def __init__(self,database,person,opt={}):
        """Initialize a dialog to request that the user select options
        for a basic drawing report.  See the ReportDialog class for
        more information."""
        ReportDialog.__init__(self,database,person,opt)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this drawing report."""
        Plugins.get_draw_doc_menu(self.format_menu,self.doc_type_changed)

    def make_document(self):
        """Create a document of the type requested by the user."""

        self.doc = self.format(self.selected_style,self.paper,
                               self.template_name,self.orien)
        if self.print_report.get_active ():
            self.doc.print_requested ()

class TemplateParser(handler.ContentHandler):
    """
    Interface to the document template file
    """
    def __init__(self,data,fpath):
        """
        Creates a template parser. The parser loads map of tempate names
        to the file containing the tempate.

        data - dictionary that holds the name to path mappings
        fpath - filename of the XML file
        """
        handler.ContentHandler.__init__(self)
        self.data = data
        self.path = fpath
    
    def setDocumentLocator(self,locator):
        """Sets the XML document locator"""
        self.locator = locator

    def startElement(self,tag,attrs):
        """
        Loads the dictionary when an XML tag of 'template' is found. The format
        XML tag is <template title=\"name\" file=\"path\">
        """
        
        if tag == "template":
            self.data[attrs['title']] = attrs['file']

            
        
#-----------------------------------------------------------------------
#
# Initialization
#
#-----------------------------------------------------------------------

try:
    parser = make_parser()
    gspath = const.template_dir
    parser.setContentHandler(TemplateParser(_template_map,gspath))
    parser.parse("file://%s/templates.xml" % gspath)
    parser = make_parser()
    gspath = os.path.expanduser("~/.gramps/templates")
    parser.setContentHandler(TemplateParser(_template_map,gspath))
    parser.parse("file://%s/templates.xml" % gspath)
except (IOError,OSError,SAXParseException):
    pass
