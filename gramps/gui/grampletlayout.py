#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps project
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Pure (GUI-free) layout helpers for the gramplet pane / Dashboard.

This module deliberately imports nothing from ``gi`` or ``gramps.gui`` so the
column-placement arithmetic can be unit-tested headlessly, without a display.
``GrampletPane`` (``gramps.gui.widgets.grampletpane``) routes its drop/add
placement through :func:`column_index_for_x`, so the regression test exercises
the real production decision rather than a copy of it.
"""


def column_index_for_x(x, column_bounds):
    """
    Return the index of the column that horizontal position *x* falls in.

    *x* and *column_bounds* must be expressed in the **same** coordinate
    space -- the gramplet pane's event-box / content space, which spans all
    the columns together (it is *wider* than the visible viewport whenever
    the configured column count makes the content overflow and scroll).

    :param x: horizontal position of the drop / click, in content coords.
    :type x: int or float
    :param column_bounds: ordered ``(start, width)`` pair per column, in the
        same coordinate space as *x*.
    :type column_bounds: list of (int, int)
    :returns: an index guaranteed to lie in ``range(len(column_bounds))``.
    :rtype: int

    The returned index is always in range: a position left of every column
    maps to the first column, a position right of every column maps to the
    last.  Mapping against each column's own allocation (rather than dividing
    the *viewport* width evenly) is what keeps a newly-added gramplet in a
    visible, on-screen column for any configured column count -- the fix for
    bug #13865, where dividing the narrower viewport width scaled the drop
    position up and sent it to a far-right column scrolled off screen.
    """
    if not column_bounds:
        return 0
    for index, (start, width) in enumerate(column_bounds):
        if x < start + width:
            return index
    return len(column_bounds) - 1
