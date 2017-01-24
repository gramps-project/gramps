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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

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
import cairo
import math
import colorsys
import pickle
from html import escape

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from ..editors import EditPerson, EditFamily
from ..utils import hex_to_rgb
from ..ddtargets import DdTargets
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.libformatting import FormattingHelper
from gramps.gen.utils.db import (find_children, find_parents, find_witnessed_people,
                          get_age, get_timeperiod)
from gramps.gen.plug.report.utils import find_spouse
from .fanchart import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
pi = math.pi

PIXELS_PER_GENPERSON = 30 # size of radius for generation of children
PIXELS_PER_GENFAMILY = 20 # size of radius for family
PIXELS_PER_RECLAIM = 4 # size of the radius of pixels taken from family to reclaim space
PARENTRING_WIDTH = 12      # width of the parent ring inside the person

ANGLE_CHEQUI = 0   #Algorithm with homogeneous children distribution
ANGLE_WEIGHT = 1   #Algorithm for angle computation based on nr of descendants


#-------------------------------------------------------------------------
#
# FanChartDescWidget
#
#-------------------------------------------------------------------------

class FanChartDescWidget(FanChartBaseWidget):
    """
    Interactive Fan Chart Widget.
    """
    CENTER = 60    # we require a larger center

    def __init__(self, dbstate, uistate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        self.set_values(None, 9, BACKGROUND_GRAD_GEN, 'Sans', '#0000FF',
                    '#FF0000', None, 0.5, FORM_CIRCLE, ANGLE_WEIGHT, '#888a85')
        FanChartBaseWidget.__init__(self, dbstate, uistate, callback_popup)

    def set_values(self, root_person_handle, maxgen, background,
              fontdescr, grad_start, grad_end,
              filter, alpha_filter, form, angle_algo, dupcolor):
        """
        Reset the values to be used:

        :param root_person_handle: person to show
        :param maxgen: maximum generations to show
        :param background: config setting of which background procedure to use
        :type background: int
        :param fontdescr: string describing the font to use
        :param grad_start: colors to use for background procedure
        :param grad_end: colors to use for background procedure
        :param filter: the person filter to apply to the people in the chart
        :param alpha_filter: the alpha transparency value (0-1) to apply to
                             filtered out data
        :param form: the ``FORM_`` constant for the fanchart
        :param angle_algo: alorithm to use to calculate the sizes of the boxes
        :param dupcolor: color to use for people or families that occur a second
                         or more time
        """
        self.rootpersonh = root_person_handle
        self.generations = maxgen
        self.background = background
        self.fontdescr = fontdescr
        self.grad_start = grad_start
        self.grad_end = grad_end
        self.filter = filter
        self.alpha_filter = alpha_filter
        self.form = form
        self.anglealgo = angle_algo
        self.dupcolor = hex_to_rgb(dupcolor)
        self.childring = False

    def gen_pixels(self):
        """
        how many pixels a generation takes up in the fanchart
        """
        return PIXELS_PER_GENPERSON + PIXELS_PER_GENFAMILY

    def set_generations(self):
        """
        Set the generations to max, and fill data structures with initial data.
        """
        self.handle2desc = {}
        self.famhandle2desc = {}
        self.handle2fam = {}
        self.gen2people = {}
        self.gen2fam = {}
        self.parentsroot = []
        self.gen2people[0] = [(None, False, 0, 2*pi, '', 0, 0, [], NORMAL)] #no center person
        self.gen2fam[0] = [] #no families
        self.angle = {}
        self.angle[-2] = []
        for i in range(1, self.generations+1):
            self.gen2fam[i] = []
            self.gen2people[i] = []
        self.gen2people[self.generations] = [] #indication of more children
        self.rotfactor = 1
        self.rotstartangle = 0
        if self.form == FORM_HALFCIRCLE:
            self.rotfactor = 1/2
            self.rotangle = 90
        elif self.form == FORM_QUADRANT:
            self.rotangle = 180
            self.rotfactor = 1/4

    def _fill_data_structures(self):
        self.set_generations()
        if not self.rootpersonh:
            return
        person = self.dbstate.db.get_person_from_handle(self.rootpersonh)
        if not person:
            #nothing to do, just return
            return
        else:
            name = name_displayer.display(person)

        # person, duplicate or not, start angle, slice size,
        #                   text, parent pos in fam, nrfam, userdata, status
        self.gen2people[0] = [[person, False, 0, 2*pi, name, 0, 0, [], NORMAL]]
        self.handle2desc[self.rootpersonh] = 0
        # fill in data for the parents
        self.parentsroot = []
        handleparents = []
        family_handle_list = person.get_parent_family_handle_list()
        if family_handle_list:
            for family_handle in family_handle_list:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if not family:
                    continue
                hfather = family.get_father_handle()
                if hfather and hfather not in handleparents:
                    father = self.dbstate.db.get_person_from_handle(hfather)
                    if father:
                        self.parentsroot.append((father, []))
                        handleparents.append(hfather)
                hmother = family.get_mother_handle()
                if hmother and hmother not in handleparents:
                    mother = self.dbstate.db.get_person_from_handle(hmother)
                    if mother:
                        self.parentsroot.append((mother, []))
                        handleparents.append(hmother)

        #recursively fill in the datastructures:
        nrdesc = self.__rec_fill_data(0, person, 0)
        self.handle2desc[person.handle] += nrdesc
        self.__compute_angles()

    def __rec_fill_data(self, gen, person, pos):
        """
        Recursively fill in the data
        """
        totdesc = 0
        nrfam = len(person.get_family_handle_list())
        self.gen2people[gen][pos][6] = nrfam
        for family_handle in person.get_family_handle_list():
            totdescfam = 0
            family = self.dbstate.db.get_family_from_handle(family_handle)

            spouse_handle = find_spouse(person, family)
            if spouse_handle:
                spouse = self.dbstate.db.get_person_from_handle(spouse_handle)
                spname = name_displayer.display(spouse)
            else:
                spname = ''
                spouse = None
            if family_handle in self.famhandle2desc:
                #family occurs via father and via mother in the chart, only
                #first to show and count.
                famdup = True
            else:
                famdup = False
            # family, duplicate or not, start angle, slice size,
            #   text, spouse pos in gen, nrchildren, userdata, parnter, status
            self.gen2fam[gen].append([family, famdup, 0, 0, spname, pos, 0, [],
                                      spouse, NORMAL])
            posfam = len(self.gen2fam[gen]) - 1

            if not famdup:
                nrchild = len(family.get_child_ref_list())
                self.gen2fam[gen][-1][6] = nrchild
                for child_ref in family.get_child_ref_list():
                    child = self.dbstate.db.get_person_from_handle(child_ref.ref)
                    chname = name_displayer.display(child)
                    if child_ref.ref in self.handle2desc:
                        dup = True
                    else:
                        dup = False
                        self.handle2desc[child_ref.ref] = 0
                    # person, duplicate or not, start angle, slice size,
                    #         text, parent pos in fam, nrfam, userdata, status
                    self.gen2people[gen+1].append([child, dup, 0, 0, chname,
                            posfam, 0, [], NORMAL])
                    totdescfam += 1 #add this person as descendant
                    pospers = len(self.gen2people[gen+1]) - 1
                    if not dup and not(self.generations == gen+2):
                        nrdesc = self.__rec_fill_data(gen+1, child, pospers)
                        self.handle2desc[child_ref.ref] += nrdesc
                        totdescfam += nrdesc # add children of him as descendants
                self.famhandle2desc[family_handle] = totdescfam
            totdesc += totdescfam
        return totdesc

    def __compute_angles(self):
        """
        Compute the angles of the boxes
        """
        #first we compute the size of the slice.
        nrgen = self.nrgen()
        #set angles root person
        if self.form == FORM_CIRCLE:
            slice = 2*pi
            start = 0.
        elif self.form == FORM_HALFCIRCLE:
            slice = pi
            start = pi/2
        elif self.form == FORM_QUADRANT:
            slice = pi/2
            start = pi
        gen = 0
        data = self.gen2people[gen][0]
        data[2] = start
        data[3] = slice
        for gen in range(1, nrgen):
            nrpeople = len(self.gen2people[gen])
            prevpartnerdatahandle = None
            offset = 0
            for data in self.gen2fam[gen-1]:
                #obtain start and stop of partner
                partnerdata = self.gen2people[gen-1][data[5]]
                dupfam = data[1]
                if dupfam:
                    # we don't show the descendants here, but in the first
                    # occurrence of the family
                    nrdescfam = 0
                    nrdescpartner = self.handle2desc[partnerdata[0].handle]
                    nrfam = partnerdata[6]
                    nrdescfam = 0
                else:
                    nrdescfam = self.famhandle2desc[data[0].handle]
                    nrdescpartner = self.handle2desc[partnerdata[0].handle]
                    nrfam = partnerdata[6]
                partstart = partnerdata[2]
                partslice = partnerdata[3]
                if prevpartnerdatahandle != partnerdata[0].handle:
                    #reset the offset
                    offset = 0
                    prevpartnerdatahandle = partnerdata[0].handle
                slice = partslice/(nrdescpartner+nrfam)*(nrdescfam+1)
                if data[9] == COLLAPSED:
                    slice = 0
                elif data[9] == EXPANDED:
                    slice = partslice

                data[2] = partstart + offset
                data[3] = slice
                offset += slice

##                if nrdescpartner == 0:
##                    #no offspring, draw as large as fraction of
##                    #nr families
##                    nrfam = partnerdata[6]
##                    slice = partslice/nrfam
##                    data[2] = partstart + offset
##                    data[3] = slice
##                    offset += slice
##                elif nrdescfam == 0:
##                    #no offspring this family, but there is another
##                    #family. We draw this as a weight of 1
##                    nrfam = partnerdata[6]
##                    slice = partslice/(nrdescpartner + nrfam - 1)*(nrdescfam+1)
##                    data[2] = partstart + offset
##                    data[3] = slice
##                    offset += slice
##                else:
##                    #this family has offspring. We give it space for it's
##                    #weight in offspring
##                    nrfam = partnerdata[6]
##                    slice = partslice/(nrdescpartner + nrfam - 1)*(nrdescfam+1)
##                    data[2] = partstart + offset
##                    data[3] = slice
##                    offset += slice

            prevfamdatahandle = None
            offset = 0
            for data in self.gen2people[gen]:
                #obtain start and stop of family this is child of
                parentfamdata = self.gen2fam[gen-1][data[5]]
                nrdescfam = 0
                if not parentfamdata[1]:
                    nrdescfam = self.famhandle2desc[parentfamdata[0].handle]
                nrdesc = 0
                if not data[1]:
                    nrdesc = self.handle2desc[data[0].handle]
                famstart = parentfamdata[2]
                famslice = parentfamdata[3]
                nrchild = parentfamdata[6]
                #now we divide this slice to the weight of children,
                #adding one for every child
                if self.anglealgo == ANGLE_CHEQUI:
                    slice = famslice / nrchild
                elif self.anglealgo == ANGLE_WEIGHT:
                    slice = famslice/(nrdescfam) * (nrdesc + 1)
                else:
                    raise NotImplementedError('Unknown angle algorithm %d' % self.anglealgo)
                if prevfamdatahandle != parentfamdata[0].handle:
                    #reset the offset
                    offset = 0
                    prevfamdatahandle = parentfamdata[0].handle
                if data[8] == COLLAPSED:
                    slice = 0
                elif data[8] == EXPANDED:
                    slice = famslice
                data[2] = famstart + offset
                data[3] = slice
                offset += slice

    def nrgen(self):
        #compute the number of generations present
        nrgen = None
        for gen in range(self.generations - 1, 0, -1):
            if len(self.gen2people[gen]) > 0:
                nrgen = gen + 1
                break
        if nrgen is None:
            nrgen = 1
        return nrgen

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        nrgen = self.nrgen()
        ringpxs = (PIXELS_PER_GENPERSON + PIXELS_PER_GENFAMILY) * (nrgen - 1)
        return ringpxs + self.CENTER + BORDER_EDGE_WIDTH

    def people_generator(self):
        """
        a generator over all people outside of the core person
        """
        for generation in range(self.generations):
            for data in self.gen2people[generation]:
                yield (data[0], data[7])
        for generation in range(self.generations-1):
            for data in self.gen2fam[generation]:
                yield (data[8], data[7])

    def innerpeople_generator(self):
        """
        a generator over all people inside of the core person
        """
        for parentdata in self.parentsroot:
            parent, userdata = parentdata
            yield (parent, userdata)

    def on_draw(self, widget, cr, scale=1.):
        """
        The main method to do the drawing.
        If widget is given, we assume we draw in GTK3 and use the allocation.
        To draw raw on the cairo context cr, set widget=None.
        """
        # first do size request of what we will need
        halfdist = self.halfdist()
        if widget:
            if self.form == FORM_CIRCLE:
                self.set_size_request(2 * halfdist, 2 * halfdist)
            elif self.form == FORM_HALFCIRCLE:
                self.set_size_request(2 * halfdist, halfdist + self.CENTER
                                      + PAD_PX)
            elif self.form == FORM_QUADRANT:
                self.set_size_request(halfdist + self.CENTER + PAD_PX,
                                      halfdist + self.CENTER + PAD_PX)

            #obtain the allocation
            alloc = self.get_allocation()
            x, y, w, h = alloc.x, alloc.y, alloc.width, alloc.height

        cr.scale(scale, scale)
        # when printing, we need not recalculate
        if widget:
            if self.form == FORM_CIRCLE:
                self.center_x = w/2 - self.center_xy[0]
                self.center_y = h/2 - self.center_xy[1]
            elif self.form == FORM_HALFCIRCLE:
                self.center_x = w/2. - self.center_xy[0]
                self.center_y = h - self.CENTER - PAD_PX- self.center_xy[1]
            elif self.form == FORM_QUADRANT:
                self.center_x = self.CENTER + PAD_PX - self.center_xy[0]
                self.center_y = h - self.CENTER - PAD_PX - self.center_xy[1]
        cr.translate(self.center_x, self.center_y)

        cr.save()
        #draw center
        cr.set_source_rgb(1, 1, 1) # white
        cr.move_to(0,0)
        cr.arc(0, 0, self.CENTER-PIXELS_PER_GENFAMILY, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgb(0, 0, 0) # black
        cr.arc(0, 0, self.CENTER-PIXELS_PER_GENFAMILY, 0, 2 * math.pi)
        cr.stroke()
        cr.restore()
        # Draw center person:
        (person, dup, start, slice, text, parentfampos, nrfam, userdata, status) \
                = self.gen2people[0][0]
        if person:
            r, g, b, a = self.background_box(person, 0, userdata)
            cr.arc(0, 0, self.CENTER-PIXELS_PER_GENFAMILY, 0, 2 * math.pi)
            if self.parentsroot:
                cr.arc_negative(0, 0, TRANSLATE_PX + CHILDRING_WIDTH,
                                2 * math.pi, 0)
                cr.close_path()
            cr.set_source_rgba(r/255, g/255, b/255, a)
            cr.fill()
            cr.save()
            name = name_displayer.display(person)
            self.draw_text(cr, name, self.CENTER - PIXELS_PER_GENFAMILY
                        - (self.CENTER - PIXELS_PER_GENFAMILY
                           - (CHILDRING_WIDTH + TRANSLATE_PX))/2,
                        95, 455, 10, False,
                        self.fontcolor(r, g, b, a), self.fontbold(a))
            cr.restore()
            #draw center to move chart
            cr.set_source_rgb(0, 0, 0) # black
            cr.move_to(TRANSLATE_PX, 0)
            cr.arc(0, 0, TRANSLATE_PX, 0, 2 * math.pi)
            if self.parentsroot: # has at least one parent
                cr.fill()
                self.draw_parentring(cr)
            else:
                cr.stroke()
        #now write all the families and children
        cr.save()
        cr.rotate(self.rotate_value * math.pi/180)
        radstart = self.CENTER - PIXELS_PER_GENFAMILY - PIXELS_PER_GENPERSON
        for gen in range(self.generations-1):
            radstart += PIXELS_PER_GENPERSON
            for famdata in self.gen2fam[gen]:
                # family, duplicate or not, start angle, slice size,
                #       text, spouse pos in gen, nrchildren, userdata, status
                fam, dup, start, slice, text, posfam, nrchild, userdata,\
                    partner, status = famdata
                if status != COLLAPSED:
                    self.draw_person(cr, text, start, slice, radstart,
                                     radstart + PIXELS_PER_GENFAMILY, gen, dup,
                                     partner, userdata, family=True, thick=status != NORMAL)
            radstart += PIXELS_PER_GENFAMILY
            for pdata in self.gen2people[gen+1]:
                # person, duplicate or not, start angle, slice size,
                #             text, parent pos in fam, nrfam, userdata, status
                pers, dup, start, slice, text, pospar, nrfam, userdata, status = \
                    pdata
                if status != COLLAPSED:
                    self.draw_person(cr, text, start, slice, radstart,
                                     radstart + PIXELS_PER_GENPERSON, gen+1, dup,
                                     pers, userdata, thick=status != NORMAL)
        cr.restore()

        if self.background in [BACKGROUND_GRAD_AGE, BACKGROUND_GRAD_PERIOD]:
            self.draw_gradient(cr, widget, halfdist)

    def draw_person(self, cr, name, start_rad, slice, radius, radiusend,
                generation, dup, person, userdata, family=False, thick=False):
        """
        Display the piece of pie for a given person. start_rad and slice
        are in radial.
        """
        if slice == 0:
            return
        cr.save()
        full = False
        if abs(slice - 2*pi) < 1e-6:
            full = True
        stop_rad = start_rad + slice
        if not person:
            #an family with partner not set. Don't have a color for this,
            # let's make it transparent
            r, g, b, a = (255, 255, 255, 0)
        elif not dup:
            r, g, b, a = self.background_box(person, generation, userdata)
        else:
            #duplicate color
            a = 1
            r, g, b = self.dupcolor #(136, 138, 133)
        # If max generation, and they have children:
        if (not family and generation == self.generations - 1
                and self._have_children(person)):
            # draw an indicator
            radmax = radiusend + BORDER_EDGE_WIDTH
            cr.move_to(radmax*math.cos(start_rad), radmax*math.sin(start_rad))
            cr.arc(0, 0, radmax, start_rad, stop_rad)
            cr.line_to(radiusend*math.cos(stop_rad), radiusend*math.sin(stop_rad))
            cr.arc_negative(0, 0, radiusend, stop_rad, start_rad)
            cr.close_path()
            ##path = cr.copy_path() # not working correct
            cr.set_source_rgb(1, 1, 1) # white
            cr.fill()
            #and again for the border
            cr.move_to(radmax*math.cos(start_rad), radmax*math.sin(start_rad))
            cr.arc(0, 0, radmax, start_rad, stop_rad)
            cr.line_to(radiusend*math.cos(stop_rad), radiusend*math.sin(stop_rad))
            cr.arc_negative(0, 0, radiusend, stop_rad, start_rad)
            cr.close_path()
            ##cr.append_path(path) # not working correct
            cr.set_source_rgb(0, 0, 0) # black
            cr.stroke()
        # now draw the person
        self.draw_radbox(cr, radius, radiusend, start_rad, stop_rad,
                         (r/255, g/255, b/255, a), thick)
        if self.last_x is None or self.last_y is None:
            #we are not in a move, so draw text
            radial = False
            width = radiusend-radius
            radstart = radius + width/2
            spacepolartext = radstart * (stop_rad-start_rad)
            if spacepolartext < width * 1.1:
                # more space to print it radial
                radial = True
                radstart = radius
            self.draw_text(cr, name, radstart, start_rad/ math.pi*180,
                           stop_rad/ math.pi*180, width, radial,
                           self.fontcolor(r, g, b, a), self.fontbold(a))
        cr.restore()

    def boxtype(self, radius):
        """
        default is only one type of box type
        """
        if radius <= self.CENTER:
            if radius >= self.CENTER - PIXELS_PER_GENFAMILY:
                return TYPE_BOX_FAMILY
            else:
                return TYPE_BOX_NORMAL
        else:
            gen = int((radius - self.CENTER)/self.gen_pixels()) + 1
            radius = (radius - self.CENTER) % PIXELS_PER_GENERATION
            if radius >= PIXELS_PER_GENPERSON:
                if gen < self.generations - 1:
                    return TYPE_BOX_FAMILY
                else:
                    # the last generation has no family boxes
                    None
            else:
                return TYPE_BOX_NORMAL

    def draw_parentring(self, cr):
        cr.move_to(TRANSLATE_PX + CHILDRING_WIDTH, 0)
        cr.set_source_rgb(0, 0, 0) # black
        cr.set_line_width(1)
        cr.arc(0, 0, TRANSLATE_PX + CHILDRING_WIDTH, 0, 2 * math.pi)
        cr.stroke()
        nrparent = len(self.parentsroot)
        #Y axis is downward. positve angles are hence clockwise
        startangle = math.pi
        if nrparent <= 2:
            angleinc = math.pi
        elif nrparent <= 4:
            angleinc = math.pi/2
        else:
            angleinc = 2 * math.pi / nrchild
        for data in self.parentsroot:
            self.draw_innerring(cr, data[0], data[1], startangle, angleinc)
            startangle += angleinc

    def personpos_at_angle(self, generation, angledeg, btype):
        """
        returns the person in generation generation at angle.
        """
        angle = angledeg / 360 * 2 * pi
        selected = None
        if btype == TYPE_BOX_NORMAL:
            for p, pdata in enumerate(self.gen2people[generation]):
                # person, duplicate or not, start angle, slice size,
                #             text, parent pos in fam, nrfam, userdata, status
                start = pdata[2]
                stop = start + pdata[3]
                if start <= angle <= stop:
                    selected = p
                    break
        elif btype == TYPE_BOX_FAMILY:
            for p, pdata in enumerate(self.gen2fam[generation]):
                # person, duplicate or not, start angle, slice size,
                #             text, parent pos in fam, nrfam, userdata, status
                start = pdata[2]
                stop = start + pdata[3]
                if start <= angle <= stop:
                    selected = p
                    break
        return selected

    def person_at(self, generation, pos, btype):
        """
        returns the person at generation, pos, btype
        """
        if pos is None:
            return None
        if generation == -2:
            person, userdata = self.parentsroot[pos]
        elif btype == TYPE_BOX_NORMAL:
            # person, duplicate or not, start angle, slice size,
            #                   text, parent pos in fam, nrfam, userdata, status
            person = self.gen2people[generation][pos][0]
        elif btype == TYPE_BOX_FAMILY:
            # family, duplicate or not, start angle, slice size,
            #       text, spouse pos in gen, nrchildren, userdata, person, status
            person = self.gen2fam[generation][pos][8]
        return person

    def family_at(self, generation, pos, btype):
        """
        returns the family at generation, pos, btype
        """
        if pos is None or btype == TYPE_BOX_NORMAL or generation < 0:
            return None
        return self.gen2fam[generation][pos][0]

    def do_mouse_click(self):
        # no drag occured, expand or collapse the section
        self.change_slice(self._mouse_click_gen, self._mouse_click_sel,
                          self._mouse_click_btype)
        self._mouse_click = False
        self.queue_draw()

    def change_slice(self, generation, selected, btype):
        if generation < 1:
            return
        if btype == TYPE_BOX_NORMAL:
            data = self.gen2people[generation][selected]
            parpos = data[5]
            status = data[8]
            if status == NORMAL:
                #should be expanded, rest collapsed
                for entry in self.gen2people[generation]:
                    if entry[5] == parpos:
                        entry[8] = COLLAPSED
                data[8] = EXPANDED
            else:
                #is expanded, set back to normal
                for entry in self.gen2people[generation]:
                    if entry[5] == parpos:
                        entry[8] = NORMAL
        if btype == TYPE_BOX_FAMILY:
            data = self.gen2fam[generation][selected]
            parpos = data[5]
            status = data[9]
            if status == NORMAL:
                #should be expanded, rest collapsed
                for entry in self.gen2fam[generation]:
                    if entry[5] == parpos:
                        entry[9] = COLLAPSED
                data[9] = EXPANDED
            else:
                #is expanded, set back to normal
                for entry in self.gen2fam[generation]:
                    if entry[5] == parpos:
                        entry[9] = NORMAL

        self.__compute_angles()

class FanChartDescGrampsGUI(FanChartGrampsGUI):
    """ class for functions fanchart GUI elements will need in Gramps
    """

    def main(self):
        """
        Fill the data structures with the active data. This initializes all
        data.
        """
        root_person_handle = self.get_active('Person')
        self.fan.set_values(root_person_handle, self.maxgen, self.background,
                        self.fonttype, self.grad_start, self.grad_end,
                        self.generic_filter, self.alpha_filter, self.form,
                        self.angle_algo, self.dupcolor)
        self.fan.reset()
        self.fan.queue_draw()
