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

""" Implements a Db interface """

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import pickle
import sys
import os

## add this directory to sys path, so we can find django_support later:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.db.generic import *
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class DbDjango(DbGeneric):

    def restore(self):
        pass

    def write_version(self, directory):
        """Write files for a newly created DB."""
        versionpath = os.path.join(directory, str(DBBACKEND))
        LOG.debug("Write database backend file to 'djangodb'")
        with open(versionpath, "w") as version_file:
            version_file.write("djangodb")
        # Write default_settings, sqlite.db
        defaults = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "django_support", "defaults")
        LOG.debug("Copy defaults from: " + defaults)
        for filename in os.listdir(defaults):
            fullpath = os.path.abspath(os.path.join(defaults, filename))
            if os.path.isfile(fullpath):
                shutil.copy2(fullpath, directory)
        # force load, to get all modules loaded because of reset issue
        self.load(directory)

    def initialize_backend(self, directory):
        pass

    def close_backend(self):
        pass

    def transaction_commit(self, txn):
        for (obj_type, trans_type) in txn.keys():
            if trans_type in [TXNUPD, TXNADD]:
                for (handle, new_data) in txn[(obj_type, trans_type)]:
                    if obj_type == PERSON_KEY:
                        self.commit_person_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == FAMILY_KEY:
                        self.commit_family_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == EVENT_KEY:
                        self.commit_event_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == PLACE_KEY:
                        self.commit_place_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == REPOSITORY_KEY:
                        self.commit_repository_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == CITATION_KEY:
                        self.commit_citation_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == SOURCE_KEY:
                        self.commit_source_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == NOTE_KEY:
                        self.commit_note_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == MEDIA_KEY:
                        self.commit_media_object_detail(handle, new_data, trans_type, txn.batch)
                    elif obj_type == TAG_KEY:
                        self.commit_tag_detail(handle, new_data, trans_type, txn.batch)
        if txn.batch and self.has_changed:
            self.rebuild_secondary(None)

    def transaction_abort(self, txn):
        pass

    def get_metadata(self, setting, default=[]):
        metadata = self.dji.Metadata.filter(setting=setting)
        if metadata.count() > 0:
            return pickle.loads(metadata[0].value)
        elif default == []:
            return []
        else:
            return default

    def set_metadata(self, setting, value):
        from gramps.webapp.grampsdb.models import Metadata
        metadata = self.dji.Metadata.filter(setting=setting)
        if metadata.count() > 0:
            metadata = metadata[0]
            metadata.value = pickle.dumps(value)
        else:
            metadata = Metadata(setting=setting, value=pickle.dumps(value))
        metadata.save()

    def get_name_group_keys(self):
        rows = self.dji.NameGroup.all().order_by('name')
        return [row.name for row in rows]

    def get_name_group_mapping(self, key):
        rows = self.dji.NameGroup.filter(name=key)
        if rows:
            return row[0].name
        else:
            return key

    def get_person_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Person.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Person.all()]

    def get_family_handles(self):
        return [item.handle for item in self.dji.Family.all()]

    def get_event_handles(self):
        return [item.handle for item in self.dji.Event.all()]

    def get_citation_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Citation.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Citation.all()]

    def get_source_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Source.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Source.all()]

    def get_place_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Place.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Place.all()]

    def get_repository_handles(self):
        return [item.handle for item in self.dji.Repository.all()]

    def get_media_object_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Media.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Media.all()]

    def get_note_handles(self):
        return [item.handle for item in self.dji.Note.all()]

    def get_tag_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Tag.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Tag.all()]

    def get_tag_from_name(self, name):
        try:
            tag = self.dji.Tag.filter(name=name)
            return self._make_tag(tag[0])
        except:
            return None

    def get_number_of_people(self):
        return self.dji.Person.count()

    def get_number_of_events(self):
        return self.dji.Event.count()

    def get_number_of_places(self):
        return self.dji.Place.count()

    def get_number_of_tags(self):
        return self.dji.Tag.count()

    def get_number_of_families(self):
        return self.dji.Family.count()

    def get_number_of_notes(self):
        return self.dji.Note.count()

    def get_number_of_citations(self):
        return self.dji.Citation.count()

    def get_number_of_sources(self):
        return self.dji.Source.count()

    def get_number_of_media_objects(self):
        return self.dji.Media.count()

    def get_number_of_repositories(self):
        return self.dji.Repository.count()

    def has_name_group_key(self, key):
        return len(self.dji.NameGroup.filter(name=key)) > 0

    def set_name_group_mapping(self, name, grouping):
        from gramps.webapp.grampsdb.models import NameGroup
        if self.has_name_group_key(name):
            namegroup = self.dji.NameGroup.get(name=name)
        else:
            namegroup = NameGroup(name=name)
        namegroup.grouping = grouping
        namegroup.save()

    def commit_person(self, person, trans, change_time=None):
        raw = person.serialize()
        items = self.dji.Person.filter(handle=person.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_person_data(person.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_person(raw)
        if count > 0:
            trans.add(PERSON_KEY, TXNUPD, person.handle, old, raw)
        else:
            trans.add(PERSON_KEY, TXNADD, person.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_person_detail(self, handle, new_data, trans_type, batch):
        old_obj = self.get_person_from_handle(handle)
        self.dji.add_person_detail(new_data)
        obj = self.get_person_from_handle(handle)
        if trans_type == TXNUPD:
            if (old_obj.gender != obj.gender or
                old_obj.primary_name.first_name !=
                obj.primary_name.first_name):
                self.genderStats.uncount_person(old_obj)
                self.genderStats.count_person(obj)
            elif trans_type == TXNADD:
                self.genderStats.count_person(person)
        person = obj
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
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("person-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("person-add", ([handle],))
        self.has_changed = True

    def commit_family(self, family, trans, change_time=None):
        raw = family.serialize()
        items = self.dji.Family.filter(handle=family.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_family_data(family.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_family(family.serialize())
        if count > 0:
            trans.add(FAMILY_KEY, TXNUPD, family.handle, old, raw)
        else:
            trans.add(FAMILY_KEY, TXNADD, family.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_family_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_family_detail(new_data)
        obj = self.get_family_from_handle(handle)
        family = obj
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

        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("family-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("family-add", ([handle],))
        self.has_changed = True

    def commit_citation(self, citation, trans, change_time=None):
        raw = citation.serialize()
        items = self.dji.Citation.filter(handle=citation.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_citation_data(citation.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_citation(citation.serialize())
        if count > 0:
            trans.add(CITATION_KEY, TXNUPD, citation.handle, old, raw)
        else:
            trans.add(CITATION_KEY, TXNADD, citation.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_citation_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_citation_detail(new_data)
        obj = self.get_citation_from_handle(handle)
        citation = obj
        # Misc updates:
        attr_list = []
        for mref in citation.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

        self.source_attributes.update(
            [str(attr.type) for attr in citation.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("citation-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("citation-add", ([handle],))
        self.has_changed = True

    def commit_source(self, source, trans, change_time=None):
        raw = source.serialize()
        items = self.dji.Source.filter(handle=source.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_source_data(source.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_source(source.serialize())
        if count > 0:
            trans.add(SOURCE_KEY, TXNUPD, source.handle, old, raw)
        else:
            trans.add(SOURCE_KEY, TXNADD, source.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_source_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_source_detail(new_data)
        obj = self.get_source_from_handle(handle)
        source = obj
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
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("source-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("source-add", ([handle],))
        self.has_changed = True

    def commit_repository(self, repository, trans, change_time=None):
        raw = repository.serialize()
        items = self.dji.Repository.filter(handle=repository.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_repository_data(repository.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_repository(repository.serialize())
        if count > 0:
            trans.add(REPOSITORY_KEY, TXNUPD, repository.handle, old, raw)
        else:
            trans.add(REPOSITORY_KEY, TXNADD, repository.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_repository_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_repository_detail(new_data)
        obj = self.get_repository_from_handle(handle)
        repository = obj
        # Misc updates:
        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update([str(url.type) for url in repository.urls
                               if url.type.is_custom()])
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("repository-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("repository-add", ([handle],))
        self.has_changed = True

    def commit_note(self, note, trans, change_time=None):
        raw = note.serialize()
        items = self.dji.Note.filter(handle=note.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_note_data(note.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_note(note.serialize())
        if count > 0:
            trans.add(NOTE_KEY, TXNUPD, note.handle, old, raw)
        else:
            trans.add(NOTE_KEY, TXNADD, note.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_note_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_note_detail(new_data)
        obj = self.get_note_from_handle(handle)
        note = obj
        # Misc updates:
        if note.type.is_custom():
            self.note_types.add(str(note.type))
        # Emit after added:
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("note-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("note-add", ([handle],))
        self.has_changed = True

    def commit_place(self, place, trans, change_time=None):
        raw = place.serialize()
        items = self.dji.Place.filter(handle=place.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_place_data(place.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_place(place.serialize())
        if count > 0:
            trans.add(PLACE_KEY, TXNUPD, place.handle, old, raw)
        else:
            trans.add(PLACE_KEY, TXNADD, place.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_place_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_place_detail(new_data)
        obj = self.get_place_from_handle(handle)
        place = obj
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
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("place-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("place-add", ([handle],))
        self.has_changed = True

    def commit_event(self, event, trans, change_time=None):
        raw = event.serialize()
        items = self.dji.Event.filter(handle=event.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_event_data(event.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_event(event.serialize())
        if count > 0:
            trans.add(EVENT_KEY, TXNUPD, event.handle, old, raw)
        else:
            trans.add(EVENT_KEY, TXNADD, event.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_event_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_event_detail(new_data)
        obj = self.get_event_from_handle(handle)
        event = obj
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
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("event-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("event-add", ([handle],))
        self.has_changed = True

    def commit_tag(self, tag, trans, change_time=None):
        raw = tag.serialize()
        items = self.dji.Tag.filter(handle=tag.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_tag_data(tag.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_tag(tag.serialize())
        if count > 0:
            trans.add(TAG_KEY, TXNUPD, tag.handle, old, raw)
        else:
            trans.add(TAG_KEY, TXNADD, tag.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_tag_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_tag_detail(new_data)
        obj = self.get_tag_from_handle(handle)
        tag = obj
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("tag-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("tag-add", ([handle],))
        self.has_changed = True

    def commit_media_object(self, media, trans, change_time=None):
        """
        Commit the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        raw = media.serialize()
        items = self.dji.Media.filter(handle=media.handle)
        count = items.count()
        old = None
        if count > 0:
            old = self._get_raw_media_data(media.handle)
            # delete and re-add
            items[0].delete()
        self.dji.add_media(media.serialize())
        if count > 0:
            trans.add(MEDIA_KEY, TXNUPD, media.handle, old, raw)
        else:
            trans.add(MEDIA_KEY, TXNADD, media.handle, old, raw)
        # Contiued in transaction_commit...

    def commit_media_object_detail(self, handle, new_data, trans_type, batch):
        self.dji.add_media_detail(new_data)
        obj = self.get_object_from_handle(handle)
        media = obj
        # Misc updates:
        self.media_attributes.update(
            [str(attr.type) for attr in media.attribute_list
             if attr.type.is_custom() and str(attr.type)])
        if not batch:
            self.update_backlinks(obj)
            if trans_type == TXNUPD:
                self.emit("media-update", ([handle],))
            elif trans_type == TXNADD:
                self.emit("media-add", ([handle],))
        self.has_changed = True

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
        rows = self.dji.Reference.filter(ref_handle=handle)
        for row in rows:
            if (include_classes is None) or (row.obj_class in include_classes):
                yield (row.obj_class, row.obj_handle)

    def update_backlinks(self, obj):
        from gramps.webapp.grampsdb.models import Reference
        # First, delete the current references:
        self.dji.Reference.filter(obj_handle=obj.handle).delete()
        # Now, add the current ones:
        references = set(obj.get_referenced_handles_recursively())
        for (ref_class_name, ref_handle) in references:
            reference = Reference(obj_handle=obj.handle,
                                  obj_class=obj.__class__.__name__,
                                  ref_handle=ref_handle,
                                  ref_class=ref_class_name)
            reference.save()

    # Removals:
    def remove_person(self, handle, transaction):
        self.dji.Person.filter(handle=handle)[0].delete()
        self.emit("person-delete", ([handle],))

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
        table = getattr(self.dji, key2table[key].title())
        table.filter(handle=handle)[0].delete()
        self.emit("%s-delete" % key2table[key], ([handle],))

    def find_initial_person(self):
        handle = self.get_default_handle()
        person = None
        if handle:
            person = self.get_person_from_handle(handle)
            if person:
                return person
        if len(self.dji.Person.all()) > 0:
            person = self.dji.Person.all()[0]
            return self.get_person_from_handle(person.handle)

    def iter_person_handles(self):
        return (person.handle for person in self.dji.Person.all())

    def iter_family_handles(self):
        return (family.handle for family in self.dji.Family.all())

    def iter_citation_handles(self):
        return (citation.handle for citation in self.dji.Citation.all())

    def iter_event_handles(self):
        return (event.handle for event in self.dji.Event.all())

    def iter_media_object_handles(self):
        return (media.handle for media in self.dji.Media.all())

    def iter_note_handles(self):
        return (note.handle for note in self.dji.Note.all())

    def iter_place_handles(self):
        return (place.handle for place in self.dji.Place.all())

    def iter_repository_handles(self):
        return (repository.handle for repository in self.dji.Repository.all())

    def iter_source_handles(self):
        return (source.handle for source in self.dji.Source.all())

    def iter_tag_handles(self):
        return (tag.handle for tag in self.dji.Tag.all())

    def reindex_reference_map(self, callback):
        from gramps.webapp.grampsdb.models import Reference
        callback(4)
        self.dji.Reference.all().delete()
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
                        reference = Reference(obj_handle=obj.handle,
                                              obj_class=obj.__class__.__name__,
                                              ref_handle=ref_handle,
                                              ref_class=ref_class_name)
                        reference.save()
        callback(5)

    def rebuild_secondary(self, update):
        gstats = self.rebuild_gender_stats()
        self.genderStats = GenderStats(gstats)

    def has_handle_for_person(self, key):
        return self.dji.Person.filter(handle=key).count() > 0

    def has_handle_for_family(self, key):
        return self.dji.Family.filter(handle=key).count() > 0

    def has_handle_for_source(self, key):
        return self.dji.Source.filter(handle=key).count() > 0

    def has_handle_for_citation(self, key):
        return self.dji.Citation.filter(handle=key).count() > 0

    def has_handle_for_event(self, key):
        return self.dji.Event.filter(handle=key).count() > 0

    def has_handle_for_media(self, key):
        return self.dji.Media.filter(handle=key).count() > 0

    def has_handle_for_place(self, key):
        return self.dji.Place.filter(handle=key).count() > 0

    def has_handle_for_repository(self, key):
        return self.dji.Repository.filter(handle=key).count() > 0

    def has_handle_for_note(self, key):
        return self.dji.Note.filter(handle=key).count() > 0

    def has_handle_for_tag(self, key):
        return self.dji.Tag.filter(handle=key).count() > 0

    def has_gramps_id_for_person(self, key):
        return self.dji.Person.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_family(self, key):
        return self.dji.Family.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_source(self, key):
        return self.dji.Source.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_citation(self, key):
        return self.dji.Citation.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_event(self, key):
        return self.dji.Event.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_media(self, key):
        return self.dji.Media.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_place(self, key):
        return self.dji.Place.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_repository(self, key):
        return self.dji.Repository.filter(gramps_id=key).count() > 0

    def has_gramps_id_for_note(self, key):
        return self.dji.Note.filter(gramps_id=key).count() > 0

    def get_person_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Person.all()]

    def get_family_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Family.all()]

    def get_source_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Source.all()]

    def get_citation_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Citation.all()]

    def get_event_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Event.all()]

    def get_media_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Media.all()]

    def get_place_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Place.all()]

    def get_repository_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Repository.all()]

    def get_note_gramps_ids(self):
        return [x.gramps_id for x in self.dji.Note.all()]

    def _get_raw_person_data(self, key):
        try:
            return self.dji.get_person(self.dji.Person.get(handle=key))
        except:
            return None

    def _get_raw_person_from_id_data(self, key):
        try:
            return self.dji.get_person(self.dji.Person.get(gramps_id=key))
        except:
            return None

    def _get_raw_family_data(self, key):
        try:
            return self.dji.get_family(self.dji.Family.get(handle=key))
        except:
            return None

    def _get_raw_family_from_id_data(self, key):
        try:
            return self.dji.get_family(self.dji.Family.get(gramps_id=key))
        except:
            return None

    def _get_raw_source_data(self, key):
        try:
            return self.dji.get_source(self.dji.Source.get(handle=key))
        except:
            return None

    def _get_raw_source_from_id_data(self, key):
        try:
            return self.dji.get_source(self.dji.Source.get(gramps_id=key))
        except:
            return None

    def _get_raw_citation_data(self, key):
        try:
            return self.dji.get_citation(self.dji.Citation.get(handle=key))
        except:
            return None

    def _get_raw_citation_from_id_data(self, key):
        try:
            return self.dji.get_citation(self.dji.Citation.get(gramps_id=key))
        except:
            return None

    def _get_raw_event_data(self, key):
        try:
            return self.dji.get_event(self.dji.Event.get(handle=key))
        except:
            return None

    def _get_raw_event_from_id_data(self, key):
        try:
            return self.dji.get_event(self.dji.Event.get(gramps_id=key))
        except:
            return None

    def _get_raw_media_data(self, key):
        try:
            return self.dji.get_media(self.dji.Media.get(handle=key))
        except:
            return None

    def _get_raw_media_from_id_data(self, key):
        try:
            return self.dji.get_media(self.dji.Media.get(gramps_id=key))
        except:
            return None

    def _get_raw_place_data(self, key):
        try:
            return self.dji.get_place(self.dji.Place.get(handle=key))
        except:
            return None

    def _get_raw_place_from_id_data(self, key):
        try:
            return self.dji.get_place(self.dji.Place.get(gramps_id=key))
        except:
            return None

    def _get_raw_repository_data(self, key):
        try:
            return self.dji.get_repository(self.dji.Repository.get(handle=key))
        except:
            return None

    def _get_raw_repository_from_id_data(self, key):
        try:
            return self.dji.get_repository(self.dji.Repository.get(gramps_id=key))
        except:
            return None

    def _get_raw_note_data(self, key):
        try:
            return self.dji.get_note(self.dji.Note.get(handle=key))
        except:
            return None

    def _get_raw_note_from_id_data(self, key):
        try:
            return self.dji.get_note(self.dji.Note.get(gramps_id=key))
        except:
            return None

    def _get_raw_tag_data(self, key):
        try:
            return self.dji.get_tag(self.dji.Tag.get(handle=key))
        except:
            return None

    def rebuild_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        Not called: this is a database-efficient version
        """
        UNKNOWN = 2
        MALE    = 1
        FEMALE  = 0
        self.dji.GenderStats.all().delete()
        gstats = {}
        for person in self.dji.Person.all():
            for first_name in person.name_set.all():
                for name in first_name.first_name.split():
                    if name not in gstats:
                        gstats[name] = [0, 0, 0]
                    if person.gender_type.val == MALE:
                        gstats[name][0] += 1
                    elif person.gender_type.val == FEMALE:
                        gstats[name][1] += 1
                    else:
                        gstats[name][2] += 1
        for key in gstats:
            gstats[key] = tuple(gstats[key])
        return gstats

    def save_gender_stats(self, genderStats):
        """
        {name: (male_count, female_count, unknown_count), ...}
        """
        from gramps.webapp.grampsdb.models import GenderStats
        self.dji.GenderStats.all().delete()
        gstats = genderStats.stats
        for key in gstats:
            data = gstats[key]
            stat = GenderStats(name=key,
                               male=data[0],
                               female=data[1],
                               unknown=data[2])
            stat.save()

    def get_gender_stats(self):
        """
        Returns a dictionary of
        {given_name: (male_count, female_count, unknown_count)}
        """
        rows = self.dji.GenderStats.values('name', 'male', 'female', 'unknown')
        gstats = {}
        for dict in rows:
            gstats[dict['name']] = (dict['male'], dict['female'], dict['unknown'])
        return gstats

    def get_surname_list(self):
        return [x['surname'] for x in self.dji.Surname.values('surname').order_by('surname').distinct()]

    def save_surname_list(self):
        # Nothing to do
        pass

    def build_surname_list(self):
        # Nothing to do
        pass

    def drop_tables(self):
        # Nothing to do
        pass

    def load(self, directory, callback=None, mode=None,
             force_schema_upgrade=False,
             force_bsddb_upgrade=False,
             force_bsddb_downgrade=False,
             force_python_upgrade=False):

        # Django-specific loads:
        from django.conf import settings

        LOG.info("Django loading...")
        default_settings = {"__file__":
                            os.path.join(directory, "default_settings.py")}
        settings_file = os.path.join(directory, "default_settings.py")
        with open(settings_file) as f:
            code = compile(f.read(), settings_file, 'exec')
            exec(code, globals(), default_settings)

        class Module(object):
            def __init__(self, dictionary):
                self.dictionary = dictionary
            def __getattr__(self, item):
                return self.dictionary[item]

        LOG.info("Django loading defaults from: " + directory)
        try:
            settings.configure(Module(default_settings))
        except RuntimeError:
            LOG.info("Django already configured error! Shouldn't happen!")
            # already configured; ignore

        import django
        django.setup()

        from gramps.webapp.libdjango import DjangoInterface

        self.dji = DjangoInterface()
        super().load(directory,
                     callback,
                     mode,
                     force_schema_upgrade,
                     force_bsddb_upgrade,
                     force_bsddb_downgrade,
                     force_python_upgrade)

    def _make_repository(self, repository):
        if self.use_db_cache and repository.cache:
            data = repository.from_cache()
        else:
            data = self.dji.get_repository(repository)
        return Repository.create(data)

    def _make_citation(self, citation):
        if self.use_db_cache and citation.cache:
            data = citation.from_cache()
        else:
            data = self.dji.get_citation(citation)
        return Citation.create(data)

    def _make_source(self, source):
        if self.use_db_cache and source.cache:
            data = source.from_cache()
        else:
            data = self.dji.get_source(source)
        return Source.create(data)

    def _make_family(self, family):
        if self.use_db_cache and family.cache:
            data = family.from_cache()
        else:
            data = self.dji.get_family(family)
        return Family.create(data)

    def _make_person(self, person):
        if self.use_db_cache and person.cache:
            data = person.from_cache()
        else:
            data = self.dji.get_person(person)
        return Person.create(data)

    def _make_event(self, event):
        if self.use_db_cache and event.cache:
            data = event.from_cache()
        else:
            data = self.dji.get_event(event)
        return Event.create(data)

    def _make_note(self, note):
        if self.use_db_cache and note.cache:
            data = note.from_cache()
        else:
            data = self.dji.get_note(note)
        return Note.create(data)

    def _make_tag(self, tag):
        data = self.dji.get_tag(tag)
        return Tag.create(data)

    def _make_place(self, place):
        if self.use_db_cache and place.cache:
            data = place.from_cache()
        else:
            data = self.dji.get_place(place)
        return Place.create(data)

    def _make_media(self, media):
        if self.use_db_cache and media.cache:
            data = media.from_cache()
        else:
            data = self.dji.get_media(media)
        return MediaObject.create(data)

    def request_rebuild(self): # override
        # caches are ok, but let's compute public's
        self.dji.update_publics()
        super().request_rebuild()
