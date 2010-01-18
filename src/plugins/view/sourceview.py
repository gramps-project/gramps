# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
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
Source View
"""

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
import gen.lib
import config
from gui.views.listview import ListView
from gui.views.treemodels import SourceModel
import Utils
import Bookmarks
import Errors
from DdTargets import DdTargets
from QuestionDialog import ErrorDialog
from gui.editors import EditSource, DeleteSrcQuery
from Filters.SideBar import SourceSidebarFilter
from gen.plug import CATEGORY_QR_SOURCE

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _


#-------------------------------------------------------------------------
#
# SourceView
#
#-------------------------------------------------------------------------
class SourceView(ListView):

    COLUMN_NAMES = [
        _('Title'),
        _('ID'),
        _('Author'),
        _('Abbreviation'),
        _('Publication Information'),
        _('Last Changed'),
        ]
    
    ADD_MSG = _("Add a new source")
    EDIT_MSG = _("Edit the selected source")
    DEL_MSG = _("Delete the selected source")
    FILTER_TYPE = "Source"
    QR_CATEGORY = CATEGORY_QR_SOURCE

    def __init__(self, dbstate, uistate, nav_group=0):

        signal_map = {
            'source-add'     : self.row_add,
            'source-update'  : self.row_update,
            'source-delete'  : self.row_delete,
            'source-rebuild' : self.object_build,
            }

        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            }

        ListView.__init__(
            self, _('Sources'), dbstate, uistate, 
            SourceView.COLUMN_NAMES, len(SourceView.COLUMN_NAMES), 
            SourceModel, signal_map,
            dbstate.db.get_source_bookmarks(),
            Bookmarks.SourceBookmarks, nav_group,
            multiple=True,
            filter_class=SourceSidebarFilter)

        config.connect("interface.filter",
                          self.filter_toggle)

    def navigation_type(self):
        return 'Source'

    def column_ord_setfunc(self, clist):
        self.dbstate.db.set_source_column_order(clist)

    def get_bookmarks(self):
        return self.dbstate.db.get_source_bookmarks()

    def drag_info(self):
        return DdTargets.SOURCE_LINK
    
    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                         _('_Column Editor'), callback=self._column_editor)
        self._add_action('FastMerge', None, _('_Merge'),
                         callback=self.fast_merge)
        self._add_action('FilterEdit', None, _('Source Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)
        self._add_action('Dummy', None, '  ', None, None, self.dummy_report)

    def _column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Source Columns'),
            self.uistate,
            self.dbstate.db.get_source_column_order(),
            SourceView.COLUMN_NAMES,
            self.set_column_order)

    def column_order(self):
        return self.dbstate.db.get_source_column_order()

    def get_stock(self):
        return 'gramps-source'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
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
              <placeholder name="Merge">
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
          </popup>
        </ui>'''

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def add(self, obj):
        EditSource(self.dbstate, self.uistate, [], gen.lib.Source())

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = Utils.get_source_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_source_from_handle(handle)
        query = DeleteSrcQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            source = self.dbstate.db.get_source_from_handle(handle)
            try:
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass

    def fast_merge(self, obj):
        mlist = self.selected_handles()
        
        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _("Exactly two sources must be selected to perform a merge. "
                     "A second source can be selected by holding down the "
                     "control key while clicking on the desired source.")
            ErrorDialog(msg, msg2)
        else:
            import Merge
            Merge.MergeSources(self.dbstate, self.uistate, mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_source_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None
