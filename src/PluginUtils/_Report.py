#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
# Copyright (C) 2001-2005  Donald N. Allingham
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
from gettext import gettext as _
from types import ClassType, InstanceType
import logging

log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import _PluginMgr
import BaseDoc
from _StyleEditor import StyleListDisplay
import Config
import _PaperMenu
import Errors
import GenericFilter
import NameDisplay
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

class FileEntry(gtk.HBox):
    def __init__(self,defname,title):
        gtk.HBox.__init__(self)

        self.title = title
        self.dir = False
        self.entry = gtk.Entry()
        self.entry.set_text(defname)
        self.set_filename(defname)
        self.set_spacing(6)
        self.set_homogeneous(False)
        self.button = gtk.Button()
        im = gtk.Image()
        im.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_BUTTON)
        self.button.add(im)
        self.button.connect('clicked',self.select_file)
        self.pack_start(self.entry,True,True)
        self.pack_end(self.button,False,False)

    def select_file(self,obj):
        if self.dir:
            my_action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        else:
            my_action = gtk.FILE_CHOOSER_ACTION_SAVE
        
        f = gtk.FileChooserDialog(self.title,
                                  action=my_action,
                                  buttons=(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN,
                                           gtk.RESPONSE_OK))

        name = os.path.basename(self.entry.get_text())
        if self.dir:
            if os.path.isdir(name):
                f.set_current_name(name)
            elif os.path.isdir(os.path.basename(name)):
                f.set_current_name(os.path.basename(name))
        else:
            f.set_current_name(name)
        f.set_current_folder(self.spath)
        status = f.run()
        if status == gtk.RESPONSE_OK:
            self.set_filename(f.get_filename())
        f.destroy()

    def set_filename(self,path):
        if not path:
            return
        if os.path.dirname(path):
            self.spath = os.path.dirname(path)
            self.defname = os.path.basename(path)

        else:
            self.spath = os.getcwd()
            self.defname = path
        self.entry.set_text(os.path.join(self.spath,self.defname))

    def gtk_entry(self):
        return self.entry

    def get_full_path(self,val):
        return self.entry.get_text()

    def set_directory_entry(self,opt):
        self.dir = opt
        
#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_default_template = _("Default Template")
_user_template = _("User Defined Template")

_template_map = {
    _user_template : ""
    }

# Modes for generating reports
MODE_GUI = 1    # Standalone report using GUI
MODE_BKI = 2    # Book Item interface using GUI
MODE_CLI = 4    # Command line interface (CLI)

# Report categories
CATEGORY_TEXT = 0
CATEGORY_DRAW = 1
CATEGORY_CODE = 2
CATEGORY_WEB  = 3
CATEGORY_VIEW = 4
CATEGORY_BOOK = 5

standalone_categories = {
    CATEGORY_TEXT : _("Text Reports"),
    CATEGORY_DRAW : _("Graphical Reports"),
    CATEGORY_CODE : _("Code Generators"),
    CATEGORY_WEB  : _("Web Page"),
    CATEGORY_VIEW : _("View"),
    CATEGORY_BOOK : _("Books"),
}

book_categories = {
    CATEGORY_TEXT : _("Text"),
    CATEGORY_DRAW : _("Graphics"),
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
# GrampsStyleComboBox
#
#-------------------------------------------------------------------------
class GrampsStyleComboBox(gtk.ComboBox):
    """
    Derived from the ComboBox, this widget provides handling of Report
    Styles.
    """

    def __init__(self,model=None):
        """
        Initializes the combobox, building the display column.
        """
        gtk.ComboBox.__init__(self,model)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        
    def set(self,style_map,default):
        """
        Sets the options for the ComboBox, using the passed style
        map as the data.

        @param style_map: dictionary of style names and the corresponding
            style sheet
        @type style_map: dictionary
        @param default: Default selection in the ComboBox
        @type default: str
        """
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        self.style_map = style_map
        keys = style_map.keys()
        keys.sort()
        index = 0
        start_index = 0
        for key in keys:
            if key == "default":
                self.store.append(row=[_('default')])
            else:
                self.store.append(row=[key])
            if key == default:
                start_index = index
            index += 1
            
        self.set_active(start_index)

    def get_value(self):
        """
        Returns the selected key (style sheet name).

        @returns: Returns the name of the selected style sheet
        @rtype: str
        """
        active = self.get_active()
        if active < 0:
            return None
        key = self.store[active][0]
        if key == _('default'):
            key = "default"
        return (key,self.style_map[key])

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

    def __init__(self, database, person, options_class):
        self.database = database
        self.start_person = person
        self.options_class = options_class

        self.doc = options_class.get_document()

        creator = database.get_researcher().get_name()
        self.doc.creator(creator)

        output = options_class.get_output()
        if output:
            self.standalone = True
            self.doc.open(options_class.get_output())
        else:
            self.standalone = False
        
        self.define_table_styles()
        self.define_graphics_styles()

    def begin_report(self):
        if self.options_class.get_newpage():
            self.doc.page_break()
        
    def write_report(self):
        pass

    def end_report(self):
        if self.standalone:
            self.doc.close()
            
    def define_table_styles(self):
        """
        This method MUST be used for adding table and cell styles.
        """
        pass

    def define_graphics_styles(self):
        """
        This method MUST be used for adding drawing styles.
        """
        pass

    def get_progressbar_data(self):
        """The window title for this dialog, and the header line to
        put at the top of the contents of the dialog box."""
        return ("%s - GRAMPS" % _("Progress Report"), _("Working"))

    def progress_bar_title(self,name,length):
        markup = '<span size="larger" weight="bold">%s</span>'
        self.lbl.set_text(markup % name)
        self.lbl.set_use_markup(True)
        self.pbar.set_fraction(0.0)

        progress_steps = length
        if length > 1:
            progress_steps = progress_steps+1
        progress_steps = progress_steps+1
        self.pbar_max = length
        
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
        self.ptop.set_has_separator(False)
        self.ptop.set_title(title)
        self.ptop.set_border_width(12)
        self.lbl = gtk.Label(header)
        self.lbl.set_use_markup(True)
        self.ptop.vbox.add(self.lbl)
        self.ptop.vbox.set_spacing(10)
        self.ptop.vbox.set_border_width(24)
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
        while gtk.events_pending():
            gtk.main_iteration()

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

    def __init__(self,database,person,option_class,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic *bare* report."""

        self.db = database
        self.person = person
        if type(option_class) == ClassType:
            self.options = option_class(name)
        elif type(option_class) == InstanceType:
            self.options = option_class
        self.report_name = translated_name
        self.init_interface()

    def init_interface(self):
        #self.output_notebook = None
        #self.notebook_page = 1
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

        self.style_name = self.options.handler.get_default_stylesheet_name()
        (self.max_gen,self.page_breaks) = self.options.handler.get_report_generations()
        try:
            self.local_filters = self.options.get_report_filters(self.person)
        except AttributeError:
            self.local_filters = []

        self.window = gtk.Dialog('GRAMPS')
        self.window.set_has_separator(False)
        self.cancel = self.window.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.ok = self.window.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)

        self.ok.connect('clicked',self.on_ok_clicked)
        self.cancel.connect('clicked',self.on_cancel)

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
        self.name = NameDisplay.displayer.display(self.person)
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
                                    ReportDialog.border_pad)
        
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

        self.style_menu = GrampsStyleComboBox()
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
        generations fields and the filter combo box are used in most
        (but not all) dialog boxes."""

        (em_label, extra_map, preset, em_tip) = self.get_report_extra_menu_info()
        (et_label, string, et_tip) = self.get_report_extra_textbox_info()

        row = 0
        max_rows = 0
        if self.max_gen:
            max_rows = max_rows + 2
            #if self.page_breaks:
            #    max_rows = max_rows + 1
        if len(self.local_filters):
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
        label.set_use_markup(True)
        
        table.set_border_width(6)
        self.notebook.append_page(table,label)
        row += 1

        if len(self.local_filters):
            self.filter_combo = GenericFilter.GrampsFilterComboBox()
            label = gtk.Label("%s:" % _("Filter"))
            label.set_alignment(0.0,0.5)
            table.attach(label, 1, 2, row, row+1, gtk.SHRINK|gtk.FILL,
                         gtk.SHRINK|gtk.FILL)
            table.attach(self.filter_combo, 2, 3, row, row+1,
                         gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)

            self.filter_combo.set(self.local_filters)
            self.filter_combo.set_active(self.options.handler.get_filter_number())
            row += 1
            
        # Set up the generations spin and page break checkbox
        if self.max_gen:
            self.generations_spinbox = gtk.SpinButton(digits=0)
            self.generations_spinbox.set_numeric(1)
            adjustment = gtk.Adjustment(self.max_gen,1,999,1,0)
            self.generations_spinbox.set_adjustment(adjustment)
            adjustment.value_changed()
            label = gtk.Label("%s:" % _("Generations"))
            label.set_alignment(0.0,0.5)
            table.attach(label, 1, 2, row, row+1,
                         gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL)
            table.attach(self.generations_spinbox, 2, 3, row, row+1,
                         gtk.EXPAND|gtk.FILL,gtk.SHRINK|gtk.FILL)
            row += 1

            #if self.page_breaks:
            msg = _("Page break between generations")
            self.pagebreak_checkbox = gtk.CheckButton(msg)
            self.pagebreak_checkbox.set_active(self.page_breaks)
            table.attach(self.pagebreak_checkbox,2,3,row,row+1,
                         yoptions=gtk.SHRINK)
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
            table.attach(self.extra_menu_label, 1, 2, row, row+1,
                         gtk.SHRINK|gtk.FILL, gtk.SHRINK)
            table.attach(self.extra_menu, 2, 3, row, row+1,
                         yoptions=gtk.SHRINK)
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

            self.extra_textbox.get_buffer().set_text('\n'.join(string))
            self.extra_textbox.set_editable(1)
            self.add_tooltip(self.extra_textbox,et_tip)
            table.attach(self.extra_textbox_label, 1, 2, row, row+1,
                         gtk.SHRINK|gtk.FILL,gtk.SHRINK)
            table.attach(swin, 2, 3, row, row+1,
                         yoptions=gtk.SHRINK)
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

        if self.generations_spinbox:
            self.max_gen = self.generations_spinbox.get_value_as_int()
        else:
            self.max_gen = 0
            
        if self.pagebreak_checkbox and self.pagebreak_checkbox.get_active():
            self.pg_brk = 1
        else:
            self.pg_brk = 0

        if self.max_gen or self.pg_brk:
            self.options.handler.set_report_generations(self.max_gen,self.pg_brk)

        if self.filter_combo:
            try:
                self.filter = self.filter_combo.get_value()
                active = max(0,self.filter_combo.get_active())
                self.options.handler.set_filter_number(active)
            except:
                print "Error setting filter. Proceeding with 'Everyone'"
                self.filter = GenericFilter.Everyone([])
        else:
            self.filter = None

        if self.extra_menu:
            self.report_menu = self.extra_menu.get_menu().get_active().get_data("d")
        else:
            self.report_menu = None

        if self.extra_textbox:
            b = self.extra_textbox.get_buffer()
            text_val = unicode(b.get_text(b.get_start_iter(),b.get_end_iter(),False))
            self.report_text = text_val.split('\n')
            self.options.handler.set_display_format(self.report_text)
        else:
            self.report_text = []
        
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
        import SelectPerson
        sel_person = SelectPerson.SelectPerson(self.db,_('Select Person'))
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


class ReportDialog(BareReportDialog):
    """
    The ReportDialog base class.  This is a base class for generating
    customized dialogs to solicit options for a report.  It cannot be
    used as is, but it can be easily sub-classed to create a functional
    dialog for a stand-alone report.
    """

    def __init__(self,database,person,option_class,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""
        
        self.style_name = "default"
        self.page_html_added = False
        BareReportDialog.__init__(self,database,person,option_class,
                                  name,translated_name)

        # Allow for post processing of the format frame, since the
        # show_all task calls events that may reset values

    def init_interface(self):
        BareReportDialog.init_interface(self)
        if self.format_menu:
            self.doc_type_changed(self.format_menu)
        self.setup_post_process()

    def setup_post_process(self):
        pass

    def setup_center_person(self):
        pass

    def get_title(self):
        """The window title for this dialog"""
        name = self.report_name
        category = standalone_categories[self.category]
        return "%s - %s - GRAMPS" % (name,category)

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        report for the selected person. """
        return _("%(report_name)s for %(person_name)s") % {
                    'report_name' : self.report_name,
                    'person_name' : name}

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
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
        spath = self.options.handler.get_stylesheet_savefile()
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
        return Config.get_report_dir()

    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        Config.save_report_dir(value)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this report.  This menu will be generated based upon the type
        of document (text, draw, graph, etc. - a subclass), whether or
        not the document requires table support, etc."""
        return None

    def make_document(self):
        """Create a document of the type requested by the user."""

        self.doc = self.format(self.selected_style,self.paper,
                               self.template_name,self.orien)
        self.options.set_document(self.doc)
        if self.print_report.get_active ():
            self.doc.print_requested ()

    def doc_type_changed(self, obj):
        """This routine is called when the user selects a new file
        formats for the report.  It adjust the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those chances are made here."""

        label = obj.get_printable()
        if label:
            self.print_report.set_label (label)
            self.print_report.set_sensitive (True)
        else:
            self.print_report.set_label (_("Print a copy"))
            self.print_report.set_sensitive (False)

        # Is this to be a printed report or an electronic report
        # (i.e. a set of web pages)

        if self.page_html_added:
            self.notebook.remove_page(0)
        if obj.get_paper() == 1:
            self.paper_label = gtk.Label('<b>%s</b>'%_("Paper Options"))
            self.paper_label.set_use_markup(True)
            self.notebook.insert_page(self.paper_table,self.paper_label,0)
            self.paper_table.show_all()
        else:
            self.html_label = gtk.Label('<b>%s</b>' % _("HTML Options"))
            self.html_label.set_use_markup(True)
            self.notebook.insert_page(self.html_table,self.html_label,0)
            self.html_table.show_all()

        if not self.get_target_is_directory():
            fname = self.target_fileentry.get_full_path(0)
            (spath,ext) = os.path.splitext(fname)

            ext_val = obj.get_ext()
            if ext_val:
                fname = spath + ext_val
	    else:
                fname = spath
            self.target_fileentry.set_filename(fname)

        # Does this report format use styles?
        if self.style_button:
            self.style_button.set_sensitive(obj.get_styles())
            self.style_menu.set_sensitive(obj.get_styles())
        self.page_html_added = True

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
        self.tbl.attach(label, 0, 4, self.col, self.col+1, gtk.FILL)
        self.col += 1
        
        hid = self.get_stylesheet_savefile()
        if hid[-4:]==".xml":
            hid = hid[0:-4]
        self.target_fileentry = FileEntry(hid,_("Save As"))

        if self.get_target_is_directory():
            self.target_fileentry.set_directory_entry(1)
            self.doc_label = gtk.Label("%s:" % _("Directory"))
        else:
            self.doc_label = gtk.Label("%s:" % _("Filename"))
        self.doc_label.set_alignment(0.0,0.5)

        self.tbl.attach(self.doc_label, 1, 2, self.col, self.col+1,
                        xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK)
        self.tbl.attach(self.target_fileentry, 2, 4, self.col, self.col+1,
                        xoptions=gtk.EXPAND|gtk.FILL,yoptions=gtk.SHRINK)
        self.col += 1
        
        spath = self.get_default_directory()

        self.target_fileentry.set_filename(spath)
        self.target_fileentry.gtk_entry().set_position(len(spath))

    def setup_format_frame(self):
        """Set up the format frame of the dialog.  This function
        relies on the make_doc_menu() function to do all the hard
        work."""

        self.print_report = gtk.CheckButton (_("Print a copy"))
        self.tbl.attach(self.print_report,2,4,self.col,self.col+1,
                        yoptions=gtk.SHRINK)
        self.col += 1

        self.make_doc_menu(self.options.handler.get_format_name())
        self.format_menu.connect('changed',self.doc_type_changed)
        label = gtk.Label("%s:" % _("Output Format"))
        label.set_alignment(0.0,0.5)
        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.format_menu,2,4,self.col,self.col+1,
                        yoptions=gtk.SHRINK)
        self.col += 1

        ext = self.format_menu.get_ext()
        if ext == None:
            ext = ""
        else:
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
        pass

    def size_changed(self,obj):
        (paper,name) = self.papersize_menu.get_value()
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
            self.paper_table = gtk.Table(2,6)
        else:
            self.paper_table = gtk.Table(3,6)
        self.paper_table.set_col_spacings(12)
        self.paper_table.set_row_spacings(6)
        self.paper_table.set_border_width(6)
            
        self.papersize_menu = _PaperMenu.GrampsPaperComboBox()
        self.papersize_menu.connect('changed',self.size_changed)
        
        self.orientation_menu = _PaperMenu.GrampsOrientationComboBox()
        l = gtk.Label("%s:" % _("Size"))
        l.set_alignment(0.0,0.5)
        
        self.paper_table.attach(l,1,2,0,1,gtk.SHRINK|gtk.FILL)
        self.paper_table.attach(self.papersize_menu,2,3,0,1,
                                yoptions=gtk.SHRINK)
        l = gtk.Label("%s:" % _("Height"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,3,4,0,1,gtk.SHRINK|gtk.FILL)

        self.pheight = gtk.Entry()
        self.pheight.set_sensitive(0)
        self.paper_table.attach(self.pheight,4,5,0,1)
        
        l = gtk.Label(_("cm"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,5,6,0,1,gtk.SHRINK|gtk.FILL)

        l = gtk.Label("%s:" % _("Orientation"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,1,2,1,2,gtk.SHRINK|gtk.FILL)
        self.paper_table.attach(self.orientation_menu,2,3,1,2,
                                yoptions=gtk.SHRINK)
        l = gtk.Label("%s:" % _("Width"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,3,4,1,2,gtk.SHRINK|gtk.FILL)

        self.pwidth = gtk.Entry()
        self.pwidth.set_sensitive(0)
        self.paper_table.attach(self.pwidth,4,5,1,2)

        l = gtk.Label(_("cm"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,5,6,1,2,gtk.SHRINK|gtk.FILL)

        self.papersize_menu.set(_PaperMenu.paper_sizes,
                                self.options.handler.get_paper_name())
        self.orientation_menu.set(self.options.handler.get_orientation())

        # The optional pagecount stuff.
        if pagecount_map:
            self.pagecount_menu = gtk.OptionMenu()
            myMenu = Utils.build_string_optmenu(pagecount_map, start_text)
            self.pagecount_menu.set_menu(myMenu)
            l = gtk.Label("%s:" % _("Page Count"))
            l.set_alignment(0.0,0.5)
            self.paper_table.attach(l,1,2,2,3,gtk.SHRINK|gtk.FILL)
            self.paper_table.attach(self.pagecount_menu,2,3,2,3)

    def html_file_enable(self,obj):
        active = obj.get_active()
        text = unicode(obj.get_model()[active][0])
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

        label = gtk.Label("%s:" % _("Template"))
        label.set_alignment(0.0,0.5)
        self.html_table.attach(label, 1, 2, 1, 2, gtk.SHRINK|gtk.FILL)

        self.template_combo = gtk.combo_box_new_text()
        tlist = _template_map.keys()
        tlist.sort()

        template_name = self.options.handler.get_template_name()

        self.template_combo.append_text(_default_template)
        template_index = 1
        active_index = 0
        for template in tlist:
            if template != _user_template:
                self.template_combo.append_text(template)
                if _template_map[template] == template_name:
                    active_index = template_index
                template_index = template_index + 1
        self.template_combo.append_text(_user_template)

        self.template_combo.connect('changed',self.html_file_enable)
        
        self.html_table.attach(self.template_combo,2,3,1,2)
        label = gtk.Label("%s:" % _("User Template"))
        label.set_alignment(0.0,0.5)
        self.html_table.attach(label, 1, 2, 2, 3, gtk.SHRINK|gtk.FILL)
        self.html_fileentry = FileEntry("HTML_Template",
                                        _("Choose File"))
        if template_name and not active_index:
            active_index = template_index
            user_template = template_name
            self.html_fileentry.set_sensitive(True)
        else:
            user_template = ''
            self.html_fileentry.set_sensitive(False)

        if os.path.isfile(user_template):
            self.html_fileentry.set_filename(user_template)
        self.html_table.attach(self.html_fileentry,2,3,2,3)
        self.template_combo.set_active(active_index)


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
            if os.path.isdir(self.target_path) \
                   and self.get_target_is_directory():

                # check whether the dir has rwx permissions
                if not os.access(self.target_path,os.R_OK|os.W_OK|os.X_OK):
                    ErrorDialog(_('Permission problem'),
                                _("You do not have permission to write "
                                  "under the directory %s\n\n"
                                  "Please select another directory or correct "
                                  "the permissions." % self.target_path) 
                                )
                    return None

            # selected path is an exsting file and we need a file
            if os.path.isfile(self.target_path) \
                   and not self.get_target_is_directory():
                a = OptionDialog(_('File already exists'),
                                 _('You can choose to either overwrite the '
                                   'file, or change the selected filename.'),
                                 _('_Overwrite'),None,
                                 _('_Change filename'),None)
                             
                if a.get_response() == gtk.RESPONSE_YES:
                    return None

        # selected path does not exist yet
        else:
            # we will need to create the file/dir
            # need to make sure we can create in the parent dir
            parent_dir = os.path.dirname(os.path.normpath(self.target_path))
            if not os.access(parent_dir,os.W_OK):
                ErrorDialog(_('Permission problem'),
                            _("You do not have permission to create "
                              "%s\n\n"
                              "Please select another path or correct "
                              "the permissions." % self.target_path) 
                            )
                return None
        
        self.set_default_directory(os.path.dirname(self.target_path) + os.sep)
        self.options.handler.output = self.target_path
        return 1

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_reference()
        format_name = self.format_menu.get_clname()
        self.options.handler.set_format_name(format_name)

    def parse_paper_frame(self):
        """Parse the paper frame of the dialog.  Save the user
        selected choices for later use.  Note that this routine
        retrieves a value from the pagecount menu, whether or not it
        is displayed on the screen.  The subclass will know which ones
        it has enabled.  This is for simplicity of programming."""

        (self.paper,paper_name) = self.papersize_menu.get_value()

        self.options.handler.set_paper_name(paper_name)
        self.options.handler.set_paper(self.paper)

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
        
        self.orien = self.orientation_menu.get_value()
        self.options.handler.set_orientation(self.orien)

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

        model = self.template_combo.get_model()
        text = unicode(model[self.template_combo.get_active()][0])

        if _template_map.has_key(text):
            if text == _user_template:
                self.template_name = self.html_fileentry.get_full_path(0)
            else:
                self.template_name = "%s/%s" % (const.template_dir,_template_map[text])
        else:
            self.template_name = ""
        self.options.handler.set_template_name(self.template_name)

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
        self.parse_paper_frame()
        self.parse_html_frame()
        self.parse_report_options_frame()
        self.parse_other_frames()
        self.parse_user_options()

        # Create the output document.
        self.make_document()
        
        # Save options
        self.options.handler.save_options()

#-----------------------------------------------------------------------
#
# Textual reports
#
#-----------------------------------------------------------------------
class TextReportDialog(ReportDialog):
    """A class of ReportDialog customized for text based reports."""

    def __init__(self,database,person,options,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information."""
        self.category = CATEGORY_TEXT
        ReportDialog.__init__(self,database,person,options,name,translated_name)

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
    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        self.format_menu = GrampsTextFormatComboBox()
        self.format_menu.set(self.doc_uses_tables(),
                             self.doc_type_changed, None, active)

#-----------------------------------------------------------------------
#
# Drawing reports
#
#-----------------------------------------------------------------------
class DrawReportDialog(ReportDialog):
    """A class of ReportDialog customized for drawing based reports."""
    def __init__(self,database,person,opt,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic drawing report.  See the ReportDialog class for
        more information."""
        self.category = CATEGORY_DRAW
        ReportDialog.__init__(self,database,person,opt,name,translated_name)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this drawing report."""
        self.format_menu = GrampsDrawFormatComboBox()
        self.format_menu.set(False,self.doc_type_changed, None, active)


#-----------------------------------------------------------------------
#
# Parser for templates file
#
#-----------------------------------------------------------------------
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
    gspath = const.template_dir
    xmlfile = os.path.join(gspath,"templates.xml")

    if os.path.isfile(xmlfile):
        parser = make_parser()
        parser.setContentHandler(TemplateParser(_template_map,gspath))
        parser.parse(xmlfile)
    
    gspath = os.path.join(const.home_dir,"templates")
    xmlfile = os.path.join(gspath,"templates.xml")
    if os.path.isfile(xmlfile):
        parser = make_parser()
        parser.setContentHandler(TemplateParser(_template_map,gspath))
        parser.parse(xmlfile)
        
except (IOError,OSError,SAXParseException):
    pass

#------------------------------------------------------------------------
#
# Command-line report
#
#------------------------------------------------------------------------
class CommandLineReport:
    """
    Provides a way to generate report from the command line.
    
    """

    def __init__(self,database,name,category,option_class,options_str_dict,
                 noopt=False):
        self.database = database
        self.category = category
        self.option_class = option_class(name)
        self.show = options_str_dict.pop('show',None)
        self.options_str_dict = options_str_dict
        self.init_options(noopt)
        self.parse_option_str()
        self.show_options()

    def init_options(self,noopt):
        self.options_dict = {
            'of'        : self.option_class.handler.module_name,
            'off'       : self.option_class.handler.get_format_name(),
            'style'     : self.option_class.handler.get_default_stylesheet_name(),
            'papers'    : self.option_class.handler.get_paper_name(),
            'papero'    : self.option_class.handler.get_orientation(),
            'template'  : self.option_class.handler.get_template_name(),
            'id'        : ''
            }

        self.options_help = {
            'of'        : ["=filename","Output file name. MANDATORY"],
            'off'       : ["=format","Output file format."],
            'style'     : ["=name","Style name."],
            'papers'    : ["=name","Paper size name."],
            'papero'    : ["=num","Paper orientation number."],
            'template'  : ["=name","Template name (HTML only)."],
            'id'        : ["=ID","Gramps ID of a central person. MANDATORY"],
            'filter'    : ["=num","Filter number."],
            'gen'       : ["=num","Number of generations to follow."],
            'pagebbg'   : ["=0/1","Page break between generations."],
            'dispf'     : ["=str","Display format for the outputbox."],
            }

        if noopt:
            return

        # Add report-specific options
        for key in self.option_class.handler.options_dict.keys():
            if key not in self.options_dict.keys():
                self.options_dict[key] = self.option_class.handler.options_dict[key]

        # Add help for report-specific options
        for key in self.option_class.options_help.keys():
            if key not in self.options_help.keys():
                self.options_help[key] = self.option_class.options_help[key]

    def parse_option_str(self):
        for opt in self.options_str_dict.keys():
            if opt in self.options_dict.keys():
                converter = Utils.get_type_converter(self.options_dict[opt])
                self.options_dict[opt] = converter(self.options_str_dict[opt])
                self.option_class.handler.options_dict[opt] = self.options_dict[opt]
            else:
                print "Ignoring unknown option: %s" % opt

        person_id = self.options_dict['id']
        self.person = self.database.get_person_from_gramps_id(person_id)
        id_list = []
        for person_handle in self.database.get_person_handles():
            person = self.database.get_person_from_handle(person_handle)
            id_list.append("%s\t%s" % (
                person.get_gramps_id(),
                NameDisplay.displayer.display(person)))
        self.options_help['id'].append(id_list)
        self.options_help['id'].append(False)

        if self.options_dict.has_key('filter'):
            filter_num = self.options_dict['filter']
            self.filters = self.option_class.get_report_filters(self.person)
            self.option_class.handler.set_filter_number(filter_num)
            
            filt_list = [ filt.get_name() for filt in self.filters ]
            cust_filt_list = [ filt2.get_name() for filt2 in 
                                GenericFilter.CustomFilters.get_filters() ]
            filt_list.extend(cust_filt_list)
            self.options_help['filter'].append(filt_list)
            self.options_help['filter'].append(True)

        if self.options_dict.has_key('gen'):
            max_gen = self.options_dict['gen']
            page_breaks = self.options_dict['pagebbg']
            self.option_class.handler.set_report_generations(max_gen,page_breaks)
            
            self.options_help['gen'].append("Whatever Number You Wish")
            self.options_help['pagebbg'].append([
                "No page break","Page break"])
            self.options_help['pagebbg'].append(True)

        if self.options_dict.has_key('dispf'):
            dispf = ''.join(self.options_dict['dispf']).replace('\\n','\n')
            self.option_class.handler.set_display_format(dispf)

            self.options_help['dispf'].append(
                        "Any string -- may use keyword substitutions")

        self.option_class.handler.output = self.options_dict['of']
        self.options_help['of'].append(os.path.join(const.user_home,"whatever_name"))
                
        if self.category == CATEGORY_TEXT:
            for item in _PluginMgr.textdoc_list:
                if item[7] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[7] for item in _PluginMgr.textdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_DRAW:
            for item in _PluginMgr.drawdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[6] for item in _PluginMgr.drawdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_BOOK:
            for item in _PluginMgr.bookdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[6] for item in _PluginMgr.bookdoc_list ]
            )
            self.options_help['off'].append(False)
        else:
            self.format = None

        for paper in _PaperMenu.paper_sizes:
            if paper.get_name() == self.options_dict['papers']:
                self.paper = paper
        self.option_class.handler.set_paper(self.paper)
        self.options_help['papers'].append(
            [ paper.get_name() for paper in _PaperMenu.paper_sizes 
                        if paper.get_name() != 'Custom Size' ] )
        self.options_help['papers'].append(False)

        self.orien = self.options_dict['papero']
        self.options_help['papero'].append([
            "%d\tPortrait" % BaseDoc.PAPER_PORTRAIT,
            "%d\tLandscape" % BaseDoc.PAPER_LANDSCAPE ] )
        self.options_help['papero'].append(False)

        self.template_name = self.options_dict['template']
        self.options_help['template'].append(os.path.join(const.user_home,"whatever_name"))

        if self.category in (CATEGORY_TEXT,CATEGORY_DRAW):
            default_style = BaseDoc.StyleSheet()
            self.option_class.make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = self.option_class.handler.get_stylesheet_savefile()
            self.style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name = self.option_class.handler.get_default_stylesheet_name()
            self.selected_style = self.style_list.get_style_sheet(style_name)
            
            self.options_help['style'].append(
                self.style_list.get_style_names() )
            self.options_help['style'].append(False)

    def show_options(self):
        if not self.show:
            return
        elif self.show == 'all':
            print "   Available options:"
            for key in self.options_dict.keys():
                print "      %s" % key
            print "   Use 'show=option' to see description and acceptable values"
        elif self.show in self.options_dict.keys():
            print '   %s%s\t%s' % (self.show,
                                    self.options_help[self.show][0],
                                    self.options_help[self.show][1])
            print "   Available values are:"
            vals = self.options_help[self.show][2]
            if type(vals) in [list,tuple]:
                if self.options_help[self.show][3]:
                    for num in range(len(vals)):
                        print "      %d\t%s" % (num,vals[num])
                else:
                    for val in vals:
                        print "      %s" % val
            else:
                print "      %s" % self.options_help[self.show][2]

        else:
            self.show = None

#------------------------------------------------------------------------
#
# Generic task functions for reports
#
#------------------------------------------------------------------------
# Standalone GUI report generic task
def report(database,person,report_class,options_class,translated_name,name,category):
    """
    report - task starts the report. The plugin system requires that the
    task be in the format of task that takes a database and a person as
    its arguments.
    """

    if category == CATEGORY_TEXT:
        dialog_class = TextReportDialog
    elif category == CATEGORY_DRAW:
        dialog_class = DrawReportDialog
    elif category in (CATEGORY_BOOK,CATEGORY_VIEW,
                        CATEGORY_CODE,CATEGORY_WEB):
        report_class(database,person)
        return
    else:
        dialog_class = ReportDialog

    dialog = dialog_class(database,person,options_class,name,translated_name)
    response = dialog.window.run()
    if response == gtk.RESPONSE_OK:
        try:
            MyReport = report_class(dialog.db,dialog.person,dialog.options)
            MyReport.doc.init()
            MyReport.begin_report()
            MyReport.write_report()
            MyReport.end_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.DatabaseError,msg:
            ErrorDialog(_("Report could not be created"),str(msg))
        except:
            log.error("Failed to run report.", exc_info=True)
    dialog.window.destroy()

# Book item generic task
def write_book_item(database,person,report_class,options_class):
    """Write the Timeline Graph using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options_class.handler.get_person_id():
            person = database.get_person_from_gramps_id(options_class.handler.get_person_id())
        return report_class(database,person,options_class)
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        log.error("Failed to write book item.", exc_info=True)
    return None

# Command-line generic task
def cl_report(database,name,category,report_class,options_class,options_str_dict):
    
    clr = CommandLineReport(database,name,category,options_class,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    # write report
    try:
        clr.option_class.handler.doc = clr.format(
                    clr.selected_style,clr.paper,clr.template_name,clr.orien)
        MyReport = report_class(database, clr.person, clr.option_class)
        MyReport.doc.init()
        MyReport.begin_report()
        MyReport.write_report()
        MyReport.end_report()
    except:
        log.error("Failed to write report.", exc_info=True)

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
class GrampsTextFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = Config.get_output_preference()
        index = 0
        _PluginMgr.textdoc_list.sort()
        active_index = 0
        for item in _PluginMgr.textdoc_list:
            if tables and item[2] == 0:
                continue
            name = item[0]
            self.store.append(row=[name])
            #if callback:
            #    menuitem.connect("activate",callback)
            if item[7] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return _PluginMgr.textdoc_list[self.get_active()][0]

    def get_reference(self):
        return _PluginMgr.textdoc_list[self.get_active()][1]

    def get_paper(self):
        return _PluginMgr.textdoc_list[self.get_active()][3]

    def get_styles(self):
        return _PluginMgr.textdoc_list[self.get_active()][4]

    def get_ext(self):
        return _PluginMgr.textdoc_list[self.get_active()][5]

    def get_printable(self):
        return _PluginMgr.textdoc_list[self.get_active()][6]

    def get_clname(self):
        return _PluginMgr.textdoc_list[self.get_active()][7]

class GrampsDrawFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = Config.get_output_preference()
        index = 0
        _PluginMgr.drawdoc_list.sort()
        active_index = 0
        for item in _PluginMgr.drawdoc_list:
            if tables and item[2] == 0:
                continue
            name = item[0]
            self.store.append(row=[name])
            #if callback:
            #    menuitem.connect("activate",callback)
            if item[6] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_reference(self):
        return _PluginMgr.drawdoc_list[self.get_active()][1]

    def get_label(self):
        return _PluginMgr.drawdoc_list[self.get_active()][0]

    def get_paper(self):
        return _PluginMgr.drawdoc_list[self.get_active()][2]

    def get_styles(self):
        return _PluginMgr.drawdoc_list[self.get_active()][3]

    def get_ext(self):
        return _PluginMgr.drawdoc_list[self.get_active()][4]

    def get_printable(self):
        return _PluginMgr.drawdoc_list[self.get_active()][5]

    def get_clname(self):
        return _PluginMgr.drawdoc_list[self.get_active()][6]

class GrampsBookFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = Config.get_output_preference()
        index = 0
        _PluginMgr.drawdoc_list.sort()
        active_index = 0
        self.data = []
        for item in _PluginMgr.bookdoc_list:
            if tables and item[2] == 0:
                continue
            self.data.append(item)
            name = item[0]
            self.store.append(row=[name])
            if item[7] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index += 1
        self.set_active(active_index)

    def get_reference(self):
        return self.data[self.get_active()][1]

    def get_label(self):
        return self.data[self.get_active()][0]

    def get_paper(self):
        return self.data[self.get_active()][3]

    def get_ext(self):
        return self.data[self.get_active()][5]

    def get_printable(self):
        return self.data[self.get_active()][6]

    def get_clname(self):
        return self.data[self.get_active()][7]

