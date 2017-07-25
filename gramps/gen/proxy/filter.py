#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008       Brian G. Matherly
# Copyright (C) 2008            Gary Burton
# Copyright (C) 2008            Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2011       Tim G L Lyons
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
Proxy class for the Gramps databases. Apply filter
"""

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from .proxybase import ProxyDbBase
from ..lib import (Date, Person, Name, Surname, NameOriginType, Family, Source,
                   Citation, Event, Media, Place, Repository, Note, Tag)
from ..const import GRAMPS_LOCALE as glocale

class FilterProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data that does not match the provided filters will be hidden from
    the user.
    """

    def __init__(self, db, person_filter=None, event_filter=None,
                 note_filter=None, user=None):
        """
        Create a new FilterProxyDb instance.
        """
        ProxyDbBase.__init__(self, db)
        self.person_filter = person_filter
        if person_filter:
            self.plist = set(person_filter.apply(
                    self.db, self.db.iter_person_handles(), user=user))
        else:
            self.plist = set(self.db.iter_person_handles())

        if event_filter:
            self.elist = set(event_filter.apply(
                    self.db, self.db.iter_event_handles(), user=user))
        else:
            self.elist = set(self.db.iter_event_handles())

        if note_filter:
            self.nlist = set(note_filter.apply(
                    self.db, self.db.iter_note_handles(), user=user))
        else:
            self.nlist = set(self.db.iter_note_handles())

        self.flist = set()
        for handle in self.plist:
            person = self.db.get_person_from_handle(handle)
            if person:
                self.flist.update(person.get_family_handle_list())
                self.flist.update(person.get_parent_family_handle_list())

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        if handle in self.plist:
            person = self.db.get_person_from_handle(handle)
            if person is None:
                return None
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
        Finds a Source in the database from the passed Gramps ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_handle(handle)

        if source:
            # Filter notes out
            self.sanitize_notebase(source)

            media_ref_list = source.get_media_list()
            for media_ref in media_ref_list:
                self.sanitize_notebase(media_ref)
                attributes = media_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

            repo_ref_list = source.get_reporef_list()
            for repo_ref in repo_ref_list:
                self.sanitize_notebase(repo_ref)

        return source

    def get_citation_from_handle(self, handle):
        """
        Finds a Citation in the database from the passed Gramps ID.
        If no such Citation exists, None is returned.
        """
        citation = self.db.get_citation_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(citation)
        return citation

    def get_media_from_handle(self, handle):
        """
        Finds a Media in the database from the passed Gramps handle.
        If no such Object exists, None is returned.
        """
        media = self.db.get_media_from_handle(handle)

        if media:
            # Filter notes out
            self.sanitize_notebase(media)

            attributes = media.get_attribute_list()
            for attr in attributes:
                self.sanitize_notebase(attr)

        return media

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed Gramps handle.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_handle(handle)

        if place:
            # Filter notes out
            self.sanitize_notebase(place)

            media_ref_list = place.get_media_list()
            for media_ref in media_ref_list:
                self.sanitize_notebase(media_ref)
                attributes = media_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

        return place

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        if handle in self.elist:
            event = self.db.get_event_from_handle(handle)
            # Filter all notes out
            self.sanitize_notebase(event)
            return event
        else:
            return None

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        if handle in self.flist:
            family = self.db.get_family_from_handle(handle)
            if family is None:
                return None
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
            for cref in clist:
                self.sanitize_notebase(cref)

            self.sanitize_notebase(family)

            attributes = family.get_attribute_list()
            for attr in attributes:
                self.sanitize_notebase(attr)

            event_ref_list = family.get_event_ref_list()
            for event_ref in event_ref_list:
                self.sanitize_notebase(event_ref)
                attributes = event_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

            media_ref_list = family.get_media_list()
            for media_ref in media_ref_list:
                self.sanitize_notebase(media_ref)
                attributes = media_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

            lds_ord_list = family.get_lds_ord_list()
            for lds_ord in lds_ord_list:
                self.sanitize_notebase(lds_ord)

            return family
        else:
            return None

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed Gramps ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_handle(handle)
        # Filter notes out
        self.sanitize_notebase(repository)
        self.sanitize_addressbase(repository)
        return repository

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed Gramps ID.
        If no such Note exists, None is returned.
        """
        if handle in self.nlist:
            return self.db.get_note_from_handle(handle)
        else:
            return None

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        if person:
            return self.get_person_from_handle(person.get_handle())
        else:
            return None

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        if family:
            return self.get_family_from_handle(family.get_handle())
        else:
            return None

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(val)
        if event:
            return self.get_event_from_handle(event.get_handle())
        else:
            return None

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed Gramps ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_gramps_id(val)
        if place:
            return self.get_place_from_handle(place.get_handle())
        else:
            return None

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed Gramps ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_gramps_id(val)
        if source:
            return self.get_source_from_handle(source.get_handle())
        else:
            return None

    def get_citation_from_gramps_id(self, val):
        """
        Finds a Citation in the database from the passed Gramps ID.
        If no such Citation exists, None is returned.
        """
        citation = self.db.get_citation_from_gramps_id(val)
        if citation:
            return self.get_citation_from_handle(citation.get_handle())
        else:
            return None

    def get_media_from_gramps_id(self, val):
        """
        Finds a Media in the database from the passed Gramps ID.
        If no such Media exists, None is returned.
        """
        media = self.db.get_media_from_gramps_id(val)
        if media:
            return self.get_media_from_handle(media.get_handle())
        else:
            return None

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed Gramps ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_gramps_id(val)
        if repository:
            return self.get_repository_from_handle(repository.get_handle())
        else:
            return None

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed Gramps ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_gramps_id(val)
        if note:
            return self.get_note_from_handle(note.get_handle())
        else:
            return None

    def get_person_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        # FIXME: plist is not a sorted list of handles
        return list(self.plist)

    def iter_person_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database.
        """
        return self.plist

    def iter_people(self):
        """
        Return an iterator over objects for Persons in the database
        """
        return map(self.get_person_from_handle, self.plist)

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in
        the database.
        """
        return list(self.elist)

    def iter_event_handles(self):
        """
        Return an iterator over database handles, one handle for each Event in
        the database.
        """
        return self.elist

    def iter_events(self):
        """
        Return an iterator over objects for Events in the database
        """
        return map(self.get_event_from_handle, self.elist)

    def get_family_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        # FIXME: flist is not a sorted list of handles
        return list(self.flist)

    def iter_family_handles(self):
        """
        Return an iterator over database handles, one handle for each Family in
        the database.
        """
        return self.flist

    def iter_families(self):
        """
        Return an iterator over objects for Families in the database
        """
        return map(self.get_family_from_handle, self.flist)

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in
        the database.
        """
        return list(self.nlist)

    def iter_note_handles(self):
        """
        Return an iterator over database handles, one handle for each Note in
        the database.
        """
        return self.nlist

    def iter_notes(self):
        """
        Return an iterator over objects for Notes in the database
        """
        return map(self.get_note_from_handle, self.nlist)

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
        #FIXME: add a filter for returned handles (see private.py as an example)
        return self.db.find_backlink_handles(handle, include_classes)

    def sanitize_notebase(self, notebase):
        """
        Filters notes out of the passed notebase object according to the Note Filter.

        :param notebase: NoteBase object to clean
        :type event: NoteBase
        """
        if notebase:
            note_list = notebase.get_note_list()
            new_note_list = [ note for note in note_list if note in self.nlist ]
            notebase.set_note_list(new_note_list)

    def sanitize_addressbase(self, addressbase):
        if addressbase:
            addresses = addressbase.get_address_list()
            for address in addresses:
                self.sanitize_notebase(address)

    def sanitize_person(self, person):
        """
        Cleans filtered notes out of the passed person

        :param event: Person object to clean
        :type event: Person
        """
        if person:
            # Filter note references
            self.sanitize_notebase(person)
            self.sanitize_addressbase(person)

            name = person.get_primary_name()
            self.sanitize_notebase(name)

            altnames = person.get_alternate_names()
            for name in altnames:
                self.sanitize_notebase(name)

            self.sanitize_addressbase(person)

            attributes = person.get_attribute_list()
            for attr in attributes:
                self.sanitize_notebase(attr)

            event_ref_list = person.get_event_ref_list()
            for event_ref in event_ref_list:
                self.sanitize_notebase(event_ref)
                attributes = event_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

            media_ref_list = person.get_media_list()
            for media_ref in media_ref_list:
                self.sanitize_notebase(media_ref)
                attributes = media_ref.get_attribute_list()
                for attribute in attributes:
                    self.sanitize_notebase(attribute)

            lds_ord_list = person.get_lds_ord_list()
            for lds_ord in lds_ord_list:
                self.sanitize_notebase(lds_ord)

            person_ref_list = person.get_person_ref_list()
            for person_ref in person_ref_list:
                self.sanitize_notebase(person_ref)
