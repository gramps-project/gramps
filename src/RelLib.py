#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"""The core library of the GRAMPS database"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from re import compile
import os

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Date import Date, SingleDate, compare_dates, not_too_old
import GrampsCfg
import sort
import const

#-------------------------------------------------------------------------
#
# Confidence levels
#
#-------------------------------------------------------------------------

CONF_VERY_HIGH = 4
CONF_HIGH      = 3
CONF_NORMAL    = 2
CONF_LOW       = 1
CONF_VERY_LOW  = 0

#-------------------------------------------------------------------------
#
# ID regular expression
#
#-------------------------------------------------------------------------
_id_reg = compile("%\d+d")


class SourceNote:
    """Base class for storing source references and notes"""
    
    def __init__(self,source=None):
        """Create a new SourceNote, copying from source if not None"""
        
        self.source_list = []

        if source:
            if len(source.source_list) > 0:
                for sref in source.source_list:
                    self.source_list.append(SourceRef(sref))
            if source.note:
                self.note = Note(source.note.get())
            else:
                self.note = None
        else:
            self.note = None

    def addSourceRef(self,id) :
        """Set the source reference"""
        self.source_list.append(id)

    def getSourceRefList(self) :
        """Return the source reference"""
        return self.source_list

    def setSourceRefList(self,list) :
        """Replaces the source reference"""
        self.source_list = list

    def setNote(self,text):
        """Set the note to the given text"""
        if self.note == None:
            self.note = Note()
        self.note.set(text)

    def getNote(self):
        """Return the current note"""
        if self.note == None:
            return ""
        else:
            return self.note.get() 

    def setNoteFormat(self,val):
        """Set the note's format to the given value"""
        if self.note:
            self.note.setFormat(val)

    def getNoteFormat(self):
        """Return the current note's format"""
        if self.note == None:
            return 0
        else:
            return self.note.getFormat()

    def setNoteObj(self,obj):
        """Change the note object instance to obj"""
        self.note = obj

    def getNoteObj(self):
        """Return in note instance, not just the text"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

class LdsOrd(SourceNote):
    """LDS Ordinance support"""
    def __init__(self,source=None):
        """Creates a LDS Ordinance instance"""
        SourceNote.__init__(self,source)
        if source:
            self.famc = source.famc
            self.date = Date(source.date)
            self.temple = source.temple
            self.status = source.status
            self.place = source.place
        else:
            self.famc = None
            self.date = None
            self.temple = ""
            self.status = 0
            self.place = None

    def getPlaceName(self):
        """returns the title of the Place associated with the Ordinance"""
        if self.place:
            return self.place.get_title()
        else:
            return ""

    def setPlace(self,place):
        """sets the Place instance of the Event"""
        self.place = place

    def getPlace(self):
        """returns the Place instance of the Event"""
        return self.place 

    def setFamily(self,family):
        """Sets the family associated with the LDS ordinance"""
        self.famc = family

    def getFamily(self):
        """Gets the family associated with the LDS ordinance"""
        return self.famc

    def setStatus(self,val):
        """Sets the status of the LDS ordinance"""
        self.status = val

    def getStatus(self):
        """Gets the status of the LDS ordinance"""
        return self.status

    def setDate(self, date) :
        """attempts to sets the date of the LdsOrd instance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def getDate(self) :
        """returns a string representation of the date of the LdsOrd instance"""
        if self.date:
            return self.date.getDate()
        return ""

    def getDateObj(self):
        """returns the Date object associated with the LdsOrd"""
        if not self.date:
            self.date = Date()
       	return self.date

    def setDateObj(self,date):
        """sets the Date object associated with the LdsOrd"""
        self.date = date

    def setTemple(self,temple):
        """Sets the temple assocated with the LDS ordinance"""
        self.temple = temple

    def getTemple(self):
        """Gets the temple assocated with the LDS ordinance"""
        return self.temple

    def isEmpty(self):
        """Returns 1 if the LDS ordidance is actually empty"""
        if (self.famc or 
                (self.date and not self.date.isEmpty()) or 
                self.temple or 
                self.status or 
                self.place):
            return 0
        else:
            return 1
        
    def are_equal(self,other):
        """returns 1 if the specified ordinance is the same as the instance"""
        if other == None:
            if self.isEmpty():
                return 1
            else:
                return 0
        if (self.famc != other.famc or
            self.place != other.place or
            self.status != other.status or
            self.temple != other.temple or
            compare_dates(self.getDateObj(),other.getDateObj()) or
            len(self.getSourceRefList()) != len(other.getSourceRefList())):
            return 0

        index = 0
        olist = other.getSourceRefList()
        for a in self.getSourceRefList():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1
        return 1

class DataObj(SourceNote):
    """Base class for data elements, providing source, note, and privacy data"""

    def __init__(self,source=None):
        """Create a new DataObj, copying data from a source object if provided"""
        SourceNote.__init__(self,source)
        
        if source:
            self.private = source.private
        else:
            self.private = 0

    def setPrivacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def getPrivacy(self):
        """Returns the privacy level of the data"""
        return self.private

class Place(SourceNote):
    """Contains information related to a place, including multiple address
    information (since place names can change with time), longitude, latitude,
    a collection of images and URLs, a note and a source"""
    
    def __init__(self,source=None):
        """Creates a new Place object.

        source - Object to copy. If none supplied, create an empty place object"""
        
        SourceNote.__init__(self,source)
        if source:
            self.long = source.log
            self.lat = source.lat
            self.title = source.title
            self.main_loc = Location(source.main_loc)
            self.alt_loc = []
            for loc in source.alt_loc:
                self.alt_loc = Location(loc)
            self.id = source.id
            self.urls = []
            for u in source.urls:
                self.urls.append(Url(u))
            self.photoList = []
            for photo in source.photoList:
                self.photoList.append(ObjectRef(photo))
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.main_loc = None
            self.alt_loc = []
            self.id = ""
            self.urls = []
            self.photoList = []
            
    def getUrlList(self):
        """Return the list of URLs"""
        return self.urls

    def setUrlList(self,list):
        """Replace the current URL list with the new one"""
        self.urls = list

    def addUrl(self,url):
        """Add a URL to the URL list"""
        self.urls.append(url)
    
    def setId(self,id):
        """Sets the gramps ID for the place object"""
        self.id = id

    def getId(self):
        """Returns the gramps ID for the place object"""
        return self.id
    
    def set_title(self,name):
        """Sets the title of the place object"""
        self.title = name

    def get_title(self):
        """Returns the title of the place object"""
        return self.title

    def set_longitude(self,long):
        """Sets the longitude of the place"""
        self.long = long

    def get_longitude(self):
        """Returns the longitude of the place"""
        return self.long

    def set_latitude(self,long):
        """Sets the latitude of the place"""
        self.lat = long

    def get_latitude(self):
        """Returns the latitude of the place"""
        return self.lat

    def get_main_location(self):
        """Returns the Location object representing the primary information"""
        if not self.main_loc:
            self.main_loc = Location()
        return self.main_loc

    def set_main_location(self,loc):
        """Assigns the main location to the Location object passed"""
        self.main_loc = loc

    def get_alternate_locations(self):
        """Returns a list of alternate location information objects"""
        return self.alt_loc

    def set_alternate_locations(self,list):
        """Replaces the current alternate location list with the new one"""
        self.alt_loc = list

    def add_alternate_locations(self,loc):
        """Adds a Location to the alternate location list"""
        if loc not in self.alt_loc:
            self.alt_loc.append(loc)

    def addPhoto(self,photo):
        """Adds a Photo object to the place object's image list"""
        self.photoList.append(photo)

    def getPhotoList(self):
        """Returns the list of Photo objects"""
        return self.photoList

    def setPhotoList(self,list):
        """Sets the list of Photo objects"""
        self.photoList = list

    def getDisplayInfo(self):
        """Gets the display information associated with the object. This includes
        the information that is used for display and for sorting. Returns a list
        consisting of 13 strings. These are: Place Title, Place ID, Main Location
        Parish, Main Location County, Main Location City, Main Location State/Province,
        Main Location Country, upper case Place Title, upper case Parish, upper
        case city, upper case county, upper case state, upper case country"""
        
        if self.main_loc:
            return [self.title,self.id,self.main_loc.parish,self.main_loc.city,
                    self.main_loc.county,self.main_loc.state,self.main_loc.country,
                    self.title.upper(), self.main_loc.parish.upper(),
                    self.main_loc.city.upper(), self.main_loc.county.upper(),
                    self.main_loc.state.upper(), self.main_loc.country.upper()]
        else:
            return [self.title,self.id,'','','','','',self.title.upper(), '','','','','']
        
class Researcher:
    """Contains the information about the owner of the database"""
    
    def __init__(self):
        """Initializes the Researcher object"""
        self.name = ""
        self.addr = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.postal = ""
        self.phone = ""
        self.email = ""

    def getName(self):
        """returns the database owner's name"""
        return self.name

    def getAddress(self):
        """returns the database owner's address"""
        return self.addr

    def getCity(self):
        """returns the database owner's city"""
        return self.city

    def getState(self):
        """returns the database owner's state"""
        return self.state

    def getCountry(self):
        """returns the database owner's country"""
        return self.country

    def getPostalCode(self):
        """returns the database owner's postal code"""
        return self.postal

    def getPhone(self):
        """returns the database owner's phone number"""
        return self.phone

    def getEmail(self):
        """returns the database owner's email"""
        return self.email

    def set(self,name,addr,city,state,country,postal,phone,email):
        """sets the information about the database owner"""
        if name:
            self.name = name.strip()
        if addr:
            self.addr = addr.strip()
        if city:
            self.city = city.strip()
        if state:
            self.state = state.strip()
        if country:
            self.country = country.strip()
        if postal:
            self.postal = postal.strip()
        if phone:
            self.phone = phone.strip()
        if email:
            self.email = email.strip()

class Location:
    """Provides information about a place, including city, county, state,
    and country. Multiple Location objects can represent the same place,
    since names of citys, countys, states, and even countries can change
    with time"""
    
    def __init__(self,source=None):
        """creates a Location object, copying from the source object if it exists"""
        if source:
            self.city = source.city
            self.parish = source.parish
            self.county = source.county
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
            self.city = ""
            self.parish = ""
            self.county = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.phone = ""

    def is_empty(self):
        return self.city=="" and self.county=="" and self.state=="" and self.country=="" and self.postal=="" and self.phone==""
        
    def set_city(self,data):
        """sets the city name of the Location object"""
        self.city = data

    def get_postal_code(self):
        """returns the postal code of the Location object"""
        return self.postal

    def set_postal_code(self,data):
        """sets the postal code of the Location object"""
        self.postal = data

    def get_phone(self):
        """returns the phone number of the Location object"""
        return self.phone

    def set_phone(self,data):
        """sets the phone number of the Location object"""
        self.phone = data

    def get_city(self):
        """returns the city name of the Location object"""
        return self.city

    def set_parish(self,data):
        """sets the religious parish name"""
        self.parish = data

    def get_parish(self):
        """gets the religious parish name"""
        return self.parish

    def set_county(self,data):
        """sets the county name of the Location object"""
        self.county = data

    def get_county(self):
        """returns the county name of the Location object"""
        return self.county

    def set_state(self,data):
        """sets the state name of the Location object"""
        self.state = data

    def get_state(self):
        """returns the state name of the Location object"""
        return self.state

    def set_country(self,data):
        """sets the country name of the Location object"""
        self.country = data

    def get_country(self):
        """returns the country name of the Location object"""
        return self.country

class Note:
    """Provides general text information"""
    
    def __init__(self,text = ""):
        """create a new Note object from the passed string"""
        self.text = text
        self.format = 0

    def set(self,text):
        """set the note contents to the passed string"""
        self.text = text

    def get(self):
        """return the note contents"""
        return self.text

    def append(self,text):
        """adds the text to the note's contents"""
        self.text = self.text + text

    def setFormat(self,format):
        """set the format to the passed value"""
        self.format = format

    def getFormat(self):
        """return the note's format"""
        return self.format

class Photo(SourceNote):
    """Containter for information about an image file, including location,
    description and privacy"""
    
    def __init__(self,source=None):
        """Create a new Photo object, copying from the source if provided"""

        SourceNote.__init__(self,source)

        self.attrlist = []
        if source:
            self.path = source.path
            self.mime = source.mime
            self.local = source.local
            self.desc = source.desc
            self.id = source.id
            for attr in source.attrlist:
                self.attrlist.append(Attribute(attr))
        else:
            self.id = ""
            self.local = 0
            self.path = ""
            self.mime = ""
            self.desc = ""

    def setLocal(self,val):
        """set or clear the local flag"""
        self.local = val

    def getLocal(self):
        """return the local flag"""
        return self.local

    def setId(self,id):
        """Sets the gramps ID for the place object"""
        self.id = id

    def getId(self):
        """Returns the gramps ID for the place object"""
        return self.id

    def setMimeType(self,type):
        self.mime = type

    def getMimeType(self):
        return self.mime
    
    def setPath(self,path):
        """set the file path to the passed path"""
        self.path = os.path.normpath(path)

    def getPath(self):
        """return the file path"""
        return self.path

    def setDescription(self,text):
        """sets the description of the image"""
        self.desc = text

    def getDescription(self):
        """returns the description of the image"""
        return self.desc

    def addAttribute(self,attr):
        """Adds a propery to the Photo object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def getAttributeList(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def setAttributeList(self,list):
        self.attrlist = list


class ObjectRef:
    """Object reference class"""
    def __init__(self,source=None):
        self.attrlist = []
        if source:
            self.private = source.private
            self.ref = source.ref
            self.note = Note(source.note)
            for attr in source.attrlist:
                self.attrlist.append(Attribute(attr))
        else:
            self.private = 0
            self.ref = None
            self.note = None

    def setPrivacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def getPrivacy(self):
        """Returns the privacy level of the data"""
        return self.private

    def setReference(self,obj):
        self.ref = obj

    def getReference(self):
        return self.ref

    def setNote(self,text):
        """Set the note to the given text"""
        if self.note == None:
            self.note = Note()
        self.note.set(text)

    def getNote(self):
        """Return the current note"""
        if self.note == None:
            return ""
        else:
            return self.note.get() 

    def setNoteFormat(self,val):
        """Set the note's format to the given value"""
        if self.note:
            self.note.setFormat(val)

    def getNoteFormat(self):
        """Return the current note's format"""
        if self.note == None:
            return 0
        else:
            return self.note.getFormat()

    def setNoteObj(self,obj):
        """Change the note object instance to obj"""
        self.note = obj

    def getNoteObj(self):
        """Return in note instance, not just the text"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())
    
    def addAttribute(self,attr):
        """Adds a propery to the Photo object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def getAttributeList(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def setAttributeList(self,list):
        """sets the property list associated with the image"""
        self.attrlist = list

class Attribute(DataObj):
    """Provides a simple key/value pair for describing properties. Used
    by the Person and Family objects to store descriptive information."""
    
    def __init__(self,source=None):
        """creates a new Attribute object, copying from the source if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.type = source.type
            self.value = source.value
        else:
            self.type = ""
            self.value = ""

    def setType(self,val):
        """sets the type (or key) of the Attribute instance"""
        self.type = val

    def getType(self):
        """returns the type (or key) or the Attribute instance"""
        return self.type

    def setValue(self,val):
        """sets the value of the Attribute instance"""
        self.value = val

    def getValue(self):
        """returns the value of the Attribute instance"""
        return self.value


class Address(DataObj):
    """Provides address information for a person"""

    def __init__(self,source=None):
        """Creates a new Address instance, copying from the source
        if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.street = source.street
            self.city = source.city
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.date = Date(source.date)
            self.phone = source.phone
        else:
            self.street = ""
            self.city = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.date = Date()
            self.phone = ""

    def setDate(self,text):
        """attempts to sets the date that the person lived at the address
        from the passed string"""
        self.date.set(text)

    def getDate(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.getDate()

    def getPrefDate(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.getPrefDate()

    def getDateObj(self):
        """returns the Date object associated with the Address"""
        return self.date

    def setDateObj(self,obj):
        """sets the Date object associated with the Address"""
        self.date = obj

    def setStreet(self,val):
        """sets the street portion of the Address"""
        self.street = val

    def getStreet(self):
        """returns the street portion of the Address"""
        return self.street

    def setPhone(self,val):
        """sets the phone number portion of the Address"""
        self.phone = val

    def getPhone(self):
        """returns the phone number portion of the Address"""
        return self.phone

    def setCity(self,val):
        """sets the city portion of the Address"""
        self.city = val

    def getCity(self):
        """returns the city portion of the Address"""
        return self.city

    def setState(self,val):
        """sets the state portion of the Address"""
        self.state = val

    def getState(self):
        """returns the state portion of the Address"""
        return self.state

    def setCountry(self,val):
        """sets the country portion of the Address"""
        self.country = val

    def getCountry(self):
        """returns the country portion of the Address"""
        return self.country

    def setPostal(self,val):
        """sets the postal code of the Address"""
        self.postal = val

    def getPostal(self):
        """returns the postal code of the Address"""
        return self.postal

class Name(DataObj):
    """Provides name information about a person. A person may have more
    that one name throughout his or her life."""
    
    def __init__(self,source=None):
        """creates a new Name instance, copying from the source if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.FirstName = source.FirstName
            self.Surname = source.Surname
            self.Suffix = source.Suffix
            self.Title = source.Title
            self.type = source.type
            self.Prefix = source.Prefix
            self.sname = source.sname
        else:
            self.FirstName = ""
            self.Surname = ""
            self.Suffix = ""
            self.Title = ""
            self.type = "Birth Name"
            self.Prefix = ""
            self.sname = '@'

    def getSurnamePrefix(self):
        return self.Prefix

    def setSurnamePrefix(self,val):
        self.Prefix = val

    def setType(self,type):
        """sets the type of the Name instance"""
        self.type = type

    def getType(self):
        """returns the type of the Name instance"""
        return self.type

    def build_sort_name(self):
        if self.Surname:
            self.sname = "%-25s%-30s%s" % (self.Surname.upper(),self.FirstName.upper(),self.Suffix.upper())
        else:
            self.sname = "@"

    def setFirstName(self,name):
        """sets the given name for the Name instance"""
        self.FirstName = name
        self.build_sort_name()

    def setSurname(self,name):
        """sets the surname (or last name) for the Name instance"""
        self.Surname = name
        self.build_sort_name()

    def setSuffix(self,name):
        """sets the suffix (such as Jr., III, etc.) for the Name instance"""
        self.Suffix = name
        self.build_sort_name()

    def getSortName(self):
        return self.sname
    
    def getFirstName(self):
        """returns the given name for the Name instance"""
        return self.FirstName

    def getSurname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.Surname

    def getUpperSurname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.Surname.upper()

    def getSuffix(self):
        """returns the suffix for the Name instance"""
        return self.Suffix

    def setTitle(self,title):
        """sets the title (Dr., Reverand, Captain) for the Name instance"""
        self.Title = title

    def getTitle(self):
        """returns the title for the Name instance"""
        return self.Title

    def getName(self):
        """returns a name string built from the components of the Name
        instance, in the form of Surname, Firstname"""
        
        if self.Suffix:
            if self.Prefix:
                return "%s %s, %s %s" % (self.Prefix, self.Surname, self.FirstName, self.Suffix)
            else:
                return "%s, %s %s" % (self.Surname, self.FirstName, self.Suffix)
        else:
            if self.Prefix:
                return "%s %s, %s" % (self.Prefix,self.Surname, self.FirstName)
            else:
                return "%s, %s" % (self.Surname, self.FirstName)

    def getUpperName(self):
        """returns a name string built from the components of the Name
        instance, in the form of Surname, Firstname"""
        
        if self.Suffix:
            if self.Prefix:
                return "%s %s, %s %s" % (self.Prefix.upper(), self.Surname.upper(), self.FirstName, self.Suffix)
            else:
                return "%s, %s %s" % (self.Surname.upper(), self.FirstName, self.Suffix)
        else:
            if self.Prefix:
                return "%s %s, %s" % (self.Prefix.upper(), self.Surname.upper(), self.FirstName)
            else:
                return "%s, %s" % (self.Surname.upper(), self.FirstName)

    def getRegularName(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname Surname"""
        if (self.Suffix == ""):
            if self.Prefix:
                return "%s %s %s" % (self.FirstName, self.Prefix, self.Surname)
            else:
                return "%s %s" % (self.FirstName, self.Surname)
        else:
            if self.Prefix:
                return "%s %s %s, %s" % (self.FirstName, self.Prefix, self.Surname, self.Suffix)
            else:
                return "%s %s, %s" % (self.FirstName, self.Surname, self.Suffix)

    def getRegularUpperName(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname Surname"""
        if (self.Suffix == ""):
            if self.Prefix:
                return "%s %s %s" % (self.FirstName, self.Prefix.upper(), self.Surname.upper())
            else:
                return "%s %s" % (self.FirstName, self.Surname.upper())
        else:
            if self.Prefix:
                return "%s %s %s, %s" % (self.FirstName, self.Prefix.upper(), self.Surname.upper(), self.Suffix)
            else:
                return "%s %s, %s" % (self.FirstName, self.Surname.upper(), self.Suffix)

    def are_equal(self,other):
        """compares to names to see if they are equal, return 0 if they
        are not"""
        if self.FirstName != other.FirstName:
            return 0
        if self.Surname != other.Surname:
            return 0
        if self.Prefix != other.Prefix:
            return 0
        if self.Suffix != other.Suffix:
            return 0
        if self.Title != other.Title:
            return 0
        if self.type != other.type:
            return 0
        if self.private != other.private:
            return 0
        if self.getNote() != other.getNote():
            return 0
        if len(self.getSourceRefList()) != len(other.getSourceRefList()):
            return 0
        index = 0
        olist = other.getSourceRefList()
        for a in self.getSourceRefList():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1
        return 1

class Url:
    """Contains information related to internet Uniform Resource Locators,
    allowing gramps to store information about internet resources"""

    def __init__(self,source=None):
        """creates a new URL instance, copying from the source if present"""
        if source:
            self.path = source.path
            self.desc = source.desc
            self.private = source.private
        else:
            self.path = ""
            self.desc = ""
            self.private = 0

    def setPrivacy(self,val):
        """sets the privacy flag for the URL instance"""
        self.private = val

    def getPrivacy(self):
        """returns the privacy flag for the URL instance"""
        return self.private

    def set_path(self,path):
        """sets the URL path"""
        self.path = path

    def get_path(self):
        """returns the URL path"""
        return self.path

    def set_description(self,description):
        """sets the description of the URL"""
        self.desc = description

    def get_description(self):
        """returns the description of the URL"""
        return self.desc

    def are_equal(self,other):
        """returns 1 if the specified URL is the same as the instance"""
        if other == None:
            return 0
        if self.path != other.path:
            return 0
        if self.desc != other.desc:
            return 0
        return 1


class Person(SourceNote):
    """Represents an individual person in the gramps database"""
    
    unknown = 2
    male = 1
    female = 0

    def __init__(self,id=""):
        """creates a new Person instance"""
        SourceNote.__init__(self)
        self.id = id
        self.PrimaryName = None
        self.EventList = []
        self.FamilyList = []
        self.AltFamilyList = []
        self.photoList = []
        self.nickname = ""
        self.alternateNames = []
        self.gender = 2
        self.death = None
        self.birth = None
        self.addressList = []
        self.attributeList = []
        self.urls = []
        self.paf_uid = ""
        self.position = None
        self.ancestor = None
        self.lds_bapt = None
        self.lds_endow = None
        self.lds_seal = None
        self.complete = 0

        # We hold a reference to the GrampsDB so that we can maintain
        # its genderStats.  It doesn't get set here, but from
        # GenderStats.count_person.
        self.db = None

    def setComplete(self,val):
        self.complete = val

    def getComplete(self):
        return self.complete

    def getDisplayInfo(self):
        if self.gender == Person.male:
            gender = const.male
        elif self.gender == Person.female:
            gender = const.female
        else:
            gender = const.unknown
        bday = self.getBirth().getDateObj()
        dday = self.getDeath().getDateObj()
        return [ GrampsCfg.display_name(self),self.id,gender,
                 bday.getQuoteDate(), dday.getQuoteDate(),
                 self.getPrimaryName().getSortName(),
                 sort.build_sort_date(bday),sort.build_sort_date(dday),
                 GrampsCfg.display_surname(self.PrimaryName)]
                                          
    def setPrimaryName(self,name):
        """sets the primary name of the Person to the specified
        Name instance"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)

        self.PrimaryName = name
	
        if db:
            db.genderStats.count_person (self, db)

    def getPrimaryName(self):
        """returns the Name instance marked as the Person's primary name"""
        if not self.PrimaryName:
            self.PrimaryName = Name()
        return self.PrimaryName

    def setPafUid(self,val):
        """sets Personal Ancestral File UID value"""
        self.paf_uid = val
	
    def getPafUid(self) :
        """returns the Personal Ancestral File UID value"""
        return self.paf_uid

    def getAlternateNames(self):
        """returns the list of alternate Names"""
        return self.alternateNames

    def setAlternateNames(self,list):
        """changes the list of alternate names to the passed list"""
        self.alternateNames = list

    def addAlternateName(self,name):
        """adds an alternate Name instance to the list"""
        self.alternateNames.append(name)

    def getUrlList(self):
        """returns the list of URL instances"""
        return self.urls

    def setUrlList(self,list):
        """sets the list of URL instances to list"""
        self.urls = list

    def addUrl(self,url):
        """adds a URL instance to the list"""
        self.urls.append(url)
    
    def setId(self,id):
        """sets the gramps ID for the Person"""
        self.id = str(id)

    def getId(self):
        """returns the gramps ID for the Person"""
        return self.id

    def setNickName(self,name):
        """sets the nickname for the Person"""
        self.nickname = name

    def getNickName(self) :
        """returns the nickname for the Person"""
        return self.nickname

    def setGender(self,val) :
        """sets the gender of the Person"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)

        self.gender = val

        if db:
            db.genderStats.count_person (self, db)

    def getGender(self) :
        """returns the gender of the Person"""
        return self.gender

    def setBirth(self,event) :
        """sets the birth event to the passed event"""
        self.birth = event

    def setDeath(self,event) :
        """sets the death event to the passed event"""
        self.death = event

    def getBirth(self) :
        """returns the birth event"""
        if self.birth == None:
            self.birth = Event()
            self.birth.name = "Birth"
        return self.birth

    def getDeath(self) :
        """returns the death event"""
        if self.death == None:
            self.death = Event()
            self.death.name = "Death"
        return self.death

    def getValidDeath(self):
        e = self.death
        if e == None:
            return None
        if e.place == None and (e.date == None or not e.date.getValid()) and \
           e.description == "" and e.cause == "" and e.witness == None:
            return None
        else:
            return e

    def getValidBirth(self):
        e = self.birth
        if e == None:
            return None
        if e.place == None and (e.date == None or not e.date.getValid()) and \
           e.description == "" and e.cause == "" and e.witness == None:
            return None
        else:
            return e

    def addPhoto(self,photo):
        """adds a Photo instance to the image list"""
        self.photoList.append(photo)

    def getPhotoList(self):
        """returns the list of Photos"""
        return self.photoList

    def setPhotoList(self,list):
        """Sets the list of Photo objects"""
        self.photoList = list

    def addEvent(self,event):
        """adds an Event to the event list"""
        self.EventList.append(event)

    def getEventList(self):
        """returns the list of Event instances"""
        return self.EventList

    def setEventList(self,list):
        """sets the event list to the passed list"""
        self.EventList = list

    def addFamily(self,family):
        """adds the specified Family instance to the list of
        families/marriages/partnerships in which the person is a
        parent or spouse"""
        self.FamilyList.append(family)

    def setPreferred(self,family):
        if family in self.FamilyList:
            self.FamilyList.remove(family)
            self.FamilyList = [family] + self.FamilyList

    def getFamilyList(self) :
        """returns the list of Family instances in which the
        person is a parent or spouse"""
        return self.FamilyList

    def clearFamilyList(self) :
        self.FamilyList = []

    def removeFamily(self,family):
        """removes the specified Family instance from the list
        of marriages/partnerships"""
        if family in self.FamilyList:
            self.FamilyList.remove(family)

    def addAddress(self,address):
        """adds the Address instance to the list of addresses"""
        self.addressList.append(address)

    def removeAddress(self,address):
        """removes the Address instance from the list of addresses"""
        if address in self.addressList:
            self.addressList.remove(address)

    def getAddressList(self):
        """returns the list of addresses"""
        return self.addressList

    def setAddressList(self,list):
        """sets the address list to the specified list"""
        self.addressList = list

    def addAttribute(self,attribute):
        """adds an Attribute instance to the attribute list"""
        self.attributeList.append(attribute)

    def removeAttribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attributeList:
            self.attributeList.remove(attribute)

    def getAttributeList(self):
        """returns the attribute list"""
        return self.attributeList

    def setAttributeList(self,list):
        """sets the attribute list to the specified list"""
        self.attributeList = list

    def getParentList(self):
        """returns the list of alternate Family instances, in which the Person
        is a child of the family, but not a natural child of both parents"""
        return self.AltFamilyList

    def addAltFamily(self,family,mrel,frel):
        """adds a Family to the alternate family list, indicating the
        relationship to the mother (mrel) and the father (frel)"""
        self.AltFamilyList.append((family,mrel,frel))

    def clearAltFamilyList(self):
        self.AltFamilyList = []

    def removeAltFamily(self,family):
        """removes a Family instance from the alternate family list"""
        for f in self.AltFamilyList[:]:
            if f[0] == family:
                self.AltFamilyList.remove(f)
                return f
        else:
            return None

    def changeAltFamily(self,family,mrel,frel):
        """removes a Family instance from the alternate family list"""
        index = 0
        for f in self.AltFamilyList[:]:
            if f[0] == family:
                self.AltFamilyList[index] = (family,mrel,frel)
            index += 1

    def has_family(self,family):
        for f in self.AltFamilyList:
            if f[0] == family:
                return f
        else:
            return None

    def setMainParents(self,family):
        """sets the main Family of the Person, the Family in which the
        Person is a natural born child"""
        f = self.removeAltFamily(family)
        if f:
            self.AltFamilyList = [f] + self.AltFamilyList
        
    def getMainParents(self):
        """returns the main Family of the Person, the Family in which the
        Person is a natural born child"""
        if len(self.AltFamilyList) == 0:
            return None
        else:
            return self.AltFamilyList[0][0]

    def getMainParentsRel(self):
        """returns the main Family of the Person, the Family in which the
        Person is a natural born child"""
        if len(self.AltFamilyList) == 0:
            return (None,None,None)
        else:
            return self.AltFamilyList[0]

    def setPosition(self,pos):
        """sets a graphical location pointer for graphic display (x,y)"""
        self.position = pos

    def getPosition(self):
        """returns a graphical location pointer for graphic display (x,y)"""
        return self.position

    def setAncestor(self, value):
        """set ancestor flag and recurse"""
        self.ancestor = value
        for (family,m,f) in self.AltFamilyList:
            if family.Father:
                # Don't waste time if the ancestor is already flagged.
                # This will happen when cousins marry.
                if not family.Father.getAncestor():
                    family.Father.setAncestor(value)
            if family.getMother():
                if not family.Mother.getAncestor():
                    family.Mother.setAncestor(value)

    def getAncestor(self):
        return self.ancestor

    def setLdsBaptism(self,ord):
        self.lds_bapt = ord

    def getLdsBaptism(self):
        return self.lds_bapt

    def setLdsEndowment(self,ord):
        self.lds_endow = ord

    def getLdsEndowment(self):
        return self.lds_endow

    def setLdsSeal(self,ord):
        self.lds_seal = ord

    def getLdsSeal(self):
        return self.lds_seal

    def probablyAlive(self):
        """Returns true if the person may be alive."""
        if not self.death.is_empty ():
            return 0
        if self.birth.getDate() != "":
            return not_too_old(self.birth.getDateObj().get_start_date())

        # Neither birth nor death events are available.  Try looking
        # for descendants that were born more than a lifespan ago.

        min_generation = 13
        max_generation = 60
        max_age_difference = 60
        def descendants_too_old (person, years):
            for family in person.getFamilyList ():
                for child in family.getChildList ():
                    if child.birth.getDate () != "":
                        d = SingleDate (child.birth.getDateObj ().
                                        get_start_date ())
                        d.setYear (d.getYear () - years)
                        if not not_too_old (d):
                            return 1

                    if child.death.getDate () != "":
                        d = SingleDate (child.death.getDateObj ().
                                        get_start_date ())
                        if not not_too_old (d):
                            return 1

                    if descendants_too_old (child, years + min_generation):
                        return 1

        if descendants_too_old (self, min_generation):
            return 0

        # What about their parents?
        def parents_too_old (person, age_difference):
            family = person.getMainParents ()
            if family:
                for parent in [family.getFather (), family.getMother ()]:
                    if not parent:
                        continue

                    if parent.birth.getDate () != "":
                        d = SingleDate (parent.birth.getDateObj ().
                                        get_start_date ())
                        d.setYear (d.getYear () + max_generation +
                                   age_difference)
                        if not not_too_old (d):
                            return 1

                    if parent.death.getDate () != "":
                        d = SingleDate (parent.death.getDateObj ().
                                        get_start_date ())
                        d.setYear (d.getYear () + age_difference)
                        if not not_too_old (d):
                            return 1

        if parents_too_old (self, 0):
            return 0

        # As a last resort, trying seeing if their spouse's age gives
        # any clue.
        for family in self.getFamilyList ():
            for spouse in [family.getFather (), family.getMother ()]:
                if not spouse:
                    continue
                if spouse == self:
                    continue
                if spouse.birth.getDate () != "":
                    d = SingleDate (spouse.birth.getDateObj().
                                    get_start_date ())
                    d.setYear (d.getYear () + max_age_difference)
                    if not not_too_old (d):
                        return 0

                if spouse.death.getDate () != "":
                    d = SingleDate (spouse.birth.getDateObj().
                                    get_start_date ())
                    d.setYear (d.getYear () - min_generation)
                    if not not_too_old (d):
                        return 0

                if parents_too_old (spouse, max_age_difference):
                    return 0

        return 1
    
class Event(DataObj):
    """Event record, recording the event type, description, place, and date
    of a particular event"""

    NAME = 0
    ID = 1
    
    def __init__(self,source=None):
        """creates a new Event instance, copying from the source if present"""
        
        DataObj.__init__(self,source)
        
        if source:
            self.place = source.place
            self.date = Date(source.date)
            self.description = source.description
            self.name = source.name
            self.cause = source.cause
            try:
                if source.witness:
                    self.witness = source.witness[:]
                else:
                    self.witness = None
            except:
                self.witness = None
        else:
            self.place = None
            self.date = None
            self.description = ""
            self.name = ""
            self.cause = ""
            self.witness = None

    def get_witness_list(self):
        return self.witness

    def set_witness_list(self,list):
        if list:
            self.witness = list[:]
        else:
            self.witness = None

    def add_witness(self,value):
        if self.witness:
            self.witness.append(value)
        else:
            self.witness = [value]
        
    def is_empty(self):
        date = self.getDateObj()
        place = self.getPlace()
        description = self.description
        cause = self.cause
        name = self.name
        if (not name or name == "Birth" or name == "Death") and \
           date.isEmpty() and not place and not description and not cause:
            return 1
        else:
            return 0

    def set(self,name,date,place,description):
        """sets the name, date, place, and description of an Event instance"""
        self.name = name
        self.place = place
        self.description = description
        self.setDate(date)
        
    def are_equal(self,other):
        """returns 1 if the specified event is the same as the instance"""
        if other == None:
            return 0
        if (self.name != other.name or self.place != other.place or
            self.description != other.description or self.cause != other.cause or
            self.private != other.private or
            compare_dates(self.getDateObj(),other.getDateObj()) or
            len(self.getSourceRefList()) != len(other.getSourceRefList())):
            return 0

        index = 0
        olist = other.getSourceRefList()
        for a in self.getSourceRefList():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1

        return 1
        
    def setName(self,name):
        """sets the name of the Event"""
        self.name = name

    def getName(self):
        """returns the name of the Event"""
        return self.name

    def setPlace(self,place):
        """sets the Place instance of the Event"""
        self.place = place

    def getPlace(self):
        """returns the Place instance of the Event"""
        return self.place 

    def setCause(self,cause):
        """sets the cause of the Event"""
        self.cause = cause

    def getCause(self):
        """returns the cause of the Event"""
        return self.cause 

    def getPlaceName(self):
        """returns the title of the Place associated with the Event"""
        if self.place:
            return self.place.get_title()
        else:
            return ""

    def setDescription(self,description):
        """sets the description of the Event instance"""
        self.description = description

    def getDescription(self) :
        """returns the description of the Event instance"""
        return self.description 

    def setDate(self, date) :
        """attempts to sets the date of the Event instance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def getDate(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.getDate()
        return ""

    def getPrefDate(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.getDate()
        return ""

    def getQuoteDate(self) :
        """returns a string representation of the date of the Event instance,
        enclosing the results in quotes if it is not a valid date"""
        if self.date:
            return self.date.getQuoteDate()
        return ""

    def getDateObj(self):
        """returns the Date object associated with the Event"""
        if not self.date:
            self.date = Date()
       	return self.date

    def setDateObj(self,date):
        """sets the Date object associated with the Event"""
        self.date = date

class Witness:
    def __init__(self,type=Event.NAME,val="",comment=""):
        self.set_type(type)
        self.set_value(val)
        self.set_comment(comment)

    def set_type(self,type):
        self.type = type

    def get_type(self):
        return self.type

    def set_value(self,val):
        self.val = val

    def get_value(self):
        return self.val

    def set_comment(self,comment):
        self.comment = comment

    def get_comment(self):
        return self.comment

class Family(SourceNote):
    """Represents a family unit in the gramps database"""

    def __init__(self):
        """creates a new Family instance"""
        SourceNote.__init__(self)
        self.Father = None
        self.Mother = None
        self.Children = []
        self.Marriage = None
        self.Divorce = None
        self.type = "Married"
        self.EventList = []
        self.id = ""
        self.photoList = []
        self.attributeList = []
        self.position = None
        self.lds_seal = None
        self.complete = 0

    def setComplete(self,val):
        self.complete = val

    def getComplete(self):
        return self.complete

    def setLdsSeal(self,ord):
        self.lds_seal = ord

    def getLdsSeal(self):
        return self.lds_seal

    def setPosition(self,pos):
        """sets a graphical location pointer for graphic display (x,y)"""
        self.position = pos

    def getPosition(self):
        """returns a graphical location pointer for graphic display (x,y)"""
        return self.position

    def addAttribute(self,attribute) :
        """adds an Attribute instance to the attribute list"""
        self.attributeList.append(attribute)

    def removeAttribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attributeList:
            self.attributeList.remove(attribute)

    def getAttributeList(self) :
        """returns the attribute list"""
        return self.attributeList

    def setAttributeList(self,list) :
        """sets the attribute list to the specified list"""
        self.attributeList = list

    def setId(self,id) :
        """sets the gramps ID for the Family"""
       	self.id = str(id)

    def getId(self) :
        """returns the gramps ID for the Family"""
       	return self.id

    def setRelationship(self,type):
        """assigns a string indicating the relationship between the
        father and the mother"""
        self.type = type

    def getRelationship(self):
        """returns a string indicating the relationship between the
        father and the mother"""
        return self.type
    
    def setFather(self,person):
        """sets the father of the Family to the specfied Person"""
        update = self.someChildIsAncestor()
        if update and self.Father:
            self.Father.setAncestor(0)
        self.Father = person
        if update and self.Father:
            self.Father.setAncestor(1)

    def getFather(self):
        """returns the father of the Family"""
       	return self.Father

    def setMother(self,person):
        """sets the mother of the Family to the specfied Person"""
        update = self.someChildIsAncestor()
        if self.Mother and update:
            self.Mother.setAncestor(0)
        self.Mother = person
        if update and self.Mother:
            self.Mother.setAncestor(1)

    def getMother(self):
        """returns the mother of the Family"""
       	return self.Mother

    def addChild(self,person):
        """adds the specfied Person as a child of the Family, adding it
        to the child list"""
        if person not in self.Children:
            self.Children.append(person)
        if person.getAncestor():
            if self.Father:
                self.Father.setAncestor(1)
            if self.Mother:
                self.Mother.setAncestor(1)
            
    def removeChild(self,person):
        """removes the specified Person from the child list"""
        if person in self.Children:
            self.Children.remove(person)
        if person.getAncestor():
            if self.Father:
                self.Father.setAncestor(0)
            if self.Mother:
                self.Mother.setAncestor(0)

    def getChildList(self):
        """returns the list of children"""
        return self.Children

    def setChildList(self, list):
        """sets the list of children"""
        self.Children = list[:]

    def getMarriage(self):
        """returns the marriage event of the Family. Obsolete"""
        for e in self.EventList:
            if e.getName() == "Marriage":
                return e
        return None

    def getDivorce(self):
        """returns the divorce event of the Family. Obsolete"""
        for e in self.EventList:
            if e.getName() == "Divorce":
                return e
        return None

    def addEvent(self,event):
        """adds an Event to the event list"""
        self.EventList.append(event)

    def getEventList(self) :
        """returns the list of Event instances"""
        return self.EventList

    def setEventList(self,list) :
        """sets the event list to the passed list"""
        self.EventList = list

    def addPhoto(self,photo):
        """Adds a Photo object to the Family instance's image list"""
        self.photoList.append(photo)

    def getPhotoList(self):
        """Returns the list of Photo objects"""
        return self.photoList

    def setPhotoList(self,list):
        """Sets the list of Photo objects"""
        self.photoList = list

    def someChildIsAncestor(self):
        for child in self.Children:
            if (child.getAncestor()):
                return 1
        return None

class Source:
    """A record of a source of information"""
    
    def __init__(self):
        """creates a new Source instance"""
        self.title = ""
        self.author = ""
        self.pubinfo = ""
        self.note = Note()
        self.photoList = []
        self.id = ""
        self.abbrev = ""
        
    def getDisplayInfo(self):
        return [self.title,self.id,self.author,self.title.upper(),self.author.upper()]

    def setId(self,newId):
        """sets the gramps' ID for the Source instance"""
        self.id = str(newId)

    def getId(self):
        """returns the gramps' ID of the Source instance"""
        return self.id

    def addPhoto(self,photo):
        """Adds a Photo object to the Source instance's image list"""
        self.photoList.append(photo)

    def getPhotoList(self):
        """Returns the list of Photo objects"""
        return self.photoList

    def setPhotoList(self,list):
        """Sets the list of Photo objects"""
        self.photoList = list

    def setTitle(self,title):
        """sets the title of the Source"""
        self.title = title

    def getTitle(self):
        """returns the title of the Source"""
        return self.title

    def setNote(self,text):
        """sets the text of the note attached to the Source"""
        self.note.set(text)

    def getNote(self):
        """returns the text of the note attached to the Source"""
        return self.note.get()

    def setNoteFormat(self,val):
        """Set the note's format to the given value"""
        self.note.setFormat(val)

    def getNoteFormat(self):
        """Return the current note's format"""
        return self.note.getFormat()

    def setNoteObj(self,obj):
        """sets the Note instance attached to the Source"""
        self.note = obj

    def getNoteObj(self):
        """returns the Note instance attached to the Source"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

    def setAuthor(self,author):
        """sets the author of the Source"""
        self.author = author

    def getAuthor(self):
        """returns the author of the Source"""
        return self.author

    def setPubInfo(self,text):
        """sets the publication information of the Source"""
        self.pubinfo = text

    def getPubInfo(self):
        """returns the publication information of the Source"""
        return self.pubinfo

    def setAbbrev(self,abbrev):
        """sets the title abbreviation of the Source"""
        self.abbrev = abbrev

    def getAbbrev(self):
        """returns the title abbreviation of the Source"""
        return self.abbrev

class SourceRef:
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    def __init__(self,source=None):
        """creates a new SourceRef, copying from the source if present"""
        if source:
            self.confidence = source.confidence
            self.ref = source.ref
            self.page = source.page
            self.date = Date(source.date)
            self.comments = Note(source.comments.get())
            self.text = source.text
        else:
            self.confidence = CONF_NORMAL
            self.ref = None
            self.page = ""
            self.date = Date()
            self.comments = Note()
            self.text = ""

    def setConfidence(self,val):
        """Sets the confidence level"""
        self.confidence = val

    def getConfidence(self):
        """Returns the confidence level"""
        return self.confidence
        
    def setBase(self,ref):
        """sets the Source instance to which the SourceRef refers"""
        self.ref = ref

    def getBase(self):
        """returns the Source instance to which the SourceRef refers"""
        return self.ref
    
    def setDate(self,date):
        """sets the Date instance of the SourceRef"""
        self.date = date

    def getDate(self):
        """returns the Date instance of the SourceRef"""
        return self.date

    def setPage(self,page):
        """sets the page indicator of the SourceRef"""
        self.page = page

    def getPage(self):
        """gets the page indicator of the SourceRef"""
        return self.page

    def setText(self,text):
        """sets the text related to the SourceRef"""
        self.text = text

    def getText(self):
        """returns the text related to the SourceRef"""
        return self.text

    def setNoteObj(self,note):
        """Change the Note instance to obj"""
        self.comments = note

    def setComments(self,comments):
        """sets the comments about the SourceRef"""
        self.comments.set(comments)

    def getComments(self):
        """returns the comments about the SourceRef"""
        return self.comments.get()

    def are_equal(self,other):
        """returns 1 if the passed SourceRef is equal to the current"""
        if self.ref and other.ref:
            if self.page != other.page:
                return 0
            if compare_dates(self.date,other.date) != 0:
                return 0
            if self.getText() != other.getText():
                return 0
            if self.getComments() != other.getComments():
                return 0
            if self.confidence != other.confidence:
                return 0
            return 1
        elif not self.ref and not other.ref:
            return 1
        else:
            return 0
        
    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.comments = Note(self.comments.get())

class GenderStats:
    def __init__ (self):
        self.stats = {}

    def _get_key (self, person):
        name = person.getPrimaryName ().getFirstName ()
        return self._get_key_from_name (name)

    def _get_key_from_name (self, name):
        return name.split (' ')[0].replace ('?', '')

    def name_stats (self, name):
        if self.stats.has_key (name):
            return self.stats[name]
        return (0, 0, 0)

    def count_person (self, person, db, undo = 0):
        # Let the Person do their own counting later
        person.db = db

        name = self._get_key (person)
        if not name:
            return

        gender = person.getGender ()
        (male, female, unknown) = self.name_stats (name)
        if not undo:
            increment = 1
        else:
            increment = -1

        if gender == Person.male:
            male += increment
        elif gender == Person.female:
            female += increment
        elif gender == Person.unknown:
            unknown += increment

        self.stats[name] = (male, female, unknown)
        return

    def uncount_person (self, person):
        return self.count_person (person, None, undo = 1)

    def guess_gender (self, name):
        name = self._get_key_from_name (name)
        if not name or not self.stats.has_key (name):
            return Person.unknown

        (male, female, unknown) = self.stats[name]
        if unknown == 0:
            if male and not female:
                return Person.male
            if female and not male:
                return Person.female

        if male > (2 * female):
            return Person.male

        if female > (2 * male):
            return Person.female

        return Person.unknown

class GrampsDB:
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""
        self.surnames = []
        self.personMap = {}
        self.placeTable = {}
        self.placeMap = {}
        self.sourceTable = {}
        self.sourceMap = {}
        self.familyMap = {}
        self.iprefix = "I%d"
        self.sprefix = "S%d"
        self.oprefix = "O%d"
        self.pprefix = "P%d"
        self.fprefix = "F%d"
        self.new()
        self.added_files = []
        self.genderStats = GenderStats ()

    def get_added_media_objects(self):
        return self.added_files

    def clear_added_media_objects(self):
        self.added_files = []
        
    def get_type(self):
        return 'GrampsDB'

    def close(self):
        pass
    
    def get_base(self):
        return ""

    def need_autosave(self):
        return 1

    def getPersonLength(self):
        return len(self.personMap)

    def getPersonKeys(self):
        return self.personMap.keys()

    def sortbyname(self,f,s):
        n1 = self.personMap[f].PrimaryName.sname
        n2 = self.personMap[s].PrimaryName.sname
        return cmp(n1,n2)

    def sortPersonKeys(self):
        keys = self.personMap.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyname)
        return keys

    def getPersonDisplay(self,key):
        return self.personMap[key].getDisplayInfo()

    def buildPersonDisplay(self,nkey,okey=None):
        person = self.personMap[nkey]
        self.addSurname(person.getPrimaryName().getSurname())

    def rebuildPersonTable(self):
        pass
        
    def buildPlaceDisplay(self,nkey,okey=None):
        if okey and nkey != okey:
            del self.placeTable[okey]
        self.placeTable[nkey] = self.placeMap[nkey].getDisplayInfo()
        
    def set_iprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.iprefix = val
            else:
                self.iprefix = val + "%d"
        else:
            self.iprefix = "I%d"
            
    def set_sprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.sprefix = val
            else:
                self.sprefix = val + "%d"
        else:
            self.sprefix = "S%d"
            
    def set_oprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.oprefix = val
            else:
                self.oprefix = val + "%d"
        else:
            self.oprefix = "O%d"

    def set_pprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.pprefix = val
            else:
                self.pprefix = val + "%d"
        else:
            self.pprefix = "P%d"

    def set_fprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.fprefix = val
            else:
                self.fprefix = val + "%d"
        else:
            self.fprefix = "F%d"
            
    def new(self):
        """initializes the GrampsDB to empty values"""

        # eliminate memory reference cycles for 1.5.2 garbage collection 
        for f in self.familyMap.values():
            f.Father = None
            f.Mother = None
            f.Children = []
        self.familyMap = {}

        for p in self.personMap.values():
            p.clearAltFamilyList()
            p.clearFamilyList()

        self.surnames = []
        self.personMap = {}
        self.sourceMap = {}
        self.sourceTable = {}
        self.placeMap  = {}
        self.placeTable = {}
        self.objectMap = {}
        self.smapIndex = 0
        self.pmapIndex = 0
        self.fmapIndex = 0
        self.lmapIndex = 0
        self.omapIndex = 0
        self.default = None
        self.owner = Researcher()
        self.bookmarks = []
        self.path = ""
        self.place2title = {}
        self.genderStats = GenderStats ()

    def getSurnames(self):
        return self.surnames

    def addSurname(self,name):
        if name and name not in self.surnames:
            self.surnames.append(name)
            self.surnames.sort()
    
    def getBookmarks(self):
        """returns the list of Person instances in the bookmarks"""
        return self.bookmarks

    def clean_bookmarks(self):
        """cleans up the bookmark list, removing empty slots"""
        new_bookmarks = []
        for person in self.bookmarks:
            new_bookmarks.append(person)
        self.bookmarks = new_bookmarks
            
    def setResearcher(self,owner):
        """sets the information about the owner of the database"""
        self.owner.set(owner.getName(),owner.getAddress(),owner.getCity(),\
                       owner.getState(),owner.getCountry(),\
                       owner.getPostalCode(),owner.getPhone(),owner.getEmail())

    def getResearcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.owner

    def setDefaultPerson(self,person):
        """sets the default Person to the passed instance"""
        if (self.default):
            self.default.setAncestor(0)
        self.default = person
        self.default.setAncestor(1)
    
    def getDefaultPerson(self):
        """returns the default Person of the database"""
        return self.default

    def getPerson(self,id):
        """returns a map of gramps's IDs to Person instances"""
        return self.personMap[id]

    def getPersonMap(self):
        """returns a map of gramps's IDs to Person instances"""
        return self.personMap

    def setPersonMap(self,map):
        """sets the map of gramps's IDs to Person instances"""
        # Should recalculate self.genderStats here.
        self.personMap = map

    def getPlaceMap(self):
        """returns a map of gramps's IDs to Place instances"""
        return self.placeMap

    def setPlaceMap(self,map):
        """sets the map of gramps's IDs to Place instances"""
        self.placeMap = map

    def getFamilyMap(self):
        """returns a map of gramps's IDs to Family instances"""
        return self.familyMap

    def getFamily(self,id):
        """returns a map of gramps's IDs to Family instances"""
        return self.familyMap[id]

    def setFamilyMap(self,map):
        """sets the map of gramps's IDs to Family instances"""
        self.familyMap = map

    def getSourceMap(self):
        """returns a map of gramps's IDs to Source instances"""
        return self.sourceMap

    def getObjectMap(self):
        """returns a map of gramps's IDs to Object instances"""
        return self.objectMap

    def getSavePath(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.path

    def setSavePath(self,path):
        """sets the save path for the database"""
        self.path = path

    def getPersonEventTypes(self):
        """returns a list of all Event types assocated with Person
        instances in the database"""
        map = {}
        for person in self.personMap.values():
            for event in person.getEventList():
                map[event.getName()] = 1
        return map.keys()

    def getPersonAttributeTypes(self):
        """returns a list of all Attribute types assocated with Person
        instances in the database"""
        map = {}
        for key in self.personMap.keys():
            person = self.personMap[key]
            for attr in person.getAttributeList():
                map[attr.getType()] = 1
        return map.keys()

    def getFamilyAttributeTypes(self):
        """returns a list of all Attribute types assocated with Family
        instances in the database"""
        map = {}
        for family in self.familyMap.values():
            for attr in family.getAttributeList():
                map[attr.getType()] = 1
        return map.keys()

    def getFamilyEventTypes(self):
        """returns a list of all Event types assocated with Family
        instances in the database"""
        map = {}
        for family in self.familyMap.values():
            for attr in family.getEventList():
                map[attr.getName()] = 1
        return map.keys()

    def getPlaces(self):
        """returns a list of Place instances"""
        return self.placeMap.values()

    def getFamilyRelationTypes(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        map = {}
        for family in self.familyMap.values():
            map[family.getRelationship()] = 1
        return map.keys()

    def removePerson(self,id):
        self.genderStats.uncount_person (self.personMap[id])
        del self.personMap[id]

    def removeSource(self,id):
        del self.sourceMap[id]
        del self.sourceTable[id]

    def addPersonAs(self,person):
        self.personMap[person.getId()] = person
        self.genderStats.count_person (person, self)
        return person.getId()
    
    def addPerson(self,person):
        """adds a Person to the database, assigning a gramps' ID"""
        index = self.iprefix % self.pmapIndex
        while self.personMap.has_key(index):
            self.pmapIndex = self.pmapIndex + 1
            index = self.iprefix % self.pmapIndex
        person.setId(index)
        self.personMap[index] = person
        self.pmapIndex = self.pmapIndex + 1
        self.genderStats.count_person (person, self)
        return index

    def findPerson(self,idVal,map):
        """finds a Person in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Person exists, a new Person instance
        is created.

        idVal - external ID number
        map - map build by findPerson of external to gramp's IDs"""

        idVal = str(idVal)
        if map.has_key(idVal):
            person = self.personMap[map[idVal]]
        else:
            person = Person()
            map[idVal] = self.addPerson(person)
            self.genderStats.count_person (person, self)
        return person

    def findPersonNoMap(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""
        
        person = self.personMap.get(val)
        if not person:
            person = Person()
            person.id = val
            self.personMap[val] = person
            self.pmapIndex = self.pmapIndex+1
            self.genderStats.count_person (person, self)
        return person

    def addPersonNoMap(self,person,id):
        """adds a Person to the database if the gramps' ID is known"""
        
        id = str(id)
        person.setId(id)
        self.personMap[id] = person
        self.pmapIndex = self.pmapIndex+1
        self.genderStats.count_person (person, self)
        return id

    def addSource(self,source):
        """adds a Source instance to the database, assigning it a gramps'
        ID number"""
        
        index = self.sprefix % self.smapIndex
        while self.sourceMap.has_key(index):
            self.smapIndex = self.smapIndex + 1
            index = self.sprefix % self.smapIndex
        source.setId(index)
        self.sourceMap[index] = source
        self.sourceTable[index] = source.getDisplayInfo()
        self.smapIndex = self.smapIndex + 1
        return index

    def addSourceNoMap(self,source,index):
        """adds a Source to the database if the gramps' ID is known"""
        source.setId(index)
        self.sourceMap[index] = source
        self.smapIndex = self.smapIndex + 1
        self.sourceTable[index] = source.getDisplayInfo()
        return index

    def findSource(self,idVal,map):
        """finds a Source in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Source exists, a new Source instance
        is created.

        idVal - external ID number
        map - map build by findSource of external to gramp's IDs"""
        
        if map.has_key(idVal):
            source = self.sourceMap[map[idVal]]
        else:
            source = Source()
            map[idVal] = self.addSource(source)
            self.sourceTable[map[idVal]] = source.getDisplayInfo()
        return source

    def findSourceNoMap(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        if self.sourceMap.has_key(val):
            source = self.sourceMap[val]
        else:
            source = Source()
            self.addSourceNoMap(source,val)
            self.sourceTable[val] = source.getDisplayInfo()
        return source

    def addObject(self,object):
        """adds an Object instance to the database, assigning it a gramps'
        ID number"""
        
        index = self.oprefix % self.omapIndex
        while self.objectMap.has_key(index):
            self.omapIndex = self.omapIndex + 1
            index = self.oprefix % self.omapIndex
        object.setId(index)
        self.objectMap[index] = object
        self.omapIndex = self.omapIndex + 1
        self.added_files.append(object)
        
        return index

    def getObject(self,id):
        return self.objectMap[id]

    def findObject(self,idVal,map):
        """finds an Object in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Object exists, a new Object instance
        is created.

        idVal - external ID number
        map - map build by findObject of external to gramp's IDs"""
        
        idVal = str(idVal)
        if map.has_key(idVal):
            object = self.objectMap[map[idVal]]
        else:
            object = Photo()
            map[idVal] = self.addObject(object)
        return object

    def findObjectNoConflicts(self,idVal,map):
        """finds an Object in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Object exists, a new Object instance
        is created.

        idVal - external ID number
        map - map build by findObject of external to gramp's IDs"""
        
        idVal = str(idVal)
        if map.has_key(idVal):
            object = self.objectMap[map[idVal]]
        else:
            object = Photo()
            if self.objectMap.has_key(idVal):
                map[idVal] = self.addObject(object)
            else:
                map[idVal] = self.addObjectNoMap(object,idVal)
        return object

    def addObjectNoMap(self,object,index):
        """adds an Object to the database if the gramps' ID is known"""
        index = str(index)
        object.setId(index)
        self.objectMap[index] = object
        self.omapIndex = self.omapIndex + 1
        self.added_files.append(object)
        return index

    def findObjectNoMap(self,idVal):
        """finds an Object in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        val = str(idVal)
        if self.objectMap.has_key(val):
            object = self.objectMap[val]
        else:
            object = Photo()
            self.addObjectNoMap(object,val)
        return object

    def addPlace(self,place):
        """adds a Place instance to the database, assigning it a gramps'
        ID number"""

        index = self.pprefix % self.lmapIndex
        while self.placeMap.has_key(index):
            self.lmapIndex = self.lmapIndex + 1
            index = self.pprefix % self.lmapIndex
        place.setId(index)
        self.placeMap[index] = place
        self.lmapIndex = self.lmapIndex + 1
        self.placeTable[index] = place.getDisplayInfo()
        return index

    def removeObject(self,id):
        del self.objectMap[id]

    def removePlace(self,id):
        del self.placeMap[id]
        del self.placeTable[id]

    def addPlaceAs(self,place):
        self.placeMap[place.getId()] = place
        self.placeTable[place.getId()] = place.getDisplayInfo()
        return place.getId()
        
    def findPlace(self,idVal,map):
        """finds a Place in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Place exists, a new Place instance
        is created.

        idVal - external ID number
        map - map build by findPlace of external to gramp's IDs"""

        idVal = str(idVal)
        if map.has_key(idVal):
            place = self.placeMap[map[idVal]]
        else:
            place = Place()
            map[idVal] = self.addPlace(place)
        return place

    def findPlaceNoConflicts(self,idVal,map):
        """finds a Place in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Place exists, a new Place instance
        is created.

        idVal - external ID number
        map - map build by findPlace of external to gramp's IDs"""

        if map.has_key(idVal):
            place = self.placeMap[map[idVal]]
        else:
            place = Place()
            if self.placeMap.has_key(idVal):
                map[idVal] = self.addPlace(place)
            else:
                place.setId(idVal)
                map[idVal] = self.addPlaceAs(place)
        return place

    def addPlaceNoMap(self,place,index):
        """adds a Place to the database if the gramps' ID is known"""

        index = str(index)
        place.setId(index)
        self.placeMap[index] = place
        self.lmapIndex = self.lmapIndex + 1
        self.placeTable[index] = place.getDisplayInfo()
        return index

    def findPlaceNoMap(self,val):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Place is added to the database."""

        place = self.placeMap.get(val)
        if not place:
            place = Place()
            place.id = val
            self.placeMap[val] = place
            self.lmapIndex = self.lmapIndex + 1
            self.placeTable[val] = place.getDisplayInfo()
        return place

    def sortbyplace(self,f,s):
        return cmp(self.placeTable[f][7],self.placeTable[s][7])

    def sortPlaceKeys(self):
        keys = self.placeTable.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyplace)
        return keys

    def getPlaceKeys(self):
        return self.placeTable.keys()

    def getPlace(self,key):
        return self.placeMap[key]

    def getPlaceDisplay(self,key):
        return self.placeTable[key]
        
    def getSourceKeys(self):
        return self.sourceTable.keys()

    def sortbysource(self,f,s):
        return cmp(self.sourceTable[f][3],self.placTable[s][3])

    def sortSourceKeys(self):
        keys = self.sourceTable.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyplace)
        return keys
    
    def getSourceDisplay(self,key):
        return self.sourceTable[key]

    def getSource(self,key):
        return self.sourceMap[key]

    def buildSourceDisplay(self,nkey,okey=None):
        if nkey != okey and okey != None:
            del self.sourceTable[okey]
        if self.sourceTable.has_key(nkey):
            del self.sourceTable[nkey]
        self.sourceTable[nkey] = self.sourceMap[nkey].getDisplayInfo()
        
    def newFamily(self):
        """adds a Family to the database, assigning a gramps' ID"""
        index = self.fprefix % self.fmapIndex
        while self.familyMap.has_key(index):
            self.fmapIndex = self.fmapIndex + 1
            index = self.fprefix % self.fmapIndex
        self.fmapIndex = self.fmapIndex + 1
        family = Family()
        family.setId(index)
        self.familyMap[index] = family
        return family

    def newFamilyNoMap(self,id):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""

        family = Family()
        id = str(id)
        family.setId(id)
        self.familyMap[id] = family
        self.fmapIndex = self.fmapIndex + 1
        return family

    def findFamily(self,idVal,map):
        """finds a Family in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Family exists, a new Family instance
        is created.

        idVal - external ID number
        map - map build by findFamily of external to gramp's IDs"""

        if map.has_key(idVal):
            family = self.familyMap[map[idVal]]
        else:
            family = self.newFamily()
            map[idVal] = family.getId()
        return family

    def findFamilyNoMap(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""

        family = self.familyMap.get(val)
        if not family:
            family = Family()
            family.id = val
            self.familyMap[val] = family
            self.fmapIndex = self.fmapIndex + 1
        return family

    def deleteFamily(self,family):
        """deletes the Family instance from the database"""
        if self.familyMap.has_key(family.getId()):
            del self.familyMap[family.getId()]


    def findPersonNoConflicts(self,idVal,map):
        """finds a Person in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Person exists, a new Person instance
        is created.

        idVal - external ID number
        map - map build by findPerson of external to gramp's IDs"""

        if map.has_key(idVal):
            person = self.personMap[map[idVal]]
        else:
            person = Person()
            if self.personMap.has_key(idVal):
                map[idVal] = self.addPerson(person)
            else:
                person.setId(idVal)
                map[idVal] = self.addPersonAs(person)
        return person

    def findFamilyNoConflicts(self,idVal,map):
        """finds a Family in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Family exists, a new Family instance
        is created.

        idVal - external ID number
        map - map build by findFamily of external to gramp's IDs"""

        if map.has_key(idVal):
            family = self.familyMap[map[idVal]]
        else:
            if self.familyMap.has_key(idVal):
                family = self.newFamily()
            else:
                family = self.newFamilyNoMap(idVal)
            map[idVal] = family.getId()
        return family

    def findSourceNoConflicts(self,idVal,map):
        """finds a Source in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Source exists, a new Source instance
        is created.

        idVal - external ID number
        map - map build by findSource of external to gramp's IDs"""
        
        if map.has_key(idVal):
            source = self.sourceMap[map[idVal]]
        else:
            source = Source()
            if self.sourceMap.has_key(idVal):
                map[idVal] = self.addSource(source)
            else:
                map[idVal] = self.addSource(source)
        return source
