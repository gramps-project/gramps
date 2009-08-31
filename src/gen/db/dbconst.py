#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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
Declare constants used by database modules
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
__all__ = (
            ('DBPAGE', 'DBMODE', 'DBCACHE', 'DBLOCKS', 'DBOBJECTS', 'DBUNDO',
             'DBEXT', 'DBMODE_R', 'DBMODE_W', 'DBUNDOFN', 'DBLOCKFN',
             'DBRECOVFN', 'DBLOGNAME', 'DBFLAGS_O',  'DBFLAGS_R', 'DBFLAGS_D',
            ) +
            
            ('PERSON_KEY', 'FAMILY_KEY', 'SOURCE_KEY', 'EVENT_KEY',
             'MEDIA_KEY', 'PLACE_KEY', 'REPOSITORY_KEY', 'NOTE_KEY',
             'REFERENCE_KEY', 'PERSON_COL_KEY', 'FAMILY_COL_KEY',
             'CHILD_COL_KEY'
            ) +

            ('PERSON_COL_KEY', 'FAMILY_COL_KEY', 'CHILD_COL_KEY',
             'PLACE_COL_KEY', 'SOURCE_COL_KEY', 'MEDIA_COL_KEY', 
             'EVENT_COL_KEY', 'REPOSITORY_COL_KEY', 'NOTE_COL_KEY'
            ) +

            ('TXNADD', 'TXNUPD', 'TXNDEL')
          )

DBEXT     = ".db"           # File extension to be used for database files
DBUNDOFN  = "undo.db"       # File name of 'undo' database
DBLOCKFN  = "lock"          # File name of lock file
DBRECOVFN = "need_recover"  # File name of recovery file
DBLOGNAME = ".GrampsDb"     # Name of logger
DBMODE_R  = "r"             # Read-only access
DBMODE_W  = "w"             # Full Reaw/Write access
DBPAGE    = 16384           # Size of the pages used to hold items in the database
DBMODE    = 0666            # Unix mode for database creation
DBCACHE   = 0x4000000       # Size of the shared memory buffer pool
DBLOCKS   = 25000           # Maximum number of locks supported
DBOBJECTS = 25000           # Maximum number of simultaneously locked objects
DBUNDO    = 1000            # Maximum size of undo buffer

from bsddb.db import DB_CREATE, DB_AUTO_COMMIT, DB_DUP, DB_DUPSORT, DB_RDONLY
DBFLAGS_O = DB_CREATE | DB_AUTO_COMMIT  # Default flags for database open
DBFLAGS_R = DB_RDONLY                   # Flags to open a database read-only
DBFLAGS_D = DB_DUP | DB_DUPSORT         # Default flags for duplicate keys

PERSON_KEY     = 0
FAMILY_KEY     = 1
SOURCE_KEY     = 2
EVENT_KEY      = 3
MEDIA_KEY      = 4
PLACE_KEY      = 5
REPOSITORY_KEY = 6
REFERENCE_KEY  = 7
NOTE_KEY       = 8

PERSON_COL_KEY      = 'columns'
CHILD_COL_KEY       = 'child_columns'
PLACE_COL_KEY       = 'place_columns'
SOURCE_COL_KEY      = 'source_columns'
MEDIA_COL_KEY       = 'media_columns'
REPOSITORY_COL_KEY  = 'repository_columns'
EVENT_COL_KEY       = 'event_columns'
FAMILY_COL_KEY      = 'family_columns'
NOTE_COL_KEY        = 'note_columns'

TXNADD, TXNUPD, TXNDEL = 0, 1, 2
