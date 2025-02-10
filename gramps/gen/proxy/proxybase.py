#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2025       Doug Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the Liceonse, or
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
Proxy class for a Gramps database.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import types
import functools
import locale

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from ..lib.json_utils import object_to_data
from ..const import GRAMPS_LOCALE as glocale
from ..db.bookmarks import DbBookmarks
from ..db import Database
from ..errors import HandleError


class ProxyDbBase:
    def __init__(self, db: Database):
        """
        Create a new ProxyDb instance.
        """
        self.db = db  # The db on the next lower layer
        self.proxy_map = {}
        self.proxy_map["Person"] = self.get_person_map()
        self.proxy_map["Family"] = self.get_family_map()
        self.proxy_map["Event"] = self.get_event_map()
        self.proxy_map["Place"] = self.get_place_map()
        self.proxy_map["Repository"] = self.get_repository_map()
        self.proxy_map["Media"] = self.get_media_map()
        self.proxy_map["Citation"] = self.get_citation_map()
        self.proxy_map["Note"] = self.get_note_map()

        self.bookmarks = DbBookmarks(
            self.filter_person_handles(self.db.bookmarks.get())
        )

    def __getattr__(self, name):
        return getattr(self.db, name)

    def locale_sort(self, class_name, collation):
        old_locale = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, collation)
            return sorted(
                self.proxy_map[class_name],
                key=lambda item: locale.strxfrm(
                    self.proxy_map[class_name][item]["surname"]
                ),
            )
        except locale.Error:
            # TODO: LOG.warning()
            return list(self.proxy_map[class_name].keys())
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)

    # Get maps:

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for handle, data in self.db._iter_raw_person_data():
            map[handle] = {
                "surname": (
                    data.primary_name.surname_list[0].surname
                    if data.primary_name.surname_list
                    else ""
                )
            }
        return map

    def get_family_map(self):
        map = {}
        for handle in self.db.iter_family_handles():
            map[handle] = {"surname": "TODO"}
        return map

    def get_event_map(self):
        map = {}
        for handle in self.db.iter_event_handles():
            map[handle] = {}
        return map

    def get_place_map(self):
        map = {}
        for handle in self.db.iter_place_handles():
            map[handle] = {}
        return map

    def get_repository_map(self):
        map = {}
        for handle in self.db.iter_repository_handles():
            map[handle] = {}
        return map

    def get_media_map(self):
        map = {}
        for handle in self.db.iter_media_handles():
            map[handle] = {}
        return map

    def get_citation_map(self):
        map = {}
        for handle in self.db.iter_citation_handles():
            map[handle] = {}
        return map

    def get_note_map(self):
        map = {}
        for handle in self.db.iter_note_handles():
            map[handle] = {}
        return map

    # Proxy process:

    def proxy_process_person(self, person):
        return person

    def proxy_process_family(self, family):
        return family

    def proxy_process_event(self, event):
        return event

    def proxy_process_place(self, place):
        return place

    def proxy_process_repository(self, repository):
        return repository

    def proxy_process_media(self, media):
        return media

    def proxy_process_citation(self, citation):
        return citation

    def proxy_process_note(self, note):
        return note

    # Filter handles:

    def filter_person_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Person"]]

    def filter_family_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Family"]]

    def filter_event_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Event"]]

    def filter_place_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Place"]]

    def filter_repository_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Repository"]]

    def filter_media_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Media"]]

    def filter_citation_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Citation"]]

    def filter_note_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Note"]]

    # Iter raw data:

    def _iter_raw_person_data(self):
        for handle in self.proxy_map["Person"]:
            # Currently the proxies use Gramps Objects for processing:
            person = self.get_person_from_handle(handle)
            yield handle, object_to_data(person)

    # Get numbers:

    def get_number_of_people(self):
        return len(self.proxy_map["Person"])

    def get_number_of_families(self):
        return len(self.proxy_map["Family"])

    # Get from handles:

    @functools.cache
    def get_person_from_handle(self, handle):
        if handle in self.proxy_map["Person"]:
            person = self.db.get_person_from_handle(handle)
            processed = self.proxy_process_person(person)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_family_from_handle(self, handle):
        if handle in self.proxy_map["Family"]:
            family = self.db.get_family_from_handle(handle)
            processed = self.proxy_process_family(family)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    # Get raw data:

    @functools.cache
    def get_raw_person_data(self, handle):
        if handle in self.proxy_map["Person"]:
            person = self.db.get_person_from_handle(handle)
            processed = self.proxy_process_person(person)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    # Get from gramps id:

    @functools.cache
    def get_person_from_gramps_id(self, gramps_id):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(gramps_id)
        if person and person.handle in self.proxy_map["Person"]:
            processed = self.proxy_process_person(person)
            return processed
        else:
            return None

    # Get all handles:

    def get_person_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Person", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Person"]:
                yield handle

    # Iter objects:

    def iter_people(self):
        for handle in self.proxy_map["Person"]:
            yield self.get_person_from_handle(handle)

    # Iter handles:

    def iter_person_handles(self):
        for handle in self.proxy_map["Person"]:
            yield handle

    def iter_family_handles(self):
        for handle in self.proxy_map["Family"]:
            yield handle

    # Misc:

    def find_backlink_handles(self, handle, include_classes=None):
        for class_name, obj_handle in self.db.find_backlink_handles(
            handle, include_classes
        ):
            if obj_handle in self.proxy_map[class_name]:
                yield (class_name, obj_handle)
