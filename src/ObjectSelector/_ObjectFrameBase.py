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

#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

class ObjectFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {}

    __default_border_width = 5

    def __init__(self,
                 dbstate,
                 uistate,
                 filter_frame,
                 preview_frame,
                 tree_frame):
        
        gtk.Frame.__init__(self)

        self._dbstate = dbstate
        self._uistate = uistate
        self._filter_frame = filter_frame
        self._preview_frame = preview_frame
        self._tree_frame = tree_frame

        self._preview_frame.set_sensitive(False)
        
        # Create the widgets for each of the object types

        vbox = gtk.VBox()
        vbox.show()

        vbox2 = gtk.VBox()
        vbox2.show()
        
        pane = gtk.HPaned()
        pane.show()
        
        vbox.pack_start(self._preview_frame,True,True)
        vbox.pack_start(self._filter_frame,True,True)
        vbox2.pack_start(self._tree_frame,True,True)

        pane.pack1(vbox2,True,False)
        pane.pack2(vbox,False,True)

        pane_align = gtk.Alignment()
        pane_align.add(pane)
        pane_align.set_padding(self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width)
        pane_align.set(0.5,0.5,1,1)
        pane_align.show()
        
        self.add(pane_align)

        
    def set_preview(self,treeselection):
        (model, iter) = treeselection.get_selected()
        if iter:
            (obj,rowref) = model.get_value(iter,0)
            if len(rowref) > 1 or model.is_list():
                if obj:
                    self._preview_frame.set_sensitive(True)
                    self._preview_frame.set_object(obj)
                else:
                    self._preview_frame.set_sensitive(False)
                    self._preview_frame.clear_object()
            else:
                self._preview_frame.set_sensitive(False)
                self._preview_frame.clear_object()
        else:
            self._preview_frame.set_sensitive(False)
            self._preview_frame.clear_object()


    def get_selection(self):
        return self._tree_frame.get_selection()
    
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(ObjectFrameBase)

if __name__ == "__main__":
    pass
