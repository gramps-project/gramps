#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Gramps project
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
Helpers for gramplet view configuration.
"""

MAX_GRAMPLET_COLUMNS = 10


def clamp_column_count(num):
    """
    Return a gramplet column count that is safe to build.

    :param num: Requested column count.
    :type num: int | str
    :returns: The requested count constrained to the supported range.
    :rtype: int
    """
    return min(max(int(num), 1), MAX_GRAMPLET_COLUMNS)
