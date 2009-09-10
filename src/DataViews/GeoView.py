# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Serge Noiraud
# Copyright (C) 2009  Helge GRAMPS
# Copyright (C) 2009  Josip
# Copyright (C) 2008  Benny Malengier
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
from gettext import gettext as _
import os
import urlparse
import const
import operator
import locale

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
import gen.lib
import Utils
import Config
from BasicUtils import name_displayer as _nd
from PlaceUtils import conv_lat_lon

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

from HtmlRenderer import HtmlView

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GEOVIEW_SUBPATH = Utils.get_empty_tempdir('geoview')
NB_MARKERS_PER_PAGE = 200

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------
def _alternate_map():
    """
    return the alternate name of the map provider.
    """
    if Config.get(Config.GEOVIEW_GOOGLEMAPS):
        alternate_map = "google"
    elif Config.get(Config.GEOVIEW_OPENLAYERS):
        alternate_map = "openlayers"
    elif Config.get(Config.GEOVIEW_YAHOO):
        alternate_map = "yahoo"
    elif Config.get(Config.GEOVIEW_MICROSOFT):
        alternate_map = "microsoft"
    return alternate_map

def _get_sign(value):
    """
    return 1 if we have a negative number, 0 in other case
    """
    if value < 0.0:
        return 1
    else:
        return 0

def _get_zoom_lat(value):
    zoomlat = 1
    for i, x in enumerate([80.0, 40.0, 20.0, 10.0, 3.0,
                           2.0, 1.0, 0.5, 0.2, 0.1]):
        if value < x:
            zoomlat = i+1
    return zoomlat + 2

def _get_zoom_long(value):
    zoomlong = 1
    for i, x in enumerate([120.0, 60.0, 30.0, 15.0, 7.0,
                           4.0, 2.0, 1.0, .5, .2, .1]):
        if value < x:
            zoomlong = i+1
    return zoomlong + 2

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
        HtmlView.__init__(self, dbstate, uistate, title=_('GeoView'))
        self.dbstate.connect('database-changed', self._new_database)
        self.usedmap = "openstreetmap"
        self.displaytype = "person"
        self.nbmarkers = 0
        self.without = 0
        self.nbpages = 0
        self.yearinmarker = []
        self.mustcenter = False
        self.centerlat = 0.0
        self.centerlon = 0.0
        self.setattr = True
        self.latit = 0.0
        self.longt = 0.0
        self.maxlat = 0.0
        self.maxlon = 0.0
        self.height = 0.0
        self.width = 0.0
        self.zoom = 1
        self.lock_action = None
        self.realzoom = 0
        self.reallatitude = 0.0
        self.reallongitude = 0.0
        if Config.get(Config.GEOVIEW_LOCKZOOM):
            self.realzoom = Config.get(Config.GEOVIEW_ZOOM)
            self.displaytype = Config.get(Config.GEOVIEW_MAP)
            self.reallatitude, self.reallongitude = conv_lat_lon(
                                    Config.get(Config.GEOVIEW_LATITUDE),
                                    Config.get(Config.GEOVIEW_LONGITUDE),
                                    "D.D8")
        self.minyear = 1
        self.maxyear = 1
        self.maxgen = 1
        self.mapview = None
        self.yearint = 0
        self.centered = True
        self.center = True
        self.place_list = []
        self.htmlfile = ""
        self.places = []
        self.sort = []
        self.without_coord_file = []
        self.place_without_coordinates = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.key_active_changed = None
 
    def top_widget(self):
        """
        The top widget to use, for GeoView, none
        """
        return gtk.Label()

    def on_delete(self):
        """
        We need to suppress temporary files here.
        Save the zoom, latitude, longitude and lock
        """
        self._savezoomandposition()
        Config.set(Config.GEOVIEW_LOCKZOOM,
                   self.lock_action.get_action('SaveZoom').get_active()
                   )
        if self.lock_action.get_action('SaveZoom').get_active():
            Config.set(Config.GEOVIEW_ZOOM, self.realzoom)
            Config.set(Config.GEOVIEW_LATITUDE, self.reallatitude)
            Config.set(Config.GEOVIEW_LONGITUDE, self.reallongitude)
            Config.set(Config.GEOVIEW_MAP, self.displaytype)
        else:
            Config.set(Config.GEOVIEW_ZOOM, 0)
            Config.set(Config.GEOVIEW_LATITUDE, "0.0")
            Config.set(Config.GEOVIEW_LONGITUDE, "0.0")
            Config.set(Config.GEOVIEW_MAP, "person")

    def init_parent_signals_for_map(self, widget, event):
        """
        Required to properly bootstrap the signal handlers.
        This handler is connected by build_widget.
        After the outside ViewManager has placed this widget we are
        able to access the parent container.
        """
        self.box.disconnect(self.bootstrap_handler)
        self.box.parent.connect("size-allocate", self._size_request_for_map)
        self._size_request_for_map(widget.parent, event)

    def _size_request_for_map(self, widget, event, data=None):
        """
        We need to resize the map
        """
        gws = widget.get_allocation()
        self.width = gws.width
        self.height = gws.height
        self.external_uri()
        if self.need_to_resize != True:
            try:
                self._geo_places()
            except:
                pass

    def set_active(self):
        """
        Set view active when we enter into this view.
        """
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.goto_active_person)

    def set_inactive(self):
        """
        Set view inactive when switching to another view.
        """
        HtmlView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)

    def _savezoomandposition(self):
        """
        The only way we have to save the zoom and position is to change the title
        of the html page then to get this title.
        When the title change, we receive a 'changed-title' signal.
        Then we can get the new title with the new values.
        """
        res = self.dbstate.db.get_researcher()
        if res: # Don't modify the current values if no db is loaded.
            start = 0
            try:
                title = ZOOMANDPOS.search(self.renderer.title, start)
                if title:
                    self.realzoom = title.group(1)
                    self.reallatitude = title.group(2)
                    self.reallongitude = title.group(3)
            except:
                pass

    def _change_map(self, usedmap):
        """
        Tell the browser to change the current map.
        """
        self.renderer.execute_script(
            "javascript:swap_map('"+usedmap+"','"+usedmap+"')")
        self._savezoomandposition()

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
              <toolitem action="OpenStreetMap"/>
              <toolitem action="%s"/>
              <toolitem action="SaveZoom"/>
              <separator/>
              <toolitem action="PersonMaps"/>
              <toolitem action="FamilyMaps"/>
              <toolitem action="EventMaps"/>
              <toolitem action="AllPlacesMaps"/>
            </placeholder>
          </toolbar>
        </ui>'''  % _alternate_map()

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. 
        """
        HtmlView._define_actions_fw_bw(self)
        self.forward_action.set_sensitive(False)
        self.back_action.set_sensitive(False)
        self._add_action('OpenStreetMap', 'gramps-geo-mainmap', 
                         _('_OpenStreetMap'),
                         callback=self._select_openstreetmap_map,
                         tip=_("Select OpenStreetMap Maps"))
        if Config.get(Config.GEOVIEW_GOOGLEMAPS):
            self._add_action('google', 'gramps-geo-altmap',
                             _('_Google Maps'),
                             callback=self._select_google_map,
                             tip=_("Select Google Maps."))
        elif Config.get(Config.GEOVIEW_OPENLAYERS):
            self._add_action('openlayers', 'gramps-geo-altmap',
                             _('_OpenLayers Maps'),
                             callback=self._select_openlayers_map,
                             tip=_("Select OpenLayers Maps."))
        elif Config.get(Config.GEOVIEW_YAHOO):
            self._add_action('yahoo', 'gramps-geo-altmap', 
                             _('_Yahoo! Maps'),
                             callback=self._select_yahoo_map,
                             tip=_("Select Yahoo Maps."))
        elif Config.get(Config.GEOVIEW_MICROSOFT):
            self._add_action('microsoft', 'gramps-geo-altmap',
                             _('_Microsoft Maps'),
                             callback=self._select_microsoft_map,
                             tip=_("Select Microsoft Maps"))
        self.lock_action = gtk.ActionGroup(self.title + '/SaveZoom')
        self.lock_action.add_toggle_actions([
            ('SaveZoom', 'gramps-lock', _("_SaveZoom"), "<ALT>L",
             _("Save the zoom between places map, person map, "
               "family map and events map"),
             self._save_zoom,
             Config.get(Config.GEOVIEW_LOCKZOOM)
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

    def goto_active_person(self, handle=None):
        """
        Here when the GeoView page is loaded
        """
        self._geo_places()

    def _all_places(self, hanle=None):
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self._geo_places()

    def _person_places(self, handle=None):
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        self._geo_places()

    def _family_places(self, hanle=None):
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        self._geo_places()

    def _event_places(self, hanle=None):
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self._geo_places()

    def _new_database(self, *args):
        """
        We just change the database.
        Restore the initial config. Is it good ?
        """
        if Config.get(Config.GEOVIEW_LOCKZOOM):
            self.realzoom = Config.get(Config.GEOVIEW_ZOOM)
            self.displaytype = Config.get(Config.GEOVIEW_MAP)
            self.reallatitude, self.reallongitude = conv_lat_lon(
                                    Config.get(Config.GEOVIEW_LATITUDE),
                                    Config.get(Config.GEOVIEW_LONGITUDE),
                                    "D.D8")

    def _geo_places(self):
        """
        Specifies the places to display with mapstraction.
        """
        if self.nbmarkers > 0 :
            # While the db is not loaded, we have 0 markers.
            self._savezoomandposition()
        self.external_url = False
        self.nbmarkers = 0
        self.without = 0
        self._createmapstraction(self.displaytype)
        self.open(urlparse.urlunsplit(
                           ('file', '',
                            URL_SEP.join(self.htmlfile.split(os.sep)),
                            '', '')))

    def _select_openstreetmap_map(self, handle):
        """
        Make openstreetmap the default map.
        """
        self.usedmap = "openstreetmap"        
        self._change_map("openstreetmap")

    def _select_openlayers_map(self, handle):
        """
        Make openstreetmap the default map.
        """
        self.usedmap = "openlayers"        
        self._change_map("openlayers")

    def _select_google_map(self, handle):
        """
        Specifies google is the default map
        """
        self.usedmap = "google"        
        self._change_map("google")

    def _select_yahoo_map(self, handle):
        """
        Make yahoo map the default map.
        """
        self.usedmap = "yahoo"        
        self._change_map("yahoo")

    def _select_microsoft_map(self, handle):
        """
        Make microsoft the default map.
        """
        self.usedmap = "microsoft"        
        self._change_map("microsoft")

    def _save_zoom(self, button):
        """
        Do we change the zoom between maps ?
        It's not between maps providers, but between people, family,
        events or places map.
        When we unlock, we reload the page with our values.
        """
        if not button.get_active():
            self._change_map(self.usedmap)

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
         </head>
         <body >
           <H4>%(content)s<a href="javascript:history.go(-1)">%(back)s</a></H4>
        """ % { 'title'  : _('List of places without coordinates'),
                'content': _('Here is the list of all places in the family tree'
                             ' for which we have no coordinates.<br>'
                             ' This means no longitude or latitude.<p>'),
                'back'   : _('Back to prior page')
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

    def _createmapstractionpostheader(self, h3mess, h4mess,
                                     maxpages, curpage, ftype):
        """
        This is needed to add infos to the header.
        This can't be in createmapstractionheader because we need
        to know something which is known only after some work.
        """
        self.maxgen = Config.get(Config.GENERATION_DEPTH)
        if self.maxyear == 0:
            self.maxyear = 2100
        if self.minyear == 9999:
            self.minyear = 1500
        period = (self.maxyear-self.minyear)
        intvl = (period/self.maxgen)
        modulo = intvl - ( intvl % 10 )
        if modulo == 0:
            modulo = 10
        self.minyear -= self.minyear % 10
        self.maxyear -= self.maxyear % 10
        self.yearint = (self.maxyear-self.minyear)/self.maxgen
        self.yearint -= self.yearint % modulo
        if self.yearint == 0:
            self.yearint = 10
        self.mapview.write("<script>\n")
        self.mapview.write("  var step = %s;\n" % self.yearint)
        self.mapview.write("</script>\n")
        self.mapview.write("</head>\n")
        self.mapview.write("<body >\n")
        if maxpages > 1:
            message = _("There are %d markers to display. They are split up "
                        "over %d pages of %d markers : " % (self.nbmarkers, 
                                            maxpages, NB_MARKERS_PER_PAGE))
            self.mapview.write(" <div id='pages' font=-4 >%s<br>\n" % message)
            if curpage != 1:
                priorfile = os.path.join(GEOVIEW_SUBPATH,
                                         "GeoV-%c-%05d.html" % 
                                                          (ftype, curpage-1))
                priorfile = urlparse.urlunsplit(
                                     ('file', '',
                                      URL_SEP.join(priorfile.split(os.sep)),
                                      '', ''))
                self.mapview.write("<a href='%s' >--</a>" % priorfile)
            else:
                self.mapview.write(" --")
            for page in range(1, maxpages+1, 1):
                if page == curpage:
                    self.mapview.write(" %d" % page)
                else:
                    if ( page < curpage + 11 ) and ( page > curpage - 11 ):
                        nextfile = os.path.join(GEOVIEW_SUBPATH,
                                                "GeoV-%c-%05d.html" % \
                                                 (ftype, page))
                        nextfile = urlparse.urlunsplit(
                                       ('file', '',
                                        URL_SEP.join(nextfile.split(os.sep)),
                                        '', ''))
                        self.mapview.write("\n<a href='%s' >%d</a>" %
                                           (nextfile, page))
            if curpage != maxpages:
                nextfile = os.path.join(GEOVIEW_SUBPATH,
                                       "GeoV-%c-%05d.html" % (ftype, curpage+1))
                nextfile = urlparse.urlunsplit(
                                    ('file', '',
                                     URL_SEP.join(nextfile.split(os.sep)),
                                     '', ''))
                self.mapview.write("\n<a href='%s' >++</a>" % nextfile)
            else:
                self.mapview.write(" ++")
            self.mapview.write("\n</div>\n")
            if self.without != 0:
                self.without_coord_file = os.path.join(GEOVIEW_SUBPATH,
                                                       "without_coord.html")
                self.mapview.write("<div id='coord' font=-4 >You have ")
                filename = urlparse.urlunsplit(
                           ('file', '',
                            URL_SEP.join(self.without_coord_file.split(os.sep)),
                            '', ''))
                self.mapview.write("<a href=\"%s\" >%d<a>" % \
                                   ( filename, self.without ) )
                self.mapview.write(" places without coordinates</div>\n" )
                self._createpageplaceswithoutcoord()
        if self.displaytype != "places":
            self.mapview.write("  <form method='POST' name='btns'>\n")
            self.mapview.write("  <input type='radio' ")
            self.mapview.write("name='years' value='All' checked\n")
            self.mapview.write("   onchange=\"selectmarkers")
            self.mapview.write("(\'All\')\"/>%s\n" % _("All"))
            for year in range(self.minyear, self.maxyear+self.yearint,
                              self.yearint):
                self.mapview.write("  <input type='radio' ")
                self.mapview.write("name='years' value=\'%s\'\n" %year)
                self.mapview.write("   onchange=\"selectmarkers")
                self.mapview.write("(\'%s\')\"/>%s\n" % ( year, year ))
            self.mapview.write("  </form>\n")
        self.mapview.write("<H3>%s</H3>" % h3mess)
        if h4mess:
            self.mapview.write("<H4>%s</H4>" % h4mess)
        margin = 10
        self.mapview.write("\n<div id=\"openstreetmap\" class=\"Mapstraction\"")
        self.mapview.write(" style=\"width: %dpx; " % (self.width - margin*4))
        self.mapview.write("height: %dpx\"></div>\n" % (self.height * 0.74))
        self.mapview.write("<div id=\"%s\" class=\"Mapstraction\"" % \
                           _alternate_map())
        self.mapview.write(" style=\"display: none; ")
        self.mapview.write("width: %dpx; height: %dpx\"></div>\n" % \
                           ((self.width - margin*4), (self.height * 0.74 )))
        self.mapview.write("<script type=\"text/javascript\">\n")
        self.mapview.write(" var mapstraction = new Mapstraction")
        self.mapview.write("('openstreetmap','openstreetmap');\n")
        self.mapview.write(" mapstraction.addControls(")
        self.mapview.write("{ pan: true, zoom: 'large', ")
        self.mapview.write("overview: true, scale: true, map_type: true });\n")

    def _create_needed_javascript(self):
        """
        Create the needed javascript functions.
        """
        self.mapview.write("<script>\n")
        self.mapview.write("  var gmarkers = [];\n")
        self.mapview.write("  var min = 0;\n")
        self.mapview.write("  var zoom = 0;\n")
        self.mapview.write("  var pos = 0;\n")
        self.mapview.write("  var selected = 0;\n")
        self.mapview.write("  var current_map = '%s';\n" % self.usedmap )
        self.mapview.write("  var selectedmarkers = 'All';\n")
        self.mapview.write("  // shows or hide markers of a ")
        self.mapview.write("particular category\n")
        self.mapview.write("  function selectmarkers(year) {\n")
        self.mapview.write("    selectedmarkers = year;\n")
        self.mapview.write("    for (var i=0; i<gmarkers.length; i++) {\n")
        self.mapview.write("      val = gmarkers[i].getAttribute")
        self.mapview.write("(\"year\");\n")
        self.mapview.write("      min = parseInt(year);\n")
        self.mapview.write("      max = min + step;\n")
        self.mapview.write("      if ( selectedmarkers == \"All\" ) ")
        self.mapview.write("{ min = 0; max = 9999; }\n")
        self.mapview.write("      gmarkers[i].hide();\n")
        self.mapview.write("      gmarkers[i].")
        self.mapview.write("closeBubble();\n")
        self.mapview.write("      years = val.split(' ');\n")
        self.mapview.write("      for ( j=0; j < years.length; j++) {\n")
        self.mapview.write("        if ( years[j] >= min ) {\n")
        self.mapview.write("          if ( years[j] < max ) {\n")
        self.mapview.write("            gmarkers[i].show();\n")
        self.mapview.write("          }\n")
        self.mapview.write("        }\n")
        self.mapview.write("      }\n")
        self.mapview.write("    }\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function savezoomandposition(mapstraction) {\n")
        self.mapview.write("    var t=setTimeout(\"savezoomandposition(")
        self.mapview.write("mapstraction)\",1000);\n")
        self.mapview.write("    nzoom = mapstraction.getZoom();\n")
        self.mapview.write("    nposition=mapstraction.getCenter();\n")
        self.mapview.write("    if ( ( nzoom != zoom ) || ")
        self.mapview.write("( nposition != pos )) {\n")
        self.mapview.write("      zoom = nzoom;\n")
        self.mapview.write("      pos = nposition;\n")
        self.mapview.write("      document.title = \"zoom=\" + zoom + \" ")
        self.mapview.write("coord=\" + pos + \":::\";\n")
        self.mapview.write("    }\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function removemarkers(mapstraction) {\n")
        self.mapview.write("    for ( m=0; m < gmarkers.length; m++) {\n")
        self.mapview.write("      mapstraction.removeMarker(gmarkers[m]);\n")
        self.mapview.write("    }\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function get_selected_radio() {\n")
        self.mapview.write("    selected = 0;\n")
        self.mapview.write("    for ( b=0; b < document.btns.years.length; ")
        self.mapview.write("b++) {\n      if ( document.btns.years[b].checked ")
        self.mapview.write("== true ) selected=b;\n")
        self.mapview.write("    }\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function set_selected_radio() {\n")
        self.mapview.write("    document.btns.years[selected].click();\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function reset_radio() {\n")
        self.mapview.write("    document.btns.years[0].click();\n")
        self.mapview.write("  }\n")
        self.mapview.write("  function swap_map(div,map) {\n")
        self.mapview.write("    savezoomandposition(mapstraction);\n")
        if self.displaytype != "places":
            self.mapview.write("    get_selected_radio();\n")
        self.mapview.write("    removemarkers(mapstraction);\n")
        self.mapview.write("    current_map=map;\n")
        self.mapview.write("    mapstraction.swap(div,map);\n")
        if self.displaytype != "places":
            self.mapview.write("    reset_radio();\n")
        self.mapview.write("    setmarkers(mapstraction);\n")
        self.mapview.write("    mapstraction.enableScrollWheelZoom();\n")

        if self.displaytype != "places":
            self.mapview.write("    set_selected_radio();\n")
        self.mapview.write("  }\n")

    def _createmapstractionheader(self, filename):
        """
        Create the html header of the page.
        """
        self.mapview = open(filename, "w+")
        self.mapview.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD")
        self.mapview.write(" XHTML 1.0 Strict//EN\" \n")
        self.mapview.write("   \"http://www.w3.org/TR/xhtml1/DTD/")
        self.mapview.write("xhtml1-strict.dtd\">\n")
        (lang_country, modifier ) = locale.getlocale()
        self.mapview.write("<html xmlns=\"http://www.w3.org/1999/xhtml\""
                           " lang=\"%s\" >\n" % lang_country)
        self.mapview.write("<head>\n")
        self.mapview.write(" <meta http-equiv=\"content-type\" ")
        self.mapview.write("content=\"text/html; charset=utf-8\"/>\n")
        self.mapview.write(" <meta http-equiv=\"Accept-Language\" ")
        self.mapview.write("content=\"%s\"/>\n" % lang_country.split('_')[0])
        self.mapview.write(" <meta http-equiv=\"Content-Language\" ")
        self.mapview.write("content=\"%s\"/>\n" % lang_country.split('_')[0])
        self.mapview.write(" <title>Geo Maps Java Script ")
        self.mapview.write("API for Gramps</title>\n")
        self.mapview.write(" <meta http-equiv=\"Content-Script-Type\" ")
        self.mapview.write("content=\"text/javascript\">\n")
        self.mapview.write("<script type=\"text/javascript\"\n" )
        fpath = os.path.join(const.ROOT_DIR,
                             'mapstraction',
                             'mapstraction.js')
        upath = urlparse.urlunsplit(('file', '',
                                     URL_SEP.join(fpath.split(os.sep)),
                                     '', ''))
        self.mapview.write("          src=\"%s\">\n" % upath)
        self.mapview.write("</script>\n")
        self.mapview.write("<script id=\"googleapiimport\" \n")
        self.mapview.write("        src=\"http://maps.google.com/")
        self.mapview.write("maps?file=api&v=2\"\n")
        self.mapview.write("        type=\"text/javascript\">\n")
        self.mapview.write("</script>\n")
        if _alternate_map() == "microsoft":
            self.mapview.write("<script type=\"text/javascript\"\n")
            self.mapview.write("        src=\"http://dev.virtualearth.net/")
            self.mapview.write("mapcontrol/mapcontrol.ashx?v=6\">\n")
            self.mapview.write("</script>\n")
        elif _alternate_map() == "yahoo":
            self.mapview.write("<script type=\"text/javascript\"\n")
            self.mapview.write("        src=\"http://api.maps.yahoo.com/")
            self.mapview.write("ajaxymap?v=3.0&appid=MapstractionDemo\" ")
            self.mapview.write("type=\"text/javascript\">\n")
            self.mapview.write("</script>\n")
        elif _alternate_map() == "openlayers":
            self.mapview.write("<script type=\"text/javascript\"\n")
            self.mapview.write("        src=\"http://openlayers.org/")
            self.mapview.write("api/OpenLayers.js\">\n")
            self.mapview.write("</script>\n")

    def _createmapstractiontrailer(self):
        """
        Add the last directives for the html page.
        """
        self.mapview.write(" setcenterandzoom(mapstraction);\n")
        self.mapview.write(" setmarkers(mapstraction);\n")
        self.mapview.write(" savezoomandposition(mapstraction);\n")
        self.mapview.write(" if ( current_map != \"openstreetmap\") {")
        self.mapview.write(" swap_map(current_map,current_map);")
        self.mapview.write(" };\n")
        self.mapview.write(" mapstraction.enableScrollWheelZoom();\n")
        self.mapview.write("</script>\n")
        self.mapview.write("</body>\n")
        self.mapview.write("</html>\n")
        self.mapview.close()

    def _set_center_and_zoom(self, ptype):
        """
        Calculate the zoom.
        """
        # Select the center of the map and the zoom
        self.centered = False
        if ptype == 2:
            # Sort by year for events
            self.sort = sorted(self.place_list, key=operator.itemgetter(7))
        else:
            # Sort by place
            self.sort = sorted(self.place_list)
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
        if zoomlat < zoomlong:
            self.zoom = zoomlat
        else:
            self.zoom = zoomlong
        self.zoom -= 1
        if self.zoom < 2:
            self.zoom = 2
        # We center the map on a point at the center of all markers
        self.centerlat = maxlat/2
        self.centerlon = maxlong/2
        latit = 0.0
        longt = 0.0
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
                if latit == 0.0 and longt == 0.0:
                    latit = 0.00000001
                    longt = 0.00000001
        self.mustcenter = False
        if latit != 0.0 or longt != 0.0:
            self.latit = latit
            self.longt = longt
            self.mustcenter = True

    def _create_pages(self, ptype, h3mess, h4mess):
        """
        Do we need to create a multi-pages document ?
        Do we have too many markers ?
        """
        nbmarkers = 0
        self.nbpages = 0
        pages = ( self.nbmarkers / NB_MARKERS_PER_PAGE ) + 1
        if (nbmarkers % NB_MARKERS_PER_PAGE) == 0:
            try:
                self._createmapstractiontrailer()
            except:
                pass
        self._set_center_and_zoom(ptype)
        for page in range(0, pages, 1):
            self.nbpages += 1
            if   ptype == 1:
                ftype = "P"
            elif ptype == 2:
                ftype = "E"
            elif ptype == 3:
                ftype = "F"
            elif ptype == 4:
                ftype = "I"
            else:
                ftype = "X"
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
            self._createmapstractionpostheader(h3mess, h4mess, 
                                              pages, self.nbpages, ftype)
            self._createmapstractiontrailer()
            if self.nbpages == 1:
                self.open(self.htmlfile)

    def _createmapstraction(self, displaytype):
        """
        Which kind of map are we going to create ?
        """
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
        self.place_without_coordinates.append([gid, place])
        self.without += 1

    def _append_to_places_list(self, place, evttype, name, lat, 
                              longit, descr, center, year):
        """
        Create a list of places with coordinates.
        """
        self.place_list.append([place, name, evttype, lat,
                                longit, descr, int(center), year])
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
        if tfa < 0.0:
            tfa -= 0.00000001
        else:
            tfa += 0.00000001
        if tfb < 0.0:
            tfb -= 0.00000001
        else:
            tfb += 0.00000001
        if self.minlat == 0.0:
            self.minlat = tfa
        if tfa < self.minlat:
            if tfa < 0.0:
                self.minlat = tfa
        if self.maxlat == 0.0:
            self.maxlat = tfa
        if tfa > self.maxlat:
            if tfa > 0.0:
                self.maxlat = tfa
        if self.minlon == 0.0:
            self.minlon = tfb
        if tfb < self.minlon:
            if tfb < 0.0:
                self.minlon = tfb
        if self.maxlon == 0.0:
            self.maxlon = tfb
        if tfb > self.maxlon:
            if tfb > 0.0:
                self.maxlon = tfb

    def _create_markers(self, format, firstm, lastm):
        """
        Create all markers for the specified person.
        """
        last = ""
        indm = 0
        divclose = True
        self.yearinmarker = []
        ininterval = False
        self.setattr = True
        self.mapview.write("  function setcenterandzoom(mapstraction) {\n")
        if self.mustcenter:
            self.centered = True
            self.mapview.write("   var point = new LatLonPoint")
            if self.lock_action.get_action('SaveZoom').get_active():
                self.mapview.write("(%s,%s);" % (self.reallatitude,
                                                 self.reallongitude))
            else:
                self.mapview.write("(%s,%s);" % (self.latit, self.longt))
            self.mapview.write("mapstraction.setCenterAndZoom")
            if self.lock_action.get_action('SaveZoom').get_active():
                self.mapview.write("(point, %s);\n" % self.realzoom)
            else:
                self.mapview.write("(point, %s);\n" % self.zoom)
            self.setattr = False
        self.mapview.write("}\n")
        self.mapview.write("  function setmarkers(mapstraction) {\n")
        for mark in self.sort:
            if ( indm >= firstm ) and ( indm <= lastm ):
                ininterval = True
            if ininterval:
                if last != mark[0]:
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
                        self.mapview.write("mapstraction.addMarker(my_marker);")
                    indm += 1
                    if ( indm > lastm ):
                        if (indm % NB_MARKERS_PER_PAGE) == 0:
                            ininterval = False
                    last = mark[0]
                    if ( indm >= firstm ) and ( indm <= lastm ):
                        self.mapview.write("\n   var point = new LatLonPoint")
                        self.mapview.write("(%s,%s);" % (mark[3], mark[4]))
                        self.mapview.write("my_marker = new Marker(point);")
                        self.mapview.write("gmarkers[%d]=my_marker;" % \
                                           (( indm - 1 ) % NB_MARKERS_PER_PAGE))
                        self.mapview.write("my_marker.setLabel")
                        self.mapview.write("(\"%s\");" % mark[0])
                        self.yearinmarker.append(mark[7])
                        divclose = False
                        self.mapview.write("my_marker.setInfoBubble(\"<div ")
                        self.mapview.write("style='white-space:nowrap;' >")
                        if format == 1:
                            self.mapview.write("%s<br>____________<br>" % \
                                               mark[0])
                            self.mapview.write("<br>%s" % mark[5])
                        elif format == 2:
                            self.mapview.write("%s____________<br>" % mark[1])
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                        elif format == 3:
                            self.mapview.write("%s<br>____________<br>" % \
                                               mark[0])
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                        elif format == 4:
                            self.mapview.write("%s<br>____________<br>" % \
                                               mark[0])
                            self.mapview.write("<br>%s - %s" % (mark[7],
                                                                mark[5]))
                else: # This marker already exists. add info.
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
            self.mapview.write("mapstraction.addMarker(my_marker);")
        if self.nbmarkers == 0:
            # We have no valid geographic point to center the map.
            # So you'll see the street where I live.
            # I think another place should be better :
            #          Where is the place where the gramps project began ?
            #
            # I think we should put here all gramps developpers.
            # not only me ...
            #
            longitude = 0.0
            latitude = 0.0
            self.mapview.write("\nvar point = new LatLonPoint")
            self.mapview.write("(%s,%s);\n" % (latitude, longitude))
            self.mapview.write("   mapstraction.setCenterAndZoom")
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
            self.mapview.write("   mapstraction.addMarker(my_marker);")
        self.mapview.write("\n}")
        self.mapview.write("\n</script>\n")

    def _createpersonmarkers(self, dbstate, person, comment):
        """
        Create all markers for the specified person.
        """
        latitude = ""
        longitude = ""
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = dbstate.db.get_event_from_handle(birth_ref.ref)
                birthdate = birth.get_date_object()
                birthyear = birthdate.get_year()
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    place = dbstate.db.get_place_from_handle(bplace_handle)
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
                                                        birthyear)
                            self.center = False
                        else:
                            self._append_to_places_without_coord(
                                 place.gramps_id, descr)
            latitude = ""
            longitude = ""
            death_ref = person.get_death_ref()
            if death_ref:
                death = dbstate.db.get_event_from_handle(death_ref.ref)
                deathdate = death.get_date_object()
                deathyear = deathdate.get_year()
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    place = dbstate.db.get_place_from_handle(dplace_handle)
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
                                                        deathyear)
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
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
        latitude = ""
        longitude = ""
        self.center = True
        for place_handle in dbstate.db.iter_place_handles():
            place = dbstate.db.get_place_from_handle( place_handle)
            if place:
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
                                                descr1, self.center, None)
                    self.center = False
                else:
                    self._append_to_places_without_coord(place.gramps_id,
                                                         descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
        else:
            mess = ""
        self._create_pages(1,
                           _("All places in the family tree with coordinates."),
                           mess)

    def _createmapstractionevents(self, dbstate):
        """
        Create one marker for each place associated with an event in the database
        which has a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
        latitude = ""
        longitude = ""
        self.center = True
        for event_handle in dbstate.db.get_event_handles():
            event = dbstate.db.get_event_from_handle( event_handle)
            if event:
                place_handle = event.get_place_handle()
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                descr1 = _("Id : %(id)s (%(year)s)") % {
                                'id' : event.gramps_id,
                                'year' : eventyear}
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude, longitude, 
                                                           "D.D8")
                        city = place.get_main_location().get_city()
                        country = place.get_main_location().get_country()
                        descr2 = "%s; %s" % (city, country)
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if ( longitude and latitude ):
                            person_list = [
                                dbstate.db.get_person_from_handle(ref_handle)
                                for (ref_type, ref_handle) in \
                                    dbstate.db.find_backlink_handles(
                                            event_handle)
                                        if ref_type == 'Person' 
                                          ]
                            if person_list:
                                descr = "<br>"
                                for person in person_list:
                                    descr = ("%(description)s%(name)s<br>") % {
                                                'description' : descr, 
                                                'name' : _nd.display(person)}
                                         #) % { 'eventtype': gen.lib.EventType(
                                descr = ("%(eventtype)s;"+
                                         " %(place)s%(description)s"
                                         ) % { 'eventtype': gen.lib.EventType(
                                                                event.get_type()
                                                                ),
                                               'place': place.get_title(), 
                                               'description': descr}
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
                                                        eventyear)
                            self.center = False
                        else:
                            descr = place.get_title()
                            self._append_to_places_without_coord(
                                 place.gramps_id, descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
        else:
            mess = ""
        self._create_pages(2,
                           _("All events in the family tree with coordinates."),
                           mess)

    def _createmapstractionfamily(self, dbstate):
        """
        Create all markers for each people of a family
        in the database which has a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
        self.center = True
        person = None
        if dbstate.active:
            person = dbstate.active
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0] # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                handle = fam.get_father_handle()
                father = dbstate.db.get_person_from_handle(handle)
                if father:
                    comment = _("Id : Father : %s") % father.gramps_id
                    self._createpersonmarkers(dbstate, father, comment)
                handle = fam.get_mother_handle()
                mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    comment = _("Id : Mother : %s") % mother.gramps_id
                    self._createpersonmarkers(dbstate, mother, comment)
                index = 0
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            index += 1
                            comment = _("Id : Child : %(id)s %(index)d") % {
                                            'id' : child.gramps_id,
                                            'index': index}
                            self._createpersonmarkers(dbstate, child, comment)
            else:
                comment = _("Id : Child : %(id)s has no parents.") % {
                                'id' : person.gramps_id }
                self._createpersonmarkers(dbstate, person, comment)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
            if person is not None:
                self._create_pages(3, _("The active person's family members "
                                        "have no places with coordinates."), 
                                   mess)
            else:
                self._create_pages(3, _("No active person set."), mess)
        else:
            mess = ""
            self._create_pages(3,
                               ( _("All %(name)s people's family places in the "
                                   "family tree with coordinates.") % {
                                     'name' :_nd.display(person) }),
                               mess)

    def _createmapstractionperson(self, dbstate):
        """
        Create all markers for each people's event in the database which has 
        a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
        latitude = ""
        longitude = ""
        person = None
        if dbstate.active:
            person = dbstate.active
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
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
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
                                                        eventyear)
                            self.center = False
                        else:
                            self._append_to_places_without_coord(
                                                        place.gramps_id, descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
            if person is not None:
                self._create_pages(4, 
                  _("The active person has no places with coordinates."), mess)
            else:
                self._create_pages(4, _("No active person set."), mess)
        else:
            mess = ""
            self._create_pages(4, ( _("All event places for %s.") % 
                                      _nd.display(person) ), mess)

    def _createmapnotimplemented(self):
        """
        Inform the user this work is not implemented.
        """
        self.mapview.write("  <H1>%s </H1>" % _("Not yet implemented ..."))

