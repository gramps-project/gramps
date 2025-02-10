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
from ..db import DbReadBase
from ..db.bookmarks import DbBookmarks
from ..const import GRAMPS_LOCALE as glocale
from ..config import config
from .private import sanitize_person, sanitize_family
from ..lib.json_utils import object_to_data
from ..lib import (
    Date,
    Person,
    Name,
    Surname,
    NameOriginType,
    Family,
    Source,
    Citation,
    Event,
    Media,
    Place,
    Repository,
    Note,
    Tag,
)


class ProxyDbBase:
    def __init__(self, db):
        """
        Create a new ProxyDb instance.
        """
        self.db = db  # The db on the next lower layer
        self.proxy_map = {}
        self.proxy_map["Person"] = self.get_person_map()
        self.proxy_map["Family"] = self.get_family_map()

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

    def proxy_process_person(self, person):
        return person

    def proxy_process_family(self, family):
        return family

    def filter_person_handles(self, handles):
        return [handle for handle in handles if handle in self.proxy_map["Person"]]

    # The public methods:

    def _iter_raw_person_data(self):
        for handle in self.proxy_map["Person"]:
            # Currently the proxies use Gramps Objects for processing:
            person = self.get_person_from_handle(handle)
            yield handle, object_to_data(person)

    def get_number_of_people(self):
        return len(self.proxy_map["Person"])

    def get_number_of_families(self):
        return len(self.proxy_map["Family"])

    @functools.cache
    def get_person_from_handle(self, handle):
        person = self.db.get_person_from_handle(handle)
        processed = self.proxy_process_person(person)
        return processed

    @functools.cache
    def get_person_from_gramps_id(self, gramps_id):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(gramps_id)
        if person and person.handle in self.proxy_map["Person"]:
            processed = self.proxy_process_person(person)
        else:
            None

    def get_person_handles(self, sort_handles=False, locale=glocale):
        if sort_handles:
            sorted_handles = self.locale_sort("Person", locale.collation)
            for handle in sorted_handles:
                yield handle
        else:
            for handle in self.proxy_map["Person"]:
                yield handle

    @functools.cache
    def get_family_from_handle(self, handle):
        family = self.db.get_family_from_handle(handle)
        processed = self.proxy_process_family(family)
        return processed

    def iter_people(self):
        for handle in self.proxy_map["Person"]:
            yield self.get_person_from_handle(handle)

    def iter_person_handles(self):
        for handle in self.proxy_map["Person"]:
            yield handle

    def iter_family_handles(self):
        for handle in self.proxy_map["Family"]:
            yield handle

    def find_backlink_handles(self, handle, include_classes=None):
        for class_name, obj_handle in self.db.find_backlink_handles(
            handle, include_classes
        ):
            if obj_handle in self.proxy_map[class_name]:
                yield (class_name, obj_handle)


class PrivateProxyDb(ProxyDbBase):
    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for handle, data in self.db._iter_raw_person_data():
            if not data.private:
                map[handle] = {
                    "surname": (
                        data.primary_name.surname_list[0].surname
                        if data.primary_name.surname_list
                        else ""
                    )
                }
        return map

    def proxy_process_person(self, person):
        return sanitize_person(self.db, person)

    def proxy_process_family(self, family):
        return sanitize_family(self.db, family)


class LivingProxyDb(ProxyDbBase):
    MODE_EXCLUDE_ALL = 0
    MODE_INCLUDE_LAST_NAME_ONLY = 1
    MODE_INCLUDE_FULL_NAME_ONLY = 2
    MODE_REPLACE_COMPLETE_NAME = 3
    MODE_INCLUDE_ALL = 99  # usually this will be only tested for, not invoked

    def __init__(
        self, db, mode, current_year=None, years_after_death=0, llocale=glocale
    ):
        self.mode = mode
        if current_year is not None:
            self.current_date = Date()
            self.current_date.set_year(current_year)
        else:
            self.current_date = None
        self.years_after_death = years_after_death
        self._ = llocale.translation.gettext
        self._p_f_n = self._(config.get("preferences.private-given-text"))
        self._p_s_n = self._(config.get("preferences.private-surname-text"))

        super().__init__(db)

    def is_living(self, person):
        """
        Check if a person is considered living.
        Returns True if the person is considered living.
        Returns False if the person is not considered living.
        """
        from ..utils.alive import probably_alive

        # Note: probably_alive uses *all* data to compute
        # alive status
        return probably_alive(
            person, self.db.basedb, self.current_date, self.years_after_death
        )

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        map = {}
        for person in self.db.iter_people():
            if self.is_living(person):
                if self.mode == self.MODE_EXCLUDE_ALL:
                    continue
                elif self.mode == self.MODE_REPLACE_COMPLETE_NAME:
                    surname = self._p_s_n
                else:
                    surname = (
                        person.primary_name.surname_list[0].surname
                        if person.primary_name.surname_list
                        else ""
                    )

                map[person.handle] = {"surname": surname}
            else:
                map[person.handle] = {
                    "surname": (
                        person.primary_name.surname_list[0].surname
                        if person.primary_name.surname_list
                        else ""
                    )
                }

        return map

    def get_family_map(self):
        map = {}
        for family in self.iter_families():
            father_not_living = family.father_handle in self.proxy_map["Person"]
            mother_not_living = family.mother_handle in self.proxy_map["Person"]
            if (
                (
                    family.father_handle is None and family.mother_handle is None
                )  # family with no parents
                or (
                    family.father_handle is None and mother_not_living
                )  # no father, dead mother
                or (
                    family.mother_handle is None and father_not_living
                )  # no mother, dead father
                or (father_not_living and mother_not_living)  # both parents dead
            ):
                map[family.handle] = {"surname": "TODO"}
        return map

    def proxy_process_family(self, family):
        parent_is_living = False

        father_handle = family.get_father_handle()
        if father_handle:
            father = self.db.get_person_from_handle(father_handle)
            if father and father_handle in self.proxy_map["Person"]:
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_father_handle(None)

        mother_handle = family.get_mother_handle()
        if mother_handle:
            if mother_handle in self.proxy_map["Person"]:
                parent_is_living = True
                if self.mode == self.MODE_EXCLUDE_ALL:
                    family.set_mother_handle(None)

        if parent_is_living:
            # Clear all events for families where a parent is living.
            family.set_event_ref_list([])

        if self.mode == self.MODE_EXCLUDE_ALL:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                if child_handle in self.proxy_map["Person"]:
                    family.remove_child_ref(child_ref)

        return family

    def proxy_process_person(self, person):
        """
        Remove information from a person and replace the first name with
        "[Living]" or what has been set in Preferences -> Text.
        """
        new_person = Person()
        new_name = Name()
        old_name = person.get_primary_name()

        new_name.set_group_as(old_name.get_group_as())
        new_name.set_sort_as(old_name.get_sort_as())
        new_name.set_display_as(old_name.get_display_as())
        new_name.set_type(old_name.get_type())
        if (
            self.mode == self.MODE_INCLUDE_LAST_NAME_ONLY
            or self.mode == self.MODE_REPLACE_COMPLETE_NAME
        ):
            new_name.set_first_name(self._p_f_n)
            new_name.set_title("")
        else:  # self.mode == self.MODE_INCLUDE_FULL_NAME_ONLY
            new_name.set_first_name(old_name.get_first_name())
            new_name.set_suffix(old_name.get_suffix())
            new_name.set_title(old_name.get_title())
            new_name.set_call_name(old_name.get_call_name())
            new_name.set_nick_name(old_name.get_nick_name())
            new_name.set_family_nick_name(old_name.get_family_nick_name())

        surnlst = []
        if self.mode == self.MODE_REPLACE_COMPLETE_NAME:
            surname = Surname(source=old_name.get_primary_surname())
            surname.set_surname(self._p_s_n)
            surnlst.append(surname)
        else:
            for surn in old_name.get_surname_list():
                surname = Surname(source=surn)
                if int(surname.origintype) in [
                    NameOriginType.PATRONYMIC,
                    NameOriginType.MATRONYMIC,
                ]:
                    surname.set_surname(self._p_s_n)
                surnlst.append(surname)

        new_name.set_surname_list(surnlst)
        new_person.set_primary_name(new_name)
        new_person.set_privacy(person.get_privacy())
        new_person.set_gender(person.get_gender())
        new_person.set_gramps_id(person.get_gramps_id())
        new_person.set_handle(person.get_handle())
        new_person.set_change_time(person.get_change_time())
        new_person.set_family_handle_list(person.get_family_handle_list())
        new_person.set_parent_family_handle_list(person.get_parent_family_handle_list())
        new_person.set_tag_list(person.get_tag_list())

        return new_person


class FilterProxyDb(ProxyDbBase):
    def __init__(
        self, db, person_filter=None, event_filter=None, note_filter=None, user=None
    ):
        self.person_filter = person_filter
        self.event_filter = event_filter
        self.note_filter = note_filter
        self.user = user

        super().__init__(db)

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        if self.person_filter:
            return self.person_filter.apply(
                self.db, self.db.iter_person_handles(), user=self.user
            )
        else:
            return super().get_person_map()

    def get_event_map(self):
        if self.event_filter:
            return self.event_filter.apply(
                self.db, self.db.iter_event_handles(), user=self.user
            )
        else:
            return super().get_event_map()

    def get_note_map(self):
        if self.note_filter:
            return self.note_filter.apply(
                self.db, self.db.iter_note_handles(), user=self.user
            )
        else:
            return super().get_note_map()


class ReferencedBySelectionProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps
    database, but returning all objects which are referenced by a
    selection, or by an object that is referenced by an object which
    is eventually referenced by one of the selected objects.
    """

    def __init__(self, db, all_people=False):
        """
        Create a new ReferencedByPeopleProxyDb instance.

        :param all_people: if True, get all people, and the items they link to;
                           if False, get all people that are connected to
                           something, and all of items they link to.
        :type all_people: boolean
        """
        self.db = db
        self.reset_references()
        # If restricted_to["Person"] is a set, restrict process to
        # them, and do not process others outside of them
        self.restricted_to = {"Person": None}
        # Build lists of referenced objects
        # iter through whatever object(s) you want to start
        # the trace.
        self.queue = []
        if all_people:
            # Do not add references to those not already included
            self.restricted_to["Person"] = list(self.db.iter_person_handles())
            # Spread activation to all other items:
            for handle in self.restricted_to["Person"]:
                if handle:
                    self.queue_object("Person", handle)
        else:
            # get rid of orphaned people:
            # first, get all of the links from people:
            for handle in self.db.iter_person_handles():
                self.queue_object("Person", handle, False)
            # save those people:
            self.restricted_to["Person"] = self.referenced["Person"]
            # reset, and just follow those people
            self.reset_references()
            for handle in self.restricted_to["Person"]:
                if handle:
                    self.queue_object("Person", handle)
        # process:
        while len(self.queue):
            obj_type, handle, reference = self.queue.pop()
            self.process_object(obj_type, handle, reference)

        super().__init__(db)

    def queue_object(self, obj_type, handle, reference=True):
        self.queue.append((obj_type, handle, reference))

    def get_person_map(self):
        return self.referenced["Person"]

    def reset_references(self):
        self.referenced = {
            "Person": set(),
            "Family": set(),
            "Event": set(),
            "Place": set(),
            "Source": set(),
            "Citation": set(),
            "Repository": set(),
            "Media": set(),
            "Note": set(),
            "Tag": set(),
        }

    def process_object(self, class_name, handle, reference=True):
        if class_name == "Person":
            obj = self.db.get_person_from_handle(handle)
            if obj:
                self.process_person(obj, reference)
        elif class_name == "Family":
            obj = self.db.get_family_from_handle(handle)
            if obj:
                self.process_family(obj)
        elif class_name == "Event":
            obj = self.db.get_event_from_handle(handle)
            if obj:
                self.process_event(obj)
        elif class_name == "Place":
            obj = self.db.get_place_from_handle(handle)
            if obj:
                self.process_place(obj)
        elif class_name == "Source":
            obj = self.db.get_source_from_handle(handle)
            if obj:
                self.process_source(obj)
        elif class_name == "Citation":
            obj = self.db.get_citation_from_handle(handle)
            if obj:
                self.process_citation(obj)
        elif class_name == "Repository":
            obj = self.db.get_repository_from_handle(handle)
            if obj:
                self.process_repository(obj)
        elif class_name == "Media":
            obj = self.db.get_media_from_handle(handle)
            if obj:
                self.process_media(obj)
        elif class_name == "Note":
            obj = self.db.get_note_from_handle(handle)
            if obj:
                self.process_note(obj)
        else:
            raise AttributeError("unknown class: '%s'" % class_name)

    def process_person(self, person, reference=True):
        """
        Follow the person object and find all of the primary objects
        that it references.
        """
        # A person we have seen before:
        if person.handle in self.referenced["Person"]:
            return
        # A person that we should not add:
        if (
            self.restricted_to["Person"]
            and person.handle not in self.restricted_to["Person"]
        ):
            return
        if reference:
            # forward reference:
            self.referenced["Person"].add(person.handle)
        # include backward references to this object:
        for class_name, handle in self.db.find_backlink_handles(
            person.handle, ["Person", "Family"]
        ):
            self.queue_object(class_name, handle)

        name = person.get_primary_name()
        if name:
            self.process_name(name)

        for handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(handle)
            if family:
                self.queue_object("Family", family.handle)

        for handle in person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(handle)
            if family:
                self.queue_object("Family", family.handle)

        for name in person.get_alternate_names():
            if name:
                self.process_name(name)

        for event_ref in person.get_event_ref_list():
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
                if event:
                    self.process_event_ref(event_ref)

        self.process_addresses(person)
        self.process_attributes(person)
        self.process_citation_ref_list(person)
        self.process_urls(person)
        self.process_media_ref_list(person)
        self.process_lds_ords(person)
        self.process_notes(person)
        self.process_associations(person)
        self.process_tags(person)

    def process_family(self, family):
        """
        Follow the family object and find all of the primary objects
        that it references.
        """
        if family is None or family.handle in self.referenced["Family"]:
            return
        self.referenced["Family"].add(family.handle)

        if family.mother_handle:
            self.queue_object("Person", family.mother_handle)
        if family.father_handle:
            self.queue_object("Person", family.father_handle)
        for child_ref in family.get_child_ref_list():
            if not child_ref:
                continue
            self.queue_object("Person", child_ref.ref)
            self.process_notes(child_ref)
            self.process_citation_ref_list(child_ref)

        for event_ref in family.get_event_ref_list():
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
                if event:
                    self.process_event_ref(event_ref)

        self.process_citation_ref_list(family)
        self.process_notes(family)
        self.process_media_ref_list(family)
        self.process_attributes(family)
        self.process_lds_ords(family)
        self.process_tags(family)

    def process_event(self, event):
        """
        Follow the event object and find all of the primary objects
        that it references.
        """
        if event is None or event.handle in self.referenced["Event"]:
            return
        self.referenced["Event"].add(event.handle)
        self.process_citation_ref_list(event)
        self.process_notes(event)
        self.process_media_ref_list(event)
        self.process_attributes(event)

        place_handle = event.get_place_handle()
        if place_handle:
            place = self.db.get_place_from_handle(place_handle)
            if place:
                self.process_place(place)

        self.process_tags(event)

    def process_place(self, place):
        """
        Follow the place object and find all of the primary objects
        that it references.
        """
        if place is None or place.handle in self.referenced["Place"]:
            return
        self.referenced["Place"].add(place.handle)
        self.process_citation_ref_list(place)
        self.process_notes(place)
        self.process_media_ref_list(place)
        self.process_urls(place)

        for placeref in place.get_placeref_list():
            place = self.db.get_place_from_handle(placeref.ref)
            if place:
                self.process_place(place)

        self.process_tags(place)

    def process_source(self, source):
        """
        Follow the source object and find all of the primary objects
        that it references.
        """
        if source is None or source.handle in self.referenced["Source"]:
            return
        self.referenced["Source"].add(source.handle)
        for repo_ref in source.get_reporef_list():
            if repo_ref:
                self.process_notes(repo_ref)
                handle = repo_ref.get_reference_handle()
                repo = self.db.get_repository_from_handle(handle)
                if repo:
                    self.process_repository(repo)
        self.process_media_ref_list(source)
        self.process_notes(source)
        self.process_tags(source)

    def process_citation(self, citation):
        """
        Follow the citation object and find all of the primary objects
        that it references.
        """
        if citation is None or citation.handle in self.referenced["Citation"]:
            return
        self.referenced["Citation"].add(citation.handle)
        source_handle = citation.get_reference_handle()
        if source_handle:
            source = self.db.get_source_from_handle(source_handle)
            if source:
                self.process_source(source)
        self.process_media_ref_list(citation)
        self.process_notes(citation)
        self.process_tags(citation)

    def process_repository(self, repository):
        """
        Follow the repository object and find all of the primary objects
        that it references.
        """
        if repository is None or repository.handle in self.referenced["Repository"]:
            return
        self.referenced["Repository"].add(repository.handle)
        self.process_notes(repository)
        self.process_addresses(repository)
        self.process_urls(repository)
        self.process_tags(repository)

    def process_media(self, media):
        """
        Follow the media object and find all of the primary objects
        that it references.
        """
        if media is None or media.handle in self.referenced["Media"]:
            return
        self.referenced["Media"].add(media.handle)
        self.process_citation_ref_list(media)
        self.process_attributes(media)
        self.process_notes(media)
        self.process_tags(media)

    def process_note(self, note):
        """
        Follow the note object and find all of the primary objects
        that it references.
        """
        if note is None or note.handle in self.referenced["Note"]:
            return
        self.referenced["Note"].add(note.handle)
        for tag in note.text.get_tags():
            if tag.name == "Link":
                if tag.value.startswith("gramps://"):
                    obj_class, prop, value = tag.value[9:].split("/", 2)
                    if obj_class == "Media":  # bug6493
                        obj_class = "Media"
                    if prop == "handle":
                        self.queue_object(obj_class, value)
        self.process_tags(note)

    def process_notes(self, original_obj):
        """Find all of the primary objects referred to"""
        for note_handle in original_obj.get_note_list():
            if note_handle:
                note = self.db.get_note_from_handle(note_handle)
                self.process_note(note)

    # --------------------------------------------

    def process_tags(self, original_obj):
        """
        Record the tags referenced by the primary object.
        """
        for tag_handle in original_obj.get_tag_list():
            self.referenced["Tag"].add(tag_handle)

    # --------------------------------------------

    def process_name(self, name):
        """Find all of the primary objects referred to"""
        self.process_citation_ref_list(name)
        self.process_notes(name)

    def process_addresses(self, original_obj):
        """Find all of the primary objects referred to"""
        for address in original_obj.get_address_list():
            if address:
                self.process_address(address)

    def process_address(self, address):
        """Find all of the primary objects referred to"""
        self.process_citation_ref_list(address)
        self.process_notes(address)

    def process_attributes(self, original_obj):
        """Find all of the primary objects referred to"""
        for attribute in original_obj.get_attribute_list():
            if attribute:
                self.process_notes(attribute)
                self.process_citation_ref_list(attribute)

    def process_citation_ref_list(self, original_obj):
        """Find all of the primary objects referred to"""
        for handle in original_obj.get_citation_list():
            if handle:
                citation = self.db.get_citation_from_handle(handle)
                if citation:
                    self.process_citation(citation)

    def process_urls(self, original_obj):
        """Find all of the primary objects referred to"""
        pass

    def process_media_ref_list(self, original_obj):
        """Find all of the primary objects referred to"""
        for media_ref in original_obj.get_media_list():
            if media_ref:
                self.process_notes(media_ref)
                self.process_attributes(media_ref)
                self.process_citation_ref_list(media_ref)
                handle = media_ref.get_reference_handle()
                media = self.db.get_media_from_handle(handle)
                if media:
                    self.process_media(media)

    def process_lds_ords(self, original_obj):
        """Find all of the primary objects referred to"""
        for lds_ord in original_obj.get_lds_ord_list():
            if lds_ord:
                self.process_lds_ord(lds_ord)

    def process_lds_ord(self, lds_ord):
        """Find all of the primary objects referred to"""
        fam_handle = lds_ord.get_family_handle()
        if fam_handle:
            fam = self.db.get_family_from_handle(fam_handle)
            if fam:
                self.queue_object("Family", fam_handle)

        place_handle = lds_ord.get_place_handle()
        if place_handle:
            place = self.db.get_place_from_handle(place_handle)
            if place:
                self.process_place(place)

        self.process_citation_ref_list(lds_ord)
        self.process_notes(lds_ord)

    def process_associations(self, original_obj):
        """Find all of the primary objects referred to"""
        for person_ref in original_obj.get_person_ref_list():
            if person_ref:
                self.process_citation_ref_list(person_ref)
                self.process_notes(person_ref)
                person = self.db.get_person_from_handle(person_ref.ref)
                if person:
                    self.queue_object("Person", person.handle)

    def process_event_ref(self, event_ref):
        """Find all of the primary objects referred to"""
        self.process_notes(event_ref)
        self.process_attributes(event_ref)
        event = self.db.get_event_from_handle(event_ref.ref)
        if event:
            self.process_event(event)
