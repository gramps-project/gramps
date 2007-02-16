#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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
This package implements the GrampsDb database. It provides a number
of different backends for different storage mechanisms.

A number of importers and exporters are provided to convert between
the different backend formats.

To obtain a class that implements the backend required you should use the
gramps_db_factory method, likewise for writers use the gramps_db_writer_factory
method and for readers use the gramps_db_reader_factory method. For information
on using these factories see the _GrampsDbFactories.py file comments.

The package also contains GrampsDBCallback which provides signal/slot type
functionality to allow objects to hook into signals that are generated from
the database objects. Read the comments in _GrampsDBCallback.py for more
information.
"""

from _GrampsDbBase import GrampsDbBase

from _GrampsDbFactories import \
     gramps_db_factory

from _GrampsDbExceptions import GrampsDbException, FileVersionError

from _GrampsDBCallback import GrampsDBCallback

from _DbUtils import *

import _GrampsDbConst as GrampsDbConst

from _LongOpStatus import LongOpStatus
from _ProgressMonitor import ProgressMonitor


