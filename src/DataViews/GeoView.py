# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Serge Noiraud
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
from gettext import gettext as _
from cgi import escape
import math
import os
import tempfile
import urlparse
import const
import gobject
import threading
import time

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#import pdb

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".GeoView")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
import ViewManager
import PageView
import Utils
import Errors
import Config
from BasicUtils import name_displayer as _nd

#-------------------------------------------------------------------------
#
# Web interfaces
#
#-------------------------------------------------------------------------
WebKit = 0
try:
    import webkit
    WebKit = 1
except:
    pass
try:
    import gtkmozembed
    WebKit = 2
except:
    pass
#no interfaces present, raise Error so that options for GeoView do not show
if WebKit  == 0 :
    Config.set(Config.GEOVIEW, False)
    LOG.warning(_("GeoView not enabled, no html plugin for GTK found."))
    raise ImportError, 'No GTK html plugin found'

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
# I think we should set the two following variable in const.py
# They are used only with gtkmozembed.
MOZEMBED_PATH = "/tmp/"
MOZEMBED_SUBPATH = "browser-gramps"

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoView(PageView.PersonNavView):

    def __init__(self,dbstate,uistate):
        PageView.PersonNavView.__init__(self, _('GeoView'), dbstate, uistate)
        
        global WebKit
        if   (WebKit == 1): LOG.info("GeoView uses WebKit")
        elif (WebKit == 2): LOG.info("GeoView uses  gtkmozembed")

        self.dbstate = dbstate
        self.usedmap = "openstreetmap"
        self.displaytype = "person"
        self.minyear = int(9999)
        self.maxyear = int(0)

        # Create a temporary dot file
        (handle,self.htmlfile) = tempfile.mkstemp(".html","GeoV",
                                                  MOZEMBED_PATH )
        # needed to be solved. where to remove it ?

    def __del__(self):
        """
        How to do this the best way. We don't go here.
        We need to suppress this temporary file.
        """
        try:
            os.remove(self.htmlfile)
        except:
            pass

    #def _quit(self, widget):
    #    gtk.main_quit()

    #def change_page(self):
    #    self.uistate.clear_filter_results()

    def init_parent_signals_cb(self, widget, event):
        # required to properly bootstrap the signal handlers.
        # This handler is connected by build_widget. After the outside ViewManager
        # has placed this widget we are able to access the parent container.
        self.notebook.disconnect(self.bootstrap_handler)
        self.notebook.parent.connect("size-allocate", self.size_request_cb)
        self.size_request_cb(widget.parent,event)
        
    def add_table_to_notebook( self, table):
        frame = gtk.ScrolledWindow(None,None)
        frame = gtk.ScrolledWindow(None,None)
        frame.set_shadow_type(gtk.SHADOW_NONE)
        frame.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        frame.add_with_viewport(table)
        table.get_parent().set_shadow_type(gtk.SHADOW_NONE)
        table.set_row_spacings(1)
        table.set_col_spacings(0)
        try:
            self.notebook.append_page(frame,None)
        except:
            # for PyGtk < 2.4
            self.notebook.append_page(frame,gtk.Label(""))

    def set_active(self):
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.goto_active_person)
    
    def set_inactive(self):
        PageView.PersonNavView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)
        
    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-geo'

    def call(self):
        self.count = self.count+1
        gobject.idle_add(self.idle_call_js ,self.count)

    def idle_call_js(self,count):
        if   (self.browser == 1):
            self.m.execute_script("javascript:callFromPython("+str(count)+")");
            #self.m.zoom_in(); # make text bigger
        elif (self.browser == 2):
            self.m.load_url("javascript:callFromPython("+str(count)+")");
        elif (self.browser == 3):
            self.m.openURL("javascript:callFromPython("+str(count)+")");

    def change_map(self):
        if   (self.browser == 1):
            self.m.execute_script("javascript:mapstraction.swap(map,'"+self.usedmap+"')");
        elif (self.browser == 2):
            self.m.load_url("javascript:mapstraction.swap(map,'"+self.usedmap+"')");
        elif (self.browser == 3):
            self.m.openURL("javascript:mapstraction.swap(map,'"+self.usedmap+"')");

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        global WebKit

        self.tooltips = gtk.Tooltips()
        self.tooltips.enable()
       
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        
        self.table_2 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_2)
        gobject.threads_init()
        self.count = 0
        self.browser = 0

        if   (WebKit == 1) :
            # We use webkit
            self.browser=1
            self.m = webkit.WebView()
        elif (WebKit == 2) :
            # We use gtkmozembed
            self.browser=2
            if hasattr(gtkmozembed, 'set_profile_path'):
                set_profile_path = gtkmozembed.set_profile_path
            else:
                set_profile_path = gtkmozembed.gtk_moz_embed_set_profile_path
            if os.path.isdir(MOZEMBED_PATH+MOZEMBED_SUBPATH):
                pass
            else:
                os.system("mkdir -p "+MOZEMBED_PATH+MOZEMBED_SUBPATH)
            set_profile_path(MOZEMBED_PATH, MOZEMBED_SUBPATH)
            self.set_mozembed_proxy()
            self.m = gtkmozembed.MozEmbed()
            self.m.set_size_request(800, 600)

        if   (WebKit != 0) :
            self.table_2.add(self.m)
            self.geo_places(None,self.displaytype)
   
            self.m.show_all()

        return self.notebook

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        global WebKit
        if  (WebKit != 0 ):
            if Config.get(Config.GEOVIEW_GOOGLEMAPS):
                alternate_map = "GoogleMaps"
            elif Config.get(Config.GEOVIEW_OPENLAYERS):
                alternate_map = "OpenLayersMaps"
            elif Config.get(Config.GEOVIEW_YAHOO):
                alternate_map = "YahooMaps"
            elif Config.get(Config.GEOVIEW_MICROSOFT):
                alternate_map = "MicrosoftMaps"
            return '''<ui>
              <toolbar name="ToolBar">
                <placeholder name="CommonEdit">
                  <toolitem action="OpenStreetMap"/>
                  <toolitem action="%s"/>
                  <separator/>
                  <toolitem action="PersonMaps"/>
                  <toolitem action="FamilyMaps"/>
                  <toolitem action="EventMaps"/>
                  <toolitem action="AllPlacesMaps"/>
                </placeholder>
              </toolbar>
            </ui>'''  % alternate_map
        else:
            return '''<ui>
              <toolbar name="ToolBar">
                <placeholder name="CommonEdit">
                  <toolitem action="MissingKit"/>
                </placeholder>
              </toolbar>
            </ui>'''

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.

        Special action groups for Forward and Back are created to allow the
        handling of navigation buttons. Forward and Back allow the user to
        advance or retreat throughout the history, and we want to have these
        be able to toggle these when you are at the end of the history or
        at the beginning of the history.
        """
        global WebKit

        if  (WebKit != 0 ):
            self._add_action('OpenStreetMap', 'gramps-openstreetmap', _('_OpenStreetMap'),
                             callback=self.select_OpenStreetMap_map,
                             tip=_("Select OpenStreetMap Maps"))
            if Config.get(Config.GEOVIEW_GOOGLEMAPS):
                self._add_action('GoogleMaps', 'gramps-alternate-map',
                                 _('_Google Maps'),
                                 callback=self.select_google_map,
                                 tip=_("Select Google Maps. If possible, "
                                        "choose OpenStreetMap!"))
            elif Config.get(Config.GEOVIEW_OPENLAYERS):
                self._add_action('OpenLayersMaps', 'gramps-alternate-map',
                                 _('_OpenLayers Maps'),
                                 callback=self.select_openlayers_map,
                                 tip=_("Select OpenLayers Maps. If possible,"
                                        " choose OpenStreetMap"))
            elif Config.get(Config.GEOVIEW_YAHOO):
                self._add_action('YahooMaps', 'gramps-alternate-map', 
                                 _('_Yahoo! Maps'),
                                 callback=self.select_yahoo_map,
                                 tip=_("Select Yahoo Maps. If possible, choose"
                                        " OpenStreetMap"))
            elif Config.get(Config.GEOVIEW_MICROSOFT):
                self._add_action('MicrosoftMaps', 'gramps-alternate-map',
                                 _('_Microsoft Maps'),
                                 callback=self.select_microsoft_map,
                                 tip=_("Select Microsoft Maps. If possible,"
                                        " choose OpenStreetMap"))
    
            self._add_action('AllPlacesMaps', gtk.STOCK_HOME, _('_AllPlacesMaps'),
                             callback=self.all_places,
                             tip=_("Attempt to view all database places on the Map."))
            self._add_action('PersonMaps', 'gramps-person', _('_Person'),
                             callback=self.person_places,
                             tip=_("Attempt to view all the places where lived the selected people."))
            self._add_action('FamilyMaps', 'gramps-parents-add', _('_Family'),
                             callback=self.family_places,
                             tip=_("Attempt to view places on the Map of the selected people's family."))
            self._add_action('EventMaps', 'gramps-event', _('_Event'),
                             callback=self.event_places,
                             tip=_("Attempt to view places on the Map for all events."))
        else:
            self._add_action('MissingKit', gtk.STOCK_REMOVE, _('_MissingKit'),
                             callback=None,
                             tip=_("You can't use GeoView: webkit, gtkmozembed or gtkhtml missing"))
        PageView.PersonNavView.define_actions(self)

    def goto_active_person(self,handle=None):
        self.geo_places(self.htmlfile,self.displaytype)

    def all_places(self,handle=None):
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self.geo_places(self.htmlfile,self.displaytype)

    def person_places(self,handle=None):
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        self.geo_places(self.htmlfile,self.displaytype)

    def family_places(self,handle=None):
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        self.geo_places(self.htmlfile,self.displaytype)

    def event_places(self,handle=None):
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self.geo_places(self.htmlfile,self.displaytype)

    def geo_places(self,htmlfile,displaytype):
        """
        Specifies the places to display with mapstraction.
        """
        if htmlfile == None:
            htmlfile = MOZEMBED_PATH+"help.html"
            self.createHelp(htmlfile)
        else:
            self.createMapstraction(htmlfile,displaytype)
        LOG.debug("geo_places : in appel page")
        if   (self.browser == 1):
	    self.m.open("file://"+htmlfile)
        elif (self.browser == 2):
	    self.m.load_url("file://"+htmlfile)
        elif (self.browser == 3):
            self.m.openURL ("file://"+htmlfile);

        if   (self.browser != 0):
            self.m.show_all()

    def select_OpenStreetMap_map(self,handle=None):
        self.usedmap = "openstreetmap"
        LOG.debug("geo_places : call %s page from select_OpenStreetMap_map\n"
                                                % self.usedmap)
        self.change_map()

    def select_openlayers_map(self,handle=None):
        self.usedmap = "openlayers"
        LOG.debug("geo_places : call %s page from select_openlayers_map\n"
                                                 % self.usedmap)
        self.change_map()

    def select_google_map(self,handle=None):
        self.usedmap = "google"
        LOG.debug("geo_places : call %s page from select_google_map\n"
                                                 % self.usedmap)
        self.change_map()

    def select_yahoo_map(self,handle=None):
        self.usedmap = "yahoo"
        LOG.debug("geo_places : call %s page from select_yahoo_map\n"
                                                % self.usedmap)
        self.change_map()

    def select_microsoft_map(self,handle=None):
        self.usedmap = "microsoft"
        LOG.debug("geo_places : call %s page from select_microsoft_map\n"
                                                 % self.usedmap)
        self.change_map()

    def set_mozembed_proxy(self):
        """
        Try to see if we have some proxy environment variable.
        http_proxy in our case.
        The standard format is : http://[user:password@]proxy:port/
        This function is only used with gtkmozembed.
        """
        try:
            proxy = os.environ['http_proxy']
            data = ""
            if proxy:
                host_port = None
                parts = urlparse.urlparse(proxy)
                if not parts[0] or parts[0] == 'http':
                    host_port = parts[1]
                    t = host_port.split(':')
                    host = t[0].strip()
                    if host:
                        try:
                            port = int(t[1])
                        except:
                            user = host
                            u = t[1].split('@')
                            password = u[0]
                            host = u[1]
                            port = int(t[2])

                if port and host:
                    port = str(port)
                    data += 'user_pref("network.proxy.type", 1);\r\n'
                    data += 'user_pref("network.proxy.http", "'+host+'");\r\n'
                    data += 'user_pref("network.proxy.http_port", '+port+');\r\n'
                    data += 'user_pref("network.proxy.no_proxies_on", "127.0.0.1,localhost,localhost.localdomain");\r\n'
                    data += 'user_pref("network.proxy.share_proxy_settings", true);\r\n'
                    data += 'user_pref("network.http.proxy.pipelining", true);\r\n'
                    data += 'user_pref("network.http.proxy.keep-alive", true);\r\n'
                    data += 'user_pref("network.http.proxy.version", 1.1);\r\n'
                    data += 'user_pref("network.http.sendRefererHeader, 0);\r\n'
            fd = file(MOZEMBED_PATH+MOZEMBED_SUBPATH+"/prefs.js","w+")
            fd.write(data)
            fd.close()
        except:
            try: # tryng to remove pref.js in case of proxy change.
                os.remove(MOZEMBED_PATH+MOZEMBED_SUBPATH+"/prefs.js")
            except:
                pass
            pass   # We don't use a proxy or the http_proxy variable is not set.

    def createMapstractionPostHeader(self):
        self.maxgen=Config.get(Config.GENERATION_DEPTH)
        if self.maxyear == 0:
            self.maxyear=2100
        if self.minyear == 9999:
            self.minyear=1500
        period = (self.maxyear-self.minyear)
        intvl = (period/self.maxgen)
        modulo = intvl - ( intvl % 10 )
        if modulo == 0:
            modulo = 10
       
        self.minyear=( self.minyear - ( self.minyear % 10 ) )
        self.maxyear=( self.maxyear - ( self.maxyear % 10 ) )
        self.yearint=(self.maxyear-self.minyear)/self.maxgen
        self.yearint=( self.yearint - ( self.yearint % modulo ) )
        if self.yearint == 0:
            self.yearint=10
        LOG.debug("period = %d, intvl = %d, interval = %d" % (period,
                                            intvl, self.yearint))
        self.geo += "       var step = %s;\n" % self.yearint
        self.geo += "  </script>\n"
        self.geo += " </head>\n"
        self.geo += " <body >\n"
        if self.displaytype != "places":
            self.geo += " <Div id='btns' font=-2 >\n"
            self.geo += "  <form method='POST'>\n"
            self.geo += "  <input type='radio' name='years' value='All' checked\n"
            self.geo += "         onchange=\"selectmarkers(\'All\')\"/>All\n"
            for year in range(self.minyear,self.maxyear+self.yearint,self.yearint):
                self.geo += "  <input type='radio' name='years' value=\'%s\'\n" %year
                self.geo += "         onchange=\"selectmarkers(\'%s\')\"/>%s\n" % ( year, year )
            self.geo += "  </form></Div>\n"

    def createMapstractionHeader(self):
        self.geo = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
        self.geo += "         \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
        self.geo += "<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n"
        self.geo += " <head>\n"
        self.geo += "  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n"
        self.geo += "  <title>Geo Maps JavaScript API for Gramps</title>\n"
        self.geo += "  <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\">\n"
        self.geo += "  <script type=\"text/javascript\"\n" 
        self.geo += "          src=\"file://"+const.ROOT_DIR+"/mapstraction/mapstraction.js\">\n"
        self.geo += "  </script>\n"
        if self.usedmap == "microsoft":
            self.geo += "  <script type=\"text/javascript\"\n"
            self.geo += "          src=\"http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6\">\n"
            self.geo += "  </script>\n"
        elif self.usedmap == "yahoo":
            self.geo += "  <script type=\"text/javascript\"\n"
            self.geo += "          src=\"http://api.maps.yahoo.com/ajaxymap?v=3.0&appid=MapstractionDemo\" type=\"text/javascript\">\n"
            self.geo += "  </script>\n"
        elif self.usedmap == "openlayers":
            self.geo += "  <script type=\"text/javascript\"\n"
            self.geo += "          src=\"http://openlayers.org/api/OpenLayers.js\">\n"
            self.geo += "  </script>\n"
        else: # openstreetmap and google
            self.geo += "  <script id=\"googleapiimport\" \n"
            self.geo += "          src=\"http://maps.google.com/maps?file=api&v=2\"\n"
            self.geo += "          type=\"text/javascript\">\n"
            self.geo += "  </script>\n"
        self.geo += "  <script>\n"
        self.geo += "       var gmarkers = [];\n"
        self.geo += "       var min = 0;\n"
        self.geo += "       var selectedmarkers = 'All';\n"
        self.geo += "       // shows or hide markers of a particular category\n"
        self.geo += "       function selectmarkers(year) {\n"
        self.geo += "         selectedmarkers = year;\n"
        self.geo += "         for (var i=0; i<gmarkers.length; i++) {\n"
        self.geo += "           val = gmarkers[i].getAttribute(\"year\");\n"
        self.geo += "           min = parseInt(year);\n"
        self.geo += "           max = min + step;\n"
        self.geo += "           if ( selectedmarkers == \"All\" ) { min = 0; max = 9999; }\n"
        self.geo += "           gmarkers[i].hide();\n"
        if   self.usedmap == "microsoft":
            self.geo += ""
        elif self.usedmap == "yahoo":
            self.geo += ""
        elif self.usedmap == "openlayers":
            self.geo += ""
        else: # openstreetmap and google
            self.geo += "           gmarkers[i].map.closeInfoWindow();\n"
        self.geo += "           years = val.split(' ');\n"
        self.geo += "           for ( j=0; j < years.length; j++) {\n"
        self.geo += "               if ( years[j] >= min ) {\n"
        self.geo += "                   if ( years[j] < max ) {\n"
        self.geo += "                       gmarkers[i].show();\n"
        self.geo += "                   }\n"
        self.geo += "               }\n"
        self.geo += "           }\n"
        self.geo += "         }\n"
        self.geo += "       }\n"

    def createMapstractionTrailer(self,filename):
        self.geo += " </body>\n"
        self.geo += "</html>\n"
        fd = file(filename,"w+")
        fd.write(self.geo)
        fd.close()

    def createMapstraction(self,filename,displaytype):
        self.createMapstractionHeader()
        if displaytype == "places":
            self.createMapstractionPlaces(self.dbstate)
        elif displaytype == "family":
            self.createMapstractionFamily(self.dbstate)
        elif displaytype == "person":
            self.createMapstractionPerson(self.dbstate)
        elif displaytype == "event":
            self.createMapstractionEvents(self.dbstate)
        else:
            self.createMapstractionNotImplemented(self.dbstate)
        self.createMapstractionTrailer(filename)

    def append_to_places_list(self, Place, evttype, name, lat, long, descr, center, year):
        self.place_list.append([Place, name, evttype, lat, long, descr, int(center), year])

        a = float(lat)
        b = float(long)
        if not year == None:
            c = int(year)
            if c != 0:
                if c < self.minyear:
                    self.minyear = c
                if c > self.maxyear:
                    self.maxyear = c

        if self.minlat == 0.0:
            self.minlat = a
        if a < self.minlat:
            self.minlat = a
        if self.maxlat == 0.0:
            self.maxlat = a
        if a > self.maxlat:
            self.maxlat = a

        if self.minlon == 0.0:
            self.minlon = b
        if b < self.minlon:
            self.minlon = b
        if self.maxlon == 0.0:
            self.maxlon = b
        if b > self.maxlon:
            self.maxlon = b

    def isyearnotinmarker(self,allyears,year):
        ret = 1
        for y in allyears:
            if year == y:
                ret = 0
        return ret

    def create_markers(self,format):
        from PlaceUtils import conv_lat_lon
        self.centered = 0
        self.geo += "  <div id=\"map\" style=\"height: %dpx\"></div>\n" % 600
        self.geo += "  <script type=\"text/javascript\">\n"
        self.geo += "   var mapstraction = new Mapstraction('map','%s');\n"%self.usedmap
        self.geo += "   mapstraction.addControls({ pan: true, zoom: 'large', "
        self.geo += "overview: true, scale: true, map_type: true });\n"
        sort = sorted(self.place_list)
        last = ""
        indm=0
        divclose=1
        # Calculate the zoom. all places must be displayed on the map.
        if self.minlon < 0.0:
            signminlon=1
        else:
            signminlon=0
        if self.maxlon < 0.0:
            signmaxlon=1
        else:
            signmaxlon=0
        if self.minlat < 0.0:
            signminlat=1
        else:
            signminlat=0
        if self.maxlat < 0.0:
            signmaxlat=1
        else:
            signmaxlat=0
        if signminlon == signmaxlon: 
            maxlong=abs(abs(self.minlon)-abs(self.maxlon))
        else:
            maxlong=abs(abs(self.minlon)+abs(self.maxlon))
        if signminlat == signmaxlat:
            maxlat=abs(abs(self.minlat)-abs(self.maxlat))
        else:
            maxlat=abs(abs(self.minlat)+abs(self.maxlat))
        zoomlat=2
        LOG.debug( "self.maxlon = %f\n" % self.maxlon)
        LOG.debug("self.minlon = %f\n" % self.minlon)
        LOG.debug("self.maxlat = %f\n" % self.maxlat)
        LOG.debug("self.minlat = %f\n" % self.minlat)
        LOG.debug("signminlon = %f\n" % signminlon )
        LOG.debug("signmaxlon = %f\n" % signmaxlon )
        LOG.debug("signminlat = %f\n" % signminlat )
        LOG.debug("signmaxlat = %f\n" % signmaxlat )
        LOG.debug("maxlong = %f\n" % maxlong)
        LOG.debug("maxlat = %f\n" % maxlat)
        if maxlat < 80.0 :
            zoomlat = 3
        if maxlat < 40.0 :
            zoomlat = 4
        if maxlat < 20.0 :
            zoomlat = 5
        if maxlat < 10.0 :
            zoomlat = 6
        if maxlat < 3.0 :
            zoomlat = 7
        if maxlat < 2.0 :
            zoomlat = 8
        if maxlat < 1.0 :
            zoomlat = 9
        if maxlat < 0.5 :
            zoomlat = 10
        if maxlat < 0.2 :
            zoomlat = 11
        if maxlat < 0.1 :
            zoomlat = 12
        zoomlong=2
        if maxlong < 120.0 :
            zoomlong = 3
        if maxlong < 60.0 :
            zoomlong = 4
        if maxlong < 30.0 :
            zoomlong = 5
        if maxlong < 15.0 :
            zoomlong = 6
        if maxlong < 7.0 :
            zoomlong = 7
        if maxlong < 4.0 :
            zoomlong = 8
        if maxlong < 2.0 :
            zoomlong = 9
        if maxlong < 1.0 :
            zoomlong = 10
        if maxlong < 0.5 :
            zoomlong = 11
        if maxlong < 0.2 :
            zoomlong = 12
        if maxlong < 0.1 :
            zoomlong = 13
        if zoomlat < zoomlong:
           self.zoom = zoomlat
        else:
           self.zoom = zoomlong
        LOG.debug("zoomlat = %f\n" % zoomlat)
        LOG.debug("zoomlong = %f\n" % zoomlong)
        LOG.debug("self.zoom = %f\n" % self.zoom)
        # We could center the map on a point at the center of all markers
        centerlat = maxlat/2
        centerlon = maxlong/2
        self.mustcenter = False
        yearinmarker = []
        for mark in sort:
            if last != mark[0]:
                years=""
                if last != "":
                    self.geo += "</div>\");\n"
                    if mark[2]:
                        for y in yearinmarker:
                            years += "%d " % y
                    years += "end"
                    self.geo += "   my_marker.setAttribute('year','%s');\n" % years
                    yearinmarker = []
                    years=""
                    self.geo += "   mapstraction.addMarker(my_marker);\n"
                    if self.mustcenter == True:
                        self.centered = 1
                        self.geo += "   var point = new LatLonPoint(%s,%s);\n"%(self.latit,self.longt)
                        self.geo += "   mapstraction.setCenterAndZoom(point, %s);\n"%self.zoom
                        self.mustcenter = False
                    if mark[2]:
                        self.geo += "   // map locations for %s;\n"%mark[1]
                    else:
                        self.geo += "   // map locations for %s;\n"%mark[0]
                last = mark[0]
                cent=int(mark[6])
                if (cent == 1):
                    self.centered = 1
                    #pdb.set_trace()
                    if ( signminlat == 1 and signmaxlat == 1 ):
                        latit = self.maxlat+centerlat
                        LOG.debug("latit 1 : %f" % self.maxlat)
                    elif ( signminlat == 0 and signmaxlat == 0 ): 
                        latit = self.maxlat-centerlat
                        LOG.debug("latit 2 : %f" % self.maxlat)
                    else:
                        latit = self.maxlat+centerlat
                        LOG.debug("latit 3 : %f" % self.maxlat)
                    if ( signminlon == 1 and signmaxlon == 1 ):
                        longt = self.maxlon-centerlon
                        LOG.debug("longt 1 : %f" % self.maxlon)
                    elif ( signminlon == 0 and signmaxlon == 0 ): 
                        longt = self.maxlon+centerlon
                        LOG.debug("longt 2 : %f" % self.maxlon)
                    else:
                        longt = self.maxlon-centerlon
                        LOG.debug("longt 3 : %f" % self.maxlon)

                    LOG.debug("latitude centree = %s\n" % latit)
                    LOG.debug("longitude centree = %s\n" % longt)
                    self.geo += "   var point = new LatLonPoint(%s,%s);\n"%(latit,longt)
                    self.geo += "   mapstraction.setCenterAndZoom(point, %s);\n"%self.zoom
                self.geo += "   var point = new LatLonPoint(%s,%s);\n"%(mark[3],mark[4])
                self.geo += "   my_marker = new Marker(point);\n"
                self.geo += "   gmarkers[%d]=my_marker;\n" % indm
                indm+=1;
                self.geo += "   my_marker.setLabel(\"%s\");\n"%mark[0]
                yearinmarker.append(mark[7])
                divclose=0
                self.geo += "   my_marker.setInfoBubble(\"<div style='white-space:nowrap;' >"
                if format == 1:
                    self.geo += "%s<br>____________<br><br>%s"%(mark[0],mark[5])
                elif format == 2:
                    self.geo += "%s<br>____________<br><br>%s - %s"%(mark[1],mark[7],mark[5])
                elif format == 3:
                    self.geo += "%s<br>____________<br><br>%s - %s"%(mark[0],mark[7],mark[5])
                elif format == 4:
                    self.geo += "%s<br>____________<br><br>%s - %s"%(mark[0],mark[7],mark[5])
            else: # This marker already exists. add info.
                self.geo += "<br>%s - %s" % (mark[7], mark[5])
                if self.isyearnotinmarker(yearinmarker,mark[7]):
                    yearinmarker.append(mark[7])
                cent=int(mark[6])
                if (cent == 1):
                    self.centered = 1
                    if float(mark[3]) == self.minlat:
                        if signminlat == 1: 
                            latit = str(float(mark[3])+centerlat)
                            LOG.debug("latit 1 1")
                        else:
                            latit = str(float(mark[3])-centerlat)
                            LOG.debug("latit 2 1")
                    else:
                        if signminlat == 1: 
                            latit = str(float(mark[3])-centerlat)
                            LOG.debug("latit 3 1")
                        else:
                            latit = str(float(mark[3])+centerlat)
                            LOG.debug("latit 4 1")
                    if float(mark[4]) == self.minlon:
                        if signminlon == 1:
                            longt = str(float(mark[4])+centerlon)
                            LOG.debug("longt 1 1")
                        else:
                            longt = str(float(mark[4])-centerlon)
                            LOG.debug("longt 2 1")
                    else:
                        if signminlon == 1:
                            longt = str(float(mark[4])-centerlon)
                            LOG.debug("longt 3 1")
                        else:
                            longt = str(float(mark[4])+centerlon)
                            LOG.debug("longt 4 1")
                    self.mustcenter = True
        if divclose == 0:
            self.geo += "</div>\");\n"
            if mark[2]:
                for y in yearinmarker:
                    years += "%d " % y
            years += "end"
            self.geo += "   my_marker.setAttribute('year','%s');\n" % years
            yearinmarker = []
            years=""
            self.geo += "   mapstraction.addMarker(my_marker);\n"
            if self.mustcenter == True:
                self.centered = 1
                self.geo += "   var point = new LatLonPoint(%s,%s);\n"%(self.latit,self.longt)
                self.geo += "   mapstraction.setCenterAndZoom(point, %s);\n"%self.zoom
        if ( self.centered == 0 ):
            # We have no valid geographic point to center the map.
            # So you'll see the street where I live.
            # I think another place should be better :
            #          Where is the place where the gramps project began ?
            #
            # I think we should put here all gramps developpers.
            # not only me ...
            #
            longitude = -1.568792
            latitude = 47.257971
            self.geo += "   var point = new LatLonPoint(%s,%s);\n"%(latitude,longitude)
            self.geo += "   mapstraction.setCenterAndZoom(point, %d);\n"%2
            self.geo += "   my_marker = new Marker(point);\n"
            self.geo += "   my_marker.setLabel(\"%s\");\n"%_("The author of this module.")
            self.geo += "   my_marker.setInfoBubble(\"<div style='white-space:nowrap;' >"
            self.geo += "Serge Noiraud<br>Nantes, France<br>"
            self.geo += "%s</div>\");\n"%_("This request has no geolocation associated.")
            self.geo += "   mapstraction.addMarker(my_marker);\n"
        self.geo += "  </script>\n"

    def createPersonMarkers(self,db,person,comment):
        """
        This function create all markers for the specified person.
        """
        latitude = ""
        longitude = ""
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = db.db.get_event_from_handle(birth_ref.ref)
                birthdate = birth.get_date_object()
                birthyear = birthdate.get_year()
                LOG.debug("birth year = %s" % birthyear)
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    place = db.db.get_place_from_handle(bplace_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    if comment:
                        descr1=comment+" : "+_("birth place.")
                    else:
                        descr1=_("birth place.")
                    descr = place.get_title()
                    city = place.get_main_location().get_city()
                    country = place.get_main_location().get_country()
            if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                self.append_to_places_list(descr, gen.lib.EventType.BIRTH, 
                                           _nd.display(person), latitude, longitude,
                                           descr1, int(self.center), birthyear)
                self.center = 0
            latitude = ""
            longitude = ""
            death_ref = person.get_death_ref()
            if death_ref:
                death = db.db.get_event_from_handle(death_ref.ref)
                deathdate = death.get_date_object()
                deathyear = deathdate.get_year()
                LOG.debug("death year = %s" % deathyear)
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    place = db.db.get_place_from_handle(dplace_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    descr = place.get_title()
                    if comment:
                        descr1=comment+" : "+_("death place.")
                    else:
                        descr1=_("death place.")
                    city = place.get_main_location().get_city()
                    country = place.get_main_location().get_country()
            if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                self.append_to_places_list(descr, gen.lib.EventType.DEATH,
                                           _nd.display(person), latitude, longitude,
                                           descr1, int(self.center), deathyear)
                self.center = 0

    def createMapstractionPlaces(self,db):
        """
        This function create the marker for each place in the database
        which has a lat/lon.
        """
        self.place_list = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
 
        latitude = ""
        longitude = ""
        person = db.db.get_default_person()
        if not person:
            person = db.active
        self.center = 1
        for place_handle in db.db.get_place_handles():
            place = db.db.get_place_from_handle( place_handle)
            if place:
                descr = place.get_title()
                descr1 = _("Id : %s")%place.gramps_id
                longitude = place.get_longitude()
                latitude = place.get_latitude()
                city = place.get_main_location().get_city()
                country = place.get_main_location().get_country()
                if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                    self.append_to_places_list(descr, None,
                                               _nd.display(person),
                                               latitude, longitude,
                                               descr1, self.center, None)
                    self.center = 0
        self.createMapstractionPostHeader()
        self.geo += "  <H3>%s</H3>"%_("All places in the database with coordinates.")
        if self.center == 1:
            self.geo += "  <H4>%s</H4>"%_("Cannot center the map. No selected location.")
        self.create_markers(1)

    def createMapstractionEvents(self,db):
        """
        This function create one marker for each place associated with an event in the database
        which has a lat/lon.
        """
        self.place_list = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
 
        latitude = ""
        longitude = ""
        person = db.db.get_default_person()
        if not person:
            person = db.active
        self.center = 1
        for event_handle in db.db.get_event_handles():
            event = db.db.get_event_from_handle( event_handle)
            if event:
                pl_id = event.get_place_handle()
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                descr1 = _("Id : %s (%s)")%(event.gramps_id,eventyear)
                if pl_id:
                    place = db.db.get_place_from_handle(pl_id)
                    #ref = db.db.get_person_from_handle(event)
                    #
                    # question :
                    # how to obtain the list of the people referenced by this event ?
                    #
                    refs = event.get_referenced_handles_recursively()
                    if refs:
                        print refs
                        for ref in refs:
                            person = db.db.get_person_from_handle(ref)
                            #descr = _("%s; %s for %s") % (gen.lib.EventType(event.get_type()),place.get_title(), _nd.display(person))
                            descr = "inconnu"
                    else:
                        descr = _("%s; %s") % (gen.lib.EventType(event.get_type()),place.get_title())
                    #descr = place.get_title()
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    city = place.get_main_location().get_city()
                    country = place.get_main_location().get_country()
                    descr2 = _("%s; %s") % (city,country)
                    if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                        self.append_to_places_list(descr1, descr,
                                                   descr,
                                                   latitude, longitude,
                                                   descr2, self.center, eventyear)
                        self.center = 0
        self.createMapstractionPostHeader()
        self.geo += "  <H3>%s</H3>"%_("All events in the database with coordinates.")
        if self.center == 1:
            self.geo += "  <H4>%s</H4>"%_("Cannot center the map. No selected location.")
        self.create_markers(2)

    def createMapstractionFamily(self,db):
        """
        This function create all markers for each people of a family
        in the database which has a lat/lon.
        """
        self.place_list = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)
        self.center = 1
        if db.active:
            person = db.active
        if person:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0] # first is primary
                fam = db.db.get_family_from_handle(fhandle)
                father_handle = fam.get_father_handle()
                father = db.db.get_person_from_handle(father_handle)
                if father:
                    comment = "Id : %s : %s"%(father.gramps_id,_("Father"))
                    self.createPersonMarkers(db,father,comment)
                mother_handle = fam.get_mother_handle()
                mother = db.db.get_person_from_handle(mother_handle)
                if mother:
                    comment = "Id : %s : %s"%(mother.gramps_id,_("Mother"))
                    self.createPersonMarkers(db,mother,comment)
                index = 0
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = db.db.get_person_from_handle(child_ref.ref)
                        if child:
                            index += 1
                            comment = "Id : %s : %s %d"%(child.gramps_id,
                                                         _("Child"),index)
                            self.createPersonMarkers(db,child,comment)
        self.createMapstractionPostHeader()
        self.geo += "  <H3>%s</H3>"%_("All %s people's family places in the database with coordinates.") % _nd.display(person)
        if self.center == 1:
            self.geo += "  <H4>%s</H4>"%_("Cannot center the map. No selected location.")
        self.create_markers(3)

    def createMapstractionPerson(self,db):
        """
        This function create all markers for each people's event
        in the database which has a lat/lon.
        """
        self.place_list = []
        self.minlat = float(0.0)
        self.maxlat = float(0.0)
        self.minlon = float(0.0)
        self.maxlon = float(0.0)
        self.minyear = int(9999)
        self.maxyear = int(0)

        latitude = ""
        longitude = ""
        if db.active:
            person = db.active
        self.center = 1
        if person:
            # For each event, if we have a place, set a marker.
            LOG.debug("event for %s" % person.gramps_id)
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                if event_ref.role != gen.lib.EventRoleType.PRIMARY:
                    # Only match primaries, no witnesses
                    continue
                event = db.db.get_event_from_handle(event_ref.ref)
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                LOG.debug("event year = %s" % eventyear)
                place_handle = event.get_place_handle()
                if place_handle:
                    place = db.db.get_place_from_handle(place_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    descr = place.get_title()
                    city = place.get_main_location().get_city()
                    country = place.get_main_location().get_country()
                    evt=gen.lib.EventType(event.get_type())
                    descr1=_("%s : %s")%(evt,_nd.display(person))
                    if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                        self.append_to_places_list(descr, evt,
                                                   _nd.display(person),
                                                   latitude, longitude,
                                                   descr1, self.center, eventyear)
                        self.center = 0
        self.createMapstractionPostHeader()
        self.geo += "  <H3>%s</H3>"%_("All event places for %s.") % _nd.display(person)
        if self.center == 1:
            self.geo += "  <H4>%s</H4>"%_("Cannot center the map. No selected location.")
        self.create_markers(4)

    def createMapstractionNotImplemented(self,db):
        """
        This function is used to inform the user this work is not implemented.
        """
        LOG.warning('createMapstractionNotImplemented')
        self.geo += "  <H1>%s ...</H1>"%_("Not yet implemented")

    def createHelp(self,filename):
        tmpdir = MOZEMBED_PATH
        geo = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
        geo += "         \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
        geo += "<html xmlns=\"http://www.w3.org/1999/xhtml\"  >\n"
        geo += " <head>\n"
        geo += "  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n"
        geo += "  <title>Geo Maps JavaScript API for Gramps</title>\n"
        geo += " </head>\n"
        geo += " <body >\n"
        geo += "  <div id=\"map\" style=\"height: %dpx\">\n" % 600
        geo += "   <br><br><br><br><br>\n"
        geo += "   <H4>"
        geo += _("You can choose between two maps. One free and a second one.")
        geo += "   <br>"
        geo += _("The best choice is the free map like openstreetmap.")
        geo += "   <br>"
        geo += _("You should use the second map only if the first one give no results ...")
        geo += "   <br>"
        geo += _("You can select Edit/Preferences to choose the second map provider.")
        geo += "   <br>"
        geo += _("They are : Googlemaps, Yahoo! maps, Microsoft maps and Openlayers.")
        geo += "   </H4>"
        geo += "  </div>\n"
        geo += " </body>\n"
        geo += "</html>\n"
        fd = file(filename,"w+")
        fd.write(geo)
        fd.close()
