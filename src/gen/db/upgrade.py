#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

from __future__ import with_statement

from gen.lib.markertype import MarkerType
from gen.lib.tag import Tag
import time

"""
methods to upgrade a database from version 13 to current version
"""
import config
if config.get('preferences.use-bsddb3'):
    from bsddb3 import db
else:
    from bsddb import db
from gen.db import BSDDBTxn
from gen.lib.nameorigintype import NameOriginType
from gen.db.write import _mkname, SURNAMES

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
        address_list = map(convert_address, address_list)
        new_primary_name = convert_name_15(primary_name)
        new_alternate_names = map(convert_name_15, alternate_names)
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
            txn.put(str(handle), new_person)
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
            txn.put(str(handle), new_family)
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
            txn.put(str(handle), new_note)
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
            txn.put(str(handle), new_media)
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
            txn.put(str(handle), new_event)
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
        new_place[6] = map(convert_location, new_place[6])
        new_place = new_place[:12] + new_place[13:]
        new_place = tuple(new_place)
        with BSDDBTxn(self.env, self.place_map) as txn:
            txn.put(str(handle), new_place)
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
            txn.put(str(handle), new_source)
        self.update()

    # ---------------------------------
    # Modify Repository
    # ---------------------------------
    # Remove the old marker field, set new locality.
    for handle in self.repository_map.keys():
        repository = self.repository_map[handle]
        new_repository = list(repository)
        new_repository = new_repository[:8] + new_repository[9:]
        new_repository[5] = map(convert_address, new_repository[5])
        new_repository = tuple(new_repository)
        with BSDDBTxn(self.env, self.repository_map) as txn:
            txn.put(str(handle), new_repository)
        self.update()

    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put('version', 15)

def convert_marker(self, marker_field):
    """Convert a marker into a tag."""
    marker = MarkerType()
    marker.unserialize(marker_field)
    tag_name = unicode(marker)
    
    if tag_name != '':
        if tag_name not in self.tags:
            tag = Tag()
            handle = self.create_id()
            tag.set_handle(handle)
            tag.set_change_time(time.time())
            tag.set_name(tag_name)
            tag.set_priority(len(self.tags))
            with BSDDBTxn(self.env, self.tag_map) as txn:
                txn.put(handle, tag.serialize())
            self.tags[tag_name] = handle
        return self.tags[tag_name]
    else:
        return None

def convert_locbase(loc):
    """Convert location base to include an empty locality field."""
    return tuple([loc[0], u''] + list(loc[1:]))
    
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
    
    connector = u""
    origintype = (NameOriginType.NONE, u"")
    patorigintype = (NameOriginType.PATRONYMIC, u"")
    
    if patronymic.strip() == u"":
        #no patronymic, create a single surname
        surname_list = [(surname, prefix, True, origintype, connector)]
    else:
        #a patronymic, if no surname or equal as patronymic, a single surname
        if (surname.strip() == u"") or (surname == patronymic and prefix == u""):
            surname_list = [(patronymic, prefix, True, patorigintype, connector)]
        else:
            #two surnames, first patronymic, then surname which is primary
            surname_list = [(patronymic, u"", False, patorigintype, u""),
                            (surname, prefix, True, origintype, connector)]
    
    #return new value, add two empty strings for nick and family nick
    return (privacy, source_list, note_list, date,
         first_name, surname_list, suffix, title, name_type,
         group_as, sort_as, display_as, call, u"", u"")

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
            txn.put(str(handle), new_note)
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
            txn.put(str(handle), new_event)
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
            txn.put(str(handle), new_person)
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
            txn.put(str(handle), new_family)
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
            txn.put(str(handle), new_repository)
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
            txn.put(str(handle), new_media)
        self.update()

    # ---------------------------------
    # Modify Place
    # ---------------------------------
    for place_handle in self.place_map.keys():
        place = self.place_map[place_handle]
        (handle, gramps_id, title, long, lat,
         main_loc, alt_loc, urls, media_list, source_list, note_list,
         change, marker, private) = place
        new_media_list = new_media_list_14(media_list)
        new_source_list = new_source_list_14(source_list)
        new_place = (handle, gramps_id, title, long, lat,
                     main_loc, alt_loc, urls, new_media_list, 
                     new_source_list, note_list, change, marker, private) 

        with BSDDBTxn(self.env, self.place_map) as txn:
            txn.put(str(handle), new_place)
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
            txn.put(str(handle), new_source)
        self.update()

    # Bump up database version. Separate transaction to save metadata.
    with BSDDBTxn(self.env, self.metadata) as txn:
        txn.put('version', 14)

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

