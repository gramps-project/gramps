#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import ManagedWindow
from DisplayTabs import GrampsTab
import Config
from gui.dbguielement import DbGUIElement

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

class RefTab(GrampsTab):
    """
    This class provides a simple tabpage for use on EditReference
    """

    def __init__(self, dbstate, uistate, track, name, widget):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        @param widget: widget to be shown in the tab
        @type widge: gtk widget
        """
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        eventbox = gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox)
        self._set_label(show_image=False)
        widget.connect('key_press_event', self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

#-------------------------------------------------------------------------
#
# EditReference class
#
#-------------------------------------------------------------------------
class EditReference(ManagedWindow.ManagedWindow, DbGUIElement):

    def __init__(self, state, uistate, track, source, source_ref, update):
        self.db = state.db
        self.dbstate = state
        self.uistate = uistate
        self.source_ref = source_ref
        self.source = source
        self.source_added = False
        self.update = update
        self.warn_box = None
        self.__tabs = []

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, source_ref)
        DbGUIElement.__init__(self, self.db)

        self._local_init()
        self._set_size()
        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()
        self._post_init()

    def _local_init(self):
        """
        Derived class should do any pre-window initalization in this task.
        """
        pass

    def define_warn_box(self,box):
        self.warn_box = box

    def enable_warnbox(self):
        self.warn_box.show()

    def define_expander(self,expander):
        expander.set_expanded(True)

    def _post_init(self):
        """
        Derived class should do any post-window initalization in this task.
        """
        pass

    def _setup_notebook_tabs(self, notebook):
        for child in notebook.get_children():
            label = notebook.get_tab_label(child)
            page_no = notebook.page_num(child)
            label.drag_dest_set(0, [], 0)
            label.connect('drag_motion',
                          self._switch_page_on_dnd,
                          notebook,
                          page_no)
            child.set_parent_notebook(notebook)
        notebook.connect('key-press-event', self.key_pressed, notebook)

    def key_pressed(self, obj, event, notebook):
        """
        Handles the key being pressed on the notebook, pass to key press of
        current page.
        """
        pag = notebook.get_current_page()
        if not pag == -1:
            notebook.get_nth_page(pag).key_pressed(obj, event)

    def _switch_page_on_dnd(self, widget, context, x, y, time, notebook, page_no):
        if notebook.get_current_page() != page_no:
            notebook.set_current_page(page_no)

    def _add_tab(self, notebook,page):
        self.__tabs.append(page)
        notebook.insert_page(page, page.get_tab_widget())
        page.label.set_use_underline(True)
        return page

    def _connect_signals(self):
        pass

    def _setup_fields(self):
        pass

    def _create_tabbed_pages(self):
        pass

    def build_window_key(self,sourceref):
        #the window key for managedwindow identification. No need to return None
        if self.source and self.source.get_handle():
            return self.source.get_handle()
        else:
            return id(self)

    def define_ok_button(self, button, function):
        button.connect('clicked',function)
        button.set_sensitive(not self.db.readonly)

    def define_cancel_button(self, button):
        button.connect('clicked',self.close_and_cancel)

    def close_and_cancel(self, obj):
        self._cleanup_on_exit()
        self.close(obj)

    def check_for_close(self, handles):
        """
        Callback method for delete signals. 
        If there is a delete signal of the primary object we are editing, the
        editor (and all child windows spawned) should be closed
        """
        if self.source.get_handle() in handles:
            self.close()

    def define_help_button(self, button, webpage='', section=''):
        import GrampsDisplay
        button.connect('clicked', lambda x: GrampsDisplay.help(webpage,
                                                               section))
        button.set_sensitive(True)

    def _cleanup_on_exit(self):
        pass

    def close(self,*obj):
        self._cleanup_db_connects()
        ManagedWindow.ManagedWindow.close(self)

    def _cleanup_db_connects(self):
        """
        All connects that happened to signals of the db must be removed on 
        closed. This implies two things:
        1. The connects on the main view must be disconnected
        2. Connects done in subelements must be disconnected
        """
        #cleanup callbackmanager of this editor
        self._cleanup_callbacks()
        for tab in [tab for tab in self.__tabs if hasattr(tab, 'callman')]:
            tab._cleanup_callbacks()
