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
        adj = Gtk.Adjustment(value=0, lower=0, upper=300,
                             step_increment=1, page_increment=10, page_size=10)
        # default value is 50.0, minimum is 10.0 and max is 300.0
        self.slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                                adjustment=adj)
        self.slider.connect('value-changed', self.slider_change)
        self.pack_start(self.slider, True, True, 0)
        self.unit = Gtk.ComboBoxText()
        list(map(self.unit.append_text,
            [ _('kilometers'), _('miles'), _('degrees') ]))
        self.unit.set_active(0)
        self.pack_start(self.unit, False, True, 0)
        self.show_all()

    def get_value(self):
        return self.slider.get_value(), self.unit.get_active()

    def set_value(self, value, unit):
        self.slider.set_value(int(value))
        self.unit.set_active(int(unit))

    def slider_change(self, value):
        _db = self.dbstate.db
        active_reference = self.uistate.get_active('Place')
        place_name = None
        if active_reference:
            place = _db.get_place_from_handle(active_reference)
            place_name = _pd.display(self.dbstate.db, place)
        if place_name is None:
            self.set_tooltip_text(_('You have no active place'))
        else:
            self.set_tooltip_text(place_name)
