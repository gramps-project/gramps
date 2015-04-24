#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
Import from GEDCOM

The GEDCOM file format is defined by the GEDCOM 5.5 Specfication, found
at http://www.familysearch.org/GEDCOM/GEDCOM55.EXE

The basic structure is a line with three attributes:

<LEVEL> <TOKEN> <DATA>

Because of this structure, it does not lend itself to more traditional
parsing techniques, such as LALR. The LEVEL token implies too much to be
useful in this context. While this makes parsing more difficult, it
does provide one very beneficial feature for GEDCOM: Error recoverability.
GEDCOM is a poorly implemented standard, primarily because it is a poor
standard to begin with. 

Most commercial applications that implement GEDCOM output add custom 
extensions, and feel free to violate the existing structure. If one were
cynical, one might believe that the commercial programs were trying to
make it difficult to transfer your data to another application.

This parser takes a different approach to parsing a GEDCOM file. The first
state, Lexer, reads lines from the file, and does some basic lexical
analysis on each line (actually several lines, since it automatically
combines CONT and CONC tagged lines). Each logical line returned to this
parser contains:

  Level, Token, Token text, Data, and line number.

The Data field is typically text, but in some cases, it may be a integer 
value representing an enumerated type or a GRAMPS object (in the case of
dates).

The parser works on the current level. Each context and level has a an 
associated table (dictionary) of functions indexed by the corresponding
TOKEN. When a token is found, we index into the table to find the function
associated with the token. If no token is found, a function that skips the
line and all subordinate (lines with a higher number). If a function is 
found, then we call that function, which in turn processes the line, and
all tokens at the lower level. 

For example:

1 BIRT
  2 DATE 1 JAN 2000
  2 UKNOWN TAG
    3 NOTE DATA

The function parsing the individual at level 1, would encounter the BIRT tag.
It would look up the BIRT token in the table to see if a function as defined 
for this TOKEN, and pass control to this function. This function would then
start parsing level 2. It would encounter the DATE tag, look up the 
corresponding function in the level 2 table, and pass control to its 
associated function. This function would terminate, and return control back to
the level 2 parser, which would then encounter the "UKNOWN" tag. Since this is
not a valid token, it would not be in the table, and a function that would skip
all lines until the next level 2 token is found (in this case, skipping the 
"3 NOTE DATA" line.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import re
import time
import codecs
from gen.ggettext import gettext as _
from xml.parsers.expat import ParserCreate
from collections import defaultdict
import cStringIO
from urlparse import urlparse
import string

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".libgedcom")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import const
import gen.lib
from gen.db import DbTxn
from gen.updatecallback import UpdateCallback
import gen.mime
import LdsUtils
import Utils
from DateHandler._DateParser import DateParser
from gen.db.dbconst import EVENT_KEY
from QuestionDialog import WarningDialog, InfoDialog
from gen.lib.const import IDENTICAL, DIFFERENT
from gen.lib import (StyledText, StyledTextTag, StyledTextTagType)

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
TOKEN_UNKNOWN = 0
TOKEN_ABBR = 1
TOKEN_ADDR = 2
TOKEN_ADOP = 3
TOKEN_ADR1 = 4
TOKEN_ADR2 = 5
TOKEN_AFN = 6
TOKEN_IGNORE = 7
TOKEN_REFN = 8
TOKEN__AKA = 9
TOKEN_ALIA = 11
TOKEN_ANCI = 12
TOKEN_ASSO = 13
TOKEN_AUTH = 14
TOKEN_BAPL = 15
TOKEN_BIRT = 16
TOKEN__CAT = 17
TOKEN_CAUS = 18
TOKEN_CHAN = 19
TOKEN_CHAR = 20
TOKEN_CHIL = 21
TOKEN_CITY = 22
TOKEN__COMM = 23
TOKEN_CONC = 24
TOKEN_CONT = 25
TOKEN_COPR = 26
TOKEN_CORP = 27
TOKEN_CTRY = 28
TOKEN_DATA = 29
TOKEN_DATE = 30
TOKEN_DEAT = 32
TOKEN_DESI = 33
TOKEN_DEST = 34
TOKEN_ENDL = 35
TOKEN_EVEN = 36
TOKEN_FAM = 38
TOKEN_FAMC = 39
TOKEN_FAMS = 40
TOKEN_FILE = 41
TOKEN_FORM = 42
TOKEN__FREL = 43
TOKEN_GEDC = 44
TOKEN_GIVN = 45
TOKEN__GODP = 46
TOKEN_HUSB = 47
TOKEN_INDI = 48
TOKEN_LABL = 49
TOKEN_LANG = 50
TOKEN__LOC = 51
TOKEN__MARNM = 52
TOKEN__MREL = 53
TOKEN__NAME = 54
TOKEN_NAME = 55
TOKEN_NCHI = 56
TOKEN_NICK = 57
TOKEN_NOTE = 58
TOKEN_NPFX = 59
TOKEN_NSFX = 60
TOKEN_OBJE = 61
TOKEN_OFFI = 62
TOKEN_PAGE = 63
TOKEN_PEDI = 64
TOKEN_PERI = 65
TOKEN_PHON = 66
TOKEN_PLAC = 67
TOKEN_POST = 68
TOKEN__PRIMARY = 69
TOKEN__PRIV = 70
TOKEN_PUBL = 71
TOKEN_QUAY = 72
TOKEN_RELI = 74
TOKEN_REPO = 75
TOKEN_RESI = 76
TOKEN_RFN = 77
TOKEN_RIN = 78
TOKEN__SCHEMA = 79
TOKEN_SEX = 80
TOKEN_SLGC = 81
TOKEN_SLGS = 82
TOKEN_SOUR = 83
TOKEN_SPFX = 84
TOKEN_STAE = 85
TOKEN__STAT = 86
TOKEN_STAT = 87
TOKEN_SUBM = 88
TOKEN_SUBN = 89
TOKEN_SURN = 90
TOKEN_TAXT = 91
TOKEN_TEMP = 92
TOKEN_TEXT = 93
TOKEN_TIME = 94
TOKEN_TITL = 95
TOKEN__TODO = 96
TOKEN_TRLR = 97
TOKEN_TYPE = 98
TOKEN__UID = 99
TOKEN_VERS = 100
TOKEN_WIFE = 101
TOKEN__WITN = 102
TOKEN__WTN = 103
TOKEN_AGNC = 104
TOKEN_HEAD = 105
TOKEN_CALN = 106
TOKEN_MEDI = 107
TOKEN_RELA = 108
TOKEN__LKD = 109
TOKEN_BLOB = 110
TOKEN_CONL = 111
TOKEN_AGE  = 112
TOKEN_RESN = 114
TOKEN_ID = 115
TOKEN_GEVENT = 116
TOKEN_RNOTE = 117
TOKEN_GATTR = 118
TOKEN_ATTR = 119
TOKEN_MAP = 120
TOKEN_LATI = 121
TOKEN_LONG = 122
TOKEN_FACT = 123
TOKEN_EMAIL = 124
TOKEN_WWW = 125
TOKEN_URL = 126
TOKEN_ROLE = 127
TOKEN__MAR = 128
TOKEN__MARN = 129
TOKEN__ADPN = 130
TOKEN__FSFTID = 131

TOKENS = {
    "HEAD"         : TOKEN_HEAD,    "MEDI"         : TOKEN_MEDI,
    "HEADER"       : TOKEN_HEAD,    "TRAILER"      : TOKEN_TRLR,
    "CALL_NUMBER"  : TOKEN_CALN,    "MEDIA"        : TOKEN_MEDI,
    "CALN"         : TOKEN_CALN,    "ABBR"         : TOKEN_ABBR,
    "ABBREVIATION" : TOKEN_ABBR,    "ADDR"         : TOKEN_ADDR,
    "ADDRESS"      : TOKEN_ADDR,    "ADOP"         : TOKEN_ADOP,
    "ADOPT"        : TOKEN_ADOP,    "ADR1"         : TOKEN_ADR1,
    "ADDRESS1"     : TOKEN_ADR1,    "ADR2"         : TOKEN_ADR2,
    "ADDRESS2"     : TOKEN_ADR2,    "AFN"          : TOKEN_AFN,
    "AGE"          : TOKEN_AGE,     "AGNC"         : TOKEN_AGNC,
    "AGENCY"       : TOKEN_IGNORE,  "_AKA"         : TOKEN__AKA,
    "_AKAN"        : TOKEN__AKA,    "AKA"          : TOKEN__AKA,
    "_ALIA"        : TOKEN_ALIA,    "ALIA"         : TOKEN_ALIA,
    "ALIAS"        : TOKEN_ALIA,    "ANCI"         : TOKEN_ANCI,
    "ASSO"         : TOKEN_ASSO,    "ASSOCIATES"   : TOKEN_ASSO,
    "AUTH"         : TOKEN_AUTH,    "AUTHOR"       : TOKEN_AUTH,
    "BAPL"         : TOKEN_BAPL,    "BAPTISM-LDS"  : TOKEN_BAPL,
    "BIRT"         : TOKEN_BIRT,    "BIRTH"        : TOKEN_BIRT,
    "_CAT"         : TOKEN_IGNORE,  "CAUS"         : TOKEN_CAUS,
    "CAUSE"        : TOKEN_CAUS,    "CHAN"         : TOKEN_CHAN,
    "CHANGE"       : TOKEN_CHAN,    "CHAR"         : TOKEN_CHAR,
    "CHARACTER"    : TOKEN_CHAR,    "CHIL"         : TOKEN_CHIL,
    "CHILD"        : TOKEN_CHIL,    "CITY"         : TOKEN_CITY,
    "_COMM"        : TOKEN__COMM,   "CONC"         : TOKEN_CONC,
    "CONCATENTATE" : TOKEN_CONC,    "CONT"         : TOKEN_CONT,
    "CONTINUED"    : TOKEN_CONT,    "CONCATENATION": TOKEN_CONC,
    "CONTINUATION" : TOKEN_CONT,    "COPR"         : TOKEN_COPR,
    "COPYRIGHT"    : TOKEN_COPR,    "CORP"         : TOKEN_CORP,
    "CORPORATION"  : TOKEN_CORP,    "CTRY"         : TOKEN_CTRY,
    "COUNTRY"      : TOKEN_CTRY,    "DATA"         : TOKEN_DATA,
    "DATE"         : TOKEN_DATE,    "_DATE2"       : TOKEN_IGNORE,
    "DEAT"         : TOKEN_DEAT,    "DEATH"        : TOKEN_DEAT,
    "DESI"         : TOKEN_DESI,    "DEST"         : TOKEN_DEST,
    "DESTINATION"  : TOKEN_DEST,    "ENDL"         : TOKEN_ENDL,
    "ENDOWMENT"    : TOKEN_ENDL,    "EVEN"         : TOKEN_EVEN,
    "EVENT"        : TOKEN_EVEN,    "_ANCES_ORDRE" : TOKEN_IGNORE,
    "FAM"          : TOKEN_FAM,     "FAMILY"       : TOKEN_FAM,
    "FAMC"         : TOKEN_FAMC,    "FAMILY_CHILD" : TOKEN_FAMC,
    "FAMS"         : TOKEN_FAMS,    "FAMILY_SPOUSE" : TOKEN_FAMS,
    "FILE"          : TOKEN_FILE,   "FORM"          : TOKEN_FORM,
    "_FREL"         : TOKEN__FREL,  "GEDC"          : TOKEN_GEDC,
    "GEDCOM"        : TOKEN_GEDC,   "GIVN"          : TOKEN_GIVN,
    "GIVEN_NAME"    : TOKEN_GIVN,   "_GODP"         : TOKEN__GODP,
    "HUSB"          : TOKEN_HUSB,   "HUSBAND"       : TOKEN_HUSB,
    "INDI"          : TOKEN_INDI,   "INDIVIDUAL"    : TOKEN_INDI,
    "LABL"          : TOKEN_LABL,   "LABEL"         : TOKEN_LABL,
    "LANG"          : TOKEN_LANG,   "_LOC"          : TOKEN__LOC,
    "_MARNM"        : TOKEN__MARNM, "_MREL"         : TOKEN__MREL,
    "_NAME"         : TOKEN__NAME,  "NAME"          : TOKEN_NAME,
    "NCHI"          : TOKEN_NCHI,   "CHILDREN_COUNT": TOKEN_NCHI,
    "NICK"          : TOKEN_NICK,   "NICKNAME"      : TOKEN_NICK,
    "NOTE"          : TOKEN_NOTE,   "NPFX"          : TOKEN_NPFX,
    "NAME_PREFIX"   : TOKEN_NPFX,   "NSFX"          : TOKEN_NSFX,
    "NAME_SUFFIX"   : TOKEN_NSFX,   "OBJE"          : TOKEN_OBJE,
    "OBJECT"        : TOKEN_OBJE,   "OFFI"          : TOKEN_OFFI,
    "PAGE"          : TOKEN_PAGE,   "PEDIGREE"      : TOKEN_PEDI,
    "PEDI"          : TOKEN_PEDI,   "PERI"          : TOKEN_PERI,
    "PHON"          : TOKEN_PHON,   "PHONE"         : TOKEN_PHON,
    "PHONE_NUMBER"  : TOKEN_PHON,   "PLAC"          : TOKEN_PLAC,
    "PLACE"         : TOKEN_PLAC,   "POST"          : TOKEN_POST,
    "POSTAL_CODE"   : TOKEN_POST,   "_PRIMARY"      : TOKEN__PRIMARY,
    "_PRIV"         : TOKEN__PRIV,  "PUBL"          : TOKEN_PUBL,
    "PUBLICATION"   : TOKEN_PUBL,   "QUAY"          : TOKEN_QUAY,
    "QUALITY_OF_DATA": TOKEN_QUAY,  "REFN"          : TOKEN_REFN,
    "REFERENCE"      : TOKEN_REFN,  "RELI"          : TOKEN_RELI,
    "RELIGION"       : TOKEN_RELI,  "REPO"          : TOKEN_REPO,
    "REPOSITORY"     : TOKEN_REPO,  "RFN"           : TOKEN_RFN,
    "RIN"            : TOKEN_RIN,   "ROLE"          : TOKEN_ROLE,
    "_SCHEMA"        : TOKEN__SCHEMA,
    "SEX"            : TOKEN_SEX,   "SCHEMA"        : TOKEN__SCHEMA,
    "SLGC"           : TOKEN_SLGC,  "SLGS"          : TOKEN_SLGS,
    "SOUR"           : TOKEN_SOUR,  "SOURCE"        : TOKEN_SOUR,
    "SPFX"           : TOKEN_SPFX,  "SURN_PREFIX"   : TOKEN_SPFX,
    "STAE"           : TOKEN_STAE,  "STATE"         : TOKEN_STAE,
    "_STAT"          : TOKEN__STAT, "STAT"          : TOKEN_STAT,
    "STATUS"         : TOKEN_STAT,  "SUBM"          : TOKEN_SUBM,
    "SUBMITTER"      : TOKEN_SUBM,  "SUBN"          : TOKEN_SUBN,
    "SUBMISSION"     : TOKEN_SUBN,  "SURN"          : TOKEN_SURN,
    "SURNAME"        : TOKEN_SURN,  "TAXT"          : TOKEN_TAXT,
    "TEMP"           : TOKEN_TEMP,  "TEMPLE"        : TOKEN_TEMP,
    "TEXT"           : TOKEN_TEXT,  "TIME"          : TOKEN_TIME,
    "TITL"           : TOKEN_TITL,  "TITLE"         : TOKEN_TITL,
    "_TODO"          : TOKEN__TODO, "TRLR"          : TOKEN_TRLR,
    "TYPE"           : TOKEN_TYPE,
    "_UID"           : TOKEN__UID,  "VERS"          : TOKEN_VERS,
    "VERSION"        : TOKEN_VERS,  "WIFE"          : TOKEN_WIFE,
    "_WITN"          : TOKEN__WITN, "_WTN"          : TOKEN__WTN,
    "_CHUR"          : TOKEN_IGNORE,"RELA"          : TOKEN_RELA,
    "_DETAIL"        : TOKEN_IGNORE,"_PREF"         : TOKEN__PRIMARY,
    "_LKD"           : TOKEN__LKD,  "_DATE"         : TOKEN_IGNORE,
    "_SCBK"          : TOKEN_IGNORE,"_TYPE"         : TOKEN_TYPE,
    "_PRIM"          : TOKEN_IGNORE,"_SSHOW"        : TOKEN_IGNORE,
    "_PAREN"         : TOKEN_IGNORE,"BLOB"          : TOKEN_BLOB,
    "CONL"           : TOKEN_CONL,  "RESN"          : TOKEN_RESN,
    "_MEDI"          : TOKEN_MEDI,  "_MASTER"       : TOKEN_IGNORE,
    "_LEVEL"         : TOKEN_IGNORE,"_PUBLISHER"    : TOKEN_IGNORE,
    "MAP"            : TOKEN_MAP,   "LATI"          : TOKEN_LATI,
    "LONG"           : TOKEN_LONG,  "_ITALIC"       : TOKEN_IGNORE,
    "_PLACE"         : TOKEN_IGNORE,
    "FACT"           : TOKEN_FACT,  "EMAIL"         : TOKEN_EMAIL,
    "EMAI"           : TOKEN_EMAIL, "WWW"           : TOKEN_WWW,
    "_URL"           : TOKEN_URL,   "URL"           : TOKEN_URL,
    "_MAR"           : TOKEN__MAR,  "_MARN"         : TOKEN__MARN,
    "_ADPN"          : TOKEN__ADPN, "_FSFTID"       : TOKEN__FSFTID,
}

ADOPT_NONE         = 0
ADOPT_EVENT        = 1
ADOPT_FTW          = 2
ADOPT_LEGACY       = 3
ADOPT_PEDI         = 4
ADOPT_STD          = 5
CONC_OK            = 0
CONC_BROKEN        = 1
ALT_NAME_NONE      = 0
ALT_NAME_STD       = 1
ALT_NAME_ALIAS     = 2
ALT_NAME_AKA       = 3
ALT_NAME_EVENT_AKA = 4
ALT_NAME_UALIAS    = 5
CALENDAR_NO        = 0
CALENDAR_YES       = 1
OBJE_NO            = 0
OBJE_YES           = 1
PREFIX_NO          = 0
PREFIX_YES         = 1
RESIDENCE_ADDR     = 0
RESIDENCE_PLAC     = 1
SOURCE_REFS_NO     = 0
SOURCE_REFS_YES    = 1

TYPE_BIRTH  = gen.lib.ChildRefType()
TYPE_ADOPT  = gen.lib.ChildRefType(gen.lib.ChildRefType.ADOPTED)
TYPE_FOSTER = gen.lib.ChildRefType(gen.lib.ChildRefType.FOSTER)

RELATION_TYPES = (
    gen.lib.ChildRefType.BIRTH, 
    gen.lib.ChildRefType.UNKNOWN, 
    gen.lib.ChildRefType.NONE, 
    )

PEDIGREE_TYPES = {
    'birth'  : gen.lib.ChildRefType(), 
    'natural': gen.lib.ChildRefType(), 
    'step'   : TYPE_ADOPT, 
    'adopted': TYPE_ADOPT, 
    'foster' : TYPE_FOSTER, 
    }

MIME_MAP = {
    'jpeg' : 'image/jpeg',   'jpg'  : 'image/jpeg', 
    'rtf'  : 'text/rtf',     'pdf'  : 'application/pdf', 
    'mpeg' : 'video/mpeg',   'mpg'  : 'video/mpeg', 
    'gif'  : 'image/gif',    'bmp'  : 'image/x-ms-bmp', 
    'tiff' : 'image/tiff',   'aif'  : 'audio/x-aiff', 
    'text' : 'text/plain',   'w8bn' : 'application/msword', 
    'wav'  : 'audio/x-wav',  'mov'  : 'video/quicktime', 
    }

FTW_BAD_PLACE = [
    gen.lib.EventType.OCCUPATION, 
    gen.lib.EventType.RELIGION, 
    gen.lib.EventType.DEGREE
    ]

MEDIA_MAP = {
    'audio'      : gen.lib.SourceMediaType.AUDIO, 
    'book'       : gen.lib.SourceMediaType.BOOK, 
    'card'       : gen.lib.SourceMediaType.CARD, 
    'electronic' : gen.lib.SourceMediaType.ELECTRONIC, 
    'fiche'      : gen.lib.SourceMediaType.FICHE, 
    'microfiche' : gen.lib.SourceMediaType.FICHE, 
    'microfilm'  : gen.lib.SourceMediaType.FICHE, 
    'film'       : gen.lib.SourceMediaType.FILM, 
    'magazine'   : gen.lib.SourceMediaType.MAGAZINE, 
    'manuscript' : gen.lib.SourceMediaType.MANUSCRIPT, 
    'map'        : gen.lib.SourceMediaType.MAP, 
    'newspaper'  : gen.lib.SourceMediaType.NEWSPAPER, 
    'photo'      : gen.lib.SourceMediaType.PHOTO, 
    'tombstone'  : gen.lib.SourceMediaType.TOMBSTONE, 
    'grave'      : gen.lib.SourceMediaType.TOMBSTONE, 
    'video'      : gen.lib.SourceMediaType.VIDEO, 
}

#-------------------------------------------------------------------------
#
# Integer to GEDCOM tag mappings for constants
#
#-------------------------------------------------------------------------
CALENDAR_MAP_GEDCOM2XML = {
    u"FRENCH R" : gen.lib.Date.CAL_FRENCH,
    u"JULIAN"   : gen.lib.Date.CAL_JULIAN,
    u"HEBREW"   : gen.lib.Date.CAL_HEBREW,
}

QUALITY_MAP = {
    'CAL' : gen.lib.Date.QUAL_CALCULATED,
    'INT' : gen.lib.Date.QUAL_CALCULATED,
    'EST' : gen.lib.Date.QUAL_ESTIMATED,
}

SEX_MAP = {
    'F' : gen.lib.Person.FEMALE,
    'M' : gen.lib.Person.MALE,
}

FAMILYCONSTANTEVENTS = {
    gen.lib.EventType.ANNULMENT  : "ANUL",
    gen.lib.EventType.DIV_FILING : "DIVF",
    gen.lib.EventType.DIVORCE    : "DIV",
    gen.lib.EventType.CENSUS     : "CENS",
    gen.lib.EventType.ENGAGEMENT : "ENGA",
    gen.lib.EventType.MARR_BANNS : "MARB",
    gen.lib.EventType.MARR_CONTR : "MARC",
    gen.lib.EventType.MARR_LIC   : "MARL",
    gen.lib.EventType.MARR_SETTL : "MARS",
    gen.lib.EventType.MARRIAGE   : "MARR"
    }

PERSONALCONSTANTEVENTS = {
    gen.lib.EventType.ADOPT            : "ADOP",
    gen.lib.EventType.ADULT_CHRISTEN   : "CHRA",
    gen.lib.EventType.BIRTH            : "BIRT",
    gen.lib.EventType.DEATH            : "DEAT",
    gen.lib.EventType.BAPTISM          : "BAPM",
    gen.lib.EventType.BAR_MITZVAH      : "BARM",
    gen.lib.EventType.BAS_MITZVAH      : "BASM",
    gen.lib.EventType.BLESS            : "BLES",
    gen.lib.EventType.BURIAL           : "BURI",
    gen.lib.EventType.CAUSE_DEATH      : "CAUS",
    gen.lib.EventType.ORDINATION       : "ORDN",
    gen.lib.EventType.CENSUS           : "CENS",
    gen.lib.EventType.CHRISTEN         : "CHR" ,
    gen.lib.EventType.CONFIRMATION     : "CONF",
    gen.lib.EventType.CREMATION        : "CREM",
    gen.lib.EventType.DEGREE           : "_DEG", 
    gen.lib.EventType.DIV_FILING       : "DIVF",
    gen.lib.EventType.EDUCATION        : "EDUC",
    gen.lib.EventType.ELECTED          : "",
    gen.lib.EventType.EMIGRATION       : "EMIG",
    gen.lib.EventType.FIRST_COMMUN     : "FCOM",
    gen.lib.EventType.GRADUATION       : "GRAD",
    gen.lib.EventType.MED_INFO         : "_MDCL", 
    gen.lib.EventType.MILITARY_SERV    : "_MILT", 
    gen.lib.EventType.NATURALIZATION   : "NATU",
    gen.lib.EventType.NOB_TITLE        : "TITL",
    gen.lib.EventType.NUM_MARRIAGES    : "NMR",
    gen.lib.EventType.IMMIGRATION      : "IMMI",
    gen.lib.EventType.OCCUPATION       : "OCCU",
    gen.lib.EventType.PROBATE          : "PROB",
    gen.lib.EventType.PROPERTY         : "PROP",
    gen.lib.EventType.RELIGION         : "RELI",
    gen.lib.EventType.RESIDENCE        : "RESI", 
    gen.lib.EventType.RETIREMENT       : "RETI",
    gen.lib.EventType.WILL             : "WILL",
    }

FAMILYCONSTANTATTRIBUTES = {
    gen.lib.AttributeType.NUM_CHILD   : "NCHI",
    }

PERSONALCONSTANTATTRIBUTES = {
    gen.lib.AttributeType.CASTE       : "CAST",
    gen.lib.AttributeType.DESCRIPTION : "DSCR",
    gen.lib.AttributeType.ID          : "IDNO",
    gen.lib.AttributeType.NATIONAL    : "NATI",
    gen.lib.AttributeType.NUM_CHILD   : "NCHI",
    gen.lib.AttributeType.SSN         : "SSN",
    }

#-------------------------------------------------------------------------
#
# Gedcom to int constants
#
#-------------------------------------------------------------------------
LDS_STATUS = {
    "BIC"      : gen.lib.LdsOrd.STATUS_BIC,
    "CANCELED" : gen.lib.LdsOrd.STATUS_CANCELED,
    "CHILD"    : gen.lib.LdsOrd.STATUS_CHILD,
    "CLEARED"  : gen.lib.LdsOrd.STATUS_CLEARED,
    "COMPLETED": gen.lib.LdsOrd.STATUS_COMPLETED,
    "DNS"      : gen.lib.LdsOrd.STATUS_DNS,
    "INFANT"   : gen.lib.LdsOrd.STATUS_INFANT,
    "PRE-1970" : gen.lib.LdsOrd.STATUS_PRE_1970,
    "QUALIFIED": gen.lib.LdsOrd.STATUS_QUALIFIED,
    "DNS/CAN"  : gen.lib.LdsOrd.STATUS_DNS_CAN,
    "STILLBORN": gen.lib.LdsOrd.STATUS_STILLBORN,
    "SUBMITTED": gen.lib.LdsOrd.STATUS_SUBMITTED,
    "UNCLEARED": gen.lib.LdsOrd.STATUS_UNCLEARED,
    }

# table for skipping illegal control chars in GEDCOM import
# Only 09, 0A, 0D are allowed.
STRIP_DICT = dict.fromkeys(range(9)+range(11, 13)+range(14, 32))

#-------------------------------------------------------------------------
#
# GEDCOM events to GRAMPS events conversion
#
#-------------------------------------------------------------------------
GED_TO_GRAMPS_EVENT = {}
for __val, __key in PERSONALCONSTANTEVENTS.iteritems():
    if __key != "":
        GED_TO_GRAMPS_EVENT[__key] = __val

for __val, __key in FAMILYCONSTANTEVENTS.iteritems():
    if __key != "":
        GED_TO_GRAMPS_EVENT[__key] = __val

GED_TO_GRAMPS_ATTR = {}
for __val, __key in PERSONALCONSTANTATTRIBUTES.iteritems():
    if __key != "":
        GED_TO_GRAMPS_ATTR[__key] = __val
        
#-------------------------------------------------------------------------
#
# GEDCOM Date Constants
#
#-------------------------------------------------------------------------
HMONTH = [
    "", "ELUL", "TSH", "CSH", "KSL", "TVT", "SHV", "ADR", 
    "ADS", "NSN", "IYR", "SVN", "TMZ", "AAV", "ELL" ]

FMONTH = [
    "",     "VEND", "BRUM", "FRIM", "NIVO", "PLUV", "VENT", 
    "GERM", "FLOR", "PRAI", "MESS", "THER", "FRUC", "COMP"]

MONTH = [
    "",    "JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]

CALENDAR_MAP = {
    gen.lib.Date.CAL_HEBREW : (HMONTH, '@#DHEBREW@'), 
    gen.lib.Date.CAL_FRENCH : (FMONTH, '@#DFRENCH R@'), 
    gen.lib.Date.CAL_JULIAN : (MONTH, '@#DJULIAN@'), 
    gen.lib.Date.CAL_SWEDISH : (MONTH, '@#DUNKNOWN@'), 
    }

CALENDAR_MAP_PARSESTRING = {
    gen.lib.Date.CAL_HEBREW : ' (h)', 
    gen.lib.Date.CAL_FRENCH : ' (f)', 
    gen.lib.Date.CAL_JULIAN : ' (j)', 
    gen.lib.Date.CAL_SWEDISH : ' (s)', 
    }

#how wrong calendar use is shown
CALENDAR_MAP_WRONGSTRING = {
    gen.lib.Date.CAL_HEBREW : ' <hebrew>', 
    gen.lib.Date.CAL_FRENCH : ' <french rep>', 
    gen.lib.Date.CAL_JULIAN : ' <julian>', 
    gen.lib.Date.CAL_SWEDISH : ' <swedish>', 
    }

DATE_MODIFIER = {
    gen.lib.Date.MOD_ABOUT   : "ABT", 
    gen.lib.Date.MOD_BEFORE  : "BEF", 
    gen.lib.Date.MOD_AFTER   : "AFT", 
    #Date.MOD_INTERPRETED : "INT",
    }

DATE_QUALITY = {
    gen.lib.Date.QUAL_CALCULATED : "CAL", 
    gen.lib.Date.QUAL_ESTIMATED  : "EST", 
}

#-------------------------------------------------------------------------
#
# regular expressions
#
#-------------------------------------------------------------------------
NOTE_RE    = re.compile(r"\s*\d+\s+\@(\S+)\@\s+NOTE(.*)$")
CONT_RE    = re.compile(r"\s*\d+\s+CONT\s?(.*)$")
CONC_RE    = re.compile(r"\s*\d+\s+CONC\s?(.*)$")
PERSON_RE  = re.compile(r"\s*\d+\s+\@(\S+)\@\s+INDI(.*)$")
MOD   = re.compile(r"\s*(INT|EST|CAL)\s+(.*)$")
CAL   = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D?([^@]+)@\s*(.*)$")
RANGE = re.compile(r"\s*BET\s+@#D?([^@]+)@\s*(.*)\s+AND\s+@#D?([^@]+)@\s*(.*)$")
RANGE1 = re.compile(r"\s*BET\s+\s*(.*)\s+AND\s+@#D?([^@]+)@\s*(.*)$")
RANGE2 = re.compile(r"\s*BET\s+@#D?([^@]+)@\s*(.*)\s+AND\s+\s*(.*)$")
SPAN  = re.compile(r"\s*FROM\s+@#D?([^@]+)@\s*(.*)\s+TO\s+@#D?([^@]+)@\s*(.*)$")
SPAN1  = re.compile(r"\s*FROM\s+\s*(.*)\s+TO\s+@#D?([^@]+)@\s*(.*)$")
SPAN2  = re.compile(r"\s*FROM\s+@#D?([^@]+)@\s*(.*)\s+TO\s+\s*(.*)$")
NAME_RE    = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
SURNAME_RE = re.compile(r"/([^/]*)/([^/]*)")

#-----------------------------------------------------------------------
#
# GedcomDateParser
#
#-----------------------------------------------------------------------
class GedcomDateParser(DateParser):

    month_to_int = {
        'jan' : 1,  'feb' : 2,  'mar' : 3,  'apr' : 4,
        'may' : 5,  'jun' : 6,  'jul' : 7,  'aug' : 8,
        'sep' : 9,  'oct' : 10, 'nov' : 11, 'dec' : 12,
        }
  
#-------------------------------------------------------------------------
#
# Lexer - serves as the lexical analysis engine
#
#-------------------------------------------------------------------------
class Lexer(object):

    def __init__(self, ifile):
        self.ifile = ifile
        self.current_list = []
        self.eof = False
        self.cnv = None
        self.cnt = 0
        self.index = 0
        self.func_map = {
            TOKEN_CONT : self.__fix_token_cont,
            TOKEN_CONC : self.__fix_token_conc,
            }

    def readline(self):
        if len(self.current_list) <= 1 and not self.eof:
            self.__readahead()
        try:
            return GedLine(self.current_list.pop())
        except:
            LOG.debug('Error in reading Gedcom line', exc_info=True)
            return None

    def __fix_token_cont(self, data):
        line = self.current_list[0]
        new_value = line[2] + '\n' + data[2]
        self.current_list[0] = (line[0], line[1], new_value, line[3], line[4])

    def __fix_token_conc(self, data):
        line = self.current_list[0]
        if len(line[2]) == 4:
            # This deals with lines of the form
            # 0 @<XREF:NOTE>@ NOTE
            #   1 CONC <SUBMITTER TEXT>
            # The previous line contains only a tag and no data so concat a
            # space to separate the new line from the tag. This prevents the
            # first letter of the new line being lost later
            # in _GedcomParse.__parse_record
            new_value = line[2] + ' ' + data[2]
        else:
            new_value = line[2] + data[2]
        self.current_list[0] = (line[0], line[1], new_value, line[3], line[4])

    def __readahead(self):
        while len(self.current_list) < 5:
            line = self.ifile.readline()
            self.index += 1
            if not line:
                self.eof = True
                return

            try:
                # According to the GEDCOM 5.5 standard,
                # Chapter 1 subsection Grammar
                #"leading whitespace preceeding a GEDCOM line should be ignored"
                # We will also strip the terminator which is any combination
                # of carriage_return and line_feed
                line = line.lstrip(' ').rstrip('\n\r')
                # split into level+delim+rest
                line = line.partition(' ')
                level = int(line[0])
                # there should only be one space after the level,
                # but we can ignore more,
                line = line[2].lstrip(' ')
                # then split into tag+delim+line_value
                # or xfef_id+delim+rest
                # the xref_id can have spaces in it
                if line.startswith('@'):
                    line = line.split('@', 2)
                    # line is now [None, alphanum+pointer_string, rest]
                    tag = '@' + line[1] + '@'
                    line_value = line[2].lstrip()
                    ## Ignore meaningless @IDENT@ on CONT or CONC line
                    ## as noted at http://www.tamurajones.net/IdentCONT.xhtml
                    if (line_value.lstrip().startswith("CONT ") or 
                        line_value.lstrip().startswith("CONC ")):
                        line = line_value.lstrip().partition(' ')
                        tag = line[0]
                        line_value = line[2]
                else:
                    line = line.partition(' ')
                    tag = line[0]
                    line_value = line[2]
            except:
                continue

            token = TOKENS.get(tag, TOKEN_UNKNOWN)
            data = (level, token, line_value, tag, self.index)

            func = self.func_map.get(data[1])
            if func:
                func(data)
            else:
                # There will normally only be one space between tag and
                # line_value, but in case there is more then one, remove extra
                # spaces after CONC/CONT processing
                data = data[:2] + (data[2].strip(),) + data[3:]
                self.current_list.insert(0, data)

    def clean_up(self):
        """
        Break circular references to parsing methods stored in dictionaries
        to aid garbage collection
        """
        for key in (self.func_map.keys()):
            del self.func_map[key]
        del self.func_map

#-----------------------------------------------------------------------
#
# GedLine - represents a tokenized version of a GEDCOM line
#
#-----------------------------------------------------------------------
class GedLine(object):
    """
    GedLine is a class the represents a GEDCOM line. The form of a  GEDCOM line 
    is:
    
    <LEVEL> <TOKEN> <TEXT>

    This gets parsed into

    Line Number, Level, Token Value, Token Text, and Data

    Data is dependent on the context the Token Value. For most of tokens, 
    this is just a text string. However, for certain tokens where we know 
    the context, we can provide some value. The current parsed tokens are:

    TOKEN_DATE   - gen.lib.Date
    TOKEN_SEX    - gen.lib.Person gender item
    TOEKN_UKNOWN - Check to see if this is a known event
    """
    __DATE_CNV = GedcomDateParser()
    
    @staticmethod
    def __extract_date(text):
        """
        Converts the specified text to a gen.lib.Date object.
        """
        dateobj = gen.lib.Date()
        text = text.replace('BET ABT','EST BET') # Horrible hack for importing
                                                 # illegal GEDCOM from
                                                 # Apple Macintosh Classic
                                                 # 'Gene' program

        # extract out the MOD line
        match = MOD.match(text)
        mod = ''
        if match:
            (mod, text) = match.groups()
            qual = QUALITY_MAP.get(mod, gen.lib.Date.QUAL_NONE)
            mod += ' '
        else:
            qual = gen.lib.Date.QUAL_NONE

        # parse the range if we match, if so, return
        match = RANGE.match(text)
        match1 = RANGE1.match(text)
        match2 = RANGE2.match(text)
        if match or match1 or match2:
            if match:
                (cal1, data1, cal2, data2) = match.groups()
            elif match1:
                cal1 = gen.lib.Date.CAL_GREGORIAN
                (data1, cal2, data2) = match1.groups()
            elif match2:
                cal2 = gen.lib.Date.CAL_GREGORIAN
                (cal1, data1, data2) = match2.groups()
            cal1 = CALENDAR_MAP_GEDCOM2XML.get(cal1, gen.lib.Date.CAL_GREGORIAN)
            cal2 = CALENDAR_MAP_GEDCOM2XML.get(cal2, gen.lib.Date.CAL_GREGORIAN)
            if cal1 != cal2:
                #not supported by GRAMPS, import as text, we construct a string
                # that the parser will not parse as a correct date
                return GedLine.__DATE_CNV.parse('%sbetween %s%s and %s%s' % 
                        (mod, data1, CALENDAR_MAP_WRONGSTRING.get(cal1, ''),
                         CALENDAR_MAP_WRONGSTRING.get(cal2, ''), data2))
            
            #add hebrew, ... calendar so that months are recognized
            data1 += CALENDAR_MAP_PARSESTRING.get(cal1, '')
            data2 += CALENDAR_MAP_PARSESTRING.get(cal2, '')
            start = GedLine.__DATE_CNV.parse(data1)
            stop =  GedLine.__DATE_CNV.parse(data2)
            dateobj.set(gen.lib.Date.QUAL_NONE, gen.lib.Date.MOD_RANGE, cal1,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj

        # parse a span if we match
        match = SPAN.match(text)
        match1 = SPAN1.match(text)
        match2 = SPAN2.match(text)
        if match or match1 or match2:
            if match:
                (cal1, data1, cal2, data2) = match.groups()
            elif match1:
                cal1 = gen.lib.Date.CAL_GREGORIAN
                (data1, cal2, data2) = match1.groups()
            elif match2:
                cal2 = gen.lib.Date.CAL_GREGORIAN
                (cal1, data1, data2) = match2.groups()
            cal1 = CALENDAR_MAP_GEDCOM2XML.get(cal1, gen.lib.Date.CAL_GREGORIAN)
            cal2 = CALENDAR_MAP_GEDCOM2XML.get(cal2, gen.lib.Date.CAL_GREGORIAN)
            if cal1 != cal2:
                #not supported by GRAMPS, import as text, we construct a string
                # that the parser will not parse as a correct date
                return GedLine.__DATE_CNV.parse('%sfrom %s%s to %s%s' % 
                        (mod, data1, CALENDAR_MAP_WRONGSTRING.get(cal1, ''),
                         CALENDAR_MAP_WRONGSTRING.get(cal2, ''), data2))
            #add hebrew, ... calendar so that months are recognized
            data1 += CALENDAR_MAP_PARSESTRING.get(cal1, '')
            data2 += CALENDAR_MAP_PARSESTRING.get(cal2, '')
            start = GedLine.__DATE_CNV.parse(data1)
            stop =  GedLine.__DATE_CNV.parse(data2)
            dateobj.set(gen.lib.Date.QUAL_NONE, gen.lib.Date.MOD_SPAN, cal1,
                        start.get_start_date() + stop.get_start_date())
            dateobj.set_quality(qual)
            return dateobj
        
        match = CAL.match(text)
        if match:
            (abt, call, data) = match.groups()
            call = CALENDAR_MAP_GEDCOM2XML.get(call, gen.lib.Date.CAL_GREGORIAN)
            data += CALENDAR_MAP_PARSESTRING.get(call, '')
            if abt:
                dateobj = GedLine.__DATE_CNV.parse("%s %s" % (abt, data))
            else:
                dateobj = GedLine.__DATE_CNV.parse(data)
            dateobj.set_quality(qual)
            return dateobj
        dateobj = GedLine.__DATE_CNV.parse(text)
        dateobj.set_quality(qual)
        return dateobj

    def __init__(self, data):
        """
        If the level is 0, then this is a top level instance. In this case, 
        we may find items in the form of:

        <LEVEL> @ID@ <ITEM>

        If this is not the top level, we check the MAP_DATA array to see if 
        there is a conversion function for the data.
        """
        self.line = data[4]
        self.level = data[0]
        self.token = data[1]
        self.token_text = data[3].strip()
        self.data = data[2]

        if self.level == 0:
            if (self.token_text and self.token_text[0] == '@' and
                self.token_text[-1] == '@'):

                self.token = TOKEN_ID
                self.token_text = self.token_text[1:-1]
                self.data = self.data.strip()
        else:
            func = _MAP_DATA.get(self.token)
            if func:
                func(self)

    def calc_sex(self):
        """
        Converts the data field to a gen.lib token indicating the gender
        """
        try:
            self.data = SEX_MAP.get(self.data.strip()[0], 
                                    gen.lib.Person.UNKNOWN)
        except:
            self.data = gen.lib.Person.UNKNOWN

    def calc_date(self):
        """
        Converts the data field to a gen.lib.Date object
        """
        self.data = self.__extract_date(self.data)

    def calc_unknown(self):
        """
        Checks to see if the token maps a known GEDCOM event. If so, we 
        change the type from UNKNOWN to TOKEN_GEVENT (gedcom event), and
        the data is assigned to the associated GRAMPS EventType
        """
        token = GED_TO_GRAMPS_EVENT.get(self.token_text)
        if token:
            event = gen.lib.Event()
            event.set_description(self.data)
            event.set_type(token)
            self.token = TOKEN_GEVENT
            self.data = event
        else:
            token = GED_TO_GRAMPS_ATTR.get(self.token_text)
            if token:
                attr = gen.lib.Attribute()
                attr.set_value(self.data)
                attr.set_type(token)
                self.token = TOKEN_ATTR
                self.data = attr

    def calc_note(self):
        gid = self.data.strip()
        if len(gid) > 2 and gid[0] == '@' and gid[-1] == '@':
            self.token = TOKEN_RNOTE
            self.data = gid[1:-1]

    def calc_nchi(self):
        attr = gen.lib.Attribute()
        attr.set_value(self.data)
        attr.set_type(gen.lib.AttributeType.NUM_CHILD)
        self.data = attr
        self.token = TOKEN_ATTR

    def calc_attr(self):
        attr = gen.lib.Attribute()
        attr.set_value(self.data)
        attr.set_type((gen.lib.AttributeType.CUSTOM, self.token_text))
        self.data = attr
        self.token = TOKEN_ATTR

    def __repr__(self):
        return "%d: %d (%d:%s) %s" % (self.line, self.level, self.token, 
                                      self.token_text, self.data)

_MAP_DATA = {
    TOKEN_UNKNOWN : GedLine.calc_unknown,
    TOKEN_DATE    : GedLine.calc_date,
    TOKEN_SEX     : GedLine.calc_sex,
    TOKEN_NOTE    : GedLine.calc_note,
    TOKEN_NCHI    : GedLine.calc_nchi,
    TOKEN__STAT   : GedLine.calc_attr,
    TOKEN__UID    : GedLine.calc_attr,
    TOKEN_AFN     : GedLine.calc_attr,
    TOKEN__FSFTID : GedLine.calc_attr,
    }

#-------------------------------------------------------------------------
#
# GedcomDescription
#
#-------------------------------------------------------------------------
class GedcomDescription(object):
    def __init__(self, name):
        self.name = name
        self.dest = ""
        self.adopt = ADOPT_STD
        self.conc = CONC_OK
        self.altname = ALT_NAME_STD
        self.cal = CALENDAR_YES
        self.obje = OBJE_YES
        self.resi = RESIDENCE_ADDR
        self.source_refs = SOURCE_REFS_YES
        self.gramps2tag_map = {}
        self.tag2gramps_map = {}
        self.prefix = PREFIX_YES
        self.endl = "\n"
        
    def set_dest(self, val):
        self.dest = val

    def get_dest(self):
        return self.dest

    def set_endl(self, val):
        self.endl = val.replace('\\r','\r').replace('\\n','\n')

    def get_endl(self):
        return self.endl

    def set_adopt(self, val):
        self.adopt = val

    def get_adopt(self):
        return self.adopt

    def set_prefix(self, val):
        self.prefix = val

    def get_prefix(self):
        return self.prefix
    
    def set_conc(self, val):
        self.conc = val

    def get_conc(self):
        return self.conc

    def set_alt_name(self, val):
        self.altname = val

    def get_alt_name(self):
        return self.altname

    def set_alt_calendar(self, val):
        self.cal = val

    def get_alt_calendar(self):
        return self.cal

    def set_obje(self, val):
        self.obje = val

    def get_obje(self):
        return self.obje

    def set_resi(self, val):
        self.resi = val

    def get_resi(self):
        return self.resi

    def set_source_refs(self, val):
        self.source_refs = val

    def get_source_refs(self):
        return self.source_refs

    def add_tag_value(self, tag, value):
        self.gramps2tag_map[value] = tag
        self.tag2gramps_map[tag] = value

    def gramps2tag(self, key):
        if key in self.gramps2tag_map:
            return self.gramps2tag_map[key]
        return ""

    def tag2gramps(self, key):
        if key in self.tag2gramps_map:
            return self.tag2gramps_map[key]
        return key

#-------------------------------------------------------------------------
#
# GedcomInfoDB
#
#-------------------------------------------------------------------------
class GedcomInfoDB(object):
    def __init__(self):
        self.map = {}

        self.standard = GedcomDescription("GEDCOM 5.5 standard")
        self.standard.set_dest("GEDCOM 5.5")

        try:
            filepath = os.path.join(const.DATA_DIR,"gedcom.xml")
            ged_file = open(filepath.encode('iso8859-1'),"r")
        except:
            return

        parser = GedInfoParser(self)
        parser.parse(ged_file)
        ged_file.close()

    def add_description(self, name, obj):
        self.map[name] = obj

    def get_description(self, name):
        if name in self.map:
            return self.map[name]
        return self.standard

    def get_from_source_tag(self, name):
        for k, val in self.map.iteritems():
            if val.get_dest() == name:
                return val
        return self.standard

    def get_name_list(self):
        return ["GEDCOM 5.5 standard"] + sorted(self.map)
    
#-------------------------------------------------------------------------
#
# GedInfoParser
#
#-------------------------------------------------------------------------
class GedInfoParser(object):
    def __init__(self, parent):
        self.parent = parent
        self.current = None

    def parse(self, ged_file):
        p = ParserCreate()
        p.StartElementHandler = self.startElement
        p.ParseFile(ged_file)
        
    def startElement(self, tag, attrs):
        if tag == "target":
            name = attrs['name']
            self.current = GedcomDescription(name)
            self.parent.add_description(name, self.current)
        elif tag == "dest":
            self.current.set_dest(attrs['val'])
        elif tag == "endl":
            self.current.set_endl(attrs['val'])
        elif tag == "adopt":
            val = attrs['val']
            if val == 'none':
                self.current.set_adopt(ADOPT_NONE)
            elif val == 'event':
                self.current.set_adopt(ADOPT_EVENT)
            elif val == 'ftw':
                self.current.set_adopt(ADOPT_FTW)
            elif val == 'legacy':
                self.current.set_adopt(ADOPT_LEGACY)
            elif val == 'pedigree':
                self.current.set_adopt(ADOPT_PEDI)
        elif tag == "conc":
            if attrs['val'] == 'broken':
                self.current.set_conc(CONC_BROKEN)
        elif tag == "alternate_names":
            val = attrs['val']
            if val == 'none':
                self.current.set_alt_name(ALT_NAME_NONE)
            elif val == 'event_aka':
                self.current.set_alt_name(ALT_NAME_EVENT_AKA)
            elif val == 'alias':
                self.current.set_alt_name(ALT_NAME_ALIAS)
            elif val == 'aka':
                self.current.set_alt_name(ALT_NAME_AKA)
            elif val == '_alias':
                self.current.set_alt_name(ALT_NAME_UALIAS)
        elif tag == "calendars":
            if attrs['val'] == 'no':
                self.current.set_alt_calendar(CALENDAR_NO)
        elif tag == "event":
            self.current.add_tag_value(attrs['tag'], attrs['value'])
        elif tag == "object_support":
            if attrs['val'] == 'no':
                self.current.set_obje(OBJE_NO)
        elif tag == "prefix":
            if attrs['val'] == 'no':
                self.current.set_obje(PREFIX_NO)
        elif tag == "residence":
            if attrs['val'] == 'place':
                self.current.set_resi(RESIDENCE_PLAC)
        elif tag == "source_refs":
            if attrs['val'] == 'no':
                self.current.set_source_refs(SOURCE_REFS_NO)

#-------------------------------------------------------------------------
#
# File Readers
#
#-------------------------------------------------------------------------
class BaseReader(object):
    def __init__(self, ifile, encoding):
        self.ifile = ifile
        self.enc = encoding

    def reset(self):
        self.ifile.seek(0)

    def readline(self):
        line = unicode(self.ifile.readline(), 
                       encoding=self.enc,
                       errors='replace')
        return line.translate(STRIP_DICT)

class UTF8Reader(BaseReader):

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, 'utf8')
        self.reset()

    def reset(self):
        self.ifile.seek(0)
        data = self.ifile.read(3)
        if data != "\xef\xbb\xbf":
            self.ifile.seek(0)

    def readline(self):
        line =  unicode(self.ifile.readline(),
                       encoding=self.enc,
                       errors='replace')
        return line.translate(STRIP_DICT)

class UTF16Reader(BaseReader):

    def __init__(self, ifile):
        new_file = codecs.EncodedFile(ifile, 'utf8', 'utf16')
        BaseReader.__init__(self, new_file, 'utf16')
        self.reset()

    def readline(self):
        l = unicode(self.ifile.readline())
        if l.strip():
            return l.translate(STRIP_DICT)
        else:
            return unicode(self.ifile.readline()).translate(STRIP_DICT)

class AnsiReader(BaseReader):

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, 'latin1')
    
class AnselReader(BaseReader):
    """
    ANSEL to Unicode Conversion
    
    ANSEL references:
    http://lcweb2.loc.gov/diglib/codetables/45.html
    http://www.gymel.com/charsets/ANSEL.html
    
    list of ANSEL codes that replicate ASCII
    note that DEL (127=0x7F) is a control char
    Note: spec allows control-chars that Gramps probably doesn't use
    but 10=0x0A _is_ needed (!)
    ---
    Also: there are two additional control chars 0x98,0x9c (unicode same)
    which we also ignore for now (start/emd of string (or sort sequence)
    ---
    TODO: should we allow TAB, as a Gramps extension?
    """
    __printable_ascii = map(chr, range(32, 127)) # note: up thru 126
    __use_ASCII = map(chr, [10, 27, 29 , 30, 31]) + __printable_ascii
    
    # mappings of single byte ANSEL codes to unicode
    __onebyte = {
         '\xA1' : u'\u0141',   '\xA2' : u'\u00d8',   '\xA3' : u'\u0110',   
         '\xA4' : u'\u00de',   '\xA5' : u'\u00c6',   '\xA6' : u'\u0152',   
         '\xA7' : u'\u02b9',   '\xA8' : u'\u00b7',   '\xA9' : u'\u266d',   
         '\xAA' : u'\u00ae',   '\xAB' : u'\u00b1',   '\xAC' : u'\u01a0',   
         '\xAD' : u'\u01af',   '\xAE' : u'\u02bc',   '\xB0' : u'\u02bb',   
         '\xB1' : u'\u0142',   '\xB2' : u'\u00f8',   '\xB3' : u'\u0111',   
         '\xB4' : u'\u00fe',   '\xB5' : u'\u00e6',   '\xB6' : u'\u0153',   
         '\xB7' : u'\u02ba',   '\xB8' : u'\u0131',   '\xB9' : u'\u00a3',   
         '\xBA' : u'\u00f0',   '\xBC' : u'\u01a1',   '\xBD' : u'\u01b0',   
         '\xC0' : u'\u00b0',   '\xC1' : u'\u2113',   '\xC2' : u'\u2117',   
         '\xC3' : u'\u00a9',   '\xC4' : u'\u266f',   '\xC5' : u'\u00bf',   
         '\xC6' : u'\u00a1',   '\xC7' : u'\u00df',   '\xC8' : u'\u20ac',  
        }
    
    # combining forms (in ANSEL, they precede the modified ASCII character
    # whereas the unicode combining term follows the character modified
    # Note: unicode allows multiple modifiers, but ANSEL may not (TDB?), 
    # so we ignore multiple combining forms in this module
    #  8d & 8e are zero-width joiner (ZWJ), and zero-width non-joiner ZWNJ
    #  (strange things) probably not commonly found in our needs, unless one
    #   starts writing persian (or???) poetry in ANSEL
    __acombiners = {
         '\x8D' : u'\u200d',   '\x8E' : u'\u200c',   '\xE0' : u'\u0309',   
         '\xE1' : u'\u0300',   '\xE2' : u'\u0301',   '\xE3' : u'\u0302',   
         '\xE4' : u'\u0303',   '\xE5' : u'\u0304',   '\xE6' : u'\u0306',   
         '\xE7' : u'\u0307',   '\xE8' : u'\u0308',   '\xE9' : u'\u030c',   
         '\xEA' : u'\u030a',   '\xEB' : u'\ufe20',   '\xEC' : u'\ufe21',   
         '\xED' : u'\u0315',   '\xEE' : u'\u030b',   '\xEF' : u'\u0310',   
         '\xF0' : u'\u0327',   '\xF1' : u'\u0328',   '\xF2' : u'\u0323',   
         '\xF3' : u'\u0324',   '\xF4' : u'\u0325',   '\xF5' : u'\u0333',   
         '\xF6' : u'\u0332',   '\xF7' : u'\u0326',   '\xF8' : u'\u031c',   
         '\xF9' : u'\u032e',   '\xFA' : u'\ufe22',   '\xFB' : u'\ufe23',   
         '\xFE' : u'\u0313',  
       }
    
    # mappings of two byte (precomposed forms) ANSEL codes to unicode
    __twobyte = {
         '\xE0\x41' : u'\u1ea2',   '\xE0\x45' : u'\u1eba',
         '\xE0\x49' : u'\u1ec8',   '\xE0\x4F' : u'\u1ece',
         '\xE0\x55' : u'\u1ee6',   '\xE0\x59' : u'\u1ef6',
         '\xE0\x61' : u'\u1ea3',   '\xE0\x65' : u'\u1ebb',
         '\xE0\x69' : u'\u1ec9',   '\xE0\x6F' : u'\u1ecf',
         '\xE0\x75' : u'\u1ee7',   '\xE0\x79' : u'\u1ef7',
         '\xE1\x41' : u'\u00c0',   '\xE1\x45' : u'\u00c8',
         '\xE1\x49' : u'\u00cc',   '\xE1\x4F' : u'\u00d2',
         '\xE1\x55' : u'\u00d9',   '\xE1\x57' : u'\u1e80',
         '\xE1\x59' : u'\u1ef2',   '\xE1\x61' : u'\u00e0',
         '\xE1\x65' : u'\u00e8',   '\xE1\x69' : u'\u00ec',
         '\xE1\x6F' : u'\u00f2',   '\xE1\x75' : u'\u00f9',
         '\xE1\x77' : u'\u1e81',   '\xE1\x79' : u'\u1ef3',
         '\xE2\x41' : u'\u00c1',   '\xE2\x43' : u'\u0106',
         '\xE2\x45' : u'\u00c9',   '\xE2\x47' : u'\u01f4',
         '\xE2\x49' : u'\u00cd',   '\xE2\x4B' : u'\u1e30',
         '\xE2\x4C' : u'\u0139',   '\xE2\x4D' : u'\u1e3e',
         '\xE2\x4E' : u'\u0143',   '\xE2\x4F' : u'\u00d3',
         '\xE2\x50' : u'\u1e54',   '\xE2\x52' : u'\u0154',
         '\xE2\x53' : u'\u015a',   '\xE2\x55' : u'\u00da',
         '\xE2\x57' : u'\u1e82',   '\xE2\x59' : u'\u00dd',
         '\xE2\x5A' : u'\u0179',   '\xE2\x61' : u'\u00e1',
         '\xE2\x63' : u'\u0107',   '\xE2\x65' : u'\u00e9',
         '\xE2\x67' : u'\u01f5',   '\xE2\x69' : u'\u00ed',
         '\xE2\x6B' : u'\u1e31',   '\xE2\x6C' : u'\u013a',
         '\xE2\x6D' : u'\u1e3f',   '\xE2\x6E' : u'\u0144',
         '\xE2\x6F' : u'\u00f3',   '\xE2\x70' : u'\u1e55',
         '\xE2\x72' : u'\u0155',   '\xE2\x73' : u'\u015b',
         '\xE2\x75' : u'\u00fa',   '\xE2\x77' : u'\u1e83',
         '\xE2\x79' : u'\u00fd',   '\xE2\x7A' : u'\u017a',
         '\xE2\xA5' : u'\u01fc',   '\xE2\xB5' : u'\u01fd',
         '\xE3\x41' : u'\u00c2',   '\xE3\x43' : u'\u0108',
         '\xE3\x45' : u'\u00ca',   '\xE3\x47' : u'\u011c',
         '\xE3\x48' : u'\u0124',   '\xE3\x49' : u'\u00ce',
         '\xE3\x4A' : u'\u0134',   '\xE3\x4F' : u'\u00d4',
         '\xE3\x53' : u'\u015c',   '\xE3\x55' : u'\u00db',
         '\xE3\x57' : u'\u0174',   '\xE3\x59' : u'\u0176',
         '\xE3\x5A' : u'\u1e90',   '\xE3\x61' : u'\u00e2',
         '\xE3\x63' : u'\u0109',   '\xE3\x65' : u'\u00ea',
         '\xE3\x67' : u'\u011d',   '\xE3\x68' : u'\u0125',
         '\xE3\x69' : u'\u00ee',   '\xE3\x6A' : u'\u0135',
         '\xE3\x6F' : u'\u00f4',   '\xE3\x73' : u'\u015d',
         '\xE3\x75' : u'\u00fb',   '\xE3\x77' : u'\u0175',
         '\xE3\x79' : u'\u0177',   '\xE3\x7A' : u'\u1e91',
         '\xE4\x41' : u'\u00c3',   '\xE4\x45' : u'\u1ebc',
         '\xE4\x49' : u'\u0128',   '\xE4\x4E' : u'\u00d1',
         '\xE4\x4F' : u'\u00d5',   '\xE4\x55' : u'\u0168',
         '\xE4\x56' : u'\u1e7c',   '\xE4\x59' : u'\u1ef8',
         '\xE4\x61' : u'\u00e3',   '\xE4\x65' : u'\u1ebd',
         '\xE4\x69' : u'\u0129',   '\xE4\x6E' : u'\u00f1',
         '\xE4\x6F' : u'\u00f5',   '\xE4\x75' : u'\u0169',
         '\xE4\x76' : u'\u1e7d',   '\xE4\x79' : u'\u1ef9',
         '\xE5\x41' : u'\u0100',   '\xE5\x45' : u'\u0112',
         '\xE5\x47' : u'\u1e20',   '\xE5\x49' : u'\u012a',
         '\xE5\x4F' : u'\u014c',   '\xE5\x55' : u'\u016a',
         '\xE5\x61' : u'\u0101',   '\xE5\x65' : u'\u0113',
         '\xE5\x67' : u'\u1e21',   '\xE5\x69' : u'\u012b',
         '\xE5\x6F' : u'\u014d',   '\xE5\x75' : u'\u016b',
         '\xE5\xA5' : u'\u01e2',   '\xE5\xB5' : u'\u01e3',
         '\xE6\x41' : u'\u0102',   '\xE6\x45' : u'\u0114',   
         '\xE6\x47' : u'\u011e',   '\xE6\x49' : u'\u012c',
         '\xE6\x4F' : u'\u014e',   '\xE6\x55' : u'\u016c',
         '\xE6\x61' : u'\u0103',   '\xE6\x65' : u'\u0115',
         '\xE6\x67' : u'\u011f',   '\xE6\x69' : u'\u012d',
         '\xE6\x6F' : u'\u014f',   '\xE6\x75' : u'\u016d',
         '\xE7\x42' : u'\u1e02',   '\xE7\x43' : u'\u010a',
         '\xE7\x44' : u'\u1e0a',   '\xE7\x45' : u'\u0116',
         '\xE7\x46' : u'\u1e1e',   '\xE7\x47' : u'\u0120',
         '\xE7\x48' : u'\u1e22',   '\xE7\x49' : u'\u0130',
         '\xE7\x4D' : u'\u1e40',   '\xE7\x4E' : u'\u1e44',
         '\xE7\x50' : u'\u1e56',   '\xE7\x52' : u'\u1e58',
         '\xE7\x53' : u'\u1e60',   '\xE7\x54' : u'\u1e6a',
         '\xE7\x57' : u'\u1e86',   '\xE7\x58' : u'\u1e8a',
         '\xE7\x59' : u'\u1e8e',   '\xE7\x5A' : u'\u017b',
         '\xE7\x62' : u'\u1e03',   '\xE7\x63' : u'\u010b',
         '\xE7\x64' : u'\u1e0b',   '\xE7\x65' : u'\u0117',
         '\xE7\x66' : u'\u1e1f',   '\xE7\x67' : u'\u0121',
         '\xE7\x68' : u'\u1e23',   '\xE7\x6D' : u'\u1e41',
         '\xE7\x6E' : u'\u1e45',   '\xE7\x70' : u'\u1e57',
         '\xE7\x72' : u'\u1e59',   '\xE7\x73' : u'\u1e61',
         '\xE7\x74' : u'\u1e6b',   '\xE7\x77' : u'\u1e87',
         '\xE7\x78' : u'\u1e8b',   '\xE7\x79' : u'\u1e8f',
         '\xE7\x7A' : u'\u017c',   '\xE8\x41' : u'\u00c4',
         '\xE8\x45' : u'\u00cb',   '\xE8\x48' : u'\u1e26',
         '\xE8\x49' : u'\u00cf',   '\xE8\x4F' : u'\u00d6',
         '\xE8\x55' : u'\u00dc',   '\xE8\x57' : u'\u1e84',
         '\xE8\x58' : u'\u1e8c',   '\xE8\x59' : u'\u0178',
         '\xE8\x61' : u'\u00e4',   '\xE8\x65' : u'\u00eb',
         '\xE8\x68' : u'\u1e27',   '\xE8\x69' : u'\u00ef',
         '\xE8\x6F' : u'\u00f6',   '\xE8\x74' : u'\u1e97',
         '\xE8\x75' : u'\u00fc',   '\xE8\x77' : u'\u1e85',
         '\xE8\x78' : u'\u1e8d',   '\xE8\x79' : u'\u00ff',
         '\xE9\x41' : u'\u01cd',   '\xE9\x43' : u'\u010c',
         '\xE9\x44' : u'\u010e',   '\xE9\x45' : u'\u011a',
         '\xE9\x47' : u'\u01e6',   '\xE9\x49' : u'\u01cf',
         '\xE9\x4B' : u'\u01e8',   '\xE9\x4C' : u'\u013d',
         '\xE9\x4E' : u'\u0147',   '\xE9\x4F' : u'\u01d1',
         '\xE9\x52' : u'\u0158',   '\xE9\x53' : u'\u0160',
         '\xE9\x54' : u'\u0164',   '\xE9\x55' : u'\u01d3',
         '\xE9\x5A' : u'\u017d',   '\xE9\x61' : u'\u01ce',
         '\xE9\x63' : u'\u010d',   '\xE9\x64' : u'\u010f',
         '\xE9\x65' : u'\u011b',   '\xE9\x67' : u'\u01e7',
         '\xE9\x69' : u'\u01d0',   '\xE9\x6A' : u'\u01f0',
         '\xE9\x6B' : u'\u01e9',   '\xE9\x6C' : u'\u013e',
         '\xE9\x6E' : u'\u0148',   '\xE9\x6F' : u'\u01d2',
         '\xE9\x72' : u'\u0159',   '\xE9\x73' : u'\u0161',
         '\xE9\x74' : u'\u0165',   '\xE9\x75' : u'\u01d4',
         '\xE9\x7A' : u'\u017e',   '\xEA\x41' : u'\u00c5',
         '\xEA\x61' : u'\u00e5',   '\xEA\x75' : u'\u016f',
         '\xEA\x77' : u'\u1e98',   '\xEA\x79' : u'\u1e99',
         '\xEA\xAD' : u'\u016e',   '\xEE\x4F' : u'\u0150',
         '\xEE\x55' : u'\u0170',   '\xEE\x6F' : u'\u0151',
         '\xEE\x75' : u'\u0171',   '\xF0\x20' : u'\u00b8',
         '\xF0\x43' : u'\u00c7',   '\xF0\x44' : u'\u1e10',
         '\xF0\x47' : u'\u0122',   '\xF0\x48' : u'\u1e28',
         '\xF0\x4B' : u'\u0136',   '\xF0\x4C' : u'\u013b',
         '\xF0\x4E' : u'\u0145',   '\xF0\x52' : u'\u0156',   
         '\xF0\x53' : u'\u015e',   '\xF0\x54' : u'\u0162',
         '\xF0\x63' : u'\u00e7',   '\xF0\x64' : u'\u1e11',
         '\xF0\x67' : u'\u0123',   '\xF0\x68' : u'\u1e29',
         '\xF0\x6B' : u'\u0137',   '\xF0\x6C' : u'\u013c',
         '\xF0\x6E' : u'\u0146',   '\xF0\x72' : u'\u0157',
         '\xF0\x73' : u'\u015f',   '\xF0\x74' : u'\u0163',
         '\xF1\x41' : u'\u0104',   '\xF1\x45' : u'\u0118',
         '\xF1\x49' : u'\u012e',   '\xF1\x4F' : u'\u01ea',
         '\xF1\x55' : u'\u0172',   '\xF1\x61' : u'\u0105',
         '\xF1\x65' : u'\u0119',   '\xF1\x69' : u'\u012f',
         '\xF1\x6F' : u'\u01eb',   '\xF1\x75' : u'\u0173',
         '\xF2\x41' : u'\u1ea0',   '\xF2\x42' : u'\u1e04',
         '\xF2\x44' : u'\u1e0c',   '\xF2\x45' : u'\u1eb8',
         '\xF2\x48' : u'\u1e24',   '\xF2\x49' : u'\u1eca',
         '\xF2\x4B' : u'\u1e32',   '\xF2\x4C' : u'\u1e36',
         '\xF2\x4D' : u'\u1e42',   '\xF2\x4E' : u'\u1e46',
         '\xF2\x4F' : u'\u1ecc',   '\xF2\x52' : u'\u1e5a',
         '\xF2\x53' : u'\u1e62',   '\xF2\x54' : u'\u1e6c',
         '\xF2\x55' : u'\u1ee4',   '\xF2\x56' : u'\u1e7e',
         '\xF2\x57' : u'\u1e88',   '\xF2\x59' : u'\u1ef4',
         '\xF2\x5A' : u'\u1e92',   '\xF2\x61' : u'\u1ea1',
         '\xF2\x62' : u'\u1e05',   '\xF2\x64' : u'\u1e0d',
         '\xF2\x65' : u'\u1eb9',   '\xF2\x68' : u'\u1e25',
         '\xF2\x69' : u'\u1ecb',   '\xF2\x6B' : u'\u1e33',
         '\xF2\x6C' : u'\u1e37',   '\xF2\x6D' : u'\u1e43',
         '\xF2\x6E' : u'\u1e47',   '\xF2\x6F' : u'\u1ecd',
         '\xF2\x72' : u'\u1e5b',   '\xF2\x73' : u'\u1e63',
         '\xF2\x74' : u'\u1e6d',   '\xF2\x75' : u'\u1ee5',
         '\xF2\x76' : u'\u1e7f',   '\xF2\x77' : u'\u1e89',
         '\xF2\x79' : u'\u1ef5',   '\xF2\x7A' : u'\u1e93',
         '\xF3\x55' : u'\u1e72',   '\xF3\x75' : u'\u1e73',
         '\xF4\x41' : u'\u1e00',   '\xF4\x61' : u'\u1e01',
         '\xF9\x48' : u'\u1e2a',   '\xF9\x68' : u'\u1e2b',  
       }

    @staticmethod
    def __ansel_to_unicode(s):
        """ Convert an ANSEL encoded string to unicode """
    
        buff = cStringIO.StringIO()
        while s:
            if ord(s[0]) < 128:
                if s[0] in AnselReader.__use_ASCII:
                    head = s[0]
                else:
                    # substitute space for disallowed (control) chars
                    head = ' '
                s = s[1:]
            else:
                if s[0:2] in AnselReader.__twobyte:
                    head = AnselReader.__twobyte[s[0:2]]
                    s = s[2:]
                elif s[0] in AnselReader.__onebyte:
                    head = AnselReader.__onebyte[s[0]]
                    s = s[1:]
                elif s[0] in AnselReader.__acombiners:
                    c =  AnselReader.__acombiners[s[0]]
                    # always consume the combiner
                    s = s[1:]
                    next = s[0]
                    if next in AnselReader.__printable_ascii:
                        # consume next as well
                        s = s[1:]
                        # unicode: combiner follows base-char
                        head = next + c
                    else:
                        # just drop the unexpected combiner
                        continue 
                else:
                    head = u'\ufffd' # "Replacement Char"
                    s = s[1:]
            # note: cStringIO handles 8-bit strings, only (no unicode)
            buff.write(head.encode("utf-8"))
        ans = unicode(buff.getvalue(), "utf-8")
        buff.close()
        return ans

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, "")

    def readline(self):
        return self.__ansel_to_unicode(self.ifile.readline())
    
#-------------------------------------------------------------------------
#
# CurrentState
#
#-------------------------------------------------------------------------
class CurrentState(object):
    """
    Keep track of the current state variables.
    """
    def __init__(self, person=None, level=0, event=None, event_ref=None):
        """
        Initialize the object.
        """
        self.name_cnt = 0
        self.person = person
        self.family = None
        self.level = level
        self.event = event
        self.event_ref = event_ref
        self.source_ref = None
        self.citation = None
        self.note = None
        self.lds_ord = None
        self.msg = ""
        self.primary = False        # _PRIM tag on an INDI.FAMC tag
        self.filename = ""
        self.title = ""
        self.addr = None
        self.res = None
        self.source = None
        self.ftype = None
        self.pf = None              # method for parsing places
        self.location = None
        self.place_fields = None    # method for parsing places
        self.ref = None             # PersonRef
        self.handle = None          # 
        self.form = ""              # Multimedia format
        self.frel = None            # Child relation to father
        self.mrel = None
        self.repo = None
        self.attr = None
        self.obj = None
        self.name = ""
        self.ignore = False
        self.repo_ref = None
        self.place = None
        self.media = None

    def __getattr__(self, name):
        """
        Return the value associated with the specified attribute.
        """
        return self.__dict__.get(name)

    def __setattr__(self, name, value):
        """
        Set the value associated with the specified attribute.
        """
        self.__dict__[name] = value

#-------------------------------------------------------------------------
#
# PlaceParser
#
#-------------------------------------------------------------------------
class PlaceParser(object):
    """
    Provide the ability to parse GEDCOM FORM statements for places, and
    the parse the line of text, mapping the text components to Location
    values based of the FORM statement.
    """

    __field_map = {
    'addr'          : gen.lib.Location.set_street,
    'subdivision'   : gen.lib.Location.set_street,
    'addr1'         : gen.lib.Location.set_street,
    'adr1'          : gen.lib.Location.set_street,
    'street'        : gen.lib.Location.set_street,
    'addr2'         : gen.lib.Location.set_locality,
    'adr2'          : gen.lib.Location.set_locality,
    'locality'      : gen.lib.Location.set_locality,
    'neighborhood'  : gen.lib.Location.set_locality,
    'city'          : gen.lib.Location.set_city,
    'town'          : gen.lib.Location.set_city,
    'village'       : gen.lib.Location.set_city,
    'county'        : gen.lib.Location.set_county,
    'country'       : gen.lib.Location.set_country,
    'state'         : gen.lib.Location.set_state,
    'state/province': gen.lib.Location.set_state,
    'region'        : gen.lib.Location.set_state,
    'province'      : gen.lib.Location.set_state,
    'area code'     : gen.lib.Location.set_postal_code,
    'post code'     : gen.lib.Location.set_postal_code,
    'zip code'      : gen.lib.Location.set_postal_code,
    }

    def __init__(self, line=None):
        self.parse_function = []

        if line:
            self.parse_form(line)

    def parse_form(self, line):
        """
        Parses the GEDCOM PLAC.FORM into a list of function
        pointers (if possible). It does this my mapping the text strings
        (separated by commas) to the corresponding gen.lib.Location
        method via the __field_map variable
        """
        for item in line.data.split(','):
            item = item.lower().strip()
            fcn = self.__field_map.get(item, lambda x, y: None)
            self.parse_function.append(fcn)

    def load_place(self, place, text):
        """
        Takes the text string representing a place, splits it into
        its subcomponents (comma separated), and calls the approriate
        function based of its position, depending on the parsed value
        from the FORM statement.
        """
        items = [item.strip() for item in text.split(',')]
        if len(items) != len(self.parse_function):
            return
        loc = place.get_main_location()
        index = 0
        for item in items:
            self.parse_function[index](loc, item)
            index += 1

#-------------------------------------------------------------------------
#
# IdFinder
#
#-------------------------------------------------------------------------
class IdFinder(object):
    """
    Provide method of finding the next available ID.
    """
    def __init__(self, keys, prefix):
        """
        Initialize the object.
        """
        self.ids = set(keys)
        self.index = 0
        self.prefix = prefix

    def find_next(self):
        """
        Return the next available GRAMPS' ID for a Event object based
        off the person ID prefix.

        @return: Returns the next available index
        @rtype: str
        """
        index = self.prefix % self.index
        while str(index) in self.ids:
            self.index += 1
            index = self.prefix % self.index
        self.ids.add(index)
        self.index += 1
        return index

#-------------------------------------------------------------------------
#
# IdMapper
#
#-------------------------------------------------------------------------
class IdMapper(object):

    def __init__(self, trans, find_next, id2user_format):
        self.trans = trans
        self.find_next = find_next
        self.id2user_format = id2user_format
        self.swap = {}
    
    def __getitem__(self, gid):
        if gid == "":
            # We need to find the next gramps ID provided it is not already
            # the target of a swap
            new_val = self.find_next()
            while new_val in self.swap.values():
                new_val = self.find_next()
        else:
            # remove any @ signs
            gid = self.clean(gid)
            if gid in self.swap:
                return self.swap[gid]
            else:
                # now standardise the format
                formatted_gid = self.id2user_format(gid)
                # I1 and I0001 will both format as I0001. If we had already
                # encountered I1, it would be in self.swap, so we would already
                # have found it. If we had already encountered I0001 and we are
                # now looking for I1, it wouldn't be in self.swap, and we now
                # find that I0001 is in use, so we have to create a new id.
                if self.trans.get(str(formatted_gid)) or \
                        (formatted_gid in self.swap.values()):
                    new_val = self.find_next()
                    while new_val in self.swap.values():
                        new_val = self.find_next()
                else:
                    new_val = formatted_gid
            # we need to distinguish between I1 and I0001, so we record the map
            # from the original format
            self.swap[gid] = new_val
        return new_val
    
    def clean(self, gid):
        temp = gid.strip()
        if len(temp) > 1 and temp[0] == '@' and temp[-1] == '@':
            temp = temp[1:-1]
        return temp
    
    def map(self):
        return self.swap

#-------------------------------------------------------------------------
#
# GedcomParser
#
#-------------------------------------------------------------------------
class GedcomParser(UpdateCallback):
    """
    Performs the second pass of the GEDCOM parser, which does all the heavy
    lifting.
    """

    __TRUNC_MSG = _("Your GEDCOM file is corrupted. "
                    "It appears to have been truncated.")
    _EMPTY_LOC = gen.lib.Location().serialize()

    SyntaxError = "Syntax Error"
    BadFile = "Not a GEDCOM file"
    
    @staticmethod
    def __find_from_handle(gramps_id, table):
        """
        Find a handle corresponding to the specified GRAMPS ID. 
        
        The passed table contains the mapping. If the value is found, we return 
        it, otherwise we create a new handle, store it, and return it.
        
        """
        intid = table.get(gramps_id)
        if not intid:
            intid = Utils.create_id()
            table[gramps_id] = intid
        return intid
    
    @staticmethod
    def __parse_name_personal(text):
        """
        Parses a GEDCOM NAME value into an Name structure
        """
        name = gen.lib.Name()
    
        match = SURNAME_RE.match(text)
        if match:
            #/surname/ extra, we assume extra is given name
            names = match.groups()
            name.set_first_name(names[1].strip())
            surn = gen.lib.Surname()
            surn.set_surname(names[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
        else:
            try:
                names = NAME_RE.match(text).groups()
                # given /surname/ extra, we assume extra is suffix
                name.set_first_name(names[0].strip())
                surn = gen.lib.Surname()
                surn.set_surname(names[2].strip())
                surn.set_primary()
                name.set_surname_list([surn])
                name.set_suffix(names[4].strip())
            except:
                # something strange, set as first name
                name.set_first_name(text.strip())
        return name

    def __init__(self, dbase, ifile, filename, callback, stage_one, 
                 default_source):
        UpdateCallback.__init__(self, callback)

        self.set_total(stage_one.get_line_count())
        self.repo2id = {}
        self.trans = None
        self.errors = []
        self.number_of_errors = 0
        self.maxpeople = stage_one.get_person_count()
        self.dbase = dbase
        self.import_researcher = self.dbase.is_empty()
        self.emapper = IdFinder(dbase.get_gramps_ids(EVENT_KEY),
                                dbase.event_prefix)
        self.famc_map = stage_one.get_famc_map()
        self.fams_map = stage_one.get_fams_map()

        self.place_parser = PlaceParser()
        self.inline_srcs = {}
        self.media_map = {}
        self.genby = ""
        self.genvers = ""
        self.subm = ""
        self.gedmap = GedcomInfoDB()
        self.gedsource = self.gedmap.get_from_source_tag('GEDCOM 5.5')
        self.use_def_src = default_source
        self.func_list = []
        if self.use_def_src:
            self.def_src = gen.lib.Source()
            fname = os.path.basename(filename).split('\\')[-1]
            self.def_src.set_title(_("Import from GEDCOM (%s)") % fname)
        self.dir_path = os.path.dirname(filename)
        self.is_ftw = False
        self.groups = None
        self.want_parse_warnings = True

        self.pid_map = IdMapper(
            self.dbase.id_trans, 
            self.dbase.find_next_person_gramps_id, 
            self.dbase.id2user_format)
        self.fid_map = IdMapper(
            self.dbase.fid_trans, 
            self.dbase.find_next_family_gramps_id, 
            self.dbase.fid2user_format)
        self.sid_map = IdMapper(
            self.dbase.sid_trans, 
            self.dbase.find_next_source_gramps_id, 
            self.dbase.sid2user_format)
        self.oid_map = IdMapper(
            self.dbase.oid_trans, 
            self.dbase.find_next_object_gramps_id, 
            self.dbase.oid2user_format)
        self.rid_map = IdMapper(
            self.dbase.rid_trans, 
            self.dbase.find_next_repository_gramps_id, 
            self.dbase.rid2user_format)
        self.nid_map = IdMapper(
            self.dbase.nid_trans, 
            self.dbase.find_next_note_gramps_id, 
            self.dbase.nid2user_format)

        self.gid2id = {}
        self.oid2id = {}
        self.sid2id = {}
        self.lid2id = {}
        self.fid2id = {}
        self.rid2id = {}
        self.nid2id = {}

        #
        # Parse table for <<SUBMITTER_RECORD>> below the level 0 SUBM tag
        #
        # n @<XREF:SUBM>@   SUBM                          {1:1}
        #   +1 NAME <SUBMITTER_NAME>                      {1:1}
        #   +1 <<ADDRESS_STRUCTURE>>                      {0:1}
        #   +1 <<MULTIMEDIA_LINK>>                        {0:M}
        #   +1 LANG <LANGUAGE_PREFERENCE>                 {0:3}
        #   +1 RFN <SUBMITTER_REGISTERED_RFN>             {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        # (N.B. GEDCOM allows multiple SUBMitter records)
        self.subm_parse_tbl = {
            # +1 NAME <SUBMITTER_NAME>
            TOKEN_NAME  : self.__subm_name, 
            # +1 <<ADDRESS_STRUCTURE>>
            TOKEN_ADDR  : self.__subm_addr, 
            TOKEN_PHON  : self.__subm_phon,
            TOKEN_EMAIL : self.__subm_email, 
            # +1 <<MULTIMEDIA_LINK>>
            # +1 LANG <LANGUAGE_PREFERENCE>
            # +1 RFN <SUBMITTER_REGISTERED_RFN>
            # +1 RIN <AUTOMATED_RECORD_ID>
            # +1 <<CHANGE_DATE>>
            TOKEN_CHAN   : self.__repo_chan,
            }
        self.func_list.append(self.subm_parse_tbl)

        #
        # Parse table for <<INDIVIDUAL_RECORD>> below the level 0  INDI tag
        #
        # n @<XREF:INDI>@  INDI                           {1:1}
        #   +1 RESN <RESTRICTION_NOTICE>                  {0:1}
        #   +1 <<PERSONAL_NAME_STRUCTURE>>                {0:M}
        #   +1 SEX <SEX_VALUE>                            {0:1}
        #   +1 <<INDIVIDUAL_EVENT_STRUCTURE>>             {0:M}
        #   +1 <<INDIVIDUAL_ATTRIBUTE_STRUCTURE>>         {0:M}
        #   +1 <<LDS_INDIVIDUAL_ORDINANCE>>               {0:M}
        #   +1 <<CHILD_TO_FAMILY_LINK>>                   {0:M}
        #   +1 <<SPOUSE_TO_FAMILY_LINK>>                  {0:M}
        #   +1 SUBM @<XREF:SUBM>@                         {0:M}
        #   +1 <<ASSOCIATION_STRUCTURE>>                  {0:M}
        #   +1 ALIA @<XREF:INDI>@                         {0:M}
        #   +1 ANCI @<XREF:SUBM>@                         {0:M}
        #   +1 DESI @<XREF:SUBM>@                         {0:M}
        #   +1 <<SOURCE_CITATION>>                        {0:M}
        #   +1 <<MULTIMEDIA_LINK>>                        {0:M}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 RFN <PERMANENT_RECORD_FILE_NUMBER>         {0:1}
        #   +1 AFN <ANCESTRAL_FILE_NUMBER>                {0:1}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>               {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        self.indi_parse_tbl = {
            # +1 RESN <RESTRICTION_NOTICE> {0:1}
            TOKEN_RESN  : self.__person_resn, 
            # +1 <<PERSONAL_NAME_STRUCTURE>> {0:M}
            TOKEN_NAME  : self.__person_name, 
            # +1 SEX <SEX_VALUE> {0:1}
            TOKEN_SEX   : self.__person_sex, 
            # +1 <<INDIVIDUAL_EVENT_STRUCTURE>> {0:M}
            TOKEN_EVEN  : self.__person_even, 
            TOKEN_GEVENT: self.__person_std_event, 
            TOKEN_BIRT  : self.__person_birt, 
            TOKEN_RELI  : self.__person_reli, 
            TOKEN_ADOP  : self.__person_adop, 
            TOKEN_DEAT  : self.__person_deat, 
            # +1 <<INDIVIDUAL_ATTRIBUTE_STRUCTURE>> {0:M}
            # +1 AFN <ANCESTRAL_FILE_NUMBER> {0:1}
            TOKEN_ATTR  : self.__person_std_attr, 
            TOKEN_FACT  : self.__person_fact, 
            #+1 <<LDS_INDIVIDUAL_ORDINANCE>> {0:M}
            TOKEN_BAPL  : self.__person_bapl, 
            TOKEN_CONL  : self.__person_conl, 
            TOKEN_ENDL  : self.__person_endl, 
            TOKEN_SLGC  : self.__person_slgc, 
            #+1 <<CHILD_TO_FAMILY_LINK>> {0:M}
            TOKEN_FAMC  : self.__person_famc, 
            # +1 <<SPOUSE_TO_FAMILY_LINK>> {0:M}
            TOKEN_FAMS  : self.__person_fams, 
            # +1 SUBM @<XREF:SUBM>@ {0:M}
            TOKEN_SUBM  : self.__skip_record, 
            # +1 <<ASSOCIATION_STRUCTURE>> {0:M}
            TOKEN_ASSO  : self.__person_asso, 
            # +1 ALIA @<XREF:INDI>@ {0:M}
            TOKEN_ALIA  : self.__person_alt_name, 
            # +1 ANCI @<XREF:SUBM>@ {0:M}
            TOKEN_ANCI  : self.__skip_record, 
            # +1 DESI @<XREF:SUBM>@ {0:M}
            TOKEN_DESI  : self.__skip_record, 
            # +1 <<SOURCE_CITATION>> {0:M}
            TOKEN_SOUR  : self.__person_sour, 
            # +1 <<MULTIMEDIA_LINK>> {0:M}
            TOKEN_OBJE  : self.__person_object, 
            # +1 <<NOTE_STRUCTURE>> {0:M} 
            TOKEN_NOTE  : self.__person_note, 
            TOKEN_RNOTE : self.__person_note, 
            TOKEN__COMM : self.__person_note, 
            # +1 RFN <PERMANENT_RECORD_FILE_NUMBER> {0:1}
            TOKEN_RFN   : self.__person_attr, 
            # +1 REFN <USER_REFERENCE_NUMBER> {0:M}
            # +2 TYPE <USER_REFERENCE_TYPE> {0:1}
            TOKEN_REFN  : self.__person_attr, 
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE  : self.__person_attr, 
            # +1 RIN <AUTOMATED_RECORD_ID> {0:1}
            TOKEN_RIN   : self.__person_attr, 
            # +1 <<CHANGE_DATE>> {0:1}
            TOKEN_CHAN  : self.__person_chan, 

            TOKEN_ADDR  : self.__person_addr, 
            TOKEN_PHON  : self.__person_phon,
            TOKEN_EMAIL : self.__person_email,
            TOKEN_URL   : self.__person_url, 
            TOKEN__TODO : self.__skip_record, 
            TOKEN_TITL  : self.__person_titl, 
            }
        self.func_list.append(self.indi_parse_tbl)

        self.name_parse_tbl = {
            # +1 NPFX <NAME_PIECE_PREFIX> {0:1}
            TOKEN_NPFX   : self.__name_npfx, 
            # +1 GIVN <NAME_PIECE_GIVEN> {0:1}
            TOKEN_GIVN   : self.__name_givn, 
            # NICK <NAME_PIECE_NICKNAME> {0:1}
            TOKEN_NICK   : self.__name_nick, 
            # +1 SPFX <NAME_PIECE_SURNAME_PREFIX {0:1}
            TOKEN_SPFX   : self.__name_spfx, 
            # +1 SURN <NAME_PIECE_SURNAME> {0:1}
            TOKEN_SURN   : self.__name_surn, 
            # +1 NSFX <NAME_PIECE_SUFFIX> {0:1}
            TOKEN_NSFX   : self.__name_nsfx, 
            # +1 <<SOURCE_CITATION>> {0:M}
            TOKEN_SOUR   : self.__name_sour, 
            # +1 <<NOTE_STRUCTURE>> {0:M}
            TOKEN_NOTE   : self.__name_note, 
            TOKEN_RNOTE  : self.__name_note, 
            # Extensions
            TOKEN_ALIA   : self.__name_alia, 
            TOKEN__MARNM : self.__name_marnm, 
            TOKEN__MAR   : self.__name_marnm,   # Generated by geni.com
            TOKEN__MARN  : self.__name_marnm,   # Gen'd by BROSKEEP 6.1.31 WIN
            TOKEN__AKA   : self.__name_aka,     # PAF and AncestQuest
            TOKEN_TYPE   : self.__name_type,    # This is legal GEDCOM 5.5.1
            TOKEN_BIRT   : self.__ignore, 
            TOKEN_DATE   : self.__name_date,
            # This handles date as a subsidiary of "1 ALIA" which might be used
            # by Family Tree Maker and Reunion, and by cheating (handling a
            # lower level from the current parse table) handles date as
            # subsidiary to "2 _MARN", "2 _AKAN" and "2 _ADPN" which has been
            # found in Brother's keeper.
            TOKEN__ADPN   : self.__name_adpn,
            }
        self.func_list.append(self.name_parse_tbl)

        #
        # Parse table for <<REPOSITORY_RECORD>> below the level 0 REPO tag
        # 
        # n @<XREF:REPO>@ REPO                            {1:1}
        #   +1 NAME <NAME_OF_REPOSITORY>                  {0:1}
        #   +1 <<ADDRESS_STRUCTURE>>                      {0:1}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>               {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        self.repo_parse_tbl = {
            TOKEN_NAME   : self.__repo_name, 
            TOKEN_ADDR   : self.__repo_addr, 
            TOKEN_RIN    : self.__ignore, 
            TOKEN_NOTE   : self.__repo_note, 
            TOKEN_RNOTE  : self.__repo_note, 
            TOKEN_CHAN   : self.__repo_chan, 
            TOKEN_PHON   : self.__repo_phon, 
            TOKEN_EMAIL  : self.__repo_email, 
            TOKEN_WWW    : self.__repo_www, 
            }
        self.func_list.append(self.repo_parse_tbl)

        self.event_parse_tbl = {
            # n TYPE <EVENT_DESCRIPTOR> {0:1}
            TOKEN_TYPE   : self.__event_type, 
            # n DATE <DATE_VALUE> {0:1} p.*/*
            TOKEN_DATE   : self.__event_date, 
            # n <<PLACE_STRUCTURE>> {0:1} p.*
            TOKEN_PLAC   : self.__event_place, 
            # n <<ADDRESS_STRUCTURE>> {0:1} p.*
            TOKEN_ADDR   : self.__event_addr, 
            # n AGE <AGE_AT_EVENT> {0:1} p.*
            TOKEN_AGE    : self.__event_age, 
            # n AGNC <RESPONSIBLE_AGENCY> {0:1} p.*
            TOKEN_AGNC   : self.__event_agnc, 
            # n CAUS <CAUSE_OF_EVENT> {0:1} p.*
            TOKEN_CAUS   : self.__event_cause, 
            # n <<SOURCE_CITATION>> {0:M} p.*
            TOKEN_SOUR   : self.__event_source, 
            # n <<MULTIMEDIA_LINK>> {0:M} p.*, *
            TOKEN_OBJE   : self.__event_object, 
            # n <<NOTE_STRUCTURE>> {0:M} p.
            TOKEN_NOTE   : self.__event_inline_note, 
            TOKEN_RNOTE  : self.__event_note, 
            # Other
            TOKEN__PRIV  : self.__event_privacy, 
            TOKEN_OFFI   : self.__event_note, 
            TOKEN_PHON   : self.__event_phon, 
            TOKEN__GODP  : self.__event_witness, 
            TOKEN__WITN  : self.__event_witness, 
            TOKEN__WTN   : self.__event_witness, 
            TOKEN_RELI   : self.__ignore,
            # Not legal, but inserted by PhpGedView 
            TOKEN_TIME   : self.__event_time, 
            TOKEN_ASSO   : self.__ignore, 
            TOKEN_IGNORE : self.__ignore, 
            TOKEN_STAT   : self.__ignore, 
            TOKEN_TEMP   : self.__ignore, 
            TOKEN_HUSB   : self.__event_husb, 
            TOKEN_WIFE   : self.__event_wife, 
            TOKEN_FAMC   : self.__person_birth_famc, 
            # Not legal, but inserted by Ultimate Family Tree
            TOKEN_CHAN   : self.__ignore, 
            TOKEN_QUAY  : self.__ignore, 
            # Not legal, but inserted by FamilyTreeBuilder
            TOKEN_RIN    : self.__event_rin,
            TOKEN_ATTR   : self.__event_attr,   # FTB for _UID
            TOKEN_EMAIL  : self.__event_email,  # FTB for RESI events
            TOKEN_WWW    : self.__event_www,    # FTB for RESI events
            }
        self.func_list.append(self.event_parse_tbl)

        self.adopt_parse_tbl = {
            TOKEN_TYPE   : self.__event_type, 
            TOKEN__PRIV  : self.__event_privacy, 
            TOKEN_DATE   : self.__event_date, 
            TOKEN_SOUR   : self.__event_source, 
            TOKEN_PLAC   : self.__event_place, 
            TOKEN_ADDR   : self.__event_addr, 
            TOKEN_PHON   : self.__event_phon,
            TOKEN_CAUS   : self.__event_cause, 
            TOKEN_AGNC   : self.__event_agnc, 
            TOKEN_AGE    : self.__event_age, 
            TOKEN_NOTE   : self.__event_note, 
            TOKEN_RNOTE  : self.__event_note, 
            TOKEN_OFFI   : self.__event_note, 
            TOKEN__GODP  : self.__event_witness, 
            TOKEN__WITN  : self.__event_witness, 
            TOKEN__WTN   : self.__event_witness, 
            TOKEN_RELI   : self.__ignore, 
            TOKEN_TIME   : self.__ignore, 
            TOKEN_ASSO   : self.__ignore, 
            TOKEN_IGNORE : self.__ignore, 
            TOKEN_STAT   : self.__ignore, 
            TOKEN_TEMP   : self.__ignore, 
            TOKEN_OBJE   : self.__event_object, 
            TOKEN_FAMC   : self.__person_adopt_famc, 
            # Not legal, but inserted by Ultimate Family Tree
            TOKEN_CHAN   : self.__ignore, 
            TOKEN_QUAY   : self.__ignore, 
            }
        self.func_list.append(self.adopt_parse_tbl)

        self.famc_parse_tbl = {
            # n FAMC @<XREF:FAM>@ {1:1}
            # +1 PEDI <PEDIGREE_LINKAGE_TYPE> {0:M} p.*
            TOKEN_PEDI   : self.__person_famc_pedi, 
            # +1 <<NOTE_STRUCTURE>> {0:M} p.*
            TOKEN_NOTE   : self.__person_famc_note, 
            TOKEN_RNOTE  : self.__person_famc_note, 
            # Extras
            TOKEN__PRIMARY: self.__person_famc_primary, 
            TOKEN_SOUR   : self.__person_famc_sour, 
            # GEDit
            TOKEN_STAT   : self.__ignore, 
            }
        self.func_list.append(self.famc_parse_tbl)

        self.person_fact_parse_tbl = {
            TOKEN_TYPE   : self.__person_fact_type, 
            TOKEN_SOUR   : self.__person_attr_source, 
            TOKEN_NOTE   : self.__person_attr_note, 
            TOKEN_RNOTE  : self.__person_attr_note, 
            }
        self.func_list.append(self.person_fact_parse_tbl)

        self.person_attr_parse_tbl = {
            TOKEN_TYPE   : self.__person_attr_type, 
            TOKEN_CAUS   : self.__ignore, 
            TOKEN_DATE   : self.__ignore, 
            TOKEN_TIME   : self.__ignore, 
            TOKEN_ADDR   : self.__ignore, 
            TOKEN_IGNORE : self.__ignore, 
            TOKEN_STAT   : self.__ignore, 
            TOKEN_TEMP   : self.__ignore, 
            TOKEN_OBJE   : self.__ignore, 
            TOKEN_SOUR   : self.__person_attr_source, 
            TOKEN_PLAC   : self.__person_attr_place, 
            TOKEN_NOTE   : self.__person_attr_note, 
            TOKEN_RNOTE  : self.__person_attr_note, 
            }
        self.func_list.append(self.person_attr_parse_tbl)

        self.lds_parse_tbl = {
            TOKEN_TEMP   : self.__lds_temple, 
            TOKEN_DATE   : self.__lds_date, 
            TOKEN_FAMC   : self.__lds_famc, 
            TOKEN_FORM   : self.__lds_form, 
            TOKEN_PLAC   : self.__lds_plac, 
            TOKEN_SOUR   : self.__lds_sour, 
            TOKEN_NOTE   : self.__lds_note, 
            TOKEN_RNOTE  : self.__lds_note, 
            TOKEN_STAT   : self.__lds_stat, 
            }
        self.func_list.append(self.lds_parse_tbl)

        self.asso_parse_tbl = {
            TOKEN_RELA   : self.__person_asso_rela, 
            TOKEN_SOUR   : self.__person_asso_sour, 
            TOKEN_NOTE   : self.__person_asso_note, 
            TOKEN_RNOTE  : self.__person_asso_note, 
            }
        self.func_list.append(self.asso_parse_tbl)

        self.citation_parse_tbl = {
            TOKEN_PAGE   : self.__citation_page, 
            TOKEN_DATE   : self.__citation_date, 
            TOKEN_DATA   : self.__citation_data, 
            TOKEN_OBJE   : self.__citation_obje, 
            TOKEN_REFN   : self.__citation_refn, 
            TOKEN_EVEN   : self.__citation_even, 
            TOKEN_IGNORE : self.__ignore, 
            TOKEN__LKD   : self.__ignore, 
            TOKEN_QUAY   : self.__citation_quay, 
            TOKEN_NOTE   : self.__citation_note, 
            TOKEN_RNOTE  : self.__citation_note, 
            TOKEN_TEXT   : self.__citation_data_text, 
            }
        self.func_list.append(self.citation_parse_tbl)

        self.object_parse_tbl = {
            TOKEN_FORM   : self.__object_ref_form, 
            TOKEN_TITL   : self.__object_ref_titl, 
            TOKEN_FILE   : self.__object_ref_file, 
            TOKEN_NOTE   : self.__object_ref_note, 
            TOKEN_RNOTE  : self.__object_ref_note, 
            TOKEN_IGNORE : self.__ignore, 
        }
        self.func_list.append(self.object_parse_tbl)

        self.parse_loc_tbl = {
            TOKEN_ADR1   : self.__location_adr1, 
            TOKEN_ADR2   : self.__location_adr2, 
            TOKEN_CITY   : self.__location_city, 
            TOKEN_STAE   : self.__location_stae, 
            TOKEN_POST   : self.__location_post, 
            TOKEN_CTRY   : self.__location_ctry, 
            # Not legal GEDCOM - not clear why these are included at this level 
            TOKEN_ADDR   : self.__ignore, 
            TOKEN_DATE   : self.__ignore, # there is nowhere to put a date
            TOKEN_NOTE   : self.__location_note, 
            TOKEN_RNOTE  : self.__location_note, 
            TOKEN__LOC   : self.__ignore, 
            TOKEN__NAME  : self.__ignore, 
            TOKEN_PHON   : self.__location_phone, 
            TOKEN_IGNORE : self.__ignore, 
            }
        self.func_list.append(self.parse_loc_tbl)
        
        #
        # Parse table for <<FAM_RECORD>> below the level 0 FAM tag
        # 
        # n @<XREF:FAM>@   FAM                            {1:1}
        #   +1 <<FAMILY_EVENT_STRUCTURE>>                 {0:M}
        #   +1 HUSB @<XREF:INDI>@                         {0:1}
        #   +1 WIFE @<XREF:INDI>@                         {0:1}
        #   +1 CHIL @<XREF:INDI>@                         {0:M}
        #   +1 NCHI <COUNT_OF_CHILDREN>                   {0:1}
        #   +1 SUBM @<XREF:SUBM>@                         {0:M}
        #   +1 <<LDS_SPOUSE_SEALING>>                     {0:M}
        #   +1 <<SOURCE_CITATION>>                        {0:M}
        #   +1 <<MULTIMEDIA_LINK>>                        {0:M}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        self.family_func = {
            # +1 <<FAMILY_EVENT_STRUCTURE>>  {0:M}
            TOKEN_GEVENT : self.__family_std_event, 
            TOKEN_EVEN   : self.__fam_even, 
            # +1 HUSB @<XREF:INDI>@  {0:1}
            TOKEN_HUSB   : self.__family_husb, 
            # +1 WIFE @<XREF:INDI>@  {0:1}
            TOKEN_WIFE   : self.__family_wife, 
            # +1 CHIL @<XREF:INDI>@  {0:M}
            TOKEN_CHIL   : self.__family_chil, 
            # +1 NCHI <COUNT_OF_CHILDREN>  {0:1}
            # +1 SUBM @<XREF:SUBM>@  {0:M}
            # +1 <<LDS_SPOUSE_SEALING>>  {0:M}
            TOKEN_SLGS   : self.__family_slgs, 
            # +1 <<SOURCE_CITATION>>  {0:M}
            TOKEN_SOUR   : self.__family_source, 
            # +1 <<MULTIMEDIA_LINK>>  {0:M}
            TOKEN_OBJE   : self.__family_object, 
            # +1 <<NOTE_STRUCTURE>>  {0:M}
            TOKEN__COMM  : self.__family_comm, 
            TOKEN_NOTE   : self.__family_note, 
            TOKEN_RNOTE  : self.__family_note, 
            # +1 REFN <USER_REFERENCE_NUMBER>  {0:M}
            TOKEN_REFN   : self.__family_cust_attr, 
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE   : self.__family_cust_attr, 
            # +1 RIN <AUTOMATED_RECORD_ID>  {0:1}
            # +1 <<CHANGE_DATE>>  {0:1}
            TOKEN_CHAN   : self.__family_chan, 
            TOKEN_ENDL   : self.__ignore, 
            TOKEN_ADDR   : self.__ignore, 
            TOKEN_RIN    : self.__family_cust_attr, 
            TOKEN_SUBM   : self.__ignore, 
            TOKEN_ATTR   : self.__family_attr, 
            }
        self.func_list.append(self.family_func)

        self.family_rel_tbl = {
            TOKEN__FREL  : self.__family_frel, 
            TOKEN__MREL  : self.__family_mrel, 
            TOKEN_ADOP   : self.__family_adopt, 
            TOKEN__STAT  : self.__family_stat, 
            }
        self.func_list.append(self.family_rel_tbl)

        #
        # Parse table for <<SOURCE_RECORD>> below the level 0 SOUR tag
        # 
        # n @<XREF:SOUR>@ SOUR                            {1:1}
        #   +1 DATA                                       {0:1}
        #     +2 EVEN <EVENTS_RECORDED>                   {0:M}
        #       +3 DATE <DATE_PERIOD>                     {0:1}
        #       +3 PLAC <SOURCE_JURISDICTION_PLACE>       {0:1}
        #     +2 AGNC <RESPONSIBLE_AGENCY>                {0:1}
        #     +2 <<NOTE_STRUCTURE>>                       {0:M}
        #   +1 AUTH <SOURCE_ORIGINATOR>                   {0:1}
        #     +2 [CONT|CONC] <SOURCE_ORIGINATOR>          {0:M}
        #   +1 TITL <SOURCE_DESCRIPTIVE_TITLE>            {0:1}
        #     +2 [CONT|CONC] <SOURCE_DESCRIPTIVE_TITLE>   {0:M}
        #   +1 ABBR <SOURCE_FILED_BY_ENTRY>               {0:1}
        #   +1 PUBL <SOURCE_PUBLICATION_FACTS>            {0:1}
        #     +2 [CONT|CONC] <SOURCE_PUBLICATION_FACTS>   {0:M}
        #   +1 TEXT <TEXT_FROM_SOURCE>                    {0:1}
        #     +2 [CONT|CONC] <TEXT_FROM_SOURCE>           {0:M}
        #   +1 <<SOURCE_REPOSITORY_CITATION>>             {0:1}
        #   +1 <<MULTIMEDIA_LINK>>                        {0:M}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>               {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        self.source_func = {
            TOKEN_TITL   : self.__source_title, 
            TOKEN_TAXT   : self.__source_taxt_peri, 
            TOKEN_PERI   : self.__source_taxt_peri, 
            TOKEN_AUTH   : self.__source_auth, 
            TOKEN_PUBL   : self.__source_publ, 
            TOKEN_NOTE   : self.__source_note, 
            TOKEN_RNOTE  : self.__source_note, 
            TOKEN_TEXT   : self.__source_text, 
            TOKEN_ABBR   : self.__source_abbr, 
            TOKEN_REFN   : self.__source_attr, 
            TOKEN_RIN    : self.__source_attr, 
            TOKEN_REPO   : self.__source_repo, 
            TOKEN_OBJE   : self.__source_object, 
            TOKEN_CHAN   : self.__source_chan, 
            TOKEN_MEDI   : self.__source_attr, 
            TOKEN__NAME  : self.__source_attr, 
            TOKEN_DATA   : self.__ignore, 
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE   : self.__source_attr, 
            TOKEN_CALN   : self.__ignore, 
            # not legal, but Ultimate Family Tree does this
            TOKEN_DATE   : self.__ignore,  
            TOKEN_IGNORE : self.__ignore, 
        }
        self.func_list.append(self.source_func)

        #
        # Parse table for <<MULTIMEDIA_RECORD>> below the level 0 OBJE tag
        # 
        # n @<XREF:OBJE>@ OBJE                            {1:1}
        #   +1 FORM <MULTIMEDIA_FORMAT>                   {1:1}
        #   +1 TITL <DESCRIPTIVE_TITLE>                   {0:1}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 <<SOURCE_CITATION>>                        {0:M}
        #   +1 BLOB                                       {1:1}
        #     +2 CONT <ENCODED_MULTIMEDIA_LINE>           {1:M}
        #   +1 OBJE @<XREF:OBJE>@     /* chain to continued object */  {0:1}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>               {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}

        self.obje_func = {
            TOKEN_FORM   : self.__obje_form, 
            TOKEN_TITL   : self.__obje_title, 
            TOKEN_FILE   : self.__obje_file, 
            TOKEN_NOTE   : self.__obje_note, 
            TOKEN_RNOTE  : self.__obje_note, 
            TOKEN_BLOB   : self.__obje_blob, 
            TOKEN_REFN   : self.__obje_refn, 
            TOKEN_TYPE   : self.__obje_type, 
            TOKEN_RIN    : self.__obje_rin, 
            TOKEN_CHAN   : self.__obje_chan, 
            }
        self.func_list.append(self.obje_func)

        self.parse_addr_tbl = {
            TOKEN_DATE   : self.__address_date, 
            TOKEN_ADR1   : self.__address_adr1, 
            TOKEN_ADR2   : self.__address_adr2, 
            TOKEN_CITY   : self.__address_city, 
            TOKEN_STAE   : self.__address_state, 
            TOKEN_POST   : self.__address_post, 
            TOKEN_CTRY   : self.__address_country, 
            TOKEN_PHON   : self.__ignore, 
            TOKEN_SOUR   : self.__address_sour, 
            TOKEN_NOTE   : self.__address_note, 
            TOKEN_RNOTE  : self.__address_note, 
            TOKEN__LOC   : self.__ignore, 
            TOKEN__NAME  : self.__ignore, 
            TOKEN_IGNORE : self.__ignore, 
            TOKEN_TYPE   : self.__ignore, 
            TOKEN_CAUS   : self.__ignore, 
            }
        self.func_list.append(self.parse_addr_tbl)

        self.event_cause_tbl = {
            TOKEN_SOUR   : self.__event_cause_source, 
            }
        self.func_list.append(self.event_cause_tbl)

        self.event_place_map = {
            TOKEN_NOTE   : self.__event_place_note, 
            TOKEN_RNOTE  : self.__event_place_note, 
            TOKEN_FORM   : self.__event_place_form, 
            # Not legal.
            TOKEN_OBJE   : self.__event_place_object, 
            TOKEN_SOUR   : self.__event_place_sour, 
            TOKEN__LOC   : self.__ignore, 
            TOKEN_MAP    : self.__place_map, 
            # Not legal,  but generated by Ultimate Family Tree
            TOKEN_QUAY   : self.__ignore, 
            }
        self.func_list.append(self.event_place_map)

        self.place_map_tbl = {
            TOKEN_LATI   : self.__place_lati, 
            TOKEN_LONG   : self.__place_long, 
            }
        self.func_list.append(self.place_map_tbl)

        self.repo_ref_tbl = {
            TOKEN_CALN   : self.__repo_ref_call, 
            TOKEN_NOTE   : self.__repo_ref_note, 
            TOKEN_RNOTE  : self.__repo_ref_note, 
            TOKEN_MEDI   : self.__repo_ref_medi, 
            TOKEN_IGNORE : self.__ignore, 
            }
        self.func_list.append(self.repo_ref_tbl)

        self.parse_person_adopt = {
            TOKEN_ADOP   : self.__person_adopt_famc_adopt, 
            }
        self.func_list.append(self.parse_person_adopt)

        self.opt_note_tbl = {
            TOKEN_RNOTE  : self.__optional_note, 
            TOKEN_NOTE   : self.__optional_note, 
            }
        self.func_list.append(self.opt_note_tbl)

        self.citation_data_tbl = {
            TOKEN_DATE   : self.__citation_data_date, 
            TOKEN_TEXT   : self.__citation_data_text,
            TOKEN_RNOTE  : self.__citation_data_note, 
            TOKEN_NOTE   : self.__citation_data_note, 
            }
        self.func_list.append(self.citation_data_tbl)

        self.citation_even_tbl = {
            TOKEN_ROLE   : self.__citation_even_role,
            }
        self.func_list.append(self.citation_even_tbl)
        
        #
        # Parse table for <<HEADER>> record below the level 0 HEAD tag
        # 
        # n HEAD                                          {1:1}
        #   +1 SOUR <APPROVED_SYSTEM_ID>                  {1:1}
        #     +2 VERS <VERSION_NUMBER>                    {0:1}
        #     +2 NAME <NAME_OF_PRODUCT>                   {0:1}
        #     +2 CORP <NAME_OF_BUSINESS>                  {0:1}
        #       +3 <<ADDRESS_STRUCTURE>>                  {0:1}
        #     +2 DATA <NAME_OF_SOURCE_DATA>               {0:1}
        #       +3 DATE <PUBLICATION_DATE>                {0:1}
        #       +3 COPR <COPYRIGHT_SOURCE_DATA>           {0:1}
        #   +1 DEST <RECEIVING_SYSTEM_NAME>               {0:1*}
        #   +1 DATE <TRANSMISSION_DATE>                   {0:1}
        #     +2 TIME <TIME_VALUE>                        {0:1}
        #   +1 SUBM @<XREF:SUBM>@                         {1:1}
        #   +1 SUBN @<XREF:SUBN>@                         {0:1}
        #   +1 FILE <FILE_NAME>                           {0:1}
        #   +1 COPR <COPYRIGHT_GEDCOM_FILE>               {0:1}
        #   +1 GEDC                                       {1:1}
        #     +2 VERS <VERSION_NUMBER>                    {1:1}
        #     +2 FORM <GEDCOM_FORM>                       {1:1}
        #   +1 CHAR <CHARACTER_SET>                       {1:1}
        #     +2 VERS <VERSION_NUMBER>                    {0:1}
        #   +1 LANG <LANGUAGE_OF_TEXT>                    {0:1}
        #   +1 PLAC                                       {0:1}
        #     +2 FORM <PLACE_HIERARCHY>                   {1:1}
        #   +1 NOTE <GEDCOM_CONTENT_DESCRIPTION>          {0:1}
        #     +2 [CONT|CONC] <GEDCOM_CONTENT_DESCRIPTION> {0:M}

        #  * NOTE: Submissions to the Family History Department for Ancestral
        #  File submission or for clearing temple ordinances must use a
        #  DESTination of ANSTFILE or TempleReady.
        
        self.head_parse_tbl = {
            TOKEN_SOUR   : self.__header_sour, 
            TOKEN_NAME   : self.__header_sour_name, # This should be below SOUR
            TOKEN_VERS   : self.__header_sour_vers, # This should be below SOUR
            TOKEN_FILE   : self.__header_file, 
            TOKEN_COPR   : self.__header_copr, 
            TOKEN_SUBM   : self.__header_subm, 
            TOKEN_CORP   : self.__ignore,           # This should be below SOUR
            TOKEN_DATA   : self.__ignore,       # This should be below SOUR
            TOKEN_SUBN   : self.__header_subn, 
            TOKEN_LANG   : self.__header_lang, 
            TOKEN_TIME   : self.__ignore,       # This should be below DATE 
            TOKEN_DEST   : self.__header_dest, 
            TOKEN_CHAR   : self.__header_char, 
            TOKEN_GEDC   : self.__header_gedc, 
            TOKEN__SCHEMA: self.__ignore, 
            TOKEN_PLAC   : self.__header_plac, 
            TOKEN_DATE   : self.__header_date, 
            TOKEN_NOTE   : self.__header_note, 
            }
        self.func_list.append(self.head_parse_tbl)

        self.header_sour_parse_tbl = {
            TOKEN_VERS   : self.__header_sour_vers,
            TOKEN_NAME   : self.__header_sour_name, 
            TOKEN_CORP   : self.__header_sour_corp,
            TOKEN_DATA   : self.__header_sour_data,
            }
        self.func_list.append(self.header_sour_parse_tbl)

        self.header_sour_data = {
            TOKEN_DATE   : self.__header_sour_date, 
            TOKEN_COPR   : self.__header_sour_copr, 
            }
        self.func_list.append(self.header_sour_data)

        self.header_corp_addr = {
            TOKEN_ADDR   : self.__repo_addr, 
            TOKEN_PHON   : self.__repo_phon, 
            }
        self.func_list.append(self.header_corp_addr)

        self.header_subm = {
            TOKEN_NAME   : self.__header_subm_name, 
            }
        self.func_list.append(self.header_subm)

        self.place_form = {
            TOKEN_FORM   : self.__place_form, 
            }
        self.func_list.append(self.place_form)

        #
        # Parse table for <<NOTE_RECORD>> below the level 0 NOTE tag
        # 
        # n @<XREF:NOTE>@ NOTE <SUBMITTER_TEXT>           {1:1}
        #   +1 [ CONC | CONT] <SUBMITTER_TEXT>            {0:M}
        #   +1 <<SOURCE_CITATION>>                        {0:M}
        #   +1 REFN <USER_REFERENCE_NUMBER>               {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>               {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        self.note_parse_tbl = {
            TOKEN_SOUR   : self.__ignore, 
            TOKEN_REFN   : self.__ignore, 
            TOKEN_RIN    : self.__ignore, 
            TOKEN_CHAN   : self.__note_chan, 
            }
        self.func_list.append(self.note_parse_tbl)

        # look for existing place titles, build a map 
        self.place_names = defaultdict(list)
        cursor = dbase.get_place_cursor()
        data = cursor.next()
        while data:
            (handle, val) = data
            self.place_names[val[2]].append(handle)
            data = cursor.next()
        cursor.close()

        enc = stage_one.get_encoding()

        if enc == "ANSEL":
            rdr = AnselReader(ifile)
        elif enc in ("UTF-8", "UTF8"):
            rdr = UTF8Reader(ifile)
        elif enc in ("UTF-16", "UTF16", "UNICODE"):
            rdr = UTF16Reader(ifile)
        else:
            rdr = AnsiReader(ifile)

        self.lexer = Lexer(rdr)
        self.filename = filename
        self.backoff = False

        fullpath = os.path.normpath(os.path.abspath(filename))
        self.geddir = os.path.dirname(fullpath)
    
        self.error_count = 0
        amap = PERSONALCONSTANTATTRIBUTES
        
        self.attrs = amap.values()
        self.gedattr = dict([key, val] for val, key in amap.iteritems())
        self.search_paths = []

    def parse_gedcom_file(self, use_trans=False):
        """
        Parses the opened GEDCOM file.
        
        LINEAGE_LINKED_GEDCOM: =
          0 <<HEADER>>                                    {1:1}
          0 <<SUBMISSION_RECORD>>                         {0:1}
          0 <<RECORD>>                                    {1:M}
          0 TRLR                                          {1:1}

        """
        no_magic = self.maxpeople < 1000
        with DbTxn(_("GEDCOM import"), self.dbase, not use_trans,
                   no_magic=no_magic) as self.trans:

            self.dbase.disable_signals()
            self.__parse_header_head()
            self.want_parse_warnings = False
            self.__parse_header()
            self.want_parse_warnings = True
            if self.use_def_src:
                self.dbase.add_source(self.def_src, self.trans)
            self.__parse_record()
            self.__parse_trailer()
            for title, handle in self.inline_srcs.iteritems():
                src = gen.lib.Source()
                src.set_handle(handle)
                src.set_title(title)
                self.dbase.add_source(src, self.trans)
            self.__clean_up()
            
        self.__check_xref()
        self.dbase.enable_signals()
        self.dbase.request_rebuild()
        if self.number_of_errors == 0:
            message  = _("GEDCOM import report: No errors detected")
        else:
            message = _("GEDCOM import report: %s errors detected") % \
                self.number_of_errors
        InfoDialog(message, "".join(self.errors), monospaced=True)

    def __clean_up(self):
        """
        Break circular references to parsing methods stored in dictionaries
        to aid garbage collection
        """
        for func_map in self.func_list:
            for key in func_map.keys():
                del func_map[key]
            del func_map
        del self.func_list
        del self.update
        self.lexer.clean_up()
        
    def __find_person_handle(self, gramps_id):
        """
        Return the database handle associated with the person's GRAMPS ID
        """
        return self.__find_from_handle(gramps_id, self.gid2id)

    def __find_family_handle(self, gramps_id):
        """
        Return the database handle associated with the family's GRAMPS ID
        """
        return self.__find_from_handle(gramps_id, self.fid2id)
        
    def __find_object_handle(self, gramps_id):
        """
        Return the database handle associated with the media object's GRAMPS ID
        """
        return self.__find_from_handle(gramps_id, self.oid2id)

    def __find_note_handle(self, gramps_id):
        """
        Return the database handle associated with the media object's GRAMPS ID
        """
        return self.__find_from_handle(gramps_id, self.nid2id)

    def __find_or_create_person(self, gramps_id):
        """
        Finds or creates a person based on the GRAMPS ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new person, assign the handle and GRAMPS ID.
        """
        person = gen.lib.Person()
        intid = self.gid2id.get(gramps_id)
        if self.dbase.has_person_handle(intid):
            person.unserialize(self.dbase.get_raw_person_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.gid2id)
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)
        return person

    def __find_or_create_family(self, gramps_id):
        """
        Finds or creates a family based on the GRAMPS ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new family, assign the handle and GRAMPS ID.
        """
        family = gen.lib.Family()
        # Add a counter for reordering the children later:
        family.child_ref_count = 0
        intid = self.fid2id.get(gramps_id)
        if self.dbase.has_family_handle(intid):
            family.unserialize(self.dbase.get_raw_family_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.fid2id)
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)
        return family

    def __find_or_create_object(self, gramps_id):
        """
        Finds or creates a media object based on the GRAMPS ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new media object, assign the handle and GRAMPS ID.
        """
        obj = gen.lib.MediaObject()
        intid = self.oid2id.get(gramps_id)
        if self.dbase.has_object_handle(intid):
            obj.unserialize(self.dbase.get_raw_object_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.oid2id)
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
        return obj

    def __find_or_create_source(self, gramps_id):
        """
        Find or create a source based on the GRAMPS ID. 
        
        If the ID is already used (is in the db), we return the item in the 
        db. Otherwise, we create a new source, assign the handle and GRAMPS ID.
        
        """
        obj = gen.lib.Source()
        intid = self.sid2id.get(gramps_id)
        if self.dbase.has_source_handle(intid):
            obj.unserialize(self.dbase.get_raw_source_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.sid2id)
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
        return obj

    def __find_or_create_repository(self, gramps_id):
        """
        Finds or creates a repository based on the GRAMPS ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new repository, assign the handle and GRAMPS ID.

        Some GEDCOM "flavors" destroy the specification, and declare the 
        repository inline instead of in a object. 
        """
        repository = gen.lib.Repository()
        intid = self.rid2id.get(gramps_id)
        if self.dbase.has_repository_handle(intid):
            repository.unserialize(self.dbase.get_raw_repository_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.rid2id)
            repository.set_handle(intid)
            repository.set_gramps_id(gramps_id)
        return repository

    def __find_or_create_note(self, gramps_id):
        """
        Finds or creates a repository based on the GRAMPS ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new repository, assign the handle and GRAMPS ID.

        Some GEDCOM "flavors" destroy the specification, and declare the 
        repository inline instead of in a object. 
        """
        note = gen.lib.Note()
        if not gramps_id:
            need_commit = True
            gramps_id = self.dbase.find_next_note_gramps_id()
        else:
            need_commit = False

        intid = self.nid2id.get(gramps_id)
        if self.dbase.has_note_handle(intid):
            note.unserialize(self.dbase.get_raw_note_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.nid2id)
            note.set_handle(intid)
            note.set_gramps_id(gramps_id)
        if need_commit:
            self.dbase.add_note(note, self.trans)
        return note

    def __loc_is_empty(self, location):
        """
        Determines whether a location is empty.
        
        @param location: The current location
        @type location: gen.lib.Location
        @return True of False
        """
        if location is None:
            return True
        elif location.serialize() == self._EMPTY_LOC:
            return True
        elif location.is_empty():
            return True
        return False
    
    def __find_place(self, title, location):
        """
        Finds an existing place based on the title and primary location.
        
        @param title: The place title
        @type title: string
        @param location: The current location
        @type location: gen.lib.Location
        @return gen.lib.Place
        """
        for place_handle in self.place_names[title]:
            place = self.dbase.get_place_from_handle(place_handle)
            if place.get_title() == title:
                if self.__loc_is_empty(location) and \
                   self.__loc_is_empty(place.get_main_location()):
                    return place
                elif (not self.__loc_is_empty(location) and \
                      not self.__loc_is_empty(place.get_main_location()) and
                      place.get_main_location().is_equivalent(location) == IDENTICAL):
                    return place
        return None

    def __create_place(self, title, location):
        """
        Create a new place based on the title and primary location.
        
        @param title: The place title
        @type title: string
        @param location: The current location
        @type location: gen.lib.Location
        @return gen.lib.Place
        """
        place = gen.lib.Place()
        place.set_title(title)
        place.set_main_location(location)
        self.dbase.add_place(place, self.trans)
        self.place_names[title].append(place.get_handle())
        return place

    def __find_file(self, fullname, altpath):
        tries = []
        fullname = fullname.replace('\\', os.path.sep)
        tries.append(fullname)
        
        try:
            if os.path.isfile(fullname):
                return (1, fullname)
        except UnicodeEncodeError:
            # FIXME: problem possibly caused by umlaut/accented character 
            # in filename
            return (0, tries)
        other = os.path.join(altpath, fullname)
        tries.append(other)
        if os.path.isfile(other):
            return (1, other)
        other = os.path.join(altpath, os.path.basename(fullname))
        tries.append(other)
        if os.path.isfile(other):
            return (1, other)
        if len(fullname) > 3:
            if fullname[1] == ':':
                fullname = fullname[2:]
                for path in self.search_paths:
                    other = os.path.normpath("%s/%s" % (path, fullname))
                    tries.append(other)
                    if os.path.isfile(other):
                        return (1, other)
            return (0, tries)
        else:
            return (0, tries)

    def __get_next_line(self):
        """
        Get the next line for analysis from the lexical analyzer. Return the
        same value if the _backup flag is set.
        """
        if not self.backoff:
            self.groups = self.lexer.readline()
            self.update()
            
            # EOF ?
            if not self.groups:
                self.backoff = False
                # We will add the truncation warning message to the error
                # messages report, even though it probably won't be reported
                # because the exception below gets raised before the report is
                # produced. We do this in case __add_msg is changed in the
                # future to do something else
                self.__add_msg(self.__TRUNC_MSG)
                self.groups = None
                raise Errors.GedcomError(self.__TRUNC_MSG)

        self.backoff = False
        return self.groups
            
    def __undefined(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__not_recognized(line, state.level+1, state)

    def __ignore(self, line, state):
        """
        Ignores an unsupported tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("Tag recognised but not supported"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __not_recognized(self, line, level, state):
        """
        Prints a message when an undefined token is found. All subordinate items
        to the current item are ignored.

        @param level: Current level in the file
        @type level: int
        """
        self.__add_msg(_("Line ignored as not understood"), line, state)
        self.__skip_subordinate_levels(level, state)

    def __skip_record(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__skip_subordinate_levels(2, state)

    def __skip_subordinate_levels(self, level, state):
        """
        Skip add lines of the specified level or lower.
        """
        skips = 0
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, level):
                if skips:
                    # This improves formatting when there are long sequences of
                    # skipped lines
                    self.__add_msg("", None, None)
                return
            self.__add_msg(_("Skipped subordinate line"), line, state)
            skips += 1
    
    def __level_is_finished(self, text, level):
        """
        Check to see if the level has been completed, indicated by finding
        a level indiciated by the passed level value. If the level is finished, 
        then make sure to call self._backup to reset the text pointer.
        """
        done = text.level < level
        if done:
            self._backup()
        return done

    def __add_msg(self, problem, line=None, state=None):
        if problem != "":
            self.number_of_errors += 1
        if line:
            prob_width = 66
            problem = problem.ljust(prob_width)[0:(prob_width-1)]
            text = str(line.data).replace("\n", "\n".ljust(prob_width + 22))
            message = "%s   Line %5d: %s %s %s\n" % (problem, line.line,
                                                       line.level, 
                                                       line.token_text,
                                                       text)
        else:
            message = problem + "\n"
        if state:
            state.msg += message
        self.errors.append(message)

    def __check_msgs(self, record_name, state, obj):
        if state.msg == "":
            return
        message = _("Records not imported into ") + record_name + ":\n\n" + \
                    state.msg
        new_note = gen.lib.Note()
        tag = StyledTextTag(StyledTextTagType.FONTFACE, 'Monospace', 
                            [(0, len(message))])
        text = StyledText(message, [tag])
        new_note.set_styledtext(text)
        new_note.set_handle(Utils.create_id())
        note_type = gen.lib.NoteType()
        note_type.set((gen.lib.NoteType.CUSTOM, _("GEDCOM import")))
        new_note.set_type(note_type)
        self.dbase.add_note(new_note, self.trans)
        # If possible, attach the note to the relevant object
        if obj:
            obj.add_note(new_note.get_handle())

    def _backup(self):
        """
        Set the _backup flag so that the current line can be accessed by the
        next level up.
        """
        self.backoff = True

    def __check_xref(self):

        def __check(map, trans, class_func, commit_func, gramps_id2handle, msg):
            for input_id, gramps_id in map.map().iteritems():
                # Check whether an object exists for the mapped gramps_id
                if not trans.get(str(gramps_id)):
                    handle = self.__find_from_handle(gramps_id, 
                                                     gramps_id2handle)
                    if msg == "FAM":
                        Utils.make_unknown(gramps_id, self.explanation.handle, 
                                           class_func, commit_func, self.trans,
                                           db=self.dbase)
                        self.__add_msg(_("Error: %(msg)s  '%(gramps_id)s'"
                                         " (input as @%(xref)s@) not in input"
                                         " GEDCOM. Record synthesised") %
                                         {'msg' : msg, 'gramps_id' : gramps_id,
                                          'xref' : input_id})
                    else:
                        Utils.make_unknown(gramps_id, self.explanation.handle, 
                                           class_func, commit_func, self.trans)
                        self.missing_references +=1
                        self.__add_msg(_("Error: %(msg)s '%(gramps_id)s'"
                                         " (input as @%(xref)s@) not in input"
                                         " GEDCOM. Record with typifying"
                                         " attribute 'Unknown' created") %
                                         {'msg' : msg, 'gramps_id' : gramps_id,
                                          'xref' : input_id})
    
        self.explanation = Utils.create_explanation_note(self.dbase)

        self.missing_references = 0
        previous_errors = self.number_of_errors
        __check(self.pid_map, self.dbase.id_trans, self.__find_or_create_person,
                self.dbase.commit_person, self.gid2id, "INDI")
        __check(self.fid_map, self.dbase.fid_trans, self.__find_or_create_family,
                self.dbase.commit_family, self.fid2id, "FAM")
        __check(self.sid_map, self.dbase.sid_trans, self.__find_or_create_source,
                self.dbase.commit_source, self.sid2id, "SOUR")
        __check(self.oid_map, self.dbase.oid_trans, self.__find_or_create_object,
                self.dbase.commit_media_object, self.oid2id, "OBJE")
        __check(self.rid_map, self.dbase.rid_trans, self.__find_or_create_repository,
                self.dbase.commit_repository, self.rid2id, "REPO")
        __check(self.nid_map, self.dbase.nid_trans, self.__find_or_create_note,
                self.dbase.commit_note, self.nid2id, "NOTE")

        # Check persons membership in referenced families
        def __input_fid(gramps_id):
            for (k,v) in self.fid_map.map().iteritems():
                if v == gramps_id:
                    return k
        
        for input_id, gramps_id in self.pid_map.map().iteritems():
            person_handle = self.__find_from_handle(gramps_id, self.gid2id)
            person = self.dbase.get_person_from_handle(person_handle)
            for family_handle in person.get_family_handle_list():
                family = self.dbase.get_family_from_handle(family_handle)
                if family and family.get_father_handle() != person_handle and \
                       family.get_mother_handle() != person_handle:
                    person.remove_family_handle(family_handle)
                    self.dbase.commit_person(person, self.trans)
                    self.__add_msg(_("Error: family '%(family)s' (input as"
                                     " @%(orig_family)s@) person %(person)s"
                                     " (input as %(orig_person)s) is not a"
                                     " member of the referenced family."
                                     " Family reference removed from person") %
                                     {'family' : family.gramps_id, 
                                      'orig_family' : 
                                            __input_fid(family.gramps_id),
                                      'person' : person.gramps_id,
                                      'orig_person' : input_id})
                        
        def __input_pid(gramps_id):
            for (k,v) in self.pid_map.map().iteritems():
                if v == gramps_id:
                    return k
        
        for input_id, gramps_id in self.fid_map.map().iteritems():
            family_handle = self.__find_from_handle(gramps_id, self.fid2id)
            family = self.dbase.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
                        
            if father_handle:
                father = self.dbase.get_person_from_handle(father_handle)
                if father and \
                    family_handle not in father.get_family_handle_list():
                    father.add_family_handle(family_handle)
                    self.dbase.commit_person(father, self.trans)
                    self.__add_msg("Error: family '%(family)s' (input as"
                                   " @%(orig_family)s@) father '%(father)s'"
                                   " (input as '%(orig_father)s') does not refer"
                                   " back to the family. Reference added." % 
                                   {'family' : family.gramps_id, 
                                    'orig_family' : input_id, 
                                    'father' : father.gramps_id,
                                    'orig_father' : 
                                            __input_pid(father.gramps_id)})

            if mother_handle:
                mother = self.dbase.get_person_from_handle(mother_handle)
                if mother and \
                    family_handle not in mother.get_family_handle_list():
                    mother.add_family_handle(family_handle)
                    self.dbase.commit_person(mother, self.trans)
                    self.__add_msg("Error: family '%(family)s' (input as"
                                   " @%(orig_family)s@) mother '%(mother)s'"
                                   " (input as '%(orig_mother)s') does not refer"
                                   " back to the family. Reference added." % 
                                   {'family' : family.gramps_id, 
                                    'orig_family' : input_id, 
                                    'mother' : mother.gramps_id,
                                    'orig_mother' : 
                                            __input_pid(mother.gramps_id)})

            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.dbase.get_person_from_handle(child_handle)
                if child:
                    if family_handle not in \
                        child.get_parent_family_handle_list():
                        # The referenced child has no reference to the family.
                        # There was a link from the FAM record to the child, but
                        # no FAMC link from the child to the FAM.
                        child.add_parent_family_handle(family_handle)
                        self.dbase.commit_person(child, self.trans)
                        self.__add_msg("Error: family '%(family)s' (input as"
                                       " @%(orig_family)s@) child '%(child)s'"
                                       " (input as '%(orig_child)s') does not "
                                       "refer back to the family. "
                                       "Reference added." % 
                                       {'family' : family.gramps_id, 
                                        'orig_family' : input_id, 
                                        'child' : child.gramps_id,
                                        'orig_child' : 
                                                __input_pid(child.gramps_id)})

        if self.missing_references:
            self.dbase.commit_note(self.explanation, self.trans, time.time())
            txt = _("\nThe imported file was not self-contained.\n"
                     "To correct for that, %d objects were created and\n"
                     "their typifying attribute was set to 'Unknown'.\n"
                     "Where possible these 'Unkown' objects are \n"
                     "referenced by note %s.\n"
                     ) % (self.missing_references, self.explanation.gramps_id)
            self.__add_msg(txt)
            self.number_of_errors -= 1
            
    def __merge_address(self, free_form_address, addr, line, state):
        """
        Merge freeform and structured addrssses.
        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}
        
        This is done along the lines suggested by Tamura Jones in
        http://www.tamurajones.net/GEDCOMADDR.xhtml as a result of bug 6382.
        "When a GEDCOM reader encounters a double address, it should read the
        structured address. ... A GEDCOM reader that does verify that the
        addresses are the same should issue an error if they are not".
        
        This is called for SUBMitter addresses (__subm_addr), INDIvidual
        addresses (__person_addr), REPO addresses and HEADer corp address
        (__repo_address) and EVENt addresses (__event_adr).
        
        The structured address (if any) will have been accumulated into an
        object of type LocationBase, which will either be a Location, or an
        Address object.
        
        If ADDR is provided, but none of ADR1, ADR2, CITY, STAE, or POST (not
        CTRY), then Street is set to the freeform address. N.B. this is a change
        for Repository addresses and HEADer Corp address where previously the
        free-form address was deconstrucated into different structured
        components. N.B. PAF provides a free-form address and a country, so this
        allows for that case.
        
        If both forms of address are provided, then the structured address is
        used, and if the ADDR/CONT contains anything not in the structured
        address, a warning is issued.
        
        If just ADR1, ADR2, CITY, STAE, POST or CTRY are provided (this is not
        actually legal GEDCOM symtax, but may be possible by GEDCOM extensions)
        then just the structrued address is used.
        """
        if not (addr.get_street() or addr.get_locality() or
                addr.get_city() or addr.get_state() or
                addr.get_postal_code()):
            
            addr.set_street(free_form_address)
        else:
            # structured address provided
            addr_list = free_form_address.split("\n")
            str_list = []
            for func in (addr.get_street(), addr.get_locality(),
                         addr.get_city(), addr.get_state(),
                         addr.get_postal_code(), addr.get_country()):
                str_list += [i.strip(',' + string.whitespace) for i in func.split("\n")]
            for elmn in addr_list:
                if elmn.strip(',' + string.whitespace) not in str_list:
                    # message means that the element %s was ignored, but
                    # expressed the wrong way round because the message is
                    # truncated for output
                    self.__add_msg(_("ADDR element ignored '%s'"
                                     % elmn), line, state)
            # The free-form address ADDR is discarded

    def __parse_trailer(self):
        """
        Looks for the expected TRLR token
        """
        try:
            line = self.__get_next_line()
            if line and line.token != TOKEN_TRLR:
                state = CurrentState()
                self.__not_recognized(line, 0, state)
                self.__check_msgs(_("TRLR (trailer)"), state, None)
        except TypeError:
            return
        
    def __parse_submitter(self, line):
        """
        Parses the submitter data

        n @<XREF:SUBM>@ SUBM
          +1 NAME <SUBMITTER_NAME>
          +1 <<ADDRESS_STRUCTURE>>
          +1 <<MULTIMEDIA_LINK>>
          +1 LANG <LANGUAGE_PREFERENCE>
          +1 RFN <SUBMITTER_REGISTERED_RFN>
          +1 RIN <AUTOMATED_RECORD_ID>
          +1 <<CHANGE_DATE>>
        """
        researcher = gen.lib.Researcher()
        state = CurrentState()
        state.res = researcher
        state.level = 1
        repo = gen.lib.Repository()
        state.repo = repo
        self.__parse_level(state, self.subm_parse_tbl, self.__undefined)
        # If this is the submitter that we were told about in the HEADer, then 
        # we will need to update the researcher
        if line.token_text == self.subm and self.import_researcher:
            self.dbase.set_researcher(state.res)
        
        if state.res.get_name() == "":
            submitter_name = _("SUBM (Submitter): @%s@") % line.token_text
        else:
            submitter_name = _("SUBM (Submitter): %s") % state.res.get_name()
        if self.use_def_src:
            repo.set_name(submitter_name)
            repo.set_handle(Utils.create_id())
            repo.set_gramps_id(self.dbase.find_next_repository_gramps_id())
            
            addr = gen.lib.Address()
            addr.set_street(state.res.get_address())
            addr.set_locality(state.res.get_locality())
            addr.set_city(state.res.get_city())
            addr.set_state(state.res.get_state())
            addr.set_country(state.res.get_country())
            addr.set_postal_code(state.res.get_postal_code())
            addr.set_county(state.res.get_county())
            addr.set_phone(state.res.get_phone())
            repo.add_address(addr)
            
            if state.res.get_email():
                url = gen.lib.Url()
                url.set_path(state.res.get_email())
                url.set_type(gen.lib.UrlType(gen.lib.UrlType.EMAIL))
                repo.add_url(url)
            
            rtype = gen.lib.RepositoryType()
            rtype.set((gen.lib.RepositoryType.CUSTOM, _('GEDCOM data')))
            repo.set_type(rtype)
            self.__check_msgs(submitter_name, state, repo)
            self.dbase.commit_repository(repo, self.trans, state.repo.change)
            repo_ref = gen.lib.RepoRef()
            repo_ref.set_reference_handle(repo.handle)
            mtype = gen.lib.SourceMediaType()
            mtype.set((gen.lib.SourceMediaType.UNKNOWN, ''))
            repo_ref.set_media_type(mtype)
            self.def_src.add_repo_reference(repo_ref)
            self.dbase.commit_source(self.def_src, self.trans)
        else:
            self.__check_msgs(submitter_name, state, None)
        

    def __parse_record(self):
        """
        Parse the top level (0 level) instances.
        RECORD: =
          [
          n <<FAM_RECORD>>                                {1:1}
          |
          n <<INDIVIDUAL_RECORD>>                         {1:1}
          |
          n <<MULTIMEDIA_RECORD>>                         {1:M}
          |
          n <<NOTE_RECORD>>                               {1:1}
          |
          n <<REPOSITORY_RECORD>>                         {1:1}
          |
          n <<SOURCE_RECORD>>                             {1:1}
          |
          n <<SUBMITTER_RECORD>>                          {1:1}
          ] 
        
        This also deals with the SUBN (submission) record, of which there should
        be exactly one.
        """
        while True:
            line = self.__get_next_line()
            key = line.data
            if not line or line.token == TOKEN_TRLR:
                self._backup()
                break
            if line.token == TOKEN_UNKNOWN:
                state = CurrentState()
                self.__add_msg(_("Unknown tag"), line, state)
                self.__skip_subordinate_levels(1, state)
                self.__check_msgs(_("Top Level"), state, None)
            elif key in ("FAM", "FAMILY"):
                self.__parse_fam(line)
            elif key in ("INDI", "INDIVIDUAL"):
                self.__parse_indi(line)
            elif key in ("OBJE", "OBJECT"):
                self.__parse_obje(line)
            elif key in ("REPO", "REPOSITORY"):
                self.__parse_repo(line)
            elif key in ("SUBM", "SUBMITTER"):
                self.__parse_submitter(line)
            elif key in ("SUBN"):
                state = CurrentState()
                self.__parse_submission(line, state)
                self.__check_msgs(_("Top Level"), state, None)
            elif line.token in (TOKEN_SUBM, TOKEN_SUBN, TOKEN_IGNORE):
                state = CurrentState()
                self.__skip_subordinate_levels(1, state)
                self.__check_msgs(_("Top Level"), state, None)
            elif key in ("SOUR", "SOURCE"):
                self.__parse_source(line.token_text, 1)
            elif (line.data.startswith("SOUR ") or
                  line.data.startswith("SOURCE ")):
                # A source formatted in a single line, for example:
                # 0 @S62@ SOUR This is the title of the source
                source = self.__find_or_create_source(self.sid_map[line.data])
                source.set_title(line.data[5:])
                self.dbase.commit_source(source, self.trans)
            elif key[0:4] == "NOTE":
                try:
                    line.data = line.data[5:]
                except:
                    # don't think this path is ever taken, but if it is..
                    # ensure a message is emitted & subordinates skipped
                    line.data = None
                self.__parse_inline_note(line, 1)
            else:
                state = CurrentState()
                self.__not_recognized(line, 1, state)
                self.__check_msgs(_("Top Level"), state, None)
        
    def __parse_level(self, state, __map, default):
        """
        Loop trough the current GEDCOM level, calling the appropriate 
        functions associated with the TOKEN. 
        
        If no matching function for the token is found, the default function 
        is called instead.
        
        """
        while True:
            line = self.__get_next_line()
            if line.level < state.level:
                self.backoff = True
                return
            else:
                func = __map.get(line.token, default)
                func(line, state)

    #----------------------------------------------------------------------
    #
    # INDI parsing
    #
    #----------------------------------------------------------------------

    def __parse_indi(self, line):
        """
        Handling of the GEDCOM INDI tag and all lines subordinate to the current
        line.

        n  @XREF:INDI@ INDI {1:1}
          +1 RESN <RESTRICTION_NOTICE> {0:1}
          +1 <<PERSONAL_NAME_STRUCTURE>> {0:M}
          +1 SEX <SEX_VALUE> {0:1}
          +1 <<INDIVIDUAL_EVENT_STRUCTURE>> {0:M}
          +1 <<INDIVIDUAL_ATTRIBUTE_STRUCTURE>> {0:M}
          +1 <<LDS_INDIVIDUAL_ORDINANCE>> {0:M}
          +1 <<CHILD_TO_FAMILY_LINK>> {0:M}
          +1 <<SPOUSE_TO_FAMILY_LINK>> {0:M}
          +1 SUBM @<XREF:SUBM>@ {0:M}
          +1 <<ASSOCIATION_STRUCTURE>> {0:M}
          +1 ALIA @<XREF:INDI>@ {0:M}
          +1 ANCI @<XREF:SUBM>@ {0:M}
          +1 DESI @<XREF:SUBM>@ {0:M}
          +1 <<SOURCE_CITATION>> {0:M}
          +1 <<MULTIMEDIA_LINK>> {0:M}
          +1 <<NOTE_STRUCTURE>> {0:M} 
          +1 RFN <PERMANENT_RECORD_FILE_NUMBER> {0:1}
          +1 AFN <ANCESTRAL_FILE_NUMBER> {0:1}
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
          +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<CHANGE_DATE>> {0:1}
        """

        # find the person
        real_id = self.pid_map[line.token_text]
        person = self.__find_or_create_person(real_id)

        # set up the state for the parsing
        state = CurrentState(person=person, level=1)

        # do the actual parsing
        self.__parse_level(state, self.indi_parse_tbl, self.__person_event)

        # Add the default reference if no source has found
        self.__add_default_source(person)

        self.__check_msgs(_("INDI (individual) Gramps ID %s") % 
                          person.get_gramps_id(), state, person)
        # commit the person to the database
        self.dbase.commit_person(person, self.trans, state.person.change)

    def __person_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        citation_handle = self.handle_source(line, state.level, state)
        state.person.add_citation(citation_handle)

    def __person_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type((gen.lib.AttributeType.CUSTOM, line.token_text))
        attr.set_value(line.data)
        state.person.add_attribute(attr)

    def __person_event(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # We can get here when a tag that is not valid in the indi_parse_tbl
        # parse table is encountered. It is remotely possible that this is
        # actally a DATE tag, in which case line.data will be a date object, so
        # we need to convert it back to a string here.
        event_ref = self.__build_event_pair(state, gen.lib.EventType.CUSTOM, 
                                            self.event_parse_tbl, 
                                            str(line.data))
        state.person.add_event_ref(event_ref)

    def __fam_even(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_family_event_pair(state, 
                                                   gen.lib.EventType.CUSTOM, 
                                                   self.event_parse_tbl, 
                                                   line.data)
        state.family.add_event_ref(event_ref)

    def __person_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.person, state.level+1, state)
        
    def __person_resn(self, line, state):
        """
        Parses the RESN tag, adding it as an attribute.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type((gen.lib.AttributeType.CUSTOM, 'RESN'))
        state.person.add_attribute(attr)

    def __person_alt_name(self, line, state):
        """
        This parses the standard GEDCOM structure:
        
        n  @XREF:INDI@ INDI {1:1}
          +1 ALIA @<XREF:INDI>@ {0:M}
          
        The ALIA tag is supposed to cross reference another person. We will
        store this in the Association record.
        
        ALIA {ALIAS}: = An indicator to link different record descriptions of a
        person who may be the same person.
        
        Some systems use the ALIA tag as an alternate NAME tag, which is not
        legal in GEDCOM, but oddly enough, is easy to support. This parses the
        illegal (ALIA or ALIAS) or non-standard (_ALIA) GEDCOM. "1 ALIA" is used
        by Family Tree Maker and Reunion. "1 ALIAS" and "1 _ALIA" do not appear
        to be used.
        
        n  @XREF:INDI@ INDI                        {1:1}
          +1  <ALIA> <NAME_PERSONAL>               {1:1}
            +2 NPFX <NAME_PIECE_PREFIX>            {0:1}
            +2 GIVN <NAME_PIECE_GIVEN>             {0:1}
            +2 NICK <NAME_PIECE_NICKNAME>          {0:1}
            +2 SPFX <NAME_PIECE_SURNAME_PREFIX>    {0:1}
            +2 SURN <NAME_PIECE_SURNAME>           {0:1}
            +2 NSFX <NAME_PIECE_SUFFIX>            {0:1}
            +2 <<SOURCE_CITATION>>                 {0:M}
              +3 <<NOTE_STRUCTURE>>                {0:M}
              +3 <<MULTIMEDIA_LINK>>               {0:M}
            +2 <<NOTE_STRUCTURE>>                  {0:M}
        where <ALIA> == ALIA | _ALIA | ALIAS
        
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data == '':
            self.__add_msg(_("Empty Alias <NAME PERSONAL> ignored"), line, state)
            self.__skip_subordinate_levels(state.level+1, state)
        elif line.data[0] == '@':
            handle = self.__find_person_handle(self.pid_map[line.data])
            ref = gen.lib.PersonRef()
            ref.ref = handle
            ref.rel = "Alias"
            state.person.add_person_ref(ref)
        else:
            self.__parse_alias_name(line, state)
        
    def __parse_alias_name(self, line, state):
        """
        Parse a level 1 alias name and subsidiary levels when called from
        __person_alt_name (when the <NAME_PERSONAL> does not start with @). Also
        parses a level 2 alias name and subsidiary levels when called from
        __name_alias.
        
          +1  <ALIA> <NAME_PERSONAL>               {1:1}
            +2 NPFX <NAME_PIECE_PREFIX>            {0:1}
            +2 GIVN <NAME_PIECE_GIVEN>             {0:1}
            +2 NICK <NAME_PIECE_NICKNAME>          {0:1}
            +2 SPFX <NAME_PIECE_SURNAME_PREFIX>    {0:1}
            +2 SURN <NAME_PIECE_SURNAME>           {0:1}
            +2 NSFX <NAME_PIECE_SUFFIX>            {0:1}
            +2 <<SOURCE_CITATION>>                 {0:M}
              +3 <<NOTE_STRUCTURE>>                {0:M}
              +3 <<MULTIMEDIA_LINK>>               {0:M}
            +2 <<NOTE_STRUCTURE>>                  {0:M}
        where <ALIA> == ALIA | _ALIA | ALIAS

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        name = self.__parse_name_personal(line.data)
        name.set_type(gen.lib.NameType.AKA)
        state.person.add_alternate_name(name)

        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = state.level+1

        self.__parse_level(sub_state, self.name_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __person_object(self, line, state):
        """
        
        Embedded form
        
        >   n OBJE @<XREF:OBJE>@ {1:1}

        Linked form
         
        >   n OBJE {1:1}
        >   +1 FORM <MULTIMEDIA_FORMAT> {1:1}
        >   +1 TITL <DESCRIPTIVE_TITLE> {0:1}
        >   +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
        >   +1 <<NOTE_STRUCTURE>> {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.person.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.__obje(state.level+1, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.person, form, filename, title, note)

    def __person_name(self, line, state):
        """
        Parsers the NAME token in a GEDCOM file. The text is in the format
        of (according to the GEDCOM Spec):
        >   <TEXT>|/<TEXT>/|<TEXT>/<TEXT>/|/<TEXT>/<TEXT>|<TEXT>/<TEXT>/<TEXT>
        We have encountered some variations that use:
        >   <TEXT>/

        The basic Name structure is:

          n  NAME <NAME_PERSONAL> {1:1}
          +1 NPFX <NAME_PIECE_PREFIX> {0:1}
          +1 GIVN <NAME_PIECE_GIVEN> {0:1}
          +1 NICK <NAME_PIECE_NICKNAME> {0:1}
          +1 SPFX <NAME_PIECE_SURNAME_PREFIX {0:1}
          +1 SURN <NAME_PIECE_SURNAME> {0:1}
          +1 NSFX <NAME_PIECE_SUFFIX> {0:1}
          +1 <<SOURCE_CITATION>> {0:M}
          +1 <<NOTE_STRUCTURE>> {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        # build a gen.lib.Name structure from the text
        
        name = self.__parse_name_personal(line.data)

        # Add the name as the primary name if this is the first one that
        # we have encountered for this person. Assume that if this is the
        # first name, that it is a birth name. Otherwise, label it as an
        # "Also Known As (AKA)". GEDCOM does not seem to have the concept
        # of different name types
        
        if state.name_cnt == 0:
            name.set_type(gen.lib.NameType.BIRTH)
            state.person.set_primary_name(name)
        else:
            name.set_type(gen.lib.NameType.AKA)
            state.person.add_alternate_name(name)
        state.name_cnt += 1

        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = state.level+1

        self.__parse_level(sub_state, self.name_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __person_sex(self, line, state):
        """
        Parses the SEX line of a GEDCOM file. It has the format of:

        +1 SEX <SEX_VALUE> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.person.set_gender(line.data)

    def __person_even(self, line, state):
        """
        Parses the custom EVEN tag, which has the format of:

           n  <<EVENT_TYPE>> {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(state, gen.lib.EventType.CUSTOM, 
                                           self.event_parse_tbl, line.data)
        state.person.add_event_ref(event_ref)

    def __person_std_event(self, line, state):
        """
        Parses GEDCOM event types that map to a GRAMPS standard type. Additional
        parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        event = line.data
        event.set_gramps_id(self.emapper.find_next())
        event_ref = gen.lib.EventRef()
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level+1
        sub_state.event = event
        sub_state.event_ref = event_ref

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.dbase.commit_event(event, self.trans)
        event_ref.ref = event.handle
        state.person.add_event_ref(event_ref)

    def __person_reli(self, line, state):
        """
        Parses the RELI tag.

           n  RELI [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(state, gen.lib.EventType.RELIGION, 
                                           self.event_parse_tbl, line.data)
        state.person.add_event_ref(event_ref)

    def __person_birt(self, line, state):
        """
        Parses GEDCOM BIRT tag into a GRAMPS birth event. Additional work
        must be done, since additional handling must be done by GRAMPS to set 
        this up as a birth reference event.

           n  BIRT [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*
           +1 FAMC @<XREF:FAM>@ {0:1} p.*

        I'm not sure what value the FAMC actually offers here, since
        the FAMC record should handle this. Why it is a valid sub value
        is beyond me.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(state, gen.lib.EventType.BIRTH, 
                                           self.event_parse_tbl, line.data)
        if state.person.get_birth_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_birth_ref(event_ref)

    def __person_adop(self, line, state):
        """
        Parses GEDCOM ADOP tag, subordinate to the INDI tag. Additinal tags
        are needed by the tag, so we pass a different function map.

           n  ADOP [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*
           +1 FAMC @<XREF:FAM>@ {0:1} p.*
           +2 ADOP <ADOPTED_BY_WHICH_PARENT> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(state, gen.lib.EventType.ADOPT, 
                                           self.adopt_parse_tbl, line.data)
        state.person.add_event_ref(event_ref)

    def __person_deat(self, line, state):
        """
        Parses GEDCOM DEAT tag into a GRAMPS birth event. Additional work
        must be done, since additional handling must be done by GRAMPS to set 
        this up as a death reference event.

           n  DEAT [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(state, gen.lib.EventType.DEATH, 
                                           self.event_parse_tbl, line.data)
        if state.person.get_death_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_death_ref(event_ref)

    def __person_note(self, line, state):
        """
        Parses a note associated with the person

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.person, 1, state)

    def __person_rnote(self, line, state):
        """
        Parses a note associated with the person

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.person, 1, state)

    def __person_addr(self, line, state):
        """
        Parses the INDIvidual <ADDRESS_STRUCTURE>

        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        free_form = line.data
        
        sub_state = CurrentState(level=state.level + 1)
        sub_state.addr = gen.lib.Address()
        
        self.__parse_level(sub_state, self.parse_addr_tbl, self.__ignore)
        state.msg += sub_state.msg
        
        self.__merge_address(free_form, sub_state.addr, line, state)
        state.person.add_address(sub_state.addr)

    def __person_phon(self, line, state):
        """
        n PHON <PHONE_NUMBER> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        addr = gen.lib.Address()
        addr.set_street("Unknown")
        addr.set_phone(line.data)
        state.person.add_address(addr)
        self.__skip_subordinate_levels(state.level+1, state)
    
    def __person_email(self, line, state):
        """
        O INDI
        1 EMAIL <EMAIL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = gen.lib.Url()
        url.set_path(line.data)
        url.set_type(gen.lib.UrlType(gen.lib.UrlType.EMAIL))
        state.person.add_url(url)
        
    def __person_url(self, line, state):
        """
        O INDI
        1 URL <URL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = gen.lib.Url()
        url.set_path(line.data)
        url.set_type(gen.lib.UrlType(gen.lib.UrlType.WEB_HOME))
        state.person.add_url(url)

    def __person_titl(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event = gen.lib.Event()
        event_ref = gen.lib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(gen.lib.EventType.NOB_TITLE)
        event.set_description(line.data)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level+1
        sub_state.event = event
        sub_state.event_ref = event_ref

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.dbase.add_event(event, self.trans)
        event_ref.ref = event.handle
        state.person.add_event_ref(event_ref)

    def __person_attr_plac(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.attr.get_value() == "":
            state.attr.set_value(line.data)

    def __name_type(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data.upper() in ("_OTHN", "_AKA", "AKA", "AKAN"):
            state.name.set_type(gen.lib.NameType.AKA)
        elif line.data.upper() in ("_MAR", "_MARN", "_MARNM", "MARRIED"):
            state.name.set_type(gen.lib.NameType.MARRIED)
        else:
            state.name.set_type((gen.lib.NameType.CUSTOM, line.data))

    def __name_date(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.name:
            state.name.set_date_object(line.data)

    def __name_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.name, state.level+1, state)

    def __name_alia(self, line, state):
        """
        This parses the illegal (ALIA or ALIAS) or non-standard (_ALIA) GEDCOM
        tag as a subsidiary of the NAME tag.
        
        n  @XREF:INDI@ INDI                        {1:1}
          +1 NAME <NAME_PERSONAL>                  {1:1}
            +2 NPFX <NAME_PIECE_PREFIX>            {0:1}
            +2 GIVN <NAME_PIECE_GIVEN>             {0:1}
            +2 NICK <NAME_PIECE_NICKNAME>          {0:1}
            +2 SPFX <NAME_PIECE_SURNAME_PREFIX>    {0:1}
            +2 SURN <NAME_PIECE_SURNAME>           {0:1}
            +2 NSFX <NAME_PIECE_SUFFIX>            {0:1}
            +2 <ALIA>  <NAME_PERSONAL>             {1:1}
              +3 NPFX <NAME_PIECE_PREFIX>          {0:1}
              +3 GIVN <NAME_PIECE_GIVEN>           {0:1}
              +3 NICK <NAME_PIECE_NICKNAME>        {0:1}
              +3 SPFX <NAME_PIECE_SURNAME_PREFIX>  {0:1}
              +3 SURN <NAME_PIECE_SURNAME>         {0:1}
              +3 NSFX <NAME_PIECE_SUFFIX>          {0:1}
              +3 <<SOURCE_CITATION>>               {0:M}
                +4 <<NOTE_STRUCTURE>>              {0:M}
                +4 <<MULTIMEDIA_LINK>>             {0:M}
              +3 <<NOTE_STRUCTURE>>                {0:M}
            +2 <<SOURCE_CITATION>>                 {0:M}
              +3 <<NOTE_STRUCTURE>>                {0:M}
              +3 <<MULTIMEDIA_LINK>>               {0:M}
            +2 <<NOTE_STRUCTURE>>                  {0:M}

        Note that the subsidiary name structure detail will overwrite the ALIA
        name (if the same elements are provided in both), so the names should
        match.

        "2 _ALIA" is used for example, by PRO-GEN v 3.0a and "2 ALIA" is used 
        by GTEdit and Brother's keeper 5.2 for windows. It had been supported in
        previous versions of Gramps but as it was probably incorrectly coded as
        it would only work if the name started with '@'.
                
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_alias_name(line, state)

    def __name_npfx(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_title(line.data.strip())
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_givn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_first_name(line.data.strip())
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_spfx(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.name.get_surname_list():
            state.name.get_surname_list()[0].set_prefix(line.data.strip())
        else:
            surn = gen.lib.Surname()
            surn.set_prefix(line.data.strip())
            surn.set_primary()
            state.name.set_surname_list([surn])
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_surn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.name.get_surname_list():
            state.name.get_surname_list()[0].set_surname(line.data.strip())
        else:
            surn = gen.lib.Surname()
            surn.set_surname(line.data.strip())
            surn.set_primary()
            state.name.set_surname_list([surn])
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_marnm(self, line, state):
        """
        This is non-standard GEDCOM. _MARNM is reported to be used in Ancestral
        Quest and Personal Ancestral File 5. This will also handle a usage which
        has been found in Brother's Keeper (BROSKEEP VERS 6.1.31 WINDOWS) as
        follows:
        
        0 @I203@ INDI
          1 NAME John Richard/Doe/
            2 _MARN Some Other Name
              3 DATE 27 JUN 1817
        
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        text = line.data.strip()
        data = text.split()
        if len(data) == 1:
            name = gen.lib.Name(state.person.primary_name)
            surn = gen.lib.Surname()
            surn.set_surname(data[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
            name.set_type(gen.lib.NameType.MARRIED)
            state.person.add_alternate_name(name)
        elif len(data) > 1:
            name = self.__parse_name_personal(text)
            name.set_type(gen.lib.NameType.MARRIED)
            state.person.add_alternate_name(name)

    def __name_nsfx(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.name.get_suffix() == "" or \
           state.name.get_suffix() == line.data:
            #suffix might be set before when parsing name string
            state.name.set_suffix(line.data)
        else:
            #previously set suffix different, to not loose information, append
            state.name.set_suffix(state.name.get_suffix() + ' ' + line.data)
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_nick(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_nick_name(line.data.strip())
        self.__skip_subordinate_levels(state.level+1, state)

    def __name_aka(self, line, state):
        """
        This parses the non-standard GEDCOM tags _AKA or _AKAN as a subsidiary
        to the NAME tag, which is reported to have been found in Ancestral Quest
        and Personal Ancestral File 4 and 5. Note: example AQ and PAF files have
        separate 2 NICK and 2 _AKA lines for the same person. The NICK will be
        stored by Gramps in the nick_name field of the name structure, while the
        _AKA, if it is a single word, will be stored in the NICKNAME attribute.
        If more than one word it is stored as an AKA alternate name.
        
        This will also handle a usage which has been found in in  Brother's
        Keeper (BROSKEEP VERS 6.1.31 WINDOWS) as follows:
        
        0 @I203@ INDI
          1 NAME John Richard/Doe/
            2 _AKAN Some Other Name
              3 DATE 27 JUN 1817

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """        
        lname = line.data.split()
        name_len = len(lname)
        if name_len == 1:
            attr = gen.lib.Attribute()
            attr.set_type(gen.lib.AttributeType.NICKNAME)
            attr.set_value(line.data)
            state.person.add_attribute(attr)
        else:
            name = gen.lib.Name()
            surname = gen.lib.Surname()
            surname.set_surname(lname[-1].strip())
            surname.set_primary()
            name.set_surname_list([surname])
            name.set_first_name(' '.join(lname[0:name_len-1]))
#            name = self.__parse_name_personal(line.data)
            name.set_type(gen.lib.NameType.AKA)
            state.person.add_alternate_name(name)

    def __name_adpn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        text = line.data.strip()
        data = text.split()
        if len(data) == 1:
            name = gen.lib.Name(state.person.primary_name)
            surn = gen.lib.Surname()
            surn.set_surname(data[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
            name.set_type((gen.lib.NameType.CUSTOM, "Adopted"))
            state.person.add_alternate_name(name)
        elif len(data) > 1:
            name = self.__parse_name_personal(text)
            name.set_type((gen.lib.NameType.CUSTOM, "Adopted"))
            state.person.add_alternate_name(name)

    
    def __name_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        citation_handle = self.handle_source(line, state.level, state)
        state.name.add_citation(citation_handle)

    def __person_std_attr(self, line, state):
        """
        Parses an TOKEN that GRAMPS recognizes as an Attribute

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.attr = line.data
        sub_state.level = state.level+1
        state.person.add_attribute(sub_state.attr)
        self.__parse_level(sub_state, self.person_attr_parse_tbl, 
                         self.__ignore)
        state.msg += sub_state.msg

    def __person_fact(self, line, state):
        """
        Parses an TOKEN that GRAMPS recognizes as an Attribute

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.attr = gen.lib.Attribute()
        sub_state.attr.set_value(line.data)
        sub_state.level = state.level+1
        state.person.add_attribute(sub_state.attr)
        self.__parse_level(sub_state, self.person_fact_parse_tbl, 
                         self.__ignore)
        state.msg += sub_state.msg

    def __person_fact_type(self, line, state):
        state.attr.set_type(line.data)
        
    def __person_bapl(self, line, state):
        """
        Parses an BAPL TOKEN, producing a GRAMPS LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, gen.lib.LdsOrd.BAPTISM)

    def __person_conl(self, line, state):
        """
        Parses an CONL TOKEN, producing a GRAMPS LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, gen.lib.LdsOrd.CONFIRMATION)

    def __person_endl(self, line, state):
        """
        Parses an ENDL TOKEN, producing a GRAMPS LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, gen.lib.LdsOrd.ENDOWMENT)

    def __person_slgc(self, line, state):
        """
        Parses an SLGC TOKEN, producing a GRAMPS LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, gen.lib.LdsOrd.SEAL_TO_PARENTS)

    def build_lds_ord(self, state, lds_type):
        """
        Parses an LDS ordinance, using the type passed to the routine

        @param state: The current state
        @type state: CurrentState
        @param lds_type: The type of the LDS ordinance
        @type line: LdsOrd type
        """
        sub_state = CurrentState()
        sub_state.level = state.level + 1
        sub_state.lds_ord = gen.lib.LdsOrd()
        sub_state.lds_ord.set_type(lds_type)
        sub_state.place = None
        sub_state.place_fields = PlaceParser()
        sub_state.person = state.person
        state.person.lds_ord_list.append(sub_state.lds_ord)

        self.__parse_level(sub_state, self.lds_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

        if sub_state.place:
            sub_state.place_fields.load_place(sub_state.place, 
                                              sub_state.place.get_title())

    def __lds_temple(self, line, state):
        """
        Parses the TEMP tag, looking up the code for a match.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        value = self.__extract_temple(line)
        if value:
            state.lds_ord.set_temple(value)

    def __lds_date(self, line, state): 
        """
        Parses the DATE tag for the LdsOrd

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.lds_ord.set_date_object(line.data)

    def __lds_famc(self, line, state):
        """
        Parses the FAMC tag attached to the LdsOrd

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        gid = self.fid_map[line.data]
        state.lds_ord.set_family_handle(self.__find_family_handle(gid))

    def __lds_form(self, line, state): 
        """
        Parses the FORM tag thate defines the place structure for a place. 
        This tag, if found, will override any global place structure.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.pf = PlaceParser(line)

    def __lds_plac(self, line, state):
        """
        Parses the PLAC tag attached to the LdsOrd. Create a new place if
        needed and set the title.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        try:
            title = line.data
            place = self.__find_place(title, None)
            if place:
                state.place = place
            else:
                state.place = self.__create_place(title, None)
            state.lds_ord.set_place_handle(state.place.handle)
        except NameError:
            return

    def __lds_sour(self, line, state):
        """
        Parses the SOUR tag attached to the LdsOrd. 

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        citation_handle = self.handle_source(line, state.level, state)
        state.lds_ord.add_citation(citation_handle)

    def __lds_note(self, line, state):
        """
        Parses the NOTE tag attached to the LdsOrd. 

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.lds_ord, state.level+1, state)

    def __lds_stat(self, line, state): 
        """
        Parses the STAT (status) tag attached to the LdsOrd. 

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        status = LDS_STATUS.get(line.data, gen.lib.LdsOrd.STATUS_NONE)
        state.lds_ord.set_status(status)

    def __person_famc(self, line, state):
        """
        Handles the parsing of the FAMC line, which indicates which family the
        person is a child of.

        n FAMC @<XREF:FAM>@ {1:1}
        +1 PEDI <PEDIGREE_LINKAGE_TYPE> {0:M} p.*
        +1 <<NOTE_STRUCTURE>> {0:M} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.ftype = None
        sub_state.primary = False

        gid = self.fid_map[line.data]
        handle = self.__find_family_handle(gid)

        self.__parse_level(sub_state, self.famc_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        # if the handle is not already in the person's parent family list, we
        # need to add it to thie list.

        flist = [fam[0] for fam in state.person.get_parent_family_handle_list()]
        if not handle in flist:
            if sub_state.ftype and int(sub_state.ftype) in RELATION_TYPES:
                state.person.add_parent_family_handle(handle)
            else:
                if state.person.get_main_parents_family_handle() == handle:
                    state.person.set_main_parent_family_handle(None)
                state.person.add_parent_family_handle(handle)

            # search childrefs
            family, new = self.dbase.find_family_from_handle(handle, self.trans)
            family.set_gramps_id(gid)
                
            for ref in family.get_child_ref_list():
                if ref.ref == state.person.handle:
                    if sub_state.ftype:
                        ref.set_mother_relation(sub_state.ftype)
                        ref.set_father_relation(sub_state.ftype)
                    break
            else:
                ref = gen.lib.ChildRef()
                ref.ref = state.person.handle
                if sub_state.ftype:
                    ref.set_mother_relation(sub_state.ftype)
                    ref.set_father_relation(sub_state.ftype)
                family.add_child_ref(ref)
            self.dbase.commit_family(family, self.trans)

    def __person_famc_pedi(self, line, state): 
        """
        Parses the PEDI tag attached to a INDI.FAMC record. No values are set
        at this point, because we have to do some post processing. Instead, we
        assign the ftype field of the state variable. We convert the text from
        the line to an index into the PEDIGREE_TYPES dictionary, which will map
        to the correct ChildTypeRef.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.ftype = PEDIGREE_TYPES.get(line.data.lower(), 
                                         gen.lib.ChildRefType.UNKNOWN)

    def __person_famc_note(self, line, state):
        """
        Parses the INDI.FAMC.NOTE tag .

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.person, state.level+1, state)

    def __person_famc_primary(self, line, state): 
        """
        Parses the _PRIM tag on an INDI.FAMC tag. This value is stored in 
        the state record to be used later.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.primary = True

    def __person_famc_sour(self, line, state):
        """
        Parses the SOUR tag on an INDI.FAMC tag. GRAMPS has no corresponding
        record on its family relationship, so we add the source to the Person
        record.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        citation_handle = self.handle_source(line, state.level, state)
        state.person.add_citation(citation_handle)

    def __person_fams(self, line, state):
        """
        Parses the INDI.FAMS record, which indicates the family in which the
        person is a spouse.

        n FAMS @<XREF:FAM>@ {1:1} p.*
        +1 <<NOTE_STRUCTURE>> {0:M} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        gid = self.fid_map[line.data]
        handle = self.__find_family_handle(gid)
        state.person.add_family_handle(handle)

        sub_state = CurrentState(level=state.level+1)
        sub_state.obj = state.person
        self.__parse_level(sub_state, self.opt_note_tbl, self.__ignore)
        state.msg += sub_state.msg

    def __person_asso(self, line, state):
        """
        Parse the ASSO tag, add the the referenced person to the person we
        are currently parsing. The GEDCOM spec indicates that valid ASSO tag
        is:
        
        n ASSO @<XREF:INDI>@ {0:M}
           
        And the the sub tags are:
        
        ASSOCIATION_STRUCTURE:=
         +1 RELA <RELATION_IS_DESCRIPTOR> {1:1}
         +1 <<NOTE_STRUCTURE>> {0:M}
         +1 <<SOURCE_CITATION>> {0:M}

        The Gedcom spec notes that the ASSOCIATION_STRUCTURE 
        can only link to an INDIVIDUAL_RECORD

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        # find the id and person that we are referencing
        handle = self.__find_person_handle(self.pid_map[line.data])

        # create a new PersonRef, and assign the handle, add the
        # PersonRef to the active person

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.ref = gen.lib.PersonRef()
        sub_state.ref.ref = handle
        sub_state.ignore = False

        self.__parse_level(sub_state, self.asso_parse_tbl, self.__ignore)
        state.msg += sub_state.msg
        if not sub_state.ignore:
            state.person.add_person_ref(sub_state.ref)

    def __person_asso_rela(self, line, state): 
        """
        Parses the INDI.ASSO.RELA tag.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.ref.rel = line.data

    def __person_asso_sour(self, line, state):
        """
        Parses the INDI.ASSO.SOUR tag.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.ref.add_citation(self.handle_source(line, state.level, state))

    def __person_asso_note(self, line, state):
        """
        Parses the INDI.ASSO.NOTE tag.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.ref, state.level, state)

    #-------------------------------------------------------------------
    # 
    # FAM parsing
    #
    #-------------------------------------------------------------------
        
    def __parse_fam(self, line):
        """
        n @<XREF:FAM>@   FAM   {1:1}
          +1 <<FAMILY_EVENT_STRUCTURE>>  {0:M}
          +1 HUSB @<XREF:INDI>@  {0:1}
          +1 WIFE @<XREF:INDI>@  {0:1}
          +1 CHIL @<XREF:INDI>@  {0:M}
          +1 NCHI <COUNT_OF_CHILDREN>  {0:1}
          +1 SUBM @<XREF:SUBM>@  {0:M}
          +1 <<LDS_SPOUSE_SEALING>>  {0:M}
          +1 <<SOURCE_CITATION>>  {0:M}
          +1 <<MULTIMEDIA_LINK>>  {0:M}
          +1 <<NOTE_STRUCTURE>>  {0:M}
          +1 REFN <USER_REFERENCE_NUMBER>  {0:M}
          +1 RIN <AUTOMATED_RECORD_ID>  {0:1}
          +1 <<CHANGE_DATE>>  {0:1}
        """
        # create a family
        
        gid = self.fid_map[line.token_text]
        family = self.__find_or_create_family(gid)

        # parse the family

        state = CurrentState(level=1)
        state.family = family

        self.__parse_level(state, self.family_func, self.__family_even)

        # handle addresses attached to families
        if state.addr is not None:
            father_handle = family.get_father_handle()
            father = self.dbase.get_person_from_handle(father_handle)
            if father:
                father.add_address(state.addr)
                self.dbase.commit_person(father, self.trans)
            mother_handle = family.get_mother_handle()
            mother = self.dbase.get_person_from_handle(mother_handle)
            if mother:
                mother.add_address(state.addr)
                self.dbase.commit_person(mother, self.trans)

            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.dbase.get_person_from_handle(child_handle)
                if child:
                    child.add_address(state.addr)
                    self.dbase.commit_person(child, self.trans)

        # add default reference if no reference exists
        self.__add_default_source(family)

        self.__check_msgs(_("FAM (family) Gramps ID %s") % family.get_gramps_id(), 
                          state, family)
        # commit family to database
        self.dbase.commit_family(family, self.trans, family.change)
    
    def __family_husb(self, line, state):
        """
        Parses the husband line of a family

        n HUSB @<XREF:INDI>@  {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
            """
        handle = self.__find_person_handle(self.pid_map[line.data])
        state.family.set_father_handle(handle)

    def __family_wife(self, line, state):
        """
            Parses the wife line of a family

              n WIFE @<XREF:INDI>@  {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
            """
        handle = self.__find_person_handle(self.pid_map[line.data])
        state.family.set_mother_handle(handle)

    def __family_std_event(self, line, state):
        """
        Parses GEDCOM event types that map to a GRAMPS standard type. Additional
        parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event = line.data
        event.set_gramps_id(self.emapper.find_next())
        event_ref = gen.lib.EventRef()
        event_ref.set_role(gen.lib.EventRoleType.FAMILY)
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level+1
        sub_state.event = event
        sub_state.event_ref = event_ref

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        if event.type == gen.lib.EventType.MARRIAGE:
            descr = event.get_description()
            if descr == "Civil Union":
                state.family.type.set(gen.lib.FamilyRelType.CIVIL_UNION)
                event.set_description('')
            elif descr == "Unmarried":
                state.family.type.set(gen.lib.FamilyRelType.UNMARRIED)
                event.set_description('')
            else:
                state.family.type.set(gen.lib.FamilyRelType.MARRIED)

        self.dbase.commit_event(event, self.trans)
        event_ref.ref = event.handle
        state.family.add_event_ref(event_ref)

    def __family_even(self, line, state):
        """
        Parses GEDCOM event types that map to a GRAMPS standard type. Additional
        parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event = gen.lib.Event()
        event_ref = gen.lib.EventRef()
        event_ref.set_role(gen.lib.EventRoleType.FAMILY)
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(line.data)
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level+1
        sub_state.event = event
        sub_state.event_ref = event_ref

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.dbase.commit_event(event, self.trans)
        event_ref.ref = event.handle
        state.family.add_event_ref(event_ref)

    def __family_chil(self, line, state):
        """
        Parses the child line of a family

        n CHIL @<XREF:INDI>@  {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.family = state.family
        sub_state.level = state.level + 1
        sub_state.mrel = None
        sub_state.frel = None

        self.__parse_level(sub_state, self.family_rel_tbl, self.__ignore)
        state.msg += sub_state.msg

        child = self.__find_or_create_person(self.pid_map[line.data])

        reflist = [ref for ref in state.family.get_child_ref_list()
                    if ref.ref == child.handle]

        if reflist: # The child has been referenced already
            ref = reflist[0]
            if sub_state.frel:
                ref.set_father_relation(sub_state.frel)
            if sub_state.mrel:
                ref.set_mother_relation(sub_state.mrel)
            # then we will set the order now:
            self.set_child_ref_order(state.family, ref)
        else:
            ref = gen.lib.ChildRef()
            ref.ref = child.handle
            if sub_state.frel:
                ref.set_father_relation(sub_state.frel)
            if sub_state.mrel:
                ref.set_mother_relation(sub_state.mrel)
            state.family.add_child_ref(ref)

    def set_child_ref_order(self, family, child_ref):
        """
        Sets the child_ref in family.child_ref_list to be in the position
        family.child_ref_count. This reorders the children to be in the 
        order given in the FAM section.
        """
        family.child_ref_list.remove(child_ref)
        family.child_ref_list.insert(family.child_ref_count, child_ref)
        family.child_ref_count += 1

    def __family_slgs(self, line, state):
        """
        n  SLGS          {1:1}
        +1 STAT <LDS_SPOUSE_SEALING_DATE_STATUS>  {0:1}
        +1 DATE <DATE_LDS_ORD>  {0:1}
        +1 TEMP <TEMPLE_CODE>  {0:1}
        +1 PLAC <PLACE_LIVING_ORDINANCE>  {0:1}
        +1 <<SOURCE_CITATION>>  {0:M}
        +1 <<NOTE_STRUCTURE>>  {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
            """
        sub_state = CurrentState()
        sub_state.level = state.level + 1
        sub_state.lds_ord = gen.lib.LdsOrd()
        sub_state.lds_ord.set_type(gen.lib.LdsOrd.SEAL_TO_SPOUSE)
        sub_state.place = None
        sub_state.family = state.family
        sub_state.place_fields = PlaceParser()
        state.family.lds_ord_list.append(sub_state.lds_ord)

        self.__parse_level(sub_state, self.lds_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

        if sub_state.place:
            sub_state.place_fields.load_place(sub_state.place, 
                                              sub_state.place.get_title())

    def __family_source(self, line, state):
        """
        n SOUR @<XREF:SOUR>@ /* pointer to source record */ {1:1} p.*
        +1 PAGE <WHERE_WITHIN_SOURCE> {0:1} p.*
        +1 EVEN <EVENT_TYPE_CITED_FROM> {0:1} p.*
        +1 DATA {0:1}
        +1 QUAY <CERTAINTY_ASSESSMENT> {0:1} p.*
        +1 <<MULTIMEDIA_LINK>> {0:M} p.*, *
        +1 <<NOTE_STRUCTURE>> {0:M} p.*

        | /* Systems not using source records */
        n SOUR <SOURCE_DESCRIPTION> {1:1} p.*
        +1 [ CONC | CONT ] <SOURCE_DESCRIPTION> {0:M}
        +1 TEXT <TEXT_FROM_SOURCE> {0:M} p.*
        +1 <<NOTE_STRUCTURE>> {0:M} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        citation_handle = self.handle_source(line, state.level, state)
        state.family.add_citation(citation_handle)

    def __family_object(self, line, state):
        """
          +1 <<MULTIMEDIA_LINK>>  {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.family.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.__obje(state.level + 1, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.family, form, filename, title, note)

    def __family_comm(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        note = line.data
        state.family.add_note(note)
        self.__skip_subordinate_levels(state.level+1, state)

    def __family_note(self, line, state):
        """
        +1 <<NOTE_STRUCTURE>>  {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.family, state.level, state)

    def __family_chan(self, line, state):
        """
        +1 <<CHANGE_DATE>>  {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.family, state.level+1, state)

    def __family_attr(self, line, state): 
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.family.add_attribute(line.data)

    def __family_cust_attr(self, line, state): 
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(line.token_text)
        attr.set_value(line.data)
        state.family.add_attribute(attr)

    def __obje(self, level, state):
        """
          n  OBJE {1:1}
          +1 FORM <MULTIMEDIA_FORMAT> {1:1}
          +1 TITL <DESCRIPTIVE_TITLE> {0:1}
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M} 

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.form = ""
        sub_state.filename = ""
        sub_state.title = ""
        sub_state.note = ""
        sub_state.level = level

        self.__parse_level(sub_state, self.object_parse_tbl, self.__ignore)
        state.msg += sub_state.msg
        return (sub_state.form, sub_state.filename, sub_state.title, 
                sub_state.note)

    def __object_ref_form(self, line, state): 
        """
          +1 FORM <MULTIMEDIA_FORMAT> {1:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.form = line.data

    def __object_ref_titl(self, line, state): 
        """
          +1 TITL <DESCRIPTIVE_TITLE> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.title = line.data

    def __object_ref_file(self, line, state): 
        """
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.filename = line.data

    def __object_ref_note(self, line, state): 
        """
          +1 <<NOTE_STRUCTURE>> {0:M} 

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # This code pretty much duplicates the code in __parse_note. In
        # __parse_note, we already know the object to which the note is to be
        # attached, so we can directly add the note to the object. however, in
        # the case of a media object, the media object is not constructed till
        # the end of processing, so we just remember the handle of the note.
        if line.token == TOKEN_RNOTE:
            # reference to a named note defined elsewhere
            #NOTE_STRUCTURE: =
            #  n  NOTE @<XREF:NOTE>@  {1:1}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}
            state.note = self.__find_note_handle(self.nid_map[line.data])
        else:
            # Embedded note
            #NOTE_STRUCTURE: =
            #  n  NOTE [<SUBMITTER_TEXT> | <NULL>]  {1:1}
            #    +1 [ CONC | CONT ] <SUBMITTER_TEXT>  {0:M}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}
            if not line.data:
                self.__add_msg(_("Empty note ignored"), line, state)
                self.__skip_subordinate_levels(state.level+1, state)
            else:
                new_note = gen.lib.Note(line.data)
                new_note.set_gramps_id(self.nid_map[""])
                new_note.set_handle(Utils.create_id())

                sub_state = CurrentState(level=state.level+1)
                sub_state.note = new_note
                self.__parse_level(sub_state, self.note_parse_tbl, 
                                   self.__undefined)
                state.msg += sub_state.msg

                self.dbase.commit_note(new_note, self.trans, new_note.change)
                state.note = new_note.get_handle()

    def __family_adopt(self, line, state):
        """
        n ADOP

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.frel = TYPE_ADOPT
        state.mrel = TYPE_ADOPT

    def __family_frel(self, line, state):
        """
        The _FREL key is a FTW/FTM specific extension to indicate father/child
        relationship.

        n _FREL <type>

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.frel = PEDIGREE_TYPES.get(line.data.strip().lower())

    def __family_mrel(self, line, state):
        """
        The _MREL key is a FTW/FTM specific extension to indicate father/child
        relationship.

        n _MREL <type>

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.mrel = PEDIGREE_TYPES.get(line.data.strip().lower())

    def __family_stat(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.mrel = TYPE_BIRTH
        state.frel = TYPE_BIRTH

    def __event_object(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.event.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.__obje(state.level + 1, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.event, form, filename, title, note)

    def __event_type(self, line, state):
        """
        Parses the TYPE line for an event.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.event.get_type().is_custom():
            if line.data in GED_TO_GRAMPS_EVENT:
                name = gen.lib.EventType(GED_TO_GRAMPS_EVENT[line.data])
            else:
                val = self.gedsource.tag2gramps(line.data)
                if val:
                    name = gen.lib.EventType((gen.lib.EventType.CUSTOM, val))
                else:
                    try:
                        name = gen.lib.EventType((gen.lib.EventType.CUSTOM, 
                                                 line.data))
                    except AttributeError:
                        name = gen.lib.EventType(gen.lib.EventType.UNKNOWN)
            state.event.set_type(name)
        else:
            try:
                if line.data not in GED_TO_GRAMPS_EVENT and \
                       line.data[0] != 'Y':
                    state.event.set_description(line.data)
            except IndexError:
                return

    def __event_date(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.event.set_date_object(line.data)

    def __event_place(self, line, state):
        """
        Parse the place portion of a event. A special case has to be made for
        Family Tree Maker, which violates the GEDCOM spec. It uses the PLAC 
        field to store the description or value associated with the event.

         n  PLAC <PLACE_VALUE> {1:1}
         +1 FORM <PLACE_HIERARCHY> {0:1}
         +1 <<SOURCE_CITATION>> {0:M}
         +1 <<NOTE_STRUCTURE>> {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        location = None
        if self.is_ftw and state.event.type in FTW_BAD_PLACE:
            state.event.set_description(line.data)
        else:
            title = line.data
            place_handle = state.event.get_place_handle()
            if place_handle:
                # We encounter a PLAC, having previously encountered an ADDR
                old_place = self.dbase.get_place_from_handle(place_handle)
                old_title = old_place.get_title()
                location = old_place.get_main_location()
                if old_title != "":
                    # We have previously found a PLAC 
                    self.__add_msg(_("A second PLAC ignored"), line, state)
                    # ignore this second PLAC, and use the old one
                    title = old_title
                    place = old_place
                else:
                    # This is the first PLAC
                    refs = list(self.dbase.find_backlink_handles(place_handle))
                    # We haven't commited the event yet, so the place will not
                    # be linked to it. If there are any refs they will be from
                    # other events (etc)
                    if len(refs) == 0:
                        place = self.__find_place(title, location)
                        if place is None:
                            place = old_place
                            place.set_title(title)
                            self.place_names[old_title].remove(place_handle)
                            self.place_names[title].append(place_handle)
                        else:
                            place.merge(old_place)
                            self.dbase.remove_place(place_handle, self.trans)
                            self.place_names[old_title].remove(place_handle)
                    else:
                        place = self.__find_place(title, location)
                        if place is None:
                            place = self.__create_place(title, location)
                        else:
                            pass
            else:
                # The first thing we encounter is PLAC
                location = None
                place = self.__find_place(title, location)
                if place is None:
                    place = self.__create_place(title, location)

            state.event.set_place_handle(place.handle)            

            sub_state = CurrentState()
            sub_state.place = place
            sub_state.level = state.level+1
            sub_state.pf = self.place_parser

            self.__parse_level(sub_state, self.event_place_map, 
                             self.__undefined)
            state.msg += sub_state.msg

            sub_state.pf.load_place(place, place.get_title())
            # If we already had a remembered location, we set it into the main
            # location if that is empty, else the alternate location
            if location and not location.is_empty():
                if place.get_main_location().is_empty():
                    place.set_main_location(location)
                else:
                    place.add_alternate_locations(location)
            self.dbase.commit_place(place, self.trans)

    def __event_place_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.place, state.level+1, state)

    def __event_place_form(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.pf = PlaceParser(line)

    def __event_place_object(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.place.add_media_reference(ref)
        else:
            # FIXME this should probably be level+1
            (form, filename, title, note) = self.__obje(state.level, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.place, form, filename, title, note)

    def __event_place_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.place.add_citation(self.handle_source(line, state.level, state))

    def __place_map(self, line, state):
        """
        
        n   MAP
        n+1 LONG <PLACE_LONGITUDE>
        n+1 LATI <PLACE_LATITUDE>
        
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.level = state.level + 1
        sub_state.place = state.place
        self.__parse_level(sub_state, self.place_map_tbl, self.__undefined)
        state.msg += sub_state.msg
        state.place = sub_state.place

    def __place_lati(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.place.set_latitude( line.data)

    def __place_long(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.place.set_longitude( line.data)

    def __event_addr(self, line, state):
        """
        Parses the EVENt <ADDRESS_STRUCTURE>
        
        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        free_form = line.data
        
        sub_state = CurrentState(level=state.level+1)
        sub_state.location = gen.lib.Location()
        sub_state.event = state.event
        sub_state.place = gen.lib.Place() # temp stash for notes, citations etc

        self.__parse_level(sub_state, self.parse_loc_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__merge_address(free_form, sub_state.location, line, state)

        location = sub_state.location
        place_handle = state.event.get_place_handle()
        if place_handle:
            # We encounter an ADDR having previously encountered a PLAC
            old_place = self.dbase.get_place_from_handle(place_handle)
            title = old_place.get_title()
            if not old_place.get_main_location().is_empty():
                # We have perviously found an ADDR, or have populated location
                # from PLAC title
                self.__add_msg(_("Location already populated; ADDR ignored"),
                               line, state)
                # ignore this second ADDR, and use the old one
                location = old_place.get_main_location()
                place = old_place
            else:
                # This is the first ADDR
                refs = list(self.dbase.find_backlink_handles(place_handle))
                # We haven't commited the event yet, so the place will not be
                # linked to it. If there are any refs they will be from other
                # events (etc)
                if len(refs) == 0:
                    place = self.__find_place(title, location)
                    if place is None:
                        place = old_place
                        place.set_main_location(location)
                    else:
                        place.merge(old_place)
                        self.dbase.remove_place(place_handle, self.trans)
                        self.place_names[title].remove(place_handle)
                else:
                    place = self.__find_place(title, location)
                    if place is None:
                        place = self.__create_place(title, location)
                    else:
                        pass
        else:
            # The first thing we encounter is ADDR
            title = ""
            place = self.__find_place(title, location)
            if place is None:
                place = self.__create_place(title, location)

        # merge notes etc into place
        place.merge(sub_state.place)

        state.event.set_place_handle(place.get_handle())
        self.dbase.commit_place(place, self.trans)

    def __add_location(self, place, location):
        """
        @param place: A place object we have found or created
        @type place: gen.lib.Place
        @param location: A location we want to add to this place
        @type location: gen.lib.location
        """
        # If there is no main location, we add the location
        if place.main_loc is None:
            place.set_main_location(location)
        elif place.get_main_location().is_equivalent(location) == IDENTICAL:
            # the location is already present as the main location
            pass
        else:
            for loc in place.get_alternate_locations():
                if loc.is_equivalent(location) == IDENTICAL:
                    return
            place.add_alternate_locations(location)
                
    
    def __event_phon(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        place_handle = state.event.get_place_handle()
        if place_handle:
            place = self.dbase.get_place_from_handle(place_handle)
            location = place.get_main_location()
            location.set_phone(line.data)
            self.dbase.commit_place(place, self.trans)

    def __event_privacy(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.event.set_privacy(True)

    def __event_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.event, state.level+1, state)

    def __event_inline_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data[0:13] == "Description: ":
            state.event.set_description(line.data[13:])
        else:
            if not line.data:
                # empty: discard, with warning and skip subs
                # Note: level+2
                self.__add_msg(_("Empty event note ignored"), line, state)
                self.__skip_subordinate_levels(state.level+2, state)
            else:
                new_note = gen.lib.Note(line.data)
                new_note.set_handle(Utils.create_id())
                self.dbase.add_note(new_note, self.trans)
                self.__skip_subordinate_levels(state.level+2, state)
                state.event.add_note(new_note.get_handle())
                
    def __event_source(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.event.add_citation(self.handle_source(line, state.level, state))

    def __event_rin(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(line.token_text)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.event.add_attribute(line.data)

    def __event_email(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(line.token_text)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_www(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(line.token_text)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_cause(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.CAUSE)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

        sub_state = CurrentState()
        sub_state.event = state.event
        sub_state.level = state.level + 1
        sub_state.attr = attr

        self.__parse_level(sub_state, self.event_cause_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __event_cause_source(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.attr.add_citation(self.handle_source(line, state.level, state))

    def __event_age(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGE)
        attr.set_value(line.data)
        state.event_ref.add_attribute(attr)

    def __event_husb(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_AGE:
                attr = gen.lib.Attribute()
                attr.set_type(gen.lib.AttributeType.FATHER_AGE)
                attr.set_value(line.data)
                state.event_ref.add_attribute(attr)
            elif line.token == TOKEN_WIFE:
                #wife event can be on same level, if so call it and finish
                self.__event_wife(line, state)
                break

    def __event_wife(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_AGE:
                attr = gen.lib.Attribute()
                attr.set_type(gen.lib.AttributeType.MOTHER_AGE)
                attr.set_value(line.data)
                state.event_ref.add_attribute(attr)
            elif line.token == TOKEN_HUSB:
                #husband event can be on same level, if so call it and finish
                self.__event_husb(line, state)
                break

    def __event_agnc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGENCY)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_time(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if hasattr(state, 'event'):
            #read in time as attribute of event
            attr = gen.lib.Attribute()
            attr.set_type(gen.lib.AttributeType.TIME)
            attr.set_value(line.data)
            state.event.add_attribute(attr)

    def __event_witness(self, line, state):
        """
        Parse the witness of an event

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == "@":
            # n  _WITN @<XREF:INDI>@
            # +1 TYPE <TYPE_OF_RELATION>
            assert( state.event.handle)  # event handle is required to be set
            wit = self.__find_or_create_person(self.pid_map[line.data])
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(state.event.handle)
            while True:
                line = self.__get_next_line()
                if self.__level_is_finished(line, state.level+1):
                    break
                elif line.token == TOKEN_TYPE:
                    if line.data in ("WITNESS_OF_MARRIAGE"):
                        role = gen.lib.EventRoleType(
                            gen.lib.EventRoleType.WITNESS)
                    else:
                        role = gen.lib.EventRoleType(
                            (gen.lib.EventRoleType.CUSTOM, line.data))
                    event_ref.set_role(role)
            wit.add_event_ref(event_ref)
            self.dbase.commit_person(wit, self.trans)
        else:
            # n _WITN <TEXTUAL_LIST_OF_NAMES>
            attr = gen.lib.Attribute()
            attr.set_type(gen.lib.AttributeType.WITNESS)
            attr.set_value(line.data)
            state.event.add_attribute(attr)
        
    def __person_adopt_famc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        gid = self.fid_map[line.data]
        handle = self.__find_family_handle(gid)
        family = self.__find_or_create_family(gid)

        sub_state = CurrentState(level=state.level+1)
        sub_state.mrel = TYPE_BIRTH
        sub_state.frel = TYPE_BIRTH

        self.__parse_level(sub_state, self.parse_person_adopt, 
                         self.__undefined)
        state.msg += sub_state.msg

        if (int(sub_state.mrel) == gen.lib.ChildRefType.BIRTH  and
            int(sub_state.frel) == gen.lib.ChildRefType.BIRTH):
            sub_state.mrel = sub_state.frel = TYPE_ADOPT

        if state.person.get_main_parents_family_handle() == handle:
            state.person.set_main_parent_family_handle(None)
        state.person.add_parent_family_handle(handle)
        
        reflist = [ref for ref in family.get_child_ref_list()
                        if ref.ref == state.person.handle]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(sub_state.frel)
            ref.set_mother_relation(sub_state.mrel)
        else:
            ref = gen.lib.ChildRef()
            ref.ref = state.person.handle
            ref.set_father_relation(sub_state.frel)
            ref.set_mother_relation(sub_state.mrel)
            family.add_child_ref(ref)
            self.dbase.commit_family(family, self.trans)

    def __person_adopt_famc_adopt(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data.strip() == "HUSB":
            state.frel = TYPE_ADOPT
        elif line.data.strip() == "WIFE":
            state.mrel = TYPE_ADOPT
        else:
            state.mrel = TYPE_ADOPT
            state.frel = TYPE_ADOPT

    def __person_birth_famc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        handle = self.__find_family_handle(self.fid_map[line.data])

        if state.person.get_main_parents_family_handle() == handle:
            state.person.set_main_parent_family_handle(None)
        state.person.add_parent_family_handle(handle)
        
        frel = mrel = gen.lib.ChildRefType.BIRTH

        family, new = self.dbase.find_family_from_handle(handle, self.trans)
        reflist = [ref for ref in family.get_child_ref_list()
                        if ref.ref == state.person.handle]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
        else:
            ref = gen.lib.ChildRef()
            ref.ref = state.person.handle
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
            family.add_child_ref(ref)
            self.dbase.commit_family(family, self.trans)

    def __address_date(self, line, state):
        """
        Parses the DATE line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_date_object(line.data)

    def __address_adr1(self, line, state):
        """
        Parses the ADR1 line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # The ADDR may already have been parsed by the level above
        assert state.addr.get_street() == ""
        if state.addr.get_street() != "":
            self.__add_msg(_("Warn: ADDR overwritten"), line, state)
        state.addr.set_street(line.data)

    def __address_adr2(self, line, state):
        """
        Parses the ADR2 line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_locality(line.data)

    def __address_city(self, line, state):
        """
        Parses the CITY line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_city(line.data)

    def __address_state(self, line, state):
        """
        Parses the STAE line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_state(line.data)

    def __address_post(self, line, state):
        """
        Parses the POST line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_postal_code(line.data)
            
    def __address_country(self, line, state):
        """
        Parses the country line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.set_country(line.data)
    
    def __address_sour(self, line, state):
        """
        Parses the SOUR line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.addr.add_citation(self.handle_source(line, state.level, state))
            
    def __address_note(self, line, state):
        """
        Parses the NOTE line of an ADDR tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.addr, state.level+1, state)

    def __citation_page(self, line, state):
        """
        Parses the PAGE line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.citation.set_page(line.data)

    def __citation_date(self, line, state):
        """
        Parses the DATE line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.citation.set_date_object(line.data)

    def __citation_data(self, line, state): 
        """
        Parses the DATA line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState(level=state.level+1)
        sub_state.citation = state.citation

        self.__parse_level(sub_state, self.citation_data_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __citation_data_date(self, line, state):
        state.citation.set_date_object(line.data)

    def __source_text(self, line, state):
        note = gen.lib.Note()
        note.set(line.data)
        gramps_id = self.dbase.find_next_note_gramps_id()
        note.set_gramps_id(gramps_id)
        note.set_type(gen.lib.NoteType.SOURCE_TEXT)
        self.dbase.add_note(note, self.trans)

        state.source.add_note(note.get_handle())

    def __citation_data_text(self, line, state):
        note = gen.lib.Note()
        note.set(line.data)
        gramps_id = self.dbase.find_next_note_gramps_id()
        note.set_gramps_id(gramps_id)
        note.set_type(gen.lib.NoteType.SOURCE_TEXT)
        self.dbase.add_note(note, self.trans)

        state.citation.add_note(note.get_handle())

    def __citation_data_note(self, line, state):
        self.__parse_note(line, state.citation, state.level, state)

    def __citation_obje(self, line, state): 
        """
        Parses the OBJE line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.citation.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.__obje(state.level+1, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.citation, form, filename, title, note)

    def __citation_refn(self, line, state): 
        """
        Parses the REFN line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("REFN ignored"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __citation_even(self, line, state): 
        """
        Parses the EVEN line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.citation.set_data_item("EVEN", line.data)
        sub_state = CurrentState(level=state.level+1)
        sub_state.citation = state.citation

        self.__parse_level(sub_state, self.citation_even_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __citation_even_role(self, line, state): 
        """
        Parses the EVEN line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.citation.set_data_item("EVEN:ROLE", line.data)

    def __citation_quay(self, line, state): 
        """
        Parses the QUAY line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        try:
            val = int(line.data)
        except ValueError:
            return
        # If value is greater than 3, cap at 3
        val = min(val, 3)
        if val > 1:
            state.citation.set_confidence_level(val+1)
        else:
            state.citation.set_confidence_level(val)

    def __citation_note(self, line, state): 
        """
        Parses the NOTE line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.citation, state.level+1, state)

    #----------------------------------------------------------------------
    #
    # SOUR parsing
    #
    #----------------------------------------------------------------------

    def __parse_source(self, name, level):
        """
        n @<XREF:SOUR>@ SOUR {1:1}
          +1 DATA {0:1}
          +2 EVEN <EVENTS_RECORDED> {0:M}
          +3 DATE <DATE_PERIOD> {0:1} 
          +3 PLAC <SOURCE_JURISDICTION_PLACE> {0:1}
          +2 AGNC <RESPONSIBLE_AGENCY> {0:1}
          +2 <<NOTE_STRUCTURE>> {0:M}
          +1 AUTH <SOURCE_ORIGINATOR> {0:1}
          +1 TITL <SOURCE_DESCRIPTIVE_TITLE> {0:1}
          +1 ABBR <SOURCE_FILED_BY_ENTRY> {0:1}
          +1 PUBL <SOURCE_PUBLICATION_FACTS> {0:1}
          +1 TEXT <TEXT_FROM_SOURCE> {0:1}
          +1 <<SOURCE_REPOSITORY_CITATION>> {0:1} 
          +1 <<MULTIMEDIA_LINK>> {0:M} 
          +1 <<NOTE_STRUCTURE>> {0:M}
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
          +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<CHANGE_DATE>> {0:1}
        """

        state = CurrentState()
        state.source = self.__find_or_create_source(self.sid_map[name]) 
        # SOURce with the given gramps_id had no title
        state.source.set_title(_("No title - ID %s") % 
                               state.source.get_gramps_id())
        state.level = level

        self.__parse_level(state, self.source_func, self.__undefined)
        self.__check_msgs(_("SOUR (source) Gramps ID %s") % 
                          state.source.get_gramps_id(), 
                          state, state.source)
        self.dbase.commit_source(state.source, self.trans, state.source.change)

    def __source_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_data_item(line.token_text, line.data)

    def __source_object(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            
            handle = self.__find_object_handle(gramps_id)
            ref = gen.lib.MediaRef()
            ref.set_reference_handle(handle)
            state.source.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.__obje(state.level+1, state)
            if filename == "":
                self.__add_msg(_("Filename omitted"), line, state)
            if form == "":
                self.__add_msg(_("Form omitted"), line, state)
            self.build_media_object(state.source, form, filename, title, note)

    def __source_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.source, state.level+1, state)

    def __source_undef(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__not_recognized(line, state.level+1, state)

    def __source_repo(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == '@':
            # This deals with the standard GEDCOM
            # SOURCE_REPOSITORY_CITATION: =
            #   n  REPO @<XREF:REPO>@                {1:1}
            #     +1 <<NOTE_STRUCTURE>>              {0:M}
            #     +1 CALN <SOURCE_CALL_NUMBER>       {0:M}
            #        +2 MEDI <SOURCE_MEDIA_TYPE>     {0:1}
            gid = self.rid_map[line.data]
            repo = self.__find_or_create_repository(gid)
        elif line.data == '':
            # This deals with the non-standard GEDCOM format found in Family
            # Tree Maker for Windows, Broderbund Software, Banner Blue
            # Division:
            # SOURCE_REPOSITORY_CITATION: =
            #   n  REPO                              {1:1}
            #     +1 <<NOTE_STRUCTURE>>              {0:M}
            #     +1 CALN <SOURCE_CALL_NUMBER>       {0:M}
            #        +2 MEDI <SOURCE_MEDIA_TYPE>     {0:1}
            #
            # This format has no repository name. See http://west-
            # penwith.org.uk/misc/ftmged.htm which points out this is
            # incorrect
            gid = self.dbase.find_next_repository_gramps_id()
            repo = self.__find_or_create_repository(gid)
            self.dbase.commit_repository(repo, self.trans)
        else:
            # This deals with the non-standard GEDCOM
            # SOURCE_REPOSITORY_CITATION: =
            #   n  REPO <NAME_OF_REPOSITORY>         {1:1}
            #     +1 <<NOTE_STRUCTURE>>              {0:M}
            #     +1 CALN <SOURCE_CALL_NUMBER>       {0:M}
            #        +2 MEDI <SOURCE_MEDIA_TYPE>     {0:1}
            # This seems to be used by Heredis 8 PC. Heredis is notorious for
            # non-standard GEDCOM.
            gid = self.repo2id.get(line.data)
            if gid is None:
                gid = self.dbase.find_next_repository_gramps_id()
            repo = self.__find_or_create_repository(gid)
            self.repo2id[line.data] = repo.get_gramps_id()
            repo.set_name(line.data)
            self.dbase.commit_repository(repo, self.trans)
        
        repo_ref = gen.lib.RepoRef()
        repo_ref.set_reference_handle(repo.handle)

        sub_state = CurrentState()
        sub_state.repo_ref = repo_ref
        sub_state.level = state.level + 1

        self.__parse_level(sub_state, self.repo_ref_tbl, self.__undefined)
        state.msg += sub_state.msg

        state.source.add_repo_reference(repo_ref)

    def __repo_ref_call(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.repo_ref.set_call_number(line.data)
        #self.__skip_subordinate_levels(state.level+1, state)

    def __repo_ref_medi(self, line, state):
        name = line.data
        mtype = MEDIA_MAP.get(name.lower(), 
                              (gen.lib.SourceMediaType.CUSTOM, name))
        state.repo_ref.set_media_type(mtype)

    def __repo_ref_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.repo_ref, state.level+1, state)

    def __repo_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.repo, state.level+1, state)

    def __source_abbr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_abbreviation(line.data)

    def __source_agnc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.AGENCY)
        attr.set_value(line.data)
        state.source.add_attribute(attr)

    def __source_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.source, state.level+1, state)

    def __source_auth(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_author(line.data)

    def __source_publ(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_publication_info(line.data)
        self.__skip_subordinate_levels(state.level+1, state)

    def __source_title(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_title(line.data.replace('\n', ' '))

    def __source_taxt_peri(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.source.get_title() == "":
            state.source.set_title(line.data.replace('\n', ' '))

    #----------------------------------------------------------------------
    #
    # OBJE parsing
    #
    #----------------------------------------------------------------------

    def __parse_obje(self, line):
        """
        n  @XREF:OBJE@ OBJE {1:1}
           +1 FORM <MULTIMEDIA_FORMAT> {1:1} p.*
           +1 TITL <DESCRIPTIVE_TITLE> {0:1} p.*
           +1 <<NOTE_STRUCTURE>> {0:M} p.*
           +1 BLOB {1:1}
           +2 CONT <ENCODED_MULTIMEDIA_LINE> {1:M} p.*
           +1 OBJE @<XREF:OBJE>@ /* chain to continued object */ {0:1} p.*
           +1 REFN <USER_REFERENCE_NUMBER> {0:M} p.*
           +2 TYPE <USER_REFERENCE_TYPE> {0:1} p.*
           +1 RIN <AUTOMATED_RECORD_ID> {0:1} p.*
           +1 <<CHANGE_DATE>> {0:1} p.*
        """
        gid = line.token_text.strip()
        media = self.__find_or_create_object(self.oid_map[gid])

        state = CurrentState()
        state.media = media
        state.level = 1

        self.__parse_level(state, self.obje_func, self.__undefined)

        # Add the default reference if no source has found
        self.__add_default_source(media)

        self.__check_msgs(_("OBJE (multi-media object) Gramps ID %s") % 
                          media.get_gramps_id(), state, media)
        # commit the person to the database
        self.dbase.commit_media_object(media, self.trans, media.change)

    def __obje_form(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # TODO: FIX THIS!!!
        state.media_form = line.data.strip()
        self.__skip_subordinate_levels(state.level+1, state)

    def __obje_file(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        res = urlparse(line.data)
        if line.data != '' and (res.scheme == '' or res.scheme == 'file'):
            (file_ok, filename) = self.__find_file(line.data, self.dir_path)
            if state.media != "URL":
                if not file_ok:
                    self.__add_msg(_("Could not import %s") % filename[0], line,
                                   state)
            path = filename[0].replace('\\', os.path.sep)
        else:
            path = line.data
            
        state.media.set_path(path)
        state.media.set_mime_type(gen.mime.get_type(path))
        if not state.media.get_description():
            state.media.set_description(path)

    def __obje_title(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.media.set_description(line.data)

    def __obje_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.media, state.level+1, state)

    def __obje_blob(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("BLOB ignored"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __obje_refn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("REFN ignored"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __obje_type(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("Multimedia REFN:TYPE ignored"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __obje_rin(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("Mutimedia RIN ignored"), line, state)
        self.__skip_subordinate_levels(state.level+1, state)

    def __obje_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.media, state.level+1, state)

    def __person_attr_type(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.attr.get_type() == "":
            if line.data in GED_TO_GRAMPS_EVENT:
                name = GED_TO_GRAMPS_EVENT[line.data]
            else:
                val = self.gedsource.tag2gramps(line.data)
                if val:
                    name = val
                else:
                    name = line.data
            state.attr.set_type(name)
        else:
            self.__ignore(line, state)

    def __person_attr_source(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.attr.add_citation(self.handle_source(line, state.level, state))

    def __person_attr_place(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        val = line.data
        if state.attr.get_value() == "":
            state.attr.set_value(val)
            self.__skip_subordinate_levels(state.level+1, state)
        else:
            self.__ignore(line, state)

    def __person_attr_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.attr, state.level+1, state)

    #----------------------------------------------------------------------
    #
    # REPO parsing
    #
    #----------------------------------------------------------------------

    def __parse_repo(self, line):
        """
        n @<XREF:REPO>@ REPO {1:1}
          +1 NAME <NAME_OF_REPOSITORY> {0:1} p.*
          +1 <<ADDRESS_STRUCTURE>> {0:1} p.*
          +1 <<NOTE_STRUCTURE>> {0:M} p.*
          +1 REFN <USER_REFERENCE_NUMBER> {0:M} p.*
          +1 RIN <AUTOMATED_RECORD_ID> {0:1} p.*
          +1 <<CHANGE_DATE>> {0:1} p.
        """
        repo = self.__find_or_create_repository(self.rid_map[line.token_text])

        state = CurrentState()
        state.repo = repo
        state.level = 1
        self.__parse_level(state, self.repo_parse_tbl, self.__ignore)

        self.__check_msgs(_("REPO (repository) Gramps ID %s") % 
                          repo.get_gramps_id(), state, repo)
        self.dbase.commit_repository(repo, self.trans, repo.change)

    def __repo_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.repo.set_name(line.data)

    def __repo_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.repo, state.level+1, state)

    def __repo_addr(self, line, state):
        """
        Parses the REPOsitory and HEADer COPR <ADDRESS_STRUCTURE>
        
        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        free_form = line.data

        sub_state = CurrentState(level=state.level + 1)
        sub_state.addr = gen.lib.Address()

        self.__parse_level(sub_state, self.parse_addr_tbl, self.__ignore)
        state.msg += sub_state.msg
        
        self.__merge_address(free_form, sub_state.addr, line, state)
        state.repo.add_address(sub_state.addr)

    def __repo_phon(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        address_list = state.repo.get_address_list()
        if address_list:
            address_list[0].set_phone(line.data)

    def __repo_www(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = gen.lib.Url()
        url.set_path(line.data)
        url.set_type(gen.lib.UrlType(gen.lib.UrlType.WEB_HOME))
        state.repo.add_url(url)

    def __repo_email(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = gen.lib.Url()
        url.set_path(line.data)
        url.set_type(gen.lib.UrlType(gen.lib.UrlType.EMAIL))
        state.repo.add_url(url)

    def __location_adr1(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        if state.location.get_street() != "":
            self.__add_msg(_("Warn: ADDR overwritten"), line, state)
        state.location.set_street(line.data)

    def __location_adr2(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_locality(line.data)

    def __location_city(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_city(line.data)

    def __location_stae(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_state(line.data)

    def __location_post(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_postal_code(line.data)

    def __location_ctry(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_country(line.data)

    def __location_phone(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = gen.lib.Location()
        state.location.set_phone(line.data)

    def __location_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.event:
            self.__parse_note(line, state.place, state.level, state)
        else:
            # This causes notes below SUBMitter to be ignored
            self.__not_recognized(line, state.level, state)

    def __optional_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.obj, state.level, state)

    #----------------------------------------------------------------------
    #
    # HEAD parsing
    #
    #----------------------------------------------------------------------

    def __parse_header(self):
        """
        Handling of the lines subordinate to the HEAD GEDCOM tag
        
         n HEAD                                          {1:1}
           +1 SOUR <APPROVED_SYSTEM_ID>                  {1:1}
             +2 VERS <VERSION_NUMBER>                    {0:1}
             +2 NAME <NAME_OF_PRODUCT>                   {0:1}
             +2 CORP <NAME_OF_BUSINESS>                  {0:1}
               +3 <<ADDRESS_STRUCTURE>>                  {0:1}
             +2 DATA <NAME_OF_SOURCE_DATA>               {0:1}
               +3 DATE <PUBLICATION_DATE>                {0:1}
               +3 COPR <COPYRIGHT_SOURCE_DATA>           {0:1}
           +1 DEST <RECEIVING_SYSTEM_NAME>               {0:1*}
           +1 DATE <TRANSMISSION_DATE>                   {0:1}
             +2 TIME <TIME_VALUE>                        {0:1}
           +1 SUBM @<XREF:SUBM>@                         {1:1}
           +1 SUBN @<XREF:SUBN>@                         {0:1}
           +1 FILE <FILE_NAME>                           {0:1}
           +1 COPR <COPYRIGHT_GEDCOM_FILE>               {0:1}
           +1 GEDC                                       {1:1}
             +2 VERS <VERSION_NUMBER>                    {1:1}
             +2 FORM <GEDCOM_FORM>                       {1:1}
           +1 CHAR <CHARACTER_SET>                       {1:1}
             +2 VERS <VERSION_NUMBER>                    {0:1}
           +1 LANG <LANGUAGE_OF_TEXT>                    {0:1}
           +1 PLAC                                       {0:1}
             +2 FORM <PLACE_HIERARCHY>                   {1:1}
           +1 NOTE <GEDCOM_CONTENT_DESCRIPTION>          {0:1}
             +2 [CONT|CONC] <GEDCOM_CONTENT_DESCRIPTION> {0:M}

          * NOTE: Submissions to the Family History Department for Ancestral
          File submission or for clearing temple ordinances must use a
          DESTination of ANSTFILE or TempleReady.
        
        """
        state = CurrentState(level=1)
        self.__parse_level(state, self.head_parse_tbl, self.__undefined)
        self.__check_msgs(_("Head (header)"), state, None)

    def __header_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.gedsource = self.gedmap.get_from_source_tag(line.data)
        if line.data.strip() in ["FTW", "FTM"]:
            self.is_ftw = True
        # We will use the approved system ID as the name of the generating
        # software, in case we do not get the name in the proper place
        self.genby = line.data
        if self.use_def_src:
            self.def_src.set_data_item(_("Approved system identification"), 
                                       "%s" % self.genby)
        sub_state = CurrentState(level=state.level+1)
        self.__parse_level(sub_state, self.header_sour_parse_tbl,
                           self.__undefined)
        state.msg += sub_state.msg
        # We can't produce the 'Generated by' statement till the end of the SOUR
        # level, because the name and version may come in any order
        if self.use_def_src:
            # feature request 2356: avoid genitive form
            self.def_src.set_data_item(_("Generated by"), "%s %s" %
                                       (self.genby, self.genvers))

    def __header_sour_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # This is where the name of the product that generated the GEDCOM file
        # should appear, and this will overwrite the approved system ID (if any)
        self.genby = line.data
        if self.use_def_src:
            self.def_src.set_data_item(_("Name of software product"), 
                                       self.genby)
        
    def __header_sour_vers(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.genvers = line.data
        if self.use_def_src:
            self.def_src.set_data_item(_("Version number of software product"),
                                       self.genvers)
        
    def __header_sour_corp(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        repo = gen.lib.Repository()
        sub_state = CurrentState(level=state.level + 1)
        sub_state.repo = repo
        self.__parse_level(sub_state, self.header_corp_addr, self.__undefined)
        state.msg += sub_state.msg

        if self.use_def_src:
            repo.set_name(_("Business that produced the product: %s") % 
                          line.data)
            rtype = gen.lib.RepositoryType()
            rtype.set((gen.lib.RepositoryType.CUSTOM, _('GEDCOM data')))
            repo.set_type(rtype)
            self.dbase.add_repository(repo, self.trans)
            repo_ref = gen.lib.RepoRef()
            repo_ref.set_reference_handle(repo.handle)
            mtype = gen.lib.SourceMediaType()
            mtype.set((gen.lib.SourceMediaType.UNKNOWN, ''))
            repo_ref.set_media_type(mtype)
            self.def_src.add_repo_reference(repo_ref)
        
    def __header_sour_data(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_data_item(_("Name of source data"), line.data)
        sub_state = CurrentState(level=state.level+1)
        self.__parse_level(sub_state, self.header_sour_data,
                           self.__undefined)
        state.msg += sub_state.msg
        
    def __header_sour_copr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_data_item(_("Copyright of source data"), line.data)
        
    def __header_sour_date(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            # Because there is a DATE tag, line.data is automatically converted
            # to a Date object before getting to this point, so it has to be
            # converted back to a string
            text_date = str(line.data)
            self.def_src.set_data_item(_("Publication date of source data"), 
                                       text_date)
        
    def __header_file(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            filename = os.path.basename(line.data).split('\\')[-1]
            # feature request 2356: avoid genitive form
            self.def_src.set_title(_("Import from %s") % filename)

    def __header_copr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_publication_info(line.data)

    def __header_subm(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        
        +1 SUBM @<XREF:SUBM>@  {1:1}
        This should be simply be a cross-reference to the correct Submitter 
        record. Note that there can be multiple Submitter records, so it is 
        necessary to remember which one should be applied.

        """
        self.subm = line.data[1:-1]
        sub_state = CurrentState(level=state.level+1)
        self.__parse_level(sub_state, self.header_subm, self.__ignore)
        state.msg += sub_state.msg

    def __header_subn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_data_item(_('Submission record identifier'), 
                                       line.token_text)

    def __header_lang(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_data_item(_('Language of GEDCOM text'), line.data)

    def __header_dest(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # FIXME: Gramps does not seem to produce a DEST line, so this processing
        # seems to be useless
        if self.genby == "GRAMPS":
            self.gedsource = self.gedmap.get_from_source_tag(line.data)

        # FIXME: This processing does not depend on DEST, so there seems to be
        # no reason for it to be placed here. Perhaps it is supposed to be after
        # all the SOUR levels have been processed, but self.genby was only
        # assigned by the initial SOUR tag, so this could have been done there.
        # Perhaps, as suggested by the text of the error message, it was
        # supposed to test whenther the_DEST_ was LEGACY, in which case the
        # coding is now wrong.
        if self.genby.upper() == "LEGACY":
            fname = os.path.basename(self.filename)
            WarningDialog(
               _("Import of GEDCOM file %s with DEST=%s, "
                 "could cause errors in the resulting database!")
                   % (fname, self.genby),
               _("Look for nameless events.")
               )
 
    def __header_char(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        #   +1 CHAR <CHARACTER_SET>                       {1:1}
        #     +2 VERS <VERSION_NUMBER>                    {0:1}
        encoding = line.data
        version = ""
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_VERS:
                version = line.data
                
        if self.use_def_src:
            if version == "":
                self.def_src.set_data_item(_('Character set'), encoding)
            else:
                self.def_src.set_data_item(_('Character set and version'), 
                                           "%s %s" % (encoding, version))
            
    def __header_gedc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_VERS:
                if line.data[0] != "5":
                    self.__add_msg(_("GEDCOM version not supported"), 
                                   line, state)
                if self.use_def_src:
                    self.def_src.set_data_item(_('GEDCOM version'), line.data)
            elif line.token == TOKEN_FORM:
                if line.data != "LINEAGE-LINKED":
                    self.__add_msg(_("GEDCOM form not supported"), line, state)
                if self.use_def_src:
                    self.def_src.set_data_item(_('GEDCOM form'), line.data)
            
    def __header_plac(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState(level=state.level+1)
        self.__parse_level(sub_state, self.place_form, self.__undefined)
        state.msg += sub_state.msg

    def __place_form(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.place_parser.parse_form(line)

    def __header_date(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        
        This processes the <TRANSMISSION_DATE>, i.e. the date when this [GEDCOM]
        transmission was created (as opposed to the date when the source data 
        that was used to create the transmission was published or created
        """
        # Because there is a DATE tag, line.data is automatically converted to a
        # Date object before getting to this point, so it has to be converted
        # back to a string
        tx_date = str(line.data)
        tx_time = ""
        line = self.__get_next_line()
        if self.__level_is_finished(line, state.level):
            pass
        elif line.token == TOKEN_TIME:
            tx_time = str(line.data)
            
        if self.use_def_src:
            if tx_time == "":
                self.def_src.set_data_item(_('Creation date of GEDCOM'), 
                                           tx_date)
            else:
                self.def_src.set_data_item(
                        _('Creation date and time of GEDCOM'), 
                        "%s %s" % (tx_date, tx_time))
                
    def __header_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.__parse_note(line, self.def_src, 2, state)

    def __header_subm_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_author(line.data)

    def __parse_note(self, line, obj, level, state):
        if line.token == TOKEN_RNOTE:
            # reference to a named note defined elsewhere
            #NOTE_STRUCTURE: =
            #  n  NOTE @<XREF:NOTE>@  {1:1}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}
            obj.add_note(self.__find_note_handle(self.nid_map[line.data]))
        else:
            # Embedded note
            #NOTE_STRUCTURE: =
            #  n  NOTE [<SUBMITTER_TEXT> | <NULL>]  {1:1}
            #    +1 [ CONC | CONT ] <SUBMITTER_TEXT>  {0:M}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}
            if not line.data:
                self.__add_msg(_("Empty note ignored"), line, state)
                self.__skip_subordinate_levels(level+1, state)
            else:
                new_note = gen.lib.Note(line.data)
                new_note.set_gramps_id(self.nid_map[""])
                new_note.set_handle(Utils.create_id())

                sub_state = CurrentState(level=state.level+1)
                sub_state.note = new_note
                self.__parse_level(sub_state, self.note_parse_tbl, 
                                   self.__undefined)
                state.msg += sub_state.msg

                self.dbase.commit_note(new_note, self.trans, new_note.change)
                obj.add_note(new_note.get_handle())

    #----------------------------------------------------------------------
    #
    # NOTE parsing
    #
    #----------------------------------------------------------------------

    def __parse_inline_note(self, line, level):
        """
        Handling of lines subordinate to the NOTE GEDCOM tag
        
        n @<XREF:NOTE>@ NOTE <SUBMITTER_TEXT>  {1:1}
          +1 [ CONC | CONT] <SUBMITTER_TEXT>  {0:M}
          +1 <<SOURCE_CITATION>>  {0:M}
          +1 REFN <USER_REFERENCE_NUMBER>  {0:M}
            +2 TYPE <USER_REFERENCE_TYPE>  {0:1}
          +1 RIN <AUTOMATED_RECORD_ID>  {0:1}
          +1 <<CHANGE_DATE>>  {0:1}
        """
        state = CurrentState(level=1)
        if not line.data and \
                self.nid_map.clean(line.token_text) not in self.nid_map.map():
            self.__add_msg(_("Empty note ignored"), line)
            self.__skip_subordinate_levels(level, state)
        else:
            gid = self.nid_map[line.token_text]
            handle = self.__find_note_handle(gid)
            new_note = gen.lib.Note(line.data)
            new_note.set_handle(handle)
            new_note.set_gramps_id(gid)

            sub_state = CurrentState(level=state.level)
            sub_state.note = new_note
            self.__parse_level(sub_state, self.note_parse_tbl, self.__undefined)
            state.msg += sub_state.msg

            self.dbase.commit_note(new_note, self.trans, new_note.change)
            self.__check_msgs(_("NOTE Gramps ID %s") % new_note.get_gramps_id(), 
                              state, None)

    def __note_chan(self, line, state):
        if state.note:
            self.__parse_change(line, state.note, state.level+1, state)
    
    def __parse_source_reference(self, citation, level, handle, state):
        """
        Read the data associated with a SOUR reference.
        """
        sub_state = CurrentState(level=level+1)
        sub_state.citation = citation
        sub_state.handle = handle
        self.__parse_level(sub_state, self.citation_parse_tbl, self.__ignore)
        state.msg += sub_state.msg
    
    def __parse_header_head(self):
        """
        Validate that this is a valid GEDCOM file.
        """
        line = self.__get_next_line()
        if line.token != TOKEN_HEAD:
            raise Errors.GedcomError("%s is not a GEDCOM file" % self.filename)
    
    def __parse_submission(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        
        Handling of lines subordinate to the level 0 SUMN (Submission) GEDCOM 
        tag
        
          n  @<XREF:SUBN>@ SUBN  {1:1]
            +1 SUBM @<XREF:SUBM>@ {0:1}
            +1 FAMF <NAME_OF_FAMILY_FILE>  {0:1}
            +1 TEMP <TEMPLE_CODE>  {0:1}
            +1 ANCE <GENERATIONS_OF_ANCESTORS>  {0:1}
            +1 DESC <GENERATIONS_OF_DESCENDANTS>  {0:1}
            +1 ORDI <ORDINANCE_PROCESS_FLAG>  {0:1}
            +1 RIN <AUTOMATED_RECORD_ID>  {0:1}
        """
        while True:
            line = self.__get_next_line()
            msg = ""
            if self.__level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_SUBM:
                msg = _("Submission: Submitter")
            elif line.token == TOKEN_UNKNOWN and line.token_text == "FAMF":
                msg = _("Submission: Family file")
            elif line.token == TOKEN_TEMP:
                msg = _("Submission: Temple code")
            elif line.token == TOKEN_UNKNOWN and line.token_text == "ANCE":
                msg = _("Submission: Generations of ancestors")
            elif line.token == TOKEN_UNKNOWN and line.token_text == "DESC":
                msg = _("Submission: Generations of descendants")
            elif line.token == TOKEN_UNKNOWN and line.token_text == "ORDI":
                msg = _("Submission: Ordinance process flag")
            else:
                self.__not_recognized(line, state.level+1, state)
                continue
                
            if self.use_def_src and msg != "":
                self.def_src.set_data_item(msg, line.data)
                self.dbase.commit_source(self.def_src, self.trans)
            
    def handle_source(self, line, level, state):
        """
        Handle the specified source, building a source reference to
        the object.
        """
        citation = gen.lib.Citation()
        if line.data and line.data[0] != "@":
            title = line.data
            handle = self.inline_srcs.get(title, Utils.create_id())
            src = gen.lib.Source()
            src.handle = handle
            src.gramps_id = self.dbase.find_next_source_gramps_id()
            self.inline_srcs[title] = handle
        else:
            src = self.__find_or_create_source(self.sid_map[line.data])
            # We need to set the title to the cross reference identifier of the
            # SOURce record, just in case we never find the source record. If we
            # din't find the source record, then the source object would have
            # got deleted by Chack and repair because the record is empty. If we
            # find the source record, the title is overwritten in
            # __source_title.
            src.set_title(line.data)
        self.dbase.commit_source(src, self.trans)
        self.__parse_source_reference(citation, level, src.handle, state)
        citation.set_reference_handle(src.handle)
        self.dbase.add_citation(citation, self.trans)
        return citation.handle

    def __parse_change(self, line, obj, level, state):
        """
        CHANGE_DATE:=

        >  n CHAN {1:1}
        >  +1 DATE <CHANGE_DATE> {1:1}
        >  +2 TIME <TIME_VALUE> {0:1}
        >  +1 <<NOTE_STRUCTURE>> {0:M}

        The Note structure is ignored, since we have nothing
        corresponding in GRAMPS.

        Based on the values calculated, attempt to convert to a valid
        change time using time.strptime. If this fails (and it shouldn't
        unless the value is meaningless and doesn't conform to the GEDCOM
        spec), the value is ignored.
        """
        tstr = None
        dstr = None
        dobj = None        
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, level):
                break
            elif line.token == TOKEN_TIME:
                tstr = line.data
            elif line.token == TOKEN_DATE:
                #Lexer converted already to Date object
                dobj = line.data
            elif line.token == TOKEN_NOTE:
                self.__skip_subordinate_levels(level+1, state)
            else:
                self.__not_recognized(line, level+1, state)

        # Attempt to convert the values to a valid change time
        if dobj:
            dstr = "%s %s %s" % (dobj.get_day(), dobj.get_month(),
                                 dobj.get_year())
            try:
                if tstr:
                    try:
                        tstruct = time.strptime("%s %s" % (dstr, tstr),
                                                "%d %m %Y %H:%M:%S")
                    except ValueError:
                        #seconds is optional in GEDCOM
                        tstruct = time.strptime("%s %s" % (dstr, tstr),
                                                "%d %m %Y %H:%M")
                else:
                    tstruct = time.strptime(dstr, "%d %m %Y")
                val = time.mktime(tstruct)
                obj.change = val
            except (ValueError, OverflowError):
                # parse of time structure failed, so ignore. According to the
                # Python manual: "The functions in this [time] module do not
                # handle dates and times before the epoch or far in the future.
                # The cut-off point in the future is determined by the C
                # library; for Unix, it is typically in 2038." If the time is
                # too far in the future, this gives OverflowError.
                pass
        
    def build_media_object(self, obj, form, filename, title, note):
        if isinstance(form, basestring) and form.lower() == "url":
            url = gen.lib.Url()
            url.set_path(filename)
            url.set_description(title)
            url.set_type(gen.lib.UrlType.WEB_HOME)
            obj.add_url(url)
        else:
            # to allow import of references to URLs (especially for import from
            # geni.com), do not try to find the files if they are blatently URLs
            res = urlparse(filename)
            if filename != '' and (res.scheme == '' or res.scheme == 'file'):
                (valid, path) = self.__find_file(filename, self.dir_path)
                if not valid:
                    self.__add_msg(_("Could not import %s") % filename)
                    path = filename.replace('\\', os.path.sep)
            else:
                path = filename
            photo_handle = self.media_map.get(path)
            if photo_handle is None:
                photo = gen.lib.MediaObject()
                photo.set_path(path)
                photo.set_description(title)
                full_path = os.path.abspath(path)
                if os.path.isfile(full_path):
                    photo.set_mime_type(gen.mime.get_type(full_path))
                else:
                    photo.set_mime_type(MIME_MAP.get(form.lower(), 'unknown'))
                self.dbase.add_object(photo, self.trans)
                self.media_map[path] = photo.handle
            else:
                photo = self.dbase.get_object_from_handle(photo_handle)
            oref = gen.lib.MediaRef()
            oref.set_reference_handle(photo.handle)
            if note:
                oref.add_note(note)
            obj.add_media_reference(oref)

    def __build_event_pair(self, state, event_type, event_map, description):
        """
        n TYPE <EVENT_DESCRIPTOR> {0:1} p.*
        n DATE <DATE_VALUE> {0:1} p.*/*
        n <<PLACE_STRUCTURE>> {0:1} p.*
        n <<ADDRESS_STRUCTURE>> {0:1} p.*
        n AGE <AGE_AT_EVENT> {0:1} p.*
        n AGNC <RESPONSIBLE_AGENCY> {0:1} p.*
        n CAUS <CAUSE_OF_EVENT> {0:1} p.*
        n <<SOURCE_CITATION>> {0:M} p.*
        n <<MULTIMEDIA_LINK>> {0:M} p.*, *
        n <<NOTE_STRUCTURE>> {0:M} p.
        """
        event = gen.lib.Event()
        event_ref = gen.lib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(event_type)

        if description and description != 'Y':
            event.set_description(description)
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.level = state.level + 1
        sub_state.event_ref = event_ref
        sub_state.event = event
        sub_state.person = state.person

        self.__parse_level(sub_state, event_map, self.__undefined)
        state.msg += sub_state.msg
        self.dbase.commit_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)
        return event_ref

    def __build_family_event_pair(self, state, event_type, event_map, 
                                 description):
        event = gen.lib.Event()
        event_ref = gen.lib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(event_type)
        if description and description != 'Y':
            event.set_description(description)

        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.family = state.family
        sub_state.level = state.level+1
        sub_state.event = event
        sub_state.event_ref = event_ref

        self.__parse_level(sub_state, event_map, self.__undefined)
        state.msg += sub_state.msg

        self.dbase.commit_event(event, self.trans)
        event_ref.set_reference_handle(event.handle)
        return event_ref

    def __extract_temple(self, line):
        def get_code(code):
            if LdsUtils.TEMPLES.is_valid_code(code):
                return code
            elif LdsUtils.TEMPLES.is_valid_name(code):
                return LdsUtils.TEMPLES.code(code)
        
        code = get_code(line.data)
        if code: 
            return code
        
        ## Not sure why we do this. Kind of ugly.
        code = get_code(line.data.split()[0])
        if code: 
            return code

        ## Okay we have no clue which temple this is.
        ## We should tell the user and store it anyway.
        self.__add_msg(_("Invalid temple code"), line, None)
        return line.data

    def __add_default_source(self, obj):
        """
        Add the default source to the object.
        """
        if self.use_def_src and len(obj.get_citation_list()) == 0:
            citation = gen.lib.Citation()
            citation.set_reference_handle(self.def_src.handle)
            self.dbase.add_citation(citation, self.trans)
            obj.add_citation(citation.handle)

    def __subm_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.res.set_name(line.data)

    def __subm_addr(self, line, state):
        """
        Parses the SUBMitter address structure

        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        free_form = line.data
        
        sub_state = CurrentState(level=state.level + 1)
        sub_state.location = state.res

        self.__parse_level(sub_state, self.parse_loc_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__merge_address(free_form, state.res, line, state)
        # Researcher is a sub-type of LocationBase, so get_street and set_street
        # which are used in routines called from self.parse_loc_tbl work fine.
        # Unfortunately, Researcher also has get_address and set_address, so we
        # need to copy the street into that.
        state.res.set_address(state.res.get_street())

    def __subm_phon(self, line, state):
        """
        n PHON <PHONE_NUMBER> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.res.set_phone(line.data)

    def __subm_email(self, line, state):
        """
        n EMAIL <ADDRESS_EMAIL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.res.set_email(line.data)

#-------------------------------------------------------------------------
#
# GedcomStageOne
#
#-------------------------------------------------------------------------
class GedcomStageOne(object):
    """
    The GedcomStageOne parser scans the file quickly, looking for a few things.
     This includes:

    1. Character set encoding
    2. Number of people and families in the list
    3. Child to family references, since Ancestry.com creates GEDCOM files 
       without the FAMC references.
    """
    __BAD_UTF16 = _("Your GEDCOM file is corrupted. "
                  "The file appears to be encoded using the UTF16 "
                  "character set, but is missing the BOM marker.")
    __EMPTY_GED = _("Your GEDCOM file is empty.")
    
    @staticmethod
    def __is_xref_value(value):
        """
        Return True if value is in the form of a XREF value. We assume that
        if we have a leading '@' character, then we are okay.
        """
        return value and value[0] == '@'
    
    def __init__(self, ifile):
        self.ifile = ifile
        self.famc = defaultdict(list)
        self.fams = defaultdict(list)
        self.enc = ""
        self.pcnt = 0
        self.lcnt = 0

    def __detect_file_decoder(self, input_file):
        """
        Detects the file encoding of the file by looking for a BOM 
        (byte order marker) in the GEDCOM file. If we detect a UTF-16
        encoded file, we must connect to a wrapper using the codecs
        package.
        """
        line = input_file.read(2)
        if line == "\xef\xbb":
            input_file.read(1)
            self.enc = "UTF8"
            return input_file
        elif line == "\xff\xfe":
            self.enc = "UTF16"
            input_file.seek(0)
            return codecs.EncodedFile(input_file, 'utf8', 'utf16')
        elif not line :
            raise Errors.GedcomError(self.__EMPTY_GED)
        elif line[0] == "\x00" or line[1] == "\x00":
            raise Errors.GedcomError(self.__BAD_UTF16)
        else:
            input_file.seek(0)
            return input_file

    def parse(self):
        """
        Parse the input file.
        """
        current_family_id = ""
        
        reader = self.__detect_file_decoder(self.ifile)

        for line in reader:
            line = line.strip()
            if not line:
                continue
            self.lcnt += 1

            data = line.split(None, 2) + ['']
            try:
                (level, key, value) = data[:3]
                value = value.strip()
                level = int(level)
                key = key.strip()
            except:
                LOG.warn(_("Invalid line %d in GEDCOM file.") % self.lcnt)
                continue

            if level == 0 and key[0] == '@':
                if value == ("FAM", "FAMILY") :
                    current_family_id = key.strip()[1:-1]
                elif value == ("INDI", "INDIVIDUAL"):
                    self.pcnt += 1
            elif key in ("HUSB", "HUSBAND", "WIFE") and \
                 self.__is_xref_value(value):
                self.fams[value[1:-1]].append(current_family_id)
            elif key in ("CHIL", "CHILD") and self.__is_xref_value(value):
                self.famc[value[1:-1]].append(current_family_id)
            elif key == 'CHAR' and not self.enc:
                assert(isinstance(value, basestring))
                self.enc = value

    def get_famc_map(self):
        """
        Return the Person to Child Family map
        """
        return self.famc

    def get_fams_map(self):
        """
        Return the Person to Family map (where the person is a spouse)
        """
        return self.fams

    def get_encoding(self):
        """
        Return the detected encoding
        """
        return self.enc.upper()

    def set_encoding(self, enc):
        """
        Forces the encoding
        """
        assert(isinstance(enc, basestring))
        self.enc = enc

    def get_person_count(self):
        """
        Return the number of INDI records found
        """
        return self.pcnt

    def get_line_count(self):
        """
        Return the number of lines in the file
        """
        return self.lcnt

#-------------------------------------------------------------------------
#
# make_gedcom_date
#
#-------------------------------------------------------------------------
def make_gedcom_date(subdate, calendar, mode, quality):
    """
    Convert a GRAMPS date structure into a GEDCOM compatible date.
    """
    retval = ""
    (day, mon, year) = subdate[0:3]
    (mmap, prefix) = CALENDAR_MAP.get(calendar, (MONTH, ""))
    if year < 0:
        year = -year
        bce = " B.C."
    else:
        bce = ""
    try:
        retval = __build_date_string(day, mon, year, bce, mmap)
    except IndexError:
        print "Month index error - %d" % mon
        retval = "%d%s" % (year, bce)
    if calendar == gen.lib.Date.CAL_SWEDISH:
        # If Swedish calendar use ISO for for date and append (swedish)
        # to indicate calandar
        if year and not mon and not day:
            retval = "%i" % (year)
        else:
            retval = "%i-%02i-%02i" % (year, mon, day)
        retval = retval + " (swedish)"
        # Skip prefix @#DUNKNOWN@ as it seems
        # not used in all other genealogy applications.
        # GRAMPS can handle it on import, but not with (swedish) appended
        # to explain what calendar, the unknown refer to
        prefix = ""
    if prefix:
        retval = "%s %s" % (prefix, retval)
    if mode in DATE_MODIFIER:
        retval = "%s %s" % (DATE_MODIFIER[mode], retval)
    if quality in DATE_QUALITY:
        retval = "%s %s" % (DATE_QUALITY[quality], retval)
    return retval

def __build_date_string(day, mon, year, bce, mmap):
    """
    Build a date string from the supplied information.
    """
    if day == 0:
        if mon == 0:
            retval = '%d%s' % (year, bce)
        elif year == 0:
            retval = '(%s)' % mmap[mon]
        else:
            retval = "%s %d%s" % (mmap[mon], year, bce)
    elif mon == 0:
        retval = '%d%s' % (year, bce)
    elif year == 0:
        retval = "(%d %s)" % (day, mmap[mon])
    else:
        retval = "%d %s %d%s" % (day, mmap[mon], year, bce)
    return retval
