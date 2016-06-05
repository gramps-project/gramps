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

## ----------------------------------------------
## Postgresql
## ----------------------------------------------

#from dbapi_support.postgresql import Postgresql
#dbapi = Postgresql(dbname='mydb', user='postgres',
#                   host='localhost', password='PASSWORD')

## ----------------------------------------------
## MySQL
## ----------------------------------------------

#from dbapi_support.mysql import MySQL
#dbapi = MySQL("localhost", "root", "PASSWORD", "mysqldb",
#              charset='utf8', use_unicode=True)

## ----------------------------------------------
## Sqlite
## ----------------------------------------------

from dbapi_support.sqlite import Sqlite
path_to_db = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'sqlite.db')
dbapi = Sqlite(path_to_db)
