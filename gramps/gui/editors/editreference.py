#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
# Copyright (C) 2014       Paul Franklin
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
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..dialog import ErrorDialog
from ..managedwindow import ManagedWindow
from .displaytabs import GrampsTab
from gramps.gen.config import config
from ..dbguielement import DbGUIElement

# -------------------------------------------------------------------------
#
# Classes
#
# -------------------------------------------------------------------------


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
        eventbox = Gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox, True, True, 0)
        self._set_label(show_image=False)
        widget.connect("key_press_event", self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False


# -------------------------------------------------------------------------
#
# EditReference class
#
# -------------------------------------------------------------------------
class EditReference(ManagedWindow, DbGUIElement):
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

        ManagedWindow.__init__(self, uistate, track, source_ref)
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

    def define_warn_box(self, box):
        self.warn_box = box

    def enable_warnbox(self):
        self.warn_box.show()

    def define_expander(self, expander):
        expander.set_expanded(True)
        expander.connect("activate", self.__on_expand)

    def __on_expand(self, expander):
        """
        Sets the packing of the expander widget to depend on whether or not
        it is expanded.
        """
        state = not expander.get_expanded()
        parent = expander.get_parent()
        parent.set_child_packing(expander, state, state, 0, Gtk.PackType.START)
        expander.set_vexpand(state)

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

    def _connect_signals(self):
        pass

    def _setup_fields(self):
        pass

    def _create_tabbed_pages(self):
        pass

    def build_window_key(self, sourceref):
        # the window key for managedwindow identification. No need to return None
        if self.source and self.source.get_handle():
            return self.source.get_handle()
        else:
            return id(self)

    def define_ok_button(self, button, function):
        button.connect("clicked", function)
        button.set_sensitive(not self.db.readonly)

    def define_cancel_button(self, button):
        button.connect("clicked", self.close_and_cancel)

    def close_and_cancel(self, obj):
        self.close(obj)

    def check_for_close(self, handles):
        """
        Callback method for delete signals.
        If there is a delete signal of the primary object we are editing, the
        editor (and all child windows spawned) should be closed
        """
        if self.source.get_handle() in handles:
            self.close()

    def define_help_button(self, button, webpage="", section=""):
        from ..display import display_help

        button.connect("clicked", lambda x: display_help(webpage, section))
        button.set_sensitive(True)

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
        self.source_ref = None
        self.source = None
        self.update = None
        self.warn_box = None
        self.db = None
        self.callman.database = None
        self.callman = None

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

    def check_for_duplicate_id(self, type):
        """
        check to see if the gramps ID (if any) already exists

        type    : the gramps primary object type, a string
        returns : True if the gramps ID already exists, else False

        N.B. the various strings, string variables, and titles existed already
        """
        new_id = self.source.get_gramps_id()
        if new_id:
            id_func = getattr(self.db, "get_%s_from_gramps_id" % type.lower())
            old_primary = id_func(new_id)
            if old_primary:
                description = None
                if type == "Event":
                    msg1 = _("Cannot save event. ID already exists.")
                    description = old_primary.get_description()
                elif type == "Media":
                    msg1 = _("Cannot save media object. ID already exists.")
                    description = old_primary.get_description()
                elif type == "Repository":
                    msg1 = _("Cannot save repository. ID already exists.")
                    description = old_primary.get_name()
                else:
                    msg1 = _("Cannot save item. ID already exists.")
                if description:
                    msg2 = _(
                        "You have attempted to use the existing Gramps "
                        "ID with value %(id)s. This value is already "
                        "used by '%(prim_object)s'. Please enter a "
                        "different ID or leave blank to get the next "
                        "available ID value."
                    ) % {"id": new_id, "prim_object": description}
                else:
                    msg2 = _(
                        "You have attempted to use the existing Gramps "
                        "ID with value %(id)s. This value is already "
                        "used. Please enter a "
                        "different ID or leave blank to get the next "
                        "available ID value."
                    ) % {"id": new_id}
                ErrorDialog(msg1, msg2, parent=self.window)
                return True
        return False
