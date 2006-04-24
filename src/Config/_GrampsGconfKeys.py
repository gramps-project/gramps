#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
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
Low-level handling of gconf keys. 
"""

#-------------------------------------------------------------------------
#
# GConf
#
#-------------------------------------------------------------------------
# SUSE calls the gconf module "gnome.gconf"
try:
    import gconf
except ImportError:
    import gnome.gconf
    gconf = gnome.gconf

import gobject
import Errors
from _GrampsConfigKeys import default_value

client = gconf.client_get_default()
client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)


#-------------------------------------------------------------------------
#
# Functions to obtain values from gconf keys
#           and store values into gconf keys
#
# All gramps keys should be accessed through these functions!
#
#-------------------------------------------------------------------------

def get_date_format(date_format_list):
    return get_int("/apps/gramps/preferences/date-format",
                        range(len(date_format_list)))

def save_date_format(val,date_format_list):
    set_int("/apps/gramps/preferences/date-format",val,
                        range(len(date_format_list)))

def get_name_format(_name_format_list):
    return get_int("/apps/gramps/preferences/name-format",
                        range(len(_name_format_list)))

def save_name_format(val,_name_format_list):
    set_int("/apps/gramps/preferences/name-format",val,
                        range(len(_name_format_list)))

#-------------------------------------------------------------------------
#
# Low-level grabbing and saving keys with error checking.
#
#-------------------------------------------------------------------------

def set(key, value):
    token = "/apps/gramps/%s/%s" % (key[0],key[1])
    if key[2] == 0:
        set_bool(token,value)
    elif key[2] == 1:
        set_int(token,value)
    else:
        set_string(token,value)

def get(key):
    token = "/apps/gramps/%s/%s" % (key[0],key[1])
    if key[2] == 0:
        val = get_bool(token)
    elif key[2] == 1:
        val = get_int(token)
    else:
        val = get_string(token)
    if not val:
        val = default_value[key]
    return val

def get_bool(key):
    try:
        val = client.get_bool(key)
    except gobject.GError:
        val = None
    if val in (True,False):
        return val
    else:
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_bool()

def set_bool(key,val):
    if val in (True,False):
        client.set_bool(key,val)

def get_int(key,correct_tuple=None):
    try:
        val = client.get_int(key)
    except gobject.GError:
        val = None
    if not correct_tuple or val in correct_tuple:
        return val
    else:
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_int()

def set_int(key,val,correct_tuple=None):
    if not correct_tuple or val in correct_tuple:
        client.set_int(key,val)

def get_string(key,test_func=None):
    try:
        val = client.get_string(key)
    except gobject.GError:
        val = None
    if not test_func or test_func(val):
        return val
    else:
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_string()

def set_string(key,val,test_func=None):
    if not test_func or test_func(val):
        client.set_string(key,val)

def sync():
    client.suggest_sync()
