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
Primary Object class for GRAMPS
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
from _BasicPrimaryObject import BasicPrimaryObject
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
class PrimaryObject(BasicPrimaryObject):
    """
    The PrimaryObject is the base class for all primary objects in the
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
        BasicPrimaryObject.__init__(self, source)

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
        if classname == 'Source' and isinstance(self, SourceBase):
            return self.has_source_reference(handle)
        elif classname == 'MediaObject' and isinstance(self, MediaBase):
            return self.has_media_reference(handle)
        else:
            return self._has_handle_reference(classname, handle)

    def remove_handle_references(self, classname, handle_list):
        """
        Removes all references in this object to object handles in the list.

        @param classname: The name of the primary object class.
        @type classname: str
        @param handle_list: The list of handles to be removed.
        @type handle_list: str
        """
        if classname == 'Source' and isinstance(self, SourceBase):
            self.remove_source_references(handle_list)
        elif classname == 'MediaObject' and isinstance(self, MediaBase):
            self.remove_media_references(handle_list)
        else:
            self._remove_handle_references(classname, handle_list)

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
        if classname == 'Source' and isinstance(self, SourceBase):
            self.replace_source_references(old_handle, new_handle)
        elif classname == 'MediaObject' and isinstance(self, MediaBase):
            self.replace_media_references(old_handle, new_handle)
        else:
            self._replace_handle_reference(classname, old_handle, new_handle)

    def _has_handle_reference(self, classname, handle):
        """
        returns True if the handle is referenced by the object
        """
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        removes the handle references from the object
        """
        pass

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        replaces the handle reference with the new reference
        """
        pass
        
    def set_marker(self, marker):
        self.marker.set(marker)
    
    def get_marker(self):
        return self.marker
