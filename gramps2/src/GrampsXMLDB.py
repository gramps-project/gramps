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

from RelLib import *
from GrampsDbBase import *

import ReadXML
import WriteXML

_UNDO_SIZE      = 1000

#-------------------------------------------------------------------------
#
# ID regular expression
#
#-------------------------------------------------------------------------
_id_reg = compile("%\d+d")

#-------------------------------------------------------------------------
#
# GrampsXMLDB
#
#-------------------------------------------------------------------------
class GrampsXMLDB(GrampsDbBase):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""
        GrampsDbBase.__init__(self)

    def load(self,name,callback):
        self.person_map = {}
        self.family_map = {}
        self.place_map  = {}
        self.source_map = {}
        self.media_map  = {}
        self.event_map  = {}
        self.metadata   = {}
        self.filename = name
        self.id_trans = {}
        self.eventnames = {}
        self.undodb = []

        ReadXML.importData(self,name)
        
        self.bookmarks = self.metadata.get('bookmarks')
        if self.bookmarks == None:
            self.bookmarks = []
        return 1

    def close(self):
        WriteXML.quick_write(self,self.filename)

    def get_surname_list(self):
        a = {}
        for person_id in self.get_person_handles(sort_handles=False):
            p = self.get_person_from_handle(person_id)
            a[p.get_primary_name().get_surname()] = 1
        vals = a.keys()
        vals.sort()
        return vals

    def get_person_event_type_list(self):
        names = self.eventnames.keys()
        a = {}
        for name in names:
            a[unicode(name)] = 1
        vals = a.keys()
        vals.sort()
        return vals

    def remove_person(self,handle,transaction):
        self.genderStats.uncount_person (self.person_map[handle])
        if transaction != None:
            old_data = self.person_map.get(handle)
            transaction.add(PERSON_KEY,handle,old_data)
        del self.person_map[handle]

    def remove_source(self,handle,transaction):
        if transaction != None:
            old_data = self.source_map.get(str(handle))
            transaction.add(SOURCE_KEY,handle,old_data)
        del self.source_map[str(handle)]

    def remove_family_handle(self,handle,transaction):
        if transaction != None:
            old_data = self.family_map.get(str(handle))
            transaction.add(FAMILY_KEY,handle,old_data)
        del self.family_map[str(handle)]

    def remove_event(self,handle,transaction):
        if transaction != None:
            old_data = self.event_map.get(str(handle))
            transaction.add(EVENT_KEY,handle,old_data)
        del self.event_map[str(handle)]

