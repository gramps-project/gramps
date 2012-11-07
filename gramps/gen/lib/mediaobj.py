#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
Media object for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
if sys.version_info[0] < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .citationbase import CitationBase
from .notebase import NoteBase
from .datebase import DateBase
from .attrbase import AttributeBase
from .tagbase import TagBase

#-------------------------------------------------------------------------
#
# MediaObject class
#
#-------------------------------------------------------------------------
class MediaObject(CitationBase, NoteBase, DateBase, AttributeBase,
                  TagBase, PrimaryObject):
    """
    Container for information about an image file, including location,
    description and privacy.
    """
    
    def __init__(self, source=None):
        """
        Initialize a MediaObject. 
        
        If source is not None, then object is initialized from values of the 
        source object.

        :param source: Object used to initialize the new object
        :type source: MediaObject
        """
        PrimaryObject.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        AttributeBase.__init__(self, source)
        TagBase.__init__(self)

        if source:
            self.path = source.path
            self.mime = source.mime
            self.desc = source.desc
            self.thumb = source.thumb
        else:
            self.path = ""
            self.mime = ""
            self.desc = ""
            self.thumb = None

    def serialize(self, no_text_date = False):
        """
        Convert the data held in the event to a Python tuple that
        represents all the data elements. 
        
        This method is used to convert the object into a form that can easily 
        be saved to a database.

        These elements may be primitive Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
            be considered persistent.
        :rtype: tuple
        """
        return (self.handle, self.gramps_id, self.path, self.mime, self.desc,
                AttributeBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                self.change,
                DateBase.serialize(self, no_text_date),
                TagBase.serialize(self),
                self.private)

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"handle": self.handle, 
                "gramps_id": self.gramps_id, 
                "path": self.path, 
                "mime": self.mime, 
                "desc": self.desc,
                "attribute_list": AttributeBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "change": self.change,
                "date": DateBase.to_struct(self),
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in an Event structure.

        :param data: tuple containing the persistent data associated the object
        :type data: tuple
        """
        (self.handle, self.gramps_id, self.path, self.mime, self.desc,
         attribute_list, citation_list, note_list, self.change,
         date, tag_list, self.private) = data

        AttributeBase.unserialize(self, attribute_list)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        DateBase.unserialize(self, date)
        TagBase.unserialize(self, tag_list)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.path, self.mime, self.desc, self.gramps_id]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer to citations.

        :returns: Returns the list of child secondary child objects that may 
                refer to citations.
        :rtype: list
        """
        return self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.attribute_list + self.citation_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles() + \
               self.get_referenced_tag_handles()  + \
               self.get_referenced_citation_handles()

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this media object.

        Lost: handle, id, file, date of acquisition.

        :param acquisition: The media object to merge with the present object.
        :rtype acquisition: MediaObject
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_mime_type(self, mime_type):
        """
        Set the MIME type associated with the MediaObject.

        :param mime_type: MIME type to be assigned to the object
        :type mime_type: str
        """
        self.mime = mime_type

    def get_mime_type(self):
        """
        Return the MIME type associated with the MediaObject.

        :returns: Returns the associated MIME type
        :rtype: str
        """
        return self.mime
    
    def set_path(self, path):
        """Set the file path to the passed path."""
        res = urlparse(path)
        if res.scheme == '' or res.scheme == 'file':
            self.path = os.path.normpath(path)
        else:
            # The principal case this path caters for is where the scheme is
            # 'http' or 'https'. It would be possible to do some more extensive
            # checking or processing, but for now we just store the reference
            self.path = path

    def get_path(self):
        """Return the file path."""
        return self.path

    def set_description(self, text):
        """Set the description of the image."""
        self.desc = text

    def get_description(self):
        """Return the description of the image."""
        return self.desc
