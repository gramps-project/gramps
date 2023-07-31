#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020 Paul Culley <paulr2787@gmail.com>
# Copyright (C) 2020  Nick Hall
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
""" BSDDB upgrade module """
# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import os
import pickle
import logging
from bsddb3.db import DB, DB_DUP, DB_HASH, DB_RDONLY

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.plugins.db.dbapi.sqlite import SQLite
from gramps.cli.clidbman import NAME_FILE, find_next_db_dir
from gramps.gen.db.dbconst import DBBACKEND, DBMODE_W, SCHVERSFN
from gramps.gen.db.exceptions import (
    DbException,
    DbSupportedError,
    DbUpgradeRequiredError,
    DbVersionError,
)
from gramps.gen.db.utils import clear_lock_file
from gramps.gen.lib import Researcher
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.updatecallback import UpdateCallback

_ = glocale.translation.gettext

LOG = logging.getLogger(".upgrade")
_MINVERSION = 9
_DBVERSION = 19


class DbBsddb(SQLite):
    """
    Gramps BSDDB Converter
    """

    def __init__(self):
        """Create a new GrampsDB."""

        super().__init__()

    def load(
        self,
        dirname,
        callback=None,
        mode=DBMODE_W,
        force_schema_upgrade=False,
        update=True,
        username=None,
        password=None,
    ):
        """
        Here we create a sqlite db, and copy the bsddb into it.
        The new db is initially in a new directory, when we finish the copy
        we replace the contents of the original directory with the new db.

        We alway raise an exception to complete this, as the new db still
        needs to be upgraded some more.  When we raise the exception, the new
        db is closed.
        """
        if not update:
            raise DbException("Not Available")
        if not force_schema_upgrade:  # make sure user wants to upgrade
            raise DbSupportedError(_("BSDDB"))

        UpdateCallback.__init__(self, callback)

        # Here we open the dbapi db (a new one) for writing
        new_path = find_next_db_dir()
        os.mkdir(new_path)
        # store dbid in new dir
        dbid = "sqlite"
        backend_path = os.path.join(new_path, DBBACKEND)
        with open(backend_path, "w", encoding="utf8") as backend_file:
            backend_file.write(dbid)

        super().load(
            new_path,
            callback=None,
            mode="w",
            force_schema_upgrade=False,
            username=username,
            password=password,
        )

        # now read in the bsddb and copy to dpapi
        schema_vers = None
        total = 0
        tables = (
            ("person", "person"),
            ("family", "family"),
            ("event", "event"),
            ("place", "place"),
            ("repo", "repository"),
            ("source", "source"),
            ("citation", "citation"),
            ("media", "media"),
            ("note", "note"),
            ("tag", "tag"),
            ("meta_data", "metadata"),
        )

        # open each dbmap, and get its length for the total
        file_name = os.path.join(dirname, "name_group.db")
        if os.path.isfile(file_name):
            name_group_dbmap = DB()
            name_group_dbmap.set_flags(DB_DUP)
            name_group_dbmap.open(file_name, "name_group", DB_HASH, DB_RDONLY)
            total += len(name_group_dbmap)
        else:
            name_group_dbmap = None

        table_list = []
        for old_t, new_t in tables:
            file_name = os.path.join(dirname, old_t + ".db")
            if not os.path.isfile(file_name):
                continue
            dbmap = DB()
            dbmap.open(file_name, old_t, DB_HASH, DB_RDONLY)
            total += len(dbmap)
            table_list.append((old_t, new_t, dbmap))

        self.set_total(total)
        # copy data from each dbmap to sqlite table
        for old_t, new_t, dbmap in table_list:
            self._txn_begin()
            if new_t == "metadata":
                sql = "REPLACE INTO metadata (setting, value) VALUES " "(?, ?)"
            else:
                sql = "INSERT INTO %s (handle, blob_data) VALUES " "(?, ?)" % new_t

            for key in dbmap.keys():
                self.update()
                data = pickle.loads(dbmap[key], encoding="utf-8")

                if new_t == "metadata":
                    if key == b"version":
                        # found a schema version in metadata
                        schema_vers = data
                    elif key == b"researcher":
                        if len(data[0]) == 7:  # Pre-3.3 format
                            # Upgrade researcher data to include a locality
                            # field in the address.
                            addr = tuple([data[0][0], ""] + list(data[0][1:]))
                            new_data = (addr, data[1], data[2], data[3])
                        else:
                            new_data = data
                        data = Researcher().unserialize(new_data)
                    elif key == b"name_formats":
                        # upgrade formats if they were saved in the old way
                        for format_ix in range(len(data)):
                            fmat = data[format_ix]
                            if len(fmat) == 3:
                                fmat = fmat + (True,)
                                data[format_ix] = fmat
                    elif key == b"gender_stats":
                        # data is a dict, containing entries (see GenderStats)
                        self.dbapi.execute("DELETE FROM gender_stats")
                        g_sql = (
                            "INSERT INTO gender_stats "
                            "(given_name, female, male, unknown) "
                            "VALUES (?, ?, ?, ?)"
                        )
                        for name in data:
                            female, male, unknown = data[name]
                            self.dbapi.execute(g_sql, [name, female, male, unknown])
                        continue  # don't need this in metadata anymore
                    elif key == b"default":
                        # convert to string and change key
                        if isinstance(data, bytes):
                            data = data.decode("utf-8")
                        key = b"default-person-handle"
                    elif key == b"mediapath":
                        # change key
                        key = b"media-path"
                    elif key in [
                        b"surname_list",  # created by db now
                        b"pevent_names",  # obsolete
                        b"fevent_names",
                    ]:  # obsolete
                        continue
                    elif (
                        b"_names" in key
                        or b"refs" in key
                        or b"_roles" in key
                        or b"rels" in key
                        or b"_types" in key
                    ):
                        # These are list, but need to be set
                        data = set(data)

                self.dbapi.execute(sql, [key.decode("utf-8"), pickle.dumps(data)])

            # get schema version from file if not in metadata
            if new_t == "metadata" and schema_vers is None:
                versionpath = os.path.join(dirname, str(SCHVERSFN))
                if os.path.isfile(versionpath):
                    with open(versionpath, "r") as version_file:
                        schema_vers = int(version_file.read().strip())
                else:
                    schema_vers = 0
                # and put schema version into metadata
                self.dbapi.execute(sql, ["version", schema_vers])
            self._txn_commit()
            dbmap.close()
            if new_t == "metadata" and schema_vers < _MINVERSION:
                raise DbVersionError(schema_vers, _MINVERSION, _DBVERSION)

        if name_group_dbmap:
            self._txn_begin()
            for key in name_group_dbmap.keys():
                self.update()
                # name_group data (grouping) is NOT pickled
                data = name_group_dbmap[key]
                name = key.decode("utf-8")
                grouping = data.decode("utf-8")
                self.dbapi.execute(
                    "INSERT INTO name_group (name, grouping) VALUES (?, ?)",
                    [name, grouping],
                )
            self._txn_commit()
            name_group_dbmap.close()

        # done with new sqlite db, close it.  Cannot use normal close as it
        # overwrites the metadata.
        self._close()
        try:
            clear_lock_file(self.get_save_path())
        except IOError:
            pass
        self.db_is_open = False
        self._directory = None

        # copy tree name to new dir
        old_db_name = os.path.join(dirname, NAME_FILE)
        db_name = os.path.join(new_path, NAME_FILE)
        with open(old_db_name, "r", encoding="utf8") as _file:
            name = _file.read().strip()
        with open(db_name, "w", encoding="utf8") as _file:
            _file.write(name)
        # remove files from old dir
        for filename in os.listdir(dirname):
            file_path = os.path.join(dirname, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                LOG.error("Failed to delete %s. Reason: %s" % (file_path, e))
        # copy new db files to old dir
        for filename in os.listdir(new_path):
            old_file_path = os.path.join(new_path, filename)
            file_path = os.path.join(dirname, filename)
            try:
                os.replace(old_file_path, file_path)
            except Exception as e:
                LOG.error("Failed to move %s. Reason: %s" % (old_file_path, e))
        os.rmdir(new_path)

        # done preparing new db, but we still need to finish schema upgrades
        raise DbUpgradeRequiredError(schema_vers, "xx")
