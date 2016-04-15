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

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from .proxybase import ProxyDbBase
from ..lib import (Date, Person, Name, Surname, NameOriginType, Family, Source,
                   Citation, Event, Media, Place, Repository, Note, Tag)
from ..utils.alive import probably_alive
from ..config import config
from gramps.gen.db.base import sort_objects
from gramps.gen.const import GRAMPS_LOCALE as glocale

#-------------------------------------------------------------------------
#
# LivingProxyDb
#
#-------------------------------------------------------------------------
class LivingProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all living people will be hidden from the user.
    """
    MODE_EXCLUDE_ALL  = 0
    MODE_INCLUDE_LAST_NAME_ONLY = 1
    MODE_INCLUDE_FULL_NAME_ONLY = 2
    MODE_REPLACE_COMPLETE_NAME = 3
    MODE_INCLUDE_ALL = 99 # usually this will be only tested for, not invoked

    def __init__(self, dbase, mode,
                 current_year=None, years_after_death=0, llocale=glocale):
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
        :param current_year: The current year to use for living determination.
         If None is supplied, the current year will be found from the system.
        :type current_year: int or None
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
        if current_year is not None:
            self.current_date = Date()
            self.current_date.set_year(current_year)
        else:
            self.current_date = None
        self.years_after_death = years_after_death
        self._ = llocale.translation.gettext
        self._p_f_n = self._(config.get('preferences.private-given-text'))
        self._p_s_n = self._(config.get('preferences.private-surname-text'))

        self.__tables = {
            'Person':
            {
                "handle_func": self.get_person_from_handle,
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                "iter_func": self.iter_people,
                "count_func": self.get_number_of_people,
            },
            'Family':
            {
                "handle_func": self.get_family_from_handle,
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                "iter_func": self.iter_families,
                "count_func": self.get_number_of_families,
            },
            'Source':
            {
                "handle_func": self.get_source_from_handle,
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                "iter_func": self.iter_sources,
                "count_func": self.get_number_of_sources,
            },
            'Citation':
            {
                "handle_func": self.get_citation_from_handle,
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                "iter_func": self.iter_citations,
                "count_func": self.get_number_of_citations,
            },
            'Event':
            {
                "handle_func": self.get_event_from_handle,
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                "iter_func": self.iter_events,
                "count_func": self.get_number_of_events,
            },
            'Media':
            {
                "handle_func": self.get_media_from_handle,
                "gramps_id_func": self.get_media_from_gramps_id,
                "class_func": Media,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_handles,
                "iter_func": self.iter_media,
                "count_func": self.get_number_of_media,
            },
            'Place':
            {
                "handle_func": self.get_place_from_handle,
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                "iter_func": self.iter_places,
                "count_func": self.get_number_of_places,
            },
            'Repository':
            {
                "handle_func": self.get_repository_from_handle,
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                "iter_func": self.iter_repositories,
                "count_func": self.get_number_of_repositories,
            },
            'Note':
            {
                "handle_func": self.get_note_from_handle,
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                "iter_func": self.iter_notes,
                "count_func": self.get_number_of_notes,
            },
            'Tag':
            {
                "handle_func": self.get_tag_from_handle,
                "gramps_id_func": None,
                "class_func": Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                "iter_func": self.iter_tags,
                "count_func": self.get_number_of_tags,
            }
        }

    def get_table_func(self, table=None, func=None):
        """
        Private implementation of get_table_func.
        """
        if table is None:
            return list(self.__tables.keys())
        elif func is None:
            return self.__tables[table]
        elif func in self.__tables[table].keys():
            return self.__tables[table][func]
        else: 
            return super().get_table_func(table, func)

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_handle(handle)
        if person and self.__is_living(person):
            if self.mode == self.MODE_EXCLUDE_ALL:
                person = None
            else:
                person = self.__restrict_person(person)
        return person

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed handle.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_handle(handle)
        family = self.__remove_living_from_family(family)
        return family

    def iter_people(self, order_by=None):
        """
        Protected version of iter_people
        """
        if order_by:
            retval = []
            for person in filter(None, self.db.iter_people()):
                if self.__is_living(person):
                    if self.mode == self.MODE_EXCLUDE_ALL:
                        continue
                    else:
                        retval.append(self.__restrict_person(person))
                else:
                    retval.append(person)
            retval = sort_objects(retval, order_by, self)
            for item in retval:
                yield item
        else:
            for person in filter(None, self.db.iter_people()):
                if self.__is_living(person):
                    if self.mode == self.MODE_EXCLUDE_ALL:
                        continue
                    else:
                        yield self.__restrict_person(person)
                else:
                    yield person

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        if person and self.__is_living(person):
            if self.mode == self.MODE_EXCLUDE_ALL:
                return None
            else:
                return self.__restrict_person(person)
        else:
            return person

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        family = self.__remove_living_from_family(family)
        return family

    def include_person(self, handle):
        if self.mode == self.MODE_EXCLUDE_ALL:
            person = self.get_unfiltered_person(handle)
            if person and self.__is_living(person):
                return False
        return True

    def get_default_person(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        if person_handle:
            return self.get_person_from_handle(person_handle)
        return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        if person_handle and self.get_person_from_handle(person_handle):
                return person_handle
        return None

    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        if self.get_person_from_handle(handle):
            return True
        return False

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an iterator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        :type include_classes: list of class names

        This default implementation does a sequential scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

        >    result_list = list(find_backlink_handles(handle))
        """
        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for (class_name, handle) in handle_itr:
            if class_name == 'Person':
                if not self.get_person_from_handle(handle):
                    continue
            yield (class_name, handle)
        return

    def __is_living(self, person):
        """
        Check if a person is considered living.
        Returns True if the person is considered living.
        Returns False if the person is not considered living.
        """
        person_handle = person.get_handle()
        unfil_person = self.get_unfiltered_person(person_handle)
        return probably_alive( unfil_person,
                               self.db,
                               self.current_date,
                               self.years_after_death )

    def __remove_living_from_family(self, family):
        """
        Remove information from a family that pertains to living people.
        Returns a family instance with information about living people removed.
        Returns None if family is None.
        """
        if family is None:
            return None

        parent_is_living = False

        father_handle = family.get_father_handle()
        if father_handle:
            father = self.db.get_person_from_handle(father_handle)
            if father and self.__is_living(father):
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_father_handle(None)

        mother_handle = family.get_mother_handle()
        if mother_handle:
            mother = self.db.get_person_from_handle(mother_handle)
            if mother and self.__is_living(mother):
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_mother_handle(None)

        if parent_is_living:
            # Clear all events for families where a parent is living.
            family.set_event_ref_list([])

        if self.mode == self.MODE_EXCLUDE_ALL:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                child = self.db.get_person_from_handle(child_handle)
                if child and self.__is_living(child):
                    family.remove_child_ref(child_ref)

        return family

    def __restrict_person(self, person):
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
        if (self.mode == self.MODE_INCLUDE_LAST_NAME_ONLY or
            self.mode == self.MODE_REPLACE_COMPLETE_NAME):
            new_name.set_first_name(self._p_f_n)
            new_name.set_title("")
        else: # self.mode == self.MODE_INCLUDE_FULL_NAME_ONLY
            new_name.set_first_name(old_name.get_first_name())
            new_name.set_suffix(old_name.get_suffix())
            new_name.set_title(old_name.get_title())

        surnlst = []
        if self.mode == self.MODE_REPLACE_COMPLETE_NAME:
            surname = Surname(source=old_name.get_primary_surname())
            surname.set_surname(self._p_s_n)
            surnlst.append(surname)
        else:
            for surn in old_name.get_surname_list():
                surname = Surname(source=surn)
                if int(surname.origintype) in [NameOriginType.PATRONYMIC,
                                               NameOriginType.MATRONYMIC]:
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
        new_person.set_parent_family_handle_list(
                                        person.get_parent_family_handle_list() )
        new_person.set_tag_list(person.get_tag_list())

        return new_person

