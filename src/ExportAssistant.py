#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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

# Written by B.Malengier

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import sys
from gettext import gettext as _

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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import const
import Config
from PluginUtils import export_list
import Utils
import ManagedWindow

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_gramps_png = os.path.join(const.image_dir,"gramps.png")
_splash_jpg = os.path.join(const.image_dir,"splash.jpg")

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

class ExportAssistant(gtk.Assistant, ManagedWindow.ManagedWindow) :
    """
    This class creates a GTK assistant to guide the user through the various
    Save as/Export options. The overall goal is to keep things simple by
    presenting few choice options on each assistant page.
    
    The export formats and options are obtained from the plugins
    """

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
        
        #set up Assisant
        gtk.Assistant.__init__(self)
        
        #set up ManagedWindow
        self.top_title = _("Export Assistant")
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],
                                                 self.__class__)
        self.set_window(self, None, self.top_title, isWindow=True)
        
        #set up callback method for the export plugins
        self.callback = self.uistate.pulse_progressbar
            
        if self.dbstate.active:
            self.person = self.dbstate.get_active_person()
        else:
            self.person = self.dbstate.db.find_initial_person()
            
        self.logo      = gtk.gdk.pixbuf_new_from_file(_gramps_png)
        self.splash    = gtk.gdk.pixbuf_new_from_file(_splash_jpg)
            
        self.obtain_export_formats()
        
        self.__previous_page = -1

        #create the assistant pages
        self.create_page_intro()
        self.create_page_exporttypes()
        self.create_page_options()
        self.create_page_fileselect()
        self.create_page_confirm()
        #no progress page, use uistate progressbar
        self.create_page_summary()
        
        #we need our own forward function as options page must not always be shown
        self.set_forward_page_func(self.forward_func, None)
        
        #ManagedWindow show method
        ManagedWindow.ManagedWindow.show(self)
        
    def build_menu_names(self,obj):
        ''' Override ManagedWindow method
        '''
        return (self.top_title, None)
        
    def create_page_intro(self):
        ''' Create the introduction page
        '''
        label = gtk.Label(self.get_intro_text())
        label.set_line_wrap(True)
        label.set_use_markup(True)
        
        page = label
        page.show_all()

        self.append_page(page)
        self.set_page_header_image(page, self.logo)
        self.set_page_side_image(page, self.splash)
        self.set_page_title(page, _('Saving your data'))
        self.set_page_complete(page, True)
        self.set_page_type(page, gtk.ASSISTANT_PAGE_INTRO)
    
    def create_page_exporttypes(self):
        ''' Create the export type page
            A Title label
            A table of format radio buttons and their descriptions.
        '''
        self.format_buttons = []

        box = gtk.VBox()
        box.set_border_width(12)
        box.set_spacing(12)

        table = gtk.Table(2*len(self.exportformats),2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        
        tip = gtk.Tooltips()
        
        group = None
        for ix in range(len(self.exportformats)):
            title = self.exportformats[ix][1]
            description= self.exportformats[ix][2]

            button = gtk.RadioButton(group,title)
            if not group:
                group = button
            self.format_buttons.append(button)
            table.attach(button,0,2,2*ix,2*ix+1)
            tip.set_tip(button,description)
        
        box.add(table)
        
        page = box
        
        page.show_all()

        self.append_page(page)
        self.set_page_header_image(page, self.logo)
        self.set_page_title(page, _('Choose the output format'))
    
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONTENT)
        
            
    def create_page_options(self):
        # as we do not know yet what to show, we create an empty page
        page = gtk.VBox()
        page.set_border_width(12)
        page.set_spacing(12)
        
        page.show_all()

        self.append_page(page)
        self.set_page_header_image(page, self.logo)
        ix = self.get_selected_format_index()
        self.set_page_title(page, self.exportformats[ix][3][0])
        self.set_page_complete(page, False)
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONTENT)
        
    def forward_func(self, pagenumber, data):
        ''' This function is called on forward press.
            Normally, go to next page, however, before options,
            we decide if options to show
        '''
        if pagenumber == _ExportAssistant_pages['exporttypes'] :
            #decide if options need to be shown:
            ix = self.get_selected_format_index()
            if self.exportformats[ix][3]: 
                return pagenumber + 1
            else :
                # no options needed
                return pagenumber + 2
        else :
            return pagenumber + 1
        
    def create_options(self):
        ''' This method gets the option page, and fills it with the options
        '''
        option = self.get_selected_format_index()
        vbox = self.get_nth_page(_ExportAssistant_pages['options'])
        # remove present content of the vbox
        vbox.foreach(vbox.remove)
        # add new content
        option_box_class = self.exportformats[option][3][1]
        self.option_box_instance = option_box_class(self.person)
        box = self.option_box_instance.get_option_box()
        vbox.add(box)
        vbox.show_all()
        
        # We silently assume all options lead to accepted behavior
        self.set_page_complete(vbox, True)
        
    def create_page_fileselect(self):
        self.chooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_SAVE)
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
        self.set_page_header_image(page, self.logo)
        self.set_page_title(page, _('Select Save File'))
        #see if page can be set as complete :
        self.check_fileselect(page)
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONTENT)
        
    def check_fileselect(self, filechooser, event=None):
        ''' Given a filechooser, determine if it can be marked complete
            in the Assistant
            Used as normal callback and event callback.
        '''
        filename = filechooser.get_filename()
        folder = filechooser.get_current_folder()
        #the file must be valid, not a folder, and folder must be valid
        if filename and filename.strip and Utils.find_folder(filename) == '' \
                    and folder and Utils.find_folder(folder): 
            #this page of the assistant is complete
            self.set_page_complete(filechooser, True)
            
        else :
            self.set_page_complete(filechooser, False)
        
    def create_page_confirm(self):
        # Construct confirm page
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.show()
        
        page = label
        self.append_page(page)
        self.set_page_header_image(page, self.logo)
        self.set_page_title(page, _('Final confirmation'))
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONFIRM)
        self.set_page_complete(page, True)
        
    def create_page_progress(self):
        ''' We use the uistate progress bar to indicate progress
        '''
        pass
    
    def create_page_summary(self):
        # Construct summary page
        # As this is the last page needs to be of page_type
        # gtk.ASSISTANT_PAGE_CONFIRM or gtk.ASSISTANT_PAGE_SUMMARY
        label = gtk.Label('Thanks for using our Export Assistant!')
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.show()
        
        page = label
        self.append_page(page)
        self.set_page_header_image(page, self.logo)
        self.set_page_title(page, _('Summary'))
        self.set_page_side_image(page, self.splash)
        self.set_page_type(page, gtk.ASSISTANT_PAGE_SUMMARY)

        
    def do_apply(self):
        pass

    def do_cancel(self):
        self.close()

    def do_close(self):
        self.close()

    def do_prepare(self, page):
        '''
        The "prepare" signal is emitted when a new page is set as the 
        assistant's current page, but before making the new page visible.
        @param page:	the new page to prepare for display
        '''
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
            
        elif page_number == _ExportAssistant_pages['options'] :
            self.create_options()
            self.set_page_complete(page, True)
        elif page == self.chooser :
            # next page is the file chooser, reset filename, keep folder where user was
            folder, name = self.suggest_filename()
            if self.folder_is_set :
                page.set_current_name(name)
            else :
                page.set_current_name(name)
                page.set_current_folder(folder)
                self.folder_is_set = True
            # see if page is complete with above
            self.check_fileselect(page)
            
        elif self.get_page_type(page) ==  gtk.ASSISTANT_PAGE_CONFIRM :
            # The confirm page with apply button
            # Present user with what will happen
            ix = self.get_selected_format_index()
            format = self.exportformats[ix][1].replace('_','')

            #Allow for exotic error: file is still not correct
            self.check_fileselect(self.chooser)
            if self.get_page_complete(self.chooser) :
                filename = unicode(self.chooser.get_filename(),
                           sys.getfilesystemencoding())
                name = os.path.split(filename)[1]
                folder = os.path.split(filename)[0]
                confirm_text = _(
                'The data will be saved as follows:\n\n'
                'Format:\t%s\nName:\t%s\nFolder:\t%s\n\n'
                'Press Apply to proceed, Back to revisit '
                'your options, or Cancel to abort') % (format, name, folder)
                self.set_page_complete(page, True)
            else :
                confirm_text = _(
                'The selected file and folder to save to '
                'cannot be created or found.\n\n'
                'Press Back to return and select a valid filename.'
                ) 
                self.set_page_complete(page, False)
            
            page.set_label(confirm_text)
                
        elif self.get_page_type(page) ==  gtk.ASSISTANT_PAGE_SUMMARY :
            # The summary page
            # Lock page, show progress bar
            self.pre_save()
            # save
            self.save()
            # Unlock page
            self.post_save()
            
            #update the label and title
            
            success = True
            if success:
                conclusion_title =  _('Your data has been saved')
                conclusion_text = _(
                'The copy of your data has been '
                'successfully saved. You may press Close button '
                'now to continue.\n\n'
                'Note: the database currently opened in your GRAMPS '
                'window is NOT the file you have just saved. '
                'Future editing of the currently opened database will '
                'not alter the copy you have just made. ')
                #add test, what is dir
                conclusion_text += '\n\n' + 'Filename: %s' %self.chooser.get_filename()
            else:
                conclusion_title =  _('Saving failed'),
                conclusion_text = _(
                'There was an error while saving your data. '
                'You may try starting the export again.\n\n'
                'Note: your currently opened database is safe. '
                'It was only '
                'a copy of your data that failed to save.')
            page.set_label(conclusion_text)
            self.set_page_title(page, conclusion_title)
            self.set_page_complete(page, True)
        else :
            #whatever other page, if we show it, it is complete to
            self.set_page_complete(page, True)
            
        #remember previous page for next time
        self.__previous_page = page_number
        
    def close(self, *obj) :
        #clean up ManagedWindow menu, then destroy window, bring forward parent
        ManagedWindow.ManagedWindow.close(self,*obj)
    
    def obtain_export_formats(self):
        """
        This method builds its own list of available exports. 
        The list is built from the PluginMgr.export_list list 
        and from the locally defined exports (i.e. native export defined here).
        """
        self.exportformats = [item for item in export_list]
        
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
        
    def suggest_filename(self):
        """
        Prepare suggested filename and set it in the file chooser. 
        """
        ix = self.get_selected_format_index()
        ext = self.exportformats[ix][4]
        
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
        return (default_dir, os.path.split(new_filename)[1])
    
    def save(self):
        """
        Perform the actual Save As/Export operation. 
        Depending on the success status, set the text for the final page.
        """
        filename = unicode(self.chooser.get_filename(),
                           sys.getfilesystemencoding())
        Config.set(Config.RECENT_EXPORT_DIR,os.path.split(filename)[0])
        ix = self.get_selected_format_index()
        if self.exportformats[ix][3]:
            success = self.exportformats[ix][0](self.dbstate.db,
                                          filename,self.person,
                                          self.option_box_instance,
                                          self.callback)
        else:
            success = self.exportformats[ix][0](self.dbstate.db,
                                          filename,self.person,
                                          self.callback)
        return success
    
    def pre_save(self):
        self.uistate.set_busy_cursor(1)
        self.set_busy_cursor(1)
        self.uistate.progress.show()

    def post_save(self):
        self.uistate.set_busy_cursor(0)
        self.set_busy_cursor(0)
        self.uistate.progress.hide()
        
    def set_busy_cursor(self,value):
        ''' set or unset the busy cursor while saving data
            Note : self.window is the gtk.Assistant gtk.Window, not 
                   a part of ManagedWindow
        '''
        if value:
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            self.set_sensitive(0)
        else:
            self.window.set_cursor(None)
            self.set_sensitive(1)

        while gtk.events_pending():
            gtk.main_iteration()
        


