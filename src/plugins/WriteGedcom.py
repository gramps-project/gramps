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
import GenericFilter
import os
import string
import time
import const
import Utils
import intl
import Date
import re

_ = intl.gettext

import gtk
import gnome.ui
import libglade

from GedcomInfo import *
try:
    from ansel import latin_to_ansel
except:
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
    Date.HEBREW : (_hmonth, '@#DHEBREW@'),
    Date.FRENCH : (_fmonth, '@#DFRENCH R@'),
    Date.JULIAN : (_month, '@#DJULIAN@'),
    }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

get_int = re.compile('([0-9]+)')

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
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1
    for attr in family.getAttributeList():
        if private and attr.getPrivacy():
            continue
        for source_ref in attr.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1

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
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1

    for event in person.getAddressList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1

    for event in person.getAttributeList():
        if private and event.getPrivacy():
            continue
        for source_ref in event.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1

    for name in person.getAlternateNames() + [person.getPrimaryName()]:
        if private and name.getPrivacy():
            continue
        for source_ref in name.getSourceRefList():
            sbase = source_ref.getBase()
            if sbase != None and not slist.has_key(sbase.getId()):
                slist[sbase.getId()] = 1

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
    try:
        GedcomWriter(database,person)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

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
        self.plist = {}
        self.slist = {}
        self.flist = {}
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
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked
            })
        
        filter_obj = self.topDialog.get_widget("filter")

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % person.getPrimaryName().getName())
        des.add_rule(GenericFilter.IsDescendantOf([person.getId()]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % person.getPrimaryName().getName())
        ans.add_rule(GenericFilter.IsAncestorOf([person.getId()]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") %
                     person.getPrimaryName().getName())
        com.add_rule(GenericFilter.HasCommonAncestorWith([person.getId()]))

        self.filter_menu = GenericFilter.build_filter_menu([all,des,ans,com])
        filter_obj.set_menu(self.filter_menu)

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

        dpath = os.path.dirname(db.getSavePath())
        pathname = "%s.ged" % dpath
        
        self.topDialog.get_widget('fileentry1').set_default_path(dpath)
        filetgt = self.topDialog.get_widget('filename')
        filetgt.set_text(pathname)
        
        self.topDialog.get_widget("gedcomExport").show()
        
    def on_ok_clicked(self,obj):
    
        self.restrict = self.topDialog.get_widget("restrict").get_active()
        self.private = self.topDialog.get_widget("private").get_active()

        cfilter = self.filter_menu.get_active().get_data("filter")
        act_tgt = self.target_menu.get_active()

        self.target_ged =  act_tgt.get_data("data")

        self.dest = self.target_ged.get_dest()
        self.adopt = self.target_ged.get_adopt()
        self.conc = self.target_ged.get_conc()
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.source_refs = self.target_ged.get_source_refs()

        if self.topDialog.get_widget("ansel").get_active():
            self.cnvtxt = latin_to_ansel
        else:
            self.cnvtxt = latin_to_utf8

        name = self.topDialog.get_widget("filename").get_text()

        if cfilter == None:
            for p in self.db.getPersonKeys():
                self.plist[p] = 1
        else:
            for p in cfilter.apply(self.db,self.db.getPersonMap().values()):
                self.plist[p.getId()] = 1
        
        self.flist = {}
        self.slist = {}
        for key in self.plist.keys():
            p = self.db.getPerson(key)
            add_persons_sources(p,self.slist,self.private)
            for family in p.getFamilyList():
                add_familys_sources(family,self.slist,self.private)
                self.flist[family.getId()] = 1
                
        Utils.destroy_passed_object(obj)

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)

        self.exprogress = libglade.GladeXML(glade_file,"exportprogress")
        self.exprogress.signal_autoconnect({
            "on_close_clicked" : Utils.destroy_passed_object
            })

        self.fbar = self.exprogress.get_widget("fbar")
        self.pbar = self.exprogress.get_widget("pbar")
        self.sbar = self.exprogress.get_widget("sbar")
        self.progress = self.exprogress.get_widget('exportprogress')

        closebtn = self.exprogress.get_widget("close")
        closebtn.connect("clicked",Utils.destroy_passed_object)
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

        pkeys = self.plist.keys()
        pkeys.sort()
        nump = float(len(self.plist))
        index = 0.0
        for key in pkeys:
            self.write_person(self.db.getPerson(key))
            index = index + 1
            if index%100 == 0:
                self.pbar.set_value((100*index)/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        self.pbar.set_value(100.0)

        self.write_families()
        if self.source_refs:
            self.write_sources()
        else:
            self.sbar.set_value(100.0)

        self.g.write("0 TRLR\n")
        self.g.close()

    def write_families(self):
        nump = float(len(self.flist))
        index = 0.0
        for key in self.flist.keys():
            family = self.db.getFamily(key)
            father_alive = mother_alive = 0
            self.g.write("0 @%s@ FAM\n" % self.fid(family.getId()))
            self.prefn(family)
            person = family.getFather()
            if person != None and self.plist.has_key(person.getId()):
                self.g.write("1 HUSB @%s@\n" % self.pid(person.getId()))
                father_alive = person.probablyAlive()

            person = family.getMother()
            if person != None and self.plist.has_key(person.getId()):
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
                if not self.plist.has_key(person.getId()):
                    continue
                self.g.write("1 CHIL @%s@\n" % self.pid(person.getId()))
                if self.adopt == ADOPT_FTW:
                    if person.getMainParents() == family:
                        self.g.write('2 _FREL Natural\n')
                        self.g.write('2 _MREL Natural\n')
                    else:
                        for f in person.getParentList():
                            if f[0] == family:
                                self.g.write('2 _FREL %s\n' % f[2])
                                self.g.write('2 _MREL %s\n' % f[1])
                                break
                if self.adopt == ADOPT_LEGACY:
                    for f in person.getAltParentList():
                        if f[0] == family:
                            self.g.write('2 _STAT %s\n' % f[2])
                            break
                
            index = index + 1
            if index % 100 == 0:
                self.fbar.set_value((100*index)/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        self.fbar.set_value(100.0)

    def write_sources(self):
        nump = float(len(self.slist))
        index = 0.0
        for key in self.slist.keys():
            source = self.db.getSource(key)
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
                self.write_long_text("NOTE",1,self.cnvtxt(source.getNote()))
            index = index + 1
            if index % 100 == 0:
                self.sbar.set_value((100*index)/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        self.sbar.set_value(100.0)

    def write_person(self,person):
        self.g.write("0 @%s@ INDI\n" % self.pid(person.getId()))
        self.prefn(person)
        self.write_person_name(person.getPrimaryName(),person.getNickName())

        if self.altname == ALT_NAME_STD:
            for name in person.getAlternateNames():
                self.write_person_name(name,"")
    
        if person.getGender() == Person.male:
            self.g.write("1 SEX M\n")
        elif person.getGender() == Person.female:	
            self.g.write("1 SEX F\n")

        ad = 0
        if (self.adopt == ADOPT_STD or self.adopt == ADOPT_EVENT):
            ad = 1
            self.write_adopt_event(person)
            
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

                if val == "ADOP" and ad == 1:
                    continue
                
                if val != "" :
                    self.g.write("1 %s %s\n" % (self.cnvtxt(val),\
                                                self.cnvtxt(event.getDescription())))
                else:
                    self.g.write("1 EVEN %s\n" % self.cnvtxt(event.getDescription()))
                    self.g.write("2 TYPE %s\n" % self.cnvtxt(event.getName()))

                self.dump_event_stats(event)

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
                    self.write_long_text("NOTE",2,self.cnvtxt(attr.getNote()))
                for srcref in attr.getSourceRefList():
                    self.write_source_ref(2,srcref)

            for addr in person.getAddressList():
                if self.private and addr.getPrivacy():
                    continue
                self.g.write("1 RESI\n")
                self.print_date("2 DATE",addr.getDateObj())
                if self.resi == 0:
                    self.write_long_text("ADDR",2,self.cnvtxt(addr.getStreet()))
                    if addr.getCity() != "":
                        self.g.write("3 CITY %s\n" % self.cnvtxt(addr.getCity()))
                    if addr.getState() != "":
                        self.g.write("3 STAE %s\n" % self.cnvtxt(addr.getState()))
                    if addr.getPostal() != "":
                        self.g.write("3 POST %s\n" % self.cnvtxt(addr.getPostal()))
                    if addr.getCountry() != "":
                        self.g.write("3 CTRY %s\n" % self.cnvtxt(addr.getCountry()))
                else:
                    text = addr.getStreet()
                    text = addr_append(text,addr.getCity())
                    text = addr_append(text,addr.getState())
                    text = addr_append(text,addr.getPostal())
                    text = addr_append(text,addr.getCountry())
                    if text:
                        self.g.write("2 PLAC %s\n" % text)
                if addr.getNote() != "":
                    self.write_long_text("NOTE",3,self.cnvtxt(addr.getNote()))
                for srcref in addr.getSourceRefList():
                    self.write_source_ref(3,srcref)

        for family in person.getParentList():
            if self.flist.has_key(family[0].getId()):
                self.g.write("1 FAMC @%s@\n" % self.fid(family[0].getId()))
                if self.adopt == ADOPT_PEDI or self.adopt == ADOPT_STD:
                    if string.lower(family[1]) == "adopted":
                        self.g.write("2 PEDI Adopted\n")
        
        for family in person.getFamilyList():
            if family != None and self.flist.has_key(family.getId()):
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
            self.write_long_text("NOTE",1,self.cnvtxt(person.getNote()))
			
    def write_adopt_event(self,person):
        fam = None
        for f in person.getParentList():
            mrel = string.lower(f[1])
            frel = string.lower(f[2])
            if mrel=="adopted" or frel=="adopted":
                fam = f[0]
                break
        if fam:
            self.g.write('1 ADOP\n')
            self.g.write('2 FAMC @%s@\n' % self.fid(fam.getId()))
            if mrel == frel:
                self.g.write('3 ADOP BOTH\n')
            elif mrel == "adopted":
                self.g.write('3 ADOP WIFE\n')
            else:
                self.g.write('3 ADOP HUSB\n')
        
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
            self.write_long_text("NOTE",2,self.cnvtxt(event.getNote()))
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
            self.g.write("2 STAT %s\n" % self.cnvtxt(statlist[ord.getStatus()]))
        if ord.getNote() != "":
            self.write_long_text("NOTE",index+1,self.cnvtxt(ord.getNote()))
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
                    val = make_date(start,mlist)
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
            self.write_long_text("NOTE",2,self.cnvtxt(name.getNote()))
        for srcref in name.getSourceRefList():
            self.write_source_ref(2,srcref)

    def write_source_ref(self,level,ref):
        if ref.getBase() == None:
            return
        if self.source_refs:
            self.g.write("%d SOUR @%s@\n" %
                         (level,self.sid(ref.getBase().getId())))
            if ref.getPage() != "":
                self.g.write("%d PAGE %s\n" % (level+1,ref.getPage()))

            ref_text = ref.getText()
            if ref_text != "" or not ref.getDate().isEmpty():
                self.g.write('%d DATA\n' % (level+1))
                if ref_text != "":
                    self.write_long_text("TEXT",level+2,self.cnvtxt(ref_text))
                pfx = "%d DATE" % (level+2)
                self.print_date(pfx,ref.getDate())
        else:
            # We put title, page, and date on the SOUR line.
            # Not using CONC because GeneWeb does not support this.
            # TEXT and NOTE will be ignored by GeneWeb, but we can't
            # output paragaphs in SOUR if we don't use CONC.
            sbase = ref.getBase()
            if sbase and sbase.getTitle():
                txt = sbase.getTitle() + ".  "
            else:
                txt = ""
            if ref.getPage():
                txt = txt + ref.getPage() + ".  "
            self.g.write("%d SOUR %s" % (level,self.cnvtxt(txt)))
            if not ref.getDate().isEmpty():
                self.print_date("", ref.getDate())
            else:
                self.g.write("\n")
            if ref.getText():
                self.write_long_text("TEXT",level+1,self.cnvtxt(ref_text))
        if ref.getComments() != "":
            self.write_long_text("NOTE",level+1,self.cnvtxt(ref.getComments()))

    def fid(self,id):
        return id

    def prefn(self,person):
        match = get_int.search(person.getId())
        if match:
            self.g.write('1 REFN %d\n' % int(match.groups()[0]))

    def frefn(self,family):
        match = get_int.search(family.getId())
        if match:
            self.g.write('1 REFN %d\n' % int(match.groups()[0]))
    
    def pid(self,id):
        return id

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
