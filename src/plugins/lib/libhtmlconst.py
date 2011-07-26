# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007       Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2011  Rob G. Healey <robhealey1@gmail.com>
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

"""
General constants used in different html enabled plugins
"""

from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

_CHARACTER_SETS = [
    # First is used as default selection.
    # As seen on the internet, ISO-xxx are listed as capital letters
    [_('Unicode UTF-8 (recommended)'), 'UTF-8'],
    ['ISO-8859-1',  'ISO-8859-1' ],
    ['ISO-8859-2',  'ISO-8859-2' ],
    ['ISO-8859-3',  'ISO-8859-3' ],
    ['ISO-8859-4',  'ISO-8859-4' ],
    ['ISO-8859-5',  'ISO-8859-5' ],
    ['ISO-8859-6',  'ISO-8859-6' ],
    ['ISO-8859-7',  'ISO-8859-7' ],
    ['ISO-8859-8',  'ISO-8859-8' ],
    ['ISO-8859-9',  'ISO-8859-9' ],
    ['ISO-8859-10', 'ISO-8859-10' ],
    ['ISO-8859-13', 'ISO-8859-13' ],
    ['ISO-8859-14', 'ISO-8859-14' ],
    ['ISO-8859-15', 'ISO-8859-15' ],
    ['koi8_r',      'koi8_r',     ],
    ]

_CC = [
    '',

    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" '
    'title="Creative Commons License - By attribution" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, '
    'No derivations" '
    'title="Creative Commons License - By attribution, Non-commercial, '
    'No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, '
    'Share-alike" '
    'title="Creative Commons License - By attribution, Non-commerical, '
    'Share-alike" '
    'src="%(gif_fname)s" /></a>'
    ]

_COPY_OPTIONS = [
        _('Standard copyright'),

        # This must match _CC
        # translators, long strings, have a look at Web report dialogs
        _('Creative Commons - By attribution'),
        _('Creative Commons - By attribution, No derivations'),
        _('Creative Commons - By attribution, Share-alike'),
        _('Creative Commons - By attribution, Non-commercial'),
        _('Creative Commons - By attribution, Non-commercial, No derivations'),
        _('Creative Commons - By attribution, Non-commercial, Share-alike'),

        _('No copyright notice'),
        ]

# NarrativeWeb javascript code for PlacePage's "Open Street Map"...
openstreet_jsc = """
OpenLayers.Lang.setCode("%s");

function initialize() {
    map = new OpenLayers.Map("map_canvas");
    var osm = new OpenLayers.Layer.OSM()
    map.addLayer(osm);

    var lonLat = new OpenLayers.LonLat(%s, %s)
        .transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
        );
    var zoom =16;
    map.setCenter(lonLat, zoom);
 
    var markers = new OpenLayers.Layer.Markers("Markers");
    markers.addMarker(new OpenLayers.Marker(lonLat));
    map.addLayer(markers);

    // add overview control
    map.addControl(new OpenLayers.Control.OverviewMap());

    // add a layer switcher
    map.addControl(new OpenLayers.Control.LayerSwitcher());
}"""

# NarrativeWeb javascript code for PlacePage's "Google Maps"...
google_jsc = """
  var myLatlng = new google.maps.LatLng(%s, %s);
    var marker;
    var map;

    function initialize() {
        var mapOptions = {
            zoom: 13,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            center: myLatlng
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
          
        marker = new google.maps.Marker({
            map:       map,
            draggable: true,
            animation: google.maps.Animation.DROP,
            position:  myLatlng
        });

        google.maps.event.addListener(marker, 'click', toggleBounce);
    }

    function toggleBounce() {

        if (marker.getAnimation() != null) {
            marker.setAnimation(null);
        } else {
            marker.setAnimation(google.maps.Animation.BOUNCE);
        }
    }"""
