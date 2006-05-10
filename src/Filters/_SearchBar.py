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

# $Id: _FilterWidget.py 6521 2006-05-03 01:02:54Z rshura $

"""
Package providing filtering framework for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# FilterWidget
#
#-------------------------------------------------------------------------
class SearchBar:
    def __init__( self, uistate, on_apply, apply_done = None):
        self.on_apply_callback = on_apply
        self.apply_done_callback = apply_done
        self.uistate = uistate
        
    def build( self):
        self.filterbar = gtk.HBox()
        self.filterbar.set_spacing(4)
        self.filter_text = gtk.Entry()
        self.filter_list = gtk.ComboBox()
        self.filter_button = gtk.Button(stock=gtk.STOCK_FIND)
        self.filter_button.connect( 'clicked',self.apply_filter_clicked)
        self.filterbar.pack_start(self.filter_list,False)
        self.filterbar.pack_start(self.filter_text,True)
        self.filterbar.pack_end(self.filter_button,False)

        return self.filterbar
        
    def setup_filter( self, column_names ):
        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        self.filter_model = gtk.ListStore(str)
        
        for col in column_names:
            rule = _("Search %s") % col
            self.filter_model.append(row=[rule])
            
        self.filter_list.set_model(self.filter_model)
        self.filter_list.set_active(0)
        self.filter_list.connect('changed',self.on_filter_name_changed)
        
    def apply_filter_clicked(self, obj):
        print "apply_filter_clicked"
        print self.on_apply_callback
        self.on_apply_callback()

    def get_value(self):
        text = self.filter_text.get_text().strip()
        index = self.filter_list.get_active()
        return (index, text)
        
    def on_filter_name_changed(self,obj):
        pass

    def apply_filter(self,current_model=None):
        self.uistate.status_text(_('Updating display...'))
        self.on_apply_callback()
        self.uistate.modify_statusbar()

    def get_filter( self):
        print "get_filter"
        return None
        
    def show( self):
        self.filterbar.show()

    def hide( self):
        self.filterbar.hide()
