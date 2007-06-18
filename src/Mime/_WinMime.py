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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: 

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from _winreg import *
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import _PythonMime


def get_application(type):
    """Returns the application command and application name of the
    specified mime type"""
    extension = _get_extension(type)
    progId = _get_prog_id(extension)

    if not progId:
        return None

    # Find the application associated with this program ID
    aReg = ConnectRegistry(None,HKEY_CLASSES_ROOT)
    subkey = OpenKey(aReg, "%s\shell\open\command" % progId)
    if subkey:
        n,command,type = EnumValue(subkey, 0)
        if type == REG_EXPAND_SZ:
            command = command.replace( '%SystemRoot%', 
                                       os.getenv('SystemRoot') )
        CloseKey(aReg)
    else:
        return None
    CloseKey(subkey)

    # Find a friendly name for the application
    if command.startswith('"'):
        app = command.split('"')[1]
    elif command.startswith('rundll32.exe'):
        # Get the description of the DLL instead of the application
        app = command.split()[1].split(',')[0]
    else:
        app = command.split()[0]

    hcu = ConnectRegistry(None,HKEY_CURRENT_USER)
    subkey = OpenKey(hcu, "Software\Microsoft\Windows\ShellNoRoam\MUICache")
    desc = None
    if subkey:
        try:
            desc,ValType = QueryValueEx(subkey, app)
        except:
            # No friendly name exists. Use progId
            desc = progId
        CloseKey(subkey)
    else:
        desc = progId
    CloseKey(hcu)

    return (command,desc)

def get_description(mime_type):
    """Returns the description of the specfied mime type"""
    desc = None
    extension = _get_extension(mime_type)
    progId = _get_prog_id(extension)
    
    if progId:
        aReg = ConnectRegistry(None,HKEY_CLASSES_ROOT)
        desc = QueryValue(aReg, progId)
        CloseKey(aReg)

    if not desc:
        desc = _("unknown")

    return desc

def get_type(file):
    """Returns the mime type of the specified file"""
    return _PythonMime.get_type(file)

def mime_type_is_defined(mime_type):
    """
    Return True if a description for a mime type exists.
    """
    extension = _get_extension(mime_type)
    if extension:
        return True
    else:
        return _PythonMime.mime_type_is_defined(mime_type)
    
_icon_theme = gtk.icon_theme_get_default()

def find_mime_type_pixbuf(mime_type):
    return _PythonMime.find_mime_type_pixbuf(mime_type)
    
#-------------------------------------------------------------------------
#
# private functions
#
#-------------------------------------------------------------------------
def _get_extension(mime_type):
    """
    Return the extension associated with this mime type
    Return None if no association exists
    """
    extension = None
    try:
        aReg = ConnectRegistry(None,HKEY_CLASSES_ROOT)
        subkey = OpenKey(aReg, "MIME\DataBase\Content Type")
        mimekey = OpenKey(subkey, mime_type)
        extension,type = QueryValueEx(mimekey, "Extension")
        CloseKey(mimekey)
        CloseKey(subkey)
        CloseKey(aReg)
    except:
        extension = None
    
    if not extension:
        # Work around for Windows mime problems
        extmap = {
            'application/abiword' : '.abw',
            'application/rtf'     : '.rtf',
            }
        if extmap.has_key(mime_type):
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
        aReg = ConnectRegistry(None,HKEY_CLASSES_ROOT)
        progId = QueryValue(aReg, extension)
        CloseKey(aReg)
        return progId
    except:
        return None
    
