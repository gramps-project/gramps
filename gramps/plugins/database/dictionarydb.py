# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012 - 2015 Douglas S. Blank <doug.blank@gmail.com>
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

""" Implements a Db interface as a Dictionary """

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.db.generic import *
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class DictionaryDb(DbGeneric):
    """
    Database backend class for dictionary databases
    """

    def restore(self):
        """
        If you wish to support an optional restore routine, put it here.
        """
        pass

    def write_version(self, directory):
        """Write files for a newly created DB."""
        versionpath = os.path.join(directory, str(DBBACKEND))
        LOG.debug("Write database backend file to 'dictionarydb'")
        with open(versionpath, "w") as version_file:
            version_file.write("dictionarydb")

    def initialize_backend(self, directory):
        # Handle dicts:
        self._person_dict = {}
        self._family_dict = {}
        self._source_dict = {}
        self._citation_dict = {}
        self._event_dict = {}
        self._media_dict = {}
        self._place_dict = {}
        self._repository_dict = {}
        self._note_dict = {}
        self._tag_dict = {}
        # Gramps id dicts:
        self._person_id_dict = {}
        self._family_id_dict = {}
        self._source_id_dict = {}
        self._citation_id_dict = {}
        self._event_id_dict = {}
        self._media_id_dict = {}
        self._place_id_dict = {}
        self._repository_id_dict = {}
        self._note_id_dict = {}
        # Name:
        self._tag_name_dict = {}

        # Secondary:
        self._reference_list = []
        self._name_group_dict = {}
        self._metadata_dict = {}
        self._gender_stats_dict = {}

    def close_backend(self):
        pass

    def transaction_commit(self, txn):
        """
        Executed after a batch operation.
        """
        self.transaction = None
        msg = txn.get_description()
        self.undodb.commit(txn, msg)
        self._after_commit(txn)
        txn.clear()
        self.has_changed = True

    def transaction_abort(self, txn):
        """
        Executed after a batch operation abort.
        """
        self.transaction = None
        txn.clear()
        txn.first = None
        txn.last = None
        self._after_commit(txn)

    def get_metadata(self, key, default=[]):
        """
        Get an item from the database.
        """
        row = self._metadata_dict.get(key, None)
        if row:
            return row
        elif default == []:
            return []
        else:
            return default

    def set_metadata(self, key, value):
        """
        key: string
        value: item, will be serialized here
        """
        self._metadata_dict[key] = value

    def get_name_group_keys(self):
        return self._name_group_dict.keys()

    def get_name_group_mapping(self, key):
        return self._name_group_dict.get(key, key)

    def get_person_handles(self, sort_handles=False):
        ## Fixme: implement sort
        return self._person_dict.keys()

    def get_family_handles(self):
        return self._family_dict.keys()

    def get_event_handles(self):
        return self._event_dict.keys()

    def get_citation_handles(self, sort_handles=False):
        ## Fixme: implement sort
        return self._citation_dict.keys()

    def get_source_handles(self, sort_handles=False):
        ## Fixme: implement sort
        return self._source_dict.keys()

    def get_place_handles(self, sort_handles=False):
        ## Fixme: implement sort
        return self._place_dict.keys()

    def get_repository_handles(self):
        return self._repository_dict.keys()

    def get_media_object_handles(self, sort_handles=False):
        ## Fixme: implement sort
        return self._media_dict.keys()

    def get_note_handles(self):
        return self._note_dict.keys()

    def get_tag_handles(self, sort_handles=False):
        # FIXME: implement sort
        return self._tag_dict.keys()

    def get_tag_from_name(self, name):
        return self._tag_name_dict.get(name, None)

    def get_number_of_people(self):
        return len(self._person_dict)

    def get_number_of_events(self):
        return len(self._event_dict)

    def get_number_of_places(self):
        return len(self._place_dict)

    def get_number_of_tags(self):
        return len(self._tag_dict)

    def get_number_of_families(self):
        return len(self._family_dict)

    def get_number_of_notes(self):
        return len(self._note_dict)

    def get_number_of_citations(self):
        return len(self._citation_dict)

    def get_number_of_sources(self):
        return len(self._source_dict)

    def get_number_of_media_objects(self):
        return len(self._media_dict)

    def get_number_of_repositories(self):
        return len(self._repository_dict)

    def has_name_group_key(self, key):
        return key in self._name_group_dict

    def set_name_group_mapping(self, name, grouping):
        self._name_group_dict[name] = grouping

    def commit_person(self, person, trans, change_time=None):
        emit = None
        old_person = None
        if person.handle in self.person_map:
            emit = "person-update"
            old_person = self.get_person_from_handle(person.handle)
            # Update gender statistics if necessary
            if (old_person.gender != person.gender or
                old_person.primary_name.first_name !=
                  person.primary_name.first_name):

                self.genderStats.uncount_person(old_person)
                self.genderStats.count_person(person)
            # Update surname list if necessary
            if (self._order_by_person_key(person) !=
                self._order_by_person_key(old_person)):
                self.remove_from_surname_list(old_person)
                self.add_to_surname_list(person, trans.batch)
            given_name, surname, gender_type = self.get_person_data(person)
            # update the person:
            self._person_dict[person.handle] = person
            self._person_id_dict[person.gramps_id] = person
        else:
            emit = "person-add"
            self.genderStats.count_person(person)
            self.add_to_surname_list(person, trans.batch)
            given_name, surname, gender_type = self.get_person_data(person)
            # Insert the person:
            self._person_dict[person.handle] = person
            self._person_id_dict[person.gramps_id] = person
        if not trans.batch:
            self.update_backlinks(person)
            if old_person:
                trans.add(PERSON_KEY, TXNUPD, person.handle,
                          old_person.serialize(),
                          person.serialize())
            else:
                trans.add(PERSON_KEY, TXNADD, person.handle,
                          None,
                          person.serialize())
        # Other misc update tasks:
        self.individual_attributes.update(
            [str(attr.type) for attr in person.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        self.event_role_names.update([str(eref.role)
                                      for eref in person.event_ref_list
                                      if eref.role.is_custom()])

        self.name_types.update([str(name.type)
                                for name in ([person.primary_name]
                                             + person.alternate_names)
                                if name.type.is_custom()])
        all_surn = []  # new list we will use for storage
        all_surn += person.primary_name.get_surname_list()
        for asurname in person.alternate_names:
            all_surn += asurname.get_surname_list()
        self.origin_types.update([str(surn.origintype) for surn in all_surn
                                if surn.origintype.is_custom()])
        all_surn = None
        self.url_types.update([str(url.type) for url in person.urls
                               if url.type.is_custom()])
        attr_list = []
        for mref in person.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([person.handle],))
        self.has_changed = True

    def commit_family(self, family, trans, change_time=None):
        emit = None
        old_family = None
        if family.handle in self.family_map:
            emit = "family-update"
            old_family = self.get_family_from_handle(family.handle).serialize()
            self._family_dict[family.handle] = family
            self._family_id_dict[family.gramps_id] = family
        else:
            emit = "family-add"
            self._family_dict[family.handle] = family
            self._family_id_dict[family.gramps_id] = family
        if not trans.batch:
            self.update_backlinks(family)
            op = TXNUPD if old_family else TXNADD
            trans.add(FAMILY_KEY, op, family.handle,
                      old_family,
                      family.serialize())

        # Misc updates:
        self.family_attributes.update(
            [str(attr.type) for attr in family.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        rel_list = []
        for ref in family.child_ref_list:
            if ref.frel.is_custom():
                rel_list.append(str(ref.frel))
            if ref.mrel.is_custom():
                rel_list.append(str(ref.mrel))
        self.child_ref_types.update(rel_list)

        self.event_role_names.update(
            [str(eref.role) for eref in family.event_ref_list
             if eref.role.is_custom()])

        if family.type.is_custom():
            self.family_rel_types.add(str(family.type))

        attr_list = []
        for mref in family.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([family.handle],))
        self.has_changed = True

    def commit_citation(self, citation, trans, change_time=None):
        emit = None
        old_citation = None
        if citation.handle in self.citation_map:
            emit = "citation-update"
            old_citation = self.get_citation_from_handle(citation.handle).serialize()
            self._citation_dict[citation.handle] = citation
            self._citation_id_dict[citation.gramps_id] = citation
        else:
            emit = "citation-add"
            self._citation_dict[citation.handle] = citation
            self._citation_id_dict[citation.gramps_id] = citation
        if not trans.batch:
            self.update_backlinks(citation)
            op = TXNUPD if old_citation else TXNADD
            trans.add(CITATION_KEY, op, citation.handle,
                      old_citation,
                      citation.serialize())
        # Misc updates:
        attr_list = []
        for mref in citation.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

        self.source_attributes.update(
            [str(attr.type) for attr in citation.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        # Emit after added:
        if emit:
            self.emit(emit, ([citation.handle],))
        self.has_changed = True

    def commit_source(self, source, trans, change_time=None):
        emit = None
        old_source = None
        if source.handle in self.source_map:
            emit = "source-update"
            old_source = self.get_source_from_handle(source.handle).serialize()
            self._source_dict[source.handle] = source
            self._source_id_dict[source.gramps_id] = source
        else:
            emit = "source-add"
            self._source_dict[source.handle] = source
            self._source_id_dict[source.gramps_id] = source
        if not trans.batch:
            self.update_backlinks(source)
            op = TXNUPD if old_source else TXNADD
            trans.add(SOURCE_KEY, op, source.handle,
                      old_source,
                      source.serialize())
        # Misc updates:
        self.source_media_types.update(
            [str(ref.media_type) for ref in source.reporef_list
             if ref.media_type.is_custom()])

        attr_list = []
        for mref in source.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        self.source_attributes.update(
            [str(attr.type) for attr in source.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        # Emit after added:
        if emit:
            self.emit(emit, ([source.handle],))
        self.has_changed = True

    def commit_repository(self, repository, trans, change_time=None):
        emit = None
        old_repository = None
        if repository.handle in self.repository_map:
            emit = "repository-update"
            old_repository = self.get_repository_from_handle(repository.handle).serialize()
            self._repository_dict[repository.handle] = repository
            self._repository_id_dict[repository.gramps_id] = repository
        else:
            emit = "repository-add"
            self._repository_dict[repository.handle] = repository
            self._repository_id_dict[repository.gramps_id] = repository
        if not trans.batch:
            self.update_backlinks(repository)
            op = TXNUPD if old_repository else TXNADD
            trans.add(REPOSITORY_KEY, op, repository.handle,
                      old_repository,
                      repository.serialize())
        # Misc updates:
        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update([str(url.type) for url in repository.urls
                               if url.type.is_custom()])
        # Emit after added:
        if emit:
            self.emit(emit, ([repository.handle],))
        self.has_changed = True

    def commit_note(self, note, trans, change_time=None):
        emit = None
        old_note = None
        if note.handle in self.note_map:
            emit = "note-update"
            old_note = self.get_note_from_handle(note.handle).serialize()
            self._note_dict[note.handle] = note
            self._note_id_dict[note.gramps_id] = note
        else:
            emit = "note-add"
            self._note_dict[note.handle] = note
            self._note_id_dict[note.gramps_id] = note
        if not trans.batch:
            self.update_backlinks(note)
            op = TXNUPD if old_note else TXNADD
            trans.add(NOTE_KEY, op, note.handle,
                      old_note,
                      note.serialize())
        # Misc updates:
        if note.type.is_custom():
            self.note_types.add(str(note.type))
        # Emit after added:
        if emit:
            self.emit(emit, ([note.handle],))
        self.has_changed = True

    def commit_place(self, place, trans, change_time=None):
        emit = None
        old_place = None
        if place.handle in self.place_map:
            emit = "place-update"
            old_place = self.get_place_from_handle(place.handle).serialize()
            self._place_dict[place.handle] = place
            self._place_id_dict[place.gramps_id] = place
        else:
            emit = "place-add"
            self._place_dict[place.handle] = place
            self._place_id_dict[place.gramps_id] = place
        if not trans.batch:
            self.update_backlinks(place)
            op = TXNUPD if old_place else TXNADD
            trans.add(PLACE_KEY, op, place.handle,
                      old_place,
                      place.serialize())
        # Misc updates:
        if place.get_type().is_custom():
            self.place_types.add(str(place.get_type()))

        self.url_types.update([str(url.type) for url in place.urls
                               if url.type.is_custom()])

        attr_list = []
        for mref in place.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([place.handle],))
        self.has_changed = True

    def commit_event(self, event, trans, change_time=None):
        emit = None
        old_event = None
        if event.handle in self.event_map:
            emit = "event-update"
            old_event = self.get_event_from_handle(event.handle).serialize()
            self._event_dict[event.handle] = event
            self._event_id_dict[event.gramps_id] = event
        else:
            emit = "event-add"
            self._event_dict[event.handle] = event
            self._event_id_dict[event.gramps_id] = event
        if not trans.batch:
            self.update_backlinks(event)
            op = TXNUPD if old_event else TXNADD
            trans.add(EVENT_KEY, op, event.handle,
                      old_event,
                      event.serialize())
        # Misc updates:
        self.event_attributes.update(
            [str(attr.type) for attr in event.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        if event.type.is_custom():
            self.event_names.add(str(event.type))
        attr_list = []
        for mref in event.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)
        # Emit after added:
        if emit:
            self.emit(emit, ([event.handle],))
        self.has_changed = True

    def commit_tag(self, tag, trans, change_time=None):
        emit = None
        if tag.handle in self.tag_map:
            emit = "tag-update"
            self._tag_dict[tag.handle] = tag
            self._tag_name_dict[tag.name] = tag
        else:
            emit = "tag-add"
            self._tag_dict[tag.handle] = tag
            self._tag_name_dict[tag.name] = tag
        if not trans.batch:
            self.update_backlinks(tag)
        # Emit after added:
        if emit:
            self.emit(emit, ([tag.handle],))

    def commit_media_object(self, media, trans, change_time=None):
        emit = None
        old_media = None
        if media.handle in self.media_map:
            emit = "media-update"
            old_media = self.get_object_from_handle(media.handle).serialize()
            self._media_dict[media.handle] = media
            self._media_id_dict[media.gramps_id] = media
        else:
            emit = "media-add"
            self._media_dict[media.handle] = media
            self._media_id_dict[media.gramps_id] = media
        if not trans.batch:
            self.update_backlinks(media)
            op = TXNUPD if old_media else TXNADD
            trans.add(MEDIA_KEY, op, media.handle,
                      old_media,
                      media.serialize())
        # Misc updates:
        self.media_attributes.update(
            [str(attr.type) for attr in media.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        # Emit after added:
        if emit:
            self.emit(emit, ([media.handle],))

    def update_backlinks(self, obj):
        # First, delete the current references:
        # self._reference_list = [[obj.handle,
        #                          obj.__class__.__name__,
        #                          ref_handle,
        #                          ref_class_name], ...]
        for item in list(self._reference_list):
            if item[0] == obj.handle:
                self._reference_list.remove(item)
        # Now, add the current ones:
        references = set(obj.get_referenced_handles_recursively())
        for (ref_class_name, ref_handle) in references:
            self._reference_list.append([obj.handle,
                                         obj.__class__.__name__,
                                         ref_handle,
                                         ref_class_name])
        # This function is followed by a commit.

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.
        """

        if self.readonly or not handle:
            return
        if handle in self.person_map:
            person = Person.create(self.person_map[handle])
            del self._person_dict[handle]
            del self._person_id_dict[person.gramps_id]
            self.emit("person-delete", ([handle],))
            if not transaction.batch:
                transaction.add(PERSON_KEY, TXNDEL, person.handle,
                                person.serialize(), None)

    def _do_remove(self, handle, transaction, data_map, data_id_map, key):
        key2table = {
            PERSON_KEY:     "person",
            FAMILY_KEY:     "family",
            SOURCE_KEY:     "source",
            CITATION_KEY:   "citation",
            EVENT_KEY:      "event",
            MEDIA_KEY:      "media",
            PLACE_KEY:      "place",
            REPOSITORY_KEY: "repository",
            NOTE_KEY:       "note",
            TAG_KEY:        "tag",
            }
        if self.readonly or not handle:
            return
        if handle in data_map:
            dict = getattr(self, "_%s_dict" % key2table[key])
            obj = dict[handle]
            del dict[handle]
            dict = getattr(self, "_%s_id_dict" % key2table[key])
            del dict[obj.gramps_id]
            self.emit(KEY_TO_NAME_MAP[key] + "-delete", ([handle],))
            if not transaction.batch:
                data = data_map[handle]
                transaction.add(key, TXNDEL, handle, data, None)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.

        Returns an interator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Default: None means include all classes.
        :type include_classes: list of class names

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """
        #self._reference_list = [[obj.handle,
        #                         obj.__class__.__name__,
        #                         ref_handle,
        #                         ref_class_name], ...]
        rows = (x for x in self._reference_list if x[2] == handle)
        for row in rows:
            if (include_classes is None) or (row[1] in include_classes):
                yield (row[1], row[0])

    def find_initial_person(self):
        handle = self.get_default_handle()
        person = None
        if handle:
            person = self.get_person_from_handle(handle)
            if person:
                return person
        if len(self._person_dict) > 0:
            return list(self._person_dict.values())[0]

    def iter_person_handles(self):
        return (handle for handle in self._person_dict.keys())

    def iter_family_handles(self):
        return (handle for handle in self._family_dict.keys())

    def iter_citation_handles(self):
        return (key for key in self._citation_dict.keys())

    def iter_event_handles(self):
        return (key for key in self._event_dict.keys())

    def iter_media_object_handles(self):
        return (key for key in self._media_dict.keys())

    def iter_note_handles(self):
        return (key for key in self._note_dict.keys())

    def iter_place_handles(self):
        return (key for key in self._place_dict.keys())

    def iter_repository_handles(self):
        return (key for key in self._repository_dict.keys())

    def iter_source_handles(self):
        return (key for key in self._source_dict.keys())

    def iter_tag_handles(self):
        return (key for key in self._tag_dict.keys())

    def reindex_reference_map(self, callback):
        callback(4)
        self._reference_list = []
        primary_table = (
            (self.get_person_cursor, Person),
            (self.get_family_cursor, Family),
            (self.get_event_cursor, Event),
            (self.get_place_cursor, Place),
            (self.get_source_cursor, Source),
            (self.get_citation_cursor, Citation),
            (self.get_media_cursor, MediaObject),
            (self.get_repository_cursor, Repository),
            (self.get_note_cursor, Note),
            (self.get_tag_cursor, Tag),
        )
        # Now we use the functions and classes defined above
        # to loop through each of the primary object tables.
        for cursor_func, class_func in primary_table:
            logging.info("Rebuilding %s reference map" %
                         class_func.__name__)
            with cursor_func() as cursor:
                for found_handle, val in cursor:
                    obj = class_func.create(val)
                    references = set(obj.get_referenced_handles_recursively())
                    # handle addition of new references
                    for (ref_class_name, ref_handle) in references:
                        self._reference_list.append([obj.handle,
                                                     obj.__class__.__name__,
                                                     ref_handle,
                                                     ref_class_name])
        callback(5)

    def rebuild_secondary(self, update):
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)
        self.surname_list = self.build_surname_list()

    def has_handle_for_person(self, key):
        return key in self._person_dict

    def has_handle_for_family(self, key):
        return key in self._family_dict

    def has_handle_for_source(self, key):
        return key in self._source_dict

    def has_handle_for_citation(self, key):
        return key in self._citation_dict

    def has_handle_for_event(self, key):
        return key in self._event_dict

    def has_handle_for_media(self, key):
        return key in self._media_dict

    def has_handle_for_place(self, key):
        return key in self._place_dict

    def has_handle_for_repository(self, key):
        return key in self._repository_dict

    def has_handle_for_note(self, key):
        return key in self._note_dict

    def has_handle_for_tag(self, key):
        return key in self._tag_dict

    def has_gramps_id_for_person(self, key):
        return (key in self._person_id_dict)

    def has_gramps_id_for_family(self, key):
        return (key in self._family_id_dict)

    def has_gramps_id_for_source(self, key):
        return (key in self._source_id_dict)

    def has_gramps_id_for_citation(self, key):
        return (key in self._citation_id_dict)

    def has_gramps_id_for_event(self, key):
        return (key in self._event_id_dict)

    def has_gramps_id_for_media(self, key):
        return (key in self._media_id_dict)

    def has_gramps_id_for_place(self, key):
        return (key in self._place_id_dict)

    def has_gramps_id_for_repository(self, key):
        return (key in self._repository_id_dict)

    def has_gramps_id_for_note(self, key):
        return (key in self._note_id_dict)

    def get_person_gramps_ids(self):
        return [x.gramps_id for x in self._person_dict.values()]

    def get_family_gramps_ids(self):
        return [x.gramps_id for x in self._family_dict.values()]

    def get_source_gramps_ids(self):
        return [x.gramps_id for x in self._source_dict.values()]

    def get_citation_gramps_ids(self):
        return [x.gramps_id for x in self._citation_dict.values()]

    def get_event_gramps_ids(self):
        return [x.gramps_id for x in self._event_dict.values()]

    def get_media_gramps_ids(self):
        return [x.gramps_id for x in self._media_dict.values()]

    def get_place_gramps_ids(self):
        return [x.gramps_id for x in self._place_dict.values()]

    def get_repository_gramps_ids(self):
        return [x.gramps_id for x in self._repository_dict.values()]

    def get_note_gramps_ids(self):
        return [x.gramps_id for x in self._note_dict.values()]

    def _get_raw_person_data(self, key):
        if key in self._person_dict:
            return self._person_dict[key].serialize()

    def _get_raw_person_from_id_data(self, key):
        if key in self._person_id_dict:
            return self._person_id_dict[key].serialize()

    def _get_raw_family_data(self, key):
        if key in self._family_dict:
            return self._family_dict[key].serialize()

    def _get_raw_family_from_id_data(self, key):
        if key in self._family_id_dict:
            return self._family_id_dict[key].serialize()

    def _get_raw_source_data(self, key):
        if key in self._source_dict:
            return self._source_dict[key].serialize()

    def _get_raw_source_from_id_data(self, key):
        if key in self._source_id_dict:
            return self._source_id_dict[key].serialize()

    def _get_raw_citation_data(self, key):
        if key in self._citation_dict:
            return self._citation_dict[key].serialize()

    def _get_raw_citation_from_id_data(self, key):
        if key in self._citation_id_dict:
            return self._citation_id_dict[key].serialize()

    def _get_raw_event_data(self, key):
        if key in self._event_dict:
            return self._event_dict[key].serialize()

    def _get_raw_event_from_id_data(self, key):
        if key in self._event_id_dict:
            return self._event_id_dict[key].serialize()

    def _get_raw_media_data(self, key):
        if key in self._media_dict:
            return self._media_dict[key].serialize()

    def _get_raw_media_from_id_data(self, key):
        if key in self._media_id_dict:
            return self._media_id_dict[key].serialize()

    def _get_raw_place_data(self, key):
        if key in self._place_dict:
            return self._place_dict[key].serialize()

    def _get_raw_place_from_id_data(self, key):
        if key in self._place_id_dict:
            return self._place_id_dict[key].serialize()

    def _get_raw_repository_data(self, key):
        if key in self._repository_dict:
            return self._repository_dict[key].serialize()

    def _get_raw_repository_from_id_data(self, key):
        if key in self._repository_id_dict:
            return self._repository_id_dict[key].serialize()

    def _get_raw_note_data(self, key):
        if key in self._note_dict:
            return self._note_dict[key].serialize()

    def _get_raw_note_from_id_data(self, key):
        if key in self._note_id_dict:
            return self._note_id_dict[key].serialize()

    def _get_raw_tag_data(self, key):
        if key in self._tag_dict:
            return self._tag_dict[key].serialize()

    def rebuild_gender_stats(self):
        """
        Builds and returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        Called locally: this is a database-efficient version
        """
        # In dictionarydb, there is no separate persistent storage of
        # gender stats, so we just get from the source:
        return self.get_gender_stats()

    def get_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        UNKNOWN = 2
        MALE    = 1
        FEMALE  = 0
        """
        gstats = {}
        for person in self._person_dict.values():
            if person.primary_name:
                first_name = person.primary_name.first_name
                if first_name not in gstats:
                    gstats[first_name] = (0, 0, 0)
                if person.gender == Person.MALE:
                    gstats[first_name] = (gstats[first_name][0] + 1,
                                          gstats[first_name][1],
                                          gstats[first_name][2])
                elif person.gender == Person.FEMALE:
                    gstats[first_name] = (gstats[first_name][0],
                                          gstats[first_name][1] + 1,
                                          gstats[first_name][2])
                else:
                    gstats[first_name] = (gstats[first_name][0],
                                          gstats[first_name][1],
                                          gstats[first_name][2] + 1)
        return gstats

    def save_gender_stats(self, gstats):
        # Gender stats are not saved in the dictionary db
        pass

    def save_surname_list(self):
        """
        Save the surname_list into persistant storage.
        """
        # Nothing for to do
        pass

    def build_surname_list(self):
        """
        Rebuild the surname_list.
        """
        surname_list = []
        for person in self._person_dict.values():
            if person.primary_name:
                if person.primary_name.surname_list:
                    if person.primary_name.surname_list[0].surname not in surname_list:
                        surname_list.append(person.primary_name.surname_list[0].surname)
        return surname_list

    def drop_tables(self):
        """
        Useful in testing, reseting.
        """
        self._person_dict = {}
        self._family_dict = {}
        self._source_dict = {}
        self._citation_dict = {}
        self._event_dict = {}
        self._media_dict = {}
        self._place_dict = {}
        self._repository_dict = {}
        self._note_dict = {}
        self._tag_dict = {}
        # Gramps id dicts:
        self._person_id_dict = {}
        self._family_id_dict = {}
        self._source_id_dict = {}
        self._citation_id_dict = {}
        self._event_id_dict = {}
        self._media_id_dict = {}
        self._place_id_dict = {}
        self._repository_id_dict = {}
        self._note_id_dict = {}
        # Name:
        self._tag_name_dict = {}

        # Secondary:
        self._reference_list = []
        self._name_group_dict = {}
        self._metadata_dict = {}
        self._gender_stats_dict = {}

    def load(self, directory, callback=None, mode=None,
             force_schema_upgrade=False,
             force_bsddb_upgrade=False,
             force_bsddb_downgrade=False,
             force_python_upgrade=False):
        super().load(directory,
                     callback,
                     mode,
                     force_schema_upgrade,
                     force_bsddb_upgrade,
                     force_bsddb_downgrade,
                     force_python_upgrade)
        # Dictionary-specific load:
        from gramps.plugins.importer.importxml import importData
        from gramps.cli.user import User
        if self._directory:
            filename = os.path.join(self._directory, "data.gramps")
            if os.path.isfile(filename):
                importData(self, filename, User())
                self.reindex_reference_map(lambda progress: None)
                self.rebuild_secondary(lambda progress: None)
