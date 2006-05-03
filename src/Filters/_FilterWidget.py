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
from _GenericFilter import GenericFilter
from _FilterStore import FilterStore

#-------------------------------------------------------------------------
#
# FilterWidget
#
#-------------------------------------------------------------------------
class FilterWidget:
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

#        self.filter_text.set_sensitive(False)

        return self.filterbar
        
    def setup_filter( self, default_filters, namespace="generic"):
        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        filter_list = []
        
        for f in default_filters:
            all = GenericFilter()
            rule = f[0](f[1])
            #print rule
            all.set_name( rule.name)
            all.add_rule( rule)
            filter_list.append(all)

        self.filter_model = FilterStore(filter_list, namespace)
        self.filter_list.set_model(self.filter_model)
        self.filter_list.set_active(self.filter_model.default_index())
        self.filter_list.connect('changed',self.on_filter_name_changed)
#        self.filter_text.set_sensitive(False)
        self.DataFilter = filter_list[self.filter_model.default_index()]
        
    def apply_filter_clicked(self,ev=None):
        print "apply_filter_clicked"
        index = self.filter_list.get_active()
        self.DataFilter = self.filter_model.get_filter(index)
        if self.DataFilter.need_param:
            qual = unicode(self.filter_text.get_text())
            self.DataFilter.set_parameter(qual)
        self.apply_filter()
        if self.apply_done_callback:
            self.apply_done_callback()

    def on_filter_name_changed(self,obj):
        print "on_filter_name_changed"
        index = self.filter_list.get_active()
#        mime_filter = self.filter_model.get_filter(index)
#        qual = mime_filter.need_param
#        if qual:
#            self.filter_text.show()
#            self.filter_text.set_sensitive(True)
#        else:
#            self.filter_text.hide()
#            self.filter_text.set_sensitive(False)

    def apply_filter(self,current_model=None):
        self.uistate.status_text(_('Updating display...'))
        self.on_apply_callback()
        self.uistate.modify_statusbar()

    def get_filter( self):
        print "get_filter"
        #print self.DataFilter.flist[0]
        return self.DataFilter
        
    def show( self):
        self.filterbar.show()

    def hide( self):
        self.filterbar.hide()
