# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009       Yevgeny Zegzda <ezegjda@ya.ru>
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

# $Id: PedigreeView.py 11820 2009-02-03 10:33:19Z romjerome $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _
from gettext import ngettext
from cgi import escape
import math

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

try:
    import cairo
    cairo_available = True
except:
    cairo_available = False

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
import gui.views.pageview as PageView
from gui.views.navigationview import NavigationView
from BasicUtils import name_displayer
import Utils
import DateHandler
import ThumbNails
import Errors
from ReportBase import ReportUtils
from Editors import EditPerson, EditFamily
from DdTargets import DdTargets
import cPickle as pickle
import config
import Bookmarks
from QuestionDialog import RunDatabaseRepair, ErrorDialog

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_PERSON = "p"
_BORN = _('short for born|b.')
_DIED = _('short for died|d.')
_BAPT = _('short for baptized|bap.')
_CHRI = _('short for chistianized|chr.')
_BURI = _('short for buried|bur.')
_CREM = _('short for cremated|crem.')


class _PersonBoxWidgetOld(gtk.Button):
    """Old widget used before revision #5646"""
    def __init__(self, format_helper, person, maxlines, image=None):
        if person:
            gtk.Button.__init__(self,
                                format_helper.format_person(person, maxlines))
            gender = person.get_gender()
            if gender == gen.lib.Person.MALE:
                self.modify_bg(gtk.STATE_NORMAL,
                               self.get_colormap().alloc_color("#F5FFFF"))
            elif gender == gen.lib.Person.FEMALE:
                self.modify_bg(gtk.STATE_NORMAL,
                               self.get_colormap().alloc_color("#FFF5FF"))
            else:
                self.modify_bg(gtk.STATE_NORMAL,
                               self.get_colormap().alloc_color("#FFFFF5"))
        else:
            gtk.Button.__init__(self, "               ")
            #self.set_sensitive(False)
        self.format_helper = format_helper
        self.image = image
        self.set_alignment(0.0, 0.0)
        white = self.get_colormap().alloc_color("white")
        self.modify_bg(gtk.STATE_ACTIVE, white)
        self.modify_bg(gtk.STATE_PRELIGHT, white)
        self.modify_bg(gtk.STATE_SELECTED, white)


class _PersonWidgetBase:
    """
    Defualt set up for person widgets.
    Set up drag options and button release events.
    """
    def __init__(self, view, format_helper, person):
        self.view = view
        self.format_helper = format_helper
        self.person = person
        self.force_mouse_over = False
        if self.person:
            self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
            self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
            self.connect("button-release-event", self.on_button_release_cb)
            self.connect("drag_data_get", self.drag_data_get)
            self.connect("drag_begin", self.drag_begin_cb)
            # Enable drag
            self.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                [DdTargets.PERSON_LINK.target()]+
                                [t.target() for t in DdTargets._all_text_types],
                                gtk.gdk.ACTION_COPY)

    def drag_begin_cb(self, widget, data):
        """Set up some inital conditions for drag. Set up icon."""
        self.drag_source_set_icon_stock('gramps-person')

    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Returned parameters after drag.
        Specified for 'person-link', for others return text info about person.
        """
        if sel_data.target == DdTargets.PERSON_LINK.drag_type:
            data = (DdTargets.PERSON_LINK.drag_type,
                    id(self), self.person.get_handle(), 0)
            sel_data.set(sel_data.target, 8, pickle.dumps(data))
        else:
            sel_data.set(sel_data.target, 8,
                         self.format_helper.format_person(self.person, 11))

    def on_button_release_cb(self, widget, event):
        """
        Defualt action for release event from mouse.
        Change active person to current.
        """
        if event.button == 1 and event.type == gtk.gdk.BUTTON_RELEASE:
            self.view.on_childmenu_changed(None, self.person.get_handle())
            return True
        return False


class PersonBoxWidgetCairo(gtk.DrawingArea, _PersonWidgetBase):
    """Draw person box using cairo library"""
    def __init__(self,
                 view, format_helper, person, alive, maxlines, image=None):
        gtk.DrawingArea.__init__(self)
        _PersonWidgetBase.__init__(self, view, format_helper, person)
        # Required for popup menu
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        # Required for tooltip and mouse-over
        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        # Required for tooltip and mouse-over
        self.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        self.alive = alive
        self.maxlines = maxlines
        self.hightlight = False
        self.connect("expose_event", self.expose)
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
        self.image = image
        try:
            self.img_surf = cairo.ImageSurface.create_from_png(image)
        except:
            self.image = False
        # enable mouse-over
        self.connect("enter-notify-event", self.on_enter_cb)
        # enable mouse-out
        self.connect("leave-notify-event", self.on_leave_cb)
        self.set_size_request(120, 25)
        # GTK object use in realize and expose methods
        self.context = None
        self.textlayout = None

    def on_enter_cb(self, widget, event):
        """On mouse-over highlight border"""
        if self.person or self.force_mouse_over:
            self.hightlight = True
            self.queue_draw()

    def on_leave_cb(self, widget, event):
        """On mouse-out normal border"""
        self.hightlight = False
        self.queue_draw()

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display. Print text and resize element.
        """
        self.context = self.window.cairo_create()
        self.textlayout = self.context.create_layout()
        self.textlayout.set_font_description(self.get_style().font_desc)
        self.textlayout.set_markup(self.text)
        size = self.textlayout.get_pixel_size()
        xmin = size[0] + 12
        ymin = size[1] + 11
        if self.image:
            xmin += self.img_surf.get_width()
            ymin = max(ymin, self.img_surf.get_height()+4)
        self.set_size_request(max(xmin, 120), max(ymin, 25))

    def expose(self, widget, event):
        """
        Redrawing the contents of the widget.
        Creat new cairo object and draw in it all (borders, background and etc.)
        witout text.
        """
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
        self.context.set_source_rgba(self.bordercolor[0],
                                     self.bordercolor[1],
                                     self.bordercolor[2],
                                     0.4)
        self.context.fill_preserve()
        self.context.set_line_width(0)
        self.context.stroke()
        self.context.restore()

        # box shape used for clipping
        self.context.append_path(path)
        self.context.clip()

        # background
        self.context.append_path(path)
        self.context.set_source_rgb(self.bgcolor[0],
                                    self.bgcolor[1],
                                    self.bgcolor[2])
        self.context.fill_preserve()
        self.context.stroke()

        # image
        if self.image:
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
        self.context.set_source_rgb(self.bordercolor[0],
                                    self.bordercolor[1],
                                    self.bordercolor[2])
        self.context.stroke()


class PersonBoxWidget(gtk.DrawingArea, _PersonWidgetBase):
    """
    Draw person box using GC library.
    For version PyGTK < 2.8
    """
    def __init__(self,
                 view, format_helper, person, alive, maxlines, image=None):
        gtk.DrawingArea.__init__(self)
        _PersonWidgetBase.__init__(self, view, format_helper, person)
                        # Required for popup menu and other right mouse button click
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.BUTTON_RELEASE_MASK
                        # Required for tooltip and mouse-over
                        | gtk.gdk.ENTER_NOTIFY_MASK
                        # Required for tooltip and mouse-over
                        | gtk.gdk.LEAVE_NOTIFY_MASK)
        self.maxlines = maxlines
        self.alive = alive
        try:
            self.image = gtk.gdk.pixbuf_new_from_file(image)
        except:
            self.image = None
        self.connect("expose_event", self.expose)
        self.connect("realize", self.realize)
        text = ""
        if self.person:
            text = self.format_helper.format_person(self.person, self.maxlines)
            # enable mouse-over
            self.connect("enter-notify-event", self.on_enter_cb)
            self.connect("leave-notify-event", self.on_leave_cb)
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

    def on_enter_cb(self, widget, event):
        """On mouse-over highlight border"""
        self.border_gc.line_width = 3
        self.queue_draw()

    def on_leave_cb(self, widget, event):
        """On mouse-out normal border"""
        self.border_gc.line_width = 1
        self.queue_draw()

    def realize(self, widget):
        """
        Necessary actions when the widget is instantiated on a particular
        display. Creat all elements for person box(bg_gc, text_gc, border_gc,
        shadow_gc), and setup they style.
        """
        self.bg_gc = self.window.new_gc()
        self.text_gc = self.window.new_gc()
        self.border_gc = self.window.new_gc()
        self.border_gc.line_style = gtk.gdk.LINE_SOLID
        self.border_gc.line_width = 1
        self.shadow_gc = self.window.new_gc()
        self.shadow_gc.line_style = gtk.gdk.LINE_SOLID
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
            elif self.alive and \
                self.person.get_gender() == gen.lib.Person.FEMALE:
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


class FormattingHelper(object):
    """
    Formatting data in text for PedigreeView.
    From family, place or person return formated text used as content
    for display in widget.
    """
    def __init__(self, dbstate):
        self.dbstate = dbstate
        self._text_cache = {}
        self._markup_cache = {}

    def format_relation(self, family, line_count):
        """Return info about marriage in text format for display"""
        text = ""
        for event_ref in family.get_event_ref_list():
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            if event and event.get_type() == gen.lib.EventType.MARRIAGE:
                if line_count < 3:
                    return DateHandler.get_date(event)
                name = str(event.get_type())
                text += name
                text += "\n"
                text += DateHandler.get_date(event)
                text += "\n"
                text += self.get_place_name(event.get_place_handle())
                if line_count < 5:
                    return text
                break
        if not text:
            text = str(family.get_relationship())
        return text

    def get_place_name(self, place_handle):
        """Return place name from place_handle and format string for display"""
        text = ""
        place = self.dbstate.db.get_place_from_handle(place_handle)
        if place:
            place_title = \
                self.dbstate.db.get_place_from_handle(place_handle).get_title()
            if place_title != "":
                if len(place_title) > 25:
                    text = place_title[:24]+"..."
                else:
                    text = place_title
        return text

    def format_person(self, person, line_count, use_markup=False):
        """Return info about person in text format for display"""
        if not person:
            return ""
        if use_markup:
            if person.handle in self._markup_cache:
                if line_count in self._markup_cache[person.handle]:
                    return self._markup_cache[person.handle][line_count]
            name = escape(name_displayer.display(person))
        else:
            if person.handle in self._text_cache:
                if line_count in self._text_cache[person.handle]:
                    return self._text_cache[person.handle][line_count]
            name = name_displayer.display(person)
        text = name
        if line_count >= 3:
            birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, person)
            if birth and use_markup and \
               birth.get_type() != gen.lib.EventType.BIRTH:
                bdate  = "<i>%s</i>" % \
                    escape(DateHandler.get_date(birth))
                bplace = "<i>%s</i>" % \
                    escape(self.get_place_name(birth.get_place_handle()))
            elif birth and use_markup:
                bdate  = escape(DateHandler.get_date(birth))
                bplace = escape(self.get_place_name(birth.get_place_handle()))
            elif birth:
                bdate  = DateHandler.get_date(birth)
                bplace = self.get_place_name(birth.get_place_handle())
            else:
                bdate = ""
                bplace = ""
            death = ReportUtils.get_death_or_fallback(self.dbstate.db, person)
            if death and use_markup and \
               death.get_type() != gen.lib.EventType.DEATH:
                ddate  = "<i>%s</i>" % \
                    escape(DateHandler.get_date(death))
                dplace = "<i>%s</i>" % \
                    escape(self.get_place_name(death.get_place_handle()))
            elif death and use_markup:
                ddate  = escape(DateHandler.get_date(death))
                dplace = escape(self.get_place_name(death.get_place_handle()))
            elif death:
                ddate  = DateHandler.get_date(death)
                dplace = self.get_place_name(death.get_place_handle())
            else:
                ddate = ""
                dplace = ""

            if line_count < 5:
                text = "%s\n* %s\n+ %s" % (name, bdate, ddate)
            else:
                text = "%s\n* %s\n  %s\n+ %s\n  %s" % (name, bdate, bplace,
                                                       ddate, dplace)
        if use_markup:
            if not person.handle in self._markup_cache:
                self._markup_cache[person.handle] = {}
            self._markup_cache[person.handle][line_count] = text
        else:
            if not person.handle in self._text_cache:
                self._text_cache[person.handle] = {}
            self._text_cache[person.handle][line_count] = text
        return text

    def clear_cache(self):
        """Clear old caching data for rebuild"""
        self._text_cache = {}
        self._markup_cache = {}


#-------------------------------------------------------------------------
#
# PedigreeView
#
#-------------------------------------------------------------------------
class PedigreeViewExt(NavigationView):
    """
    View for pedigree tree.
    Displays the ancestors of a selected individual.
    """

    def __init__(self, dbstate, uistate):
        NavigationView.__init__(self, _('Pedigree'), dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      Bookmarks.Bookmarks)

        self.func_list = {
            'F2' : self.kb_goto_home,
            'F3' : self.kb_change_style,
            'F4' : self.kb_change_direction,
            'F6' : self.kb_plus_generation,
            'F5' : self.kb_minus_generation,
            '<CONTROL>J' : self.jump,
            }

        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.change_db)
        # Automatic resize
        self.force_size = config.get('interface.pedviewext-tree-size') 
        # Nice tree
        self.tree_style = config.get('interface.pedviewext-layout')
        # Show photos of persons
        self.show_images = config.get('interface.pedviewext-show-images')
        # Hide marriage data by default
        self.show_marriage_data = config.get(
                                'interface.pedviewext-show-marriage')
        # Tree draw direction
        self.tree_direction = config.get('interface.pedviewext-tree-direction')
        # Show on not unknown peoples.
        # Default - not show, for mo fast display hight tree
        self.show_unknown_peoples = config.get(
                                'interface.pedviewext-show-unknown-peoples')
        
        self.format_helper = FormattingHelper( self.dbstate)
        
        # Depth of tree.
        self._depth = 1
        # Variables for drag and scroll
        self._last_x = 0
        self._last_y = 0
        self._in_move = False
        # Change or nor mouse whell scroll direction
        self.scroll_direction = config.get(
                                'interface.pedviewext-scroll-direction')
        self.key_active_changed = None
        # GTK objects
        self.tooltips = None
        self.scrolledwindow = None
        self.table = None

    def change_page(self):
        """Called when the page changes."""
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()

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
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.ScrolledWindow page.
        """
        self.tooltips = gtk.Tooltips()
        self.tooltips.enable()

        self.scrolledwindow = gtk.ScrolledWindow(None, None)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.add_events(gtk.gdk.SCROLL_MASK)
        self.scrolledwindow.connect("scroll-event", self.bg_scroll_event)
        event_box = gtk.EventBox()
        # Required for drag-scroll events and popup menu
        event_box.add_events(gtk.gdk.BUTTON_PRESS_MASK
                             | gtk.gdk.BUTTON_RELEASE_MASK
                             | gtk.gdk.BUTTON1_MOTION_MASK)
        # Signal begin drag-scroll
        event_box.connect("button-press-event", self.bg_button_press_cb)
        # Signal end drag-scroll and popup menu
        event_box.connect("button-release-event", self.bg_button_release_cb)
        #Signal for controll motion-notify when left mouse button pressed
        event_box.connect("motion-notify-event", self.bg_motion_notify_event_cb)
        self.scrolledwindow.add_with_viewport(event_box)

        self.table = gtk.Table(1, 1, False)
        event_box.add(self.table)
        event_box.get_parent().set_shadow_type(gtk.SHADOW_NONE)
        self.table.set_row_spacings(1)
        self.table.set_col_spacings(0)

        return self.scrolledwindow

    def ui_definition(self):
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
                        callback=self.filter_editor)

    def filter_editor(self, obj):
        from FilterEditor import FilterEditor

        try:
            FilterEditor('Person', const.CUSTOM_FILTERS, 
                         self.dbstate, self.uistate)
        except Errors.WindowActiveError:
            return

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        try:
            active = self.dbstate.get_active_person()
            if active:
                self.rebuild_trees(active.handle)
            else:
                self.rebuild_trees(None)
        except AttributeError, msg:
            RunDatabaseRepair(str(msg))

    def change_db(self, db):
        """
        Callback associated with DbState. Whenever the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tree
        is no need to store the database, since we will get the value
        from self.state.db
        """
        db.connect('person-add', self.person_rebuild)
        db.connect('person-update', self.person_rebuild)
        db.connect('person-delete', self.person_rebuild)
        db.connect('person-rebuild', self.person_rebuild_bm)
        db.connect('family-update', self.person_rebuild)
        db.connect('family-add', self.person_rebuild)
        db.connect('family-delete', self.person_rebuild)
        db.connect('family-rebuild', self.person_rebuild)
        self.bookmarks.update_bookmarks(self.dbstate.db.get_bookmarks())
        if self.active:
            self.bookmarks.redraw()
        self.build_tree()

    def navigation_type(self):
        return PageView.NAVIGATION_PERSON

    def goto_handle(self, handle=None):
        """Callback function for change active person in other GRAMPS page."""
        self.dirty = True
        if handle:
            self.rebuild_trees(handle)
            self.handle_history(handle)
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
        if self.dbstate.active:
            self.rebuild_trees(self.dbstate.active.handle)
        else:
            self.rebuild_trees(None)

    def rebuild_trees(self, person_handle):
        """
        Rebild tree with root person_handle.
        Called from many fuctions, when need full redraw tree.
        """

        self.dirty = False

        person = None
        if person_handle:
            person = self.dbstate.db.get_person_from_handle(person_handle)

        if self.tree_style != 2 and \
           (self.force_size > 5 or self.force_size == 0):
            self.force_size = 5

        # format of the definition is:
        # ((each box of the pedigree has a node here),
        #  ((person data), (connection line), (marriage data)),
        #  ((person box position and size),(parent relation box),
        #   (marriage data)),
        #  ((or for another design),((fater relation box),
        #   (mother relation box)),(marriage data)))
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
        elif self.tree_style == 0:
            if self.force_size == 2:
                pos = (((0, 0, 1, 3), (1, 0, 3), (2, 1, 1, 1)),
                        ((2, 0, 1, 1), None, None),
                        ((2, 2, 1, 1), None, None))
            elif self.force_size == 3:
                pos = (((0, 2, 1, 3), (1, 1, 5), (2, 3, 1, 1)),
                      ((2, 0, 1, 3), (3, 0, 3), (4, 1, 1, 1)),
                      ((2, 4, 1, 3), (3, 4, 3), (4, 5, 1, 1)),
                      ((4, 0, 1, 1), None, None),
                      ((4, 2, 1, 1), None, None),
                      ((4, 4, 1, 1), None, None),
                      ((4, 6, 1, 1), None, None))
            elif self.force_size == 4:
                pos = (((0, 6, 1, 3), (1, 3, 9), (2, 5, 1, 5)),
                      ((2, 2, 1, 3), (3, 1, 5), (4, 3, 1, 1)),
                      ((2, 10, 1, 3), (3, 9, 5), (4, 11, 1, 1)),
                      ((4, 0, 1, 3), (5, 0, 3), (6, 1, 1, 1)),
                      ((4, 4, 1, 3), (5, 4, 3), (6, 5, 1, 1)),
                      ((4, 8, 1, 3), (5, 8, 3), (6, 9, 1, 1)),
                      ((4, 12, 1, 3), (5, 12, 3), (6, 13, 1, 1)),
                      ((6, 0, 1, 1), None, None),
                      ((6, 2, 1, 1), None, None),
                      ((6, 4, 1, 1), None, None),
                      ((6, 6, 1, 1), None, None),
                      ((6, 8, 1, 1), None, None),
                      ((6, 10, 1, 1), None, None),
                      ((6, 12, 1, 1), None, None),
                      ((6, 14, 1, 1), None, None))
            elif self.force_size == 5:
                pos = (((0, 14, 1, 3), (1, 7, 17), (2, 13, 1, 5)),
                      ((2, 6, 1, 3), (3, 3, 9), (4, 5, 1, 5)),
                      ((2, 22, 1, 3), (3, 19, 9), (4, 21, 1, 5)),
                      ((4, 2, 1, 3), (5, 1, 5), (6, 3, 1, 1)),
                      ((4, 10, 1, 3), (5, 9, 5), (6, 11, 1, 1)),
                      ((4, 18, 1, 3), (5, 17, 5), (6, 19, 1, 1)),
                      ((4, 26, 1, 3), (5, 25, 5), (6, 27, 1, 1)),
                      ((6, 0, 1, 3), (7, 0, 3), (8, 1, 1, 1)),
                      ((6, 4, 1, 3), (7, 4, 3), (8, 5, 1, 1)),
                      ((6, 8, 1, 3), (7, 8, 3), (8, 9, 1, 1)),
                      ((6, 12, 1, 3), (7, 12, 3), (8, 13, 1, 1)),
                      ((6, 16, 1, 3), (7, 16, 3), (8, 17, 1, 1)),
                      ((6, 20, 1, 3), (7, 20, 3), (8, 21, 1, 1)),
                      ((6, 24, 1, 3), (7, 24, 3), (8, 25, 1, 1)),
                      ((6, 28, 1, 3), (7, 28, 3), (8, 29, 1, 1)),
                      ((8, 0, 1, 1), None, None),
                      ((8, 2, 1, 1), None, None),
                      ((8, 4, 1, 1), None, None),
                      ((8, 6, 1, 1), None, None),
                      ((8, 8, 1, 1), None, None),
                      ((8, 10, 1, 1), None, None),
                      ((8, 12, 1, 1), None, None),
                      ((8, 14, 1, 1), None, None),
                      ((8, 16, 1, 1), None, None),
                      ((8, 18, 1, 1), None, None),
                      ((8, 20, 1, 1), None, None),
                      ((8, 22, 1, 1), None, None),
                      ((8, 24, 1, 1), None, None),
                      ((8, 26, 1, 1), None, None),
                      ((8, 28, 1, 1), None, None),
                      ((8, 30, 1, 1), None, None))
        elif self.tree_style == 2:
            pos = None

        # Build ancestor tree only one for all different sizes
        self._depth = 1
        lst = [None] * (1 << self.force_size) # [None] * (2**self.force_size)
        self.find_tree(person, 0, 1, lst)

        self.rebuild(self.table, pos, person, lst, self.force_size)

    def rebuild(self, table_widget, positions, active_person, lst, size):
        """
        Function called from rebuild_trees.
        For table_widget (gtk.Table) place list of person, use positions array.
        For style C position calculated, for others style use static posotins.
        All display options process in this function.
        """

        if not active_person:
            return

        # Purge current table content
        for child in table_widget.get_children():
            child.destroy()
        table_widget.resize(1, 1)

        xmax = 0
        ymax = 0
        if self.tree_style == 2:
            # For style C change tree depth if they real size less then max.
            if self.show_unknown_peoples:
                self._depth += 1
            if size > self._depth:
                size = self._depth
            # Calculate max X and Y for style C
            if self.tree_direction == 0 or self.tree_direction == 1:
                xmax = 1 << size # xmax = (1 + 1)**size
                ymax = (size << 2) + 1 # ymax = (3 + 1) * size + 1
            else:
                xmax = size << 1 # xmax = 2 * size
                ymax = 1 << (size + 1) # ymax = 2**size * 2
        #for i in range(0, 2**size - 1):
        for i in range(0, (1<<size) - 1):
            # Table placement for person data
            if self.tree_style == 2:
                # Dynamic position person in tree
                width = _width = 1
                height = _height = 3
                if self.tree_direction == 0 or self.tree_direction == 1:
                    _height = width
                    _width = height
                _x = int(math.log(i+1, 2))
                x = (1 + _width) * _x + 1
                # _y = i + 1 - (2**_x)
                _y = i + 1 - (1 << _x)
                # _delta = (2**size) / (2**_x) / 2 * (_height + 1)
                _delta = (1 << size - _x - 1) * (_height + 1)
                # y = _delta / 2 + _y * _delta - 1
                y = (_delta >> 1) + _y * _delta - 1
                if self.tree_direction == 3:
                    x = x - 1
                elif self.tree_direction == 0 or self.tree_direction == 1:
                    y += 1
            else:
                try:
                    x = positions[i][0][0]+1
                    y = positions[i][0][1]+1
                    width = positions[i][0][2]
                    height = positions[i][0][3]
                except IndexError:  # no position for this person defined
                    continue
            if not lst[i] and \
               ((self.tree_style == 2 and self.show_unknown_peoples and
               lst[((i+1)>>1)-1]) or self.tree_style != 2):
                # No person -> show empty box
                if cairo_available:
                    pbw = PersonBoxWidgetCairo(
                        self, self.format_helper, None, False, 0, None)
                else:
                    pbw = PersonBoxWidget(
                        self, self.format_helper, None, False, 0, None)
                if i > 0 and lst[((i+1)>>1)-1]: # ((i+1)/2
                    fam_h = None
                    fam = lst[((i+1)>>1)-1][2]
                    if fam:
                        fam_h = fam.get_handle()
                    if not self.dbstate.db.readonly:
                        pbw.connect("button-press-event",
                                    self.missing_parent_button_press_cb,
                                    lst[((i+1)>>1)-1][0].get_handle(), fam_h)
                        pbw.force_mouse_over = True
                if self.tree_style != 2 or self.tree_direction == 2:
                    if width > 1:
                        table_widget.attach(pbw, x, x+width, y, y+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, x, x+width, y, y+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                    if x+width > xmax:
                        xmax = x+width
                    if y+height > ymax:
                        ymax = y+height
                elif self.tree_direction == 0:
                    if width > 1:
                        table_widget.attach(pbw, y, y+width, x, x+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, y, y+width, x, x+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                # Rotate tree for others tree directions
                elif self.tree_direction == 1:
                    if width > 1:
                        table_widget.attach(pbw, y, y+width, ymax-(x+height),
                                            ymax-x, gtk.FILL, gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, y, y+width, ymax-(x+height),
                                            ymax-x, gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 3:
                    if width > 1:
                        table_widget.attach(pbw, xmax-(x+width), xmax-x, y,
                                            y+height, gtk.FILL, gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, xmax-(x+width), xmax-x, y,
                                            y+height, gtk.FILL, gtk.FILL, 0, 0)
            elif lst[i]:
                # Get foto
                image = None
                #if self.show_images and i < ((2**size-1)/2) and height > 1:
                if self.show_images and height > 1 and \
                   (i < (((1<<size)-1)>>1) or self.tree_style == 2):
                    media_list = lst[i][0].get_media_list()
                    if media_list:
                        photo = media_list[0]
                        object_handle = photo.get_reference_handle()
                        obj = self.dbstate.db.get_object_from_handle(
                            object_handle)
                        if obj:
                            mtype = obj.get_mime_type()
                            if mtype and mtype[0:5] == "image":
                                image = ThumbNails.get_thumbnail_path(
                                            Utils.media_path_full(
                                                        self.dbstate.db,
                                                        obj.get_path()),
                                            rectangle=photo.get_rectangle())
                if cairo_available:
                    pbw = PersonBoxWidgetCairo(self, self.format_helper,
                        lst[i][0], lst[i][3], height, image)
                else:
                    pbw = PersonBoxWidget(self, self.format_helper,
                        lst[i][0], lst[i][3], height, image)
                if height < 7:
                    self.tooltips.set_tip(pbw,
                        self.format_helper.format_person(lst[i][0], 11))

                fam_h = None
                if lst[i][2]:
                    fam_h = lst[i][2].get_handle()
                pbw.connect("button-press-event",
                            self.person_button_press_cb,
                            lst[i][0].get_handle(), fam_h)
                if self.tree_style != 2 or self.tree_direction == 2:
                    if width > 1:
                        table_widget.attach(pbw, x, x+width, y, y+height,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, x, x+width, y, y+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                    if x+width > xmax:
                        xmax = x+width
                    if y+height > ymax:
                        ymax = y+height
                elif self.tree_direction == 0:
                    if width > 1:
                        table_widget.attach(pbw, y, y+width, x, x+height,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw, y, y+width, x, x+height,
                                            gtk.FILL, gtk.FILL, 0, 0)
                # Rotate tree for others tree directions
                elif self.tree_direction == 1:
                    if width > 1:
                        table_widget.attach(pbw,
                            y, y+width, ymax-(x+height), ymax-x,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw,
                            y, y+width, ymax-(x+height), ymax-x,
                            gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 3:
                    if width > 1:
                        table_widget.attach(pbw,
                            xmax-(x+width), xmax-x, y, y+height,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
                    else:
                        table_widget.attach(pbw,
                            xmax-(x+width), xmax-x, y, y+height,
                            gtk.FILL, gtk.FILL, 0, 0)

            # Connection lines
            if self.tree_style != 2 and \
               positions[i][1] and len(positions[i][1]) == 2:
                # separate boxes for father and mother
                x = positions[i][1][0][0]+1
                y = positions[i][1][0][1]+1
                width = 1
                height = positions[i][1][0][2]
                line = gtk.DrawingArea()
                line.set_size_request(20, -1)
                line.connect("expose-event", self.line_expose_cb)
                if lst[i] and lst[i][2]:
                    # Required for popup menu
                    line.add_events(gtk.gdk.BUTTON_PRESS_MASK)
                    line.connect("button-press-event",
                                 self.relation_button_press_cb,
                                 lst[i][2].get_handle())
                line.set_data("idx", (i<<1)+1) # i*2+1
                if lst[(i<<1)+1]:
                    line.set_data("rela", lst[(i<<1)+1][1])
                table_widget.attach(line, x, x+width, y, y+height,
                                    gtk.FILL, gtk.FILL, 0, 0)
                if x+width > xmax:
                    xmax = x+width
                if y+height > ymax:
                    ymax = y+height

                # x = positions[i][1][1][0]+1
                # y = positions[i][1][1][1]+1
                # w = 1
                # h = positions[i][1][1][2]
                line = gtk.DrawingArea()
                line.set_size_request(20, -1)
                line.connect("expose-event", self.line_expose_cb)
                if lst[i] and lst[i][2]:
                    # Required for popup menu
                    line.add_events(gtk.gdk.BUTTON_PRESS_MASK)
                    line.connect("button-press-event",
                                 self.relation_button_press_cb,
                                 lst[i][2].get_handle())
                line.set_data("idx", (i+1)<<1) # i*2+2
                if lst[(i+1)<<1]:
                    line.set_data("rela", lst[(i+1)<<1][1])
                table_widget.attach(line, x, x+width, y, y+height,
                                    gtk.FILL, gtk.FILL, 0, 0)
                if x+width > xmax:
                    xmax = x+width
                if y+height > ymax:
                    ymax = y+height
            elif (self.tree_style != 2 and
                positions[i][1] and len(positions[i][1]) == 3) or \
                (self.tree_style == 2 and (_x+1) < size and lst[i]):
                # combined for father and mother
                if self.tree_style == 2:
                    x = (1 + _width) * (_x + 1)
                    # y = _delta/4 + _y*_delta-1+_height/2
                    y = (_delta >> 2) + _y*_delta-1 + (_height >> 1)
                    width = 1
                    height = (_delta >> 1)+1 # _delta/2+1
                    if self.tree_direction == 3:
                        x = x - 1
                    elif self.tree_direction == 0 or self.tree_direction == 1:
                        y = y + 1
                else:
                    x = positions[i][1][0]+1
                    y = positions[i][1][1]+1
                    width = 1
                    height = positions[i][1][2]
                line = gtk.DrawingArea()
                line.set_size_request(20, 20)
                line.connect("expose-event", self.tree_expose_cb)
                if lst[i] and lst[i][2]:
                    # Required for popup menu
                    line.add_events(gtk.gdk.BUTTON_PRESS_MASK)
                    line.connect("button-press-event",
                                 self.relation_button_press_cb,
                                 lst[i][2].get_handle())
                line.set_data("height", height)
                if lst[i] and lst[i][2]:
                    # Required for tooltip and mouse-over
                    line.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
                    # Required for tooltip and mouse-over
                    line.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
                    self.tooltips.set_tip(line,
                        self.format_helper.format_relation(lst[i][2], 11))
                if lst[(i<<1)+1]: # i*2+1
                    line.set_data("frela", lst[(i<<1)+1][1])
                if lst[(i+1)<<1]: # i*2+2
                    line.set_data("mrela", lst[(i+1)<<1][1])
                if self.tree_style != 2 or self.tree_direction == 2:
                    table_widget.attach(line, x, x+width, y, y+height,
                                        gtk.FILL, gtk.FILL, 0, 0)
                    if x+width > xmax:
                        xmax = x+width
                    if y+height > ymax:
                        ymax = y+height
                # Rotate tree for others tree directions
                elif self.tree_direction == 0:
                    table_widget.attach(line, y, y+height, x, x+width,
                                        gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 1:
                    table_widget.attach(line, y, y+height, ymax-(x+width),
                                        ymax-x, gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 3:
                    table_widget.attach(line, xmax-(x+width), xmax-x, y,
                                        y+height, gtk.FILL, gtk.FILL, 0, 0)

            # Show marriage data
            if self.show_marriage_data and \
               ((self.tree_style != 2 and positions[i][2]) or
               (self.tree_style == 2 and (_x+1) < size)):
                if lst[i] and lst[i][2]:
                    text = self.format_helper.format_relation(lst[i][2], 1)
                else:
                    text = " "
                label = gtk.Label(text)
                label.set_justify(gtk.JUSTIFY_LEFT)
                label.set_line_wrap(True)
                label.set_alignment(0.1, 0.5)
                if self.tree_style == 2:
                    x = (1 + _width) * (_x + 1) + 1
                    # y = _delta / 2 + _y * _delta -1 + _height / 2
                    y = (_delta >> 1) + _y * _delta - 1 + (_height >> 1)
                    width = 1
                    height = 1
                    if self.tree_direction == 3:
                        x = x - 1
                    elif self.tree_direction == 0 or self.tree_direction == 1:
                        y = y + 1
                else:
                    x = positions[i][2][0]+1
                    y = positions[i][2][1]+1
                    width = positions[i][2][2]
                    height = positions[i][2][3]
                if self.tree_style != 2 or self.tree_direction == 2:
                    table_widget.attach(label, x, x+width, y, y+height,
                                        gtk.FILL, gtk.FILL, 0, 0)
                # Rotate tree for others tree directions
                elif self.tree_direction == 0:
                    table_widget.attach(label, y, y+width, x, x+height,
                                        gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 1:
                    table_widget.attach(label, y, y+width, ymax-(x+height),
                                        ymax-x, gtk.FILL, gtk.FILL, 0, 0)
                elif self.tree_direction == 3:
                    table_widget.attach(label, xmax-(x+width), xmax-x, y,
                                        y+height, gtk.FILL, gtk.FILL, 0, 0)

        # Add navigation arrows
        if lst[0]:
            if self.tree_style != 2 or self.tree_direction == 2:
                arrow_top = gtk.ARROW_LEFT
                arrow_buttom = gtk.ARROW_RIGHT
            elif self.tree_direction == 0:
                arrow_top = gtk.ARROW_UP
                arrow_buttom = gtk.ARROW_DOWN
            elif self.tree_direction == 1:
                arrow_top = gtk.ARROW_DOWN
                arrow_buttom = gtk.ARROW_UP
            elif self.tree_direction == 3:
                arrow_top = gtk.ARROW_RIGHT
                arrow_buttom = gtk.ARROW_LEFT

            button = gtk.Button()
            button.add(gtk.Arrow(arrow_top, gtk.SHADOW_IN))
            childlist = find_children(self.dbstate.db, lst[0][0])
            if childlist:
                button.connect("clicked", self.on_show_child_menu)
                self.tooltips.set_tip(button, _("Jump to child..."))
            else:
                button.set_sensitive(False)
            if self.tree_style != 2 or self.tree_direction == 2:
                ymid = int(math.floor(ymax/2))
                table_widget.attach(button, 0, 1, ymid, ymid+1, 0, 0, 0, 0)
            elif self.tree_direction == 0:
                xmid = int(math.floor(xmax/2))
                table_widget.attach(button, xmid, xmid+1, 0, 1, 0, 0, 0, 0)
            elif self.tree_direction == 1:
                xmid = int(math.floor(xmax/2))
                table_widget.attach(button, xmid, xmid+1, ymax, ymax+1,
                                    0, 0, 0, 0)
            elif self.tree_direction == 3:
                ymid = int(math.floor(ymax/2))
                table_widget.attach(button, xmax, xmax+1, ymid, ymid+1,
                                    0, 0, 0, 0)

            button = gtk.Button()
            button.add(gtk.Arrow(arrow_buttom, gtk.SHADOW_IN))
            if lst[1]:
                button.connect("clicked", self.on_childmenu_changed,
                          lst[1][0].handle)
                self.tooltips.set_tip(button, _("Jump to father"))
            else:
                button.set_sensitive(False)
            if self.tree_style != 2 or self.tree_direction == 2:
                ymid = int(math.floor(ymax/4))
                table_widget.attach(button, xmax, xmax+1, ymid-1, ymid+2,
                                    0, 0, 0, 0)
            elif self.tree_direction == 0:
                xmid = int(math.floor(xmax/4))
                table_widget.attach(button, xmid-1, xmid+2, ymax, ymax+1,
                                    0, 0, 0, 0)
            elif self.tree_direction == 1:
                xmid = int(math.floor(xmax/4))
                table_widget.attach(button, xmid-1, xmid+2, 0, 1, 0, 0, 0, 0)
            elif self.tree_direction == 3:
                ymid = int(math.floor(ymax/4))
                table_widget.attach(button, 0, 1, ymid-1, ymid+2, 0, 0, 0, 0)

            button = gtk.Button()
            button.add(gtk.Arrow(arrow_buttom, gtk.SHADOW_IN))
            if lst[2]:
                button.connect("clicked", self.on_childmenu_changed,
                          lst[2][0].handle)
                self.tooltips.set_tip(button, _("Jump to mother"))
            else:
                button.set_sensitive(False)
            if self.tree_style != 2 or self.tree_direction == 2:
                ymid = int(math.floor(ymax/4*3))
                table_widget.attach(button, xmax, xmax+1, ymid-1, ymid+2,
                                    0, 0, 0, 0)
            elif self.tree_direction == 0:
                xmid = int(math.floor(xmax/4*3))
                table_widget.attach(button, xmid-1, xmid+2, ymax, ymax+1,
                                    0, 0, 0, 0)
            elif self.tree_direction == 1:
                xmid = int(math.floor(xmax/4*3))
                table_widget.attach(button, xmid-1, xmid+2, 0, 1, 0, 0, 0, 0)
            elif self.tree_direction == 3:
                ymid = int(math.floor(ymax/4*3))
                table_widget.attach(button, 0, 1, ymid-1, ymid+2, 0, 0, 0, 0)

        # add dummy widgets into the corners of the table
        # to allow the pedigree to be centered
        label = gtk.Label("")
        table_widget.attach(label, 0, 1, 0, 1,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
        label = gtk.Label("")
        table_widget.attach(label, xmax, xmax+1, ymax, ymax+1,
                            gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)

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
                for x in range(left, right):
                    for y in range(top, bottom):
                        try:
                            used_cells[x][y] = True
                        except KeyError:
                            used_cells[x] = {}
                            used_cells[x][y] = True
                        if y > ymax:
                            ymax = y
                    if x > xmax:
                        xmax = x
            for x in range(0, xmax+1):
                for y in range(0, ymax+1):
                    try:
                        tmp = used_cells[x][y]
                    except KeyError:
                        # fill unused cells
                        label = gtk.Label("%d,%d"%(x, y))
                        frame = gtk.ScrolledWindow(None, None)
                        frame.set_shadow_type(gtk.SHADOW_NONE)
                        frame.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
                        frame.add_with_viewport(label)
                        table_widget.attach(frame, x, x+1, y, y+1,
                                            gtk.FILL, gtk.FILL, 0, 0)
        table_widget.show_all()

        # Setup scrollbars for view root person
        window = table_widget.get_parent().get_parent()
        hadjustment = window.get_hadjustment()
        vadjustment = window.get_vadjustment()
        if self.tree_style != 2 or self.tree_direction == 2:
            self.update_scrollbar_positions(hadjustment, hadjustment.lower)
            self.update_scrollbar_positions(vadjustment,
                (vadjustment.upper - vadjustment.page_size) / 2)
        elif self.tree_direction == 0:
            self.update_scrollbar_positions(hadjustment,
                (hadjustment.upper - hadjustment.page_size) / 2)
            self.update_scrollbar_positions(vadjustment,
                vadjustment.upper - vadjustment.page_size)
        elif self.tree_direction == 1:
            self.update_scrollbar_positions(hadjustment,
                (hadjustment.upper - hadjustment.page_size) / 2)
            self.update_scrollbar_positions(vadjustment, vadjustment.lower)
        elif self.tree_direction == 3:
            self.update_scrollbar_positions(hadjustment,
                hadjustment.upper - hadjustment.page_size)
            self.update_scrollbar_positions(vadjustment,
                (vadjustment.upper - vadjustment.page_size) / 2)

        # Setup mouse whell scroll direction for styce C,
        # depending of tree direction
        if self.tree_style == 2:
            if self.tree_direction in [0, 1]:
                self.change_scroll_direction_cb(None, True)
            elif self.tree_direction in [2, 3]:
                self.change_scroll_direction_cb(None, False)

    def line_expose_cb(self, area, event):
        """Expose tree lines for style B."""
        gc = area.window.new_gc()
        alloc = area.get_allocation()
        idx = area.get_data("idx")
        rela = area.get_data("rela")
        if not rela:
            gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
        else:
            gc.line_style = gtk.gdk.LINE_SOLID
        gc.line_width = 3
        if idx % 2 == 0:
            area.window.draw_line(gc, alloc.width, alloc.height>>1,
                                  alloc.width>>1, alloc.height>>1)
            area.window.draw_line(gc, alloc.width>>1, 0,
                                  alloc.width>>1, alloc.height>>1)
        else:
            area.window.draw_line(gc, alloc.width, alloc.height>>1,
                                  alloc.width>>1, alloc.height>>1)
            area.window.draw_line(gc, alloc.width>>1, alloc.height,
                                  alloc.width>>1, alloc.height>>1)

    def tree_expose_cb(self, area, event):
        """
        Expose tree lines for style A and C.
        For style C check options show unknown peoples and tree direction.
        """
        gc = area.window.new_gc()
        alloc = area.get_allocation()
        height = area.get_data("height")
        frela = area.get_data("frela")
        mrela = area.get_data("mrela")
        if not frela and not mrela:
            gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
        else:
            gc.line_style = gtk.gdk.LINE_SOLID
        gc.line_width = 3
        rela = area.get_data("mrela")
        if self.tree_style != 2 or self.tree_direction == 2:
            gap = alloc.height / (height<<1)
            if self.tree_style == 2 and \
               (self.show_unknown_peoples or
               (not self.show_unknown_peoples and (frela or mrela))) or \
               self.tree_style != 2:
                area.window.draw_line(gc, 0, alloc.height>>1,
                                      alloc.width>>1, alloc.height>>1)

            if self.tree_style == 2 and \
               (self.show_unknown_peoples or
               (not self.show_unknown_peoples and frela)) or \
               self.tree_style != 2:
                if not frela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width>>1, gap)
                area.window.draw_line(gc, alloc.width>>1, gap,
                                      alloc.width, gap)

            if self.tree_style == 2 and \
               (self.show_unknown_peoples or
               (not self.show_unknown_peoples and mrela)) or \
               self.tree_style != 2:
                if not mrela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width>>1, alloc.height-gap)
                area.window.draw_line(gc, alloc.width>>1, alloc.height-gap,
                                      alloc.width, alloc.height-gap)
        elif self.tree_direction == 0:
            gap = alloc.width / (height<<1)
            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and (frela or mrela)):
                area.window.draw_line(gc, alloc.width>>1, 0,
                                      alloc.width>>1, alloc.height>>1)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and frela):
                if not frela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      gap, alloc.height>>1)
                area.window.draw_line(gc, gap, alloc.height>>1,
                                      gap, alloc.height)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and mrela):
                if not mrela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width-gap, alloc.height>>1)
                area.window.draw_line(gc, alloc.width-gap, alloc.height>>1,
                                      alloc.width-gap, alloc.height)
        elif self.tree_direction == 1:
            gap = alloc.width / (height<<1)
            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and (frela or mrela)):
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width>>1, alloc.height)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and frela):
                if not frela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      gap, alloc.height>>1)
                area.window.draw_line(gc, gap, 0, gap, alloc.height>>1)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and mrela):
                if not mrela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width-gap, alloc.height>>1)
                area.window.draw_line(gc, alloc.width-gap, 0,
                                      alloc.width-gap, alloc.height>>1)
        elif self.tree_direction == 3:
            gap = alloc.height / (height<<1)
            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and (frela or mrela)):
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width, alloc.height>>1)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and frela):
                if not frela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width>>1, gap)
                area.window.draw_line(gc, alloc.width>>1, gap, 0, gap)

            if self.show_unknown_peoples or \
               (not self.show_unknown_peoples and mrela):
                if not mrela:
                    gc.line_style = gtk.gdk.LINE_ON_OFF_DASH
                else:
                    gc.line_style = gtk.gdk.LINE_SOLID
                area.window.draw_line(gc, alloc.width>>1, alloc.height>>1,
                                      alloc.width>>1, alloc.height-gap)
                area.window.draw_line(gc, alloc.width>>1, alloc.height-gap,
                                      0, alloc.height-gap)

    def home(self, menuitem):
        """Change root person to default person for database."""
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.dbstate.change_active_person(defperson)

    def edit_person_cb(self, obj, person_handle):
        """
        Open edit person window for person_handle.
        Called after double click or from submenu.
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass
            return True
        return False

    def edit_family_cb(self, obj, family_handle):
        """
        Open edit person family for family_handle.
        Called after double click or from submenu.
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass
            return True
        return False

    def add_parents_cb(self, obj, person_handle, family_handle):
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
        except Errors.WindowActiveError:
            pass

    def copy_person_to_clipboard_cb(self, obj, person_handle):
        """
        Renders the person data into some lines of text and
        puts that into the clipboard
        """
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self.format_helper.format_person(person, 11))
            return True
        return False

    def copy_family_to_clipboard_cb(self, obj, family_handle):
        """
        Renders the family data into some lines of text and
        puts that into the clipboard
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self.format_helper.format_relation(family, 11))
            return True
        return False

    def on_show_option_menu_cb(self, obj, event, data=None):
        """Right click option menu."""
        menu = gtk.Menu()
        self.add_nav_portion_to_menu(menu)
        self.add_settings_to_menu(menu)
        menu.popup(None, None, None, 0, event.time)
        return True

    def bg_button_press_cb(self, widget, event):
        """
        Enter in scroll mode when mouse button pressed in background
        or call option menu.
        """
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))
            self._last_x = event.x
            self._last_y = event.y
            self._in_move = True
            return True
        elif event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            self.on_show_option_menu_cb(widget, event)
            return True
        return False

    def bg_button_release_cb(self, widget, event):
        """Exit from scroll mode when button release."""
        if event.button == 1 and event.type == gtk.gdk.BUTTON_RELEASE:
            self.bg_motion_notify_event_cb(widget, event)
            widget.window.set_cursor(None)
            self._in_move = False
            return True
        return False

    def bg_motion_notify_event_cb(self, widget, event):
        """Function for motion notify events for drag and scroll mode."""
        if self._in_move and (event.type == gtk.gdk.MOTION_NOTIFY or \
           event.type == gtk.gdk.BUTTON_RELEASE):
            window = widget.get_parent()
            hadjustment = window.get_hadjustment()
            vadjustment = window.get_vadjustment()
            self.update_scrollbar_positions(vadjustment,
                vadjustment.value - (event.y - self._last_y))
            self.update_scrollbar_positions(hadjustment,
                hadjustment.value - (event.x - self._last_x))
            return True
        return False

    def update_scrollbar_positions(self, adjustment, value):
        """Controle value then try setup in scrollbar."""
        if value > (adjustment.upper - adjustment.page_size):
            adjustment.set_value(adjustment.upper - adjustment.page_size)
        else:
            adjustment.set_value(value)
        return True

    def bg_scroll_event(self, widget, event):
        """
        Function change scroll direction to horizontally
        if variable self.scroll_direction setup.
        """
        if self.scroll_direction and event.type == gtk.gdk.SCROLL:
            if event.direction == gtk.gdk.SCROLL_UP:
                event.direction = gtk.gdk.SCROLL_LEFT
            elif event.direction == gtk.gdk.SCROLL_DOWN:
                event.direction = gtk.gdk.SCROLL_RIGHT
        return False

    def person_button_press_cb(self, obj, event, person_handle, family_handle):
        """
        Call edit person function for mouse left button double click on person
        or submenu for person for mouse right click.
        And setup plug for button press on person widget.
        """
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            self.build_full_nav_menu_cb(obj, event,
                                        person_handle, family_handle)
            return True
        elif event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.edit_person_cb(obj, person_handle)
            return True
        return True

    def relation_button_press_cb(self, obj, event, family_handle):
        """
        Call edit family function for mouse left button double click
        on family line or call full submenu for mouse right click.
        And setup plug for button press on family line.
        """
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            self.build_relation_nav_menu_cb(obj, event, family_handle)
            return True
        elif event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.edit_family_cb(obj, family_handle)
            return True
        return True

    def missing_parent_button_press_cb(self, obj, event,
                                       person_handle, family_handle):
        """
        Call function for not full family for mouse left button double click
        on missing persons or call submenu for mouse right click.
        """
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.add_parents_cb(obj, person_handle, family_handle)
            return True
        elif event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            self.build_missing_parent_nav_menu_cb(obj, event, person_handle,
                                                  family_handle)
            return True
        return False

    def on_show_child_menu(self, obj):
        """User clicked button to move to child of active person"""
        if self.dbstate.active:
            # Build and display the menu attached to the left pointing arrow
            # button. The menu consists of the children of the current root
            # person of the tree. Attach a child to each menu item.

            childlist = find_children(self.dbstate.db, self.dbstate.active)
            if len(childlist) == 1:
                child = self.dbstate.db.get_person_from_handle(childlist[0])
                if child:
                    self.dbstate.change_active_person(child)
            elif len(childlist) > 1:
                myMenu = gtk.Menu()
                for child_handle in childlist:
                    child = self.dbstate.db.get_person_from_handle(child_handle)
                    cname = escape(name_displayer.display(child))
                    if find_children(self.dbstate.db, child):
                        label = gtk.Label('<b><i>%s</i></b>' % cname)
                    else:
                        label = gtk.Label(cname)
                    label.set_use_markup(True)
                    label.show()
                    label.set_alignment(0, 0)
                    menuitem = gtk.ImageMenuItem(None)
                    go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                        gtk.ICON_SIZE_MENU)
                    go_image.show()
                    menuitem.set_image(go_image)
                    menuitem.add(label)
                    myMenu.append(menuitem)
                    menuitem.connect("activate", self.on_childmenu_changed,
                                     child_handle)
                    menuitem.show()
                myMenu.popup(None, None, None, 0, 0)
            return 1
        return 0

    def on_childmenu_changed(self, obj, person_handle):
        """
        Callback for the pulldown menu selection, changing to the person
        attached with menu item.
        """
        self.dbstate.change_active_handle(person_handle)
        return True

    def change_force_size_cb(self, menuitem, data):
        """Change force_size option."""
        if data in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            config.set('interface.pedview-tree-size', data)
            self.force_size = data
            self.dirty = True
            # switch to matching size
            self.rebuild_trees(self.dbstate.active.handle)

    def change_tree_style_cb(self, menuitem, data):
        """Change tree_style option."""
        if data in [0, 1, 2]:
            config.set('interface.pedviewext-layout', data)
            if self.tree_style != data:
                if self.tree_style == 2 and self.force_size > 5:
                    self.force_size = 5
                self.dirty = True
                self.tree_style = data
                if self.dbstate.active:
                    # Rebuild using new style
                    self.rebuild_trees(self.dbstate.active.handle)
                else:
                    self.rebuild_trees(None)

    def change_tree_direction_cb(self, menuitem, data):
        """Change tree_direction option."""
        if data in [0, 1, 2, 3]:
            config.set('interface.pedviewext-tree-direction', data)
            if self.tree_direction != data:
                self.dirty = True
                self.tree_direction = data
                if self.dbstate.active:
                    # Rebuild using new tree direction
                    self.rebuild_trees(self.dbstate.active.handle)
                else:
                    self.rebuild_trees(None)

    def change_show_images_cb(self, event):
        """Change show_images option."""
        self.show_images = not self.show_images
        config.set('interface.pedviewext-show-images', self.show_images)
        self.dirty = True
        if self.dbstate.active:
            # Rebuild using new style
            self.rebuild_trees(self.dbstate.active.handle)
        else:
            self.rebuild_trees(None)

    def change_show_marriage_cb(self, event):
        """Change show_marriage_data option."""
        self.show_marriage_data = not self.show_marriage_data
        config.set('interface.pedviewext-show-marriage', 
                    self.show_marriage_data)
        self.dirty = True
        if self.dbstate.active:
            # Rebuild using new style
            self.rebuild_trees(self.dbstate.active.handle)
        else:
            self.rebuild_trees(None)

    def change_show_unknown_peoples_cb(self, event):
        """Change show_unknown_peoples option."""
        self.show_unknown_peoples = not self.show_unknown_peoples
        config.set('interface.pedviewext-show-unknown-peoples', 
                    self.show_unknown_peoples)
        self.dirty = True
        if self.dbstate.active:
            # Rebuild using new style
            self.rebuild_trees(self.dbstate.active.handle)
        else:
            self.rebuild_trees(None)

    def change_scroll_direction_cb(self, menuitem, data):
        """Change scroll_direction option."""
        config.set('interface.pedviewext-scroll-direction', 
                    self.scroll_direction)
        if data:
            self.scroll_direction = True
        else:
            self.scroll_direction = False

    def kb_goto_home(self):
        """Goto home person from keyboard."""
        self.home(None)

    def kb_plus_generation(self):
        """Increment size of tree from keyboard."""
        self.change_force_size_cb(None, self.force_size + 1)

    def kb_minus_generation(self):
        """Decrement size of tree from keyboard."""
        self.change_force_size_cb(None, self.force_size - 1)

    def kb_change_style(self):
        """Change style of tree from keyboard."""
        next_style = self.tree_style + 1
        if next_style > 2:
            next_style = 0
        self.change_tree_style_cb(None, next_style)

    def kb_change_direction(self):
        """Change direction of tree from keyboard."""
        next_direction = self.tree_direction + 1
        if next_direction > 3:
            next_direction = 0
        self.change_tree_direction_cb(None, next_direction)

    def find_tree(self, person, index, depth, lst, val=0):
        """Recursively build a list of ancestors"""

        if depth > self.force_size or not person:
            return

        if self._depth < depth:
            self._depth = depth

        try:
            alive = Utils.probably_alive(person, self.dbstate.db)
        except RuntimeError:
            ErrorDialog(_('Relationship loop detected'),
                        _('A person was found to be his/her own ancestor.'))
            alive = False

        lst[index] = (person, val, None, alive)

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

                    lst[index] = (person, val, family, alive)
                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self.dbstate.\
                            db.get_person_from_handle(father_handle)
                        self.find_tree(father, (2*index)+1, depth+1, lst, frel)
                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self.dbstate.\
                            db.get_person_from_handle(mother_handle)
                        self.find_tree(mother, (2*index)+2, depth+1, lst, mrel)

    def add_nav_portion_to_menu(self, menu):
        """
        This function adds a common history-navigation portion
        to the context menu. Used by both build_nav_menu() and
        build_full_nav_menu() methods.
        """
        hobj = self.uistate.phistory
        home_sensitivity = True
        if not self.dbstate.db.get_default_person():
            home_sensitivity = False
        entries = [
            (gtk.STOCK_GO_BACK, self.back_clicked, not hobj.at_front()),
            (gtk.STOCK_GO_FORWARD, self.fwd_clicked, not hobj.at_end()),
            (gtk.STOCK_HOME, self.home, home_sensitivity),
            (None, None, 0)
        ]

        for stock_id, callback, sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            item.set_sensitive(sensitivity)
            if callback:
                item.connect("activate", callback)
            item.show()
            menu.append(item)

    def add_settings_to_menu(self, menu):
        """
        Add settings to menu (Show images, Show marriage data,
        Show unknown peoples, Mouse scroll direction, Tree style,
        Tree size, Tree direction), marked selected items.
        Othet menu for othet styles.
        """
        entry = gtk.ImageMenuItem(_("Show images"))
        if self.show_images:
            current_show_images_image = \
                gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
            current_show_images_image.show()
            entry.set_image(current_show_images_image)
        entry.connect("activate", self.change_show_images_cb)
        entry.show()
        menu.append(entry)

        entry = gtk.ImageMenuItem(_("Show marriage data"))
        if self.show_marriage_data:
            current_show_marriage_image = \
                gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
            current_show_marriage_image.show()
            entry.set_image(current_show_marriage_image)
        entry.connect("activate", self.change_show_marriage_cb)
        entry.show()
        menu.append(entry)

        if self.tree_style == 2:
            entry = gtk.ImageMenuItem(_("Show unknown peoples"))
            if self.show_unknown_peoples:
                current_show_unknown_peoples_image = \
                    gtk.image_new_from_stock(gtk.STOCK_APPLY,
                                             gtk.ICON_SIZE_MENU)
                current_show_unknown_peoples_image.show()
                entry.set_image(current_show_unknown_peoples_image)
            entry.connect("activate", self.change_show_unknown_peoples_cb)
            entry.show()
            menu.append(entry)

        item = gtk.MenuItem(_("Mouse scroll direction"))
        item.set_submenu(gtk.Menu())
        scroll_direction_menu = item.get_submenu()

        scroll_direction_image = gtk.image_new_from_stock(gtk.STOCK_APPLY,
                                                       gtk.ICON_SIZE_MENU)
        scroll_direction_image.show()

        entry = gtk.ImageMenuItem(_("Top <-> Bottom"))
        entry.connect("activate", self.change_scroll_direction_cb, False)
        if self.scroll_direction == False:
            entry.set_image(scroll_direction_image)
        entry.show()
        scroll_direction_menu.append(entry)

        entry = gtk.ImageMenuItem(_("Left <-> Right"))
        entry.connect("activate", self.change_scroll_direction_cb, True)
        if self.scroll_direction == True:
            entry.set_image(scroll_direction_image)
        entry.show()
        scroll_direction_menu.append(entry)

        scroll_direction_menu.show()
        item.show()
        menu.append(item)

        item = gtk.MenuItem(_("Tree style"))
        item.set_submenu(gtk.Menu())
        style_menu = item.get_submenu()

        current_style_image = gtk.image_new_from_stock(gtk.STOCK_APPLY,
                                                       gtk.ICON_SIZE_MENU)
        current_style_image.show()

        entry = gtk.ImageMenuItem(_("Version A"))
        entry.connect("activate", self.change_tree_style_cb, 0)
        if self.tree_style == 0:
            entry.set_image(current_style_image)
        entry.show()
        style_menu.append(entry)

        entry = gtk.ImageMenuItem(_("Version B"))
        entry.connect("activate", self.change_tree_style_cb, 1)
        if self.tree_style == 1:
            entry.set_image(current_style_image)
        entry.show()
        style_menu.append(entry)

        entry = gtk.ImageMenuItem(_("Version C"))
        entry.connect("activate", self.change_tree_style_cb, 2)
        if self.tree_style == 2:
            entry.set_image(current_style_image)
        entry.show()
        style_menu.append(entry)

        style_menu.show()
        item.show()
        menu.append(item)

        item = gtk.MenuItem(_("Tree size"))
        item.set_submenu(gtk.Menu())
        size_menu = item.get_submenu()

        current_size_image = gtk.image_new_from_stock(gtk.STOCK_APPLY,
                                                      gtk.ICON_SIZE_MENU)
        current_size_image.show()

        for num in range(2, 6):
            entry = gtk.ImageMenuItem(
                ngettext("%d generation", "%d generations", num) %num)
            if self.force_size == num:
                entry.set_image(current_size_image)
            entry.connect("activate", self.change_force_size_cb, num)
            entry.show()
            size_menu.append(entry)

        if self.tree_style == 2:

            for num in range(6, 11):
                entry = gtk.ImageMenuItem(
                    ngettext("%d generation", "%d generations", num) %num)
                if self.force_size == num:
                    entry.set_image(current_size_image)
                entry.connect("activate", self.change_force_size_cb, num)
                entry.show()
                size_menu.append(entry)

            item2 = gtk.MenuItem(_("Tree direction"))
            item2.set_submenu(gtk.Menu())
            direction_menu = item2.get_submenu()

            current_direction_image = gtk.image_new_from_stock(gtk.STOCK_APPLY,
                gtk.ICON_SIZE_MENU)
            current_direction_image.show()

            entry = gtk.ImageMenuItem(_("Vertical (top to bottom)"))
            entry.connect("activate", self.change_tree_direction_cb, 0)
            if self.tree_direction == 0:
                entry.set_image(current_direction_image)
            entry.show()
            direction_menu.append(entry)

            entry = gtk.ImageMenuItem(_("Vertical (bottom to top)"))
            entry.connect("activate", self.change_tree_direction_cb, 1)
            if self.tree_direction == 1:
                entry.set_image(current_direction_image)
            entry.show()
            direction_menu.append(entry)

            entry = gtk.ImageMenuItem(_("Horizontal (left to right)"))
            entry.connect("activate", self.change_tree_direction_cb, 2)
            if self.tree_direction == 2:
                entry.set_image(current_direction_image)
            entry.show()
            direction_menu.append(entry)

            entry = gtk.ImageMenuItem(_("Horizontal (right to left)"))
            entry.connect("activate", self.change_tree_direction_cb, 3)
            if self.tree_direction == 3:
                entry.set_image(current_direction_image)
            entry.show()
            direction_menu.append(entry)

            direction_menu.show()
            item2.show()
            menu.append(item2)

        size_menu.show()
        item.show()
        menu.append(item)

    def build_missing_parent_nav_menu_cb(self, obj, event,
                                         person_handle, family_handle):
        """Builds the menu for a missing parent."""
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))

        add_item = gtk.ImageMenuItem(gtk.STOCK_ADD)
        add_item.connect("activate", self.add_parents_cb, person_handle,
                         family_handle)
        add_item.show()
        menu.append(add_item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(menu)
        self.add_settings_to_menu(menu)
        menu.popup(None, None, None, 0, event.time)
        return 1

    def build_full_nav_menu_cb(self, obj, event, person_handle, family_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children,
        and Parents) with navigation.
        """

        menu = gtk.Menu()
        menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                            gtk.ICON_SIZE_MENU)
        go_image.show()
        go_item = gtk.ImageMenuItem(name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate", self.on_childmenu_changed, person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        edit_item.connect("activate", self.edit_person_cb, person_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        clipboard_item.connect("activate", self.copy_person_to_clipboard_cb,
                               person_handle)
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

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                gtk.ICON_SIZE_MENU)
            go_image.show()
            sp_item = gtk.ImageMenuItem(name_displayer.display(spouse))
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
        item = gtk.MenuItem(_("Siblings"))
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
                    item.set_submenu(gtk.Menu())
                    sib_menu = item.get_submenu()

                if find_children(self.dbstate.db, sib):
                    label = gtk.Label('<b><i>%s</i></b>' % \
                        escape(name_displayer.display(sib)))
                else:
                    label = gtk.Label(escape(name_displayer.display(sib)))

                go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                    gtk.ICON_SIZE_MENU)
                go_image.show()
                sib_item = gtk.ImageMenuItem(None)
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0, 0)
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
        item = gtk.MenuItem(_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db, person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue

            if no_children:
                no_children = 0
                item.set_submenu(gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.dbstate.db, child):
                label = gtk.Label('<b><i>%s</i></b>' % \
                    escape(name_displayer.display(child)))
            else:
                label = gtk.Label(escape(name_displayer.display(child)))

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                gtk.ICON_SIZE_MENU)
            go_image.show()
            child_item = gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
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
        item = gtk.MenuItem(_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db, person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db, par):
                label = gtk.Label('<b><i>%s</i></b>' % \
                    escape(name_displayer.display(par)))
            else:
                label = gtk.Label(escape(name_displayer.display(par)))

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                gtk.ICON_SIZE_MENU)
            go_image.show()
            par_item = gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate", self.on_childmenu_changed, par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            if self.tree_style == 2 and not self.show_unknown_peoples:
                item.set_submenu(gtk.Menu())
                par_menu = item.get_submenu()
                par_item = gtk.ImageMenuItem(_("Add New Parents..."))
                par_item.connect("activate", self.add_parents_cb, person_handle,
                         family_handle)
                par_item.show()
                par_menu.append(par_item)
            else:
                item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = gtk.MenuItem(_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db, person):
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

            go_image = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                                gtk.ICON_SIZE_MENU)
            go_image.show()
            per_item = gtk.ImageMenuItem(None)
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

        # Add separator
        item = gtk.MenuItem(None)
        item.show()
        menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(menu)
        self.add_settings_to_menu(menu)
        menu.popup(None, None, None, 0, event.time)
        return 1

    def build_relation_nav_menu_cb(self, obj, event, family_handle):
        """Builds the menu for a parents-child relation line."""
        menu = gtk.Menu()
        menu.set_title(_('Family Menu'))

        family = self.dbstate.db.get_family_from_handle(family_handle)
        if not family:
            return 0

        edit_item = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        edit_item.connect("activate", self.edit_family_cb, family_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        clipboard_item.connect("activate", self.copy_family_to_clipboard_cb,
                               family_handle)
        clipboard_item.show()
        menu.append(clipboard_item)

        # Add separator
        item = gtk.MenuItem(None)
        item.show()
        menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(menu)
        self.add_settings_to_menu(menu)
        menu.popup(None, None, None, 0, event.time)
        return 1


#-------------------------------------------------------------------------
#
# Function to return children's list of a person
#
#-------------------------------------------------------------------------
def find_children(db, person):
    """Return the list of all children's IDs for a person."""
    childlist = []
    for family_handle in person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for child_ref in family.get_child_ref_list():
            childlist.append(child_ref.ref)
    return childlist

#-------------------------------------------------------------------------
#
# Function to return parent's list of a person
#
#-------------------------------------------------------------------------
def find_parents(db, person):
    """Return the unique list of all parent's IDs for a person."""
    parentlist = []
    for family_handle in person.get_parent_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if father_handle not in parentlist:
            parentlist.append(father_handle)
        if mother_handle not in parentlist:
            parentlist.append(mother_handle)
    return parentlist

#-------------------------------------------------------------------------
#
# Function to return persons, that share the same event.
# This for example links witnesses to the tree
#
#-------------------------------------------------------------------------
def find_witnessed_people(db, person):
    """Return the list of all IDs associated with a person."""
    people = []
    for event_ref in person.get_event_ref_list():
        for link in db.find_backlink_handles(event_ref.ref):
            if link[0] == 'Person' and \
               link[1] != person.get_handle() and link[1] not in people:
                people.append(link[1])
            if link[0] == 'Family':
                fam = db.get_family_from_handle(link[1])
                if fam:
                    father_handle = fam.get_father_handle()
                    if father_handle and \
                       father_handle != person.get_handle() and \
                       father_handle not in people:
                        people.append(father_handle)
                    mother_handle = fam.get_mother_handle()
                    if mother_handle and \
                       mother_handle != person.get_handle() and \
                       mother_handle not in people:
                        people.append(mother_handle)
    for family_handle in person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for event_ref in family.get_event_ref_list():
            for link in db.find_backlink_handles(event_ref.ref):
                if link[0] == 'Person' and \
                   link[1] != person.get_handle() and link[1] not in people:
                    people.append(link[1])
    for pref in person.get_person_ref_list():
        if pref.ref != person.get_handle and pref.ref not in people:
            people.append(pref.ref)
    return people

#-------------------------------------------------------------------------
#
# Functions to build the text displayed in the details view of a DispBox
# additionally used by PedigreeView to get the largest area covered by a DispBox
#
#-------------------------------------------------------------------------
def build_detail_string(db, person):
    """For person formating in text birth_ref and death_ref.
    Now not used, use class FormattingHelper"""

    detail_text = name_displayer.display(person)

    def format_event(db, label, event):
        """Formating event to text view"""
        if not event:
            return u""
        event_date = DateHandler.get_date(event)
        event_place = None
        place_handle = event.get_place_handle()
        if place_handle:
            place_title = db.get_place_from_handle(place_handle).get_title()
            if place_title != "":
                if len(place_title) > 15:
                    event_place = place_title[:14]+"..."
                else:
                    event_place = place_title
        if event_place:
            return u"\n%s %s, %s" % (label, event_date, event_place)
        return u"\n%s %s" % (label, event_date)

    birth_ref = person.get_birth_ref()
    if birth_ref:
        detail_text += format_event(db, _BORN,
                                    db.get_event_from_handle(birth_ref.ref))
    else:
        for event_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if event and event.get_type() == gen.lib.EventType.BAPTISM:
                detail_text += format_event(db, _BAPT, event)
                break
            if event and event.get_type() == gen.lib.EventType.CHRISTEN:
                detail_text += format_event(db, _CHRI, event)
                break

    death_ref = person.get_death_ref()
    if death_ref:
        detail_text += format_event(db, _DIED,
                                    db.get_event_from_handle(death_ref.ref))
    else:
        for event_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if event and event.get_type() == gen.lib.EventType.BURIAL:
                detail_text += format_event(db, _BURI, event)
                break
            if event and event.get_type() == gen.lib.EventType.CREMATION:
                detail_text += format_event(db, _CREM, event)
                break

    return detail_text
