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
     CATEGORY_VIEW, CATEGORY_CODE, CATEGORY_WEB, CATEGORY_GRAPHVIZ, \
     standalone_categories
from _BareReportDialog import BareReportDialog
from _FileEntry import FileEntry
from _PaperMenu import PaperComboBox, OrientationComboBox, paper_sizes
from _TemplateParser import _template_map, _default_template, _user_template
from BaseDoc import PaperStyle

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

    def get_title(self):
        """The window title for this dialog"""
        name = self.report_name
        category = standalone_categories[self.category]
        return "%s - %s - GRAMPS" % (name,category)

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        report for the selected person. """
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
    elif category == CATEGORY_GRAPHVIZ:
        from _GraphvizReportDialog import GraphvizReportDialog
        dialog_class = GraphvizReportDialog
    elif category == CATEGORY_WEB:
        from _WebReportDialog import WebReportDialog
        dialog_class = WebReportDialog
    elif category in (CATEGORY_BOOK,CATEGORY_CODE,CATEGORY_VIEW):
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
            dialog.close()
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
                log.error("Failed to run report.", exc_info=True)
            break
        elif (response == gtk.RESPONSE_DELETE_EVENT or
              response == gtk.RESPONSE_CANCEL):
            dialog.close()
            break
