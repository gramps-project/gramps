#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

_LEFT = Gdk.keyval_from_name("Left")
_RIGHT = Gdk.keyval_from_name("Right")

# -------------------------------------------------------------------------
#
# Classes
#
# -------------------------------------------------------------------------


class GrampsTab(Gtk.Box):
    """
    This class provides the base level class for 'tabs', which are used to
    fill in notebook tabs for Gramps edit dialogs.

    Each tab returns a gtk container widget which can be inserted into a
    Gtk.Notebook by the instantiating object.

    All tab classes should inherit from GrampsTab
    """

    def __init__(self, dbstate, uistate, track, name):
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
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # store information to pass to child windows
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.changed = False
        self.__refs_for_deletion = []

        # save name used for notebook label, and build the widget used
        # for the label

        self.tab_name = name
        self.track_ref_for_deletion("tab_name")
        self.label_container = self.build_label_widget()
        self.track_ref_for_deletion("label_container")

        # build the interface
        self.share_btn = None
        self.build_interface()
        self.parent_notebook = None

    def get_selected(self):
        return None

    def is_empty(self):
        """
        Indicate if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        return True

    def build_label_widget(self):
        """
        Standard routine to build a widget. Does not need to be overridden
        by the derived class. Creates an container that has the label and
        the icon in it.
        @returns: widget to be used for the notebook label.
        @rtype: Gtk.Box
        """
        hbox = Gtk.Box()
        icon = self.get_icon_name()

        if isinstance(icon, tuple):
            name = icon[1]
        else:
            name = icon

        self.tab_image = Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)
        self.track_ref_for_deletion("tab_image")
        self.label = Gtk.Label(label=self.tab_name)
        self.track_ref_for_deletion("label")
        hbox.pack_start(self.tab_image, True, True, 0)
        hbox.set_spacing(6)
        hbox.add(self.label)
        hbox.show_all()
        return hbox

    def get_icon_name(self):
        """
        Provide the name of the registered stock icon to be used as the
        icon in the label. This is typically overridden by the derived
        class to provide the new name.
        @returns: stock icon name
        @rtype: str
        """
        return "document-new"

    def get_tab_widget(self):
        """
        Provide the widget to be used for the notebook tab label. A
        container class is provided, and the object may manipulate the
        child widgets contained in the container.
        @returns: gtk widget
        @rtype: Gtk.Box
        """
        return self.label_container

    def key_pressed(self, obj, event):
        """
        Handles the key being pressed.
        The inheriting object must contain a widget that connects at mimimum
        to this method, eg an eventbox, tree, ...
        """
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval in (_LEFT,) and (
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

    def _set_label(self, show_image=True):
        """
        Updates the label based of if the tab contains information. Tabs
        without information will not have an icon, and the text will not
        be bold. Tabs that contain data will have their icon displayed and
        the label text will be in bold face.
        """
        if not self.is_empty():
            if show_image:
                self.tab_image.show()
            else:
                self.tab_image.hide()
            self.label.set_text("<b>%s</b>" % self.tab_name)
            self.label.set_use_markup(True)
        else:
            self.tab_image.hide()
            self.label.set_text(self.tab_name)
        self.label.set_use_underline(True)

    def build_interface(self):
        """
        Builds the interface for the derived class. This function should be
        overridden in the derived class. Since the classes are derived from
        Gtk.Box, the self.pack_start, self.pack_end, and self.add functions
        can be used to add widgets to the interface.
        """
        pass

    def set_parent_notebook(self, book):
        self.parent_notebook = book
        self.track_ref_for_deletion("parent_notebook")

    def next_page(self):
        if self.parent_notebook:
            self.parent_notebook.next_page()

    def prev_page(self):
        if self.parent_notebook:
            self.parent_notebook.prev_page()

    def track_ref_for_deletion(self, ref):
        """
        Record references of instance variables that need to be removed
        from scope so that the class can be garbage collected
        """
        if ref not in self.__refs_for_deletion:
            self.__refs_for_deletion.append(ref)

    def clean_up(self):
        """
        Remove any instance variables from scope which point to non-glade
        GTK objects so that the class can be garbage collected.
        """
        while len(self.__refs_for_deletion):
            attr = self.__refs_for_deletion.pop()
            delattr(self, attr)
