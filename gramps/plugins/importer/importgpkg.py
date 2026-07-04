#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License,  or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# Written by Alex Roitman, largely based on ReadNative.py by Don Allingham

"Import from Gramps package"

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os
import tarfile
from contextlib import suppress
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

log = logging.getLogger(".ReadPkg")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import XMLFILE
from gramps.gen.utils.file import media_path

## we need absolute import as this is dynamically loaded:
from gramps.plugins.importer.importxml import importData


# -------------------------------------------------------------------------
#
# Safe tar extraction (CVE-2007-4559)
#
# -------------------------------------------------------------------------
def _is_within_directory(directory: str, target: str) -> bool:
    """
    Return True if ``target`` resolves to a path inside ``directory``.
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonpath([abs_directory, abs_target]) == abs_directory


def _is_safe_member(tarinfo: tarfile.TarInfo, target_dir: str) -> bool:
    """
    Check that extracting ``tarinfo`` into ``target_dir`` cannot write or
    link outside of it.

    A malicious .gpkg file could otherwise use an absolute path, a
    path-traversal name (e.g. ``../../etc/passwd``), or a symlink/hardlink
    to make ``TarFile.extract()`` create or overwrite files outside the
    intended media directory (CVE-2007-4559).
    """
    if os.path.isabs(tarinfo.name) or tarinfo.name.startswith(("/", "\\")):
        return False
    target_path = os.path.join(target_dir, tarinfo.name)
    if not _is_within_directory(target_dir, target_path):
        return False
    if tarinfo.issym() or tarinfo.islnk():
        link_target = os.path.join(os.path.dirname(target_path), tarinfo.linkname)
        if not _is_within_directory(target_dir, link_target):
            return False
    return True


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
def impData(database, name, user):
    # Create tempdir, if it does not exist, then check for writability
    #     THE TEMP DIR is named as the filname.gpkg.media and is created
    #     in the mediapath dir of the family tree we import to
    oldmediapath = database.get_mediapath()
    # use home dir if no media path
    my_media_path = media_path(database)
    media_dir = "%s.media" % os.path.basename(name)
    tmpdir_path = os.path.join(my_media_path, media_dir)
    if not os.path.isdir(tmpdir_path):
        try:
            os.mkdir(tmpdir_path, 0o700)
        except:
            user.notify_error(_("Could not create media directory %s") % tmpdir_path)
            return
    elif not os.access(tmpdir_path, os.W_OK):
        user.notify_error(_("Media directory %s is not writable") % tmpdir_path)
        return
    else:
        # mediadir exists and writable -- User could have valuable stuff in
        # it, have him remove it!
        user.notify_error(
            _(
                "Media directory %s exists. Delete it first, then"
                " restart the import process"
            )
            % tmpdir_path
        )
        return
    try:
        archive = tarfile.open(name)
        for tarinfo in archive:
            if not _is_safe_member(tarinfo, tmpdir_path):
                raise tarfile.TarError(
                    "Unsafe path in archive member: %s" % tarinfo.name
                )
            archive.extract(tarinfo, tmpdir_path)
        archive.close()
    except:
        user.notify_error(_("Error extracting into %s") % tmpdir_path)
        return

    imp_db_name = os.path.join(tmpdir_path, XMLFILE)

    importer = importData
    info = importer(database, imp_db_name, user)

    newmediapath = database.get_mediapath()
    # import of gpkg should not change media path as all media has new paths!
    if not oldmediapath == newmediapath:
        database.set_mediapath(oldmediapath)

    # Set correct media dir if possible, complain if problems
    if oldmediapath is None:
        database.set_mediapath(tmpdir_path)
        user.warn(
            _("Base path for relative media set"),
            _(
                "The base media path of this Family Tree has been set to "
                "%s. Consider taking a simpler path. You can change this "
                "in the Preferences, while moving your media files to the "
                "new position, and using the media manager tool, option "
                "'Replace substring in the path' to set"
                " correct paths in your media objects."
            )
            % tmpdir_path,
        )
    else:
        user.warn(
            _("Cannot set base media path"),
            _(
                "The Family Tree you imported into already has a base media "
                "path: %(orig_path)s. The imported media objects however "
                "are relative from the path %(path)s. You can change the "
                "media path in the Preferences or you can convert the "
                "imported files to the existing base media path. You can "
                "do that by moving your media files to the "
                "new position, and using the media manager tool, option "
                "'Replace substring in the path' to set"
                " correct paths in your media objects."
            )
            % {"orig_path": oldmediapath, "path": tmpdir_path},
        )

    # Remove xml file extracted to media dir we imported from
    with suppress(FileNotFoundError):
        os.remove(imp_db_name)

    return info
