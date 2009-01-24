# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Serge Noiraud
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
import operator

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
import PageView
import Utils
import Config
from const import TEMP_DIR
from BasicUtils import name_displayer as _nd
from PlaceUtils import conv_lat_lon

#-------------------------------------------------------------------------
#
# Web interfaces
#
#-------------------------------------------------------------------------

NOWEB  = 0
WEBKIT = 1
MOZIL  = 2

WebKit = NOWEB
try:
    import webkit
    WebKit = WEBKIT
except:
    pass

if WebKit == NOWEB:
    try:
        import gtkmozembed
        WebKit = MOZIL
    except:
        pass

#no interfaces present, raise Error so that options for GeoView do not show
if WebKit == NOWEB :
    Config.set(Config.GEOVIEW, False)
    raise ImportError, 'No GTK html plugin found'

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
# I think we should set the two following variable in const.py
# They are used only with gtkmozembed.
MOZEMBED_PATH = TEMP_DIR
MOZEMBED_SUBPATH = Utils.get_empty_tempdir('mozembed_gramps')
GEOVIEW_SUBPATH = Utils.get_empty_tempdir('geoview')
NB_MARKERS_PER_PAGE = 200

#-------------------------------------------------------------------------
#
# Renderer
#
#-------------------------------------------------------------------------
class Renderer():
    """
    Renderer renders the webpage. Several backend implementations are 
    possible
    """
    def __init__(self):
        self.window = None
        self.fct = None

    def get_window(self):
        """
        Returns a container class with the widget that contains browser
        window
        """
        return self.window
    
    def get_uri(self):
        raise NotImplementedError
    
    def show_all(self):
        self.window.show_all()
    
    def open(self, url):
        """ open the webpage at url
        """
        raise NotImplementedError
    
    def refresh(self):
        raise NotImplementedError

    def go_back(self):
        self.window.go_back();

    def can_go_back(self):
        return self.window.can_go_back()

    def go_forward(self):
        self.window.go_forward();

    def can_go_forward(self):
        return self.window.can_go_forward()

    def execute_script(self, url):
        """ execute script in the current html page
        """
        raise NotImplementedError
    
    #def page_loaded(self,obj,status):
    def page_loaded(self):
        raise NotImplementedError
    
    def set_button_sensitivity(self):
        """
        We must set the back and forward button in the HtmlView class.
        """
        self.fct()

#-------------------------------------------------------------------------
#
# Renderer with WebKit
#
#-------------------------------------------------------------------------
class RendererWebkit(Renderer):
    """
    Implementation of Renderer with Webkit
    """
    def __init__(self):
        Renderer.__init__(self)
        self.window = webkit.WebView()
        self.browser = WEBKIT
        self.window.get_main_frame().connect("load-done", self.page_loaded)

    def page_loaded(self,obj,status):
        self.set_button_sensitivity()
    
    def open(self, url):
        self.window.open(url)
        
    def refresh(self):
        self.window.reload();

    def execute_script(self,url):
        self.window.execute_script(url);
    
    def get_uri(self):
        return self.window.get_main_frame().get_uri()

class RendererMozilla(Renderer):
    """
    Implementation of Renderer with gtkmozembed
    """
    def __init__(self):
        Renderer.__init__(self)
        if hasattr(gtkmozembed, 'set_profile_path'):
            set_profile_path = gtkmozembed.set_profile_path
        else:
            set_profile_path = gtkmozembed.gtk_moz_embed_set_profile_path
        set_profile_path(MOZEMBED_PATH, MOZEMBED_SUBPATH)
        self.__set_mozembed_proxy()
        self.window = gtkmozembed.MozEmbed()
        self.browser = MOZIL
        self.handler = self.window.connect("net-stop", self.page_loaded)
    
    def page_loaded(self,obj):
        self.set_button_sensitivity()
    
    def open(self, url):
        self.window.load_url(url)

    def execute_script(self,url):
        self.window.load_url(url);
    
    def get_uri(self):
        return self.window.get_location()

    def refresh(self):
        self.window.reload(0);

    def __set_mozembed_proxy(self):
        """
        Try to see if we have some proxy environment variable.
        http_proxy in our case.
        The standard format is : http://[user:password@]proxy:port/
        """
        try:
            proxy = os.environ['http_proxy']
            if proxy:
                host_port = None
                prefs = open(MOZEMBED_SUBPATH+"/prefs.js","w+")
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
                    prefs.write('user_pref("network.proxy.type", 1);\r\n')
                    prefs.write('user_pref("network.proxy.http", "'+host+'");\r\n')
                    prefs.write('user_pref("network.proxy.http_port", '+port+');\r\n')
                    prefs.write('user_pref("network.proxy.no_proxies_on", '\
                                '"127.0.0.1,localhost,localhost.localdomain");\r\n')
                    prefs.write('user_pref("network.proxy.share_proxy_settings", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.pipelining", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.keep-alive", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.version", 1.1);\r\n')
                    prefs.write('user_pref("network.http.sendRefererHeader, 0);\r\n')
                prefs.close()
        except:
            try: # trying to remove pref.js in case of proxy change.
                os.remove(MOZEMBED_SUBPATH+"/prefs.js")
            except:
                pass
            pass   # We don't use a proxy or the http_proxy variable is not set.

#-------------------------------------------------------------------------
#
# HtmlView
#
#-------------------------------------------------------------------------
class HtmlView(PageView.PageView):
    """
    HtmlView is a view showing a top widget with controls, and a bottom part
    with an embedded webbrowser showing a given URL
    """

    def __init__(self, dbstate, uistate):
        PageView.PageView.__init__(self, _('HtmlView'), dbstate, uistate)
        
        self.dbstate = dbstate
        
        self.external_url = False
        self.need_to_resize = False

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        global WebKit

        self.box = gtk.VBox(False, 4)
        #top widget at the top
        self.box.pack_start(self.top_widget(), False, False,0 )
        #web page under it in a scrolled window
        self.table = gtk.Table(1, 1, False)
        frame = gtk.ScrolledWindow(None, None)
        frame.set_shadow_type(gtk.SHADOW_NONE)
        frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        frame.add_with_viewport(self.table)
        self.bootstrap_handler = self.box.connect("size-request", self.init_parent_signals_for_map)
        self.table.get_parent().set_shadow_type(gtk.SHADOW_NONE)
        self.table.set_row_spacings(1)
        self.table.set_col_spacings(0)

        if   (WebKit == WEBKIT) :
            # We use webkit
            self.renderer = RendererWebkit()
        elif (WebKit == MOZIL) :
            # We use gtkmozembed
            self.renderer = RendererMozilla()

        self.table.add(self.renderer.get_window())
        self.box.pack_start(frame, True, True, 0)

        # this is used to activate the back and forward button from the renderer class.
        self.renderer.fct = self.set_button_sensitivity
        self.renderer.show_all()
        
        #load a welcome html page
        urlhelp = self.create_start_page()
        self.open(urlhelp)

        return self.box

    def top_widget(self):
        """
        The default class gives a widget where user can type an url
        """
        hbox = gtk.HBox(False,4)
        self.urlfield = gtk.Entry()
        self.urlfield.set_text("http://gramps-project.org")
        self.urlfield.connect('activate', self._on_activate);
        hbox.pack_start(self.urlfield, True, True, 4)
        button = gtk.Button(stock=gtk.STOCK_APPLY)
        button.connect('clicked', self._on_activate)
        hbox.pack_start(button, False, False, 4)
        return hbox

    def set_button_sensitivity(self):
        self.forward_action.set_sensitive(self.renderer.can_go_forward())
        self.back_action.set_sensitive(self.renderer.can_go_back())
        
    def open(self, url):
        """ open an url
        """
        self.renderer.open(url)

    def go_back(self, button):
        self.renderer.go_back();
        self.set_button_sensitivity()
        self.external_uri()

    def go_forward(self, button):
        self.renderer.go_forward();
        self.set_button_sensitivity()
        self.external_uri()

    def refresh(self,button):
        self.renderer.refresh();

    def external_uri(self):
        uri = self.renderer.get_uri()
        if self.external_url:
            self.external_url = False
            self.need_to_resize = True
        else:
            try:
                if uri.find(self.htmlfile) == -1:
                    # external web page or start_page
                    self.need_to_resize = True
                else:
                    self.need_to_resize = False
            except:
                pass

    def _on_activate(self, object):
        url = self.urlfield.get_text()
        if url.find('://') == -1:
            url = 'http://'+ url
        self.external_url = True
        self.open(url)
        
    def build_tree(self):
        """
        Rebuilds the current display. Called from ViewManager
        """
        pass #htmlview is build on click and startup

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-geo'

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
          </toolbar>
        </ui>'''

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. 
        """
        HtmlView._define_actions_fw_bw(self)
    
    def _define_actions_fw_bw(self):
        # add the Backward action to handle the Backward button
        # accel doesn't work in webkit and gtkmozembed !
        # we must do that ...
        self.back_action = gtk.ActionGroup(self.title + '/Back')
        self.back_action.add_actions([
            ('Back', gtk.STOCK_GO_BACK, _("_Back"), 
             "<ALT>Left", _("Go to the previous page in the history"), 
             self.go_back)
            ])
        self._add_action_group(self.back_action)
 
        # add the Forward action to handle the Forward button
        self.forward_action = gtk.ActionGroup(self.title + '/Forward')
        self.forward_action.add_actions([
            ('Forward', gtk.STOCK_GO_FORWARD, _("_Forward"), 
             "<ALT>Right", _("Go to the next page in the history"), 
             self.go_forward)
            ])
        self._add_action_group(self.forward_action)
 
        # add the Refresh action to handle the Refresh button
        self._add_action('Refresh', gtk.STOCK_REFRESH, _("_Refresh"), 
                          callback=self.refresh,
                          accel="<Ctl>R",
                          tip=_("Stop and reload the page."))

    def init_parent_signals_for_map(self, widget, event):
        # required to properly bootstrap the signal handlers.
        # This handler is connected by build_widget. After the outside ViewManager
        # has placed this widget we are able to access the parent container.
        pass
        
    def create_start_page(self):
        """
        This command creates a default start page, and returns the URL of this
        page.
        """
        tmpdir = GEOVIEW_SUBPATH
        data = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" \
                 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"  >
         <head>
          <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
          <title>%(title)s</title>
         </head>
         <body >
           <H4>%(content)s</H4>
         </body>
        </html>
        """ % { 'height' : 600,
                'title'  : _('Start page for the Html View'),
                'content': _('Type an webpage address at the top, and hit'
                             ' the execute button to load a webpage in this'
                             ' page\n<br>\n'
                             'For example: <b>http://gramps-project.org</p>')
        }
        filename = os.path.join(tmpdir, 'startpage')
        fd = file(filename,"w+")
        fd.write(data)
        fd.close()
        return 'file://'+filename


#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoView(HtmlView):

    def __init__(self,dbstate,uistate):
        HtmlView.__init__(self, dbstate, uistate)
        
        self.usedmap = "openstreetmap"
        self.displaytype = "person"
        self.nbmarkers = 0
        self.nbpages = 0

    def on_delete(self):
        """
        We need to suppress temporary files here.
        """
        pass

    def init_parent_signals_for_map(self, widget, event):
        # required to properly bootstrap the signal handlers.
        # This handler is connected by build_widget. After the outside ViewManager
        # has placed this widget we are able to access the parent container.
        self.box.disconnect(self.bootstrap_handler)
        self.box.parent.connect("size-allocate", self.size_request_for_map)
        self.size_request_for_map(widget.parent,event)
        
    def size_request_for_map(self, widget, event, data=None):
        v = widget.get_allocation()
        self.width = v.width
        self.height = v.height
        uri = self.renderer.get_uri()
        self.external_uri()
        if self.need_to_resize != True:
            try:
                self.geo_places(self.displaytype)
            except:
                pass

    def set_active(self):
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.goto_active_person)
    
    def set_inactive(self):
        HtmlView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)
        
    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-geo'

    def change_map(self,usedmap):
        self.renderer.execute_script("javascript:mapstraction.swap(map,'"+usedmap+"')");

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """

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
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="Refresh"/>
            </placeholder>
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

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. 
        """

        HtmlView._define_actions_fw_bw(self)
        self.forward_action.set_sensitive(False)
        self.back_action.set_sensitive(False)

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


    def goto_active_person(self,handle=None):
        self.geo_places(self.displaytype)

    def all_places(self,handle=None):
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self.geo_places(self.displaytype)

    def person_places(self,handle=None):
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        self.geo_places(self.displaytype)

    def family_places(self,handle=None):
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        self.geo_places(self.displaytype)

    def event_places(self,handle=None):
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self.geo_places(self.displaytype)

    def geo_places(self,displaytype):
        """
        Specifies the places to display with mapstraction.
        """
        self.external_url = False
        self.nbmarkers = 0
        self.createMapstraction(displaytype)
        self.open("file://"+self.htmlfile)

    def select_OpenStreetMap_map(self,handle=None):
        self.change_map("openstreetmap")

    def select_openlayers_map(self,handle=None):
        self.change_map("openlayers")

    def select_google_map(self,handle=None):
        self.change_map("google")

    def select_yahoo_map(self,handle=None):
        self.change_map("yahoo")

    def select_microsoft_map(self,handle=None):
        self.change_map("microsoft")

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
                prefs = open(MOZEMBED_PATH+MOZEMBED_SUBPATH+"/prefs.js","w")
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
                    prefs.write('user_pref("network.proxy.type", 1);\r\n')
                    prefs.write('user_pref("network.proxy.http", "'+host+'");\r\n')
                    prefs.write('user_pref("network.proxy.http_port", '+port+');\r\n')
                    prefs.write('user_pref("network.proxy.no_proxies_on", "127.0.0.1,localhost,localhost.localdomain");\r\n')
                    prefs.write('user_pref("network.proxy.share_proxy_settings", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.pipelining", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.keep-alive", true);\r\n')
                    prefs.write('user_pref("network.http.proxy.version", 1.1);\r\n')
                    prefs.write('user_pref("network.http.sendRefererHeader, 0);\r\n')
            prefs.close()
        except:
            try: # trying to remove pref.js in case of proxy change.
                os.remove(MOZEMBED_PATH+MOZEMBED_SUBPATH+"/prefs.js")
            except:
                pass
            pass   # We don't use a proxy or the http_proxy variable is not set.

    def createMapstractionPostHeader(self,h3mess,h4mess,maxpages,curpage,ftype):
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
        self.mapview.write("       var step = %s;\n" % self.yearint)
        self.mapview.write("  </script>\n")
        self.mapview.write(" </head>\n")
        self.mapview.write(" <body >\n")
        if maxpages > 1:
            message = _("We have %d markers, so I split this document in %d pages of %d markers : " % (self.nbmarkers, maxpages, NB_MARKERS_PER_PAGE))
            self.mapview.write(" <div id='pages' font=-4 >%s<br>\n" % message)
            if curpage != 1:
                priorfile=GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % (ftype,curpage-1)
                self.mapview.write(" <a href='%s' >--</a>" % priorfile)
            else:
                self.mapview.write(" --")
            for page in range(1,maxpages+1,1):
                if page == curpage:
                    self.mapview.write(" %d" % page)
                else:
                    if ( page < curpage + 10 ) and ( page > curpage - 10 ):
                        nextfile=GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % (ftype,page)
                        self.mapview.write(" <a href='%s' >%d</a>" % (nextfile, page))
            if curpage != maxpages:
                nextfile=GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % (ftype,curpage+1)
                self.mapview.write(" <a href='%s' >++</a>" % nextfile)
            else:
                self.mapview.write(" ++")
            self.mapview.write("\n</div>\n")
        if self.displaytype != "places":
            self.mapview.write(" <Div id='btns' font=-4 >\n")
            self.mapview.write("  <form method='POST'>\n")
            self.mapview.write("  <input type='radio' name='years' value='All' checked\n")
            self.mapview.write("         onchange=\"selectmarkers(\'All\')\"/>All\n")
            for year in range(self.minyear,self.maxyear+self.yearint,self.yearint):
                self.mapview.write("  <input type='radio' name='years' value=\'%s\'\n" %year)
                self.mapview.write("         onchange=\"selectmarkers(\'%s\')\"/>%s\n" % ( year, year ))
            self.mapview.write("  </form></Div>\n")
        self.mapview.write("<H3>%s</H3>" % h3mess)
        if h4mess:
            self.mapview.write("<H4>%s</H4>" % h4mess)

    def createMapstractionHeader(self,filename):
        self.mapview = open(filename,"w+")
        self.mapview.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n")
        self.mapview.write("         \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n")
        self.mapview.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n")
        self.mapview.write(" <head>\n")
        self.mapview.write("  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n")
        self.mapview.write("  <title>Geo Maps JavaScript API for Gramps</title>\n")
        self.mapview.write("  <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\">\n")
        self.mapview.write("  <script type=\"text/javascript\"\n" )
        self.mapview.write("          src=\"file://"+const.ROOT_DIR+"/mapstraction/mapstraction.js\">\n")
        self.mapview.write("  </script>\n")
        if self.usedmap == "microsoft":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6\">\n")
            self.mapview.write("  </script>\n")
        elif self.usedmap == "yahoo":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://api.maps.yahoo.com/ajaxymap?v=3.0&appid=MapstractionDemo\" type=\"text/javascript\">\n")
            self.mapview.write("  </script>\n")
        elif self.usedmap == "openlayers":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://openlayers.org/api/OpenLayers.js\">\n")
            self.mapview.write("  </script>\n")
        else: # openstreetmap and google
            self.mapview.write("  <script id=\"googleapiimport\" \n")
            self.mapview.write("          src=\"http://maps.google.com/maps?file=api&v=2\"\n")
            self.mapview.write("          type=\"text/javascript\">\n")
            self.mapview.write("  </script>\n")
        self.mapview.write("  <script>\n")
        self.mapview.write("       var gmarkers = [];\n")
        self.mapview.write("       var min = 0;\n")
        self.mapview.write("       var selectedmarkers = 'All';\n")
        self.mapview.write("       // shows or hide markers of a particular category\n")
        self.mapview.write("       function selectmarkers(year) {\n")
        self.mapview.write("         selectedmarkers = year;\n")
        self.mapview.write("         for (var i=0; i<gmarkers.length; i++) {\n")
        self.mapview.write("           val = gmarkers[i].getAttribute(\"year\");\n")
        self.mapview.write("           min = parseInt(year);\n")
        self.mapview.write("           max = min + step;\n")
        self.mapview.write("           if ( selectedmarkers == \"All\" ) { min = 0; max = 9999; }\n")
        self.mapview.write("           gmarkers[i].hide();\n")
        if   self.usedmap == "microsoft":
            self.mapview.write("")
        elif self.usedmap == "yahoo":
            self.mapview.write("")
        elif self.usedmap == "openlayers":
            self.mapview.write("")
        else: # openstreetmap and google
            self.mapview.write("           gmarkers[i].map.closeInfoWindow();\n")
        self.mapview.write("           years = val.split(' ');\n")
        self.mapview.write("           for ( j=0; j < years.length; j++) {\n")
        self.mapview.write("               if ( years[j] >= min ) {\n")
        self.mapview.write("                   if ( years[j] < max ) {\n")
        self.mapview.write("                       gmarkers[i].show();\n")
        self.mapview.write("                   }\n")
        self.mapview.write("               }\n")
        self.mapview.write("           }\n")
        self.mapview.write("         }\n")
        self.mapview.write("       }\n")

    def createMapstractionTrailer(self):
        self.mapview.write(" </body>\n")
        self.mapview.write("</html>\n")
        self.mapview.close()

    def create_pages(self,type,h3mess,h4mess):
        nbmarkers = 0
        self.nbpages = 0
        pages = ( self.nbmarkers / NB_MARKERS_PER_PAGE ) + 1
        if (nbmarkers % NB_MARKERS_PER_PAGE) == 0:
            try:
                self.createMapstractionTrailer()
            except:
                pass
        # Select the center of the map and the zoom
        self.centered = False
        if   type == 2:
            # Sort by year for events
            self.sort = sorted(self.place_list, key=operator.itemgetter(7))
        else:
            # Sort by place
            self.sort = sorted(self.place_list)
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
        # Calculate the zoom. all places must be displayed on the map.
        zoomlat=2
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
        self.zoom -= 1
        # We center the map on a point at the center of all markers
        self.centerlat = maxlat/2
        self.centerlon = maxlong/2
        for mark in self.sort:
            cent = int(mark[6])
            if cent:
                self.centered = True
                if ( signminlat == 1 and signmaxlat == 1 ):
                    latit = self.maxlat+self.centerlat
                elif ( signminlat == 0 and signmaxlat == 0 ): 
                    latit = self.maxlat-self.centerlat
                else:
                    latit = self.maxlat+self.centerlat
                if ( signminlon == 1 and signmaxlon == 1 ):
                    longt = self.maxlon-self.centerlon
                elif ( signminlon == 0 and signmaxlon == 0 ): 
                    longt = self.maxlon+self.centerlon
                else:
                    longt = self.maxlon-self.centerlon
        self.latit = latit
        self.longt = longt
        self.mustcenter = True
        for page in range(0,pages,1):
            self.nbpages += 1
            if   type == 1:
                ftype = "P"
            elif type == 2:
                ftype = "E"
            elif type == 3:
                ftype = "F"
            elif type == 4:
                ftype = "I"
            else:
                ftype = "X"
            filename = GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % (ftype,self.nbpages)
            if self.nbpages == 1:
                self.htmlfile=filename
            self.createMapstractionHeader(filename)
            self.createMapstractionPostHeader(h3mess,h4mess,pages,self.nbpages,ftype)
            first = ( self.nbpages - 1 ) * NB_MARKERS_PER_PAGE 
            last = ( self.nbpages * NB_MARKERS_PER_PAGE ) - 1
            self.create_markers(type,first,last)
            self.createMapstractionTrailer()
            if self.nbpages == 1:
                self.open(self.htmlfile)

    def createMapstraction(self,displaytype):
        if displaytype == "places":
            self.createMapstractionPlaces(self.dbstate)
        elif displaytype == "family":
            self.createMapstractionFamily(self.dbstate)
        elif displaytype == "person":
            self.createMapstractionPerson(self.dbstate)
        elif displaytype == "event":
            self.createMapstractionEvents(self.dbstate)
        else:
            self.createMapstractionHeader(GEOVIEW_SUBPATH+"/error.html")
            self.createMapstractionNotImplemented(self.dbstate)
            self.createMapstractionTrailer()

    def append_to_places_list(self, Place, evttype, name, lat, long, descr, center, year):
        self.place_list.append([Place, name, evttype, lat, long, descr, int(center), year])
        self.nbmarkers += 1

        a = float(lat)
        b = float(long)
        if year is not None:
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

    def create_markers(self,format,firstm,lastm):
        margin = 10
        self.mapview.write("  <div id=\"map\" style=\"width: %dpx; height: %dpx\"></div>\n" % 
                           ( ( self.width - margin*4 ), ( self.height * 0.74 )))
        self.mapview.write("  <script type=\"text/javascript\">\n")
        self.mapview.write("   var mapstraction = new Mapstraction('map','%s');\n"%self.usedmap)
        self.mapview.write("   mapstraction.addControls({ pan: true, zoom: 'large', ")
        self.mapview.write("overview: true, scale: true, map_type: true });\n")
        last = ""
        indm=0
        divclose=1
        self.yearinmarker = []
        InInterval = False
        self.setattr = True
        if self.mustcenter:
            self.centered = True
            self.mapview.write("var point = new LatLonPoint(%s,%s);"%(self.latit,self.longt))
            self.mapview.write("mapstraction.setCenterAndZoom(point, %s);"%self.zoom)
            self.setattr = False
        for mark in self.sort:
            if ( indm >= firstm ) and ( indm <= lastm ):
                InInterval = True
            if InInterval:
                if last != mark[0]:
                    self.setattr = True
                    last = mark[0]
                    self.mapview.write("\nvar point = new LatLonPoint(%s,%s);"%(mark[3],mark[4]))
                    self.mapview.write("my_marker = new Marker(point);")
                    self.mapview.write("gmarkers[%d]=my_marker;" % (indm % NB_MARKERS_PER_PAGE))
                    indm += 1;
                    if ( indm > lastm ):
                        InInterval = False
                    if ( indm >= firstm ) and ( indm <= lastm ):
                        self.mapview.write("my_marker.setLabel(\"%s\");"%mark[0])
                        self.yearinmarker.append(mark[7])
                        divclose=0
                        self.mapview.write("my_marker.setInfoBubble(\"<div style='white-space:nowrap;' >")
                        if format == 1:
                            self.mapview.write("%s<br>____________<br><br>%s"%(mark[0],mark[5]))
                        elif format == 2:
                            self.mapview.write("%s____________<br><br>%s - %s"%(mark[1],mark[7],mark[5]))
                        elif format == 3:
                            self.mapview.write("%s<br>____________<br><br>%s - %s"%(mark[0],mark[7],mark[5]))
                        elif format == 4:
                            self.mapview.write("%s<br>____________<br><br>%s - %s"%(mark[0],mark[7],mark[5]))
                else: # This marker already exists. add info.
                    self.mapview.write("<br>%s - %s" % (mark[7], mark[5]))
                    if self.isyearnotinmarker(self.yearinmarker,mark[7]):
                        self.yearinmarker.append(mark[7])
                    cent = int(mark[6])
                    if cent:
                        self.centered = True
                        if float(mark[3]) == self.minlat:
                            if signminlat == 1: 
                                latit = str(float(mark[3])+self.centerlat)
                            else:
                                latit = str(float(mark[3])-self.centerlat)
                        else:
                            if signminlat == 1: 
                                latit = str(float(mark[3])-self.centerlat)
                            else:
                                latit = str(float(mark[3])+self.centerlat)
                        if float(mark[4]) == self.minlon:
                            if signminlon == 1:
                                longt = str(float(mark[4])+self.centerlon)
                            else:
                                longt = str(float(mark[4])-self.centerlon)
                        else:
                            if signminlon == 1:
                                longt = str(float(mark[4])-self.centerlon)
                            else:
                                longt = str(float(mark[4])+self.centerlon)
                if divclose == 0:
                    if InInterval:
                        self.mapview.write("</div>\");")
                years = ""
                if mark[2]:
                    for y in self.yearinmarker:
                        years += "%d " % y
                years += "end"
            else:
                indm += 1
            if self.setattr:
                years=""
                if mark[2]:
                    for y in self.yearinmarker:
                        years += "%d " % y
                years += "end"
                self.mapview.write("my_marker.setAttribute('year','%s');" % years)
                self.yearinmarker = []
                self.mapview.write("mapstraction.addMarker(my_marker);")
                self.setattr = False
            if not self.centered:
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
                self.mapview.write("\nvar point = new LatLonPoint(%s,%s);\n"%(latitude,longitude))
                self.mapview.write("   mapstraction.setCenterAndZoom(point, %d);\n"%2)
                self.mapview.write("   my_marker = new Marker(point);\n")
                self.mapview.write("   my_marker.setLabel(\"%s\");\n"%_("The author of this module."))
                self.mapview.write("   my_marker.setInfoBubble(\"<div style='white-space:nowrap;' >")
                self.mapview.write("Serge Noiraud<br>Nantes, France<br>")
                self.mapview.write("%s</div>\");\n"%_("This request has no geolocation associated."))
                self.mapview.write("   mapstraction.addMarker(my_marker);")
                self.setattr = False
        if self.setattr:
            years = ""
            if mark[2]:
                for y in self.yearinmarker:
                    years += "%d " % y
            years += "end"
            self.mapview.write("my_marker.setAttribute('year','%s');" % years)
            self.yearinmarker = []
            years=""
            self.mapview.write("mapstraction.addMarker(my_marker);")
            self.setattr = False
        self.mapview.write("\n  </script>\n")


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
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    place = db.db.get_place_from_handle(bplace_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
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
                self.center = False
            latitude = ""
            longitude = ""
            death_ref = person.get_death_ref()
            if death_ref:
                death = db.db.get_event_from_handle(death_ref.ref)
                deathdate = death.get_date_object()
                deathyear = deathdate.get_year()
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    place = db.db.get_place_from_handle(dplace_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
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
                self.center = False

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
        self.center = True
        for place_handle in db.db.get_place_handles():
            place = db.db.get_place_from_handle( place_handle)
            if place:
                descr = place.get_title()
                descr1 = _("Id : %s")%place.gramps_id
                longitude = place.get_longitude()
                latitude = place.get_latitude()
                latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                city = place.get_main_location().get_city()
                country = place.get_main_location().get_country()
                if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                    self.append_to_places_list(descr, None,
                                               "",
                                               latitude, longitude,
                                               descr1, self.center, None)
                    self.center = False
        if self.center:
            mess = _("Cannot center the map. No selected location.")
        else:
            mess = ""
        self.create_pages(1,_("All places in the database with coordinates."),mess)

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
        self.center = True
        for event_handle in db.db.get_event_handles():
            event = db.db.get_event_from_handle( event_handle)
            if event:
                pl_id = event.get_place_handle()
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                descr1 = _("Id : %s (%s)")%(event.gramps_id,eventyear)
                if pl_id:
                    place = db.db.get_place_from_handle(pl_id)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                    city = place.get_main_location().get_city()
                    country = place.get_main_location().get_country()
                    descr2 = "%s; %s" % (city,country)
                    if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                        person_list = [ db.db.get_person_from_handle(ref_handle)
                                        for (ref_type, ref_handle) in db.db.find_backlink_handles(event_handle)
                                            if ref_type == 'Person' 
                                      ]
                        if person_list:
                            descr = "<br>"
                            for person in person_list:
                                descr = _("%s%s<br>") % (descr, _nd.display(person))
                            descr = _("%s; %s%s") % (gen.lib.EventType(event.get_type()),place.get_title(), descr)
                        else:
                            descr = _("%s; %s<br>") % (gen.lib.EventType(event.get_type()),place.get_title())
                        self.append_to_places_list(descr1, descr,
                                                   descr,
                                                   latitude, longitude,
                                                   descr2, self.center, eventyear)
                        self.center = False
        if self.center:
            mess = _("Cannot center the map. No selected location.")
        else:
            mess = ""
        self.create_pages(2,_("All events in the database with coordinates."),mess)

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
        self.center = True
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
        if self.center:
            mess = _("Cannot center the map. No selected location.")
        else:
            mess = ""
        self.create_pages(3,
                          ( _("All %s people's familiy places in the database with coordinates.") % 
                              _nd.display(person) ),
                          mess)

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
        self.center = True
        if person:
            # For each event, if we have a place, set a marker.
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                if event_ref.role != gen.lib.EventRoleType.PRIMARY:
                    # Only match primaries, no witnesses
                    continue
                event = db.db.get_event_from_handle(event_ref.ref)
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                place_handle = event.get_place_handle()
                if place_handle:
                    place = db.db.get_place_from_handle(place_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
                    latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
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
                        self.center = False
        if self.center:
            mess = _("Cannot center the map. No selected location.")
        else:
            mess = ""
        self.create_pages(4,( _("All event places for %s.") % _nd.display(person) ) ,mess)

    def createMapstractionNotImplemented(self,db):
        """
        This function is used to inform the user this work is not implemented.
        """
        self.mapview.write("  <H1>%s ...</H1>"%_("Not yet implemented"))

