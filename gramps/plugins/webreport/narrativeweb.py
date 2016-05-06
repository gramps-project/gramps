# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007-2009  Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2011  Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010-2016  Serge Noiraud
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2016       Allen Crider
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

Classes:
    NavWebReport - main class that produces the report. Entry point to produce
    the report is write_report
    NavWebOptions - class that defines the options and provides the handling
    interface

    BasePage - super class for producing a web page. This class is instantiated
    once for each page. Provdes various common functions.

Classes for producing the web pages:
    SurnamePage - creates list of individuals with same surname
    FamilyPage - Family index page and individual Family pages
    PlacePage - Place index page and individual Place pages
    EventPage - Event index page and individual Event pages
    SurnameListPage - Index for first letters of surname
    IntroductionPage
    HomePage
    CitationPages - dummy
    SourcePage - Source index page and individual Source pages
    MediaPage - Media index page and individual Media pages
    ThimbnailPreviewPage
    DownloadPage
    ContactPage
    PersonPage - Person index page and individual `Person pages
    RepositoryPage - Repository index page and individual Repository pages
    AddressBookListPage
    AddressBookPage
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from functools import partial
import gc
import os
import sys
import re
import copy
from hashlib import md5
import time, datetime
import shutil
import tarfile
import tempfile
from io import BytesIO, TextIOWrapper
from unicodedata import normalize
from collections import defaultdict
from xml.sax.saxutils import escape

from operator import itemgetter
from decimal import Decimal, getcontext
getcontext().prec = 8

#------------------------------------------------
# Set up logging
#------------------------------------------------
import logging
LOG = logging.getLogger(".NarrativeWeb")

# py lint: disable=line-too-long

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.lib import (ChildRefType, Date, EventType, FamilyRelType, Name,
                            NameType, Person, UrlType, NoteType, PlaceType,
                            EventRoleType, Family, Event, Place, Source,
                            Citation, Media, Repository, Note, Tag)
from gramps.gen.lib.date import Today
from gramps.gen.const import PROGRAM_NAME, URL_HOMEPAGE
from gramps.version import VERSION
from gramps.gen.plug.menu import PersonOption, NumberOption, StringOption, \
                          BooleanOption, EnumeratedListOption, FilterOption, \
                          NoteOption, MediaOption, DestinationOption
from gramps.gen.plug.report import (Report, Bibliography)
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions

from gramps.gen.utils.config import get_researcher
from gramps.gen.utils.string import conf_strings
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.alive import probably_alive
from gramps.gen.constfunc import win, get_curr_dir
from gramps.gen.config import config
from gramps.gen.utils.thumbnails import get_thumbnail_path, run_thumbnailer
from gramps.gen.utils.image import image_size # , resize_to_jpeg_buffer
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.datehandler import displayer as _dd
from gramps.gen.proxy import LivingProxyDb
from gramps.plugins.lib.libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS
from gramps.gen.datehandler import get_date

# import HTML Class from src/plugins/lib/libhtml.py
from gramps.plugins.lib.libhtml import Html, xml_lang

# import styled notes from src/plugins/lib/libhtmlbackend.py
from gramps.plugins.lib.libhtmlbackend import HtmlBackend, process_spaces

from gramps.plugins.lib.libgedcom import make_gedcom_date, DATE_QUALITY
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.plug import BasePluginManager

from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.location import get_main_location

COLLATE_LANG = glocale.collation
SORT_KEY = glocale.sort_key
#------------------------------------------------
# Everything below this point is identical for gramps34 (post 3.4.2),
# gramps40 and trunk
#------------------------------------------------

#------------------------------------------------
# constants
#------------------------------------------------
# javascript code for Google single Marker...
GOOGLE_JSC = """
  var myLatLng = new google.maps.LatLng(%s, %s);

  function initialize() {
    var mapOptions = {
      scaleControl:    true,
      panControl:      true,
      backgroundColor: '#000000',
      draggable:       true,
      zoom:            10,
      center:          myLatLng,
      mapTypeId:       google.maps.MapTypeId.ROADMAP
    }
    var map = new google.maps.Map(document.getElementById("place_canvas"), mapOptions);

    var marker = new google.maps.Marker({
      position:  myLatLng,
      draggable: true,
      title:     "%s",
      map:       map
    });
  }"""

# javascript code for Google's FamilyLinks...
FAMILYLINKS = """
  var tracelife = %s

  function initialize() {
    var myLatLng = new google.maps.LatLng(%s, %s);

    var mapOptions = {
      scaleControl:    true,
      panControl:      true,
      backgroundColor: '#000000',
      zoom:            %d,
      center:          myLatLng,
      mapTypeId:       google.maps.MapTypeId.ROADMAP
    }
    var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

    var flightPath = new google.maps.Polyline({
      path:          tracelife,
      strokeColor:   "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight:  2
    });

   flightPath.setMap(map);
  }"""

# javascript for Google's Drop Markers...
DROPMASTERS = """
  var markers = [];
  var iterator = 0;

  var tracelife = %s
  var map;

  function initialize() {
    var mapOptions = {
      scaleControl: true,
      zoomControl:  true,
      zoom:         %d,
      mapTypeId:    google.maps.MapTypeId.ROADMAP,
      center:       new google.maps.LatLng(0, 0)
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
  }

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

    markers.push(new google.maps.Marker({
      position:  myLatLng,
      map:       map,
      draggable: true,
      title:     location[0],
      animation: google.maps.Animation.DROP
    }));
    iterator++;
  }"""

# javascript for Google's Markers...
MARKERS = """
  var tracelife = %s
  var map;

  function initialize() {
    var mapOptions = {
      scaleControl:    true,
      panControl:      true,
      backgroundColor: '#000000',
      zoom:            %d,
      center:          new google.maps.LatLng(0, 0),
      mapTypeId:       google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
    addMarkers();
  }

  function addMarkers() {
    var bounds = new google.maps.LatLngBounds();

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
      bounds.extend(myLatLng);
      map.fitBounds(bounds);
    }
  }"""

CANADA_MAP = """
    var dm_wms = new OpenLayers.Layer.WMS(
      "Canadian Data",
      "http://www2.dmsolutions.ca/cgi-bin/mswms_gmap",
      {layers: "bathymetry,land_fn,park,drain_fn,drainage," +
         "prov_bound,fedlimit,rail,road,popplace",
         transparent: "true",
         format: "image/png"},
       {isBaseLayer: false});
     map.addLayers([wms, dm_wms]);
"""

# javascript code for OpenStreetMap single marker
OPENSTREETMAP_JSC = """
  OpenLayers.Lang.setCode("%s");

  function initialize(){
    var map = new OpenLayers.Map('place_canvas');

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

# javascript for OpenStreetMap's markers...
OSM_MARKERS = """
  OpenLayers.Lang.setCode("%s");
  var map;

  var tracelife = %s

  function initialize(){
    map = new OpenLayers.Map('map_canvas');

    var wms = new OpenLayers.Layer.WMS(
      "OpenLayers WMS",
      "http://vmap0.tiles.osgeo.org/wms/vmap0",
      {'layers':'basic'});
    map.addLayer(wms);

    map.setCenter(new OpenLayers.LonLat(%s, %s), %d);

    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);

    addMarkers(markers, map);
  }

  function addMarkers(markers, map) {
    for (var i = 0; i < tracelife.length; i++) {
      var location = tracelife[i];

      marker = new OpenLayers.Marker(new OpenLayers.LonLat(location[0], location[1]));
      markers.addMarker(marker);
      map.addControl(new OpenLayers.Control.LayerSwitcher());
    }
  }"""
# there is no need to add an ending "</script>",
# as it will be added automatically by libhtml()


# Translatable strings for variables within this plugin
# gettext carries a huge footprint with it.
AHEAD = _("Attributes")
BIRTH = _("Birth")
CITY = _("City")
COUNTY = _("County")
COUNTRY = _("Country")
DEATH = _("Death")
DHEAD = _("Date")
DESCRHEAD = _("Description")
_EVENT = _("Event")
GRAMPSID = _("Gramps&nbsp;ID")
LATITUDE = _("Latitude")
LOCALITY = _("Locality")
LONGITUDE = _("Longitude")
NHEAD = _("Notes")
PARENTS = _("Parents")
PARISH = _("Church Parish")
_PARTNER = _("Partner")
PHEAD = _("Place")
_PERSON = _("Person")
PHONE = _("Phone")
POSTAL = _("Postal Code")
SHEAD = _("Sources")
ST = _("Status")
STATE = _("State/ Province")
STREET = _("Street")
THEAD = _("Type")
TEMPLE = _("Temple")
VHEAD = _("Value")
ALT_LOCATIONS = _("Alternate Locations")
LOCATIONS = _("Locations")
_UNKNOWN = _("Unknown")
_ABSENT = _("<absent>")

# Events that are usually a family event
_EVENTMAP = set(
                [EventType.MARRIAGE, EventType.MARR_ALT,
                 EventType.MARR_SETTL, EventType.MARR_LIC,
                 EventType.MARR_CONTR, EventType.MARR_BANNS,
                 EventType.ENGAGEMENT, EventType.DIVORCE,
                 EventType.DIV_FILING
                ]
              )

# define clear blank line for proper styling
FULLCLEAR = Html("div", class_="fullclear", inline=True)

# Names for stylesheets
_NARRATIVESCREEN = "narrative-screen.css"
_NARRATIVEPRINT = "narrative-print.css"

# variables for alphabet_navigation()
_KEYPERSON, _KEYPLACE, _KEYEVENT, _ALPHAEVENT = 0, 1, 2, 3

# Web page filename extensions
_WEB_EXT = ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']

_INCLUDE_LIVING_VALUE = LivingProxyDb.MODE_INCLUDE_ALL
_NAME_COL = 3

_DEFAULT_MAX_IMG_WIDTH = 800   # resize images that are wider than this
_DEFAULT_MAX_IMG_HEIGHT = 600  # resize images that are taller than this
                               # The two values above are settable in options.
_WIDTH = 160
_HEIGHT = 64
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5
_WRONGMEDIAPATH = []

_NAME_STYLE_SHORT = 2
_NAME_STYLE_DEFAULT = 1
_NAME_STYLE_FIRST = 0
_NAME_STYLE_SPECIAL = None

PLUGMAN = BasePluginManager.get_instance()
CSS = PLUGMAN.process_plugin_data('WEBSTUFF')

_HTML_DBL_QUOTES = re.compile(r'([^"]*) " ([^"]*) " (.*)', re.VERBOSE)
_HTML_SNG_QUOTES = re.compile(r"([^']*) ' ([^']*) ' (.*)", re.VERBOSE)

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
    text = text.replace('"', '&#34;')

    # Deal with single quotes.
    text = text.replace("'s ", '&#8217;s ')
    match = _HTML_SNG_QUOTES.match(text)
    while match:
        text = "%s" "&#8216;" "%s" "&#8217;" "%s" % match.groups()
        match = _HTML_SNG_QUOTES.match(text)
    # Replace remaining single quotes.
    text = text.replace("'", '&#39;')

    return text

def name_to_md5(text):
    """This creates an MD5 hex string to be used as filename."""

    return md5(text.encode('utf-8')).hexdigest()

def conf_priv(obj):
    """
    Return private string

    @param: obj -- The object reference
    """
    if obj.get_privacy() != 0:
        return ' priv="%d"' % obj.get_privacy()
    else:
        return ''

def get_gendex_data(database, event_ref):
    """
    Given an event, return the date and place a strings

    @param: database  -- The database
    @param: event_ref -- The event reference
    """
    doe = "" # date of event
    poe = "" # place of event
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
                make_gedcom_date(date.get_stop_date(), cal, mod, None))
        elif mod == Date.MOD_RANGE:
            val = "%sBET %s AND %s" % (
                qual_text,
                make_gedcom_date(start, cal, mod, None),
                make_gedcom_date(date.get_stop_date(), cal, mod, None))
        else:
            val = make_gedcom_date(start, cal, mod, quality)
        return val
    return ""

def sort_on_name_and_grampsid(obj, dbase):
    """ Used to sort on name and gramps ID. """

    person = dbase.get_person_from_handle(obj)
    name = _nd.display(person)
    return (name, person.get_gramps_id())

def copy_thumbnail(report, handle, photo, region=None):
    """
    Given a handle (and optional region) make (if needed) an
    up-to-date cache of a thumbnail, and call report.copy_file
    to copy the cached thumbnail to the website.
    Return the new path to the image.
    """
    to_dir = report.build_path('thumb', handle)
    to_path = os.path.join(to_dir, handle) + (
        ('%d,%d-%d,%d.png' % region) if region else '.png'
        )

    if photo.get_mime_type():
        full_path = media_path_full(report.database, photo.get_path())
        from_path = get_thumbnail_path(full_path,
                                       photo.get_mime_type(),
                                       region)
        if not os.path.isfile(from_path):
            from_path = CSS["Document"]["filename"]
    else:
        from_path = CSS["Document"]["filename"]
    report.copy_file(from_path, to_path)
    return to_path

# pylint: disable=unused-variable
# pylint: disable=unused-argument

class BasePage(object):
    """
    Manages all the functions, variables, and everything needed
    for all of the classes contained within this plugin
    """
    def __init__(self, report, title, gid=None):
        """
        @param: report -- The instance of the main report class for
                          this report
        @param: title  -- Is the title of the web page
        @param: gid    -- The family gramps ID
        """
        self.uplink = False
        # class to do conversion of styled notes to html markup
        self._backend = HtmlBackend()
        self._backend.build_link = report.build_link

        self.report = report
        self.title_str = title
        self.gid = gid
        self.bibli = Bibliography()
        self.dbase_ = report.database

        self.page_title = ""

        self.author = get_researcher().get_name()
        if self.author:
            self.author = self.author.replace(',,,', '')

        # TODO. All of these attributes are not necessary, because we have
        # also the options in self.options.  Besides, we need to check which
        # are still required.
        self.html_dir = report.options['target']
        self.ext = report.options['ext']
        self.noid = report.options['nogid']
        self.linkhome = report.options['linkhome']
        self.create_media = report.options['gallery']
        self.create_unused_media = report.options['unused']
        self.create_thumbs_only = report.options['create_thumbs_only']
        self.inc_families = report.options['inc_families']
        self.inc_events = report.options['inc_events']
        self.usecms = report.options['usecms']
        self.target_uri = report.options['cmsuri']
        self.usecal = report.options['usecal']
        self.target_cal_uri = report.options['caluri']
        self.familymappages = None

    # Functions used when no Web Page plugin is provided
    def add_instance(self, *param):
        """
        Add an instance
        """
        pass

    def display_pages(self, title):
        """
        Display the pages
        """
        pass

    def get_nav_menu_hyperlink(self, url_fname, nav_text):
        """
        Returns the navigation menu hyperlink
        """
        if url_fname == self.target_cal_uri:
            uplink = False
        else:
            uplink = self.uplink

        # check for web page file extension?
        if not _has_webpage_extension(url_fname):
            url_fname += self.ext

        # get menu item url and begin hyperlink...
        url = self.report.build_url_fname(url_fname, None, uplink)

        return Html("a", nav_text, href=url, title=nav_text, inline=True)

    def get_column_data(self, unordered, data_list, column_title):
        """
        Returns the menu column for Drop Down Menus and Drop Down Citations
        """
        if len(data_list) == 0:
            return

        elif len(data_list) == 1:
            url_fname, nav_text = data_list[0][0], data_list[0][1]
            hyper = self.get_nav_menu_hyperlink(url_fname, nav_text)
            unordered.extend(
                Html("li", hyper, inline=True)
            )
        else:
            col_list = Html("li") + (
                Html("a", column_title, href="#",
                     title=column_title, inline=True)
            )
            unordered += col_list

            unordered1 = Html("ul")
            col_list += unordered1

            for url_fname, nav_text in data_list:
                hyper = self.get_nav_menu_hyperlink(url_fname, nav_text)
                unordered1.extend(
                   Html("li", hyper, inline=True)
                )

    def display_relationships(self, individual, place_lat_long):
        """
        Displays a person's relationships ...

        @param: family_handle_list -- families in this report database
        @param: place_lat_long -- for use in Family Map Pages. This will be None
        if called from Family pages, which do not create a Family Map
        """
        family_list = sorted(individual.get_family_handle_list())
        if not family_list:
            return None

        with Html("div", class_="subsection", id="families") as section:
            section += Html("h4", _("Families"), inline=True)

            table_class = "infolist"
            if len(family_list) > 1:
                table_class += " fixed_subtables"
            with Html("table", class_=table_class) as table:
                section += table

                for family_handle in family_list:
                    family = self.dbase_.get_family_from_handle(family_handle)
                    if family:
                        link = self.family_link(
                            family_handle,
                            self.report.obj_dict[Family][family_handle][1],
                            gid=family.get_gramps_id(), uplink=True)
                        trow = Html("tr", class_="BeginFamily") + (
                            Html("td", "&nbsp", class_="ColumnType",
                                 inline=True),
                            Html("td", "&nbsp", class_="ColumnAttribute",
                                 inline=True),
                            Html("td", link, class_="ColumnValue",
                                 inline=True)
                        )
                        table += trow
                        # find the spouse of the principal individual and
                        # display that person
                        spouse_handle = ReportUtils.find_spouse(individual,
                                                                family)
                        if spouse_handle:
                            spouse = self.dbase_.get_person_from_handle(
                                          spouse_handle)
                            if spouse:
                                table += self.display_spouse(spouse, family,
                                                             place_lat_long)

                        details = self.display_family_details(family,
                                                              place_lat_long)
                        if details is not None:
                            table += details
        return section

    def display_family_relationships(self, family, place_lat_long):
        """
        Displays a family's relationships ...

        @param: family -- the family to be displayed
        @param: place_lat_long -- for use in Family Map Pages. This will be None
        if called from Family pages, which do not create a Family Map
        """
        with Html("div", class_="subsection", id="families") as section:
            section += Html("h4", _("Families"), inline=True)

            table_class = "infolist"
            with Html("table", class_=table_class) as table:
                section += table
                for person_handle in [family.get_father_handle(),
                                      family.get_mother_handle()]:
                    person = None
                    if person_handle:
                        person = self.dbase_.get_person_from_handle(
                                          person_handle)
                    if person:
                        table += self.display_spouse(person,
                                                     family, place_lat_long)

                details = self.display_family_details(family, place_lat_long)
                if details is not None:
                    table += details
        return section

    def display_family_details(self, family, place_lat_long):
        """
        Display details about one family: family events, children, family LDS
        ordinances, family attributes
        """
        table = None
        birthorder = self.report.options["birthorder"]
        # display family events; such as marriage and divorce...
        family_events = family.get_event_ref_list()
        if family_events:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html("td", "&nbsp;", class_="ColumnAttribute", inline=True),
                Html("td", self.format_family_events(family_events,
                                                     place_lat_long),
                     class_="ColumnValue")
            )
            table = trow

        # If the families pages are not output, display family notes
        if not self.inc_families:
            notelist = family.get_note_list()
            for notehandle in notelist:
                note = self.dbase_.get_note_from_handle(notehandle)
                if note:
                    trow = Html("tr") + (
                    Html("td", "&nbsp;", class_="ColumnType", inline=True),
                    Html("td", _("Narrative"), class_="ColumnAttribute",
                         inline=True),
                    Html("td", self.get_note_format(note, True),
                         class_="ColumnValue")
                    )
                    table = table + trow if table is not None else trow

        childlist = family.get_child_ref_list()
        if childlist:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html("td", _("Children"), class_="ColumnAttribute", inline=True)
            )
            table = table + trow if table is not None else trow

            tcell = Html("td", class_="ColumnValue")
            trow += tcell

            ordered = Html("ol")
            tcell += ordered
            childlist = [child_ref.ref for child_ref in childlist]

            # add individual's children event places to family map...
            if self.familymappages:
                for handle in childlist:
                    child = self.dbase_.get_person_from_handle(handle)
                    if child:
                        self._get_event_place(child, place_lat_long)

            children = add_birthdate(self.dbase_, childlist)
            if birthorder:
                children = sorted(children)

            ordered.extend(
             (Html("li") +
              self.display_child_link(chandle))
                    for birth_date, chandle in children
            )

        # family LDS ordinance list
        family_lds_ordinance_list = family.get_lds_ord_list()
        if family_lds_ordinance_list:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html("td", _("LDS Ordinance"), class_="ColumnAttribute",
                     inline=True),
                Html("td", self.dump_ordinance(family, "Family"),
                     class_="ColumnValue")
            )
            table = table + trow if table is not None else trow

        # Family Attribute list
        family_attribute_list = family.get_attribute_list()
        if family_attribute_list:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html("td", _("Attributes"), class_="ColumnAttribute",
                     inline=True)
            )
            table = table + trow if table is not None else trow

            tcell = Html("td", class_="ColumnValue")
            trow += tcell

            # we do not need the section variable for this instance
            # of Attributes...
            dummy, attrtable = self.display_attribute_header()
            tcell += attrtable
            self.display_attr_list(family_attribute_list, attrtable)
        return table

    def complete_people(self, tcell, first_person, handle_list, uplink=True):
        """
        completes the person column for classes EventListPage and EventPage

        @param: tcell -- table cell from its caller
        @param: first_person -- Not used any more, done via css
        @param: handle_list -- handle list from the backlink of the event_handle
        """
        for (classname, handle) in handle_list:

            # personal event
            if classname == "Person":
                tcell += Html("span", self.new_person_link(handle, uplink),
                              class_="person", inline=True)

            # family event
            else:
                _obj = self.dbase_.get_family_from_handle(handle)
                if _obj:

                    # husband and spouse in this example,
                    # are called father and mother
                    husband_handle = _obj.get_father_handle()
                    if husband_handle:
                        hlink = self.new_person_link(husband_handle, uplink)
                    spouse_handle = _obj.get_mother_handle()
                    if spouse_handle:
                        slink = self.new_person_link(spouse_handle, uplink)

                    if spouse_handle and husband_handle:
                        tcell += Html("span", hlink, class_="father",
                                      inline=True)
                        tcell += Html("span", slink, class_="mother",
                                      inline=True)
                    elif spouse_handle:
                        tcell += Html("span", slink, class_="mother",
                                      inline=True)
                    elif husband_handle:
                        tcell += Html("span", hlink, class_="father",
                                      inline=True)
        return tcell

    def dump_attribute(self, attr):
        """
        dump attribute for object presented in display_attr_list()

        @param: attr = attribute object
        """
        trow = Html("tr")

        trow.extend(
            Html("td", data or "&nbsp;", class_=colclass,
                inline=True if (colclass == "Type" or "Sources") else False)
                for (data, colclass) in [
                    (str(attr.get_type()), "ColumnType"),
                    (attr.get_value(), "ColumnValue"),
                    (self.dump_notes(attr.get_note_list()), "ColumnNotes"),
                    (self.get_citation_links(attr.get_citation_list()),
                                                            "ColumnSources")
                ]
        )
        return trow

    def get_citation_links(self, citation_handle_list):
        """
        get citation link from the citation handle list

        @param: citation_handle_list = list of gen/lib/Citation
        """
        text = ""
        for citation_handle in citation_handle_list:
            citation = self.report.database.get_citation_from_handle(
                                       citation_handle)
            if citation:
                index, key = self.bibli.add_reference(citation)
                id_ = "%d%s" % (index+1, key)
                text += ' <a href="#sref%s">%s</a>' % (id_, id_)
        return text

    def get_note_format(self, note, link_prefix_up):
        """
        will get the note from the database, and will return either the
        styled text or plain note
        """
        self.report.link_prefix_up = link_prefix_up

        text = ""
        if note is not None:
            # retrieve the body of the note
            note_text = note.get()

            # styled notes
            htmlnotetext = self.styled_note(
                                       note.get_styledtext(),
                                       note.get_format(), contains_html=
                                       note.get_type() == NoteType.HTML_CODE)
            text = htmlnotetext or Html("p", note_text)

        # return text of the note to its callers
        return text

    def styled_note(self, styledtext, styled_format, contains_html=False):
        """
        styledtext : assumed a StyledText object to write
        styled_format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        """
        text = str(styledtext)

        if not text:
            return ''

        s_tags = styledtext.get_tags()
        htmllist = Html("div", class_="grampsstylednote")
        if contains_html:
            markuptext = self._backend.add_markup_from_styled(text,
                                                              s_tags,
                                                              split='\n',
                                                              escape=False)
            htmllist += markuptext
        else:
            markuptext = self._backend.add_markup_from_styled(text,
                                                              s_tags,
                                                              split='\n')
            linelist = []
            linenb = 1
            for line in markuptext.split('\n'):
                [line, sigcount] = process_spaces(line, styled_format)
                if sigcount == 0:
                    # The rendering of an empty paragraph '<p></p>'
                    # is undefined so we use a non-breaking space
                    if linenb == 1:
                        linelist.append('&nbsp;')
                    htmllist.extend(Html('p') + linelist)
                    linelist = []
                    linenb = 1
                else:
                    if linenb > 1:
                        linelist[-1] += '<br />'
                    linelist.append(line)
                    linenb += 1
            if linenb > 1:
                htmllist.extend(Html('p') + linelist)
            # if the last line was blank, then as well as outputting
            # the previous para, which we have just done,
            # we also output a new blank para
            if sigcount == 0:
                linelist = ["&nbsp;"]
                htmllist.extend(Html('p') + linelist)
        return htmllist

    def dump_notes(self, notelist):
        """
        dump out of list of notes with very little elements of its own

        @param: notelist -- list of notes
        """
        if not notelist:
            return Html("div")

        # begin unordered list
        notesection = Html("div")
        for notehandle in notelist:
            this_note = self.report.database.get_note_from_handle(notehandle)
            if this_note is not None:
                notesection.extend(Html("i", str(this_note.type),
                                        class_="NoteType"))
                notesection.extend(self.get_note_format(this_note, True))
        return notesection

    def event_header_row(self):
        """
        creates the event header row for all events
        """
        trow = Html("tr")
        trow.extend(
            Html("th", trans, class_=colclass, inline=True)
            for trans, colclass in  [
                (_("Event"), "ColumnEvent"),
                (_("Date"), "ColumnDate"),
                (_("Place"), "ColumnPlace"),
                (_("Description"), "ColumnDescription"),
                (_("Notes"), "ColumnNotes"),
                (_("Sources"), "ColumnSources")]
        )
        return trow

    def display_event_row(self, event, event_ref, place_lat_long,
                          uplink, hyperlink, omit):
        """
        display the event row for IndividualPage

        @param: evt            -- Event object from report database
        @param: evt_ref        -- Event reference
        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        @param: uplink         -- If True, then "../../../" is inserted in front
                                  of the result.
        @param: hyperlink      -- Add a hyperlink or not
        @param: omit           -- Role to be omitted in output
        """
        event_gid = event.get_gramps_id()

        place_handle = event.get_place_handle()
        if place_handle:
            place = self.dbase_.get_place_from_handle(place_handle)
            if place:
                self.append_to_place_lat_long(place, event, place_lat_long)

        # begin event table row
        trow = Html("tr")

        # get event type and hyperlink to it or not?
        etype = str(event.get_type())

        event_role = event_ref.get_role()
        if not event_role == omit:
            etype += " (%s)" % event_role
        event_hyper = self.event_link(event_ref.ref,
                                      etype,
                                      event_gid,
                                      uplink) if hyperlink else etype
        trow += Html("td", event_hyper, class_="ColumnEvent")

        # get event data
        event_data = self.get_event_data(event, event_ref, uplink)

        trow.extend(
            Html("td", data or "&nbsp;", class_=colclass,
                inline=(not data or colclass == "ColumnDate"))
            for (label, colclass, data) in event_data
        )

        # get event notes
        notelist = event.get_note_list()
        notelist.extend(event_ref.get_note_list())
        htmllist = self.dump_notes(notelist)

        # if the event or event reference has an attribute attached to it,
        # get the text and format it correctly?
        attrlist = event.get_attribute_list()
        attrlist.extend(event_ref.get_attribute_list())
        for attr in attrlist:
            htmllist.extend(Html(
                "p",
                _("%(type)s: %(value)s") % {
                'type'     : Html("b", attr.get_type()),
                'value'    : attr.get_value()
                }))

            #also output notes attached to the attributes
            notelist = attr.get_note_list()
            if notelist:
                htmllist.extend(self.dump_notes(notelist))

        trow += Html("td", htmllist, class_="ColumnNotes")

        # get event source references
        srcrefs = self.get_citation_links(event.get_citation_list()) or "&nbsp;"
        trow += Html("td", srcrefs, class_="ColumnSources")

        # return events table row to its callers
        return trow

    def append_to_place_lat_long(self, place, event, place_lat_long):
        """
        Create a list of places with coordinates.

        @param: place_lat_long -- for use in Family Map Pages. This will be None
        if called from Family pages, which do not create a Family Map
        """
        if place_lat_long is None:
            return
        place_handle = place.get_handle()

        # 0 = latitude, 1 = longitude, 2 - placetitle,
        # 3 = place handle, 4 = event date, 5 = event type
        found = any(data[3] == place_handle for data in place_lat_long)
        if not found:
            placetitle = _pd.display(self.dbase_, place)
            latitude = place.get_latitude()
            longitude = place.get_longitude()
            if latitude and longitude:
                latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                if latitude is not None:
                    event_date = event.get_date_object()
                    etype = event.get_type()

                    # only allow Birth, Death, Census, Marriage,
                    # and Divorce events...
                    if etype in [EventType.BIRTH, EventType.DEATH,
                                 EventType.CENSUS,
                                 EventType.MARRIAGE, EventType.DIVORCE]:
                        place_lat_long.append([latitude, longitude, placetitle,
                                               place_handle, event_date, etype])

    def _get_event_place(self, person, place_lat_long):
        """
        Retrieve from a person their events, and places for family map

        @param: person         -- Person object from the database
        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        """
        if not person:
            return

        # check to see if this person is in the report database?
        use_link = self.report.person_in_webreport(person.get_handle())
        if use_link:
            evt_ref_list = person.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    event = self.dbase_.get_event_from_handle(evt_ref.ref)
                    if event:
                        place_handle = event.get_place_handle()
                        if place_handle:
                            place = self.dbase_.get_place_from_handle(
                                              place_handle)
                            if place:
                                self.append_to_place_lat_long(place, event,
                                                              place_lat_long)

    def family_link(self, family_handle, name, gid=None, uplink=False):
        """
        Create the url and link for FamilyPage

        @param: family_handle -- The handle for the family to link
        @param: name          -- The family name
        @param: gid           -- The family gramps ID
        @param: uplink        -- If True, then "../../../" is inserted in front
                                 of the result.
        """
        name = html_escape(name)
        if not self.noid and gid:
            gid_html = Html("span", " [%s]" % gid, class_="grampsid",
                            inline=True)
        else:
            gid_html = ""

        result = self.report.obj_dict.get(Family).get(family_handle)
        if result is None:
            # the family is not included in the webreport
            return name + str(gid_html)

        url = self.report.build_url_fname(result[0], uplink=uplink)
        hyper = Html("a", name, href=url, title=name)
        hyper += gid_html
        return hyper

    def get_family_string(self, family):
        """
        Unused method ???
        Returns a hyperlink for each person linked to the Family Page

        @param: family -- The family
        """
        husband, spouse = [False]*2

        husband_handle = family.get_father_handle()

        if husband_handle:
            husband = self.dbase_.get_person_from_handle(husband_handle)
        else:
            husband = None

        spouse_handle = family.get_mother_handle()
        if spouse_handle:
            spouse = self.dbase_.get_person_from_handle(spouse_handle)
        else:
            spouse = None

        if husband:
            husband_name = self.get_name(husband)
            hlink = self.family_link(family.get_handle(),
                                     husband_name, uplink=self.uplink)
        if spouse:
            spouse_name = self.get_name(spouse)
            slink = self.family_link(family.get_handle(),
                                     spouse_name, uplink=self.uplink)

        title_str = ''
        if husband and spouse:
            title_str = '%s ' % hlink + _("and") + ' %s' % slink
        elif husband:
            title_str = '%s ' % hlink
        elif spouse:
            title_str = '%s ' % slink
        return title_str

    def event_link(self, event_handle, event_title, gid=None, uplink=False):
        """
        Creates a hyperlink for an event based on its type

        @param: event_handle -- Event handle
        @param: event_title  -- Event title
        @param: gid          -- The gramps ID for the event
        @param: uplink       -- If True, then "../../../" is inserted in front
                                of the result.
        """
        if not self.inc_events:
            return event_title

        url = self.report.build_url_fname_html(event_handle, "evt", uplink)
        hyper = Html("a", event_title, href=url, title=event_title)

        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_="grampsid", inline=True)
        return hyper

    def format_family_events(self, event_ref_list, place_lat_long):
        """
        displays the event row for events such as marriage and divorce

        @param: event_ref_list -- List of events reference
        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        """
        with Html("table", class_="infolist eventlist") as table:
            thead = Html("thead")
            table += thead

            # attach event header row
            thead += self.event_header_row()

            # begin table body
            tbody = Html("tbody")
            table += tbody

            for evt_ref in event_ref_list:
                event = self.dbase_.get_event_from_handle(evt_ref.ref)

                # add event body row
                tbody += self.display_event_row(event, evt_ref, place_lat_long,
                                            uplink=True, hyperlink=True,
                                            omit=EventRoleType.FAMILY)
        return table

    def get_event_data(self, evt, evt_ref,
                       uplink, gid=None):
        """
        retrieve event data from event and evt_ref

        @param: evt     -- Event from database
        @param: evt_ref -- Event reference
        @param: uplink  -- If True, then "../../../" is inserted in front of the
                           result.
        """
        place = None
        place_handle = evt.get_place_handle()
        if place_handle:
            place = self.dbase_.get_place_from_handle(place_handle)

        place_hyper = None
        if place:
            place_name = _pd.display(self.dbase_, place, evt.get_date_object())
            place_hyper = self.place_link(place_handle, place_name,
                                          uplink=uplink)

        evt_desc = evt.get_description()

        # wrap it all up and return to its callers
        # position 0 = translatable label, position 1 = column class
        # position 2 = data
        return [
               (_("Date"), "ColumnDate", _dd.display(evt.get_date_object())),
               (_("Place"), "ColumnPlace", place_hyper),
               (_("Description"), "ColumnDescription", evt_desc)]

    def dump_ordinance(self, ldsobj,
                       ldssealedtype):
        """
        will dump the LDS Ordinance information for either
        a person or a family ...

        @param: ldsobj        -- Either person or family
        @param: ldssealedtype -- Either Sealed to Family or Spouse
        """
        objectldsord = ldsobj.get_lds_ord_list()
        if not objectldsord:
            return None

        # begin LDS ordinance table and table head
        with Html("table", class_="infolist ldsordlist") as table:
            thead = Html("thead")
            table += thead

            # begin HTML row
            trow = Html("tr")
            thead += trow

            trow.extend(
                Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        [_("Type"), "ColumnLDSType"],
                        [_("Date"), "ColumnDate"],
                        [_("Temple"), "ColumnLDSTemple"],
                        [_("Place"), "ColumnLDSPlace"],
                        [_("Status"), "ColumnLDSStatus"],
                        [_("Sources"), "ColumnLDSSources"]
                    ]
            )

            # start table body
            tbody = Html("tbody")
            table += tbody

            for ordobj in objectldsord:
                place_hyper = "&nbsp;"
                place_handle = ordobj.get_place_handle()
                if place_handle:
                    place = self.dbase_.get_place_from_handle(place_handle)
                    if place:
                        place_title = _pd.display(self.dbase_, place)
                        place_hyper = self.place_link(place_handle, place_title,
                            place.get_gramps_id(), uplink=True)

                # begin ordinance rows
                trow = Html("tr")

                trow.extend(
                    Html("td", value or "&nbsp;", class_=colclass,
                        inline=(not value or colclass == "ColumnDate"))
                        for (value, colclass) in [
                            (ordobj.type2xml(), "ColumnType"),
                            (_dd.display(ordobj.get_date_object()),
                                                  "ColumnDate"),
                            (ordobj.get_temple(), "ColumnLDSTemple"),
                            (place_hyper, "ColumnLDSPlace"),
                            (ordobj.get_status(), "ColumnLDSStatus"),
                            (self.get_citation_links(
                                  ordobj.get_citation_list()), "ColumnSources")
                        ]
                )
                tbody += trow
        return table

    def write_srcattr(self, srcattr_list):
        """
        Writes out the srcattr for the different objects

        @param: srcattr_list -- List of source attributes
        """
        if len(srcattr_list) == 0:
            return None

        # begin data map division and section title...
        with Html("div", class_="subsection", id="data_map") as section:
            section += Html("h4", _("Attributes"), inline=True)

            with Html("table", class_="infolist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", _("Key"), class_="ColumnAttribute", inline=True),
                    Html("th", _("Value"), class_="ColumnValue", inline=True)
                )
                thead += trow

                tbody = Html("tbody")
                table += tbody

                for srcattr in srcattr_list:
                    trow = Html("tr") + (
                        Html("td", str(srcattr.get_type()),
                             class_="ColumnAttribute", inline=True),
                        Html("td", srcattr.get_value(),
                             class_="ColumnValue", inline=True)
                    )
                    tbody += trow
        return section

    def source_link(self, source_handle, source_title,
                    gid=None, cindex=None, uplink=False):
        """
        Creates a link to the source object

        @param: source_handle -- Source handle from database
        @param: source_title  -- Title from the source object
        @param: gid           -- Source gramps id from the source object
        @param: cindex        -- Count index
        @param: uplink        -- If True, then "../../../" is inserted in front
                                 of the result.
        """
        url = self.report.build_url_fname_html(source_handle, "src", uplink)
        hyper = Html("a", source_title,
                     href=url,
                     title=source_title)

        # if not None, add name reference to hyperlink element
        if cindex:
            hyper.attr += ' name ="sref%d"' % cindex

        # add GRAMPS ID
        if not self.noid and gid:
            hyper += Html("span", ' [%s]' % gid, class_="grampsid", inline=True)
        return hyper

    def display_addr_list(self, addrlist, showsrc):
        """
        Display a person's or repository's addresses ...

        @param: addrlist -- a list of address handles
        @param: showsrc  -- True = show sources
                            False = do not show sources
                            None = djpe
        """
        if not addrlist:
            return None

        # begin addresses division and title
        with Html("div", class_="subsection", id="Addresses") as section:
            section += Html("h4", _("Addresses"), inline=True)

            # write out addresses()
            section += self.dump_addresses(addrlist, showsrc)

        # return address division to its caller
        return section

    def dump_addresses(self, addrlist, showsrc):
        """
        will display an object's addresses, url list, note list,
        and source references.

        @param: addrlist = either person or repository address list
        @param: showsrc = True  --  person and their sources
                          False -- repository with no sources
                          None  -- Address Book address with sources
        """
        if not addrlist:
            return None

        # begin summaryarea division
        with Html("div", id="AddressTable") as summaryarea:

            # begin address table
            with Html("table") as table:
                summaryarea += table

                # get table class based on showsrc
                if showsrc == True:
                    table.attr = 'class = "infolist addrlist"'
                elif showsrc == False:
                    table.attr = 'class = "infolist repolist"'
                else:
                    table.attr = 'class = "infolist addressbook"'

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                addr_header = [
                      [DHEAD, "Date"],
                      [STREET, "StreetAddress"],
                      [_("Locality"), "Locality"],
                      [CITY, "City"],
                      [STATE, "State"],
                      [COUNTY, "County"],
                      [POSTAL, "Postalcode"],
                      [COUNTRY, "Cntry"],
                      [PHONE, "Phone"]]

                # True, False, or None ** see docstring for explanation
                if showsrc in [True, None]:
                    addr_header.append([SHEAD, "Sources"])

                trow.extend(
                    Html("th", label, class_="Colummn" + colclass, inline=True)
                    for (label, colclass) in addr_header
                )

                # begin table body
                tbody = Html("tbody")
                table += tbody

                # get address list from an object; either repository or person
                for address in addrlist:

                    trow = Html("tr")
                    tbody += trow

                    addr_data_row = [
                        (_dd.display(address.get_date_object()), "ColumnDate"),
                        (address.get_street(), "ColumnStreetAddress"),
                        (address.get_locality(), "ColumnLocality"),
                        (address.get_city(), "ColumnCity"),
                        (address.get_state(), "ColumnState"),
                        (address.get_county(), "ColumnCounty"),
                        (address.get_postal_code(), "ColumnPostalCode"),
                        (address.get_country(), "ColumnCntry"),
                        (address.get_phone(), "ColumnPhone")
                    ]

                    # get source citation list
                    if showsrc in [True, None]:
                        addr_data_row.append([
                          self.get_citation_links(address.get_citation_list()),
                                              "ColumnSources"])

                    trow.extend(
                        Html("td", value or "&nbsp;",
                             class_=colclass, inline=True)
                            for (value, colclass) in addr_data_row
                    )

                    # address: notelist
                    if showsrc is not None:
                        notelist = self.display_note_list(
                                                address.get_note_list())
                        if notelist is not None:
                            summaryarea += notelist
        return summaryarea

    def addressbook_link(self, person_handle, uplink=False):
        """
        Creates a hyperlink for an address book link based on person's handle

        @param: person_handle -- Person's handle from the database
        @param: uplink        -- If True, then "../../../" is inserted in front
                                 of the result.
        """
        url = self.report.build_url_fname_html(person_handle, "addr", uplink)
        person = self.report.database.get_person_from_handle(person_handle)
        person_name = self.get_name(person)

        # return addressbook hyperlink to its caller
        return Html("a", person_name, href=url, title=html_escape(person_name))

    def get_copyright_license(self, copyright_, uplink=False):
        """
        Will return either the text or image of the copyright license

        @param: copyright_ -- The kind of copyright
        @param: uplink     -- If True, then "../../../" is inserted in front
                              of the result.
        """
        text = ''
        if copyright_ == 0:
            if self.author:
                year = Today().get_year()
                text = '&copy; %(year)d %(person)s' % {
                    'person' : self.author,
                    'year' : year}
        elif 0 < copyright_ < len(_CC):
            # Note. This is a URL
            fname = "/".join(["images", "somerights20.gif"])
            url = self.report.build_url_fname(fname, None, uplink=False)
            text = _CC[copyright_] % {'gif_fname' : url}

        # return text or image to its callers
        return text

    def get_name(self, person, maiden_name=None):
        """ I5118

        Return person's name, unless maiden_name given, unless married_name
        listed.

        @param: person -- person object from database
        @param: maiden_name -- Female's family surname
        """
        # get name format for displaying names
        name_format = self.report.options['name_format']

        # Get all of a person's names
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == NameType.MARRIED:
                married_name = name
                break # use first

        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = Name(married_name)
            else:
                name = Name(primary_name)
                surname_obj = name.get_primary_surname()
                surname_obj.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def display_attribute_header(self):
        """
        Display the attribute section and its table header
        """
        # begin attributes division and section title
        with Html("div", class_="subsection", id="attributes") as section:
            section += Html("h4", _("Attributes"), inline=True)

            # begin attributes table
            with Html("table", class_="infolist attrlist") as attrtable:
                section += attrtable

                thead = Html("thead")
                attrtable += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        (_("Type"), "ColumnType"),
                        (_("Value"), "ColumnValue"),
                        (_("Notes"), "ColumnNotes"),
                        (_("Sources"), "ColumnSources")]
                )
        return section, attrtable

    def display_attr_list(self, attrlist,
                          attrtable):
        """
        Will display a list of attributes

        @param: attrlist -- a list of attributes
        @param: attrtable -- the table element that is being added to
        """
        tbody = Html("tbody")
        attrtable += tbody

        tbody.extend(
            self.dump_attribute(attr) for attr in attrlist
        )

    def write_footer(self, date):
        """
        Will create and display the footer section of each page...

        @param: bottom -- whether to specify location of footer section or not?
        """
        # begin footer division
        with Html("div", id="footer") as footer:

            footer_note = self.report.options['footernote']
            if footer_note:
                note = self.get_note_format(
                    self.report.database.get_note_from_gramps_id(footer_note),
                    False
                    )
                user_footer = Html("div", id='user_footer')
                footer += user_footer

                # attach note
                user_footer += note

            msg = _('Generated by %(gramps_home_html_start)s'
                    'Gramps%(html_end)s %(version)s'
                   ) % {'gramps_home_html_start' :
                            '<a href="' + URL_HOMEPAGE + '">',
                        'html_end' : '</a>',
                        'version' : VERSION}
            if date is not None:
                msg += "<br />"
                last_modif = datetime.datetime.fromtimestamp(date).strftime(
                                               '%Y-%m-%d %H:%M:%S')
                msg += _('Last change was the %(date)s') % {'date' : last_modif}
            else:
                msg += _(' on %(date)s') % {'date' : _dd.display(Today())}

            # optional "link-home" feature; see bug report #2736
            if self.report.options['linkhome']:
                center_person = self.report.database.get_person_from_gramps_id(
                                                     self.report.options['pid'])
                if (center_person and
                   self.report.person_in_webreport(center_person.handle)):
                    center_person_url = self.report.build_url_fname_html(
                        center_person.handle, "ppl", self.uplink)

                    person_name = self.get_name(center_person)
                    subject_url = '<a href="' + center_person_url + '">'
                    subject_url += person_name + '</a>'
                    msg += _('%(http_break)sCreated for %(subject_url)s') % {
                                 'http_break'  : '<br />',
                                 'subject_url' : subject_url}

            # creation author
            footer += Html("p", msg, id='createdate')

            # get copyright license for all pages
            copy_nr = self.report.copyright

            text = ''
            if copy_nr == 0:
                if self.author:
                    year = Today().get_year()
                    text = '&copy; %(year)d %(person)s' % {
                               'person' : self.author,
                               'year' : year}
            elif copy_nr < len(_CC):
                # Note. This is a URL
                fname = "/".join(["images", "somerights20.gif"])
                url = self.report.build_url_fname(fname, None, self.uplink)
                text = _CC[copy_nr] % {'gif_fname' : url}
            footer += Html("p", text, id='copyright')

        # return footer to its callers
        return footer

    def write_header(self, title):
        """
        Note. 'title' is used as currentsection in the navigation links and
        as part of the header title.

        @param: title -- Is the title of the web page
        """
        # begin each html page...
        xmllang = xml_lang()
        page, head, body = Html.page('%s - %s' %
                                    (html_escape(self.title_str.strip()),
                                     html_escape(title)),
                                    self.report.encoding,
                                    xmllang, cms=self.usecms)

        # temporary fix for .php parsing error
        if self.ext in [".php", ".php3", ".cgi"]:
            del page[0]

        # Header constants
        _meta1 = 'name ="viewport" content="width=device-width; '
        _meta1 += 'height=device-height; initial-scale=0.1; '
        _meta1 += 'maximum-scale=10.0; user-scalable=yes"'
        _meta2 = 'name ="apple-mobile-web-app-capable" content="yes"'
        _meta3 = 'name="generator" content="%s %s %s"' % (
                    PROGRAM_NAME, VERSION, URL_HOMEPAGE)
        _meta4 = 'name="author" content="%s"' % self.author

        # create additional meta tags
        meta = Html("meta", attr=_meta1) + (
                Html("meta", attr=_meta2, indent=False),
                Html("meta", attr=_meta3, indent=False),
                Html("meta", attr=_meta4, indent=False)
        )

        # Link to _NARRATIVESCREEN  stylesheet
        fname = "/".join(["css", _NARRATIVESCREEN])
        url2 = self.report.build_url_fname(fname, None, self.uplink)

        # Link to _NARRATIVEPRINT stylesheet
        fname = "/".join(["css", _NARRATIVEPRINT])
        url3 = self.report.build_url_fname(fname, None, self.uplink)

        # Link to GRAMPS favicon
        fname = "/".join(['images', 'favicon2.ico'])
        url4 = self.report.build_url_image("favicon2.ico",
                                           "images", self.uplink)

        # create stylesheet and favicon links
        links = Html("link", type="image/x-icon",
                     href=url4, rel="shortcut icon") + (
             Html("link", type="text/css", href=url2,
                  media="screen", rel="stylesheet", indent=False),
             Html("link", type="text/css", href=url3,
                  media='print', rel="stylesheet", indent=False)
             )

        # Link to Navigation Menus stylesheet
        if CSS[self.report.css]["navigation"]:
            fname = "/".join(["css", "narrative-menus.css"])
            url = self.report.build_url_fname(fname, None, self.uplink)
            links += Html("link", type="text/css", href=url,
                          media="screen", rel="stylesheet", indent=False)

        # add additional meta and link tags
        head += meta
        head += links

        # begin header section
        headerdiv = Html("div", id='header') + (
            Html("h1", html_escape(self.title_str), id="SiteTitle", inline=True)
        )
        body += headerdiv

        header_note = self.report.options['headernote']
        if header_note:
            note = self.get_note_format(
                self.report.database.get_note_from_gramps_id(header_note),
                False)

            user_header = Html("div", id='user_header')
            headerdiv += user_header

            # attach note
            user_header += note

        # Begin Navigation Menu--
        # is the style sheet either Basic-Blue or Visually Impaired,
        # and menu layout is Drop Down?
        if (self.report.css == _("Basic-Blue") or
            self.report.css == _("Visually Impaired")) and \
            self.report.navigation == "dropdown":
            body += self.display_drop_menu()
        else:
            body += self.display_nav_links(title)

        # return page, head, and body to its classes...
        return page, head, body

    def display_nav_links(self, currentsection):
        """
        Creates the navigation menu

        @param: currentsection = which menu item are you on
        """
        # include repositories or not?
        inc_repos = True
        if (not self.report.inc_repository or
            not len(self.report.database.get_repository_handles())):
            inc_repos = False

        # create media pages...
        _create_media_link = False
        if self.create_media:
            _create_media_link = True
            if self.create_thumbs_only:
                _create_media_link = False

        # create link to web calendar pages...
        _create_calendar_link = False
        if self.usecal:
            _create_calendar_link = True
            self.target_cal_uri += "/index"

        # Determine which menu items will be available?
        # Menu items have been adjusted to concide with Gramps Navigation
        # Sidebar order...

        navs = [
            (self.report.index_fname, _("Html|Home"), self.report.use_home),
            (self.report.intro_fname, _("Introduction"), self.report.use_intro),
            ('individuals', _("Individuals"), True),
            (self.report.surname_fname, _("Surnames"), True),
            ('families', _("Families"), self.report.inc_families),
            ('events', _("Events"), self.report.inc_events),
            ('places', _("Places"), True),
            ('sources', _("Sources"), True),
            ('repositories', _("Repositories"), inc_repos),
            ('media', _("Media"), _create_media_link),
            ('thumbnails', _("Thumbnails"), self.create_media),
            ('download', _("Download"), self.report.inc_download),
            ("addressbook", _("Address Book"), self.report.inc_addressbook),
            ('contact', _("Contact"), self.report.use_contact),
            (self.target_cal_uri, _("Web Calendar"), self.usecal)
        ]

        # Remove menu sections if they are not being created?
        navs = ((url_text, nav_text) for url_text, nav_text,
                                         cond in navs if cond)
        menu_items = [[url, text] for url, text in navs]

        number_items = len(menu_items)
        num_cols = 10
        num_rows = ((number_items // num_cols) + 1)

        # begin navigation menu division...
        with Html("div", class_="wrapper",
                  id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:

                index = 0
                for rows in range(num_rows):
                    unordered = Html("ul", class_="menu", id="dropmenu")

                    cols = 0
                    while cols <= num_cols and index < number_items:
                        url_fname, nav_text = menu_items[index]

                        hyper = self.get_nav_menu_hyperlink(url_fname, nav_text)

                        # Define 'currentsection' to correctly set navlink item
                        # CSS id 'CurrentSection' for Navigation styling.
                        # Use 'self.report.cur_fname' to determine
                        # 'CurrentSection' for individual elements for
                        # Navigation styling.

                        # Figure out if we need <li class = "CurrentSection">
                        # or just <li>

                        check_cs = False
                        if nav_text == currentsection:
                            check_cs = True
                        elif nav_text == _("Surnames"):
                            if "srn" in self.report.cur_fname:
                                check_cs = True
                            elif _("Surnames") in currentsection:
                                check_cs = True
                        elif nav_text == _("Individuals"):
                            if "ppl" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Families"):
                            if "fam" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Sources"):
                            if "src" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Places"):
                            if "plc" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Events"):
                            if "evt" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Media"):
                            if "img" in self.report.cur_fname:
                                check_cs = True
                        elif nav_text == _("Address Book"):
                            if "addr" in self.report.cur_fname:
                                check_cs = True
                        temp_cs = 'class = "CurrentSection"'
                        check_cs = temp_cs if check_cs else False
                        if check_cs:
                            unordered.extend(
                                Html("li", hyper, attr=check_cs, inline=True)
                            )
                        else:
                            unordered.extend(
                                Html("li", hyper, inline=True)
                            )
                        index += 1
                        cols += 1

                    container += unordered
                navigation += container
        return navigation

    def display_drop_menu(self):
        """
        Creates the Drop Down Navigation Menu
        """
        # include repositories or not?
        inc_repos = True
        if (not self.report.inc_repository or
            not len(self.report.database.get_repository_handles())):
            inc_repos = False

        # create media pages...
        _create_media_link = False
        if self.create_media:
            _create_media_link = True
            if self.create_thumbs_only:
                _create_media_link = False

        personal = [
            (self.report.intro_fname, _("Introduction"), self.report.use_intro),
            ("individuals", _("Individuals"), True),
            (self.report.surname_fname, _("Surnames"), True),
            ("families", _("Families"), self.report.inc_families)
        ]
        personal = ((url_text, nav_text) for url_text, nav_text,
                                             cond in personal if cond)
        personal = [[url, text] for url, text in personal]

        navs1 = [
            ("events", _("Events"), self.report.inc_events),
            ("places", _("Places"), True),
            ("sources", _("Sources"), True),
            ("repositories", _("Repositories"), inc_repos)
        ]
        navs1 = ((url_text, nav_text) for url_text, nav_text,
                                          cond in navs1 if cond)
        navs1 = [[url, text] for url, text in navs1]

        media = [
            ("media", _("Media"), _create_media_link),
            ("thumbnails", _("Thumbnails"), True)
        ]
        media = ((url_text, nav_text) for url_text, nav_text,
                                          cond in media if cond)
        media = [[url, text] for url, text in media]

        misc = [
            ('download', _("Download"), self.report.inc_download),
            ("addressbook", _("Address Book"), self.report.inc_addressbook)
        ]
        misc = ((url_text, nav_text) for url_text, nav_text,
                                         cond in misc if cond)
        misc = [[url, text] for url, text in misc]

        contact = [
            ('contact', _("Contact"), self.report.use_contact)
        ]
        contact = ((url_text, nav_text) for url_text, nav_text,
                                            cond in contact if cond)
        contact = [[url, text] for url, text in contact]

        # begin navigation menu division...
        with Html("div", class_="wrapper",
                  id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:
                unordered = Html("ul", class_="menu", id="dropmenu")

                if self.report.use_home:
                    list_html = Html("li",
                           self.get_nav_menu_hyperlink(self.report.index_fname,
                           _("Html|Home")))
                    unordered += list_html

                # add personal column
                self.get_column_data(unordered, personal, _("Personal"))

                if len(navs1):
                    for url_fname, nav_text in navs1:
                        unordered.extend(
                            Html("li", self.get_nav_menu_hyperlink(url_fname,
                                                                   nav_text),
                                 inline=True)
                        )

                # add media column
                self.get_column_data(unordered, media, _("Media"))

                # add miscellaneous column
                self.get_column_data(unordered, misc, _("Miscellaneous"))

                # add contact column
                self.get_column_data(unordered, contact, _("Contact"))

                container += unordered
            navigation += container
        return navigation

    def add_image(self, option_name, height=0):
        """
        Will add an image (if present) to the page

        @param: option_name -- The name of the report option
        @param: height      -- Height of the image
        """
        pic_id = self.report.options[option_name]
        if pic_id:
            obj = self.report.database.get_media_from_gramps_id(pic_id)
            if obj is None:
                return None
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:

                    newpath, thumb_path = self.report.prepare_copy_media(obj)
                    self.report.copy_file(media_path_full(
                        self.report.database, obj.get_path()), newpath)

                    # begin image
                    image = Html("img")
                    image.attr = ''
                    if height:
                        image.attr += 'height = "%d"'  % height

                    descr = html_escape(obj.get_description())
                    newpath = self.report.build_url_fname(newpath)
                    image.attr += ' src = "%s" alt = "%s"' % (newpath, descr)

                    # return an image
                    return image

                except (IOError, OSError) as msg:
                    self.report.user.warn(_("Could not add photo to page"),
                                          str(msg))

        # no image to return
        return None

    def media_ref_rect_regions(self, handle):
        """
        GRAMPS feature #2634 -- attempt to highlight subregions in media
        objects and link back to the relevant web page.

        This next section of code builds up the "records" we'll need to
        generate the html/css code to support the subregions

        @param: handle -- The media handle to use
        """
        # get all of the backlinks to this media object; meaning all of
        # the people, events, places, etc..., that use this image
        _region_items = set()
        for (classname, newhandle) in self.dbase_.find_backlink_handles(handle,
            include_classes=["Person", "Family", "Event", "Place"]):

            # for each of the backlinks, get the relevant object from the db
            # and determine a few important things, such as a text name we
            # can use, and the URL to a relevant web page
            _obj = None
            _name = ""
            _linkurl = "#"
            if classname == "Person":
                # Is this a person for whom we have built a page:
                if self.report.person_in_webreport(newhandle):
                    # If so, let's add a link to them:
                    _obj = self.dbase_.get_person_from_handle(newhandle)
                    if _obj:
                        # What is the shortest possible name we could use
                        # for this person?
                        _name = (_obj.get_primary_name().get_call_name() or
                                 _obj.get_primary_name().get_first_name() or
                                 _UNKNOWN
                                )
                        _linkurl = self.report.build_url_fname_html(_obj.handle,
                                                                    "ppl", True)
            elif classname == "Family":
                _obj = self.dbase_.get_family_from_handle(newhandle)
                partner1_handle = _obj.get_father_handle()
                partner2_handle = _obj.get_mother_handle()
                partner1 = None
                partner2 = None
                if partner1_handle:
                    partner1 = self.dbase_.get_person_from_handle(
                                           partner1_handle)
                if partner2_handle:
                    partner2 = self.dbase_.get_person_from_handle(
                                           partner2_handle)
                if partner2 and partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner1_handle,
                                                                "ppl", True)
                elif partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner1_handle,
                                                                "ppl", True)
                elif partner2:
                    _name = partner2.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner2_handle,
                                                                "ppl", True)
                if not _name:
                    _name = _UNKNOWN
            elif classname == "Event":
                _obj = self.dbase_.get_event_from_handle(newhandle)
                _name = _obj.get_description()
                if not _name:
                    _name = _UNKNOWN
                _linkurl = self.report.build_url_fname_html(_obj.handle,
                                                            "evt", True)
            elif classname == "Place":
                _obj = self.dbase_.get_place_from_handle(newhandle)
                _name = _pd.display(self.dbase_, _obj)
                if not _name:
                    _name = _UNKNOWN
                _linkurl = self.report.build_url_fname_html(newhandle,
                                                            "plc", True)

            # continue looking through the loop for an object...
            if _obj is None:
                continue

            # get a list of all media refs for this object
            media_list = _obj.get_media_list()

            # go media refs looking for one that points to this image
            for mediaref in media_list:

                # is this mediaref for this image?  do we have a rect?
                if mediaref.ref == handle and mediaref.rect is not None:

                    (coord_x1, coord_y1, coord_x2, coord_y2) = mediaref.rect
                    # Gramps gives us absolute coordinates,
                    # but we need relative width + height
                    width = coord_x2 - coord_x1
                    height = coord_y2 - coord_y1

                    # remember all this information, cause we'll need
                    # need it later when we output the <li>...</li> tags
                    item = (_name, coord_x1, coord_y1, width, height, _linkurl)
                    _region_items.add(item)

        # End of code that looks for and prepares the media object regions

        # return media rectangles to its callers
        # bug 8950 : it seems it's better to sort on name
        #            + coords of the rectangle.
        def sort_by_name_and_rectangle(obj):
            """
            Sort by name and rectangle

            @param: obj -- The object reference
            """
            return(obj[0], obj[1], obj[2], obj[3], obj[4])

        return sorted(_region_items,
                      key=lambda x: sort_by_name_and_rectangle(x))

    def media_ref_region_to_object(self, media_handle, obj):
        """
        Return a region of this image if it refers to this object.

        @param: media_handle -- The media handle to use
        @param: obj          -- The object reference
        """
        # get a list of all media refs for this object
        for mediaref in obj.get_media_list():
            # is this mediaref for this image?  do we have a rect?
            if (mediaref.ref == media_handle and
                mediaref.rect is not None):
                return mediaref.rect # (x1, y1, x2, y2)
        return None

    def disp_first_img_as_thumbnail(self, photolist, object_):
        """
        Return the Html of the first image of photolist that is
        associated with object. First image might be a region in an
        image. Or, the first image might have regions defined in it.

        @param: photolist -- The list of media
        @param: object_   -- The object reference
        """
        if not photolist or not self.create_media:
            return None

        photo_handle = photolist[0].get_reference_handle()
        photo = self.report.database.get_media_from_handle(photo_handle)
        mime_type = photo.get_mime_type()
        descr = photo.get_description()

        # begin snapshot division
        with Html("div", class_="snapshot") as snapshot:

            if mime_type:

                region = self.media_ref_region_to_object(photo_handle, object_)
                if region:

                    # make a thumbnail of this region
                    newpath = copy_thumbnail(self.report, photo_handle,
                                             photo, region)
                    newpath = self.report.build_url_fname(newpath, uplink=True)

                    snapshot += self.media_link(photo_handle, newpath, descr,
                                                uplink=self.uplink,
                                                usedescr=False)
                else:

                    real_path, newpath = self.report.prepare_copy_media(photo)
                    newpath = self.report.build_url_fname(newpath, uplink=True)

                    # FIXME: There doesn't seem to be any point in highlighting
                    # a sub-region in the thumbnail and linking back to the
                    # person or whatever. First it is confusing when the link
                    # probably has nothing to do with the page on which the
                    # thumbnail is displayed, and second on a thumbnail it is
                    # probably too small to see, and third, on the thumbnail,
                    # the link is shown above the image (which is pretty
                    # useless!)
                    _region_items = self.media_ref_rect_regions(photo_handle)
                    if len(_region_items):
                        with Html("div", id="GalleryDisplay") as mediadisplay:
                            snapshot += mediadisplay

                            ordered = Html("ol", class_="RegionBox")
                            mediadisplay += ordered
                            while len(_region_items):
                                (name, coord_x, coord_y,
                                 width, height, linkurl) = _region_items.pop()
                                ordered += Html("li",
                                                style="left:%d%%; top:%d%%; "
                                                 "width:%d%%; height:%d%%;" % (
                                           coord_x, coord_y, width, height))
                                ordered += Html("a", name, href=linkurl)
                            # Need to add link to mediadisplay to get the links:
                            mediadisplay += self.media_link(photo_handle,
                                                            newpath, descr,
                                                            self.uplink, False)
                    else:
                        try:

                            # Begin hyperlink. Description is given only for
                            # the purpose of the alt tag in img element
                            snapshot += self.media_link(photo_handle, newpath,
                                                        descr,
                                                        uplink=self.uplink,
                                                        usedescr=False)

                        except (IOError, OSError) as msg:
                            self.report.user.warn(_("Could not add photo "
                                                    "to page"), str(msg))
            else:
                # begin hyperlink
                snapshot += self.doc_link(photo_handle, descr,
                                          uplink=self.uplink, usedescr=False)

        # return snapshot division to its callers
        return snapshot

    def disp_add_img_as_gallery(self, photolist, object_):
        """
        Display additional image as gallery

        @param: photolist -- The list of media
        @param: object_   -- The object reference
        """
        if not photolist or not self.create_media:
            return None

        # make referenced images have the same order as in media list:
        photolist_handles = {}
        for mediaref in photolist:
            photolist_handles[mediaref.get_reference_handle()] = mediaref
        photolist_ordered = []
        for photoref in copy.copy(object_.get_media_list()):
            if photoref.ref in photolist_handles:
                photo = photolist_handles[photoref.ref]
                photolist_ordered.append(photo)
                try:
                    photolist.remove(photo)
                except ValueError:
                    LOG.warning("Error trying to remove '%s' from photolist",
                                photo)
        # and add any that are left (should there be any?)
        photolist_ordered += photolist

        # begin individualgallery division and section title
        with Html("div", class_="subsection", id="indivgallery") as section:
            section += Html("h4", _("Media"), inline=True)

            displayed = []
            for mediaref in photolist_ordered:

                photo_handle = mediaref.get_reference_handle()
                photo = self.report.database.get_media_from_handle(photo_handle)

                if photo_handle in displayed:
                    continue
                mime_type = photo.get_mime_type()

                # get media description
                descr = photo.get_description()

                if mime_type:
                    try:
                        # create thumbnail url
                        # extension needs to be added as it is not already there
                        url = self.report.build_url_fname(photo_handle, "thumb",
                                                          True) + ".png"
                        # begin hyperlink
                        section += self.media_link(photo_handle, url,
                                                   descr, uplink=self.uplink,
                                                   usedescr=True)
                    except (IOError, OSError) as msg:
                        self.report.user.warn(_("Could not add photo to page"),
                                              str(msg))
                else:
                    try:
                        # begin hyperlink
                        section += self.doc_link(photo_handle, descr,
                                                 uplink=self.uplink)
                    except (IOError, OSError) as msg:
                        self.report.user.warn(_("Could not add photo to page"),
                                              str(msg))
                displayed.append(photo_handle)

        # add fullclear for proper styling
        section += FULLCLEAR

        # return indivgallery division to its caller
        return section

    def display_note_list(self, notelist=None):
        """
        Display note list

        @param: notelist -- The list of notes
        """
        if not notelist:
            return None

        # begin narrative division
        with Html("div", class_="subsection narrative") as section:

            for notehandle in notelist:
                note = self.report.database.get_note_from_handle(notehandle)

                if note:
                    note_text = self.get_note_format(note, True)

                    # add section title
                    section += Html("h4", _("Narrative"), inline=True)

                    # attach note
                    section += note_text

        # return notes to its callers
        return section

    def display_url_list(self, urllist=None):
        """
        Display URL list

        @param: urllist -- The list of urls
        """
        if not urllist:
            return None

        # begin web links division
        with Html("div", class_="subsection", id="WebLinks") as section:
            section += Html("h4", _("Web Links"), inline=True)

            with Html("table", class_="infolist weblinks") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html('th', label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            (_("Type"), "ColumnType"),
                            (_("Description"), "ColumnDescription")
                        ]
                    )

                tbody = Html("tbody")
                table += tbody

                for url in urllist:

                    trow = Html("tr")
                    tbody += trow

                    _type = url.get_type()
                    uri = url.get_path()
                    descr = url.get_description()

                    # Email address
                    if _type == UrlType.EMAIL:
                        if not uri.startswith("mailto:"):
                            uri = "mailto:%(email)s" % {'email' : uri}

                    # Web Site address
                    elif _type == UrlType.WEB_HOME:
                        if not (uri.startswith("http://") or
                                uri.startswith("https://")):
                            uri = "http://%(website)s" % {"website" : uri}

                    # FTP server address
                    elif _type == UrlType.WEB_FTP:
                        if not (uri.startswith("ftp://") or
                                uri.startswith("ftps://")):
                            uri = "ftp://%(ftpsite)s" % {"ftpsite" : uri}

                    descr = Html("p", html_escape(descr)) + (
                        Html("a", _(" [Click to Go]"), href=uri, title=uri)
                    )

                    trow.extend(
                        Html("td", data, class_=colclass, inline=True)
                            for (data, colclass) in [
                                (str(_type), "ColumnType"),
                                (descr, "ColumnDescription")
                            ]
                    )
        return section

    def display_lds_ordinance(self, db_obj_):
        """
        Display LDS information for a person or family

        @param: db_obj_ -- The database object
        """
        ldsordlist = db_obj_.lds_ord_list
        if not ldsordlist:
            return None

        # begin LDS Ordinance division and section title
        with Html("div", class_="subsection", id="LDSOrdinance") as section:
            section += Html("h4", _("Latter-Day Saints/ LDS Ordinance"),
                            inline=True)

            # ump individual LDS ordinance list
            section += self.dump_ordinance(db_obj_, "Person")

        # return section to its caller
        return section

    def display_ind_sources(self, srcobj):
        """
        Will create the "Source References" section for an object

        @param: srcobj -- Sources object
        """
        list(map(lambda i: self.bibli.add_reference(
                              self.report.database.get_citation_from_handle(i)),
                           srcobj.get_citation_list()))
        sourcerefs = self.display_source_refs(self.bibli)

        # return to its callers
        return sourcerefs

    # Only used in IndividualPage.display_ind_sources(),
    # and MediaPage.display_media_sources()
    def display_source_refs(self, bibli):
        """
        Display source references

        @param: bibli -- List of sources
        """
        if bibli.get_citation_count() == 0:
            return None

        with Html("div", class_="subsection", id="sourcerefs") as section:
            section += Html("h4", _("Source References"), inline=True)

            ordered = Html("ol")

            cindex = 0
            citationlist = bibli.get_citation_list()
            for citation in citationlist:
                cindex += 1
                # Add this source and its references to the page
                source = self.dbase_.get_source_from_handle(
                                                citation.get_source_handle())
                if source is not None:
                    if source.get_author():
                        authorstring = source.get_author() + ": "
                    else:
                        authorstring = ""
                    list_html = Html("li", self.source_link(source.get_handle(),
                                authorstring + source.get_title(),
                                source.get_gramps_id(), cindex,
                                uplink=self.uplink))
                else:
                    list_html = Html("li", "None")

                ordered1 = Html("ol")
                citation_ref_list = citation.get_ref_list()
                for key, sref in citation_ref_list:
                    cit_ref_li = Html("li", id="sref%d%s" % (cindex, key))
                    tmp = Html("ul")
                    conf = conf_strings.get(sref.confidence, _('Unknown'))
                    if conf == conf_strings[Citation.CONF_NORMAL]:
                        conf = None
                    else:
                        conf = _(conf)
                    for (label, data) in [
                                          [_("Date"), _dd.display(sref.date)],
                                          [_("Page"), sref.page],
                                          [_("Confidence"), conf]]:
                        if data:
                            tmp += Html("li", "%s: %s" % (label, data))
                    if self.create_media:
                        for media_ref in sref.get_media_list():
                            media_handle = media_ref.get_reference_handle()
                            media = self.dbase_.get_media_from_handle(
                                                               media_handle)
                            if media:
                                mime_type = media.get_mime_type()
                                if mime_type:
                                    if mime_type.startswith("image/"):
                                        real_path, newpath = self.report.prepare_copy_media(media)
                                        newpath = self.report.build_url_fname(
                                                       newpath,
                                                        uplink=self.uplink)
                                        dest_dir = os.path.dirname(
                                                       self.report.cur_fname)
                                        if dest_dir:
                                            newpath = os.path.join(dest_dir,
                                                                   newpath)
                                        self.report.copy_file(media_path_full(
                                            self.report.database,
                                            media.get_path()), newpath)

                                        tmp += Html("li",
                                                self.media_link(media_handle,
                                                        newpath,
                                                        media.get_description(),
                                                        self.uplink,
                                                        usedescr=False),
                                                inline=True)

                                    else:
                                        tmp += Html("li",
                                                    self.doc_link(media_handle,
                                                        media.get_description(),
                                                        self.uplink,
                                                        usedescr=False),
                                                    inline=True)
                    for handle in sref.get_note_list():
                        this_note = self.dbase_.get_note_from_handle(handle)
                        if this_note is not None:
                            tmp += Html("li",
                                        "%s: %s" % (
                                            str(this_note.get_type()),
                                            self.get_note_format(this_note,
                                                                 True)
                                            ))
                    if tmp:
                        cit_ref_li += tmp
                        ordered1 += cit_ref_li

                if citation_ref_list:
                    list_html += ordered1
                ordered += list_html
            section += ordered

        # return section to its caller
        return section

    def display_references(self, handlelist,
                           uplink=False):
        """
        Display references for the current objects

        @param: handlelist -- List of handles
        @param: uplink     -- If True, then "../../../" is inserted in front of
                              the result.
        """
        if not handlelist:
            return None

        # begin references division and title
        with Html("div", class_="subsection", id="references") as section:
            section += Html("h4", _("References"), inline=True)

            ordered = Html("ol")
            section += ordered
            sortlist = sorted(handlelist, key=lambda x: SORT_KEY(x[1]))

            for (path, name, gid) in sortlist:
                list_html = Html("li")
                ordered += list_html

                name = name or _UNKNOWN
                if not self.noid and gid != "":
                    gid_html = Html("span", " [%s]" % gid, class_="grampsid",
                                    inline=True)
                else:
                    gid_html = ""

                if path != "":
                    url = self.report.build_url_fname(path, None, self.uplink)
                    list_html += Html("a", href=url) + name + gid_html
                else:
                    list_html += name + str(gid_html)

        # return references division to its caller
        return section

    def family_map_link(self, handle, url):
        """
        Creates a link to the family map

        @param: handle -- The family handle
        @param: url    -- url to be linked
        """
        return Html("a", _("Family Map"), href=url,
                    title=_("Family Map"), class_="familymap", inline=True)

    def display_spouse(self, partner, family, place_lat_long):
        """
        Display an individual's partner

        @param: partner        -- The partner
        @param: family         -- The family
        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        """
        gender = partner.get_gender()
        reltype = family.get_relationship()

        if reltype == FamilyRelType.MARRIED:
            if gender == Person.FEMALE:
                relstr = _("Wife")
            elif gender == Person.MALE:
                relstr = _("Husband")
            else:
                relstr = _("Partner")
        else:
            relstr = _("Partner")

        rtype = str(family.get_relationship())

        # display family relationship status, and add spouse to FamilyMapPages
        if self.familymappages:
            self._get_event_place(partner, place_lat_long)

        trow = Html("tr", class_="BeginFamily") + (
            Html("td", rtype, class_="ColumnType", inline=True),
            Html("td", relstr, class_="ColumnAttribute", inline=True)
        )

        tcell = Html("td", class_="ColumnValue")
        trow += tcell

        tcell += self.new_person_link(partner.get_handle(), uplink=True,
                                      person=partner)
        return trow

    def display_child_link(self, chandle):
        """
        display child link ...

        @param: chandle -- Child handle
        """
        return self.new_person_link(chandle, uplink=True)

    def new_person_link(self, person_handle, uplink=False, person=None,
                        name_style=_NAME_STYLE_DEFAULT):
        """
        creates a link for a person. If a page is generated for the person, a
        hyperlink is created, else just the name of the person. The returned
        vale will be an Html object if a hyperlink is generated, otherwise just
        a string

        @param: person_handle -- Person in database
        @param: uplink        -- If True, then "../../../" is inserted in front
                                 of the result
        @param: person        -- Person object. This does not need to be passed.
                                 It should be passed if the person object has
                                 already been retrieved, as it will be used to
                                 improve performance
        """
        result = self.report.obj_dict.get(Person).get(person_handle)

        # construct link, name and gid
        if result is None:
            # The person is not included in the webreport
            link = ""
            if person is None:
                person = self.dbase_.get_person_from_handle(person_handle)
            if person:
                name = self.report.get_person_name(person)
                gid = person.get_gramps_id()
            else:
                name = _("Unknown")
                gid = ""
        else:
            # The person has been encountered in the web report, but this does
            # not necessarily mean that a page has been generated
            (link, name, gid) = result

        if name_style == _NAME_STYLE_FIRST and person:
            name = _get_short_name(person.get_gender(),
                                   person.get_primary_name())
        name = html_escape(name)
        # construct the result
        if not self.noid and gid != "":
            gid_html = Html("span", " [%s]" % gid, class_="grampsid",
                            inline=True)
        else:
            gid_html = ""

        if link != "":
            url = self.report.build_url_fname(link, uplink=uplink)
            hyper = Html("a", name, gid_html, href=url, inline=True)
        else:
            hyper = name + str(gid_html)

        return hyper

    def media_link(self, media_handle, img_url, name,
                   uplink=False, usedescr=True):
        """
        creates and returns a hyperlink to the thumbnail image

        @param: media_handle -- Photo handle from report database
        @param: img_url      -- Thumbnail url
        @param: name         -- Photo description
        @param: uplink       -- If True, then "../../../" is inserted in front
                                of the result.
        @param: usedescr     -- Add media description
        """
        url = self.report.build_url_fname_html(media_handle, "img", uplink)
        name = html_escape(name)

        # begin thumbnail division
        with Html("div", class_="thumbnail") as thumbnail:

            # begin hyperlink
            if not self.create_thumbs_only:
                hyper = Html("a", href=url, title=name) + (
                    Html("img", src=img_url, alt=name)
                )
            else:
                hyper = Html("img", src=img_url, alt=name)
            thumbnail += hyper

            if usedescr:
                hyper += Html("p", name, inline=True)
        return thumbnail

    def doc_link(self, handle, name, uplink=False, usedescr=True):
        """
        create a hyperlink for the media object and returns it

        @param: handle   -- Document handle
        @param: name     -- Document name
        @param: uplink   -- If True, then "../../../" is inserted in front of
                            the result.
        @param: usedescr -- Add description to hyperlink
        """
        url = self.report.build_url_fname_html(handle, "img", uplink)
        name = html_escape(name)

        # begin thumbnail division
        with Html("div", class_="thumbnail") as thumbnail:
            document_url = self.report.build_url_image("document.png",
                                                       "images", uplink)

            if not self.create_thumbs_only:
                document_link = Html("a", href=url, title=name) + (
                    Html("img", src=document_url, alt=name)
                )
            else:
                document_link = Html("img", src=document_url, alt=name)

            if usedescr:
                document_link += Html('br') + (
                    Html("span", name, inline=True)
                )
            thumbnail += document_link
        return thumbnail

    def place_link(self, handle, name, gid=None, uplink=False):
        """
        Returns a hyperlink for place link

        @param: handle -- repository handle from report database
        @param: name   -- repository title
        @param: gid    -- gramps id
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        url = self.report.build_url_fname_html(handle, "plc", uplink)

        hyper = Html("a", html_escape(name), href=url, title=html_escape(name))
        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_="grampsid", inline=True)

        # return hyperlink to its callers
        return hyper

    def dump_place(self, place, table):
        """
        Dump a place's information from within the database

        @param: place -- Place object from the database
        @param: table -- Table from Placedetail
        """
        if place in self.report.visited:
            return
        self.report.visited.append(place)
        # add table body
        tbody = Html("tbody")
        table += tbody

        gid = place.gramps_id
        if not self.noid and gid:
            trow = Html("tr") + (
                Html("td", GRAMPSID, class_="ColumnAttribute", inline=True),
                Html("td", gid, class_="ColumnValue", inline=True)
            )
            tbody += trow

        data = place.get_latitude()
        if data != "":
            trow = Html('tr') + (
                Html("td", LATITUDE, class_="ColumnAttribute", inline=True),
                Html("td", data, class_="ColumnValue", inline=True)
            )
            tbody += trow
        data = place.get_longitude()
        if data != "":
            trow = Html('tr') + (
                Html("td", LONGITUDE, class_="ColumnAttribute", inline=True),
                Html("td", data, class_="ColumnValue", inline=True)
            )
            tbody += trow

        mlocation = get_main_location(self.dbase_, place)
        for (label, data) in [
            (STREET, mlocation.get(PlaceType.STREET, '')),
            (LOCALITY, mlocation.get(PlaceType.LOCALITY, '')),
            (CITY, mlocation.get(PlaceType.CITY, '')),
            (PARISH, mlocation.get(PlaceType.PARISH, '')),
            (COUNTY, mlocation.get(PlaceType.COUNTY, '')),
            (STATE, mlocation.get(PlaceType.STATE, '')),
            (POSTAL, place.get_code()),
            (COUNTRY, mlocation.get(PlaceType.COUNTRY, ''))]:
            if data:
                trow = Html("tr") + (
                    Html("td", label, class_="ColumnAttribute", inline=True),
                    Html("td", data, class_="ColumnValue", inline=True)
                )
                tbody += trow

        altloc = place.get_alternate_locations()
        if altloc:
            tbody += Html("tr") + Html("td", "&nbsp;", colspan=2)
            trow = Html("tr") + (
                    Html("th", ALT_LOCATIONS, colspan=2,
                         class_="ColumnAttribute", inline=True),
            )
            tbody += trow
            for loc in (nonempt for
                           nonempt in altloc if not nonempt.is_empty()):
                for (label, data) in [
                    (STREET, loc.street),
                    (LOCALITY, loc.locality),
                    (CITY, loc.city),
                    (PARISH, loc.parish),
                    (COUNTY, loc.county),
                    (STATE, loc.state),
                    (POSTAL, loc.postal),
                    (COUNTRY, loc.country),]:
                    if data:
                        trow = Html("tr") + (
                            Html("td", label, class_="ColumnAttribute",
                                 inline=True),
                            Html("td", data, class_="ColumnValue", inline=True)
                        )
                        tbody += trow
                tbody += Html("tr") + Html("td", "&nbsp;", colspan=2)

        # display all related locations
        for placeref in place.get_placeref_list():
            place_date = get_date(placeref)
            if place_date != "":
                parent_place = self.dbase_.get_place_from_handle(placeref.ref)
                parent_name = parent_place.get_name().get_value()
                trow = Html('tr') + (
                    Html("td", LOCATIONS, class_="ColumnAttribute",
                         inline=True),
                    Html("td", parent_name, class_="ColumnValue", inline=True),
                    Html("td", place_date, class_="ColumnValue", inline=True)
                )
                tbody += trow

        # return place table to its callers
        return table

    def repository_link(self, repository_handle, name, gid=None, uplink=False):
        """
        Returns a hyperlink for repository links

        @param: repository_handle -- repository handle from report database
        @param: name              -- repository title
        @param: gid               -- gramps id
        @param: uplink            -- If True, then "../../../" is inserted in
                                     front of the result.
        """
        url = self.report.build_url_fname_html(repository_handle,
                                               'repo', uplink)
        name = html_escape(name)

        hyper = Html("a", name, href=url, title=name)

        if not self.noid and gid:
            hyper += Html("span", '[%s]' % gid, class_="grampsid", inline=True)
        return hyper

    def dump_repository_ref_list(self, repo_ref_list):
        """
        Dumps the repository

        @param: repo_ref_list -- The list of repositories references
        """
        if len(repo_ref_list) == 0:
            return None
        # Repository list division...
        with Html("div", class_="subsection",
                  id="repositories") as repositories:
            repositories += Html("h4", _("Repositories"), inline=True)

            with Html("table", class_="infolist") as table:
                repositories += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", _("Number"), class_="ColumnRowLabel",
                         inline=True),
                    Html("th", _("Title"), class_="ColumnName", inline=True),
                    Html("th", _("Type"), class_="ColumnName", inline=True),
                    Html("th", _("Call number"), class_="ColumnName",
                         inline=True)
                )
                thead += trow

                tbody = Html("tbody")
                table += tbody

                index = 1
                for repo_ref in repo_ref_list:
                    repository = self.dbase_.get_repository_from_handle(
                                                                 repo_ref.ref)
                    if repository:

                        trow = Html("tr") + (
                            Html("td", index, class_="ColumnRowLabel",
                                 inline=True),
                            Html("td",
                                 self.repository_link(repo_ref.ref,
                                                 repository.get_name(),
                                                 repository.get_gramps_id(),
                                                 self.uplink)),
                            Html("td", repo_ref.get_media_type(),
                                 class_="ColumnName"),
                            Html("td", repo_ref.get_call_number(),
                                 class_="ColumnName")
                        )
                        tbody += trow
                        index += 1
        return repositories

    def dump_residence(self, has_res):
        """
        Creates a residence from the database

        @param: has_res -- The residence to use
        """
        if not has_res:
            return None

        # begin residence division
        with Html("div", class_="content Residence") as residence:
            residence += Html("h4", _("Residence"), inline=True)

            with Html("table", class_="infolist place") as table:
                residence += table

                place_handle = has_res.get_place_handle()
                if place_handle:
                    place = self.report.database.get_place_from_handle(
                                                                place_handle)
                    if place:
                        self.dump_place(place, table)

                descr = has_res.get_description()
                if descr:

                    trow = Html("tr")
                    if len(table) == 3:
                        # append description row to tbody element of dump_place
                        table[-2] += trow
                    else:
                        # append description row to table element
                        table += trow

                    trow.extend(Html("td", DESCRHEAD,
                                     class_="ColumnAttribute", inline=True))
                    trow.extend(Html("td", descr, class_="ColumnValue",
                                     inline=True))

        # return information to its callers
        return residence

    def display_bkref(self, bkref_list, depth):
        """
        Display a reference list for an object class

        @param: bkref_list -- The reference list
        @param: depth      -- The style of list to use
        """
        list_style = "1", "a", "I", "A", "i"
        ordered = Html("ol", class_="Col1", role="Volume-n-Page")
        ordered.attr += "type = %s" % list_style[depth]
        if depth > len(list_style):
            return ""
        # Sort by the name of the object at the bkref_class, bkref_handle
        # bug 8950 : it seems it's better to sort on name + gid.
        def sort_by_name_and_gid(obj):
            """
            Sort by name then gramps ID
            """
            return (obj[1], obj[2])

        for (bkref_class, bkref_handle) in sorted(
                bkref_list, key=lambda x:
                      sort_by_name_and_gid(self.report.obj_dict[x[0]][x[1]])):
            list_html = Html("li")
            path = self.report.obj_dict[bkref_class][bkref_handle][0]
            name = self.report.obj_dict[bkref_class][bkref_handle][1]
            gid = self.report.obj_dict[bkref_class][bkref_handle][2]
            ordered += list_html
            if path == "":
                list_html += name
                list_html += self.display_bkref(
                            self.report.bkref_dict[bkref_class][bkref_handle],
                            depth+1)
            else:
                url = self.report.build_url_fname(path, uplink=self.uplink)
                if not self.noid and gid != "":
                    gid_html = Html("span", " [%s]" % gid,
                                     class_="grampsid", inline=True)
                else:
                    gid_html = ""
                list_html += Html("a", href=url) + name + gid_html
        return ordered

    def display_bkref_list(self, obj_class, obj_handle):
        """
        Display a reference list for an object class

        @param: obj_class  -- The object class to use
        @param: obj_handle -- The handle to use
        """
        bkref_list = self.report.bkref_dict[obj_class][obj_handle]
        if not bkref_list:
            return None
        # begin references division and title
        with Html("div", class_="subsection", id="references") as section:
            section += Html("h4", _("References"), inline=True)
            depth = 0
            ordered = self.display_bkref(bkref_list, depth)
            section += ordered
        return section

    # -------------------------------------------------------------------------
    #              # Web Page Fortmatter and writer
    # -------------------------------------------------------------------------
    def xhtml_writer(self, htmlinstance, output_file, sio, date):
        """
        Will format, write, and close the file

        @param: output_file  -- Open file that is being written to
        @param: htmlinstance -- Web page created with libhtml
                                src/plugins/lib/libhtml.py
        """
        htmlinstance.write(partial(print, file=output_file))

        # closes the file
        self.report.close_file(output_file, sio, date)

#################################################
#
#    create the page from SurnameListPage
#
#################################################
class SurnamePage(BasePage):
    """
    This will create a list of individuals with the same surname
    """
    def __init__(self, report, title, surname, ppl_handle_list):
        """
        @param: report          -- The instance of the main report class for
                                   this report
        @param: title           -- Is the title of the web page
        @param: surname         -- The surname to use
        @param: ppl_handle_list -- The list of people for whom we need to create
                                   a page.
        """
        BasePage.__init__(self, report, title)

        # module variables
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        if surname == '':
            surname = _ABSENT

        output_file, sio = self.report.create_file(name_to_md5(surname), "srn")
        self.uplink = True
        (surnamepage, head,
         body) = self.write_header("%s - %s" % (_("Surname"), surname))
        ldatec = 0

        # begin SurnameDetail division
        with Html("div", class_="content", id="SurnameDetail") as surnamedetail:
            body += surnamedetail

            # section title
            surnamedetail += Html("h3", html_escape(surname), inline=True)

            # feature request 2356: avoid genitive form
            msg = _("This page contains an index of all the individuals in the "
                    "database with the surname of %s. "
                    "Selecting the person&#8217;s name "
                    "will take you to that person&#8217;s "
                    "individual page.") % html_escape(surname)
            surnamedetail += Html("p", msg, id="description")

            # begin surname table and thead
            with Html("table", class_="infolist primobjlist surname") as table:
                surnamedetail += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # Name Column
                trow += Html("th", _("Given Name"), class_="ColumnName",
                             inline=True)

                if showbirth:
                    trow += Html("th", _("Birth"), class_="ColumnDate",
                                 inline=True)

                if showdeath:
                    trow += Html("th", _("Death"), class_="ColumnDate",
                                 inline=True)

                if showpartner:
                    trow += Html("th", _("Partner"), class_="ColumnPartner",
                                 inline=True)

                if showparents:
                    trow += Html("th", _("Parents"), class_="ColumnParents",
                                 inline=True)

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for person_handle in sorted(ppl_handle_list,
                       key=lambda x: sort_on_name_and_grampsid(x, self.dbase_)):

                    person = self.dbase_.get_person_from_handle(person_handle)
                    if person.get_change_time() > ldatec:
                        ldatec = person.get_change_time()
                    trow = Html("tr")
                    tbody += trow

                    # firstname column
                    link = self.new_person_link(person_handle, uplink=True,
                                                 person=person,
                                                 name_style=_NAME_STYLE_FIRST)
                    trow += Html("td", link, class_="ColumnName")

                    # birth column
                    if showbirth:
                        tcell = Html("td", class_="ColumnBirth", inline=True)
                        trow += tcell

                        birth_date = _find_birth_date(self.dbase_, person)
                        if birth_date is not None:
                            if birth_date.fallback:
                                tcell += Html('em', _dd.display(birth_date),
                                              inline=True)
                            else:
                                tcell += _dd.display(birth_date)
                        else:
                            tcell += "&nbsp;"

                    # death column
                    if showdeath:
                        tcell = Html("td", class_="ColumnDeath", inline=True)
                        trow += tcell

                        death_date = _find_death_date(self.dbase_, person)
                        if death_date is not None:
                            if death_date.fallback:
                                tcell += Html('em', _dd.display(death_date),
                                              inline=True)
                            else:
                                tcell += _dd.display(death_date)
                        else:
                            tcell += "&nbsp;"

                    # partner column
                    if showpartner:
                        tcell = Html("td", class_="ColumnPartner")
                        trow += tcell
                        family_list = person.get_family_handle_list()
                        first_family = True
                        if family_list:
                            for family_handle in family_list:
                                family = self.dbase_.get_family_from_handle(
                                                                family_handle)
                                partner_handle = ReportUtils.find_spouse(person,
                                                                         family)
                                if partner_handle:
                                    if not first_family:
                                        tcell += ','
                                    tcell += self.new_person_link(
                                                             partner_handle,
                                                             uplink=True)
                                    first_family = False
                        else:
                            tcell += "&nbsp;"

                    # parents column
                    if showparents:
                        parent_handle_list = person.get_parent_family_handle_list()
                        if parent_handle_list:
                            parent_handle = parent_handle_list[0]
                            family = self.dbase_.get_family_from_handle(
                                                                 parent_handle)
                            father_id = family.get_father_handle()
                            mother_id = family.get_mother_handle()
                            mother = father = None
                            if father_id:
                                father = self.dbase_.get_person_from_handle(
                                                                     father_id)
                                if father:
                                    father_name = self.get_name(father)
                            if mother_id:
                                mother = self.dbase_.get_person_from_handle(
                                                                     mother_id)
                                if mother:
                                    mother_name = self.get_name(mother)
                            if mother and father:
                                tcell = Html("span", father_name,
                                             class_="father fatherNmother")
                                tcell += Html("span", mother_name,
                                              class_="mother")
                            elif mother:
                                tcell = Html("span", mother_name,
                                             class_="mother", inline=True)
                            elif father:
                                tcell = Html("span", father_name,
                                             class_="father", inline=True)
                            samerow = False
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", tcell,
                                     class_="ColumnParents", inline=samerow)

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(surnamepage, output_file, sio, ldatec)

#################################################
#
#    creates the Family List Page and Family Pages
#
#################################################
class FamilyPages(BasePage):
    """
    This class is responsible for displaying information about the 'Family'
    database objects. It displays this information under the 'Families'
    tab. It is told by the 'add_instances' call which 'Family's to display,
    and remembers the list of Family. A single call to 'display_pages'
    displays both the Family List (Index) page and all the Family
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")
        self.family_dict = defaultdict(set)
        self.person = None
        self.familymappages = None

    def display_pages(self, title):
        """
        Generate and output the pages under the Family tab, namely the family
        index and the individual family pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Family]")
        for item in self.report.obj_dict[Family].items():
            LOG.debug("    %s", str(item))

        with self.report.user.progress(_("Narrated Web Site Report"),
                                 _("Creating family pages..."),
                                 len(self.report.obj_dict[Family]) + 1) as step:
            self.familylistpage(self.report, title,
                                self.report.obj_dict[Family].keys())

            for family_handle in self.report.obj_dict[Family]:
                step()
                self.familypage(self.report, title, family_handle)

    def familylistpage(self, report, title, fam_list):
        """
        Create a family index

        @param: report   -- The instance of the main report class for
                            this report
        @param: title    -- Is the title of the web page
        @param: fam_list -- The handle for the place to add
        """
        BasePage.__init__(self, report, title)

        output_file, sio = self.report.create_file("families")
        familieslistpage, head, body = self.write_header(_("Families"))
        ldatec = 0
        prev_letter = " "

        # begin Family Division
        with Html("div", class_="content", id="Relationships") as relationlist:
            body += relationlist

            # Families list page message
            msg = _("This page contains an index of all the "
                    "families/ relationships in the "
                    "database, sorted by their family name/ surname. "
                    "Clicking on a person&#8217;s "
                    "name will take you to their "
                    "family/ relationship&#8217;s page.")
            relationlist += Html("p", msg, id="description")

            # go through all the families, and construct a dictionary of all the
            # people and the families thay are involved in. Note that the people
            # in the list may be involved in OTHER families, that are not listed
            # because they are not in the original family list.
            pers_fam_dict = defaultdict(list)
            for family_handle in fam_list:
                family = self.dbase_.get_family_from_handle(family_handle)
                if family:
                    if family.get_change_time() > ldatec:
                        ldatec = family.get_change_time()
                    husband_handle = family.get_father_handle()
                    spouse_handle = family.get_mother_handle()
                    if husband_handle:
                        pers_fam_dict[husband_handle].append(family)
                    if spouse_handle:
                        pers_fam_dict[spouse_handle].append(family)

            # add alphabet navigation
            index_list = get_first_letters(self.dbase_, pers_fam_dict.keys(),
                                           _KEYPERSON)
            alpha_nav = alphabet_navigation(index_list)
            if alpha_nav:
                relationlist += alpha_nav

            # begin families table and table head
            with Html("table", class_="infolist relationships") as table:
                relationlist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

               # set up page columns
                trow.extend(
                    Html("th", trans, class_=colclass, inline=True)
                        for trans, colclass in [
                            (_("Letter"), "ColumnRowLabel"),
                            (_("Person"), "ColumnPartner"),
                            (_("Family"), "ColumnPartner"),
                            (_("Marriage"), "ColumnDate"),
                            (_("Divorce"), "ColumnDate")
                        ]
                )

                tbody = Html("tbody")
                table += tbody

                # begin displaying index list
                ppl_handle_list = sort_people(self.dbase_, pers_fam_dict.keys())
                first = True
                for (surname, handle_list) in ppl_handle_list:

                    if surname and not surname.isspace():
                        letter = get_index_letter(first_letter(surname),
                                                  index_list)
                    else:
                        letter = '&nbsp;'

                    # get person from sorted database list
                    for person_handle in sorted(handle_list,
                          key=lambda x: sort_on_name_and_grampsid(x,
                                                                  self.dbase_)):
                        person = self.dbase_.get_person_from_handle(
                                                             person_handle)
                        if person:
                            family_list = sorted(pers_fam_dict[person_handle],
                                                 key=lambda x: x.get_gramps_id()
                                                )
                            first_family = True
                            for family in family_list:
                                trow = Html("tr")
                                tbody += trow

                                tcell = Html("td", class_="ColumnRowLabel")
                                trow += tcell

                                if first or primary_difference(letter,
                                                               prev_letter):
                                    first = False
                                    prev_letter = letter
                                    trow.attr = 'class="BeginLetter"'
                                    ttle = _("Families beginning with letter ")
                                    tcell += Html("a", letter, name=letter,
                                                  title=ttle + letter,
                                                  inline=True)
                                else:
                                    tcell += '&nbsp;'

                                tcell = Html("td", class_="ColumnPartner")
                                trow += tcell

                                if first_family:
                                    trow.attr = 'class ="BeginFamily"'

                                    tcell += self.new_person_link(person_handle,
                                                             uplink=self.uplink)

                                    first_family = False
                                else:
                                    tcell += '&nbsp;'

                                tcell = Html("td", class_="ColumnPartner")
                                trow += tcell

                                tcell += self.family_link(
                                    family.get_handle(),
                                    self.report.get_family_name(family),
                                    family.get_gramps_id(), self.uplink)

                                # family events; such as marriage and divorce
                                # events
                                fam_evt_ref_list = family.get_event_ref_list()
                                tcell1 = Html("td", class_="ColumnDate",
                                              inline=True)
                                tcell2 = Html("td", class_="ColumnDate",
                                              inline=True)
                                trow += (tcell1, tcell2)

                                if fam_evt_ref_list:
                                    def sort_on_grampsid(obj):
                                        """
                                        Sort on gramps ID
                                        """
                                        evt = self.dbase_.get_event_from_handle(
                                                                    obj.ref)
                                        return evt.get_gramps_id()

                                    fam_evt_srt_ref_list = sorted(
                                            fam_evt_ref_list,
                                            key=lambda x: sort_on_grampsid(x))
                                    for evt_ref in fam_evt_srt_ref_list:
                                        evt = self.dbase_.get_event_from_handle(
                                                                    evt_ref.ref)
                                        if evt:
                                            evt_type = evt.get_type()
                                            if evt_type in [EventType.MARRIAGE,
                                                            EventType.DIVORCE]:

                                                if (evt_type ==
                                                            EventType.MARRIAGE):
                                                    tcell1 += _dd.display(
                                                          evt.get_date_object())
                                                else:
                                                    tcell1 += '&nbsp;'

                                                if (evt_type ==
                                                            EventType.DIVORCE):
                                                    tcell2 += _dd.display(
                                                          evt.get_date_object())
                                                else:
                                                    tcell2 += '&nbsp;'
                                else:
                                    tcell1 += '&nbsp;'
                                    tcell2 += '&nbsp;'
                                first_family = False

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familieslistpage, output_file, sio, ldatec)

    def familypage(self, report, title, family_handle):
        """
        Create a family page

        @param: report        -- The instance of the main report class for
                                 this report
        @param: title         -- Is the title of the web page
        @param: family_handle -- The handle for the family to add
        """
        family = report.database.get_family_from_handle(family_handle)
        if not family:
            return
        BasePage.__init__(self, report, title, family.get_gramps_id())
        ldatec = family.get_change_time()

        self.bibli = Bibliography()
        self.uplink = True
        family_name = self.report.get_family_name(family)
        self.page_title = family_name

        self.familymappages = report.options["familymappages"]

        output_file, sio = self.report.create_file(family.get_handle(), "fam")
        familydetailpage, head, body = self.write_header(family_name)

        # begin FamilyDetaill division
        with Html("div", class_="content",
                  id="RelationshipDetail") as relationshipdetail:
            body += relationshipdetail

            # family media list for initial thumbnail
            if self.create_media:
                media_list = family.get_media_list()
                # If Event pages are not being created, then we need to display
                # the family event media here
                if not self.inc_events:
                    for evt_ref in family.get_event_ref_list():
                        event = self.dbase_.get_event_from_handle(evt_ref.ref)
                        media_list += event.get_media_list()
                thumbnail = self.disp_first_img_as_thumbnail(media_list,
                                                                  family)
                if thumbnail:
                    relationshipdetail += thumbnail

            self.person = None   # no longer used

            relationshipdetail += Html("h2", self.page_title, inline=True) +\
                (Html('sup') +\
                 (Html('small') +
                  self.get_citation_links(family.get_citation_list())))

            # display relationships
            families = self.display_family_relationships(family, None)
            if families is not None:
                relationshipdetail += families

            # display additional images as gallery
            if self.create_media and media_list:
                addgallery = self.disp_add_img_as_gallery(media_list, family)
                if addgallery:
                    relationshipdetail += addgallery

            # Narrative subsection
            notelist = family.get_note_list()
            if notelist:
                relationshipdetail += self.display_note_list(notelist)

            # display family LDS ordinance...
            family_lds_ordinance_list = family.get_lds_ord_list()
            if family_lds_ordinance_list:
                relationshipdetail += self.display_lds_ordinance(family)

            # get attribute list
            attrlist = family.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                relationshipdetail += attrsection

            # source references
            srcrefs = self.display_ind_sources(family)
            if srcrefs:
                relationshipdetail += srcrefs

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familydetailpage, output_file, sio, ldatec)

######################################################
#                                                    #
#                    Place Pages                     #
#                                                    #
######################################################
class PlacePages(BasePage):
    """
    This class is responsible for displaying information about the 'Person'
    database objects. It displays this information under the 'Events'
    tab. It is told by the 'add_instances' call which 'Person's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Event List (Index) page and all the Event
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")
        self.place_dict = defaultdict(set)
        self.placemappages = None
        self.mapservice = None
        self.person = None
        self.familymappages = None

    def display_pages(self, title):
        """
        Generate and output the pages under the Place tab, namely the place
        index and the individual place pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Place]")
        for item in self.report.obj_dict[Place].items():
            LOG.debug("    %s", str(item))
        with self.report.user.progress(_("Narrated Web Site Report"),
                                  _("Creating place pages"),
                                  len(self.report.obj_dict[Place]) + 1) as step:

            self.placelistpage(self.report, title,
                               self.report.obj_dict[Place].keys())

            for place_handle in self.report.obj_dict[Place]:
                step()
                self.placepage(self.report, title, place_handle)

    def placelistpage(self, report, title, place_handles):
        """
        Create a place index

        @param: report        -- The instance of the main report class for
                                 this report
        @param: title         -- Is the title of the web page
        @param: place_handles -- The handle for the place to add
        """
        BasePage.__init__(self, report, title)

        output_file, sio = self.report.create_file("places")
        placelistpage, head, body = self.write_header(_("Places"))
        ldatec = 0
        prev_letter = " "

        # begin places division
        with Html("div", class_="content", id="Places") as placelist:
            body += placelist

            # place list page message
            msg = _("This page contains an index of all the places in the "
                          "database, sorted by their title. "
                          "Clicking on a place&#8217;s "
                          "title will take you to that place&#8217;s page.")
            placelist += Html("p", msg, id="description")

            # begin alphabet navigation
            index_list = get_first_letters(self.dbase_, place_handles,
                                           _KEYPLACE)
            alpha_nav = alphabet_navigation(index_list)
            if alpha_nav is not None:
                placelist += alpha_nav

            # begin places table and table head
            with Html("table",
                      class_="infolist primobjlist placelist") as table:
                placelist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        [_("Letter"), "ColumnLetter"],
                        [_("Place Name | Name"), "ColumnName"],
                        [_("State"), "ColumnState"],
                        [_("Country"), "ColumnCountry"],
                        [_("Latitude"), "ColumnLatitude"],
                        [_("Longitude"), "ColumnLongitude"]]
                )

                handle_list = sorted(place_handles,
                                     key=lambda x:
                              SORT_KEY(ReportUtils.place_name(self.dbase_, x)))
                first = True

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for place_handle in handle_list:
                    place = self.dbase_.get_place_from_handle(place_handle)
                    if place:
                        if place.get_change_time() > ldatec:
                            ldatec = place.get_change_time()
                        place_title = ReportUtils.place_name(self.dbase_,
                                                             place_handle)
                        main_location = get_main_location(self.dbase_, place)

                        if place_title and not place_title.isspace():
                            letter = get_index_letter(first_letter(place_title),
                                                      index_list)
                        else:
                            letter = '&nbsp;'

                        trow = Html("tr")
                        tbody += trow

                        tcell = Html("td", class_="ColumnLetter", inline=True)
                        trow += tcell
                        if first or primary_difference(letter, prev_letter):
                            first = False
                            prev_letter = letter
                            trow.attr = 'class = "BeginLetter"'

                            ttle = _("Places beginning with letter %s") % letter
                            tcell += Html("a", letter, name=letter, title=ttle)
                        else:
                            tcell += "&nbsp;"

                        trow += Html("td", self.place_link(place.get_handle(),
                                     place_title, place.get_gramps_id()),
                            class_="ColumnName")

                        trow.extend(
                            Html("td", data or "&nbsp;", class_=colclass,
                                 inline=True)
                            for (colclass, data) in [
                                       ["ColumnState",
                                        main_location.get(PlaceType.STATE,
                                        '')],
                                       ["ColumnCountry",
                                        main_location.get(PlaceType.COUNTRY,
                                        '')]]
                        )

                        tcell1 = Html("td", class_="ColumnLatitude",
                                      inline=True)
                        tcell2 = Html("td", class_="ColumnLongitude",
                                      inline=True)
                        trow += (tcell1, tcell2)

                        if place.lat and place.long:
                            latitude, longitude = conv_lat_lon(place.lat,
                                                               place.long,
                                                               "DEG")
                            tcell1 += latitude
                            tcell2 += longitude
                        else:
                            tcell1 += '&nbsp;'
                            tcell2 += '&nbsp;'

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(placelistpage, output_file, sio, ldatec)

    def placepage(self, report, title, place_handle):
        """
        Create a place page

        @param: report            -- The instance of the main report class for
                                     this report
        @param: title             -- Is the title of the web page
        @param: place_handle -- The handle for the place to add
        """
        place = report.database.get_place_from_handle(place_handle)
        if not place:
            return None
        BasePage.__init__(self, report, title, place.get_gramps_id())
        self.bibli = Bibliography()
        place_name = self.report.obj_dict[Place][place_handle][1]
        ldatec = place.get_change_time()

        output_file, sio = self.report.create_file(place_handle, "plc")
        self.uplink = True
        self.page_title = _pd.display(self.dbase_, place)
        placepage, head, body = self.write_header(_("Places"))

        self.placemappages = self.report.options['placemappages']
        self.mapservice = self.report.options['mapservice']

        # begin PlaceDetail Division
        with Html("div", class_="content", id="PlaceDetail") as placedetail:
            body += placedetail

            if self.create_media:
                media_list = place.get_media_list()
                thumbnail = self.disp_first_img_as_thumbnail(media_list,
                                                                  place)
                if thumbnail is not None:
                    placedetail += thumbnail

            # add section title
            placedetail += Html("h3", html_escape(place.get_name().get_value()),
                                inline=True)

            # begin summaryarea division and places table
            with Html("div", id='summaryarea') as summaryarea:
                placedetail += summaryarea

                with Html("table", class_="infolist place") as table:
                    summaryarea += table

                    # list the place fields
                    self.dump_place(place, table)

            # place gallery
            if self.create_media:
                placegallery = self.disp_add_img_as_gallery(media_list, place)
                if placegallery is not None:
                    placedetail += placegallery

            # place notes
            notelist = self.display_note_list(place.get_note_list())
            if notelist is not None:
                placedetail += notelist

            # place urls
            urllinks = self.display_url_list(place.get_url_list())
            if urllinks is not None:
                placedetail += urllinks

            # add place map here
            if self.placemappages:
                if place and (place.lat and place.long):
                    latitude, longitude = conv_lat_lon(place.get_latitude(),
                                                       place.get_longitude(),
                                                       "D.D8")
                    placetitle = place_name

                    # add narrative-maps CSS...
                    fname = "/".join(["css", "narrative-maps.css"])
                    url = self.report.build_url_fname(fname, None, self.uplink)
                    head += Html("link", href=url, type="text/css",
                                 media="screen", rel="stylesheet")

                    # add MapService specific javascript code
                    src_js = "http://maps.googleapis.com/maps/api/js?sensor=false"
                    if self.mapservice == "Google":
                        head += Html("script", type="text/javascript",
                                     src=src_js, inline=True)
                    else:
                        src_js = "http://www.openlayers.org/api/OpenLayers.js"
                        head += Html("script", type="text/javascript",
                                     src=src_js, inline=True)

                    # section title
                    placedetail += Html("h4", _("Place Map"), inline=True)

                    # begin map_canvas division
                    with Html("div", id="place_canvas", inline=True) as canvas:
                        placedetail += canvas

                        # Begin inline javascript code because jsc is a
                        # docstring, it does NOT have to be properly indented
                        if self.mapservice == "Google":
                            with Html("script", type="text/javascript",
                                      indent=False) as jsc:
                                head += jsc

                                # Google adds Latitude/ Longitude to its maps...
                                plce = placetitle.replace("'", "\\'")
                                jsc += GOOGLE_JSC % (latitude, longitude, plce)

                        else:
                            # OpenStreetMap (OSM) adds Longitude/ Latitude
                            # to its maps, and needs a country code in
                            # lowercase letters...
                            with Html("script", type="text/javascript") as jsc:
                                canvas += jsc
                                param1 = xml_lang()[3:5].lower()
                                jsc += OPENSTREETMAP_JSC % (param1, longitude,
                                                            latitude)

            # add javascript function call to body element
            body.attr += ' onload = "initialize();" '

            # source references
            srcrefs = self.display_ind_sources(place)
            if srcrefs is not None:
                placedetail += srcrefs

            # References list
            ref_list = self.display_bkref_list(Place, place_handle)
            if ref_list is not None:
                placedetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(placepage, output_file, sio, ldatec)

#################################################
#
#    creates the Event List Page and EventPages
#
#################################################
class EventPages(BasePage):
    """
    This class is responsible for displaying information about the 'Person'
    database objects. It displays this information under the 'Events'
    tab. It is told by the 'add_instances' call which 'Person's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Event List (Index) page and all the Event
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")
        self.event_handle_list = []
        self.event_types = []
        self.event_dict = defaultdict(set)

    def display_pages(self, title):
        """
        Generate and output the pages under the Event tab, namely the event
        index and the individual event pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Event]")
        for item in self.report.obj_dict[Event].items():
            LOG.debug("    %s", str(item))
        event_handle_list = self.report.obj_dict[Event].keys()
        event_types = []
        for event_handle in event_handle_list:
            event = self.report.database.get_event_from_handle(event_handle)
            event_types.append(str(event.get_type()))
        with self.report.user.progress(_("Narrated Web Site Report"),
                                  _("Creating event pages"),
                                  len(event_handle_list) + 1) as step:
            self.eventlistpage(self.report, title, event_types,
                               event_handle_list)

            for event_handle in event_handle_list:
                step()
                self.eventpage(self.report, title, event_handle)


    def eventlistpage(self, report, title, event_types, event_handle_list):
        """
        Will create the event list page

        @param: report            -- The instance of the main report class for
                                     this report
        @param: title             -- Is the title of the web page
        @param: event_types       -- A list of the type in the events database
        @param: event_handle_list -- A list of event handles
        """
        BasePage.__init__(self, report, title)
        ldatec = 0
        prev_letter = " "

        output_file, sio = self.report.create_file("events")
        eventslistpage, head, body = self.write_header(_("Events"))

        # begin events list  division
        with Html("div", class_="content", id="EventList") as eventlist:
            body += eventlist

            msg = _("This page contains an index of all the events in the "
                    "database, sorted by their type and date (if one is "
                    "present). Clicking on an event&#8217;s Gramps ID "
                    "will open a page for that event.")
            eventlist += Html("p", msg, id="description")

            # get alphabet navigation...
            index_list = get_first_letters(self.dbase_, event_types,
                                           _ALPHAEVENT)
            alpha_nav = alphabet_navigation(index_list)
            if alpha_nav:
                eventlist += alpha_nav

            # begin alphabet event table
            with Html("table",
                      class_="infolist primobjlist alphaevent") as table:
                eventlist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            (_("Letter"), "ColumnRowLabel"),
                            (_("Type"), "ColumnType"),
                            (_("Date"), "ColumnDate"),
                            (_("Gramps ID"), "ColumnGRAMPSID"),
                            (_("Person"), "ColumnPerson")
                        ]
                )

                tbody = Html("tbody")
                table += tbody

                # separate events by their type and then thier event handles
                for (evt_type,
                     data_list) in sort_event_types(self.dbase_,
                                                    event_types,
                                                    event_handle_list):
                    first = True
                    _event_displayed = []

                    # sort datalist by date of event and by event handle...
                    data_list = sorted(data_list, key=itemgetter(0, 1))
                    first_event = True

                    for (sort_value, event_handle) in data_list:
                        event = self.dbase_.get_event_from_handle(event_handle)
                        _type = event.get_type()
                        gid = event.get_gramps_id()
                        if event.get_change_time() > ldatec:
                            ldatec = event.get_change_time()

                        # check to see if we have listed this gramps_id yet?
                        if gid not in _event_displayed:

                            # family event
                            if int(_type) in _EVENTMAP:
                                handle_list = set(
                                              self.dbase_.find_backlink_handles(
                                                  event_handle,
                                                  include_classes=['Family',
                                                                   'Person']))
                            else:
                                handle_list = set(
                                              self.dbase_.find_backlink_handles(
                                                  event_handle,
                                                  include_classes=['Person']))
                            if handle_list:

                                trow = Html("tr")
                                tbody += trow

                                # set up hyperlinked letter for
                                # alphabet_navigation
                                tcell = Html("td", class_="ColumnLetter",
                                             inline=True)
                                trow += tcell

                                if evt_type and not evt_type.isspace():
                                    letter = get_index_letter(
                                            str(evt_type)[0].capitalize(),
                                            index_list)
                                else:
                                    letter = "&nbsp;"

                                if first or primary_difference(letter,
                                                               prev_letter):
                                    first = False
                                    prev_letter = letter
                                    trow.attr = 'class = "BeginLetter BeginType"'
                                    ttle = _("Event types beginning with letter %s") % letter
                                    tcell += Html("a", letter, name=letter,
                                                  id_=letter, title=ttle,
                                                  inline=True)
                                else:
                                    tcell += "&nbsp;"

                                # display Event type if first in the list
                                tcell = Html("td", class_="ColumnType",
                                             title=evt_type, inline=True)
                                trow += tcell
                                if first_event:
                                    tcell += evt_type
                                    if trow.attr == "":
                                        trow.attr = 'class = "BeginType"'
                                else:
                                    tcell += "&nbsp;"

                                # event date
                                tcell = Html("td", class_="ColumnDate",
                                             inline=True)
                                trow += tcell
                                date = Date.EMPTY
                                if event:
                                    date = event.get_date_object()
                                    if date and date is not Date.EMPTY:
                                        tcell += _dd.display(date)
                                else:
                                    tcell += "&nbsp;"

                                # Gramps ID
                                trow += Html("td", class_="ColumnGRAMPSID") + (
                                    self.event_grampsid_link(event_handle,
                                                             gid, None)
                                    )

                                # Person(s) column
                                tcell = Html("td", class_="ColumnPerson")
                                trow += tcell

                                # classname can either be a person or a family
                                first_person = True

                                # get person(s) for ColumnPerson
                                sorted_list = sorted(handle_list)
                                self.complete_people(tcell, first_person,
                                                     sorted_list,
                                                     uplink=False)

                        _event_displayed.append(gid)
                        first_event = False

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page ut for processing
        # and close the file
        self.xhtml_writer(eventslistpage, output_file, sio, ldatec)

    def _geteventdate(self, event_handle):
        """
        Get the event date

        @param: event_handle -- The handle for the event to use
        """
        event_date = Date.EMPTY
        event = self.report.database.get_event_from_handle(event_handle)
        if event:
            date = event.get_date_object()
            if date:

                # returns the date in YYYY-MM-DD format
                return Date(date.get_year_calendar("Gregorian"),
                            date.get_month(), date.get_day())

        # return empty date string
        return event_date

    def event_grampsid_link(self, handle, grampsid, uplink):
        """
        Create a hyperlink from event handle, but show grampsid

        @param: handle   -- The handle for the event
        @param: grampsid -- The gramps ID to display
        @param: uplink   -- If True, then "../../../" is inserted in front of
                            the result.
        """
        url = self.report.build_url_fname_html(handle, "evt", uplink)

        # return hyperlink to its caller
        return Html("a", grampsid, href=url, title=grampsid, inline=True)

    def eventpage(self, report, title, event_handle):
        """
        Creates the individual event page

        @param: report       -- The instance of the main report class for
                                this report
        @param: title        -- Is the title of the web page
        @param: event_handle -- The event handle for the database
        """
        event = report.database.get_event_from_handle(event_handle)
        BasePage.__init__(self, report, title, event.get_gramps_id())
        if not event:
            return None

        ldatec = event.get_change_time()
        event_media_list = event.get_media_list()

        self.uplink = True
        subdirs = True
        evt_type = str(event.get_type())
        self.page_title = "%(eventtype)s" % {'eventtype' : evt_type}
        self.bibli = Bibliography()

        output_file, sio = self.report.create_file(event_handle, "evt")
        eventpage, head, body = self.write_header(_("Events"))

        # start event detail division
        with Html("div", class_="content", id="EventDetail") as eventdetail:
            body += eventdetail

            thumbnail = self.disp_first_img_as_thumbnail(event_media_list,
                                                              event)
            if thumbnail is not None:
                eventdetail += thumbnail

            # display page title
            eventdetail += Html("h3", self.page_title, inline=True)

            # begin eventdetail table
            with Html("table", class_="infolist eventlist") as table:
                eventdetail += table

                tbody = Html("tbody")
                table += tbody

                evt_gid = event.get_gramps_id()
                if not self.noid and evt_gid:
                    trow = Html("tr") + (
                        Html("td", _("Gramps ID"),
                             class_="ColumnAttribute", inline=True),
                        Html("td", evt_gid,
                             class_="ColumnGRAMPSID", inline=True)
                        )
                    tbody += trow

                # get event data
                #
                # for more information: see get_event_data()
                #
                event_data = self.get_event_data(event, event_handle,
                                                 subdirs, evt_gid)

                for (label, colclass, data) in event_data:
                    if data:
                        trow = Html("tr") + (
                            Html("td", label, class_="ColumnAttribute",
                                 inline=True),
                            Html('td', data, class_="Column" + colclass)
                            )
                        tbody += trow

            # Narrative subsection
            notelist = event.get_note_list()
            notelist = self.display_note_list(notelist)
            if notelist is not None:
                eventdetail += notelist

            # get attribute list
            attrlist = event.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                eventdetail += attrsection

            # event source references
            srcrefs = self.display_ind_sources(event)
            if srcrefs is not None:
                eventdetail += srcrefs

            # display additional images as gallery
            if self.create_media:
                addgallery = self.disp_add_img_as_gallery(event_media_list,
                                                          event)
                if addgallery:
                    eventdetail += addgallery

            # References list
            ref_list = self.display_bkref_list(Event, event_handle)
            if ref_list is not None:
                eventdetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the page
        self.xhtml_writer(eventpage, output_file, sio, ldatec)

#################################################
#
#    Creates the Surname List page
#
#################################################
class SurnameListPage(BasePage):
    """
    This class is responsible for displaying the list of Surnames
    """
    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1

    def __init__(self, report, title, ppl_handle_list,
                 order_by=ORDER_BY_NAME, filename="surnames"):
        """
        @param: report          -- The instance of the main report class for
                                   this report
        @param: title           -- Is the title of the web page
        @param: ppl_handle_list -- The list of people for whom we need to create
                                   a page.
        @param: order_by        -- The way to sort surnames :
                                   Surnames or Surnames count
        @param: filename        -- The name to use for the Surnames page
        """
        BasePage.__init__(self, report, title)
        prev_surname = ""
        prev_letter = " "

        if order_by == self.ORDER_BY_NAME:
            output_file, sio = self.report.create_file(filename)
            surnamelistpage, head, body = self.write_header(_('Surnames'))
        else:
            output_file, sio = self.report.create_file("surnames_count")
            (surnamelistpage, head,
             body) = self.write_header(_('Surnames by person count'))

        # begin surnames division
        with Html("div", class_="content", id="surnames") as surnamelist:
            body += surnamelist

            # page message
            msg = _('This page contains an index of all the '
                    'surnames in the database. Selecting a link '
                    'will lead to a list of individuals in the '
                    'database with this same surname.')
            surnamelist += Html("p", msg, id="description")

            # add alphabet navigation...
            # only if surname list not surname count
            if order_by == self.ORDER_BY_NAME:
                index_list = get_first_letters(self.dbase_, ppl_handle_list,
                                               _KEYPERSON)
                alpha_nav = alphabet_navigation(index_list)
                if alpha_nav is not None:
                    surnamelist += alpha_nav

            if order_by == self.ORDER_BY_COUNT:
                table_id = 'SortByCount'
            else:
                table_id = 'SortByName'

            # begin surnamelist table and table head
            with Html("table", class_="infolist primobjlist surnamelist",
                      id=table_id) as table:
                surnamelist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow += Html("th", _("Letter"), class_="ColumnLetter",
                             inline=True)

                # create table header surname hyperlink
                fname = self.report.surname_fname + self.ext
                tcell = Html("th", class_="ColumnSurname", inline=True)
                trow += tcell
                hyper = Html("a", _("Surname"), href=fname, title=_("Surnames"))
                tcell += hyper

                # create table header number of people hyperlink
                fname = "surnames_count" + self.ext
                tcell = Html("th", class_="ColumnQuantity", inline=True)
                trow += tcell
                num_people = _("Number of People")
                hyper = Html("a", num_people, href=fname, title=num_people)
                tcell += hyper

                # begin table body
                with Html("tbody") as tbody:
                    table += tbody

                    ppl_handle_list = sort_people(self.dbase_, ppl_handle_list)
                    if order_by == self.ORDER_BY_COUNT:
                        temp_list = {}
                        for (surname, data_list) in ppl_handle_list:
                            index_val = "%90d_%s" % (999999999-len(data_list),
                                                     surname)
                            temp_list[index_val] = (surname, data_list)

                        ppl_handle_list = (temp_list[key]
                            for key in sorted(temp_list, key=SORT_KEY))

                    first = True
                    first_surname = True

                    for (surname, data_list) in ppl_handle_list:

                        if surname and not surname.isspace():
                            letter = first_letter(surname)
                            if order_by == self.ORDER_BY_NAME:
                                # There will only be an alphabetic index list if
                                # the ORDER_BY_NAME page is being generated
                                letter = get_index_letter(letter, index_list)
                        else:
                            letter = '&nbsp;'
                            surname = _ABSENT

                        trow = Html("tr")
                        tbody += trow

                        tcell = Html("td", class_="ColumnLetter", inline=True)
                        trow += tcell

                        if first or primary_difference(letter, prev_letter):
                            first = False
                            prev_letter = letter
                            trow.attr = 'class = "BeginLetter"'
                            ttle = _("Surnames beginning with letter %s") % letter
                            hyper = Html(
                                    "a", letter, name=letter,
                                    title=ttle,
                                    inline=True)
                            tcell += hyper
                        elif first_surname or surname != prev_surname:
                            first_surname = False
                            tcell += "&nbsp;"
                            prev_surname = surname

                        trow += Html("td",
                                     self.surname_link(name_to_md5(surname),
                                     html_escape(surname)),
                                     class_="ColumnSurname", inline=True)

                        trow += Html("td", len(data_list),
                                     class_="ColumnQuantity", inline=True)

        # create footer section
        # add clearline for proper styling
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(surnamelistpage,
                         output_file, sio, 0) # 0 => current date modification

    def surname_link(self, fname, name, opt_val=None, uplink=False):
        """
        Create a link to the surname page.

        @param: fname   -- Path to the file name
        @param: name    -- Name to see in the link
        @param: opt_val -- Option value to use
        @param: uplink  -- If True, then "../../../" is inserted in front of
                           the result.
        """
        url = self.report.build_url_fname_html(fname, "srn", uplink)
        hyper = Html("a", name, href=url, title=html_escape(name), inline=True)
        if opt_val is not None:
            hyper += opt_val

        # return hyperlink to its caller
        return hyper

class IntroductionPage(BasePage):
    """
    This class is responsible for displaying information
    about the introduction page.
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for
                          this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)
        ldatec = 0

        output_file, sio = self.report.create_file(report.intro_fname)
        intropage, head, body = self.write_header(_('Introduction'))

        # begin Introduction division
        with Html("div", class_="content", id="Introduction") as section:
            body += section

            introimg = self.add_image('introimg')
            if introimg is not None:
                section += introimg

            note_id = report.options['intronote']
            if note_id:
                note = self.dbase_.get_note_from_gramps_id(note_id)
                note_text = self.get_note_format(note, False)

                # attach note
                section += note_text

                # last modification of this note
                ldatec = note.get_change_time()

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(intropage, output_file, sio, ldatec)

class HomePage(BasePage):
    """
    This class is responsible for displaying information about the Home page.
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for
                          this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)
        ldatec = 0

        output_file, sio = self.report.create_file("index")
        homepage, head, body = self.write_header(_('Home'))

        # begin home division
        with Html("div", class_="content", id="Home") as section:
            body += section

            homeimg = self.add_image('homeimg')
            if homeimg is not None:
                section += homeimg

            note_id = report.options['homenote']
            if note_id:
                note = self.dbase_.get_note_from_gramps_id(note_id)
                note_text = self.get_note_format(note, False)

                # attach note
                section += note_text

                # last modification of this note
                ldatec = note.get_change_time()

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(homepage, output_file, sio, ldatec)

#################################################
#
#    Passes citations through to the Sources page
#
#################################################
class CitationPages(BasePage):
    """
    This class is responsible for displaying information about the 'Citation'
    database objects. It passes this information to the 'Sources' tab. It is
    told by the 'add_instances' call which 'Citation's to display.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")

    def display_pages(self, title):
        pass

#################################################
#
#    creates the Source List Page and Source Pages
#
#################################################
class SourcePages(BasePage):
    """
    This class is responsible for displaying information about the 'Source'
    database objects. It displays this information under the 'Sources'
    tab. It is told by the 'add_instances' call which 'Source's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")
        self.source_dict = defaultdict(set)
        self.navigation = None
        self.citationreferents = None

    def display_pages(self, title):
        """
        Generate and output the pages under the Sources tab, namely the sources
        index and the individual sources pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Source]")
        for item in self.report.obj_dict[Source].items():
            LOG.debug("    %s", str(item))
        with self.report.user.progress(_("Narrated Web Site Report"),
                                 _("Creating source pages"),
                                 len(self.report.obj_dict[Source]) + 1) as step:
            self.sourcelistpage(self.report, title,
                                self.report.obj_dict[Source].keys())

            for source_handle in self.report.obj_dict[Source]:
                step()
                self.sourcepage(self.report, title, source_handle)


    def sourcelistpage(self, report, title, source_handles):
        """
        Generate and output the Sources index page.

        @param: report         -- The instance of the main report class for
                                  this report
        @param: title          -- Is the title of the web page
        @param: source_handles -- A list of the handles of the sources to be
                                  displayed
        """
        BasePage.__init__(self, report, title)

        source_dict = {}

        output_file, sio = self.report.create_file("sources")
        sourcelistpage, head, body = self.write_header(_("Sources"))

        # begin source list division
        with Html("div", class_="content", id="Sources") as sourceslist:
            body += sourceslist

            # Sort the sources
            for handle in source_handles:
                source = self.dbase_.get_source_from_handle(handle)
                if source is not None:
                    key = source.get_title() + source.get_author()
                    key += str(source.get_gramps_id())
                    source_dict[key] = (source, handle)

            keys = sorted(source_dict, key=SORT_KEY)

            msg = _("This page contains an index of all the sources in the "
                    "database, sorted by their title. "
                    "Clicking on a source&#8217;s "
                    "title will take you to that source&#8217;s page.")
            sourceslist += Html("p", msg, id="description")

            # begin sourcelist table and table head
            with Html("table",
                      class_="infolist primobjlist sourcelist") as table:
                sourceslist += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                header_row = [
                    (_("Number"), "ColumnRowLabel"),
                    (_("Author"), "ColumnAuthor"),
                    (_("Source Name|Name"), "ColumnName")]

                trow.extend(
                    Html("th", label or "&nbsp;", class_=colclass, inline=True)
                    for (label, colclass) in header_row)

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for index, key in enumerate(keys):
                    source, source_handle = source_dict[key]

                    trow = Html("tr") + (
                        Html("td", index + 1, class_="ColumnRowLabel",
                             inline=True)
                    )
                    tbody += trow
                    trow.extend(
                        Html("td", source.get_author(), class_="ColumnAuthor",
                             inline=True)
                    )
                    trow.extend(
                        Html("td", self.source_link(source_handle,
                             source.get_title(),
                             source.get_gramps_id()), class_="ColumnName")
                    )

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(sourcelistpage, output_file, sio, 0)

    def sourcepage(self, report, title, source_handle):
        """
        Generate and output an individual Source page.

        @param: report        -- The instance of the main report class
                                 for this report
        @param: title         -- Is the title of the web page
        @param: source_handle -- The handle of the source to be output
        """
        source = report.database.get_source_from_handle(source_handle)
        BasePage.__init__(self, report, title, source.get_gramps_id())
        if not source:
            return

        self.page_title = source.get_title()

        inc_repositories = self.report.options["inc_repository"]
        self.navigation = self.report.options['navigation']
        self.citationreferents = self.report.options['citationreferents']

        output_file, sio = self.report.create_file(source_handle, "src")
        self.uplink = True
        sourcepage, head, body = self.write_header("%s - %s" % (_('Sources'),
                                                   self.page_title))

        ldatec = 0
        # begin source detail division
        with Html("div", class_="content", id="SourceDetail") as sourcedetail:
            body += sourcedetail

            media_list = source.get_media_list()
            if self.create_media and media_list:
                thumbnail = self.disp_first_img_as_thumbnail(media_list,
                                                                  source)
                if thumbnail is not None:
                    sourcedetail += thumbnail

            # add section title
            sourcedetail += Html("h3", html_escape(source.get_title()),
                                 inline=True)

            # begin sources table
            with Html("table", class_="infolist source") as table:
                sourcedetail += table

                tbody = Html("tbody")
                table += tbody

                source_gid = False
                if not self.noid and self.gid:
                    source_gid = source.get_gramps_id()

                    # last modification of this source
                    ldatec = source.get_change_time()

                for (label, value) in [
                    (_("Gramps ID"), source_gid),
                    (_("Author"), source.get_author()),
                    (_("Abbreviation"), source.get_abbreviation()),
                    (_("Publication information"),
                                        source.get_publication_info())]:
                    if value:
                        trow = Html("tr") + (
                            Html("td", label, class_="ColumnAttribute",
                                 inline=True),
                            Html("td", value, class_="ColumnValue", inline=True)
                        )
                        tbody += trow

            # Source notes
            notelist = self.display_note_list(source.get_note_list())
            if notelist is not None:
                sourcedetail += notelist

            # additional media from Source (if any?)
            if self.create_media and media_list:
                sourcemedia = self.disp_add_img_as_gallery(media_list, source)
                if sourcemedia is not None:
                    sourcedetail += sourcemedia

            # Source Data Map...
            src_data_map = self.write_srcattr(source.get_attribute_list())
            if src_data_map is not None:
                sourcedetail += src_data_map

            # Source Repository list
            if inc_repositories:
                repo_list = self.dump_repository_ref_list(
                                                     source.get_reporef_list())
                if repo_list is not None:
                    sourcedetail += repo_list

            # Source references list
            ref_list = self.display_bkref_list(Source, source_handle)
            if ref_list is not None:
                sourcedetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(sourcepage, output_file, sio, ldatec)

#################################################
#
#    creates the Media List Page and Media Pages
#
#################################################
class MediaPages(BasePage):
    """
    This class is responsible for displaying information about the 'Media'
    database objects. It displays this information under the 'Individuals'
    tab. It is told by the 'add_instances' call which 'Media's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for this report
        """
        BasePage.__init__(self, report, title="")
        self.media_dict = defaultdict(set)

    def display_pages(self, title):
        """
        Generate and output the pages under the Media tab, namely the media
        index and the individual media pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Media]")
        for item in self.report.obj_dict[Media].items():
            LOG.debug("    %s", str(item))
        with self.report.user.progress(_("Narrated Web Site Report"),
                                  _("Creating media pages"),
                                  len(self.report.obj_dict[Media]) + 1) as step:
            # bug 8950 : it seems it's better to sort on desc + gid.
            def sort_by_desc_and_gid(obj):
                """
                Sort by media description and gramps ID
                """
                return (obj.desc.lower(), obj.gramps_id)

            sorted_media_handles = sorted(self.report.obj_dict[Media].keys(),
                                          key=lambda x: sort_by_desc_and_gid(
                                 self.report.database.get_media_from_handle(x)))
            self.medialistpage(self.report, title, sorted_media_handles)

            prev = None
            total = len(sorted_media_handles)
            index = 1
            for handle in sorted_media_handles:
                gc.collect() # Reduce memory usage when there are many images.
                next_ = None if index == total else sorted_media_handles[index]
                step()
                self.mediapage(self.report, title,
                               handle, (prev, next_, index, total))
                prev = handle
                index += 1

    def medialistpage(self, report, title, sorted_media_handles):
        """
        Generate and output the Media index page.

        @param: report               -- The instance of the main report class
                                        for this report
        @param: title                -- Is the title of the web page
        @param: sorted_media_handles -- A list of the handles of the media to be
                                        displayed sorted by the media title
        """
        BasePage.__init__(self, report, title)

        output_file, sio = self.report.create_file("media")
        medialistpage, head, body = self.write_header(_('Media'))

        ldatec = 0
        # begin gallery division
        with Html("div", class_="content", id="Gallery") as medialist:
            body += medialist

            msg = _("This page contains an index of all the media objects "
                          "in the database, sorted by their title. Clicking on "
                          "the title will take you to that "
                          "media object&#8217;s page.  "
                          "If you see media size dimensions "
                          "above an image, click on the "
                          "image to see the full sized version.  ")
            medialist += Html("p", msg, id="description")

            # begin gallery table and table head
            with Html("table",
                      class_="infolist primobjlist gallerylist") as table:
                medialist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", trans, class_=colclass, inline=True)
                        for trans, colclass in [
                            ("&nbsp;", "ColumnRowLabel"),
                            (_("Media | Name"), "ColumnName"),
                            (_("Date"), "ColumnDate"),
                            (_("Mime Type"), "ColumnMime")
                        ]
                )

                # begin table body
                tbody = Html("tbody")
                table += tbody

                index = 1
                for media_handle in sorted_media_handles:
                    media = self.dbase_.get_media_from_handle(media_handle)
                    if media:
                        if media.get_change_time() > ldatec:
                            ldatec = media.get_change_time()
                        title = media.get_description() or "[untitled]"

                        trow = Html("tr")
                        tbody += trow

                        media_data_row = [
                            [index, "ColumnRowLabel"],
                            [self.media_ref_link(media_handle,
                                                 title), "ColumnName"],
                            [_dd.display(media.get_date_object()),
                                                         "ColumnDate"],
                            [media.get_mime_type(), "ColumnMime"]]

                        trow.extend(
                            Html("td", data, class_=colclass)
                                for data, colclass in media_data_row
                        )
                        index += 1

            def sort_by_desc_and_gid(obj):
                """
                Sort by media description and gramps ID
                """
                return (obj.desc, obj.gramps_id)

            unused_media_handles = []
            if self.create_unused_media:
                # add unused media
                media_list = self.dbase_.get_media_handles()
                for media_ref in media_list:
                    media_handle = media_ref.decode("utf-8")
                    if media_handle not in self.report.obj_dict[Media]:
                        unused_media_handles.append(media_handle)
                unused_media_handles = sorted(unused_media_handles,
                                          key=lambda x: sort_by_desc_and_gid(
                                 self.report.database.get_media_from_handle(x)))

            indx = 1
            prev = None
            total = len(unused_media_handles)
            if total > 0:
                trow += Html("tr")
                trow.extend(
                    Html("td", Html("h4", " "), inline=True) +
                    Html("td",
                         Html("h4",
                              _("Below unused media objects"), inline=True),
                         class_="") +
                    Html("td", Html("h4", " "), inline=True) +
                    Html("td", Html("h4", " "), inline=True)
                )
                for media_handle in unused_media_handles:
                    media = self.dbase_.get_media_from_handle(media_handle)
                    gc.collect() # Reduce memory usage when many images.
                    next_ = None if indx == total else \
                                                      unused_media_handles[indx]
                    trow += Html("tr")
                    media_data_row = [
                        [index, "ColumnRowLabel"],
                        [self.media_ref_link(media_handle,
                                        media.get_description()), "ColumnName"],
                        [_dd.display(media.get_date_object()), "ColumnDate"],
                        [media.get_mime_type(), "ColumnMime"]]
                    trow.extend(
                        Html("td", data, class_=colclass)
                            for data, colclass in media_data_row
                    )
                    self.mediapage(self.report, title,
                                   media_handle, (prev, next_, index, total))
                    prev = media_handle
                    index += 1
                    indx += 1

        # add footer section
        # add clearline for proper styling
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(medialistpage, output_file, sio, ldatec)

    def media_ref_link(self, handle, name, uplink=False):
        """
        Create a reference link to a media

        @param: handle -- The media handle
        @param: name   -- The name to use for the link
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        # get media url
        url = self.report.build_url_fname_html(handle, "img", uplink)

        # get name
        name = html_escape(name)

        # begin hyper link
        hyper = Html("a", name, href=url, title=name)

        # return hyperlink to its callers
        return hyper

    def mediapage(self, report, title, media_handle, info):
        """
        Generate and output an individual Media page.

        @param: report       -- The instance of the main report class
                                for this report
        @param: title        -- Is the title of the web page
        @param: media_handle -- The media handle to use
        @param: info         -- A tuple containing the media handle for the
                                next and previous media, the current page
                                number, and the total number of media pages
        """
        media = report.database.get_media_from_handle(media_handle)
        BasePage.__init__(self, report, title, media.gramps_id)
        (prev, next_, page_number, total_pages) = info

        ldatec = media.get_change_time()

        # get media rectangles
        _region_items = self.media_ref_rect_regions(media_handle)

        output_file, sio = self.report.create_file(media_handle, "img")
        self.uplink = True

        self.bibli = Bibliography()

        # get media type to be used primarily with "img" tags
        mime_type = media.get_mime_type()
        #mtype = get_description(mime_type)

        if mime_type:
            #note_only = False
            newpath = self.copy_source_file(media_handle, media)
            target_exists = newpath is not None
        else:
            #note_only = True
            target_exists = False

        copy_thumbnail(self.report, media_handle, media)
        self.page_title = media.get_description()
        (mediapage, head,
         body) = self.write_header("%s - %s" % (_("Media"),
                                   self.page_title))

        # if there are media rectangle regions, attach behaviour style sheet
        if _region_items:

            fname = "/".join(["css", "behaviour.css"])
            url = self.report.build_url_fname(fname, None, self.uplink)
            head += Html("link", href=url, type="text/css",
                         media="screen", rel="stylesheet")

        # begin MediaDetail division
        with Html("div", class_="content", id="GalleryDetail") as mediadetail:
            body += mediadetail

            # media navigation
            with Html("div", id="GalleryNav", role="navigation") as medianav:
                mediadetail += medianav
                if prev:
                    medianav += self.media_nav_link(prev, _("Previous"), True)
                data = _('%(strong1_start)s%(page_number)d%(strong_end)s of '
                         '%(strong2_start)s%(total_pages)d%(strong_end)s'
                        ) % {'strong1_start' :
                                 '<strong id="GalleryCurrent">',
                             'strong2_start' :
                                 '<strong id="GalleryTotal">',
                             'strong_end' : '</strong>',
                             'page_number' : page_number,
                             'total_pages' : total_pages}
                medianav += Html("span", data, id="GalleryPages")
                if next_:
                    medianav += self.media_nav_link(next_, _("Next"), True)

            # missing media error message
            errormsg = _("The file has been moved or deleted.")

            # begin summaryarea division
            with Html("div", id="summaryarea") as summaryarea:
                mediadetail += summaryarea
                if mime_type:
                    if mime_type.startswith("image"):
                        if not target_exists:
                            with Html("div", id="MediaDisplay") as mediadisplay:
                                summaryarea += mediadisplay
                                mediadisplay += Html("span", errormsg,
                                                     class_="MissingImage")

                        else:
                            # Check how big the image is relative to the
                            # requested 'initial' image size.
                            # If it's significantly bigger, scale it down to
                            # improve the site's responsiveness. We don't want
                            # the user to have to await a large download
                            # unnecessarily. Either way, set the display image
                            # size as requested.
                            orig_image_path = media_path_full(self.dbase_,
                                                              media.get_path())
                            #mtime = os.stat(orig_image_path).st_mtime
                            (width, height) = image_size(orig_image_path)
                            max_width = self.report.options[
                                                        'maxinitialimagewidth']
                            max_height = self.report.options[
                                                        'maxinitialimageheight']
                            if width != 0 and height != 0:
                                scale_w = (float(max_width)/width) or 1
                                           # the 'or 1' is so that a max of
                                           # zero is ignored
                                scale_h = (float(max_height)/height) or 1
                            else:
                                scale_w = 1.0
                                scale_h = 1.0
                            scale = min(scale_w, scale_h, 1.0)
                            new_width = int(width*scale)
                            new_height = int(height*scale)

                            # TODO. Convert disk path to URL.
                            url = self.report.build_url_fname(orig_image_path,
                                                              None, self.uplink)
                            with Html("div", id="GalleryDisplay",
                                      style='width: %dpx; height: %dpx' % (
                                            new_width,
                                            new_height)) as mediadisplay:
                                summaryarea += mediadisplay

                                # Feature #2634; display the mouse-selectable
                                # regions. See the large block at the top of
                                # this function where the various regions are
                                # stored in _region_items
                                if _region_items:
                                    ordered = Html("ol", class_="RegionBox")
                                    mediadisplay += ordered
                                    while len(_region_items) > 0:
                                        (name, coord_x, coord_y, width, height,
                                         linkurl) = _region_items.pop()
                                        ordered += Html("li",
                                                        style="left:%d%%; top:%d%%; width:%d%%; height:%d%%;"
                                            % (coord_x, coord_y,
                                               width, height)) + (
                                            Html("a", name, href=linkurl)
                                        )

                                # display the image
                                if orig_image_path != newpath:
                                    url = self.report.build_url_fname(newpath,
                                                None, self.uplink)
                                mediadisplay += Html("a", href=url) + (
                                    Html("img", width=new_width,
                                         height=new_height, src=url,
                                         alt=html_escape(self.page_title))
                                )
                    else:
                        dirname = tempfile.mkdtemp()
                        thmb_path = os.path.join(dirname, "document.png")
                        if run_thumbnailer(mime_type,
                                           media_path_full(self.dbase_,
                                                           media.get_path()),
                                           thmb_path, 320):
                            try:
                                path = self.report.build_path("preview",
                                                             media.get_handle())
                                npath = os.path.join(path, media.get_handle())
                                npath += ".png"
                                self.report.copy_file(thmb_path, npath)
                                path = npath
                                os.unlink(thmb_path)
                            except EnvironmentError:
                                path = os.path.join("images", "document.png")
                        else:
                            path = os.path.join("images", "document.png")
                        os.rmdir(dirname)

                        with Html("div", id="GalleryDisplay") as mediadisplay:
                            summaryarea += mediadisplay

                            img_url = self.report.build_url_fname(path,
                                                                  None,
                                                                  self.uplink)
                            if target_exists:
                                # TODO. Convert disk path to URL
                                url = self.report.build_url_fname(newpath,
                                                                  None,
                                                                  self.uplink)
                                hyper = Html("a", href=url,
                                             title=html_escape(
                                                           self.page_title)) + (
                                    Html("img", src=img_url,
                                         alt=html_escape(self.page_title))
                                    )
                                mediadisplay += hyper
                            else:
                                mediadisplay += Html("span", errormsg,
                                                     class_="MissingImage")
                else:
                    with Html("div", id="GalleryDisplay") as mediadisplay:
                        summaryarea += mediadisplay
                        url = self.report.build_url_image("document.png",
                                                          "images", self.uplink)
                        mediadisplay += Html("img", src=url,
                                             alt=html_escape(self.page_title),
                            title=html_escape(self.page_title))

                # media title
                title = Html("h3", html_escape(self.page_title.strip()),
                             inline=True)
                summaryarea += title

                # begin media table
                with Html("table", class_="infolist gallery") as table:
                    summaryarea += table

                    # Gramps ID
                    media_gid = media.gramps_id
                    if not self.noid and media_gid:
                        trow = Html("tr") + (
                            Html("td", GRAMPSID, class_="ColumnAttribute",
                                 inline=True),
                            Html("td", media_gid, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                    # mime type
                    if mime_type:
                        trow = Html("tr") + (
                            Html("td", _("File Type"), class_="ColumnAttribute",
                                 inline=True),
                            Html("td", mime_type, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                    # media date
                    date = media.get_date_object()
                    if date and date is not Date.EMPTY:
                        trow = Html("tr") + (
                            Html("td", DHEAD, class_="ColumnAttribute",
                                 inline=True),
                            Html("td", _dd.display(date), class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

            # get media notes
            notelist = self.display_note_list(media.get_note_list())
            if notelist is not None:
                mediadetail += notelist

            # get attribute list
            attrlist = media.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                mediadetail += attrsection

            # get media sources
            srclist = self.display_media_sources(media)
            if srclist is not None:
                mediadetail += srclist

            # get media references
            reflist = self.display_bkref_list(Media, media_handle)
            if reflist is not None:
                mediadetail += reflist

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(mediapage, output_file, sio, ldatec)

    def media_nav_link(self, handle, name, uplink=False):
        """
        Creates the Media Page Navigation hyperlinks for Next and Prev
        """
        url = self.report.build_url_fname_html(handle, "img", uplink)
        name = html_escape(name)
        return Html("a", name, name=name, id=name, href=url,
                    title=name, inline=True)

    def display_media_sources(self, photo):
        """
        Display media sources

        @param: photo  -- The source object (image, pdf, ...)
        """
        list(map(lambda i: self.bibli.add_reference(
                            self.report.database.get_citation_from_handle(i)),
            photo.get_citation_list()))
        sourcerefs = self.display_source_refs(self.bibli)

        # return source references to its caller
        return sourcerefs

    def copy_source_file(self, handle, photo):
        """
        Copy source file in the web tree.

        @param: handle -- Handle of the source
        @param: photo  -- The source object (image, pdf, ...)
        """
        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.report.build_path('images', handle)
        newpath = os.path.join(to_dir, handle) + ext

        fullpath = media_path_full(self.dbase_, photo.get_path())
        if not os.path.isfile(fullpath):
            _WRONGMEDIAPATH.append([photo.get_gramps_id(), fullpath])
            return None
        try:
            mtime = os.stat(fullpath).st_mtime
            if self.report.archive:
                self.report.archive.add(fullpath, str(newpath))
            else:
                to_dir = os.path.join(self.html_dir, to_dir)
                if not os.path.isdir(to_dir):
                    os.makedirs(to_dir)
                new_file = os.path.join(self.html_dir, newpath)
                shutil.copyfile(fullpath, new_file)
                os.utime(new_file, (mtime, mtime))
            return newpath
        except (IOError, OSError) as msg:
            error = _("Missing media object:") +                               \
                     "%s (%s)" % (photo.get_description(),
                                  photo.get_gramps_id())
            self.report.user.warn(error, str(msg))
            return None

class ThumbnailPreviewPage(BasePage):
    """
    This class is responsible for displaying information about
    the Thumbnails page.
    """
    def __init__(self, report, title, cb_progress):
        """
        @param: report      -- The instance of the main report class
                               for this report
        @param: title       -- Is the title of the web page
        @param: cb_progress -- The step used for the progress bar.
        """
        BasePage.__init__(self, report, title)
        self.create_thumbs_only = report.options['create_thumbs_only']
        # bug 8950 : it seems it's better to sort on desc + gid.
        def sort_by_desc_and_gid(obj):
            """
            Sort by media description and gramps ID
            """
            return (obj.desc, obj.gramps_id)

        self.photo_keys = sorted(self.report.obj_dict[Media],
                                 key=lambda x: sort_by_desc_and_gid(
                                          self.dbase_.get_media_from_handle(x)))

        if self.create_unused_media:
            # add unused media
            media_list = self.dbase_.get_media_handles()
            unused_media_handles = []
            for media_ref in media_list:
                media_handle = media_ref.decode("utf-8")
                if media_handle not in self.report.obj_dict[Media]:
                    self.photo_keys.append(media_handle)

        media_list = []
        for person_handle in self.photo_keys:
            photo = self.dbase_.get_media_from_handle(person_handle)
            if photo:
                if photo.get_mime_type().startswith("image"):
                    media_list.append((photo.get_description(), person_handle,
                                       photo))

                    if self.create_thumbs_only:
                        copy_thumbnail(self.report, person_handle, photo)

        media_list.sort(key=lambda x: SORT_KEY(x[0]))

        # Create thumbnail preview page...
        output_file, sio = self.report.create_file("thumbnails")
        thumbnailpage, head, body = self.write_header(_("Thumbnails"))

        with Html("div", class_="content", id="Preview") as previewpage:
            body += previewpage

            msg = _("This page displays a indexed list "
                    "of all the media objects "
                    "in this database.  It is sorted by media title.  "
                    "There is an index "
                    "of all the media objects in this database.  "
                    "Clicking on a thumbnail "
                    "will take you to that image&#8217;s page.")
            previewpage += Html("p", msg, id="description")

            with Html("table", class_="calendar") as table:
                previewpage += table

                thead = Html("thead")
                table += thead

                # page title...
                trow = Html("tr")
                thead += trow

                trow += Html("th", _("Thumbnail Preview"),
                             class_="monthName", colspan=7, inline=True)

                # table header cells...
                trow = Html("tr")
                thead += trow

                ltrs = ["&nbsp;", "&nbsp;", "&nbsp;",
                        "&nbsp;", "&nbsp;", "&nbsp;", "&nbsp;"]
                for ltr in ltrs:
                    trow += Html("th", ltr, class_="weekend", inline=True)

                tbody = Html("tbody")
                table += tbody

                index, indexpos = 1, 0
                num_of_images = len(media_list)
                num_of_rows = ((num_of_images // 7) + 1)
                num_of_cols = 7
                grid_row = 0
                while grid_row < num_of_rows:
                    trow = Html("tr", id="RowNumber: %08d" % grid_row)
                    tbody += trow

                    cols = 0
                    while cols < num_of_cols and indexpos < num_of_images:
                        ptitle = media_list[indexpos][0]
                        person_handle = media_list[indexpos][1]
                        photo = media_list[indexpos][2]

                        # begin table cell and attach to table row(trow)...
                        tcell = Html("td", class_="highlight weekend")
                        trow += tcell

                        # attach index number...
                        numberdiv = Html("div", class_="date")
                        tcell += numberdiv

                        # attach anchor name to date cell in upper right
                        # corner of grid...
                        numberdiv += Html("a", index, name=index, title=index,
                                          inline=True)

                        # begin unordered list and
                        # attach to table cell(tcell)...
                        unordered = Html("ul")
                        tcell += unordered

                        # create thumbnail
                        (real_path,
                         newpath) = self.report.prepare_copy_media(photo)
                        newpath = self.report.build_url_fname(newpath)

                        list_html = Html("li")
                        unordered += list_html

                        # attach thumbnail to list...
                        list_html += self.thumb_hyper_image(newpath, "img",
                                                       person_handle, ptitle)

                        index += 1
                        indexpos += 1
                        cols += 1
                    grid_row += 1

        # if last row is incomplete, finish it off?
        if grid_row == num_of_rows and cols < num_of_cols:
            for emptycols in range(cols,
                                   num_of_cols):
                trow += Html("td", class_="emptyDays", inline=True)

        # begin Thumbnail Reference section...
        with Html("div", class_="subsection", id="references") as section:
            body += section
            section += Html("h4", _("References"), inline=True)

            with Html("table", class_="infolist") as table:
                section += table

                tbody = Html("tbody")
                table += tbody

                index = 1
                for ptitle, person_handle, photo in media_list:
                    trow = Html("tr")
                    tbody += trow

                    tcell1 = Html("td",
                                  self.thumbnail_link(ptitle, index),
                                  class_="ColumnRowLabel")
                    tcell2 = Html("td", ptitle, class_="ColumnName")
                    trow += (tcell1, tcell2)

                    # increase index for row number...
                    index += 1

                    # increase progress meter...
                    cb_progress()

        # add body id element
        body.attr = 'id ="ThumbnailPreview"'

        # add footer section
        # add clearline for proper styling
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(thumbnailpage, output_file, sio, 0)


    def thumbnail_link(self, name, index):
        """
        creates a hyperlink for Thumbnail Preview Reference...
        """
        return Html("a", index, title=html_escape(name), href="#%d" % index)

    def thumb_hyper_image(self, thumbnail_url, subdir, fname, name):
        """
        eplaces media_link() because it doesn't work for this instance
        """
        name = html_escape(name)
        url = "/".join(self.report.build_subdirs(subdir,
                                                 fname) + [fname]) + self.ext

        with Html("div", class_="content", id="ThumbnailPreview") as section:
            with Html("div", class_="snapshot") as snapshot:
                section += snapshot

                with Html("div", class_="thumbnail") as thumbnail:
                    snapshot += thumbnail

                    if not self.create_thumbs_only:
                        thumbnail_link = Html("a", href=url, title=name) + (
                            Html("img", src=thumbnail_url, alt=name)
                        )
                    else:
                        thumbnail_link = Html("img", src=thumbnail_url,
                                              alt=name)
                    thumbnail += thumbnail_link
        return section

class DownloadPage(BasePage):
    """
    This class is responsible for displaying information about the Download page
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)

        # do NOT include a Download Page
        if not self.report.inc_download:
            return

        # menu options for class
        # download and description #1

        dlfname1 = self.report.dl_fname1
        dldescr1 = self.report.dl_descr1

        # download and description #2
        dlfname2 = self.report.dl_fname2
        dldescr2 = self.report.dl_descr2

        # if no filenames at all, return???
        if dlfname1 or dlfname2:

            output_file, sio = self.report.create_file("download")
            downloadpage, head, body = self.write_header(_('Download'))

            # begin download page and table
            with Html("div", class_="content", id="Download") as download:
                body += download

                msg = _("This page is for the user/ creator "
                        "of this Family Tree/ Narrative website "
                        "to share a couple of files with you "
                        "regarding their family.  If there are "
                        "any files listed "
                        "below, clicking on them will allow you "
                        "to download them. The "
                        "download page and files have the same "
                        "copyright as the remainder "
                        "of these web pages.")
                download += Html("p", msg, id="description")

                # begin download table and table head
                with Html("table", class_="infolist download") as table:
                    download += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_="Column" + colclass,
                             inline=True)
                        for (label, colclass) in [
                            (_("File Name"), "Filename"),
                            (DESCRHEAD, "Description"),
                            (_("Last Modified"), "Modified")]
                            )
                    # table body
                    tbody = Html("tbody")
                    table += tbody

                    # if dlfname1 is not None, show it???
                    if dlfname1:

                        trow = Html("tr", id='Row01')
                        tbody += trow

                        fname = os.path.basename(dlfname1)
                        # TODO dlfname1 is filename, convert disk path to URL
                        tcell = Html("td", class_="ColumnFilename") + (
                            Html("a", fname, href=dlfname1,
                                 title=html_escape(dldescr1))
                        )
                        trow += tcell

                        dldescr1 = dldescr1 or "&nbsp;"
                        trow += Html("td", dldescr1,
                                     class_="ColumnDescription", inline=True)

                        tcell = Html("td", class_="ColumnModified", inline=True)
                        trow += tcell
                        if os.path.exists(dlfname1):
                            modified = os.stat(dlfname1).st_mtime
                            last_mod = datetime.datetime.fromtimestamp(modified)
                            tcell += last_mod
                        else:
                            tcell += "&nbsp;"

                    # if download filename #2, show it???
                    if dlfname2:

                        # begin row #2
                        trow = Html("tr", id='Row02')
                        tbody += trow

                        fname = os.path.basename(dlfname2)
                        tcell = Html("td", class_="ColumnFilename") + (
                            Html("a", fname, href=dlfname2,
                                 title=html_escape(dldescr2))
                        )
                        trow += tcell

                        dldescr2 = dldescr2 or "&nbsp;"
                        trow += Html("td", dldescr2,
                                     class_="ColumnDescription", inline=True)

                        tcell = Html("td", id='Col04',
                                     class_="ColumnModified", inline=True)
                        trow += tcell
                        if os.path.exists(dlfname2):
                            modified = os.stat(dlfname2).st_mtime
                            last_mod = datetime.datetime.fromtimestamp(modified)
                            tcell += last_mod
                        else:
                            tcell += "&nbsp;"

            # clear line for proper styling
            # create footer section
            footer = self.write_footer(None)
            body += (FULLCLEAR, footer)

            # send page out for processing
            # and close the file
            self.xhtml_writer(downloadpage, output_file, sio, 0)

class ContactPage(BasePage):
    """
    This class is responsible for displaying information about the 'Researcher'
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)

        output_file, sio = self.report.create_file("contact")
        contactpage, head, body = self.write_header(_('Contact'))

        # begin contact division
        with Html("div", class_="content", id="Contact") as section:
            body += section

            # begin summaryarea division
            with Html("div", id='summaryarea') as summaryarea:
                section += summaryarea

                contactimg = self.add_image('contactimg', 200)
                if contactimg is not None:
                    summaryarea += contactimg

                # get researcher information
                res = get_researcher()

                with Html("div", id='researcher') as researcher:
                    summaryarea += researcher

                    if res.name:
                        res.name = res.name.replace(',,,', '')
                        researcher += Html("h3", res.name, inline=True)
                    if res.addr:
                        researcher += Html("span", res.addr,
                                           id='streetaddress', inline=True)
                    if res.locality:
                        researcher += Html("span", res.locality,
                                           id="locality", inline=True)
                    text = "".join([res.city, res.state, res.postal])
                    if text:
                        city = Html("span", res.city, id='city', inline=True)
                        state = Html("span", res.state, id='state', inline=True)
                        postal = Html("span", res.postal, id='postalcode',
                                      inline=True)
                        researcher += (city, state, postal)
                    if res.country:
                        researcher += Html("span", res.country,
                                           id='country', inline=True)
                    if res.email:
                        researcher += Html("span", id='email') + (
                            Html("a", res.email,
                                 href='mailto:%s' % res.email, inline=True)
                        )

                    # add clear line for proper styling
                    summaryarea += FULLCLEAR

                    note_id = report.options['contactnote']
                    if note_id:
                        note = self.dbase_.get_note_from_gramps_id(note_id)
                        note_text = self.get_note_format(note, False)

                        # attach note
                        summaryarea += note_text

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for porcessing
        # and close the file
        self.xhtml_writer(contactpage, output_file, sio, 0)

#################################################
#
#    creates the Individual List Page and IndividualPages
#
#################################################
class PersonPages(BasePage):
    """
    This class is responsible for displaying information about the 'Person'
    database objects. It displays this information under the 'Individuals'
    tab. It is told by the 'add_instances' call which 'Person's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for this report
        """
        BasePage.__init__(self, report, title="")
        self.ind_dict = defaultdict(set)
        self.mapservice = None
        self.sort_name = None
        self.googleopts = None
        self.birthorder = None
        self.person = None
        self.familymappages = None
        self.rel_class = None
        self.placemappages = None
        self.name = None

    def display_pages(self, title):
        """
        Generate and output the pages under the Individuals tab, namely the
        individual index and the individual pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Person]")
        for item in self.report.obj_dict[Person].items():
            LOG.debug("    %s", str(item))
        with self.report.user.progress(_("Narrated Web Site Report"),
                                       _('Creating individual pages'),
                              len(self.report.obj_dict[Person]) + 1) as step:
            self.individuallistpage(self.report, title,
                                    self.report.obj_dict[Person].keys())
            for person_handle in sorted(self.report.obj_dict[Person]):
                step()
                person = self.report.database.get_person_from_handle(
                                                                  person_handle)
                self.individualpage(self.report, title, person)

#################################################
#
#    creates the Individual List Page
#
#################################################
    def individuallistpage(self, report, title, ppl_handle_list):
        """
        Creates an individual page

        @param: report          -- The instance of the main report class
                                   for this report
        @param: title           -- Is the title of the web page
        @param: ppl_handle_list -- The list of people for whom we need
                                   to create a page.
        """
        BasePage.__init__(self, report, title)
        prev_letter = " "

        # plugin variables for this module
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        output_file, sio = self.report.create_file("individuals")
        indlistpage, head, body = self.write_header(_("Individuals"))
        date = 0

        # begin Individuals division
        with Html("div", class_="content", id="Individuals") as individuallist:
            body += individuallist

            # Individual List page message
            msg = _("This page contains an index of all the individuals in "
                          "the database, sorted by their last names. "
                          "Selecting the person&#8217;s "
                          "name will take you to that "
                          "person&#8217;s individual page.")
            individuallist += Html("p", msg, id="description")

            # add alphabet navigation
            index_list = get_first_letters(self.dbase_, ppl_handle_list,
                                           _KEYPERSON)
            alpha_nav = alphabet_navigation(index_list)
            if alpha_nav is not None:
                individuallist += alpha_nav

            # begin table and table head
            with Html("table",
                       class_="infolist primobjlist IndividualList") as table:
                individuallist += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # show surname and first name
                trow += Html("th", _("Surname"), class_="ColumnSurname",
                             inline=True)
                trow += Html("th", _("Given Name"), class_="ColumnName",
                             inline=True)

                if showbirth:
                    trow += Html("th", _("Birth"), class_="ColumnDate",
                                 inline=True)

                if showdeath:
                    trow += Html("th", _("Death"), class_="ColumnDate",
                                 inline=True)

                if showpartner:
                    trow += Html("th", _("Partner"), class_="ColumnPartner",
                                 inline=True)

                if showparents:
                    trow += Html("th", _("Parents"), class_="ColumnParents",
                                 inline=True)

            tbody = Html("tbody")
            table += tbody

            ppl_handle_list = sort_people(self.dbase_, ppl_handle_list)
            first = True
            for (surname, handle_list) in ppl_handle_list:

                if surname and not surname.isspace():
                    letter = get_index_letter(first_letter(surname), index_list)
                else:
                    letter = '&nbsp'
                    surname = _ABSENT

                first_surname = True
                for person_handle in sorted(handle_list,
                       key=lambda x: sort_on_name_and_grampsid(x, self.dbase_)):
                    person = self.dbase_.get_person_from_handle(person_handle)
                    if person.get_change_time() > date:
                        date = person.get_change_time()

                    # surname column
                    trow = Html("tr")
                    tbody += trow
                    tcell = Html("td", class_="ColumnSurname", inline=True)
                    trow += tcell

                    if first or primary_difference(letter, prev_letter):
                        first = False
                        first_surname = False
                        prev_letter = letter
                        trow.attr = 'class = "BeginSurname"'
                        tcell += Html(
                            "a", html_escape(surname), name=letter,
                            id_=letter,
                            title=_("Surnames %(surname)s beginning "
                                    "with letter %(letter)s") %
                                         {'surname' : surname,
                                          'letter' : letter})
                    elif first_surname:
                        first_surname = False
                        tcell += Html("a", html_escape(surname),
                                      title="Surnames " + surname)
                    else:
                        tcell += "&nbsp;"

                    # firstname column
                    link = self.new_person_link(person_handle, person=person,
                                                 name_style=_NAME_STYLE_FIRST)
                    trow += Html("td", link, class_="ColumnName")

                    # birth column
                    if showbirth:
                        tcell = Html("td", class_="ColumnBirth", inline=True)
                        trow += tcell

                        birth_date = _find_birth_date(self.dbase_, person)
                        if birth_date is not None:
                            if birth_date.fallback:
                                tcell += Html('em', _dd.display(birth_date),
                                              inline=True)
                            else:
                                tcell += _dd.display(birth_date)
                        else:
                            tcell += "&nbsp;"

                    # death column
                    if showdeath:
                        tcell = Html("td", class_="ColumnDeath", inline=True)
                        trow += tcell

                        death_date = _find_death_date(self.dbase_, person)
                        if death_date is not None:
                            if death_date.fallback:
                                tcell += Html('em', _dd.display(death_date),
                                              inline=True)
                            else:
                                tcell += _dd.display(death_date)
                        else:
                            tcell += "&nbsp;"

                    # partner column
                    if showpartner:

                        family_list = person.get_family_handle_list()
                        first_family = True
                        #partner_name = None
                        tcell = ()
                        if family_list:
                            for family_handle in family_list:
                                family = self.dbase_.get_family_from_handle(
                                                                  family_handle)
                                partner_handle = ReportUtils.find_spouse(person,
                                                                         family)
                                if partner_handle:
                                    if not first_family:
                                        # have to do this to get the comma on
                                        # the same line as the link
                                        if isinstance(tcell[-1], Html):
                                            # tcell is an instance of Html (or
                                            # of a subclass thereof)
                                            tcell[-1].inside += ","
                                        else:
                                            tcell = tcell[:-1] +\
                                                ((tcell[-1] + ", "),)
                                    # Have to manipulate as tuples so that
                                    # subsequent people are not nested
                                    # within the first link
                                    tcell += (self.new_person_link(
                                                               partner_handle),)
                                    first_family = False
                        else:
                            tcell = "&nbsp;"
                        trow += Html("td", class_="ColumnPartner") + tcell

                    # parents column
                    if showparents:

                        parent_handle_list = person.get_parent_family_handle_list()
                        if parent_handle_list:
                            parent_handle = parent_handle_list[0]
                            family = self.dbase_.get_family_from_handle(
                                                                  parent_handle)
                            father_handle = family.get_father_handle()
                            mother_handle = family.get_mother_handle()
                            if father_handle:
                                father = self.dbase_.get_person_from_handle(
                                                                  father_handle)
                            else:
                                father = None
                            if mother_handle:
                                mother = self.dbase_.get_person_from_handle(
                                                                  mother_handle)
                            else:
                                mother = None
                            if father:
                                father_name = self.get_name(father)
                            if mother:
                                mother_name = self.get_name(mother)
                            samerow = False
                            if mother and father:
                                tcell = (Html("span", father_name,
                                              class_="father fatherNmother",
                                              inline=True),
                                         Html("span", mother_name,
                                              class_="mother", inline=True))
                            elif mother:
                                tcell = Html("span", mother_name,
                                             class_="mother", inline=True)
                            elif father:
                                tcell = Html("span", father_name,
                                             class_="father", inline=True)
                            else:
                                tcell = "&nbsp;"
                                samerow = True
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", class_="ColumnParents",
                                     inline=samerow) + tcell

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(date)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(indlistpage, output_file, sio, date)

#################################################
#
#    creates an Individual Page
#
#################################################
    gender_map = {
        Person.MALE    : _('male'),
        Person.FEMALE  : _('female'),
        Person.UNKNOWN : _('unknown'),
        }

    def individualpage(self, report, title, person):
        """
        Creates an individual page

        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        @param: person -- The person to use for this page.
        """
        BasePage.__init__(self, report, title, person.get_gramps_id())
        place_lat_long = []

        self.person = person
        self.bibli = Bibliography()
        self.sort_name = self.get_name(person)
        self.name = self.get_name(person)

        date = self.person.get_change_time()

        # to be used in the Family Map Pages...
        self.familymappages = self.report.options['familymappages']
        self.placemappages = self.report.options['placemappages']
        self.mapservice = self.report.options['mapservice']
        self.googleopts = self.report.options['googleopts']

        # decide if we will sort the birth order of siblings...
        self.birthorder = self.report.options['birthorder']

        # get the Relationship Calculator so that we can determine
        # bio, half, step- siblings for use in display_ind_parents() ...
        self.rel_class = self.report.rel_class

        output_file, sio = self.report.create_file(person.get_handle(), "ppl")
        self.uplink = True
        indivdetpage, head, body = self.write_header(self.sort_name)

        # attach the ancestortree style sheet if ancestor
        # graph is being created?
        if self.report.options["ancestortree"]:
            if self.usecms:
                fname = "".join([self.target_uri, "css", "ancestortree.css"])
            else:
                fname = "/".join(["css", "ancestortree.css"])
            url = self.report.build_url_fname(fname, None, self.uplink)
            head += Html("link", href=url, type="text/css", media="screen",
                         rel="stylesheet")

        # begin individualdetail division
        with Html("div", class_="content",
                  id='IndividualDetail') as individualdetail:
            body += individualdetail

            # display a person's general data
            thumbnail, name, summary = self.display_ind_general()
            if thumbnail is not None:
                individualdetail += thumbnail
            individualdetail += (name, summary)

            # display a person's events
            sect2 = self.display_ind_events(place_lat_long)
            if sect2 is not None:
                individualdetail += sect2

            # display relationship to the center person
            sect3 = self.display_ind_center_person()
            if sect3 is not None:
                individualdetail += sect3

            # display parents
            sect4 = self.display_ind_parents()
            if sect4 is not None:
                individualdetail += sect4

            # display relationships
            relationships = self.display_relationships(self.person,
                                                       place_lat_long)
            if relationships is not None:
                individualdetail += relationships

            # display LDS ordinance
            sect5 = self.display_lds_ordinance(self.person)
            if sect5 is not None:
                individualdetail += sect5

            # display address(es) and show sources
            sect6 = self.display_addr_list(self.person.get_address_list(), True)
            if sect6 is not None:
                individualdetail += sect6

            photo_list = self.person.get_media_list()
            media_list = photo_list[:]

            # if Family Pages are not being created, then include the Family
            # Media objects? There is no reason to add these objects to the
            # Individual Pages...
            if not self.inc_families:
                for handle in self.person.get_family_handle_list():
                    family = self.dbase_.get_family_from_handle(handle)
                    if family:
                        media_list += family.get_media_list()
                        for evt_ref in family.get_event_ref_list():
                            event = self.dbase_.get_event_from_handle(
                                                                    evt_ref.ref)
                            media_list += event.get_media_list()

            # if the Event Pages are not being createsd, then include the Event
            # Media objects? There is no reason to add these objects to the
            # Individual Pages...
            if not self.inc_events:
                for evt_ref in self.person.get_primary_event_ref_list():
                    event = self.dbase_.get_event_from_handle(evt_ref.ref)
                    if event:
                        media_list += event.get_media_list()

            # display additional images as gallery
            sect7 = self.disp_add_img_as_gallery(media_list, person)
            if sect7 is not None:
                individualdetail += sect7

            # display Narrative Notes
            notelist = person.get_note_list()
            sect8 = self.display_note_list(notelist)
            if sect8 is not None:
                individualdetail += sect8

            # display attributes
            attrlist = person.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                individualdetail += attrsection

            # display web links
            sect10 = self.display_url_list(self.person.get_url_list())
            if sect10 is not None:
                individualdetail += sect10

            # display associations
            assocs = person.get_person_ref_list()
            if assocs:
                individualdetail += self.display_ind_associations(assocs)

            # for use in family map pages...
            if len(place_lat_long) > 0:
                if self.report.options["familymappages"]:
                    # save output_file, string_io and cur_fname
                    # before creating a new page
                    sof = output_file
                    sstring_io = sio
                    sfname = self.report.cur_fname
                    individualdetail += self.__display_family_map(person,
                                                                 place_lat_long)
                    # restore output_file, string_io and cur_fname
                    # after creating a new page
                    output_file = sof
                    sio = sstring_io
                    self.report.cur_fname = sfname

            # display pedigree
            sect13 = self.display_ind_pedigree()
            if sect13 is not None:
                individualdetail += sect13

            # display ancestor tree
            if report.options['ancestortree']:
                sect14 = self.display_tree()
                if sect14 is not None:
                    individualdetail += sect14

            # display source references
            sect14 = self.display_ind_sources(person)
            if sect14 is not None:
                individualdetail += sect14

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer(date)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(indivdetpage, output_file, sio, date)

    def __create_family_map(self, person, place_lat_long):
        """
        creates individual family map page

        @param: person -- person from database
        @param: place_lat_long -- for use in Family Map Pages
        """
        if not place_lat_long:
            return

        output_file, sio = self.report.create_file(person.get_handle(), "maps")
        self.uplink = True
        familymappage, head, body = self.write_header(_("Family Map"))

        minx, maxx = Decimal("0.00000001"), Decimal("0.00000001")
        miny, maxy = Decimal("0.00000001"), Decimal("0.00000001")
        xwidth, yheight = [], []
        midx_, midy_, spanx, spany = [None]*4

        number_markers = len(place_lat_long)
        if number_markers > 1:
            for (latitude, longitude, placetitle, handle,
                 date, etype) in place_lat_long:
                xwidth.append(latitude)
                yheight.append(longitude)
            xwidth.sort()
            yheight.sort()

            minx = xwidth[0] if xwidth[0] else minx
            maxx = xwidth[-1] if xwidth[-1] else maxx
            minx, maxx = Decimal(minx), Decimal(maxx)
            midx_ = str(Decimal((minx + maxx) /2))

            miny = yheight[0] if yheight[0] else miny
            maxy = yheight[-1] if yheight[-1] else maxy
            miny, maxy = Decimal(miny), Decimal(maxy)
            midy_ = str(Decimal((miny + maxy) /2))

            midx_, midy_ = conv_lat_lon(midx_, midy_, "D.D8")

            # get the integer span of latitude and longitude
            spanx = int(maxx - minx)
            spany = int(maxy - miny)

        # set zoom level based on span of Longitude?
        tinyset = [value for value in (-3, -2, -1, 0, 1, 2, 3)]
        smallset = [value for value in (-4, -5, -6, -7, 4, 5, 6, 7)]
        middleset = [value for value in (-8, -9, -10, -11, 8, 9, 10, 11)]
        largeset = [value for value in (-11, -12, -13, -14, -15, -16,
                                        -17, 11, 12, 13, 14, 15, 16, 17)]

        if spany in tinyset or spany in smallset:
            zoomlevel = 6
        elif spany in middleset:
            zoomlevel = 5
        elif spany in largeset:
            zoomlevel = 4
        else:
            zoomlevel = 3

        # 0 = latitude, 1 = longitude, 2 = place title,
        # 3 = handle, and 4 = date, 5 = event type...
        # being sorted by date, latitude, and longitude...
        place_lat_long = sorted(place_lat_long, key=itemgetter(4, 0, 1))

        # for all plugins
        # if family_detail_page
        # if active
        # call_(report, up, head)

        # add narrative-maps style sheet
        if self.usecms:
            fname = "".join([self.target_uri, "css", "narrative-maps.css"])
        else:
            fname = "/".join(["css", "narrative-maps.css"])
        url = self.report.build_url_fname(fname, None, self.uplink)
        head += Html("link", href=url, type="text/css", media="screen",
                     rel="stylesheet")

        # add MapService specific javascript code
        if self.mapservice == "Google":
            src_js = "http://maps.googleapis.com/maps/api/js?sensor=false"
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)
        else:
            src_js = "http://www.openlayers.org/api/OpenLayers.js"
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)

        if number_markers > 1:
            tracelife = "["
            seq_ = 1

            for index in range(0, (number_markers - 1)):
                (latitude, longitude, placetitle, handle, date,
                 etype) = place_lat_long[index]

                # are we using Google?
                if self.mapservice == "Google":

                    # are we creating Family Links?
                    if self.googleopts == "FamilyLinks":
                        tracelife += """
    new google.maps.LatLng(%s, %s),""" % (latitude, longitude)

                    # are we creating Drop Markers or Markers?
                    elif self.googleopts in ["Drop", "Markers"]:
                        tracelife += """
    ['%s', %s, %s, %d],""" % (placetitle.replace("'", "\\'"), latitude,
                              longitude, seq_)

                # are we using OpenStreetMap?
                else:
                    tracelife += """
    [%s, %s],""" % (longitude, latitude)
                seq_ += 1
            # FIXME: The last element in the place_lat_long list is treated
            # specially, and the code above is apparently repeated so as to
            # avoid a comma at the end, and get the right closing. This is very
            # ugly.
            (latitude, longitude, placetitle, handle, date,
             etype) = place_lat_long[-1]

            # are we using Google?
            if self.mapservice == "Google":

                # are we creating Family Links?
                if self.googleopts == "FamilyLinks":
                    tracelife += """
    new google.maps.LatLng(%s, %s)
  ];""" % (latitude, longitude)

                # are we creating Drop Markers or Markers?
                elif self.googleopts in ["Drop", "Markers"]:
                    tracelife += """
    ['%s', %s, %s, %d]
  ];""" % (placetitle.replace("'", "\\'"), latitude, longitude, seq_)

            # are we using OpenStreetMap?
            elif self.mapservice == "OpenStreetMap":
                tracelife += """
    [%s, %s]
  ];""" % (longitude, latitude)

        # begin MapDetail division...
        with Html("div", class_="content", id="FamilyMapDetail") as mapdetail:
            body += mapdetail

            # add page title
            mapdetail += Html("h3", html_escape(_("Tracking %s") %
                                  self.get_name(person)), inline=True)

            # page description
            msg = _("This map page represents that person "
                    "and any descendants with "
                    "all of their event/ places. If you place your mouse over "
                    "the marker it will display the place name. "
                    "The markers and the Reference "
                    "list are sorted in date order (if any?). "
                    "Clicking on a place&#8217;s "
                    "name in the Reference section will take you "
                    "to that place&#8217;s page.")
            mapdetail += Html("p", msg, id="description")

            # this is the style element where the Map is held in the CSS...
            with Html("div", id="map_canvas") as canvas:
                mapdetail += canvas

                # begin javascript inline code...
                with Html("script", deter="deter",
                          style='width =100%; height =100%;',
                          type="text/javascript", indent=False) as jsc:
                    head += jsc

                    # if there is only one marker?
                    if number_markers == 1:
                        (latitude, longitude,
                         placetitle, handle, date, etype) = place_lat_long[0]

                        # are we using Google?
                        if self.mapservice == "Google":
                            # FIXME: Horrible hack, because when there is only a
                            # single marker, the javascript for place is used,
                            # which has a 'place_canvas' division, instead of a
                            # 'map_canvas' division.
                            jsc += GOOGLE_JSC.replace("place_canvas",
                                                      "map_canvas") % \
                                    (latitude, longitude,
                                                 placetitle.replace("'", "\\'"))

                        # we are using OpenStreetMap?
                        else:
                            # FIXME: Horrible hack, because when there is only a
                            # single marker, the javascript for place is used,
                            # which has a 'place_canvas' division, instead of a
                            # 'map_canvas' division.
                            jsc += OPENSTREETMAP_JSC.replace("place_canvas",
                                                             "map_canvas") % \
                                    (xml_lang()[3:5].lower(),
                                     longitude, latitude)

                    # there is more than one marker...
                    else:

                        # are we using Google?
                        if self.mapservice == "Google":

                            # are we creating Family Links?
                            if self.googleopts == "FamilyLinks":
                                jsc += FAMILYLINKS % (tracelife, midx_, midy_,
                                                      zoomlevel)

                            # are we creating Drop Markers?
                            elif self.googleopts == "Drop":
                                jsc += DROPMASTERS  % (tracelife, zoomlevel)

                            # we are creating Markers only...
                            else:
                                jsc += MARKERS % (tracelife, zoomlevel)

                        # we are using OpenStreetMap...
                        else:
                            jsc += OSM_MARKERS % (xml_lang()[3:5].lower(),
                                                  tracelife, midy_, midx_,
                                                  zoomlevel)

            # if Google and Drop Markers are selected,
            # then add "Drop Markers" button?
            if self.mapservice == "Google" and self.googleopts == "Drop":
                mapdetail += Html("button", _("Drop Markers"),
                                  id="drop", onclick="drop()", inline=True)

            # begin place reference section and its table...
            with Html("div", class_="subsection", id="references") as section:
                mapdetail += section
                section += Html("h4", _("References"), inline=True)

                with Html("table", class_="infolist") as table:
                    section += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                            for (label, colclass) in [
                                (_("Date"), "ColumnDate"),
                                (_("Place Title"), "ColumnPlace"),
                                (_("Event Type"), "ColumnType")
                            ]
                    )

                    tbody = Html("tbody")
                    table += tbody

                    for (latitude, longitude, placetitle, handle, date,
                         etype) in place_lat_long:
                        trow = Html("tr")
                        tbody += trow

                        trow.extend(
                            Html("td", data, class_=colclass, inline=True)
                                for data, colclass in [
                                    (date, "ColumnDate"),
                                    (self.place_link(handle,
                                                     placetitle,
                                                     uplink=True),
                                                         "ColumnPlace"),
                                    (str(etype), "ColumnType")
                                ]
                        )

        # add body id for this page...
        body.attr = 'id ="FamilyMap" onload ="initialize()"'

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familymappage, output_file, sio, 0)

    def __display_family_map(self, person, place_lat_long):
        """
        Create the family map link

        @param: person         -- The person to set in the box
        @param: place_lat_long -- The center of the box
        """
        # create family map page
        self.__create_family_map(person, place_lat_long)

        # begin family map division plus section title
        with Html("div", class_="subsection", id="familymap") as familymap:
            familymap += Html("h4", _("Family Map"), inline=True)

            # add family map link
            person_handle = person.get_handle()
            url = self.report.build_url_fname_html(person_handle, "maps", True)
            familymap += self.family_map_link(person_handle, url)

        # return family map link to its caller
        return familymap

    def draw_box(self, center, col, person):
        """
        Draw the box around the AncestorTree Individual name box...

        @param: center -- The center of the box
        @param: col    -- The generation number
        @param: person -- The person to set in the box
        """
        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)
        sex = person.gender
        if sex == Person.MALE:
            divclass = "male"
        elif sex == Person.FEMALE:
            divclass = "female"
        else:
            divclass = "unknown"

        boxbg = Html("div", class_="boxbg %s AncCol%s" % (divclass, col),
                    style="top: %dpx; left: %dpx;" % (top, xoff+1)
                   )

        person_name = self.get_name(person)
        # This does not use [new_]person_link because the requirements are
        # unique
        result = self.report.obj_dict.get(Person).get(person.handle)
        if result is None or result[0] == "":
            # The person is not included in the webreport or there is no link
            # to them
            boxbg += Html("span", person_name, class_="unlinked", inline=True)
        else:
            thumbnail_url = None
            if self.create_media and col < 5:
                photolist = person.get_media_list()
                if photolist:
                    photo_handle = photolist[0].get_reference_handle()
                    photo = self.dbase_.get_media_from_handle(photo_handle)
                    mime_type = photo.get_mime_type()
                    if mime_type:
                        region = self.media_ref_region_to_object(photo_handle,
                                                                 person)
                        if region:
                            # make a thumbnail of this region
                            newpath = copy_thumbnail(self.report, photo_handle,
                                                     photo, region)
                            # TODO. Check if build_url_fname can be used.
                            newpath = "/".join(['..']*3 + [newpath])
                            if win():
                                newpath = newpath.replace('\\', "/")
                            thumbnail_url = newpath
                        else:
                            (photo_url,
                             thumbnail_url) = self.report.prepare_copy_media(
                                        photo)
                            thumbnail_url = "/".join(['..']*3 + [thumbnail_url])
                            if win():
                                thumbnail_url = thumbnail_url.replace('\\', "/")
            url = self.report.build_url_fname_html(person.handle, "ppl", True)
            if thumbnail_url is None:
                boxbg += Html("a", href=url, class_="noThumb") + person_name
            else:
                thumb = Html("span", class_="thumbnail") + \
                    (Html("img", src=thumbnail_url, alt="Image: "
                          + person_name))
                boxbg += Html("a", href=url) + thumb + person_name
        shadow = Html("div", class_="shadow", inline=True,
                      style="top: %dpx; left: %dpx;"
                                             % (top + _SHADOW, xoff + _SHADOW))

        return [boxbg, shadow]

    def extend_line(self, coord_y0, coord_x0):
        """
        Draw and extended line

        @param: coord_y0 -- The starting point
        @param: coord_x0 -- The end of the line
        """
        style = "top: %dpx; left: %dpx; width: %dpx"
        ext_bv = Html("div", class_="bvline", inline=True,
                      style=style % (coord_y0, coord_x0, _HGAP/2)
                    )
        ext_gv = Html("div", class_="gvline", inline=True,
                      style=style % (coord_y0+_SHADOW,
                                     coord_x0, _HGAP/2+_SHADOW)
                    )
        return [ext_bv, ext_gv]

    def connect_line(self, coord_y0, coord_y1, col):
        """
        We need to draw a line between to points

        @param: coord_y0 -- The starting point
        @param: coord_y1 -- The end of the line
        @param: col      -- The generation number
        """
        coord_y = min(coord_y0, coord_y1)
        stylew = "top: %dpx; left: %dpx; width: %dpx;"
        styleh = "top: %dpx; left: %dpx; height: %dpx;"
        coord_x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        cnct_bv = Html("div", class_="bvline", inline=True,
                       style=stylew % (coord_y1, coord_x0, _HGAP/2))
        cnct_gv = Html("div", class_="gvline", inline=True, style=stylew %
            (coord_y1+_SHADOW, coord_x0+_SHADOW, _HGAP/2+_SHADOW))
        cnct_bh = Html("div", class_="bhline", inline=True,
                       style=styleh % (coord_y, coord_x0,
                                       abs(coord_y0-coord_y1)))
        cnct_gh = Html("div", class_="gvline", inline=True, style=styleh %
                 (coord_y+_SHADOW, coord_x0+_SHADOW, abs(coord_y0-coord_y1)))
        return [cnct_bv, cnct_gv, cnct_bh, cnct_gh]

    def draw_connected_box(self, center1, center2, col, handle):
        """
        Draws the connected box for Ancestor Tree on the Individual Page

        @param: center1 -- The first box to connect
        @param: center2 -- The destination box to draw
        @param: col     -- The generation number
        @param: handle  -- The handle of the person to set in the new box
        """
        box = []
        if not handle:
            return box
        person = self.dbase_.get_person_from_handle(handle)
        box = self.draw_box(center2, col, person)
        box += self.connect_line(center1, center2, col)
        return box

    def display_tree(self):
        """
        Display the Ancestor Tree
        """
        tree = []
        if not self.person.get_main_parents_family_handle():
            return None

        generations = self.report.options['graphgens']
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        with Html("div", id="tree", class_="subsection") as tree:
            tree += Html("h4", _('Ancestors'), inline=True)
            with Html("div", id="treeContainer",
                    style="width:%dpx; height:%dpx;" %
                        (_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP,
                        max_size)
                     ) as container:
                tree += container
                container += self.draw_tree(1, generations, max_size,
                                            0, center, self.person.handle)
        return tree

    def draw_tree(self, gen_nr, maxgen, max_size, old_center,
                  new_center, person_handle):
        """
        Draws the Ancestor Tree

        @param: gen_nr        -- The generation number to draw
        @param: maxgen        -- The maximum number of generations to draw
        @param: max_size      -- The maximum size of the drawing area
        @param: old_center    -- The position of the old box
        @param: new_center    -- The position of the new box
        @param: person_handle -- The handle of the person to draw
        """
        tree = []
        if gen_nr > maxgen:
            return tree
        gen_offset = int(max_size / pow(2, gen_nr+1))
        if person_handle:
            person = self.dbase_.get_person_from_handle(person_handle)
        else:
            person = None
        if not person:
            return tree

        if gen_nr == 1:
            tree = self.draw_box(new_center, 0, person)
        else:
            tree = self.draw_connected_box(old_center, new_center,
                                           gen_nr-1, person_handle)

        if gen_nr == maxgen:
            return tree

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + gen_nr*_WIDTH + (gen_nr-1)*_HGAP
            tree += self.extend_line(new_center, line_offset)

            family = self.dbase_.get_family_from_handle(family_handle)

            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size,
                                   new_center, f_center, f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size,
                                   new_center, m_center, m_handle)
        return tree

    def display_ind_associations(self, assoclist):
        """
        Display an individual's associations

        @param: assoclist -- The list of persons for association
        """
        # begin Associations division
        with Html("div", class_="subsection", id="Associations") as section:
            section += Html("h4", _('Associations'), inline=True)

            with Html("table", class_="infolist assoclist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                assoc_row = [
                    (_("Person"), 'Person'),
                    (_('Relationship'), 'Relationship'),
                    (NHEAD, 'Notes'),
                    (SHEAD, 'Sources'),
                    ]

                trow.extend(
                    Html("th", label, class_="Column" + colclass, inline=True)
                    for (label, colclass) in assoc_row)

                tbody = Html("tbody")
                table += tbody

                for person_ref in assoclist:
                    trow = Html("tr")
                    tbody += trow

                    person_lnk = self.new_person_link(person_ref.ref,
                                                      uplink=True)

                    index = 0
                    for data in [
                        person_lnk,
                        person_ref.get_relation(),
                        self.dump_notes(person_ref.get_note_list()),
                        self.get_citation_links(person_ref.get_citation_list()),
                        ]:

                        # get colclass from assoc_row
                        colclass = assoc_row[index][1]

                        trow += Html("td", data, class_="Column" + colclass,
                            inline=True)
                        index += 1

        # return section to its callers
        return section

    def display_ind_pedigree(self):
        """
        Display an individual's pedigree
        """
        birthorder = self.report.options["birthorder"]

        # Define helper functions
        def children_ped(ol_html):
            """
            Create a children list

            @param: ol_html -- The html element to complete
            """
            if family:
                childlist = family.get_child_ref_list()

                childlist = [child_ref.ref for child_ref in childlist]
                children = add_birthdate(self.dbase_, childlist)

                if birthorder:
                    children = sorted(children)

                for birthdate, handle in children:
                    if handle == self.person.get_handle():
                        child_ped(ol_html)
                    elif handle:
                        child = self.dbase_.get_person_from_handle(handle)
                        if child:
                            ol_html += Html("li") + self.pedigree_person(child)
            else:
                child_ped(ol_html)
            return ol_html

        def child_ped(ol_html):
            """
            Create a child element list

            @param: ol_html -- The html element to complete
            """
            with Html("li", self.name, class_="thisperson") as pedfam:
                family = self.pedigree_family()
                if family:
                    pedfam += Html("ol", class_="spouselist") + family
            return ol_html + pedfam
        # End of helper functions

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = self.dbase_.get_family_from_handle(parent_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.dbase_.get_person_from_handle(mother_handle)
            else:
                mother = None
            if father_handle:
                father = self.dbase_.get_person_from_handle(father_handle)
            else:
                father = None
        else:
            family = None
            father = None
            mother = None

        with Html("div", id="pedigree", class_="subsection") as ped:
            ped += Html("h4", _('Pedigree'), inline=True)
            with Html("ol", class_="pedigreegen") as pedol:
                ped += pedol
                if father and mother:
                    pedfa = Html("li") + self.pedigree_person(father)
                    pedol += pedfa
                    with Html("ol") as pedma:
                        pedfa += pedma
                        pedma += (Html("li", class_="spouse") +
                                      self.pedigree_person(mother) +
                                      children_ped(Html("ol"))
                                 )
                elif father:
                    pedol += (Html("li") + self.pedigree_person(father) +
                                  children_ped(Html("ol"))
                             )
                elif mother:
                    pedol += (Html("li") + self.pedigree_person(mother) +
                                  children_ped(Html("ol"))
                             )
                else:
                    pedol += (Html("li") + children_ped(Html("ol")))
        return ped

    def display_ind_general(self):
        """
        display an individual's general information...
        """
        self.page_title = self.sort_name
        thumbnail = self.disp_first_img_as_thumbnail(
                                      self.person.get_media_list(), self.person)
        section_title = Html("h3", html_escape(self.page_title),
                             inline=True) + \
                        (Html('sup') +\
                         (Html('small') +
                      self.get_citation_links(self.person.get_citation_list())))

        # begin summaryarea division
        with Html("div", id='summaryarea') as summaryarea:

            # begin general details table
            with Html("table", class_="infolist") as table:
                summaryarea += table

                primary_name = self.person.get_primary_name()
                all_names = [primary_name] + self.person.get_alternate_names()
                # if the callname or the nickname is the same as the 'first
                # name' (given name), then they are not displayed.
                first_name = primary_name.get_first_name()

                # Names [and their sources]
                for name in all_names:
                    pname = html_escape(_nd.display_name(name))
                    pname += self.get_citation_links(name.get_citation_list())

                    # if we have just a firstname, then the name is preceeded
                    # by ", " which doesn't exactly look very nice printed on
                    # the web page
                    if pname[:2] == ', ':
                        pname = pname[2:]
                    if name != primary_name:
                        datetext = _dd.display(name.date)
                        if datetext:
                            pname = datetext + ': ' + pname

                    type_ = str(name.get_type())
                    trow = Html("tr") + (
                           Html("td", type_, class_="ColumnAttribute",
                                inline=True)
                                         )

                    tcell = Html("td", pname, class_="ColumnValue")
                    # display any notes associated with this name
                    notelist = name.get_note_list()
                    if len(notelist):
                        unordered = Html("ul")

                        for notehandle in notelist:
                            note = self.dbase_.get_note_from_handle(notehandle)
                            if note:
                                note_text = self.get_note_format(note, True)

                                # attach note
                                unordered += note_text
                        tcell += unordered
                    trow += tcell
                    table += trow

                    # display the callname associated with this name.
                    call_name = name.get_call_name()
                    if call_name and call_name != first_name:
                        trow = Html("tr") + (
                            Html("td", _("Call Name"), class_="ColumnAttribute",
                                 inline=True),
                            Html("td", call_name, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                    # display the nickname associated with this name. Note that
                    # this no longer displays the Nickname attribute (if
                    # present), because the nickname attribute is deprecated in
                    # favour of the nick_name property of the name structure
                    # (see http://gramps.1791082.n4.nabble.com/Where-is-
                    # nickname-stored-tp4469779p4484272.html), and also because
                    # the attribute is (normally) displayed lower down the
                    # wNarrative Web report.
                    nick_name = name.get_nick_name()
                    if nick_name and nick_name != first_name:
                        trow = Html("tr") + (
                            Html("td", _("Nick Name"), class_="ColumnAttribute",
                                 inline=True),
                            Html("td", nick_name, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                # Gramps ID
                person_gid = self.person.get_gramps_id()
                if not self.noid and person_gid:
                    trow = Html("tr") + (
                        Html("td", GRAMPSID, class_="ColumnAttribute",
                             inline=True),
                        Html("td", person_gid, class_="ColumnValue",
                             inline=True)
                        )
                    table += trow

                # Gender
                gender = self.gender_map[self.person.gender]
                trow = Html("tr") + (
                    Html("td", _("Gender"), class_="ColumnAttribute",
                         inline=True),
                    Html("td", gender, class_="ColumnValue", inline=True)
                    )
                table += trow

                # Age At Death???
                birth_date = Date.EMPTY
                birth_ref = self.person.get_birth_ref()
                if birth_ref:
                    birth = self.dbase_.get_event_from_handle(birth_ref.ref)
                    if birth:
                        birth_date = birth.get_date_object()

                if birth_date and birth_date is not Date.EMPTY:
                    alive = probably_alive(self.person, self.dbase_, Today())

                    death_date = _find_death_date(self.dbase_, self.person)
                    if not alive and death_date is not None:
                        nyears = death_date - birth_date
                        nyears.format(precision=3)
                        trow = Html("tr") + (
                            Html("td", _("Age at Death"),
                                 class_="ColumnAttribute", inline=True),
                            Html("td", nyears,
                                 class_="ColumnValue", inline=True)
                            )
                        table += trow

        # return all three pieces to its caller
        # do NOT combine before returning
        return thumbnail, section_title, summaryarea

    def display_ind_events(self, place_lat_long):
        """
        will create the events table

        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        """
        event_ref_list = self.person.get_event_ref_list()
        if not event_ref_list:
            return None

        # begin events division and section title
        with Html("div", id="events", class_="subsection") as section:
            section += Html("h4", _("Events"), inline=True)

            # begin events table
            with Html("table", class_="infolist eventlist") as table:
                section += table

                thead = Html("thead")
                table += thead

                # attach event header row
                thead += self.event_header_row()

                tbody = Html("tbody")
                table += tbody

                for evt_ref in event_ref_list:
                    event = self.dbase_.get_event_from_handle(evt_ref.ref)
                    if event:

                        # display event row
                        tbody += self.display_event_row(event, evt_ref,
                                                        place_lat_long,
                                                        True, True,
                                                        EventRoleType.PRIMARY)
        return section

    def display_parent(self, handle, title, rel):
        """
        This will display a parent ...

        @param: handle -- The person handle
        @param: title  -- Is the title of the web page
        @param: rel    -- The relation
        """
        tcell1 = Html("td", title, class_="ColumnAttribute", inline=True)
        tcell2 = Html("td", class_="ColumnValue")

        tcell2 += self.new_person_link(handle, uplink=True)

        if rel and rel != ChildRefType(ChildRefType.BIRTH):
            tcell2 += ''.join(['&nbsp;'] *3 + ['(%s)']) % str(rel)

        # return table columns to its caller
        return tcell1, tcell2

    def get_reln_in_family(self, ind, family):
        """
        Display the relation of the indiv in the family

        @param: ind    -- The person to use
        @param: family -- The family
        """
        child_handle = ind.get_handle()
        child_ref_list = family.get_child_ref_list()
        for child_ref in child_ref_list:
            if child_ref.ref == child_handle:
                return (child_ref.get_father_relation(),
                        child_ref.get_mother_relation())
        return (None, None)

    def display_ind_parent_family(self, birthmother, birthfather, family,
                                  table,
                                  first=False):
        """
        Display the individual parent family

        @param: birthmother -- The birth mother
        @param: birthfather -- The birth father
        @param: family      -- The family
        @param: table       -- The html document to complete
        @param: first       -- Is this the first indiv ?
        """
        if not first:
            trow = Html("tr") + (Html("td", "&nbsp;", colspan=3,
                                      inline=True))
            table += trow

        # get the father
        father_handle = family.get_father_handle()
        if father_handle:
            if father_handle == birthfather:
                # The parent may not be birth father in ths family, because it
                # may be a step family. However, it will be odd to display the
                # parent as anything other than "Father"
                reln = _("Father")
            else:
                # Stepfather may not always be quite right (for example, it may
                # actually be StepFather-in-law), but it is too expensive to
                # calculate out the correct relationship using the Relationship
                # Calculator
                reln = _("Stepfather")
            trow = Html("tr") + (self.display_parent(father_handle, reln, None))
            table += trow

        # get the mother
        mother_handle = family.get_mother_handle()
        if mother_handle:
            if mother_handle == birthmother:
                reln = _("Mother")
            else:
                reln = _("Stepmother")
            trow = Html("tr") + (self.display_parent(mother_handle, reln, None))
            table += trow

        for child_ref in family.get_child_ref_list():
            child_handle = child_ref.ref
            child = self.dbase_.get_person_from_handle(child_handle)
            if child:
                if child == self.person:
                    reln = ""
                else:
                    try:
                        # We have a try except block here, because the two
                        # people MUST be siblings for the called Relationship
                        # routines to work. Depending on your definition of
                        # sibling, we cannot necessarily guarantee that.
                        sibling_type = self.rel_class.get_sibling_type(
                                self.dbase_, self.person, child)

                        reln = self.rel_class.get_sibling_relationship_string(
                                sibling_type, self.person.gender,
                                child.gender)
                        reln = reln[0].upper() + reln[1:]
                    except:
                        reln = _("Not siblings")

                reln = "&nbsp;&nbsp;&nbsp;&nbsp;" + reln
                # Now output reln, child_link, (frel, mrel)
                frel = child_ref.get_father_relation()
                mrel = child_ref.get_mother_relation()
                if frel != ChildRefType.BIRTH or \
                   mrel != ChildRefType.BIRTH:
                    frelmrel = "(%s, %s)" % (str(frel), str(mrel))
                else:
                    frelmrel = ""
                trow = Html("tr") + (
                    Html("td", reln, class_="ColumnAttribute", inline=True))

                tcell = Html("td", class_="ColumnValue", inline=True)
                tcell += "&nbsp;&nbsp;&nbsp;&nbsp;"
                tcell += self.display_child_link(child_handle)
                trow += tcell
                tcell = Html("td", frelmrel, class_="ColumnValue",
                             inline=True)
                trow += tcell
                table += trow

    def display_step_families(self, parent_handle,
                              family,
                              all_family_handles,
                              birthmother, birthfather,
                              table):
        """
        Display step families

        @param: parent_handle      -- The family parent handle to display
        @param: family             -- The family
        @param: all_family_handles -- All known family handles
        @param: birthmother        -- The birth mother
        @param: birthfather        -- The birth father
        @param: table              -- The html document to complete
        """
        if parent_handle:
            parent = self.dbase_.get_person_from_handle(parent_handle)
            for parent_family_handle in parent.get_family_handle_list():
                if parent_family_handle not in all_family_handles:
                    parent_family = self.dbase_.get_family_from_handle(
                                        parent_family_handle)
                    self.display_ind_parent_family(birthmother, birthfather,
                                                   parent_family, table)
                    all_family_handles.append(parent_family_handle)

    def display_ind_center_person(self):
        """
        Display the person's relationship to the center person
        """
        center_person = self.report.database.get_person_from_gramps_id(
                                                     self.report.options['pid'])
        relationship = self.rel_class.get_one_relationship(self.dbase_,
                                                           self.person,
                                                           center_person)
        if relationship == "": # No relation to display
            return

        # begin center_person division
        section = ""
        with Html("div", class_="subsection", id="parents") as section:
            message = _("Relation to the center person")
            message += " ("
            name_format = self.report.options['name_format']
            primary_name = center_person.get_primary_name()
            name = Name(primary_name)
            name.set_display_as(name_format)
            message += _nd.display_name(name)
            message += ") : "
            message += relationship
            section += Html("h4", message, inline=True)
        return section

    def display_ind_parents(self):
        """
        Display a person's parents
        """
        parent_list = self.person.get_parent_family_handle_list()
        if not parent_list:
            return None

        # begin parents division
        with Html("div", class_="subsection", id="parents") as section:
            section += Html("h4", _("Parents"), inline=True)

            # begin parents table
            with Html("table", class_="infolist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                          (_("Relation to main person"), "ColumnAttribute"),
                          (_("Name"), "ColumnValue"),
                          (_("Relation within this family (if not by birth)"),
                             "ColumnValue")
                        ]
                )

                tbody = Html("tbody")
                table += tbody

                all_family_handles = list(parent_list)
                (birthmother, birthfather) = self.rel_class.get_birth_parents(
                                                self.dbase_, self.person)

                first = True
                for family_handle in parent_list:
                    family = self.dbase_.get_family_from_handle(family_handle)
                    if family:
                        # Display this family
                        self.display_ind_parent_family(
                                                    birthmother, birthfather,
                                                    family, table, first)
                        first = False

                        if self.report.options['showhalfsiblings']:
                            # Display all families in which the parents are
                            # involved. This displays half siblings and step
                            # siblings
                            self.display_step_families(
                                    family.get_father_handle(), family,
                                    all_family_handles,
                                    birthmother, birthfather, table)
                            self.display_step_families(
                                    family.get_mother_handle(), family,
                                    all_family_handles,
                                    birthmother, birthfather, table)
        return section

    def pedigree_person(self, person):
        """
        will produce a hyperlink for a pedigree person ...

        @param: person -- The person
        """
        hyper = self.new_person_link(person.handle, person=person, uplink=True)
        return hyper

    def pedigree_family(self):
        """
        Returns a family pedigree
        """
        ped = []
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.dbase_.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person, rel_family)
            if spouse_handle:
                spouse = self.dbase_.get_person_from_handle(spouse_handle)
                pedsp = (Html("li", class_="spouse") +
                         self.pedigree_person(spouse)
                        )
            else:
                pedsp = (Html("li", class_="spouse"))
            ped += [pedsp]
            childlist = rel_family.get_child_ref_list()
            if childlist:
                with Html("ol") as childol:
                    pedsp += [childol]
                    for child_ref in childlist:
                        child = self.dbase_.get_person_from_handle(
                                                                  child_ref.ref)
                        if child:
                            childol += (Html("li") +
                                        self.pedigree_person(child)
                                    )
        return ped

    def display_event_header(self):
        """
        will print the event header row for display_event_row() and
            format_family_events()
        """
        trow = Html("tr")

        trow.extend(
                Html("th", label, class_="Column" + colclass, inline=True)
                for (label, colclass) in  [
                    (_EVENT, "Event"),
                    (DHEAD, "Date"),
                    (PHEAD, "Place"),
                    (DESCRHEAD, "Description"),
                    (NHEAD, "Notes"),
                    (SHEAD, "Sources")]
                )
        return trow

#################################################
#
#    creates the Repository List Page and Repository Pages
#
#################################################
class RepositoryPages(BasePage):
    """
    This class is responsible for displaying information about the 'Repository'
    database objects. It displays this information under the 'Individuals'
    tab. It is told by the 'add_instances' call which 'Repository's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for this report
        """
        BasePage.__init__(self, report, title="")
        self.repos_dict = defaultdict(set)

    def display_pages(self, title):
        """
        Generate and output the pages under the Repository tab, namely the
        repository index and the individual repository pages.

        @param: title  -- Is the title of the web page
        """
        LOG.debug("obj_dict[Person]")
        for item in self.report.obj_dict[Repository].items():
            LOG.debug("    %s", str(item))

        # set progress bar pass for Repositories
        with self.report.user.progress(_("Narrated Web Site Report"),
                         _('Creating repository pages'),
                         len(self.report.obj_dict[Repository]) + 1) as step:
            # Sort the repositories
            repos_dict = {}
            for repository_handle in self.report.obj_dict[Repository]:
                repository = self.report.database.get_repository_from_handle(
                                                              repository_handle)
                key = repository.get_name() + str(repository.get_gramps_id())
                repos_dict[key] = (repository, repository_handle)

            keys = sorted(repos_dict, key=SORT_KEY)

            # RepositoryListPage Class
            self.repositorylistpage(self.report, title, repos_dict, keys)

            for index, key in enumerate(keys):
                (repo, handle) = repos_dict[key]

                step()
                self.repositorypage(self.report, title, repo, handle)

    def repositorylistpage(self, report, title, repos_dict, keys):
        """
        Create Index for repositories

        @param: report     -- The instance of the main report class
                              for this report
        @param: title      -- Is the title of the web page
        @param: repos_dict -- The dictionary for all repositories
        @param: keys       -- The keys used to access repositories
        """
        BasePage.__init__(self, report, title)
        #inc_repos = self.report.options["inc_repository"]

        output_file, sio = self.report.create_file("repositories")
        repolistpage, head, body = self.write_header(_("Repositories"))

        ldatec = 0
        # begin RepositoryList division
        with Html("div", class_="content",
                  id="RepositoryList") as repositorylist:
            body += repositorylist

            msg = _("This page contains an index of "
                    "all the repositories in the "
                    "database, sorted by their title. "
                    "Clicking on a repositories&#8217;s "
                    "title will take you to that repositories&#8217;s page.")
            repositorylist += Html("p", msg, id="description")

            # begin repositories table and table head
            with Html("table", class_="infolist primobjlist repolist") as table:
                repositorylist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", "&nbsp;", class_="ColumnRowLabel", inline=True),
                    Html("th", THEAD, class_="ColumnType", inline=True),
                    Html("th", _("Repository |Name"), class_="ColumnName",
                         inline=True)
                    )
                thead += trow

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for index, key in enumerate(keys):
                    (repo, handle) = repos_dict[key]

                    trow = Html("tr")
                    tbody += trow

                    # index number
                    trow += Html("td", index + 1, class_="ColumnRowLabel",
                                 inline=True)

                    # repository type
                    rtype = str(repo.type)
                    trow += Html("td", rtype, class_="ColumnType", inline=True)

                    # repository name and hyperlink
                    if repo.get_name():
                        trow += Html("td",
                                     self.repository_link(handle,
                                                          repo.get_name(),
                                                          repo.get_gramps_id(),
                                                          self.uplink),
                                     class_="ColumnName")
                        ldatec = repo.get_change_time()
                    else:
                        trow += Html("td", "[ untitled ]", class_="ColumnName")

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(repolistpage, output_file, sio, ldatec)

    def repositorypage(self, report, title, repo, handle):
        """
        Create one page for one repository.

        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        @param: repo   -- the repository to use
        @param: handle -- the handle to use
        """
        gid = repo.get_gramps_id()
        BasePage.__init__(self, report, title, gid)
        ldatec = repo.get_change_time()

        output_file, sio = self.report.create_file(handle, 'repo')
        self.uplink = True
        repositorypage, head, body = self.write_header(_('Repositories'))

        # begin RepositoryDetail division and page title
        with Html("div", class_="content",
                  id="RepositoryDetail") as repositorydetail:
            body += repositorydetail

            # repository name
            repositorydetail += Html("h3", html_escape(repo.name), inline=True)

            # begin repository table
            with Html("table", class_="infolist repolist") as table:
                repositorydetail += table

                tbody = Html("tbody")
                table += tbody

                if not self.noid and gid:
                    trow = Html("tr") + (
                        Html("td", _("Gramps ID"), class_="ColumnAttribute",
                             inline=True),
                        Html("td", gid, class_="ColumnValue", inline=True)
                    )
                    tbody += trow

                trow = Html("tr") + (
                    Html("td", _("Type"), class_="ColumnAttribute",
                         inline=True),
                    Html("td", str(repo.get_type()), class_="ColumnValue",
                         inline=True)
                )
                tbody += trow

            # repository: address(es)...
            # repository addresses do NOT have Sources
            repo_address = self.display_addr_list(repo.get_address_list(),
                                                  False)
            if repo_address is not None:
                repositorydetail += repo_address

            # repository: urllist
            urllist = self.display_url_list(repo.get_url_list())
            if urllist is not None:
                repositorydetail += urllist

            # reposity: notelist
            notelist = self.display_note_list(repo.get_note_list())
            if notelist is not None:
                repositorydetail += notelist

            # display Repository Referenced Sources...
            ref_list = self.display_bkref_list(Repository, repo.get_handle())
            if ref_list is not None:
                repositorydetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(repositorypage, output_file, sio, ldatec)

class AddressBookListPage(BasePage):
    """
    Create the index for addresses.
    """
    def __init__(self, report, title, has_url_addr_res):
        """
        @param: report           -- The instance of the main report class
                                    for this report
        @param: title            -- Is the title of the web page
        @param: has_url_addr_res -- The url, address and residence to use
                                    for the report
        """
        BasePage.__init__(self, report, title)

        # Name the file, and create it
        output_file, sio = self.report.create_file("addressbook")

        # Add xml, doctype, meta and stylesheets
        addressbooklistpage, head, body = self.write_header(_("Address Book"))

        # begin AddressBookList division
        with Html("div", class_="content",
                  id="AddressBookList") as addressbooklist:
            body += addressbooklist

            # Address Book Page message
            msg = _("This page contains an index of all the individuals in "
                    "the database, sorted by their surname, with one of the "
                    "following: Address, Residence, or Web Links. "
                    "Selecting the person&#8217;s name will take you "
                    "to their individual Address Book page.")
            addressbooklist += Html("p", msg, id="description")

            # begin Address Book table
            with Html("table",
                      class_="infolist primobjlist addressbook") as table:
                addressbooklist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        ["&nbsp;", "ColumnRowLabel"],
                        [_("Full Name"), "ColumnName"],
                        [_("Address"), "ColumnAddress"],
                        [_("Residence"), "ColumnResidence"],
                        [_("Web Links"), "ColumnWebLinks"]]
                        )

                tbody = Html("tbody")
                table += tbody

                index = 1
                for (sort_name, person_handle,
                     has_add, has_res,
                     has_url) in has_url_addr_res:

                    address = None
                    residence = None
                    weblinks = None

                    # has address but no residence event
                    if has_add and not has_res:
                        address = "X"

                    # has residence, but no addresses
                    elif has_res and not has_add:
                        residence = "X"

                    # has residence and addresses too
                    elif has_add and has_res:
                        address = "X"
                        residence = "X"

                    # has Web Links
                    if has_url:
                        weblinks = "X"

                    trow = Html("tr")
                    tbody += trow

                    trow.extend(
                        Html("td", data or "&nbsp;", class_=colclass,
                             inline=True)
                        for (colclass, data) in [
                            ["ColumnRowLabel", index],
                            ["ColumnName",
                                          self.addressbook_link(person_handle)],
                            ["ColumnAddress", address],
                            ["ColumnResidence", residence],
                            ["ColumnWebLinks", weblinks]]
                            )
                    index += 1

        # Add footer and clearline
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send the page out for processing
        # and close the file
        self.xhtml_writer(addressbooklistpage, output_file, sio, 0)

class AddressBookPage(BasePage):
    """
    Create one page for one Address
    """
    def __init__(self, report, title, person_handle, has_add, has_res, has_url):
        """
        @param: report        -- The instance of the main report class
                                 for this report
        @param: title         -- Is the title of the web page
        @param: person_handle -- the url, address and residence to use
                                 for the report
        @param: has_add       -- the address to use for the report
        @param: has_res       -- the residence to use for the report
        @param: has_url       -- the url to use for the report
        """
        person = report.database.get_person_from_handle(person_handle)
        BasePage.__init__(self, report, title, person.gramps_id)
        self.bibli = Bibliography()

        self.uplink = True

        # set the file name and open file
        output_file, sio = self.report.create_file(person_handle, "addr")
        addressbookpage, head, body = self.write_header(_("Address Book"))

        # begin address book page division and section title
        with Html("div", class_="content",
                  id="AddressBookDetail") as addressbookdetail:
            body += addressbookdetail

            link = self.new_person_link(person_handle, uplink=True,
                                        person=person)
            addressbookdetail += Html("h3", link)

            # individual has an address
            if has_add:
                addressbookdetail += self.display_addr_list(has_add, None)

            # individual has a residence
            if has_res:
                addressbookdetail.extend(
                    self.dump_residence(res)
                    for res in has_res
                )

            # individual has a url
            if has_url:
                addressbookdetail += self.display_url_list(has_url)

        # add fullclear for proper styling
        # and footer section to page
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(addressbookpage, output_file, sio, 0)

class NavWebReport(Report):
    """
    Create WebReport object that produces the report.
    """
    def __init__(self, database, options, user):
        """
        @param: database -- The GRAMPS database instance
        @param: options  -- Instance of the Options class for this report
        @param: user     -- Instance of a gen.user.User()
        """
        Report.__init__(self, database, options, user)
        self.user = user
        menu = options.menu
        self.link_prefix_up = True
        self.options = {}

        for optname in menu.get_all_option_names():
            menuopt = menu.get_option_by_name(optname)
            self.options[optname] = menuopt.get_value()

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu)
        stdoptions.run_private_data_option(self, menu)

        livinginfo = self.options['living_people']
        yearsafterdeath = self.options['years_past_death']

        if livinginfo != _INCLUDE_LIVING_VALUE:
            self.database = LivingProxyDb(self.database,
                                          livinginfo,
                                          None,
                                          yearsafterdeath)

        filters_option = menu.get_option_by_name('filter')
        self.filter = filters_option.get_filter()

        self.copyright = self.options['cright']
        self.target_path = self.options['target']
        self.ext = self.options['ext']
        self.css = self.options['css']
        self.navigation = self.options["navigation"]
        self.citationreferents = self.options['citationreferents']

        self.title = self.options['title']

        self.inc_gallery = self.options['gallery']
        self.inc_unused_gallery = self.options['unused']
        self.create_thumbs_only = self.options['create_thumbs_only']

        self.inc_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # name format options
        self.name_format = self.options['name_format']

        # include families or not?
        self.inc_families = self.options['inc_families']

        # create an event pages or not?
        self.inc_events = self.options['inc_events']

        # include repository page or not?
        self.inc_repository = self.options['inc_repository']

        # include GENDEX page or not?
        self.inc_gendex = self.options['inc_gendex']

        # Download Options Tab
        self.inc_download = self.options['incdownload']
        self.dl_fname1 = self.options['down_fname1']
        self.dl_descr1 = self.options['dl_descr1']
        self.dl_fname2 = self.options['down_fname2']
        self.dl_descr2 = self.options['dl_descr2']

        self.encoding = self.options['encoding']

        self.use_archive = self.options['archive']
        self.use_intro = self.options['intronote'] or \
                         self.options['introimg']
        self.use_home = self.options['homenote'] or \
                        self.options['homeimg']
        self.use_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # Do we need to include this in a cms ?
        self.usecms = self.options['usecms']
        self.target_uri = self.options['cmsuri']

        # Do we need to include web calendar ?
        self.usecal = self.options['usecal']
        self.target_cal_uri = self.options['caluri']

        # either include the gender graphics or not?
        self.ancestortree = self.options['ancestortree']

        # whether to display children in birthorder or entry order?
        self.birthorder = self.options['birthorder']

        # get option for Internet Address Book
        self.inc_addressbook = self.options["inc_addressbook"]

        # Place Map tab options
        self.placemappages = self.options['placemappages']
        self.familymappages = self.options['familymappages']
        self.mapservice = self.options['mapservice']
        self.googleopts = self.options['googleopts']

        if self.use_home:
            self.index_fname = "index"
            self.surname_fname = "surnames"
            self.intro_fname = "introduction"
        elif self.use_intro:
            self.index_fname = None
            self.surname_fname = "surnames"
            self.intro_fname = "index"
        else:
            self.index_fname = None
            self.surname_fname = "index"
            self.intro_fname = None

        self.archive = None
        self.cur_fname = None      # Internal use. The name of the output file,
                                   # to be used for the tar archive.
        self.string_io = None
        if self.use_archive:
            self.html_dir = None
        else:
            self.html_dir = self.target_path
        self.warn_dir = True       # Only give warning once.
        self.obj_dict = None
        self.visited = None
        self.bkref_dict = None
        self.rel_class = None
        self.tab = None

    def write_report(self):
        """
        The first method called to write the Narrative Web after loading options
        """
        global _WRONGMEDIAPATH

        _WRONGMEDIAPATH = []
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name is None:
                dir_name = get_curr_dir()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    msg = _("Neither %(current)s nor %(parent)s "
                            "are directories") % {
                                'current': dir_name, 'parent': parent_dir}
                    self.user.notify_error(msg)
                    return
                else:
                    try:
                        os.mkdir(dir_name)
                    except IOError as value:
                        msg = _("Could not create the directory: %s") % \
                              dir_name + "\n" + value[1]
                        self.user.notify_error(msg)
                        return
                    except:
                        msg = _("Could not create the directory: %s") % dir_name
                        self.user.notify_error(msg)
                        return

            try:
                image_dir_name = os.path.join(dir_name, 'images')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)

                image_dir_name = os.path.join(dir_name, 'thumb')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)
            except IOError as value:
                msg = _("Could not create the directory: %s") % \
                      image_dir_name + "\n" + value[1]
                self.user.notify_error(msg)
                return
            except:
                msg = _("Could not create the directory: %s") % \
                      image_dir_name + "\n" + value[1]
                self.user.notify_error(msg)
                return
        else:
            if os.path.isdir(self.target_path):
                self.user.notify_error(_('Invalid file name'),
                        _('The archive file must be a file, not a directory'))
                return
            try:
                self.archive = tarfile.open(self.target_path, "w:gz")
            except (OSError, IOError) as value:
                self.user.notify_error(
                            _("Could not create %s") % self.target_path,
                            str(value))
                return
        config.set('paths.website-directory',
                   os.path.dirname(self.target_path) + os.sep)
        if self.usecms:
            config.set('paths.website-cms-uri',
                       os.path.dirname(self.target_uri))
        if self.usecal:
            config.set('paths.website-cal-uri',
                       os.path.dirname(self.target_cal_uri))

        # for use with discovering biological, half, and step siblings for use
        # in display_ind_parents()...
        self.rel_class = get_relationship_calculator()

        #################################################
        #
        # Pass 0 Initialise the plug-ins
        #
        #################################################

        # FIXME: The whole of this section of code should be implemented by the
        # registration process for the Web Page plugins.

        # Note that by use of a dictionary we ensure that at most one Web Page
        # plugin is provided for any object class

        self.tab = {}
        # FIXME: Initialising self.tab in this way means that this code has to
        # run before the Web Page registration - I am not sure whether this is
        # possible, in which case an alternative approach to provinding the
        # mapping of object class to Web Page plugin will be needed.
        for obj_class in ("Person", "Family", "Source", "Citation", "Place",
                          "Event", "Media", "Repository"):
            # FIXME: Would it be better if the Web Page plugins used a different
            # base class rather than BasePage, which is really just for each web
            # page
            self.tab[obj_class] = BasePage(report=self, title="")

        # Note that by not initialising any Web Page plugins that are not going
        # to generate pages, we ensure that there is not performance implication
        # for such plugins.
        self.tab["Person"] = PersonPages(self)
        if self.inc_families:
            self.tab["Family"] = FamilyPages(self)
        if self.inc_events:
            self.tab["Event"] = EventPages(self)
        if self.inc_gallery:
            self.tab["Media"] = MediaPages(self)
        self.tab["Place"] = PlacePages(self)
        self.tab["Source"] = SourcePages(self)
        self.tab["Repository"] = RepositoryPages(self)
        self.tab["Citation"] = CitationPages(self)

        # FIXME: The following routines that are not run in two passes have not
        # yet been converted to a form suitable for separation into Web Page
        # plugins: SurnamePage, SurnameListPage, IntroductionPage, HomePage,
        # ThumbnailPreviewPage, DownloadPage, ContactPage,AddressBookListPage,
        # AddressBookPage

        #################################################
        #
        # Pass 1 Build the lists of objects to be output
        #
        #################################################

        self._build_obj_dict()

        #################################################
        #
        # Pass 2 Generate the web pages
        #
        #################################################

        self.base_pages()
        self.visited = []

        # build classes IndividualListPage and IndividualPage
        self.tab["Person"].display_pages(self.title)

        self.build_gendex(self.obj_dict[Person])

        # build classes SurnameListPage and SurnamePage
        self.surname_pages(self.obj_dict[Person])

        # build classes FamilyListPage and FamilyPage
        if self.inc_families:
            self.tab["Family"].display_pages(self.title)

        # build classes EventListPage and EventPage
        if self.inc_events:
            self.tab["Event"].display_pages(self.title)

        # build classes PlaceListPage and PlacePage
        self.tab["Place"].display_pages(self.title)

        # build classes RepositoryListPage and RepositoryPage
        if self.inc_repository:
            self.tab["Repository"].display_pages(self.title)

        # build classes MediaListPage and MediaPage
        if self.inc_gallery:
            if not self.create_thumbs_only:
                self.tab["Media"].display_pages(self.title)

            # build Thumbnail Preview Page...
            self.thumbnail_preview_page()

        # build classes AddressBookListPage and AddressBookPage
        if self.inc_addressbook:
            self.addressbook_pages(self.obj_dict[Person])

        # build classes SourceListPage and SourcePage
        self.tab["Source"].display_pages(self.title)

        # copy all of the neccessary files
        self.copy_narrated_files()

        # if an archive is being used, close it?
        if self.archive:
            self.archive.close()

        if len(_WRONGMEDIAPATH) > 0:
            error = '\n'.join([_('ID=%(grampsid)s, path=%(dir)s') % {
                            'grampsid': x[0],
                            'dir': x[1]} for x in _WRONGMEDIAPATH[:10]])
            if len(_WRONGMEDIAPATH) > 10:
                error += '\n ...'
            self.user.warn(_("Missing media objects:"), error)

    def _build_obj_dict(self):
        """
        Construct the dictionaries of objects to be included in the reports.
        There are two dictionaries, which have the same structure: they are two
        level dictionaries,the first key is the class of object
        (e.g. gen.lib.Person).
        The second key is the handle of the object.

        For the obj_dict, the value is a tuple containing the gramps_id,
        the text name for the object, and the file name for the display.

        For the bkref_dict, the value is a tuple containg the class of object
        and the handle for the object that refers to the 'key' object.
        """
        _obj_class_list = (Person, Family, Event, Place, Source, Citation,
                           Media, Repository, Note, Tag)

        # setup a dictionary of the required structure
        self.obj_dict = defaultdict(lambda: defaultdict(set))
        self.bkref_dict = defaultdict(lambda: defaultdict(set))

        # initialise the dictionary to empty in case no objects of any
        # particular class are incuded in the web report
        for obj_class in _obj_class_list:
            self.obj_dict[obj_class] = defaultdict(set)

        ind_list = self.database.iter_person_handles()
        with self.user.progress(_("Narrated Web Site Report"),
                                  _('Applying Person Filter...'),
                                  self.database.get_number_of_people()) as step:
            ind_list = self.filter.apply(self.database, ind_list,
                                         step)

        with self.user.progress(_("Narrated Web Site Report"),
                                  _('Constructing list of other objects...'),
                                  sum(1 for _ in ind_list)) as step:
            for handle in ind_list:
                # FIXME work around bug that self.database.iter under python 3
                # returns (binary) data rather than text
                if not isinstance(handle, str):
                    handle = handle.decode('utf-8')
                step()
                self._add_person(handle, "", "")

        LOG.debug("final object dictionary \n" + "".join(
                         ("%s: %s\n" % item) for item in self.obj_dict.items()))

        LOG.debug("final backref dictionary \n" + "".join(
                       ("%s: %s\n" % item) for item in self.bkref_dict.items()))

    def _add_person(self, person_handle, bkref_class, bkref_handle):
        """
        Add person_handle to the obj_dict, and recursively all referenced
        objects

        @param: person_handle -- The handle for the person to add
        @param: bkref_class   -- The class associated to this handle (person)
        @param: bkref_handle  -- The handle associated to this person
        """
        person = self.database.get_person_from_handle(person_handle)
        person_name = self.get_person_name(person)
        person_fname = self.build_url_fname(person_handle, "ppl",
                                                   False) + self.ext
        self.obj_dict[Person][person_handle] = (person_fname, person_name,
                                                person.gramps_id)
        self.bkref_dict[Person][person_handle].add((bkref_class, bkref_handle))

        if person:
            ############### Header section ##############
            for citation_handle in person.get_citation_list():
                self._add_citation(citation_handle, Person, person_handle)

            ############### Name section ##############
            for name in [person.get_primary_name()] + \
                            person.get_alternate_names():
                for citation_handle in name.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Events section ##############
            # Now tell the events tab to display the individual events
            evt_ref_list = person.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    event = self.database.get_event_from_handle(evt_ref.ref)
                    if event:
                        self._add_event(evt_ref.ref, Person, person_handle)
                        place_handle = event.get_place_handle()
                        if place_handle:
                            self._add_place(place_handle, Person,
                                            person_handle, event)
                        # If event pages are not being output, then tell the
                        # media tab to display the perosn's event media. If
                        # events are being displayed, then the media are linked
                        # from the event tab
                        if not self.inc_events:
                            for media_ref in event.get_media_list():
                                media_handle = media_ref.get_reference_handle()
                                self._add_media(media_handle, Person,
                                                person_handle)

                        for citation_handle in event.get_citation_list():
                            self._add_citation(citation_handle, Person,
                                               person_handle)

            ############### Families section ##############
            # Tell the families tab to display this individuals families
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                for family_handle in person.get_family_handle_list():
                    self._add_family(family_handle, Person, person_handle)

                    # Tell the events tab to display the family events which are
                    # referenced from the individual page.
                    family = self.database.get_family_from_handle(family_handle)
                    if family:
                        family_evt_ref_list = family.get_event_ref_list()
                        if family_evt_ref_list:
                            for evt_ref in family_evt_ref_list:
                                event = self.database.get_event_from_handle(
                                                                    evt_ref.ref)
                                if event:
                                    self._add_event(evt_ref.ref, Person,
                                                    person_handle)
                                    place_handle = event.get_place_handle()
                                    if place_handle:
                                        self._add_place(place_handle, Person,
                                                        person_handle, event)
                                    for citation_handle in event.get_citation_list():
                                        self._add_citation(citation_handle,
                                                           Person,
                                                           person_handle)
                    # add the family media and the family event media if the
                    # families page is not being displayed (If it is displayed,
                    # the media are linked from the families page)
                                    if not self.inc_families:
                                        for media_ref in event.get_media_list():
                                            media_handle = media_ref.get_reference_handle()
                                            self._add_media(media_handle,
                                                            Person,
                                                            person_handle)

                        for lds_ord in family.get_lds_ord_list():
                            for citation_handle in lds_ord.get_citation_list():
                                self._add_citation(citation_handle,
                                                   Person, person_handle)

                        for attr in family.get_attribute_list():
                            for citation_handle in attr.get_citation_list():
                                self._add_citation(citation_handle,
                                                   Person, person_handle)

                        if not self.inc_families:
                            for media_ref in family.get_media_list():
                                media_handle = media_ref.get_reference_handle()
                                self._add_media(media_handle, Person,
                                                person_handle)

            ############### LDS Ordinance section ##############
            for lds_ord in person.get_lds_ord_list():
                for citation_handle in lds_ord.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Attribute section ##############
            for attr in person.get_attribute_list():
                for citation_handle in attr.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Address section ##############
            for addr in person.get_address_list():
                for addr_handle in addr.get_citation_list():
                    self._add_citation(addr_handle, Person, person_handle)

            ############### Media section ##############
            # Now tell the Media tab which media objects to display
            # First the person's media objects
            for media_ref in person.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Person, person_handle)

    def get_person_name(self, person):
        """
        Return a string containing the person's primary name in the name
        format chosen in the web report options

        @param: person -- person object from database
        """
        name_format = self.options['name_format']
        primary_name = person.get_primary_name()
        name = Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def _add_family(self, family_handle, bkref_class, bkref_handle):
        """
        Add family to the Family object list

        @param: family_handle -- The handle for the family to add
        @param: bkref_class   -- The class associated to this handle (family)
        @param: bkref_handle  -- The handle associated to this family
        """
        family = self.database.get_family_from_handle(family_handle)
        family_name = self.get_family_name(family)
        if self.inc_families:
            family_fname = self.build_url_fname(family_handle, "fam",
                                                   False) + self.ext
        else:
            family_fname = ""
        self.obj_dict[Family][family_handle] = (family_fname, family_name,
                                                family.gramps_id)
        self.bkref_dict[Family][family_handle].add((bkref_class, bkref_handle))

        if self.inc_gallery:
            for media_ref in family.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Family, family_handle)

        ############### Events section ##############
        for evt_ref in family.get_event_ref_list():
            event = self.database.get_event_from_handle(evt_ref.ref)
            place_handle = event.get_place_handle()
            if place_handle:
                self._add_place(place_handle, Family, family_handle, event)

            if self.inc_events:
                # detail for family events are displayed on the events pages as
                # well as on this family page
                self._add_event(evt_ref.ref, Family, family_handle)
            else:
                # There is no event page. Family events are displayed on the
                # family page, but the associated family event media may need to
                # be displayed on the media page
                if self.inc_gallery:
                    for media_ref in event.get_media_list():
                        media_handle = media_ref.get_reference_handle()
                        self._add_media(media_handle, Family, family_handle)

        ############### LDS Ordinance section ##############
        for lds_ord in family.get_lds_ord_list():
            for citation_handle in lds_ord.get_citation_list():
                self._add_citation(citation_handle, Family, family_handle)

        ############### Attributes section ##############
        for attr in family.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Family, family_handle)

        ############### Sources section ##############
        for citation_handle in family.get_citation_list():
            self._add_citation(citation_handle, Family, family_handle)

    def get_family_name(self, family):
        """
        Return a string containing the name of the family (e.g. 'Family of John
        Doe and Jane Doe')

        @param: family -- family object from database
        """
        husband_handle = family.get_father_handle()
        spouse_handle = family.get_mother_handle()

        if husband_handle:
            husband = self.database.get_person_from_handle(husband_handle)
        else:
            husband = None
        if spouse_handle:
            spouse = self.database.get_person_from_handle(spouse_handle)
        else:
            spouse = None

        if husband and spouse:
            husband_name = self.get_person_name(husband)
            spouse_name = self.get_person_name(spouse)
            title_str = _("Family of %(husband)s and %(spouse)s") % {
                              'husband' : husband_name, 'spouse' : spouse_name}
        elif husband:
            husband_name = self.get_person_name(husband)
            # Only the name of the husband is known
            title_str = _("Family of %s") % husband_name
        elif spouse:
            spouse_name = self.get_person_name(spouse)
            # Only the name of the wife is known
            title_str = _("Family of %s") % spouse_name
        else:
            title_str = ''

        return title_str

    def _add_event(self, event_handle, bkref_class, bkref_handle):
        """
        Add event to the Event object list

        @param: event_handle -- The handle for the event to add
        @param: bkref_class  -- The class associated to this handle (event)
        @param: bkref_handle -- The handle associated to this event
        """
        event = self.database.get_event_from_handle(event_handle)
        event_name = event.get_description()
        # The event description can be Y on import from GEDCOM. See the
        # following quote from the GEDCOM spec: "The occurrence of an event is
        # asserted by the presence of either a DATE tag and value or a PLACe tag
        # and value in the event structure. When neither the date value nor the
        # place value are known then a Y(es) value on the parent event tag line
        # is required to assert that the event happened.""
        if event_name == "" or event_name is None or event_name == 'Y':
            event_name = str(event.get_type())
            # begin add generated descriptions to media pages
            # (request 7074 : acrider)
            ref_name = ""
            for reference in self.database.find_backlink_handles(event_handle):
                ref_class, ref_handle = reference
                if ref_class == 'Person':
                    person = self.database.get_person_from_handle(ref_handle)
                    ref_name = self.get_person_name(person)
                elif ref_class == 'Family':
                    family = self.database.get_family_from_handle(ref_handle)
                    ref_name = self.get_family_name(family)
            if ref_name != "":
                event_name += ", " + ref_name
            # end descriptions to media pages
        if self.inc_events:
            event_fname = self.build_url_fname(event_handle, "evt",
                                                   False) + self.ext
        else:
            event_fname = ""
        self.obj_dict[Event][event_handle] = (event_fname, event_name,
                                              event.gramps_id)
        self.bkref_dict[Event][event_handle].add((bkref_class, bkref_handle))

        ############### Attribute section ##############
        for attr in event.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Event, event_handle)

        ############### Source section ##############
        for citation_handle in event.get_citation_list():
            self._add_citation(citation_handle, Event, event_handle)

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in event.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Event, event_handle)

    def _add_place(self, place_handle, bkref_class, bkref_handle, event):
        """
        Add place to the Place object list

        @param: place_handle -- The handle for the place to add
        @param: bkref_class  -- The class associated to this handle (place)
        @param: bkref_handle -- The handle associated to this place
        """
        place = self.database.get_place_from_handle(place_handle)
        if place is None:
            return
        place_name = _pd.display_event(self.database, event)
        place_fname = self.build_url_fname(place_handle, "plc",
                                                   False) + self.ext
        self.obj_dict[Place][place_handle] = (place_fname, place_name,
                                              place.gramps_id, event)
        self.bkref_dict[Place][place_handle].add((bkref_class, bkref_handle))

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in place.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Place, place_handle)

        ############### Sources section ##############
        for citation_handle in place.get_citation_list():
            self._add_citation(citation_handle, Place, place_handle)

    def _add_source(self, source_handle, bkref_class, bkref_handle):
        """
        Add source to the Source object list

        @param: source_handle -- The handle for the source to add
        @param: bkref_class   -- The class associated to this handle (source)
        @param: bkref_handle  -- The handle associated to this source
        """
        source = self.database.get_source_from_handle(source_handle)
        source_name = source.get_title()
        source_fname = self.build_url_fname(source_handle, "src",
                                                   False) + self.ext
        self.obj_dict[Source][source_handle] = (source_fname, source_name,
                                                source.gramps_id)
        self.bkref_dict[Source][source_handle].add((bkref_class, bkref_handle))

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in source.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Source, source_handle)

        ############### Repository section ##############
        if self.inc_repository:
            for repo_ref in source.get_reporef_list():
                repo_handle = repo_ref.get_reference_handle()
                self._add_repository(repo_handle, Source, source_handle)

    def _add_citation(self, citation_handle, bkref_class, bkref_handle):
        """
        Add citation to the Citation object list

        @param: citation_handle -- The handle for the citation to add
        @param: bkref_class     -- The class associated to this handle
        @param: bkref_handle    -- The handle associated to this citation
        """
        citation = self.database.get_citation_from_handle(citation_handle)
        # If Page is none, we want to make sure that a tuple is generated for
        # the source backreference
        citation_name = citation.get_page() or ""
        source_handle = citation.get_reference_handle()
        self.obj_dict[Citation][citation_handle] = ("", citation_name,
                                                    citation.gramps_id)
        self.bkref_dict[Citation][citation_handle].add((bkref_class,
                                                        bkref_handle))

        ############### Source section ##############
        self._add_source(source_handle, Citation, citation_handle)

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in citation.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Citation, citation_handle)

    def _add_media(self, media_handle, bkref_class, bkref_handle):
        """
        Add media to the Media object list

        @param: media_handle -- The handle for the media to add
        @param: bkref_class  -- The class associated to this handle (media)
        @param: bkref_handle -- The handle associated to this media
        """
        media_refs = self.bkref_dict[Media].get(media_handle)
        if media_refs and (bkref_class, bkref_handle) in media_refs:
            return
        media = self.database.get_media_from_handle(media_handle)
        # use media title (request 7074 acrider)
        media_name = media.get_description()
        if media_name is None or media_name == "":
            media_name = "Media"
        #end media title
        if self.inc_gallery:
            media_fname = self.build_url_fname(media_handle, "img",
                                                   False) + self.ext
        else:
            media_fname = ""
        self.obj_dict[Media][media_handle] = (media_fname, media_name,
                                                    media.gramps_id)
        self.bkref_dict[Media][media_handle].add((bkref_class, bkref_handle))

        ############### Attribute section ##############
        for attr in media.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Media, media_handle)

        ############### Sources section ##############
        for citation_handle in media.get_citation_list():
            self._add_citation(citation_handle, Media, media_handle)

    def _add_repository(self, repos_handle, bkref_class, bkref_handle):
        """
        Add repository to the Repository object list

        @param: repos_handle -- The handle for the repository to add
        @param: bkref_class  -- The class associated to this handle (source)
        @param: bkref_handle -- The handle associated to this source
        """
        repos = self.database.get_repository_from_handle(repos_handle)
        repos_name = repos.name
        if self.inc_repository:
            repos_fname = self.build_url_fname(repos_handle, "repo",
                                                   False) + self.ext
        else:
            repos_fname = ""
        self.obj_dict[Repository][repos_handle] = (repos_fname, repos_name,
                                                   repos.gramps_id)
        self.bkref_dict[Repository][repos_handle].add((bkref_class,
                                                       bkref_handle))

    def copy_narrated_files(self):
        """
        Copy all of the CSS, image, and javascript files for Narrated Web
        """
        imgs = []

        # copy screen style sheet
        if CSS[self.css]["filename"]:
            fname = CSS[self.css]["filename"]
            self.copy_file(fname, _NARRATIVESCREEN, "css")

        # copy printer style sheet
        fname = CSS["Print-Default"]["filename"]
        self.copy_file(fname, _NARRATIVEPRINT, "css")

        # copy ancestor tree style sheet if tree is being created?
        if self.ancestortree:
            fname = CSS["ancestortree"]["filename"]
            self.copy_file(fname, "ancestortree.css", "css")

        # copy behaviour style sheet
        fname = CSS["behaviour"]["filename"]
        self.copy_file(fname, "behaviour.css", "css")

        # copy Menu Layout Style Sheet if Blue or Visually is being
        # used as the stylesheet?
        if CSS[self.css]["navigation"]:
            if self.navigation == "Horizontal":
                fname = CSS["Horizontal-Menus"]["filename"]
            elif self.navigation == "Vertical":
                fname = CSS["Vertical-Menus"]["filename"]
            elif self.navigation == "Fade":
                fname = CSS["Fade-Menus"]["filename"]
            elif self.navigation == "dropdown":
                fname = CSS["DropDown-Menus"]["filename"]
            self.copy_file(fname, "narrative-menus.css", "css")

        # copy narrative-maps Style Sheet if Place or Family Map pages
        # are being created?
        if self.placemappages or self.familymappages:
            fname = CSS["NarrativeMaps"]["filename"]
            self.copy_file(fname, "narrative-maps.css", "css")

        # Copy the Creative Commons icon if the Creative Commons
        # license is requested
        if 0 < self.copyright <= len(_CC):
            imgs += [CSS["Copyright"]["filename"]]

        # copy Gramps favorite icon #2
        imgs += [CSS["favicon2"]["filename"]]

        # we need the blank image gif needed by behaviour.css
        # add the document.png file for media other than photos
        imgs += CSS["All Images"]["images"]

        # copy Ancestor Tree graphics if needed???
        if self.ancestortree:
            imgs += CSS["ancestortree"]["images"]

        # Anything css-specific:
        imgs += CSS[self.css]["images"]

        # copy all to images subdir:
        for from_path in imgs:
            fdir, fname = os.path.split(from_path)
            self.copy_file(from_path, fname, "images")

    def build_gendex(self, ind_list):
        """
        Create a gendex file

        @param: ind_list -- The list of person to use
        """
        if self.inc_gendex:
            with self.user.progress(_("Narrated Web Site Report"),
                    _('Creating GENDEX file'), len(ind_list)) as step:
                fp_gendex, gendex_io = self.create_file("gendex", ext=".txt")
                date = 0
                for person_handle in ind_list:
                    step()
                    person = self.database.get_person_from_handle(person_handle)
                    datex = person.get_change_time()
                    if datex > date:
                        date = datex
                    if self.archive:
                        self.write_gendex(gendex_io, person)
                    else:
                        self.write_gendex(fp_gendex, person)
                self.close_file(fp_gendex, gendex_io, date)

    def write_gendex(self, filep, person):
        """
        Reference|SURNAME|given name /SURNAME/|date of birth|place of birth|
            date of death|place of death|
        * field 1: file name of web page referring to the individual
        * field 2: surname of the individual
        * field 3: full name of the individual
        * field 4: date of birth or christening (optional)
        * field 5: place of birth or christening (optional)
        * field 6: date of death or burial (optional)
        * field 7: place of death or burial (optional)

        @param: filep  -- The gendex output file name
        @param: person -- The person to use for gendex file
        """
        url = self.build_url_fname_html(person.handle, "ppl")
        surname = person.get_primary_name().get_surname()
        fullname = person.get_primary_name().get_gedcom_name()

        # get birth info:
        dob, pob = get_gendex_data(self.database, person.get_birth_ref())

        # get death info:
        dod, pod = get_gendex_data(self.database, person.get_death_ref())
        filep.write(
            '|'.join((url, surname, fullname, dob, pob, dod, pod)) + '|\n')

    def surname_pages(self, ind_list):
        """
        Generates the surname related pages from list of individual
        people.

        @param: ind_list -- The list of person to use
        """
        local_list = sort_people(self.database, ind_list)

        with self.user.progress(_("Narrated Web Site Report"),
                _("Creating surname pages"), len(local_list)) as step:

            SurnameListPage(self, self.title, ind_list,
                            SurnameListPage.ORDER_BY_NAME,
                            self.surname_fname)

            SurnameListPage(self, self.title, ind_list,
                            SurnameListPage.ORDER_BY_COUNT,
                            "surnames_count")

            for (surname, handle_list) in local_list:
                SurnamePage(self, self.title, surname, sorted(handle_list))
                step()

    def thumbnail_preview_page(self):
        """
        creates the thumbnail preview page
        """
        with self.user.progress(_("Narrated Web Site Report"),
                                  _("Creating thumbnail preview page..."),
                                  len(self.obj_dict[Media])) as step:
            ThumbnailPreviewPage(self, self.title, step)

    def addressbook_pages(self, ind_list):
        """
        Create a webpage with a list of address availability for each person
        and the associated individual address pages.

        @param: ind_list -- The list of person to use
        """
        url_addr_res = []

        for person_handle in ind_list:

            person = self.database.get_person_from_handle(person_handle)
            addrlist = person.get_address_list()
            evt_ref_list = person.get_event_ref_list()
            urllist = person.get_url_list()

            add = addrlist or None
            url = urllist or None
            res = []

            for event_ref in evt_ref_list:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event.get_type() == EventType.RESIDENCE:
                    res.append(event)

            if add or res or url:
                primary_name = person.get_primary_name()
                sort_name = ''.join([primary_name.get_surname(), ", ",
                                    primary_name.get_first_name()])
                url_addr_res.append((sort_name, person_handle, add, res, url))

        url_addr_res.sort()
        AddressBookListPage(self, self.title, url_addr_res)

        # begin Address Book pages
        addr_size = len(url_addr_res)

        with self.user.progress(_("Narrated Web Site Report"),
                                  _("Creating address book pages ..."),
                                  addr_size) as step:
            for (sort_name, person_handle, add, res, url) in url_addr_res:
                AddressBookPage(self, self.title, person_handle, add, res, url)
                step()

    def base_pages(self):
        """
        creates HomePage, ContactPage, DownloadPage, and IntroductionPage
        if requested by options in plugin
        """
        if self.use_home:
            HomePage(self, self.title)

        if self.inc_contact:
            ContactPage(self, self.title)

        if self.inc_download:
            DownloadPage(self, self.title)

        if self.use_intro:
            IntroductionPage(self, self.title)

    def build_subdirs(self, subdir, fname, uplink=False):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories
        with too many entries.

        For example, this may return "8/1/aec934857df74d36618"

        @param: subdir -- The subdirectory name to use
        @param: fname  -- The file name for which we need to build the path
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
                          If uplink = None then [./] for use in EventListPage
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())

        if self.usecms:
            if self.target_uri not in subdirs:
                subdirs = [self.target_uri] + subdirs
        else:
            if uplink == True:
                subdirs = ['..']*3 + subdirs

            # added for use in EventListPage
            elif uplink is None:
                subdirs = ['.'] + subdirs
        return subdirs

    def build_path(self, subdir, fname, uplink=False):
        """
        Return the name of the subdirectory.

        Notice that we DO use os.path.join() here.

        @param: subdir -- The subdirectory name to use
        @param: fname  -- The file name for which we need to build the path
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        return os.path.join(*self.build_subdirs(subdir, fname, uplink))

    def build_url_image(self, fname, subdir=None, uplink=False):
        """
        builds a url from an image

        @param: fname  -- The file name for which we need to build the path
        @param: subdir -- The subdirectory name to use
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
        if self.usecms:
            if self.target_uri not in subdirs:
                subdirs = [self.target_uri] + subdirs
        else:
            if uplink:
                subdirs = ['..']*3 + subdirs
        nname = "/".join(subdirs + [fname])
        if win():
            nname = nname.replace('\\', "/")
        return nname

    def build_url_fname_html(self, fname, subdir=None, uplink=False):
        """
        builds a url filename from html

        @param: fname  -- The file name to create
        @param: subdir -- The subdirectory name to use
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        return self.build_url_fname(fname, subdir, uplink) + self.ext

    def build_link(self, prop, handle, obj_class):
        """
        Build a link to an item.

        @param: prop      -- Property
        @param: handle    -- The handle for which we need to build a link
        @param: obj_class -- The class of the related object.
        """
        if prop == "gramps_id":
            if obj_class in self.database.get_table_names():
                obj = self.database.get_table_metadata(obj_class)[
                                                       "gramps_id_func"](handle)
                if obj:
                    handle = obj.handle
                else:
                    raise AttributeError("gramps_id '%s' not found in '%s'" %
                                         handle, obj_class)
            else:
                raise AttributeError("invalid gramps_id lookup "
                                     "in table name '%s'" % obj_class)
        uplink = self.link_prefix_up
        # handle, ppl
        if obj_class == "Person":
            if self.person_in_webreport(handle):
                return self.build_url_fname(handle, "ppl", uplink) + self.ext
            else:
                return None
        elif obj_class == "Source":
            subdir = "src"
        elif obj_class == "Place":
            subdir = "plc"
        elif obj_class == "Event":
            subdir = "evt"
        elif obj_class == "Media":
            subdir = "img"
        elif obj_class == "Repository":
            subdir = "repo"
        elif obj_class == "Family":
            subdir = "fam"
        else:
            print("NarrativeWeb ignoring link type '%s'" % obj_class)
            return None
        return self.build_url_fname(handle, subdir, uplink) + self.ext

    def build_url_fname(self, fname, subdir=None, uplink=False):
        """
        Create part of the URL given the filename and optionally the
        subdirectory. If the subdirectory is given, then two extra levels of
        subdirectory are inserted between 'subdir' and the filename.
        The reason is to prevent directories with too many entries.

        @param: fname  -- The file name to create
        @param: subdir -- The subdirectory name to use
        @param: uplink -- if True, then "../../../" is inserted in front of the
                          result.

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        Imagine we run gramps on Windows (heaven forbits), we don't want to
        see backslashes in the URL.
        """
        if not fname:
            return ""

        if win():
            fname = fname.replace('\\', "/")
        fname = fname.replace(self.target_uri + "/", "")
        if self.usecms:
            subdirs = self.build_subdirs(subdir, fname, False)
        else:
            subdirs = self.build_subdirs(subdir, fname, uplink)
        return "/".join(subdirs + [fname])

    def create_file(self, fname, subdir=None, ext=None):
        """
        will create filename given

        @param: fname  -- File name to be created
        @param: subdir -- A subdir to be added to filename
        @param: ext    -- An extension to be added to filename
        """
        if ext is None:
            ext = self.ext
        if self.usecms and subdir is None:
            self.cur_fname = os.path.join(self.target_uri, fname) + ext
        else:
            if subdir:
                subdir = self.build_path(subdir, fname)
                self.cur_fname = os.path.join(subdir, fname) + ext
            else:
                self.cur_fname = fname + ext
        if self.archive:
            string_io = BytesIO()
            output_file = TextIOWrapper(string_io, encoding=self.encoding,
                               errors='xmlcharrefreplace')
        else:
            string_io = None
            if subdir:
                subdir = os.path.join(self.html_dir, subdir)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
            fname = os.path.join(self.html_dir, self.cur_fname)
            output_file = open(fname, 'w', encoding=self.encoding,
                      errors='xmlcharrefreplace')
        return (output_file, string_io)

    def close_file(self, output_file, string_io, date):
        """
        will close any file passed to it

        @param: output_file -- The output file to flush
        @param: string_io   -- The string IO used when we are in archive mode
        @param: date        -- The last modification date for this object
                               If we have "zero", we use the current time.
                               This is related to bug 8950 and very useful
                               when we use rsync.
        """
        if self.archive:
            output_file.flush()
            tarinfo = tarfile.TarInfo(self.cur_fname)
            tarinfo.size = len(string_io.getvalue())
            tarinfo.mtime = date if date is not None else time.time()
            if not win():
                tarinfo.uid = os.getuid()
                tarinfo.gid = os.getgid()
            string_io.seek(0)
            self.archive.addfile(tarinfo, string_io)
            output_file.close()
        else:
            output_file.close()
            if date > 0:
                os.utime(output_file.name, (date, date))

    def prepare_copy_media(self, photo):
        """
        prepares a media object to copy

        @param: photo -- The photo for which we need a real path
                         and a thumbnail path
        """
        handle = photo.get_handle()
        ext = os.path.splitext(photo.get_path())[1]
        real_path = os.path.join(self.build_path('images', handle),
                                 handle + ext)
        thumb_path = os.path.join(self.build_path('thumb', handle),
                                  handle + '.png')
        return real_path, thumb_path

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present and if the target is not an archive,
        then the destination directory will be created.

        @param: from_fname -- The path of the file to copy.
        @param: to_fname   -- Will be just a filename, without directory path.
        @param: to_dir     -- Is the relative path name in the destination root.
                              It will be prepended before 'to_fname'.
        """
        if self.usecms:
            to_dir = "/" + self.target_uri + "/" + to_dir
        # LOG.debug("copying '%s' to '%s/%s'" % (from_fname, to_dir, to_fname))
        mtime = os.stat(from_fname).st_mtime
        if self.archive:
            def set_mtime(tarinfo):
                """
                For each file, we set the last modification time.

                We could also set uid, gid, uname, gname and mode
                #tarinfo.uid = os.getuid()
                #tarinfo.mode = 0660
                #tarinfo.uname = tarinfo.gname = "www-data"
                """
                tarinfo.mtime = mtime
                return tarinfo

            dest = os.path.join(to_dir, to_fname)
            self.archive.add(from_fname, dest, filter=set_mtime)
        else:
            dest = os.path.join(self.html_dir, to_dir, to_fname)

            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

            if from_fname != dest:
                try:
                    shutil.copyfile(from_fname, dest)
                    os.utime(dest, (mtime, mtime))
                except:
                    print("Copying error: %s" % sys.exc_info()[1])
                    print("Continuing...")
            elif self.warn_dir:
                self.user.warn(
                    _("Possible destination error") + "\n" +
                    _("You appear to have set your target directory "
                      "to a directory used for data storage. This "
                      "could create problems with file management. "
                      "It is recommended that you consider using "
                      "a different directory to store your generated "
                      "web pages."))
                self.warn_dir = False

    def person_in_webreport(self, person_handle):
        """
        Return the handle if we created a page for this person.

        @param: person_handle -- The person we are looking for
        """
        return person_handle in self.obj_dict[Person]

#################################################
#
#    Creates the NarrativeWeb Report Menu Options
#
#################################################
class NavWebOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        """
        @param: name  -- The name of the report
        @param: dbase -- The Gramps database instance
        """
        self.__db = dbase
        self.__archive = None
        self.__target = None
        self.__target_uri = None
        self.__pid = None
        self.__filter = None
        self.__graph = None
        self.__graphgens = None
        self.__living = None
        self.__yearsafterdeath = None
        self.__usecms = None
        self.__cms_uri = None
        self.__usecal = None
        self.__calendar_uri = None
        self.__create_thumbs_only = None
        self.__mapservice = None
        self.__maxinitialimageheight = None
        self.__maxinitialimagewidth = None
        self.__citationreferents = None
        self.__incdownload = None
        self.__placemappages = None
        self.__familymappages = None
        self.__googleopts = None
        self.__ancestortree = None
        self.__css = None
        self.__dl_descr1 = None
        self.__dl_descr2 = None
        self.__down_fname2 = None
        self.__gallery = None
        self.__unused = None
        self.__down_fname1 = None
        self.__navigation = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web site.

        @param: menu -- The menu for which we add options
        """
        self.__add_report_options(menu)
        self.__add_page_generation_options(menu)
        self.__add_privacy_options(menu)
        self.__add_download_options(menu)
        self.__add_advanced_options(menu)
        self.__add_place_map_options(menu)
        self.__add_others_options(menu)


    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")
        addopt = partial(menu.add_option, category_name)

        self.__archive = BooleanOption(_('Store web pages in .tar.gz archive'),
                                       False)
        self.__archive.set_help(_('Whether to store the web pages in an '
                                  'archive file'))
        addopt("archive", self.__archive)
        self.__archive.connect('value-changed', self.__archive_changed)

        dbname = self.__db.get_dbname()
        default_dir = dbname + "_" + "NAVWEB"
        self.__target = DestinationOption(_("Destination"),
                            os.path.join(config.get('paths.website-directory'),
                                         default_dir))
        self.__target.set_help(_("The destination directory for the web "
                                 "files"))
        addopt("target", self.__target)

        self.__archive_changed()

        title = StringOption(_("Web site title"), _('My Family Tree'))
        title.set_help(_("The title of the web site"))
        addopt("title", title)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on web site"))
        addopt("filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        addopt("pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_name_format_option(menu, category_name)

        ext = EnumeratedListOption(_("File extension"), ".html")
        for etype in _WEB_EXT:
            ext.add_item(etype, etype)
        ext.set_help(_("The extension to be used for the web files"))
        addopt("ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0)
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help(_("The copyright to be used for the web files"))
        addopt("cright", cright)

        self.__css = EnumeratedListOption(_('StyleSheet'), CSS["default"]["id"])
        for (fname, gid) in sorted([(CSS[key]["translation"], CSS[key]["id"])
                                  for key in list(CSS.keys())]):
            if CSS[gid]["user"]:
                self.__css.add_item(CSS[gid]["id"], CSS[gid]["translation"])
        self.__css.set_help(_('The stylesheet to be used for the web pages'))
        addopt("css", self.__css)
        self.__css.connect("value-changed", self.__stylesheet_changed)

        _nav_opts = [
            (_("Horizontal -- Default"), "Horizontal"),
            (_("Vertical   -- Left Side"), "Vertical"),
            (_("Fade       -- WebKit Browsers Only"), "Fade"),
            (_("Drop-Down  -- WebKit Browsers Only"), "dropdown")
        ]
        self.__navigation = EnumeratedListOption(_("Navigation Menu Layout"),
                                                 _nav_opts[0][1])
        for layout in _nav_opts:
            self.__navigation.add_item(layout[1], layout[0])
        self.__navigation.set_help(_("Choose which layout "
                                     "for the Navigation Menus."))
        addopt("navigation", self.__navigation)

        self.__stylesheet_changed()

        _cit_opts = [
            (_("Normal Outline Style"), "Outline"),
            (_("Drop-Down  -- WebKit Browsers Only"), "DropDown")
        ]
        self.__citationreferents = EnumeratedListOption(
                    _("Citation Referents Layout"), _cit_opts[0][1])
        for layout in _cit_opts:
            self.__citationreferents.add_item(layout[1], layout[0])
        self.__citationreferents.set_help(
                    _("Determine the default layout for the "
                      "Source Page's Citation Referents section"))
        addopt("citationreferents", self.__citationreferents)

        self.__ancestortree = BooleanOption(_("Include ancestor's tree"), True)
        self.__ancestortree.set_help(_('Whether to include an ancestor '
                                       'graph on each individual page'))
        addopt("ancestortree", self.__ancestortree)
        self.__ancestortree.connect('value-changed', self.__graph_changed)

        self.__graphgens = NumberOption(_("Graph generations"), 4, 2, 5)
        self.__graphgens.set_help(_("The number of generations to include in "
                                     "the ancestor graph"))
        addopt("graphgens", self.__graphgens)

        self.__graph_changed()

    def __add_page_generation_options(self, menu):
        """
        Options on the "Page Generation" tab.
        """
        category_name = _("Page Generation")
        addopt = partial(menu.add_option, category_name)

        homenote = NoteOption(_('Home page note'))
        homenote.set_help(_("A note to be used on the home page"))
        addopt("homenote", homenote)

        homeimg = MediaOption(_('Home page image'))
        homeimg.set_help(_("An image to be used on the home page"))
        addopt("homeimg", homeimg)

        intronote = NoteOption(_('Introduction note'))
        intronote.set_help(_("A note to be used as the introduction"))
        addopt("intronote", intronote)

        introimg = MediaOption(_('Introduction image'))
        introimg.set_help(_("An image to be used as the introduction"))
        addopt("introimg", introimg)

        contactnote = NoteOption(_("Publisher contact note"))
        contactnote.set_help(_("A note to be used as the publisher contact."
                                "\nIf no publisher information is given,"
                                "\nno contact page will be created")
                              )
        addopt("contactnote", contactnote)

        contactimg = MediaOption(_("Publisher contact image"))
        contactimg.set_help(_("An image to be used as the publisher contact."
                               "\nIf no publisher information is given,"
                               "\nno contact page will be created")
                             )
        addopt("contactimg", contactimg)

        headernote = NoteOption(_('HTML user header'))
        headernote.set_help(_("A note to be used as the page header"))
        addopt("headernote", headernote)

        footernote = NoteOption(_('HTML user footer'))
        footernote.set_help(_("A note to be used as the page footer"))
        addopt("footernote", footernote)

        self.__gallery = BooleanOption(_("Include images and media objects"),
                                       True)
        self.__gallery.set_help(_('Whether to include '
                                  'a gallery of media objects'))
        addopt("gallery", self.__gallery)
        self.__gallery.connect('value-changed', self.__gallery_changed)

        self.__unused = BooleanOption(
                                   _("Include unused images and media objects"),
                                   True)
        self.__unused.set_help(_('Whether to include unused or unreferenced'
                               ' media objects'))
        addopt("unused", self.__unused)

        self.__create_thumbs_only = BooleanOption(
                    _("Create and only use thumbnail- sized images"), False)
        self.__create_thumbs_only.set_help(
                    _("This option allows you to create only thumbnail images "
                      "instead of the full-sized images on the Media Page. "
                      "This will allow you to have a much "
                      "smaller total upload size to your web hosting site."))
        addopt("create_thumbs_only", self.__create_thumbs_only)
        self.__create_thumbs_only.connect("value-changed",
                                          self.__gallery_changed)

        self.__maxinitialimagewidth = NumberOption(
                                               _("Max width of initial image"),
                                               _DEFAULT_MAX_IMG_WIDTH, 0, 2000)
        self.__maxinitialimagewidth.set_help(
              _("This allows you to set the maximum width "
                "of the image shown on the media page. Set to 0 for no limit."))
        addopt("maxinitialimagewidth", self.__maxinitialimagewidth)

        self.__maxinitialimageheight = NumberOption(
                                               _("Max height of initial image"),
                                               _DEFAULT_MAX_IMG_HEIGHT, 0, 2000)
        self.__maxinitialimageheight.set_help(
              _("This allows you to set the maximum height "
                "of the image shown on the media page. Set to 0 for no limit."))
        addopt("maxinitialimageheight", self.__maxinitialimageheight)

        self.__gallery_changed()

        nogid = BooleanOption(_('Suppress Gramps ID'), False)
        nogid.set_help(_('Whether to include the Gramps ID of objects'))
        addopt("nogid", nogid)

    def __add_privacy_options(self, menu):
        """
        Options on the "Privacy" tab.
        """
        category_name = _("Privacy")

        stdoptions.add_living_people_option(menu, category_name)
        stdoptions.add_private_data_option(menu, category_name, default=False)

        addopt = partial(menu.add_option, category_name)

    def __add_download_options(self, menu):
        """
        Options for the download tab ...
        """
        category_name = _("Download")
        addopt = partial(menu.add_option, category_name)

        self.__incdownload = BooleanOption(_("Include download page"), False)
        self.__incdownload.set_help(
                             _('Whether to include a database download option'))
        addopt("incdownload", self.__incdownload)
        self.__incdownload.connect('value-changed', self.__download_changed)

        self.__down_fname1 = DestinationOption(_("Download Filename"),
            os.path.join(config.get('paths.website-directory'), ""))
        self.__down_fname1.set_help(
                             _("File to be used for downloading of database"))
        addopt("down_fname1", self.__down_fname1)

        self.__dl_descr1 = StringOption(_("Description for download"),
                                        _('Smith Family Tree'))
        self.__dl_descr1.set_help(_('Give a description for this file.'))
        addopt("dl_descr1", self.__dl_descr1)

        self.__down_fname2 = DestinationOption(_("Download Filename"),
            os.path.join(config.get('paths.website-directory'), ""))
        self.__down_fname2.set_help(
                             _("File to be used for downloading of database"))
        addopt("down_fname2", self.__down_fname2)

        self.__dl_descr2 = StringOption(_("Description for download"),
                                        _('Johnson Family Tree'))
        self.__dl_descr2.set_help(_('Give a description for this file.'))
        addopt("dl_descr2", self.__dl_descr2)

        self.__download_changed()

    def __add_advanced_options(self, menu):
        """
        Options on the "Advanced" tab.
        """
        category_name = _("Advanced Options")
        addopt = partial(menu.add_option, category_name)

        encoding = EnumeratedListOption(_('Character set encoding'),
                                        _CHARACTER_SETS[0][1])
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help(_("The encoding to be used for the web files"))
        addopt("encoding", encoding)

        linkhome = BooleanOption(
                        _('Include link to active person on every page'), False)
        linkhome.set_help(
              _('Include a link to the active person (if they have a webpage)'))
        addopt("linkhome", linkhome)

        showbirth = BooleanOption(
                 _("Include a column for birth dates on the index pages"), True)
        showbirth.set_help(_('Whether to include a birth column'))
        addopt("showbirth", showbirth)

        showdeath = BooleanOption(
                _("Include a column for death dates on the index pages"), False)
        showdeath.set_help(_('Whether to include a death column'))
        addopt("showdeath", showdeath)

        showpartner = BooleanOption(_("Include a column for partners on the "
                                      "index pages"), False)
        showpartner.set_help(_('Whether to include a partners column'))
        menu.add_option(category_name, 'showpartner', showpartner)

        showparents = BooleanOption(_("Include a column for parents on the "
                                      "index pages"), False)
        showparents.set_help(_('Whether to include a parents column'))
        addopt("showparents", showparents)

        showallsiblings = BooleanOption(
                            _("Include half and/ or "
                              "step-siblings on the individual pages"), False)
        showallsiblings.set_help(_("Whether to include half and/ or "
                              "step-siblings with the parents and siblings"))
        addopt('showhalfsiblings', showallsiblings)

        birthorder = BooleanOption(_('Sort all children in birth order'), False)
        birthorder.set_help(
             _('Whether to display children in birth order or in entry order?'))
        addopt("birthorder", birthorder)

        inc_families = BooleanOption(_("Include family pages"), False)
        inc_families.set_help(_("Whether or not to include family pages."))
        addopt("inc_families", inc_families)

        inc_events = BooleanOption(_('Include event pages'), False)
        inc_events.set_help(
                      _('Add a complete events list and relevant pages or not'))
        addopt("inc_events", inc_events)

        inc_repository = BooleanOption(_('Include repository pages'), False)
        inc_repository.set_help(
                      _('Whether or not to include the Repository Pages.'))
        addopt("inc_repository", inc_repository)

        inc_gendex = BooleanOption(
                      _('Include GENDEX file (/gendex.txt)'), False)
        inc_gendex.set_help(_('Whether to include a GENDEX file or not'))
        addopt("inc_gendex", inc_gendex)

        inc_addressbook = BooleanOption(_("Include address book pages"), False)
        inc_addressbook.set_help(_("Whether or not to add Address Book pages,"
                                   "which can include e-mail and website "
                                   "addresses and personal address/ residence "
                                   "events."))
        addopt("inc_addressbook", inc_addressbook)

    def __add_place_map_options(self, menu):
        """
        options for the Place Map tab.
        """
        category_name = _("Place Map Options")
        addopt = partial(menu.add_option, category_name)

        mapopts = [
            [_("Google"), "Google"],
            [_("OpenStreetMap"), "OpenStreetMap"]]
        self.__mapservice = EnumeratedListOption(_("Map Service"),
                                                 mapopts[0][1])
        for trans, opt in mapopts:
            self.__mapservice.add_item(opt, trans)
        self.__mapservice.set_help(_("Choose your choice of map service for "
                                     "creating the Place Map Pages."))
        self.__mapservice.connect("value-changed", self.__placemap_options)
        addopt("mapservice", self.__mapservice)

        self.__placemappages = BooleanOption(
                                   _("Include Place map on Place Pages"), False)
        self.__placemappages.set_help(
                         _("Whether to include a place map on the Place Pages, "
                           "where Latitude/ Longitude are available."))
        self.__placemappages.connect("value-changed", self.__placemap_options)
        addopt("placemappages", self.__placemappages)

        self.__familymappages = BooleanOption(_("Include Family Map Pages with "
                                                "all places shown on the map"),
                                              False)
        self.__familymappages.set_help(
                               _("Whether or not to add an individual page map "
                                 "showing all the places on this page. "
                                 "This will allow you to see how your family "
                                 "traveled around the country."))
        self.__familymappages.connect("value-changed", self.__placemap_options)
        addopt("familymappages", self.__familymappages)

        googleopts = [
            (_("Family Links"), "FamilyLinks"),
            (_("Drop"), "Drop"),
            (_("Markers"), "Markers")]
        self.__googleopts = EnumeratedListOption(_("Google/ FamilyMap Option"),
                                                 googleopts[0][1])
        for trans, opt in googleopts:
            self.__googleopts.add_item(opt, trans)
        self.__googleopts.set_help(_("Select which option that you would like "
            "to have for the Google Maps Family Map pages..."))
        addopt("googleopts", self.__googleopts)

        self.__placemap_options()

    def __add_others_options(self, menu):
        """
        Options for the cms tab, web calendar inclusion, php ...
        """
        category_name = _("Other inclusion (CMS, Web Calendar, Php)")
        addopt = partial(menu.add_option, category_name)

        self.__usecms = BooleanOption(
                           _("Do we include these pages in a cms web ?"), False)
        addopt("usecms", self.__usecms)

        default_dir = "/NAVWEB"
        self.__cms_uri = DestinationOption(_("URI"),
                            os.path.join(config.get('paths.website-cms-uri'),
                                         default_dir))
        self.__cms_uri.set_help(_("Where do you place your web site ?"
                                   " default = /NAVWEB"))
        self.__cms_uri.connect('value-changed', self.__cms_uri_changed)
        addopt("cmsuri", self.__cms_uri)

        self.__cms_uri_changed()

        self.__usecal = BooleanOption(
                           _("Do we include the web calendar ?"), False)
        addopt("usecal", self.__usecal)

        default_calendar = "/WEBCAL"
        self.__calendar_uri = DestinationOption(_("URI"),
                            os.path.join(config.get('paths.website-cal-uri'),
                                         default_calendar))
        self.__calendar_uri.set_help(_("Where do you place your web site ?"
                                   " default = /WEBCAL"))
        self.__calendar_uri.connect('value-changed',
                                    self.__calendar_uri_changed)
        addopt("caluri", self.__calendar_uri)

        self.__calendar_uri_changed()

    def __cms_uri_changed(self):
        """
        Update the change of storage: archive or directory
        """
        self.__target_uri = self.__cms_uri.get_value()

    def __calendar_uri_changed(self):
        """
        Update the change of storage: Where is the web calendar ?

        Possible cases :
        1 - /WEBCAL                  (relative URI to the navweb site)
        2 - http://mysite.org/WEBCAL (URL is on another website)
        3 - //mysite.org/WEBCAL      (PRL depend on the protocol used)
        """
        self.__target_cal_uri = self.__calendar_uri.get_value()

    def __archive_changed(self):
        """
        Update the change of storage: archive or directory
        """
        if self.__archive.get_value() == True:
            self.__target.set_extension(".tar.gz")
            self.__target.set_directory_entry(False)
        else:
            self.__target.set_directory_entry(True)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def __stylesheet_changed(self):
        """
        Handles the changing nature of the stylesheet
        """
        css_opts = self.__css.get_value()
        if CSS[css_opts]["navigation"]:
            self.__navigation.set_available(True)
        else:
            self.__navigation.set_available(False)
            self.__navigation.set_value("Horizontal")

    def __graph_changed(self):
        """
        Handle enabling or disabling the ancestor graph
        """
        self.__graphgens.set_available(self.__ancestortree.get_value())

    def __gallery_changed(self):
        """
        Handles the changing nature of gallery
        """
        _gallery_option = self.__gallery.get_value()
        _create_thumbs_only_option = self.__create_thumbs_only.get_value()

        # images and media objects to be used, make all opti8ons available...
        if _gallery_option:
            self.__create_thumbs_only.set_available(True)
            self.__maxinitialimagewidth.set_available(True)
            self.__maxinitialimageheight.set_available(True)

            # thumbnail-sized images only...
            if _create_thumbs_only_option:
                self.__maxinitialimagewidth.set_available(False)
                self.__maxinitialimageheight.set_available(False)

            # full- sized images and Media Pages will be created...
            else:
                self.__maxinitialimagewidth.set_available(True)
                self.__maxinitialimageheight.set_available(True)

        # no images or media objects are to be used...
        else:
            self.__create_thumbs_only.set_available(False)
            self.__maxinitialimagewidth.set_available(False)
            self.__maxinitialimageheight.set_available(False)

    def __download_changed(self):
        """
        Handles the changing nature of include download page
        """
        if self.__incdownload.get_value():
            self.__down_fname1.set_available(True)
            self.__dl_descr1.set_available(True)
            self.__down_fname2.set_available(True)
            self.__dl_descr2.set_available(True)
        else:
            self.__down_fname1.set_available(False)
            self.__dl_descr1.set_available(False)
            self.__down_fname2.set_available(False)
            self.__dl_descr2.set_available(False)

    def __placemap_options(self):
        """
        Handles the changing nature of the place map Options
        """
        # get values for all Place Map Options tab...
        place_active = self.__placemappages.get_value()
        family_active = self.__familymappages.get_value()
        mapservice_opts = self.__mapservice.get_value()
        #google_opts = self.__googleopts.get_value()

        if place_active or family_active:
            self.__mapservice.set_available(True)
        else:
            self.__mapservice.set_available(False)

        if family_active and mapservice_opts == "Google":
            self.__googleopts.set_available(True)
        else:
            self.__googleopts.set_available(False)

# FIXME. Why do we need our own sorting? Why not use Sort?
def sort_people(dbase, handle_list):
    """
    will sort the database people by surname
    """
    sname_sub = defaultdict(list)
    sortnames = {}

    for person_handle in handle_list:
        person = dbase.get_person_from_handle(person_handle)
        primary_name = person.get_primary_name()

        if primary_name.group_as:
            surname = primary_name.group_as
        else:
            surname = str(dbase.get_name_group_mapping(
                            _nd.primary_surname(primary_name)))

        # Treat people who have no name with those whose name is just
        # 'whitespace'
        if surname is None or surname.isspace():
            surname = ''
        sortnames[person_handle] = _nd.sort_string(primary_name)
        sname_sub[surname].append(person_handle)

    sorted_lists = []
    temp_list = sorted(sname_sub, key=SORT_KEY)

    for name in temp_list:
        slist = sorted(((sortnames[x], x) for x in sname_sub[name]),
                    key=lambda x: SORT_KEY(x[0]))
        entries = [x[1] for x in slist]
        sorted_lists.append((name, entries))

    return sorted_lists

def sort_event_types(dbase, event_types, event_handle_list):
    """
    sort a list of event types and their associated event handles

    @param: dbase -- report database
    @param: event_types -- a dict of event types
    @param: event_handle_list -- all event handles in this database
    """
    event_dict = dict((evt_type, list()) for evt_type in event_types)

    for event_handle in event_handle_list:

        event = dbase.get_event_from_handle(event_handle)
        event_type = str(event.get_type())

        # add (gramps_id, date, handle) from this event
        if event_type in event_dict:
            sort_value = event.get_date_object().get_sort_value()
            event_dict[event_type].append((sort_value, event_handle))

    for tup_list in event_dict.values():
        tup_list.sort()

    # return a list of sorted tuples, one per event
    retval = [(event_type, event_list) for (event_type,
                                            event_list) in event_dict.items()]
    retval.sort(key=lambda item: str(item[0]))

    return retval

# Modified _get_regular_surname from WebCal.py to get prefix, first name,
# and suffix
def _get_short_name(gender, name):
    """ Will get suffix for all people passed through it """

    short_name = name.get_first_name()
    suffix = name.get_suffix()
    if suffix:
        short_name = short_name + ", " + suffix
    return short_name

def __get_person_keyname(dbase, handle):
    """ .... """

    person = dbase.get_person_from_handle(handle)
    return _nd.sort_string(person.get_primary_name())

def __get_place_keyname(dbase, handle):
    """ ... """

    return ReportUtils.place_name(dbase, handle)

# See : http://www.gramps-project.org/bugs/view.php?id = 4423

# Contraction data taken from CLDR 22.1. Only the default variant is considered.
# The languages included below are, by no means, all the langauges that have
# contractions - just a sample of langauges that have been supported

# At the time of writing (Feb 2013), the following langauges have greater that
# 50% coverage of translation of Gramps: bg Bulgarian, ca Catalan, cs Czech, da
# Danish, de German, el Greek, en_GB, es Spanish, fi Finish, fr French, he
# Hebrew, hr Croation, hu Hungarian, it Italian, ja Japanese, lt Lithuanian, nb
# Noregian Bokmål, nn Norwegian Nynorsk, nl Dutch, pl Polish, pt_BR Portuguese
# (Brazil), pt_P Portugeuse (Portugal), ru Russian, sk Slovak, sl Slovenian, sv
# Swedish, vi Vietnamese, zh_CN Chinese.

# Key is the language (or language and country), Value is a list of
# contractions. Each contraction consists of a tuple. First element of the
# tuple is the list of characters, second element is the string to use as the
# index entry.

# The DUCET contractions (e.g. LATIN CAPIAL LETTER L, MIDDLE DOT) are ignored,
# as are the supresscontractions in some locales.

CONTRACTIONS_DICT = {
    # bg Bulgarian validSubLocales="bg_BG" no contractions
    # ca Catalan validSubLocales="ca_AD ca_ES"
    "ca" : [(("l·", "L·"), "L")],
    # Czech, validSubLocales="cs_CZ" Czech_Czech Republic
    "cs" : [(("ch", "cH", "Ch", "CH"), "Ch")],
    # Danish validSubLocales="da_DK" Danish_Denmark
    "da" : [(("aa", "Aa", "AA"), "Å")],
    # de German validSubLocales="de_AT de_BE de_CH de_DE de_LI de_LU" no
    # contractions in standard collation.
    # el Greek validSubLocales="el_CY el_GR" no contractions.
    # es Spanish validSubLocales="es_419 es_AR es_BO es_CL es_CO es_CR es_CU
    # es_DO es_EA es_EC es_ES es_GQ es_GT es_HN es_IC es_MX es_NI es_PA es_PE
    # es_PH es_PR es_PY es_SV es_US es_UY es_VE" no contractions in standard
    # collation.
    # fi Finish validSubLocales="fi_FI" no contractions in default (phonebook)
    # collation.
    # fr French no collation data.
    # he Hebrew validSubLocales="he_IL" no contractions
    # hr Croation validSubLocales="hr_BA hr_HR"
    "hr" : [(("dž", "Dž"), "dž"),
            (("lj", "Lj", 'LJ'), "Ǉ"),
            (("Nj", "NJ", "nj"), "Ǌ")],
    # Hungarian hu_HU for two and three character contractions.
    "hu" : [(("cs", "Cs", "CS"), "CS"),
            (("dzs", "Dzs", "DZS"), "DZS"), # order is important
            (("dz", "Dz", "DZ"), "DZ"),
            (("gy", "Gy", "GY"), "GY"),
            (("ly", "Ly", "LY"), "LY"),
            (("ny", "Ny", "NY"), "NY"),
            (("sz", "Sz", "SZ"), "SZ"),
            (("ty", "Ty", "TY"), "TY"),
            (("zs", "Zs", "ZS"), "ZS")
           ],
    # it Italian no collation data.
    # ja Japanese unable to process the data as it is too complex.
    # lt Lithuanian no contractions.
    # Norwegian Bokmål
    "nb" : [(("aa", "Aa", "AA"), "Å")],
    # nn Norwegian Nynorsk validSubLocales="nn_NO"
    "nn" : [(("aa", "Aa", "AA"), "Å")],
    # nl Dutch no collation data.
    # pl Polish validSubLocales="pl_PL" no contractions
    # pt Portuguese no collation data.
    # ru Russian validSubLocales="ru_BY ru_KG ru_KZ ru_MD ru_RU ru_UA" no
    # contractions
    # Slovak,  validSubLocales="sk_SK" Slovak_Slovakia
    # having DZ in Slovak as a contraction was rejected in
    # http://unicode.org/cldr/trac/ticket/2968
    "sk" : [(("ch", "cH", "Ch", "CH"), "Ch")],
    # sl Slovenian validSubLocales="sl_SI" no contractions
    # sv Swedish validSubLocales="sv_AX sv_FI sv_SE" default collation is
    # "reformed" no contractions.
    # vi Vietnamese validSubLocales="vi_VN" no contractions.
    # zh Chinese validSubLocales="zh_Hans zh_Hans_CN zh_Hans_SG" no contractions
    # in Latin characters the others are too complex.
                    }

    # The comment below from the glibc locale sv_SE in
    # localedata/locales/sv_SE :
    #
    # % The letter w is normally not present in the Swedish alphabet. It
    # % exists in some names in Swedish and foreign words, but is accounted
    # % for as a variant of 'v'.  Words and names with 'w' are in Swedish
    # % ordered alphabetically among the words and names with 'v'. If two
    # % words or names are only to be distinguished by 'v' or % 'w', 'v' is
    # % placed before 'w'.
    #
    # See : http://www.gramps-project.org/bugs/view.php?id = 2933
    #

# HOWEVER: the characters V and W in Swedish are not considered as a special
# case for several reasons. (1) The default collation for Swedish (called the
# 'reformed' collation type) regards the difference between 'v' and 'w' as a
# primary difference. (2) 'v' and 'w' in the 'standard' (non-default) collation
# type are not a contraction, just a case where the difference is secondary
# rather than primary. (3) There are plenty of other languages where a
# difference that is primary in other languages is secondary, and those are not
# specially handled.

def first_letter(string):
    """
    Receives a string and returns the first letter
    """
    if string is None or len(string) < 1:
        return ' '

    norm_unicode = normalize('NFKC', str(string))
    contractions = CONTRACTIONS_DICT.get(COLLATE_LANG)
    if contractions == None:
        contractions = CONTRACTIONS_DICT.get(COLLATE_LANG.split("_")[0])

    if contractions is not None:
        for contraction in contractions:
            count = len(contraction[0][0])
            if len(norm_unicode) >= count and \
               norm_unicode[:count] in contraction[0]:
                return contraction[1]

    # no special case
    return norm_unicode[0].upper()

try:
    import PyICU
    PRIM_COLL = PyICU.Collator.createInstance(PyICU.Locale(COLLATE_LANG))
    PRIM_COLL.setStrength(PRIM_COLL.PRIMARY)

    def primary_difference(prev_key, new_key):
        """
        Try to use the PyICU collation.
        """

        return PRIM_COLL.compare(prev_key, new_key) != 0

except:
    def primary_difference(prev_key, new_key):
        """
        The PyICU collation is not available.

        Returns true if there is a primary difference between the two parameters
        See http://www.gramps-project.org/bugs/view.php?id=2933#c9317 if
        letter[i]+'a' < letter[i+1]+'b' and letter[i+1]+'a' < letter[i]+'b' is
        true then the letters should be grouped together

        The test characters here must not be any that are used in contractions.
        """

        return SORT_KEY(prev_key + "e") >= SORT_KEY(new_key + "f") or\
            SORT_KEY(new_key + "e") >= SORT_KEY(prev_key + "f")

def get_first_letters(dbase, handle_list, key):
    """
    get the first letters of the handle_list

    @param: handle_list -- One of a handle list for either person or
                           place handles or an evt types list
    @param: key         -- Either a person, place, or event type

    The first letter (or letters if there is a contraction) are extracted from
    all the objects in the handle list. There may be duplicates, and there may
    be letters where there is only a secondary or tertiary difference, not a
    primary difference. The list is sorted in collation order. For each group
    with secondary or tertiary differences, the first in collation sequence is
    retained. For example, assume the default collation sequence (DUCET) and
    names Ånström and Apple. These will sort in the order shown. Å and A have a
    secondary difference. If the first letter from these names was chosen then
    the inex entry would be Å. This is not desirable. Instead, the initial
    letters are extracted (Å and A). These are sorted, which gives A and Å. Then
    the first of these is used for the index entry.
    """
    index_list = []

    for handle in handle_list:
        if key == _KEYPERSON:
            keyname = __get_person_keyname(dbase, handle)

        elif key == _KEYPLACE:
            keyname = __get_place_keyname(dbase, handle)

        else:
            keyname = handle
        ltr = first_letter(keyname)

        index_list.append(ltr)

    # Now remove letters where there is not a primary difference
    index_list.sort(key=SORT_KEY)
    first = True
    prev_index = None
    for key in index_list[:]:   #iterate over a slice copy of the list
        if first or primary_difference(prev_index, key):
            first = False
            prev_index = key
        else:
            index_list.remove(key)

    # return menu set letters for alphabet_navigation
    return index_list

def get_index_letter(letter, index_list):
    """
    This finds the letter in the index_list that has no primary difference from
    the letter provided. See the discussion in get_first_letters above.
    Continuing the example, if letter is Å and index_list is A, then this would
    return A.
    """
    for index in index_list:
        if not primary_difference(letter, index):
            return index

    LOG.warning("Initial letter '%s' not found in alphabetic navigation list",
                letter)
    LOG.debug("filtered sorted index list %s", index_list)
    return letter

def alphabet_navigation(index_list):
    """
    Will create the alphabet navigation bar for classes IndividualListPage,
    SurnameListPage, PlaceListPage, and EventList

    @param: index_list -- a dictionary of either letters or words
    """
    sorted_set = defaultdict(int)

    for menu_item in index_list:
        sorted_set[menu_item] += 1

    # remove the number of each occurance of each letter
    sorted_alpha_index = sorted(sorted_set, key=SORT_KEY)

    # if no letters, return None to its callers
    if not sorted_alpha_index:
        return None

    num_ltrs = len(sorted_alpha_index)
    num_of_cols = 26
    num_of_rows = ((num_ltrs // num_of_cols) + 1)

    # begin alphabet navigation division
    with Html("div", id="alphanav") as alphabetnavigation:

        index = 0
        for row in range(num_of_rows):
            unordered = Html("ul")

            cols = 0
            while cols <= num_of_cols and index < num_ltrs:
                menu_item = sorted_alpha_index[index]
                if menu_item == ' ':
                    menu_item = '&nbsp;'
                # adding title to hyperlink menu for screen readers and
                # braille writers
                title_str = _("Alphabet Menu: %s") % menu_item
                hyper = Html("a", menu_item, title=title_str,
                             href="#%s" % menu_item)
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

def add_birthdate(dbase, ppl_handle_list):
    """
    This will sort a list of child handles in birth order

    @param: dbase           -- The database to use
    @param: ppl_handle_list -- the handle for the people
    """
    sortable_individuals = []
    for person_handle in ppl_handle_list:
        birth_date = 0    # dummy value in case none is found
        person = dbase.get_person_from_handle(person_handle)
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = dbase.get_event_from_handle(birth_ref.ref)
                if birth:
                    birth_date = birth.get_date_object().get_sort_value()
        sortable_individuals.append((birth_date, person_handle))

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
