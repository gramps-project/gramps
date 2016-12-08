#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
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

## This file is copied from gramps/plugins/db/dbapi/settings.py
## into each grampsdb/*/ directory. You can edit each copy
## to connect to different databases, or with different
## parameters.

## The database options are saved in settings.ini.
# NOTE: config is predefined

# NOTE: you can override this in settings.ini or here:
dbtype = config.get('database.dbtype')

if dbtype == "sqlite":
    from gramps.plugins.db.dbapi.sqlite import Sqlite
    path_to_db = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'sqlite.db')
    dbapi = Sqlite(path_to_db)
else:
    # NOTE: you can override these settings here or in settings.ini:
    dbname = config.get('database.dbname')
    host = config.get('database.host')
    user = config.get('database.user')
    password = config.get('database.password')
    port = config.get('database.port')
    if dbtype == "postgresql":
        from gramps.plugins.db.dbapi.postgresql import Postgresql
        dbapi = Postgresql(dbname=dbname, user=user,
                           host=host, password=password)
    else:
        raise AttributeError(("invalid DB-API dbtype: '%s'. " +
                              "Should be 'sqlite' or 'postgresql'") % dbtype)
