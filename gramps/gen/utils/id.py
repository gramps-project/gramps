#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
Utilities to create unique identifiers
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import random
import time
import uuid

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_UUID

#-------------------------------------------------------------------------
#
# create_id
#
#-------------------------------------------------------------------------
rand = random.Random(time.time())

def create_id():
    return "%08x%08x" % (int(time.time()*10000),
                         rand.randint(0, sys.maxsize))

def create_uid(self, handle=None):
    if handle:
        uid = uuid.uuid5(GRAMPS_UUID, handle)
    else:
        uid = uuid.uuid4()
    return uid.hex.upper()

