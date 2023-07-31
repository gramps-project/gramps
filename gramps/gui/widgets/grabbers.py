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
from gi.repository import Gdk

# -------------------------------------------------------------------------
#
# grabbers constants and routines
#
# -------------------------------------------------------------------------

GRABBER_INSIDE = 0
GRABBER_OUTSIDE = 1

MIN_CORNER_GRABBER = 20
MIN_SIDE_GRABBER = 20
MIN_GRABBER_PADDING = 10
MIN_SIDE_FOR_INSIDE_GRABBERS = (
    2 * (MIN_CORNER_GRABBER + MIN_GRABBER_PADDING) + MIN_SIDE_GRABBER
)

INSIDE = 0
GRABBER_UPPER_LEFT = 1
GRABBER_UPPER = 2
GRABBER_UPPER_RIGHT = 3
GRABBER_RIGHT = 4
GRABBER_LOWER_RIGHT = 5
GRABBER_LOWER = 6
GRABBER_LOWER_LEFT = 7
GRABBER_LEFT = 8


def upper_left_grabber_inner(x1, y1, x2, y2):
    return (x1, y1, x1 + MIN_CORNER_GRABBER, y1 + MIN_CORNER_GRABBER)


def upper_grabber_inner(x1, y1, x2, y2):
    return (
        x1 + MIN_CORNER_GRABBER + MIN_GRABBER_PADDING,
        y1,
        x2 - MIN_CORNER_GRABBER - MIN_GRABBER_PADDING,
        y1 + MIN_CORNER_GRABBER,
    )


def upper_right_grabber_inner(x1, y1, x2, y2):
    return (x2 - MIN_CORNER_GRABBER, y1, x2, y1 + MIN_CORNER_GRABBER)


def right_grabber_inner(x1, y1, x2, y2):
    return (
        x2 - MIN_CORNER_GRABBER,
        y1 + MIN_CORNER_GRABBER + MIN_GRABBER_PADDING,
        x2,
        y2 - MIN_CORNER_GRABBER - MIN_GRABBER_PADDING,
    )


def lower_right_grabber_inner(x1, y1, x2, y2):
    return (x2 - MIN_CORNER_GRABBER, y2 - MIN_CORNER_GRABBER, x2, y2)


def lower_grabber_inner(x1, y1, x2, y2):
    return (
        x1 + MIN_CORNER_GRABBER + MIN_GRABBER_PADDING,
        y2 - MIN_CORNER_GRABBER,
        x2 - MIN_CORNER_GRABBER - MIN_GRABBER_PADDING,
        y2,
    )


def lower_left_grabber_inner(x1, y1, x2, y2):
    return (x1, y2 - MIN_CORNER_GRABBER, x1 + MIN_CORNER_GRABBER, y2)


def left_grabber_inner(x1, y1, x2, y2):
    return (
        x1,
        y1 + MIN_CORNER_GRABBER + MIN_GRABBER_PADDING,
        x1 + MIN_CORNER_GRABBER,
        y2 - MIN_CORNER_GRABBER - MIN_GRABBER_PADDING,
    )


# outer


def upper_left_grabber_outer(x1, y1, x2, y2):
    return (x1 - MIN_CORNER_GRABBER, y1 - MIN_CORNER_GRABBER, x1, y1)


def upper_grabber_outer(x1, y1, x2, y2):
    return (x1, y1 - MIN_CORNER_GRABBER, x2, y1)


def upper_right_grabber_outer(x1, y1, x2, y2):
    return (x2, y1 - MIN_CORNER_GRABBER, x2 + MIN_CORNER_GRABBER, y1)


def right_grabber_outer(x1, y1, x2, y2):
    return (x2, y1, x2 + MIN_CORNER_GRABBER, y2)


def lower_right_grabber_outer(x1, y1, x2, y2):
    return (x2, y2, x2 + MIN_CORNER_GRABBER, y2 + MIN_CORNER_GRABBER)


def lower_grabber_outer(x1, y1, x2, y2):
    return (x1, y2, x2, y2 + MIN_CORNER_GRABBER)


def lower_left_grabber_outer(x1, y1, x2, y2):
    return (x1 - MIN_CORNER_GRABBER, y2, x1, y2 + MIN_CORNER_GRABBER)


def left_grabber_outer(x1, y1, x2, y2):
    return (x1 - MIN_CORNER_GRABBER, y1, x1, y2)


# motion


def inside_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1, x2, y2)


def upper_left_moved(x1, y1, x2, y2, dx, dy):
    return (x1 + dx, y1 + dy, x2, y2)


def upper_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1 + dy, x2, y2)


def upper_right_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1 + dy, x2 + dx, y2)


def right_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1, x2 + dx, y2)


def lower_right_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1, x2 + dx, y2 + dy)


def lower_moved(x1, y1, x2, y2, dx, dy):
    return (x1, y1, x2, y2 + dy)


def lower_left_moved(x1, y1, x2, y2, dx, dy):
    return (x1 + dx, y1, x2, y2 + dy)


def left_moved(x1, y1, x2, y2, dx, dy):
    return (x1 + dx, y1, x2, y2)


# switching

GRABBERS = [
    INSIDE,
    GRABBER_UPPER_LEFT,
    GRABBER_UPPER,
    GRABBER_UPPER_RIGHT,
    GRABBER_RIGHT,
    GRABBER_LOWER_RIGHT,
    GRABBER_LOWER,
    GRABBER_LOWER_LEFT,
    GRABBER_LEFT,
]

INNER_GRABBERS = [
    None,
    upper_left_grabber_inner,
    upper_grabber_inner,
    upper_right_grabber_inner,
    right_grabber_inner,
    lower_right_grabber_inner,
    lower_grabber_inner,
    lower_left_grabber_inner,
    left_grabber_inner,
]

OUTER_GRABBERS = [
    None,
    upper_left_grabber_outer,
    upper_grabber_outer,
    upper_right_grabber_outer,
    right_grabber_outer,
    lower_right_grabber_outer,
    lower_grabber_outer,
    lower_left_grabber_outer,
    left_grabber_outer,
]

MOTION_FUNCTIONS = [
    inside_moved,
    upper_left_moved,
    upper_moved,
    upper_right_moved,
    right_moved,
    lower_right_moved,
    lower_moved,
    lower_left_moved,
    left_moved,
]

GRABBERS_SWITCH = [
    [INSIDE, INSIDE, INSIDE],
    [GRABBER_UPPER_RIGHT, GRABBER_LOWER_RIGHT, GRABBER_LOWER_LEFT],
    [GRABBER_UPPER, GRABBER_LOWER, GRABBER_LOWER],
    [GRABBER_UPPER_LEFT, GRABBER_LOWER_LEFT, GRABBER_LOWER_RIGHT],
    [GRABBER_LEFT, GRABBER_LEFT, GRABBER_RIGHT],
    [GRABBER_LOWER_LEFT, GRABBER_UPPER_LEFT, GRABBER_UPPER_RIGHT],
    [GRABBER_LOWER, GRABBER_UPPER, GRABBER_UPPER],
    [GRABBER_LOWER_RIGHT, GRABBER_UPPER_RIGHT, GRABBER_UPPER_LEFT],
    [GRABBER_RIGHT, GRABBER_RIGHT, GRABBER_LEFT],
]

# cursors
try:
    CURSOR_UPPER = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.TOP_SIDE
    )
    CURSOR_LOWER = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.BOTTOM_SIDE
    )
    CURSOR_LEFT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.LEFT_SIDE
    )
    CURSOR_RIGHT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.RIGHT_SIDE
    )
    CURSOR_UPPER_LEFT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.TOP_LEFT_CORNER
    )
    CURSOR_UPPER_RIGHT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.TOP_RIGHT_CORNER
    )
    CURSOR_LOWER_LEFT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.BOTTOM_LEFT_CORNER
    )
    CURSOR_LOWER_RIGHT = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.BOTTOM_RIGHT_CORNER
    )
except:
    CURSOR_UPPER = None
    CURSOR_LOWER = None
    CURSOR_LEFT = None
    CURSOR_RIGHT = None
    CURSOR_UPPER_LEFT = None
    CURSOR_UPPER_RIGHT = None
    CURSOR_LOWER_LEFT = None
    CURSOR_LOWER_RIGHT = None

CURSORS = [
    None,
    CURSOR_UPPER_LEFT,
    CURSOR_UPPER,
    CURSOR_UPPER_RIGHT,
    CURSOR_RIGHT,
    CURSOR_LOWER_RIGHT,
    CURSOR_LOWER,
    CURSOR_LOWER_LEFT,
    CURSOR_LEFT,
]

# helper functions


def grabber_position(rect):
    x1, y1, x2, y2 = rect
    if (
        x2 - x1 >= MIN_SIDE_FOR_INSIDE_GRABBERS
        and y2 - y1 >= MIN_SIDE_FOR_INSIDE_GRABBERS
    ):
        return GRABBER_INSIDE
    else:
        return GRABBER_OUTSIDE


def grabber_generators(rect):
    if grabber_position(rect) == GRABBER_INSIDE:
        return INNER_GRABBERS
    else:
        return OUTER_GRABBERS


def switch_grabber(grabber, x1, y1, x2, y2):
    switch_row = GRABBERS_SWITCH[grabber]
    if x1 > x2:
        if y1 > y2:
            return switch_row[1]
        else:
            return switch_row[0]
    else:
        if y1 > y2:
            return switch_row[2]
        else:
            return grabber


def inside_rect(rect, x, y):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def can_grab(rect, x, y):
    """
    Checks if (x,y) lies within one of the grabbers of rect.
    """
    (x1, y1, x2, y2) = rect
    if (
        x2 - x1 >= MIN_SIDE_FOR_INSIDE_GRABBERS
        and y2 - y1 >= MIN_SIDE_FOR_INSIDE_GRABBERS
    ):
        # grabbers are inside
        if x < x1 or x > x2 or y < y1 or y > y2:
            return None
        for grabber in GRABBERS[1:]:
            grabber_area = INNER_GRABBERS[grabber](x1, y1, x2, y2)
            if inside_rect(grabber_area, x, y):
                return grabber
        return INSIDE
    else:
        # grabbers are outside
        if x1 <= x <= x2 and y1 <= y <= y2:
            return INSIDE
        for grabber in GRABBERS[1:]:
            grabber_area = OUTER_GRABBERS[grabber](x1, y1, x2, y2)
            if inside_rect(grabber_area, x, y):
                return grabber
        return None
