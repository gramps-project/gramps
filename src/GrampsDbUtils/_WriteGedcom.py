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
import Utils
from QuestionDialog import ErrorDialog, WarningDialog
from BasicUtils import UpdateCallback, name_displayer

try:
    import Config
    HAVE_CONFIG = True
except:
    log.warn("No Config module available using defaults.")
    HAVE_CONFIG = False

#-------------------------------------------------------------------------
#
# GEDCOM tags representing attributes that may take a parameter, value or
# description on the same line as the tag
#
#-------------------------------------------------------------------------
personalAttributeTakesParam = set(
    ["CAST", "DSCR", "EDUC", "IDNO", "NATI", "NCHI", 
     "NMR",  "OCCU", "PROP", "RELI", "SSN",  "TITL"])

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

LANGUAGES = {
    'cs' : 'Czech',     'da' : 'Danish',    'nl' : 'Dutch',
    'en' : 'English',   'eo' : 'Esperanto', 'fi' : 'Finnish',
    'fr' : 'French',    'de' : 'German',    'hu' : 'Hungarian',
    'it' : 'Italian',   'lt' : 'Latvian',   'lv' : 'Lithuanian',
    'no' : 'Norwegian', 'po' : 'Polish',    'pt' : 'Portuguese',
    'ro' : 'Romanian',  'sk' : 'Slovak',    'es' : 'Spanish',
    'sv' : 'Swedish',   'ru' : 'Russian',    
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
def sort_by_gramps_id(first, second):
    return cmp(first.gramps_id, second.gramps_id)

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
    """
    Breaks a line of text into a list of strings that conform to the 
    maximum length specified, while breaking words in the middle of a word
    to avoid issues with spaces.
    """
    data = []
    original = txt
    while limit < len(txt)+1:
        idx = limit-1
        while txt[idx-1] in string.whitespace or txt[idx] in string.whitespace :
            idx -= 1
        data.append(txt[:idx])
        txt = txt[idx:]
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

        glade_file = "%s/gedcomexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/gedcomexport.glade"

        self.topDialog = gtk.glade.XML(glade_file, "gedcomExport", "gramps")
        self.topDialog.signal_autoconnect({
                "on_restrict_toggled" : self.on_restrict_toggled, 
                })

        filter_obj = self.topDialog.get_widget("filter")

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

        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("gedcomExport").destroy()
        return the_box

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

        self.cfilter = self.filter_menu.get_active().get_data("filter")

        self.images = self.topDialog.get_widget ("images").get_active ()
        if self.images:
            images_path = self.topDialog.get_widget ("images_path")
            self.images_path = unicode(images_path.get_text ())
        else:
            self.images_path = ""

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
        self.nlist = set()

        # Collect needed families
        for handle in list(self.plist):
            person = self.db.get_person_from_handle(handle)
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                self.flist.add(family_handle)

    def __writeln(self, level, token, textlines="", limit=72):
        if textlines:
            textlist = textlines.split('\n')
            token_level = level
            for text in textlist:
                if limit:
                    prefix = "\n%d CONC " % (level + 1)
                    txt = prefix.join(breakup(text, limit))
                else:
                    txt = text
                self.g.write("%d %s %s\n" % (token_level, token, txt))
                token_level = level+1
                token = "CONT"
        else:
            self.g.write("%d %s\n" % (level, token))
    
    def gui_setup(self):
        # Get settings from the options store/dialog
        self.option_box.parse_options()

        self.restrict = self.option_box.restrict
        self.living = self.option_box.living
        self.exclnotes = self.option_box.exclnotes
        self.exclsrcs = self.option_box.exclsrcs
        self.images = self.option_box.images
        self.images_path = self.option_box.images_path

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
        self.images = 0

        self.plist = set(self.db.get_person_handles(sort_handles=False))

        return True

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
        self.__write_notes()

        self.__writeln(0, "TRLR")
        self.g.close()
        return 1

    def __write_header(self, filename):
        """
        Writes the GEDCOM header. 

          HEADER:=
          n HEAD {1:1}
          +1 SOUR <APPROVED_SYSTEM_ID> {1:1} 
          +2 VERS <VERSION_NUMBER> {0:1} 
          +2 NAME <NAME_OF_PRODUCT> {0:1} 
          +2 CORP <NAME_OF_BUSINESS> {0:1}           # Not used
          +3 <<ADDRESS_STRUCTURE>> {0:1}             # Not used
          +2 DATA <NAME_OF_SOURCE_DATA> {0:1}        # Not used
          +3 DATE <PUBLICATION_DATE> {0:1}           # Not used
          +3 COPR <COPYRIGHT_SOURCE_DATA> {0:1}      # Not used
          +1 DEST <RECEIVING_SYSTEM_NAME> {0:1*}     # Not used
          +1 DATE <TRANSMISSION_DATE> {0:1} 
          +2 TIME <TIME_VALUE> {0:1} 
          +1 SUBM @XREF:SUBM@ {1:1} 
          +1 SUBN @XREF:SUBN@ {0:1} 
          +1 FILE <FILE_NAME> {0:1} 
          +1 COPR <COPYRIGHT_GEDCOM_FILE> {0:1} 
          +1 GEDC {1:1}
          +2 VERS <VERSION_NUMBER> {1:1} 
          +2 FORM <GEDCOM_FORM> {1:1} 
          +1 CHAR <CHARACTER_SET> {1:1} 
          +2 VERS <VERSION_NUMBER> {0:1} 
          +1 LANG <LANGUAGE_OF_TEXT> {0:1} 
          +1 PLAC {0:1}
          +2 FORM <PLACE_HIERARCHY> {1:1} 
          +1 NOTE <GEDCOM_CONTENT_DESCRIPTION> {0:1} 
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
        self.__writeln(1, "CHAR", "UTF-8")
        
        # write the language string if the current LANG variable 
        # matches something we know about.

        lang = os.getenv('LANG')
        if lang and len(lang) >= 2:
            lang_code = LANGUAGES.get(lang[0:2])
            if lang_code:
                self.__writeln(1, 'LANG', lang_code)

    def __write_submitter(self):
        """
          n @<XREF:SUBM>@ SUBM {1:1}
          +1 NAME <SUBMITTER_NAME> {1:1} 
          +1 <<ADDRESS_STRUCTURE>> {0:1}
          +1 <<MULTIMEDIA_LINK>> {0:M}              # not used
          +1 LANG <LANGUAGE_PREFERENCE> {0:3}       # not used
          +1 RFN <SUBMITTER_REGISTERED_RFN> {0:1}   # not used
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}        # not used
          +1 <<CHANGE_DATE>> {0:1}                  # not used
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
        else:
            self.__writeln(2, "CONT", u"Not Provided")
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

        for data in sorted:
            self.__write_person(self.db.get_person_from_handle(data[1]))
            self.update()

    def __write_person(self, person):
        """
        Writes out a single person

          n @XREF:INDI@ INDI {1:1}
          +1 RESN <RESTRICTION_NOTICE> {0:1}            # not used
          +1 <<PERSONAL_NAME_STRUCTURE>> {0:M}          
          +1 SEX <SEX_VALUE> {0:1} 
          +1 <<INDIVIDUAL_EVENT_STRUCTURE>> {0:M} 
          +1 <<INDIVIDUAL_ATTRIBUTE_STRUCTURE>> {0:M} 
          +1 <<LDS_INDIVIDUAL_ORDINANCE>> {0:M} 
          +1 <<CHILD_TO_FAMILY_LINK>> {0:M} 
          +1 <<SPOUSE_TO_FAMILY_LINK>> {0:M} 
          +1 SUBM @<XREF:SUBM>@ {0:M} 
          +1 <<ASSOCIATION_STRUCTURE>> {0:M} 
          +1 ALIA @<XREF:INDI>@ {0:M} 
          +1 ANCI @<XREF:SUBM>@ {0:M} 
          +1 DESI @<XREF:SUBM>@ {0:M} 
          +1 <<SOURCE_CITATION>> {0:M} 
          +1 <<MULTIMEDIA_LINK>> {0:M} ,*
          +1 <<NOTE_STRUCTURE>> {0:M} 
          +1 RFN <PERMANENT_RECORD_FILE_NUMBER> {0:1} 
          +1 AFN <ANCESTRAL_FILE_NUMBER> {0:1} 
          +1 REFN <USER_REFERENCE_NUMBER> {0:M} 
          +2 TYPE <USER_REFERENCE_TYPE> {0:1} 
          +1 RIN <AUTOMATED_RECORD_ID> {0:1} 
          +1 <<CHANGE_DATE>> {0:1} 
        """
        self.__writeln(0, "@%s@" % person.get_gramps_id(),  "INDI")

        self.__write_names(person)
        self.__write_gender(person)
        self.__write_person_event_ref('BIRT', person.get_birth_ref())
        self.__write_person_event_ref('DEAT', person.get_death_ref())
        self.__write_remaining_events(person)
        self.__write_attributes(person)
        self.__write_lds_ords(person, 1)
        self.__write_child_families(person)
        self.__write_parent_families(person)
        self.__write_assoc(person, 1)
        self.__write_person_sources(person)
        self.__write_addresses(person)
        self.__write_photos(person.get_media_list(), 1)
        self.__write_url_list(person, 1)
        self.__write_note_references(person.get_note_list(), 1)
        self.__write_change(person.get_change_time(), 1)

    def __write_assoc(self, person, level):
        """
          n ASSO @<XREF:INDI>@ {0:M} 
          +1 TYPE <RECORD_TYPE> {1:1}
          +1 RELA <RELATION_IS_DESCRIPTOR> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M} 
          +1 <<SOURCE_CITATION>> {0:M} 
        """
        for ref in person.get_person_ref_list():
            person = self.db.get_person_from_handle(ref.ref)
            self.__writeln(level, "ASSO", "@%s@" % person.get_gramps_id())
            self.__writeln(level+1, "TYPE", ref.get_relation())
            self.__write_note_references(ref.get_note_list(), level+1)
            self.__write_source_references(ref.get_source_references, level+1)

    def __write_note_references(self, notelist, level):
        for note_handle in notelist:
            note = self.db.get_note_from_handle(note_handle)
            self.__writeln(level, 'NOTE', '@%s@' % note.get_gramps_id())
            self.nlist.add(note_handle)

    def __write_names(self, person):
        nicknames = [ attr.get_value() for attr in person.get_attribute_list()
                      if int(attr.get_type()) == RelLib.AttributeType.NICKNAME ]
        if len(nicknames) > 0:
            nickname = nicknames[0]
        else:
            nickname = ""

        self.__write_person_name(person.get_primary_name(), nickname)
        for name in person.get_alternate_names():
            self.__write_person_name(name, "")

    def __write_gender(self, person):
        if person.get_gender() == RelLib.Person.MALE:
            self.__writeln(1, "SEX", "M")
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.__writeln(1, "SEX", "F")

    def __write_lds_ords(self, obj, level):
        for lds_ord in obj.get_lds_ord_list():
            self.write_ord(lds_ord, level)

    def __write_remaining_events(self, person):

        ad = False
        for event_ref in person.get_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            etype = int(event.get_type())

            if etype in (RelLib.EventType.BIRTH, RelLib.EventType.DEATH):
                continue
                
            val = GedcomInfo.personalConstantEvents.get(etype, "")
                        
            if val and val.strip():
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
                self.__writeln(1, 'EVEN')
                if val.strip():
                    self.__writeln(2, 'TYPE', val)
                else:
                    self.__writeln(2, 'TYPE', str(event.get_type()))

            self.dump_event_stats(event, event_ref)

        self.__write_adoption_record(person)

    def __write_adoption_record(self, person):
        
        adopt_records = []

        for family in [ self.db.get_family_from_handle(fh) 
                        for fh in person.get_parent_family_handle_list() ]:
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == person.handle:
                    if child_ref.mrel == RelLib.ChildRefType.ADOPTED \
                            or child_ref.frel == RelLib.ChildRefType.ADOPTED:
                        adopt_records.append((family, child_ref.frel, child_ref.mrel))

        for (fam, frel, mrel) in adopt_records:
            self.__writeln(1, 'ADOP', 'Y')
            self.__writeln(2, 'FAMC', '@%s@' % fam.get_gramps_id())
            if mrel == frel:
                self.__writeln(3, 'ADOP', 'BOTH')
            elif mrel == RelLib.ChildRefType.ADOPTED:
                self.__writeln(3, 'ADOP', 'WIFE')
            else:
                self.__writeln(3, 'ADOP', 'HUSB')

    def __write_attributes(self, person):
        
        # filter out the Nicknames, since they have already been
        # processed.

        attr_list = [ attr for attr in person.get_attribute_list()
                      if attr.get_type() != RelLib.AttributeType.NICKNAME ]

        for attr in attr_list:

            t = int(attr.get_type())
            name = GedcomInfo.personalConstantAttributes.get(t)
            key = str(attr.get_type())
            value = attr.get_value().strip().replace('\r', ' ')
            
            if key in ("AFN", "RFN", "REFN", "_UID"):
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

            self.__write_note_references(attr.get_note_list(), 2)
            self.__write_source_references(attr.get_source_references(), 2)

    def __write_source_references(self, ref_list, level):
        for srcref in ref_list:
            self.write_source_ref(level, srcref)

    def __write_addresses(self, person):
        for addr in person.get_address_list():
            self.__writeln(1, 'RESI')
            self.print_date(2, addr.get_date_object())
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

            self.__write_note_references(addr.get_note_list(), 2)
            self.__write_source_references(addr.get_source_references(), 2)

    def __write_photos(self, media_list, level):
        if self.images:
            for photo in media_list:
                self.__write_photo(photo, level)

    def __write_child_families(self, person):
        hndl_list = [ hndl for hndl in person.get_parent_family_handle_list() \
                          if hndl and hndl in self.flist ]

        for family_handle in hndl_list:
            family = self.db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            self.__writeln(1, 'FAMC', '@%s@' % family_id)

    def __write_parent_families(self, person):
        for family_handle in person.get_family_handle_list():
            if family_handle in self.flist:
                family = self.db.get_family_from_handle(family_handle)
                self.__writeln(1, 'FAMS', '@%s@' % family.get_gramps_id())

    def __write_person_sources(self, person):
        for srcref in person.get_source_references():
            self.write_source_ref(1, srcref)

    def __write_url_list(self, obj, level):
        """
          n OBJE {1:1}
          +1 FORM <MULTIMEDIA_FORMAT> {1:1} 
          +1 TITL <DESCRIPTIVE_TITLE> {0:1} 
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
        """
        for url in obj.get_url_list():
            self.__writeln(level, 'OBJE')
            self.__writeln(level+1, 'FORM', 'URL')
            if url.get_description():
                self.__writeln(level+1, 'TITL', url.get_description())
            if url.get_path():
                self.__writeln(level+1, 'FILE', url.get_path())

    def __write_families(self):
        sorted = []

        for family_handle in self.flist:
            family = self.db.get_family_from_handle(family_handle)
            data = (family.get_gramps_id(), family_handle)
            sorted.append (data)
        sorted.sort ()

        for (gramps_id, family_handle) in sorted:
            family = self.db.get_family_from_handle(family_handle)
            self.__write_family(family)

    def __write_family_reference(self, token, person_handle):
        if person_handle != None and person_handle in self.plist:
            person = self.db.get_person_from_handle(person_handle)
            gramps_id = person.get_gramps_id()
            self.__writeln(1, token, '@%s@' % gramps_id)
            return Utils.probably_alive(person, self.db)

    def __write_family(self, family):

        gramps_id = family.get_gramps_id()
        family_handle = family.get_handle()

        self.__writeln(0, '@%s@' % gramps_id, 'FAM' )

        self.__write_family_reference('HUSB', family.get_father_handle())
        self.__write_family_reference('WIFE', family.get_mother_handle())

        self.__write_lds_ords(family, 1)
        self.__write_family_events(family)

        self.__write_family_attributes(family.get_attribute_list(), 1)

        
        child_list = [ self.db.get_person_from_handle(cref.ref).get_gramps_id()
                       for cref in family.get_child_ref_list() 
                       if cref.ref in self.plist]
        child_list.sort()

        for gid in child_list:
            self.__writeln(1, 'CHIL', '@%s@' % gid)

        self.__write_source_references(family.get_source_references(), 1)
        self.__write_photos(family.get_media_list(), 1)
        self.__write_note_references(family.get_note_list(), 1)
        self.__write_change(family.get_change_time(), 1)
        self.update()

    def __write_family_events(self, family):

        for event_ref in [ ref for ref in family.get_event_ref_list()]:
            event = self.db.get_event_from_handle(event_ref.ref)
            if not event:
                continue

            etype = int(event.get_type())
            val = GedcomInfo.familyConstantEvents.get(etype)
            
            if val:
                if (not event.get_date_object().is_empty()) \
                        or event.get_place_handle():
                    self.__writeln(1, val)
                else:
                    self.__writeln(1, val, 'Y')

                if event.get_type() == RelLib.EventType.MARRIAGE:
                    ftype = family.get_relationship()
                    if ftype != RelLib.FamilyRelType.MARRIED and str(ftype):
                        self.__writeln(2, 'TYPE', str(ftype))

                    self.__write_family_event_attrs(event.get_attribute_list(), 2) 
                elif event.get_description().strip() != "":
                    self.__writeln(2, 'TYPE', event.get_description())
            else:
                self.__writeln(1, 'EVEN')
                the_type = str(event.get_type())
                if the_type:
                    self.__writeln(2, 'TYPE', the_type)

            self.dump_event_stats(event, event_ref)


    def __write_family_event_attrs(self, attr_list, level):
        for attr in attr_list:
            if attr.get_type() == RelLib.AttributeType.FATHER_AGE:
                self.__writeln(level, 'HUSB')
                self.__writeln(level+1, 'AGE', attr.get_value())
            elif attr.get_type() == RelLib.AttributeType.MOTHER_AGE:
                self.__writeln(level, 'WIFE')
                self.__writeln(level+1, 'AGE', attr.get_value())

    def __write_family_attributes(self, attr_list, level):

        for attr in attr_list:
            
            t = int(attr.get_type())
            name = GedcomInfo.familyConstantAttributes.get(t)
            value = attr.get_value().replace('\r', ' ')

            if t in ("AFN", "RFN", "REFN", "_UID"):
                self.__writeln(1, t, value)
                continue
            
            if name and name.strip():
                self.__writeln(1, name, value)
                continue
            else:
                the_name = str(attr.get_type())
                self.__writeln(level, 'EVEN')
                if value:
                    self.__writeln(level+1, 'TYPE', '%s %s' % (the_name, value))
                else:
                    self.__writeln(level+1, 'TYPE', the_name)

            self.__write_note_references(attr.get_note_list(), level+1)
            self.__write_source_references(attr.get_source_references(), level+1)

    def __write_sources(self):
        sorted = []
        for handle in self.slist:
            source = self.db.get_source_from_handle(handle)
            if not source:
                continue
            data = (source.get_gramps_id(), handle)
            sorted.append (data)
        sorted.sort ()

        for (source_id, handle) in sorted:
            source = self.db.get_source_from_handle(handle)
            self.__writeln(0, '@%s@' % source_id, 'SOUR')
            if source.get_title():
                self.__writeln(1, 'TITL', source.get_title())

            if source.get_author():
                self.__writeln(1, "AUTH", source.get_author())

            if source.get_publication_info():
                self.__writeln(1, "PUBL", source.get_publication_info())

            if source.get_abbreviation():
                self.__writeln(1, 'ABBR', source.get_abbreviation())

            self.__write_photos(source.get_media_list(), 1)

            for reporef in source.get_reporef_list():
                self.write_reporef(reporef, 1)
                break

            self.__write_note_references(source.get_note_list(), 1)
            self.__write_change(source.get_change_time(), 1)

    def __write_notes(self):
        sorted = []
        for handle in self.nlist:
            note = self.db.get_note_from_handle(handle)
            data = (note.get_gramps_id(), handle)
            sorted.append (data)
        sorted.sort ()

        for (node_id, note_handle) in sorted:
            note = self.db.get_note_from_handle(note_handle)
            self.__write_note_record(note)
            
    def __write_note_record(self, note):
        """
          n @<XREF:NOTE>@ NOTE <SUBMITTER_TEXT> {1:1} 
          +1 [ CONC | CONT] <SUBMITTER_TEXT> {0:M}
          +1 <<SOURCE_CITATION>> {0:M} 
          +1 REFN <USER_REFERENCE_NUMBER> {0:M} 
          +2 TYPE <USER_REFERENCE_TYPE> {0:1} 
          +1 RIN <AUTOMATED_RECORD_ID> {0:1} 
          +1 <<CHANGE_DATE>> {0:1} 
        """

        self.__writeln(0, '@%s@' % note.get_gramps_id(),  'NOTE ' + note.get())

    def __write_repos(self):
        sorted = []
        for handle in self.rlist:
            repo = self.db.get_repository_from_handle(handle)
            repo_id = repo.get_gramps_id()
            sorted.append((repo_id, handle))

        sorted.sort()

        slist = set()

        # GEDCOM only allows for a single repository per source

        for (repo_id, handle) in sorted:
            repo = self.db.get_repository_from_handle(handle)
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
            self.__write_note_references(repo.get_note_list(), 1)

    def write_reporef(self, reporef, level):

        if reporef.ref == None:
            return

        # Append handle to the list for exporting REPOs later
        self.rlist.add(reporef.ref)

        repo = self.db.get_repository_from_handle(reporef.ref)
        repo_id = repo.get_gramps_id()

        self.__writeln(level, 'REPO', '@%s@' % repo_id )

        self.__write_note_references(reporef.get_note_list(), level+1)

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

    def __write_change(self, timeval, level):
        self.__writeln(level, 'CHAN')
        time_val = time.localtime(timeval)
        self.__writeln(level+1, 'DATE', '%d %s %d' % (
                time_val[2], _month[time_val[1]], time_val[0]))
        self.__writeln(level+2, 'TIME', '%02d:%02d:%02d' % (
                time_val[3], time_val[4], time_val[5]))

    def dump_event_stats(self, event, event_ref):
        dateobj = event.get_date_object()
        self.print_date(2, dateobj)
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

        self.__write_note_references(event.get_note_list(), 1)
        self.__write_source_references(event.get_source_references(), 2)

        if self.images:
            self.__write_photos(event.get_media_list(), 2)
            if place:
                self.__write_photos(place.get_media_list(), 2)

    def write_ord(self, ord, index):
        self.__writeln(index, lds_ord_name[ord.get_type()])
        self.print_date(index + 1, ord.get_date_object())
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
        
        self.__write_note_references(ord.get_note_list(), index+1)
        self.__write_source_references(ord.get_source_references(), index+1)

    def print_date(self, level, date):
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
            self.__writeln(level, 'DATE', val)
        elif date.get_text():
            self.__writeln(level, 'DATE', date.get_text())

    def __write_person_name(self, name, nick):
        """
          n NAME <NAME_PERSONAL> {1:1} 
          +1 NPFX <NAME_PIECE_PREFIX> {0:1} 
          +1 GIVN <NAME_PIECE_GIVEN> {0:1} 
          +1 NICK <NAME_PIECE_NICKNAME> {0:1} 
          +1 SPFX <NAME_PIECE_SURNAME_PREFIX {0:1} 
          +1 SURN <NAME_PIECE_SURNAME> {0:1} 
          +1 NSFX <NAME_PIECE_SUFFIX> {0:1} 
          +1 <<SOURCE_CITATION>> {0:M} 
          +1 <<NOTE_STRUCTURE>> {0:M} 
        """
        firstname = name.get_first_name().strip()
        patron = name.get_patronymic().strip()
        if patron:
            firstname = "%s %s" % (first, patron)

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
        if surprefix:
            self.__writeln(2, 'SPFX', surprefix)
        if surname:
            self.__writeln(2, 'SURN', surname)
                
        if name.get_suffix():
            self.__writeln(2, 'NSFX', suffix)
        if name.get_title():
            self.__writeln(2, 'NPFX', title)
        if nick:
            self.__writeln(2, 'NICK', nick)

        self.__write_source_references(name.get_source_references(), 2)
        self.__write_note_references(name.get_note_list(), 2)

    def write_source_ref(self, level, ref):
        """
          n SOUR @<XREF:SOUR>@ /* pointer to source record */ {1:1} 
          +1 PAGE <WHERE_WITHIN_SOURCE> {0:1} 
          +1 EVEN <EVENT_TYPE_CITED_FROM> {0:1} 
          +2 ROLE <ROLE_IN_EVENT> {0:1} 
          +1 DATA {0:1}
          +2 DATE <ENTRY_RECORDING_DATE> {0:1} 
          +2 TEXT <TEXT_FROM_SOURCE> {0:M} 
          +3 [ CONC | CONT ] <TEXT_FROM_SOURCE> {0:M}
          +1 QUAY <CERTAINTY_ASSESSMENT> {0:1} 
          +1 <<MULTIMEDIA_LINK>> {0:M} ,*
          +1 <<NOTE_STRUCTURE>> {0:M} 
        """

        src_handle = ref.get_reference_handle()
        if src_handle == None:
            return

        src = self.db.get_source_from_handle(src_handle)
        self.slist.add(src_handle)

        # Reference to the source
        self.__writeln(level, "SOUR", "@%s@" % src.get_gramps_id())
        if ref.get_page() != "":
            self.__writeln(level+1, 'PAGE', ref.get_page())

        conf = min(ref.get_confidence_level(), RelLib.SourceRef.CONF_VERY_HIGH)
        if conf != RelLib.SourceRef.CONF_NORMAL and conf != -1:
            self.__writeln(level+1, "QUAY", str(quay_map[conf]))

        if len(ref.get_note_list()) > 0:

            note_list = [ self.db.get_note_from_handle(h) for h in ref.get_note_list() ]
            note_list = [ n for n in note_list 
                          if n.get_type() == RelLib.NoteType.SOURCE_TEXT]

            if note_list:
                ref_text = note_list[0].get()
            else:
                ref_text = ""

            if ref_text != "" or not ref.get_date_object().is_empty():
                self.__writeln(level+1, 'DATA')
                if ref_text != "":
                    self.__writeln(level+2, "TEXT", ref_text)
                self.print_date(level+2, ref.get_date_object())

            note_list = [ self.db.get_note_from_handle(h) for h in ref.get_note_list() ]
            note_list = [ n.handle for n in note_list 
                          if n.get_type() != RelLib.NoteType.SOURCE_TEXT]
            self.__write_note_references(note_list, level+1)

    def __write_photo(self, photo, level):
        """
          n OBJE {1:1}
          +1 FORM <MULTIMEDIA_FORMAT> {1:1} 
          +1 TITL <DESCRIPTIVE_TITLE> {0:1} 
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
        """
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.db.get_object_from_handle(photo_obj_id)
        if photo_obj:
            mime = photo_obj.get_mime_type()
            form = mime2ged.get(mime, mime)
            path = photo_obj.get_path()
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

            self.__write_note_references(photo_obj.get_note_list(), level+1)

    def write_place(self, place, level):
        place_name = place.get_title()
        self.__writeln(level, "PLAC", place_name.replace('\r', ' '))

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
