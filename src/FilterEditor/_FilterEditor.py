#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
from Filters import GenericFilterFactory, FilterList, \
     reload_custom_filters, reload_system_filters
from Filters.Rules._MatchesFilterBase import MatchesFilterBase
import ListModel
import ManagedWindow
from QuestionDialog import QuestionDialog

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class FilterEditor(ManagedWindow.ManagedWindow):
    def __init__(self, space, filterdb, dbstate, uistate):

        ManagedWindow.ManagedWindow.__init__(self, uistate, [],
                                             FilterEditor)
        self.dbstate = dbstate
        self.db = dbstate.db
        self.filterdb = FilterList(filterdb)
        self.filterdb.load()
        self.space = space

        self.define_glade('filter_list', const.rule_glade)
        self.filter_list = self.get_widget('filters')
        self.edit = self.get_widget('edit')
        self.clone = self.get_widget('clone')
        self.delete = self.get_widget('delete')
        self.test = self.get_widget('test')

        self.edit.set_sensitive(False)
        self.clone.set_sensitive(False)
        self.delete.set_sensitive(False)
        self.test.set_sensitive(False)

        self.set_window(self.get_widget('filter_list'),
                        self.get_widget('title'),
                        _('%s filters') % _(self.space))

        self.edit.connect('clicked', self.edit_filter)
        self.clone.connect('clicked', self.clone_filter)
        self.test.connect('clicked', self.test_clicked)
        self.delete.connect('clicked', self.delete_filter)

        self.connect_button('help', self.help_clicked)
        self.connect_button('close', self.close)
        self.connect_button('add', self.add_new_filter)
        
        self.uistate.connect('filter-name-changed',self.clean_after_rename)

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
            self.clone.set_sensitive(True)
            self.delete.set_sensitive(True)
            self.test.set_sensitive(True)
        else:
            self.edit.set_sensitive(False)
            self.clone.set_sensitive(False)
            self.delete.set_sensitive(False)
            self.test.set_sensitive(False)
    
    def close(self,*obj):
        self.filterdb.save()
        reload_custom_filters()
        reload_system_filters()
        self.uistate.emit('filters-changed',(self.space,))
        ManagedWindow.ManagedWindow.close(self,*obj)
        
    def draw_filters(self):
        self.clist.clear()
        for f in self.filterdb.get_filters(self.space):
            self.clist.add([f.get_name(),f.get_comment()],f)

    def add_new_filter(self,obj):
        from _EditFilter import EditFilter

        the_filter = GenericFilterFactory(self.space)()
        EditFilter(self.space, self.dbstate, self.uistate, self.track,
                   the_filter, self.filterdb, self.draw_filters)

    def edit_filter(self,obj):
        store,node = self.clist.get_selected()
        if node:
            from _EditFilter import EditFilter
            
            gfilter = self.clist.get_object(node)
            EditFilter(self.space, self.dbstate, self.uistate, self.track,
                       gfilter, self.filterdb, self.draw_filters)

    def clone_filter(self,obj):
        store,node = self.clist.get_selected()
        if node:
            from _EditFilter import EditFilter
            
            old_filter = self.clist.get_object(node)
            the_filter = GenericFilterFactory(self.space)(old_filter)
            the_filter.set_name('')
            EditFilter(self.space, self.dbstate, self.uistate, self.track,
                       the_filter, self.filterdb, self.draw_filters)

    def test_clicked(self,obj):
        store,node = self.clist.get_selected()
        if node:
            from _ShowResults import ShowResults
            
            filt = self.clist.get_object(node)
            handle_list = filt.apply(self.db,self.get_all_handles())
            ShowResults(self.db, self.uistate, self.track, handle_list,
                        filt.get_name(),self.space)

    def delete_filter(self,obj):
        store,node = self.clist.get_selected()
        if node:
            gfilter = self.clist.get_object(node)
            name = gfilter.get_name()
            if self.check_recursive_filters(self.space,name):
                QuestionDialog( _('Delete Filter?'),
                                _('This filter is currently being used '
                                  'as the base for other filters. Deleting'
                                  'this filter will result in removing all '
                                  'other filters that depend on it.'),
                                _('Delete Filter'),
                                self._do_delete_selected_filter,
                                self.window)
            else:
                self._do_delete_selected_filter()

    def _do_delete_selected_filter(self):
        store,node = self.clist.get_selected()
        if node:
            gfilter = self.clist.get_object(node)
            self._do_delete_filter(self.space,gfilter)
            self.draw_filters()

    def _do_delete_filter(self,space,gfilter):
        """
        This method recursively calls itself to delete all dependent filters
        before removing this filter. Otherwise when A is 'matches B'
        and C is 'matches D' the removal of A leads to two broken filter
        being left behind.
        """
        filters = self.filterdb.get_filters(space)
        name = gfilter.get_name()
        for the_filter in filters:
            for rule in the_filter.get_rules():
                values = rule.values()
                if issubclass(rule.__class__,MatchesFilterBase) \
                       and (name in values):
                    self._do_delete_filter(space,the_filter)
        filters.remove(gfilter)

    def get_all_handles(self):
        if self.space == 'Person':
            return self.db.get_person_handles(sort_handles=False)
        elif self.space == 'Family':
            return self.db.get_family_handles()
        elif self.space == 'Event':
            return self.db.get_event_handles()
        elif self.space == 'Source':
            return self.db.get_source_handles()
        elif self.space == 'Place':
            return self.db.get_place_handles()
        elif self.space == 'MediaObject':
            return self.db.get_media_object_handles()
        elif self.space == 'Repository':
            return self.db.get_repository_handles()
        elif self.space == 'Note':
            return self.db.get_note_handles()

    def clean_after_rename(self,space,old_name,new_name):
        if old_name == "":
            return

        if old_name == new_name:
            return

        for the_filter in self.filterdb.get_filters(space):
            for rule in the_filter.get_rules():
                values = rule.values()
                if issubclass(rule.__class__,MatchesFilterBase) \
                       and (old_name in values):
                    ind = values.index(old_name)
                    values[ind] = new_name

    def check_recursive_filters(self,space,name):
        for the_filter in self.filterdb.get_filters(space):
            for rule in the_filter.get_rules():
                values = rule.values()
                if issubclass(rule.__class__,MatchesFilterBase) \
                       and (name in values):
                    return True
        return False
