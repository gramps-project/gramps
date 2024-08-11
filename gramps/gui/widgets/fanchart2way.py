#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2012 Benny Malengier
# Copyright (C) 2014 Bastien Jacquet
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import math
import cairo

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..utils import hex_to_rgb
from .fanchart import FanChartWidget, PIXELS_PER_GENERATION, BORDER_EDGE_WIDTH
from .fanchartdesc import (
    FanChartBaseWidget,
    FanChartDescWidget,
    FanChartGrampsGUI,
    NORMAL,
    EXPANDED,
    COLLAPSED,
    TRANSLATE_PX,
    CHILDRING_WIDTH,
    BACKGROUND_GRAD_GEN,
    BACKGROUND_GRAD_AGE,
    BACKGROUND_GRAD_PERIOD,
    FORM_CIRCLE,
    TYPE_BOX_NORMAL,
    TYPE_BOX_FAMILY,
)

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

PIXELS_PER_GENPERSON_RATIO = 0.55  # ratio of generation radius for person
# (rest for partner)
PIXELS_PER_GEN_SMALL = 80
PIXELS_PER_GEN_LARGE = 160
N_GEN_SMALL = 4
PIXELS_PER_GENFAMILY = 25  # size of radius for family
PIXELS_PER_RECLAIM = 4  # size of the radius of pixels taken from family
# to reclaim space
PIXELS_PARTNER_GAP = 0  # Padding between someone and his partner
PIXELS_CHILDREN_GAP = 5  # Padding between generations
PARENTRING_WIDTH = 12  # width of the parent ring inside the person

ANGLE_CHEQUI = 0  # Algorithm with homogeneous children distribution
ANGLE_WEIGHT = 1  # Algorithm for angle computation based on nr of descendants

TYPE_ASCENDANCE = 0
TYPE_DESCENDANCE = 1

# -------------------------------------------------------------------------
#
# FanChart2WayWidget
#
# -------------------------------------------------------------------------


class FanChart2WayWidget(FanChartWidget, FanChartDescWidget):
    """
    Interactive Fan Chart Widget.
    """

    CENTER = 50  # we require a larger center

    def __init__(self, dbstate, uistate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        self.gen2people = {}
        self.gen2fam = {}
        self.rootangle_rad_desc = [math.radians(275), math.radians(275 + 170)]
        self.rootangle_rad_asc = [math.radians(90), math.radians(270)]
        self.data = {}
        self.set_values(
            None,
            6,
            5,
            True,
            True,
            BACKGROUND_GRAD_GEN,
            True,
            "Sans",
            "#0000FF",
            "#FF0000",
            None,
            0.5,
            ANGLE_WEIGHT,
            "#888a85",
            False,
        )
        FanChartBaseWidget.__init__(self, dbstate, uistate, callback_popup)

    def reset(self):
        """
        Reset the fan chart. This should trigger computation of all data
        structures needed
        """
        self.cache_fontcolor = {}

        # fill the data structure
        self._fill_data_structures()

        # prepare the colors for the boxes
        self.prepare_background_box(self.generations_asc + self.generations_desc - 1)

    def set_values(
        self,
        root_person_handle,
        maxgen_asc,
        maxgen_desc,
        flipupsidedownname,
        twolinename,
        background,
        background_gradient,
        fontdescr,
        grad_start,
        grad_end,
        filtr,
        alpha_filter,
        angle_algo,
        dupcolor,
        showid,
    ):
        """
        Reset the values to be used:

        :param root_person_handle: person to show
        :param maxgen_asc: maximum of ascendant generations to show
        :param maxgen_desc: maximum of descendant generations to show
        :param flipupsidedownname: flip name on the left of the fanchart
                                   for the display of person's name
        :param background: config setting of which background procedure to use
        :type background: int
        :param background_gradient: option to add an overall gradient
                                    for distinguishing Asc/Desc
        :param fontdescr: string describing the font to use
        :param grad_start: colors to use for background procedure
        :param grad_end: colors to use for background procedure
        :param filtr: the person filter to apply to the people in the chart
        :param alpha_filter: the alpha transparency value (0-1) to apply to
                             filtered out data
        :param angle_algo: alorithm to use to calculate the sizes of the boxes
        :param dupcolor: color to use for people or families that occur a second
                         or more time
        :param showid: option to show the gramps id or not
        """
        self.rootpersonh = root_person_handle
        self.generations_asc = maxgen_asc
        self.generations_desc = maxgen_desc
        self.background = background
        self.background_gradient = background_gradient
        self.fontdescr = fontdescr
        self.grad_start = grad_start
        self.grad_end = grad_end
        self.filter = filtr
        self.form = FORM_CIRCLE
        self.alpha_filter = alpha_filter
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
        self.rootangle_rad_desc = [math.radians(275), math.radians(275 + 170)]
        self.rootangle_rad_asc = [math.radians(90), math.radians(270)]

        self.handle2desc = {}
        self.famhandle2desc = {}
        self.handle2fam = {}
        self.gen2people = {}
        self.gen2fam = {}
        # no center person
        self.gen2people[0] = [(None, False, 0, 2 * math.pi, 0, 0, [], NORMAL)]
        self.gen2fam[0] = []  # no families
        for i in range(1, self.generations_desc):
            self.gen2fam[i] = []
            self.gen2people[i] = []
        # indication of more children
        self.gen2people[self.generations_desc] = []

        # Ascendance part
        self.angle = {}
        self.data = {}
        for i in range(self.generations_asc):
            # name, person, parents?, children?
            self.data[i] = [(None,) * 4] * 2**i
            self.angle[i] = []
            angle = self.rootangle_rad_asc[0]
            portion = (
                1 / (2**i) * (self.rootangle_rad_asc[1] - self.rootangle_rad_asc[0])
            )
            for dummy_count in self.data[i]:
                # start, stop, state
                self.angle[i].append([angle, angle + portion, NORMAL])
                angle += portion

    def _fill_data_structures(self):
        """
        Initialize the data structures
        """
        self.set_generations()
        if not self.rootpersonh:
            return
        person = self.dbstate.db.get_person_from_handle(self.rootpersonh)
        if not person:
            # nothing to do, just return
            return

        # Descendance part
        # person, duplicate or not, start angle, slice size,
        #                   text, parent pos in fam, nrfam, userdata, status
        self.gen2people[0] = [[person, False, 0, 2 * math.pi, 0, 0, [], NORMAL]]
        self.handle2desc[self.rootpersonh] = 0
        # recursively fill in the datastructures:
        nrdesc = self._rec_fill_data(0, person, 0, self.generations_desc)
        self.handle2desc[person.handle] += nrdesc
        self._compute_angles(*self.rootangle_rad_desc)

        # Ascendance part
        parents = self._have_parents(person)
        child = self._have_children(person)
        # Ascendance data structure is the person object, parents, child and
        # list for userdata which we might fill in later.
        self.data[0][0] = (person, parents, child, [])
        for current in range(1, self.generations_asc):
            parent = 0
            # name, person, parents, children
            for pers, dummy_q, dummy_c, dummy_d in self.data[current - 1]:
                # Get father's and mother's details:
                for person in [
                    self._get_parent(pers, True),
                    self._get_parent(pers, False),
                ]:
                    if current == self.generations_asc - 1:
                        parents = self._have_parents(person)
                    else:
                        parents = None
                    self.data[current][parent] = (person, parents, None, [])
                    if person is None:
                        # start,stop,male/right,state
                        self.angle[current][parent][2] = COLLAPSED
                    parent += 1

    def nrgen_desc(self):
        """
        compute the number of generations present
        """
        for gen in range(self.generations_desc - 1, 0, -1):
            if self.gen2people[gen]:
                return gen + 1
        return 1

    def nrgen_asc(self):
        """
        compute the number of generations present
        """
        for generation in range(self.generations_asc - 1, 0, -1):
            for idx, (person, *rest) in enumerate(self.data[generation]):
                if person:
                    return generation
        return 1

    def maxradius_asc(self, generation):
        """
        Compute the current half radius of the ascendant circle
        """
        (dummy_radiusin, radius_asc) = self.get_radiusinout_for_gen_asc(generation)
        return radius_asc + BORDER_EDGE_WIDTH

    def maxradius_desc(self, generation):
        """
        Compute the current radius of the descendant circle
        """
        (
            dummy_radiusin_pers,
            dummy_radiusout_pers,
            dummy_radiusin_partner,
            radius_desc,
        ) = self.get_radiusinout_for_gen_pair(generation - 1)
        return radius_desc + BORDER_EDGE_WIDTH

    def halfdist(self):
        """
        Compute the current max half radius of the circle
        """
        return max(
            self.maxradius_desc(self.nrgen_desc()), self.maxradius_asc(self.nrgen_asc())
        )

    def get_radiusinout_for_gen_desc(self, generation):
        """
        Get the in and out radius for descendant generation
        (starting with center pers = 0)
        """
        radius_first_gen = (
            self.CENTER - (1 - PIXELS_PER_GENPERSON_RATIO) * PIXELS_PER_GEN_SMALL
        )
        if generation < N_GEN_SMALL:
            radius_start = PIXELS_PER_GEN_SMALL * generation + radius_first_gen
            return (radius_start, radius_start + PIXELS_PER_GEN_SMALL)
        else:
            radius_start = (
                PIXELS_PER_GEN_SMALL * N_GEN_SMALL
                + PIXELS_PER_GEN_LARGE * (generation - N_GEN_SMALL)
                + radius_first_gen
            )
            return (radius_start, radius_start + PIXELS_PER_GEN_LARGE)

    def get_radiusinout_for_gen_asc(self, generation):
        """
        Get the in and out radius for ascendant generation
        (starting with center pers = 0)
        """
        dummy_radiusin, radius_first_gen = self.get_radiusinout_for_gen_desc(0)
        outerradius = generation * PIXELS_PER_GENERATION + radius_first_gen
        innerradius = (generation - 1) * PIXELS_PER_GENERATION + radius_first_gen
        if generation == 0:
            innerradius = CHILDRING_WIDTH + TRANSLATE_PX
        return (innerradius, outerradius)

    def get_radiusinout_for_gen_pair(self, generation):
        """
        Get the in and out radius for descendant generation pair
        (starting with center pers = 0)
        :return: (radiusin_pers, radiusout_pers,
                  radiusin_partner, radiusout_partner)
        """
        radiusin, radiusout = self.get_radiusinout_for_gen_desc(generation)
        radius_spread = radiusout - radiusin - PIXELS_CHILDREN_GAP - PIXELS_PARTNER_GAP

        radiusin_pers = radiusin + PIXELS_CHILDREN_GAP
        radiusout_pers = radiusin_pers + PIXELS_PER_GENPERSON_RATIO * radius_spread
        radiusin_partner = radiusout_pers + PIXELS_PARTNER_GAP
        radiusout_partner = radiusout
        return (radiusin_pers, radiusout_pers, radiusin_partner, radiusout_partner)

    def people_generator(self):
        """
        a generator over all people outside of the core person
        """
        for generation in range(self.generations_desc):
            for data in self.gen2people[generation]:
                yield (data[0], data[6])
        for generation in range(self.generations_desc):
            for data in self.gen2fam[generation]:
                yield (data[7], data[6])
        for generation in range(self.generations_asc):
            for person, dummy_parents, dummy_child, userdata in self.data[generation]:
                yield person, userdata

    def innerpeople_generator(self):
        """
        a generator over all people inside of the core person
        """
        if False:
            yield

    def draw_background(self, ctx):
        """
        Draw the background
        """
        ctx.save()

        ctx.rotate(math.radians(self.rotate_value))
        delta = (self.rootangle_rad_asc[0] - self.rootangle_rad_desc[1]) / 2.0 % math.pi

        ctx.move_to(0, 0)
        radius_gradient_asc = 1.5 * self.maxradius_asc(self.generations_asc)
        gradient_asc = cairo.RadialGradient(
            0, 0, self.CENTER, 0, 0, radius_gradient_asc
        )
        color = hex_to_rgb(self.grad_end)
        gradient_asc.add_color_stop_rgba(
            0.0, color[0] / 255, color[1] / 255, color[2] / 255, 0.5
        )
        gradient_asc.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
        start_rad, stop_rad = (
            self.rootangle_rad_asc[0] - delta,
            self.rootangle_rad_asc[1] + delta,
        )
        ctx.set_source(gradient_asc)
        ctx.arc(0, 0, radius_gradient_asc, start_rad, stop_rad)
        ctx.fill()

        ctx.move_to(0, 0)
        radius_gradient_desc = 1.5 * self.maxradius_desc(self.generations_desc)
        gradient_desc = cairo.RadialGradient(
            0, 0, self.CENTER, 0, 0, radius_gradient_desc
        )
        color = hex_to_rgb(self.grad_start)
        gradient_desc.add_color_stop_rgba(
            0.0, color[0] / 255, color[1] / 255, color[2] / 255, 0.5
        )
        gradient_desc.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
        start_rad, stop_rad = (
            self.rootangle_rad_desc[0] - delta,
            self.rootangle_rad_desc[1] + delta,
        )
        ctx.set_source(gradient_desc)
        ctx.arc(0, 0, radius_gradient_desc, start_rad, stop_rad)
        ctx.fill()
        ctx.restore()

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
            size_w = size_h = 2 * halfdist

            size_w_a = self.get_allocated_width()
            size_h_a = self.get_allocated_height()
            self.set_size_request(max(size_w, size_w_a), max(size_h, size_h_a))
            size_w = self.get_allocated_width()
            size_h = self.get_allocated_height()
            scale_factor = self.get_scale_factor()
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, size_w * scale_factor, size_h * scale_factor
            )
            self.surface.set_device_scale(scale_factor, scale_factor)
            ctx = cairo.Context(self.surface)
            self.center_xy = self.center_xy_from_delta()
            ctx.translate(*self.center_xy)
        else:  # printing
            self.center_xy = halfdist, halfdist
            ctx.scale(scale, scale)
            ctx.translate(halfdist, halfdist)

        ctx.save()
        # Draw background
        if self.background_gradient:
            self.draw_background(ctx)
        # Draw center person:
        (
            person,
            dup,
            start,
            portion,
            dummy_parentfampos,
            dummy_nrfam,
            userdata,
            status,
        ) = self.gen2people[0][0]
        if not person:
            return
        gen_remapped = self.generations_desc - 1  # remapped generation
        if gen_remapped == 0:
            # remapped generation
            gen_remapped = self.generations_desc + self.generations_asc - 1
        (
            radiusin_pers,
            radiusout_pers,
            radiusin_partner,
            radiusout_partner,
        ) = self.get_radiusinout_for_gen_pair(0)
        radiusin = TRANSLATE_PX
        radiusout = radiusout_pers
        self.draw_person(
            ctx,
            person,
            radiusin,
            radiusout,
            math.pi / 2,
            math.pi / 2 + 2 * math.pi,
            gen_remapped,
            False,
            userdata,
            is_central_person=True,
        )
        # draw center to move chart
        ctx.set_source_rgb(0, 0, 0)  # black
        ctx.move_to(TRANSLATE_PX, 0)
        ctx.arc(0, 0, TRANSLATE_PX, 0, 2 * math.pi)
        ctx.fill()

        ctx.rotate(math.radians(self.rotate_value))
        # Ascendance
        for generation in range(self.generations_asc - 1, 0, -1):
            for idx, (person, parents, dummy_child, userdata) in enumerate(
                self.data[generation]
            ):
                if person:
                    start, stop, state = self.angle[generation][idx]
                    if state in [NORMAL, EXPANDED]:
                        fct = self.get_radiusinout_for_gen_asc
                        radiusin, radiusout = fct(generation)
                        dup = False
                        # remapped generation
                        gen_remapped = generation + self.generations_desc - 1
                        indicator = generation == self.generations_asc - 1 and parents
                        self.draw_person(
                            ctx,
                            person,
                            radiusin,
                            radiusout,
                            start,
                            stop,
                            gen_remapped,
                            dup,
                            userdata,
                            thick=(state == EXPANDED),
                            has_moregen_indicator=indicator,
                        )

        # Descendance
        for gen in range(self.generations_desc):
            (
                radiusin_pers,
                radiusout_pers,
                radiusin_partner,
                radiusout_partner,
            ) = self.get_radiusinout_for_gen_pair(gen)
            gen_remapped = self.generations_desc - gen - 1
            if gen_remapped == 0:
                # remapped generation
                gen_remapped = self.generations_desc + self.generations_asc - 1
            if gen > 0:
                for pdata in self.gen2people[gen]:
                    # person, duplicate or not, start angle, slice size,
                    #             parent pos in fam, nrfam, userdata, status
                    (
                        pers,
                        dup,
                        start,
                        portion,
                        dummy_pospar,
                        dummy_nrfam,
                        userdata,
                        status,
                    ) = pdata
                    if status != COLLAPSED:
                        self.draw_person(
                            ctx,
                            pers,
                            radiusin_pers,
                            radiusout_pers,
                            start,
                            start + portion,
                            gen_remapped,
                            dup,
                            userdata,
                            thick=status != NORMAL,
                        )
            # if gen < self.generations_desc - 1:
            for famdata in self.gen2fam[gen]:
                # family, duplicate or not, start angle, slice size,
                #       spouse pos in gen, nrchildren, userdata, status
                (
                    fam,
                    dup,
                    start,
                    portion,
                    dummy_posfam,
                    dummy_nrchild,
                    userdata,
                    partner,
                    status,
                ) = famdata
                if status != COLLAPSED:
                    more_pers_flag = (
                        gen == self.generations_desc - 1 and fam.get_child_ref_list()
                    )
                    self.draw_person(
                        ctx,
                        partner,
                        radiusin_partner,
                        radiusout_partner,
                        start,
                        start + portion,
                        gen_remapped,
                        dup,
                        userdata,
                        thick=(status != NORMAL),
                        has_moregen_indicator=more_pers_flag,
                    )
        ctx.restore()

        if self.background in [BACKGROUND_GRAD_AGE, BACKGROUND_GRAD_PERIOD]:
            self.draw_gradient_legend(ctx, halfdist)

    def cell_address_under_cursor(self, curx, cury):
        """
        Determine the cell address in the fan under the cursor
        position x and y.
        None if outside of diagram
        """
        radius, rads, dummy_raw_rads = self.cursor_to_polar(
            curx, cury, get_raw_rads=True
        )

        if radius < TRANSLATE_PX:
            return None
        radius_parents = self.get_radiusinout_for_gen_asc(0)[1]
        if (radius < radius_parents) or self.radian_in_bounds(
            self.rootangle_rad_desc[0], rads, self.rootangle_rad_desc[1]
        ):
            cell_address = self.cell_address_under_cursor_desc(rads, radius)
            if cell_address is not None:
                return (TYPE_DESCENDANCE,) + cell_address
        elif self.radian_in_bounds(
            self.rootangle_rad_asc[0], rads, self.rootangle_rad_asc[1]
        ):
            cell_address = self.cell_address_under_cursor_asc(rads, radius)
            if cell_address and cell_address[0] == 0:
                return None  # There is a gap before first parents
            if cell_address is not None:
                return (TYPE_ASCENDANCE,) + cell_address

        return None

    def cell_address_under_cursor_desc(self, rads, radius):
        """
        Determine the cell address in the fan under the cursor
        position x and y.
        None if outside of diagram
        """
        generation, selected, btype = None, None, TYPE_BOX_NORMAL
        for gen in range(self.generations_desc):
            (
                radiusin_pers,
                radiusout_pers,
                radiusin_partner,
                radiusout_partner,
            ) = self.get_radiusinout_for_gen_pair(gen)
            if radiusin_pers <= radius <= radiusout_pers:
                generation, btype = gen, TYPE_BOX_NORMAL
                break
            if radiusin_partner <= radius <= radiusout_partner:
                generation, btype = gen, TYPE_BOX_FAMILY
                break
        # find what person is in this position:
        if not (generation is None) and generation > 0:
            selected = FanChartDescWidget.personpos_at_angle(
                self, generation, rads, btype
            )

        if generation is None or selected is None:
            return None

        return generation, selected, btype

    def cell_address_under_cursor_asc(self, rads, radius):
        """
        Determine the cell address in the fan under the cursor
        position x and y.
        None if outside of diagram
        """

        generation, selected = None, None
        for gen in range(self.generations_asc):
            radiusin, radiusout = self.get_radiusinout_for_gen_asc(gen)
            if radiusin <= radius <= radiusout:
                generation = gen
                break

        # find what person is in this position:
        if not (generation is None) and generation > 0:
            selected = FanChartWidget.personpos_at_angle(self, generation, rads)
        if generation is None or selected is None:
            return None
        return generation, selected

    def person_at(self, cell_address):
        """
        returns the person at radius_first_gen
        """
        direction = cell_address[0]
        if direction == TYPE_ASCENDANCE:
            return FanChartWidget.person_at(self, cell_address[1:])
        elif direction == TYPE_DESCENDANCE:
            return FanChartDescWidget.person_at(self, cell_address[1:])
        return None

    def family_at(self, cell_address):
        """
        returns the family at cell_address
        """
        direction = cell_address[0]
        if direction == TYPE_ASCENDANCE:
            return None
        elif direction == TYPE_DESCENDANCE:
            return FanChartDescWidget.family_at(self, cell_address[1:])
        return None

    def do_mouse_click(self):
        # no drag occured, expand or collapse the section
        self.toggle_cell_state(self._mouse_click_cell_address)
        self._mouse_click = False
        self.draw()
        self.queue_draw()

    def expand_parents(self, generation, selected, current):
        if generation >= self.generations_asc:
            return
        selected = 2 * selected
        start, stop, state = self.angle[generation][selected]
        if state in [NORMAL, EXPANDED]:
            portion = (stop - start) * 2.0
            self.angle[generation][selected] = [current, current + portion, state]
            self.expand_parents(generation + 1, selected, current)
            current += portion
        start, stop, state = self.angle[generation][selected + 1]
        if state in [NORMAL, EXPANDED]:
            portion = (stop - start) * 2.0
            self.angle[generation][selected + 1] = [current, current + portion, state]
            self.expand_parents(generation + 1, selected + 1, current)

    def show_parents(self, generation, selected, angle, portion):
        if generation >= self.generations_asc:
            return
        selected *= 2
        self.angle[generation][selected][0] = angle
        self.angle[generation][selected][1] = angle + portion
        self.angle[generation][selected][2] = NORMAL
        self.show_parents(generation + 1, selected, angle, portion / 2.0)
        self.angle[generation][selected + 1][0] = angle + portion
        self.angle[generation][selected + 1][1] = angle + portion + portion
        self.angle[generation][selected + 1][2] = NORMAL
        self.show_parents(generation + 1, selected + 1, angle + portion, portion / 2.0)

    def hide_parents(self, generation, selected, angle):
        if generation >= self.generations_asc:
            return
        selected = 2 * selected
        self.angle[generation][selected][0] = angle
        self.angle[generation][selected][1] = angle
        self.angle[generation][selected][2] = COLLAPSED
        self.hide_parents(generation + 1, selected, angle)
        self.angle[generation][selected + 1][0] = angle
        self.angle[generation][selected + 1][1] = angle
        self.angle[generation][selected + 1][2] = COLLAPSED
        self.hide_parents(generation + 1, selected + 1, angle)

    def shrink_parents(self, generation, selected, current):
        if generation >= self.generations_asc:
            return
        selected = 2 * selected
        start, stop, state = self.angle[generation][selected]
        if state in [NORMAL, EXPANDED]:
            portion = (stop - start) / 2.0
            self.angle[generation][selected] = [current, current + portion, state]
            self.shrink_parents(generation + 1, selected, current)
            current += portion
        start, stop, state = self.angle[generation][selected + 1]
        if state in [NORMAL, EXPANDED]:
            portion = (stop - start) / 2.0
            self.angle[generation][selected + 1] = [current, current + portion, state]
            self.shrink_parents(generation + 1, selected + 1, current)

    def toggle_cell_state(self, cell_address):
        direction = cell_address[0]
        if direction == TYPE_ASCENDANCE:
            FanChartWidget.toggle_cell_state(self, cell_address[1:])
        elif direction == TYPE_DESCENDANCE:
            FanChartDescWidget.toggle_cell_state(self, cell_address[1:])
            self._compute_angles(*self.rootangle_rad_desc)


class FanChart2WayGrampsGUI(FanChartGrampsGUI):
    """class for functions fanchart GUI elements will need in Gramps"""

    def main(self):
        """
        Fill the data structures with the active data. This initializes all
        data.
        """
        root_person_handle = self.get_active("Person")
        self.fan.set_values(
            root_person_handle,
            self.generations_asc,
            self.generations_desc,
            self.flipupsidedownname,
            self.twolinename,
            self.background,
            self.background_gradient,
            self.fonttype,
            self.grad_start,
            self.grad_end,
            self.generic_filter,
            self.alpha_filter,
            self.angle_algo,
            self.dupcolor,
            self.showid,
        )
        self.fan.reset()
        self.fan.draw()
        self.fan.queue_draw()
