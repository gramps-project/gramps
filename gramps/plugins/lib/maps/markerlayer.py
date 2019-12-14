# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011-2016       Serge Noiraud
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
import time
from math import pi as PI


#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.markerlayer")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    import gi
    gi.require_version('OsmGpsMap', '1.0')
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise

# pylint: disable=unused-argument

class MarkerLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display the markers.
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.markers = []
        self.max_references = 0
        self.max_places = 0
        self.nb_ref_by_places = 0
        self.max_value = 0
        self.min_value = 9999

    def clear_markers(self):
        """
        reset the layer attributes.
        """
        self.markers = []
        self.max_references = 0
        self.max_places = 0
        self.nb_ref_by_places = 0
        self.max_value = 0
        self.min_value = 9999

    def add_marker(self, points, image, count, color=None):
        """
        Add a marker.
        Set minimum value, maximum value for the markers
        Set the average value too.
        We calculate that here, to minimize the overhead at markers drawing
        """
        self.markers.append((points, image, count, color))
        self.max_references += count
        self.max_places += 1
        if count > self.max_value:
            self.max_value = count
        if count < self.min_value:
            self.min_value = count
        self.nb_ref_by_places = self.max_references / self.max_places

    def do_draw(self, gpsmap, ctx):
        """
        Draw all markers here. Calculate where to draw the marker.
        Depending of the average, minimum and maximum value, resize the marker.
        We use cairo to resize the marker.
        """
        max_interval = self.max_value - self.nb_ref_by_places
        min_interval = self.nb_ref_by_places - self.min_value
        if max_interval <= 0: # This to avoid divide by zero
            max_interval = 0.01
        if min_interval <= 0: # This to avoid divide by zero
            min_interval = 0.01
        _LOG.debug("%s", time.strftime("start drawing   : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        for marker in self.markers:
            # the icon size in 48, so the standard icon size is 0.6 * 48 = 28.8
            size = 0.6
            mark = float(marker[2])
            if mark > self.nb_ref_by_places or max_interval > 3:
                # at maximum, we'll have an icon size = (0.6 + 0.2) * 48 = 38.4
                size += (0.2 * ((mark - self.nb_ref_by_places)
                                 / max_interval))
            else:
                # at minimum, we'll have an icon size = (0.6 - 0.2) * 48 = 19.2
                size -= (0.2 * ((self.nb_ref_by_places - mark)
                                 / min_interval))

            conv_pt = osmgpsmap.MapPoint.new_degrees(float(marker[0][0]),
                                                     float(marker[0][1]))
            coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
            if marker[3] == None:
                # We use the standard icons.
                ctx.save()
                ctx.translate(coord_x, coord_y)
                ctx.scale(size, size)
                # below, we try to place exactly the marker depending on its
                # size. The left top corner of the image is set to the
                # coordinates. The tip of the pin which should be at the marker
                # position is at 3/18 of the width and to the height of the
                # image. So we shift the image position.
                pos_y = - int(48 * size + 0.5) - 10
                pos_x = - int((48 * size) / 6 + 0.5) - 10
                ctx.set_source_surface(marker[1], pos_x, pos_y)
                ctx.paint()
                ctx.restore()
            else:
                # We use colored icons.
                draw_marker(ctx, float(coord_x), float(coord_y),
                            size, marker[3][1])
        _LOG.debug("%s", time.strftime("end drawing     : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))

    def do_render(self, gpsmap):
        """
        render the layer
        """
        pass

    def do_busy(self):
        """
        set the layer busy
        """
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        """
        When we press a button.
        """
        return False

GObject.type_register(MarkerLayer)

def draw_marker(ctx, x1, y1, size, color):
    width = 48.0 * size
    height = width / 2
    color = Gdk.color_parse(color)
    ctx.set_source_rgba(float(color.red / 65535.0),
                        float(color.green / 65535.0),
                        float(color.blue / 65535.0),
                        1.0) # transparency
    ctx.set_line_width (2.0);
    ctx.move_to(x1, y1)
    ctx.line_to((x1 + (height/3)), (y1 - height*2))
    ctx.line_to((x1 - (height/3)), (y1 - height*2))
    ctx.fill()
    ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5)
    ctx.move_to(x1, y1)
    ctx.line_to((x1 + (height/3)), (y1 - height*2))
    ctx.line_to((x1 - (height/3)), (y1 - height*2))
    ctx.line_to(x1, y1)
    ctx.stroke()
    ctx.save()
    ctx.translate(x1 + width/4 - (width/4) , y1 - height*2 - (width/4))
    ctx.scale(width / 2., height / 2.)
    ctx.arc(0., 0., 1., 0., 2 * PI)
    ctx.fill_preserve()
    ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5)
    ctx.set_line_width (2.0);
    ctx.arc(0., 0., 1., 0., 2 * PI)
    ctx.restore()
    ctx.stroke();
    ctx.save()
    ctx.set_source_rgba(float(color.red / 65535.0),
                        float(color.green / 65535.0),
                        float(color.blue / 65535.0),
                        1.0) # transparency
    #ctx.translate(x1 + width/4 - 12.0 , y1 - height*2 - 12.0)
    ctx.translate(x1 + width/4 - (width/4) , y1 - height*2 - (width/4))
    ctx.scale(width / 2., height / 2.)
    ctx.arc(0., 0., 1., 0., 2 * PI)
    ctx.fill_preserve()
    ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5)
    ctx.set_line_width (2.0);
    ctx.arc(0., 0., 1., 0., 2 * PI)
    ctx.restore()
    ctx.stroke();
