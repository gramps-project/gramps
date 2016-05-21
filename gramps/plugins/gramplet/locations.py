# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014-2016 Nick Hall
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.dbguielement import DbGUIElement
from gramps.gui.editors import EditPlace
from gramps.gen.errors import WindowActiveError
from gramps.gui.listmodel import ListModel, NOSORT
from gramps.gen.datehandler import get_date
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Locations gramplet
#
#-------------------------------------------------------------------------
class Locations(Gramplet, DbGUIElement):
    """
    Gramplet showing the locations of a place over time.
    """
    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        DbGUIElement.__init__(self, self.dbstate.db)

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        self.callman.register_callbacks({'place-update': self.changed})
        self.callman.connect_all(keys=['place'])

    def db_changed(self):
        self.connect_signal('Place', self.update)

    def changed(self, handle):
        """
        Called when a registered place is updated.
        """
        self.update()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a row to edit the selected place.')
        self.set_tooltip(tip)
        top = Gtk.TreeView()
        titles = [('', 0, 50),
                  (_('Name'), 1, 300),
                  (_('Type'), 2, 150),
                  (_('Date'), 4, 150),
                  ('', NOSORT, 50)]
        self.model = ListModel(top, titles, list_mode="tree",
                               event_func=self.edit_place)
        return top

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Place')
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def get_has_data(self, place):
        """
        Return True if the gramplet has data, else return False.
        """
        pass

    def main(self):
        self.model.clear()
        self.callman.unregister_all()
        active_handle = self.get_active('Place')
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            if active:
                self.display_place(active, None, [active_handle])
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_place(self, place, node, visited):
        """
        Display the location hierarchy for the active place.
        """
        pass

    def add_place(self, placeref, place, node, visited):
        """
        Add a place to the model.
        """
        place_date = get_date(placeref)
        place_sort = '%012d' % placeref.get_date_object().get_sort_value()
        place_name = place.get_name().get_value()
        place_type = str(place.get_type())

        new_node = self.model.add([place.handle,
                                   place_name,
                                   place_type,
                                   place_date,
                                   place_sort],
                                  node=node)

        self.display_place(place, new_node, visited + [place.handle])

    def edit_place(self, treeview):
        """
        Edit the selected place.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            place = self.dbstate.db.get_place_from_handle(handle)
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except WindowActiveError:
                pass

#-------------------------------------------------------------------------
#
# EnclosedBy gramplet
#
#-------------------------------------------------------------------------
class EnclosedBy(Locations):

    def display_place(self, place, node, visited):
        """
        Display the location hierarchy for the active place.
        """
        self.callman.register_obj(place)
        for placeref in place.get_placeref_list():
            if placeref.ref in visited:
                continue

            parent_place = self.dbstate.db.get_place_from_handle(placeref.ref)
            self.add_place(placeref, parent_place, node, visited)

        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, place):
        """
        Return True if the gramplet has data, else return False.
        """
        if place is None:
            return False
        if len(place.get_placeref_list()) > 0:
            return True
        return False

#-------------------------------------------------------------------------
#
# Encloses gramplet
#
#-------------------------------------------------------------------------
class Encloses(Locations):

    def display_place(self, place, node, visited):
        """
        Display the location hierarchy for the active place.
        """
        self.callman.register_obj(place)
        for link in self.dbstate.db.find_backlink_handles(
                place.handle, include_classes=['Place']):
            if link[1] in visited:
                continue

            child_place = self.dbstate.db.get_place_from_handle(link[1])
            placeref = None
            for placeref in child_place.get_placeref_list():
                if placeref.ref == place.handle:
                    self.add_place(placeref, child_place, node, visited)

        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, place):
        """
        Return True if the gramplet has data, else return False.
        """
        if place is None:
            return False
        for link in self.dbstate.db.find_backlink_handles(
                place.handle, include_classes=['Place']):
            return True
        return False
