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
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from RelLib import *

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class NoteEditor:

    def __init__(self,data):

        self.editnote = libglade.GladeXML(const.editnoteFile,"editnote")
        self.textobj = self.editnote.get_widget("notetext")
        self.en_obj = self.editnote.get_widget("editnote")
        self.data = data
        self.en_obj.editable_enters(self.textobj);

        self.textobj.set_point(0)
        self.textobj.insert_defaults(self.data.getNote())
        self.textobj.set_word_wrap(1)
        
        self.editnote.signal_autoconnect({
            "on_save_note_clicked"  : self.on_save_note_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

    def on_save_note_clicked(self,obj):
        text = self.textobj.get_chars(0,-1)
        if text != self.data.getNote():
            self.data.setNote(text)
            Utils.modified()
        Utils.destroy_passed_object(obj)
