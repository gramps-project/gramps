#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020-2016 Gramps Development Team
# Copyright (C) 2020      Paul Culley
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
""" Generic upgrade module for dbapi dbs """
#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import os
import re
import time
import logging
#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.cli.clidbman import NAME_FILE
from gramps.gen.lib import EventType, NameOriginType, Tag, MarkerType
from gramps.gen.utils.file import create_checksum
from gramps.gen.utils.id import create_id
from gramps.gui.dialog import (InfoDialog)
from .dbconst import (PERSON_KEY, FAMILY_KEY, EVENT_KEY, MEDIA_KEY, PLACE_KEY,
                      REPOSITORY_KEY, CITATION_KEY, SOURCE_KEY, NOTE_KEY,
                      TAG_KEY)
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

LOG = logging.getLogger(".upgrade")


def gramps_upgrade_20(self):
    """
    Placeholder update.
    """
    length = 0
    self.set_total(length)
    self._txn_begin()

    # uid and place upgrade code goes here

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 20)


def gramps_upgrade_19(self):
    """
    Upgrade database from version 18 to 19.
    """
    # This is done in the conversion from bsddb, so just say we did it.
    self._set_metadata('version', 19)


def gramps_upgrade_18(self):
    """
    Upgrade database from version 17 to 18.
    """
    length = self.get_number_of_places()
    self.set_total(length)
    self._txn_begin()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    # Convert name fields to use PlaceName.
    for handle in self.get_place_handles():
        place = self.get_raw_place_data(handle)
        new_place = list(place)
        new_place[6] = (new_place[6], None, '')
        alt_names = []
        for name in new_place[7]:
            alt_names.append((name, None, ''))
        new_place[7] = alt_names
        new_place = tuple(new_place)
        self._commit_raw(new_place, PLACE_KEY)
        self.update()

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 18)


def gramps_upgrade_17(self):
    """
    Upgrade database from version 16 to 17.

    1. This upgrade adds tags to event, place, repository, source and
       citation objects.
    2. Data of Source becomes SourceAttributes Secondary Object
    3. Create a place hierarchy.
    4. Add checksum field to media objects.
    5. Rebuild list of custom events.
    """
    length = (self.get_number_of_events() + self.get_number_of_places() +
              self.get_number_of_citations() + self.get_number_of_sources() +
              self.get_number_of_repositories() + self.get_number_of_media())
    self.set_total(length)
    self._txn_begin()

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # Add new tag_list field.
    self.event_names = set()
    for handle in self.get_event_handles():
        event = self.get_raw_event_data(handle)
        new_event = list(event)
        event_type = EventType()
        event_type.unserialize(new_event[2])
        if event_type.is_custom():
            self.event_names.add(str(event_type))
        new_event = new_event[:11] + [[]] + new_event[11:]
        new_event = tuple(new_event)
        self._commit_raw(new_event, EVENT_KEY)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    # Convert to hierarchical structure and add new tag_list field.
    locations = {}
    self.max_id = 0
    index = re.compile('[0-9]+')
    for handle in self.get_place_handles():
        place = self.get_raw_place_data(handle)
        match = index.search(place[1])
        if match:
            if self.max_id <= int(match.group(0)):
                self.max_id = int(match.group(0))
        if place[5] is not None:
            locations[get_location(place[5])] = handle

    for handle in list(self.get_place_handles()):
        place = self.get_raw_place_data(handle)
        new_place = list(place)

        zip_code = ''
        if new_place[5]:
            zip_code = new_place[5][0][6]

        # find title and type
        main_loc = get_location(new_place[5])
        for level, name in enumerate(main_loc):
            if name:
                break

        loc = list(main_loc[:])
        loc[level] = ''

        # find top parent
        parent_handle = None
        for n in range(7):
            if loc[n]:
                tup = tuple([''] * n + loc[n:])
                parent_handle = locations.get(tup, None)
                if parent_handle:
                    break

        # create nodes
        if parent_handle:
            n -= 1
        while n > level:
            if loc[n]:
                # TODO for Arabic, should the next line's comma be translated?
                title = ', '.join([item for item in loc[n:] if item])
                parent_handle = add_place(
                    self, loc[n], n, parent_handle, title)
                locations[tuple([''] * n + loc[n:])] = parent_handle
            n -= 1

        if parent_handle is not None:
            placeref_list = [(parent_handle.decode('utf-8'), None)]
        else:
            placeref_list = []

        if name:
            type_num = 7 - level
        else:
            name = new_place[2]
            type_num = -1
        new_place = (new_place[:5] + [
            placeref_list, name, [], (type_num, ''), zip_code] +
            new_place[6:12] + [[]] + new_place[12:])
        new_place = tuple(new_place)
        self._commit_raw(new_place, PLACE_KEY)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.get_repository_handles():
        repository = self.get_raw_repository_data(handle)
        new_repository = list(repository)
        new_repository = new_repository[:8] + [[]] + new_repository[8:]
        new_repository = tuple(new_repository)
        self._commit_raw(new_repository, REPOSITORY_KEY)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.get_source_handles():
        source = self.get_raw_source_data(handle)
        new_source = list(source)
        new_source = new_source[:11] + [[]] + new_source[11:]
        new_source = tuple(new_source)
        self._commit_raw(new_source, SOURCE_KEY)
        self.update()

    # ---------------------------------
    # Modify Citation
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.get_citation_handles():
        citation = self.get_raw_citation_data(handle)
        new_citation = list(citation)
        new_citation = new_citation[:10] + [[]] + new_citation[10:]
        new_citation = tuple(new_citation)
        self._commit_raw(new_citation, CITATION_KEY)
        self.update()

    # -------------------------------------------------------
    # Upgrade Source and Citation datamap to SrcAttributeBase
    # -------------------------------------------------------
    for handle in self.get_source_handles():
        source = self.get_raw_source_data(handle)
        (handle, gramps_id, title, author, pubinfo,
            notelist, medialist, abbrev, change, datamap, reporef_list,
            taglist, private) = source
        srcattributelist = upgrade_datamap_17(datamap)
        new_source = (handle, gramps_id, title, author, pubinfo,
                      notelist, medialist, abbrev, change, srcattributelist,
                      reporef_list, taglist, private)
        self._commit_raw(new_source, SOURCE_KEY)
        self.update()

    for handle in self.get_citation_handles():
        citation = self.get_raw_citation_data(handle)
        (handle, gramps_id, datelist, page, confidence, source_handle,
            notelist, medialist, datamap, change, taglist, private) = citation
        srcattributelist = upgrade_datamap_17(datamap)
        new_citation = (handle, gramps_id, datelist, page, confidence,
                        source_handle, notelist, medialist, srcattributelist,
                        change, taglist, private)
        self._commit_raw(new_citation, CITATION_KEY)
        self.update()

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    # Add new checksum field.
    base_path = self._get_metadata('media-path')
    if not base_path:
        # Check that the mediapath is not set to None (bug #7844).
        base_path = ''
    for handle in self.get_media_handles():
        media = self.get_raw_media_data(handle)
        new_media = list(media)
        if os.path.isabs(new_media[2]):
            full_path = new_media[2]
        else:
            full_path = os.path.join(base_path, new_media[2])
        checksum = create_checksum(full_path)
        new_media = new_media[:5] + [checksum] + new_media[5:]
        new_media = tuple(new_media)
        self._commit_raw(new_media, MEDIA_KEY)
        self.update()

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 17)


def get_location(loc):
    # (street, locality, parish, city, county, state, country)
    if loc is None:
        location = ('',) * 7
    else:
        location = loc[0][:2] + (loc[1],) + loc[0][2:6]
    return location


def add_place(self, name, level, parent, title):
    handle = create_id()
    self.max_id += 1
    gid = self.place_prefix % self.max_id
    placetype = (7 - level, '')
    if parent is not None:
        placeref_list = [(parent.decode('utf-8'), None)]
    else:
        placeref_list = []
    place = (handle, gid, title, '', '', placeref_list, name, [], placetype,
             '', [], [], [], [], [], 0, [], False)
    self._commit_raw(place, PLACE_KEY)
    return handle


def upgrade_datamap_17(datamap):
    """
    In version 16 key value pairs are stored in source and citation.
    These become SrcAttribute
    """
    new_srcattr_list = []
    private = False
    from gramps.gen.lib.srcattrtype import SrcAttributeType
    for (key, value) in datamap.items():
        the_type = SrcAttributeType(key).serialize()
        new_srcattr_list.append((private, the_type, value))
    return new_srcattr_list


def gramps_upgrade_16(self):
    """
    Upgrade database from version 15 to 16. This upgrade converts all
    SourceRef child objects to Citation Primary objects.

    For each primary object that has a sourceref, what we have to do is:

        (1) create each citation
        (2) update the object to reference the Citations
        (3) remove backlinks for references from object to Source
        (4) add backlinks for references from object to Citations
        (5) add backlinks for references from Citation to Source

    the backlinks are all updated at the end by calling
    :py:meth:`reindex_reference_map <.write.DbBsddb.reindex_reference_map>`
    """
    # Only People, Families, Events, Media Objects, Places, Sources and
    # Repositories need to be updated, because these are the only primary
    # objects that can have source citations.
    length = (self.get_number_of_people() +
              self.get_number_of_events() + self.get_number_of_families() +
              self.get_number_of_repositories() + self.get_number_of_media() +
              self.get_number_of_places() + self.get_number_of_sources())
    self.set_total(length)
    self._txn_begin()

    # Setup data for upgrade statistics information dialogue
    keyorder = [PERSON_KEY, FAMILY_KEY, EVENT_KEY, MEDIA_KEY,
                PLACE_KEY, REPOSITORY_KEY, SOURCE_KEY]
    key2data = {
        PERSON_KEY : 0,
        FAMILY_KEY : 1,
        EVENT_KEY: 2,
        MEDIA_KEY: 3,
        PLACE_KEY: 4,
        REPOSITORY_KEY: 5,
        SOURCE_KEY : 6,
    }
    key2string = {
        PERSON_KEY      : _('%(n1)6d  People        upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        FAMILY_KEY      : _('%(n1)6d  Families      upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        EVENT_KEY       : _('%(n1)6d  Events        upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        MEDIA_KEY       : _('%(n1)6d  Media Objects upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        PLACE_KEY       : _('%(n1)6d  Places        upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        REPOSITORY_KEY  : _('%(n1)6d  Repositories  upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
        SOURCE_KEY      : _('%(n1)6d  Sources       upgraded with '
                            '%(n2)6d citations in %(n3)6d secs\n'),
    }
    data_upgradeobject = [0] * 7

    # Initialise the citation gramps ID number
    self.cmap_index = 0

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for person_handle in self.get_person_handles():
        person = self.get_raw_person_data(person_handle)
        try:
            # The parameters are evaluated before deciding whether logging is
            # on or not. Since the retrieval of names is so complex, I think it
            # is safer to protect this with a try except block, even though it
            # seems to work for names being present and not.
            LOG.debug("upgrade person %s %s" % (person[3][4],
                      " ".join([name[0] for name in person[3][5]])))
        except:
            pass
        (handle, gramps_id, gender, primary_name, alternate_names,
         death_ref_index, birth_ref_index, event_ref_list, family_list,
         parent_family_list, media_list, address_list, attribute_list,
         urls, lds_seal_list, source_list, note_list, change, tag_list,
         private, person_ref_list) = person
        if primary_name:
            primary_name = upgrade_name_16(self, primary_name)
        if alternate_names:
            alternate_names = upgrade_name_list_16(self, alternate_names)
        if address_list:
            address_list = upgrade_address_list_16(self, address_list)
        if media_list:
            media_list = upgrade_media_list_16(self, media_list)
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(self, attribute_list)
        if lds_seal_list:
            lds_seal_list = upgrade_lds_seal_list_16(self, lds_seal_list)
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                self, source_list)
        else:
            new_citation_list = []
        if person_ref_list:
            person_ref_list = upgrade_person_ref_list_16(self, person_ref_list)
        if event_ref_list:
            event_ref_list = upgrade_event_ref_list_16(self, event_ref_list)
        if(primary_name or alternate_names or address_list or media_list or
           attribute_list or lds_seal_list or source_list or
           person_ref_list or event_ref_list):
            new_person = (handle, gramps_id, gender, primary_name,
                          alternate_names, death_ref_index,
                          birth_ref_index, event_ref_list, family_list,
                          parent_family_list, media_list, address_list,
                          attribute_list, urls, lds_seal_list,
                          new_citation_list, note_list, change, tag_list,
                          private, person_ref_list)
            LOG.debug("      upgrade new_person %s" % [new_person])
            self._commit_raw(new_person, PERSON_KEY)
        self.update()

    LOG.debug("%d persons upgraded with %d citations in %d seconds. " %
              (self.get_number_of_people(),
               self.cmap_index - start_num_citations,
               time.time() - start_time))
    data_upgradeobject[key2data[PERSON_KEY]] = (
        self.get_number_of_people(), self.cmap_index - start_num_citations,
        time.time() - start_time)

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for media_handle in self.get_media_handles():
        media = self.get_raw_media_data(media_handle)
        LOG.debug("upgrade media object %s" % media[4])
        (handle, gramps_id, path, mime, desc,
         attribute_list, source_list, note_list, change,
         date, tag_list, private) = media
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_attribute_list = upgrade_attribute_list_16(self, attribute_list)

        new_media = (handle, gramps_id, path, mime, desc,
                     new_attribute_list, new_citation_list, note_list,
                     change, date, tag_list, private)
        LOG.debug("      upgrade new_media %s" % [new_media])
        self._commit_raw(new_media, MEDIA_KEY)
        self.update()

    LOG.debug("%d media objects upgraded with %d citations in %d seconds" %
              (self.get_number_of_media(),
               self.cmap_index - start_num_citations,
               int(time.time() - start_time)))
    data_upgradeobject[key2data[MEDIA_KEY]] = (
        self.get_number_of_media(), self.cmap_index - start_num_citations,
        time.time() - start_time)

    # ---------------------------------
    # Modify Places
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for place_handle in self.get_place_handles():
        place = self.get_raw_place_data(place_handle)
        LOG.debug("upgrade place %s" % place[2])
        (handle, gramps_id, title, longi, lat,
         main_loc, alt_loc, urls, media_list, source_list, note_list,
         change, private) = place
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                self, source_list)
        else:
            new_citation_list = []
        if media_list:
            media_list = upgrade_media_list_16(self, media_list)
        if source_list or media_list:
            new_place = (handle, gramps_id, title,
                         longi, lat, main_loc, alt_loc, urls,
                         media_list, new_citation_list, note_list,
                         change, private)
            LOG.debug("      upgrade new_place %s" % [new_place])
            self._commit_raw(new_place, PLACE_KEY)
        self.update()

    LOG.debug("%d places upgraded with %d citations in %d seconds. " %
              (self.get_number_of_places(),
               self.cmap_index - start_num_citations,
               time.time() - start_time))
    data_upgradeobject[key2data[PLACE_KEY]] = (
        self.get_number_of_places(), self.cmap_index - start_num_citations,
        time.time() - start_time)

    # ---------------------------------
    # Modify Families
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for family_handle in self.get_family_handles():
        family = self.get_raw_family_data(family_handle)
        LOG.debug("upgrade family (gramps_id) %s" % family[1])
        (handle, gramps_id, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, source_list, note_list,
         change, tag_list, private) = family
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                self, source_list)
        else:
            new_citation_list = []
        if child_ref_list:
            child_ref_list = upgrade_child_ref_list_16(self, child_ref_list)
        if lds_seal_list:
            lds_seal_list = upgrade_lds_seal_list_16(self, lds_seal_list)
        if media_list:
            media_list = upgrade_media_list_16(self, media_list)
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(self, attribute_list)
        if event_ref_list:
            event_ref_list = upgrade_event_ref_list_16(self, event_ref_list)
        if(source_list or media_list or child_ref_list or
           attribute_list or lds_seal_list or event_ref_list):
            new_family = (handle, gramps_id, father_handle, mother_handle,
                          child_ref_list, the_type, event_ref_list, media_list,
                          attribute_list, lds_seal_list, new_citation_list,
                          note_list, change, tag_list, private)
            LOG.debug("      upgrade new_family %s" % [new_family])
            self._commit_raw(new_family, FAMILY_KEY)
        self.update()

    LOG.debug("%d families upgraded with %d citations in %d seconds. " %
              (self.get_number_of_families(),
               self.cmap_index - start_num_citations,
               time.time() - start_time))
    data_upgradeobject[key2data[FAMILY_KEY]] = (
        self.get_number_of_families(), self.cmap_index - start_num_citations,
        time.time() - start_time)
    # ---------------------------------
    # Modify Events
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for event_handle in self.get_event_handles():
        event = self.get_raw_event_data(event_handle)
        LOG.debug("upgrade event %s" % event[4])
        (handle, gramps_id, the_type, date, description, place,
         source_list, note_list, media_list, attribute_list,
         change, private) = event
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                self, source_list)
        else:
            new_citation_list = []
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(self, attribute_list)
        if media_list:
            media_list = upgrade_media_list_16(self, media_list)
        if source_list or attribute_list or media_list:
            new_event = (handle, gramps_id, the_type, date, description, place,
                         new_citation_list, note_list, media_list,
                         attribute_list,
                         change, private)
            LOG.debug("      upgrade new_event %s" % [new_event])
            self._commit_raw(new_event, EVENT_KEY)
        self.update()

    LOG.debug("%d events upgraded with %d citations in %d seconds. " %
              (self.get_number_of_events(),
               self.cmap_index - start_num_citations,
               time.time() - start_time))
    data_upgradeobject[key2data[EVENT_KEY]] = (
        self.get_number_of_events(), self.cmap_index - start_num_citations,
        time.time() - start_time)

    # ---------------------------------
    # Modify Repositories
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for repository_handle in self.get_repository_handles():
        repository = self.get_raw_repository_data(repository_handle)
        LOG.debug("upgrade repository %s" % repository[3])
        (handle, gramps_id, the_type, name, note_list,
         address_list, urls, change, private) = repository
        if address_list:
            address_list = upgrade_address_list_16(self, address_list)
        if address_list:
            new_repository = (handle, gramps_id, the_type, name, note_list,
                              address_list, urls, change, private)
            LOG.debug("      upgrade new_repository %s" % [new_repository])
            self._commit_raw(new_repository, REPOSITORY_KEY)
        self.update()

    LOG.debug("%d repositories upgraded with %d citations in %d seconds. " %
              (self.get_number_of_repositories(),
               self.cmap_index - start_num_citations,
               time.time() - start_time))
    data_upgradeobject[key2data[REPOSITORY_KEY]] = (
        self.get_number_of_repositories(),
        self.cmap_index - start_num_citations,
        time.time() - start_time)

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for source_handle in self.get_source_handles():
        source = self.get_raw_source_data(source_handle)
        LOG.debug("upgrade source %s" % source[2])
        (handle, gramps_id, title, author,
         pubinfo, note_list, media_list,
         abbrev, change, datamap, reporef_list,
         private) = source
        if media_list:
            media_list = upgrade_media_list_16(self, media_list)

        new_source = (handle, gramps_id, title, author,
                      pubinfo, note_list, media_list,
                      abbrev, change, datamap, reporef_list,
                      private)
        LOG.debug("      upgrade new_source %s" % [new_source])
        self._commit_raw(new_source, SOURCE_KEY)
        self.update()

    LOG.debug("%d sources upgraded with %d citations in %d seconds" %
              (self.get_number_of_sources(),
               self.cmap_index - start_num_citations,
               int(time.time() - start_time)))
    data_upgradeobject[key2data[SOURCE_KEY]] = (
        self.get_number_of_sources(), self.cmap_index - start_num_citations,
        time.time() - start_time)

# ---------------------------------
# Example database from repository took:
# 3403 events upgraded with 8 citations in 23 seconds. Backlinks took 1071 secs
# actually 4 of these citations were from:
# Media upgrade 4 citations upgraded in 4 seconds
# by only doing the backlinks when there might be something to do,
# improved to:
# 3403 events upgraded with 8 citations in 19 seconds. Backlinks took 1348 secs
# further improved by skipping debug logging:
# 3403 events upgraded with 8 citations in 2 seconds. Backlinks took 167 secs

#Number of new objects upgraded:
#  2090  People        upgraded with   2092 citations in 2148 secs
#   734  Families      upgraded with    735 citations in 768 secs
#  3403  Events        upgraded with      4 citations in 212 secs
#     7  Media Objects upgraded with      4 citations in 3 secs
#   852  Places        upgraded with      0 citations in 39 secs

# with reduced diagnostics
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in     74 secs
#    35  Families      upgraded with     36 citations in     31 secs
#  3403  Events        upgraded with      4 citations in      7 secs
#     7  Media Objects upgraded with      4 citations in      3 secs
#   852  Places        upgraded with      0 citations in      1 secs

# without doing any backlinks
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in     43 secs
#    35  Families      upgraded with     36 citations in     24 secs
#  3403  Events        upgraded with      4 citations in      6 secs
#     7  Media Objects upgraded with      4 citations in      2 secs
#   852  Places        upgraded with      0 citations in      1 secs

# another run about the same code:
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in     48 secs
#    35  Families      upgraded with     36 citations in     21 secs
#  3403  Events        upgraded with      4 citations in      9 secs
#     7  Media Objects upgraded with      4 citations in      4 secs
#   852  Places        upgraded with      0 citations in      1 secs

# another run
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in     36 secs
#    35  Families      upgraded with     36 citations in     18 secs
#  3403  Events        upgraded with      4 citations in      9 secs
#     7  Media Objects upgraded with      4 citations in      2 secs
#   852  Places        upgraded with      0 citations in      1 secs

# without incorrect nested tranaction structure:
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in      0 secs
#    35  Families      upgraded with     36 citations in      0 secs
#  3403  Events        upgraded with      4 citations in      0 secs
#     7  Media Objects upgraded with      4 citations in      0 secs
#   852  Places        upgraded with      0 citations in      0 secs

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 16)

    LOG.debug([data_upgradeobject])
    txt = _("Number of new objects upgraded:\n")
    for key in keyorder:
        try:
            txt += key2string[key] % {
                'n1' : data_upgradeobject[key2data[key]][0],
                'n2' : data_upgradeobject[key2data[key]][1],
                'n3' : data_upgradeobject[key2data[key]][2]}
        except:
            txt += key2string[key]
    txt += _("\n\nYou may want to run\n"
             "Tools -> Family Tree Processing -> Merge\n"
             "in order to merge citations that contain similar\n"
             "information")
    InfoDialog(_('Upgrade Statistics'), txt, monospaced=True)  # TODO no-parent


def upgrade_media_list_16(self, media_list):
    new_media_list = []
    for media in media_list:
        (privacy, source_list, note_list, attribute_list, ref, rect) = media
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_attribute_list = upgrade_attribute_list_16(self, attribute_list)
        new_media = (privacy, new_citation_list, note_list, new_attribute_list,
                     ref, rect)
        new_media_list.append((new_media))
    return new_media_list


def upgrade_attribute_list_16(self, attribute_list):
    new_attribute_list = []
    for attribute in attribute_list:
        (privacy, source_list, note_list, the_type,
         value) = attribute
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_attribute = (privacy, new_citation_list, note_list,
                         the_type, value)
        new_attribute_list.append((new_attribute))
    return new_attribute_list


def upgrade_child_ref_list_16(self, child_ref_list):
    new_child_ref_list = []
    for child_ref in child_ref_list:
        (privacy, source_list, note_list, ref, frel, mrel) = child_ref
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_child_ref = (privacy, new_citation_list, note_list, ref,
                         frel, mrel)
        new_child_ref_list.append((new_child_ref))
    return new_child_ref_list


def upgrade_lds_seal_list_16(self, lds_seal_list):
    new_lds_seal_list = []
    for lds_seal in lds_seal_list:
        (source_list, note_list, date, type_, place,
         famc, temple, status, private) = lds_seal
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_lds_seal = (new_citation_list, note_list, date, type_, place,
                        famc, temple, status, private)
        new_lds_seal_list.append((new_lds_seal))
    return new_lds_seal_list


def upgrade_address_list_16(self, address_list):
    new_address_list = []
    for address in address_list:
        (privacy, source_list, note_list, date, location) = address
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_address = (privacy, new_citation_list, note_list, date, location)
        new_address_list.append((new_address))
    return new_address_list


def upgrade_name_list_16(self, name_list):
    new_name_list = []
    for name in name_list:
        new_name = upgrade_name_16(self, name)
        new_name_list.append((new_name))
    return new_name_list


def upgrade_name_16(self, name):
    (privacy, source_list, note, date, first_name, surname_list, suffix,
     title, name_type, group_as, sort_as, display_as, call, nick,
     famnick) = name
    new_citation_list = convert_source_list_to_citation_list_16(
        self, source_list)
    new_name = (privacy, new_citation_list, note, date, first_name,
                surname_list, suffix, title, name_type, group_as, sort_as,
                display_as, call, nick, famnick)
    return new_name


def upgrade_person_ref_list_16(self, person_ref_list):
    new_person_ref_list = []
    for person_ref in person_ref_list:
        (privacy, source_list, note_list, ref, rel) = person_ref
        new_citation_list = convert_source_list_to_citation_list_16(
            self, source_list)
        new_person_ref = (privacy, new_citation_list, note_list, ref, rel)
        new_person_ref_list.append((new_person_ref))
    return new_person_ref_list


def upgrade_event_ref_list_16(self, event_ref_list):
    new_event_ref_list = []
    for event_ref in event_ref_list:
        (privacy, note_list, attribute_list, ref, role) = event_ref
        new_attribute_list = upgrade_attribute_list_16(self, attribute_list)
        new_event_ref = (privacy, note_list, new_attribute_list, ref, role)
        new_event_ref_list.append((new_event_ref))
    return new_event_ref_list


def convert_source_list_to_citation_list_16(self, source_list):
    citation_list = []
    for source in source_list:
        (date, private, note_list, confidence, ref, page) = source
        new_handle = create_id()
        new_media_list = []
        new_data_map = {}
        new_change = time.time()
        new_gramps_id = self.citation_prefix % self.cmap_index
        new_citation = (new_handle, new_gramps_id,
                        date, page, confidence, ref, note_list, new_media_list,
                        new_data_map, new_change, private)
        citation_list.append((new_handle))
        self._commit_raw(new_citation, CITATION_KEY)
        self.cmap_index += 1
    return citation_list


def gramps_upgrade_15(self):
    """
    Upgrade database from version 14 to 15. This upgrade adds:

        * tagging
        * surname list
        * remove marker
    """
    length = (self.get_number_of_notes() + self.get_number_of_people() +
              self.get_number_of_events() + self.get_number_of_families() +
              self.get_number_of_repositories() + self.get_number_of_media() +
              self.get_number_of_places() + self.get_number_of_sources()) + 10
    self.set_total(length)
    self._txn_begin()
    self.tags = {}

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.get_person_handles():
        person = self.get_raw_person_data(handle)

        (junk_handle,         # 0
         gramps_id,           # 1
         gender,              # 2
         primary_name,        # 3
         alternate_names,     # 4
         death_ref_index,     # 5
         birth_ref_index,     # 6
         event_ref_list,      # 7
         family_list,         # 8
         parent_family_list,  # 9
         media_list,          # 10
         address_list,        # 11
         attribute_list,      # 12
         urls,                # 13
         ord_list,            # 14
         psource_list,        # 15
         pnote_list,          # 16
         change,              # 17
         marker,              # 18
         pprivate,            # 19
         person_ref_list,     # 20
         ) = person

        tag_handle = convert_marker(self, marker)
        if tag_handle:
            tags = [tag_handle]
        else:
            tags = []
        address_list = list(map(convert_address, address_list))
        new_primary_name = convert_name_15(primary_name)
        new_alternate_names = list(map(convert_name_15, alternate_names))
        new_person = (junk_handle,          # 0
                      gramps_id,            # 1
                      gender,               # 2
                      new_primary_name,     # 3
                      new_alternate_names,  # 4
                      death_ref_index,      # 5
                      birth_ref_index,      # 6
                      event_ref_list,       # 7
                      family_list,          # 8
                      parent_family_list,   # 9
                      media_list,           # 10
                      address_list,         # 11
                      attribute_list,       # 12
                      urls,                 # 13
                      ord_list,             # 14
                      psource_list,         # 15
                      pnote_list,           # 16
                      change,               # 17
                      tags,                 # 18
                      pprivate,             # 19
                      person_ref_list       # 20
                      )

        self._commit_raw(new_person, PERSON_KEY)
        self.update()

    # ---------------------------------
    # Modify Family
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.get_family_handles():
        family = self.get_raw_family_data(handle)
        new_family = list(family)
        tag_handle = convert_marker(self, new_family[13])
        if tag_handle:
            new_family[13] = [tag_handle]
        else:
            new_family[13] = []
        new_family = tuple(new_family)
        self._commit_raw(new_family, FAMILY_KEY)
        self.update()

    # ---------------------------------
    # Modify Note
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.get_note_handles():
        note = self.get_raw_note_data(handle)
        new_note = list(note)
        tag_handle = convert_marker(self, new_note[6])
        if tag_handle:
            new_note[6] = [tag_handle]
        else:
            new_note[6] = []
        new_note = tuple(new_note)
        self._commit_raw(new_note, NOTE_KEY)
        self.update()

    # ---------------------------------
    # Modify Media object
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.get_media_handles():
        media = self.get_raw_media_data(handle)
        new_media = list(media)
        new_media[10] = []
        new_media = tuple(new_media)
        self._commit_raw(new_media, MEDIA_KEY)
        self.update()

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.get_event_handles():
        event = self.get_raw_event_data(handle)
        new_event = list(event)
        new_event = new_event[:11] + new_event[12:]
        #new_event[11] = []
        new_event = tuple(new_event)
        self._commit_raw(new_event, EVENT_KEY)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    # Remove the old marker field, set new locality.
    for handle in self.get_place_handles():
        place = self.get_raw_place_data(handle)
        new_place = list(place)
        if new_place[5] is not None:
            new_place[5] = convert_location(new_place[5])
        new_place[6] = list(map(convert_location, new_place[6]))
        new_place = new_place[:12] + new_place[13:]
        new_place = tuple(new_place)
        self._commit_raw(new_place, PLACE_KEY)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    # Remove the old marker field.
    for handle in self.get_source_handles():
        source = self.get_raw_source_data(handle)
        new_source = list(source)
        new_source = new_source[:11] + new_source[12:]
        new_source = tuple(new_source)
        self._commit_raw(new_source, SOURCE_KEY)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # Remove the old marker field, set new locality.
    for handle in self.get_repository_handles():
        repository = self.get_raw_repository_data(handle)
        new_repository = list(repository)
        new_repository = new_repository[:8] + new_repository[9:]
        new_repository[5] = list(map(convert_address, new_repository[5]))
        new_repository = tuple(new_repository)
        self._commit_raw(new_repository, REPOSITORY_KEY)
        self.update()

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 15)


def convert_marker(self, marker_field):
    """Convert a marker into a tag."""
    marker = MarkerType()
    marker.unserialize(marker_field)
    tag_name = str(marker)

    if tag_name != '':
        if tag_name not in self.tags:
            tag = Tag()
            handle = create_id()
            tag.set_handle(handle)
            tag.set_change_time(time.time())
            tag.set_name(tag_name)
            tag.set_priority(len(self.tags))
            self._commit_raw(tag.serialize(), TAG_KEY)
            self.tags[tag_name] = handle
        return self.tags[tag_name]
    else:
        return None


def convert_locbase(loc):
    """Convert location base to include an empty locality field."""
    return tuple([loc[0], ''] + list(loc[1:]))


def convert_location(loc):
    """Convert a location into the new format."""
    return (convert_locbase(loc[0]), loc[1])


def convert_address(addr):
    """Convert an address into the new format."""
    return (addr[0], addr[1], addr[2], addr[3], convert_locbase(addr[4]))


def convert_name_15(name):
    (privacy, source_list, note_list, date,
     first_name, surname, suffix, title,
     name_type, prefix, patronymic,
     group_as, sort_as, display_as, call) = name

    connector = ""
    origintype = (NameOriginType.NONE, "")
    patorigintype = (NameOriginType.PATRONYMIC, "")

    if patronymic.strip() == "":
        #no patronymic, create a single surname
        surname_list = [(surname, prefix, True, origintype, connector)]
    else:
        #a patronymic, if no surname or equal as patronymic, a single surname
        if (surname.strip() == "") or (surname == patronymic and prefix == ""):
            surname_list = [
                (patronymic, prefix, True, patorigintype, connector)]
        else:
            #two surnames, first patronymic, then surname which is primary
            surname_list = [(patronymic, "", False, patorigintype, ""),
                            (surname, prefix, True, origintype, connector)]

    #return new value, add two empty strings for nick and family nick
    return (privacy, source_list, note_list, date,
            first_name, surname_list, suffix, title, name_type,
            group_as, sort_as, display_as, call, "", "")


def gramps_upgrade_14(self):
    """Upgrade database from version 13 to 14."""
    # This upgrade modifies notes and dates
    length = (self.get_number_of_notes() + self.get_number_of_people() +
              self.get_number_of_events() + self.get_number_of_families() +
              self.get_number_of_repositories() + self.get_number_of_media() +
              self.get_number_of_places() + self.get_number_of_sources())
    self.set_total(length)
    self._txn_begin()

    # ---------------------------------
    # Modify Notes
    # ---------------------------------
    # replace clear text with StyledText in Notes
    for handle in self.get_note_handles():
        note = self.get_raw_note_data(handle)
        (junk_handle, gramps_id, text, format_, note_type,
         change, marker, private) = note
        styled_text = (text, [])
        new_note = (handle, gramps_id, styled_text, format_, note_type,
                    change, marker, private)
        self._commit_raw(new_note, NOTE_KEY)
        self.update()

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # update dates with newyear
    for handle in self.get_event_handles():
        event = self.get_raw_event_data(handle)
        (junk_handle, gramps_id, the_type, date, description, place,
         source_list, note_list, media_list, attribute_list,
         change, marker, private) = event
        new_date = convert_date_14(date)
        new_source_list = new_source_list_14(source_list)
        new_media_list = new_media_list_14(media_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_event = (junk_handle, gramps_id, the_type, new_date, description,
                     place, new_source_list, note_list, new_media_list,
                     new_attribute_list, change, marker, private)
        self._commit_raw(new_event, EVENT_KEY)
        self.update()

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    # update dates with newyear
    for handle in self.get_person_handles():
        person = self.get_raw_person_data(handle)
        (junk_handle,         # 0
         gramps_id,           # 1
         gender,              # 2
         primary_name,        # 3
         alternate_names,     # 4
         death_ref_index,     # 5
         birth_ref_index,     # 6
         event_ref_list,      # 7
         family_list,         # 8
         parent_family_list,  # 9
         media_list,          # 10
         address_list,        # 11
         attribute_list,      # 12
         urls,                # 13
         lds_ord_list,        # 14
         psource_list,        # 15
         pnote_list,          # 16
         change,              # 17
         marker,              # 18
         pprivate,            # 19
         person_ref_list,     # 20
         ) = person

        new_address_list = []
        for address in address_list:
            (privacy, asource_list, anote_list, date, location) = address
            new_date = convert_date_14(date)
            new_asource_list = new_source_list_14(asource_list)
            new_address_list.append((privacy, new_asource_list, anote_list,
                                     new_date, location))
        new_ord_list = []
        for ldsord in lds_ord_list:
            (lsource_list, lnote_list, date, type_, place,
             famc, temple, status, lprivate) = ldsord
            new_date = convert_date_14(date)
            new_lsource_list = new_source_list_14(lsource_list)
            new_ord_list.append((new_lsource_list, lnote_list, new_date, type_,
                                 place, famc, temple, status, lprivate))

        new_primary_name = convert_name_14(primary_name)

        new_alternate_names = [convert_name_14(name) for name
                               in alternate_names]

        new_media_list = new_media_list_14(media_list)
        new_psource_list = new_source_list_14(psource_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_person_ref_list = new_person_ref_list_14(person_ref_list)

        new_person = (junk_handle,          # 0
                      gramps_id,            # 1
                      gender,               # 2
                      new_primary_name,     # 3
                      new_alternate_names,  # 4
                      death_ref_index,      # 5
                      birth_ref_index,      # 6
                      event_ref_list,       # 7
                      family_list,          # 8
                      parent_family_list,   # 9
                      new_media_list,       # 10
                      new_address_list,     # 11
                      new_attribute_list,   # 12
                      urls,                 # 13
                      new_ord_list,         # 14
                      new_psource_list,     # 15
                      pnote_list,           # 16
                      change,               # 17
                      marker,               # 18
                      pprivate,             # 19
                      new_person_ref_list,  # 20
                      )

        self._commit_raw(new_person, PERSON_KEY)
        self.update()

    # ---------------------------------
    # Modify Family
    # ---------------------------------
    # update dates with newyear
    for handle in self.get_family_handles():
        family = self.get_raw_family_data(handle)
        (junk_handle, gramps_id, father_handle, mother_handle,
         child_ref_list, the_type, event_ref_list, media_list,
         attribute_list, lds_seal_list, source_list, note_list,
         change, marker, private) = family
        new_child_ref_list = new_child_ref_list_14(child_ref_list)
        new_media_list = new_media_list_14(media_list)
        new_source_list = new_source_list_14(source_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_seal_list = []
        for ldsord in lds_seal_list:
            (lsource_list, lnote_list, date, type_, place,
             famc, temple, status, lprivate) = ldsord
            new_date = convert_date_14(date)
            new_lsource_list = new_source_list_14(lsource_list)
            new_seal_list.append((new_lsource_list, lnote_list, new_date,
                                  type_, place, famc, temple, status,
                                  lprivate))

        new_family = (junk_handle, gramps_id, father_handle, mother_handle,
                      new_child_ref_list, the_type, event_ref_list,
                      new_media_list, new_attribute_list, new_seal_list,
                      new_source_list, note_list, change, marker, private)

        self._commit_raw(new_family, FAMILY_KEY)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # update dates with newyear
    for handle in self.get_repository_handles():
        repository = self.get_raw_repository_data(handle)
        # address
        (junk_handle, gramps_id, the_type, name, note_list,
         address_list, urls, change, marker, private) = repository

        new_address_list = []
        for address in address_list:
            (privacy, asource_list, anote_list, date, location) = address
            new_date = convert_date_14(date)
            new_asource_list = new_source_list_14(asource_list)
            new_address_list.append((privacy, new_asource_list, anote_list,
                                     new_date, location))

        new_repository = (junk_handle, gramps_id, the_type, name, note_list,
                          new_address_list, urls, change, marker, private)

        self._commit_raw(new_repository, REPOSITORY_KEY)
        self.update()

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    for media_handle in self.get_media_handles():
        media = self.get_raw_media_data(media_handle)
        (handle, gramps_id, path, mime, desc,
         attribute_list, source_list, note_list, change,
         date, marker, private) = media
        new_source_list = new_source_list_14(source_list)
        new_date = convert_date_14(date)
        new_media = (handle, gramps_id, path, mime, desc,
                     attribute_list, new_source_list, note_list, change,
                     new_date, marker, private)

        self._commit_raw(new_media, MEDIA_KEY)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    for place_handle in self.get_place_handles():
        place = self.get_raw_place_data(place_handle)
        (handle, gramps_id, title, longi, lat,
         main_loc, alt_loc, urls, media_list, source_list, note_list,
         change, marker, private) = place
        new_media_list = new_media_list_14(media_list)
        new_source_list = new_source_list_14(source_list)
        new_place = (handle, gramps_id, title, longi, lat,
                     main_loc, alt_loc, urls, new_media_list,
                     new_source_list, note_list, change, marker, private)

        self._commit_raw(new_place, PLACE_KEY)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    for source_handle in self.get_source_handles():
        source = self.get_raw_source_data(source_handle)
        (handle, gramps_id, title, author,
         pubinfo, note_list, media_list,
         abbrev, change, datamap, reporef_list,
         marker, private) = source
        new_media_list = new_media_list_14(media_list)
        new_source = (handle, gramps_id, title, author,
                      pubinfo, note_list, new_media_list,
                      abbrev, change, datamap, reporef_list,
                      marker, private)

        self._commit_raw(new_source, SOURCE_KEY)
        self.update()

    self._txn_commit()
    # Bump up database version. Separate transaction to save metadata.
    self._set_metadata('version', 14)


def new_source_list_14(source_list):
    new_source_list = []
    for source in source_list:
        (date, private, note_list, confidence, ref, page) = source
        new_date = convert_date_14(date)
        new_source_list.append((new_date, private, note_list, confidence, ref,
                                page))
    return new_source_list


def new_attribute_list_14(attribute_list):
    new_attribute_list = []
    for attribute in attribute_list:
        (private, asource_list, note_list, the_type, value) = attribute
        new_asource_list = new_source_list_14(asource_list)
        new_attribute_list.append((private, new_asource_list, note_list,
                                   the_type, value))
    return new_attribute_list


def new_media_list_14(media_list):
    # ---------------------------------
    # Event Media list
    # ---------------------------------
    new_media_list = []
    for media in media_list:
        (private, source_list, note_list, attribute_list, ref, role) = media
        new_source_list = new_source_list_14(source_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_media_list.append((private, new_source_list, note_list,
                               new_attribute_list, ref, role))
    return new_media_list


def new_person_ref_list_14(person_ref_list):
    new_person_ref_list = []
    for person_ref in person_ref_list:
        (private, source_list, note_list, ref, rel) = person_ref
        new_source_list = new_source_list_14(source_list)
        new_person_ref_list.append((private, new_source_list, note_list, ref,
                                    rel))
    return new_person_ref_list


def new_child_ref_list_14(child_ref_list):
    new_child_ref_list = []
    for data in child_ref_list:
        (private, source_list, note_list, ref, frel, mrel) = data
        new_source_list = new_source_list_14(source_list)
        new_child_ref_list.append((private, new_source_list, note_list, ref,
                                   frel, mrel))
    return new_child_ref_list


def convert_date_14(date):
    if date:
        (calendar, modifier, quality, dateval, text, sortval) = date
        return (calendar, modifier, quality, dateval, text, sortval, 0)
    else:
        return None


def convert_name_14(name):
    (privacy, source_list, note_list, date,
     first_name, surname, suffix, title,
     name_type, prefix, patronymic,
     group_as, sort_as, display_as, call) = name
    new_date = convert_date_14(date)
    new_source_list = new_source_list_14(source_list)
    return (privacy, new_source_list, note_list, new_date,
            first_name, surname, suffix, title,
            name_type, prefix, patronymic,
            group_as, sort_as, display_as, call)


def make_zip_backup(dirname):
    """
    This backs up the db files so an upgrade can be (manually) undone.
    """
    LOG.debug("Make backup prior to schema upgrade")
    import zipfile
    # In Windows reserved characters is "<>:"/\|?*"
    reserved_char = r':,<>"/\|?* '
    replace_char = "-__________"
    filepath = os.path.join(dirname, NAME_FILE)
    with open(filepath, "r", encoding='utf8') as name_file:
        title = name_file.readline().strip()
    trans = title.maketrans(reserved_char, replace_char)
    title = title.translate(trans)

    if not os.access(dirname, os.W_OK):
        LOG.warning("Can't write technical DB backup for %s", title)
        return
    (grampsdb_path, db_code) = os.path.split(dirname)
    dotgramps_path = os.path.dirname(grampsdb_path)
    zipname = title + time.strftime("_%Y-%m-%d_%H-%M-%S") + ".zip"
    zippath = os.path.join(dotgramps_path, zipname)
    with zipfile.ZipFile(zippath, 'w') as myzip:
        for filename in os.listdir(dirname):
            pathname = os.path.join(dirname, filename)
            myzip.write(pathname, os.path.join(db_code, filename))
    LOG.warning("If upgrade and loading the Family Tree works, you can "
                "delete the zip file at %s", zippath)
