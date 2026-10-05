#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import abc

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository.Gio import SimpleActionGroup

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..managedwindow import ManagedWindow
from gramps.gen.datehandler import displayer, parser
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.config import config
from ..utils import is_right_click
from ..display import display_help
from ..dialog import SaveDialog
from gramps.gen.lib import PrimaryObject
from ..dbguielement import DbGUIElement
from ..uimanager import ActionGroup
from ..savecascade import children_to_resolve


class EditPrimary(ManagedWindow, DbGUIElement, metaclass=abc.ABCMeta):
    QR_CATEGORY = -1

    def __init__(
        self,
        state,
        uistate,
        track,
        obj,
        get_from_handle,
        get_from_gramps_id,
        callback=None,
    ):
        """
        Create an edit window.

        Associate a person with the window.

        """
        self.dp = parser
        self.dd = displayer
        self.name_displayer = name_displayer
        self.obj = obj
        self.dbstate = state
        self.uistate = uistate
        self.db = state.db
        self.callback = callback
        self.ok_button = None
        # The editor's confirm handler, captured by define_ok_button and driven
        # by _save_with_dependent_children. Defaults to save so the shared save
        # guard is safe even before/without define_ok_button (#7924).
        self._ok_function = self.save
        self.get_from_handle = get_from_handle
        self.get_from_gramps_id = get_from_gramps_id
        self.contexteventbox = None
        self.__tabs = []
        self.action_group = None

        ManagedWindow.__init__(self, uistate, track, obj)
        DbGUIElement.__init__(self, self.db)

        self.original = None
        if self.obj.handle:
            self.original = self.get_from_handle(self.obj.handle)

        self._local_init()
        # self.set_size() is called by self._local_init()'s self.setup_configs
        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        # if the database is changed, all info shown is invalid and the window
        # should close
        self.dbstate_connect_key = self.dbstate.connect(
            "database-changed", self._do_close
        )
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

    def _setup_fields(self):
        pass

    def _create_tabbed_pages(self):
        pass

    def _connect_signals(self):
        pass

    def build_window_key(self, obj):
        if obj and obj.get_handle():
            return obj.get_handle()
        else:
            return id(self)

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

    def object_is_empty(self):
        return self.obj.serialize()[1:] == self.empty_object().serialize()[1:]

    def define_ok_button(self, button, function):
        self.ok_button = button
        # Do not wire the editor's confirm handler straight to the OK button.
        # Route it -- and every other save door (see close()) -- through
        # _save_with_dependent_children first: when this editor is confirmed
        # while a child primary editor it spawned is still open holding unsaved
        # data whose completion callback must land a reference on this editor's
        # working object, that child is resolved BEFORE this editor reads its
        # references and commits. See Mantis #7924.
        self._ok_function = function
        button.connect("clicked", self._save_with_dependent_children)
        button.set_sensitive(not self.db.readonly)

    def _save_with_dependent_children(self, *args):
        """Confirm handler shared by every save door: resolve open dependent
        child editors, then save.

        A primary editor is non-modal, so it can be confirmed while a child
        primary editor it spawned -- e.g. an EditPerson opened as "add a new
        person as the mother" from EditFamily -- is still open with unsaved
        data. That child's completion callback, which writes the child's
        handle onto *this* editor's working object (EditFamily.new_mother_added),
        only runs when the *child* saves. If this editor commits first, it
        persists an object graph with that reference silently dropped and the
        child's data orphaned -- the #7924 defect.

        So drive each open dependent child's own save-guard first. If any child
        is left unresolved (the user chose "keep editing" on its "Save Changes?"
        prompt, or its save aborted on a validation error), abort this editor's
        save entirely -- it stays open and nothing is committed, so no partial
        graph is ever persisted.

        This is wired to BOTH the OK button (define_ok_button) and the
        close/Cancel/window-X save path (close()'s SaveDialog), so the child is
        resolved no matter which door commits the parent (Mantis #7924).
        """
        if not self._resolve_dependent_children():
            return
        self._ok_function(*args)

    def _resolve_dependent_children(self):
        """Resolve open child primary editors holding unsaved data before commit.

        Returns True if the save may proceed -- every dependent child editor
        was resolved (saved, or discarded by the user), or there were none.
        Returns False if a child was left unresolved, in which case the parent
        save must abort.

        Children are resolved deepest-first (see
        :func:`~gramps.gui.savecascade.children_to_resolve`) so that, in a
        nested chain, each level's completion callback has already landed on
        its own parent before that parent reads its references.
        """
        if self.uistate is None:
            return True
        try:
            item = self.uistate.gwm.get_item_from_track(self.track)
        except (IndexError, KeyError):
            return True
        for child in children_to_resolve(item, self._is_unresolved_dependent_child):
            if not child._resolve_before_parent_commit():
                return False
        return True

    def _is_unresolved_dependent_child(self, window):
        """True if ``window`` is an open child primary editor with a pending
        reference this editor's commit would drop.

        Only a primary editor opened WITH a completion callback (``callback``
        is not None -- e.g. EditFamily.new_mother_added) writes a handle back
        onto the spawning editor's object, so only such a child must be
        resolved before this editor commits. A child opened to edit an
        *existing* object carries no callback (EditFamily.edit_person passes
        none) -- committing this editor drops nothing, so it is left alone and
        the common case is unchanged (#7924 over-trigger guard). Selectors and
        secondary/reference windows are excluded by the EditPrimary check.
        """
        return (
            window is not self
            and isinstance(window, EditPrimary)
            and getattr(window, "opened", False)
            and getattr(window, "callback", None) is not None
            and window.data_has_changed()
        )

    def _resolve_before_parent_commit(self):
        """Drive this child editor's save-guard as part of a parent's commit.

        Called on a child primary editor when its parent is confirmed while
        this child is still open with unsaved data. It reuses the very same
        "Save Changes?" guard the direct-close path shows (:meth:`close`) --
        Save runs this editor's own save (its completion callback lands our
        reference on the parent's object), "Close without saving" discards our
        edits, Cancel keeps this editor open.

        Whether the parent save may proceed is read from *this* editor's own
        window state AFTER the attempt, never assumed up front: a successful
        save (or an explicit discard) closes this editor (``self.opened``
        becomes False); a Cancel ("keep editing") or a validation-aborted save
        leaves it open. So:

          * closed  -> return True  (resolved; the parent may commit);
          * open    -> return False (unresolved; the parent must abort).
        """
        if config.get("interface.dont-ask"):
            # The user opted out of the "Save Changes?" prompt. Honour that as
            # "save without asking" -- a silent save of this child, NOT as
            # skipping its save (which would drop its reference and revive the
            # #7924 defect for dont-ask users). A validation error still leaves
            # the editor open, handled by the check below.
            self.save()
        else:
            SaveDialog(
                _("Save Changes?"),
                _(
                    "If you close without saving, the changes you "
                    "have made will be lost"
                ),
                self._do_close,
                self.save,
                parent=self.window,
            )
        return not self.opened

    def define_cancel_button(self, button):
        button.connect("clicked", self.close)

    def define_help_button(self, button, webpage="", section=""):
        button.connect("clicked", lambda x: display_help(webpage, section))

    def _do_close(self, *obj):
        self._cleanup_db_connects()
        self.dbstate.disconnect(self.dbstate_connect_key)
        self._cleanup_connects()
        self._cleanup_on_exit()
        if self.action_group:
            self.uistate.uimanager.remove_action_group(self.action_group)
        self.get_from_handle = None
        self.get_from_gramps_id = None
        ManagedWindow.close(self)
        self.dbstate = None
        self.uistate = None
        self.db = None

    def _cleanup_db_connects(self):
        """
        All connects that happened to signals of the db must be removed on
        closed. This implies two things:
        1. The connects on the main view must be disconnected
        2. Connects done in subelements must be disconnected
        """
        # cleanup callbackmanager of this editor
        self._cleanup_callbacks()
        for tab in self.__tabs:
            if hasattr(tab, "callman"):
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

    def check_for_close(self, handles):
        """
        Callback method for delete signals.
        If there is a delete signal of the primary object we are editing, the
        editor (and all child windows spawned) should be closed
        """
        if self.obj.get_handle() in handles:
            self._do_close()

    def close(self, *obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if not config.get("interface.dont-ask") and self.data_has_changed():
            SaveDialog(
                _("Save Changes?"),
                _(
                    "If you close without saving, the changes you "
                    "have made will be lost"
                ),
                self._do_close,
                # Save via the shared guard, not self.save directly: closing a
                # parent editor with the window-X or Cancel and choosing Save
                # must ALSO resolve an open dependent child first, or the parent
                # commits with the child's reference dropped -- the #7924 defect
                # via a second save door (see _save_with_dependent_children).
                self._save_with_dependent_children,
                parent=self.window,
            )
            return True
        else:
            self._do_close()
            return False

    @abc.abstractmethod
    def empty_object(self):
        """empty_object should be overridden in child class"""

    def data_has_changed(self):
        if self.db.readonly:
            return False
        if self.original:
            cmp_obj = self.original
        else:
            cmp_obj = self.empty_object()
        return cmp_obj.serialize()[1:] != self.obj.serialize()[1:]

    def save(self, *obj):
        """Save changes and close. Inheriting classes must implement this"""
        self.close()

    def set_contexteventbox(self, eventbox):
        """Set the contextbox that grabs button presses if not grabbed
        by overlying widgets.
        """
        self.contexteventbox = eventbox
        self.contexteventbox.connect(
            "button-press-event", self._contextmenu_button_press
        )

    def _contextmenu_button_press(self, obj, event):
        """
        Button press event that is caught when a mousebutton has been
        pressed while on contexteventbox
        It opens a context menu with possible actions
        """
        if is_right_click(event):
            if self.obj.get_handle() == 0:
                return False

            # build the possible popup menu
            menu_model = self._build_popup_ui()
            if not menu_model:
                return False
            # set or unset sensitivity in popup
            self._post_build_popup_ui()

            menu = Gtk.Menu.new_from_model(menu_model)
            menu.attach_to_widget(obj, None)
            menu.show_all()
            menu.popup_at_pointer(event)
            return True
        return False

    def _build_popup_ui(self):
        """
        Create actions and ui of context menu
        If you don't need a popup, override this and return None
        """
        from ..plug.quick import create_quickreport_menu

        prefix = str(id(self))
        # get custom ui and actions
        ui_top, actions = self._top_contextmenu(prefix)
        # see which quick reports are available now:
        ui_qr = ""
        if self.QR_CATEGORY > -1:
            ui_qr, reportactions = create_quickreport_menu(
                self.QR_CATEGORY,
                self.dbstate,
                self.uistate,
                self.obj,
                prefix,
                track=self.track,
            )
            actions.extend(reportactions)

        popupui = (
            """<?xml version="1.0" encoding="UTF-8"?>
            <interface>
            <menu id="Popup">"""
            + ui_top
            + """
              <section>
            """
            + ui_qr
            + """
              </section>
            </menu>
            </interface>"""
        )

        builder = Gtk.Builder.new_from_string(popupui, -1)

        self.action_group = ActionGroup("EditPopup" + prefix, actions, prefix)
        act_grp = SimpleActionGroup()
        self.window.insert_action_group(prefix, act_grp)
        self.window.set_application(self.uistate.uimanager.app)
        self.uistate.uimanager.insert_action_group(self.action_group, act_grp)
        return builder.get_object("Popup")

    def _top_contextmenu(self, prefix):
        """
        Derived class can create a ui with menuitems and corresponding list of
        actiongroups
        """
        return "", []

    def _post_build_popup_ui(self):
        """
        Derived class should do extra actions here on the menu
        """
        pass

    def _uses_duplicate_id(self):
        """
        Check whether a changed or added Gramps ID already exists in the DB.

        Return True if a duplicate Gramps ID has been detected.

        """
        idval = self.obj.get_gramps_id()
        existing = self.get_from_gramps_id(idval)
        if existing:
            if existing.get_handle() == self.obj.get_handle():
                return (False, 0)
            else:
                return (True, idval)
        else:
            return (False, 0)
