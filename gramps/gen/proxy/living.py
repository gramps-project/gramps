#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2016       Matt Keenan <matt.keenan@gmail.com>
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
Proxy class for the Gramps databases. Filter out all living people.
"""

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from .proxybase import ProxyDbBase
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
from ..config import config
from ..const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# LivingProxyDb
#
# -------------------------------------------------------------------------
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
        # alive status by using the basedb:
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

    def get_family_map(self):
        map = {}
        for family in self.db.iter_families():
            father_not_living = family.father_handle in self.proxy_map["Person"]
            mother_not_living = family.mother_handle in self.proxy_map["Person"]
            if (
                (
                    family.father_handle is None and family.mother_handle is None
                )  # family with no parents
                or (
                    family.father_handle is None and mother_not_living
                )  # no father, dead mother
                or (
                    family.mother_handle is None and father_not_living
                )  # no mother, dead father
                or (father_not_living and mother_not_living)  # both parents dead
            ):
                map[family.handle] = {"surname": "TODO"}
        return map

    def proxy_process_family(self, family):
        parent_is_living = False

        father_handle = family.get_father_handle()
        if father_handle:
            father = self.db.get_person_from_handle(father_handle)
            if father and father_handle in self.proxy_map["Person"]:
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_father_handle(None)

        mother_handle = family.get_mother_handle()
        if mother_handle:
            if mother_handle in self.proxy_map["Person"]:
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_mother_handle(None)

        if parent_is_living:
            # Clear all events for families where a parent is living.
            family.set_event_ref_list([])

        if self.mode == self.MODE_EXCLUDE_ALL:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                if child_handle in self.proxy_map["Person"]:
                    family.remove_child_ref(child_ref)

        return family

    def proxy_process_person(self, person):
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
