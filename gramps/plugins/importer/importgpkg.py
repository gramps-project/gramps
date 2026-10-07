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
import ntpath
import shutil
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


def _member_path(directory: str, name: str) -> str:
    """Resolve a portable archive name without allowing directory escape.

    :param directory: Newly created media directory.
    :param name: Untrusted archive member or hard-link target name.
    :returns: Confined absolute destination.
    :raises ValueError: If the name is not a safe relative path.
    """
    portable = name.replace("\\", "/")
    parts = portable.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(
        prefix + number
        for prefix in ("COM", "LPT")
        for number in "123456789\u00b9\u00b2\u00b3"
    )
    if (
        not portable
        or ntpath.isabs(portable)
        or ntpath.splitdrive(portable)[0]
        or ".." in parts
        or ":" in portable
        or any(
            part not in ("", ".")
            and (part.rstrip(" .") != part or part.split(".", 1)[0].upper() in reserved)
            for part in parts
        )
    ):
        raise ValueError(_("Unsafe path in Gramps package: %s") % name)
    target = os.path.realpath(os.path.join(directory, portable))
    if os.path.commonpath([directory, target]) != directory:
        raise ValueError(_("Unsafe path in Gramps package: %s") % name)
    return target


def _extract_package(archive: tarfile.TarFile, directory: str) -> dict[str, str]:
    """Validate a package before copying regular files into its media folder.

    :param archive: Open package archive.
    :param directory: Newly created, empty extraction directory.
    :returns: Normalised archive names mapped to extracted regular files.
    :raises ValueError: If members contain unsafe paths, links or file types.
    """
    directory = os.path.realpath(directory)
    files: dict[str, tarfile.TarInfo] = {}
    members: list[tuple[str, tarfile.TarInfo | None]] = []
    for member in archive.getmembers():
        target = _member_path(directory, member.name)
        if member.isdir():
            members.append((target, None))
            continue
        if member.isfile():
            source = member
        elif member.islnk():
            # Older packages may deduplicate regular media with hard links.
            # Copy the earlier member's bytes instead of creating OS links.
            link = _member_path(directory, member.linkname)
            if os.path.normcase(link) not in files:
                raise ValueError(
                    _("Invalid hard link in Gramps package: %s") % member.name
                )
            source = files[os.path.normcase(link)]
        else:
            raise ValueError(
                _("Unsupported file type in Gramps package: %s") % member.name
            )
        files[os.path.normcase(target)] = source
        members.append((target, source))
    if os.path.normcase(os.path.join(directory, XMLFILE)) not in files:
        raise ValueError(_("Gramps package contains no data.gramps file"))
    for target, member_data in members:
        if member_data is None:
            os.makedirs(target, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            incoming = archive.extractfile(member_data)
            if incoming is None:
                raise tarfile.ExtractError(_("Could not read Gramps package member"))
            with incoming, open(target, "wb") as output:
                shutil.copyfileobj(incoming, output)
    return {
        os.path.normcase(os.path.relpath(target, directory)): target
        for target, member_data in members
        if member_data is not None
    }


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
    # Use the pictures directory if no media path is set.
    my_media_path = media_path(database)
    media_dir = "%s.media" % os.path.basename(name)
    tmpdir_path = os.path.join(my_media_path, media_dir)
    if not os.path.isdir(tmpdir_path):
        try:
            os.mkdir(tmpdir_path, 0o700)
        except OSError:
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
        with tarfile.open(name) as archive:
            media_paths = _extract_package(archive, tmpdir_path)
    except (OSError, EOFError, tarfile.TarError, ValueError) as error:
        # The directory was created by this import and contains no symlinks.
        shutil.rmtree(tmpdir_path)
        log.warning("Package extraction failed: %s", error)
        user.notify_error(_("Error extracting into %s") % tmpdir_path, str(error))
        return

    imp_db_name = os.path.join(tmpdir_path, XMLFILE)

    # Resolve only members actually extracted from this package. The existing
    # tree's media base and unrelated media records must retain their paths.
    try:
        info = importData(database, imp_db_name, user, media_paths=media_paths)
    finally:
        if database.get_mediapath() != oldmediapath:
            database.set_mediapath(oldmediapath)

    # Remove xml file extracted to media dir we imported from
    with suppress(FileNotFoundError):
        os.remove(imp_db_name)

    return info
