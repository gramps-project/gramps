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

FAMILY_DETAILS       = ('preferences','family-details', 0)
FAMILY_SIBLINGS      = ('preferences','family-siblings', 0)
AUTOLOAD             = ('behavior','autoload', 0)
SPELLCHECK           = ('behavior','spellcheck', 0)
BETAWARN             = ('behavior','betawarn', 0)
FAMILY_WARN          = ('behavior','family-warn', 0)
WELCOME              = ('behavior','welcome', 1)
DATE_FORMAT          = ('preferences','date-format', 1)
DONT_ASK             = ('interface','dont-ask', 0)
DEFAULTVIEW          = ('interface','defaultview', 1)
HEIGHT               = ('interface','height', 1)
WIDTH                = ('interface','width', 1)
FAMILYVIEW           = ('interface','familyview', 1)
FILTER               = ('interface','filter', 0)
FPREFIX              = ('preferences','fprefix', 2)
EPREFIX              = ('preferences','eprefix', 2)
IPREFIX              = ('preferences','iprefix', 2)
OPREFIX              = ('preferences','oprefix', 2)
PPREFIX              = ('preferences','pprefix', 2)
SPREFIX              = ('preferences','sprefix', 2)
RPREFIX              = ('preferences','rprefix', 2)
GOUTPUT_PREFERENCE   = ('preferences','goutput-preference', 2)
OUTPUT_PREFERENCE    = ('preferences','output-preference', 2)
PAPER_PREFERENCE     = ('preferences','paper-preference', 2)
RECENT_FILE          = ('paths','recent-file', 2)
RECENT_IMPORT_DIR    = ('paths','recent-import-dir', 2)
RECENT_EXPORT_DIR    = ('paths','recent-export-dir', 2)
MAKE_REFERENCE       = ('behavior','make-reference', 0)
MEDIA_GLOBAL         = ('behavior','media-global', 0)
MEDIA_LOCAL          = ('behavior','media-local', 0)
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
SHOW_CALENDAR        = ('behavior','show-calendar', 0)
STARTUP              = ('behavior','startup', 1)
SIZE_CHECKED         = ('interface','size-checked', 0)
STATUSBAR            = ('interface','statusbar', 1)
SURNAME_GUESSING     = ('behavior','surname-guessing', 1)
TOOLBAR              = ('interface','toolbar', 1)
TOOLBAR_ON           = ('interface','toolbar-on', 0)
USE_LDS              = ('behavior','use-lds', 0)
USE_TIPS             = ('behavior','use-tips', 0)
POP_PLUGIN_STATUS    = ('behavior','pop-plugin-status', 0)
VIEW                 = ('interface','view', 0)
WEBSITE_DIRECTORY    = ('paths','website-directory', 2)


default_value = {
    FAMILY_DETAILS       : True,
    FAMILY_SIBLINGS      : True,
    AUTOLOAD             : False,
    SPELLCHECK           : False,
    BETAWARN             : False,
    FAMILY_WARN          : False,
    WELCOME              : 100,
    DATE_FORMAT          : 0,
    DONT_ASK             : False,
    DEFAULTVIEW          : 0,
    HEIGHT               : 500,
    WIDTH                : 775,
    FAMILYVIEW           : 0,
    FILTER               : False,
    FPREFIX              : 'F%04d',
    EPREFIX              : 'E%04d',
    IPREFIX              : 'I%04d',
    OPREFIX              : 'O%04d',
    PPREFIX              : 'P%04d',
    SPREFIX              : 'S%04d',
    RPREFIX              : 'R%04d',
    GOUTPUT_PREFERENCE   : 'No default format',
    OUTPUT_PREFERENCE    : 'No default format',
    PAPER_PREFERENCE     : 'Letter',
    RECENT_FILE          : '',
    RECENT_IMPORT_DIR    : '',
    RECENT_EXPORT_DIR    : '',
    MAKE_REFERENCE       : True,
    MEDIA_GLOBAL         : True,
    MEDIA_LOCAL          : True,
    NAME_FORMAT          : 0,
    REPORT_DIRECTORY     : './',
    RESEARCHER_ADDR      : '',
    RESEARCHER_CITY      : '',
    RESEARCHER_COUNTRY   : '',
    RESEARCHER_EMAIL     : '',
    RESEARCHER_NAME      : '',
    RESEARCHER_PHONE     : '',
    RESEARCHER_POSTAL    : '',
    RESEARCHER_STATE     : '',
    SHOW_CALENDAR        : False,
    STARTUP              : 0,
    SIZE_CHECKED         : False,
    STATUSBAR            : 1,
    SURNAME_GUESSING     : 0,
    TOOLBAR              : -1,
    TOOLBAR_ON           : True,
    USE_LDS              : False,
    USE_TIPS             : False,
    POP_PLUGIN_STATUS    : False,
    VIEW                 : True,
    WEBSITE_DIRECTORY    : './',
}
