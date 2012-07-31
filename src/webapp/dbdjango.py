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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

""" Implements a Db interface """

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import cPickle
import base64
import time
import gen
import re
from gen.db import DbReadBase, DbWriteBase, DbTxn
from gen.db import (PERSON_KEY,
                    FAMILY_KEY,
                    CITATION_KEY,
                    SOURCE_KEY,
                    EVENT_KEY,
                    MEDIA_KEY,
                    PLACE_KEY,
                    REPOSITORY_KEY,
                    NOTE_KEY)
from gen.utils.id import create_id
from webapp.libdjango import DjangoInterface
from django.db import transaction

class Cursor(object):
    def __init__(self, model, func):
        self.model = model
        self.func = func
    def __enter__(self):
        return self
    def __iter__(self):
        return self.__next__()
    def __next__(self):
        for item in self.model.all():
            yield (item.handle, self.func(item.handle))
    def __exit__(self, *args, **kwargs):
        pass
    def iter(self):
        for item in self.model.all():
            yield (item.handle, self.func(item.handle))
        yield None

class Bookmarks:
    def get(self):
        return [] # handles
    def append(self, handle):
        pass

class DjangoTxn(DbTxn):
    def __init__(self, message, db, table=None):
        DbTxn.__init__(self, message, db)
        self.table = table

    def get(self, key, default=None, txn=None, **kwargs):
        """
        Returns the data object associated with key
        """
        try:
            return self.table.objects(handle=key)
        except:
            if txn and key in txn:
                return txn[key]
            else:
                return None

    def put(self, handle, new_data, txn):
        """
        """
        txn[handle] = new_data

class DbDjango(DbWriteBase, DbReadBase):
    """
    A Gramps Database Backend. This replicates the grampsdb functions.
    """

    def __init__(self):
        DbReadBase.__init__(self)
        DbWriteBase.__init__(self)
        # skip GEDCOM cross-ref check for now:
        self.set_feature("skip-check-xref", True)
        self.dji = DjangoInterface()
        self.readonly = False
        self.db_is_open = True
        self.name_formats = []
        self.bookmarks = Bookmarks()
        self.family_bookmarks = Bookmarks()
        self.event_bookmarks = Bookmarks()
        self.place_bookmarks = Bookmarks()
        self.citation_bookmarks = Bookmarks()
        self.source_bookmarks = Bookmarks()
        self.repo_bookmarks = Bookmarks()
        self.media_bookmarks = Bookmarks()
        self.note_bookmarks = Bookmarks()
        self.set_person_id_prefix('I%04d')
        self.set_object_id_prefix('O%04d')
        self.set_family_id_prefix('F%04d')
        self.set_citation_id_prefix('C%04d')
        self.set_source_id_prefix('S%04d')
        self.set_place_id_prefix('P%04d')
        self.set_event_id_prefix('E%04d')
        self.set_repository_id_prefix('R%04d')
        self.set_note_id_prefix('N%04d')
        # ----------------------------------
        self.id_trans  = DjangoTxn("ID Transaction", self, self.dji.Person)
        self.fid_trans = DjangoTxn("FID Transaction", self, self.dji.Family)
        self.pid_trans = DjangoTxn("PID Transaction", self, self.dji.Place)
        self.cid_trans = DjangoTxn("CID Transaction", self, self.dji.Citation)
        self.sid_trans = DjangoTxn("SID Transaction", self, self.dji.Source)
        self.oid_trans = DjangoTxn("OID Transaction", self, self.dji.Media)
        self.rid_trans = DjangoTxn("RID Transaction", self, self.dji.Repository)
        self.nid_trans = DjangoTxn("NID Transaction", self, self.dji.Note)
        self.eid_trans = DjangoTxn("EID Transaction", self, self.dji.Event)
        self.cmap_index = 0
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.rmap_index = 0
        self.nmap_index = 0
        self.env = None
        self.person_map = {}
        self.family_map = {}
        self.place_map  = {}
        self.citation_map = {}
        self.source_map = {}
        self.repository_map  = {}
        self.note_map = {}
        self.media_map  = {}
        self.event_map  = {}
        self.metadata   = {}
        self.name_group = {}
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified   = 0
        self.txn = DjangoTxn("DbDjango Transaction", self)
        self.transaction = None
        # Import cache for gedcom import, uses transactions, and
        # two step adding of objects.
        self.import_cache = {}
        self.use_import_cache = False
        self.use_db_cache = True

    def prepare_import(self):
        """
        DbDjango does not commit data on gedcom import, but saves them
        for later commit.
        """
        self.use_import_cache = True
        self.import_cache = {}

    @transaction.commit_on_success
    def commit_import(self):
        """
        Commits the items that were queued up during the last gedcom
        import for two step adding.
        """
        # First we add the primary objects:
        for key in self.import_cache.keys():
            obj = self.import_cache[key]
            if isinstance(obj, gen.lib.Person):
                self.dji.add_person(obj.serialize())
            elif isinstance(obj, gen.lib.Family):
                self.dji.add_family(obj.serialize())
            elif isinstance(obj, gen.lib.Event):
                self.dji.add_event(obj.serialize())
            elif isinstance(obj, gen.lib.Place):
                self.dji.add_place(obj.serialize())
            elif isinstance(obj, gen.lib.Repository):
                self.dji.add_repository(obj.serialize())
            elif isinstance(obj, gen.lib.Citation):
                self.dji.add_citation(obj.serialize())
            elif isinstance(obj, gen.lib.Source):
                self.dji.add_source(obj.serialize())
            elif isinstance(obj, gen.lib.Note):
                self.dji.add_note(obj.serialize())
            elif isinstance(obj, gen.lib.MediaObject):
                self.dji.add_media(obj.serialize())
            elif isinstance(obj, gen.lib.Tag):
                self.dji.add_tag(obj.serialize())
        # Next we add the links:
        for key in self.import_cache.keys():
            obj = self.import_cache[key]
            if isinstance(obj, gen.lib.Person):
                self.dji.add_person_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Family):
                self.dji.add_family_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Event):
                self.dji.add_event_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Place):
                self.dji.add_place_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Repository):
                self.dji.add_repository_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Citation):
                self.dji.add_citation_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Source):
                self.dji.add_source_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Note):
                self.dji.add_note_detail(obj.serialize())
            elif isinstance(obj, gen.lib.MediaObject):
                self.dji.add_media_detail(obj.serialize())
            elif isinstance(obj, gen.lib.Tag):
                self.dji.add_tag_detail(obj.serialize())
        self.use_import_cache = False
        self.import_cache = {}
        self.dji.update_publics()

    def transaction_commit(self, txn):
        pass

    def enable_signals(self):
        pass

    def request_rebuild(self):
        # caches are ok, but let's compute public's
        self.dji.update_publics()

    def get_undodb(self):
        return None

    def transaction_abort(self, txn):
        pass

    @staticmethod
    def _validated_id_prefix(val, default):
        if isinstance(val, basestring) and val:
            try:
                str_ = val % 1
            except TypeError:           # missing conversion specifier
                prefix_var = val + "%d"
            except ValueError:          # incomplete format
                prefix_var = default+"%04d"
            else:
                prefix_var = val        # OK as given
        else:
            prefix_var = default+"%04d" # not a string or empty string
        return prefix_var

    @staticmethod
    def __id2user_format(id_pattern):
        """
        Return a method that accepts a Gramps ID and adjusts it to the users
        format.
        """
        pattern_match = re.match(r"(.*)%[0 ](\d+)[diu]$", id_pattern)
        if pattern_match:
            str_prefix = pattern_match.group(1)
            nr_width = pattern_match.group(2)
            def closure_func(gramps_id):
                if gramps_id and gramps_id.startswith(str_prefix):
                    id_number = gramps_id[len(str_prefix):]
                    if id_number.isdigit():
                        id_value = int(id_number, 10)
                        if len(str(id_value)) > nr_width:
                            # The ID to be imported is too large to fit in the
                            # users format. For now just create a new ID,
                            # because that is also what happens with IDs that
                            # are identical to IDs already in the database. If
                            # the problem of colliding import and already
                            # present IDs is solved the code here also needs
                            # some solution.
                            gramps_id = id_pattern % 1
                        else:
                            gramps_id = id_pattern % id_value
                return gramps_id
        else:
            def closure_func(gramps_id):
                return gramps_id
        return closure_func

    def set_person_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Person ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as I%d or I%04d.
        """
        self.person_prefix = self._validated_id_prefix(val, "I")
        self.id2user_format = self.__id2user_format(self.person_prefix)

    def set_citation_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Citation ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as C%d or C%04d.
        """
        self.citation_prefix = self._validated_id_prefix(val, "C")
        self.cid2user_format = self.__id2user_format(self.citation_prefix)
            
    def set_source_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Source ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as S%d or S%04d.
        """
        self.source_prefix = self._validated_id_prefix(val, "S")
        self.sid2user_format = self.__id2user_format(self.source_prefix)
            
    def set_object_id_prefix(self, val):
        """
        Set the naming template for GRAMPS MediaObject ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as O%d or O%04d.
        """
        self.mediaobject_prefix = self._validated_id_prefix(val, "O")
        self.oid2user_format = self.__id2user_format(self.mediaobject_prefix)

    def set_place_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Place ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as P%d or P%04d.
        """
        self.place_prefix = self._validated_id_prefix(val, "P")
        self.pid2user_format = self.__id2user_format(self.place_prefix)

    def set_family_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        self.family_prefix = self._validated_id_prefix(val, "F")
        self.fid2user_format = self.__id2user_format(self.family_prefix)

    def set_event_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Event ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as E%d or E%04d.
        """
        self.event_prefix = self._validated_id_prefix(val, "E")
        self.eid2user_format = self.__id2user_format(self.event_prefix)

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Repository ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as R%d or R%04d.
        """
        self.repository_prefix = self._validated_id_prefix(val, "R")
        self.rid2user_format = self.__id2user_format(self.repository_prefix)

    def set_note_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Note ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as N%d or N%04d.
        """
        self.note_prefix = self._validated_id_prefix(val, "N")
        self.nid2user_format = self.__id2user_format(self.note_prefix)

    def __find_next_gramps_id(self, prefix, map_index, trans):
        """
        Helper function for find_next_<object>_gramps_id methods
        """
        index = prefix % map_index
        while trans.get(str(index), txn=self.txn) is not None:
            map_index += 1
            index = prefix % map_index
        map_index += 1
        return (map_index, index)
        
    def find_next_person_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Person object based off the 
        person ID prefix.
        """
        self.pmap_index, gid = self.__find_next_gramps_id(self.person_prefix,
                                          self.pmap_index, self.id_trans)
        return gid

    def find_next_place_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Place object based off the 
        place ID prefix.
        """
        self.lmap_index, gid = self.__find_next_gramps_id(self.place_prefix,
                                          self.lmap_index, self.pid_trans)
        return gid

    def find_next_event_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Event object based off the 
        event ID prefix.
        """
        self.emap_index, gid = self.__find_next_gramps_id(self.event_prefix,
                                          self.emap_index, self.eid_trans)
        return gid

    def find_next_object_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a MediaObject object based
        off the media object ID prefix.
        """
        self.omap_index, gid = self.__find_next_gramps_id(self.mediaobject_prefix,
                                          self.omap_index, self.oid_trans)
        return gid

    def find_next_citation_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Citation object based off the 
        citation ID prefix.
        """
        self.cmap_index, gid = self.__find_next_gramps_id(self.citation_prefix,
                                          self.cmap_index, self.cid_trans)
        return gid

    def find_next_source_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Source object based off the 
        source ID prefix.
        """
        self.smap_index, gid = self.__find_next_gramps_id(self.source_prefix,
                                          self.smap_index, self.sid_trans)
        return gid

    def find_next_family_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Family object based off the 
        family ID prefix.
        """
        self.fmap_index, gid = self.__find_next_gramps_id(self.family_prefix,
                                          self.fmap_index, self.fid_trans)
        return gid

    def find_next_repository_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Respository object based 
        off the repository ID prefix.
        """
        self.rmap_index, gid = self.__find_next_gramps_id(self.repository_prefix,
                                          self.rmap_index, self.rid_trans)
        return gid

    def find_next_note_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Note object based off the 
        note ID prefix.
        """
        self.nmap_index, gid = self.__find_next_gramps_id(self.note_prefix,
                                          self.nmap_index, self.nid_trans)
        return gid

    def get_mediapath(self):
        return None

    def get_name_group_keys(self):
        return []

    def get_name_group_mapping(self, key):
        return None

    def get_researcher(self):
        obj = gen.lib.Researcher()
        return obj

    def get_tag_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Tag.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Tag.all()]

    def get_person_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Person.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Person.all()]

    def get_family_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Family.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Family.all()]

    def get_event_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Event.all().order_by("handle")]
        else:
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

    def get_repository_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Repository.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Repository.all()]

    def get_media_object_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Media.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Media.all()]

    def get_note_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Note.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Note.all()]

    def get_event_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            event = self.dji.Event.get(handle=handle)
        except:
            return None
        return self.make_event(event)

    def get_family_from_handle(self, handle): 
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            family = self.dji.Family.get(handle=handle)
        except:
            return None
        return self.make_family(family)

    def get_family_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        try:
            family = self.dji.Family.get(gramps_id=gramps_id)
        except:
            return None
        return self.make_family(family)

    def get_repository_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            repository = self.dji.Repository.get(handle=handle)
        except:
            return None
        return self.make_repository(repository)

    def get_person_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            person = self.dji.Person.get(handle=handle)
        except:
            return None
        return self.make_person(person)

    def get_tag_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            tag = self.dji.Tag.get(handle=handle)
        except:
            return None
        return self.make_tag(tag)

    def make_repository(self, repository):
        if self.use_db_cache and repository.cache:
            data = cPickle.loads(base64.decodestring(repository.cache))
        else:
            data = self.dji.get_repository(repository)
        return gen.lib.Repository.create(data)

    def make_citation(self, citation):
        if self.use_db_cache and citation.cache:
            data = cPickle.loads(base64.decodestring(citation.cache))
        else:
            data = self.dji.get_citation(citation)
        return gen.lib.Citation.create(data)

    def make_source(self, source):
        if self.use_db_cache and source.cache:
            data = cPickle.loads(base64.decodestring(source.cache))
        else:
            data = self.dji.get_source(source)
        return gen.lib.Source.create(data)

    def make_family(self, family):
        if self.use_db_cache and family.cache:
            data = cPickle.loads(base64.decodestring(family.cache))
        else:
            data = self.dji.get_family(family)
        return gen.lib.Family.create(data)

    def make_person(self, person):
        if self.use_db_cache and person.cache:
            data = cPickle.loads(base64.decodestring(person.cache))
        else:
            data = self.dji.get_person(person)
        return gen.lib.Person.create(data)

    def make_event(self, event):
        if self.use_db_cache and event.cache:
            data = cPickle.loads(base64.decodestring(event.cache))
        else:
            data = self.dji.get_event(event)
        return gen.lib.Event.create(data)

    def make_note(self, note):
        if self.use_db_cache and note.cache:
            data = cPickle.loads(base64.decodestring(note.cache))
        else:
            data = self.dji.get_note(note)
        return gen.lib.Note.create(data)

    def make_tag(self, tag):
        data = self.dji.get_tag(tag)
        return gen.lib.Tag.create(data)

    def make_place(self, place):
        if self.use_db_cache and place.cache:
            data = cPickle.loads(base64.decodestring(place.cache))
        else:
            data = self.dji.get_place(place)
        return gen.lib.Place.create(data)

    def make_media(self, media):
        if self.use_db_cache and media.cache:
            data = cPickle.loads(base64.decodestring(media.cache))
        else:
            data = self.dji.get_media(media)
        return gen.lib.MediaObject.create(data)

    def get_place_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            place = self.dji.Place.get(handle=handle)
        except:
            return None
        return self.make_place(place)

    def get_citation_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            citation = self.dji.Citation.get(handle=handle)
        except:
            return None
        return self.make_citation(citation)

    def get_source_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            source = self.dji.Source.get(handle=handle)
        except:
            return None
        return self.make_source(source)

    def get_note_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            note = self.dji.Note.get(handle=handle)
        except:
            return None
        return self.make_note(note)

    def get_object_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            media = self.dji.Media.get(handle=handle)
        except:
            return None
        return self.make_media(media)

    def get_default_person(self):
        return None

    def iter_people(self):
        return (self.get_person_from_handle(person.handle) 
                for person in self.dji.Person.all())

    def iter_person_handles(self):
        return (person.handle for person in self.dji.Person.all())

    def iter_families(self):
        return (self.get_family_from_handle(family.handle) 
                for family in self.dji.Family.all())

    def iter_family_handles(self):
        return (family.handle for family in self.dji.Family.all())

    def get_tag_from_name(self, name):
        try:
            tag = self.dji.Tag.filter(name=name)
            return self.make_tag(tag[0])
        except:
            return None

    def get_person_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Person.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_person(match_list[0])
        else:
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

    def get_place_cursor(self):
        return Cursor(self.dji.Place, self.get_raw_place_data).iter()

    def get_person_cursor(self):
        return Cursor(self.dji.Person, self.get_raw_person_data).iter()

    def get_family_cursor(self):
        return Cursor(self.dji.Family, self.get_raw_family_data).iter()

    def get_events_cursor(self):
        return Cursor(self.dji.Event, self.get_raw_event_data).iter()

    def get_citation_cursor(self):
        return Cursor(self.dji.Citation, self.get_raw_citation_data).iter()

    def get_source_cursor(self):
        return Cursor(self.dji.Source, self.get_raw_source_data).iter()

    def has_gramps_id(self, obj_key, gramps_id):
        key2table = {
            PERSON_KEY:     self.dji.Person, 
            FAMILY_KEY:     self.dji.Family, 
            SOURCE_KEY:     self.dji.Source, 
            CITATION_KEY:   self.dji.Citation, 
            EVENT_KEY:      self.dji.Event, 
            MEDIA_KEY:      self.dji.Media, 
            PLACE_KEY:      self.dji.Place, 
            REPOSITORY_KEY: self.dji.Repository, 
            NOTE_KEY:       self.dji.Note, 
            }
        table = key2table[obj_key]
        return table.filter(gramps_id=gramps_id).count() > 0

    def has_person_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Person.filter(handle=handle).count() == 1

    def has_family_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Family.filter(handle=handle).count() == 1

    def has_citation_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Citation.filter(handle=handle).count() == 1

    def has_source_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Source.filter(handle=handle).count() == 1

    def has_repository_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Repository.filter(handle=handle).count() == 1

    def has_note_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Note.filter(handle=handle).count() == 1

    def has_place_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Place.filter(handle=handle).count() == 1

    def has_event_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Event.filter(handle=handle).count() == 1

    def has_tag_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Tag.filter(handle=handle).count() == 1

    def has_object_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Media.filter(handle=handle).count() == 1

    def has_name_group_key(self, key):
        # FIXME:
        return False

    def set_name_group_mapping(self, key, value):
        # FIXME:
        pass

    def set_default_person_handle(self, handle):
        pass

    def set_mediapath(self, mediapath):
        pass

    def get_raw_person_data(self, handle):
        try:
            return self.dji.get_person(self.dji.Person.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_family_data(self, handle):
        try:
            return self.dji.get_family(self.dji.Family.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_citation_data(self, handle):
        try:
            return self.dji.get_citation(self.dji.Citation.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_source_data(self, handle):
        try:
            return self.dji.get_source(self.dji.Source.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_repository_data(self, handle):
        try:
            return self.dji.get_repository(self.dji.Repository.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_note_data(self, handle):
        try:
            return self.dji.get_note(self.dji.Note.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_place_data(self, handle):
        try:
            return self.dji.get_place(self.dji.Place.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_object_data(self, handle):
        try:
            return self.dji.get_media(self.dji.Media.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def add_person(self, person, trans, set_gid=True):
        if not person.handle:
            person.handle = create_id()
        if not person.gramps_id and set_gid:
            person.gramps_id = self.find_next_person_gramps_id()
        self.commit_person(person, trans)
        return person.handle

    def add_family(self, family, trans, set_gid=True):
        if not family.handle:
            family.handle = create_id()
        if not family.gramps_id and set_gid:
            family.gramps_id = self.find_next_family_gramps_id()
        self.commit_family(family, trans)
        return family.handle

    def add_citation(self, citation, trans, set_gid=True):
        if not citation.handle:
            citation.handle = create_id()
        if not citation.gramps_id and set_gid:
            citation.gramps_id = self.find_next_citation_gramps_id()
        self.commit_citation(citation, trans)
        return citation.handle

    def add_source(self, source, trans, set_gid=True):
        if not source.handle:
            source.handle = create_id()
        if not source.gramps_id and set_gid:
            source.gramps_id = self.find_next_source_gramps_id()
        self.commit_source(source, trans)
        return source.handle

    def add_repository(self, repository, trans, set_gid=True):
        if not repository.handle:
            repository.handle = create_id()
        if not repository.gramps_id and set_gid:
            repository.gramps_id = self.find_next_repository_gramps_id()
        self.commit_repository(repository, trans)
        return repository.handle

    def add_note(self, note, trans, set_gid=True):
        if not note.handle:
            note.handle = create_id()
        if not note.gramps_id and set_gid:
            note.gramps_id = self.find_next_note_gramps_id()
        self.commit_note(note, trans)
        return note.handle

    def add_place(self, place, trans, set_gid=True):
        if not place.handle:
            place.handle = create_id()
        if not place.gramps_id and set_gid:
            place.gramps_id = self.find_next_place_gramps_id()
        self.commit_place(place, trans)
        return place.handle

    def add_event(self, event, trans, set_gid=True):
        if not event.handle:
            event.handle = create_id()
        if not event.gramps_id and set_gid:
            event.gramps_id = self.find_next_event_gramps_id()
        self.commit_event(event, trans)
        return event.handle

    def add_tag(self, tag, trans):
        if not tag.handle:
            tag.handle = create_id()
        self.commit_event(tag, trans)
        return tag.handle

    def add_object(self, obj, transaction, set_gid=True):
        """
        Add a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        if not obj.handle:
            obj.handle = create_id()
        if not obj.gramps_id and set_gid:
            obj.gramps_id = self.find_next_object_gramps_id()
        self.commit_media_object(obj, transaction)
        return obj.handle

    def commit_person(self, person, trans, change_time=None):
        self.import_cache[person.handle] = person

    def commit_family(self, family, trans, change_time=None):
        self.import_cache[family.handle] = family

    def commit_citation(self, citation, trans, change_time=None):
        self.import_cache[citation.handle] = citation

    def commit_source(self, source, trans, change_time=None):
        self.import_cache[source.handle] = source

    def commit_repository(self, repository, trans, change_time=None):
        self.import_cache[repository.handle] = repository

    def commit_note(self, note, trans, change_time=None):
        self.import_cache[note.handle] = note

    def commit_place(self, place, trans, change_time=None):
        self.import_cache[place.handle] = place

    def commit_event(self, event, trans, change_time=None):
        self.import_cache[event.handle] = event

    def commit_tag(self, tag, trans, change_time=None):
        self.import_cache[tag.handle] = tag

    def commit_media_object(self, obj, transaction, change_time=None):
        """
        Commit the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        self.import_cache[obj.handle] = obj

    def get_gramps_ids(self, obj_key):
        key2table = {
            PERSON_KEY:     self.id_trans, 
            FAMILY_KEY:     self.fid_trans, 
            CITATION_KEY:   self.cid_trans, 
            SOURCE_KEY:     self.sid_trans, 
            EVENT_KEY:      self.eid_trans, 
            MEDIA_KEY:      self.oid_trans, 
            PLACE_KEY:      self.pid_trans, 
            REPOSITORY_KEY: self.rid_trans, 
            NOTE_KEY:       self.nid_trans, 
            }

        table = key2table[obj_key]
        return table.keys()

    def transaction_begin(self, transaction):
        return 

    def disable_signals(self):
        pass

    def set_researcher(self, owner):
        pass

