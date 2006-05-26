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
import Spell
from _GrampsTab import GrampsTab

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class NoteTab(GrampsTab):

    def __init__(self, dbstate, uistate, track, note_obj, title=_('Note')):
        self.note_obj = note_obj        
        GrampsTab.__init__(self, dbstate, uistate, track, title)
        self.show_all()

    def get_icon_name(self):
        return 'gramps-notes'

    def _update_label(self, *obj):
        cc = self.buf.get_char_count()
        if cc == 0 and not self.empty:
            self.empty = True
            self._set_label()
        elif cc != 0 and self.empty:
            self.empty = False
            self._set_label()

    def is_empty(self):
        """
        Indicates if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        return self.buf.get_char_count() == 0

    def build_interface(self):
        vbox = gtk.VBox()
        
        self.text = gtk.TextView()
        self.flowed = gtk.RadioButton(None, _('Flowed'))
        self.format = gtk.RadioButton(self.flowed, _('Formatted'))

        if self.note_obj and self.note_obj.get_format():
            self.format.set_active(True)
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.flowed.set_active(True)
            self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.spellcheck = Spell.Spell(self.text)

        self.flowed.connect('toggled', self.flow_changed)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.text)
        scroll.connect('focus-out-event', self.update)

        vbox.pack_start(scroll, True)
        vbox.set_spacing(6)
        vbox.set_border_width(6)

        hbox = gtk.HBox()
        hbox.set_spacing(12)
        hbox.set_border_width(6)
        hbox.pack_start(self.flowed, False)
        hbox.pack_start(self.format, False)

        vbox.pack_start(hbox, False)
        
        self.pack_start(vbox, True)
        self.buf = self.text.get_buffer()
        if self.note_obj:
            self.empty = False
            self.buf.insert_at_cursor(self.note_obj.get())
        else:
            self.empty = True
            
        self.buf.connect('changed', self.update)
        self.rebuild()

    def update(self, obj):
        if self.note_obj:
            start = self.buf.get_start_iter()
            stop = self.buf.get_end_iter()
            text = self.buf.get_text(start, stop)
            self.note_obj.set(text)
        else:
            print "NOTE OBJ DOES NOT EXIST"
        self._update_label(obj)
        return False

    def flow_changed(self, obj):
        if obj.get_active():
            self.text.set_wrap_mode(gtk.WRAP_WORD)
            self.note_obj.set_format(0)
        else:
            self.text.set_wrap_mode(gtk.WRAP_NONE)
            self.note_obj.set_format(1)

    def rebuild(self):
        self._set_label()
