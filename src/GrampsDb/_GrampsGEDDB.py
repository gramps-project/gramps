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
of GEDCOM files.
"""

from RelLib import *
from _GrampsInMemDB import *
from _GrampsDbExceptions import GrampsDbException

from _DbUtils import db_copy

#-------------------------------------------------------------------------
#
# GrampsGEDDB
#
#-------------------------------------------------------------------------
class GrampsGEDDB(GrampsInMemDB):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self, use_txn = False):
        """creates a new GrampsDB"""
        GrampsInMemDB.__init__(self)

    def load(self, name, callback, mode="w"):
        if self.db_is_open:
            self.close()
        GrampsInMemDB.load(self,name,callback,mode)

        try:
            from GrampsDbUtils._ReadGedcom import importData
        except:
            log.warning("Failed to load Gedcom reader", exc_info=True)
            raise GrampsDbException("Failed to load Gedcom reader")

        importData(self,name,callback,use_trans=False)

        self.bookmarks = GrampsDbBookmarks(self.metadata.get('bookmarks',[]))
        self.db_is_open = True
        self.readonly = True
        return 1

    def load_from(self, other_database, filename, callback):
        db_copy(other_database,self,callback)
        GrampsInMemDB.load(self,filename,callback)
        self.bookmarks = GrampsDbBookmarks(self.metadata.get('bookmarks',[]))
        self.db_is_open = True

        try:            
            from GrampsDbUtils._WriteGedcom import GedcomWriter
        except:
            log.warning("Failed to load Gedcom writer", exc_info=True)
            raise GrampsDbException("Failed to load Gedcom writer")

        writer = GedcomWriter(self,self.get_default_person(),
                                          callback=callback)
        writer.export_data(self.full_name)
        return 1

    def close(self):
        if not self.db_is_open:
            return

        try:            
            from GrampsDbUtils._WriteGedcom import GedcomWriter
        except:
            log.warning("Failed to load Gedcom writer", exc_info=True)
            raise GrampsDbException("Failed to load Gedcom writer")

        if not self.readonly and len(self.undodb) > 0:
            writer = GedcomWriter(self,self.get_default_person())
            writer.export_data(self.full_name)
        self.db_is_open = False
        GrampsInMemDB.close(self)
