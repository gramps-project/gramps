#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008-2009  Gary Burton
# Copyright (C) 2008       Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"Export to GEDCOM"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import time

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import (AttributeType, ChildRefType, Citation, Date,
                            EventRoleType, EventType, LdsOrd, NameType,
                            PlaceType, NoteType, Person, UrlType)
from gramps.version import VERSION
import gramps.plugins.lib.libgedcom as libgedcom
from gramps.gen.errors import DatabaseError
# keep the following line even though not obviously used (works on import)
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as _pd

#-------------------------------------------------------------------------
#
# GEDCOM tags representing attributes that may take a parameter, value or
# description on the same line as the tag
#
#-------------------------------------------------------------------------
NEEDS_PARAMETER = set(
    ["CAST", "DSCR", "EDUC", "IDNO", "NATI", "NCHI",
     "NMR", "OCCU", "PROP", "RELI", "SSN", "TITL"])

LDS_ORD_NAME = {
    LdsOrd.BAPTISM         : 'BAPL',
    LdsOrd.ENDOWMENT       : 'ENDL',
    LdsOrd.SEAL_TO_PARENTS : 'SLGC',
    LdsOrd.SEAL_TO_SPOUSE  : 'SLGS',
    LdsOrd.CONFIRMATION    : 'CONL',
}

LDS_STATUS = {
    LdsOrd.STATUS_BIC        : "BIC",
    LdsOrd.STATUS_CANCELED   : "CANCELED",
    LdsOrd.STATUS_CHILD      : "CHILD",
    LdsOrd.STATUS_CLEARED    : "CLEARED",
    LdsOrd.STATUS_COMPLETED  : "COMPLETED",
    LdsOrd.STATUS_DNS        : "DNS",
    LdsOrd.STATUS_INFANT     : "INFANT",
    LdsOrd.STATUS_PRE_1970   : "PRE-1970",
    LdsOrd.STATUS_QUALIFIED  : "QUALIFIED",
    LdsOrd.STATUS_DNS_CAN    : "DNS/CAN",
    LdsOrd.STATUS_STILLBORN  : "STILLBORN",
    LdsOrd.STATUS_SUBMITTED  : "SUBMITTED",
    LdsOrd.STATUS_UNCLEARED  : "UNCLEARED",
}

LANGUAGES = {
    'cs' : 'Czech', 'da' : 'Danish', 'nl' : 'Dutch', 'en' : 'English',
    'eo' : 'Esperanto', 'fi' : 'Finnish', 'fr' : 'French', 'de' : 'German',
    'hu' : 'Hungarian', 'it' : 'Italian', 'lt' : 'Latvian',
    'lv' : 'Lithuanian', 'no' : 'Norwegian', 'po' : 'Polish',
    'pt' : 'Portuguese', 'ro' : 'Romanian', 'sk' : 'Slovak',
    'es' : 'Spanish', 'sv' : 'Swedish', 'ru' : 'Russian', }

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
    Citation.CONF_VERY_HIGH : "3",
    Citation.CONF_HIGH      : "2",
    Citation.CONF_LOW       : "1",
    Citation.CONF_VERY_LOW  : "0",
}

PEDIGREE_TYPES = {
    ChildRefType.BIRTH    : 'birth',
    ChildRefType.STEPCHILD: 'Step',
    ChildRefType.ADOPTED  : 'Adopted',
    ChildRefType.FOSTER   : 'Foster',
}

NOTES_PER_PERSON = 104  # fudge factor to make progress meter a bit smoother


#-------------------------------------------------------------------------
#
# sort_handles_by_id
#
#-------------------------------------------------------------------------
def sort_handles_by_id(handle_list, handle_to_object):
    """
    Sort a list of handles by the Gramps ID.

    The function that returns the object from the handle needs to be supplied
    so that we get the right object.

    """
    sorted_list = []
    for handle in handle_list:
        obj = handle_to_object(handle)
        if obj:
            data = (obj.get_gramps_id(), handle)
            sorted_list.append(data)
    sorted_list.sort()
    return sorted_list


#-------------------------------------------------------------------------
#
# breakup
#
#-------------------------------------------------------------------------
def breakup(txt, limit):
    """
    Break a line of text into a list of strings that conform to the
    maximum length specified, while breaking words in the middle of a word
    to avoid issues with spaces.
    """
    if limit < 1:
        raise ValueError("breakup: unexpected limit: %r" % limit)
    data = []
    while len(txt) > limit:
        # look for non-space pair to break between
        # do not break within a UTF-8 byte sequence, i. e. first char >127
        idx = limit
        while (idx > 0 and (txt[idx - 1].isspace() or txt[idx].isspace() or
                            ord(txt[idx - 1]) > 127)):
            idx -= 1
        if idx == 0:
            #no words to break on, just break at limit anyway
            idx = limit
        data.append(txt[:idx])
        txt = txt[idx:]
    if len(txt) > 0:
        data.append(txt)
    return data


#-------------------------------------------------------------------------
#
# event_has_subordinate_data
#   may want to compare description w/ auto-generated one, and
#   if so, treat it same as if it were empty for this purpose
#
#-------------------------------------------------------------------------
def event_has_subordinate_data(event, event_ref):
    """ determine if event is empty or not """
    if event and event_ref:
        return (event.get_description().strip() or
                not event.get_date_object().is_empty() or
                event.get_place_handle() or
                event.get_attribute_list() or
                event_ref.get_attribute_list() or
                event.get_note_list() or
                event.get_citation_list() or
                event.get_media_list())
    else:
        return False


#-------------------------------------------------------------------------
#
# GedcomWriter class
#
#-------------------------------------------------------------------------
class GedcomWriter(UpdateCallback):
    """
    The GEDCOM writer creates a GEDCOM file that contains the exported
    information from the database. It derives from UpdateCallback
    so that it can provide visual feedback via a progress bar if needed.
    """

    def __init__(self, database, user, option_box=None):
        UpdateCallback.__init__(self, user.callback)
        self.dbase = database
        self.dirname = None
        self.gedcom_file = None
        self.progress_cnt = 0
        self.setup(option_box)

    def setup(self, option_box):
        """
        If the option_box is present (GUI interface), then we check the
        "private", "restrict", and "cfilter" arguments to see if we need
        to apply proxy databases.
        """
        if option_box:
            option_box.parse_options()
            self.dbase = option_box.get_filtered_database(self.dbase, self)

    def write_gedcom_file(self, filename):
        """
        Write the actual GEDCOM file to the specified filename.
        """

        self.dirname = os.path.dirname(filename)
        with open(filename, "w", encoding='utf-8') as self.gedcom_file:
            person_len = self.dbase.get_number_of_people()
            family_len = self.dbase.get_number_of_families()
            source_len = self.dbase.get_number_of_sources()
            repo_len = self.dbase.get_number_of_repositories()
            note_len = self.dbase.get_number_of_notes() / NOTES_PER_PERSON

            total_steps = (person_len + family_len + source_len + repo_len +
                           note_len)
            self.set_total(total_steps)
            self._header(filename)
            self._submitter()
            self._individuals()
            self._families()
            self._sources()
            self._repos()
            self._notes()
            self._all_media()

            self._writeln(0, "TRLR")

        return True

    def _writeln(self, level, token, textlines="", limit=72):
        """
        Write a line of text to the output file in the form of:

            LEVEL TOKEN text

        If the line contains newlines, it is broken into multiple lines using
        the CONT token. If any line is greater than the limit, it will broken
        into multiple lines using CONC.

        """
        assert token
        if textlines:
            # break the line into multiple lines if a newline is found
            textlines = textlines.replace('\n\r', '\n')
            textlines = textlines.replace('\r', '\n')
            # Need to double '@' See Gedcom 5.5 spec 'any_char'
            # but avoid xrefs and escapes
            if not textlines.startswith('@') and '@#' not in textlines:
                textlines = textlines.replace('@', '@@')
            textlist = textlines.split('\n')
            token_level = level
            for text in textlist:
                # make it unicode so that breakup below does the right thin.
                text = str(text)
                if limit:
                    prefix = "\n%d CONC " % (level + 1)
                    txt = prefix.join(breakup(text, limit))
                else:
                    txt = text
                self.gedcom_file.write("%d %s %s\n" %
                                       (token_level, token, txt))
                token_level = level + 1
                token = "CONT"
        else:
            self.gedcom_file.write("%d %s\n" % (level, token))

    def _header(self, filename):
        """
        Write the GEDCOM header.

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
        date_str = "%d %s %d" % (day, libgedcom.MONTH[mon], year)
        time_str = "%02d:%02d:%02d" % (hour, minutes, sec)
        rname = self.dbase.get_researcher().get_name()

        self._writeln(0, "HEAD")
        self._writeln(1, "SOUR", "Gramps")
        self._writeln(2, "VERS", VERSION)
        self._writeln(2, "NAME", "Gramps")
        self._writeln(1, "DATE", date_str)
        self._writeln(2, "TIME", time_str)
        self._writeln(1, "SUBM", "@SUBM@")
        self._writeln(1, "FILE", filename, limit=255)
        self._writeln(1, "COPR", 'Copyright (c) %d %s.' % (year, rname))
        self._writeln(1, "GEDC")
        self._writeln(2, "VERS", "5.5.1")
        self._writeln(2, "FORM", 'LINEAGE-LINKED')
        self._writeln(1, "CHAR", "UTF-8")

        # write the language string if the current LANG variable
        # matches something we know about.

        lang = glocale.language[0]
        if lang and len(lang) >= 2:
            lang_code = LANGUAGES.get(lang[0:2])
            if lang_code:
                self._writeln(1, 'LANG', lang_code)

    def _submitter(self):
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
        name = owner.get_name()
        phon = owner.get_phone()
        mail = owner.get_email()

        self._writeln(0, "@SUBM@", "SUBM")
        self._writeln(1, "NAME", name)

        # Researcher is a sub-type of LocationBase, so get_city etc. which are
        # used in __write_addr work fine. However, the database owner street is
        # stored in address, so we need to temporarily copy it into street so
        # __write_addr works properly
        owner.set_street(owner.get_address())
        self.__write_addr(1, owner)

        if phon:
            self._writeln(1, "PHON", phon)
        if mail:
            self._writeln(1, "EMAIL", mail)

    def _individuals(self):
        """
        Write the individual people to the gedcom file.

        Since people like to have the list sorted by ID value, we need to go
        through a sorting step. We need to reset the progress bar, otherwise,
        people will be confused when the progress bar is idle.

        """
        self.set_text(_("Writing individuals"))
        phandles = self.dbase.iter_person_handles()

        sorted_list = []
        for handle in phandles:
            person = self.dbase.get_person_from_handle(handle)
            if person:
                data = (person.get_gramps_id(), handle)
                sorted_list.append(data)
        sorted_list.sort()

        for data in sorted_list:
            self.update()
            self._person(self.dbase.get_person_from_handle(data[1]))

    def _person(self, person):
        """
        Write out a single person.

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
        if person is None:
            return
        self._writeln(0, "@%s@" % person.get_gramps_id(), "INDI")

        self._names(person)
        self._gender(person)
        self._person_event_ref('BIRT', person.get_birth_ref())
        self._person_event_ref('DEAT', person.get_death_ref())
        self._remaining_events(person)
        self._attributes(person)
        self._lds_ords(person, 1)
        self._child_families(person)
        self._parent_families(person)
        self._assoc(person, 1)
        self._person_sources(person)
        self._addresses(person)
        self._photos(person.get_media_list(), 1)
        self._url_list(person, 1)
        self._note_references(person.get_note_list(), 1)
        self._change(person.get_change_time(), 1)

    def _assoc(self, person, level):
        """
        n ASSO @<XREF:INDI>@ {0:M}
        +1 RELA <RELATION_IS_DESCRIPTOR> {1:1}
        +1 <<NOTE_STRUCTURE>> {0:M}
        +1 <<SOURCE_CITATION>> {0:M}
        """
        for ref in person.get_person_ref_list():
            person = self.dbase.get_person_from_handle(ref.ref)
            if person:
                self._writeln(level, "ASSO", "@%s@" % person.get_gramps_id())
                self._writeln(level + 1, "RELA", ref.get_relation())
                self._note_references(ref.get_note_list(), level + 1)
                self._source_references(ref.get_citation_list(), level + 1)

    def _note_references(self, notelist, level):
        """
        Write out the list of note handles to the current level.

        We use the Gramps ID as the XREF for the GEDCOM file.

        """
        for note_handle in notelist:
            note = self.dbase.get_note_from_handle(note_handle)
            if note:
                self._writeln(level, 'NOTE', '@%s@' % note.get_gramps_id())

    def _names(self, person):
        """
        Write the names associated with the person to the current level.

        Since nicknames in version < 3.3 are separate from the name structure,
        we search the attribute list to see if we can find a nickname.
        Because we do not know the mappings, we just take the first nickname
        we find, and add it to the primary name.
        If a nickname is present in the name structure, it has precedence

        """
        nicknames = [attr.get_value() for attr in person.get_attribute_list()
                     if int(attr.get_type()) == AttributeType.NICKNAME]
        if len(nicknames) > 0:
            nickname = nicknames[0]
        else:
            nickname = ""

        self._person_name(person.get_primary_name(), nickname)
        for name in person.get_alternate_names():
            self._person_name(name, "")

    def _gender(self, person):
        """
        Write out the gender of the person to the file.

        If the gender is not male or female, simply do not output anything.
        The only valid values are M (male) or F (female). So if the geneder is
        unknown, we output nothing.

        """
        if person.get_gender() == Person.MALE:
            self._writeln(1, "SEX", "M")
        elif person.get_gender() == Person.FEMALE:
            self._writeln(1, "SEX", "F")

    def _lds_ords(self, obj, level):
        """
        Simply loop through the list of LDS ordinances, and call the function
        that writes the LDS ordinance structure.
        """
        for lds_ord in obj.get_lds_ord_list():
            self.write_ord(lds_ord, level)

    def _remaining_events(self, person):
        """
        Output all events associated with the person that are not BIRTH or
        DEATH events.

        Because all we have are event references, we have to
        extract the real event to discover the event type.

        """
        global adop_written
        # adop_written is only shared between this function and
        # _process_person_event. This is rather ugly code, but it is difficult
        # to support an Adoption event without an Adopted relationship from the
        # parent(s), an Adopted relationship from the parent(s) without an
        # event, and both an event and a relationship. All these need to be
        # supported without duplicating the output of the ADOP GEDCOM tag. See
        # bug report 2370.
        adop_written = False
        for event_ref in person.get_event_ref_list():
            event = self.dbase.get_event_from_handle(event_ref.ref)
            if not event:
                continue
            self._process_person_event(person, event, event_ref)
        if not adop_written:
            self._adoption_records(person, adop_written)

    def _process_person_event(self, person, event, event_ref):
        """
        Process a person event, which is not a BIRTH or DEATH event.
        """
        global adop_written
        etype = int(event.get_type())
        # if the event is a birth or death, skip it.
        if etype in (EventType.BIRTH, EventType.DEATH):
            return

        role = int(event_ref.get_role())

        # if the event role is not primary, skip the event.
        if role != EventRoleType.PRIMARY:
            return

        val = libgedcom.PERSONALCONSTANTEVENTS.get(etype, "").strip()

        if val and val.strip():
            if val in NEEDS_PARAMETER:
                if event.get_description().strip():
                    self._writeln(1, val, event.get_description())
                else:
                    self._writeln(1, val)
            else:
                if event_has_subordinate_data(event, event_ref):
                    self._writeln(1, val)
                else:
                    self._writeln(1, val, 'Y')
                if event.get_description().strip():
                    self._writeln(2, 'TYPE', event.get_description())
        else:
            descr = event.get_description()
            if descr:
                self._writeln(1, 'EVEN', descr)
            else:
                self._writeln(1, 'EVEN')
            if val.strip():
                self._writeln(2, 'TYPE', val)
            else:
                self._writeln(2, 'TYPE', str(event.get_type()))
        self._dump_event_stats(event, event_ref)
        if etype == EventType.ADOPT and not adop_written:
            adop_written = True
            self._adoption_records(person, adop_written)

    def _adoption_records(self, person, adop_written):
        """
        Write Adoption events for each child that has been adopted.

        n ADOP
        +1 <<INDIVIDUAL_EVENT_DETAIL>>
        +1 FAMC @<XREF:FAM>@
        +2 ADOP <ADOPTED_BY_WHICH_PARENT>

        """

        adoptions = []

        for family in [self.dbase.get_family_from_handle(fh)
                       for fh in person.get_parent_family_handle_list()]:
            if family is None:
                continue
            for child_ref in [ref for ref in family.get_child_ref_list()
                              if ref.ref == person.handle]:
                if child_ref.mrel == ChildRefType.ADOPTED \
                        or child_ref.frel == ChildRefType.ADOPTED:
                    adoptions.append((family, child_ref.frel, child_ref.mrel))

        for (fam, frel, mrel) in adoptions:
            if not adop_written:
                self._writeln(1, 'ADOP', 'Y')
            self._writeln(2, 'FAMC', '@%s@' % fam.get_gramps_id())
            if mrel == frel:
                self._writeln(3, 'ADOP', 'BOTH')
            elif mrel == ChildRefType.ADOPTED:
                self._writeln(3, 'ADOP', 'WIFE')
            else:
                self._writeln(3, 'ADOP', 'HUSB')

    def _attributes(self, person):
        """
        Write out the attributes to the GEDCOM file.

        Since we have already looked at nicknames when we generated the names,
        we filter them out here.

        We use the GEDCOM 5.5.1 FACT command to write out attributes not
        built in to GEDCOM.

        """

        # filter out the nicknames
        attr_list = [attr for attr in person.get_attribute_list()
                     if attr.get_type() != AttributeType.NICKNAME]

        for attr in attr_list:

            attr_type = int(attr.get_type())
            name = libgedcom.PERSONALCONSTANTATTRIBUTES.get(attr_type)
            key = str(attr.get_type())
            value = attr.get_value().strip().replace('\r', ' ')

            if key in ("AFN", "RFN", "REFN", "_UID", "_FSFTID"):
                self._writeln(1, key, value)
                continue

            if key == "RESN":
                self._writeln(1, 'RESN')
                continue

            if name and name.strip():
                self._writeln(1, name, value)
            elif value:
                self._writeln(1, 'FACT', value)
                self._writeln(2, 'TYPE', key)
            else:
                continue
            self._note_references(attr.get_note_list(), 2)
            self._source_references(attr.get_citation_list(), 2)

    def _source_references(self, citation_list, level):
        """
        Loop through the list of citation handles, writing the information
        to the file.
        """
        for citation_handle in citation_list:
            self._source_ref_record(level, citation_handle)

    def _addresses(self, person):
        """
        Write out the addresses associated with the person as RESI events.
        """
        for addr in person.get_address_list():
            self._writeln(1, 'RESI')
            self._date(2, addr.get_date_object())
            self.__write_addr(2, addr)
            if addr.get_phone():
                self._writeln(2, 'PHON', addr.get_phone())

            self._note_references(addr.get_note_list(), 2)
            self._source_references(addr.get_citation_list(), 2)

    def _photos(self, media_list, level):
        """
        Loop through the list of media objects, writing the information
        to the file.
        """
        for photo in media_list:
            self._photo(photo, level)

    def _child_families(self, person):
        """
        Write the Gramps ID as the XREF for each family in which the person
        is listed as a child.
        """

        # get the list of familes from the handle list
        family_list = [self.dbase.get_family_from_handle(hndl)
                       for hndl in person.get_parent_family_handle_list()]

        for family in family_list:
            if family:
                self._writeln(1, 'FAMC', '@%s@' % family.get_gramps_id())
                for child in family.get_child_ref_list():
                    if child.get_reference_handle() == person.get_handle():
                        if child.frel == ChildRefType.ADOPTED and \
                                child.mrel == ChildRefType.ADOPTED:
                            self._writeln(2, 'PEDI adopted')
                        elif child.frel == ChildRefType.BIRTH and \
                                child.mrel == ChildRefType.BIRTH:
                            self._writeln(2, 'PEDI birth')
                        elif child.frel == ChildRefType.STEPCHILD and \
                                child.mrel == ChildRefType.STEPCHILD:
                            self._writeln(2, 'PEDI stepchild')
                        elif child.frel == ChildRefType.FOSTER and \
                                child.mrel == ChildRefType.FOSTER:
                            self._writeln(2, 'PEDI foster')
                        elif child.frel == child.mrel:
                            self._writeln(2, 'PEDI Unknown')
                        else:
                            self._writeln(2, '_FREL %s' %
                                          PEDIGREE_TYPES.get(child.frel.value,
                                                             "Unknown"))
                            self._writeln(2, '_MREL %s' %
                                          PEDIGREE_TYPES.get(child.mrel.value,
                                                             "Unknown"))

    def _parent_families(self, person):
        """
        Write the Gramps ID as the XREF for each family in which the person
        is listed as a parent.
        """

        # get the list of familes from the handle list
        family_list = [self.dbase.get_family_from_handle(hndl)
                       for hndl in person.get_family_handle_list()]

        for family in family_list:
            if family:
                self._writeln(1, 'FAMS', '@%s@' % family.get_gramps_id())

    def _person_sources(self, person):
        """
        Loop through the list of citations, writing the information
        to the file.
        """
        for citation_handle in person.get_citation_list():
            self._source_ref_record(1, citation_handle)

    def _url_list(self, obj, level):
        """
        For Person's FAX, PHON, EMAIL, WWW lines;
        n PHON <PHONE_NUMBER> {0:3}
        n EMAIL <ADDRESS_EMAIL> {0:3}
        n FAX <ADDRESS_FAX> {0:3}
        n WWW <ADDRESS_WEB_PAGE> {0:3}

        n OBJE {1:1}
        +1 FORM <MULTIMEDIA_FORMAT> {1:1}
        +1 TITL <DESCRIPTIVE_TITLE> {0:1}
        +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
        +1 <<NOTE_STRUCTURE>> {0:M}
        """
        for url in obj.get_url_list():
            if url.get_type() == UrlType.EMAIL:
                self._writeln(level, 'EMAIL', url.get_path())
            elif url.get_type() == UrlType.WEB_HOME:
                self._writeln(level, 'WWW', url.get_path())
            elif url.get_type() == _('Phone'):
                self._writeln(level, 'PHON', url.get_path())
            elif url.get_type() == _('FAX'):
                self._writeln(level, 'FAX', url.get_path())
            else:
                self._writeln(level, 'OBJE')
                self._writeln(level + 1, 'FORM', 'URL')
                if url.get_description():
                    self._writeln(level + 1, 'TITL', url.get_description())
                if url.get_path():
                    self._writeln(level + 1, 'FILE', url.get_path(), limit=255)

    def _families(self):
        """
        Write out the list of families, sorting by Gramps ID.
        """
        self.set_text(_("Writing families"))
        # generate a list of (GRAMPS_ID, HANDLE) pairs. This list
        # can then be sorted by the sort routine, which will use the
        # first value of the tuple as the sort key.
        sorted_list = sort_handles_by_id(self.dbase.get_family_handles(),
                                         self.dbase.get_family_from_handle)

        # loop through the sorted list, pulling of the handle. This list
        # has already been sorted by GRAMPS_ID
        for family_handle in [hndl[1] for hndl in sorted_list]:
            self.update()
            self._family(self.dbase.get_family_from_handle(family_handle))

    def _family(self, family):
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
        if family is None:
            return
        gramps_id = family.get_gramps_id()

        self._writeln(0, '@%s@' % gramps_id, 'FAM')

        self._family_reference('HUSB', family.get_father_handle())
        self._family_reference('WIFE', family.get_mother_handle())

        self._lds_ords(family, 1)
        self._family_events(family)
        self._family_attributes(family.get_attribute_list(), 1)
        self._family_child_list(family.get_child_ref_list())
        self._source_references(family.get_citation_list(), 1)
        self._photos(family.get_media_list(), 1)
        self._note_references(family.get_note_list(), 1)
        self._change(family.get_change_time(), 1)

    def _family_child_list(self, child_ref_list):
        """
        Write the child XREF values to the GEDCOM file.
        """
        child_list = [
            self.dbase.get_person_from_handle(cref.ref).get_gramps_id()
            for cref in child_ref_list]

        for gid in child_list:
            if gid is None:
                continue
            self._writeln(1, 'CHIL', '@%s@' % gid)

    def _family_reference(self, token, person_handle):
        """
        Write the family reference to the file.

        This is either 'WIFE' or 'HUSB'. As usual, we use the Gramps ID as the
        XREF value.

        """
        if person_handle:
            person = self.dbase.get_person_from_handle(person_handle)
            if person:
                self._writeln(1, token, '@%s@' % person.get_gramps_id())

    def _family_events(self, family):
        """
        Output the events associated with the family.

        Because all we have are event references, we have to extract the real
        event to discover the event type.

        """
        for event_ref in family.get_event_ref_list():
            event = self.dbase.get_event_from_handle(event_ref.ref)
            if event is None:
                continue
            self._process_family_event(event, event_ref)
            self._dump_event_stats(event, event_ref)

    def _process_family_event(self, event, event_ref):
        """
        Process a single family event.
        """
        etype = int(event.get_type())
        val = libgedcom.FAMILYCONSTANTEVENTS.get(etype)

        if val:
            if event_has_subordinate_data(event, event_ref):
                self._writeln(1, val)
            else:
                self._writeln(1, val, 'Y')

            if event.get_type() == EventType.MARRIAGE:
                self._family_event_attrs(event.get_attribute_list(), 2)

            if event.get_description().strip() != "":
                self._writeln(2, 'TYPE', event.get_description())
        else:
            descr = event.get_description()
            if descr:
                self._writeln(1, 'EVEN', descr)
            else:
                self._writeln(1, 'EVEN')
            the_type = str(event.get_type())
            if the_type:
                self._writeln(2, 'TYPE', the_type)

    def _family_event_attrs(self, attr_list, level):
        """
        Write the attributes associated with the family event.

        The only ones we really care about are FATHER_AGE and MOTHER_AGE which
        we translate to WIFE/HUSB AGE attributes.

        """
        for attr in attr_list:
            if attr.get_type() == AttributeType.FATHER_AGE:
                self._writeln(level, 'HUSB')
                self._writeln(level + 1, 'AGE', attr.get_value())
            elif attr.get_type() == AttributeType.MOTHER_AGE:
                self._writeln(level, 'WIFE')
                self._writeln(level + 1, 'AGE', attr.get_value())

    def _family_attributes(self, attr_list, level):
        """
        Write out the attributes associated with a family to the GEDCOM file.

        Since we have already looked at nicknames when we generated the names,
        we filter them out here.

        We use the GEDCOM 5.5.1 FACT command to write out attributes not
        built in to GEDCOM.

        """

        for attr in attr_list:

            attr_type = int(attr.get_type())
            name = libgedcom.FAMILYCONSTANTATTRIBUTES.get(attr_type)
            key = str(attr.get_type())
            value = attr.get_value().replace('\r', ' ')

            if key in ("AFN", "RFN", "REFN", "_UID"):
                self._writeln(1, key, value)
                continue

            if name and name.strip():
                self._writeln(1, name, value)
                continue
            else:
                self._writeln(1, 'FACT', value)
                self._writeln(2, 'TYPE', key)

            self._note_references(attr.get_note_list(), level + 1)
            self._source_references(attr.get_citation_list(),
                                    level + 1)

    def _sources(self):
        """
        Write out the list of sources, sorting by Gramps ID.
        """
        self.set_text(_("Writing sources"))
        sorted_list = sort_handles_by_id(self.dbase.get_source_handles(),
                                         self.dbase.get_source_from_handle)

        for (source_id, handle) in sorted_list:
            self.update()
            source = self.dbase.get_source_from_handle(handle)
            if source is None:
                continue
            self._writeln(0, '@%s@' % source_id, 'SOUR')
            if source.get_title():
                self._writeln(1, 'TITL', source.get_title())

            if source.get_author():
                self._writeln(1, "AUTH", source.get_author())

            if source.get_publication_info():
                self._writeln(1, "PUBL", source.get_publication_info())

            if source.get_abbreviation():
                self._writeln(1, 'ABBR', source.get_abbreviation())

            self._photos(source.get_media_list(), 1)

            for reporef in source.get_reporef_list():
                self._reporef(reporef, 1)
                # break

            self._note_references(source.get_note_list(), 1)
            self._change(source.get_change_time(), 1)

    def _notes(self):
        """
        Write out the list of notes, sorting by Gramps ID.
        """
        self.set_text(_("Writing notes"))
        note_cnt = 0
        sorted_list = sort_handles_by_id(self.dbase.get_note_handles(),
                                         self.dbase.get_note_from_handle)

        for note_handle in [hndl[1] for hndl in sorted_list]:
            # the following makes the progress bar a bit smoother
            if not note_cnt % NOTES_PER_PERSON:
                self.update()
            note_cnt += 1
            note = self.dbase.get_note_from_handle(note_handle)
            if note is None:
                continue
            self._note_record(note)

    def _note_record(self, note):
        """
        n @<XREF:NOTE>@ NOTE <SUBMITTER_TEXT> {1:1}
        +1 [ CONC | CONT] <SUBMITTER_TEXT> {0:M}
        +1 <<SOURCE_CITATION>> {0:M}
        +1 REFN <USER_REFERENCE_NUMBER> {0:M}
        +2 TYPE <USER_REFERENCE_TYPE> {0:1}
        +1 RIN <AUTOMATED_RECORD_ID> {0:1}
        +1 <<CHANGE_DATE>> {0:1}
        """
        if note:
            self._writeln(0, '@%s@' % note.get_gramps_id(),
                          'NOTE ' + note.get())

    def _repos(self):
        """
        Write out the list of repositories, sorting by Gramps ID.

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
        self.set_text(_("Writing repositories"))
        sorted_list = sort_handles_by_id(self.dbase.get_repository_handles(),
                                         self.dbase.get_repository_from_handle)

        # GEDCOM only allows for a single repository per source

        for (repo_id, handle) in sorted_list:
            self.update()
            repo = self.dbase.get_repository_from_handle(handle)
            if repo is None:
                continue
            self._writeln(0, '@%s@' % repo_id, 'REPO')
            if repo.get_name():
                self._writeln(1, 'NAME', repo.get_name())
            for addr in repo.get_address_list():
                self.__write_addr(1, addr)
                if addr.get_phone():
                    self._writeln(1, 'PHON', addr.get_phone())
            for url in repo.get_url_list():
                if url.get_type() == UrlType.EMAIL:
                    self._writeln(1, 'EMAIL', url.get_path())
                elif url.get_type() == UrlType.WEB_HOME:
                    self._writeln(1, 'WWW', url.get_path())
                elif url.get_type() == _('FAX'):
                    self._writeln(1, 'FAX', url.get_path())
            self._note_references(repo.get_note_list(), 1)

    def _reporef(self, reporef, level):
        """
        n REPO [ @XREF:REPO@ | <NULL>] {1:1}
        +1 <<NOTE_STRUCTURE>> {0:M}
        +1 CALN <SOURCE_CALL_NUMBER> {0:M}
        +2 MEDI <SOURCE_MEDIA_TYPE> {0:1}
        """

        if reporef.ref is None:
            return

        repo = self.dbase.get_repository_from_handle(reporef.ref)
        if repo is None:
            return

        repo_id = repo.get_gramps_id()

        self._writeln(level, 'REPO', '@%s@' % repo_id)

        self._note_references(reporef.get_note_list(), level + 1)

        if reporef.get_call_number():
            self._writeln(level + 1, 'CALN', reporef.get_call_number())
            if reporef.get_media_type():
                self._writeln(level + 2, 'MEDI', str(reporef.get_media_type()))

    def _person_event_ref(self, key, event_ref):
        """
        Write out the BIRTH and DEATH events for the person.
        """
        if event_ref:
            event = self.dbase.get_event_from_handle(event_ref.ref)
            if event_has_subordinate_data(event, event_ref):
                self._writeln(1, key)
            else:
                self._writeln(1, key, 'Y')
            if event.get_description().strip() != "":
                self._writeln(2, 'TYPE', event.get_description())
            self._dump_event_stats(event, event_ref)

    def _change(self, timeval, level):
        """
        CHANGE_DATE:=
            n CHAN {1:1}
            +1 DATE <CHANGE_DATE> {1:1}
            +2 TIME <TIME_VALUE> {0:1}
            +1 <<NOTE_STRUCTURE>>          # not used
        """
        self._writeln(level, 'CHAN')
        time_val = time.gmtime(timeval)
        self._writeln(level + 1, 'DATE', '%d %s %d' % (
            time_val[2], libgedcom.MONTH[time_val[1]], time_val[0]))
        self._writeln(level + 2, 'TIME', '%02d:%02d:%02d' % (
            time_val[3], time_val[4], time_val[5]))

    def _dump_event_stats(self, event, event_ref):
        """
        Write the event details for the event, using the event and event
        reference information.

        GEDCOM does not make a distinction between the two.

        """
        dateobj = event.get_date_object()
        self._date(2, dateobj)
        if self._datewritten:
            # write out TIME if present
            times = [attr.get_value() for attr in event.get_attribute_list()
                     if int(attr.get_type()) == AttributeType.TIME]
            # Not legal, but inserted by PhpGedView
            if len(times) > 0:
                self._writeln(3, 'TIME', times[0])

        place = None

        if event.get_place_handle():
            place = self.dbase.get_place_from_handle(event.get_place_handle())
            self._place(place, dateobj, 2)

        for attr in event.get_attribute_list():
            attr_type = attr.get_type()
            if attr_type == AttributeType.CAUSE:
                self._writeln(2, 'CAUS', attr.get_value())
            elif attr_type == AttributeType.AGENCY:
                self._writeln(2, 'AGNC', attr.get_value())
            elif attr_type == _("Phone"):
                self._writeln(2, 'PHON', attr.get_value())
            elif attr_type == _("FAX"):
                self._writeln(2, 'FAX', attr.get_value())
            elif attr_type == _("EMAIL"):
                self._writeln(2, 'EMAIL', attr.get_value())
            elif attr_type == _("WWW"):
                self._writeln(2, 'WWW', attr.get_value())

        for attr in event_ref.get_attribute_list():
            attr_type = attr.get_type()
            if attr_type == AttributeType.AGE:
                self._writeln(2, 'AGE', attr.get_value())
            elif attr_type == AttributeType.FATHER_AGE:
                self._writeln(2, 'HUSB')
                self._writeln(3, 'AGE', attr.get_value())
            elif attr_type == AttributeType.MOTHER_AGE:
                self._writeln(2, 'WIFE')
                self._writeln(3, 'AGE', attr.get_value())

        self._note_references(event.get_note_list(), 2)
        self._source_references(event.get_citation_list(), 2)

        self._photos(event.get_media_list(), 2)
        if place:
            self._photos(place.get_media_list(), 2)

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

        self._writeln(index, LDS_ORD_NAME[lds_ord.get_type()])
        self._date(index + 1, lds_ord.get_date_object())
        if lds_ord.get_family_handle():
            family_handle = lds_ord.get_family_handle()
            family = self.dbase.get_family_from_handle(family_handle)
            if family:
                self._writeln(index + 1, 'FAMC', '@%s@' %
                              family.get_gramps_id())
        if lds_ord.get_temple():
            self._writeln(index + 1, 'TEMP', lds_ord.get_temple())
        if lds_ord.get_place_handle():
            place = self.dbase.get_place_from_handle(
                lds_ord.get_place_handle())
            self._place(place, lds_ord.get_date_object(), 2)
        if lds_ord.get_status() != LdsOrd.STATUS_NONE:
            self._writeln(2, 'STAT', LDS_STATUS[lds_ord.get_status()])

        self._note_references(lds_ord.get_note_list(), index + 1)
        self._source_references(lds_ord.get_citation_list(), index + 1)

    def _date(self, level, date):
        """
        Write the 'DATE' GEDCOM token, along with the date in GEDCOM's
        expected format.
        """
        self._datewritten = True
        start = date.get_start_date()
        if start != Date.EMPTY:
            cal = date.get_calendar()
            mod = date.get_modifier()
            quality = date.get_quality()
            if quality in libgedcom.DATE_QUALITY:
                qual_text = libgedcom.DATE_QUALITY[quality] + " "
            else:
                qual_text = ""
            if mod == Date.MOD_SPAN:
                val = "%sFROM %s TO %s" % (
                    qual_text,
                    libgedcom.make_gedcom_date(start, cal, mod, None),
                    libgedcom.make_gedcom_date(date.get_stop_date(),
                                               cal, mod, None))
            elif mod == Date.MOD_RANGE:
                val = "%sBET %s AND %s" % (
                    qual_text,
                    libgedcom.make_gedcom_date(start, cal, mod, None),
                    libgedcom.make_gedcom_date(date.get_stop_date(),
                                               cal, mod, None))
            else:
                val = libgedcom.make_gedcom_date(start, cal, mod, quality)
            self._writeln(level, 'DATE', val)
        elif date.get_text():
            self._writeln(level, 'DATE', date.get_text())
        else:
            self._datewritten = False

    def _person_name(self, name, attr_nick):
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
        gedcom_name = name.get_gedcom_name()

        firstname = name.get_first_name().strip()
        surns = []
        surprefs = []
        for surn in name.get_surname_list():
            surns.append(surn.get_surname().replace('/', '?'))
            if surn.get_connector():
                #we store connector with the surname
                surns[-1] = surns[-1] + ' ' + surn.get_connector()
            surprefs.append(surn.get_prefix().replace('/', '?'))
        surname = ', '.join(surns)
        surprefix = ', '.join(surprefs)
        suffix = name.get_suffix()
        title = name.get_title()
        nick = name.get_nick_name()
        if nick.strip() == '':
            nick = attr_nick

        self._writeln(1, 'NAME', gedcom_name)
        if int(name.get_type()) == NameType.BIRTH:
            pass
        elif int(name.get_type()) == NameType.MARRIED:
            self._writeln(2, 'TYPE', 'married')
        elif int(name.get_type()) == NameType.AKA:
            self._writeln(2, 'TYPE', 'aka')
        else:
            self._writeln(2, 'TYPE', name.get_type().xml_str())

        if firstname:
            self._writeln(2, 'GIVN', firstname)
        if surprefix:
            self._writeln(2, 'SPFX', surprefix)
        if surname:
            self._writeln(2, 'SURN', surname)
        if name.get_suffix():
            self._writeln(2, 'NSFX', suffix)
        if name.get_title():
            self._writeln(2, 'NPFX', title)
        if nick:
            self._writeln(2, 'NICK', nick)

        self._source_references(name.get_citation_list(), 2)
        self._note_references(name.get_note_list(), 2)

    def _source_ref_record(self, level, citation_handle):
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

        citation = self.dbase.get_citation_from_handle(citation_handle)

        src_handle = citation.get_reference_handle()
        if src_handle is None:
            return

        src = self.dbase.get_source_from_handle(src_handle)
        if src is None:
            return

        # Reference to the source
        self._writeln(level, "SOUR", "@%s@" % src.get_gramps_id())
        if citation.get_page() != "":
            # PAGE <WHERE_WITHIN_SOURCE> can not have CONC lines.
            # WHERE_WITHIN_SOURCE:= {Size=1:248}
            # Maximize line to 248 and set limit to 248, for no line split
            self._writeln(level + 1, 'PAGE', citation.get_page()[0:248],
                          limit=248)

        conf = min(citation.get_confidence_level(),
                   Citation.CONF_VERY_HIGH)
        if conf != Citation.CONF_NORMAL and conf != -1:
            self._writeln(level + 1, "QUAY", QUALITY_MAP[conf])

        if not citation.get_date_object().is_empty():
            self._writeln(level + 1, 'DATA')
            self._date(level + 2, citation.get_date_object())

        if len(citation.get_note_list()) > 0:

            note_list = [self.dbase.get_note_from_handle(h)
                         for h in citation.get_note_list()]
            note_list = [n for n in note_list
                         if n.get_type() == NoteType.SOURCE_TEXT]

            if note_list:
                ref_text = note_list[0].get()
            else:
                ref_text = ""

            if ref_text != "" and citation.get_date_object().is_empty():
                self._writeln(level + 1, 'DATA')
            if ref_text != "":
                self._writeln(level + 2, "TEXT", ref_text)

            note_list = [self.dbase.get_note_from_handle(h)
                         for h in citation.get_note_list()]
            note_list = [n.handle for n in note_list
                         if n and n.get_type() != NoteType.SOURCE_TEXT]
            self._note_references(note_list, level + 1)

        self._photos(citation.get_media_list(), level + 1)

        even = None
        for srcattr in citation.get_attribute_list():
            if str(srcattr.type) == "EVEN":
                even = srcattr.value
                self._writeln(level + 1, "EVEN", even)
                break
        if even:
            for srcattr in citation.get_attribute_list():
                if str(srcattr.type) == "EVEN:ROLE":
                    self._writeln(level + 2, "ROLE", srcattr.value)
                    break

    def _photo(self, photo, level):
        """
        n OBJE @<XREF:OBJE>@ {1:1}
        """
        photo_obj_id = photo.get_reference_handle()
        photo_obj = self.dbase.get_media_from_handle(photo_obj_id)
        if photo_obj:
            # if not os.path.isfile(path):
                # return
            self._writeln(level, 'OBJE @%s@' % photo_obj.get_gramps_id())

    def _all_media(self):
        """
        Write out the list of media, sorting by Gramps ID.
        """
        self.set_text(_("Writing media"))
        # generate a list of (GRAMPS_ID, HANDLE) pairs. This list
        # can then be sorted by the sort routine, which will use the
        # first value of the tuple as the sort key.
        sorted_list = sort_handles_by_id(self.dbase.get_media_handles(),
                                         self.dbase.get_media_from_handle)

        # loop through the sorted list, pulling of the handle. This list
        # has already been sorted by GRAMPS_ID
        for media_handle in [hndl[1] for hndl in sorted_list]:
            self.update()
            self._media(self.dbase.get_media_from_handle(media_handle))

    def _media(self, media):
        """
        n @XREF:OBJE@ OBJE {1:1}
        +1 FILE <MULTIMEDIA_FILE_REFN> {1:M}
        +2 FORM <MULTIMEDIA_FORMAT> {1:1}
        +3 TYPE <SOURCE_MEDIA_TYPE> {0:1}
        +2 TITL <DESCRIPTIVE_TITLE> {0:1} p.48
        +1 REFN <USER_REFERENCE_NUMBER> {0:M}
        +2 TYPE <USER_REFERENCE_TYPE> {0:1}
        +1 RIN <AUTOMATED_RECORD_ID> {0:1}
        +1 <<NOTE_STRUCTURE>> {0:M}
        +1 <<SOURCE_CITATION>> {0:M}
        +1 <<CHANGE_DATE>> {0:1}
        """
        if media is None:
            return
        gramps_id = media.get_gramps_id()

        self._writeln(0, '@%s@' % gramps_id, 'OBJE')
        mime = media.get_mime_type()
        form = MIME2GED.get(mime, mime)
        path = media_path_full(self.dbase, media.get_path())
        self._writeln(1, 'FILE', path, limit=255)
        if form:
            self._writeln(2, 'FORM', form)
        self._writeln(2, 'TITL', media.get_description())

        for attr in media.get_attribute_list():
            key = str(attr.get_type())
            value = attr.get_value().replace('\r', ' ')
            if key in ("RIN", "RFN", "REFN"):
                self._writeln(1, key, value)
                continue
        self._note_references(media.get_note_list(), 1)
        self._source_references(media.get_citation_list(), 1)
        self._change(media.get_change_time(), 1)

    def _place(self, place, dateobj, level):
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
        if place is None:
            return
        place_name = _pd.display(self.dbase, place, dateobj)
        self._writeln(level, "PLAC", place_name.replace('\r', ' '), limit=120)
        longitude = place.get_longitude()
        latitude = place.get_latitude()
        if longitude and latitude:
            (latitude, longitude) = conv_lat_lon(latitude, longitude, "GEDCOM")
        if longitude and latitude:
            self._writeln(level + 1, "MAP")
            self._writeln(level + 2, 'LATI', latitude)
            self._writeln(level + 2, 'LONG', longitude)

        # The Gedcom standard shows that an optional address structure can
        # be written out in the event detail.
        # http://homepages.rootsweb.com/~pmcbride/gedcom/55gcch2.htm#EVENT_DETAIL
        location = get_main_location(self.dbase, place)
        street = location.get(PlaceType.STREET)
        locality = location.get(PlaceType.LOCALITY)
        city = location.get(PlaceType.CITY)
        state = location.get(PlaceType.STATE)
        country = location.get(PlaceType.COUNTRY)
        postal_code = place.get_code()

        if street or locality or city or state or postal_code or country:
            self._writeln(level, "ADDR", street)
            if street:
                self._writeln(level + 1, 'ADR1', street)
            if locality:
                self._writeln(level + 1, 'ADR2', locality)
            if city:
                self._writeln(level + 1, 'CITY', city)
            if state:
                self._writeln(level + 1, 'STAE', state)
            if postal_code:
                self._writeln(level + 1, 'POST', postal_code)
            if country:
                self._writeln(level + 1, 'CTRY', country)

        self._note_references(place.get_note_list(), level + 1)

    def __write_addr(self, level, addr):
        """
        n ADDR <ADDRESS_LINE> {0:1}
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}  (Street)
        +1 ADR2 <ADDRESS_LINE2> {0:1}  (Locality)
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}

        This is done along the lines suggested by Tamura Jones in
        http://www.tamurajones.net/GEDCOMADDR.xhtml as a result of bug 6382.
        "GEDCOM writers should always use the structured address format,
        and it use it for all addresses, including the submitter address and
        their own corporate address." "Vendors that want their product to pass
        even the strictest GEDCOM validation, should include export to the old
        free-form format..." [This goes on to say the free-form should be an
        option, but we have not made it an option in Gramps].

        @param level: The level number for the ADDR tag
        @type level: Integer
        @param addr: The location or address
        @type addr: [a super-type of] LocationBase
        """
        if addr.get_street() or addr.get_locality() or addr.get_city() or \
           addr.get_state() or addr.get_postal_code or addr.get_country():
            self._writeln(level, 'ADDR', addr.get_street())
            if addr.get_locality():
                self._writeln(level + 1, 'CONT', addr.get_locality())
            if addr.get_city():
                self._writeln(level + 1, 'CONT', addr.get_city())
            if addr.get_state():
                self._writeln(level + 1, 'CONT', addr.get_state())
            if addr.get_postal_code():
                self._writeln(level + 1, 'CONT', addr.get_postal_code())
            if addr.get_country():
                self._writeln(level + 1, 'CONT', addr.get_country())

            if addr.get_street():
                self._writeln(level + 1, 'ADR1', addr.get_street())
            if addr.get_locality():
                self._writeln(level + 1, 'ADR2', addr.get_locality())
            if addr.get_city():
                self._writeln(level + 1, 'CITY', addr.get_city())
            if addr.get_state():
                self._writeln(level + 1, 'STAE', addr.get_state())
            if addr.get_postal_code():
                self._writeln(level + 1, 'POST', addr.get_postal_code())
            if addr.get_country():
                self._writeln(level + 1, 'CTRY', addr.get_country())


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def export_data(database, filename, user, option_box=None):
    """
    External interface used to register with the plugin system.
    """
    ret = False
    try:
        ged_write = GedcomWriter(database, user, option_box)
        ret = ged_write.write_gedcom_file(filename)
    except IOError as msg:
        msg2 = _("Could not create %s") % filename
        user.notify_error(msg2, str(msg))
    except DatabaseError as msg:
        user.notify_db_error("%s\n%s" % (_("GEDCOM Export failed"), str(msg)))
    return ret
