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
# Gramps imports
#
#---------------------------------------------------------------
import os
from gettext import gettext as _

#---------------------------------------------------------------
#
# Gramps imports
#
#---------------------------------------------------------------
import const
from gen.utils import ConfigManager

#---------------------------------------------------------------
#
# Constants
#
#---------------------------------------------------------------
INIFILE = os.path.join(const.HOME_DIR, "gramps32.ini")

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

config = CONFIGMAN
