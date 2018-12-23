#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright(C) 2014  Bastien Jacquet
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

"""
GtkWidget showing a box for interactive-search in Gtk.TreeView
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.interactivesearch")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk, Gdk, GLib

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..utils import match_primary_mask
#-------------------------------------------------------------------------
#
# InteractiveSearchBox class
#
#-------------------------------------------------------------------------


class InteractiveSearchBox:
    """
    Mainly adapted from gtktreeview.c
    """
    _SEARCH_DIALOG_TIMEOUT = 5000
    _SEARCH_DIALOG_LAUNCH_TIMEOUT = 150

    def __init__(self, treeview):
        self._treeview = treeview
        self._search_window = None
        self._search_entry = None
        self._search_entry_changed_id = 0
        self.__disable_popdown = False
        self._entry_flush_timeout = None
        self._entry_launchsearch_timeout = None
        self.__selected_search_result = 0
        # Disable builtin interactive search by intercepting CTRL-F instead.
        # self._treeview.connect('start-interactive-search',
        #                       self.start_interactive_search)

    def treeview_keypress(self, obj, event):
        """
        function handling keypresses from the treeview
        for the typeahead find capabilities
        """
        if not Gdk.keyval_to_unicode(event.keyval):
            return False
        if self._key_cancels_search(event.keyval):
            return False
        self.ensure_interactive_directory()

        # Make a copy of the current text
        old_text = self._search_entry.get_text()

        popup_menu_id = self._search_entry.connect("popup-menu",
                                                   lambda x: True)

        # Move the entry off screen
        screen = self._treeview.get_screen()
        self._search_window.move(screen.get_width() + 1,
                                 screen.get_height() + 1)
        self._search_window.show()

        # Send the event to the window.  If the preedit_changed signal is
        # emitted during this event, we will set self.__imcontext_changed
        new_event = Gdk.Event.copy(event)
        new_event.window = self._search_window.get_window()
        self._search_window.realize()
        self.__imcontext_changed = False
        retval = self._search_window.event(new_event)
        self._search_window.hide()

        self._search_entry.disconnect(popup_menu_id)

        # Intercept CTRL+F keybinding because Gtk do not allow to _replace_ it.
        if (match_primary_mask(event.state)
                and event.keyval in [Gdk.KEY_f, Gdk.KEY_F]):
            self.__imcontext_changed = True
            # self.real_start_interactive_search(event.get_device(), True)

        # We check to make sure that the entry tried to handle the text,
        # and that the text has changed.
        new_text = self._search_entry.get_text()
        text_modified = (old_text != new_text)
        if (self.__imcontext_changed or  # we're in a preedit
                (retval and text_modified)):  # ...or the text was modified
            self.real_start_interactive_search(event.get_device(), False)
            self._treeview.grab_focus()
            return True
        else:
            self._search_entry.set_text("")
            return False

    def _preedit_changed(self, im_context, tree_view):
        self.__imcontext_changed = 1
        if(self._entry_flush_timeout):
            GLib.source_remove(self._entry_flush_timeout)
            self._entry_flush_timeout = GLib.timeout_add(
                self._SEARCH_DIALOG_TIMEOUT, self.cb_entry_flush_timeout)

    def ensure_interactive_directory(self):
        toplevel = self._treeview.get_toplevel()
        screen = self._treeview.get_screen()
        if self._search_window:
            if toplevel.has_group():
                toplevel.get_group().add_window(self._search_window)
            elif self._search_window.has_group():
                self._search_window.get_group().remove_window(
                    self._search_window)
            self._search_window.set_screen(screen)
            return

        self._search_window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self._search_window.set_screen(screen)
        if toplevel.has_group():
            toplevel.get_group().add_window(self._search_window)
        self._search_window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self._search_window.set_modal(True)
        self._search_window.connect("delete-event", self._delete_event)
        self._search_window.connect("key-press-event", self._key_press_event)
        self._search_window.connect("button-press-event",
                                    self._button_press_event)
        self._search_window.connect("scroll-event", self._scroll_event)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        frame.show()
        self._search_window.add(frame)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.show()
        frame.add(vbox)
        vbox.set_border_width(3)

        """ add entry """
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.show()
        self._search_entry.connect("populate-popup", self._disable_popdown)
        self._search_entry.connect("activate", self._activate)
        self._search_entry.connect("preedit-changed", self._preedit_changed)

        vbox.add(self._search_entry)
        self._search_entry.realize()

    def real_start_interactive_search(self, device, keybinding):
        """
        Pops up the interactive search entry.  If keybinding is TRUE then
        the user started this by typing the start_interactive_search
        keybinding. Otherwise, it came from just typing
        """
        if (self._search_window.get_visible()):
            return True
        self.ensure_interactive_directory()
        if keybinding:
            self._search_entry.set_text("")
        self._position_func()
        self._search_window.show()
        if self._search_entry_changed_id == 0:
            self._search_entry_changed_id = \
                self._search_entry.connect("changed", self.delayed_changed)

        # Grab focus without selecting all the text
        self._search_entry.grab_focus()
        self._search_entry.set_position(-1)
        # send focus-in event
        event = Gdk.Event()
        event.type = Gdk.EventType.FOCUS_CHANGE
        event.focus_change.in_ = True
        event.focus_change.window = self._search_window.get_window()
        self._search_entry.emit('focus-in-event', event)
        # search first matching iter
        self.delayed_changed(self._search_entry)
        # uncomment when deleting delayed_changed
        # self.search_init(self._search_entry)
        return True

    def cb_entry_flush_timeout(self):
        event = Gdk.Event()
        event.type = Gdk.EventType.FOCUS_CHANGE
        event.focus_change.in_ = True
        event.focus_change.window = self._treeview.get_window()
        self._dialog_hide(event)
        self._entry_flush_timeout = 0
        return False

    def delayed_changed(self, obj):
        """
        This permits to start the search only a short delay after last keypress
        This becomes useless with Gtk 3.10 Gtk.SearchEntry, which has a
        'search-changed' signal.
        """
        # renew flush timeout
        self._renew_flush_timeout()
        # renew search timeout
        if self._entry_launchsearch_timeout:
            GLib.source_remove(self._entry_launchsearch_timeout)
        self._entry_launchsearch_timeout = GLib.timeout_add(
            self._SEARCH_DIALOG_LAUNCH_TIMEOUT, self.search_init)

    def search_init(self):
        """
        This is the function performing the search
        """
        self._entry_launchsearch_timeout = 0
        text = self._search_entry.get_text()
        if not text:
            return

        model = self._treeview.get_model()
        if not model:
            return
        selection = self._treeview.get_selection()
        # disable flush timeout while searching
        if self._entry_flush_timeout:
            GLib.source_remove(self._entry_flush_timeout)
            self._entry_flush_timeout = 0
        # search
        # cursor_path = self._treeview.get_cursor()[0]
        # model.get_iter(cursor_path)
        start_iter = model.get_iter_first()
        self.search_iter(selection, start_iter, text, 0, 1)
        self.__selected_search_result = 1
        # renew flush timeout
        self._renew_flush_timeout()

    def _renew_flush_timeout(self):
        if self._entry_flush_timeout:
            GLib.source_remove(self._entry_flush_timeout)
        self._entry_flush_timeout = GLib.timeout_add(
            self._SEARCH_DIALOG_TIMEOUT, self.cb_entry_flush_timeout)

    def _move(self, up=False):
        text = self._search_entry.get_text()
        if not text:
            return

        if up and self.__selected_search_result == 1:
            return False

        model = self._treeview.get_model()
        selection = self._treeview.get_selection()
        # disable flush timeout while searching
        if self._entry_flush_timeout:
            GLib.source_remove(self._entry_flush_timeout)
            self._entry_flush_timeout = 0
        # search
        start_count = self.__selected_search_result + (-1 if up else 1)
        start_iter = model.get_iter_first()
        found_iter = self.search_iter(selection, start_iter, text, 0,
                                      start_count)
        if found_iter:
            self.__selected_search_result += (-1 if up else 1)
            return True
        else:
            # Return to old iter
            self.search_iter(selection, start_iter, text, 0,
                             self.__selected_search_result)
            return False
        # renew flush timeout
        self._renew_flush_timeout()
        return

    def _activate(self, obj):
        self.cb_entry_flush_timeout()
        # If we have a row selected and it's the cursor row, we activate
        # the row XXX
#         if self._cursor_node and \
#             self._cursor_node.set_flag(Gtk.GTK_RBNODE_IS_SELECTED):
#             path = _gtk_tree_path_new_from_rbtree(
#                            tree_view->priv->cursor_tree,
#                            tree_view->priv->cursor_node)
#             gtk_tree_view_row_activated(tree_view, path,
#                                         tree_view->priv->focus_column)

    def _button_press_event(self, obj, event):
        if not obj:
            return
        # keyb_device = event.device
        event = Gdk.Event()
        event.type = Gdk.EventType.FOCUS_CHANGE
        event.focus_change.in_ = True
        event.focus_change.window = self._treeview.get_window()
        self._dialog_hide(event)

    def _disable_popdown(self, obj, menu):
        self.__disable_popdown = 1
        menu.connect("hide", self._enable_popdown)

    def _enable_popdown(self, obj):
        self._timeout_enable_popdown = GLib.timeout_add(
            self._SEARCH_DIALOG_TIMEOUT, self._real_search_enable_popdown)

    def _real_search_enable_popdown(self):
        self.__disable_popdown = 0

    def _delete_event(self, obj, event):
        if not obj:
            return
        self._dialog_hide(None)

    def _scroll_event(self, obj, event):
        retval = False
        if (event.direction == Gdk.ScrollDirection.UP):
            self._move(True)
            retval = True
        elif (event.direction == Gdk.ScrollDirection.DOWN):
            self._move(False)
            retval = True
        if retval:
            self._renew_flush_timeout()

    def _key_cancels_search(self, keyval):
        return keyval in [Gdk.KEY_Escape,
                          Gdk.KEY_Tab,
                          Gdk.KEY_KP_Tab,
                          Gdk.KEY_ISO_Left_Tab]

    def _key_press_event(self, widget, event):
        retval = False
        # close window and cancel the search
        if self._key_cancels_search(event.keyval):
            self.cb_entry_flush_timeout()
            return True
        # Launch search
        if (event.keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]):
            if self._entry_launchsearch_timeout:
                GLib.source_remove(self._entry_launchsearch_timeout)
                self._entry_launchsearch_timeout = 0
            self.search_init()
            retval = True

        default_accel = widget.get_modifier_mask(
            Gdk.ModifierIntent.PRIMARY_ACCELERATOR)
        # select previous matching iter
        if ((event.keyval in [Gdk.KEY_Up, Gdk.KEY_KP_Up]) or
            (((event.state & (default_accel | Gdk.ModifierType.SHIFT_MASK))
                == (default_accel | Gdk.ModifierType.SHIFT_MASK))
                and (event.keyval in [Gdk.KEY_g, Gdk.KEY_G]))):
            if(not self._move(True)):
                widget.error_bell()
            retval = True

        # select next matching iter
        if ((event.keyval in [Gdk.KEY_Down, Gdk.KEY_KP_Down]) or
            (((event.state & (default_accel | Gdk.ModifierType.SHIFT_MASK))
                == (default_accel))
                and (event.keyval in [Gdk.KEY_g, Gdk.KEY_G]))):
            if(not self._move(False)):
                widget.error_bell()
            retval = True

        # renew the flush timeout
        if retval:
            self._renew_flush_timeout()
        return retval

    def _dialog_hide(self, event):
        if self.__disable_popdown:
            return
        if self._search_entry_changed_id:
            self._search_entry.disconnect(self._search_entry_changed_id)
            self._search_entry_changed_id = 0
        if self._entry_flush_timeout:
            GLib.source_remove(self._entry_flush_timeout)
            self._entry_flush_timeout = 0
        if self._entry_launchsearch_timeout:
            GLib.source_remove(self._entry_launchsearch_timeout)
            self._entry_launchsearch_timeout = 0
        if self._search_window.get_visible():
            # send focus-in event
            self._search_entry.emit('focus-out-event', event)
            self._search_window.hide()
            self._search_entry.set_text("")
            self._treeview.emit('focus-in-event', event)
        self.__selected_search_result = 0

    def _position_func(self, userdata=None):
        tree_window = self._treeview.get_window()
        screen = self._treeview.get_screen()

        monitor_num = screen.get_monitor_at_window(tree_window)
        monitor = screen.get_monitor_workarea(monitor_num)

        self._search_window.realize()
        ret, tree_x, tree_y = tree_window.get_origin()
        tree_width = tree_window.get_width()
        tree_height = tree_window.get_height()
        _, requisition = self._search_window.get_preferred_size()

        if tree_x + tree_width > screen.get_width():
            x = screen.get_width() - requisition.width
        elif tree_x + tree_width - requisition.width < 0:
            x = 0
        else:
            x = tree_x + tree_width - requisition.width

        if tree_y + tree_height + requisition.height > screen.get_height():
            y = screen.get_height() - requisition.height
        elif(tree_y + tree_height < 0):  # isn't really possible ...
            y = 0
        else:
            y = tree_y + tree_height

        self._search_window.move(x, y)

    def search_iter_slow(self, selection, cur_iter, text, count, n):
        """
        Standard row-by-row search through all rows
        Should work for both List/Tree models
        Both expanded and collapsed rows are searched.
        """
        model = self._treeview.get_model()
        search_column = self._treeview.get_search_column()
        is_tree = not (model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY)
        while True:
            if not cur_iter:    # can happen on empty list
                return False
            if (self.search_equal_func(model, search_column,
                                       text, cur_iter)):
                count += 1
                if (count == n):
                    found_path = model.get_path(cur_iter)
                    self._treeview.expand_to_path(found_path)
                    self._treeview.scroll_to_cell(found_path, None, 1, 0.5, 0)
                    selection.select_path(found_path)
                    self._treeview.set_cursor(found_path)
                    return True

            if is_tree and model.iter_has_child(cur_iter):
                cur_iter = model.iter_children(cur_iter)
            else:
                done = False
                while True:  # search iter of next row
                    next_iter = model.iter_next(cur_iter)
                    if next_iter:
                        cur_iter = next_iter
                        done = True
                    else:
                        cur_iter = model.iter_parent(cur_iter)
                        if(not cur_iter):
                            # we've run out of tree, done with this func
                            return False
                    if done:
                        break
        return False

    @staticmethod
    def search_equal_func(model, search_column, text, cur_iter):
        value = model.get_value(cur_iter, search_column)
        key1 = value.lower()
        key2 = text.lower()
        return key1.startswith(key2)

    def search_iter(self, selection, cur_iter, text, count, n):
        model = self._treeview.get_model()
        is_listonly = (model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY)
        if is_listonly and hasattr(model, "node_map"):
            return self.search_iter_sorted_column_flat(selection, cur_iter,
                                                       text, count, n)
        else:
            return self.search_iter_slow(selection, cur_iter, text, count, n)

    def search_iter_sorted_column_flat(self, selection, cur_iter, text,
                                       count, n):
        """
        Search among the currently set search-column for a cell starting with
        text
        It assumes that this column is currently sorted, and as
        a LIST_ONLY view it therefore contains index2hndl = model.node_map._index2hndl
        which is a _sorted_ list of (sortkey, handle) tuples
        """
        model = self._treeview.get_model()
        search_column = self._treeview.get_search_column()
        is_tree = not (model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY)

        # If there is a sort_key index, let's use it
        if not is_tree and hasattr(model, "node_map"):
            import bisect
            index2hndl = model.node_map._index2hndl

            # create lookup key from the appropriate sort_func
            # TODO: explicitely announce the data->sortkey func in models
            # sort_key = model.sort_func(text)
            sort_key = glocale.sort_key(text.lower())
            srtkey_hndl = (sort_key, "")
            lo_bound = 0  # model.get_path(cur_iter)
            found_index = bisect.bisect_left(index2hndl, srtkey_hndl, lo=lo_bound)
            # if insert position is at tail, no match
            if found_index == len(index2hndl):
                return False
            srt_key, hndl = index2hndl[found_index]
            # Check if insert position match for real
            # (as insert position might not start with the text)
            if not model[found_index][search_column].lower().startswith(text.lower()):
                return False
            found_path = Gtk.TreePath((model.node_map.real_path(found_index),))
            self._treeview.scroll_to_cell(found_path, None, 1, 0.5, 0)
            selection.select_path(found_path)
            self._treeview.set_cursor(found_path)
            return True
        return False
