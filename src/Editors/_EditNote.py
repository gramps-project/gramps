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

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import const
import Spell
import Config
import MarkupText
from _EditPrimary import EditPrimary
from GrampsWidgets import *
from RelLib import Note

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class EditNote(EditPrimary):

    def __init__(self, state, uistate, track, note, callback=None):
        """Create an EditNote window. Associate a note with the window."""
        EditPrimary.__init__(self, state, uistate, track, note, 
                             state.db.get_note_from_handle, callback)

    def empty_object(self):
        """Return an empty Note object for comparison for changes.
        
        It is used by the base class (EditPrimary).
        
        """
        return Note()

    def get_menu_title(self):
        if self.obj.get_handle():
            title = _('Note') + ': %s' % self.obj.get_gramps_id()
        else:
            title = _('New Note')
        return title

    def _local_init(self):
        """Local initialization function.
        
        Perform basic initialization, including setting up widgets
        and the glade interface. It is called by the base class (EditPrimary),
        and overridden here.
        
        """
        self.top = gtk.glade.XML(const.gladeFile, "edit_note", "gramps")
        win = self.top.get_widget("edit_note")
        self.set_window(win, None, self.get_menu_title())

        width = Config.get(Config.NOTE_WIDTH)
        height = Config.get(Config.NOTE_HEIGHT)
        self.window.set_default_size(width, height)

        self.build_interface()
        
    def _setup_fields(self):
        """Get control widgets and attached them to Note's attributes."""
        self.type_selector = MonitoredDataType(
            self.top.get_widget('type'),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly)

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
        
    def _connect_signals(self):
        """Connects any signals that need to be connected.
        
        Called by the init routine of the base class (_EditPrimary).
        
        """
        self.define_ok_button(self.top.get_widget('ok'),self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'), '')
        
    def build_interface(self):
        FORMAT_TOOLBAR = '''
        <ui>
        <toolbar name="ToolBar">
          <toolitem action="italic"/>  
          <toolitem action="bold"/>  
          <toolitem action="underline"/>
          <separator/>
          <toolitem action="font"/>
          <toolitem action="foreground"/>
          <toolitem action="background"/>
          <separator/>
          <toolitem action="clear"/>
        </toolbar>
        </ui>
        '''

        buffer = MarkupText.MarkupBuffer()

        self.text = self.top.get_widget('text')
        self.text.set_editable(not self.dbstate.db.readonly)
        self.text.set_buffer(buffer)
        self.text.connect('key-press-event', self.on_textview_key_press_event)
        self.text.connect('populate-popup', self.on_textview_populate_popup)
        self.spellcheck = Spell.Spell(self.text)

        # create a formatting toolbar
        if not self.dbstate.db.readonly:
            uimanager = gtk.UIManager()
            uimanager.insert_action_group(buffer.format_action_group, 0)
            uimanager.add_ui_from_string(FORMAT_TOOLBAR)
            uimanager.ensure_update()

            toolbar = uimanager.get_widget('/ToolBar')      
            toolbar.set_style(gtk.TOOLBAR_ICONS)
            vbox = self.top.get_widget('container')
            vbox.pack_start(toolbar, False)
                
        # setup initial values for textview and buffer
        if self.obj:
            self.empty = False
            self.flow_changed(self.obj.get_format())
            buffer.set_text(self.obj.get(markup=True))
            log.debug("Initial Note: %s" % buffer.get_text())
        else:
            self.empty = True

    def on_textview_key_press_event(self, textview, event):
        """Handle shortcuts in the TextView."""
        return textview.get_buffer().on_key_press_event(textview, event)
    
    def on_textview_populate_popup(self, view, menu):
        """Hijack popup menu population to be able to edit it."""
        pass
    
    def update_note(self):
        """Update the Note object with current value."""
        if self.obj:
            buffer = self.text.get_buffer()
            (start, stop) = buffer.get_bounds()
            text = buffer.get_text(start, stop)
            self.obj.set(text)
            log.debug(text)

    def flow_changed(self, active):
        if active:
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.text.set_wrap_mode(gtk.WRAP_WORD)

    def save(self, *obj):
        """Save the data."""
        trans = self.db.transaction_begin()

        self.update_note()

        if self.obj.get_handle():
            self.db.commit_note(self.obj,trans)
        else:
            self.db.add_note(self.obj,trans)
        self.db.transaction_commit(trans, _("Edit Note"))
        
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
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_note(note_handle)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_note(note_handle)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            place.remove_note(note_handle)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            source.remove_note(note_handle)
            self.db.commit_source(source,trans)

        for handle in media_list:
            media = self.db.get_object_from_handle(handle)
            media.remove_note(note_handle)
            self.db.commit_media_object(media,trans)

        for handle in repo_list:
            repo = self.db.get_repository_from_handle(handle)
            repo.remove_note(note_handle)
            self.db.commit_repository(repo,trans)

        self.db.enable_signals()
        self.db.remove_note(note_handle, trans)
        self.db.transaction_commit(
            trans,_("Delete Note (%s)") % self.note.get_gramps_id())
