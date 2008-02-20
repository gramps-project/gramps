#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
import const
from _ReportDialog import ReportDialog
from _FileEntry import FileEntry
from _TemplateParser import _template_map, _default_template, _user_template
from _PaperMenu import PaperFrame

#-------------------------------------------------------------------------
#
# ReportDialog class
#
#-------------------------------------------------------------------------
class DocReportDialog(ReportDialog):
    """
    The DocReportDialog base class.  This is a base class for generating
    dialogs for docgen derived reports.
    """

    def __init__(self, dbstate, uistate, option_class, name, trans_name):
        """Initialize a dialog to request that the user select options
        for a basic *stand-alone* report."""
        
        self.style_name = "default"
        self.page_html_added = False
        ReportDialog.__init__(self, dbstate, uistate, option_class,
                                  name, trans_name)

        # Allow for post processing of the format frame, since the
        # show_all task calls events that may reset values

    def init_interface(self):
        ReportDialog.init_interface(self)
        self.doc_type_changed(self.format_menu)

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
        raise NotImplementedError

    def make_document(self):
        """Create a document of the type requested by the user.
        """
        pstyle = self.paper_frame.get_paper_style()
        
        self.doc = self.format(self.selected_style, pstyle, self.template_name)
        
        self.options.set_document(self.doc)

        if self.print_report.get_active():
            self.doc.print_requested()

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
            self.notebook.insert_page(self.paper_frame,self.paper_label,0)
            self.paper_frame.show_all()
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
                
    def setup_report_options_frame(self):
        self.paper_frame = PaperFrame(self.options.handler.get_paper_metric(),
                                      self.options.handler.get_paper_name(),
                                      self.options.handler.get_orientation(),
                                      self.options.handler.get_margins(),
                                      self.options.handler.get_custom_paper_size()
                                      )
        self.setup_html_frame()
        ReportDialog.setup_report_options_frame(self)

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

    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_reference()
        format_name = self.format_menu.get_clname()
        self.options.handler.set_format_name(format_name)
        
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
                self.template_name = "%s%s%s" % (const.TEMPLATE_DIR,os.path.sep,
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
        self.parse_html_frame()

        self.options.handler.set_paper_metric(self.paper_frame.get_paper_metric())
        self.options.handler.set_paper_name(self.paper_frame.get_paper_name())
        self.options.handler.set_orientation(self.paper_frame.get_orientation())
        self.options.handler.set_margins(self.paper_frame.get_paper_margins())
        self.options.handler.set_custom_paper_size(self.paper_frame.get_custom_paper_size())
        
        self.parse_user_options()

        # Create the output document.
        self.make_document()
        
        # Save options
        self.options.handler.save_options()
