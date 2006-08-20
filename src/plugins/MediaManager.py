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

# Written by Alex Roitman

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
from RelLib import MediaObject
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
        elif page == self.settings_page:
            self.build_confirmation()
        elif page == self.confirm_page:
            success = self.run()
            self.build_conclusion(success)

    def get_info_text(self):
        return _("This tool allows batch operations on media objects "
                 "stored in GRAMPS. "
                 "An important distinction must be made between a GRAMPS "
                 "media object and its file.\n\n"
                 "The GRAMPS media object is a collection of data about "
                 "the media object file: its filename and/or path, its "
                 "description, its ID, notes, source references, etc. "
                 "These data <b>do not include the file itself</b>.\n\n"
                 "The files containing image, sound, video, etc, exist "
                 "separately on your hard drive. These files are "
                 "not managed by GRAMPS and are not included in the GRAMPS "
                 "database. "
                 "The GRAMPS database only stores the path and file names.\n\n"
                 "This tool allows you to only modify the records within "
                 "your GRAMPS database. If you want to move or rename "
                 "the files then you need to do it on your own, outside of "
                 "GRAMPS. Then you can adjust the paths using this tool so "
                 "that the media objects store the correct file locations.")

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
            title = self.batch_ops[ix].title
            description= self.batch_ops[ix].description

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
            Convert2Abs,
            Convert2Rel,
            ]

        for batch_class in batches_to_use:
            self.batch_ops.append(batch_class(self.db,self.callback))

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
        config = self.batch_ops[ix].build_config()
        if config:
            if ix == self.batch_settings:
                return
            elif self.batch_settings:
                self.w.remove_page(self.settings_page)
                self.settings_page = None
                self.confirm_page -= 1
                self.conclusion_page -= 1
                self.batch_settings = None
                self.build_confirmation()
            title,box = config
            self.settings_page = self.w.insert_page(title,box,
                                                    self.selection_page+1)
            self.confirm_page += 1
            self.conclusion_page += 1
            self.batch_settings = ix
            box.show_all()
        else:
            if self.batch_settings != None:
                self.w.remove_page(self.settings_page)
                self.settings_page = None
                self.confirm_page -= 1
                self.conclusion_page -= 1
                self.batch_settings = None
            self.build_confirmation()

    def build_confirmation(self):
        """
        Build the confirmation page.

        This should query the selected settings and present the summary
        of the proposed action, as well as the list of affected paths.
        """

        ix = self.get_selected_op_index()
        confirm_text = self.batch_ops[ix].build_confirm_text()
        path_list = self.batch_ops[ix].build_path_list()

        box = gtk.VBox()
        box.set_spacing(12)
        box.set_border_width(12)

        label1 = gtk.Label(confirm_text)
        label1.set_line_wrap(True)
        label1.set_use_markup(True)
        label1.set_alignment(0,0.5)
        box.pack_start(label1,expand=False)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        tree = gtk.TreeView()
        model = gtk.ListStore(str)
        tree.set_model(model)
        tree_view_column = gtk.TreeViewColumn(_('Affected path'),
                                              gtk.CellRendererText(),text=0)
        tree_view_column.set_sort_column_id(0)
        tree.append_column(tree_view_column)
        for path in path_list:
            model.append(row=[path])
        scrolled_window.add(tree)
        box.pack_start(scrolled_window,expand=True,fill=True)

        label3 = gtk.Label(_('Press OK to proceed, Cancel to abort, '
                             'or Back to revisit your options.'))
        box.pack_start(label3,expand=False)
        box.show_all()

        self.w.remove_page(self.confirm_page)
        self.confirm_page = self.w.insert_page(_('Final confirmation'),
                                               box,self.confirm_page)

    def run(self):
        """
        Run selected batch op with selected settings.
        """
        ix = self.get_selected_op_index()
        self.pre_run()
        success = self.batch_ops[ix].run_tool()
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
                'The operation you requested has finished successfully. '
                'You may press OK button now to continue.')
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
class BatchOp(UpdateCallback):
    """
    Base class for the sub-tools.
    """
    title       = 'Untitled operation'
    description = 'This operation needs to be described'

    def __init__(self,db,callback):
        UpdateCallback.__init__(self,callback)
        self.db = db
        self.prepared = False

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
        text = _(
            'The following action is to be performed:\n\n'
            'Operation:\t%s') % self.title.replace('_','')
        return text

    def build_path_list(self):
        """
        This method returns a list of the path names that would be
        affected by the batch op. Typically it would rely on prepare()
        to do the actual job, but it does not have to be that way.
        """
        self.prepare()
        return self.path_list

    def run_tool(self):
        """
        This method runs the batch op, taking care of database signals
        and transactions before and after the running.
        Should not be overridden without good reasons.
        """
        self._pre_run()
        success = self._run()
        self._post_run()
        return success

    def _pre_run(self):
        """
        Low-level method for starting transaction and disabling signals.
        Should not be overridden without good reasons.
        """
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()

    def _post_run(self):
        """
        Low-level method for committing transaction and enabling signals.
        Should not be overridden without good reasons.
        """
        self.db.transaction_commit(self.trans,self.title)
        self.db.enable_signals()
        self.db.request_rebuild()

    def _run(self):
        """
        This method is the beef of the tool.
        Needs to be overridden in the subclass.
        """
        print "This method needs to be written."
        print "Running BatchOp tool... done."
        return True

    def prepare(self):
        """
        This method should prepare the tool for the actual run.
        Typically this involves going over media objects and
        selecting the ones that will be affected by the batch op.

        This method should set self.prepared to True, to indicate
        that it has already ran.
        """
        self.handle_list = []
        self.path_list = []
        self._prepare()
        self.prepared = True

    def _prepare(self):
        print "This method needs to be written."
        print "Preparing BatchOp tool... done."
        pass

#------------------------------------------------------------------------
# Simple op to replace substrings in the paths
#------------------------------------------------------------------------
class PathChange(BatchOp):
    title       = _('Replace _substrings in the path')
    description = _('This tool allows replacing specified substring in the '
                    'path of media objects with another substring. '
                    'This can be useful when you move your media files '
                    'from one directory to another')

    def build_config(self):
        title = _("Replace substring settings")

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
            'Operation:\t%s\nReplace:\t\t%s\nWith:\t\t%s'
            ) % (self.title.replace('_',''), from_text, to_text)
        return text
        
    def _prepare(self):
        from_text = unicode(self.from_entry.get_text())
        cursor = self.db.get_media_cursor()
        self.set_total(self.db.get_number_of_media_objects())
        item = cursor.first()
        while item:
            (handle,data) = item
            obj = MediaObject()
            obj.unserialize(data)
            if obj.get_path().find(from_text) != -1:
                self.handle_list.append(handle)
                self.path_list.append(obj.path)
            item = cursor.next()
            self.update()
        cursor.close()
        self.reset()
        self.prepared = True

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        from_text = unicode(self.from_entry.get_text())
        to_text = unicode(self.to_entry.get_text())
        for handle in self.handle_list:
            obj = self.db.get_object_from_handle(handle)
            new_path = obj.get_path().replace(from_text,to_text)
            obj.set_path(new_path)
            self.db.commit_media_object(obj,self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#An op to convert relative paths to absolute
#------------------------------------------------------------------------
class Convert2Abs(BatchOp):
    title       = _('Convert paths from relative to _absolute')
    description = _('This tool allows converting relative media paths '
                    'to the absolute ones. An absolute path allows to '
                    'fix the file location while moving the database.')

    def _prepare(self):
        cursor = self.db.get_media_cursor()
        self.set_total(self.db.get_number_of_media_objects())
        item = cursor.first()
        while item:
            (handle,data) = item
            obj = MediaObject()
            obj.unserialize(data)
            if not os.path.isabs(obj.path):
                self.handle_list.append(handle)
                self.path_list.append(obj.path)
            item = cursor.next()
            self.update()
        cursor.close()
        self.reset()

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        for handle in self.handle_list:
            obj = self.db.get_object_from_handle(handle)
            new_path = os.path.abspath(obj.path)
            obj.set_path(new_path)
            self.db.commit_media_object(obj,self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#An op to convert absolute paths to relative
#------------------------------------------------------------------------
class Convert2Rel(BatchOp):
    title       = _('Convert paths from absolute to r_elative')
    description = _('This tool allows converting absolute media paths '
                    'to the relative ones. A relative path allows to '
                    'tie the file location to that of the database.')

    def _prepare(self):
        cursor = self.db.get_media_cursor()
        self.set_total(self.db.get_number_of_media_objects())
        item = cursor.first()
        while item:
            (handle,data) = item
            obj = MediaObject()
            obj.unserialize(data)
            if os.path.isabs(obj.path):
                self.handle_list.append(handle)
                self.path_list.append(obj.path)
            item = cursor.next()
            self.update()
        cursor.close()
        self.reset()

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        db_dir = os.path.normpath(os.path.dirname(self.db.full_name))
        for handle in self.handle_list:
            obj = self.db.get_object_from_handle(handle)
            new_path = get_rel_path(db_dir,obj.path)
            obj.set_path(new_path)
            self.db.commit_media_object(obj,self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#
# Helper functions
#
#------------------------------------------------------------------------
def get_rel_path(db_dir,obj_path):
    obj_dir = os.path.dirname(os.path.normpath(obj_path))
    obj_name = os.path.basename(os.path.normpath(obj_path))
    
    # Get the list of dirnames for each
    db_dir_list = [word for word in db_dir.split(os.path.sep) if word]
    obj_dir_list = [word for word in obj_dir.split(os.path.sep) if word]

    # The worst case scenario: nothing in common:
    # we would need to go ndirs up and then use the full obj path
    ndirs = len(db_dir_list)

    # Compare words in both lists
    for word_ix in range(min(len(db_dir_list),len(obj_dir_list))):
        # A common word reduces the trip by one '../' and one word
        if db_dir_list[word_ix] == obj_dir_list[word_ix]:
            ndirs -= 1
        else:
            break

    up_from_db = '../'*ndirs
    obj_dir_rem = os.path.sep.join(obj_dir_list[len(db_dir_list)-ndirs:])
    return os.path.join(up_from_db,obj_dir_rem,obj_name)

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
