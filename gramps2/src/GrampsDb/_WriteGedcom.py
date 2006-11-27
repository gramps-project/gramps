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
from gettext import gettext as _
import os
import time
import re
import shutil
try:
    set()
except:
    from sets import Set as set

import logging
log = logging.getLogger(".WriteGedcom")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
from Filters import GenericFilter, Rules, build_filter_menu
import const
import _GedcomInfo as GedcomInfo
import Config
import Errors
import ansel_utf8
import Utils
import NameDisplay
from QuestionDialog import ErrorDialog, WarningDialog, MessageHideDialog
from BasicUtils import UpdateCallback

#------------------------------------------------------------------------
#
# Helper functions
#
#------------------------------------------------------------------------
def keep_utf8(s):
    return s

def iso8859(s):
    return s.encode('iso-8859-1','replace')

def researcher_info_missing():
    val = Config.get(Config.STARTUP)
    if val < const.startup:
        return True
    return False

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
    RelLib.LdsOrd.CONFIRMATION    : 'CONL',
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

mime2ged = {
    "image/bmp"   : "bmp",
    "image/gif"   : "gif",
    "image/jpeg"  : "jpeg",
    "image/x-pcx" : "pcx",
    "image/tiff"  : "tiff",
    "audio/x-wav" : "wav"
    }

quay_map = {
    RelLib.SourceRef.CONF_VERY_HIGH : 3,
    RelLib.SourceRef.CONF_HIGH      : 2,
    RelLib.SourceRef.CONF_LOW       : 1,
    RelLib.SourceRef.CONF_VERY_LOW  : 0,
}

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

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        the_filters = [all]

        if self.person:
            des = GenericFilter()
            des.set_name(_("Descendants of %s") %
                         NameDisplay.displayer.display(self.person))
            des.add_rule(Rules.Person.IsDescendantOf(
                [self.person.get_gramps_id(),1]))

            ans = GenericFilter()
            ans.set_name(_("Ancestors of %s")
                         % NameDisplay.displayer.display(self.person))
            ans.add_rule(Rules.Person.IsAncestorOf(
                [self.person.get_gramps_id(),1]))

            com = GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         NameDisplay.displayer.display(self.person))
            com.add_rule(Rules.Person.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))

            the_filters += [des,ans,com]

        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))
        self.filter_menu = build_filter_menu(the_filters)
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

#-------------------------------------------------------------------------
#
# GedcomWriter class
#
#-------------------------------------------------------------------------
class GedcomWriter(UpdateCallback):
    def __init__(self,database,person,cl=0,filename="",option_box=None,
                 callback=None):
        UpdateCallback.__init__(self,callback)

        self.db = database
        self.person = person
        self.option_box = option_box
        self.cl = cl
        self.filename = filename
        
        if option_box:
            setup_func = self.gui_setup
        else:
            setup_func = self.cli_setup

        # Run setup, bail out if status is not Ture
        if not setup_func():
            return

        self.flist = set()
        self.slist = set()
        self.rlist = set()

        # Collect needed families
        for handle in list(self.plist):
            person = self.db.get_person_from_handle(handle)
            if self.private and person.private:
                self.plist.remove(handle)
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if self.private and family.private:
                    continue
                self.flist.add(family_handle)
    
    def gui_setup(self):
        # Get settings from the options store/dialog
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

        if researcher_info_missing():
            MessageHideDialog(
                _('Researcher information'),
                _('A valid GEDCOM file is required to contain researcher '
                  'information. You need to fill these data in the '
                  'Preferences dialog.\n\n'
                  'However, most programs do not require it. '
                  'You may leave this empty if you want.'),Config.STARTUP)

        if self.option_box.cfilter == None:
            self.plist = set(self.db.get_person_handles(sort_handles=False))
        else:
            try:
                self.plist = set(self.option_box.cfilter.apply(
                    self.db,self.db.get_person_handles(sort_handles=False)))
                return True
            except Errors.FilterError, msg:
                (m1,m2) = msg.messages()
                ErrorDialog(m1,m2)
                return False

    def cli_setup(self):
        # use default settings
        self.restrict = 0
        self.private = 0
        self.copy = 0
        self.images = 0

        self.plist = set(self.db.get_person_handles(sort_handles=False))

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

        return True

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
                self.writeln("2 CONT %s" %
                             self.cnvtxt(owner.get_postal_code()))
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

        self.set_total(len(self.plist) + len(self.flist))
        
        sorted = []
        for handle in self.plist:
            person = self.db.get_person_from_handle (handle)
            data = (person.get_gramps_id (), person)
            sorted.append (data)
        sorted.sort()
        for (gramps_id, person) in sorted:
            self.write_person(person)
            self.update()

        self.write_families()
        if self.source_refs:
            self.write_sources()
            self.write_repos()

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
            self.writeln('1 COPR Copyright (c) %d %s. '
                         'See additional copyright NOTE below.' % (y,o))

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
        for family_handle in self.flist:
            family = self.db.get_family_from_handle(family_handle)
            data = (family.get_gramps_id(), family_handle, family)
            sorted.append (data)
        sorted.sort ()
        for (gramps_id, family_handle, family) in sorted:
            father_alive = mother_alive = 0
            self.writeln("0 @%s@ FAM" % gramps_id)
            self.frefn(family)
            person_handle = family.get_father_handle()
            if (person_handle != None) and (person_handle in self.plist):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.writeln("1 HUSB @%s@" % gramps_id)
                father_alive = Utils.probably_alive(person,self.db)

            person_handle = family.get_mother_handle()
            if (person_handle != None) and (person_handle in self.plist):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.writeln("1 WIFE @%s@" % gramps_id)
                mother_alive = Utils.probably_alive(person,self.db)

            if not self.restrict or ( not father_alive and not mother_alive ):
                for lds_ord in family.get_lds_ord_list():
                    self.write_ord(lds_ord,1)

                for event_ref in family.get_event_ref_list():
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if not event or self.private and event.get_privacy():
                        continue

                    etype = int(event.get_type())
                    val = GedcomInfo.familyConstantEvents.get(etype)

                    if val == None:
                        val = self.target_ged.gramps2tag(etype)

                    if val:
                        if (not event.get_date_object().is_empty()) \
                               or event.get_place_handle():
                            self.writeln("1 %s" % self.cnvtxt(val))
                        else:
                            self.writeln("1 %s Y" % self.cnvtxt(val))

                        if event.get_type() == RelLib.EventType.MARRIAGE:
                            ftype = family.get_relationship()
                            if ftype != RelLib.FamilyRelType.MARRIED and \
                               str(ftype).strip() != "":
                                self.writeln("2 TYPE %s" % str(ftype))
                        elif event.get_description().strip() != "":
                            self.writeln("2 TYPE %s" % event.get_description())
                    else:
                        self.writeln("1 EVEN")
                        the_type = str(event.get_type())
                        if the_type:
                            self.writeln("2 TYPE %s" % self.cnvtxt(the_type))

                    self.dump_event_stats(event, event_ref)

            for attr in family.get_attribute_list():
                if self.private and attr.get_privacy():
                    continue

                t = int(attr.get_type())
                name = GedcomInfo.familyConstantAttributes.get(t)
                value = self.cnvtxt(attr.get_value()).replace('\r',' ')

                if name and name.strip():
                    self.writeln("1 %s %s" % (name,value))
                    continue
                else:
                    the_name = str(attr.get_type())
                    self.writeln("1 EVEN")
                    if value:
                        self.writeln("2 TYPE %s %s" %(self.cnvtxt(the_name),
                                                      value))
                    else:
                        self.writeln("2 TYPE %s" % self.cnvtxt(the_name))

                if attr.get_note():
                    self.write_long_text("NOTE",2,self.cnvtxt(attr.get_note()))
                for srcref in attr.get_source_references():
                    self.write_source_ref(2,srcref)

            for child_ref in family.get_child_ref_list():
                if child_ref.ref not in self.plist:
                    continue
                person = self.db.get_person_from_handle(child_ref.ref)
                if not person:
                    continue
                self.writeln("1 CHIL @%s@" % person.get_gramps_id())
                if self.adopt == GedcomInfo.ADOPT_FTW:
                    if person.get_main_parents_family_handle() \
                           == family.get_handle():
                        self.writeln('2 _FREL Natural')
                        self.writeln('2 _MREL Natural')
                    else:
                        if family.get_handle() in \
                               person.get_parent_family_handle_list():
                            for child_ref in family.get_child_ref_list():
                                if child_ref.ref == person.handle:
                                    self.writeln('2 _FREL %s' %
                                                 child_ref.frel.xml_str())
                                    self.writeln('2 _MREL %s' %
                                                 child_ref.mrel.xml_str())
                                    break
                if self.adopt == GedcomInfo.ADOPT_LEGACY:
                    if family.get_handle() in \
                           person.get_parent_family_handle_list():
                        self.writeln('2 _STAT %s' % child_ref.mrel.xml_str())

            for srcref in family.get_source_references():
                self.write_source_ref(1,srcref)

            if self.images:
                photos = family.get_media_list ()
                for photo in photos:
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,1)

            if family.get_note():
                self.write_long_text("NOTE",1,self.cnvtxt(family.get_note()))

            self.write_change(1,family.get_change_time())
            self.update()
            
    def write_sources(self):
        sorted = []
        for handle in self.slist:
            source = self.db.get_source_from_handle(handle)
            if not source:
                continue
            if self.private and source.private:
                continue
            data = (source.get_gramps_id(), source)
            sorted.append (data)
        sorted.sort ()

        for (source_id, source) in sorted:
            self.writeln("0 @%s@ SOUR" % source_id)
            if source.get_title():
                self.write_long_text('TITL',1,
                                     "%s" % self.cnvtxt(source.get_title()))

            if source.get_author():
                self.write_long_text("AUTH", 1,
                                     "%s" % self.cnvtxt(source.get_author()))

            if source.get_publication_info():
                self.write_long_text("PUBL", 1,"%s" % self.cnvtxt(
                    source.get_publication_info()))

            if source.get_abbreviation():
                self.writeln("1 ABBR %s" %
                             self.cnvtxt(source.get_abbreviation()))
            if self.images:
                photos = source.get_media_list ()
                for photo in photos:
                    if self.private and photo.get_privacy():
                        continue
                    self.write_photo(photo,1)

            for reporef in source.get_reporef_list():
                self.write_reporef(reporef,1)

            if source.get_note():
                self.write_long_text("NOTE",1,self.cnvtxt(source.get_note()))
            self.write_change(1,source.get_change_time())
            
    def write_repos(self):
        sorted = []
        for handle in self.rlist:
            repo = self.db.get_repository_from_handle(handle)
            if self.private and repo.private:
                continue
            repo_id = repo.get_gramps_id()
            sorted.append((repo_id,repo))

        sorted.sort()

        slist = set()
        
        for (repo_id,repo) in sorted:
            self.writeln("0 @%s@ REPO" % repo_id)
            if repo.get_name():
                self.write_long_text('NAME',1,
                                     "%s" % self.cnvtxt(repo.get_name()))
            for addr in repo.get_address_list():
                self.write_long_text("ADDR",1,
                                     self.cnvtxt(addr.get_street()))
                if addr.get_city():
                    self.writeln("2 CITY %s"
                                 % self.cnvtxt(addr.get_city()))
                if addr.get_state():
                    self.writeln("2 STAE %s"
                                 % self.cnvtxt(addr.get_state()))
                if addr.get_postal_code():
                    self.writeln("2 POST %s"
                                 % self.cnvtxt(addr.get_postal_code()))
                if addr.get_country():
                    self.writeln("2 CTRY %s"
                                 % self.cnvtxt(addr.get_country()))
                if addr.get_phone():
                    self.writeln("1 PHON %s"
                                 % self.cnvtxt(addr.get_phone()))

            if repo.get_note():
                self.write_long_text("NOTE",1,self.cnvtxt(repo.get_note()))

    def write_reporef(self,reporef,level):

        if reporef.ref == None:
            return

        # Append handle to the list for exporting REPOs later
        self.rlist.add(reporef.ref)

        repo = self.db.get_repository_from_handle(reporef.ref)
        repo_id = repo.get_gramps_id()

        self.writeln("%d REPO @%s@" % (level,repo_id) )

        if reporef.get_note():
            self.write_long_text("NOTE",level+1,
                                 self.cnvtxt(reporef.get_note()))

        if reporef.get_call_number():
            self.writeln("%d CALN %s" %
                         ( (level+1), reporef.get_call_number() ) )
            if reporef.get_media_type():
                self.writeln("%d MEDI %s" %
                             ((level+2),
                              self.cnvtxt(str(reporef.get_media_type()))))


    def write_person(self,person):
        self.writeln("0 @%s@ INDI" % person.get_gramps_id())
        restricted = self.restrict and Utils.probably_alive (person,self.db)
        self.prefn(person)
        primaryname = person.get_primary_name ()
        nickname = ""
        if restricted and self.living:
            primaryname = RelLib.Name (primaryname)
            primaryname.set_first_name ("Living")
            #nickname = ""
        else:
            primaryname = person.get_primary_name ()
            #nickname = person.get_nick_name ()
           
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
                    if (not birth.get_date_object().is_empty()) \
                           or birth.get_place_handle():
                        self.writeln("1 BIRT")
                    else:
                        self.writeln("1 BIRT Y")
                    if birth.get_description().strip() != "":
                        self.writeln("2 TYPE %s" % birth.get_description())
                    self.dump_event_stats(birth, birth_ref)

            death_ref = person.get_death_ref()
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if not (self.private and death.get_privacy()):
                    if (not death.get_date_object().is_empty()) \
                           or death.get_place_handle():
                        self.writeln("1 DEAT")
                    else:
                        self.writeln("1 DEAT Y")
                    if death.get_description().strip() != "":
                        self.writeln("2 TYPE %s" % death.get_description())
                    self.dump_event_stats(death, death_ref)

            ad = 0

            for lds_ord in person.get_lds_ord_list():
                self.write_ord(lds_ord,1)
            
            for event_ref in person.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) in (RelLib.EventType.BIRTH,
                                             RelLib.EventType.DEATH):
                    continue
                
                if self.private and event.get_privacy():
                    continue

                etype = int(event.get_type())
                val = GedcomInfo.personalConstantEvents.get(etype)
                if val == None:
                    val = self.target_ged.gramps2tag(etype)
                        
                if self.adopt == GedcomInfo.ADOPT_EVENT and val == "ADOP":
                    ad = 1
                    self.writeln('1 ADOP')
                    fam = None
                    for fh in person.get_parent_family_handle_list():
                        family = self.db.get_family_from_handle(fh)
                        for child_ref in family.get_child_ref_list():
                            if child_ref.ref == person.handle:
                                if \
                                       child_ref.mrel == \
                                       RelLib.ChildRefType.ADOPTED \
                                       or child_ref.frel == \
                                       RelLib.ChildRefType.ADOPTED:
                                    frel = child_ref.frel
                                    mrel = child_ref.mrel
                                    fam = family
                                    break
                    if fam:
                        self.writeln('2 FAMC @%s@' % fam.get_gramps_id())
                        if mrel == frel:
                            self.writeln('3 ADOP BOTH')
                        elif mrel == RelLib.ChildRefType.ADOPTED:
                            self.writeln('3 ADOP WIFE')
                        else:
                            self.writeln('3 ADOP HUSB')
                elif val and val.strip():
                    if val in personalAttributeTakesParam:
                        if event.get_description().strip():
                            self.writeln(
                                "1 %s %s" %
                                (self.cnvtxt(val),
                                 self.cnvtxt(event.get_description())))
                        else:
                            self.writeln("1 %s" % self.cnvtxt(val))
                    else:
                        if (not event.get_date_object().is_empty()) \
                               or event.get_place_handle():
                            self.writeln("1 %s" % self.cnvtxt(val))
                        else:
                            self.writeln("1 %s Y" % self.cnvtxt(val))
                        if event.get_description().strip():
                            self.writeln(
                                "2 TYPE %s"
                                % self.cnvtxt(event.get_description()))
                else:
                    # Actually, it is against the spec to put anything
                    # after EVEN on the same line, possibly an option is
                    # needed on how to handle this

                    if event.get_description().strip() != "":
                        self.writeln("1 EVEN %s" %
                                     self.cnvtxt(event.get_description()))
                    else:
                        self.writeln("1 EVEN")
                    if val.strip():
                        self.writeln("2 TYPE %s" % self.cnvtxt(val))
                    else:
                        self.writeln("2 TYPE %s" % self.cnvtxt(str(event.get_type())))

                self.dump_event_stats(event, event_ref)

            if (self.adopt == GedcomInfo.ADOPT_EVENT) and (ad == 0) \
                   and (len(person.get_parent_family_handle_list()) != 0):
                self.writeln('1 ADOP')
                fam = None
                for fh in person.get_parent_family_handle_list():
                    family = self.db.get_family_from_handle(fh)
                    for child_ref in family.get_child_ref_list():
                        if child_ref.ref == person.handle:
                            if (child_ref.mrel == RelLib.ChildRefType.ADOPTED)\
                                   or (child_ref.frel \
                                       == RelLib.ChildRefType.ADOPTED):
                                frel = child_ref.frel
                                mrel = child_ref.mrel
                                fam = family
                                break
                if fam:
                    self.writeln('2 FAMC @%s@' % fam.get_gramps_id())
                    if mrel == frel:
                        self.writeln('3 ADOP BOTH')
                    elif mrel == RelLib.ChildRefType.ADOPTED:
                        self.writeln('3 ADOP WIFE')
                    else:
                        self.writeln('3 ADOP HUSB')

            for attr in person.get_attribute_list():
                if self.private and attr.get_privacy():
                    continue

                t = int(attr.get_type())
                name = GedcomInfo.personalConstantAttributes.get(t)
                key = str(attr.get_type())
                value = self.cnvtxt(attr.get_value().strip()).replace('\r',' ')

                if key in ("AFN", "RFN", "_UID"):
                    self.writeln("1 %s %s" % (name,value))
                    continue

                if key == "RESN":
                    self.writeln("1 RESN")
                    continue

                if name and name.strip():
                    self.writeln("1 %s %s" % (name,value))
                else:
                    self.writeln("1 EVEN")
                    if value:
                        self.writeln("2 TYPE %s %s" %(self.cnvtxt(name),value))
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
                    self.write_long_text("ADDR",2,
                                         self.cnvtxt(addr.get_street()))
                    if addr.get_city():
                        self.writeln("3 CITY %s"
                                     % self.cnvtxt(addr.get_city()))
                    if addr.get_state():
                        self.writeln("3 STAE %s"
                                     % self.cnvtxt(addr.get_state()))
                    if addr.get_postal_code():
                        self.writeln("3 POST %s"
                                     % self.cnvtxt(addr.get_postal_code()))
                    if addr.get_country():
                        self.writeln("3 CTRY %s"
                                     % self.cnvtxt(addr.get_country()))
                    if addr.get_phone():
                        self.writeln("2 PHON %s"
                                     % self.cnvtxt(addr.get_phone()))
                else:
                    text = addr.get_street()
                    text = addr_append(text,addr.get_city())
                    text = addr_append(text,addr.get_state())
                    text = addr_append(text,addr.get_postal_code())
                    text = addr_append(text,addr.get_country())
                    text = addr_append(text,addr.get_phone())
                    if text:
                        self.writeln("2 PLAC %s"
                                     % self.cnvtxt(text).replace('\r',' '))
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

        for family_handle in person.get_parent_family_handle_list():
            if family_handle in self.flist:
                family = self.db.get_family_from_handle(family_handle)
                family_id = family.get_gramps_id()
                self.writeln("1 FAMC @%s@" % family_id)
                if self.adopt == GedcomInfo.ADOPT_PEDI:
                    # Go over all children of the family to find the ref
                    for child_ref in family.get_child_ref_list():
                        if child_ref.ref == person.handle:
                            if (child_ref.frel ==
                                RelLib.ChildRef.ADOPTED) \
                                or (child_ref.mrel \
                                    == RelLib.ChildRef.ADOPTED):
                                self.writeln("2 PEDI Adopted")
                                break

        for family_handle in person.get_family_handle_list():
            if (family_handle != None) and (family_handle in self.flist):
                family = self.db.get_family_from_handle(family_handle)
                self.writeln("1 FAMS @%s@" % family.get_gramps_id())

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
                if ll == 0:
                    self.writeln("%s " % prefix)
                    prefix = "%d CONT" % (level+1)
                    continue
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
                if ll == 0:
                    self.writeln("%s " % prefix)
                    prefix = "%d CONT" % (level+1)
                    continue
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
    
    def dump_event_stats(self,event, event_ref):
        dateobj = event.get_date_object()
        self.print_date("2 DATE",dateobj)
        place = None
        if event.get_place_handle():
            place = self.db.get_place_from_handle(event.get_place_handle())
            self.write_place(place,2)
        for attr in event.get_attribute_list():
            t = attr.get_type()
            if t == RelLib.AttributeType.CAUSE:
                self.writeln("2 CAUS %s" % self.cnvtxt(attr.get_value()))
            elif t == RelLib.AttributeType.AGENCY:
                self.writeln("2 AGNC %s" % self.cnvtxt(attr.get_value()))
        for attr in event_ref.get_attribute_list():
            t = attr.get_type()
            if t == RelLib.AttributeType.AGE:
                self.writeln("2 AGE %s" % self.cnvtxt(attr.get_value()))
            elif t == RelLib.AttributeType.FATHER_AGE:
                self.writeln("2 HUSB")
                self.writeln("3 AGE %s" % self.cnvtxt(attr.get_value()))
            elif t == RelLib.AttributeType.MOTHER_AGE:
                self.writeln("2 WIFE")
                self.writeln("3 AGE %s" % self.cnvtxt(attr.get_value()))
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
        if self.private and ord.private:
            return
        self.writeln('%d %s' % (index, lds_ord_name[ord.get_type()]))
        self.print_date("%d DATE" % (index + 1), ord.get_date_object())
        if ord.get_family_handle():
            family_handle = ord.get_family_handle()
            family = self.db.get_family_from_handle(family_handle)
            if family:
                self.writeln('%d FAMC @%s@' % (index+1,family.get_gramps_id()))
        if ord.get_temple():
            self.writeln('%d TEMP %s' % (index+1,ord.get_temple()))
        if ord.get_place_handle():
            self.write_place(
                self.db.get_place_from_handle(ord.get_place_handle()),2)
        if ord.get_status() != RelLib.LdsOrd.STATUS_NONE:
            self.writeln("2 STAT %s" %
                         self.cnvtxt(lds_status[ord.get_status()]))
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
                val = "FROM %s TO %s" % (
                    make_date(start,cal,mod),
                    make_date(date.get_stop_date(),cal,mod))
            elif date.get_modifier() == RelLib.Date.MOD_RANGE:
                val = "BET %s AND %s" % (
                    make_date(start,cal,mod),
                    make_date(date.get_stop_date(),cal,mod))
            else:
                val = make_date(start,cal,mod)
            self.writeln("%s %s" % (prefix,val))
        elif date.get_text():
            self.writeln("%s %s" % (prefix,self.cnvtxt(date.get_text())))

    def write_person_name(self,name,nick):
        if self.private and name.private:
            return
        firstName = self.cnvtxt("%s %s" % (name.get_first_name(),
                                           name.get_patronymic())).strip()
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
                self.writeln("1 NAME %s /%s %s/ %s" % (firstName,surPref,
                                                       surName,suffix))

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
        if self.private and ref.private:
            return

        src_handle = ref.get_reference_handle()
       
        if src_handle == None:
            return

        src = self.db.get_source_from_handle(src_handle)
        if self.private and src.private:
            return

        self.slist.add(src_handle)

        if self.source_refs:
            # Reference to the source
            self.writeln("%d SOUR @%s@" % (level,src.get_gramps_id()))
            if ref.get_page() != "":
                self.write_long_text("PAGE",level+1,
                                     self.cnvtxt(ref.get_page()))

            conf = ref.get_confidence_level()
            # Cap the maximum level
            conf = min(conf,RelLib.SourceRef.CONF_VERY_HIGH)
            if conf != RelLib.SourceRef.CONF_NORMAL:
                self.write_long_text("QUAY",level+1, str(quay_map[conf]))

            ref_text = ref.get_text()
            if ref_text != "" or not ref.get_date_object().is_empty():
                self.writeln('%d DATA' % (level+1))
                if ref_text != "":
                    self.write_long_text("TEXT",level+2,self.cnvtxt(ref_text))
                pfx = "%d DATE" % (level+2)
                self.print_date(pfx,ref.get_date_object())
        else:
            # Inline source
            
            # We put title, page, and date on the SOUR line.
            # Not using CONC and CONT because GeneWeb does not support these.
            # TEXT and NOTE will be ignored by GeneWeb, but we can't
            # output paragaphs in SOUR without CONT.
            txt = ""
            if src.get_title():
                txt = src.get_title() + ".  "
            if ref.get_page():
                txt = txt + ref.get_page() + ".  "
            self.writeln("%d SOUR %s" % (level,self.cnvtxt(txt)))
            if not ref.get_date_object().is_empty():
                self.print_date("", ref.get_date_object())
            ref_text = ref.get_text()
            if ref_text:                
                self.write_long_text("TEXT",level+1,self.cnvtxt(ref_text))
 
        if ref.get_note():
            self.write_long_text("NOTE",level+1,self.cnvtxt(ref.get_note()))

    def write_photo(self,photo,level):
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.db.get_object_from_handle(photo_obj_id)
        if photo_obj:
            mime = photo_obj.get_mime_type()
            if mime2ged.has_key(mime):
                form = mime2ged[mime]
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
            basename = os.path.basename (path)
            self.writeln('%d FILE %s' % (level+1,os.path.join(self.images_path,
                                                              basename)))
            if photo_obj.get_note():
                self.write_long_text("NOTE",level+1,
                                     self.cnvtxt(photo_obj.get_note()))

    def write_place(self,place,level):
        if self.private and place.private:
            return
        place_name = place.get_title()
        self.writeln("%d PLAC %s" %
                     (level,self.cnvtxt(place_name).replace('\r',' ')))

    def prefn(self,person):
        match = _get_int.search(person.get_gramps_id())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))

    def frefn(self,family):
        match = _get_int.search(family.get_gramps_id())
        if match:
            self.writeln('1 REFN %d' % int(match.groups()[0]))

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
