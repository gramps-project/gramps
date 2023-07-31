#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
File and folder related utility functions
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os
import sys
import shutil
import tempfile
import hashlib
import logging

LOG = logging.getLogger(".gen.utils.file")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..constfunc import win, mac, get_env_var
from ..const import USER_HOME, USER_PICTURES, ENV, GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
#  Constants
#
# -------------------------------------------------------------------------
_NEW_NAME_PATTERN = "%s%sUntitled_%d.%s"


# -------------------------------------------------------------------------
#
#  Functions
#
# -------------------------------------------------------------------------
def find_file(filename):
    # try the filename we got
    try:
        if os.path.isfile(filename):
            return filename
    except UnicodeError as err:
        LOG.error("Filename %s raised a Unicode Error %s.", repr(filename), err)

    LOG.debug("Filename %s not found.", repr(filename))
    return ""


def find_folder(filename):
    # try the filename we got
    try:
        if os.path.isdir(filename):
            return filename
    except UnicodeError as err:
        LOG.error("Filename %s raised a Unicode Error %s", repr(filename), err)

    LOG.debug("Filename %s either not found or not a directory.", repr(filename))
    return ""


def get_new_filename(ext, folder="~/"):
    ix = 1
    while os.path.isfile(
        os.path.expanduser(_NEW_NAME_PATTERN % (folder, os.path.sep, ix, ext))
    ):
        ix = ix + 1
    return os.path.expanduser(_NEW_NAME_PATTERN % (folder, os.path.sep, ix, ext))


def get_empty_tempdir(dirname):
    """Return path to TEMP_DIR/dirname, a guaranteed empty directory

    makes intervening directories if required
    fails if _file_ by that name already exists,
    or for inadequate permissions to delete dir/files or create dir(s)

    """
    dirpath = tempfile.mkdtemp(prefix="gramps-", suffix="-" + dirname)
    return dirpath


def rm_tempdir(path):
    """Remove a tempdir created with get_empty_tempdir"""
    if path.startswith(tempfile.gettempdir()) and os.path.isdir(path):
        shutil.rmtree(path)


def relative_path(original, base):
    """
    Calculate the relative path from base to original, with base a directory,
    and original an absolute path
    On problems, original is returned unchanged
    """
    if not os.path.isdir(base):
        return original
    # original and base must be absolute paths
    if not os.path.isabs(base):
        return original
    if not os.path.isabs(original):
        return original
    original = os.path.normpath(original)
    base = os.path.normpath(base)

    # If the db_dir and obj_dir are on different drives (win only)
    # then there cannot be a relative path. Return original obj_path
    (base_drive, base) = os.path.splitdrive(base)
    (orig_drive, orig_name) = os.path.splitdrive(original)
    if base_drive.upper() != orig_drive.upper():
        return original

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    base_list = (base).split(os.sep)
    target_list = (orig_name).split(os.sep)
    # make sure '/home/person' and 'c:/home/person' both give
    #   list ['home', 'person']
    base_list = [_f for _f in base_list if _f]
    target_list = [_f for _f in target_list if _f]
    i = -1
    # base path is normcase (lower case on Windows) so compare target in lower
    # on Windows as well
    for i in range(min(len(base_list), len(target_list))):
        if win():
            if base_list[i].lower() != target_list[i].lower():
                break
        else:
            if base_list[i] != target_list[i]:
                break
    else:
        # if break did not happen we are here at end, and add 1.
        i += 1
    rel_list = [os.pardir] * (len(base_list) - i) + target_list[i:]
    return os.path.join(*rel_list)


def expand_path(path, normalize=True):
    """
    Expand environment variables in a path
    Uses both the environment variables and the Gramps environment
    The expansion uses the str.format, e.g. "~/{GRAMPSHOME}/{VERSION}/filename.txt"
    We make the assumption that the user will not use a path that contain variable names
    (it is technically possible to use characters "{", "}" in  paths)
    """
    environment = dict(os.environ)
    environment.update(ENV)
    if not "GRAMPSHOME" in environment:
        environment["GRAMPSHOME"] = USER_HOME
    path = path.format(**environment)
    if normalize:
        path = os.path.normcase(os.path.normpath(os.path.abspath(path)))
    return path


def media_path(db):
    """
    Given a database, return the mediapath to use as basedir for media
    """
    mpath = db.get_mediapath()
    return expand_media_path(mpath, db)


def expand_media_path(mpath, db):
    """
    Normalize a mediapath:
     - Relative mediapath are considered as relative to the database
     - Expand variables, see expand_path
     - Convert to absolute path
     - Convert slashes and case (on Windows)
    """
    # Use XDG pictures diectory if no media_path specified
    if mpath is None:
        mpath = os.path.abspath(USER_PICTURES)
    # Expand environment variables
    mpath = expand_path(mpath, False)
    # Relative mediapath are considered as relative to the database
    if not os.path.isabs(mpath):
        basepath = db.get_save_path()
        if not basepath:
            basepath = USER_HOME
        mpath = os.path.join(os.path.abspath(basepath), mpath)
    # Normalize path
    mpath = os.path.normcase(os.path.normpath(os.path.abspath(mpath)))
    return mpath


def media_path_full(db, filename):
    """
    Given a database and a filename of a media, return the media filename
    is full form, eg 'graves/tomb.png' becomes '/home/me/genea/graves/tomb.png
    """
    if os.path.isabs(filename):
        return filename
    mpath = media_path(db)
    return os.path.join(mpath, filename)


def search_for(name):
    if name.startswith('"'):
        name = name.split('"')[1]
    else:
        name = name.split()[0]
    if win():
        for i in get_env_var("PATH").split(";"):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
        if os.access(name, os.X_OK) and not os.path.isdir(name):
            return 1
    else:
        for i in os.environ["PATH"].split(":"):  # not win()
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
    return 0


def where_is(name):
    """This command is similar to the Linux "whereis -b file" command.
    It looks for an executable file (name) in the PATH python is using, as
    well as several likely other paths.  It returns the first file found,
    or an empty string if not found.
    """
    paths = set(os.environ["PATH"].split(os.pathsep))
    if not win():
        paths.update(
            ("/bin", "/usr/bin", "/usr/local/bin", "/opt/local/bin", "/opt/bin")
        )
    for i in paths:
        fname = os.path.join(i, name)
        if os.access(fname, os.X_OK) and not os.path.isdir(fname):
            return fname
    return ""


def create_checksum(full_path):
    """
    Create a md5 hash for the given file.
    """
    full_path = os.path.normpath(full_path)
    md5 = hashlib.md5()
    try:
        with open(full_path, "rb") as media_file:
            while True:
                buf = media_file.read(65536)
                if not buf:
                    break
                md5.update(buf)
        md5sum = md5.hexdigest()
    except IOError:
        md5sum = ""
    except UnicodeEncodeError:
        md5sum = ""
    return md5sum
