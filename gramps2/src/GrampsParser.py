#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

import const
import RelLib
import Date

import string
import Calendar
import Utils
import xml.parsers.expat
    
#-------------------------------------------------------------------------
#
# Remove extraneous spaces
#
#-------------------------------------------------------------------------

def rs(text):
    return string.join(string.split(text))

def fix_spaces(text_list):
    return string.join(map(rs,text_list),'\n')

#-------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
#-------------------------------------------------------------------------
class GrampsParser:

    def __init__(self,database,callback,base):
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []
        self.tlist = []
        self.conf = 2
        
        self.ord = None
        self.objref = None
        self.object = None
        self.pref = None
        self.use_p = 0
        self.in_note = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.in_witness = 0
        self.db = database
        self.base = base
        self.photo = None
        self.person = None
        self.family = None
        self.address = None
        self.source = None
        self.source_ref = None
        self.attribute = None
        self.placeobj = None
        self.locations = 0
        self.place_map = {}

        self.resname = ""
        self.resaddr = "" 
        self.rescity = ""
        self.resstate = ""
        self.rescon = "" 
        self.respos = ""
        self.resphone = ""
        self.resemail = ""

        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.lmap = {}
        self.media_file_map = {}
        
        self.callback = callback
        self.entries = 0
        self.count = 0
        self.increment = 100
        self.event = None
        self.name = None
        self.tempDefault = None
        self.owner = RelLib.Researcher()
        self.func_list = [None]*50
        self.func_index = 0
        self.func = None
        self.witness_comment = ""

        self.func_map = {
            "address"    : (self.start_address, self.stop_address),
            "addresses"  : (None,None),
            "childlist"  : (None,None),
            "aka"        : (self.start_name, self.stop_aka),
            "attribute"  : (self.start_attribute, self.stop_attribute),
            "attr_type"  : (None,self.stop_attr_type),
            "attr_value" : (None,self.stop_attr_value),
            "bookmark"   : (self.start_bmark, None),
            "witness"    : (self.start_witness,self.stop_witness),
            "bookmarks"  : (None, None),
            "child"      : (self.start_child,None),
            "childof"    : (self.start_childof,None),
            "city"       : (None, self.stop_city),
            "country"    : (None, self.stop_country),
            "comment"    : (None, self.stop_comment),
            "created"    : (self.start_created, None),
            "ref"        : (None, self.stop_ref),
            "database"   : (None, None),
            "phone"      : (None, self.stop_phone),
            "date"       : (None, self.stop_date),
            "cause"      : (None, self.stop_cause),
            "description": (None, self.stop_description),
            "event"      : (self.start_event, self.stop_event),
            "families"   : (None, self.stop_families),
            "family"     : (self.start_family, self.stop_family),
            "father"     : (self.start_father, None),
            "first"      : (None, self.stop_first),
            "gender"     : (None, self.stop_gender),
            "header"     : (None, None),
            "last"       : (self.start_last, self.stop_last),
            "mother"     : (self.start_mother,None),
            "name"       : (self.start_name, self.stop_name),
            "nick"       : (None, self.stop_nick),
            "note"       : (self.start_note, self.stop_note),
            "p"          : (None, self.stop_ptag),
            "parentin"   : (self.start_parentin,None),
            "people"     : (self.start_people, self.stop_people),
            "person"     : (self.start_person, self.stop_person),
            "img"        : (self.start_photo, self.stop_photo),
            "objref"     : (self.start_objref, self.stop_objref),
            "object"     : (self.start_object, self.stop_object),
            "place"      : (self.start_place, self.stop_place),
            "dateval"    : (self.start_dateval, None),
            "daterange"  : (self.start_daterange, None),
            "datestr"    : (self.start_datestr, None),
            "places"     : (None, self.stop_places),
            "placeobj"   : (self.start_placeobj,self.stop_placeobj),
            "location"   : (self.start_location,None),
            "lds_ord"    : (self.start_lds_ord, self.stop_lds_ord),
            "temple"     : (self.start_temple, None),
            "status"     : (self.start_status, None),
            "sealed_to"  : (self.start_sealed_to, None),
            "coord"      : (self.start_coord,None),
            "pos"        : (self.start_pos, None),
            "postal"     : (None, self.stop_postal),
            "researcher" : (None, self.stop_research),
            "resname"    : (None, self.stop_resname ),
            "resaddr"    : (None, self.stop_resaddr ),
            "rescity"    : (None, self.stop_rescity ),
            "resstate"   : (None, self.stop_resstate ),
            "rescountry" : (None, self.stop_rescountry),
            "respostal"  : (None, self.stop_respostal),
            "resphone"   : (None, self.stop_resphone),
            "resemail"   : (None, self.stop_resemail),
            "sauthor"    : (None, self.stop_sauthor),
            "sabbrev"    : (None, self.stop_sabbrev),
            "scomments"  : (None, self.stop_scomments),
            "sdate"      : (None,self.stop_sdate),
            "source"     : (self.start_source, self.stop_source),
            "sourceref"  : (self.start_sourceref, self.stop_sourceref),
            "sources"    : (None, None),
            "spage"      : (None, self.stop_spage),
            "spubinfo"   : (None, self.stop_spubinfo),
            "state"      : (None, self.stop_state),
            "stext"      : (None, self.stop_stext),
            "stitle"     : (None, self.stop_stitle),
            "street"     : (None, self.stop_street),
            "suffix"     : (None, self.stop_suffix),
            "title"      : (None, self.stop_title),
            "url"        : (self.start_url, None)
            }


    def parse(self,file):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.ParseFile(file)
            
        self.db.set_researcher(self.owner)
        if self.tempDefault != None:
            id = self.tempDefault
            if self.db.has_person_id(id) and self.db.get_default_person() == None:
                self.db.set_default_person_id(id)

        for key in self.func_map.keys():
            del self.func_map[key]
        del self.func_map
        del self.func_list
        del p

    def start_lds_ord(self,attrs):
        type = attrs['type']
        self.ord = RelLib.LdsOrd()
        if self.person:
            if type == "baptism":
                self.person.set_lds_baptism(self.ord)
            elif type == "endowment":
                self.person.set_lds_endowment(self.ord)
            elif type == "sealed_to_parents":
                self.person.set_lds_sealing(self.ord)
        elif self.family:
            if type == "sealed_to_spouse":
                self.family.set_lds_sealing(self.ord)

    def start_temple(self,attrs):
        self.ord.set_temple(attrs['val'])

    def start_status(self,attrs):
        self.ord.set_status(int(attrs['val']))

    def start_sealed_to(self,attrs):
        id = attrs['ref']
        self.ord.set_family_id(self.db.find_family_no_map(id))
        
    def start_place(self,attrs):
        if attrs.has_key('ref'):
            self.placeobj = self.db.find_place_from_id(attrs['ref'])
        else:
            self.placeobj = None

    def start_placeobj(self,attrs):
        self.placeobj = self.db.find_place_from_id(attrs['id'])
        title = attrs['title']
        if title == "":
            title = attrs['id']
        self.placeobj.set_title(title)
        self.locations = 0
        if self.num_places > 0:
            if self.callback != None and self.count % self.increment == 0:
                self.callback(float(self.count)/float(self.entries))
            self.count = self.count + 1
            
    def start_location(self,attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""
        
        loc = RelLib.Location()
        if attrs.has_key('phone'):
            loc.phone = attrs['phone']
        if attrs.has_key('postal'):
            loc.postal = attrs['postal']
        if attrs.has_key('city'):
            loc.city = attrs['city']
        if attrs.has_key('parish'):
            loc.parish = attrs['parish']
        if attrs.has_key('state'):
            loc.state = attrs['state']
        if attrs.has_key('county'):
            loc.county =attrs['county']
        if attrs.has_key('country'):
            loc.country = attrs['country']
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
            self.locations = self.locations + 1

    def start_witness(self,attrs):
        self.in_witness = 1
        if attrs.has_key('ref'):
            self.witness = RelLib.Witness(RelLib.Event.ID,attrs['ref'])
        if attrs.has_key('name'):
            self.witness = RelLib.Witness(RelLib.Event.NAME,attrs['name'])
        
    def start_coord(self,attrs):
        if attrs.has_key('lat'):
            self.placeobj.set_latitude(attrs['lat'])
        if attrs.has_key('long'):
            self.placeobj.set_longitude(attrs['long'])

    def start_event(self,attrs):
        self.event = RelLib.Event()
        self.db.add_event(self.event)
        self.event_type = const.save_event(attrs["type"])
        if attrs.has_key("conf"):
            self.event.conf = int(attrs["conf"])
        else:
            self.event.conf = 2
        if attrs.has_key("priv"):
            self.event.private = int(attrs["priv"])
        
    def start_attribute(self,attrs):
        self.attribute = RelLib.Attribute()
        if attrs.has_key("conf"):
            self.attribute.conf = int(attrs["conf"])
        else:
            self.attribute.conf = 2
        if attrs.has_key("priv"):
            self.attribute.private = int(attrs["priv"])
        if attrs.has_key('type'):
            self.attribute.set_type(const.save_attr(attrs["type"]))
        if attrs.has_key('value'):
            self.attribute.set_value(attrs["value"])
        if self.photo:
            self.photo.add_attribute(self.attribute)
        elif self.object:
            self.object.add_attribute(self.attribute)
        elif self.objref:
            self.objref.add_attribute(self.attribute)
        elif self.person:
            self.person.add_attribute(self.attribute)
        elif self.family:
            self.family.add_attribute(self.attribute)

    def start_address(self,attrs):
        self.address = RelLib.Address()
        self.person.add_address(self.address)
        if attrs.has_key("conf"):
            self.address.conf = int(attrs["conf"])
        else:
            self.address.conf = 2
        if attrs.has_key("priv"):
            self.address.private = int(attrs["priv"])

    def start_bmark(self,attrs):
        self.db.bookmarks.append(attrs["ref"])

    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.find_person_from_id(attrs["id"])
        if attrs.has_key("complete"):
            self.person.set_complete(int(attrs['complete']))
        else:
            self.person.set_complete(0)

    def start_people(self,attrs):
        if attrs.has_key("default"):
            self.tempDefault = attrs["default"]

    def start_father(self,attrs):
        self.family.set_father_id(attrs["ref"])

    def start_mother(self,attrs):
        self.family.set_mother_id(attrs["ref"])
    
    def start_child(self,attrs):
        self.family.add_child_id(attrs["ref"])

    def start_url(self,attrs):

        if not attrs.has_key("href"):
            return
        try:
            desc = attrs["description"]
        except KeyError:
            desc = ""

        try:
            url = RelLib.Url()
            url.set_path(attrs["href"])
            url.set_description(desc)
            if attrs.has_key("priv"):
                url.set_privacy(int(attrs['priv']))
            if self.person:
                self.person.add_url(url)
            elif self.placeobj:
                self.placeobj.add_url(url)
        except KeyError:
            return

    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.find_family_no_map(attrs["id"])
        if attrs.has_key("type"):
            self.family.set_relationship(const.save_frel(attrs["type"]))
        else:
            self.family.set_relationship("")
        if attrs.has_key("complete"):
            self.family.set_complete(int(attrs['complete']))
        else:
            self.family.set_complete(0)

    def start_childof(self,attrs):
        family = self.db.find_family_no_map(attrs["ref"])
        if attrs.has_key("mrel"):
            mrel = attrs["mrel"]
        else:
            mrel = "Birth"
        if attrs.has_key("frel"):
            frel = attrs["frel"]
        else:
            frel = "Birth"
        self.person.add_parent_family_id(family.get_id(),mrel,frel)

    def start_parentin(self,attrs):
        self.person.add_family_id(attrs["ref"])

    def start_name(self,attrs):
        if not self.in_witness:
            self.name = RelLib.Name()
            if attrs.has_key("type"):
                self.name.set_type(attrs["type"])
            if attrs.has_key("conf"):
                self.name.set_confidence(int(attrs["conf"]))
            else:
                self.name.conf = 2
            if attrs.has_key("priv"):
                self.name.set_privacy(int(attrs["priv"]))

    def start_last(self,attrs):
        if attrs.has_key('prefix'):
            self.name.set_surname_prefix(attrs['prefix'])
        
    def start_note(self,attrs):
        self.in_note = 1
        self.note = RelLib.Note()
        if attrs.has_key("format"):
            self.note.set_format(int(attrs['format']))

    def start_sourceref(self,attrs):
        self.source_ref = RelLib.SourceRef()
        source = self.db.find_source_from_id(attrs["ref"])
        if attrs.has_key("conf"):
            self.source_ref.confidence = int(attrs["conf"])
        else:
            self.source_ref.confidence = self.conf
        self.source_ref.set_base_id(source.get_id())
        if self.photo:
            self.photo.add_source_reference(self.source_ref)
        elif self.ord:
            self.ord.add_source_reference(self.source_ref)
        elif self.object:
            self.object.add_source_reference(self.source_ref)
        elif self.event:
            self.event.add_source_reference(self.source_ref)
        elif self.address:
            self.address.add_source_reference(self.source_ref)
        elif self.name:
            self.name.add_source_reference(self.source_ref)
        elif self.attribute:
            self.attribute.add_source_reference(self.source_ref)
        elif self.placeobj:
            self.placeobj.add_source_reference(self.source_ref)
        elif self.family:
            self.family.add_source_reference(self.source_ref)
        elif self.person:
            self.person.add_source_reference(self.source_ref)

    def start_source(self,attrs):
        if self.num_srcs > 0:
            if self.callback != None and self.count % self.increment == 0:
                self.callback(float(self.count)/float(self.entries))
            self.count = self.count + 1
        self.source = self.db.find_source_from_id(attrs["id"])

    def start_objref(self,attrs):
        self.objref = RelLib.MediaRef()
        self.objref.set_reference_id(attrs['ref'])
        if attrs.has_key('priv'):
            self.objref.set_privacy(int(attrs['priv']))
        if self.family:
            self.family.add_media_reference(self.objref)
        elif self.source:
            self.source.add_media_reference(self.objref)
        elif self.person:
            self.person.add_media_reference(self.objref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.objref)

    def start_object(self,attrs):
        self.object = self.db.find_object_from_id(attrs['id'])
        self.object.set_mime_type(attrs['mime'])
        self.object.set_description(attrs['description'])
        src = attrs["src"]
        if src:
            if src[0] != '/':
                self.object.set_path("%s/%s" % (self.base,src))
            else:
                self.object.set_path(src)

    def stop_people(self,tag):
        pass

    def stop_object(self,tag):
        self.db.commit_media_object(self.object)
        self.object = None

    def stop_objref(self,tag):
        self.objref = None
        
    def start_photo(self,attrs):
        self.photo = RelLib.MediaObject()
        self.pref = RelLib.MediaRef()
        self.pref.set_reference_id(self.photo.get_id())
        
        for key in attrs.keys():
            if key == "descrip" or key == "description":
                self.photo.set_description(attrs[key])
            elif key == "priv":
                self.pref.set_privacy(int(attrs[key]))
            elif key == "src":
                src = attrs["src"]
                if src[0] != '/':
                    self.photo.set_path("%s/%s" % (self.base,src))
                else:
                    self.photo.set_path(src)
            else:
                a = RelLib.Attribute()
                a.set_type(key)
                a.set_value(attrs[key])
                self.photo.add_attribute(a)
        self.photo.set_mime_type(Utils.get_mime_type(self.photo.get_path()))
        self.db.add_object(self.photo)
        if self.family:
            self.family.add_media_reference(self.pref)
        elif self.source:
            self.source.add_media_reference(self.pref)
        elif self.person:
            self.person.add_media_reference(self.pref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.pref)

    def start_daterange(self,attrs):
        if self.source_ref:
            d = self.source_ref.get_date()
        elif self.ord:
            d = self.ord.get_date_object()
        elif self.address:
            d = self.address.get_date_object()
        else:
            d = self.event.get_date_object()

        if attrs.has_key("calendar"):
            d.set_calendar_val(int(attrs['calendar']))

        if attrs.has_key("cformat"):
            d.set_calendar(Calendar.find_calendar(attrs['calendar']))

        d.get_start_date().set_iso_date(attrs['start'])
        d.get_stop_date().set_iso_date(attrs['stop'])
        d.range = 1
        
    def start_dateval(self,attrs):
        if self.source_ref:
            d = self.source_ref.get_date()
        elif self.ord:
            d = self.ord.get_date_object()
        elif self.address:
            d = self.address.get_date_object()
        else:
            d = self.event.get_date_object()

        if attrs.has_key("calendar"):
            d.set_calendar_val(int(attrs['calendar']))

        if attrs.has_key("cformat"):
            d.set_calendar(Calendar.find_calendar(attrs['cformat']))

        d.get_start_date().set_iso_date(attrs['val'])
        
        if attrs.has_key("type"):
            d.get_start_date().set_mode(attrs['type'])
        else:
            d.get_start_date().set_mode(None)

    def start_datestr(self,attrs):
        if self.source_ref:
            d = self.source_ref.get_date()
        elif self.ord:
            d = self.ord.get_date_object()
        elif self.address:
            d = self.address.get_date_object()
        else:
            d = self.event.get_date_object()

        d.set(attrs['val'])

    def start_created(self,attrs):
        if attrs.has_key('sources'):
            self.num_srcs = int(attrs['sources'])
        else:
            self.num_srcs = 0
        if attrs.has_key('places'):
            self.num_places = int(attrs['places'])
        else:
            self.num_places = 0
        self.entries = int(attrs["people"]) + int(attrs["families"]) + \
                       self.num_places + self.num_srcs

    def start_pos(self,attrs):
        self.person.position = (int(attrs["x"]), int(attrs["y"]))

    def stop_attribute(self,tag):
        self.attribute = None

    def stop_comment(self,tag):
        if tag.strip():
            self.witness_comment = tag
        else:
            self.witness_comment = ""

    def stop_witness(self,tag):
        if self.witness_comment:
            self.witness.set_comment(self.witness_comment)
        elif tag.strip():
            self.witness.set_comment(tag)
        else:
            self.witness.set_comment("")
        self.event.add_witness(self.witness)
        self.in_witness = 0

    def stop_attr_type(self,tag):
        self.attribute.set_type(tag)

    def stop_attr_value(self,tag):
        self.attribute.set_value(tag)

    def stop_address(self,tag):
        self.address = None
        
    def stop_places(self,tag):
        self.placeobj = None

    def stop_photo(self,tag):
        self.photo = None

    def stop_placeobj(self,tag):
        if self.placeobj.get_title() == "":
            loc = self.placeobj.get_main_location()
            self.placeobj.set_title(build_place_title(loc))
        self.db.commit_place(self.placeobj)
        self.placeobj = None

    def stop_family(self,tag):
        self.db.commit_family(self.family)
        self.family = None
        
    def stop_event(self,tag):
        self.event.name = self.event_type

        if self.family:
            self.family.add_event_id(self.event.get_id())
        else:
            if self.event_type == "Birth":
                self.person.set_birth_id(self.event.get_id())
            elif self.event_type == "Death":
                self.person.set_death_id(self.event.get_id())
            else:
                self.person.add_event_id(self.event.get_id())
        self.db.commit_event(self.event)
        self.event = None

    def stop_name(self,tag):
        if self.in_witness:
            self.witness = RelLib.Witness(RelLib.Event.NAME,tag)
        else:
            if self.name.get_type() == "":
                self.name.set_type("Birth Name")
            self.person.set_primary_name (self.name)
            self.person.get_primary_name().build_sort_name()
            self.name = None

    def stop_ref(self,tag):
        self.witness = RelLib.Witness(RelLib.Event.ID,tag)

    def stop_place(self,tag):
        if self.placeobj == None:
            if self.place_map.has_key(tag):
                self.placeobj = self.place_map[tag]
            else:
                self.placeobj = RelLib.Place()
                self.placeobj.set_title(tag)
        if self.ord:
            self.ord.set_place_id(self.placeobj.get_id())
        else:
            self.event.set_place_id(self.placeobj.get_id())
        self.db.commit_place(self.placeobj)
        self.placeobj = None
        
    def stop_date(self,tag):
        if tag:
            if self.address:
                self.address.set_date(tag)
            else:
                self.event.set_date(tag)

    def stop_first(self,tag):
        self.name.set_first_name(tag)

    def stop_families(self,tag):
        self.family = None

    def stop_person(self,tag):
        self.db.commit_person(self.person)
        self.person = None

    def stop_description(self,tag):
        self.event.set_description(tag)

    def stop_cause(self,tag):
        self.event.set_cause(tag)

    def stop_gender(self,tag):
        t = tag
        if t == "M":
            self.person.set_gender (RelLib.Person.male)
        elif t == "F":
            self.person.set_gender (RelLib.Person.female)
        else:
            self.person.set_gender (RelLib.Person.unknown)

    def stop_stitle(self,tag):
        self.source.set_title(tag)

    def stop_sourceref(self,tag):
        self.source_ref = None

    def stop_source(self,tag):
        self.db.commit_source(self.source)
        self.source = None

    def stop_sauthor(self,tag):
        self.source.set_author(tag)

    def stop_sdate(self,tag):
        date = Date.Date()
        date.set(tag)
        self.source_ref.set_date(date)
        
    def stop_phone(self,tag):
        self.address.set_phone(tag)

    def stop_street(self,tag):
        self.address.set_street(tag)

    def stop_city(self,tag):
        self.address.set_city(tag)

    def stop_state(self,tag):
        self.address.set_state(tag)
        
    def stop_country(self,tag):
        self.address.setCountry(tag)

    def stop_postal(self,tag):
        self.address.set_postal_code(tag)

    def stop_spage(self,tag):
        self.source_ref.set_page(tag)

    def stop_lds_ord(self,tag):
        self.ord = None

    def stop_spubinfo(self,tag):
        self.source.set_publication_info(tag)

    def stop_sabbrev(self,tag):
        self.source.set_abbreviation(tag)
        
    def stop_stext(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.stext_list)
        else:
            note = tag
        self.source_ref.set_text(note)

    def stop_scomments(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.scomments_list)
        else:
            note = tag
        self.source_ref.set_comments(note)

    def stop_last(self,tag):
        if self.name:
            self.name.set_surname(tag)

    def stop_suffix(self,tag):
        if self.name:
            self.name.set_suffix(tag)

    def stop_title(self,tag):
        if self.name:
            self.name.set_title(tag)

    def stop_nick(self,tag):
        if self.person:
            self.person.set_nick_name(tag)

    def stop_note(self,tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.note_list)
        else:
            text = tag
        self.note.set(text)

        if self.address:
            self.address.set_note_object(self.note)
        elif self.ord:
            self.ord.set_note_object(self.note)
        elif self.attribute:
            self.attribute.set_note_object(self.note)
        elif self.object:
            self.object.set_note_object(self.note)
        elif self.objref:
            self.objref.set_note_object(self.note)
        elif self.photo:
            self.photo.set_note_object(self.note)
        elif self.name:
            self.name.set_note_object(self.note)
        elif self.source:
            self.source.set_note_object(self.note)
        elif self.event:
            self.event.set_note_object(self.note)
        elif self.person:
            self.person.set_note_object(self.note)
        elif self.family:
            self.family.set_note_object(self.note)
        elif self.placeobj:
            self.placeobj.set_note_object(self.note)

    def stop_research(self,tag):
        self.owner.set(self.resname, self.resaddr, self.rescity, self.resstate,
                       self.rescon, self.respos, self.resphone, self.resemail)

    def stop_resname(self,tag):
        self.resname = tag

    def stop_resaddr(self,tag):
        self.resaddr = tag

    def stop_rescity(self,tag):
        self.rescity = tag

    def stop_resstate(self,tag):
        self.resstate = tag

    def stop_rescountry(self,tag):
        self.rescon = tag

    def stop_respostal(self,tag):
        self.respos = tag

    def stop_resphone(self,tag):
        self.resphone = tag

    def stop_resemail(self,tag):
        self.resemail = tag

    def stop_ptag(self,tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(tag)
        elif self.in_stext:
            self.stext_list.append(tag)
        elif self.in_scomments:
            self.scomments_list.append(tag)

    def stop_aka(self,tag):
        self.person.add_alternate_name(self.name)
        if self.name.get_type() == "":
            self.name.set_type("Also Known As")
        self.name = None

    def startElement(self,tag,attrs):

        self.func_list[self.func_index] = (self.func,self.tlist)
        self.func_index = self.func_index + 1
        self.tlist = []

        try:
	    f,self.func = self.func_map[tag]
            if f:
                f(attrs)
        except KeyError:
            self.func_map[tag] = (None,None)
            self.func = None

    def endElement(self,tag):

        if self.func:
            self.func(string.join(self.tlist,''))
        self.func_index = self.func_index - 1    
        self.func,self.tlist = self.func_list[self.func_index]

    def characters(self, data):
        if self.func:
            self.tlist.append(data)

#-------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
#-------------------------------------------------------------------------
class GrampsImportParser(GrampsParser):

    def __init__(self,database,callback,base):
        GrampsParser.__init__(self,database,callback,base)

    def start_childof(self,attrs):
        family = self.db.find_family_no_conflicts(attrs["ref"],self.fmap)
        if attrs.has_key("mrel"):
            mrel = attrs["mrel"]
        else:
            mrel = "Birth"
        if attrs.has_key("frel"):
            frel = attrs["frel"]
        else:
            frel = "Birth"
        self.person.add_parent_family_id(family.get_id(),mrel,frel)

    def start_parentin(self,attrs):
        self.person.add_family_id(attrs["ref"])

    def start_bmark(self,attrs):
        person = self.db.find_person_no_conflicts(attrs["ref"],self.pmap)
        self.db.bookmarks.append(person)

    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.find_person_no_conflicts(attrs["id"],self.pmap)
        if attrs.has_key("complete"):
            self.person.set_complete(int(attrs['complete']))
        else:
            self.person.set_complete(0)

    def start_father(self,attrs):
        self.family.set_father_id(attrs["ref"])

    def start_mother(self,attrs):
        self.family.set_mother_id(attrs["ref"])
    
    def start_child(self,attrs):
        self.family.add_child_id(attrs["ref"])

    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.find_family_no_conflicts(attrs["id"],self.fmap)
        if attrs.has_key("type"):
            self.family.set_relationship(const.save_frel(attrs["type"]))
        if attrs.has_key("complete"):
            self.family.set_complete(int(attrs['complete']))
        else:
            self.family.set_complete(0)

    def start_source(self,attrs):
        self.source = self.db.find_source_no_conflicts(attrs["id"],self.smap)

    def start_sourceref(self,attrs):
        self.source_ref = RelLib.SourceRef()
        source = self.db.find_source_no_conflicts(attrs["ref"],self.smap)
        if attrs.has_key("conf"):
            self.source_ref.confidence = int(attrs["conf"])
        else:
            self.source_ref.confidence = self.conf
        self.source_ref.set_base_id(source.get_id())
        if self.photo:
            self.photo.add_source_reference(self.source_ref)
        elif self.ord:
            self.ord.add_source_reference(self.source_ref)
        elif self.object:
            self.object.add_source_reference(self.source_ref)
        elif self.event:
            self.event.add_source_reference(self.source_ref)
        elif self.address:
            self.address.add_source_reference(self.source_ref)
        elif self.name:
            self.name.add_source_reference(self.source_ref)
        elif self.attribute:
            self.attribute.add_source_reference(self.source_ref)
        elif self.placeobj:
            self.placeobj.add_source_reference(self.source_ref)
        elif self.family:
            self.family.add_source_reference(self.source_ref)

    def start_place(self,attrs):
        self.placeobj = self.db.find_place_no_conflicts(attrs['ref'],self.lmap)

    def start_placeobj(self,attrs):
        self.placeobj = self.db.find_place_no_conflicts(attrs['id'],self.lmap)
        title = attrs['title']
        if title == "":
            title = attrs['id']
        self.placeobj.set_title(title)
        self.locations = 0
        if self.num_places > 0:
            if self.callback != None and self.count % self.increment == 0:
                self.callback(float(self.count)/float(self.entries))
            self.count = self.count + 1

    def start_objref(self,attrs):
        self.objref = RelLib.MediaRef()
        id = self.db.find_object_no_conflicts(attrs['ref'],self.media_file_map).get_id()
        self.objref.set_reference_id(id)
        if attrs.has_key('priv'):
            self.objref.set_privacy(int(attrs['priv']))
        if self.family:
            self.family.add_media_reference(self.objref)
        elif self.source:
            self.source.add_media_reference(self.objref)
        elif self.person:
            self.person.add_media_reference(self.objref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.objref)

    def start_object(self,attrs):
        self.object = self.db.find_object_no_conflicts(attrs['id'],self.media_file_map)
        self.object.set_mime_type(attrs['mime'])
        self.object.set_description(attrs['description'])
        src = attrs["src"]
        if src:
            if src[0] != '/':
                self.object.set_path("%s/%s" % (self.db.get_save_path(),src))
            else:
                self.object.set_path(src)

def append_value(orig,val):
    if orig:
        return "%s, %s" % (orig,val)
    else:
        return val

def build_place_title(loc):
    "Builds a title from a location"
    city = loc.get_city()
    state = loc.get_state()
    country = loc.get_country()
    county = loc.get_county()
    parish = loc.get_parish()
    
    value = ""

    if parish:
        value = parish
    if city:
        value = append_value(value,city)
    if county:
        value = append_value(value,county)
    if state:
        value = append_value(value,state)
    if country:
        value = append_value(value,country)
    return value
