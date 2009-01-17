# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Douglas S. Blank
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import pango
import gtk
import math
from gtk import gdk
try:
    import cairo
except ImportError:
    pass

if gtk.pygtk_version < (2,3,93):
    raise Exception("PyGtk 2.3.93 or later required")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from BasicUtils import name_displayer
from Simple import SimpleAccess
from gettext import gettext as _
from DataViews import Gramplet, register

#-------------------------------------------------------------------------
#
# FanChartWidget
#
#-------------------------------------------------------------------------
class FanChartWidget(gtk.Widget):
    BORDER_WIDTH = 10
    __gsignals__ = { 'realize':          'override',
                     'expose-event' :    'override',
                     'size-allocate':    'override',
                     'size-request':     'override',
                     }

    def __init__(self, generations):
        """
        Highly experimental... documents forthcoming...
        """
        gtk.Widget.__init__(self)
        self.draw_gc = None
        self.pixels_per_generation = 50
        ## gotten from experiments with "sans serif 8":
        self.degrees_per_radius = .80
        self.generations = generations
        self.rotate_value = 0
        self.data = {}
        for i in range(self.generations):
            self.data[i] = [None for j in range(2 ** i)]
        self.center = 50
        self.layout = self.create_pango_layout('cairo')
        self.layout.set_font_description(pango.FontDescription("sans serif 8"))

    def set_generations(self, generations):
        self.generations = generations
        self.data = {}
        for i in range(self.generations):
            self.data[i] = [None for j in range(2 ** i)]
                                           
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK)
        if not hasattr(self.window, "cairo_create"):
            self.draw_gc = gdk.GC(self.window,
                                  line_width=5,
                                  line_style=gdk.SOLID,
                                  join_style=gdk.JOIN_ROUND)

	self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)

    def do_size_request(self, requisition):
	width, height = self.layout.get_size()
	requisition.width = (width // pango.SCALE + self.BORDER_WIDTH*4)* 1.45
	requisition.height = (3 * height // pango.SCALE + self.BORDER_WIDTH*4) * 1.2

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def _expose_gdk(self, event):
        x, y, w, h = self.allocation
        self.layout = self.create_pango_layout('no cairo')
        fontw, fonth = self.layout.get_pixel_size()
        self.style.paint_layout(self.window, self.state, False,
                                event.area, self, "label",
                                (w - fontw) / 2, (h - fonth) / 2,
                                self.layout)

    def do_expose_event(self, event):
        try:
            cr = self.window.cairo_create()
        except AttributeError:
            return self._expose_gdk(event)
        return self._expose_cairo(event, cr)

    def _expose_cairo(self, event, cr):
        x, y, w, h = self.allocation
        cr.translate(w/2., h/2.)
        cr.rotate(self.rotate_value * math.pi/180)
        for generation in range(self.generations - 1, 0, -1):
            slice = 360 / len(self.data[generation])
            current = 0
            for person in self.data[generation]:
                if person:
                    name = name_displayer.display(person)
                    gender = person.get_gender()
                    self.draw_person(cr, gender, name, current, generation)
                current += slice
        cr.set_source_rgb(1, 1, 1) # white
        cr.move_to(0,0)
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.move_to(0,0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.stroke()
        person = self.data[0][0]
        if person:
            cr.save()
            name = name_displayer.display(person)
            layout = self.create_pango_layout(name)
            layout.set_font_description(pango.FontDescription("sans serif 8"))
            cr.move_to(-self.center + 10, -4)
            cr.show_layout(layout)
            cr.restore()
        fontw, fonth = self.layout.get_pixel_size()
        cr.move_to((w - fontw - 4), (h - fonth ))
        cr.update_layout(self.layout)
        cr.show_layout(self.layout)

    def draw_person(self, cr, gender, name, start, generation):
        x, y, w, h = self.allocation
        start_rad = start * math.pi/180
        if gender == 0:
            cr.set_source_rgb(1, 0.69, 0.69) # pink
        elif gender == 1:
            cr.set_source_rgb(0, 1, 1) # cyan
        radius = generation * self.pixels_per_generation + self.center
        cr.move_to(0, 0)
        cr.arc(0, 0, radius, start_rad, start_rad + (2 * math.pi) / 2 ** generation) 
        cr.move_to(0, 0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, radius, start_rad, start_rad) 
        cr.line_to(0, 0)
        cr.arc(0, 0, radius, start_rad, start_rad + (2 * math.pi) / 2 ** generation) 
        cr.line_to(0, 0)
        cr.set_line_width(1)
        cr.stroke()
        degrees = 6 # self.text_degrees(name, radius)/2
        #FIXME: if degrees bigger than arc available, trim or wrap?
        self.draw_text(cr, name, 
                       radius - self.pixels_per_generation/2, 
                       start + 90 + degrees)

    def text_degrees(self, text, radius):
        return 360.0 * len(text)/(radius * self.degrees_per_radius)

    def draw_text(self, cr, text, radius, pos):
        x, y, w, h = self.allocation
        cr.save()
        # Create a PangoLayout, set the font and text 
        # Draw the layout N_WORDS times in a circle 
        for i in range(len(text)):
            cr.save()
            layout = self.create_pango_layout(text[i])
            layout.set_font_description(pango.FontDescription("sans serif 8"))
            angle = 360.0 * i / (radius * self.degrees_per_radius) + pos
            cr.set_source_rgb(0, 0, 1) # blue clickable
            cr.rotate(angle * (math.pi / 180));
            # Inform Pango to re-layout the text with the new transformation
            cr.update_layout(layout)
            width, height = layout.get_size()
            cr.move_to(- (width / pango.SCALE) / 2.0, - radius)
            cr.show_layout(layout)
            cr.restore()
        cr.restore()

class FanChartGramplet(Gramplet):
    def init(self):
        self.gui.fan = FanChartWidget(4)
        self.gui.get_container_widget().remove(self.gui.textview)
        vbox = gtk.VBox()
        self.scale = gtk.HScale()
        self.scale.set_draw_value(0)
        self.scale.set_value_pos(gtk.POS_LEFT)
        self.scale.set_range(0, 360)
        self.scale.connect("value-changed", self.scale_changed)
        vbox.pack_start(self.scale, False, False)
        vbox.pack_start(self.gui.fan)
        self.gui.get_container_widget().add_with_viewport(vbox)
        #container is a gtk.ScrolledWindow
        container = self.gui.get_container_widget()
        container.connect("button-press-event", self.on_mouse_down)
        vbox.show()
        self.gui.fan.show()
        self.scale.show()

    def scale_changed(self, widget):
        self.gui.fan.rotate_value = widget.get_value()
        self.gui.fan.queue_draw()

    def on_mouse_down(self, widget, e):
        # compute angle, radius, find out who would be there (rotated)
        x, y, w, h = self.gui.fan.allocation
        cx = w/2
        cy = h/2
        radius = math.sqrt((e.x - cx) ** 2 + (e.y - cy - 20) ** 2)
        if radius < self.gui.fan.center:
            generation = 0
        else:
            generation = int((radius - self.gui.fan.center) / 
                             self.gui.fan.pixels_per_generation) + 1
        rads = math.atan2( (e.y - cy), (e.x - cx - 20) )
        if rads < 0:
            rads = math.pi + (math.pi + rads)
        pos = (rads/(math.pi * 2) - self.gui.fan.rotate_value/360.)
        pos = int(math.floor(pos * 2 ** generation))
        pos = pos % (2 ** generation)
        if 0 < generation < 4 and 0 <= pos < len(self.gui.fan.data[generation]):
            person = self.gui.fan.data[generation][pos]
            if person:
                #name = name_displayer.display(person)
                self.dbstate.change_active_person(person)
        return True

    def db_changed(self):
        self.sa = SimpleAccess(self.dbstate.db)

    def active_changed(self, handle):
        self.gui.fan.rotate_value = 0
        self.scale.set_value(0)
        self.scale.set_value_pos(gtk.POS_LEFT)
        self.update()

    def main(self):
        self.gui.fan.data[0][0] = self.dbstate.get_active_person()
        for current in range(1, 4):
            parent = 0
            for p in self.gui.fan.data[current - 1]:
                self.gui.fan.data[current][parent] = self.sa.father(p)
                parent += 1
                self.gui.fan.data[current][parent] = self.sa.mother(p)
                parent += 1
        self.gui.fan.queue_draw()

register(type="gramplet", 
         name= "Fan Chart Gramplet", 
         tname=_("Fan Chart Gramplet"), 
         height=430,
         expand=False,
         content = FanChartGramplet,
         detached_height = 550,
         detached_width = 475,
         title=_("Fan Chart"),
         )
