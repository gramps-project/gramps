#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Marker types.

From version 3.3 onwards, this is only kept to convert markers into tags
when loading old database files.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class MarkerType(GrampsType):
    """
    Class for handling data markers.
    """

    NONE = -1
    CUSTOM = 0
    COMPLETE = 1
    TODO_TYPE = 2

    _CUSTOM = CUSTOM
    _DEFAULT = NONE

    _DATAMAP = [
        (NONE, "", ""),
        (CUSTOM, _("Custom"), "Custom"),
        (COMPLETE, _("Complete"), "Complete"),
        (TODO_TYPE, _("ToDo"), "ToDo"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
