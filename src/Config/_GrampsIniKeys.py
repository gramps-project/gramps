#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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
Low-level handling of .ini keys. 
"""

import os
import time
import ConfigParser
import errno
import const
from _GrampsConfigKeys import *

NL = "\n" # FIX: newlines on Mac/Windows, if different?

def make_bool(val):
    """ Function to turn strings into booleans. """
    # these are the possible strings that should be considered False
    if val.lower() in ["0", "false", "none", ""]:
        return False
    else:
        return True

class IniKeyClient:
    """ Class to emulate gconf's client """
    def __init__(self, filename = None):
        """ Constructor takes an optional filename """
        self.data = {}
        self.callbacks = {}
        self.filename = filename
        if self.filename and os.path.exists(filename):
            self.data = self.load_ini(self.filename)

    def notify_add(self, path, func):
        """
        I think that these are callbacks that get called when the keys
        are set.
        """
        parts = path.split("/") # FIX: make path-sep independent
        # /apps/gramps/section/key
        section = parts[-2]
        key = parts[-1]
        if section not in self.callbacks:
            self.callbacks[section] = {}
        self.callbacks[section][key] = func

    def load_ini(self, filename):
        """ Load .ini into dict of dicts, which it returns """
        cp = ConfigParser.ConfigParser()
        cp.read(filename)
        data = {}
        for sec in cp.sections():
            name = sec.lower()
            if not data.has_key(name):
                data[name] = {}
            for opt in cp.options(sec):
                data[name][opt.lower()] = cp.get(sec, opt).strip()
        return data

    def save_ini(self, filename = None):
        """
        Saves the current section/keys to a .ini file. Optional filename
        will override the default filename, if one.
        """
        if not filename:
            filename = self.filename
        if filename:
            try:
                head, tail = os.path.split( filename )
                os.makedirs( head )
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            fp = open(filename, "w")
            fp.write(";; Gramps key file" + NL)
            fp.write((";; Automatically created at %s" % time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
            sections = self.data.keys()
            sections.sort()
            for section in sections:
                fp.write(("[%s]" + NL) % section)
                keys = self.data[section].keys()
                keys.sort()
                for key in keys:
                    fp.write(("%s=%s" + NL)% (key, self.data[section][key]))
                fp.write(NL)
            fp.close()
        # else, no filename given

    def get_bool(self, key):
        """ Emulates gconf's client method """
        return make_bool(self.data[key[0]][key[1]])

    def get_string(self, key):
        """ Emulates gconf's client method """
        return self.data[key[0]][key[1]]

    def get_int(self, key):
        """ Emulates gconf's client method """
        if self.data[key[0]][key[1]].isdigit():
            return int(self.data[key[0]][key[1]])
        elif self.data[key[0]][key[1]].lower() in ["true"]:
            return 1
        else:
            return 0

    def set_bool(self, key, val):
        """ Emulates gconf's client method """
        if key[0] not in self.data:
            self.data[key[0]] = {}
        self.data[key[0]][key[1]] = str(val)
        if key[0] in self.callbacks and key[1] in self.callbacks[key[0]]:
            self.callbacks[key[0]][key[1]](self,0,self.data[key[0]][key[1]],None) 

    def set_string(self, key, val):
        """ Emulates gconf's client method """
        if key[0] not in self.data:
            self.data[key[0]] = {}
        self.data[key[0]][key[1]] = val
        if key[0] in self.callbacks and key[1] in self.callbacks[key[0]]:
            self.callbacks[key[0]][key[1]](self,0,self.data[key[0]][key[1]],None) 

    def set_int(self, key, val):
        """ Emulates gconf's client method """
        if key[0] not in self.data:
            self.data[key[0]] = {}
        self.data[key[0]][key[1]] = str(val)
        if key[0] in self.callbacks and key[1] in self.callbacks[key[0]]:
            self.callbacks[key[0]][key[1]](self,0,self.data[key[0]][key[1]],None) 

    def suggest_sync(self):
        self.save_ini() # save back to default file, if named

client = IniKeyClient(os.path.join(const.home_dir,"keys.ini"))

#-------------------------------------------------------------------------
#
# Functions to obtain values from .ini keys
#           and store values into .ini keys
#
# All gramps keys should be accessed through these functions!
#
#-------------------------------------------------------------------------


def get_date_format(_date_format_list=[]):
    return get_int(DATE_FORMAT,
                   range(len(_date_format_list)))

def save_date_format(val,_date_format_list=[]):
    set_int(DATE_FORMAT, val,
            range(len(_date_format_list)))

def get_name_format(_name_format_list):
    return get_int(NAME_FORMAT,
                   range(len(_name_format_list)))

def save_name_format(val,_name_format_list):
    set_int(NAME_FORMAT, val,
            range(len(_name_format_list)))


#-------------------------------------------------------------------------
#
# Low-level grabbing and saving keys with error checking.
#
#-------------------------------------------------------------------------

def set(key, value):
    if key[2] == 0:
        set_bool(key, value)
    elif key[2] == 1:
        set_int(key, value)
    else:
        set_string(key, value)

def get(key):
    if key[2] == 0:
        val = get_bool(key)
    elif key[2] == 1:
        val = get_int(key)
    else:
        val = get_string(key)
    if not val:
        val = default_value[key]
    return val

def get_bool(key):
    try:
        val = client.get_bool(key)
    except KeyError:
        val = None
    if val in (True,False):
        return val
    else:
        return default_value[key]

def set_bool(key, val):
    if val in (True,False):
        client.set_bool(key,val)

def get_int(key, correct_tuple=None):
    try:
        return client.get_int(key)
    except KeyError:
        return default_value[key]

def set_int(key, val, correct_tuple=None):
    if not correct_tuple or val in correct_tuple:
        client.set_int(key, val)

def get_string(key, test_func=None):
    try:
        val = client.get_string(key)
    except KeyError:
        val = ""
    if not test_func or test_func(val):
        return val
    else:
        return default_value[key]

def set_string(key, val, test_func=None):
    if not test_func or test_func(val):
        client.set_string(key, val)

def sync():
    client.suggest_sync()

def get_default(key,sample=''):
    return default_value[key]
