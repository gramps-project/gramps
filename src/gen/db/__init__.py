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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
    Gramps Database API.

    Database Architecture
    =====================

    Access to the database is made through Python classes. Exactly
    what functionality you have is dependent on the properties of the
    database. For example, if you are accessing a read-only view, then
    you will only have access to a subset of the methods available.

    At the root of any database interface is either DbReadBase and/or
    DbWriteBase. These define the methods to read and write to a
    database, respectively.

    The full database hierarchy is:

    - B{DbBsddb} - read and write implementation to BSDDB databases (U{gen/db/write<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/write.py?view=markup>})
        - B{DbWriteBase} - virtual and implementation-independent methods for reading data (U{gen/db/base.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/base.py?view=markup>})
        - B{DbBsddbRead} - read-only (accessors, getters) implementation to BSDDB databases (U{gen/db/read.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/read.py?view=markup})
            - B{DbReadBase} - virtual and implementation-independent methods for reading data (U{gen/db/base.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/base.py?view=markup})
            - B{Callback} - callback and signal functions (U{gen/utils/callback.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/utils/callback.py?view=markup})
        - B{UpdateCallback} - callback functionality (U{gen/updatecallback.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/read.py?view=markup gen/updatecallback.py?view=markup>})
    - B{DbBDjango} - read and write implementation to Django-based databases (U{web/djangodb.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/web/djangodb.py?view=markup})
        - B{DbWriteBase} - virtual and implementation-independent methods for reading data (U{gen/db/base.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/base.py?view=markup})
        - B{DbReadBase} - virtual and implementation-independent methods for reading data (U{gen/db/base.py<http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/src/gen/db/base.py?view=markup})

    DbBsddb
    =======

    The DbBsddb interface defines a hierarchical database
    (non-relational) written in
    U{http://www.jcea.es/programacion/pybsddb.htm PyBSDDB}. There is no
    such thing as a database schema, and the meaning of the data is
    defined in the Python classes above. The data is stored as pickled
    tuples and unserialized into the primary data types (below).

    DbDjango
    ========

    The DbDjango interface defines the Gramps data in terms of
    I{models} and I{relations} from the
    U{Django project<http://www.djangoproject.com/}. The database
    backend can be any implementation that supports Django, including
    such popular SQL implementations as sqlite, MySQL, Postgresql, and
    Oracle. The data is retrieved from the SQL fields, serialized and
    then unserialized into the primary data types (below).

    More details can be found in the manual's U{Using database API<http://www.gramps-project.org/wiki/index.php?title=Using_database_API>}.
"""

from base import *
from dbconst import *
from cursor import *
from read import *
from bsddbtxn import *
from txn import *
from undoredo import *
from exceptions import *
from write import *
from backup import backup, restore
