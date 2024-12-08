#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Doug Blank <doug.blank@gmail.com>
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


def convert_21(classname, array):
    if classname == "Person":
        return convert_person(array)
    elif classname == "Family":
        return convert_family(array)
    elif classname == "Event":
        return convert_event(array)
    elif classname == "Place":
        return convert_place(array)
    elif classname == "Repository":
        return convert_repository(array)
    elif classname == "Source":
        return convert_source(array)
    elif classname == "Citation":
        return convert_citation(array)
    elif classname == "Media":
        return convert_media(array)
    elif classname == "Note":
        return convert_note(array)
    elif classname == "Tag":
        return convert_tag(array)
    else:
        raise Exception("unknown class: %s" % classname)


def convert_researcher(researcher):
    # This can be a problem if the Researcher class
    # changes!
    return {
        "_class": "Researcher",
        "street": researcher.street,
        "city": researcher.city,
        "county": researcher.county,
        "state": researcher.state,
        "country": researcher.country,
        "postal": researcher.postal,
        "phone": researcher.phone,
        "locality": researcher.locality,
        "name": researcher.name,
        "addr": researcher.addr,
        "email": researcher.email,
    }


def convert_person(array):
    return {
        "_class": "Person",
        "handle": array[0],
        "gramps_id": array[1],
        "gender": array[2],
        "primary_name": convert_name(array[3]),
        "alternate_names": [convert_name(name) for name in array[4]],
        "death_ref_index": array[5],
        "birth_ref_index": array[6],
        "event_ref_list": [convert_event_ref(ref) for ref in array[7]],
        "family_list": array[8],
        "parent_family_list": array[9],
        "media_list": [convert_media_ref(ref) for ref in array[10]],
        "address_list": [convert_address(address) for address in array[11]],
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[12]],
        "urls": [convert_url(url) for url in array[13]],
        "lds_ord_list": [convert_ord(ord) for ord in array[14]],
        "citation_list": array[15],  # handles
        "note_list": array[16],  # handles
        "change": array[17],
        "tag_list": array[18],  # handles
        "private": array[19],
        "person_ref_list": [convert_person_ref(ref) for ref in array[20]],
    }


def convert_person_ref(array):
    return {
        "_class": "PersonRef",
        "private": array[0],
        "citation_list": array[1],  # handles
        "note_list": array[2],  # handles
        "ref": array[3],
        "rel": array[4],
    }


def convert_ord(array):
    return {
        "_class": "LdsOrd",
        "citation_list": array[0],  # handles
        "note_list": array[1],  # handles
        "date": convert_date(array[2]),
        "type": array[3],  # string
        "place": array[4],
        "famc": array[5],
        "temple": array[6],
        "status": array[7],
        "private": array[8],
    }


def convert_url(array):
    return {
        "_class": "Url",
        "private": array[0],
        "path": array[1],
        "desc": array[2],
        "type": convert_type("UrlType", array[3]),
    }


def convert_address(array):
    return {
        "_class": "Address",
        "private": array[0],
        "citation_list": array[1],  # handles
        "note_list": array[2],  # handles
        "date": convert_date(array[3]),
        "street": array[4][0],
        "locality": array[4][1],
        "city": array[4][2],
        "county": array[4][3],
        "state": array[4][4],
        "country": array[4][5],
        "postal": array[4][6],
        "phone": array[4][7],
    }


def convert_media_ref(array):
    return {
        "_class": "MediaRef",
        "private": array[0],
        "citation_list": array[1],  # handles
        "note_list": array[2],  # handles
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[3]],
        "ref": array[4],
        "rect": list(array[5]) if array[5] is not None else None,
    }


def convert_event_ref(array):
    return {
        "_class": "EventRef",
        "private": array[0],
        "citation_list": array[1],  # handles
        "note_list": array[2],  # handles
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[3]],
        "ref": array[4],
        "role": convert_type("EventRoleType", array[5]),
    }


def convert_attribute(classname, array):
    if classname == "SrcAttribute":
        return {
            "_class": classname,
            "private": array[0],
            "type": convert_type("SrcAttributeType", array[1]),
            "value": array[2],
        }
    else:
        return {
            "_class": classname,
            "private": array[0],
            "citation_list": array[1],  # handles
            "note_list": array[2],  # handles
            "type": convert_type("AttributeType", array[3]),
            "value": array[4],
        }


def convert_name(array):
    return {
        "_class": "Name",
        "private": array[0],
        "citation_list": array[1],
        "note_list": array[2],  # handles
        "date": convert_date(array[3]),
        "first_name": array[4],
        "surname_list": [convert_surname(name) for name in array[5]],
        "suffix": array[6],
        "title": array[7],
        "type": convert_type("NameType", array[8]),
        "group_as": array[9],
        "sort_as": array[10],
        "display_as": array[11],
        "call": array[12],
        "nick": array[13],
        "famnick": array[14],
    }


def convert_surname(array):
    return {
        "_class": "Surname",
        "surname": array[0],
        "prefix": array[1],
        "primary": array[2],
        "origintype": convert_type("NameOriginType", array[3]),
        "connector": array[4],
    }


def convert_date(array):
    if array is None:
        return {
            "_class": "Date",
            "calendar": 0,
            "modifier": 0,
            "quality": 0,
            "dateval": [0, 0, 0, False],
            "text": "",
            "sortval": 0,
            "newyear": 0,
            "format": None,
        }
    else:
        return {
            "_class": "Date",
            "calendar": array[0],
            "modifier": array[1],
            "quality": array[2],
            "dateval": list(array[3]),
            "text": array[4],
            "sortval": array[5],
            "newyear": array[6],
            "format": None,
        }


def convert_stt(array):
    return {
        "_class": "StyledTextTag",
        "name": convert_type("StyledTextTagType", array[0]),
        "value": array[1],
        "ranges": [list(r) for r in array[2]],
    }


def convert_type(classname, array):
    return {
        "_class": classname,
        "value": array[0],
        "string": array[1],
    }


def convert_family(array):
    return {
        "_class": "Family",
        "handle": array[0],
        "gramps_id": array[1],
        "father_handle": array[2],
        "mother_handle": array[3],
        "child_ref_list": [convert_child_ref(ref) for ref in array[4]],
        "type": convert_type("FamilyRelType", array[5]),
        "event_ref_list": [convert_event_ref(ref) for ref in array[6]],
        "media_list": [convert_media_ref(ref) for ref in array[7]],
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[8]],
        "lds_ord_list": [convert_ord(ord) for ord in array[9]],
        "citation_list": array[10],  # handles
        "note_list": array[11],  # handles
        "change": array[12],
        "tag_list": array[13],
        "private": array[14],
        "complete": 0,
    }


def convert_child_ref(array):
    return {
        "_class": "ChildRef",
        "private": array[0],
        "citation_list": array[1],
        "note_list": array[2],
        "ref": array[3],
        "frel": convert_type("ChildRefType", array[4]),
        "mrel": convert_type("ChildRefType", array[5]),
    }


def convert_event(array):
    return {
        "_class": "Event",
        "handle": array[0],
        "gramps_id": array[1],
        "type": convert_type("EventType", array[2]),
        "date": convert_date(array[3]),
        "description": array[4],
        "place": array[5],
        "citation_list": array[6],
        "note_list": array[7],
        "media_list": [convert_media_ref(ref) for ref in array[8]],
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[9]],
        "change": array[10],
        "tag_list": array[11],
        "private": array[12],
    }


def convert_place(array):
    return {
        "_class": "Place",
        "handle": array[0],
        "gramps_id": array[1],
        "title": array[2],
        "long": array[3],
        "lat": array[4],
        "placeref_list": [convert_place_ref(ref) for ref in array[5]],
        "name": convert_place_name(array[6]),
        "alt_names": [convert_place_name(name) for name in array[7]],
        "place_type": convert_type("PlaceType", array[8]),
        "code": array[9],
        "alt_loc": [convert_location(loc) for loc in array[10]],
        "urls": [convert_url(url) for url in array[11]],
        "media_list": [convert_media_ref(ref) for ref in array[12]],
        "citation_list": array[13],
        "note_list": array[14],
        "change": array[15],
        "tag_list": array[16],
        "private": array[17],
    }


def convert_location(array):
    return {
        "_class": "Location",
        "street": array[0][0],
        "locality": array[0][1],
        "city": array[0][2],
        "county": array[0][3],
        "state": array[0][4],
        "country": array[0][5],
        "postal": array[0][6],
        "phone": array[0][7],
        "parish": array[1],
    }


def convert_place_ref(array):
    return {
        "_class": "PlaceRef",
        "ref": array[0],
        "date": convert_date(array[1]),
    }


def convert_place_name(array):
    return {
        "_class": "PlaceName",
        "value": array[0],
        "date": convert_date(array[1]),
        "lang": array[2],
    }


def convert_repository(array):
    return {
        "_class": "Repository",
        "handle": array[0],
        "gramps_id": array[1],
        "type": convert_type("RepositoryType", array[2]),
        "name": array[3],
        "note_list": array[4],
        "address_list": [convert_address(addr) for addr in array[5]],
        "urls": [convert_url(url) for url in array[6]],
        "change": array[7],
        "tag_list": array[8],
        "private": array[9],
    }


def convert_source(array):
    return {
        "_class": "Source",
        "handle": array[0],
        "gramps_id": array[1],
        "title": array[2],
        "author": array[3],
        "pubinfo": array[4],
        "note_list": array[5],
        "media_list": [convert_media_ref(ref) for ref in array[6]],
        "abbrev": array[7],
        "change": array[8],
        "attribute_list": [
            convert_attribute("SrcAttribute", attr) for attr in array[9]
        ],
        "reporef_list": [convert_repo_ref(ref) for ref in array[10]],
        "tag_list": array[11],
        "private": array[12],
    }


def convert_repo_ref(array):
    return {
        "_class": "RepoRef",
        "note_list": array[0],
        "ref": array[1],
        "call_number": array[2],
        "media_type": convert_type("SourceMediaType", array[3]),
        "private": array[4],
    }


def convert_citation(array):
    return {
        "_class": "Citation",
        "handle": array[0],
        "gramps_id": array[1],
        "date": convert_date(array[2]),
        "page": array[3],
        "confidence": array[4],
        "source_handle": array[5],
        "note_list": array[6],
        "media_list": [convert_media_ref(ref) for ref in array[7]],
        "attribute_list": [
            convert_attribute("SrcAttribute", attr) for attr in array[8]
        ],
        "change": array[9],
        "tag_list": array[10],
        "private": array[11],
    }


def convert_media(array):
    return {
        "_class": "Media",
        "handle": array[0],
        "gramps_id": array[1],
        "path": array[2],
        "mime": array[3],
        "desc": array[4],
        "checksum": array[5],
        "attribute_list": [convert_attribute("Attribute", attr) for attr in array[6]],
        "citation_list": array[7],
        "note_list": array[8],
        "change": array[9],
        "date": convert_date(array[10]),
        "tag_list": array[11],
        "private": array[12],
        "thumb": None,
    }


def convert_note(array):
    return {
        "_class": "Note",
        "handle": array[0],
        "gramps_id": array[1],
        "text": convert_styledtext(array[2]),
        "format": array[3],
        "type": convert_type("NoteType", array[4]),
        "change": array[5],
        "tag_list": array[6],
        "private": array[7],
    }


def convert_styledtext(array):
    return {
        "_class": "StyledText",
        "string": array[0],
        "tags": [convert_stt(stt) for stt in array[1]],
    }


def convert_tag(array):
    return {
        "_class": "Tag",
        "handle": array[0],
        "name": array[1],
        "color": array[2],
        "priority": array[3],
        "change": array[4],
    }
