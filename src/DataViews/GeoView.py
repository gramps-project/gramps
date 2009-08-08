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
class Renderer(object):
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
        """
        Get the current url
        """
        raise NotImplementedError

    def show_all(self):
        """
        show all in the main window.
        """
        self.window.show_all()

    def open(self, url):
        """
        open the webpage at url
        """
        raise NotImplementedError

    def refresh(self):
        """
        We need to reload the page.
        """
        raise NotImplementedError

    def go_back(self):
        """
        Go to the previous page.
        """
        self.window.go_back()

    def can_go_back(self):
        """
        is the browser able to go backward ?
        """
        return self.window.can_go_back()

    def go_forward(self):
        """
        Go to the next page.
        """
        self.window.go_forward()

    def can_go_forward(self):
        """
        is the browser able to go forward ?
        """
        return self.window.can_go_forward()

    def execute_script(self, url):
        """
        execute javascript in the current html page
        """
        raise NotImplementedError

    def page_loaded(self):
        """
        The page is completely loaded.
        """
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
        self.frame = self.window.get_main_frame()
        self.frame.connect("load-done", self.page_loaded)

    def page_loaded(self, obj, status):
        """
        We just loaded one page in the browser.
        Set the button sensitivity 
        """
        self.set_button_sensitivity()

    def open(self, url):
        """
        We need to load the page in the browser.
        """
        self.window.open(url)

    def refresh(self):
        """
        We need to reload the page in the browser.
        """
        self.window.reload()

    def execute_script(self, url):
        """
        We need to execute a javascript function into the browser
        """
        self.window.execute_script(url)

    def get_uri(self):
        """
        What is the uri loaded in the browser ?
        """
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

    def page_loaded(self, obj):
        """
        We just loaded one page in the browser.
        Set the button sensitivity 
        """
        self.set_button_sensitivity()

    def open(self, url):
        """
        We need to load the page in the browser.
        """
        self.window.load_url(url)

    def execute_script(self, url):
        """
        We need to execute a javascript function into the browser
        """
        self.window.load_url(url)

    def get_uri(self):
        """
        What is the uri loaded in the browser ?
        """
        return self.window.get_location()

    def refresh(self):
        """
        We need to reload the page in the browser.
        """
        self.window.reload(0)

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
                prefs = open(MOZEMBED_SUBPATH+"/prefs.js", "w+")
                parts = urlparse.urlparse(proxy)
                if not parts[0] or parts[0] == 'http':
                    host_port = parts[1]
                    hport = host_port.split(':')
                    host = hport[0].strip()
                    if host:
                        try:
                            port = int(hport[1])
                        except:
                            user = host
                            uprox = hport[1].split('@')
                            password = uprox[0]
                            host = uprox[1]
                            port = int(hport[2])

                if port and host:
                    port = str(port)
                    prefs.write('user_pref("network.proxy')
                    prefs.write('.type", 1);\r\n')
                    prefs.write('user_pref("network.proxy')
                    prefs.write('.http", "'+host+'");\r\n')
                    prefs.write('user_pref("network.proxy')
                    prefs.write('.http_port", '+port+');\r\n')
                    prefs.write('user_pref("network.proxy')
                    prefs.write('.no_proxies_on",')
                    prefs.write(' "127.0.0.1,localhost,localhost')
                    prefs.write('.localdomain");\r\n')
                    prefs.write('user_pref("network.proxy')
                    prefs.write('.share_proxy_settings", true);\r\n')
                    prefs.write('user_pref("network.http')
                    prefs.write('.proxy.pipelining", true);\r\n')
                    prefs.write('user_pref("network.http')
                    prefs.write('.proxy.keep-alive", true);\r\n')
                    prefs.write('user_pref("network.http')
                    prefs.write('.proxy.version", 1.1);\r\n')
                    prefs.write('user_pref("network.http')
                    prefs.write('.sendRefererHeader, 0);\r\n')
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

    def __init__(self, dbstate, uistate, title=_('HtmlView')):
        PageView.PageView.__init__(self, title, dbstate, uistate)
        self.dbstate = dbstate
        self.external_url = False
        self.need_to_resize = False
        self.back_action = None
        self.forward_action = None
        self.renderer = None
        self.urlfield = ""
        self.htmlfile = ""
        self.table = ""
        self.bootstrap_handler = None
        self.box = None

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        global WebKit
        self.box = gtk.VBox(False, 4)
        #top widget at the top
        self.box.pack_start(self.top_widget(), False, False, 0 )
        #web page under it in a scrolled window
        self.table = gtk.Table(1, 1, False)
        frame = gtk.ScrolledWindow(None, None)
        frame.set_shadow_type(gtk.SHADOW_NONE)
        frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        frame.add_with_viewport(self.table)
        self.bootstrap_handler = self.box.connect("size-request", 
                                 self.init_parent_signals_for_map)
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
        # this is used to activate the back and forward button
        # from the renderer class.
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
        hbox = gtk.HBox(False, 4)
        self.urlfield = gtk.Entry()
        self.urlfield.set_text("http://gramps-project.org")
        self.urlfield.connect('activate', self._on_activate)
        hbox.pack_start(self.urlfield, True, True, 4)
        button = gtk.Button(stock=gtk.STOCK_APPLY)
        button.connect('clicked', self._on_activate)
        hbox.pack_start(button, False, False, 4)
        return hbox

    def set_button_sensitivity(self):
        """
        Set the backward and forward button in accordance to the browser.
        """
        self.forward_action.set_sensitive(self.renderer.can_go_forward())
        self.back_action.set_sensitive(self.renderer.can_go_back())
        
    def open(self, url):
        """
        open an url
        """
        self.renderer.open(url)

    def go_back(self, button):
        """
        Go to the previous loaded url.
        """
        self.renderer.go_back()
        self.set_button_sensitivity()
        self.external_uri()

    def go_forward(self, button):
        """
        Go to the next loaded url.
        """
        self.renderer.go_forward()
        self.set_button_sensitivity()
        self.external_uri()

    def refresh(self, button):
        """
        Force to reload the page.
        """
        self.renderer.refresh()

    def external_uri(self):
        """
        used to resize or not resize depending on external or local file.
        """
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

    def _on_activate(self, nobject):
        """
        Here when we activate the url button.
        """
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
        """
        prepare the forward and backward buttons.
        add the Backward action to handle the Backward button
        accel doesn't work in webkit and gtkmozembed !
        we must do that ...
        """
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
        """
        Required to properly bootstrap the signal handlers.
        This handler is connected by build_widget.
        After the outside ViewManager has placed this widget we are
        able to access the parent container.
        """
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
                'content': _('Type a webpage address at the top, and hit'
                             ' the execute button to load a webpage in this'
                             ' page\n<br>\n'
                             'For example: <b>http://gramps-project.org</p>')
        }
        filename = os.path.join(tmpdir, 'startpage')
        ufd = file(filename, "w+")
        ufd.write(data)
        ufd.close()
        return 'file://'+filename

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
        """
        pass

    def init_parent_signals_for_map(self, widget, event):
        """
        Required to properly bootstrap the signal handlers.
        This handler is connected by build_widget.
        After the outside ViewManager has placed this widget we are
        able to access the parent container.
        """
        self.box.disconnect(self.bootstrap_handler)
        self.box.parent.connect("size-allocate", self.size_request_for_map)
        self.size_request_for_map(widget.parent, event)

    def size_request_for_map(self, widget, event, data=None):
        """
        We need to resize the map
        """
        gws = widget.get_allocation()
        self.width = gws.width
        self.height = gws.height
        #uri = self.renderer.get_uri()
        self.external_uri()
        if self.need_to_resize != True:
            try:
                self.geo_places(self.displaytype)
            except:
                pass

    def set_active(self):
        """
        Here when we enter in this view.
        """
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.goto_active_person)

    def set_inactive(self):
        """
        Here when we go to another view.
        """
        HtmlView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-geo'

    def change_map(self, usedmap):
        """
        Ask to the browser to change the current map.
        """
        self.renderer.execute_script(
            "javascript:mapstraction.swap('"+usedmap+"','"+usedmap+"')")

    def _alternate_map(self):
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
              <separator/>
              <toolitem action="PersonMaps"/>
              <toolitem action="FamilyMaps"/>
              <toolitem action="EventMaps"/>
              <toolitem action="AllPlacesMaps"/>
            </placeholder>
          </toolbar>
        </ui>'''  % self._alternate_map()

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. 
        """
        HtmlView._define_actions_fw_bw(self)
        self.forward_action.set_sensitive(False)
        self.back_action.set_sensitive(False)
        self._add_action('OpenStreetMap', 'gramps-openstreetmap', 
                         _('_OpenStreetMap'),
                         callback=self.select_openstreetmap_map,
                         tip=_("Select OpenStreetMap Maps"))
        if Config.get(Config.GEOVIEW_GOOGLEMAPS):
            self._add_action('google', 'gramps-alternate-map',
                             _('_Google Maps'),
                             callback=self.select_google_map,
                             tip=_("Select Google Maps."))
        elif Config.get(Config.GEOVIEW_OPENLAYERS):
            self._add_action('openlayers', 'gramps-alternate-map',
                             _('_OpenLayers Maps'),
                             callback=self.select_openlayers_map,
                             tip=_("Select OpenLayers Maps."))
        elif Config.get(Config.GEOVIEW_YAHOO):
            self._add_action('yahoo', 'gramps-alternate-map', 
                             _('_Yahoo! Maps'),
                             callback=self.select_yahoo_map,
                             tip=_("Select Yahoo Maps."))
        elif Config.get(Config.GEOVIEW_MICROSOFT):
            self._add_action('microsoft', 'gramps-alternate-map',
                             _('_Microsoft Maps'),
                             callback=self.select_microsoft_map,
                             tip=_("Select Microsoft Maps"))
        self._add_action('AllPlacesMaps', gtk.STOCK_HOME, _('_All Places'),
            callback=self.all_places,
            tip=_("Attempt to view all places in the family tree."))
        self._add_action('PersonMaps', 'gramps-person', _('_Person'),
            callback=self.person_places,
            tip=_("Attempt to view all the places where the selected people lived."))
        self._add_action('FamilyMaps', 'gramps-parents-add', _('_Family'),
            callback=self.family_places,
            tip=_("Attempt to view places of the selected people's family."))
        self._add_action('EventMaps', 'gramps-event', _('_Event'),
            callback=self.event_places,
            tip=_("Attempt to view places connected to all events."))

    def goto_active_person(self, handle=None):
        """
        Here when the GeoView page is loaded
        """
        self.geo_places(self.displaytype)

    def all_places(self, hanle=None):
        """
        Specifies the place for the home person to display with mapstraction.
        """
        self.displaytype = "places"
        self.geo_places(self.displaytype)

    def person_places(self, handle=None):
        """
        Specifies the person places.
        """
        self.displaytype = "person"
        self.geo_places(self.displaytype)

    def family_places(self, hanle=None):
        """
        Specifies the family places to display with mapstraction.
        """
        self.displaytype = "family"
        self.geo_places(self.displaytype)

    def event_places(self, hanle=None):
        """
        Specifies all event places to display with mapstraction.
        """
        self.displaytype = "event"
        self.geo_places(self.displaytype)

    def geo_places(self, displaytype):
        """
        Specifies the places to display with mapstraction.
        """
        self.external_url = False
        self.nbmarkers = 0
        self.without = 0
        self.createmapstraction(displaytype)
        self.open("file://"+self.htmlfile)

    def select_openstreetmap_map(self,handle):
        """
        Specifies openstreetmap is the default map
        """
        self.usedmap = "openstreetmap"        
        self.change_map("openstreetmap")

    def select_openlayers_map(self,handle):
        """
        Specifies openstreetmap is the default map
        """
        self.usedmap = "openlayers"        
        self.change_map("openlayers")

    def select_google_map(self,handle):
        """
        Specifies google is the default map
        """
        self.usedmap = "google"        
        self.change_map("google")

    def select_yahoo_map(self,handle):
        """
        Specifies yahoo map is the default map
        """
        self.usedmap = "yahoo"        
        self.change_map("yahoo")

    def select_microsoft_map(self,handle):
        """
        Specifies microsoft is the default map
        """
        self.usedmap = "microsoft"        
        self.change_map("microsoft")

    def createpageforplaceswithoutcoord(self):
        """
        This command creates a page with the list of all places without coordinates
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
           <H4>%(content)s</H4>
        """ % { 'title'  : _('List of places without coordinates'),
                'content': _('Here is the list of all places in the family tree'
                             ' for which we have no coordinates.<br>'
                             ' This means no longitude or latitude.<p>')
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
            ufd.write("<tr><td>%d</td><td>%s</td><td>%s</td>"
                     % ( i, place[0], place[1] ))
            i += 1
        ufd.write(end)
        ufd.close()

    def createmapstractionpostheader(self, h3mess, h4mess,
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
        self.minyear = ( self.minyear - ( self.minyear % 10 ) )
        self.maxyear = ( self.maxyear - ( self.maxyear % 10 ) )
        self.yearint = (self.maxyear-self.minyear)/self.maxgen
        self.yearint = ( self.yearint - ( self.yearint % modulo ) )
        if self.yearint == 0:
            self.yearint = 10
        self.mapview.write("       var step = %s;\n" % self.yearint)
        self.mapview.write("  </script>\n")
        self.mapview.write(" </head>\n")
        self.mapview.write(" <body >\n")
        if maxpages > 1:
            message = _("There are %d markers to display. They are split up "
                        "over %d pages of %d markers : " % (self.nbmarkers, 
                                            maxpages, NB_MARKERS_PER_PAGE))
            self.mapview.write(" <div id='pages' font=-4 >%s<br>\n" % message)
            if curpage != 1:
                priorfile = GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % \
                            (ftype, curpage-1)
                self.mapview.write("<a href='%s' >--</a>" % priorfile)
            else:
                self.mapview.write(" --")
            for page in range(1, maxpages+1, 1):
                if page == curpage:
                    self.mapview.write(" %d" % page)
                else:
                    if ( page < curpage + 11 ) and ( page > curpage - 11 ):
                        nextfile = GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % \
                                   (ftype, page)
                        self.mapview.write(" <a href='%s' >%d</a>" % \
                                           (nextfile, page))
            if curpage != maxpages:
                nextfile = GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % \
                                           (ftype, curpage+1)
                self.mapview.write(" <a href='%s' >++</a>" % nextfile)
            else:
                self.mapview.write(" ++")
            self.mapview.write("\n</div>\n")
            if self.without != 0:
                self.without_coord_file = GEOVIEW_SUBPATH+"/without_coord.html"
                self.mapview.write("<div id='coord' font=-4 >You have ")
                self.mapview.write("<a href=\"%s\" >%d<a>" % \
                                   ( self.without_coord_file, self.without ) )
                self.mapview.write(" places without coordinates</div>\n" )
                self.createpageforplaceswithoutcoord()
        if self.displaytype != "places":
            self.mapview.write(" <Div id='btns' font=-4 >\n")
            self.mapview.write("  <form method='POST'>\n")
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
            self.mapview.write("  </form></Div>\n")
        self.mapview.write("<H3>%s</H3>" % h3mess)
        if h4mess:
            self.mapview.write("<H4>%s</H4>" % h4mess)

    def createmapstractionheader(self, filename):
        """
        Create the html header of the page.
        """
        self.mapview = open(filename, "w+")
        self.mapview.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD")
        self.mapview.write(" XHTML 1.0 Strict//EN\" \n")
        self.mapview.write("   \"http://www.w3.org/TR/xhtml1/DTD/")
        self.mapview.write("xhtml1-strict.dtd\">\n")
        self.mapview.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" >\n")
        self.mapview.write(" <head>\n")
        self.mapview.write("  <meta http-equiv=\"content-type\" ")
        self.mapview.write("content=\"text/html; charset=utf-8\"/>\n")
        self.mapview.write("  <title>Geo Maps Java Script ")
        self.mapview.write("API for Gramps</title>\n")
        self.mapview.write("  <meta http-equiv=\"Content-Script-Type\" ")
        self.mapview.write("content=\"text/javascript\">\n")
        self.mapview.write("  <script type=\"text/javascript\"\n" )
        self.mapview.write("          src=\"file://"+const.ROOT_DIR+"/")
        self.mapview.write("mapstraction/mapstraction.js\">\n")
        self.mapview.write("  </script>\n")
        self.mapview.write("  <script id=\"googleapiimport\" \n")
        self.mapview.write("          src=\"http://maps.google.com/")
        self.mapview.write("maps?file=api&v=2\"\n")
        self.mapview.write("          type=\"text/javascript\">\n")
        self.mapview.write("  </script>\n")
        alternatemap = self._alternate_map()
        if alternatemap == "microsoft":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://dev.virtualearth.net/")
            self.mapview.write("mapcontrol/mapcontrol.ashx?v=6\">\n")
            self.mapview.write("  </script>\n")
        elif alternatemap == "yahoo":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://api.maps.yahoo.com/")
            self.mapview.write("ajaxymap?v=3.0&appid=MapstractionDemo\" ")
            self.mapview.write("type=\"text/javascript\">\n")
            self.mapview.write("  </script>\n")
        elif alternatemap == "openlayers":
            self.mapview.write("  <script type=\"text/javascript\"\n")
            self.mapview.write("          src=\"http://openlayers.org/")
            self.mapview.write("api/OpenLayers.js\">\n")
            self.mapview.write("  </script>\n")
        self.mapview.write("  <script>\n")
        self.mapview.write("       var gmarkers = [];\n")
        self.mapview.write("       var min = 0;\n")
        self.mapview.write("       var selectedmarkers = 'All';\n")
        self.mapview.write("       // shows or hide markers of a ")
        self.mapview.write("particular category\n")
        self.mapview.write("       function selectmarkers(year) {\n")
        self.mapview.write("         selectedmarkers = year;\n")
        self.mapview.write("         for (var i=0; i<gmarkers.length; i++) {\n")
        self.mapview.write("           val = gmarkers[i].getAttribute")
        self.mapview.write("(\"year\");\n")
        self.mapview.write("           min = parseInt(year);\n")
        self.mapview.write("           max = min + step;\n")
        self.mapview.write("           if ( selectedmarkers == \"All\" ) ")
        self.mapview.write("{ min = 0; max = 9999; }\n")
        self.mapview.write("           gmarkers[i].hide();\n")
        if   self.usedmap == "microsoft":
            self.mapview.write("")
        elif self.usedmap == "yahoo":
            self.mapview.write("")
        elif self.usedmap == "openlayers":
            self.mapview.write("")
        else: # openstreetmap and google
            self.mapview.write("           gmarkers[i].map.")
            self.mapview.write("closeInfoWindow();\n")
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

    def createmapstractiontrailer(self):
        """
        Add the last directives for the html page
        """
        self.mapview.write(" </body>\n")
        self.mapview.write("</html>\n")
        self.mapview.close()

    def create_pages(self, ptype, h3mess, h4mess):
        """
        Do we need to create a multi-pages document ?
        Do we have too many markers ?
        """
        nbmarkers = 0
        self.nbpages = 0
        pages = ( self.nbmarkers / NB_MARKERS_PER_PAGE ) + 1
        if (nbmarkers % NB_MARKERS_PER_PAGE) == 0:
            try:
                self.createmapstractiontrailer()
            except:
                pass
        # Select the center of the map and the zoom
        self.centered = False
        if ptype == 2:
            # Sort by year for events
            self.sort = sorted(self.place_list, key=operator.itemgetter(7))
        else:
            # Sort by place
            self.sort = sorted(self.place_list)
        if self.minlon < 0.0:
            signminlon = 1
        else:
            signminlon = 0
        if self.maxlon < 0.0:
            signmaxlon = 1
        else:
            signmaxlon = 0
        if self.minlat < 0.0:
            signminlat = 1
        else:
            signminlat = 0
        if self.maxlat < 0.0:
            signmaxlat = 1
        else:
            signmaxlat = 0
        if signminlon == signmaxlon: 
            maxlong = abs(abs(self.minlon)-abs(self.maxlon))
        else:
            maxlong = abs(abs(self.minlon)+abs(self.maxlon))
        if signminlat == signmaxlat:
            maxlat = abs(abs(self.minlat)-abs(self.maxlat))
        else:
            maxlat = abs(abs(self.minlat)+abs(self.maxlat))
        # Calculate the zoom. all places must be displayed on the map.
        zoomlat = 2
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
        zoomlong = 2
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
            filename = GEOVIEW_SUBPATH+"/GeoV-%c-%05d.html" % \
                       (ftype, self.nbpages)
            if self.nbpages == 1:
                self.htmlfile = filename
            self.createmapstractionheader(filename)
            self.createmapstractionpostheader(h3mess, h4mess, 
                                              pages, self.nbpages, ftype)
            first = ( self.nbpages - 1 ) * NB_MARKERS_PER_PAGE 
            last = ( self.nbpages * NB_MARKERS_PER_PAGE ) - 1
            self.create_markers(ptype, first, last)
            self.createmapstractiontrailer()
            if self.nbpages == 1:
                self.open(self.htmlfile)

    def createmapstraction(self, displaytype):
        """
        Which kind of map are we going to create ?
        """
        if displaytype == "places":
            self.createmapstractionplaces(self.dbstate)
        elif displaytype == "family":
            self.createmapstractionfamily(self.dbstate)
        elif displaytype == "person":
            self.createmapstractionperson(self.dbstate)
        elif displaytype == "event":
            self.createmapstractionevents(self.dbstate)
        else:
            self.createmapstractionheader(GEOVIEW_SUBPATH+"/error.html")
            self.createmapnotimplemented()
            self.createmapstractiontrailer()

    def append_to_places_without_coord(self, gid, place):
        """
        Create a list of places without coordinates
        """
        self.place_without_coordinates.append([gid, place])
        self.without += 1

    def append_to_places_list(self, place, evttype, name, lat, 
                              longit, descr, center, year):
        """
        Create a list of places with coordinates
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
            tfa = tfa - 0.00000001
        else:
            tfa = tfa + 0.00000001
        if tfb < 0.0:
            tfb = tfb - 0.00000001
        else:
            tfb = tfb + 0.00000001

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

    def isyearnotinmarker(self, allyears, yeartosearch):
        """
        This function is used to find if a year is in a list
        """
        ret = 1
        for year in allyears:
            if yeartosearch == year:
                ret = 0
        return ret

    def create_markers(self, format, firstm, lastm):
        """
        This function create all markers for the specified person.
        """
        margin = 10
        self.mapview.write("\n<div id=\"openstreetmap\" class=\"Mapstraction\"")
        self.mapview.write(" style=\"width: %dpx; " % (self.width - margin*4))
        self.mapview.write("height: %dpx\"></div>\n" % (self.height * 0.74))
        self.mapview.write("<div id=\"%s\" class=\"Mapstraction\"" % self._alternate_map())
        self.mapview.write(" style=\"display: none; ")
        self.mapview.write("width: %dpx; height: %dpx\"></div>\n" % \
                           ((self.width - margin*4), (self.height * 0.74 )))
        self.mapview.write("<script type=\"text/javascript\">\n")
        self.mapview.write(" var mapstraction = new Mapstraction")
        self.mapview.write("('openstreetmap','openstreetmap');\n")
        self.mapview.write(" mapstraction.addControls(")
        self.mapview.write("{ pan: true, zoom: 'large', ")
        self.mapview.write("overview: true, scale: true, map_type: true });\n")
        last = ""
        indm = 0
        divclose = True
        self.yearinmarker = []
        ininterval = False
        self.setattr = True
        if self.mustcenter:
            self.centered = True
            self.mapview.write("var point = new LatLonPoint")
            self.mapview.write("(%s,%s);" % (self.latit, self.longt))
            self.mapview.write("mapstraction.setCenterAndZoom")
            self.mapview.write("(point, %s);" % self.zoom)
            self.setattr = False
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
                        self.mapview.write("\nvar point = new LatLonPoint")
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
                    if self.isyearnotinmarker(self.yearinmarker, mark[7]):
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
        self.mapview.write("\n  </script>\n")

    def createpersonmarkers(self, dbstate, person, comment):
        """
        This function create all markers for the specified person.
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
                        self.append_to_places_list(descr,
                                                   gen.lib.EventType.BIRTH, 
                                                   _nd.display(person),
                                                   latitude, longitude,
                                                   descr1, int(self.center),
                                                   birthyear)
                        self.center = False
                    else:
                        self.append_to_places_without_coord(place.gramps_id,
                                                            descr)
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
                        self.append_to_places_list(descr,
                                                   gen.lib.EventType.DEATH,
                                                   _nd.display(person),
                                                   latitude, longitude,
                                                   descr1, int(self.center),
                                                   deathyear)
                        self.center = False
                    else:
                        self.append_to_places_without_coord(place.gramps_id,
                                                            descr)

    def createmapstractionplaces(self, dbstate):
        """
        This function create the marker for each place in the database
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
        for place_handle in dbstate.db.get_place_handles():
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
                    self.append_to_places_list(descr, None,
                                               "",
                                               latitude, longitude,
                                               descr1, self.center, None)
                    self.center = False
                else:
                    self.append_to_places_without_coord(place.gramps_id,
                                                              descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
        else:
            mess = ""
        self.create_pages(1,
                          _("All places in the family tree with coordinates."),
                          mess)

    def createmapstractionevents(self, dbstate):
        """
        This function create one marker for each place associated with an event in the database
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
                pl_id = event.get_place_handle()
                eventdate = event.get_date_object()
                eventyear = eventdate.get_year()
                descr1 = _("Id : %(id)s (%(year)s)") % {
                                'id' : event.gramps_id,
                                'year' : eventyear}
                if pl_id:
                    place = dbstate.db.get_place_from_handle(pl_id)
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
                        person_list = [dbstate.db.get_person_from_handle(ref_handle)
                            for (ref_type, ref_handle) in \
                                dbstate.db.find_backlink_handles(event_handle)
                                    if ref_type == 'Person' 
                                      ]
                        if person_list:
                            descr = "<br>"
                            for person in person_list:
                                descr = ("%(description)s%(name)s<br>") % {
                                            'description' : descr, 
                                            'name' : _nd.display(person)}
                            descr = ("%(eventtype)s; %(place)s%(description)s"
                                     ) % { 'eventtype': gen.lib.EventType(
                                                            event.get_type()),
                                            'place': place.get_title(), 
                                            'description': descr}
                        else:
                            descr = ("%(eventtype)s; %(place)s<br>") % {
                                            'eventtype': gen.lib.EventType(
                                                            event.get_type()),
                                            'place': place.get_title()}
                        self.append_to_places_list(descr1, descr,
                                                   descr,
                                                   latitude, longitude,
                                                   descr2, self.center,
                                                   eventyear)
                        self.center = False
                    else:
                        descr = place.get_title()
                        self.append_to_places_without_coord(place.gramps_id,
                                                            descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
        else:
            mess = ""
        self.create_pages(2, _("All events in the family tree with coordinates."
                             ), mess)

    def createmapstractionfamily(self, dbstate):
        """
        This function create all markers for each people of a family
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
                father_handle = fam.get_father_handle()
                father = dbstate.db.get_person_from_handle(father_handle)
                if father:
                    comment = _("Id : Father : %s") % father.gramps_id
                    self.createpersonmarkers(dbstate, father, comment)
                mother_handle = fam.get_mother_handle()
                mother = dbstate.db.get_person_from_handle(mother_handle)
                if mother:
                    comment = _("Id : Mother : %s") % mother.gramps_id
                    self.createpersonmarkers(dbstate, mother, comment)
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
                            self.createpersonmarkers(dbstate, child, comment)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
            if person is not None:
                self.create_pages(3, _("The active person's family members "
                                       "have no places with coordinates."), 
                                    mess)
            else:
                self.create_pages(3, _("No active person set."), mess)
        else:
            mess = ""
            self.create_pages(3,
                              ( _("All %(name)s people's family places in the "
                                  "family tree with coordinates.") % {
                                     'name' :_nd.display(person) }),
                                mess)

    def createmapstractionperson(self, dbstate):
        """
        This function create all markers for each people's event
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
                        self.append_to_places_list(descr, evt,
                                                   _nd.display(person),
                                                   latitude, longitude,
                                                   descr1, self.center, 
                                                   eventyear)
                        self.center = False
                    else:
                        self.append_to_places_without_coord(
                                                        place.gramps_id, descr)
        if self.center:
            mess = _("Cannot center the map. No location with coordinates.")
            if person is not None:
                self.create_pages(4, 
                _("The active person has no places with coordinates."), mess)
            else:
                self.create_pages(4, _("No active person set."), mess)
        else:
            mess = ""
            self.create_pages(4, ( _("All event places for %s.") % 
                                        _nd.display(person) ), mess)

    def createmapnotimplemented(self):
        """
        This function is used to inform the user this work is not implemented.
        """
        self.mapview.write("  <H1>%s </H1>" % _("Not yet implemented ..."))

