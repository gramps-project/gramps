#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015        Nick Hall
# Copyright (C) 2017-       Serge Noiraud
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

__all__ = ["PlaceWithin"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.placewithin")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..selectors import SelectorFactory
from gramps.gen.display.place import displayer as _pd
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PlaceWithin class
#
#-------------------------------------------------------------------------
class PlaceWithin(Gtk.Box):

    def __init__(self, dbstate, uistate, track):
        Gtk.Box.__init__(self)
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.last = ""
        # initial tooltip when no place already selected.
        self.tooltip = _('Matches places within a given distance'
                         ' of the active place. You have no active place.')
        self.set_tooltip_text(self.tooltip)
        self.entry = Gtk.Entry()
        self.entry.set_max_length(3)
        self.entry.set_width_chars(5)
        self.entry.connect('changed', self.entry_change)
        self.pack_start(self.entry, True, True, 0)
        self.unit = Gtk.ComboBoxText()
        list(map(self.unit.append_text,
            [ _('kilometers'), _('miles'), _('degrees') ]))
        self.unit.set_active(0)
        self.pack_start(self.unit, False, True, 0)
        self.show_all()

    def get_value(self):
        value = self.entry.get_text()
        if value == "":
            value = "0"
        return int(value), self.unit.get_active()

    def set_value(self, value, unit):
        self.entry.set_text(str(value))
        self.unit.set_active(int(unit))

    def entry_change(self, entry):
        value = entry.get_text()
        if value.isnumeric() or value == "":
            self.last = value # This entry is numeric and valid.
        else:
            entry.set_text(self.last) # reset to the last valid entry
        _db = self.dbstate.db
        active_reference = self.uistate.get_active('Place')
        place_name = None
        if active_reference:
            place = _db.get_place_from_handle(active_reference)
            place_name = _pd.display(self.dbstate.db, place)
        if place_name is None:
            self.set_tooltip_text(self.tooltip)
        else:
            self.set_tooltip_text(place_name)
