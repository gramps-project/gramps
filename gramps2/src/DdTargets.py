# -*- python -*-
# -*- coding: utf-8 -*-
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
   This module provides management of all the drag and drop target information
   required by gramps widgets.

   Adding a new drag and drop target.
   ==================================

   To add a new target: add a new _DdType to in _DdTargets.__init__ and
   then add this new type to the list returned from either all_text_types()
   and all_text_targets() or  or all_gramps_targets() and all_gramps_types().

   Usage
   =====

   The module defines a singleton instance of _DdTargets called DdTargets.

   from DdTargets import DdTargets

   drag_dest_set(gtk.DEST_DEFAULT_ALL,
                 DdTargets.all_targets(),
                 ACTION_COPY)
   
"""

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DdTargets")


class _DdType:
    """Represents the fields needed by a drag and drop traget."""
    
    _APP_ID_OFFSET = 40  # Starting value of app_ids
    
    def __init__(self,container,drag_type,target_flags=0,app_id=None):
        """Create a new DdType:

        drag_type: string holding the name of the type.
        target_flags: int value that will be passed to drop target.
        app_id: integer target id passed to drop target.
        """
        
        self.drag_type = drag_type
        self.target_flags = target_flags
        self.app_id = app_id or self._calculate_id()
        container.insert(self)

    def _calculate_id(self):
        """return the next available app_id."""
        
        idval = _DdType._APP_ID_OFFSET
        _DdType._APP_ID_OFFSET += 1
        return idval

    def target(self):
        """return the full target information in the format
        required by the Gtk functions."""
        return (self.drag_type,self.target_flags,self.app_id)
        
        

class _DdTargets(object):
    """A single class that manages all the drag and drop targets."""
    
    _instance = None # Singleton instance

    def __new__(cls):
        """Ensure that we never have more than one instance."""
        
        if _DdTargets._instance:
            return _DdTargets._instance
        _DdTargets._instance = object.__new__(cls)
        return _DdTargets._instance        

    def __init__(self):
        """Set up the drag and drop targets."""
        
        self._type_map = {}
        self._app_id_map = {}
        
        self.URL       = _DdType(self,'url')
        self.EVENT     = _DdType(self,'pevent')
        self.EVENTREF  = _DdType(self,'eventref')
        self.ATTRIBUTE = _DdType(self,'pattr')
        self.ADDRESS   = _DdType(self,'paddr')
        self.LOCATION  = _DdType(self,'location')
        self.SOURCEREF = _DdType(self,'srcref')
        self.REPOREF   = _DdType(self,'reporef')
        self.REPO_LINK = _DdType(self,'repo-link')
        self.PLACE_LINK= _DdType(self,'place-link')
        self.NAME      = _DdType(self,'name')
        self.MEDIAOBJ  = _DdType(self,'mediaobj')
        self.MEDIAREF  = _DdType(self,'mediaref')
        self.DATA      = _DdType(self,'data_tuple')

        self.PERSON_LINK  = _DdType(self,'person-link')
        self.PERSON_LINK_LIST  = _DdType(self,'person-link-list')
        self.PERSONREF  = _DdType(self,'personref')

        self.SOURCE_LINK  = _DdType(self,'source-link')

        self.FAMILY_EVENT     = _DdType(self,'fevent')
        self.FAMILY_ATTRIBUTE = _DdType(self,'fattr')

        # List of all types that are used between
        # gramps widgets but should not be exported
        # to non gramps widgets.
        self._all_gramps_types = [self.URL,
                                  self.EVENT,
                                  self.ATTRIBUTE,
                                  self.ADDRESS,
                                  self.LOCATION,
                                  self.SOURCEREF,
                                  self.EVENTREF,
                                  self.NAME,
                                  self.REPOREF,
                                  self.MEDIAOBJ,
                                  self.MEDIAREF,
                                  self.REPO_LINK,
                                  self.PLACE_LINK,
                                  self.SOURCE_LINK,
                                  self.PERSON_LINK,
                                  self.PERSON_LINK_LIST,
                                  self.PERSONREF]
        
        self.CHILD         = _DdType(self,'child')
        self.SPOUSE        = _DdType(self,'spouse')
        self.TEXT          = _DdType(self,'TEXT',0,1)
        self.TEXT_MIME     = _DdType(self,'text/plain',0,0)
        self.STRING        = _DdType(self,'STRING', 0, 2)
        self.COMPOUND_TEXT = _DdType(self,'COMPOUND_TEXT', 0, 3)
        self.UTF8_STRING   = _DdType(self,'UTF8_STRING', 0, 4)
        self.URI_LIST      = _DdType(self,'text/uri-list', 0, 5)
        self.APP_ROOT      = _DdType(self,'application/x-rootwin-drop', 0, 6)

        # List of all the test types. These are types
        # that can be interpreted as text.
        self._all_text_types = (self.UTF8_STRING,
                                self.TEXT,
                                self.TEXT_MIME,
                                self.STRING,
                                self.COMPOUND_TEXT)

    def insert(self,dd_type):
        """Add a target to the lookup lists. These lists are
        used purely for performance reasons."""
        
        self._type_map[dd_type.drag_type] = dd_type
        self._app_id_map[dd_type.app_id] = dd_type

    def get_dd_type_from_type_name(self,type_name):
        return self._type_map.get(type_name,None)

    def get_dd_type_from_app_id(self,app_id):
        return self._app_id_map.get(app_id,None)

    def is_text_type(self,type_name):
        return type_name in self.all_text_types()

    def all_text(self):
        return self._all_text_types
        
    def all_text_types(self):
        """return a list of all the type names that could be
        used as the type of a string."""
        
        return tuple([t.drag_type for t in self._all_text_types])
    
    def is_gramps_type(self,type_name):
        return type_name in self.all_gramps_types()

    def all_gramps_types(self):
        """return a list of all the type names that are internal
        to gramps."""

        return tuple([t.drag_type for t in self._all_gramps_types])

    def all_text_targets(self):
        """return a list of all the targets that could be used
        for text."""
        
        return tuple([t.target() for t in self._all_text_types])


    def all_gramps_targets(self):
        """return a list off the internal gramps targets."""

        return tuple([t.target() for t in self._all_gramps_types])

    def all_targets(self):
        """return a list of all the known targets."""
        return self.all_gramps_targets() + self.all_text_targets()

# Create the singleton instance.

DdTargets = _DdTargets()


#
# Below here is test code.
#
if __name__ == "__main__":

    print repr(DdTargets.all_text_types())
    print repr(DdTargets.URL)
    print DdTargets.is_gramps_type('pevent')
