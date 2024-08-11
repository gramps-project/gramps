#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2011  Gary Burton
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
# Python classes
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ...widgets import SimpleButton
from .grampstab import GrampsTab
from gramps.gen.errors import WindowActiveError
from ...utils import match_primary_mask

_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_RETURN = Gdk.keyval_from_name("Return")
_DEL = Gdk.keyval_from_name("Delete")
_ADD = Gdk.keyval_from_name("Insert")
_OPEN = Gdk.keyval_from_name("o")
_LEFT = Gdk.keyval_from_name("Left")
_RIGHT = Gdk.keyval_from_name("Right")


# -------------------------------------------------------------------------
#
# Classes
#
# -------------------------------------------------------------------------
class ButtonTab(GrampsTab):
    """
    This class derives from the base GrampsTab, yet is not a usable Tab. It
    serves as another base tab for classes which need an Add/Edit/Remove button
    combination.
    """

    _MSG = {
        "add": _("Add"),
        "del": _("Remove"),
        "edit": _("Edit"),
        "share": _("Share"),
        "jump": _("Jump To"),
        "up": _("Move Up"),
        "down": _("Move Down"),
        "left": _("Move Left"),
        "right": _("Move right"),
    }
    L_R = 2  # indicator for left/right move buttons

    def __init__(
        self,
        dbstate,
        uistate,
        track,
        name,
        share_button=False,
        move_buttons=False,
        jump_button=False,
        top_label=None,
    ):
        """
        Similar to the base class, except after Build.

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
        @param share_button: Add a share button to the Notebook tab or not
        @type name: bool
        @param move_buttons: Add up and down button to the Notebook tab or not
        @type name: bool
        @param jump_button: Add a goto button
        @type name: bool
        @param top_label: Add a label in front of the buttons if given
        @type top_label: string or None for no label
        """
        self.dirty_selection = False
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        self._create_buttons(share_button, move_buttons, jump_button, top_label)

    def _create_buttons(self, share_button, move_buttons, jump_button, top_label):
        """
        Create a button box consisting of three buttons, one for Add,
        one for Edit, and one for Delete.

        Add buttons for Share, Move and Jump depending on parameters. This
        button box is then appended hbox (self).
        Prepend a label if top_label given

        Note: some ButtonTab subclasses override this method.
        """
        if top_label:
            self.top_label = Gtk.Label(label=top_label)
            self.top_label.set_use_markup(True)
            self.track_ref_for_deletion("top_label")

        self.add_btn = SimpleButton("list-add", self.add_button_clicked)
        self.edit_btn = SimpleButton("gtk-edit", self.edit_button_clicked)
        self.del_btn = SimpleButton("list-remove", self.del_button_clicked)
        self.track_ref_for_deletion("add_btn")
        self.track_ref_for_deletion("edit_btn")
        self.track_ref_for_deletion("del_btn")

        self.add_btn.set_tooltip_text(self._MSG["add"])
        self.edit_btn.set_tooltip_text(self._MSG["edit"])
        self.del_btn.set_tooltip_text(self._MSG["del"])

        if share_button:
            self.share_btn = SimpleButton("gtk-index", self.share_button_clicked)
            self.share_btn.set_tooltip_text(self._MSG["share"])
            self.track_ref_for_deletion("share_btn")
        else:
            self.share_btn = None

        if move_buttons:
            l_r = move_buttons == self.L_R
            self.up_btn = SimpleButton(
                "go-previous" if l_r else "go-up", self.up_button_clicked
            )
            self.up_btn.set_tooltip_text(self._MSG["left" if l_r else "up"])
            self.down_btn = SimpleButton(
                "go-next" if l_r else "go-down", self.down_button_clicked
            )
            self.down_btn.set_tooltip_text(self._MSG["right" if l_r else "down"])
            self.track_ref_for_deletion("up_btn")
            self.track_ref_for_deletion("down_btn")
        else:
            self.up_btn = None
            self.down_btn = None

        if jump_button:
            self.jump_btn = SimpleButton("go-jump", self.jump_button_clicked)
            self.track_ref_for_deletion("jump_btn")
            self.jump_btn.set_tooltip_text(self._MSG["jump"])
        else:
            self.jump_btn = None

        hbox = Gtk.Box()
        hbox.set_spacing(6)
        if top_label:
            hbox.pack_start(self.top_label, False, True, 0)
        hbox.pack_start(self.add_btn, False, True, 0)
        if share_button:
            hbox.pack_start(self.share_btn, False, True, 0)
        hbox.pack_start(self.edit_btn, False, True, 0)
        hbox.pack_start(self.del_btn, False, True, 0)
        if move_buttons:
            hbox.pack_start(self.up_btn, False, True, 0)
            hbox.pack_start(self.down_btn, False, True, 0)

        if self.jump_btn:
            hbox.pack_start(self.jump_btn, False, True, 0)
        hbox.show_all()
        self.pack_start(hbox, False, True, 0)

        if self.dbstate.db.readonly:
            self.add_btn.set_sensitive(False)
            self.del_btn.set_sensitive(False)
            if share_button:
                self.share_btn.set_sensitive(False)
            if jump_button and self.jump_btn:
                self.jump_btn.set_sensitive(False)
            if move_buttons:
                self.up_btn.set_sensitive(False)
                self.down_btn.set_sensitive(False)

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs,
        the Edit button handler is called
        """
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            try:
                self.edit_button_clicked(obj)
            except WindowActiveError:
                pass

    def key_pressed(self, obj, event):
        """
        Handles the return key being pressed on list. If the key is pressed,
        the Edit button handler is called
        """
        if event.type == Gdk.EventType.KEY_PRESS:
            # print 'key pressed', event.keyval, event.get_state(), _ADD
            if event.keyval in (_RETURN, _KP_ENTER):
                try:
                    self.edit_button_clicked(obj)
                except WindowActiveError:
                    pass
            elif event.keyval in (_DEL,) and self.del_btn:
                if self.dirty_selection or self.dbstate.db.readonly:
                    return
                self.del_button_clicked(obj)
            elif event.keyval in (_ADD,) and self.add_btn:
                if self.dirty_selection or self.dbstate.db.readonly:
                    return
                self.add_button_clicked(obj)
            elif (
                event.keyval in (_OPEN,)
                and self.share_btn
                and match_primary_mask(event.get_state())
            ):
                self.share_button_clicked(obj)
            elif event.keyval in (_LEFT,) and (
                event.get_state() & Gdk.ModifierType.MOD1_MASK
            ):
                self.prev_page()
            elif event.keyval in (_RIGHT,) and (
                event.get_state() & Gdk.ModifierType.MOD1_MASK
            ):
                self.next_page()
            else:
                return
            return True

    def add_button_clicked(self, obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        print("Uncaught Add clicked")

    def share_button_clicked(self, obj):
        """
        Function called with the Share button is clicked. This function
        should be overridden by the derived class.
        """
        print("Uncaught Share clicked")

    def jump_button_clicked(self, obj):
        """
        Function called with the Jump button is clicked. This function
        should be overridden by the derived class.
        """
        print("Uncaught Jump clicked")

    def del_button_clicked(self, obj):
        """
        Function called with the Delete button is clicked. This function
        should be overridden by the derived class.
        """
        print("Uncaught Delete clicked")

    def edit_button_clicked(self, obj):
        """
        Function called with the Edit button is clicked or the double
        click is caught. This function should be overridden by the derived
        class.
        """
        print("Uncaught Edit clicked")

    def up_button_clicked(self, obj):
        """
        Function called with the Up button is clicked.
        This function should be overridden by the derived class.
        """
        print("Uncaught Up clicked")

    def down_button_clicked(self, obj):
        """
        Function called with the Down button is clicked.
        This function should be overridden by the derived class.
        """
        print("Uncaught Down clicked")

    def _selection_changed(self, obj=None):
        """
        Attached to the selection's 'changed' signal. Checks
        to see if anything is selected. If it is, the edit and
        delete buttons are enabled, otherwise the are disabled.
        """
        # Comparing to None is important, as empty strings
        # and 0 can be returned
        # This method is called as callback on change, and can be called
        # explicitly, dirty_selection must make sure they do not interact
        if self.dirty_selection:
            return
        if self.get_selected() is not None:
            self.edit_btn.set_sensitive(True)
            if self.jump_btn:
                self.jump_btn.set_sensitive(True)
            if not self.dbstate.db.readonly:
                self.del_btn.set_sensitive(True)
            # note: up and down cannot be set unsensitive after clicked
            #       or they do not respond to a next click
            # if self.up_btn :
            #    self.up_btn.set_sensitive(True)
            #    self.down_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            if self.jump_btn:
                self.jump_btn.set_sensitive(False)
            if not self.dbstate.db.readonly:
                self.del_btn.set_sensitive(False)
            # note: up and down cannot be set unsensitive after clicked
            #       or they do not respond to a next click
            # if self.up_btn :
            #    self.up_btn.set_sensitive(False)
            #    self.down_btn.set_sensitive(False)
