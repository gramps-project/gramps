#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
import string

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
import Errors
import ansel_utf8
import Utils
from BasicUtils import name_displayer
from QuestionDialog import *
from BasicUtils import UpdateCallback

try:
    import Config
    HAVE_CONFIG = True
except:
    log.warn("No Config module available using defaults.")
    HAVE_CONFIG = False

#------------------------------------------------------------------------
#
# Helper functions
#
#------------------------------------------------------------------------
def keep_utf8(s):
    return s

def iso8859(s):
    return s.encode('iso-8859-1', 'replace')

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
    RelLib.Date.CAL_HEBREW : (_hmonth, '@#DHEBREW@'), 
    RelLib.Date.CAL_FRENCH : (_fmonth, '@#DFRENCH R@'), 
    RelLib.Date.CAL_JULIAN : (_month, '@#DJULIAN@'), 
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
def addr_append(text, data):
    if data:
        return "%s, %s" % (text, data)
    else:
        return text
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sort_by_gramps_id(first, second):
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
def make_date(subdate, calendar, mode):
    retval = ""
    (day, mon, year, sl) = subdate
    
    (mmap, prefix) = _calmap.get(calendar, (_month, ""))

    if year < 0:
        year = -year
        bc = " B.C."
    else:
        bc = ""
        
    if day == 0:
        try:
            if mon == 0:
                retval = '%d%s' % (year, bc)
            elif year == 0:
                retval = '(%s)' % mmap[mon]
            else:
                retval = "%s %d%s" % (mmap[mon], year, bc)
        except IndexError:
            print "Month index error - %d" % mon
            retval = '%d%s' % (year, bc)
    elif mon == 0:
        retval = '%d%s' % (year, bc)
    else:
        try:
            month = mmap[mon]
            if year == 0:
                retval = "(%d %s)" % (day, month)
            else:
                retval = "%d %s %d%s" % (day, month, year, bc)
        except IndexError:
            print "Month index error - %d" % mon
            retval = "%d%s" % (year, bc)

    if prefix:
        retval = "%s %s" % (prefix, retval)

    if _caldef.has_key(mode):
        retval = "%s %s"  % (_caldef[mode], retval)
        
    return retval

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def writeData(database, person):
    GedcomWriter(database, person)


def breakup(txt, limit):
    data = []
    while limit < len(txt):
        idx = limit-1
        while txt[idx] in string.whitespace:
            idx -= 1
        data.append(txt[:idx+1])
        txt = txt[idx+1:]
    if len(txt) > 0:
        data.append(txt)
    return data

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
    def __init__(self, person):
        self.person = person

    def get_option_box(self):
        self.restrict = True
        self.private = True
        self.cnvtxt = keep_utf8
        self.adopt = GedcomInfo.ADOPT_EVENT

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/gedcomexport.glade"

        self.topDialog = gtk.glade.XML(glade_file, "gedcomExport", "gramps")
        self.topDialog.signal_autoconnect({
                "gnu_free"            : self.gnu_free, 
                "standard_copyright"  : self.standard_copyright, 
                "no_copyright"        : self.no_copyright, 
                "ansel"               : self.ansel, 
                "ansi"                : self.ansi, 
                "unicode"             : self.uncd, 
                "on_restrict_toggled" : self.on_restrict_toggled, 
                })

        self.topDialog.get_widget("encoding").set_history(1)

        filter_obj = self.topDialog.get_widget("filter")
        self.copy = 0

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        the_filters = [all]

        if self.person:
            des = GenericFilter()
            des.set_name(_("Descendants of %s") %
                         name_displayer.display(self.person))
            des.add_rule(Rules.Person.IsDescendantOf(
                [self.person.get_gramps_id(), 1]))

            ans = GenericFilter()
            ans.set_name(_("Ancestors of %s")
                         % name_displayer.display(self.person))
            ans.add_rule(Rules.Person.IsAncestorOf(
                [self.person.get_gramps_id(), 1]))

            com = GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         name_displayer.display(self.person))
            com.add_rule(Rules.Person.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))

            the_filters += [des, ans, com]

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
            menuitem.set_data("data", data)
            menuitem.show()

        target_obj.set_menu(myMenu)
        self.target_menu = myMenu
        
        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("gedcomExport").destroy()
        return the_box

    def gnu_free(self, obj):
        self.copy = 1

    def standard_copyright(self, obj):
        self.copy = 0

    def no_copyright(self, obj):
        self.copy = 2

    def ansel(self, obj):
        self.cnvtxt = ansel_utf8.utf8_to_ansel

    def uncd(self, obj):
        self.cnvtxt = keep_utf8

    def ansi(self, obj):
        self.cnvtxt = iso8859

    def on_restrict_toggled(self, restrict):
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
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.prefix = self.target_ged.get_prefix()

        self.nl = self.cnvtxt(self.target_ged.get_endl())

#-------------------------------------------------------------------------
#
# GedcomWriter class
#
#-------------------------------------------------------------------------
class GedcomWriter(UpdateCallback):
    def __init__(self, database, person, cl=0, filename="", option_box=None, 
                 callback=None):
        UpdateCallback.__init__(self, callback)

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
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                self.flist.add(family_handle)

    def __writeln(self, level, token, text="", limit=248):
        if text:
            if limit:
                prefix = "\n%d CONC " % (level + 1)
                txt = prefix.join(breakup(self.cnvtxt(text), limit))
            else:
                txt = self.cnvtxt(text)
            self.g.write("%d %s %s\n" % (level, token, txt))
        else:
            self.g.write("%d %s\n" % (level, token))
    
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
        self.altname = self.option_box.altname
        self.cal = self.option_box.cal
        self.obje = self.option_box.obje
        self.resi = self.option_box.resi
        self.prefix = self.option_box.prefix
        self.cnvtxt = self.option_box.cnvtxt
        self.nl = self.option_box.nl

        if self.option_box.cfilter == None:
            self.plist = set(self.db.get_person_handles(sort_handles=False))
        else:
            try:
                self.plist = set(self.option_box.cfilter.apply(
                    self.db, self.db.get_person_handles(sort_handles=False)))
                return True
            except Errors.FilterError, msg:
                (m1, m2) = msg.messages()
                ErrorDialog(m1, m2)
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
        self.altname = self.target_ged.get_alt_name()
        self.cal = self.target_ged.get_alt_calendar()
        self.obje = self.target_ged.get_obje()
        self.resi = self.target_ged.get_resi()
        self.prefix = self.target_ged.get_prefix()

        self.cnvtxt = keep_utf8
        self.nl = self.cnvtxt(self.target_ged.get_endl())

        return True

    def writeln(self, text):
        self.g.write('%s%s' % (text, self.nl))

    def export_data(self, filename):

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename, "w")
        except IOError, msg:
            msg2 = _("Could not create %s") % filename
            ErrorDialog(msg2, str(msg))
            return 0
        except:
            ErrorDialog(_("Could not create %s") % filename)
            return 0

        self.set_total(len(self.plist) + len(self.flist))

        self.__write_header(filename)
        self.__write_submitter()
        self.__write_individuals()
        self.__write_families()
        self.__write_sources()
        self.__write_repos()

        self.__writeln(0, "TRLR")
        self.g.close()
        return 1

    def __write_header(self, filename):
        """
        Writes the GEDCOM header. 

          HEADER:=
          n HEAD {1:1}
          +1 SOUR <APPROVED_SYSTEM_ID> {1:1} p.*
          +2 VERS <VERSION_NUMBER> {0:1} p.*
          +2 NAME <NAME_OF_PRODUCT> {0:1} p.*
          +2 CORP <NAME_OF_BUSINESS> {0:1} p.*          # Not used
          +3 <<ADDRESS_STRUCTURE>> {0:1} p.*            # Not used
          +2 DATA <NAME_OF_SOURCE_DATA> {0:1} p.*       # Not used
          +3 DATE <PUBLICATION_DATE> {0:1} p.*          # Not used
          +3 COPR <COPYRIGHT_SOURCE_DATA> {0:1} p.*     # Not used
          +1 DEST <RECEIVING_SYSTEM_NAME> {0:1*} p.*    # Not used
          +1 DATE <TRANSMISSION_DATE> {0:1} p.*
          +2 TIME <TIME_VALUE> {0:1} p.*
          +1 SUBM @XREF:SUBM@ {1:1} p.*
          +1 SUBN @XREF:SUBN@ {0:1} p.*
          +1 FILE <FILE_NAME> {0:1} p.*
          +1 COPR <COPYRIGHT_GEDCOM_FILE> {0:1} p.*
          +1 GEDC {1:1}
          +2 VERS <VERSION_NUMBER> {1:1} p.*
          +2 FORM <GEDCOM_FORM> {1:1} p.*
          +1 CHAR <CHARACTER_SET> {1:1} p.*
          +2 VERS <VERSION_NUMBER> {0:1} p.*
          +1 LANG <LANGUAGE_OF_TEXT> {0:1} p.*
          +1 PLAC {0:1}
          +2 FORM <PLACE_HIERARCHY> {1:1} p.*
          +1 NOTE <GEDCOM_CONTENT_DESCRIPTION> {0:1} p.*
          +2 [CONT|CONC] <GEDCOM_CONTENT_DESCRIPTION> {0:M}
        """
        (year, mon, day, hour, min, sec, x, y, z) = time.localtime(time.time())
        date_str = "%d %s %d" % (day, _month[mon], year)
        time_str = "%02d:%02d:%02d" % (hour, min, sec)
        rname = self.db.get_researcher().get_name()

        self.__writeln(0, "HEAD")
        self.__writeln(1, "SOUR", "GRAMPS")
        self.__writeln(2, "VERS",  const.version)
        self.__writeln(2, "NAME", "GRAMPS")
        self.__writeln(1, "DATE", date_str)
        self.__writeln(2, "TIME", time_str)
        self.__writeln(1, "SUBM", "@SUBM@")
        self.__writeln(1, "FILE", filename)
        self.__writeln(1, "COPR", 'Copyright (c) %d %s.' % (year, rname))
        self.__writeln(1, "GEDC")
        self.__writeln(2, "VERS", "5.5")
        self.__writeln(2, "FORM", 'LINEAGE-LINKED')

        if self.cnvtxt == ansel_utf8.utf8_to_ansel:
            self.__writeln(1, "CHAR", "ANSEL")
        elif self.cnvtxt == iso8859:
            self.__writeln(1, "CHAR", "ANSI")
        else:
            self.__writeln(1, "CHAR", "UTF-8")

    def __write_submitter(self):
        """
        SUBMITTER RECORD
        """
        owner = self.db.get_researcher()
        (name, addr, city, stae, ctry, post, phon, mail) = owner.get()
        if not name : 
            name = u'Not Provided'
        if not addr : 
            addr = u'Not Provided'
        
        self.__writeln(0, "@SUBM@", "SUBM")
        self.__writeln(1, "NAME", name)
        self.__writeln(1, "ADDR", addr)
        if city and stae and post:
            self.__writeln(2, "CONT", "%s, %s %s" % (city, stae, post))
        if city:
            self.__writeln(2, "CITY", city)
        if stae:
            self.__writeln(2, "STAE", stae)
        if post:
            self.__writeln(2, "POST", post)
        if ctry:
            self.__writeln(2, "CTRY", ctry)
        if phon:
            self.__writeln(1, "PHON", phon)

    def __write_individuals(self):
        """
        INDIVIDUAL RECORDS
        """
        sorted = []
        for handle in self.plist:
            person = self.db.get_person_from_handle (handle)
            data = (person.get_gramps_id (), handle)
            sorted.append (data)
        sorted.sort()

        for handle in [ data[1] for data in sorted]:
            person = self.db.get_person_from_handle (handle)
            self.__write_person(person)
            self.update()

    def __write_person(self, person):
        """
        Writes out a single person
        """
        self.__writeln(0, "@%s@" % person.get_gramps_id(),  "INDI")

        self.__write_refn(person)
        self.__write_names(person)
        self.__write_gender(person)
        self.__write_person_event_ref('BIRT', person.get_birth_ref())
        self.__write_person_event_ref('DEAT', person.get_death_ref())
        self.__write_lds_ords(person)

        self.__write_remaining_events(person)

        self.__write_attributes(person)
        self.__write_addresses(person)
        self.__write_photos(person.get_media_list())
        self.__write_child_families(person)
        self.__write_parent_families(person)
        self.__write_person_sources(person)
        self.__write_person_objects(person)
        
        for notehandle in person.get_note_list():
            self.write_note(1, notehandle)

        self.write_change(1, person.get_change_time())

    def __write_refn(self, person):
        match = _get_int.search(person.get_gramps_id())
        if match:
            self.__writeln(1, 'REFN', match.groups()[0])

    def __write_names(self, person):
        nickname = ""

        self.write_person_name(person.get_primary_name(), nickname)

        if self.altname == GedcomInfo.ALT_NAME_STD and not self.living:
            for name in person.get_alternate_names():
                self.write_person_name(name, "")

    def __write_gender(self, person):
        if person.get_gender() == RelLib.Person.MALE:
            self.__writeln(1, "SEX", "M")
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.__writeln(1, "SEX", "F")

    def __write_lds_ords(self, person):
        for lds_ord in person.get_lds_ord_list():
            self.write_ord(lds_ord, 1)

    def __write_remaining_events(self, person):

        ad = 0
        for event_ref in person.get_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            etype = int(event.get_type())

            if etype in (RelLib.EventType.BIRTH, RelLib.EventType.DEATH):
                continue
                
            val = GedcomInfo.personalConstantEvents.get(
                etype, self.target_ged.gramps2tag(etype))
                        
            if self.adopt == GedcomInfo.ADOPT_EVENT and val == "ADOP":
                ad = 1
                self.__write_adoption_record(person)
            elif val and val.strip():
                if val in personalAttributeTakesParam:
                    if event.get_description().strip():
                        self.__writeln(1, val, event.get_description())
                    else:
                        self.__writeln(1, val)
                else:
                    if (not event.get_date_object().is_empty()) \
                            or event.get_place_handle():
                        self.__writeln(1, val)
                    else:
                        self.__writeln(1, val, 'Y')
                    if event.get_description().strip():
                        self.__writeln(2, 'TYPE', event.get_description())
            else:
                # Actually, it is against the spec to put anything
                # after EVEN on the same line, possibly an option is
                # needed on how to handle this
                
                if event.get_description().strip() != "":
                    self.__writeln(1, 'EVEN', event.get_description())
                else:
                    self.__writeln(1, 'EVEN')
                if val.strip():
                    self.__writeln(2, 'TYPE', val)
                else:
                    self.__writeln(2, 'TYPE', str(event.get_type()))

            self.dump_event_stats(event, event_ref)
        
        if (self.adopt == GedcomInfo.ADOPT_EVENT) and (ad == 0) \
                and (len(person.get_parent_family_handle_list()) != 0):
            self.__write_adoption_record(person)


    def __write_adoption_record(self, person):
        self.__writeln(1, 'ADOP')
        fam = None
        for fh in person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(fh)
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == person.handle:
                    if child_ref.mrel == RelLib.ChildRefType.ADOPTED \
                            or child_ref.frel == RelLib.ChildRefType.ADOPTED:
                        frel = child_ref.frel
                        mrel = child_ref.mrel
                        fam = family
                        break
        if fam:
            self.__writeln(2, 'FAMC', '@%s@' % fam.get_gramps_id())
            if mrel == frel:
                self.__writeln(3, 'ADOP', 'BOTH')
            elif mrel == RelLib.ChildRefType.ADOPTED:
                self.__writeln(3, 'ADOP', 'WIFE')
            else:
                self.__writeln(3, 'ADOP', 'HUSB')

    def __write_attributes(self, person):
        for attr in person.get_attribute_list():

            t = int(attr.get_type())
            name = GedcomInfo.personalConstantAttributes.get(t)
            key = str(attr.get_type())
            value = attr.get_value().strip().replace('\r', ' ')
            
            if key in ("AFN", "RFN", "_UID"):
                self.__writeln(1, name, value)
                continue

            if key == "RESN":
                self.__writeln(1, 'RESN')
                continue

            if name and name.strip():
                self.__writeln(1, name, value)
            else:
                self.__writeln(1, 'EVEN')
                if value:
                    self.__writeln(2, 'TYPE', "%s %s" % (key , value))
                else:
                    self.__writeln(2, 'TYPE', key)

            for notehandle in attr.get_note_list():
                self.write_note(2, notehandle)
                
            for srcref in attr.get_source_references():
                self.write_source_ref(2, srcref)

    def __write_addresses(self, person):
        for addr in person.get_address_list():
            self.__writeln(1, 'RESI')
            self.print_date("2 DATE", addr.get_date_object())
            if self.resi == 0:
                self.__writeln(2, "ADDR", addr.get_street())
                if addr.get_city():
                    self.__writeln(3, 'CITY', addr.get_city())
                if addr.get_state():
                    self.__writeln(3, 'STAE', addr.get_state())
                if addr.get_postal_code():
                    self.__writeln(3, 'POST', addr.get_postal_code())
                if addr.get_country():
                    self.__writeln(3, 'CTRY', addr.get_country())
                if addr.get_phone():
                    self.__writeln(2, 'PHON', addr.get_phone())
            else:
                text = addr.get_street()
                text = addr_append(text, addr.get_city())
                text = addr_append(text, addr.get_state())
                text = addr_append(text, addr.get_postal_code())
                text = addr_append(text, addr.get_country())
                text = addr_append(text, addr.get_phone())
                if text:
                    self.__writeln(2, 'PLAC', text.replace('\r', ' '))
            for notehandle in addr.get_note_list():
                self.write_note(2, notehandle)
                
            for srcref in addr.get_source_references():
                self.write_source_ref(2, srcref)

    def __write_photos(self, media_list):
        if self.images:
            for photo in media_list:
                self.write_photo(photo, 1)

    def __write_child_families(self, person):
        hndl_list = [ hndl for hndl in person.get_parent_family_handle_list() \
                          if hndl and hndl in self.flist ]

        for family_handle in hndl_list:
            family = self.db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            self.__writeln(1, 'FAMC', '@%s@' % family_id)
            if self.adopt == GedcomInfo.ADOPT_PEDI:
                # Go over all children of the family to find the ref
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref == person.handle:
                        if (child_ref.frel == RelLib.ChildRefType.ADOPTED) \
                            or (child_ref.mrel == RelLib.ChildRefType.ADOPTED):
                            self.__writeln(2, 'PEDI', 'Adopted')
                            break

    def __write_parent_families(self, person):
        for family_handle in person.get_family_handle_list():
            if family_handle in self.flist:
                family = self.db.get_family_from_handle(family_handle)
                self.__writeln(1, 'FAMS', '@%s@' % family.get_gramps_id())

    def __write_person_sources(self, person):
        for srcref in person.get_source_references():
            self.write_source_ref(1, srcref)

    def __write_person_objects(self, person):
        if self.obje:
            for url in person.get_url_list():
                self.__writeln(1, 'OBJE')
                self.__writeln(2, 'FORM', 'URL')
                if url.get_description():
                    self.__writeln(2, 'TITL', url.get_description())
                    if url.get_path():
                        self.__writeln(2, 'FILE', url.get_path())

    def __write_families(self):
        sorted = []

        for family_handle in self.flist:
            family = self.db.get_family_from_handle(family_handle)
            data = (family.get_gramps_id(), family_handle, family)
            sorted.append (data)
        sorted.sort ()

        for (gramps_id, family_handle, family) in sorted:
            father_alive = mother_alive = 0
            self.__writeln(0, '@%s@' % gramps_id, 'FAM' )
            self.frefn(family)
            person_handle = family.get_father_handle()
            if (person_handle != None) and (person_handle in self.plist):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.__writeln(1, 'HUSB', '@%s@' % gramps_id)
                father_alive = Utils.probably_alive(person, self.db)

            person_handle = family.get_mother_handle()
            if (person_handle != None) and (person_handle in self.plist):
                person = self.db.get_person_from_handle(person_handle)
                gramps_id = person.get_gramps_id()
                self.__writeln(1, 'WIFE', '@%s@' % gramps_id)
                mother_alive = Utils.probably_alive(person, self.db)

            if not self.restrict or ( not father_alive and not mother_alive ):
                for lds_ord in family.get_lds_ord_list():
                    self.write_ord(lds_ord, 1)

                for event_ref in family.get_event_ref_list():
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if not event:
                        continue

                    etype = int(event.get_type())
                    val = GedcomInfo.familyConstantEvents.get(etype)

                    if val == None:
                        val = self.target_ged.gramps2tag(etype)

                    if val:
                        if (not event.get_date_object().is_empty()) \
                               or event.get_place_handle():
                            self.__writeln(1, val)
                        else:
                            self.__writeln(1, val, 'Y')

                        if event.get_type() == RelLib.EventType.MARRIAGE:
                            ftype = family.get_relationship()
                            if ftype != RelLib.FamilyRelType.MARRIED and \
                               str(ftype).strip() != "":
                                self.__writeln(2, 'TYPE', str(ftype))
                        elif event.get_description().strip() != "":
                            self.__writeln(2, 'TYPE', event.get_description())
                    else:
                        self.__writeln(1, 'EVEN')
                        the_type = str(event.get_type())
                        if the_type:
                            self.__writeln(2, 'TYPE', the_type)

                    self.dump_event_stats(event, event_ref)

            for attr in family.get_attribute_list():

                t = int(attr.get_type())
                name = GedcomInfo.familyConstantAttributes.get(t)
                value = attr.get_value().replace('\r', ' ')

                if name and name.strip():
                    self.__writeln(1, name, value)
                    continue
                else:
                    the_name = str(attr.get_type())
                    self.__writeln(1, 'EVEN')
                    if value:
                        self.__writeln(2, 'TYPE', '%s %s' % (the_name, value))
                    else:
                        self.__writeln(2, 'TYPE', the_name)

                for notehandle in attr.get_note_list():
                    self.write_note(2, notehandle)

                for srcref in attr.get_source_references():
                    self.write_source_ref(2, srcref)

            for child_ref in family.get_child_ref_list():
                if child_ref.ref not in self.plist:
                    continue
                person = self.db.get_person_from_handle(child_ref.ref)
                if not person:
                    continue
                self.__writeln(1, 'CHIL', '@%s@' % person.get_gramps_id())

            for srcref in family.get_source_references():
                self.write_source_ref(1, srcref)

            if self.images:
                photos = family.get_media_list ()
                for photo in photos:
                    self.write_photo(photo, 1)

            for notehandle in family.get_note_list():
                self.write_note(1, notehandle)

            self.write_change(1, family.get_change_time())
            self.update()

    def write_note(self, level, handle):
        note = self.db.get_note_from_handle(handle)
        self.__writeln(level, "NOTE", note.get())

    def __write_sources(self):
        sorted = []
        for handle in self.slist:
            source = self.db.get_source_from_handle(handle)
            if not source:
                continue
            data = (source.get_gramps_id(), source)
            sorted.append (data)
        sorted.sort ()

        for (source_id, source) in sorted:
            self.__writeln(0, '@%s@' % source_id, 'SOUR')
            if source.get_title():
                self.__writeln(1, 'TITL', source.get_title())

            if source.get_author():
                self.__writeln(1, "AUTH", source.get_author())

            if source.get_publication_info():
                self.__writeln(1, "PUBL", source.get_publication_info())

            if source.get_abbreviation():
                self.__writeln(1, 'ABBR', source.get_abbreviation())

            if self.images:
                photos = source.get_media_list ()
                for photo in photos:
                    self.write_photo(photo, 1)

            for reporef in source.get_reporef_list():
                self.write_reporef(reporef, 1)

            for notehandle in source.get_note_list():
                self.write_note(1, notehandle)

            self.write_change(1, source.get_change_time())
            
    def __write_repos(self):
        sorted = []
        for handle in self.rlist:
            repo = self.db.get_repository_from_handle(handle)
            repo_id = repo.get_gramps_id()
            sorted.append((repo_id, repo))

        sorted.sort()

        slist = set()
        
        for (repo_id, repo) in sorted:
            self.__writeln(0, '@%s@' % repo_id, 'REPO' )
            if repo.get_name():
                self.__writeln(1, 'NAME', repo.get_name())
            for addr in repo.get_address_list():
                self.__writeln(1, "ADDR", addr.get_street())
                if addr.get_city():
                    self.__writeln(2, 'CITY', addr.get_city())
                if addr.get_state():
                    self.__writeln(2, 'STAE', addr.get_state())
                if addr.get_postal_code():
                    self.__writeln(2, 'POST', addr.get_postal_code())
                if addr.get_country():
                    self.__writeln(2, 'CTRY', addr.get_country())
                if addr.get_phone():
                    self.__writeln(1, 'PHON', addr.get_phone())

            for notehandle in repo.get_note_list():
                self.write_note(1, notehandle)

    def write_reporef(self, reporef, level):

        if reporef.ref == None:
            return

        # Append handle to the list for exporting REPOs later
        self.rlist.add(reporef.ref)

        repo = self.db.get_repository_from_handle(reporef.ref)
        repo_id = repo.get_gramps_id()

        self.__writeln(level, 'REPO', '@%s@' % repo_id )

        for notehandle in reporef.get_note_list():
            self.write_note(level+1, notehandle)

        if reporef.get_call_number():
            self.__writeln(level+1, 'CALN', reporef.get_call_number() )
            if reporef.get_media_type():
                self.__writeln(level+2, 'MEDI', str(reporef.get_media_type()))

    def __write_person_event_ref(self, key, event_ref):

        if event_ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if (not event.get_date_object().is_empty()) \
                    or event.get_place_handle():
                self.__writeln(1, key)
            else:
                self.__writeln(1, key, 'Y')
            if event.get_description().strip() != "":
                self.__writeln(2, 'TYPE', event.get_description())
            self.dump_event_stats(event, event_ref)

    def write_change(self, level, timeval):
        self.__writeln(level, 'CHAN')
        time_val = time.localtime(timeval)
        self.__writeln(level+1, 'DATE', '%d %s %d' % (time_val[2], 
                                                      _month[time_val[1]], 
                                                      time_val[0]))
        self.__writeln(level+2, 'TIME', '%02d:%02d:%02d' % (time_val[3], 
                                                            time_val[4], 
                                                            time_val[5]))

    def dump_event_stats(self, event, event_ref):
        dateobj = event.get_date_object()
        self.print_date("2 DATE", dateobj)
        place = None

        if event.get_place_handle():
            place = self.db.get_place_from_handle(event.get_place_handle())
            self.write_place(place, 2)

        for attr in event.get_attribute_list():
            t = attr.get_type()
            if t == RelLib.AttributeType.CAUSE:
                self.__writeln(2, 'CAUS', attr.get_value())
            elif t == RelLib.AttributeType.AGENCY:
                self.__writeln(2, 'AGNC', attr.get_value())

        for attr in event_ref.get_attribute_list():
            t = attr.get_type()
            if t == RelLib.AttributeType.AGE:
                self.__writeln(2, 'AGE', attr.get_value())
            elif t == RelLib.AttributeType.FATHER_AGE:
                self.__writeln(2, 'HUSB')
                self.__writeln(3, 'AGE', attr.get_value())
            elif t == RelLib.AttributeType.MOTHER_AGE:
                self.__writeln(2, 'WIFE')
                self.__writeln(3, 'AGE', attr.get_value())

        for notehandle in event.get_note_list():
            self.write_note(2, notehandle)

        for srcref in event.get_source_references():
            self.write_source_ref(2, srcref)

        if self.images:
            photos = event.get_media_list()
            for photo in photos:
                self.write_photo(photo, 2)
            if place:
                for photo in place.get_media_list():
                    self.write_photo(photo, 2)

    def write_ord(self, ord, index):
        self.__writeln(index, lds_ord_name[ord.get_type()])
        self.print_date("%d DATE" % (index + 1), ord.get_date_object())
        if ord.get_family_handle():
            family_handle = ord.get_family_handle()
            family = self.db.get_family_from_handle(family_handle)
            if family:
                self.__writeln(index+1, 'FAMC', '@%s@' % family.get_gramps_id())
        if ord.get_temple():
            self.__writeln(index+1, 'TEMP', ord.get_temple())
        if ord.get_place_handle():
            self.write_place(
                self.db.get_place_from_handle(ord.get_place_handle()), 2)
        if ord.get_status() != RelLib.LdsOrd.STATUS_NONE:
            self.__writeln(2, 'STAT', lds_status[ord.get_status()])
        for notehandle in ord.get_note_list():
            self.write_note(index+1, notehandle)

        for srcref in ord.get_source_references():
            self.write_source_ref(index+1, srcref)

    def print_date(self, prefix, date):
        start = date.get_start_date()
        if start != RelLib.Date.EMPTY:
            cal = date.get_calendar()
            mod = date.get_modifier()
            if date.get_modifier() == RelLib.Date.MOD_SPAN:
                val = "FROM %s TO %s" % (
                    make_date(start, cal, mod), 
                    make_date(date.get_stop_date(), cal, mod))
            elif date.get_modifier() == RelLib.Date.MOD_RANGE:
                val = "BET %s AND %s" % (
                    make_date(start, cal, mod), 
                    make_date(date.get_stop_date(), cal, mod))
            else:
                val = make_date(start, cal, mod)
            self.writeln("%s %s" % (prefix, val))
        elif date.get_text():
            self.writeln("%s %s" % (prefix, self.cnvtxt(date.get_text())))

    def write_person_name(self, name, nick):
        firstname = "%s %s" % (name.get_first_name(), 
                               name.get_patronymic().strip())
        surname = name.get_surname().replace('/', '?')
        surprefix = name.get_surname_prefix().replace('/', '?')
        suffix = name.get_suffix()
        title = name.get_title()
        if suffix == "":
            if surprefix == "":
                self.__writeln(1, 'NAME', '%s/%s/' % (firstname, surname))
            else:
                self.__writeln(1, 'NAME', '%s/%s %s/' % (firstname, surprefix, surname))
        else:
            if surprefix == "":
                self.__writeln(1, 'NAME', '%s/%s/ %s' % (firstname, surname, suffix))
            else:
                self.__writeln(1, 'NAME', '%s/%s %s/ %s' % (firstname, surprefix, 
                                                            surname, suffix))

        if firstname:
            self.__writeln(2, 'GIVN', firstname)
        if self.prefix:
            if surprefix:
                self.__writeln(2, 'SPFX', surprefix)
            if surname:
                self.__writeln(2, 'SURN', surname)
        else:
            if surprefix:
                self.__writeln(2, 'SURN', '%s %s' % (surprefix, surname))
            elif surname:
                self.__writeln(2, 'SURN', surname)
                
        if name.get_suffix():
            self.__writeln(2, 'NSFX', suffix)
        if name.get_title():
            self.__writeln(2, 'NPFX', title)
        if nick:
            self.__writeln(2, 'NICK', nick)
        for notehandle in name.get_note_list():
            self.write_note(2, notehandle)
        for srcref in name.get_source_references():
            self.write_source_ref(2, srcref)

    def write_source_ref(self, level, ref):

        src_handle = ref.get_reference_handle()
       
        if src_handle == None:
            return

        src = self.db.get_source_from_handle(src_handle)

        self.slist.add(src_handle)

        already_printed = None

        # Reference to the source
        self.__writeln(level, "SOUR", "@%s@" % src.get_gramps_id())
        if ref.get_page() != "":
            sep = "\n%d CONT " % (level+2)
            page_text = self.cnvtxt(ref.get_page().replace('\n', sep))
            self.writeln('%d PAGE %s' % (level+1, page_text))
        conf = ref.get_confidence_level()
            # Cap the maximum level
        conf = min(conf, RelLib.SourceRef.CONF_VERY_HIGH)
        if conf != RelLib.SourceRef.CONF_NORMAL and conf != -1:
            self.__writeln(level+1, "QUAY", str(quay_map[conf]))

        if len(ref.get_note_list()) > 0:

            note_list = [ self.db.get_note_from_handle(h) for h in ref.get_note_list() ]
            note_list = [ n for n in note_list 
                          if n.get_type() == RelLib.NoteType.SOURCE_TEXT]

            if note_list:
                ref_text = note_list[0].get()
                already_printed = note_list[0].get_handle()
            else:
                ref_text = ""

            if ref_text != "" or not ref.get_date_object().is_empty():
                self.__writeln(level+1, 'DATA')
                if ref_text != "":
                    self.__writeln(level+1, "TEXT", ref_text)
                pfx = "%d DATE" % (level+2)
                self.print_date(pfx, ref.get_date_object())

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
            self.__writeln(level, "SOUR", txt)
            if not ref.get_date_object().is_empty():
                self.print_date("", ref.get_date_object())
            #ref_text = ref.get_text()
            #if ref_text:                
            #    self.write_long_text("TEXT", level+1, self.cnvtxt(ref_text))
 
        for notehandle in ref.get_note_list():
            if notehandle != already_printed:
                self.write_note(level+1, notehandle)

    def write_photo(self, photo, level):
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.db.get_object_from_handle(photo_obj_id)
        if photo_obj:
            mime = photo_obj.get_mime_type()
            if mime2ged.has_key(mime):
                form = mime2ged[mime]
            else:
                form = mime
            path = photo_obj.get_path ()
            imgdir = os.path.join(self.dirname, self.images_path)
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
                except (IOError, OSError), msg:
                    msg2 = _("Could not create %s") % dest
                    WarningDialog(msg2, str(msg))
                    return

            self.__writeln(level, 'OBJE')
            if form:
                self.__writeln(level+1, 'FORM', form)
            self.__writeln(level+1, 'TITL', photo_obj.get_description())
            basename = os.path.basename (path)
            self.__writeln(level+1, 'FILE', os.path.join(self.images_path, basename))
            for notehandle in photo_obj.get_note_list():
                self.write_note(level+1, notehandle)

    def write_place(self, place, level):
        place_name = place.get_title()
        self.__writeln(level, "PLAC", place_name.replace('\r', ' '))

    def frefn(self, family):
        match = _get_int.search(family.get_gramps_id())
        if match:
            self.__writeln(1, 'REFN', match.groups()[0])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, person, option_box, callback=None):
    ret = 0
    try:
        gw = GedcomWriter(database, person, 0, filename, option_box, callback)
        ret = gw.export_data(filename)
#    except AttributeError, msg:
#        RunDatabaseRepair(msg)
    except Errors.DatabaseError, msg:
        ErrorDialog(_("Export failed"), str(msg))
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('GE_DCOM')
_description = _('GEDCOM is used to transfer data between genealogy programs. '
        'Most genealogy software will accept a GEDCOM file as input. ')
_config = (_('GEDCOM export options'), GedcomWriterOptionBox)
_filename = 'ged'

from PluginUtils import register_export
register_export(exportData, _title, _description, _config, _filename)
