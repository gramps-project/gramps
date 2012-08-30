#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2012 Benny Malengier
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
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import PangoCairo
import math
import cPickle as pickle

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
import gen.lib
import gui.utils
from gui.ddtargets import DdTargets
from gen.utils.alive import probably_alive

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
class FanChartWidget(Gtk.DrawingArea):
    """
    Interactive Fan Chart Widget. 
    """
    BORDER_WIDTH = 10
    GENCOLOR = ((229,191,252),
                (191,191,252),
                (191,222,252),
                (183,219,197),
                (206,246,209))
    TRANSLATE_PX = 10
    COLLAPSED = 0
    NORMAL = 1
    EXPANDED = 2

    def __init__(self, generations, dbstate, context_popup_callback=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        GObject.GObject.__init__(self)
        self.dbstate = dbstate
        self.translating = False
        self.last_x, self.last_y = None, None
        self.connect("button_release_event", self.on_mouse_up)
        self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("draw", self.on_draw)
        self.connect("drag_data_get", self.on_drag_data_get)
        self.connect("drag_begin", self.on_drag_begin)
        self.connect("drag_end", self.on_drag_end)
        self.context_popup_callback = context_popup_callback
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
        # Enable drag
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                            [],
                            Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                   DdTargets.PERSON_LINK.target_flags,
                   DdTargets.PERSON_LINK.app_id)
        #allow drag to a text document, info on drag_get will be 0L !
        tglist.add_text_targets(0L)
        self.drag_source_set_target_list(tglist)
        self.pixels_per_generation = 50 # size of radius for generation
        ## gotten from experiments with "sans serif 8":
        self.degrees_per_radius = .80
        self._mouse_click = False
        ## Other fonts will have different settings. Can you compute that
        ## from the font size? I have no idea.
        self.generations = generations
        self.rotate_value = 90 # degrees, initially, 1st gen male on right half
        self.center_xy = [0, 0] # distance from center (x, y)
        self.set_generations(self.generations)
        self.center = 50 # pixel radius of center
        self.gen_color = True
        self.layout = self.create_pango_layout('cairo')
        self.layout.set_font_description(Pango.FontDescription("sans 8"))
        self.set_size_request(120,120)

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
            self.data[i] = [(None,) * 4] * 2 ** i
            self.angle[i] = []
            angle = 0
            slice = 360.0 / (2 ** i)
            gender = True
            for count in range(len(self.data[i])):
                # start, stop, male, state
                self.angle[i].append([angle, angle + slice, gender, self.NORMAL])
                angle += slice
                gender = not gender

    def do_size_request(self, requisition):
        """
        Overridden method to handle size request events.
        """
        width, height = self.layout.get_size()
        requisition.width = (width // Pango.SCALE + self.BORDER_WIDTH*4)* 1.45
        requisition.height = (3 * height // Pango.SCALE + self.BORDER_WIDTH*4) * 1.2

    def do_get_preferred_width(self):
        """ GTK3 uses width for height sizing model. This method will 
            override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.width, req.width

    def do_get_preferred_height(self):
        """ GTK3 uses width for height sizing model. This method will 
            override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.height, req.height

    def on_draw(self, widget, cr):
        """
        The main method to do the drawing.
        """
        # first do size request of what we will need
        nrgen = None
        for generation in range(self.generations - 1, 0, -1):
            for p in range(len(self.data[generation])):
                (text, person, parents, child) = self.data[generation][p]
                if person:
                    nrgen = generation
                    break
            if nrgen is not None:
                break
        if nrgen is None:
            nrgen = 1
        halfdist = self.pixels_per_generation * nrgen + self.center
        self.set_size_request(2 * halfdist, 2 * halfdist)
        
        #obtain the allocation
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
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
                                         generation, state, parents, child, person)
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
                cr.move_to(0, 0)
                cr.arc(0, 0, self.TRANSLATE_PX, 0, 2 * math.pi)
                cr.move_to(0,0)
                cr.fill()
        fontw, fonth = self.layout.get_pixel_size()
        cr.move_to((w - fontw - 4), (h - fonth ))
        self.layout.context_changed()
        PangoCairo.show_layout(cr, self.layout)

    def draw_person(self, cr, gender, name, start, stop, generation, 
                    state, parents, child, person):
        """
        Display the piece of pie for a given person. start and stop
        are in degrees. Gender is indication of father position or mother 
        position in the chart
        """
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        start_rad = start * math.pi/180
        stop_rad = stop * math.pi/180
        if self.gen_color:
            r,g,b = self.GENCOLOR[generation % len(self.GENCOLOR)]
            if gender == gen.lib.Person.MALE:
                r *= .9
                g *= .9
                b *= .9
        else:
            try:
                alive = probably_alive(person, self.dbstate.db)
            except RuntimeError:
                alive = False
            backgr, border = gui.utils.color_graph_box(alive, person.gender)
            r, g, b = gui.utils.hex_to_rgb(backgr)
        radius = generation * self.pixels_per_generation + self.center
        # If max generation, and they have parents:
        if generation == self.generations - 1 and parents:
            # draw an indicator
            cr.move_to(0, 0)
            cr.set_source_rgb(255, 255, 255) # white
            cr.arc(0, 0, radius + 10, start_rad, stop_rad) 
            cr.fill()
            cr.move_to(0, 0)
            cr.set_source_rgb(0, 0, 0) # black
            cr.arc(0, 0, radius + 10, start_rad, stop_rad) 
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
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        cr.save()
        # Create a PangoLayout, set the font and text 
        # Draw the layout N_WORDS times in a circle 
        for i in range(len(text)):
            cr.save()
            layout = self.create_pango_layout(text[i])
            layout.set_font_description(Pango.FontDescription("sans 8"))
            angle = 360.0 * i / (radius * self.degrees_per_radius) + pos
            cr.set_source_rgb(0, 0, 0) # black 
            cr.rotate(angle * (math.pi / 180));
            # Inform Pango to re-layout the text with the new transformation
            layout.context_changed()
            width, height = layout.get_size()
            cr.move_to(- (width / Pango.SCALE) / 2.0, - radius)
            PangoCairo.show_layout(cr, layout)
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
        if generation < 1:
            return
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

    def on_mouse_move(self, widget, event):
        self._mouse_click = False
        if self.last_x is None or self.last_y is None:
            # while mouse is moving, we must update the tooltip based on person
            generation, selected = self.person_under_cursor(event.x, event.y)
            tooltip = ""
            if selected is not None:
                text, person, parents, child = self.data[generation][selected]
                if person:
                    tooltip = self.format_helper.format_person(person, 11)
            self.set_tooltip_text(tooltip)
            return False
        
        #translate or rotate should happen
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        if self.translating:
            self.center_xy = w/2 - event.x, h/2 - event.y
        else:
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
            self.last_x, self.last_y = event.x, event.y
        self.queue_draw()
        return True

    def person_under_cursor(self, curx, cury):
        """
        Determine the generation and the position in the generation at 
        position x and y. 
        generation = -1 on center black dot
        generation >= self.generations outside of diagram
        """
        # compute angle, radius, find out who would be there (rotated)
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        cx = w/2 - self.center_xy[0]
        cy = h/2 - self.center_xy[1]
        radius = math.sqrt((curx - cx) ** 2 + (cury - cy) ** 2)
        if radius < self.TRANSLATE_PX:
            generation = -1
        elif radius < self.center:
            generation = 0
        else:
            generation = int((radius - self.center) / 
                             self.pixels_per_generation) + 1

        rads = math.atan2( (cury - cy), (curx - cx) )
        if rads < 0: # second half of unit circle
            rads = math.pi + (math.pi + rads)
        pos = ((rads/(math.pi * 2) - self.rotate_value/360.) * 360.0) % 360
        # if generation is in expand zone:
        # FIXME: add a way of expanding 
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
        elif generation == 0:
            selected = 0
        return generation, selected

    def on_mouse_down(self, widget, event):
        self.translating = False # keep track of up/down/left/right movement
        generation, selected = self.person_under_cursor(event.x, event.y)

        # left mouse on center dot, we translate on left click
        if generation == -1: 
            if event.button == 1: # left mouse
                # save the mouse location for movements
                self.translating = True
                self.last_x, self.last_y = event.x, event.y
                return True

        #click in open area, prepare for a rotate
        if selected is None:
            # save the mouse location for movements
            self.last_x, self.last_y = event.x, event.y
            return True

        #left click on person, prepare for expand/collapse or drag
        if event.button == 1:
            self._mouse_click = True
            self._mouse_click_gen = generation
            self._mouse_click_sel = selected
            return False
    
        #right click on person, context menu
        # Do things based on state, event.get_state(), or button, event.button
        if gui.utils.is_right_click(event):
            text, person, parents, child = self.data[generation][selected]
            if person and self.context_popup_callback:
                self.context_popup_callback(widget, event, person.handle)
                return True

        return False

    def on_mouse_up(self, widget, event):
        if self._mouse_click:
            # no drag occured, expand or collapse the section
            self.change_slice(self._mouse_click_gen, self._mouse_click_sel)
            self._mouse_click = False
            self.queue_draw()
            return True
        if self.last_x is None or self.last_y is None:
            # No translate or rotate
            return True
        if self.translating:
            self.translating = False
            alloc = self.get_allocation()
            x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
            self.center_xy = w/2 - event.x, h/2 - event.y
        self.last_x, self.last_y = None, None
        self.queue_draw()
        return True

    def on_drag_begin(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        self.in_drag = True
        self.drag_source_set_icon_stock('gramps-person')

    def on_drag_end(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        self.in_drag = False

    def on_drag_data_get(self, widget, context, sel_data, info, time):
        """
        Returned parameters after drag.
        Specified for 'person-link', for others return text info about person.
        """
        tgs = [x.name() for x in context.list_targets()]
        text, person, parents, child = self.data[self._mouse_click_gen][self._mouse_click_sel]
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type,
                    id(self), person.get_handle(), 0)
            sel_data.set(sel_data.get_target(), 8, pickle.dumps(data))
        elif ('TEXT' in tgs or 'text/plain' in tgs) and info == 0L:
            sel_data.set_text(self.format_helper.format_person(person, 11), -1)
