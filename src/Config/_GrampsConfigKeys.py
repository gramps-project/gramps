#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006  Donald N. Allingham
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

DEFAULT_SOURCE       = ('preferences','default-source', 0)
RELATION_SHADE       = ('preferences','relation-shade', 0)
ONLINE_MAPS          = ('preferences','online-maps', 0)
FAMILY_DETAILS       = ('preferences','family-details', 0)
COMPLETE_COLOR       = ('preferences','complete-color', 2)
TODO_COLOR           = ('preferences','todo-color', 2)
CUSTOM_MARKER_COLOR  = ('preferences','custom-marker-color', 2)
FAMILY_WARN          = ('preferences','family-warn', 0)
HIDE_EP_MSG          = ('preferences','hide-ep-msg', 0)
LAST_VIEW            = ('preferences','last-view', 1)
FAMILY_SIBLINGS      = ('preferences','family-siblings', 0)
AUTOLOAD             = ('behavior','autoload', 0)
SPELLCHECK           = ('behavior','spellcheck', 0)
BETAWARN             = ('behavior','betawarn', 0)
WELCOME              = ('behavior','welcome', 1)
DATE_FORMAT          = ('preferences','date-format', 1)
DONT_ASK             = ('interface','dont-ask', 0)
HEIGHT               = ('interface','height', 1)
WIDTH                = ('interface','width', 1)
FILTER               = ('interface','filter', 0)
FPREFIX              = ('preferences','fprefix', 2)
EPREFIX              = ('preferences','eprefix', 2)
RPREFIX              = ('preferences','rprefix', 2)
IPREFIX              = ('preferences','iprefix', 2)
OPREFIX              = ('preferences','oprefix', 2)
PPREFIX              = ('preferences','pprefix', 2)
SPREFIX              = ('preferences','sprefix', 2)
GOUTPUT_PREFERENCE   = ('preferences','goutput-preference', 2)
OUTPUT_PREFERENCE    = ('preferences','output-preference', 2)
PAPER_PREFERENCE     = ('preferences','paper-preference', 2)
RECENT_FILE          = ('paths','recent-file', 2)
RECENT_IMPORT_DIR    = ('paths','recent-import-dir', 2)
RECENT_EXPORT_DIR    = ('paths','recent-export-dir', 2)
NAME_FORMAT          = ('preferences','name-format', 1)
REPORT_DIRECTORY     = ('paths','report-directory', 2)
RESEARCHER_ADDR      = ('researcher','researcher-addr', 2)
RESEARCHER_CITY      = ('researcher','researcher-city', 2)
RESEARCHER_COUNTRY   = ('researcher','researcher-country', 2)
RESEARCHER_EMAIL     = ('researcher','researcher-email', 2)
RESEARCHER_NAME      = ('researcher','researcher-name', 2)
RESEARCHER_PHONE     = ('researcher','researcher-phone', 2)
RESEARCHER_POSTAL    = ('researcher','researcher-postal', 2)
RESEARCHER_STATE     = ('researcher','researcher-state', 2)
STARTUP              = ('behavior','startup', 1)
SIZE_CHECKED         = ('interface','size-checked', 0)
STATUSBAR            = ('interface','statusbar', 1)
SURNAME_GUESSING     = ('behavior','surname-guessing', 1)
TOOLBAR_ON           = ('interface','toolbar-on', 0)
USE_TIPS             = ('behavior','use-tips', 0)
POP_PLUGIN_STATUS    = ('behavior','pop-plugin-status', 0)
VIEW                 = ('interface','view', 0)
SIDEBAR_TEXT         = ('interface','sidebar-text', 0)
WEBSITE_DIRECTORY    = ('paths','website-directory', 2)


default_value = {
    DEFAULT_SOURCE       : False,
    RELATION_SHADE       : True,
    ONLINE_MAPS          : False,
    FAMILY_DETAILS       : True,
    COMPLETE_COLOR       : '#008b00',
    TODO_COLOR           : '#ff0000',
    CUSTOM_MARKER_COLOR  : '#8b008b',
    FAMILY_WARN          : True,
    HIDE_EP_MSG          : False,
    LAST_VIEW            : 0,
    FAMILY_SIBLINGS      : True,
    AUTOLOAD             : False,
    SPELLCHECK           : False,
    BETAWARN             : False,
    WELCOME              : 100,
    DATE_FORMAT          : 0,
    DONT_ASK             : False,
    HEIGHT               : 500,
    WIDTH                : 775,
    FILTER               : False,
    FPREFIX              : 'F%04d',
    EPREFIX              : 'E%04d',
    RPREFIX              : 'R%04d',
    IPREFIX              : 'I%04d',
    OPREFIX              : 'O%04d',
    PPREFIX              : 'P%04d',
    SPREFIX              : 'S%04d',
    GOUTPUT_PREFERENCE   : 'No default format',
    OUTPUT_PREFERENCE    : 'No default format',
    PAPER_PREFERENCE     : 'Letter',
    RECENT_FILE          : '',
    RECENT_IMPORT_DIR    : '',
    RECENT_EXPORT_DIR    : '',
    NAME_FORMAT          : 1,
    REPORT_DIRECTORY     : './',
    RESEARCHER_ADDR      : '',
    RESEARCHER_CITY      : '',
    RESEARCHER_COUNTRY   : '',
    RESEARCHER_EMAIL     : '',
    RESEARCHER_NAME      : '',
    RESEARCHER_PHONE     : '',
    RESEARCHER_POSTAL    : '',
    RESEARCHER_STATE     : '',
    STARTUP              : 0,
    SIZE_CHECKED         : False,
    STATUSBAR            : 1,
    SURNAME_GUESSING     : 0,
    TOOLBAR_ON           : True,
    USE_TIPS             : False,
    POP_PLUGIN_STATUS    : False,
    VIEW                 : True,
    SIDEBAR_TEXT         : True,
    WEBSITE_DIRECTORY    : './',
}
