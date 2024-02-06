#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2016       Paul R. Culley
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

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
value representing an enumerated type or a Gramps object (in the case of
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

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
import os
import re
import time

# from xml.parsers.expat import ParserCreate
from collections import defaultdict, OrderedDict
import string
import mimetypes
from io import StringIO, TextIOWrapper
from urllib.parse import urlparse

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".libgedcom")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.errors import GedcomError
from gramps.gen.lib import (
    Address,
    Attribute,
    AttributeType,
    ChildRef,
    ChildRefType,
    Citation,
    Date,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    FamilyRelType,
    LdsOrd,
    Location,
    Media,
    MediaRef,
    Name,
    NameType,
    Note,
    NoteType,
    Person,
    PersonRef,
    Place,
    RepoRef,
    Repository,
    RepositoryType,
    Researcher,
    Source,
    SourceMediaType,
    SrcAttribute,
    Surname,
    Tag,
    Url,
    UrlType,
    PlaceType,
    PlaceRef,
    PlaceName,
)
from gramps.gen.db import DbTxn
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.utils.file import media_path
from gramps.gen.utils.id import create_id
from gramps.gen.utils.lds import TEMPLES
from gramps.gen.utils.unknown import make_unknown, create_explanation_note
from gramps.gen.datehandler._dateparser import DateParser
from gramps.gen.db.dbconst import EVENT_KEY
from gramps.gen.lib.const import IDENTICAL
from gramps.gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gramps.gen.lib.urlbase import UrlBase
from gramps.plugins.lib.libplaceimport import PlaceImport
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.grampslocale import GrampsLocale

# -------------------------------------------------------------------------
#
# constants
#
# -------------------------------------------------------------------------
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
TOKEN_AGE = 112
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
TOKEN_FAX = 126
TOKEN_ROLE = 127
TOKEN__MAR = 128
TOKEN__MARN = 129
TOKEN__ADPN = 130
TOKEN__FSFTID = 131
TOKEN__PHOTO = 132
TOKEN__LINK = 133
TOKEN__PRIM = 134
TOKEN__JUST = 135
TOKEN__TEXT = 136
TOKEN__DATE = 137
TOKEN__APID = 138
TOKEN__CALLNAME = 139

TOKENS = {
    "_ADPN": TOKEN__ADPN,
    "_AKA": TOKEN__AKA,
    "_AKAN": TOKEN__AKA,
    "_ALIA": TOKEN_ALIA,
    "_ANCES_ORDRE": TOKEN_IGNORE,
    "_APID": TOKEN__APID,  # Ancestry.com database and page id
    "_CAT": TOKEN_IGNORE,
    "_CHUR": TOKEN_IGNORE,
    "_COMM": TOKEN__COMM,
    "_DATE": TOKEN__DATE,
    "_DATE2": TOKEN_IGNORE,
    "_DETAIL": TOKEN_IGNORE,
    "_EMAIL": TOKEN_EMAIL,
    "_E-MAIL": TOKEN_EMAIL,
    "_FREL": TOKEN__FREL,
    "_FSFTID": TOKEN__FSFTID,
    "_GODP": TOKEN__GODP,
    "_ITALIC": TOKEN_IGNORE,
    "_JUST": TOKEN__JUST,  # FTM Citation Quality Justification
    "_LEVEL": TOKEN_IGNORE,
    "_LINK": TOKEN__LINK,
    "_LKD": TOKEN__LKD,
    "_LOC": TOKEN__LOC,
    "_MAR": TOKEN__MAR,
    "_MARN": TOKEN__MARN,
    "_MARNM": TOKEN__MARNM,
    "_MASTER": TOKEN_IGNORE,
    "_MEDI": TOKEN_MEDI,
    "_MREL": TOKEN__MREL,
    "_NAME": TOKEN__NAME,
    "_PAREN": TOKEN_IGNORE,
    "_PHOTO": TOKEN__PHOTO,
    "_PLACE": TOKEN_IGNORE,
    "_PREF": TOKEN__PRIMARY,
    "_PRIM": TOKEN__PRIM,
    "_PRIMARY": TOKEN__PRIMARY,
    "_PRIV": TOKEN__PRIV,
    "_PUBLISHER": TOKEN_IGNORE,
    "_RUFNAME": TOKEN__CALLNAME,
    "_SCBK": TOKEN_IGNORE,
    "_SCHEMA": TOKEN__SCHEMA,
    "_SSHOW": TOKEN_IGNORE,
    "_STAT": TOKEN__STAT,
    "_TEXT": TOKEN__TEXT,
    "_TODO": TOKEN__TODO,
    "_TYPE": TOKEN_TYPE,
    "_UID": TOKEN__UID,
    "_URL": TOKEN_WWW,
    "_WITN": TOKEN__WITN,
    "_WTN": TOKEN__WTN,
    "ABBR": TOKEN_ABBR,
    "ABBREVIATION": TOKEN_ABBR,
    "ADDR": TOKEN_ADDR,
    "ADDRESS": TOKEN_ADDR,
    "ADDRESS1": TOKEN_ADR1,
    "ADDRESS2": TOKEN_ADR2,
    "ADOP": TOKEN_ADOP,
    "ADOPT": TOKEN_ADOP,
    "ADR1": TOKEN_ADR1,
    "ADR2": TOKEN_ADR2,
    "AFN": TOKEN_AFN,
    "AGE": TOKEN_AGE,
    "AGENCY": TOKEN_IGNORE,
    "AGNC": TOKEN_AGNC,
    "AKA": TOKEN__AKA,
    "ALIA": TOKEN_ALIA,
    "ALIAS": TOKEN_ALIA,
    "ANCI": TOKEN_ANCI,
    "ASSO": TOKEN_ASSO,
    "ASSOCIATES": TOKEN_ASSO,
    "AUTH": TOKEN_AUTH,
    "AUTHOR": TOKEN_AUTH,
    "BAPL": TOKEN_BAPL,
    "BAPTISM-LDS": TOKEN_BAPL,
    "BIRT": TOKEN_BIRT,
    "BIRTH": TOKEN_BIRT,
    "BLOB": TOKEN_BLOB,
    "CALL_NUMBER": TOKEN_CALN,
    "CALN": TOKEN_CALN,
    "CAUS": TOKEN_CAUS,
    "CAUSE": TOKEN_CAUS,
    "CHAN": TOKEN_CHAN,
    "CHANGE": TOKEN_CHAN,
    "CHAR": TOKEN_CHAR,
    "CHARACTER": TOKEN_CHAR,
    "CHIL": TOKEN_CHIL,
    "CHILD": TOKEN_CHIL,
    "CHILDREN_COUNT": TOKEN_NCHI,
    "CITY": TOKEN_CITY,
    "CONC": TOKEN_CONC,
    "CONCATENATION": TOKEN_CONC,
    "CONCATENTATE": TOKEN_CONC,
    "CONL": TOKEN_CONL,
    "CONT": TOKEN_CONT,
    "CONTINUATION": TOKEN_CONT,
    "CONTINUED": TOKEN_CONT,
    "COPR": TOKEN_COPR,
    "COPYRIGHT": TOKEN_COPR,
    "CORP": TOKEN_CORP,
    "CORPORATION": TOKEN_CORP,
    "COUNTRY": TOKEN_CTRY,
    "CTRY": TOKEN_CTRY,
    "DATA": TOKEN_DATA,
    "DATE": TOKEN_DATE,
    "DEAT": TOKEN_DEAT,
    "DEATH": TOKEN_DEAT,
    "DESI": TOKEN_DESI,
    "DEST": TOKEN_DEST,
    "DESTINATION": TOKEN_DEST,
    "EMAI": TOKEN_EMAIL,
    "EMAIL": TOKEN_EMAIL,
    "ENDL": TOKEN_ENDL,
    "ENDOWMENT": TOKEN_ENDL,
    "EVEN": TOKEN_EVEN,
    "EVENT": TOKEN_EVEN,
    "FACT": TOKEN_FACT,
    "FAM": TOKEN_FAM,
    "FAMC": TOKEN_FAMC,
    "FAMILY": TOKEN_FAM,
    "FAMILY_CHILD": TOKEN_FAMC,
    "FAMILY_SPOUSE": TOKEN_FAMS,
    "FAMS": TOKEN_FAMS,
    "FAX": TOKEN_FAX,
    "FILE": TOKEN_FILE,
    "FORM": TOKEN_FORM,
    "GEDC": TOKEN_GEDC,
    "GEDCOM": TOKEN_GEDC,
    "GIVEN_NAME": TOKEN_GIVN,
    "GIVN": TOKEN_GIVN,
    "HEAD": TOKEN_HEAD,
    "HEADER": TOKEN_HEAD,
    "HUSB": TOKEN_HUSB,
    "HUSBAND": TOKEN_HUSB,
    "INDI": TOKEN_INDI,
    "INDIVIDUAL": TOKEN_INDI,
    "LABEL": TOKEN_LABL,
    "LABL": TOKEN_LABL,
    "LANG": TOKEN_LANG,
    "LATI": TOKEN_LATI,
    "LONG": TOKEN_LONG,
    "MAP": TOKEN_MAP,
    "MEDI": TOKEN_MEDI,
    "MEDIA": TOKEN_MEDI,
    "NAME": TOKEN_NAME,
    "NAME_PREFIX": TOKEN_NPFX,
    "NAME_SUFFIX": TOKEN_NSFX,
    "NCHI": TOKEN_NCHI,
    "NICK": TOKEN_NICK,
    "NICKNAME": TOKEN_NICK,
    "NOTE": TOKEN_NOTE,
    "NPFX": TOKEN_NPFX,
    "NSFX": TOKEN_NSFX,
    "OBJE": TOKEN_OBJE,
    "OBJECT": TOKEN_OBJE,
    "OFFI": TOKEN_OFFI,
    "PAGE": TOKEN_PAGE,
    "PEDI": TOKEN_PEDI,
    "PEDIGREE": TOKEN_PEDI,
    "PERI": TOKEN_PERI,
    "PHON": TOKEN_PHON,
    "PHONE": TOKEN_PHON,
    "PHONE_NUMBER": TOKEN_PHON,
    "PLAC": TOKEN_PLAC,
    "PLACE": TOKEN_PLAC,
    "POST": TOKEN_POST,
    "POSTAL_CODE": TOKEN_POST,
    "PUBL": TOKEN_PUBL,
    "PUBLICATION": TOKEN_PUBL,
    "QUALITY_OF_DATA": TOKEN_QUAY,
    "QUAY": TOKEN_QUAY,
    "REFERENCE": TOKEN_REFN,
    "REFN": TOKEN_REFN,
    "RELA": TOKEN_RELA,
    "RELI": TOKEN_RELI,
    "RELIGION": TOKEN_RELI,
    "REPO": TOKEN_REPO,
    "REPOSITORY": TOKEN_REPO,
    "RESN": TOKEN_RESN,
    "RFN": TOKEN_RFN,
    "RIN": TOKEN_RIN,
    "ROLE": TOKEN_ROLE,
    "SCHEMA": TOKEN__SCHEMA,
    "SEX": TOKEN_SEX,
    "SLGC": TOKEN_SLGC,
    "SLGS": TOKEN_SLGS,
    "SOUR": TOKEN_SOUR,
    "SOURCE": TOKEN_SOUR,
    "SPFX": TOKEN_SPFX,
    "STAE": TOKEN_STAE,
    "STAT": TOKEN_STAT,
    "STATE": TOKEN_STAE,
    "STATUS": TOKEN_STAT,
    "SUBM": TOKEN_SUBM,
    "SUBMISSION": TOKEN_SUBN,
    "SUBMITTER": TOKEN_SUBM,
    "SUBN": TOKEN_SUBN,
    "SURN": TOKEN_SURN,
    "SURN_PREFIX": TOKEN_SPFX,
    "SURNAME": TOKEN_SURN,
    "TAXT": TOKEN_TAXT,
    "TEMP": TOKEN_TEMP,
    "TEMPLE": TOKEN_TEMP,
    "TEXT": TOKEN_TEXT,
    "TIME": TOKEN_TIME,
    "TITL": TOKEN_TITL,
    "TITLE": TOKEN_TITL,
    "TRAILER": TOKEN_TRLR,
    "TRLR": TOKEN_TRLR,
    "TYPE": TOKEN_TYPE,
    "URL": TOKEN_WWW,
    "VERS": TOKEN_VERS,
    "VERSION": TOKEN_VERS,
    "WIFE": TOKEN_WIFE,
    "WWW": TOKEN_WWW,
}

ADOPT_NONE = 0
ADOPT_EVENT = 1
ADOPT_FTW = 2
ADOPT_LEGACY = 3
ADOPT_PEDI = 4
ADOPT_STD = 5
CONC_OK = 0
CONC_BROKEN = 1
ALT_NAME_NONE = 0
ALT_NAME_STD = 1
ALT_NAME_ALIAS = 2
ALT_NAME_AKA = 3
ALT_NAME_EVENT_AKA = 4
ALT_NAME_UALIAS = 5
CALENDAR_NO = 0
CALENDAR_YES = 1
OBJE_NO = 0
OBJE_YES = 1
PREFIX_NO = 0
PREFIX_YES = 1
RESIDENCE_ADDR = 0
RESIDENCE_PLAC = 1
SOURCE_REFS_NO = 0
SOURCE_REFS_YES = 1

TYPE_BIRTH = ChildRefType()
TYPE_ADOPT = ChildRefType(ChildRefType.ADOPTED)
TYPE_FOSTER = ChildRefType(ChildRefType.FOSTER)

RELATION_TYPES = (ChildRefType.BIRTH, ChildRefType.UNKNOWN, ChildRefType.NONE)

PEDIGREE_TYPES = {
    "birth": ChildRefType(),
    "natural": ChildRefType(),
    "step": ChildRefType(ChildRefType.STEPCHILD),
    "adopted": TYPE_ADOPT,
    "foster": TYPE_FOSTER,
}

FTW_BAD_PLACE = [
    EventType.OCCUPATION,
    EventType.RELIGION,
    EventType.DEGREE,
]

MEDIA_MAP = {
    "audio": SourceMediaType.AUDIO,
    "book": SourceMediaType.BOOK,
    "card": SourceMediaType.CARD,
    "electronic": SourceMediaType.ELECTRONIC,
    "fiche": SourceMediaType.FICHE,
    "microfiche": SourceMediaType.FICHE,
    "microfilm": SourceMediaType.FICHE,
    "film": SourceMediaType.FILM,
    "magazine": SourceMediaType.MAGAZINE,
    "manuscript": SourceMediaType.MANUSCRIPT,
    "map": SourceMediaType.MAP,
    "newspaper": SourceMediaType.NEWSPAPER,
    "photo": SourceMediaType.PHOTO,
    "tombstone": SourceMediaType.TOMBSTONE,
    "grave": SourceMediaType.TOMBSTONE,
    "video": SourceMediaType.VIDEO,
}

OBJ_NOTETYPE = {
    "Attribute": NoteType.ATTRIBUTE,
    "Address": NoteType.ADDRESS,
    "Citation": NoteType.CITATION,
    "Event": NoteType.EVENT,
    "Family": NoteType.FAMILY,
    "LdsOrd": NoteType.LDS,
    "Media": NoteType.MEDIA,
    "Name": NoteType.GENERAL,
    "Place": NoteType.PLACE,
    "Person": NoteType.PERSON,
    "Repository": NoteType.REPO,
    "RepoRef": NoteType.REPOREF,
    "Source": NoteType.SOURCE,
    "PersonRef": NoteType.ASSOCIATION,
}

# -------------------------------------------------------------------------
#
# Integer to GEDCOM tag mappings for constants
#
# -------------------------------------------------------------------------
CALENDAR_MAP_GEDCOM2XML = {
    "FRENCH R": Date.CAL_FRENCH,
    "JULIAN": Date.CAL_JULIAN,
    "HEBREW": Date.CAL_HEBREW,
}

QUALITY_MAP = {
    "CAL": Date.QUAL_CALCULATED,
    "INT": Date.QUAL_CALCULATED,
    "EST": Date.QUAL_ESTIMATED,
}

SEX_MAP = {
    "F": Person.FEMALE,
    "M": Person.MALE,
    "X": Person.OTHER,
}

FAMILYCONSTANTEVENTS = {
    EventType.ANNULMENT: "ANUL",
    EventType.DIV_FILING: "DIVF",
    EventType.DIVORCE: "DIV",
    EventType.CENSUS: "CENS",
    EventType.ENGAGEMENT: "ENGA",
    EventType.MARR_BANNS: "MARB",
    EventType.MARR_CONTR: "MARC",
    EventType.MARR_LIC: "MARL",
    EventType.MARR_SETTL: "MARS",
    EventType.MARRIAGE: "MARR",
}

PERSONALCONSTANTEVENTS = {
    EventType.ADOPT: "ADOP",
    EventType.ADULT_CHRISTEN: "CHRA",
    EventType.BIRTH: "BIRT",
    EventType.DEATH: "DEAT",
    EventType.BAPTISM: "BAPM",
    EventType.BAR_MITZVAH: "BARM",
    EventType.BAS_MITZVAH: "BASM",
    EventType.BLESS: "BLES",
    EventType.BURIAL: "BURI",
    # EventType.CAUSE_DEATH      : "CAUS",  Not legal Gedcom since v5.0
    EventType.ORDINATION: "ORDN",
    EventType.CENSUS: "CENS",
    EventType.CHRISTEN: "CHR",
    EventType.CONFIRMATION: "CONF",
    EventType.CREMATION: "CREM",
    EventType.DEGREE: "_DEG",
    EventType.DIV_FILING: "DIVF",
    EventType.EDUCATION: "EDUC",
    EventType.ELECTED: "_ELEC",  # FTM custom tag
    EventType.EMIGRATION: "EMIG",
    EventType.FIRST_COMMUN: "FCOM",
    EventType.GRADUATION: "GRAD",
    EventType.MED_INFO: "_MDCL",
    EventType.MILITARY_SERV: "_MILT",
    EventType.NATURALIZATION: "NATU",
    EventType.NOB_TITLE: "TITL",
    EventType.NUM_MARRIAGES: "NMR",
    EventType.IMMIGRATION: "IMMI",
    EventType.OCCUPATION: "OCCU",
    EventType.PROBATE: "PROB",
    EventType.PROPERTY: "PROP",
    EventType.RELIGION: "RELI",
    EventType.RESIDENCE: "RESI",
    EventType.RETIREMENT: "RETI",
    EventType.WILL: "WILL",
}

FAMILYCONSTANTATTRIBUTES = {
    AttributeType.NUM_CHILD: "NCHI",
}

PERSONALCONSTANTATTRIBUTES = {
    AttributeType.CASTE: "CAST",
    AttributeType.DESCRIPTION: "DSCR",
    AttributeType.ID: "IDNO",
    AttributeType.NATIONAL: "NATI",
    AttributeType.NUM_CHILD: "NCHI",
    AttributeType.SSN: "SSN",
}

# -------------------------------------------------------------------------
#
# Gedcom to int constants
#
# -------------------------------------------------------------------------
LDS_STATUS = {
    "BIC": LdsOrd.STATUS_BIC,
    "CANCELED": LdsOrd.STATUS_CANCELED,
    "CHILD": LdsOrd.STATUS_CHILD,
    "CLEARED": LdsOrd.STATUS_CLEARED,
    "COMPLETED": LdsOrd.STATUS_COMPLETED,
    "DNS": LdsOrd.STATUS_DNS,
    "INFANT": LdsOrd.STATUS_INFANT,
    "PRE-1970": LdsOrd.STATUS_PRE_1970,
    "QUALIFIED": LdsOrd.STATUS_QUALIFIED,
    "DNS/CAN": LdsOrd.STATUS_DNS_CAN,
    "STILLBORN": LdsOrd.STATUS_STILLBORN,
    "SUBMITTED": LdsOrd.STATUS_SUBMITTED,
    "UNCLEARED": LdsOrd.STATUS_UNCLEARED,
}
# -------------------------------------------------------------------------
#
# Custom event friendly names.  These are non-standard GEDCOM "NEW_TAG"
# tags that start with an '_' i.e. "_DNA".  FTM has several of these, other
# programs may have more.  If a tag with this format is encountered it is
# checked in this table for a "friendly" name translation and thereafter is
# displayed and exported as such.  If the tag is NOT in this table and not
# otherwise handled by the code, the tag itself is used for display and
# export.  For example "_XYZ" is not in the table and will be displayed as
# "_XYZ" and exported as an EVEN.TYPE=_XYZ
# As Custom entries, they do not appear in Gramps Events add choice unless
# already imported via GEDCOM.
#
# -------------------------------------------------------------------------
CUSTOMEVENTTAGS = {
    "_CIRC": _("Circumcision"),
    "_COML": _("Common Law Marriage"),
    "_DEST": _("Destination"),
    "_DNA": _("DNA"),
    "_DCAUSE": _("Cause of Death"),
    "_EMPLOY": _("Employment"),
    "_EXCM": _("Excommunication"),
    "_EYC": _("Eye Color"),
    "_FUN": _("Funeral"),
    "_HEIG": _("Height"),
    "_INIT": _("Initiatory (LDS)"),
    "_MILTID": _("Military ID"),
    "_MISN": _("Mission (LDS)"),
    "_NAMS": _("Namesake"),
    "_ORDI": _("Ordinance"),
    "_ORIG": _("Origin"),
    "_SEPR": _("Separation"),  # Applies to Families
    "_WEIG": _("Weight"),
}
# table for skipping illegal control chars in GEDCOM import
# Only 09, 0A, 0D are allowed.
STRIP_DICT = dict.fromkeys(list(range(9)) + list(range(11, 13)) + list(range(14, 32)))
# The C1 Control characters are not treated in Latin-1 (ISO-8859-1) as
# undefined, but if they have been used, the file is probably supposed to be
# cp1252
DEL_AND_C1 = dict.fromkeys(list(range(0x7F, 0x9F)))

# -------------------------------------------------------------------------
#
# GEDCOM events to Gramps events conversion
#
# -------------------------------------------------------------------------
GED_TO_GRAMPS_EVENT = {}
for __val, __key in PERSONALCONSTANTEVENTS.items():
    if __key != "":
        GED_TO_GRAMPS_EVENT[__key] = __val

for __val, __key in FAMILYCONSTANTEVENTS.items():
    if __key != "":
        GED_TO_GRAMPS_EVENT[__key] = __val

GED_TO_GRAMPS_ATTR = {}
for __val, __key in PERSONALCONSTANTATTRIBUTES.items():
    if __key != "":
        GED_TO_GRAMPS_ATTR[__key] = __val

# -------------------------------------------------------------------------
#
# GEDCOM Date Constants
#
# -------------------------------------------------------------------------
HMONTH = [
    "",
    "TSH",
    "CSH",
    "KSL",
    "TVT",
    "SHV",
    "ADR",
    "ADS",
    "NSN",
    "IYR",
    "SVN",
    "TMZ",
    "AAV",
    "ELL",
]

FMONTH = [
    "",
    "VEND",
    "BRUM",
    "FRIM",
    "NIVO",
    "PLUV",
    "VENT",
    "GERM",
    "FLOR",
    "PRAI",
    "MESS",
    "THER",
    "FRUC",
    "COMP",
]

MONTH = [
    "",
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]

CALENDAR_MAP = {
    Date.CAL_HEBREW: (HMONTH, "@#DHEBREW@"),
    Date.CAL_FRENCH: (FMONTH, "@#DFRENCH R@"),
    Date.CAL_JULIAN: (MONTH, "@#DJULIAN@"),
    Date.CAL_SWEDISH: (MONTH, "@#DUNKNOWN@"),
}

CALENDAR_MAP_PARSESTRING = {
    Date.CAL_HEBREW: " (h)",
    Date.CAL_FRENCH: " (f)",
    Date.CAL_JULIAN: " (j)",
    Date.CAL_SWEDISH: " (s)",
}

# how wrong calendar use is shown
CALENDAR_MAP_WRONGSTRING = {
    Date.CAL_HEBREW: " <hebrew>",
    Date.CAL_FRENCH: " <french rep>",
    Date.CAL_JULIAN: " <julian>",
    Date.CAL_SWEDISH: " <swedish>",
}

DATE_MODIFIER = {
    Date.MOD_ABOUT: "ABT",
    Date.MOD_BEFORE: "BEF",
    Date.MOD_AFTER: "AFT",
    Date.MOD_FROM: "FROM",
    Date.MOD_TO: "TO",
    # Date.MOD_INTERPRETED : "INT",
}

DATE_QUALITY = {
    Date.QUAL_CALCULATED: "CAL",
    Date.QUAL_ESTIMATED: "EST",
}

# -------------------------------------------------------------------------
#
# regular expressions
#
# -------------------------------------------------------------------------
NOTE_RE = re.compile(r"\s*\d+\s+\@(\S+)\@\s+NOTE(.*)$")
CONT_RE = re.compile(r"\s*\d+\s+CONT\s?(.*)$")
CONC_RE = re.compile(r"\s*\d+\s+CONC\s?(.*)$")
PERSON_RE = re.compile(r"\s*\d+\s+\@(\S+)\@\s+INDI(.*)$")
MOD = re.compile(r"\s*(INT|EST|CAL)\s+(.*)$")
CAL = re.compile(r"\s*(ABT|BEF|AFT|FROM|TO)?\s*@#D?([^@]+)@\s*(.*)$")
RANGE = re.compile(r"\s*BET\s+@#D?([^@]+)@\s*(.*)\s+AND\s+@#D?([^@]+)@\s*(.*)$")
RANGE1 = re.compile(r"\s*BET\s+\s*(.*)\s+AND\s+@#D?([^@]+)@\s*(.*)$")
RANGE2 = re.compile(r"\s*BET\s+@#D?([^@]+)@\s*(.*)\s+AND\s+\s*(.*)$")
SPAN = re.compile(r"\s*FROM\s+@#D?([^@]+)@\s*(.*)\s+TO\s+@#D?([^@]+)@\s*(.*)$")
SPAN1 = re.compile(r"\s*FROM\s+\s*(.*)\s+TO\s+@#D?([^@]+)@\s*(.*)$")
SPAN2 = re.compile(r"\s*FROM\s+@#D?([^@]+)@\s*(.*)\s+TO\s+\s*(.*)$")
NAME_RE = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
SURNAME_RE = re.compile(r"/([^/]*)/([^/]*)")


# -----------------------------------------------------------------------
#
# GedcomDateParser
#
# -----------------------------------------------------------------------
class GedcomDateParser(DateParser):
    """Parse the dates"""

    month_to_int = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    _locale = GrampsLocale(lang="en_US")  # no register_datehandler here

    def dhformat_changed(self):
        """Allow overriding so a subclass can modify it"""
        self.dhformat = "%m/%d/%y"


# -------------------------------------------------------------------------
#
# Lexer - serves as the lexical analysis engine
#
# -------------------------------------------------------------------------
class Lexer:
    """low level line reading and early parsing"""

    def __init__(self, ifile, __add_msg):
        self.ifile = ifile
        self.current_list = []
        self.eof = False
        self.cnv = None
        self.cnt = 0
        self.index = 0
        self.func_map = {
            TOKEN_CONT: self.__fix_token_cont,
            TOKEN_CONC: self.__fix_token_conc,
        }
        self.__add_msg = __add_msg

    def readline(self):
        """read a line from file with possibility of putting it back"""
        if len(self.current_list) <= 1 and not self.eof:
            self.__readahead()
        try:
            return GedLine(self.current_list.pop())
        except:
            LOG.debug("Error in reading Gedcom line", exc_info=True)
            return None

    def __fix_token_cont(self, data):
        line = self.current_list[0]
        new_value = line[2] + "\n" + data[2]
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
            new_value = line[2] + " " + data[2]
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

            original_line = line
            try:
                # According to the GEDCOM 5.5 standard,
                # Chapter 1 subsection Grammar "leading whitespace preceeding
                # a GEDCOM line should be ignored"
                # We will also strip the terminator which is any combination
                # of carriage_return and line_feed
                line = line.lstrip(" ").rstrip("\n\r")
                # split into level+delim+rest
                line = line.partition(" ")
                level = int(line[0])
                # there should only be one space after the level,
                # but we can ignore more,
                line = line[2].lstrip(" ")
                # then split into tag+delim+line_value
                # or xfef_id+delim+rest
                # the xref_id can have spaces in it
                if line.startswith("@"):
                    line = line.split("@", 2)
                    # line is now [None, alphanum+pointer_string, rest]
                    tag = "@" + line[1] + "@"
                    line_value = line[2].lstrip()
                    # Ignore meaningless @IDENT@ on CONT or CONC line
                    # as noted at http://www.tamurajones.net/IdentCONT.xhtml
                    if line_value.lstrip().startswith(
                        "CONT "
                    ) or line_value.lstrip().startswith("CONC "):
                        line = line_value.lstrip().partition(" ")
                        tag = line[0]
                        line_value = line[2]
                else:
                    line = line.partition(" ")
                    tag = line[0]
                    line_value = line[2]
            except:
                problem = _("Line ignored ")
                text = original_line.rstrip("\n\r")
                prob_width = 66
                problem = problem.ljust(prob_width)[0 : (prob_width - 1)]
                text = text.replace("\n", "\n".ljust(prob_width + 22))
                message = "%s              %s" % (problem, text)
                self.__add_msg(message)
                continue

            # Need to un-double '@' See Gedcom 5.5 spec 'any_char'
            line_value = line_value.replace("@@", "@")
            token = TOKENS.get(tag, TOKEN_UNKNOWN)
            data = (level, token, line_value, tag, self.index)

            func = self.func_map.get(data[1])
            if func:
                func(data)
            else:
                # There will normally only be one space between tag and
                # line_value, but in case there is more then one, remove extra
                # spaces after CONC/CONT processing
                # Also, Gedcom spec says there should be no spaces at end of
                # line, however some programs put them there (FTM), so let's
                # leave them in place.
                data = data[:2] + (data[2].lstrip(),) + data[3:]
                self.current_list.insert(0, data)

    def clean_up(self):
        """
        Break circular references to parsing methods stored in dictionaries
        to aid garbage collection
        """
        for key in list(self.func_map.keys()):
            del self.func_map[key]
        del self.func_map


# -----------------------------------------------------------------------
#
# GedLine - represents a tokenized version of a GEDCOM line
#
# -----------------------------------------------------------------------
class GedLine:
    """
    GedLine is a class the represents a GEDCOM line. The form of a  GEDCOM line
    is:

    <LEVEL> <TOKEN> <TEXT>

    This gets parsed into

    Line Number, Level, Token Value, Token Text, and Data

    Data is dependent on the context the Token Value. For most of tokens,
    this is just a text string. However, for certain tokens where we know
    the context, we can provide some value. The current parsed tokens are:

    TOKEN_DATE   - Date
    TOKEN_SEX    - Person gender item
    TOEKN_UKNOWN - Check to see if this is a known event
    """

    __DATE_CNV = GedcomDateParser()

    @staticmethod
    def __extract_date(text):
        """
        Converts the specified text to a Date object.
        """
        dateobj = Date()
        # Horrible hack for importing illegal GEDCOM from Apple Macintosh
        # Classic 'Gene' program
        text = text.replace("BET ABT", "EST BET")

        # extract out the MOD line
        match = MOD.match(text)
        mod = ""
        if match:
            (mod, text) = match.groups()
            qual = QUALITY_MAP.get(mod, Date.QUAL_NONE)
            mod += " "
        else:
            qual = Date.QUAL_NONE

        # parse the range if we match, if so, return
        match = RANGE.match(text)
        match1 = RANGE1.match(text)
        match2 = RANGE2.match(text)
        if match or match1 or match2:
            if match:
                (cal1, data1, cal2, data2) = match.groups()
            elif match1:
                cal1 = Date.CAL_GREGORIAN
                (data1, cal2, data2) = match1.groups()
            elif match2:
                cal2 = Date.CAL_GREGORIAN
                (cal1, data1, data2) = match2.groups()
            cal1 = CALENDAR_MAP_GEDCOM2XML.get(cal1, Date.CAL_GREGORIAN)
            cal2 = CALENDAR_MAP_GEDCOM2XML.get(cal2, Date.CAL_GREGORIAN)
            if cal1 != cal2:
                # not supported by GRAMPS, import as text, we construct a string
                # that the parser will not parse as a correct date
                return GedLine.__DATE_CNV.parse(
                    "%sbetween %s%s and %s%s"
                    % (
                        mod,
                        data1,
                        CALENDAR_MAP_WRONGSTRING.get(cal1, ""),
                        CALENDAR_MAP_WRONGSTRING.get(cal2, ""),
                        data2,
                    )
                )

            # add hebrew, ... calendar so that months are recognized
            data1 += CALENDAR_MAP_PARSESTRING.get(cal1, "")
            data2 += CALENDAR_MAP_PARSESTRING.get(cal2, "")
            start = GedLine.__DATE_CNV.parse(data1)
            stop = GedLine.__DATE_CNV.parse(data2)
            dateobj.set(
                Date.QUAL_NONE,
                Date.MOD_RANGE,
                cal1,
                start.get_start_date() + stop.get_start_date(),
            )
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
                cal1 = Date.CAL_GREGORIAN
                (data1, cal2, data2) = match1.groups()
            elif match2:
                cal2 = Date.CAL_GREGORIAN
                (cal1, data1, data2) = match2.groups()
            cal1 = CALENDAR_MAP_GEDCOM2XML.get(cal1, Date.CAL_GREGORIAN)
            cal2 = CALENDAR_MAP_GEDCOM2XML.get(cal2, Date.CAL_GREGORIAN)
            if cal1 != cal2:
                # not supported by GRAMPS, import as text, we construct a string
                # that the parser will not parse as a correct date
                return GedLine.__DATE_CNV.parse(
                    "%sfrom %s%s to %s%s"
                    % (
                        mod,
                        data1,
                        CALENDAR_MAP_WRONGSTRING.get(cal1, ""),
                        CALENDAR_MAP_WRONGSTRING.get(cal2, ""),
                        data2,
                    )
                )
            # add hebrew, ... calendar so that months are recognized
            data1 += CALENDAR_MAP_PARSESTRING.get(cal1, "")
            data2 += CALENDAR_MAP_PARSESTRING.get(cal2, "")
            start = GedLine.__DATE_CNV.parse(data1)
            stop = GedLine.__DATE_CNV.parse(data2)
            dateobj.set(
                Date.QUAL_NONE,
                Date.MOD_SPAN,
                cal1,
                start.get_start_date() + stop.get_start_date(),
            )
            dateobj.set_quality(qual)
            return dateobj

        match = CAL.match(text)
        if match:
            (abt, call, data) = match.groups()
            call = CALENDAR_MAP_GEDCOM2XML.get(call, Date.CAL_GREGORIAN)
            data += CALENDAR_MAP_PARSESTRING.get(call, "")
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
        self.data = str(data[2])

        if self.level == 0:
            if (
                self.token_text
                and self.token_text[0] == "@"
                and self.token_text[-1] == "@"
            ):
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
            self.data = SEX_MAP.get(self.data.strip()[0], Person.UNKNOWN)
        except:
            self.data = Person.UNKNOWN

    def calc_date(self):
        """
        Converts the data field to a Date object
        """
        self.data = self.__extract_date(self.data)
        self.token = TOKEN_DATE

    def calc_unknown(self):
        """
        Checks to see if the token maps a known GEDCOM event. If so, we
        change the type from UNKNOWN to TOKEN_GEVENT (gedcom event), and
        the data is assigned to the associated Gramps EventType
        """
        token = GED_TO_GRAMPS_EVENT.get(self.token_text)
        if token:
            event = Event()
            event.set_description(self.data)
            event.set_type(token)
            self.token = TOKEN_GEVENT
            self.data = event
        else:
            token = GED_TO_GRAMPS_ATTR.get(self.token_text)
            if token:
                attr = Attribute()
                attr.set_value(self.data)
                attr.set_type(token)
                self.token = TOKEN_ATTR
                self.data = attr

    def calc_note(self):
        """look for a note xref @N0001@"""
        gid = self.data.strip()
        if len(gid) > 2 and gid[0] == "@" and gid[-1] == "@":
            self.token = TOKEN_RNOTE
            self.data = gid[1:-1]

    def calc_nchi(self):
        """set attribute for number of children"""
        attr = Attribute()
        attr.set_value(self.data)
        attr.set_type(AttributeType.NUM_CHILD)
        self.data = attr
        self.token = TOKEN_ATTR

    def calc_attr(self):
        """set attribure for general attributes"""
        attr = Attribute()
        attr.set_value(self.data)
        attr.set_type((AttributeType.CUSTOM, self.token_text))
        self.data = attr
        self.token = TOKEN_ATTR

    def __repr__(self):
        return "%d: %d (%d:%s) %s" % (
            self.line,
            self.level,
            self.token,
            self.token_text,
            self.data,
        )


_MAP_DATA = {
    TOKEN_UNKNOWN: GedLine.calc_unknown,
    TOKEN_DATE: GedLine.calc_date,
    TOKEN__DATE: GedLine.calc_date,
    TOKEN_SEX: GedLine.calc_sex,
    TOKEN_NOTE: GedLine.calc_note,
    TOKEN_NCHI: GedLine.calc_nchi,
    TOKEN__STAT: GedLine.calc_attr,
    TOKEN__UID: GedLine.calc_attr,
    TOKEN_AFN: GedLine.calc_attr,
    TOKEN__FSFTID: GedLine.calc_attr,
}


# -------------------------------------------------------------------------
#
# File Readers
#
# -------------------------------------------------------------------------
class BaseReader:
    """base char level reader"""

    def __init__(self, ifile, encoding, __add_msg):
        self.ifile = ifile
        self.enc = encoding
        self.__add_msg = __add_msg

    def reset(self):
        """return to beginning"""
        self.ifile.seek(0)

    def readline(self):
        """Read a single line"""
        raise NotImplementedError()

    def report_error(self, problem, line):
        """Create an error message"""
        line = line.rstrip("\n\r")
        prob_width = 66
        problem = problem.ljust(prob_width)[0 : (prob_width - 1)]
        text = line.replace("\n", "\n".ljust(prob_width + 22))
        message = "%s               %s" % (problem, text)
        self.__add_msg(message)


class UTF8Reader(BaseReader):
    """The main UTF-8 reader, uses Python for char handling"""

    def __init__(self, ifile, __add_msg, enc):
        BaseReader.__init__(self, ifile, enc, __add_msg)
        self.reset()
        if enc == "UTF_8_SIG":
            self.ifile = TextIOWrapper(
                ifile, encoding="utf_8_sig", errors="replace", newline=None
            )
        else:
            self.ifile = TextIOWrapper(
                ifile, encoding="utf_8", errors="replace", newline=None
            )

    def readline(self):
        line = self.ifile.readline()
        return line.translate(STRIP_DICT)


class UTF16Reader(BaseReader):
    """The main UTF-16 reader, uses Python for char handling"""

    def __init__(self, ifile, __add_msg):
        BaseReader.__init__(self, ifile, "UTF16", __add_msg)
        self.ifile = TextIOWrapper(
            ifile, encoding="utf_16", errors="replace", newline=None
        )
        self.reset()

    def readline(self):
        line = self.ifile.readline()
        return line.translate(STRIP_DICT)


class AnsiReader(BaseReader):
    """The main ANSI (latin1) reader, uses Python for char handling"""

    def __init__(self, ifile, __add_msg):
        BaseReader.__init__(self, ifile, "latin1", __add_msg)
        self.ifile = TextIOWrapper(
            ifile, encoding="latin1", errors="replace", newline=None
        )

    def readline(self):
        line = self.ifile.readline()
        if line.translate(DEL_AND_C1) != line:
            self.report_error(
                "DEL or C1 control chars in line did you mean " "CHAR cp1252??", line
            )
        return line.translate(STRIP_DICT)


class CP1252Reader(BaseReader):
    """The extra credit CP1252 reader, uses Python for char handling"""

    def __init__(self, ifile, __add_msg):
        BaseReader.__init__(self, ifile, "cp1252", __add_msg)
        self.ifile = TextIOWrapper(
            ifile, encoding="cp1252", errors="replace", newline=None
        )

    def readline(self):
        line = self.ifile.readline()
        return line.translate(STRIP_DICT)


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
    ?: should we allow TAB, as a Gramps extension?
    """

    __printable_ascii = list(map(chr, list(range(32, 127))))  # up thru 126
    #                            LF  CR  Esc GS  RS  US
    __use_ASCII = list(map(chr, [10, 13, 27, 29, 30, 31])) + __printable_ascii

    # mappings of single byte ANSEL codes to unicode
    __onebyte = {
        b"\xA1": "\u0141",
        b"\xA2": "\u00d8",
        b"\xA3": "\u0110",
        b"\xA4": "\u00de",
        b"\xA5": "\u00c6",
        b"\xA6": "\u0152",
        b"\xA7": "\u02b9",
        b"\xA8": "\u00b7",
        b"\xA9": "\u266d",
        b"\xAA": "\u00ae",
        b"\xAB": "\u00b1",
        b"\xAC": "\u01a0",
        b"\xAD": "\u01af",
        b"\xAE": "\u02bc",
        b"\xB0": "\u02bb",
        b"\xB1": "\u0142",
        b"\xB2": "\u00f8",
        b"\xB3": "\u0111",
        b"\xB4": "\u00fe",
        b"\xB5": "\u00e6",
        b"\xB6": "\u0153",
        b"\xB7": "\u02ba",
        b"\xB8": "\u0131",
        b"\xB9": "\u00a3",
        b"\xBA": "\u00f0",
        b"\xBC": "\u01a1",
        b"\xBD": "\u01b0",
        b"\xBE": "\u25a1",
        b"\xBF": "\u25a0",
        b"\xC0": "\u00b0",
        b"\xC1": "\u2113",
        b"\xC2": "\u2117",
        b"\xC3": "\u00a9",
        b"\xC4": "\u266f",
        b"\xC5": "\u00bf",
        b"\xC6": "\u00a1",
        b"\xC7": "\u00df",
        b"\xC8": "\u20ac",
        b"\xCD": "\u0065",
        b"\xCE": "\u006f",
        b"\xCF": "\u00df",
    }

    # combining forms (in ANSEL, they precede the modified ASCII character
    # whereas the unicode combining term follows the character modified
    # Note: unicode allows multiple modifiers, but ANSEL may not (TDB?),
    # so we ignore multiple combining forms in this module
    #  8d & 8e are zero-width joiner (ZWJ), and zero-width non-joiner ZWNJ
    #  (strange things) probably not commonly found in our needs, unless one
    #   starts writing persian (or???) poetry in ANSEL
    __acombiners = {
        b"\x8D": "\u200d",
        b"\x8E": "\u200c",
        b"\xE0": "\u0309",
        b"\xE1": "\u0300",
        b"\xE2": "\u0301",
        b"\xE3": "\u0302",
        b"\xE4": "\u0303",
        b"\xE5": "\u0304",
        b"\xE6": "\u0306",
        b"\xE7": "\u0307",
        b"\xE8": "\u0308",
        b"\xE9": "\u030c",
        b"\xEA": "\u030a",
        b"\xEB": "\ufe20",
        b"\xEC": "\ufe21",
        b"\xED": "\u0315",
        b"\xEE": "\u030b",
        b"\xEF": "\u0310",
        b"\xF0": "\u0327",
        b"\xF1": "\u0328",
        b"\xF2": "\u0323",
        b"\xF3": "\u0324",
        b"\xF4": "\u0325",
        b"\xF5": "\u0333",
        b"\xF6": "\u0332",
        b"\xF7": "\u0326",
        b"\xF8": "\u031c",
        b"\xF9": "\u032e",
        b"\xFA": "\ufe22",
        b"\xFB": "\ufe23",
        b"\xFC": "\u0338",
        b"\xFE": "\u0313",
    }

    # mappings of two byte (precomposed forms) ANSEL codes to unicode
    __twobyte = {
        b"\xE0\x41": "\u1ea2",
        b"\xE0\x45": "\u1eba",
        b"\xE0\x49": "\u1ec8",
        b"\xE0\x4F": "\u1ece",
        b"\xE0\x55": "\u1ee6",
        b"\xE0\x59": "\u1ef6",
        b"\xE0\x61": "\u1ea3",
        b"\xE0\x65": "\u1ebb",
        b"\xE0\x69": "\u1ec9",
        b"\xE0\x6F": "\u1ecf",
        b"\xE0\x75": "\u1ee7",
        b"\xE0\x79": "\u1ef7",
        b"\xE1\x41": "\u00c0",
        b"\xE1\x45": "\u00c8",
        b"\xE1\x49": "\u00cc",
        b"\xE1\x4F": "\u00d2",
        b"\xE1\x55": "\u00d9",
        b"\xE1\x57": "\u1e80",
        b"\xE1\x59": "\u1ef2",
        b"\xE1\x61": "\u00e0",
        b"\xE1\x65": "\u00e8",
        b"\xE1\x69": "\u00ec",
        b"\xE1\x6F": "\u00f2",
        b"\xE1\x75": "\u00f9",
        b"\xE1\x77": "\u1e81",
        b"\xE1\x79": "\u1ef3",
        b"\xE2\x41": "\u00c1",
        b"\xE2\x43": "\u0106",
        b"\xE2\x45": "\u00c9",
        b"\xE2\x47": "\u01f4",
        b"\xE2\x49": "\u00cd",
        b"\xE2\x4B": "\u1e30",
        b"\xE2\x4C": "\u0139",
        b"\xE2\x4D": "\u1e3e",
        b"\xE2\x4E": "\u0143",
        b"\xE2\x4F": "\u00d3",
        b"\xE2\x50": "\u1e54",
        b"\xE2\x52": "\u0154",
        b"\xE2\x53": "\u015a",
        b"\xE2\x55": "\u00da",
        b"\xE2\x57": "\u1e82",
        b"\xE2\x59": "\u00dd",
        b"\xE2\x5A": "\u0179",
        b"\xE2\x61": "\u00e1",
        b"\xE2\x63": "\u0107",
        b"\xE2\x65": "\u00e9",
        b"\xE2\x67": "\u01f5",
        b"\xE2\x69": "\u00ed",
        b"\xE2\x6B": "\u1e31",
        b"\xE2\x6C": "\u013a",
        b"\xE2\x6D": "\u1e3f",
        b"\xE2\x6E": "\u0144",
        b"\xE2\x6F": "\u00f3",
        b"\xE2\x70": "\u1e55",
        b"\xE2\x72": "\u0155",
        b"\xE2\x73": "\u015b",
        b"\xE2\x75": "\u00fa",
        b"\xE2\x77": "\u1e83",
        b"\xE2\x79": "\u00fd",
        b"\xE2\x7A": "\u017a",
        b"\xE2\xA5": "\u01fc",
        b"\xE2\xB5": "\u01fd",
        b"\xE3\x41": "\u00c2",
        b"\xE3\x43": "\u0108",
        b"\xE3\x45": "\u00ca",
        b"\xE3\x47": "\u011c",
        b"\xE3\x48": "\u0124",
        b"\xE3\x49": "\u00ce",
        b"\xE3\x4A": "\u0134",
        b"\xE3\x4F": "\u00d4",
        b"\xE3\x53": "\u015c",
        b"\xE3\x55": "\u00db",
        b"\xE3\x57": "\u0174",
        b"\xE3\x59": "\u0176",
        b"\xE3\x5A": "\u1e90",
        b"\xE3\x61": "\u00e2",
        b"\xE3\x63": "\u0109",
        b"\xE3\x65": "\u00ea",
        b"\xE3\x67": "\u011d",
        b"\xE3\x68": "\u0125",
        b"\xE3\x69": "\u00ee",
        b"\xE3\x6A": "\u0135",
        b"\xE3\x6F": "\u00f4",
        b"\xE3\x73": "\u015d",
        b"\xE3\x75": "\u00fb",
        b"\xE3\x77": "\u0175",
        b"\xE3\x79": "\u0177",
        b"\xE3\x7A": "\u1e91",
        b"\xE4\x41": "\u00c3",
        b"\xE4\x45": "\u1ebc",
        b"\xE4\x49": "\u0128",
        b"\xE4\x4E": "\u00d1",
        b"\xE4\x4F": "\u00d5",
        b"\xE4\x55": "\u0168",
        b"\xE4\x56": "\u1e7c",
        b"\xE4\x59": "\u1ef8",
        b"\xE4\x61": "\u00e3",
        b"\xE4\x65": "\u1ebd",
        b"\xE4\x69": "\u0129",
        b"\xE4\x6E": "\u00f1",
        b"\xE4\x6F": "\u00f5",
        b"\xE4\x75": "\u0169",
        b"\xE4\x76": "\u1e7d",
        b"\xE4\x79": "\u1ef9",
        b"\xE5\x41": "\u0100",
        b"\xE5\x45": "\u0112",
        b"\xE5\x47": "\u1e20",
        b"\xE5\x49": "\u012a",
        b"\xE5\x4F": "\u014c",
        b"\xE5\x55": "\u016a",
        b"\xE5\x61": "\u0101",
        b"\xE5\x65": "\u0113",
        b"\xE5\x67": "\u1e21",
        b"\xE5\x69": "\u012b",
        b"\xE5\x6F": "\u014d",
        b"\xE5\x75": "\u016b",
        b"\xE5\xA5": "\u01e2",
        b"\xE5\xB5": "\u01e3",
        b"\xE6\x41": "\u0102",
        b"\xE6\x45": "\u0114",
        b"\xE6\x47": "\u011e",
        b"\xE6\x49": "\u012c",
        b"\xE6\x4F": "\u014e",
        b"\xE6\x55": "\u016c",
        b"\xE6\x61": "\u0103",
        b"\xE6\x65": "\u0115",
        b"\xE6\x67": "\u011f",
        b"\xE6\x69": "\u012d",
        b"\xE6\x6F": "\u014f",
        b"\xE6\x75": "\u016d",
        b"\xE7\x42": "\u1e02",
        b"\xE7\x43": "\u010a",
        b"\xE7\x44": "\u1e0a",
        b"\xE7\x45": "\u0116",
        b"\xE7\x46": "\u1e1e",
        b"\xE7\x47": "\u0120",
        b"\xE7\x48": "\u1e22",
        b"\xE7\x49": "\u0130",
        b"\xE7\x4D": "\u1e40",
        b"\xE7\x4E": "\u1e44",
        b"\xE7\x50": "\u1e56",
        b"\xE7\x52": "\u1e58",
        b"\xE7\x53": "\u1e60",
        b"\xE7\x54": "\u1e6a",
        b"\xE7\x57": "\u1e86",
        b"\xE7\x58": "\u1e8a",
        b"\xE7\x59": "\u1e8e",
        b"\xE7\x5A": "\u017b",
        b"\xE7\x62": "\u1e03",
        b"\xE7\x63": "\u010b",
        b"\xE7\x64": "\u1e0b",
        b"\xE7\x65": "\u0117",
        b"\xE7\x66": "\u1e1f",
        b"\xE7\x67": "\u0121",
        b"\xE7\x68": "\u1e23",
        b"\xE7\x6D": "\u1e41",
        b"\xE7\x6E": "\u1e45",
        b"\xE7\x70": "\u1e57",
        b"\xE7\x72": "\u1e59",
        b"\xE7\x73": "\u1e61",
        b"\xE7\x74": "\u1e6b",
        b"\xE7\x77": "\u1e87",
        b"\xE7\x78": "\u1e8b",
        b"\xE7\x79": "\u1e8f",
        b"\xE7\x7A": "\u017c",
        b"\xE8\x41": "\u00c4",
        b"\xE8\x45": "\u00cb",
        b"\xE8\x48": "\u1e26",
        b"\xE8\x49": "\u00cf",
        b"\xE8\x4F": "\u00d6",
        b"\xE8\x55": "\u00dc",
        b"\xE8\x57": "\u1e84",
        b"\xE8\x58": "\u1e8c",
        b"\xE8\x59": "\u0178",
        b"\xE8\x61": "\u00e4",
        b"\xE8\x65": "\u00eb",
        b"\xE8\x68": "\u1e27",
        b"\xE8\x69": "\u00ef",
        b"\xE8\x6F": "\u00f6",
        b"\xE8\x74": "\u1e97",
        b"\xE8\x75": "\u00fc",
        b"\xE8\x77": "\u1e85",
        b"\xE8\x78": "\u1e8d",
        b"\xE8\x79": "\u00ff",
        b"\xE9\x41": "\u01cd",
        b"\xE9\x43": "\u010c",
        b"\xE9\x44": "\u010e",
        b"\xE9\x45": "\u011a",
        b"\xE9\x47": "\u01e6",
        b"\xE9\x49": "\u01cf",
        b"\xE9\x4B": "\u01e8",
        b"\xE9\x4C": "\u013d",
        b"\xE9\x4E": "\u0147",
        b"\xE9\x4F": "\u01d1",
        b"\xE9\x52": "\u0158",
        b"\xE9\x53": "\u0160",
        b"\xE9\x54": "\u0164",
        b"\xE9\x55": "\u01d3",
        b"\xE9\x5A": "\u017d",
        b"\xE9\x61": "\u01ce",
        b"\xE9\x63": "\u010d",
        b"\xE9\x64": "\u010f",
        b"\xE9\x65": "\u011b",
        b"\xE9\x67": "\u01e7",
        b"\xE9\x69": "\u01d0",
        b"\xE9\x6A": "\u01f0",
        b"\xE9\x6B": "\u01e9",
        b"\xE9\x6C": "\u013e",
        b"\xE9\x6E": "\u0148",
        b"\xE9\x6F": "\u01d2",
        b"\xE9\x72": "\u0159",
        b"\xE9\x73": "\u0161",
        b"\xE9\x74": "\u0165",
        b"\xE9\x75": "\u01d4",
        b"\xE9\x7A": "\u017e",
        b"\xEA\x41": "\u00c5",
        b"\xEA\x61": "\u00e5",
        b"\xEA\x75": "\u016f",
        b"\xEA\x77": "\u1e98",
        b"\xEA\x79": "\u1e99",
        b"\xEA\xAD": "\u016e",
        b"\xEE\x4F": "\u0150",
        b"\xEE\x55": "\u0170",
        b"\xEE\x6F": "\u0151",
        b"\xEE\x75": "\u0171",
        b"\xF0\x20": "\u00b8",
        b"\xF0\x43": "\u00c7",
        b"\xF0\x44": "\u1e10",
        b"\xF0\x47": "\u0122",
        b"\xF0\x48": "\u1e28",
        b"\xF0\x4B": "\u0136",
        b"\xF0\x4C": "\u013b",
        b"\xF0\x4E": "\u0145",
        b"\xF0\x52": "\u0156",
        b"\xF0\x53": "\u015e",
        b"\xF0\x54": "\u0162",
        b"\xF0\x63": "\u00e7",
        b"\xF0\x64": "\u1e11",
        b"\xF0\x67": "\u0123",
        b"\xF0\x68": "\u1e29",
        b"\xF0\x6B": "\u0137",
        b"\xF0\x6C": "\u013c",
        b"\xF0\x6E": "\u0146",
        b"\xF0\x72": "\u0157",
        b"\xF0\x73": "\u015f",
        b"\xF0\x74": "\u0163",
        b"\xF1\x41": "\u0104",
        b"\xF1\x45": "\u0118",
        b"\xF1\x49": "\u012e",
        b"\xF1\x4F": "\u01ea",
        b"\xF1\x55": "\u0172",
        b"\xF1\x61": "\u0105",
        b"\xF1\x65": "\u0119",
        b"\xF1\x69": "\u012f",
        b"\xF1\x6F": "\u01eb",
        b"\xF1\x75": "\u0173",
        b"\xF2\x41": "\u1ea0",
        b"\xF2\x42": "\u1e04",
        b"\xF2\x44": "\u1e0c",
        b"\xF2\x45": "\u1eb8",
        b"\xF2\x48": "\u1e24",
        b"\xF2\x49": "\u1eca",
        b"\xF2\x4B": "\u1e32",
        b"\xF2\x4C": "\u1e36",
        b"\xF2\x4D": "\u1e42",
        b"\xF2\x4E": "\u1e46",
        b"\xF2\x4F": "\u1ecc",
        b"\xF2\x52": "\u1e5a",
        b"\xF2\x53": "\u1e62",
        b"\xF2\x54": "\u1e6c",
        b"\xF2\x55": "\u1ee4",
        b"\xF2\x56": "\u1e7e",
        b"\xF2\x57": "\u1e88",
        b"\xF2\x59": "\u1ef4",
        b"\xF2\x5A": "\u1e92",
        b"\xF2\x61": "\u1ea1",
        b"\xF2\x62": "\u1e05",
        b"\xF2\x64": "\u1e0d",
        b"\xF2\x65": "\u1eb9",
        b"\xF2\x68": "\u1e25",
        b"\xF2\x69": "\u1ecb",
        b"\xF2\x6B": "\u1e33",
        b"\xF2\x6C": "\u1e37",
        b"\xF2\x6D": "\u1e43",
        b"\xF2\x6E": "\u1e47",
        b"\xF2\x6F": "\u1ecd",
        b"\xF2\x72": "\u1e5b",
        b"\xF2\x73": "\u1e63",
        b"\xF2\x74": "\u1e6d",
        b"\xF2\x75": "\u1ee5",
        b"\xF2\x76": "\u1e7f",
        b"\xF2\x77": "\u1e89",
        b"\xF2\x79": "\u1ef5",
        b"\xF2\x7A": "\u1e93",
        b"\xF3\x55": "\u1e72",
        b"\xF3\x75": "\u1e73",
        b"\xF4\x41": "\u1e00",
        b"\xF4\x61": "\u1e01",
        b"\xF9\x48": "\u1e2a",
        b"\xF9\x68": "\u1e2b",
    }

    def __ansel_to_unicode(self, text):
        """Convert an ANSEL encoded text to unicode"""

        buff = StringIO()
        error = ""
        while text:
            if text[0] < 128:
                if chr(text[0]) in AnselReader.__use_ASCII:
                    head = chr(text[0])
                else:
                    # substitute space for disallowed (control) chars
                    error += " (%#X)" % text[0]
                    head = " "
                text = text[1:]
            else:
                if text[0:2] in AnselReader.__twobyte:
                    head = AnselReader.__twobyte[text[0:2]]
                    text = text[2:]
                elif bytes([text[0]]) in AnselReader.__onebyte:
                    head = AnselReader.__onebyte[bytes([text[0]])]
                    text = text[1:]
                elif bytes([text[0]]) in AnselReader.__acombiners:
                    cmb = AnselReader.__acombiners[bytes([text[0]])]
                    # always consume the combiner
                    text = text[1:]
                    next_byte = text[0]
                    if (
                        next_byte < 128
                        and chr(next_byte) in AnselReader.__printable_ascii
                    ):
                        # consume next as well
                        text = text[1:]
                        # unicode: combiner follows base-char
                        head = chr(next_byte) + cmb
                    else:
                        # just drop the unexpected combiner
                        error += " (%#X)" % text[0]
                        continue
                else:
                    error += " (%#X)" % text[0]
                    head = "\ufffd"  # "Replacement Char"
                    text = text[1:]
            buff.write(head)
        ans = buff.getvalue()

        if error:
            # e.g. Illegal character (oxAB) (0xCB)... 1 NOTE xyz?pqr?lmn
            self.report_error(_("Illegal character%s") % error, ans)
        buff.close()
        return ans

    def __init__(self, ifile, __add_msg):
        BaseReader.__init__(self, ifile, "ANSEL", __add_msg)
        # In theory, we should have been able to skip the encode/decode from
        # ascii.  But this way allows us to use pythons universal newline
        self.ifile = TextIOWrapper(
            ifile, encoding="ascii", errors="surrogateescape", newline=None
        )

    def readline(self):
        line = self.ifile.readline()
        linebytes = line.encode(encoding="ascii", errors="surrogateescape")
        return self.__ansel_to_unicode(linebytes)


# -------------------------------------------------------------------------
#
# CurrentState
#
# -------------------------------------------------------------------------
class CurrentState:
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
        self.primary = False  # _PRIMARY tag on an INDI.FAMC tag
        self.filename = ""
        self.title = ""
        self.addr = None
        self.res = None
        self.source = None
        self.ftype = None
        self.pf = None  # method for parsing places
        self.location = None
        self.place_fields = None  # method for parsing places
        self.ref = None  # PersonRef
        self.handle = None  #
        self.form = ""  # Multimedia format
        self.frel = None  # Child relation to father
        self.mrel = None
        self.repo = None
        self.attr = None
        self.obj = None
        self.name = ""
        self.ignore = False
        self.repo_ref = None
        self.place = None
        self.media = None
        self.photo = ""  # Person primary photo
        self.prim = None  # Photo is primary

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


# -------------------------------------------------------------------------
#
# PlaceParser
#
# -------------------------------------------------------------------------
class PlaceParser:
    """
    Provide the ability to parse GEDCOM FORM statements for places, and
    the parse the line of text, mapping the text components to Location
    values based of the FORM statement.
    """

    __field_map = {
        "addr": Location.set_street,
        "subdivision": Location.set_street,
        "addr1": Location.set_street,
        "adr1": Location.set_street,
        "street": Location.set_street,
        "addr2": Location.set_locality,
        "adr2": Location.set_locality,
        "locality": Location.set_locality,
        "neighborhood": Location.set_locality,
        "city": Location.set_city,
        "town": Location.set_city,
        "village": Location.set_city,
        "county": Location.set_county,
        "country": Location.set_country,
        "state": Location.set_state,
        "state/province": Location.set_state,
        "region": Location.set_state,
        "province": Location.set_state,
        "area code": Location.set_postal_code,
        "post code": Location.set_postal_code,
        "zip code": Location.set_postal_code,
    }

    def __init__(self, line=None):
        self.parse_function = []

        if line:
            self.parse_form(line)

    def parse_form(self, line):
        """
        Parses the GEDCOM PLAC.FORM into a list of function
        pointers (if possible). It does this my mapping the text strings
        (separated by commas) to the corresponding Location
        method via the __field_map variable
        """
        for item in line.data.split(","):
            item = item.lower().strip()
            fcn = self.__field_map.get(item, lambda x, y: None)
            self.parse_function.append(fcn)

    def load_place(self, place_import, place, text):
        """
        Takes the text string representing a place, splits it into
        its subcomponents (comma separated), and calls the approriate
        function based of its position, depending on the parsed value
        from the FORM statement.
        """
        items = [item.strip() for item in text.split(",")]
        if len(items) != len(self.parse_function):
            return
        index = 0
        loc = Location()
        for item in items:
            self.parse_function[index](loc, item)
            index += 1

        location = (
            loc.get_street(),
            loc.get_locality(),
            loc.get_parish(),
            loc.get_city(),
            loc.get_county(),
            loc.get_state(),
            loc.get_country(),
        )

        for level, name in enumerate(location):
            if name:
                break

        if name:
            type_num = 7 - level
        else:
            name = place.title
            type_num = PlaceType.UNKNOWN
        place.name.set_value(name)
        place.set_type(PlaceType(type_num))
        code = loc.get_postal_code()
        place.set_code(code)
        if place.handle:  # if handle is available, store immediately
            place_import.store_location(location, place.handle)
        else:  # return for storage later
            return location


# -------------------------------------------------------------------------
#
# IdFinder
#
# -------------------------------------------------------------------------
class IdFinder:
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
        while index in self.ids:
            self.index += 1
            index = self.prefix % self.index
        self.ids.add(index)
        self.index += 1
        return index


# -------------------------------------------------------------------------
#
# IdMapper
#
# -------------------------------------------------------------------------
class IdMapper:
    """This class provide methods to keep track of the correspoindence between
    Gedcom xrefs (@P1023@) and Gramps IDs."""

    def __init__(self, has_gid, find_next, id2user_format):
        self.has_gid = has_gid
        self.find_next = find_next
        self.id2user_format = id2user_format
        self.swap = {}

    def __getitem__(self, gid):
        if gid == "":
            # We need to find the next gramps ID provided it is not already
            # the target of a swap
            new_val = self.find_next()
            while new_val in list(self.swap.values()):
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
                if self.has_gid(formatted_gid) or (
                    formatted_gid in list(self.swap.values())
                ):
                    new_val = self.find_next()
                    while new_val in list(self.swap.values()):
                        new_val = self.find_next()
                else:
                    new_val = formatted_gid
            # we need to distinguish between I1 and I0001, so we record the map
            # from the original format
            self.swap[gid] = new_val
        return new_val

    def clean(self, gid):
        """remove '@' from start and end of xref"""
        temp = gid.strip()
        if len(temp) > 1 and temp[0] == "@" and temp[-1] == "@":
            temp = temp[1:-1]
        return temp

    def map(self):
        """return the xref to GID translation map"""
        return self.swap


# -------------------------------------------------------------------------
#
# GedcomParser
#
# -------------------------------------------------------------------------
class GedcomParser(UpdateCallback):
    """
    Performs the second pass of the GEDCOM parser, which does all the heavy
    lifting.
    """

    __TRUNC_MSG = _(
        "Your GEDCOM file is corrupted. " "It appears to have been truncated."
    )
    _EMPTY_LOC = Location().serialize()

    SyntaxError = "Syntax Error"
    BadFile = "Not a GEDCOM file"

    @staticmethod
    def __find_from_handle(gramps_id, table):
        """
        Find a handle corresponding to the specified Gramps ID.

        The passed table contains the mapping. If the value is found, we return
        it, otherwise we create a new handle, store it, and return it.

        """
        intid = table.get(gramps_id)
        if not intid:
            intid = create_id()
            table[gramps_id] = intid
        return intid

    @staticmethod
    def __parse_name_personal(text):
        """
        Parses a GEDCOM NAME value into an Name structure
        """
        name = Name()

        match = SURNAME_RE.match(text)
        if match:
            # /surname/ extra, we assume extra is given name
            names = match.groups()
            name.set_first_name(names[1].strip())
            surn = Surname()
            surn.set_surname(names[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
        else:
            try:
                names = NAME_RE.match(text).groups()
                # given /surname/ extra, we assume extra is suffix
                name.set_first_name(names[0].strip())
                surn = Surname()
                surn.set_surname(names[2].strip())
                surn.set_primary()
                name.set_surname_list([surn])
                name.set_suffix(names[4].strip())
            except:
                # something strange, set as first name
                name.set_first_name(text.strip())
        return name

    def __init__(
        self,
        dbase,
        ifile,
        filename,
        user,
        stage_one,
        default_source,
        default_tag_format=None,
    ):
        UpdateCallback.__init__(self, user.callback)
        self.user = user
        self.set_total(stage_one.get_line_count())
        self.repo2id = {}
        self.trans = None
        self.errors = []
        self.number_of_errors = 0
        self.maxpeople = stage_one.get_person_count()
        self.dbase = dbase
        self.import_researcher = self.dbase.get_total() == 0
        event_ids = []
        for event in dbase.iter_events():
            event_ids.append(event.gramps_id)
        self.emapper = IdFinder(event_ids, dbase.event_prefix)
        self.famc_map = stage_one.get_famc_map()
        self.fams_map = stage_one.get_fams_map()

        self.place_parser = PlaceParser()
        self.inline_srcs = OrderedDict()
        self.media_map = {}
        self.note_type_map = {}
        self.genby = ""
        self.genvers = ""
        self.subm = ""
        self.use_def_src = default_source
        self.func_list = []
        if self.use_def_src:
            self.def_src = Source()
            fname = os.path.basename(filename).split("\\")[-1]
            self.def_src.set_title(_("Import from GEDCOM (%s)") % fname)
        if default_tag_format:
            name = time.strftime(default_tag_format)
            tag = self.dbase.get_tag_from_name(name)
            if tag:
                self.default_tag = tag
            else:
                self.default_tag = Tag()
                self.default_tag.set_name(name)
        else:
            self.default_tag = None
        self.dir_path = os.path.dirname(filename)
        self.is_ftw = False
        self.addr_is_detail = False
        self.groups = None
        self.want_parse_warnings = True

        self.pid_map = IdMapper(
            self.dbase.has_person_gramps_id,
            self.dbase.find_next_person_gramps_id,
            self.dbase.id2user_format,
        )
        self.fid_map = IdMapper(
            self.dbase.has_family_gramps_id,
            self.dbase.find_next_family_gramps_id,
            self.dbase.fid2user_format,
        )
        self.sid_map = IdMapper(
            self.dbase.has_source_gramps_id,
            self.dbase.find_next_source_gramps_id,
            self.dbase.sid2user_format,
        )
        self.oid_map = IdMapper(
            self.dbase.has_media_gramps_id,
            self.dbase.find_next_media_gramps_id,
            self.dbase.oid2user_format,
        )
        self.rid_map = IdMapper(
            self.dbase.has_repository_gramps_id,
            self.dbase.find_next_repository_gramps_id,
            self.dbase.rid2user_format,
        )
        self.nid_map = IdMapper(
            self.dbase.has_note_gramps_id,
            self.dbase.find_next_note_gramps_id,
            self.dbase.nid2user_format,
        )

        self.gid2id = {}
        self.oid2id = {}
        self.sid2id = {}
        self.lid2id = {}
        self.fid2id = {}
        self.rid2id = {}
        self.nid2id = {}

        self.place_import = PlaceImport(self.dbase)

        #
        # Parse table for <<SUBMITTER_RECORD>> below the level 0 SUBM tag
        #
        # n @<XREF:SUBM>@   SUBM                          {1:1}
        #   +1 NAME <SUBMITTER_NAME>                      {1:1}
        #   +1 <<ADDRESS_STRUCTURE>>                      {0:1}
        #   +1 <<MULTIMEDIA_LINK>>                        {0:M}
        #   +1 LANG <LANGUAGE_PREFERENCE>                 {0:3}
        #   +1 <<NOTE_STRUCTURE>>                         {0:M}
        #   +1 RFN <SUBMITTER_REGISTERED_RFN>             {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>                  {0:1}
        #   +1 <<CHANGE_DATE>>                            {0:1}

        # (N.B. GEDCOM allows multiple SUBMitter records)
        self.subm_parse_tbl = {
            # +1 NAME <SUBMITTER_NAME>
            TOKEN_NAME: self.__subm_name,
            # +1 <<ADDRESS_STRUCTURE>>
            TOKEN_ADDR: self.__subm_addr,
            TOKEN_PHON: self.__subm_phon,
            TOKEN_EMAIL: self.__subm_email,
            TOKEN_WWW: self.__repo_www,
            TOKEN_FAX: self.__repo_fax,
            # +1 <<MULTIMEDIA_LINK>>
            # +1 LANG <LANGUAGE_PREFERENCE>
            # +1 <<NOTE_STRUCTURE>>
            TOKEN_NOTE: self.__repo_note,
            TOKEN_RNOTE: self.__repo_note,
            # +1 RFN <SUBMITTER_REGISTERED_RFN>
            # +1 RIN <AUTOMATED_RECORD_ID>
            # +1 <<CHANGE_DATE>>
            TOKEN_CHAN: self.__repo_chan,
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
            TOKEN_RESN: self.__person_resn,
            # +1 <<PERSONAL_NAME_STRUCTURE>> {0:M}
            TOKEN_NAME: self.__person_name,
            # +1 SEX <SEX_VALUE> {0:1}
            TOKEN_SEX: self.__person_sex,
            # +1 <<INDIVIDUAL_EVENT_STRUCTURE>> {0:M}
            TOKEN_EVEN: self.__person_even,
            TOKEN_GEVENT: self.__person_std_event,
            TOKEN_BIRT: self.__person_birt,
            TOKEN_RELI: self.__person_reli,
            TOKEN_ADOP: self.__person_adop,
            TOKEN_DEAT: self.__person_deat,
            # +1 <<INDIVIDUAL_ATTRIBUTE_STRUCTURE>> {0:M}
            # +1 AFN <ANCESTRAL_FILE_NUMBER> {0:1}
            TOKEN_ATTR: self.__person_std_attr,
            TOKEN_FACT: self.__person_fact,
            # +1 <<LDS_INDIVIDUAL_ORDINANCE>> {0:M}
            TOKEN_BAPL: self.__person_bapl,
            TOKEN_CONL: self.__person_conl,
            TOKEN_ENDL: self.__person_endl,
            TOKEN_SLGC: self.__person_slgc,
            # +1 <<CHILD_TO_FAMILY_LINK>> {0:M}
            TOKEN_FAMC: self.__person_famc,
            # +1 <<SPOUSE_TO_FAMILY_LINK>> {0:M}
            TOKEN_FAMS: self.__person_fams,
            # +1 SUBM @<XREF:SUBM>@ {0:M}
            TOKEN_SUBM: self.__skip_record,
            # +1 <<ASSOCIATION_STRUCTURE>> {0:M}
            TOKEN_ASSO: self.__person_asso,
            # +1 ALIA @<XREF:INDI>@ {0:M}
            TOKEN_ALIA: self.__person_alt_name,
            # +1 ANCI @<XREF:SUBM>@ {0:M}
            TOKEN_ANCI: self.__skip_record,
            # +1 DESI @<XREF:SUBM>@ {0:M}
            TOKEN_DESI: self.__skip_record,
            # +1 <<SOURCE_CITATION>> {0:M}
            TOKEN_SOUR: self.__person_sour,
            # +1 <<MULTIMEDIA_LINK>> {0:M}
            TOKEN_OBJE: self.__person_object,
            # +1 <<NOTE_STRUCTURE>> {0:M}
            TOKEN_NOTE: self.__person_note,
            TOKEN_RNOTE: self.__person_note,
            TOKEN__COMM: self.__person_note,
            # +1 RFN <PERMANENT_RECORD_FILE_NUMBER> {0:1}
            TOKEN_RFN: self.__person_attr,
            # +1 REFN <USER_REFERENCE_NUMBER> {0:M}
            # +2 TYPE <USER_REFERENCE_TYPE> {0:1}
            TOKEN_REFN: self.__person_refn,
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE: self.__person_attr,
            # +1 RIN <AUTOMATED_RECORD_ID> {0:1}
            TOKEN_RIN: self.__person_attr,
            # +1 <<CHANGE_DATE>> {0:1}
            TOKEN_CHAN: self.__person_chan,
            # The following tags are not part of Gedcom spec but are commonly
            # found here anyway
            TOKEN_ADDR: self.__person_addr,
            TOKEN_PHON: self.__person_phon,
            TOKEN_FAX: self.__person_fax,
            TOKEN_EMAIL: self.__person_email,
            TOKEN_WWW: self.__person_www,
            TOKEN__TODO: self.__skip_record,
            TOKEN_TITL: self.__person_titl,
            TOKEN__PHOTO: self.__person_photo,
        }
        self.func_list.append(self.indi_parse_tbl)

        self.name_parse_tbl = {
            # +1 NPFX <NAME_PIECE_PREFIX> {0:1}
            TOKEN_NPFX: self.__name_npfx,
            # +1 GIVN <NAME_PIECE_GIVEN> {0:1}
            TOKEN_GIVN: self.__name_givn,
            # NICK <NAME_PIECE_NICKNAME> {0:1}
            TOKEN_NICK: self.__name_nick,
            # _RUFNAME <NAME_PIECE_CALLNAME> {0:1}
            TOKEN__CALLNAME: self.__name_call,
            # +1 SPFX <NAME_PIECE_SURNAME_PREFIX {0:1}
            TOKEN_SPFX: self.__name_spfx,
            # +1 SURN <NAME_PIECE_SURNAME> {0:1}
            TOKEN_SURN: self.__name_surn,
            # +1 NSFX <NAME_PIECE_SUFFIX> {0:1}
            TOKEN_NSFX: self.__name_nsfx,
            # +1 <<SOURCE_CITATION>> {0:M}
            TOKEN_SOUR: self.__name_sour,
            # +1 <<NOTE_STRUCTURE>> {0:M}
            TOKEN_NOTE: self.__name_note,
            TOKEN_RNOTE: self.__name_note,
            # Extensions
            TOKEN_ALIA: self.__name_alia,
            TOKEN__MARNM: self.__name_marnm,
            TOKEN__MAR: self.__name_marnm,  # Generated by geni.com
            TOKEN__MARN: self.__name_marnm,  # Gen'd by BROSKEEP 6.1.31 WIN
            TOKEN__AKA: self.__name_aka,  # PAF and AncestQuest
            TOKEN_TYPE: self.__name_type,  # This is legal GEDCOM 5.5.1
            TOKEN_BIRT: self.__ignore,
            TOKEN_DATE: self.__name_date,
            # This handles date as a subsidiary of "1 ALIA" which might be used
            # by Family Tree Maker and Reunion, and by cheating (handling a
            # lower level from the current parse table) handles date as
            # subsidiary to "2 _MARN", "2 _AKAN" and "2 _ADPN" which has been
            # found in Brother's keeper.
            TOKEN__ADPN: self.__name_adpn,
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
            TOKEN_NAME: self.__repo_name,
            TOKEN_ADDR: self.__repo_addr,
            TOKEN_RIN: self.__ignore,
            TOKEN_NOTE: self.__repo_note,
            TOKEN_RNOTE: self.__repo_note,
            TOKEN_CHAN: self.__repo_chan,
            TOKEN_PHON: self.__repo_phon,
            TOKEN_EMAIL: self.__repo_email,
            TOKEN_WWW: self.__repo_www,
            TOKEN_FAX: self.__repo_fax,
        }
        self.func_list.append(self.repo_parse_tbl)

        self.event_parse_tbl = {
            # n TYPE <EVENT_DESCRIPTOR> {0:1}
            TOKEN_TYPE: self.__event_type,
            # n DATE <DATE_VALUE> {0:1} p.*/*
            TOKEN_DATE: self.__event_date,
            # n <<PLACE_STRUCTURE>> {0:1} p.*
            TOKEN_PLAC: self.__event_place,
            # n <<ADDRESS_STRUCTURE>> {0:1} p.*
            TOKEN_ADDR: self.__event_addr,
            # n AGE <AGE_AT_EVENT> {0:1} p.*
            TOKEN_AGE: self.__event_age,
            # n AGNC <RESPONSIBLE_AGENCY> {0:1} p.*
            TOKEN_AGNC: self.__event_agnc,
            # n CAUS <CAUSE_OF_EVENT> {0:1} p.*
            TOKEN_CAUS: self.__event_cause,
            # n <<SOURCE_CITATION>> {0:M} p.*
            TOKEN_SOUR: self.__event_source,
            # n <<MULTIMEDIA_LINK>> {0:M} p.*, *
            TOKEN_OBJE: self.__event_object,
            # n <<NOTE_STRUCTURE>> {0:M} p.
            TOKEN_NOTE: self.__event_inline_note,
            TOKEN_RNOTE: self.__event_note,
            # Other
            TOKEN__PRIV: self.__event_privacy,
            TOKEN_OFFI: self.__event_note,
            TOKEN_PHON: self.__event_phon,
            TOKEN__GODP: self.__event_witness,
            TOKEN__WITN: self.__event_witness,
            TOKEN__WTN: self.__event_witness,
            TOKEN_RELI: self.__ignore,
            # Not legal, but inserted by PhpGedView
            TOKEN_TIME: self.__event_time,
            TOKEN_ASSO: self.__ignore,
            TOKEN_IGNORE: self.__ignore,
            TOKEN_STAT: self.__ignore,
            TOKEN_TEMP: self.__ignore,
            TOKEN_HUSB: self.__event_husb,
            TOKEN_WIFE: self.__event_wife,
            TOKEN_FAMC: self.__person_birth_famc,
            # Not legal, but inserted by Ultimate Family Tree
            TOKEN_CHAN: self.__ignore,
            TOKEN_QUAY: self.__ignore,
            # Not legal, but inserted by FamilyTreeBuilder
            TOKEN_RIN: self.__event_rin,
            TOKEN_ATTR: self.__event_attr,  # FTB for _UID
            TOKEN_EMAIL: self.__event_email,  # FTB for RESI events
            TOKEN_WWW: self.__event_www,  # FTB for RESI events
            TOKEN_FAX: self.__event_fax,  # legal...
        }
        self.func_list.append(self.event_parse_tbl)

        self.adopt_parse_tbl = {
            TOKEN_TYPE: self.__event_type,
            TOKEN__PRIV: self.__event_privacy,
            TOKEN_DATE: self.__event_date,
            TOKEN_SOUR: self.__event_source,
            TOKEN_PLAC: self.__event_place,
            TOKEN_ADDR: self.__event_addr,
            TOKEN_PHON: self.__event_phon,
            TOKEN_CAUS: self.__event_cause,
            TOKEN_AGNC: self.__event_agnc,
            TOKEN_AGE: self.__event_age,
            TOKEN_NOTE: self.__event_note,
            TOKEN_RNOTE: self.__event_note,
            TOKEN_OFFI: self.__event_note,
            TOKEN__GODP: self.__event_witness,
            TOKEN__WITN: self.__event_witness,
            TOKEN__WTN: self.__event_witness,
            TOKEN_RELI: self.__ignore,
            TOKEN_TIME: self.__ignore,
            TOKEN_ASSO: self.__ignore,
            TOKEN_IGNORE: self.__ignore,
            TOKEN_STAT: self.__ignore,
            TOKEN_TEMP: self.__ignore,
            TOKEN_OBJE: self.__event_object,
            TOKEN_FAMC: self.__person_adopt_famc,
            # Not legal, but inserted by Ultimate Family Tree
            TOKEN_CHAN: self.__ignore,
            TOKEN_QUAY: self.__ignore,
        }
        self.func_list.append(self.adopt_parse_tbl)

        self.famc_parse_tbl = {
            # n FAMC @<XREF:FAM>@ {1:1}
            # +1 PEDI <PEDIGREE_LINKAGE_TYPE> {0:1} p.*
            TOKEN_PEDI: self.__person_famc_pedi,
            # +1 _FREL <Father PEDIGREE_LINKAGE_TYPE> {0:1}  non-standard
            TOKEN__FREL: self.__person_famc_frel,
            # +1 _MREL <Mother PEDIGREE_LINKAGE_TYPE> {0:1}  non-standard
            TOKEN__MREL: self.__person_famc_mrel,
            # +1 <<NOTE_STRUCTURE>> {0:M} p.*
            TOKEN_NOTE: self.__person_famc_note,
            TOKEN_RNOTE: self.__person_famc_note,
            # Extras
            TOKEN__PRIMARY: self.__person_famc_primary,
            TOKEN_SOUR: self.__person_famc_sour,
            # GEDit
            TOKEN_STAT: self.__ignore,
        }
        self.func_list.append(self.famc_parse_tbl)

        self.person_fact_parse_tbl = {
            TOKEN_TYPE: self.__person_fact_type,
            TOKEN_SOUR: self.__person_attr_source,
            TOKEN_NOTE: self.__person_attr_note,
            TOKEN_RNOTE: self.__person_attr_note,
        }
        self.func_list.append(self.person_fact_parse_tbl)

        self.person_attr_parse_tbl = {
            TOKEN_TYPE: self.__person_attr_type,
            TOKEN_CAUS: self.__ignore,
            TOKEN_DATE: self.__ignore,
            TOKEN_TIME: self.__ignore,
            TOKEN_ADDR: self.__ignore,
            TOKEN_IGNORE: self.__ignore,
            TOKEN_STAT: self.__ignore,
            TOKEN_TEMP: self.__ignore,
            TOKEN_OBJE: self.__ignore,
            TOKEN_SOUR: self.__person_attr_source,
            TOKEN_PLAC: self.__person_attr_place,
            TOKEN_NOTE: self.__person_attr_note,
            TOKEN_RNOTE: self.__person_attr_note,
        }
        self.func_list.append(self.person_attr_parse_tbl)

        self.lds_parse_tbl = {
            TOKEN_TEMP: self.__lds_temple,
            TOKEN_DATE: self.__lds_date,
            TOKEN_FAMC: self.__lds_famc,
            TOKEN_FORM: self.__lds_form,
            TOKEN_PLAC: self.__lds_plac,
            TOKEN_SOUR: self.__lds_sour,
            TOKEN_NOTE: self.__lds_note,
            TOKEN_RNOTE: self.__lds_note,
            TOKEN_STAT: self.__lds_stat,
        }
        self.func_list.append(self.lds_parse_tbl)

        self.asso_parse_tbl = {
            TOKEN_RELA: self.__person_asso_rela,
            TOKEN_SOUR: self.__person_asso_sour,
            TOKEN_NOTE: self.__person_asso_note,
            TOKEN_RNOTE: self.__person_asso_note,
        }
        self.func_list.append(self.asso_parse_tbl)

        self.citation_parse_tbl = {
            TOKEN_PAGE: self.__citation_page,
            TOKEN_DATE: self.__citation_date,
            TOKEN_DATA: self.__citation_data,
            TOKEN_OBJE: self.__citation_obje,
            TOKEN_REFN: self.__citation_refn,
            TOKEN_EVEN: self.__citation_even,
            TOKEN_IGNORE: self.__ignore,
            TOKEN__LKD: self.__ignore,
            TOKEN_QUAY: self.__citation_quay,
            TOKEN_NOTE: self.__citation_note,
            TOKEN_RNOTE: self.__citation_note,
            TOKEN_TEXT: self.__citation_data_text,
            TOKEN__LINK: self.__citation_link,
            TOKEN__JUST: self.__citation__just,
            TOKEN__APID: self.__citation__apid,
        }
        self.func_list.append(self.citation_parse_tbl)

        self.media_parse_tbl = {
            TOKEN_FORM: self.__media_ref_form,
            TOKEN_MEDI: self.__media_ref_medi,  # v5.5.1
            TOKEN_TITL: self.__media_ref_titl,
            TOKEN_FILE: self.__media_ref_file,
            TOKEN_NOTE: self.__obje_note,  # illegal, but often there
            TOKEN_RNOTE: self.__obje_note,  # illegal, but often there
            TOKEN__PRIM: self.__media_ref_prim,  # LFT etc.
            TOKEN_IGNORE: self.__ignore,
        }
        self.func_list.append(self.media_parse_tbl)

        self.parse_loc_tbl = {
            TOKEN_ADR1: self.__location_adr1,
            TOKEN_ADR2: self.__location_adr2,
            TOKEN_CITY: self.__location_city,
            TOKEN_STAE: self.__location_stae,
            TOKEN_POST: self.__location_post,
            TOKEN_CTRY: self.__location_ctry,
            # Not legal GEDCOM - not clear why these are included at this level
            TOKEN_ADDR: self.__ignore,
            TOKEN_DATE: self.__ignore,  # there is nowhere to put a date
            TOKEN_NOTE: self.__location_note,
            TOKEN_RNOTE: self.__location_note,
            TOKEN__LOC: self.__ignore,
            TOKEN__NAME: self.__ignore,
            TOKEN_PHON: self.__location_phone,
            TOKEN_IGNORE: self.__ignore,
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
            TOKEN_GEVENT: self.__family_std_event,
            TOKEN_EVEN: self.__fam_even,
            # +1 HUSB @<XREF:INDI>@  {0:1}
            TOKEN_HUSB: self.__family_husb,
            # +1 WIFE @<XREF:INDI>@  {0:1}
            TOKEN_WIFE: self.__family_wife,
            # +1 CHIL @<XREF:INDI>@  {0:M}
            TOKEN_CHIL: self.__family_chil,
            # +1 NCHI <COUNT_OF_CHILDREN>  {0:1}
            # +1 SUBM @<XREF:SUBM>@  {0:M}
            # +1 <<LDS_SPOUSE_SEALING>>  {0:M}
            TOKEN_SLGS: self.__family_slgs,
            # +1 <<SOURCE_CITATION>>  {0:M}
            TOKEN_SOUR: self.__family_source,
            # +1 <<MULTIMEDIA_LINK>>  {0:M}
            TOKEN_OBJE: self.__family_object,
            # +1 <<NOTE_STRUCTURE>>  {0:M}
            TOKEN__COMM: self.__family_comm,
            TOKEN_NOTE: self.__family_note,
            TOKEN_RNOTE: self.__family_note,
            # +1 REFN <USER_REFERENCE_NUMBER>  {0:M}
            TOKEN_REFN: self.__family_refn,
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE: self.__family_cust_attr,
            # +1 RIN <AUTOMATED_RECORD_ID>  {0:1}
            # +1 <<CHANGE_DATE>>  {0:1}
            TOKEN_CHAN: self.__family_chan,
            TOKEN_ENDL: self.__ignore,
            TOKEN_ADDR: self.__ignore,
            TOKEN_RIN: self.__family_cust_attr,
            TOKEN_SUBM: self.__ignore,
            TOKEN_ATTR: self.__family_attr,
        }
        self.func_list.append(self.family_func)

        self.family_rel_tbl = {
            TOKEN__FREL: self.__family_frel,
            TOKEN__MREL: self.__family_mrel,
            TOKEN_ADOP: self.__family_adopt,
            TOKEN__STAT: self.__family_stat,
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
            TOKEN_TITL: self.__source_title,
            TOKEN_TAXT: self.__source_taxt_peri,
            TOKEN_PERI: self.__source_taxt_peri,
            TOKEN_AUTH: self.__source_auth,
            TOKEN_PUBL: self.__source_publ,
            TOKEN_NOTE: self.__source_note,
            TOKEN_RNOTE: self.__source_note,
            TOKEN_TEXT: self.__source_text,
            TOKEN_ABBR: self.__source_abbr,
            TOKEN_REFN: self.__source_attr,
            TOKEN_RIN: self.__source_attr,
            TOKEN_REPO: self.__source_repo,
            TOKEN_OBJE: self.__source_object,
            TOKEN_CHAN: self.__source_chan,
            TOKEN_MEDI: self.__source_attr,
            TOKEN__NAME: self.__source_attr,
            TOKEN_DATA: self.__ignore,
            # TYPE should be below REFN, but will work here anyway
            TOKEN_TYPE: self.__source_attr,
            TOKEN_CALN: self.__ignore,
            # not legal, but Ultimate Family Tree does this
            TOKEN_DATE: self.__ignore,
            TOKEN_IGNORE: self.__ignore,
            TOKEN__APID: self.__source_attr,
        }
        self.func_list.append(self.source_func)

        #
        # Parse table for <<MULTIMEDIA_RECORD>> below the level 0 OBJE tag
        #
        # n  @XREF:OBJE@ OBJE {1:1}                 # v5.5 layout
        #   +1 FILE <MULTIMEDIA_FILE_REFN>    {1:1} # de-facto extension
        #   +1 FORM <MULTIMEDIA_FORMAT>       {1:1}
        #   +1 TITL <DESCRIPTIVE_TITLE>       {0:1}
        #   +1 <<NOTE_STRUCTURE>>             {0:M}
        #   +1 BLOB                           {1:1} # Deprecated, no support
        #     +2 CONT <ENCODED_MULTIMEDIA_LINE> {1:M}
        #   +1 OBJE @<XREF:OBJE>@ /* chain */ {0:1} # Deprecated, no support
        #   +1 REFN <USER_REFERENCE_NUMBER>   {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>   {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>      {0:1}
        #   +1 <<CHANGE_DATE>>                {0:1}
        #
        # n @XREF:OBJE@ OBJE {1:1}                  # v5.5.1 layout
        #   +1 FILE <MULTIMEDIA_FILE_REFN>    {1:M} # multi files, no support
        #     +2 FORM <MULTIMEDIA_FORMAT>     {1:1}
        #       +3 TYPE <SOURCE_MEDIA_TYPE>   {0:1}
        #     +2 TITL <DESCRIPTIVE_TITLE>     {0:1}
        #     +2 DATE <mm/dd/yyy hh:mn:ss AM> {0:1}    # FTM extension
        #     +2 TEXT <COMMENT, by user or exif> {0:1} # FTM extension
        #   +1 REFN <USER_REFERENCE_NUMBER>   {0:M}
        #     +2 TYPE <USER_REFERENCE_TYPE>   {0:1}
        #   +1 RIN <AUTOMATED_RECORD_ID>      {0:1}
        #   +1 <<NOTE_STRUCTURE>>             {0:M}
        #   +1 <<SOURCE_CITATION>>            {0:M}
        #   +1 <<CHANGE_DATE>>                {0:1}

        self.obje_func = {
            TOKEN_FORM: self.__obje_form,
            TOKEN_TYPE: self.__obje_type,  # v5.5.1
            TOKEN_TITL: self.__obje_title,
            TOKEN_FILE: self.__obje_file,  # de-facto extension
            TOKEN_TEXT: self.__obje_text,  # FTM extension
            TOKEN__TEXT: self.__obje_text,  # FTM 2017 extension
            TOKEN_DATE: self.__obje_date,  # FTM extension
            TOKEN__DATE: self.__obje_date,  # FTM 2017 extension
            TOKEN_NOTE: self.__obje_note,
            TOKEN_RNOTE: self.__obje_note,
            TOKEN_SOUR: self.__obje_sour,
            TOKEN_BLOB: self.__ignore,  # v5.5.1 deprecated
            TOKEN_REFN: self.__obje_refn,
            TOKEN_RIN: self.__obje_rin,
            TOKEN_CHAN: self.__obje_chan,
        }
        self.func_list.append(self.obje_func)

        self.parse_addr_tbl = {
            TOKEN_DATE: self.__address_date,
            TOKEN_ADR1: self.__address_adr1,
            TOKEN_ADR2: self.__address_adr2,
            TOKEN_CITY: self.__address_city,
            TOKEN_STAE: self.__address_state,
            TOKEN_POST: self.__address_post,
            TOKEN_CTRY: self.__address_country,
            TOKEN_PHON: self.__ignore,
            TOKEN_SOUR: self.__address_sour,
            TOKEN_NOTE: self.__address_note,
            TOKEN_RNOTE: self.__address_note,
            TOKEN__LOC: self.__ignore,
            TOKEN__NAME: self.__ignore,
            TOKEN_IGNORE: self.__ignore,
            TOKEN_TYPE: self.__ignore,
            TOKEN_CAUS: self.__ignore,
        }
        self.func_list.append(self.parse_addr_tbl)

        self.event_cause_tbl = {
            TOKEN_SOUR: self.__event_cause_source,
        }
        self.func_list.append(self.event_cause_tbl)

        self.event_place_map = {
            TOKEN_NOTE: self.__event_place_note,
            TOKEN_RNOTE: self.__event_place_note,
            TOKEN_FORM: self.__event_place_form,
            # Not legal.
            TOKEN_OBJE: self.__event_place_object,
            TOKEN_SOUR: self.__event_place_sour,
            TOKEN__LOC: self.__ignore,
            TOKEN_MAP: self.__place_map,
            # Not legal,  but generated by Ultimate Family Tree
            TOKEN_QUAY: self.__ignore,
        }
        self.func_list.append(self.event_place_map)

        self.place_map_tbl = {
            TOKEN_LATI: self.__place_lati,
            TOKEN_LONG: self.__place_long,
        }
        self.func_list.append(self.place_map_tbl)

        self.repo_ref_tbl = {
            TOKEN_CALN: self.__repo_ref_call,
            TOKEN_NOTE: self.__repo_ref_note,
            TOKEN_RNOTE: self.__repo_ref_note,
            TOKEN_MEDI: self.__repo_ref_medi,
            TOKEN_IGNORE: self.__ignore,
        }
        self.func_list.append(self.repo_ref_tbl)

        self.parse_person_adopt = {
            TOKEN_ADOP: self.__person_adopt_famc_adopt,
        }
        self.func_list.append(self.parse_person_adopt)

        self.opt_note_tbl = {
            TOKEN_RNOTE: self.__optional_note,
            TOKEN_NOTE: self.__optional_note,
        }
        self.func_list.append(self.opt_note_tbl)

        self.citation_data_tbl = {
            TOKEN_DATE: self.__citation_data_date,
            TOKEN_TEXT: self.__citation_data_text,
            TOKEN_RNOTE: self.__citation_data_note,
            TOKEN_NOTE: self.__citation_data_note,
        }
        self.func_list.append(self.citation_data_tbl)

        self.citation_even_tbl = {
            TOKEN_ROLE: self.__citation_even_role,
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
            TOKEN_SOUR: self.__header_sour,
            TOKEN_NAME: self.__header_sour_name,  # This should be below SOUR
            TOKEN_VERS: self.__header_sour_vers,  # This should be below SOUR
            TOKEN_FILE: self.__header_file,
            TOKEN_COPR: self.__header_copr,
            TOKEN_SUBM: self.__header_subm,
            TOKEN_CORP: self.__ignore,  # This should be below SOUR
            TOKEN_DATA: self.__ignore,  # This should be below SOUR
            TOKEN_SUBN: self.__header_subn,
            TOKEN_LANG: self.__header_lang,
            TOKEN_TIME: self.__ignore,  # This should be below DATE
            TOKEN_DEST: self.__header_dest,
            TOKEN_CHAR: self.__header_char,
            TOKEN_GEDC: self.__header_gedc,
            TOKEN_PLAC: self.__header_plac,
            TOKEN_DATE: self.__header_date,
            TOKEN_NOTE: self.__header_note,
            TOKEN__SCHEMA: self.__ignore,
        }
        self.func_list.append(self.head_parse_tbl)

        self.header_sour_parse_tbl = {
            TOKEN_VERS: self.__header_sour_vers,
            TOKEN_NAME: self.__header_sour_name,
            TOKEN_CORP: self.__header_sour_corp,
            TOKEN_DATA: self.__header_sour_data,
        }
        self.func_list.append(self.header_sour_parse_tbl)

        self.header_sour_data = {
            TOKEN_DATE: self.__header_sour_date,
            TOKEN_COPR: self.__header_sour_copr,
        }
        self.func_list.append(self.header_sour_data)

        self.header_corp_addr = {
            TOKEN_ADDR: self.__repo_addr,
            TOKEN_PHON: self.__repo_phon,
            TOKEN_FAX: self.__repo_fax,
            TOKEN_WWW: self.__repo_www,
            TOKEN_EMAIL: self.__repo_email,
        }
        self.func_list.append(self.header_corp_addr)

        self.header_subm = {
            TOKEN_NAME: self.__header_subm_name,
        }
        self.func_list.append(self.header_subm)

        self.place_form = {
            TOKEN_FORM: self.__place_form,
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
            TOKEN_SOUR: self.__ignore,
            TOKEN_REFN: self.__ignore,
            TOKEN_RIN: self.__ignore,
            TOKEN_CHAN: self.__note_chan,
        }
        self.func_list.append(self.note_parse_tbl)

        # look for existing place titles, build a map
        self.place_names = defaultdict(list)
        cursor = dbase.get_place_cursor()
        data = next(cursor)
        while data:
            (handle, val) = data
            self.place_names[val[2]].append(handle)
            data = next(cursor)
        cursor.close()

        enc = stage_one.get_encoding()

        if enc == "ANSEL":
            rdr = AnselReader(ifile, self.__add_msg)
        elif enc in ("UTF-8", "UTF8", "UTF_8_SIG"):
            rdr = UTF8Reader(ifile, self.__add_msg, enc)
        elif enc in ("UTF-16LE", "UTF-16BE", "UTF16", "UNICODE"):
            rdr = UTF16Reader(ifile, self.__add_msg)
        elif enc in ("CP1252", "WINDOWS-1252"):
            rdr = CP1252Reader(ifile, self.__add_msg)
        else:
            rdr = AnsiReader(ifile, self.__add_msg)

        self.lexer = Lexer(rdr, self.__add_msg)
        self.filename = filename
        self.backoff = False

        fullpath = os.path.normpath(os.path.abspath(filename))
        self.geddir = os.path.dirname(fullpath)

        self.error_count = 0
        amap = PERSONALCONSTANTATTRIBUTES

        self.attrs = list(amap.values())
        self.gedattr = dict([key, val] for val, key in amap.items())

    def parse_gedcom_file(self, use_trans=False):
        """
        Parses the opened GEDCOM file.

        LINEAGE_LINKED_GEDCOM: =
          0 <<HEADER>>                                    {1:1}
          0 <<SUBMISSION_RECORD>>                         {0:1}
          0 <<RECORD>>                                    {1:M}
          0 TRLR                                          {1:1}

        """
        with DbTxn(_("GEDCOM import"), self.dbase, not use_trans) as self.trans:
            self.dbase.disable_signals()
            self.__parse_header_head()
            self.want_parse_warnings = False
            self.want_parse_warnings = True
            if self.use_def_src:
                self.dbase.add_source(self.def_src, self.trans)
            if self.default_tag and self.default_tag.handle is None:
                self.dbase.add_tag(self.default_tag, self.trans)
            self.__parse_header()
            self.__parse_record()
            self.__parse_trailer()
            for title, handle in self.inline_srcs.items():
                src = Source()
                src.set_handle(handle)
                src.set_title(title)
                self.dbase.add_source(src, self.trans)
            self.__clean_up()

            self.place_import.generate_hierarchy(self.trans)

            if not self.dbase.get_feature("skip-check-xref"):
                self.__check_xref()
        self.dbase.enable_signals()
        self.dbase.request_rebuild()
        if self.number_of_errors == 0:
            message = _("GEDCOM import report: No errors detected")
        else:
            message = (
                _("GEDCOM import report: %s errors detected") % self.number_of_errors
            )
        if hasattr(self.user.uistate, "window"):
            parent_window = self.user.uistate.window
        else:
            parent_window = None
        self.user.info(
            message, "".join(self.errors), parent=parent_window, monospaced=True
        )

    def __clean_up(self):
        """
        Break circular references to parsing methods stored in dictionaries
        to aid garbage collection
        """
        for func_map in self.func_list:
            for key in list(func_map.keys()):
                del func_map[key]
            del func_map
        del self.func_list
        del self.update
        self.lexer.clean_up()

    def __find_person_handle(self, gramps_id):
        """
        Return the database handle associated with the person's Gramps ID
        """
        return self.__find_from_handle(gramps_id, self.gid2id)

    def __find_family_handle(self, gramps_id):
        """
        Return the database handle associated with the family's Gramps ID
        """
        return self.__find_from_handle(gramps_id, self.fid2id)

    def __find_media_handle(self, gramps_id):
        """
        Return the database handle associated with the media object's Gramps ID
        """
        return self.__find_from_handle(gramps_id, self.oid2id)

    def __find_note_handle(self, gramps_id):
        """
        Return the database handle associated with the media object's Gramps ID
        """
        return self.__find_from_handle(gramps_id, self.nid2id)

    def __find_or_create_person(self, gramps_id):
        """
        Finds or creates a person based on the Gramps ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise,
        we create a new person, assign the handle and Gramps ID.
        """
        person = Person()
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
        Finds or creates a family based on the Gramps ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise,
        we create a new family, assign the handle and Gramps ID.
        """
        family = Family()
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

    def __find_or_create_media(self, gramps_id):
        """
        Finds or creates a media object based on the Gramps ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise,
        we create a new media object, assign the handle and Gramps ID.
        """
        obj = Media()
        intid = self.oid2id.get(gramps_id)
        if self.dbase.has_media_handle(intid):
            obj.unserialize(self.dbase.get_raw_media_data(intid))
        else:
            intid = self.__find_from_handle(gramps_id, self.oid2id)
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
        return obj

    def __find_or_create_source(self, gramps_id):
        """
        Find or create a source based on the Gramps ID.

        If the ID is already used (is in the db), we return the item in the
        db. Otherwise, we create a new source, assign the handle and Gramps ID.

        """
        obj = Source()
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
        Finds or creates a repository based on the Gramps ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise,
        we create a new repository, assign the handle and Gramps ID.

        Some GEDCOM "flavors" destroy the specification, and declare the
        repository inline instead of in a object.
        """
        repository = Repository()
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
        Finds or creates a note based on the Gramps ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise,
        we create a new note, assign the handle and Gramps ID.
        If no Gramps ID is passed in, we not only make a Note with GID, we
        commit it.
        """
        note = Note()
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

    def __find_place(self, title, location, placeref_list):
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
                if (
                    self.__loc_is_empty(location)
                    and self.__loc_is_empty(self.__get_first_loc(place))
                    and place.get_placeref_list() == placeref_list
                ):
                    return place
                elif (
                    not self.__loc_is_empty(location)
                    and not self.__loc_is_empty(self.__get_first_loc(place))
                    and self.__get_first_loc(place).is_equivalent(location) == IDENTICAL
                ) and place.get_placeref_list() == placeref_list:
                    return place
        return None

    def __add_place(self, event, sub_state):
        """
        Add a new place to an event if not already present, or update a
        place.

        @param event: The event
        @type event: gen.lib.Event
        @param substate: The sub-state for PLAC or ADDR elements (i.e. parsed
                        by event_parse_tbl)
        @type sub_state: CurrentState
        """
        if sub_state.place:
            # see whether this place already exists
            place = self.__find_place(
                sub_state.place.get_title(),
                self.__get_first_loc(sub_state.place),
                sub_state.place.get_placeref_list(),
            )
            if place is None:
                place = sub_state.place
                place_title = _pd.display(self.dbase, place)
                location = sub_state.pf.load_place(
                    self.place_import, place, place_title
                )
                self.dbase.add_place(place, self.trans)
                # if 'location was created, then store it, now that we have a
                # handle.
                if location:
                    self.place_import.store_location(location, place.handle)
                self.place_names[place.get_title()].append(place.get_handle())
                event.set_place_handle(place.get_handle())
            else:
                place.merge(sub_state.place)
                place_title = _pd.display(self.dbase, place)
                location = sub_state.pf.load_place(
                    self.place_import, place, place_title
                )
                self.dbase.commit_place(place, self.trans)
                if location:
                    self.place_import.store_location(location, place.handle)
                event.set_place_handle(place.get_handle())

    def __find_file(self, fullname, altpath):
        # try to find the media file
        fullname = fullname.replace("\\", os.path.sep)

        try:
            if os.path.isfile(fullname):
                return (1, fullname)
        except UnicodeEncodeError:
            # FIXME: problem possibly caused by umlaut/accented character
            # in filename
            return (0, fullname)
        # strip off Windows drive letter, if present
        if len(fullname) > 3 and fullname[1] == ":":
            fullname = fullname[2:]
        # look where we found the '.ged', using the full path in fullname
        other = os.path.join(altpath, fullname)
        if os.path.isfile(other):
            return (1, other)
        # lets try reducing to just where we found '.ged'
        other = os.path.join(altpath, os.path.basename(fullname))
        if os.path.isfile(other):
            return (1, other)
        # lets try using the base path for relative media paths
        other = os.path.join(media_path(self.dbase), fullname)
        if os.path.isfile(other):
            return (1, fullname)
        # lets try using the base path for relative media paths with base name
        other = os.path.join(media_path(self.dbase), os.path.basename(fullname))
        if os.path.isfile(other):
            return (1, os.path.basename(fullname))
        return (0, fullname)

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
                raise GedcomError(self.__TRUNC_MSG)

        self.backoff = False
        return self.groups

    def __chk_subordinate(self, level, state, token):
        """
        checks for a single subordinate line with specific token.  If any other
        lines are present, they are not understood.

        @param level: Current level in the file
        @type level: int
        @param state: The current state
        @type state: CurrentState
        @param token: The token to search for
        @type token: int
        """
        skips = 0
        got_line = None
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, level):
                if skips:
                    # This improves formatting when there are long sequences of
                    # skipped lines
                    self.__add_msg("", None, None)
                return got_line
            if line.token == token:
                got_line = line
            else:
                self.__add_msg(_("Line ignored as not understood"), line, state)
                skips += 1

    def __undefined(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__not_recognized(line, state)

    def __ignore(self, line, state):
        """
        Prints a message when an unexpected token is found.  If the token is
        known, then the line is considered "not supported", otherwise the line
        is "not understood".

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.token == TOKEN_UNKNOWN:
            self.__add_msg(_("Line ignored as not understood"), line, state)
        else:
            self.__add_msg(_("Tag recognized but not supported"), line, state)
        self.__skip_subordinate_levels(line.level + 1, state)

    def __not_recognized(self, line, state):
        """
        Prints a message when an undefined token is found. All subordinate
        items to the current item are ignored.

        @param level: Current level in the file
        @type level: int
        """
        self.__add_msg(_("Line ignored as not understood"), line, state)
        self.__skip_subordinate_levels(line.level + 1, state)

    def __skip_record(self, _line, state):
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
            problem = problem.ljust(prob_width)[0 : (prob_width - 1)]
            text = str(line.data).replace("\n", "\n".ljust(prob_width + 22))
            message = "%s   Line %5d: %s %s %s\n" % (
                problem,
                line.line,
                line.level,
                line.token_text,
                text,
            )
        else:
            message = problem + "\n"
        if state:
            state.msg += message
        self.errors.append(message)

    def __check_msgs(self, record_name, state, obj):
        if state.msg == "":
            return
        message = _("Records not imported into ") + record_name + ":\n\n" + state.msg
        new_note = Note()
        tag = StyledTextTag(
            StyledTextTagType.FONTFACE, "Monospace", [(0, len(message))]
        )
        text = StyledText(message, [tag])
        new_note.set_styledtext(text)
        new_note.set_handle(create_id())
        gramps_id = self.nid_map[""]
        new_note.set_gramps_id(gramps_id)
        note_type = NoteType()
        note_type.set((NoteType.CUSTOM, _("GEDCOM import")))
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
        def __check(_map, has_gid_func, class_func, commit_func, gramps_id2handle, msg):
            for input_id, gramps_id in _map.map().items():
                # Check whether an object exists for the mapped gramps_id
                if not has_gid_func(gramps_id):
                    _handle = self.__find_from_handle(gramps_id, gramps_id2handle)
                    if msg == "FAM":
                        make_unknown(
                            gramps_id,
                            self.explanation.handle,
                            class_func,
                            commit_func,
                            self.trans,
                            db=self.dbase,
                        )
                        self.missing_references += 1
                        self.__add_msg(
                            _(
                                "Error: %(msg)s  '%(gramps_id)s'"
                                " (input as @%(xref)s@) not in input"
                                " GEDCOM. Record synthesised"
                            )
                            % {"msg": msg, "gramps_id": gramps_id, "xref": input_id}
                        )
                    else:
                        make_unknown(
                            gramps_id,
                            self.explanation.handle,
                            class_func,
                            commit_func,
                            self.trans,
                        )
                        self.missing_references += 1
                        self.__add_msg(
                            _(
                                "Error: %(msg)s '%(gramps_id)s'"
                                " (input as @%(xref)s@) not in input"
                                " GEDCOM. Record with typifying"
                                " attribute 'Unknown' created"
                            )
                            % {"msg": msg, "gramps_id": gramps_id, "xref": input_id}
                        )

        self.explanation = create_explanation_note(self.dbase)

        self.missing_references = 0
        __check(
            self.pid_map,
            self.dbase.has_person_gramps_id,
            self.__find_or_create_person,
            self.dbase.commit_person,
            self.gid2id,
            "INDI",
        )
        __check(
            self.fid_map,
            self.dbase.has_family_gramps_id,
            self.__find_or_create_family,
            self.dbase.commit_family,
            self.fid2id,
            "FAM",
        )
        __check(
            self.sid_map,
            self.dbase.has_source_gramps_id,
            self.__find_or_create_source,
            self.dbase.commit_source,
            self.sid2id,
            "SOUR",
        )
        __check(
            self.oid_map,
            self.dbase.has_media_gramps_id,
            self.__find_or_create_media,
            self.dbase.commit_media,
            self.oid2id,
            "OBJE",
        )
        __check(
            self.rid_map,
            self.dbase.has_repository_gramps_id,
            self.__find_or_create_repository,
            self.dbase.commit_repository,
            self.rid2id,
            "REPO",
        )
        __check(
            self.nid_map,
            self.dbase.has_note_gramps_id,
            self.__find_or_create_note,
            self.dbase.commit_note,
            self.nid2id,
            "NOTE",
        )

        # Check persons membership in referenced families
        def __input_fid(gramps_id):
            for key, val in self.fid_map.map().items():
                if val == gramps_id:
                    return key

        for input_id, gramps_id in self.pid_map.map().items():
            person_handle = self.__find_from_handle(gramps_id, self.gid2id)
            person = self.dbase.get_person_from_handle(person_handle)
            for family_handle in person.get_family_handle_list():
                family = self.dbase.get_family_from_handle(family_handle)
                if (
                    family
                    and family.get_father_handle() != person_handle
                    and family.get_mother_handle() != person_handle
                ):
                    person.remove_family_handle(family_handle)
                    self.dbase.commit_person(person, self.trans)
                    self.__add_msg(
                        _(
                            "Error: family '%(family)s' (input as"
                            " @%(orig_family)s@) person %(person)s"
                            " (input as %(orig_person)s) is not a"
                            " member of the referenced family."
                            " Family reference removed from person"
                        )
                        % {
                            "family": family.gramps_id,
                            "orig_family": __input_fid(family.gramps_id),
                            "person": person.gramps_id,
                            "orig_person": input_id,
                        }
                    )

        def __input_pid(gramps_id):
            for key, val in self.pid_map.map().items():
                if val == gramps_id:
                    return key

        for input_id, gramps_id in self.fid_map.map().items():
            family_handle = self.__find_from_handle(gramps_id, self.fid2id)
            family = self.dbase.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()

            if father_handle:
                father = self.dbase.get_person_from_handle(father_handle)
                if father and family_handle not in father.get_family_handle_list():
                    father.add_family_handle(family_handle)
                    self.dbase.commit_person(father, self.trans)
                    self.__add_msg(
                        "Error: family '%(family)s' (input as"
                        " @%(orig_family)s@) father '%(father)s'"
                        " (input as '%(orig_father)s') does not "
                        "refer back to the family. Reference added."
                        % {
                            "family": family.gramps_id,
                            "orig_family": input_id,
                            "father": father.gramps_id,
                            "orig_father": __input_pid(father.gramps_id),
                        }
                    )

            if mother_handle:
                mother = self.dbase.get_person_from_handle(mother_handle)
                if mother and family_handle not in mother.get_family_handle_list():
                    mother.add_family_handle(family_handle)
                    self.dbase.commit_person(mother, self.trans)
                    self.__add_msg(
                        "Error: family '%(family)s' (input as"
                        " @%(orig_family)s@) mother '%(mother)s'"
                        " (input as '%(orig_mother)s') does not "
                        "refer back to the family. Reference added."
                        % {
                            "family": family.gramps_id,
                            "orig_family": input_id,
                            "mother": mother.gramps_id,
                            "orig_mother": __input_pid(mother.gramps_id),
                        }
                    )

            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.dbase.get_person_from_handle(child_handle)
                if child:
                    if family_handle not in child.get_parent_family_handle_list():
                        # The referenced child has no reference to the family.
                        # There was a link from the FAM record to the child,
                        # but no FAMC link from the child to the FAM.
                        child.add_parent_family_handle(family_handle)
                        self.dbase.commit_person(child, self.trans)
                        self.__add_msg(
                            "Error: family '%(family)s' (input as"
                            " @%(orig_family)s@) child '%(child)s'"
                            " (input as '%(orig_child)s') does not "
                            "refer back to the family. "
                            "Reference added."
                            % {
                                "family": family.gramps_id,
                                "orig_family": input_id,
                                "child": child.gramps_id,
                                "orig_child": __input_pid(child.gramps_id),
                            }
                        )

        if self.missing_references:
            self.dbase.commit_note(self.explanation, self.trans, time.time())
            txt = _(
                "\nThe imported file was not self-contained.\n"
                "To correct for that, %(new)d objects were created and\n"
                "their typifying attribute was set to 'Unknown'.\n"
                "Where possible these 'Unknown' objects are \n"
                "referenced by note %(unknown)s.\n"
            ) % {"new": self.missing_references, "unknown": self.explanation.gramps_id}
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
        CTRY), then Street is set to the freeform address. N.B. this is a
        change for Repository addresses and HEADer Corp address where
        previously the free-form address was deconstrucated into different
        structured components. N.B. PAF provides a free-form address and a
        country, so this allows for that case.

        If both forms of address are provided, then the structured address is
        used, and if the ADDR/CONT contains anything not in the structured
        address, a warning is issued.

        If just ADR1, ADR2, CITY, STAE, POST or CTRY are provided (this is not
        actually legal GEDCOM symtax, but may be possible by GEDCOM extensions)
        then just the structrued address is used.
        The routine returns a string suitable for a title.
        """
        title = ""
        free_form_address = free_form_address.replace("\n", ", ")
        if not (
            addr.get_street()
            or addr.get_locality()
            or addr.get_city()
            or addr.get_state()
            or addr.get_postal_code()
        ):
            addr.set_street(free_form_address)
            return free_form_address
        else:
            # structured address provided
            addr_list = free_form_address.split(",")
            str_list = []
            for func in (
                addr.get_street(),
                addr.get_locality(),
                addr.get_city(),
                addr.get_state(),
                addr.get_postal_code(),
                addr.get_country(),
            ):
                str_list += [i.strip("," + string.whitespace) for i in func.split("\n")]
            for elmn in addr_list:
                if elmn.strip("," + string.whitespace) not in str_list:
                    # message means that the element %s was ignored, but
                    # expressed the wrong way round because the message is
                    # truncated for output
                    self.__add_msg(_("ADDR element ignored '%s'" % elmn), line, state)
            # The free-form address ADDR is discarded
            # Assemble a title out of structured address
            for elmn in str_list:
                if elmn:
                    if title != "":
                        # TODO for Arabic, should the next comma be translated?
                        title += ", "
                    title += elmn
            return title

    def __parse_trailer(self):
        """
        Looks for the expected TRLR token
        """
        try:
            line = self.__get_next_line()
            if line and line.token != TOKEN_TRLR:
                state = CurrentState()
                self.__not_recognized(line, state)
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
        researcher = Researcher()
        state = CurrentState()
        state.res = researcher
        state.level = 1
        repo = Repository()
        state.repo = repo
        self.__parse_level(state, self.subm_parse_tbl, self.__undefined)
        # If this is the submitter that we were told about in the HEADer, then
        # we will need to update the researcher
        if line.token_text == self.subm and self.import_researcher:
            self.dbase.set_researcher(state.res)

        localized_submitter = _("(Submitter):")
        if state.res.get_name() == "":
            submitter_name = "SUBM %s @%s@" % (localized_submitter, line.token_text)
        else:
            submitter_name = "SUBM %s (@%s@) %s" % (
                localized_submitter,
                line.token_text,
                state.res.get_name(),
            )
        if self.use_def_src:
            repo.set_name(submitter_name)
            repo.set_handle(create_id())
            repo.set_gramps_id(self.rid_map[""])

            addr = Address()
            addr.set_street(state.res.get_address())
            addr.set_locality(state.res.get_locality())
            addr.set_city(state.res.get_city())
            addr.set_state(state.res.get_state())
            addr.set_country(state.res.get_country())
            addr.set_postal_code(state.res.get_postal_code())
            addr.set_county(state.res.get_county())
            addr.set_phone(state.res.get_phone())
            repo.add_address(addr)
            rtype = RepositoryType()
            rtype.set((RepositoryType.CUSTOM, _("GEDCOM data")))
            repo.set_type(rtype)
            self.__check_msgs(submitter_name, state, repo)
            self.dbase.commit_repository(repo, self.trans, state.repo.change)
            repo_ref = RepoRef()
            repo_ref.set_reference_handle(repo.handle)
            mtype = SourceMediaType()
            mtype.set((SourceMediaType.UNKNOWN, ""))
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

        This also deals with the SUBN (submission) record, of which there
        should be exactly one.
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
            elif key == "SUBN":
                state = CurrentState(level=1)
                self.__parse_submission(line, state)
                self.__check_msgs(_("Top Level"), state, None)
            elif line.token in (TOKEN_SUBM, TOKEN_SUBN, TOKEN_IGNORE):
                state = CurrentState()
                self.__skip_subordinate_levels(1, state)
                self.__check_msgs(_("Top Level"), state, None)
            elif key in ("SOUR", "SOURCE"):
                self.__parse_source(line.token_text, 1)
            elif line.data.startswith("SOUR ") or line.data.startswith("SOURCE "):
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
                self.__not_recognized(line, state)
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

    # ----------------------------------------------------------------------
    #
    # INDI parsing
    #
    # ----------------------------------------------------------------------

    def __parse_indi(self, line):
        """
        Handling of the GEDCOM INDI tag and all lines subordinate to the
        current line.

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

        # Add a default tag if provided
        self.__add_default_tag(person)

        # Set up primary photo if present
        self.__do_photo(state)

        self.__check_msgs(
            _("INDI (individual) Gramps ID %s") % person.get_gramps_id(), state, person
        )
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

    def __person_refn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__do_refn(line, state, state.person)

    def __person_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type((AttributeType.CUSTOM, line.token_text))
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
        # parse table is encountered. The tag may be of the form "_XXX".  We
        # try to convert to a friendly name, if fails use the tag itself as
        # the TYPE in a custom event
        cust_tag = CUSTOMEVENTTAGS.get(line.token_text, line.token_text)
        cust_type = EventType((EventType.CUSTOM, cust_tag))
        event_ref = self.__build_event_pair(
            state, cust_type, self.event_parse_tbl, str(line.data)
        )
        state.person.add_event_ref(event_ref)

    def __fam_even(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_family_event_pair(
            state, EventType.CUSTOM, self.event_parse_tbl, line.data
        )
        state.family.add_event_ref(event_ref)

    def __person_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.person, state.level + 1, state)

    def __person_resn(self, line, state):
        """
        Parses the RESN tag, adding it as an attribute.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type((AttributeType.CUSTOM, "RESN"))
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
        illegal (ALIA or ALIAS) or non-standard (_ALIA) GEDCOM. "1 ALIA" is
        used by Family Tree Maker and Reunion. "1 ALIAS" and "1 _ALIA" do not
        appear to be used.

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
        if line.data == "":
            self.__add_msg(_("Empty Alias <NAME PERSONAL> ignored"), line, state)
            self.__skip_subordinate_levels(state.level + 1, state)
        elif line.data[0] == "@":
            handle = self.__find_person_handle(self.pid_map[line.data])
            ref = PersonRef()
            ref.ref = handle
            ref.rel = "Alias"
            state.person.add_person_ref(ref)
        else:
            self.__parse_alias_name(line, state)

    def __parse_alias_name(self, line, state):
        """
        Parse a level 1 alias name and subsidiary levels when called from
        __person_alt_name (when the <NAME_PERSONAL> does not start with @).
        Also parses a level 2 alias name and subsidiary levels when called
        from __name_alias.

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
        name.set_type(NameType.AKA)
        state.person.add_alternate_name(name)

        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = state.level + 1

        self.__parse_level(sub_state, self.name_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __person_object(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__obje(line, state, state.person)

    def __person_photo(self, line, state):
        """
        This handles the FTM _PHOTO feature, which identifies an OBJE to use
        as the person's primary photo.
        """
        state.photo = line.data  # Just save it for now.

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

        # build a Name structure from the text

        name = self.__parse_name_personal(line.data)

        # Add the name as the primary name if this is the first one that
        # we have encountered for this person. Assume that if this is the
        # first name, that it is a birth name. Otherwise, label it as an
        # "Also Known As (AKA)". GEDCOM does not seem to have the concept
        # of different name types

        if state.name_cnt == 0:
            name.set_type(NameType.BIRTH)
            state.person.set_primary_name(name)
        else:
            name.set_type(NameType.AKA)
            state.person.add_alternate_name(name)
        state.name_cnt += 1

        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = state.level + 1

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
        event_ref = self.__build_event_pair(
            state, EventType.CUSTOM, self.event_parse_tbl, line.data
        )
        state.person.add_event_ref(event_ref)

    def __person_std_event(self, line, state):
        """
        Parses GEDCOM event types that map to a Gramps standard type.
        Additional parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        event = line.data
        event.set_gramps_id(self.emapper.find_next())
        event_ref = EventRef()
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.event = event
        sub_state.event_ref = event_ref
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

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
        event_ref = self.__build_event_pair(
            state, EventType.RELIGION, self.event_parse_tbl, line.data
        )
        state.person.add_event_ref(event_ref)

    def __person_birt(self, line, state):
        """
        Parses GEDCOM BIRT tag into a Gramps birth event. Additional work
        must be done, since additional handling must be done by Gramps to set
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
        event_ref = self.__build_event_pair(
            state, EventType.BIRTH, self.event_parse_tbl, line.data
        )
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
        event_ref = self.__build_event_pair(
            state, EventType.ADOPT, self.adopt_parse_tbl, line.data
        )
        state.person.add_event_ref(event_ref)

    def __person_deat(self, line, state):
        """
        Parses GEDCOM DEAT tag into a Gramps birth event. Additional work
        must be done, since additional handling must be done by Gramps to set
        this up as a death reference event.

           n  DEAT [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event_ref = self.__build_event_pair(
            state, EventType.DEATH, self.event_parse_tbl, line.data
        )
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
        self.__parse_note(line, state.person, state)

    def __person_rnote(self, line, state):
        """
        Parses a note associated with the person

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.person, state)

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
        n PHON <PHONE_NUMBER> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.is_ftw:
            self.__person_resi(line, state)
            return
        free_form = line.data

        sub_state = CurrentState(level=state.level + 1)
        sub_state.addr = Address()

        self.__parse_level(sub_state, self.parse_addr_tbl, self.__ignore)
        state.msg += sub_state.msg

        self.__merge_address(free_form, sub_state.addr, line, state)
        state.person.add_address(sub_state.addr)

    def __person_resi(self, line, state):
        """
        Parses GEDCOM ADDR tag, subordinate to the INDI tag, when sourced by
        FTM.  We treat this as a RESI event, because FTM puts standard event
        details below the ADDR line.

           n  ADDR <ADDRESS_LINE> {0:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.backoff = True  # reprocess the current ADDR line
        line.level += 1  # as if it was next level down
        event_ref = self.__build_event_pair(
            state, EventType.RESIDENCE, self.event_parse_tbl, ""
        )
        state.person.add_event_ref(event_ref)

    def __person_phon(self, line, state):
        """
        n PHON <PHONE_NUMBER> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(_("Phone")))
        state.person.add_url(url)

    def __person_fax(self, line, state):
        """
        O INDI
        1 FAX <PHONE_NUMBER> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(_("FAX")))
        state.person.add_url(url)

    def __person_email(self, line, state):
        """
        O INDI
        1 EMAIL <EMAIL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(UrlType.EMAIL))
        state.person.add_url(url)

    def __person_www(self, line, state):
        """
        O INDI
        1 WWW <URL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(UrlType.WEB_HOME))
        state.person.add_url(url)

    def __person_titl(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event = Event()
        event_ref = EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(EventType.NOB_TITLE)
        event.set_description(line.data)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.event = event
        sub_state.event_ref = event_ref
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

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
            state.name.set_type(NameType.AKA)
        elif line.data.upper() in ("_MAR", "_MARN", "_MARNM", "MARRIED"):
            state.name.set_type(NameType.MARRIED)
        else:
            state.name.set_type((NameType.CUSTOM, line.data))

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
        self.__parse_note(line, state.name, state)

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
        by GTEdit and Brother's keeper 5.2 for windows. It had been supported
        in previous versions of Gramps but as it was probably incorrectly coded
        as it would only work if the name started with '@'.

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
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_givn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_first_name(line.data.strip())
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_spfx(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        spfx = line.data.strip().split(", ")[0]
        if state.name.get_surname_list():
            state.name.get_surname_list()[0].set_prefix(spfx)
        else:
            surn = Surname()
            surn.set_prefix(spfx)
            surn.set_primary()
            state.name.set_surname_list([surn])
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_surn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        names = line.data.strip().split(", ")
        overwrite = bool(state.name.get_surname_list())
        for name in names:
            if overwrite:
                state.name.get_surname_list()[0].set_surname(name)
                overwrite = False
            else:
                surn = Surname()
                surn.set_surname(name)
                surn.set_primary(primary=not state.name.get_surname_list())
                state.name.get_surname_list().append(surn)
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_marnm(self, line, state):
        """
        This is non-standard GEDCOM. _MARNM is reported to be used in Ancestral
        Quest and Personal Ancestral File 5. This will also handle a usage
        which has been found in Brother's Keeper (BROSKEEP VERS 6.1.31 WINDOWS)
        as follows:

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
            name = Name(state.person.primary_name)
            surn = Surname()
            surn.set_surname(data[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
            name.set_type(NameType.MARRIED)
            state.person.add_alternate_name(name)
        elif len(data) > 1:
            name = self.__parse_name_personal(text)
            name.set_type(NameType.MARRIED)
            state.person.add_alternate_name(name)

    def __name_nsfx(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.name.get_suffix() == "" or state.name.get_suffix() == line.data:
            # suffix might be set before when parsing name string
            state.name.set_suffix(line.data)
        else:
            # previously set suffix different, to not loose information, append
            state.name.set_suffix(state.name.get_suffix() + " " + line.data)
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_nick(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_nick_name(line.data.strip())
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_call(self, line, state):
        """
        This parses the inofficial _RUFNAME tag that indicates which part
        of a person's given name is commonly used to address them.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.name.set_call_name(line.data.strip())
        self.__skip_subordinate_levels(state.level + 1, state)

    def __name_aka(self, line, state):
        """
        This parses the non-standard GEDCOM tags _AKA or _AKAN as a subsidiary
        to the NAME tag, which is reported to have been found in Ancestral
        Quest and Personal Ancestral File 4 and 5. Note: example AQ and PAF
        files have separate 2 NICK and 2 _AKA lines for the same person. The
        NICK will be stored by Gramps in the nick_name field of the name
        structure, while the _AKA, if it is a single word, will be stored in
        the NICKNAME attribute. If more than one word it is stored as an AKA
        alternate name.

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
            attr = Attribute()
            attr.set_type(AttributeType.NICKNAME)
            attr.set_value(line.data)
            state.person.add_attribute(attr)
        elif name_len == 0:
            return
        else:
            name = Name()
            surname = Surname()
            surname.set_surname(lname[-1].strip())
            surname.set_primary()
            name.set_surname_list([surname])
            name.set_first_name(" ".join(lname[0 : name_len - 1]))
            #            name = self.__parse_name_personal(line.data)
            name.set_type(NameType.AKA)
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
            name = Name(state.person.primary_name)
            surn = Surname()
            surn.set_surname(data[0].strip())
            surn.set_primary()
            name.set_surname_list([surn])
            name.set_type((NameType.CUSTOM, "Adopted"))
            state.person.add_alternate_name(name)
        elif len(data) > 1:
            name = self.__parse_name_personal(text)
            name.set_type((NameType.CUSTOM, "Adopted"))
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
        Parses an TOKEN that Gramps recognizes as an Attribute

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.attr = line.data
        sub_state.level = state.level + 1
        state.person.add_attribute(sub_state.attr)
        self.__parse_level(sub_state, self.person_attr_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

    def __person_fact(self, line, state):
        """
        Parses an TOKEN that Gramps recognizes as an Attribute

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.attr = Attribute()
        sub_state.attr.set_value(line.data)
        sub_state.level = state.level + 1
        state.person.add_attribute(sub_state.attr)
        self.__parse_level(sub_state, self.person_fact_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

    def __person_fact_type(self, line, state):
        state.attr.set_type(line.data)

    def __person_bapl(self, line, state):
        """
        Parses an BAPL TOKEN, producing a Gramps LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, LdsOrd.BAPTISM)

    def __person_conl(self, line, state):
        """
        Parses an CONL TOKEN, producing a Gramps LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, LdsOrd.CONFIRMATION)

    def __person_endl(self, line, state):
        """
        Parses an ENDL TOKEN, producing a Gramps LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, LdsOrd.ENDOWMENT)

    def __person_slgc(self, line, state):
        """
        Parses an SLGC TOKEN, producing a Gramps LdsOrd instance

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.build_lds_ord(state, LdsOrd.SEAL_TO_PARENTS)

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
        sub_state.lds_ord = LdsOrd()
        sub_state.lds_ord.set_type(lds_type)
        sub_state.place = None
        sub_state.place_fields = PlaceParser()
        sub_state.person = state.person
        state.person.lds_ord_list.append(sub_state.lds_ord)

        self.__parse_level(sub_state, self.lds_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

        if sub_state.place:
            place_title = _pd.display(self.dbase, sub_state.place)
            sub_state.place_fields.load_place(
                self.place_import, sub_state.place, place_title
            )

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
            place = self.__find_place(title, None, None)
            if place is None:
                place = Place()
                place.set_title(title)
                place.name.set_value(title)
                self.dbase.add_place(place, self.trans)
                self.place_names[place.get_title()].append(place.get_handle())
            else:
                pass
            state.lds_ord.set_place_handle(place.handle)
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
        self.__parse_note(line, state.lds_ord, state)

    def __lds_stat(self, line, state):
        """
        Parses the STAT (status) tag attached to the LdsOrd.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        status = LDS_STATUS.get(line.data, LdsOrd.STATUS_NONE)
        state.lds_ord.set_status(status)

    def __person_famc(self, line, state):
        """
        Handles the parsing of the FAMC line, which indicates which family the
        person is a child of.

        n FAMC @<XREF:FAM>@ {1:1}
        +1 PEDI <PEDIGREE_LINKAGE_TYPE> {0:1} p.*
        +1 _FREL <Father relationship type> {0:1}   non-standard Extension
        +1 _MREL <Mother relationship type> {0:1}   non-standard Extension
        +1 <<NOTE_STRUCTURE>> {0:M} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """

        if not line.data:  # handles empty FAMC line
            self.__not_recognized(line, state)
            return
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

        flist = state.person.get_parent_family_handle_list()
        if handle not in flist:
            state.person.add_parent_family_handle(handle)

            # search childrefs
            family, _new = self.dbase.find_family_from_handle(handle, self.trans)
            family.set_gramps_id(gid)

            for ref in family.get_child_ref_list():
                if ref.ref == state.person.handle:
                    break
            else:
                ref = ChildRef()
                ref.ref = state.person.handle
                family.add_child_ref(ref)
            if sub_state.ftype:
                ref.set_mother_relation(sub_state.ftype)
                ref.set_father_relation(sub_state.ftype)
            else:
                if sub_state.frel:
                    ref.set_father_relation(sub_state.frel)
                if sub_state.mrel:
                    ref.set_mother_relation(sub_state.mrel)
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
        state.ftype = PEDIGREE_TYPES.get(line.data.lower(), ChildRefType.UNKNOWN)

    def __person_famc_frel(self, line, state):
        """
        Parses the _FREL tag attached to a INDI.FAMC record. No values are set
        at this point, because we have to do some post processing. Instead, we
        assign the frel field of the state variable. We convert the text from
        the line to an index into the PEDIGREE_TYPES dictionary, which will map
        to the correct ChildTypeRef.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.frel = PEDIGREE_TYPES.get(line.data.lower().strip(), None)
        if state.frel is None:
            state.frel = ChildRefType(line.data.capitalize().strip())

    def __person_famc_mrel(self, line, state):
        """
        Parses the _MREL tag attached to a INDI.FAMC record. No values are set
        at this point, because we have to do some post processing. Instead, we
        assign the mrel field of the state variable. We convert the text from
        the line to an index into the PEDIGREE_TYPES dictionary, which will map
        to the correct ChildTypeRef.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.mrel = PEDIGREE_TYPES.get(line.data.lower().strip(), None)
        if state.mrel is None:
            state.mrel = ChildRefType(line.data.capitalize().strip())

    def __person_famc_note(self, line, state):
        """
        Parses the INDI.FAMC.NOTE tag .

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.person, state)

    def __person_famc_primary(self, line, state):
        """
        Parses the _PRIMARY tag on an INDI.FAMC tag. This value is stored in
        the state record to be used later.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.primary = True

    def __person_famc_sour(self, line, state):
        """
        Parses the SOUR tag on an INDI.FAMC tag. Gramps has no corresponding
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

        sub_state = CurrentState(level=state.level + 1)
        sub_state.obj = state.person
        self.__parse_level(sub_state, self.opt_note_tbl, self.__ignore)
        state.msg += sub_state.msg

    def __person_asso(self, line, state):
        """
        Parse the ASSO tag, add the referenced person to the person we
        are currently parsing. The GEDCOM spec indicates that valid ASSO tag
        is:

        n ASSO @<XREF:INDI>@ {0:M}

        And the sub tags are:

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
        sub_state.ref = PersonRef()
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
        self.__parse_note(line, state.ref, state)

    # -------------------------------------------------------------------
    #
    # FAM parsing
    #
    # -------------------------------------------------------------------

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

        # Add a default tag if provided
        self.__add_default_tag(family)

        self.__check_msgs(
            _("FAM (family) Gramps ID %s") % family.get_gramps_id(), state, family
        )
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
        Parses GEDCOM event types that map to a Gramps standard type.
        Additional parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        event = line.data
        event.set_gramps_id(self.emapper.find_next())
        event_ref = EventRef()
        event_ref.set_role(EventRoleType.FAMILY)
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.event = event
        sub_state.event_ref = event_ref
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

        if event.type == EventType.MARRIAGE:
            descr = event.get_description()
            if descr == "Civil Union":
                state.family.type.set(FamilyRelType.CIVIL_UNION)
                event.set_description("")
            elif descr == "Unmarried":
                state.family.type.set(FamilyRelType.UNMARRIED)
                event.set_description("")
            else:
                state.family.type.set(FamilyRelType.MARRIED)
            if descr == "Y":
                event.set_description("")

        self.dbase.commit_event(event, self.trans)
        event_ref.ref = event.handle
        state.family.add_event_ref(event_ref)

    def __family_even(self, line, state):
        """
        Parses GEDCOM event types that map to a Gramps standard type.
        Additional parsing required is for the event detail:

           +1 <<EVENT_DETAIL>> {0:1} p.*

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # We can get here when a tag that is not valid in the family_func
        # parse table is encountered. The tag may be of the form "_XXX".  We
        # try to convert to a friendly name, if fails use the tag itself as
        # the TYPE in a custom event
        cust_tag = CUSTOMEVENTTAGS.get(line.token_text, line.token_text)
        cust_type = EventType((EventType.CUSTOM, cust_tag))
        event = Event()
        event_ref = EventRef()
        event_ref.set_role(EventRoleType.FAMILY)
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(cust_type)
        # in case a description ever shows up
        if line.data and line.data != "Y":
            event.set_description(str(line.data))
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.level = state.level + 1
        sub_state.event = event
        sub_state.event_ref = event_ref
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, self.event_parse_tbl, self.__undefined)
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

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

        reflist = [
            ref for ref in state.family.get_child_ref_list() if ref.ref == child.handle
        ]

        if reflist:  # The child has been referenced already
            ref = reflist[0]
            if sub_state.frel:
                ref.set_father_relation(sub_state.frel)
            if sub_state.mrel:
                ref.set_mother_relation(sub_state.mrel)
            # then we will set the order now:
            self.set_child_ref_order(state.family, ref)
        else:
            ref = ChildRef()
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
        sub_state.lds_ord = LdsOrd()
        sub_state.lds_ord.set_type(LdsOrd.SEAL_TO_SPOUSE)
        sub_state.place = None
        sub_state.family = state.family
        sub_state.place_fields = PlaceParser()
        state.family.lds_ord_list.append(sub_state.lds_ord)

        self.__parse_level(sub_state, self.lds_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

        if sub_state.place:
            place_title = _pd.display(self.dbase, sub_state.place)
            sub_state.place_fields.load_place(
                self.place_import, sub_state.place, place_title
            )

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
        self.__obje(line, state, state.family)

    def __family_comm(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        note = line.data
        state.family.add_note(note)
        self.__skip_subordinate_levels(state.level + 1, state)

    def __family_note(self, line, state):
        """
        +1 <<NOTE_STRUCTURE>>  {0:M}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.family, state)

    def __family_chan(self, line, state):
        """
        +1 <<CHANGE_DATE>>  {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.family, state.level + 1, state)

    def __family_attr(self, line, state):
        """
        Parses an TOKEN that Gramps recognizes as an Attribute
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.attr = line.data
        sub_state.level = state.level + 1
        state.family.add_attribute(line.data)
        self.__parse_level(sub_state, self.person_attr_parse_tbl, self.__ignore)
        state.msg += sub_state.msg

    def __family_refn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__do_refn(line, state, state.family)

    def __family_cust_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(line.token_text)
        attr.set_value(line.data)
        state.family.add_attribute(attr)

    def __obje(self, line, state, pri_obj):
        """
        Embedded form

           n OBJE @<XREF:OBJE>@ {1:1}
           +1 _PRIM <Y/N>       {0:1}                # Indicates primary photo

         Linked form

           n  OBJE {1:1}
           +1 FORM <MULTIMEDIA_FORMAT> {1:1}         # v5.5 layout
           +1 TITL <DESCRIPTIVE_TITLE> {0:1}
           +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1} # v5.5.1 allows multiple
             +2 FORM <MULTIMEDIA_FORMAT> {1:1}       # v5.5.1 layout
               +3 MEDI <SOURCE_MEDIA_TYPE> {0:1}     # v5.5.1 layout
           +1 <<NOTE_STRUCTURE>> {0:M}
           +1 _PRIM <Y/N>       {0:1}                # Indicates primary photo

         @param line: The current line in GedLine format
         @type line: GedLine
         @param state: The current state
         @type state: CurrentState
         @param pri_obj: The Primary object to which this is attached
         @type state: Person # or Family, or Source etc.
        """
        if line.data and line.data[0] == "@":
            # Reference to a named multimedia object defined elsewhere
            gramps_id = self.oid_map[line.data]
            handle = self.__find_media_handle(gramps_id)
            # check to see if this is a primary photo
            line = self.__chk_subordinate(state.level + 1, state, TOKEN__PRIM)
            if line and line.data == "Y":
                state.photo = handle
            oref = MediaRef()
            oref.set_reference_handle(handle)
            pri_obj.add_media_reference(oref)
            return
        #
        # The remainder of this code is similar in concept to __parse_obje
        # except that it combines references to the same media file by
        # comparing path names.  If they are the same, then only the first
        # is kept.  This does mean that if there are different notes etc. on a
        # later OBJE, they will be lost.
        #
        sub_state = CurrentState()
        sub_state.form = ""
        sub_state.attr = None
        sub_state.filename = ""
        sub_state.title = ""
        sub_state.media = Media()
        sub_state.level = state.level + 1
        sub_state.prim = ""

        self.__parse_level(sub_state, self.media_parse_tbl, self.__ignore)
        state.msg += sub_state.msg
        if sub_state.filename == "":
            self.__add_msg(_("Filename omitted"), line, state)
        # The following lines are commented out because Gramps is NOT a
        # Gedcom validator!
        # if sub_state.form == "":
        #     self.__add_msg(_("Form omitted"), line, state)

        # The following code that detects URL is an older v5.5 usage; the
        # modern option is to use the EMAIL tag.
        if isinstance(sub_state.form, str) and sub_state.form == "url":
            if isinstance(pri_obj, UrlBase):
                url = Url()
                url.set_path(sub_state.filename)
                url.set_description(sub_state.title)
                url.set_type(UrlType.WEB_HOME)
                pri_obj.add_url(url)
            else:  # some primary objects (Event) son't have spot for URL
                new_note = Note(sub_state.filename)
                new_note.set_gramps_id(self.nid_map[""])
                new_note.set_handle(create_id())
                new_note.set_type(
                    OBJ_NOTETYPE.get(type(pri_obj).__name__, NoteType.GENERAL)
                )
                self.dbase.commit_note(new_note, self.trans, new_note.change)
                pri_obj.add_note(new_note.get_handle())

        else:
            # to allow import of references to URLs (especially for import from
            # geni.com), do not try to find the file if it is blatently a URL
            res = urlparse(sub_state.filename)
            if sub_state.filename != "" and (
                res.scheme == "" or len(res.scheme) == 1 or res.scheme == "file"
            ):
                (valid, path) = self.__find_file(sub_state.filename, self.dir_path)
                if not valid:
                    self.__add_msg(
                        _("Could not import %s") % sub_state.filename, line, state
                    )
            else:
                path = sub_state.filename
            # Multiple references to the same media silently drops the later
            # ones, even if title, etc.  are different
            photo_handle = self.media_map.get(path)
            if photo_handle is None:
                photo = Media()
                photo.set_path(path)
                if sub_state.title:
                    photo.set_description(sub_state.title)
                else:
                    photo.set_description(path.replace("\\", "/"))
                full_path = os.path.abspath(path)
                # deal with mime types
                value = mimetypes.guess_type(full_path)
                if value and value[0]:  # found from filename
                    photo.set_mime_type(value[0])
                else:  # get from OBJE.FILE.FORM
                    if "/" in sub_state.form:  # already has expanded mime type
                        photo.set_mime_type(sub_state.form)
                    else:
                        value = mimetypes.types_map.get(
                            "." + sub_state.form, _("unknown")
                        )
                        photo.set_mime_type(value)
                if sub_state.attr:
                    photo.attribute_list.append(sub_state.attr)
                self.dbase.add_media(photo, self.trans)
                self.media_map[path] = photo.handle
            else:
                photo = self.dbase.get_media_from_handle(photo_handle)
            # copy notes to our media
            for note in sub_state.media.get_note_list():
                photo.add_note(note)
            self.dbase.commit_media(photo, self.trans)

            if sub_state.prim == "Y":
                state.photo = photo.handle
            oref = MediaRef()
            oref.set_reference_handle(photo.handle)
            pri_obj.add_media_reference(oref)

    def __media_ref_form(self, line, state):
        """
          +1 FORM <MULTIMEDIA_FORMAT> {1:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.form = line.data.lower()

    def __media_ref_medi(self, line, state):
        """
          +1 MEDI <SOURCE_MEDIA_TYPE> {0:1}   (Photo, Audio, Book, etc.)

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.attr = Attribute()
        mtype = MEDIA_MAP.get(line.data.lower(), (SourceMediaType.CUSTOM, line.data))
        state.attr.set_type(_("Media-Type"))
        state.attr.set_value(str(SourceMediaType(mtype)))

    def __media_ref_titl(self, line, state):
        """
          +1 TITL <DESCRIPTIVE_TITLE> {0:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.title = line.data

    def __media_ref_file(self, line, state):
        """
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.filename != "":
            self.__add_msg(_("Multiple FILE in a single OBJE ignored"), line, state)
            self.__skip_subordinate_levels(state.level + 1, state)
            return
        state.filename = line.data

    def __media_ref_prim(self, line, state):
        """
          +1 _PRIM <Y/N> {0:1}

        Indicates that this OBJE is the primary photo.

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.prim = line.data

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
        self.__obje(line, state, state.event)

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
                name = EventType(GED_TO_GRAMPS_EVENT[line.data])
            else:
                try:
                    name = EventType((EventType.CUSTOM, line.data))
                except AttributeError:
                    name = EventType(EventType.UNKNOWN)
            state.event.set_type(name)
        else:
            try:
                if line.data not in GED_TO_GRAMPS_EVENT and line.data[0] != "Y":
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

        if (
            self.is_ftw
            and (state.event.type in FTW_BAD_PLACE)
            and not state.event.get_description()
        ):
            state.event.set_description(line.data)
        else:
            place = state.place
            if place:
                # We encounter a PLAC, having previously encountered an ADDR
                if state.place.place_type.string != _("Address"):
                    # We have previously found a PLAC
                    self.__add_msg(_("A second PLAC ignored"), line, state)
                    # ignore this second PLAC, and use the old one
                else:
                    # This is the first PLAC
                    place.set_title(line.data)
                    place.name.set_value(line.data)
            else:
                # The first thing we encounter is PLAC
                state.place = Place()
                place = state.place
                place.set_title(line.data)
                place.name.set_value(line.data)

            sub_state = CurrentState()
            sub_state.place = place
            sub_state.level = state.level + 1

            self.__parse_level(sub_state, self.event_place_map, self.__undefined)
            state.msg += sub_state.msg
            if sub_state.pf:  # if we found local PLAC:FORM
                state.pf = sub_state.pf  # save to override global value
            # merge notes etc into place
            state.place.merge(sub_state.place)

    def __event_place_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.place, state)

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
        self.__obje(line, state, state.place)

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
        state.place.set_latitude(line.data)

    def __place_long(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.place.set_longitude(line.data)

    def __event_addr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        free_form = line.data

        sub_state = CurrentState(level=state.level + 1)
        sub_state.location = Location()
        sub_state.event = state.event
        sub_state.place = Place()  # temp stash for notes, citations etc

        self.__parse_level(sub_state, self.parse_loc_tbl, self.__undefined)
        state.msg += sub_state.msg

        title = self.__merge_address(free_form, sub_state.location, line, state)

        location = sub_state.location

        if self.addr_is_detail and state.place:
            # Commit the enclosing place
            place = self.__find_place(
                state.place.get_title(), None, state.place.get_placeref_list()
            )
            if place is None:
                place = state.place
                self.dbase.add_place(place, self.trans)
                self.place_names[place.get_title()].append(place.get_handle())
            else:
                place.merge(state.place)
                self.dbase.commit_place(place, self.trans)
            place_title = _pd.display(self.dbase, place)
            state.pf.load_place(self.place_import, place, place_title)

            # Create the Place Details (it is committed with the event)
            place_detail = Place()
            place_detail.set_name(PlaceName(value=title))
            place_detail.set_title(title)
            # For RootsMagic etc. Place Details e.g. address, hospital, ...
            place_detail.set_type((PlaceType.CUSTOM, _("Detail")))
            placeref = PlaceRef()
            placeref.ref = place.get_handle()
            place_detail.set_placeref_list([placeref])
            state.place = place_detail
        else:
            place = state.place
            if place:
                # We encounter an ADDR having previously encountered a PLAC
                if (
                    len(place.get_alternate_locations()) != 0
                    and not self.__get_first_loc(place).is_empty()
                ):
                    # We have perviously found an ADDR, or have populated
                    # location from PLAC title
                    self.__add_msg(
                        _("Location already populated; ADDR " "ignored"), line, state
                    )
                    # ignore this second ADDR, and use the old one
                else:
                    # This is the first ADDR
                    place.add_alternate_locations(location)
            else:
                # The first thing we encounter is ADDR
                state.place = Place()
                place = state.place
                place.add_alternate_locations(location)
                place.set_name(PlaceName(value=title))
                place.set_title(title)
                place.set_type((PlaceType.CUSTOM, _("Address")))

        # merge notes etc into place
        state.place.merge(sub_state.place)

    def __add_location(self, place, location):
        """
        @param place: A place object we have found or created
        @type place: Place
        @param location: A location we want to add to this place
        @type location: gen.lib.location
        """
        for loc in place.get_alternate_locations():
            if loc.is_equivalent(location) == IDENTICAL:
                return
        place.add_alternate_locations(location)

    def __get_first_loc(self, place):
        """
        @param place: A place object
        @type place: Place
        @return location: the first alternate location if any else None
        @type location: gen.lib.location
        """
        if len(place.get_alternate_locations()) == 0:
            return None
        else:
            return place.get_alternate_locations()[0]

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
        self.__parse_note(line, state.event, state)

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
            self.__parse_note(line, state.event, state)

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
        attr = Attribute()
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

    def __event_phon(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(_("Phone"))
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_fax(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(_("FAX"))
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_email(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(_("EMAIL"))
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_www(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(_("WWW"))
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_cause(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(AttributeType.CAUSE)
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
        attr = Attribute()
        attr.set_type(AttributeType.AGE)
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
            if self.__level_is_finished(line, state.level + 1):
                break
            elif line.token == TOKEN_AGE:
                attr = Attribute()
                attr.set_type(AttributeType.FATHER_AGE)
                attr.set_value(line.data)
                state.event_ref.add_attribute(attr)
            elif line.token == TOKEN_WIFE:
                # wife event can be on same level, if so call it and finish
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
            if self.__level_is_finished(line, state.level + 1):
                break
            elif line.token == TOKEN_AGE:
                attr = Attribute()
                attr.set_type(AttributeType.MOTHER_AGE)
                attr.set_value(line.data)
                state.event_ref.add_attribute(attr)
            elif line.token == TOKEN_HUSB:
                # husband event can be on same level, if so call it and finish
                self.__event_husb(line, state)
                break

    def __event_agnc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(AttributeType.AGENCY)
        attr.set_value(line.data)
        state.event.add_attribute(attr)

    def __event_time(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if hasattr(state, "event"):
            # read in time as attribute of event
            attr = Attribute()
            attr.set_type(AttributeType.TIME)
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
            assert state.event.handle  # event handle is required to be set
            wit = self.__find_or_create_person(self.pid_map[line.data])
            event_ref = EventRef()
            event_ref.set_reference_handle(state.event.handle)
            while True:
                line = self.__get_next_line()
                if self.__level_is_finished(line, state.level + 1):
                    break
                elif line.token == TOKEN_TYPE:
                    if line.data == "WITNESS_OF_MARRIAGE":
                        role = EventRoleType(EventRoleType.WITNESS)
                    else:
                        role = EventRoleType((EventRoleType.CUSTOM, line.data))
                    event_ref.set_role(role)
            wit.add_event_ref(event_ref)
            self.dbase.commit_person(wit, self.trans)
        else:
            # n _WITN <TEXTUAL_LIST_OF_NAMES>
            attr = Attribute()
            attr.set_type(AttributeType.WITNESS)
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

        sub_state = CurrentState(level=state.level + 1)
        sub_state.mrel = TYPE_BIRTH
        sub_state.frel = TYPE_BIRTH

        self.__parse_level(sub_state, self.parse_person_adopt, self.__undefined)
        state.msg += sub_state.msg

        if (
            int(sub_state.mrel) == ChildRefType.BIRTH
            and int(sub_state.frel) == ChildRefType.BIRTH
        ):
            sub_state.mrel = sub_state.frel = TYPE_ADOPT

        state.person.add_parent_family_handle(handle)

        reflist = [
            ref for ref in family.get_child_ref_list() if ref.ref == state.person.handle
        ]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(sub_state.frel)
            ref.set_mother_relation(sub_state.mrel)
        else:
            ref = ChildRef()
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

        state.person.add_parent_family_handle(handle)

        frel = mrel = ChildRefType.BIRTH

        family, _new = self.dbase.find_family_from_handle(handle, self.trans)
        reflist = [
            ref for ref in family.get_child_ref_list() if ref.ref == state.person.handle
        ]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
        else:
            ref = ChildRef()
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
        # assert state.addr.get_street() == ""
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
        self.__parse_note(line, state.addr, state)

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
        sub_state = CurrentState(level=state.level + 1)
        sub_state.citation = state.citation

        self.__parse_level(sub_state, self.citation_data_tbl, self.__undefined)
        state.msg += sub_state.msg

    def __citation_data_date(self, line, state):
        state.citation.set_date_object(line.data)

    def __source_text(self, line, state):
        note = Note()
        note.set(line.data)
        gramps_id = self.nid_map[""]
        note.set_gramps_id(gramps_id)
        note.set_type(NoteType.SOURCE_TEXT)
        self.dbase.add_note(note, self.trans)

        state.source.add_note(note.get_handle())

    def __citation_data_text(self, line, state):
        note = Note()
        note.set(line.data)
        gramps_id = self.nid_map[""]
        note.set_gramps_id(gramps_id)
        note.set_type(NoteType.SOURCE_TEXT)
        self.dbase.add_note(note, self.trans)

        state.citation.add_note(note.get_handle())

    def __citation_link(self, line, state):
        """
        Not legal GEDCOM - added to support FTM, converts the _LINK tag to a
        note with styled text so link can be followed in reports etc.
        """
        note = Note()
        tags = StyledTextTag(StyledTextTagType.LINK, line.data, [(0, len(line.data))])
        note.set_styledtext(StyledText(line.data, [tags]))
        gramps_id = self.nid_map[""]
        note.set_gramps_id(gramps_id)
        note.set_type(NoteType.CITATION)
        self.dbase.add_note(note, self.trans)
        state.citation.add_note(note.get_handle())

    def __citation__just(self, line, state):
        """
        Not legal GEDCOM - added to support FTM, converts the _JUST tag to a
        note.  This tag represents the Justification for a source.
        """
        note = Note()
        note.set(line.data)
        gramps_id = self.nid_map[""]
        note.set_gramps_id(gramps_id)
        note.set_type(_("Citation Justification"))
        self.dbase.add_note(note, self.trans)
        state.citation.add_note(note.get_handle())

    def __citation__apid(self, line, state):
        """
        Not legal GEDCOM - added to support Ancestry.com, converts the
        _APID tag to an attribute. This tag identifies the location of
        the cited page in the relevant Ancestry.com database.
        """
        sattr = SrcAttribute()
        sattr.set_type("_APID")
        sattr.set_value(line.data)
        state.citation.add_attribute(sattr)

    def __citation_data_note(self, line, state):
        self.__parse_note(line, state.citation, state)

    def __citation_obje(self, line, state):
        """
        Parses the OBJE line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__obje(line, state, state.citation)

    def __citation_refn(self, line, state):
        """
        Parses the REFN line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__add_msg(_("REFN ignored"), line, state)
        self.__skip_subordinate_levels(state.level + 1, state)

    def __citation_even(self, line, state):
        """
        Parses the EVEN line of an SOUR instance tag

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sattr = SrcAttribute()
        sattr.set_type("EVEN")
        sattr.set_value(line.data)
        state.citation.add_attribute(sattr)
        sub_state = CurrentState(level=state.level + 1)
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
        sattr = SrcAttribute()
        sattr.set_type("EVEN:ROLE")
        sattr.set_value(line.data)
        state.citation.add_attribute(sattr)

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
            state.citation.set_confidence_level(val + 1)
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
        self.__parse_note(line, state.citation, state)

    # ----------------------------------------------------------------------
    #
    # SOUR parsing
    #
    # ----------------------------------------------------------------------

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
        state.source.set_title(_("No title - ID %s") % state.source.get_gramps_id())
        state.level = level

        self.__parse_level(state, self.source_func, self.__undefined)
        self.__check_msgs(
            _("SOUR (source) Gramps ID %s") % state.source.get_gramps_id(),
            state,
            state.source,
        )
        self.dbase.commit_source(state.source, self.trans, state.source.change)

    def __source_attr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sattr = SrcAttribute()
        sattr.set_type(line.token_text)
        sattr.set_value(line.data)
        state.source.add_attribute(sattr)
        self.__skip_subordinate_levels(state.level + 1, state)

    def __source_object(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__obje(line, state, state.source)

    def __source_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.source, state.level + 1, state)

    def __source_repo(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data and line.data[0] == "@":
            # This deals with the standard GEDCOM
            # SOURCE_REPOSITORY_CITATION: =
            #   n  REPO @<XREF:REPO>@                {1:1}
            #     +1 <<NOTE_STRUCTURE>>              {0:M}
            #     +1 CALN <SOURCE_CALL_NUMBER>       {0:M}
            #        +2 MEDI <SOURCE_MEDIA_TYPE>     {0:1}
            gid = self.rid_map[line.data]
            repo = self.__find_or_create_repository(gid)
        elif line.data == "":
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
            gid = self.rid_map[""]
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
                gid = self.rid_map[""]
            repo = self.__find_or_create_repository(gid)
            self.repo2id[line.data] = repo.get_gramps_id()
            repo.set_name(line.data)
            self.dbase.commit_repository(repo, self.trans)

        repo_ref = RepoRef()
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
        # self.__skip_subordinate_levels(state.level + 1, state)

    def __repo_ref_medi(self, line, state):
        name = line.data
        mtype = MEDIA_MAP.get(name.lower(), (SourceMediaType.CUSTOM, name))
        state.repo_ref.set_media_type(mtype)

    def __repo_ref_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.repo_ref, state)

    def __repo_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.repo, state.level + 1, state)

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
        attr = Attribute()
        attr.set_type(AttributeType.AGENCY)
        attr.set_value(line.data)
        state.source.add_attribute(attr)

    def __source_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.source, state)

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
        self.__skip_subordinate_levels(state.level + 1, state)

    def __source_title(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.source.set_title(line.data.replace("\n", " "))

    def __source_taxt_peri(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.source.get_title() == "":
            state.source.set_title(line.data.replace("\n", " "))

    # ----------------------------------------------------------------------
    #
    # OBJE parsing
    #
    # ----------------------------------------------------------------------

    def __parse_obje(self, line):
        """
        n  @XREF:OBJE@ OBJE {1:1}                   # v5.5 layout
          +1 FILE <MULTIMEDIA_FILE_REFN> {1:1}      # de-facto extension
          +1 FORM <MULTIMEDIA_FORMAT> {1:1}
          +1 TITL <DESCRIPTIVE_TITLE> {0:1}
          +1 <<NOTE_STRUCTURE>> {0:M} p.*
          +1 BLOB {1:1}                             # Deprecated, no support
            +2 CONT <ENCODED_MULTIMEDIA_LINE> {1:M}
          +1 OBJE @<XREF:OBJE>@ /* chain */ {0:1}   # Deprecated, no support
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
            +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<CHANGE_DATE>> {0:1}

        n @XREF:OBJE@ OBJE {1:1}                    # v5.5.1 layout
          +1 FILE <MULTIMEDIA_FILE_REFN> {1:M}      # multi files, no support
            +2 FORM <MULTIMEDIA_FORMAT> {1:1}
              +3 TYPE <SOURCE_MEDIA_TYPE> {0:1}
            +2 TITL <DESCRIPTIVE_TITLE> {0:1}
            +2 DATE <mm/dd/yyy hh:mn:ss AM> {0:1}   # FTM extension
            +2 TEXT <COMMENT, by user or exif>      # FTM extension
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
            +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
          +1 <<SOURCE_CITATION>> {0:M}
          +1 <<CHANGE_DATE>> {0:1}
        """
        gid = line.token_text.strip()
        media = self.__find_or_create_media(self.oid_map[gid])

        state = CurrentState()
        state.media = media
        state.level = 1

        self.__parse_level(state, self.obje_func, self.__undefined)

        if state.media.get_path() == "":
            self.__add_msg(_("Filename omitted"), line, state)
        # deal with mime types
        value = mimetypes.guess_type(state.media.get_path())
        if value and value[0]:  # found from filename
            state.media.set_mime_type(value[0])
        else:  # get from OBJE.FILE.FORM
            if "/" in state.form:  # already has expanded mime type
                state.media.set_mime_type(state.form)
            else:
                value = mimetypes.types_map.get("." + state.form, _("unknown"))
                state.media.set_mime_type(value)
        # Add the default reference if no source has found
        self.__add_default_source(media)

        # Add a default tag if provided
        self.__add_default_tag(media)

        self.__check_msgs(
            _("OBJE (multi-media object) Gramps ID %s") % media.get_gramps_id(),
            state,
            media,
        )
        # commit the person to the database
        self.dbase.commit_media(media, self.trans, media.change)

    def __obje_form(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.form = line.data.lower().strip()

    def __obje_file(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # The following checks for the odd "feature" of GEDCOM 5.5.1 that
        # allows multiple files to be attached to a single OBJE; not supported
        if state.media.get_path() != "":
            self.__add_msg(_("Multiple FILE in a single OBJE ignored"), line, state)
            self.__skip_subordinate_levels(state.level + 1, state)
            return
        res = urlparse(line.data)
        if line.data != "" and (
            res.scheme == "" or len(res.scheme) == 1 or res.scheme == "file"
        ):
            (file_ok, filename) = self.__find_file(line.data, self.dir_path)
            if state.form != "url":
                # Might not work if FORM doesn't precede FILE
                if not file_ok:
                    self.__add_msg(_("Could not import %s") % line.data, line, state)
            path = filename
        else:
            path = line.data

        state.media.set_path(path)
        if not state.media.get_description():
            state.media.set_description(path.replace("\\", "/"))

    def __obje_title(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.media.set_description(line.data)

    # FTM non-standard TEXT in OBJE, treat as note.
    def __obje_text(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        new_note = Note(line.data)
        new_note.set_gramps_id(self.nid_map[""])
        new_note.set_handle(create_id())
        new_note.set_type(NoteType.MEDIA)
        self.dbase.commit_note(new_note, self.trans, new_note.change)
        state.media.add_note(new_note.get_handle())

    # FTM non-standard DATE in OBJE, treat as Media Date.
    def __obje_date(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.media.set_date_object(line.data)

    def __obje_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.media, state)

    def __obje_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        state.media.add_citation(self.handle_source(line, state.level, state))

    def __obje_refn(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__do_refn(line, state, state.media)

    def __obje_type(self, line, state):
        """
        +1 FILE <MULTIMEDIA_FILE_REFN> {1:M}
          +2 FORM <MULTIMEDIA_FORMAT> {1:1}
            +3 TYPE <SOURCE_MEDIA_TYPE> {0:1}   # v5.5.1

        Source_Media_type is one of (Photo, Audio, Book, etc.)

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        mtype = MEDIA_MAP.get(line.data.lower(), (SourceMediaType.CUSTOM, line.data))
        attr.set_type(_("Media-Type"))
        attr.set_value(str(SourceMediaType(mtype)))
        state.media.attribute_list.append(attr)

    def __obje_rin(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        attr = Attribute()
        attr.set_type(line.token_text)  # Attribute: RIN
        attr.set_value(line.data)
        state.media.attribute_list.append(attr)

    def __obje_chan(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_change(line, state.media, state.level + 1, state)

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
            self.__skip_subordinate_levels(state.level + 1, state)
        else:
            self.__ignore(line, state)

    def __person_attr_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.attr, state)

    # ----------------------------------------------------------------------
    #
    # REPO parsing
    #
    # ----------------------------------------------------------------------

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

        self.__check_msgs(
            _("REPO (repository) Gramps ID %s") % repo.get_gramps_id(), state, repo
        )
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
        self.__parse_note(line, state.repo, state)

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
        n PHON <PHONE_NUMBER> {0:3}

        Some repositories do not try to break up the address,
        instead they put everything on a single line. Try to determine
        if this happened, and try to fix it.
        """
        free_form = line.data

        sub_state = CurrentState(level=state.level + 1)
        sub_state.addr = Address()

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
            if address_list[0].get_phone():
                self.__add_msg(_("Only one phone number supported"), line, state)
            else:
                address_list[0].set_phone(line.data)

    def __repo_fax(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(_("FAX")))
        state.repo.add_url(url)

    def __repo_www(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(UrlType.WEB_HOME))
        state.repo.add_url(url)

    def __repo_email(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        url = Url()
        url.set_path(line.data)
        url.set_type(UrlType(UrlType.EMAIL))
        state.repo.add_url(url)

    def __location_adr1(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
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
            state.location = Location()
        state.location.set_locality(line.data)

    def __location_city(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
        state.location.set_city(line.data)

    def __location_stae(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
        state.location.set_state(line.data)

    def __location_post(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
        state.location.set_postal_code(line.data)

    def __location_ctry(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
        state.location.set_country(line.data)

    def __location_phone(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if not state.location:
            state.location = Location()
        state.location.set_phone(line.data)

    def __location_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if state.event:
            self.__parse_note(line, state.place, state)
        else:
            # This causes notes below SUBMitter to be ignored
            self.__not_recognized(line, state)

    def __optional_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.__parse_note(line, state.obj, state)

    # ----------------------------------------------------------------------
    #
    # HEAD parsing
    #
    # ----------------------------------------------------------------------

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
        self.__check_msgs(_("HEAD (header)"), state, None)

    def __header_sour(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if line.data.strip() in ["FTW", "FTM"]:
            self.is_ftw = True
        # Some software (e.g. RootsMagic (http://files.rootsmagic.com/PAF-
        # Book/RootsMagic-for-PAF-Users-Printable.pdf) use the Addr fields for
        # 'Place Details (address, hospital, cemetary)'
        if line.data.strip().lower() in ["rootsmagic"]:
            self.addr_is_detail = True
        # We will use the approved system ID as the name of the generating
        # software, in case we do not get the name in the proper place
        self.genby = line.data
        if self.use_def_src:
            sattr = SrcAttribute()
            sattr.set_type(_("Approved system identification"))
            sattr.set_value("%s" % self.genby)
            self.def_src.add_attribute(sattr)
        sub_state = CurrentState(level=state.level + 1)
        self.__parse_level(sub_state, self.header_sour_parse_tbl, self.__undefined)
        state.msg += sub_state.msg
        # We can't produce the 'Generated by' statement till the end of the
        # SOUR level, because the name and version may come in any order
        if self.use_def_src:
            # feature request 2356: avoid genitive form
            sattr = SrcAttribute()
            sattr.set_type(_("Generated By"))
            sattr.set_value("%s %s" % (self.genby, self.genvers))
            self.def_src.add_attribute(sattr)

    def __header_sour_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # This is where the name of the product that generated the GEDCOM file
        # should appear, and this will overwrite the approved system ID, if any
        self.genby = line.data
        if self.use_def_src:
            sattr = SrcAttribute()
            sattr.set_type(_("Name of software product"))
            sattr.set_value(self.genby)
            self.def_src.add_attribute(sattr)

    def __header_sour_vers(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        self.genvers = line.data
        if self.use_def_src:
            sattr = SrcAttribute()
            sattr.set_type(_("Version number of software product"))
            sattr.set_value(self.genvers)
            self.def_src.add_attribute(sattr)

    def __header_sour_corp(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        repo = Repository()
        sub_state = CurrentState(level=state.level + 1)
        sub_state.repo = repo
        self.__parse_level(sub_state, self.header_corp_addr, self.__undefined)
        state.msg += sub_state.msg

        if self.use_def_src:
            repo.set_name(_("Business that produced the product: %s") % line.data)
            rtype = RepositoryType()
            rtype.set((RepositoryType.CUSTOM, _("GEDCOM data")))
            repo.set_type(rtype)
            self.dbase.add_repository(repo, self.trans)
            repo_ref = RepoRef()
            repo_ref.set_reference_handle(repo.handle)
            mtype = SourceMediaType()
            mtype.set((SourceMediaType.UNKNOWN, ""))
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
            sattr = SrcAttribute()
            sattr.set_type(_("Name of source data"))
            sattr.set_value(line.data)
            self.def_src.add_attribute(sattr)
        sub_state = CurrentState(level=state.level + 1)
        self.__parse_level(sub_state, self.header_sour_data, self.__undefined)
        state.msg += sub_state.msg

    def __header_sour_copr(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            sattr = SrcAttribute()
            sattr.set_type(_("Copyright of source data"))
            sattr.set_value(line.data)
            self.def_src.add_attribute(sattr)

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
            sattr = SrcAttribute()
            sattr.set_type(_("Publication date of source data"))
            sattr.set_value(text_date)
            self.def_src.add_attribute(sattr)

    def __header_file(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            filename = os.path.basename(line.data).split("\\")[-1]
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
        sub_state = CurrentState(level=state.level + 1)
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
            sattr = SrcAttribute()
            sattr.set_type(_("Submission record identifier"))
            sattr.set_value(line.token_text)
            self.def_src.add_attribute(sattr)

    def __header_lang(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            sattr = SrcAttribute()
            sattr.set_type(_("Language of GEDCOM text"))
            sattr.set_value(line.data)
            self.def_src.add_attribute(sattr)

    def __header_dest(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState

        FIXME: This processing does not depend on DEST, so there seems to be
        no reason for it to be placed here. Perhaps it is supposed to be after
        all the SOUR levels have been processed, but self.genby was only
        assigned by the initial SOUR tag, so this could have been done there.
        Perhaps, as suggested by the text of the error message, it was
        supposed to test whenther the_DEST_ was LEGACY, in which case the
        coding is now wrong.
        """
        if self.genby.upper() == "LEGACY":
            fname = os.path.basename(self.filename)
            self.user.warn(
                _(
                    "Import of GEDCOM file %(filename)s with DEST=%(by)s, "
                    "could cause errors in the resulting database!"
                )
                % {"filename": fname, "by": self.genby},
                _("Look for nameless events."),
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
            if self.__level_is_finished(line, state.level + 1):
                break
            elif line.token == TOKEN_VERS:
                version = line.data

        if self.use_def_src:
            if version == "":
                sattr = SrcAttribute()
                sattr.set_type(_("Character set"))
                sattr.set_value(encoding)
                self.def_src.add_attribute(sattr)
            else:
                sattr = SrcAttribute()
                sattr.set_type(_("Character set and version"))
                sattr.set_value("%s %s" % (encoding, version))
                self.def_src.add_attribute(sattr)

    def __header_gedc(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        while True:
            line = self.__get_next_line()
            if self.__level_is_finished(line, state.level + 1):
                break
            elif line.token == TOKEN_VERS:
                if (not line.data) or line.data[0] != "5":
                    self.__add_msg(_("GEDCOM version not supported"), line, state)
                if self.use_def_src:
                    sattr = SrcAttribute()
                    sattr.set_type(_("GEDCOM version"))
                    sattr.set_value(line.data)
                    self.def_src.add_attribute(sattr)
            elif line.token == TOKEN_FORM:
                if line.data == "LINEAGE-LINKED":
                    pass
                elif line.data.upper() == "LINEAGE-LINKED":
                    # Allow Lineage-Linked etc. though it should be in
                    # uppercase  (Note: Gramps is not a validator! prc)
                    self.__add_msg(_("GEDCOM FORM should be in uppercase"), line, state)
                else:
                    self.__add_msg(_("GEDCOM FORM not supported"), line, state)
                if self.use_def_src:
                    sattr = SrcAttribute()
                    sattr.set_type(_("GEDCOM form"))
                    sattr.set_value(line.data)
                    self.def_src.add_attribute(sattr)

    def __header_plac(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        sub_state = CurrentState(level=state.level + 1)
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

        This processes the <TRANSMISSION_DATE>, i.e. the date when this
        [GEDCOM] transmission was created (as opposed to the date when the
        source data that was used to create the transmission was published or
        created

        Because there is a DATE tag, line.data is automatically converted to a
        Date object before getting to this point, so it has to be converted
        back to a string
        """
        tx_date = str(line.data)
        tx_time = ""
        line = self.__get_next_line()
        if self.__level_is_finished(line, state.level):
            pass
        elif line.token == TOKEN_TIME:
            tx_time = str(line.data)

        if self.use_def_src:
            if tx_time == "":
                sattr = SrcAttribute()
                sattr.set_type(_("Creation date of GEDCOM"))
                sattr.set_value(tx_date)
                self.def_src.add_attribute(sattr)
            else:
                sattr = SrcAttribute()
                sattr.set_type(_("Creation date and time of GEDCOM"))
                sattr.set_value("%s %s" % (tx_date, tx_time))
                self.def_src.add_attribute(sattr)

    def __header_note(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.__parse_note(line, self.def_src, state)

    def __header_subm_name(self, line, state):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        if self.use_def_src:
            self.def_src.set_author(line.data)

    def __parse_note(self, line, obj, state):
        if line.token == TOKEN_RNOTE:
            # reference to a named note defined elsewhere
            # NOTE_STRUCTURE: =
            #  n  NOTE @<XREF:NOTE>@  {1:1}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}  # 5.5 only, not in 5.5.1
            handle = self.__find_note_handle(self.nid_map[line.data])
            obj.add_note(handle)
            self.note_type_map[handle] = OBJ_NOTETYPE.get(
                type(obj).__name__, NoteType.GENERAL
            )
        else:
            # Embedded note
            # NOTE_STRUCTURE: =
            #  n  NOTE [<SUBMITTER_TEXT> | <NULL>]  {1:1}
            #    +1 [ CONC | CONT ] <SUBMITTER_TEXT>  {0:M}
            #    +1 SOUR @<XREF:SOUR>@  {0:M}
            if not line.data:
                self.__add_msg(_("Empty note ignored"), line, state)
                self.__skip_subordinate_levels(line.level + 1, state)
            else:
                new_note = Note(line.data)
                new_note.set_gramps_id(self.nid_map[""])
                new_note.set_handle(create_id())

                sub_state = CurrentState(level=state.level + 1)
                sub_state.note = new_note
                self.__parse_level(sub_state, self.note_parse_tbl, self.__undefined)
                state.msg += sub_state.msg

                # Add a default tag if provided
                self.__add_default_tag(new_note)
                # Set the type of the note
                new_note.set_type(
                    OBJ_NOTETYPE.get(type(obj).__name__, NoteType.GENERAL)
                )
                self.dbase.commit_note(new_note, self.trans, new_note.change)
                obj.add_note(new_note.get_handle())

    # ----------------------------------------------------------------------
    #
    # NOTE parsing
    #
    # ----------------------------------------------------------------------

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
        if (
            not line.data
            and self.nid_map.clean(line.token_text) not in self.nid_map.map()
        ):
            self.__add_msg(_("Empty note ignored"), line)
            self.__skip_subordinate_levels(level, state)
        else:
            gid = self.nid_map[line.token_text]
            handle = self.__find_note_handle(gid)
            new_note = Note(line.data)
            new_note.set_handle(handle)
            new_note.set_gramps_id(gid)
            if handle in self.note_type_map:
                new_note.set_type(self.note_type_map[handle])
            sub_state = CurrentState(level=state.level)
            sub_state.note = new_note
            self.__parse_level(sub_state, self.note_parse_tbl, self.__undefined)
            state.msg += sub_state.msg

            self.dbase.commit_note(new_note, self.trans, new_note.change)
            self.__check_msgs(
                _("NOTE Gramps ID %s") % new_note.get_gramps_id(), state, None
            )

    def __note_chan(self, line, state):
        if state.note:
            self.__parse_change(line, state.note, state.level + 1, state)

    def __parse_source_reference(self, citation, level, handle, state):
        """
        Read the data associated with a SOUR reference.
        """
        sub_state = CurrentState(level=level + 1)
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
            raise GedcomError("%s is not a GEDCOM file" % self.filename)

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
            +1 NOTE <NOTE_STRUCTURE> {0:m}
        """
        if not self.use_def_src:
            # no place to put data, so call it not recognized
            self.__not_recognized(line, state)
            return
        while True:
            line = self.__get_next_line()
            msg = ""
            if self.__level_is_finished(line, state.level):
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
            elif line.token == TOKEN_NOTE or line.token == TOKEN_RNOTE:
                self.__parse_note(line, self.def_src, state)
                self.dbase.commit_source(self.def_src, self.trans)
            else:
                self.__not_recognized(line, state)
                continue

            if msg != "":
                sattr = SrcAttribute()
                sattr.set_type(msg)
                sattr.set_value(line.data)
                self.def_src.add_attribute(sattr)
                self.dbase.commit_source(self.def_src, self.trans)

    def handle_source(self, line, level, state):
        """
        Handle the specified source, building a source reference to
        the object.
        """
        citation = Citation()
        if line.data and line.data[0] != "@":
            title = line.data
            handle = self.inline_srcs.get(title, create_id())
            src = Source()
            src.handle = handle
            src.gramps_id = self.sid_map[""]
            self.inline_srcs[title] = handle
        else:
            src = self.__find_or_create_source(self.sid_map[line.data])
            # We need to set the title to the cross reference identifier of the
            # SOURce record, just in case we never find the source record. If
            # we didn't find the source record, then the source object would
            # have got deleted by Chack and repair because the record is empty.
            # If we find the source record, the title is overwritten in
            # __source_title.
            if not src.title:
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
        corresponding in Gramps.

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
                # Lexer converted already to Date object
                dobj = line.data
            elif line.token == TOKEN_NOTE or line.token == TOKEN_RNOTE:
                self.__ignore(line, state)
            else:
                self.__not_recognized(line, state)

        # Attempt to convert the values to a valid change time
        if dobj:
            dstr = "%s %s %s" % (dobj.get_day(), dobj.get_month(), dobj.get_year())
            try:
                if tstr:
                    try:
                        tstruct = time.strptime(
                            "%s %s" % (dstr, tstr), "%d %m %Y %H:%M:%S"
                        )
                    except ValueError:
                        # seconds is optional in GEDCOM
                        tstruct = time.strptime(
                            "%s %s" % (dstr, tstr), "%d %m %Y %H:%M"
                        )
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

    def __do_refn(self, line, state, obj):
        """
        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        @param obj: The object to attach the attribute
        @type obj: Gramps primary object
        """
        attr = Attribute()
        attr.set_type(line.token_text)  # Atrribute : REFN
        attr.set_value(line.data)
        # if there is a subsequent TYPE, we add it as a note to the attribute
        line = self.__chk_subordinate(state.level + 1, state, TOKEN_TYPE)
        if line:
            new_note = Note(line.data)
            new_note.set_gramps_id(self.nid_map[""])
            new_note.set_handle(create_id())
            new_note.set_type("REFN-TYPE")
            self.dbase.commit_note(new_note, self.trans, new_note.change)
            attr.add_note(new_note.get_handle())
        obj.attribute_list.append(attr)

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
        event = Event()
        event_ref = EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(event_type)

        if description and description != "Y":
            event.set_description(description)
        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.level = state.level + 1
        sub_state.event_ref = event_ref
        sub_state.event = event
        sub_state.person = state.person
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, event_map, self.__undefined)
        if (
            description == "Y"
            and event.date.is_empty()
            and event.type == EventType.BIRTH
            and not event.place
        ):
            event.set_description(_("No Date Information"))
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

        self.dbase.commit_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)
        return event_ref

    def __build_family_event_pair(self, state, event_type, event_map, description):
        event = Event()
        event_ref = EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(event_type)
        if description and description != "Y":
            event.set_description(description)

        self.dbase.add_event(event, self.trans)

        sub_state = CurrentState()
        sub_state.family = state.family
        sub_state.level = state.level + 1
        sub_state.event = event
        sub_state.event_ref = event_ref
        sub_state.pf = self.place_parser

        self.__parse_level(sub_state, event_map, self.__undefined)
        state.msg += sub_state.msg

        self.__add_place(event, sub_state)

        self.dbase.commit_event(event, self.trans)
        event_ref.set_reference_handle(event.handle)
        return event_ref

    def __do_photo(self, state):
        """
        Choose the primary photo from the list of media present for this
        person.  Supports FTM _PHOTO. and others _PRIM feature.
          0 INDI
          +1 _PHOTO @<XREF:OBJE>@ {1:1}

          0 INDI
            +1 OBJE @<XREF:OBJE>@
              +2 _PRIM <Y/N>

          0 INDI
            +1 OBJE
              +2 FILE primary_photo.jpg
              +2 _PRIM <Y/N>

        For the _PHOTO varient, state.photo contains the XREF ('@M1@').
        For the _PRIM varients, state.photo contains the handle.
        Since Gramps currently uses the first media in the list as the
        primary, find the primary photo if already in the list, if present,
        move to beginning.  If not present, add at the beginning.
        This is run after all of the person processing is complete but before
        committing the person.
        """
        if state.photo.startswith("@"):
            gramps_id = self.oid_map[state.photo]
            handle = self.__find_media_handle(gramps_id)
        elif state.photo:
            handle = state.photo
        else:
            return
        for mref in state.person.media_list:
            if handle == mref.ref:
                state.person.media_list.remove(mref)
                state.person.media_list.insert(0, mref)
                return
        mref = MediaRef()
        mref.set_reference_handle(handle)
        state.person.media_list.insert(0, mref)

    def __extract_temple(self, line):
        """Determine the LDS Temple from the input line"""

        def get_code(code):
            """get the Temple code"""
            if TEMPLES.is_valid_code(code):
                return code
            elif TEMPLES.is_valid_name(code):
                return TEMPLES.code(code)

        code = get_code(line.data)
        if code:
            return code

        # Not sure why we do this. Kind of ugly.
        code = get_code(line.data.split()[0])
        if code:
            return code

        # Okay we have no clue which temple this is.
        # We should tell the user and store it anyway.
        self.__add_msg(_("Invalid temple code"), line, None)
        return line.data

    def __add_default_source(self, obj):
        """
        Add the default source to the object.
        """
        if self.use_def_src and len(obj.get_citation_list()) == 0:
            citation = Citation()
            citation.set_reference_handle(self.def_src.handle)
            self.dbase.add_citation(citation, self.trans)
            obj.add_citation(citation.handle)

    def __add_default_tag(self, obj):
        """
        Add the default tag to the object.
        """
        if self.default_tag:
            obj.add_tag(self.default_tag.handle)

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
        # Researcher is a sub-type of LocationBase, so get_street and
        # set_street which are used in routines called from self.parse_loc_tbl
        # work fine.
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
        if state.res.get_phone():
            self.__add_msg(_("Only one phone number supported"), line, state)
        else:
            state.res.set_phone(line.data)

    def __subm_email(self, line, state):
        """
        n EMAIL <ADDRESS_EMAIL> {0:3}

        @param line: The current line in GedLine format
        @type line: GedLine
        @param state: The current state
        @type state: CurrentState
        """
        # only record the first multiple emails for researcher
        if not state.res.get_email():
            state.res.set_email(line.data)
        self.__repo_email(line, state)


# -------------------------------------------------------------------------
#
# GedcomStageOne
#
# -------------------------------------------------------------------------
class GedcomStageOne:
    """
    The GedcomStageOne parser scans the file quickly, looking for a few things.
     This includes:

    1. Character set encoding
    2. Number of people and families in the list
    3. Child to family references, since Ancestry.com creates GEDCOM files
       without the FAMC references.
    """

    __BAD_UTF16 = _(
        "Your GEDCOM file is corrupted. "
        "The file appears to be encoded using the UTF16 "
        "character set, but is missing the BOM marker."
    )
    __EMPTY_GED = _("Your GEDCOM file is empty.")

    @staticmethod
    def __is_xref_value(value):
        """
        Return True if value is in the form of a XREF value. We assume that
        if we have a leading '@' character, then we are okay.
        """
        return value and value[0] == "@"

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
        (byte order marker) in the GEDCOM file. If we detect a UTF-16 or
        UTF-8-BOM encoded file, we choose appropriate decoders.  If no BOM
        is detected, we return in UTF-8 mode it is the more modern option;
        and anyway it doesn't really matter as we are only looking for GEDCOM
        keywords which are only 7-bit ASCII anyway.
        In any case, we Always return the file in text mode with transparent
        newline (CR, LF, or CRLF).
        """
        line = input_file.read(2)
        if line == b"\xef\xbb":
            input_file.read(1)
            self.enc = "utf_8_sig"
            return TextIOWrapper(
                input_file, encoding="utf_8_sig", errors="replace", newline=None
            )
        elif line == b"\xff\xfe" or line == b"\xfe\xff":
            self.enc = "UTF16"
            input_file.seek(0)
            return TextIOWrapper(
                input_file, encoding="utf_16", errors="replace", newline=None
            )
        elif not line:
            raise GedcomError(self.__EMPTY_GED)
        elif line == b"\x30\x00" or line == b"\x00\x30":
            raise GedcomError(self.__BAD_UTF16)
        else:
            input_file.seek(0)
            return TextIOWrapper(
                input_file, encoding="utf-8", errors="replace", newline=None
            )

    def parse(self):
        """
        Parse the input file.
        """
        current_family_id = ""

        reader = self.__detect_file_decoder(self.ifile)

        for line in reader:
            # Scan for a few items, keep counts.  Also look for actual CHAR
            # Keyword to figure out actual encodeing for non-unicode file types
            line = line.strip()
            if not line:
                continue
            self.lcnt += 1

            try:
                data = line.split(None, 3) + [""]
                (level, key, value) = data[:3]
                level = int(level)
                key = key.strip()
                value = value.strip()
            except:
                continue

            if level == 0 and key[0] == "@":
                if value in ("FAM", "FAMILY"):
                    current_family_id = key.strip()[1:-1]
                elif value in ("INDI", "INDIVIDUAL"):
                    self.pcnt += 1
            elif key in ("HUSB", "HUSBAND", "WIFE") and self.__is_xref_value(value):
                self.fams[value[1:-1]].append(current_family_id)
            elif key in ("CHIL", "CHILD") and self.__is_xref_value(value):
                self.famc[value[1:-1]].append(current_family_id)
            elif key == "CHAR" and not self.enc:
                assert isinstance(value, str)
                self.enc = value
        LOG.debug("parse pcnt %d", self.pcnt)
        LOG.debug("parse famc %s", dict(self.famc))
        LOG.debug("parse fams %s", dict(self.fams))
        self.ifile = reader  # need this to keep python from autoclosing file

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
        assert isinstance(enc, str)
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


# -------------------------------------------------------------------------
#
# make_gedcom_date
#
# -------------------------------------------------------------------------
def make_gedcom_date(subdate, calendar, mode, quality):
    """
    Convert a Gramps date structure into a GEDCOM compatible date.
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
        print("Month index error - %d" % mon)
        retval = "%d%s" % (year, bce)
    if calendar == Date.CAL_SWEDISH:
        # If Swedish calendar use ISO for for date and append (swedish)
        # to indicate calandar
        if year and not mon and not day:
            retval = "%i" % (year)
        else:
            retval = "%i-%02i-%02i" % (year, mon, day)
        retval = retval + " (swedish)"
        # Skip prefix @#DUNKNOWN@ as it seems
        # not used in all other genealogy applications.
        # Gramps can handle it on import, but not with (swedish) appended
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
            retval = "%d%s" % (year, bce)
        elif year == 0:
            retval = "(%s)" % mmap[mon]
        else:
            retval = "%s %d%s" % (mmap[mon], year, bce)
    elif mon == 0:
        retval = "%d%s" % (year, bce)
    elif year == 0:
        retval = "(%d %s)" % (day, mmap[mon])
    else:
        retval = "%d %s %d%s" % (day, mmap[mon], year, bce)
    return retval
