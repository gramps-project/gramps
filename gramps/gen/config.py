# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Gary Burton
# Copyright (C) 2009-2012  Doug Blank <doug.blank@gmail.com>
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
This package implements access to Gramps configuration.
"""

#---------------------------------------------------------------
#
# Gramps imports
#
#---------------------------------------------------------------
import os
import re
import logging

#---------------------------------------------------------------
#
# Gramps imports
#
#---------------------------------------------------------------
from .const import HOME_DIR, USER_HOME, VERSION_DIR
from .utils.configmanager import ConfigManager
from .const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
    return value

#---------------------------------------------------------------
#
# Constants
#
#---------------------------------------------------------------
INIFILE = os.path.join(VERSION_DIR, "gramps.ini")

#---------------------------------------------------------------
#
# Module functions
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

CONFIGMAN = ConfigManager(INIFILE, "plugins")

register('behavior.addmedia-image-dir', '')
register('behavior.addmedia-relative-path', False)
register('behavior.autoload', False)
register('behavior.avg-generation-gap', 20)
register('behavior.betawarn', False)
register('behavior.check-for-addon-updates', 0)
register('behavior.check-for-addon-update-types', ["new"])
register('behavior.last-check-for-addon-updates', "1970/01/01")
register('behavior.previously-seen-addon-updates', [])
register('behavior.do-not-show-previously-seen-addon-updates', True)
register('behavior.date-about-range', 50)
register('behavior.date-after-range', 50)
register('behavior.date-before-range', 50)
register('behavior.generation-depth', 15)
register('behavior.max-age-prob-alive', 110)
register('behavior.max-sib-age-diff', 20)
register('behavior.min-generation-years', 13)
register('behavior.owner-warn', False)
register('behavior.pop-plugin-status', False)
register('behavior.recent-export-type', 3)
register('behavior.spellcheck', False)
register('behavior.startup', 0)
register('behavior.surname-guessing', 0)
register('behavior.translator-needed', True)
register('behavior.use-tips', False)
register('behavior.welcome', 100)
register('behavior.web-search-url', 'http://google.com/#&q=%(text)s')
register('behavior.addons-url', "https://raw.githubusercontent.com/gramps-project/addons/master/gramps51")

register('database.backend', 'bsddb')
register('database.compress-backup', True)
register('database.backup-path', USER_HOME)
register('database.backup-on-exit', True)
register('database.autobackup', 0)
register('database.path', os.path.join(HOME_DIR, 'grampsdb'))
register('database.host', '')
register('database.port', '')

register('export.proxy-order',
         [["privacy", 0],
          ["living", 0],
          ["person", 0],
          ["note", 0],
          ["reference", 0]]
        )

register('geography.center-lon', 0.0)
register('geography.lock', False)
register('geography.center-lat', 0.0)
register('geography.map', "person")
register('geography.map_service', 1)
register('geography.zoom', 0)
register('geography.zoom_when_center', 12)
register('geography.show_cross', False)
register('geography.path', "")
register('geography.use-keypad', True)

# note that other calls to "register" are done in realtime (when
# needed), for instance to four 'interface.clipboard' variables --
# so do a recursive grep for "setup_configs" to see all the (base) names
register('interface.dont-ask', False)
register('interface.view-categories',
         ["Dashboard", "People", "Relationships", "Families",
          "Ancestry", "Events", "Places", "Geography", "Sources",
          "Citations", "Repositories", "Media", "Notes"])
register('interface.filter', False)
register('interface.fullscreen', False)
register('interface.grampletbar-close', False)
register('interface.ignore-gexiv2', False)
register('interface.ignore-pil', False)
register('interface.ignore-osmgpsmap', False)
register('interface.main-window-height', 500)
register('interface.main-window-horiz-position', 15)
register('interface.main-window-vert-position', 10)
register('interface.main-window-width', 775)
register('interface.mapservice', 'OpenStreetMap')
register('interface.open-with-default-viewer', False)
register('interface.pedview-layout', 0)
register('interface.pedview-show-images', True)
register('interface.pedview-show-marriage', False)
register('interface.pedview-tree-size', 5)
register('interface.pedview-tree-direction', 2)
register('interface.pedview-show-unknown-people', False)
register('interface.place-name-height', 100)
register('interface.place-name-width', 450)
register('interface.sidebar-text', True)
register('interface.size-checked', False)
register('interface.statusbar', 1)
register('interface.toolbar-on', True)
register('interface.toolbar-text', False)
register('interface.view', True)
register('interface.surname-box-height', 150)
register('interface.treemodel-cache-size', 1000)

register('paths.recent-export-dir', USER_HOME)
register('paths.recent-file', '')
register('paths.recent-import-dir', USER_HOME)
register('paths.report-directory', USER_HOME)
register('paths.website-directory', USER_HOME)
register('paths.website-cms-uri', '')
register('paths.website-cal-uri', '')
register('paths.website-extra-page-uri', '')
register('paths.website-extra-page-name', '')
register('paths.quick-backup-directory', USER_HOME)
register('paths.quick-backup-filename',
         "%(filename)s_%(year)d-%(month)02d-%(day)02d.%(extension)s")

register('preferences.quick-backup-include-mode', False)
register('preferences.date-format', 0)
register('preferences.calendar-format-report', 0)
register('preferences.cprefix', 'C%04d')
register('preferences.alternate-fonthandler', False)
register('preferences.default-source', False)
register('preferences.tag-on-import', False)
register('preferences.tag-on-import-format', _("Imported %Y/%m/%d %H:%M:%S"))
register('preferences.eprefix', 'E%04d')
register('preferences.family-warn', True)
register('preferences.fprefix', 'F%04d')
register('preferences.hide-ep-msg', False)
register('preferences.invalid-date-format', "<b>%s</b>")
register('preferences.iprefix', 'I%04d')
register('preferences.name-format', 1)
register('preferences.place-format', 0)
register('preferences.place-auto', True)
register('preferences.patronimic-surname', False)
register('preferences.no-given-text', "[%s]" % _("Missing Given Name"))
register('preferences.no-record-text', "[%s]" % _("Missing Record"))
register('preferences.no-surname-text', "[%s]" % _("Missing Surname"))
register('preferences.nprefix', 'N%04d')
register('preferences.online-maps', False)
register('preferences.oprefix', 'O%04d')
register('preferences.paper-metric', 0)
register('preferences.paper-preference', 'Letter')
register('preferences.pprefix', 'P%04d')
register('preferences.private-given-text', "%s" % _T_("[Living]"))
register('preferences.private-record-text', "[%s]" % _("Private Record"))
register('preferences.private-surname-text', "%s" % _T_("[Living]"))
register('preferences.rprefix', 'R%04d')
register('preferences.sprefix', 'S%04d')
register('preferences.use-last-view', False)
register('preferences.last-view', '')
register('preferences.last-views', [])
register('preferences.family-relation-type', 3) # UNKNOWN
register('preferences.age-display-precision', 1)

register('colors.scheme', 0)
register('colors.male-alive', ['#b8cee6', '#1f344a'])
register('colors.male-dead', ['#b8cee6', '#2d3039'])
register('colors.female-alive', ['#feccf0', '#62242D'])
register('colors.female-dead', ['#feccf0', '#3a292b'])
register('colors.unknown-alive', ['#f3dbb6', '#75507B'])
register('colors.unknown-dead', ['#f3dbb6', '#35103b'])
register('colors.family', ['#eeeeee', '#454545'])
register('colors.family-divorced', ['#ffdede', '#5c3636'])
register('colors.home-person', ['#bbe68a', '#304918'])
register('colors.border-male-alive', ['#1f4986', '#171d26'])
register('colors.border-male-dead', ['#000000', '#000000'])
register('colors.border-female-alive', ['#861f69', '#261111'])
register('colors.border-female-dead', ['#000000', '#000000'])
register('colors.border-unknown-alive', ['#8e5801', '#8e5801'])
register('colors.border-unknown-dead', ['#000000', '#000000'])
register('colors.border-family', ['#cccccc', '#252525'])
register('colors.border-family-divorced', ['#ff7373', '#720b0b'])

register('researcher.researcher-addr', '')
register('researcher.researcher-locality', '')
register('researcher.researcher-city', '')
register('researcher.researcher-country', '')
register('researcher.researcher-email', '')
register('researcher.researcher-name', '')
register('researcher.researcher-phone', '')
register('researcher.researcher-postal', '')
register('researcher.researcher-state', '')

register('plugin.hiddenplugins', [])
register('plugin.addonplugins', [])

if __debug__: # enable a simple CLI test to see if the datestrings exist
    register('test.january', _("localized lexeme inflections||January"))

#---------------------------------------------------------------
#
# Upgrade Conversions go here.
#
#---------------------------------------------------------------

# If we have not already upgraded to this version,
# we can tell by seeing if there is a key file for this version:
if not os.path.exists(CONFIGMAN.filename):
    # If not, let's read old if there:
    if os.path.exists(os.path.join(HOME_DIR, "keys.ini")):
        # read it in old style:
        logging.warning("Importing old key file 'keys.ini'...")
        CONFIGMAN.load(os.path.join(HOME_DIR, "keys.ini"),
                       oldstyle=True)
        logging.warning("Done importing old key file 'keys.ini'")
    # other version upgrades here...
    # check previous version of gramps:
    fullpath, filename = os.path.split(CONFIGMAN.filename)
    fullpath, previous = os.path.split(fullpath)
    match = re.match(r'gramps(\d*)', previous)
    if match:
        # cycle back looking for previous versions of gramps
        for i in range(1, 20): # check back 2 gramps versions
            # -----------------------------------------
            # TODO: Assumes minor version is a decimal, not semantic versioning
            #       Uses ordering ... 4.9, 5.0, 5.1, ...
            #       Not ... 4.9, 4.10, 4.11, 5.0, 5.1, ...
            # If not true, need to add a different method to auto upgrade.
            # Perhaps addings specific list of versions to check
            # -----------------------------------------
            digits = str(int(match.groups()[0]) - i)
            previous_grampsini = os.path.join(fullpath, "gramps" + digits,
                                              filename)
            if os.path.exists(previous_grampsini):
                logging.warning("Importing old config file '%s'...",
                                previous_grampsini)
                CONFIGMAN.load(previous_grampsini)
                logging.warning("Done importing old config file '%s'",
                                previous_grampsini)
                break

#---------------------------------------------------------------
#
# Now, load the settings from the config file, if one
#
#---------------------------------------------------------------
CONFIGMAN.load()

config = CONFIGMAN
