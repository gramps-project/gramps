#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

from RelLib import *
from Date import SingleDate

import string
import Utils
import xml.parsers.expat
    
#-------------------------------------------------------------------------
#
# Unicode to latin conversion
#
#-------------------------------------------------------------------------
from latin_utf8 import utf8_to_latin
u2l = utf8_to_latin

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
        
        self.callback = callback
        self.entries = 0
        self.count = 0
        self.increment = 100
        self.event = None
        self.name = None
        self.tempDefault = None
        self.owner = Researcher()
	self.func_list = [None]*50
	self.func_index = 0
	self.func = None

    def parse(self,file):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.ParseFile(file)
            
        self.db.setResearcher(self.owner)
        if self.tempDefault != None:
            id = self.tempDefault
            if self.db.personMap.has_key(id):
                person = self.db.personMap[id]
                self.db.setDefaultPerson(person)

    def start_lds_ord(self,attrs):
        type = u2l(attrs['type'])
        self.ord = LdsOrd()
        if self.person:
            if type == "baptism":
                self.person.setLdsBaptism(self.ord)
            elif type == "endowment":
                self.person.setLdsEndowment(self.ord)
            elif type == "sealed_to_parents":
                self.person.setLdsSeal(self.ord)
        elif self.family:
            if type == "sealed_to_spouse":
                self.family.setLdsSeal(self.ord)

    def start_temple(self,attrs):
        self.ord.setTemple(u2l(attrs['val']))

    def start_status(self,attrs):
        self.ord.setStatus(int(u2l(attrs['val'])))

    def start_sealed_to(self,attrs):
        id = u2l(attrs['ref'])
        self.ord.setFamily(self.db.findFamilyNoMap(id))
        
    def start_place(self,attrs):
        if attrs.has_key('ref'):
            self.placeobj = self.db.findPlaceNoMap(u2l(attrs['ref']))
        else:
            self.placeobj = None

    def start_placeobj(self,attrs):
        self.placeobj = self.db.findPlaceNoMap(u2l(attrs['id']))
        title = u2l(attrs['title'])
        if title == "":
            title = u2l(attrs['id'])
        self.placeobj.set_title(title)
        self.locations = 0
        if self.num_places > 0:
            if self.callback != None and self.count % self.increment == 0:
                self.callback(float(self.count)/float(self.entries))
            self.count = self.count + 1

    def start_location(self,attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""
        
        loc = Location()
        if attrs.has_key('city'):
            loc.city = u2l(attrs['city'])
        if attrs.has_key('parish'):
            loc.parish = u2l(attrs['parish'])
        if attrs.has_key('state'):
            loc.state = u2l(attrs['state'])
        if attrs.has_key('county'):
            loc.county = u2l(attrs['county'])
        if attrs.has_key('country'):
            loc.country = u2l(attrs['country'])
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
            self.locations = self.locations + 1
        
    def start_coord(self,attrs):
        if attrs.has_key('lat'):
            self.placeobj.set_latitude(u2l(attrs['lat']))
        if attrs.has_key('long'):
            self.placeobj.set_longitude(u2l(attrs['long']))

    def start_event(self,attrs):
        self.event = Event()
        self.event_type = u2l(attrs["type"])
        if attrs.has_key("conf"):
            self.event.conf = int(attrs["conf"])
        else:
            self.event.conf = 2
        if attrs.has_key("priv"):
            self.event.private = int(attrs["priv"])
        
    def start_attribute(self,attrs):
        self.attribute = Attribute()
        if attrs.has_key("conf"):
            self.attribute.conf = int(attrs["conf"])
        else:
            self.attribute.conf = 2
        if attrs.has_key("priv"):
            self.attribute.private = int(attrs["priv"])
        if attrs.has_key('type'):
            self.attribute.setType(u2l(attrs["type"]))
        if attrs.has_key('value'):
            self.attribute.setValue(u2l(attrs["value"]))
        if self.photo:
            self.photo.addAttribute(self.attribute)
        elif self.object:
            self.object.addAttribute(self.attribute)
        elif self.objref:
            self.objref.addAttribute(self.attribute)
        elif self.person:
            self.person.addAttribute(self.attribute)
        elif self.family:
            self.family.addAttribute(self.attribute)

    def start_address(self,attrs):
        self.address = Address()
        self.person.addAddress(self.address)
        if attrs.has_key("conf"):
            self.address.conf = int(attrs["conf"])
        else:
            self.address.conf = 2
        if attrs.has_key("priv"):
            self.address.private = int(attrs["priv"])

    def start_bmark(self,attrs):
        person = self.db.findPersonNoMap(u2l(attrs["ref"]))
        self.db.bookmarks.append(person)

    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.findPersonNoMap(u2l(attrs["id"]))

    def start_people(self,attrs):
        if attrs.has_key("default"):
            self.tempDefault = u2l(attrs["default"])

    def start_father(self,attrs):
        self.family.Father = self.db.findPersonNoMap(u2l(attrs["ref"]))

    def start_mother(self,attrs):
        self.family.Mother = self.db.findPersonNoMap(u2l(attrs["ref"]))
    
    def start_child(self,attrs):
        self.family.Children.append(self.db.findPersonNoMap(u2l(attrs["ref"])))

    def start_url(self,attrs):

        if not attrs.has_key("href"):
            return
        try:
            desc = u2l(attrs["description"])
        except KeyError:
            desc = ""

        try:
            url = Url()
            url.set_path(u2l(attrs["href"]))
            url.set_description(desc)
            if attrs.has_key("priv"):
                url.setPrivacy(int(attrs['priv']))
            if self.person:
                self.person.addUrl(url)
            elif self.placeobj:
                self.placeobj.addUrl(url)
        except KeyError:
            return

    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.findFamilyNoMap(u2l(attrs["id"]))
        if attrs.has_key("type"):
            self.family.setRelationship(u2l(attrs["type"]))
        else:
            self.family.setRelationship("")

    def start_childof(self,attrs):
        family = self.db.findFamilyNoMap(u2l(attrs["ref"]))
        if attrs.has_key("mrel"):
            mrel = u2l(attrs["mrel"])
        else:
            mrel = "Birth"
        if attrs.has_key("frel"):
            frel = u2l(attrs["frel"])
        else:
            frel = "Birth"
        self.person.AltFamilyList.append((family,mrel,frel))

    def start_parentin(self,attrs):
        self.person.FamilyList.append(self.db.findFamilyNoMap(u2l(attrs["ref"])))

    def start_name(self,attrs):
        self.name = Name()
        if attrs.has_key("type"):
            self.name.setType(u2l(attrs["type"]))
        if attrs.has_key("conf"):
            self.name.conf = int(attrs["conf"])
        else:
            self.name.conf = 2
        if attrs.has_key("priv"):
            self.name.private = int(attrs["priv"])
        
    def start_note(self,attrs):
        self.in_note = 1

    def start_sourceref(self,attrs):
        self.source_ref = SourceRef()
        source = self.db.findSourceNoMap(u2l(attrs["ref"]))
        if attrs.has_key("conf"):
            self.source_ref.confidence = int(u2l(attrs["conf"]))
        else:
            self.source_ref.confidence = self.conf
        self.source_ref.setBase(source)
        if self.photo:
            self.photo.addSourceRef(self.source_ref)
        elif self.ord:
            self.ord.addSourceRef(self.source_ref)
        elif self.object:
            self.object.addSourceRef(self.source_ref)
        elif self.event:
            self.event.addSourceRef(self.source_ref)
        elif self.address:
            self.address.addSourceRef(self.source_ref)
        elif self.name:
            self.name.addSourceRef(self.source_ref)
        elif self.attribute:
            self.attribute.addSourceRef(self.source_ref)
        elif self.placeobj:
            self.placeobj.addSourceRef(self.source_ref)

    def start_source(self,attrs):
        if self.num_srcs > 0:
            if self.callback != None and self.count % self.increment == 0:
                self.callback(float(self.count)/float(self.entries))
            self.count = self.count + 1
        self.source = self.db.findSourceNoMap(u2l(attrs["id"]))

    def start_objref(self,attrs):
        self.objref = ObjectRef()
        self.objref.setReference(self.db.findObjectNoMap(u2l(attrs['ref'])))
        if attrs.has_key('priv'):
            self.objref.setPrivacy(int(u2l(attrs['priv'])))
        if self.family:
            self.family.addPhoto(self.objref)
        elif self.source:
            self.source.addPhoto(self.objref)
        elif self.person:
            self.person.addPhoto(self.objref)
        elif self.placeobj:
            self.placeobj.addPhoto(self.objref)

    def start_object(self,attrs):
        self.object = self.db.findObjectNoMap(u2l(attrs['id']))
        self.object.setMimeType(u2l(attrs['mime']))
        self.object.setDescription(u2l(attrs['description']))
        src = u2l(attrs["src"])
        if src:
            if src[0] != '/':
                self.object.setPath("%s/%s" % (self.base,src))
                self.object.setLocal(1)
            else:
                self.object.setPath(src)
                self.object.setLocal(0)

    def stop_object(self,tag):
        self.object = None

    def stop_objref(self,tag):
        self.objref = None
        
    def start_photo(self,attrs):
        self.photo = Photo()
        self.pref = ObjectRef()
        self.pref.setReference(self.photo)
        
        for key in attrs.keys():
            if key == "descrip" or key == "description":
                self.photo.setDescription(u2l(attrs[key]))
            elif key == "priv":
                self.pref.setPrivacy(int(attrs[key]))
            elif key == "src":
                src = u2l(attrs["src"])
                if src[0] != '/':
                    self.photo.setPath("%s/%s" % (self.base,src))
                    self.photo.setLocal(1)
                else:
                    self.photo.setPath(src)
                    self.photo.setLocal(0)
            else:
                a = Attribute()
                a.setType(key)
                a.setValue(u2l(attrs[key]))
                self.photo.addAttribute(a)
        self.photo.setMimeType(Utils.get_mime_type(self.photo.getPath()))
        self.db.addObject(self.photo)
        if self.family:
            self.family.addPhoto(self.pref)
        elif self.source:
            self.source.addPhoto(self.pref)
        elif self.person:
            self.person.addPhoto(self.pref)
        elif self.placeobj:
            self.placeobj.addPhoto(self.pref)

    def start_daterange(self,attrs):
        if self.source_ref:
            d = self.source_ref.getDate()
        elif self.ord:
            d = self.ord.getDateObj()
        elif self.address:
            d = self.address.getDateObj()
        else:
            d = self.event.getDateObj()

        if attrs.has_key("calendar"):
            d.set_calendar(int(attrs['calendar']))

        d.get_start_date().setIsoDate(u2l(attrs['start']))
        d.get_stop_date().setIsoDate(u2l(attrs['stop']))
        d.range = 1
        
    def start_dateval(self,attrs):
        if self.source_ref:
            d = self.source_ref.getDate()
        elif self.ord:
            d = self.ord.getDateObj()
        elif self.address:
            d = self.address.getDateObj()
        else:
            d = self.event.getDateObj()

        if attrs.has_key("calendar"):
            d.set_calendar(int(attrs['calendar']))

        d.get_start_date().setIsoDate(u2l(attrs['val']))
        
        if attrs.has_key("type"):
            d.get_start_date().setMode(u2l(attrs['type']))
        else:
            d.get_start_date().setMode(None)

    def start_datestr(self,attrs):
        if self.source_ref:
            d = self.source_ref.getDate()
        elif self.ord:
            d = self.ord.getDateObj()
        elif self.address:
            d = self.address.getDateObj()
        else:
            d = self.event.getDateObj()

        d.set(u2l(attrs['val']))

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

    def stop_attr_type(self,tag):
        self.attribute.setType(u2l(tag))

    def stop_attr_value(self,tag):
        self.attribute.setValue(u2l(tag))

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
        self.db.buildPlaceDisplay(self.placeobj.getId())
        self.palceobj = None
        
    def stop_event(self,tag):
        self.event.name = self.event_type

        if self.family:
            self.family.EventList.append(self.event)
        else:
            if self.event_type == "Birth":
                self.person.setBirth(self.event)
            elif self.event_type == "Death":
                self.person.setDeath(self.event)
            else:
                self.person.EventList.append(self.event)
        self.event = None

    def stop_name(self,tag):
        self.person.PrimaryName = self.name
        if self.name.getType() == "":
            self.name.setType("Birth Name")
        self.name = None

    def stop_place(self,tag):
        if self.placeobj == None:
            if self.place_map.has_key(u2l(tag)):
                self.placeobj = self.place_map[u2l(tag)]
            else:
                self.placeobj = Place()
                self.placeobj.set_title(u2l(tag))
                self.db.addPlace(self.placeobj)
                self.place_map[u2l(tag)] = self.placeobj
        if self.ord:
            self.ord.setPlace(self.placeobj)
        else:
            self.event.place = self.placeobj
            
    def stop_uid(self,tag):
        self.person.setPafUid(u2l(tag))

    def stop_date(self,tag):
        if tag:
            if self.address:
                self.address.setDate(u2l(tag))
            else:
                self.event.setDate(u2l(tag))

    def stop_first(self,tag):
        self.name.FirstName = u2l(tag)

    def stop_families(self,tag):
        self.family = None

    def stop_people(self,tag):
        self.person = None

    def stop_person(self,tag):
        self.db.buildPersonDisplay(self.person.getId())

    def stop_description(self,tag):
        self.event.setDescription(u2l(tag))

    def stop_cause(self,tag):
        self.event.setCause(u2l(tag))

    def stop_gender(self,tag):
        t = u2l(tag)
        if t == "M":
            self.person.gender = Person.male
        elif t == "F":
            self.person.gender = Person.female
        else:
            self.person.gender = Person.unknown

    def stop_stitle(self,tag):
        self.source.setTitle(u2l(tag))

    def stop_sourceref(self,tag):
        self.source_ref = None

    def stop_source(self,tag):
        self.db.buildSourceDisplay(self.source.getId())
        self.source = None

    def stop_sauthor(self,tag):
        self.source.setAuthor(u2l(tag))

    def stop_sdate(self,tag):
        date = Date()
        date.set(u2l(tag))
        self.source_ref.setDate(date)
        
    def stop_street(self,tag):
        self.address.setStreet(u2l(tag))

    def stop_city(self,tag):
        self.address.setCity(u2l(tag))

    def stop_state(self,tag):
        self.address.setState(u2l(tag))
        
    def stop_country(self,tag):
        self.address.setCountry(u2l(tag))

    def stop_postal(self,tag):
        self.address.setPostal(u2l(tag))

    def stop_spage(self,tag):
        self.source_ref.setPage(u2l(tag))

    def stop_lds_ord(self,tag):
        self.ord = None

    def stop_spubinfo(self,tag):
        self.source.setPubInfo(u2l(tag))

    def stop_scallno(self,tag):
        self.source.setCallNumber(u2l(tag))
        
    def stop_stext(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.stext_list)
        else:
            note = u2l(tag)
        self.source_ref.setText(note)

    def stop_scomments(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.scomments_list)
        else:
            note = u2l(tag)
        self.source_ref.setComments(note)

    def stop_last(self,tag):
        if self.name:
            self.name.Surname = u2l(tag)

    def stop_suffix(self,tag):
        if self.name:
            self.name.Suffix = u2l(tag)

    def stop_title(self,tag):
        if self.name:
            self.name.Title = u2l(tag)

    def stop_nick(self,tag):
        if self.person:
            self.person.setNickName(u2l(tag))

    def stop_note(self,tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.note_list)
        else:
            note = u2l(tag)

        if self.address:
            self.address.setNote(note)
        elif self.ord:
            self.ord.setNote(note)
        elif self.attribute:
            self.attribute.setNote(note)
        elif self.object:
            self.object.setNote(note)
        elif self.objref:
            self.objref.setNote(note)
        elif self.photo:
            self.photo.setNote(note)
        elif self.name:
            self.name.setNote(note)
        elif self.source:
            self.source.setNote(note)
        elif self.event:
            self.event.setNote(note)
        elif self.person:
            self.person.setNote(note)
        elif self.family:
            self.family.setNote(note)
        elif self.placeobj:
            self.placeobj.setNote(note)
        self.note_list = []

    def stop_research(self,tag):
        self.owner.set(self.resname, self.resaddr, self.rescity, self.resstate,
                       self.rescon, self.respos, self.resphone, self.resemail)

    def stop_resname(self,tag):
        self.resname = u2l(tag)

    def stop_resaddr(self,tag):
        self.resaddr = u2l(tag)

    def stop_rescity(self,tag):
        self.rescity = u2l(tag)

    def stop_resstate(self,tag):
        self.resstate = u2l(tag)

    def stop_rescountry(self,tag):
        self.rescon = u2l(tag)

    def stop_respostal(self,tag):
        self.respos = u2l(tag)

    def stop_resphone(self,tag):
        self.resphone = u2l(tag)

    def stop_resemail(self,tag):
        self.resemail = u2l(tag)

    def stop_ptag(self,tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(u2l(tag))
        elif self.in_stext:
            self.stext_list.append(u2l(tag))
        elif self.in_scomments:
            self.scomments_list.append(u2l(tag))

    def stop_aka(self,tag):
        self.person.addAlternateName(self.name)
        if self.name.getType() == "":
            self.name.setType("Also Known As")
        self.name = None

    func_map = {
        "address"    : (start_address, stop_address),
        "addresses"  : (None,None),
        "childlist"  : (None,None),
        "aka"        : (start_name, stop_aka),
        "attribute"  : (start_attribute, stop_attribute),
        "attr_type"  : (None,stop_attr_type),
        "attr_value" : (None,stop_attr_value),
        "bookmark"   : (start_bmark, None),
        "bookmarks"  : (None, None),
        "child"      : (start_child,None),
        "childof"    : (start_childof,None),
        "city"       : (None, stop_city),
        "country"    : (None, stop_country),
        "created"    : (start_created, None),
        "database"   : (None, None),
        "date"       : (None, stop_date),
        "cause"      : (None, stop_cause),
        "description": (None, stop_description),
        "event"      : (start_event, stop_event),
        "families"   : (None, stop_families),
        "family"     : (start_family, None),
        "father"     : (start_father, None),
        "first"      : (None, stop_first),
        "gender"     : (None, stop_gender),
        "header"     : (None, None),
        "last"       : (None, stop_last),
        "mother"     : (start_mother,None),
        "name"       : (start_name, stop_name),
        "nick"       : (None, stop_nick),
        "note"       : (start_note, stop_note),
        "p"          : (None, stop_ptag),
        "parentin"   : (start_parentin,None),
        "people"     : (start_people, stop_people),
        "person"     : (start_person, stop_person),
        "img"        : (start_photo, stop_photo),
        "objref"     : (start_objref, stop_objref),
        "object"     : (start_object, stop_object),
        "place"      : (start_place, stop_place),
        "dateval"    : (start_dateval, None),
        "daterange"  : (start_daterange, None),
        "datestr"    : (start_datestr, None),
        "places"     : (None, stop_places),
        "placeobj"   : (start_placeobj,stop_placeobj),
        "location"   : (start_location,None),
        "lds_ord"    : (start_lds_ord, stop_lds_ord),
        "temple"     : (start_temple, None),
        "status"     : (start_status, None),
        "sealed_to"  : (start_sealed_to, None),
        "coord"      : (start_coord,None),
        "pos"        : (start_pos, None),
        "postal"     : (None, stop_postal),
        "researcher" : (None, stop_research),
    	"resname"    : (None, stop_resname ),
    	"resaddr"    : (None, stop_resaddr ),
	"rescity"    : (None, stop_rescity ),
    	"resstate"   : (None, stop_resstate ),
    	"rescountry" : (None, stop_rescountry),
    	"respostal"  : (None, stop_respostal),
    	"resphone"   : (None, stop_resphone),
    	"resemail"   : (None, stop_resemail),
        "sauthor"    : (None, stop_sauthor),
        "scallno"    : (None, stop_scallno),
        "scomments"  : (None, stop_scomments),
        "sdate"      : (None,stop_sdate),
        "source"     : (start_source, stop_source),
        "sourceref"  : (start_sourceref, stop_sourceref),
        "sources"    : (None, None),
        "spage"      : (None, stop_spage),
        "spubinfo"   : (None, stop_spubinfo),
        "state"      : (None, stop_state),
        "stext"      : (None, stop_stext),
        "stitle"     : (None, stop_stitle),
        "street"     : (None, stop_street),
        "suffix"     : (None, stop_suffix),
        "title"      : (None, stop_title),
        "uid"        : (None, stop_uid),
        "url"        : (start_url, None)
        }

    def startElement(self,tag,attrs):

        self.func_list[self.func_index] = (self.func,self.tlist)
        self.func_index = self.func_index + 1
        self.tlist = []

        try:
	    f,self.func = GrampsParser.func_map[tag]
            if f:
                f(self,attrs)
        except KeyError:
            GrampsParser.func_map[tag] = (None,None)
            self.func = None

    def endElement(self,tag):

        if self.func:
            self.func(self,string.join(self.tlist,''))
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

    def start_bmark(self,attrs):
        person = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.db.bookmarks.append(person)

    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.findPerson("x%s" % u2l(attrs["id"]),self.pmap)

    def start_father(self,attrs):
        father = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.setFather(father)

    def start_mother(self,attrs):
        mother = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.setMother(mother)
    
    def start_child(self,attrs):
        child = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.addChild(child)

    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.findFamily(u2l(attrs["id"]),self.fmap)
        if attrs.has_key("type"):
            self.family.setRelationship(u2l(attrs["type"]))

    def start_sourceref(self,attrs):
        self.source_ref = SourceRef()
        self.source = self.db.findSource(u2l(attrs["ref"]),self.smap)
        self.source_ref.setBase(self.source)
        if self.address:
            self.address.addSourceRef(self.source_ref)
        elif self.name:
            self.name.addSourceRef(self.source_ref)
        elif self.event:
            self.event.addSourceRef(self.source_ref)
        elif self.attribute:
            self.attribute.addSourceRef(self.source_ref)
        elif self.placeobj:
            self.placeobj.addSourceRef(self.source_ref)
        else: 
            print "Sorry, I'm lost"

    def start_source(self,attrs):
        self.source = self.db.findSource(u2l(attrs["id"]),self.smap)


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

