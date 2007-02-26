#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

tokens = {
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
    "REPOSITORY"     : TOKEN_REPO,  "RESI"          : TOKEN_RESI,
    "RESIDENCE"      : TOKEN_RESI,  "RFN"           : TOKEN_RFN,
    "RIN"            : TOKEN_RIN,   "_SCHEMA"       : TOKEN__SCHEMA,
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
    "TRAILER"        : TOKEN_TRLR,  "TYPE"          : TOKEN_TYPE,
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
}
