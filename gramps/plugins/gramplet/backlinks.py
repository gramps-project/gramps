# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2024-2025  Steve Youngs
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
# python
#
# -------------------------------------------------------------------------
import pickle

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.clipboard import obj2icon, obj2target
from gramps.gui.ddtargets import DdTargets
from gramps.gen.lib.datebase import DateBase
from gramps.gui.listmodel import ListModel
from gramps.gen.utils.db import navigation_label
from gramps.gen.plug import Gramplet
from gramps.gui.utils import edit_object
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.datehandler import displayer

_ = glocale.translation.gettext


class Backlinks(Gramplet):
    """
    Displays the back references for an object.
    """

    __obj2target = {
        "Person": DdTargets.PERSON_LINK,
        "Family": DdTargets.FAMILY_LINK,
        "Event": DdTargets.EVENT,
        "Citation": DdTargets.CITATION_LINK,
        "Source": DdTargets.SOURCE_LINK,
        "Place": DdTargets.PLACE_LINK,
        "Repository": DdTargets.REPO_LINK,
        "Media": DdTargets.MEDIAOBJ,
        "Note": DdTargets.NOTE_LINK,
    }

    def __init__(self, classname, gui, nav_group=0):
        self.__classname = classname  # must be set before calling super().__init__
        super().__init__(gui, nav_group)

    def init(self):
        self.date_column = None
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.TreeView()
        self.top.get_selection().connect("changed", self.selection_changed)
        self.top.connect_after("drag-begin", self.drag_begin)
        self.top.connect("drag_data_get", self.drag_data_get)

        titles = [
            (_("Type"), 1, 100),
            (_("Name"), 2, 100),
            (_("Date"), 4, 200),
            ("date_sort_value", 4, 1),  # hidden column
            ("", 5, 1),  # hidden column for the handle
            ("", 6, 1),  # hidden column for non-localized object type
        ]
        self.model = ListModel(
            self.top,
            titles,
            event_func=self.cb_double_click,
            middle_click=self.cb_middle_click,
            right_click=self.cb_right_click,
        )

        self.date_column = self.top.get_column(2)
        self.date_column.set_visible(False)
        self.date_column.set_sort_column_id(3)
        self.top.get_column(1).set_expand(
            True
        )  # Expand the Name column as far as possible
        self.top.get_column(3).set_visible(
            False
        )  # always hide the date_sort_value column
        # possible size
        return self.top

    def selection_changed(self, selection):
        """
        Called when the selection is changed in the TreeView.
        """
        target = None
        (model, iter_) = selection.get_selected()
        if iter_:
            objclass = model.get_value(iter_, 5)
            target = self.__obj2target.get(objclass)

        if target:
            self.top.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, [target.target()], Gdk.DragAction.COPY
            )
        else:
            self.top.drag_source_unset()

    def drag_begin(self, widget, drag_context):
        """
        We want to show the icon during drag instead of the long row entry
        """
        (model, iter_) = self.top.get_selection().get_selected()
        if not iter_:
            return

        objclass = model.get_value(iter_, 5)
        Gtk.drag_set_icon_name(drag_context, obj2icon(objclass.lower()), 0, 0)

    def drag_data_get(self, widget, context, sel_data, info, time):
        # get the selected object, returning if nothing is selected
        (model, iter_) = self.top.get_selection().get_selected()
        if not iter_:
            return

        (objclass, handle) = (model.get_value(iter_, 5), model.get_value(iter_, 4))

        target = obj2target(objclass)
        data = (target.name(), id(self), handle, 0)

        sel_data.set(target, 8, pickle.dumps(data))

    def display_backlinks(self, active_handle):
        """
        Display the back references for an object.
        """
        have_dates = False  # True if any of the objects we are displaying are instances of DateBase
        for classname, handle in self.dbstate.db.find_backlink_handles(active_handle):
            name = navigation_label(self.dbstate.db, classname, handle)[0]
            obj = self.dbstate.db.method("get_%s_from_handle", classname)(handle)
            if isinstance(obj, DateBase):
                o_date = obj.get_date_object()
                date = displayer.display(o_date)
                date_sort_value = "%09d" % o_date.get_sort_value()
                have_dates = True
            else:
                date = date_sort_value = ""
            self.model.add(
                (_(classname), name, date, date_sort_value, handle, classname)
            )

        self.date_column.set_visible(
            have_dates
        )  # only show the Date column if there are some values
        self.set_has_data(self.model.count > 0)

    def get_has_data(self, active_handle):
        """
        Return True if the gramplet has data, else return False.
        """
        if not active_handle:
            return False
        for handle in self.dbstate.db.find_backlink_handles(active_handle):
            return True
        return False

    def cb_double_click(self, treeview):
        """
        Handle double click on treeview.
        """
        (model, iter_) = treeview.get_selection().get_selected()
        if not iter_:
            return

        (objclass, handle) = (model.get_value(iter_, 5), model.get_value(iter_, 4))

        edit_object(self.dbstate, self.uistate, objclass, handle)

    def cb_middle_click(self, treeview, event):
        """
        Handle middle click on view.
        """
        (model, iter_) = treeview.get_selection().get_selected()
        if not iter_:
            return

        (objclass, handle) = (model.get_value(iter_, 5), model.get_value(iter_, 4))
        self.uistate.set_active(handle, objclass)

    def cb_right_click(self, treeview, event):
        """
        Handle right click on view.
        """
        (model, iter_) = self.top.get_selection().get_selected()
        if not iter_:
            return  # nothing selected, so do not display the context menu

        (objclass, handle) = (model.get_value(iter_, 5), model.get_value(iter_, 4))

        self.__store_menu = Gtk.Menu()  # need to keep reference or menu disappears
        menu = self.__store_menu

        item = Gtk.MenuItem.new_with_mnemonic(_("_Edit"))
        item.connect(
            "activate",
            lambda obj: edit_object(self.dbstate, self.uistate, objclass, handle),
        )
        item.show()
        menu.append(item)

        item = Gtk.MenuItem.new_with_mnemonic(_("_Make Active %s") % objclass)
        item.connect("activate", lambda obj: self.uistate.set_active(handle, objclass))
        item.show()
        menu.append(item)

        menu.popup_at_pointer(event)
        return True

    def db_changed(self):
        for item in [
            "person",
            "family",
            "source",
            "citation",
            "event",
            "media",
            "place",
            "repository",
            "note",
        ]:
            self.connect(self.dbstate.db, "%s-delete" % item, self.update)
            self.connect(self.dbstate.db, "%s-add" % item, self.update)
            self.connect(self.dbstate.db, "%s-update" % item, self.update)
        if self.__classname != "Person":
            # the Gramplet super class already connects to changes in
            # active person and calls active_changed
            self.connect_signal(self.__classname, self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active(self.__classname)
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active(self.__classname)
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class PersonBacklinks(Backlinks):
    """
    Displays the back references for a person.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Person", gui, nav_group)


class EventBacklinks(Backlinks):
    """
    Displays the back references for an event.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Event", gui, nav_group)


class FamilyBacklinks(Backlinks):
    """
    Displays the back references for a family.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Family", gui, nav_group)


class PlaceBacklinks(Backlinks):
    """
    Displays the back references for a place.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Place", gui, nav_group)


class SourceBacklinks(Backlinks):
    """
    Displays the back references for a source.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Source", gui, nav_group)


class CitationBacklinks(Backlinks):
    """
    Displays the back references for a Citation.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Citation", gui, nav_group)


class RepositoryBacklinks(Backlinks):
    """
    Displays the back references for a repository.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Repository", gui, nav_group)


class MediaBacklinks(Backlinks):
    """
    Displays the back references for a media object.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Media", gui, nav_group)


class NoteBacklinks(Backlinks):
    """
    Displays the back references for a note.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Note", gui, nav_group)
