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
import Date
_ = intl.gettext

import gtk
import gnome.ui
import libglade

from GedcomInfo import *
from latin_ansel import latin_to_ansel
from latin_utf8  import latin_to_utf8

#-------------------------------------------------------------------------
#
# Calendar month names
#
#-------------------------------------------------------------------------

_hmonth = [
    "", "ELUL", "TSH", "CSH", "KSL", "TVT", "SHV", "ADR",
    "ADS", "NSN", "IYR", "SVN", "TMZ", "AAV", "ELL" ]

_fmonth = [
    "",     "VEND", "BRUM", "FRIM", "NIVO", "PLUV", "VENT",
    "GERM", "FLOR", "PRAI", "MESS", "THER", "FRUC", "COMP"]

_month = [
    "",    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]

_calmap = {
    Date.HEBREW : (_hmonth, '@#HEBREW@'),
    Date.FRENCH : (_fmonth, '@#FRENCH R@'),
    Date.JULIAN : (_month, '@#JULIAN@'),
    }


#-------------------------------------------------------------------------
#
# Filters
#
#-------------------------------------------------------------------------
def entire_database(database,person,private):
    plist = database.getPersonMap().values()
    flist = database.getFamilyMap().values()
    slist = database.getSourceMap().values()
    return (plist,flist,slist)

def active_person_descendants(database,person,private):
    plist = []
    flist = []
    slist = []
    descend(person,plist,flist,slist,private)
    return (plist,flist,slist)
    
def active_person_ancestors_and_descendants(database,person,private):
    plist = []
    flist = []
    slist = []
    descend(person,plist,flist,slist,private)
    ancestors(person,plist,flist,slist,private)
    return (plist,flist,slist)

def active_person_ancestors(database,person,private):
    plist = []
    flist = []
    slist = []
    ancestors(person,plist,flist,slist,private)
    return (plist,flist,slist)

def interconnected(database,person,private):
    plist = []
    flist = []
    slist = []
    walk(person,plist,flist,slist,private)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def descend(person,plist,flist,slist,private):
    if person == None or person in plist:
        return
    plist.append(person)
    add_persons_sources(person,slist,private)
    for family in person.getFamilyList():
        add_familys_sources(family,slist,private)
        flist.append(family)
        father = family.getFather()
        mother = family.getMother()
        if father != None and father not in plist:
            plist.append(father)
            add_persons_sources(father,slist,private)
        if mother != None and mother not in plist:
            plist.append(mother)
            add_persons_sources(mother,slist,private)
        for child in family.getChildList():
            descend(child,plist,flist,slist,private)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ancestors(person,plist,flist,slist,private):
    if person == None or person in plist:
        return
    plist.append(person)
    add_persons_sources(person,slist,private)
    family = person.getMainFamily()
    if family == None or family in flist:
        return
    add_familys_sources(family,slist,private)
    flist.append(family)
    ancestors(family.getMother(),plist,flist,slist,private)
    ancestors(family.getFather(),plist,flist,slist,private)
    

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def walk(person,plist,flist,slist,private):
    if person == None or person in plist:
        return
    plist.append(person)
    add_persons_sources(person,slist,private)
    families = person.getFamilyList()
    families.append(person.getMainFamily())
    for f in person.getAltFamilyList():
        families.append(f[0])
    for family in families:
        if family == None or family in flist:
            continue
        add_familys_sources(family,slist,private)
        flist.append(family)
        walk(family.getFather(),plist,flist,slist,private)
        walk(family.getMother(),plist,flist,slist,private)
        for child in family.getChildList():
            walk(child,plist,flist,slist,private)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_familys_sources(family,slist,private):
    for event in family.getEventList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)
    for attr in family.getAttributeList():
        if private and attr.getPrivacy():
            continue
        for source_ref in attr.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_persons_sources(person,slist,private):
    elist = person.getEventList()[:]

    elist.append(person.getBirth())
    elist.append(person.getDeath())
    for event in elist:
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)
    for event in person.getAddressList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)
    for event in person.getAttibuteList:
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)
    for name in person.getNameList + [person.getPrimaryName()]:
        if private and name.getPrivacy():
            continue
        for source_ref in name.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and sbase not in slist:
                slist.append(sbase)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def addr_append(text,data):
    if data:
        return "%s, %s" % (text,data)
    else:
        return text
    
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
def make_date(subdate,mmap):
    retval = ""
    day = subdate.getDay()
    mon = subdate.getMonth()
    year = subdate.getYear()
    mode = subdate.getModeVal()
    day_valid = subdate.getDayValid()
    mon_valid = subdate.getMonthValid()
    year_valid = subdate.getYearValid()

    if not day_valid:
        try:
            if not mon_valid:
                retval = str(year)
            elif not year_valid:
                retval = mmap[mon]
            else:
                retval = "%s %d" % (mmap[mon],year)
        except IndexError:
            print "Month index error - %d" % mon
            retval = str(year)
    elif not mon_valid:
        retval = str(year)
    else:
        try:
            month = mmap[mon]
            if not year_valid:
                retval = "%d %s ????" % (day,month)
            else:
                retval = "%d %s %d" % (day,month,year)
        except IndexError:
            print "Month index error - %d" % mon
            retval = str(year)
    if mode == Date.SingleDate.about:
        retval = "ABT %s"  % retval
    elif mode == Date.SingleDate.before:
        retval = "BEF %s" % retval
    elif mode == Date.SingleDate.after:
        retval = "AFT %s" % retval
    return retval
        
def fmtline(text,limit,level):
    new_text = []
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
        
    if not date.getValid():
        return ""
    elif not date.getDayValid():
        try:
            if not date.getMonthValid():
                retval = str(date.year)
            elif not date.getYearValid():
                retval = "(%s)" % Date.SingleDate.emname[date.month]
            else:	
                retval = "%s %d" % (Date.SingleDate.emname[date.month],date.year)
        except IndexError:
            print "Month index error - %d" % date.month
            retval = str(date.year)
    elif not date.getMonthValid():
        retval = str(date.year)
    else:
        try:
            month = Date.SingleDate.emname[date.month]
            if not date.getYearValid():
                retval = "(%d %s)" % (date.day,month)
            else:
                retval = "%d %s %d" % (date.day,month,date.year)
        except IndexError:
            print "Month index error - %d" % date.month
            retval = str(date.year)

    if date.mode == Date.SingleDate.about:
        retval = "ABT %s"  % retval

    if date.mode == Date.SingleDate.before:
        retval = "BEF %s" % retval
    elif date.mode == Date.SingleDate.after:
        retval = "AFT %s" % retval

    return retval
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def writeData(database,person):
    GedcomWriter(database,person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GedcomWriter:
    """Writes a GEDCOM file from the passed database"""
    
    def __init__(self,db,person):
        self.db = db
        self.person = person
        self.restrict = 1
        self.private = 1
        self.cnvtxt = latin_to_ansel
        self.plist = []
        self.slist = []
        self.flist = []
        self.adopt = ADOPT_EVENT
        self.fidval = 0
        self.fidmap = {}
        self.pidval = 0
        self.pidmap = {}
        self.sidval = 0
        self.sidmap = {}

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)
        
        self.topDialog = libglade.GladeXML(glade_file,"gedcomExport")
        self.topDialog.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked
            })
        
        filter_obj = self.topDialog.get_widget("filter")
        myMenu = gtk.GtkMenu()
        menuitem = gtk.GtkMenuItem(_("Entire Database"))
        myMenu.append(menuitem)
        menuitem.set_data("filter",entire_database)
        menuitem.show()
        name = person.getPrimaryName().getRegularName()
        menuitem = gtk.GtkMenuItem(_("Ancestors of %s") % name)
        myMenu.append(menuitem)
        menuitem.set_data("filter",active_person_ancestors)
        menuitem.show()
        menuitem = gtk.GtkMenuItem(_("Descendants of %s") % name)
        myMenu.append(menuitem)
        menuitem.set_data("filter",active_person_descendants)
        menuitem.show()
        menuitem = gtk.GtkMenuItem(_("Ancestors and Descendants of %s") % name)
        myMenu.append(menuitem)
        menuitem.set_data("filter",active_person_ancestors_and_descendants)
        menuitem.show()
        menuitem = gtk.GtkMenuItem(_("People somehow connected to %s") % name)
        myMenu.append(menuitem)
        menuitem.set_data("filter",interconnected)
        menuitem.show()
        filter_obj.set_menu(myMenu)
        self.filter_menu = myMenu

        gedmap = GedcomInfoDB()
        
        target_obj = self.topDialog.get_widget("target")
        myMenu = gtk.GtkMenu()
        for name in gedmap.get_name_list():
            menuitem = gtk.GtkMenuItem(name)
            myMenu.append(menuitem)
            data = gedmap.get_description(name)
            menuitem.set_data("data",data)
            menuitem.show()

        target_obj.set_menu(myMenu)
        self.target_menu = myMenu
        
        self.topDialog.get_widget("gedcomExport").show()
        
    def on_ok_clicked(self,obj):
    
        self.restrict = self.topDialog.get_widget("restrict").get_active()
        self.private = self.topDialog.get_widget("private").get_active()

        filter = self.filter_menu.get_active().get_data("filter")
        act_tgt = self.target_menu.get_active()

        self.target_ged =  act_tgt.get_data("data")

        self.dest = self.target_ged.get_dest()
        self.adopt = self.target_ged.get_adopt()
        self.conc = self.target_ged.get_conc()
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()


        if self.topDialog.get_widget("ansel").get_active():
            self.cnvtxt = latin_to_ansel
        else:
            self.cnvtxt = latin_to_utf8

        name = self.topDialog.get_widget("filename").get_text()

        (self.plist,self.flist,self.slist) = filter(self.db,self.person,self.private)
    
        utils.destroy_passed_object(obj)

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)

        self.exprogress = libglade.GladeXML(glade_file,"exportprogress")
        self.exprogress.signal_autoconnect({
            "on_close_clicked" : utils.destroy_passed_object
            })

        self.fbar = self.exprogress.get_widget("fbar")
        self.pbar = self.exprogress.get_widget("pbar")
        self.sbar = self.exprogress.get_widget("sbar")
        self.progress = self.exprogress.get_widget('exportprogress')

        closebtn = self.exprogress.get_widget("close")
        closebtn.connect("clicked",utils.destroy_passed_object)
        closebtn.set_sensitive(0)

        self.export_data(name)

        closebtn.set_sensitive(1)

    def export_data(self,filename):
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg = "%s\n%s" % (_("Could not create %s") % filename,str(msg))
            gnome.ui.GnomeErrorDialog(msg)
            self.progress.destroy()
            return
        except:
            gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename)
            self.progress.destroy()
            return

        date = string.split(time.ctime(time.time()))
        
        self.g.write("0 HEAD\n")
        self.g.write("1 SOUR GRAMPS\n")
        self.g.write("2 VERS " + const.version + "\n")
        self.g.write("2 NAME Gramps\n")
        if self.dest:
            self.g.write("1 DEST %s\n" % self.dest)
        self.g.write("1 DATE %s %s %s\n" % (date[2],string.upper(date[1]),date[4]))
        if self.cnvtxt == latin_to_ansel:
            self.g.write("1 CHAR ANSEL\n");
        else:
            self.g.write("1 CHAR UTF-8\n");
        self.g.write("1 SUBM @SUBM@\n")
        self.g.write("1 FILE %s\n" % filename)
        self.g.write("1 GEDC\n")
        self.g.write("2 VERS 5.5\n")
        self.g.write('2 FORM LINEAGE-LINKED\n')
        self.g.write("0 @SUBM@ SUBM\n")
        owner = self.db.getResearcher()
        if owner.getName() != "":
            self.g.write("1 NAME " + self.cnvtxt(owner.getName()) +"\n")
        else:
            self.g.write('1 NAME Not Provided\n')

        if owner.getAddress() != "":
            cnt = 0
            self.g.write("1 ADDR " + self.cnvtxt(owner.getAddress()) + "\n")
            if owner.getCity() != "":
                self.g.write("2 CONT " + self.cnvtxt(owner.getCity()) + "\n")
                cnt = 1
            if owner.getState() != "":
                self.g.write("2 CONT " + self.cnvtxt(owner.getState()) + "\n")
                cnt = 1
            if owner.getPostalCode() != "":
                self.g.write("2 CONT " + self.cnvtxt(owner.getPostalCode()) + "\n")
                cnt = 1
            if owner.getCountry() != "":
                self.g.write("2 CONT " + self.cnvtxt(owner.getCountry()) + "\n")
                cnt = 1
            if owner.getPhone() != "":
                self.g.write("2 PHON " + self.cnvtxt(owner.getPhone()) + "\n")
                cnt = 1
            if cnt == 0:
                self.g.write('2 CONT Not Provided\n')
        else:
            self.g.write('1 ADDR Not Provided\n')
            self.g.write('2 CONT Not Provided\n')

        self.plist.sort(sortById)
        nump = float(len(self.plist))
        index = 0.0
        for person in self.plist:
            self.write_person(person)
            index = index + 1
            self.pbar.set_value((100*index)/nump)
            while(gtk.events_pending()):
                gtk.mainiteration()
        self.pbar.set_value(100.0)

        self.write_families()
        self.write_sources()
        
        self.g.write("0 TRLR\n")
        self.g.close()

    def write_families(self):
        nump = float(len(self.flist))
        index = 0.0
        for family in self.flist:
            father_alive = mother_alive = 0
            self.g.write("0 @%s@ FAM\n" % self.fid(family.getId()))
            person = family.getFather()
            if person != None:
                self.g.write("1 HUSB @%s@\n" % self.pid(person.getId()))
                father_alive = person.probablyAlive()

            person = family.getMother()
            if person != None:
                self.g.write("1 WIFE @%s@\n" % self.pid(person.getId()))
                mother_alive = person.probablyAlive()

            if not self.restrict or ( not father_alive and not mother_alive ):
                self.write_ord("SLGS",family.getLdsSeal(),1,const.lds_ssealing)

                for event in family.getEventList():
                    if self.private and event.getPrivacy():
                        continue
                    name = event.getName()
                    val = ""
                    if const.familyConstantEvents.has_key(name):
                        val = const.familyConstantEvents[name]
                    if val == "":
                        val = self.target_ged.gramps2tag(name)
                        
                    if val != "":
                        self.g.write("1 %s %s\n" % (self.cnvtxt(val),
                                                 self.cnvtxt(event.getDescription())))
                    else:	
                        self.g.write("1 EVEN %s\n" % self.cnvtxt(event.getDescription()))
                        self.g.write("2 TYPE %s\n" % self.cnvtxt(name))
					
                    self.dump_event_stats(event)

            for person in family.getChildList():
                self.g.write("1 CHIL @%s@\n" % self.pid(person.getId()))
                if self.adopt == ADOPT_FTW:
                    if person.getMainFamily() == family:
                        self.g.write('2 _FREL Natural\n')
                        self.g.write('2 _MREL Natural\n')
                    else:
                        for f in person.getAltFamilyList():
                            if f[0] == family:
                                self.g.write('2 _FREL %s\n' % f[2])
                                self.g.write('2 _MREL %s\n' % f[1])
                                break
                if self.adopt == ADOPT_LEGACY:
                    for f in person.getAltFamilyList():
                        if f[0] == family:
                            self.g.write('2 _STAT %s\n' % f[2])
                            break
                
            index = index + 1
            self.fbar.set_value((100*index)/nump)
            while(gtk.events_pending()):
                gtk.mainiteration()
        self.fbar.set_value(100.0)

    def write_sources(self):
        nump = float(len(self.slist))
        index = 0.0
        for source in self.slist:
            self.g.write("0 @%s@ SOUR\n" % self.sid(source.getId()))
            if source.getTitle() != "":
                self.g.write("1 TITL %s\n" % fmtline(self.cnvtxt(source.getTitle()),248,1))
            if source.getAuthor() != "":
                self.g.write("1 AUTH %s\n" % self.cnvtxt(source.getAuthor()))
            if source.getPubInfo() != "":
                self.g.write("1 PUBL %s\n" % self.cnvtxt(source.getPubInfo()))
            if source.getTitle() != "":
                self.g.write("1 ABBR %s\n" % self.cnvtxt(source.getTitle()))
            if source.getCallNumber() != "":
                self.g.write("1 CALN %s\n" % self.cnvtxt(source.getCallNumber()))
            if source.getNote() != "":
                self.write_long_text("NOTE",1,source.getNote())
            index = index + 1
            self.sbar.set_value((100*index)/nump)
            while(gtk.events_pending()):
                gtk.mainiteration()
        self.sbar.set_value(100.0)

    def write_person(self,person):
        self.g.write("0 @%s@ INDI\n" % self.pid(person.getId()))

        self.write_person_name(person.getPrimaryName(),person.getNickName())

        if self.altname == ALT_NAME_STD:
            for name in person.getAlternateNames():
                self.write_person_name(name,"")
    
        if person.getGender() == Person.male:
            self.g.write("1 SEX M\n")
        elif person.getGender() == Person.female:	
            self.g.write("1 SEX F\n")

        if not self.restrict or not person.probablyAlive():

            birth = person.getBirth()
            if not (self.private and birth.getPrivacy()):
                if not birth.getDateObj().isEmpty() or birth.getPlaceName() != "":
                    self.g.write("1 BIRT\n")
                    self.dump_event_stats(birth)
				
            death = person.getDeath()
            if not (self.private and death.getPrivacy()):
                if not death.getDateObj().isEmpty() or death.getPlaceName() != "":
                    self.g.write("1 DEAT\n")
                    self.dump_event_stats(death)

            uid = person.getPafUid()
            if uid != "":
                self.g.write("1 _UID %s\n" % uid)
            
            ad = 0

            self.write_ord("BAPL",person.getLdsBaptism(),1,const.lds_baptism)
            self.write_ord("ENDL",person.getLdsEndowment(),1,const.lds_baptism)
            self.write_ord("SLGC",person.getLdsSeal(),1,const.lds_csealing)
            
            for event in person.getEventList():
                if self.private and event.getPrivacy():
                    continue
                name = event.getName()
                val = ""
                if const.personalConstantEvents.has_key(name):
                    val = const.personalConstantEvents[name]
                if val == "":
                    val = self.target_ged.gramps2tag(name)
                    
                if self.adopt == ADOPT_EVENT and val == "ADOP":
                    ad = 1
                    self.g.write('1 ADOP\n')
                    fam = None
                    for f in person.getAltFamilyList():
                        mrel = string.lower(f[1])
                        frel = string.lower(f[2])
                        if mrel=="adopted" or mrel=="adopted":
                            fam = f[0]
                            break
                    if fam:
                        self.g.write('2 FAMC @%s@\n' % self.fid(fam.getId()))
                        if mrel == frel:
                            self.g.write('3 ADOP BOTH\n')
                        elif mrel == "adopted":
                            self.g.write('3 ADOP WIFE\n')
                        else:
                            self.g.write('3 ADOP HUSB\n')
                elif val != "" :
                    self.g.write("1 %s %s\n" % (self.cnvtxt(val),\
                                                self.cnvtxt(event.getDescription())))
                else:
                    self.g.write("1 EVEN %s\n" % self.cnvtxt(event.getDescription()))
                    self.g.write("2 TYPE %s\n" % self.cnvtxt(event.getName()))

                self.dump_event_stats(event)

            if self.adopt == ADOPT_EVENT and ad == 0 and len(person.getAltFamilyList()) != 0:
                self.g.write('1 ADOP\n')
                fam = None
                for f in person.getAltFamilyList():
                    mrel = string.lower(f[1])
                    frel = string.lower(f[2])
                    if mrel=="adopted" or mrel=="adopted":
                        fam = f[0]
                        break
                if fam:
                    self.g.write('2 FAMC @%s@\n' % self.fid(fam.getId()))
                    if mrel == frel:
                        self.g.write('3 ADOP BOTH\n')
                    elif mrel == "adopted":
                        self.g.write('3 ADOP WIFE\n')
                    else:
                        self.g.write('3 ADOP HUSB\n')

            for attr in person.getAttributeList():
                if self.private and attr.getPrivacy():
                    continue
                name = attr.getType()
                if const.personalConstantAttributes.has_key(name):
                    val = const.personalConstantAttributes[name]
                else:
                    val = ""
                if val != "" : 
                    self.g.write("1 %s\n" % val)
                else:
                    self.g.write("1 EVEN\n")
                    self.g.write("2 TYPE %s\n" % self.cnvtxt(name))
                self.g.write("2 PLAC %s\n" % self.cnvtxt(attr.getValue()))
                if attr.getNote() != "":
                    self.write_long_text("NOTE",2,attr.getNote())
                for srcref in attr.getSourceRefList():
                    self.write_source_ref(2,srcref)

            for addr in person.getAddressList():
                if self.private and addr.getPrivacy():
                    continue
                self.g.write("1 RESI\n")
                self.print_date("2 DATE",addr.getDateObj())
                if self.resi == 0:
                    self.write_long_text("ADDR",2,addr.getStreet())
                    if addr.getCity() != "":
                        self.g.write("3 CITY %s\n" % addr.getCity())
                    if addr.getState() != "":
                        self.g.write("3 STAE %s\n" % addr.getState())
                    if addr.getPostal() != "":
                        self.g.write("3 POST %s\n" % addr.getPostal())
                    if addr.getCountry() != "":
                        self.g.write("3 CTRY %s\n" % addr.getCountry())
                else:
                    text = addr.getStreet()
                    text = addr_append(text,addr.getCity())
                    text = addr_append(text,addr.getState())
                    text = addr_append(text,addr.getPostal())
                    text = addr_append(text,addr.getCountry())
                    if text:
                        self.g.write("2 PLAC %s\n" % text)
                if addr.getNote() != "":
                    self.write_long_text("NOTE",3,addr.getNote())
                for srcref in addr.getSourceRefList():
                    self.write_source_ref(3,srcref)

        family = person.getMainFamily()
        if family != None and family in self.flist:
            self.g.write("1 FAMC @%s@\n" % self.fid(family.getId()))

        for family in person.getAltFamilyList():
            self.g.write("1 FAMC @%s@\n" % self.fid(family[0].getId()))
            if self.adopt == ADOPT_PEDI:
                if string.lower(family[1]) == "adopted":
                    self.g.write("2 PEDI Adopted\n")
        
        for family in person.getFamilyList():
            if family != None and family in self.flist:
                self.g.write("1 FAMS @%s@\n" % self.fid(family.getId()))

        if self.obje:
            for url in person.getUrlList():
                self.g.write('1 OBJE\n')
                self.g.write('2 FORM URL\n')
                if url.get_description() != "":
                    self.g.write('2 TITL %s\n' % url.get_description())
                if url.get_path() != "":
                    self.g.write('2 FILE %s\n' % url.get_path())

        if person.getNote() != "":
            self.write_long_text("NOTE",1,person.getNote())
			
    def write_long_text(self,tag,level,note):
        if self.conc == CONC_OK:
            self.write_conc_ok(tag,level,note)
        else:
            self.write_conc_broken(tag,level,note)

    def write_conc_ok(self,tag,level,note):
        prefix = "%d %s" % (level,tag)
        textlines = string.split(note,'\n')
        if len(note) == 0:
            self.g.write("%s\n" % prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and line[brkpt] in string.whitespace):
                            brkpt = brkpt+1
                            if ll == brkpt:
                                self.g.write("%s %s\n" % (prefix,line))
                                line = ''
                                break
                        else:
                            self.g.write("%s %s\n" % (prefix,line[0:brkpt+1]))
                            line = line[brkpt+1:]
                    else:
                        self.g.write("%s %s\n" % (prefix,line))
                        line = ""
                    if len(line) > 0:
                        prefix = "%d CONC" % (level+1)
                    else:
                        prefix = "%d CONT" % (level+1)
                    ll = len(line)

    def write_conc_broken(self,tag,level,note):
        prefix = "%d %s" % (level,tag)
        textlines = string.split(note,'\n')
        if len(note) == 0:
            self.g.write("%s\n" % prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and line[brkpt] not in string.whitespace):
                            brkpt = brkpt+1
                            if ll == brkpt:
                                self.g.write("%s %s\n" % (prefix,line))
                                line = ''
                                break
                        else:
                            self.g.write("%s %s\n" % (prefix,line[0:brkpt+1]))
                            line = line[brkpt+1:]
                    else:
                        self.g.write("%s %s\n" % (prefix,line))
                        line = ""
                    if len(line) > 0:
                        prefix = "%d CONC" % (level+1)
                    else:
                        prefix = "%d CONT" % (level+1)
                    ll = len(line)
    
    def dump_event_stats(self,event):
        dateobj = event.getDateObj()
        self.print_date("2 DATE",dateobj)
        if event.getPlaceName() != "":
            self.g.write("2 PLAC %s\n" % self.cnvtxt(event.getPlaceName()))
        if event.getCause() != "":
            self.g.write("2 CAUS %s\n" % self.cnvtxt(event.getCause()))
        if event.getNote() != "":
            self.write_long_text("NOTE",2,event.getNote())
        for srcref in event.getSourceRefList():
            self.write_source_ref(2,srcref)

    def write_ord(self,name,ord,index,statlist):
        if ord == None:
            return
        self.g.write('%d %s\n' % (index,name))
        self.print_date("%d DATE" % (index + 1), ord.getDateObj())
        if ord.getFamily():
            self.g.write('%d FAMC @%s@\n' % (index+1,self.fid(ord.getFamily().getId())))
        if ord.getTemple() != "":
            self.g.write('%d TEMP %s\n' % (index+1,ord.getTemple()))
        if ord.getPlaceName() != "":
            self.g.write("2 PLAC %s\n" % self.cnvtxt(ord.getPlaceName()))
        if ord.getStatus() != 0:
            self.g.write("2 STAT %S\n" % self.cnvtxt(statlist[ord.getStatus()]))
        if ord.getNote() != "":
            self.write_long_text("NOTE",index+1,ord.getNote())
        for srcref in ord.getSourceRefList():
            self.write_source_ref(index+1,srcref)

    def print_date(self,prefix,date):
        start = date.get_start_date()
        if date.isEmpty():
            val = date.getText()
            if val != "":
                self.g.write("%s %s\n" % (prefix,self.cnvtxt(val)))
        elif date.get_calendar() == Date.GREGORIAN:
            if date.isRange():
                val = "FROM %s TO %s" % (make_date(start,_month),
                                         make_date(date.get_stop_date(),_month))
            else:
                val = make_date(start,_month)
            self.g.write("%s %s\n" % (prefix,val))
        else:
            if self.cal == CALENDAR_YES:
                (mlist,cal) = _calmap[date.get_calendar()]
                if date.isRange():
                    stop = date.get_stop_date()
                    val = "FROM %s TO %s" % (make_date(start,mlist),
                                             make_date(stop,mlist))
                else:
                    val = make_date(start,_hmonth)
                self.g.write("%s %s %s\n" % (prefix,cal,val))
            else:
                mydate = Date.Date(date)
                mydate.set_calendar(Date.GREGORIAN)
                start = mydate.get_start_date()
                if mydate.isRange():
                    stop = mydate.get_stop_date()
                    val = "FROM %s TO %s" % (make_date(start,_month),
                                             make_date(stop,_month))
                else:
                    val = make_date(start,_month)
                self.g.write("%s %s\n" % (prefix,val))

    def write_person_name(self,name,nick):
        firstName = self.cnvtxt(name.getFirstName())
        surName = self.cnvtxt(name.getSurname())
        suffix = self.cnvtxt(name.getSuffix())
        title = self.cnvtxt(name.getTitle())
        if suffix == "":
            self.g.write("1 NAME %s /%s/\n" % (firstName,surName))
        else:
            self.g.write("1 NAME %s /%s/, %s\n" % (firstName,surName, suffix))

        if name.getFirstName() != "":
            self.g.write("2 GIVN %s\n" % firstName)
        if name.getSurname() != "":
            self.g.write("2 SURN %s\n" % surName)
        if name.getSuffix() != "":
            self.g.write("2 NSFX %s\n" % suffix)
        if name.getTitle() != "":
            self.g.write("2 NPFX %s\n" % title)
        if nick != "":
            self.g.write('2 NICK %s\n' % nick)
        if name.getNote() != "":
            self.write_long_text("NOTE",2,name.getNote())
        for srcref in name.getSourceRefList():
            self.write_source_ref(2,srcref)

    def write_source_ref(self,level,ref):
        if ref.getBase() == None:
            return
        self.g.write("%d SOUR @%s@\n" % (level,self.sid(ref.getBase().getId())))
        if ref.getPage() != "":
            self.g.write("%d PAGE %s\n" % (level+1,ref.getPage()))

        ref_text = ref.getText()
        if ref_text != "" or not ref.getDate().isEmpty():
            self.g.write('%d DATA\n' % (level+1))
            if ref_text != "":
                self.write_long_text("TEXT",level+2,ref_text)
            pfx = "%d DATE" % (level+2)
            self.print_date(pfx,ref.getDate())
        if ref.getComments() != "":
            self.write_long_text("NOTE",level+1,ref.getComments())
        
    def fid(self,id):
        if self.fidmap.has_key(id):
            return self.fidmap[id]
        else:
            val = "F%05d" % self.fidval
            self.fidval = self.fidval + 1
            self.fidmap[id] = val
            return val

    def pid(self,id):
        if self.pidmap.has_key(id):
            return self.pidmap[id]
        else:
            val = "I%05d" % self.pidval
            self.pidval = self.pidval + 1
            self.pidmap[id] = val
            return val

    def sid(self,id):
        if self.sidmap.has_key(id):
            return self.sidmap[id]
        else:
            val = "S%05d" % self.sidval
            self.sidval = self.sidval + 1
            self.sidmap[id] = val
            return val

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to GEDCOM"))
