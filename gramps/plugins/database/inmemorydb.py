#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Douglas S. Blank <doug.blank@gmail.com>
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

from dbapi import DBAPI
from dbapi_support.sqlite import Sqlite
from gramps.gen.db.generic import DbGeneric, DBBACKEND, LOG
import os
import glob

class InMemoryDB(DBAPI):
    """
    A DB-API 2.0 In-memory SQL database.
    """

    def initialize_backend(self, directory):
        """
        Create an in-memory sqlite database.
        """
        self.dbapi = Sqlite(":memory:")
        self.update_schema()

    def write_version(self, directory):
        """Write files for a newly created DB."""
        versionpath = os.path.join(directory, str(DBBACKEND))
        LOG.debug("Write database backend file to 'inmemorydb'")
        with open(versionpath, "w") as version_file:
            version_file.write("inmemorydb")
        versionpath = os.path.join(directory, "bdbversion.txt")
        with open(versionpath, "w") as version_file:
            version_file.write(str(self.VERSION))

    def load(self, directory, callback=None, mode=None,
             force_schema_upgrade=False,
             force_bsddb_upgrade=False,
             force_bsddb_downgrade=False,
             force_python_upgrade=False,
             update=True):
        DbGeneric.load(self, directory,
                       callback,
                       mode,
                       force_schema_upgrade,
                       force_bsddb_upgrade,
                       force_bsddb_downgrade,
                       force_python_upgrade)
        # Dictionary-specific load:
        from gramps.plugins.importer.importxml import importData
        from gramps.cli.user import User
        if self._directory:
            backups = sorted(glob.glob(os.path.join(
                self._directory, "backup-*.gramps")), reverse=True)
            if backups:
                filename = backups[0]
                if os.path.isfile(filename):
                    importData(self, filename, User())
                    self.reindex_reference_map(lambda progress: None)
                    self.rebuild_secondary(lambda progress: None)
                    self.has_changed = False
