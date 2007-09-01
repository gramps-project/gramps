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

# $Id: _PrivateProxyDb.py 8864 2007-08-25 05:03:23Z dallingham $

"""
Proxy class for the GRAMPS databases. Apply filter
"""

__author__ = "Don Allingham"
__revision__ = "$Revision: 8864 $"

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from RelLib import *
from _ProxyDbBase import ProxyDbBase

class FilterProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

    def __init__(self, db, person_filter=None, event_filter=None):
        """
        Creates a new PrivateProxyDb instance. 
        """
        ProxyDbBase.__init__(self, db)
        self.person_filter = person_filter

        if person_filter:
            self.plist = set(person_filter.apply(
                    self.db, self.db.get_person_handles(sort_handles=False)))
        else:
            self.plist = self.db.get_person_handles(sort_handles=False)

        if event_filter:
            self.elist = set(event_filter.apply(
                    self.db, self.db.get_event_handles()))
        else:
            self.elist = self.db.get_event_handles()

        self.flist = set()
        for handle in list(self.plist):
            person = self.db.get_person_from_handle(handle)
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                self.flist.add(family_handle)

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned.
        """
        if handle in self.plist:
            person = self.db.get_person_from_handle(handle)

            person.set_person_ref_list(
                [ ref for ref in person.get_person_ref_list()
                  if ref.ref in self.plist ])

            person.set_family_handle_list(
                [ hndl for hndl in person.get_family_handle_list()
                  if hndl in self.flist ])

            person.set_parent_family_handle_list(
                [ hndl for hndl in person.get_parent_family_handle_list()
                  if hndl in self.flist ])

            eref_list = person.get_event_ref_list()
            bref = person.get_birth_ref()
            dref = person.get_death_ref()

            new_eref_list = [ ref for ref in eref_list
                              if ref.ref in self.elist]

            person.set_event_ref_list(new_eref_list)
            if bref in new_eref_list:
                person.set_birth_ref(bref)
            if dref in new_eref_list:
                person.set_death_ref(dref)

            return person
        else:
            return None

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self.db.get_source_from_handle(handle)

    def get_object_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned.
        """
        return self.db.get_object_from_handle(handle)

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self.db.get_place_from_handle(handle)

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        if handle in self.elist:
            return self.db.get_event_from_handle(handle)
        else:
            return None

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        if handle in self.flist:
            family = self.db.get_family_from_handle(handle)
        
            eref_list = [ eref for eref in family.get_event_ref_list()
                          if eref.ref in self.elist ]
            family.set_event_ref_list(eref_list)

            if family.get_father_handle() not in self.plist:
                family.set_father_handle(None)
                
            if family.get_mother_handle() not in self.plist:
                family.set_mother_handle(None)

            clist = [ cref for cref in family.get_child_ref_list()
                      if cref.ref in self.plist ]
            family.set_child_ref_list(clist)
            return family
        else:
            return None

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
        if person.get_handle() not in self.plist:
            return None
        else:
            return person

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        return self.db.get_family_from_gramps_id(val)

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(val)
        if event.get_handle() not in self.elist:
            return None
        else:
            return event

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
        return list(self.plist)

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
        return list(self.elist)

    def get_family_handles(self):
        """
        Returns a list of database handles, one handle for each Family in
        the database.
        """
        return list(self.flist)

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
        person = self.db.get_default_person()
        if person and person.get_handle() in self.plist:
            return person
        else:
            return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        handle = self.db.get_default_handle()
        if handle in self.plist:
            return handle
        else:
            return None
    
    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        return handle in self.plist

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        return handle in self.elist

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

