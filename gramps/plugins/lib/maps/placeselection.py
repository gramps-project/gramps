# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011-2012       Serge Noiraud
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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
import re
from gi.repository import GObject
import math

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.placeselection")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.errors import WindowActiveError
from gramps.gui.managedwindow import ManagedWindow
from .osmgps import OsmGps
from gramps.gen.utils.location import get_main_location
from gramps.gen.lib import PlaceType

#-------------------------------------------------------------------------
#
# Functions and variables
#
#-------------------------------------------------------------------------
PLACE_REGEXP = re.compile('<span background="green">(.*)</span>')
PLACE_STRING = '<span background="green">%s</span>'

def match(self, lat, lon, radius):
    """
    coordinates matching.
    """
    rds = float(radius)
    self.places = []

    # place
    for entry in self.place_list:
        if (math.hypot(lat-float(entry[3]),
                       lon-float(entry[4])) <= rds) == True:
            # Do we already have this place ? avoid duplicates
            country, state, county, place = self.get_location(entry[9])
            if not [country, state, county, place] in self.places:
                self.places.append([country, state, county, place])
    return self.places

#-------------------------------------------------------------------------
#
# PlaceSelection
#
#-------------------------------------------------------------------------
class PlaceSelection(ManagedWindow, OsmGps):
    """
    We show a selection box for possible places in a region of the map.
    We can select the diameter of the region which is a circle.
    Depending of this region, we can show the possible choice.
    We select the value depending of our need which open the EditPlace box.
    """
    def __init__(self, uistate, dbstate, maps, layer, places, lat, lon,
                 function, oldvalue=None):
        """
        Place Selection initialization
        """
        try:
            ManagedWindow.__init__(self, uistate, [], PlaceSelection)
        except WindowActiveError:
            return
        self.uistate = uistate
        self.dbstate = dbstate
        self.lat = lat
        self.lon = lon
        self.osm = maps
        self.radius = 1.0
        self.circle = None
        self.oldvalue = oldvalue
        self.place_list = places
        self.function = function
        self.selection_layer = layer
        self.layer = layer
        self.set_window(
            Gtk.Dialog(_('Place Selection in a region'),
                       buttons=(_('_Close'), Gtk.ResponseType.CLOSE)),
            None, _('Place Selection in a region'), None)
        label = Gtk.Label(label=_('Choose the radius of the selection.\n'
                            'On the map you should see a circle or an'
                            ' oval depending on the latitude.'))
        label.set_valign(Gtk.Align.END)
        self.window.vbox.pack_start(label, False, True, 0)
        adj = Gtk.Adjustment(value=1.0, lower=0.1, upper=3.0,
                             step_increment=0.1, page_increment=0, page_size=0)
        # default value is 1.0, minimum is 0.1 and max is 3.0
        slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                           adjustment=adj)
        slider.set_digits(1)
        slider.set_value_pos(Gtk.PositionType.BOTTOM)
        slider.connect('value-changed', self.slider_change, self.lat, self.lon)
        self.window.vbox.pack_start(slider, False, True, 0)
        self.vadjust = Gtk.Adjustment(page_size=15)
        self.scroll = Gtk.ScrolledWindow(self.vadjust)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_shadow_type(Gtk.ShadowType.IN)
        self.plist = Gtk.ListStore(str, str, str, str)
        self.choices = Gtk.TreeView(self.plist)
        self.scroll.add(self.choices)
        self.renderer = Gtk.CellRendererText()
        self.tvcol1 = Gtk.TreeViewColumn(_('Country'), self.renderer, markup=0)
        self.tvcol2 = Gtk.TreeViewColumn(_('State'), self.renderer, markup=1)
        self.tvcol3 = Gtk.TreeViewColumn(_('County'), self.renderer, markup=2)
        self.tvcol1.set_sort_column_id(0)
        self.tvcol2.set_sort_column_id(1)
        self.tvcol3.set_sort_column_id(2)
        self.choices.append_column(self.tvcol1)
        self.choices.append_column(self.tvcol2)
        self.choices.append_column(self.tvcol3)
        self.window.vbox.pack_start(self.scroll, True, True, 0)
        self.label2 = Gtk.Label()
        self.label2.set_markup('<span background="green" foreground="black"'
                               '>%s</span>' %
             _('The green values in the row correspond '
               'to the current place values.'))
        self.label2.set_valign(Gtk.Align.END)
        self.window.vbox.pack_start(self.label2, False, True, 0)
        self.window.set_default_size(400, 300)
        self.choices.connect('row-activated', self.selection, function)
        self.window.connect('response', self.close)
        self.window.show_all()
        self.show()
        self.label2.hide()
        self.slider_change(None, lat, lon)

    def close(self, *obj):
        """
        Close the selection place editor
        """
        self.hide_the_region()
        ManagedWindow.close(self, *obj)

    def slider_change(self, obj, lat, lon):
        """
        Display on the map a circle in which we select all the places inside this region.
        """
        self.radius = obj.get_value() if obj else 1.0
        self.show_the_region(self.radius)
        match(self, lat, lon, self.radius)
        self.plist.clear()
        if self.oldvalue != None:
            # The old values are always in the first row.
            # In this case, we change the color of the row.
            # display the associated message
            self.label2.show()
            place = self.dbstate.db.get_place_from_handle(self.oldvalue)
            loc = get_main_location(self.dbstate.db, place)
            self.plist.append((PLACE_STRING % loc.get(PlaceType.COUNTRY, ''),
                               PLACE_STRING % loc.get(PlaceType.STATE, ''),
                               PLACE_STRING % loc.get(PlaceType.COUNTY, ''),
                               self.oldvalue)
                             )
        for place in self.places:
            p = (place[0].value, place[1], place[2], place[3])
            self.plist.append(p)
        # here, we could add value from geography names services ...

        # if we found no place, we must create a default place.
        self.plist.append((_("New place with empty fields"), "", "...", None))

    def hide_the_region(self):
        """
        Hide the layer which contains the circle
        """
        layer = self.get_selection_layer()
        if layer:
            self.remove_layer(layer)

    def show_the_region(self, rds):
        """
        Show a circle in which we select the places.
        """
        # circle (rds)
        self.hide_the_region()
        self.selection_layer = self.add_selection_layer()
        self.selection_layer.add_circle(rds/2.0, self.lat, self.lon)

    def get_location(self, gramps_id):
        """
        get location values
        """
        parent_place = None
        country = state = county = ''
        place = self.dbstate.db.get_place_from_gramps_id(gramps_id)
        place_name = place.name.get_value()
        parent_list = place.get_placeref_list()
        while len(parent_list) > 0:
            place = self.dbstate.db.get_place_from_handle(parent_list[0].ref)
            parent_list = place.get_placeref_list()
            if int(place.get_type()) == PlaceType.COUNTY:
                county = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
            elif int(place.get_type()) == PlaceType.STATE:
                state = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
            elif int(place.get_type()) == PlaceType.COUNTRY:
                country = place.name
                if parent_place is None:
                    parent_place = place.get_handle()
        return(country, state, county, place_name)

    def selection(self, obj, index, column, function):
        """
        get location values and call the real function : add_place, edit_place
        """
        self.function(self.plist[index][3], self.lat, self.lon)
