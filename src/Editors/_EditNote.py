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
import pango

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import const
import Spell
import Config
from _EditPrimary import EditPrimary
from MarkupText import EditorBuffer
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class EditNote(EditPrimary):

    def __init__(self, state, uistate, track, note, callback=None):
        """
        Creates an EditPerson window.  Associates a person with the window.
        """
        EditPrimary.__init__(self, state, uistate, track, note, 
                             state.db.get_note_from_handle, callback)

    def empty_object(self):
        """
        Returns an empty Person object for comparison for changes. This
        is used by the base class (EditPrimary)
        """
        return RelLib.Note()

    def get_menu_title(self):
        if self.obj.get_handle():
            title = _('Note') + ': %s' % self.obj.get_gramps_id()
        else:
            title = _('New Note')
        return title

    def _local_init(self):
        """
        Local initialization function. Performs basic initialization,
        including setting up widgets and the glade interface. This is called
        by the base class of EditPrimary, and overridden here.
        """
        self.top = gtk.glade.XML(const.gladeFile, "edit_note", "gramps")
        win = self.top.get_widget("edit_note")
        self.set_window(win, None, self.get_menu_title())

        width = Config.get(Config.NOTE_WIDTH)
        height = Config.get(Config.NOTE_HEIGHT)
        self.window.set_default_size(width, height)

        self.build_interface()
        self.window.show_all()
        
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
          </toolbar>
        </ui>
        '''
        format_actions = [
            ('<i>i</i>','<Control>I',
             ('italic',_('Italic'),_('Italic'),gtk.STOCK_ITALIC)),
            ('<b>b</b>','<Control>B',
             ('bold',_('Bold'),_('Bold'),gtk.STOCK_BOLD)),
            ('<u>u</u>','<Control>U',
             ('underline',_('Underline'),_('Underline'),gtk.STOCK_UNDERLINE)),
        ]

        buffer = EditorBuffer()

        self.text = self.top.get_widget('text')
        self.text.set_editable(not self.dbstate.db.readonly)
        self.spellcheck = Spell.Spell(self.text)
        self.text.set_buffer(buffer)

        # create a formatting toolbar and pass the actions 
        # together with the related markup tag to the buffer
        if not self.dbstate.db.readonly:
            uimanager = gtk.UIManager()
            accelgroup = uimanager.get_accel_group()
            self.window.add_accel_group(accelgroup)

            action_group = gtk.ActionGroup('Format')
            for markup, accel, action_desc in format_actions:
                action = gtk.ToggleAction(*action_desc)
                action_group.add_action_with_accel(action, accel)
                # FIXME why are these needed?
                # Shouldn't uimanager do it automatically!?
                action.set_accel_group(accelgroup)
                action.connect_accelerator()
                #
                buffer.setup_action_from_xml(action, markup)
        
            uimanager.insert_action_group(action_group, 0)
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

        # connection to buffer signals must be after the initial values are set
        buffer.connect('changed', self.update_note)
        buffer.connect_after('apply-tag', self.update_note)
        buffer.connect_after('remove-tag', self.update_note)

    def update_note(self, buffer, *args):
        """Update the Note object with current value.
        
        This happens after each change in the text or the formatting.
        
        """
        if self.obj:
            start = buffer.get_start_iter()
            stop = buffer.get_end_iter()
            text = buffer.get_text(start, stop)
            self.obj.set(text)
        else:
            log.debug("NOTE OBJ DOES NOT EXIST")
        return False

    def flow_changed(self, active):
        if active:
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.text.set_wrap_mode(gtk.WRAP_WORD)

    def save(self, *obj):
        """
        Save the data.
        """
        trans = self.db.transaction_begin()
        if self.obj.get_handle():
            self.db.commit_note(self.obj,trans)
        else:
            self.db.add_note(self.obj,trans)
        self.db.transaction_commit(trans, _("Edit Note"))
        
        if self.callback:
            self.callback(self.obj)
        self.close()

    def _cleanup_on_exit(self):
        (width, height) = self.window.get_size()
        Config.set(Config.NOTE_WIDTH, width)
        Config.set(Config.NOTE_HEIGHT, height)
        Config.sync()
