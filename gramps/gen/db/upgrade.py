#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

from __future__ import with_statement, unicode_literals

import sys
import os
from ..lib.markertype import MarkerType
from ..lib.tag import Tag
from ..utils.file import create_checksum
import time
import logging
LOG = logging.getLogger(".citation")

from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ..constfunc import cuni, UNITYPE

"""
methods to upgrade a database from version 13 to current version
"""
from ..config import config
if config.get('preferences.use-bsddb3') or sys.version_info[0] >= 3:
    from bsddb3 import db
else:
    from bsddb import db
from . import BSDDBTxn
from ..lib.nameorigintype import NameOriginType
from .write import _mkname, SURNAMES
from .dbconst import (PERSON_KEY, FAMILY_KEY, EVENT_KEY, 
                            MEDIA_KEY, PLACE_KEY, REPOSITORY_KEY)
from gramps.gui.dialog import (InfoDialog)

def gramps_upgrade_17(self):
    """Upgrade database from version 16 to 17. 
       1. This upgrade adds tags to event, place, repository, source and 
          citation objects.
       2. Data of Source becomes SourceAttributes Secondary Object
       3. Add checksum field to media objects.
    """
    length = (len(self.event_map) + len(self.place_map) +
              len(self.repository_map) + len(self.source_map) +
              len(self.citation_map) + len(self.media_map))
    self.set_total(length)

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.event_map.keys():
        event = self.event_map[handle]
        new_event = list(event)
        new_event = new_event[:11] + [[]] + new_event[11:]
        new_event = tuple(new_event)
        with BSDDBTxn(self.env, self.event_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_event)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.place_map.keys():
        place = self.place_map[handle]
        new_place = list(place)
        new_place = new_place[:12] + [[]] + new_place[12:]
        new_place = tuple(new_place)
        with BSDDBTxn(self.env, self.place_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_place)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.repository_map.keys():
        repository = self.repository_map[handle]
        new_repository = list(repository)
        new_repository = new_repository[:8] + [[]] + new_repository[8:]
        new_repository = tuple(new_repository)
        with BSDDBTxn(self.env, self.repository_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_repository)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.source_map.keys():
        source = self.source_map[handle]
        new_source = list(source)
        new_source = new_source[:11] + [[]] + new_source[11:]
        new_source = tuple(new_source)
        with BSDDBTxn(self.env, self.source_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_source)
        self.update()

    # ---------------------------------
    # Modify Citation
    # ---------------------------------
    # Add new tag_list field.
    for handle in self.citation_map.keys():
        citation = self.citation_map[handle]
        new_citation = list(citation)
        new_citation = new_citation[:10] + [[]] + new_citation[10:]
        new_citation = tuple(new_citation)
        with BSDDBTxn(self.env, self.citation_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_citation)
        self.update()

    # -------------------------------------------------------
    # Upgrade Source and Citation datamap to SrcAttributeBase
    # -------------------------------------------------------
    for handle in self.source_map.keys():
        source = self.source_map[handle]
        (handle, gramps_id, title, author, pubinfo,
            notelist, medialist, abbrev, change, datamap, reporef_list,
            taglist, private) = source
        srcattributelist = upgrade_datamap_17(datamap)
        new_source = (handle, gramps_id, title, author, pubinfo,
            notelist, medialist, abbrev, change, srcattributelist, reporef_list,
            taglist, private)
        with BSDDBTxn(self.env, self.source_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_source)
        self.update()

    for handle in self.citation_map.keys():
        citation = self.citation_map[handle]
        (handle, gramps_id, datelist, page, confidence, source_handle, 
            notelist, medialist, datamap, change, taglist, private) = citation
        srcattributelist = upgrade_datamap_17(datamap)
        new_citation = (handle, gramps_id, datelist, page, confidence, source_handle, 
            notelist, medialist, srcattributelist, change, taglist, private)
        with BSDDBTxn(self.env, self.citation_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_citation)
        self.update()

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    # Add new checksum field.
    base_path = self.metadata[b'mediapath']
    for handle in self.media_map.keys():
        media = self.media_map[handle]
        new_media = list(media)
        if os.path.isabs(new_media[2]):
            full_path = new_media[2]
        else:
            full_path = os.path.join(base_path, new_media[2])
        checksum = create_checksum(full_path)
        new_media = new_media[:5] + [checksum] + new_media[5:]
        new_media = tuple(new_media)
        with BSDDBTxn(self.env, self.media_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_media)
        self.update()

    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put(b'version', 17)

def upgrade_datamap_17(datamap):
    """
    In version 16 key value pairs are stored in source and citation. These become
    SrcAttribute
    """
    new_srcattr_list = []
    private = False
    from ..lib.srcattrtype import SrcAttributeType
    for (key, value) in datamap.iteritems():
        the_type = SrcAttributeType(key).serialize()
        new_srcattr_list.append((private, the_type, value))
    return new_srcattr_list

def gramps_upgrade_16(self):
    """Upgrade database from version 15 to 16. This upgrade converts all
       SourceRef child objects to Citation Primary objects.
       
       For each primary object that has a sourceref, what we have to do is: 
       
             (1) create each citation
             (2) update the object to reference the Citations
             (3) remove backlinks for references from object to Source
             (4) add backlinks for references from object to Citations
             (5) add backlinks for references from Citation to Source
            
        the backlinks are all updated at the end by calling
        reindex_reference_map

    """
    length = (len(self.note_map) + len(self.person_map) +
              len(self.event_map) + len(self.family_map) +
              len(self.repository_map) + len(self.media_map) +
              len(self.place_map) + len(self.source_map)) + 10
    self.set_total(length)

    # Setup data for upgrade statistics information dialogue
    keyorder = [PERSON_KEY, FAMILY_KEY, EVENT_KEY, MEDIA_KEY, 
                PLACE_KEY, REPOSITORY_KEY]
    key2data = {
            PERSON_KEY : 0,
            FAMILY_KEY : 1,
            EVENT_KEY: 2, 
            MEDIA_KEY: 3, 
            PLACE_KEY: 4,
            REPOSITORY_KEY: 5, 
            }
    key2string = {
        PERSON_KEY      : _('%6d  People        upgraded with %6d citations in %6d secs\n'),
        FAMILY_KEY      : _('%6d  Families      upgraded with %6d citations in %6d secs\n'),
        EVENT_KEY       : _('%6d  Events        upgraded with %6d citations in %6d secs\n'),
        MEDIA_KEY       : _('%6d  Media Objects upgraded with %6d citations in %6d secs\n'),
        PLACE_KEY       : _('%6d  Places        upgraded with %6d citations in %6d secs\n'),
        REPOSITORY_KEY  : _('%6d  Repositories  upgraded with %6d citations in %6d secs\n'),
        }
    data_upgradeobject = [0] * 6

    # Initialise the citation gramps ID number
    self.cmap_index = 0

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for person_handle in self.person_map.keys():
        person = self.person_map[person_handle]
        (handle, gramps_id, gender, primary_name, alternate_names, 
         death_ref_index, birth_ref_index, event_ref_list, family_list, 
         parent_family_list, media_list, address_list, attribute_list, 
         urls, lds_seal_list, source_list, note_list, change, tag_list, 
         private, person_ref_list) = person
        if primary_name:
            primary_name = upgrade_name_16(self, primary_name)
        if alternate_names:
            alternate_names = upgrade_name_list_16(
                                    self, alternate_names)
        if address_list:
            address_list = upgrade_address_list_16(
                                    self, address_list)
        if media_list:
            media_list = upgrade_media_list_16(
                                    self, media_list)
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(
                                    self, attribute_list)
        if lds_seal_list:
            lds_seal_list = upgrade_lds_seal_list_16(
                                    self, lds_seal_list)
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                                    self, source_list)
        else:
            new_citation_list = []
        if person_ref_list:
            person_ref_list = upgrade_person_ref_list_16(
                                    self, person_ref_list)
        if event_ref_list:
            event_ref_list = upgrade_event_ref_list_16(self, event_ref_list)
        if primary_name or alternate_names  or address_list or \
           media_list or attribute_list or lds_seal_list or source_list or \
           person_ref_list or event_ref_list:
            new_person = (handle, gramps_id, gender, primary_name, 
                          alternate_names, death_ref_index, 
                          birth_ref_index, event_ref_list, family_list, 
                          parent_family_list, media_list, address_list, 
                          attribute_list, urls, lds_seal_list, 
                          new_citation_list, note_list, change, tag_list, 
                          private, person_ref_list)
            with BSDDBTxn(self.env, self.person_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, new_person)
        self.update()

    LOG.debug("%d persons upgraded with %d citations in %d seconds. " % 
              (len(list(self.person_map.keys())), 
               self.cmap_index - start_num_citations, 
               time.time() - start_time))
    data_upgradeobject[key2data[PERSON_KEY]] = (len(list(self.person_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for media_handle in self.media_map.keys():
        media = self.media_map[media_handle]
        LOG.debug("upgrade media %s" % media[4])
        (handle, gramps_id, path, mime, desc,
         attribute_list, source_list, note_list, change,
         date, tag_list, private) = media
        new_citation_list = convert_source_list_to_citation_list_16(
                                   self, source_list)
        new_attribute_list = upgrade_attribute_list_16(
                                   self, attribute_list)
            
        new_media = (handle, gramps_id, path, mime, desc,
                     new_attribute_list, new_citation_list, note_list, 
                     change, date, tag_list, private)
        LOG.debug("      upgrade new_media %s" % [new_media])
        with BSDDBTxn(self.env, self.media_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_media)
        LOG.debug("      update ref map media %s" % [handle,
                        self.get_object_from_handle(handle) ])
        self.update()

    LOG.debug("Media upgrade %d citations upgraded in %d seconds" % 
              (self.cmap_index - start_num_citations, 
               int(time.time() - start_time)))
    data_upgradeobject[key2data[MEDIA_KEY]] = (len(list(self.media_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)

    # ---------------------------------
    # Modify Places
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for place_handle in self.place_map.keys():
        place = self.place_map[place_handle]
        (handle, gramps_id, title, longi, lat,
         main_loc, alt_loc, urls, media_list, source_list, note_list,
         change, private) = place
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                                    self, source_list)
        else:
            new_citation_list = []
        if media_list:
            media_list = upgrade_media_list_16(
                                    self, media_list)
        if source_list or media_list:
            new_place = (handle, gramps_id, title, 
                         longi, lat, main_loc, alt_loc, urls,
                         media_list, new_citation_list, note_list, 
                         change, private)
            with BSDDBTxn(self.env, self.place_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, new_place)
        self.update()

    LOG.debug("%d places upgraded with %d citations in %d seconds. " % 
              (len(list(self.place_map.keys())), 
               self.cmap_index - start_num_citations, 
               time.time() - start_time))
    data_upgradeobject[key2data[PLACE_KEY]] = (len(list(self.place_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)

    # ---------------------------------
    # Modify Families
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for family_handle in self.family_map.keys():
        family = self.family_map[family_handle]
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
            child_ref_list = upgrade_child_ref_list_16(
                                    self, child_ref_list)
        if lds_seal_list:
            lds_seal_list = upgrade_lds_seal_list_16(
                                    self, lds_seal_list)
        if media_list:
            media_list = upgrade_media_list_16(
                                    self, media_list)
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(
                                    self, attribute_list)
        if event_ref_list:
            event_ref_list = upgrade_event_ref_list_16(self, event_ref_list)
        if source_list or media_list or child_ref_list or \
            attribute_list or lds_seal_list or event_ref_list:
            new_family = (handle, gramps_id, father_handle, mother_handle,
                          child_ref_list, the_type, event_ref_list, media_list,
                          attribute_list, lds_seal_list, new_citation_list, 
                          note_list, change, tag_list, private)
            with BSDDBTxn(self.env, self.family_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, new_family)
        self.update()

    LOG.debug("%d familys upgraded with %d citations in %d seconds. " % 
              (len(list(self.family_map.keys())), 
               self.cmap_index - start_num_citations, 
               time.time() - start_time))
    data_upgradeobject[key2data[FAMILY_KEY]] = (len(list(self.family_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)
    # ---------------------------------
    # Modify Events
    # ---------------------------------
    upgrade_time = 0
    backlink_time = 0
    start_num_citations = self.cmap_index
    start_time = time.time()
    for event_handle in self.event_map.keys():
        t1 = time.time()
        event = self.event_map[event_handle]
        (handle, gramps_id, the_type, date, description, place, 
         source_list, note_list, media_list, attribute_list,
         change, private) = event
        if source_list:
            new_citation_list = convert_source_list_to_citation_list_16(
                                    self, source_list)
        else:
            new_citation_list = []
        if attribute_list:
            attribute_list = upgrade_attribute_list_16(
                                    self, attribute_list)
        if media_list:
            media_list = upgrade_media_list_16(
                                    self, media_list)
        if source_list or attribute_list or media_list:
            new_event = (handle, gramps_id, the_type, date, description, place,
                         new_citation_list, note_list, media_list,
                         attribute_list, 
                         change, private)
            with BSDDBTxn(self.env, self.event_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, new_event)
        t2 = time.time()
        upgrade_time += t2 - t1
        t3 = time.time()
        backlink_time += t3 - t2
        self.update()

    LOG.debug("%d events upgraded with %d citations in %d seconds. "
              "Backlinks took %d seconds" % 
              (len(list(self.event_map.keys())), 
               self.cmap_index - start_num_citations, 
               int(upgrade_time), int(backlink_time)))
    data_upgradeobject[key2data[EVENT_KEY]] = (len(list(self.event_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)

    # ---------------------------------
    # Modify Repositories
    # ---------------------------------
    start_num_citations = self.cmap_index
    start_time = time.time()
    for repository_handle in self.repository_map.keys():
        repository = self.repository_map[repository_handle]
        (handle, gramps_id, the_type, name, note_list,
         address_list, urls, change, private) = repository
        if address_list:
            address_list = upgrade_address_list_16(
                                    self, address_list)
        if address_list:
            new_repository = (handle, gramps_id, the_type, name, note_list,
                              address_list, urls, change, private)
            with BSDDBTxn(self.env, self.repository_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, new_repository)
        self.update()

    LOG.debug("%d repositorys upgraded with %d citations in %d seconds. " % 
              (len(list(self.repository_map.keys())), 
               self.cmap_index - start_num_citations, 
               time.time() - start_time))
    data_upgradeobject[key2data[REPOSITORY_KEY]] = (len(list(self.repository_map.keys())),
                                       self.cmap_index - start_num_citations,
                                       time.time() - start_time)
    # ---------------------------------

    
    # ---------------------------------
    # Example database from repository took:
    # 3403 events upgraded with 8 citations in 23 seconds. Backlinks took 1071 seconds
    # actually 4 of these citations were from:
    # Media upgrade 4 citations upgraded in 4 seconds         
    # by only doing the backlinks when there might be something to do,
    # improved to:
    # 3403 events upgraded with 8 citations in 19 seconds. Backlinks took 1348 seconds
    # further improved by skipping debug logging:
    # 3403 events upgraded with 8 citations in 2 seconds. Backlinks took 167 seconds
    
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

# without incorrect nestetd tranaction structure:
#Number of new objects upgraded:
#    73  People        upgraded with     76 citations in      0 secs
#    35  Families      upgraded with     36 citations in      0 secs
#  3403  Events        upgraded with      4 citations in      0 secs
#     7  Media Objects upgraded with      4 citations in      0 secs
#   852  Places        upgraded with      0 citations in      0 secs

#[[(73, 76, 0.12430405616760254), (35, 36, 0.042523860931396484), (3403, 4, 0.52303886413574219), (7, 4, 0.058229923248291016), (852, 0, 0.14816904067993164)]]






    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put(b'version', 16)
        
    LOG.debug([data_upgradeobject])
    txt = _("Number of new objects upgraded:\n")
    for key in keyorder:
        try:
            txt += key2string[key] % data_upgradeobject[key2data[key]]
        except:
            txt += key2string[key]
    txt += _("\n\nYou may want to run\n"
             "Tools -> Family Tree Processing -> Merge\n"
             "in order to merge citations that contain similar\n"
             "information")
    InfoDialog(_('Upgrade Statistics'), txt, monospaced=True)

def upgrade_media_list_16(self, media_list):
    new_media_list = []
    for media in media_list:
        (privacy, source_list, note_list, attribute_list, ref, rect) = media
        new_citation_list = convert_source_list_to_citation_list_16(
                                        self, source_list)
        new_attribute_list = upgrade_attribute_list_16(
                                        self, attribute_list)
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
        new_child_ref = (privacy, new_citation_list, note_list, ref, frel, mrel)
        new_child_ref_list.append((new_child_ref))
    return new_child_ref_list

def upgrade_lds_seal_list_16(self, lds_seal_list):
    new_lds_seal_list = []
    for lds_seal in lds_seal_list:
        (source_list, note_list, date, type, place,
         famc, temple, status, private) = lds_seal
        new_citation_list = convert_source_list_to_citation_list_16(
                                        self, source_list)
        new_lds_seal = (new_citation_list, note_list, date, type, place,
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
        new_attribute_list = upgrade_attribute_list_16(
                                        self, attribute_list)
        new_event_ref = (privacy, note_list, new_attribute_list, ref, role)
        new_event_ref_list.append((new_event_ref))
    return new_event_ref_list

def convert_source_list_to_citation_list_16(self, source_list):
    citation_list = []
    for source in source_list:
        (date, private, note_list, confidence, ref, page) = source
        new_handle = self.create_id()
        new_media_list = []
        new_data_map = {}
        new_change = time.time()
        new_gramps_id = self.citation_prefix % self.cmap_index
        new_citation = (new_handle, new_gramps_id,
                        date, page, confidence, ref, note_list, new_media_list,
                        new_data_map, new_change, private)
        with BSDDBTxn(self.env, self.citation_map) as txn:
            if isinstance(new_handle, UNITYPE):
                new_handle = new_handle.encode('utf-8')
            txn.put(new_handle, new_citation)
        self.cmap_index += 1
#        # add backlinks for references from Citation to Source
#        with BSDDBTxn(self.env) as txn:
#            self.update_reference_map( 
#                    self.get_citation_from_handle(new_handle),
#                    transaction,
#                    txn.txn)
        citation_list.append((new_handle))
    return citation_list

def gramps_upgrade_15(self):
    """Upgrade database from version 14 to 15. This upgrade adds:
         * tagging
         * surname list
         * remove marker
    """
    length = (len(self.note_map) + len(self.person_map) +
              len(self.event_map) + len(self.family_map) +
              len(self.repository_map) + len(self.media_map) +
              len(self.place_map) + len(self.source_map)) + 10
    self.set_total(length)
    self.tags = {}

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.person_map.keys():
        person = self.person_map[handle]

        (junk_handle,        #  0
         gramps_id,          #  1
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
         urls,               # 13
         ord_list,           # 14
         psource_list,       # 15
         pnote_list,         # 16
         change,             # 17
         marker,             # 18
         pprivate,           # 19
         person_ref_list,    # 20
         ) = person

        tag_handle = convert_marker(self, marker)
        if tag_handle:
            tags = [tag_handle]
        else:
            tags = []
        address_list = list(map(convert_address, address_list))
        new_primary_name = convert_name_15(primary_name)
        new_alternate_names = list(map(convert_name_15, alternate_names))
        new_person = (junk_handle,        #  0
                      gramps_id,          #  1
                      gender,             #  2
                      new_primary_name,   #  3
                      new_alternate_names,#  4
                      death_ref_index,    #  5
                      birth_ref_index,    #  6
                      event_ref_list,     #  7
                      family_list,        #  8
                      parent_family_list, #  9
                      media_list,         # 10
                      address_list,       # 11
                      attribute_list,     # 12
                      urls,               # 13
                      ord_list,           # 14
                      psource_list,       # 15
                      pnote_list,         # 16
                      change,             # 17
                      tags,               # 18
                      pprivate,           # 19
                      person_ref_list     # 20
                      )

        with BSDDBTxn(self.env, self.person_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_person)
        self.update()
    #surname is now different, remove secondary index with names
    _db = db.DB(self.env)
    try:
        _db.remove(_mkname(self.full_name, SURNAMES), SURNAMES)
    except db.DBNoSuchFileError:
        pass

    # ---------------------------------
    # Modify Family
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.family_map.keys():
        family = self.family_map[handle]
        new_family = list(family)
        tag_handle = convert_marker(self, new_family[13])
        if tag_handle:
            new_family[13] = [tag_handle]
        else:
            new_family[13] = []
        new_family = tuple(new_family)
        with BSDDBTxn(self.env, self.family_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_family)
        self.update()

    # ---------------------------------
    # Modify Note
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.note_map.keys():
        note = self.note_map[handle]
        new_note = list(note)
        tag_handle = convert_marker(self, new_note[6])
        if tag_handle:
            new_note[6] = [tag_handle]
        else:
            new_note[6] = []
        new_note = tuple(new_note)
        with BSDDBTxn(self.env, self.note_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_note)
        self.update()

    # ---------------------------------
    # Modify Media object
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.media_map.keys():
        media = self.media_map[handle]
        new_media = list(media)
        new_media[10] = []
        new_media = tuple(new_media)
        with BSDDBTxn(self.env, self.media_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_media)
        self.update()

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # Replace the old marker field with the new tag list field.
    for handle in self.event_map.keys():
        event = self.event_map[handle]
        new_event = list(event)
        new_event = new_event[:11] + new_event[12:]
        #new_event[11] = []
        new_event = tuple(new_event)
        with BSDDBTxn(self.env, self.event_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_event)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    # Remove the old marker field, set new locality.
    for handle in self.place_map.keys():
        place = self.place_map[handle]
        new_place = list(place)
        if new_place[5] is not None:
            new_place[5] = convert_location(new_place[5])
        new_place[6] = list(map(convert_location, new_place[6]))
        new_place = new_place[:12] + new_place[13:]
        new_place = tuple(new_place)
        with BSDDBTxn(self.env, self.place_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_place)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    # Remove the old marker field.
    for handle in self.source_map.keys():
        source = self.source_map[handle]
        new_source = list(source)
        new_source = new_source[:11] + new_source[12:]
        new_source = tuple(new_source)
        with BSDDBTxn(self.env, self.source_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_source)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # Remove the old marker field, set new locality.
    for handle in self.repository_map.keys():
        repository = self.repository_map[handle]
        new_repository = list(repository)
        new_repository = new_repository[:8] + new_repository[9:]
        new_repository[5] = list(map(convert_address, new_repository[5]))
        new_repository = tuple(new_repository)
        with BSDDBTxn(self.env, self.repository_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_repository)
        self.update()

    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put(b'version', 15)

def convert_marker(self, marker_field):
    """Convert a marker into a tag."""
    marker = MarkerType()
    marker.unserialize(marker_field)
    tag_name = cuni(marker)
    
    if tag_name != '':
        if tag_name not in self.tags:
            tag = Tag()
            handle = self.create_id()
            tag.set_handle(handle)
            tag.set_change_time(time.time())
            tag.set_name(tag_name)
            tag.set_priority(len(self.tags))
            with BSDDBTxn(self.env, self.tag_map) as txn:
                if isinstance(handle, UNITYPE):
                    handle = handle.encode('utf-8')
                txn.put(handle, tag.serialize())
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
            surname_list = [(patronymic, prefix, True, patorigintype, connector)]
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
    length = (len(self.note_map) + len(self.person_map) +
              len(self.event_map) + len(self.family_map) +
              len(self.repository_map) + len(self.media_map) +
              len(self.place_map) + len(self.source_map))
    self.set_total(length)

    # ---------------------------------
    # Modify Notes
    # ---------------------------------
    # replace clear text with StyledText in Notes
    for handle in self.note_map.keys():
        note = self.note_map[handle]
        (junk_handle, gramps_id, text, format, note_type,
         change, marker, private) = note
        styled_text = (text, [])
        new_note = (handle, gramps_id, styled_text, format, note_type,
                    change, marker, private)
        with BSDDBTxn(self.env, self.note_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_note)
        self.update()

    # ---------------------------------
    # Modify Event
    # ---------------------------------
    # update dates with newyear
    for handle in self.event_map.keys():
        event = self.event_map[handle]
        (junk_handle, gramps_id, the_type, date, description, place, 
         source_list, note_list, media_list, attribute_list,
         change, marker, private) = event
        new_date = convert_date_14(date)
        new_source_list = new_source_list_14(source_list)
        new_media_list = new_media_list_14(media_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_event = (junk_handle, gramps_id, the_type, new_date,
                     description, place, new_source_list, note_list, 
                     new_media_list, new_attribute_list, change,marker,private)
        with BSDDBTxn(self.env, self.event_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_event)
        self.update()

    # ---------------------------------
    # Modify Person
    # ---------------------------------
    # update dates with newyear
    for handle in self.person_map.keys():
        person = self.person_map[handle]
        (junk_handle,        #  0
         gramps_id,          #  1
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
         urls,               # 13
         lds_ord_list,       # 14
         psource_list,       # 15
         pnote_list,         # 16
         change,             # 17
         marker,             # 18
         pprivate,           # 19
         person_ref_list,    # 20
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
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            new_date = convert_date_14(date)
            new_lsource_list = new_source_list_14(lsource_list)
            new_ord_list.append( (new_lsource_list, lnote_list, new_date, type, 
                                  place, famc, temple, status, lprivate))

        new_primary_name = convert_name_14(primary_name)

        new_alternate_names = [convert_name_14(name) for name 
                               in alternate_names]
        
        new_media_list = new_media_list_14(media_list)
        new_psource_list = new_source_list_14(psource_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_person_ref_list = new_person_ref_list_14(person_ref_list)

        new_person = (junk_handle,        #  0
                      gramps_id,          #  1
                      gender,             #  2
                      new_primary_name,       #  3
                      new_alternate_names,    #  4
                      death_ref_index,    #  5
                      birth_ref_index,    #  6
                      event_ref_list,     #  7
                      family_list,        #  8
                      parent_family_list, #  9
                      new_media_list,         # 10
                      new_address_list,       # 11
                      new_attribute_list,     # 12
                      urls,               # 13
                      new_ord_list,          # 14
                      new_psource_list,       # 15
                      pnote_list,         # 16
                      change,             # 17
                      marker,             # 18
                      pprivate,           # 19
                      new_person_ref_list,    # 20
                      )

        with BSDDBTxn(self.env, self.person_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_person)
        self.update()

    # ---------------------------------
    # Modify Family
    # ---------------------------------
    # update dates with newyear
    for handle in self.family_map.keys():
        family = self.family_map[handle]
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
            (lsource_list, lnote_list, date, type, place,
             famc, temple, status, lprivate) = ldsord
            new_date = convert_date_14(date)
            new_lsource_list = new_source_list_14(lsource_list)
            new_seal_list.append( (new_lsource_list, lnote_list, new_date, type, 
                                   place, famc, temple, status, lprivate))

        new_family = (junk_handle, gramps_id, father_handle, mother_handle,
                      new_child_ref_list, the_type, event_ref_list, new_media_list,
                      new_attribute_list, new_seal_list, new_source_list, note_list,
                      change, marker, private)

        with BSDDBTxn(self.env, self.family_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_family)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # update dates with newyear
    for handle in self.repository_map.keys():
        repository = self.repository_map[handle]
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

        with BSDDBTxn(self.env, self.repository_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_repository)
        self.update()

    # ---------------------------------
    # Modify Media
    # ---------------------------------
    for media_handle in self.media_map.keys():
        media = self.media_map[media_handle]
        (handle, gramps_id, path, mime, desc,
         attribute_list, source_list, note_list, change,
         date, marker, private) = media
        new_source_list = new_source_list_14(source_list)
        new_date = convert_date_14(date)
        new_media = (handle, gramps_id, path, mime, desc,
                     attribute_list, new_source_list, note_list, change,
                     new_date, marker, private)

        with BSDDBTxn(self.env, self.media_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_media)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    for place_handle in self.place_map.keys():
        place = self.place_map[place_handle]
        (handle, gramps_id, title, longi, lat,
         main_loc, alt_loc, urls, media_list, source_list, note_list,
         change, marker, private) = place
        new_media_list = new_media_list_14(media_list)
        new_source_list = new_source_list_14(source_list)
        new_place = (handle, gramps_id, title, longi, lat,
                     main_loc, alt_loc, urls, new_media_list, 
                     new_source_list, note_list, change, marker, private) 

        with BSDDBTxn(self.env, self.place_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_place)
        self.update()

    # ---------------------------------
    # Modify Source
    # ---------------------------------
    for source_handle in self.source_map.keys():
        source = self.source_map[source_handle]
        (handle, gramps_id, title, author,
         pubinfo, note_list, media_list,
         abbrev, change, datamap, reporef_list,
         marker, private) = source
        new_media_list = new_media_list_14(media_list)
        new_source = (handle, gramps_id, title, author,
                      pubinfo, note_list, new_media_list,
                      abbrev, change, datamap, reporef_list,
                      marker, private)

        with BSDDBTxn(self.env, self.source_map) as txn:
            if isinstance(handle, UNITYPE):
                handle = handle.encode('utf-8')
            txn.put(handle, new_source)
        self.update()

    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put(b'version', 14)

def new_source_list_14(source_list):
    new_source_list = []
    for source in source_list:
        (date, private, note_list, confidence, ref, page) = source
        new_date = convert_date_14(date)
        new_source_list.append((new_date, private, note_list, confidence, ref, page))
    return new_source_list

def new_attribute_list_14(attribute_list):
    new_attribute_list = []
    for attribute in attribute_list:
        (private, asource_list, note_list, the_type, value) = attribute
        new_asource_list = new_source_list_14(asource_list)
        new_attribute_list.append((private, new_asource_list, note_list, the_type, value))
    return new_attribute_list

def new_media_list_14(media_list):
    # ---------------------------------
    # Event Media list
    # ---------------------------------
    new_media_list = []
    for media in media_list:
        (private, source_list, note_list,attribute_list,ref,role) = media
        new_source_list = new_source_list_14(source_list)
        new_attribute_list = new_attribute_list_14(attribute_list)
        new_media_list.append((private, new_source_list, note_list, new_attribute_list, ref, role))
    return new_media_list

def new_person_ref_list_14(person_ref_list):
    new_person_ref_list = []
    for person_ref in person_ref_list:
        (private, source_list, note_list, ref, rel) = person_ref
        new_source_list = new_source_list_14(source_list)
        new_person_ref_list.append((private, new_source_list, note_list, ref, rel))
    return new_person_ref_list

def new_child_ref_list_14(child_ref_list):
    new_child_ref_list = []
    for data in child_ref_list:
        (private, source_list, note_list, ref, frel, mrel) = data
        new_source_list = new_source_list_14(source_list)
        new_child_ref_list.append((private, new_source_list, note_list, ref, frel, mrel))
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

