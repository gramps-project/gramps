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
version      = "0.7.0pre"
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

lds_temple_codes = {
    "ALBERTA" :            "ALBER",
    "APIA"    :            "SAMOA",
    "ARIZONA" :            "ARIZO",
    "ATLANTA GA":          "ATLAN",
    "BOGOTA COL.":         "BOGOT", 
    "BOISE ID":            "BOISE",
    "BOUNTIFUL UT":        "BOUNT",
    "BUENOS AIRES":        "BAIRE",
    "CHICAGO IL":          "CHICA",
    "COCHABAMBA, BOLIVA":  "COCHA",
    "DALLAS, TX":          "DALLA",
    "DENVER, CO":          "DENVE",
    "ENDOWMENT HOUSE":     "EHOUS",
    "FRANKFURT":           "FRANK",
    "FREIBERG":            "FREIB",
    "GUATAMALA":           "GUATE",
    "GUAYAQUIL, ECUADOR":  "GUAYA",
    "HARTFORD, CONN":      "HARTF",
    "HAWAII":              "HAWAI",
    "HONG KONG":           "HKONG",
    "IDAHO FALLS, ID":     "IFALL",
    "JOHANNESBURG, S.A.":  "JOHAN",
    "JORDAN RIVER, UT":    "JRIVE",
    "LAS VEGAS, NV":       "LVEGA",
    "LIMA, PERU":          "LIMA" ,
    "LOGAN, UT":           "LOGAN",
    "LONDON":              "LONDO",
    "LOS ANGELES, CA":     "LANGE",
    "MADRID, SPAIN":       "MADRI",
    "MANILA, PHILIPPINES": "MANIL",
    "MANTI, UT":           "MANTI",
    "MEXICO CITY":         "MEXIC",
    "MT. TIMPANOGAS, UT":  "MTIMP",
    "NASHVILLE, TENN":     "NASHV",
    "NAUVOO":              "NAUVO",
    "NEW ZEALAND":         "NZEAL",
    "NUKU'ALOFA, TONGA":   "NUKUA",
    "OAKLAND, CA":         "OAKLA",
    "OGDEN, UT":           "OGDEN",
    "ORLANDO, FL":         "ORLAN",
    "PAPEETE, TAHITI":     "PAPEE",
    "PORTLAND, OR":        "PORTL",
    "PRESIDENT'S OFFICE":  "POFFI",
    "PRESTON, ENG":        "PREST",
    "PROVO, UT":           "PROVO",
    "RECIFE, BRAZIL":      "RECIF",
    "SALT LAKE, UT":       "SLAKE",
    "SAN DIEGO, CA":       "SDIEG",
    "SANTIAGO, CHILE":     "SANTI",
    "SANTO DOMINGO, D.R.": "SDOMI",
    "SAO PAULO, BRAZ":     "SPAUL",
    "SEATTLE, WA":         "SEATT",
    "SEOUL, KOREA":        "SEOUL",
    "ST. GEORGE, UT":      "SGEOR",
    "ST. LOUIS, MISSOURI": "SLOUI",
    "STOCKHOLM, SWDN":     "STOCK",
    "SWISS":               "SWISS",
    "SYDNEY, AUST":        "SYDNE",
    "TAIPEI, TAIWAN":      "TAIPE",
    "TOKYO, JAPAN":        "TOKYO",
    "TORONTO, CAN.":       "TORNO",
    "VERNAL, UT.":         "VERNA",
    "WASHINGTON, DC":      "WASHI",
}

lds_temple_to_abrev = {
    "ALBER":    "ALBERTA" ,            
    "SAMOA":    "APIA"    ,            
    "AP":    "APIA"    ,            
    "APIA":    "APIA"    ,            
    "ARIZO":    "ARIZONA" ,            
    "AZ":    "ARIZONA" ,            
    "ATLAN":    "ATLANTA GA",          
    "AT":    "ATLANTA GA",          
    "BOGOT":    "BOGOTA COL.",         
    "BG":    "BOGOTA COL.",         
    "BOISE":    "BOISE ID",            
    "BO":    "BOISE ID",            
    "BOUNT":    "BOUNTIFUL UT",        
    "BAIRE":    "BUENOS AIRES",        
    "BA":    "BUENOS AIRES",        
    "CHICA":    "CHICAGO IL",          
    "CH":    "CHICAGO IL",          
    "COCHA":    "COCHABAMBA, BOLIVA",  
    "DALLA":    "DALLAS, TX",          
    "DA":    "DALLAS, TX",          
    "DENVE":    "DENVER, CO",          
    "DV":    "DENVER, CO",          
    "EHOUS":    "ENDOWMENT HOUSE",     
    "EH":    "ENDOWMENT HOUSE",     
    "FRANK":    "FRANKFURT",           
    "FR":    "FRANKFURT",           
    "FREIB":    "FREIBERG",            
    "FD":    "FREIBERG",            
    "GUATE":    "GUATAMALA",           
    "GA":    "GUATAMALA",           
    "GUAYA": "GUAYAQUIL, ECUADOR",  
    "GY":    "GUAYAQUIL, ECUADOR",  
    "HARTF": "HARTFORD, CONN",      
    "HAWAI": "HAWAII",              
    "HA":    "HAWAII",              
    "HKONG": "HONG KONG",           
    "IFALL": "IDAHO FALLS, ID",     
    "IF":    "IDAHO FALLS, ID",     
    "JOHAN": "JOHANNESBURG, S.A.",  
    "JO":    "JOHANNESBURG, S.A.",  
    "JRIVE": "JORDAN RIVER, UT",    
    "JR":    "JORDAN RIVER, UT",    
    "LVEGA": "LAS VEGAS, NV",       
    "LV":    "LAS VEGAS, NV",       
    "LIMA" : "LIMA, PERU",          
    "LI":    "LIMA, PERU",          
    "LOGAN": "LOGAN, UT",           
    "LG":    "LOGAN, UT",           
    "LONDO": "LONDON",              
    "LD":    "LONDON",              
    "LANGE": "LOS ANGELES, CA",     
    "LA":    "LOS ANGELES, CA",     
    "MADRI": "MADRID, SPAIN",       
    "MANIL": "MANILA, PHILIPPINES", 
    "MA":    "MANILA, PHILIPPINES", 
    "MANTI": "MANTI, UT",           
    "MT":    "MANTI, UT",           
    "MEXIC": "MEXICO CITY",         
    "MX":    "MEXICO CITY",         
    "MTIMP": "MT. TIMPANOGAS, UT",  
    "NASHV": "NASHVILLE, TENN",     
    "NAUVO": "NAUVOO",              
    "NZEAL": "NEW ZEALAND",         
    "NZ":    "NEW ZEALAND",         
    "NUKUA": "NUKU'ALOFA, TONGA",   
    "TG":    "NUKU'ALOFA, TONGA",   
    "OAKLA":    "OAKLAND, CA",         
    "OK":    "OAKLAND, CA",         
    "OGDEN":    "OGDEN, UT",           
    "OG":    "OGDEN, UT",           
    "ORLAN":    "ORLANDO, FL",         
    "PAPEE":    "PAPEETE, TAHITI",     
    "TA":    "PAPEETE, TAHITI",     
    "PORTL":    "PORTLAND, OR",        
    "PT":    "PORTLAND, OR",        
    "POFFI":    "PRESIDENT'S OFFICE",  
    "PREST":    "PRESTON, ENG",        
    "PROVO":    "PROVO, UT",           
    "PV":    "PROVO, UT",           
    "RECIF":    "RECIFE, BRAZIL",      
    "SLAKE":    "SALT LAKE, UT",       
    "SL":    "SALT LAKE, UT",       
    "SDIEG":    "SAN DIEGO, CA",       
    "SA":    "SAN DIEGO, CA",       
    "SANTI":    "SANTIAGO, CHILE",     
    "SN":    "SANTIAGO, CHILE",     
    "SDOMI":    "SANTO DOMINGO, D.R.", 
    "SPAUL":    "SAO PAULO, BRAZ",     
    "SP":    "SAO PAULO, BRAZ",     
    "SEATT":    "SEATTLE, WA",         
    "SE":    "SEATTLE, WA",         
    "SEOUL":    "SEOUL, KOREA",        
    "SO":    "SEOUL, KOREA",        
    "SGEOR":    "ST. GEORGE, UT",      
    "SG":    "ST. GEORGE, UT",      
    "SLOUI":    "ST. LOUIS, MISSOURI", 
    "STOCK":    "STOCKHOLM, SWDN",     
    "ST":    "STOCKHOLM, SWDN",     
    "SWISS":    "SWISS",               
    "SW":    "SWISS",               
    "SYDNE":    "SYDNEY, AUST",        
    "SD":    "SYDNEY, AUST",        
    "TAIPE":    "TAIPEI, TAIWAN",      
    "TP":    "TAIPEI, TAIWAN",      
    "TOKYO":    "TOKYO, JAPAN",        
    "TK":    "TOKYO, JAPAN",        
    "TORNO":    "TORONTO, CAN.",       
    "TR":    "TORONTO, CAN.",       
    "VERNA":    "VERNAL, UT.",         
    "WASHI":    "WASHINGTON, DC",      
    "WA":    "WASHINGTON, DC",      
}
