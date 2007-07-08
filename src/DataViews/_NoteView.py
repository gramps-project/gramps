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
Place View
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
import PageView
import DisplayModels
import Utils
import Errors
import Bookmarks
import Config
import ColumnOrder
from RelLib import Note
from DdTargets import DdTargets
from QuestionDialog import QuestionDialog, ErrorDialog
from Filters.SideBar import NoteSidebarFilter
from Editors import EditNote, DeleteNoteQuery

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('ID'),
    _('Type'),
    _('Marker'),
    _('Preview'),
    ]

#-------------------------------------------------------------------------
#
# NoteView
#
#-------------------------------------------------------------------------
class NoteView(PageView.ListView):

    ADD_MSG     = _("Add a new note")
    EDIT_MSG    = _("Edit the selected note")
    DEL_MSG     = _("Delete the selected note")
    FILTER_TYPE = "Note"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'note-add'     : self.row_add,
            'note-update'  : self.row_update,
            'note-delete'  : self.row_delete,
            'note-rebuild' : self.build_tree,
        }

        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
        }

        PageView.ListView.__init__(
            self, _('Notes'), dbstate, uistate, column_names,
            len(column_names), DisplayModels.NoteModel, signal_map,
            dbstate.db.get_note_bookmarks(),
            Bookmarks.NoteBookmarks,
            filter_class=NoteSidebarFilter,
            multiple=False)

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)

    def get_bookmarks(self):
        """
        Returns the bookmark object
        """
        return self.dbstate.db.get_note_bookmarks()

    def drag_info(self):
        """
        Indicates that the drag type is an EVENT
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
        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        _('_Column Editor'), callback=self.column_editor)
        self.add_action('FilterEdit', None, _('Note Filter Editor'),
                        callback=self.filter_editor,)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_note_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def column_editor(self, obj):
        """
        returns a tuple indicating the column order
        """
        ColumnOrder.ColumnOrder(
            _('Select Note Columns'),
            self.uistate,
            self.dbstate.db.get_note_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self, clist):
        self.dbstate.db.set_note_column_order(clist)
        self.build_columns()

    def add(self, obj):
        try:
            EditNote(self.dbstate, self.uistate, [], Note())
        except Errors.WindowActiveError:
            pass

    def remove(self, obj):
        for note_handle in self.selected_handles():
            db = self.dbstate.db
            the_lists = Utils.get_note_referents(note_handle, db)

            note = db.get_note_from_handle(note_handle)

            ans = DeleteNoteQuery(self.dbstate, self.uistate, note, the_lists)

            if filter(None, the_lists): # quick test for non-emptiness
                msg = _('This note is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'other objects that reference it.')
            else:
                msg = _('Deleting note will remove it from the database.')
            
            msg = "%s %s" % (msg, Utils.data_recover_msg)
            descr = note.get_gramps_id()
            self.uistate.set_busy_cursor(1)
            QuestionDialog(_('Delete %s?') % descr, msg,
                           _('_Delete Note'), ans.query_response)
            self.uistate.set_busy_cursor(0)

    def edit(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        for handle in mlist:
            note = self.dbstate.db.get_note_from_handle(handle)
            try:
                EditNote(self.dbstate, self.uistate, [], note)
            except Errors.WindowActiveError:
                pass
