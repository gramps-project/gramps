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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
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
from ..lib import Date
from ..config import config
from ..const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# LivingProxyDb
#
# -------------------------------------------------------------------------
class LivingProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all living people will be hidden from the user.
    """

    MODE_EXCLUDE_ALL = 0
    MODE_INCLUDE_LAST_NAME_ONLY = 1
    MODE_INCLUDE_FULL_NAME_ONLY = 2
    MODE_REPLACE_COMPLETE_NAME = 3
    MODE_INCLUDE_ALL = 99  # usually this will be only tested for, not invoked

    def __init__(
        self, dbase, mode, current_year=None, years_after_death=0, llocale=glocale
    ):
        """
        Create a new LivingProxyDb instance.

        :param dbase: The database to be a proxy for
        :type dbase: DbBase
        :param mode:
            The method for handling living people.
            LivingProxyDb.MODE_EXCLUDE_ALL will remove living people
                altogether.
            LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY will remove all
                information and change their given name to "[Living]" or what
                has been set in Preferences -> Text -> Private given name.
            LivingProxyDb.MODE_REPLACE_COMPLETE_NAME will remove all
                information and change their given name and surname to
                "[Living]" or whatever has been set in Preferences -> Text
                for Private surname and Private given name.
            LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY will remove all
                information but leave the entire name intact.
        :type mode: int
        :param current_year: The reference point for living determination.
         Pass an int for a year-only date, or a :class:`.Date` object for a
         fully-specified date.  If None, Today() is used.
        :type current_year: int, :class:`.Date`, or None
        :param years_after_death: The number of years after a person's death to
                                  still consider them living.
        :type years_after_death: int
        If llocale is passed in (a :class:`.GrampsLocale`), then (insofar as
        possible) the translated values will be returned instead.
        :param llocale: allow deferred translation of "[Living]"
        :type llocale: a :class:`.GrampsLocale` instance
        """
        ProxyDbBase.__init__(self, dbase)
        self.mode = mode
        if isinstance(current_year, Date):
            self.current_date = current_year
        elif current_year is not None:
            self.current_date = Date()
            self.current_date.set_year(current_year)
        else:
            self.current_date = None
        self.years_after_death = years_after_death
        self._ = llocale.translation.gettext
        self._p_f_n = self._(config.get("preferences.private-given-text"))
        self._p_s_n = self._(config.get("preferences.private-surname-text"))

    def include_person(self, handle):
        """Exclude living people in MODE_EXCLUDE_ALL; include all otherwise."""
        if self.mode == self.MODE_EXCLUDE_ALL:
            person = self.get_unfiltered_person(handle)
            if person and self.__is_living(person):
                return False
        return True

    def sanitize_person(self, data):
        """
        For modes 1-3, replace name data with restricted versions.
        Also clear all non-name data for living people.
        """
        if self.mode == self.MODE_INCLUDE_ALL:
            return data

        # Check if this person is living using the unfiltered person
        person = self.get_unfiltered_person(data.handle)
        if not person or not self.__is_living(person):
            return data

        # Person is living — restrict data based on mode
        from ..lib.json_utils import object_to_data
        from ..lib import Name, Surname, NameOriginType

        old_name_data = data.primary_name
        new_name = Name()

        new_name.set_group_as(old_name_data.group_as)
        new_name.set_sort_as(old_name_data.sort_as)
        new_name.set_display_as(old_name_data.display_as)
        new_name.set_type(old_name_data.type)

        if self.mode in (
            self.MODE_INCLUDE_LAST_NAME_ONLY,
            self.MODE_REPLACE_COMPLETE_NAME,
        ):
            new_name.set_first_name(self._p_f_n)
            new_name.set_title("")
        else:  # MODE_INCLUDE_FULL_NAME_ONLY
            new_name.set_first_name(old_name_data.first_name)
            new_name.set_suffix(old_name_data.suffix)
            new_name.set_title(old_name_data.title)
            new_name.set_call_name(old_name_data.call)
            new_name.set_nick_name(old_name_data.nick)
            new_name.set_family_nick_name(old_name_data.famnick)

        if self.mode == self.MODE_REPLACE_COMPLETE_NAME:
            surname = Surname()
            surname.set_surname(self._p_s_n)
            new_name.set_surname_list([surname])
        else:
            surns = []
            for surn_data in old_name_data.surname_list:
                from ..lib import Surname as SurnameLib

                new_surn = SurnameLib()
                new_surn.set_surname(surn_data.surname)
                new_surn.set_prefix(surn_data.prefix)
                new_surn.set_connector(surn_data.connector)
                new_surn.set_origintype(surn_data.origintype)
                new_surn.set_primary(surn_data.primary)
                if surn_data.origintype.value in [
                    NameOriginType.PATRONYMIC,
                    NameOriginType.MATRONYMIC,
                ]:
                    new_surn.set_surname(self._p_s_n)
                surns.append(new_surn)
            new_name.set_surname_list(surns)

        data.primary_name = object_to_data(new_name)

        # Clear all non-name data for living people
        data.alternate_names = []
        data.event_ref_list = []
        data.address_list = []
        data.attribute_list = []
        data.urls = []
        data.media_list = []
        data.lds_ord_list = []
        data.citation_list = []
        data.note_list = []
        data.person_ref_list = []

        return data

    def get_raw_family_data(self, handle):
        """
        Override to additionally clear family events when any parent is living.
        """
        data = super().get_raw_family_data(handle)
        if data is None:
            return None

        if self.mode == self.MODE_INCLUDE_ALL:
            return data

        # Check original (unfiltered) family for living parents
        orig = self.basedb.get_raw_family_data(handle)
        if orig is None:
            return data

        parent_is_living = False
        if orig.father_handle:
            father = self.basedb.get_person_from_handle(orig.father_handle)
            if father and self.__is_living(father):
                parent_is_living = True
        if orig.mother_handle:
            mother = self.basedb.get_person_from_handle(orig.mother_handle)
            if mother and self.__is_living(mother):
                parent_is_living = True

        if parent_is_living:
            data.event_ref_list = []

        return data

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed Gramps ID.
        """
        person = self.db.get_person_from_gramps_id(val)
        if person is None:
            return None
        return self.get_person_from_handle(person.handle)

    def get_default_person(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        if person_handle:
            return self.get_person_from_handle(person_handle)
        return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        if person_handle and self.has_person_handle(person_handle):
            return person_handle
        return None

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an iterator over a list of (class_name, handle) tuples.
        """
        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for class_name, ref_handle in handle_itr:
            if self.mode == self.MODE_INCLUDE_ALL:
                yield (class_name, ref_handle)
            elif class_name == "Person":
                person = self.db.get_person_from_handle(ref_handle)
                if person and not self.__is_living(person):
                    yield (class_name, ref_handle)
            elif class_name == "Family":
                family = self.db.get_family_from_handle(ref_handle)
                father = mother = None
                if family.father_handle:
                    father = self.db.get_person_from_handle(family.father_handle)
                if family.mother_handle:
                    mother = self.db.get_person_from_handle(family.mother_handle)
                father_not_living = father and not self.__is_living(father)
                mother_not_living = mother and not self.__is_living(mother)
                if (
                    (father is None and mother is None)
                    or (father is None and mother_not_living)
                    or (mother is None and father_not_living)
                    or (father_not_living and mother_not_living)
                ):
                    yield (class_name, ref_handle)
            else:
                yield (class_name, ref_handle)

    def __is_living(self, person):
        """
        Check if a person is considered living.
        Returns True if the person is considered living.
        """
        from ..utils.alive import probably_alive

        unfil_person = self.get_unfiltered_person(person.handle)
        return probably_alive(
            unfil_person, self.db, self.current_date, self.years_after_death
        )
