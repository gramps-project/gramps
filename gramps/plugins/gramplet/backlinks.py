# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
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

    def init(self):
        self.date_column = None
        self.evts = False
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.TreeView()
        titles = [
            (_("Type"), 1, 100),
            (_("Name"), 2, 100),
            (_("Date"), 4, 200),
            ("sd", 4, 120),  # sorted date column
            ("", 5, 1),  # hidden column for the handle
            ("", 6, 1),  # hidden column for non-localized object type
        ]
        self.model = ListModel(self.top, titles, event_func=self.cb_double_click)
        self.date_column = self.top.get_column(2)
        self.sdate = self.top.get_column(3)
        self.top.get_column(1).set_expand(True)  # The name use the max
        # possible size
        return self.top

    def display_backlinks(self, active_handle):
        """
        Display the back references for an object.
        """
        self.evts = False
        sdcolumn = None
        for classname, handle in self.dbstate.db.find_backlink_handles(active_handle):
            name = navigation_label(self.dbstate.db, classname, handle)[0]
            sdcolumn = self.top.get_column(3)
            dcolumn = self.top.get_column(2)
            if classname == "Event":
                obj = self.dbstate.db.get_event_from_handle(handle)
                o_date = obj.get_date_object()
                date = displayer.display(o_date)
                sdate = "%09d" % o_date.get_sort_value()
                sdcolumn.set_sort_column_id(3)
                dcolumn.set_sort_column_id(3)
                self.evts = True
            else:
                sdcolumn.set_sort_column_id(1)
                date = sdate = ""
            self.model.add((_(classname), name, date, sdate, handle, classname))
        if self.evts:
            self.date_column.set_visible(True)
            sdcolumn.set_visible(False)
        else:
            self.date_column.set_visible(False)
            if sdcolumn:
                sdcolumn.set_visible(False)
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


class PersonBacklinks(Backlinks):
    """
    Displays the back references for a person.
    """

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active("Person")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Person")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class EventBacklinks(Backlinks):
    """
    Displays the back references for an event.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Event", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Event")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Event")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class FamilyBacklinks(Backlinks):
    """
    Displays the back references for a family.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Family", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Family")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Family")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class PlaceBacklinks(Backlinks):
    """
    Displays the back references for a place.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Place", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Place")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Place")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class SourceBacklinks(Backlinks):
    """
    Displays the back references for a source,.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Source", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Source")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Source")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class CitationBacklinks(Backlinks):
    """
    Displays the back references for a Citation,.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Citation", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Citation")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Citation")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class RepositoryBacklinks(Backlinks):
    """
    Displays the back references for a repository.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Repository", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Repository")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Repository")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class MediaBacklinks(Backlinks):
    """
    Displays the back references for a media object.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Media", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Media")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Media")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)


class NoteBacklinks(Backlinks):
    """
    Displays the back references for a note.
    """

    def db_changed(self):
        super().db_changed()
        self.connect_signal("Note", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Note")
        self.set_has_data(self.get_has_data(active_handle))

    def main(self):
        active_handle = self.get_active("Note")
        self.model.clear()
        if active_handle:
            self.display_backlinks(active_handle)
        else:
            self.set_has_data(False)
