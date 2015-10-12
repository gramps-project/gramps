# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2012       Doug Blank
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
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
Provides constants for other modules
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
import uuid

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .git_revision import get_git_revision
from .constfunc import get_env_var, conv_to_unicode
#-------------------------------------------------------------------------
#
# Gramps Version
#
#-------------------------------------------------------------------------
PROGRAM_NAME   = "Gramps"
from gramps.version import VERSION, VERSION_TUPLE, major_version
#-------------------------------------------------------------------------
#
# Standard GRAMPS Websites
#
#-------------------------------------------------------------------------
URL_HOMEPAGE    = "http://gramps-project.org/"
URL_MAILINGLIST = "http://sourceforge.net/mail/?group_id=25770"
URL_BUGHOME     = "http://bugs.gramps-project.org"
URL_BUGTRACKER  = "http://bugs.gramps-project.org/bug_report_page.php"
URL_WIKISTRING  = "http://gramps-project.org/wiki/index.php?title="
URL_MANUAL_PAGE = "Gramps_%s_Wiki_Manual" % major_version
URL_MANUAL_DATA = '%s_-_Entering_and_editing_data:_detailed' % URL_MANUAL_PAGE
URL_MANUAL_SECT1 = '%s_-_part_1' % URL_MANUAL_DATA
URL_MANUAL_SECT2 = '%s_-_part_2' % URL_MANUAL_DATA
URL_MANUAL_SECT3 = '%s_-_part_3' % URL_MANUAL_DATA
WIKI_FAQ = "FAQ"
WIKI_KEYBINDINGS = "Gramps_%s_Wiki_Manual_-_Keybindings" % major_version
WIKI_EXTRAPLUGINS= "%s_Addons" % major_version
WIKI_EXTRAPLUGINS_RAWDATA = "Plugins%s&action=raw" % major_version

#-------------------------------------------------------------------------
#
# Mime Types
#
#-------------------------------------------------------------------------
APP_FAMTREE     = 'x-directory/normal'
APP_GRAMPS      = "application/x-gramps"
APP_GRAMPS_XML  = "application/x-gramps-xml"
APP_GEDCOM      = "application/x-gedcom"
APP_GRAMPS_PKG  = "application/x-gramps-package"
APP_GENEWEB     = "application/x-geneweb"
APP_VCARD       = ["text/x-vcard", "text/x-vcalendar"]

#-------------------------------------------------------------------------
#
# Determine the home directory. According to Wikipedia, most UNIX like
# systems use HOME. I'm assuming that this would apply to OS X as well.
# Windows apparently uses USERPROFILE
#
#-------------------------------------------------------------------------
if 'GRAMPSHOME' in os.environ:
    USER_HOME = get_env_var('GRAMPSHOME') 
    HOME_DIR = os.path.join(USER_HOME, 'gramps')
elif 'USERPROFILE' in os.environ:
    USER_HOME = get_env_var('USERPROFILE') 
    if 'APPDATA' in os.environ:
        HOME_DIR = os.path.join(get_env_var('APPDATA'), 'gramps')
    else:
        HOME_DIR = os.path.join(USER_HOME, 'gramps')
else:
    USER_HOME = get_env_var('HOME') 
    HOME_DIR = os.path.join(USER_HOME, '.gramps')


VERSION_DIR    = os.path.join(
    HOME_DIR, "gramps%s%s" % (VERSION_TUPLE[0], VERSION_TUPLE[1]))

CUSTOM_FILTERS = os.path.join(VERSION_DIR, "custom_filters.xml")
REPORT_OPTIONS = os.path.join(HOME_DIR, "report_options.xml")
TOOL_OPTIONS   = os.path.join(HOME_DIR, "tool_options.xml")

ENV_DIR        = os.path.join(HOME_DIR, "env")
TEMP_DIR       = os.path.join(HOME_DIR, "temp")
THUMB_DIR      = os.path.join(HOME_DIR, "thumb")
THUMB_NORMAL   = os.path.join(THUMB_DIR, "normal")
THUMB_LARGE    = os.path.join(THUMB_DIR, "large")
USER_PLUGINS   = os.path.join(VERSION_DIR, "plugins")
# dirs checked/made for each Gramps session
USER_DIRLIST = (USER_HOME, HOME_DIR, VERSION_DIR, ENV_DIR, TEMP_DIR, THUMB_DIR,
                THUMB_NORMAL, THUMB_LARGE, USER_PLUGINS)

#-------------------------------------------------------------------------
#
# Paths to python modules - assumes that the root directory is one level 
# above this one, and that the plugins directory is below the root directory.
#
#-------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(
    conv_to_unicode(__file__)), os.pardir))

sys.path.insert(0, ROOT_DIR)
git_revision = get_git_revision(ROOT_DIR)
if sys.platform == 'win32' and git_revision == "":
    git_revision = get_git_revision(os.path.split(ROOT_DIR)[1])
VERSION += git_revision
#VERSION += "-1"

#
# Glade files
#
GLADE_DIR      = os.path.join(ROOT_DIR, "gui", "glade")
GLADE_FILE     = os.path.join(GLADE_DIR, "gramps.glade")
PERSON_GLADE   = os.path.join(GLADE_DIR, "edit_person.glade")
PLUGINS_GLADE  = os.path.join(GLADE_DIR, "plugins.glade")
MERGE_GLADE    = os.path.join(GLADE_DIR, "mergedata.glade")
RULE_GLADE     = os.path.join(GLADE_DIR, "rule.glade")


PLUGINS_DIR        = os.path.join(ROOT_DIR, "plugins")
WEB_DIR            = os.path.join(ROOT_DIR, 'webapp')

USE_TIPS = False

if sys.platform == 'win32':
    USE_THUMBNAILER = False
else:
    USE_THUMBNAILER = True

#-------------------------------------------------------------------------
#
# Paths to data files.
#
#-------------------------------------------------------------------------
from gramps.gen.utils.resourcepath import ResourcePath
_resources = ResourcePath()
DATA_DIR = _resources.data_dir
IMAGE_DIR = _resources.image_dir

TIP_DATA = os.path.join(DATA_DIR, "tips.xml")
PAPERSIZE = os.path.join(DATA_DIR, "papersize.xml")

ICON = os.path.join(IMAGE_DIR, "gramps.png")
LOGO = os.path.join(IMAGE_DIR, "logo.png")
SPLASH = os.path.join(IMAGE_DIR, "splash.jpg")

LICENSE_FILE = os.path.join(_resources.doc_dir, 'COPYING')
#-------------------------------------------------------------------------
#
# Init Localization
#
#-------------------------------------------------------------------------
from gramps.gen.utils.grampslocale import GrampsLocale
GRAMPS_LOCALE = GrampsLocale(localedir=_resources.locale_dir)
_ = GRAMPS_LOCALE.translation.sgettext
GTK_GETTEXT_DOMAIN = 'gtk30'

#-------------------------------------------------------------------------
#
# About box information
#
#-------------------------------------------------------------------------
COPYRIGHT_MSG  = "© 2001-2006 Donald N. Allingham\n" \
                 "© 2007-2015 The Gramps Developers"
COMMENTS       = _("Gramps\n (Genealogical Research and Analysis "
                   "Management Programming System)\n"
                   "is a personal genealogy program.")
AUTHORS        = [
    "Alexander Roitman",
    "Benny Malengier", 
    "Brian Matherly",
    "Donald A. Peterson", 
    "Donald N. Allingham", 
    "David Hampton",  
    "Martin Hawlisch",
    "Richard Taylor", 
    "Tim Waugh",
    "John Ralls"
    ]
    
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.xml")

DOCUMENTERS    = [
    'Alexander Roitman', 
    ]

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
THUMBSCALE       = 96.0
THUMBSCALE_LARGE = 180.0
XMLFILE          = "data.gramps"
NO_SURNAME       = "(%s)" % _("none")
NO_GIVEN         = "(%s)" % _("none")
ARABIC_COMMA     = "،"
ARABIC_SEMICOLON = "؛"

#-------------------------------------------------------------------------
#
# Options Constants
#
#-------------------------------------------------------------------------

# Note: Make sure to edit argparser.py _help string too!
# (longName, shortName, type , default, flags, descrip , argDescrip)
POPT_TABLE = [
    ("config",  'c',  str, None, 0, "Set config setting(s) and start Gramps",  ""),
    ("open",    'O', str, None, 0, "Open family tree",  "FAMILY_TREE"), 
    ("create",  'C', str, None, 0, "Create or Open family tree",  "FAMILY_TREE"), 
    ("import",  'i', str, None, 0, "Import file",       "FILENAME"), 
    ("export",  'e', str, None, 0, "Export file",       "FILENAME"),
    ("format",  'f', str, None, 0, 'Specify format',    "FORMAT"), 
    ("action",  'a', str, None, 0, 'Specify action',    "ACTION"), 
    ("options", 'p', str, None, 0, 'Specify options',   "OPTIONS_STRING"), 
    ("debug",   'd', str, None, 0, 'Enable debug logs', "LOGGER_NAME"), 
    ("",        'l', None, None, 0, 'List Family Trees', ""),
    ("",        'L', None, None, 0, 'List Family Tree Details', ""),
    ("show",    's', None, None, 0, "Show config settings",  ""),
    ("force-unlock", 'u', None, None, 0, 'Force unlock of family tree', ""),
    ("version", 'v', None, None, 0, 'Show versions', ""),
]

LONGOPTS = [
    "action=", 
    "class=",
    "config=",
    "debug=",
    "display=",
    "disable-sound", 
    "disable-crash-dialog", 
    "enable-sound",
    "espeaker=",
    "export=",
    "force-unlock",
    "format=",
    "gdk-debug=", 
    "gdk-no-debug=", 
    "gtk-debug=", 
    "gtk-no-debug=", 
    "gtk-module=", 
    "g-fatal-warnings",
    "help",
    "import=", 
    "load-modules=",
    "list" 
    "name=",
    "oaf-activate-iid=", 
    "oaf-ior-fd=", 
    "oaf-private",
    "open=",
    "create=",
    "options=",
    "screen=",
    "show", 
    "sm-client-id=", 
    "sm-config-prefix=", 
    "sm-disable",
    "sync",
    "usage", 
    "version",
    "qml",
    "yes",
    "quiet",
]

SHORTOPTS = "O:C:i:e:f:a:p:d:c:lLthuv?syq"

GRAMPS_UUID =  uuid.UUID('516cd010-5a41-470f-99f8-eb22f1098ad6')
