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
from Researcher import Researcher

import string
import os

from xml.sax import handler

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
try:
    import xml.sax.saxexts
    sax = 1
except:
    sax = 2

from latin_utf8 import utf8_to_latin

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

    researchTag = "researcher"
    resnameTag  = "resname"
    resaddrTag  = "resaddr"
    rescityTag  = "rescity"
    resstateTag = "resstate"
    resconTag   = "rescountry"
    resposTag   = "respostal"
    resphoneTag = "resphone"
    resemailTag = "resemail"
    attrTag     = "attribute"
    addressTag  = "address"
    startTag    = "date_start"
    stopTag     = "date_stop"
    cityTag     = "city"
    stateTag    = "state"
    streetTag   = "street"
    countryTag  = "country"
    postalTag   = "postal"
    noteTag     = "note"
    uidTag      = "uid"
    urlTag      = "url"
    pTag        = "p"
    personTag   = "person"
    peopleTag   = "people"
    sourcesTag  = "sources"
    sourcerefTag= "sourceref"
    photoTag    = "img"
    nameTag     = "name"
    akaTag      = "aka"
    firstTag    = "first"
    lastTag     = "last"
    nickTag     = "nick"
    genderTag   = "gender"
    titleTag    = "title"
    suffixTag   = "suffix"
    placeTag    = "place"
    descriptionTag = "description"
    dateTag     = "date"
    familyTag   = "family"
    fatherTag   = "father"
    childTag    = "child"
    createdTag  = "created"
    childofTag  = "childof"
    parentinTag = "parentin"
    motherTag   = "mother"
    familiesTag = "families"
    eventTag    = "event"
    sourceTag   = "source"
    sdateTag    = "sdate"
    spageTag    = "spage"
    stitleTag   = "stitle"
    sauthorTag  = "sauthor"
    spubinfoTag = "spubinfo"
    scallnoTag  = "scallno"
    stextTag    = "stext"
    bmarksTag   = "bookmarks"
    bmarkTag    = "bookmark"
    scommentsTag= "scomments"
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------

    def __init__(self,database,callback,base,is_import):
        self.call = None
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []

        self.in_note = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.in_people = 0
        self.database = database
        self.base = base
        self.in_family = 0
        self.in_sources = 0
        self.person = None
        self.family = None
        self.source = None
        self.sourceRef = None
        self.is_import = is_import

        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        
        self.callback = callback
        self.entries = 0
        self.count = 0
        self.increment = 50
        self.event = None
        self.name = None
        self.tempDefault = None
        self.owner = Researcher()
        self.active = ""
        self.data = {}
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
        self.database.setResearcher(self.owner)
        if self.tempDefault != None:
            id = self.tempDefault
            if self.database.personMap.has_key(id):
                person = self.database.personMap[id]
                self.database.setDefaultPerson(person)
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_event(self,attrs):
        self.event = Event()
        self.event_type = string.capwords(attrs["type"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_attribute(self,attrs):
        self.attribute = Attribute()
        self.attribute.setType(string.capwords(attrs["type"]))
        self.person.addAttribute(self.attribute)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_address(self,attrs):
        self.address = Address()
        self.person.addAddress(self.address)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_bmark(self,attrs):
        if self.is_import:
            person = self.database.findPerson("x%s" % attrs["ref"],self.pmap)
        else:
            person = self.database.findPersonNoMap(attrs["ref"])
        self.database.bookmarks.append(person)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_person(self,attrs):
        if self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        if self.is_import:
            self.person = self.database.findPerson("x%s" % attrs["id"],self.pmap)
        else:
            self.person = self.database.findPersonNoMap(attrs["id"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_people(self,attrs):
        self.in_family  = 0
        self.in_people  = 1
        self.in_sources = 0
        if self.is_import == 0 and attrs.has_key("default"):
            self.tempDefault = int(attrs["default"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_father(self,attrs):
        if self.is_import:
            father = self.database.findPerson("x%s" % attrs["ref"],self.pmap)
        else:
            father = self.database.findPersonNoMap(attrs["ref"])
        self.family.setFather(father)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_mother(self,attrs):
        if self.is_import:
            mother = self.database.findPerson("x%s" % attrs["ref"],self.pmap)
        else:
            mother = self.database.findPersonNoMap(attrs["ref"])
        self.family.setMother(mother)
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_child(self,attrs):
        if self.is_import:
            child = self.database.findPerson("x%s" % attrs["ref"],self.pmap)
        else:
            child = self.database.findPersonNoMap(attrs["ref"])
        self.family.addChild(child)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_url(self,attrs):

        if not attrs.has_key("href"):
            return
        try:
            desc = attrs["description"]
        except KeyError:
            desc = ""

        try:
            url = Url(attrs["href"],desc)
            self.person.addUrl(url)
        except KeyError:
            return

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_family(self,attrs):
        if self.count % self.increment == 0:
            self.callback(float(self.count)/float(self.entries))
        self.count = self.count + 1
        if self.is_import:
            self.family = self.database.findFamily(attrs["id"],self.fmap)
        else:
            self.family = self.database.findFamilyNoMap(attrs["id"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_childof(self,attrs):
        if self.is_import:
            family = self.database.findFamily(attrs["ref"],self.fmap)
        else:
            family = self.database.findFamilyNoMap(attrs["ref"])
        if attrs.has_key("type"):
            type = attrs["type"]
            self.person.addAltFamily(family,type)
        else:
            self.person.setMainFamily(family)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_parentin(self,attrs):
        if self.is_import:
            family = self.database.findFamily(attrs["ref"],self.fmap)
        else:
            family = self.database.findFamilyNoMap(attrs["ref"])
        self.person.addFamily(family)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_name(self,attrs):
        self.name = Name()

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
    def start_families(self,attrs):
        self.in_family  = 1
        self.in_people  = 0
        self.in_sources = 0

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_sources(self,attrs):
        self.in_family  = 0
        self.in_people  = 0
        self.in_sources = 1
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_sourceref(self,attrs):
        self.source = Source()
        if self.is_import:
            self.sourceRef = self.database.findSource(attrs["ref"],self.smap)
        else:
            self.sourceRef = self.database.findSourceNoMap(attrs["ref"])
        self.source.setBase(self.sourceRef)
        self.event.setSource(self.source)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_source(self,attrs):
        if self.is_import:
            self.sourceRef = self.database.findSource(attrs["id"],self.smap)
        else:
            self.sourceRef = self.database.findSourceNoMap(attrs["id"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_photo(self,attrs):
        photo = Photo()
        if attrs.has_key("descrip"):
            photo.setDescription(attrs["descrip"])
        src = attrs["src"]
        if src[0] != os.sep:
            photo.setPath(self.base + os.sep + attrs["src"])
            photo.setPrivate(1)
        else:
            photo.setPath(src)
            photo.setPrivate(0)
        if self.in_family == 1:
            self.family.addPhoto(photo)
        else:
            self.person.addPhoto(photo)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def start_created(self,attrs):
        self.entries = string.atoi(attrs["people"]) + \
                       string.atoi(attrs["families"])

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_attribute(self,tag):
        self.attribute.setValue(tag)
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_event(self,tag):
        self.event.setName(self.event_type)

        if self.event_type == "Birth":
            self.person.setBirth(self.event)
        elif self.event_type == "Death":
            self.person.setDeath(self.event)
        elif self.event_type == "Marriage":
            self.family.setMarriage(self.event)
        elif self.event_type == "Divorce":
            self.family.setDivorce(self.event)
        elif self.in_people == 1:
            self.person.addEvent(self.event)
        else:
            self.family.addEvent(self.event)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_name(self,tag):
        self.person.setPrimaryName(self.name)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_place(self,tag):
        self.event.setPlace(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_uid(self,tag):
        self.person.setPafUid(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_date(self,tag):
        if tag != "":
            self.event.getDateObj().quick_set(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_first(self,tag):
        self.name.setFirstName(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_description(self,tag):
        self.event.setDescription(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_gender(self,tag):
        if tag == "M":
            self.person.setGender(Person.male)
        else:
            self.person.setGender(Person.female)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_stitle(self,tag):
        self.sourceRef.setTitle(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_sauthor(self,tag):
        self.sourceRef.setAuthor(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_sdate(self,tag):
        date = Date()
        date.quick_set(tag)
        self.source.setDate(date)
        
    def stop_date_start(self,tag):
        date = self.address.getStartDateObj()
        date.quick_set(tag)

    def stop_date_stop(self,tag):
        date = self.address.getStopDateObj()
        date.quick_set(tag)

    def stop_street(self,tag):
        self.address.setStreet(tag)

    def stop_city(self,tag):
        self.address.setCity(tag)

    def stop_state(self,tag):
        self.address.setState(tag)
        
    def stop_country(self,tag):
        self.address.setCountry(tag)

    def stop_postal(self,tag):
        self.address.setPostal(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_spage(self,tag):
        self.source.setPage(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_spubinfo(self,tag):
        self.sourceRef.setPubInfo(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_scallno(self,tag):
        self.sourceRef.setCallNumber(tag)
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_stext(self,tag):
        self.source.setText(fix_spaces(tag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_scomments(self,tag):
        self.source.setComments(fix_spaces(self.scomments_list))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_last(self,tag):
        self.name.setSurname(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_suffix(self,tag):
        self.name.setSuffix(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_title(self,tag):
        self.name.setTitle(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_nick(self,tag):
        self.person.setNickName(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_note(self,tag):
        self.in_note = 0
        if self.in_people == 1:
            self.person.setNote(fix_spaces(self.note_list))
        elif self.in_family == 1:
            self.family.setNote(fix_spaces(self.note_list))
        self.note_list = []

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def get_val(self,tag):
        if self.data.has_key(tag):
            return self.data[tag]
        else:
            return ""
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_research(self,tag):
        self.owner.set(self.get_val(GrampsParser.resnameTag), \
                       self.get_val(GrampsParser.resaddrTag), \
                       self.get_val(GrampsParser.rescityTag), \
                       self.get_val(GrampsParser.resstateTag), \
                       self.get_val(GrampsParser.resconTag), \
                       self.get_val(GrampsParser.resposTag),\
                       self.get_val(GrampsParser.resphoneTag),\
                       self.get_val(GrampsParser.resemailTag))

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_ptag(self,tag):
        if self.in_note:
            self.note_list.append(tag)
        elif self.in_stext:
            self.stext_list.append(tag)
        elif self.in_scomments:
            self.scomments_list.append(tag)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def stop_aka(self,tag):
        self.person.addAlternateName(self.name)

    stop  = { eventTag : stop_event,
              attrTag : stop_attribute,
              nameTag : stop_name,
              placeTag : stop_place,
              dateTag : stop_date,
              firstTag : stop_first,
              lastTag : stop_last,
              titleTag : stop_title,
              nickTag : stop_nick,
              suffixTag : stop_suffix,
              noteTag : stop_note,
              uidTag : stop_uid,
              stopTag : stop_date_stop,
              startTag : stop_date_start,
              streetTag : stop_street,
              cityTag : stop_city,
              stateTag : stop_state,
              countryTag : stop_country,
              postalTag : stop_postal,
              researchTag : stop_research,
              descriptionTag : stop_description,
              genderTag : stop_gender,
              stitleTag : stop_stitle,
              sauthorTag : stop_sauthor,
              sdateTag: stop_sdate,
              spageTag : stop_spage,
              spubinfoTag : stop_spubinfo,
              scallnoTag : stop_scallno,
              stextTag : stop_stext,
              pTag : stop_ptag,
              akaTag : stop_aka,
              scommentsTag : stop_scomments
              }
    
    start = { eventTag : start_event ,
              attrTag : start_attribute,
              bmarkTag : start_bmark,
              urlTag : start_url,
              personTag : start_person,
              addressTag : start_address,
              peopleTag : start_people,
              fatherTag : start_father,
              noteTag : start_note,
              motherTag : start_mother,
              childTag : start_child,
              familyTag : start_family,
              childofTag : start_childof,
              parentinTag : start_parentin,\
              nameTag : start_name,
              familiesTag : start_families,
              sourcesTag : start_sources,
              sourcerefTag : start_sourceref,
              sourceTag : start_source,
              photoTag : start_photo,
              akaTag : start_name,
              createdTag : start_created }

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def startElement(self,tag,attrs):

        self.active = tag
        self.data[tag] = ""
        if GrampsParser.start.has_key(tag):
            GrampsParser.start[tag](self,attrs)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def endElement(self,tag):

        if GrampsParser.stop.has_key(tag):
            if sax == 1:
                data = utf8_to_latin(self.data[tag])
            else:
                data = self.data[tag]
            GrampsParser.stop[tag](self,data)

    if sax == 1:
        def characters(self, data, offset, length):
            self.data[self.active] = self.data[self.active] + data
    else:
        def characters(self, data):
            self.data[self.active] = self.data[self.active] + data

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
