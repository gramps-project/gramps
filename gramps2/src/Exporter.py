#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".Exporter")

#-------------------------------------------------------------------------
#
# Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from PluginUtils import export_list
import QuestionDialog
import Config
import GrampsDisplay
import Assistant
import Errors
from GrampsDb import gramps_db_writer_factory
#-------------------------------------------------------------------------
#
# Exporter
#
#-------------------------------------------------------------------------
class Exporter:
    """
    This class creates Gnome Druid to guide the user through the various
    Save as/Export options. The overall goal is to keep things simple by
    presenting few choice options on each druid page.
    
    The export formats and options are obtained from the plugins, with the
    exception of a native save. Native save as just copies file to another 
    name. 
    """

    def __init__(self,dbstate,uistate):
        """
        Set up the window, the druid, and build all the druid's pages. 
        Some page elements are left empty, since their contents depends
        on the user choices and on the success of the attempted save. 
        """
        self.dbstate = dbstate
        self.uistate = uistate
        self.callback = self.uistate.pulse_progressbar
        if self.dbstate.active:
            self.person = self.dbstate.get_active_person()
        else:
            self.person = self.dbstate.db.find_initial_person()

        self.build_exports()
        self.format_option = None

        try:
            self.w = Assistant.Assistant(uistate,self.complete,
                                         _("Export Assistant"))
        except Errors.WindowActiveError:
            return

        self.w.add_text_page(_('Saving your data'),self.get_intro_text())
        
        self.format_page = self.w.add_page(_('Choosing the format to save'),
                                           self.build_format_page())

        self.file_sel_page = self.w.add_page(_('Selecting the file name'),
                                             self.build_file_sel_page())

        self.confirm_page = self.w.add_text_page('','')
        self.conclusion_page = self.w.add_text_page('','')

        self.w.connect('before-page-next',self.on_before_page_next)

        self.w.show()

    def complete(self):
        pass

    def on_before_page_next(self,obj,page,data=None):
        if page == self.format_page:
            self.build_options()
            self.suggest_filename()
        elif page == self.file_sel_page:
            self.build_confirmation()
        elif page == self.confirm_page:
            success = self.save()
            self.build_conclusion(success)

    def help(self,obj):
        """
        Help handler.
        """
        GrampsDisplay.help('export-data')

    def get_intro_text(self):
        return _('Under normal circumstances, GRAMPS does not require you '
                 'to directly save your changes. All changes you make are '
                 'immediately saved to the database.\n\n'
                 'This process will help you save a copy of your data '
                 'in any of the several formats supported by GRAMPS. '
                 'This can be used to make a copy of your data, backup '
                 'your data, or convert it to a format that will allow '
                 'you to transfer it to a different program.\n\n'
                 'If you change your mind during this process, you '
                 'can safely press the Cancel button at any time and your '
                 'present database will still be intact.')

    def build_confirmation(self):
        """
        Build the text of the confirmation label. This should query
        the selected options (format, filename) and present the summary
        of the proposed action.
        """
        filename = self.chooser.get_filename()
        name = os.path.split(filename)[1]
        folder = os.path.split(filename)[0]
        ix = self.get_selected_format_index()
        format = self.exports[ix][1].replace('_','')

        confirm_text = _(
                'The data will be saved as follows:\n\n'
                'Format:\t%s\nName:\t%s\nFolder:\t%s\n\n'
                'Press OK to proceed, Cancel to abort, or Back to '
                'revisit your options.') % (format, name, folder)
        self.w.remove_page(self.confirm_page)
        self.confirm_page = self.w.insert_text_page(_('Final confirmation'),
                                                    confirm_text,
                                                    self.confirm_page)

    def save(self):
        """
        Perform the actual Save As/Export operation. 
        Depending on the success status, set the text for the final page.
        """
        filename = self.chooser.get_filename()
        Config.set(Config.RECENT_EXPORT_DIR,os.path.split(filename)[0])
        ix = self.get_selected_format_index()
        self.pre_save()
        if self.exports[ix][3]:
            success = self.exports[ix][0](self.dbstate.db,
                                          filename,self.person,
                                          self.option_box_instance,
                                          self.callback)
        else:
            success = self.exports[ix][0](self.dbstate.db,
                                          filename,self.person,
                                          self.callback)
        self.post_save()
        return success

    def pre_save(self):
        self.uistate.set_busy_cursor(1)
        self.w.set_busy_cursor(1)
        self.uistate.progress.show()

    def post_save(self):
        self.uistate.set_busy_cursor(0)
        self.w.set_busy_cursor(0)
        self.uistate.progress.hide()

    def build_conclusion(self,success):
        if success:
            conclusion_title =  _('Your data has been saved')
            conclusion_text = _(
                'The copy of your data has been '
                'successfully saved. You may press OK button '
                'now to continue.\n\n'
                'Note: the database currently opened in your GRAMPS '
                'window is NOT the file you have just saved. '
                'Future editing of the currently opened database will '
                'not alter the copy you have just made. ')
        else:
            conclusion_title =  _('Saving failed'),
            conclusion_text = _(
                'There was an error while saving your data. '
                'You may try starting the export again.\n\n'
                'Note: your currently opened database is safe. '
                'It was only '
                'a copy of your data that failed to save.')
        self.w.remove_page(self.conclusion_page)
        self.conclusion_page = self.w.insert_text_page(conclusion_title,
                                                       conclusion_text,
                                                       self.conclusion_page)

    def build_format_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        self.format_buttons = []

        box = gtk.VBox()
        box.set_spacing(12)

        table = gtk.Table(2*len(self.exports),2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        
        tip = gtk.Tooltips()
        
        group = None
        for ix in range(len(self.exports)):
            title = self.exports[ix][1]
            description= self.exports[ix][2]

            button = gtk.RadioButton(group,title)
            if not group:
                group = button
            self.format_buttons.append(button)
            table.attach(button,0,2,2*ix,2*ix+1)
            tip.set_tip(button,description)
        
        box.add(table)
        return box

    def build_options(self):
        """
        Build an extra page with the options specific for the chosen format.
        If there's already an entry for this format in self.extra_pages then
        do nothing, otherwise add a page.

        If the chosen format does not have options then remove all
        extra pages that are already there (from previous user passes 
        through the assistant).
        """
        ix = self.get_selected_format_index()
        if self.exports[ix][3]:
            if ix == self.format_option:
                return
            elif self.format_option:
                self.w.remove_page(self.option_page)
                self.format_option = None
            title = self.exports[ix][3][0]
            option_box_class = self.exports[ix][3][1]
            self.option_box_instance = option_box_class(self.person)
            box = self.option_box_instance.get_option_box()
            self.option_page = self.w.insert_page(title,box,
                                                   self.format_page+1)
            self.file_sel_page += 1
            self.confirm_page += 1
            self.conclusion_page += 1
            self.format_option = ix
            box.show_all()
        elif self.format_option:
            self.w.remove_page(self.option_page)
            self.format_option = None

    def build_file_sel_page(self):
        """
        Build a druid page embedding the FileChooserWidget.
        """

        self.chooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.chooser.set_local_only(False)
        box = gtk.VBox()
        box.set_spacing(12)
        box.add(self.chooser)

        # Dirty hack to enable proper EXPAND/FILL properties of the chooser
        box.set_child_packing(self.chooser,1,1,0,gtk.PACK_START)

        return box

    def suggest_filename(self):
        """
        Prepare suggested filename and set it in the file chooser. 
        """
        ix = self.get_selected_format_index()
        ext = self.exports[ix][4]
        
        # Suggested folder: try last export, then last import, then home.
        default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = const.user_home

        if ext == 'gramps':
            new_filename = os.path.join(default_dir,'data.gramps')
        elif ext == 'burn':
            new_filename = os.path.basename(self.dbstate.db.get_save_path())
        else:
            new_filename = Utils.get_new_filename(ext,default_dir)
        self.chooser.set_current_folder(default_dir)
        self.chooser.set_current_name(os.path.split(new_filename)[1])

    def get_selected_format_index(self):
        """
        Query the format radiobuttons and return the index number 
        of the selected one. 
        """
        for ix in range(len(self.format_buttons)):
            button = self.format_buttons[ix]
            if button.get_active():
                return ix
        else:
            return 0
    
    def native_export(self,database,filename,person,callback=None):
        """
        Native database export.
        
        In the future, filter and other options may be added.
        """
        try:
            gramps_db_writer_factory(const.app_gramps)(database,
                                                       filename,
                                                       person,
                                                       callback)
            return 1
        except IOError, msg:
            QuestionDialog.ErrorDialog(
                _("Could not write file: %s") % filename,
                _('System message was: %s') % msg )
            return 0

    def build_exports(self):
        """
        This method builds its own list of available exports. 
        The list is built from the PluginMgr.export_list list 
        and from the locally defined exports (i.e. native export defined here).
        """
        native_title = _('GRAMPS _GRDB database')
        native_description =_('The GRAMPS GRDB database is a format '
                'that GRAMPS uses to store information. '
                'Selecting this option will allow you to '
                'make a copy of the current database.') 
        native_config = None
        native_ext = 'grdb'
        native_export = self.native_export

        self.exports = [(native_export,
                         native_title,
                         native_description,
                         native_config,
                         native_ext)]
        self.exports = self.exports + [item for item in export_list]
