# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010-      Serge Noiraud
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

"""
Narrative Web Page generator.

This module is used to share variables, enums and functions between all modules

"""

from collections import defaultdict
from hashlib import md5
import re
import logging
from xml.sax.saxutils import escape

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.db import get_death_or_fallback
from gramps.gen.lib import EventType, Date
from gramps.gen.plug import BasePluginManager
from gramps.plugins.lib.libgedcom import make_gedcom_date, DATE_QUALITY
from gramps.gen.plug.report import utils
from gramps.plugins.lib.libhtml import Html

HAVE_ICU = False
HAVE_ALPHABETICINDEX = False  # separate check as this is only in ICU 4.6+
try:
    from icu import Locale

    HAVE_ICU = True
    try:
        from icu import AlphabeticIndex as icuAlphabeticIndex

        HAVE_ALPHABETICINDEX = True
    except ImportError:
        from gramps.plugins.webreport.alphabeticindex import (
            AlphabeticIndex as localAlphabeticIndex,
        )
except ImportError:
    try:
        from PyICU import Locale

        HAVE_ICU = True
        try:
            from PyICU import AlphabeticIndex as icuAlphabeticIndex

            HAVE_ALPHABETICINDEX = True
        except ImportError:
            from gramps.plugins.webreport.alphabeticindex import (
                AlphabeticIndex as localAlphabeticIndex,
            )
    except ImportError:
        pass

LOG = logging.getLogger(".NarrativeWeb")

# define clear blank line for proper styling
FULLCLEAR = Html("div", class_="fullclear", inline=True)
# define all possible web page filename extensions
_WEB_EXT = [".html", ".htm", ".shtml", ".php", ".cgi"]
# used to select secured web site or not
HTTP = "http://"
HTTPS = "https://"

GOOGLE_MAPS = "https://maps.googleapis.com/maps/"
# javascript code for marker path
MARKER_PATH = """
  var marker_png = '%s';
"""

# javascript code for Google's FamilyLinks...
FAMILYLINKS = """
  var tracelife = %s;

  window.addEventListener("load", function() {
    var myLatLng = new google.maps.LatLng(%s, %s);

    var mapOptions = {
      scaleControl:    true,
      panControl:      true,
      backgroundColor: '#000000',
      zoom:            %d,
      center:          myLatLng,
      mapTypeId:       google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"),
                                  mapOptions);

    var flightPath = new google.maps.Polyline({
      path:          tracelife,
      strokeColor:   "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight:  2
    });

   flightPath.setMap(map);
  });
"""

# javascript for Google's Drop Markers...
DROPMASTERS = """
  var markers = [];
  var iterator = 0;

  var tracelife = %s;
  var map;
  var myLatLng = new google.maps.LatLng(%s, %s);

  window.addEventListener("load", function() {
    var mapOptions = {
      scaleControl: true,
      zoomControl:  true,
      zoom:         %d,
      mapTypeId:    google.maps.MapTypeId.ROADMAP,
      center:       myLatLng,
    };
    map = new google.maps.Map(document.getElementById("map_canvas"),
                              mapOptions);
  });

  function drop() {
    for (var i = 0; i < tracelife.length; i++) {
      setTimeout(function() {
        addMarker();
      }, i * 1000);
    }
  }

  function addMarker() {
    var location = tracelife[iterator];
    var myLatLng = new google.maps.LatLng(location[1], location[2]);
    var infoWindow = new google.maps.InfoWindow;

    var marker = new google.maps.Marker({
      position:  myLatLng,
      map:       map,
      draggable: true,
      title:     location[0],
      animation: google.maps.Animation.DROP
    });
    markers.push(marker);
    iterator++;
    var title = "<h2>" + location[0] + "</h2>"
    bindInfoWindow(marker, map, infoWindow, title+location[4]);
  }
  function bindInfoWindow(marker, map, infoWindow, html) {
          google.maps.event.addListener(marker, 'click', function() {
              infoWindow.setContent(html);
              infoWindow.open(map, marker);
          });
  }
"""

# javascript for Google's Markers...
MARKERS = """
  var tracelife = %s;
  var map;
  var myLatLng = new google.maps.LatLng(%s, %s);

  window.addEventListener("load", function() {
    var mapOptions = {
      scaleControl:    true,
      panControl:      true,
      backgroundColor: '#000000',
      zoom:            %d,
      center:          myLatLng,
      mapTypeId:       google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"),
                              mapOptions);
    addMarkers();
  });

  function addMarkers() {
    var bounds = new google.maps.LatLngBounds();
    var infoWindow = new google.maps.InfoWindow;

    for (var i = 0; i < tracelife.length; i++) {
      var location = tracelife[i];
      var myLatLng = new google.maps.LatLng(location[1], location[2]);

      var marker = new google.maps.Marker({
        position:  myLatLng,
        draggable: true,
        title:     location[0],
        map:       map,
        zIndex:    location[3]
      });
      var title = "<h2>" + location[0] + "</h2>"
      bindInfoWindow(marker, map, infoWindow, title+location[4]);
      bounds.extend(myLatLng);
      if ( i > 1 ) { map.fitBounds(bounds); };
    }
  }
  function bindInfoWindow(marker, map, infoWindow, html) {
          google.maps.event.addListener(marker, 'click', function() {
              infoWindow.setContent(html);
              infoWindow.open(map, marker);
          });
  }
"""

# javascript for OpenStreetMap's markers...
"""
https://openlayers.org/en/latest/examples/
"""

OSM_MARKERS = """
  window.addEventListener("load", function() {
    var map;
    var tracelife = %s;
    var iconStyle = new ol.style.Style({
      image: new ol.style.Icon(({
        anchor: [0.2, 48],
        anchorXUnits: 'fraction',
        anchorYUnits: 'pixels',
        opacity: 1.0,
        src: marker_png
      }))
    });
    var markerSource = new ol.source.Vector({
    });
    for (var i = 0; i < tracelife.length; i++) {
      var loc = tracelife[i];
      var iconFeature = new ol.Feature({
       geometry: new ol.geom.Point(ol.proj.transform([loc[0], loc[1]],
                                                     'EPSG:4326', 'EPSG:3857')),
       name: loc[2],
       data: loc[3],
      });
      iconFeature.setStyle(iconStyle);
      markerSource.addFeature(iconFeature);
    }
    markerLayer = new ol.layer.Vector({
      source: markerSource,
      style: iconStyle
    });
    tooltip = new ol.layer.Vector({
      source: markerSource,
      style: iconStyle
    });
    var centerCoord = new ol.proj.transform([%s, %s], 'EPSG:4326', 'EPSG:3857');
    map = new ol.Map({
                 target: 'map_canvas',
                 layers: [new ol.layer.Tile({ source: new ol.source.OSM() }),
                          markerLayer, tooltip],
                 view: new ol.View({ center: centerCoord, zoom: %d })
                 });
"""

STAMEN_MARKERS = """
  window.addEventListener("load", function() {
    var map;
    var tracelife = %s;
    var layer = '%s';
    var iconStyle = new ol.style.Style({
      image: new ol.style.Icon(({
        anchor: [0.2, 48],
        anchorXUnits: 'fraction',
        anchorYUnits: 'pixels',
        opacity: 1.0,
        src: marker_png
      }))
    });
    var markerSource = new ol.source.Vector({
    });
    for (var i = 0; i < tracelife.length; i++) {
      var loc = tracelife[i];
      var iconFeature = new ol.Feature({
       geometry: new ol.geom.Point(ol.proj.transform([loc[0], loc[1]],
                                                     'EPSG:4326', 'EPSG:3857')),
       name: loc[2],
       data: loc[3],
      });
      iconFeature.setStyle(iconStyle);
      markerSource.addFeature(iconFeature);
    }
    var centerCoord = new ol.proj.transform([%s, %s], 'EPSG:4326', 'EPSG:3857');
    markerLayer = new ol.layer.Vector({
      source: markerSource,
      style: iconStyle
    });
    tooltip = new ol.layer.Vector({
      source: markerSource,
      style: iconStyle
    });
    map = new ol.Map({
                 target: 'map_canvas',
                 layers: [
                   new ol.layer.Tile({ source: new ol.source.Stamen({
                                         layer: layer }) }),
                          markerLayer, tooltip],
                 view: new ol.View({ center: centerCoord, zoom: %d })
                 });
"""

OPENLAYER = """
    var element = document.getElementById('popup');
    var content = document.getElementById('popup-content');
    var ptitle = document.getElementById('popup-title');
    var closer = document.getElementById('popup-closer');
    var tip = document.getElementById('tooltip');
    var tipcontent = document.getElementById('tooltip-content');
    var tooltip = new ol.Overlay({
      element: tip,
      positioning: 'bottom-center',
      offset: [10, 0],
    });
    map.addOverlay(tooltip);
    var popup = new ol.Overlay({
      element: element,
      positioning: 'bottom-center',
      autoPan: true,
      autoPanAnimation: { duration: 500 },
      stopEvent: true
    });
    map.addOverlay(popup);
    /**
     * Add a click handler to hide the popup.
     * @return {boolean} Don't follow the href.
     */
    closer.onclick = function() {
      popup.setPosition(undefined);
      closer.blur();
      return false;
    };
    map.on('pointermove', function(evt) {
      evt.preventDefault()
      var feature = this.forEachFeatureAtPixel(evt.pixel,
                                               function(feature, layer) {
        return feature;
      });
      map.getTargetElement().style.cursor = feature ? 'pointer' : '';
      if (evt.dragging) {
        tooltip.setPosition(undefined);
        return;
      }
      if (feature) {
        var coordinate = evt.coordinate;
        tipcontent.innerHTML = feature.get('name');
        tooltip.setPosition(coordinate);
      } else {
        tooltip.setPosition(undefined);
      }
    });
    map.on('singleclick', function(evt) {
      evt.preventDefault();
      var feature = map.forEachFeatureAtPixel(evt.pixel,
                                              function(feature, layer) {
        return feature;
      });
      if (feature) {
      var coordinate = evt.coordinate;
      var title = '<h2>' + feature.get('name') + '</h2>';
      ptitle.innerHTML = title;
      content.innerHTML = feature.get('data');
      popup.setPosition(coordinate);
      }
      });
  });
"""

# variables for alphabet_navigation()
_KEYPERSON, _KEYPLACE, _KEYEVENT, _ALPHAEVENT = 0, 1, 2, 3

COLLATE_LANG = glocale.collation

_NAME_STYLE_SHORT = 2
_NAME_STYLE_DEFAULT = 1
_NAME_STYLE_FIRST = 0
_NAME_STYLE_SPECIAL = None

PLUGMAN = BasePluginManager.get_instance()
CSS = PLUGMAN.process_plugin_data("WEBSTUFF")

# _NAME_COL = 3

_WRONGMEDIAPATH = []

_HTML_DBL_QUOTES = re.compile(r'([^"]*) " ([^"]*) " (.*)', re.VERBOSE)
_HTML_SNG_QUOTES = re.compile(r"([^']*) ' ([^']*) ' (.*)", re.VERBOSE)

# Events that are usually a family event
_EVENTMAP = set(
    [
        EventType.MARRIAGE,
        EventType.MARR_ALT,
        EventType.MARR_SETTL,
        EventType.MARR_LIC,
        EventType.MARR_CONTR,
        EventType.MARR_BANNS,
        EventType.ENGAGEMENT,
        EventType.DIVORCE,
        EventType.DIV_FILING,
    ]
)

# Names for stylesheets
_NARRATIVESCREEN = "narrative-screen.css"
_NARRATIVEPRINT = "narrative-print.css"

HOLIDAYS_ASSOC = [
    # LANG INDEX HOLIDAY_NAME
    ("be", 0, "Bulgaria"),
    ("ca", 1, "Canada"),
    ("cs", 2, "Czech Republic"),
    ("cl", 3, "Chile"),
    ("zh", 4, "China"),
    ("hr", 5, "Croatia"),
    ("en", 13, "United States of America"),  # must be here. should be en_US
    ("en_GB", 6, "England"),
    ("fi", 7, "Finland"),
    ("fr_FR", 8, "France"),
    ("de", 9, "Germany"),
    ("ja", 10, "Japan"),
    ("sk", 11, "Slovakia"),
    ("sv", 12, "Sweden"),
    ("he", 14, "Jewish Holidays"),
    ("en_NZ", 15, "New Zealand"),
    ("uk", 16, "Ukraine"),
    ("sr_RS", 17, "Serbia"),
    ("sr_RS@latin", 18, "Serbia (Latin)"),
]


def do_we_have_holidays(lang):
    """
    Associate an index for the holidays depending on the LANG
    """
    for lng, idx, dummy_name in HOLIDAYS_ASSOC:
        if lng == lang:  # i.e. en_US
            return idx
        if lng[:2] == lang:  # i.e. en_US[:2] => en
            return idx
    return None


def get_surname_from_person(dbase, person):
    """
    get the person's surname
    get the primary name
    if group as get the group_as surname
    else get the primary surname of the primary name
         and correct for [global] group_as name
    correct for surnames that are space or None
    """
    primary_name = person.get_primary_name()

    if primary_name.group_as:
        surname = primary_name.group_as
    else:
        group_map = _nd.primary_surname(primary_name)
        surname = dbase.get_name_group_mapping(group_map)

    # Treat people who have no name with those whose name is just
    # 'whitespace'
    if surname is None or surname.isspace():
        surname = ""
    return surname


def sort_people(dbase, handle_list, rlocale=glocale):
    """
    will sort the database people by surname
    @param: dbase           -- The instance of the database
    @param: handle_list     -- The list of handles of people to sort
    @param: rlocale         -- The locale related to the language used for the
                               sort
    @result:                -- A list sorted by surname, each element of which
                               consists of a tuple of (surname, list of handles)
                               where the list of handles is sorted by
                               primary surname, first name, suffix.
                               Surname uses group_as, but primary surname
                               does not.
    get the primary name
    if group as get the group_as surname
    else get the primary surname of the primary name
         and correct for [global] group_as name
    correct for surnames that are space or None
    for each surname sort handles by the surname, first name and suffix
    construct a list of surnames and list of handles
    """
    sname_sub = defaultdict(list)
    sortnames = {}

    for person_handle in handle_list:
        person = dbase.get_person_from_handle(person_handle)
        surname = get_surname_from_person(dbase, person)
        sortnames[person_handle] = _nd.sort_string(person.get_primary_name())
        sname_sub[surname].append(person_handle)

    sorted_lists = []
    temp_list = sorted(sname_sub, key=rlocale.sort_key)

    for name in temp_list:
        if isinstance(name, bytes):
            name = name.decode("utf-8")
        slist = sorted(
            ((sortnames[x], x) for x in sname_sub[name]),
            key=lambda x: rlocale.sort_key(x[0]),
        )
        entries = [x[1] for x in slist]
        sorted_lists.append((name, entries))

    return sorted_lists


def sort_places(dbase, handle_list, rlocale=glocale):
    """
    will sort the database places
    """
    pname_sub = defaultdict(list)

    for place_name in handle_list.keys():
        cname = sname = None
        if len(handle_list[place_name]) == 6:
            (hdle, pname, cname, sname, dummy_id, event) = handle_list[place_name]
        else:
            continue
        place = dbase.get_place_from_handle(hdle)
        pname = _pd.display(dbase, place, fmt=0)
        apname = _pd.display_event(dbase, event, fmt=0)

        pname_sub[pname].append(hdle)
        pname_sub[apname].append((hdle, pname, cname, sname))

    sorted_lists = []
    temp_list = sorted(pname_sub, key=rlocale.sort_key)

    for name in temp_list:
        if isinstance(name, bytes):
            name = name.decode("utf-8")
        sorted_lists.append((name, pname_sub[name][0]))

    return sorted_lists


def sort_event_types(dbase, event_types, event_handle_list, rlocale):
    """
    sort a list of event types and their associated event handles

    @param: dbase -- report database
    @param: event_types -- a dict of event types
    @param: event_handle_list -- all event handles in this database
    """
    rts = rlocale.translation.sgettext
    event_dict = dict((rts(evt_type), list()) for evt_type in event_types)

    for event_handle in event_handle_list:
        event = dbase.get_event_from_handle(event_handle)
        event_type = rts(event.get_type().xml_str())

        # add (gramps_id, date, handle) from this event
        if event_type in event_dict:
            sort_value = event.get_date_object().get_sort_value()
            event_dict[event_type].append((sort_value, event_handle))

    for tup_list in event_dict.values():
        tup_list.sort()

    # return a list of sorted tuples, one per event
    retval = [
        (event_type, event_list) for (event_type, event_list) in event_dict.items()
    ]
    retval.sort(key=lambda item: str(item[0]))

    return retval


# Modified _get_regular_surname from WebCal.py to get prefix, first name,
# and suffix
def _get_short_name(gender, name):
    """Will get suffix for all people passed through it"""

    dummy_gender = gender
    short_name = name.get_first_name()
    suffix = name.get_suffix()
    if suffix:
        # TODO for Arabic, should the next line's comma be translated?
        short_name = short_name + ", " + suffix
    return short_name


def __get_person_keyname(dbase, handle):
    """...."""

    person = dbase.get_person_from_handle(handle)
    return _nd.sort_string(person.get_primary_name())


def __get_place_keyname(dbase, handle):
    """..."""

    return utils.place_name(dbase, handle)


if HAVE_ALPHABETICINDEX:

    class AlphabeticIndex(icuAlphabeticIndex):
        """
        Call the ICU AlphabeticIndex, passing the ICU Locale
        """

        def __init__(self, rlocale):
            self.iculocale = Locale(rlocale.collation)
            super().__init__(self.iculocale)

            # set the maximum number of buckets, the undocumented default is 99
            # Latin + Greek + Cyrillic + Hebrew + Arabic + Tamil + Hiragana +
            # CJK Unified is about 206 different buckets
            self.maxLabelCount = 500  # pylint: disable=invalid-name

            # Add bucket labels for scripts other than the one for the output
            # which is being generated
            self.iculocale.addLikelySubtags()
            default_script = self.iculocale.getDisplayScript()
            used_scripts = [default_script]

            for lang_code in glocale.get_language_dict().values():
                loc = Locale(lang_code)
                loc.addLikelySubtags()
                script = loc.getDisplayScript()
                if script not in used_scripts:
                    used_scripts.append(script)
                    super().addLabels(loc)

else:
    AlphabeticIndex = localAlphabeticIndex


def alphabet_navigation(sorted_alpha_index, rlocale=glocale, rtl=False):
    """
    Will create the alphabet navigation bar for classes IndividualListPage,
    SurnameListPage, PlaceListPage, and EventList

    @param: index_list -- a dictionary of either letters or words
    @param: rlocale    -- The locale to use
    """
    # if no letters, return None to its callers
    if not sorted_alpha_index:
        return None

    num_ltrs = len(sorted_alpha_index)
    num_of_cols = 26
    num_of_rows = (num_ltrs // num_of_cols) + 1

    # begin alphabet navigation division
    with Html("div", id=rtl) as alphabetnavigation:
        index = 0
        output = []
        dup_index = 0
        for dummy_row in range(num_of_rows):
            unordered = Html("ul", class_=rtl)

            cols = 0
            while cols <= num_of_cols and index < num_ltrs:
                menu_item = sorted_alpha_index[index]
                if menu_item == " ":
                    menu_item = "&nbsp;"
                # adding title to hyperlink menu for screen readers and
                # braille writers
                title_txt = "Alphabet Menu: %s" % menu_item
                title_str = rlocale.translation.sgettext(title_txt)
                # deal with multiple ellipsis which are generated for overflow,
                # underflow and inflow labels
                link = menu_item
                if menu_item in output:
                    link = "%s (%i)" % (menu_item, dup_index)
                    dup_index += 1
                output.append(menu_item)

                hyper = Html("a", menu_item, title=title_str, href="#%s" % link)
                unordered.extend(Html("li", hyper, inline=True))

                index += 1
                cols += 1
            num_of_rows -= 1

            alphabetnavigation += unordered

    return alphabetnavigation


def _has_webpage_extension(url):
    """
    determine if a filename has an extension or not...

    @param: url -- filename to be checked
    """
    return any(url.endswith(ext) for ext in _WEB_EXT)


def add_birthdate(dbase, ppl_handle_list, rlocale):
    """
    This will sort a list of child handles in birth order
    For each entry in the list, we'll have :
         birth date
         The transtated birth date for the configured locale
         The transtated death date for the configured locale
         The handle for the child

    @param: dbase           -- The database to use
    @param: ppl_handle_list -- the handle for the people
    @param: rlocale         -- the locale for date translation
    """
    sortable_individuals = []
    for person_handle in ppl_handle_list:
        birth_date = 0  # dummy value in case none is found
        person = dbase.get_person_from_handle(person_handle)
        if person:
            birth_ref = person.get_birth_ref()
            birth1 = ""
            if birth_ref:
                birth = dbase.get_event_from_handle(birth_ref.ref)
                if birth:
                    birth1 = rlocale.get_date(birth.get_date_object())
                    birth_date = birth.get_date_object().get_sort_value()
            death_event = get_death_or_fallback(dbase, person)
            if death_event:
                death = rlocale.get_date(death_event.get_date_object())
            else:
                death = ""
        sortable_individuals.append((birth_date, birth1, death, person_handle))

    # return a list of handles with the individual's birthdate attached
    return sortable_individuals


def _find_birth_date(dbase, individual):
    """
    will look for a birth date within the person's events

    @param: dbase      -- The database to use
    @param: individual -- The individual for who we want to find the birth date
    """
    date_out = None
    birth_ref = individual.get_birth_ref()
    if birth_ref:
        birth = dbase.get_event_from_handle(birth_ref.ref)
        if birth:
            date_out = birth.get_date_object()
            date_out.fallback = False
    else:
        person_evt_ref_list = individual.get_primary_event_ref_list()
        if person_evt_ref_list:
            for evt_ref in person_evt_ref_list:
                event = dbase.get_event_from_handle(evt_ref.ref)
                if event:
                    if event.get_type().is_birth_fallback():
                        date_out = event.get_date_object()
                        date_out.fallback = True
                        LOG.debug("setting fallback to true for '%s'", event)
                        break
    return date_out


def _find_death_date(dbase, individual):
    """
    will look for a death date within a person's events

    @param: dbase      -- The database to use
    @param: individual -- The individual for who we want to find the death date
    """
    date_out = None
    death_ref = individual.get_death_ref()
    if death_ref:
        death = dbase.get_event_from_handle(death_ref.ref)
        if death:
            date_out = death.get_date_object()
            date_out.fallback = False
    else:
        person_evt_ref_list = individual.get_primary_event_ref_list()
        if person_evt_ref_list:
            for evt_ref in person_evt_ref_list:
                event = dbase.get_event_from_handle(evt_ref.ref)
                if event:
                    if event.get_type().is_death_fallback():
                        date_out = event.get_date_object()
                        date_out.fallback = True
                        LOG.debug("setting fallback to true for '%s'", event)
                        break
    return date_out


def build_event_data_by_individuals(dbase, ppl_handle_list):
    """
    creates a list of event handles and event types for this database

    @param: dbase           -- The database to use
    @param: ppl_handle_list -- the handle for the people
    """
    event_handle_list = []
    event_types = []

    for person_handle in ppl_handle_list:
        person = dbase.get_person_from_handle(person_handle)
        if person:
            evt_ref_list = person.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    event = dbase.get_event_from_handle(evt_ref.ref)
                    if event:
                        event_types.append(str(event.get_type()))
                        event_handle_list.append(evt_ref.ref)

            person_family_handle_list = person.get_family_handle_list()
            if person_family_handle_list:
                for family_handle in person_family_handle_list:
                    family = dbase.get_family_from_handle(family_handle)
                    if family:
                        family_evt_ref_list = family.get_event_ref_list()
                        if family_evt_ref_list:
                            for evt_ref in family_evt_ref_list:
                                event = dbase.get_event_from_handle(evt_ref.ref)
                                if event:
                                    event_types.append(str(event.type))
                                    event_handle_list.append(evt_ref.ref)

    # return event_handle_list and event types to its caller
    return event_handle_list, event_types


def name_to_md5(text):
    """This creates an MD5 hex string to be used as filename."""

    return md5(text.encode("utf-8")).hexdigest()


def get_gendex_data(database, event_ref):
    """
    Given an event, return the date and place a strings

    @param: database  -- The database
    @param: event_ref -- The event reference
    """
    doe = ""  # date of event
    poe = ""  # place of event
    if event_ref and event_ref.ref:
        event = database.get_event_from_handle(event_ref.ref)
        if event:
            date = event.get_date_object()
            doe = format_date(date)
            if event.get_place_handle():
                place_handle = event.get_place_handle()
                if place_handle:
                    place = database.get_place_from_handle(place_handle)
                    if place:
                        poe = _pd.display(database, place, date)
    return doe, poe


def format_date(date):
    """
    Format the date
    """
    start = date.get_start_date()
    if start != Date.EMPTY:
        cal = date.get_calendar()
        mod = date.get_modifier()
        quality = date.get_quality()
        if quality in DATE_QUALITY:
            qual_text = DATE_QUALITY[quality] + " "
        else:
            qual_text = ""
        if mod == Date.MOD_SPAN:
            val = "%sFROM %s TO %s" % (
                qual_text,
                make_gedcom_date(start, cal, mod, None),
                make_gedcom_date(date.get_stop_date(), cal, mod, None),
            )
        elif mod == Date.MOD_RANGE:
            val = "%sBET %s AND %s" % (
                qual_text,
                make_gedcom_date(start, cal, mod, None),
                make_gedcom_date(date.get_stop_date(), cal, mod, None),
            )
        else:
            val = make_gedcom_date(start, cal, mod, quality)
        return val
    return ""


# This command then defines the 'html_escape' option for escaping
# special characters for presentation in HTML based on the above list.
def html_escape(text):
    """Convert the text and replace some characters with a &# variant."""

    # First single characters, no quotes
    text = escape(text)

    # Deal with double quotes.
    match = _HTML_DBL_QUOTES.match(text)
    while match:
        text = "%s" "&#8220;" "%s" "&#8221;" "%s" % match.groups()
        match = _HTML_DBL_QUOTES.match(text)
    # Replace remaining double quotes.
    text = text.replace('"', "&#34;")

    # Deal with single quotes.
    text = text.replace("'s ", "&#8217;s ")
    match = _HTML_SNG_QUOTES.match(text)
    while match:
        text = "%s" "&#8216;" "%s" "&#8217;" "%s" % match.groups()
        match = _HTML_SNG_QUOTES.match(text)
    # Replace remaining single quotes.
    text = text.replace("'", "&#39;")

    return text
