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

# $Id: _SecondaryObject.py 6386 2006-04-21 00:03:27Z rshura $

"""
Secondary Object class for GRAMPS
"""

__revision__ = "$Revision: $"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BaseObject import BaseObject

#-------------------------------------------------------------------------
#
# Secondary Object class
#
#-------------------------------------------------------------------------
class SecondaryObject(BaseObject):
    """
    The SecondaryObject is the base class for all primary objects in the
    database. Secondary objects are the core objects in the database.
    Each object has a database handle and a GRAMPS ID value. The database
    handle is used as the record number for the database, and the GRAMPS
    ID is the user visible version.
    """
    
    def is_equal(self, source):
        return cmp(self.serialize(), source.serialize()) == 0
