#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gnome.ui import *
from gtk import *
import GTK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# NoteEditor
#
#-------------------------------------------------------------------------
class NoteEditor:
    """Displays a simple text editor that allows a person to edit a note"""
    def __init__(self,data):

        self.data = data
        self.draw()
        self.entry.set_point(0)
        self.entry.insert_defaults(self.data.getNote())
        self.entry.set_word_wrap(1)

    def draw(self):
        """Displays the NoteEditor window"""
        title = "%s - GRAMPS" % _("Edit Note")

        self.top = GnomeDialog(title,STOCK_BUTTON_OK,STOCK_BUTTON_CANCEL)
        self.top.set_policy(FALSE,TRUE,FALSE)

        vbox = GtkVBox()
        self.top.vbox.pack_start(vbox,TRUE,TRUE,0)
        vbox.pack_start(GtkLabel(_("Edit Note")), FALSE, FALSE, 10)

        vbox.pack_start(GtkHSeparator(), FALSE, TRUE, 5)
        self.entry = GtkText()
        self.entry.set_editable(TRUE)
        self.entry.show()
        scroll = GtkScrolledWindow()
        scroll.add(self.entry)
        scroll.set_policy (GTK.POLICY_NEVER, GTK.POLICY_ALWAYS)
        scroll.set_usize(450, 300)
        scroll.show()
        vbox.pack_start(scroll, TRUE, TRUE, 0)

        self.top.button_connect(0,self.on_save_note_clicked)
        self.top.button_connect(1,self.cancel)
        self.top.show_all()
        self.entry.grab_focus()

    def cancel(self,obj):
        """Closes the window without saving the note"""
        self.top.destroy()
        
    def on_save_note_clicked(self,obj):
        """Saves the note and closes the window"""
        text = self.entry.get_chars(0,-1)
        if text != self.data.getNote():
            self.data.setNote(text)
            Utils.modified()
        self.top.destroy()

