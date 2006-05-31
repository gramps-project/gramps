#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

# $Id: _Report.py 6669 2006-05-15 15:53:42Z rshura $

import gtk
import Config
import PluginUtils

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
class TextFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = Config.get(Config.OUTPUT_PREFERENCE)
        index = 0
        PluginUtils.textdoc_list.sort()
        active_index = 0
        for item in PluginUtils.textdoc_list:
            if tables and item[2] == 0:
                continue
            name = item[0]
            self.store.append(row=[name])
            #if callback:
            #    menuitem.connect("activate",callback)
            if item[7] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return PluginUtils.textdoc_list[self.get_active()][0]

    def get_reference(self):
        return PluginUtils.textdoc_list[self.get_active()][1]

    def get_paper(self):
        return PluginUtils.textdoc_list[self.get_active()][3]

    def get_styles(self):
        return PluginUtils.textdoc_list[self.get_active()][4]

    def get_ext(self):
        return PluginUtils.textdoc_list[self.get_active()][5]

    def get_printable(self):
        return PluginUtils.textdoc_list[self.get_active()][6]

    def get_clname(self):
        return PluginUtils.textdoc_list[self.get_active()][7]
