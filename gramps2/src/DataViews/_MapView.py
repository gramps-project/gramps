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
import re
import logging
import os

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
import RelLib
import PageView
import const

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
        ("Anchorage",-150.00,61.17)]


# Draws a map image and tries to allocate space in the correct aspect ratio
class GuideMap(gtk.DrawingArea):
    def __init__(self, map_pixbuf):
        gtk.DrawingArea.__init__(self)
        self.map_pixbuf = map_pixbuf
        self.connect("expose-event", self.expose_cb)
        self.connect("size-allocate", self.size_allocate_cb)
        self.gc = None
        self.current_area = None
        self.old_size = (-1,-1)
    
    # Set hightlight region
    def hightlight_area( self, area):
        self.current_area = area
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

    def map_to_screen( self, x,y,w,h):
        px = int((float(x) + 180.0) / 360.0 * self.backbuf.get_width())
        py = int((90-float(y)) / 180.0 * self.backbuf.get_height())
        pw = int(float(w) / 360.0 * self.backbuf.get_width())
        ph = int(float(h) / 180.0 * self.backbuf.get_height())
        
        return (px,py,pw,ph)

# Zoomable map image
class ZoomMap( gtk.DrawingArea):
    def __init__(self, map_pixbuf, place_marker_pixbuf,
                 hightlight_marker_pixbuf):
        gtk.DrawingArea.__init__(self)
        self.map_pixbuf = map_pixbuf
        self.place_marker_pixbuf = place_marker_pixbuf
        self.hightlight_marker_pixbuf = hightlight_marker_pixbuf
        self.connect("expose-event", self.expose_cb)
        self.connect("size-allocate", self.size_allocate_cb)
        self.gc = None
        self.old_size = (-1,-1)
        self.zoom_pos = (0,0)
        self.current_area = (0,0,0,0)
        self.magnifer = 0.5
        self.guide = None
        self.textlayout = self.create_pango_layout("")
    
    # Set the guide map that should follow the zoom area
    def set_guide( self, guide):
        self.guide = guide

    def set_location_model( self, model, idx_name, idx_long, idx_lat):
        self.location_model = model
        self.idx_name = idx_name
        self.idx_long = idx_long
        self.idx_lat = idx_lat
        
    # Redraw the image
    def expose_cb(self,widget,event):
        if not self.gc:
            self.gc = self.window.new_gc()
            self.gc.set_foreground( self.get_colormap().alloc_color("red"))
            self.gc.set_background( self.get_colormap().alloc_color("blue"))
        if not self.backbuf:
            self.size_allocate_cb( self,self.get_allocation())
        if self.backbuf and self.gc:
            self.window.draw_pixbuf( self.gc, self.backbuf, 0,0, 0,0, -1,-1)
            
            # draw all available locations
            if self.location_model:
                iter = self.location_model.get_iter_first()
                while iter:
                    (n,x,y) = self.location_model.get( iter, self.idx_name, self.idx_long, self.idx_lat)
                    (px,py) = self.map_to_screen( x, y)
                    if px > 0 and py > 0 and px < self.backbuf.get_width() and py < self.backbuf.get_height():
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

    def map_to_screen( self, long, lat):
        px = int(self.backbuf.get_width() / self.current_map_area[2] *
                    (float(long) - self.current_map_area[0]))
        py = int(self.backbuf.get_height() / self.current_map_area[3] *
                    (-float(lat) + self.current_map_area[1]))
        return( px, py)
        
    # Scale backbuffer
    def size_allocate_cb(self,widget,allocation):
        # only create new backbuffer if size is different
        new_size = (allocation.width,allocation.height)
        if new_size is not self.old_size or not self.backbuf:
            self.old_size = new_size
            
            # Desired midpoint in map
            pw = int(self.old_size[0]*self.magnifer)
            ph = int(self.old_size[1]*self.magnifer)
            
            px = int((float(self.zoom_pos[0]) + 180.0) / 360.0
                     * self.map_pixbuf.get_width())
            py = int((90-float(self.zoom_pos[1])) / 180.0
                     * self.map_pixbuf.get_height())

            px = max( pw/2, px)
            py = max( ph/2, py)
            
            px = min( px, self.map_pixbuf.get_width()-1-pw/2)
            py = min( py, self.map_pixbuf.get_height()-1-ph/2)
            
            try:
                zoomebuf = self.map_pixbuf.subpixbuf( max(0,int(px-pw/2)),max(0,int(py-ph/2)),
                                                        min(self.map_pixbuf.get_width(),pw),
                                                        min(self.map_pixbuf.get_height(),ph))
                self.backbuf = zoomebuf.scale_simple(self.old_size[0],
                                                 self.old_size[1],
                                                 gtk.gdk.INTERP_BILINEAR)
                gc.collect()
                mx = 360.0 / self.map_pixbuf.get_width() * (px-pw/2.0) - 180.0
                my = 90.0 - 180.0 / self.map_pixbuf.get_height() * (py-ph/2.0)
                mw = 360.0 / self.map_pixbuf.get_width() * pw
                mh = 180.0 / self.map_pixbuf.get_height() * ph
                self.current_area = (px-pw/2, py-ph/2, pw,ph)
                self.current_map_area = (mx, my, mw, mh)
                if self.guide:
                    self.guide.hightlight_area( (mx,my,mw,mh))
            except:
                pass

    # Scroll to requested position
    def scroll_to( self, long, lat):
        self.zoom_pos = ( min(180,(max(-180,long))), min(90,(max(-90,lat))))
        self.backbuf = None
        self.queue_draw()

    def zoom_out(self):
        self.magnifer = min( 10, self.magnifer * 1.5)
        self.backbuf = None
        self.queue_draw()
    
    def zoom_in(self):
        self.magnifer = max( 0.1, self.magnifer * 0.75)
        self.backbuf = None
        self.queue_draw()
    
    def zoom_normal(self):
        self.magnifer = 1
        self.backbuf = None
        self.queue_draw()

    def zoom_fit(self):
        self.magnifer = 2
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
        PageView.PageView.__init__(self,'Map View',dbstate,uistate)
        dbstate.connect('database-changed',self.change_db)
        self.current_marker = None

    def navigation_type(self):
        return PageView.NAVIGATION_NONE

    def define_actions(self):
        self.add_action('ZoomIn',gtk.STOCK_ZOOM_IN,
                        "Zoom _In",callback=self.zoom_in_cb)
        self.add_action('ZoomOut',gtk.STOCK_ZOOM_OUT,
                        "Zoom _Out",callback=self.zoom_out_cb)
        self.add_action('ZoomNormal',gtk.STOCK_ZOOM_100,
                        "_Normal Size", callback=self.zoom_100_cb)
        self.add_action('ZoomFit',gtk.STOCK_ZOOM_FIT,
                        "Best _Fit",callback=self.zoom_fit_cb)

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
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"land_shallow_topo_2048.jpg")),
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"bad.png")),
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"good.png")))
        self.zoom_map.set_size_request(300,300)
        hbox.pack_start( self.zoom_map, True, True, 0)
        
        # On the right side
        vbox = gtk.VBox( False, 4)
        hbox.pack_start( vbox, False, False, 0)
        
        # The small guide map
        self.guide_map = GuideMap(
            gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"land_shallow_topo_350.jpg")))
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
