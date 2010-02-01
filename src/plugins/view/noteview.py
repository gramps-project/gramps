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
from gen.ggettext import gettext as _
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
from gen.lib import Note
from DdTargets import DdTargets
from Filters.SideBar import NoteSidebarFilter
from gui.editors import EditNote, DeleteNoteQuery
from gen.plug import CATEGORY_QR_NOTE

#-------------------------------------------------------------------------
#
# NoteView
#
#-------------------------------------------------------------------------
class NoteView(ListView):
    """
    Noteview, a normal flat listview for the notes
    """
    COL_PREVIEW = 0
    COL_ID = 1
    COL_TYPE = 2
    COL_MARKER = 3
    COL_CHAN = 4
    
    COLUMN_NAMES = [
        _('Preview'),
        _('ID'),
        _('Type'),
        _('Marker'),
        _('Last Changed')
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_PREVIEW, COL_ID, COL_TYPE, COL_MARKER]),
        ('columns.order', [COL_PREVIEW, COL_ID, COL_TYPE, COL_MARKER,
                           COL_CHAN]),
        ('columns.sizecol', [350, 75, 100, 100, 100]))

    ADD_MSG     = _("Add a new note")
    EDIT_MSG    = _("Edit the selected note")
    DEL_MSG     = _("Delete the selected note")
    FILTER_TYPE = "Note"
    QR_CATEGORY = CATEGORY_QR_NOTE

    def __init__(self, dbstate, uistate, nav_group=0):

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
            Bookmarks.NoteBookmarks, nav_group,
            filter_class=NoteSidebarFilter,
            multiple=True)

        config.connect("interface.filter",
                          self.filter_toggle)

    def navigation_type(self):
        return 'Note'

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
              <menuitem action="FilterEdit"/>
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

    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('FilterEdit', None, _('Note Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)
        self._add_action('Dummy', None, '  ', None, None, self.dummy_report)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_note_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

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
