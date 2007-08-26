#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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
Proxy class for the GRAMPS databases. Filter out all living people.
"""

__author__ = "Brian Matherly"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from _ProxyDbBase import ProxyDbBase
from RelLib import *
from Utils import probably_alive

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
    MODE_EXCLUDE  = 0
    MODE_RESTRICT = 1

    def __init__(self,db,mode,current_year=None,years_after_death=0):
        """
        Creates a new LivingProxyDb instance.
        
        @param db: The database to be a proxy for
        @type db: DbBase
        @param mode: The method for handling living people. 
         LivingProxyDb.MODE_EXCLUDE will remove living people altogether. 
         LivingProxyDb.MODE_RESTRICT will remove all information and change their
         given name to "Living". 
        @type mode: int
        @param current_year: The current year to use for living determination.
         If None is supplied, the current year will be found from the system.
        @type current_year: int or None
        @param years_after_death: The number of years after a person's death to 
        still consider them living.
        @type years_after_death: int
        """
        self.db = db
        self.mode = mode
        self.current_year = current_year
        self.years_after_death = years_after_death

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_handle(handle)
        if person and self.__is_living(person):
            if self.mode == self.MODE_EXCLUDE:
                person = None
            elif self.mode == self.MODE_RESTRICT:
                person = _restrict_person(person)
        return person

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps ID.
        If no such Source exists, None is returned.
        """
        return self.db.get_source_from_handle(handle)

    def get_object_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps ID.
        If no such Object exists, None is returned.
        """
        return self.db.get_object_from_handle(handle)

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps ID.
        If no such Place exists, None is returned.
        """
        return self.db.get_place_from_handle(handle)

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps ID.
        If no such Event exists, None is returned.
        """
        return self.db.get_event_from_handle(handle)

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed handle.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_handle(handle)
        family = self.__remove_living_from_family(family)
        return family

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self.db.get_repository_from_handle(handle)

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.db.get_note_from_handle(handle)

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        if self.__is_living(person):
            if self.mode == self.MODE_EXCLUDE:
                return None
            else:
                return _restrict_person(person)
        else:
            return person

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        family = self.__remove_living_from_family(family)
        return family

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        return self.db.get_event_from_gramps_id(val)

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self.db.get_place_from_gramps_id(val)

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self.db.get_source_from_gramps_id(val)

    def get_object_from_gramps_id(self, val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        return self.db.get_object_from_gramps_id(val)

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self.db.get_repository_from_gramps_id(val)

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.db.get_note_from_gramps_id(val)

    def get_person_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        handles = []
        if self.mode == self.MODE_EXCLUDE:
            for handle in self.db.get_person_handles(sort_handles):
                person = self.db.get_person_from_handle(handle)
                if not self.__is_living(person):
                    handles.append(handle)
        elif self.mode == self.MODE_RESTRICT:
            handles = self.db.get_person_handles(sort_handles)
        return handles

    def get_place_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Place in
        the database. If sort_handles is True, the list is sorted by
        Place title.
        """
        return self.db.get_place_handles(sort_handles)

    def get_source_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Source in
        the database. If sort_handles is True, the list is sorted by
        Source title.
        """
        return self.db.get_source_handles(sort_handles)

    def get_media_object_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each MediaObject in
        the database. If sort_handles is True, the list is sorted by title.
        """
        return self.db.get_media_object_handles(sort_handles)

    def get_event_handles(self):
        """
        Returns a list of database handles, one handle for each Event in
        the database. 
        """
        return self.db.get_event_handles()

    def get_family_handles(self):
        """
        Returns a list of database handles, one handle for each Family in
        the database.
        """
        return self.db.get_family_handles()

    def get_repository_handles(self):
        """
        Returns a list of database handles, one handle for each Repository in
        the database.
        """
        return self.db.get_repository_handles()

    def get_note_handles(self):
        """
        Returns a list of database handles, one handle for each Note in
        the database.
        """
        return self.db.get_note_handles()

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.db.get_researcher()

    def get_default_person(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        return self.get_person_from_handle(person_handle)

    def get_default_handle(self):
        """returns the default Person of the database"""
        person_handle = self.db.get_default_handle()
        if self.get_person_from_handle(person_handle):
            return person_handle
        return None

    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        if self.get_person_from_handle(handle):
            return True
        return False

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        return self.db.has_event_handle(handle)

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        return self.db.has_source_handle(handle)

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        return self.db.has_place_handle(handle)

    def has_family_handle(self, handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return self.db.has_family_handle(handle)

    def has_object_handle(self, handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        return self.db.has_object_handle(handle)

    def has_repository_handle(self, handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.db.has_repository_handle(handle)

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return self.db.has_note_handle(handle)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an interator over alist of (class_name, handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names
        
        This default implementation does a sequencial scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

        >    result_list = [i for i in find_backlink_handles(handle)]
        """
        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for (class_name, handle) in handle_itr:
            if class_name == 'Person':
                if not self.get_person_from_handle(handle):
                    continue
            yield (class_name,handle)
        return
    
    def __is_living(self,person):
        return probably_alive( person,
                               self.db,
                               self.current_year,
                               self.years_after_death )
    
    def __remove_living_from_family(self,family):
        parent_is_living = False
        
        father_handle = family.get_father_handle()
        if father_handle:
            father = self.db.get_person_from_handle(father_handle)
            if  self.__is_living(father):
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE:
                    family.set_father_handle(None)
    
        mother_handle = family.get_mother_handle()
        if mother_handle:
            mother = self.db.get_person_from_handle(mother_handle)
            if self.__is_living(mother):
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE:
                    family.set_mother_handle(None)
                    
        if parent_is_living:
            # Clear all events for families where a parent is living.
            family.set_event_ref_list([])
            
        if self.mode == self.MODE_EXCLUDE:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                child = self.db.get_person_from_handle(child_handle)
                if self.__is_living(child):
                    family.remove_child_ref(child_ref)
        
        return family

def _restrict_person(person):
    new_person = Person()
    new_name = Name()
    old_name = person.get_primary_name()
    
    new_name.set_group_as(old_name.get_group_as())
    new_name.set_sort_as(old_name.get_sort_as())
    new_name.set_display_as(old_name.get_display_as())
    new_name.set_surname_prefix(old_name.get_surname_prefix())
    new_name.set_type(old_name.get_type())
    new_name.set_first_name(_(u'Living'))
    new_name.set_patronymic(old_name.get_patronymic())
    new_name.set_surname(old_name.get_surname())
    new_name.set_privacy(old_name.get_privacy())

    new_person.set_primary_name(new_name)
    new_person.set_privacy(person.get_privacy())
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    new_person.set_family_handle_list(person.get_family_handle_list())
    new_person.set_parent_family_handle_list( 
                                        person.get_parent_family_handle_list() )

    return new_person


