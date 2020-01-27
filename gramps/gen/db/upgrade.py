#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2019-2016 Gramps Development Team
# Copyright (C) 2019      Paul Culley
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
""" Generic upgrade module for dbapi dbs """
#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import os
import time
import logging
#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.cli.clidbman import NAME_FILE, find_next_db_dir
from gramps.gui.dialog import GrampsLoginDialog
from gramps.gen.config import config
from . import DbTxn
from .dbconst import (PERSON_KEY, FAMILY_KEY, EVENT_KEY, MEDIA_KEY, PLACE_KEY,
                      REPOSITORY_KEY, SOURCE_KEY, KEY_TO_NAME_MAP, DBBACKEND)
from .exceptions import DbConnectionError
from .utils import make_database
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

LOG = logging.getLogger(".upgrade")


def convert_db(old_db, dirname, uistate):
    """
    Convert a db from its current type to a new format determined by the
    config setting.  This is done by creating a new db in its own directory,
    copying all data objects as serialized data, copying metadata.
    Then both dbs are closed, the original db files are erased, and the new
    db files are moved to the original db directory.

    If the new db needs a password, the dialog is started to get it.

    Returns the dbid of the new db, as well as username, password if any.
    """
    # make a directory for new upgraded db
    old_db_name = os.path.join(dirname, NAME_FILE)
    new_path = find_next_db_dir()
    os.mkdir(new_path)
    # store dbid in new dir
    dbid = config.get('database.backend')
    backend_path = os.path.join(new_path, DBBACKEND)
    with open(backend_path, "w", encoding='utf8') as backend_file:
        backend_file.write(dbid)
    # make and load the new db
    new_db = make_database(dbid)
    username = password = None
    if new_db.requires_login():
        login = GrampsLoginDialog(uistate)
        credentials = login.run()
        if credentials is None:
            raise DbConnectionError(_("No credentials."))
        username, password = credentials
    new_db.load(new_path, uistate.pulse_progressbar, 'w',
                False, False,  # force_schema_upgrade, force_bsddb_upgrade
                False, False,  # force_bsddb_downgrade, force_python_upgrade
                username=username, password=password)
    total = 0
    for _obj_key, obj_name in KEY_TO_NAME_MAP.items():
        data_map = getattr(old_db, obj_name + "_map", None)
        if not data_map:
            continue
        total += len(data_map)
    old_db.set_total(total)
    with DbTxn('upgraded', new_db, batch=True) as trans:
        for obj_key, obj_name in KEY_TO_NAME_MAP.items():
            data_map = getattr(old_db, obj_name + "_map", None)
            if not data_map:
                continue
            for handle in data_map.keys():
                obj = data_map[handle]
                new_db._commit_raw(obj, obj_key, trans)
                old_db.update()
    # copy metadata from old_db to new db
    new_db.set_schema_version(old_db.get_schema_version())
    new_db.name_formats = old_db.name_formats
    new_db.owner = old_db.owner
    new_db.bookmarks = old_db.bookmarks
    new_db.family_bookmarks = old_db.family_bookmarks
    new_db.event_bookmarks = old_db.event_bookmarks
    new_db.source_bookmarks = old_db.source_bookmarks
    new_db.citation_bookmarks = old_db.citation_bookmarks
    new_db.repo_bookmarks = old_db.repo_bookmarks
    new_db.media_bookmarks = old_db.media_bookmarks
    new_db.place_bookmarks = old_db.place_bookmarks
    new_db.note_bookmarks = old_db.note_bookmarks

    # Custom type values
    new_db.event_names = old_db.event_names
    new_db.family_attributes = old_db.family_attributes
    new_db.individual_attributes = old_db.individual_attributes
    new_db.source_attributes = old_db.source_attributes
    new_db.marker_names = old_db.marker_names
    new_db.child_ref_types = old_db.child_ref_types
    new_db.family_rel_types = old_db.family_rel_types
    new_db.event_role_names = old_db.event_role_names
    new_db.name_types = old_db.name_types
    new_db.origin_types = old_db.origin_types
    new_db.repository_types = old_db.repository_types
    new_db.note_types = old_db.note_types
    new_db.source_media_types = old_db.source_media_types
    new_db.url_types = old_db.url_types
    new_db.media_attributes = old_db.media_attributes
    new_db.event_attributes = old_db.event_attributes
    new_db.place_types = old_db.place_types

    # surname list
    new_db.surname_list = old_db.surname_list

    old_db.close()
    new_db.close()
    # copy tree name to new dir
    db_name = os.path.join(new_path, NAME_FILE)
    with open(old_db_name, "r", encoding='utf8') as _file:
        name = _file.read().strip()
    with open(db_name, "w", encoding='utf8') as _file:
        _file.write(name)
    # remove files from old dir
    for filename in os.listdir(dirname):
        file_path = os.path.join(dirname, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            LOG.error('Failed to delete %s. Reason: %s' % (file_path, e))
    # copy new db files to old dir
    for filename in os.listdir(new_path):
        old_file_path = os.path.join(new_path, filename)
        file_path = os.path.join(dirname, filename)
        try:
            os.replace(old_file_path, file_path)
        except Exception as e:
            LOG.error('Failed to move %s. Reason: %s' % (old_file_path, e))
    os.rmdir(new_path)
    return (dbid, username, password)


def gramps_upgrade_20(self):
    """
    Generic update.
    """


def make_zip_backup(self, dirname):
    """
    This backs up the db files so an upgrade can be (manually) undone.
    """
    import zipfile
    # In Windows reserved characters is "<>:"/\|?*"
    reserved_char = r':,<>"/\|?* '
    replace_char = "-__________"
    title = self.get_dbname()
    trans = title.maketrans(reserved_char, replace_char)
    title = title.translate(trans)

    if not os.access(dirname, os.W_OK):
        LOG.warning("Can't write technical DB backup for %s", title)
        return
    (grampsdb_path, db_code) = os.path.split(dirname)
    dotgramps_path = os.path.dirname(grampsdb_path)
    zipname = title + time.strftime("_%Y-%m-%d_%H-%M-%S") + ".zip"
    zippath = os.path.join(dotgramps_path, zipname)
    with zipfile.ZipFile(zippath, 'w') as myzip:
        for filename in os.listdir(dirname):
            pathname = os.path.join(dirname, filename)
            myzip.write(pathname, os.path.join(db_code, filename))
    LOG.warning("If upgrade and loading the Family Tree works, you can "
                "delete the zip file at %s", zippath)
