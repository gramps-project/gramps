#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2019       Nick Hall
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
"""
Provides a simple histogram widget for use in gramplets.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import math

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango, PangoCairo

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from ...gen.const import GRAMPS_LOCALE as glocale


class Histogram(Gtk.DrawingArea):
    """
    A simple histogram widget for use in gramplets.
    """

    __gsignals__ = {"clicked": (GObject.SignalFlags.RUN_FIRST, None, (int,))}

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        self.connect("motion-notify-event", self.on_pointer_motion)
        self.connect("button-press-event", self.on_button_press)

        self.title = ""
        self.bucket_axis = ""
        self.value_axis = ""
        self.grid_lines = True
        self.data = []
        self.labels = []
        self.tooltip = ""
        self.highlight = None
        self.__bars = None
        self.__active = -1

    def set_title(self, title):
        """
        Set the main chart title.
        @param title: The main chart title.
        @type title: str
        """
        self.title = title

    def set_bucket_axis(self, bucket_axis):
        """
        Set the bucket axis label.
        @param bucket_axis: The bucket axis label.
        @type bucket_axis: str
        """
        self.bucket_axis = bucket_axis

    def set_value_axis(self, value_axis):
        """
        Set the value axis label.
        @param bucket_axis: The value axis label.
        @type bucket_axis: str
        """
        self.value_axis = value_axis

    def set_grid_lines(self, grid_lines):
        """
        Specify if grid lines should be displayed.
        @param grid_lines: True if grid lines should be displayed.
        @type grid_lines: bool
        """
        self.grid_lines = grid_lines

    def set_values(self, data):
        """
        Set the chart values.
        @param data: A list of values, one for each bucket.
        @type data: list
        """
        self.data = data

    def set_labels(self, labels):
        """
        Set the labels on the bucket axis.
        @param labels: A list of labels, one for each bucket.
        @type labels: list
        """
        self.labels = labels

    def set_tooltip(self, tooltip):
        """
        Set the tooltip to display on bars.  If the string contains a "%d"
        substitution variable it will be replaced with the value that the
        bar represents.
        @param labels: A tooltip.
        @type labels: str
        """
        self.tooltip = tooltip

    def set_highlight(self, highlight):
        """
        Specify the bars to hightlight.
        @param labels: A list of bucket numbers.
        @type labels: list
        """
        self.highlight = highlight

    def do_draw(self, cr):
        """
        A custom draw method for this widget.
        @param cr: A cairo context.
        @type cr: cairo.Context
        """
        allocation = self.get_allocation()
        context = self.get_style_context()
        fg_color = context.get_color(context.get_state())
        cr.set_source_rgba(*fg_color)

        # Title
        layout = self.create_pango_layout(self.title)
        width, height = layout.get_pixel_size()
        offset = height + 5

        # Labels
        label_width = 0
        for i in range(len(self.labels)):
            layout = self.create_pango_layout(self.labels[i])
            width, height = layout.get_pixel_size()
            if width > label_width:
                label_width = width
            cr.move_to(0, i * height + offset)
            PangoCairo.show_layout(cr, layout)

        layout = self.create_pango_layout(self.bucket_axis)
        width, height = layout.get_pixel_size()
        if width > label_width:
            label_width = width
        label_width += 5
        cr.move_to((label_width - width) / 2, 0)
        PangoCairo.show_layout(cr, layout)

        # Values
        percent_width = 0
        total = sum(self.data)
        for i in range(len(self.data)):
            if total > 0:
                percent = glocale.format_string("%.2f", self.data[i] / total * 100)
            else:
                percent = ""
            layout = self.create_pango_layout(percent)
            width, height = layout.get_pixel_size()
            if width > percent_width:
                percent_width = width
            cr.move_to(allocation.width - width, i * height + offset)
            PangoCairo.show_layout(cr, layout)

        layout = self.create_pango_layout(self.value_axis)
        width, height = layout.get_pixel_size()
        if width > percent_width:
            percent_width = width
        percent_width += 5
        cr.move_to(allocation.width - (percent_width + width) / 2, 0)
        PangoCairo.show_layout(cr, layout)

        chart_width = allocation.width - label_width - percent_width
        spacing = 2

        # Title
        layout = self.create_pango_layout(self.title)
        layout.set_ellipsize(Pango.EllipsizeMode.END)
        layout.set_width((chart_width - 10) * Pango.SCALE)
        cr.move_to(label_width + 5, 0)
        PangoCairo.show_layout(cr, layout)

        # Border
        cr.move_to(0, offset)
        cr.line_to(allocation.width, offset)
        cr.stroke()

        bottom = len(self.data) * height + (2 * spacing) + offset
        cr.move_to(0, bottom)
        cr.line_to(allocation.width, bottom)
        cr.stroke()

        cr.move_to(label_width, 0)
        cr.line_to(label_width, bottom)
        cr.stroke()

        cr.move_to(allocation.width - percent_width, 0)
        cr.line_to(allocation.width - percent_width, bottom)
        cr.stroke()

        # Ticks and grid lines
        tick_step, maximum = self.__get_tick_step(chart_width)
        count = 0
        while count <= maximum:
            # draw tick
            tick_pos = label_width + chart_width * count / maximum
            cr.move_to(tick_pos, bottom)
            cr.line_to(tick_pos, bottom + 5)
            cr.stroke()
            # draw grid line
            if self.grid_lines:
                cr.set_dash([1, 2])
                cr.move_to(tick_pos, bottom)
                cr.line_to(tick_pos, (2 * spacing) + offset)
                cr.stroke()
                cr.set_dash([])
            layout = self.create_pango_layout("%d" % count)
            width, height = layout.get_pixel_size()
            cr.move_to(tick_pos - (width / 2), bottom + 5)
            PangoCairo.show_layout(cr, layout)
            count += tick_step

        # Bars
        cr.set_line_width(1)
        bar_size = height - (2 * spacing)
        self.__bars = []
        for i in range(len(self.labels)):
            cr.rectangle(
                label_width,
                i * height + (2 * spacing) + offset,
                chart_width * self.data[i] / maximum,
                bar_size,
            )
            self.__bars.append(
                [
                    label_width,
                    i * height + (2 * spacing) + offset,
                    chart_width * self.data[i] / maximum,
                    bar_size,
                ]
            )
            if i in self.highlight:
                if self.__active == i:
                    cr.set_source_rgba(1, 0.7, 0, 1)
                else:
                    cr.set_source_rgba(1, 0.5, 0, 1)
            else:
                if self.__active == i:
                    cr.set_source_rgba(0.7, 0.7, 1, 1)
                else:
                    cr.set_source_rgba(0.5, 0.5, 1, 1)

            cr.fill_preserve()
            cr.set_source_rgba(*fg_color)
            cr.stroke()

        self.set_size_request(-1, bottom + height + 5)

    def __get_tick_step(self, chart_width):
        """
        A method used to calculate the value axis scale and label spacing.
        @param chart_width: The chart size in pixels.
        @type chart_width: int
        """
        max_data = max(self.data)
        if max_data == 0:
            return 1, 1
        digits = int(math.log10(max_data)) + 1
        ticks = chart_width / (digits * 10 * 3)
        approx_step = max_data / ticks
        if approx_step < 1:
            approx_step = 1
        multiplier = 10 ** int(math.log10(approx_step))
        intervals = [1, 2, 5, 10]
        for interval in intervals:
            if interval >= approx_step / multiplier:
                break
        step = interval * multiplier
        max_value = (int(max_data / step) + 1) * step
        return step, max_value

    def on_pointer_motion(self, _dummy, event):
        """
        Called when the pointer is moved.
        @param _dummy: This widget.  Unused.
        @type _dummy: Gtk.Widget
        @param event: An event.
        @type event: Gdk.Event
        """
        if self.__bars is None:
            return False
        active = -1
        for i, bar in enumerate(self.__bars):
            if (
                event.x > bar[0]
                and event.x < bar[0] + bar[2]
                and event.y > bar[1]
                and event.y < bar[1] + bar[3]
            ):
                active = i
        if self.__active != active:
            self.__active = active
            self.queue_draw()
            if active == -1:
                self.set_tooltip_text("")
            else:
                if "%d" in self.tooltip:
                    self.set_tooltip_text(self.tooltip % self.data[active])
                else:
                    self.set_tooltip_text(self.tooltip)
        return False

    def on_button_press(self, _dummy, event):
        """
        Called when a mouse button is clicked.
        @param _dummy: This widget.  Unused.
        @type _dummy: Gtk.Widget
        @param event: An event.
        @type event: Gdk.Event
        """
        if (
            event.button == 1
            and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS
            and self.__active != -1
        ):
            self.emit("clicked", self.__active)
