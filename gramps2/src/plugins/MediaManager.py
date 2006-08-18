#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Media Manager tool"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import GrampsDisplay
import Assistant
import Errors
from BasicUtils import UpdateCallback
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# This is an Assistant implementation to guide the user
#
#-------------------------------------------------------------------------
class MediaMan(Tool.Tool):

    def __init__(self, dbstate, uistate, options_class, name, callback=None):

        Tool.Tool.__init__(self, dbstate, options_class, name)
        self.uistate = uistate
        self.callback = uistate.pulse_progressbar

        self.build_batch_ops()
        self.batch_settings = None
        self.settings_page = None

        try:
            self.w = Assistant.Assistant(uistate,self.__class__,self.complete,
                                         _("Media Manager"))
        except Errors.WindowActiveError:
            return

        self.welcome_page = self.w.add_text_page(_('GRAMPS Media Manager'),
                                                 self.get_info_text())
        self.selection_page = self.w.add_page(_('Selecting operation'),
                                              self.build_selection_page())
        self.confirm_page = self.w.add_text_page('','')
        self.conclusion_page = self.w.add_text_page('','')

        self.w.connect('before-page-next',self.on_before_page_next)

        self.w.show()

    def complete(self):
        pass

    def on_before_page_next(self,obj,page,data=None):
        if page == self.selection_page:
            self.build_settings_page()
            self.build_confirmation()
        elif page == self.settings_page:
            self.build_confirmation()
        elif page == self.confirm_page:
            success = self.run()
            self.build_conclusion(success)

    def get_info_text(self):
        return _("This tool allows batch operations on media objects "
                 "stored in GRAMPS, as well as on their files. "
                 "An important distinction must be made between a GRAMPS "
                 "media object and its file.\n\n"
                 "The GRAMPS media object is a collection of data about "
                 "the media object file: its filename and/or path, its "
                 "description, its ID, notes, source references, etc. "
                 "These data <b>do not include the file itself</b>.\n\n"
                 "The files containing image, sound, video, etc, exists "
                 "separately on your hard drive. These files are normally "
                 "not managed by GRAMPS and are not included in the GRAMPS "
                 "database. "
                 "The GRAMPS database only stores the path and file names.\n\n"
                 "This tool allows you to modify both the records within "
                 "your GRAMPS database and the media object files that GRAMPS "
                 "normaly does not manage. Please be careful in selecting "
                 "your options, as you may potentially harm your files.")

    def build_selection_page(self):
        """
        Build a page with the radio buttons for every available batch op.
        """
        self.batch_op_buttons = []

        box = gtk.VBox()
        box.set_spacing(12)

        table = gtk.Table(2*len(self.batch_ops),2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        
        tip = gtk.Tooltips()
        
        group = None
        for ix in range(len(self.batch_ops)):
            title = self.batch_ops[ix][1]
            description= self.batch_ops[ix][2]

            button = gtk.RadioButton(group,title)
            if not group:
                group = button
            self.batch_op_buttons.append(button)
            table.attach(button,0,2,2*ix,2*ix+1,yoptions=0)
            tip.set_tip(button,description)
        
        box.add(table)
        return box

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-other')

    def build_batch_ops(self):
        self.batch_ops = []
        batches_to_use = [
            PathChange,
            ]

        for batch_class in batches_to_use:
            batch = batch_class()
            self.batch_ops.append(batch.get_self())

    def get_selected_op_index(self):
        """
        Query the selection radiobuttons and return the index number 
        of the selected batch op. 
        """
        for ix in range(len(self.batch_op_buttons)):
            button = self.batch_op_buttons[ix]
            if button.get_active():
                return ix
        else:
            return 0
    
    def build_settings_page(self):
        """
        Build an extra page with the settings specific for the chosen batch-op.
        If there's already an entry for this batch-op then do nothing,
        otherwise add a page.

        If the chosen batch-op does not have settings then remove the
        settings page that is already there (from previous user passes 
        through the assistant).
        """
        ix = self.get_selected_op_index()
        if self.batch_ops[ix][3]:
            if ix == self.batch_settings:
                return
            elif self.batch_settings:
                self.w.remove_page(self.settings_page)
                self.batch_settings = None
            title,box = self.batch_ops[ix][3]
            self.settings_page = self.w.insert_page(title,box,
                                                    self.selection_page+1)
            self.confirm_page += 1
            self.conclusion_page += 1
            self.batch_settings = ix
            box.show_all()
        elif self.batch_settings:
            self.w.remove_page(self.settings_page)
            self.batch_settings = None

    def build_confirmation(self):
        """
        Build the text of the confirmation label. This should query
        the selected options (format, filename) and present the summary
        of the proposed action.
        """
        ix = self.get_selected_op_index()
        confirm_text_builder = self.batch_ops[ix][4]
        confirm_text = confirm_text_builder()
        self.w.remove_page(self.confirm_page)
        self.confirm_page = self.w.insert_text_page(_('Final confirmation'),
                                                    confirm_text,
                                                    self.confirm_page)

    def run(self):
        """
        Run selected batch op with selected settings.
        """
        ix = self.get_selected_op_index()
        batch_op = self.batch_ops[ix][0]
        self.pre_run()
        success = batch_op(self.db,self.callback)
        self.post_run()
        return success
        
    def pre_run(self):
        self.uistate.set_busy_cursor(1)
        self.w.set_busy_cursor(1)
        self.uistate.progress.show()

    def post_run(self):
        self.uistate.set_busy_cursor(0)
        self.w.set_busy_cursor(0)
        self.uistate.progress.hide()

    def build_conclusion(self,success):
        if success:
            conclusion_title =  _('Operation succesfully finished.')
            conclusion_text = _(
                'The operation you requested has been '
                'successfully finished. You may press OK button '
                'now to continue.')
        else:
            conclusion_title =  _('Operation failed'),
            conclusion_text = _(
                'There was an error while performing the requested '
                'operation. You may try starting the tool again.')
        self.w.remove_page(self.conclusion_page)
        self.conclusion_page = self.w.insert_text_page(conclusion_title,
                                                       conclusion_text,
                                                       self.conclusion_page)

#------------------------------------------------------------------------
#
# These are the actuall sub-tools (batch-ops) for use from Assistant
#
#------------------------------------------------------------------------
class BatchOp:
    """
    Base class for the sub-tools.
    """
    title = 'Untitled operation'
    description = 'This operation needs to be described'

    def build_config(self):
        """
        This method should return either None (if the batch op requires
        no settings to run) or a tuple (title,box) for the settings page.
        """
        return None

    def build_confirm_text(self):
        """
        This method should return either None (if the batch op requires
        no confirmation) or a string with the confirmation text.
        """
        return "This confirmation text needs to be written"

    def run_tool(self,db,callback):
        self._prepare(db,callback)
        success = self._run(db)
        self._cleanup(db)
        return success

    def _prepare(self,db,callback):
        uc = UpdateCallback(callback)
        uc.set_total(db.get_number_of_media_objects())
        self.update = uc.update
        self.trans = db.transaction_begin("",batch=True)
        db.disable_signals()

    def _cleanup(self,db):
        db.transaction_commit(self.trans,self.title)
        db.enable_signals()
        db.request_rebuild()

    def _run(self,db,callback):
        print "Running BatchOp tool... done."
        return True

    def get_self(self):
        return (self.run_tool,self.title,self.description,
                self.build_config(),self.build_confirm_text)

class PathChange(BatchOp):
    title = _('Change path')
    description = _('This tool allows changing specified path '
                    'into another specified path')

    def build_config(self):
        title = _("Change path settings")

        box = gtk.VBox()
        box.set_spacing(12)

        table = gtk.Table(2,2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        self.from_entry = gtk.Entry()
        table.attach(self.from_entry,1,2,0,1,yoptions=0)
        
        from_label = gtk.Label(_('_Replace:'))
        from_label.set_use_underline(True)
        from_label.set_alignment(0,0.5)
        from_label.set_mnemonic_widget(self.from_entry)
        table.attach(from_label,0,1,0,1,xoptions=0,yoptions=0)

        self.to_entry = gtk.Entry()
        table.attach(self.to_entry,1,2,1,2,yoptions=0)

        to_label = gtk.Label(_('_With:'))
        to_label.set_use_underline(True)
        to_label.set_alignment(0,0.5)
        to_label.set_mnemonic_widget(self.to_entry)
        table.attach(to_label,0,1,1,2,xoptions=0,yoptions=0)

        box.add(table)

        return (title,box)

    def build_confirm_text(self):
        from_text = unicode(self.from_entry.get_text())
        to_text = unicode(self.to_entry.get_text())
        text = _(
            'The following action is to be performed:\n\n'
            'Operation:\t%s\nReplace:\t\t%s\nWith:\t\t%s\n\n'
            'Press OK to proceed, Cancel to abort, or Back to '
            'revisit your options.') % (self.title, from_text, to_text)
        return text
        
    def _run(self,db):
        from_text = unicode(self.from_entry.get_text())
        to_text = unicode(self.to_entry.get_text())
        for handle in db.get_media_object_handles():
            obj = db.get_object_from_handle(handle)
            if obj.get_path().find(from_text) != -1:
                new_path = obj.get_path().replace(from_text,to_text)
                obj.set_path(new_path)
                db.commit_media_object(obj,self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class MediaManOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'mediaman',
    category = Tool.TOOL_UTILS,
    tool_class = MediaMan,
    options_class = MediaManOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Media manager"),
    status=(_("Beta")),
    author_name = "Alex Roitman",
    author_email = "shura@gramps-project.org",
    description=_("Manages batch operations on media files")
    )
