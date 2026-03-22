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

    # -----------------------------------------------------------------------
    # include_* predicates — use precomputed handle sets
    # -----------------------------------------------------------------------

    def include_person(self, handle):
        return handle in self.plist

    def include_family(self, handle):
        return handle in self.flist

    def include_event(self, handle):
        return handle in self.elist

    def include_note(self, handle):
        return handle in self.nlist

    # -----------------------------------------------------------------------
    # sanitize_* methods — filter notes from sub-objects on DataDicts.
    # Top-level note_list is already filtered by the base class.
    # These handle nested note_list fields inside sub-objects.
    # -----------------------------------------------------------------------

    def _filter_note_list(self, note_list):
        return [h for h in note_list if h in self.nlist]

    def _sanitize_subnotes(self, items):
        """Filter note_list on each item in a DataList."""
        for item in items:
            if hasattr(item, "note_list"):
                item["note_list"] = self._filter_note_list(item.note_list)
        return items

    def sanitize_person(self, data):
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

    def sanitize_family(self, data):
        self._sanitize_subnotes(data.attribute_list)
        self._sanitize_subnotes(data.event_ref_list)
        self._sanitize_subnotes(data.media_list)
        self._sanitize_subnotes(data.lds_ord_list)
        self._sanitize_subnotes(data.child_ref_list)
        return data

    def sanitize_source(self, data):
        self._sanitize_subnotes(data.reporef_list)
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_citation(self, data):
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_place(self, data):
        self._sanitize_subnotes(data.media_list)
        return data

    def sanitize_media(self, data):
        self._sanitize_subnotes(data.attribute_list)
        return data

    def sanitize_repository(self, data):
        self._sanitize_subnotes(data.address_list)
        return data

    # -----------------------------------------------------------------------
    # Handle list / iterator overrides (using precomputed sets for speed)
    # -----------------------------------------------------------------------

    def get_person_handles(self, sort_handles=False, locale=glocale):
        # FIXME: plist is not a sorted list of handles
        return list(self.plist)

    def iter_person_handles(self):
        return self.plist

    def iter_people(self):
        return map(self.get_person_from_handle, self.plist)

    def get_event_handles(self):
        return list(self.elist)

    def iter_event_handles(self):
        return self.elist

    def iter_events(self):
        return map(self.get_event_from_handle, self.elist)

    def get_family_handles(self, sort_handles=False, locale=glocale):
        # FIXME: flist is not a sorted list of handles
        return list(self.flist)

    def iter_family_handles(self):
        return self.flist

    def iter_families(self):
        return map(self.get_family_from_handle, self.flist)

    def get_note_handles(self):
        return list(self.nlist)

    def iter_note_handles(self):
        return self.nlist

    def iter_notes(self):
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
