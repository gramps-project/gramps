#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import os
import sys
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Paths to external programs
#
#-------------------------------------------------------------------------
editor  = "gimp"
zipcmd  = "/usr/bin/zip -r -q"
convert = "/usr/X11R6/bin/convert"

#-------------------------------------------------------------------------
#
# Exceptions
#
#-------------------------------------------------------------------------

OpenFailed = "Open Failed"

#-------------------------------------------------------------------------
#
# Paths to files - assumes that files reside in the same directory as
# this one, and that the plugins directory is in a directory below this.
#
#-------------------------------------------------------------------------

if os.environ.has_key('GRAMPSDIR'):
    rootDir = os.environ['GRAMPSDIR']
else:
    rootDir = "."

logo           = rootDir + os.sep + "gramps.xpm"
gladeFile      = rootDir + os.sep + "gramps.glade"
imageselFile   = rootDir + os.sep + "imagesel.glade"
marriageFile   = rootDir + os.sep + "marriage.glade"
editPersonFile = rootDir + os.sep + "EditPerson.glade"
bookFile       = rootDir + os.sep + "bookmarks.glade"
pluginsFile    = rootDir + os.sep + "plugins.glade"
editnoteFile   = rootDir + os.sep + "editnote.glade"
configFile     = rootDir + os.sep + "config.glade"
stylesFile     = rootDir + os.sep + "styles.glade"
pluginsDir     = rootDir + os.sep + "plugins"
filtersDir     = rootDir + os.sep + "filters"
dataDir        = rootDir + os.sep + "data"
gtkrcFile      = rootDir + os.sep + "gtkrc"

#-------------------------------------------------------------------------
#
# About box information
#
#-------------------------------------------------------------------------
progName     = "gramps"
version      = "0.3.2"
copyright    = "(C) 2001 Donald N. Allingham"
authors      = ["Donald N. Allingham"]
comments     = _("Gramps (Genealogical Research and Analysis Management Programming System) is a personal genealogy program that can be extended by using the Python programming language.")

#-------------------------------------------------------------------------
#
# Enable/disable exceptions.  For debugging purposes
#
#-------------------------------------------------------------------------
useExceptions= 0

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
picWidth     = 275.0
thumbScale   = 100.0
indexFile    = "data.gramps"
male         = _("male")
female       = _("female")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

output_formats = ["OpenOffice", "AbiWord", "PDF", "HTML" ]

childRelations = [
    "Birth",
    "Adopted",
    "Other"
    ]

#-------------------------------------------------------------------------
#
# Family event string mappings
#
#-------------------------------------------------------------------------
familyConstantEvents = {
    "Annulment"             : "ANUL",
    "Divorce Filing"        : "DIVF",
    "Divorce"               : "DIV",
    "Engagement"            : "ENGA",
    "Marriage Contract"     : "MARC",
    "Marriage License"      : "MARL",
    "Marriage Settlement"   : "MARS",
    "Marriage"              : "MARR"
    }

_fe_e2l = {
    "Annulment"             : _("Annulment"),
    "Divorce Filing"        : _("Divorce Filing"),
    "Divorce"               : _("Divorce"),
    "Engagement"            : _("Engagement"),
    "Marriage Contract"     : _("Marriage Contract"),
    "Marriage License"      : _("Marriage License"),
    "Marriage Settlement"   : _("Marriage Settlement"),
    "Marriage"              : _("Marriage")
    }

_fe_l2e = {}
for a in _fe_e2l.keys():
    _fe_l2e[_fe_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def display_fevent(st):
    if _fe_e2l.has_key(st):
        return _fe_e2l[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_fevent(st):
    if _fe_l2e.has_key(st):
        return _fe_l2e[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
personalConstantEvents = {
    "Adopted"               : "ADOP",
    "Alternate Birth"       : "BIRT",
    "Alternate Death"       : "DEAT",
    "Baptism (LDS)"         : "BAPL",
    "Baptism"               : "BAPM",
    "Bar Mitzvah"           : "BARM",
    "Bas Mitzvah"           : "BASM",
    "Burial"                : "BURI",
    "Cause Of Death"        : "CAUS",
    "Census"                : "CENS",
    "Christening"           : "CHR" ,
    "Confirmation"          : "CONF",
    "Cremation"             : "CREM",
    "Degree"                : "_DEG", 
    "Divorce Filing"        : "DIVF",
    "Education"             : "EDUC",
    "Elected"               : "_ELEC",
    "Emigration"            : "EMIG",
    "Graduation"            : "GRAD",
    "Military Service"      : "_MILT", 
    "Naturalization"        : "NATU",
    "Occupation"            : "OCCU",
    "Probate"               : "PROB",
    "Religion"              : "RELI",
    "Residence"             : "RESI",
    "Residence"             : "RESI", 
    "Retirement"            : "RETI"
    }

_pe_e2l = {
    "Adopted"               : _("Adopted"),
    "Alternate Birth"       : _("Alternate Birth"),
    "Alternate Death"       : _("Alternate Death"),
    "Baptism (LDS)"         : _("Baptism (LDS)"),
    "Baptism"               : _("Baptism"),
    "Bar Mitzvah"           : _("Bar Mitzvah"),
    "Bas Mitzvah"           : _("Bas Mitzvah"),
    "Burial"                : _("Burial"),
    "Cause Of Death"        : _("Cause Of Death"),
    "Census"                : _("Census"),
    "Christening"           : _("Christening"),
    "Confirmation"          : _("Confirmation"),
    "Cremation"             : _("Cremation"),
    "Degree"                : _("Degree"),
    "Divorce Filing"        : _("Divorce Filing"),
    "Education"             : _("Education"),
    "Elected"               : _("Elected"),
    "Emigration"            : _("Emigration"),
    "Graduation"            : _("Graduation"),
    "Military Service"      : _("Military Service"), 
    "Naturalization"        : _("Naturalization"),
    "Occupation"            : _("Occupation"),
    "Probate"               : _("Probate"),
    "Religion"              : _("Religion"),
    "Residence"             : _("Residence"),
    "Retirement"            : _("Retirement"),
    }

_pe_l2e = {}
for a in _pe_e2l.keys():
    _pe_l2e[_pe_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def display_pevent(st):
    if _pe_e2l.has_key(st):
        return _pe_e2l[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_pevent(st):
    if _pe_l2e.has_key(st):
        return _pe_l2e[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
personalConstantAttributes = {
    "Description"           : "DSCR",
    "Identification Number" : "IDNO",
    "Social Security Number": "SSN"
    }

_pa_e2l = {
    "Description"           : _("Description"),
    "Identification Number" : _("Identification Number"),
    "Social Security Number": _("Social Security Number")
    }

_pa_l2e = {}
for a in _pa_e2l.keys():
    _pa_l2e[_pa_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def display_pattr(st):
    if _pa_e2l.has_key(st):
        return _pa_e2l[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_pattr(st):
    if _pa_l2e.has_key(st):
        return _pa_l2e[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
familyConstantAttributes = {
    }

_fa_e2l = {
    }

_fa_l2e = {}
for a in _fa_e2l.keys():
    _fa_l2e[_fa_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def display_fattr(st):
    if _fa_e2l.has_key(st):
        return _fa_e2l[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_fattr(st):
    if _fa_l2e.has_key(st):
        return _fa_l2e[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------

_fr_e2l = {
    "Married"    : _("Married"),
    "Common Law" : _("Common Law"),
    "Partners"   : _("Partners"),
    "Unknown"    : _("Unknown")
}

_fr_l2e = {}
for a in _fa_e2l.keys():
    _fa_l2e[_fa_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def display_frel(st):
    if _fr_e2l.has_key(st):
        return _fr_e2l[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_frel(st):
    if _fr_l2e.has_key(st):
        return _fr_l2e[st]
    else:
        return st

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def initialize_personal_event_list():
    p = []
    for event in personalConstantEvents.keys():
        p.append(_pe_e2l[event])
    p.sort()
    return p

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def initialize_marriage_event_list():
    p = []
    for event in familyConstantEvents.keys():
        p.append(_fe_e2l[event])
    p.sort()
    return p

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def initialize_personal_attribute_list():
    p = []
    for event in personalConstantAttributes.keys():
        p.append(_pa_e2l[event])
    p.sort()
    return p

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def initialize_family_attribute_list():
    p = []
    for event in familyConstantAttributes.keys():
        p.append(_fa_e2l[event])
    p.sort()
    return p

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def initialize_family_relation_list():
    p = []
    for event in _fr_e2l.keys():
        p.append(_fr_e2l[event])
    p.sort()
    return p

personalEvents = initialize_personal_event_list()
personalAttributes = initialize_personal_attribute_list()
marriageEvents = initialize_marriage_event_list()
familyAttributes = initialize_family_attribute_list()
familyRelations = initialize_family_relation_list()
