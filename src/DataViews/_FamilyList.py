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

# $Id$

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayModels
import Bookmarks
import Errors
import Config
import const
from Filters.SideBar import FamilySidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gtk

column_names = [
    _('ID'),
    _('Father'),
    _('Mother'),
    _('Relationship'),
    _('Last Changed'),
    ]

#-------------------------------------------------------------------------
#
# FamilyListView
#
#-------------------------------------------------------------------------
class FamilyListView(PageView.ListView):

    ADD_MSG = _("Add a new family")
    EDIT_MSG = _("Edit the selected family")
    DEL_MSG = _("Delete the selected family")
    
    def __init__(self,dbstate,uistate):

        signal_map = {
            'family-add'     : self.family_add,
            'family-update'  : self.family_update,
            'family-delete'  : self.family_delete,
            'family-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(
            self, _('Family List'), dbstate, uistate,
            column_names, len(column_names), DisplayModels.FamilyModel,
            signal_map, dbstate.db.get_family_bookmarks(),
            Bookmarks.FamilyBookmarks, filter_class=FamilySidebarFilter)
        
        self.updating = False

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)

    def define_actions(self):
        # add the Forward action group to handle the Forward button

        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        _('_Column Editor'), callback=self.column_editor)

        self.add_action('FilterEdit', None, _('Family Filter Editor'),
                        callback=self.filter_editor,)

    def filter_toggle(self, client, cnxn_id, etnry, data):
        if Config.get(Config.FILTER):
            self.search_bar.hide()
            self.filter_pane.show()
            active = True
        else:
            self.search_bar.show()
            self.filter_pane.hide()
            active = False

    def filter_editor(self,obj):
        from FilterEditor import FilterEditor

        try:
            FilterEditor('Family',const.custom_filters,
                         self.dbstate,self.uistate)
        except Errors.WindowActiveError:
            pass            

    def add_bookmark(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))
        
    def get_bookmarks(self):
        return self.dbstate.db.get_family_bookmarks()

    def column_order(self):
        return self.dbstate.db.get_family_list_column_order()

    def column_editor(self,obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Family List Columns'),
            self.uistate,
            self.dbstate.db.get_family_list_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self,list):
        self.dbstate.db.set_family_list_column_order(list)
        self.build_columns()

    def get_stock(self):
        return 'gramps-family-list'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
            </menu>
           <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
           </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
          </popup>
        </ui>'''

    def add(self,obj):
        from Editors import EditFamily
        family = RelLib.Family()
        try:
            EditFamily(self.dbstate,self.uistate,[],family)
        except Errors.WindowActiveError:
            pass

    def family_add(self,handle_list):
        while not self.family_add_loop(handle_list):
            pass

    def family_update(self,handle_list):
        while not self.family_update_loop(handle_list):
            pass

    def family_delete(self,handle_list):
        while not self.family_delete_loop(handle_list):
            pass

    def family_add_loop(self,handle_list):
        if self.updating:
            return False
        self.updating = True
        self.row_add(handle_list)
        self.updating = False
        return True

    def family_update_loop(self,handle_list):
        if self.updating:
            return False
        self.updating = True
        self.row_update(handle_list)
        self.updating = False
        return True

    def family_delete_loop(self,handle_list):
        if self.updating:
            return False
        self.updating = True
        self.row_delete(handle_list)
        self.updating = False
        return True

    def remove(self,obj):
        import GrampsDb
        
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        for handle in mlist:
            GrampsDb.remove_family_relationships(self.dbstate.db, handle)
        self.build_tree()
    
    def edit(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            from Editors import EditFamily
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate,self.uistate,[],family)
            except Errors.WindowActiveError:
                pass
