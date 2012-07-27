# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009       Yevgeny Zegzda <ezegjda@ya.ru>
# Copyright (C) 2010       Nick Hall
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _
from gen.ggettext import ngettext
from cgi import escape
import math
import sys
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import PangoCairo

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
from gui.views.navigationview import NavigationView
from gui.editors import FilterEditor
from gen.display.name import displayer as name_displayer
from gen.utils.alive import probably_alive
from gen.utils.file import media_path_full
from gen.utils.db import find_children, find_parents, find_witnessed_people
from libformatting import FormattingHelper
from gui.thumbnails import get_thumbnail_path
from gen.errors import WindowActiveError
from gui.editors import EditPerson, EditFamily
from gui.ddtargets import DdTargets
import cPickle as pickle
from gen.config import config
from gui.views.bookmarks import PersonBookmarks
from gen.const import CUSTOM_FILTERS
from gen.constfunc import is_quartz, win
from gui.dialog import RunDatabaseRepair, ErrorDialog
import gui.utils

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if is_quartz():
    CAIRO_AVAILABLE = False
else:
    try:
        import cairo
        CAIRO_AVAILABLE = True
    except ImportError:
        CAIRO_AVAILABLE = False

_PERSON = "p"
_BORN = _('short for born|b.')
_DIED = _('short for died|d.')
_BAPT = _('short for baptized|bap.')
_CHRI = _('short for christened|chr.')
_BURI = _('short for buried|bur.')
_CREM = _('short for cremated|crem.')

class _PersonWidgetBase(Gtk.DrawingArea):
    """
    Defualt set up for person widgets.
    Set up drag options and button release events.
    """
    def __init__(self, view, format_helper, person):
        GObject.GObject.__init__(self)
        self.view = view
        self.format_helper = format_helper
        self.person = person
        self.force_mouse_over = False
        if self.person:
            self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
            self.connect("button-release-event", self.cb_on_button_release)
            self.connect("drag_data_get", self.cb_drag_data_get)
            self.connect("drag_begin", self.cb_drag_begin)
            # Enable drag
            self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                [],
                                Gdk.DragAction.COPY)
            tglist = Gtk.TargetList.new([])
            tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                       DdTargets.PERSON_LINK.target_flags,
                       DdTargets.PERSON_LINK.app_id)
            tglist.add_text_targets(0L)
            self.drag_source_set_target_list(tglist)

    def cb_drag_begin(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        self.drag_source_set_icon_stock('gramps-person')

    def cb_drag_data_get(self, widget, context, sel_data, info, time):
        """
        Returned parameters after drag.
        Specified for 'person-link', for others return text info about person.
        """
        #TODO GTK3 Still to convert when pedigreeview works again
        if sel_data.target == DdTargets.PERSON_LINK.drag_type:
            data = (DdTargets.PERSON_LINK.drag_type,
                    id(self), self.person.get_handle(), 0)
            sel_data.set(sel_data.target, 8, pickle.dumps(data))
        else:
            sel_data.set(sel_data.target, 8,
                         self.format_helper.format_person(self.person, 11))

    def cb_on_button_release(self, widget, event):
        """
        Defualt action for release event from mouse.
        Change active person to current.
        """
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_RELEASE:
            self.view.cb_childmenu_changed(None, self.person.get_handle())
            return True
        return False
        
    def get_image(self, dbstate, person):
        """
        Return a thumbnail image for the given person.
        """
        image_path = None
        media_list = person.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            obj = dbstate.db.get_object_from_handle(
                object_handle)
            if obj:
                mtype = obj.get_mime_type()
                if mtype and mtype[0:5] == "image":
                    image_path = get_thumbnail_path(
                                media_path_full(
                                            dbstate.db,
                                            obj.get_path()),
                                rectangle=photo.get_rectangle())
        return image_path


class PersonBoxWidgetCairo(_PersonWidgetBase):
    """Draw person box using cairo library"""
    def __init__(self, view, format_helper, dbstate, person, alive, maxlines,
                image=None):
        _PersonWidgetBase.__init__(self, view, format_helper, person)
        # Required for popup menu
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        # Required for tooltip and mouse-over
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        # Required for tooltip and mouse-over
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.alive = alive
        self.maxlines = maxlines
        self.hightlight = False
##TODO GTK3: event deprecated , instead if still needed connect to event, 
## and check if event is an expose event.
##        self.connect("expose_event", self.expose)
        if not win():
            self.connect("realize", self.realize)
        self.text = ""
        if self.person:
            self.text = self.format_helper.format_person(self.person,
                                                         self.maxlines, True)
            if alive and self.person.get_gender() == gen.lib.Person.MALE:
                self.bgcolor = (185/256.0, 207/256.0, 231/256.0)
                self.bordercolor = (32/256.0, 74/256.0, 135/256.0)
            elif alive and self.person.get_gender() == gen.lib.Person.FEMALE:
                self.bgcolor = (255/256.0, 205/256.0, 241/256.0)
                self.bordercolor = (135/256.0, 32/256.0, 106/256.0)
            elif alive:
                self.bgcolor = (244/256.0, 220/256.0, 183/256.0)
                self.bordercolor = (143/256.0, 89/256.0, 2/256.0)
            elif self.person.get_gender() == gen.lib.Person.MALE:
                self.bgcolor = (185/256.0, 207/256.0, 231/256.0)
                self.bordercolor = (0, 0, 0)
            elif self.person.get_gender() == gen.lib.Person.FEMALE:
                self.bgcolor = (255/256.0, 205/256.0, 241/256.0)
                self.bordercolor = (0, 0, 0)
            else:
                self.bgcolor = (244/256.0, 220/256.0, 183/256.0)
                self.bordercolor = (0, 0, 0)
        else:
            self.bgcolor = (211/256.0, 215/256.0, 207/256.0)
            self.bordercolor = (0, 0, 0)

        self.img_surf = None    
        if image:
            image_path = self.get_image(dbstate, person)
            if isinstance(image_path, unicode):
                image_path = image_path.encode(sys.getfilesystemencoding())
            if image_path and os.path.exists(image_path):
                self.img_surf = cairo.ImageSurface.create_from_png(image_path)

        # enable mouse-over
        self.connect("enter-notify-event", self.cb_on_enter)
        # enable mouse-out
        self.connect("leave-notify-event", self.cb_on_leave)
        self.set_size_request(120, 25)
        # GTK object use in realize and expose methods
        self.context = None
        self.textlayout = None

    def cb_on_enter(self, widget, event):
        """On mouse-over highlight border"""
        if self.person or self.force_mouse_over:
            self.hightlight = True
            self.queue_draw()

    def cb_on_leave(self, widget, event):
        """On mouse-out normal border"""
        self.hightlight = False
        self.queue_draw()

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display. Print text and resize element.
        """
        # pylint: disable-msg=E1101
        self.context = self.get_root_window().cairo_create()
        self.textlayout = PangoCairo.create_layout(self.context)
        self.textlayout.set_font_description(self.get_style().font_desc)
        self.textlayout.set_markup(self.text)
        size = self.textlayout.get_pixel_size()
        xmin = size[0] + 12
        ymin = size[1] + 11
        if self.img_surf:
            xmin += self.img_surf.get_width()
            ymin = max(ymin, self.img_surf.get_height()+4)
        self.set_size_request(max(xmin, 120), max(ymin, 25))

    def expose(self, widget, event):
        """
        Redrawing the contents of the widget.
        Creat new cairo object and draw in it all (borders, background and etc.)
        witout text.
        """
        # pylint: disable-msg=E1101
        if win():
            self.context = self.window.cairo_create()
            self.textlayout = self.context.create_layout()
            self.textlayout.set_font_description(self.get_style().font_desc)
            self.textlayout.set_markup(self.text)
            size = self.textlayout.get_pixel_size()
            xmin = size[0] + 12
            ymin = size[1] + 11
            if self.img_surf:
                xmin += self.img_surf.get_width()
                ymin = max(ymin, self.img_surf.get_height()+4)
            self.set_size_request(max(xmin, 120), max(ymin, 25))

        alloc = self.get_allocation()
        self.context = self.window.cairo_create()

        # widget area for debugging
        #self.context.rectangle(0, 0, alloc.width, alloc.height)
        #self.context.set_source_rgb(1, 0, 1)
        #self.context.fill_preserve()
        #self.context.stroke()

        # Create box shape and store path
        self.context.move_to(0, 5)
        self.context.curve_to(0, 2, 2, 0, 5, 0)
        self.context.line_to(alloc.width-8, 0)
        self.context.curve_to(alloc.width-5, 0,
                              alloc.width-3, 2,
                              alloc.width-3, 5)
        self.context.line_to(alloc.width-3, alloc.height-8)
        self.context.curve_to(alloc.width-3, alloc.height-5,
                              alloc.width-5, alloc.height-3,
                              alloc.width-8, alloc.height-3)
        self.context.line_to(5, alloc.height-3)
        self.context.curve_to(2, alloc.height-3,
                              0, alloc.height-5,
                              0, alloc.height-8)
        self.context.close_path()
        path = self.context.copy_path()

        # shadow
        self.context.save()
        self.context.translate(3, 3)
        self.context.new_path()
        self.context.append_path(path)
        self.context.set_source_rgba(*(self.bordercolor[:3] + (0.4,)))
        self.context.fill_preserve()
        self.context.set_line_width(0)
        self.context.stroke()
        self.context.restore()

        # box shape used for clipping
        self.context.append_path(path)
        self.context.clip()

        # background
        self.context.append_path(path)
        self.context.set_source_rgb(*self.bgcolor[:3])
        self.context.fill_preserve()
        self.context.stroke()

        # image
        if self.img_surf:
            self.context.set_source_surface(self.img_surf,
                alloc.width-4-self.img_surf.get_width(), 1)
            self.context.paint()

        # text
        self.context.move_to(5, 4)
        self.context.set_source_rgb(0, 0, 0)
        self.context.show_layout(self.textlayout)

        # text extents
        #self.context.set_source_rgba(1, 0, 0, 0.5)
        #s = self.textlayout.get_pixel_size()
        #self.context.set_line_width(1)
        #self.context.rectangle(5.5, 4.5, s[0]-1, s[1]-1)
        #self.context.stroke()

        # Mark deceased
        if self.person and not self.alive:
            self.context.set_line_width(2)
            self.context.move_to(0, 10)
            self.context.line_to(10, 0)
            self.context.stroke()

        #border
        if self.hightlight:
            self.context.set_line_width(5)
        else:
            self.context.set_line_width(2)
        self.context.append_path(path)
        self.context.set_source_rgb(*self.bordercolor[:3])
        self.context.stroke()

class PersonBoxWidget(_PersonWidgetBase):
    """
    Draw person box using GC library.
    For version PyGTK < 2.8
    """
    def __init__(self, view, format_helper, dbstate, person, alive, maxlines,
                image=False):
        _PersonWidgetBase.__init__(self, view, format_helper, person)
                        # Required for popup menu and right mouse button click
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK
                        | Gdk.EventMask.BUTTON_RELEASE_MASK
                        # Required for tooltip and mouse-over
                        | Gdk.EventMask.ENTER_NOTIFY_MASK
                        # Required for tooltip and mouse-over
                        | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.maxlines = maxlines
        self.alive = alive
        
        self.image = None
        if image:
            image_path = self.get_image(dbstate, person)
            if image_path:
                self.image = GdkPixbuf.Pixbuf.new_from_file(image_path)

##TODO GTK3: event deprecated , instead if still needed connect to event, 
## and check if event is an expose event.
##        self.connect("expose_event", self.expose)
        self.connect("realize", self.realize)
        text = ""
        if self.person:
            text = self.format_helper.format_person(self.person, self.maxlines)
            # enable mouse-over
            self.connect("enter-notify-event", self.cb_on_enter)
            self.connect("leave-notify-event", self.cb_on_leave)
        self.textlayout = self.create_pango_layout(text)
        size = self.textlayout.get_pixel_size()
        xmin = size[0] + 12
        ymin = size[1] + 11
        if self.image:
            xmin += self.image.get_width()
            ymin = max(ymin, self.image.get_height()+4)
        self.set_size_request(max(xmin, 120), max(ymin, 25))
        # GTK object use in realize and expose methods
        self.bg_gc = None
        self.text_gc = None
        self.border_gc = None
        self.shadow_gc = None

    def cb_on_enter(self, widget, event):
        """On mouse-over highlight border"""
        self.border_gc.line_width = 3
        self.queue_draw()

    def cb_on_leave(self, widget, event):
        """On mouse-out normal border"""
        self.border_gc.line_width = 1
        self.queue_draw()

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display. Creat all elements for person box(bg_gc, text_gc, border_gc,
        shadow_gc), and setup they style.
        """
        # pylint: disable-msg=E1101
        self.bg_gc = self.window.new_gc()
        self.text_gc = self.window.new_gc()
        self.border_gc = self.window.new_gc()
        self.border_gc.line_style = Gdk.LINE_SOLID
        self.border_gc.line_width = 1
        self.shadow_gc = self.window.new_gc()
        self.shadow_gc.line_style = Gdk.LINE_SOLID
        self.shadow_gc.line_width = 4
        if self.person:
            if self.alive and self.person.get_gender() == gen.lib.Person.MALE:
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#b9cfe7"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#204a87"))
            elif self.person.get_gender() == gen.lib.Person.MALE:
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#b9cfe7"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#000000"))
            elif self.alive and (
                self.person.get_gender() == gen.lib.Person.FEMALE):
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#ffcdf1"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#87206a"))
            elif self.person.get_gender() == gen.lib.Person.FEMALE:
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#ffcdf1"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#000000"))
            elif self.alive:
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#f4dcb7"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#8f5902"))
            else:
                self.bg_gc.set_foreground(
                    self.get_colormap().alloc_color("#f4dcb7"))
                self.border_gc.set_foreground(
                    self.get_colormap().alloc_color("#000000"))
        else:
            self.bg_gc.set_foreground(
                self.get_colormap().alloc_color("#eeeeee"))
            self.border_gc.set_foreground(
                self.get_colormap().alloc_color("#777777"))
        self.shadow_gc.set_foreground(
            self.get_colormap().alloc_color("#999999"))


    def expose(self, widget, event):
        """
        Redrawing the contents of the widget.
        Drawing borders and person info on exist elements.
        """
        # pylint: disable-msg=E1101
        alloc = self.get_allocation()
        # shadow
        self.window.draw_line(self.shadow_gc, 3, alloc.height-1,
                              alloc.width, alloc.height-1)
        self.window.draw_line(self.shadow_gc, alloc.width-1, 3,
                              alloc.width-1, alloc.height)
        # box background
        self.window.draw_rectangle(self.bg_gc, True, 1, 1,
                                   alloc.width-5, alloc.height-5)
        # text
        if self.person:
            self.window.draw_layout(self.text_gc, 5, 4, self.textlayout)
        # image
        if self.image:
            self.window.draw_pixbuf(self.text_gc, self.image, 0, 0,
                                    alloc.width-4-self.image.get_width(), 1)
        # border
        if self.border_gc.line_width > 1:
            self.window.draw_rectangle(self.border_gc, False, 1, 1,
                                       alloc.width-6, alloc.height-6)
        else:
            self.window.draw_rectangle(self.border_gc, False, 0, 0,
                                       alloc.width-4, alloc.height-4)

class LineWidget(Gtk.DrawingArea):
    """
    Draw lines linking Person boxes - Types A and C.
    """
    def __init__(self, child, father, frel, mother, mrel, direction):
        GObject.GObject.__init__(self)

        self.child_box = child
        self.father_box = father
        self.mother_box = mother
        self.frel = frel
        self.mrel = mrel
        self.direction = direction
        self.line_gc = None
        
##TODO GTK3: event deprecated , instead if still needed connect to event, 
## and check if event is an expose event.
##        self.connect("expose_event", self.expose)
        self.connect("realize", self.realize)

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display.
        """
        # pylint: disable-msg=E1101
        self.set_size_request(20, 20)
##TODO GTK3:to rewrite in terms of cairo!
##        self.line_gc = self.get_root_window().new_gc()
##        self.line_gc.set_foreground(
##            self.get_colormap().alloc_color("#000000"))
        self.cairocontext = self.get_root_window().cairo_create()
        self.cairocontext.set_source_rgb(0.,0.,0.)
        
    def expose(self, widget, event):
        """
        Redraw the contents of the widget.
        """
        # pylint: disable-msg=E1101
        alloc = self.get_allocation()
        child = self.child_box.get_allocation()

        if self.father_box:
            father = self.father_box.get_allocation()
        if self.mother_box:
            mother = self.mother_box.get_allocation()

        if self.direction in [2, 3]: # horizontal
            child_side = 0
            centre = alloc.width / 2
            parent_side = alloc.width
            middle = child.y - alloc.y + child.height / 2
            if self.father_box:
                father_side = father.height / 2
            if self.mother_box:
                mother_side = alloc.height - mother.height / 2
        else:
            child_side = 0
            centre = alloc.height / 2
            parent_side = alloc.height
            middle = child.x - alloc.x + child.width / 2
            if self.father_box:
                father_side = father.width / 2
            if self.mother_box:
                mother_side = alloc.width - mother.width / 2

        if self.direction in [1, 3]: # bottom to top or right to left
            child_side = parent_side
            parent_side = 0

        self.line_gc.line_width = 3

        if self.father_box:
            self.draw_link(parent_side, middle, child_side, centre,
                           father_side, self.mrel)

        if self.mother_box:
            self.draw_link(parent_side, middle, child_side, centre,
                           mother_side, self.frel)

    def draw_link(self, parent_side, middle, child_side, centre, side, rela):
        """
        Draw a link between parent and child.
        """
        if rela:
            self.line_gc.line_style = Gdk.LINE_SOLID
        else:
            self.line_gc.line_style = Gdk.LINE_ON_OFF_DASH
        
        self.draw_line(centre, side, parent_side, side)
        self.draw_line(centre, side, centre, middle)
        self.draw_line(centre, middle, child_side, middle)

    def draw_line(self, x_from, y_from, x_to, y_to):
        """
        Draw a single line in a link.
        """
        # pylint: disable-msg=E1101
        if self.direction in [2, 3]: # horizontal
            self.window.draw_line(self.line_gc, x_from, y_from, x_to, y_to)
        else:
            self.window.draw_line(self.line_gc, y_from, x_from, y_to, x_to)
            
class LineWidget2(Gtk.DrawingArea):
    """
    Draw lines linking Person boxes - Type B.
    """
    def __init__(self, male, rela, direction):
        GObject.GObject.__init__(self)

        self.male = male
        self.rela = rela
        self.direction = direction
        self.line_gc = None
        
##TODO GTK3: event deprecated , instead if still needed connect to event, 
## and check if event is an expose event.
##        self.connect("expose_event", self.expose)
        self.connect("realize", self.realize)

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display.
        """
        # pylint: disable-msg=E1101
        self.set_size_request(20, -1)
        self.line_gc = self.window.new_gc()
        self.line_gc.set_foreground(
            self.get_colormap().alloc_color("#000000"))
        
    def expose(self, widget, event):
        """
        Redraw the contents of the widget.
        """
        # pylint: disable-msg=E1101
        alloc = self.get_allocation()

        if self.direction in [2, 3]: # horizontal
            child_x = alloc.width / 2
            child_y = alloc.height
            parent_x = alloc.width
            parent_y = alloc.height / 2
            mid_x = alloc.width / 2
            mid_y = alloc.height / 2
        else:
            child_y = alloc.width
            child_x = alloc.height / 2
            parent_y = alloc.width / 2
            parent_x = alloc.height
            mid_y = alloc.width / 2
            mid_x = alloc.height / 2

        if not self.rela:
            self.line_gc.line_style = Gdk.LINE_ON_OFF_DASH
        else:
            self.line_gc.line_style = Gdk.LINE_SOLID

        self.line_gc.line_width = 3

        if self.direction in [1, 3]:
            parent_x = 0

        if not self.male:
            child_y = 0

        self.draw_line(child_x, child_y, mid_x, mid_y)
        self.draw_line(mid_x, mid_y, parent_x, parent_y)
        
    def draw_line(self, x_from, y_from, x_to, y_to):
        """
        Draw a single line in a link.
        """
        # pylint: disable-msg=E1101
        if self.direction in [2, 3]: # horizontal
            self.window.draw_line(self.line_gc, x_from, y_from, x_to, y_to)
        else:
            self.window.draw_line(self.line_gc, y_from, x_from, y_to, x_to)
        
#-------------------------------------------------------------------------
#
# PedigreeView
#
#-------------------------------------------------------------------------
class PedigreeView(NavigationView):
    """
    View for pedigree tree.
    Displays the ancestors of a selected individual.
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('interface.pedview-tree-size', 5),
        ('interface.pedview-layout', 0),
        ('interface.pedview-show-images', True),
        ('interface.pedview-show-marriage', True),
        ('interface.pedview-tree-direction', 2),
        ('interface.pedview-show-unknown-people', True),
        )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        NavigationView.__init__(self, _('Pedigree'), pdata, dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      PersonBookmarks,
                                      nav_group)

        self.func_list.update({
            'F2' : self.kb_goto_home,
            '<PRIMARY>J' : self.jump,
            })

        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.change_db)
        uistate.connect('nameformat-changed', self.person_rebuild)
        
        self.format_helper = FormattingHelper(self.dbstate)
        
        # Depth of tree.
        self._depth = 1
        # Variables for drag and scroll
        self._last_x = 0
        self._last_y = 0
        self._in_move = False
        self.key_active_changed = None
        # GTK objects
        self.scrolledwindow = None
        self.table = None

        self.additional_uis.append(self.additional_ui())

        # Automatic resize
        self.force_size = self._config.get('interface.pedview-tree-size') 
        # Nice tree
        self.tree_style = self._config.get('interface.pedview-layout')
        # Show photos of persons
        self.show_images = self._config.get('interface.pedview-show-images')
        # Hide marriage data by default
        self.show_marriage_data = self._config.get(
                                'interface.pedview-show-marriage')
        # Tree draw direction
        self.tree_direction = self._config.get('interface.pedview-tree-direction')
        self.cb_change_scroll_direction(None, self.tree_direction < 2)
        # Show on not unknown people.
        # Default - not show, for mo fast display hight tree
        self.show_unknown_people = self._config.get(
                                'interface.pedview-show-unknown-people')

    def change_page(self):
        """Called when the page changes."""
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()
        if self.dirty:
            self.rebuild_trees(self.get_active())

    def get_stock(self):
        """
        The category stock icon
        """
        return 'gramps-pedigree'
    
    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-pedigree'

    def build_widget(self):
        """
        Builds the interface and returns a Gtk.Container type that
        contains the interface. This containter will be inserted into
        a Gtk.ScrolledWindow page.
        """
        self.scrolledwindow = Gtk.ScrolledWindow(None, None)
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                       Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.add_events(Gdk.EventMask.SCROLL_MASK)
        self.scrolledwindow.connect("scroll-event", self.cb_bg_scroll_event)
        event_box = Gtk.EventBox()
        # Required for drag-scroll events and popup menu
        event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK
                             | Gdk.EventMask.BUTTON_RELEASE_MASK
                             | Gdk.EventMask.BUTTON1_MOTION_MASK)
        # Signal begin drag-scroll
        event_box.connect("button-press-event", self.cb_bg_button_press)
        # Signal end drag-scroll and popup menu
        event_box.connect("button-release-event", self.cb_bg_button_release)
        #Signal for controll motion-notify when left mouse button pressed
        event_box.connect("motion-notify-event", self.cb_bg_motion_notify_event)
        self.scrolledwindow.add_with_viewport(event_box)

        self.table = Gtk.Table(1, 1, False)
        event_box.add(self.table)
        event_box.get_parent().set_shadow_type(Gtk.ShadowType.NONE)
        self.table.set_row_spacings(1)
        self.table.set_col_spacings(0)

        return self.scrolledwindow

    def additional_ui(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <menuitem action="FilterEdit"/>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>
              <toolitem action="Forward"/>
              <toolitem action="HomePerson"/>
            </placeholder>
          </toolbar>
        </ui>'''

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.

        Special action groups for Forward and Back are created to allow the
        handling of navigation buttons. Forward and Back allow the user to
        advance or retreat throughout the history, and we want to have these
        be able to toggle these when you are at the end of the history or
        at the beginning of the history.
        """
        NavigationView.define_actions(self)
        
        self._add_action('FilterEdit',  None, _('Person Filter Editor'), 
                        callback=self.cb_filter_editor)

    def cb_filter_editor(self, obj):
        """
        Display the person filter editor.
        """
        try:
            FilterEditor('Person', CUSTOM_FILTERS, 
                         self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        try:
            active = self.get_active()
            if active:
                self.rebuild_trees(active)
            else:
                self.rebuild_trees(None)
        except AttributeError, msg:
            RunDatabaseRepair(str(msg))

    def _connect_db_signals(self):
        """
        Connect database signals.
        """
        self._add_db_signal('person-add', self.person_rebuild)
        self._add_db_signal('person-update', self.person_rebuild)
        self._add_db_signal('person-delete', self.person_rebuild)
        self._add_db_signal('person-rebuild', self.person_rebuild_bm)
        self._add_db_signal('family-update', self.person_rebuild)
        self._add_db_signal('family-add', self.person_rebuild)
        self._add_db_signal('family-delete', self.person_rebuild)
        self._add_db_signal('family-rebuild', self.person_rebuild)
        
    def change_db(self, db):
        """
        Callback associated with DbState. Whenever the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tree
        is no need to store the database, since we will get the value
        from self.state.db
        """
        self._change_db(db)
        self.bookmarks.update_bookmarks(self.dbstate.db.get_bookmarks())
        if self.active:
            self.bookmarks.redraw()
        self.build_tree()

    def navigation_type(self):
        """
        Indicates the navigation type. Navigation type can be the string
        name of any of the primary objects.
        """
        return 'Person'

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView 
        :return: bool
        """
        return True

    def on_delete(self):
        self._config.save()
        NavigationView.on_delete(self)

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given person handle as the root.
        """
        self.dirty = True
        if handle:
            person = self.dbstate.db.get_person_from_handle(handle)
            if person:
                self.rebuild_trees(handle)
            else:
                self.rebuild_trees(None)
        else:
            self.rebuild_trees(None)
        self.uistate.modify_statusbar(self.dbstate)

    def person_rebuild_bm(self, dummy=None):
        """Large change to person database"""
        self.person_rebuild(dummy)
        if self.active:
            self.bookmarks.redraw()

    def person_rebuild(self, dummy=None):
        """Callback function for signals of change database."""
        self.format_helper.clear_cache()
        self.dirty = True
        if self.active:
            self.rebuild_trees(self.get_active())

    def rebuild_trees(self, person_handle):
        """
        Rebuild tree with root person_handle.
        Called from many fuctions, when need full redraw tree.
        """
        person = None
        if person_handle:
            person = self.dbstate.db.get_person_from_handle(person_handle)

        self.dirty = False

        if self.tree_style == 1 and (
           self.force_size > 5 or self.force_size == 0):
            self.force_size = 5

        # A position definition is a tuple of nodes.
        # Each node consists of a tuple of:
        #     (person box rectangle, connection, marriage box rectangle)
        # A rectangle is a tuple of the format (x, y, width, height)
        # A connectcion is either a line or a tuple of two lines.
        # A line is of the format (x, y, height).  Lines have a width of 1.
        if self.tree_style == 1:
            if self.force_size == 2:
                pos = (((0, 3, 3, 3), ((1, 0, 3), (1, 6, 3)), (3, 3, 2, 3)),
                      ((2, 0, 3, 3), None, None),
                      ((2, 6, 3, 3), None, None))
            elif self.force_size == 3:
                pos = (((0, 4, 3, 5), ((1, 1, 3), (1, 9, 3)), (3, 5, 2, 3)),
                      ((2, 1, 3, 3), ((3, 0, 1), (3, 4, 1)), (5, 1, 2, 3)),
                      ((2, 9, 3, 3), ((3, 8, 1), (3, 12, 1)), (5, 9, 2, 3)),
                      ((4, 0, 3, 1), None, None),
                      ((4,4,3,1),None,None),
                      ((4,8,3,1),None,None),
                      ((4,12,3,1),None,None))
            elif self.force_size == 4:
                pos = (((0, 5, 3, 5), ((1, 2, 3), (1, 10, 3)), (3,  6, 2, 3)),
                      ((2,  2, 3, 3), ((3, 1, 1), (3, 5, 1)), (5,  3, 2, 1)),
                      ((2, 10, 3, 3), ((3, 9, 1), (3, 13, 1)), (5, 11, 2, 1)),
                      ((4,  1, 3, 1), ((5, 0, 1), (5, 2, 1)), (7, 1, 2, 1)),
                      ((4,  5, 3, 1), ((5, 4, 1), (5, 6, 1)), (7, 5, 2, 1)),
                      ((4,  9, 3, 1), ((5, 8, 1), (5, 10, 1)), (7, 9, 2, 1)),
                      ((4, 13, 3, 1), ((5, 12, 1), (5, 14, 1)), (7, 13, 2, 1)),
                      ((6,  0, 3, 1), None, None),
                      ((6,  2, 3, 1), None, None),
                      ((6,  4, 3, 1), None, None),
                      ((6,  6, 3, 1), None, None),
                      ((6,  8, 3, 1), None, None),
                      ((6, 10, 3, 1), None, None),
                      ((6, 12, 3, 1), None, None),
                      ((6, 14, 3, 1), None, None))
            elif self.force_size == 5:
                pos = (((0, 10, 3, 11), ((1, 5, 5), (1, 21, 5)), (3, 13, 2, 5)),
                      ((2,  5, 3, 5), ((3, 2, 3), (3, 10, 3)), (5,  6, 2, 3)),
                      ((2, 21, 3, 5), ((3, 18, 3), (3, 26, 3)), (5, 22, 2, 3)),
                      ((4,  2, 3, 3), ((5, 1, 1), (5, 5, 1)), (7, 3, 2, 1)),
                      ((4, 10, 3, 3), ((5, 9, 1), (5, 13, 1)), (7, 11, 2, 1)),
                      ((4, 18, 3, 3), ((5, 17, 1), (5, 21, 1)), (7, 19, 2, 1)),
                      ((4, 26, 3, 3), ((5, 25, 1), (5, 29, 1)), (7, 27, 2, 1)),
                      ((6,  1, 3, 1), ((7, 0, 1), (7, 2, 1)), (9, 1, 2, 1)),
                      ((6,  5, 3, 1), ((7, 4, 1), (7, 6, 1)), (9, 5, 2, 1)),
                      ((6,  9, 3, 1), ((7, 8, 1), (7, 10, 1)), (9, 9, 2, 1)),
                      ((6, 13, 3, 1), ((7, 12, 1), (7, 14, 1)), (9, 13, 2, 1)),
                      ((6, 17, 3, 1), ((7, 16, 1), (7, 18, 1)), (9, 17, 2, 1)),
                      ((6, 21, 3, 1), ((7, 20, 1), (7, 22, 1)), (9, 21, 2, 1)),
                      ((6, 25, 3, 1), ((7, 24, 1), (7, 26, 1)), (9, 25, 2, 1)),
                      ((6, 29, 3, 1), ((7, 28, 1), (7, 30, 1)), (9, 29, 2, 1)),
                      ((8,  0, 3, 1), None, None),
                      ((8,  2, 3, 1), None, None),
                      ((8,  4, 3, 1), None, None),
                      ((8,  6, 3, 1), None, None),
                      ((8,  8, 3, 1), None, None),
                      ((8, 10, 3, 1), None, None),
                      ((8, 12, 3, 1), None, None),
                      ((8, 14, 3, 1), None, None),
                      ((8, 16, 3, 1), None, None),
                      ((8, 18, 3, 1), None, None),
                      ((8, 20, 3, 1), None, None),
                      ((8, 22, 3, 1), None, None),
                      ((8, 24, 3, 1), None, None),
                      ((8, 26, 3, 1), None, None),
                      ((8, 28, 3, 1), None, None),
                      ((8, 30, 3, 1), None, None))
        else:
            pos = None

        # Build ancestor tree only one for all different sizes
        self._depth = 1
        lst = [None] * (2**self.force_size)
        self.find_tree(person, 0, 1, lst)

        # Purge current table content
        for child in self.table.get_children():
            child.destroy()
        self.table.resize(1, 1)

        if person:
            self.rebuild(self.table, pos, lst, self.force_size)

    def rebuild(self, table_widget, positions, lst, size):
        """
        Function called from rebuild_trees.
        For table_widget (Gtk.Table) place list of person, use positions array.
        For style C position calculated, for others style use static posotins.
        All display options process in this function.
        """

        # Calculate maximum table size
        xmax = 0
        ymax = 0
        if self.tree_style == 0:
            xmax = 2 * size
            ymax = 2 ** size          
        elif self.tree_style == 1:
            xmax = 2 * size + 2
            ymax = [0, 10, 14, 16, 32][size - 1]
        elif self.tree_style == 2:
            # For style C change tree depth if they real size less then max.
            if self.show_unknown_people:
                self._depth += 1
            if size > self._depth:
                size = self._depth
            xmax = 2 * size
            ymax = 2 ** size * 2

        pbw = None
        for i in range(0, 2 ** size - 1):
            ####################################################################
            # Table placement for person data
            ####################################################################
            if self.tree_style in [0, 2]:
                # Dynamic position person in tree
                width = _width = 1
                height = _height = 3
                level = int(math.log(i+1, 2))
                offset = i + 1 - (2**level)

                if self.tree_style == 0:
                    _delta = (2**size) / (2**level)
                else:
                    _delta = (2**size) / (2**level) * 2

                x_pos = (1 + _width) * level + 1
                y_pos = _delta / 2 + offset * _delta - 1

                if self.tree_style == 0 and level == size - 1:
                    y_pos = _delta / 2 + offset * _delta
                    height = _height = 1
            else:
                try:
                    x_pos = positions[i][0][0]+1
                    y_pos = positions[i][0][1]+1
                    width = positions[i][0][2]
                    height = positions[i][0][3]
                except IndexError:  # no position for this person defined
                    continue

            last_pbw = pbw
            pbw = None
            if not lst[i] and (
               (self.tree_style in [0, 2] and self.show_unknown_people and
               lst[((i+1)/2)-1]) or self.tree_style == 1):
                #
                # No person -> show empty box
                #
                if CAIRO_AVAILABLE:
                    pbw = PersonBoxWidgetCairo(self, self.format_helper,
                        self.dbstate, None, False, 0, None)
                else:
                    pbw = PersonBoxWidget(self, self.format_helper,
                        self.dbstate, None, False, 0, None)

                if i > 0 and lst[((i+1)/2)-1]:
                    fam_h = None
                    fam = lst[((i+1)/2)-1][2]
                    if fam:
                        fam_h = fam.get_handle()
                    if not self.dbstate.db.readonly:
                        pbw.connect("button-press-event",
                                    self.cb_missing_parent_button_press,
                                    lst[((i+1)/2)-1][0].get_handle(), fam_h)
                        pbw.force_mouse_over = True

            elif lst[i]:
                #
                # Person exists -> populate box
                #
                image = False
                if self.show_images and height > 1 and (
                   i < ((2**size-1)/2) or self.tree_style == 2):
                    image = True

                if CAIRO_AVAILABLE:
                    pbw = PersonBoxWidgetCairo(self, self.format_helper,
                        self.dbstate, lst[i][0], lst[i][3], height, image)
                else:
                    pbw = PersonBoxWidget(self, self.format_helper,
                        self.dbstate, lst[i][0], lst[i][3], height, image)
                lst[i][4] = pbw
                if height < 7:
                    pbw.set_tooltip_text(self.format_helper.format_person(
                                                                lst[i][0], 11))

                fam_h = None
                if lst[i][2]:
                    fam_h = lst[i][2].get_handle()
                pbw.connect("button-press-event",
                            self.cb_person_button_press,
                            lst[i][0].get_handle(), fam_h)

            if pbw:
                self.attach_widget(table_widget, pbw, xmax,
                                    x_pos, x_pos+width, y_pos, y_pos+height)
                
            ####################################################################
            # Connection lines
            ####################################################################
            if self.tree_style == 1 and (
               positions[i][1] and len(positions[i][1]) == 2):
                # separate boxes for father and mother
                x_pos = positions[i][1][0][0]+1
                y_pos = positions[i][1][0][1]+1
                width = 1
                height = positions[i][1][0][2]

                rela = False
                if lst[2*i+1]: # Father
                    rela = lst[2*i+1][1]
                line = LineWidget2(1, rela, self.tree_direction)

                if lst[i] and lst[i][2]:
                    # Required for popup menu
                    line.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                    line.connect("button-press-event",
                                 self.cb_relation_button_press,
                                 lst[i][2].get_handle())
                                 
                self.attach_widget(table_widget, line, xmax,
                                    x_pos, x_pos+width, y_pos, y_pos+height)

                x_pos = positions[i][1][1][0]+1
                y_pos = positions[i][1][1][1]+1

                rela = False
                if lst[2*i+2]: # Mother
                    rela = lst[2*i+2][1]
                line = LineWidget2(0,  rela, self.tree_direction)

                if lst[i] and lst[i][2]:
                    # Required for popup menu
                    line.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                    line.connect("button-press-event",
                                 self.cb_relation_button_press,
                                 lst[i][2].get_handle())

                self.attach_widget(table_widget, line, xmax,
                                    x_pos, x_pos+width, y_pos, y_pos+height)

            elif self.tree_style in [0, 2] and lst[((i+1)/2)-1]:
                # combined for father and mother
                x_pos = (1 + _width)*level
                y_pos = offset * _delta - (_delta / 2) - 1
                width = 1
                height = _delta + 3

                if self.tree_style == 0 and level == size - 1:
                    height -= 2
                    y_pos += 1
 
                if i > 0 and i % 2 == 0 and (pbw or last_pbw):
                    frela = mrela = None
                    if lst[i]:
                        frela = lst[i][1]
                    if lst[i - 1]:
                        mrela = lst[i-1][1]

                    line = LineWidget(lst[((i+1)/2)-1][4],
                                      last_pbw, frela,
                                      pbw, mrela,
                                      self.tree_direction)
                        
                    if lst[i] and lst[i][2]:
                        # Required for popup menu
                        line.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                        line.connect("button-press-event",
                                     self.cb_relation_button_press,
                                     lst[((i+1)/2)-1][2].get_handle())
                        # Required for tooltip and mouse-over
                        line.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
                        # Required for tooltip and mouse-over
                        line.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
                        line.set_tooltip_text(
                            self.format_helper.format_relation(
                                                    lst[((i+1)/2)-1][2], 11))
                    
                    self.attach_widget(table_widget, line, xmax,
                                        x_pos, x_pos+width, y_pos, y_pos+height)

            ####################################################################
            # Show marriage data
            ####################################################################
            if self.show_marriage_data and (
                self.tree_style == 1 and positions[i][2] or
               (self.tree_style in [0, 2] and level+1 < size)):
                if lst[i] and lst[i][2]:
                    text = self.format_helper.format_relation(lst[i][2], 1, True)
                else:
                    text = " "
                label = Gtk.Label(label=text)
                label.set_justify(Gtk.Justification.LEFT)
                label.set_use_markup(True)
                label.set_line_wrap(True)
                label.set_alignment(0.1, 0.5)
                if self.tree_style in [0, 2]:
                    x_pos = (1 + _width) * (level + 1) + 1
                    y_pos = _delta / 2 + offset * _delta -1 + _height / 2
                    width = 1
                    height = 1
                    if self.tree_style == 0 and level < 2 and size > 4:
                        # Boxes can be bigger for lowest levels on larger trees.
                        y_pos -= 2
                        height += 4
                else:
                    x_pos = positions[i][2][0]+1
                    y_pos = positions[i][2][1]+1
                    width = positions[i][2][2]
                    height = positions[i][2][3]

                self.attach_widget(table_widget, label, xmax,
                                    x_pos, x_pos+width, y_pos, y_pos+height)
                                        
        ########################################################################
        # Add navigation arrows
        ########################################################################
        if lst[0]:
            if self.tree_direction == 2:
                child_arrow = Gtk.ArrowType.LEFT
                parent_arrow = Gtk.ArrowType.RIGHT
            elif self.tree_direction == 0:
                child_arrow = Gtk.ArrowType.UP
                parent_arrow = Gtk.ArrowType.DOWN
            elif self.tree_direction == 1:
                child_arrow = Gtk.ArrowType.DOWN
                parent_arrow = Gtk.ArrowType.UP
            elif self.tree_direction == 3:
                child_arrow = Gtk.ArrowType.RIGHT
                parent_arrow = Gtk.ArrowType.LEFT

            button = Gtk.Button()
            button.add(Gtk.Arrow.new(child_arrow, Gtk.ShadowType.IN))
            childlist = find_children(self.dbstate.db, lst[0][0])
            if childlist:
                button.connect("clicked", self.cb_on_show_child_menu)
                button.set_tooltip_text(_("Jump to child..."))
            else:
                button.set_sensitive(False)

            ymid = int(math.floor(ymax/2))
            self.attach_widget(table_widget, button, xmax,
                                0, 1, ymid, ymid +1, fill=False)
            
            button = Gtk.Button()
            button.add(Gtk.Arrow.new(parent_arrow, Gtk.ShadowType.IN))
            if lst[1]:
                button.connect("clicked", self.cb_childmenu_changed,
                          lst[1][0].handle)
                button.set_tooltip_text(_("Jump to father"))
            else:
                button.set_sensitive(False)
                
            ymid = int(math.floor(ymax/4))
            self.attach_widget(table_widget, button, xmax,
                                xmax, xmax+1, ymid-1, ymid+2, fill=False)

            button = Gtk.Button()
            button.add(Gtk.Arrow.new(parent_arrow, Gtk.ShadowType.IN))
            if lst[2]:
                button.connect("clicked", self.cb_childmenu_changed,
                          lst[2][0].handle)
                button.set_tooltip_text(_("Jump to mother"))
            else:
                button.set_sensitive(False)
                
            ymid = int(math.floor(ymax/4*3))
            self.attach_widget(table_widget, button, xmax,
                                xmax, xmax+1, ymid-1, ymid+2, fill=False)

        # add dummy widgets into the corners of the table
        # to allow the pedigree to be centered
        label = Gtk.Label(label="")
        table_widget.attach(label, 0, 1, 0, 1,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, 0, 0)
        label = Gtk.Label(label="")
        if self.tree_direction in [2, 3]:
            table_widget.attach(label, xmax, xmax+1, ymax, ymax+1,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, 0, 0)
        else:
            table_widget.attach(label, ymax, ymax+1, xmax, xmax+1,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL,
                        Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, 0, 0)

        debug = False
        if debug:
            used_cells = {}
            xmax = 0
            ymax = 0
            # iterate table to see which cells are used.
            for child in table_widget.get_children():
                left = table_widget.child_get_property(child, "left-attach")
                right = table_widget.child_get_property(child, "right-attach")
                top = table_widget.child_get_property(child, "top-attach")
                bottom = table_widget.child_get_property(child, "bottom-attach")
                for x_pos in range(left, right):
                    for y_pos in range(top, bottom):
                        try:
                            used_cells[x_pos][y_pos] = True
                        except KeyError:
                            used_cells[x_pos] = {}
                            used_cells[x_pos][y_pos] = True
                        if y_pos > ymax:
                            ymax = y_pos
                    if x_pos > xmax:
                        xmax = x_pos
            for x_pos in range(0, xmax+1):
                for y_pos in range(0, ymax+1):
                    try:
                        tmp = used_cells[x_pos][y_pos]
                    except KeyError:
                        # fill unused cells
                        label = Gtk.Label(label="%d,%d"%(x_pos, y_pos))
                        frame = Gtk.ScrolledWindow(None, None)
                        frame.set_shadow_type(Gtk.ShadowType.NONE)
                        frame.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
                        frame.add_with_viewport(label)
                        table_widget.attach(frame, x_pos, x_pos+1,
                                            y_pos, y_pos+1,
                                            Gtk.AttachOptions.FILL,
                                            Gtk.AttachOptions.FILL, 0, 0)
        table_widget.show_all()

        # Setup scrollbars for view root person
        window = table_widget.get_parent().get_parent()
        hadjustment = window.get_hadjustment()
        vadjustment = window.get_vadjustment()
        if self.tree_direction == 2:
            self.update_scrollbar_positions(hadjustment, hadjustment.get_lower())
            self.update_scrollbar_positions(vadjustment,
                (vadjustment.get_upper() - vadjustment.get_page_size()) / 2)
        elif self.tree_direction == 0:
            self.update_scrollbar_positions(hadjustment,
                (hadjustment.get_upper() - hadjustment.get_page_size()) / 2)
            self.update_scrollbar_positions(vadjustment,
                vadjustment.get_upper() - vadjustment.get_page_size())
        elif self.tree_direction == 1:
            self.update_scrollbar_positions(hadjustment,
                (hadjustment.get_upper() - hadjustment.get_page_size()) / 2)
            self.update_scrollbar_positions(vadjustment, vadjustment.get_lower())
        elif self.tree_direction == 3:
            self.update_scrollbar_positions(hadjustment,
                hadjustment.get_upper() - hadjustment.get_page_size())
            self.update_scrollbar_positions(vadjustment,
                (vadjustment.get_upper() - vadjustment.get_page_size()) / 2)

        # Setup mouse wheel scroll direction for style C,
        # depending of tree direction
        if self.tree_direction in [0, 1]:
            self.cb_change_scroll_direction(None, True)
        elif self.tree_direction in [2, 3]:
            self.cb_change_scroll_direction(None, False)

    def attach_widget(self, table, widget, xmax, right, left, top, bottom,
                        fill=True):
        """
        Attach a widget to the table.
        """
        xopts = yopts = 0
        if fill:
            xopts = yopts = Gtk.AttachOptions.FILL

        if self.tree_direction == 0: # Vertical (top to bottom)
            table.attach(widget, top, bottom, right, left, xopts, yopts, 0, 0)
        elif self.tree_direction == 1: # Vertical (bottom to top)
            table.attach(widget, top, bottom, xmax - left + 1, xmax - right + 1,
                                xopts, yopts, 0, 0)
        elif self.tree_direction == 2: # Horizontal (left to right)
            table.attach(widget, right, left, top, bottom, xopts, yopts, 0, 0)
        elif self.tree_direction == 3: # Horizontal (right to left)
            table.attach(widget, xmax - left + 1, xmax - right + 1, top, bottom,
                                xopts, yopts, 0, 0)

    def cb_home(self, menuitem):
        """Change root person to default person for database."""
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.change_active(defperson.get_handle())

    def cb_edit_person(self, obj, person_handle):
        """
        Open edit person window for person_handle.
        Called after double click or from submenu.
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                return True
            return True
        return False

    def cb_edit_family(self, obj, family_handle):
        """
        Open edit person family for family_handle.
        Called after double click or from submenu.
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                return True
            return True
        return False

    def cb_add_parents(self, obj, person_handle, family_handle):
        """Edit not full family."""
        if family_handle:   # one parent already exists -> Edit current family
            family = self.dbstate.db.get_family_from_handle(family_handle)
        else:   # no parents -> create new family
            family = gen.lib.Family()
            childref = gen.lib.ChildRef()
            childref.set_reference_handle(person_handle)
            family.add_child_ref(childref)
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            return

    def cb_copy_person_to_clipboard(self, obj, person_handle):
        """
        Renders the person data into some lines of text and
        puts that into the clipboard
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), 
                        Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self.format_helper.format_person(person, 11))
            return True
        return False

    def cb_copy_family_to_clipboard(self, obj, family_handle):
        """
        Renders the family data into some lines of text and
        puts that into the clipboard
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), 
                        Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self.format_helper.format_relation(family, 11))
            return True
        return False

    def cb_on_show_option_menu(self, obj, event, data=None):
        """Right click option menu."""
        self.menu = Gtk.Menu()
        self.add_nav_portion_to_menu(self.menu)
        self.add_settings_to_menu(self.menu)
        self.menu.popup(None, None, None, None, 0, event.time)
        return True

    def cb_bg_button_press(self, widget, event):
        """
        Enter in scroll mode when mouse button pressed in background
        or call option menu.
        """
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS:
            widget.get_root_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.FLEUR))
            self._last_x = event.x
            self._last_y = event.y
            self._in_move = True
            return True
        elif gui.utils.is_right_click(event):
            self.cb_on_show_option_menu(widget, event)
            return True
        return False

    def cb_bg_button_release(self, widget, event):
        """Exit from scroll mode when button release."""
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_RELEASE:
            self.cb_bg_motion_notify_event(widget, event)
            widget.get_root_window().set_cursor(None)
            self._in_move = False
            return True
        return False

    def cb_bg_motion_notify_event(self, widget, event):
        """Function for motion notify events for drag and scroll mode."""
        if self._in_move and (event.type == Gdk.EventType.MOTION_NOTIFY or
           event.type == Gdk.EventType.BUTTON_RELEASE):
            window = widget.get_parent()
            hadjustment = window.get_hadjustment()
            vadjustment = window.get_vadjustment()
            self.update_scrollbar_positions(vadjustment,
                vadjustment.get_value() - (event.y - self._last_y))
            self.update_scrollbar_positions(hadjustment,
                hadjustment.get_value() - (event.x - self._last_x))
            return True
        return False

    def update_scrollbar_positions(self, adjustment, value):
        """Controle value then try setup in scrollbar."""
        if value > (adjustment.get_upper() - adjustment.get_page_size()):
            adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
        else:
            adjustment.set_value(value)
        return True

    def cb_bg_scroll_event(self, widget, event):
        """
        Function change scroll direction to horizontally
        if variable self.scroll_direction setup.
        """
        if self.scroll_direction and event.type == Gdk.EventType.SCROLL:
            if event.direction == Gdk.ScrollDirection.UP:
                event.direction = Gdk.ScrollDirection.LEFT
            elif event.direction == Gdk.ScrollDirection.DOWN:
                event.direction = Gdk.ScrollDirection.RIGHT
        return False

    def cb_person_button_press(self, obj, event, person_handle, family_handle):
        """
        Call edit person function for mouse left button double click on person
        or submenu for person for mouse right click.
        And setup plug for button press on person widget.
        """
        if gui.utils.is_right_click(event):
            self.cb_build_full_nav_menu(obj, event,
                                        person_handle, family_handle)
            return True
        elif event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            self.cb_edit_person(obj, person_handle)
            return True
        return True

    def cb_relation_button_press(self, obj, event, family_handle):
        """
        Call edit family function for mouse left button double click
        on family line or call full submenu for mouse right click.
        And setup plug for button press on family line.
        """
        if gui.utils.is_right_click(event):
            self.cb_build_relation_nav_menu(obj, event, family_handle)
            return True
        elif event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            self.cb_edit_family(obj, family_handle)
            return True
        return True

    def cb_missing_parent_button_press(self, obj, event,
                                       person_handle, family_handle):
        """
        Call function for not full family for mouse left button double click
        on missing persons or call submenu for mouse right click.
        """
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            self.cb_add_parents(obj, person_handle, family_handle)
            return True
        elif gui.utils.is_right_click(event):
            self.cb_build_missing_parent_nav_menu(obj, event, person_handle,
                                                  family_handle)
            return True
        return False

    def cb_on_show_child_menu(self, obj):
        """User clicked button to move to child of active person"""
        person = self.dbstate.db.get_person_from_handle(self.get_active())
        if person:
            # Build and display the menu attached to the left pointing arrow
            # button. The menu consists of the children of the current root
            # person of the tree. Attach a child to each menu item.

            childlist = find_children(self.dbstate.db, person)
            if len(childlist) == 1:
                child = self.dbstate.db.get_person_from_handle(childlist[0])
                if child:
                    self.change_active(childlist[0])
            elif len(childlist) > 1:
                self.my_menu = Gtk.Menu()
                for child_handle in childlist:
                    child = self.dbstate.db.get_person_from_handle(child_handle)
                    cname = escape(name_displayer.display(child))
                    if find_children(self.dbstate.db, child):
                        label = Gtk.Label(label='<b><i>%s</i></b>' % cname)
                    else:
                        label = Gtk.Label(label=cname)
                    label.set_use_markup(True)
                    label.show()
                    label.set_alignment(0, 0)
                    menuitem = Gtk.ImageMenuItem(None)
                    go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                        Gtk.IconSize.MENU)
                    go_image.show()
                    menuitem.set_image(go_image)
                    menuitem.add(label)
                    self.my_menu.append(menuitem)
                    menuitem.connect("activate", self.cb_childmenu_changed,
                                     child_handle)
                    menuitem.show()
                self.my_menu.popup(None, None, None, None, 0, 0)
            return 1
        return 0

    def cb_childmenu_changed(self, obj, person_handle):
        """
        Callback for the pulldown menu selection, changing to the person
        attached with menu item.
        """
        self.change_active(person_handle)
        return True

    def cb_change_scroll_direction(self, menuitem, data):
        """Change scroll_direction option."""
        if data:
            self.scroll_direction = True
        else:
            self.scroll_direction = False

    def kb_goto_home(self):
        """Goto home person from keyboard."""
        self.cb_home(None)

    def find_tree(self, person, index, depth, lst, val=0):
        """Recursively build a list of ancestors"""

        if depth > self.force_size or not person:
            return

        if self._depth < depth:
            self._depth = depth

        try:
            alive = probably_alive(person, self.dbstate.db)
        except RuntimeError:
            ErrorDialog(_('Relationship loop detected'),
                        _('A person was found to be his/her own ancestor.'))
            alive = False

        lst[index] = [person, val, None, alive, None]

        parent_families = person.get_parent_family_handle_list()
        if parent_families:
            family_handle = parent_families[0]
        else:
            return

        mrel = True
        frel = True
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == person.handle:
                    mrel = child_ref.mrel == gen.lib.ChildRefType.BIRTH
                    frel = child_ref.frel == gen.lib.ChildRefType.BIRTH

                    lst[index] = [person, val, family, alive, None]
                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self.dbstate.db.get_person_from_handle(
                                    father_handle)
                        self.find_tree(father, (2*index)+1, depth+1, lst, frel)
                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self.dbstate.db.get_person_from_handle(
                                    mother_handle)
                        self.find_tree(mother, (2*index)+2, depth+1, lst, mrel)

    def add_nav_portion_to_menu(self, menu):
        """
        This function adds a common history-navigation portion
        to the context menu. Used by both build_nav_menu() and
        build_full_nav_menu() methods.
        """
        hobj = self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())
        home_sensitivity = True
        if not self.dbstate.db.get_default_person():
            home_sensitivity = False
            # bug 4884: need to translate the home label
        entries = [
            (Gtk.STOCK_GO_BACK, self.back_clicked, not hobj.at_front()),
            (Gtk.STOCK_GO_FORWARD, self.fwd_clicked, not hobj.at_end()),
            (_("Home"), self.cb_home, home_sensitivity),
        ]

        for stock_id, callback, sensitivity in entries:
            item = Gtk.ImageMenuItem(stock_id)
            item.set_sensitive(sensitivity)
            if stock_id == _("Home"):
                im = Gtk.Image.new_from_stock(Gtk.STOCK_HOME, Gtk.IconSize.MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate", callback)
            item.show()
            menu.append(item)

    def add_settings_to_menu(self, menu):
        """
        Add frequently used settings to the menu.  Most settings will be set
        from the configuration dialog.
        """
        # Separator. 
        item = Gtk.SeparatorMenuItem()
        item.show()
        menu.append(item)

        # Mouse scroll direction setting. 
        item = Gtk.MenuItem(label=_("Mouse scroll direction"))
        item.set_submenu(Gtk.Menu())
        scroll_direction_menu = item.get_submenu()

        scroll_direction_image = Gtk.Image.new_from_stock(Gtk.STOCK_APPLY,
                                                       Gtk.IconSize.MENU)
        scroll_direction_image.show()

        entry = Gtk.ImageMenuItem(label=_("Top <-> Bottom"))
        entry.connect("activate", self.cb_change_scroll_direction, False)
        if self.scroll_direction == False:
            entry.set_image(scroll_direction_image)
        entry.show()
        scroll_direction_menu.append(entry)

        entry = Gtk.ImageMenuItem(_("Left <-> Right"))
        entry.connect("activate", self.cb_change_scroll_direction, True)
        if self.scroll_direction == True:
            entry.set_image(scroll_direction_image)
        entry.show()
        scroll_direction_menu.append(entry)

        scroll_direction_menu.show()
        item.show()
        menu.append(item)

    def cb_build_missing_parent_nav_menu(self, obj, event,
                                         person_handle, family_handle):
        """Builds the menu for a missing parent."""
        self.menu = Gtk.Menu()
        self.menu.set_title(_('People Menu'))

        add_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ADD, None)
        add_item.connect("activate", self.cb_add_parents, person_handle,
                         family_handle)
        add_item.show()
        self.menu.append(add_item)

        # Add a separator line
        add_item = Gtk.SeparatorMenuItem()
        add_item.show()
        self.menu.append(add_item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(self.menu)
        self.add_settings_to_menu(self.menu)
        self.menu.popup(None, None, None, None, 0, event.time)
        return 1

    def cb_build_full_nav_menu(self, obj, event, person_handle, family_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children,
        and Parents) with navigation.
        """

        self.menu = Gtk.Menu()
        self.menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                            Gtk.IconSize.MENU)
        go_image.show()
        go_item = Gtk.ImageMenuItem(label=name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate", self.cb_childmenu_changed, person_handle)
        go_item.show()
        self.menu.append(go_item)

        edit_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_EDIT, None)
        edit_item.connect("activate", self.cb_edit_person, person_handle)
        edit_item.show()
        self.menu.append(edit_item)

        clipboard_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_COPY, None)
        clipboard_item.connect("activate", self.cb_copy_person_to_clipboard,
                               person_handle)
        clipboard_item.show()
        self.menu.append(clipboard_item)

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

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                Gtk.IconSize.MENU)
            go_image.show()
            sp_item = Gtk.ImageMenuItem(label=name_displayer.display(spouse))
            sp_item.set_image(go_image)
            linked_persons.append(sp_id)
            sp_item.connect("activate", self.cb_childmenu_changed, sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        self.menu.append(item)

        # Go over siblings and build their menu
        item = Gtk.MenuItem(label=_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for pfam in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(pfam)
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

                if find_children(self.dbstate.db, sib):
                    label = Gtk.Label(label='<b><i>%s</i></b>'
                                % escape(name_displayer.display(sib)))
                else:
                    label = Gtk.Label(label=escape(name_displayer.display(sib)))

                go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                    Gtk.IconSize.MENU)
                go_image.show()
                sib_item = Gtk.ImageMenuItem()
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0, 0)
                sib_item.add(label)
                linked_persons.append(sib_id)
                sib_item.connect("activate", self.cb_childmenu_changed, sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

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

            if find_children(self.dbstate.db, child):
                label = Gtk.Label(label='<b><i>%s</i></b>'
                            % escape(name_displayer.display(child)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                Gtk.IconSize.MENU)
            go_image.show()
            child_item = Gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate", self.cb_childmenu_changed,
                               child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db, person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db, par):
                label = Gtk.Label(label='<b><i>%s</i></b>'
                            % escape(name_displayer.display(par)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                Gtk.IconSize.MENU)
            go_image.show()
            par_item = Gtk.ImageMenuItem()
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate", self.cb_childmenu_changed, par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            if self.tree_style == 2 and not self.show_unknown_people:
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()
                par_item = Gtk.ImageMenuItem(label=_("Add New Parents..."))
                par_item.connect("activate", self.cb_add_parents, person_handle,
                         family_handle)
                par_item.show()
                par_menu.append(par_item)
            else:
                item.set_sensitive(0)
        item.show()
        self.menu.append(item)

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

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,
                                                Gtk.IconSize.MENU)
            go_image.show()
            per_item = Gtk.ImageMenuItem()
            per_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            per_item.add(label)
            per_item.connect("activate", self.cb_childmenu_changed, p_id)
            per_item.show()
            per_menu.append(per_item)

        if no_related:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Add separator line
        item = Gtk.SeparatorMenuItem()
        item.show()
        self.menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(self.menu)
        self.add_settings_to_menu(self.menu)
        self.menu.popup(None, None, None, None, 0, event.time)
        return 1

    def cb_build_relation_nav_menu(self, obj, event, family_handle):
        """Builds the menu for a parents-child relation line."""
        self.menu = Gtk.Menu()
        self.menu.set_title(_('Family Menu'))

        family = self.dbstate.db.get_family_from_handle(family_handle)
        if not family:
            return 0

        edit_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_EDIT, None)
        edit_item.connect("activate", self.cb_edit_family, family_handle)
        edit_item.show()
        self.menu.append(edit_item)

        clipboard_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_COPY, None)
        clipboard_item.connect("activate", self.cb_copy_family_to_clipboard,
                               family_handle)
        clipboard_item.show()
        self.menu.append(clipboard_item)

        # Add separator
        item = Gtk.SeparatorMenuItem()
        item.show()
        self.menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(self.menu)
        self.add_settings_to_menu(self.menu)
        self.menu.popup(None, None, None, None, 0, event.time)
        return 1
        
    def cb_update_show_images(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the images setting. 
        """
        if entry == 'True':
            self.show_images = True
        else:
            self.show_images = False
        self.rebuild_trees(self.get_active())

    def cb_update_show_marriage(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the marriage data setting. 
        """
        if entry == 'True':
            self.show_marriage_data = True
        else:
            self.show_marriage_data = False
        self.rebuild_trees(self.get_active())

    def cb_update_show_unknown_people(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the unknown people setting. 
        """
        if entry == 'True':
            self.show_unknown_people = True
        else:
            self.show_unknown_people = False
        self.rebuild_trees(self.get_active())

    def cb_update_layout(self, obj, constant):
        """
        Called when the configuration menu changes the layout. 
        """
        entry = obj.get_active()
        self._config.set(constant, entry)
        self.tree_style = int(entry)
        adj = self.config_size_slider.get_adjustment()
        if entry == 1: # Limit tree size to 5 for the compact style
            adj.set_upper(5)
            if self.force_size > 5:
                self.force_size = 5
                adj.set_value(5)
        else:
            adj.set_upper(9)
        adj.emit("changed")
        self.rebuild_trees(self.get_active())

    def cb_update_tree_direction(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the tree direction. 
        """
        self.tree_direction = int(entry)
        self.rebuild_trees(self.get_active())

    def cb_update_tree_size(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the tree size. 
        """
        self.force_size = int(entry)
        self.rebuild_trees(self.get_active())

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect('interface.pedview-show-images',
                          self.cb_update_show_images)
        self._config.connect('interface.pedview-show-marriage',
                          self.cb_update_show_marriage)
        self._config.connect('interface.pedview-show-unknown-people',
                          self.cb_update_show_unknown_people)
        self._config.connect('interface.pedview-tree-direction',
                          self.cb_update_tree_direction)
        self._config.connect('interface.pedview-tree-size',
                          self.cb_update_tree_size)

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the 
        notebook pages of the Configure dialog
        
        :return: list of functions
        """
        return [self.config_panel]

    def config_panel(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        """
        table = Gtk.Table(7, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        configdialog.add_checkbox(table, 
                _('Show images'), 
                0, 'interface.pedview-show-images')
        configdialog.add_checkbox(table, 
                _('Show marriage data'), 
                1, 'interface.pedview-show-marriage')
        configdialog.add_checkbox(table, 
                _('Show unknown people'), 
                2, 'interface.pedview-show-unknown-people')
        configdialog.add_combo(table, 
                _('Tree style'), 
                4, 'interface.pedview-layout',
                ((0, _('Standard')),
                (1, _('Compact')),
                (2, _('Expanded'))),
                callback=self.cb_update_layout)
        configdialog.add_combo(table, 
                _('Tree direction'), 
                5, 'interface.pedview-tree-direction',
                ((0, _(u'Vertical (↓)')),
                (1, _(u'Vertical (↑)')),
                (2, _(u'Horizontal (→)')),
                (3, _(u'Horizontal (←)'))))
        self.config_size_slider = configdialog.add_slider(table, 
                _('Tree size'), 
                6, 'interface.pedview-tree-size',
                (2, 9))

        return _('Layout'), table
