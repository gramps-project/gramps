#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Declare constants used by database modules
"""

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
__all__ = (
            ('DBPAGE', 'DBMODE', 'DBCACHE', 'DBLOCKS', 'DBOBJECTS', 'DBUNDO',
             'DBEXT', 'DBMODE_R', 'DBMODE_W', 'DBUNDOFN', 'DBLOCKFN',
             'DBRECOVFN','BDBVERSFN', 'DBLOGNAME', 'SCHVERSFN', 'PCKVERSFN',
             'DBBACKEND'
            ) +
            
            ('PERSON_KEY', 'FAMILY_KEY', 'SOURCE_KEY', 'CITATION_KEY',
             'EVENT_KEY', 'MEDIA_KEY', 'PLACE_KEY', 'REPOSITORY_KEY',
             'NOTE_KEY', 'REFERENCE_KEY', 'TAG_KEY'
            ) +

            ('TXNADD', 'TXNUPD', 'TXNDEL')
          )

DBEXT     = ".db"           # File extension to be used for database files
DBUNDOFN  = "undo.db"       # File name of 'undo' database
DBLOCKFN  = "lock"          # File name of lock file
DBRECOVFN = "need_recover"  # File name of recovery file
BDBVERSFN = "bdbversion.txt"# File name of Berkeley DB version file
DBBACKEND = "database.txt"  # File name of Database backend file
SCHVERSFN = "schemaversion.txt"# File name of schema version file
PCKVERSFN = "pickleupgrade.txt" # Indicator that pickle has been upgrade t Python3
DBLOGNAME = ".Db"           # Name of logger
DBMODE_R  = "r"             # Read-only access
DBMODE_W  = "w"             # Full Read/Write access
DBPAGE    = 16384           # Size of the pages used to hold items in the database
DBMODE    = 0o666            # Unix mode for database creation
DBCACHE   = 0x4000000       # Size of the shared memory buffer pool
DBLOCKS   = 100000          # Maximum number of locks supported
DBOBJECTS = 100000          # Maximum number of simultaneously locked objects
DBUNDO    = 1000            # Maximum size of undo buffer

PERSON_KEY     = 0
FAMILY_KEY     = 1
SOURCE_KEY     = 2
EVENT_KEY      = 3
MEDIA_KEY      = 4
PLACE_KEY      = 5
REPOSITORY_KEY = 6
REFERENCE_KEY  = 7
NOTE_KEY       = 8
TAG_KEY        = 9
CITATION_KEY   = 10

TXNADD, TXNUPD, TXNDEL = 0, 1, 2
