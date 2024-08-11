#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006  Brian Matherly
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
Mime utility functions for the MS Windows platform
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import os
from winreg import *

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import _pythonmime
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def get_description(mime_type):
    """Return the description of the specfied mime type"""
    desc = None
    extension = _get_extension(mime_type)
    progid = _get_prog_id(extension)

    if progid:
        try:
            hcr = ConnectRegistry(None, HKEY_CLASSES_ROOT)
            desc = QueryValue(hcr, progid)
            CloseKey(hcr)
        except WindowsError:
            pass

    if not desc:
        desc = _("unknown")

    return desc


def get_type(file):
    """Return the mime type of the specified file"""
    return _pythonmime.get_type(file)


def mime_type_is_defined(mime_type):
    """
    Return True if a description for a mime type exists.
    """
    extension = _get_extension(mime_type)
    if extension:
        return True
    else:
        return _pythonmime.mime_type_is_defined(mime_type)


# -------------------------------------------------------------------------
#
# private functions
#
# -------------------------------------------------------------------------
def _get_extension(mime_type):
    """
    Return the extension associated with this mime type
    Return None if no association exists
    """
    extension = None
    try:
        hcr = ConnectRegistry(None, HKEY_CLASSES_ROOT)
        subkey = OpenKey(hcr, r"MIME\DataBase\Content Type")
        mimekey = OpenKey(subkey, mime_type)
        extension, value_type = QueryValueEx(mimekey, "Extension")
        CloseKey(mimekey)
        CloseKey(subkey)
        CloseKey(hcr)
    except WindowsError:
        extension = None

    if not extension:
        # Work around for Windows mime problems
        extmap = {
            "application/abiword": ".abw",
            "application/rtf": ".rtf",
        }
        if mime_type in extmap:
            extension = extmap[mime_type]

    return extension


def _get_prog_id(extension):
    """
    Return the program ID associated with this extension
    Return None if no association exists
    """
    if not extension:
        return None

    try:
        hcr = ConnectRegistry(None, HKEY_CLASSES_ROOT)
        progid = QueryValue(hcr, extension)
        CloseKey(hcr)
        return progid
    except WindowsError:
        return None
