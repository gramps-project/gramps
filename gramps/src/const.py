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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext
_ = gettext

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

icon           = "%s/gramps.xpm" % rootDir
logo           = "%s/logo.png" % rootDir
gladeFile      = "%s/gramps.glade" % rootDir
placesFile     = "%s/places.glade" % rootDir
imageselFile   = "%s/imagesel.glade" % rootDir
marriageFile   = "%s/marriage.glade" % rootDir
editPersonFile = "%s/EditPerson.glade" % rootDir
bookFile       = "%s/bookmarks.glade" % rootDir
pluginsFile    = "%s/plugins.glade" % rootDir
editnoteFile   = "%s/editnote.glade" % rootDir
configFile     = "%s/config.glade" % rootDir
stylesFile     = "%s/styles.glade" % rootDir
dialogFile     = "%s/dialog.glade" % rootDir
revisionFile   = "%s/revision.glade" % rootDir
srcselFile     = "%s/srcsel.glade" % rootDir
findFile       = "%s/find.glade" % rootDir
mergeFile      = "%s/mergedata.glade" % rootDir
traceFile      = "%s/trace.glade" % rootDir
pluginsDir     = "%s/plugins" % rootDir
filtersDir     = "%s/filters" % rootDir
dataDir        = "%s/data" % rootDir
gtkrcFile      = "%s/gtkrc" % rootDir

#-------------------------------------------------------------------------
#
# About box information
#
#-------------------------------------------------------------------------
progName     = "gramps"
version      = "0.7.1pre"
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
    "Baptism"             : "BAPM",
    "Bar Mitzvah"         : "BARM",
    "Bas Mitzvah"         : "BASM",
    "Blessing"            : "BLES",
    "Burial"              : "BURI",
    "Cause Of Death"      : "CAUS",
    "Ordination"          : "ORDI",
    "Census"              : "CENS",
    "Christening"         : "CHR" ,
    "Confirmation"        : "CONF",
    "Cremation"           : "CREM",
    "Degree"              : "", 
    "Divorce Filing"      : "DIVF",
    "Education"           : "EDUC",
    "Elected"             : "",
    "Emigration"          : "EMIG",
    "First Communion"     : "FCOM",
    "Graduation"          : "GRAD",
    "Medical Information" : "", 
    "Military Service"    : "", 
    "Naturalization"      : "NATU",
    "Nobility Title"      : "TITL",
    "Number of Marriages" : "NMR",
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
    "Baptism"             : _("Baptism"),
    "Bar Mitzvah"         : _("Bar Mitzvah"),
    "Bas Mitzvah"         : _("Bas Mitzvah"),
    "Blessing"            : _("Blessing"),
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
    "Nobility Title"      : _("Nobility Title"),
    "Number of Marriages" : _("Number of Marriages"),
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
    val = _pe_e2l[a]
    if val:
        _pe_l2e[val] = a

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

lds_temple_codes = {
    "Cardston, Alberta"        : "ALBER",
    "Apia, Samoa"              : "APIA",
    "Mesa, Arizona"            : "ARIZO",
    "Atlanta Georgia"          : "ATLAN",
    "Bogota Columbia"          : "BOGOT", 
    "Boise Idaho"              : "BOISE",
    "Bountiful Utah"           : "BOUNT",
    "Buenos Aires, Argentina"  : "BAIRE",
    "Chicago, Illinois"        : "CHICA",
    "Cochabamba, Boliva"       : "COCHA",
    "Dallas, Texas"            : "DALLA",
    "Denver, Colorado"         : "DENVE",
    "Endowment House"          : "EHOUS",
    "Frankfurt, Germany"       : "FRANK",
    "Freiberg, Germany"        : "FREIB",
    "Guatamala City, Guatamala": "GUATE",
    "Guayaquil, Ecuador"       : "GUAYA",
    "Hartford, Connecticut"    : "HARTF",
    "Laie, Hawaii"             : "HAWAI",
    "Hong Kong, China"         : "HKONG",
    "Idaho Falls, Idaho"       : "IFALL",
    "Johannesburg, South Africa" : "JOHAN",
    "Sourth Jordan, Utah"      : "JRIVE",
    "Las Vegas, Nevada"        : "LVEGA",
    "Lima, Peru"               : "LIMA" ,
    "Logan, Utah"              : "LOGAN",
    "London, England"          : "LONDO",
    "Los Angeles, California"  : "LANGE",
    "Madrid, Spain"            : "MADRI",
    "Manila, Philippines"      : "MANIL",
    "Manti, Utah"              : "MANTI",
    "Mexico City, Mexico"      : "MEXIC",
    "American Fork, Utah"      : "MTIMP",
    "Nashville, Tennessee"     : "NASHV",
    "Nauvoo, Illinois"         : "NAUVO",
    "Hamilton, New Zealand"    : "NZEAL",
    "Nuku'alofa, Tonga"        : "NUKUA",
    "Oakland, California"      : "OAKLA",
    "Ogden, Utah"              : "OGDEN",
    "Orlando, Florida"         : "ORLAN",
    "Papeete, Tahiti"          : "PAPEE",
    "Portland, Oregon"         : "PORTL",
    "President's Office"       : "POFFI",
    "Preston, England"         : "PREST",
    "Provo, Utah"              : "PROVO",
    "Recife, Brazil"           : "RECIF",
    "Salt Lake City, Utah"     : "SLAKE",
    "San Diego, California"    : "SDIEG",
    "Santiago, Chile"          : "SANTI",
    "Santo Domingo, Dominican Republic" : "SDOMI",
    "Sao Paulo, Brazil"        : "SPAUL",
    "Seattle, Washington"      : "SEATT",
    "Seoul, South Korea"       : "SEOUL",
    "St. George, Utah"         : "SGEOR",
    "St. Louis, Missouri"      : "SLOUI",
    "Stockholm, Sweden"        : "STOCK",
    "Bern, Switzerland"        : "SWISS",
    "Sydney, Australia"        : "SYDNE",
    "Taipei, Taiwan"           : "TAIPE",
    "Tokyo, Japan"             : "TOKYO",
    "Toronto, Ontario"         : "TORNO",
    "Vernal, Utah"             : "VERNA",
    "Washington, D.C."         : "WASHI",
}

lds_temple_to_abrev = {
    "ALBER": "Cardston, Alberta",
    "APIA" : "Apia, Samoa",            
    "AP"   : "Apia, Samoa",            
    "ARIZO": "Mesa, Arizona",
    "AZ"   : "Mesa, Arizona",
    "ATLAN": "Atlanta, Georgia",          
    "AT"   : "Atlanta, Georgia",          
    "BOGOT": "Bogota, Columbia",         
    "BG"   : "Bogota, Columbia",         
    "BOISE": "Boise Idaho",            
    "BO"   : "Boise Idaho",            
    "BOUNT": "Bountiful, Utah",        
    "BAIRE": "Buenos Aires, Argentina",        
    "BA"   : "Buenos Aires, Argentina",        
    "CHICA": "Chicago, Illinois",          
    "CH"   : "Chicago, Illinois",          
    "COCHA": "Cochabamba, Boliva",  
    "DALLA": "Dallas, Texas",          
    "DA"   : "Dallas, Texas",          
    "DENVE": "Denver, Colorado",          
    "DV"   : "Denver, Colorado",          
    "EHOUS": "Endowment House",     
    "EH"   : "Endowment House",     
    "FRANK": "Frankfurt, Germany",           
    "FR"   : "Frankfurt, Germany",           
    "FREIB": "Freiberg, Germany",            
    "FD"   : "Freiberg, Germany",            
    "GUATE": "Guatamala City, Guatamala",           
    "GA"   : "Guatamala City, Guatamala",           
    "GUAYA": "Guayaquil, Ecuador",  
    "GY"   : "Guayaquil, Ecuador",  
    "HARTF": "Hartford, Connecticut",      
    "HAWAI": "Laie, Hawaii",              
    "HA"   : "Laie, Hawaii",              
    "HKONG": "Hong Kong, China",           
    "IFALL": "Idaho Falls, Idaho",     
    "IF"   : "Idaho Falls, Idaho",     
    "JOHAN": "Johannesburg, South Africa",  
    "JO"   : "Johannesburg, South Africa",  
    "JRIVE": "South Jordan, Utah",    
    "JR"   : "South Jorhan, Utah",    
    "LVEGA": "Las Vegas, Nevada",       
    "LV"   : "Las Vegas, Nevada",       
    "LIMA" : "Lima, Peru",          
    "LI"   : "Lima, Peru",          
    "LOGAN": "Logan, Utah",           
    "LG"   : "Logan, Utah",           
    "LONDO": "London, England",              
    "LD"   : "London, England",              
    "LANGE": "Los Angeles, California",     
    "LA"   : "Los Angeles, California",     
    "MADRI": "Madrid, Spain",       
    "MANIL": "Manila, Philippines", 
    "MA"   : "Manila, Philippines", 
    "MANTI": "Manti, Utah",           
    "MT"   : "Manti, Utah",           
    "MEXIC": "Mexico City, Mexico",         
    "MX"   : "Mexico City, Mexico",         
    "MTIMP": "American Fork, Utah",  
    "NASHV": "Nashville, Tennessee",     
    "NAUVO": "Nauvoo, Illinois",              
    "NZEAL": "Hamilton, New Zealand",         
    "NZ"   : "Hamilton, New Zealand",         
    "NUKUA": "Nuku'alofa, Tonga",   
    "TG"   : "Nuku'alofa, Tonga",   
    "OAKLA": "Oakland, California",         
    "OK"   : "Oakland, California",         
    "OGDEN": "Ogden, Utah",           
    "OG"   : "Ogden, Utah",           
    "ORLAN": "Orlando, Florida",         
    "PAPEE": "Papeete, Tahiti",     
    "TA"   : "Papeete, Tahiti",     
    "PORTL": "Portland, Oregon",        
    "PT"   : "Portland, Oregon",        
    "POFFI": "President's Office",  
    "PREST": "Preston, England",        
    "PROVO": "Provo, Utah",           
    "PV"   : "Provo, Utah",           
    "RECIF": "Recife, Brazil",      
    "SLAKE": "Salt Lake City, Utah",       
    "SL"   : "Salt Lake City, Utah",       
    "SDIEG": "San Diego, California",       
    "SA"   : "San Diego, California",       
    "SANTI": "Santiago, Chile",     
    "SN"   : "Santiago, Chile",     
    "SDOMI": "Santo Domingo, Dominican Republic", 
    "SPAUL": "Sao Paulo, Brazil",     
    "SP"   : "Sao Paulo, Brazil",     
    "SEATT": "Seattle, Washington",         
    "SE"   : "Seattle, Washington",         
    "SEOUL": "Seoul, South Korea",        
    "SO"   : "Seoul, South Korea",        
    "SGEOR": "St. George, Utah",      
    "SG"   : "St. George, Utah",      
    "SLOUI": "St. Louis, Missouri", 
    "STOCK": "Stockholm, Sweden",     
    "ST"   : "Stockholm, Sweden",     
    "SWISS": "Bern, Switzerland",               
    "SW"   : "Bern, Switzerland",               
    "SYDNE": "Sydney, Australia",        
    "SD"   : "Sydney, Australia",        
    "TAIPE": "Taipei, Taiwan",      
    "TP"   : "Taipei, Taiwan",      
    "TOKYO": "Tokyo, Japan",        
    "TK"   : "Tokyo, Japan",        
    "TORNO": "Toronto, Ontario",       
    "TR"   : "Toronto, Ontario",       
    "VERNA": "Vernal, Utah",         
    "WASHI": "Washington, D.C.",      
    "WA"   : "Washington, D.C.",      
}

lds_status = {
    "BIC"         : 1,
    "CANCELED"    : 1,
    "CHILD"       : 1,
    "CLEARED"     : 2,
    "COMPLETED"   : 3,
    "DNS"         : 4,
    "INFANT"      : 4,
    "PRE-1970"    : 5,
    "QUALIFIED"   : 6,
    "DNS/CAN"     : 7,
    "STILLBORN"   : 7,
    "SUBMITTED"   : 8,
    "UNCLEARED"   : 9,
    }

lds_baptism = [
    "<No Status>",
    "Child",
    "Cleared",
    "Completed",
    "Infant",
    "Pre-1970",
    "Qualified",
    "Stillborn",
    "Submitted",
    "Uncleared",
    ]

lds_csealing = [
    "<No Status>",
    "BIC",
    "Cleared",
    "Completed",
    "DNS",
    "Pre-1970",
    "Qualified",
    "Stillborn",
    "Submitted",
    "Uncleared",
    ]

lds_ssealing = [
    "<No Status>",
    "Canceled",
    "Cleared",
    "Completed",
    "DNS",
    "Pre-1970",
    "Qualified",
    "DNS/CAN",
    "Submitted",
    "Uncleared",
    ]

    
