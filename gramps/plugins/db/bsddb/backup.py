#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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
# gen/db/backup.py

"""
Description
===========

This module Provides backup and restore functions for a database. The
backup function saves the data into backup files, while the restore
function loads the data back into a database.

You should only restore the data into an empty database.

Implementation
==============

Not all of the database tables need to be backed up, since many are
automatically generated from the others. The tables that are backed up
are the primary tables and the metadata table.

The database consists of a table of "pickled" tuples. Each of the
primary tables is "walked", and the pickled tuple is extracted, and
written to the backup file.

Restoring the data is just as simple. The backup file is parsed an
entry at a time, and inserted into the associated database table. The
derived tables are built automatically as the items are entered into
db.
"""

#-------------------------------------------------------------------------
#
# load standard python libraries
#
#-------------------------------------------------------------------------
import os
import pickle

#------------------------------------------------------------------------
#
# Gramps libs
#
#------------------------------------------------------------------------
from gramps.gen.db.exceptions import DbException
from .write import FAMILY_TBL, PLACES_TBL, SOURCES_TBL, MEDIA_TBL, \
    EVENTS_TBL, PERSON_TBL, REPO_TBL, NOTE_TBL, TAG_TBL, META, CITATIONS_TBL

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".Backup")

