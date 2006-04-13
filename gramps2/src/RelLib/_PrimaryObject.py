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
Primary Object class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time
import GrampsLocale

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BaseObject import BaseObject
from _PrivacyBase import PrivacyBase
from _SourceBase import SourceBase
from _MediaBase import MediaBase

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_codeset = GrampsLocale.codeset

#-------------------------------------------------------------------------
#
# Primary Object class
#
#-------------------------------------------------------------------------
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
            return unicode(time.strftime('%x %X',time.localtime(self.change)),
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
        if classname == 'Source' and isinstance(self,SourceBase):
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
        if classname == 'Source' and isinstance(self,SourceBase):
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
        if classname == 'Source' and isinstance(self,SourceBase):
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
