#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"Export to GEDCOM"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import string
import time
import re

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import GenericFilter
import const
import Utils
import Date
import Calendar
import Julian
import Hebrew
import FrenchRepublic
import GedcomInfo
import Errors
import ansel_utf8

from gettext import gettext as _
from QuestionDialog import ErrorDialog

_title_string = _("Export to GEDCOM")

def keep_utf8(s):
    return s

def iso8859(s):
    return s.encode('iso-8859-1')

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
    Hebrew.Hebrew.NAME : (_hmonth, '@#HEBREW@'),
    FrenchRepublic.FrenchRepublic.NAME : (_fmonth, '@#FRENCH R@'),
    Julian.Julian.NAME : (_month, '@#JULIAN@'),
    }

_caldef = {
    Calendar.ABOUT : "ABT",
    Calendar.BEFORE : "BEF",
    Calendar.AFTER : "AFT",
    }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_get_int = re.compile('([0-9]+)')

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
def make_date(subdate):
    retval = ""
    day = subdate.getDay()
    mon = subdate.getMonth()
    year = subdate.getYear()
    mode = subdate.getModeVal()
    day_valid = subdate.getDayValid()
    mon_valid = subdate.getMonthValid()
    year_valid = subdate.getYearValid()

    if _calmap.has_key(subdate.calendar.NAME):
        (mmap,prefix) = _calmap[subdate.calendar.NAME]
    else:
        mmap = _month
        prefix = ""

    if not day_valid:
        try:
            if not mon_valid:
                retval = '%d' % year
            elif not year_valid:
                retval = '(%s)' % mmap[mon]
            else:
                retval = "%s %d" % (mmap[mon],year)
        except IndexError:
            print "Month index error - %d" % mon
            retval = '%d' % year
    elif not mon_valid:
        retval = '%d' % year
    else:
        try:
            month = mmap[mon]
            if not year_valid:
                retval = "(%d %s)" % (day,month)
            else:
                retval = "%d %s %d" % (day,month,year)
        except IndexError:
            print "Month index error - %d" % mon
            retval = str(year)

    if prefix:
        retval = "%s %s" % (prefix, retval)
    
    if _caldef.has_key(mode):
        retval = "%s %s"  % (_caldef[mode],retval)

    return retval
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fmtline(text,limit,level,endl):
    new_text = []
    while len(text) > limit:
        new_text.append(text[0:limit-1])
        text = text[limit:]
    if len(text) > 0:
        new_text.append(text)
    app = "%s%d CONC " % (endl,level+1)
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
    
    def __init__(self,db,person,cl=0,name=""):
        self.db = db
        self.person = person
        self.restrict = 1
        self.private = 1
        self.cnvtxt = ansel_utf8.utf8_to_ansel
        self.plist = {}
        self.slist = {}
        self.flist = {}
        self.adopt = GedcomInfo.ADOPT_EVENT
        self.fidval = 0
        self.fidmap = {}
        self.pidval = 0
        self.pidmap = {}
        self.sidval = 0
        self.sidmap = {}
	self.cl = cl
        self.name = name

        if self.cl:
            self.cl_setup()
        else:
            glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)
            
            self.topDialog = gtk.glade.XML(glade_file,"gedcomExport","gramps")
            self.topDialog.signal_autoconnect({
                "destroy_passed_object" : Utils.destroy_passed_object,
                "gnu_free" : self.gnu_free,
                "standard_copyright" : self.standard_copyright,
                "no_copyright" : self.no_copyright,
                "on_restrict_toggled": self.on_restrict_toggled,
                "on_ok_clicked" : self.on_ok_clicked,
                "on_help_clicked" : self.on_help_clicked
                })

            Utils.set_titles(self.topDialog.get_widget('gedcomExport'),
                             self.topDialog.get_widget('title'),
                             _('GEDCOM export'))
        
            filter_obj = self.topDialog.get_widget("filter")
            self.copy = 0

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

            gedmap = GedcomInfo.GedcomInfoDB()
            
            target_obj = self.topDialog.get_widget("target")
            myMenu = gtk.Menu()
            for name in gedmap.get_name_list():
                menuitem = gtk.MenuItem(name)
                myMenu.append(menuitem)
                data = gedmap.get_description(name)
                menuitem.set_data("data",data)
                menuitem.show()

            target_obj.set_menu(myMenu)
            self.target_menu = myMenu

            pathname = os.path.join (os.path.dirname(db.getSavePath()),
                                     "export.ged")
        
            filetgt = self.topDialog.get_widget('fileentry1')
            filetgt.set_filename(pathname)

            self.topDialog.get_widget("gedcomExport").show()

    def gnu_free(self,obj):
        self.copy = 1
        
    def standard_copyright(self,obj):
        self.copy = 0
        
    def no_copyright(self,obj):
        self.copy = 2

    def on_restrict_toggled(self,restrict):
        active = restrict.get_active ()
        map (lambda x: x.set_sensitive (active),
             [self.topDialog.get_widget("living"),
              self.topDialog.get_widget("notes"),
              self.topDialog.get_widget("sources")])

    def on_ok_clicked(self,obj):
    
        self.restrict = self.topDialog.get_widget("restrict").get_active()
        self.living = (self.restrict and
                       self.topDialog.get_widget("living").get_active())
        self.exclnotes = (self.restrict and
                          self.topDialog.get_widget("notes").get_active())
        self.exclsrcs = (self.restrict and
                         self.topDialog.get_widget("sources").get_active())
        self.private = self.topDialog.get_widget("private").get_active()

        cfilter = self.filter_menu.get_active().get_data("filter")
        act_tgt = self.target_menu.get_active()

        self.target_ged =  act_tgt.get_data("data")
        self.images = self.topDialog.get_widget ("images").get_active ()
        if self.images:
            images_path = self.topDialog.get_widget ("images_path")
            self.images_path = images_path.get_text ()

        self.dest = self.target_ged.get_dest()
        self.adopt = self.target_ged.get_adopt()
        self.conc = self.target_ged.get_conc()
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.prefix = self.target_ged.get_prefix()
        self.source_refs = self.target_ged.get_source_refs()
        
        if self.topDialog.get_widget("ansel").get_active():
            self.cnvtxt = ansel_utf8.utf8_to_ansel
        elif self.topDialog.get_widget("ansi").get_active():
            self.cnvtxt = iso8859
        else:
            self.cnvtxt = keep_utf8

        self.nl = self.cnvtxt(self.target_ged.get_endl())
        name = self.topDialog.get_widget("filename").get_text()

        if cfilter == None:
            for p in self.db.getPersonKeys():
                self.plist[p] = 1
        else:
            try:
                for p in cfilter.apply(self.db, self.db.getPersonMap().values()):
                    self.plist[p.getId()] = 1
            except Errors.FilterError, msg:
                (m1,m2) = msg.messages()
                ErrorDialog(m1,m2)
                return
            
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

        self.exprogress = gtk.glade.XML(glade_file,"exportprogress","gramps")
        self.exprogress.signal_autoconnect({
            "on_close_clicked" : Utils.destroy_passed_object
            })

        Utils.set_titles(self.exprogress.get_widget('exportprogress'),
                         self.exprogress.get_widget('title'),
                         _('GEDCOM export'))

        self.fbar = self.exprogress.get_widget("fbar")
        self.pbar = self.exprogress.get_widget("pbar")
        self.sbar = self.exprogress.get_widget("sbar")
        self.progress = self.exprogress.get_widget('exportprogress')

        closebtn = self.exprogress.get_widget("close")
        closebtn.connect("clicked",Utils.destroy_passed_object)
        closebtn.set_sensitive(0)

        self.export_data(name)
        closebtn.set_sensitive(1)

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','export-data')

    def cl_setup(self):
        self.restrict = 0
        self.private = 0
        self.copy = 0

        for p in self.db.getPersonKeys():
            self.plist[p] = 1

        gedmap = GedcomInfo.GedcomInfoDB()
        self.target_ged = gedmap.standard

        self.dest = self.target_ged.get_dest()
        self.adopt = self.target_ged.get_adopt()
        self.conc = self.target_ged.get_conc()
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.prefix = self.target_ged.get_prefix()
        self.source_refs = self.target_ged.get_source_refs()
        
        self.cnvtxt = keep_utf8
        self.nl = self.cnvtxt(self.target_ged.get_endl())
        
        self.flist = {}
        self.slist = {}

        for key in self.plist.keys():
            p = self.db.getPerson(key)
            add_persons_sources(p,self.slist,self.private)
            for family in p.getFamilyList():
                add_familys_sources(family,self.slist,self.private)
                self.flist[family.getId()] = 1

        self.export_data(self.name)

    def writeln(self,text):
        self.g.write('%s%s' % (text,self.nl))
        
    def export_data(self,filename):
        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % filename
            ErrorDialog(msg2,str(msg))
            self.progress.destroy()
            return
        except:
            ErrorDialog(_("Could not create %s") % filename)
            self.progress.destroy()
            return

        date = string.split(time.ctime(time.time()))

        self.writeln("0 HEAD")
        self.writeln("1 SOUR GRAMPS")
        self.writeln("2 VERS %s" % const.version)
        self.writeln("2 NAME GRAMPS")
        if self.dest:
            self.writeln("1 DEST %s" % self.dest)
        self.writeln("1 DATE %s %s %s" % (date[2],string.upper(date[1]),date[4]))
        if self.cnvtxt == ansel_utf8.utf8_to_ansel:
            self.writeln("1 CHAR ANSEL")
        elif self.cnvtxt == iso8859:
            self.writeln("1 CHAR ANSI")
        else:
            self.writeln("1 CHAR UTF-8")
        self.writeln("1 SUBM @SUBM@")
        self.writeln("1 FILE %s" % filename)
        self.write_copy()
        self.writeln("1 GEDC")
        self.writeln("2 VERS 5.5")
        self.writeln('2 FORM LINEAGE-LINKED')
        self.gnu_fdl()
        self.writeln("0 @SUBM@ SUBM")
        owner = self.db.getResearcher()
        if owner.getName():
            self.writeln("1 NAME %s" % self.cnvtxt(owner.getName()))
        else:
            self.writeln('1 NAME Not Provided')

        if owner.getAddress():
            cnt = 0
            self.writeln("1 ADDR %s" % self.cnvtxt(owner.getAddress()))
            if owner.getCity():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.getCity()))
                cnt = 1
            if owner.getState():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.getState()))
                cnt = 1
            if owner.getPostalCode():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.getPostalCode()))
                cnt = 1
            if owner.getCountry():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.getCountry()))
                cnt = 1
            if owner.getPhone():
                self.writeln("2 PHON %s" % self.cnvtxt(owner.getPhone()))
                cnt = 1
            if cnt == 0:
                self.writeln('2 CONT Not Provided')
        else:
            self.writeln('1 ADDR Not Provided')
            self.writeln('2 CONT Not Provided')

        pkeys = self.plist.keys()
        pkeys.sort()
        nump = float(len(self.plist))
        index = 0.0
        for key in pkeys:
            self.write_person(self.db.getPerson(key))
            index = index + 1
            if index%100 == 0 and not self.cl:
                self.pbar.set_fraction(index/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        if not self.cl:
            self.pbar.set_fraction(1.0)

        self.write_families()
        if self.source_refs:
            self.write_sources()
        else:
            if not self.cl:
                self.sbar.set_fraction(1.0)

        self.writeln("0 TRLR")
        self.g.close()

    def write_copy(self):
        import time

        t = time.localtime(time.time())
        y = t[0]
        
        if self.copy == 0:
            o = self.db.getResearcher().getName()
            self.writeln('1 COPR Copyright (c) %d %s.' % (y,o))
        elif self.copy == 1:
            o = self.db.getResearcher().getName()
            self.writeln('1 COPR Copyright (c) %d %s. See additional copyright NOTE below.' % (y,o))

    def gnu_fdl(self):
        import time

        if self.copy != 1:
            return
        
        t = time.localtime(time.time())
        y = t[0]
        o = self.db.getResearcher().getName()
        
        self.writeln('1 NOTE       Copyright (c) %d %s.' % (y,o))
        try:
            f = open(const.fdl,"r")
            for line in f.readlines():
                self.g.write('2 CONT %s' % line)
            f.close()
        except:
            pass
        
    def write_families(self):
        nump = float(len(self.flist))
        index = 0.0
        for key in self.flist.keys():
            family = self.db.getFamily(key)
            father_alive = mother_alive = 0
            self.writeln("0 @%s@ FAM" % self.fid(family.getId()))
            self.frefn(family)
            person = family.getFather()
            if person != None and self.plist.has_key(person.getId()):
                self.writeln("1 HUSB @%s@" % self.pid(person.getId()))
                father_alive = person.probablyAlive()

            person = family.getMother()
            if person != None and self.plist.has_key(person.getId()):
                self.writeln("1 WIFE @%s@" % self.pid(person.getId()))
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
                        
                    if val:
                        self.writeln("1 %s %s" % (self.cnvtxt(val),
                                                  self.cnvtxt(event.getDescription())))
                    else:	
                        self.writeln("1 EVEN %s" % self.cnvtxt(event.getDescription()))
                        self.writeln("2 TYPE %s" % self.cnvtxt(name))
					
                    self.dump_event_stats(event)

            for person in family.getChildList():
                if not self.plist.has_key(person.getId()):
                    continue
                self.writeln("1 CHIL @%s@" % self.pid(person.getId()))
                if self.adopt == GedcomInfo.ADOPT_FTW:
                    if person.getMainParents() == family:
                        self.writeln('2 _FREL Natural')
                        self.writeln('2 _MREL Natural')
                    else:
                        for f in person.getParentList():
                            if f[0] == family:
                                self.writeln('2 _FREL %s' % f[2])
                                self.writeln('2 _MREL %s' % f[1])
                                break
                if self.adopt == GedcomInfo.ADOPT_LEGACY:
                    for f in person.getAltParentList():
                        if f[0] == family:
                            self.writeln('2 _STAT %s' % f[2])
                            break
                
            index = index + 1
            if index % 100 == 0 and not self.cl:
                self.fbar.set_fraction(index/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        if not self.cl:
            self.fbar.set_fraction(1.0)

    def write_sources(self):
        nump = float(len(self.slist))
        index = 0.0
        for key in self.slist.keys():
            source = self.db.getSource(key)
            self.writeln("0 @%s@ SOUR" % self.sid(source.getId()))
            if source.getTitle():
                self.writeln("1 TITL %s" % fmtline(self.cnvtxt(source.getTitle()),248,1,self.nl))
            if source.getAuthor():
                self.writeln("1 AUTH %s" % self.cnvtxt(source.getAuthor()))
            if source.getPubInfo():
                self.writeln("1 PUBL %s" % self.cnvtxt(source.getPubInfo()))
            if source.getAbbrev():
                self.writeln("1 ABBR %s" % self.cnvtxt(source.getAbbrev()))
            if source.getNote():
                self.write_long_text("NOTE",1,self.cnvtxt(source.getNote()))
            index = index + 1
            if index % 100 == 0 and not self.cl:
                self.sbar.set_fraction(index/nump)
                while(gtk.events_pending()):
                    gtk.mainiteration()
        if not self.cl:
            self.sbar.set_fraction(1.0)

    def write_person(self,person):
        self.writeln("0 @%s@ INDI" % self.pid(person.getId()))
        restricted = self.restrict and person.probablyAlive ()
        self.prefn(person)
        primaryname = person.getPrimaryName ()
        if restricted and self.living:
            primaryname = RelLib.Name (primaryname)
            primaryname.setFirstName ("Living")
            nickname = ""
        else:
            primaryname = person.getPrimaryName ()
            nickname = person.getNickName ()

        if restricted and self.exclnotes:
            primaryname = RelLib.Name (primaryname)
            primaryname.setNote ('')

        if restricted and self.exclsrcs:
            primaryname = RelLib.Name (primaryname)
            primaryname.setSourceRefList ([])

        self.write_person_name(primaryname, nickname)

        if (self.altname == GedcomInfo.ALT_NAME_STD and
            not (restricted and self.living)):
            for name in person.getAlternateNames():
                self.write_person_name(name,"")
    
        if person.getGender() == RelLib.Person.male:
            self.writeln("1 SEX M")
        elif person.getGender() == RelLib.Person.female:	
            self.writeln("1 SEX F")

        if not restricted:

            birth = person.getBirth()
            if not (self.private and birth.getPrivacy()):
                if not birth.getDateObj().isEmpty() or birth.getPlaceName():
                    self.writeln("1 BIRT")
                    self.dump_event_stats(birth)
				
            death = person.getDeath()
            if not (self.private and death.getPrivacy()):
                if not death.getDateObj().isEmpty() or death.getPlaceName():
                    self.writeln("1 DEAT")
                    self.dump_event_stats(death)

            uid = person.getPafUid()
            if uid:
                self.writeln("1 _UID %s" % uid)
            
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
                    
                if self.adopt == GedcomInfo.ADOPT_EVENT and val == "ADOP":
                    ad = 1
                    self.writeln('1 ADOP')
                    fam = None
                    for f in person.getParentList():
                        mrel = string.lower(f[1])
                        frel = string.lower(f[2])
                        if mrel=="adopted" or frel=="adopted":
                            fam = f[0]
                            break
                    if fam:
                        self.writeln('2 FAMC @%s@' % self.fid(fam.getId()))
                        if mrel == frel:
                            self.writeln('3 ADOP BOTH')
                        elif mrel == "adopted":
                            self.writeln('3 ADOP WIFE')
                        else:
                            self.writeln('3 ADOP HUSB')
                elif val :
                    self.writeln("1 %s %s" % (self.cnvtxt(val),\
                                              self.cnvtxt(event.getDescription())))
                else:
                    self.writeln("1 EVEN %s" % self.cnvtxt(event.getDescription()))
                    self.writeln("2 TYPE %s" % self.cnvtxt(event.getName()))

                self.dump_event_stats(event)

            if self.adopt == GedcomInfo.ADOPT_EVENT and ad == 0 and len(person.getParentList()) != 0:
                self.writeln('1 ADOP')
                fam = None
                for f in person.getParentList():
                    mrel = string.lower(f[1])
                    frel = string.lower(f[2])
                    if mrel=="adopted" or frel=="adopted":
                        fam = f[0]
                        break
                if fam:
                    self.writeln('2 FAMC @%s@' % self.fid(fam.getId()))
                    if mrel == frel:
                        self.writeln('3 ADOP BOTH')
                    elif mrel == "adopted":
                        self.writeln('3 ADOP WIFE')
                    else:
                        self.writeln('3 ADOP HUSB')

            for attr in person.getAttributeList():
                if self.private and attr.getPrivacy():
                    continue
                name = attr.getType()
                if const.personalConstantAttributes.has_key(name):
                    val = const.personalConstantAttributes[name]
                else:
                    val = ""
                if val : 
                    self.writeln("1 %s" % val)
                else:
                    self.writeln("1 EVEN")
                    self.writeln("2 TYPE %s" % self.cnvtxt(name))
                self.writeln("2 PLAC %s" % string.replace(self.cnvtxt(attr.getValue()),'\r',' '))
                if attr.getNote():
                    self.write_long_text("NOTE",2,self.cnvtxt(attr.getNote()))
                for srcref in attr.getSourceRefList():
                    self.write_source_ref(2,srcref)

            for addr in person.getAddressList():
                if self.private and addr.getPrivacy():
                    continue
                self.writeln("1 RESI")
                self.print_date("2 DATE",addr.getDateObj())
                if self.resi == 0:
                    self.write_long_text("ADDR",2,self.cnvtxt(addr.getStreet()))
                    if addr.getCity():
                        self.writeln("3 CITY %s" % self.cnvtxt(addr.getCity()))
                    if addr.getState():
                        self.writeln("3 STAE %s" % self.cnvtxt(addr.getState()))
                    if addr.getPostal():
                        self.writeln("3 POST %s" % self.cnvtxt(addr.getPostal()))
                    if addr.getCountry():
                        self.writeln("3 CTRY %s" % self.cnvtxt(addr.getCountry()))
                else:
                    text = addr.getStreet()
                    text = addr_append(text,addr.getCity())
                    text = addr_append(text,addr.getState())
                    text = addr_append(text,addr.getPostal())
                    text = addr_append(text,addr.getCountry())
                    if text:
                        self.writeln("2 PLAC %s" % string.replace(self.cnvtxt(text),'\r',' '))
                if addr.getNote():
                    self.write_long_text("NOTE",2,self.cnvtxt(addr.getNote()))
                for srcref in addr.getSourceRefList():
                    self.write_source_ref(2,srcref)

            if self.images:
                photos = person.getPhotoList ()
            else:
                photos = []

            for photo in photos:
                if photo.ref.getMimeType() == "image/jpeg":
                    self.writeln('1 OBJE')
                    self.writeln('2 FORM jpeg')
                    path = photo.ref.getPath ()
                    dirname = os.path.join (self.dirname, self.images_path)
                    basename = os.path.basename (path)
                    self.writeln('2 FILE %s' % os.path.join(self.images_path,
                                                            basename))
                    try:
                        os.mkdir (dirname)
                    except:
                        pass
                    dest = os.path.join (dirname, basename)
                    try:
                        os.link (path, dest)
                    except OSError, e:
                        file (dest,
                              "wb").writelines (file (path,
                                                      "rb").xreadlines ())

        for family in person.getParentList():
            if self.flist.has_key(family[0].getId()):
                self.writeln("1 FAMC @%s@" % self.fid(family[0].getId()))
                if self.adopt == GedcomInfo.ADOPT_PEDI:
                    if string.lower(family[1]) == "adopted":
                        self.writeln("2 PEDI Adopted")
        
        for family in person.getFamilyList():
            if family != None and self.flist.has_key(family.getId()):
                self.writeln("1 FAMS @%s@" % self.fid(family.getId()))

        if not restricted:
            if self.obje:
                for url in person.getUrlList():
                    self.writeln('1 OBJE')
                    self.writeln('2 FORM URL')
                    if url.get_description():
                        self.writeln('2 TITL %s' % url.get_description())
                    if url.get_path():
                        self.writeln('2 FILE %s' % url.get_path())

        if not restricted or not self.exclnotes:
            if person.getNote():
                self.write_long_text("NOTE",1,self.cnvtxt(person.getNote()))

    def write_long_text(self,tag,level,note):
        if self.conc == GedcomInfo.CONC_OK:
            self.write_conc_ok(tag,level,note)
        else:
            self.write_conc_broken(tag,level,note)

    def write_conc_ok(self,tag,level,note):
        prefix = "%d %s" % (level,tag)
        textlines = string.split(note,'\n')
        if len(note) == 0:
            self.writeln(prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and line[brkpt] in string.whitespace):
                            brkpt = brkpt+1
                            if ll == brkpt:
                                self.writeln("%s %s" % (prefix,line))
                                line = ''
                                break
                        else:
                            self.writeln("%s %s" % (prefix,line[0:brkpt+1]))
                            line = line[brkpt+1:]
                    else:
                        self.writeln("%s %s" % (prefix,line))
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
            self.writeln(prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and line[brkpt] not in string.whitespace):
                            brkpt = brkpt+1
                            if ll == brkpt:
                                self.writeln("%s %s" % (prefix,line))
                                line = ''
                                break
                        else:
                            self.writeln("%s %s" % (prefix,line[0:brkpt+1]))
                            line = line[brkpt+1:]
                    else:
                        self.writeln("%s %s" % (prefix,line))
                        line = ""
                    if len(line) > 0:
                        prefix = "%d CONC" % (level+1)
                    else:
                        prefix = "%d CONT" % (level+1)
                    ll = len(line)
    
    def dump_event_stats(self,event):
        dateobj = event.getDateObj()
        self.print_date("2 DATE",dateobj)
        if event.getPlaceName():
            self.writeln("2 PLAC %s" % string.replace(self.cnvtxt(event.getPlaceName()),'\r',' '))
        if event.getCause():
            self.writeln("2 CAUS %s" % self.cnvtxt(event.getCause()))
        if event.getNote():
            self.write_long_text("NOTE",2,self.cnvtxt(event.getNote()))
        for srcref in event.getSourceRefList():
            self.write_source_ref(2,srcref)

    def write_ord(self,name,ord,index,statlist):
        if ord == None:
            return
        self.writeln('%d %s' % (index,name))
        self.print_date("%d DATE" % (index + 1), ord.getDateObj())
        if ord.getFamily():
            self.writeln('%d FAMC @%s@' % (index+1,self.fid(ord.getFamily().getId())))
        if ord.getTemple():
            self.writeln('%d TEMP %s' % (index+1,ord.getTemple()))
        if ord.getPlaceName():
            self.writeln("2 PLAC %s" % string.replace(self.cnvtxt(ord.getPlaceName()),'\r',' '))
        if ord.getStatus() != 0:
            self.writeln("2 STAT %s" % self.cnvtxt(statlist[ord.getStatus()]))
        if ord.getNote():
            self.write_long_text("NOTE",index+1,self.cnvtxt(ord.getNote()))
        for srcref in ord.getSourceRefList():
            self.write_source_ref(index+1,srcref)

    def print_date(self,prefix,date):
        start = date.get_start_date()
        val = date.getText()
        if val:
            self.writeln("%s %s" % (prefix,self.cnvtxt(val)))
        elif not date.isEmpty ():
            if date.isRange():
                val = "FROM %s TO %s" % (make_date(start),
                                         make_date(date.get_stop_date()))
            else:
                val = make_date(start)
            self.writeln("%s %s" % (prefix,val))

    def write_person_name(self,name,nick):
        firstName = self.cnvtxt(name.getFirstName())
        surName = self.cnvtxt(name.getSurname())
        surName = surName.replace('/','?')
        surPref = self.cnvtxt(name.getSurnamePrefix())
        surPref = surPref.replace('/','?')
        suffix = self.cnvtxt(name.getSuffix())
        title = self.cnvtxt(name.getTitle())
        if suffix == "":
            if not surPref:
                self.writeln("1 NAME %s /%s/" % (firstName,surName))
            else:
                self.writeln("1 NAME %s /%s %s/" % (firstName,surPref,surName))
        else:
            if not surPref:
                self.writeln("1 NAME %s /%s %s/, %s" % (firstName,surPref,surName,suffix))
            else:
                self.writeln("1 NAME %s /%s/, %s" % (firstName,surName,suffix))

        if name.getFirstName():
            self.writeln("2 GIVN %s" % firstName)
        if self.prefix:
            if surPref:
                self.writeln('2 SPFX %s' % surPref)
            if surName:
                self.writeln("2 SURN %s" % surName)
        else:
            if surPref:
                self.writeln("2 SURN %s %s" % (surPref,surName))
            elif surName:
                self.writeln("2 SURN %s" % surName)
                
        if name.getSuffix():
            self.writeln("2 NSFX %s" % suffix)
        if name.getTitle():
            self.writeln("2 NPFX %s" % title)
        if nick:
            self.writeln('2 NICK %s' % nick)
        if name.getNote():
            self.write_long_text("NOTE",2,self.cnvtxt(name.getNote()))
        for srcref in name.getSourceRefList():
            self.write_source_ref(2,srcref)

    def write_source_ref(self,level,ref):
        if ref.getBase() == None:
            return

        if self.source_refs:
            self.writeln("%d SOUR @%s@" %
                         (level,self.sid(ref.getBase().getId())))
            if ref.getPage() != "":
                self.write_long_text("PAGE",level+1,self.cnvtxt(ref.getPage()))

            ref_text = ref.getText()
            if ref_text != "" or not ref.getDate().isEmpty():
                self.writeln('%d DATA' % (level+1))
                if ref_text != "":
                    self.write_long_text("TEXT",level+2,self.cnvtxt(ref_text))
                pfx = "%d DATE" % (level+2)
                self.print_date(pfx,ref.getDate())
        else:
            # We put title, page, and date on the SOUR line.
            # Not using CONC and CONT because GeneWeb does not support these.
            # TEXT and NOTE will be ignored by GeneWeb, but we can't
            # output paragaphs in SOUR without CONT.
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
                self.writeln("")
            if ref.getText():
                ref_text = ref.getText()
                self.write_long_text("TEXT",level+1,self.cnvtxt(ref_text))

        if ref.getComments():
            self.write_long_text("NOTE",level+1,self.cnvtxt(ref.getComments()))
        
    def fid(self,id):
        return id

    def prefn(self,person):
        match = _get_int.search(person.getId())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))

    def frefn(self,family):
        match = _get_int.search(family.getId())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))
    
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

register_export(writeData,_title_string)
