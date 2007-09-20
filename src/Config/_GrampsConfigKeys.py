#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006-2007  Donald N. Allingham
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
Adding a new configuration key:

Add a value in the form of:

  VARIABLE = ( category, key_name, type)

Where:

  cateogory is a single word string defining the grouping along 
  with related keys

  key_name is a single word string defining the actual configuration
  name

  type is an integer defining the type of the value of the 
  configuration value. 

    0 - boolean
    1 - integer
    2 - string

Then add the variable to the default_value map at the end of the
file, and provide a default value according to the value's type.
"""

EXPORT_NO_PRIVATE    = ('export', 'no-private', 0)
EXPORT_RESTRICT      = ('export', 'restrict-living', 0)
DEFAULT_SOURCE       = ('preferences', 'default-source', 0)
RELATION_SHADE       = ('preferences', 'relation-shade', 0)
ONLINE_MAPS          = ('preferences', 'online-maps', 0)
FAMILY_DETAILS       = ('preferences', 'family-details', 0)
COMPLETE_COLOR       = ('preferences', 'complete-color', 2)
TODO_COLOR           = ('preferences', 'todo-color', 2)
CUSTOM_MARKER_COLOR  = ('preferences', 'custom-marker-color', 2)
FAMILY_WARN          = ('preferences', 'family-warn', 0)
HIDE_EP_MSG          = ('preferences', 'hide-ep-msg', 0)
LAST_VIEW            = ('preferences', 'last-view', 1)
USE_LAST_VIEW        = ('preferences', 'use-last-view', 0)
FAMILY_SIBLINGS      = ('preferences', 'family-siblings', 0)
AUTOLOAD             = ('behavior', 'autoload', 0)
ENABLE_AUTOBACKUP    = ('behavior', 'enable-autobackup', 0)
SPELLCHECK           = ('behavior', 'spellcheck', 0)
BETAWARN             = ('behavior', 'betawarn', 0)
WELCOME              = ('behavior', 'welcome', 1)
DATE_FORMAT          = ('preferences', 'date-format', 1)
DONT_ASK             = ('interface', 'dont-ask', 0)
RELEDITBTN           = ('interface', 'releditbtn', 0)
HEIGHT               = ('interface', 'height', 1)
WIDTH                = ('interface', 'width', 1)
FAMILY_HEIGHT        = ('interface', 'family-height', 1)
FAMILY_WIDTH         = ('interface', 'family-width', 1)
NOTE_HEIGHT          = ('interface', 'note-height', 1)
NOTE_WIDTH           = ('interface', 'note-width', 1)
PERSON_HEIGHT        = ('interface', 'person-height', 1)
PERSON_WIDTH         = ('interface', 'person-width', 1)
EVENT_HEIGHT         = ('interface', 'event-height', 1)
EVENT_WIDTH          = ('interface', 'event-width', 1)
EVENT_REF_HEIGHT     = ('interface', 'event-ref-height', 1)
EVENT_REF_WIDTH      = ('interface', 'event-ref-width', 1)
PLACE_HEIGHT         = ('interface', 'place-height', 1)
PLACE_WIDTH          = ('interface', 'place-width', 1)
REPO_HEIGHT          = ('interface', 'repo-height', 1)
REPO_WIDTH           = ('interface', 'repo-width', 1)
MEDIA_HEIGHT         = ('interface', 'media-height', 1)
MEDIA_WIDTH          = ('interface', 'media-width', 1)
ADDRESS_HEIGHT       = ('interface', 'address-height', 1)
ADDRESS_WIDTH        = ('interface', 'address-width', 1)
ATTRIBUTE_HEIGHT     = ('interface', 'attribute-height', 1)
ATTRIBUTE_WIDTH      = ('interface', 'attribute-width', 1)
NAME_HEIGHT          = ('interface', 'name-height', 1)
NAME_WIDTH           = ('interface', 'name-width', 1)
SOURCE_HEIGHT        = ('interface', 'source-height', 1)
SOURCE_WIDTH         = ('interface', 'source-width', 1)
SOURCE_REF_HEIGHT    = ('interface', 'source-ref-height', 1)
SOURCE_REF_WIDTH     = ('interface', 'source-ref-width', 1)
FILTER               = ('interface', 'filter', 0)
DATABASE_PATH        = ('behavior', 'database-path', 2)
FPREFIX              = ('preferences', 'fprefix', 2)
EPREFIX              = ('preferences', 'eprefix', 2)
RPREFIX              = ('preferences', 'rprefix', 2)
NPREFIX              = ('preferences', 'nprefix', 2)
IPREFIX              = ('preferences', 'iprefix', 2)
OPREFIX              = ('preferences', 'oprefix', 2)
PPREFIX              = ('preferences', 'pprefix', 2)
SPREFIX              = ('preferences', 'sprefix', 2)
GOUTPUT_PREFERENCE   = ('preferences', 'goutput-preference', 2)
OUTPUT_PREFERENCE    = ('preferences', 'output-preference', 2)
PAPER_PREFERENCE     = ('preferences', 'paper-preference', 2)
RECENT_FILE          = ('paths', 'recent-file', 2)
RECENT_IMPORT_DIR    = ('paths', 'recent-import-dir', 2)
RECENT_EXPORT_DIR    = ('paths', 'recent-export-dir', 2)
RECENT_EXPORT_TYPE   = ('behavior', 'recent-export-type', 1)
NAME_FORMAT          = ('preferences', 'name-format', 1)
REPORT_DIRECTORY     = ('paths', 'report-directory', 2)
RESEARCHER_ADDR      = ('researcher', 'researcher-addr', 2)
RESEARCHER_CITY      = ('researcher', 'researcher-city', 2)
RESEARCHER_COUNTRY   = ('researcher', 'researcher-country', 2)
RESEARCHER_EMAIL     = ('researcher', 'researcher-email', 2)
RESEARCHER_NAME      = ('researcher', 'researcher-name', 2)
RESEARCHER_PHONE     = ('researcher', 'researcher-phone', 2)
RESEARCHER_POSTAL    = ('researcher', 'researcher-postal', 2)
RESEARCHER_STATE     = ('researcher', 'researcher-state', 2)
STARTUP              = ('behavior', 'startup', 1)
SIZE_CHECKED         = ('interface', 'size-checked', 0)
STATUSBAR            = ('interface', 'statusbar', 1)
SURNAME_GUESSING     = ('behavior', 'surname-guessing', 1)
TOOLBAR_ON           = ('interface', 'toolbar-on', 0)
USE_TIPS             = ('behavior', 'use-tips', 0)
POP_PLUGIN_STATUS    = ('behavior', 'pop-plugin-status', 0)
VIEW                 = ('interface', 'view', 0)
SIDEBAR_TEXT         = ('interface', 'sidebar-text', 0)
WEBSITE_DIRECTORY    = ('paths', 'website-directory', 2)
PORT_WARN            = ('preferences', 'port-warn', 0)
TRANSACTIONS         = ('behavior', 'transactions', 0)
LDS_HEIGHT           = ('interface', 'lds-height', 1)
LDS_WIDTH            = ('interface', 'lds-width', 1)
LOCATION_HEIGHT      = ('interface', 'location-height', 1)
LOCATION_WIDTH       = ('interface', 'location-width', 1)
MEDIA_REF_HEIGHT     = ('interface', 'media-ref-height', 1)
MEDIA_REF_WIDTH      = ('interface', 'media-ref-width', 1)
URL_HEIGHT           = ('interface', 'url-height', 1)
URL_WIDTH            = ('interface', 'url-width', 1)
PERSON_REF_HEIGHT    = ('interface', 'person-ref-height', 1)
PERSON_REF_WIDTH     = ('interface', 'person-ref-width', 1)
REPO_REF_HEIGHT      = ('interface', 'repo-ref-height', 1)
REPO_REF_WIDTH       = ('interface', 'repo-ref-width', 1)
OWNER_WARN           = ('behavior', 'owner-warn', 0)
DATE_BEFORE_RANGE    = ('behavior', 'date-before-range', 1)
DATE_AFTER_RANGE     = ('behavior', 'date-after-range', 1)
DATE_ABOUT_RANGE     = ('behavior', 'date-about-range', 1)


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
    USE_LAST_VIEW        : True, 
    FAMILY_SIBLINGS      : True, 
    AUTOLOAD             : False, 
    ENABLE_AUTOBACKUP    : True, 
    SPELLCHECK           : False, 
    BETAWARN             : False, 
    WELCOME              : 100, 
    DATE_FORMAT          : 0, 
    DONT_ASK             : False, 
    RELEDITBTN           : False, 
    HEIGHT               : 500, 
    WIDTH                : 775, 
    FAMILY_HEIGHT        : 500, 
    FAMILY_WIDTH         : 700, 
    NOTE_HEIGHT          : 500, 
    NOTE_WIDTH           : 700, 
    PERSON_HEIGHT        : 550, 
    PERSON_WIDTH         : 750, 
    EVENT_HEIGHT         : 450, 
    EVENT_WIDTH          : 600, 
    EVENT_REF_HEIGHT     : 450, 
    EVENT_REF_WIDTH      : 600, 
    PLACE_HEIGHT         : 450, 
    PLACE_WIDTH          : 650, 
    REPO_HEIGHT          : 450, 
    REPO_WIDTH           : 650, 
    MEDIA_HEIGHT         : 450, 
    MEDIA_WIDTH          : 650, 
    ADDRESS_HEIGHT       : 450, 
    ADDRESS_WIDTH        : 650, 
    ATTRIBUTE_HEIGHT     : 350, 
    ATTRIBUTE_WIDTH      : 600, 
    NAME_HEIGHT          : 350, 
    NAME_WIDTH           : 600, 
    SOURCE_HEIGHT        : 450, 
    SOURCE_WIDTH         : 600, 
    SOURCE_REF_HEIGHT    : 450, 
    SOURCE_REF_WIDTH     : 600, 
    FILTER               : False, 
    DATABASE_PATH        : '~/.gramps/grampsdb', 
    FPREFIX              : 'F%04d', 
    EPREFIX              : 'E%04d', 
    RPREFIX              : 'R%04d', 
    NPREFIX              : 'N%04d', 
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
    RECENT_EXPORT_TYPE   : 1, 
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
    PORT_WARN            : False, 
    TRANSACTIONS         : True, 
    LDS_HEIGHT           : 450, 
    LDS_WIDTH            : 600, 
    LOCATION_HEIGHT      : 250, 
    LOCATION_WIDTH       : 600, 
    MEDIA_REF_HEIGHT     : 450, 
    MEDIA_REF_WIDTH      : 600, 
    URL_HEIGHT           : 150, 
    URL_WIDTH            : 600, 
    PERSON_REF_HEIGHT    : 350, 
    PERSON_REF_WIDTH     : 600, 
    REPO_REF_HEIGHT      : 450, 
    REPO_REF_WIDTH       : 600, 
    OWNER_WARN           : False, 
    EXPORT_NO_PRIVATE    : True,
    EXPORT_RESTRICT      : True,
    DATE_BEFORE_RANGE    : 9999,
    DATE_AFTER_RANGE     : 9999,
    DATE_ABOUT_RANGE     : 10,
}
