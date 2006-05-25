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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayModels
import const
import Utils
import Bookmarks
import Errors
from DdTargets import DdTargets
from Editors import EditSource, DelSrcQuery
from QuestionDialog import QuestionDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Title'),
    _('ID'),
    _('Author'),
    _('Abbreviation'),
    _('Publication Information'),
    _('Last Changed'),
    ]

#-------------------------------------------------------------------------
#
# SourceView
#
#-------------------------------------------------------------------------
class SourceView(PageView.ListView):

    ADD_MSG = _("Add a new source")
    EDIT_MSG = _("Edit the selected source")
    DEL_MSG = _("Delete the selected source")

    def __init__(self,dbstate,uistate):

        signal_map = {
            'source-add'     : self.row_add,
            'source-update'  : self.row_update,
            'source-delete'  : self.row_delete,
            'source-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(
            self, _('Sources'), dbstate, uistate, column_names,
            len(column_names), DisplayModels.SourceModel, signal_map,
            dbstate.db.get_source_bookmarks(),
            Bookmarks.SourceBookmarks, multiple=True)

    def get_bookmarks(self):
        return self.dbstate.db.get_source_bookmarks()

    def drag_info(self):
        return DdTargets.SOURCE_LINK
    
    def define_actions(self):
        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        _('_Column Editor'), callback=self.column_editor)
        self.add_action('FastMerge', None, _('_Merge'),
                        callback=self.fast_merge)

    def column_editor(self,obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Source Columns'),
            self.uistate,
            self.dbstate.db.get_source_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self,list):
        self.dbstate.db.set_source_column_order(list)
        self.build_columns()

    def column_order(self):
        return self.dbstate.db.get_source_column_order()

    def get_stock(self):
        return 'gramps-source'

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
              <placeholder name="Merge">
                <menuitem action="FastMerge"/>
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

    def on_double_click(self,obj,event):
        handle = self.first_selected()
        source = self.dbstate.db.get_source_from_handle(handle)
        try:
            EditSource(self.dbstate, self.uistate, [], source)
        except Errors.WindowActiveError:
            pass

    def add(self,obj):
        EditSource(self.dbstate, self.uistate, [], RelLib.Source())

    def remove(self,obj):
        for source_handle in self.selected_handles():
            db = self.dbstate.db
            the_lists = Utils.get_source_referents(source_handle,db)

            source = db.get_source_from_handle(source_handle)

            ans = DelSrcQuery(source,db,the_lists)

            if filter(None,the_lists): # quick test for non-emptiness
                msg = _('This source is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'people and families that reference it.')
            else:
                msg = _('Deleting source will remove it from the database.')
            
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            descr = source.get_title()
            if descr == "":
                descr = source.get_gramps_id()
                
            QuestionDialog(_('Delete %s?') % descr, msg,
                           _('_Delete Source'),ans.query_response)

    def edit(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            source = self.dbstate.db.get_source_from_handle(handle)
            try:
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass

    def fast_merge(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        
        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _("Exactly two sources must be selected to perform a merge. "
                     "A second source can be selected by holding down the "
                     "control key while clicking on the desired source.")
            ErrorDialog(msg,msg2)
        else:
            import Merge
            Merge.MergeSources(self.dbstate, self.uistate, mlist[0], mlist[1])

