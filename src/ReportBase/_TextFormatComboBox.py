#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

# $Id:_TextFormatComboBox.py 9912 2008-01-22 09:17:46Z acraphae $

import gtk
import gobject
import Config
import gen

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
class TextFormatComboBox(gtk.ComboBox):

    def __init__(self):
        pmgr = gen.plug.PluginManager.get_instance()
        self.__text_doc_list = pmgr.get_text_doc_list()
        self.__text_doc_list.sort()
        gtk.ComboBox.__init__(self)

    def set(self, callback, obj=None, active=None):
        self.store = gtk.ListStore(gobject.TYPE_STRING)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        out_pref = Config.get(Config.OUTPUT_PREFERENCE)
        index = 0
        active_index = 0
        for item in self.__text_doc_list:
            name = item[0]
            self.store.append(row=[name])
            if item[5] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return self.__text_doc_list[self.get_active()][0]

    def get_reference(self):
        return self.__text_doc_list[self.get_active()][1]

    def get_paper(self):
        return self.__text_doc_list[self.get_active()][2]

    def get_styles(self):
        return self.__text_doc_list[self.get_active()][3]

    def get_ext(self):
        return self.__text_doc_list[self.get_active()][4]

    def is_file_output(self):
        return len(self.get_ext()) > 0

    def get_clname(self):
        return self.__text_doc_list[self.get_active()][5]
