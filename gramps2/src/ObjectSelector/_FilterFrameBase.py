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

import gtk
import gobject

from GrampsWidgets import IntEdit
from Filters import GenericFilter

class FilterFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        'apply-filter': (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,)),
        'clear-filter': (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         ())
        }

    __default_border_width = 5

    def __init__(self,filter_spec=None,label="Filter"):
	gtk.Frame.__init__(self,label)
                
        self._filter_spec = filter_spec    

	align = gtk.Alignment()

        # table layout
        
        self._table = gtk.Table(3,6,False)
        self._table.set_row_spacings(5)
        self._table.set_col_spacings(5)

        self._label_col = 0
        self._check_col = 1
        self._control_col = 2
        

        # Apply / Clear

        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        apply_button.connect('clicked',self.on_apply)
        clear_button = gtk.Button(stock=gtk.STOCK_CLEAR)
        clear_button.connect('clicked',self.on_clear)

        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        button_box.pack_start(apply_button,False,False)
        button_box.pack_start(clear_button,False,False)
        

        # Outer box

        outer_box = gtk.VBox()
        outer_box.pack_start(self._table,True,True)
        outer_box.pack_start(button_box,False,False)
        outer_box.set_border_width(self.__class__.__default_border_width/2)
        outer_box.set_spacing(self.__class__.__default_border_width/2)
        
	align.add(outer_box)
        align.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width)
                          

	self.add(align)


    def on_apply(self,button):
        """Build a GenericFilter object from the settings in the filter controls and
        emit a 'apply-filter' signal with the GenericFilter object as the parameter."""
        
        raise NotImplementedError("subclass of FilterFrameBase must implement on_apply")

    def on_clear(self,button):
        """Clear all the filter widgets and  emit a 'clear-filter' signal."""
        
        raise NotImplementedError("subclass of FilterFrameBase must implement on_apply")
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FilterFrameBase)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonFilterFrame()
    w.add(f)
    w.show_all()

    gtk.main()
