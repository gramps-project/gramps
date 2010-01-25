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
import urlparse
import const
import operator
import locale
from gtk.keysyms import Tab as KEY_TAB

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
from gui.utils import add_menuitem
from ReportBase import CSS_FILES
from gen.display.name import displayer as _nd
from PlaceUtils import conv_lat_lon
from gui.views.pageview import PageView
from gui.editors import EditPlace
from gui.selectors.selectplace import SelectPlace
from Filters.SideBar import PlaceSidebarFilter, EventSidebarFilter

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
GEOVIEW_SUBPATH = Utils.get_empty_tempdir('geoview')
NB_MARKERS_PER_PAGE = 200

#-------------------------------------------------------------------------
#
# Javascript template
#
#-------------------------------------------------------------------------

_HTMLHEADER = '''<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" 
    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\" %(xmllang)s >
<html xmlns=\"http://www.w3.org/1999/xhtml\" >
<head>
 <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>
 <title>This is used to pass messages between javascript and python</title>
 <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\">
 %(css)s<script type=\"text/javascript\"'''

_JAVASCRIPT = '''<script>
 var gmarkers = []; var min = 0; var zoom = 0; var uzoom = 0;
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
'''

_HTMLTRAILER = '''
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

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoView(HtmlView):
    """
    The view used to render html pages.
    """
    def __init__(self, dbstate, uistate):
        HtmlView.__init__(self, dbstate, uistate, title=_("GeoView"))
        self.dbstate = dbstate
        self.uistate = uistate
        self.dbstate.connect('database-changed', self._new_database)
        self.usedmap = "openstreetmap"
        self.placeslist = []
        self.stylesheetlabel = []
        self.stylesheetdata = {}
        self.stylesheetlbl = None
        self.displaytype = "person"
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
        self.stylesheet = config.get('geoview.stylesheet')
        if ( self.stylesheet == "" ):
            self.stylesheet = CSS_FILES[0][1]
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
        self.years.pack_start(self.ylabel, True, True, padding=2)
        self.years.pack_start(self.yearsbox, True, True, padding=2)
        self.pages_selection = gtk.HBox()
        self.pages = []
        self.last_page = 1
        self.pages.append(gtk.Button("<<"))
        self.pages.append(gtk.Button("1")) # current page
        self.pages.append(gtk.Button(">>"))
        for page in self.pages:
            page.connect("clicked", self._ask_new_page)
            self.pages_selection.pack_start(page, False, False, padding=2)
        self.nocoord = gtk.Button("Unref") # don't translate
        self.nocoord.connect("clicked", self._show_places_without_coord)
        self.without_coord_file = os.path.join(GEOVIEW_SUBPATH,
                                               "without_coord.html")
        self.endinit = False
        self.generic_filter = None
        self.hpaned = gtk.HBox() # for filters
        self.filter.pack_start(self.hpaned, True, True)
        self.signal_map = {'place-add': self._place_changed,
                           'place-update' : self._place_changed}

    def _place_changed(self, handle_list):
        """
        One place changed. need to display it.
        """
        self.displaytype = "places"
        self._set_lock_unlock(True)
        self.filter_toggle(None, None, None, None)
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
        cell = gtk.CellRendererText()
        self.placebox = gtk.ComboBoxEntry(self.plist)# pylint: disable-msg=W0201
        self.placebox.pack_start(cell)
        self.placebox.add_attribute(self.placebox.get_cells()[0], 'text', 0)
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
        box.pack_start(self.placebox, False, False, padding=2)
        box.pack_start(self.pages_selection, False, False, padding=2)
        box.pack_start(self.nocoord, False, False, padding=2)
        box.pack_start(self.years, False, False, padding=2)
        box.show_all()
        self.title = gtk.Label('')
        self.title.set_single_line_mode(True)
        font = pango.FontDescription("monospace")
        font.set_weight(pango.WEIGHT_HEAVY)
        font.set_style(pango.STYLE_NORMAL)
        self.title.modify_font(font)
        self.box1.pack_start(box, False, False, padding=2)
        self.box1.pack_start(self.title, False, False, padding=2)
        self.box1.show_all()
        if self.displaytype == "places":
            self.build_filters_container(self.filter, PlaceSidebarFilter)
        elif self.displaytype == "event":
            self.build_filters_container(self.filter, EventSidebarFilter)
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
        found = "inconnu"
        if event.keyval == KEY_TAB:
            for place in self.plist:
                if prefix in place[0].lower():
                   count += 1
                   found = place[0]
        if count == 1:
            self.placebox.child.set_text(found)
        pass

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
        if widget == None:
            return
        if widget.get_active():
            self.last_year = widget
            self._set_markersonpage(widget)

    def _ask_new_page(self, widget, data=None): # pylint: disable-msg=W0613
        """
        Ask to select a new page when we are in a multi-pages map.
        """
        if widget == None:
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
        url = os.path.join(GEOVIEW_SUBPATH, "GeoV-%c-%05d.html" % (ftype,
                                                                   cpage))
        url = urlparse.urlunsplit( ('file', '', URL_SEP.join(url.split(os.sep)),
                                    '', ''))
        url += '?map=%s' % self.usedmap
        url += '&zoom=%d' % int(self.realzoom)
        url += '&lat=%s' % str(self.reallatitude)
        url += '&lon=%s' % str(self.reallongitude)
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
            index = 0
            for r_year in self.buttons:
                if self.last_selected_year == r_year[0]:
                    self.yearsbox.set_active(index)
                    self._call_js_selectmarkers(r_year[0])
                index += 1

    def _show_places_without_coord(self, widget): # pylint: disable-msg=W0613
        """
        Show the page which contains the list of all places without coordinates.
        """
        url = urlparse.urlunsplit( ('file', '',
                    URL_SEP.join(self.without_coord_file.split(os.sep)),
                    '', ''))
        self._openurl(url)

    def _entry_selected_place(self, combobox): # pylint: disable-msg=W0612
        """
        Ask to the renderer to show the info bubble.
        """
        place = combobox.get_text()
        for entry in self.placebox.get_model():
            if ( entry[0] == place ):
                # Is this entry in the current page ?
                if self.last_page == int(entry[2]):
                    # Yes, we don't need to load another page.
                    self._show_place_info_bubble(entry[1])
                    self._show_selected_places()
                else:
                    # No, we need to load the correct page
                    self.last_page = int(entry[2])
                    ftype = { "places":'P',
                              "event":'E',
                              "family":'F',
                              "person":'I'}.get( self.displaytype, 'X')
                    url = os.path.join(GEOVIEW_SUBPATH, "GeoV-%c-%05d.html" %
                                       (ftype, entry[2]))
                    url = urlparse.urlunsplit( ('file', '',
                                                URL_SEP.join(url.split(os.sep)),
                                               '', ''))
                    url += '?map=%s' % self.usedmap
                    url += '&zoom=%d' % int(self.realzoom)
                    url += '&lat=%s' % str(self.reallatitude)
                    url += '&lon=%s' % str(self.reallongitude)
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

    def _erase_placebox_selection(self, arg):
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
        config.set('geoview.lock',
                   self.lock_action.get_action('SaveZoom').get_active()
                   )
        if self.lock_action.get_action('SaveZoom').get_active():
            config.set('geoview.zoom', int(self.realzoom))
            config.set('geoview.latitude', self.reallatitude)
            config.set('geoview.longitude', self.reallongitude)
            config.set('geoview.map', self.displaytype)
        else:
            config.set('geoview.zoom', 0)
            config.set('geoview.latitude', "0.0")
            config.set('geoview.longitude', "0.0")
            config.set('geoview.map', "person")
        config.set('geoview.stylesheet', self.stylesheet)

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
        self._size_request_for_map(widget.parent, event)

    def _size_request_for_map(self, widget, event, data=None):
        # pylint: disable-msg=W0613
        """
        We need to resize the map
        """
        gws = widget.get_allocation()
        self.width = gws.width
        self.height = gws.height
        self.header_size = self.box1.get_allocation().height + 8
        if not self.uistate.get_active('Person'):
            return
        self.external_uri()

    def set_active(self):
        """
        Set view active when we enter into this view.
        """
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self._goto_active_person)
        self._goto_active_person()

    def set_inactive(self):
        """
        Set view inactive when switching to another view.
        """
        HtmlView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)

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
        if res: # Don't modify the current values if no db is loaded.
            start = 0
            try:
                title = ZOOMANDPOS.search(self.renderer.title, start)
                if title:
                    if self.realzoom != title.group(1):
                        self.realzoom = title.group(1)
                    if self.reallatitude != title.group(2):
                        self.reallatitude = title.group(2)
                    if self.reallongitude != title.group(3):
                        self.reallongitude = title.group(3)
            except:  # pylint: disable-msg=W0704
                pass # pylint: disable-msg=W0702
        if timeloop:
            gobject.timeout_add(timeloop, self._savezoomandposition, timeloop)

    def _do_we_need_to_zoom_between_map(self):
        """
        Look if we need to use the lasts zoom, latitude and longitude retrieved
        from the renderer, or if we must use the last ones we just created.
        """
        if self.reallatitude == None:
            self.reallatitude = 0.0
        if self.reallongitude == None:
            self.reallongitude = 0.0
        if not self.lock_action.get_action('SaveZoom').get_active():
            self.reallatitude = self.latit
            self.reallongitude = self.longt
            self.realzoom = self.zoom

    def _change_map(self, usedmap):
        """
        Tell the browser to change the current map.
        """
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
            url = urlparse.urlunsplit( ('file', '',
                                URL_SEP.join(self.htmlfile.split(os.sep)),
                                '', ''))
        url += '?map=%s' % usedmap
        url += '&zoom=%d' % int(self.realzoom)
        url += '&lat=%s' % str(self.reallatitude)
        url += '&lon=%s' % str(self.reallongitude)
        self._openurl(url)
        self._savezoomandposition()
        if self.displaytype != "places":
            # Need to wait the page is loaded to set the markers.
            gobject.timeout_add(1500, self._set_markersonpage, self.last_year)

    def _set_markersonpage(self, widget):
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

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="Refresh"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Provider"/>
              <toolitem action="SaveZoom"/>
              <toolitem action="AddPlace"/>
              <toolitem action="LinkPlace"/>
              <toolitem action="StyleSheet"/>
              <separator/>
              <toolitem action="PersonMaps"/>
              <toolitem action="FamilyMaps"/>
              <toolitem action="EventMaps"/>
              <toolitem action="AllPlacesMaps"/>
            </placeholder>
          </toolbar>
        </ui>'''

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. 
        """
        HtmlView._define_actions_fw_bw(self)
        self.forward_action.set_sensitive(False)
        self.back_action.set_sensitive(False)
        self._add_action('AddPlace', gtk.STOCK_ADD, 
            _('_Add Place'),
            callback=self._add_place,
            tip=_("Add the location centred on the map as a new place in "
                  "Gramps. Double click the location to centre on the map."))
        self._add_action('LinkPlace', 'gramps-place', 
            _('_Link Place'),
            callback=self._link_place,
            tip=_("Link the location centred on the map to a place in "
                  "Gramps. Double click the location to centre on the map."))
        self.provider_action = gtk.ActionGroup(self.title + "/Provider")
        self.provider_action.add_toggle_actions([
            ('Provider', 'gramps-geo-mainmap', _("_Provider"), "<ALT>P",
             _("Select the maps provider. You can choose "
               "between OpenStreetMap and Google maps"),
             self._change_provider,
             )
            ])
        self._add_action_group(self.provider_action)
        self.lock_action = gtk.ActionGroup(self.title + "/SaveZoom")
        self.lock_action.add_toggle_actions([
            ('SaveZoom', 'gramps-lock', _("_SaveZoom"), "<ALT>L",
             _("Save the zoom between places map, person map, "
               "family map and events map"),
             self._save_zoom,
             config.get('geoview.lock')
             )
            ])
        self._add_action_group(self.lock_action)
        self._add_action('AllPlacesMaps', gtk.STOCK_HOME, _('_All Places'),
        callback=self._all_places, tip=_("Attempt to view all places in "
                                         "the family tree."))
        self._add_action('PersonMaps', 'gramps-person', _('_Person'),
            callback=self._person_places,
            tip=_("Attempt to view all the places "
                  "where the selected people lived."))
        self._add_action('FamilyMaps', 'gramps-parents-add', _('_Family'),
            callback=self._family_places,
            tip=_("Attempt to view places of the selected people's family."))
        self._add_action('EventMaps', 'gramps-event', _('_Event'),
            callback=self._event_places,
            tip=_("Attempt to view places connected to all events."))
        self._add_toolmenu_action('StyleSheet', _('Selecting stylesheet ...'),
                        _("Reload the map with new style."),
                        self._gotostyle,
                        _('Select a StyleSheet'))
        self._add_toggle_action('Filter', None, _('_Filter'), 
                                callback=self.filter_toggle_action,
                                value=config.get('interface.filter'))
        config.connect('interface.filter',self.filter_toggle)

    def go_back(self, button): # pylint: disable-msg=W0613
        """
        Go to the previous loaded url.
        We need to set all the buttons insensitive.
        """
        self.box1.set_sensitive(False)
        self.renderer.window.go_back()

    def go_forward(self, button): # pylint: disable-msg=W0613
        """
        Go to the next loaded url.
        We need to set all the buttons sensitive if we cannot go forward.
        """
        self.renderer.window.go_forward()
        if not self.renderer.window.can_go_forward():
            self.box1.set_sensitive(True)

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
        PageView.change_page(self)
        # menutoolbutton actions are stored in PageView class, 
        # obtain the widgets where we need to add to menu
        actionstyles = self.action_toolmenu['StyleSheet']
        widgets = actionstyles.get_proxies()
        mmenu = self.__create_styles_menu_actions()

        if not self.stylesheetdata:
            return

        self.stylesheetlabel = []

        #store all gtk labels to be able to update label on selection change
        for widget in widgets :
            if isinstance(widget, gtk.MenuToolButton):
                widget.set_menu(mmenu)
                if gtk.pygtk_version >= (2, 12, 0):
                    widget.set_arrow_tooltip_text(actionstyles.arrowtooltip)
                lbl = gtk.Label(self._mapstyle_label())
                self.stylesheetlbl = lbl
                lbl.show()
                self.stylesheetlabel.append(lbl)
                widget.set_label_widget(self.stylesheetlabel[-1])
                widget.set_stock_id(gtk.STOCK_SELECT_FONT)
        self._set_lock_unlock_icon()
        self._set_mapstylelabel(self.stylesheet)
        self._savezoomandposition(500) # every 500 millisecondes
        self.endinit = True
        self.filter_toggle(None, None, None, None)
        self._geo_places()

    def __create_styles_menu_actions(self):
        """
        Function creating a menu and actions that are used as dropdown menu
        from the menutoolbutton
        """
        # disable msg=W0612 # i is unused
        # pylint: disable-msg=W0612
        menu = gtk.Menu()
        #select the stylesheets to show
        self.stylesheetdata = {}
        stylelist = []
        for style in CSS_FILES:
            stylelist.append([style[0], style[1]])
        for i, stylesheet in zip(range(len(stylelist)), stylelist):
            key = ""
            for word in stylesheet[0].split(' '):
                key += word.capitalize()
            key = key.replace(' ','')
            add_menuitem(menu, stylesheet[0], stylesheet[1] , 
                               _make_callback(self._set_mapstylesheet,
                                             stylesheet[1]))
            self.stylesheetdata[key] = [stylesheet[0], stylesheet[1]]
        return menu

    def _mapstyle_label(self):
        """
        return the current label for the menutoolbutton
        """
        return self.stylesheet

    def _set_mapstylesheet(self, obj):
        """
        Set the style of the map view
        """
        self.stylesheet = obj
        self._set_mapstylelabel(obj)

    def _set_mapstylelabel(self, obj):
        """
        Set the style label in the selection button.
        """
        for stylesheet in self.stylesheetdata.keys():
            if obj == self.stylesheetdata[stylesheet][1]:
                self.stylesheetlbl.set_text(self.stylesheetdata[stylesheet][0])

    def _gotostyle(self, obj): # pylint: disable-msg=W0613
        """
        Change the style of the map view
        """
        if not self.uistate.get_active('Person'):
            return
        self.filter_toggle(None, None, None, None)
        self._geo_places()

    def _goto_active_person(self, handle=None): # pylint: disable-msg=W0613
        """
        Here when the GeoView page is loaded
        """
        if not self.uistate.get_active('Person'):
            return
        self.filter_toggle(None, None, None, None)
        self._geo_places()

    def _all_places(self, hanle=None): # pylint: disable-msg=W0613
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self.build_filters_container(self.filter, PlaceSidebarFilter)
        self._geo_places()

    def _person_places(self, handle=None): # pylint: disable-msg=W0613
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        self.no_filter()
        if not self.uistate.get_active('Person'):
            return
        self._geo_places()

    def _family_places(self, hanle=None): # pylint: disable-msg=W0613 
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        self.no_filter()
        if not self.uistate.get_active('Person'):
            return
        self._geo_places()

    def _event_places(self, hanle=None): # pylint: disable-msg=W0613
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self.build_filters_container(self.filter, EventSidebarFilter)
        self._geo_places()

    def _new_database(self, db):
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
        self._change_db(db)
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])

    def _geo_places(self):
        """
        Specifies the places to display with mapstraction.
        """
        if not self.endinit:
            return
        if self.nbmarkers > 0 :
            # While the db is not loaded, we have 0 markers.
            self._savezoomandposition()
        self.nbmarkers = 0
        self.nbplaces = 0
        self.without = 0
        self.javascript_ready = False
        self._createmapstraction(self.displaytype)

    def _set_lock_unlock(self, state):
        """
        Change the lock/unlock state.
        """
        actionstyles = self.lock_action.get_action('SaveZoom')
        widgets = actionstyles.get_proxies()
        for widget in widgets :
            if isinstance(widget, gtk.ToggleToolButton):
                widget.set_active(state)
        self._set_lock_unlock_icon()

    def _set_lock_unlock_icon(self):
        """
        Change the lock/unlock icon depending on the button state.
        """
        actionstyles = self.lock_action.get_action('SaveZoom')
        widgets = actionstyles.get_proxies()
        for widget in widgets :
            if isinstance(widget, gtk.ToggleToolButton):
                if self.lock_action.get_action('SaveZoom').get_active():
                    widget.set_stock_id('gramps-lock')
                else:
                    widget.set_stock_id('gramps-unlock')

    def _save_zoom(self, button):
        """
        Do we change the zoom between maps ?
        It's not between maps providers, but between people, family,
        events or places map.
        When we unlock, we reload the page with our values.
        """
        if not button.get_active():
            self._change_map(self.usedmap)
        self._set_lock_unlock_icon()

    def _change_provider(self, button):
        """
        Toogle between the two maps providers.
        Inactive ( the default ) is openstreetmap.
        Active means Google maps.
        """
        if button.get_active():
            self.usedmap = "google"
        else:
            self.usedmap = "openstreetmap"
        self._change_map(self.usedmap)
        self._set_provider_icon()
        self._ask_year_selection(self.last_year)

    def _set_provider_icon(self):
        """
        Change the provider icon depending on the button state.
        """
        actionstyles = self.provider_action.get_action('Provider')
        widgets = actionstyles.get_proxies()
        for widget in widgets :
            if isinstance(widget, gtk.ToggleToolButton):
                if self.provider_action.get_action('Provider').get_active():
                    widget.set_stock_id('gramps-geo-altmap')
                else:
                    widget.set_stock_id('gramps-geo-mainmap')

    def _createpageplaceswithoutcoord(self):
        """
        Create a page with the list of all places without coordinates
        page.
        """
        data = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" \
                 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"  >
         <head>
          <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
          <title>%(title)s</title>
          %(css)s
         </head>
         <body >
           <H4>%(content)s<a href="javascript:history.go(-1)">%(back)s</a></H4>
        """ % { 'title'  : _('List of places without coordinates'),
                'content': _('Here is the list of all places in the family tree'
                             ' for which we have no coordinates.<br>'
                             ' This means no longitude or latitude.<p>'),
                'back'   : _('Back to prior page'),
                'css'    : self._add_stylesheet()
        }
        end = """
          </table>
         </body>
        </html>
        """
        ufd = open(self.without_coord_file, "w+")
        ufd.write(data)
        self.places = sorted(self.place_without_coordinates)
        i = 1
        ufd.write("<table border=1 ><th width=10%>NB</th>")
        ufd.write("<th width=20%>Gramps ID</th><th>Place</th>")
        for place in self.places:
            ufd.write("<tr><td>%d</td><td>%s</td><td>%s</td></tr>\n"
                     % ( i, place[0], place[1] ))
            i += 1
        ufd.write(end)
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
        adjust_before_min_year = config.get('behavior.date-before-range')
        adjust_after_max_year = config.get('behavior.date-after-range')
        self.minyear -= ( self.minyear - adjust_before_min_year ) % 10
        self.maxyear -= ( self.maxyear + adjust_after_max_year ) % 10
        self.yearint = adjust_after_max_year + \
                           ( self.maxyear - self.minyear ) / \
                           ( self.maxbut - 1 )
        self.yearint -= self.yearint % 10
        if self.yearint == 0:
            self.yearint = 10
        self.mapview.write("<script>\n")
        self.mapview.write(" var step = %s;\n" % self.yearint)
        self.mapview.write("</script>\n")
        self.mapview.write("</head>\n")
        self.mapview.write("<body>\n")
        self.years.hide()
        if h4mess:
            self.mapview.write("<h4>%s</h4>\n" % h4mess)
        else:
            if self.displaytype != "places":
                self._set_years_selection(self.minyear,
                                          self.yearint,
                                          self.maxyear)
                                          #self.maxyear + adjust_after_max_year)
                self.years.show()
        self.mapview.write("<div id=\"GOverviewMapControl_Helper\"")
        self.mapview.write(" style=\"height: %dpx; " %
                           (self.height - self.header_size ))
        self.mapview.write(" width: %dpx; display:none;\"\n" % self.width)
        self.mapview.write(" comment=\"just a work around a GOverview"
                           "MapControl() behaviour:\n")
        self.mapview.write("         some time the first non-class object will "
                           "be used to find the width\n")
        self.mapview.write("         because GOverviewMapControl() wants to be "
                           "most rigth the map jumps\n")
        self.mapview.write("         to the left (outside)\"")
        self.mapview.write("></div>\n")
        self.mapview.write("<div id='geo-map' class='Mapstraction' style=\"")
        if h4mess:
            self.mapview.write("display: none; ")
        self.mapview.write("height: %dpx\"></div>\n" % 
                           (self.height - self.header_size ))
        self.mapview.write("<script type=\"text/javascript\">\n")
        self.mapview.write(" args=getArgs();")
        self.mapview.write(" if (args.map) current_map=args.map;")
        self.mapview.write(" if (args.lat) ulat=args.lat;")
        self.mapview.write(" if (args.lon) ulon=args.lon;")
        self.mapview.write(" if (args.zoom) uzoom=parseInt(args.zoom);")
        self.mapview.write(" mapstraction = new Mapstraction")
        self.mapview.write("('geo-map',args.map);\n")
        self.mapview.write(" mapstraction.addControls(")
        self.mapview.write("{ pan: true, zoom: 'large', ")
        self.mapview.write("scale: true, map_type: true });\n")

    def _create_needed_javascript(self):
        """
        Create the needed javascript functions.
        """
        self.mapview.write(_JAVASCRIPT)
        #    _JAVASCRIPT.format(
        #        )
        #    )
        return

    def _createmapstractionheader(self, filename):
        """
        Create the html header of the page.
        """
        # disable msg=W0612 # modifier is unused
        # pylint: disable-msg=W0612
        self.mapview = open(filename, "w+")
        (lang_country, modifier ) = locale.getlocale()
        if lang_country == None:
            lang = "en"
        else:
            lang = lang_country.split('_')[0]
        self.mapview.write(
            _HTMLHEADER % {
                "xmllang" : "xml:lang=\"%s\"" % lang,
                "css": self._add_stylesheet()
                }
            )
        fpath = os.path.join(const.ROOT_DIR, 'mapstraction',
                                             #'mxn.js?(openlayers,google)')
                                             'mapstraction.js')
        upath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(fpath.split(os.sep)),
                                     '', ''))
        self.mapview.write(" src=\"%s\"></script>\n" % upath)
        self.mapview.write("<script type=\"text/javascript\"")
        self.mapview.write(" src=\"http://maps.google.com/")
        self.mapview.write("maps?file=api&v=2&hl=%s\"></script>\n" % lang ) 

    def _createmapstractiontrailer(self):
        """
        Add the last directives for the html page.
        """

        self.mapview.write(_HTMLTRAILER)
        #    _HTMLTRAILER.format(
        #        )
        #    )
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
            maxlong = abs(abs(self.minlon)-abs(self.maxlon))
        else:
            maxlong = abs(abs(self.minlon)+abs(self.maxlon))
        if signminlat == signmaxlat:
            maxlat = abs(abs(self.minlat)-abs(self.maxlat))
        else:
            maxlat = abs(abs(self.minlat)+abs(self.maxlat))
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
        pages = ( self.nbplaces / NB_MARKERS_PER_PAGE )
        if (self.nbplaces % NB_MARKERS_PER_PAGE ) != 0:
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
            filename = os.path.join(GEOVIEW_SUBPATH,
                                    "GeoV-%c-%05d.html" % 
                                              (ftype, self.nbpages))
            if self.nbpages == 1:
                self.htmlfile = filename
            self._createmapstractionheader(filename)
            self._create_needed_javascript()
            first = ( self.nbpages - 1 ) * NB_MARKERS_PER_PAGE 
            last = ( self.nbpages * NB_MARKERS_PER_PAGE ) - 1
            self._create_markers(ptype, first, last)
            self._show_title(h3mess)
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
                self._openurl(url)
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
            self._createmapstractionheader(os.path.join(GEOVIEW_SUBPATH,
                                                       "error.html"))
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
        found = 0
        for place_info in self.place_list:
            if place_info[0] == place:
                found = 1
                break
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
            value = value.replace("default","\" + default_icon + \"")
        ipath = os.path.join(const.ROOT_DIR, 'images/22x22/', '%s.png' % value )
        upath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(ipath.split(os.sep)), '', ''))
        self.mapview.write("my_marker.setIcon(\"%s\",[22,22],[0,22]);" % upath)
        self.mapview.write("my_marker.setShadowIcon(\"\");")

    def _show_title(self, title):
        """
        Show the current title map in the gtk label above the map.
        """
        self.title.set_text(title)

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
            self.mapview.write("  var point = new LatLonPoint")
            self.mapview.write("(ulat,ulon);")
            self.mapview.write("map.setCenterAndZoom")
            self.mapview.write("(point, uzoom);\n")
            self.setattr = False
        self.mapview.write("}\n")
        self.mapview.write(" function setmarkers(map) {\n")
        self.mapview.write("  if ( args.map != \"openstreetmap\" ) {")
        self.mapview.write(" default_icon = \"altmap\";")
        self.mapview.write(" } else { ")
        self.mapview.write(" default_icon = \"mainmap\"; }\n")
        differtype = False
        savetype = None
        index_mark = 0
        indm = firstm
        for mark in self.sort:
            index_mark += 1
            if index_mark < self.last_index:
                continue
            if ( indm >= firstm ) and ( indm <= lastm ):
                ininterval = True
            if ininterval:
                current = {
                            2 : [mark[3], mark[4]],
                          }.get(formatype, mark[0])
                if last != current:
                    if not divclose:
                        if ininterval:
                            self.mapview.write("</div>\");")
                            divclose = True
                        years = ""
                        if mark[2]:
                            for year in self.yearinmarker:
                                years += "%d " % year
                        years += "end"
                        self.mapview.write("my_marker.setAttribute")
                        self.mapview.write("('year','%s');" % years)
                        self.yearinmarker = []
                        self._set_icon(savetype, differtype, formatype)
                        differtype = False
                        self.mapview.write("map.addMarker(my_marker);")
                    if ( indm > lastm ):
                        if (indm % NB_MARKERS_PER_PAGE) == 0:
                            self.last_index = index_mark
                            ininterval = False
                    last = {
                             2 : [mark[3], mark[4]],
                           }.get(formatype, mark[0])
                    if ( indm >= firstm ) and ( indm <= lastm ):
                        ind = indm % NB_MARKERS_PER_PAGE
                        self.plist.append([ mark[0], ind, self.nbpages] )
                        indm += 1
                        self.mapview.write("\n  var point = new LatLonPoint")

                        self.mapview.write("(%s,%s);" % (mark[3], mark[4]))
                        self.mapview.write("my_marker = new Marker(point);")
                        self.mapview.write("gmarkers[%d]=my_marker;" % ind )
                        self.mapview.write("my_marker.setLabel")
                        self.mapview.write("(\"%s\");" % mark[0])
                        self.yearinmarker.append(mark[7])
                        divclose = False
                        differtype = False
                        if mark[8] and not differtype:
                            savetype = mark[8]
                        self.mapview.write("my_marker.setInfoBubble(\"<div ")
                        self.mapview.write("id='geo-info' >")
                        self.mapview.write("%s<br>" % mark[0])
                        if formatype == 1:
                            self.mapview.write("<br>%s" % mark[5])
                        elif formatype == 2:
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                        elif formatype == 3:
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                        elif formatype == 4:
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                else: # This marker already exists. add info.
                    if ( mark[8] and savetype != mark[8] ):
                        differtype = True
                    if indm > last:
                        divclose = True
                    else:
                        self.mapview.write("<br>%s - %s" % (mark[7], mark[5]))
                    ret = 1
                    for year in self.yearinmarker:
                        if year == mark[7]:
                            ret = 0
                    if (ret):
                        self.yearinmarker.append(mark[7])
            else:
                indm += 1
        if self.nbmarkers > 0 and ininterval:
            years = ""
            if mark[2]:
                for year in self.yearinmarker:
                    years += "%d " % year
            years += "end"
            self.mapview.write("</div>\");")
            self.mapview.write("my_marker.setAttribute('year','%s');" % years)
            self._set_icon(savetype, differtype, formatype)
            self.mapview.write("map.addMarker(my_marker);")
        if self.nbmarkers == 0:
            # We have no valid geographic point to center the map.
            longitude = 0.0
            latitude = 0.0
            self.mapview.write("\nvar point = new LatLonPoint")
            self.mapview.write("(%s,%s);\n" % (latitude, longitude))
            self.mapview.write("   map.setCenterAndZoom")
            self.mapview.write("(point, %d);\n" % 2)
            self.mapview.write("   my_marker = new Marker(point);\n")
            self.mapview.write("   my_marker.setLabel")
            self.mapview.write("(\"%s\");\n" % _("No location."))
            self.mapview.write("   my_marker.setInfoBubble(\"<div ")
            self.mapview.write("style='white-space:nowrap;' >")
            self.mapview.write(_("You have no places in your family tree "
                                 " with coordinates."))
            self.mapview.write("<br>")
            self.mapview.write(_("You are looking at the default map."))
            self.mapview.write("</div>\");\n")
            self._set_icon(None, True, 1)
            self.mapview.write("   map.addMarker(my_marker);")
        self.mapview.write("\n}")
        self.mapview.write("\n</script>\n")

    def _createpersonmarkers(self, dbstate, person, comment):
        """
        Create all markers for the specified person.
        """
        latitude = ""
        longitude = ""
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
                            descr1 = _("%(comment)s : birth place.") % {
                                                'comment': comment}
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
            latitude = ""
            longitude = ""
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
                            descr1 = _("%(comment)s : death place.") % {
                                                'comment': comment} 
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

        if self.generic_filter == None or not config.get('interface.filter'):
            places_handle = dbstate.db.iter_place_handles()
        else:
            places_handle = self.generic_filter.apply(dbstate.db, dbstate.db.iter_place_handles())
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

        if self.generic_filter == None or not config.get('interface.filter'):
            events_handle = dbstate.db.iter_event_handles()
        else:
            events_handle = self.generic_filter.apply(dbstate.db, dbstate.db.iter_event_handles())
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
                        descr2 = event.get_type()
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
                                      _("All %(name)s people's family places in the"
                                       " family tree with coordinates.") % {
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
                if event_ref.role != gen.lib.EventRoleType.PRIMARY:
                    # Only match primaries, no witnesses
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
            self._create_pages(ptype, "",
              _("Cannot center the map. No location with coordinates."
                "The following reasons are : <ul>"
                "<li>The active person has no places with coordinates.</li>"
                "<li>The active person's family members have no places "
                "with coordinates.</li><li>You have no places.</li>"
                "<li>You have no active person set.</li>"), 
              )
            self.box1.set_sensitive(False)
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
        return all the css styles sheet needed for GeoView.
        We use two styles sheets :
        The first one based on the default used by NarrativeWeb.
        The second one is specific to GeoView.
        """
        # Get the default stylesheet.
        dblp = "<link media=\"screen\" "
        delp = "type=\"text/css\" rel=\"stylesheet\" />\n"
        if self.stylesheet != "":
            cpath = os.path.join(const.ROOT_DIR,
                                 'data',
                                 '%s' % self.stylesheet
                                )
            dpath = urlparse.urlunsplit(('file', '',
                                         URL_SEP.join(cpath.split(os.sep)),
                                         '', ''))
            dcp = "href=\"%s\" " % dpath
        # Get the GeoView stylesheet.
        cpath = os.path.join(const.ROOT_DIR,
                             'data',
                             'GeoView.css'
                            )
        gpath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(cpath.split(os.sep)),
                                     '', ''))
        gcp = "href=\"%s\" " % gpath
        if self.stylesheet != "":
            return u'%s%s%s  %s%s%s' % (dblp, dcp, delp, dblp, gcp, delp)
        else:
            return u'%s%s%s' % (dblp, gcp, delp)
    
    def _openurl(self,url):
        """
        Here, we call really the htmlview and the renderer
        """
        if self.endinit:
            self.open(url)
            self.javascript_ready = True

    def _add_place(self,url):
        """
        Add a new place using longitude and latitude of location centred
        on the map
        """
        new_place = gen.lib.Place()
        new_place.set_latitude(str(self.reallatitude))
        new_place.set_longitude(str(self.reallongitude))
        try:
            EditPlace(self.dbstate, self.uistate, [], new_place)
        except Errors.WindowActiveError:
            pass

    def _link_place(self,url):
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
            except Errors.WindowActiveError:
                pass

    ####################################################################
    # Filters
    ####################################################################
    def build_filters_container(self, box, filter_class):
        """
        Used to create the filters on Geoview.
        Depending on the events view or places, view we must generate the
        good filter.
        We need to remove the old filter if it exists then add the new one.
        """
        try:
            self.vbox.destroy()
        except:  # pylint: disable-msg=W0704
            pass # pylint: disable-msg=W0702
        map(self.hpaned.remove, self.hpaned.get_children())
        self.vbox = gtk.VBox()
        self.hpaned.pack_start(self.vbox, True, True)
        self.filter_sidebar = filter_class(self.dbstate, self.uistate, 
                                           self.filter_clicked)
        self.filter_pane = self.filter_sidebar.get_widget()
        self.hpaned.pack_end(self.filter_pane, False, False)
        box.show_all()
        self.filter_toggle(None, None, None, None)

    def no_filter(self):
        """
        We don't need a filter for the current view.
        """
        try:
            self.filter_pane.hide()
        except:  # pylint: disable-msg=W0704
            pass # pylint: disable-msg=W0702

    def filter_toggle(self, client, cnxn_id, entry, data):
        """
        We must show or hide the filter depending on the filter toggle button.
        """
        if not self.endinit:
            return

        if self.displaytype == "places" or self.displaytype == "event":
            if config.get('interface.filter'):
                self.filter_pane.show()
            else:
                self.filter_pane.hide()

    def filter_toggle_action(self, obj):
        """
        Depending on the filter toggle button action, we must show or hile
        the filter then save the state in the config file.
        """
        if self.displaytype == "places" or self.displaytype == "event":
            if obj.get_active():
                self.filter_pane.show()
                active = True
            else:
                self.filter_pane.hide()
                active = False
            config.set('interface.filter', active)
            self.build_tree()

    def filter_clicked(self):
        """
        We have clicked on the Find button into the filter box.
        """
        self.generic_filter = self.filter_sidebar.get_filter()
        self.build_tree()

    def build_tree(self):
        """
        Builds the new view depending on the filter.
        """
        self._geo_places()
