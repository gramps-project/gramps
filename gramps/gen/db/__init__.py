#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Gramps Database API.

Database Architecture
=====================

Access to the database is made through Python classes. Exactly
what functionality you have is dependent on the properties of the
database. For example, if you are accessing a read-only view, then
you will only have access to a subset of the methods available.

At the root of any database interface is either :py:class:`.DbReadBase` and/or
:py:class:`.DbWriteBase`. These define the methods to read and write to a
database, respectively.

The full database hierarchy is:

- :py:class:`.DbBsddb` - read and write implementation to BSDDB databases

  * :py:class:`.DbWriteBase` - virtual and implementation-independent methods
    for reading data

  * :py:class:`.DbBsddbRead` - read-only (accessors, getters) implementation
    to BSDDB databases

    + :py:class:`.DbReadBase` - virtual and implementation-independent
      methods for reading data

    + :py:class:`.Callback` - callback and signal functions

  * :py:class:`.UpdateCallback` - callback functionality

- :py:class:`.DbDjango` - read and write implementation to Django-based
  databases

  * :py:class:`.DbWriteBase` - virtual and implementation-independent methods
    for reading data

  * :py:class:`.DbReadBase` - virtual and implementation-independent methods
    for reading data

DbBsddb
=======

The :py:class:`.DbBsddb` interface defines a hierarchical database
(non-relational) written in
`PyBSDDB <http://www.jcea.es/programacion/pybsddb.htm>`_. There is no
such thing as a database schema, and the meaning of the data is
defined in the Python classes above. The data is stored as pickled
tuples and unserialized into the primary data types (below).

DbDjango
========

The DbDjango interface defines the Gramps data in terms of
*models* and *relations* from the
`Django project <http://www.djangoproject.com/>`_. The database
backend can be any implementation that supports Django, including
such popular SQL implementations as sqlite, MySQL, Postgresql, and
Oracle. The data is retrieved from the SQL fields, serialized and
then unserialized into the primary data types (below).

More details can be found in the manual's
`Using database API <http://www.gramps-project.org/wiki/index.php?title=Using_database_API>`_.
"""

from .base import *
from .dbconst import *
from .txn import *
from .exceptions import *
from .undoredo import *

def find_surname_name(key, data):
    """
    Creating a surname from raw name, to use for sort and index
    returns a byte string
    """
    return __index_surname(data[5])

def __index_surname(surn_list):
    """
    All non pa/matronymic surnames are used in indexing.
    pa/matronymic not as they change for every generation!
    returns a byte string
    """
    from gramps.gen.lib import NameOriginType
    if surn_list:
        surn = " ".join([x[0] for x in surn_list if not (x[3][0] in [
                    NameOriginType.PATRONYMIC, NameOriginType.MATRONYMIC]) ])
    else:
        surn = ""
    return surn

def open_database(database, force_unlock=False):
    """
    Shortcut for external uses of databases.
    """
    from ..dbstate import DbState
    return DbState().open_database(database, force_unlock)

def make_database(dbid):
    """
    Shortcut for external uses of databases.
    """
    from ..dbstate import DbState
    return DbState().make_database(dbid)
