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
import intl
import GdkImlib

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Paths to external programs
#
#-------------------------------------------------------------------------
editor  = "gimp"
zipcmd  = "zip -r -q"
convert = "convert"

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

icon           = rootDir + os.sep + "gramps.xpm"
logo           = rootDir + os.sep + "logo.png"
gladeFile      = rootDir + os.sep + "gramps.glade"
placesFile     = rootDir + os.sep + "places.glade"
imageselFile   = rootDir + os.sep + "imagesel.glade"
marriageFile   = rootDir + os.sep + "marriage.glade"
editPersonFile = rootDir + os.sep + "EditPerson.glade"
bookFile       = rootDir + os.sep + "bookmarks.glade"
pluginsFile    = rootDir + os.sep + "plugins.glade"
editnoteFile   = rootDir + os.sep + "editnote.glade"
configFile     = rootDir + os.sep + "config.glade"
stylesFile     = rootDir + os.sep + "styles.glade"
dialogFile     = rootDir + os.sep + "dialog.glade"
mergeFile      = rootDir + os.sep + "mergedata.glade"
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
version      = "0.6.0pre"
copyright    = "© 2001 Donald N. Allingham"
authors      = ["Donald N. Allingham", "David Hampton"]
comments     = _("Gramps (Genealogical Research and Analysis Management Programming System) is a personal genealogy program.")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
picWidth     = 275.0
thumbScale   = 96.0
indexFile    = "data.gramps"
male         = _("male")
female       = _("female")
unknown      = _("unknown")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

output_formats = [
    "OpenOffice",
    "AbiWord",
    "PDF",
    "HTML"
    ]

childRelations = {
    _("Birth")     : "Birth",
    _("Adopted")   : "Adopted",
    _("Stepchild") : "Stepchild",
    _("Foster")    : "Foster",
    _("None")      : "None",
    _("Unknown")   : "Unknown",
    _("Other")     : "Other",
    }

#-------------------------------------------------------------------------
#
# Confidence
#
#-------------------------------------------------------------------------
confidence = [
    _("Very Low"),
    _("Low"),
    _("Normal"),
    _("High"),
    _("Very High")
    ]

#-------------------------------------------------------------------------
#
# Family event string mappings
#
#-------------------------------------------------------------------------
familyConstantEvents = {
    "Annulment"           : "ANUL",
    "Divorce Filing"      : "DIVF",
    "Divorce"             : "DIV",
    "Engagement"          : "ENGA",
    "Marriage Contract"   : "MARC",
    "Marriage License"    : "MARL",
    "Marriage Settlement" : "MARS",
    "Marriage"            : "MARR"
    }

_fe_e2l = {
    "Annulment"           : _("Annulment"),
    "Divorce Filing"      : _("Divorce Filing"),
    "Divorce"             : _("Divorce"),
    "Engagement"          : _("Engagement"),
    "Marriage Contract"   : _("Marriage Contract"),
    "Marriage License"    : _("Marriage License"),
    "Marriage Settlement" : _("Marriage Settlement"),
    "Marriage"            : _("Marriage")
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
    "Adopted"             : "ADOP",
    "Adult Christening"   : "CHRA",
    "Alternate Birth"     : "BIRT",
    "Alternate Death"     : "DEAT",
    "Baptism (LDS)"       : "BAPL",
    "Baptism"             : "BAPM",
    "Bar Mitzvah"         : "BARM",
    "Bas Mitzvah"         : "BASM",
    "Burial"              : "BURI",
    "Cause Of Death"      : "CAUS",
    "Ordination"          : "ORID",
    "Census"              : "CENS",
    "Christening"         : "CHR" ,
    "Confirmation"        : "CONF",
    "Cremation"           : "CREM",
    "Degree"              : "_DEG", 
    "Divorce Filing"      : "DIVF",
    "Education"           : "EDUC",
    "Elected"             : "_ELEC",
    "Emigration"          : "EMIG",
    "First Communion"     : "FCOM",
    "Graduation"          : "GRAD",
    "Medical Information" : "_MDCL", 
    "Military Service"    : "_MILT", 
    "Naturalization"      : "NATU",
    "Immigration"         : "IMMI",
    "Occupation"          : "OCCU",
    "Probate"             : "PROB",
    "Property"            : "PROP",
    "Religion"            : "RELI",
    "Residence"           : "RESI", 
    "Retirement"          : "RETI",
    "Will"                : "WILL"
    }

_pe_e2l = {
    "Adopted"             : _("Adopted"),
    "Alternate Birth"     : _("Alternate Birth"),
    "Alternate Death"     : _("Alternate Death"),
    "Adult Christening"   : _("Adult Christening"),
    "Baptism (LDS)"       : _("Baptism (LDS)"),
    "Baptism"             : _("Baptism"),
    "Bar Mitzvah"         : _("Bar Mitzvah"),
    "Bas Mitzvah"         : _("Bas Mitzvah"),
    "Burial"              : _("Burial"),
    "Cause Of Death"      : _("Cause Of Death"),
    "Census"              : _("Census"),
    "Christening"         : _("Christening"),
    "Confirmation"        : _("Confirmation"),
    "Cremation"           : _("Cremation"),
    "Degree"              : _("Degree"),
    "Divorce Filing"      : _("Divorce Filing"),
    "Education"           : _("Education"),
    "Elected"             : _("Elected"),
    "Emigration"          : _("Emigration"),
    "First Communion"     : _("First Communion"),
    "Immigration"         : _("Immigration"),
    "Graduation"          : _("Graduation"),
    "Medical Information" : _("Medical Information"),
    "Military Service"    : _("Military Service"), 
    "Naturalization"      : _("Naturalization"),
    "Occupation"          : _("Occupation"),
    "Ordination"          : _("Ordination"),
    "Probate"             : _("Probate"),
    "Property"            : _("Property"),
    "Religion"            : _("Religion"),
    "Residence"           : _("Residence"),
    "Retirement"          : _("Retirement"),
    "Will"                : _("Will")
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
    "Caste"                 : "CAST",
    "Description"           : "DSCR",
    "Identification Number" : "IDNO",
    "National Origin"       : "NATI",
    "Social Security Number": "SSN"
    }

_pa_e2l = {
    "Caste"                 : _("Caste"),
    "Description"           : _("Description"),
    "Identification Number" : _("Identification Number"),
    "National Origin"       : _("National Origin"),
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
    "Number of Children" : "NCHI",
    }

_fa_e2l = {
    "Number of Children" : _("Number of Children"),
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

_frel2def = {
    _("Married")  : _("A legal or common-law relationship between a husband and wife"),
    _("Unmarried"): _("No legal or common-law relationship between man and woman"),
    _("Partners") : _("An established relationship between members of the same sex"),
    _("Unknown")  : _("Unknown relationship between a man and woman"),
    _("Other")    : _("An unspecified relationship between a man and woman")
}

_fr_e2l = {
    "Married"   : _("Married"),
    "Unmarried" : _("Unmarried"),
    "Partners"  : _("Partners"),
    "Unknown"   : _("Unknown"),
    "Other"     : _("Other")
}

_fr_l2e = {}
for a in _fa_e2l.keys():
    _fa_l2e[_fa_e2l[a]] = a

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def relationship_def(txt):
    if _frel2def.has_key(txt):
        return _frel2def[txt]
    else:
        return _("No definition available")

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
places = []
surnames = []

xpm_data = [
    '/* XPM */',
    'static char * foo_xpm[] = {',
    '"1 1 1 1"',
    '" 	c None"',
    '" "};']

empty_image = GdkImlib.create_image_from_xpm(xpm_data)
