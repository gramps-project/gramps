# -*- coding: utf-8 -*-
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
from gettext import gettext as _

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
# Gramps imports
#
#---------------------------------------------------------------
import const

#---------------------------------------------------------------
#
# Constants
#
#---------------------------------------------------------------
INIFILE = os.path.join(const.HOME_DIR, "gramps32.ini")

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
        self.filename = filename
        self.callbacks = {}
        self.default = {}
        self.data = {}
        self.reset()

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

#---------------------------------------------------------------
#
# Convience functions to call ConfigManager instance methods
#
#---------------------------------------------------------------

def register(key, value):
    """ Module shortcut to register key, value """
    return CONFIGMAN.register(key, value)

def get(key):
    """ Module shortcut to get value from key """
    return CONFIGMAN.get(key)

def get_default(key):
    """ Module shortcut to get default from key """
    return CONFIGMAN.get_default(key)

def has_default(key):
    """ Module shortcut to get see if there is a default for key """
    return CONFIGMAN.has_default(key)

def get_sections():
    """ Module shortcut to get all section names of settings """
    return CONFIGMAN.get_sections()

def get_section_settings(section):
    """ Module shortcut to get all settings of a section """
    return CONFIGMAN.get_section_settings(section)

def set(key, value):
    """ Module shortcut to set value from key """
    return CONFIGMAN.set(key, value)

def is_set(key):
    """ Module shortcut to set value from key """
    return CONFIGMAN.is_set(key)

def save(filename=None):
    """ Module shortcut to save config file """
    return CONFIGMAN.save(filename)

def connect(key, func):
    """ 
    Module shortcut to connect a key to a callback func.
    Returns a unique callback ID number.
    """
    return CONFIGMAN.connect(key, func)

def disconnect(callback_id):
    """ Module shortcut to remove callback by ID number """
    return CONFIGMAN.disconnect(callback_id)

def reset(key=None):
    """ Module shortcut to reset some or all config data """
    return CONFIGMAN.reset(key)

def load(filename=None, oldstyle=False):
    """ Module shortcut to load an INI file into config data """
    return CONFIGMAN.load(filename, oldstyle)

def emit(key):
    """ Module shortcut to call all callbacks associated with key """
    return CONFIGMAN.emit(key)

#---------------------------------------------------------------
#
# Register the system-wide settings in a singleton config manager
#
#---------------------------------------------------------------

CONFIGMAN = ConfigManager(INIFILE)

register('behavior.addmedia-image-dir', '')
register('behavior.addmedia-relative-path', False)
register('behavior.autoload', False)
register('behavior.avg-generation-gap', 20)
register('behavior.betawarn', False)
register('behavior.database-path', os.path.join( const.HOME_DIR, 'grampsdb'))
register('behavior.date-about-range', 10)
register('behavior.date-after-range', 10)
register('behavior.date-before-range', 10)
register('behavior.generation-depth', 15)
register('behavior.max-age-prob-alive', 110)
register('behavior.max-sib-age-diff', 20)
register('behavior.min-generation-years', 13)
register('behavior.owner-warn', False)
register('behavior.pop-plugin-status', False)
register('behavior.recent-export-type', 1)
register('behavior.spellcheck', False)
register('behavior.startup', 0)
register('behavior.surname-guessing', 0)
register('behavior.use-tips', False)
register('behavior.welcome', 100)

register('export.no-private', True)
register('export.no-unlinked', True)
register('export.restrict-living', True)

register('geoview.latitude', "0.0")
register('geoview.lock', False)
register('geoview.longitude', "0.0")
register('geoview.map', "person")
register('geoview.stylesheet', "")
register('geoview.zoom', 0)

register('htmlview.start-url', "http://gramps-project.org")

register('interface.address-height', 450)
register('interface.address-width', 650)
register('interface.attribute-height', 350)
register('interface.attribute-width', 600)
register('interface.child-ref-height', 450)
register('interface.child-ref-width', 600)
register('interface.clipboard-height', 300)
register('interface.clipboard-width', 300)
register('interface.dont-ask', False)
register('interface.view-categories',
         ["Gramplets", "People", "Relationships", "Families", 
          "Ancestry", "Events", "Places", "Geography", "Sources",
          "Repositories", "Media", "Notes"])
register('interface.event-height', 450)
register('interface.event-ref-height', 450)
register('interface.event-ref-width', 600)
register('interface.event-sel-height', 450)
register('interface.event-sel-width', 600)
register('interface.event-width', 600)
register('interface.family-height', 500)
register('interface.family-sel-height', 450)
register('interface.family-sel-width', 600)
register('interface.family-width', 700)
register('interface.filter', False)
register('interface.fullscreen', False)
register('interface.height', 500)
register('interface.lds-height', 450)
register('interface.lds-width', 600)
register('interface.location-height', 250)
register('interface.location-width', 600)
register('interface.mapservice', 'OpenStreetMap')
register('interface.media-height', 450)
register('interface.media-ref-height', 450)
register('interface.media-ref-width', 600)
register('interface.media-sel-height', 450)
register('interface.media-sel-width', 600)
register('interface.media-width', 650)
register('interface.name-height', 350)
register('interface.name-width', 600)
register('interface.note-height', 500)
register('interface.note-sel-height', 450)
register('interface.note-sel-width', 600)
register('interface.note-width', 700)
register('interface.patro-title', 0)
register('interface.pedview-layout', 0)
register('interface.pedview-show-images', True)
register('interface.pedview-show-marriage', False)
register('interface.pedview-tree-size', 0)
register('interface.pedviewext-layout', 0)
register('interface.pedviewext-show-images', True)
register('interface.pedviewext-show-marriage', False)
register('interface.pedviewext-tree-size', 5)
register('interface.pedviewext-tree-direction', 2)
register('interface.pedviewext-scroll-direction', False)
register('interface.pedviewext-show-unknown-peoples', False)
register('interface.person-height', 550)
register('interface.person-ref-height', 350)
register('interface.person-ref-width', 600)
register('interface.person-sel-height', 450)
register('interface.person-sel-width', 600)
register('interface.person-width', 750)
register('interface.place-height', 450)
register('interface.place-sel-height', 450)
register('interface.place-sel-width', 600)
register('interface.place-width', 650)
register('interface.prefix-suffix', 0)
register('interface.releditbtn', False)
register('interface.repo-height', 450)
register('interface.repo-ref-height', 450)
register('interface.repo-ref-width', 600)
register('interface.repo-sel-height', 450)
register('interface.repo-sel-width', 600)
register('interface.repo-width', 650)
register('interface.sidebar-text', True)
register('interface.size-checked', False)
register('interface.source-height', 450)
register('interface.source-ref-height', 450)
register('interface.source-ref-width', 600)
register('interface.source-sel-height', 450)
register('interface.source-sel-width', 600)
register('interface.source-width', 600)
register('interface.statusbar', 1)
register('interface.toolbar-on', True)
register('interface.url-height', 150)
register('interface.url-width', 600)
register('interface.view', True)
register('interface.width', 775)

register('paths.recent-export-dir', '')
register('paths.recent-file', '')
register('paths.recent-import-dir', '')
register('paths.report-directory', const.USER_HOME)
register('paths.website-directory', const.USER_HOME)

register('preferences.complete-color', '#008b00')
register('preferences.custom-marker-color', '#8b008b')
register('preferences.date-format', 0)
register('preferences.date-format-report', 0)
register('preferences.calendar-format-report', 0)
register('preferences.default-source', False)
register('preferences.eprefix', 'E%04d')
register('preferences.family-details', True)
register('preferences.family-siblings', True)
register('preferences.family-warn', True)
register('preferences.fprefix', 'F%04d')
register('preferences.hide-ep-msg', False)
register('preferences.invalid-date-format', "<b>%s</b>")
register('preferences.iprefix', 'I%04d')
register('preferences.last-view', '')
register('preferences.name-format', 1)
register('preferences.no-given-text', "[%s]" % _("Missing Given Name"))
register('preferences.no-record-text', "[%s]" % _("Missing Record"))
register('preferences.no-surname-text', "[%s]" % _("Missing Surname"))
register('preferences.nprefix', 'N%04d')
register('preferences.online-maps', False)
register('preferences.oprefix', 'O%04d')
register('preferences.paper-metric', 0)
register('preferences.paper-preference', 'Letter')
register('preferences.pprefix', 'P%04d')
register('preferences.private-given-text', "[%s]" % _("Living"))
register('preferences.private-record-text', "[%s]" % _("Private Record"))
register('preferences.private-surname-text', "[%s]" % _("Living"))
register('preferences.relation-display-theme', "CLASSIC")
register('preferences.relation-shade', True)
register('preferences.rprefix', 'R%04d')
register('preferences.sprefix', 'S%04d')
register('preferences.todo-color', '#ff0000')
register('preferences.use-last-view', True)

register('person-view.columns', [(1, 0, 250), (1, 1, 50), (1, 2, 75), 
                                 (1, 3, 100), (1, 4, 175), (1, 5, 100), 
                                 (1, 6, 175), (1, 7, 100), (0, 8, 100)])
register('child-view.columns', [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), 
                                (1, 5), (0, 6), (0, 7)])
register('place-view.columns', [(1, 0, 250), (1, 1, 75), (1, 11, 100), 
                                (0, 3, 100), (1, 4, 100, ), (0, 5, 150), 
                                (1, 6, 150), (0, 7, 150), (0, 8, 150), 
                                (0, 9, 150), (0, 10, 150),(0,2,100)])
register('source-view.columns', [(1, 0, 200), (1, 1, 75), (1, 2, 150), 
                                 (0, 3, 100), (1, 4, 150), (0, 5, 100)])
register('media-view.columns', [(1, 0, 200, ), (1, 1, 75), (1, 2, 100), 
                                (1, 3, 200), (1, 5, 150), (0, 4, 150)])
register('repository-view.columns', [(1, 0, 200), (1, 1, 75), (0, 5, 100), 
                                     (0, 6, 100), (1, 2, 100), (1, 3, 250), 
                                     (1, 4, 100), (0, 7, 100), (0, 8, 100), 
                                     (0, 9, 100), (0, 10, 100), (0, 12, 100)])
register('event-view.columns', [(1, 0, 200), (1, 1, 75), (1, 2, 100), 
                                (0, 6, 230), (1, 3, 150),
                                (1, 4, 200), (0, 5, 100)])
register('family-view.columns', [(1, 0, 75), (1, 1, 200), (1, 2, 200), 
                                 (1, 3, 100), (0, 4, 100)])
register('note-view.columns', [(1, 0, 350), (1, 1, 75), (1, 2, 100), 
                               (1, 3, 100)])

register('researcher.researcher-addr', '')
register('researcher.researcher-city', '')
register('researcher.researcher-country', '')
register('researcher.researcher-email', '')
register('researcher.researcher-name', '')
register('researcher.researcher-phone', '')
register('researcher.researcher-postal', '')
register('researcher.researcher-state', '')

register('plugin.hiddenplugins', [])

#---------------------------------------------------------------
#
# Upgrade Conversions go here.
#
#---------------------------------------------------------------

# If we have not already upgraded to this version,
# we can tell by seeing if there is a key file for this version:
if not os.path.exists(CONFIGMAN.filename):
    # If not, let's read old if there:
    if os.path.exists(os.path.join(const.HOME_DIR, "keys.ini")):
        # read it in old style:
        print >> sys.stderr, "Importing old key file 'keys.ini'..."
        CONFIGMAN.load(os.path.join(const.HOME_DIR, "keys.ini"),
                            oldstyle=True)
        print >> sys.stderr, "Done importing old key file 'keys.ini'"
    # other version upgrades here...

#---------------------------------------------------------------
#
# Now, load the settings from the config file, if one
#
#---------------------------------------------------------------
CONFIGMAN.load()
