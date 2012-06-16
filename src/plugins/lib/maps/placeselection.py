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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _
import re
import gobject
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
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gen.errors import WindowActiveError
from gui.managedwindow import ManagedWindow
from osmGps import OsmGps

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
            self.get_location(entry[9])
            if not [self.country, self.state, self.county] in self.places:
                self.places.append([self.country, self.state, self.county])
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
            ManagedWindow.__init__(self, uistate, [],
                                                 PlaceSelection)
        except WindowActiveError:
            return
        self.uistate = uistate
        self.dbstate = dbstate
        self.lat = lat
        self.lon = lon
        self.osm = maps
        self.country = None
        self.state = None
        self.county = None
        self.radius = 1.0
        self.circle = None
        self.oldvalue = oldvalue
        self.place_list = places
        self.function = function
        self.selection_layer = layer
        self.layer = layer
        alignment = gtk.Alignment(0, 1, 0, 0)
        self.set_window(
            gtk.Dialog(_('Place Selection in a region'),
                       flags=gtk.DIALOG_NO_SEPARATOR,
                       buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
            None, _('Place Selection in a region'), None)
        label = gtk.Label(_('Choose the radius of the selection.\n'
                            'On the map you should see a circle or an'
                            ' oval depending on the latitude.'))
        alignment.add(label)
        self.window.vbox.pack_start(alignment, expand=False)
        adj = gtk.Adjustment(1.0, 0.1, 3.0, 0.1, 0, 0)
        # default value is 1.0, minimum is 0.1 and max is 3.0
        slider = gtk.HScale(adj)
        slider.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        slider.set_digits(1)
        slider.set_value_pos(gtk.POS_BOTTOM)
        slider.connect('value-changed', self.slider_change, self.lat, self.lon)
        self.window.vbox.pack_start(slider, expand=False)
        self.vadjust = gtk.Adjustment(page_size=15)
        self.scroll = gtk.ScrolledWindow(self.vadjust)
        self.scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.scroll.set_shadow_type(gtk.SHADOW_IN)
        self.plist = gtk.ListStore(str, str, str)
        self.choices = gtk.TreeView(self.plist)
        self.scroll.add(self.choices)
        self.renderer = gtk.CellRendererText()
        self.tvcol1 = gtk.TreeViewColumn(_('Country'), self.renderer, markup=0)
        self.tvcol2 = gtk.TreeViewColumn(_('State'), self.renderer, markup=1)
        self.tvcol3 = gtk.TreeViewColumn(_('County'), self.renderer, markup=2)
        self.tvcol1.set_sort_column_id(0)
        self.tvcol2.set_sort_column_id(1)
        self.tvcol3.set_sort_column_id(2)
        self.choices.append_column(self.tvcol1)
        self.choices.append_column(self.tvcol2)
        self.choices.append_column(self.tvcol3)
        self.window.vbox.pack_start(self.scroll, expand=True)
        self.label2 = gtk.Label()
        self.label2.set_markup('<span background="green" foreground="black"'
                               '>%s</span>' % 
             _('The green values in the row correspond '
               'to the current place values.'))
        alignment = gtk.Alignment(0, 1, 0, 0)
        alignment.add(self.label2)
        self.window.vbox.pack_start(alignment, expand=False)
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
            field1, field2, field3 = self.oldvalue
            self.plist.append((PLACE_STRING % field1,
                               PLACE_STRING % field2,
                               PLACE_STRING % field3)
                             )
        for place in self.places:
            self.plist.append(place)
        # here, we could add value from geography names services ...

        # if we found no place, we must create a default place.
        self.plist.append((_("New place with empty fields"), "", "..."))

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
        self.selection_layer.add_circle(rds, self.lat, self.lon)

    def get_location(self, place):
        """
        get location values
        """
        place = self.dbstate.db.get_place_from_gramps_id(place)
        loc = place.get_main_location()
        data = loc.get_text_data_list()
        # new background or font color on gtk fields ?
        self.country = data[6]
        self.state = data[5]
        self.county = data[4]
        return(self.country, self.state, self.county)

    def selection(self, obj, index, column, function):
        """
        get location values and call the real function : add_place, edit_place
        """
        if self.plist[index][2] == "...":
            # case with blank values ( New place with empty fields )
            self.function( "", "", "", self.lat, self.lon)
        elif self.plist[index][0][1:5] == "span":
            # case with old values ( keep the old values of the place )
            name = PLACE_REGEXP.search(self.plist[index][0], 0)
            country = name.group(1)
            name = PLACE_REGEXP.search(self.plist[index][1], 0)
            state = name.group(1)
            name = PLACE_REGEXP.search(self.plist[index][2], 0)
            county = name.group(1)
            self.function( country, county, state, self.lat, self.lon)
        else:
            # Set the new values of the country, county and state fields.
            self.function( self.plist[index][0], self.plist[index][2],
                           self.plist[index][1], self.lat, self.lon)

