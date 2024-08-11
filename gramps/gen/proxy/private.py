#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2010       Nick Hall
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
Proxy class for the Gramps databases. Filter out all data marked private.
"""

# -------------------------------------------------------------------------
#
# Python libraries
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
import logging

LOG = logging.getLogger(".citation")

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from ..lib import (
    MediaRef,
    Attribute,
    Address,
    EventRef,
    Person,
    Name,
    Source,
    RepoRef,
    Media,
    Place,
    Event,
    Family,
    ChildRef,
    Repository,
    LdsOrd,
    Surname,
    Citation,
    SrcAttribute,
    Note,
    Tag,
)
from .proxybase import ProxyDbBase


class PrivateProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

    def __init__(self, db):
        """
        Create a new PrivateProxyDb instance.
        """
        ProxyDbBase.__init__(self, db)

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_handle(handle)
        if person and not person.get_privacy():
            return sanitize_person(self.db, person)
        return None

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed Gramps ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_handle(handle)
        if source and not source.get_privacy():
            return sanitize_source(self.db, source)
        return None

    def get_citation_from_handle(self, handle):
        """
        Finds a Citation in the database from the passed Gramps ID.
        If no such Citation exists, None is returned.
        """
        citation = self.db.get_citation_from_handle(handle)
        if citation and not citation.get_privacy():
            return sanitize_citation(self.db, citation)
        return None

    def get_media_from_handle(self, handle):
        """
        Finds an Object in the database from the passed Gramps ID.
        If no such Object exists, None is returned.
        """
        media = self.db.get_media_from_handle(handle)
        if media and not media.get_privacy():
            return sanitize_media(self.db, media)
        return None

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed Gramps ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_handle(handle)
        if place and not place.get_privacy():
            return sanitize_place(self.db, place)
        return None

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_handle(handle)
        if event and not event.get_privacy():
            return sanitize_event(self.db, event)
        return None

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_handle(handle)
        if family and not family.get_privacy():
            return sanitize_family(self.db, family)
        return None

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed Gramps ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_handle(handle)
        if repository and not repository.get_privacy():
            return sanitize_repository(self.db, repository)
        return None

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed Gramps ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_handle(handle)
        if note and not note.get_privacy():
            return note
        return None

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        if person and not person.get_privacy():
            return sanitize_person(self.db, person)
        return None

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        if family and not family.get_privacy():
            return sanitize_family(self.db, family)
        return None

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(val)
        if event and not event.get_privacy():
            return sanitize_event(self.db, event)
        return None

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed Gramps ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_gramps_id(val)
        if place and not place.get_privacy():
            return sanitize_place(self.db, place)
        return None

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed Gramps ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_gramps_id(val)
        if source and not source.get_privacy():
            return sanitize_source(self.db, source)
        return None

    def get_citation_from_gramps_id(self, val):
        """
        Finds a Citation in the database from the passed Gramps ID.
        If no such Citation exists, None is returned.
        """
        citation = self.db.get_citation_from_gramps_id(val)
        if citation and not citation.get_privacy():
            return sanitize_citation(self.db, citation)
        return None

    def get_media_from_gramps_id(self, val):
        """
        Finds a Media in the database from the passed Gramps ID.
        If no such Media exists, None is returned.
        """
        obj = self.db.get_media_from_gramps_id(val)
        if obj and not obj.get_privacy():
            return sanitize_media(self.db, obj)
        return None

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed Gramps ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_gramps_id(val)
        if repository and not repository.get_privacy():
            return sanitize_repository(self.db, repository)
        return None

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed Gramps ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_gramps_id(val)
        if note and not note.get_privacy():
            return note
        return None

    # Define predicate functions for use by default iterator methods

    def include_person(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_person(handle)
        return obj and not obj.get_privacy()

    def include_family(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_family(handle)
        return obj and not obj.get_privacy()

    def include_event(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_event(handle)
        return obj and not obj.get_privacy()

    def include_source(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_source(handle)
        return obj and not obj.get_privacy()

    def include_citation(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_citation(handle)
        return obj and not obj.get_privacy()

    def include_place(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_place(handle)
        return obj and not obj.get_privacy()

    def include_media(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_media(handle)
        return obj and not obj.get_privacy()

    def include_repository(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_repository(handle)
        return obj and not obj.get_privacy()

    def include_note(self, handle):
        """
        Predicate returning True if object is to be included, else False
        """
        obj = self.get_unfiltered_note(handle)
        return obj and not obj.get_privacy()

    def get_default_person(self):
        """returns the default Person of the database"""
        person = self.db.get_default_person()
        if person and not person.get_privacy():
            return sanitize_person(self.db, person)
        return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        handle = self.db.get_default_handle()
        if handle:
            person = self.db.get_person_from_handle(handle)
            if person and not person.get_privacy():
                return handle
        return None

    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        person = self.db.get_person_from_handle(handle)
        if person and not person.get_privacy():
            return True
        return False

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        event = self.db.get_event_from_handle(handle)
        if event and not event.get_privacy():
            return True
        return False

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        source = self.db.get_source_from_handle(handle)
        if source and not source.get_privacy():
            return True
        return False

    def has_citation_handle(self, handle):
        """
        returns True if the handle exists in the current Citation database.
        """
        citation = self.db.get_citation_from_handle(handle)
        if citation and not citation.get_privacy():
            return True
        return False

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        place = self.db.get_place_from_handle(handle)
        if place and not place.get_privacy():
            return True
        return False

    def has_family_handle(self, handle):
        """
        Return True if the handle exists in the current Family database.
        """
        family = self.db.get_family_from_handle(handle)
        if family and not family.get_privacy():
            return True
        return False

    def has_object_handle(self, handle):
        """
        Return True if the handle exists in the current Mediadatabase.
        """
        object = self.db.get_media_from_handle(handle)
        if object and not object.get_privacy():
            return True
        return False

    def has_repository_handle(self, handle):
        """
        Return True if the handle exists in the current Repository database.
        """
        repository = self.db.get_repository_from_handle(handle)
        if repository and not repository.get_privacy():
            return True
        return False

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
        """
        note = self.db.get_note_from_handle(handle)
        if note and not note.get_privacy():
            return True
        return False

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

        # This isn't done yet because it doesn't check if references are
        # private (like a MediaRef). It only checks if the
        # referenced object is private.

        objects = {
            "Person": self.db.get_person_from_handle,
            "Family": self.db.get_family_from_handle,
            "Event": self.db.get_event_from_handle,
            "Source": self.db.get_source_from_handle,
            "Citation": self.db.get_citation_from_handle,
            "Place": self.db.get_place_from_handle,
            "Media": self.db.get_media_from_handle,
            "Note": self.db.get_note_from_handle,
            "Repository": self.db.get_repository_from_handle,
        }

        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for class_name, handle in handle_itr:
            if class_name in objects:
                obj = objects[class_name](handle)
                if obj and not obj.get_privacy():
                    yield (class_name, handle)
            else:
                raise NotImplementedError
        return


def copy_media_ref_list(db, original_obj, clean_obj):
    """
    Copies media references from one object to another - excluding private
    references and references to private objects.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: MediaBase
    :param clean_obj: Object that will have only non-private references
    :type original_obj: MediaBase
    :returns: Nothing
    """
    for media_ref in original_obj.get_media_list():
        if media_ref and not media_ref.get_privacy():
            handle = media_ref.get_reference_handle()
            media = db.get_media_from_handle(handle)
            if media and not media.get_privacy():
                clean_obj.add_media_reference(sanitize_media_ref(db, media_ref))


def copy_citation_ref_list(db, original_obj, clean_obj):
    """
    Copies citation references from one object to another - excluding references
    to private citations, and references to citations that refer to private
    sources.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: CitationBase
    :param clean_obj: Object that will have only non-private references
    :type original_obj: CitationBase
    :returns: Nothing
    """
    for citation_handle in original_obj.get_citation_list():
        citation = db.get_citation_from_handle(citation_handle)
        if citation and not citation.get_privacy():
            handle = citation.get_reference_handle()
            source = db.get_source_from_handle(handle)
            if source and not source.get_privacy():
                clean_obj.add_citation(citation_handle)


def copy_notes(db, original_obj, clean_obj):
    """
    Copies notes from one object to another - excluding references to private
    notes.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: NoteBase
    :param clean_obj: Object that will have only non-private references
    :type original_obj: NoteBase
    :returns: Nothing
    """
    for note_handle in original_obj.get_note_list():
        note = db.get_note_from_handle(note_handle)
        if note and not note.get_privacy():
            clean_obj.add_note(note_handle)


def copy_associations(db, original_obj, clean_obj):
    """
    Copies associations from one object to another - excluding
    references to private notes.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: Base
    :param clean_obj: Object that will have only non-private references
    :type original_obj: Base
    :returns: Nothing
    """
    new_person_ref_list = []
    for person_ref in original_obj.get_person_ref_list():
        if person_ref and not person_ref.get_privacy():
            associated_person = db.get_person_from_handle(person_ref.ref)
            if associated_person and not associated_person.get_privacy():
                new_person_ref_list.append(person_ref)
    clean_obj.set_person_ref_list(new_person_ref_list)


def copy_attributes(db, original_obj, clean_obj):
    """
    Copies attributes from one object to another - excluding references to
    private attributes.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: AttributeBase
    :param clean_obj: Object that will have only non-private references
    :type original_obj: AttributeBase
    :returns: Nothing
    """
    for attribute in original_obj.get_attribute_list():
        if attribute and not attribute.get_privacy():
            new_attribute = Attribute()
            new_attribute.set_type(attribute.get_type())
            new_attribute.set_value(attribute.get_value())
            copy_notes(db, attribute, new_attribute)
            copy_citation_ref_list(db, attribute, new_attribute)
            clean_obj.add_attribute(new_attribute)


def copy_srcattributes(db, original_obj, clean_obj):
    """
    Copies srcattributes from one object to another - excluding references to
    private srcattributes.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have private references
    :type original_obj: SrcAttributeBase
    :param clean_obj: Object that will have only non-private references
    :type original_obj: SrcAttributeBase
    :returns: Nothing
    """
    for attribute in original_obj.get_attribute_list():
        if attribute and not attribute.get_privacy():
            new_attribute = SrcAttribute()
            new_attribute.set_type(attribute.get_type())
            new_attribute.set_value(attribute.get_value())
            clean_obj.add_attribute(new_attribute)


def copy_urls(db, original_obj, clean_obj):
    """
    Copies urls from one object to another - excluding references to
    private urls.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have urls
    :type original_obj: UrlBase
    :param clean_obj: Object that will have only non-private urls
    :type original_obj: UrlBase
    :returns: Nothing
    """
    for url in original_obj.get_url_list():
        if url and not url.get_privacy():
            clean_obj.add_url(url)


def copy_lds_ords(db, original_obj, clean_obj):
    """
    Copies LDS ORDs from one object to another - excluding references to
    private LDS ORDs.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have LDS ORDs
    :type original_obj: LdsOrdBase
    :param clean_obj: Object that will have only non-private LDS ORDs
    :type original_obj: LdsOrdBase
    :returns: Nothing
    """
    for lds_ord in original_obj.get_lds_ord_list():
        if lds_ord and not lds_ord.get_privacy():
            clean_obj.add_lds_ord(sanitize_lds_ord(db, lds_ord))


def copy_addresses(db, original_obj, clean_obj):
    """
    Copies addresses from one object to another - excluding references to
    private addresses.

    :param db: Gramps database to which the references belongs
    :type db: DbBase
    :param original_obj: Object that may have addresses
    :type original_obj: AddressBase
    :param clean_obj: Object that will have only non-private addresses
    :type original_obj: AddressBase
    :returns: Nothing
    """
    for address in original_obj.get_address_list():
        if address and not address.get_privacy():
            clean_obj.add_address(sanitize_address(db, address))


def sanitize_lds_ord(db, lds_ord):
    """
    Create a new LdsOrd instance based off the passed LdsOrd
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the LdsOrd object belongs
    :type db: DbBase
    :param name: source LdsOrd object that will be copied with
                 privacy records removed
    :type name: LdsOrd
    :returns: 'cleansed' LdsOrd object
    :rtype: LdsOrd
    """
    new_lds_ord = LdsOrd()
    new_lds_ord.set_type(lds_ord.get_type())
    new_lds_ord.set_status(lds_ord.get_status())
    new_lds_ord.set_temple(lds_ord.get_temple())

    fam_handle = lds_ord.get_family_handle()
    if fam_handle:
        fam = db.get_family_from_handle(fam_handle)
        if fam and not fam.get_privacy():
            new_lds_ord.set_family_handle(fam_handle)

    new_lds_ord.set_date_object(lds_ord.get_date_object())

    place_handle = lds_ord.get_place_handle()
    if place_handle:
        place = db.get_place_from_handle(place_handle)
        if place and not place.get_privacy():
            new_lds_ord.set_place_handle(place_handle)

    copy_citation_ref_list(db, lds_ord, new_lds_ord)
    copy_notes(db, lds_ord, new_lds_ord)

    return new_lds_ord


def sanitize_address(db, address):
    """
    Create a new Address instance based off the passed Address
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param name: source Address object that will be copied with
                 privacy records removed
    :type name: Address
    :returns: 'cleansed' Address object
    :rtype: Address
    """
    new_address = Address()

    new_address.set_street(address.get_street())
    new_address.set_locality(address.get_locality())
    new_address.set_city(address.get_city())
    new_address.set_county(address.get_county())
    new_address.set_state(address.get_state())
    new_address.set_country(address.get_country())
    new_address.set_postal_code(address.get_postal_code())
    new_address.set_phone(address.get_phone())

    new_address.set_date_object(address.get_date_object())
    copy_citation_ref_list(db, address, new_address)
    copy_notes(db, address, new_address)

    return new_address


def sanitize_name(db, name):
    """
    Create a new Name instance based off the passed Name
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param name: source Name object that will be copied with
                 privacy records removed
    :type name: Name
    :returns: 'cleansed' Name object
    :rtype: Name
    """
    new_name = Name()
    new_name.set_group_as(name.get_group_as())
    new_name.set_sort_as(name.get_sort_as())
    new_name.set_display_as(name.get_display_as())
    new_name.set_call_name(name.get_call_name())
    new_name.set_nick_name(name.get_nick_name())
    new_name.set_family_nick_name(name.get_family_nick_name())
    new_name.set_type(name.get_type())
    new_name.set_first_name(name.get_first_name())
    new_name.set_suffix(name.get_suffix())
    new_name.set_title(name.get_title())
    new_name.set_date_object(name.get_date_object())
    new_name.set_surname_list(name.get_surname_list())

    copy_citation_ref_list(db, name, new_name)
    copy_notes(db, name, new_name)

    return new_name


def sanitize_media_ref(db, media_ref):
    """
    Create a new MediaRef instance based off the passed MediaRef
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the MediaRef object belongs
    :type db: DbBase
    :param source_ref: source MediaRef object that will be copied with
                       privacy records removed
    :type source_ref: MediaRef
    :returns: 'cleansed' MediaRef object
    :rtype: MediaRef
    """
    new_ref = MediaRef()
    new_ref.set_rectangle(media_ref.get_rectangle())

    new_ref.set_reference_handle(media_ref.get_reference_handle())
    copy_notes(db, media_ref, new_ref)
    copy_attributes(db, media_ref, new_ref)
    copy_citation_ref_list(db, media_ref, new_ref)

    return new_ref


def sanitize_citation(db, citation):
    """
    Create a new Citation instance based off the passed Citation
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param citation: source Citation object that will be copied with
                     privacy records removed
    :type citation: Citation
    :returns: 'cleansed' Citation object
    :rtype: Citation
    """
    new_citation = Citation()
    new_citation.set_date_object(citation.get_date_object())
    new_citation.set_page(citation.get_page())
    new_citation.set_confidence_level(citation.get_confidence_level())
    new_citation.set_reference_handle(citation.get_reference_handle())
    new_citation.set_gramps_id(citation.get_gramps_id())
    new_citation.set_handle(citation.get_handle())
    new_citation.set_change_time(citation.get_change_time())
    new_citation.set_tag_list(citation.get_tag_list())
    copy_srcattributes(db, citation, new_citation)
    copy_notes(db, citation, new_citation)
    copy_media_ref_list(db, citation, new_citation)

    return new_citation


def sanitize_event_ref(db, event_ref):
    """
    Create a new EventRef instance based off the passed EventRef
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param event_ref: source EventRef object that will be copied with
                      privacy records removed
    :type event_ref: EventRef
    :returns: 'cleansed' EventRef object
    :rtype: EventRef
    """
    new_ref = EventRef()

    new_ref.set_reference_handle(event_ref.get_reference_handle())
    new_ref.set_role(event_ref.get_role())
    copy_citation_ref_list(db, event_ref, new_ref)
    copy_notes(db, event_ref, new_ref)
    copy_attributes(db, event_ref, new_ref)

    return new_ref


def sanitize_person(db, person):
    """
    Create a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param person: source Person object that will be copied with
                   privacy records removed
    :type person: Person
    :returns: 'cleansed' Person object
    :rtype: Person
    """
    new_person = Person()

    # copy gender
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    new_person.set_change_time(person.get_change_time())
    new_person.set_tag_list(person.get_tag_list())

    # copy names if not private
    name = person.get_primary_name()
    if (name and name.get_privacy()) or (person and person.get_privacy()):
        # Do this so a person always has a primary name of some sort.
        name = Name()
        surn = Surname()
        surn.set_surname(_("Private"))
        name.set_surname_list([surn])
        name.set_primary_surname()
    else:
        name = sanitize_name(db, name)
    new_person.set_primary_name(name)

    # copy Family reference list
    for handle in person.get_family_handle_list():
        family = db.get_family_from_handle(handle)
        if family and not family.get_privacy():
            new_person.add_family_handle(handle)

    # copy Family reference list
    for handle in person.get_parent_family_handle_list():
        family = db.get_family_from_handle(handle)
        if not family:
            continue
        elif family.get_privacy():
            continue
        child_ref_list = family.get_child_ref_list()
        for child_ref in child_ref_list:
            if child_ref.get_reference_handle() == person.get_handle():
                if child_ref and not child_ref.get_privacy():
                    new_person.add_parent_family_handle(handle)
                break

    for name in person.get_alternate_names():
        if name and not name.get_privacy():
            new_person.add_alternate_name(sanitize_name(db, name))

    # copy event list
    for event_ref in person.get_event_ref_list():
        if event_ref and not event_ref.get_privacy():
            event = db.get_event_from_handle(event_ref.ref)
            if event and not event.get_privacy():
                new_person.add_event_ref(sanitize_event_ref(db, event_ref))

    # Copy birth and death after event list to maintain the order.
    # copy birth event
    event_ref = person.get_birth_ref()
    if event_ref and not event_ref.get_privacy():
        event = db.get_event_from_handle(event_ref.ref)
        if event and not event.get_privacy():
            new_person.set_birth_ref(sanitize_event_ref(db, event_ref))

    # copy death event
    event_ref = person.get_death_ref()
    if event_ref and not event_ref.get_privacy():
        event = db.get_event_from_handle(event_ref.ref)
        if event and not event.get_privacy():
            new_person.set_death_ref(sanitize_event_ref(db, event_ref))

    copy_addresses(db, person, new_person)
    copy_attributes(db, person, new_person)
    copy_citation_ref_list(db, person, new_person)
    copy_urls(db, person, new_person)
    copy_media_ref_list(db, person, new_person)
    copy_lds_ords(db, person, new_person)
    copy_notes(db, person, new_person)
    copy_associations(db, person, new_person)

    return new_person


def sanitize_source(db, source):
    """
    Create a new Source instance based off the passed Source
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param source: source Source object that will be copied with
                   privacy records removed
    :type source: Source
    :returns: 'cleansed' Source object
    :rtype: Source
    """
    new_source = Source()

    new_source.set_author(source.get_author())
    new_source.set_title(source.get_title())
    new_source.set_publication_info(source.get_publication_info())
    new_source.set_abbreviation(source.get_abbreviation())
    new_source.set_gramps_id(source.get_gramps_id())
    new_source.set_handle(source.get_handle())
    new_source.set_change_time(source.get_change_time())
    new_source.set_tag_list(source.get_tag_list())

    for repo_ref in source.get_reporef_list():
        if repo_ref and not repo_ref.get_privacy():
            handle = repo_ref.get_reference_handle()
            repo = db.get_repository_from_handle(handle)
            if repo and not repo.get_privacy():
                new_source.add_repo_reference(RepoRef(repo_ref))

    copy_srcattributes(db, source, new_source)
    copy_media_ref_list(db, source, new_source)
    copy_notes(db, source, new_source)

    return new_source


def sanitize_media(db, media):
    """
    Create a new Media instance based off the passed Media
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param media: source Media object that will be copied with
                  privacy records removed
    :type media: Media
    :returns: 'cleansed' Media object
    :rtype: Media
    """
    new_media = Media()

    new_media.set_mime_type(media.get_mime_type())
    new_media.set_path(media.get_path())
    new_media.set_description(media.get_description())
    new_media.set_gramps_id(media.get_gramps_id())
    new_media.set_handle(media.get_handle())
    new_media.set_change_time(media.get_change_time())
    new_media.set_date_object(media.get_date_object())
    new_media.set_tag_list(media.get_tag_list())
    new_media.set_checksum(media.get_checksum())

    copy_citation_ref_list(db, media, new_media)
    copy_attributes(db, media, new_media)
    copy_notes(db, media, new_media)

    return new_media


def sanitize_place(db, place):
    """
    Create a new Place instance based off the passed Place
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param place: source Place object that will be copied with
                  privacy records removed
    :type place: Place
    :returns: 'cleansed' Place object
    :rtype: Place
    """
    new_place = Place()

    new_place.set_title(place.get_title())
    new_place.set_gramps_id(place.get_gramps_id())
    new_place.set_handle(place.get_handle())
    new_place.set_change_time(place.get_change_time())
    new_place.set_longitude(place.get_longitude())
    new_place.set_latitude(place.get_latitude())
    new_place.set_alternate_locations(place.get_alternate_locations())
    new_place.set_name(place.get_name())
    new_place.set_alternative_names(place.get_alternative_names())
    new_place.set_type(place.get_type())
    new_place.set_code(place.get_code())
    new_place.set_placeref_list(place.get_placeref_list())
    new_place.set_tag_list(place.get_tag_list())

    copy_citation_ref_list(db, place, new_place)
    copy_notes(db, place, new_place)
    copy_media_ref_list(db, place, new_place)
    copy_urls(db, place, new_place)

    return new_place


def sanitize_event(db, event):
    """
    Create a new Event instance based off the passed Event
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param event: source Event object that will be copied with
                  privacy records removed
    :type event: Event
    :returns: 'cleansed' Event object
    :rtype: Event
    """
    new_event = Event()

    new_event.set_type(event.get_type())
    new_event.set_description(event.get_description())
    new_event.set_gramps_id(event.get_gramps_id())
    new_event.set_handle(event.get_handle())
    new_event.set_date_object(event.get_date_object())
    new_event.set_change_time(event.get_change_time())
    new_event.set_tag_list(event.get_tag_list())

    copy_citation_ref_list(db, event, new_event)
    copy_notes(db, event, new_event)
    copy_media_ref_list(db, event, new_event)
    copy_attributes(db, event, new_event)

    place_handle = event.get_place_handle()
    if place_handle:
        place = db.get_place_from_handle(place_handle)
        if place and not place.get_privacy():
            new_event.set_place_handle(place_handle)

    return new_event


def sanitize_family(db, family):
    """
    Create a new Family instance based off the passed Family
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param family: source Family object that will be copied with
                   privacy records removed
    :type family: Family
    :returns: 'cleansed' Family object
    :rtype: Family
    """
    new_family = Family()

    new_family.set_gramps_id(family.get_gramps_id())
    new_family.set_handle(family.get_handle())
    new_family.set_relationship(family.get_relationship())
    new_family.set_change_time(family.get_change_time())
    new_family.set_tag_list(family.get_tag_list())

    # Copy the father handle.
    father_handle = family.get_father_handle()
    if father_handle:
        father = db.get_person_from_handle(father_handle)
        if father and not father.get_privacy():
            new_family.set_father_handle(father_handle)

    # Copy the mother handle.
    mother_handle = family.get_mother_handle()
    if mother_handle:
        mother = db.get_person_from_handle(mother_handle)
        if mother and not mother.get_privacy():
            new_family.set_mother_handle(mother_handle)

    # Copy child references.
    for child_ref in family.get_child_ref_list():
        if child_ref and child_ref.get_privacy():
            continue
        child_handle = child_ref.get_reference_handle()
        child = db.get_person_from_handle(child_handle)
        if child and child.get_privacy():
            continue
        # Copy this reference
        new_ref = ChildRef()
        new_ref.set_reference_handle(child_ref.get_reference_handle())
        new_ref.set_father_relation(child_ref.get_father_relation())
        new_ref.set_mother_relation(child_ref.get_mother_relation())
        copy_notes(db, child_ref, new_ref)
        copy_citation_ref_list(db, child_ref, new_ref)
        new_family.add_child_ref(new_ref)

    # Copy event ref list.
    for event_ref in family.get_event_ref_list():
        if event_ref and not event_ref.get_privacy():
            event = db.get_event_from_handle(event_ref.ref)
            if event and not event.get_privacy():
                new_family.add_event_ref(sanitize_event_ref(db, event_ref))

    copy_citation_ref_list(db, family, new_family)
    copy_notes(db, family, new_family)
    copy_media_ref_list(db, family, new_family)
    copy_attributes(db, family, new_family)
    copy_lds_ords(db, family, new_family)

    return new_family


def sanitize_repository(db, repository):
    """
    Create a new Repository instance based off the passed Repository
    instance. The returned instance has all private records
    removed from it.

    :param db: Gramps database to which the Person object belongs
    :type db: DbBase
    :param repository: source Repository object that will be copied with
                       privacy records removed
    :type repository: Repository
    :returns: 'cleansed' Repository object
    :rtype: Repository
    """
    new_repository = Repository()

    new_repository.set_type(repository.get_type())
    new_repository.set_name(repository.get_name())
    new_repository.set_gramps_id(repository.get_gramps_id())
    new_repository.set_handle(repository.get_handle())
    new_repository.set_change_time(repository.get_change_time())
    new_repository.set_tag_list(repository.get_tag_list())

    copy_notes(db, repository, new_repository)
    copy_addresses(db, repository, new_repository)
    copy_urls(db, repository, new_repository)

    return new_repository
