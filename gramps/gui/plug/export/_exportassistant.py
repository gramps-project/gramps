#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
# Copyright (C) 2008      Brian G. Matherly
# Contribution  2009 by   Brad Crittenden <brad [AT] bradcrittenden.net>
# Copyright (C) 2008      Benny Malengier
# Copyright (C) 2010      Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Written by B.Malengier

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import sys

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".ExportAssistant")

#-------------------------------------------------------------------------
#
# Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

from gramps.gen.const import ICON, SPLASH, GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.config import config
from ...pluginmanager import GuiPluginManager
from gramps.gen.utils.file import (find_folder, get_new_filename)
from ...managedwindow import ManagedWindow
from ...dialog import ErrorDialog
from ...user import User

#-------------------------------------------------------------------------
#
# ExportAssistant
#
#-------------------------------------------------------------------------

_ExportAssistant_pages = {
            'intro'                  : 0,
            'exporttypes'            : 1,
            'options'                : 2,
            'fileselect'             : 3,
            'confirm'                : 4,
            'summary'                : 5,
            }

class ExportAssistant(ManagedWindow, Gtk.Assistant):
    """
    This class creates a GTK assistant to guide the user through the various
    Save as/Export options.

    The overall goal is to keep things simple by presenting few choice options
    on each assistant page.

    The export formats and options are obtained from the plugins.

    """

    #override predefined do_xxx signal handlers
    __gsignals__ = {"apply": "override", "cancel": "override",
                    "close": "override", "prepare": "override"}

    def __init__(self,dbstate,uistate):
        """
        Set up the assistant, and build all the possible assistant pages.

        Some page elements are left empty, since their contents depends
        on the user choices and on the success of the attempted save.

        """
        self.dbstate = dbstate
        self.uistate = uistate

        self.writestarted = False
        self.confirm = None

        # set export mode and busy mode to avoid all other operations
        self.uistate.set_export_mode(True)

        #set up Assistant
        Gtk.Assistant.__init__(self)

        #set up ManagedWindow
        self.top_title = _("Export Assistant")
        ManagedWindow.__init__(self, uistate, [], self.__class__, modal=True)

        #set_window is present in both parent classes
        self.set_window(self, None, self.top_title, isWindow=True)
        self.setup_configs('interface.exportassistant', 760, 500)

        #set up callback method for the export plugins
        self.callback = self.pulse_progressbar

        person_handle = self.uistate.get_active('Person')
        if person_handle:
            self.person = self.dbstate.db.get_person_from_handle(person_handle)
            if not self.person:
                self.person = self.dbstate.db.find_initial_person()
        else:
            self.person = None

        pmgr = GuiPluginManager.get_instance()
        self.__exporters = pmgr.get_export_plugins()
        self.map_exporters = {}

        self.__previous_page = -1

        #create the assistant pages
        self.create_page_intro()
        self.create_page_exporttypes()
        self.create_page_options()
        self.create_page_fileselect()
        self.create_page_confirm()
        #no progress page, looks ugly, and user needs to hit forward at end!
        self.create_page_summary()

        self.option_box_instance = None
        #we need our own forward function as options page must not always be shown
        self.set_forward_page_func(self.forward_func, None)

        #ManagedWindow show method
        self.show()

    def build_menu_names(self, obj):
        """Override ManagedWindow method."""
        return (self.top_title, self.top_title)

    def create_page_intro(self):
        """Create the introduction page."""
        label = Gtk.Label(label=self.get_intro_text())
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_max_width_chars(60)

        image = Gtk.Image()
        image.set_from_file(SPLASH)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(image, False, False, 5)
        box.pack_start(label, False, False, 5)

        page = box
        page.show_all()

        self.append_page(page)
        self.set_page_title(page, _('Saving your data'))
        self.set_page_complete(page, True)
        self.set_page_type(page, Gtk.AssistantPageType.INTRO)

    def create_page_exporttypes(self):
        """Create the export type page.

            A Title label.
            A grid of format radio buttons and their descriptions.

        """
        self.format_buttons = []

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(12)
        box.set_spacing(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        button = None
        recent_type = config.get('behavior.recent-export-type')

        exporters = [(x.get_name().replace("_", ""), x) for x in self.__exporters]
        exporters.sort()
        ix = 0
        for sort_title, exporter in exporters:
            title = exporter.get_name()
            description= exporter.get_description()
            self.map_exporters[ix] = exporter
            button = Gtk.RadioButton.new_with_mnemonic_from_widget(button, title)
            button.set_tooltip_text(description)
            self.format_buttons.append(button)
            grid.attach(button, 0, 2*ix, 2, 1)
            if ix == recent_type:
                button.set_active(True)
            ix += 1

        box.pack_start(grid, False, False, 0)

        page = box

        page.show_all()

        self.append_page(page)
        self.set_page_title(page, _('Choose the output format'))

        self.set_page_type(page, Gtk.AssistantPageType.CONTENT)


    def create_page_options(self):
        # as we do not know yet what to show, we create an empty page
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_border_width(0)
        page.set_spacing(12)

        page.show_all()

        self.append_page(page)
        self.set_page_title(page, _('Export options'))
        self.set_page_complete(page, False)
        self.set_page_type(page, Gtk.AssistantPageType.CONTENT)

    def forward_func(self, pagenumber, data):
        """This function is called on forward press.

            Normally, go to next page, however, before options,
            we decide if options to show
        """
        if pagenumber == _ExportAssistant_pages['exporttypes'] :
            #decide if options need to be shown:
            self.option_box_instance = None
            ix = self.get_selected_format_index()
            if not self.map_exporters[ix].get_config():
                # no options needed
                return pagenumber + 2
        elif pagenumber == _ExportAssistant_pages['options']:
            # need to check to see if we should show file selection
            if (self.option_box_instance and
                hasattr(self.option_box_instance, "no_fileselect")):
                # don't show fileselect, but mark it ok
                return pagenumber + 2
        return pagenumber + 1

    def create_options(self):
        """This method gets the option page, and fills it with the options."""
        option = self.get_selected_format_index()
        vbox = self.get_nth_page(_ExportAssistant_pages['options'])
        (config_title, config_box_class) = self.map_exporters[option].get_config()
        #self.set_page_title(vbox, config_title)
        # remove present content of the vbox
        list(map(vbox.remove, vbox.get_children()))
        # add new content
        if config_box_class:
            self.option_box_instance = config_box_class(
                self.person, self.dbstate, self.uistate, track=self.track,
                window=self.window)
            box = self.option_box_instance.get_option_box()
            vbox.add(box)
        else:
            self.option_box_instance = None
        vbox.show_all()

        # We silently assume all options lead to accepted behavior
        self.set_page_complete(vbox, True)

    def create_page_fileselect(self):
        self.chooser = Gtk.FileChooserWidget(Gtk.FileChooserAction.SAVE)
        self.chooser.set_homogeneous(False) # Fix for bug #8350.
        #add border
        self.chooser.set_border_width(12)
        #global files, ask before overwrite
        self.chooser.set_local_only(False)
        self.chooser.set_do_overwrite_confirmation(True)

        #created, folder and name not set
        self.folder_is_set = False

        #connect changes in filechooser with check to mark page complete
        self.chooser.connect("selection-changed", self.check_fileselect)
        self.chooser.connect("key-release-event", self.check_fileselect)
        #first selection does not give a selection-changed event, grab the button
        self.chooser.connect("button-release-event", self.check_fileselect)
        #Note, we can induce an exotic error, delete filename,
        #  do not release button, click forward. We expect user not to do this
        #  In case he does, recheck on confirmation page!

        self.chooser.show_all()
        page = self.chooser

        self.append_page(page)
        self.set_page_title(page, _('Select save file'))
        self.set_page_type(page, Gtk.AssistantPageType.CONTENT)

    def check_fileselect(self, filechooser, event=None, show=True):
        """Given a filechooser, determine if it can be marked complete in
        the Assistant.

        Used as normal callback and event callback. For callback, we will have
        show=True
        """
        filename = filechooser.get_filename()
        if not filename:
            self.set_page_complete(filechooser, False)
        else:
            folder = filechooser.get_current_folder()
            if not folder:
                folder = find_folder(filename)
            else:
                folder = find_folder(folder)
            #the file must be valid, not a folder, and folder must be valid
            if (filename and os.path.basename(filename.strip()) and folder):
                #this page of the assistant is complete
                self.set_page_complete(filechooser, True)
            else :
                self.set_page_complete(filechooser, False)

    def create_page_confirm(self):
        # Construct confirm page
        self.confirm = Gtk.Label()
        self.confirm.set_line_wrap(True)
        self.confirm.set_use_markup(True)
        self.confirm.show()

        image = Gtk.Image()
        image.set_from_file(SPLASH)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(12)
        box.set_spacing(6)
        box.pack_start(image, False, False, 5)
        box.pack_start(self.confirm, False, False, 5)
        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, False, False, 0)

        page = box
        self.append_page(page)
        self.set_page_title(page, _('Final confirmation'))
        self.set_page_type(page, Gtk.AssistantPageType.CONFIRM)
        self.set_page_complete(page, True)

    def create_page_summary(self):
        # Construct summary page
        # As this is the last page needs to be of page_type
        # Gtk.AssistantPageType.CONFIRM or Gtk.AssistantPageType.SUMMARY
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_border_width(12)
        vbox.set_spacing(6)

        image = Gtk.Image()
        image.set_from_file(SPLASH)
        vbox.pack_start(image, False, False, 5)

        self.labelsum = Gtk.Label()
        self.labelsum.set_line_wrap(True)
        self.labelsum.set_use_markup(True)
        vbox.pack_start(self.labelsum, False, False, 0)

        page = vbox
        page.show_all()

        self.append_page(page)
        self.set_page_title(page, _('Summary'))
        self.set_page_complete(page, False)
        self.set_page_type(page, Gtk.AssistantPageType.SUMMARY)

    def do_apply(self):
        pass

    def do_close(self):
        self.uistate.set_export_mode(False)
        if self.writestarted :
            pass
        else :
            self.close()

    def do_cancel(self):
        self.do_close()

    def do_prepare(self, page):
        """
        The "prepare" signal is emitted when a new page is set as the
        assistant's current page, but before making the new page visible.

        :param page:   the new page to prepare for display.

        """
        #determine if we go backward or forward
        page_number = self.get_current_page()
        assert page == self.get_nth_page(page_number)
        if page_number <= self.__previous_page :
            back = True
        else :
            back = False

        if back :
            #when moving backward, show page as it was,
            #page we come from is set incomplete so as to disallow user jumping
            # to last page after backward move
            self.set_page_complete(self.get_nth_page(self.__previous_page),
                                    False)

        elif page_number == _ExportAssistant_pages['options']:
            self.create_options()
            self.set_page_complete(page, True)
        elif page == self.chooser :
            # next page is the file chooser, reset filename, keep folder where user was
            folder, name = self.suggest_filename()
            page.set_action(Gtk.FileChooserAction.SAVE)
            if self.folder_is_set:
                page.set_current_name(name)
            else :
                page.set_current_name(name)
                page.set_current_folder(folder)
                self.folder_is_set = True
            # see if page is complete with above
            self.check_fileselect(page, show=True)

        elif self.get_page_type(page) ==  Gtk.AssistantPageType.CONFIRM:
            # The confirm page with apply button
            # Present user with what will happen
            ix = self.get_selected_format_index()
            format = self.map_exporters[ix].get_name()
            page_complete = False
            # If no file select:
            if (self.option_box_instance and
                hasattr(self.option_box_instance, "no_fileselect")):
                # No file selection
                filename = ''
                confirm_text = _(
                    'The data will be exported as follows:\n\n'
                    'Format:\t%s\n\n'
                    'Press Apply to proceed, Back to revisit '
                    'your options, or Cancel to abort') % (format.replace("_",""), )
                page_complete = True
            else:
                #Allow for exotic error: file is still not correct
                self.check_fileselect(self.chooser, show=False)
                if self.get_page_complete(self.chooser) :
                    filename = self.chooser.get_filename()
                    name = os.path.split(filename)[1]
                    folder = os.path.split(filename)[0]
                    confirm_text = _(
                    'The data will be saved as follows:\n\n'
                    'Format:\t%(format)s\nName:\t%(name)s\nFolder:\t%(folder)s\n\n'
                    'Press Apply to proceed, Go Back to revisit '
                    'your options, or Cancel to abort') % {
                    'format': format.replace("_",""),
                    'name': name,
                    'folder': folder}
                    page_complete = True
                else :
                    confirm_text = _(
                        'The selected file and folder to save to '
                        'cannot be created or found.\n\n'
                        'Press Back to return and select a valid filename.'
                        )
                    page_complete = False
            # Set the page_complete status
            self.set_page_complete(page, page_complete)
            # If it is ok, then look for alternate confirm_text
            if (page_complete and
                self.option_box_instance and
                hasattr(self.option_box_instance, "confirm_text")):
                # Override message
                confirm_text = self.option_box_instance.confirm_text
            self.confirm.set_label(confirm_text)
            self.progressbar.hide()

        elif self.get_page_type(page) ==  Gtk.AssistantPageType.SUMMARY :
            # The summary page
            # Lock page, show progress bar
            self.pre_save(page)
            # save
            success = self.save()
            # Unlock page
            self.post_save()

            #update the label and title
            if success:
                conclusion_title =  _('Your data has been saved')
                conclusion_text = _(
                'The copy of your data has been '
                'successfully saved. You may press Close button '
                'now to continue.\n\n'
                'Note: the database currently opened in your Gramps '
                'window is NOT the file you have just saved. '
                'Future editing of the currently opened database will '
                'not alter the copy you have just made. ')
                #add test, what is dir
                conclusion_text += '\n\n' + _('Filename: %s') %self.chooser.get_filename()
            else:
                conclusion_title =  _('Saving failed')
                conclusion_text = _(
                'There was an error while saving your data. '
                'You may try starting the export again.\n\n'
                'Note: your currently opened database is safe. '
                'It was only '
                'a copy of your data that failed to save.')
            self.labelsum.set_label(conclusion_text)
            self.set_page_title(page, conclusion_title)
            self.set_page_complete(page, True)
        else :
            #whatever other page, if we show it, it is complete to
            self.set_page_complete(page, True)

        #remember previous page for next time
        self.__previous_page = page_number

    def get_intro_text(self):
        return _('Under normal circumstances, Gramps does not require you '
                 'to directly save your changes. All changes you make are '
                 'immediately saved to the database.\n\n'
                 'This process will help you save a copy of your data '
                 'in any of the several formats supported by Gramps. '
                 'This can be used to make a copy of your data, backup '
                 'your data, or convert it to a format that will allow '
                 'you to transfer it to a different program.\n\n'
                 'If you change your mind during this process, you '
                 'can safely press the Cancel button at any time and your '
                 'present database will still be intact.')

    def get_selected_format_index(self):
        """
        Query the format radiobuttons and return the index number of the
        selected one.

        """
        for ix in range(len(self.format_buttons)):
            button = self.format_buttons[ix]
            if button.get_active():
                return ix
        return 0

    def suggest_filename(self):
        """Prepare suggested filename and set it in the file chooser."""
        ix = self.get_selected_format_index()
        ext = self.map_exporters[ix].get_extension()

        default_dir = config.get('paths.recent-export-dir')

        if ext == 'gramps':
            new_filename = os.path.join(default_dir,'data.gramps')
        elif ext == 'burn':
            new_filename = os.path.basename(self.dbstate.db.get_save_path())
        else:
            new_filename = get_new_filename(ext,default_dir)
        return (default_dir, os.path.split(new_filename)[1])

    def save(self):
        """
        Perform the actual Save As/Export operation.

        Depending on the success status, set the text for the final page.

        """
        success = False
        try:
            if (self.option_box_instance and
                hasattr(self.option_box_instance, "no_fileselect")):
                filename = ""
            else:
                filename = self.chooser.get_filename()
                config.set('paths.recent-export-dir', os.path.split(filename)[0])
            ix = self.get_selected_format_index()
            config.set('behavior.recent-export-type', ix)
            export_function = self.map_exporters[ix].get_export_function()
            success = export_function(self.dbstate.db,
                            filename,
                            User(error=ErrorDialog, parent=self.uistate.window,
                                 callback=self.callback),
                            self.option_box_instance)
        except:
            #an error not catched in the export_function itself
            success = False
            log.error(_("Error exporting your Family Tree"), exc_info=True)
        return success

    def pre_save(self, page):
        ''' Since we are in 'prepare', the next page is not yet shown, so
        modify the 'confirm' page text and show the progress bar
        '''
        self.confirm.set_label(
            _("Please wait while your data is selected and exported"))
        self.writestarted = True
        self.progressbar.show()
        self.show_all()

        self.set_busy_cursor(1)

    def post_save(self):
        self.set_busy_cursor(0)
        self.progressbar.hide()
        self.writestarted = False

    def set_busy_cursor(self,value):
        """
        Set or unset the busy cursor while saving data.
        """
        BUSY_CURSOR = Gdk.Cursor.new_for_display(Gdk.Display.get_default(),
                                                 Gdk.CursorType.WATCH)

        if value:
            Gtk.Assistant.get_window(self).set_cursor(BUSY_CURSOR)
            #self.set_sensitive(0)
        else:
            Gtk.Assistant.get_window(self).set_cursor(None)
            #self.set_sensitive(1)

        while Gtk.events_pending():
            Gtk.main_iteration()

    def pulse_progressbar(self, value, text=None):
        self.progressbar.set_fraction(min(value/100.0, 1.0))
        if text:
            self.progressbar.set_text("%s: %d%%" % (text, value))
            self.confirm.set_label(
                _("Please wait while your data is selected and exported") +
                "\n" + text)
        else:
            self.progressbar.set_text("%d%%" % value)
        while Gtk.events_pending():
            Gtk.main_iteration()
