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
from latin_utf8  import latin_to_utf8

cnvtxt = latin_to_ansel

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
    families = person.getFamilyList()
    families.append(person.getMainFamily())
    for f in person.getAltFamilyList():
        families.append(f[0])
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
def write_long_text(g,tag,level,note):
    prefix = "%d %s" % (level,tag)
    textlines = string.split(note,'\n')
    for line in textlines:
        while len(line) > 0:
            if len(line) > 70:
                g.write("%s %s\n" % (prefix,line[0:70]))
                line = line[70:]
            else:
                g.write("%s %s\n" % (prefix,line))
                line = ""
            if len(line) > 0:
                prefix = "%d CONC" % (level + 1)
            else:
                prefix = "%d CONT" % (level + 1)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_event_stats(g,event):
    if event.getSaveDate() != "":
        g.write("2 DATE %s\n" % cnvtxt(event.getSaveDate()))
    if event.getPlace() != "":
        g.write("2 PLAC %s\n" % cnvtxt(event.getPlace()))
    if event.getNote() != "":
        write_long_text(g,"NOTE",2,event.getNote())
    if event.getSourceRef() != None:
        write_source_ref(g,2,event.getSourceRef())
        
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
def write_person_name(g,name,nick):
    firstName = cnvtxt(name.getFirstName())
    surName = cnvtxt(name.getSurname())
    suffix = cnvtxt(name.getSuffix())
    title = cnvtxt(name.getTitle())
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
    if name.getTitle() != "":
        g.write("2 TITL %s\n" % title)
    if nick != "":
        g.write('2 NICK %s\n' % nick)
    if name.getNote() != "":
        write_long_text(g,"NOTE",2,name.getNote())
    if name.getSourceRef() != None:
        write_source_ref(g,2,name.getSourceRef())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_source_ref(g,level,ref):
    if ref.getBase() == None:
        return
    g.write("%d SOUR @S%s@\n" % (level,ref.getBase().getId()))
    if ref.getPage() != "":
        g.write("%d PAGE %s\n" % (level+1,ref.getPage()))

    ref_text = ref.getText()
    if ref_text != "" or ref.getDate().getDate() != "":
        g.write('%d DATA\n' % (level+1))
        if ref_text != "":
            write_long_text(g,"TEXT",level+1,ref_text)
        if ref.getDate().getDate():
            g.write("%d DATE %s\n" % (level+1,ref.getDate().getSaveDate()))
    if ref.getComments() != "":
        write_long_text(g,"NOTE",level+1,ref.getComments())
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_person(g,person):
    g.write("0 @I%s@ INDI\n" % person.getId())

    write_person_name(g,person.getPrimaryName(),person.getNickName())
    for name in person.getAlternateNames():
        write_person_name(g,name,"")
    
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
            g.write("1 _UID %s\n" % uid)
            
        for event in person.getEventList():
            name = event.getName()
            if const.personalConstantEvents.has_key(name):
                val = const.personalConstantEvents[name]
            else:
                val = ""
            if val != "" :
                g.write("1 %s %s\n" % (cnvtxt(val),cnvtxt(event.getDescription())))
            else:
                g.write("1 EVEN %s\n" % cnvtxt(event.getDescription()))
                g.write("2 TYPE %s\n" % cnvtxt(event.getName()))
            dump_event_stats(g,event)

        for attr in person.getAttributeList():
            name = attr.getType()
            if const.personalConstantAttributes.has_key(name):
                val = const.personalConstantEvents[name]
            else:
                val = ""
            if val != "" : 
                g.write("1 %s\n" % val)
            else:
                g.write("1 EVEN\n")
                g.write("2 TYPE %s\n" % cnvtxt(name))
            g.write("2 PLAC %s\n" % cnvtxt(attr.getValue()))
            if attr.getNote() != "":
                write_long_text(g,"NOTE",2,attr.getNote())
            if attr.getSourceRef() != None:
                write_source_ref(g,2,attr.getSourceRef())

        for addr in person.getAddressList():
            write_long_text(g,"RESI",1,addr.getStreet())
            if addr.getCity() != "":
                g.write("2 CITY %s\n" % addr.getCity())
            if addr.getState() != "":
                g.write("2 STAE %s\n" % addr.getState())
            if addr.getPostal() != "":
                g.write("2 POST %s\n" % addr.getPostal())
            if addr.getCountry() != "":
                g.write("2 CTRY %s\n" % addr.getCountry())
            if addr.getNote() != "":
                write_long_text(g,"NOTE",2,addr.getNote())
            if addr.getSourceRef() != None:
                write_source_ref(g,2,addr.getSourceRef())

    family = person.getMainFamily()
    if family != None and family in family_list:
        g.write("1 FAMC @F%s@\n" % family.getId())
        g.write("2 PEDI birth\n")

    for family in person.getAltFamilyList():
        g.write("1 FAMC @F%s@\n" % family[0].getId())
        if string.lower(family[1]) == "adopted":
            g.write("2 PEDI adopted\n")
        
    for family in person.getFamilyList():
        if family != None and family in family_list:
            g.write("1 FAMS @F%s@\n" % family.getId())

    for url in person.getUrlList():
        g.write('1 OBJE\n')
        g.write('2 FORM URL\n')
        if url.get_description() != "":
            g.write('2 TITL %s\n' % url.get_description())
        if url.get_path() != "":
            g.write('2 FILE %s\n' % url.get_path())

    if person.getNote() != "":
        write_long_text(g,"NOTE",1,person.getNote())
			
    
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
    if cnvtxt == latin_to_ansel:
        g.write("1 CHAR ANSEL\n");
    else:
        g.write("1 CHAR UNICODE\n");
    g.write("1 SUBM @SUBM@\n")
    g.write("1 FILE %s\n" % filename)
    g.write("1 GEDC\n")
    g.write("2 VERS 5.5\n")
    g.write("0 @SUBM@ SUBM\n")
    owner = database.getResearcher()
    if owner.getName() != "":
        g.write("1 NAME " + cnvtxt(owner.getName()) +"\n")
        if owner.getAddress() != "":
            g.write("1 ADDR " + cnvtxt(owner.getAddress()) + "\n")
        if owner.getCity() != "":
            g.write("2 CITY " + cnvtxt(owner.getCity()) + "\n")
        if owner.getState() != "":
            g.write("2 STAE " + cnvtxt(owner.getState()) + "\n")
        if owner.getPostalCode() != "":
            g.write("2 POST " + cnvtxt(owner.getPostalCode()) + "\n")
        if owner.getCountry() != "":
            g.write("2 CTRY " + cnvtxt(owner.getCountry()) + "\n")
        if owner.getPhone() != "":
            g.write("1 PHON " + cnvtxt(owner.getPhone()) + "\n")

    people_list.sort(sortById)
    for person in people_list:
        write_person(g,person)
            
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
                name = event.getName()

                if const.familyConstantEvents.has_key(name):
                    val = const.familyConstantEvents[name]
                else:
                    val = ""
                if val != "":
                    g.write("1 %s\n" % const.familyConstantEvents[name])
                else:	
                    g.write("1 EVEN\n")
                    g.write("2 TYPE %s\n" % cnvtxt(name))
					
                dump_event_stats(g,event)

        for person in family.getChildList():
            g.write("1 CHIL @I%s@\n" % person.getId())

    for source in source_list:
        g.write("0 @S%s@ SOUR\n" % source.getId())
        if source.getTitle() != "":
            g.write("1 TITL %s\n" % cnvtxt(source.getTitle()))
        if source.getAuthor() != "":
            g.write("1 AUTH %s\n" % cnvtxt(source.getAuthor()))
        if source.getPubInfo() != "":
            g.write("1 PUBL %s\n" % cnvtxt(source.getPubInfo()))
        if source.getTitle() != "":
            g.write("1 ABBR %s\n" % cnvtxt(source.getTitle()))
        if source.getCallNumber() != "":
            g.write("1 CALN %s\n" % cnvtxt(source.getCallNumber()))
        if source.getNote() != "":
            write_long_text(g,"NOTE",1,source.getNote())
            
        
    g.write("0 TRLR\n")
    g.close()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def gedcom_date(date):
    if date.range == 1:
        s1 = ged_subdate(date.get_start_date())
        s2 = ged_subdate(date.get_stop_date())
        return "BET %s AND %s" % (s1,s2)
    elif date.range == -1:
        return "(%s)" % date.text
    else:
        return ged_subdate(self.start)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ged_subdate(date):
        
    if date.month == -1 and date.day == -1 and date.year == -1 :
        return ""
    elif date.day == -1:
        if date.month == -1:
            retval = str(date.year)
        elif date.year == -1:
            retval = "(%s)" % SingleDate.emname[date.month]
        else:	
            retval = "%s %d" % (SingleDate.emname[date.month],date.year)
    elif date.month == -1:
        retval = str(date.year)
    else:
        month = SingleDate.emname[date.month]
        if date.year == -1:
            retval = "(%d %s)" % (date.day,month)
        else:
            retval = "%d %s %d" % (date.day,month,date.year)

    if date.mode == SingleDate.about:
        retval = "ABT %s"  % retval

    if date.mode == SingleDate.before:
        retval = "BEF %s" % retval
    elif date.mode == SingleDate.after:
        retval = "AFT %s" % retval

    return retval

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global topDialog
    global restrict
    global cnvtxt
    
    restrict = topDialog.get_widget("restrict").get_active()
    filter_obj = topDialog.get_widget("filter").get_menu().get_active()
    filter = filter_obj.get_data("filter")

    if topDialog.get_widget("ansel").get_active():
        cnvtxt = latin_to_ansel
    else:
        cnvtxt = latin_to_utf8

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
