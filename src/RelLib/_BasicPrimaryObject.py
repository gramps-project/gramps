#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007 Donald N. Allingham
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
Basic Primary Object class for GRAMPS
"""

__revision__ = "$Revision$"

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
from _MarkerType import MarkerType

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
CODESET = GrampsLocale.codeset

#-------------------------------------------------------------------------
#
# Basic Primary Object class
#
#-------------------------------------------------------------------------
class BasicPrimaryObject(BaseObject, PrivacyBase):
    """
    The BasicPrimaryObject is the base class for Note objects.
    It is also the base class for the PrimaryObject class.    
    
    The PrimaryObject is the base class for all other primary objects in the
    database. Primary objects are the core objects in the database.
    Each object has a database handle and a GRAMPS ID value. The database
    handle is used as the record number for the database, and the GRAMPS
    ID is the user visible version.
    """
    
    def __init__(self, source=None):
        """
        Initialize a PrimaryObject. If source is None, both the ID and handle
        are assigned as empty strings. If source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PrimaryObject
        """
        BaseObject.__init__(self)
        PrivacyBase.__init__(self, source)
        if source:
            self.gramps_id = source.gramps_id
            self.handle = source.handle
            self.change = source.change
            self.marker = source.marker
        else:
            self.gramps_id = None
            self.handle = None
            self.change = 0
            self.marker = MarkerType()

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
            return unicode(time.strftime('%x %X', time.localtime(self.change)),
                           CODESET)
        else:
            return u''

    def set_handle(self, handle):
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

    def set_gramps_id(self, gramps_id):
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

    def has_handle_reference(self, classname, handle):
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
        return False

    def remove_handle_references(self, classname, handle_list):
        """
        Removes all references in this object to object handles in the list.

        @param classname: The name of the primary object class.
        @type classname: str
        @param handle_list: The list of handles to be removed.
        @type handle_list: str
        """
        pass

    def replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replaces all references to old handle with those to the new handle.

        @param classname: The name of the primary object class.
        @type classname: str
        @param old_handle: The handle to be replaced.
        @type old_handle: str
        @param new_handle: The handle to replace the old one with.
        @type new_handle: str
        """
        pass

    def set_marker(self, marker):
        """
        Sets the marker for the object.

        @param marker: marker assigned to the object
        @type marker: MarkerType
        """
        self.marker.set(marker)
    
    def get_marker(self):
        """
        Returns the marker for the object. The exact type depends on the
        derived class type.

        @return: Returns the marker for the object.
        @rtype: MarkerType
        """
        return self.marker

    def has_source_reference(self, handle):
        """
        Indicates if the object has a source references. In the base class,
        no such references exist. Derived classes should override this if they
        provide source references.
        """
        return False

    def has_media_reference(self, handle):
        """
        Indicates if the object has a media references. In the base class,
        no such references exist. Derived classes should override this if they
        provide media references.
        """
        return False

    def remove_source_references(self, handle_list):
        """
        Removes the specified source references from the object. In the base class
        no such references exist. Derived classes should override this if they
        provide source references.
        """
        pass

    def remove_media_references(self, handle_list):
        """
        Removes the specified media references from the object. In the base class
        no such references exist. Derived classes should override this if they
        provide media references.
        """
        pass

    def replace_source_references(self, old_handle, new_handle):
        pass

    def replace_media_references(self, old_handle, new_handle):
        pass
