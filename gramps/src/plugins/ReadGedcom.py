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
import gnome.mime

ANSEL = 1
UNICODE = 2

topDialog = None
db = None
callback = None
glade_file = None
clear_data = 0

photo_types = [ "jpeg", "bmp", "pict", "pntg", "tpic", "png", "gif",
                "tiff", "pcx" ]

_ADDRX = [ "ADDR", "ADR1", "ADR2" ]


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

lineRE = re.compile(r"\s*(\d+)\s+(\S+)\s*(.*)$")
nameRegexp = re.compile(r"([\S\s]*\S)?\s*/([^/]+)?/\s*,?\s*([\S]+)?")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def find_file(fullname,altpath):
    if os.path.isfile(fullname):
        type = gnome.mime.type(fullname)
        if type[0:6] != "image/":
            return ""
        else:
            return fullname
    other = altpath + os.sep + os.path.basename(fullname)
    if os.path.isfile(other):
        type = gnome.mime.type(other)
        if type[0:6] != "image/":
            return ""
        else:
            return other
    else:
        return ""

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

    statusTop = GladeXML(glade_file,"status")
    statusWindow = statusTop.get_widget("status")
    statusTop.get_widget("close").set_sensitive(0)
    statusTop.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object
        })

    g = GedcomParser(database,filename,statusTop)
    g.parse_gedcom_file()

    statusTop.get_widget("close").set_sensitive(1)

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
    def __init__(self, db, file, window):
        self.db = db
        self.person = None
        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.nmap = {}
        self.dir_path = os.path.dirname(file)
        f = open(file,"r")
        self.lines = f.readlines()
        f.close()

        self.file_obj = window.get_widget("file")
        self.encoding_obj = window.get_widget("encoding")
        self.created_obj = window.get_widget("created")
        self.version_obj = window.get_widget("version")
        self.families_obj = window.get_widget("families")
        self.people_obj = window.get_widget("people")
        self.errors_obj = window.get_widget("errors")
        self.error_text_obj = window.get_widget("error_text")
        self.error_count = 0
        self.error_text_obj.set_point(0)
        self.error_text_obj.set_word_wrap(0)
        
        self.update(self.file_obj,file)
        
	self.index = 0
        self.code = 0

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def update(self,field,text):
        field.set_text(text)
        while events_pending():
            mainiteration()

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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def barf(self,level):
        msg = _("Warning: line %d was not understood, so it was ignored.") % self.index
        self.error_text_obj.insert_defaults(msg)
        msg = "\n\t%s\n" % self.lines[self.index-1]
        self.error_text_obj.insert_defaults(msg)
        self.error_count = self.error_count + 1
        self.update(self.errors_obj,str(self.error_count))
        self.ignore_sub_junk(level)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def warn(self,msg):
        self.error_text_obj.insert_defaults(msg)
        self.error_count = self.error_count + 1
        self.update(self.errors_obj,str(self.error_count))

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
        self.fam_count = 0
        self.indi_count = 0
	self.parse_header()
        self.parse_submitter()
	self.parse_record()
        self.parse_trailer()
        self.update(self.families_obj,str(self.fam_count))
        self.update(self.people_obj,str(self.indi_count))

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
        index = 0
        while 1:
	    matches = self.get_next()

            if matches[2] == "FAM":
                if self.fam_count % 10 == 0:
                    self.update(self.families_obj,str(self.fam_count))
                self.fam_count = self.fam_count + 1
                self.family = self.db.findFamily(matches[1],self.fmap)
                self.parse_family()
            elif matches[2] == "INDI":
                if self.indi_count % 10 == 0:
                    self.update(self.people_obj,str(self.indi_count))
                self.indi_count = self.indi_count + 1
                self.person = self.db.findPerson(matches[1],self.pmap)
                self.parse_individual()
            elif matches[2] == "SUBM":
                self.ignore_sub_junk(1)
            elif matches[1] == "SUBM":
                self.ignore_sub_junk(1)
            elif matches[2] == "SOUR":
                self.parse_source(matches[1],1)
            elif matches[2] == "REPO":
                self.ignore_sub_junk(1)
            elif matches[2][0:4] == "NOTE":
                if self.nmap.has_key(matches[1]):
                    noteobj = self.nmap[matches[1]]
                else:
                    noteobj = Note()
                    self.nmap[matches[1]] = noteobj
                text =  matches[2][4:]
                if text == "":
                    noteobj.set(self.parse_continue_data(1))
                else:
                    noteobj.set(text + self.parse_continue_data(1))
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
    def parse_ftw_relations(self,level):
        retval = ""
        
        while 1:
            matches = self.get_next()
	    if int(matches[0]) < level:
                self.backup()
                return retval
            elif matches[1] == "_FREL":
                if string.lower(matches[2]) != "natural":
                    retval = matches[2]
            elif matches[1] == "_MREL":
                if string.lower(matches[2]) != "natural":
                    retval = matches[2]
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
                type = self.parse_ftw_relations(2)
                child = self.db.findPerson(matches[2],self.pmap)
                self.family.addChild(child)
                if type != "":
                    if child.getMainFamily() == self.family:
                        child.setMainFamily(None)
                    child.addAltFamily(self.family,type)
	    elif matches[1] == "NCHI" or matches[1] == "RIN" or matches[1] == "SUBM":  
                pass
            elif matches[1] == "REFN" or matches[1] == "CHAN":
                self.ignore_sub_junk(2)
            elif matches[1] == "SOUR":
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
	    elif matches[1] == "OBJE":
                if matches[2] and matches[2][0] == '@':
                    self.barf(2)
#                    self.ignore_sub_junk(2)
                else:
                    self.parse_family_object(2)
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
                    event.setName(ged2fam[matches[1]])
                except:
                    event.setName(matches[1])
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
	    elif matches[1] == "RIN" or matches[1] == "RFN":
                pass
	    elif matches[1] == "AFN" or matches[1] == "CHAN":
                self.ignore_sub_junk(2)
	    elif matches[1] == "ALIA":
                pass
	    elif matches[1] == "ANCI" or matches[1] == "DESI":
                pass
	    elif matches[1] == "REFN":
                self.ignore_sub_junk(2)
	    elif matches[1] == "SOUR":
                self.ignore_sub_junk(2)
	    elif matches[1] == "OBJE":
                if matches[2] and matches[2][0] == '@':
                    self.barf(2)
                else:
                    self.parse_person_object(2)
            elif matches[1] == "NOTE":
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
                    note = matches[2] + self.parse_continue_data(1)
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
	    elif matches[1] == "FAMS":
                family = self.db.findFamily(matches[2],self.fmap)
                self.person.addFamily(family)
                note = self.parse_optional_note(2)
	    elif matches[1] == "FAMC":
                type,note = self.parse_famc_type(2)
                family = self.db.findFamily(matches[2],self.fmap)
                if type == "" or type == "Birth":
                    if self.person.getMainFamily() == None:
                        self.person.setMainFamily(family)
                    else:
                        self.person.addAltFamily(family,"unknown")
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_optional_note(self,level):
        note = ""
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return note
            elif matches[1] == "NOTE":
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
                    note = matches[2] + self.parse_continue_data(level+1)
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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
            elif matches[1] == "_PRIMARY":
                type = matches[1]
            elif matches[1] == "NOTE":
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
                    note = matches[2] + self.parse_continue_data(level+1)
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
	        self.barf(level+1)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_person_object(self,level):
        form = ""
        file = ""
        title = ""
        note = ""
        while 1:
            matches = self.get_next()
            if matches[1] == "FORM":
                form = string.lower(matches[2])
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

        if form == "url":
            url = Url(file,title)
            self.person.addUrl(url)
        elif form in photo_types:
            path = find_file(file,self.dir_path)
            if path == "":
                self.warn(_("Could not import %s: either the file could not be found, or it was not a valid image") % file + "\n")
            else:
                photo = Photo()
                photo.setPath(path)
                photo.setDescription(title)
                self.person.addPhoto(photo)
        else:
            self.warn(_("Could not import %s: currently an unknown file type") % \
                      file + "\n")

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_family_object(self,level):
        form = ""
        file = ""
        title = ""
        note = ""
        while 1:
            matches = self.get_next()
            if matches[1] == "FORM":
                form = string.lower(matches[2])
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

        if form == "url":
            pass
#            url = Url(file,title)
#            self.family.addUrl(url)
        elif form in photo_types:
            path = find_file(file,self.dir_path)
            if path == "":
                self.warn("Could not import %s: the file could not be found\n" % \
                          file)
            else:
                photo = Photo()
                photo.setPath(path)
                photo.setDescription(title)
                self.family.addPhoto(photo)
        else:
            self.warn("Could not import %s: current an unknown file type\n" % \
                      file)

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
            elif matches[1] == "AGE" or matches[1] in "AGNC":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "CAUS" or matches[1] in "ADDR":
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
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_address(self,address,level):
        first = 0
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] in _ADDRX:
                val = address.getStreet()
                data = self.parse_continue_data(level+1)
                if first == 0:
                    val = "%s %s" % (matches[2],data)
                    first = 1
                else:
                    val = "%s,%s %s" % (val,matches[2],data)
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
                if event.getName() == "":
                    if ged2rel.has_key(matches[2]):
                        name = ged2rel[matches[2]]
                    else:
                        name = matches[2]
                    print name
                    event.setName(name)
                else:
                    print "*",event.getName()
                print event.getName()
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
        global ged2fam
        global ged2rel
        
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
            elif matches[1] == "CAUS" or matches[1] in "ADDR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "STAT" or matches[1] == "TEMP":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "HUSB" or matches[1] == "WIFE":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "OBJE" or matches[1] == "QUAY":
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
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
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

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_source_reference(self,source,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "PAGE":
                source.setPage(matches[2] + self.parse_continue_data(level+1))
            elif matches[1] == "DATA":
                date,text = self.parse_source_data(level+1)
                d = Date()
                d.set(date)
                source.setDate(d)
                source.setText(text)
            elif matches[1] == "QUAY":
                pass
            elif matches[1] == "NOTE":
                if not string.strip(matches[2]) or matches[2] and matches[2][0] != "@":
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
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
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
                name.setTitle(matches[2])
	    elif matches[1] == "GIVN":
                name.setFirstName(matches[2])
	    elif matches[1] == "SPFX":
                pass
	    elif matches[1] == "SURN":
                name.setSurname(matches[2])
	    elif matches[1] == "NSFX":
                name.setSuffix(matches[2])
	    elif matches[1] == "NICK":
                self.person.setNickName(matches[2])
            elif matches[1] == "SOUR":
                self.ignore_sub_junk(level+1)
            elif matches[1] == "NOTE":
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

	    if int(matches[0]) == 0:
                self.backup()
                return
	    elif matches[1] == "SOUR":
                if self.created_obj.get_text() == "":
                    self.update(self.created_obj,matches[2])
   	    elif matches[1] == "NAME":
                self.update(self.created_obj,matches[2])
   	    elif matches[1] == "VERS":
                self.update(self.version_obj,matches[2])
   	    elif matches[1] == "CORP":
                self.ignore_sub_junk(2)
   	    elif matches[1] == "DATA":
                self.parse_sub_data(3)
   	    elif matches[1] == "SUBM":
                pass
   	    elif matches[1] == "SUBN":
                pass
   	    elif matches[1] == "DEST":
                pass
   	    elif matches[1] == "FILE":
                self.ignore_sub_junk(2)
   	    elif matches[1] == "COPR":
                pass
   	    elif matches[1] == "CHAR":
                if matches[2] == "UNICODE" or matches[2] == "UTF-8" or \
                   matches[2] == "UTF8":
                    self.code = UNICODE
                elif matches[2] == "ANSEL":
                    self.code = ANSEL
                self.ignore_sub_junk(2)
                self.update(self.encoding_obj,matches[2])
   	    elif matches[1] == "GEDC":
                self.ignore_sub_junk(2)
   	    elif matches[1] == "_SCHEMA":
                self.parse_ftw_schema(2)
   	    elif matches[1] == "LANG":
                pass
   	    elif matches[1] == "PLAC":
                self.parse_place_form(2)
   	    elif matches[1] == "DATE":
                date = self.parse_date(2)
                date.date = matches[2]
   	    elif matches[1] == "NOTE":
                note = matches[2] + self.parse_continue_data(2)
            elif matches[1][0] == "_":
                self.ignore_sub_junk(2)
            else:
	        self.barf(2)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_ftw_schema(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "INDI":
                self.parse_ftw_indi_schema(level+1)
            elif matches[1] == "FAM":
                self.parse_ftw_fam_schema(level+1)
            else:
	        self.barf(2)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_ftw_indi_schema(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            else:
                label = self.parse_label(level+1)
                ged2rel[matches[1]] = label

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_label(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == "LABL":
                return matches[2]
            else:
	        self.barf(2)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def parse_ftw_fam_schema(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            else:
                label = self.parse_label(level+1)
                ged2fam[matches[1]] = label

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
    def parse_place_form(self,level):
        while 1:
            matches = self.get_next()

	    if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] != "FORM":
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
            elif matches[1] in "ADDR":
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
