# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Serge Noiraud
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

# $Id: GoogleView.py 9598 2007-12-27 15:24:30Z dsblank $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
from cgi import escape
import math
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

try:
    import cairo
    cairo_available = True
except:
    cairo_available = False

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
import PageView
#from BasicUtils import name_displayer
import Utils
#import DateHandler
#import ThumbNails
import Errors
#from ReportBase import ReportUtils
#from Editors import EditPerson, EditFamily 
#from DdTargets import DdTargets
#import cPickle as pickle
#import Config
#from QuestionDialog import RunDatabaseRepair, ErrorDialog
import gtkmozembed
import urlparse


#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
MOZEMBED_PATH = "/tmp/"
MOZEMBED_SUBPATH = "browser"

#-------------------------------------------------------------------------
#
# GoogleView
#
#-------------------------------------------------------------------------
class GoogleView(PageView.PersonNavView):

    def __init__(self,dbstate,uistate):
        PageView.PersonNavView.__init__(self, _('GoogleView'), dbstate, uistate)
        
        self.func_list = {
            '<CONTROL>J' : self.jump,
            }

        self.dbstate = dbstate

    def _on_url(self, widget):
        self.m.load_url(widget.get_text())

    def _quit(self, widget):
        gtk.main_quit()

    def set_mozembed_proxy(self):
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
        fd = file(MOZEMBED_PATH+MOZEMBED_SUBPATH+"/prefs.js","w+")
        fd.write(data)
        fd.close()

    def change_page(self):
        self.uistate.clear_filter_results()

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
        return 'gramps-place'

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        self.tooltips = gtk.Tooltips()
        self.tooltips.enable()
        
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
            
        self.table_2 = gtk.Table(1,1,False)
        self.add_table_to_notebook( self.table_2)

        if hasattr(gtkmozembed, 'set_profile_path'):
            set_profile_path = gtkmozembed.set_profile_path
        else:
            set_profile_path = gtkmozembed.gtk_moz_embed_set_profile_path
        set_profile_path(MOZEMBED_PATH, MOZEMBED_SUBPATH)
        self.m = gtkmozembed.MozEmbed()
        self.set_mozembed_proxy()
        self.m.set_size_request(800,600)
        self.table_2.add(self.m)

        #d = {}
        #for iteration in dir(self.__class__):
        #    d[iteration]=getattr(self, iteration)
        #ui.signal_autoconnect(d)
        self.m.show()
        return self.notebook

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="GoogleMaps"/>
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
        self._add_action('GoogleMaps', gtk.STOCK_JUMP_TO, _('_GoogleMaps'),
                         callback=self.google_places,
                         tip=_("Attempt to map places on Google Maps"))

        PageView.PersonNavView.define_actions(self)

    def goto_active_person(self,handle=None):
        self.google_places(handle)

    def google_places(self,htmlfile):
        htmlfile = MOZEMBED_PATH+"/index.html"
        self.createHtml()
	self.m.load_url("file://"+htmlfile)

    def createHtml(self):
        from PlaceUtils import conv_lat_lon
        db=self.dbstate.db
        tmpdir = MOZEMBED_PATH
        google = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
        google += "            \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
        google += "    <html xmlns=\"http://www.w3.org/1999/xhtml\"  xmlns:v=\"urn:schemas-microsoft-com:vml\">\n"
        google += "    <head>\n"
        google += "            <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n"
        google += "            <title>Google Maps JavaScript API Example</title>\n"
        google += "            <script id=\"googleapiimport\" src=\"http://maps.google.com/maps?file=api&amp;v=2\"\n"
        google += "                    type=\"text/javascript\"></script>\n"
        google += "            <script type=\"text/javascript\">\n"
        google += "            //<![CDATA[\n"
        google += """
            function createMarker(point,html) { 
                    var marker = new GMarker(point); 
                    GEvent.addListener(marker, "click", function() { marker.openInfoWindowHtml(html); }); 
                    return marker;
                    }

"""

        google += "            function load() {\n"
        google += "                    if (GBrowserIsCompatible()) {\n"
        google += "                            var map = new GMap2(document.getElementById(\"map\"));\n"
        google += "                            map.addControl(new GLargeMapControl());\n"
        google += "                            map.addControl(new GMapTypeControl());\n"
        google += "                            map.addControl(new GScaleControl());\n"
        #
        # We center the map on the home person if we can.
        #
        latitude = ""
        longitude = ""
        #person = db.find_person_from_handle(self.home, self.trans)
        person = db.get_default_person()
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = db.get_event_from_handle(birth_ref.ref)
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    place = db.get_place_from_handle(bplace_handle)
                    longitude = place.get_longitude()
                    latitude = place.get_latitude()
            else:
                death_ref = person.get_death_ref()
                if death_ref:
                    death = db.get_event_from_handle(death_ref.ref)
                    bplace_handle = death.get_place_handle()
                    if bplace_handle:
                        place = db.get_place_from_handle(bplace_handle)
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
        if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
            centered=1
            latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
            centeredPoint = "%s:%s"%(latitude, longitude)
            google += "                            centeredPoint = new GLatLng(%f,%f)\n"%(float(latitude),float(longitude))
            google += "                            map.setCenter(centeredPoint, 13);\n"
        else:
            centered=0
            #latitude, longitude = conv_lat_lon(float(-1.568792), float(47.257971), "D.D8")
        google += "                            ovMap=new GOverviewMapControl();\n"
        google += "                            map.addControl(ovMap);\n"
        google += "                            mini=ovMap.getOverviewMap();\n"
        for place_handle in db.get_place_handles():
            place = db.get_place_from_handle( place_handle)
            if place:
                descr = place.get_title()
                longitude = place.get_longitude()
                latitude = place.get_latitude()
                city = place.get_main_location().get_city()
                country = place.get_main_location().get_country()
                if ( cmp(longitude,"") == 1 | cmp(latitude,"") == 1 ):
                    google += "                            var point = new GLatLng('%s','%s')\n"%(latitude,longitude)
                    if ( centered == 0 ):
                        centered = 1
                        google += "                            map.setCenter(point, 13);\n"
                        google += "                            res = createMarker(point,'<div>%s<br>%s<br>%s<br><br>%s</div>')\n"%(city,country,descr,_("This is the first place we found with a geographical location."))
                    else:
                        latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                        newP = "%s:%s"%(latitude, longitude)
                        if ( centeredPoint == newP ):
                            google += "                            res = createMarker(point,'<div>%s<br>%s<br>%s<br><br>%s</div>')\n"%(city,country,descr,_("This is the place for the home person."))
                        else:
                            google += "                            res = createMarker(point,'<div>%s<br>%s<br>%s<br><br>%s</div>')\n"%(city,country,descr,_("This is a common place we found with a geographical location."))
                    google += "                            map.addOverlay(res);\n"
        if ( centered == 0 ):
            # We have no valid geographic point to center the map.
            # So you'll see the street where I live.
            longitude = -1.568792
            latitude = 47.257971
            google += "                            var point = new GLatLng('%s','%s')\n"%(latitude,longitude)
            google += "                            map.setCenter(point, 13);\n"
            google += "                            res = createMarker(point,'<div>Serge Noiraud<br>Nantes, France<br>%s</div>')\n"%_("The author of this view. You see that because you have no location in your database.")
            google += "                            map.addOverlay(res);\n"
        google += "                            document.getElementById('map').style.top='0px';\n"
        google += "                            document.getElementById('map').style.left='0px';\n"
        google += "                            document.getElementById('map').style.width='100%';\n"
        google += "                            }\n"
        google += "                    }\n     "
        google += "            //]]>\n"
        google += "    </script>\n"
        google += "    </head>\n"
        google += "    <body onload=\"load()\" onunload=\"GUnload()\">\n"
        google += "            <div id=\"map\" style=\"width: 1000x; height: 600px\"></div>\n"
        google += "    </body>\n"
        google += "</html>\n"
        fd = file(MOZEMBED_PATH+"/index.html","w+")
        fd.write(google)
        fd.close()
