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

# $Id:$

"""
Package providing filtering framework for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK
#
#-------------------------------------------------------------------------
import gtk
from gettext import gettext as _

_RETURN = gtk.gdk.keyval_from_name("Return")

#-------------------------------------------------------------------------
#
# SearchBar
#
#-------------------------------------------------------------------------
class SearchBar:
    def __init__( self, uistate, on_apply, apply_done = None):
        self.on_apply_callback = on_apply
        self.apply_done_callback = apply_done
        self.uistate = uistate
        self.apply_text = ''
        
    def build( self):
        self.filterbar = gtk.HBox()
        self.filterbar.set_spacing(4)
        self.filter_list = gtk.ComboBox()
        self.filter_list.connect('changed', self.filter_changed)

        self.filter_text = gtk.Entry()
        self.filter_text.connect('key-press-event',self.key_press)
        self.filter_text.connect('changed',self.text_changed)

        self.filter_button = gtk.Button(stock=gtk.STOCK_FIND)
        self.filter_button.connect( 'clicked',self.apply_filter_clicked)
        self.filter_button.set_sensitive(False)

        self.clear_button = gtk.Button(stock=gtk.STOCK_CLEAR)
        self.clear_button.connect( 'clicked',self.apply_clear)
        self.clear_button.set_sensitive(False)

        self.filterbar.pack_start(self.filter_list,False)
        self.filterbar.pack_start(self.filter_text,True)
        self.filterbar.pack_end(self.clear_button,False)
        self.filterbar.pack_end(self.filter_button,False)

        return self.filterbar
        
    def setup_filter( self, column_data ):
        old_value = self.filter_list.get_active()
        
        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        self.filter_model = gtk.ListStore(str, int, bool)

        maxval = 0
        for col,index in column_data:
            rule = _("%s contains") % col
            self.filter_model.append(row=[rule,index,False])
            maxval += 1
            rule = _("%s does not contain") % col
            self.filter_model.append(row=[rule,index,True])
            maxval += 1
            
        self.filter_list.set_model(self.filter_model)
        if old_value == -1 or old_value >= maxval:
            self.filter_list.set_active(0)
        else:
            self.filter_list.set_active(old_value)

    def filter_changed(self, obj):
        self.filter_button.set_sensitive(True)
        self.clear_button.set_sensitive(True)

    def text_changed(self, obj):
        text = obj.get_text()
        if self.apply_text == '' and text == '':
            self.filter_button.set_sensitive(False)
            self.clear_button.set_sensitive(False)
        elif self.apply_text == text:
            self.filter_button.set_sensitive(False)
            self.clear_button.set_sensitive(True)
        else:
            self.filter_button.set_sensitive(True)
            self.clear_button.set_sensitive(True)

    def key_press(self, obj, event):
        if event.keyval == _RETURN and not event.state:
            self.filter_button.set_sensitive(False)
            self.clear_button.set_sensitive(True)
            self.apply_filter()
        return False
        
    def apply_filter_clicked(self, obj):
        self.apply_filter()

    def apply_clear(self, obj):
        self.filter_text.set_text('')
        self.apply_filter()

    def get_value(self):
        text = unicode(self.filter_text.get_text()).strip()
        node = self.filter_list.get_active_iter()
        index = self.filter_model.get_value(node,1)
        inv = self.filter_model.get_value(node,2)
        return (index, text, inv)
        
    def apply_filter(self,current_model=None):
        self.apply_text = unicode(self.filter_text.get_text())
        self.filter_button.set_sensitive(False)
        self.uistate.status_text(_('Updating display...'))
        self.on_apply_callback()
        self.uistate.modify_statusbar()

    def show(self):
        self.filterbar.show()

    def hide(self):
        self.filterbar.hide()
