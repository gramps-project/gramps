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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
File and folder related utility functions
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import sys
import locale
import shutil
import logging
LOG = logging.getLogger(".gen.utils.file")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..constfunc import win, mac, cuni, conv_to_unicode, UNITYPE
from ..const import TEMP_DIR, USER_HOME, GRAMPS_LOCALE as glocale

#-------------------------------------------------------------------------
#
#  Constants
#
#-------------------------------------------------------------------------
_NEW_NAME_PATTERN = '%s%sUntitled_%d.%s'

#-------------------------------------------------------------------------
#
#  Functions
#
#-------------------------------------------------------------------------
def find_file( filename):
    # try the filename we got
    try:
        fname = filename
        if os.path.isfile(filename):
            return(filename)
    except UnicodeError:
        try:
            fname = filename.encode(glocale.getfilesystemencoding())
            if os.path.isfile(fname):
                return fname
        except UnicodeError:
            return ''

def find_folder( filename):
    # try the filename we got
    try:
        fname = filename
        if os.path.isdir(filename):
            return(filename)
    except UnicodeError:
        try:
            fname = filename.encode(glocale.getfilesystemencoding())
            if os.path.isdir(fname):
                return fname
        except UnicodeError:
            return ''

def get_unicode_path_from_file_chooser(path):
    """
    Return the Unicode version of a path string.

    :type  path: str
    :param path: The path to be converted to Unicode
    :rtype:      unicode
    :returns:    The Unicode version of path.
    """
    # make only unicode of path of type 'str'
    if isinstance(path, UNITYPE):
        return path
    
    if not (isinstance(path,  str)):
        return path
    ## ONLY PYTHON 2 code shoulr reach this !
    if win():
        # in windows filechooser returns officially utf-8, not filesystemencoding
        try:
            return cuni(path)
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            if sys.version_info[0] < 3:
                return unicode(path, sys.getfilesystemencoding(), 
                                    errors='replace')
            else:
                #no idea, need to know what path is to know what to do
                raise NotImplementedError("Path of type", type(path))
    else:
        try:
            return cuni(path, sys.getfilesystemencoding())
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            if sys.version_info[0] < 3:
                return unicode(path, sys.getfilesystemencoding(), errors='replace')
            else:
                #no idea, need to know what path is to know what to do
                raise NotImplementedError("Path of type", type(path))
            

def get_unicode_path_from_env_var(path):
    """
    Return the Unicode version of a path string.

    :type  path: str
    :param path: The path to be converted to Unicode
    :rtype:      unicode
    :returns:    The Unicode version of path.
    """
    # make only unicode of path of type 'str'
    if not (isinstance(path,  str)):
        raise TypeError("path %s isn't a str" % str(path))

    if win():
        # In Windows path/filename returned from a environment variable is in filesystemencoding
        try:
            new_path = conv_to_unicode(path, sys.getfilesystemencoding())
            return new_path
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            if sys.version_info[0] < 3:
                return unicode(path, sys.getfilesystemencoding(), errors='replace')
            else:
                #no idea, need to know what path is to know what to do
                raise NotImplementedError("Path of type", type(path))
    else:
        try:
            return str(path)
        except:
            LOG.warn("Problem encountered converting string: %s." % path)
            if sys.version_info[0] < 3:
                return unicode(path, sys.getfilesystemencoding(), errors='replace')
            else:
                #no idea, need to know what path is to know what to do
                raise NotImplementedError("Path of type", type(path))

def get_new_filename(ext, folder='~/'):
    ix = 1
    while os.path.isfile(os.path.expanduser(_NEW_NAME_PATTERN %
                                            (folder, os.path.sep, ix, ext))):
        ix = ix + 1
    return os.path.expanduser(_NEW_NAME_PATTERN % (folder, os.path.sep, ix, ext))

def get_empty_tempdir(dirname):
    """ Return path to TEMP_DIR/dirname, a guaranteed empty directory

    makes intervening directories if required
    fails if _file_ by that name already exists, 
    or for inadequate permissions to delete dir/files or create dir(s)

    """
    dirpath = os.path.join(TEMP_DIR,dirname)
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    dirpath = get_unicode_path_from_env_var(dirpath)
    return dirpath

def rm_tempdir(path):
    """Remove a tempdir created with get_empty_tempdir"""
    if path.startswith(TEMP_DIR) and os.path.isdir(path):
        shutil.rmtree(path)

def relative_path(original, base):
    """
    Calculate the relative path from base to original, with base a directory,
    and original an absolute path
    On problems, original is returned unchanged
    """
    if not os.path.isdir(base):
        return original
    #original and base must be absolute paths
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
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] != target_list[i]: break
    else:
        #if break did not happen we are here at end, and add 1.
        i += 1
    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)

def media_path(db):
    """
    Given a database, return the mediapath to use as basedir for media
    """
    mpath = db.get_mediapath()
    if mpath is None:
        #use home dir
        mpath = USER_HOME
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
    if name.startswith( '"' ):
        name = name.split('"')[1]
    else:
        name = name.split()[0]
    if win():
        for i in os.environ['PATH'].split(';'):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
        if os.access(name, os.X_OK) and not os.path.isdir(name):
            return 1
    else:
        for i in os.environ['PATH'].split(':'):
            fname = os.path.join(i, name)
            if os.access(fname, os.X_OK) and not os.path.isdir(fname):
                return 1
    return 0

def fix_encoding(value, errors='strict'):
    # The errors argument specifies the response when the input string can't be
    # converted according to the encoding's rules. Legal values for this
    # argument are 'strict' (raise a UnicodeDecodeError exception), 'replace'
    # (add U+FFFD, 'REPLACEMENT CHARACTER'), or 'ignore' (just leave the
    # character out of the Unicode result).
    if not isinstance(value, UNITYPE):
        try:
            return cuni(value)
        except:
            codeset = glocale.encoding
            if sys.version_info[0] < 3:
                return unicode(value, codeset, errors)
            else:
                return value.decode(encoding=codeset, errors=errors)
    else:
        return value
