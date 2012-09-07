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

from __future__ import division

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
import cairo
import math
import colorsys
import cPickle as pickle
from cgi import escape

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
from gen.errors import WindowActiveError
from gui.editors import EditPerson
import gen.lib
import gui.utils
from gui.ddtargets import DdTargets
from gen.utils.alive import probably_alive
from gen.utils.libformatting import FormattingHelper
from gen.utils.db import (find_children, find_parents, find_witnessed_people,
                          get_age)

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
    
    PIXELS_PER_GENERATION = 50 # size of radius for generation
    BORDER_EDGE_WIDTH = 10
    CHILDRING_WIDTH = 12
    TRANSLATE_PX = 10
    
    BACKGROUND_SCHEME1 = 0
    BACKGROUND_SCHEME2 = 1
    BACKGROUND_GENDER = 2
    BACKGROUND_WHITE = 3
    BACKGROUND_GRAD_GEN = 4
    BACKGROUND_GRAD_AGE = 5
    GENCOLOR = {
        BACKGROUND_SCHEME1: ((255, 63,  0),
                             (255,175, 15),
                             (255,223, 87),
                             (255,255,111),
                             (159,255,159),
                             (111,215,255),
                             ( 79,151,255),
                             (231, 23,255),
                             (231, 23,121),
                             (210,170,124),
                             (189,153,112)),
        BACKGROUND_SCHEME2: ((229,191,252),
                             (191,191,252),
                             (191,222,252),
                             (183,219,197),
                             (206,246,209)),
        BACKGROUND_WHITE: ((255,255,255),
                           (255,255,255),),
        }
    
    MAX_AGE = 100

    COLLAPSED = 0
    NORMAL = 1
    EXPANDED = 2

    def __init__(self, dbstate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        GObject.GObject.__init__(self)
        self.dbstate = dbstate
        self.translating = False
        self.goto = None
        self.on_popup = callback_popup
        self.last_x, self.last_y = None, None
        self.fontdescr = "Sans"
        self.fontsize = 8
        self.connect("button_release_event", self.on_mouse_up)
        self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("draw", self.on_draw)
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
        self.connect("drag_data_get", self.on_drag_data_get)
        self.connect("drag_begin", self.on_drag_begin)
        self.connect("drag_end", self.on_drag_end)
        # Enable drop
        self.drag_dest_set(Gtk.DestDefaults.MOTION |
                            Gtk.DestDefaults.DROP,
                            [],
                            Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                   DdTargets.PERSON_LINK.target_flags,
                   DdTargets.PERSON_LINK.app_id)
        self.drag_dest_set_target_list(tglist)
        self.connect('drag_data_received', self.on_drag_data_received)

        self._mouse_click = False
        self.rotate_value = 90 # degrees, initially, 1st gen male on right half
        self.center_xy = [0, 0] # distance from center (x, y)
        self.center = 50 # pixel radius of center
        #default values
        self.reset(None, 9, self.BACKGROUND_GRAD_GEN, True, True, 'Sans', '#0000FF',
                    '#FF0000', None, 0.5)
        self.set_size_request(120, 120)

    def reset(self, root_person_handle, maxgen, background, childring,
              radialtext, fontdescr, grad_start, grad_end,
              filter, alpha_filter):
        """
        Reset all of the data:
         root_person_handle = person to show
         maxgen = maximum generations to show
         background = config setting of which background procedure to use (int)
         childring = to show the center ring with children or not
         radialtext = try to use radial text or not
         fontdescr = string describing the font to use
         grad_start, grad_end: colors to use for background procedure
         filter = the person filter to apply to the people in the chart
         alpha = the alpha transparency value (0-1) to apply to filtered out data
        """
        self.cache_fontcolor = {}
        
        self.radialtext = radialtext
        self.childring = childring
        self.background = background
        self.fontdescr = fontdescr
        self.grad_start = grad_start
        self.grad_end = grad_end
        self.filter = filter
        self.alpha_filter = alpha_filter
        
        self.set_generations(maxgen)
        
        # fill the data structure: self.data, self.childrenroot, self.angle
        self._fill_data_structures(root_person_handle)
    
        # prepare the colors for the boxes 
        self.prepare_background_box()

    def _fill_data_structures(self, root_person_handle):
        person = self.dbstate.db.get_person_from_handle(root_person_handle)
        if not person: 
            name = None
        else:
            name = name_displayer.display(person)
        parents = self._have_parents(person)
        child = self._have_children(person)
        # our data structure is the text, the person object, parents, child and
        # list for userdata which we might fill in later.
        self.data[0][0] = (name, person, parents, child, [])
        self.childrenroot = []
        if child:
            childlist = find_children(self.dbstate.db, person)
            for child_handle in childlist:
                child = self.dbstate.db.get_person_from_handle(child_handle)
                if not child:
                    continue
                else:
                    self.childrenroot.append((child_handle, child.get_gender(),
                                              self._have_children(child), []))
        for current in range(1, self.generations):
            parent = 0
            # name, person, parents, children
            for (n, p, q, c, d) in self.data[current - 1]:
                # Get father's details:
                person = self._get_parent(p, True)
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self._have_parents(person)
                else:
                    parents = None
                self.data[current][parent] = (name, person, parents, None, [])
                if person is None:
                    # start,stop,male/right,state
                    self.angle[current][parent][3] = self.COLLAPSED
                parent += 1
                # Get mother's details:
                person = self._get_parent(p, False)
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self._have_parents(person)
                else:
                    parents = None
                self.data[current][parent] = (name, person, parents, None, [])
                if person is None:
                    # start,stop,male/right,state
                    self.angle[current][parent][3] = self.COLLAPSED
                parent += 1

    def _have_parents(self, person):
        """
        Returns True if a person has parents. 
        TODO: is there no util function for this
        """
        if person:
            m = self._get_parent(person, False)
            f = self._get_parent(person, True)
            return not m is f is None
        return False
            
    def _have_children(self, person):
        """
        Returns True if a person has children.
        TODO: is there no util function for this
        """
        if person:
            for family_handle in person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and len(family.get_child_ref_list()) > 0:
                    return True
        return False

    def _get_parent(self, person, father):
        """
        Get the father of the family if father == True, otherwise mother
        """
        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbstate.db.get_family_from_handle(family_id)
                if family:
                    if father:
                        person_handle = gen.lib.Family.get_father_handle(family)
                    else:
                        person_handle = gen.lib.Family.get_mother_handle(family)
                    if person_handle:
                        return self.dbstate.db.get_person_from_handle(person_handle)
        return None
    
    def set_generations(self, generations):
        """
        Set the generations to max, and fill data structures with initial data.
        """
        self.generations = generations
        self.angle = {}
        self.data = {}
        self.childrenroot = []
        for i in range(self.generations):
            # name, person, parents?, children?
            self.data[i] = [(None,) * 5] * 2 ** i
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
        requisition.width = 2 * self.halfdist()
        requisition.height = requisition.width

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

    def nrgen(self):
        #compute the number of generations present
        nrgen = None
        for generation in range(self.generations - 1, 0, -1):
            for p in range(len(self.data[generation])):
                (text, person, parents, child, userdata) = self.data[generation][p]
                if person:
                    nrgen = generation
                    break
            if nrgen is not None:
                break
        if nrgen is None:
            nrgen = 1
        return nrgen

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        nrgen = self.nrgen()
        return self.PIXELS_PER_GENERATION * nrgen + self.center \
                + self.BORDER_EDGE_WIDTH

    def on_draw(self, widget, cr, scale=1.):
        """
        The main method to do the drawing.
        If widget is given, we assume we draw in GTK3 and use the allocation. 
        To draw raw on the cairo context cr, set widget=None.
        """
        # first do size request of what we will need
        nrgen = self.nrgen()
        halfdist = self.PIXELS_PER_GENERATION * nrgen + self.center
        self.set_size_request(2 * halfdist, 2 * halfdist)
        
        #obtain the allocation
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        cr.scale(scale, scale)
        if widget:
            cr.translate(w/2. - self.center_xy[0], h/2. - self.center_xy[1])
        else:
            cr.translate(halfdist - self.center_xy[0], halfdist - self.center_xy[1])
        cr.save()
        cr.rotate(self.rotate_value * math.pi/180)
        for generation in range(self.generations - 1, 0, -1):
            for p in range(len(self.data[generation])):
                (text, person, parents, child, userdata) = self.data[generation][p]
                if person:
                    start, stop, male, state = self.angle[generation][p]
                    if state in [self.NORMAL, self.EXPANDED]:
                        self.draw_person(cr, gender_code(male), 
                                         text, start, stop, 
                                         generation, state, parents, child,
                                         person, userdata)
        cr.set_source_rgb(1, 1, 1) # white
        cr.move_to(0,0)
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.move_to(0,0)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, self.center, 0, 2 * math.pi)
        cr.stroke()
        cr.restore()
        # Draw center person:
        (text, person, parents, child, userdata) = self.data[0][0]
        if person:
            r, g, b, a = self.background_box(person, person.gender, 0, userdata)
            cr.arc(0, 0, self.center, 0, 2 * math.pi)
            cr.set_source_rgba(r/255, g/255, b/255, a)
            cr.fill()
            cr.save()
            name = name_displayer.display(person)
            self.draw_text(cr, name, self.center - 10, 95, 455, False,
                           self.fontcolor(r,g,b))
            cr.restore()
            #draw center to move chart
            cr.set_source_rgb(0, 0, 0) # black
            cr.move_to(self.TRANSLATE_PX, 0)
            cr.arc(0, 0, self.TRANSLATE_PX, 0, 2 * math.pi)
            if child: # has at least one child
                cr.fill()
            else:
                cr.stroke()
            if child and self.childring:
                self.drawchildring(cr)
        if self.background in [self.BACKGROUND_GRAD_AGE]:
            self.draw_gradient(cr, widget, halfdist)

    def draw_person(self, cr, gender, name, start, stop, generation, 
                    state, parents, child, person, userdata):
        """
        Display the piece of pie for a given person. start and stop
        are in degrees. Gender is indication of father position or mother 
        position in the chart
        """
        cr.save()
        start_rad = start * math.pi/180
        stop_rad = stop * math.pi/180
        r, g, b, a = self.background_box(person, gender, generation, userdata)
        radius = generation * self.PIXELS_PER_GENERATION + self.center
        # If max generation, and they have parents:
        if generation == self.generations - 1 and parents:
            # draw an indicator
            radmax = radius + self.BORDER_EDGE_WIDTH
            cr.move_to(radmax*math.cos(start_rad), radmax*math.sin(start_rad))
            cr.arc(0, 0, radius + self.BORDER_EDGE_WIDTH, start_rad, stop_rad)
            cr.line_to(radius*math.cos(stop_rad), radius*math.sin(stop_rad))
            cr.arc_negative(0, 0, radius, stop_rad, start_rad)
            cr.close_path()
            ##path = cr.copy_path() # not working correct
            cr.set_source_rgb(255, 255, 255) # white
            cr.fill()
            #and again for the border
            cr.move_to(radmax*math.cos(start_rad), radmax*math.sin(start_rad))
            cr.arc(0, 0, radius + self.BORDER_EDGE_WIDTH, start_rad, stop_rad)
            cr.line_to(radius*math.cos(stop_rad), radius*math.sin(stop_rad))
            cr.arc_negative(0, 0, radius, stop_rad, start_rad)
            cr.close_path()
            ##cr.append_path(path) # not working correct
            cr.set_source_rgb(0, 0, 0) # black
            cr.stroke()
        # now draw the person
        cr.move_to(radius * math.cos(start_rad), radius * math.sin(start_rad))
        cr.arc(0, 0, radius, start_rad, stop_rad)
        radmin = radius - self.PIXELS_PER_GENERATION
        cr.line_to(radmin * math.cos(stop_rad), radmin * math.sin(stop_rad))
        cr.arc_negative(0, 0, radmin, stop_rad, start_rad)
        cr.close_path()
        ##path = cr.copy_path() # not working correct
        cr.set_source_rgba(r/255., g/255., b/255., a) 
        cr.fill()
        #and again for the border
        cr.move_to(radius * math.cos(start_rad), radius * math.sin(start_rad))
        cr.arc(0, 0, radius, start_rad, stop_rad)
        radmin = radius - self.PIXELS_PER_GENERATION
        cr.line_to(radmin * math.cos(stop_rad), radmin * math.sin(stop_rad))
        cr.arc_negative(0, 0, radmin, stop_rad, start_rad)
        cr.close_path()
        ##cr.append_path(path) # not working correct
        cr.set_source_rgb(0, 0, 0) # black
        if state == self.NORMAL: # normal
            cr.set_line_width(1)
        else: # EXPANDED
            cr.set_line_width(3)
        cr.stroke()
        cr.set_line_width(1)
        if self.last_x is None or self.last_y is None: 
            #we are not in a move, so draw text
            radial = False
            radstart = radius - self.PIXELS_PER_GENERATION/2
            if self.radialtext and generation >= 6:
                spacepolartext = radstart * (stop-start)*math.pi/180
                if spacepolartext < self.PIXELS_PER_GENERATION * 1.1:
                    # more space to print it radial
                    radial = True
                    radstart = radius - self.PIXELS_PER_GENERATION + 4
            self.draw_text(cr, name, radstart, start, stop, radial, 
                           self.fontcolor(r, g, b))
        cr.restore()

    def drawchildring(self, cr):
        cr.move_to(self.TRANSLATE_PX + self.CHILDRING_WIDTH, 0)
        cr.set_source_rgb(0, 0, 0) # black
        cr.set_line_width(1)
        cr.arc(0, 0, self.TRANSLATE_PX + self.CHILDRING_WIDTH, 0, 2 * math.pi)
        cr.stroke()
        nrchild = len(self.childrenroot)
        #Y axis is downward. positve angles are hence clockwise
        startangle = math.pi
        if nrchild <= 4:
            angleinc = math.pi/2
        else:
            angleinc = 2 * math.pi / nrchild
        self.angle[-2] = []
        for child in self.childrenroot:
            self.drawchild(cr, child, startangle, angleinc)
            startangle += angleinc

    def drawchild(self, cr, childdata, start, inc):
        child_handle, child_gender, has_child, userdata = childdata
        # in polar coordinates what is to draw
        rmin = self.TRANSLATE_PX
        rmax = self.TRANSLATE_PX + self.CHILDRING_WIDTH
        thetamin = start
        thetamax = start + inc
        # add child to angle storage
        self.angle[-2].append([thetamin, thetamax, child_gender, None])
        #draw child now
        cr.move_to(rmin*math.cos(thetamin), rmin*math.sin(thetamin))
        cr.arc(0, 0, rmin, thetamin, thetamax)
        cr.line_to(rmax*math.cos(thetamax), rmax*math.sin(thetamax))
        cr.arc_negative(0, 0, rmax, thetamax, thetamin)
        cr.close_path()
        ##path = cr.copy_path() # not working correct
        cr.set_source_rgb(0, 0, 0) # black
        cr.set_line_width(1)
        cr.stroke()
        #now again to fill
        person = self.dbstate.db.get_person_from_handle(child_handle)
        r, g, b, a = self.background_box(person, person.gender, -1, userdata)
        cr.move_to(rmin*math.cos(thetamin), rmin*math.sin(thetamin))
        cr.arc(0, 0, rmin, thetamin, thetamax)
        cr.line_to(rmax*math.cos(thetamax), rmax*math.sin(thetamax))
        cr.arc_negative(0, 0, rmax, thetamax, thetamin)
        cr.close_path()
        ##cr.append_path(path) # not working correct
        cr.set_source_rgba(r/255., g/255., b/255., a) 
        cr.fill()

    def draw_text(self, cr, text, radius, start, stop, radial=False,
                  fontcolor=(0, 0, 0)):
        """
        Display text at a particular radius, between start and stop
        degrees.
        """
        cr.save()
        font = Pango.FontDescription(self.fontdescr)
        fontsize = self.fontsize
        font.set_size(fontsize * Pango.SCALE)
        cr.set_source_rgb(fontcolor[0], fontcolor[1], fontcolor[2])
        if radial and self.radialtext:
            cr.save()
            layout = self.create_pango_layout(text)
            layout.set_font_description(font)
            w, h = layout.get_size()
            w = w / Pango.SCALE + 5 # 5 pixel padding
            h = h / Pango.SCALE + 4 # 4 pixel padding
            #first we check if height is ok
            degneedheight = h / radius * (180 / math.pi)
            degavailheight = stop-start
            degoffsetheight = 0
            if degneedheight > degavailheight:
                #reduce height
                fontsize = degavailheight / degneedheight * fontsize / 2
                font.set_size(fontsize * Pango.SCALE)
                layout = self.create_pango_layout(text)
                layout.set_font_description(font)
                w, h = layout.get_size()
                w = w / Pango.SCALE + 5 # 5 pixel padding
                h = h / Pango.SCALE + 4 # 4 pixel padding
                #first we check if height is ok
                degneedheight = h / radius * (180 / math.pi)
                degavailheight = stop-start
                if degneedheight > degavailheight:
                    #we could not fix it, no text
                    text = ""
            if text:
                #spread rest
                degoffsetheight = (degavailheight - degneedheight) / 2
            txlen = len(text)
            if w > self.PIXELS_PER_GENERATION:
                txlen = int(w/self.PIXELS_PER_GENERATION * txlen)
            cont = True
            while cont:
                layout = self.create_pango_layout(text[:txlen])
                layout.set_font_description(font)
                w, h = layout.get_size()
                w = w / Pango.SCALE + 5 # 5 pixel padding
                h = h / Pango.SCALE + 4 # 4 pixel padding
                if w > self.PIXELS_PER_GENERATION:
                    if txlen <= 1:
                        cont = False
                        txlen = 0
                    else:
                        txlen -= 1
                else:
                    cont = False
            # offset for cairo-font system is 90
            rotval = self.rotate_value % 360 - 90
            if (start + rotval) % 360 > 179:
                pos = start + degoffsetheight + 90 - 90
            else:
                pos = stop - degoffsetheight + 180
            cr.rotate(pos * math.pi / 180)
            layout.context_changed()
            if (start + rotval) % 360 > 179:
                cr.move_to(radius+2, 0)
            else:
                cr.move_to(-radius-self.PIXELS_PER_GENERATION+6, 0)
            PangoCairo.show_layout(cr, layout)
            cr.restore()
        else:
            # center text:
            #  1. determine degrees of the text we can draw
            degpadding = 5 / radius * (180 / math.pi) # degrees for 5 pixel padding
            degneed = degpadding
            maxlen = len(text)
            for i in range(len(text)):
                layout = self.create_pango_layout(text[i])
                layout.set_font_description(font)
                w, h = layout.get_size()
                w = w / Pango.SCALE + 2 # 2 pixel padding after letter
                h = h / Pango.SCALE + 2 # 2 pixel padding
                degneed += w / radius * (180 / math.pi)
                if degneed > stop - start:
                    #outside of the box
                    maxlen = i
                    break
            #  2. determine degrees over we can distribute before and after
            if degneed > stop - start:
                degover = 0
            else:
                degover = stop - start - degneed - degpadding
            #  3. now draw this text, letter per letter
            text = text[:maxlen]
            
            # offset for cairo-font system is 90, padding used is 5:
            pos = start + 90 + degpadding + degover / 2
            # Create a PangoLayout, set the font and text 
            # Draw the layout N_WORDS times in a circle 
            for i in range(len(text)):
                layout = self.create_pango_layout(text[i])
                layout.set_font_description(font)
                w, h = layout.get_size()
                w = w / Pango.SCALE + 2 # 4 pixel padding after word
                h = h / Pango.SCALE + 2 # 4 pixel padding
                degneed = w / radius * (180 / math.pi)
                if pos+degneed > stop + 90:
                    #failsafe, outside of the box, redo
                    break

                cr.save()
                cr.rotate(pos * math.pi / 180)
                pos = pos + degneed
                # Inform Pango to re-layout the text with the new transformation
                layout.context_changed()
                #width, height = layout.get_size()
                #r.move_to(- (width / Pango.SCALE) / 2.0, - radius)
                cr.move_to(0, - radius)
                PangoCairo.show_layout(cr, layout)
                cr.restore()
        cr.restore()

    def draw_gradient(self, cr, widget, halfdist):
        gradwidth = 10
        gradheight = 10
        starth = 25
        startw = 5
        alloc = self.get_allocation()
        x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height
        cr.save()
        if widget:
            cr.translate(-w/2. + self.center_xy[0], -h/2. + self.center_xy[1])
        else:
            cr.translate(-halfdist + self.center_xy[0], -halfdist + self.center_xy[1])
        font = Pango.FontDescription(self.fontdescr)
        fontsize = self.fontsize
        font.set_size(fontsize * Pango.SCALE)
        for color, text in zip(self.gradcol, self.gradval):
            cr.move_to(startw, starth)
            cr.rectangle(startw, starth, gradwidth, gradheight)
            cr.set_source_rgb(color[0], color[1], color[2])
            cr.fill()
            layout = self.create_pango_layout(text)
            layout.set_font_description(font)
            cr.move_to(startw+gradwidth+4, starth)
            cr.set_source_rgb(0, 0, 0) #black
            PangoCairo.show_layout(cr, layout)
            starth = starth+gradheight
        cr.restore()

    def prepare_background_box(self):
        """
        Method that is called every reset of the chart, to precomputed values
        needed for the background of the boxes
        """
        maxgen = self.generations
        cstart = gui.utils.hex_to_rgb(self.grad_start)
        cend = gui.utils.hex_to_rgb(self.grad_end)
        cstart_hsv = colorsys.rgb_to_hsv(cstart[0]/255, cstart[1]/255, 
                                         cstart[2]/255)
        cend_hsv = colorsys.rgb_to_hsv(cend[0]/255, cend[1]/255, 
                                       cend[2]/255)
        if self.background == self.BACKGROUND_GENDER:
            # nothing to precompute
            self.colors =  None
        elif self.background == self.BACKGROUND_GRAD_GEN:
            #compute the colors, -1, 0, ..., maxgen
            divs = [x/(maxgen-1) for x in range(maxgen)]
            rgb_colors = [colorsys.hsv_to_rgb(
                            (1-x) * cstart_hsv[0] + x * cend_hsv[0], 
                            (1-x) * cstart_hsv[1] + x * cend_hsv[1],
                            (1-x) * cstart_hsv[2] + x * cend_hsv[2],
                            ) for x in divs]
            self.colors = [(255*r, 255*g, 255*b) for r, g, b in rgb_colors]
        elif self.background == self.BACKGROUND_GRAD_AGE:
            # we fill in in the data structure what the age is, None if no age
            for generation in range(self.generations):
                for p in range(len(self.data[generation])):
                    agecol = (255, 255, 255)  # white
                    (text, person, parents, child, userdata) = self.data[generation][p]
                    if person:
                        age = get_age(self.dbstate.db, person)
                        if age is not None:
                            age = age[0]
                            if age < 0:
                                age = 0
                            #now determine fraction for gradient
                            agefrac = age / self.MAX_AGE
                            agecol = colorsys.hsv_to_rgb(
                                (1-agefrac) * cstart_hsv[0] + agefrac * cend_hsv[0], 
                                (1-agefrac) * cstart_hsv[1] + agefrac * cend_hsv[1],
                                (1-agefrac) * cstart_hsv[2] + agefrac * cend_hsv[2],
                                )
                    userdata.append((agecol[0]*255, agecol[1]*255, agecol[2]*255))
            # same for child
            for childdata in self.childrenroot:
                agecol = (255, 255, 255)  # white
                child_handle, child_gender, has_child, userdata = childdata
                child = self.dbstate.db.get_person_from_handle(child_handle)
                age = get_age(self.dbstate.db, child)
                if age is not None:
                    age = age[0]
                    if age < 0:
                        age = 0
                    #now determine fraction for gradient
                    agefrac = age / self.MAX_AGE
                    agecol = colorsys.hsv_to_rgb(
                        (1-agefrac) * cstart_hsv[0] + agefrac * cend_hsv[0], 
                        (1-agefrac) * cstart_hsv[1] + agefrac * cend_hsv[1],
                        (1-agefrac) * cstart_hsv[2] + agefrac * cend_hsv[2],
                        )
                userdata.append((agecol[0]*255, agecol[1]*255, agecol[2]*255))
            #now create gradient data, 5 values from 0 to max
            steps = 5
            divs = [x/steps for x in range(steps+1)]
            self.gradval = ['%d' % int(x*self.MAX_AGE) for x in divs]
            self.gradcol = [colorsys.hsv_to_rgb(
                        (1-div) * cstart_hsv[0] + div * cend_hsv[0], 
                        (1-div) * cstart_hsv[1] + div * cend_hsv[1],
                        (1-div) * cstart_hsv[2] + div * cend_hsv[2],
                        ) for div in divs]
        else:
            # known colors per generation, set or compute them
            self.colors = self.GENCOLOR[self.background]

    def background_box(self, person, gender, generation, userdata):
        """
        determine red, green, blue value of background of the box of person,
        which has gender gender, and is in ring generation
        """
        if generation == 0 and self.background in [self.BACKGROUND_GENDER, 
                self.BACKGROUND_GRAD_GEN, self.BACKGROUND_SCHEME1,
                self.BACKGROUND_SCHEME2]:
            # white for center person:
            color = (255, 255, 255)
        elif self.background == self.BACKGROUND_GENDER:
            try:
                alive = probably_alive(person, self.dbstate.db)
            except RuntimeError:
                alive = False
            backgr, border = gui.utils.color_graph_box(alive, person.gender)
            color = gui.utils.hex_to_rgb(backgr)
        elif self.background == self.BACKGROUND_GRAD_AGE:
            color = userdata[0]
        else:
            if self.background == self.BACKGROUND_GRAD_GEN and generation < 0:
                generation = 0
            color = self.colors[generation % len(self.colors)]
            if gender == gen.lib.Person.MALE:
                color = [x*.9 for x in color]
        # now we set transparency data
        if self.filter and not self.filter.match(person.handle, self.dbstate.db):
            alpha = self.alpha_filter
        else:
            alpha = 1.
        
        return color[0], color[1], color[2], alpha
    
    def fontcolor(self, r, g, b):
        """
        return the font color based on the r, g, b of the background
        """
        try:
            return self.cache_fontcolor[(r, g, b)]
        except KeyError:
            hls = colorsys.rgb_to_hls(r/255, g/255, b/255)
            # we use the lightness value to determine white or black font
            if hls[1] > 0.4:
                self.cache_fontcolor[(r, g, b)] = (0, 0, 0)
            else:
                self.cache_fontcolor[(r, g, b)] = (255, 255, 255)
        return self.cache_fontcolor[(r, g, b)]

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
            person = None
            if selected is not None and generation >= 0:
                text, person, parents, child, userdata = \
                                                self.data[generation][selected]
            elif selected is not None and generation == -2:
                child_handle, child_gender, has_child, userdata = \
                                                self.childrenroot[selected]
                person = self.dbstate.db.get_person_from_handle(child_handle)
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
        elif (self.childring and self.childrenroot and 
                    radius < self.TRANSLATE_PX + self.CHILDRING_WIDTH):
            generation = -2  # indication of one of the children
        elif radius < self.center:
            generation = 0
        else:
            generation = int((radius - self.center) / 
                             self.PIXELS_PER_GENERATION) + 1

        rads = math.atan2( (cury - cy), (curx - cx) )
        if rads < 0: # second half of unit circle
            rads = math.pi + (math.pi + rads)
        pos = ((rads/(math.pi * 2) - self.rotate_value/360.) * 360.0) % 360
        #children are in cairo angle (clockwise) from pi to 3 pi
        #rads however is clock 0 to 2 pi
        if rads < math.pi:
            rads += 2 * math.pi
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
        elif generation == -2:
            for p in range(len(self.angle[generation])):
                start, stop, male, state = self.angle[generation][p]
                if start <= rads <= stop:
                    selected = p
                    break
            
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
            if generation == -2:
                child_handle, child_gender, has_child, userdata = \
                                                self.childrenroot[selected]
                person = self.dbstate.db.get_person_from_handle(child_handle)
            else:
                text, person, parents, child, userdata = \
                                                self.data[generation][selected]
            if person and self.on_popup:
                self.on_popup(widget, event, person.handle)
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
        if self._mouse_click_gen == -2:
            #children
            child_handle, child_gender, has_child, userdata = \
                                    self.childrenroot[self._mouse_click_sel]
            person = self.dbstate.db.get_person_from_handle(child_handle)
        else:
            text, person, parents, child, userdata \
                    = self.data[self._mouse_click_gen][self._mouse_click_sel]
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type,
                    id(self), person.get_handle(), 0)
            sel_data.set(sel_data.get_target(), 8, pickle.dumps(data))
        elif ('TEXT' in tgs or 'text/plain' in tgs) and info == 0L:
            sel_data.set_text(self.format_helper.format_person(person, 11), -1)

    def on_drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is defined, extract the value from sel_data.data
        """
        gen, persatcurs = self.person_under_cursor(x, y)
        if gen == -1 or gen == 0:
            if sel_data and sel_data.get_data():
                (drag_type, idval, handle, val) = pickle.loads(sel_data.get_data())
                self.goto(self, handle)
                

class FanChartGrampsGUI(object):
    """ class for functions fanchart GUI elements will need in Gramps
    """
    def __init__(self, maxgen, background, childring, radialtext, font,
                 on_childmenu_changed):
        """
        Common part of GUI that shows Fan Chart, needs to know what to do if
        one moves via Fan Ch    def set_fan(self, fan):art to a new person
        on_childmenu_changed: in popup, function called on moving to a new person
        """
        self.fan = None
        self.on_childmenu_changed = on_childmenu_changed
        self.format_helper = FormattingHelper(self.dbstate)

        self.maxgen = maxgen 
        self.background = background
        self.childring = childring
        self.radialtext = radialtext
        self.fonttype = font
        self.grad_start = '#0000FF'
        self.grad_end = '#FF0000'
        self.generic_filter = None   # the filter to use. Named as in PageView
        self.alpha_filter = 0.2      # transparency of filtered out values
    
    def set_fan(self, fan):
        """
        Set the fanchartwidget to work on
        """
        self.fan = fan
        self.fan.format_helper = self.format_helper
        self.fan.goto = self.on_childmenu_changed

    def main(self):
        """
        Fill the data structures with the active data. This initializes all 
        data.
        """
        root_person_handle = self.get_active('Person')
        self.fan.reset(root_person_handle, self.maxgen, self.background, self.childring,
                       self.radialtext, self.fonttype,
                       self.grad_start, self.grad_end,
                       self.generic_filter, self.alpha_filter)
        self.fan.queue_draw()

    def on_popup(self, obj, event, person_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation. Copied from PedigreeView.
        """
        #store menu for GTK3 to avoid it being destroyed before showing
        self.menu = Gtk.Menu()
        menu = self.menu
        menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
        go_image.show()
        go_item = Gtk.ImageMenuItem(name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate", self.on_childmenu_changed, person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = Gtk.ImageMenuItem.new_from_stock(stock_id=Gtk.STOCK_EDIT, accel_group=None)
        edit_item.connect("activate", self.edit_person_cb, person_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = Gtk.ImageMenuItem.new_from_stock(stock_id=Gtk.STOCK_COPY, accel_group=None)
        clipboard_item.connect("activate", self.copy_person_to_clipboard_cb,
                               person_handle)
        clipboard_item.show()
        menu.append(clipboard_item)

        # collect all spouses, parents and children
        linked_persons = []
        
        # Go over spouses and build their menu
        item = Gtk.MenuItem(label=_("Spouses"))
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
                item.set_submenu(Gtk.Menu())
                sp_menu = item.get_submenu()

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            sp_item = Gtk.ImageMenuItem(name_displayer.display(spouse))
            sp_item.set_image(go_image)
            linked_persons.append(sp_id)
            sp_item.connect("activate", self.on_childmenu_changed, sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        menu.append(item)
        
        # Go over siblings and build their menu
        item = Gtk.MenuItem(label=_("Siblings"))
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
                    item.set_submenu(Gtk.Menu())
                    sib_menu = item.get_submenu()

                if find_children(self.dbstate.db,sib):
                    label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(sib)))
                else:
                    label = Gtk.Label(label=escape(name_displayer.display(sib)))

                go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
                go_image.show()
                sib_item = Gtk.ImageMenuItem(None)
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0,0)
                sib_item.add(label)
                linked_persons.append(sib_id)
                sib_item.connect("activate", self.on_childmenu_changed, sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        
        # Go over children and build their menu
        item = Gtk.MenuItem(label=_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db, person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue
        
            if no_children:
                no_children = 0
                item.set_submenu(Gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.dbstate.db,child):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(child)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            child_item = Gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate", self.on_childmenu_changed, child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db,person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db,par):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(par)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            par_item = Gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate",self.on_childmenu_changed, par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
    
        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db,person):
            #if p_id in linked_persons:
            #    continue    # skip already listed family members
            
            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(Gtk.Menu())
                per_menu = item.get_submenu()

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            per_item = Gtk.ImageMenuItem(None)
            per_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            per_item.add(label)
            per_item.connect("activate", self.on_childmenu_changed, p_id)
            per_item.show()
            per_menu.append(per_item)
        
        if no_related:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        menu.popup(None, None, None, None, event.button, event.time)
        return 1
    
    def edit_person_cb(self, obj,person_handle):
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
            return True
        return False

    def copy_person_to_clipboard_cb(self, obj,person_handle):
        """Renders the person data into some lines of text and puts that into the clipboard"""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            cb = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), 
                        Gdk.SELECTION_CLIPBOARD)
            cb.set_text( self.format_helper.format_person(person,11))
            return True
        return False
