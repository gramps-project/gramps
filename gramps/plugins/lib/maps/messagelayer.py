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

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.messagelayer")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Pango, PangoCairo

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.constfunc import is_quartz

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

# pylint: disable=unused-variable
# pylint: disable=unused-argument
# pylint: disable=no-member

class MessageLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display messages over the map
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.message = ""
        self.color = "black"
        self.font = "Sans"
        self.size = 13

    def clear_messages(self):
        """
        reset the layer attributes.
        """
        self.message = ""

    def clear_font_attributes(self):
        """
        reset the font attributes.
        """
        self.color = "black"
        self.font = "Sans"
        self.size = 13

    def set_font_attributes(self, font, size, color):
        """
        Set the font color, size and name
        """
        if color is not None:
            self.color = color
        if font is not None:
            self.font = font
        if size is not None:
            self.size = size

    def add_message(self, message):
        """
        Add a message
        """
        self.message += "\n%s" % message if self.message is not "" else message

    def do_draw(self, gpsmap, ctx):
        """
        Draw all the messages
        """
        ctx.save()
        font_size = "%s %d" % (self.font, self.size)
        font = Pango.FontDescription(font_size)
        descr = Pango.font_description_from_string(self.font)
        descr.set_size(self.size * Pango.SCALE)
        color = Gdk.color_parse(self.color)
        ctx.set_source_rgba(float(color.red / 65535.0),
                            float(color.green / 65535.0),
                            float(color.blue / 65535.0),
                            0.9) # transparency
        d_width = gpsmap.get_allocation().width
        d_width -= 100
        ctx.restore()
        ctx.save()
        ctx.move_to(100, 5)
        layout = PangoCairo.create_layout(ctx)
        if is_quartz():
            PangoCairo.context_set_resolution(layout.get_context(), 72)
        layout.set_font_description(descr)
        layout.set_indent(Pango.SCALE * 0)
        layout.set_alignment(Pango.Alignment.LEFT)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_spacing(Pango.SCALE * 3)
        layout.set_width(d_width * Pango.SCALE)
        layout.set_text(self.message, -1)
        PangoCairo.show_layout(ctx, layout)
        ctx.restore()
        ctx.stroke()

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

GObject.type_register(MessageLayer)

