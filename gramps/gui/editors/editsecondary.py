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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..managedwindow import ManagedWindow
from ..display import display_help
from gramps.gen.config import config
from ..dbguielement import DbGUIElement


class EditSecondary(ManagedWindow, DbGUIElement):
    def __init__(self, state, uistate, track, obj, callback=None):
        """Create an edit window.  Associates a person with the window."""

        self.obj = obj
        self.old_obj = obj.serialize()
        self.dbstate = state
        self.uistate = uistate
        self.db = state.db
        self.callback = callback
        self.__tabs = []

        ManagedWindow.__init__(self, uistate, track, obj)
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

    def _post_init(self):
        """
        Derived class should do any post-window initalization in this task.
        """
        pass

    def _connect_signals(self):
        pass

    def _setup_fields(self):
        pass

    def _create_tabbed_pages(self):
        pass

    def build_window_key(self, obj):
        return id(obj)

    def _setup_notebook_tabs(self, notebook):
        for child in notebook.get_children():
            label = notebook.get_tab_label(child)
            page_no = notebook.page_num(child)
            label.drag_dest_set(0, [], 0)
            label.connect("drag_motion", self._switch_page_on_dnd, notebook, page_no)
            child.set_parent_notebook(notebook)
        notebook.connect("key-press-event", self.key_pressed, notebook)

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

    def _add_tab(self, notebook, page):
        self.__tabs.append(page)
        notebook.insert_page(page, page.get_tab_widget(), -1)
        page.label.set_use_underline(True)
        return page

    def _cleanup_on_exit(self):
        """Unset all things that can block garbage collection.
        Finalize rest
        """
        for tab in self.__tabs:
            if hasattr(tab, "_cleanup_on_exit"):
                tab._cleanup_on_exit()
        self.__tabs = None
        self.dbstate = None
        self.uistate = None
        self.obj = None
        self.db = None
        self.callback = None
        self.callman.database = None
        self.callman = None

    def define_ok_button(self, button, function):
        button.connect("clicked", function)
        button.set_sensitive(not self.db.readonly)

    def define_cancel_button(self, button):
        button.connect("clicked", self.canceledits)

    def define_help_button(self, button, webpage="", section=""):
        button.connect("clicked", lambda x: display_help(webpage, section))

    def canceledits(self, *obj):
        """
        Undo the edits that happened on this secondary object
        """
        self.obj.unserialize(self.old_obj)
        self.close(obj)

    def close(self, *obj):
        self._cleanup_db_connects()
        self._cleanup_connects()
        ManagedWindow.close(self)
        self._cleanup_on_exit()

    def _cleanup_db_connects(self):
        """
        All connects that happened to signals of the db must be removed on
        closed. This implies two things:
        1. The connects on the main view must be disconnected
        2. Connects done in subelements must be disconnected
        """
        # cleanup callbackmanager of this editor
        self._cleanup_callbacks()
        for tab in [tab for tab in self.__tabs if hasattr(tab, "callman")]:
            tab._cleanup_callbacks()

    def _cleanup_connects(self):
        """
        Connects to interface elements to things outside the element should be
        removed before destroying the interface
        """
        self._cleanup_local_connects()
        for tab in [
            tab for tab in self.__tabs if hasattr(tab, "_cleanup_local_connects")
        ]:
            tab._cleanup_local_connects()

    def _cleanup_local_connects(self):
        """
        Connects to interface elements to things outside the element should be
        removed before destroying the interface. This methods cleans connects
        of the main interface, not of the displaytabs.
        """
        pass
