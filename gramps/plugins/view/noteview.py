# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Note View.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
import logging
_LOG = logging.getLogger(".plugins.noteview")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import NoteModel
from gramps.gen.utils.db import get_note_referents
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import NoteBookmarks
from gramps.gen.config import config
from gramps.gen.lib import Note
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gui.filters.sidebar import NoteSidebarFilter
from gramps.gui.editors import EditNote, DeleteNoteQuery
from gramps.gui.merge import MergeNote
from gramps.gen.plug import CATEGORY_QR_NOTE

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
    COL_PRIV = 3
    COL_TAGS = 4
    COL_CHAN = 5

    # column definitions
    COLUMNS = [
        (_('Preview'), TEXT, None),
        (_('ID'), TEXT, None),
        (_('Type'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_PREVIEW, COL_ID, COL_TYPE]),
        ('columns.rank', [COL_PREVIEW, COL_ID, COL_TYPE, COL_PRIV, COL_TAGS,
                          COL_CHAN]),
        ('columns.size', [350, 75, 100, 40, 100, 100]))

    ADD_MSG = _("Add a new note")
    EDIT_MSG = _("Edit the selected note")
    DEL_MSG = _("Delete the selected note")
    MERGE_MSG = _("Merge the selected notes")
    FILTER_TYPE = "Note"
    QR_CATEGORY = CATEGORY_QR_NOTE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):

        signal_map = {
            'note-add'     : self.row_add,
            'note-update'  : self.row_update,
            'note-delete'  : self.row_delete,
            'note-rebuild' : self.object_build,
        }

        ListView.__init__(
            self, _('Notes'), pdata, dbstate, uistate,
            NoteModel, signal_map,
            NoteBookmarks, nav_group,
            filter_class=NoteSidebarFilter,
            multiple=True)

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return 'Note'

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

    additional_ui = [  # Defines the UI string for UIManager
        '''
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
''',
        '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label">%s...</attribute>
        </item>
      </section>
''' % _('Organize Bookmarks'),
        '''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
''',
        '''
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
''' % _("_Edit...", "action"),  # to use sgettext()
        '''
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Note Filter Editor</attribute>
        </item>
        </placeholder>
''',  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-add</property>
        <property name="action-name">win.Add</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Add...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">Edit...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-remove</property>
        <property name="action-name">win.Remove</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Delete</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-merge</property>
        <property name="action-name">win.Merge</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Merge...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''' % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
        '''
    <menu id="Popup">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">Forward</attribute>
        </item>
      </section>
      <section id="PopUpTree">
      </section>
      <section>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
    </menu>
    ''' % _('_Edit...', 'action')  # to use sgettext()
    ]

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_note_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def add(self, *obj):
        try:
            EditNote(self.dbstate, self.uistate, [], Note())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = get_note_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_note_from_handle(handle)
        query = DeleteNoteQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, *obj):
        for handle in self.selected_handles():
            note = self.dbstate.db.get_note_from_handle(handle)
            try:
                EditNote(self.dbstate, self.uistate, [], note)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Merge the selected notes.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge notes.")
            msg2 = _("Exactly two notes must be selected to perform a merge. "
                    "A second note can be selected by holding down the "
                    "control key while clicking on the desired note.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeNote(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set([])
        for tag_handle in handle_list:
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                    include_classes='Note')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, note_handle, tag_handle):
        """
        Add the given tag to the given note.
        """
        note = self.dbstate.db.get_note_from_handle(note_handle)
        note.add_tag(tag_handle)
        self.dbstate.db.commit_note(note, transaction)

    def remove_tag(self, transaction, note_handle, tag_handle):
        """
        Remove the given tag from the given note.
        """
        note = self.dbstate.db.get_note_from_handle(note_handle)
        note.remove_tag(tag_handle)
        self.dbstate.db.commit_note(note, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Note Filter",),
                ("Note Backlinks",))
