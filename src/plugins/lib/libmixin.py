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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Mixin for DbDir to enable find_from_handle and check_from_handle methods.
"""

#------------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------------
from gen.lib import (GenderStats, Person, Family, Event, Place, Source, 
                     MediaObject, Repository, Note)

#------------------------------------------------------------------------------
#
# DbMixin class
#
#------------------------------------------------------------------------------
class DbMixin(object):
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
    def find_from_handle(self, handle, transaction, class_type, dmap,
                          add_func):
        """
        Find a object of class_type in the database from the passed handle.
        
        If no object exists, a new object is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        obj = class_type()
        handle = str(handle)
        new = True
        if handle in dmap:
            obj.unserialize(dmap.get(handle))
            #references create object with id None before object is really made
            if obj.gramps_id is not None:
                new = False
        else:
            obj.set_handle(handle)
            add_func(obj, transaction)
        return obj, new

    def __check_from_handle(self, handle, transaction, class_type, dmap,
                            add_func, set_gid=True):
        handle = str(handle)
        if handle not in dmap:
            obj = class_type()
            obj.set_handle(handle)
            add_func(obj, transaction, set_gid=set_gid)

    def find_person_from_handle(self, handle, transaction):
        """
        Find a Person in the database from the passed handle.
        
        If no such Person exists, a new Person is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Person, 
                                     self.person_map, self.add_person)

    def find_source_from_handle(self, handle, transaction):
        """
        Find a Source in the database from the passed handle.
        
        If no such Source exists, a new Source is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Source, 
                                     self.source_map, self.add_source)

    def find_event_from_handle(self, handle, transaction):
        """
        Find a Event in the database from the passed handle.
        
        If no such Event exists, a new Event is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Event, 
                                     self.event_map, self.add_event)

    def find_object_from_handle(self, handle, transaction):
        """
        Find a MediaObject in the database from the passed handle.
        
        If no such MediaObject exists, a new Object is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, MediaObject, 
                                     self.media_map, self.add_object)

    def find_place_from_handle(self, handle, transaction):
        """
        Find a Place in the database from the passed handle.
        
        If no such Place exists, a new Place is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Place, 
                                     self.place_map, self.add_place)

    def find_family_from_handle(self, handle, transaction):
        """
        Find a Family in the database from the passed handle.
        
        If no such Family exists, a new Family is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Family, 
                                     self.family_map, self.add_family)

    def find_repository_from_handle(self, handle, transaction):
        """
        Find a Repository in the database from the passed handle.
        
        If no such Repository exists, a new Repository is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Repository, 
                                     self.repository_map, self.add_repository)

    def find_note_from_handle(self, handle, transaction):
        """
        Find a Note in the database from the passed handle.
        
        If no such Note exists, a new Note is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        return self.find_from_handle(handle, transaction, Note, 
                                     self.note_map, self.add_note)

    def check_person_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Person with the passed handle exists in the database.
        
        If no such Person exists, a new Person is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Person, 
                                 self.person_map, self.add_person, 
                                 set_gid = set_gid)

    def check_source_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Source with the passed handle exists in the database.
        
        If no such Source exists, a new Source is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Source, 
                                 self.source_map, self.add_source, 
                                 set_gid=set_gid)
                                
    def check_event_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether an Event with the passed handle exists in the database.
        
        If no such Event exists, a new Event is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Event, 
                                 self.event_map, self.add_event, 
                                 set_gid=set_gid)

    def check_object_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a MediaObject with the passed handle exists in the 
        database. 
        
        If no such MediaObject exists, a new Object is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """

        self.__check_from_handle(handle, transaction, MediaObject, 
                                 self.media_map, self.add_object, 
                                 set_gid=set_gid)

    def check_place_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Place with the passed handle exists in the database.
        
        If no such Place exists, a new Place is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Place, 
                                 self.place_map, self.add_place, 
                                 set_gid=set_gid)

    def check_family_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Family with the passed handle exists in the database.
        
        If no such Family exists, a new Family is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Family, 
                                 self.family_map, self.add_family, 
                                 set_gid=set_gid)

    def check_repository_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Repository with the passed handle exists in the
        database. 
        
        If no such Repository exists, a new Repository is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Repository, 
                                 self.repository_map, self.add_repository, 
                                 set_gid=set_gid)

    def check_note_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Note with the passed handle exists in the database. 
        
        If no such Note exists, a new Note is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        self.__check_from_handle(handle, transaction, Note, 
                                 self.note_map, self.add_note, 
                                 set_gid=set_gid)
