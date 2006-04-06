#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import time
import re
import shutil

try:
    set()
except:
    from sets import Set as set

from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WriteGedcom")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import GenericFilter
import const
import lds
import _GedcomInfo as GedcomInfo
import Errors
import ansel_utf8
import Utils
import NameDisplay
from QuestionDialog import ErrorDialog, WarningDialog

def keep_utf8(s):
    return s

def iso8859(s):
    return s.encode('iso-8859-1','replace')

#-------------------------------------------------------------------------
#
# GEDCOM tags representing attributes that may take a parameter, value or
# description on the same line as the tag
#
#-------------------------------------------------------------------------
personalAttributeTakesParam = set(["CAST", "DSCR", "EDUC", "IDNO",
                                   "NATI", "NCHI", "NMR",  "OCCU",
                                   "PROP", "RELI", "SSN",  "TITL"])

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
    RelLib.Date.CAL_HEBREW : (_hmonth, '@#HEBREW@'),
    RelLib.Date.CAL_FRENCH : (_fmonth, '@#FRENCH R@'),
    RelLib.Date.CAL_JULIAN : (_month, '@#JULIAN@'),
    }

_caldef = {
    RelLib.Date.MOD_ABOUT : "ABT",
    RelLib.Date.MOD_BEFORE : "BEF",
    RelLib.Date.MOD_AFTER : "AFT",
    }


lds_ord_name = {
    RelLib.LdsOrd.BAPTISM         : 'BAPL',
    RelLib.LdsOrd.ENDOWMENT       : 'ENDL',
    RelLib.LdsOrd.SEAL_TO_PARENTS : 'SLGC',
    RelLib.LdsOrd.SEAL_TO_SPOUSE  : 'SGLS',
    }

lds_status = {
    RelLib.LdsOrd.STATUS_BIC        : "BIC",
    RelLib.LdsOrd.STATUS_CANCELED   : "CANCELED",
    RelLib.LdsOrd.STATUS_CHILD      : "CHILD",
    RelLib.LdsOrd.STATUS_CLEARED    : "CLEARED",
    RelLib.LdsOrd.STATUS_COMPLETED  : "COMPLETED",
    RelLib.LdsOrd.STATUS_DNS        : "DNS",
    RelLib.LdsOrd.STATUS_INFANT     : "INFANT",
    RelLib.LdsOrd.STATUS_PRE_1970   : "PRE-1970",
    RelLib.LdsOrd.STATUS_QUALIFIED  : "QUALIFIED",
    RelLib.LdsOrd.STATUS_DNS_CAN    : "DNS/CAN",
    RelLib.LdsOrd.STATUS_STILLBORN  : "STILLBORN",
    RelLib.LdsOrd.STATUS_SUBMITTED  : "SUBMITTED" ,
    RelLib.LdsOrd.STATUS_UNCLEARED  : "UNCLEARED",
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
def add_familys_sources(db,family_handle,slist,private):
    family = db.get_family_from_handle(family_handle)
    for source_ref in family.get_source_references():
        sbase = source_ref.get_base_handle()
        if sbase != None and not slist.has_key(sbase):
            slist[sbase] = 1
        
    for event_ref in family.get_event_ref_list():
        if not event_ref:
            continue
        event_handle = event_ref.ref
        event = db.get_event_from_handle(event_handle)
        if private and event.get_privacy():
            continue
        for source_ref in event.get_source_references():
            sbase = source_ref.get_base_handle()
            if sbase != None and not slist.has_key(sbase):
                slist[sbase] = 1

    for attr in family.get_attribute_list():
        if private and attr.get_privacy():
            continue
        for source_ref in attr.get_source_references():
            sbase = source_ref.get_base_handle()
            if sbase != None and not slist.has_key(sbase):
                slist[sbase] = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_persons_sources(db,person,slist,private):
    for source_ref in person.get_source_references():
        sbase = source_ref.get_base_handle()
        if sbase != None and not slist.has_key(sbase):
            slist[sbase] = 1
        
    for event_ref in person.get_event_ref_list() + [person.get_birth_ref(),
                      person.get_death_ref()]:
        if event_ref:
            event_handle = event_ref.ref
            event = db.get_event_from_handle(event_handle)
            if not event:
                continue
            if private and event.get_privacy():
                continue
            for source_ref in event.get_source_references():
                sbase = source_ref.get_base_handle()
                if sbase != None and not slist.has_key(sbase):
                    slist[sbase] = 1

    for event in person.get_address_list():
        if private and event.get_privacy():
            continue
        for source_ref in event.get_source_references():
            sbase = source_ref.get_base_handle()
            if sbase != None and not slist.has_key(sbase):
                slist[sbase] = 1

    for event in person.get_attribute_list():
        if private and event.get_privacy():
            continue
        for source_ref in event.get_source_references():
            sbase = source_ref.get_base_handle()
            if sbase != None and not slist.has_key(sbase):
                slist[sbase] = 1

    for name in person.get_alternate_names() + [person.get_primary_name()]:
        if private and name.get_privacy():
            continue
        for source_ref in name.get_source_references():
            sbase = source_ref.get_base_handle()
            if sbase != None and not slist.has_key(sbase):
                slist[sbase] = 1
                
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
    fid = first.get_handle()
    sid = second.get_handle()
    
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
def sort_by_gramps_id(first,second):
    fid = first.get_gramps_id()
    sid = second.get_gramps_id()
    
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
def make_date(subdate,calendar,mode):
    retval = ""
    (day,mon,year,sl) = subdate
    
    (mmap,prefix) = _calmap.get(calendar,(_month,""))

    if year < 0:
        year = -year
        bc = " B.C."
    else:
        bc = ""
        
    if day == 0:
        try:
            if mon == 0:
                retval = '%d%s' % (year,bc)
            elif year == 0:
                retval = '(%s)' % mmap[mon]
            else:
                retval = "%s %d%s" % (mmap[mon],year,bc)
        except IndexError:
            print "Month index error - %d" % mon
            retval = '%d%s' % (year,bc)
    elif mon == 0:
        retval = '%d%s' % (year,bc)
    else:
        try:
            month = mmap[mon]
            if year == 0:
                retval = "(%d %s)" % (day,month)
            else:
                retval = "%d %s %d%s" % (day,month,year,bc)
        except IndexError:
            print "Month index error - %d" % mon
            retval = "%d%s" % (year,bc)

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
    return app.join(new_text)

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
class GedcomWriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self,person):
        self.person = person

    def get_option_box(self):
        self.restrict = True
        self.private = True
        self.cnvtxt = ansel_utf8.utf8_to_ansel
        self.adopt = GedcomInfo.ADOPT_EVENT

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/gedcomexport.glade"

        self.topDialog = gtk.glade.XML(glade_file,"gedcomExport","gramps")
        self.topDialog.signal_autoconnect({
                "gnu_free" : self.gnu_free,
                "standard_copyright" : self.standard_copyright,
                "no_copyright" : self.no_copyright,
                "ansel" : self.ansel,
                "ansi" : self.ansi,
                "unicode" : self.uncd,
                "on_restrict_toggled": self.on_restrict_toggled,
                })

        filter_obj = self.topDialog.get_widget("filter")
        self.copy = 0

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        if self.person:
            des = GenericFilter.GenericFilter()
            des.set_name(_("Descendants of %s") %
                         NameDisplay.displayer.display(self.person))
            des.add_rule(GenericFilter.IsDescendantOf(
                [self.person.get_gramps_id(),1]))

            ans = GenericFilter.GenericFilter()
            ans.set_name(_("Ancestors of %s")
                         % NameDisplay.displayer.display(self.person))
            ans.add_rule(GenericFilter.IsAncestorOf(
                [self.person.get_gramps_id(),1]))

            com = GenericFilter.GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         NameDisplay.displayer.display(self.person))
            com.add_rule(GenericFilter.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))

            self.filter_menu = GenericFilter.build_filter_menu([all,des,ans,com])
        else:
            self.filter_menu = GenericFilter.build_filter_menu([all])
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
        
        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("gedcomExport").destroy()
        return the_box

    def gnu_free(self,obj):
        self.copy = 1

    def standard_copyright(self,obj):
        self.copy = 0

    def no_copyright(self,obj):
        self.copy = 2

    def ansel(self,obj):
        self.cnvtxt = ansel_utf8.utf8_to_ansel

    def uncd(self,obj):
        self.cnvtxt = keep_utf8

    def ansi(self,obj):
        self.cnvtxt = iso8859

    def on_restrict_toggled(self,restrict):
        active = restrict.get_active ()
        map (lambda x: x.set_sensitive (active),
             [self.topDialog.get_widget("living"),
              self.topDialog.get_widget("notes"),
              self.topDialog.get_widget("sources")])

    def parse_options(self):

        self.restrict = self.topDialog.get_widget("restrict").get_active()
        self.living = (self.restrict and
                       self.topDialog.get_widget("living").get_active())
        self.exclnotes = (self.restrict and
                          self.topDialog.get_widget("notes").get_active())
        self.exclsrcs = (self.restrict and
                         self.topDialog.get_widget("sources").get_active())
        self.private = self.topDialog.get_widget("private").get_active()

        self.cfilter = self.filter_menu.get_active().get_data("filter")
        act_tgt = self.target_menu.get_active()

        self.target_ged =  act_tgt.get_data("data")
        self.images = self.topDialog.get_widget ("images").get_active ()
        if self.images:
            images_path = self.topDialog.get_widget ("images_path")
            self.images_path = unicode(images_path.get_text ())
        else:
            self.images_path = ""

        self.dest = self.target_ged.get_dest()
        self.adopt = self.target_ged.get_adopt()
        self.conc = self.target_ged.get_conc()
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.prefix = self.target_ged.get_prefix()
        self.source_refs = self.target_ged.get_source_refs()

        self.nl = self.cnvtxt(self.target_ged.get_endl())


class GedcomWriter:
    def __init__(self,database,person,cl=0,filename="",option_box=None,
                 callback=None):
        self.db = database
        self.person = person
        self.option_box = option_box
        self.cl = cl
        self.filename = filename
        self.callback = callback
        if '__call__' in dir(self.callback): # callback is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        self.plist = {}
        self.slist = {}
        self.flist = {}
        self.fidval = 0
        self.fidmap = {}
        self.sidval = 0
        self.sidmap = {}
        
        if not option_box:
            self.cl_setup()
        else:
            self.option_box.parse_options()

            self.restrict = self.option_box.restrict
            self.living = self.option_box.living
            self.exclnotes = self.option_box.exclnotes
            self.exclsrcs = self.option_box.exclsrcs
            self.private = self.option_box.private
            self.copy = self.option_box.copy
            self.images = self.option_box.images
            self.images_path = self.option_box.images_path
            self.target_ged = self.option_box.target_ged
            self.dest = self.option_box.dest
            self.adopt = self.option_box.adopt
            self.conc = self.option_box.conc
            self.altname = self.option_box.altname
            self.cal = self.option_box.cal
            self.obje = self.option_box.obje
            self.resi = self.option_box.resi
            self.prefix = self.option_box.prefix
            self.source_refs = self.option_box.source_refs
            self.cnvtxt = self.option_box.cnvtxt
            self.nl = self.option_box.nl
            
            if self.option_box.cfilter == None:
                for p in self.db.get_person_handles(sort_handles=False):
                    self.plist[p] = 1
            else:
                try:
                    for p in self.option_box.cfilter.apply(self.db,
                            self.db.get_person_handles(sort_handles=False)):
                        self.plist[p] = 1
                except Errors.FilterError, msg:
                    (m1,m2) = msg.messages()
                    ErrorDialog(m1,m2)
                    return

            self.flist = {}
            self.slist = {}
            for key in self.plist.keys():
                p = self.db.get_person_from_handle(key)
                add_persons_sources(self.db,p,self.slist,
                                    self.option_box.private)
                for family_handle in p.get_family_handle_list():
                    add_familys_sources(self.db,family_handle,
                                        self.slist,self.option_box.private)
                    self.flist[family_handle] = 1
    
    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100*self.count/self.total)
        if newval != self.oldval:
            self.callback(newval)
            self.oldval = newval

    def cl_setup(self):
        self.restrict = 0
        self.private = 0
        self.copy = 0
        self.images = 0

        for p in self.db.get_person_handles(sort_handles=False):
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
            p = self.db.get_person_from_handle(key)
            add_persons_sources(self.db,p,self.slist,self.private)
            for family_handle in p.get_family_handle_list():
                add_familys_sources(self.db,family_handle,
                                    self.slist,self.private)
                self.flist[family_handle] = 1

    def writeln(self,text):
        self.g.write('%s%s' % (text,self.nl))

    def export_data(self,filename):

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % filename
            ErrorDialog(msg2,str(msg))
            return 0
        except:
            ErrorDialog(_("Could not create %s") % filename)
            return 0

        date = time.ctime(time.time()).split()

        self.writeln("0 HEAD")
        self.writeln("1 SOUR GRAMPS")
        self.writeln("2 VERS %s" % const.version)
        self.writeln("2 NAME GRAMPS")
        if self.dest:
            self.writeln("1 DEST %s" % self.dest)
        self.writeln("1 DATE %s %s %s" % (date[2],date[1].upper(),date[4]))
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
        owner = self.db.get_researcher()
        if owner.get_name():
            self.writeln("1 NAME %s" % self.cnvtxt(owner.get_name()))
        else:
            self.writeln('1 NAME Not Provided')

        if owner.get_address():
            cnt = 0
            self.writeln("1 ADDR %s" % self.cnvtxt(owner.get_address()))
            if owner.get_city():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.get_city()))
                cnt = 1
            if owner.get_state():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.get_state()))
                cnt = 1
            if owner.get_postal_code():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.get_postal_code()))
                cnt = 1
            if owner.get_country():
                self.writeln("2 CONT %s" % self.cnvtxt(owner.get_country()))
                cnt = 1
            if cnt == 0:
                self.writeln('2 CONT Not Provided')
            if owner.get_phone():
                self.writeln("1 PHON %s" % self.cnvtxt(owner.get_phone()))
        else:
            self.writeln('1 ADDR Not Provided')
            self.writeln('2 CONT Not Provided')

        pkeys = self.plist.keys()
        self.total = len(pkeys) + len(self.flist.keys()) \
                     + len(self.slist.keys())
        self.oldval = 0
        self.count = 0
        
        sorted = []
        for key in pkeys:
            person = self.db.get_person_from_handle (key)
            data = (person.get_gramps_id (), person)
            sorted.append (data)
        sorted.sort()
        for (gramps_id, person) in sorted:
            self.write_person(person)
            self.update()

        self.write_families()
        if self.source_refs:
            self.write_sources()

        self.writeln("0 TRLR")
        self.g.close()
        return 1

    def write_copy(self):
        t = time.localtime(time.time())
        y = t[0]

        if self.copy == 0:
            o = self.db.get_researcher().get_name()
            self.writeln('1 COPR Copyright (c) %d %s.' % (y,o))
        elif self.copy == 1:
            o = self.db.get_researcher().get_name()
            self.writeln('1 COPR Copyright (c) %d %s. See additional copyright NOTE below.' % (y,o))

    def gnu_fdl(self):
        if self.copy != 1:
            return

        t = time.localtime(time.time())
        y = t[0]
        o = self.db.get_researcher().get_name()

        self.writeln('1 NOTE       Copyright (c) %d %s.' % (y,o))
        try:
            f = open(const.fdl,"r")
            for line in f.readlines():
                self.g.write('2 CONT %s' % line)
            f.close()
        except:
            pass

    def write_families(self):
        sorted = []
        for family_handle in self.flist.keys ():
            family = self.db.get_family_from_handle(family_handle)
            data = (self.fid (family_handle), family_handle, family)
            sorted.append (data)
        sorted.sort ()
        for (gramps_id, family_handle, family) in sorted:
            father_alive = mother_alive = 0
            self.writeln("0 @%s@ FAM" % gramps_id)
            self.frefn(family)
            person_handle = family.get_father_handle()
            if person_handle != None and self.plist.has_key(person_handle):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.writeln("1 HUSB @%s@" % gramps_id)
                father_alive = Utils.probably_alive(person,self.db)

            person_handle = family.get_mother_handle()
            if person_handle != None and self.plist.has_key(person_handle):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.writeln("1 WIFE @%s@" % gramps_id)
                mother_alive = Utils.probably_alive(person,self.db)

            if not self.restrict or ( not father_alive and not mother_alive ):
                for lds in family.get_lds_ord_list():
                    self.write_ord(lds,1)

                for event_ref in family.get_event_ref_list():
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if not event or self.private and event.get_privacy():
                        continue
                    (index,name) = event.get_type()

                    val = ""
                    if Utils.family_events.has_key(index):
                        val = Utils.family_events[index]
                    if val == "":
                        val = self.target_ged.gramps2tag(name)

                    if val:
                        if not event.get_date_object().is_empty() or event.get_place_handle():
                            self.writeln("1 %s" % self.cnvtxt(val))
                        else:
                            self.writeln("1 %s Y" % self.cnvtxt(val))
                        if event.get_description() != "":
                            self.writeln("2 TYPE %s" % event.get_description())
                    else:
                        self.writeln("1 EVEN")
                        self.writeln("2 TYPE %s" % ' '.join([self.cnvtxt(name),
                                                             event.get_description()]))

                    self.dump_event_stats(event)

            for person_handle in family.get_child_handle_list():
                if not self.plist.has_key(person_handle):
                    continue
                person = self.db.get_person_from_handle(person_handle)
                if not person:
                    continue
                self.writeln("1 CHIL @%s@" % person.get_gramps_id())
                if self.adopt == GedcomInfo.ADOPT_FTW:
                    if person.get_main_parents_family_handle() == family.get_handle():
                        self.writeln('2 _FREL Natural')
                        self.writeln('2 _MREL Natural')
                    else:
                        for f in person.get_parent_family_handle_list():
                            if f[0] == family.get_handle():
                                self.writeln('2 _FREL %s' % f[2])
                                self.writeln('2 _MREL %s' % f[1])
                                break
                if self.adopt == GedcomInfo.ADOPT_LEGACY:
                    for f in person.get_parent_family_handle_list():
                       if f[0] == family.get_handle():
                           self.writeln('2 _STAT %s' % f[2])
                           break

            for srcref in family.get_source_references():
                self.write_source_ref(1,srcref)

            if self.images:
                photos = family.get_media_list ()
                for photo in photos:
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,1)

            self.write_change(1,family.get_change_time())
            self.update()
            
    def write_sources(self):
        index = 0.0
        sorted = []
        for handle in self.slist.keys():
            source = self.db.get_source_from_handle(handle)
            if not source:
                continue
            data = (self.sid(handle), source)
            sorted.append (data)
        sorted.sort ()
        for (source_id, source) in sorted:
            self.writeln("0 @%s@ SOUR" % source_id)
            if source.get_title():
                self.writeln("1 TITL %s" % fmtline(self.cnvtxt(source.get_title()),248,1,self.nl))
            if source.get_author():
                self.writeln("1 AUTH %s" % self.cnvtxt(source.get_author()))
            if source.get_publication_info():
                self.writeln("1 PUBL %s" % self.cnvtxt(source.get_publication_info()))
            if source.get_abbreviation():
                self.writeln("1 ABBR %s" % self.cnvtxt(source.get_abbreviation()))
            if self.images:
                photos = source.get_media_list ()
                for photo in photos:
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,1)

            if source.get_note():
                self.write_long_text("NOTE",1,self.cnvtxt(source.get_note()))
            index = index + 1
            self.write_change(1,source.get_change_time())
            self.update()
            
    def write_person(self,person):
        self.writeln("0 @%s@ INDI" % person.get_gramps_id())
        restricted = self.restrict and Utils.probably_alive (person,self.db)
        self.prefn(person)
        primaryname = person.get_primary_name ()
        if restricted and self.living:
            primaryname = RelLib.Name (primaryname)
            primaryname.set_first_name ("Living")
            nickname = ""
        else:
            primaryname = person.get_primary_name ()
            nickname = person.get_nick_name ()
           
        if restricted and self.exclnotes:
            primaryname = RelLib.Name (primaryname)
            primaryname.set_note ('')

        if restricted and self.exclsrcs:
            primaryname = RelLib.Name (primaryname)
            primaryname.set_source_reference_list ([])

        self.write_person_name(primaryname, nickname)

        if (self.altname == GedcomInfo.ALT_NAME_STD and
            not (restricted and self.living)):
            for name in person.get_alternate_names():
                self.write_person_name(name,"")
    
        if person.get_gender() == RelLib.Person.MALE:
            self.writeln("1 SEX M")
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.writeln("1 SEX F")

        if not restricted:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if not (self.private and birth.get_privacy()):
                    if not birth.get_date_object().is_empty() or birth.get_place_handle():
                        self.writeln("1 BIRT")
                    else:
                        self.writeln("1 BIRT Y")
                    if birth.get_description() != "":
                        self.writeln("2 TYPE %s" % birth.get_description())
                    self.dump_event_stats(birth)

            death_ref = person.get_death_ref()
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if not (self.private and death.get_privacy()):
                    if not death.get_date_object().is_empty() or death.get_place_handle():
                        self.writeln("1 DEAT")
                    else:
                        self.writeln("1 DEAT Y")
                    if death.get_description() != "":
                        self.writeln("2 TYPE %s" % death.get_description())
                    self.dump_event_stats(death)

            ad = 0

            for lds_ord in person.get_lds_ord_list():
                self.write_ord(lds_ord,1)
            
            for event_ref in person.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if self.private and event.get_privacy():
                    continue
                (index,name) = event.get_type()
                val = ""
                if Utils.personal_events.has_key(index):
                    val = Utils.personal_events[index]
                if val == "":
                    val = self.target_ged.gramps2tag(index)
                        
                if self.adopt == GedcomInfo.ADOPT_EVENT and val == "ADOP":
                    ad = 1
                    self.writeln('1 ADOP')
                    fam = None
                    for f in person.get_parent_family_handle_list():
                        mrel = f[1]
                        frel = f[2]
                        if (mrel == RelLib.Person.CHILD_ADOPTED or
                            frel == RelLib.Person.CHILD_ADOPTED):
                            fam = f[0]
                            break
                    if fam:
                        self.writeln('2 FAMC @%s@' % self.fid(fam.get_gramps_id()))
                        if mrel == frel:
                            self.writeln('3 ADOP BOTH')
                        elif mrel == "adopted":
                            self.writeln('3 ADOP WIFE')
                        else:
                            self.writeln('3 ADOP HUSB')
                elif val :
                    if val in personalAttributeTakesParam:
                        if event.get_description():
                            self.writeln("1 %s %s" % (self.cnvtxt(val),\
                                                      self.cnvtxt(event.get_description())))
                        else:
                            self.writeln("1 %s" % self.cnvtxt(val))
                    else:
                        if not event.get_date_object().is_empty() or event.get_place_handle():
                            self.writeln("1 %s" % self.cnvtxt(val))
                        else:
                            self.writeln("1 %s Y" % self.cnvtxt(val))
                        if event.get_description():
                            self.writeln("2 TYPE %s" % self.cnvtxt(event.get_description()))
                else:
                    # Actually, it is against the spec to put anything
                    # after EVEN on the same line, possibly an option is
                    # needed on how to handle this
                    if event.get_description() != "":
                        self.writeln("1 EVEN %s" % event.get_description())
                    else:
                        self.writeln("1 EVEN")
                    self.writeln("2 TYPE %s" % self.cnvtxt(name))

                self.dump_event_stats(event)

            if self.adopt == GedcomInfo.ADOPT_EVENT and ad == 0 and len(person.get_parent_family_handle_list()) != 0:
                self.writeln('1 ADOP')
                fam = None
                for f in person.get_parent_family_handle_list():
                    mrel = f[1]
                    frel = f[2]
                    if (mrel == RelLib.Person.CHILD_ADOPTED or
                        frel == RelLib.Person.CHILD_ADOPTED):
                        fam = f[0]
                        break
                if fam:
                    self.writeln('2 FAMC @%s@' % self.fid(fam.get_gramps_id()))
                    if mrel == frel:
                        self.writeln('3 ADOP BOTH')
                    elif mrel == "adopted":
                        self.writeln('3 ADOP WIFE')
                    else:
                        self.writeln('3 ADOP HUSB')

            for attr in person.get_attribute_list():
                if self.private and attr.get_privacy():
                    continue
                name = attr.get_type()
 
                if name in ["AFN", "RFN", "_UID"]:
                    self.writeln("1 %s %s" % ( name, attr.get_value()))
                    continue
                
                if Utils.personal_attributes.has_key(name):
                    val = Utils.personal_attributes[name]
                else:
                    val = ""
                value = self.cnvtxt(attr.get_value()).replace('\r',' ')
                if val:
                    if value:
                        self.writeln("1 %s %s" % (val, value))
                    else:
                        self.writeln("1 %s" % val)
                else:
                    self.writeln("1 EVEN")
                    if value:
                        self.writeln("2 TYPE %s %s" % (self.cnvtxt(name), value))
                    else:
                        self.writeln("2 TYPE %s" % self.cnvtxt(name))
                if attr.get_note():
                    self.write_long_text("NOTE",2,self.cnvtxt(attr.get_note()))
                for srcref in attr.get_source_references():
                    self.write_source_ref(2,srcref)
 
            for addr in person.get_address_list():
                if self.private and addr.get_privacy():
                    continue
                self.writeln("1 RESI")
                self.print_date("2 DATE",addr.get_date_object())
                if self.resi == 0:
                    self.write_long_text("ADDR",2,self.cnvtxt(addr.get_street()))
                    if addr.get_city():
                        self.writeln("3 CITY %s" % self.cnvtxt(addr.get_city()))
                    if addr.get_state():
                        self.writeln("3 STAE %s" % self.cnvtxt(addr.get_state()))
                    if addr.get_postal_code():
                        self.writeln("3 POST %s" % self.cnvtxt(addr.get_postal_code()))
                    if addr.get_country():
                        self.writeln("3 CTRY %s" % self.cnvtxt(addr.get_country()))
                    if addr.get_phone():
                        self.writeln("2 PHON %s" % self.cnvtxt(addr.get_phone()))
                else:
                    text = addr.get_street()
                    text = addr_append(text,addr.get_city())
                    text = addr_append(text,addr.get_state())
                    text = addr_append(text,addr.get_postal_code())
                    text = addr_append(text,addr.get_country())
                    text = addr_append(text,addr.get_phone())
                    if text:
                        self.writeln("2 PLAC %s" % self.cnvtxt(text).replace('\r',' '))
                if addr.get_note():
                    self.write_long_text("NOTE",2,self.cnvtxt(addr.get_note()))
                for srcref in addr.get_source_references():
                    self.write_source_ref(2,srcref)

            if self.images:
                photos = person.get_media_list ()
                for photo in photos:
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,1)

        for family in person.get_parent_family_handle_list():
            if self.flist.has_key(family[0]):
                self.writeln("1 FAMC @%s@" % self.fid(family[0]))
                if self.adopt == GedcomInfo.ADOPT_PEDI:
                    if family[1] == RelLib.Person.CHILD_ADOPTED:
                        self.writeln("2 PEDI Adopted")

        for family_handle in person.get_family_handle_list():
            if family_handle != None and self.flist.has_key(family_handle):
                self.writeln("1 FAMS @%s@" % self.fid(family_handle))

        for srcref in person.get_source_references():
            self.write_source_ref(1,srcref)
        
        if not restricted:
            if self.obje:
                for url in person.get_url_list():
                    if self.private and url.get_privacy():
                        continue
                    self.writeln('1 OBJE')
                    self.writeln('2 FORM URL')
                    if url.get_description():
                        self.writeln('2 TITL %s' % url.get_description())
                    if url.get_path():
                        self.writeln('2 FILE %s' % url.get_path())

        if not restricted or not self.exclnotes:
            if person.get_note():
                self.write_long_text("NOTE",1,self.cnvtxt(person.get_note()))

        self.write_change(1,person.get_change_time())


    def write_change(self,level,timeval):
        self.writeln('%d CHAN' % level)
        time_val = time.localtime(timeval)
        self.writeln('%d DATE %d %s %d' % (level + 1,time_val[2],
                                           _month[time_val[1]],time_val[0]))
        self.writeln('%d TIME %02d:%02d:%02d' % (level + 2,time_val[3],
                                                 time_val[4],time_val[5]))
        

    def write_long_text(self,tag,level,note):
        if self.conc == GedcomInfo.CONC_OK:
            self.write_conc_ok(tag,level,note)
        else:
            self.write_conc_broken(tag,level,note)

    def write_conc_ok(self,tag,level,note):
        prefix = "%d %s" % (level,tag)
        textlines = note.split('\n')
        if len(note) == 0:
            self.writeln(prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and line[brkpt].isspace()):
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
        textlines = note.split('\n')
        if len(note) == 0:
            self.writeln(prefix)
        else:
            for line in textlines:
                ll = len(line)
                while ll > 0:
                    brkpt = 70
                    if ll > brkpt:
                        while (ll > brkpt and not line[brkpt].isspace()):
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
        dateobj = event.get_date_object()
        self.print_date("2 DATE",dateobj)
        place = None
        if event.get_place_handle():
            place = self.db.get_place_from_handle(event.get_place_handle())
            self.write_place(place,2)
        if event.get_cause():
            self.writeln("2 CAUS %s" % self.cnvtxt(event.get_cause()))
        if event.get_note():
            self.write_long_text("NOTE",2,self.cnvtxt(event.get_note()))
        for srcref in event.get_source_references():
            self.write_source_ref(2,srcref)

        if self.images:
            photos = event.get_media_list()
            for photo in photos:
                if self.private and photo.get_privacy():
                    continue
                self.write_photo(photo,2)
            if place:
                for photo in place.get_media_list():
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,2)

    def write_ord(self, ord, index):
        self.writeln('%d %s' % (index, lds_ord_name[ord.get_type()]))
        self.print_date("%d DATE" % (index + 1), ord.get_date_object())
        if ord.get_family_handle():
            family_id = ord.get_family_handle()
            f = self.db.get_family_from_handle(family_id)
            if f:
                self.writeln('%d FAMC @%s@' % (index+1,self.fid(family_id)))
        if ord.get_temple():
            self.writeln('%d TEMP %s' % (index+1,ord.get_temple()))
        if ord.get_place_handle():
            self.write_place(self.db.get_place_from_handle(ord.get_place_handle()),2)
        if ord.get_status() != RelLib.LdsOrd.STATUS_NONE:
            self.writeln("2 STAT %s" % self.cnvtxt(lds_status[ord.get_status()]))
        if ord.get_note():
            self.write_long_text("NOTE",index+1,self.cnvtxt(ord.get_note()))
        for srcref in ord.get_source_references():
            self.write_source_ref(index+1,srcref)

    def print_date(self,prefix,date):
        start = date.get_start_date()
        if start != RelLib.Date.EMPTY:
            cal = date.get_calendar()
            mod = date.get_modifier()
            if date.get_modifier() == RelLib.Date.MOD_SPAN:
                val = "FROM %s TO %s" % (make_date(start,cal,mod),
                                         make_date(date.get_stop_date(),cal,mod))
            elif date.get_modifier() == RelLib.Date.MOD_RANGE:
                val = "BET %s AND %s" % (make_date(start,cal,mod),
                                         make_date(date.get_stop_date(),cal,mod))
            else:
                val = make_date(start,cal,mod)
            self.writeln("%s %s" % (prefix,val))
        elif date.get_text():
            self.writeln("%s %s" % (prefix,self.cnvtxt(date.get_text())))

    def write_person_name(self,name,nick):
        firstName = self.cnvtxt("%s %s" % (name.get_first_name(),name.get_patronymic())).strip()
        surName = self.cnvtxt(name.get_surname())
        surName = surName.replace('/','?')
        surPref = self.cnvtxt(name.get_surname_prefix())
        surPref = surPref.replace('/','?')
        suffix = self.cnvtxt(name.get_suffix())
        title = self.cnvtxt(name.get_title())
        if suffix == "":
            if surPref == "":
                self.writeln("1 NAME %s /%s/" % (firstName,surName))
            else:
                self.writeln("1 NAME %s /%s %s/" % (firstName,surPref,surName))
        else:
            if surPref == "":
                self.writeln("1 NAME %s /%s/ %s" % (firstName,surName,suffix))
            else:
                self.writeln("1 NAME %s /%s %s/ %s" % (firstName,surPref,surName,suffix))

        if firstName:
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
                
        if name.get_suffix():
            self.writeln("2 NSFX %s" % suffix)
        if name.get_title():
            self.writeln("2 NPFX %s" % title)
        if nick:
            self.writeln('2 NICK %s' % nick)
        if name.get_note():
            self.write_long_text("NOTE",2,self.cnvtxt(name.get_note()))
        for srcref in name.get_source_references():
            self.write_source_ref(2,srcref)

    def write_source_ref(self,level,ref):
        if ref.get_base_handle() == None:
            return

        if self.source_refs:
            self.writeln("%d SOUR @%s@" %
                         (level,self.sid(ref.get_base_handle())))
            if ref.get_page() != "":
                self.write_long_text("PAGE",level+1,self.cnvtxt(ref.get_page()))
 
            ref_text = ref.get_text()
            if ref_text != "" or not ref.get_date_object().is_empty():
                self.writeln('%d DATA' % (level+1))
                if ref_text != "":
                    self.write_long_text("TEXT",level+2,self.cnvtxt(ref_text))
                pfx = "%d DATE" % (level+2)
                self.print_date(pfx,ref.get_date_object())
        else:
            # We put title, page, and date on the SOUR line.
            # Not using CONC and CONT because GeneWeb does not support these.
            # TEXT and NOTE will be ignored by GeneWeb, but we can't
            # output paragaphs in SOUR without CONT.
            txt = ""
            sbase_handle = ref.get_base_handle()
            if sbase_handle:
                sbase = self.db.get_source_from_handle(sbase_handle)
                if sbase and sbase.get_title():
                    txt = sbase.get_title() + ".  "
            if ref.get_page():
                txt = txt + ref.get_page() + ".  "
            self.g.write("%d SOUR %s" % (level,self.cnvtxt(txt)))
            if not ref.get_date_object().is_empty():
                self.print_date("", ref.get_date_object())
            else:
                 self.writeln("")
            if ref.get_text():
                ref_text = ref.get_text()
                self.write_long_text("TEXT",level+1,self.cnvtxt(ref_text))
 
        if ref.get_note():
            self.write_long_text("NOTE",level+1,self.cnvtxt(ref.get_note()))

    mime2ged = {
        "image/bmp"   : "bmp",
        "image/gif"   : "gif",
        "image/jpeg"  : "jpeg",
        "image/x-pcx" : "pcx",
        "image/tiff"  : "tiff",
        "audio/x-wav" : "wav"
        }

    def write_photo(self,photo,level):
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.db.get_object_from_handle(photo_obj_id)
        print photo_obj, photo_obj.get_mime_type()
        if photo_obj:
            mime = photo_obj.get_mime_type()
            if self.mime2ged.has_key(mime):
                form = self.mime2ged[mime]
            else:
                form = mime
            path = photo_obj.get_path ()
            imgdir = os.path.join(self.dirname,self.images_path)
            if not os.path.isfile(path):
                return
            try:
                if not os.path.isdir(imgdir):
                    os.makedirs(imgdir)
            except:
                return
            basename = os.path.basename(path)
            dest = os.path.join (imgdir, basename)
            if dest != path:
                try:
                    shutil.copyfile(path, dest)
                    shutil.copystat(path, dest)
                except (IOError,OSError),msg:
                    msg2 = _("Could not create %s") % dest
                    WarningDialog(msg2,str(msg))
                    return

            self.writeln('%d OBJE' % level)
            if form:
                self.writeln('%d FORM %s' % (level+1, form) )
            self.writeln('%d TITL %s' % (level+1, photo_obj.get_description()))
            dirname = os.path.join (self.dirname, self.images_path)
            basename = os.path.basename (path)
            self.writeln('%d FILE %s' % (level+1,os.path.join(self.images_path,
                                                              basename)))
            if photo_obj.get_note():
                self.write_long_text("NOTE",level+1,self.cnvtxt(photo_obj.get_note()))

    def write_place(self,place,level):
        place_name = place.get_title()
        self.writeln("%d PLAC %s" % (level,self.cnvtxt(place_name).replace('\r',' ')))

    def fid(self,id):
        family = self.db.get_family_from_handle (id)
        return family.get_gramps_id ()
 
    def prefn(self,person):
        match = _get_int.search(person.get_gramps_id())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))

    def frefn(self,family):
        match = _get_int.search(family.get_gramps_id())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))
    
    def sid(self,handle):
        source = self.db.get_source_from_handle(handle)
        return source.get_gramps_id()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database,filename,person,option_box,callback=None):
    ret = 0
    try:
        gw = GedcomWriter(database,person,0,filename,option_box,callback)
        ret = gw.export_data(filename)
    except Errors.DatabaseError,msg:
        ErrorDialog(_("Export failed"),str(msg))
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('GE_DCOM')
_description = _('GEDCOM is used to transfer data between genealogy programs. '
        'Most genealogy software will accept a GEDCOM file as input. ')
_config = (_('GEDCOM export options'),GedcomWriterOptionBox)
_filename = 'ged'

from PluginUtils import register_export
register_export(exportData,_title,_description,_config,_filename)
