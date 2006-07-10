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

"""
Custom Filter Editor tool.
"""

__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".FilterEdit")

#-------------------------------------------------------------------------
#
# GTK/GNOME 
#
#-------------------------------------------------------------------------
import GrampsDisplay

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
from Filters import GenericFilter, FilterList, \
     reload_custom_filters, reload_system_filters
import ListModel
import ManagedWindow

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class FilterEditor(ManagedWindow.ManagedWindow):
    def __init__(self, space, filterdb, dbstate, uistate, ftype=GenericFilter):

        ManagedWindow.ManagedWindow.__init__(self, uistate, [],
                                             FilterEditor)
        self.ftype = ftype
        self.dbstate = dbstate
        self.db = dbstate.db
        self.filterdb = FilterList(filterdb)
        self.filterdb.load()
        self.space = space

        self.define_glade('filter_list', const.rule_glade)
        self.filter_list = self.get_widget('filters')
        self.edit = self.get_widget('edit')
        self.delete = self.get_widget('delete')
        self.test = self.get_widget('test')

        self.edit.set_sensitive(False)
        self.delete.set_sensitive(False)
        self.test.set_sensitive(False)

        self.set_window(self.get_widget('filter_list'),
                        self.get_widget('title'),
                        _('%s filters') % _(self.space))

        self.edit.connect('clicked', self.edit_filter)
        self.test.connect('clicked', self.test_clicked)
        self.delete.connect('clicked', self.delete_filter)

        self.connect_button('help', self.help_clicked)
        self.connect_button('close', self.close_window)
        self.connect_button('add', self.add_new_filter)
        
        self.clist = ListModel.ListModel(
            self.filter_list,
            [(_('Filter'),0,150),(_('Comment'),1,150)],
            self.filter_select_row,
            self.edit_filter)
        self.draw_filters()
        self.show()

    def build_menu_names(self, obj):
        return (_("Custom Filter Editor"), _("Custom Filter Editor"))
        
    def help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-cfe')

    def filter_select_row(self,obj):
        store,node = self.clist.get_selected()
        if node:
            self.edit.set_sensitive(True)
            self.delete.set_sensitive(True)
            self.test.set_sensitive(True)
        else:
            self.edit.set_sensitive(False)
            self.delete.set_sensitive(False)
            self.test.set_sensitive(False)
    
    def close_window(self,obj):
        self.filterdb.save()
        reload_custom_filters()
        reload_system_filters()
        self.close()
        
    def draw_filters(self):
        self.clist.clear()
        for f in self.filterdb.get_filters(self.space):
            self.clist.add([f.get_name(),f.get_comment()],f)

    def add_new_filter(self,obj):
        from _EditFilter import EditFilter

        the_filter = self.ftype()
        EditFilter(self.space, self.dbstate, self.uistate, self.track,
                   the_filter, self.filterdb, self.draw_filters)

    def edit_filter(self,obj):
        store,node = self.clist.get_selected()
        if node:
            from _EditFilter import EditFilter
            
            gfilter = self.clist.get_object(node)
            EditFilter(self.space, self.dbstate, self.uistate, self.track,
                       gfilter, self.filterdb, self.draw_filters)

    def test_clicked(self,obj):
        store,node = self.clist.get_selected()
        if node:
            from _ShowResults import ShowResults
            
            filt = self.clist.get_object(node)
            handle_list = filt.apply(
                self.db, self.db.get_person_handles(sort_handles=False))
            ShowResults(self.db, self.uistate, self.track, handle_list,
                        filt.get_name())

    def delete_filter(self,obj):
        store,node = self.clist.get_selected()
        if node:
            gfilter = self.clist.get_object(node)
            self.filterdb.get_filters(self.space).remove(gfilter)
            self.draw_filters()

