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
import types

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

    def add_source_reference(self,id) :
        """Set the source reference"""
        self.source_list.append(id)

    def get_source_references(self) :
        """Return the source reference"""
        return self.source_list

    def set_source_reference_list(self,list) :
        """Replaces the source reference"""
        self.source_list = list

    def set_note(self,text):
        """Set the note to the given text"""
        if self.note == None:
            self.note = Note()
        self.note.set(text)

    def get_note(self):
        """Return the current note"""
        if self.note == None:
            return ""
        else:
            return self.note.get() 

    def set_note_format(self,val):
        """Set the note's format to the given value"""
        if self.note:
            self.note.set_format(val)

    def get_note_format(self):
        """Return the current note's format"""
        if self.note == None:
            return 0
        else:
            return self.note.get_format()

    def set_note_object(self,obj):
        """Change the note object instance to obj"""
        self.note = obj

    def get_note_object(self):
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

    def get_place_name(self):
        """returns the title of the Place associated with the Ordinance"""
        if self.place:
            return self.place.get_title()
        else:
            return ""

    def set_place_id(self,place):
        """sets the Place instance of the Event"""
        assert(type(place) == types.StringType or type(place) == types.UnicodeType)
        self.place = place

    def get_place_id(self):
        """returns the Place instance of the Event"""
        return self.place 

    def set_family_id(self,family):
        """Sets the family associated with the LDS ordinance"""
        self.famc = family

    def get_family_id(self):
        """Gets the family associated with the LDS ordinance"""
        return self.famc

    def set_status(self,val):
        """Sets the status of the LDS ordinance"""
        self.status = val

    def get_status(self):
        """Gets the status of the LDS ordinance"""
        return self.status

    def set_date(self, date) :
        """attempts to sets the date of the LdsOrd instance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def get_date(self) :
        """returns a string representation of the date of the LdsOrd instance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_date_object(self):
        """returns the Date object associated with the LdsOrd"""
        if not self.date:
            self.date = Date()
       	return self.date

    def set_date_object(self,date):
        """sets the Date object associated with the LdsOrd"""
        self.date = date

    def set_temple(self,temple):
        """Sets the temple assocated with the LDS ordinance"""
        self.temple = temple

    def get_temple(self):
        """Gets the temple assocated with the LDS ordinance"""
        return self.temple

    def is_empty(self):
        """Returns 1 if the LDS ordidance is actually empty"""
        if (self.famc or 
                (self.date and not self.date.is_empty()) or 
                self.temple or 
                self.status or 
                self.place):
            return 0
        else:
            return 1
        
    def are_equal(self,other):
        """returns 1 if the specified ordinance is the same as the instance"""
        if other == None:
            if self.is_empty():
                return 1
            else:
                return 0
        if (self.famc != other.famc or
            self.place != other.place or
            self.status != other.status or
            self.temple != other.temple or
            compare_dates(self.get_date_object(),other.get_date_object()) or
            len(self.get_source_references()) != len(other.get_source_references())):
            return 0

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
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

    def set_privacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def get_privacy(self):
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
            self.long = source.long
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
            self.media_list = []
            for media_id in source.media_list:
                self.media_list.append(MediaRef(media_id))
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.main_loc = None
            self.alt_loc = []
            self.id = ""
            self.urls = []
            self.media_list = []

    def serialize(self):
        return (self.id, self.title, self.long, self.lat, self.main_loc,
                self.alt_loc, self.urls, self.media_list, self.source_list, self.note)

    def unserialize(self,data):
        (self.id, self.title, self.long, self.lat, self.main_loc,
         self.alt_loc, self.urls, self.media_list, self.source_list, self.note) = data
            
    def get_url_list(self):
        """Return the list of URLs"""
        return self.urls

    def set_url_list(self,list):
        """Replace the current URL list with the new one"""
        self.urls = list

    def add_url(self,url):
        """Add a URL to the URL list"""
        self.urls.append(url)
    
    def set_id(self,id):
        """Sets the gramps ID for the place object"""
        self.id = id

    def get_id(self):
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

    def add_media_reference(self,media_id):
        """Adds a Photo object to the place object's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of Photo objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of Photo objects"""
        self.media_list = list

    def get_display_info(self):
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

    def get_name(self):
        """returns the database owner's name"""
        return self.name

    def get_address(self):
        """returns the database owner's address"""
        return self.addr

    def get_city(self):
        """returns the database owner's city"""
        return self.city

    def get_state(self):
        """returns the database owner's state"""
        return self.state

    def get_country(self):
        """returns the database owner's country"""
        return self.country

    def get_postal_code(self):
        """returns the database owner's postal code"""
        return self.postal

    def get_phone(self):
        """returns the database owner's phone number"""
        return self.phone

    def get_email(self):
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

    def set_format(self,format):
        """set the format to the passed value"""
        self.format = format

    def get_format(self):
        """return the note's format"""
        return self.format

class MediaObject(SourceNote):
    """Containter for information about an image file, including location,
    description and privacy"""
    
    def __init__(self,source=None):
        """Create a new MediaObject object, copying from the source if provided"""

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

    def serialize(self):
        return (self.id, self.local, self.path, self.mime, self.desc, self.attrlist,
                self.source_list, self.note)

    def unserialize(self,data):
        (self.id, self.local, self.path, self.mime, self.desc, self.attrlist,
         self.source_list, self.note) = data
    
    def set_local(self,val):
        """set or clear the local flag"""
        self.local = val

    def get_local(self):
        """return the local flag"""
        return self.local

    def set_id(self,id):
        """Sets the gramps ID for the place object"""
        self.id = id

    def get_id(self):
        """Returns the gramps ID for the place object"""
        return self.id

    def set_mime_type(self,type):
        self.mime = type

    def get_mime_type(self):
        return self.mime
    
    def set_path(self,path):
        """set the file path to the passed path"""
        self.path = os.path.normpath(path)

    def get_path(self):
        """return the file path"""
        return self.path

    def set_description(self,text):
        """sets the description of the image"""
        self.desc = text

    def get_description(self):
        """returns the description of the image"""
        return self.desc

    def add_attribute(self,attr):
        """Adds a propery to the MediaObject object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def get_attribute_list(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def set_attribute_list(self,list):
        self.attrlist = list


class MediaRef:
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

    def set_privacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def get_privacy(self):
        """Returns the privacy level of the data"""
        return self.private

    def set_reference_id(self,obj_id):
        self.ref = obj_id

    def get_reference_id(self):
        return self.ref

    def set_note(self,text):
        """Set the note to the given text"""
        if self.note == None:
            self.note = Note()
        self.note.set(text)

    def get_note(self):
        """Return the current note"""
        if self.note == None:
            return ""
        else:
            return self.note.get() 

    def set_note_format(self,val):
        """Set the note's format to the given value"""
        if self.note:
            self.note.set_format(val)

    def get_note_format(self):
        """Return the current note's format"""
        if self.note == None:
            return 0
        else:
            return self.note.get_format()

    def set_note_object(self,obj):
        """Change the note object instance to obj"""
        self.note = obj

    def get_note_object(self):
        """Return in note instance, not just the text"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())
    
    def add_attribute(self,attr):
        """Adds a propery to the MediaObject object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def get_attribute_list(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def set_attribute_list(self,list):
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

    def set_type(self,val):
        """sets the type (or key) of the Attribute instance"""
        self.type = val

    def get_type(self):
        """returns the type (or key) or the Attribute instance"""
        return self.type

    def set_value(self,val):
        """sets the value of the Attribute instance"""
        self.value = val

    def get_value(self):
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

    def set_date(self,text):
        """attempts to sets the date that the person lived at the address
        from the passed string"""
        self.date.set(text)

    def get_date(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.get_date()

    def get_preferred_date(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.get_preferred_date()

    def get_date_object(self):
        """returns the Date object associated with the Address"""
        return self.date

    def set_date_object(self,obj):
        """sets the Date object associated with the Address"""
        self.date = obj

    def set_street(self,val):
        """sets the street portion of the Address"""
        self.street = val

    def get_street(self):
        """returns the street portion of the Address"""
        return self.street

    def set_phone(self,val):
        """sets the phone number portion of the Address"""
        self.phone = val

    def get_phone(self):
        """returns the phone number portion of the Address"""
        return self.phone

    def set_city(self,val):
        """sets the city portion of the Address"""
        self.city = val

    def get_city(self):
        """returns the city portion of the Address"""
        return self.city

    def set_state(self,val):
        """sets the state portion of the Address"""
        self.state = val

    def get_state(self):
        """returns the state portion of the Address"""
        return self.state

    def setCountry(self,val):
        """sets the country portion of the Address"""
        self.country = val

    def get_country(self):
        """returns the country portion of the Address"""
        return self.country

    def set_postal_code(self,val):
        """sets the postal code of the Address"""
        self.postal = val

    def get_postal_code(self):
        """returns the postal code of the Address"""
        return self.postal

class Name(DataObj):
    """Provides name information about a person. A person may have more
    that one name throughout his or her life."""
    
    def __init__(self,source=None):
        """creates a new Name instance, copying from the source if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.first_name = source.first_name
            self.surname = source.surname
            self.suffix = source.suffix
            self.title = source.title
            self.type = source.type
            self.prefix = source.prefix
            self.sname = source.sname
        else:
            self.first_name = ""
            self.surname = ""
            self.suffix = ""
            self.title = ""
            self.type = "Birth Name"
            self.prefix = ""
            self.sname = '@'

    def get_surname_prefix(self):
        return self.prefix

    def set_surname_prefix(self,val):
        self.prefix = val

    def set_type(self,type):
        """sets the type of the Name instance"""
        self.type = type

    def get_type(self):
        """returns the type of the Name instance"""
        return self.type

    def build_sort_name(self):
        if self.surname:
            self.sname = "%-25s%-30s%s" % (self.surname.upper(),self.first_name.upper(),self.suffix.upper())
        else:
            self.sname = "@"

    def set_first_name(self,name):
        """sets the given name for the Name instance"""
        self.first_name = name
        self.build_sort_name()

    def set_surname(self,name):
        """sets the surname (or last name) for the Name instance"""
        self.surname = name
        self.build_sort_name()

    def set_suffix(self,name):
        """sets the suffix (such as Jr., III, etc.) for the Name instance"""
        self.suffix = name
        self.build_sort_name()

    def get_sort_name(self):
        return self.sname
    
    def get_first_name(self):
        """returns the given name for the Name instance"""
        return self.first_name

    def get_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname

    def get_upper_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname.upper()

    def get_suffix(self):
        """returns the suffix for the Name instance"""
        return self.suffix

    def set_title(self,title):
        """sets the title (Dr., Reverand, Captain) for the Name instance"""
        self.title = title

    def get_title(self):
        """returns the title for the Name instance"""
        return self.title

    def get_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix, self.surname, self.first_name, self.suffix)
            else:
                return "%s, %s %s" % (self.surname, self.first_name, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix,self.surname, self.first_name)
            else:
                return "%s, %s" % (self.surname, self.first_name)

    def get_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix.upper(), self.surname.upper(), self.first_name, self.suffix)
            else:
                return "%s, %s %s" % (self.surname.upper(), self.first_name, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix.upper(), self.surname.upper(), self.first_name)
            else:
                return "%s, %s" % (self.surname.upper(), self.first_name)

    def get_regular_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (self.first_name, self.prefix, self.surname)
            else:
                return "%s %s" % (self.first_name, self.surname)
        else:
            if self.prefix:
                return "%s %s %s, %s" % (self.first_name, self.prefix, self.surname, self.suffix)
            else:
                return "%s %s, %s" % (self.first_name, self.surname, self.suffix)

    def get_regular_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (self.first_name, self.prefix.upper(), self.surname.upper())
            else:
                return "%s %s" % (self.first_name, self.surname.upper())
        else:
            if self.prefix:
                return "%s %s %s, %s" % (self.first_name, self.prefix.upper(), self.surname.upper(), self.suffix)
            else:
                return "%s %s, %s" % (self.first_name, self.surname.upper(), self.suffix)

    def are_equal(self,other):
        """compares to names to see if they are equal, return 0 if they
        are not"""
        if self.first_name != other.first_name:
            return 0
        if self.surname != other.surname:
            return 0
        if self.prefix != other.prefix:
            return 0
        if self.suffix != other.suffix:
            return 0
        if self.title != other.title:
            return 0
        if self.type != other.type:
            return 0
        if self.private != other.private:
            return 0
        if self.get_note() != other.get_note():
            return 0
        if len(self.get_source_references()) != len(other.get_source_references()):
            return 0
        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
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

    def set_privacy(self,val):
        """sets the privacy flag for the URL instance"""
        self.private = val

    def get_privacy(self):
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
        self.primary_name = Name()
        self.event_list = []
        self.family_list = []
        self.parent_family_list = []
        self.media_list = []
        self.nickname = ""
        self.alternate_names = []
        self.gender = 2
        self.death_id = None
        self.birth_id = None
        self.address_list = []
        self.attribute_list = []
        self.urls = []
        self.ancestor = None
        self.lds_bapt = None
        self.lds_endow = None
        self.lds_seal = None
        self.complete = 0

        # We hold a reference to the GrampsDB so that we can maintain
        # its genderStats.  It doesn't get set here, but from
        # GenderStats.count_person.
        self.db = None
        
    def serialize(self):
        return (self.id, self.gender, 
                self.primary_name, self.alternate_names, self.nickname, 
                self.death_id, self.birth_id, self.event_list,
                self.family_list, self.parent_family_list,
                self.media_list, 
                self.address_list,
                self.attribute_list,
                self.urls,
                self.lds_bapt, self.lds_endow, self.lds_seal,
                self.complete,
                self.source_list,
                self.note)

    def unserialize(self,data):
        (self.id, self.gender, 
         self.primary_name, self.alternate_names, self.nickname, 
         self.death_id, self.birth_id, self.event_list,
         self.family_list, self.parent_family_list,
         self.media_list, 
         self.address_list,
         self.attribute_list,
         self.urls,
         self.lds_bapt, self.lds_endow, self.lds_seal,
         self.complete, self.source_list, self.note) = data

    def set_complete(self,val):
        self.complete = val

    def get_complete(self):
        return self.complete

    def get_display_info(self):
        if self.gender == Person.male:
            gender = const.male
        elif self.gender == Person.female:
            gender = const.female
        else:
            gender = const.unknown
        bday = self.birth_id
        dday = self.death_id
        return [ GrampsCfg.display_name(self),
                 self.id,
                 gender,
                 bday,
                 dday,
                 self.get_primary_name().get_sort_name(),
#                  sort.build_sort_date(bday),
#                  sort.build_sort_date(dday),
                 bday, dday,
                 GrampsCfg.display_surname(self.primary_name)]
                                          
    def set_primary_name(self,name):
        """sets the primary name of the Person to the specified
        Name instance"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)

        self.primary_name = name
	
        if db:
            db.genderStats.count_person (self, db)

    def get_primary_name(self):
        """returns the Name instance marked as the Person's primary name"""
        if not self.primary_name:
            self.primary_name = Name()
        return self.primary_name

    def get_alternate_names(self):
        """returns the list of alternate Names"""
        return self.alternate_names

    def set_alternate_names(self,list):
        """changes the list of alternate names to the passed list"""
        self.alternate_names = list

    def add_alternate_name(self,name):
        """adds an alternate Name instance to the list"""
        self.alternate_names.append(name)

    def get_url_list(self):
        """returns the list of URL instances"""
        return self.urls

    def set_url_list(self,list):
        """sets the list of URL instances to list"""
        self.urls = list

    def add_url(self,url):
        """adds a URL instance to the list"""
        self.urls.append(url)
    
    def set_id(self,id):
        """sets the gramps ID for the Person"""
        self.id = str(id)

    def get_id(self):
        """returns the gramps ID for the Person"""
        return self.id

    def set_nick_name(self,name):
        """sets the nickname for the Person"""
        self.nickname = name

    def get_nick_name(self) :
        """returns the nickname for the Person"""
        return self.nickname

    def set_gender(self,val) :
        """sets the gender of the Person"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)

        self.gender = val

        if db:
            db.genderStats.count_person (self, db)

    def get_gender(self) :
        """returns the gender of the Person"""
        return self.gender

    def set_birth_id(self,event_id) :
        """sets the birth event to the passed event"""
        self.birth_id = event_id

    def set_death_id(self,event_id) :
        """sets the death event to the passed event"""
        self.death_id = event_id

    def get_birth_id(self) :
        """returns the birth event"""
        return self.birth_id

    def get_death_id(self) :
        """returns the death event"""
        return self.death_id

#     def get_valid_death(self):
#         e = self.death
#         if e == None:
#             return None
#         if e.place == None and (e.date == None or not e.date.getValid()) and \
#            e.description == "" and e.cause == "" and e.witness == None:
#             return None
#         else:
#             return e

#     def get_valid_birth(self):
#         e = self.birth
#         if e == None:
#             return None
#         if e.place == None and (e.date == None or not e.date.getValid()) and \
#            e.description == "" and e.cause == "" and e.witness == None:
#             return None
#         else:
#             return e

    def add_media_reference(self,media_id):
        """adds a MediaObject instance to the image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """returns the list of MediaObjects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def add_event_id(self,event_id):
        """adds an Event to the event list"""
        self.event_list.append(event_id)

    def get_event_list(self):
        """returns the list of Event instances"""
        return self.event_list

    def set_event_list(self,list):
        """sets the event list to the passed list"""
        self.event_list = list

    def add_family_id(self,family_id):
        """adds the specified Family instance to the list of
        families/marriages/partnerships in which the person is a
        parent or spouse"""
        assert(type(family_id) == types.StringType or type(family_id) == types.UnicodeType)
        
        self.family_list.append(family_id)

    def set_preferred_family_id(self,family):
        if family in self.family_list:
            self.family_list.remove(family)
            self.family_list = [family] + self.family_list

    def get_family_id_list(self) :
        """returns the list of Family instances in which the
        person is a parent or spouse"""
        return self.family_list

    def clear_family_id_list(self) :
        self.family_list = []

    def remove_family_id(self,family):
        """removes the specified Family instance from the list
        of marriages/partnerships"""
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        if family in self.family_list:
            self.family_list.remove(family)

    def add_address(self,address):
        """adds the Address instance to the list of addresses"""
        self.address_list.append(address)

    def remove_address(self,address):
        """removes the Address instance from the list of addresses"""
        if address in self.address_list:
            self.address_list.remove(address)

    def get_address_list(self):
        """returns the list of addresses"""
        return self.address_list

    def set_address_list(self,list):
        """sets the address list to the specified list"""
        self.address_list = list

    def add_attribute(self,attribute):
        """adds an Attribute instance to the attribute list"""
        self.attribute_list.append(attribute)

    def remove_attribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)

    def get_attribute_list(self):
        """returns the attribute list"""
        return self.attribute_list

    def set_attribute_list(self,list):
        """sets the attribute list to the specified list"""
        self.attribute_list = list

    def get_parent_family_id_list(self):
        """returns the list of alternate Family instances, in which the Person
        is a child of the family, but not a natural child of both parents"""
        return self.parent_family_list

    def add_parent_family_id(self,family,mrel,frel):
        """adds a Family to the alternate family list, indicating the
        relationship to the mother (mrel) and the father (frel)"""
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        self.parent_family_list.append((family,mrel,frel))

    def clear_parent_family_id_list(self):
        self.parent_family_list = []

    def remove_parent_family_id(self,family):
        """removes a Family instance from the alternate family list"""
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        for f in self.parent_family_list[:]:
            assert(type(f[0]) == types.StringType or type(f[0]) == types.UnicodeType)
            if f[0] == family:
                self.parent_family_list.remove(f)
                return f
        else:
            return None

    def change_parent_family_id(self,family,mrel,frel):
        """removes a Family instance from the alternate family list"""
        index = 0
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        for f in self.parent_family_list[:]:
            if f[0] == family:
                self.parent_family_list[index] = (family,mrel,frel)
            index += 1

    def has_family(self,family):
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        for f in self.parent_family_list:
            assert(type(f[0]) == types.StringType or type(f[0]) == types.UnicodeType)
            if f[0] == family:
                return f
        else:
            return None

    def set_main_parent_family_id(self,family):
        """sets the main Family of the Person, the Family in which the
        Person is a natural born child"""
        assert(type(family) == types.StringType or type(family) == types.UnicodeType)
        f = self.remove_parent_family_id(family)
        if f:
            self.parent_family_list = [f] + self.parent_family_list
        
    def get_main_parents_family_id(self):
        """returns the main Family of the Person, the Family in which the
        Person is a natural born child"""
        if len(self.parent_family_list) == 0:
            return None
        else:
            return self.parent_family_list[0][0]

    def get_main_parents_family_idRel(self):
        """returns the main Family of the Person, the Family in which the
        Person is a natural born child"""
        if len(self.parent_family_list) == 0:
            return (None,None,None)
        else:
            return self.parent_family_list[0]

    def set_ancestor(self, value):
        """set ancestor flag and recurse"""
        self.ancestor = value
#         for (fam,m,f) in self.parent_family_list:
#             family
#             if family.Father:
#                 # Don't waste time if the ancestor is already flagged.
#                 # This will happen when cousins marry.
#                 if not family.Father.get_ancestor():
#                     family.Father.set_ancestor(value)
#             if family.get_mother_id():
#                 if not family.Mother.get_ancestor():
#                     family.Mother.set_ancestor(value)

    def get_ancestor(self):
        return self.ancestor

    def set_lds_baptism(self,ord):
        self.lds_bapt = ord

    def get_lds_baptism(self):
        return self.lds_bapt

    def set_lds_endowment(self,ord):
        self.lds_endow = ord

    def get_lds_endowment(self):
        return self.lds_endow

    def set_lds_sealing(self,ord):
        self.lds_seal = ord

    def get_lds_sealing(self):
        return self.lds_seal

    def probably_alive(self):
        """Returns true if the person may be alive."""
        if not self.death.is_empty ():
            return 0
        if self.birth.get_date() != "":
            return not_too_old(self.birth.get_date_object().get_start_date())

        # Neither birth nor death events are available.  Try looking
        # for descendants that were born more than a lifespan ago.

        min_generation = 13
        max_generation = 60
        max_age_difference = 60
        def descendants_too_old (person, years):
            for family in person.get_family_id_list():
                for child in family.get_child_id_list():
                    if child.birth.get_date () != "":
                        d = SingleDate (child.birth.get_date_object ().
                                        get_start_date ())
                        d.setYear (d.getYear () - years)
                        if not not_too_old (d):
                            return 1

                    if child.death.get_date () != "":
                        d = SingleDate (child.death.get_date_object ().
                                        get_start_date ())
                        if not not_too_old (d):
                            return 1

                    if descendants_too_old (child, years + min_generation):
                        return 1

        if descendants_too_old (self, min_generation):
            return 0

        # What about their parents?
        def parents_too_old (person, age_difference):
            family = person.get_main_parents_family_id ()
            if family:
                for parent in [family.get_father_id (), family.get_mother_id ()]:
                    if not parent:
                        continue

                    if parent.birth.get_date () != "":
                        d = SingleDate (parent.birth.get_date_object ().
                                        get_start_date ())
                        d.setYear (d.getYear () + max_generation +
                                   age_difference)
                        if not not_too_old (d):
                            return 1

                    if parent.death.get_date () != "":
                        d = SingleDate (parent.death.get_date_object ().
                                        get_start_date ())
                        d.setYear (d.getYear () + age_difference)
                        if not not_too_old (d):
                            return 1

        if parents_too_old (self, 0):
            return 0

        # As a last resort, trying seeing if their spouse's age gives
        # any clue.
        for family in self.get_family_id_list ():
            for spouse in [family.get_father_id (), family.get_mother_id ()]:
                if not spouse:
                    continue
                if spouse == self:
                    continue
                if spouse.birth.get_date () != "":
                    d = SingleDate (spouse.birth.get_date_object().
                                    get_start_date ())
                    d.setYear (d.getYear () + max_age_difference)
                    if not not_too_old (d):
                        return 0

                if spouse.death.get_date () != "":
                    d = SingleDate (spouse.birth.get_date_object().
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
            self.id = source.id
            try:
                if source.witness:
                    self.witness = source.witness[:]
                else:
                    self.witness = None
            except:
                self.witness = None
        else:
            self.place = u''
            self.date = None
            self.description = ""
            self.name = ""
            self.cause = ""
            self.witness = None
            self.id = None

    def clone(self,source):
        self.place = source.place
        self.date = Date(source.date)
        self.description = source.description
        self.name = source.name
        self.cause = source.cause
        self.id = source.id
        self.private = source.private
        self.source_list = source.source_list[:]
        self.note = source.note
        try:
            if source.witness:
                self.witness = source.witness[:]
            else:
                self.witness = None
        except:
            self.witness = None

    def serialize(self):
        return (self.id, self.name, self.date, self.description,
                self.place, self.cause, self.private, self.source_list,
                self.note, self.witness)

    def unserialize(self,data):
        (self.id, self.name, self.date, self.description,
         self.place, self.cause, self.private, self.source_list,
         self.note, self.witness) = data

    def set_id(self,id):
        """Sets the gramps ID for the place object"""
        self.id = id

    def get_id(self):
        """Returns the gramps ID for the place object"""
        return self.id

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
        date = self.get_date_object()
        place = self.get_place_id()
        description = self.description
        cause = self.cause
        name = self.name
        if (not name or name == "Birth" or name == "Death") and \
           date.is_empty() and not place and not description and not cause:
            return 1
        else:
            return 0

    def set(self,name,date,place,description):
        """sets the name, date, place, and description of an Event instance"""
        self.name = name
        self.place = place
        self.description = description
        self.set_date(date)
        
    def are_equal(self,other):
        """returns 1 if the specified event is the same as the instance"""
        if other == None:
            return 0
        if (self.name != other.name or self.place != other.place or
            self.description != other.description or self.cause != other.cause or
            self.private != other.private or
            compare_dates(self.get_date_object(),other.get_date_object()) or
            len(self.get_source_references()) != len(other.get_source_references())):
            return 0

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1

        witness_list = self.get_witness_list()
        other_list = other.get_witness_list()
        if (not witness_list) and (not other_list):
            return 1
        elif not (witness_list and other_list):
            return 0
        other_list = other_list[:]
        for a in witness_list:
            if a in other_list:
                other_list.remove(a)
            else:
                return 0
        if other_list:
            return 0

        return 1
        
    def set_name(self,name):
        """sets the name of the Event"""
        self.name = name

    def get_name(self):
        """returns the name of the Event"""
        return self.name

    def set_place_id(self,place):
        """sets the Place instance of the Event"""
        assert(type(place) == types.StringType or type(place) == types.UnicodeType)
        self.place = place

    def get_place_id(self):
        """returns the Place instance of the Event"""
        return self.place 

    def set_cause(self,cause):
        """sets the cause of the Event"""
        self.cause = cause

    def get_cause(self):
        """returns the cause of the Event"""
        return self.cause 

    def set_description(self,description):
        """sets the description of the Event instance"""
        self.description = description

    def get_description(self) :
        """returns the description of the Event instance"""
        return self.description 

    def set_date(self, date) :
        """attempts to sets the date of the Event instance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def get_date(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_preferred_date(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_quote_date(self) :
        """returns a string representation of the date of the Event instance,
        enclosing the results in quotes if it is not a valid date"""
        if self.date:
            return self.date.get_quote_date()
        return ""

    def get_date_object(self):
        """returns the Date object associated with the Event"""
        if not self.date:
            self.date = Date()
       	return self.date

    def set_date_object(self,date):
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
        self.father_id = None
        self.mother_id = None
        self.child_list = []
        self.type = "Married"
        self.event_list = []
        self.id = ""
        self.media_list = []
        self.attribute_list = []
        self.lds_seal = None
        self.complete = 0


    def serialize(self):
        return (self.id, self.father_id, self.mother_id,
                self.child_list, self.type, self.event_list,
                self.media_list, self.attribute_list, self.lds_seal,
                self.complete,
                self.source_list,
                self.note)

    def unserialize(self, data):
        (self.id, self.father_id, self.mother_id,
         self.child_list, self.type, self.event_list,
         self.media_list, self.attribute_list, self.lds_seal,
         self.complete,
         self.source_list,
         self.note) = data

    def set_complete(self,val):
        self.complete = val

    def get_complete(self):
        return self.complete

    def set_lds_sealing(self,ord):
        self.lds_seal = ord

    def get_lds_sealing(self):
        return self.lds_seal

    def add_attribute(self,attribute) :
        """adds an Attribute instance to the attribute list"""
        self.attribute_list.append(attribute)

    def remove_attribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)

    def get_attribute_list(self) :
        """returns the attribute list"""
        return self.attribute_list

    def set_attribute_list(self,list) :
        """sets the attribute list to the specified list"""
        self.attribute_list = list

    def set_id(self,id) :
        """sets the gramps ID for the Family"""
       	self.id = str(id)

    def get_id(self) :
        """returns the gramps ID for the Family"""
       	return self.id

    def set_relationship(self,type):
        """assigns a string indicating the relationship between the
        father and the mother"""
        self.type = type

    def get_relationship(self):
        """returns a string indicating the relationship between the
        father and the mother"""
        return self.type
    
    def set_father_id(self,person_id):
        """sets the father of the Family to the specfied Person"""
#        update = self.some_child_is_ancestor()
#        if update and father_id:
#            father_id.set_ancestor(0)
        self.father_id = person_id
#        if update and father_id:
#            father_id.set_ancestor(1)

    def get_father_id(self):
        """returns the father of the Family"""
       	return self.father_id

    def set_mother_id(self,person):
        """sets the mother of the Family to the specfied Person"""
#        update = self.some_child_is_ancestor()
#        if self.mother_id and update:
#            self.mother_id.set_ancestor(0)
        self.mother_id = person
#        if update and self.mother_id:
#            self.mother_id.set_ancestor(1)

    def get_mother_id(self):
        """returns the mother of the Family"""
       	return self.mother_id

    def add_child_id(self,person):
        """adds the specfied Person as a child of the Family, adding it
        to the child list"""
        assert(type(person) == types.StringType or type(person) == types.UnicodeType)

        if person not in self.child_list:
            self.child_list.append(person)
#        if person.get_ancestor():
#            if father_id:
#                father_id.set_ancestor(1)
#            if self.mother_id:
#                self.mother_id.set_ancestor(1)
            
    def remove_child_id(self,person):
        """removes the specified Person from the child list"""
        assert(type(person) == types.StringType or type(person) == types.UnicodeType)

        if person in self.child_list:
            self.child_list.remove(person)
#        if person.get_ancestor():
#            if father_id:
#                father_id.set_ancestor(0)
#            if self.mother_id:
#                self.mother_id.set_ancestor(0)

    def get_child_id_list(self):
        """returns the list of children"""
        return self.child_list

    def set_child_id_list(self, list):
        """sets the list of children"""
        self.child_list = list[:]

#     def get_marriage(self):
#         """returns the marriage event of the Family. Obsolete"""
#         for e in self.event_list:
#             if e.get_name() == "Marriage":
#                 return e
#         return None

    def get_divorce(self):
        """returns the divorce event of the Family. Obsolete"""
        for e in self.event_list:
            if e.get_name() == "Divorce":
                return e
        return None

    def add_event_id(self,event_id):
        """adds an Event to the event list"""
        self.event_list.append(event_id)

    def get_event_list(self) :
        """returns the list of Event instances"""
        return self.event_list

    def set_event_list(self,list) :
        """sets the event list to the passed list"""
        self.event_list = list

    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the Family instance's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def some_child_is_ancestor(self):
        for child in self.child_list:
            if (child.get_ancestor()):
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
        self.media_list = []
        self.id = ""
        self.abbrev = ""

    def serialize(self):
        return (self.id,self.title,self.author,self.pubinfo,self.note,self.media_list,self.abbrev)

    def unserialize(self,data):
        (self.id,self.title,self.author,self.pubinfo,self.note,self.media_list,self.abbrev) = data
        
    def get_display_info(self):
        return [self.title,self.id,self.author,self.title.upper(),self.author.upper()]

    def set_id(self,newId):
        """sets the gramps' ID for the Source instance"""
        self.id = str(newId)

    def get_id(self):
        """returns the gramps' ID of the Source instance"""
        return self.id

    #EARNEY, this should eventually be a list of ids not objects, right?
    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the Source instance's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def set_title(self,title):
        """sets the title of the Source"""
        self.title = title

    def get_title(self):
        """returns the title of the Source"""
        return self.title

    def set_note(self,text):
        """sets the text of the note attached to the Source"""
        self.note.set(text)

    def get_note(self):
        """returns the text of the note attached to the Source"""
        return self.note.get()

    def set_note_format(self,val):
        """Set the note's format to the given value"""
        self.note.set_format(val)

    def get_note_format(self):
        """Return the current note's format"""
        return self.note.get_format()

    def set_note_object(self,obj):
        """sets the Note instance attached to the Source"""
        self.note = obj

    def get_note_object(self):
        """returns the Note instance attached to the Source"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

    def set_author(self,author):
        """sets the author of the Source"""
        self.author = author

    def get_author(self):
        """returns the author of the Source"""
        return self.author

    def set_publication_info(self,text):
        """sets the publication information of the Source"""
        self.pubinfo = text

    def get_publication_info(self):
        """returns the publication information of the Source"""
        return self.pubinfo

    def set_abbreviation(self,abbrev):
        """sets the title abbreviation of the Source"""
        self.abbrev = abbrev

    def get_abbreviation(self):
        """returns the title abbreviation of the Source"""
        return self.abbrev

class SourceRef:
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    def __init__(self,source=None):
        """creates a new SourceRef, copying from the source if present"""
        if source:
            self.confidence = source.confidence
            assert(type(source.ref) == types.StringType or type(source.ref) == types.UnicodeType)
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

    def set_confidence_level(self,val):
        """Sets the confidence level"""
        self.confidence = val

    def get_confidence_level(self):
        """Returns the confidence level"""
        return self.confidence
        
    def set_base_id(self,ref):
        """sets the Source instance to which the SourceRef refers"""
        assert(type(ref) == types.StringType or type(ref) == types.UnicodeType)
        self.ref = ref

    def get_base_id(self):
        """returns the Source instance to which the SourceRef refers"""
        return self.ref
    
    def set_date(self,date):
        """sets the Date instance of the SourceRef"""
        self.date = date

    def get_date(self):
        """returns the Date instance of the SourceRef"""
        return self.date

    def set_page(self,page):
        """sets the page indicator of the SourceRef"""
        self.page = page

    def get_page(self):
        """gets the page indicator of the SourceRef"""
        return self.page

    def set_text(self,text):
        """sets the text related to the SourceRef"""
        self.text = text

    def get_text(self):
        """returns the text related to the SourceRef"""
        return self.text

    def set_note_object(self,note):
        """Change the Note instance to obj"""
        self.comments = note

    def set_comments(self,comments):
        """sets the comments about the SourceRef"""
        self.comments.set(comments)

    def get_comments(self):
        """returns the comments about the SourceRef"""
        return self.comments.get()

    def are_equal(self,other):
        """returns 1 if the passed SourceRef is equal to the current"""
        if self.ref and other.ref:
            if self.page != other.page:
                return 0
            if compare_dates(self.date,other.date) != 0:
                return 0
            if self.get_text() != other.get_text():
                return 0
            if self.get_comments() != other.get_comments():
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
        name = person.get_primary_name ().get_first_name ()
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

        gender = person.get_gender ()
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

try:    # First try python2.3 and later: this is the future
    from bsddb import dbshelve, db
except ImportError: # try python2.2
    from bsddb3 import dbshelve, db


def find_surname(key,data):
    return str(data[2].get_surname())

class GrampsDB:
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""

        self.env = db.DBEnv()
        flags = db.DB_CREATE|db.DB_INIT_MPOOL
        
        self.env.open(".", flags)
        
        self.person_map = dbshelve.open('person.db', dbname="person", dbenv=self.env)
        self.family_map = dbshelve.open('person.db', dbname="family", dbenv=self.env)
        self.place_map  = dbshelve.open('person.db', dbname="places", dbenv=self.env)
        self.source_map = dbshelve.open('person.db', dbname="sources",dbenv=self.env)
        self.media_map  = dbshelve.open('person.db', dbname="media",  dbenv=self.env)
        self.event_map  = dbshelve.open('person.db', dbname="events", dbenv=self.env)

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open("person.db", "surnames", db.DB_HASH, flags=db.DB_CREATE)

        self.person_map.associate(self.surnames, find_surname, db.DB_CREATE)

        self.iprefix = "I%04d"
        self.sprefix = "S%04d"
        self.oprefix = "O%04d"
        self.pprefix = "P%04d"
        self.fprefix = "F%04d"
        self.eprefix = "E%04d"
        self.new()
        self.added_files = []
        self.genderStats = GenderStats ()

    def close(self):
        self.person_map.close()
        self.family_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
        self.surnames.close()

    def get_added_media_objects(self):
        return self.added_files

    def clear_added_media_objects(self):
        self.added_files = []
        
    def get_type(self):
        return 'GrampsDB'

    def get_base(self):
        return ""

    def need_autosave(self):
        return 1

    def get_number_of_people(self):
        return len(self.person_map)

    def get_person_keys(self):
        return self.person_map.keys()

    def get_family_keys(self):
        return self.family_map.keys()

    def sort_by_name(self,f,s):
        n1 = self.person_map.get(str(f))[2].sname
        n2 = self.person_map.get(str(s))[2].sname
        return cmp(n1,n2)

    def sort_person_keys(self):
        return self.person_map.keys()
#         keys = self.person_map.keys()
#         if type(keys) == type([]):
#             keys.sort(self.sort_by_name)
#         return keys

    def get_person_display(self,key):
        data = self.person_map.get(str(key))

        if data[1] == Person.male:
            gender = const.male
        elif data[1] == Person.female:
            gender = const.female
        else:
            gender = const.unknown
            
        return [ data[2].get_name(),
                 data[0],
                 gender,
                 data[6],
                 data[5],
                 data[2].get_sort_name(),
#                  sort.build_sort_date(bday),
#                  sort.build_sort_date(dday),
                 data[6],
                 data[5],
                 GrampsCfg.display_surname(data[2])]

    def commit_person(self,person):
        assert(person.get_id())
        self.person_map.put(str(person.get_id()),person.serialize())

    def commit_media_object(self,object):
        self.media_map.put(str(object.get_id()),object.serialize())

    def commit_source(self,source):
        self.source_map.put(str(source.get_id()),source.serialize())

    def commit_place(self,place):
        self.place_map.put(str(place.get_id()),place.serialize())

    def commit_event(self,event):
        self.event_map.put(str(event.get_id()),event.serialize())

    def commit_family(self,family):
        self.family_map.put(str(family.get_id()),family.serialize())

    def build_person_display(self,nkey,okey=None):
        pass

    def rebuild_person_table(self):
        pass
        
    def build_place_display(self,nkey,okey=None):
        pass
        
    def set_iprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.iprefix = val
            else:
                self.iprefix = val + "%d"
        else:
            self.iprefix = "I%04d"
            
    def set_sprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.sprefix = val
            else:
                self.sprefix = val + "%d"
        else:
            self.sprefix = "S%04d"
            
    def set_oprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.oprefix = val
            else:
                self.oprefix = val + "%d"
        else:
            self.oprefix = "O%04d"

    def set_pprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.pprefix = val
            else:
                self.pprefix = val + "%d"
        else:
            self.pprefix = "P%04d"

    def set_fprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.fprefix = val
            else:
                self.fprefix = val + "%d"
        else:
            self.fprefix = "F%04d"

    def set_eprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.eprefix = val
            else:
                self.eprefix = val + "%d"
        else:
            self.eprefix = "E%04d"
            
    def new(self):
        """initializes the GrampsDB to empty values"""

        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.default = None
        self.owner = Researcher()
        self.bookmarks = []
        self.path = ""
        self.place2title = {}
        self.genderStats = GenderStats ()

    #EARNEY, may eventually be able to use secondary indexes for this
    #that way we will not have to track these with code.
    def get_surnames(self):
        return []
#        return self.surnames.keys()

    #this function may eventually become obsolete.. if we use
    #secondary indexes.
    def add_surname(self,name):
        pass
#         if name and name not in self.surnames:
#             self.surnames.append(name)
#             self.surnames.sort()

    def get_bookmarks(self):
        """returns the list of Person instances in the bookmarks"""
        return self.bookmarks

    def clean_bookmarks(self):
        """cleans up the bookmark list, removing empty slots"""
        new_bookmarks = []
        for person_id in self.bookmarks:
            new_bookmarks.append(person_id)
        self.bookmarks = new_bookmarks
            
    def set_researcher(self,owner):
        """sets the information about the owner of the database"""
        self.owner.set(owner.get_name(),owner.get_address(),owner.get_city(),\
                       owner.get_state(),owner.get_country(),\
                       owner.get_postal_code(),owner.get_phone(),owner.get_email())

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.owner

    def set_default_person(self,person):
        """sets the default Person to the passed instance"""
#        if (self.default):
#            self.default.set_ancestor(0)
        self.default = str(person)
#        if person:
#            self.default.set_ancestor(1)
    
    def get_default_person(self):
        """returns the default Person of the database"""
        if self.default == None:
            return None
        person = Person()
        data = self.person_map.get(self.default)
        person.unserialize(data)
        return person

    def get_person(self,id):
        """returns a Person from a GRAMPS's ID"""
        p = Person()
        data = self.person_map.get(str(id))
        p.unserialize(data)
        return p

    def get_place_id_map(self):
        """returns a map of gramps's IDs to Place instances"""
        return self.place_map

    def set_place_id_map(self,map):
        """sets the map of gramps's IDs to Place instances"""
        self.place_map = map

    def get_family_id(self,id):
        """returns a map of gramps's IDs to Family instances"""
        return self.family_map.get(str(id))

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.path

    def set_save_path(self,path):
        """sets the save path for the database"""
        self.path = path

    def get_person_event_types(self):
        """returns a list of all Event types assocated with Person
        instances in the database"""
        map = {}
#        for person in self.person_map.values():
#            for event_id in person.get_event_list():
#                event = self.event_map[event_id]
#                map[event.get_name()] = 1
        return map.keys()

    def get_person_attribute_types(self):
        """returns a list of all Attribute types assocated with Person
        instances in the database"""
        map = {}
#        for key in self.person_map.keys():
#            person = self.person_map[key]
#            for attr in person.get_attribute_list():
#                map[attr.get_type()] = 1
        return map.keys()

    def get_family_attribute_types(self):
        """returns a list of all Attribute types assocated with Family
        instances in the database"""
        map = {}
#        for family in self.family_map.values():
#            for attr in family.get_attribute_list():
#                map[attr.get_type()] = 1
        return map.keys()

    def get_family_event_types(self):
        """returns a list of all Event types assocated with Family
        instances in the database"""
        map = {}
#        for family in self.family_map.values():
#            for event_id in family.get_event_list():
#                event = self.event_map[event_id]
#                map[event.get_name()] = 1
        return map.keys()

    def get_place_ids(self):
        """returns a list of Place instances"""
        return self.place_map.keys() 

    def get_family_relation_types(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        map = {}
#        for family in self.family_map.values():
#            map[family.get_relationship()] = 1
        return map.keys()

    def remove_person_id(self,id):
#        self.genderStats.uncount_person (self.person_map[id])
        self.person_map.delete(str(id))

    def remove_source_id(self,id):
        self.source_map.delete(str(id))

    def remove_event_id(self,id):
        self.event_map.delete(str(id))

    def add_person_as(self,person):
        assert(person.get_id())
        self.person_map.put(str(person.get_id()),person.serialize())
#        self.genderStats.count_person (person, self)
        return person.get_id()
    
    def add_person(self,person):
        """adds a Person to the database, assigning a gramps' ID"""
        index = self.iprefix % self.pmap_index
        while self.person_map.get(str(index)):
            self.pmap_index = self.pmap_index + 1
            index = self.iprefix % self.pmap_index
        person.set_id(index)
        assert(person.get_id())
        self.person_map.put(str(index),person.serialize())
        self.pmap_index = self.pmap_index + 1
        self.genderStats.count_person (person, self)
        return index

    def find_person(self,idVal,map):
        """finds a Person in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Person exists, a new Person instance
        is created.

        idVal - external ID number
        map - map build by findPerson of external to gramp's IDs"""

        idVal = str(idVal)
        person = Person()
        if map.has_key(idVal):
            person.unserialize(self.person_map.get(str(map[idVal])))
        else:
            person = Person()
            map[idVal] = self.add_person(person)
            self.genderStats.count_person (person, self)
        return person

    def has_person_id(self,val):            #what does this function do?
        return self.person_map.get(str(val))  #EARNEY

    def find_person_from_id(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""

        person = Person()
        data = self.person_map.get(str(val))

        if data:
            person.unserialize(data)
        else:
            person.set_id(val)
            assert(person.get_id())
            assert(person.get_id()[0] == 'I')
            self.person_map.put(str(val), person.serialize())
            self.pmap_index = self.pmap_index+1
#            self.genderStats.count_person (person, self)
        return person

    def add_person_no_map(self,person,id):
        """adds a Person to the database if the gramps' ID is known"""
        
        id = str(id)
        person.set_id(id)
        self.person_map.set(str(id),person.serialize())
        self.pmap_index = self.pmap_index+1
#        self.genderStats.count_person (person, self)
        return id

    def add_source(self,source):
        """adds a Source instance to the database, assigning it a gramps'
        ID number"""
        
        index = self.sprefix % self.smap_index
        while self.source_map.get(str(index)):
            self.smap_index = self.smap_index + 1
            index = self.sprefix % self.smap_index
        source.set_id(index)
        self.source_map.put(str(index),source.serialize())
        self.smap_index = self.smap_index + 1
        return index

    def add_event(self,event):
        """adds a Event instance to the database, assigning it a gramps'
        ID number"""
        index = self.eprefix % self.emap_index
        while self.event_map.get(str(index)):
            self.emap_index += 1
            index = self.eprefix % self.emap_index
        event.set_id(index)
        self.event_map.put(str(index),event.serialize())
        self.emap_index += 1
        return index

    def add_source_no_map(self,source,index):
        """adds a Source to the database if the gramps' ID is known"""
        source.set_id(index)
        self.source_map.put(str(index),source.serialize())
        self.smap_index = self.smap_index + 1
        return index

    def add_event_no_map(self,event,index):
        """adds a Source to the database if the gramps' ID is known"""
        return
        event.set_id(index)
        self.event_map.put(str(index),event.serialize())
        self.emap_index += 1
        return index

    def find_source(self,idVal,map):
        """finds a Source in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Source exists, a new Source instance
        is created.

        idVal - external ID number
        map - map build by find_source of external to gramp's IDs"""
        
        if map.has_key(idVal):
            data = self.source_map.get(str(map[idVal]))
            source = Source()
            source.unserialize(data)
        else:
            source = Source()
            map[idVal] = self.add_source(source)
        return source

    def find_event(self,idVal,map):
        """finds a Event in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Event exists, a new Event instance
        is created.

        idVal - external ID number
        map - map build by find_source of external to gramp's IDs"""
        
        event = Event()
        if map.has_key(idVal):
            pass
#            data = self.event_map.get(str(map[idVal]))
#            event.serialize(data)
        else:
            map[idVal] = self.add_event(event)
        return event

    def find_source_from_id(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        source = Source()
        if self.source_map.get(str(val)):
            source.unserialize(self.source_map.get(str(val)))
        else:
            self.add_source_no_map(source,val)
        return source

    def find_event_from_id(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""
        data = self.event_map.get(str(val))
        if data:
            event = Event()
            event.unserialize(data)
            return event
        else:
            return None

    def add_object(self,object):
        """adds an Object instance to the database, assigning it a gramps'
        ID number"""
        
        index = self.oprefix % self.omap_index
        while self.media_map.get(str(index)):
            self.omap_index = self.omap_index + 1
            index = self.oprefix % self.omap_index
        object.set_id(index)
        self.media_map.put(str(index),object.serialize())
        self.omap_index = self.omap_index + 1
        self.added_files.append(object)
        
        return index

    def get_object(self,id):
        return self.media_map[str(id)]

    def find_object(self,idVal,map):
        """finds an Object in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Object exists, a new Object instance
        is created.

        idVal - external ID number
        map - map build by find_object of external to gramp's IDs"""
        
        idVal = str(idVal)
        
        object = MediaObject()
        if map.has_key(idVal):
            object.unserialize(self.media_map.get(str(map[idVal])))
        else:
            map[idVal] = self.add_object(object)
        return object

    def find_object_no_conflicts(self,idVal,map):
        """finds an Object in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Object exists, a new Object instance
        is created.

        idVal - external ID number
        map - map build by find_object of external to gramp's IDs"""
        
        idVal = str(idVal)
        object = MediaObject()
        if map.has_key(idVal):
            object.unserialize(self.media_map.get(str(map[idVal])))
        else:
            if self.media_map.get(str(idVal)):
                map[idVal] = self.add_object(object)
            else:
                map[idVal] = self.add_object_no_map(object,idVal)
        return object

    def add_object_no_map(self,object,index):
        """adds an Object to the database if the gramps' ID is known"""
        index = str(index)
        object.set_id(index)
        self.media_map.put(str(index),object.serialize())
        self.omap_index = self.omap_index + 1
        self.added_files.append(object)
        return index

    def find_object_from_id(self,idVal):
        """finds an Object in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        object = MediaObject()
        if self.media_map.get(str(idVal)):
            object.unserialize(self.media_map.get(str(idVal)))
        else:
            self.add_object_no_map(object,idVal)
        return object

    def add_place(self,place):
        """adds a Place instance to the database, assigning it a gramps'
        ID number"""

        index = self.pprefix % self.lmap_index
        while self.place_map.get(str(index)):
            self.lmap_index = self.lmap_index + 1
            index = self.pprefix % self.lmap_index
        place.set_id(index)
        self.place_map.put(str(index),place.serialize())
        self.lmap_index = self.lmap_index + 1
        return index

    def remove_object(self,id):
        self.media_map.delete(str(id))

    def remove_place(self,id):
        self.place_map.delete(str(id))

    def add_place_as(self,place):
        self.place_map.put(str(place.get_id()),place.serialize())
        return place.get_id()
        
    def find_place_no_conflicts(self,idVal,map):
        """finds a Place in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Place exists, a new Place instance
        is created.

        idVal - external ID number
        map - map build by findPlace of external to gramp's IDs"""

        if map.has_key(idVal):
            place = Place()
            data = self.place_map[map[idVal]]
            place.unserialize(data)
        else:
            place = Place()
            if self.place_map.has_key(idVal):
                map[idVal] = self.add_place(place)
            else:
                place.set_id(idVal)
                map[idVal] = self.add_place_as(place)
            self.place_map.put(str(idVal),place.serialize())
        return place

    def add_place_no_map(self,place,index):
        """adds a Place to the database if the gramps' ID is known"""

        index = str(index)
        place.set_id(index)
        self.place_map.put(str(index), place.serialize())
        self.lmap_index = self.lmap_index + 1
        return index

    def find_place_from_id(self,id):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Place is added to the database."""

        data = self.place_map.get(str(id))
        place = Place()
        if not data:
            place.id = id
            self.place_map.put(str(id),place.serialize())
            self.lmap_index = self.lmap_index + 1
        else:
            place.unserialize(data)
        return place

    def sortbyplace(self,f,s):
        fp = self.place_map[f][0].upper()
        sp = self.place_map[s][0].upper()
        return cmp(fp,sp)

    def sort_place_keys(self):
        keys = self.place_map.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyplace)
        return keys

    def get_place_id_keys(self):
        return self.place_map.keys()

    def get_place_id(self,key):
        place = Place()
        place.unserialize(self.place_map.get(str(key)))
        return place

    def get_place_display(self,key):
        # fix this up better
        place = Place()
        place.unserialize(self.place_map[key])
        return place.get_display_info()
        
    def get_source_keys(self):
        return self.source_map.keys()

    def get_object_keys(self):
        return self.media_map.keys()

    def sortbysource(self,f,s):
        f1 = self.source_map[f][1].upper()
        s1 = self.source_map[s][1].upper()
        return cmp(f1,s1)

    def set_source_keys(self):
        keys = self.source_map.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyplace)
        return keys
    
    def get_source_display(self,key):
        source = Source()
        source.unserialize(self.source_map.get(str(key)))
        return source.get_display_info()

    def get_source(self,key):
        source = Source()
        source.unserialize(self.source_map[key])
        return source

    def build_source_display(self,nkey,okey=None):
        pass
        
    def new_family(self):
        """adds a Family to the database, assigning a gramps' ID"""
        index = self.fprefix % self.fmap_index
        while self.family_map.get(str(index)):
            self.fmap_index = self.fmap_index + 1
            index = self.fprefix % self.fmap_index
        self.fmap_index = self.fmap_index + 1
        family = Family()
        family.set_id(index)
        self.family_map.put(str(index),family.serialize())
        return family

    def new_family_no_map(self,id):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""

        family = Family()
        id = str(id)
        family.set_id(id)
        self.family_map.put(str(id),family.serialize())
        self.fmap_index = self.fmap_index + 1
        return family

    def find_family_with_map(self,idVal,map):
        """finds a Family in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Family exists, a new Family instance
        is created.

        idVal - external ID number
        map - map build by find_family_with_map of external to gramp's IDs"""

        if map.has_key(idVal):
            family = Family()
            data = self.family_map.get(str(map[idVal]))
            family.unserialize(data)
        else:
            family = self.new_family()
            map[idVal] = family.get_id()
        return family

    def find_family_no_map(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""

        family = Family()
        data = self.family_map.get(str(val))
        if data:
            family.unserialize(data)
        else:
            family.id = val
            self.family_map.put(str(val),family.serialize())
            self.fmap_index = self.fmap_index + 1
        return family

    def find_family_from_id(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""
        data = self.family_map.get(str(val))
        if data:
            family = Family()
            family.unserialize(data)
            return family
        else:
            return None

    def delete_family(self,family_id):
        """deletes the Family instance from the database"""
        if self.family_map.get(str(family_id)):
            self.family_map.delete(str(family_id))

    def find_person_no_conflicts(self,idVal,map):
        """finds a Person in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Person exists, a new Person instance
        is created.

        idVal - external ID number
        map - map build by findPerson of external to gramp's IDs"""

        person = Person()
        if map.has_key(idVal):
            person.serialize(self.person_map.get(str(map[idVal])))
        else:
            if self.person_map.get(str(idVal)):
                map[idVal] = self.add_person(person)
            else:
                person.set_id(idVal)
                map[idVal] = self.add_person_as(person)
        return person

    def find_family_no_conflicts(self,idVal,map):
        """finds a Family in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Family exists, a new Family instance
        is created.

        idVal - external ID number
        map - map build by findFamily of external to gramp's IDs"""

        if map.has_key(idVal):
            family = Family()
            family.unserialize(self.family_map.get(str(map[idVal])))
        else:
            if self.family_map.has_key(idVal):
                family = self.new_family()
            else:
                family = self.new_family_no_map(idVal)
            map[idVal] = family.get_id()
        return family

    def find_source_no_conflicts(self,idVal,map):
        """finds a Source in the database using the idVal and map
        variables to translate between the external ID and gramps'
        internal ID. If no such Source exists, a new Source instance
        is created.

        idVal - external ID number
        map - map build by findSource of external to gramp's IDs"""
        
        source = Source()
        if map.has_key(idVal):
            source.unserialize(self.source_map.get(str(map[idVal])))
        else:
            if self.source_map.get(str(idVal)):
                map[idVal] = self.add_source(source)
            else:
                map[idVal] = self.add_source(source)
        return source
