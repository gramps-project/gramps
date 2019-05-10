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
import math
import cairo

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug.report.utils import find_spouse
from ..utils import hex_to_rgb
from .fanchart import (FanChartBaseWidget, FanChartGrampsGUI,
                       PAD_PX, TRANSLATE_PX,
                       FORM_CIRCLE, FORM_HALFCIRCLE, FORM_QUADRANT,
                       NORMAL, EXPANDED, COLLAPSED,
                       BACKGROUND_GRAD_GEN, BACKGROUND_GRAD_AGE,
                       BACKGROUND_GRAD_PERIOD, CHILDRING_WIDTH)

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

PIXELS_PER_GENPERSON_RATIO = 0.55 # ratio of generation radius for person
                                  # (rest for partner)
PIXELS_PER_GEN_SMALL = 80
PIXELS_PER_GEN_LARGE = 160
N_GEN_SMALL = 4
PIXELS_PER_GENFAMILY = 25 # size of radius for family
PIXELS_PER_RECLAIM = 4 # size of the radius of pixels taken from family
                       # to reclaim space
PIXELS_PARTNER_GAP = 0 # Padding between someone and his partner
PIXELS_CHILDREN_GAP = 5 # Padding between generations
PARENTRING_WIDTH = 12  # width of the parent ring inside the person

ANGLE_CHEQUI = 0   #Algorithm with homogeneous children distribution
ANGLE_WEIGHT = 1   #Algorithm for angle computation based on nr of descendants

TYPE_BOX_NORMAL = 0
TYPE_BOX_FAMILY = 1

#-------------------------------------------------------------------------
#
# FanChartDescWidget
#
#-------------------------------------------------------------------------

class FanChartDescWidget(FanChartBaseWidget):
    """
    Interactive Fan Chart Widget.
    """
    CENTER = 60 # we require a larger center as CENTER includes the 1st partner

    def __init__(self, dbstate, uistate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        self.gen2people = {}
        self.gen2fam = {}
        self.rootangle_rad = []
        self.handle2desc = {}
        self.famhandle2desc = {}
        self.handle2fam = {}
        self.innerring = []
        self.angle = {}
        self.set_values(None, 9, True, True, BACKGROUND_GRAD_GEN, 'Sans',
                        '#0000FF', '#FF0000', None, 0.5,
                        FORM_CIRCLE, ANGLE_WEIGHT, '#888a85', False)
        FanChartBaseWidget.__init__(self, dbstate, uistate, callback_popup)

    def set_values(self, root_person_handle, maxgen, flipupsidedownname,
                   twolinename, background, fontdescr, grad_start, grad_end,
                   filtr, alpha_filter, form, angle_algo, dupcolor, showid):
        """
        Reset the values to be used:

        :param root_person_handle: person to show
        :param maxgen: maximum generations to show
        :param flipupsidedownname: flip name on the left of the fanchart
                                   for the display of person's name
        :param background: config setting of which background procedure to use
        :type background: int
        :param fontdescr: string describing the font to use
        :param grad_start: colors to use for background procedure
        :param grad_end: colors to use for background procedure
        :param filtr: the person filter to apply to the people in the chart
        :param alpha_filter: the alpha transparency value (0-1) to apply to
                             filtered out data
        :param form: the ``FORM_`` constant for the fanchart
        :param angle_algo: alorithm to use to calculate the sizes of the boxes
        :param dupcolor: color to use for people or families that occur a second
                         or more time
        :param showid: to show the gramps_id or not
        """
        self.rootpersonh = root_person_handle
        self.generations = maxgen
        self.background = background
        self.fontdescr = fontdescr
        self.grad_start = grad_start
        self.grad_end = grad_end
        self.filter = filtr
        self.alpha_filter = alpha_filter
        self.form = form
        self.anglealgo = angle_algo
        self.dupcolor = hex_to_rgb(dupcolor)
        self.childring = False
        self.flipupsidedownname = flipupsidedownname
        self.twolinename = twolinename
        self.showid = showid

    def set_generations(self):
        """
        Set the generations to max, and fill data structures with initial data.
        """

        if self.form == FORM_CIRCLE:
            self.rootangle_rad = [math.radians(0), math.radians(360)]
        elif self.form == FORM_HALFCIRCLE:
            self.rootangle_rad = [math.radians(90), math.radians(90 + 180)]
        elif self.form == FORM_QUADRANT:
            self.rootangle_rad = [math.radians(180), math.radians(270)]

        self.handle2desc = {}
        self.famhandle2desc = {}
        self.handle2fam = {}
        self.gen2people = {}
        self.gen2fam = {}
        self.innerring = []
        self.gen2people[0] = [(None, False, 0, 2*math.pi, 0, 0,
                               [], NORMAL)] #no center person
        self.gen2fam[0] = [] #no families
        self.angle = {}
        self.angle[-2] = []
        for i in range(1, self.generations+1):
            self.gen2fam[i] = []
            self.gen2people[i] = []
        self.gen2people[self.generations] = [] #indication of more children

    def _fill_data_structures(self):
        self.set_generations()
        if not self.rootpersonh:
            return
        person = self.dbstate.db.get_person_from_handle(self.rootpersonh)
        if not person:
            #nothing to do, just return
            return

        # person, duplicate or not, start angle, slice size,
        #                   text, parent pos in fam, nrfam, userdata, status
        self.gen2people[0] = [[person, False, 0, 2*math.pi, 0, 0, [], NORMAL]]
        self.handle2desc[self.rootpersonh] = 0
        # fill in data for the parents
        self.innerring = []
        handleparents = []
        family_handle_list = person.get_parent_family_handle_list()
        if family_handle_list:
            for family_handle in family_handle_list:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if not family:
                    continue
                for hparent in [family.get_father_handle(),
                                family.get_mother_handle()]:
                    if hparent and hparent not in handleparents:
                        parent = self.dbstate.db.get_person_from_handle(hparent)
                        if parent:
                            self.innerring.append((parent, []))
                            handleparents.append(hparent)

        #recursively fill in the datastructures:
        nrdesc = self._rec_fill_data(0, person, 0, self.generations)
        self.handle2desc[person.handle] += nrdesc
        self._compute_angles(*self.rootangle_rad)

    def _rec_fill_data(self, gen, person, pos, maxgen):
        """
        Recursively fill in the data
        """
        totdesc = 0
        marriage_handle_list = person.get_family_handle_list()
        self.gen2people[gen][pos][5] = len(marriage_handle_list)
        for family_handle in marriage_handle_list:
            totdescfam = 0
            family = self.dbstate.db.get_family_from_handle(family_handle)

            spouse_handle = find_spouse(person, family)
            if spouse_handle:
                spouse = self.dbstate.db.get_person_from_handle(spouse_handle)
            else:
                spouse = None
            # family may occur via father and via mother in the chart, only
            # first to show and count.
            fam_duplicate = family_handle in self.famhandle2desc
            # family, duplicate or not, start angle, slice size,
            #   spouse pos in gen, nrchildren, userdata, parnter, status
            self.gen2fam[gen].append([family, fam_duplicate, 0, 0,
                                      pos, 0, [], spouse, NORMAL])
            posfam = len(self.gen2fam[gen]) - 1

            if not fam_duplicate and gen < maxgen-1:
                nrchild = len(family.get_child_ref_list())
                self.gen2fam[gen][posfam][5] = nrchild
                for child_ref in family.get_child_ref_list():
                    chld = self.dbstate.db.get_person_from_handle(child_ref.ref)
                    child_dup = child_ref.ref in self.handle2desc
                    if not child_dup:
                        # mark this child as processed
                        self.handle2desc[child_ref.ref] = 0
                    # person, duplicate or not, start angle, slice size,
                    #         parent pos in fam, nrfam, userdata, status
                    self.gen2people[gen+1].append([chld, child_dup, 0, 0,
                                                   posfam, 0, [], NORMAL])
                    totdescfam += 1 #add this person as descendant
                    pospers = len(self.gen2people[gen + 1]) - 1
                    if not child_dup:
                        nrdesc = self._rec_fill_data(gen + 1, chld,
                                                     pospers, maxgen)
                        self.handle2desc[child_ref.ref] += nrdesc
                        # add children of him as descendants
                        totdescfam += nrdesc
            if not fam_duplicate:
                self.famhandle2desc[family_handle] = totdescfam
            totdesc += totdescfam
        return totdesc

    def _compute_angles(self, start_rad, stop_rad):
        """
        Compute the angles of the boxes
        """
        #first we compute the size of the slice.
        #set angles root person
        start, portion = start_rad, stop_rad - start_rad
        nr_gen = len(self.gen2people)-1
        # Fill in central person angles
        gen = 0
        data = self.gen2people[gen][0]
        data[2] = start
        data[3] = portion
        for gen in range(0, nr_gen):
            prevpartnerdatahandle = None
            offset = 0
            for data_fam in self.gen2fam[gen]:  # for each partner/fam of gen-1
                #obtain start and stop from the people of this partner
                persondata = self.gen2people[gen][data_fam[4]]
                dupfam = data_fam[1]
                if dupfam:
                    # we don't show again the descendants here
                    nrdescfam = 0
                else:
                    nrdescfam = self.famhandle2desc[data_fam[0].handle]
                nrdescperson = self.handle2desc[persondata[0].handle]
                nrfam = persondata[5]
                personstart, personslice = persondata[2:4]
                if prevpartnerdatahandle != persondata[0].handle:
                    #partner of a new person: reset the offset
                    offset = 0
                    prevpartnerdatahandle = persondata[0].handle
                portion = personslice/(nrdescperson+nrfam)*(nrdescfam+1)
                if data_fam[8] == COLLAPSED:
                    portion = 0
                elif data_fam[8] == EXPANDED:
                    portion = personslice

                data_fam[2] = personstart + offset
                data_fam[3] = portion
                offset += portion

##                if nrdescperson == 0:
##                    #no offspring, draw as large as fraction of
##                    #nr families
##                    nrfam = persondata[6]
##                    portion = personslice/nrfam
##                    data_fam[2] = personstart + offset
##                    data_fam[3] = portion
##                    offset += portion
##                elif nrdescfam == 0:
##                    #no offspring this family, but there is another
##                    #family. We draw this as a weight of 1
##                    nrfam = persondata[6]
##                    portion = (personslice/(nrdescperson + nrfam - 1) *
##                               (nrdescfam + 1))
##                    data_fam[2] = personstart + offset
##                    data_fam[3] = portion
##                    offset += portion
##                else:
##                    #this family has offspring. We give it space for it's
##                    #weight in offspring
##                    nrfam = persondata[6]
##                    portion = (personslice/(nrdescperson + nrfam - 1) *
##                               (nrdescfam + 1))
##                    data_fam[2] = personstart + offset
##                    data_fam[3] = portion
##                    offset += portion

            prevfamdatahandle = None
            offset = 0
            for persondata in self.gen2people[gen+1] if gen < nr_gen else []:
                #obtain start and stop of family this is child of
                parentfamdata = self.gen2fam[gen][persondata[4]]
                nrdescfam = 0
                if not parentfamdata[1]:
                    nrdescfam = self.famhandle2desc[parentfamdata[0].handle]
                nrdesc = 0
                if not persondata[1]:
                    nrdesc = self.handle2desc[persondata[0].handle]
                famstart = parentfamdata[2]
                famslice = parentfamdata[3]
                nrchild = parentfamdata[5]
                #now we divide this slice to the weight of children,
                #adding one for every child
                if self.anglealgo == ANGLE_CHEQUI:
                    portion = famslice / nrchild
                elif self.anglealgo == ANGLE_WEIGHT:
                    portion = famslice/(nrdescfam) * (nrdesc + 1)
                else:
                    raise NotImplementedError('Unknown angle algorithm %d' %
                                              self.anglealgo)
                if prevfamdatahandle != parentfamdata[0].handle:
                    #reset the offset
                    offset = 0
                    prevfamdatahandle = parentfamdata[0].handle
                if persondata[7] == COLLAPSED:
                    portion = 0
                elif persondata[7] == EXPANDED:
                    portion = famslice
                persondata[2] = famstart + offset
                persondata[3] = portion
                offset += portion

    def nrgen(self):
        """
        compute the number of generations present
        """
        for gen in range(self.generations - 1, 0, -1):
            if self.gen2people[gen]:
                return gen + 1
        return 1

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        return self.get_radiusinout_for_generation(self.nrgen())[1]

    def get_radiusinout_for_generation(self, generation):
        """
        Get the in and out radius for the generation
        """
        radius_first_gen = 14  # fudged to make inner circle a bit tighter
        if generation < N_GEN_SMALL:
            radius_start = PIXELS_PER_GEN_SMALL * generation + radius_first_gen
            return (radius_start, radius_start + PIXELS_PER_GEN_SMALL)
        else:
            radius_start = (PIXELS_PER_GEN_SMALL * N_GEN_SMALL +
                            PIXELS_PER_GEN_LARGE * (generation - N_GEN_SMALL)
                            + radius_first_gen)
            return (radius_start, radius_start + PIXELS_PER_GEN_LARGE)

    def get_radiusinout_for_gen_pair(self, generation):
        """
        Get the in and out radius for the father and mother
        """
        radiusin, radiusout = self.get_radiusinout_for_generation(generation)
        radius_spread = (radiusout - radiusin -
                         PIXELS_CHILDREN_GAP - PIXELS_PARTNER_GAP)

        radiusin_pers = radiusin + PIXELS_CHILDREN_GAP
        radiusout_pers = (radiusin_pers +
                          PIXELS_PER_GENPERSON_RATIO * radius_spread)
        radiusin_partner = radiusout_pers + PIXELS_PARTNER_GAP
        radiusout_partner = radiusout
        return (radiusin_pers, radiusout_pers,
                radiusin_partner, radiusout_partner)

    def people_generator(self):
        """
        a generator over all people outside of the core person
        """
        for generation in range(self.generations):
            for data in self.gen2people[generation]:
                yield (data[0], data[6])
        for generation in range(self.generations):
            for data in self.gen2fam[generation]:
                yield (data[7], data[6])

    def innerpeople_generator(self):
        """
        a generator over all people inside of the core person
        """
        for parentdata in self.innerring:
            parent, userdata = parentdata
            yield (parent, userdata)

    def draw(self, ctx=None, scale=1.0):
        """
        The main method to do the drawing.
        If ctx is given, we assume we draw draw raw on the cairo context ctx
        To draw in GTK3 and use the allocation, set ctx=None.
        Note: when drawing for display, to counter a Gtk issue with scrolling
        or resizing the drawing window, we draw on a surface, then copy to the
        drawing context when the Gtk 'draw' signal arrives.
        """
        # first do size request of what we will need
        halfdist = self.halfdist()
        if not ctx:  # Display
            if self.form == FORM_CIRCLE:
                size_w = size_h = 2 * halfdist
            elif self.form == FORM_HALFCIRCLE:
                size_w = 2 * halfdist
                size_h = halfdist + self.CENTER + PAD_PX
            elif self.form == FORM_QUADRANT:
                size_w = size_h = halfdist + self.CENTER + PAD_PX

            size_w_a = self.get_allocated_width()
            size_h_a = self.get_allocated_height()
            self.set_size_request(max(size_w, size_w_a), max(size_h, size_h_a))
            size_w = self.get_allocated_width()
            size_h = self.get_allocated_height()
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                              size_w, size_h)
            ctx = cairo.Context(self.surface)
            self.center_xy = self.center_xy_from_delta()
            ctx.translate(*self.center_xy)
        else:  # printing
            if self.form == FORM_QUADRANT:
                self.center_xy = self.CENTER, halfdist
            else:
                self.center_xy = halfdist, halfdist
            ctx.scale(scale, scale)
            ctx.translate(*self.center_xy)

        ctx.save()
        # Draw center person:
        (person, dup, start, portion, dummy_parentfampos, dummy_nrfam,
         userdata, status) = self.gen2people[0][0]
        if person:
            #r, g, b, a = self.background_box(person, 0, userdata)
            (radiusin_pers, radiusout_pers, radiusin_partner,
             radiusout_partner) = self.get_radiusinout_for_gen_pair(0)
            if not self.innerring:
                radiusin_pers = TRANSLATE_PX
            self.draw_person(ctx, person, radiusin_pers, radiusout_pers,
                             math.pi / 2, math.pi / 2 + 2 * math.pi,
                             0, False, userdata, is_central_person=True)
            #draw center to move chart
            ctx.set_source_rgb(0, 0, 0) # black
            ctx.move_to(TRANSLATE_PX, 0)
            ctx.arc(0, 0, TRANSLATE_PX, 0, 2 * math.pi)
            if self.innerring: # has at least one parent
                ctx.fill()
                self.draw_innerring_people(ctx)
            else:
                ctx.stroke()
        #now write all the families and children
        ctx.rotate(self.rotate_value * math.pi/180)
        for gen in range(self.generations):
            (radiusin_pers, radiusout_pers, radiusin_partner,
             radiusout_partner) = self.get_radiusinout_for_gen_pair(gen)
            if gen > 0:
                for pdata in self.gen2people[gen]:
                    # person, duplicate or not, start angle, slice size,
                    #             parent pos in fam, nrfam, userdata, status
                    (pers, dup, start, portion, dummy_pospar, dummy_nrfam,
                     userdata, status) = pdata
                    if status != COLLAPSED:
                        self.draw_person(ctx, pers, radiusin_pers,
                                         radiusout_pers, start, start + portion,
                                         gen, dup, userdata,
                                         thick=status != NORMAL)
            #if gen < self.generations-1:
            for famdata in self.gen2fam[gen]:
                # family, duplicate or not, start angle, slice size,
                #       spouse pos in gen, nrchildren, userdata, status
                (fam, dup, start, portion, dummy_posfam, dummy_nrchild,
                 userdata, partner, status) = famdata
                if status != COLLAPSED:
                    more_pers_flag = (gen == self.generations - 1
                                      and fam.get_child_ref_list())
                    self.draw_person(ctx, partner, radiusin_partner,
                                     radiusout_partner, start, start + portion,
                                     gen, dup, userdata,
                                     thick=(status != NORMAL),
                                     has_moregen_indicator=more_pers_flag)
        ctx.restore()

        if self.background in [BACKGROUND_GRAD_AGE, BACKGROUND_GRAD_PERIOD]:
            self.draw_gradient_legend(ctx, halfdist)

    def cell_address_under_cursor(self, curx, cury):
        """
        Determine the cell address in the fan under the cursor
        position x and y.
        None if outside of diagram
        """
        radius, rads, raw_rads = self.cursor_to_polar(curx, cury,
                                                      get_raw_rads=True)

        btype = TYPE_BOX_NORMAL
        if radius < TRANSLATE_PX:
            return None
        elif (self.innerring and self.angle[-2] and
              radius < CHILDRING_WIDTH + TRANSLATE_PX):
            generation = -2  # indication of one of the children
        elif radius < self.CENTER:
            generation = 0
        else:
            generation = None
            for gen in range(self.generations):
                (radiusin_pers, radiusout_pers, radiusin_partner,
                 radiusout_partner) = self.get_radiusinout_for_gen_pair(gen)
                if radiusin_pers <= radius <= radiusout_pers:
                    generation, btype = gen, TYPE_BOX_NORMAL
                    break
                if radiusin_partner <= radius <= radiusout_partner:
                    generation, btype = gen, TYPE_BOX_FAMILY
                    break

        # find what person is in this position:
        selected = None
        if not (generation is None) and generation > 0:
            selected = self.personpos_at_angle(generation, rads, btype)
        elif generation == -2:
            for idx in range(len(self.angle[generation])):
                start, stop, dummy_state = self.angle[generation][idx]
                if self.radian_in_bounds(start, raw_rads, stop):
                    selected = idx
                    break
        if (generation is None or selected is None):
            return None
        return generation, selected, btype

    def draw_innerring_people(self, ctx):
        """
        Draw the innerring person
        """
        ctx.move_to(TRANSLATE_PX + CHILDRING_WIDTH, 0)
        ctx.set_source_rgb(0, 0, 0) # black
        ctx.set_line_width(1)
        ctx.arc(0, 0, TRANSLATE_PX + CHILDRING_WIDTH, 0, 2 * math.pi)
        ctx.stroke()
        nrparent = len(self.innerring)
        #Y axis is downward. positve angles are hence clockwise
        startangle = math.pi
        if nrparent <= 2:
            angleinc = math.pi
        elif nrparent <= 4:
            angleinc = math.pi/2
        else:
            angleinc = 2 * math.pi / nrparent
        for data in self.innerring:
            self.draw_innerring(ctx, data[0], data[1], startangle, angleinc)
            startangle += angleinc

    def personpos_at_angle(self, generation, rads, btype):
        """
        returns the person in generation generation at angle.
        """
        selected = None
        datas = None
        if btype == TYPE_BOX_NORMAL:
            if generation == 0:
                return 0  # central person is always ok !
            datas = self.gen2people[generation]
        elif btype == TYPE_BOX_FAMILY:
            datas = self.gen2fam[generation]
        else:
            return None
        for idx, pdata in enumerate(datas):
            # person, duplicate or not, start angle, slice size,
            #             parent pos in fam, nrfam, userdata, status
            start, stop = pdata[2], pdata[2] + pdata[3]
            if self.radian_in_bounds(start, rads, stop):
                selected = idx
                break
        return selected

    def person_at(self, cell_address):
        """
        returns the person at generation, pos, btype
        """
        generation, pos, btype = cell_address
        if generation == -2:
            person, dummy_userdata = self.innerring[pos]
        elif btype == TYPE_BOX_NORMAL:
            # person, duplicate or not, start angle, slice size,
            #                   parent pos in fam, nrfam, userdata, status
            person = self.gen2people[generation][pos][0]
        elif btype == TYPE_BOX_FAMILY:
            # family, duplicate or not, start angle, slice size,
            #       spouse pos in gen, nrchildren, userdata, person, status
            person = self.gen2fam[generation][pos][7]
        return person

    def family_at(self, cell_address):
        """
        returns the family at generation, pos, btype
        """
        generation, pos, btype = cell_address
        if pos is None or btype == TYPE_BOX_NORMAL or generation < 0:
            return None
        return self.gen2fam[generation][pos][0]

    def do_mouse_click(self):
        """
        no drag occured, expand or collapse the section
        """
        self.toggle_cell_state(self._mouse_click_cell_address)
        self._compute_angles(*self.rootangle_rad)
        self._mouse_click = False
        self.draw()
        self.queue_draw()

    def toggle_cell_state(self, cell_address):
        """
        Toggle the person cell (EXPAND/COLLAPSE)
        """
        generation, selected, btype = cell_address
        if generation < 1:
            return
        if btype == TYPE_BOX_NORMAL:
            data = self.gen2people[generation][selected]
            parpos = data[4]
            status = data[7]
            if status == NORMAL:
                #should be expanded, rest collapsed
                for entry in self.gen2people[generation]:
                    if entry[4] == parpos:
                        entry[7] = COLLAPSED
                data[7] = EXPANDED
            else:
                #is expanded, set back to normal
                for entry in self.gen2people[generation]:
                    if entry[4] == parpos:
                        entry[7] = NORMAL
        if btype == TYPE_BOX_FAMILY:
            data = self.gen2fam[generation][selected]
            parpos = data[4]
            status = data[8]
            if status == NORMAL:
                #should be expanded, rest collapsed
                for entry in self.gen2fam[generation]:
                    if entry[4] == parpos:
                        entry[8] = COLLAPSED
                data[8] = EXPANDED
            else:
                #is expanded, set back to normal
                for entry in self.gen2fam[generation]:
                    if entry[4] == parpos:
                        entry[8] = NORMAL

class FanChartDescGrampsGUI(FanChartGrampsGUI):
    """ class for functions fanchart GUI elements will need in Gramps
    """

    def main(self):
        """
        Fill the data structures with the active data. This initializes all
        data.
        """
        root_person_handle = self.get_active('Person')
        self.fan.set_values(root_person_handle, self.maxgen,
                            self.flipupsidedownname, self.twolinename,
                            self.background, self.fonttype, self.grad_start,
                            self.grad_end, self.generic_filter,
                            self.alpha_filter, self.form, self.angle_algo,
                            self.dupcolor, self.showid)
        self.fan.reset()
        self.fan.draw()
        self.fan.queue_draw()
