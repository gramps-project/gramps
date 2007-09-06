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
import string

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import _GedcomInfo as GedcomInfo
import Errors
import ExportOptions
import BasicUtils
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# GEDCOM tags representing attributes that may take a parameter, value or
# description on the same line as the tag
#
#-------------------------------------------------------------------------
NEEDS_PARAMETER = set(
    ["CAST", "DSCR", "EDUC", "IDNO", "NATI", "NCHI", 
     "NMR",  "OCCU", "PROP", "RELI", "SSN",  "TITL"])

#-------------------------------------------------------------------------
#
# Calendar month names
#
#-------------------------------------------------------------------------
 
HMONTH = [
    "", "ELUL", "TSH", "CSH", "KSL", "TVT", "SHV", "ADR", 
    "ADS", "NSN", "IYR", "SVN", "TMZ", "AAV", "ELL" ]

FMONTH = [
    "",     "VEND", "BRUM", "FRIM", "NIVO", "PLUV", "VENT", 
    "GERM", "FLOR", "PRAI", "MESS", "THER", "FRUC", "COMP"]

MONTH = [
    "",    "JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]

CALENDAR_MAP = {
    RelLib.Date.CAL_HEBREW : (HMONTH, '@#DHEBREW@'), 
    RelLib.Date.CAL_FRENCH : (FMONTH, '@#DFRENCH R@'), 
    RelLib.Date.CAL_JULIAN : (MONTH, '@#DJULIAN@'), 
    }

DATE_MODIFIER = {
    RelLib.Date.MOD_ABOUT : "ABT", 
    RelLib.Date.MOD_BEFORE : "BEF", 
    RelLib.Date.MOD_AFTER : "AFT", 
    }

LDS_ORD_NAME = {
    RelLib.LdsOrd.BAPTISM         : 'BAPL', 
    RelLib.LdsOrd.ENDOWMENT       : 'ENDL', 
    RelLib.LdsOrd.SEAL_TO_PARENTS : 'SLGC', 
    RelLib.LdsOrd.SEAL_TO_SPOUSE  : 'SGLS', 
    RelLib.LdsOrd.CONFIRMATION    : 'CONL', 
    }

LDS_STATUS = {
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

MIME2GED = {
    "image/bmp"   : "bmp", 
    "image/gif"   : "gif", 
    "image/jpeg"  : "jpeg", 
    "image/x-pcx" : "pcx", 
    "image/tiff"  : "tiff", 
    "audio/x-wav" : "wav"
    }

QUALITY_MAP = {
    RelLib.SourceRef.CONF_VERY_HIGH : "3", 
    RelLib.SourceRef.CONF_HIGH      : "2", 
    RelLib.SourceRef.CONF_LOW       : "1", 
    RelLib.SourceRef.CONF_VERY_LOW  : "0", 
    }

#-------------------------------------------------------------------------
#
# sort_by_gramps_id
#
#-------------------------------------------------------------------------
def sort_by_gramps_id(first, second):
    """
    Sorts objects by their GRAMPS ID
    """
    return cmp(first.gramps_id, second.gramps_id)

def sort_handles_by_id(handle_list, handle_to_object):
    """
    Sorts a list of handles by the GRAMPS ID. The function that returns the
    object from the handle needs to be supplied so that we get the right 
    object.
    """
    sorted_list = []
    for handle in handle_list:
        obj = handle_to_object(handle)
        data = (obj.get_gramps_id(), handle)
        sorted_list.append (data)
    sorted_list.sort()
    return sorted_list

#-------------------------------------------------------------------------
#
# make_date
#
#-------------------------------------------------------------------------
def make_date(subdate, calendar, mode):
    """
    Converts a GRAMPS date structure into a GEDCOM compatible date
    """
    retval = ""
    (day, mon, year) = subdate[0:3]
    
    (mmap, prefix) = CALENDAR_MAP.get(calendar, (MONTH, ""))

    if year < 0:
        year = -year
        bce = " B.C."
    else:
        bce = ""

    try:
        if day == 0:
            if mon == 0:
                retval = '%d%s' % (year, bce)
            elif year == 0:
                retval = '(%s)' % mmap[mon]
            else:
                retval = "%s %d%s" % (mmap[mon], year, bce)
        elif mon == 0:
            retval = '%d%s' % (year, bce)
        else:
            month = mmap[mon]
            if year == 0:
                retval = "(%d %s)" % (day, month)
            else:
                retval = "%d %s %d%s" % (day, month, year, bce)
    except IndexError:
        print "Month index error - %d" % mon
        retval = "%d%s" % (year, bce)

    if prefix:
        retval = "%s %s" % (prefix, retval)

    if DATE_MODIFIER.has_key(mode):
        retval = "%s %s"  % (DATE_MODIFIER[mode], retval)
        
    return retval

#-------------------------------------------------------------------------
#
# breakup
#
#-------------------------------------------------------------------------
def breakup(txt, limit):
    """
    Breaks a line of text into a list of strings that conform to the 
    maximum length specified, while breaking words in the middle of a word
    to avoid issues with spaces.
    """
    data = []
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
# GedcomWriter class
#
#-------------------------------------------------------------------------
class GedcomWriter(BasicUtils.UpdateCallback):
    """
    The GEDCOM writer creates a GEDCOM file that contains the exported 
    information from the database. It derives from BasicUtils.UpdateCallback
    so that it can provide visual feedback via a progress bar if needed.
    """

    def __init__(self, database, person, cmd_line=0,
                 option_box=None, callback=None):
        BasicUtils.UpdateCallback.__init__(self, callback)

        self.dbase = database
        self.person = person
        self.cmd_line = cmd_line
        self.dirname = None
        self.gedcom_file = None
        
        self.slist = set()
        self.rlist = set()
        self.nlist = set()

        self.setup(option_box)

    def setup(self, option_box):
        """
        If the option_box is present (GUI interface), then we check the
        "private", "restrict", and "cfilter" arguments to see if we need
        to apply proxy databases.
        """
        if option_box:

            option_box.parse_options()

            # If the private flag is set, apply the PrivateProxyDb
            if option_box.private:
                from _PrivateProxyDb import PrivateProxyDb
                self.dbase = PrivateProxyDb(self.dbase)

            # If the restrict flag is set, apply the LivingProxyDb
            if option_box.restrict:
                from _LivingProxyDb import LivingProxyDb
                self.dbase = LivingProxyDb(self.dbase, 
                                           LivingProxyDb.MODE_RESTRICT)

            # If the filter returned by cfilter is not empty, apply the 
            # FilterProxyDb
            if not option_box.cfilter.is_empty():
                from _FilterProxyDb import FilterProxyDb
                self.dbase = FilterProxyDb(self.dbase, option_box.cfilter)

    def write_gedcom_file(self, filename):
        """
        Writes the actual GEDCOM file to the specfied filename
        """

        self.dirname = os.path.dirname (filename)
        self.gedcom_file = open(filename, "w")

        self.__header(filename)
        self.__submitter()
        self.__individuals()
        self.__families()
        self.__sources()
        self.__repos()
        self.__notes()

        self.__writeln(0, "TRLR")
        self.gedcom_file.close()
        return 1

    def __writeln(self, level, token, textlines="", limit=72):
        """
        Writes a line of text to the output file in the form of:

          LEVEL TOKEN text

        If the line contains newlines, it is broken into multiple lines using
        the CONT token. If any line is greater than the limit, it will broken
        into multiple lines using CONC.
        """

        assert(token)

        if textlines:
            # break the line into multiple lines if a newline is found
            textlist = textlines.split('\n')
            token_level = level
            for text in textlist:
                if limit:
                    prefix = "\n%d CONC " % (level + 1)
                    txt = prefix.join(breakup(text, limit))
                else:
                    txt = text
                self.gedcom_file.write("%d %s %s\n" % (token_level, token, txt))
                token_level = level + 1
                token = "CONT"
        else:
            self.gedcom_file.write("%d %s\n" % (level, token))
    
    def __header(self, filename):
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
        local_time = time.localtime(time.time())
        (year, mon, day, hour, minutes, sec) = local_time[0:6]
        date_str = "%d %s %d" % (day, MONTH[mon], year)
        time_str = "%02d:%02d:%02d" % (hour, minutes, sec)
        rname = self.dbase.get_researcher().get_name()

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

    def __submitter(self):
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
        owner = self.dbase.get_researcher()
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
        if mail:
            self.__writeln(1, "EMAIL", mail)

    def __individuals(self):
        """
        Writes the individual people to the gedcom file. Since people like to 
        have the list sorted by ID value, we need to go through a sorting step.
        We need to reset the progress bar, otherwise, people will be confused
        when the progress bar is idle.
        """
        phandles = self.dbase.get_person_handles()

        hcnt = len(phandles)

        self.reset(_("Sorting"))
        self.set_total(hcnt)
        sorted_list = []
        for handle in phandles:
            person = self.dbase.get_person_from_handle(handle)
            data = (person.get_gramps_id(), handle)
            sorted_list.append(data)
            self.update()
        sorted_list.sort()

        self.set_total(hcnt + len(self.dbase.get_family_handles()))
        self.reset(_("Writing"))
        for data in sorted_list:
            self.__person(self.dbase.get_person_from_handle(data[1]))
            self.update()

    def __person(self, person):
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

        self.__names(person)
        self.__gender(person)
        self.__person_event_ref('BIRT', person.get_birth_ref())
        self.__person_event_ref('DEAT', person.get_death_ref())
        self.__remaining_events(person)
        self.__attributes(person)
        self.__lds_ords(person, 1)
        self.__child_families(person)
        self.__parent_families(person)
        self.__assoc(person, 1)
        self.__person_sources(person)
        self.__addresses(person)
        self.__photos(person.get_media_list(), 1)
        self.__url_list(person, 1)
        self.__note_references(person.get_note_list(), 1)
        self.__change(person.get_change_time(), 1)

    def __assoc(self, person, level):
        """
          n ASSO @<XREF:INDI>@ {0:M} 
          +1 TYPE <RECORD_TYPE> {1:1}
          +1 RELA <RELATION_IS_DESCRIPTOR> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M} 
          +1 <<SOURCE_CITATION>> {0:M} 
        """
        for ref in person.get_person_ref_list():
            person = self.dbase.get_person_from_handle(ref.ref)
            self.__writeln(level, "ASSO", "@%s@" % person.get_gramps_id())
            self.__writeln(level+1, "TYPE", ref.get_relation())
            self.__note_references(ref.get_note_list(), level+1)
            self.__source_references(ref.get_source_references, level+1)

    def __note_references(self, notelist, level):
        """
        Write out the list of note handles to the current level. We use the
        GRAMPS ID as the XREF for the GEDCOM file.

        Add the note_handle to the nlist set so what we know which notes to 
        write to the output GEDCOM file.
        """
        for note_handle in notelist:
            note = self.dbase.get_note_from_handle(note_handle)
            self.__writeln(level, 'NOTE', '@%s@' % note.get_gramps_id())
            self.nlist.add(note_handle)

    def __names(self, person):
        """
        Write the names associated with the person to the current level. 
        Since nicknames are now separate from the name structure, we search
        the attribute list to see if we can find a nickname. Because we do
        not know the mappings, we just take the first nickname we find, and 
        add it to the primary name.

        All other names are assumed to not  have a nickname, even if other 
        nicknames exist in the attribute list.
        """
        nicknames = [ attr.get_value() for attr in person.get_attribute_list()
                      if int(attr.get_type()) == RelLib.AttributeType.NICKNAME ]
        if len(nicknames) > 0:
            nickname = nicknames[0]
        else:
            nickname = ""

        self.__person_name(person.get_primary_name(), nickname)
        for name in person.get_alternate_names():
            self.__person_name(name, "")

    def __gender(self, person):
        """
        Writes out the gender of the person to the file. If the gender is not
        male or female, simply do not output anything. The only valid values are
        M (male) or F (female). So if the geneder is unknown, we output nothing.
        """
        if person.get_gender() == RelLib.Person.MALE:
            self.__writeln(1, "SEX", "M")
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.__writeln(1, "SEX", "F")

    def __lds_ords(self, obj, level):
        """
        Simply loop through the list of LDS ordinances, and call the function 
        that write the LDS oridinance structure.
        """
        for lds_ord in obj.get_lds_ord_list():
            self.write_ord(lds_ord, level)

    def __remaining_events(self, person):
        """
        Output all events associated with the person that are not BIRTH or
        DEATH events. Because all we have are event references, we have to
        extract the real event to discover the event type.
        """
        for event_ref in person.get_event_ref_list():
            event = self.dbase.get_event_from_handle(event_ref.ref)
            etype = int(event.get_type())

            # if the event is a birth or death, skip it.
            if etype in (RelLib.EventType.BIRTH, RelLib.EventType.DEATH):
                continue
                
            val = GedcomInfo.personalConstantEvents.get(etype, "").strip()
                        
            if val and val.strip():
                if val in NEEDS_PARAMETER:
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
                descr = event.get_description()
                if descr:
                    self.__writeln(2, 'NOTE', "Description: " + descr)
            self.dump_event_stats(event, event_ref)

        self.__adoption_records(person)

    def __adoption_records(self, person):
        
        adoptions = []

        for family in [ self.dbase.get_family_from_handle(fh) 
                        for fh in person.get_parent_family_handle_list() ]:
            for child_ref in [ ref for ref in family.get_child_ref_list()
                               if ref.ref == person.handle ]:
                if child_ref.mrel == RelLib.ChildRefType.ADOPTED \
                        or child_ref.frel == RelLib.ChildRefType.ADOPTED:
                    adoptions.append((family, child_ref.frel, child_ref.mrel))

        for (fam, frel, mrel) in adoptions:
            self.__writeln(1, 'ADOP', 'Y')
            self.__writeln(2, 'FAMC', '@%s@' % fam.get_gramps_id())
            if mrel == frel:
                self.__writeln(3, 'ADOP', 'BOTH')
            elif mrel == RelLib.ChildRefType.ADOPTED:
                self.__writeln(3, 'ADOP', 'WIFE')
            else:
                self.__writeln(3, 'ADOP', 'HUSB')

    def __attributes(self, person):
        """
        Writes out the attributes to the GEDCOM file. Since we have already
        looked at nicknames when we generated the names, we filter them out 
        here.

        We use the GEDCOM 5.5.1 FACT command to write out attributes not
        built in to GEDCOM.
        """
        
        # filter out the nicknames
        attr_list = [ attr for attr in person.get_attribute_list()
                      if attr.get_type() != RelLib.AttributeType.NICKNAME ]

        for attr in attr_list:

            attr_type = int(attr.get_type())
            name = GedcomInfo.personalConstantAttributes.get(attr_type)
            key = str(attr.get_type())
            value = attr.get_value().strip().replace('\r', ' ')
            
            if key in ("AFN", "RFN", "REFN", "_UID"):
                self.__writeln(1, key, value)
                continue

            if key == "RESN":
                self.__writeln(1, 'RESN')
                continue

            if name and name.strip():
                self.__writeln(1, name, value)
            elif value:
                self.__writeln(1, 'FACT', value)
                self.__writeln(2, 'TYPE', key)
            else:
                continue
            self.__note_references(attr.get_note_list(), 2)
            self.__source_references(attr.get_source_references(), 2)

    def __source_references(self, ref_list, level):
        """
        Loop through the list of source references, writing the information
        to the file.
        """
        for srcref in ref_list:
            self.__source_ref_record(level, srcref)

    def __addresses(self, person):
        """
        Write out the addresses associated with the person as RESI events.
        """
        for addr in person.get_address_list():
            self.__writeln(1, 'RESI')
            self.__date(2, addr.get_date_object())
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

            self.__note_references(addr.get_note_list(), 2)
            self.__source_references(addr.get_source_references(), 2)

    def __photos(self, media_list, level):
        """
        Loop through the list of media objects, writing the information
        to the file.
        """
        for photo in media_list:
            self.__photo(photo, level)

    def __child_families(self, person):
        """
        Write the GRAMPS ID as the XREF for each family in which the person
        is listed as a child.
        """
        
        # get the list of familes from the handle list
        family_list = [ self.dbase.get_family_from_handle(hndl)
                        for hndl in person.get_parent_family_handle_list() ]

        for family in family_list:
            self.__writeln(1, 'FAMC', '@%s@' % family.get_gramps_id())

    def __parent_families(self, person):
        """
        Write the GRAMPS ID as the XREF for each family in which the person
        is listed as a parent.
        """

        # get the list of familes from the handle list
        family_list = [ self.dbase.get_family_from_handle(hndl)
                        for hndl in person.get_family_handle_list() ]

        for family in family_list:
            self.__writeln(1, 'FAMS', '@%s@' % family.get_gramps_id())

    def __person_sources(self, person):
        """
        Loop through the list of source references, writing the information
        to the file.
        """
        for srcref in person.get_source_references():
            self.__source_ref_record(1, srcref)

    def __url_list(self, obj, level):
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

    def __families(self):
        """
        Writes out the list of families, sorting by GRAMPS ID
        """

        # generate a list of (GRAMPS_ID, HANDLE) pairs. This list
        # can then be sorted by the sort routine, which will use the
        # first value of the tuple as the sort key. 
        sorted_list = sort_handles_by_id(self.dbase.get_family_handles(),
                                         self.dbase.get_family_from_handle)

        # loop through the sorted list, pulling of the handle. This list
        # has already been sorted by GRAMPS_ID
        for family_handle in [hndl[1] for hndl in sorted_list]:
            self.__family(self.dbase.get_family_from_handle(family_handle))

    def __family(self, family):
        """
           n @<XREF:FAM>@ FAM {1:1}
          +1 RESN <RESTRICTION_NOTICE> {0:1)
          +1 <<FAMILY_EVENT_STRUCTURE>> {0:M} 
          +1 HUSB @<XREF:INDI>@ {0:1}
          +1 WIFE @<XREF:INDI>@ {0:1}
          +1 CHIL @<XREF:INDI>@ {0:M}
          +1 NCHI <COUNT_OF_CHILDREN> {0:1}
          +1 SUBM @<XREF:SUBM>@ {0:M}
          +1 <<LDS_SPOUSE_SEALING>> {0:M}
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
        """
        gramps_id = family.get_gramps_id()

        self.__writeln(0, '@%s@' % gramps_id, 'FAM' )

        self.__family_reference('HUSB', family.get_father_handle())
        self.__family_reference('WIFE', family.get_mother_handle())

        self.__lds_ords(family, 1)
        self.__family_events(family)
        self.__family_attributes(family.get_attribute_list(), 1)
        self.__family_child_list(family.get_child_ref_list())
        self.__source_references(family.get_source_references(), 1)
        self.__photos(family.get_media_list(), 1)
        self.__note_references(family.get_note_list(), 1)
        self.__change(family.get_change_time(), 1)
        self.update()

    def __family_child_list(self, child_ref_list):
        """
        Write the child XREF values to the GEDCOM file. Sorts the child
        list by ID value before writing.
        """

        # sort the childlist by GRAMPS ID
        child_list = [ 
            self.dbase.get_person_from_handle(cref.ref).get_gramps_id()
            for cref in child_ref_list ]
        child_list.sort()

        for gid in child_list:
            self.__writeln(1, 'CHIL', '@%s@' % gid)

    def __family_reference(self, token, person_handle):
        """
        Write the family reference to the file. This is either 'WIFE' or
        'HUSB'. As usual, we use the GRAMPS ID as the XREF value.
        """
        if person_handle:
            person = self.dbase.get_person_from_handle(person_handle)
            self.__writeln(1, token, '@%s@' % person.get_gramps_id())

    def __family_events(self, family):

        for event_ref in [ ref for ref in family.get_event_ref_list()]:
            event = self.dbase.get_event_from_handle(event_ref.ref)
            etype = int(event.get_type())
            val = GedcomInfo.familyConstantEvents.get(etype)
            
            if val:
                if (not event.get_date_object().is_empty() 
                    or event.get_place_handle()):
                    self.__writeln(1, val)
                else:
                    self.__writeln(1, val, 'Y')

                if event.get_type() == RelLib.EventType.MARRIAGE:
                    ftype = family.get_relationship()
                    if ftype != RelLib.FamilyRelType.MARRIED and str(ftype):
                        self.__writeln(2, 'TYPE', str(ftype))

                    self.__family_event_attrs(event.get_attribute_list(), 2) 
                elif event.get_description().strip() != "":
                    self.__writeln(2, 'TYPE', event.get_description())
            else:
                self.__writeln(1, 'EVEN')
                the_type = str(event.get_type())
                if the_type:
                    self.__writeln(2, 'TYPE', the_type)
                descr = event.get_description()
                if descr:
                    self.__writeln(2, 'NOTE', "Description: " + descr)

            self.dump_event_stats(event, event_ref)

    def __family_event_attrs(self, attr_list, level):
        for attr in attr_list:
            if attr.get_type() == RelLib.AttributeType.FATHER_AGE:
                self.__writeln(level, 'HUSB')
                self.__writeln(level+1, 'AGE', attr.get_value())
            elif attr.get_type() == RelLib.AttributeType.MOTHER_AGE:
                self.__writeln(level, 'WIFE')
                self.__writeln(level+1, 'AGE', attr.get_value())

    def __family_attributes(self, attr_list, level):

        for attr in attr_list:
            
            attr_type = int(attr.get_type())
            name = GedcomInfo.familyConstantAttributes.get(attr_type)
            value = attr.get_value().replace('\r', ' ')

            if attr_type in ("AFN", "RFN", "REFN", "_UID"):
                self.__writeln(1, attr_type, value)
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

            self.__note_references(attr.get_note_list(), level+1)
            self.__source_references(attr.get_source_references(), 
                                           level+1)

    def __sources(self):
        """
        Writes out the list of sources, sorting by GRAMPS ID
        """
        sorted_list = sort_handles_by_id(self.slist, 
                                         self.dbase.get_source_from_handle)

        for (source_id, handle) in sorted_list:
            source = self.dbase.get_source_from_handle(handle)
            self.__writeln(0, '@%s@' % source_id, 'SOUR')
            if source.get_title():
                self.__writeln(1, 'TITL', source.get_title())

            if source.get_author():
                self.__writeln(1, "AUTH", source.get_author())

            if source.get_publication_info():
                self.__writeln(1, "PUBL", source.get_publication_info())

            if source.get_abbreviation():
                self.__writeln(1, 'ABBR', source.get_abbreviation())

            self.__photos(source.get_media_list(), 1)

            for reporef in source.get_reporef_list():
                self.__reporef(reporef, 1)
                break

            self.__note_references(source.get_note_list(), 1)
            self.__change(source.get_change_time(), 1)

    def __notes(self):
        """
        Writes out the list of notes, sorting by GRAMPS ID
        """
        sorted_list = sort_handles_by_id(self.nlist,
                                         self.dbase.get_note_from_handle)

        for note_handle in [hndl[1] for hndl in sorted_list]:
            note = self.dbase.get_note_from_handle(note_handle)
            self.__note_record(note)
            
    def __note_record(self, note):
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

    def __repos(self):
        """
        Writes out the list of repositories, sorting by GRAMPS ID

        REPOSITORY_RECORD:=
           n @<XREF:REPO>@ REPO {1:1}
          +1 NAME <NAME_OF_REPOSITORY> {1:1}
          +1 <<ADDRESS_STRUCTURE>> {0:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
          +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<CHANGE_DATE>> {0:1}
        """
        sorted_list = sort_handles_by_id(self.rlist,
                                         self.dbase.get_repository_from_handle)

        # GEDCOM only allows for a single repository per source

        for (repo_id, handle) in sorted_list:
            repo = self.dbase.get_repository_from_handle(handle)
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
            self.__note_references(repo.get_note_list(), 1)

    def __reporef(self, reporef, level):
        """
           n REPO [ @XREF:REPO@ | <NULL>] {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
          +1 CALN <SOURCE_CALL_NUMBER> {0:M}
            +2 MEDI <SOURCE_MEDIA_TYPE> {0:1}
        """

        if reporef.ref == None:
            return

        # Append handle to the list for exporting REPOs later
        self.rlist.add(reporef.ref)

        repo = self.dbase.get_repository_from_handle(reporef.ref)
        repo_id = repo.get_gramps_id()

        self.__writeln(level, 'REPO', '@%s@' % repo_id )

        self.__note_references(reporef.get_note_list(), level+1)

        if reporef.get_call_number():
            self.__writeln(level+1, 'CALN', reporef.get_call_number() )
            if reporef.get_media_type():
                self.__writeln(level+2, 'MEDI', str(reporef.get_media_type()))

    def __person_event_ref(self, key, event_ref):
        """
        Writes out the BIRTH and DEATH events for the person.
        """
        if event_ref:
            event = self.dbase.get_event_from_handle(event_ref.ref)
            if (not event.get_date_object().is_empty()) \
                    or event.get_place_handle():
                self.__writeln(1, key)
            else:
                self.__writeln(1, key, 'Y')
            if event.get_description().strip() != "":
                self.__writeln(2, 'TYPE', event.get_description())
            self.dump_event_stats(event, event_ref)

    def __change(self, timeval, level):
        """
          CHANGE_DATE:=
             n CHAN {1:1}
            +1 DATE <CHANGE_DATE> {1:1}
            +2 TIME <TIME_VALUE> {0:1}
            +1 <<NOTE_STRUCTURE>>          # not used
        """
        self.__writeln(level, 'CHAN')
        time_val = time.localtime(timeval)
        self.__writeln(level+1, 'DATE', '%d %s %d' % (
                time_val[2], MONTH[time_val[1]], time_val[0]))
        self.__writeln(level+2, 'TIME', '%02d:%02d:%02d' % (
                time_val[3], time_val[4], time_val[5]))

    def dump_event_stats(self, event, event_ref):
        dateobj = event.get_date_object()
        self.__date(2, dateobj)
        place = None

        if event.get_place_handle():
            place = self.dbase.get_place_from_handle(event.get_place_handle())
            self.__place(place, 2)

        for attr in event.get_attribute_list():
            attr_type = attr.get_type()
            if attr_type == RelLib.AttributeType.CAUSE:
                self.__writeln(2, 'CAUS', attr.get_value())
            elif attr_type == RelLib.AttributeType.AGENCY:
                self.__writeln(2, 'AGNC', attr.get_value())

        for attr in event_ref.get_attribute_list():
            attr_type = attr.get_type()
            if attr_type == RelLib.AttributeType.AGE:
                self.__writeln(2, 'AGE', attr.get_value())
            elif attr_type == RelLib.AttributeType.FATHER_AGE:
                self.__writeln(2, 'HUSB')
                self.__writeln(3, 'AGE', attr.get_value())
            elif attr_type == RelLib.AttributeType.MOTHER_AGE:
                self.__writeln(2, 'WIFE')
                self.__writeln(3, 'AGE', attr.get_value())

        self.__note_references(event.get_note_list(), 2)
        self.__source_references(event.get_source_references(), 2)

        self.__photos(event.get_media_list(), 2)
        if place:
            self.__photos(place.get_media_list(), 2)

    def write_ord(self, lds_ord, index):
        """
          LDS_INDIVIDUAL_ORDINANCE:=
          [
             n [ BAPL | CONL ] {1:1}
            +1 DATE <DATE_LDS_ORD> {0:1}
            +1 TEMP <TEMPLE_CODE> {0:1}
            +1 PLAC <PLACE_LIVING_ORDINANCE> {0:1}
            +1 STAT <LDS_BAPTISM_DATE_STATUS> {0:1}
              +2 DATE <CHANGE_DATE> {1:1}
            +1 <<NOTE_STRUCTURE>> {0:M}
            +1 <<SOURCE_CITATION>> {0:M} p.39
          |
             n ENDL {1:1}
            +1 DATE <DATE_LDS_ORD> {0:1}
            +1 TEMP <TEMPLE_CODE> {0:1}
            +1 PLAC <PLACE_LIVING_ORDINANCE> {0:1}
            +1 STAT <LDS_ENDOWMENT_DATE_STATUS> {0:1}
              +2 DATE <CHANGE_DATE> {1:1}
            +1 <<NOTE_STRUCTURE>> {0:M}
            +1 <<SOURCE_CITATION>> {0:M}
          |
             n SLGC {1:1}
            +1 DATE <DATE_LDS_ORD> {0:1}
            +1 TEMP <TEMPLE_CODE> {0:1}
            +1 PLAC <PLACE_LIVING_ORDINANCE> {0:1}
            +1 FAMC @<XREF:FAM>@ {1:1}
            +1 STAT <LDS_CHILD_SEALING_DATE_STATUS> {0:1}
              +2 DATE <CHANGE_DATE> {1:1}
            +1 <<NOTE_STRUCTURE>> {0:M}
            +1 <<SOURCE_CITATION>> {0:M}
          ]
        """

        self.__writeln(index, LDS_ORD_NAME[lds_ord.get_type()])
        self.__date(index + 1, lds_ord.get_date_object())
        if lds_ord.get_family_handle():
            family_handle = lds_ord.get_family_handle()
            family = self.dbase.get_family_from_handle(family_handle)
            if family:
                self.__writeln(index+1, 'FAMC', '@%s@' % family.get_gramps_id())
        if lds_ord.get_temple():
            self.__writeln(index+1, 'TEMP', lds_ord.get_temple())
        if lds_ord.get_place_handle():
            self.__place(
                self.dbase.get_place_from_handle(lds_ord.get_place_handle()), 2)
        if lds_ord.get_status() != RelLib.LdsOrd.STATUS_NONE:
            self.__writeln(2, 'STAT', LDS_STATUS[lds_ord.get_status()])
        
        self.__note_references(lds_ord.get_note_list(), index+1)
        self.__source_references(lds_ord.get_source_references(), index+1)

    def __date(self, level, date):
        """
        Writes the 'DATE' GEDCOM token, along with the date in GEDCOM's
        expected formta.
        """
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

    def __person_name(self, name, nick):
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
            firstname = "%s %s" % (firstname, patron)

        surname = name.get_surname().replace('/', '?')
        surprefix = name.get_surname_prefix().replace('/', '?')
        suffix = name.get_suffix()
        title = name.get_title()
        if suffix == "":
            if surprefix == "":
                self.__writeln(1, 'NAME', '%s/%s/' % (firstname, surname))
            else:
                self.__writeln(1, 'NAME', '%s/%s %s/' % 
                               (firstname, surprefix, surname))
        elif surprefix == "":
            self.__writeln(1, 'NAME', '%s/%s/ %s' % 
                           (firstname, surname, suffix))
        else:
            self.__writeln(1, 'NAME', '%s/%s %s/ %s' % 
                           (firstname, surprefix, surname, suffix))

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

        self.__source_references(name.get_source_references(), 2)
        self.__note_references(name.get_note_list(), 2)

    def __source_ref_record(self, level, ref):
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

        src = self.dbase.get_source_from_handle(src_handle)
        self.slist.add(src_handle)

        # Reference to the source
        self.__writeln(level, "SOUR", "@%s@" % src.get_gramps_id())
        if ref.get_page() != "":
            self.__writeln(level+1, 'PAGE', ref.get_page())

        conf = min(ref.get_confidence_level(), RelLib.SourceRef.CONF_VERY_HIGH)
        if conf != RelLib.SourceRef.CONF_NORMAL and conf != -1:
            self.__writeln(level+1, "QUAY", QUALITY_MAP[conf])

        if len(ref.get_note_list()) > 0:

            note_list = [ self.dbase.get_note_from_handle(h) 
                          for h in ref.get_note_list() ]
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
                self.__date(level+2, ref.get_date_object())

            note_list = [ self.dbase.get_note_from_handle(h) 
                          for h in ref.get_note_list() ]
            note_list = [ n.handle for n in note_list 
                          if n.get_type() != RelLib.NoteType.SOURCE_TEXT]
            self.__note_references(note_list, level+1)

    def __photo(self, photo, level):
        """
          n OBJE {1:1}
          +1 FORM <MULTIMEDIA_FORMAT> {1:1} 
          +1 TITL <DESCRIPTIVE_TITLE> {0:1} 
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M}
        """
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.dbase.get_object_from_handle(photo_obj_id)
        if photo_obj:
            mime = photo_obj.get_mime_type()
            form = MIME2GED.get(mime, mime)
            path = photo_obj.get_path()
            if not os.path.isfile(path):
                return
            self.__writeln(level, 'OBJE')
            if form:
                self.__writeln(level+1, 'FORM', form)
            self.__writeln(level+1, 'TITL', photo_obj.get_description())
            self.__writeln(level+1, 'FILE', path)

            self.__note_references(photo_obj.get_note_list(), level+1)

    def __place(self, place, level):
        """
          PLACE_STRUCTURE:=
             n PLAC <PLACE_NAME> {1:1}
            +1 FORM <PLACE_HIERARCHY> {0:1}
            +1 FONE <PLACE_PHONETIC_VARIATION> {0:M}  # not used
              +2 TYPE <PHONETIC_TYPE> {1:1}
            +1 ROMN <PLACE_ROMANIZED_VARIATION> {0:M} # not used
              +2 TYPE <ROMANIZED_TYPE> {1:1}
            +1 MAP {0:1}
              +2 LATI <PLACE_LATITUDE> {1:1}
              +2 LONG <PLACE_LONGITUDE> {1:1}
            +1 <<NOTE_STRUCTURE>> {0:M} 
        """
        place_name = place.get_title()
        self.__writeln(level, "PLAC", place_name.replace('\r', ' '))
        longitude = place.get_longitude()
        latitude = place.get_latitude()
        if longitude and latitude:
            self.__writeln(level+1, "MAP")
            self.__writeln(level+2, 'LATI', latitude)
            self.__writeln(level+2, 'LONG', longitude)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def export_data(database, filename, person, option_box, callback=None):
    """
    External interface used to register with the plugin system.
    """
    ret = 0
    try:
        ged_write = GedcomWriter(database, person, 0,  
                                 option_box, callback)
        ret = ged_write.write_gedcom_file(filename)
    except IOError, msg:
        msg2 = _("Could not create %s") % filename
        ErrorDialog(msg2, str(msg))
    except Errors.DatabaseError, msg:
        ErrorDialog(_("Export failed"), str(msg))
    except:
        ErrorDialog(_("Could not create %s") % filename)
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
TITLE = _('GE_DCOM')
DESCRIPTION = _('GEDCOM is used to transfer data between genealogy programs. '
                'Most genealogy software will accept a GEDCOM file as input.')
CONFIG = (_('GEDCOM export options'), ExportOptions.WriterOptionBox)
FILENAME = 'ged'

from PluginUtils import register_export
register_export(export_data, TITLE, DESCRIPTION, CONFIG, FILENAME)
