#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2025       Doug Blank <doug.blank@gmail.com>
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
Proxy class for a Gramps database.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import types
import functools

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from ..db import DbReadBase
from ..db.bookmarks import DbBookmarks
from ..const import GRAMPS_LOCALE as glocale
from ..config import config
from .private import sanitize_person
from ..lib.json_utils import object_to_data
from ..lib import (
    Date,
    Person,
    Name,
    Surname,
    NameOriginType,
    Family,
    Source,
    Citation,
    Event,
    Media,
    Place,
    Repository,
    Note,
    Tag,
)


class ProxyDbBase:
    def __init__(self, db):
        """
        Create a new ProxyDb instance.
        """
        self.db = db  # The db on the next lower layer
        self.person_map = self.get_person_map()

        self.bookmarks = DbBookmarks(
            self.filter_person_handles(self.db.bookmarks.get())
        )

    def __getattr__(self, name):
        return getattr(self.db, name)

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for handle, data in self.db._iter_raw_person_data():
            map[handle] = {
                "surname": (
                    data.primary_name.surname_list[0].surname
                    if data.primary_name.surname_list
                    else ""
                )
            }
        return map

    def filter_person_handles(self, handles):
        return [handle for handle in handles if handle in self.person_map]

    def _iter_raw_person_data(self):
        for handle in self.person_map:
            # Currently the proxies use Gramps Objects for processing:
            person = self.get_person_from_handle(handle)
            yield handle, object_to_data(person)

    def get_number_of_people(self):
        return len(self.person_map)


class PrivateProxyDb(ProxyDbBase):
    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for handle, data in self.db._iter_raw_person_data():
            if not data.private:
                map[handle] = {
                    "surname": (
                        data.primary_name.surname_list[0].surname
                        if data.primary_name.surname_list
                        else ""
                    )
                }
        return map

    @functools.cache
    def get_person_from_handle(self, handle):
        person = self.db.get_person_from_handle(handle)
        privatized = self.process_person(person)
        return privatized

    def process_person(self, person):
        return sanitize_person(self.db, person)

    def iter_people(self):
        for handle in self.person_map:
            yield self.get_person_from_handle(handle)


class LivingProxyDb(ProxyDbBase):
    MODE_EXCLUDE_ALL = 0
    MODE_INCLUDE_LAST_NAME_ONLY = 1
    MODE_INCLUDE_FULL_NAME_ONLY = 2
    MODE_REPLACE_COMPLETE_NAME = 3
    MODE_INCLUDE_ALL = 99  # usually this will be only tested for, not invoked

    def __init__(
        self, db, mode, current_year=None, years_after_death=0, llocale=glocale
    ):
        self.mode = mode
        if current_year is not None:
            self.current_date = Date()
            self.current_date.set_year(current_year)
        else:
            self.current_date = None
        self.years_after_death = years_after_death
        self._ = llocale.translation.gettext
        self._p_f_n = self._(config.get("preferences.private-given-text"))
        self._p_s_n = self._(config.get("preferences.private-surname-text"))

        super().__init__(db)

    def is_living(self, person):
        """
        Check if a person is considered living.
        Returns True if the person is considered living.
        Returns False if the person is not considered living.
        """
        from ..utils.alive import probably_alive

        # Note: probably_alive uses *all* data to compute
        # alive status
        return probably_alive(
            person, self.db.basedb, self.current_date, self.years_after_death
        )

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for person in self.db.iter_people():
            if self.is_living(person):
                if self.mode == self.MODE_EXCLUDE_ALL:
                    continue
                elif self.mode == self.MODE_REPLACE_COMPLETE_NAME:
                    surname = self._p_s_n
                else:
                    surname = (
                        person.primary_name.surname_list[0].surname
                        if person.primary_name.surname_list
                        else ""
                    )

                map[person.handle] = {"surname": surname}
            else:
                map[person.handle] = {
                    "surname": (
                        person.primary_name.surname_list[0].surname
                        if person.primary_name.surname_list
                        else ""
                    )
                }

        return map

    @functools.cache
    def get_person_from_handle(self, handle):
        person = self.db.get_person_from_handle(handle)
        processed = self.process_person(person)
        return processed

    def process_person(self, person):
        """
        Remove information from a person and replace the first name with
        "[Living]" or what has been set in Preferences -> Text.
        """
        new_person = Person()
        new_name = Name()
        old_name = person.get_primary_name()

        new_name.set_group_as(old_name.get_group_as())
        new_name.set_sort_as(old_name.get_sort_as())
        new_name.set_display_as(old_name.get_display_as())
        new_name.set_type(old_name.get_type())
        if (
            self.mode == self.MODE_INCLUDE_LAST_NAME_ONLY
            or self.mode == self.MODE_REPLACE_COMPLETE_NAME
        ):
            new_name.set_first_name(self._p_f_n)
            new_name.set_title("")
        else:  # self.mode == self.MODE_INCLUDE_FULL_NAME_ONLY
            new_name.set_first_name(old_name.get_first_name())
            new_name.set_suffix(old_name.get_suffix())
            new_name.set_title(old_name.get_title())
            new_name.set_call_name(old_name.get_call_name())
            new_name.set_nick_name(old_name.get_nick_name())
            new_name.set_family_nick_name(old_name.get_family_nick_name())

        surnlst = []
        if self.mode == self.MODE_REPLACE_COMPLETE_NAME:
            surname = Surname(source=old_name.get_primary_surname())
            surname.set_surname(self._p_s_n)
            surnlst.append(surname)
        else:
            for surn in old_name.get_surname_list():
                surname = Surname(source=surn)
                if int(surname.origintype) in [
                    NameOriginType.PATRONYMIC,
                    NameOriginType.MATRONYMIC,
                ]:
                    surname.set_surname(self._p_s_n)
                surnlst.append(surname)

        new_name.set_surname_list(surnlst)
        new_person.set_primary_name(new_name)
        new_person.set_privacy(person.get_privacy())
        new_person.set_gender(person.get_gender())
        new_person.set_gramps_id(person.get_gramps_id())
        new_person.set_handle(person.get_handle())
        new_person.set_change_time(person.get_change_time())
        new_person.set_family_handle_list(person.get_family_handle_list())
        new_person.set_parent_family_handle_list(person.get_parent_family_handle_list())
        new_person.set_tag_list(person.get_tag_list())

        return new_person

    def iter_people(self):
        for handle in self.person_map:
            yield self.get_person_from_handle(handle)
