#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Gary Burton
# Copyright (C) 2009       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2023       Christopher Horn
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
This package implements access to Gramps configuration.
"""

# ---------------------------------------------------------------
#
# Python modules
#
# ---------------------------------------------------------------
import configparser
import copy
import errno
import logging
import os
import sys
import time

# ---------------------------------------------------------------
#
# Gramps modules
#
# ---------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def clean_up(parser):
    # Needed so that the parser can be removed by the garabge collection
    for section in parser:
        delattr(parser._proxies[section], "getboolean")
        delattr(parser._proxies[section], "getint")
        delattr(parser._proxies[section], "getfloat")
        del parser._proxies[section]
    del parser._converters


def safe_eval(exp):
    # restrict eval to empty environment
    return eval(exp, {})


# ---------------------------------------------------------------
#
# ConfigManager
#
# ---------------------------------------------------------------
class ConfigManager:
    """
    Class to construct the singleton CONFIGMAN where all
    settings are stored.
    """

    PLUGINS = {}

    def __init__(self, filename=None, plugins=None):
        """
        Configure manager constructor takes an optional filename, and
        plugin path.

        The data dictionary stores the settings::

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
        on start-up::

           self.default[section][setting] = default_value

        Callbacks are stored as callables here::

           self.callbacks[section][setting] = (id, func)

        The default filename (usually the one you are reading from)
        is stored as self.filename. However, you can save to another
        filename using self.save(otherfilename).

        :param filename: (if given) is a fullpath.
        :param plugins: (if given) is a relative path to filename.

        """
        self._cb_id = 0  # callback id counter
        self.config_path, dummy_config_filename = os.path.split(
            os.path.abspath(filename)
        )
        self.filename = filename  # fullpath and filename, or None
        self.plugins = plugins  # relative directory name, or None
        self.callbacks = {}
        self.default = {}
        self.data = {}
        self.reset()

    def register_manager(
        self, name, override="", use_plugins_path=True, use_config_path=False
    ):
        """
        Register a plugin manager.

        :param name: is used as the key of the config manager singleton. It is
                     also be used as the base filename (unless an override is
                     given, or use_config_path or use_plugins_path is True).
        :param override: is used to override the default location of the .ini
                         file.
        :param use_config_path: if True, use this ConfigManager's path as the
                                new manager's path, ignoring any path given in
                                override.

        Override is either:

        - a full path+filename ending in .ini
        - a filename ending in .ini
        - a dir path to put ini file into
        - a full path+filename to get dir to put ini file into
        - a ConfigManager instance

        Examples::

          >>> config.register_manager("Simple", use_plugins_path=False)
          # will use the calling programs directory, and "Simple.ini"
          >>> config.register_manager("Simple", __file__,
                                      use_plugins_path=False)
          # will use the __file__'s directory, and "Simple.ini"
          >>> config.register_manager("Simple", "c:\\temp",
                                      use_plugins_path=False)
          # will use the given directory, "c:\\temp\\Simple.ini"
          >>> config.register_manager("Simple", use_config_path=True)
          # will use config's path: ~/.gramps/gramps32/Simple.ini
          >>> config.register_manager("Simple", "Other.ini")
          # will use config + plugins path: ~/.gramps/gramps32/plugins/Other.ini
          >>> config.register_manager("Simple", "/tmp/Other.ini",
                                      use_plugins_path=False)
          # will use /tmp/Other.ini
        """
        if isinstance(override, str):  # directory or filename
            if override:
                path, ininame = os.path.split(os.path.abspath(override))
            else:
                path, ininame = os.path.split(sys._getframe(1).f_code.co_filename)
            if not ininame.endswith(".ini"):
                ininame = f"{name}.ini"
            if use_config_path:
                path = self.config_path
            elif use_plugins_path:
                path = os.path.join(self.config_path, self.plugins)
            filename = os.path.join(path, ininame)
            plugin = ConfigManager(filename)
        elif isinstance(override, ConfigManager):
            plugin = override
        else:
            raise AttributeError("plugin needs to be a file or ConfigManager")
        ConfigManager.PLUGINS[name] = plugin
        return ConfigManager.PLUGINS[name]

    def get_manager(self, name):
        """
        Return manager for a plugin.
        """
        if name in ConfigManager.PLUGINS:
            return ConfigManager.PLUGINS[name]
        raise AttributeError(f"config '{name}': does not exist")

    def has_manager(self, name):
        """
        Check if have manager for a plugin.
        """
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
        else:  # key is not None and doesn't have a "."
            section = key
            setting = None

        # Now, do the reset on the right parts:
        if section is None:
            self.data = {}
            for section in self.default:
                self.data[section] = {}
                for setting in self.default[section]:
                    self.data[section][setting] = copy.deepcopy(
                        self.default[section][setting]
                    )
        elif setting is None:
            self.data[section] = {}
            for setting in self.default[section]:
                self.data[section][setting] = copy.deepcopy(
                    self.default[section][setting]
                )
        else:
            self.data[section][setting] = copy.deepcopy(self.default[section][setting])
        # Callbacks are still connected

    def get_sections(self):
        """
        Return all section names.
        """
        return list(self.data.keys())

    def get_section_settings(self, section):
        """
        Return all section setting names.
        """
        return list(self.data[section].keys())

    def load(self, filename=None, oldstyle=False):
        """
        Loads an .ini into self.data.
        """
        if filename is None:
            filename = self.filename
        if filename and os.path.exists(filename):
            parser = configparser.RawConfigParser()
            try:  # see bugs 5356, 5490, 5591, 5651, 5718, etc.
                parser.read(filename, encoding="utf8")
            except Exception as err:
                msg1 = _(
                    "WARNING: could not parse file:\n%(file)s\n"
                    "because %(error)s -- recreating it\n"
                ) % {"file": filename, "error": str(err)}
                logging.warning(msg1)
                return

            if oldstyle:
                loader = self._load_oldstyle_section
            else:
                loader = self._load_section

            for section in parser.sections():
                name = section.lower()
                if name not in self.data:
                    self.data[name] = {}
                loader(section, parser)

            clean_up(parser)

    def _load_section(self, section, parser):
        """
        Load a section of an .ini file into self.data
        """
        name = section.lower()
        for option in parser.options(section):
            raw_value = get_raw_value(parser, section, option)
            setting = option.lower()

            try:
                value = safe_eval(raw_value)
            except:
                # most likely exception is SyntaxError but
                # others are possible  ex: '0L' from Python2 days
                value = None

            self._load_setting(name, setting, value)

    def _load_oldstyle_section(self, section, parser):
        """
        Load a section of an .ini file into self.data
        """
        name = section.lower()
        for option in parser.options(section):
            raw_value = get_raw_value(parser, section, option)
            setting = option.lower()

            ####################### Upgrade from oldstyle < 3.2
            # Oldstyle didn't mark setting type, but had it
            # set in preferences. New style gets it from evaling
            # the setting's value
            #######################
            # if we know this setting, convert type
            key = f"{name}.{setting}"
            if self.has_default(key):
                vtype = type(self.get_default(key))
                if vtype == bool:
                    value = raw_value in ["1", "True"]
                elif vtype == list:
                    logging.warning("WARNING: ignoring old key '%s'", key)
                    continue  # there were no lists in oldstyle
                else:
                    value = vtype(raw_value)
            else:
                # else, ignore it
                logging.warning("WARNING: ignoring old key '%s'", key)
                continue  # with next setting
            ####################### End upgrade code
            self._load_setting(name, setting, value)

    def _load_setting(self, name, setting, value):
        if name in self.default and setting in self.default[name]:
            if isinstance(self.default[name][setting], bool):
                value = bool(value)
            if self.check_type(self.default[name][setting], value):
                self.data[name][setting] = value
            else:
                logging.warning(
                    "WARNING: ignoring key with wrong type "
                    "'%s.%s' %s needed instead of %s",
                    name,
                    setting,
                    type(self.data[name][setting]),
                    type(value),
                )
        else:
            # this could be a third-party setting; add it:
            self.data[name][setting] = value

    def save(self, filename=None, comments=None):
        """
        Saves the current section/settings to an .ini file. Optional filename
        will override the default filename to save to, if given.
        """
        if filename is None:
            filename = self.filename
        if filename:
            try:
                head = os.path.split(filename)[0]
                os.makedirs(head)
            except OSError as exp:
                if exp.errno != errno.EEXIST:
                    raise
            try:
                with open(filename, "w", encoding="utf-8") as key_file:
                    key_file.write(";; Gramps key file\n")
                    key_file.write(
                        ";; Automatically created at "
                        f"{time.strftime('%Y/%m/%d %H:%M:%S')}\n\n"
                    )
                    write_comments(key_file, comments)
                    for section in sorted(self.data):
                        key_file.write(f"[{section}]\n")
                        for key in sorted(self.data[section]):
                            value = self.data[section][key]
                            default = ""  # might be a third-party setting
                            if self.has_default(f"{section}.{key}"):
                                if value == self.get_default(f"{section}.{key}"):
                                    default = ";;"
                            if isinstance(value, int):
                                value = int(value)  # TODO why is this needed?
                            key_file.write(f"{default}{key}={repr(value)}\n")
                        key_file.write("\n")
                # else, no filename given; nothing to save so do nothing quietly
            except IOError as err:
                logging.warning("Failed to open %s because %s", filename, str(err))
                return

    def get(self, key):
        """
        Get the setting's value. raise an error if an invalid section.setting.
        Key is a string in the "section.setting" format.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                f"Invalid config section.setting name: '{key}'"
            ) from error

        self._validate_section_and_setting(section, setting)
        return self.data[section][setting]

    def _validate_section_and_setting(self, section, setting):
        """
        Validate section and setting present in the loaded data.
        """
        if section not in self.data:
            raise AttributeError(f"No such config section name: '{section}'")
        if setting not in self.data[section]:
            raise AttributeError(f"No such config setting name: '{section}.{setting}'")

    def is_set(self, key):
        """
        Does the setting exist? Returns True if does, False otherwise.
        Key is a string in the "section.setting" format.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError:
            return False

        if section not in self.data:
            return False
        if setting not in self.data[section]:
            return False
        return True

    def has_default(self, key):
        """
        Does the setting have a default value? Returns True if it does,
        False otherwise. Key is a string in the "section.setting" format.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError:
            return False

        if section not in self.default:
            return False
        if setting not in self.default[section]:
            return False
        return True

    def get_default(self, key):
        """
        Get the setting's default value. Raises an error if invalid key is
        give. Key is a string in the "section.setting" format.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                f"Invalid config section.setting name: '{key}'"
            ) from error

        if section not in self.default:
            raise AttributeError(f"No such config section name: '{section}'")
        if setting not in self.default[section]:
            raise AttributeError(f"No such config setting name: '{section}.{setting}'")
        return self.default[section][setting]

    def register(self, key, default):
        """
        Register a section.setting, and set the default.
        Will overwrite any previously set default, and set setting if not one.
        The default value deterimines the type of the setting.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                f"Invalid config section.setting name: '{key}'"
            ) from error

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
        self.default[section][setting] = copy.deepcopy(default)

    def connect(self, key, func):
        """
        Connect a callback func that gets called when key is changed.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                f"Invalid config section.setting name: '{key}'"
            ) from error

        self._validate_section_and_setting(section, setting)
        self._cb_id += 1
        self.callbacks[section][setting].append((self._cb_id, func))
        return self._cb_id

    def disconnect(self, callback_id):
        """
        Removes a callback given its callback ID. The ID is generated and
        returned when the function is connected to the key (section.setting).
        """
        for dummy_section, settings in self.callbacks.items():
            for dummy_setting, callbacks in settings.items():
                for cbid, func in callbacks:
                    if callback_id == cbid:
                        callbacks.remove((cbid, func))

    def emit(self, key):
        """
        Emits the signal "key" which will call the callbacks associated
        with that setting.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                f"Invalid config section.setting name: '{key}'"
            ) from error

        if section not in self.callbacks:
            raise AttributeError(f"No such config section name: '{section}'")
        if setting not in self.callbacks[section]:
            raise AttributeError(f"No such config setting name: '{section}.{setting}'")
        for dummy_cbid, func in self.callbacks[section][setting]:
            func(self, 0, str(self.data[section][setting]), None)

    def set(self, key, value):
        """
        Set the setting's value. There are only two ways to get into
        the data dictionary: via the :meth:`load` method that reads a file,
        or from this method.
        """
        try:
            section, setting = key.split(".", 1)
        except ValueError as error:
            raise AttributeError(
                "Invalid config section.setting name: '{key}'"
            ) from error

        self._validate_section_and_setting(section, setting)

        # Check value to see if right type:
        if self.has_default(key):
            if not self.check_type(self.get_default(key), value):
                raise AttributeError(
                    f"attempting to set '{key}' to wrong type "
                    f"'{type(value)}'; should be "
                    f"'{type(self.get_default(key))}'"
                )
        if setting in self.data[section] and self.data[section][setting] == value:
            # Do nothing if existed and is the same
            pass
        else:
            # Set the value:
            self.data[section][setting] = value
            # Only call callback if the value changed!
            if section in self.callbacks and setting in self.callbacks[section]:
                self.emit(key)

    def check_type(self, value1, value2):
        """
        Check if value1 and value2 are different types.
        """
        type1 = type(value1)
        type2 = type(value2)
        if type1 == type2:
            return True
        if isinstance(value1, str) and isinstance(value2, str):
            return True
        if type1 in [int, float] and type2 in [int, float]:
            return True
        return False


def get_raw_value(parser, section, option):
    """
    Prepare and return raw value.
    """
    raw_value = parser.get(section, option).strip()
    if raw_value[:2] == "u'":
        raw_value = raw_value[1:]
    elif raw_value.startswith("["):
        raw_value = raw_value.replace(", u'", ", '")
        raw_value = raw_value.replace("[u'", "['")
    return raw_value


def write_comments(output_file, comments):
    """
    Sanity check and write comments out to a .ini file.
    """
    if comments:
        if not isinstance(comments, list):
            raise AttributeError("Comments should be a list")

        output_file.write("\n")
        for comment in comments:
            if not isinstance(comment, str):
                raise AttributeError("Comment should be a string")
            clean_comment = comment.strip("; \n")
            output_file.write(f";; {clean_comment}\n")
