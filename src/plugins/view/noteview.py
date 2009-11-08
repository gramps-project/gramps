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
Note View.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import logging
_LOG = logging.getLogger(".plugins.noteview")

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
from gui.views.listview import ListView
from gui.views.treemodels import NoteModel
import Utils
import Errors
import Bookmarks
import config
import ColumnOrder
from gen.lib import Note
from DdTargets import DdTargets
from Filters.SideBar import NoteSidebarFilter
from Editors import EditNote, DeleteNoteQuery

#-------------------------------------------------------------------------
#
# NoteView
#
#-------------------------------------------------------------------------
class NoteView(ListView):
    
    COLUMN_NAMES = [
        _('Preview'),
        _('ID'),
        _('Type'),
        _('Marker'),
        ]

    ADD_MSG     = _("Add a new note")
    EDIT_MSG    = _("Edit the selected note")
    DEL_MSG     = _("Delete the selected note")
    FILTER_TYPE = "Note"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'note-add'     : self.row_add,
            'note-update'  : self.row_update,
            'note-delete'  : self.row_delete,
            'note-rebuild' : self.object_build,
        }

        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
        }

        ListView.__init__(
            self, _('Notes'), dbstate, uistate, NoteView.COLUMN_NAMES,
            len(NoteView.COLUMN_NAMES), NoteModel, signal_map,
            dbstate.db.get_note_bookmarks(),
            Bookmarks.NoteBookmarks,
            filter_class=NoteSidebarFilter,
            multiple=True)

        config.connect("interface.filter",
                          self.filter_toggle)

    def column_ord_setfunc(self, clist):
        self.dbstate.db.set_note_column_order(clist)

    def get_bookmarks(self):
        """
        Return the bookmark object
        """
        return self.dbstate.db.get_note_bookmarks()

    def drag_info(self):
        """
        Indicate that the drag type is an EVENT
        """
        return DdTargets.NOTE_LINK

    def column_order(self):
        """
        returns a tuple indicating the column order
        """
        return self.dbstate.db.get_note_column_order()

    def get_stock(self):
        """
        Use the gramps-event stock icon
        """
        return 'gramps-notes'

    def ui_definition(self):
        """
        Defines the UI string for UIManager
        """
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

    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                         _('_Column Editor'), callback=self._column_editor)
        self._add_action('FilterEdit', None, _('Note Filter Editor'),
                         callback=self.filter_editor,)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_note_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def _column_editor(self, obj):
        """
        returns a tuple indicating the column order
        """
        ColumnOrder.ColumnOrder(
            _('Select Note Columns'),
            self.uistate,
            self.dbstate.db.get_note_column_order(),
            NoteView.COLUMN_NAMES,
            self.set_column_order)

    def add(self, obj):
        try:
            EditNote(self.dbstate, self.uistate, [], Note())
        except Errors.WindowActiveError:
            pass

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = Utils.get_note_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_note_from_handle(handle)
        query = DeleteNoteQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            note = self.dbstate.db.get_note_from_handle(handle)
            try:
                EditNote(self.dbstate, self.uistate, [], note)
            except Errors.WindowActiveError:
                pass
