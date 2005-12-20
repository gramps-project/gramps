#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

"""
Secondary (non-primary) objects for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _helper import *

#-------------------------------------------------------------------------
#
# Class for notes used throughout the majority of GRAMPS objects
#
#-------------------------------------------------------------------------
class Note(BaseObject):
    """
    Introduction
    ============
    The Note class defines a text note. The note may be preformatted
    or 'flowed', which indicates that it text string is considered
    to be in paragraphs, separated by newlines.
    """
    
    def __init__(self,text = ""):
        """
        Creates a new Note object, initializing from the passed string.
        """
        BaseObject.__init__(self)
        self.text = text
        self.format = 0

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.text]

    def set(self,text):
        """
        Sets the text associated with the note to the passed string.

        @param text: Text string defining the note contents.
        @type text: str
        """
        self.text = text

    def get(self):
        """
        Return the text string associated with the note.
        @returns: Returns the text string defining the note contents.
        @rtype: str
        """
        return self.text

    def append(self,text):
        """
        Appends the specified text to the text associated with the note.

        @param text: Text string to be appended to the note.
        @type text: str
        """
        self.text = self.text + text

    def set_format(self,format):
        """
        Sets the format of the note to the passed value. The value can
        either indicate Flowed or Preformatted.

        @param format: 0 indicates Flowed, 1 indicates Preformated
        @type format: int
        """
        self.format = format

    def get_format(self):
        """
        Returns the format of the note. The value can either indicate
        Flowed or Preformatted.

        @returns: 0 indicates Flowed, 1 indicates Preformated
        @rtype: int
        """
        return self.format

#-------------------------------------------------------------------------
#
# Personal Name
#
#-------------------------------------------------------------------------
class Name(PrivateSourceNote,DateBase):
    """
    Provides name information about a person.

    A person may have more that one name throughout his or her life.
    """

    DEF  = 0  # locale default
    LNFN = 1  # last name first name [patronymic]
    FNLN = 2  # first name last name
    PTFN = 3  # patronymic last name
    FN   = 4  # first name
    
    UNKNOWN = -1
    CUSTOM  = 0
    AKA     = 1
    BIRTH   = 2
    MARRIED = 3

    def __init__(self,source=None):
        """creates a new Name instance, copying from the source if provided"""
        PrivateSourceNote.__init__(self,source)
        DateBase.__init__(self,source)

        if source:
            self.first_name = source.first_name
            self.surname = source.surname
            self.suffix = source.suffix
            self.title = source.title
            self.type = source.type
            self.prefix = source.prefix
            self.patronymic = source.patronymic
            self.sname = source.sname
            self.group_as = source.group_as
            self.sort_as = source.sort_as
            self.display_as = source.display_as
        else:
            self.first_name = ""
            self.surname = ""
            self.suffix = ""
            self.title = ""
            self.type = (Name.BIRTH,"")
            self.prefix = ""
            self.patronymic = ""
            self.sname = '@'
            self.group_as = ""
            self.sort_as = self.DEF
            self.display_as = self.DEF

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.first_name,self.surname,self.suffix,self.title,
                self.type[1],self.prefix,self.patronymic]
        #return [self.first_name,self.surname,self.suffix,self.title,
        #        self.type[1],self.prefix,self.patronymic,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_group_as(self,name):
        """
        Sets the grouping name for a person. Normally, this is the person's
        surname. However, some locales group equivalent names (e.g. Ivanova
        and Ivanov in Russian are usually considered equivalent.
        """
        if name == self.surname:
            self.group_as = ""
        else:
            self.group_as = name

    def get_group_as(self):
        """
        Returns the grouping name, which is used to group equivalent surnames.
        """
        return self.group_as

    def get_group_name(self):
        """
        Returns the grouping name, which is used to group equivalent surnames.
        """
        if self.group_as:
            return self.group_as
        else:
            return self.surname

    def set_sort_as(self,value):
        """
        Specifies the sorting method for the specified name. Typically the
        locale's default should be used. However, there may be names where
        a specific sorting structure is desired for a name. 
        """
        self.sort_as = value

    def get_sort_as(self):
        """
        Returns the selected sorting method for the name. The options are
        DEF (default for the current locale), LNFN (last name, first name),
        or FNLN (first name, last name).
        """
        return self.sort_as 

    def set_display_as(self,value):
        """
        Specifies the display format for the specified name. Typically the
        locale's default should be used. However, there may be names where
        a specific display format is desired for a name. 
        """
        self.display_as = value

    def get_display_as(self):
        """
        Returns the selected display format for the name. The options are
        DEF (default for the current locale), LNFN (last name, first name),
        or FNLN (first name, last name).
        """
        return self.display_as

    def get_surname_prefix(self):
        """
        Returns the prefix (or article) of a surname. The prefix is not
        used for sorting or grouping.
        """
        return self.prefix

    def set_surname_prefix(self,val):
        """
        Sets the prefix (or article) of a surname. Examples of articles
        would be 'de' or 'van'.
        """
        self.prefix = val

    def set_type(self,the_type):
        """sets the type of the Name instance"""
        if not type(the_type) == tuple:
            if the_type in [UNKNOWN,CUSTOM,AKA,BIRTH,MARRIED]:
                warn( "set_type now takes a tuple", DeprecationWarning, 2)
                # Wrapper for old API
                # remove when transitition done.
                the_type = (the_type,'')
            else:
                assert type(the_type) == tuple
        self.type = the_type

    def get_type(self):
        """returns the type of the Name instance"""
        return self.type

    def build_sort_name(self):
        if self.surname:
            self.sname = "%-25s%-30s%s" % (self.surname,self.first_name,self.suffix)
        else:
            self.sname = "@"

    def set_first_name(self,name):
        """sets the given name for the Name instance"""
        self.first_name = name
        self.build_sort_name()

    def set_patronymic(self,name):
        """sets the patronymic name for the Name instance"""
        self.patronymic = name
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

    def get_patronymic(self):
        """returns the patronymic name for the Name instance"""
        return self.patronymic

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

        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix, self.surname, first, self.suffix)
            else:
                return "%s, %s %s" % (self.surname, first, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix,self.surname, first)
            else:
                return "%s, %s" % (self.surname, first)

    def get_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix.upper(), self.surname.upper(), first, self.suffix)
            else:
                return "%s, %s %s" % (self.surname.upper(), first, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix.upper(), self.surname.upper(), first)
            else:
                return "%s, %s" % (self.surname.upper(), first)

    def get_regular_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (first, self.prefix, self.surname)
            else:
                return "%s %s" % (first, self.surname)
        else:
            if self.prefix:
                return "%s %s %s, %s" % (first, self.prefix, self.surname, self.suffix)
            else:
                return "%s %s, %s" % (first, self.surname, self.suffix)

    def is_equal(self,other):
        """
        compares to names to see if they are equal, return 0 if they
        are not
        """
        if self.first_name != other.first_name:
            return False
        if self.surname != other.surname:
            return False
        if self.patronymic != other.patronymic:
            return False
        if self.prefix != other.prefix:
            return False
        if self.suffix != other.suffix:
            return False
        if self.title != other.title:
            return False
        if self.type != other.type:
            return False
        if self.private != other.private:
            return False
        if self.get_note() != other.get_note():
            return False
        if (self.date and other.date and not self.date.is_equal(other.date)) \
                        or (self.date and not other.date) \
                        or (not self.date and other.date):
            return False
        if len(self.get_source_references()) != len(other.get_source_references()):
            return False
        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return True
            index += 1
        return True

#-------------------------------------------------------------------------
#
# Attribute for Person/Family/MediaObject/MediaRef
#
#-------------------------------------------------------------------------
class Attribute(PrivateSourceNote):
    """Provides a simple key/value pair for describing properties. Used
    by the Person and Family objects to store descriptive information."""
    
    UNKNOWN     = -1
    CUSTOM      = 0
    CASTE       = 1
    DESCRIPTION = 2
    ID          = 3
    NATIONAL    = 4
    NUM_CHILD   = 5
    SSN         = 6

    def __init__(self,source=None):
        """creates a new Attribute object, copying from the source if provided"""
        PrivateSourceNote.__init__(self,source)
        
        if source:
            self.type = source.type
            self.value = source.value
        else:
            self.type = (Attribute.CUSTOM,"")
            self.value = ""

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.value]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_type(self,val):
        """sets the type (or key) of the Attribute instance"""
        if not type(val) == tuple:
            warn( "set_type now takes a tuple", DeprecationWarning, 2)
            # Wrapper for old API
            # remove when transitition done.
            if val in range(-1,7):
                val = (val,'')
            else:
                val = (Attribute.CUSTOM,val)
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

#-------------------------------------------------------------------------
#
# Address for Person/Repository
#
#-------------------------------------------------------------------------
class Address(PrivateSourceNote,DateBase):
    """Provides address information for a person"""

    def __init__(self,source=None):
        """Creates a new Address instance, copying from the source
        if provided"""
        PrivateSourceNote.__init__(self,source)
        DateBase.__init__(self,source)

        if source:
            self.street = source.street
            self.city = source.city
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
            self.street = ""
            self.city = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.phone = ""

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.street,self.city,self.state,self.country,
                self.postal,self.phone]
        #return [self.street,self.city,self.state,self.country,
        #        self.postal,self.phone,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

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

    def set_country(self,val):
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

#-------------------------------------------------------------------------
#
# Url for Person/Place/Repository
#
#-------------------------------------------------------------------------
class Url(BaseObject,PrivacyBase):
    """Contains information related to internet Uniform Resource Locators,
    allowing gramps to store information about internet resources"""

    UNKNOWN    = -1
    CUSTOM     = 0
    EMAIL      = 1
    WEB_HOME   = 2
    WEB_SEARCH = 3
    WEB_FTP    = 4
    
    def __init__(self,source=None):
        """creates a new URL instance, copying from the source if present"""
        BaseObject.__init__(self)
        PrivacyBase.__init__(self,source)
        if source:
            self.path = source.path
            self.desc = source.desc
            self.type = source.type
        else:
            self.path = ""
            self.desc = ""
            self.type = (Url.CUSTOM,"")

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.path,self.desc]

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

    def set_type(self,the_type):
        """
        @param type: descriptive type of the Url
        @type type: str
        """
        if not type(the_type) == tuple:
            warn( "set_type now takes a tuple", DeprecationWarning, 2)
            # Wrapper for old API
            # remove when transitition done.
            if the_type in range(-1,5):
                the_type = (the_type,'')
            else:
                the_type = (Url.CUSTOM,the_type)
        self.type = the_type

    def get_type(self):
        """
        @returns: the descriptive type of the Url
        @rtype: str
        """
        return self.type

    def are_equal(self,other):
        """returns 1 if the specified URL is the same as the instance"""
        if other == None:
            return 0
        if self.path != other.path:
            return 0
        if self.desc != other.desc:
            return 0
        if self.type != other.type:
            return 0
        return 1

#-------------------------------------------------------------------------
#
# Location class for Places
#
#-------------------------------------------------------------------------
class Location(BaseObject):
    """
    Provides information about a place.

    The data including city, county, state, and country.
    Multiple Location objects can represent the same place, since names
    of citys, countys, states, and even countries can change with time.
    """
    
    def __init__(self,source=None):
        """
        Creates a Location object, copying from the source object if it exists.
        """

        BaseObject.__init__(self)
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

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.city,self.parish,self.county,self.state,
                self.country,self.postal,self.phone]

    def is_empty(self):
        return not self.city and not self.county and not self.state and \
               not self.country and not self.postal and not self.phone
        
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

#-------------------------------------------------------------------------
#
# LDS Ordinance class
#
#-------------------------------------------------------------------------
class LdsOrd(SourceNote,DateBase,PlaceBase):
    """
    Class that contains information about LDS Ordinances. LDS
    ordinances are similar to events, but have very specific additional
    information related to data collected by the Church of Jesus Christ
    of Latter Day Saints (Morman church). The LDS church is the largest
    source of genealogical information in the United States.
    """
    def __init__(self,source=None):
        """Creates a LDS Ordinance instance"""
        SourceNote.__init__(self,source)
        DateBase.__init__(self,source)
        PlaceBase.__init__(self,source)
        
        if source:
            self.famc = source.famc
            self.temple = source.temple
            self.status = source.status
        else:
            self.famc = None
            self.temple = ""
            self.status = 0

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.temple]
        #return [self.temple,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.place:
            return [('Place',self.place)]
        else:
            return []

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_family_handle(self,family):
        """Sets the Family database handle associated with the LDS ordinance"""
        self.famc = family

    def get_family_handle(self):
        """Gets the Family database handle associated with the LDS ordinance"""
        return self.famc

    def set_status(self,val):
        """
        Sets the status of the LDS ordinance. The status is a text string
        that matches a predefined set of strings."""
        self.status = val

    def get_status(self):
        """Gets the status of the LDS ordinance"""
        return self.status

    def set_temple(self,temple):
        """Sets the temple assocated with the ordinance"""
        self.temple = temple

    def get_temple(self):
        """Gets the temple assocated with the ordinance"""
        return self.temple

    def is_empty(self):
        """Returns 1 if the ordidance is actually empty"""
        if (self.famc or 
                (self.date and not self.date.is_empty()) or 
                self.temple or 
                self.status or 
                self.place):
            return False
        else:
            return True
        
    def are_equal(self,other):
        """returns 1 if the specified ordinance is the same as the instance"""
        if other == None:
            return self.is_empty()
        if (self.famc != other.famc or
            self.place != other.place or
            self.status != other.status or
            self.temple != other.temple or
            not self.get_date_object().is_equal(other.get_date_object()) or
            len(self.get_source_references()) != len(other.get_source_references())):
            return False

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return False
            index += 1
        return True

#-------------------------------------------------------------------------
#
# Event References for Person/Family
#
#-------------------------------------------------------------------------
class EventRef(BaseObject,PrivacyBase,NoteBase):
    """
    Event reference class.

    This class is for keeping information about how the person relates
    to the refereneced event.
    """

    UNKNOWN   = -1
    CUSTOM    = 0
    PRIMARY   = 1
    CLERGY    = 2
    CELEBRANT = 3
    AIDE      = 4
    BRIDE     = 5
    GROOM     = 6
    WITNESS   = 7
    FAMILY    = 8

    def __init__(self,source=None):
        """
        Creates a new EventRef instance, copying from the source if present.
        """
        PrivacyBase.__init__(self)
        NoteBase.__init__(self)
        if source:
            self.ref = source.ref
            self.role = source.role_int
        else:
            self.ref = None
            self.role = (EventRef.CUSTOM,"")

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.role_str]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        if self.note:
            return [self.note]
        return []

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Event',self.ref)]
        else:
            return []

    def get_reference_handle(self):
        """
        Returns the handle of the referred Event object.
        """
        return self.ref

    def set_reference_handle(self,handle):
        """
        Sets the handle of the referred Event object.
        """
        self.ref = handle

    def get_role(self):
        """
        Returns the tuple corresponding to the preset role.
        """
        return self.role

    def set_role(self,role):
        """
        Sets the role according to the given argument.
        """
        if not type(role) == tuple:
            if role in range(-1,9):
                warn( "set_role now takes a tuple", DeprecationWarning, 2)
                # Wrapper for old API
                # remove when transitition done.
                role = (role,'')
            else:
                assert type(role) == tuple
        self.role = role

#-------------------------------------------------------------------------
#
# Source References for all primary objects
#
#-------------------------------------------------------------------------
class SourceRef(BaseObject,DateBase,PrivacyBase,NoteBase):
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    CONF_VERY_HIGH = 4
    CONF_HIGH      = 3
    CONF_NORMAL    = 2
    CONF_LOW       = 1
    CONF_VERY_LOW  = 0

    def __init__(self,source=None):
        """creates a new SourceRef, copying from the source if present"""
        BaseObject.__init__(self)
        DateBase.__init__(self,source)
        PrivacyBase.__init__(self,source)
        NoteBase.__init__(self,source)
        if source:
            self.confidence = source.confidence
            self.ref = source.ref
            self.page = source.page
            self.text = source.text
        else:
            self.confidence = SourceRef.CONF_NORMAL
            self.ref = None
            self.page = ""
            self.note = Note()
            self.text = ""

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.page,self.text]
        #return [self.page,self.text,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        return [self.note]

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Source',self.ref)]
        else:
            return []

    def set_confidence_level(self,val):
        """Sets the confidence level"""
        self.confidence = val

    def get_confidence_level(self):
        """Returns the confidence level"""
        return self.confidence
        
    def set_base_handle(self,ref):
        """sets the Source instance to which the SourceRef refers"""
        self.ref = ref

    def get_base_handle(self):
        """returns the Source instance to which the SourceRef refers"""
        return self.ref
    
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

    def are_equal(self,other):
        """returns True if the passed SourceRef is equal to the current"""
        if self.ref and other.ref:
            if self.page != other.page:
                return False
            if not self.get_date_object().is_equal(other.get_date_object()):
                return False
            if self.get_text() != other.get_text():
                return False
            if self.get_note() != other.get_note():
                return False
            if self.confidence != other.confidence:
                return False
            return True
        elif not self.ref and not other.ref:
            return True
        else:
            return False

#-------------------------------------------------------------------------
#
# MediaObject References for Person/Place/Source
#
#-------------------------------------------------------------------------
class MediaRef(PrivateSourceNote,AttributeBase):
    """Media reference class"""
    def __init__(self,source=None):

        PrivateSourceNote.__init__(self,source)
        AttributeBase.__init__(self,source)

        if source:
            self.ref = source.ref
            self.rect = source.rect
        else:
            self.ref = None
            self.rect = None

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.attribute_list + self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return self.attribute_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('MediaObject',self.ref)]
        else:
            return []

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.attribute_list + self.source_list

    def set_rectangle(self,coord):
        """Sets subection of an image"""
        self.rect = coord

    def get_rectangle(self):
        """Returns the subsection of an image"""
        return self.rect

    def set_reference_handle(self,obj_id):
        self.ref = obj_id

    def get_reference_handle(self):
        return self.ref

class RepoRef(BaseObject,NoteBase):
    """
    Repository reference class.
    """

    UNKNOWN    = -1
    CUSTOM     = 0
    AUDIO      = 1
    BOOK       = 2
    CARD       = 3
    ELECTRONIC = 4
    FICHE      = 5
    FILM       = 6
    MAGAZINE   = 7
    MANUSCRIPT = 8
    MAP        = 9
    NEWSPAPER  = 10
    PHOTO      = 11
    TOMBSTONE  = 12
    VIDEO      = 13

    def __init__(self,source=None):
        NoteBase.__init__(self)
        if source:
            self.ref = source.ref
            self.call_number = source.call_number
            self.media_type = source.media_type
        else:
            self.ref = None
            self.call_number = ""
            self.media_type = (RepoRef.CUSTOM,"")

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.call_number,self.media_type[1]]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        if self.note:
            return [self.note]
        return []

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Repository',self.ref)]
        else:
            return []

    def set_reference_handle(self,ref):
        self.ref = ref

    def get_reference_handle(self):
        return self.ref

    def set_call_number(self,number):
        self.call_number = number

    def get_call_number(self):
        return self.call_number

    def get_media_type(self):
        return self.media_type

    def set_media_type(self,media_type):
       self.media_type = media_type

