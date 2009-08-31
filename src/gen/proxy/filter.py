#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008       Brian G. Matherly
# Copyright (C) 2008            Gary Burton
# Copyright (C) 2008            Robert Cheramy <robert@cheramy.net>
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
Proxy class for the GRAMPS databases. Apply filter
"""

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
#from gen.lib import *
from proxybase import ProxyDbBase

class FilterProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data that does not match the provided filters will be hidden from
    the user.
    """

    def __init__(self, db, person_filter=None, event_filter=None, 
                 note_filter=None):
        """
        Create a new PrivateProxyDb instance. 
        """
        ProxyDbBase.__init__(self, db)
        self.person_filter = person_filter

        if person_filter:
            #self.plist = set(person_filter.apply(
            #        self.db, self.db.iter_person_handles()))
            self.plist = dict((h, 1) for h in person_filter.apply(
                    self.db, self.db.iter_person_handles()))
        else:
            #self.plist = self.db.get_person_handles()
            self.plist = dict((h, 1) for h in self.db.iter_person_handles())

        if event_filter:
            #self.elist = set(event_filter.apply(
            #        self.db, self.db.iter_event_handles()))
            self.elist = dict((h, 1) for h in event_filter.apply(
                    self.db, self.db.iter_event_handles()))
        else:
            #self.elist = self.db.get_event_handles()
            self.elist = dict((h, 1) for h in self.db.iter_event_handles())
        
        if note_filter:
            #self.nlist = set(note_filter.apply(
            #        self.db, self.db.iter_note_handles()))
            self.nlist = dict((h, 1) for h in note_filter.apply(
                    self.db, self.db.iter_note_handles()))
        else:
            self.nlist = dict((h, 1) for h in self.db.iter_note_handles())

        self.flist = {}
        for handle in list(self.plist):
            person = self.db.get_person_from_handle(handle)
            for handle in person.get_family_handle_list():
                self.flist[handle] = 1

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
            
            # Filter notes out
            self.sanitize_person(person)
            
            return person
        else:
            return None

    def include_person(self, handle):
        return handle in self.plist               

    def include_family(self, handle):
        return handle in self.flist               

    def include_event(self, handle):
        return handle in self.elist               

    def include_note(self, handle):
        return handle in self.nlist               

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(source)
        return source

    def get_object_from_handle(self, handle):
        """
        Finds a MediaObject in the database from the passed GRAMPS' handle.
        If no such Object exists, None is returned.
        """
        media = self.db.get_object_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(media)
        self.sanitize_sourcebase(media)
        return media

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed GRAMPS' handle.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(place)
        self.sanitize_sourcebase(place)
        return place

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        if handle in self.elist:
            event = self.db.get_event_from_handle(handle)
            # Filter all notes out
            self.sanitize_notebase(event)
            self.sanitize_sourcebase(event)
            return event
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
            
            # Filter notes out
            self.sanitize_notebase(family)
            self.sanitize_sourcebase(family)
            return family
        else:
            return None

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(repository)
        self.sanitize_addressbase(repository)
        return repository

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        if handle in self.nlist:
            return self.db.get_note_from_handle(handle)
        else:
            return None

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        return self.get_person_from_handle(person.get_handle())

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        return self.get_family_from_handle(family.get_handle())

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(val)
        return self.get_event_from_handle(event.get_handle())

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_gramps_id(val)
        return self.get_place_from_handle(place.get_handle())

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_gramps_id(val)
        return self.get_source_from_handle(source.get_handle())

    def get_object_from_gramps_id(self, val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        media = self.db.get_object_from_gramps_id(val)
        return self.get_object_from_handle(media.get_handle())

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_gramps_id(val)
        return self.get_repository_from_handle(repository.get_handle())

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_gramps_id(val)
        return self.get_note_from_handle(note.get_handle())

    def get_person_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        # FIXME: plist is not a sorted list of handles
        return list(self.plist)

    def iter_person_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database. 
        """
        # FIXME: plist is not a sorted list of handles
        return self.plist

    def iter_people(self):
        """
        Return an iterator over handles and objects for Persons in the database
        """
        for handle in self.plist:
            yield handle, self.get_person_from_handle(handle)

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in
        the database. 
        """
        return list(self.elist)
        
    def iter_event_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database. 
        """
        return self.elist        

    def get_family_handles(self):
        """
        Return a list of database handles, one handle for each Family in
        the database.
        """
        return list(self.flist)
        
    def iter_family_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database. 
        """
        return self.flist

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in
        the database.
        """
        return list(self.nlist)

    def iter_note_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database. 
        """
        return self.nlist

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

    def has_family_handle(self, handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return handle in self.flist

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return handle in self.nlist

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an iterator over a list of (class_name, handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names
        
        This default implementation does a sequential scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

        >    result_list = list(find_backlink_handles(handle))
        """
        #FIXME: add a filter for returned handles (see private.py as an example)
        return self.db.find_backlink_handles(handle, include_classes)
    
    def sanitize_notebase(self, notebase):
        """
        Filters notes out of the passed notebase object according to the Note Filter.
        @param notebase: NoteBase object to clean
        @type event: NoteBase
        """
        note_list = notebase.get_note_list()
        new_note_list = [ note for note in note_list if note in self.nlist ]
        notebase.set_note_list(new_note_list)
     
    def sanitize_sourcebase(self, sourcebase):
        """
        Filter notes out of an SourceBase object
        @param event: SourceBase object to clean
        @type event: SourceBase
        """
        sources = sourcebase.get_source_references()
        for source in sources:
            self.sanitize_notebase(source)
            
    def sanitize_addressbase(self, addressbase):
        addresses = addressbase.get_address_list()
        for address in addresses:
            self.sanitize_notebase(address)
            self.sanitize_sourcebase(address)
       
    def sanitize_person(self, person):
        """
        Cleans filtered notes out of the passed person
        @param event: Person object to clean
        @type event: Person
        """
        # Filter note references
        self.sanitize_notebase(person)
        self.sanitize_sourcebase(person)
        self.sanitize_addressbase(person)
        
        name = person.get_primary_name()
        self.sanitize_notebase(name)
        self.sanitize_sourcebase(name)
        
        altnames = person.get_alternate_names()
        for name in altnames:
            self.sanitize_notebase(name)
            self.sanitize_sourcebase(name)
        
        self.sanitize_addressbase(person)
