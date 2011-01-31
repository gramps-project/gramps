# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Serge Noiraud
# Copyright (C) 2008  Benny Malengier
# Copyright (C) 2009  Gerald Britton
# Copyright (C) 2009  Helge GRAMPS
# Copyright (C) 2009  Josip
# Copyright (C) 2009  Gary Burton
# Copyright (C) 2009  Nick Hall
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
Geo View
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import os
import sys
import urlparse
import const
import operator
import locale
from gtk.keysyms import Tab as KEY_TAB
import socket

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("GeoGraphy")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import pango
import gobject

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
import Utils
import config
import Errors
from gen.display.name import displayer as _nd
from PlaceUtils import conv_lat_lon
from gui.views.navigationview import NavigationView
from gui.editors import EditPlace
from gui.selectors.selectplace import SelectPlace
import Bookmarks
from Utils import navigation_label


#-------------------------------------------------------------------------
#
# map icons
#
#-------------------------------------------------------------------------
_ICONS = {
    gen.lib.EventType.BIRTH                : 'gramps-geo-birth',
    gen.lib.EventType.DEATH                : 'gramps-geo-death',
    gen.lib.EventType.MARRIAGE             : 'gramps-geo-marriage',
}

#-------------------------------------------------------------------------
#
# regexp for html title Notes ...
#
#-------------------------------------------------------------------------
import re
ZOOMANDPOS = re.compile('zoom=([0-9]*) coord=([0-9\.\-\+]*), ([0-9\.\-\+]*):::')

#-------------------------------------------------------------------------
#
# Web interfaces
#
#-------------------------------------------------------------------------

URL_SEP = '/'

from htmlrenderer import HtmlView

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
#covert to unicode for better hadnling of path in Windows
GEOVIEW_SUBPATH = Utils.get_empty_tempdir('geoview')

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_HTMLHEADER = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="%(lang)s">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>%(title)s</title>
    <meta http-equiv="Content-Script-Type" content="text/javascript">
    %(css)s
'''

_JAVASCRIPT = '''\
<script>
 var gmarkers = []; var min = 0; var zoom = 0; var uzoom = 0; var ucross = 0;
 var pos = 0; var mapstraction;
 var regrep = new RegExp(\"default\",\"g\");
 var current_map; var ulat; var ulon; var default_icon;
 function getArgs(){
  var args = new Object();
  var query = location.search.substring(1);
  var pairs = query.split("&");
  search_array = query.split("&");
  for (var i=0; i < pairs.length; i++){
   var pos = pairs[i].indexOf('=');
   if (pos == -1) continue;
    var argname = pairs[i].substring(0,pos);
    var value = pairs[i].substring(pos+1);
    args[argname] = unescape(value);
  }
  return args;
 }
 var selectedmarkers = 'All';
 // shows or hide markers of a particular category
 function selectmarkers(year) {
  selectedmarkers = year;
  for (var i=0; i<gmarkers.length; i++) {
   val = gmarkers[i].getAttribute("year");
   min = parseInt(year);
   max = min + step;
   if ( selectedmarkers == "All" ) { min = 0; max = 9999; }
   gmarkers[i].hide();
   years = val.split(' ');
   for ( j=0; j < years.length; j++) {
    if ( years[j] >= min ) {
     if ( years[j] < max ) {
      gmarkers[i].show();
     }
    }
   }
  }
 }
 function savezoomandposition(map) {
  var t=setTimeout("savezoomandposition(mapstraction)",1000);
  // shows or hide markers of a particular category
  nzoom = map.getZoom();
  nposition=map.getCenter();
  if ( ( nzoom != zoom ) || ( nposition != pos )) {
   zoom = nzoom;
   pos = nposition;
   document.title = "zoom=" + zoom + " coord=" + pos + ":::";
  }
 }
 function placeclick(i) {
  gmarkers[i].openBubble();
 }
 function swapmap(newmap) {
  current_map=newmap;
  mapstraction.swap(current_map,current_map);
 }
 var crosshairsSize=19;
 var crossh=null;
 var DivId='geo-map';
 function addcrosshair(state,Cross,DivId) {
  if ( state == 0 ) {
    if (crossh != null) mapstraction.removeCrosshair(crossh);
  } else {
    crossh = mapstraction.addCrosshair(Cross,crosshairsSize,DivId);
  };
 }
'''

_HTMLTRAILER = '''\
 setmarkers(mapstraction);
 setcenterandzoom(mapstraction,uzoom,ulat,ulon);
 savezoomandposition(mapstraction);
 mapstraction.enableScrollWheelZoom();
</script>
</body>
</html>
'''

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------
def _get_sign(value):
    """
    return 1 if we have a negative number, 0 in other case
    """
    if value < 0.0:
        return 1
    else:
        return 0

def _get_zoom_lat(value):
    """
    return the zoom value for latitude depending on the distance.
    """
    zoomlat = 1
    for i, distance in enumerate([80.0, 40.0, 20.0, 10.0, 3.0,
                           2.0, 1.0, 0.5, 0.2, 0.1]):
        if value < distance:
            zoomlat = i+1
    return zoomlat + 2

def _get_zoom_long(value):
    """
    return the zoom value for longitude depending on the distance.
    """
    zoomlong = 1
    for i, distance in enumerate([120.0, 60.0, 30.0, 15.0, 7.0,
                           4.0, 2.0, 1.0, .5, .2, .1]):
        if value < distance:
            zoomlong = i+1
    return zoomlong + 2

def _make_callback(func, val):
    """
    return a function
    """
    return lambda x: func(val)

def _escape(text):
    """
    return the text with some characters translated : " &
    """
    text = text.replace('&','\\&')
    text = text.replace('"','\\"')
    return text

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoView(HtmlView):
    """
    The view used to render html pages.
    """
    CONFIGSETTINGS = (
        ('preferences.alternate-provider', False),
        ('preferences.timeperiod-before-range', 10),
        ('preferences.timeperiod-after-range', 10),
        ('preferences.crosshair', False),
        ('preferences.markers', 200),
        ('preferences.coordinates-in-degree', False),
        ('preferences.network-test', False),
        ('preferences.network-timeout', 5),
        ('preferences.network-periodicity', 10),
        ('preferences.network-site', 'www.gramps-project.org'),
        ('preferences.webkit', False),
        )

    def __init__(self, pdata, dbstate, uistate):
        HtmlView.__init__(self, pdata, dbstate, uistate, title=_("GeoView"))
        self.dbstate = dbstate
        self.uistate = uistate
        self.dbstate.connect('database-changed', self._new_database)
        self.widget = None
        self.invalidpath = const.ROOT_DIR.find("(")
        if self.invalidpath != -1:
            _LOG.debug("\n\nInvalid PATH (avoid parenthesis):\n%s\n\n" %
                       const.ROOT_DIR)
        self.displaytype = "person"
        self.active_filter = 'Person Filter Gramplet'

        self.additional_uis.append(self.additional_ui())
        self.resize_occurs = False

    def build_widget(self):
        self.no_network = False
        self.placeslist = []
        self.nbmarkers = 0
        self.nbplaces = 0
        self.without = 0
        self.nbpages = 0
        self.last_index = 0
        self.yearinmarker = []
        self.javascript_ready = False
        self.mustcenter = False
        self.centerlat = self.centerlon = 0.0
        self.setattr = True
        self.latit = self.longt = 0.0
        self.height = self.width = 0.0
        self.zoom = 1
        self.lock_action = None
        self.realzoom = 0
        self.reallatitude = self.reallongitude = 0.0
        self.cal = 0
        if config.get('geoview.lock'):
            self.realzoom = config.get('geoview.zoom')
            self.displaytype = config.get('geoview.map')
            self.reallatitude, self.reallongitude = conv_lat_lon(
                                    config.get('geoview.latitude'),
                                    config.get('geoview.longitude'),
                                    "D.D8")
        if self.displaytype == "places":
            self.active_filter = 'Place Filter Gramplet'
        elif self.displaytype == "event":
            self.active_filter = 'Event Filter Gramplet'
        elif self.displaytype == "family":
            self.active_filter = 'Family Filter Gramplet'
        else:
            self.active_filter = 'Person Filter Gramplet'

        self.minyear = self.maxyear = 1
        self.maxbut = 10
        self.mapview = None
        self.yearint = 0
        self.centered = True
        self.center = True
        self.place_list = []
        self.htmlfile = ""
        self.places = []
        self.sort = []
        self.psort = []
        self.clear = gtk.Button("")
        self.clear.set_tooltip_text(
            _("Clear the entry field in the places selection box.")
            )
        self.savezoom = gtk.Button("")
        self.savezoom.connect("clicked", self._save_zoom)
        self.savezoom.set_tooltip_text(
            _("Save the zoom and coordinates between places "
              "map, person map, family map and event map.")
            )
        self.provider = gtk.Button("")
        self.provider.connect("clicked", self._change_provider)
        self.provider.set_tooltip_text(
            _("Select the maps provider. You can choose "
              "between OpenStreetMap and Google maps.")
            )
        self.buttons = gtk.ListStore(gobject.TYPE_STRING, # The year
                                  )
        self.plist = gtk.ListStore(gobject.TYPE_STRING, # The name
                                   gobject.TYPE_INT,    # the marker index
                                   gobject.TYPE_INT     # the marker page
                                  )
        # I suppress sort in the combobox for performances.
        # I tried to load a database with more than 35000 places.
        # with the sort function, its takes approximatively 20 minutes
        # to see the combobox and the map.
        # Without the sort function, it takes approximatively 4 minutes.
        #self.plist.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.without_coord_file = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.last_year = None
        self.last_selected_year = 0
        self.header_size = 0
        self.years = gtk.HBox()
        self.ylabel = gtk.Label("")
        self.ylabel.set_alignment(1.0, 0.5)
        cell = gtk.CellRendererText()
        self.yearsbox = gtk.ComboBox(self.buttons) # pylint: disable-msg=W0201
        self.yearsbox.pack_start(cell)
        self.yearsbox.add_attribute(self.yearsbox.get_cells()[0], 'text', 0)
        self.yearsbox.connect('changed', self._ask_year_selection)
        self.yearsbox.set_tooltip_text(
            _("Select the period for which you want to see the places.")
            )
        self.years.pack_start(self.ylabel, True, True, padding=2)
        self.years.pack_start(self.yearsbox, True, True, padding=2)
        self.pages_selection = gtk.HBox()
        self.pages = []
        self.last_page = 1
        bef = gtk.Button("<<")
        bef.set_tooltip_text(_("Prior page."))
        self.pages.append(bef)
        cur = gtk.Button("1")
        cur.set_tooltip_text(_("The current page/the last page."))
        self.pages.append(cur)
        aft = gtk.Button(">>")
        aft.set_tooltip_text(_("Next page."))
        self.pages.append(aft)
        for page in self.pages:
            page.connect("clicked", self._ask_new_page)
            self.pages_selection.pack_start(page, False, False, padding=2)
        self.nocoord = gtk.Button("Unref") # don't translate
        self.nocoord.connect("clicked", self._show_places_without_coord)
        self.nocoord.set_tooltip_text(
            _("The number of places which have no coordinates."))
        self.without_coord_file = os.path.join(GEOVIEW_SUBPATH,
                                               "without_coord.html")
        self.endinit = False
        self.generic_filter = None
        self.signal_map = {'place-add': self._place_changed,
                           'place-update' : self._place_changed}
        self.context_id = 0
        self.active = False
        self.already_testing = False
        self.alt_provider = self._config.get('preferences.alternate-provider')
        self.usedmap = "googlev3" if self.alt_provider else "openlayers"
        fpath = os.path.join(const.WEBSTUFF_DIR, 'images', 'crosshairs.png')
        self.crosspath = urlparse.urlunsplit(
            ('file', '', URL_SEP.join(fpath.split(os.sep)), '', '')
            )
        self.side = None
        self.bottom = None
        self.sidebar.remove_gramplet('Event Filter Gramplet')
        self.sidebar.add_gramplet('Place Filter Gramplet')
        return HtmlView.build_widget(self)

    def can_configure(self):
        """
        We have a configuration window.
        """
        return True

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _('Geography')

    def _get_configure_page_funcs(self):
        """
        The function which is used to create the configuration window.
        """
        return [self.map_options, self.geoview_options, self.net_options]

    def config_connect(self):
        """
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect("preferences.crosshair",
                          self.config_crosshair)
        self._config.connect("preferences.network-test",
                          self.config_network_test)

    def config_update_int(self, obj, constant):
        """
        Try to read an int.
        """
        try:
            self._config.set(constant, int(obj.get_text()))
        except:  # pylint: disable-msg=W0704
            #pass # pylint: disable-msg=W0702
            print "WARNING: ignoring invalid value for '%s'" % constant

    def config_update(self, obj, constant):
        # pylint: disable-msg=W0613
        """
        Some preferences changed in the configuration window.
        """
        self._change_map(self.usedmap)
        self._set_provider_icon()
        self._ask_year_selection(self.last_year)

    def config_crosshair(self, client, cnxn_id, entry, data):
        # pylint: disable-msg=W0613
        """
        Do we have a crosshair ?
        """
        if self.javascript_ready:
            _LOG.debug("crosshair : %d" %
                self._config.get("preferences.crosshair")
                )
            self.renderer.execute_script(
                "javascript:addcrosshair('%d','%s','geo-map')" %
                    (self._config.get("preferences.crosshair"),
                self.crosspath)
                )
            self._size_request_for_map(self.box, None)
        pass

    def geoview_options(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        for the time period options.
        """
        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        configdialog.add_text(table, 
                _("You can adjust the time period "
                  "with the two following values."),
                1)
        configdialog.add_pos_int_entry(table, 
                _('The number of years before the first event date'),
                2, 'preferences.timeperiod-before-range',
                self.config_update_int)
        configdialog.add_pos_int_entry(table, 
                _('The number of years after the last event date'),
                3, 'preferences.timeperiod-after-range',
                self.config_update_int)
        return _('Time period adjustment'), table

    def map_options(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        for the map options.
        """
        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        configdialog.add_checkbox(table,
                _('Crosshair on the map.'),
                1, 'preferences.crosshair')
        configdialog.add_checkbox(table,
                _('Show the coordinates in the statusbar either in degrees\n'
                  'or in internal Gramps format ( D.D8 )'),
                2, 'preferences.coordinates-in-degree')
        configdialog.add_pos_int_entry(table, 
                _('The maximum number of markers per page. '
                  'If the time to load one page is too long, reduce this value'),
                3, 'preferences.markers',
                self.config_update_int)
        if self.get_toolkit() == 3 :
            # We have mozilla ( gecko ) and webkit toolkits.
            # We propose to the user the choice between these toolkits.
            # useful when webkit crash and not gecko.
            # We need to restart Gramps.
            # In case of crash with a browser, we can change the toolkit in 
            # Geography_geoview.ini : 
            #      webkit=False => gtkmozembed (gecko)
            #      webkit=True  => webkit
            configdialog.add_checkbox(table,
                _('When selected, we use webkit else we use mozilla\n'
                  'We need to restart Gramps.'),
                4, 'preferences.webkit')
        return _('The map'), table

    def config_network_test(self, client, cnxn_id, entry, data):
        # pylint: disable-msg=W0613
        """
        Do we need to test the network ?
        """
        if self._config.get('preferences.network-test'):
            self._test_network()

    def net_options(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        for the network options.
        """
        table = gtk.Table(1, 1)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        configdialog.add_checkbox(table,
                _('Test the network '),
                1, 'preferences.network-test')
        configdialog.add_pos_int_entry(table, 
                _('Time out for the network connection test'),
                2, 'preferences.network-timeout',
                self.config_update_int)
        configdialog.add_pos_int_entry(table, 
                _('Time in seconds between two network tests.\n'
                  'Must be greater or equal to 10 seconds'),
                3, 'preferences.network-periodicity',
                self.config_update_int)
        configdialog.add_text(table,
                _('Host to test for http. Please, change this '
                  'and select one of your choice.'),
                4)
        configdialog.add_entry(table, '',
                5, 'preferences.network-site')
        return _('The network'), table

    def _place_changed(self, handle_list):
        # pylint: disable-msg=W0613
        """
        One place changed. need to display it.
        """
        self.displaytype = "places"
        self._set_lock_unlock(True)
        self._geo_places()
        
    def top_widget(self):
        """
        The top widget to use, for GeoView :
         - Places list search
         - Page selection if more than NB_MARKERS_PER_PAGE markers.
         - Place without coordinates if needed
         - Years selection
        """
        self.box1 = gtk.VBox(False, 1) # pylint: disable-msg=W0201
        self.clear.set_alignment(1.0, 0.5)
        self.savezoom.set_alignment(1.0, 0.5)
        cell = gtk.CellRendererText()

        self.placebox = gtk.ComboBoxEntry(self.plist)# pylint: disable-msg=W0201
        self.placebox.pack_start(cell)
        self.placebox.add_attribute(self.placebox.get_cells()[0], 'text', 0)
        self.placebox.set_tooltip_text(
            _("Select the place for which you want to see the info bubble."))

        completion = gtk.EntryCompletion()
        completion.set_model(self.plist)
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_match_func(self._match_string)

        self.placebox.child.connect('changed', self._entry_selected_place)
        self.placebox.child.connect('key-press-event', self._entry_key_event)
        self.clear.connect('clicked', self._erase_placebox_selection)
        self.placebox.child.set_completion(completion)

        box = gtk.HBox()
        box.pack_start(self.clear, False, False, padding=2)
        box.pack_start(self.placebox, True, True, padding=2)
        box.pack_start(self.pages_selection, False, False, padding=2)
        box.pack_start(self.nocoord, False, False, padding=2)
        box.pack_start(self.years, False, False, padding=2)
        box.pack_start(self.savezoom, False, False, padding=2)
        box.pack_start(self.provider, False, False, padding=2)
        box.show_all()

        self.heading = gtk.Label('')
        self.heading.set_single_line_mode(True)
        font = pango.FontDescription("monospace")
        font.set_weight(pango.WEIGHT_HEAVY)
        font.set_style(pango.STYLE_NORMAL)
        self.heading.modify_font(font)

        self.box1.pack_start(box, True, True, padding=2)
        self.box1.pack_start(self.heading, True, True, padding=2)
        self.box1.show_all()
        return self.box1

    def _entry_key_event(self, widget, event):
        """
        The user enter characters. If he enter tab, I'll try to complete.
        This is used when the completion doen't start at the beginning
        of the word or sentence.
        i.e : If we have in our place list :
             ...
             "town of london, England"
             "in the town of londonderry"
             "ville de londres"
             ...
        in the entrybox, if you select "londr", then enter tab,
        the selected item will be "ville de londres"
        """
        prefix = widget.get_text().lower()
        count = 0
        found = _("Unknown")
        if event.keyval == KEY_TAB:
            for place in self.plist:
                if prefix in place[0].lower():
                    count += 1
                    found = place[0]
        if count == 1:
            self.placebox.child.set_text(found)

    def _match_string(self, compl, key, fiter): # pylint: disable-msg=W0613
        """
        Used to select places in the combobox.
        """
        model = compl.get_model()
        text = model.get_value(fiter, 0)
        # the key passed to this function is not unicode! bug ?
        # ie : in french, when you enter é, key is equal to e
        ukey = compl.get_entry().get_text()
        if ukey is None or text is None:
            return False
        if ukey.lower() in text.lower():
            return True
        return False

    def _set_years_selection(self, yearbase, step, maxyear):
        """
        Creation of the years list for the years comboBox.
        """
        base = 0
        self.ylabel.set_text("%s : %d %s" % ( _("Time period"),
                                              step, _("years")) )
        self.yearsbox.hide()
        self.yearsbox.freeze_child_notify()
        self.yearsbox.set_model(None)
        self.buttons.clear()
        self.buttons.append([""])
        self.buttons.append([_("All")])
        for but in range(0, self.maxbut + 1): # pylint: disable-msg=W0612
            newyear = yearbase + base
            if newyear <= maxyear:
                self.buttons.append([str(newyear)])
            base += step
        self.yearsbox.set_model(self.buttons)
        self.yearsbox.set_active(1)
        self.yearsbox.show()
        self.yearsbox.thaw_child_notify()

    def _ask_year_selection(self, widget, data=None):
        # pylint: disable-msg=W0613
        """
        Ask to the renderer to apply the selected year
        """
        if widget and widget.get_active():
            self.last_year = widget
            self._set_markers_and_crosshair_on_page(widget)

    def _ask_new_page(self, widget, data=None): # pylint: disable-msg=W0613
        """
        Ask to select a new page when we are in a multi-pages map.
        """
        if widget is None:
            return
        page = widget.get_label()
        (current, maxp ) = self.pages[1].get_label().split('/', 1)
        if ( page == "<<" and int(current) > 1):
            cpage = -1
        elif ( page == ">>" and int(current) < int(maxp)):
            cpage = +1
        else:
            cpage = 0
        cpage += int(current)
        self.last_page = cpage
        ftype = {"places":'P', "event":'E', "family":'F', "person":'I'}.get(
                          self.displaytype, 'X')
        url = os.path.join(GEOVIEW_SUBPATH,
                "GeoV-%c-%05d.html" % (ftype, cpage)
                )
        url = urlparse.urlunsplit(
                ('file', '', URL_SEP.join(url.split(os.sep)), '', '')
                )
        url += '?map=%s' % self.usedmap
        url += '&zoom=%d' % int(self.realzoom)
        url += '&lat=%s' % str(self.reallatitude)
        url += '&lon=%s' % str(self.reallongitude)
        url += '&cross=%s' % int(self._config.get("preferences.crosshair"))
        self._openurl(url)
        self._create_pages_selection(cpage, int(maxp))
        self._savezoomandposition()
        # Need to wait the page is loaded to show the markers.
        gobject.timeout_add(1500, self._show_selected_places)
        self.placebox.child.set_text("")

    def _show_selected_places(self):
        """
        Here, we synchronize the years combobox with the renderer
        except when we are in the places view.
        """
        if self.displaytype != "places":
            for index, r_year in enumerate(self.buttons):
                if self.last_selected_year == r_year[0]:
                    self.yearsbox.set_active(index)
                    self._call_js_selectmarkers(r_year[0])
            self._size_request_for_map(self.box, None)

    def _show_places_without_coord(self, widget): # pylint: disable-msg=W0613
        """
        Show the page which contains the list of all places without coordinates.
        """
        url = urlparse.urlunsplit(
            ('file', '', URL_SEP.join(self.without_coord_file.split(os.sep)),
             '', '')
            )
        self._openurl(url)

    def _entry_selected_place(self, combobox): # pylint: disable-msg=W0612
        """
        Ask to the renderer to show the info bubble.
        """
        place = combobox.get_text()
        for entry in self.placebox.get_model():
            if entry[0] == place:
                # Is this entry in the current page ?
                if self.last_page == int(entry[2]):
                    # Yes, we don't need to load another page.
                    self._show_place_info_bubble(entry[1])
                    self._show_selected_places()
                else:
                    # No, we need to load the correct page
                    self.last_page = int(entry[2])
                    ftype = {"places":'P',
                             "event":'E',
                             "family":'F',
                             "person":'I'}.get( self.displaytype, 'X')
                    url = os.path.join(GEOVIEW_SUBPATH,
                        "GeoV-%c-%05d.html" % (ftype, entry[2])
                        )
                    url = urlparse.urlunsplit(
                        ('file', '', URL_SEP.join(url.split(os.sep)), '', '')
                        )
                    url += '?map=%s' % self.usedmap
                    url += '&zoom=%d' % int(self.realzoom)
                    url += '&lat=%s' % str(self.reallatitude)
                    url += '&lon=%s' % str(self.reallongitude)
                    url += '&cross=%s' % int(
                        self._config.get("preferences.crosshair")
                        )
                    self._openurl(url)
                    (current, maxp ) = self.pages[1].get_label().split('/', 1)
                    self._create_pages_selection(entry[2], int(maxp))
                    self._savezoomandposition()
                    # Need to wait the page is loaded to show the info bubble.
                    gobject.timeout_add(1500, self._show_place_info_bubble,
                                        entry[1])
                    # Need to wait the page is loaded to show the markers.
                    gobject.timeout_add(1600, self._show_selected_places)
        return
        
    def _show_place_info_bubble(self, marker_index):
        """
        We need to call javascript to show the info bubble.
        """
        if self.javascript_ready:
            self.renderer.execute_script("javascript:placeclick('%d')" % 
                                         marker_index)
            self._size_request_for_map(self.box, None)

    def _erase_placebox_selection(self, arg):
        # pylint: disable-msg=W0613
        """
        We erase the place name in the entrybox after 1 second.
        """
        self.placebox.child.set_text("")

    def on_delete(self):
        """
        We need to suppress temporary files here.
        Save the zoom, latitude, longitude and lock
        """
        self._savezoomandposition()
        if config.get('geoview.lock'):
            config.set('geoview.zoom', int(self.realzoom))
            config.set('geoview.latitude', str(self.reallatitude))
            config.set('geoview.longitude', str(self.reallongitude))
            config.set('geoview.map', self.displaytype)
        else:
            config.set('geoview.zoom', 0)
            config.set('geoview.latitude', "0.0")
            config.set('geoview.longitude', "0.0")
            config.set('geoview.map', "person")
        NavigationView.on_delete(self)

    def init_parent_signals_for_map(self, widget, event):
        """
        Required to properly bootstrap the signal handlers.
        This handler is connected by build_widget.
        After the outside ViewManager has placed this widget we are
        able to access the parent container.
        """
        self.box.disconnect(self.bootstrap_handler)
        self.years.hide()
        self.pages_selection.hide()
        self.nocoord.hide()
        self.box.connect("size-allocate", self._size_request_for_map)

    def _size_request_for_bars(self, widget, event, data, data1):
        if self.widget is not None:
            self._size_request_for_map(self.widget,None,None)

    def _size_request_for_map(self, widget, event, data=None):
        # pylint: disable-msg=W0613
        """
        We need to resize the map
        """
        if not self.javascript_ready:
            return
        if not self.resize_occurs:
            self.resize_occurs = True
            gobject.timeout_add(1500, self._really_resize_the_map,
                                widget, event, data)

    def _really_resize_the_map(self, widget, event, data=None):
        # VPane -> Hpane -> NoteBook -> HPaned -> VBox -> Window
        # We need to get the HPaned size and the VPaned size.
        self.resize_occurs = False
        self.box1_size = self.box1.get_allocation()
        self.header_size = self.box1_size.height 
        self.height = (widget.parent.get_allocation().height - self.header_size - 
                        widget.parent.get_child2().get_allocation().height - 30)
        self.width = (widget.parent.parent.get_allocation().width -
                       widget.parent.parent.get_child2().get_allocation().width - 30)

        if not self.sidebar.get_property('visible'):
            if self.side is not None:
                self.width = widget.parent.parent.get_allocation().width - 24
            else:
                self.side = widget
                self.width = widget.parent.parent.get_allocation().width - 300
            _LOG.debug("No sidebar : map width=%d" % self.width)
        else:
            _LOG.debug("Sidebar : map width=%d" % self.width)

        if not self.bottombar.get_property('visible'):
            if self.bottom is not None:
                self.height = (widget.parent.get_allocation().height
                                - self.header_size - 24)
            else:
                self.bottom = widget
                self.height = (widget.parent.get_allocation().height
                                - self.header_size - 400)
            _LOG.debug("No bottombar : map height=%d" % self.height )
        else:
            _LOG.debug("bottombar : map height=%d" % self.height )
        self.widget = widget
        self.height = 10 if self.height < 10 else self.height
        self.width = 10 if self.width < 10 else self.width
        self.box1_size.width = self.width
        self.box1_size.height = self.height
        #self.box1.set_allocation(self.box1_size)
        if self.javascript_ready:
            _LOG.debug("New size : width=%d and height=%d" %
                            (self.width, self.height)
                      )
            self.renderer.execute_script(
                "javascript:mapstraction.resizeTo('%dpx','%dpx');" %
                     (self.width, self.height)
                )
            self.renderer.execute_script(
                "javascript:setcenterandzoom(mapstraction,uzoom,ulat,ulon)"
                )
            self.frames.set_size_request(self.width+4, self.height+4)
        if not self.uistate.get_active('Person'):
            return
        self.external_uri()

    def set_active(self):
        """
        Set view active when we enter into this view.
        """
        self.key_active_changed = self.dbstate.connect(
            'active-changed', self._goto_active_person)
        hobj = self.get_history()
        self.active_signal = hobj.connect(
            'active-changed', self._goto_active_person)
        self._goto_active_person()
        self.active = True
        self._test_network()

    def set_inactive(self):
        """
        Set view inactive when switching to another view.
        """
        HtmlView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)
        self.active = False

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered 
        as a stock icon.
        """
        return 'gramps-geo'
    
    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-geo'

    def _savezoomandposition(self, timeloop=None):
        """
        The only way we have to save the zoom and position is to change the
        title of the html page then to get this title.
        When the title change, we receive a 'changed-title' signal.
        Then we can get the new title with the new values.
        """
        res = self.dbstate.db.get_researcher()
        title = None
        if res: # Don't modify the current values if no db is loaded.
            start = 0
            try:
                title = ZOOMANDPOS.search(self.renderer.title, start)
                if title:
                    if self.realzoom != title.group(1):
                        self.realzoom = title.group(1) if int(title.group(1)) < 17 else 17
                    if self.reallatitude != title.group(2):
                        self.reallatitude = title.group(2)
                    if self.reallongitude != title.group(3):
                        self.reallongitude = title.group(3)
            except:  # pylint: disable-msg=W0704
                pass # pylint: disable-msg=W0702
        if timeloop:
            if self.active:
                if title is not None:
                    self.uistate.status.pop(self.context_id)
                    if self._config.get('preferences.coordinates-in-degree'):
                        latitude, longitude = conv_lat_lon(
                            self.reallatitude, self.reallongitude, "DEG")
                    else:
                        latitude, longitude = conv_lat_lon(
                            self.reallatitude, self.reallongitude, "D.D8")
                    mess = "%s= %s\t%s= %s\t%s= %s" % (
                        _("Latitude"), latitude,
                        _("Longitude"), longitude,
                        _("Zoom"), self.realzoom
                        )
                    self.context_id = self.uistate.status.push(1, mess)
                gobject.timeout_add(timeloop,
                                    self._savezoomandposition, timeloop)

    def _do_we_need_to_zoom_between_map(self):
        """
        Look if we need to use the lasts zoom, latitude and longitude retrieved
        from the renderer, or if we must use the last ones we just created.
        """
        if self.reallatitude is None:
            self.reallatitude = 0.0
        if self.reallongitude is None:
            self.reallongitude = 0.0
        if not config.get('geoview.lock'):
            self.reallatitude = self.latit
            self.reallongitude = self.longt
            self.realzoom = self.zoom if self.zoom < 17 else 17

    def _change_map(self, usedmap):
        """
        Tell the browser to change the current map.
        """
        self.uistate.clear_filter_results()
        self._do_we_need_to_zoom_between_map()
        if self.last_page != 1:
            ftype = {"places":'P',
                     "event":'E',
                     "family":'F',
                     "person":'I'}.get(self.displaytype, 'X')
            url = os.path.join(GEOVIEW_SUBPATH, "GeoV-%c-%05d.html" %
                               (ftype, self.last_page))
            url = urlparse.urlunsplit( ('file', '',
                                        URL_SEP.join(url.split(os.sep)),
                                        '', ''))
        else:
            if not self.htmlfile:
                self.htmlfile = os.path.join(GEOVIEW_SUBPATH, "geography.html")
            url = urlparse.urlunsplit( ('file', '',
                                URL_SEP.join(self.htmlfile.split(os.sep)),
                                '', ''))
        url += '?map=%s' % usedmap
        url += '&zoom=%d' % int(self.realzoom)
        url += '&lat=%s' % str(self.reallatitude)
        url += '&lon=%s' % str(self.reallongitude)
        url += '&cross=%s' % int(self._config.get("preferences.crosshair"))
        self._openurl(url)
        self._savezoomandposition()
        if self.displaytype != "places":
            # Need to wait the page is loaded to set the markers and crosshair.
            gobject.timeout_add(1500, self._set_markers_and_crosshair_on_page,
                                      self.last_year)
        else:
            # Need to wait the page is loaded to set the crosshair.
            gobject.timeout_add(1500, self.config_crosshair,
                                      False, False, False, False)

    def _set_markers_and_crosshair_on_page(self, widget):
        """
        get the year to select then call javascript
        """
        if not self.endinit:
            return
        if widget:
            model = widget.get_model()
            if model:
                year = "no"
                try:
                    year = model.get_value(widget.get_active_iter(), 0)
                except:  # pylint: disable-msg=W0704
                    pass # pylint: disable-msg=W0702
                if self.last_selected_year == 0:
                    self.last_selected_year = year
                elif year != "no":
                    self.last_selected_year = year
                    self._call_js_selectmarkers(year)
        self.config_crosshair(False, False, False, False)

    def _call_js_selectmarkers(self, year):
        """
        Ask to the renderer to show All or specific markers.
        """
        if self.javascript_ready:
            if year == _("All"):
                self.renderer.execute_script(
                    "javascript:selectmarkers('All')")
            else:
                self.renderer.execute_script(
                    "javascript:selectmarkers('%s')" % year )

    def additional_ui(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <menubar name="MenuBar">
          <menu action="GoMenu">
            <placeholder name="CommonGo">
              <menuitem action="PersonMapsMenu"/>
              <menuitem action="FamilyMapsMenu"/>
              <menuitem action="EventMapsMenu"/>
              <menuitem action="AllPlacesMapsMenu"/>
            </placeholder>
          </menu>
          <menu action="EditMenu">
            <separator/>
            <menuitem action="AddPlaceMenu"/>
            <menuitem action="LinkPlaceMenu"/>
          </menu>
          </menubar>
          <toolbar name="ToolBar">
          <placeholder name="CommonEdit">
            <toolitem action="AddPlace"/>
            <toolitem action="LinkPlace"/>
            <separator/>
            <toolitem action="PersonMaps"/>
            <toolitem action="FamilyMaps"/>
            <toolitem action="EventMaps"/>
            <toolitem action="AllPlacesMaps"/>
          </placeholder>
          <placeholder name="CommonNavigation">
            <toolitem action="Back"/>  
            <toolitem action="Forward"/>  
            <toolitem action="HomePerson"/>
          </placeholder>
          </toolbar>
          </ui>'''

    def define_actions(self):
        """
        Required define_actions function for NavigationView. Builds the action
        group information required. 
        """
        NavigationView.define_actions(self)

        # geoview actions
        self._add_action('AddPlace', 'geo-place-add', 
            _('_Add Place'),
            callback=self._add_place,
            tip=_("Add the location centred on the map as a new place in "
                  "Gramps. Double click the location to centre on the map."))
        self._add_action('LinkPlace',  'geo-place-link', 
            _('_Link Place'),
            callback=self._link_place,
            tip=_("Link the location centred on the map to a place in "
                  "Gramps. Double click the location to centre on the map."))
        self._add_action('AddPlaceMenu', 'geo-place-add', 
            _('_Add Place'),
            callback=self._add_place,
            tip=_("Add the location centred on the map as a new place in "
                  "Gramps. Double click the location to centre on the map."))
        self._add_action('LinkPlaceMenu',  'geo-place-link', 
            _('_Link Place'),
            callback=self._link_place,
            tip=_("Link the location centred on the map to a place in "
                  "Gramps. Double click the location to centre on the map."))
        self._add_action('AllPlacesMaps', 'geo-show-place', _('_All Places'),
        callback=self._all_places, tip=_("Attempt to view all places in "
                                         "the family tree."))
        self._add_action('PersonMaps', 'geo-show-person', _('_Person'),
            callback=self._person_places,
            tip=_("Attempt to view all the places "
                  "where the selected people lived."))
        self._add_action('FamilyMaps', 'geo-show-family', _('_Family'),
            callback=self._family_places,
            tip=_("Attempt to view places of the selected people's family."))
        self._add_action('EventMaps', 'geo-show-event', _('_Event'),
            callback=self._event_places,
            tip=_("Attempt to view places connected to all events."))
        self._add_action('AllPlacesMapsMenu', 'geo-show-place',
                         _('_All Places'), callback=self._all_places,
                         tip=_("Attempt to view all places in "
                               "the family tree."))
        self._add_action('PersonMapsMenu', 'geo-show-person', _('_Person'),
            callback=self._person_places,
            tip=_("Attempt to view all the places "
                  "where the selected people lived."))
        self._add_action('FamilyMapsMenu', 'geo-show-family', _('_Family'),
            callback=self._family_places,
            tip=_("Attempt to view places of the selected people's family."))
        self._add_action('EventMapsMenu', 'geo-show-event', _('_Event'),
            callback=self._event_places,
            tip=_("Attempt to view places connected to all events."))

    def change_page(self):
        """
        Called by viewmanager at end of realization when arriving on the page
        At this point the Toolbar is created. We need to:
          1. get the menutoolbutton
          2. add all possible css styles sheet available
          3. add the actions that correspond to clicking in this drop down menu
          4. set icon and label of the menutoolbutton now that it is realized
          5. store label so it can be changed when selection changes
        """
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
        self.other_action.set_sensitive(not self.dbstate.db.readonly)
        self.uistate.modify_statusbar(self.dbstate)
        self.uistate.clear_filter_results()
        self._set_lock_unlock(config.get('geoview.lock'))
        self._savezoomandposition(500) # every 500 millisecondes
        self.endinit = True
        self.uistate.clear_filter_results()
        self._set_provider_icon()
        self._geo_places()

    def _goto_active_person(self, handle=None): # pylint: disable-msg=W0613
        """
        Here when the GeoView page is loaded
        """
        if not self.uistate.get_active('Person'):
            return
        self._geo_places()

    def _all_places(self, hanle=None): # pylint: disable-msg=W0613
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self.sidebar.remove_gramplet(self.active_filter)
        self.active_filter = 'Place Filter Gramplet'
        self.sidebar.add_gramplet(self.active_filter)
        #self.widget.parent.parent.get_child2().show()
        self._geo_places()

    def _person_places(self, handle=None): # pylint: disable-msg=W0613
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        if not self.uistate.get_active('Person'):
            return
        self.sidebar.remove_gramplet(self.active_filter)
        self.active_filter = 'Person Filter Gramplet'
        self.sidebar.add_gramplet(self.active_filter)
        self._geo_places()

    def _family_places(self, hanle=None): # pylint: disable-msg=W0613 
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        if not self.uistate.get_active('Person'):
            return
        self.sidebar.remove_gramplet(self.active_filter)
        self.active_filter = 'Family Filter Gramplet'
        self.sidebar.add_gramplet(self.active_filter)
        self._geo_places()

    def _event_places(self, hanle=None): # pylint: disable-msg=W0613
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self.sidebar.remove_gramplet(self.active_filter)
        self.active_filter = 'Event Filter Gramplet'
        self.sidebar.add_gramplet(self.active_filter)
        self._geo_places()

    def _new_database(self, database):
        """
        We just change the database.
        Restore the initial config. Is it good ?
        """
        if config.get('geoview.lock'):
            self.realzoom = config.get('geoview.zoom')
            self.displaytype = config.get('geoview.map')
            self.reallatitude, self.reallongitude = conv_lat_lon(
                                    config.get('geoview.latitude'),
                                    config.get('geoview.longitude'),
                                    "D.D8")
        self._change_db(database)
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])

    def _geo_places(self):
        """
        Specifies the places to display with mapstraction.
        """
        if not self.endinit:
            return
        if not self.dbstate.db.is_open():
            return
        if self.nbmarkers > 0 :
            # While the db is not loaded, we have 0 markers.
            self._savezoomandposition()
        self._test_network()
        self.nbmarkers = 0
        self.nbplaces = 0
        self.without = 0
        self.javascript_ready = False
        self._createmapstraction(self.displaytype)

    def _set_lock_unlock(self, state):
        """
        Change the lock/unlock state.
        """
        config.set('geoview.lock', state)
        self._set_lock_unlock_icon()

    def _set_lock_unlock_icon(self):
        """
        Change the lock/unlock icon depending on the button state.
        """
        child = self.savezoom.child
        if child:
            self.savezoom.remove(child)
        image = gtk.Image()
        if config.get('geoview.lock'):
            image.set_from_stock('geo-fixed-zoom', gtk.ICON_SIZE_MENU)
        else:
            image.set_from_stock('geo-free-zoom', gtk.ICON_SIZE_MENU)
        image.show()
        self.savezoom.add(image)
        self._geo_places()

    def _save_zoom(self, button): # pylint: disable-msg=W0613
        """
        Do we change the zoom between maps ?
        It's not between maps providers, but between people, family,
        events or places map.
        When we unlock, we reload the page with our values.
        """
        if config.get('geoview.lock'):
            config.set('geoview.lock', False)
            self._set_lock_unlock(False)
        else:
            config.set('geoview.lock', True)
            self._set_lock_unlock(True)

    def _change_provider(self, button): # pylint: disable-msg=W0613
        """
        Toogle between the two maps providers.
        Inactive ( the default ) is openstreetmap.
        As openstreetmap has no api, we now use openlayers.
        Active means Google maps.
        """
        if self._config.get('preferences.alternate-provider'):
            self.usedmap = "openlayers"
            self._config.set('preferences.alternate-provider', False)
        else:
            self.usedmap = "googlev3"
            self._config.set('preferences.alternate-provider', True)
        self._set_provider_icon()
        self._change_map(self.usedmap)
        self._ask_year_selection(self.last_year)

    def _set_provider_icon(self):
        """
        Change the provider icon depending on the button state.
        """
        child = self.provider.child
        if child:
            self.provider.remove(child)
        image = gtk.Image()
        if self._config.get('preferences.alternate-provider'):
            image.set_from_stock('gramps-geo-altmap', gtk.ICON_SIZE_MENU)
        else:
            image.set_from_stock('gramps-geo-mainmap', gtk.ICON_SIZE_MENU)
        image.show()
        self.provider.add(image)

    def _createpageplaceswithoutcoord(self):
        """
        Create a page with the list of all places without coordinates
        page.
        """
        ufd = open(self.without_coord_file, "w+")
        ufd.write(
            _HTMLHEADER %
                { 'title'  : _('List of places without coordinates'),
                  'lang'   : 'en',
                  'css'    : self._add_stylesheet(),
                }
            + '  </head>\n'
            )
        ufd.write(
            '  <body>\n' +
            '    <H4>%s<a href="javascript:history.go(-1)">%s</a></H4>'
                % (_('Here is the list of all places in the family tree'
                     ' for which we have no coordinates.<br>'
                     ' This means no longitude or latitude.<p>'),
                   _('Back to prior page')
                  )
            )
        self.places = sorted(self.place_without_coordinates)
        ufd.write(
            "    <table border=1 ><th width=10%>NB</th>" +
                    "<th width=20%>Gramps ID</th><th>Place</th>"
            )
        #for p, place in enumerate(self.places):
        #    ufd.write("    <tr><td>%d</td><td>%s</td><td>%s</td></tr>\n"
        #             % (p + 1, place[0], place[1]))

        ufd.writelines(
            "    <tr><td>%d</td><td>%s</td><td>%s</td></tr>\n"
                % (p + 1, gid, place)
            for p, (gid, place) in enumerate(self.places)
            )
        ufd.write("    </table>\n"
                  "  </body>\n"
                  "</html>\n"
            )
        ufd.close()

    def _create_pages_without(self):
        """
        Show or hide the page without coord button.
        """
        if self.without > 0:
            self._createpageplaceswithoutcoord()
            self.nocoord.set_label("%d ?" % ( self.without) )
            self.nocoord.show()
        else:
            self.nocoord.hide()

    def _create_pages_selection(self, current, pages):
        """
        Set the label text in the pages selection button
        """
        self.pages[1].set_label("%d/%d" % ( current, pages ) )

    def _createmapstractionpostheader(self, h4mess, curpage):
        # disable msg=W0613 # curpage is unused
        # pylint: disable-msg=W0613
        """
        This is needed to add infos to the header.
        This can't be in createmapstractionheader because we need
        to know something which is known only after some work.
        """
        if self.maxyear == 0:
            self.maxyear = 2100
        if self.minyear == 9999:
            self.minyear = 1500
        adjust_before_min_year = self._config.get(
                                       'preferences.timeperiod-before-range')
        adjust_after_max_year = self._config.get(
                                       'preferences.timeperiod-after-range')
        self.minyear -= ( self.minyear - adjust_before_min_year ) % 10
        self.maxyear -= ( self.maxyear + adjust_after_max_year ) % 10
        self.yearint = (adjust_after_max_year +
                           (self.maxyear - self.minyear) / (self.maxbut - 1)
                       )
        self.yearint -= self.yearint % 10
        if self.yearint == 0:
            self.yearint = 10
        self.mapview.write(
            "<script>\n" +
            " var step = %s;\n" % self.yearint +
            "</script>\n" +
            "</head>\n"+
            "<body>\n"
            )
        self.years.hide()
        if h4mess:
            self.mapview.write("<h4>%s</h4>\n" % h4mess)
        else:
            if self.displaytype != "places":
                self._set_years_selection(self.minyear,
                                          self.yearint,
                                          self.maxyear)
                self.years.show()
        self.mapview.write(
            '<div id="geo-map" style="' +
            'height: %dpx; width: %dpx; " ></div>\n'
                % ( self.height, self.width ) +
            '<script type="text/javascript">\n' +
            ' args=getArgs();\n' +
            ' if (args.map) current_map=args.map;\n' +
            ' if (args.lat) ulat=parseFloat(args.lat);\n' +
            ' if (args.lon) ulon=parseFloat(args.lon);\n' +
            ' if (args.zoom) uzoom=parseInt(args.zoom);\n' +
            ' if (args.cross) ucross=parseInt(args.cross);\n' +
            ' mapstraction = new mxn.Mapstraction' +
            "('geo-map',current_map);\n" +
            ' mapstraction.addControls(' +
            "{ pan: true, zoom: 'small', " +
            'scale: true, map_type: true });\n' +
            "addcrosshair(ucross, '%s', 'geo-map');" % self.crosspath
            )

    def _create_needed_javascript(self):
        """
        Create the needed javascript functions.
        """
        self.mapview.write(_JAVASCRIPT)
        return

    def _createmapstractionheader(self, filename):
        """
        Create the html header of the page.
        """
        # disable msg=W0612 # modifier is unused
        # pylint: disable-msg=W0612
        self.mapview = open(filename, "w+")
        (lang_country, modifier ) = locale.getlocale()
        lang = lang_country.split('_')[0] if lang_country else 'en'
        self.mapview.write(
            _HTMLHEADER % {
                "title": "This is used to pass messages between "
                         "Javascript and Python",
                "lang" : lang,
                "css"  : self._add_stylesheet()
                }
            )
        fpath = os.path.join(const.WEBSTUFF_DIR, 'js/mapstraction',
                                             "mxn.js?(googlev3,openlayers)")
        upath = urlparse.urlunsplit(
            ('file', '', URL_SEP.join(fpath.split(os.sep)), '', '')
            )
        self.mapview.write(
            '<script type="text/javascript"' +
            ' src="http://maps.google.com/maps/api/js?sensor=false">' +
            '</script>\n' +
            '<script type="text/javascript"' +
            ' src="http://openlayers.org/api/OpenLayers.js">' +
            '</script>\n' +
            '<script type="text/javascript"' +
            ' src="%s"></script>\n' % upath
            )

    def _createmapstractiontrailer(self):
        """
        Add the last directives for the html page.
        """

        self.mapview.write(_HTMLTRAILER)
        self.mapview.close()

    def _set_center_and_zoom(self, ptype):
        """
        Calculate the zoom.
        """
        # Select the center of the map and the zoom
        self.centered = False
        if ptype == 2:
            # Sort by places and year for events
            self.sort = sorted(self.place_list,
                               key=operator.itemgetter(3, 4, 7)
                              )
        else:
            # Sort by date in all other cases
            self.sort = sorted(self.place_list,
                               key=operator.itemgetter(7)
                              )
        signminlon = _get_sign(self.minlon)
        signminlat = _get_sign(self.minlat)
        signmaxlon = _get_sign(self.maxlon)
        signmaxlat = _get_sign(self.maxlat)
        if signminlon == signmaxlon: 
            maxlong = abs(abs(self.minlon) - abs(self.maxlon))
        else:
            maxlong = abs(abs(self.minlon) + abs(self.maxlon))
        if signminlat == signmaxlat:
            maxlat = abs(abs(self.minlat) - abs(self.maxlat))
        else:
            maxlat = abs(abs(self.minlat) + abs(self.maxlat))
        # Calculate the zoom. all places must be displayed on the map.
        zoomlat = _get_zoom_lat(maxlat)
        zoomlong = _get_zoom_long(maxlong)
        self.zoom = zoomlat if zoomlat < zoomlong else zoomlong
        self.zoom -= 1
        if self.zoom < 2:
            self.zoom = 2
        # We center the map on a point at the center of all markers
        self.centerlat = maxlat/2
        self.centerlon = maxlong/2
        latit = longt = 0.0
        for mark in self.sort:
            cent = int(mark[6])
            if cent:
                self.centered = True
                if ( signminlat == signmaxlat ):
                    if signminlat == 1: 
                        latit = self.minlat+self.centerlat
                    else:
                        latit = self.maxlat-self.centerlat
                elif self.maxlat > self.centerlat:
                    latit = self.maxlat-self.centerlat
                else:
                    latit = self.minlat+self.centerlat
                if ( signminlon == signmaxlon ):
                    if signminlon == 1: 
                        longt = self.minlon+self.centerlon
                    else:
                        longt = self.maxlon-self.centerlon
                elif self.maxlon > self.centerlon:
                    longt = self.maxlon-self.centerlon
                else:
                    longt = self.minlon+self.centerlon
                # all maps: 0.0 for longitude and latitude means no location.
                if latit == longt == 0.0:
                    latit = longt = 0.00000001
        self.mustcenter = False
        if not (latit == longt == 0.0):
            self.latit = latit
            self.longt = longt
            self.mustcenter = True

    def _create_pages(self, ptype, h3mess, h4mess):
        """
        Do we need to create a multi-pages document ?
        Do we have too many markers ?
        """
        # disable msg=W0612 # page is unused
        # pylint: disable-msg=W0612
        self.nbpages = 0
        self.last_page = 1
        self.box1.set_sensitive(True)
        self.pages_selection.hide()
        self.placebox.child.set_text("")
        self.placebox.freeze_child_notify()
        self.placebox.set_model(None)
        self.plist.clear()
        self.clear.set_label("%s (%d)" % ( _("Places list"), self.nbplaces ))
        pages = ( self.nbplaces / self._config.get('preferences.markers') )
        if (self.nbplaces % self._config.get('preferences.markers') ) != 0:
            pages += 1
        if self.nbplaces == 0:
            try:
                self._createmapstractiontrailer()
            except:  # pylint: disable-msg=W0704
                pass # pylint: disable-msg=W0702
        self._set_center_and_zoom(ptype)
        self._create_pages_without()
        if pages > 1:
            self._create_pages_selection(1, pages)
            self.pages_selection.show()
        self.last_index = 0
        for page in range(0, pages, 1):
            self.nbpages += 1
            ftype = {1:'P', 2:'E', 3:'F', 4:'I'}.get(ptype, 'X')
            filename = os.path.join(
                GEOVIEW_SUBPATH, "GeoV-%c-%05d.html" %  (ftype, self.nbpages))
            if self.nbpages == 1:
                self.htmlfile = filename
            self._createmapstractionheader(filename)
            self._create_needed_javascript()
            first = ( self.nbpages - 1 ) * self._config.get('preferences.markers') 
            last = ( self.nbpages * self._config.get('preferences.markers') ) - 1
            self._create_markers(ptype, first, last)
            self._show_heading(h3mess)
            self._createmapstractionpostheader(h4mess, self.nbpages)
            self._createmapstractiontrailer()
            if self.nbpages == 1:
                self._do_we_need_to_zoom_between_map()
                url = urlparse.urlunsplit( ('file', '',
                                URL_SEP.join(self.htmlfile.split(os.sep)),
                                '', ''))
                url += '?map=%s' % self.usedmap
                url += '&zoom=%d' % int(self.realzoom)
                url += '&lat=%s' % str(self.reallatitude)
                url += '&lon=%s' % str(self.reallongitude)
                url += '&cross=%s' % int(self._config.get("preferences.crosshair"))
                self._openurl(url)
                self._savezoomandposition()
                if self.displaytype != "places":
                    # Need to wait the page is loaded to set the markers and crosshair.
                    gobject.timeout_add(1500,
                                        self._set_markers_and_crosshair_on_page,
                                        self.last_year)
                else:
                    # Need to wait the page is loaded to set the crosshair.
                    gobject.timeout_add(1500, self.config_crosshair,
                                              False, False, False, False)
        self.placebox.set_model(self.plist)
        self.placebox.thaw_child_notify()

    def _createmapstraction(self, displaytype):
        """
        Which kind of map are we going to create ?
        """
        self.cal = config.get('preferences.calendar-format-report')
        if displaytype == "places":
            self._createmapstractionplaces(self.dbstate)
        elif displaytype == "family":
            self._createmapstractionfamily(self.dbstate)
        elif displaytype == "person":
            self._createmapstractionperson(self.dbstate)
        elif displaytype == "event":
            self._createmapstractionevents(self.dbstate)
        else:
            self._createmapstractionheader(
                os.path.join(GEOVIEW_SUBPATH, "error.html"))
            self._createmapnotimplemented()
            self._createmapstractiontrailer()

    def _append_to_places_without_coord(self, gid, place):
        """
        Create a list of places without coordinates.
        """
        if not [gid, place] in self.place_without_coordinates:
            self.place_without_coordinates.append([gid, place])
            self.without += 1

    def _append_to_places_list(self, place, evttype, name, lat, 
                              longit, descr, center, year, icontype):
        """
        Create a list of places with coordinates.
        """
        found = any(p[0] == place for p in self.place_list)
        if not found:
            self.nbplaces += 1
        self.place_list.append([place, name, evttype, lat,
                                longit, descr, int(center), year, icontype])
        self.nbmarkers += 1
        tfa = float(lat)
        tfb = float(longit)
        if year is not None:
            tfc = int(year)
            if tfc != 0:
                if tfc < self.minyear:
                    self.minyear = tfc
                if tfc > self.maxyear:
                    self.maxyear = tfc
        tfa += 0.00000001 if tfa >= 0 else -0.00000001
        tfb += 0.00000001 if tfb >= 0 else -0.00000001
        if self.minlat == 0.0 or tfa < self.minlat:
            self.minlat = tfa
        if self.maxlat == 0.0 or tfa > self.maxlat:
            self.maxlat = tfa
        if self.minlon == 0.0 or tfb < self.minlon:
            self.minlon = tfb
        if self.maxlon == 0.0 or tfb > self.maxlon:
            self.maxlon = tfb

    def _set_icon(self, markertype, differtype, ptype):
        """
        Select the good icon depending on events.
        If we have different events for one place, we use the default icon.
        """
        if ptype != 1: # for places, we have no event type
            value = _ICONS.get(markertype.value, 'gramps-geo-default')
        else:
            value = 'gramps-geo-default'
        if differtype:                   # in case multiple evts
            value = 'gramps-geo-default' # we use default icon.
        if ( value == "gramps-geo-default" ):
            value = value.replace("default",'" + default_icon + "')
        ipath = os.path.join(const.WEBSTUFF_DIR, 'images', '%s.png' % value )
        upath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(ipath.split(os.sep)), '', ''))
        # Workaround to avoid a drift problem with openlayers.
        self.mapview.write(
            #'\n  // workaround to avoid openlayers drift.\n' +
            '\n  if ( current_map != "openlayers" ) {' +
            '   my_marker.setIcon("%s",[19,19],[0,19]);' % upath +
            '   } else { ' +
            '   my_marker.setIcon("%s",[19,19],[0,-19]);' % upath +
            '   }\n'
            )

    def _show_heading(self, heading):
        """
        Show the current map heading in the gtk label above the map.
        """
        self.heading.set_text(heading)

    def _create_markers(self, formatype, firstm, lastm):
        """
        Create all markers for the specified person.
        """
        last = ""
        current = ""
        self.placeslist = []
        indm = 0
        divclose = True
        self.yearinmarker = []
        ininterval = False
        self.setattr = True
        self.mapview.write(" function setcenterandzoom(map,uzoom,ulat,ulon){\n")
        if self.mustcenter:
            self.centered = True
            self.mapview.write(
                "  var point = new mxn.LatLonPoint" 
                "(ulat,ulon);" 
                "map.setCenterAndZoom" 
                "(point, uzoom);\n"
                )
            self.setattr = False
        self.mapview.write(
            '}\n'
            ' function setmarkers(map) {\n'
            '  if ( current_map != "openlayers" ) {'
            ' default_icon = "altmap";'
            ' } else { '
            ' default_icon = "mainmap"; }\n'
            )
        differtype = False
        savetype = None
        index_mark = 0
        indm = firstm
        for mark in self.sort:
            index_mark += 1
            if index_mark < self.last_index:
                continue
            if lastm >= indm >= firstm:
                ininterval = True
            if ininterval:
                current = {2 : [mark[3], mark[4]],
                          }.get(formatype, mark[0])
                if last != current:
                    if not divclose:
                        if ininterval:
                            self.mapview.write('</div>");')
                            divclose = True
                        years = ""
                        if mark[2]:
                            for year in self.yearinmarker:
                                years += "%d " % year
                        years += "end"
                        self.mapview.write(
                            "my_marker.setAttribute" +
                            "('year','%s');" % years
                            )
                        self.yearinmarker = []
                        self._set_icon(savetype, differtype, formatype)
                        differtype = False
                        self.mapview.write("  map.addMarker(my_marker);")
                    if ( indm > lastm ):
                        if (indm % self._config.get('preferences.markers')) == 0:
                            self.last_index = index_mark
                            ininterval = False
                    last = {2 : [mark[3], mark[4]],
                           }.get(formatype, mark[0])
                    if lastm >= indm >= firstm:
                        ind = indm % self._config.get('preferences.markers')
                        self.plist.append([ mark[0], ind, self.nbpages] )
                        indm += 1
                        self.mapview.write(
                            "\n  var point = new mxn.LatLonPoint" +

                            "(%s,%s);" % (mark[3], mark[4]) +
                            "my_marker = new mxn.Marker(point);" +
                            "gmarkers[%d]=my_marker;" % ind +
                            "my_marker.setLabel" +
                            '("%s");' % _escape(mark[0])
                            )
                        self.yearinmarker.append(mark[7])
                        divclose = False
                        differtype = False
                        if mark[8] and not differtype:
                            savetype = mark[8]
                        self.mapview.write(
                            'my_marker.setInfoBubble("<div ' +
                            "id='geo-info' >" +
                            "%s<br>" % _escape(mark[0])
                            )
                        if formatype == 1:
                            self.mapview.write("<br>%s" % _escape(mark[5]))
                        else:
                            self.mapview.write("<br>%s - %s" % 
                                               (mark[7], _escape(mark[5])))
                else: # This marker already exists. add info.
                    if ( mark[8] and savetype != mark[8] ):
                        differtype = True
                    if indm > last:
                        divclose = True
                    else:
                        self.mapview.write("<br>%s - %s" % (mark[7],
                                                            _escape(mark[5])))
                    if not any(y == mark[7] for y in self.yearinmarker):
                        self.yearinmarker.append(mark[7])
            else:
                indm += 1
        if self.nbmarkers > 0 and ininterval:
            years = ""
            if mark[2]:
                for year in self.yearinmarker:
                    years += "%d " % year
            years += "end"
            self.mapview.write(
                '</div>");' +
                "my_marker.setAttribute('year','%s');" % years
                )
            self._set_icon(savetype, differtype, formatype)
            self.mapview.write("  map.addMarker(my_marker);")
        if self.nbmarkers == 0:
            # We have no valid geographic point to center the map.
            longitude = 0.0
            latitude = 0.0
            self.mapview.write(
                "\nvar point = new mxn.LatLonPoint" +
                "(%s,%s);\n" % (latitude, longitude) +
                "   map.setCenterAndZoom" +
                "(point, %d);\n" % 2 +
                "   my_marker = new mxn.Marker(point);\n" +
                "   my_marker.setLabel" +
                '("%s");\n' % _("No location.") +
                '   my_marker.setInfoBubble("<div ' +
                "style='white-space:nowrap;' >" +
                _("You have no places in your family tree "
                                     " with coordinates.") +
                "<br>" +
                _("You are looking at the default map.") +
                '</div>");\n'
                )
            self._set_icon(None, True, 1)
            self.mapview.write("   map.addMarker(my_marker);")
        self.mapview.write(
            "\n}"
            "\n</script>\n"
            )

    def _createpersonmarkers(self, dbstate, person, comment):
        """
        Create all markers for the specified person.
        """
        latitude = longitude = ""
        if person:
            event_ref = person.get_birth_ref()
            if event_ref:
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                eventyear = event.get_date_object().to_calendar(self.cal).get_year()
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude,
                                                           longitude, "D.D8")
                        if comment:
                            descr1 = _("%s : birth place.") % comment
                        else:
                            descr1 = _("birth place.")
                        descr = place.get_title()
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if ( longitude and latitude ):
                            self._append_to_places_list(descr,
                                                        gen.lib.EventType.BIRTH,
                                                        _nd.display(person),
                                                        latitude, longitude,
                                                        descr1,
                                                        int(self.center),
                                                        eventyear,
                                                        event.get_type()
                                                        )
                            self.center = False
                        else:
                            self._append_to_places_without_coord(
                                 place.gramps_id, descr)
            latitude = longitude = ""
            event_ref = person.get_death_ref()
            if event_ref:
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                eventyear = event.get_date_object().to_calendar(self.cal).get_year()
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude,
                                                           longitude, "D.D8")
                        descr = place.get_title()
                        if comment:
                            descr1 = _("%s : death place.") % comment
                        else:
                            descr1 = _("death place.")
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if ( longitude and latitude ):
                            self._append_to_places_list(descr,
                                                        gen.lib.EventType.DEATH,
                                                        _nd.display(person),
                                                        latitude, longitude,
                                                        descr1,
                                                        int(self.center),
                                                        eventyear,
                                                        event.get_type()
                                                        )
                            self.center = False
                        else:
                            self._append_to_places_without_coord(
                                 place.gramps_id, descr)

    def _createmapstractionplaces(self, dbstate):
        """
        Create the marker for each place in the database which has a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = 0.0
        self.maxlat = 0.0
        self.minlon = 0.0
        self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        latitude = ""
        longitude = ""
        self.center = True

        if self.generic_filter is None or not config.get('interface.filter'):
            places_handle = dbstate.db.iter_place_handles()
        else:
            places_handle = self.generic_filter.apply(
                dbstate.db, dbstate.db.iter_place_handles())
        for place_hdl in places_handle:
            place = dbstate.db.get_place_from_handle(place_hdl)
            descr = place.get_title()
            descr1 = _("Id : %s") % place.gramps_id
            longitude = place.get_longitude()
            latitude = place.get_latitude()
            latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
            # place.get_longitude and place.get_latitude return
            # one string. We have coordinates when the two values
            # contains non null string.
            if ( longitude and latitude ):
                self._append_to_places_list(descr, None, "",
                                            latitude, longitude,
                                            descr1, self.center, None,
                                            gen.lib.EventType.UNKNOWN)
                self.center = False
            else:
                self._append_to_places_without_coord(place.gramps_id, descr)
        self.yearsbox.hide()
        self._need_to_create_pages(1, self.center,
                                  _("All places in the family tree with "
                                    "coordinates."),
                                  )

    def _createmapstractionevents(self, dbstate):
        """
        Create one marker for each place associated with an event in the
        database which has a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        latitude = ""
        longitude = ""
        self.center = True

        if self.generic_filter is None or not config.get('interface.filter'):
            events_handle = dbstate.db.iter_event_handles()
        else:
            events_handle = self.generic_filter.apply(
                dbstate.db, dbstate.db.iter_event_handles())
        for event_hdl in events_handle:
            event = dbstate.db.get_event_from_handle(event_hdl)
            place_handle = event.get_place_handle()
            eventyear = event.get_date_object().to_calendar(self.cal).get_year()
            if place_handle:
                place = dbstate.db.get_place_from_handle(place_handle)
                if place:
                    descr1 = place.get_title()
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    latitude, longitude = conv_lat_lon(latitude, longitude, 
                                                       "D.D8")
                    # place.get_longitude and place.get_latitude return
                    # one string. We have coordinates when the two values
                    # contains non null string.
                    if ( longitude and latitude ):
                        person_list = [
                            dbstate.db.get_person_from_handle(ref_handle)
                            for (ref_type, ref_handle) in 
                                dbstate.db.find_backlink_handles(event.handle)
                                    if ref_type == 'Person' 
                                      ]
                        descr2 = "%s" % event.get_type()
                        if person_list:
                            for person in person_list:
                                descr2 = ("%(description)s - %(name)s") % {
                                            'description' : descr2, 
                                            'name' : _nd.display(person)}
                            descr = ("%(eventtype)s;"+
                                     " %(place)s%(description)s"
                                     ) % { 'eventtype': gen.lib.EventType(
                                                            event.get_type()
                                                            ),
                                           'place': place.get_title(), 
                                           'description': descr2}
                        else:
                            descr = ("%(eventtype)s; %(place)s<br>") % {
                                           'eventtype': gen.lib.EventType(
                                                            event.get_type()
                                                            ),
                                           'place': place.get_title()}
                        self._append_to_places_list(descr1, descr,
                                                    descr,
                                                    latitude, longitude,
                                                    descr2, self.center,
                                                    eventyear,
                                                    event.get_type()
                                                    )
                        self.center = False
                    else:
                        descr = place.get_title()
                        self._append_to_places_without_coord(
                             place.gramps_id, descr)
        self._need_to_create_pages(2, self.center,
                                  _("All events in the family tree with "
                                    "coordinates."),
                                  )

    def _createmapstractionfamily(self, dbstate):
        """
        Create all markers for each people of a family
        in the database which has a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.center = True
        person_handle = self.uistate.get_active('Person')
        person = dbstate.db.get_person_from_handle(person_handle)
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0] # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                handle = fam.get_father_handle()
                father = dbstate.db.get_person_from_handle(handle)
                if father:
                    comment = _("Id : Father : %s : %s") % ( father.gramps_id,
                                                             _nd.display(father)
                                                            )
                    self._createpersonmarkers(dbstate, father, comment)
                handle = fam.get_mother_handle()
                mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    comment = _("Id : Mother : %s : %s") % ( mother.gramps_id,
                                                             _nd.display(mother)
                                                            )
                    self._createpersonmarkers(dbstate, mother, comment)
                index = 0
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            index += 1
                            comment = _("Id : Child : %(id)s - %(index)d "
                                        ": %(name)s") % {
                                            'id'    : child.gramps_id,
                                            'index' : index,
                                            'name'  : _nd.display(child)
                                         }
                            self._createpersonmarkers(dbstate, child, comment)
            else:
                comment = _("Id : Person : %(id)s %(name)s has no family.") % {
                                'id' : person.gramps_id ,
                                'name' : _nd.display(person)
                                }
                self._createpersonmarkers(dbstate, person, comment)
            self._need_to_create_pages(3, self.center,
                                      _("All %(name)s people's family places in"
                                       " the family tree with coordinates.") % {
                                         'name' :_nd.display(person) },
                                      )

    def _createmapstractionperson(self, dbstate):
        """
        Create all markers for each people's event in the database which has 
        a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        latitude = ""
        longitude = ""
        person_handle = self.uistate.get_active('Person')
        person = dbstate.db.get_person_from_handle(person_handle)
        self.center = True
        if person is not None:
            # For each event, if we have a place, set a marker.
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                eventyear = event.get_date_object().to_calendar(self.cal).get_year()
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude,
                                                           longitude, "D.D8")
                        descr = place.get_title()
                        evt = gen.lib.EventType(event.get_type())
                        descr1 = _("%(eventtype)s : %(name)s") % {
                                        'eventtype': evt,
                                        'name': _nd.display(person)}
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if ( longitude and latitude ):
                            self._append_to_places_list(descr, evt,
                                                        _nd.display(person),
                                                        latitude, longitude,
                                                        descr1, self.center, 
                                                        eventyear,
                                                        event.get_type()
                                                        )
                            self.center = False
                        else:
                            self._append_to_places_without_coord(
                                                        place.gramps_id, descr)
            self._need_to_create_pages(4, self.center, 
                                       _("All event places for") + (" %s." % 
                                                         _nd.display(person) ) )

    def _need_to_create_pages(self, ptype, center, message ):
        """
        Prepare the header of the page if we have no markers.
        """
        if center:
            page = self._create_message_page(
              _("Cannot center the map. No location with coordinates."
                "That may happen for one of the following reasons : <ul>"
                "<li>The filter you use returned nothing.</li>"
                "<li>The active person has no places with coordinates.</li>"
                "<li>The active person's family members have no places "
                "with coordinates.</li><li>You have no places.</li>"
                "<li>You have no active person set.</li>"), 
              )
            self.box1.set_sensitive(False)
            self._openurl(page)
        else:
            mess = ""
            self._create_pages(ptype, message, mess)

    def _createmapnotimplemented(self):
        """
        Inform the user this work is not implemented.
        """
        self.mapview.write("  <H1>%s </H1>" % _("Not yet implemented ..."))

    def _add_stylesheet(self):
        """
        Return the css style sheet needed for GeoView.
        """
        dblp = '<link media="screen" '
        delp = 'type="text/css" rel="stylesheet" />\n'
        # Get the GeoView stylesheet.
        cpath = os.path.join(const.WEBSTUFF_DIR, 'css', 'GeoView.css')
        gpath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(cpath.split(os.sep)),
                                     '', ''))
        gcp = 'href="%s" ' % gpath
        return u'%s%s%s' % (dblp, gcp, delp)
    
    def _openurl(self, url):
        """
        Here, we call really the htmlview and the renderer
        """
        if self.endinit and not self.no_network:
            if self.invalidpath != -1:
                spaces = ""
                for i in range(self.invalidpath):
                    spaces = spaces + ' '
                spaces = spaces + '^'
                self.open(self._create_message_page('<p>%s<br><br>'
                                                    '<pre>%s<br>%s</pre>' % (
                               _('Invalid path for const.ROOT_DIR:<br>'
                                 ' avoid parenthesis into this parameter'),
                               const.ROOT_DIR, spaces )
                                                   )
                         )
            else:
                self.open(url)
                self.javascript_ready = True

    def _add_place(self, url): # pylint: disable-msg=W0613
        """
        Add a new place using longitude and latitude of location centred
        on the map
        """
        new_place = gen.lib.Place()
        new_place.set_latitude(str(self.reallatitude))
        new_place.set_longitude(str(self.reallongitude))
        try:
            EditPlace(self.dbstate, self.uistate, [], new_place)
        except Errors.WindowActiveError: # pylint: disable-msg=W0704
            pass # pylint: disable-msg=W0702

    def _link_place(self, url): # pylint: disable-msg=W0613
        """
        Link an existing place using longitude and latitude of location centred
        on the map
        """
        selector = SelectPlace(self.dbstate, self.uistate, [])
        place = selector.run()
        if place:
            place.set_latitude(str(self.reallatitude))
            place.set_longitude(str(self.reallongitude))
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except Errors.WindowActiveError: # pylint: disable-msg=W0704
                pass # pylint: disable-msg=W0702

    def build_tree(self):
        """
        Builds the new view depending on the filter.
        """
        self._geo_places()

    def _create_start_page(self):
        """
        This command creates a default start page, and returns the URL of
        this page.
        """
        tmpdir = GEOVIEW_SUBPATH
        content = _('You don\'t see a map here for one of the following '
                    'reasons :<br><ol>'
                    '<li>Your database is empty or not yet selected.</li>'
                    '<li>You have not selected a person yet.</li>'
                    '<li>You have no places in your database.</li>'
                    '<li>The selected places have no coordinates.</li>'
                     '</ol>')
        
        filename = os.path.join(tmpdir, 'geography.html')
        # Now we have two views : Web and Geography, we need to create the
        # startpage only once.
        if not os.path.exists(filename):
            ufd = file(filename, "w+")
            ufd.write(
                _HTMLHEADER % {
                    'title': _('Start page for the Geography View'),
                    'lang' : 'en',
                    'css'  : '',
                    }
                + '  </head>\n'
                )
            ufd.write('''\
                 <body>
                   <H1>%(title)s</H1>
                   <H4>%(content)s</H4>
                 </body>
                </html>
                ''' % {
                        'title'  : _('Start page for the Geography View'),
                        'content': content,
                      }
                )
            ufd.close()
        return urlparse.urlunsplit(
            ('file', '', URL_SEP.join(filename.split(os.sep)), '', '')
            )

    def _create_message_page(self, message):
        """
        This function creates a page which contains a message.
        """
        tmpdir = GEOVIEW_SUBPATH
        filename = os.path.join(tmpdir, 'message.html')
        ufd = file(filename, "w+")
        ufd.write(
            _HTMLHEADER % {
                'title' : 'Message',
                'lang'  : 'en',
                'css'   : '',
                }
            + '  </head>\n'
            )
        ufd.write(
            '<body>\n'
            '  <h4>%s</h4>\n' % message +
            '<body>\n'
            '</html>'
            )
        ufd.close()
        return urlparse.urlunsplit(
            ('file', '', URL_SEP.join(filename.split(os.sep)), '', '')
            )

    def __test_network(self):
        """
        This function is used to test if we are connected to a network.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._config.get('preferences.network-timeout'))
            sock.connect((self._config.get('preferences.network-site'), 80))
            if sock is not None:
                if self.no_network == True:
                    self.no_network = False
                    self._change_map(self.usedmap)
                sock.close()
            else:
                self.no_network = True
        except:
            self.no_network = True

        if self.active and self._config.get('preferences.network-test'):
            gobject.timeout_add(
                    self._config.get('preferences.network-periodicity') * 1000,
                    self.__test_network)
        else: 
            self.already_testing = False
        if self.no_network:
            self.open(self._create_message_page(
                      'No network connection found.<br>A connection to the'
                      ' internet is needed to show places or events on a map.'))

    def _test_network(self):
        """
        This function is used to test if we are connected to a network.
        """
        if not self.endinit:
            return
        if not self._config.get('preferences.network-test'):
            return
        if self.already_testing: # we need to avoid multiple tests.
            return
        else:
            self.already_testing = True
        if self._config.get('preferences.network-periodicity') < 10:
            # How many seconds between tests ? mini = 10 secondes.
            self._config.set('preferences.network-periodicity', 10)
        self.__test_network()

    def get_bookmarks(self):
        return self.dbstate.db.get_family_bookmarks()

    def add_bookmark(self, obj):
        mlist = self.selected_handles()
        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))

    def navigation_group(self):
        """
        Return the navigation group.
        """
        return self.nav_group

    def navigation_type(self):
        return 'Person'

    def get_history(self):
        """
        Return the history object.
        """
        _LOG.debug("get history")
        return self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())
