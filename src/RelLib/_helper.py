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
The helper classes for GRAMPS objects
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time
import re
import locale

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Date

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_date_format = locale.nl_langinfo(locale.D_T_FMT)
_codeset = locale.nl_langinfo(locale.CODESET)

#-------------------------------------------------------------------------
#
# Base classes
#
#-------------------------------------------------------------------------
class BaseObject:
    """
    The BaseObject is the base class for all data objects in GRAMPS,
    whether primary or not. Its main goal is to provide common capabilites
    to all objects, such as searching through all available information.
    """
    
    def __init__(self):
        """
        Initialize a BaseObject.
        """
        pass
    
    def matches_string(self,pattern,case_sensitive=False):
        """
        Returns True if any text data in the object or any of it's child
        objects matches a given pattern.

        @param pattern: The pattern to match.
        @type pattern: str
        @param case_sensitive: Whether the match is case-sensitive.
        @type case_sensitive: bool
        @return: Returns whether any text data in the object or any of it's child objects matches a given pattern.
        @rtype: bool
        """
        # Run through its own items
        patern_upper = pattern.upper()
        for item in self.get_text_data_list():
            if not item:
                continue
            if case_sensitive:
                if item.find(pattern) != -1:
                    return True
            else:
                if item.upper().find(patern_upper) != -1:
                    return True

        # Run through child objects
        for obj in self.get_text_data_child_list():
            if obj.matches_string(pattern,case_sensitive):
                return True

        return False

    def matches_regexp(self,pattern,case_sensitive=False):
        """
        Returns True if any text data in the object or any of it's child
        objects matches a given regular expression.

        @param pattern: The pattern to match.
        @type pattern: str
        @return: Returns whether any text data in the object or any of it's child objects matches a given regexp.
        @rtype: bool
        """

        # Run through its own items
        if case_sensitive:
            pattern_obj = re.compile(pattern)
        else:
            pattern_obj = re.compile(pattern,re.IGNORECASE)
        for item in self.get_text_data_list():
            if item and pattern_obj.match(item):
                return True

        # Run through child objects
        for obj in self.get_text_data_child_list():
            if obj.matches_regexp(pattern,case_sensitive):
                return True

        return False

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return []

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        return []

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        return []

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects.
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return []

    def get_referenced_handles_recursively(self):
        """
        Returns the list of (classname,handle) tuples for all referenced
        primary objects, whether directly or through child objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = self.get_referenced_handles()
        
        # Run through child objects
        for obj in self.get_handle_referents():
            ret += obj.get_referenced_handles_recursively()

        return ret

class PrivacyBase:
    """
    Base class for privacy-aware objects.
    """

    def __init__(self,source=None):
        """
        Initialize a PrivacyBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PrivacyBase
        """
        
        if source:
            self.private = source.private
        else:
            self.private = False

    def set_privacy(self,val):
        """
        Sets or clears the privacy flag of the data

        @param val: value to assign to the privacy flag. True indicates that the
           record is private, False indicates that it is public.
        @type val: bool
        """
        self.private = val

    def get_privacy(self):
        """
        Returns the privacy level of the data. 

        @returns: True indicates that the record is private
        @rtype: bool
        """
        return self.private

class PrimaryObject(BaseObject,PrivacyBase):
    """
    The PrimaryObject is the base class for all primary objects in the
    database. Primary objects are the core objects in the database.
    Each object has a database handle and a GRAMPS ID value. The database
    handle is used as the record number for the database, and the GRAMPS
    ID is the user visible version.
    """
    
    MARKER_NONE = -1
    MARKER_CUSTOM = 0
    MARKER_COMPLETE = 1
    MARKER_TODO = 2

    def __init__(self,source=None):
        """
        Initialize a PrimaryObject. If source is None, both the ID and handle
        are assigned as empty strings. If source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PrimaryObject
        """
        BaseObject.__init__(self)
        PrivacyBase.__init__(self,source)
        if source:
            self.gramps_id = source.gramps_id
            self.handle = source.handle
            self.change = source.change
            self.marker = source.marker
        else:
            self.gramps_id = None
            self.handle = None
            self.change = 0
            self.marker = (PrimaryObject.MARKER_NONE,"")

    def get_change_time(self):
        """
        Returns the time that the data was last changed. The value
        in the format returned by the time.time() command.
           
        @returns: Time that the data was last changed. The value
           in the format returned by the time.time() command.
        @rtype: int
        """
        return self.change

    def get_change_display(self):
        """
        Returns the string representation of the last change time.

        @returns: string representation of the last change time.
        @rtype: str
        
        """
        if self.change:
            return unicode(time.strftime(_date_format,
                                         time.localtime(self.change)),
                           _codeset)
        else:
            return ''

    def set_handle(self,handle):
        """
        Sets the database handle for the primary object

        @param handle: object database handle
        @type handle: str
        """
        self.handle = handle

    def get_handle(self):
        """
        Returns the database handle for the primary object

        @returns: database handle associated with the object
        @rtype: str
        """
        return self.handle

    def set_gramps_id(self,gramps_id):
        """
        Sets the GRAMPS ID for the primary object
        
        @param gramps_id: GRAMPS ID
        @type gramps_id: str
        """
        self.gramps_id = gramps_id

    def get_gramps_id(self):
        """
        Returns the GRAMPS ID for the primary object

        @returns: GRAMPS ID associated with the object
        @rtype: str
        """
        return self.gramps_id

    def has_handle_reference(self,classname,handle):
        """
        Returns True if the object has reference to a given handle
        of given primary object type.
        
        @param classname: The name of the primary object class.
        @type classname: str
        @param handle: The handle to be checked.
        @type handle: str
        @return: Returns whether the object has reference to this handle of this object type.
        @rtype: bool
        """
        if classname == 'Source' and isinstance(self,SourceNote):
            return self.has_source_reference(handle)
        elif classname == 'MediaObject' and isinstance(self,MediaBase):
            return self.has_media_reference(handle)
        else:
            return self._has_handle_reference(classname,handle)

    def remove_handle_references(self,classname,handle_list):
        """
        Removes all references in this object to object handles in the list.

        @param classname: The name of the primary object class.
        @type classname: str
        @param handle_list: The list of handles to be removed.
        @type handle_list: str
        """
        if classname == 'Source' and isinstance(self,SourceNote):
            self.remove_source_references(handle_list)
        elif classname == 'MediaObject' and isinstance(self,MediaBase):
            self.remove_media_references(handle_list)
        else:
            self._remove_handle_references(classname,handle_list)

    def replace_handle_reference(self,classname,old_handle,new_handle):
        """
        Replaces all references to old handle with those to the new handle.

        @param classname: The name of the primary object class.
        @type classname: str
        @param old_handle: The handle to be replaced.
        @type old_handle: str
        @param new_handle: The handle to replace the old one with.
        @type new_handle: str
        """
        if classname == 'Source' and isinstance(self,SourceNote):
            self.replace_source_references(old_handle,new_handle)
        elif classname == 'MediaObject' and isinstance(self,MediaBase):
            self.replace_media_references(old_handle,new_handle)
        else:
            self._replace_handle_reference(classname,old_handle,new_handle)

    def _has_handle_reference(self,classname,handle):
        return False

    def _remove_handle_references(self,classname,handle_list):
        pass

    def _replace_handle_reference(self,classname,old_handle,new_handle):
        pass
        
    def set_marker(self,marker):
        self.marker = marker
    
    def get_marker(self):
        return self.marker
    
class NoteBase:
    """
    Base class for storing notes.
    """
    def __init__(self,source=None):
        """
        Create a new NoteBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: NoteBase
        """
        
        if source and source.note:
            self.note = Note(source.note.get())
        else:
            self.note = None

    def set_note(self,text):
        """
        Assigns the specified text to the associated note.

        @param text: Text of the note
        @type text: str
        """
        if not self.note:
            self.note = Note()
        self.note.set(text)

    def get_note(self):
        """
        Returns the text of the current note.

        @returns: the text of the current note
        @rtype: str
        """
        if self.note:
            return self.note.get()
        return ""

    def set_note_format(self,val):
        """
        Sets the note's format to the given value. The format indicates
        whether the text is flowed (wrapped) or preformatted.

        @param val: True indicates the text is flowed
        @type val: bool
        """
        if self.note:
            self.note.set_format(val)

    def get_note_format(self):
        """
        Returns the current note's format

        @returns: True indicates that the note should be flowed (wrapped)
        @rtype: bool
        """
        if self.note == None:
            return False
        else:
            return self.note.get_format()

    def set_note_object(self,note_obj):
        """
        Replaces the current L{Note} object associated with the object

        @param note_obj: New L{Note} object to be assigned
        @type note_obj: L{Note}
        """
        self.note = note_obj

    def get_note_object(self):
        """
        Returns the L{Note} instance associated with the object.

        @returns: L{Note} object assocated with the object
        @rtype: L{Note}
        """
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

class SourceNote(BaseObject,NoteBase):
    """
    Base class for storing source references and notes
    """
    
    def __init__(self,source=None):
        """
        Create a new SourceNote, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: SourceNote
        """
        BaseObject.__init__(self)
        NoteBase.__init__(self,source)
        if source:
            self.source_list = [SourceRef(sref) for sref in source.source_list]
        else:
            self.source_list = []

    def add_source_reference(self,src_ref) :
        """
        Adds a source reference to this object.

        @param src_ref: The source reference to be added to the
            SourceNote's list of source references.
        @type src_ref: L{SourceRef}
        """
        self.source_list.append(src_ref)

    def get_source_references(self) :
        """
        Returns the list of source references associated with the object.

        @return: Returns the list of L{SourceRef} objects assocated with
            the object.
        @rtype: list
        """
        return self.source_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return []

    def has_source_reference(self,src_handle) :
        """
        Returns True if the object or any of it's child objects has reference
        to this source handle.

        @param src_handle: The source handle to be checked.
        @type src_handle: str
        @return: Returns whether the object or any of it's child objects has reference to this source handle.
        @rtype: bool
        """
        for src_ref in self.source_list:
            # Using direct access here, not the getter method -- efficiency!
            if src_ref.ref == src_handle:
                return True

        for item in self.get_sourcref_child_list():
            if item.has_source_reference(src_handle):
                return True

        return False

    def remove_source_references(self,src_handle_list):
        """
        Removes references to all source handles in the list
        in this object and all child objects.

        @param src_handle_list: The list of source handles to be removed.
        @type src_handle_list: list
        """
        new_source_list = [ src_ref for src_ref in self.source_list \
                                    if src_ref.ref not in src_handle_list ]
        self.source_list = new_source_list

        for item in self.get_sourcref_child_list():
            item.remove_source_references(src_handle_list)

    def replace_source_references(self,old_handle,new_handle):
        """
        Replaces references to source handles in the list
        in this object and all child objects.

        @param old_handle: The source handle to be replaced.
        @type old_handle: str
        @param new_handle: The source handle to replace the old one with.
        @type new_handle: str
        """
        refs_list = [ src_ref.ref for src_ref in self.source_list ]
        n_replace = refs_list.count(old_handle)
        for ix_replace in xrange(n_replace):
            ix = refs_list.index(old_handle)
            self.source_list[ix].ref = new_handle
            refs_list[ix] = new_handle
            
        for item in self.get_sourcref_child_list():
            item.replace_source_references(old_handle,new_handle)

    def set_source_reference_list(self,src_ref_list) :
        """
        Assigns the passed list to the object's list of source references.

        @param src_ref_list: List of source references to ba associated
            with the object
        @type src_ref_list: list of L{SourceRef} instances
        """
        self.source_list = src_ref_list

class MediaBase:
    """
    Base class for storing media references
    """
    
    def __init__(self,source=None):
        """
        Create a new MediaBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: MediaBase
        """
        
        if source:
            self.media_list = [ MediaRef(mref) for mref in source.media_list ]
        else:
            self.media_list = []

    def add_media_reference(self,media_ref):
        """
        Adds a L{MediaRef} instance to the object's media list.

        @param media_ref: L{MediaRef} instance to be added to the object's
            media list.
        @type media_ref: L{MediaRef}
        """
        self.media_list.append(media_ref)

    def get_media_list(self):
        """
        Returns the list of L{MediaRef} instances associated with the object.

        @returns: list of L{MediaRef} instances associated with the object
        @rtype: list
        """
        return self.media_list

    def set_media_list(self,media_ref_list):
        """
        Sets the list of L{MediaRef} instances associated with the object.
        It replaces the previous list.

        @param media_ref_list: list of L{MediaRef} instances to be assigned
            to the object.
        @type media_ref_list: list
        """
        self.media_list = media_ref_list

    def has_media_reference(self,obj_handle) :
        """
        Returns True if the object or any of it's child objects has reference
        to this media object handle.

        @param obj_handle: The media handle to be checked.
        @type obj_handle: str
        @return: Returns whether the object or any of it's child objects has reference to this media handle.
        @rtype: bool
        """
        return obj_handle in [media_ref.ref for media_ref in self.media_list]

    def remove_media_references(self,obj_handle_list):
        """
        Removes references to all media handles in the list.

        @param obj_handle_list: The list of media handles to be removed.
        @type obj_handle_list: list
        """
        new_media_list = [ media_ref for media_ref in self.media_list \
                                    if media_ref.ref not in obj_handle_list ]
        self.media_list = new_media_list

    def replace_media_references(self,old_handle,new_handle):
        """
        Replaces all references to old media handle with the new handle.

        @param old_handle: The media handle to be replaced.
        @type old_handle: str
        @param new_handle: The media handle to replace the old one with.
        @type new_handle: str
        """
        refs_list = [ media_ref.ref for media_ref in self.media_list ]
        n_replace = refs_list.count(old_handle)
        for ix_replace in xrange(n_replace):
            ix = refs_list.index(old_handle)
            self.media_list[ix].ref = new_handle
            refs_list[ix] = new_handle

class DateBase:
    """
    Base class for storing date information.
    """

    def __init__(self,source=None):
        """
        Create a new DateBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: DateBase
        """
        if source:
            self.date = Date.Date(source.date)
        else:
            self.date = None

#     def set_date(self, date) :
#         """
#         Sets the date of the DateBase instance.
        
#         The date is parsed into a L{Date} instance.

#         @param date: String representation of a date. The locale specific
#             L{DateParser} is used to parse the string into a GRAMPS L{Date}
#             object.
#         @type date: str
#         """
#         self.date = DateHandler.parser.parse(date)

#     def get_date(self) :
#         """
#         Returns a string representation of the date of the DateBase instance.
        
#         This representation is based off the default date display format
#         determined by the locale's L{DateDisplay} instance.

#         @return: Returns a string representing the DateBase date
#         @rtype: str
#         """
#         if self.date:
#             return DateHandler.displayer.display(self.date)
#         return u""

#     def get_quote_date(self) :
#         """
#         Returns a string representation of the date of the DateBase instance.
        
#         This representation is based off the default date display format
#         determined by the locale's L{DateDisplay} instance. The date is
#         enclosed in quotes if the L{Date} is not a valid date.

#         @return: Returns a string representing the DateBase date
#         @rtype: str
#         """
#         if self.date:
#             return DateHandler.displayer.quote_display(self.date)
#         return u""

    def get_date_object(self):
        """
        Returns the L{Date} object associated with the DateBase.

        @return: Returns a DateBase L{Date} instance.
        @rtype: L{Date}
        """
        if not self.date:
            self.date = Date.Date()
        return self.date

    def set_date_object(self,date):
        """
        Sets the L{Date} object associated with the DateBase.

        @param date: L{Date} instance to be assigned to the DateBase
        @type date: L{Date}
        """
        self.date = date

class AttributeBase:
    """
    Base class for attribute-aware objects.
    """

    def __init__(self,source=None):
        """
        Initialize a AttributeBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: AttributeBase
        """
        
        if source:
            self.attribute_list = [ Attribute(attribute) \
                                    for attribute in source.attribute_list ]
        else:
            self.attribute_list = []

    def add_attribute(self,attribute):
        """
        Adds the L{Attribute} instance to the object's list of attributes

        @param attribute: L{Attribute} instance to add.
        @type attribute: L{Attribute}
        """
        self.attribute_list.append(attribute)

    def remove_attribute(self,attribute):
        """
        Removes the specified L{Attribute} instance from the attribute list
        If the instance does not exist in the list, the operation has
        no effect.

        @param attribute: L{Attribute} instance to remove from the list
        @type attribute: L{Attribute}

        @return: True if the attribute was removed, False if it was not
            in the list.
        @rtype: bool
        """
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)
            return True
        else:
            return False

    def get_attribute_list(self):
        """
        Returns the list of L{Attribute} instances associated with the object.
        
        @returns: Returns the list of L{Attribute} instances.
        @rtype: list
        """
        return self.attribute_list

    def set_attribute_list(self,attribute_list):
        """
        Assigns the passed list to the Person's list of L{Attribute} instances.

        @param attribute_list: List of L{Attribute} instances to ba associated
            with the Person
        @type attribute_list: list
        """
        self.attribute_list = attribute_list

class AddressBase:
    """
    Base class for address-aware objects.
    """

    def __init__(self,source=None):
        """
        Initialize a AddressBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: AddressBase
        """
        
        if source:
            self.address_list = [ Address(address) \
                                    for address in source.address_list ]
        else:
            self.address_list = []

    def add_address(self,address):
        """
        Adds the L{Address} instance to the object's list of addresses

        @param address: L{Address} instance to add to the object's address list
        @type address: list
        """
        self.address_list.append(address)

    def remove_address(self,address):
        """
        Removes the specified L{Address} instance from the address list
        If the instance does not exist in the list, the operation has
        no effect.

        @param address: L{Address} instance to remove from the list
        @type address: L{Address}

        @return: True if the address was removed, False if it was not in the list.
        @rtype: bool
        """
        if address in self.address_list:
            self.address_list.remove(address)
            return True
        else:
            return False

    def get_address_list(self):
        """
        Returns the list of L{Address} instances associated with the object

        @return: Returns the list of L{Address} instances
        @rtype: list
        """
        return self.address_list

    def set_address_list(self,address_list):
        """
        Assigns the passed list to the object's list of L{Address} instances.
        @param address_list: List of L{Address} instances to be associated
            with the object
        @type address_list: list
        """
        self.address_list = address_list

class UrlBase:
    """
    Base class for url-aware objects.
    """

    def __init__(self,source=None):
        """
        Initialize an UrlBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: UrlBase
        """
        
        if source:
            self.urls = [ Url(url) for url in source.urls ]
        else:
            self.urls = []

    def get_url_list(self):
        """
        Returns the list of L{Url} instances associated with the object.

        @returns: List of L{Url} instances
        @rtype: list
        """
        return self.urls

    def set_url_list(self,url_list):
        """
        Sets the list of L{Url} instances to passed the list.

        @param url_list: List of L{Url} instances
        @type url_list: list
        """
        self.urls = url_list

    def add_url(self,url):
        """
        Adds a L{Url} instance to the object's list of L{Url} instances

        @param url: L{Url} instance to be added to the Person's list of
            related web sites.
        @type url: L{Url}
        """
        self.urls.append(url)
    

    def remove_url(self,url):
        """
        Removes the specified L{Url} instance from the url list
        If the instance does not exist in the list, the operation has
        no effect.

        @param attribute: L{Url} instance to remove from the list
        @type attribute: L{Url}

        @return: True if the url was removed, False if it was not in the list.
        @rtype: bool
        """
        if url in self.urls:
            self.urls.remove(url)
            return True
        else:
            return False

class PlaceBase:
    """
    Base class for place-aware objects.
    """
    def __init__(self,source=None):
        """
        Initialize a PlaceBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PlaceBase
        """
        if source:
            self.place = source.place
        else:
            self.place = ""

    def set_place_handle(self,place_handle):
        """
        Sets the database handle for L{Place} associated with the object.

        @param place_handle: L{Place} database handle
        @type place_handle: str
        """
        self.place = place_handle

    def get_place_handle(self):
        """
        Returns the database handle of the L{Place} assocated with
        the Event.

        @returns: L{Place} database handle
        @rtype: str
        """
        return self.place 

class PrivateSourceNote(SourceNote,PrivacyBase):
    """
    Same as SourceNote, plus the privacy capabilities.
    """
    def __init__(self,source=None):
        """
        Initialize a PrivateSourceNote. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PrivateSourceNote
        """
        SourceNote.__init__(self,source)
        PrivacyBase.__init__(self,source)

class LocationBase:
    """
    Base class for all things Address.
    """
    
    def __init__(self,source=None):
        """
        Creates a LocationBase object,
        copying from the source object if it exists.
        """
        if source:
            self.city = source.city
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
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
        return [self.city,self.state,self.country,self.postal,self.phone]

    def set_city(self,data):
        """sets the city name of the LocationBase object"""
        self.city = data

    def get_city(self):
        """returns the city name of the LocationBase object"""
        return self.city

    def set_postal_code(self,data):
        """sets the postal code of the LocationBase object"""
        self.postal = data

    def get_postal_code(self):
        """returns the postal code of the LocationBase object"""
        return self.postal

    def set_phone(self,data):
        """sets the phone number of the LocationBase object"""
        self.phone = data

    def get_phone(self):
        """returns the phone number of the LocationBase object"""
        return self.phone

    def set_state(self,data):
        """sets the state name of the LocationBase object"""
        self.state = data

    def get_state(self):
        """returns the state name of the LocationBase object"""
        return self.state

    def set_country(self,data):
        """sets the country name of the LocationBase object"""
        self.country = data

    def get_country(self):
        """returns the country name of the LocationBase object"""
        return self.country

class Witness(BaseObject,PrivacyBase):
    # FIXME: this class is only present to enable db upgrade
    def __init__(self):
        pass
