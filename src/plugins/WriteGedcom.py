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

active_person = None
topDialog = None
db = None

people_list = []
family_list = []
source_list = []
adopt_mode = 1

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

    elist.append(person.getBirth())
    elist.append(person.getDeath())
    for event in elist:
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)
    for event in person.getAddressList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)
    for event in person.getAttibuteList:
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)
    for name in person.getNameList + [ person.getPrimaryName() ]:
        if private and name.getPrivacy():
            continue
        for source_ref in name.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_familys_sources(family):
    for event in family.getEventList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)
    for attr in family.getAttributeList():
        if private and attr.getPrivacy():
            continue
        for source_ref in attr.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in source_list:
                source_list.append(sbase)

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
    if len(note) == 0:
        g.write("%s\n" % prefix)
    else:
        for line in textlines:
            ll = len(line)
            while ll > 0:
                brkpt = 70
                if ll > brkpt:
                    while (ll > brkpt and line[brkpt] in string.whitespace):
                        brkpt = brkpt+1
                    if ll == brkpt:
                        g.write("%s %s\n" % (prefix,line))
                        line = ''
                    else:
                        g.write("%s %s\n" % (prefix,line[0:brkpt+1]))
                        line = line[brkpt+1:]
                else:
                    g.write("%s %s\n" % (prefix,line))
                    line = ""
                if len(line) > 0:
                    prefix = "%d CONC" % (level + 1)
                else:
                    prefix = "%d CONT" % (level + 1)
                ll = len(line)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_event_stats(g,event):
    if event.getSaveDate() != "":
        g.write("2 DATE %s\n" % cnvtxt(event.getSaveDate()))
    if event.getPlaceName() != "":
        g.write("2 PLAC %s\n" % cnvtxt(event.getPlaceName()))
    if event.getCause() != "":
        g.write("2 CAUS %s\n" % cnvtxt(event.getCause()))
    if event.getNote() != "":
        write_long_text(g,"NOTE",2,event.getNote())
    for srcref in event.getSourceRefList():
        write_source_ref(g,2,srcref)
        
def fmtline(text,limit,level):
    new_text = []
    text = cnvtxt(text)
    while len(text) > limit:
        new_text.append(text[0:limit-1])
        text = text[limit:]
    if len(text) > 0:
        new_text.append(text)
    app = "\n%d CONC " % (level+1)
    return string.join(new_text,app)
    
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
        g.write("2 NPFX %s\n" % title)
    if nick != "":
        g.write('2 NICK %s\n' % nick)
    if name.getNote() != "":
        write_long_text(g,"NOTE",2,name.getNote())
    for srcref in name.getSourceRefList():
        write_source_ref(g,2,srcref)

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
            write_long_text(g,"TEXT",level+2,ref_text)
        if ref.getDate().getDate():
            g.write("%d DATE %s\n" % (level+2,ref.getDate().getSaveDate()))
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
#    for name in person.getAlternateNames():
#        write_person_name(g,name,"")
    
    if person.getGender() == Person.male:
        g.write("1 SEX M\n")
    elif person.getGender() == Person.female:	
        g.write("1 SEX F\n")

    if not probably_alive(person):

        birth = person.getBirth()
        if not (private and birth.getPrivacy()):
            if birth.getSaveDate() != "" or birth.getPlaceName() != "":
                g.write("1 BIRT\n")
                dump_event_stats(g,birth)
				
        death = person.getDeath()
        if not (private and death.getPrivacy()):
            if death.getSaveDate() != "" or death.getPlaceName() != "":
                g.write("1 DEAT\n")
                dump_event_stats(g,death)

        uid = person.getPafUid()
        if uid != "":
            g.write("1 _UID %s\n" % uid)
            
        ad = 0
        for event in person.getEventList():
            if private and event.getPrivacy():
                continue
            name = event.getName()
            if const.personalConstantEvents.has_key(name):
                val = const.personalConstantEvents[name]
            else:
                val = ""
            if adopt_mode == 1 and val == "ADOP":
                ad = 1
                g.write('1 ADOP\n')
                fam = None
                for f in person.getAltFamilyList():
                    mrel = string.lower(f[1])
                    frel = string.lower(f[2])
                    if mrel=="adopted" or mrel=="adopted":
                        fam = f[0]
                        break
                if fam:
                    g.write('2 FAMC @F%s@\n' % fam.getId())
                    if mrel == frel:
                        g.write('3 ADOP BOTH\n')
                    elif mrel == "adopted":
                        g.write('3 ADOP WIFE\n')
                    else:
                        g.write('3 ADOP HUSB\n')
            elif val != "" :
                g.write("1 %s %s\n" % (cnvtxt(val),cnvtxt(event.getDescription())))
            else:
                g.write("1 EVEN %s\n" % cnvtxt(event.getDescription()))
                g.write("2 TYPE %s\n" % cnvtxt(event.getName()))
            dump_event_stats(g,event)

        if adopt_mode == 1 and ad == 0 and len(person.getAltFamilyList()) != 0:
            g.write('1 ADOP\n')
            fam = None
            for f in person.getAltFamilyList():
                mrel = string.lower(f[1])
                frel = string.lower(f[2])
                if mrel=="adopted" or mrel=="adopted":
                    fam = f[0]
                    break
            if fam:
                g.write('2 FAMC @F%s@\n' % fam.getId())
                if mrel == frel:
                    g.write('3 ADOP BOTH\n')
                elif mrel == "adopted":
                    g.write('3 ADOP WIFE\n')
                else:
                    g.write('3 ADOP HUSB\n')

        for attr in person.getAttributeList():
            if private and attr.getPrivacy():
                continue
            name = attr.getType()
            if const.personalConstantAttributes.has_key(name):
                val = const.personalConstantAttributes[name]
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
            for srcref in attr.getSourceRefList():
                write_source_ref(g,2,srcref)

        for addr in person.getAddressList():
            if private and addr.getPrivacy():
                continue
            g.write("1 RESI\n")
            datestr = addr.getDateObj().getSaveDate()
            if datestr != "":
                g.write("2 DATE %s\n" % cnvtxt(datestr))
            write_long_text(g,"ADDR",2,addr.getStreet())
            if addr.getCity() != "":
                g.write("3 CITY %s\n" % addr.getCity())
            if addr.getState() != "":
                g.write("3 STAE %s\n" % addr.getState())
            if addr.getPostal() != "":
                g.write("3 POST %s\n" % addr.getPostal())
            if addr.getCountry() != "":
                g.write("3 CTRY %s\n" % addr.getCountry())
            if addr.getNote() != "":
                write_long_text(g,"NOTE",3,addr.getNote())
            for srcref in addr.getSourceRefList():
                write_source_ref(g,3,srcref)

    family = person.getMainFamily()
    if family != None and family in family_list:
        g.write("1 FAMC @F%s@\n" % family.getId())

    for family in person.getAltFamilyList():
        g.write("1 FAMC @F%s@\n" % family[0].getId())
        if adopt_mode == 0:
            if string.lower(family[1]) == "adopted":
                g.write("2 PEDI Adopted\n")
        
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
def exportData(database, filename, progress, pbar, fbar, sbar):

    try:
        g = open(filename,"w")
    except IOError,msg:
        msg = "%s\n%s" % (_("Could not open %s") % filename,str(msg))
        GnomeErrorDialog(msg)
        progress.destroy()
        return
    except:
        GnomeErrorDialog(_("Could not open %s") % filename)
        progress.destroy()
        return

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
        g.write("1 CHAR UTF-8\n");
    g.write("1 SUBM @SUBM@\n")
    g.write("1 FILE %s\n" % filename)
    g.write("1 GEDC\n")
    g.write("2 VERS 5.5\n")
    g.write('2 FORM LINEAGE-LINKED\n')
    g.write("0 @SUBM@ SUBM\n")
    owner = database.getResearcher()
    if owner.getName() != "":
        g.write("1 NAME " + cnvtxt(owner.getName()) +"\n")
    else:
        g.write('1 NAME Not Provided\n')
    if owner.getAddress() != "":
        cnt = 0
        g.write("1 ADDR " + cnvtxt(owner.getAddress()) + "\n")
        if owner.getCity() != "":
            g.write("2 CONT " + cnvtxt(owner.getCity()) + "\n")
            cnt = 1
        if owner.getState() != "":
            g.write("2 CONT " + cnvtxt(owner.getState()) + "\n")
            cnt = 1
        if owner.getPostalCode() != "":
            g.write("2 CONT " + cnvtxt(owner.getPostalCode()) + "\n")
            cnt = 1
        if owner.getCountry() != "":
            g.write("2 CONT " + cnvtxt(owner.getCountry()) + "\n")
            cnt = 1
        if owner.getPhone() != "":
            g.write("2 PHON " + cnvtxt(owner.getPhone()) + "\n")
            cnt = 1
        if cnt == 0:
            g.write('2 CONT Not Provided\n')
    else:
        g.write('1 ADDR Not Provided\n')
        g.write('2 CONT Not Provided\n')
    people_list.sort(sortById)
    nump = float(len(people_list))
    index = 0.0
    for person in people_list:
        write_person(g,person)
        index = index + 1
        pbar.set_value((100*index)/nump)
        while(events_pending()):
            mainiteration()
    pbar.set_value(100.0)

    nump = float(len(family_list))
    index = 0.0
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
            for event in family.getEventList():
                if private and event.getPrivacy():
                    continue
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
            if adopt_mode == 2:
                if person.getMainFamily() == family:
                    g.write('2 _FREL Natural\n')
                    g.write('2 _MREL Natural\n')
                else:
                    for f in person.getAltFamilyList():
                        if f[0] == family:
                            g.write('2 _FREL %s\n' % f[2])
                            g.write('2 _MREL %s\n' % f[1])
                            break
            if adopt_mode == 3:
                for f in person.getAltFamilyList():
                    if f[0] == family:
                        g.write('2 _STAT %s\n' % f[2])
                        break
                
        index = index + 1
        fbar.set_value((100*index)/nump)
        while(events_pending()):
            mainiteration()
    fbar.set_value(100.0)

    nump = float(len(source_list))
    index = 0.0
    for source in source_list:
        g.write("0 @S%s@ SOUR\n" % source.getId())
        if source.getTitle() != "":
            g.write("1 TITL %s\n" % fmtline(source.getTitle(),248,1))
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
        index = index + 1
        sbar.set_value((100*index)/nump)
        while(events_pending()):
            mainiteration()
    sbar.set_value(100.0)
            
        
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
        return ged_subdate(date.start)

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
    global private
    global cnvtxt
    
    restrict = topDialog.get_widget("restrict").get_active()
    private = topDialog.get_widget("private").get_active()
    filter_obj = topDialog.get_widget("filter").get_menu().get_active()
    filter = filter_obj.get_data("filter")

    if topDialog.get_widget("ansel").get_active():
        cnvtxt = latin_to_ansel
    else:
        cnvtxt = latin_to_utf8

    name = topDialog.get_widget("filename").get_text()
    filter()
    
    utils.destroy_passed_object(obj)

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "gedcomexport.glade"
    progress = GladeXML(glade_file,"exportprogress")
    progress.signal_autoconnect({"on_close_clicked":utils.destroy_passed_object})
    fbar = progress.get_widget("fbar")
    pbar = progress.get_widget("pbar")
    sbar = progress.get_widget("sbar")
    closebtn = progress.get_widget("close")
    closebtn.connect("clicked",utils.destroy_passed_object)
    closebtn.set_sensitive(0)
    exportData(db,name,progress.get_widget('exportprogress'),pbar,fbar,sbar)
    closebtn.set_sensitive(1)
    
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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to GEDCOM"))
