#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Provides the GRAMPS DB interface for supporting in-memory editing
of GRAMPS XML format.
"""

from RelLib import *
from _GrampsInMemDB import *

import _ReadXML as ReadXML
import _WriteXML as WriteXML
from _DbUtils import db_copy

#-------------------------------------------------------------------------
#
# GrampsXMLDB
#
#-------------------------------------------------------------------------
class GrampsXMLDB(GrampsInMemDB):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""
        GrampsInMemDB.__init__(self)

    def load(self,name,callback,mode="w"):
        if self.db_is_open:
            self.close()
        GrampsInMemDB.load(self,name,callback,mode)
        self.id_trans = {}
        
        ReadXML.importData(self,name,callback,use_trans=False)
        
        self.bookmarks = self.metadata.get('bookmarks')
        if self.bookmarks == None:
            self.bookmarks = []
        self.db_is_open = True
        return 1

    def load_from(self, other_database, filename, callback):
        self.id_trans = {}
        db_copy(other_database,self,callback)
        GrampsInMemDB.load(self,filename,callback)
        self.bookmarks = self.metadata.get('bookmarks')
        if self.bookmarks == None:
            self.bookmarks = []
        self.db_is_open = True
        WriteXML.quick_write(self,self.full_name)
        return 1

    def close(self):
        if not self.db_is_open:
            return
        if not self.readonly and len(self.undodb) > 0:
            WriteXML.quick_write(self,self.full_name)
        self.db_is_open = False
