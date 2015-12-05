# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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

""" Interface to Django models """

#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import time
import sys
import pickle
import base64
import collections

#------------------------------------------------------------------------
#
# Django Modules
#
#------------------------------------------------------------------------
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import gramps.webapp.grampsdb.models as models
from gramps.gen.lib import Name
from gramps.gen.utils.id import create_id

# To get a django person from a django database:
#    djperson = dji.Person.get(handle='djhgsdh324hjg234hj24')
#
# To turn the djperson into a Gramps Person:
#    tuple = dji.get_person(djperson)
#    gperson = lib.gen.Person(tuple)
# OR
#    gperson = djangodb.DbDjango().get_person_from_handle(handle)

def check_diff(item, raw):
    encoded = str(base64.encodebytes(pickle.dumps(raw)), "utf-8")
    if item.cache != encoded:
        print("Different:", item.__class__.__name__, item.gramps_id)
        print("raw  :", raw)
        print("cache:", item.from_cache())
        # FIXING, TOO:
        item.save_cache()

#-------------------------------------------------------------------------
#
# Import functions
#
#-------------------------------------------------------------------------
def lookup_role_index(role0, event_ref_list):
    """
    Find the handle in a unserialized event_ref_list and return code.
    """
    if role0 is None:
        return -1
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, erole) = event_ref
            try:
                event = models.Event.objects.get(handle=ref)
            except:
                return -1
            if event.event_type[0] == role0:
                return count
            count += 1
        return -1

def totime(dtime):
    if dtime:
        return int(time.mktime(dtime.timetuple()))
    else:
        return 0

#-------------------------------------------------------------------------
#
# Export functions
#
#-------------------------------------------------------------------------
def todate(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def lookup(index, event_ref_list):
    """
    Get the unserialized event_ref in an list of them and return it.
    """
    if index < 0:
        return None
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            if index == count:
                return ref
            count += 1
        return None

def get_datamap(grampsclass):
    return [x[0] for x in grampsclass._DATAMAP if x[0] != grampsclass.CUSTOM]

#-------------------------------------------------------------------------
#
# Django Interface
#
#-------------------------------------------------------------------------
class DjangoInterface(object):
    """
    DjangoInterface for interoperating between Gramps and Django.

    This interface comes in a number of parts:
        get_ITEMS()
        add_ITEMS()

    get_ITEM(ITEM)

    Given an ITEM from a Django table, construct a Gramps Raw Data tuple.

    add_ITEM(data)

    Given a Gramps Raw Data tuple, add the data to the Django tables.


    """
    def __init__(self):
        self.debug = 0

    def __getattr__(self, name):
        """
        Django Objects database interface.

        >>> self.Person.all()
        >>> self.Person.get(id=1)
        >>> self.Person.get(handle='gh71234dhf3746347734')
        """
        if hasattr(models, name):
            return getattr(models, name).objects
        else:
            raise AttributeError("no such model: '%s'" % name)

    def get_next_id(self, obj, prefix):
        """
        Get next gramps_id

        >>> dji.get_next_id(Person, "P")
        'P0002'
        >>> dji.get_next_id(Media, "M")
        'M2349'
        """
        ids = [o["gramps_id"] for o in obj.objects.values("gramps_id")]
        count = 1
        while "%s%04d" % (prefix, count) in ids:
            count += 1
        return "%s%04d" % (prefix, count)

    def get_model(self, name):
        if hasattr(models, name):
            return getattr(models, name)
        elif hasattr(models, name.title()):
            return getattr(models, name.title())
        else:
            raise AttributeError("no such model: '%s'" % name)

    # -----------------------------------------------
    # Get methods to retrieve list data from the tables
    # -----------------------------------------------

    def clear_tables(self, *args):
        return models.clear_tables(*args)

    def get_tag_list(self, obj):
        return obj.get_tag_list()

    def get_attribute_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        attribute_list = models.Attribute.objects.filter(object_id=obj.id,
                                                     object_type=obj_type)
        return list(map(self.pack_attribute, attribute_list))

    def get_primary_name(self, person):
        names = person.name_set.filter(preferred=True).order_by("order")
        if len(names) > 0:
            return Name.create(self.pack_name(names[0]))
        else:
            return Name()

    def get_alternate_names(self, person):
        names = person.name_set.filter(preferred=False).order_by("order")
        return [Name.create(self.pack_name(n)) for n in names]

    def get_names(self, person, preferred):
        names = person.name_set.filter(preferred=preferred).order_by("order")
        if preferred:
            if len(names) > 0:
                return self.pack_name(names[0])
            else:
                return Name().serialize()
        else:
            return list(map(self.pack_name, names))

    def get_source_attribute_list(self, source):
        return [(map.private, map.key, map.value) for map in source.sourceattribute_set.all().order_by("order")]

    def get_citation_attribute_list(self, citation):
        return [(map.private, map.key, map.value) for map in citation.citationattribute_set.all().order_by("order")]

    def get_media_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        mediarefs = models.MediaRef.objects.filter(object_id=obj.id,
                                               object_type=obj_type)
        return list(map(self.pack_media_ref, mediarefs))

    def get_note_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        noterefs = models.NoteRef.objects.filter(object_id=obj.id,
                                             object_type=obj_type)
        return [noteref.ref_object.handle for noteref in noterefs]

    def get_repository_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        reporefs = models.RepositoryRef.objects.filter(object_id=obj.id,
                                                   object_type=obj_type)
        return list(map(self.pack_repository_ref, reporefs))

    def get_place_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        refs = models.PlaceRef.objects.filter(object_id=obj.id,
                                              object_type=obj_type)
        return list(map(self.pack_place_ref, refs))

    def get_url_list(self, obj):
        return list(map(self.pack_url, obj.url_set.all().order_by("order")))

    def get_address_list(self, obj, with_parish): # person or repository
        addresses = obj.address_set.all().order_by("order")
        return [self.pack_address(address, with_parish)
                    for address in addresses]

    def get_child_ref_list(self, family):
        obj_type = ContentType.objects.get_for_model(family)
        childrefs = models.ChildRef.objects.filter(object_id=family.id,
                                        object_type=obj_type).order_by("order")
        return list(map(self.pack_child_ref, childrefs))

    def get_citation_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        citationrefs = models.CitationRef.objects.filter(object_id=obj.id,
                                                         object_type=obj_type).order_by("order")
        return [citationref.citation.handle for citationref in citationrefs]

    def get_event_refs(self, obj, order="order"):
        obj_type = ContentType.objects.get_for_model(obj)
        eventrefs = models.EventRef.objects.filter(object_id=obj.id,
                                        object_type=obj_type).order_by(order)
        return eventrefs

    def get_event_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        eventrefs = models.EventRef.objects.filter(object_id=obj.id,
                                        object_type=obj_type).order_by("order")
        return list(map(self.pack_event_ref, eventrefs))

    def get_family_list(self, person): # person has families
        return [fam.family.handle for fam in
                models.MyFamilies.objects.filter(person=person).order_by("order")]

    def get_parent_family_list(self, person): # person's parents has families
        return [fam.family.handle for fam in
                models.MyParentFamilies.objects.filter(person=person).order_by("order")]

    def get_person_ref_list(self, person):
        obj_type = ContentType.objects.get_for_model(person)
        return list(map(self.pack_person_ref,
                models.PersonRef.objects.filter(object_id=person.id,
                                            object_type=obj_type)))

    def get_lds_list(self, obj): # person or family
        return list(map(self.pack_lds, obj.lds_set.all().order_by("order")))

    def get_place_handle(self, obj): # obj is event
        if obj.place:
            return obj.place.handle
        return None

    ## Packers:

    def get_event(self, event):
        handle = event.handle
        gid = event.gramps_id
        the_type = tuple(event.event_type)
        description = event.description
        change = totime(event.last_changed)
        private = event.private
        note_list = self.get_note_list(event)
        citation_list = self.get_citation_list(event)
        media_list = self.get_media_list(event)
        attribute_list = self.get_attribute_list(event)
        date = self.get_date(event)
        place_handle = self.get_place_handle(event)
        tag_list = self.get_tag_list(event)
        return (str(handle), gid, the_type, date, description, place_handle,
                citation_list, note_list, media_list, attribute_list,
                change, tag_list, private)

    def get_note_markup(self, note):
        retval = []
        markups = models.Markup.objects.filter(note=note).order_by("order")
        for markup in markups:
            if markup.string and markup.string.isdigit():
                value = int(markup.string)
            else:
                value = markup.string
            start_stop_list  = markup.start_stop_list
            ss_list = eval(start_stop_list)
            retval += [(tuple(markup.styled_text_tag_type), value, ss_list)]
        return retval

    def get_tag(self, tag):
        changed = totime(tag.last_changed)
        return (str(tag.handle),
                tag.name,
                tag.color,
                tag.priority,
                changed)

    def get_note(self, note):
        styled_text = [note.text, self.get_note_markup(note)]
        changed = totime(note.last_changed)
        tag_list = self.get_tag_list(note)
        return (str(note.handle),
                note.gramps_id,
                styled_text,
                note.preformatted,
                tuple(note.note_type),
                changed,
                tag_list,
                note.private)

    def get_family(self, family):
        child_ref_list = self.get_child_ref_list(family)
        event_ref_list = self.get_event_ref_list(family)
        media_list = self.get_media_list(family)
        attribute_list = self.get_attribute_list(family)
        lds_seal_list = self.get_lds_list(family)
        citation_list = self.get_citation_list(family)
        note_list = self.get_note_list(family)
        tag_list = self.get_tag_list(family)
        if family.father:
            father_handle = family.father.handle
        else:
            father_handle = None
        if family.mother:
            mother_handle = family.mother.handle
        else:
            mother_handle = None
        return (str(family.handle), family.gramps_id,
                father_handle, mother_handle,
                child_ref_list, tuple(family.family_rel_type),
                event_ref_list, media_list,
                attribute_list, lds_seal_list,
                citation_list, note_list,
                totime(family.last_changed),
                tag_list,
                family.private)

    def get_repository(self, repository):
        note_list = self.get_note_list(repository)
        address_list = self.get_address_list(repository, with_parish=False)
        url_list = self.get_url_list(repository)
        tag_list = self.get_tag_list(repository)
        return (str(repository.handle),
                repository.gramps_id,
                tuple(repository.repository_type),
                repository.name,
                note_list,
                address_list,
                url_list,
                totime(repository.last_changed),
                tag_list,
                repository.private)

    def get_citation(self, citation):
        note_list = self.get_note_list(citation)
        media_list = self.get_media_list(citation)
        attribute_list = self.get_citation_attribute_list(citation)
        tag_list = self.get_tag_list(citation)
        date = self.get_date(citation)
        # I guess citations can have no source
        if citation.source:
            handle = citation.source.handle
        else:
            handle = None
        return (str(citation.handle),
                citation.gramps_id,
                date,
                citation.page,
                citation.confidence,
                handle,
                note_list,
                media_list,
                attribute_list,
                totime(citation.last_changed),
                tag_list,
                citation.private)

    def get_source(self, source):
        note_list = self.get_note_list(source)
        media_list = self.get_media_list(source)
        attribute_list = self.get_source_attribute_list(source)
        reporef_list = self.get_repository_ref_list(source)
        tag_list = self.get_tag_list(source)
        return (str(source.handle),
                source.gramps_id,
                source.title,
                source.author,
                source.pubinfo,
                note_list,
                media_list,
                source.abbrev,
                totime(source.last_changed),
                attribute_list,
                reporef_list,
                tag_list,
                source.private)

    def get_media(self, media):
        attribute_list = self.get_attribute_list(media)
        citation_list = self.get_citation_list(media)
        note_list = self.get_note_list(media)
        tag_list = self.get_tag_list(media)
        date = self.get_date(media)
        return (str(media.handle),
                media.gramps_id,
                media.path,
                str(media.mime),
                str(media.desc),
                media.checksum,
                attribute_list,
                citation_list,
                note_list,
                totime(media.last_changed),
                date,
                tag_list,
                media.private)

    def get_person(self, person):
        primary_name = self.get_names(person, True) # one
        alternate_names = self.get_names(person, False) # list
        event_ref_list = self.get_event_ref_list(person)
        family_list = self.get_family_list(person)
        parent_family_list = self.get_parent_family_list(person)
        media_list = self.get_media_list(person)
        address_list = self.get_address_list(person, with_parish=False)
        attribute_list = self.get_attribute_list(person)
        url_list = self.get_url_list(person)
        lds_ord_list = self.get_lds_list(person)
        pcitation_list = self.get_citation_list(person)
        pnote_list = self.get_note_list(person)
        person_ref_list = self.get_person_ref_list(person)
        # This looks up the events for the first EventType given:
        death_ref_index = person.death_ref_index
        birth_ref_index = person.birth_ref_index
        tag_list = self.get_tag_list(person)

        return (str(person.handle),
                person.gramps_id,
                tuple(person.gender_type)[0],
                primary_name,
                alternate_names,
                death_ref_index,
                birth_ref_index,
                event_ref_list,
                family_list,
                parent_family_list,
                media_list,
                address_list,
                attribute_list,
                url_list,
                lds_ord_list,
                pcitation_list,
                pnote_list,
                totime(person.last_changed),
                tag_list,
                person.private,
                person_ref_list)

    def get_date(self, obj):
        if ((obj.calendar == obj.modifier == obj.quality == obj.sortval == obj.newyear == 0) and
            obj.text == "" and (not obj.slash1) and (not obj.slash2) and
            (obj.day1 == obj.month1 == obj.year1 == 0) and
            (obj.day2 == obj.month2 == obj.year2 == 0)):
            return None
        elif ((not obj.slash1) and (not obj.slash2) and
            (obj.day2 == obj.month2 == obj.year2 == 0)):
            dateval = (obj.day1, obj.month1, obj.year1, obj.slash1)
        else:
            dateval = (obj.day1, obj.month1, obj.year1, obj.slash1,
                       obj.day2, obj.month2, obj.year2, obj.slash2)
        return (obj.calendar, obj.modifier, obj.quality, dateval,
                obj.text, obj.sortval, obj.newyear)

    def get_placename(self, place):
        placename_date = self.get_date(place)
        placename_value = place.name
        placename_lang = place.lang
        return (placename_value,
                placename_date,
                placename_lang)

    def get_place(self, place):
        locations = place.location_set.all().order_by("order")
        alt_location_list = [self.pack_location(location, True) for location in locations]
        url_list = self.get_url_list(place)
        media_list = self.get_media_list(place)
        citation_list = self.get_citation_list(place)
        note_list = self.get_note_list(place)
        tag_list = self.get_tag_list(place)
        place_ref_list = self.get_place_ref_list(place)
        placename = self.get_placename(place)
        return (str(place.handle),
                place.gramps_id,
                place.title,
                place.long,
                place.lat,
                place_ref_list,
                placename,
                [], ## FIXME: get_alt_names
                tuple(place.place_type),
                place.code,
                alt_location_list,
                url_list,
                media_list,
                citation_list,
                note_list,
                totime(place.last_changed),
                tag_list,
                place.private)

    # ---------------------------------
    # Packers
    # ---------------------------------

    ## The packers build GRAMPS raw unserialized data.

    ## Reference packers

    def pack_child_ref(self, child_ref):
        citation_list = self.get_citation_list(child_ref)
        note_list = self.get_note_list(child_ref)
        return (child_ref.private, citation_list, note_list, child_ref.ref_object.handle,
                tuple(child_ref.father_rel_type), tuple(child_ref.mother_rel_type))

    def pack_person_ref(self, personref):
        citation_list = self.get_citation_list(personref)
        note_list = self.get_note_list(personref)
        return (personref.private,
                citation_list,
                note_list,
                personref.ref_object.handle,
                personref.description)

    def pack_media_ref(self, media_ref):
        citation_list = self.get_citation_list(media_ref)
        note_list = self.get_note_list(media_ref)
        attribute_list = self.get_attribute_list(media_ref)
        if ((media_ref.x1 == media_ref.y1 == media_ref.x2 == media_ref.y2 == -1) or
            (media_ref.x1 == media_ref.y1 == media_ref.x2 == media_ref.y2 == 0)):
            role = None
        else:
            role = (media_ref.x1, media_ref.y1, media_ref.x2, media_ref.y2)
        return (media_ref.private, citation_list, note_list, attribute_list,
                media_ref.ref_object.handle, role)

    def pack_repository_ref(self, repo_ref):
        note_list = self.get_note_list(repo_ref)
        return (note_list,
                repo_ref.ref_object.handle,
                repo_ref.call_number,
                tuple(repo_ref.source_media_type),
                repo_ref.private)

    def pack_place_ref(self, place_ref):
        date = self.get_date(place_ref)
        return (place_ref.ref_object.handle, date)

    def pack_media_ref(self, media_ref):
        note_list = self.get_note_list(media_ref)
        attribute_list = self.get_attribute_list(media_ref)
        citation_list = self.get_citation_list(media_ref)
        return (media_ref.private, citation_list, note_list, attribute_list,
                media_ref.ref_object.handle, (media_ref.x1,
                                              media_ref.y1,
                                              media_ref.x2,
                                              media_ref.y2))

    def pack_event_ref(self, event_ref):
        note_list = self.get_note_list(event_ref)
        attribute_list = self.get_attribute_list(event_ref)
        return (event_ref.private, note_list, attribute_list,
                event_ref.ref_object.handle, tuple(event_ref.role_type))

    def pack_citation(self, citation):
        handle = citation.handle
        gid = citation.gramps_id
        date = self.get_date(citation)
        page = citation.page
        confidence = citation.confidence
        source_handle = citation.source.handle
        note_list = self.get_note_list(citation)
        media_list = self.get_media_list(citation)
        attribute_list = self.get_citation_attribute_list(citation)
        changed = totime(citation.last_changed)
        private = citation.private
        tag_list = self.get_tag_list(citation)
        return (handle, gid, date, page, confidence, source_handle,
                note_list, media_list, attribute_list, changed, tag_list,
                private)

    def pack_address(self, address, with_parish):
        citation_list = self.get_citation_list(address)
        date = self.get_date(address)
        note_list = self.get_note_list(address)
        locations = address.location_set.all().order_by("order")
        if len(locations) > 0:
            location = self.pack_location(locations[0], with_parish)
        else:
            if with_parish:
                location = (("", "", "", "", "", "", ""), "")
            else:
                location = ("", "", "", "", "", "", "")
        return (address.private, citation_list, note_list, date, location)

    def pack_lds(self, lds):
        citation_list = self.get_citation_list(lds)
        note_list = self.get_note_list(lds)
        date = self.get_date(lds)
        if lds.famc:
            famc = lds.famc.handle
        else:
            famc = None
        place_handle = self.get_place_handle(lds)
        return (citation_list, note_list, date, lds.lds_type[0], place_handle,
                famc, lds.temple, lds.status[0], lds.private)

    def pack_source(self, source):
        note_list = self.get_note_list(source)
        media_list = self.get_media_list(source)
        reporef_list = self.get_repository_ref_list(source)
        attribute_list = self.get_source_attribute_list(source)
        tag_list = self.get_tag_list(source)
        return (source.handle, source.gramps_id, source.title,
                source.author, source.pubinfo,
                note_list,
                media_list,
                source.abbrev,
                totime(last_changed), attribute_list,
                reporef_list,
                tag_list,
                source.private)

    def pack_name(self, name):
        citation_list = self.get_citation_list(name)
        note_list = self.get_note_list(name)
        date = self.get_date(name)
        return (name.private, citation_list, note_list, date,
                name.first_name, name.make_surname_list(), name.suffix,
                name.title, tuple(name.name_type),
                name.group_as, name.sort_as.val,
                name.display_as.val, name.call, name.nick,
                name.famnick)

    def pack_location(self, loc, with_parish):
        if with_parish:
            return ((loc.street, loc.locality, loc.city, loc.county, loc.state, loc.country,
                     loc.postal, loc.phone), loc.parish)
        else:
            return (loc.street, loc.locality, loc.city, loc.county, loc.state, loc.country,
                    loc.postal, loc.phone)

    def pack_url(self, url):
        return  (url.private, url.path, url.desc, tuple(url.url_type))

    def pack_attribute(self, attribute):
        citation_list = self.get_citation_list(attribute)
        note_list = self.get_note_list(attribute)
        return (attribute.private,
                citation_list,
                note_list,
                tuple(attribute.attribute_type),
                attribute.value)


    ## Export lists:

    def add_child_ref_list(self, obj, ref_list):
        ## Currently, only Family references children
        for child_data in ref_list:
            self.add_child_ref(obj, child_data)

    def add_citation_list(self, obj, citation_list):
        for citation_handle in citation_list:
            self.add_citation_ref(obj, citation_handle)

    def add_event_ref_list(self, obj, event_ref_list):
        for event_ref in event_ref_list:
            self.add_event_ref(obj, event_ref)

    def add_surname_list(self, name, surname_list):
        order = 1
        for data in surname_list:
            (surname_text, prefix, primary, origin_type,
             connector) = data
            surname = models.Surname()
            surname.surname = surname_text
            surname.prefix = prefix
            surname.primary = primary
            surname.name_origin_type = models.get_type(models.NameOriginType,
                                                       origin_type)
            surname.connector = connector
            surname.name = name
            surname.order = order
            surname.save()
            order += 1

    def add_note_list(self, obj, note_list):
        for handle in note_list:
            # Just the handle
            try:
                note = models.Note.objects.get(handle=handle)
                self.add_note_ref(obj, note)
            except:
                print(("ERROR: Note does not exist: '%s'" %
                                      str(handle)), file=sys.stderr)

    def add_alternate_name_list(self, person, alternate_names):
        for name in alternate_names:
            if name:
                self.add_name(person, name, False)

    def add_parent_family_list(self, person, parent_family_list):
        for parent_family_data in parent_family_list:
            self.add_parent_family(person, parent_family_data)

    def add_media_ref_list(self, person, media_list):
        for media_data in media_list:
            self.add_media_ref(person, media_data)

    def add_attribute_list(self, obj, attribute_list):
        for attribute_data in attribute_list:
            self.add_attribute(obj, attribute_data)

    def add_tag_list(self, obj, tag_list):
        for tag_handle in tag_list:
            try:
                tag = models.Tag.objects.get(handle=tag_handle)
            except:
                print(("ERROR: Tag does not exist: '%s'" %
                                      str(tag_handle)), file=sys.stderr)
            obj.tags.add(tag)

    def add_url_list(self, field, obj, url_list):
        if not url_list: return None
        count = 1
        for url_data in url_list:
            self.add_url(field, obj, url_data, count)
            count += 1

    def add_person_ref_list(self, obj, person_ref_list):
        for person_ref_data in person_ref_list:
            self.add_person_ref(obj, person_ref_data)

    def add_address_list(self, field, obj, address_list):
        count = 1
        for address_data in address_list:
            self.add_address(field, obj, address_data, count)
            count += 1

    def add_lds_list(self, field, obj, lds_ord_list):
        count = 1
        for ldsord in lds_ord_list:
            lds = self.add_lds(field, obj, ldsord, count)
            #obj.lds_list.add(lds)
            #obj.save()
            count += 1

    def add_repository_ref_list(self, obj, reporef_list):
        for data in reporef_list:
            self.add_repository_ref(obj, data)

    def add_place_ref_list(self, obj, placeref_list):
        for data in placeref_list:
            self.add_place_ref(obj, data)

    def add_family_ref_list(self, person, family_list):
        for family_handle in family_list:
            self.add_family_ref(person, family_handle)

    def add_alt_name_list(self, place, alt_name_list):
        print("FIXME: add alt_name_list!", alt_name_list)

    ## Export reference objects:

    def add_person_ref_default(self, obj, person, private=False, desc=None):
        count = person.references.count()
        person_ref = models.PersonRef(referenced_by=obj,
                                  ref_object=person,
                                  private=private,
                                  order=count + 1,
                                  description=desc)
        person_ref.save()

    def add_person_ref(self, obj, person_ref_data):
        (private,
         citation_list,
         note_list,
         handle,
         desc) = person_ref_data
        try:
            person = models.Person.objects.get(handle=handle)
        except:
            print(("ERROR: Person does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return

        count = person.references.count()
        person_ref = models.PersonRef(referenced_by=obj,
                                  ref_object=person,
                                  private=private,
                                  order=count + 1,
                                  description=desc)
        person_ref.save()
        self.add_note_list(person_ref, note_list)
        self.add_citation_list(person_ref, citation_list)

    def add_note_ref(self, obj, note):
        count = note.references.count()
        note_ref = models.NoteRef(referenced_by=obj,
                              ref_object=note,
                              private=False,
                              order=count + 1)
        note_ref.save()

    def add_media_ref_default(self, obj, media, private=False, role=None):
        count = media.references.count()
        if not role:
            role = (0,0,0,0)
        media_ref = models.MediaRef(referenced_by=obj,
                                ref_object=media,
                                x1=role[0],
                                y1=role[1],
                                x2=role[2],
                                y2=role[3],
                                private=private,
                                order=count + 1)
        media_ref.save()

    def add_media_ref(self, obj, media_ref_data):
        (private, citation_list, note_list, attribute_list,
         ref, role) = media_ref_data
        try:
            media = models.Media.objects.get(handle=ref)
        except:
            print(("ERROR: Media does not exist: '%s'" %
                                  str(ref)), file=sys.stderr)
            return
        count = media.references.count()
        if not role:
            role = (0,0,0,0)
        media_ref = models.MediaRef(referenced_by=obj,
                                ref_object=media,
                                x1=role[0],
                                y1=role[1],
                                x2=role[2],
                                y2=role[3],
                                private=private,
                                order=count + 1)
        media_ref.save()
        self.add_note_list(media_ref, note_list)
        self.add_attribute_list(media_ref, attribute_list)
        self.add_citation_list(media_ref, citation_list)

    def add_citation_ref_default(self, obj, citation, private=False):
        object_type = ContentType.objects.get_for_model(obj)
        count = models.CitationRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        citation_ref = models.CitationRef(private=private,
                                          referenced_by=obj,
                                          citation=citation,
                                          order=count + 1)
        citation_ref.save()

    def add_citation_ref(self, obj, handle):
        try:
            citation = models.Citation.objects.get(handle=handle)
        except:
            print(("ERROR: Citation does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return

        object_type = ContentType.objects.get_for_model(obj)
        count = models.CitationRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        citation_ref = models.CitationRef(private=False,
                                          referenced_by=obj,
                                          citation=citation,
                                          order=count + 1)
        citation_ref.save()

    def add_citation(self, citation_data):
        (handle, gid, date, page, confidence, source_handle, note_list,
         media_list, attribute_list, changed, tag_list, private) = citation_data
        citation = models.Citation(
            handle=handle,
            gramps_id=gid,
            private=private,
            last_changed=todate(changed),
            confidence=confidence,
            page=page)
        citation.save(save_cache=False)

    def add_citation_detail(self, citation_data):
        (handle, gid, date, page, confidence, source_handle, note_list,
         media_list, attribute_list, change, tag_list, private) = citation_data
        try:
            citation = models.Citation.objects.get(handle=handle)
        except:
            print(("ERROR: Citation does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        try:
            source = models.Source.objects.get(handle=source_handle)
        except:
            print(("ERROR: Source does not exist: '%s'" %
                                  str(source_handle)), file=sys.stderr)
            return
        citation.source = source
        self.add_date(citation, date)
        citation.save(save_cache=False)
        self.add_note_list(citation, note_list)
        self.add_media_ref_list(citation, media_list)
        self.add_citation_attribute_list(citation, attribute_list)
        self.add_tag_list(citation, tag_list)
        citation.save_cache()

    def add_child_ref_default(self, obj, child, frel=1, mrel=1, private=False):
        object_type = ContentType.objects.get_for_model(obj) # obj is family
        count = models.ChildRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        child_ref = models.ChildRef(private=private,
                                referenced_by=obj,
                                ref_object=child,
                                order=count + 1,
                                father_rel_type=models.get_type(models.ChildRefType, frel),  # birth
                                mother_rel_type=models.get_type(models.ChildRefType, mrel))
        child_ref.save()

    def add_child_ref(self, obj, data):
        (private, citation_list, note_list, ref, frel, mrel) = data
        try:
            child = models.Person.objects.get(handle=ref)
        except:
            print(("ERROR: Person does not exist: '%s'" %
                                  str(ref)), file=sys.stderr)
            return
        object_type = ContentType.objects.get_for_model(obj)
        count = models.ChildRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        child_ref = models.ChildRef(private=private,
                                referenced_by=obj,
                                ref_object=child,
                                order=count + 1,
                                father_rel_type=models.get_type(models.ChildRefType, frel),
                                mother_rel_type=models.get_type(models.ChildRefType, mrel))
        child_ref.save()
        self.add_citation_list(child_ref, citation_list)
        self.add_note_list(child_ref, note_list)

    def add_event_ref_default(self, obj, event, private=False, role=models.EventRoleType._DEFAULT):
        object_type = ContentType.objects.get_for_model(obj)
        count = models.EventRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        event_ref = models.EventRef(private=private,
                                referenced_by=obj,
                                ref_object=event,
                                order=count + 1,
                                role_type = models.get_type(models.EventRoleType, role))
        event_ref.save()

    def add_event_ref(self, obj, event_data):
        (private, note_list, attribute_list, ref, role) = event_data
        try:
            event = models.Event.objects.get(handle=ref)
        except:
            print(("ERROR: Event does not exist: '%s'" %
                                  str(ref)), file=sys.stderr)
            return
        object_type = ContentType.objects.get_for_model(obj)
        count = models.EventRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        event_ref = models.EventRef(private=private,
                                referenced_by=obj,
                                ref_object=event,
                                order=count + 1,
                                role_type = models.get_type(models.EventRoleType, role))
        event_ref.save()
        self.add_note_list(event_ref, note_list)
        self.add_attribute_list(event_ref, attribute_list)

    def add_repository_ref_default(self, obj, repository, private=False, call_number="",
                                   source_media_type=models.SourceMediaType._DEFAULT):
        object_type = ContentType.objects.get_for_model(obj)
        count = models.RepositoryRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        repos_ref = models.RepositoryRef(private=private,
                                         referenced_by=obj,
                                         call_number=call_number,
                                         source_media_type=models.get_type(models.SourceMediaType,
                                                                           source_media_type),
                                         ref_object=repository,
                                         order=count + 1)
        repos_ref.save()

    def add_repository_ref(self, obj, reporef_data):
        (note_list,
         ref,
         call_number,
         source_media_type,
         private) = reporef_data
        try:
            repository = models.Repository.objects.get(handle=ref)
        except:
            print(("ERROR: Repository does not exist: '%s'" %
                                  str(ref)), file=sys.stderr)
            return
        object_type = ContentType.objects.get_for_model(obj)
        count = models.RepositoryRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        repos_ref = models.RepositoryRef(private=private,
                                     referenced_by=obj,
                                     call_number=call_number,
                                     source_media_type=models.get_type(models.SourceMediaType,
                                                                source_media_type),
                                     ref_object=repository,
                                     order=count + 1)
        repos_ref.save()
        self.add_note_list(repos_ref, note_list)

    def add_family_ref(self, obj, handle):
        try:
            family = models.Family.objects.get(handle=handle)
        except:
            print(("ERROR: Family does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        #obj.families.add(family)
        pfo = models.MyFamilies(person=obj, family=family,
                                order=len(models.MyFamilies.objects.filter(person=obj)) + 1)
        pfo.save()
        obj.save()

    ## Export individual objects:

    def add_source_attribute_list(self, source, attribute_list):
        ## FIXME: dict to list
        count = 1
        #for key in datamap_dict:
        #    value = datamap_dict[key]
        #    datamap = models.SourceDatamap(key=key, value=value, order=count)
        #    datamap.source = source
        #    datamap.save()
        #    count += 1

    def add_citation_attribute_list(self, citation, attribute_list):
        ## FIXME: dict to list
        count = 1
        #for key in datamap_dict:
        #    value = datamap_dict[key]
        #    datamap = models.CitationDatamap(key=key, value=value, order=count)
        #    datamap.citation = citation
        #    datamap.save()
        #    count += 1

    def add_lds(self, field, obj, data, order):
        (lcitation_list, lnote_list, date, type, place_handle,
         famc_handle, temple, status, private) = data
        if place_handle:
            try:
                place = models.Place.objects.get(handle=place_handle)
            except:
                print(("ERROR: Place does not exist: '%s'" %
                                      str(place_handle)), file=sys.stderr)
                place = None
        else:
            place = None
        if famc_handle:
            try:
                famc = models.Family.objects.get(handle=famc_handle)
            except:
                print(("ERROR: Family does not exist: '%s'" %
                                      str(famc_handle)), file=sys.stderr)
                famc = None
        else:
            famc = None
        lds = models.Lds(lds_type = models.get_type(models.LdsType, type),
                     temple=temple,
                     place=place,
                     famc=famc,
                     order=order,
                     status = models.get_type(models.LdsStatus, status),
                     private=private)
        self.add_date(lds, date)
        lds.save()
        self.add_note_list(lds, lnote_list)
        self.add_citation_list(lds, lcitation_list)
        if field == "person":
            lds.person = obj
        elif field == "family":
            lds.family = obj
        else:
            raise AttributeError("invalid field '%s' to attach lds" %
                                 str(field))
        lds.save()
        return lds

    def add_address(self, field, obj, address_data, order):
        (private, acitation_list, anote_list, date, location) = address_data
        address = models.Address(private=private, order=order)
        self.add_date(address, date)
        address.save()
        self.add_location("address", address, location, 1)
        self.add_note_list(address, anote_list)
        self.add_citation_list(address, acitation_list)
        if field == "person":
            address.person = obj
        elif field == "repository":
            address.repository = obj
        else:
            raise AttributeError("invalid field '%s' to attach address" %
                                 str(field))
        address.save()
        #obj.save()
        #obj.addresses.add(address)
        #obj.save()

    def add_attribute(self, obj, attribute_data):
        (private, citation_list, note_list, the_type, value) = attribute_data
        attribute_type = models.get_type(models.AttributeType, the_type)
        attribute = models.Attribute(private=private,
                                 attribute_of=obj,
                                 attribute_type=attribute_type,
                                 value=value)
        attribute.save()
        self.add_citation_list(attribute, citation_list)
        self.add_note_list(attribute, note_list)
        #obj.attributes.add(attribute)
        #obj.save()

    def add_url(self, field, obj, url_data, order):
        (private, path, desc, type) = url_data
        url = models.Url(private=private,
                     path=path,
                     desc=desc,
                     order=order,
                     url_type=models.get_type(models.UrlType, type))
        if field == "person":
            url.person = obj
        elif field == "repository":
            url.repository = obj
        elif field == "place":
            url.place = obj
        else:
            raise AttributeError("invalid field '%s' to attach to url" %
                                 str(field))
        url.save()
        #obj.url_list.add(url)
        #obj.save()

    def add_place_ref_default(self, obj, place, date=None):
        count = place.references.count()
        object_type = ContentType.objects.get_for_model(obj)
        count = models.PlaceRef.objects.filter(object_id=obj.id,
                                               object_type=object_type).count()
        place_ref = models.PlaceRef(referenced_by=obj,
                                    ref_object=place,
                                    order=count + 1)
        self.add_date(obj, date)
        place_ref.save()

    def add_place_ref(self, obj, data):
        place_handle, date = data
        if place_handle:
            try:
                place = models.Place.objects.get(handle=place_handle)
            except:
                print(("ERROR: Place does not exist: '%s'" % str(place_handle)), file=sys.stderr)
                #from gramps.gen.utils.debug import format_exception
                #print("".join(format_exception()), file=sys.stderr)
                return
        object_type = ContentType.objects.get_for_model(obj)
        count = models.PlaceRef.objects.filter(object_id=obj.id,object_type=object_type).count()
        place_ref = models.PlaceRef(referenced_by=obj, ref_object=place, order=count + 1)
        place_ref.save()
        self.add_date(place_ref, date)

    def add_parent_family(self, person, parent_family_handle):
        try:
            family = models.Family.objects.get(handle=parent_family_handle)
        except:
            print(("ERROR: Family does not exist: '%s'" %
                                  str(parent_family_handle)), file=sys.stderr)
            return
        #person.parent_families.add(family)
        pfo = models.MyParentFamilies(
            person=person,
            family=family,
            order=len(models.MyParentFamilies.objects.filter(person=person)) + 1)
        pfo.save()
        person.save()

    def add_date(self, obj, date):
        if date is None:
            (calendar, modifier, quality, text, sortval, newyear) = \
                (0, 0, 0, "", 0, 0)
            day1, month1, year1, slash1 = 0, 0, 0, 0
            day2, month2, year2, slash2 = 0, 0, 0, 0
        else:
            (calendar, modifier, quality, dateval, text, sortval, newyear) = date
            if len(dateval) == 4:
                day1, month1, year1, slash1 = dateval
                day2, month2, year2, slash2 = 0, 0, 0, 0
            elif len(dateval) == 8:
                day1, month1, year1, slash1, day2, month2, year2, slash2 = dateval
            else:
                raise AttributeError("ERROR: dateval format '%s'" % str(dateval))
        obj.calendar = calendar
        obj.modifier = modifier
        obj.quality = quality
        obj.text = text
        obj.sortval = sortval
        obj.newyear = newyear
        obj.day1 = day1
        obj.month1 = month1
        obj.year1 = year1
        obj.slash1 = slash1
        obj.day2 = day2
        obj.month2 = month2
        obj.year2 = year2
        obj.slash2 = slash2

    def add_name(self, person, data, preferred):
        if data:
            (private, citation_list, note_list, date,
             first_name, surname_list, suffix, title,
             name_type, group_as, sort_as,
             display_as, call, nick, famnick) = data

            count = person.name_set.count()
            name = models.Name()
            name.order = count + 1
            name.preferred = preferred
            name.private = private
            name.first_name = first_name
            name.suffix = suffix
            name.title = title
            name.name_type = models.get_type(models.NameType, name_type)
            name.group_as = group_as
            name.sort_as = models.get_type(models.NameFormatType, sort_as)
            name.display_as = models.get_type(models.NameFormatType, display_as)
            name.call = call
            name.nick = nick
            name.famnick = famnick
            # we know person exists
            # needs to have an ID for key
            name.person = person
            self.add_date(name, date)
            name.save()
            self.add_surname_list(name, surname_list)
            self.add_note_list(name, note_list)
            self.add_citation_list(name, citation_list)
            #person.save()

    ## Export primary objects:

    def add_person(self, data):
        # Unpack from the BSDDB:
        (handle,        #  0
         gid,          #  1
         gender,             #  2
         primary_name,       #  3
         alternate_names,    #  4
         death_ref_index,    #  5
         birth_ref_index,    #  6
         event_ref_list,     #  7
         family_list,        #  8
         parent_family_list, #  9
         media_list,         # 10
         address_list,       # 11
         attribute_list,     # 12
         url_list,               # 13
         lds_ord_list,       # 14
         pcitation_list,       # 15
         pnote_list,         # 16
         change,             # 17
         tag_list,             # 18
         private,           # 19
         person_ref_list,    # 20
         ) = data

        person = models.Person(handle=handle,
                            gramps_id=gid,
                            last_changed=todate(change),
                            private=private,
                            gender_type=models.get_type(models.GenderType, gender))
        person.save(save_cache=False)

    def add_person_detail(self, data):
        # Unpack from the BSDDB:
        (handle,        #  0
         gid,          #  1
         gender,             #  2
         primary_name,       #  3
         alternate_names,    #  4
         death_ref_index,    #  5
         birth_ref_index,    #  6
         event_ref_list,     #  7
         family_list,        #  8
         parent_family_list, #  9
         media_list,         # 10
         address_list,       # 11
         attribute_list,     # 12
         url_list,               # 13
         lds_ord_list,       # 14
         pcitation_list,       # 15
         pnote_list,         # 16
         change,             # 17
         tag_list,             # 18
         private,           # 19
         person_ref_list,    # 20
         ) = data

        try:
            person = models.Person.objects.get(handle=handle)
        except:
            print(("ERROR: Person does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        if primary_name:
            self.add_name(person, primary_name, True)
        self.add_alternate_name_list(person, alternate_names)
        self.add_event_ref_list(person, event_ref_list)
        self.add_family_ref_list(person, family_list)
        self.add_parent_family_list(person, parent_family_list)
        self.add_media_ref_list(person, media_list)
        self.add_note_list(person, pnote_list)
        self.add_attribute_list(person, attribute_list)
        self.add_url_list("person", person, url_list)
        self.add_person_ref_list(person, person_ref_list)
        self.add_citation_list(person, pcitation_list)
        self.add_address_list("person", person, address_list)
        self.add_lds_list("person", person, lds_ord_list)
        self.add_tag_list(person, tag_list)
        # set person.birth and birth.death to correct events:

        obj_type = ContentType.objects.get_for_model(person)
        events = models.EventRef.objects.filter(
            object_id=person.id,
            object_type=obj_type,
            ref_object__event_type__val=models.EventType.BIRTH).order_by("order")

        all_events = self.get_event_ref_list(person)
        if events:
            person.birth = events[0].ref_object
            person.birth_ref_index = lookup_role_index(models.EventType.BIRTH, all_events)

        events = models.EventRef.objects.filter(
            object_id=person.id,
            object_type=obj_type,
            ref_object__event_type__val=models.EventType.DEATH).order_by("order")
        if events:
            person.death = events[0].ref_object
            person.death_ref_index = lookup_role_index(models.EventType.DEATH, all_events)
        person.save()
        return person

    def save_note_markup(self, note, markup_list):
        # delete any prexisting markup:
        models.Markup.objects.filter(note=note).delete()
        count = 1
        for markup in markup_list:
            markup_code, value, start_stop_list = markup
            m = models.Markup(
                note=note,
                order=count,
                styled_text_tag_type=models.get_type(models.StyledTextTagType,
                                                     markup_code,
                                                     get_or_create=False),
                string=value,
                start_stop_list=str(start_stop_list))
            m.save()

    def add_note(self, data):
        # Unpack from the BSDDB:
        (handle, gid, styled_text, format, note_type,
         change, tag_list, private) = data
        text, markup_list = styled_text
        n = models.Note(handle=handle,
                        gramps_id=gid,
                        last_changed=todate(change),
                        private=private,
                        preformatted=format,
                        text=text,
                        note_type=models.get_type(models.NoteType, note_type))
        n.save(save_cache=False)
        self.save_note_markup(n, markup_list)

    def add_note_detail(self, data):
        # Unpack from the BSDDB:
        (handle, gid, styled_text, format, note_type,
         change, tag_list, private) = data
        note = models.Note.objects.get(handle=handle)
        note.save(save_cache=False)
        self.add_tag_list(note, tag_list)
        note.save_cache()

    def add_family(self, data):
        # Unpack from the BSDDB:
        (handle, gid, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, citation_list, note_list,
         change, tag_list, private) = data

        family = models.Family(handle=handle, gramps_id=gid,
                               family_rel_type = models.get_type(models.FamilyRelType, the_type),
                               last_changed=todate(change),
                               private=private)
        family.save(save_cache=False)

    def add_family_detail(self, data):
        # Unpack from the BSDDB:
        (handle, gid, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, citation_list, note_list,
         change, tag_list, private) = data

        try:
            family = models.Family.objects.get(handle=handle)
        except:
            print(("ERROR: Family does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        # father_handle and/or mother_handle can be None
        if father_handle:
            try:
                family.father = models.Person.objects.get(handle=father_handle)
            except:
                print(("ERROR: Father does not exist: '%s'" %
                                      str(father_handle)), file=sys.stderr)
                family.father = None
        if mother_handle:
            try:
                family.mother = models.Person.objects.get(handle=mother_handle)
            except:
                print(("ERROR: Mother does not exist: '%s'" %
                                      str(mother_handle)), file=sys.stderr)
                family.mother = None
        family.save(save_cache=False)
        self.add_child_ref_list(family, child_ref_list)
        self.add_note_list(family, note_list)
        self.add_attribute_list(family, attribute_list)
        self.add_citation_list(family, citation_list)
        self.add_media_ref_list(family, media_list)
        self.add_event_ref_list(family, event_ref_list)
        self.add_lds_list("family", family, lds_seal_list)
        self.add_tag_list(family, tag_list)
        family.save_cache()

    def add_source(self, data):
        (handle, gid, title,
         author, pubinfo,
         note_list,
         media_list,
         abbrev,
         change, attribute_list,
         reporef_list,
         tag_list,
         private) = data
        source = models.Source(handle=handle, gramps_id=gid, title=title,
                               author=author, pubinfo=pubinfo, abbrev=abbrev,
                               last_changed=todate(change), private=private)
        source.save(save_cache=False)

    def add_source_detail(self, data):
        (handle, gid, title,
         author, pubinfo,
         note_list,
         media_list,
         abbrev,
         change, attribute_list,
         reporef_list,
         tag_list,
         private) = data
        try:
            source = models.Source.objects.get(handle=handle)
        except:
            print(("ERROR: Source does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        source.save(save_cache=False)
        self.add_note_list(source, note_list)
        self.add_media_ref_list(source, media_list)
        self.add_source_attribute_list(source, attribute_list)
        self.add_repository_ref_list(source, reporef_list)
        self.add_tag_list(source, tag_list)
        source.save_cache()

    def add_repository(self, data):
        (handle, gid, the_type, name, note_list,
         address_list, url_list, change, tag_list, private) = data

        repository = models.Repository(handle=handle,
                                       gramps_id=gid,
                                       last_changed=todate(change),
                                       private=private,
                                       repository_type=models.get_type(models.RepositoryType, the_type),
                                       name=name)
        repository.save(save_cache=False)

    def add_repository_detail(self, data):
        (handle, gid, the_type, name, note_list,
         address_list, url_list, change, tag_list, private) = data
        try:
            repository = models.Repository.objects.get(handle=handle)
        except:
            print(("ERROR: Repository does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        repository.save(save_cache=False)
        self.add_note_list(repository, note_list)
        self.add_url_list("repository", repository, url_list)
        self.add_address_list("repository", repository, address_list)
        self.add_tag_list(repository, tag_list)
        repository.save_cache()

    def add_location(self, field, obj, location_data, order):
        # location now has 8 items
        # street, locality, city, county, state,
        # country, postal, phone, parish

        if location_data == None: return
        if len(location_data) == 8:
            (street, locality, city, county, state, country, postal, phone) = location_data
            parish = None
        elif len(location_data) == 2:
            ((street, locality, city, county, state, country, postal, phone), parish) = location_data
        else:
            print(("ERROR: unknown location: '%s'" %
                                  str(location_data)), file=sys.stderr)
            (street, locality, city, county, state, country, postal, phone, parish) = \
                ("", "", "", "", "", "", "", "", "")
        location = models.Location(street = street,
                                   locality = locality,
                               city = city,
                               county = county,
                               state = state,
                               country = country,
                               postal = postal,
                               phone = phone,
                               parish = parish,
                               order = order)
        if field == "address":
            location.address = obj
        elif field == "place":
            location.place = obj
        else:
            raise AttributeError("invalid field '%s' to attach to location" %
                                 str(field))
        location.save()
        #obj.locations.add(location)
        #obj.save()

    def add_place(self, data):
        ## ('cef246c95c132bcf6a0255d4d17', 'P0036', ('Santa Clara Co., CA, USA', DATE, "English"),
        ## '', '', [('cef243fb5634559442323368f63', None)], 'Santa Clara Co.', [], (3, ''), '', [], [], [], [], [], 1422124781, [], False)
        (handle, gid, title, long, lat,
         place_ref_list,
         (placename, date, placelang),
         alt_name_list,
         place_type,
         code,
         alt_location_list,
         url_list,
         media_list,
         citation_list,
         note_list,
         change,
         tag_list,
         private) = data
        place = models.Place(
            handle=handle,
            gramps_id=gid,
            title=title,
            long=long,
            lat=lat,
            name=placename,
            lang=placelang,
            place_type=models.get_type(models.PlaceType, place_type),
            code=code,
            last_changed=todate(change),
            private=private)
        try:
            place.save(save_cache=False)
        except:
            print("FIXME: error in saving place")

    def add_place_detail(self, data):
        (handle, gid, title, long, lat,
         place_ref_list,
         (placename, date, placelang),
         alt_name_list,
         place_type,
         code,
         alt_location_list,
         url_list,
         media_list,
         citation_list,
         note_list,
         change,
         tag_list,
         private) = data
        try:
            place = models.Place.objects.get(handle=handle)
        except:
            print(("ERROR: Place does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        self.add_date(place, date)
        place.save(save_cache=False)
        self.add_url_list("place", place, url_list)
        self.add_media_ref_list(place, media_list)
        self.add_citation_list(place, citation_list)
        self.add_note_list(place, note_list)
        self.add_tag_list(place, tag_list)
        self.add_place_ref_list(place, place_ref_list)
        self.add_alt_name_list(place, alt_name_list)
        count = 1
        for loc_data in alt_location_list:
            self.add_location("place", place, loc_data, count)
            count + 1
        place.save_cache()

    def add_tag(self, data):
        (handle,
         name,
         color,
         priority,
         change) = data
        tag = models.Tag(handle=handle,
                         gramps_id=create_id(),
                         name=name,
                         color=color,
                         priority=priority,
                         last_changed=todate(change))
        tag.save(save_cache=False)

    def add_tag_detail(self, data):
        (handle,
         name,
         color,
         priority,
         change) = data
        tag = models.Tag.objects.get(handle=handle)
        tag.save()

    def add_media(self, data):
        (handle, gid, path, mime, desc,
         checksum,
         attribute_list,
         citation_list,
         note_list,
         change,
         date,
         tag_list,
         private) = data
        media = models.Media(handle=handle, gramps_id=gid,
                             path=path, mime=mime, checksum=checksum,
                             desc=desc, last_changed=todate(change),
                             private=private)
        self.add_date(media, date)
        media.save(save_cache=False)

    def add_media_detail(self, data):
        (handle, gid, path, mime, desc,
         checksum,
         attribute_list,
         citation_list,
         note_list,
         change,
         date,
         tag_list,
         private) = data
        try:
            media = models.Media.objects.get(handle=handle)
        except:
            print(("ERROR: Media does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        media.save(save_cache=False)
        self.add_note_list(media, note_list)
        self.add_citation_list(media, citation_list)
        self.add_attribute_list(media, attribute_list)
        self.add_tag_list(media, tag_list)
        media.save_cache()

    def add_event(self, data):
        (handle, gid, the_type, date, description, place_handle,
         citation_list, note_list, media_list, attribute_list,
         change, tag_list, private) = data
        event = models.Event(handle=handle,
                             gramps_id=gid,
                             event_type=models.get_type(models.EventType, the_type),
                             private=private,
                             description=description,
                             last_changed=todate(change))
        self.add_date(event, date)
        event.save(save_cache=False)

    def add_event_detail(self, data):
        (handle, gid, the_type, date, description, place_handle,
         citation_list, note_list, media_list, attribute_list,
         change, tag_list, private) = data
        try:
            event = models.Event.objects.get(handle=handle)
        except:
            print(("ERROR: Event does not exist: '%s'" %
                                  str(handle)), file=sys.stderr)
            return
        try:
            place = models.Place.objects.get(handle=place_handle)
        except:
            place = None
            print(("ERROR: Place does not exist: '%s'" %
                                  str(place_handle)), file=sys.stderr)
        event.place = place
        event.save(save_cache=False)
        self.add_note_list(event, note_list)
        self.add_attribute_list(event, attribute_list)
        self.add_media_ref_list(event, media_list)
        self.add_citation_list(event, citation_list)
        self.add_tag_list(event, tag_list)
        event.save_cache()

    def get_raw(self, item):
        """
        Build and return the raw, serialized data of an object.
        """
        if isinstance(item, models.Person):
            raw = self.get_person(item)
        elif isinstance(item, models.Family):
            raw = self.get_family(item)
        elif isinstance(item, models.Place):
            raw = self.get_place(item)
        elif isinstance(item, models.Media):
            raw = self.get_media(item)
        elif isinstance(item, models.Source):
            raw = self.get_source(item)
        elif isinstance(item, models.Citation):
            raw = self.get_citation(item)
        elif isinstance(item, models.Repository):
            raw = self.get_repository(item)
        elif isinstance(item, models.Note):
            raw = self.get_note(item)
        elif isinstance(item, models.Event):
            raw = self.get_event(item)
        else:
            raise Exception("Don't know how to get raw '%s'" % type(item))
        return raw

    def check_caches(self, callback=None):
        """
        Call this to check the caches for all primary models.
        """
        if not isinstance(callback, collections.Callable):
            callback = lambda percent: None # dummy

        callback(0)
        count = 0.0
        total = (self.Note.all().count() +
                 self.Person.all().count() +
                 self.Event.all().count() +
                 self.Family.all().count() +
                 self.Repository.all().count() +
                 self.Place.all().count() +
                 self.Media.all().count() +
                 self.Source.all().count() +
                 self.Citation.all().count() +
                 self.Tag.all().count())

        for item in self.Note.all():
            raw = self.get_note(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Person.all():
            raw = self.get_person(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Family.all():
            raw = self.get_family(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Source.all():
            raw = self.get_source(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Event.all():
            raw = self.get_event(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Repository.all():
            raw = self.get_repository(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Place.all():
            raw = self.get_place(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Media.all():
            raw = self.get_media(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Citation.all():
            raw = self.get_citation(item)
            check_diff(item, raw)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Tag.all():
            raw = self.get_tag(item)
            check_diff(item, raw)
            count += 1
        callback(100)

    def check_families(self):
        """
        Check family structures.
        """
        for family in self.Family.all():
            if family.mother:
                if not family in family.mother.families.all():
                    print("Mother not in family", mother, family)
            if family.father:
                if not family in family.father.families.all():
                    print("Father not in family", mother, family)
            for child in family.get_children():
                if family not in child.parent_families.all():
                    print("Child not in family", child, family)
        for person in self.Person.all():
            for family in person.families.all():
                if person not in [family.mother, family.father]:
                    print("Spouse not in family", person, family)
            for family in person.parent_families.all():
                if person not in family.get_children():
                    print("Child not in family", person, family)

    def is_public(self, obj, objref):
        """
        Returns whether or not an item is "public", and the reason
        why/why not.

        @param obj - an instance of any Primary object
        @param objref - one of the PrimaryRef.objects
        @return - a tuple containing a boolean (public?) and reason.

        There are three reasons why an item might not be public:
           1) The item itself is private.
           2) The item is referenced by a living Person.
           3) The item is referenced by some other private item.
        """
        # If it is private, then no:
        if obj.private:
            return (False, "It is marked private.")
        elif hasattr(obj, "probably_alive") and obj.probably_alive:
            return (False, "It is marked probaby alive.")
        elif hasattr(obj, "mother") and obj.mother:
            public, reason = self.is_public(obj.mother, self.PersonRef)
            if not public:
                return public, reason
        elif hasattr(obj, "father") and obj.father:
            public, reason = self.is_public(obj.father, self.PersonRef)
            if not public:
                return public, reason
        # FIXME: what about Associations... anything else? Check PrivateProxy
        if objref:
            if hasattr(objref.model, "ref_object"):
                obj_ref_list = objref.filter(ref_object=obj)
            elif hasattr(objref.model, "citation"):
                obj_ref_list = objref.filter(citation=obj)
            else:
                raise Exception("objref '%s' needs a ref for '%s'" % (objref.model, obj))
            for reference in obj_ref_list:
                ref_from_class = reference.object_type.model_class()
                item = None
                try:
                    item = ref_from_class.objects.get(id=reference.object_id)
                except:
                    print("Warning: Corrupt reference: %s" % str(reference))
                    continue
                # If it is linked to by someone alive? public = False
                if hasattr(item, "probably_alive") and item.probably_alive:
                    return (False, "It is referenced by someone who is probaby alive.")
                # If it is linked to by something private? public = False
                elif item.private:
                    return (False, "It is referenced by an item which is marked private.")
        return (True, "It is visible to the public.")

    def update_public(self, obj, save=True):
        """
        >>> dji.update_public(event)

        Given an Event or other instance, update the event's public
        status, or any event referenced to by the instance.

        For example, if a person is found to be alive, then the
        referenced events should be marked not public (public = False).

        """
        from gramps.webapp.utils import probably_alive
        if obj.__class__.__name__ == "Event":
            objref = self.EventRef
        elif obj.__class__.__name__ == "Person":
            objref = self.PersonRef
        elif obj.__class__.__name__ == "Note":
            objref = self.NoteRef
        elif obj.__class__.__name__ == "Repository":
            objref = self.RepositoryRef
        elif obj.__class__.__name__ == "Citation":
            objref = self.CitationRef
        elif obj.__class__.__name__ == "Media":
            objref = self.MediaRef
        elif  obj.__class__.__name__ == "Place": # no need for dependency
            objref = None
        elif  obj.__class__.__name__ == "Source": # no need for dependency
            objref = None
        elif  obj.__class__.__name__ == "Family":
            objref = self.ChildRef # correct?
        else:
            raise Exception("Can't compute public of type '%s'" % str(obj))
        public, reason = self.is_public(obj, objref) # correct?
        # Ok, update, if needed:
        if obj.public != public:
            obj.public = public
            if save:
                print("Updating public:", obj.__class__.__name__, obj.gramps_id)
                obj.save()
                #log = self.Log()
                #log.referenced_by = obj
                #log.object_id = obj.id
                #log.object_type = obj_type
                #log.log_type = "update public status"
                #log.reason = reason
                #log.order = 0
                #log.save()

    def update_publics(self, callback=None):
        """
        Call this to update probably_alive for all primary models.
        """
        if not isinstance(callback, collections.Callable):
            callback = lambda percent: None # dummy

        callback(0)
        count = 0.0
        total = (self.Note.all().count() +
                 self.Person.all().count() +
                 self.Event.all().count() +
                 self.Family.all().count() +
                 self.Repository.all().count() +
                 self.Place.all().count() +
                 self.Media.all().count() +
                 self.Source.all().count() +
                 self.Citation.all().count())

        for item in self.Note.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Person.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Family.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Source.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Event.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Repository.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Place.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Media.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

        for item in self.Citation.all():
            self.update_public(item)
            count += 1
        callback(100 * (count/total if total else 0))

    def update_probably_alive(self, callback=None):
        """
        Call this to update primary_alive for people.
        """
        from gramps.webapp.utils import probably_alive
        if not isinstance(callback, collections.Callable):
            callback = lambda percent: None # dummy
        callback(0)
        count = 0.0
        total = self.Person.all().count()
        for item in self.Person.all():
            pa = probably_alive(item.handle)
            if pa != item.probably_alive:
                print("Updating probably_alive")
                item.probably_alive = pa
                item.save()
            count += 1
        callback(100 * (count/total if total else 0))
