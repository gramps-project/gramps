#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
import gc
import logging
import os
import math
import urllib
import urllib2
import tempfile
from xml.dom.minidom import parseString as xmlStringParser

use_online_map = False

log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import PageView
import const

# Some initial places for debugging
glob_loc_data = [ # (Name, longitude, latitude)
        ("_Center", 0,0),
        ("_North",0,90),
        ("_South",0,-90),
        ("_West",-180,0),
        ("_East",180,0),
        ("Chicago",-87.75,41.83),
        ("Berlin",13.42,52.53),
        ("Honolulu",-157.83,21.32),
        ("Madrid",-3.72,40.42),
        ("Moscow",37.70,55.75),
        ("Vienna",16.37,48.22),
        ("Sidney",151.17,-33.92),
        ("Rio de Janeiro",-43.28,-22.88),
        ("Tokyo",139.75,35.67),
        ("Cape Town",18.47,-33.93),
        ("Anchorage",-150.00,61.17),
        ("Mannheim-Wallstadt",8.55,49.48),
        ("Mannheim-Neckarau",8.48,49.45),
        ("Gorxheimertal",8.73,49.53)]

enable_debug = True


# Draws a map image and tries to allocate space in the correct aspect ratio
class GuideMap(gtk.DrawingArea):
    def __init__(self, map_pixbuf):
        gtk.DrawingArea.__init__(self)
        self.map_pixbuf = map_pixbuf
        self.connect("expose-event", self.expose_cb)
        self.connect("size-allocate", self.size_allocate_cb)
        self.gc = None
        self.current_area = None
        self.current_spot = None
        self.old_size = (-1,-1)
    
    # Set hightlight region
    def hightlight_area( self, area):
        self.current_area = area
        self.queue_draw()

    # Set hightlight region
    def hightlight_spot( self, spot):
        self.current_spot = spot
        self.queue_draw()

    # Redraw the image
    def expose_cb(self,widget,event):
        if not self.gc:
            self.gc = self.window.new_gc()
            self.gc.set_foreground( self.get_colormap().alloc_color("red"))
            self.gc.set_background( self.get_colormap().alloc_color("blue"))
        if self.backbuf and self.gc:
            self.window.draw_pixbuf( self.gc, self.backbuf, 0,0, 0,0, -1,-1)
            if self.current_area:
                r = self.map_to_screen(self.current_area[0],
                                       self.current_area[1],
                                       self.current_area[2],
                                       self.current_area[3])
                self.window.draw_rectangle( self.gc, False,
                                            r[0],r[1],r[2],r[3])
            if self.current_spot:
                r = self.map_to_screen(self.current_spot[0],
                                       self.current_spot[1])
                self.window.draw_line( self.gc,0,r[1],
                                       self.backbuf.get_width(),r[1])
                self.window.draw_line( self.gc,r[0],0,
                                       r[0],self.backbuf.get_height())
                

    # Scale backbuffer
    def size_allocate_cb(self,widget,allocation):
        # Always request a height, that is half of the width
        w = max( 128,allocation.width)
        self.set_size_request(-1,w/2)
        
        # only create new backbuffer if size is different
        new_size = (allocation.width,allocation.height)
        if new_size is not self.old_size:
            self.old_size = new_size
            self.backbuf = self.map_pixbuf.scale_simple(
                self.old_size[0],
                self.old_size[1],
                gtk.gdk.INTERP_BILINEAR)
            gc.collect()

    def map_to_screen( self, x,y,w=None,h=None):
        px = int((float(x) + 180.0) / 360.0 * self.backbuf.get_width())
        py = int((90-float(y)) / 180.0 * self.backbuf.get_height())
        if w and h:
            pw = int(float(w) / 360.0 * self.backbuf.get_width())
            ph = int(float(h) / 180.0 * self.backbuf.get_height())
            return (px,py,pw,ph)
        return (px,py)

# Map tile files used by the ZoomMap
class MapTile:
    def __init__( self, filename, x, y, w, h, pw, ph):
        self.filename = filename
        self.full_path = os.path.join(const.image_dir,filename)
        self.map_x = float(x)
        self.map_y = float(y)
        self.map_width = float(w)
        self.map_height = float(h)
        self.map_pixel_width = float(pw)
        self.map_pixel_height = float(ph)
        self.source_pixbuf = None
        self.source_scale = self.map_pixel_width / self.map_width
        self.scale = None
        self.scaled_pixbuf = None
        self.scaled_map_x = None
        self.scaled_map_y = None

    def set_viewport( self, target_scale, x_in, y_in, w_in, h_in):
        # intersect viewport with map area
        x = max(self.map_x, max(-180.0,x_in))
        y = min(self.map_y, min(  90.0,y_in))
        xmax = min( min(180.0,x_in+w_in), self.map_x+self.map_width)
        ymin = max( max(-90.0,y_in-h_in), self.map_y-self.map_width)
        w = xmax-x
        h = y-ymin
        
        if w > 0.0 and h > 0.0:
            # crop source tile to not scale the whole image_dir
            xoffset = max(0,math.floor((x - self.map_x) * self.source_scale))
            xmax = max(0,math.ceil((x+w - self.map_x) * self.source_scale))
            yoffset = min(self.map_pixel_width,math.floor(-(y - self.map_y) * self.source_scale))
            ymax = min(self.map_pixel_height,math.ceil(-(y-h - self.map_y) * self.source_scale))

            rescale = target_scale / self.source_scale
            if int((xmax-xoffset)*rescale) > 0 and int((ymax-yoffset)*rescale) > 0:
                self.scaled_map_x = self.map_x + xoffset / self.source_scale
                self.scaled_map_y = self.map_y - yoffset / self.source_scale
                self.scaled_map_pixel_w = int((xmax-xoffset)*rescale)
                self.scaled_map_pixel_h = int((ymax-yoffset)*rescale)
                
                if enable_debug:
                    print 
                    print "Source-Map origin: %f x %f, %f, %f" % (self.map_x,self.map_y,self.map_width,self.map_height)
                    print "Source-Map pixels: %f x %f" % (self.map_pixel_width,self.map_pixel_height)
                    print "Source-Map scale: %f" % self.source_scale
                    print "Target origin: %f x %f, %f, %f" % (x,y,w,h)
                    print "Target scale: %f" % target_scale
                    print "Target crop: %f x %f, %f x %f" % (xoffset,yoffset,xmax,ymax)
                    print "Origin of crop: %f x %f" % (self.scaled_map_x,self.scaled_map_y)
                    print "scaled tile size: %f x %f pix" % (self.scaled_map_pixel_w,self.scaled_map_pixel_h)

                try:
                    if not self.source_pixbuf:
                        self.source_pixbuf = gtk.gdk.pixbuf_new_from_file( self.full_path)
        
                    clip_pixbuf = self.source_pixbuf.subpixbuf(int(xoffset),int(yoffset),int(xmax-xoffset),int(ymax-yoffset))
                        
                    self.scale = target_scale
                    self.scaled_pixbuf = clip_pixbuf.scale_simple( int((xmax-xoffset)*rescale), int((ymax-yoffset)*rescale), gtk.gdk.INTERP_BILINEAR)
                    clip_pixbuf = None
                except:
                    pass

            else:
                self.scale = None
                self.scaled_pixbuf = None
        else:
            self.scale = None
            self.scaled_pixbuf = None

    def free(self):
        self.scale = None
        self.scaled_pixbuf = None

class WMSMapTile:
    def __init__(self,capabilities):
        self.scaled_pixbuf = None
        self.capabilities_url = capabilities
        u_reader = urllib2.urlopen(self.capabilities_url)
        response_body = u_reader.read()
        u_reader.close()
        xml_doc = xmlStringParser( response_body)
        # validate name of root element
        e = xml_doc.documentElement
        if e.nodeName != "WMT_MS_Capabilities":
            print "unsupported Document type '%s'" % e.nodeName
            return None
        self.map_request_params = {}
        self.map_request_params["VERSION"] = e.getAttribute("version")
        self.map_request_params["REQUEST"] = "GetMap"
        self.map_request_params["SERVICE"] = "WMS"
        self.map_request_params["REQUEST"] = "GetMap"
        self.map_request_params["REQUEST"] = "GetMap"
        self.map_request_params["FORMAT"] = "image/png"
        self.map_request_params["SRS"] = "epsg:4326"
        self.map_request_params["LAYERS"] = ""
        # Child-nodes of root element
        for n in e.childNodes:
            if n.nodeName == "Service":
                # Parse Service header
                map_title = n.getElementsByTagName("Title")[0].firstChild.data
                print " MAP Title: %s" % map_title
                try:
                    map_fees = e.getElementsByTagName("Fees")[0].firstChild.data
                except IndexError:
                    map_fees = "-"
                print " MAP Fees: %s" % map_fees
                try:
                    map_access_constraints = e.getElementsByTagName("AccessConstraints")[0].firstChild.data
                except IndexError:
                    map_access_constraints = "-"
                print " MAP AccessConstraints: %s" % map_access_constraints
    
            elif n.nodeName == "Capability":
                # Parse Capabilities
                for n2 in n.childNodes:
                    if n2.nodeName == "Request":
                        t1 = n2.getElementsByTagName("GetMap")[0]
                        t2 = t1.getElementsByTagName("DCPType")[0]
                        t3 = t2.getElementsByTagName("HTTP")[0]
                        t4 = t3.getElementsByTagName("Get")[0]
                        t5 = t4.getElementsByTagName("OnlineResource")[0]
                        self.map_get_url = t5.getAttribute("xlink:href")
                        print(" Map Tile base url: %s" % self.map_get_url)
                    elif n2.nodeName == "Layer":
                        # parse Layers
                        if not self._srs_is_supported(n2.getElementsByTagName("SRS")[0].firstChild.data):
                            print "Layer coordinates not supported :-("
                            return None
                        layer_title = n2.getElementsByTagName("Title")[0].firstChild.data
                        print " Layer: %s" % layer_title
                        for n3 in n2.childNodes:
                            if n3.nodeName == "Layer":
                                # parse Layers
                                layer_title = n3.getElementsByTagName("Title")[0].firstChild.data
                                print "   - Layer: %s" % layer_title
                                if self.map_request_params["LAYERS"]:
                                    self.map_request_params["LAYERS"] += ","
                                self.map_request_params["LAYERS"] += layer_title
    def _srs_is_supported( self, srs_string):
        list = srs_string.lower().split()
        if "epsg:4326" in list:
            return True
        return False
        
    def set_viewport( self, target_scale, x_in, y_in, w_in, h_in):
        self.scaled_map_x = x_in
        self.scaled_map_y = y_in
        self.scaled_map_pixel_w = int(w_in*target_scale)
        self.scaled_map_pixel_h = int(h_in*target_scale)
        self.map_request_params["BBOX"] = "%f,%f,%f,%f" % (x_in,y_in-h_in,x_in+w_in,y_in) # Neds to be set for request
        self.map_request_params["WIDTH"] = int(w_in*target_scale)
        self.map_request_params["HEIGHT"] = int(h_in*target_scale)
        params = urllib.urlencode(self.map_request_params)
        f = tempfile.NamedTemporaryFile()
        f_name = f.name
        urllib.urlretrieve(self.map_get_url+params,f_name)
        self.scaled_pixbuf = gtk.gdk.pixbuf_new_from_file(f_name)

    def free(self):
        pass

# Zoomable map image
class ZoomMap( gtk.DrawingArea):
    def __init__( self, place_marker_pixbuf, hightlight_marker_pixbuf):
        gtk.DrawingArea.__init__(self)
        self.place_marker_pixbuf = place_marker_pixbuf
        self.hightlight_marker_pixbuf = hightlight_marker_pixbuf
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)  # position overlay
        self.connect("expose-event", self.expose_cb)
        self.connect("size-allocate", self.size_allocate_cb)
        if enable_debug:
            self.connect("motion-notify-event", self.motion_notify_event_cb)
        self.gc = None
        self.current_pixel_size = (-1,-1)
        self.zoom_pos = (0,0)
        self.magnifer = 0.0 # in pixel per degree
        self.guide = None
        self.textlayout = self.create_pango_layout("")
        self.map_sources = {}
        self.initial_exposed = False
        if use_online_map:
            self.map_sources[0.0] = []
            self.map_sources[0.0].append(WMSMapTile("http://www2.demis.nl/wms/wms.asp?wms=WorldMap&VERSION=1.1.1&REQUEST=GetCapabilities"))

    def add_map_source( self,filename, x, y, w, h,pw,ph):
        tile = MapTile( filename, x, y, w, h, pw, ph)
        if not tile.source_scale in self.map_sources:
            self.map_sources[tile.source_scale] = []
        self.map_sources[tile.source_scale].append( tile)
        
    # Set the guide map that should follow the zoom area
    def set_guide( self, guide):
        self.guide = guide

    def set_location_model( self, model, idx_name, idx_long, idx_lat):
        self.location_model = model
        self.idx_name = idx_name
        self.idx_long = idx_long
        self.idx_lat = idx_lat
        
    def motion_notify_event_cb(self,widget,event):
        self.textlayout.set_text( "Position: %03.0f,%03.0f pixel" % (event.x,event.y))
        (w,h) = self.textlayout.get_pixel_size()
        self.gc.set_foreground( self.get_colormap().alloc_color("white"))
        self.window.draw_rectangle( self.gc, True, 10,50,w,h)
        self.gc.set_foreground( self.get_colormap().alloc_color("red"))
        self.window.draw_layout( self.gc, 10, 50, self.textlayout)
        (lon,lat) = self.screen_to_map(event.x,event.y)
        self.textlayout.set_text( "Position: %03.0f,%03.0f degree" % (lon,lat))
        (w,h) = self.textlayout.get_pixel_size()
        self.gc.set_foreground( self.get_colormap().alloc_color("white"))
        self.window.draw_rectangle( self.gc, True, 10,70,w,h)
        self.gc.set_foreground( self.get_colormap().alloc_color("red"))
        self.window.draw_layout( self.gc, 10, 70, self.textlayout)
        
    # Redraw the image
    def expose_cb(self,widget,event):
        if not self.gc:
            self.gc = self.window.new_gc()
            self.gc.set_foreground( self.get_colormap().alloc_color("red"))
            self.gc.set_background( self.get_colormap().alloc_color("blue"))
        if not self.backbuf:
            self.size_allocate_cb( self,self.get_allocation())
        if self.backbuf and self.gc:
            #draw all maps
            scales = self.map_sources.keys()
            scales.sort()
            for scale in scales:
                for map in self.map_sources[scale]:
                    if map.scaled_pixbuf:
                        (px,py) = self.map_to_screen( map.scaled_map_x, map.scaled_map_y)
                        self.window.draw_pixbuf( self.gc, map.scaled_pixbuf, 0,0, px,py)
                        if enable_debug:
                            self.window.draw_rectangle( self.gc, False, px,py,map.scaled_map_pixel_w,map.scaled_map_pixel_h)
                            self.window.draw_line( self.gc, px,py,px+map.scaled_map_pixel_w,py+map.scaled_map_pixel_h)
                            self.window.draw_line( self.gc, px,py+map.scaled_map_pixel_h,px+map.scaled_map_pixel_w,py)
            gc.collect()


            # draw all available locations
            if self.location_model:
                iter = self.location_model.get_iter_first()
                while iter:
                    (n,x,y) = self.location_model.get( iter, self.idx_name, self.idx_long, self.idx_lat)
                    (px,py) = self.map_to_screen( x, y)
                    #if px > 0 and py > 0 and px < self.backbuf.get_width() and py < self.backbuf.get_height():
                        # draw only visible markers
                        #self.window.draw_pixbuf(
                        #    self.gc,
                        #    self.place_marker_pixbuf,
                        #    0,0,
                        #    px-self.place_marker_pixbuf.get_width()/2,
                        #    py-self.place_marker_pixbuf.get_height()/2,
                        #   -1,-1)
                    self.textlayout.set_text(n)
                    self.window.draw_layout(
                           self.gc,
                           px,py,
                           self.textlayout)
                    iter = self.location_model.iter_next( iter)
            
            # hightlight current location
            (px,py) = self.map_to_screen( self.zoom_pos[0], self.zoom_pos[1])
            self.window.draw_pixbuf(
                self.gc,
                self.hightlight_marker_pixbuf,
                0,0,
                px-self.hightlight_marker_pixbuf.get_width()/2,
                py-self.hightlight_marker_pixbuf.get_height()/2,
                -1,-1)
            #self.window.draw_rectangle( self.gc, False, px-3,py-3, 6,6)
            
            #(px1,py1) = self.map_to_screen(-180, 90)
            #(px2,py2) = self.map_to_screen( 180,-90)
            #self.window.draw_rectangle( self.gc, False, px1,py1,px2-px1,py2-py1)
            #self.window.draw_line( self.gc, px1,py1,px2,py2)
            #self.window.draw_line( self.gc, px1,py2,px2,py1)
            if enable_debug:
                # Output debugging info
                self.textlayout.set_text( "Magnifer: %f pixel per degree" % self.magnifer)
                self.window.draw_layout( self.gc, 10, 10, self.textlayout)
                self.textlayout.set_text( "Current map: %f pixel per degree" % self.selected_map_scale)
                self.window.draw_layout( self.gc, 10, 30, self.textlayout)

    def map_to_screen( self, lon, lat):
        px = int(self.current_pixel_size[0] / 2.0 + (lon - self.zoom_pos[0]) * self.magnifer)
        py = int(self.current_pixel_size[1] / 2.0 - (lat - self.zoom_pos[1]) * self.magnifer)
        return( px, py)

    def screen_to_map( self, px, py):
        px = float(px)
        py = float(py)
        lon = (px - self.current_pixel_size[0]/2) / self.magnifer + self.zoom_pos[0];
        lat = -(py - self.current_pixel_size[1]/2) / self.magnifer + self.zoom_pos[1];
        return( lon, lat)

    # Scale backbuffer
    def size_allocate_cb(self,widget,allocation):
        # only create new backbuffer if size is different
        new_size = (allocation.width,allocation.height)
        if new_size is not self.current_pixel_size or not self.backbuf:
            self.backbuf = True
            self.current_pixel_size = new_size
            if self.magnifer == 0.0:
                # scale map to full width
                self.magnifer = self.current_pixel_size[0] / 360.0
            x0,y0 = self.screen_to_map( 0, 0)
            x1,y1 = self.screen_to_map( new_size[0], new_size[1])
            self.guide.hightlight_area( (x0,y0,x1-x0, y0-y1))
            
            def cmpfunc(s):
                return((self.magnifer-s)*(self.magnifer-s))
                
            # select best matching tile set
            self.selected_map_scale = None
            smallest_scale = None
            largest_scale = None
            for s in self.map_sources.keys():
                if not self.selected_map_scale or cmpfunc(s) < cmpfunc(self.selected_map_scale):
                    self.selected_map_scale = s
                if not smallest_scale or s < smallest_scale:
                    smallest_scale = s
                if not largest_scale or s > largest_scale:
                    largest_scale = s
            if enable_debug:
                print "scale of display: %f" % self.magnifer
                print "available map scales:"
                print self.map_sources.keys()
                print "largest scale: %f" % largest_scale
                print "smallest scale: %f" % smallest_scale
                print "selected scale: %f" % self.selected_map_scale
            
            for s in self.map_sources.keys():
                for map in self.map_sources[s]:
                    if s == self.selected_map_scale or s == smallest_scale:
                        map.set_viewport( self.magnifer, x0, y0, x1-x0, y0-y1)
                    else:
                        map.free()

    # Scroll to requested position
    def scroll_to( self, long, lat):
        self.zoom_pos = (float( min(180,(max(-180,long)))), float(min(90,(max(-90,lat)))))
        self.backbuf = None
        if self.guide:
            self.guide.hightlight_spot( self.zoom_pos)
        self.queue_draw()

    def zoom_out(self):
        self.magnifer = max( 1.0, self.magnifer * 2.0/3.0)
        self.backbuf = None
        self.queue_draw()
    
    def zoom_in(self):
        self.magnifer = min( 1000.0, self.magnifer * 1.5)
        self.backbuf = None
        self.queue_draw()
    
    def zoom_normal(self):
        self.magnifer = 1.0
        self.magnifer = self.selected_map_scale
        self.backbuf = None
        self.queue_draw()

    def zoom_fit(self):
        self.magnifer = self.current_pixel_size[0] / 360.0
        self.backbuf = None
        self.queue_draw()


# Place list widget
class MapPlacesList(gtk.TreeView):
    def __init__(self, data):
        self.lstore = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_FLOAT,
            gobject.TYPE_FLOAT)
        
        self.change_data( data)

        gtk.TreeView.__init__(self, self.lstore)
        self.set_rules_hint(True)
        self.set_search_column(0)

        column = gtk.TreeViewColumn('Place', gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.append_column(column)

        column = gtk.TreeViewColumn('Lat', gtk.CellRendererText(), text=1)
        column.set_sort_column_id(1)
        self.append_column(column)

        column = gtk.TreeViewColumn('Long', gtk.CellRendererText(),text=2)
        column.set_sort_column_id(2)
        self.append_column(column)

    def change_data( self, data):
        self.lstore.clear()
        for item in data:
            iter = self.lstore.append()
            self.lstore.set(iter,
                0, item[0],
                1, item[1],
                2, item[2])



# Map View main class
class MapView(PageView.PageView):
    def __init__(self,dbstate,uistate):
        PageView.PageView.__init__(self, _('Maps'), dbstate, uistate)
        dbstate.connect('database-changed',self.change_db)
        self.current_marker = None

    def navigation_type(self):
        return PageView.NAVIGATION_NONE

    def define_actions(self):
        self.add_action('ZoomIn',gtk.STOCK_ZOOM_IN,
                        _("Zoom _In"),tip=_("Zoom in by a factor of 2"),
                        callback=self.zoom_in_cb)
        self.add_action('ZoomOut',gtk.STOCK_ZOOM_OUT,
                        _("Zoom _Out"),tip=_("Zoom out by a factor of 2"),
                        callback=self.zoom_out_cb)
        self.add_action('ZoomNormal',gtk.STOCK_ZOOM_100,
                        _("_Normal Size"), tip=_("Return to normal size"),
                        callback=self.zoom_100_cb)
        self.add_action('ZoomFit',gtk.STOCK_ZOOM_FIT,
                        _("Best _Fit"),
                        tip=_("Produce the best fit of the map in the window"),
                        callback=self.zoom_fit_cb)

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-map'


    # For debugging: Reads in location from xearth
    def get_xearth_markers(self):
        data = []
        try:
            f = open("/etc/xearth/xearth.markers")
            l = f.readline()
            #linere = re.compile('[^0-9.-]*(-?[0-9]+\.[0-9]+)[^0-9.-]*(-?[0-9]+\.[0-9]+).*"([^"])".*', "I")
            while l:
                if not l[0] == "#":
                    l = l.strip().replace('"',"").replace("    "," ").replace("   "," ").replace("  "," ").replace(" # ",", ")
                    m = l.split( None, 2)
                    if len(m) == 3:
                        data.append( (m[2],float(m[1]),float(m[0])))
                l = f.readline()
        except IOError:
            pass
        return data

    # Reads in locations from current GRAMPS database
    def get_markers_from_database(self, db):
        data = []
        for place_handle in db.get_place_handles():
            place = db.get_place_from_handle( place_handle)
            if place:
                try:
                    data.append( (place.get_title(),float(place.get_longitude()),float(place.get_latitude())))
                except (TypeError, ValueError):
                    # ignore places that dont have usable data
                    pass
        return data

    # Reads in textfiles from NIMA:
    # http://earth-info.nga.mil/gns/html/cntry_files.html
    def parse_nima_countryfile(self, filename):
        import csv
        data = []
        try:
            csvreader = csv.reader(open(filename), "excel-tab")
            l = csvreader.next()    # skip header
            l = csvreader.next()
            line = 1
            while l:
                if l[17] == "N" and l[9] == "P":
                    city = l[22]
                    lat = float( l[3])
                    lon = float( l[4])
                    
                    if line % 10 == 0:
                        data.append( (city, lon, lat))
                l = csvreader.next()
                line = line + 1
        except (IOError,StopIteration):
            pass
        return data

    def build_widget(self):
        hbox = gtk.HBox( False, 4)
        hbox.set_border_width( 4)

        no = gtk.Image()
        # The large zoomable map
        self.zoom_map = ZoomMap( 
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"bad.png")),
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"good.png")))
        if not use_online_map:
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_0.jpg', -180,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_1.jpg', -135,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_2.jpg', -90,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_3.jpg', -45,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_4.jpg', 0,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_5.jpg', 45,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_6.jpg', 90,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_0_7.jpg', 135,90, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_0.jpg', -180,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_1.jpg', -135,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_2.jpg', -90,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_3.jpg', -45,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_4.jpg', 0,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_5.jpg', 45,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_6.jpg', 90,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_1_7.jpg', 135,45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_0.jpg', -180,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_1.jpg', -135,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_2.jpg', -90,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_3.jpg', -45,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_4.jpg', 0,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_5.jpg', 45,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_6.jpg', 90,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_2_7.jpg', 135,0, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_0.jpg', -180,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_1.jpg', -135,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_2.jpg', -90,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_3.jpg', -45,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_4.jpg', 0,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_5.jpg', 45,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_6.jpg', 90,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x3200x1600_tile_3_7.jpg', 135,-45, 45,45, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_0_0.jpg', -180,90, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_0_1.jpg', -90,90, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_0_2.jpg', 0,90, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_0_3.jpg', 90,90, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_1_0.jpg', -180,0, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_1_1.jpg', -90,0, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_1_2.jpg', 0,0, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x1600x800_tile_1_3.jpg', 90,0, 90,90, 400,400)
            self.zoom_map.add_map_source('world.topo.200407.3x800x400.jpg', -180,90, 360,180, 800,400)
            self.zoom_map.add_map_source('world.topo.200407.3x400x200.jpg', -180,90, 360,180, 400,200)
            self.zoom_map.add_map_source('world.topo.200407.3x128x60.jpg', -180,90, 360,180, 128,60)

        self.zoom_map.set_size_request(300,300)
        hbox.pack_start( self.zoom_map, True, True, 0)
        
        # On the right side
        vbox = gtk.VBox( False, 4)
        hbox.pack_start( vbox, False, False, 0)
        
        # The small guide map
        self.guide_map = GuideMap(
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"world.topo.200407.3x128x60.jpg")))
        self.guide_map.set_size_request(128,64)
        vbox.pack_start( self.guide_map, False, True, 0)
        
        self.zoom_map.set_guide(self.guide_map)
        
        # and the place list
        self.place_list_view = MapPlacesList( [])
        self.zoom_map.set_location_model(self.place_list_view.get_model(), 0,1,2)
        self.place_list_view.connect("cursor-changed", self.entry_select_cb)
        self.place_list_view.set_size_request(128,-1)
        vport = gtk.ScrolledWindow()
        vbox.pack_start(vport,True,True,0)
        vport.add( self.place_list_view)

        self.rebuild_places()
        
        return hbox

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <toolbar name="ToolBar">
            <toolitem action="ZoomIn"/>  
            <toolitem action="ZoomOut"/>  
            <toolitem action="ZoomNormal"/>
            <toolitem action="ZoomFit"/>
          </toolbar>
        </ui>'''

    def change_db(self,db):
        """
        Callback associated with DbState. Whenenver the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tere
        is no need to store the database, since we will get the value
        from self.state.db
        """
        db.connect('place-rebuild',self.rebuild_places)
        db.connect('place-update',self.rebuild_places)
    
    def rebuild_places(self,handle_list=None):
        d = glob_loc_data
        try:
            d = d + self.get_xearth_markers()
            #d = self.parse_nima_countryfile("/tmp/gm.txt")
            d = d + self.get_markers_from_database( self.dbstate.db)
        except:
            log.error("Failed to rebuild places.", exc_info=True)
        self.place_list_view.change_data( d)

    def entry_select_cb(self,treeview):
        s = treeview.get_selection()
        (model,sel) = s.get_selected_rows()
        for path in sel:
            iter = model.get_iter(path)
            self.zoom_map.scroll_to(model.get_value(iter,1),
                                    model.get_value(iter,2))
            break

    def zoom_in_cb(self,obj):
        self.zoom_map.zoom_in()

    def zoom_out_cb(self,obj):
        self.zoom_map.zoom_out()

    def zoom_100_cb(self,obj):
        self.zoom_map.zoom_normal()

    def zoom_fit_cb(self,obj):
        self.zoom_map.zoom_fit()
