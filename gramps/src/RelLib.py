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

from Date import *
from Researcher import *

#-------------------------------------------------------------------------
#
# Photo class. Contains information about a photo stored in the database
#
#-------------------------------------------------------------------------
class Photo:
    def __init__(self):
        self.path = ""
        self.desc = ""
        self.private = 0

    def setPath(self,path):
        self.path = path

    def getPath(self):
        return self.path

    def setPrivate(self,val):
        self.private = val

    def getPrivate(self):
        return self.private

    def setDescription(self,text):
        self.desc = text

    def getDescription(self):
        return self.desc

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Attribute:
    def __init__(self):
        self.type = ""
        self.value = ""

    def setType(self,val):
        self.type = val

    def getType(self):
        return self.type

    def setValue(self,val):
        self.value = val

    def getValue(self):
        return self.value

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Address:
    def __init__(self):
        self.street = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.postal = ""
        self.start = Date()
        self.stop = Date()

    def setStartDate(self,date):
        self.start.set(date)

    def getStartDate(self):
        return self.start.getDate()

    def getStartDateObj(self):
        return self.start

    def setStopDate(self,date):
        self.stop.set(date)

    def getStopDate(self):
        return self.stop.getDate()

    def getStopDateObj(self):
        return self.stop

    def setStreet(self,val):
        self.street = val

    def getStreet(self):
        return self.street

    def setCity(self,val):
        self.city = val

    def getCity(self):
        return self.city

    def setState(self,val):
        self.state = val

    def getState(self):
        return self.state

    def setCountry(self,val):
        self.country = val

    def getCountry(self):
        return self.country

    def setPostal(self,val):
        self.postal = val

    def getPostal(self):
        return self.postal

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Name:

    def __init__(self):
        self.FirstName = ""
        self.Surname = ""
        self.Suffix = ""
        self.Title = ""
        
    def setName(self,first,last,suffix):
        self.FirstName = first
        self.Surname = last
        self.Suffix = suffix

    def setFirstName(self,name):
        self.FirstName = name

    def setSurname(self,name):
        self.Surname = name

    def setSuffix(self,name):
        self.Suffix = name

    def getFirstName(self):
        return self.FirstName

    def getSurname(self):
        return self.Surname

    def getSuffix(self):
        return self.Suffix

    def setTitle(self,title):
        self.Title = title

    def getTitle(self):
        return self.Title

    def getName(self):
        if (self.Suffix == ""):
            return "%s, %s" % (self.Surname, self.FirstName)
        else:
            return "%s, %s %s" % (self.Surname, self.FirstName, self.Suffix)

    def getRegularName(self):
        if (self.Suffix == ""):
            return "%s %s" % (self.FirstName, self.Surname)
        else:
            return "%s %s, %s" % (self.FirstName, self.Surname, self.Suffix)

    def getNote(self):
        return self.note

    def setNote(self,text):
        self.note = text

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Url:

    def __init__(self,path="",desc=""):
        self.path = path
        self.desc = desc

    def set_path(self,path):
        self.path = path

    def get_path(self):
        return self.path

    def set_description(self,description):
        self.desc = description

    def get_description(self):
        return self.desc

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Person:

    male = 1
    female = 0

    def __init__(self):
        self.id = -1
        self.PrimaryName = Name()
        self.EventList = []
        self.FamilyList = []
        self.AltFamilyList = []
        self.MainFamily = None
        self.photoList = []
        self.nickname = ""
        self.alternateNames = []
        self.gender = Person.female
        self.death = Event()
        self.birth = Event()
        self.addressList = []
        self.attributeList = []
        self.urls = []
        self.note = ""
        self.paf_uid = ""

    def setPrimaryName(self,name) :
         self.PrimaryName = name
	
    def getPrimaryName(self) :
        return self.PrimaryName

    def setPafUid(self,val) :
         self.paf_uid = val
	
    def getPafUid(self) :
        return self.paf_uid

    def getAlternateNames(self):
        return self.alternateNames

    def addAlternateName(self,name):
        self.alternateNames.append(name)

    def getUrlList(self):
        return self.urls

    def addUrl(self,url):
        self.urls.append(url)
    
    def setId(self,id) :
        self.id = id

    def getId(self) :
        return self.id

    def setNickName(self,name) :
        self.nickname = name

    def getNickName(self) :
        return self.nickname

    def setGender(self,val) :
        self.gender = val

    def getGender(self) :
        return self.gender

    def setBirth(self,event) :
        self.birth = event

    def setDeath(self,event) :
        self.death = event

    def getBirth(self) :
        return self.birth

    def getDeath(self) :
        return self.death

    def addPhoto(self,photo):
        self.photoList.append(photo)

    def getPhotoList(self):
        return self.photoList

    def addEvent(self,event) :
        self.EventList.append(event)

    def getEventList(self) :
        return self.EventList

    def addFamily(self,family) :
        self.FamilyList.append(family)

    def getFamilyList(self) :
        return self.FamilyList

    def removeFamily(self,family):
        index = 0
        for fam in self.FamilyList:
            if fam == family:
                del self.FamilyList[index]
                return
            index = index + 1

    def addAddress(self,address) :
        self.addressList.append(address)

    def removeAddress(self,address):
        index = 0
        for addr in self.addressList:
            if addr == address:
                del self.addressList[index]
                return
            index = index + 1

    def getAddressList(self) :
        return self.addressList

    def addAttribute(self,attribute) :
        self.attributeList.append(attribute)

    def removeAttribute(self,attribute):
        index = 0
        for attr in self.attributeList:
            if attr == attribute:
                del self.attributeList[index]
                return
            index = index + 1

    def getAttributeList(self) :
        return self.attributeList

    def getAltFamilyList(self) :
        return self.AltFamilyList

    def addAltFamily(self,family,type) :
        self.AltFamilyList.append((family,type))

    def removeAltFamily(self,family):
        index = 0
        for fam in self.AltFamilyList:
            if fam[0] == family:
                del self.AltFamilyList[index]
                return
            index = index + 1

    def getFamilyIndex(self,index) :
        return self.FamilyList[index]

    def setMainFamily(self,family) :
        self.MainFamily = family

    def getMainFamily(self) :
        return self.MainFamily

    def setNote(self,text):
        self.note = text

    def getNote(self):
        return self.note
	
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Event:
	
    def __init__(self):
        self.place = ""
        self.date = Date()
        self.description = ""
        self.name = ""
        self.source = None

    def set(self,name,date,place,description):
        self.name = name
        self.place = place
        self.description = description
        self.setDate(date)
        
    def compare(self,other):
        if other == None:
            return 1
        c = cmp(self.name,other.name)
        if c == 0:
            c = cmp(self.place,other.place)
            if c == 0:
                c = compare_dates(self.date,other.date)
                if c == 0:
                    return cmp(self.description,other.description)
        return c
        
    def setName(self,name) :
        self.name = name

    def getName(self) :
        return self.name

    def setSource(self,id) :
        self.source = id

    def getSource(self) :
        return self.source

    def setPlace(self,place) :
        self.place = place

    def getPlace(self) :
        return self.place 

    def setDescription(self,description) :
        self.description = description

    def getDescription(self) :
        return self.description 

    def setDate(self, date) :
       	self.date.set(date)

    def getDate(self) :
       	return self.date.getDate()

    def getDateObj(self) :
       	return self.date

    def getSaveDate(self) :
       	return self.date.getSaveDate()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Family:

    def __init__(self):
        self.Father = None
        self.Mother = None
        self.Children = []
        self.Marriage = None
        self.Divorce = None
        self.EventList = []
        self.id = -1
        self.photoList = []

    def setId(self,id) :
       	self.id = id

    def getId(self) :
       	return self.id

    def setFather(self,person):
       	self.Father = person

    def getFather(self):
       	return self.Father

    def setMother(self,person):
       	self.Mother = person

    def getMother(self):
       	return self.Mother

    def addChild(self,person):
        if person not in self.Children:
            self.Children.append(person)

    def removeChild(self,person):
       	index = 0
       	for child in self.Children:
            if child == person:
                del self.Children[index]
                return
            index = index + 1

    def getChildList(self):
        return self.Children

    def setMarriage(self,event):
        self.Marriage = event

    def getMarriage(self):
        return self.Marriage

    def setDivorce(self,event):
        self.Divorce = event

    def getDivorce(self):
        return self.Divorce

    def addEvent(self,event) :
        self.EventList.append(event)

    def getEventList(self) :
        return self.EventList

    def addPhoto(self,photo):
        self.photoList.append(photo)

    def getPhotoList(self):
        return self.photoList

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class SourceBase:
    def __init__(self):
        self.title = ""
        self.author = ""
        self.pubinfo = ""
        self.callno = ""

    def setId(self,newId):
        self.id = newId

    def getId(self):
        return self.id

    def setTitle(self,title):
        self.title = title

    def getTitle(self):
        return self.title

    def setAuthor(self,author):
        self.author = author

    def getAuthor(self):
        return self.author

    def setPubInfo(self,text):
        self.pubinfo = text

    def getPubInfo(self):
        return self.pubinfo

    def setCallNumber(self,val):
        self.callno = val

    def getCallNumber(self):
        return self.callno

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Source:
    def __init__(self):
        self.ref = None
        self.page = ""
        self.date = Date()
        self.comments = ""
        self.text = ""

    def setBase(self,ref):
        self.ref = ref

    def getBase(self):
        return self.ref
    
    def setDate(self,date):
        self.date = date

    def getDate(self):
        return self.date

    def setPage(self,page):
        self.page = page

    def getPage(self):
        return self.page

    def getDate(self):
        return self.date

    def setText(self,text):
        self.text = text

    def getText(self):
        return self.text

    def setComments(self,comments):
        self.comments = comments

    def getComments(self):
        return self.comments

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelDataBase:

    def __init__(self):
        self.new()

    def new(self):
        self.personMap = {}
        self.familyMap = {}
        self.sourceMap = {}
        self.smapIndex = 0
        self.pmapIndex = 0
        self.fmapIndex = 0
        self.default = None
        self.owner = Researcher()
        self.bookmarks = []
        self.path = ""

    def clean_bookmarks(self):
        new_bookmarks = []
        for person in self.bookmarks:
            new_bookmarks.append(person)
        self.bookmarks = new_bookmarks
            
    def setResearcher(self,owner):
        self.owner.set(owner.getName(),owner.getAddress(),owner.getCity(),\
                       owner.getState(),owner.getCountry(),\
                       owner.getPostalCode(),owner.getPhone(),owner.getEmail())

    def getResearcher(self):
        return self.owner

    def setDefaultPerson(self,person):
        self.default = person
    
    def getDefaultPerson(self):
        return self.default

    def getPersonMap(self):
        return self.personMap

    def setPersonMap(self,map):
        self.personMap = map

    def getFamilyMap(self):
        return self.familyMap

    def setFamilyMap(self,map):
        self.familyMap = map

    def getSavePath(self):
        return self.path

    def setSavePath(self,path):
        self.path = path

    def getSourceMap(self):
        return self.sourceMap

    def addPerson(self,person):
        index = self.pmapIndex
        person.setId(index)
        self.personMap[index] = person
        self.pmapIndex = self.pmapIndex + 1
        return index

    def getPersonEventTypes(self):
        map = {}
        for person in self.personMap.values():
            for event in person.getEventList():
                map[event.getName()] = 1
        return map.keys()

    def getPersonAttributeTypes(self):
        map = {}
        for person in self.personMap.values():
            for attr in person.getAttributeList():
                map[attr.getType()] = 1
        return map.keys()

    def findPerson(self,idVal,map):
        if map.has_key(idVal):
            person = self.personMap[map[idVal]]
        else:
            person = Person()
            map[idVal] = self.addPerson(person)
        return person

    def addPersonNoMap(self,person,id):
        person.setId(id)
        self.personMap[id] = person
        self.pmapIndex = max(self.pmapIndex,id)+1
        return id

    def findPersonNoMap(self,idVal):
        val = int(idVal)
        if self.personMap.has_key(val):
            person = self.personMap[val]
        else:
            person = Person()
            self.addPersonNoMap(person,val)
        return person

    def getNextPersonId(self):
        return self.pmapIndex

    def getNextFamilyId(self):
        return self.fmapIndex

    def getNextSourceId(self):
        return self.smapIndex

    def addSource(self,source):
        index = self.smapIndex
        source.setId(index)
        self.sourceMap[index] = source
        self.smapIndex = self.smapIndex + 1
        return index

    def findSource(self,idVal,map):
        if map.has_key(idVal):
            source = self.sourceMap[map[idVal]]
        else:
            source = SourceBase()
            map[idVal] = self.addSource(source)
        return source

    def addSourceNoMap(self,source,index):
        source.setId(index)
        self.sourceMap[index] = source
        self.smapIndex = max(self.smapIndex,index) + 1
        return index

    def findSourceNoMap(self,idVal):
        val = int(idVal)
        if self.sourceMap.has_key(val):
            source = self.sourceMap[val]
        else:
            source = SourceBase()
            self.addSourceNoMap(source,val)
        return source

    def newFamily(self):
        id = self.fmapIndex
        self.fmapIndex = self.fmapIndex + 1
        family = Family()
        family.setId(id)
        self.familyMap[id] = family
        return family

    def newFamilyNoMap(self,id):
        self.fmapIndex = max(self.fmapIndex,id) + 1
        family = Family()
        family.setId(id)
        self.familyMap[id] = family
        return family

    def findFamily(self,idVal,map):
        if map.has_key(idVal):
            family = self.familyMap[map[idVal]]
        else:
            family = self.newFamily()
            map[idVal] = family.getId()
        return family

    def findFamilyNoMap(self,idVal):
        val = int(idVal)
        if self.familyMap.has_key(val):
            family = self.familyMap[val]
        else:
            family = self.newFamilyNoMap(val)
        return family

    def deleteFamily(self,family):
        if self.familyMap.has_key(family.getId()):
            del self.familyMap[family.getId()]

        
