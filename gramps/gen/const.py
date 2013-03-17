# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2012       Doug Blank
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
Provides constants for other modules
"""

from __future__ import unicode_literals

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
from .ggettext import sgettext as _
from .svn_revision import get_svn_revision

#-------------------------------------------------------------------------
#
# Gramps Version
#
#-------------------------------------------------------------------------
PROGRAM_NAME   = "Gramps"
VERSION        = "4.0.0-alpha4"
if VERSION == "@" + "VERSIONSTRING" + "@":
    raise Exception("Please run 'python setup.py build'")
def get_version_tuple(v):
    """ Get the numeric-dotted part of version number"""
    retval = ""
    for c in v:
        if c.isdigit() or (c == "." and retval.count(".") <= 1):
            retval += c
        else:
            break
    return tuple(map(int, retval.split(".")))
VERSION_TUPLE  = get_version_tuple(VERSION)
major_version = "%s.%s" % (VERSION_TUPLE[0], VERSION_TUPLE[1])

#-------------------------------------------------------------------------
#
# Standard GRAMPS Websites
#
#-------------------------------------------------------------------------
URL_HOMEPAGE    = "http://gramps-project.org/"
URL_MAILINGLIST = "http://sourceforge.net/mail/?group_id=25770"
URL_BUGTRACKER  = "http://bugs.gramps-project.org/bug_report_advanced_page.php"
URL_WIKISTRING  = "http://gramps-project.org/wiki/index.php?title="
URL_MANUAL_PAGE = "Gramps_%s_Wiki_Manual" % major_version
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
# Platforms
# Never test on LINUX, handle Linux in the else statement as default
#
#-------------------------------------------------------------------------
LINUX = ["Linux", "linux", "linux2"]
MACOS = ["Darwin", "darwin"]
WINDOWS = ["Windows", "win32"]


#-------------------------------------------------------------------------
#
# Determine the home directory. According to Wikipedia, most UNIX like
# systems use HOME. I'm assuming that this would apply to OS X as well.
# Windows apparently uses USERPROFILE
#
#-------------------------------------------------------------------------
if 'GRAMPSHOME' in os.environ:
    USER_HOME = os.environ['GRAMPSHOME'] 
    HOME_DIR = os.path.join(USER_HOME, 'gramps')
elif 'USERPROFILE' in os.environ:
    USER_HOME = os.environ['USERPROFILE'] 
    if 'APPDATA' in os.environ:
        HOME_DIR = os.path.join(os.environ['APPDATA'], 'gramps')
    else:
        HOME_DIR = os.path.join(USER_HOME, 'gramps')
else:
    USER_HOME = os.environ['HOME'] 
    HOME_DIR = os.path.join(USER_HOME, '.gramps')

# Conversion of USER_HOME to unicode was needed to have better
# support for non ASCII path names in Windows for the Gramps database.

if sys.version_info[0] < 3:
    if not isinstance(USER_HOME, unicode):
        USER_HOME = unicode(USER_HOME, sys.getfilesystemencoding())
    if not isinstance(HOME_DIR, unicode):
        HOME_DIR = unicode(HOME_DIR, sys.getfilesystemencoding())
else:
    pass

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
USER_DIRLIST = (HOME_DIR, VERSION_DIR, ENV_DIR, TEMP_DIR, THUMB_DIR,
                THUMB_NORMAL, THUMB_LARGE, USER_PLUGINS)

#-------------------------------------------------------------------------
#
# Paths to python modules - assumes that the root directory is one level 
# above this one, and that the plugins directory is below the root directory.
#
#-------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(
            __file__), os.pardir))
if sys.version_info[0] < 3:
    # test for sys.frozen to detect a py2exe executable on Windows
    if hasattr(sys, "frozen"):
        ROOT_DIR = os.path.abspath(os.path.dirname(
            unicode(sys.executable, sys.getfilesystemencoding())))
    else:
        ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(
            unicode(__file__, sys.getfilesystemencoding())), os.pardir))

VERSION += get_svn_revision(ROOT_DIR)

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
WEBSTUFF_DIR       = os.path.join(PLUGINS_DIR, "webstuff")
WEBSTUFF_IMAGE_DIR = os.path.join(WEBSTUFF_DIR, "images")

USE_TIPS = False

if os.sys.platform in WINDOWS:
    USE_THUMBNAILER = False
else:
    USE_THUMBNAILER = True

#-------------------------------------------------------------------------
#
# Paths to data files.
#
#-------------------------------------------------------------------------
LOCALE_DIR = "/Users/tim/gramps/gramps40/build/mo"
DATA_DIR = "/Users/tim/gramps/gramps40/data"
IMAGE_DIR = "/Users/tim/gramps/gramps40/images"
DOC_DIR = "/Users/tim/gramps/gramps40"

TIP_DATA = os.path.join(DATA_DIR, "tips.xml")
PAPERSIZE = os.path.join(DATA_DIR, "papersize.xml")

ICON = os.path.join(IMAGE_DIR, "gramps.png")
LOGO = os.path.join(IMAGE_DIR, "logo.png")
SPLASH = os.path.join(IMAGE_DIR, "splash.jpg")

LICENSE_FILE = os.path.join(DOC_DIR, 'COPYING')

#-------------------------------------------------------------------------
#
# About box information
#
#-------------------------------------------------------------------------
COPYRIGHT_MSG  = "© 2001-2006 Donald N. Allingham\n" \
                 "© 2007-2013 The Gramps Developers"
COMMENTS       = _("Gramps (Genealogical Research and Analysis "
                   "Management Programming System) is a personal "
                   "genealogy program.")
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
    ]
    
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.xml")

DOCUMENTERS    = [
    'Alexander Roitman', 
    ]

TRANSLATORS = _('TRANSLATORS: Translate this to your '
                'name in your native language')

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
]

SHORTOPTS = "O:C:i:e:f:a:p:d:c:lLhuv?s"

GRAMPS_UUID =  uuid.UUID('516cd010-5a41-470f-99f8-eb22f1098ad6')

def need_to_update_const():
    """ Check to see if this file is older than 
        setup.py or const.py.in """
    this_file = os.path.join(ROOT_DIR, "gen", "const.py")
    in_file = os.path.join(ROOT_DIR, "gen", "const.py.in")
    setup_file = os.path.join(ROOT_DIR, "..", "setup.py")

    if (os.path.exists(this_file) and 
        os.path.exists(in_file) and 
        os.path.exists(setup_file)):

        this_file_time = os.path.getmtime(this_file)
        in_file_time = os.path.getmtime(in_file)
        setup_file_time = os.path.getmtime(setup_file)

        # Is this file older than others? If so,
        # need to run setup
        return (this_file_time < in_file_time or
                this_file_time < setup_file_time)
    else:
        # Can't tell because can't find the files
        return False

if need_to_update_const():
    print("Outdated gramps.gen.const; please run 'python setup.py build'")
