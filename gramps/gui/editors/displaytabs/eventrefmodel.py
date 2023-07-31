#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       B. Malengier
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
# python
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango

WEIGHT_NORMAL = Pango.Weight.NORMAL
WEIGHT_BOLD = Pango.Weight.BOLD

from html import escape

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from ...widgets.undoablebuffer import UndoableBuffer
from gramps.gen.lib import EventRoleType, EventType, Date
from gramps.gen.datehandler import get_date, get_date_valid
from gramps.gen.config import config
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.proxy.cache import CacheProxyDb

# -------------------------------------------------------------------------
#
# Globals
#
# -------------------------------------------------------------------------
invalid_date_format = config.get("preferences.invalid-date-format")
age_precision = config.get("preferences.age-display-precision")
age_after_death = config.get("preferences.age-after-death")


# -------------------------------------------------------------------------
#
# EventRefModel
#
# -------------------------------------------------------------------------
class EventRefModel(Gtk.TreeStore):
    # index of the working group
    _ROOTINDEX = 0
    _GROUPSTRING = _("%(groupname)s - %(groupnumber)d")

    COL_DESCR = (0, str)
    COL_TYPE = (1, str)
    COL_GID = (2, str)
    COL_DATE = (3, str)
    COL_PLACE = (4, str)
    COL_ROLE = (5, str)
    COL_PARTIC = (6, str)
    COL_SORTDATE = (7, str)
    COL_EVENTREF = (8, object)
    COL_FONTWEIGHT = (9, int)
    COL_AGE = (10, str)
    COL_SORTAGE = (11, str)
    COL_PRIVATE = (12, bool)
    COL_HAS_SOURCE = (13, bool)

    COLS = (
        COL_DESCR,
        COL_TYPE,
        COL_GID,
        COL_DATE,
        COL_PLACE,
        COL_ROLE,
        COL_PARTIC,
        COL_SORTDATE,
        COL_EVENTREF,
        COL_FONTWEIGHT,
        COL_AGE,
        COL_SORTAGE,
        COL_PRIVATE,
        COL_HAS_SOURCE,
    )

    def __init__(self, event_list, db, groups, **kwargs):
        """
        @param event_list: A list of lists, every entry is a group, the entries
            in a group are the data that needs to be shown subordinate to the
            group
        @param db: a database objects that can be used to obtain info
        @param groups: a list of (key, name) tuples. key is a key for the group
            that might be used. name is the name for the group.
        @param kwargs: A dictionary of additional settings/values.
        """
        self.start_date = kwargs.get("start_date", None)
        self.end_date = kwargs.get("end_date", None)
        typeobjs = (x[1] for x in self.COLS)
        Gtk.TreeStore.__init__(self, *typeobjs)
        self.db = CacheProxyDb(db)
        self.groups = groups
        for index, group in enumerate(event_list):
            parentiter = self.append(None, row=self.row_group(index, group))
            for eventref in group:
                event = db.get_event_from_handle(eventref.ref)
                self.append(parentiter, row=self.row(index, eventref, event))

    def row_group(self, index, group):
        name = self.namegroup(index, len(group))
        spouse = self.groups[index][2]
        return [
            spouse,
            name,
            "",
            "",
            "",
            "",
            "",
            "",
            (index, None),
            WEIGHT_BOLD,
            "",
            "",
            None,
            None,
        ]

    def namegroup(self, groupindex, length):
        return self._GROUPSTRING % {
            "groupname": self.groups[groupindex][1],
            "groupnumber": length,
        }

    def row(self, index, eventref, event):
        return [
            event.get_description(),
            str(event.get_type()),
            event.get_gramps_id(),
            self.column_date(eventref),
            self.column_place(eventref),
            self.column_role(eventref),
            self.column_participant(eventref),
            self.column_sort_date(eventref),
            (index, eventref),
            self.colweight(index),
            self.column_age(event),
            self.column_sort_age(event),
            eventref.get_privacy(),
            event.has_citations(),
        ]

    def colweight(self, index):
        return WEIGHT_NORMAL

    def column_role(self, event_ref):
        return str(event_ref.get_role())

    def column_date(self, event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        retval = get_date(event)
        if not get_date_valid(event):
            return invalid_date_format % escape(retval)
        else:
            return retval

    def column_sort_date(self, event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        date = event.get_date_object()
        if date:
            return "%09d" % date.get_sort_value()
        else:
            return ""

    def column_place(self, event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                return place_displayer.display_event(self.db, event)
        return ""

    def column_participant(self, event_ref):
        return get_participant_from_event(self.db, event_ref.ref)

    def column_age(self, event):
        """
        Returns a string representation of age in years.  Change
        precision=2 for "year, month", or precision=3 for "year,
        month, days"
        """
        date = event.get_date_object()
        if date and self.start_date:
            if (
                date == self.start_date
                and date.modifier == Date.MOD_NONE
                and not (
                    event.get_type().is_death_fallback()
                    or event.get_type() == EventType.DEATH
                )
            ):
                return ""
            elif self.end_date and self.end_date < date and not age_after_death:
                return ""
            else:
                return (date - self.start_date).format(precision=age_precision)
        else:
            return ""

    def column_sort_age(self, event):
        """
        Returns a string version of number of days of age.
        """
        date = event.get_date_object()
        if date and self.start_date:
            return "%09d" % int(date - self.start_date)
        else:
            return ""
