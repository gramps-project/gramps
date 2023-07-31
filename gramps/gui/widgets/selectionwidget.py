#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Artem Glebov <artem.glebov@gmail.com>
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

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib, GObject

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.display.name import displayer as name_displayer

# -------------------------------------------------------------------------
#
# grabbers constants and routines
#
# -------------------------------------------------------------------------
from .grabbers import (
    grabber_generators,
    can_grab,
    grabber_position,
    switch_grabber,
    CURSORS,
    GRABBER_INSIDE,
    INSIDE,
    INNER_GRABBERS,
    OUTER_GRABBERS,
    MOTION_FUNCTIONS,
)

# -------------------------------------------------------------------------
#
# PhotoTaggingGramplet
#
# -------------------------------------------------------------------------

RESIZE_RATIO = 1.5
MAX_ZOOM = 10
MIN_ZOOM = 0.05
MAX_SIZE = 2000
MIN_SIZE = 50
SHADING_OPACITY = 0.7
MIN_SELECTION_SIZE = 10


def scale_to_fit(orig_x, orig_y, target_x, target_y):
    """
    Calculates the scale factor to fit the rectangle
    orig_x * orig_y by scaling keeping the aspect ratio.
    """
    orig_aspect = orig_x / orig_y
    target_aspect = target_x / target_y
    if orig_aspect > target_aspect:
        return target_x / orig_x
    else:
        return target_y / orig_y


def resize_keep_aspect(orig_x, orig_y, target_x, target_y):
    """
    Calculates the dimensions of the rectangle obtained from
    the rectangle orig_x * orig_y by scaling to fit
    target_x * target_y keeping the aspect ratio.
    """
    orig_aspect = orig_x / orig_y
    target_aspect = target_x / target_y
    if orig_aspect > target_aspect:
        return (target_x, target_x * orig_y // orig_x)
    else:
        return (target_y * orig_x // orig_y, target_y)


def order_coordinates(point1, point2):
    """
    Returns the rectangle (x1, y1, x2, y2) based on point1 and point2,
    such that x1 <= x2 and y1 <= y2.
    """
    x1 = min(point1[0], point2[0])
    x2 = max(point1[0], point2[0])
    y1 = min(point1[1], point2[1])
    y2 = max(point1[1], point2[1])
    return (x1, y1, x2, y2)


def minimum_region(point1, point2):
    """
    Returns whether the rectangle defined by the corner points point1
    and point2 exceeds the minimum dimensions.
    """
    return (
        abs(point1[0] - point2[0]) >= MIN_SELECTION_SIZE
        and abs(point1[1] - point2[1]) >= MIN_SELECTION_SIZE
    )


class Region:
    """
    Representation of a region of image that can be associated with
    a person.
    """

    def __init__(self, x1, y1, x2, y2):
        """
        Creates a new region with the specified coordinates.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.person = None
        self.mediaref = None

    def coords(self):
        """
        Returns the coordinates of the region as a 4-tuple in the
        format (x1, y1, x2, y2).
        """
        return (self.x1, self.y1, self.x2, self.y2)

    def set_coords(self, x1, y1, x2, y2):
        """
        Sets the coordinates of this region.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def contains(self, x, y):
        """
        Returns whether the point with coordinates (x, y) lies insided
        this region.
        """
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def contains_rect(self, other):
        """
        Returns whether this region fully contains the region other.
        """
        return self.contains(other.x1, other.y1) and self.contains(other.x2, other.y2)

    def area(self):
        """
        Returns the area of this region.
        """
        return abs(self.x1 - self.x2) * abs(self.y1 - self.y2)

    def intersects(self, other):
        """
        Returns whether the current region intersects other.
        """
        # assumes that x1 <= x2 and y1 <= y2
        return not (
            self.x2 < other.x1
            or self.x1 > other.x2
            or self.y2 < other.y1
            or self.y1 > other.y2
        )


class SelectionWidget(Gtk.ScrolledWindow):
    """
    A widget that displays an image and permits GIMP-like selection of regions
    within the image. The widget derives from gtk.ScrolledWindow.
    """

    __gsignals__ = {
        "region-modified": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "region-created": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "region-selected": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "selection-cleared": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "right-button-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "zoomed-in": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "zoomed-out": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        """
        Creates a new selection widget.
        """
        self.multiple_selection = True

        self.loaded = False
        self.start_point_screen = None
        self.selection = None
        self.current = None
        self.in_region = None
        self.grabber = None
        self.regions = []
        self.translation = None
        self.pixbuf = None
        self.scaled_pixbuf = None
        self.scale = 1.0
        self.old_viewport_size = None

        Gtk.ScrolledWindow.__init__(self)
        self.add(self._build_gui())
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

    def _build_gui(self):
        """
        Builds and lays out the GUI of the widget.
        """
        self.image = Gtk.Image()
        self.image.set_has_tooltip(True)
        self.image.connect_after("draw", self._expose_handler)
        self.image.connect("query-tooltip", self._show_tooltip)

        self.event_box = Gtk.EventBox()
        self.event_box.connect("button-press-event", self._button_press_event)
        self.event_box.connect("button-release-event", self._button_release_event)
        self.connect("motion-notify-event", self._motion_notify_event)
        self.connect("scroll-event", self._motion_scroll_event)
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.event_box.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.event_box.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        self.event_box.add(self.image)

        self.viewport = Gtk.Viewport()
        self.connect("size-allocate", self._resize)
        self.viewport.add(self.event_box)
        return self.viewport

    # ======================================================
    # public field accessors
    # ======================================================

    def get_multiple_selection(self):
        """
        Return whether multiple selection is enabled.
        """
        return self.multiple_selection

    def set_multiple_selection(self, enable):
        """
        Enables or disables multiple selection.
        """
        self.multiple_selection = enable

    def is_image_loaded(self):
        """
        Returns whether an image has been loaded into this selection widget.
        """
        return self.loaded

    def set_regions(self, regions):
        """
        Sets the list of regions to be displayed in the widget.
        """
        self.regions = regions

    def get_current(self):
        """
        Returns the currently active region.
        """
        return self.current

    def set_current(self, region):
        """
        Activates the given region in the widget.
        """
        self.current = region

    def get_selection(self):
        """
        Returns the coordinates of the current selection.
        """
        return self.selection

    # ======================================================
    # loading the image
    # ======================================================

    def load_image(self, image_path):
        """
        Loads an image from a given path into this selection widget.
        """
        self.start_point_screen = None
        self.selection = None
        self.in_region = None
        self.grabber_position = None
        self.grabber_to_draw = None

        try:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            self.original_image_size = (
                self.pixbuf.get_width(),
                self.pixbuf.get_height(),
            )

            viewport_size = self.get_allocation()
            self.old_viewport_size = viewport_size
            self.scale = scale_to_fit(
                self.pixbuf.get_width(),
                self.pixbuf.get_height(),
                viewport_size.width,
                viewport_size.height,
            )
            self._rescale()
            self.loaded = True
        except (GLib.GError, OSError):
            self.show_missing()

    def show_missing(self):
        """
        Displays a 'missing image' icon in the widget.
        """
        self.pixbuf = None
        self.image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        self.image.queue_draw()

    def _resize(self, *dummy):
        """
        Handles size-allocate' events from Gtk.
        """
        if self.pixbuf:
            viewport_size = self.get_allocation()
            if (
                viewport_size.height != self.old_viewport_size.height
                or viewport_size.width != self.old_viewport_size.width
                or not self.image.get_pixbuf()
            ):
                self.scale = scale_to_fit(
                    self.pixbuf.get_width(),
                    self.pixbuf.get_height(),
                    viewport_size.width,
                    viewport_size.height,
                )
                self._rescale()
                self.old_viewport_size = viewport_size
                return False

    def expander(self, *dummy):
        """Handler for expander in caller; needed because Gtk doesn't handle
        verticle expansion right
        """
        self.image.clear()
        self.image.set_size_request(2, 2)
        self.event_box.set_size_request(2, 2)
        return False

    # ======================================================
    # coordinate transformations (public methods)
    # ======================================================

    def proportional_to_real_rect(self, rect):
        """
        Translates proportional (ranging from 0 to 100) coordinates to image
        coordinates (in pixels).
        """
        x1, y1, x2, y2 = rect
        return self._proportional_to_real((x1, y1)) + self._proportional_to_real(
            (x2, y2)
        )

    def real_to_proportional_rect(self, rect):
        """
        Translates image coordinates (in pixels) to proportional (ranging
        from 0 to 100).
        """
        x1, y1, x2, y2 = rect
        return self._real_to_proportional((x1, y1)) + self._real_to_proportional(
            (x2, y2)
        )

    # ======================================================
    # widget manipulation
    # ======================================================

    def refresh(self):
        """
        Schedules a redraw of the image.
        """
        self.image.queue_draw()

    def can_zoom_in(self):
        """
        Returns whether it is possible to zoom in the image.
        """
        if self.original_image_size:
            scaled_size = (
                self.original_image_size[0] * self.scale * RESIZE_RATIO,
                self.original_image_size[1] * self.scale * RESIZE_RATIO,
            )
            return scaled_size[0] < MAX_SIZE and scaled_size[1] < MAX_SIZE
        return False

    def can_zoom_out(self):
        """
        Returns whether it is possible to zoom out the image.
        """
        if self.original_image_size:
            scaled_size = (
                self.original_image_size[0] * self.scale * RESIZE_RATIO,
                self.original_image_size[1] * self.scale * RESIZE_RATIO,
            )
            return scaled_size[0] >= MIN_SIZE and scaled_size[1] >= MIN_SIZE
        return False

    def zoom_in(self):
        """
        Zooms in the image. The zoom factor is defined by RESIZE_RATIO.
        """
        if self.can_zoom_in():
            self.scale *= RESIZE_RATIO
            self._rescale()
            self.emit("zoomed-in")

    def zoom_out(self):
        """
        Zooms out the image. The zoom factor is defined by RESIZE_RATIO.
        """
        if self.can_zoom_out():
            self.scale /= RESIZE_RATIO
            self._rescale()
            self.emit("zoomed-out")

    def select(self, region):
        """
        Highlights the given region in the image.
        """
        self.current = region
        if self.current is not None:
            self.selection = self.current.coords()
        self.image.queue_draw()

    def clear_selection(self):
        """
        Clears the selection.
        """
        self.current = None
        self.selection = None
        self.image.queue_draw()

    def find_region(self, x, y):
        """
        Given screen coordinates, find where that point is in the image.
        """
        return self._find_region(*self._screen_to_image((x, y)))

    # ======================================================
    # thumbnails
    # ======================================================

    def get_thumbnail(self, region, thumbnail_size):
        """
        Returns the thumbnail of the given region.
        """
        w = region.x2 - region.x1
        h = region.y2 - region.y1
        if w >= 1 and h >= 1 and self.pixbuf:
            subpixbuf = self.pixbuf.new_subpixbuf(region.x1, region.y1, w, h)
            size = resize_keep_aspect(w, h, *thumbnail_size)
            return subpixbuf.scale_simple(
                size[0], size[1], GdkPixbuf.InterpType.BILINEAR
            )
        else:
            return None

    # ======================================================
    # utility functions for retrieving properties
    # ======================================================

    def _get_original_image_size(self):
        """
        Returns the size of the image before scaling.
        """
        return self.original_image_size

    def _get_scaled_image_size(self):
        """
        Returns the size of images scaled with the current scaled.
        """
        unscaled_size = self._get_original_image_size()
        return (unscaled_size[0] * self.scale, unscaled_size[1] * self.scale)

    # ======================================================
    # coordinate transformations
    # ======================================================

    def _proportional_to_real(self, coord):
        """
        Translates proportional (ranging from 0 to 100) coordinates to image
        coordinates (in pixels).
        """
        w, h = self.original_image_size
        return (int(round(coord[0] * w / 100)), int(round(coord[1] * h / 100)))

    def _real_to_proportional(self, coord):
        """
        Translates image coordinates (in pixels) to proportional (ranging
        from 0 to 100).
        """
        w, h = self.original_image_size
        return (int(round(coord[0] * 100 / w)), int(round(coord[1] * 100 / h)))

    def _image_to_screen(self, coords):
        """
        Translates image coordinates to viewport coordinates using the current
        scale and viewport size.
        """
        viewport_rect = self.get_allocation()
        image_rect = self.scaled_size
        if image_rect[0] < viewport_rect.width:
            offset_x = (image_rect[0] - viewport_rect.width) / 2
        else:
            offset_x = 0.0
        if image_rect[1] < viewport_rect.height:
            offset_y = (image_rect[1] - viewport_rect.height) / 2
        else:
            offset_y = 0.0
        return (
            int(coords[0] * self.scale - offset_x),
            int(coords[1] * self.scale - offset_y),
        )

    def _screen_to_image(self, coords):
        """
        Translates viewport coordinates to original (unscaled) image coordinates
        using the current scale and viewport size.
        """
        viewport_rect = self.get_allocation()
        image_rect = self.scaled_size
        if image_rect[0] < viewport_rect.width:
            offset_x = (image_rect[0] - viewport_rect.width) / 2
        else:
            offset_x = 0.0
        if image_rect[1] < viewport_rect.height:
            offset_y = (image_rect[1] - viewport_rect.height) / 2
        else:
            offset_y = 0.0
        return (
            int((coords[0] + offset_x) / self.scale),
            int((coords[1] + offset_y) / self.scale),
        )

    def _truncate_to_image_size(self, coords):
        """
        Modifies the coordinates of the given point to ensure that it lies
        within the image. Negative values are replaced with 0, positive values
        exceeding the image dimensions - with those corresponding dimensions.
        """
        x, y = coords
        (image_width, image_height) = self._get_original_image_size()
        x = max(x, 0)
        x = min(x, image_width)
        y = max(y, 0)
        y = min(y, image_height)
        return self._proportional_to_real(self._real_to_proportional((x, y)))

    def _screen_to_truncated(self, coords):
        """
        Transforms the screen coordinates to image coordinates and truncate to
        the image size.
        """
        return self._truncate_to_image_size(self._screen_to_image(coords))

    def _rect_image_to_screen(self, rect):
        """
        Translates the coordinates of the rectangle from image to screen.
        """
        x1, y1, x2, y2 = rect
        x1, y1 = self._image_to_screen((x1, y1))
        x2, y2 = self._image_to_screen((x2, y2))
        return (x1, y1, x2, y2)

    # ======================================================
    # drawing and scaling the image
    # ======================================================

    def _expose_handler(self, widget, cr):
        """
        Handles the expose-event signal of the underlying widget.
        """
        if self.pixbuf:
            self._draw_selection(widget, cr)

    def _draw_selection(self, widget, cr):
        """
        Draws the image, the selection boxes and does the necessary
        shading.
        """
        if not self.scaled_size:
            return

        w, h = self.scaled_size
        offset_x, offset_y = self._image_to_screen((0, 0))
        offset_x -= 1
        offset_y -= 1

        if self.selection:
            x1, y1, x2, y2 = self._rect_image_to_screen(self.selection)

            # transparent shading
            self._draw_transparent_shading(cr, x1, y1, x2, y2, w, h, offset_x, offset_y)

            # selection frame
            self._draw_selection_frame(cr, x1, y1, x2, y2)

            # draw grabber
            self._draw_grabber(cr)
        else:
            # selection frame
            for region in self.regions:
                x1, y1, x2, y2 = self._rect_image_to_screen(region.coords())
                self._draw_region_frame(cr, x1, y1, x2, y2)

    def _draw_transparent_shading(self, cr, x1, y1, x2, y2, w, h, offset_x, offset_y):
        """
        Draws the shading for a selection box.
        """
        cr.set_source_rgba(1.0, 1.0, 1.0, SHADING_OPACITY)
        cr.rectangle(offset_x, offset_y, x1 - offset_x, y1 - offset_y)
        cr.rectangle(offset_x, y1, x1 - offset_x, y2 - y1)
        cr.rectangle(offset_x, y2, x1 - offset_x, h - y2 + offset_y + 1)
        cr.rectangle(x1, y2 + 1, x2 - x1 + 1, h - y2 + offset_y)
        cr.rectangle(x2 + 1, y2 + 1, w - x2 + offset_x, h - y2 + offset_y)
        cr.rectangle(x2 + 1, y1, w - x2 + offset_x, y2 - y1 + 1)
        cr.rectangle(x2 + 1, offset_y, w - x2 + offset_x, y2 - offset_y)
        cr.rectangle(x1, offset_y, x2 - x1 + 1, y1 - offset_y)
        cr.fill()

    def _draw_selection_frame(self, cr, x1, y1, x2, y2):
        """
        Draws the frame during selection.
        """
        self._draw_region_frame(cr, x1, y1, x2, y2)

    def _draw_region_frame(self, cr, x1, y1, x2, y2):
        """
        Draws a region frame.
        """
        cr.set_source_rgb(1.0, 1.0, 1.0)  # white
        cr.rectangle(x1, y1, x2 - x1, y2 - y1)
        cr.stroke()
        cr.set_source_rgb(0.0, 0.0, 1.0)  # blue
        cr.rectangle(x1 - 2, y1 - 2, x2 - x1 + 4, y2 - y1 + 4)
        cr.stroke()

    def _draw_grabber(self, cr):
        """
        Draws a grabber.
        """
        if self.selection is not None and self.grabber is not None:
            selection_rect = self._rect_image_to_screen(self.selection)
            cr.set_source_rgb(1.0, 0, 0)
            if self.grabber_position is None:
                generators = grabber_generators(selection_rect)
            elif self.grabber_position == GRABBER_INSIDE:
                generators = INNER_GRABBERS
            else:
                generators = OUTER_GRABBERS
            if self.grabber_to_draw is not None:
                generator = generators[self.grabber_to_draw]
            else:
                generator = generators[self.grabber]
            if generator is not None:
                x1, y1, x2, y2 = generator(*selection_rect)
                cr.rectangle(x1, y1, x2 - x1, y2 - y1)
            cr.stroke()

    def _rescale(self):
        """
        Recalculates the sizes using the current scale and updates
        the buffers.
        """
        self.scaled_size = (
            int(self.original_image_size[0] * self.scale),
            int(self.original_image_size[1] * self.scale),
        )
        self.scaled_image = self.pixbuf.scale_simple(
            self.scaled_size[0], self.scaled_size[1], GdkPixbuf.InterpType.BILINEAR
        )
        self.image.set_from_pixbuf(self.scaled_image)
        self.image.set_size_request(*self.scaled_size)
        self.event_box.set_size_request(*self.scaled_size)

    # ======================================================
    # managing regions
    # ======================================================

    def _find_region(self, x, y):
        """
        Finds the smallest region containing point (x, y).
        """
        result = None
        for region in self.regions:
            if region.contains(x, y):
                if result is None or result.area() > region.area():
                    result = region
        return result

    # ======================================================
    # mouse event handlers
    # ======================================================

    def _button_press_event(self, obj, event):
        """
        Handles the button-press-event signal.
        """
        if not self.is_image_loaded():
            return
        if event.button == 1:  # left button
            self.start_point_screen = (event.x, event.y)
            if (
                self.current is not None
                and self.grabber is None
                and self.multiple_selection
            ):
                self.current = None
                self.selection = None
                self.refresh()
                self.emit("selection-cleared")
        elif event.button == 3:  # right button
            # select a region, if clicked inside one
            click_point = self._screen_to_image((event.x, event.y))
            self.current = self._find_region(*click_point)
            self.selection = self.current.coords() if self.current is not None else None
            self.start_point_screen = None
            self.refresh()
            if self.current is not None:
                self.emit("region-selected")
                self.emit("right-button-clicked")
            else:
                self.emit("selection-cleared")
        return True  # don't propagate the event further

    def _button_release_event(self, obj, event):
        """
        Handles the button-release-event signal.
        """
        if not self.is_image_loaded():
            return
        if event.button == 1:
            if self.start_point_screen:
                if self.current is not None:
                    # a box is currently selected
                    if self.grabber and self.grabber != INSIDE:
                        # clicked on one of the grabbers
                        dx, dy = (
                            event.x - self.start_point_screen[0],
                            event.y - self.start_point_screen[1],
                        )
                        self.grabber_to_draw = self._modify_selection(dx, dy)
                        self.current.set_coords(*self.selection)
                        self.emit("region-modified")
                    elif self.grabber is None and self.multiple_selection:
                        # clicked outside of the grabbing area
                        self.current = None
                        self.selection = None
                        self.emit("selection-cleared")
                    else:
                        # update current selection
                        self.current.set_coords(*self.selection)
                        self.region = self.current
                        self.emit("region-modified")
                else:
                    # nothing is currently selected
                    if (
                        minimum_region(self.start_point_screen, (event.x, event.y))
                        and self._can_select()
                    ):
                        # region selection
                        region = Region(*self.selection)
                        self.regions.append(region)
                        self.current = region
                        self.emit("region-created")
                    else:
                        # nothing selected, just a click
                        click_point = self._screen_to_image(self.start_point_screen)
                        self.current = self._find_region(*click_point)
                        self.selection = (
                            self.current.coords() if self.current is not None else None
                        )
                        self.emit("region-selected")

                self.start_point_screen = None
                self.refresh()

    def _motion_notify_event(self, widget, event):
        """
        Handles the motion-notify-event signal.
        """
        if not self.is_image_loaded():
            return
        end_point_orig = self._screen_to_image((event.x, event.y))
        end_point = self._truncate_to_image_size(end_point_orig)
        if self.start_point_screen:
            # selection or dragging (mouse button pressed)
            if self.grabber is not None and self.grabber != INSIDE:
                # dragging the grabber
                dx, dy = (
                    event.x - self.start_point_screen[0],
                    event.y - self.start_point_screen[1],
                )
                self.grabber_to_draw = self._modify_selection(dx, dy)
            else:
                # making new selection
                start_point = self._screen_to_truncated(self.start_point_screen)
                self.selection = order_coordinates(start_point, end_point)

        else:
            # motion (mouse button is not pressed)
            self.in_region = self._find_region(*end_point_orig)
            if self.current is not None:
                # a box is active, so check if the pointer is inside a grabber
                rect = self._rect_image_to_screen(self.current.coords())
                self.grabber = can_grab(rect, event.x, event.y)
                if self.grabber is not None:
                    self.grabber_to_draw = self.grabber
                    self.grabber_position = grabber_position(rect)
                    self.event_box.get_window().set_cursor(CURSORS[self.grabber])
                else:
                    self.grabber_to_draw = None
                    self.grabber_position = None
                    self.event_box.get_window().set_cursor(None)
            else:
                # nothing is active
                self.grabber = None
                self.grabber_to_draw = None
                self.grabber_position = None
                self.event_box.get_window().set_cursor(None)
        self.image.queue_draw()

    def _motion_scroll_event(self, widget, event):
        """
        Handles the motion-scroll-event signal.
        """
        if not self.is_image_loaded():
            return
        if event.direction == Gdk.ScrollDirection.UP:
            self.zoom_in()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom_out()
        elif event.direction == Gdk.ScrollDirection.SMOOTH:
            if event.delta_y < 0:
                self.zoom_in()
            else:
                self.zoom_out()

    # ======================================================
    # helpers for mouse event handlers
    # ======================================================

    def _can_select(self):
        """
        Returns whether selection is currently possible, which is when
        multiple selection is enabled or otherwise when no region is
        currently selected.
        """
        return self.multiple_selection or len(self.regions) < 1

    def _modify_selection(self, dx, dy):
        """
        Changes the selection when a grabber is dragged, returns the new
        grabber if a grabber switch has happened, and the current grabber
        otherwise.
        """
        x1, y1, x2, y2 = self._rect_image_to_screen(self.current.coords())
        x1, y1, x2, y2 = MOTION_FUNCTIONS[self.grabber](x1, y1, x2, y2, dx, dy)
        (x1, y1) = self._screen_to_truncated((x1, y1))
        (x2, y2) = self._screen_to_truncated((x2, y2))
        grabber = switch_grabber(self.grabber, x1, y1, x2, y2)
        self.selection = order_coordinates((x1, y1), (x2, y2))
        return grabber

    # ======================================================
    # tooltips
    # ======================================================

    def _show_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        """
        Handles the query-tooltip signal.
        """
        if self.in_region:
            person = self.in_region.person
            if person:
                name = name_displayer.display(person)
            else:
                return False
            tooltip.set_text(name)
            return True
        else:
            return False
