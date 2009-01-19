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
    GENCOLOR = ((229,191,252),
                (191,191,252),
                (191,222,252),
                (183,219,197),
                (206,246,209))

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
        self.rotate_value = 90
        self.set_generations(self.generations)
        self.center = 50
        self.layout = self.create_pango_layout('cairo')
        self.layout.set_font_description(pango.FontDescription("sans serif 8"))

    def reset_generations(self):
        self.set_generations(self.generations)

    def set_generations(self, generations):
        self.generations = generations
        self.angle = {}
        self.data = {}
        for i in range(self.generations):
            self.data[i] = [None for j in range(2 ** i)]
            self.angle[i] = []
            angle = 0
            slice = 360.0 / (2 ** i)
            gender = True
            for a in range(len(self.data[i])):
                # start, stop, male, state
                self.angle[i].append([angle, angle + slice, gender, 1])
                angle += slice
                gender = not gender
                                           
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
        cr.save()
        cr.rotate(self.rotate_value * math.pi/180)
        for generation in range(self.generations - 1, 0, -1):
            for p in range(len(self.data[generation])):
                person = self.data[generation][p]
                if person:
                    start, stop, male, state = self.angle[generation][p]
                    name = name_displayer.display(person)
                    gender = person.get_gender()
                    if state > 0:
                        self.draw_person(cr, gender, name, start, stop, generation, state)
        cr.set_source_rgb(1, 1, 1) # white
        cr.move_to(0,0)
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.move_to(0,0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.stroke()
        person = self.data[0][0]
        # Draw center person:
        cr.restore()
        if person:
            cr.save()
            name = name_displayer.display(person)
            self.draw_text(cr, name, self.center - 10, 95, 455)
            #layout = self.create_pango_layout(name)
            #layout.set_font_description(pango.FontDescription("sans serif 8"))
            #cr.move_to(-self.center + 10, -4) # start place for center text
            #cr.show_layout(layout)
            cr.restore()
        fontw, fonth = self.layout.get_pixel_size()
        cr.move_to((w - fontw - 4), (h - fonth ))
        cr.update_layout(self.layout)
        cr.show_layout(self.layout)

    def draw_person(self, cr, gender, name, start, stop, generation, state):
        """
        Display the piece of pie for a given person. start and stop
        are in degrees.
        """
        x, y, w, h = self.allocation
        start_rad = start * math.pi/180
        stop_rad = stop * math.pi/180
        r,g,b = self.GENCOLOR[generation % len(self.GENCOLOR)]
        if gender == 1:
            r -= r * .10
            g -= g * .10
            b -= b * .10
        cr.set_source_rgb(r/255., g/255., b/255.) 
        radius = generation * self.pixels_per_generation + self.center
        cr.move_to(0, 0)
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.move_to(0, 0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.line_to(0, 0)
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.line_to(0, 0)
        cr.set_line_width(state)
        cr.stroke()
        self.draw_text(cr, name, radius - self.pixels_per_generation/2, 
                       start, stop)

    def text_degrees(self, text, radius):
        """
        Returns the number of degrees of text at a given radius.
        """
        return 360.0 * len(text)/(radius * self.degrees_per_radius)

    def text_limit(self, text, degrees, radius):
        while self.text_degrees(text, radius) > degrees:
            text = text[:-1]
        return text

    def draw_text(self, cr, text, radius, start, stop):
        """
        Display text at a particular radius, between start and stop
        degrees.
        """
        # trim to fit:
        text = self.text_limit(text, stop - start, radius - 15)
        # center text:
        pos = start + ((stop - start) - self.text_degrees(text, radius))/2.0 + 90
        # offset for cairo-font system is 90
        x, y, w, h = self.allocation
        cr.save()
        # Create a PangoLayout, set the font and text 
        # Draw the layout N_WORDS times in a circle 
        for i in range(len(text)):
            cr.save()
            layout = self.create_pango_layout(text[i])
            layout.set_font_description(pango.FontDescription("sans serif 8"))
            angle = 360.0 * i / (radius * self.degrees_per_radius) + pos
            cr.set_source_rgb(0, 0, 0) # black 
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
        self.generations = 6
        self.gui.fan = FanChartWidget(self.generations)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.fan)
        #container is a gtk.ScrolledWindow
        container = self.gui.get_container_widget()
        container.connect("button-press-event", self.on_mouse_down)
        self.gui.fan.show()

    def expand_parents(self, generation, selected, to_right):
        print "expanding", generation, selected
        if generation >= self.generations: return
        selected = 2 * selected
        start,stop,male,state = self.gui.fan.angle[generation][selected]
        slice = (stop - start) * 2.0
        current = start
        if state > 0:
            if to_right:
                current = start+slice
                self.gui.fan.angle[generation][selected] = start,current,male,state
            else:
                current = stop - slice
                self.gui.fan.angle[generation][selected] = current,stop,male,state
            self.expand_parents(generation + 1, selected, to_right)
        start,stop,male,state = self.gui.fan.angle[generation][selected+1]
        if state > 0:
            self.gui.fan.angle[generation][selected+1] = current,current+slice,male,state
            self.expand_parents(generation + 1, selected+1, to_right)

    def shrink_parents(self, generation, selected, from_right):
        pass

    def change_slice(self, generation, selected):
        gstart, gstop, gmale, gstate = self.gui.fan.angle[generation][selected]
        if gstate == 1: # normal, let's expand
            if gmale:
                # go to right
                stop = gstop + (gstop - gstart)
                self.gui.fan.angle[generation][selected] = [gstart,stop,gmale,2]
                start,stop,male,state = self.gui.fan.angle[generation][selected+1]
                self.gui.fan.angle[generation][selected+1] = [stop,stop,male,0]
            else:
                # go to left
                start = gstart - (gstop - gstart)
                self.gui.fan.angle[generation][selected] = [start,gstop,gmale,2]
                start,stop,male,state = self.gui.fan.angle[generation][selected-1]
                self.gui.fan.angle[generation][selected-1] = [start,start,male,0]
            # now we need to expand each of the slices outward:
            #self.expand_parents(generation + 1, selected, gmale)
        elif gstate == 2: # expanded, let's shrink
            if gmale:
                # shrink from right
                slice = (gstop - gstart)/2.0
                stop = gstop - slice
                self.gui.fan.angle[generation][selected] = [gstart,stop,gmale,1]
                start,stop,male,state = self.gui.fan.angle[generation][selected+1]
                self.gui.fan.angle[generation][selected+1] = [stop-slice,stop,male,1]
            else:
                # shrink from left
                slice = (gstop - gstart)/2.0
                start = gstop - slice
                self.gui.fan.angle[generation][selected] = [start,gstop,gmale,1]
                start,stop,male,state = self.gui.fan.angle[generation][selected-1]
                self.gui.fan.angle[generation][selected-1] = [start,start+slice,male,1]
            # now we need to shrink each of the slices outward:
            #self.shrink_parents(self, generation + 1, selected, gmale)

    def on_mouse_down(self, widget, e):
        # compute angle, radius, find out who would be there (rotated)
        x, y, w, h = self.gui.fan.allocation
        cx = w/2
        cy = h/2
        radius = math.sqrt((e.x - cx) ** 2 + (e.y - cy) ** 2)
        if radius < self.gui.fan.center:
            generation = 0
        else:
            generation = int((radius - self.gui.fan.center) / 
                             self.gui.fan.pixels_per_generation) + 1
        rads = math.atan2( (e.y - cy), (e.x - cx) )
        if rads < 0:
            rads = math.pi + (math.pi + rads)
        pos = ((rads/(math.pi * 2) - self.gui.fan.rotate_value/360.) * 360.0) % 360
        # find what person is in this position:
        selected = None
        if (0 < generation < self.generations):
            for p in range(len(self.gui.fan.angle[generation])):
                start, stop, male, state = self.gui.fan.angle[generation][p]
                if state == 0: continue
                if start <= pos <= stop:
                    selected = p
                    break
        print "---------------"
        print "   angle:", pos
        print "   generation:", generation
        print "   selected:", selected
        if selected == None: 
            if radius < self.gui.fan.center:
                pass # TODO: select children
            elif e.x > cx: # on right, rotate clockwise
                self.gui.fan.rotate_value += 90.0
            else: # on left, rotate counterclockwise
                self.gui.fan.rotate_value -= 90.0
            self.gui.fan.rotate_value %= 360
            self.gui.fan.queue_draw()
            return True
        self.change_slice(generation, selected)
        person = self.gui.fan.data[generation][selected]
        if person:
            name = name_displayer.display(person)
            print name, start, stop
                #self.dbstate.change_active_person(person)
        self.gui.fan.queue_draw()
        return True

    def db_changed(self):
        self.sa = SimpleAccess(self.dbstate.db)

    def active_changed(self, handle):
        # Reset everything
        self.gui.fan.rotate_value = 90
        self.gui.fan.reset_generations()
        self.update()

    def main(self):
        self.gui.fan.data[0][0] = self.dbstate.get_active_person()
        for current in range(1, self.generations):
            parent = 0
            for p in self.gui.fan.data[current - 1]:
                self.gui.fan.data[current][parent] = self.sa.father(p)
                if self.gui.fan.data[current][parent] is None:
                    self.gui.fan.angle[current][parent][3] = 0 # start,stop,g,state
                parent += 1
                self.gui.fan.data[current][parent] = self.sa.mother(p)
                if self.gui.fan.data[current][parent] is None:
                    self.gui.fan.angle[current][parent][3] = 0 # start,stop,g,state
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
