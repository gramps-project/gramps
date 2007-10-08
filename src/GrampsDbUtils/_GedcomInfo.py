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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import gen.lib

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

#-------------------------------------------------------------------------
#
# Integer to GEDCOM tag mappings for constants
#
#-------------------------------------------------------------------------
familyConstantEvents = {
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

personalConstantEvents = {
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

familyConstantAttributes = {
    gen.lib.AttributeType.NUM_CHILD   : "NCHI",
    }

personalConstantAttributes = {
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
lds_status = {
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

#-------------------------------------------------------------------------
#
# XML parser
#
#-------------------------------------------------------------------------
from xml.parsers.expat import ParserCreate

class GedcomDescription:
    def __init__(self,name):
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
        
    def set_dest(self,val):
        self.dest = val

    def get_dest(self):
        return self.dest

    def set_endl(self,val):
        self.endl = val.replace('\\r','\r').replace('\\n','\n')

    def get_endl(self):
        return self.endl

    def set_adopt(self,val):
        self.adopt = val

    def get_adopt(self):
        return self.adopt

    def set_prefix(self,val):
        self.prefix=val

    def get_prefix(self):
        return self.prefix
    
    def set_conc(self,val):
        self.conc = val

    def get_conc(self):
        return self.conc

    def set_alt_name(self,val):
        self.altname = val

    def get_alt_name(self):
        return self.altname

    def set_alt_calendar(self,val):
        self.cal = val

    def get_alt_calendar(self):
        return self.cal

    def set_obje(self,val):
        self.obje = val

    def get_obje(self):
        return self.obje

    def set_resi(self,val):
        self.resi = val

    def get_resi(self):
        return self.resi

    def set_source_refs(self,val):
        self.source_refs = val

    def get_source_refs(self):
        return self.source_refs

    def add_tag_value(self,tag,value):
        self.gramps2tag_map[value] = tag
        self.tag2gramps_map[tag] = value

    def gramps2tag(self,key):
        if self.gramps2tag_map.has_key(key):
            return self.gramps2tag_map[key]
        return ""

    def tag2gramps(self,key):
        if self.tag2gramps_map.has_key(key):
            return self.tag2gramps_map[key]
        return key

class GedcomInfoDB:
    def __init__(self):
        self.map = {}

        self.standard = GedcomDescription("GEDCOM 5.5 standard")
        self.standard.set_dest("GEDCOM 5.5")

        try:
            filepath = os.path.join(const.DATA_DIR,"gedcom.xml")
            f = open(filepath.encode('iso8859-1'),"r")
        except:
            return

        parser = GedInfoParser(self)
        parser.parse(f)
        f.close()

    def add_description(self,name,obj):
        self.map[name] = obj

    def get_description(self,name):
        if self.map.has_key(name):
            return self.map[name]
        return self.standard

    def get_from_source_tag(self,name):
        for k in self.map.keys():
            val = self.map[k]
            if val.get_dest() == name:
                return val
        return self.standard

    def get_name_list(self):
        mylist = self.map.keys()
        mylist.sort()
        return ["GEDCOM 5.5 standard"] + mylist
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class GedInfoParser:
    def __init__(self,parent):
        self.parent = parent
        self.current = None

    def parse(self,file):
        p = ParserCreate()
        p.StartElementHandler = self.startElement
        p.ParseFile(file)
        
    def startElement(self,tag,attrs):
        if tag == "target":
            name = attrs['name']
            self.current = GedcomDescription(name)
            self.parent.add_description(name,self.current)
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
            self.current.add_tag_value(attrs['tag'],attrs['value'])
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
