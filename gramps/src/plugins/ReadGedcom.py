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

import os
import re
import string
import const
import utils
import shutil

from gtk import *
from gnome.ui import *
from libglade import *


topDialog = None
db = None
callback = None
glade_file = None
clear_data = 0

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
    
    headRegexp   = re.compile(r"\s*0\s+HEAD")
    charRegexp   = re.compile(r"\s*1\s+CHAR\s+(\S+)\s*$")
    sourceRegexp = re.compile(r"\s*1\s+SOUR\s+(\S?[\s\S]*\S)\s*$")
    srcrefRegexp = re.compile(r"\s*2\s+SOUR\s+@(.+)@")
    indiRegexp   = re.compile(r"\s*0\s+@(.+)@\s+INDI")
    familyRegexp = re.compile(r"\s*0\s+@(.+)@\s+FAM")
    srcRegexp    = re.compile(r"\s*0\s+@(.+)@\s+SOUR")
    topRegexp    = re.compile(r"\s*0\s+")
    changeRegexp = re.compile(r"\s*1\s+CHAN")
    geventRegexp = re.compile(r"\s*1\s+EVEN")
    numRegexp    = re.compile(r"\s*[2-9]\s")
    eventRegexp  = re.compile(r"\s*1\s+([\S]+)\s*(.*)?$")
    titleRegexp  = re.compile(r"\s*1\s+TITL\s*(.*)?$")
    objeRegexp   = re.compile(r"\s*1\s+OBJE")
    title2Regexp = re.compile(r"\s*2\s+TITL\s*(.*)?$")
    fileRegexp   = re.compile(r"\s*2\s+FILE\s*(.*)?$")
    uidRegexp    = re.compile(r"\s*1\s+_UID\s*(.*)?$")
    authorRegexp = re.compile(r"\s*1\s+AUTH\s*(.*)?$")
    pubRegexp    = re.compile(r"\s*1\s+PUBL\s*(.*)?$")
    callnoRegexp = re.compile(r"\s*1\s+CALN\s*(.*)?$")
    prefixRegexp = re.compile(r"\s*2\s+NPFX\s*(.*)?$")
    suffixRegexp = re.compile(r"\s*2\s+NSFX\s*(.*)?$")
    birthRegexp  = re.compile(r"\s*1\s+BIRT\s*(.*)?$")
    noterefRegexp= re.compile(r"\s*1\s+NOTE\s+@(.+)@")
    noteactRegexp= re.compile(r"\s*1\s+NOTE\s+(.+)*")
    refnRegexp   = re.compile(r"\s*1\s+REFN")
    noteRegexp   = re.compile(r"\s*0\s+@(.+)@\s+NOTE\s*(.*)?$")
    concRegexp   = re.compile(r"\s*1\s+CONC\s(.*)?$")
    contRegexp   = re.compile(r"\s*1\s+CONT\s(.*)?$")
    deathRegexp  = re.compile(r"\s*1\s+DEAT\s*(.*)?$")
    divorceRegexp= re.compile(r"\s*1\s+DIV\s*(.*)?$")
    marriedRegexp= re.compile(r"\s*1\s+MAR\s*(.*)?$")
    genderRegexp = re.compile(r"\s*1\s+SEX\s+(\S)?")
    typeRegexp   = re.compile(r"\s*2\s+TYPE\s*(.*)?$")
    placeRegexp  = re.compile(r"\s*2\s+PLAC\s*(.*)?$")
    pageRegexp   = re.compile(r"\s*3\s+PAGE\s*(.*)?$")
    dateRegexp   = re.compile(r"\s*2\s+DATE\s*(.*)?$")
    nameRegexp   = re.compile(r"\s*1\s+NAME\s+([\S\s]*\S)?\s*/([^/]+)?/\s*,?\s*([\S]+)?")
    famsRegexp   = re.compile(r"\s*1\s+FAMS\s+@(.*)@")
    famcRegexp   = re.compile(r"\s*1\s+FAMC\s+@(.*)@")
    fatherRegexp = re.compile(r"\s*1\s+HUSB\s+@(.*)@")
    motherRegexp = re.compile(r"\s*1\s+WIFE\s+@(.*)@")
    childRegexp  = re.compile(r"\s*1\s+CHIL\s+@(.*)@")

    noteId = ""
    inlineNote = 0
    inlocalNote = 0
    user2note = {}
    person2note = {}
    personActive = 0
    familyActive = 0
    sourceActive = 0
    noteActive = 0
    allLines = []
    values = {}
    index = 0
    currentLine = 0
    fmap = {}
    pmap = {}
    smap = {}
    familyTree = 0
    in_change = 0
    photo = None
    ansel = 0

    # add some checking here

    gedcom = open(filename,"r")

    if clear_data == 1:
        database.new()

    statusTop = GladeXML(glade_file,"status")
    statusWindow = statusTop.get_widget("status")
    progressWindow = statusTop.get_widget("progress")
    
    allLines = gedcom.readlines()
    gedcom.close()

    # use search here instead of match, since PAF5 seems to like to
    # insert garbage as the first couple of characters in the file
    
    regex_match = headRegexp.search(allLines[0])
    if regex_match == None:
        raise InvalidGedcom
	
    total = len(allLines)

    value = 0
    for index in range(1,21):
        value = value + total/20
        values[index] = value

    index = 1
    value = values[1]
    for line in allLines:

        line = string.replace(line, '\r', "")
        if ansel == 1:
            line = latin_ansel.ansel_to_latin(line)
            
        if currentLine == value and index <= 20:
            index = index + 1
            if index <= 20:
                value = values[index]
                progressWindow.set_percentage(float(currentLine)/float(total))
                while events_pending():
                    mainiteration()

        currentLine = currentLine + 1

		
        regex_match = charRegexp.match(line)
        if regex_match:
            id = regex_match.groups()
            if id[0] == "ANSEL":
                ansel = 1
            continue

        regex_match = changeRegexp.match(line)
        if regex_match:
            in_change = 1
            continue

        if in_change:
            if numRegexp.match(line):
                in_change = 0
                continue

        regex_match = indiRegexp.match(line)
        if regex_match:
            id = regex_match.groups()
            person = database.findPerson(id[0],pmap)
            personActive = 1
            familyActive = 0
            sourceActive = 0
            noteActive = 0
            continue

        regex_match = familyRegexp.match(line)
        if regex_match:
            id = regex_match.groups()
            family = database.findFamily(id[0],fmap)
            personActive = 0
            familyActive = 1
            sourceActive = 0
            noteActive = 0
            continue

        regex_match = srcRegexp.match(line)
        if regex_match:
            id = regex_match.groups()
            source = database.findSource(id[0],smap)
            personActive = 0
            familyActive = 0
            sourceActive = 1
            noteActive = 0
            continue
				
        regex_match = noteRegexp.match(line)
        if regex_match:
            matches = regex_match.groups()
            noteId = matches[0]
            noteActive = 1
            sourceActive = 0
            familyActive = 0
            personActive = 0
            if matches[1] == None:
                user2note[noteId] = ""
            else:
                user2note[noteId] = matches[1]
                continue

        regex_match = sourceRegexp.match(line)
        if regex_match:
            matches = regex_match.groups()
            if matches[0] == "FTW":
                familyTree = 1
                continue

        regex_match = topRegexp.match(line)
        if regex_match:
            personActive = 0
            familyActive = 0
            noteActive = 0
            continue				

        if familyActive == 1:
            regex_match = srcrefRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source = database.findSource(matches[0],smap)
                mySource = Source()
                mySource.setBase(source)
                event.setSource(mySource)
                continue

            regex_match = pageRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                mySource.setPage(matches[0])
                continue

            regex_match = fatherRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                father = database.findPerson(matches[0],pmap)
                family.setFather(father)
                continue

            regex_match = motherRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                mother = database.findPerson(matches[0],pmap)
                family.setMother(mother)
                continue
            
            regex_match = childRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                child = database.findPerson(matches[0],pmap)
                family.addChild(child)
                continue

            regex_match = marriedRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()
                event.setName("Marriage")
                family.setMarriage(event)
                continue

            regex_match = divorceRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()
                event.setName("Divorce")
                family.setDivorce(event)
                continue

            regex_match = placeRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event.setPlace(matches[0])
                continue

            regex_match = geventRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()
                family.addEvent(event)
                continue

            regex_match = dateRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                try:
                    event.setDate(matches[0])
                except:
                    pass
                continue
            
            regex_match = typeRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event.setName(matches[0])
                continue

        elif personActive == 1:

            regex_match = nameRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                name = Name()
                if matches[0] :
                    name.setFirstName(matches[0])
                if matches[1] :
                    name.setSurname(matches[1])
                if matches[2] :
                    name.setSuffix(matches[2])
					
                person.setPrimaryName(name)
                continue

            regex_match = titleRegexp.match(line)
            if regex_match:
                continue

            regex_match = prefixRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                name.setTitle(matches[0])
                continue

            regex_match = uidRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                person.setPafUid(matches[0])
                continue

            regex_match = suffixRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                name.setSuffix(matches[0])
                continue

            if inlocalNote == 1:

                regex_match = concRegexp.match(line)
                if regex_match :
                    matches = regex_match.groups()
                    user2note[noteId] = user2note[noteId] + matches[0]
                    continue

                regex_match = contRegexp.match(line)
                if regex_match :
                    matches = regex_match.groups()
                    user2note[noteId] = user2note[noteId] + "\n" + matches[0]
                    continue

                inlocalNote = 0
                person.setNote(user2note[noteId])

            regex_match = noteactRegexp.match(line)
            if regex_match :
                inlocalNote = 1
                matches = regex_match.groups()
                noteId = "local%d" % inlineNote
                inlineNote = inlineNote + 1
                if matches[0] == None:
                    user2note[noteId] = ""
                else:
                    user2note[noteId] = matches[0]
                continue

            regex_match = srcrefRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source = database.findSource(matches[0],smap)
                mySource = Source()
                mySource.setBase(source)
                event.setSource(mySource)
                continue

            regex_match = pageRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                mySource.setPage(matches[0])
                continue

            regex_match = noterefRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                person2note[person] = matches[0]
                continue

            regex_match = genderRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                if matches[0] == "M":
                    person.setGender(Person.male)
                else:
                    person.setGender(Person.female)
                continue

            regex_match = famcRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                new_family = database.findFamily(matches[0],fmap)
                person.setMainFamily(new_family)
                continue

            regex_match = famsRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                new_family = database.findFamily(matches[0],fmap)
                person.addFamily(new_family)
                continue

            regex_match = birthRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()

                # check to see if the person already had a birthdate set.
                # if he/she does, then add the birthdate as an alternate.
                # this assumes that the first birthdate in the GEDCOM file
                # is the one that should be considered the primary
                
                lbirth = person.getBirth()
                if lbirth.getDate() != "" or lbirth.getPlace() != "":
                    person.addEvent(event)
                    event.setName("Alternate Birth")
                else:
                    person.setBirth(event)
                continue

            regex_match = deathRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()

                # check to see if the person already had a birthdate set.
                # if he/she does, then add the birthdate as an alternate.
                # this assumes that the first birthdate in the GEDCOM file
                # is the one that should be considered the primary
                
                ldeath = person.getDeath()
                if ldeath.getDate() != "" or ldeath.getPlace() != "":
                    person.addEvent(event)
                    event.setName("Alternate Death")
                else:
                    person.setDeath(event)
                continue

            regex_match = refnRegexp.match(line)
            if regex_match :
                continue
            
            regex_match = geventRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()
                person.addEvent(event)
                continue

            regex_match = eventRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event = Event()
                if ged2rel.has_key(matches[0]):
                    type = ged2rel[matches[0]]
                elif ged2fam.has_key(matches[0]):
                    type = ged2fam[matches[0]]
                else:
                    type = matches[0]
                event.setName(type)
                if matches[1] :
                    event.setDescription(matches[1])
                person.addEvent(event)
                continue
				
            regex_match = typeRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event.setName(matches[0])
                continue

            regex_match = placeRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                event.setPlace(matches[0])
                continue

            regex_match = dateRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                try:
                    event.setDate(matches[0])
                except:
                    pass
                continue

            regex_match = fileRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                imagepath = find_file(matches[0],os.path.dirname(filename))
                savepath = database.getSavePath()
                if imagepath != "" and savepath != "":
                    id = person.getId()
                    for index in range(0,100):
                        base = "i%s_%d.jpg" % (id,index)
                        name = savepath + os.sep + base
                        if os.path.exists(name) == 0:
                            break
                        shutil.copy(imagepath,name)

                    photo = Photo()
                continue

            regex_match = title2Regexp.match(line)
            if regex_match and photo != None:
                matches = regex_match.groups()
                photo.setDescripton(matches[0])
                continue

            if objeRegexp.match(line):
                photo = None
                continue
			
        elif noteActive == 1:

            regex_match = concRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                user2note[noteId] = user2note[noteId] + matches[0]
                continue

            regex_match = contRegexp.match(line)
            if regex_match :
                matches = regex_match.groups()
                user2note[noteId] = user2note[noteId] + "\n" + matches[0]
                continue

        elif sourceActive == 1:

            regex_match = titleRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source.setTitle(matches[0])
                continue

            regex_match = authorRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source.setAuthor(matches[0])
                continue

            regex_match = pubRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source.setPubInfo(matches[0])
                continue

            regex_match = callnoRegexp.match(line)
            if regex_match:
                matches = regex_match.groups()
                source.setCallNumber(matches[0])
                continue

    for person in person2note.keys():
        name = person.getPrimaryName()
        noteId = person2note[person]
        person.setNote(user2note[noteId])

    statusWindow.destroy()

    callback(1)

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
    try:
        importData(db,name)
    except InvalidGedcom:
        GnomeErrorDialog(name + " is not a valid GEDCOM file")
        statusWindow.destroy()
    except IOError, val:
        GnomeErrorDialog("Could not load " + name + "\n" + val[1])
        statusWindow.destroy()
#    except:
#        GnomeErrorDialog("Could not load " + name + \
#                         "\n due to an unexpected internal error")
#        statusWindow.destroy()
    
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

