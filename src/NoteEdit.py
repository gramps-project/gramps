#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gc

import const
import Utils
import Spell

#-------------------------------------------------------------------------
#
# NoteEditor
#
#-------------------------------------------------------------------------
class NoteEditor:
    """Displays a simple text editor that allows a person to edit a note"""
    def __init__(self,data,parent,parent_window=None,callback=None,
                 readonly=False):

        self.parent = parent
        self.callback = callback
        if data:
            if self.parent.child_windows.has_key(data):
                self.parent.child_windows[data].present(None)
                return
            else:
                self.win_key = data
        else:
            self.win_key = self
        self.data = data
        self.parent_window = parent_window
        self.glade = gtk.glade.XML(const.gladeFile,"note_edit")
        self.readonly = readonly
        self.draw()

    def draw(self):
        """Displays the NoteEditor window"""

        self.top = self.glade.get_widget('note_edit')
        alt_title = self.glade.get_widget('title_msg')
        Utils.set_titles(self.top, alt_title, _('Note Editor'))

        if self.callback:
            self.title_entry = self.glade.get_widget('title')
            self.title_entry.set_text(self.data.get_description())
            self.title_entry.set_editable(not self.readonly)
        else:
            self.glade.get_widget('tbox').hide()

        self.entry = self.glade.get_widget('note')
        self.entry.get_buffer().set_text(self.data.get_note())
        self.entry.set_editable(not self.readonly)
        self.spellcheck = Spell.Spell(self.entry)

        cancel_button = self.glade.get_widget('cancel')
        ok_button = self.glade.get_widget('ok')
        ok_button.set_sensitive(not self.readonly)
        cancel_button.connect("clicked",self.close)
        ok_button.connect("clicked",self.on_save_note_clicked)
        self.top.connect("delete_event",self.on_delete_event)
        
        if self.parent_window:
            self.top.set_transient_for(self.parent_window)
        self.add_itself_to_menu()
        
    def on_delete_event(self,*obj):
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,*obj):
        self.remove_itself_from_menu()
        self.top.destroy()
        gc.collect()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Note'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,*obj):
        self.top.present()

    def on_save_note_clicked(self,obj):
        """Saves the note and closes the window"""
        tbuffer = self.entry.get_buffer()
        text = unicode(tbuffer.get_text(tbuffer.get_start_iter(),
                                        tbuffer.get_end_iter(),False))
        if text != self.data.get_note():
            self.data.set_note(text)
        if self.callback:
            self.data.set_description(self.title_entry.get_text())
            self.callback(self.data)
        self.close(obj)
