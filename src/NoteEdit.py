#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# NoteEditor
#
#-------------------------------------------------------------------------
class NoteEditor:
    """Displays a simple text editor that allows a person to edit a note"""
    def __init__(self,data,parent_window=None):

        self.data = data
        self.parent_window = parent_window
        self.draw()

    def draw(self):
        """Displays the NoteEditor window"""
        title = "%s - GRAMPS" % _("Edit Note")

        self.top = gtk.Dialog(title)
        self.top.set_default_size(450,300)
        
        vbox = gtk.VBox()
        self.top.vbox.pack_start(vbox,gtk.TRUE,gtk.TRUE,0)
	label = gtk.Label('<span weight="bold" size="larger">%s</span>' % _('Edit Note'))
	label.set_use_markup(gtk.TRUE)
        vbox.pack_start(label, gtk.FALSE, gtk.FALSE, 10)

        self.entry = gtk.TextView()
        self.entry.set_editable(gtk.TRUE)
        self.entry.show()
        
        scroll = gtk.ScrolledWindow()
        scroll.add(self.entry)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.show()
        vbox.pack_start(scroll, gtk.TRUE, gtk.TRUE, 0)

        self.entry.get_buffer().set_text(self.data.get_note())

        self.top.add_button(gtk.STOCK_CANCEL,1)
        self.top.add_button(gtk.STOCK_OK,0)
        self.top.show_all()
        
        if self.parent_window:
            self.top.set_transient_for(self.parent_window)
        if self.top.run() == 0:
            self.on_save_note_clicked()
        self.top.destroy()
        
    def on_save_note_clicked(self):
        """Saves the note and closes the window"""
        buffer = self.entry.get_buffer()
        text = unicode(buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE))
        if text != self.data.get_note():
            self.data.set_note(text)
            Utils.modified()
