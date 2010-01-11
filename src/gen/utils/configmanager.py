#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Gary Burton 
# Copyright (C) 2009       Doug Blank <doug.blank@gmail.com>
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
This package implements access to GRAMPS configuration.
"""

#---------------------------------------------------------------
#
# System imports
#
#---------------------------------------------------------------
import os
import sys
import time
import ConfigParser
import errno

try:
    from ast import literal_eval as safe_eval
except:
    # PYTHON2.5 COMPATIBILITY: no ast present
    # not as safe as literal_eval, but works for python2.5:
    def safe_eval(exp):
        # restrict eval to empty environment
        return eval(exp, {})

#---------------------------------------------------------------
#
# Classes
#
#---------------------------------------------------------------
class ConfigManager(object):
    """
    Class to construct the singleton CONFIGMAN where all 
    settings are stored.
    """
    PLUGINS = {}

    def __init__(self, filename = None):
        """ 
        Configure manager constructor takes an optional filename.

        The data dictionary stores the settings:

           self.data[section][setting] = value

        The value has a type that matches the default. It is an error
        to attempt to set the setting to a different type. To change
        the type, you must re-register the setting, and re-set the
        value. Values can be any simple type in Python (except,
        currently longs, which are saved as ints to avoid type
        errors). This includes: str, int, list, tuple, dict, float,
        etc. Of course, composite types must themselves be composed of
        simple types.

        The default values are given in Python code and stored here
        on start-up:

           self.default[section][setting] = default_value

        Callbacks are stored as callables here:

           self.callbacks[section][setting] = (id, func)

        The default filename (usually the one you are reading from)
        is stored as self.filename. However, you can save to another
        filename using self.save(otherfilename).
        """
        self._cb_id = 0 # callback id counter
        self.config_path, config_filename = os.path.split(os.path.abspath(filename))
        self.filename = filename # fullpath and filename
        self.callbacks = {}
        self.default = {}
        self.data = {}
        self.reset()

    def register_manager(self, name, plugin="", use_config_path=False):
        """
        Register a plugin manager. name is used as the filename
        and the name of the key of the singleton. plugin is either:
        - full filename ending in .ini
        - a dir or full filename to put ini file into
        - a ConfigManager instance

        If use_config_path is True, use this ConfigManager's path.
        """
        if isinstance(plugin, str): # directory or filename
            path, ininame = os.path.split(os.path.abspath(plugin))
            if not ininame.endswith(".ini"):
                ininame = "%s.ini" % name
            if use_config_path:
                path = self.config_path
            filename = os.path.join(path, ininame)
            plugin = ConfigManager(filename)
        elif isinstance(plugin, ConfigManager):
            pass # ok!
        else:
            raise AttributeError("plugin needs to be a file or ConfigManager")
        ConfigManager.PLUGINS[name] = plugin
        return ConfigManager.PLUGINS[name]

    def get_manager(self, name):
        if name in ConfigManager.PLUGINS:
            return ConfigManager.PLUGINS[name]
        else:
            raise AttributeError("config '%s': does not exist"% name)

    def has_manager(self, name):
        return name in ConfigManager.PLUGINS

    def init(self):
        """
        Either loads from an existing ini file, or saves to it.
        """
        if self.filename:
            if os.path.exists(self.filename):
                self.load()
            else:
                self.save()

    def __getitem__(self, item):
        """
        For item access, such as config["interface.dont-ask"]
        """
        return self.get(item)
    
    def __setitem__(self, item, value):
        """
        For item assignment, such as config["interface.dont-ask"] = True
        """
        self.set(item, value)    
        
    def reset(self, key=None):
        """
        Resets one, a section, or all settings values to their defaults.
        This does not disconnect callbacks.
        """
        if key is None:
            section = None
            setting = None
        elif "." in key:
            section, setting = key.split(".", 1)
        else: # key is not None and doesn't have a "."
            section = key
            setting = None
        # Now, do the reset on the right parts:
        if section is None:
            self.data = {}
            for section in self.default:
                self.data[section] = {}
                for setting in self.default[section]:
                    self.data[section][setting] = self.default[section][setting]
        elif setting is None:
            self.data[section] = {}
            for setting in self.default[section]:
                self.data[section][setting] = self.default[section][setting]
        else:
            self.data[section][setting] = self.default[section][setting]
        # Callbacks are still connected

    def get_sections(self):
        """
        Return all section names.
        """
        return self.data.keys()

    def get_section_settings(self, section):
        """
        Return all section setting names.
        """
        return self.data[section].keys()

    def load(self, filename=None, oldstyle=False):
        """ 
        Loads an .ini into self.data.
        """
        if filename is None:
            filename = self.filename
        if filename and os.path.exists(filename):
            parser = ConfigParser.RawConfigParser()
            parser.read(filename)
            for sec in parser.sections():
                name = sec.lower()
                if name not in self.data:
                    # Add the setting from file
                    # These might be old settings, or third-party settings
                    self.data[name] = {}
                for opt in parser.options(sec):
                    raw_value = parser.get(sec, opt).strip()
                    setting = opt.lower()
                    if oldstyle:
                    ####################### Upgrade from oldstyle < 3.2
                    # Oldstyle didn't mark setting type, but had it 
                    # set in preferences. New style gets it from evaling
                    # the setting's value
                    #######################
                        # if we know this setting, convert type
                        key = "%s.%s" % (name, setting)
                        if self.has_default(key):
                            vtype = type(self.get_default(key))
                            if vtype == bool:
                                value = raw_value in ["1", "True"]
                            elif vtype == list:
                                print >> sys.stderr, "WARNING: ignoring old key '%s'" % key
                                continue # there were no lists in oldstyle
                            else:
                                value = vtype(raw_value)
                        else:
                            # else, ignore it
                            print >> sys.stderr, "WARNING: ignoring old key '%s'" % key
                            continue # with next setting
                    ####################### End upgrade code
                    else:
                        value = safe_eval(raw_value)
                    ####################### Now, let's test and set:
                    if (name in self.default and 
                        setting in self.default[name]):
                        if type(value) == type(self.default[name][setting]):
                            self.data[name][setting] = value
                        else:
                            print >> sys.stderr, ("WARNING: ignoring key with wrong type "
                                   "'%s.%s'" % (name, setting))
                    else:
                        # this could be a third-party setting; add it:
                        self.data[name][setting] = value

    def save(self, filename = None):
        """
        Saves the current section/settings to an .ini file. Optional filename
        will override the default filename to save to, if given.
        """
        if filename is None:
            filename = self.filename
        if filename:
            try:
                head = os.path.split( filename )[0]
                os.makedirs( head )
            except OSError, exp:
                if exp.errno != errno.EEXIST:
                    raise
            key_file = open(filename, "w")
            key_file.write(";; Gramps key file\n")
            key_file.write((";; Automatically created at %s" % 
                      time.strftime("%Y/%m/%d %H:%M:%S")) + "\n\n")
            sections = sorted(self.data)
            for section in sections:
                key_file.write(("[%s]\n") % section)
                keys = sorted(self.data[section])
                for key in keys:
                    value = self.data[section][key]
                    # If it has a default:
                    if self.has_default("%s.%s" % (section, key)):
                        if value == self.get_default("%s.%s" % (section, key)):
                            default = ";;"
                        else:
                            default = ""
                        if isinstance(value, long):
                            value = int(value)
                        key_file.write(("%s%s=%s\n")% (default, 
                                                       key, 
                                                       repr(value)))
                key_file.write("\n")
            key_file.close()
        # else, no filename given; nothing to save so do nothing quietly

    def get(self, key):
        """
        Get the setting's value. raise an error if an invalid section.setting.
        Key is a sting in the "section.setting" format.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.data:
            raise AttributeError("No such config section name: '%s'" % section)
        if setting not in self.data[section]:
            raise AttributeError("No such config setting name: '%s.%s'" % 
                                 (section, setting))
        return self.data[section][setting]

    def is_set(self, key):
        """
        Does the setting exist? Returns True if does, False otherwise.
        Key is a sting in the "section.setting" format.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            return False
        if section not in self.data:
            return False
        if setting not in self.data[section]:
            return False
        return True

    def has_default(self, key):
        """
        Does the setting have a default value? Returns True if it does, 
        False otherwise. Key is a sting in the "section.setting" format.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            return False
        if section not in self.default:
            return False
        if setting not in self.default[section]:
            return False
        return True

    def get_default(self, key):
        """
        Get the setting's default value. Raises an error if invalid key is
        give. Key is a sting in the "section.setting" format.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.default:
            raise AttributeError("No such config section name: '%s'" % section)
        if setting not in self.default[section]:
            raise AttributeError("No such config setting name: '%s.%s'" % 
                                 (section, setting))
        return self.default[section][setting]

    def register(self, key, default):
        """
        Register a section.setting, and set the default.
        Will overwrite any previously set default, and set setting if not one.
        The default value deterimines the type of the setting.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.data:
            self.data[section] = {}
        if section not in self.default:
            self.default[section] = {}
        if section not in self.callbacks:
            self.callbacks[section] = {}
        if setting not in self.callbacks[section]:
            self.callbacks[section][setting] = []
        # Add the default value to settings, if not exist:
        if setting not in self.data[section]:
            self.data[section][setting] = default
        # Set the default, regardless:
        self.default[section][setting] = default

    def connect(self, key, func):
        """
        Connect a callback func that gets called when key is changed.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.data:
            raise AttributeError("No such config section name: '%s'" % section)
        if setting not in self.data[section]:
            raise AttributeError("No such config setting name: '%s.%s'" % 
                                 (section, setting))
        self._cb_id += 1
        self.callbacks[section][setting].append((self._cb_id, func))
        return self._cb_id

    def disconnect(self, callback_id):
        """
        Removes a callback given its callback ID. The ID is generated and
        returned when the function is connected to the key (section.setting).
        """
        for section in self.callbacks:
            for setting in self.callbacks[section]:
                for (cbid, func) in self.callbacks[section][setting]:
                    if callback_id == cbid:
                        self.callbacks[section][setting].remove((cbid, func))

    def emit(self, key):
        """
        Emits the signal "key" which will call the callbacks associated
        with that setting.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.callbacks:
            raise AttributeError("No such config section name: '%s'" % section)
        if setting not in self.callbacks[section]:
            raise AttributeError("No such config setting name: '%s.%s'" % 
                                 (section, setting))
        for (cbid, func) in self.callbacks[section][setting]:
            func(self, 0, str(self.data[section][setting]), None) 

    def set(self, key, value):
        """
        Set the setting's value. There are only two ways to get into
        the data dictionary: via the load() method that reads a file,
        or from this method.
        """
        if "." in key:
            section, setting = key.split(".", 1)
        else:
            raise AttributeError("Invalid config section.setting name: '%s'" % 
                                 key)
        if section not in self.data:
            raise AttributeError("No such config section name: '%s'" % section)
        if setting not in self.data[section]:
            raise AttributeError("No such config setting name: '%s.%s'" % 
                                 (section, setting))
        # Check value to see if right type:
        if type(value) == long:
            value = int(value)
        if type(value) == unicode:
            value = str(value)
        if self.has_default(key):
            if type(self.get_default(key)) != type(value):
                raise AttributeError("attempting to set '%s' to wrong type "
                                     "'%s'; should be '%s'" %
                                     (key, type(value), 
                                      type(self.get_default(key))))
        if (setting in self.data[section] and 
            self.data[section][setting] == value):
            # Do nothing if existed and is the same
            pass
        else:
            # Set the value:
            self.data[section][setting] = value
            # Only call callback if the value changed!
            if (section in self.callbacks and 
                setting in self.callbacks[section]):
                self.emit(key)

