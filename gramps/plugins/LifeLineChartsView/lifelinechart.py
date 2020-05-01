#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020 Christian Schulze
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

"""
See https://github.com/CWSchulze/life_line_chart
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
import math
import colorsys
import pickle
from html import escape
import cairo
from gi.repository import Pango
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import PangoCairo

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from copy import deepcopy
import sys, os
from life_line_chart import AncestorGraph
from life_line_chart import BaseIndividual, BaseFamily, InstanceContainer, estimate_birth_date, estimate_death_date
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import Person, ChildRefType, EventType, FamilyRelType
from gramps.gen.lib import Date
import datetime

logger = logging.getLogger("LifeLineChart View")

def get_date(event):
    event_data = None
    try:
        date_obj = event.get_date_object()
        if date_obj.year == 0:
            return None
        date = datetime.datetime(date_obj.dateval[2], max(
            1, date_obj.dateval[1]), max(1, date_obj.dateval[0]), 0, 0, 0)
        quality = date_obj.get_quality()
        modifier = date_obj.get_modifier()
        comment = ''
        if quality == Date.QUAL_CALCULATED:
            comment = 'Calculated'
        elif quality == Date.QUAL_ESTIMATED:
            comment = 'Estimated'
        elif modifier == Date.MOD_BEFORE:
            comment = 'Before'
        elif modifier == Date.MOD_AFTER:
            comment = 'After'
        elif modifier == Date.MOD_ABOUT:
            comment = 'About'
        event_data = {
            'gramps_event': event,
            'date': date,
            'ordinal_value': date.toordinal(),
            'comment': comment
        }
    except:
        pass
    return event_data


def get_relevant_events(gramps_person, dbstate, target):
    events_key_name = {
        EventType.BIRTH: 'birth',
        EventType.CHRISTEN: 'christening',
        EventType.DEATH: 'death',
        EventType.BURIAL: 'burial',
        EventType.BAPTISM: 'baptism',
    }
    for eventref in gramps_person.get_event_ref_list():
        #        for get_event_reference, key_name in events:
        #            eventref = get_event_reference()
        event = dbstate.db.get_event_from_handle(eventref.ref)
        if event and event.get_type().value in events_key_name:
            key_name = events_key_name[event.get_type().value]
            val = get_date(event)
            if val:
                target[key_name] = val

    if 'birth' in target:
        target['birth_or_christening'] = target['birth']
    elif 'birth_or_christening' not in target and 'christening' in target:
        target['birth_or_christening'] = target['christening']
    elif 'birth_or_christening' not in target and 'baptism' in target:
        target['birth_or_christening'] = target['baptism']
    else:
        target['birth_or_christening'] = None

    if 'death' in target:
        target['death_or_burial'] = target['death']
    elif 'death_or_burial' not in target and 'burial' in target:
        target['death_or_burial'] = target['burial']
    else:
        target['death_or_burial'] = None


class GrampsIndividual(BaseIndividual):
    def __init__(self, instances, dbstate, individual_id):
        BaseIndividual.__init__(self, instances, individual_id)
        self._dbstate = dbstate
        self._gramps_person = self._dbstate.db.get_person_from_handle(
            individual_id)
        self._initialize()

    def _initialize(self):
        BaseIndividual._initialize(self)
        self.child_of_family_id = self._gramps_person.get_parent_family_handle_list()
        get_relevant_events(self._gramps_person, self._dbstate, self.events)
        estimate_birth_date(self, self._instances)
        estimate_death_date(self)

        # if family and other.get_handle() in [family.get_father_handle(),
        #                                          family.get_mother_handle()]:
        #         family_rel = family.get_relationship()
        #         #check for divorce event:
        #         ex = False
        #         for eventref in family.get_event_ref_list():
        #             event = db.get_event_from_handle(eventref.ref)
        #             if event and (event.get_type() == EventType.DIVORCE
        #                           or event.get_type() == EventType.ANNULMENT):
        #                 ex = True
        #                 break
        #         if family_rel == FamilyRelType.MARRIED:
        #             if ex:
        #                 val.append(self.PARTNER_EX_MARRIED)
        #             else:
        #                 val.append(self.PARTNER_MARRIED)
        #         elif family_rel == FamilyRelType.UNMARRIED:
        #             if ex:
        #                 val.append(self.PARTNER_EX_UNMARRIED)
        #             else:
        #                 val.append(self.PARTNER_UNMARRIED)
        #         elif family_rel == FamilyRelType.CIVIL_UNION:
        #             if ex:
        #                 val.append(self.PARTNER_EX_CIVIL_UNION)
        #             else:
        #                 val.append(self.PARTNER_CIVIL_UNION)
        #         else:
        #             if ex:
        #                 val.append(self.PARTNER_EX_UNKNOWN_REL)
        #             else:
        #                 val.append(self.PARTNER_UNKNOWN_REL)

    #     _get_relevant_events(self._database_indi, self.individual_id, self.events)
    #     estimate_birth_date(self, self._instances)
    #     estimate_death_date(self)

    def _get_name(self):
        return [name_displayer.display_format(self._gramps_person, 101), name_displayer.display_format(self._gramps_person, 100)]
    name = property(_get_name)

    def _get_father_and_mother(self):
        child_of_families = self._gramps_person.get_parent_family_handle_list()
        if child_of_families:
            child_of_family = self._dbstate.db.get_family_from_handle(
                child_of_families[0])
            father = child_of_family.get_father_handle()
            mother = child_of_family.get_mother_handle()
            return father, mother
        return None, None

    def _get_marriage_family_ids(self):
        return self._gramps_person.get_family_handle_list()


def estimate_marriage_date(family):
    if not family.marriage:
        children_events = []
        for child in family.children_individual_ids:
            child_events = {}
            gramps_person = family._dbstate.db.get_person_from_handle(child)
            get_relevant_events(gramps_person, family._dbstate, child_events)
            if child_events['birth_or_christening']:
                children_events.append(child_events['birth_or_christening'])

        #unsorted_marriages = [family._instances[('f',m)] for m in family._marriage_family_ids]
        if len(children_events) > 0:
            sorted_pairs = list(zip([(m['ordinal_value'], i) for i, m in enumerate(
                children_events)], children_events))
            sorted_pairs.sort()
            family.marriage = sorted_pairs[0][1]


class GrampsFamily(BaseFamily):
    def __init__(self, instances, dbstate, family_id):
        BaseFamily.__init__(self, instances, family_id)
        self._dbstate = dbstate
        self._gramps_family = self._dbstate.db.get_family_from_handle(
            family_id)
        self._initialize()

    def _initialize(self):
        BaseFamily._initialize(self)
        #self.marriage = {}

        reflist = self._gramps_family.get_event_ref_list()
        if reflist:
            elist = [self._dbstate.db.get_event_from_handle(ref.ref)
                     for ref in reflist]
            events = [evnt for evnt in elist
                      if evnt.type == EventType.MARRIAGE]
            if events:
                #    return displayer.display(date_obj)
                self.marriage = get_date(events[0])
                if self.marriage and events[0].place:
                    p = self._dbstate.db.get_place_from_handle(events[0].place)
                    self.location = p.title
        estimate_marriage_date(self)

    def _get_husband_and_wife_id(self):
        father_handle = Family.get_father_handle(self._gramps_family)
        mother_handle = Family.get_mother_handle(self._gramps_family)
        return father_handle, mother_handle

    def _get_children_ids(self):
        return [ref.ref for ref in self._gramps_family.get_child_ref_list()]

    def _get_husb_name(self):
        father_handle = Family.get_father_handle(self._gramps_family)
        return self.husb.name

    def _get_wife_name(self):
        mother_handle = Family.get_mother_handle(self._gramps_family)
        return self.wife.name
    husb_name = property(_get_husb_name)
    wife_name = property(_get_wife_name)




def get_dbdstate_instance_container(dbstate):
    logger.debug('start reading data')

    # def instantiate_all(self, database_fam, database_indi):
    #     for family_id in list(database_fam.keys()):
    #         if not ('f',family_id) in self:
    #             self[('f',family_id)] = Family(self, database_fam, database_indi, family_id)
    #     for individual_id in list(database_indi.keys()):
    #         if not ('i',individual_id) in self:
    #             self[('i',individual_id)] = Individual(self, database_fam, database_indi, individual_id)

    logger.debug('start creating instances')
    return InstanceContainer(
        lambda self, key: GrampsFamily(self, dbstate, key[1]),
        lambda self, key: GrampsIndividual(self, dbstate, key[1]),
        None)  # lambda self : instantiate_all(self, database_fam, database_indi))



from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import ChildRef, Family, Name, Person, Surname
from gramps.gen.lib.date import Today
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.libformatting import FormattingHelper
from gramps.gen.utils.db import (find_children, find_parents, get_timeperiod,
                                 find_witnessed_people, get_age, preset_name)
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
    EXPANDED)
from gramps.gui.widgets.reorderfam import Reorder
from gramps.gui.utils import color_graph_box, hex_to_rgb, is_right_click
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditPerson, EditFamily
from gramps.gui.utilscairo import warpPath
from gramps.gen.utils.symbols import Symbols

_ = glocale.translation.gettext

# following are used in name_displayer format def
# (must not conflict with standard defs)
TWO_LINE_FORMAT_1 = 100
TWO_LINE_FORMAT_2 = 101

#-------------------------------------------------------------------------
#
# LifeLineChartBaseWidget
#
#-------------------------------------------------------------------------


class LifeLineChartBaseWidget(Gtk.DrawingArea):
    """ a base widget for lifelinecharts"""
    CENTER = 60                # pixel radius of center, changes per lifelinechart

    def __init__(self, dbstate, uistate, callback_popup=None):
        Gtk.DrawingArea.__init__(self)
        self.radialtext = True
        st_cont = self.get_style_context()
        col = st_cont.lookup_color('text_color')
        if col[0]:
            self.textcolor = (col[1].red, col[1].green, col[1].blue)
        else:
            self.textcolor = (0, 0, 0)
        self.dbstate = dbstate
        self.uistate = uistate
        self.form = FORM_CIRCLE
        self.generations = 3
        self.childring = 0
        self.childrenroot = []
        self.angle = {}
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
            [(TWO_LINE_FORMAT_1, 'lifelinechart_name_line1', '%l', False),
             (TWO_LINE_FORMAT_2, 'lifelinechart_name_line2', '%f %s', False)])
        self.connect("button_release_event", self.on_mouse_up)
        self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button-press-event", self.on_mouse_down)
        #we want to grab key events also
        self.set_can_focus(True)
        self.connect("key-press-event", self.on_key_press)

        self.connect("draw", self.on_draw)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK)

        # Enable drag
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [],
                             Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                   DdTargets.PERSON_LINK.target_flags,
                   DdTargets.PERSON_LINK.app_id)
        #allow drag to a text document, info on drag_get will be 0L !
        tglist.add_text_targets(0)
        self.drag_source_set_target_list(tglist)
        self.connect("drag_data_get", self.on_drag_data_get)
        self.connect("drag_begin", self.on_drag_begin)
        self.connect("drag_end", self.on_drag_end)
        # Enable drop
        self.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
                           [DdTargets.PERSON_LINK.target()],
                           Gdk.DragAction.COPY)
        self.connect('drag_data_received', self.on_drag_data_received)
        self.uistate.connect('font-changed', self.reload_symbols)

        self._mouse_click = False
        self.rotate_value = 90  # degrees, initially, 1st gen male on right half
        self.center_delta_xy = [0, 0]  # translation of the center of the
        # lifeline wrt canonical center
        self.center_xy = [0, 0]  # coord of the center of the lifeline
        self.mouse_x = 0
        self.mouse_y = 0
        #(re)compute everything
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
        self.symbols = Symbols()
        self.reload_symbols()

    def reload_symbols(self):
        dth_idx = self.uistate.death_symbol
        if self.uistate.symbols:
            self.bth = self.symbols.get_symbol_for_string(
                self.symbols.SYMBOL_BIRTH)
            self.dth = self.symbols.get_death_symbol_for_char(dth_idx)
        else:
            self.bth = self.symbols.get_symbol_fallback(
                self.symbols.SYMBOL_BIRTH)
            self.dth = self.symbols.get_death_symbol_fallback(dth_idx)

    def reset(self):
        """
        Reset the lifeline chart. This should trigger computation of all data
        structures needed
        """

        # fill the data structure
        #self._fill_data_structures()

        # prepare the colors for the boxes

    def _fill_data_structures(self):
        """
        fill in the data structures that will be needed to draw the chart
        """
        raise NotImplementedError

    def do_size_request(self, requisition):
        """
        Overridden method to handle size request events.
        """
        requisition.width = 800
        requisition.height = 600

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

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        raise NotImplementedError

    def on_draw(self, widget, ctx, scale=1.):
        """
        callback to draw the lifelinechart
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
                #now determine fraction for gradient
                agefrac = age / MAX_AGE
                agecol = colorsys.hsv_to_rgb(
                    ((1-agefrac) * self.cstart_hsv[0] +
                     agefrac * self.cend_hsv[0]),
                    ((1-agefrac) * self.cstart_hsv[1] +
                     agefrac * self.cend_hsv[1]),
                    ((1-agefrac) * self.cstart_hsv[2] +
                     agefrac * self.cend_hsv[2]),
                )
        userdata.append((agecol[0]*255, agecol[1]*255, agecol[2]*255))

    def background_box(self, person, generation, userdata):
        """
        determine red, green, blue value of background of the box of person,
        which has gender gender, and is in ring generation
        """
        if generation == 0 and self.background in [BACKGROUND_GENDER,
                                                   BACKGROUND_GRAD_GEN,
                                                   BACKGROUND_SCHEME1,
                                                   BACKGROUND_SCHEME2]:
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
                    periodfrac = ((period - self.minperiod)
                                  / (self.maxperiod - self.minperiod))
                else:
                    periodfrac = 0.5
                periodcol = colorsys.hsv_to_rgb(
                    ((1-periodfrac) * self.cstart_hsv[0] +
                     periodfrac * self.cend_hsv[0]),
                    ((1-periodfrac) * self.cstart_hsv[1] +
                     periodfrac * self.cend_hsv[1]),
                    ((1-periodfrac) * self.cstart_hsv[2] +
                     periodfrac * self.cend_hsv[2]),
                )
                color = (periodcol[0]*255, periodcol[1]*255, periodcol[2]*255)
        else:
            if self.background == BACKGROUND_GRAD_GEN and generation < 0:
                generation = 0
            color = self.colors[generation % len(self.colors)]
            if person.gender == Person.MALE:
                color = [x*.9 for x in color]
        # now we set transparency data
        if self.filter and not self.filter.match(person.handle,
                                                 self.dbstate.db):
            if self.background == BACKGROUND_SINGLE_COLOR:
                alpha = 0.  # no color shown
            else:
                alpha = self.alpha_filter
        else:
            alpha = 1.

        return color[0], color[1], color[2], alpha

    def cursor_to_polar(self, curx, cury, get_raw_rads=False):
        """
        Compute angle, radius in unrotated lifeline
        """
        lifelinexy = curx - self.center_xy[0], cury - self.center_xy[1]
        radius = math.sqrt((lifelinexy[0]) ** 2 + (lifelinexy[1]) ** 2)
        #angle before rotation:
        #children are in cairo angle (clockwise) from pi to 3 pi
        #rads however is clock 0 to 2 pi
        raw_rads = math.atan2(lifelinexy[1], lifelinexy[0]) % (2 * math.pi)
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
        """grab key press
        """
        dummy_widget = widget
        if Gdk.keyval_name(eventkey.keyval) == 'plus':
            # we edit the person
            self.zoom_level *= 1.1
            self.draw()
            self.queue_draw()
            return True
        if Gdk.keyval_name(eventkey.keyval) == 'minus':
            # we edit the person
            self.zoom_level /= 1.1
            self.draw()
            self.queue_draw()
            return True
        #if self.mouse_x and self.mouse_y:
            # cell_address = self.cell_address_under_cursor(self.mouse_x,
            # #                                               self.mouse_y)
            # if cell_address is None:
            #     return False
            # person, family = (self.person_at(cell_address),
            #                   self.family_at(cell_address))
            # if person and (Gdk.keyval_name(eventkey.keyval) == 'e'):
            #     # we edit the person
            #     self.edit_person_cb(None, person.handle)
            #     return True
            # elif family and (Gdk.keyval_name(eventkey.keyval) == 'f'):
            #     # we edit the family
            #     self.edit_fam_cb(None, family.handle)
            #     return True

        return False

    def on_mouse_down(self, widget, event):
        """
        What to do if we release a mouse button
        """
        dummy_widget = widget
        self.translating = False  # keep track of up/down/left/right movement

        if event.button == 1:
            #we grab the focus to enable to see key_press events
            self.grab_focus()

        # cell_address = self.cell_address_under_cursor(event.x, event.y)
        individual = self.life_line_chart_ancestor_graph.get_individual_from_position(
            event.x/self.zoom_level, event.y/self.zoom_level)
        if individual:
            individual_id = individual.individual_id
        else:
            #return True

            # left mouse on center dot, we translate on left click
            if event.button == 1:  # left mouse
                # save the mouse location for movements
                self.translating = True
                self.last_x, self.last_y = event.x, event.y
                return True

        # #left click on person, prepare for expand/collapse or drag
        if event.button == 1:
            self._mouse_click = True
            self._mouse_click_individual_id = individual_id
            return False

        # #right click on person, context menu
        # # Do things based on state, event.get_state(), or button, event.button
        # if is_right_click(event):
        #     person, family = (self.person_at(cell_address),
        #                       self.family_at(cell_address))
        #     fhandle = None
        #     if family:
        #         fhandle = family.handle
        #     if person and self.on_popup:
        #         self.on_popup(widget, event, person.handle, fhandle)
        #         return True

        return False

    def on_mouse_move(self, widget, event):
        """
        What to do if we move the mouse
        """
        dummy_widget = widget
        self._mouse_click = False
        if self.last_x is None or self.last_y is None:
            # while mouse is moving, we must update the tooltip based on person
            individual = self.life_line_chart_ancestor_graph.get_individual_from_position(
                event.x/self.zoom_level, event.y/self.zoom_level)
            self.mouse_x, self.mouse_y = event.x, event.y
            tooltip = ""
            if individual:
                tooltip = individual.individual.short_info_text
            self.set_tooltip_text(tooltip)
            return False

        #translate or rotate should happen
        if self.translating:
            #canonical_center = self.center_xy_from_delta([0, 0])
            self.center_delta_xy = (event.x - self.last_x,
                                    event.y - self.last_y)
        else:
            # get the angles of the two points from the center:
            start_angle = math.atan2(event.y - self.center_xy[1],
                                     event.x - self.center_xy[0])
            end_angle = math.atan2(self.last_y - self.center_xy[1],
                                   self.last_x - self.center_xy[0])
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
        (dummy_x, dummy_y,
         width, height) = alloc.x, alloc.y, alloc.width, alloc.height
        if delta is None:
            delta = self.center_delta_xy
        if self.form == FORM_CIRCLE:
            canvas_xy = width / 2 - delta[0], height / 2 - delta[1]
        elif self.form == FORM_HALFCIRCLE:
            canvas_xy = (width / 2 - delta[0],
                         height - self.CENTER - PAD_PX - delta[1])
        elif self.form == FORM_QUADRANT:
            canvas_xy = (self.CENTER + PAD_PX - delta[0],
                         height - self.CENTER - PAD_PX - delta[1])
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
            self.center_xy = self.center_xy[0] + \
                self.center_delta_xy[0], self.center_xy[1] + \
                self.center_delta_xy[1]
            self.center_delta_xy = 0, 0
        else:
            self.center_delta_xy = 0, 0
            #self.center_xy = self.center_xy[0] + self.center_delta_xy[0], self.center_xy[1] + self.center_delta_xy[1]

        self.last_x, self.last_y = None, None
        self.draw()
        self.queue_draw()
        return True

    def on_drag_begin(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        dummy_widget = widget
        dummy_data = data
        self.in_drag = True
        self.drag_source_set_icon_name('gramps-person')

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
        if not self._mouse_click_individual_id:
            return
        dummy_widget = widget
        dummy_time = time
        tgs = [x.name() for x in context.list_targets()]
        person = self.life_line_chart_ancestor_graph._instances[(
            'i', self._mouse_click_individual_id)]._gramps_person
        if person:
            if info == DdTargets.PERSON_LINK.app_id:
                data = (DdTargets.PERSON_LINK.drag_type,
                        id(self), person.get_handle(), 0)
                sel_data.set(sel_data.get_target(), 8, pickle.dumps(data))
            elif ('TEXT' in tgs or 'text/plain' in tgs) and info == 0:
                sel_data.set_text(self.format_helper.format_person(person,
                                                                   11), -1)

    def on_drag_data_received(self, widget, context, pos_x, pos_y,
                              sel_data, info, time):
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
                (dummy_drag_type, dummy_idval, handle,
                 dummy_val) = pickle.loads(sel_data.get_data())
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

#-------------------------------------------------------------------------
#
# LifeLineChartWidget
#
#-------------------------------------------------------------------------


class LifeLineChartWidget(LifeLineChartBaseWidget):
    """
    Interactive Fan Chart Widget.
    """

    def __init__(self, dbstate, uistate, callback_popup=None):
        """
        Fan Chart Widget. Handles visualization of data in self.data.
        See main() of LifeLineChartGramplet for example of model format.
        """
        self.rootpersonh = None
        self.formatting = None
        self.positioning = None
        self.filter = None
        self.zoom_level = 1.0
        self.zoom_level_backup = 1.0
        self.life_line_chart_ancestor_graph = None
        self.angle = {}
        self.childrenroot = []
        self.rootangle_rad = []
        self.menu = None
        self.data = {}
        self.dbstate = dbstate
        self.set_values(None, 5, BACKGROUND_GRAD_GEN, True, True, True, True,
                        'Sans', None, 0.5, FORM_CIRCLE,
                        False)
        LifeLineChartBaseWidget.__init__(
            self, dbstate, uistate, callback_popup)
        self.ic = get_dbdstate_instance_container(self.dbstate)

    def set_values(self, root_person_handle, maxgen, background, childring,
                   flipupsidedownname, twolinename, radialtext, fontdescr,
                   filtr, alpha_filter, form, showid):
        """
        Reset the values to be used:

        """

        reset = False
        if self.rootpersonh != root_person_handle:  # or self.filter != filtr:
            reset = True
            self.rootpersonh = root_person_handle
        new_filter = self.filter != filtr
        self.generations = maxgen
        self.radialtext = radialtext
        self.childring = childring
        self.twolinename = twolinename
        self.flipupsidedownname = flipupsidedownname
        self.background = background
        self.fontdescr = fontdescr
        self.filter = filtr
        self.alpha_filter = alpha_filter
        self.form = form
        self.showid = showid
        if self.rootpersonh:
            def plot():
                # x = GrampsIndividual(self.ic, self.dbstate, self.rootpersonh)
                if (reset or self.life_line_chart_ancestor_graph is None or self.positioning != self.life_line_chart_ancestor_graph._positioning or
                        self.formatting != self.life_line_chart_ancestor_graph._formatting or new_filter):

                    if reset or self.life_line_chart_ancestor_graph is None or self.positioning != self.life_line_chart_ancestor_graph._positioning:
                        self.life_line_chart_ancestor_graph = AncestorGraph(
                            positioning=self.positioning, formatting=self.formatting, instance_container=lambda: get_dbdstate_instance_container(self.dbstate))
                        root_individual = self.life_line_chart_ancestor_graph._instances[(
                            'i', self.rootpersonh)]

                        self.life_line_chart_ancestor_graph.select_individuals(
                            root_individual)
                        cof_family_id = None
                        if root_individual.child_of_family_id:
                            cof_family_id = root_individual.child_of_family_id[0]
                        self.life_line_chart_ancestor_graph.place_selected_individuals(
                            root_individual, None, None, self.life_line_chart_ancestor_graph._instances[('f', cof_family_id)])
                        try:
                            self.life_line_chart_ancestor_graph.modify_layout(
                                self.rootpersonh)
                        except:
                            pass

                        #backup color
                        for gir in self.life_line_chart_ancestor_graph.graphical_individual_representations:
                            gir.color_backup = gir.color
                    else:
                        self.life_line_chart_ancestor_graph.clear_svg_items()
                        self.life_line_chart_ancestor_graph._formatting = deepcopy(
                            self.formatting)

                    def filter(individual_id):
                        if self.filter:
                            person = self.life_line_chart_ancestor_graph._instances[(
                                'i', individual_id)]._gramps_person
                            if not self.filter.match(person.handle, self.dbstate.db):
                                return True
                        return False
                    for gir in self.life_line_chart_ancestor_graph.graphical_individual_representations:
                        if filter(gir.individual_id):
                            gir.color = (220, 220, 220)
                        else:
                            gir.color = gir.color_backup
                    self.life_line_chart_ancestor_graph.define_svg_items()
            plot()

    def nrgen(self):
        """
        return the generation if we have a person to draw
        """
        #compute the number of generations present
        for generation in range(self.generations - 1, 0, -1):
            for idx in range(len(self.data[generation])):
                (person, dummy_parents, dummy_child,
                 dummy_userdata) = self.data[generation][idx]
                if person:
                    return generation
        return 1

    def halfdist(self):
        """
        Compute the half radius of the circle
        """
        return (PIXELS_PER_GENERATION * self.nrgen() +
                self.CENTER + BORDER_EDGE_WIDTH)

    def draw(self, ctx=None, scale=1.):
        """
        The main method to do the drawing.
        If ctx is given, we assume we draw draw raw on the cairo context ctx
        To draw in GTK3 and use the allocation, set ctx=None.
        Note: when drawing for display, to counter a Gtk issue with scrolling
        or resizing the drawing window, we draw on a surface, then copy to the
        drawing context when the Gtk 'draw' signal arrives.
        """
        # first do size request of what we will need
        if not ctx:  # Display
            graph = self.life_line_chart_ancestor_graph
            size_w_a = int(graph.get_full_width()*self.zoom_level)
            size_h_a = int(graph.get_full_height()*self.zoom_level)
            #size_w_a = max(size_w_a, self.get_allocated_width())
            #size_h_a = max(size_h_a, self.get_allocated_height())
            self.set_size_request(size_w_a, size_h_a)
            size_w = self.get_allocated_width()
            size_h = self.get_allocated_height()
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                              size_w_a, size_h_a)
            ctx = cairo.Context(self.surface)
            #self.center_xy = self.center_xy_from_delta()
            #ctx.translate(self.center_xy[0] + self.center_delta_xy[0], self.center_xy[1] + self.center_delta_xy[1])
            ctx.scale(self.zoom_level, self.zoom_level)

            visible_range = self.scrolledwindow.get_clip(
            ).width, self.scrolledwindow.get_clip().height
            sb_h_adj = self.scrolledwindow.get_hscrollbar().get_adjustment()
            sb_v_adj = self.scrolledwindow.get_vscrollbar().get_adjustment()
            #visible_range = 0,0
            sb_h_adj.set_value((self.zoom_level / self.zoom_level_backup) * (
                visible_range[0] * 0.5 + sb_h_adj.get_value()) - visible_range[0] * 0.5)
            sb_v_adj.set_value((self.zoom_level / self.zoom_level_backup) * (
                visible_range[1] * 0.5 + sb_v_adj.get_value()) - visible_range[1] * 0.5)
            self.zoom_level_backup = self.zoom_level
        else:  # printing
            # ??
            #ctx.translate(*self.center_xy)
            ctx.scale(scale, scale)

        additional_items = []
        for key, value in self.life_line_chart_ancestor_graph.additional_graphical_items.items():
            additional_items += value
        sorted_individuals = [(gr.get_birth_event()['ordinal_value'], index, gr) for index, gr in enumerate(
            self.life_line_chart_ancestor_graph.graphical_individual_representations)]
        sorted_individuals.sort()
        sorted_individual_items = []
        for _, index, graphical_individual_representation in sorted_individuals:
            sorted_individual_items += graphical_individual_representation.items
        for item in additional_items + sorted_individual_items:

                def text_function(ctx, text, x, y, rotation=0, fontName="Arial", fontSize=10, verticalPadding=0, vertical_offset=0, horizontal_offset=0, bold=False, align='center', position='middle'):

                    rotation = rotation * math.pi / 180

                    if bold:
                        ctx.select_font_face(
                            fontName, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    else:
                        ctx.select_font_face(
                            fontName, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(fontSize)

                    fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()

                    ctx.save()
                    ctx.translate(x, y)
                    ctx.rotate(rotation)
                    ctx.translate(horizontal_offset, vertical_offset)

                    lines = text.split("\n")

                    for i, line in enumerate(lines):
                        xoff, yoff, textWidth, textHeight = ctx.text_extents(line)[
                            :4]

                        if align == 'middle':
                            offx = -textWidth / 2.0
                        elif align == 'end':
                            offx = -textWidth
                        else:
                            offx = 0

                        if position == 'middle':
                            offy = (fheight / 2.0) + \
                                (fheight + verticalPadding) * i
                        else:
                            offy = (fheight + verticalPadding) * i

                        ctx.move_to(offx, offy)
                        ctx.show_text(line)

                    ctx.restore()

                if item['type'] == 'text':
                    args = item['config']
                    ctx.set_source_rgb(0, 0, 0)
                    #ctx.set_font_size(float(args['font_size'][:-2]))
                    # ctx.select_font_face("Arial",
                    #                     cairo.FONT_SLANT_NORMAL,
                    #                     cairo.FONT_WEIGHT_NORMAL)
                    font_size = item['font_size']
                    if type(font_size) == str:
                        if font_size.endswith('px') or font_size.endswith('pt'):
                            font_size = float(font_size[:-2])
                    rotation = 0
                    if 'transform' in args and args['transform'].startswith('rotate('):
                        rotation = float(args['transform'][7:-1].split(',')[0])
                    vertical_offset = 0
                    if 'dy' in args:
                        if args['dy'][0].endswith('px') or args['dy'][0].endswith('pt'):
                            vertical_offset = float(args['dy'][0][:-2])
                        else:
                            vertical_offset = float(args['dy'][0])
                    horizontal_offset = 0
                    if 'dx' in args:
                        if args['dx'][0].endswith('px') or args['dx'][0].endswith('pt'):
                            horizontal_offset = float(args['dx'][0][:-2])
                        else:
                            horizontal_offset = float(args['dx'][0])
                    anchor = args.get('text-anchor')
                    if not anchor:
                        anchor = 'start'
                    text_function(
                        ctx,
                        args['text'],
                        args['insert'][0],
                        args['insert'][1],
                        rotation,
                        fontSize=font_size,
                        fontName=item['font_name'],
                        vertical_offset=vertical_offset,
                        horizontal_offset=horizontal_offset,
                        align=anchor,
                        position='top')
                    # ctx.save()
                    # ctx.
                    # if 'text-anchor' in args and args['text-anchor'] == 'middle':
                    #     x_bearing, y_bearing, width, height = ctx.text_extents(args['text'])[:4]
                    #     ctx.move_to(args['insert'][0] - width/2, args['insert'][1])
                    #     ctx.show_text(args['text'])
                    # else:
                    #     ctx.move_to(*args['insert'])
                    #     ctx.show_text(args['text'])
                    # cr.restore()
                    #
                    # #args = deepcopy(item['config'])
                    # #args['insert'] = (args['insert'][0], args['insert'][1])
                    # svg_text = svg_document.text(
                    #     **args)
                    # x = svg_document.add(svg_text)
                elif item['type'] == 'path':
                    arguments = deepcopy(item['config']['arguments'])
                    arguments = [individual_id for individual_id in arguments]
                    if self.formatting['fade_individual_color'] and 'color_pos' in item:
                        cp = item['color_pos']

                        #ctx.set_source_rgb(*[c/255. for c in item['color']])
                        #lg3 = cairo.LinearGradient(0, item['color_pos'][0],  0, item['color_pos'][1])
                        lg3 = cairo.LinearGradient(
                            0, item['color_pos'][0], 0, item['color_pos'][1])
                        #fill = svg_document.linearGradient(("0", str(item['color_pos'][0])+""), ("0", str(item['color_pos'][1])+""), gradientUnits='userSpaceOnUse')
                        lg3.add_color_stop_rgba(
                            0, *[c/255. for c in item['color']], 1)
                        lg3.add_color_stop_rgba(1, 0, 0, 0, 1)

                        ctx.set_source(lg3)
                        if item['config']['type'] == 'Line':
                            ctx.move_to(arguments[0].real, arguments[0].imag)
                            ctx.set_line_width(item['stroke_width'])
                            ctx.line_to(arguments[1].real, arguments[1].imag)
                            ctx.stroke()
                        elif item['config']['type'] == 'CubicBezier':
                            ctx.move_to(arguments[0].real, arguments[0].imag)
                            ctx.set_line_width(item['stroke_width'])
                            ctx.curve_to(arguments[1].real, arguments[1].imag, arguments[2].real,
                                         arguments[2].imag, arguments[3].real, arguments[3].imag)
                            ctx.stroke()
                    else:
                        if item['config']['type'] == 'Line':
                            ctx.move_to(arguments[0].real, arguments[0].imag)
                            ctx.set_source_rgb(
                                *[c/255. for c in item['color']])
                            ctx.set_line_width(item['stroke_width'])
                            ctx.line_to(arguments[1].real, arguments[1].imag)
                            ctx.stroke()
                        elif item['config']['type'] == 'CubicBezier':

                            ctx.move_to(arguments[0].real, arguments[0].imag)
                            ctx.set_source_rgb(
                                *[c/255. for c in item['color']])
                            ctx.set_line_width(item['stroke_width'])
                            ctx.curve_to(arguments[1].real, arguments[1].imag, arguments[2].real,
                                         arguments[2].imag, arguments[3].real, arguments[3].imag)
                            ctx.stroke()
                elif item['type'] == 'textPath':
                    from math import cos, sin, atan2, pi

                    # def distance(x1, y1, x2, y2):
                    #     """Get the distance between two points."""
                    #     return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                    # def point_angle(cx, cy, px, py):
                    #     """Return angle between x axis and point knowing given center."""
                    #     return atan2(py - cy, px - cx)

                    # def point_following_path(path, width):
                    #     """Get the point at ``width`` distance on ``path``."""
                    #     total_length = 0
                    #     for item in path:
                    #         if item[0] == cairo.PATH_MOVE_TO:
                    #             old_point = item[1]
                    #         elif item[0] == cairo.PATH_LINE_TO:
                    #             new_point = item[1]
                    #             length = distance(
                    #                 old_point[0], old_point[1], new_point[0], new_point[1])
                    #             total_length += length
                    #             if total_length < width:
                    #                 old_point = new_point
                    #             else:
                    #                 length -= total_length - width
                    #                 angle = point_angle(
                    #                     old_point[0], old_point[1], new_point[0], new_point[1])
                    #                 x = cos(angle) * length + old_point[0]
                    #                 y = sin(angle) * length + old_point[1]
                    #                 return x, y

                    # def zip_letters(xl, yl, dxl, dyl, rl, word):
                    #     """Returns a list with the current letter's positions (x, y and rotation).
                    #     E.g.: for letter 'L' with positions x = 10, y = 20 and rotation = 30:
                    #     >>> [[10, 20, 30], 'L']
                    #     Store the last value of each position and pop the first one in order to
                    #     avoid setting an x,y or rotation value that have already been used.
                    #     """
                    #     return (
                    #         ([pl.pop(0) if pl else None for pl in (xl, yl, dxl, dyl, rl)], char)
                    #         for char in word)

                    # x, y, dx, dy, rotate = [], [], [], [], [0]
                    # if 'x' in node:
                    #     x = [size(surface, i, 'x')
                    #         for i in normalize(node['x']).strip().split(' ')]
                    # if 'y' in node:
                    #     y = [size(surface, i, 'y')
                    #         for i in normalize(node['y']).strip().split(' ')]
                    # if 'dx' in node:
                    #     dx = [size(surface, i, 'x')
                    #         for i in normalize(node['dx']).strip().split(' ')]
                    # if 'dy' in node:
                    #     dy = [size(surface, i, 'y')
                    #         for i in normalize(node['dy']).strip().split(' ')]
                    # if 'rotate' in node:
                    #     rotate = [radians(float(i)) if i else 0
                    #             for i in normalize(node['rotate']).strip().split(' ')]
                    # last_r = rotate[-1]
                    # letters_positions = zip_letters(x, y, dx, dy, rotate, node.text)
                    # def draw_t_a_p():
                    #
                    #     for i, ((x, y, dx, dy, r), letter) in enumerate(letters_positions):
                    #         if x:
                    #             surface.cursor_d_position[0] = 0
                    #         if y:
                    #             surface.cursor_d_position[1] = 0
                    #         surface.cursor_d_position[0] += dx or 0
                    #         surface.cursor_d_position[1] += dy or 0
                    #         text_extents = surface.context.text_extents(letter)
                    #         extents = text_extents[4]
                    #         if text_path:
                    #             start = surface.text_path_width + surface.cursor_d_position[0]
                    #             start_point = point_following_path(cairo_path, start)
                    #             middle = start + extents / 2
                    #             middle_point = point_following_path(cairo_path, middle)
                    #             end = start + extents
                    #             end_point = point_following_path(cairo_path, end)
                    #             if i:
                    #                 extents += letter_spacing
                    #             surface.text_path_width += extents
                    #             if not all((start_point, middle_point, end_point)):
                    #                 continue
                    #             if not 0 <= middle <= length:
                    #                 continue
                    #             surface.context.save()
                    #             surface.context.translate(*start_point)
                    #             surface.context.rotate(point_angle(*(start_point + end_point)))
                    #             surface.context.translate(0, surface.cursor_d_position[1])
                    #             surface.context.move_to(0, 0)
                    #             bounding_box = extend_bounding_box(
                    #                 bounding_box, ((end_point[0], text_extents[3]),))

                    # def pathtext(g, path, txt, offset) :
                    #     "draws the characters of txt along the specified path in the Context g, using its" \
                    #     " current font and other rendering settings. offset is the initial character placement" \
                    #     " offset from the start of the path."
                    #     #path = path.flatten() # ensure all straight-line segments
                    #     curch = 0 # index into txt
                    #     setdist = offset # distance at which to place next char
                    #     pathdist = 0
                    #     for seg in path.segments :
                    #         curpos = None
                    #         ovr = 0
                    #         for pt in tuple(seg.points) + ((), (seg.points[0],))[seg.closed] :
                    #             assert not pt.off
                    #             prevpos = curpos
                    #             curpos = pt.pt
                    #             if prevpos != None :
                    #                 delta = curpos - prevpos
                    #                 dist = abs(delta) # length of line segment
                    #                 if dist != 0 :
                    #                     ds = delta / dist * ovr
                    #                     cp = g.user_to_device(prevpos + ds)
                    #                     pathdist += dist # accumulate length of path
                    #                     while True :
                    #                         if setdist > pathdist :
                    #                             # no more room to place a character
                    #                             ovr = setdist - pathdist
                    #                             # deduct off placement of first char on next line segment
                    #                             break
                    #                         #end if
                    #                         if curch == len(txt) :
                    #                             # no more characters to place
                    #                             break
                    #                         # place another character along this line segment
                    #                         ch = txt[curch] # FIXME: should not split off trailing diacritics
                    #                         curch += 1
                    #                         text_extents = g.text_extents(ch)
                    #                         charbounds = Vector(text_extents.x_advance, text_extents.y_bearing)
                    #                         g.save()
                    #                         g.transform \
                    #                         (
                    #                                 Matrix.translate
                    #                                 (
                    #                                     g.device_to_user(cp) + delta * charbounds / 2 / dist
                    #                                 ) # midpoint of character back to character position
                    #                             *
                    #                                 Matrix.rotate(delta.angle())
                    #                                 # rotate about midpoint of character
                    #                             *
                    #                                 Matrix.translate(- charbounds / 2)
                    #                                 # midpoint of character to origin
                    #                         )
                    #                         g.show_text(ch)
                    #                         cp = g.user_to_device(g.current_point)
                    #                         g.restore()
                    #                         setdist += charbounds.x # update distance travelled along path
                    #                     #end while
                    #                 #end if
                    #             #end if
                    #         #end for
                    #     #end for
                    # #end pathtext
                    import svgpathtools
                    from cmath import phase

                    def draw_text_along_path(ctx, textspans, start_x, start_y, cp1_x, cp1_y, cp2_x, cp2_y, end_x, end_y, show_path_line=True):
                        def warpPath(ctx, function):
                            first = True

                            for type, points in ctx.copy_path_flat():
                                if type == cairo.PATH_MOVE_TO:
                                    if first:
                                        ctx.new_path()
                                        first = False
                                    x, y = function(*points)
                                    ctx.move_to(x, y)

                                elif type == cairo.PATH_LINE_TO:
                                    x, y = function(*points)
                                    ctx.line_to(x, y)

                                elif type == cairo.PATH_CURVE_TO:
                                    x1, y1, x2, y2, x3, y3 = points
                                    x1, y1 = function(x1, y1)
                                    x2, y2 = function(x2, y2)
                                    x3, y3 = function(x3, y3)
                                    ctx.curve_to(x1, y1, x2, y2, x3, y3)

                                elif type == cairo.PATH_CLOSE_PATH:
                                    ctx.close_path()

                        def follow_path(path_length, path, te, x, y):
                            #p = x/path_length
                            p = path.ilength(
                                min(x, path_length), error=1e-3, min_depth=2)
                            return path.point(p).real - path.normal(p).real*(y-te.y_bearing/2), path.point(p).imag - path.normal(p).imag*(y-te.y_bearing/2)

                        def xxx(path_length, ctx, path, textspans, vertical_offset, horizontal_offset):
                            x_pos = horizontal_offset
                            for text, args in textspans:
                                if 'dx' in args:
                                    x_pos += float(args['dx'][0])
                                for character in text:
                                    p = path.ilength(
                                        min(x_pos, path_length), error=1e-3, min_depth=2)
                                    character_pos = path.point(
                                        p) - path.normal(p) * vertical_offset*0
                                    x, y = (character_pos.real,
                                            character_pos.imag)
                                    r = phase(path.normal(p))/pi*180 + 90
                                    ctx.save()

                                    text_function(
                                        ctx,
                                        character,
                                        x,
                                        y,
                                        r,
                                        fontSize=item['font_size'],
                                        fontName=item['font_name'],
                                        vertical_offset=vertical_offset,
                                        horizontal_offset=horizontal_offset,
                                        align='start',
                                        position='left',
                                        bold='style' in args and 'bold' in args['style'])
                                    ctx.select_font_face(
                                        item['font_name'], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                                    ctx.set_font_size(font_size)
                                    te = ctx.text_extents(character,)
                                    ctx.restore()
                                    x_pos += te.x_advance

                                te = ctx.text_extents(' ',)
                                x_pos += te.x_advance
                        svg_path = svgpathtools.CubicBezier(
                            start_x + start_y*1j, cp1_x + cp1_y*1j, cp2_x + cp2_y*1j, end_x + end_y*1j)
                        # if show_path_line:
                        #     ctx.move_to(start_x, start_y)
                        #     ctx.curve_to(cp1_x, cp1_y, cp2_x, cp2_y, end_x, end_y)
                        #     ctx.stroke()
                        #path = ctx.copy_path_flat()

                        #ctx.new_path()
                        #ctx.move_to(0, 0)
                        #ctx.text_path(text)
                        path_length = svg_path.length(error=1e-3, min_depth=2)

                        ##pathtext(ctx, path, text, 0)

                        vertical_offset = 0
                        if 'dy' in item['config']:
                            if item['config']['dy'][0].endswith('px') or item['config']['dy'][0].endswith('pt'):
                                vertical_offset = float(
                                    item['config']['dy'][0][:-2])
                            else:
                                vertical_offset = float(
                                    item['config']['dy'][0])
                        horizontal_offset = 0
                        if 'dx' in args:
                            if args['dx'][0].endswith('px') or args['dx'][0].endswith('pt'):
                                horizontal_offset = float(args['dx'][0][:-2])
                            else:
                                horizontal_offset = float(args['dx'][0])
                        xxx(path_length, ctx, svg_path,
                            item['spans'], vertical_offset, horizontal_offset)
                        #te=ctx.text_extents(text)

                        #warpPath(ctx, lambda x, y: follow_path(path_length, svg_path, te, x, y))
                        ctx.fill()

                    args_path = item['path']
                    args_text = item['config']

                    if args_path['type'] == 'CubicBezier':
                        arguments = deepcopy(args_path['arguments'])
                        ctx.new_path()
                        ctx.set_line_width(0.1)
                        #path = svgpathtools.CubicBezier(*arguments)
                        ctx.set_source_rgb(0, 0, 0)

                        draw_text_along_path(ctx, item['spans'][0][0], arguments[0].real, arguments[0].imag, arguments[1].real,
                                             arguments[1].imag, arguments[2].real, arguments[2].imag, arguments[3].real, arguments[3].imag)
                        # ctx.move_to(arguments[0].real, arguments[0].imag)
                        # ctx.set_source_rgb(*[c/255. for c in graphical_individual_representation.color])
                        # ctx.set_line_width(self.life_line_chart_ancestor_graph._formatting['line_thickness'])
                        # ctx.curve_to()
                        # ctx.text_path("textxxxxxx")
                        # path = ctx.copy_path()
                        #ctx.curve_to(arguments[1].real, arguments[1].imag, arguments[2].real, arguments[2].imag, arguments[3].real, arguments[3].imag)
                        #warpPath(ctx, curl)
                        #ctx.close_path()
                        #ctx.fill()
                        #ctx.stroke()
                    #args_path['arguments']
                    pass
                    # svg_text = svg_document.text(
                    #     **args_text)
                    # if args_path['type'] == 'Line':
                    #     constructor_function = Line
                    # elif args_path['type'] == 'CubicBezier':
                    #     constructor_function = CubicBezier
                    # svg_path = Path(constructor_function(*args_path['arguments']))
                    # y = svg_document.path( svg_path.d(), fill = 'none')
                    # svg_document.add(y)
                    # #x = svg_document.add(svg_text)
                    # x = svg_document.add(svgwrite.text.Text('', dy = [args_text['dy']], font_size = args_text['font_size']))
                    # t = svgwrite.text.TextPath(y, text = args_text['text'])
                    # for span in item['spans']:
                    #     t.add(svg_document.tspan(span[0], **span[1]))
                    # x.add(t)

                elif item['type'] == 'image':
                    def draw_image(ctx, image, left, top, width, height):
                        """Draw a scaled image on a given context."""
                        image_surface = cairo.ImageSurface.create_from_png(
                            image)
                        # calculate proportional scaling
                        img_height = image_surface.get_height()
                        img_width = image_surface.get_width()
                        width_ratio = float(width) / float(img_width)
                        height_ratio = float(height) / float(img_height)
                        scale_xy = min(height_ratio, width_ratio)
                        if height_ratio > scale_xy:
                            top -= (img_height * scale_xy - height)/2
                        if width_ratio - scale_xy:
                            left -= (img_width * scale_xy - width)/2
                        # scale image and add it
                        ctx.save()
                        ctx.translate(left, top)
                        ctx.scale(scale_xy, scale_xy)
                        ctx.set_source_surface(image_surface)

                        ctx.paint()
                        ctx.restore()
                    import os
                    draw_image(ctx, item['filename'], *item['config']
                               ['insert'], *item['config']['size'])
                    # marriage_pos and 'spouse' in positions[individual_id]['marriage']:
                    #m_pos_x = (positions[positions[individual_id]['marriage']['spouse']]['x_position'] + x_pos)/2
                    #svg_document.add(svg_document.use(image_def.get_iri(), **item['config']))
                    pass

                elif item['type'] == 'rect':
                    pass
                    #this_rect = svg_document.rect(**item['config'])

                    #insert=(rect[0], rect[1]), size = (rect[2]-rect[0], rect[3]-rect[1]), fill = 'none')
                    #svg_document.add(this_rect)

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
        self._mouse_click = False
        self.draw()
        self.queue_draw()


class LifeLineChartGrampsGUI:
    """ class for functions lifelinechart GUI elements will need in Gramps
    """

    def __init__(self, on_childmenu_changed):
        """
        Common part of GUI that shows Fan Chart, needs to know what to do if
        one moves via Fan Ch    def set_lifeline(self, lifeline):art to a new person
        on_childmenu_changed: in popup, function called on moving
                              to a new person
        """
        self.lifeline = None
        self.menu = None
        self.twolinename = False
        self.radialtext = None
        self.maxgen = 8
        self.childring = 0
        self.showid = False
        self.form = FORM_CIRCLE
        self.alpha_filter = 0.5
        self.filter = None
        self.background = BACKGROUND_GRAD_GEN
        self.on_childmenu_changed = on_childmenu_changed
        self.format_helper = FormattingHelper(self.dbstate, self.uistate)
        self.uistate.connect('font-changed', self.reload_symbols)

    def reload_symbols(self):
        self.format_helper.reload_symbols()

    def set_lifeline(self, lifeline):
        """
        Set the lifelinechartwidget to work on
        """
        self.lifeline = lifeline
        self.lifeline.format_helper = self.format_helper
        self.lifeline.goto = self.on_childmenu_changed

    def main(self):
        """
        Fill the data structures with the active data. This initializes all
        data.
        """
        root_person_handle = self.get_active('Person')
        self.lifeline.set_values(root_person_handle, self.maxgen, self.background,
                                 self.childring, False,
                                 self.twolinename, self.radialtext, self.fonttype,
                                 self.generic_filter,
                                 self.alpha_filter, self.form, self.showid)
        self.lifeline.reset()
        self.lifeline.draw()
        self.lifeline.queue_draw()

    def on_popup(self, obj, event, person_handle, family_handle=None):
        """
        Builds the full menu (including Siblings, Spouses, Children,
        and Parents) with navigation.
        """
        dummy_obj = obj
        #store menu for GTK3 to avoid it being destroyed before showing
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

        edit_item = Gtk.MenuItem.new_with_mnemonic(_('_Edit'))
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
            #see if a reorder button is needed
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

        clipboard_item = Gtk.MenuItem.new_with_mnemonic(_('_Copy'))
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
                other_families = [self.dbstate.db.get_family_from_handle(fam_id)
                                  for fam_id in parent.get_family_handle_list()
                                  if fam_id not in pfam_list]
                for step_fam in other_families:
                    fam_stepsiblings = [sib_ref.ref
                                        for sib_ref in
                                        step_fam.get_child_ref_list()
                                        if not sib_ref.ref ==
                                        person.get_handle()]
                    if fam_stepsiblings:
                        step_siblings.append(fam_stepsiblings)

        # Add siblings sub-menu with a bar between each siblings group
        if siblings or step_siblings:
            item.set_submenu(Gtk.Menu())
            sib_menu = item.get_submenu()
            sib_menu.set_reserve_toggle_size(False)
            sibs = [siblings]+step_siblings
            for sib_group in sibs:
                for sib_id in sib_group:
                    sib = self.dbstate.db.get_person_from_handle(sib_id)
                    if not sib:
                        continue
                    if find_children(self.dbstate.db, sib):
                        thelabel = escape(name_displayer.display(sib))
                        label = Gtk.Label(label='<b><i>%s</i></b>' % thelabel)
                    else:
                        thelabel = escape(name_displayer.display(sib))
                        label = Gtk.Label(label=thelabel)
                    sib_item = Gtk.MenuItem()
                    label.set_use_markup(True)
                    label.show()
                    label.set_alignment(0, 0)
                    sib_item.add(label)
                    linked_persons.append(sib_id)
                    sib_item.connect("activate", self.on_childmenu_changed,
                                     sib_id)
                    sib_item.show()
                    sib_menu.append(sib_item)
                if sibs.index(sib_group) < len(sibs)-1:
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
                label = Gtk.Label(label='<b><i>%s</i></b>' % thelabel)
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            child_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate", self.on_childmenu_changed,
                               child_handle)
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
                label = Gtk.Label(label='<b><i>%s</i></b>' % thelabel)
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
            #show an add button
            add_item = Gtk.MenuItem.new_with_mnemonic(_('_Add'))
            add_item.connect("activate", self.on_add_parents, person_handle)
            add_item.show()
            par_menu.append(add_item)

        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db, person):
            #if p_id in linked_persons:
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

        #we now construct an add menu
        item = Gtk.MenuItem.new_with_mnemonic(_("_Add"))
        item.set_submenu(Gtk.Menu())
        add_menu = item.get_submenu()
        add_menu.set_reserve_toggle_size(False)
        if family_handle:
            # allow to add a child to this family
            add_child_item = Gtk.MenuItem()
            add_child_item.set_label(_("Add child to family"))
            add_child_item.connect("activate", self.add_child_to_fam_cb,
                                   family_handle)
            add_child_item.show()
            add_menu.append(add_child_item)
        elif person_handle:
            #allow to add a partner to this person
            add_partner_item = Gtk.MenuItem()
            add_partner_item.set_label(_("Add partner to person"))
            add_partner_item.connect("activate", self.add_partner_to_pers_cb,
                                     person_handle)
            add_partner_item.show()
            add_menu.append(add_partner_item)

        add_pers_item = Gtk.MenuItem()
        add_pers_item.set_label(_("Add a person"))
        add_pers_item.connect("activate", self.add_person_cb)
        add_pers_item.show()
        add_menu.append(add_pers_item)
        item.show()
        menu.append(item)

        menu.popup(None, None, None, None, event.button, event.time)
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
        #the editor requires a surname
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
        def callback(x): return self.callback_add_child(x, family_handle)
        person = Person()
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        family = self.dbstate.db.get_family_from_handle(family_handle)
        father = self.dbstate.db.get_person_from_handle(
            family.get_father_handle())
        if father:
            preset_name(father, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person,
                       callback=callback)
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
            #add parentref to child
            person.add_parent_family_handle(family_handle)
            #default relationship is used
            self.dbstate.db.commit_person(person, trans)
            #add child to family
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
            cbx = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                                                Gdk.SELECTION_CLIPBOARD)
            cbx.set_text(self.format_helper.format_person(person, 11), -1)
            return True
        return False
