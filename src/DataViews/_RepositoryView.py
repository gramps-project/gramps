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

"""
Repository View
"""

__author__ = "Don Allingham"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayModels
import Utils
import Bookmarks
import Errors
import const
import Config
from Editors import EditRepository, DelRepositoryQuery
from DdTargets import DdTargets

from QuestionDialog import QuestionDialog
from Filters.SideBar import RepoSidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Name'),
    _('ID'),
    _('Type'),
    _('Home URL'),
    _('Street'),
    _('ZIP/Postal Code'),
    _('City'),
    _('County'),
    _('State'),
    _('Country'),
    _('Email'),
    _('Search URL'),
    ]

#-------------------------------------------------------------------------
#
# RepositoryView
#
#-------------------------------------------------------------------------
class RepositoryView(PageView.ListView):
    
    ADD_MSG = _("Add a new repository")
    EDIT_MSG = _("Edit the selected repository")
    DEL_MSG = _("Delete the selected repository")
    FILTER_TYPE = "Repository"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'repository-add'     : self.row_add,
            'repository-update'  : self.row_update,
            'repository-delete'  : self.row_delete,
            'repository-rebuild' : self.build_tree,
            }
        
        PageView.ListView.__init__(
            self, _('Repositories'), dbstate, uistate,
            column_names, len(column_names),
            DisplayModels.RepositoryModel, signal_map,
            dbstate.db.get_repo_bookmarks(),
            Bookmarks.RepoBookmarks,filter_class=RepoSidebarFilter)

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)

    def get_bookmarks(self):
        return self.dbstate.db.get_repo_bookmarks()

    def drag_info(self):
        return DdTargets.REPO_LINK

    def define_actions(self):
        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        _('_Column Editor'), callback=self.column_editor)
        self.add_action('FilterEdit', None, _('Repository Filter Editor'),
                        callback=self.filter_editor,)

    def column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Repository Columns'),
            self.uistate,
            self.dbstate.db.get_repository_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self, clist):
        self.dbstate.db.set_repository_column_order(clist)
        self.build_columns()

    def column_order(self):
        return self.dbstate.db.get_repository_column_order()

    def get_stock(self):
        return 'gramps-repository'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
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

    def on_double_click(self, obj, event):
        handle = self.first_selected()
        repos = self.dbstate.db.get_repository_from_handle(handle)
        try:
            EditRepository(self.dbstate, self.uistate, [], repos)
        except Errors.WindowActiveError:
            pass

    def add(self, obj):
        EditRepository(self.dbstate, self.uistate, [], RelLib.Repository())

    def remove(self, obj):
        db = self.dbstate.db
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        for repos_handle in mlist:

            source_list = [ src_handle for src_handle \
                            in db.get_source_handles() \
                            if db.get_source_from_handle(src_handle).has_repo_reference(repos_handle)]

            repository = db.get_repository_from_handle(repos_handle)

            ans = DelRepositoryQuery(repository, db, source_list)

            if len(source_list) > 0:
                msg = _('This repository is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'sources that reference it.')
            else:
                msg = _('Deleting repository will remove it from the database.')
            
            msg = "%s %s" % (msg, Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % repository.get_name(), msg,
                           _('_Delete Repository'), ans.query_response)
            

    def edit(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        for handle in mlist:
            repos = self.dbstate.db.get_repository_from_handle(handle)
            try:
                EditRepository(self.dbstate, self.uistate, [], repos)
            except Errors.WindowActiveError:
                pass

