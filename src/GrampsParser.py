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

import string
import os
import sys

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
if sys.version[0] != '1':
    try:
        from _xmlplus.sax import handler
        from _xmlplus.sax import make_parser
    except:
        from xml.sax import handler
        from xml.sax import make_parser
else:
    from xml.sax import handler
    from xml.sax import make_parser

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
def fix_spaces(text_list):
    val = ""
    for text in text_list:
        val = val + string.join(string.split(text),' ') + "\n"
    return val

#-------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
#-------------------------------------------------------------------------
class GrampsParser(handler.ContentHandler):

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------

    def __init__(self,database,callback,base):
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []
        self.tlist = []
        
        self.use_p = 0
        self.in_note = 0
        self.in_old_attr = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.db = database
        self.base = base
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

        handler.ContentHandler.__init__(self)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def setDocumentLocator(self,locator):
        self.locator = locator

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def endDocument(self):
        self.db.setResearcher(self.owner)
        if self.tempDefault != None:
            id = self.tempDefault
            if self.db.personMap.has_key(id):
                person = self.db.personMap[id]
                self.db.setDefaultPerson(person)
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_place(self,attrs):
        if attrs.has_key('ref'):
            self.placeobj = self.db.findPlaceNoMap(u2l(attrs['ref']))
        else:
            self.placeobj = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_placeobj(self,attrs):
        self.placeobj = self.db.findPlaceNoMap(u2l(attrs['id']))
        self.placeobj.set_title(u2l(attrs['title']))
        self.locations = 0

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_location(self,attrs):
        loc = Location()
        if attrs.has_key('city'):
            loc.set_city(u2l(attrs['city']))
        if attrs.has_key('state'):
            loc.set_state(u2l(attrs['state']))
        if attrs.has_key('county'):
            loc.set_county(u2l(attrs['county']))
        if attrs.has_key('country'):
            loc.set_country(u2l(attrs['country']))
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
        self.locations = self.locations + 1
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_coord(self,attrs):
        if attrs.has_key('lat'):
            self.placeobj.set_latitude(u2l(attrs['lat']))
        if attrs.has_key('long'):
            self.placeobj.set_longitude(u2l(attrs['long']))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_event(self,attrs):
        self.event = Event()
        self.event_type = u2l(attrs["type"])
        if attrs.has_key("conf"):
            self.event.confidence = int(attrs["conf"])
        if attrs.has_key("priv"):
            self.event.private = int(attrs["priv"])
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_attribute(self,attrs):
        self.attribute = Attribute()
        if attrs.has_key("conf"):
            self.attribute.confidence = int(attrs["conf"])
        if attrs.has_key("priv"):
            self.attribute.privacy = int(attrs["priv"])
        if attrs.has_key('type'):
            self.in_old_attr = 1
            self.attribute.setType(u2l(attrs["type"]))
        else:
            self.in_old_attr = 0
        if self.person:
            self.person.addAttribute(self.attribute)
        elif self.family:
            self.family.addAttribute(self.attribute)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_address(self,attrs):
        self.address = Address()
        self.person.addAddress(self.address)
        if attrs.has_key("conf"):
            self.address.confidence = int(attrs["conf"])
        if attrs.has_key("priv"):
            self.address.private = int(attrs["priv"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_bmark(self,attrs):
        person = self.db.findPersonNoMap(u2l(attrs["ref"]))
        self.db.bookmarks.append(person)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.findPersonNoMap(u2l(attrs["id"]))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_people(self,attrs):
        if attrs.has_key("default"):
            self.tempDefault = attrs["default"]

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_father(self,attrs):
        self.family.Father = self.db.findPersonNoMap(u2l(attrs["ref"]))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_mother(self,attrs):
        self.family.Mother = self.db.findPersonNoMap(u2l(attrs["ref"]))
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_child(self,attrs):
        self.family.Children.append(self.db.findPersonNoMap(u2l(attrs["ref"])))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.findFamilyNoMap(u2l(attrs["id"]))
        if attrs.has_key("type"):
            self.family.setRelationship(u2l(attrs["type"]))
        else:
            self.family.setRelationship("")

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_childof(self,attrs):
        family = self.db.findFamilyNoMap(u2l(attrs["ref"]))
        if attrs.has_key("type"):
            type = u2l(attrs["type"])
            self.person.AltFamilyList.append((family,type,type))
        elif attrs.has_key("mrel") or attrs.has_key("frel"):
            if attrs.has_key("mrel"):
                mrel = u2l(attrs["mrel"])
            else:
                mrel = ""
            if attrs.has_key("frel"):
                frel = u2l(attrs["frel"])
            else:
                frel = ""
            if mrel=="Birth" and frel=="Birth":
                self.person.MainFamily = family
            else:
                self.person.AltFamilyList.append((family,mrel,frel))
        else:
            self.person.MainFamily = family

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_parentin(self,attrs):
        self.person.FamilyList.append(self.db.findFamilyNoMap(u2l(attrs["ref"])))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_name(self,attrs):
        self.name = Name()
        if attrs.has_key("conf"):
            self.name.confidence = int(attrs["conf"])
        if attrs.has_key("priv"):
            self.name.private = int(attrs["priv"])
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_note(self,attrs):
        self.in_note = 1

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_sourceref(self,attrs):
        self.source_ref = SourceRef()
        source = self.db.findSourceNoMap(u2l(attrs["ref"]))
        self.source_ref.setBase(source)
        if self.event:
            self.event.setSourceRef(self.source_ref)
        elif self.address:
            self.address.setSourceRef(self.source_ref)
        elif self.name:
            self.name.setSourceRef(self.source_ref)
        elif self.attribute:
            self.attribute.setSourceRef(self.source_ref)
        elif self.placeobj:
            self.placeobj.setSourceRef(self.source_ref)
        else: 
            print "Sorry, I'm lost"

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_source(self,attrs):
        self.source = self.db.findSourceNoMap(u2l(attrs["id"]))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_photo(self,attrs):
        photo = Photo()
        for key in attrs.keys():
            if key == "descrip" or key == "description":
                photo.setDescription(u2l(attrs[key]))
            elif key == "src":
                src = u2l(attrs["src"])
                if src[0] != os.sep:
                    photo.setPath("%s%s%s" % (self.base,os.sep,src))
                    photo.setPrivate(1)
                else:
                    photo.setPath(src)
                    photo.setPrivate(0)
                if self.family:
                    self.family.addPhoto(photo)
                elif self.source:
                    self.source.addPhoto(photo)
                elif self.person:
                    self.person.addPhoto(photo)
                elif self.placeobj:
                    self.placeobj.addPhoto(photo)
            else:
                photo.addProperty(key,attrs[key])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_created(self,attrs):
        self.entries = int(attrs["people"]) + int(attrs["families"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_pos(self,attrs):
        self.person.position = (int(u2l(attrs["x"])), int(u2l(attrs["y"])))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_attribute(self,tag):
        if self.in_old_attr:
            self.attribute.setValue(u2l(tag))
        self.in_old_attr = 0
        self.attribute = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_attr_type(self,tag):
        self.attribute.setType(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_attr_value(self,tag):
        self.attribute.setValue(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_address(self,tag):
        self.address = None
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_places(self,tag):
        self.placeobj = None

    def stop_placeobj(self,tag):
        if self.placeobj.get_title() == "":
            loc = self.placeobj.get_main_location()
            self.placeobj.set_title(build_place_title(loc))
        self.palceobj = None
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_name(self,tag):
        self.person.PrimaryName = self.name
        self.name = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_place(self,tag):
        if self.placeobj == None:
            if self.place_map.has_key(u2l(tag)):
                self.placeobj = self.place_map[u2l(tag)]
            else:
                self.placeobj = Place()
                self.placeobj.set_title(u2l(tag))
                self.db.addPlace(self.placeobj)
                self.place_map[u2l(tag)] = self.placeobj
        self.event.place = self.placeobj
            
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_uid(self,tag):
        self.person.setPafUid(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_date(self,tag):
        if tag:
            if self.address:
                self.address.setDate(u2l(tag))
            else:
                self.event.date.quick_set(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_first(self,tag):
        self.name.FirstName = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_families(self,tag):
        self.family = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_people(self,tag):
        self.person = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_description(self,tag):
        self.event.setDescription(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_gender(self,tag):
        self.person.gender = (u2l(tag) == "M")

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_stitle(self,tag):
        self.source.setTitle(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_sourceref(self,tag):
        self.source_ref = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_source(self,tag):
        self.source = None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_sauthor(self,tag):
        self.source.setAuthor(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_sdate(self,tag):
        date = Date()
        date.quick_set(u2l(tag))
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_spage(self,tag):
        self.source_ref.setPage(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_spubinfo(self,tag):
        self.source.setPubInfo(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_scallno(self,tag):
        self.source.setCallNumber(u2l(tag))
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_stext(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.stext_list)
        else:
            note = u2l(tag)
        self.source_ref.setText(note)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_scomments(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.scomments_list)
        else:
            note = u2l(tag)
        self.source_ref.setComments(note)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_last(self,tag):
        if self.name:
            self.name.Surname = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_suffix(self,tag):
        if self.name:
            self.name.Suffix = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_title(self,tag):
        if self.name:
            self.name.Title = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_nick(self,tag):
        if self.person:
            self.person.setNickName(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_note(self,tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.note_list)
        else:
            note = u2l(tag)

        if self.address:
            self.address.setNote(note)
        elif self.attribute:
            self.attribute.setNote(note)
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_research(self,tag):
        self.owner.set(self.resname, self.resaddr, self.rescity, self.resstate,
                       self.rescon, self.respos, self.resphone, self.resemail)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_resname(self,tag):
        self.resname = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_resaddr(self,tag):
        self.resaddr = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_rescity(self,tag):
        self.rescity = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_resstate(self,tag):
        self.resstate = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_rescountry(self,tag):
        self.rescon = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_respostal(self,tag):
        self.respos = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_resphone(self,tag):
        self.resphone = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_resemail(self,tag):
        self.resemail = u2l(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_ptag(self,tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(u2l(tag))
        elif self.in_stext:
            self.stext_list.append(u2l(tag))
        elif self.in_scomments:
            self.scomments_list.append(u2l(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_aka(self,tag):
        self.person.addAlternateName(self.name)
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
        "person"     : (start_person, None),
        "img"        : (start_photo, None),
        "place"      : (start_place, stop_place),
        "places"     : (None, stop_places),
        "placeobj"   : (start_placeobj,stop_placeobj),
        "location"   : (start_location,None),
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------

    def endElement(self,tag):

        if self.func:
            self.func(self,string.join(self.tlist))
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_bmark(self,attrs):
        person = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.db.bookmarks.append(person)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_person(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.person = self.db.findPerson("x%s" % u2l(attrs["id"]),self.pmap)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_father(self,attrs):
        father = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.setFather(father)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_mother(self,attrs):
        mother = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.setMother(mother)
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_child(self,attrs):
        child = self.db.findPerson("x%s" % u2l(attrs["ref"]),self.pmap)
        self.family.addChild(child)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_family(self,attrs):
        if self.callback != None and self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        self.family = self.db.findFamily(u2l(attrs["id"]),self.fmap)
        if attrs.has_key("type"):
            self.family.setRelationship(u2l(attrs["type"]))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_childof(self,attrs):
        family = self.db.findFamily(u2l(attrs["ref"]),self.fmap)
        if attrs.has_key("type"):
            type = u2l(attrs["type"])
            self.person.addAltFamily(family,type)
        else:
            self.person.setMainFamily(family)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_sourceref(self,attrs):
        self.source_ref = SourceRef()
        self.source = self.db.findSource(u2l(attrs["ref"]),self.smap)
        self.source_ref.setBase(self.source)
        if self.address:
            self.address.setSourceRef(self.source_ref)
        elif self.name:
            self.name.setSourceRef(self.source_ref)
        elif self.event:
            self.event.setSourceRef(self.source_ref)
        elif self.attribute:
            self.attribute.setSourceRef(self.source_ref)
        elif self.placeobj:
            self.placeobj.setSourceRef(self.source_ref)
        else: 
            print "Sorry, I'm lost"

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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

    value = ""

    if city:
        value = city
    if county:
        value = append_value(value,county)
    if state:
        value = append_value(value,state)
    if country:
        value = append_value(value,country)
    return value

