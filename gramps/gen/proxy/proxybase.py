#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2025       Doug Blank <doug.blank@gmail.com>
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
from ..const import GRAMPS_LOCALE as glocale
from ..db import Database
from ..db.bookmarks import DbBookmarks
from ..errors import HandleError
from ..lib.json_utils import object_to_data


class ProxyCursor:
    """
    A cursor for moving through proxied data.
    """

    def __init__(self, get_raw, get_handles):
        self.get_raw = get_raw
        self.get_handles = get_handles

    def __enter__(self):
        """
        Context manager enter method
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        for handle in self.get_handles():
            yield handle, self.get_raw(handle)


class ProxyDbBase:
    def __init__(self, db: Database):
        """
        Create a new ProxyDb instance.
        """
        self.db = db  # The db on the next lower layer
        self.basedb = db.basedb  # the basedb
        self.proxy_map = {}
        self.proxy_map["Person"] = self.get_person_map()
        self.proxy_map["Family"] = self.get_family_map()
        self.proxy_map["Event"] = self.get_event_map()
        self.proxy_map["Place"] = self.get_place_map()
        self.proxy_map["Repository"] = self.get_repository_map()
        self.proxy_map["Media"] = self.get_media_map()
        self.proxy_map["Citation"] = self.get_citation_map()
        self.proxy_map["Source"] = self.get_source_map()
        self.proxy_map["Note"] = self.get_note_map()

        self.bookmarks = DbBookmarks(
            self.filter_person_handles(self.db.bookmarks.get())
        )
        self.family_bookmarks = DbBookmarks(
            self.filter_family_handles(self.db.family_bookmarks.get())
        )
        self.event_bookmarks = DbBookmarks(
            self.filter_event_handles(self.db.event_bookmarks.get())
        )
        self.place_bookmarks = DbBookmarks(
            self.filter_place_handles(self.db.place_bookmarks.get())
        )
        self.citation_bookmarks = DbBookmarks(
            self.filter_citation_handles(self.db.citation_bookmarks.get())
        )
        self.source_bookmarks = DbBookmarks(
            self.filter_source_handles(self.db.source_bookmarks.get())
        )
        self.repo_bookmarks = DbBookmarks(
            self.filter_repository_handles(self.db.repo_bookmarks.get())
        )
        self.media_bookmarks = DbBookmarks(
            self.filter_media_handles(self.db.media_bookmarks.get())
        )
        self.note_bookmarks = DbBookmarks(
            self.filter_note_handles(self.db.note_bookmarks.get())
        )

    def __getattr__(self, name):
        if name == "readonly":
            return True
        else:
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

    def get_source_map(self):
        map = {}
        for handle in self.db.iter_source_handles():
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

    def proxy_process_source(self, source):
        return source

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

    def filter_source_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Source"]]

    def filter_note_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Note"]]

    # Iter raw data:

    def _iter_raw_person_data(self):
        for handle in self.proxy_map["Person"]:
            # Currently the proxies use Gramps Objects for processing:
            person = self.get_person_from_handle(handle)
            yield handle, object_to_data(person)

    def _iter_raw_family_data(self):
        for handle in self.proxy_map["Family"]:
            # Currently the proxies use Gramps Objects for processing:
            family = self.get_family_from_handle(handle)
            yield handle, object_to_data(family)

    def _iter_raw_event_data(self):
        for handle in self.proxy_map["Event"]:
            # Currently the proxies use Gramps Objects for processing:
            event = self.get_event_from_handle(handle)
            yield handle, object_to_data(event)

    def _iter_raw_place_data(self):
        for handle in self.proxy_map["Place"]:
            # Currently the proxies use Gramps Objects for processing:
            place = self.get_place_from_handle(handle)
            yield handle, object_to_data(place)

    def _iter_raw_repository_data(self):
        for handle in self.proxy_map["Repository"]:
            # Currently the proxies use Gramps Objects for processing:
            repository = self.get_repository_from_handle(handle)
            yield handle, object_to_data(repository)

    def _iter_raw_media_data(self):
        for handle in self.proxy_map["Media"]:
            # Currently the proxies use Gramps Objects for processing:
            media = self.get_media_from_handle(handle)
            yield handle, object_to_data(media)

    def _iter_raw_citation_data(self):
        for handle in self.proxy_map["Citation"]:
            # Currently the proxies use Gramps Objects for processing:
            citation = self.get_citation_from_handle(handle)
            yield handle, object_to_data(citation)

    def _iter_raw_source_data(self):
        for handle in self.proxy_map["Source"]:
            # Currently the proxies use Gramps Objects for processing:
            source = self.get_source_from_handle(handle)
            yield handle, object_to_data(source)

    def _iter_raw_note_data(self):
        for handle in self.proxy_map["Note"]:
            # Currently the proxies use Gramps Objects for processing:
            note = self.get_note_from_handle(handle)
            yield handle, object_to_data(note)

    # Get numbers:

    def get_number_of_people(self):
        return len(self.proxy_map["Person"])

    def get_number_of_families(self):
        return len(self.proxy_map["Family"])

    def get_number_of_events(self):
        return len(self.proxy_map["Event"])

    def get_number_of_places(self):
        return len(self.proxy_map["Place"])

    def get_number_of_repositories(self):
        return len(self.proxy_map["Repository"])

    def get_number_of_media(self):
        return len(self.proxy_map["Media"])

    def get_number_of_citations(self):
        return len(self.proxy_map["Citation"])

    def get_number_of_sources(self):
        return len(self.proxy_map["Source"])

    def get_number_of_notes(self):
        return len(self.proxy_map["Note"])

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

    @functools.cache
    def get_event_from_handle(self, handle):
        if handle in self.proxy_map["Event"]:
            event = self.db.get_event_from_handle(handle)
            processed = self.proxy_process_event(event)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_place_from_handle(self, handle):
        if handle in self.proxy_map["Place"]:
            place = self.db.get_place_from_handle(handle)
            processed = self.proxy_process_place(place)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_repository_from_handle(self, handle):
        if handle in self.proxy_map["Repository"]:
            repository = self.db.get_repository_from_handle(handle)
            processed = self.proxy_process_repository(repository)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_media_from_handle(self, handle):
        if handle in self.proxy_map["Media"]:
            media = self.db.get_media_from_handle(handle)
            processed = self.proxy_process_media(media)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_citation_from_handle(self, handle):
        if handle in self.proxy_map["Citation"]:
            citation = self.db.get_citation_from_handle(handle)
            processed = self.proxy_process_citation(citation)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_source_from_handle(self, handle):
        if handle in self.proxy_map["Source"]:
            source = self.db.get_source_from_handle(handle)
            processed = self.proxy_process_source(source)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    @functools.cache
    def get_note_from_handle(self, handle):
        if handle in self.proxy_map["Note"]:
            note = self.db.get_note_from_handle(handle)
            processed = self.proxy_process_note(note)
            return processed
        else:
            raise HandleError(f"Handle {handle} not found")

    # Get raw data:

    def get_raw_person_data(self, handle):
        if handle in self.proxy_map["Person"]:
            person = self.db.get_person_from_handle(handle)
            processed = self.proxy_process_person(person)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_family_data(self, handle):
        if handle in self.proxy_map["Family"]:
            family = self.db.get_family_from_handle(handle)
            processed = self.proxy_process_family(family)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_event_data(self, handle):
        if handle in self.proxy_map["Event"]:
            event = self.db.get_event_from_handle(handle)
            processed = self.proxy_process_event(event)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_place_data(self, handle):
        if handle in self.proxy_map["Place"]:
            place = self.db.get_place_from_handle(handle)
            processed = self.proxy_process_place(place)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_repository_data(self, handle):
        if handle in self.proxy_map["Repository"]:
            repository = self.db.get_repository_from_handle(handle)
            processed = self.proxy_process_repository(repository)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_media_data(self, handle):
        if handle in self.proxy_map["Media"]:
            media = self.db.get_media_from_handle(handle)
            processed = self.proxy_process_media(media)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_citation_data(self, handle):
        if handle in self.proxy_map["Citation"]:
            citation = self.db.get_citation_from_handle(handle)
            processed = self.proxy_process_citation(citation)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_source_data(self, handle):
        if handle in self.proxy_map["Source"]:
            source = self.db.get_source_from_handle(handle)
            processed = self.proxy_process_source(source)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    def get_raw_note_data(self, handle):
        if handle in self.proxy_map["Note"]:
            note = self.db.get_note_from_handle(handle)
            processed = self.proxy_process_note(note)
            return object_to_data(processed)
        else:
            raise HandleError(f"Handle {handle} not found")

    # Get from gramps id:

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

    def get_family_from_gramps_id(self, gramps_id):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(gramps_id)
        if family and family.handle in self.proxy_map["Family"]:
            processed = self.proxy_process_family(family)
            return processed
        else:
            return None

    def get_event_from_gramps_id(self, gramps_id):
        """
        Finds a Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(gramps_id)
        if event and event.handle in self.proxy_map["Event"]:
            processed = self.proxy_process_event(event)
            return processed
        else:
            return None

    def get_place_from_gramps_id(self, gramps_id):
        """
        Finds a Place in the database from the passed Gramps ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_gramps_id(gramps_id)
        if place and place.handle in self.proxy_map["Place"]:
            processed = self.proxy_process_place(place)
            return processed
        else:
            return None

    def get_repository_from_gramps_id(self, gramps_id):
        """
        Finds a Repository in the database from the passed Gramps ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_gramps_id(gramps_id)
        if repository and repository.handle in self.proxy_map["Repository"]:
            processed = self.proxy_process_repository(repository)
            return processed
        else:
            return None

    def get_media_from_gramps_id(self, gramps_id):
        """
        Finds a Media in the database from the passed Gramps ID.
        If no such Media exists, None is returned.
        """
        media = self.db.get_media_from_gramps_id(gramps_id)
        if media and media.handle in self.proxy_map["Media"]:
            processed = self.proxy_process_media(media)
            return processed
        else:
            return None

    def get_citation_from_gramps_id(self, gramps_id):
        """
        Finds a Citation in the database from the passed Gramps ID.
        If no such Citation exists, None is returned.
        """
        citation = self.db.get_citation_from_gramps_id(gramps_id)
        if citation and citation.handle in self.proxy_map["Citation"]:
            processed = self.proxy_process_citation(citation)
            return processed
        else:
            return None

    def get_source_from_gramps_id(self, gramps_id):
        """
        Finds a Source in the database from the passed Gramps ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_gramps_id(gramps_id)
        if source and source.handle in self.proxy_map["Source"]:
            processed = self.proxy_process_source(source)
            return processed
        else:
            return None

    def get_note_from_gramps_id(self, gramps_id):
        """
        Finds a Note in the database from the passed Gramps ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_gramps_id(gramps_id)
        if note and note.handle in self.proxy_map["Note"]:
            processed = self.proxy_process_note(note)
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

    def get_family_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Family", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Family"]:
                yield handle

    def get_event_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Event", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Event"]:
                yield handle

    def get_place_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Place", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Place"]:
                yield handle

    def get_repository_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Repository", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Repository"]:
                yield handle

    def get_media_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Media", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Media"]:
                yield handle

    def get_citation_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Citation", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Citation"]:
                yield handle

    def get_source_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Source", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Source"]:
                yield handle

    def get_note_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Note", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Note"]:
                yield handle

    # Iter objects:

    def iter_people(self):
        for handle in self.proxy_map["Person"]:
            yield self.get_person_from_handle(handle)

    def iter_families(self):
        for handle in self.proxy_map["Family"]:
            yield self.get_family_from_handle(handle)

    def iter_events(self):
        for handle in self.proxy_map["Event"]:
            yield self.get_event_from_handle(handle)

    def iter_places(self):
        for handle in self.proxy_map["Place"]:
            yield self.get_place_from_handle(handle)

    def iter_repositories(self):
        for handle in self.proxy_map["Repository"]:
            yield self.get_repository_from_handle(handle)

    def iter_media(self):
        for handle in self.proxy_map["Media"]:
            yield self.get_media_from_handle(handle)

    def iter_citations(self):
        for handle in self.proxy_map["Citation"]:
            yield self.get_citation_from_handle(handle)

    def iter_sources(self):
        for handle in self.proxy_map["Source"]:
            yield self.get_source_from_handle(handle)

    def iter_notes(self):
        for handle in self.proxy_map["Note"]:
            yield self.get_note_from_handle(handle)

    # Iter handles:

    def iter_person_handles(self):
        for handle in self.proxy_map["Person"]:
            yield handle

    def iter_family_handles(self):
        for handle in self.proxy_map["Family"]:
            yield handle

    def iter_event_handles(self):
        for handle in self.proxy_map["Event"]:
            yield handle

    def iter_place_handles(self):
        for handle in self.proxy_map["Place"]:
            yield handle

    def iter_repository_handles(self):
        for handle in self.proxy_map["Repository"]:
            yield handle

    def iter_media_handles(self):
        for handle in self.proxy_map["Media"]:
            yield handle

    def iter_citation_handles(self):
        for handle in self.proxy_map["Citation"]:
            yield handle

    def iter_source_handles(self):
        for handle in self.proxy_map["Source"]:
            yield handle

    def iter_note_handles(self):
        for handle in self.proxy_map["Note"]:
            yield handle

    # Has handle:

    def has_person_handle(self, handle):
        return handle in self.proxy_map["Person"]

    def has_family_handle(self, handle):
        return handle in self.proxy_map["Family"]

    def has_event_handle(self, handle):
        return handle in self.proxy_map["Event"]

    def has_place_handle(self, handle):
        return handle in self.proxy_map["Place"]

    def has_repository_handle(self, handle):
        return handle in self.proxy_map["Repository"]

    def has_media_handle(self, handle):
        return handle in self.proxy_map["Media"]

    def has_citation_handle(self, handle):
        return handle in self.proxy_map["Citation"]

    def has_source_handle(self, handle):
        return handle in self.proxy_map["Source"]

    def has_note_handle(self, handle):
        return handle in self.proxy_map["Note"]

    # Cursors:

    def get_person_cursor(self):
        return ProxyCursor(self.get_raw_person_data, self.get_person_handles)

    def get_family_cursor(self):
        return ProxyCursor(self.get_raw_family_data, self.get_family_handles)

    def get_event_cursor(self):
        return ProxyCursor(self.get_raw_event_data, self.get_event_handles)

    def get_place_cursor(self):
        return ProxyCursor(self.get_raw_place_data, self.get_place_handles)

    def get_repository_cursor(self):
        return ProxyCursor(self.get_raw_repository_data, self.get_repository_handles)

    def get_media_cursor(self):
        return ProxyCursor(self.get_raw_media_data, self.get_media_handles)

    def get_citation_cursor(self):
        return ProxyCursor(self.get_raw_citation_data, self.get_citation_handles)

    def get_source_cursor(self):
        return ProxyCursor(self.get_raw_source_data, self.get_source_handles)

    def get_note_cursor(self):
        return ProxyCursor(self.get_raw_note_data, self.get_note_handles)

    # Misc:

    def find_backlink_handles(self, handle, include_classes=None):
        for class_name, obj_handle in self.db.find_backlink_handles(
            handle, include_classes
        ):
            if obj_handle in self.proxy_map[class_name]:
                yield (class_name, obj_handle)

    def get_default_person(self):
        """returns the default Person of the database"""
        person = self.db.get_default_person()
        if person and person.handle in self.proxy_map["Person"]:
            return person
        else:
            return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        handle = self.db.get_default_handle()
        if handle in self.proxy_map["Person"]:
            return handle
        else:
            return None

    def find_initial_person(self):
        """
        Returns first person in the database
        """
        handle = self.get_default_handle()
        if handle and handle in self.proxy_map["Person"]:
            return self.get_person_from_handle(handle)
        elif len(self.proxy_map["Person"]) > 0:
            return self.get_person_from_handle(self.proxy_map["Person"])
        else:
            return None
