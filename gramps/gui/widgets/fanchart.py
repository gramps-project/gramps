#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2012 Benny Malengier
# Copyright (C) 2013 Vassilii Khachaturov
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
import colorsys
import pickle
from html import escape
import cairo
from gi.repository import Pango
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import PangoCairo

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import ChildRef, Family, Name, Person, Surname
from gramps.gen.lib.date import Today
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.libformatting import FormattingHelper
from gramps.gen.utils.db import (
    find_children,
    find_parents,
    get_timeperiod,
    find_witnessed_people,
    get_age,
    preset_name,
)
from gramps.gen.constfunc import is_quartz
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import (
    PIXELS_PER_GENERATION,
    BORDER_EDGE_WIDTH,
    CHILDRING_WIDTH,
    TRANSLATE_PX,
    PAD_PX,
    PAD_TEXT,
    BACKGROUND_SCHEME1,
    BACKGROUND_SCHEME2,
    BACKGROUND_GENDER,
    BACKGROUND_WHITE,
    BACKGROUND_GRAD_GEN,
    BACKGROUND_GRAD_AGE,
    BACKGROUND_SINGLE_COLOR,
    BACKGROUND_GRAD_PERIOD,
    GENCOLOR,
    MAX_AGE,
    GRADIENTSCALE,
    FORM_CIRCLE,
    FORM_HALFCIRCLE,
    FORM_QUADRANT,
    COLLAPSED,
    NORMAL,
    EXPANDED,
)
from .reorderfam import Reorder
from ..utils import color_graph_box, hex_to_rgb, is_right_click
from ..ddtargets import DdTargets
from ..editors import EditPerson, EditFamily
from ..utilscairo import warpPath
from gramps.gen.utils.symbols import Symbols

_ = glocale.translation.gettext

# following are used in name_displayer format def
# (must not conflict with standard defs)
TWO_LINE_FORMAT_1 = 100
TWO_LINE_FORMAT_2 = 101

# -------------------------------------------------------------------------
#
# FanChartBaseWidget
#
# -------------------------------------------------------------------------


class FanChartBaseWidget(Gtk.DrawingArea):
    """a base widget for fancharts"""

    CENTER = 60  # pixel radius of center, changes per fanchart

    def __init__(self, dbstate, uistate, callback_popup=None):
        Gtk.DrawingArea.__init__(self)
        self.radialtext = True
        st_cont = self.get_style_context()
        col = st_cont.lookup_color("text_color")
        if col[0]:
            self.textcolor = (col[1].red, col[1].green, col[1].blue)
        else:
            self.textcolor = (0, 0, 0)
        self.dbstate = dbstate
        self.uistate = uistate
        self.form = FORM_CIRCLE
        self.generations = 8
        self.childring = 0
        self.childrenroot = []
        self.angle = {}
        self.grad_start = "#0000FF"
        self.grad_end = "#FF0000"
        self.background = BACKGROUND_GRAD_GEN
        self.filter = None
        self.alpha_filter = 0.5
        self.translating = False
        self.showid = False
        self.flipupsidedownname = True
        self.dupcolor = None
        self.twolinename = False
        self.surface = None
        self.goto = None
        self.on_popup = callback_popup
        self.last_x, self.last_y = None, None
        self.fontdescr = "Sans"
        self.fontsize = 8
        # add parts of a two line name format to the displayer.  We add them
        # as standard names, but set them inactive so they don't show up in
        # name editor or selector.
        name_displayer.set_name_format(
            [
                (TWO_LINE_FORMAT_1, "fanchart_name_line1", "%l", False),
                (TWO_LINE_FORMAT_2, "fanchart_name_line2", "%f %s", False),
            ]
        )
        self.connect("button_release_event", self.on_mouse_up)
        self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button-press-event", self.on_mouse_down)
        # we want to grab key events also
        self.set_can_focus(True)
        self.connect("key-press-event", self.on_key_press)

        self.connect("notify::scale-factor", self.on_notify_scale_factor)
        self.connect("draw", self.on_draw)
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )

        # Enable drag
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(
            DdTargets.PERSON_LINK.atom_drag_type,
            DdTargets.PERSON_LINK.target_flags,
            DdTargets.PERSON_LINK.app_id,
        )
        # allow drag to a text document, info on drag_get will be 0L !
        tglist.add_text_targets(0)
        self.drag_source_set_target_list(tglist)
        self.connect("drag_data_get", self.on_drag_data_get)
        self.connect("drag_begin", self.on_drag_begin)
        self.connect("drag_end", self.on_drag_end)
        # Enable drop
        self.drag_dest_set(
            Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
            [DdTargets.PERSON_LINK.target()],
            Gdk.DragAction.COPY,
        )
        self.connect("drag_data_received", self.on_drag_data_received)
        self.uistate.connect("font-changed", self.reload_symbols)

        self._mouse_click = False
        self.rotate_value = 90  # degrees, initially, 1st gen male on right half
        self.center_delta_xy = [0, 0]  # translation of the center of the
        # fan wrt canonical center
        self.center_xy = [0, 0]  # coord of the center of the fan
        self.mouse_x = 0
        self.mouse_y = 0
        # (re)compute everything
        self.reset()
        self.set_size_request(120, 120)
        self.maxperiod = 0
        self.minperiod = 0
        self.cstart_hsv = None
        self.cend_hsv = None
        self.colors = None
        self.maincolor = None
        self.gradval = None
        self.gradcol = None
        self.in_drag = False
        self._mouse_click_cell_address = None
        self.reload_symbols()

    def reload_symbols(self):
        self.symbols = Symbols()
        dth_idx = self.uistate.death_symbol
        if self.uistate.symbols:
            self.bth = self.symbols.get_symbol_for_string(self.symbols.SYMBOL_BIRTH)
            self.dth = self.symbols.get_death_symbol_for_char(dth_idx)
        else:
            self.bth = self.symbols.get_symbol_fallback(self.symbols.SYMBOL_BIRTH)
            self.dth = self.symbols.get_death_symbol_fallback(dth_idx)

    def reset(self):
        """
        Reset the fan chart. This should trigger computation of all data
        structures needed
        """
        self.cache_fontcolor = {}

        # fill the data structure
        self._fill_data_structures()

        # prepare the colors for the boxes
        self.prepare_background_box(self.generations)

    def _fill_data_structures(self):
        """
        fill in the data structures that will be needed to draw the chart
        """
        raise NotImplementedError

    def do_size_request(self, requisition):
        """
        Overridden method to handle size request events.
        """
        if self.form == FORM_CIRCLE:
            requisition.width = 2 * self.halfdist()
            requisition.height = requisition.width
        elif self.form == FORM_HALFCIRCLE:
            requisition.width = 2 * self.halfdist()
            requisition.height = requisition.width / 2 + self.CENTER + PAD_PX
        elif self.form == FORM_QUADRANT:
            requisition.width = self.halfdist() + self.CENTER + PAD_PX
            requisition.height = requisition.width

    def do_get_preferred_width(self):
        """GTK3 uses width for height sizing model. This method will
        override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.width, req.width

    def do_get_preferred_height(self):
        """GTK3 uses width for height sizing model. This method will
        override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.height, req.height

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        raise NotImplementedError

    def gen_pixels(self):
        """
        how many pixels a generation takes up in the fanchart
        """
        raise NotImplementedError

    def get_radiusinout_for_gen(self, generation):
        """
        Get the in and out radius for descendant generation
        """
        raise NotImplementedError

    def on_notify_scale_factor(self, obj, pspec):
        """
        Callback to redraw the fanchart if the display's scale factor changes.
        """
        if not self.surface:
            return
        existing_scale = self.surface.get_device_scale()
        if self.get_scale_factor() == existing_scale[0] == existing_scale[1]:
            return
        self.surface = None
        self.draw()
        self.queue_draw()

    def on_draw(self, widget, ctx, scale=1.0):
        """
        callback to draw the fanchart
        """
        dummy_scale = scale
        dummy_widget = widget
        if self.surface:
            ctx.set_source_surface(self.surface, 0, 0)
            ctx.paint()

    def prt_draw(self, widget, ctx, scale=1.0):
        """
        method to allow direct drawing to cairo context for printing
        """
        dummy_widget = widget
        self.draw(ctx=ctx, scale=scale)

    def people_generator(self):
        """
        a generator over all people outside of the core person
        """
        raise NotImplementedError

    def innerpeople_generator(self):
        """
        a generator over all people inside of the core person
        """
        raise NotImplementedError

    def set_userdata_timeperiod(self, person, userdata):
        """
        set the userdata as used by timeperiod
        """
        period = None
        if person:
            period = get_timeperiod(self.dbstate.db, person)
            if period is not None:
                if period > self.maxperiod:
                    self.maxperiod = period
                if period < self.minperiod:
                    self.minperiod = period
        userdata.append(period)

    def set_userdata_age(self, person, userdata):
        """
        set the userdata as used by age
        """
        agecol = (1, 1, 1)  # white
        if person:
            age = get_age(self.dbstate.db, person)
            if age is not None:
                age = age[0]
                if age < 0:
                    age = 0
                elif age > MAX_AGE:
                    age = MAX_AGE
                # now determine fraction for gradient
                agefrac = age / MAX_AGE
                agecol = colorsys.hsv_to_rgb(
                    ((1 - agefrac) * self.cstart_hsv[0] + agefrac * self.cend_hsv[0]),
                    ((1 - agefrac) * self.cstart_hsv[1] + agefrac * self.cend_hsv[1]),
                    ((1 - agefrac) * self.cstart_hsv[2] + agefrac * self.cend_hsv[2]),
                )
        userdata.append((agecol[0] * 255, agecol[1] * 255, agecol[2] * 255))

    def prepare_background_box(self, maxgen):
        """
        Method that is called every reset of the chart, to precomputed values
        needed for the background of the boxes
        """
        cstart = hex_to_rgb(self.grad_start)
        cend = hex_to_rgb(self.grad_end)
        self.cstart_hsv = colorsys.rgb_to_hsv(
            cstart[0] / 255, cstart[1] / 255, cstart[2] / 255
        )
        self.cend_hsv = colorsys.rgb_to_hsv(cend[0] / 255, cend[1] / 255, cend[2] / 255)
        if self.background in [BACKGROUND_GENDER, BACKGROUND_SINGLE_COLOR]:
            # nothing to precompute
            self.colors = None
            self.maincolor = cstart
        elif self.background == BACKGROUND_GRAD_GEN:
            # compute the colors, -1, 0, ..., maxgen
            divs = [x / (maxgen - 1) for x in range(maxgen)] if maxgen > 1 else [0]
            rgb_colors = [
                colorsys.hsv_to_rgb(
                    (1 - x) * self.cstart_hsv[0] + x * self.cend_hsv[0],
                    (1 - x) * self.cstart_hsv[1] + x * self.cend_hsv[1],
                    (1 - x) * self.cstart_hsv[2] + x * self.cend_hsv[2],
                )
                for x in divs
            ]
            self.colors = [
                (255 * red, 255 * green, 255 * blue) for red, green, blue in rgb_colors
            ]
        elif self.background == BACKGROUND_GRAD_PERIOD:
            # we fill in in the data structure what the period is,
            # None if not found
            self.colors = None
            self.minperiod = 1e10
            self.maxperiod = -1e10
            gen_people = self.people_generator()
            for person, userdata in gen_people:
                self.set_userdata_timeperiod(person, userdata)
            # same for child
            gen_inner = self.innerpeople_generator()
            for child, userdata in gen_inner:
                self.set_userdata_timeperiod(child, userdata)
            # now create gradient data, 5 values from min to max rounded
            # to nearest 50
            if self.maxperiod < self.minperiod:
                self.maxperiod = self.minperiod = Today().get_year()
            rper = self.maxperiod // 50
            if rper * 50 != self.maxperiod:
                self.maxperiod = rper * 50 + 50
            self.minperiod = 50 * (self.minperiod // 50)
            periodrange = self.maxperiod - self.minperiod
            steps = 2 * GRADIENTSCALE - 1
            divs = [x / (steps - 1) for x in range(steps)]
            self.gradval = ["%d" % int(self.minperiod + x * periodrange) for x in divs]
            for index, value in enumerate(self.gradval):
                if index % 2 == 1:
                    self.gradval[index] = ""
            self.gradcol = [
                colorsys.hsv_to_rgb(
                    (1 - div) * self.cstart_hsv[0] + div * self.cend_hsv[0],
                    (1 - div) * self.cstart_hsv[1] + div * self.cend_hsv[1],
                    (1 - div) * self.cstart_hsv[2] + div * self.cend_hsv[2],
                )
                for div in divs
            ]

        elif self.background == BACKGROUND_GRAD_AGE:
            # we fill in in the data structure what the color age is,
            # white if no age
            self.colors = None
            gen_people = self.people_generator()
            for person, userdata in gen_people:
                self.set_userdata_age(person, userdata)
            # same for child
            gen_inner = self.innerpeople_generator()
            for child, userdata in gen_inner:
                self.set_userdata_age(child, userdata)
            # now create gradient data, 5 values from 0 to max
            steps = 2 * GRADIENTSCALE - 1
            divs = [x / (steps - 1) for x in range(steps)]
            self.gradval = ["%d" % int(x * MAX_AGE) for x in divs]
            self.gradval[-1] = "%d+" % MAX_AGE
            for index, value in enumerate(self.gradval):
                if index % 2 == 1:
                    self.gradval[index] = ""
            self.gradcol = [
                colorsys.hsv_to_rgb(
                    (1 - div) * self.cstart_hsv[0] + div * self.cend_hsv[0],
                    (1 - div) * self.cstart_hsv[1] + div * self.cend_hsv[1],
                    (1 - div) * self.cstart_hsv[2] + div * self.cend_hsv[2],
                )
                for div in divs
            ]
        else:
            # known colors per generation, set or compute them
            self.colors = GENCOLOR[self.background]

    def background_box(self, person, generation, userdata):
        """
        determine red, green, blue value of background of the box of person,
        which has gender gender, and is in ring generation
        """
        if generation == 0 and self.background in [
            BACKGROUND_GENDER,
            BACKGROUND_GRAD_GEN,
            BACKGROUND_SCHEME1,
            BACKGROUND_SCHEME2,
        ]:
            # white for center person:
            color = (255, 255, 255)
        elif self.background == BACKGROUND_GENDER:
            try:
                alive = probably_alive(person, self.dbstate.db)
            except RuntimeError:
                alive = False
            backgr, dummy_border = color_graph_box(alive, person.gender)
            color = hex_to_rgb(backgr)
        elif self.background == BACKGROUND_SINGLE_COLOR:
            color = self.maincolor
        elif self.background == BACKGROUND_GRAD_AGE:
            color = userdata[0]
        elif self.background == BACKGROUND_GRAD_PERIOD:
            period = userdata[0]
            if period is None:
                color = (255, 255, 255)  # white
            else:
                if self.maxperiod != self.minperiod:
                    periodfrac = (period - self.minperiod) / (
                        self.maxperiod - self.minperiod
                    )
                else:
                    periodfrac = 0.5
                periodcol = colorsys.hsv_to_rgb(
                    (
                        (1 - periodfrac) * self.cstart_hsv[0]
                        + periodfrac * self.cend_hsv[0]
                    ),
                    (
                        (1 - periodfrac) * self.cstart_hsv[1]
                        + periodfrac * self.cend_hsv[1]
                    ),
                    (
                        (1 - periodfrac) * self.cstart_hsv[2]
                        + periodfrac * self.cend_hsv[2]
                    ),
                )
                color = (periodcol[0] * 255, periodcol[1] * 255, periodcol[2] * 255)
        else:
            if self.background == BACKGROUND_GRAD_GEN and generation < 0:
                generation = 0
            color = self.colors[generation % len(self.colors)]
            if person.gender == Person.MALE:
                color = [x * 0.9 for x in color]
            elif person.gender == Person.OTHER:
                color = [x * 0.8 for x in color]
        # now we set transparency data
        if self.filter and not self.filter.match(person.handle, self.dbstate.db):
            if self.background == BACKGROUND_SINGLE_COLOR:
                alpha = 0.0  # no color shown
            else:
                alpha = self.alpha_filter
        else:
            alpha = 1.0

        return color[0], color[1], color[2], alpha

    def fontcolor(self, red, green, blue, alpha):
        """
        return the font color based on the r, g, b of the background
        """
        if alpha == 0:
            return self.textcolor
        try:
            return self.cache_fontcolor[(red, green, blue)]
        except KeyError:
            hls = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
            # we use the lightness value to determine white or black font
            if hls[1] > 0.4:
                self.cache_fontcolor[(red, green, blue)] = (0, 0, 0)
            else:
                self.cache_fontcolor[(red, green, blue)] = (1, 1, 1)
        return self.cache_fontcolor[(red, green, blue)]

    def fontbold(self, alpha):
        """
        The font should be bold if no transparency and font is set.
        In that case, True is returned
        """
        if alpha >= 1.0 and self.filter:
            return True
        return False

    def draw_radbox(
        self, ctx, radiusin, radiusout, start_rad, stop_rad, color, thick=False
    ):
        """
        Procedure to draw a person box in the outter ring position
        """
        ctx.move_to(radiusout * math.cos(start_rad), radiusout * math.sin(start_rad))
        ctx.arc(0, 0, radiusout, start_rad, stop_rad)
        ctx.line_to(radiusin * math.cos(stop_rad), radiusin * math.sin(stop_rad))
        ctx.arc_negative(0, 0, radiusin, stop_rad, start_rad)
        ctx.close_path()
        ##path = ctx.copy_path() # not working correct
        ctx.set_source_rgba(color[0], color[1], color[2], color[3])
        ctx.fill()
        # and again for the border
        ctx.move_to(radiusout * math.cos(start_rad), radiusout * math.sin(start_rad))
        ctx.arc(0, 0, radiusout, start_rad, stop_rad)
        if (start_rad - stop_rad) % (2 * math.pi) > 1e-5:
            radial_motion_type = ctx.line_to
        else:
            radial_motion_type = ctx.move_to
        radial_motion_type(radiusin * math.cos(stop_rad), radiusin * math.sin(stop_rad))
        ctx.arc_negative(0, 0, radiusin, stop_rad, start_rad)
        radial_motion_type(
            radiusout * math.cos(start_rad), radiusout * math.sin(start_rad)
        )
        ##ctx.append_path(path) # not working correct
        ctx.set_source_rgb(0, 0, 0)  # black
        if thick:
            ctx.set_line_width(3)
        else:
            ctx.set_line_width(1)
        ctx.stroke()
        ctx.set_line_width(1)

    def draw_innerring(self, ctx, person, userdata, start, inc):
        """
        Procedure to draw a person in the inner ring position
        """
        # in polar coordinates what is to draw
        rmin = TRANSLATE_PX
        rmax = TRANSLATE_PX + CHILDRING_WIDTH
        thetamin = start
        thetamax = start + inc
        # add child to angle storage
        self.angle[-2].append([thetamin, thetamax, None])
        # draw child now
        ctx.move_to(rmin * math.cos(thetamin), rmin * math.sin(thetamin))
        ctx.arc(0, 0, rmin, thetamin, thetamax)
        ctx.line_to(rmax * math.cos(thetamax), rmax * math.sin(thetamax))
        ctx.arc_negative(0, 0, rmax, thetamax, thetamin)
        ctx.close_path()
        ##path = ctx.copy_path() # not working correct
        ctx.set_source_rgb(0, 0, 0)  # black
        ctx.set_line_width(1)
        ctx.stroke()
        # now again to fill
        if person:
            red, green, blue, alpha = self.background_box(person, -1, userdata)
        else:
            red = green = blue = 255
            alpha = 1
        ctx.move_to(rmin * math.cos(thetamin), rmin * math.sin(thetamin))
        ctx.arc(0, 0, rmin, thetamin, thetamax)
        ctx.line_to(rmax * math.cos(thetamax), rmax * math.sin(thetamax))
        ctx.arc_negative(0, 0, rmax, thetamax, thetamin)
        ctx.close_path()
        ##ctx.append_path(path) # not working correct
        ctx.set_source_rgba(red / 255.0, green / 255.0, blue / 255.0, alpha)
        ctx.fill()

    def draw_person(
        self,
        ctx,
        person,
        radiusin,
        radiusout,
        start_rad,
        stop_rad,
        generation,
        dup,
        userdata,
        thick=False,
        has_moregen_indicator=False,
        is_central_person=False,
    ):
        """
        Display the piece of pie for a given person. start_rad and stop_rad
        are in radians.
        """
        ctx.save()
        # If we need an indicator of more generations:
        if has_moregen_indicator:
            # draw an indicator
            color = (1.0, 1.0, 1.0, 1.0)  # white
            self.draw_radbox(
                ctx,
                radiusout,
                radiusout + BORDER_EDGE_WIDTH,
                start_rad,
                stop_rad,
                color,
                thick=False,
            )

        # get the color of the background
        if not person:
            # if called on None, let's make a transparent box
            red, green, blue, alpha = (255, 255, 255, 0)
        elif dup:
            red, green, blue = self.dupcolor  # duplicate color
            alpha = 1.0
        else:
            red, green, blue, alpha = self.background_box(person, generation, userdata)
        color = (red / 255.0, green / 255.0, blue / 255.0, alpha)

        # now draw the person
        if not is_central_person:
            self.draw_radbox(
                ctx, radiusin, radiusout, start_rad, stop_rad, color, thick
            )
        else:
            # special box for centrer pers
            ctx.arc(0, 0, radiusout, 0, 2 * math.pi)
            if self.childring and self.childrenroot:
                ctx.arc_negative(0, 0, radiusin, 2 * math.pi, 0)
                ctx.close_path()
            ctx.set_source_rgba(*color)
            ctx.fill()

        if self.last_x is None or self.last_y is None:
            # we are not in a move, so draw text
            radial = False
            if self.radialtext:  ## and generation >= 6:
                space_arc_text = (radiusin + radiusout) / 2 * (stop_rad - start_rad)
                # is there more space to print it radial ?
                radial = space_arc_text < (radiusout - radiusin) * 1.1
            self.draw_person_text(
                ctx,
                person,
                radiusin,
                radiusout,
                start_rad,
                stop_rad,
                radial,
                self.fontcolor(red, green, blue, alpha),
                self.fontbold(alpha),
                can_flip=not is_central_person,
            )
        ctx.restore()

    def draw_person_text(
        self,
        ctx,
        person,
        radiusin,
        radiusout,
        start,
        stop,
        radial=False,
        fontcolor=(0, 0, 0),
        bold=False,
        can_flip=True,
    ):
        """
        Draw the piece of pie for a given person.
        """
        if not person:
            return
        draw_radial = radial and self.radialtext
        try:
            alive = probably_alive(person, self.dbstate.db)
        except RuntimeError:
            alive = False
        if not self.twolinename:
            name = name_displayer.display(person)
            if self.showid:
                name += " (" + person.gramps_id + ")"
            if self.uistate.symbols and not alive:
                name = self.dth + " " + name
            self.draw_text(
                ctx,
                name,
                radiusin,
                radiusout,
                start,
                stop,
                draw_radial,
                fontcolor,
                bold,
            )
        else:
            # text=name_displayer.display(person)
            if self.showid:
                text_line1 = "(" + person.gramps_id + ") "
            else:
                text_line1 = ""
            text_line1 += name_displayer.display_format(person, TWO_LINE_FORMAT_1)
            text_line2 = name_displayer.display_format(person, TWO_LINE_FORMAT_2)
            if draw_radial:
                split_frac_line1 = 0.5
                flipped = can_flip and (
                    (math.degrees((start + stop) / 2.0) + self.rotate_value - 90) % 360
                    < 179
                    and self.flipupsidedownname
                )
                if flipped:
                    middle = start * split_frac_line1 + stop * (1.0 - split_frac_line1)
                    (a11, a12, a21, a22) = (middle, stop, start, middle)
                else:
                    middle = start * (1.0 - split_frac_line1) + stop * split_frac_line1
                    (a11, a12, a21, a22) = (start, middle, middle, stop)
                written_textwidth = self.draw_text(
                    ctx,
                    text_line1,
                    radiusin,
                    radiusout,
                    a11,
                    a12,
                    draw_radial,
                    fontcolor,
                    bold=1,
                    flipped=flipped,
                )
                if written_textwidth == 0 and text_line1 != "":
                    # Not enought space for 2 line, fallback to 1 line
                    written_textwidth = self.draw_text(
                        ctx,
                        text_line1,
                        radiusin,
                        radiusout,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold=1,
                        flipped=flipped,
                    )
                    self.draw_text(
                        ctx,
                        text_line2,
                        radiusin + written_textwidth + PAD_TEXT,
                        radiusout,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold,
                        flipped,
                    )
                else:
                    self.draw_text(
                        ctx,
                        text_line2,
                        radiusin,
                        radiusout,
                        a21,
                        a22,
                        draw_radial,
                        fontcolor,
                        bold,
                        flipped,
                    )
            else:
                middle = radiusin * 0.5 + radiusout * 0.5
                flipped = can_flip and (
                    (math.degrees((start + stop) / 2.0) + self.rotate_value) % 360 < 179
                    and self.flipupsidedownname
                )
                if flipped:
                    self.draw_text(
                        ctx,
                        text_line2,
                        middle,
                        radiusout,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold=0,
                        flipped=flipped,
                    )
                    self.draw_text(
                        ctx,
                        text_line1,
                        radiusin,
                        middle,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold=1,
                        flipped=flipped,
                    )
                else:
                    self.draw_text(
                        ctx,
                        text_line1,
                        middle,
                        radiusout,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold=1,
                        flipped=flipped,
                    )
                    self.draw_text(
                        ctx,
                        text_line2,
                        radiusin,
                        middle,
                        start,
                        stop,
                        draw_radial,
                        fontcolor,
                        bold=0,
                        flipped=flipped,
                    )

    def wrap_truncate_layout(
        self, layout, font, width_pixels, height_pixels, tryrescale=True
    ):
        """
        Uses the layout to wrap and truncate its text to given width
        Returns: (w,h) as returned by layout.get_pixel_size()
        """
        all_text_backup = layout.get_text()
        layout.set_font_description(font)
        layout.set_width(Pango.SCALE * width_pixels)

        # NOTE: one may not truncate the text to just the 1st line's text,
        # because the truncation can create invalid Unicode.
        if layout.get_line_count() > 1:
            layout.set_text(layout.get_text(), layout.get_line(0).length)

        # 2. we check if height is ok
        dummy_width, height = layout.get_pixel_size()
        if height > height_pixels:
            if tryrescale:
                # try to reduce the height
                fontsize = max(
                    height_pixels / height * font.get_size() / 1.1,
                    font.get_size() / 2.0,
                )
                font.set_size(fontsize)
                # reducing the height allows for more characters
                layout.set_text(all_text_backup, len(all_text_backup.encode("utf-8")))
                layout.set_font_description(font)
                if layout.get_line_count() > 1:
                    layout.set_text(layout.get_text(), layout.get_line(0).length)
                dummy_width, height = layout.get_pixel_size()
            # we check again if height is ok
            if height > height_pixels:
                # we could not fix it, no text
                layout.set_text("", 0)
        layout.context_changed()
        return layout.get_pixel_size()

    def draw_text(
        self,
        ctx,
        text,
        radiusin,
        radiusout,
        start_rad,
        stop_rad,
        radial=False,
        fontcolor=(0, 0, 0),
        bold=False,
        flipped=False,
    ):
        """
        Display text at a particular radius, between start_rad and stop_rad
        radians.
        """
        font = Pango.FontDescription("")
        fontsize = self.fontsize
        font.set_size(fontsize * Pango.SCALE)
        if bold:
            font.set_weight(Pango.Weight.BOLD)
        ctx.save()
        ctx.set_source_rgb(*fontcolor)
        if radial and self.radialtext:
            self.draw_radial_text(
                ctx, text, radiusin, radiusout, start_rad, stop_rad, font, flipped
            )
        else:
            self.draw_arc_text(
                ctx, text, radiusin, radiusout, start_rad, stop_rad, font, flipped
            )
        ctx.restore()

    def draw_radial_text(
        self, ctx, text, radiusin, radiusout, start_rad, stop_rad, font, flipped
    ):
        """
        Draw the text in the available portion.
        """
        layout = self.create_pango_layout(text)
        if is_quartz():
            PangoCairo.context_set_resolution(layout.get_context(), 72)
        layout.set_font_description(font)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)

        # compute available text space
        # NOTE: for radial text, the sector radius height is the text width
        avail_height = (stop_rad - start_rad) * radiusin - 2.0 * PAD_TEXT
        avail_width = radiusout - radiusin - 2.0 * PAD_TEXT

        dummy_width, height = self.wrap_truncate_layout(
            layout, font, avail_width, avail_height, tryrescale=True
        )

        #  2. now draw this text
        # offset for cairo-font system is 90
        if flipped:
            angle = (start_rad + stop_rad) / 2 + (height / radiusin / 2) + math.pi
            start_pos = -radiusout + PAD_TEXT
        else:
            angle = (start_rad + stop_rad) / 2 - (height / radiusin / 2)
            start_pos = radiusin + PAD_TEXT
        ctx.rotate(angle)
        layout.context_changed()
        ctx.move_to(start_pos, 0)
        PangoCairo.show_layout(ctx, layout)

    def draw_arc_text(
        self,
        ctx,
        text,
        radiusin,
        radiusout,
        start_rad,
        stop_rad,
        font,
        bottom_is_outside,
    ):
        """
        Display text at a particular radius, between start and stop
        degrees, setting it up along the arc, center-justified.

        Text not fitting a single line will be char-wrapped away.
        """
        layout = self.create_pango_layout(text)
        if is_quartz():
            PangoCairo.context_set_resolution(layout.get_context(), 72)
        layout.set_font_description(font)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)

        # get height of text:
        textheight = layout.get_size()[1] / Pango.SCALE
        radius_text = (radiusin + radiusout) / 2.0

        # 1. compute available text space
        avail_height = radiusout - radiusin - 2.0 * PAD_TEXT
        avail_width = (stop_rad - start_rad) * radius_text - 2.0 * PAD_TEXT

        width, dummy_height = self.wrap_truncate_layout(
            layout, font, avail_width, avail_height, tryrescale=True
        )

        # 2. Compute text position start angle
        mid_rad = (stop_rad + start_rad) / 2
        pos_rad = mid_rad - (width / 2 / radius_text)
        end_rad = pos_rad + (width / radius_text)

        # 3. Use the layout to provide us the metrics of the text box
        ctx.new_path()
        PangoCairo.layout_path(ctx, layout)

        # 4. The moment of truth: map the text box onto the sector, and render!
        warpPath(
            ctx,
            self.create_map_rect_to_sector(
                radius_text, pos_rad, end_rad, textheight, bottom_is_outside
            ),
        )
        ctx.fill()

    @staticmethod
    def create_map_rect_to_sector(
        radius, start_rad, stop_rad, textheight, bottom_is_outside=False
    ):
        """
        Create a 2D-transform, mapping a rectangle onto a circle sector.

        :param radius: average radius of the target sector
        :param start_rad: start radial angle of the sector, in radians
        :param stop_rad: stop radial angle of the sector, in radians
        :param textheight height of the text
        :param bottom_is_outside flag defining if we write with the
                                 bottom toward outside
        :returns: a lambda (x,y)|->(xNew,yNew) to feed to warpPath.
        """
        if bottom_is_outside:

            def phi(posx):
                """x in outside case"""
                return -posx / radius + stop_rad

            def rho(posy):
                """y in outside case"""
                return radius + (posy - textheight / 2.0)

        else:

            def phi(posx):
                """x in inside case"""
                return posx / radius + start_rad

            def rho(posy):
                """y in inside case"""
                return radius - (posy - textheight / 2.0)

        return lambda posx, posy: (
            rho(posy) * math.cos(phi(posx)),
            rho(posy) * math.sin(phi(posx)),
        )

    def draw_gradient_legend(self, ctx, halfdist):
        """
        Draw the gradient legend
        """
        dummy_halfdist = halfdist
        gradwidth = 10
        gradheight = 10
        starth = 15
        startw = 5
        ctx.save()

        ctx.translate(-self.center_xy[0], -self.center_xy[1])

        font = Pango.FontDescription("")
        fontsize = self.fontsize
        font.set_size(fontsize * Pango.SCALE)
        for color, text in zip(self.gradcol, self.gradval):
            ctx.move_to(startw, starth)
            ctx.rectangle(startw, starth, gradwidth, gradheight)
            ctx.set_source_rgb(color[0], color[1], color[2])
            ctx.fill()
            layout = self.create_pango_layout(text)
            if is_quartz():
                PangoCairo.context_set_resolution(layout.get_context(), 72)
            layout.set_font_description(font)
            ctx.move_to(startw + gradwidth + 4, starth)
            ctx.set_source_rgb(0, 0, 0)  # black
            PangoCairo.show_layout(ctx, layout)
            starth = starth + gradheight
        ctx.restore()

    def cursor_on_tranlation_dot(self, curx, cury):
        """
        Determine if the cursor at position x and y is
        on the translation dot
        """
        fanxy = curx - self.center_xy[0], cury - self.center_xy[1]
        radius = math.sqrt((fanxy[0]) ** 2 + (fanxy[1]) ** 2)
        return radius < TRANSLATE_PX

    def cursor_to_polar(self, curx, cury, get_raw_rads=False):
        """
        Compute angle, radius in unrotated fan
        """
        fanxy = curx - self.center_xy[0], cury - self.center_xy[1]
        radius = math.sqrt((fanxy[0]) ** 2 + (fanxy[1]) ** 2)
        # angle before rotation:
        # children are in cairo angle (clockwise) from pi to 3 pi
        # rads however is clock 0 to 2 pi
        raw_rads = math.atan2(fanxy[1], fanxy[0]) % (2 * math.pi)
        rads = (raw_rads - math.radians(self.rotate_value)) % (2 * math.pi)
        if get_raw_rads:
            return radius, rads, raw_rads
        else:
            return radius, rads

    def radian_in_bounds(self, start_rad, rads, stop_rad):
        """
        We compare (rads - start_rad) % (2.0 * math.pi) and
                   (stop_rad - start_rad)
        """
        assert start_rad <= stop_rad
        portion = stop_rad - start_rad
        dist_rads_to_start_rads = (rads - start_rad) % (2.0 * math.pi)
        # print(start_rad, rads, stop_rad, ". (rads-start), portion :",
        #       dist_rads_to_start_rads, portion)
        return dist_rads_to_start_rads < portion

    def cell_address_under_cursor(self, curx, cury):
        """
        Determine the generation and the position in the generation at
        position x and y, as well as the type of box.
        generation = -1 on center black dot
        generation >= self.generations outside of diagram
        """
        raise NotImplementedError

    def person_at(self, cell_address):
        """
        returns the person at cell_address
        """
        raise NotImplementedError

    def family_at(self, cell_address):
        """
        returns the family at cell_address
        """
        raise NotImplementedError

    def _have_children(self, person):
        """
        Returns True if a person has children.
        TODO: is there no util function for this
        """
        if person:
            for family_handle in person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and family.get_child_ref_list():
                    return True
        return False

    def on_key_press(self, widget, eventkey):
        """grab key press"""
        dummy_widget = widget
        if self.mouse_x and self.mouse_y:
            cell_address = self.cell_address_under_cursor(self.mouse_x, self.mouse_y)
            if cell_address is None:
                return False
            person, family = (
                self.person_at(cell_address),
                self.family_at(cell_address),
            )
            if person and (Gdk.keyval_name(eventkey.keyval) == "e"):
                # we edit the person
                self.edit_person_cb(None, person.handle)
                return True
            elif family and (Gdk.keyval_name(eventkey.keyval) == "f"):
                # we edit the family
                self.edit_fam_cb(None, family.handle)
                return True

        return False

    def on_mouse_down(self, widget, event):
        """
        What to do if we release a mouse button
        """
        dummy_widget = widget
        self.translating = False  # keep track of up/down/left/right movement

        if event.button == 1:
            # we grab the focus to enable to see key_press events
            self.grab_focus()

        # left mouse on center dot, we translate on left click
        if self.cursor_on_tranlation_dot(event.x, event.y):
            if event.button == 1:  # left mouse
                # save the mouse location for movements
                self.translating = True
                self.last_x, self.last_y = event.x, event.y
                return True

        cell_address = self.cell_address_under_cursor(event.x, event.y)
        # click in open area, prepare for a rotate
        if cell_address is None:
            # save the mouse location for movements
            self.last_x, self.last_y = event.x, event.y
            return True

        # left click on person, prepare for expand/collapse or drag
        if event.button == 1:
            self._mouse_click = True
            self._mouse_click_cell_address = cell_address
            return False

        # right click on person, context menu
        # Do things based on state, event.get_state(), or button, event.button
        if is_right_click(event):
            person, family = (
                self.person_at(cell_address),
                self.family_at(cell_address),
            )
            fhandle = None
            if family:
                fhandle = family.handle
            if person and self.on_popup:
                self.on_popup(widget, event, person.handle, fhandle)
                return True

        return False

    def on_mouse_move(self, widget, event):
        """
        What to do if we move the mouse
        """
        dummy_widget = widget
        self._mouse_click = False
        if self.last_x is None or self.last_y is None:
            # while mouse is moving, we must update the tooltip based on person
            cell_address = self.cell_address_under_cursor(event.x, event.y)
            self.mouse_x, self.mouse_y = event.x, event.y
            tooltip = ""
            if cell_address:
                person = self.person_at(cell_address)
                tooltip = self.format_helper.format_person(person, 11)
            self.set_tooltip_text(tooltip)
            return False

        # translate or rotate should happen
        if self.translating:
            canonical_center = self.center_xy_from_delta([0, 0])
            self.center_delta_xy = (
                canonical_center[0] - event.x,
                canonical_center[1] - event.y,
            )
            self.center_xy = self.center_xy_from_delta()
        else:
            # get the angles of the two points from the center:
            start_angle = math.atan2(
                event.y - self.center_xy[1], event.x - self.center_xy[0]
            )
            end_angle = math.atan2(
                self.last_y - self.center_xy[1], self.last_x - self.center_xy[0]
            )
            # now look at change in angle:
            diff_angle = (end_angle - start_angle) % (math.pi * 2.0)
            self.rotate_value -= math.degrees(diff_angle)
            self.last_x, self.last_y = event.x, event.y
        self.draw()
        self.queue_draw()
        return True

    def center_xy_from_delta(self, delta=None):
        """
        return the x and y position for the center of the canvas
        """
        alloc = self.get_allocation()
        (dummy_x, dummy_y, width, height) = alloc.x, alloc.y, alloc.width, alloc.height
        if delta is None:
            delta = self.center_delta_xy
        if self.form == FORM_CIRCLE:
            canvas_xy = width / 2 - delta[0], height / 2 - delta[1]
        elif self.form == FORM_HALFCIRCLE:
            canvas_xy = (width / 2 - delta[0], height - self.CENTER - PAD_PX - delta[1])
        elif self.form == FORM_QUADRANT:
            canvas_xy = (
                self.CENTER + PAD_PX - delta[0],
                height - self.CENTER - PAD_PX - delta[1],
            )
        return canvas_xy

    def do_mouse_click(self):
        """
        action to take on left mouse click
        """
        pass

    def on_mouse_up(self, widget, event):
        """
        What to do if we move the mouse
        """
        dummy_widget = widget
        dummy_event = event
        if self._mouse_click:
            self.do_mouse_click()
            return True
        if self.last_x is None or self.last_y is None:
            # No translate or rotate
            return True
        if self.translating:
            self.translating = False
        else:
            self.center_delta_xy = -1, 0
            self.center_xy = self.center_xy_from_delta()

        self.last_x, self.last_y = None, None
        self.draw()
        self.queue_draw()
        return True

    def on_drag_begin(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        dummy_widget = widget
        dummy_data = data
        self.in_drag = True
        self.drag_source_set_icon_name("gramps-person")

    def on_drag_end(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        dummy_widget = widget
        dummy_data = data
        self.in_drag = False

    def on_drag_data_get(self, widget, context, sel_data, info, time):
        """
        Returned parameters after drag.
        Specified for 'person-link', for others return text info about person.
        """
        dummy_widget = widget
        dummy_time = time
        tgs = [x.name() for x in context.list_targets()]
        person = self.person_at(self._mouse_click_cell_address)
        if person:
            if info == DdTargets.PERSON_LINK.app_id:
                data = (
                    DdTargets.PERSON_LINK.drag_type,
                    id(self),
                    person.get_handle(),
                    0,
                )
                sel_data.set(sel_data.get_target(), 8, pickle.dumps(data))
            elif ("TEXT" in tgs or "text/plain" in tgs) and info == 0:
                sel_data.set_text(self.format_helper.format_person(person, 11), -1)

    def on_drag_data_received(
        self, widget, context, pos_x, pos_y, sel_data, info, time
    ):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is defined, extract the value from sel_data.data
        """
        dummy_context = context
        dummy_widget = widget
        dummy_info = info
        dummy_time = time
        radius, dummy_rads = self.cursor_to_polar(pos_x, pos_y)

        if radius < self.CENTER:
            if sel_data and sel_data.get_data():
                (dummy_drag_type, dummy_idval, handle, dummy_val) = pickle.loads(
                    sel_data.get_data()
                )
                self.goto(self, handle)

    def edit_person_cb(self, obj, person_handle):
        """
        Edit a person
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
            return True
        return False

    def edit_fam_cb(self, obj, family_handle):
        """
        Edit a family
        """
        fam = self.dbstate.db.get_family_from_handle(family_handle)
        if fam:
            try:
                EditFamily(self.dbstate, self.uistate, [], fam)
            except WindowActiveError:
                pass
            return True
        return False


# -------------------------------------------------------------------------
#
# FanChartWidget
#
# -------------------------------------------------------------------------


class FanChartWidget(FanChartBaseWidget):
    """
    Interactive Fan Chart Widget.
    """

    def __init__(self, dbstate, uistate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of FanChartGramplet for example of model format.
        """
        self.angle = {}
        self.childrenroot = []
        self.rootangle_rad = []
        self.menu = None
        self.data = {}
        self.set_values(
            None,
            9,
            BACKGROUND_GRAD_GEN,
            True,
            True,
            True,
            True,
            "Sans",
            "#0000FF",
            "#FF0000",
            None,
            0.5,
            FORM_CIRCLE,
            False,
        )
        FanChartBaseWidget.__init__(self, dbstate, uistate, callback_popup)

    def set_values(
        self,
        root_person_handle,
        maxgen,
        background,
        childring,
        flipupsidedownname,
        twolinename,
        radialtext,
        fontdescr,
        grad_start,
        grad_end,
        filtr,
        alpha_filter,
        form,
        showid,
    ):
        """
        Reset the values to be used:

        :param root_person_handle: person to show
        :param maxgen: maximum generations to show
        :param background: config setting of which background procedure to use
        :type background: int
        :param childring: to show the center ring with children or not
        :param twolinename: uses two lines for the display of person's name
        :param flipupsidedownname: flip name on the left of the fanchart
                                   for the display of person's name
        :param radialtext: try to use radial text or not
        :param fontdescr: string describing the font to use
        :param grad_start: colors to use for background procedure
        :param grad_end: colors to use for background procedure
        :param filtr: the person filter to apply to the people in the chart
        :param alpha: the alpha transparency value (0-1) to apply to filtered
                      out data
        :param form: the ``FORM_`` constant for the fanchart
        :param showid: to show the gramps_id or not
        """
        self.rootpersonh = root_person_handle
        self.generations = maxgen
        self.radialtext = radialtext
        self.childring = childring
        self.twolinename = twolinename
        self.flipupsidedownname = flipupsidedownname
        self.background = background
        self.fontdescr = fontdescr
        self.grad_start = grad_start
        self.grad_end = grad_end
        self.filter = filtr
        self.alpha_filter = alpha_filter
        self.form = form
        self.showid = showid

    def set_generations(self):
        """
        Set the generations to max, and fill data structures with initial data.
        """
        self.angle = {}
        if self.childring:
            self.angle[-2] = []
        self.data = {}
        self.childrenroot = []
        self.rootangle_rad = [math.radians(0), math.radians(360)]
        if self.form == FORM_HALFCIRCLE:
            self.rootangle_rad = [math.radians(90), math.radians(270)]
        elif self.form == FORM_QUADRANT:
            self.rootangle_rad = [math.radians(180), math.radians(270)]
        for i in range(self.generations):
            # person, parents?, children?
            self.data[i] = [(None,) * 4] * 2**i
            self.angle[i] = []
            angle = self.rootangle_rad[0]
            portion = 1 / (2**i) * (self.rootangle_rad[1] - self.rootangle_rad[0])
            for dummy_count in self.data[i]:
                # start, stop, state
                self.angle[i].append([angle, angle + portion, NORMAL])
                angle += portion

    def _fill_data_structures(self):
        """
        Initialise the data structures
        """
        self.set_generations()
        if not self.rootpersonh:
            return
        person = self.dbstate.db.get_person_from_handle(self.rootpersonh)
        parents = self._have_parents(person)
        child = self._have_children(person)
        # our data structure is the text, the person object, parents, child and
        # list for userdata which we might fill in later.
        self.data[0][0] = (person, parents, child, [])
        self.childrenroot = []
        if child:
            childlist = find_children(self.dbstate.db, person)
            for child_handle in childlist:
                child = self.dbstate.db.get_person_from_handle(child_handle)
                if not child:
                    continue
                else:
                    self.childrenroot.append(
                        (child, True, self._have_children(child), [])
                    )
        for current in range(1, self.generations):
            parent = 0
            # person, parents, children
            for pers, dummy_q, dummy_c, dummy_d in self.data[current - 1]:
                # Get father's and mother's details:
                for person in [
                    self._get_parent(pers, True),
                    self._get_parent(pers, False),
                ]:
                    if current == self.generations - 1:
                        parents = self._have_parents(person)
                    else:
                        parents = None
                    self.data[current][parent] = (person, parents, None, [])
                    if person is None:
                        # start,stop,male/right,state
                        self.angle[current][parent][2] = COLLAPSED
                    parent += 1

    def _have_parents(self, person):
        """
        Returns True if a person has parents.
        TODO: is there no util function for this
        """
        if person:
            mother = self._get_parent(person, False)
            father = self._get_parent(person, True)
            return not mother is father is None
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
                        person_handle = Family.get_father_handle(family)
                    else:
                        person_handle = Family.get_mother_handle(family)
                    if person_handle:
                        fct = self.dbstate.db.get_person_from_handle
                        return fct(person_handle)
        return None

    def gen_pixels(self):
        """
        how many pixels a generation takes up in the fanchart
        """
        return PIXELS_PER_GENERATION

    def nrgen(self):
        """
        return the generation if we have a person to draw
        """
        # compute the number of generations present
        for generation in range(self.generations - 1, 0, -1):
            for person, *rest in self.data[generation]:
                if person:
                    return generation
        return 1

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        return PIXELS_PER_GENERATION * self.nrgen() + self.CENTER + BORDER_EDGE_WIDTH

    def get_radiusinout_for_gen(self, generation):
        outerradius = generation * PIXELS_PER_GENERATION + self.CENTER
        innerradius = (generation - 1) * PIXELS_PER_GENERATION + self.CENTER
        if generation == 0:
            innerradius = CHILDRING_WIDTH + TRANSLATE_PX
        return (innerradius, outerradius)

    def people_generator(self):
        """
        a generator over all people outside of the core person
        """
        for generation in range(self.generations):
            for person, dummy_parents, dummy_child, userdata in self.data[generation]:
                yield person, userdata

    def innerpeople_generator(self):
        """
        a generator over all people inside of the core person
        """
        for childdata in self.childrenroot:
            (person, dummy_parents, dummy_child, userdata) = childdata
            yield (person, userdata)

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
            scale_factor = self.get_scale_factor()
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, size_w * scale_factor, size_h * scale_factor
            )
            self.surface.set_device_scale(scale_factor, scale_factor)
            ctx = cairo.Context(self.surface)
            self.center_xy = self.center_xy_from_delta()
            ctx.translate(*self.center_xy)
        else:  # printing
            if self.form == FORM_QUADRANT:
                self.center_xy = self.CENTER + PIXELS_PER_GENERATION, halfdist
            else:
                self.center_xy = halfdist + PIXELS_PER_GENERATION, halfdist
            ctx.scale(scale, scale)
            ctx.translate(*self.center_xy)

        ctx.save()
        ctx.rotate(math.radians(self.rotate_value))
        for generation in range(self.generations - 1, 0, -1):
            for idx, (person, parents, child, userdata) in enumerate(
                self.data[generation]
            ):
                if person:
                    start, stop, state = self.angle[generation][idx]
                    if state in [NORMAL, EXPANDED]:
                        (radiusin, radiusout) = self.get_radiusinout_for_gen(generation)
                        dup = False
                        indicator = generation == self.generations - 1 and parents
                        self.draw_person(
                            ctx,
                            person,
                            radiusin,
                            radiusout,
                            start,
                            stop,
                            generation,
                            dup,
                            userdata,
                            thick=(state == EXPANDED),
                            has_moregen_indicator=indicator,
                        )
        ctx.restore()
        # Draw center person:
        (person, parents, child, userdata) = self.data[0][0]
        if person:
            radiusin, radiusout = self.get_radiusinout_for_gen(0)
            if not child:
                radiusin = TRANSLATE_PX
            self.draw_person(
                ctx,
                person,
                radiusin,
                radiusout,
                math.pi / 2,
                math.pi / 2 + 2 * math.pi,
                0,
                False,
                userdata,
                thick=False,
                has_moregen_indicator=False,
                is_central_person=True,
            )
            # draw center disk to move chart
            ctx.set_source_rgb(0, 0, 0)  # black
            ctx.move_to(TRANSLATE_PX, 0)
            ctx.arc(0, 0, TRANSLATE_PX, 0, 2 * math.pi)
            if child:  # has at least one child
                ctx.fill()
            else:
                ctx.stroke()
            if child and self.childring:
                self.draw_childring(ctx)
        if self.background in [BACKGROUND_GRAD_AGE, BACKGROUND_GRAD_PERIOD]:
            self.draw_gradient_legend(ctx, halfdist)

    def draw_childring(self, ctx):
        """
        Draw the ring for the children
        """
        ctx.move_to(TRANSLATE_PX + CHILDRING_WIDTH, 0)
        ctx.set_source_rgb(0, 0, 0)  # black
        ctx.set_line_width(1)
        ctx.arc(0, 0, TRANSLATE_PX + CHILDRING_WIDTH, 0, 2 * math.pi)
        ctx.stroke()
        nrchild = len(self.childrenroot)
        # Y axis is downward. positve angles are hence clockwise
        startangle = math.pi
        if nrchild <= 4:
            angleinc = math.pi / 2
        else:
            angleinc = 2 * math.pi / nrchild
        for childdata in self.childrenroot:
            (person, dummy_parents, dummy_child, userdata) = childdata
            self.draw_innerring(ctx, person, userdata, startangle, angleinc)
            startangle += angleinc

    def expand_parents(self, generation, selected, current):
        """
        Expand the parents
        """
        if generation >= self.generations:
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
        """
        Show the parents
        """
        if generation >= self.generations:
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
        """
        Hide the parents
        """
        if generation >= self.generations:
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
        """
        Shrink the parents
        """
        if generation >= self.generations:
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
        """
        Toggle the cell (expanded/shrinked)
        """
        generation, selected = cell_address
        if generation < 1:
            return
        gstart, gstop, gstate = self.angle[generation][selected]
        if gstate == NORMAL:  # let's expand
            if selected % 2 == 0:
                # go to right
                stop = gstop + (gstop - gstart)
                self.angle[generation][selected] = [gstart, stop, EXPANDED]
                self.expand_parents(generation + 1, selected, gstart)
                start, stop, dummy_state = self.angle[generation][selected + 1]
                self.angle[generation][selected + 1] = [stop, stop, COLLAPSED]
                self.hide_parents(generation + 1, selected + 1, stop)
            else:
                # go to left
                start = gstart - (gstop - gstart)
                self.angle[generation][selected] = [start, gstop, EXPANDED]
                self.expand_parents(generation + 1, selected, start)
                start, stop, dummy_state = self.angle[generation][selected - 1]
                self.angle[generation][selected - 1] = [start, start, COLLAPSED]
                self.hide_parents(generation + 1, selected - 1, start)
        elif gstate == EXPANDED:  # let's shrink
            if selected % 2 == 0:
                # shrink from right
                portion = (gstop - gstart) / 2.0
                stop = gstop - portion
                self.angle[generation][selected] = [gstart, stop, NORMAL]
                self.shrink_parents(generation + 1, selected, gstart)
                self.angle[generation][selected + 1][0] = stop  # start
                self.angle[generation][selected + 1][1] = stop + portion  # stop
                self.angle[generation][selected + 1][2] = NORMAL
                self.show_parents(generation + 1, selected + 1, stop, portion / 2.0)
            else:
                # shrink from left
                portion = (gstop - gstart) / 2.0
                start = gstop - portion
                self.angle[generation][selected] = [start, gstop, NORMAL]
                self.shrink_parents(generation + 1, selected, start)
                start, stop, dummy_state = self.angle[generation][selected - 1]
                self.angle[generation][selected - 1] = [start, start + portion, NORMAL]
                self.show_parents(generation + 1, selected - 1, start, portion / 2.0)

    def cell_address_under_cursor(self, curx, cury):
        """
        Determine the cell address in the fan under the cursor
        position x and y.
        None if outside of diagram
        """
        radius, rads, raw_rads = self.cursor_to_polar(curx, cury, get_raw_rads=True)

        # find out the generation
        if radius < TRANSLATE_PX:
            return None
        elif (
            self.childring
            and self.angle[-2]
            and radius < TRANSLATE_PX + CHILDRING_WIDTH
        ):
            generation = -2  # indication of one of the children
        elif radius < self.CENTER:
            generation = 0
        else:
            generation = None
            for gen in range(self.generations):
                radiusin, radiusout = self.get_radiusinout_for_gen(gen)
                if radiusin <= radius <= radiusout:
                    generation = gen
                    break

        # find what person at this angle:
        selected = None
        if not (generation is None) and generation > 0:
            selected = self.personpos_at_angle(generation, rads)
        elif generation == -2:
            for idx, (start, stop, dummy_state) in enumerate(self.angle[generation]):
                if self.radian_in_bounds(start, raw_rads, stop):
                    selected = idx
                    break
        if generation is None or selected is None:
            return None
        return generation, selected

    def personpos_at_angle(self, generation, rads):
        """
        returns the person in generation generation at angle.
        """
        if generation == 0:
            return 0
        selected = None
        for idx, (start, stop, state) in enumerate(self.angle[generation]):
            if self.data[generation][idx][0]:  # there is a person there
                if state == COLLAPSED:
                    continue
                if self.radian_in_bounds(start, rads, stop):
                    selected = idx
                    break
        return selected

    def person_at(self, cell_address):
        """
        returns the person at cell_address
        """
        generation, pos = cell_address
        if generation == -2:
            person = self.childrenroot[pos][0]
        else:
            person = self.data[generation][pos][0]
        return person

    def family_at(self, cell_address):
        """
        returns the family at cell_address
        Difficult here, we would need to go to child, and then obtain the first
        parent family, as that is the family that is shown.
        """
        return None

    def do_mouse_click(self):
        # no drag occured, expand or collapse the section
        self.toggle_cell_state(self._mouse_click_cell_address)
        self._mouse_click = False
        self.draw()
        self.queue_draw()


class FanChartGrampsGUI:
    """class for functions fanchart GUI elements will need in Gramps"""

    def __init__(self, on_childmenu_changed):
        """
        Common part of GUI that shows Fan Chart, needs to know what to do if
        one moves via Fan Ch    def set_fan(self, fan):art to a new person
        on_childmenu_changed: in popup, function called on moving
                              to a new person
        """
        self.fan = None
        self.menu = None
        self.twolinename = False
        self.radialtext = None
        self.maxgen = 8
        self.childring = 0
        self.showid = False
        self.grad_start = "#0000FF"
        self.grad_end = "#FF0000"
        self.form = FORM_CIRCLE
        self.alpha_filter = 0.5
        self.filter = None
        self.background = BACKGROUND_GRAD_GEN
        self.on_childmenu_changed = on_childmenu_changed
        self.format_helper = FormattingHelper(self.dbstate, self.uistate)
        self.uistate.connect("font-changed", self.reload_symbols)

    def reload_symbols(self):
        self.format_helper.reload_symbols()

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
        root_person_handle = self.get_active("Person")
        self.fan.set_values(
            root_person_handle,
            self.maxgen,
            self.background,
            self.childring,
            self.flipupsidedownname,
            self.twolinename,
            self.radialtext,
            self.fonttype,
            self.grad_start,
            self.grad_end,
            self.generic_filter,
            self.alpha_filter,
            self.form,
            self.showid,
        )
        self.fan.reset()
        self.fan.draw()
        self.fan.queue_draw()

    def on_popup(self, obj, event, person_handle, family_handle=None):
        """
        Builds the full menu (including Siblings, Spouses, Children,
        and Parents) with navigation.
        """
        dummy_obj = obj
        # store menu for GTK3 to avoid it being destroyed before showing
        self.menu = Gtk.Menu()
        menu = self.menu
        self.menu.set_reserve_toggle_size(False)

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_item = Gtk.MenuItem(label=name_displayer.display(person))
        go_item.connect("activate", self.on_childmenu_changed, person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = Gtk.MenuItem.new_with_mnemonic(_("_Edit"))
        edit_item.connect("activate", self.edit_person_cb, person_handle)
        edit_item.show()
        menu.append(edit_item)
        # action related to the clicked family (when there is one)
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            edit_fam_item = Gtk.MenuItem()
            edit_fam_item.set_label(label=_("Edit family"))
            edit_fam_item.connect("activate", self.edit_fam_cb, family_handle)
            edit_fam_item.show()
            menu.append(edit_fam_item)
            # see if a reorder button is needed
            if family.get_father_handle() == person_handle:
                parth = family.get_mother_handle()
            else:
                parth = family.get_father_handle()
            lenfams = 0
            if parth:
                partner = self.dbstate.db.get_person_from_handle(parth)
                lenfams = len(partner.get_family_handle_list())
                if lenfams in [0, 1]:
                    lenfams = len(partner.get_parent_family_handle_list())
            reord_fam_item = Gtk.MenuItem()
            reord_fam_item.set_label(label=_("Reorder families"))
            reord_fam_item.connect("activate", self.reord_fam_cb, parth)
            reord_fam_item.set_sensitive(lenfams > 1)
            reord_fam_item.show()
            menu.append(reord_fam_item)

        clipboard_item = Gtk.MenuItem.new_with_mnemonic(_("_Copy"))
        clipboard_item.connect(
            "activate", self.copy_person_to_clipboard_cb, person_handle
        )
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
            if not sp_id:
                continue
            spouse = self.dbstate.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(Gtk.Menu())
                sp_menu = item.get_submenu()
                sp_menu.set_reserve_toggle_size(False)

            sp_item = Gtk.MenuItem(label=name_displayer.display(spouse))
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
        siblings = []
        step_siblings = []
        for fhdle in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(fhdle)
            sib_list = fam.get_child_ref_list()
            for sib_ref in sib_list:
                sib_id = sib_ref.ref
                if sib_id == person.get_handle():
                    continue
                siblings.append(sib_id)
            # Collect a list of per-step-family step-siblings
            for parent_h in [fam.get_father_handle(), fam.get_mother_handle()]:
                if not parent_h:
                    continue
                parent = self.dbstate.db.get_person_from_handle(parent_h)
                other_families = [
                    self.dbstate.db.get_family_from_handle(fam_id)
                    for fam_id in parent.get_family_handle_list()
                    if fam_id not in pfam_list
                ]
                for step_fam in other_families:
                    fam_stepsiblings = [
                        sib_ref.ref
                        for sib_ref in step_fam.get_child_ref_list()
                        if not sib_ref.ref == person.get_handle()
                    ]
                    if fam_stepsiblings:
                        step_siblings.append(fam_stepsiblings)

        # Add siblings sub-menu with a bar between each siblings group
        if siblings or step_siblings:
            item.set_submenu(Gtk.Menu())
            sib_menu = item.get_submenu()
            sib_menu.set_reserve_toggle_size(False)
            sibs = [siblings] + step_siblings
            for sib_group in sibs:
                for sib_id in sib_group:
                    sib = self.dbstate.db.get_person_from_handle(sib_id)
                    if not sib:
                        continue
                    if find_children(self.dbstate.db, sib):
                        thelabel = escape(name_displayer.display(sib))
                        label = Gtk.Label(label="<b><i>%s</i></b>" % thelabel)
                    else:
                        thelabel = escape(name_displayer.display(sib))
                        label = Gtk.Label(label=thelabel)
                    sib_item = Gtk.MenuItem()
                    label.set_use_markup(True)
                    label.show()
                    label.set_alignment(0, 0)
                    sib_item.add(label)
                    linked_persons.append(sib_id)
                    sib_item.connect("activate", self.on_childmenu_changed, sib_id)
                    sib_item.show()
                    sib_menu.append(sib_item)
                if sibs.index(sib_group) < len(sibs) - 1:
                    sep = Gtk.SeparatorMenuItem.new()
                    sep.show()
                    sib_menu.append(sep)
        else:
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
                child_menu.set_reserve_toggle_size(False)

            if find_children(self.dbstate.db, child):
                thelabel = escape(name_displayer.display(child))
                label = Gtk.Label(label="<b><i>%s</i></b>" % thelabel)
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            child_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
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
        item.set_submenu(Gtk.Menu())
        par_menu = item.get_submenu()
        par_menu.set_reserve_toggle_size(False)
        no_parents = 1
        par_list = find_parents(self.dbstate.db, person)
        for par_id in par_list:
            if not par_id:
                continue
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0

            if find_parents(self.dbstate.db, par):
                thelabel = escape(name_displayer.display(par))
                label = Gtk.Label(label="<b><i>%s</i></b>" % thelabel)
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            par_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate", self.on_childmenu_changed, par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            # show an add button
            add_item = Gtk.MenuItem.new_with_mnemonic(_("_Add"))
            add_item.connect("activate", self.on_add_parents, person_handle)
            add_item.show()
            par_menu.append(add_item)

        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db, person):
            # if p_id in linked_persons:
            #    continue    # skip already listed family members

            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(Gtk.Menu())
                per_menu = item.get_submenu()
                per_menu.set_reserve_toggle_size(False)

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            per_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            per_item.add(label)
            per_item.connect("activate", self.on_childmenu_changed, p_id)
            per_item.show()
            per_menu.append(per_item)

        if no_related:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # we now construct an add menu
        item = Gtk.MenuItem.new_with_mnemonic(_("_Add"))
        item.set_submenu(Gtk.Menu())
        add_menu = item.get_submenu()
        add_menu.set_reserve_toggle_size(False)
        if family_handle:
            # allow to add a child to this family
            add_child_item = Gtk.MenuItem()
            add_child_item.set_label(_("Add child to family"))
            add_child_item.connect("activate", self.add_child_to_fam_cb, family_handle)
            add_child_item.show()
            add_menu.append(add_child_item)
        elif person_handle:
            # allow to add a partner to this person
            add_partner_item = Gtk.MenuItem()
            add_partner_item.set_label(_("Add partner to person"))
            add_partner_item.connect(
                "activate", self.add_partner_to_pers_cb, person_handle
            )
            add_partner_item.show()
            add_menu.append(add_partner_item)

        add_pers_item = Gtk.MenuItem()
        add_pers_item.set_label(_("Add a person"))
        add_pers_item.connect("activate", self.add_person_cb)
        add_pers_item.show()
        add_menu.append(add_pers_item)
        item.show()
        menu.append(item)

        menu.popup_at_pointer(event)
        return 1

    def edit_person_cb(self, obj, person_handle):
        """
        Edit a person
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
            return True
        return False

    def edit_fam_cb(self, obj, family_handle):
        """
        Edit a family
        """
        fam = self.dbstate.db.get_family_from_handle(family_handle)
        if fam:
            try:
                EditFamily(self.dbstate, self.uistate, [], fam)
            except WindowActiveError:
                pass
            return True
        return False

    def reord_fam_cb(self, obj, person_handle):
        """
        reorder a family
        """
        try:
            Reorder(self.dbstate, self.uistate, [], person_handle)
        except WindowActiveError:
            pass
        return True

    def add_person_cb(self, obj):
        """
        Add a person
        """
        person = Person()
        # the editor requires a surname
        person.primary_name.add_surname(Surname())
        person.primary_name.set_primary_surname(0)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def add_child_to_fam_cb(self, obj, family_handle):
        """
        Add a child to a family
        """
        callback = lambda x: self.callback_add_child(x, family_handle)
        person = Person()
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        family = self.dbstate.db.get_family_from_handle(family_handle)
        father = self.dbstate.db.get_person_from_handle(family.get_father_handle())
        if father:
            preset_name(father, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person, callback=callback)
        except WindowActiveError:
            pass

    def callback_add_child(self, person, family_handle):
        """
        Add a child
        """
        ref = ChildRef()
        ref.ref = person.get_handle()
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_child_ref(ref)

        with DbTxn(_("Add Child to Family"), self.dbstate.db) as trans:
            # add parentref to child
            person.add_parent_family_handle(family_handle)
            # default relationship is used
            self.dbstate.db.commit_person(person, trans)
            # add child to family
            self.dbstate.db.commit_family(family, trans)

    def add_partner_to_pers_cb(self, obj, person_handle):
        """
        Add a family with the person preset
        """
        family = Family()
        person = self.dbstate.db.get_person_from_handle(person_handle)

        if not person:
            return

        if person.gender == Person.MALE:
            family.set_father_handle(person.handle)
        else:
            family.set_mother_handle(person.handle)

        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def on_add_parents(self, obj, person_handle):
        """
        Add a family
        """
        dummy_obj = obj
        family = Family()
        childref = ChildRef()
        childref.set_reference_handle(person_handle)
        family.add_child_ref(childref)
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            return

    def copy_person_to_clipboard_cb(self, obj, person_handle):
        """
        Renders the person data into some lines of text and puts that
        into the clipboard
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            cbx = Gtk.Clipboard.get_for_display(
                Gdk.Display.get_default(), Gdk.SELECTION_CLIPBOARD
            )
            cbx.set_text(self.format_helper.format_person(person, 11), -1)
            return True
        return False
