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
Utility functions to cast types
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import locale
import sys

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..datehandler import codeset
from ..constfunc import conv_to_unicode, conv_to_unicode_direct, UNITYPE, STRTYPE

"""
strxfrm needs it's unicode argument correctly cast before used.
"""
if sys.version_info[0] < 3:
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode(codeset, 'replace'))
else:
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x)

if codeset == 'UTF-8':
    conv_str_tosrtkey = lambda x: locale.strxfrm(x)
else:
    conv_str_tosrtkey = lambda x: locale.strxfrm(
                        conv_to_unicode(x,'UTF-8').encode(codeset, 'replace'))

def conv_tosrtkey(value):
    if isinstance(value, UNITYPE):
        return conv_unicode_tosrtkey(value)
    elif not isinstance(value, STRTYPE):
        return conv_str_tosrtkey(str(value))
    return conv_str_tosrtkey(value)

#strings in database are utf-8
conv_dbstr_to_unicode = lambda x: conv_to_unicode(x, 'UTF-8')

def cast_to_bool(val):
    if val == str(True):
        return True
    return False

def get_type_converter(val):
    """
    Return function that converts strings into the type of val.
    """
    val_type = type(val)
    if isinstance(val, STRTYPE):
        return str
    elif val_type == int:
        return int
    elif val_type == float:
        return float
    elif val_type == bool:
        return cast_to_bool
    elif val_type in (list, tuple):
        return list

def type_name(val):
    """
    Return the name the type of val.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    val_type = type(val)
    if val_type == int:
        return 'int'
    elif val_type == float:
        return 'float'
    elif val_type == bool:
        return 'bool'
    elif isinstance(val, STRTYPE):
        return 'unicode'
    return 'unicode'

def get_type_converter_by_name(val_str):
    """
    Return function that converts strings into the type given by val_str.
    
    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    if val_str == 'int':
        return int
    elif val_str == 'float':
        return float
    elif val_str == 'bool':
        return cast_to_bool
    elif val_str in ('str', 'unicode'):
        return str
    return str
