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
class TextTab(GrampsTab):

    def __init__(self, dbstate, uistate, track, obj, title=_('Text')):
        self.obj = obj
	self.original = obj.serialize()
        GrampsTab.__init__(self, dbstate, uistate, track, title)
        self.show_all()

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
        
        self.text_view = gtk.TextView()
        self.spellcheck = Spell.Spell(self.text_view)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.text_view)
        scroll.connect('focus-out-event', self.update)

        vbox.pack_start(scroll, True)
        vbox.set_spacing(6)
        vbox.set_border_width(6)
       
        self.pack_start(vbox, True)
        self.buf = self.text_view.get_buffer()
        if self.obj.get_text():
            self.empty = False
            self.buf.insert_at_cursor(self.obj.get_text())
        else:
            self.empty = True
            
        self.buf.connect('changed', self.update)
        self.rebuild()

    def update(self, obj):
        start = self.buf.get_start_iter()
        stop = self.buf.get_end_iter()
        text = unicode(self.buf.get_text(start, stop))
        self.obj.set_text(text)
        self._update_label(obj)
        return False

    def rebuild(self):
        self._set_label()

    def cancel(self):
	self.obj.unserialize(self.original)
