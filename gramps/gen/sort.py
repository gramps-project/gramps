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
Provide sorting routines for use in Gramps. Since these functions are
intended to provide fast sorting, they tend to bypass access methods,
and directly use class members. For this reason, care needs to be taken
to make sure these remain in sync with the rest of the design.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from .lib import Date
from .utils.db import get_birth_or_fallback
from .display.name import displayer as _nd
from .display.place import displayer as _pd
from .const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


class Sort:
    def __init__(self, database):
        self.database = database

    ##    def by_last_name(self, first_id, second_id):
    ##        """Sort routine for comparing two last names. If last names are equal,
    ##        uses the given name and suffix"""
    ##        first = self.database.get_person_from_handle(first_id)
    ##        second = self.database.get_person_from_handle(second_id)
    ##
    ##        name1 = first.get_primary_name()
    ##        name2 = second.get_primary_name()
    ##
    ##        fsn = name1.get_surname()
    ##        ssn = name2.get_surname()
    ##
    ##        if fsn == ssn :
    ##            ffn = name1.get_first_name()
    ##            sfn = name2.get_first_name()
    ##            if ffn == sfn:
    ##                return glocale.strcoll(name1.get_suffix(), name2.get_suffix())
    ##            else:
    ##                return glocale.strcoll(ffn, sfn)
    ##        else:
    ##            return glocale.strcoll(fsn, ssn)

    def by_last_name_key(self, first_id):
        """
        Sort routine for comparing two last names. If last names are equal,
        uses the given name and suffix
        """
        first = self.database.get_person_from_handle(first_id)

        name1 = first.get_primary_name()

        fsn = name1.get_surname()
        ffn = name1.get_first_name()
        fsu = name1.get_suffix()
        return glocale.sort_key(fsn + ffn + fsu)

    ##    def by_sorted_name(self, first_id, second_id):
    ##        """
    ##        Sort routine for comparing two displayed names.
    ##        """
    ##
    ##        first = self.database.get_person_from_handle(first_id)
    ##        second = self.database.get_person_from_handle(second_id)
    ##
    ##        name1 = _nd.sorted(first)
    ##        name2 = _nd.sorted(second)
    ##
    ##        return glocale.strcoll(name1, name2)

    def by_sorted_name_key(self, first_id):
        """
        Sort routine for comparing two displayed names.
        """

        first = self.database.get_person_from_handle(first_id)

        name1 = _nd.sorted(first)

        return glocale.sort_key(name1)

    ##    def by_birthdate(self, first_id, second_id):
    ##        """Sort routine for comparing two people by birth dates. If the birth
    ##        dates are equal, sorts by name"""
    ##        first = self.database.get_person_from_handle(first_id)
    ##        second = self.database.get_person_from_handle(second_id)
    ##
    ##        birth1 = get_birth_or_fallback(self.database, first)
    ##        if birth1:
    ##            date1 = birth1.get_date_object()
    ##        else:
    ##            date1 = Date()
    ##
    ##        birth2 = get_birth_or_fallback(self.database, second)
    ##        if birth2:
    ##            date2 = birth2.get_date_object()
    ##        else:
    ##            date2 = Date()
    ##
    ##        dsv1 = date1.get_sort_value()
    ##        dsv2 = date2.get_sort_value()
    ##
    ##        val = cmp(dsv1, dsv2)
    ##        if val == 0:
    ##            return self.by_last_name(first_id, second_id)
    ##        return val

    def by_birthdate_key(self, first_id):
        """
        Sort routine for comparing two people by birth dates. If the birth dates
        are equal, sorts by name
        """
        first = self.database.get_person_from_handle(first_id)

        birth1 = get_birth_or_fallback(self.database, first)
        if birth1:
            date1 = birth1.get_date_object()
        else:
            date1 = Date()

        dsv1 = date1.get_sort_value()
        return "%08d" % dsv1 + str(self.by_last_name_key(first_id))

    ##    def by_date(self, a_id, b_id):
    ##        """Sort routine for comparing two events by their dates. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        a_obj = self.database.get_event_from_handle(a_id)
    ##        b_obj = self.database.get_event_from_handle(b_id)
    ##        dsv1 = a_obj.get_date_object().get_sort_value()
    ##        dsv2 = b_obj.get_date_object().get_sort_value()
    ##        return cmp(dsv1, dsv2)

    def by_date_key(self, a_id):
        """Sort routine for comparing two events by their dates."""
        if not a_id:
            return 0
        a_obj = self.database.get_event_from_handle(a_id)
        return a_obj.get_date_object().get_sort_value()

    ##    def by_place_title(self, a_id, b_id):
    ##        """Sort routine for comparing two places. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        a_obj = self.database.get_place_from_handle(a_id)
    ##        b_obj = self.database.get_place_from_handle(b_id)
    ##        return glocale.strcoll(a_obj.title, b_obj.title)

    def by_place_title_key(self, a_id):
        """Sort routine for comparing two places."""
        if not a_id:
            return 0
        a_obj = self.database.get_place_from_handle(a_id)
        title = _pd.display(self.database, a_obj)
        return glocale.sort_key(title)

    ##    def by_event_place(self, a_id, b_id):
    ##        """Sort routine for comparing two events by their places. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        evt_a = self.database.get_event_from_handle(a_id)
    ##        evt_b = self.database.get_event_from_handle(b_id)
    ##        plc_a = self.database.get_place_from_handle(evt_a.get_place_handle())
    ##        plc_b = self.database.get_place_from_handle(evt_b.get_place_handle())
    ##        plc_a_title = ""
    ##        plc_b_title = ""
    ##        if plc_a:
    ##            plc_a_title = plc_a.title
    ##        if plc_b:
    ##            plc_b_title = plc_b.title
    ##        return glocale.strcoll(plc_a_title, plc_b_title)

    def by_event_place_key(self, a_id):
        """Sort routine for comparing two events by their places."""
        if not a_id:
            return 0
        evt_a = self.database.get_event_from_handle(a_id)
        title = _pd.display_event(self.database, evt_a)
        return glocale.sort_key(title)

    ##    def by_event_description(self, a_id, b_id):
    ##        """Sort routine for comparing two events by their descriptions. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        evt_a = self.database.get_event_from_handle(a_id)
    ##        evt_b = self.database.get_event_from_handle(b_id)
    ##        return glocale.strcoll(evt_a.get_description(),
    ##                               evt_b.get_description())

    def by_event_description_key(self, a_id):
        """Sort routine for comparing two events by their descriptions."""
        if not a_id:
            return 0
        evt_a = self.database.get_event_from_handle(a_id)
        return glocale.sort_key(evt_a.get_description())

    ##    def by_event_id(self, a_id, b_id):
    ##        """Sort routine for comparing two events by their ID. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        evt_a = self.database.get_event_from_handle(a_id)
    ##        evt_b = self.database.get_event_from_handle(b_id)
    ##        return glocale.strcoll(evt_a.get_gramps_id(), evt_b.get_gramps_id())

    def by_event_id_key(self, a_id):
        """Sort routine for comparing two events by their ID."""
        if not a_id:
            return 0
        evt_a = self.database.get_event_from_handle(a_id)
        return glocale.sort_key(evt_a.get_gramps_id())

    ##    def by_event_type(self, a_id, b_id):
    ##        """Sort routine for comparing two events by their type. """
    ##        if not (a_id and b_id):
    ##            return 0
    ##        evt_a = self.database.get_event_from_handle(a_id)
    ##        evt_b = self.database.get_event_from_handle(b_id)
    ##        return glocale.strcoll(str(evt_a.get_type()), str(evt_b.get_type()))

    def by_event_type_key(self, a_id):
        """Sort routine for comparing two events by their type."""
        if not a_id:
            return 0
        evt_a = self.database.get_event_from_handle(a_id)
        return glocale.sort_key(str(evt_a.get_type()))

    ##    def by_media_title(self,a_id,b_id):
    ##        """Sort routine for comparing two media objects by their title. """
    ##        if not (a_id and b_id):
    ##            return False
    ##        a = self.database.get_media_from_handle(a_id)
    ##        b = self.database.get_media_from_handle(b_id)
    ##        return glocale.strcoll(a.desc, b.desc)

    def by_media_title_key(self, a_id):
        """Sort routine for comparing two media objects by their title."""
        if not a_id:
            return False
        obj_a = self.database.get_media_from_handle(a_id)
        return glocale.sort_key(obj_a.desc)
