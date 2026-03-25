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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Proxy class for the Gramps databases. Apply filter
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from .proxybase import ProxyDbBase
from ..lib.json_utils import DataDict
from ..const import GRAMPS_LOCALE as glocale


class FilterProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data that does not match the provided filters will be hidden from
    the user.
    """

    def __init__(
        self, db, person_filter=None, event_filter=None, note_filter=None, user=None
    ):
        """
        Create a new FilterProxyDb instance.
        """
        ProxyDbBase.__init__(self, db)
        self.person_filter = person_filter
        if person_filter:
            self.plist = set(
                person_filter.apply(self.db, self.db.iter_person_handles(), user=user)
            )
        else:
            self.plist = set(self.db.iter_person_handles())

        if event_filter:
            self.elist = set(
                event_filter.apply(self.db, self.db.iter_event_handles(), user=user)
            )
        else:
            self.elist = set(self.db.iter_event_handles())

        if note_filter:
            self.nlist = set(
                note_filter.apply(self.db, self.db.iter_note_handles(), user=user)
            )
        else:
            self.nlist = set(self.db.iter_note_handles())

        self.flist = set()
        for handle in self.plist:
            person = self.db.get_person_from_handle(handle)
            if person:
                self.flist.update(person.family_list)
                self.flist.update(person.parent_family_list)

        # Exclude notes whose embedded gramps:// links reference objects that
        # are not included by this proxy.  All other include sets (plist,
        # elist, flist) must be fully built before this step.
        self.nlist = {h for h in self.nlist if self._note_links_included(h)}

    # -----------------------------------------------------------------------
    # include_* predicates — use precomputed handle sets
    # -----------------------------------------------------------------------

    def include_person(self, handle: PersonHandle) -> bool:
        """
        Return True if *handle* is in the precomputed set of visible persons.

        :param handle: database handle of the Person to test
        :type handle: PersonHandle
        :returns: True if the person passed the filter
        :rtype: bool
        """
        return handle in self.plist

    def include_family(self, handle: FamilyHandle) -> bool:
        """
        Return True if *handle* is in the precomputed set of visible families.

        :param handle: database handle of the Family to test
        :type handle: FamilyHandle
        :returns: True if the family is included (derived from filtered persons)
        :rtype: bool
        """
        return handle in self.flist

    def include_event(self, handle: str) -> bool:
        """
        Return True if *handle* is in the precomputed set of visible events.

        :param handle: database handle of the Event to test
        :type handle: str
        :returns: True if the event passed the filter
        :rtype: bool
        """
        return handle in self.elist

    def include_note(self, handle: str) -> bool:
        """
        Return True if *handle* is in the precomputed set of visible notes.

        :param handle: database handle of the Note to test
        :type handle: str
        :returns: True if the note passed the filter and its links are included
        :rtype: bool
        """
        return handle in self.nlist

    # -----------------------------------------------------------------------
    # sanitize_* methods — filter notes from sub-objects on DataDicts.
    # Top-level note_list is already filtered by the base class.
    # These handle nested note_list fields inside sub-objects.
    # -----------------------------------------------------------------------

    def _filter_note_list(self, note_list: list) -> list:
        """
        Return a new list containing only those note handles that are in the
        precomputed visible notes set.

        :param note_list: list of note handles to filter
        :type note_list: list[NoteHandle]
        :returns: filtered list of note handles
        :rtype: list[NoteHandle]
        """
        return [h for h in note_list if h in self.nlist]

    def _sanitize_subnotes(self, items) -> list:
        """
        Filter note_list on each item in a DataList.

        :param items: iterable of DataDict sub-objects to sanitize
        :returns: the items list with each item's note_list filtered in place
        :rtype: list
        """
        for item in items:
            if hasattr(item, "note_list"):
                item["note_list"] = self._filter_note_list(item.note_list)
        return items

    def sanitize_person(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the person DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside attribute_list, address_list,
        event_ref_list, media_list, lds_ord_list, person_ref_list, and
        primary_name sub-objects.

        :param data: raw DataDict for the Person, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.attribute_list)
        self._sanitize_subnotes(data.address_list)
        self._sanitize_subnotes(data.event_ref_list)
        self._sanitize_subnotes(data.media_list)
        self._sanitize_subnotes(data.lds_ord_list)
        self._sanitize_subnotes(data.person_ref_list)
        if hasattr(data.primary_name, "note_list"):
            data.primary_name["note_list"] = self._filter_note_list(
                data.primary_name.note_list
            )
        self._sanitize_subnotes(data.alternate_names)
        return data

    def sanitize_family(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the family DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside attribute_list, event_ref_list,
        media_list, lds_ord_list, and child_ref_list sub-objects.

        :param data: raw DataDict for the Family, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.attribute_list)
        self._sanitize_subnotes(data.event_ref_list)
        self._sanitize_subnotes(data.media_list)
        self._sanitize_subnotes(data.lds_ord_list)
        self._sanitize_subnotes(data.child_ref_list)
        return data

    def sanitize_source(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the source DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside reporef_list and media_list sub-objects.

        :param data: raw DataDict for the Source, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.reporef_list)
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_citation(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the citation DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside media_list sub-objects.

        :param data: raw DataDict for the Citation, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_place(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the place DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside media_list sub-objects.

        :param data: raw DataDict for the Place, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_media(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the media DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside attribute_list sub-objects.

        :param data: raw DataDict for the Media, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.attribute_list)
        return data

    def sanitize_repository(self, data: "DataDict") -> "DataDict":
        """
        Filter note_list on nested sub-objects of the repository DataDict.

        Top-level note_list filtering is handled by the base class; this method
        handles note_list fields inside address_list sub-objects.

        :param data: raw DataDict for the Repository, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        self._sanitize_subnotes(data.address_list)
        return data

    # -----------------------------------------------------------------------
    # Handle list / iterator overrides (using precomputed sets for speed)
    # -----------------------------------------------------------------------

    def get_person_handles(self, sort_handles=False, locale=glocale) -> list:
        """
        Return a list of database handles for all Person objects that passed
        the filter.  The list is not sorted (sort_handles is ignored here).

        :param sort_handles: ignored; the precomputed set is unordered
        :type sort_handles: bool
        :param locale: locale used for sorting (ignored)
        :type locale: GrampsLocale
        :returns: list of person handles
        :rtype: list[str]
        """
        # FIXME: plist is not a sorted list of handles
        return list(self.plist)

    def iter_person_handles(self):
        """
        Return an iterator over handles of Person objects that passed the filter.

        :returns: iterator over person handles
        """
        return self.plist

    def iter_people(self):
        """
        Return an iterator over Person objects that passed the filter.

        :returns: iterator over Person objects
        """
        return map(self.get_person_from_handle, self.plist)

    def get_event_handles(self) -> list:
        """
        Return a list of database handles for all Event objects that passed
        the filter.

        :returns: list of event handles
        :rtype: list[str]
        """
        return list(self.elist)

    def iter_event_handles(self):
        """
        Return an iterator over database handles for all visible Event objects.

        :returns: iterator over event handles
        """
        return self.elist

    def iter_events(self):
        """
        Return an iterator over Event objects that passed the filter.

        :returns: iterator over Event objects
        """
        return map(self.get_event_from_handle, self.elist)

    def get_family_handles(self, sort_handles=False, locale=glocale) -> list:
        """
        Return a list of database handles for all Family objects derived from
        the filtered person set.  The list is not sorted (sort_handles is
        ignored here).

        :param sort_handles: ignored; the precomputed set is unordered
        :type sort_handles: bool
        :param locale: locale used for sorting (ignored)
        :type locale: GrampsLocale
        :returns: list of family handles
        :rtype: list[str]
        """
        # FIXME: flist is not a sorted list of handles
        return list(self.flist)

    def iter_family_handles(self):
        """
        Return an iterator over database handles for all visible Family objects.

        :returns: iterator over family handles
        """
        return self.flist

    def iter_families(self):
        """
        Return an iterator over Family objects derived from the filtered person
        set.

        :returns: iterator over Family objects
        """
        return map(self.get_family_from_handle, self.flist)

    def get_note_handles(self) -> list:
        """
        Return a list of database handles for all Note objects that passed
        the filter.

        :returns: list of note handles
        :rtype: list[str]
        """
        return list(self.nlist)

    def iter_note_handles(self):
        """
        Return an iterator over database handles for all visible Note objects.

        :returns: iterator over note handles
        """
        return self.nlist

    def iter_notes(self):
        """
        Return an iterator over Note objects that passed the filter.

        :returns: iterator over Note objects
        """
        return map(self.get_note_from_handle, self.nlist)

    def get_default_person(self):
        """returns the default Person of the database"""
        person = self.db.get_default_person()
        if person and person.handle in self.plist:
            return person
        return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        handle = self.db.get_default_handle()
        if handle in self.plist:
            return handle
        return None

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an iterator over a list of (class_name, handle) tuples.
        """
        # FIXME: add a filter for returned handles
        return self.db.find_backlink_handles(handle, include_classes)
