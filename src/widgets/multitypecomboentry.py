#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"The MultiTypeComboEntry widget class."

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.multitypecomboentry")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# MultiTypeComboEntry class
#
#-------------------------------------------------------------------------
class MultiTypeComboEntry(gtk.ComboBox, gtk.CellLayout):
    """A ComboBoxEntry widget with validation.
    
    MultiTypeComboEntry may have data type other then string (tbd.).
    
    Its behaviour is different from gtk.ComboBoxEntry in the way how
    the entry part of the widget is handled. While gtk.ComboBoxEntry
    emits the 'changed' signal immediatelly the text in the entry is 
    changed, MultiTypeComboEntry emits the signal only after the text is
    activated (enter is pressed, the focus is moved out) and validated.
    
    Validation function is an optional feature and activated only if a
    validator function is given at instantiation.
    
    The entry can be set as editable or not editable using the
    L{set_entry_editable} method.
    
    """
    __gtype_name__ = "MultiTypeComboEntry"
    
    def __init__(self, model=None, column=-1, validator=None):
        gtk.ComboBox.__init__(self, model)

        self._entry = gtk.Entry()
        # <hack description="set the GTK_ENTRY (self._entry)->is_cell_renderer
        # flag to TRUE in order to tell the entry to fill its allocation.">
        dummy_event = gtk.gdk.Event(gtk.gdk.NOTHING)
        self._entry.start_editing(dummy_event)
        # </hack>
        self.add(self._entry)
        self._entry.show()
        
        self._text_renderer = gtk.CellRendererText()
        self.pack_start(self._text_renderer, False)
        
        self._text_column = -1
        self.set_text_column(column)
        self._active_text = ''
        self.set_active(-1)
        
        self._validator = validator
        
        self._entry.connect('activate', self._on_entry_activate)
        self._entry.connect('focus-in-event', self._on_entry_focus_in_event)
        self._entry.connect('focus-out-event', self._on_entry_focus_out_event)
        self._entry.connect('key-press-event', self._on_entry_key_press_event)
        self.changed_cb_id = self.connect('changed', self._on_changed)
        
        self._has_frame_changed()
        self.connect('notify', self._on_notify)

    # Virtual overriden methods
    
    def do_mnemonic_activate(self, group_cycling):
        self._entry.grab_focus()
        return True
    
    def do_grab_focus(self):
        self._entry.grab_focus()
        
    # Signal handlers
    
    def _on_entry_activate(self, entry):
        """Signal handler.
        
        Called when the entry is activated.
        
        """
        self._entry_changed(entry)
    
    def _on_entry_focus_in_event(self, widget, event):
        """Signal handler.
        
        Called when the focus enters the entry, and is used for saving
        the entry's text for later comparison.
        
        """
        self._text_on_focus_in = self._entry.get_text()
        
    def _on_entry_focus_out_event(self, widget, event):
        """Signal handler.
        
        Called when the focus leaves the entry.
        
        """
        if (self._entry.get_text() != self._text_on_focus_in):
            self._entry_changed(widget)
    
    def _on_entry_key_press_event(self, entry, event):
        """Signal handler.
        
        Its purpose is to handle escape button.
        
        """
        # FIXME Escape never reaches here, the dialog eats it, I assume.
        if event.keyval == gtk.keysyms.Escape:
            entry.set_text(self._active_text)

        return False

    def _on_changed(self, combobox):
        """Signal handler.
        
        Called when the active row is changed in the combo box.
        
        """
        iter = self.get_active_iter()
        if iter:
            model = self.get_model()
            self._active_text = model.get_value(iter, self._text_column)
            self._entry.set_text(self._active_text)

    def _on_notify(self, object, gparamspec):
        """Signal handler.
        
        Called whenever a property of the object is changed.
        
        """
        if gparamspec.name == 'has-frame':
            self._has_frame_changed()
    
    # Private methods
    
    def _entry_changed(self, entry):
        new_text = entry.get_text()
        
        if (self._validator is not None) and not self._validator(new_text):
            entry.set_text(self._active_text)
            return
        
        self._active_text = new_text
        self.handler_block(self.changed_cb_id)
        self.set_active(-1)
        self.handler_unblock(self.changed_cb_id)

    def _has_frame_changed(self):
        has_frame = self.get_property('has-frame')
        self._entry.set_has_frame(has_frame)

    # Public methods
    
    def set_text_column(self, text_column):
        if text_column < 0:
            return
        
        if text_column > self.get_model().get_n_columns():
            return
        
        if self._text_column == -1:
            self._text_column = text_column
            self.set_attributes(self._text_renderer, text=text_column)
        
    def get_text_column(self):
        return self._text_column
    
    def set_active_text(self, text):
        if self._entry:
            self._entry.set_text(text)
            self._entry_changed(self._entry)

    def get_active_text(self):
        if self._entry:
            return self._entry.get_text()
        
        return None

    def set_entry_editable(self, is_editable):
        self._entry.set_editable(is_editable)
