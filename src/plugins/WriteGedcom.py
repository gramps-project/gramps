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

"Export to GEDCOM"

from RelLib import *
import os
import string
import time
import const
import utils
import intl
_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

import const
from latin_ansel import latin_to_ansel

topDialog = None
db = None

people_list = []
family_list = []
source_list = []

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def entire_database():
    global people_list
    global family_list
    global source_list
    
    people_list = db.getPersonMap().values()
    family_list = db.getFamilyMap().values()
    source_list = db.getSourceMap().values()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_descendants():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    descend(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_ancestors_and_descendants():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    descend(active_person)
    ancestors(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_ancestors():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    ancestors(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def interconnected():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    walk(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def descend(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    for family in person.getFamilyList():
        add_familys_sources(family)
        family_list.append(family)
        father = family.getFather()
        mother = family.getMother()
        if father != None and father not in people_list:
            people_list.append(father)
            add_persons_sources(father)
        if mother != None and mother not in people_list:
            people_list.append(mother)
            add_persons_sources(mother)
        for child in family.getChildList():
            descend(child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ancestors(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    family = person.getMainFamily()
    if family == None or family in family_list:
        return
    add_familys_sources(family)
    family_list.append(family)
    ancestors(family.getMother())
    ancestors(family.getFather())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def walk(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    families = person.getFamilyList() + person.getAltFamilyList()
    families.append(person.getMainFamily())
    for family in families:
        if family == None or family in family_list:
            continue
        add_familys_sources(family)
        family_list.append(family)
        walk(family.getFather())
        walk(family.getMother())
        for child in family.getChildList():
            walk(child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_persons_sources(person):
    elist = person.getEventList()[:]
    if person.getBirth():
        elist.append(person.getBirth())
    if person.getDeath():
        elist.append(person.getDeath())
    for event in elist:
        source_ref = event.getSourceRef()
        if source_ref != None:
            source_list.append(source_ref)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_familys_sources(family):
    elist = family.getEventList()[:]
    if family.getMarriage():
        elist.append(family.getMarriage())
    if family.getDivorce():
        elist.append(family.getDivorce())
    for event in elist:
        source_ref = event.getSourceRef()
        if source_ref != None:
            source_list.append(source_ref)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sortById(first,second):
    fid = first.getId()
    sid = second.getId()

    if fid == sid:
        return 0
    elif fid < sid:
        return -1
    else:
        return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def writeNote(g,id,note):
    g.write("1 NOTE @NI%s@\n" % id)
    g.write("0 @NI%s@ NOTE\n" % id)
    first = 0
    realfirst = 0
    words = []
    textlines = string.split(note,'\n')

    lineLen = 0
    text = ""
	
    for line in textlines:
        if line == "":
            continue
        line = latin_to_ansel(line)
        for word in string.split(line):
            text = text + " " + word
            if len(text) > 72 :
                if first == 0 or realfirst == 0:
                    g.write("1 CONC%s \n" % text)
                    realfirst = 1
                else:	
                    g.write("1 CONT%s\n" % text)
                    first = 0
                text = ""
        if len(text) > 0:
            if first == 0 or realfirst == 0:
                g.write("1 CONC%s \n" % text)
                realfirst = 1
            else:	
                g.write("1 CONT%s\n" % text)
                first = 1
            text = ""
			
        g.write("1 CONT\n")
        first = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_comment(g,note):
    g.write("3 NOTE ")
    first = 0
    realfirst = 0
    words = []
    textlines = string.split(note,'\n')

    lineLen = 0
    text = ""
	
    for line in textlines:
        if line == "":
            continue
        line = latin_to_ansel(line)
        for word in string.split(line):
            text = text + " " + word
            if len(text) > 72 :
                if realfirst == 0:
                    g.write("%s \n" % text)
                    realfirst = 1
                elif first == 0:
                    g.write("1 CONC%s \n" % text)
                    realfirst = 1
                else:	
                    g.write("1 CONT%s\n" % text)
                    first = 0
                text = ""
        if len(text) > 0:
            if realfirst == 0:
                g.write("%s \n" % text)
                realfirst = 1
            elif first == 0:
                g.write("1 CONC%s \n" % text)
                realfirst = 1
            else:	
                g.write("1 CONT%s\n" % text)
                first = 1
            text = ""
			
        g.write("1 CONT\n")
        first = 1
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_event_stats(g,event):
    if event.getSaveDate() != "":
        g.write("2 DATE %s\n" % latin_to_ansel(event.getSaveDate()))
    if event.getPlace() != "":
        g.write("2 PLAC %s\n" % latin_to_ansel(event.getPlace()))
    source = event.getSourceRef()
    if source:
        base = source.getBase()
        if base:
            g.write("2 SOUR @" + str(base.getId()) + "@\n")
        text = latin_to_ansel(string.strip(source.getPage()))
        if text != "":
            g.write("3 PAGE " + text + "\n")
        text = latin_to_ansel(string.strip(source.getText()))
        if text != "":
            g.write("3 DATA\n")
            g.write("4 TEXT " + text + "\n")
        comments = latin_to_ansel(string.strip(source.getComments()))
        if comments != "":
            write_comment(g,comments)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def probably_alive(person):

    if person == None:
        return 1

    if restrict == 0:
        return 0
    
    death = person.getDeath()
    birth = person.getBirth()

    if death.getDate() != "":
        return 0
    if birth.getDate() != "":
        year = birth.getDateObj().getYear()
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]
        if year != -1 and current_year - year > 110:
            return 0
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename):

    g = open(filename,"w")

    date = string.split(time.ctime(time.time()))

    g.write("0 HEAD\n")
    g.write("1 SOUR GRAMPS\n")
    g.write("2 VERS " + const.version + "\n")
    g.write("2 NAME Gramps\n")
    g.write("1 DEST GRAMPS\n")
    g.write("1 DATE %s %s %s\n" % (date[2],string.upper(date[1]),date[4]))
    g.write("1 CHAR ANSEL\n");
    g.write("1 SUBM @SUBM@\n")
    g.write("1 FILE %s\n" % filename)
    g.write("1 GEDC\n")
    g.write("2 VERS 5.5\n")
    g.write("0 @SUBM@ SUBM\n")
    owner = database.getResearcher()
    if owner.getName() != "":
        g.write("1 NAME " + latin_to_ansel(owner.getName()) +"\n")
        if owner.getAddress() != "":
            g.write("1 ADDR " + latin_to_ansel(owner.getAddress()) + "\n")
        if owner.getCity() != "":
            g.write("2 CITY " + latin_to_ansel(owner.getCity()) + "\n")
        if owner.getState() != "":
            g.write("2 STAE " + latin_to_ansel(owner.getState()) + "\n")
        if owner.getPostalCode() != "":
            g.write("2 POST " + latin_to_ansel(owner.getPostalCode()) + "\n")
        if owner.getCountry() != "":
            g.write("2 CTRY " + latin_to_ansel(owner.getCountry()) + "\n")
        if owner.getPhone() != "":
            g.write("1 PHON " + latin_to_ansel(owner.getPhone()) + "\n")

    people_list.sort(sortById)
    for person in people_list:
        g.write("0 @I%s@ INDI\n" % person.getId())
        name = person.getPrimaryName()
        firstName = latin_to_ansel(name.getFirstName())
        surName = latin_to_ansel(name.getSurname())
        suffix = latin_to_ansel(name.getSuffix())
        if suffix == "":
            g.write("1 NAME %s /%s/\n" % (firstName,surName))
        else:
            g.write("1 NAME %s /%s/, %s\n" % (firstName,surName, suffix))

        if name.getFirstName() != "":
            g.write("2 GIVN %s\n" % firstName)
        if name.getSurname() != "":
            g.write("2 SURN %s\n" % surName)
        if name.getSuffix() != "":
            g.write("2 NSFX %s\n" % suffix)

        if person.getGender() == Person.male:
            g.write("1 SEX M\n")
        else:	
            g.write("1 SEX F\n")

        if not probably_alive(person):

            birth = person.getBirth()
            if birth.getSaveDate() != "" or birth.getPlace() != "":
                g.write("1 BIRT\n")
                dump_event_stats(g,birth)
				
            death = person.getDeath()
            if death.getSaveDate() != "" or death.getPlace() != "":
                g.write("1 DEAT\n")
                dump_event_stats(g,death)

            uid = person.getPafUid()
            if uid != "":
                g.write("1 _UID " + uid + "\n")
            
            for event in person.getEventList():
                name = event.getName()
                if const.personalConstantEvents.has_key(name):
                    val = const.personalConstantEvents[name]
                else:
                    val = ""
                if val != "" : 
                    g.write("1 " + const.personalConstantEvents[name] + \
                            " " + event.getDescription() + "\n")
                else:
                    g.write("1 EVEN " + latin_to_ansel(event.getDescription()) + "\n")
                    g.write("2 TYPE " + latin_to_ansel(event.getName()) + "\n")
                dump_event_stats(g,event)

            for attr in person.getAttributeList():
                name = attr.getType()
                if const.personalConstantAttributes.has_key(name):
                    val = const.personalConstantEvents[name]
                else:
                    val = ""
                if val != "" : 
                    g.write("1 " + val + "\n")
                else:
                    g.write("1 EVEN " + "\n")
                    g.write("2 TYPE " + latin_to_ansel(name) + "\n")
                g.write("2 PLAC " + latin_to_ansel(attr.getValue()) + "\n")
            
        family = person.getMainFamily()
        if family != None and family in family_list:
            g.write("1 FAMC @F%s@\n" % family.getId())

        for family in person.getFamilyList():
            if family != None and family in family_list:
                g.write("1 FAMS @F%s@\n" % family.getId())

        if person.getNote() != "":
            writeNote(g,person.getId(),person.getNote())
			
    for family in family_list:
        g.write("0 @F%s@ FAM\n" % family.getId())
        person = family.getFather()
        if person != None:
            g.write("1 HUSB @I%s@\n" % person.getId())

        person = family.getMother()
        if person != None:
            g.write("1 WIFE @I%s@\n" % person.getId())

        father = family.getFather()
        mother = family.getMother()
        if not probably_alive(father) or not probably_alive(mother):
            event = family.getMarriage()
            if event != None:
                g.write("1 MARR\n");
                dump_event_stats(g,event)

            event = family.getDivorce()
            if event != None:
                g.write("1 DIV\n");
                dump_event_stats(g,event)

            for event in family.getEventList():
                text = event.getName()

                if const.familyConstantEvents.has_key(name):
                    val = const.personalConstantEvents[name]
                else:
                    val = ""
                if val != "": # and val[0] != "_":
                    g.write("1 %s\n" % const.familyConstantEvents[text])
                else:	
                    g.write("1 EVEN\n")
                    g.write("2 TYPE %s\n" % latin_to_ansel(event.getName()))
					
                dump_event_stats(g,event)

        for person in family.getChildList():
            g.write("1 CHIL @I%s@\n" % person.getId())

    for source in source_list:
        g.write("0 @" + str(source.getId()) + "@ SOUR\n")
        if source.getTitle() != "":
            g.write("1 TITL " + latin_to_ansel(source.getTitle()) + "\n")
        if source.getAuthor() != "":
            g.write("1 AUTH " + latin_to_ansel(source.getAuthor()) + "\n")
        if source.getPubInfo() != "":
            g.write("1 PUBL " + latin_to_ansel(source.getPubInfo()) + "\n")
        if source.getTitle() != "":
            g.write("1 ABBR " + latin_to_ansel(source.getTitle()) + "\n")
        if source.getCallNumber() != "":
            g.write("1 CALN " + latin_to_ansel(source.getCallNumber()) + "\n")
            
        
    g.write("0 TRLR\n")
    g.close()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global topDialog
    global restrict
    
    restrict = topDialog.get_widget("restrict").get_active()
    filter_obj = topDialog.get_widget("filter").get_menu().get_active()
    filter = filter_obj.get_data("filter")

    name = topDialog.get_widget("filename").get_text()
    filter()
    
    exportData(db,name)
    utils.destroy_passed_object(obj)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def writeData(database,person):
    global db
    global topDialog
    global active_person
    
    db = database
    active_person = person
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "gedcomexport.glade"
        
    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked
        }

    topDialog = GladeXML(glade_file,"gedcomExport")
    topDialog.signal_autoconnect(dic)

    filter_obj = topDialog.get_widget("filter")
    myMenu = GtkMenu()
    menuitem = GtkMenuItem(_("Entire Database"))
    myMenu.append(menuitem)
    menuitem.set_data("filter",entire_database)
    menuitem.show()
    name = active_person.getPrimaryName().getRegularName()
    menuitem = GtkMenuItem(_("Ancestors of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_ancestors)
    menuitem.show()
    menuitem = GtkMenuItem(_("Descendants of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_descendants)
    menuitem.show()
    menuitem = GtkMenuItem(_("Ancestors and Descendants of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_ancestors_and_descendants)
    menuitem.show()
    menuitem = GtkMenuItem(_("People somehow connected to %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",interconnected)
    menuitem.show()
    filter_obj.set_menu(myMenu)

    topDialog.get_widget("gedcomExport").show()

def get_name():
    return _("Export to GEDCOM")
