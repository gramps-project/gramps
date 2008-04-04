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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

import logging
_LOG = logging.getLogger(".Editors.EditNote")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade
import gobject
import pango

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Config
from const import GLADE_FILE
from Editors._StyledTextEditor import StyledTextEditor
from Editors._EditPrimary import EditPrimary
from DisplayTabs import GrampsTab, NoteBackRefList
from GrampsWidgets import (MonitoredDataType, MonitoredCheckbox, 
                           MonitoredEntry, PrivacyButton)
from gen.lib import Note
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------

class NoteTab(GrampsTab):
    """
    This class provides the tabpage of the note
    """

    def __init__(self, dbstate, uistate, track, name, widget):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: L{DbState.DbState}
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: L{DisplayState.DisplayState}
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        @param widget: widget to be shown in the tab
        @type widget: gtk widget
        """
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        eventbox = gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox)
        self._set_label(show_image=False)
        eventbox.connect('key_press_event', self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

#-------------------------------------------------------------------------
#
# EditNote
#
#-------------------------------------------------------------------------

class EditNote(EditPrimary):
    def __init__(self, dbstate, uistate, track, note, callback=None, 
                 callertitle = None, extratype = None):
        """Create an EditNote window. Associate a note with the window.
        
        @param callertitle: Text passed by calling object to add to title 
        @type callertitle: str
        @param extratype: Extra L{NoteType} values to add to the default types.
        They are removed from the ignorelist of L{NoteType}.
        @type extratype: list of int
        
        """
        self.callertitle = callertitle
        self.extratype = extratype
        EditPrimary.__init__(self, dbstate, uistate, track, note, 
                             dbstate.db.get_note_from_handle, 
                             dbstate.db.get_note_from_gramps_id, callback)

    def empty_object(self):
        """Return an empty Note object for comparison for changes.
        
        It is used by the base class L{EditPrimary}.
        
        """
        empty_note = Note();
        if self.extratype:
            empty_note.set_type(self.extratype[0])
        return empty_note

    def get_menu_title(self):
        if self.obj.get_handle():
            if self.callertitle :
                title = _('Note: %(id)s - %(context)s') % {
                    'id'      : self.obj.get_gramps_id(),
                    'context' : self.callertitle
                }
            else :
                title = _('Note: %s') % self.obj.get_gramps_id()
        else:
            if self.callertitle :
                title = _('New Note - %(context)s') % {
                    'context' : self.callertitle
                }
            else :
                title = _('New Note')  
            
        return title
    
    def get_custom_notetypes(self):
        return self.dbstate.db.get_note_types()

    def _local_init(self):
        """Local initialization function.
        
        Perform basic initialization, including setting up widgets
        and the glade interface. It is called by the base class L{EditPrimary},
        and overridden here.
        
        """
        self.top = glade.XML(GLADE_FILE, "edit_note", "gramps")
        win = self.top.get_widget("edit_note")
        self.set_window(win, None, self.get_menu_title())

        width = Config.get(Config.NOTE_WIDTH)
        height = Config.get(Config.NOTE_HEIGHT)
        self.window.set_default_size(width, height)

        vboxnote =  self.top.get_widget('vbox131')
        notebook = self.top.get_widget('note_notebook')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.ntab = NoteTab(self.dbstate, self.uistate, self.track, 
                              _('_Note'), vboxnote)
        
        self.build_interface()
        
    def _setup_fields(self):
        """Get control widgets and attach them to Note's attributes."""
        self.type_selector = MonitoredDataType(
            self.top.get_widget('type'),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            custom_values=self.get_custom_notetypes(),
            ignore_values=self.obj.get_type().get_ignore_list(self.extratype))

        self.check = MonitoredCheckbox(
            self.obj,
            self.top.get_widget('format'),
            self.obj.set_format,
            self.obj.get_format,
            on_toggle = self.flow_changed,
            readonly = self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.top.get_widget('id'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.marker = MonitoredDataType(
            self.top.get_widget('marker'), 
            self.obj.set_marker, 
            self.obj.get_marker, 
            self.db.readonly,
            self.db.get_marker_types())

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj, self.db.readonly)
        
    def _connect_signals(self):
        """Connects any signals that need to be connected.
        
        Called by the init routine of the base class L{EditPrimary}.
        
        """
        self.define_ok_button(self.top.get_widget('ok'), self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'), '')
    
    def _create_tabbed_pages(self):
        """Create the notebook tabs and inserts them into the main window."""
        notebook = self.top.get_widget("note_notebook")

        self._add_tab(notebook, self.ntab)

        handles = self.dbstate.db.find_backlink_handles(self.obj.handle)
        rlist = NoteBackRefList(self.dbstate, self.uistate, self.track, handles)
        self.backref_tab = self._add_tab(notebook, rlist)
        
        self._setup_notebook_tabs(notebook)

# THIS IS THE MARKUP VERSION - enable for markup
    def build_interface(self):
        self.texteditor = self.top.get_widget('texteditor')
        self.texteditor.set_editable(not self.dbstate.db.readonly)

        # create a formatting toolbar
        if not self.dbstate.db.readonly:
            vbox = self.top.get_widget('container')
            vbox.pack_start(self.texteditor.get_toolbar(),
                            expand=False, fill=False)
                
        # setup initial values for textview and textbuffer
        if self.obj:
            self.empty = False
            self.flow_changed(self.obj.get_format())
            self.texteditor.set_text(self.obj.get_styledtext())
            _LOG.debug("Initial Note: %s" % str(self.texteditor.get_text()))
        else:
            self.empty = True

# NON-MARKUP VERSION - Disable for markup
    #def build_interface(self):
        #textbuffer = gtk.TextBuffer()

        #self.text = self.top.get_widget('text')
        #self.text.set_editable(not self.dbstate.db.readonly)
        #self.text.set_buffer(textbuffer)
        
        ## setup spell checking interface
        #spellcheck = Spell(self.text)
        #liststore = gtk.ListStore(gobject.TYPE_STRING)
        #cell = gtk.CellRendererText()
        #lang_selector = self.top.get_widget('spell')
        #lang_selector.set_model(liststore)
        #lang_selector.pack_start(cell, True)
        #lang_selector.add_attribute(cell, 'text', 0)
        #act_lang = spellcheck.get_active_language()
        #idx = 0
        #for lang in spellcheck.get_all_languages():
            #lang_selector.append_text(lang)
            #if lang == act_lang:
                #act_idx = idx
            #idx = idx + 1
        #lang_selector.set_active(act_idx)
        #lang_selector.connect('changed', self.on_spell_change, spellcheck)
        ##lang_selector.set_sensitive(Config.get(Config.SPELLCHECK))
                
        ## setup initial values for textview and textbuffer
        #if self.obj:
            #self.empty = False
            #self.flow_changed(self.obj.get_format())
            #textbuffer.set_text(self.obj.get())
        #else:
            #self.empty = True
            
    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Note'), self.get_menu_title())

    def _post_init(self):
        self.texteditor.grab_focus()

    def update_note(self):
        """Update the Note object with current value."""
        if self.obj:
            text = self.texteditor.get_text()
            self.obj.set_styledtext(text)
            _LOG.debug(str(text))

    def flow_changed(self, active):
        if active:
            # Set the text style to monospace
            self.text.set_wrap_mode(gtk.WRAP_NONE)
            self.texteditor.modify_font(pango.FontDescription("monospace"))
        else:
            # Set the text style to normal
            self.texteditor.set_wrap_mode(gtk.WRAP_WORD)
            self.texteditor.modify_font(pango.FontDescription("normal"))

    def save(self, *obj):
        """Save the data."""
        self.ok_button.set_sensitive(False)
        
        self.update_note()
        
        if self.object_is_empty():
            ErrorDialog(_("Cannot save note"), 
                        _("No data exists for this note. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return
        
        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            msg1 = _("Cannot save note. ID already exists.")
            msg2 = _("You have attempted to use the existing GRAMPS ID with "
                         "value %(id)s. This value is already used. Please "
                         "enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return
        
        trans = self.db.transaction_begin()

        if not self.obj.get_handle():
            self.db.add_note(self.obj, trans)
            msg = _("Add Note")
        else:
            if not self.obj.get_gramps_id():
                self.obj.set_gramps_id(self.db.find_next_note_gramps_id())
            self.db.commit_note(self.obj, trans)
            msg = _("Edit Note")
            
        self.db.transaction_commit(trans, msg)
        
        if self.callback:
            self.callback(self.obj.get_handle())
        self.close()

    def _cleanup_on_exit(self):
        (width, height) = self.window.get_size()
        Config.set(Config.NOTE_WIDTH, width)
        Config.set(Config.NOTE_HEIGHT, height)
        Config.sync()

class DeleteNoteQuery:
    def __init__(self, dbstate, uistate, note, the_lists):
        self.note = note
        self.db = dbstate.db
        self.uistate = uistate
        self.the_lists = the_lists

    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list, family_list, event_list, place_list, source_list,
         media_list, repo_list) = self.the_lists

        note_handle = self.note.get_handle()

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_note(note_handle)
            self.db.commit_person(person, trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_note(note_handle)
            self.db.commit_family(family, trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_note(note_handle)
            self.db.commit_event(event, trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            place.remove_note(note_handle)
            self.db.commit_place(place, trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            source.remove_note(note_handle)
            self.db.commit_source(source, trans)

        for handle in media_list:
            media = self.db.get_object_from_handle(handle)
            media.remove_note(note_handle)
            self.db.commit_media_object(media, trans)

        for handle in repo_list:
            repo = self.db.get_repository_from_handle(handle)
            repo.remove_note(note_handle)
            self.db.commit_repository(repo, trans)

        self.db.enable_signals()
        self.db.remove_note(note_handle, trans)
        self.db.transaction_commit(
            trans,_("Delete Note (%s)") % self.note.get_gramps_id())
