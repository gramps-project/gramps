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

"Import from GEDCOM"

from RelLib import *
import latin_ansel
import latin_utf8 
import intl
_ = intl.gettext

import os
import re
import string
import const
import utils
import shutil

from gtk import *
from gnome.ui import *
from libglade import *

ANSEL = 1
UNICODE = 2

topDialog = None
db = None
callback = None
glade_file = None
clear_data = 0
in_obje = 0

InvalidGedcom = "Invalid GEDCOM file"

ged2rel = {}
for val in const.personalConstantEvents.keys():
    key = const.personalConstantEvents[val]
    if key != "":
        ged2rel[key] = val

ged2fam = {}
for val in const.familyConstantEvents.keys():
    key = const.familyConstantEvents[val]
    if key != "":
        ged2fam[key] = val

def find_file(fullname,altpath):
    if os.path.isfile(fullname):
        return fullname
    other = altpath + os.sep + os.path.basename(fullname)
    if os.path.isfile(other):
        return other
    else:
        return ""

lineRE = re.compile(r"\s*(\d+)\s+(\S+)\s*(.*)$")
nameRegexp = re.compile(r"([\S\s]*\S)?\s*/([^/]+)?/\s*,?\s*([\S]+)?")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def importData(database, filename):
    global callback
    global topDialog
    global glade_file
    global statusWindow
    

    # add some checking here

    if clear_data == 1:
        database.new()

    g = GedcomParser(database,filename)
    g.parse_gedcom_file()

#    statusTop = GladeXML(glade_file,"status")
#    statusWindow = statusTop.get_widget("status")
#    progressWindow = statusTop.get_widget("progress")

    utils.modified()
    callback(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class AddrStruct:
    def __init__(self):
        self.label = ""
        self.addr1 = ""
        self.addr2 = ""
        self.city = ""
        self.state = ""
        self.postal = ""
        self.country = ""
	self.phone = ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateStruct:
    def __init__(self):
        self.date = ""
        self.time = ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GedcomParser:

    SyntaxError = "Syntax Error"

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def __init__(self,db, file):
        self.db = db
        self.person = None
        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.nmap = {}
        f = open(file,"r")
        self.lines = f.readlines()
        f.close()
	self.index = 0
        self.code = 0

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def get_next(self):
        line = string.replace(self.lines[self.index],'\r','')
        if self.code == ANSEL:
            line = latin_ansel.ansel_to_latin(line)
        elif self.code == UNICODE:
            line = latin_utf8.utf8_to_latin(line)
	match = lineRE.match(line)
        if not match:
	    raise GedcomParser.SyntaxError, self.lines[self.index]
        self.index = self.index + 1
    	return match.groups()

    def barf(self,level):
        print "IGNORED (%d): %s" % (self.index, self.lines[self.index-1])
        self.ignore_sub_junk(level)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def backup(self):
        self.index = self.index - 1

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_gedcom_file(self):
        self.index = 0
	self.parse_header()
        self.parse_submitter()
	self.parse_record()
        self.parse_trailer()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_trailer(self):
	matches = self.get_next()

        if matches[1] != "TRLR":
	    self.barf(0)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header(self):
	self.parse_header_head()
        self.parse_header_source()
        self.parse_header_dest()
        self.parse_header_date()
        self.parse_header_subm()
        self.parse_header_subn()
        self.parse_header_file()
        self.parse_header_copr()
        self.parse_header_gedc() 
        self.parse_header_char()
        self.parse_header_lang()
        self.parse_header_plac()
        self.parse_header_note()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_submitter(self):
	matches = self.get_next()

        if matches[2] != "SUBN":
            self.backup()
	    return
        else:
            self.ignore_sub_junk(1)

    def parse_source(self,name,level):
        self.source = self.db.findSource(name,self.smap)
        
        while 1:
            matches = self.get_next()
	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "DATA" or matches[1] == "TEXT":
                self.ignore_sub_junk(2)
            elif matches[1] == "TITL":
                self.source.setTitle(matches[2] + self.parse_continue_data(2))
            elif matches[1] == "AUTH":
                self.source.setAuthor(matches[2] + self.parse_continue_data(2))
            elif matches[1] == "PUBL":
                self.source.setPubInfo(matches[2] + self.parse_continue_data(2))
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    self.source.setNote(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        self.source.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        self.source.setNoteObj(noteobj)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_record(self):
        while 1:
	    matches = self.get_next()

            if matches[2] == "FAM":
                self.family = self.db.findFamily(matches[1],self.fmap)
                self.parse_family()
            elif matches[2] == "INDI":
                self.person = self.db.findPerson(matches[1],self.pmap)
                self.parse_individual()
            elif matches[2] == "SUBM":
                self.ignore_sub_junk(1)
            elif matches[1] == "SUBM":
                self.ignore_sub_junk(1)
            elif matches[2] == "SOUR":
                self.parse_source(matches[1],1)
            elif matches[2] == "REPO":
                print "REPO",matches[1]
                self.ignore_sub_junk(1)
            elif matches[2] == "NOTE":
                if self.nmap.has_key(matches[1]):
                    noteobj = self.nmap[matches[1]]
                else:
                    noteobj = Note()
                    self.nmap[matches[1]] = noteobj
                noteobj.set(self.parse_continue_data(1))
                self.parse_note_data(1)
            elif matches[2] == "OBJE":
                print "OBJE",matches[1]
                self.ignore_sub_junk(1)
	    elif matches[1] == "TRLR":
                self.backup()
                return
            else:
	        self.barf(1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_note_data(self,level):
        while 1:
            matches = self.get_next()
	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "SOUR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "CHAN":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "REFN":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "RIN":
                pass
            else:
                self.barf(level+1)
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_source_citation(self,level):
        while 1:
            matches = self.get_next()
	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "PAGE":
                pass
            elif matches[1] == "EVEN":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "DATA":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "QUAY":
                pass
            elif matches[1] == "NOTE":
                note = matches[1] + self.parse_continue_data(level+1)
                self.ignore_change_data(level+1)
                pass
            else:
                self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_family(self):
        while 1:
	    matches = self.get_next()

	    if int(matches[0]) == 0:
                self.backup()
                return
	    elif matches[1] == "HUSB":
                self.family.setFather(self.db.findPerson(matches[2],self.pmap))
                self.ignore_sub_junk(2)
	    elif matches[1] == "WIFE":
                self.family.setMother(self.db.findPerson(matches[2],self.pmap))
                self.ignore_sub_junk(2)
	    elif matches[1] == "CHIL":
                self.family.addChild(self.db.findPerson(matches[2],self.pmap))
	    elif matches[1] == "NCHI" or matches[1] == "RIN" or matches[1] == "SUBM":  
                pass
            elif matches[1] == "REFN" or matches[1] == "CHAN":
                self.ignore_sub_junk(2)
            elif matches[1] == "MARR":
                event = Event()
                event.setName("Marriage")
                self.family.setMarriage(event)
                self.parse_family_event(event,2)
            elif matches[1] == "DIV":
                event = Event()
                event.setName("Divorce")
                self.family.setDivorce(event)
                self.parse_family_event(event,2)
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    self.family.setNote(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        self.family.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        self.family.setNoteObj(noteobj)
            else:
                event = Event()
                try:
                    event.setName(ged2fam[matches[2]])
                except:
                    event.setName(matches[2])
                self.family.addEvent(event)
	        self.parse_family_event(event,2)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_individual(self):
        while 1:
	    matches = self.get_next()

	    if int(matches[0]) == 0:
                self.backup()
                return
	    elif matches[1] == "NAME":
                name = Name()
                names = nameRegexp.match(matches[2]).groups()
                if names[0]:
                    name.setFirstName(names[0])
                if names[1]:
                    name.setSurname(names[1])
                if names[2]:
                    name.setSuffix(names[2])
                self.person.setPrimaryName(name)
                self.parse_name(name,2)
	    elif matches[1] == "RIN":
                pass
	    elif matches[1] == "RFN":
                pass
	    elif matches[1] == "AFN":
                pass
	    elif matches[1] == "CHAN":
                self.ignore_sub_junk(1)
	    elif matches[1] == "ALIA":
                pass
	    elif matches[1] == "ANCI" or matches[1] == "DESI":
                pass
	    elif matches[1] == "REFN":
                self.ignore_sub_junk(1)
	    elif matches[1] == "SOUR":
                self.ignore_sub_junk(1)
	    elif matches[1] == "OBJE":
                if matches[2] and matches[2][0] == '@':
                    self.ignore_sub_junk(2)
                else:
                    self.parse_person_object(2)
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    self.person.setNote(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        self.person.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        self.person.setNoteObj(noteobj)
	    elif matches[1] == "SEX":
                if matches[2][0] == "M":
                    self.person.setGender(Person.male)
                else:
                    self.person.setGender(Person.female)
	    elif matches[1] == "EVEN":
                pass
	    elif matches[1] == "FAMS":
                self.person.addFamily(self.db.findFamily(matches[2],self.fmap))
                note = self.parse_optional_note(2)
	    elif matches[1] == "FAMC":
                type,note = self.parse_famc_type(2)
                family = self.db.findFamily(matches[2],self.fmap)
                if type == "" or type == "Birth":
                    self.person.setMainFamily(family)
                else:
                    self.person.addAltFamily(family,type)
	    elif matches[1] == "RESI":
                addr = Address()
                self.person.addAddress(addr)
                self.parse_residence(addr,2)
	    elif matches[1] == "BIRT":
                event = Event()
                if self.person.getBirth().getDate() != "" or \
                   self.person.getBirth().getPlace() != "":
                    event.setName("Alternate Birth")
                    self.person.addEvent(event)
                else:
                    event.setName("Birth")
                    self.person.setBirth(event)
                self.parse_person_event(event,2)
	    elif matches[1] == "ADOP":
                event = Event()
                event.setName("Adopted")
                self.person.addEvent(event)
                self.parse_person_event(event,2)
	    elif matches[1] == "DEAT":
                event = Event()
                if self.person.getDeath().getDate() != "" or \
                   self.person.getDeath().getPlace() != "":
                    event.setName("Alternate Death")
                    self.person.addEvent(event)
                else:
                    event.setName("Death")
                    self.person.setDeath(event)
                self.parse_person_event(event,2)
	    elif matches[1] == "EVEN":
                event = Event()
                self.person.addEvent(event)
	        self.parse_person_event(event,2)
            else:
                event = Event()
                try:
                    event.setName(ged2rel[matches[1]])
                except:
                    event.setName(matches[1])
                self.person.addEvent(event)
	        self.parse_person_event(event,2)

    def parse_optional_note(self,level):
        note = ""
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return note
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[2] + self.parse_continue_data(level+1)
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
	        self.barf(level+1)

    def parse_famc_type(self,level):
        type = ""
        note = ""
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return (string.capitalize(type),note)
            elif matches[1] == "PEDI":
                type = matches[2]
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[2] + self.parse_continue_data(level+1)
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
	        self.barf(level+1)

    def parse_person_object(self,level):
        form = ""
        file = ""
        title = ""
        note = ""
        while 1:
            matches = self.get_next()
            if matches[1] == "FORM":
                form = matches[2]
            elif matches[1] == "TITL":
                title = matches[2]
            elif matches[1] == "FILE":
                file = matches[2]
            elif matches[1] == "NOTE":
                note = matches[2] + self.parse_continue_data(level+1)
	    elif int(matches[0]) < level:
                self.backup()
                break
            else:
	        self.barf(level+1)

        if form == "URL":
            url = Url(file,title)
            self.person.addUrl(url)
        else:
            print "*",form,title

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_residence(self,address,level):
        while 1:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == "DATE":
                address.setDate(matches[2])
            elif matches[1] == "AGE" or matches[1] == "AGNC":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "CAUS" or matches[1] == "ADDR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "STAT" or matches[1] == "TEMP":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "OBJE" or matches[1] == "TYPE":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "SOUR":
                source_ref = SourceRef()
                source_ref.setBase(self.db.findSource(matches[2],self.smap))
                address.setSourceRef(source_ref)
                self.parse_source_reference(source_ref,level+1)
            elif matches[1] == "PLAC":
                address.setStreet(matches[2])
                self.parse_address(address,level+1)
            elif matches[1] == "PHON":
                pass
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    self.address.setNote(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        self.address.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        self.address.setNoteObj(noteobj)
            else:
	        self.barf(level+1)

    def parse_address(self,address,level):
        first = 0
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "ADDR" or matches[1] == "ADR1" or matches[1] == "ADR2":
                val = address.getStreet()
                if first == 0:
                    val = "%s %s" % (matches[2], self.parse_continue_data(level+1))
                    first = 1
                else:
                    val = "%s,%s %s" % (val,matches[2],self.parse_continue_data(level+1))
                address.setStreet(val)
            elif matches[1] == "CITY":
                address.setCity(matches[2])
            elif matches[1] == "STAE":
                address.setState(matches[2])
            elif matches[1] == "POST":
                address.setPostal(matches[2])
            elif matches[1] == "CTRY":
                address.setCountry(matches[2])
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_person_event(self,event,level):
        while 1:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == "TYPE":
                if event.getName() != "":
                    try:
                        event.setName(ged2rel[matches[2]])
                    except:
                        event.setName(matches[2])
            elif matches[1] == "DATE":
                event.setDate(matches[2])
            elif matches[1] == "AGE" or matches[1] == "AGNC":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "CAUS" or matches[1] == "ADDR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "STAT" or matches[1] == "TEMP":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "OBJE":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "SOUR":
                source_ref = SourceRef()
                source_ref.setBase(self.db.findSource(matches[2],self.smap))
                event.setSourceRef(source_ref)
                self.parse_source_reference(source,level+1)
            elif matches[1] == "FAMC":
                family = self.db.findFamily(matches[2],self.fmap)
                if event.getName() == "Birth":
                    self.person.setMainFamily(family)
                else:
                    self.person.addAltFamily(family,event.getName())
                self.ignore_sub_junk(level+1)
            elif matches[1] == "PLAC":
                event.setPlace(matches[2])
                self.ignore_sub_junk(level+1)
            elif matches[1] == "NOTE":
                note = matches[2] + self.parse_continue_data(level+1)
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_family_event(self,event,level):
        while 1:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == "TYPE":
                if event.getName() != "":
                    try:
                        event.setName(ged2fam[matches[2]])
                    except:
                        event.setName(matches[2])
            elif matches[1] == "DATE":
                event.setDate(matches[2])
            elif matches[1] == "AGE" or matches[1] == "AGNC":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "CAUS" or matches[1] == "ADDR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "STAT" or matches[1] == "TEMP":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "OBJE":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "SOUR":
                source_ref = SourceRef()
                source_ref.setBase(self.db.findSource(matches[2],self.smap))
                event.setSourceRef(source_ref)
                self.parse_source_reference(source_ref,level+1)
            elif matches[1] == "PLAC":
                event.setPlace(matches[2])
                self.ignore_sub_junk(level+1)
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    event.setNote(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        event.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        event.setNoteObj(noteobj)
            else:
	        self.barf(level+1)

    def parse_source_reference(self,source,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "PAGE":
                source.setPage(matches[2])
            elif matches[1] == "DATA":
                date,text = self.parse_source_data(level+1)
                d = Date()
                d.set(date)
                source.setDate(d)
                source.setText(text)
            elif matches[1] == "QUAY":
                pass
            elif matches[1] == "NOTE":
                if matches[2] and matches[2][0] != "@":
                    note = matches[1] + self.parse_continue_data(1)
                    source.setComments(note)
                    self.ignore_sub_junk(2)
                else:
                    if self.nmap.has_key(matches[2]):
                        source.setNoteObj(self.nmap[matches[2]])
                    else:
                        noteobj = Note()
                        self.nmap[matches[2]] = noteobj
                        source.setNoteObj(noteobj)
            else:
	        self.barf(level+1)
        
    def parse_source_data(self,level):
        date = ""
        note = ""
        while 1:
	    matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return (date,note)
            elif matches[1] == "DATE":
                date = matches[2]

            elif matches[1] == "TEXT":
                note = matches[2] + self.parse_continue_data(level+1)
            else:
	        self.barf(level+1)
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_name(self,name,level):
        while 1:
	    matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
	    elif matches[1] == "NPFX":
                name.setTitle(matches[1])
	    elif matches[1] == "GIVN":
                name.setFirstName(matches[1])
	    elif matches[1] == "SPFX":
                pass
	    elif matches[1] == "SURN":
                name.setSurname(matches[1])
	    elif matches[1] == "NSFX":
                name.setSuffix(matches[1])
	    elif matches[1] == "NICK":
                self.person.setNickName(matches[1])
            elif matches[1] == "SOUR":
                self.ignore_sub_junk(level+1)
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_head(self):
	matches = self.get_next()

        if matches[1] != "HEAD":
	    self.barf(0)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_source(self):
        while 1:
	    matches = self.get_next()

            print matches[0],matches[1],matches[2]
	    if int(matches[0]) == 0:
                self.backup()
                return
	    elif matches[1] == "SOUR":
                print "Source is",matches[2]
   	    elif matches[1] == "NAME":
                print "Name is",matches[2]
   	    elif matches[1] == "VERS":
                print "Version is",matches[2]
   	    elif matches[1] == "CORP":
                self.ignore_sub_junk(2)
   	    elif matches[1] == "DATA":
                print "Data is",matches[2]
                self.parse_sub_data(3)
   	    elif matches[1] == "SUBM":
                pass
   	    elif matches[1] == "SUBN":
                pass
   	    elif matches[1] == "DEST":
                pass
   	    elif matches[1] == "FILE":
                self.ignore_sub_junk(1)
   	    elif matches[1] == "COPR":
                pass
   	    elif matches[1] == "CHAR":
                if matches[2] == "UNICODE" or matches[2] == "UTF-8" or \
                   matches[2] == "UTF8":
                    self.code = UNICODE
                elif matches[2] == "ANSEL":
                    self.code = ANSEL
                self.parse_sub_char(2)
   	    elif matches[1] == "GEDC":
                self.parse_gedc(2)
   	    elif matches[1] == "LANG":
                print "Language is",matches[2]
   	    elif matches[1] == "PLAC":
                self.parse_place_form(2)
   	    elif matches[1] == "DATE":
                date = self.parse_date(2)
                date.date = matches[2]
   	    elif matches[1] == "NOTE":
                note = matches[2] + self.parse_continue_data(2)
                print note
            elif matches[1][0] == "_":
                self.ignore_sub_junk(2)
            else:
	        self.barf(2)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def ignore_sub_junk(self,level):

        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def ignore_change_data(self,level):

	matches = self.get_next()
        if matches[1] == "CHAN":
	    while 1:
                matches = self.get_next()

	        if int(matches[0]) < level+1:
                    self.backup()
                    return
        else:
            self.backup()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_sub_char(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "VERS":
               print "CHAR version is",matches[2]
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_place_form(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "FORM":
               print "FORM",matches[2]
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_continue_data(self,level):
	data = ""
        while 1:
            matches = self.get_next()

            if matches[1] == "CONC":
               data = "%s%s" % (data,matches[2])
            elif matches[1] == "CONT":
               data = "%s\n%s" % (data,matches[2])
            else:
                self.backup()
                return data

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_gedc(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "VERS":
               print "Gedcom version is",matches[2]
            elif matches[1] == "FORM":
               print "Gedcom form is",matches[2]
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_date(self,level):
        date = DateStruct()
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return date
            elif matches[1] == "TIME":
                date.time = matches[2]
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_addr_struct(self,level):
        addr = AddrStruct()

        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "ADDR":
                addr.label = matches[2]
                self.parse_sub_addr(level+1, addr)
            elif matches[1] == "PHON":
                addr.phone = matches[2]
            else:
                self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_sub_addr(self,level,addr):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "CONT":
                addr.label = "%s\n%s" %(addr.label,matches[2])
            elif matches[1] == "ADR1":
                addr.addr1 = matches[2]
            elif matches[1] == "ADR2":
                addr.addr2 = matches[2]
            elif matches[1] == "CITY":
                addr.city = matches[2]
            elif matches[1] == "STAE":
                addr.state = matches[2]
            elif matches[1] == "POST":
                addr.postal = matches[2]
            elif matches[1] == "CTRY":
                addr.country = matches[2]
            else:
                self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_sub_data(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "DATE":
                pass
            elif matches[1] == "COPR":
                pass
            else:
                self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_dest(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_date(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_subm(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_subn(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_file(self):
        pass
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_copr(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_gedc(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_char(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_lang(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_plac(self):
        pass

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_header_note(self):
        pass

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global topDialog
    global clear_data

    name = topDialog.get_widget("filename").get_text()
    if name == "":
        return

    if topDialog.get_widget("new").get_active():
        clear_data = 1
    else:
        clear_data = 0

    utils.destroy_passed_object(obj)
    importData(db,name)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def readData(database,active_person,cb):
    global db
    global topDialog
    global callback
    global glade_file
    
    db = database
    callback = cb
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "gedcomimport.glade"
        
    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked
        }

    topDialog = GladeXML(glade_file,"gedcomImport")
    topDialog.signal_autoconnect(dic)
    topDialog.get_widget("gedcomImport").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_name():
    return _("Import from GEDCOM")

if __name__ == "__main__":

    import sys

    db = RelDataBase()
    if len(sys.argv) == 1:
        g = GedcomParser(db,"test.ged")
    else:
        g = GedcomParser(db,sys.argv[1])
    g.parse_gedcom_file()
