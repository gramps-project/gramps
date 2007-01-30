#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

from gettext import gettext as _
import gtk
import GrampsWidgets

_RETURN = gtk.gdk.keyval_from_name("Return")
_KP_ENTER = gtk.gdk.keyval_from_name("KP_Enter")

class SidebarFilter:

    def __init__(self,uistate):
        self.position = 1
        self.table = gtk.Table(3,11)
        self.table.set_border_width(6)
        self.table.set_row_spacings(6)
        self.table.set_col_spacing(0,6)
        self.table.set_col_spacing(1,6)
        self.tooltips = gtk.Tooltips()
        self._init_interface()
        uistate.connect('filters-changed',self.on_filters_changed)
        self.uistate = uistate

    def _init_interface(self):
        self.table.attach(GrampsWidgets.MarkupLabel(_('<b>Filter</b>')),
                          0, 3, 0, 1, xoptions=gtk.FILL, yoptions=0)

        self.create_widget()

        self.apply_btn = gtk.Button(stock=gtk.STOCK_FIND)
        self.apply_btn.connect('clicked', self.clicked)

        hbox = gtk.HBox()
        hbox.show()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_BUTTON)
        image.show()
        label = gtk.Label(_('Reset'))
        label.show()
        hbox.pack_start(image,False,False)
        hbox.pack_start(label,False,True)
        hbox.set_spacing(4)
        
        self.clear_btn = gtk.Button()
        self.clear_btn.add(hbox)
        self.clear_btn.connect('clicked', self.clear)

        hbox = gtk.HBox()
        hbox.set_spacing(6)
        hbox.add(self.apply_btn)
        hbox.add(self.clear_btn)
        hbox.show()
        self.table.attach(hbox, 2, 3, self.position, self.position+1,
                          xoptions=gtk.FILL, yoptions=0)

    def get_widget(self):
        return self.table

    def create_widget(self):
        pass

    def clear(self, obj):
        pass

    def clicked(self, obj):
        self.uistate.set_busy_cursor(1)
        self.clicked_func()
        self.uistate.set_busy_cursor(0)

    def clicked_func(self):
        pass

    def get_filter(self):
        pass

    def add_text_entry(self, name, widget, tooltip=None):
        self.add_entry(name, widget)
        widget.connect('key-press-event',self.key_press)
        if tooltip:
            self.tooltips.set_tip(widget, tooltip)

    def key_press(self, obj, event):
        if not event.state or event.state in (gtk.gdk.MOD2_MASK,):
            if event.keyval in (_RETURN, _KP_ENTER):
                self.clicked(obj)
        return False

    def add_entry(self, name, widget):
        if name:
            self.table.attach(GrampsWidgets.BasicLabel(name),
                              1, 2, self.position, self.position+1,
                              xoptions=gtk.FILL, yoptions=0)
        self.table.attach(widget, 2, 3, self.position, self.position+1,
                          xoptions=gtk.FILL, yoptions=0)
        self.position += 1

    def on_filters_changed(self,namespace):
        pass

