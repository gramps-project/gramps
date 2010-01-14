# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
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

## Based on the paper:
##   http://www.cs.utah.edu/~draperg/research/fanchart/draperg_FHT08.pdf
## and the applet:
##   http://www.cs.utah.edu/~draperg/research/fanchart/demo/

## Found by redwood:
## http://www.gramps-project.org/bugs/view.php?id=2611

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
from cgi import escape
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
from gen.display.name import displayer as name_displayer
from gettext import gettext as _
from gen.plug import Gramplet
from Utils import (find_children, find_parents, find_witnessed_people)
from libformatting import FormattingHelper
import gen.lib
import Errors
from gui.editors import EditPerson

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------
def gender_code(is_male):
    """
    Given boolean is_male (means position in FanChart) return code.
    """
    if is_male: 
        return gen.lib.Person.MALE
    else:
        return gen.lib.Person.FEMALE

#-------------------------------------------------------------------------
#
# FanChartWidget
#
#-------------------------------------------------------------------------
class FanChartWidget(gtk.Widget):
    """
    Interactive Fan Chart Widget. 
    """
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

    COLLAPSED = 0
    NORMAL = 1
    EXPANDED = 2

    def __init__(self, generations, context_popup_callback=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        gtk.Widget.__init__(self)
        self.translating = False
        self.last_x, self.last_y = None, None
        self.connect("button_release_event", self.on_mouse_up)
        self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button-press-event", self.on_mouse_down)
        self.context_popup_callback = context_popup_callback
        self.add_events(gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.POINTER_MOTION_MASK)
        self.pixels_per_generation = 50 # size of radius for generation
        ## gotten from experiments with "sans serif 8":
        self.degrees_per_radius = .80
        ## Other fonts will have different settings. Can you compute that
        ## from the font size? I have no idea.
        self.generations = generations
        self.rotate_value = 90 # degrees, initially, 1st gen male on right half
        self.center_xy = [0, 0] # distance from center (x, y)
        self.set_generations(self.generations)
        self.center = 50 # pixel radius of center
        self.layout = self.create_pango_layout('cairo')
        self.layout.set_font_description(pango.FontDescription("sans 8"))

    def reset_generations(self):
        """
        Reset all of the data on where slices appear, and if they are expanded.
        """
        self.set_generations(self.generations)

    def set_generations(self, generations):
        """
        Set the generations to max, and fill data structures with initial data.
        """
        self.generations = generations
        self.angle = {}
        self.data = {}
        for i in range(self.generations):
            # name, person, parents?, children?
            self.data[i] = [(None, None, None, None) for j in range(2 ** i)]
            self.angle[i] = []
            angle = 0
            slice = 360.0 / (2 ** i)
            gender = True
            for count in range(len(self.data[i])):
                # start, stop, male, state
                self.angle[i].append([angle, angle + slice,gender,self.NORMAL])
                angle += slice
                gender = not gender
                                           
    def do_realize(self):
        """
        Overriden method to handle the realize event.
        """
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
        """
        Overridden method to handle size request events.
        """
        width, height = self.layout.get_size()
        requisition.width = (width // pango.SCALE + self.BORDER_WIDTH*4)* 1.45
        requisition.height = (3 * height // pango.SCALE + self.BORDER_WIDTH*4) * 1.2

    def do_size_allocate(self, allocation):
        """
        Overridden method to handle size allocation events.
        """
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
        """
        Overridden method to handle expose events.
        """
        try:
            cr = self.window.cairo_create()
        except AttributeError:
            return self._expose_gdk(event)
        return self._expose_cairo(event, cr)

    def _expose_cairo(self, event, cr):
        """
        The main method to do the drawing.
        """
        x, y, w, h = self.allocation
        cr.translate(w/2. - self.center_xy[0], h/2. - self.center_xy[1])
        cr.save()
        cr.rotate(self.rotate_value * math.pi/180)
        for generation in range(self.generations - 1, 0, -1):
            for p in range(len(self.data[generation])):
                (text, person, parents, child) = self.data[generation][p]
                if person:
                    start, stop, male, state = self.angle[generation][p]
                    if state in [self.NORMAL, self.EXPANDED]:
                        self.draw_person(cr, gender_code(male), 
                                         text, start, stop, 
                                         generation, state, parents, child)
        cr.set_source_rgb(1, 1, 1) # white
        cr.move_to(0,0)
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.move_to(0,0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.stroke()
        # Draw center person:
        (text, person, parents, child) = self.data[0][0]
        cr.restore()
        if person:
            cr.save()
            name = name_displayer.display(person)
            self.draw_text(cr, name, self.center - 10, 95, 455)
            cr.restore()
            if child: # has at least one child
                cr.set_source_rgb(0, 0, 0) # black
                cr.move_to(0,0)
                cr.arc(0, 0, 10, 0, 2 * math.pi)
                cr.move_to(0,0)
                cr.fill()
        fontw, fonth = self.layout.get_pixel_size()
        cr.move_to((w - fontw - 4), (h - fonth ))
        cr.update_layout(self.layout)
        cr.show_layout(self.layout)

    def draw_person(self, cr, gender, name, start, stop, generation, 
                    state, parents, child):
        """
        Display the piece of pie for a given person. start and stop
        are in degrees.
        """
        x, y, w, h = self.allocation
        start_rad = start * math.pi/180
        stop_rad = stop * math.pi/180
        r,g,b = self.GENCOLOR[generation % len(self.GENCOLOR)]
        if gender == gen.lib.Person.MALE:
            r *= .9
            g *= .9
            b *= .9
        radius = generation * self.pixels_per_generation + self.center
        # If max generation, and they have parents:
        if generation == self.generations - 1 and parents:
            # draw an indicator
            cr.move_to(0, 0)
            #cr.set_source_rgba(1, 0.2, 0.2, 0.6) # pink
            cr.set_source_rgb(255, 255, 255) # white
            cr.arc(0, 0, radius + 5, start_rad, stop_rad) 
            cr.fill()
            cr.move_to(0, 0)
            cr.set_source_rgb(0, 0, 0) # black
            cr.arc(0, 0, radius + 5, start_rad, stop_rad) 
            cr.line_to(0, 0)
            cr.stroke()
        cr.set_source_rgb(r/255., g/255., b/255.) 
        cr.move_to(0, 0)
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.move_to(0, 0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.line_to(0, 0)
        cr.arc(0, 0, radius, start_rad, stop_rad) 
        cr.line_to(0, 0)
        if state == self.NORMAL: # normal
            cr.set_line_width(1)
        else: # EXPANDED
            cr.set_line_width(3)
        cr.stroke()
        cr.set_line_width(1)
        if self.last_x is None or self.last_y is None: 
            self.draw_text(cr, name, radius - self.pixels_per_generation/2, 
                           start, stop)

    def text_degrees(self, text, radius):
        """
        Returns the number of degrees of text at a given radius.
        """
        return 360.0 * len(text)/(radius * self.degrees_per_radius)

    def text_limit(self, text, degrees, radius):
        """
        Trims the text to fit a given angle at a given radius. Probably 
        a better way to do this.
        """
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
        # offset for cairo-font system is 90:
        pos = start + ((stop - start) - self.text_degrees(text,radius))/2.0 + 90
        x, y, w, h = self.allocation
        cr.save()
        # Create a PangoLayout, set the font and text 
        # Draw the layout N_WORDS times in a circle 
        for i in range(len(text)):
            cr.save()
            layout = self.create_pango_layout(text[i])
            layout.set_font_description(pango.FontDescription("sans 8"))
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

    def expand_parents(self, generation, selected, current):
        if generation >= self.generations: return
        selected = 2 * selected
        start,stop,male,state = self.angle[generation][selected]
        if state in [self.NORMAL, self.EXPANDED]:
            slice = (stop - start) * 2.0
            self.angle[generation][selected] = [current,current+slice,
                                                male,state]
            self.expand_parents(generation + 1, selected, current)
            current += slice
        start,stop,male,state = self.angle[generation][selected+1]
        if state in [self.NORMAL, self.EXPANDED]:
            slice = (stop - start) * 2.0
            self.angle[generation][selected+1] = [current,current+slice,
                                                  male,state]
            self.expand_parents(generation + 1, selected+1, current)

    def show_parents(self, generation, selected, angle, slice):
        if generation >= self.generations: return
        selected *= 2
        self.angle[generation][selected][0] = angle
        self.angle[generation][selected][1] = angle + slice
        self.angle[generation][selected][3] = self.NORMAL
        self.show_parents(generation+1, selected, angle, slice/2.0)
        self.angle[generation][selected+1][0] = angle + slice
        self.angle[generation][selected+1][1] = angle + slice + slice
        self.angle[generation][selected+1][3] = self.NORMAL
        self.show_parents(generation+1, selected + 1, angle + slice, slice/2.0)

    def hide_parents(self, generation, selected, angle):
        if generation >= self.generations: return
        selected = 2 * selected
        self.angle[generation][selected][0] = angle
        self.angle[generation][selected][1] = angle
        self.angle[generation][selected][3] = self.COLLAPSED
        self.hide_parents(generation + 1, selected, angle)
        self.angle[generation][selected+1][0] = angle
        self.angle[generation][selected+1][1] = angle
        self.angle[generation][selected+1][3] = self.COLLAPSED
        self.hide_parents(generation + 1, selected+1, angle)

    def shrink_parents(self, generation, selected, current):
        if generation >= self.generations: return
        selected = 2 * selected
        start,stop,male,state = self.angle[generation][selected]
        if state in [self.NORMAL, self.EXPANDED]:
            slice = (stop - start) / 2.0
            self.angle[generation][selected] = [current, current + slice, 
                                                male,state]
            self.shrink_parents(generation + 1, selected, current)
            current += slice
        start,stop,male,state = self.angle[generation][selected+1]
        if state in [self.NORMAL, self.EXPANDED]:
            slice = (stop - start) / 2.0
            self.angle[generation][selected+1] = [current,current+slice,
                                                  male,state]
            self.shrink_parents(generation + 1, selected+1, current)

    def change_slice(self, generation, selected):
        gstart, gstop, gmale, gstate = self.angle[generation][selected]
        if gstate == self.NORMAL: # let's expand
            if gmale:
                # go to right
                stop = gstop + (gstop - gstart)
                self.angle[generation][selected] = [gstart,stop,gmale,
                                                    self.EXPANDED]
                self.expand_parents(generation + 1, selected, gstart)
                start,stop,male,state = self.angle[generation][selected+1]
                self.angle[generation][selected+1] = [stop,stop,male,
                                                      self.COLLAPSED]
                self.hide_parents(generation+1, selected+1, stop)
            else:
                # go to left
                start = gstart - (gstop - gstart)
                self.angle[generation][selected] = [start,gstop,gmale,
                                                    self.EXPANDED]
                self.expand_parents(generation + 1, selected, start)
                start,stop,male,state = self.angle[generation][selected-1]
                self.angle[generation][selected-1] = [start,start,male,
                                                      self.COLLAPSED]
                self.hide_parents(generation+1, selected-1, start)
        elif gstate == self.EXPANDED: # let's shrink
            if gmale:
                # shrink from right
                slice = (gstop - gstart)/2.0
                stop = gstop - slice
                self.angle[generation][selected] = [gstart,stop,gmale,
                                                    self.NORMAL]
                self.shrink_parents(generation+1, selected, gstart)
                self.angle[generation][selected+1][0] = stop # start
                self.angle[generation][selected+1][1] = stop + slice # stop
                self.angle[generation][selected+1][3] = self.NORMAL
                self.show_parents(generation+1, selected+1, stop, slice/2.0)
            else:
                # shrink from left
                slice = (gstop - gstart)/2.0
                start = gstop - slice
                self.angle[generation][selected] = [start,gstop,gmale,
                                                    self.NORMAL]
                self.shrink_parents(generation+1, selected, start)
                start,stop,male,state = self.angle[generation][selected-1]
                self.angle[generation][selected-1] = [start,start+slice,male,
                                                      self.NORMAL]
                self.show_parents(generation+1, selected-1, start, slice/2.0)

    def on_mouse_up(self, widget, event):
        # Done with mouse movement
        if self.last_x is None or self.last_y is None: return True
        if self.translating:
            self.translating = False
            x, y, w, h = self.allocation
            self.center_xy = w/2 - event.x, h/2 - event.y
        self.last_x, self.last_y = None, None
        self.queue_draw()
        return True

    def on_mouse_move(self, widget, event):
        if self.last_x is None or self.last_y is None: return False
        x, y, w, h = self.allocation
        if self.translating:
            self.center_xy = w/2 - event.x, h/2 - event.y
            self.queue_draw()
            return True
        cx = w/2 - self.center_xy[0]
        cy = h/2 - self.center_xy[1]
        # get the angles of the two points from the center:
        start_angle = math.atan2(event.y - cy, event.x - cx)
        end_angle = math.atan2(self.last_y - cy, self.last_x - cx)
        if start_angle < 0: # second half of unit circle
            start_angle = math.pi + (math.pi + start_angle)
        if end_angle < 0: # second half of unit circle
            end_angle = math.pi + (math.pi + end_angle)
        # now look at change in angle:
        diff_angle = (end_angle - start_angle) % (math.pi * 2.0)
        self.rotate_value -= diff_angle * 180.0/ math.pi
        self.queue_draw()
        self.last_x, self.last_y = event.x, event.y
        return True

    def on_mouse_down(self, widget, event):
        # compute angle, radius, find out who would be there (rotated)
        x, y, w, h = self.allocation
        self.translating = False # keep track of up/down/left/right movement
        cx = w/2 - self.center_xy[0]
        cy = h/2 - self.center_xy[1]
        radius = math.sqrt((event.x - cx) ** 2 + (event.y - cy) ** 2)
        if radius < self.center:
            generation = 0
        else:
            generation = int((radius - self.center) / 
                             self.pixels_per_generation) + 1
        rads = math.atan2( (event.y - cy), (event.x - cx) )
        if rads < 0: # second half of unit circle
            rads = math.pi + (math.pi + rads)
        pos = ((rads/(math.pi * 2) - self.rotate_value/360.) * 360.0) % 360
        # find what person is in this position:
        selected = None
        if (0 < generation < self.generations):
            for p in range(len(self.angle[generation])):
                if self.data[generation][p][1]: # there is a person there
                    start, stop, male, state = self.angle[generation][p]
                    if state == self.COLLAPSED: continue
                    if start <= pos <= stop:
                        selected = p
                        break
        # Handle the click:
        if generation == 0: 
            # left mouse on center:
            if event.button == 1: # left mouse
                # save the mouse location for movements
                self.translating = True
                self.last_x, self.last_y = event.x, event.y
                return True
        if selected is None: # clicked in open area, or center
            if radius < self.center:
                # right mouse
                if event.button == 3 and self.context_popup_callback: 
                    if self.data[0][0][1]:
                        self.context_popup_callback(widget, event, 
                                                    self.data[0][0][1].handle)
                    return True
                else:
                    return False
                # else, what to do on left click?
            else:
                # save the mouse location for movements
                self.last_x, self.last_y = event.x, event.y
                return True
        # Do things based on state, event.state, or button, event.button
        if event.button == 1: # left mouse
            self.change_slice(generation, selected)
        elif event.button == 3: # right mouse
            text, person, parents, child = self.data[generation][selected]
            if person and self.context_popup_callback:
                self.context_popup_callback(widget, event, person.handle)
        self.queue_draw()
        return True

class FanChartGramplet(Gramplet):
    """
    The Gramplet code that realizes the FanChartWidget. 
    """
    def init(self):
        self.set_tooltip(_("Click to expand/contract person\nRight-click for options\nClick and drag in open area to rotate"))
        self.generations = 6
        self.format_helper = FormattingHelper(self.dbstate)
        self.gui.fan = FanChartWidget(self.generations, 
                        context_popup_callback=self.on_popup)
        # Replace the standard textview with the fan chart widget:
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.fan)
        # Make sure it is visible:
        self.gui.fan.show()

    def active_changed(self, handle):
        """
        Method called when active person changes.
        """
        # Reset everything but rotation angle (leave it as is)
        self.update()

    def have_parents(self, person):
        """
        Returns True if a person has parents.
        """
        if person:
            m = self.get_parent(person, "female")
            f = self.get_parent(person, "male")
            return not m is f is None
        return False
            
    def have_children(self, person):
        """
        Returns True if a person has children.
        """
        if person:
            for family_handle in person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and len(family.get_child_ref_list()) > 0:
                    return True
        return False
            
    def get_parent(self, person, gender):
        """
        Get the father if gender == "male", or get mother otherwise.
        """
        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbstate.db.get_family_from_handle(family_id)
                if family:
                    if gender == "male":
                        person_handle = gen.lib.Family.get_father_handle(family)
                    else:
                        person_handle = gen.lib.Family.get_mother_handle(family)
                    if person_handle:
                        return self.dbstate.db.get_person_from_handle(person_handle)
        return None

    def main(self):
        """
        Fill the data structures with the active data. This initializes all 
        data.
        """
        self.gui.fan.reset_generations()
        active_handle = self.get_active('Person')
        person = self.dbstate.db.get_person_from_handle(active_handle)
        if not person: 
            name = None
        else:
            name = name_displayer.display(person)
        parents = self.have_parents(person)
        child = self.have_children(person)
        self.gui.fan.data[0][0] = (name, person, parents, child)
        for current in range(1, self.generations):
            parent = 0
            # name, person, parents, children
            for (n,p,q,c) in self.gui.fan.data[current - 1]:
                # Get father's details:
                person = self.get_parent(p, "male")
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.gui.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.gui.fan.angle[current][parent][3] = self.gui.fan.COLLAPSED
                parent += 1
                # Get mother's details:
                person = self.get_parent(p, "female")
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.gui.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.gui.fan.angle[current][parent][3] = self.gui.fan.COLLAPSED
                parent += 1
        self.gui.fan.queue_draw()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""
        self.set_active('Person', person_handle)
        return True

    def edit_person_cb(self, obj,person_handle):
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass
            return True
        return False

    def copy_person_to_clipboard_cb(self, obj,person_handle):
        """Renders the person data into some lines of text and puts that into the clipboard"""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            cb = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
            cb.set_text( self.format_helper.format_person(person,11))
            return True
        return False

    def on_popup(self, obj, event, person_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation. Copied from PedigreeView.
        """
        
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
        go_image.show()
        go_item = gtk.ImageMenuItem(name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate",self.on_childmenu_changed,person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        edit_item.connect("activate",self.edit_person_cb,person_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        clipboard_item.connect("activate",self.copy_person_to_clipboard_cb,person_handle)
        clipboard_item.show()
        menu.append(clipboard_item)

        # collect all spouses, parents and children
        linked_persons = []
        
        # Go over spouses and build their menu
        item = gtk.MenuItem(_("Spouses"))
        fam_list = person.get_family_handle_list()
        no_spouses = 1
        for fam_id in fam_list:
            family = self.dbstate.db.get_family_from_handle(fam_id)
            if family.get_father_handle() == person.get_handle():
                sp_id = family.get_mother_handle()
            else:
                sp_id = family.get_father_handle()
            spouse = self.dbstate.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(gtk.Menu())
                sp_menu = item.get_submenu()

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            sp_item = gtk.ImageMenuItem(name_displayer.display(spouse))
            sp_item.set_image(go_image)
            linked_persons.append(sp_id)
            sp_item.connect("activate",self.on_childmenu_changed,sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        menu.append(item)
        
        # Go over siblings and build their menu
        item = gtk.MenuItem(_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for f in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(f)
            sib_list = fam.get_child_ref_list()
            for sib_ref in sib_list:
                sib_id = sib_ref.ref
                if sib_id == person.get_handle():
                    continue
                sib = self.dbstate.db.get_person_from_handle(sib_id)
                if not sib:
                    continue

                if no_siblings:
                    no_siblings = 0
                    item.set_submenu(gtk.Menu())
                    sib_menu = item.get_submenu()

                if find_children(self.dbstate.db,sib):
                    label = gtk.Label('<b><i>%s</i></b>' % escape(name_displayer.display(sib)))
                else:
                    label = gtk.Label(escape(name_displayer.display(sib)))

                go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
                go_image.show()
                sib_item = gtk.ImageMenuItem(None)
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0,0)
                sib_item.add(label)
                linked_persons.append(sib_id)
                sib_item.connect("activate",self.on_childmenu_changed,sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        
        # Go over children and build their menu
        item = gtk.MenuItem(_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db,person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue
        
            if no_children:
                no_children = 0
                item.set_submenu(gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.dbstate.db,child):
                label = gtk.Label('<b><i>%s</i></b>' % escape(name_displayer.display(child)))
            else:
                label = gtk.Label(escape(name_displayer.display(child)))

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            child_item = gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate",self.on_childmenu_changed,child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = gtk.MenuItem(_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db,person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db,par):
                label = gtk.Label('<b><i>%s</i></b>' % escape(name_displayer.display(par)))
            else:
                label = gtk.Label(escape(name_displayer.display(par)))

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            par_item = gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate",self.on_childmenu_changed,par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
    
        # Go over parents and build their menu
        item = gtk.MenuItem(_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db,person):
            #if p_id in linked_persons:
            #    continue    # skip already listed family members
            
            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(gtk.Menu())
                per_menu = item.get_submenu()

            label = gtk.Label(escape(name_displayer.display(per)))

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,gtk.ICON_SIZE_MENU)
            go_image.show()
            per_item = gtk.ImageMenuItem(None)
            per_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            per_item.add(label)
            per_item.connect("activate",self.on_childmenu_changed,p_id)
            per_item.show()
            per_menu.append(per_item)
        
        if no_related:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        menu.popup(None,None,None,event.button,event.time)
        return 1
