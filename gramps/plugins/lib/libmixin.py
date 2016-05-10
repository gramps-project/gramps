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
Mixin for DbDir to enable find_from_handle and check_from_handle methods.
"""

#------------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------------
from gramps.gen.lib import (Person, Family, Event, Place, Source,
                     Media, Repository, Note, Tag)

#------------------------------------------------------------------------------
#
# DbMixin class
#
#------------------------------------------------------------------------------
class DbMixin:
    """
    DbMixin -- a collection of methods to be added to the main
    gramps database class for use with import functions.  To enable these
    functions, add the following code to your module:

        if DbMixin not in database.__class__.__bases__:
        database.__class__.__bases__ = (DbMixin,) +  \
                                        database.__class__.__bases__

    where "database" is the object name of your instance of the gramps
    database.
    """

    def __find_primary_from_handle(self, handle, transaction, class_type,
                                   get_raw_obj_data, add_func):
        """
        Find a primary object of class_type in the database from the passed
        handle.

        If no object exists, a new object is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        obj = class_type()
        handle = str(handle)
        new = True
        raw = get_raw_obj_data(handle)
        if raw is not None:
            obj.unserialize(raw)
            #references create object with id None before object is really made
            if obj.gramps_id is not None:
                new = False
        else:
            obj.set_handle(handle)
            add_func(obj, transaction)
        return obj, new

    def __find_table_from_handle(self, handle, transaction, class_type,
                                 get_raw_obj_data, add_func):
        """
        Find a table object of class_type in the database from the passed
        handle.

        If no object exists, a new object is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        obj = class_type()
        handle = str(handle)
        raw = get_raw_obj_data(handle)
        if raw is not None:
            obj.unserialize(raw)
            return obj, False
        else:
            obj.set_handle(handle)
            add_func(obj, transaction)
            return obj, True

    def __check_primary_from_handle(self, handle, transaction, class_type,
                                    has_handle_func, add_func, set_gid):
        """
        Check whether a primary object of class_type with the passed handle
        exists in the database.

        If no such object exists, a new object is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        handle = str(handle)
        if not has_handle_func(handle):
            obj = class_type()
            obj.set_handle(handle)
            add_func(obj, transaction, set_gid=set_gid)

    def __check_table_from_handle(self, handle, transaction, class_type,
                                  has_handle_func, add_func):
        """
        Check whether a table object of class_type with the passed handle exists
        in the database.

        If no such object exists, a new object is added to the database.
        """
        handle = str(handle)
        if not has_handle_func(handle):
            obj = class_type()
            obj.set_handle(handle)
            add_func(obj, transaction)

    def find_person_from_handle(self, handle, transaction):
        """
        Find a Person in the database from the passed handle.

        If no such Person exists, a new Person is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Person,
                                     self.get_raw_person_data, self.add_person)

    def find_source_from_handle(self, handle, transaction):
        """
        Find a Source in the database from the passed handle.

        If no such Source exists, a new Source is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Source,
                                     self.get_raw_source_data, self.add_source)

    def find_event_from_handle(self, handle, transaction):
        """
        Find a Event in the database from the passed handle.

        If no such Event exists, a new Event is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Event,
                                     self.get_raw_event_data, self.add_event)

    def find_object_from_handle(self, handle, transaction):
        """
        Find a Media in the database from the passed handle.

        If no such Media exists, a new Object is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Media,
                                     self.get_raw_object_data, self.add_object)

    def find_place_from_handle(self, handle, transaction):
        """
        Find a Place in the database from the passed handle.

        If no such Place exists, a new Place is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Place,
                                     self.get_raw_place_data, self.add_place)

    def find_family_from_handle(self, handle, transaction):
        """
        Find a Family in the database from the passed handle.

        If no such Family exists, a new Family is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Family,
                                     self.get_raw_family_data, self.add_family)

    def find_repository_from_handle(self, handle, transaction):
        """
        Find a Repository in the database from the passed handle.

        If no such Repository exists, a new Repository is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Repository,
                              self.get_raw_repository_data, self.add_repository)

    def find_note_from_handle(self, handle, transaction):
        """
        Find a Note in the database from the passed handle.

        If no such Note exists, a new Note is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_primary_from_handle(handle, transaction, Note,
                                     self.get_raw_note_data, self.add_note)

    def find_tag_from_handle(self, handle, transaction):
        """
        Find a Tag in the database from the passed handle.

        If no such Tag exists, a new Tag is added to the database.

        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.__find_table_from_handle(handle, transaction, Tag,
                                     self.get_raw_tag_data, self.add_tag)

    def check_person_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Person with the passed handle exists in the database.

        If no such Person exists, a new Person is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Person,
                                 self.has_person_handle, self.add_person,
                                 set_gid = set_gid)

    def check_source_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Source with the passed handle exists in the database.

        If no such Source exists, a new Source is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Source,
                                 self.has_source_handle, self.add_source,
                                 set_gid=set_gid)

    def check_event_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether an Event with the passed handle exists in the database.

        If no such Event exists, a new Event is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Event,
                                 self.has_event_handle, self.add_event,
                                 set_gid=set_gid)

    def check_object_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Media with the passed handle exists in the
        database.

        If no such Media exists, a new Object is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """

        self.__check_primary_from_handle(handle, transaction, Media,
                                 self.has_object_handle, self.add_object,
                                 set_gid=set_gid)

    def check_place_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Place with the passed handle exists in the database.

        If no such Place exists, a new Place is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Place,
                                 self.has_place_handle, self.add_place,
                                 set_gid=set_gid)

    def check_family_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Family with the passed handle exists in the database.

        If no such Family exists, a new Family is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Family,
                                 self.has_family_handle, self.add_family,
                                 set_gid=set_gid)

    def check_repository_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Repository with the passed handle exists in the
        database.

        If no such Repository exists, a new Repository is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Repository,
                               self.has_repository_handle, self.add_repository,
                               set_gid=set_gid)

    def check_note_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Note with the passed handle exists in the database.

        If no such Note exists, a new Note is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_primary_from_handle(handle, transaction, Note,
                                 self.has_note_handle, self.add_note,
                                 set_gid=set_gid)

    def check_tag_from_handle(self, handle, transaction):
        """
        Check whether a Tag with the passed handle exists in the database.

        If no such Tag exists, a new Tag is added to the database.
        """
        self.__check_table_from_handle(handle, transaction, Tag,
                                 self.has_tag_handle, self.add_tag)
