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
import os
from gettext import gettext as _

import logging

log = logging.getLogger(".")

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
import Utils
import const

from QuestionDialog import ErrorDialog, OptionDialog, RunDatabaseRepair

from _Constants import CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, \
     CATEGORY_VIEW, CATEGORY_CODE, CATEGORY_WEB, standalone_categories
from _BareReportDialog import BareReportDialog
from _FileEntry import FileEntry
from _PaperMenu import PaperComboBox, OrientationComboBox, paper_sizes
from _TemplateParser import _template_map, _default_template, _user_template

#-------------------------------------------------------------------------
#
# ReportDialog class
#
#-------------------------------------------------------------------------
class ReportDialog(BareReportDialog):
    """
    The ReportDialog base class.  This is a base class for generating
    customized dialogs to solicit options for a report.  It cannot be
    used as is, but it can be easily sub-classed to create a functional
    dialog for a stand-alone report.
    """

    def __init__(self,dbstate,uistate,person,option_class,name,trans_name):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""
        
        self.style_name = "default"
        self.page_html_added = False
        BareReportDialog.__init__(self,dbstate,uistate,person,option_class,
                                  name,trans_name)

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
        if name.strip():
            return _("%(report_name)s for %(person_name)s") % {
                'report_name' : self.report_name,
                'person_name' : name}
        else:
            # No need to translate report_name, it is already translated
            return self.report_name

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
        return Config.get(Config.REPORT_DIRECTORY)

    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        Config.set(Config.REPORT_DIRECTORY,value)

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

        if name == "Custom Size":
            self.pwidth.set_sensitive(1)
            self.pheight.set_sensitive(1)
        else:
            self.pwidth.set_sensitive(0)
            self.pheight.set_sensitive(0)

        if paper.get_width() > 0 and paper.get_height() > 0:
            if self.metric.get_active():
                self.pwidth.set_text("%.2f" % paper.get_width())
                self.pheight.set_text("%.2f" % paper.get_height())
            else:
                self.pwidth.set_text("%.2f" % paper.get_width_inches())
                self.pheight.set_text("%.2f" % paper.get_height_inches())
            
    def units_changed(self,obj):
        (paper,name) = self.papersize_menu.get_value()

        if self.metric.get_active():
            self.lunits1.set_text("cm")
            self.lunits2.set_text("cm")
            self.pwidth.set_text("%.2f" % paper.get_width())
            self.pheight.set_text("%.2f" % paper.get_height())
        else:
            self.lunits1.set_text("in.")
            self.lunits2.set_text("in.")
            self.pwidth.set_text("%.2f" % paper.get_width_inches())
            self.pheight.set_text("%.2f" % paper.get_height_inches())

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
        self.paper_table.set_border_width(6)
            
        self.papersize_menu = PaperComboBox()
        self.papersize_menu.connect('changed',self.size_changed)
        
        self.orientation_menu = OrientationComboBox()
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
        
        self.lunits1 = gtk.Label(_("cm"))
        self.lunits1.set_alignment(0.0,0.5)
        self.paper_table.attach(self.lunits1,5,6,0,1,gtk.SHRINK|gtk.FILL)
        
        self.metric = gtk.CheckButton (_("Metric"))
        self.paper_table.attach(self.metric,2,3,1,2,gtk.SHRINK|gtk.FILL)
        self.metric.connect('toggled',self.units_changed)

        l = gtk.Label("%s:" % _("Orientation"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,1,2,2,3,gtk.SHRINK|gtk.FILL)
        self.paper_table.attach(self.orientation_menu,2,3,2,3,
                                yoptions=gtk.SHRINK)
        l = gtk.Label("%s:" % _("Width"))
        l.set_alignment(0.0,0.5)
        self.paper_table.attach(l,3,4,1,2,gtk.SHRINK|gtk.FILL)

        self.pwidth = gtk.Entry()
        self.pwidth.set_sensitive(0)
        self.paper_table.attach(self.pwidth,4,5,1,2)

        self.lunits2 = gtk.Label(_("cm"))
        self.lunits2.set_alignment(0.0,0.5)
        self.paper_table.attach(self.lunits2,5,6,1,2,gtk.SHRINK|gtk.FILL)

        self.papersize_menu.set(paper_sizes,
                                self.options.handler.get_paper_name())
        self.orientation_menu.set(self.options.handler.get_orientation())
        self.metric.set_active(1)

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
        self.html_table.attach(label, 1, 2, 1, 2, gtk.SHRINK|gtk.FILL,
                               yoptions=gtk.SHRINK)

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
                if _template_map[template] == os.path.basename(template_name):
                    active_index = template_index
                template_index = template_index + 1
        self.template_combo.append_text(_user_template)

        self.template_combo.connect('changed',self.html_file_enable)
        
        self.html_table.attach(self.template_combo,2,3,1,2, yoptions=gtk.SHRINK)
        label = gtk.Label("%s:" % _("User Template"))
        label.set_alignment(0.0,0.5)
        self.html_table.attach(label, 1, 2, 2, 3, gtk.SHRINK|gtk.FILL,
                               yoptions=gtk.SHRINK)
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
        self.html_table.attach(self.html_fileentry,2,3,2,3, yoptions=gtk.SHRINK)
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
        
        if self.metric.get_active():
            multiplier = 1
        else:
            multiplier = 1 / 0.3937008

        if self.paper.get_height() <= 0 or self.paper.get_width() <= 0:
            try:
                h = float(unicode(self.pheight.get_text()))
                w = float(unicode(self.pwidth.get_text()))
                
                if h <= 1.0 or w <= 1.0:
                    self.paper.set_height(29.7 * multiplier)
                    self.paper.set_width(21.0 * multiplier)
                else:
                    self.paper.set_height(h * multiplier)
                    self.paper.set_width(w * multiplier)
            except:
                self.paper.set_height(29.7 * multiplier)
                self.paper.set_width(21.0 * multiplier)
        
        self.orien = self.orientation_menu.get_value()
        self.options.handler.set_orientation(self.orien)

        if self.pagecount_menu == None:
            self.pagecount = 0
        else:
            self.pagecount = \
                     self.pagecount_menu.get_menu().get_active().get_data("d")

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
                self.template_name = "%s%s%s" % (const.template_dir,os.path.sep,
                                                _template_map[text])
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

#------------------------------------------------------------------------
#
# Generic task function a standalone GUI report
#
#------------------------------------------------------------------------
def report(dbstate,uistate,person,report_class,options_class,
           trans_name,name,category, require_active):
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
    elif category in (CATEGORY_BOOK,CATEGORY_CODE,CATEGORY_VIEW,CATEGORY_WEB):
        try:
            report_class(dbstate,uistate,person)
        except Errors.WindowActiveError:
            pass
        return        
    else:
        dialog_class = ReportDialog

    dialog = dialog_class(dbstate,uistate,person,options_class,name,trans_name)

    while True:
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
            except IOError, msg:
                ErrorDialog(_("Report could not be created"),str(msg))
            except Errors.ReportError, msg:
                (m1,m2) = msg.messages()
                ErrorDialog(m1,m2)
            except Errors.DatabaseError,msg:
                ErrorDialog(_("Report could not be created"),str(msg))
            except AttributeError,msg:
                if str(msg).startswith("None"):
                    # "None object type has no attribute . . . " usually means
                    # database corruption
                    RunDatabaseRepair(str(msg))
                else:
                    raise
            except:
                log.error("Failed to run report.", exc_info=True)
            break
        elif response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            break
    dialog.close()
