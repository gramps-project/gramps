# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008-2011  Kees Bakker
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2013-2017  Alois Poettker
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

"Import from Pro-Gen"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import re, os, struct, sys, time

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.ImportProGen')

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.datehandler import displayer
from gramps.gen.db.txn import DbTxn
from gramps.gen.db.dbconst import (PERSON_KEY, FAMILY_KEY, EVENT_KEY, PLACE_KEY,
                                   NOTE_KEY, TAG_KEY, CITATION_KEY, SOURCE_KEY)
from gramps.gen.errors import HandleError
from gramps.gen.lib import (Address, Attribute, AttributeType, ChildRef,
                            Citation, Date, Event, EventRef, EventType, Family,
                            FamilyRelType, Name, NameType, NameOriginType, Note,
                            NoteType, Person, Place, PlaceName, Source,
                            SrcAttribute, Surname, Tag)
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.utils.id import create_id

from gramps.gui.utils import ProgressMeter

from gramps.plugins.importer.importxml import ImportInfo

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
PRIMOBJECTS = ('person', 'family', 'child')
TAGOBJECTS = ('person', 'family', 'event', 'place', 'source', 'citation', 'note')
OPTOBJECTS = (
    'person-ident', 'family-ident',
    'surname-male', 'surname-female',
    'birth-date', 'death-date', 'death-cause',
    'refn-code'
)
MONTHES = {
    'jan' : 1,   # de, en, nl
    'feb' : 2, 'febr' : 2,   # de, en, nl
    'mrz' : 3,   # de
    'mar' : 3, 'march' : 3,  # en
    'maa' : 3, 'mrt' : 3, 'maart' : 3,   # nl
    'apr' : 4, 'april' : 4,   # de, en, nl
    'mai' : 5, 'may' : 5, 'mei' : 5,   # de, en, nl
    'jun' : 6, 'june' : 6, 'juni' : 6,   # de, en, nl
    'jul' : 7, 'july' : 7, 'juli' : 7,   # de, en, nl
    'aug' : 8,   # de, en, nl
    'sep' : 9, 'sept' : 9,   # de, en, nl
    'okt' : 10, 'oct' : 10, 'ok' : 10,  # de, en, nl
    'nov' : 11,   # de, en, nl
    'dez' : 12, 'dec' : 12   # de, en, nl
}
PREFIXES = (
    't ',   # nl
    'den ', 'der ', 'de ',   # de, nl
    'het ',   # nl
    'in den ',   # nl
    'ten ', 'ter ', 'te ',   # nl
    'van ', 'van den ', 'van der ', 'van de ',   # nl
    'von ', 'von der ',   # de
    'zu '   # DE
)

class ProgenError(Exception):
    """
    Class used to report Pro-Gen exceptions (mostly errors).
    """
    def __init__(self, value=''):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value

def _read_mem(bname):
    """
    Read a Pro-Gen record.
    """
    # Each record is 32 bytes. First a 4 byte reference to the next record
    # followed by 28 bytes of text. The information forms a chain of records,
    # that stops when a reference is 0 or smaller. There are two special
    # sequences:
    # <ESC> <CR> hard return
    # <ESC> <^Z> end of the memo field
    if os.path.exists(bname + '.MEM'):
        fname = bname + '.MEM'
    else:
        fname = bname + '.mem'

    with open(fname, "rb") as file_:
        LOG.debug("The current system is %s-endian", sys.byteorder)

        # The input file comes from [what was originally] a DOS machine so will
        # be little-endian, regardless of the 'native' byte order of the host
        recfmt = "<i28s"
        reclen = struct.calcsize(str(recfmt))
        # print("# reclen = %d" % reclen)

        mems = []
        while 1:
            buf = file_.read(reclen)
            if not buf:
                break
            (recno, text) = struct.unpack(recfmt, buf)
            mems.append([recno, text])

        return mems

def _read_recs(table, bname, mems):
    """
    Read records from .PER or .REL file.
    """
    if os.path.exists(bname + table.fileext):
        fname = bname + table.fileext
    else:
        fname = bname + table.fileext.lower()

    with open(fname, "rb") as file_:
        recfmt = table.recfmt
        LOG.info("# %s - recfmt = %s", table['name1'], recfmt)
        reclen = struct.calcsize(str(recfmt))
        LOG.info("# %s - reclen = %d", table['name1'], reclen)

        recs = []
        pos_recs, tot_recs = 0, 0   # positive / total records
        while 1:
            buf = file_.read(reclen)
            if not buf:
                break

            tot_recs += 1
            # check if all items in list are identical
            if buf.count(buf[0]) != len(buf):
                pos_recs += 1
                tups = struct.unpack(recfmt, buf)
                gid = str(tot_recs).encode('cp850')
                tups = list(tups)   # casting to list
                tups.insert(0, gid)   # inserting essential Gramps ID!
                recs.append(tups)
                # recflds = table.convert_record_to_list(tups, mems)  # Debug!

        LOG.info("# length %s.recs[] = %d", table['name1'], len(recs))
        LOG.info("# total %d, pos. %d, null %d recs", \
                 tot_recs, pos_recs, tot_recs - pos_recs)

        return recs

def _get_defname(fname):
    """
    Get the name of the PG30.DEF file by looking at the user DEF file.
    """
    # Return the name of the DEF file. <fname> is expected to be somewhere in
    # the PG30 tree. Contents of <fname> is always something like:
    # => \\0
    # => C:\\PG30\\NL\\PG30-1.DEF

    # We will strip the C: and convert the rest to a native pathname. Next,
    # this pathname is compared with <fname>.

    with open(fname, buffering=1, encoding='cp437', errors='strict') as file_:
        lines = file_.readlines()
    if not lines[0].startswith(r'\0') or len(lines) != 2:
        return None, fname

    defname = lines[1]
    defname = defname.strip()
    # Strip drive, if any
    defname = re.sub(r'^\w:', '', defname)
    defname = defname.replace('\\', os.sep)
    # Strip leading slash, if any.
    if defname.startswith(os.sep):
        defname = defname[1:]
    # LOG.warning('_get_defname: fname=%(fname)s => defname=%(defname)s', vars())

    # Using directory of <fname>, go to parent directory until the DEF is found
    dir_, file_ = os.path.split(os.path.abspath(fname))
    while dir_ and dir_ != os.sep:
        # LOG.warning('_get_defname: dir=%(dir_)s => defname=%(defname)s', vars())
        newdefname = os.path.join(dir_, defname)

        if os.path.exists(newdefname):
            return newdefname, defname
        newdefname = newdefname.lower()
        if os.path.exists(newdefname):
            return newdefname, defname

        # One level up
        dir_, file_ = os.path.split(dir_)

    return None, defname


# Example field:
# ['First name', '47', '64', '4', '2', '15', '""', '""']
# item 0
# item 1 is a number indicating the fieldtype
# item 2
# item 3 is the size of the field
class PG30DefTableField(object):
    """
    This class represents a field in one of the tables in the DEF file.
    """
    def __init__(self, name, value):
        self.fieldname = name
        self.fields = value.split(',')
        self.fields = [p.strip() for p in self.fields]
        # We have seen some case insensitivity in DEF files ...
        self.name = self.fields[0].lower()
        self.type_ = int(self.fields[1])
        self.size = int(self.fields[3])

    def __repr__(self):
        return self.fieldname + ' -> ' + ', '.join(self.fields)


ESC_CTRLZ = re.compile(r'\033\032.*')
class PG30DefTable(object):
    """
    This class represents a table in the DEF file.
    """
    def __init__(self, name, lines):
        self.name = name
        self.flds = []
        self.parms = {}
        self.recfmt = None

        # Example line:
        # f02=Person_last_change  ,32,10,10, 1,68,"","INDI CHAN DATE"
        line_pat = re.compile(r'(\w+) = (.*)', re.VERBOSE)
        for lne in lines:
            mtch = line_pat.match(lne)
            if mtch:   # Catch duplicates?
                self.parms[mtch.group(1)] = mtch.group(2)

        self.fileext = self.parms.get('fileext', None)

        # If there is a n_fields entry then this is a table that
        # has details about the record format of another file (PER or REL).
        if 'n_fields' in self.parms:
            self.flds = self.get_fields()
            self.recfmt = self.get_recfmt()
            self.nam2fld = {}
            self.nam2idx = {}
            self.recflds = []   # list of fields that use up space in a record
            j = 0
            for i, fld in enumerate(self.flds):
                # print("# field %s" % fld)
                nam = fld.name
                self.nam2fld[nam] = fld
                # fld.size == 0: Field will not be acknowleged!
                if (i == 0) or (fld.size != 0):
                    self.nam2idx[nam] = j
                    # print("#       %s <= %d" % (fld.fieldname, j))
                    self.recflds.append(fld)
                    j += 1

    def __getitem__(self, i):
        return self.parms.get(i, None)

    def get_recfmt(self):
        """ Get the record format for struct.unpack """
        # Example field:
        # ['First Name', '47', '64', '4', '2', '15', '""', '""']
        # item 0
        # item 1 is a number indicating the fieldtype
        # item 2
        # item 3 is the size of the field
        # ...

        flds = self.flds
        # The input file comes from [what was originally] a DOS machine so will
        # be little-endian, regardless of 'native' byte order of the host system
        fmt = '<'
        for fld in flds:
            fldtyp = fld.type_
            if fldtyp == 2 or fldtyp == 3 or fldtyp == 22 or fldtyp == 23:
                fmt += 'i'
            elif fldtyp == 31:
                pass
            elif fldtyp == 32 or fldtyp == 44 or fldtyp == 45:
                fmt += '%ds' % fld.size
            elif fldtyp == 41:
                fmt += 'h'
            elif fldtyp == 42 or fldtyp == 43 or fldtyp == 46 or fldtyp == 47:
                fmt += 'i'
            else:
                pass   # ???? Do we want to know?

        return fmt

    def get_fields(self):
        """ Get the fields """
        # For example from PG30-1.DEF
        # n_fields=58
        # f01=Person ID    , 31,  6, 0, 1, 17, "", "INDI RFN"
        # f02=Person change, 32, 10,10, 1, 68, "", "INDI CHAN DATE"
        # f03=First name   , 47, 64, 4, 2, 15, "", ""

        n_fields = int(self.parms['n_fields'])
        flds = []
        for i in range(n_fields):
            fld_name = 'f%02d' % (i+1)
            fld = self.parms.get(fld_name, None)
            flds.append(PG30DefTableField(fld_name, fld))

        return flds

    def get_mem_text(self, mems, i):
        """ Normalize text. """
        # Notice that Pro-Gen starts the mem numbering at 1.
        if i <= 0:
            # MEM index 0, just return an empty string
            return ""

        i -= 1
        recno = mems[i][0] - 1
        text = mems[i][1].decode('cp850')
        while recno >= 0:
            text += mems[recno][1].decode('cp850')
            recno = mems[recno][0] - 1

        text = text.replace('\033\r', '\n')   # ESC-^M is newline
        text = ESC_CTRLZ.sub('', text)   # ESC-^Z is end of string
        text = text.replace('\0', '')   # There can be nul bytes. Remove them.
        text = text.strip()   # Strip leading/trailing whitespace

        return text

    def get_record_field_index(self, fldname):
        """ Return the index number in the record tuple, based on the name. """

        if not fldname in self.nam2idx:
            raise ProgenError(_("Field '%(fldname)s' not found") % locals())

        return self.nam2idx[fldname]

    def convert_record_to_list(self, rec, mems):
        """ Convert records to list. """

        flds = []
        for i in range(len(rec)):
            typ = self.recflds[i].type_
            if typ == 2 or typ == 3 or typ == 22 or typ == 23:
                # Record field is record number
                flds.append("%d" % rec[i])
            elif typ == 46 or typ == 47:
                # Record field is memory type
                flds.append(self.get_mem_text(mems, rec[i]))
            else:
                # Not a record number, not a memory type. It must be just text.
                fld = rec[i].strip()
                fld = fld.decode('cp850')   # Convert to unicode
                flds.append(fld)

        # print(', '.join(flds))
        return flds

    def get_field_names(self):
        """ Return field names. """

        ret = []
        for fld in self.flds:
            if fld.size != 0:
                ret.append(fld.name)

        return ret

    def diag(self):
        """ Diagnostic ... """

        txt = self.name + '\n'
        if 'n_fields' in self.parms:
            txt += 'n_fields = %s\n' % self.parms['n_fields']
            # Just grab a field
            txt += '"%s"\n' % self.flds[1]
            txt += 'recfmt = %s (length=%d)' % \
                   (self.recfmt, struct.calcsize(str(self.recfmt)))

        return txt


class PG30Def(object):
    """
    Utility class to read PG30-1.DEF and to get certain information from it.
    """
    # The contents of the DEF file is separated in sections that start with
    # [<section name>]. For example:
    # [general]
    #    dateformat=DD-MM-YYYY
    #    pointerlength=4
    #    tables=2

    def __init__(self, fname):
        # Read the main DEF file (maybe throw a IOError)
        lines = None
        with open(fname, buffering=1, encoding='cp437', errors='strict') as frame:
            lines = frame.readlines()

        # Analyse the DEF lines
        lines = [l.strip() for l in lines]
        content = '\n'.join(lines)
        parts = re.split(r'\n(?=\[)', content)
        self.parts = {}
        self.tables = {}
        for prts in parts:
            lines = prts.splitlines()

            # Get section names (typically "PRO-GEN", "general",
            # "Table_1", "Table_2", "Genealogical")
            k = re.sub(r'\[(.*)\]', r'\1', lines[0])

            # Store section contents in a hashtable using that section name
            self.parts[k] = lines[1:]
            self.tables[k] = PG30DefTable(k, self.parts[k])

    def __getitem__(self, i):
        return self.tables.get(i, None)

    def __repr__(self):
        return '\n'.join([self.tables[t].diag() for t in self.tables])


# Split surname prefixes
def _split_surname(surname):
    """ Divides prefix from surname. """
    for prefix in PREFIXES:
        if surname.startswith(prefix):
            return prefix.strip(), surname[len(prefix):].strip()

    return '', surname

class ProgenParser(UpdateCallback):
    """
    Main class to parse and import Pro-Gen files.
    """
    def parse_progen_file(self):
        """
        Parse and analyse the Pro-Gen file.
        """
        if not (self.option['prim_person'] or
                self.option['prim_family'] or
                self.option['prim_child']):
            # Nothing to import
            return None

        # Read the stub DEF file (maybe throw a IOError)
        self.fname, dname = _get_defname(self.fname)
        if not self.fname:
            error_msg = ProgenError(_("Not a (right) DEF file: %(dname)s") % locals())
            self.user.notify_error(_("Pro-Gen data error"), str(error_msg))
            # close feedback about import progress (GUI)!
            if self.uistate: self.progress.close()
            return None

        # start feedback about import progress (GUI / TXT)
        self.__display_message(_('Initializing.'), _('Import from Pro-Gen'))
        self.def_ = PG30Def(self.fname)

        # Check correct languages (only 'de', 'en' and 'nl' accepted)
        male_text = self.def_.tables['Genealogical']
        male_text = male_text.parms['field_father'].lower()
        female_text = self.def_.tables['Genealogical']
        female_text = female_text.parms['field_mother'].lower()
        # Double check on keywords
        if male_text == "vater" and female_text == "mutter":
            self.language = 0   # language = 'de'
        elif male_text == "father" and female_text == "mother":
            self.language = 1   # language = 'en'
        elif male_text == "vader" and female_text == "moeder":
            self.language = 2   # language = 'nl'
        else:
            # Raise a error message
            error_msg = ProgenError(_("Not a supported Pro-Gen import file language"))
            self.user.notify_error(_("Pro-Gen data error"), str(error_msg))
            # close feedback about import progress (GUI)
            if self.uistate: self.progress.close()
            return None

        self.mems = _read_mem(self.bname)
        self.pers = _read_recs(self.def_['Table_1'], self.bname, self.mems)
        self.rels = _read_recs(self.def_['Table_2'], self.bname, self.mems)

        # calculate total amount of data
        if not self.uistate:
            # approx. (1x father, 1x mother) + 1.5x child & families
            self.set_total(2.5 * len(self.pers) + len(self.rels))

        self.dbase.disable_signals()
        with DbTxn(_("Pro-Gen import"), self.dbase, batch=True) as self.trans:
            self.create_tags()
            if self.option['prim_person']:
                self.create_persons()
            if self.option['prim_family']:
                self.create_families()
            if self.option['prim_child']:
                self.add_children()
            self.__display_message(_('Saving.'))
        self.dbase.enable_signals()
        self.dbase.request_rebuild()

        # close feedback about import progress (GUI)
        if self.uistate: self.progress.close()

        return self.info

    def __init__(self, data_base, file_name, user, option):
        """
        Pro-Gen defines his own set of (static) person and family identifiers.
        """
        # Sometime their match the Gramps localisation, sometimes not. To be on
        # a safe and uniform path person and family identifiers for (alphabetic)
        # German (de), English (en) and Dutch (nl) language defined here.
        self.bname, ext = os.path.splitext(file_name)
        if ext.lower() in ('.per', '.rel', '.mem'):
            file_name = self.bname + '.def'
        self.dbase = data_base
        self.fname = file_name
        self.user = user
        self.uistate = user.uistate
        self.info = ImportInfo()
        self.option = option
        self.language = 0

        self.mems = None   # Memory area
        self.pers = []   # List for raw person data
        self.rels = []   # List for raw relation data

        self.gid2id = {}  # Maps person id to id
        self.fid2id = {}  # Maps family id to id
        self.fm2fam = {}  # Maps family id to family
        self.pkeys = {}   # Caching place handles
        self.skeys = {}   # Caching source handles
        self.ckeys = {}   # Caching citation handles

        # Miscellaneous
        self.trans = None   # Transaction identifier
        self.def_ = None   # PG30 definitions
        self.high_fam_id = -1

        # Add Config import tag?
        self.tagobject_list = {}

        # Records in the PER file using PG30-1.DEF contain the following fields:
        self.person_identifier = [
            # F00: None
            [""],   # F00

            # F01 - F15: Person ID, Change, First / Last Name, Gender,
            #            Call Name, Alias, Person Code, Titel 1/2/3,
            #            Father, Mother, Occupation
            ["Person_ID", "Person_record", "Persoon record"],   # F01
            ["Person_Änderung", "Person_last_change", "Persoon gewijzigd"], # F02
            ["Vorname", "Given_name", "Voornaam"],   # F03
            ["Nachname", "Surname", "Achternaam"],   # F04
            ["Geschlecht", "Sex", "Geslacht"],   # F05
            ["Patronym", "Patronym", "Patroniem"],   # F06
            ["Rufname", "Call_name", "Roepnaam"],   # F07
            ["Alias", "Alias", "Alias"],   # F08
            ["Person_Code", "Person_code", "Persoon code"],   # F09
            ["Titel1", "Title1", "Titel1"],   # F10
            ["Titel2", "Title2", "Titel2"],   # F11
            ["Titel3", "Title3", "Titel3"],   # F12
            ["Vater", "Father", "Vader"],   # F13
            ["Mutter", "Mother", "Moeder"],   # F14
            ["Beruf", "Occupation", "Beroep"],   # F15

            # F16 - F17: Person Note, Info
            ["Person_Notiz", "Person_scratch", "Persoon klad"],   # F16
            ["Person_Info", "Person_info", "Persoon info"],   # F17

            # F18 - F24: Address Date, Street, ZIP, Place, Country, Phone, Info
            ["Anschrift_Datum", "Address_date", "Adres datum"],   # F18
            ["Anschrift_Straße", "Address_street", "Adres straat"],   # F19
            ["Anschrift_PLZ", "Address_zip", "Adres postcode"],   # F20
            ["Anschrift_Ort", "Address_place", "Adres plaats"],   # F21
            ["Anschrift_Land", "Address_country", "Adres land"],   # F22
            ["Anschrift_Telefon", "Address_phone", "Adres telefoon"],   #
            ["Anschrift_Info", "Address_info", "Adres info"],   # F24

            # F25 - F31: Birth Date, Place, Time, Source, Reference, Text, Info
            ["Geburt_Datum", "Birth_date", "Geboorte datum"],   # F25
            ["Geburt_Ort", "Birth_place", "Geboorte plaats"],   # F26
            ["Geburt_Zeit", "Birth_time", "Geboorte tijd"],   # F27
            ["Geburt_Quelle", "Birth_source", "Geboorte bron"],   # F28
            ["Geburt_Akte", "Birth_ref", "Geboorte akte"],   # F29
            ["Geburt_Text", "Birth_text", "Geboorte brontekst"],   # F30
            ["Geburt_Info", "Birth_info", "Geboorte info"],   # F31

            # F32 - F39: Christening Date, Place, Religion, Witness, Source,
            #                  Reference, Text, Info
            ["Taufe_Datum", "Christening_date", "Doop datum"],   # F32
            ["Taufe_Ort", "Christening_place", "Doop plaats"],   # F33
            ["Religion", "Religion", "Gezindte"],   # F34
            ["Taufe_Paten", "Christening_witness", "Doop getuigen"],   # F35
            ["Taufe_Quelle", "Christening_source", "Doop bron"],   # F36
            ["Taufe_Akte", "Christening_ref", "Doop akte"],   # F37
            ["Taufe_Text", "Christening_text", "Doop brontekst"],   # F38
            ["Taufe_Info", "Christening_info", "Doop info"],   # F39

            # F40 - F46: Death Date, Place, Time, Source, Reference, Text, Info
            ["Sterbe_Datum", "Death_date", "Overlijden datum"],   # F40
            ["Sterbe_Ort", "Death_place", "Overlijden plaats"],   # F41
            ["Sterbe_Zeit", "Death_time", "Overlijden tijd"],   # F42
            ["Sterbe_Quelle", "Death_source", "Overlijden bron"],   # F43
            ["Sterbe_Akte", "Death_ref", "Overlijden akte"],   # F44
            ["Sterbe_Text", "Death_text", "Overlijden brontekst"],   # F45
            ["Sterbe_Info", "Death_info", "Overlijden info"],   # F46

            # F47 - F52: Cremation Date, Place, Source, Reference, Text, Info
            ["Einäscherung_Datum", "Cremation_date", "Crematie datum"],   # F47
            ["Einäscherung_Ort", "Cremation_place", "Crematie plaats"],   # F48
            ["Einäscherung_Quelle", "Cremation_source", "Crematie bron"], # F49
            ["Einäscherung_Akte", "Cremation_ref", "Crematie akte"],   # F50
            ["Einäscherung_Text", "Cremation_text", "Crematie brontekst"], # F51
            ["Einäscherung_Info", "Cremation_info", "Crematie info"],   # F52

            # F53 - F58: Burial Date, Place, Source, Reference, Text, Info
            ["Beerdigung_Datum", "Burial_date", "Begrafenis datum"],   # F53
            ["Beerdigung_Ort", "Burial_place", "Begrafenis plaats"],   # F54
            ["Beerdigung_Quelle", "Burial_source", "Begrafenis bron"],   # F55
            ["Beerdigung_Akte", "Burial_ref", "Begrafenis akte"],   # F56
            ["Beerdigung_Text", "Burial_text", "Begrafenis brontekst"],   # F57
            ["Beerdigung_Info", "Burial_info", "Begrafenis info"],   # F58
        ]

        # Records in the REL file using PG30-1.DEF contain the following fields:
        self.family_identifier = [
            # F00: None
            [""],   # F00

            # F01 - F07: Relation ID, Change, Husband, Wife, Code, Note, Info
            ["Ehe_ID", "Relation_record", "Relatie record"],   # F01
            ["Ehe_Änderung", "Relation_last_change", "Relatie gewijzigd"], # F02
            ["Ehemann", "Husband", "Man"],   # F03
            ["Ehefrau", "Wife", "Vrouw"],   # F04
            ["Ehe_Code", "Relation_code", "Relatie code"],   # F05
            ["Ehe_Notiz", "Relation_scratch", "Relatie klad"],   # F06
            ["Ehe_Info", "Relation_info", "Relatie info"],   # F07

            # F08 - F13: Civil Union Date, Place, Source, Reference, Text, Info
            ["Lebensgem_Datum", "Living_date", "Samenwonen datum"],   # F08
            ["Lebensgem_Ort", "Living_place", "Samenwonen plaats"],   # F09
            ["Lebensgem_Quelle", "Living_source", "Samenwonen bron"],   # F10
            ["Lebensgem_Akte", "Living_ref", "Samenwonen akte"],   # F11
            ["Lebensgem_Text", "Living_text", "Samenwonen brontekst"],   # F12
            ["Lebensgem_Info", "Living_info", "Samenwonen info"],   # F13

            # F14 - F20: Marriage License Date, Place, Witness, Source, Record,
            #                     Text, Info
            ["Aufgebot_Datum", "Banns_date", "Ondertrouw datum"],   # F14
            ["Aufgebot_Ort", "Banns_place", "Ondertrouw plaats"],   # F15
            ["Aufgebot_Zeugen", "Banns_witnesses", "Ondertrouw getuigen"], # F16
            ["Aufgebot_Quelle", "Banns_source", "Ondertrouw bron"],   # F17
            ["Aufgebot_Akte", "Banns_ref", "Ondertrouw akte"],   # F18
            ["Aufgebot_Text", "Banns_text", "Ondertrouw brontekst"],   # F19
            ["Aufgebot_Info", "Banns_info", "Ondertrouw info"],   # F20

            # F14 - F20: Civil Marriage Date, Place, Witness, Source, Record,
            #                  Text, Info
            ["Standesamt_Datum", "Civil_date", "Wettelijk datum"],   # F21
            ["Standesamt_Ort", "Civil_place", "Wettelijk plaats"],   # F22
            ["Standesamt_Zeugen", "Civil_witnesses", "Wettelijk getuigen"], # F23
            ["Standesamt_Quelle", "Civil_source", "Wettelijk bron"],   # F24
            ["Standesamt_Akte", "Civil_ref", "Wettelijk akte"],   # F25
            ["Standesamt_Text", "Civil_text", "Wettelijk brontekst"],   # F26
            ["Standesamt_Info", "Civil_info", "Wettelijk info"],   # F27

            # F28 - F35: Church Wedding Date, Place, Church Name, Witness,
            #                  Source, Reference, Text, Info
            ["Kirche_Datum", "Church_date", "Kerkelijk datum"],   # F28
            ["Kirche_Ort", "Church_place", "Kerkelijk plaats"],   # F29
            ["Kirche", "Church", "Kerk"],               # F30
            ["Kirche_Zeugen", "Church_witnesses", "Kerkelijk getuigen"],   # F31
            ["Kirche_Quelle", "Church_source", "Kerkelijk bron"],   # F32
            ["Kirche_Akte", "Church_ref", "Kerkelijk akte"],   # F33
            ["Kirche_Text", "Church_text", "Kerkelijk brontekst"],   # F34
            ["Kirche_Info", "Church_info", "Kerkelijk info"],   # F35

            # F36 - F41: Divorce Date, Place, Source, Reference, Text, Info
            ["Scheidung_Datum", "Divorce_date", "Scheiding datum"],   # F36
            ["Scheidung_Ort", "Divorce_place", "Scheiding plaats"],   # F37
            ["Scheidung_Quelle", "Divorce_source", "Scheiding bron"],   # F38
            ["Scheidung_Akte", "Divorce_ref", "Scheiding akte"],   # F39
            ["Scheidung_Text", "Divorce_text", "Scheiding brontekst"],   # F40
            ["Scheidung_Info", "Divorce_info", "Scheiding info"],   # F41
        ]

        # provide feedback about import progress (GUI / TXT)
        if self.uistate:
            self.progress = ProgressMeter(_("Import from Pro-Gen"), '',
                                          parent=self.uistate.window)
        else:
            UpdateCallback.__init__(self, user.callback)

    def __add_name(self, person, citationhandle, nametype,
                   firstname, prefix, surname, suffix):
        """
        Add a new name to the object.
        """
        name = Name()
        name.set_type(nametype)
        name.set_first_name(firstname)
        sur_name = Surname()
        sur_name.set_prefix(prefix)
        sur_name.set_surname(surname)
        name.add_surname(sur_name)
        name.set_suffix(suffix)
        if citationhandle:
            name.add_citation(citationhandle)

        person.add_alternate_name(name)

    def __add_tag(self, tag, obj):
        """
        Add the default tag to the object.
        """
        if self.tagobject_list and (tag in self.tagobject_list):
            obj.add_tag(self.tagobject_list[tag].handle)

    def __find_from_handle(self, progen_id, table):
        """
        Find a handle corresponding to the specified Pro-Gen ID.
        """
        # The passed table contains the mapping. If the value is found, we
        # return it, otherwise we create a new handle, store it, and return it.
        intid = table.get(progen_id)
        if not intid:
            intid = create_id()
            table[progen_id] = intid

        return intid

    def __find_person_handle(self, progen_id):
        """
        Return the database handle associated with the person's Pro-Gen ID
        """
        return self.__find_from_handle(progen_id, self.gid2id)

    def __find_family_handle(self, progen_id):
        """
        Return the database handle associated with the family's Pro-Gen ID
        """
        return self.__find_from_handle(progen_id, self.fid2id)

    def __find_or_create_person(self, progen_id):
        """
        Finds or creates a Person based on the Pro-Gen ID.
        """
        # If the ID is already used (= is in the database), return the item in
        # DB. Otherwise, create a new person, assign the handle and Gramps ID.
        person = Person()
        intid = self.gid2id.get(progen_id)
        if self.dbase.has_person_handle(intid):
            person.unserialize(self.dbase.get_raw_person_data(intid))
        else:
            # create a new Person
            gramps_id = self.dbase.id2user_format("I%06d" % progen_id)
            if self.dbase.has_person_gramps_id(gramps_id):
                gramps_id = self.dbase.find_next_person_gramps_id()
            intid = self.__find_from_handle(progen_id, self.gid2id)
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)

            # add info for import statistic
            self.info.add('new-object', PERSON_KEY, None)

        return person

    def __find_or_create_family(self, progen_id):
        """
        Finds or creates a Family based on the Pro-Gen ID.
        """
        family = Family()
        intid = self.fid2id.get(progen_id)
        if self.dbase.has_family_handle(intid):
            family.unserialize(self.dbase.get_raw_family_data(intid))
        else:
            # create a new Family
            gramps_id = self.dbase.fid2user_format("F%04d" % progen_id)
            if self.dbase.has_family_gramps_id(gramps_id):
                gramps_id = self.dbase.find_next_family_gramps_id()
            intid = self.__find_from_handle(progen_id, self.fid2id)
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)

            # add info for import statistic
            self.info.add('new-object', FAMILY_KEY, None)

        return family

    def __get_or_create_place(self, place_name):
        """
        Finds or creates a Place based on the place name.
        """
        if not place_name:
            return None

        if place_name in self.pkeys:
            place = self.dbase.get_place_from_handle(self.pkeys[place_name])
        else:
            # create a new Place
            place = Place()
            place.set_name(PlaceName(value=place_name))
            place.set_title(place_name)
            self.__add_tag('place', place)   # add tag to 'Place'

            self.dbase.add_place(place, self.trans)   # add & commit ...

            self.pkeys[place_name] = place.get_handle()

            # add info for import statistic
            self.info.add('new-object', PLACE_KEY, None)

        return place

    def __get_or_create_citation(self, source_title, date_text,
                                 page_text='', page_ref=''):
        """
        Finds or creates Source & Citation based on:
            Source, Name, Date, Page, Note, Attribute.
        """
        if not source_title:
            return None

        # process Source
        if not self.option['imp_source']:   # No Source enabled
            return None

        if source_title in self.skeys:   # source exists
            source = self.dbase.get_source_from_handle(self.skeys[source_title])
        else:   # create a new source
            source = Source()
            source.set_title(source_title)
            source.private = self.option['imp_source_priv']

            self.__add_tag('source', source)   # add tag to 'Source'

            # process Attribute
            if self.option['imp_source_attr']:
                sattr = SrcAttribute()
                sattr.set_type(_("Source"))
                sattr.set_value(self.option['imp_source_attr'])
                source.add_attribute(sattr)

            self.dbase.add_source(source, self.trans)   # add & commit ...

            self.skeys[source_title] = source.get_handle()

            # add info for import statistic
            self.info.add('new-object', SOURCE_KEY, None)

        # process Citation
        if not self.option['imp_citation']:   # No Citation enabled
            return None

        # process Volume/Page
        page = source_title
        if page_text or page_ref:
            page = '%s %s' % (page_text, page_ref)

        if page in self.ckeys:   # citation exists
            citation = self.dbase.get_citation_from_handle(self.ckeys[page])
        else:   # create a new citation
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            citation.private = self.option['imp_citation_priv']

            self.__add_tag('citation', citation)   # add tag to 'Citation'

            # process Date
            date = self.__create_date_from_text(date_text)
            if date:
                citation.set_date_object(date)

            # process Confidence
            citation.set_confidence_level(self.option['imp_citation_conf'])

            # process Page (substitute string directives)
            if ('%Y' or '%m' or '%d' or '%H' or '%M' or '%S') in page:
                page = time.strftime(page)
            citation.set_page('%s' % page)

            # process Note
            imp_citation_note = ''   # Not yet used
            if imp_citation_note:
                note = self.__create_note(imp_citation_note, NoteType.CUSTOM,
                                          _("Pro-Gen Import"))
                if note and note.handle:
                    citation.add_note(note.handle)

            # process Attribute
            if self.option['imp_citation_attr']:
                sattr = SrcAttribute()
                sattr.set_type(_("Citation"))
                sattr.set_value(self.option['imp_citation_attr'])
                citation.add_attribute(sattr)

            self.dbase.add_citation(citation, self.trans)   # add & commit ...

            self.ckeys[page] = citation.get_handle()

            # add info for import statistic
            self.info.add('new-object', CITATION_KEY, None)

        return citation

    def __create_note(self, note_text, note_type, note_cust=''):
        """
        Create an note base on Type and Text.
        """
        if not note_text:
            return None

        if isinstance(note_text, list):
            note_text = '\n'.join(note_text)

        note = Note()
        note.set(note_text)
        note_type = NoteType()
        note_type.set((note_type, note_cust))

        self.__add_tag('note', note)   # add tag to 'Note'

        self.dbase.add_note(note, self.trans)   # add & commit ...

        # add info for import statistic
        self.info.add('new-object', NOTE_KEY, None)

        return note

    def __create_attribute(self, attr_text, attr_type, attr_cust=''):
        """
        Creates an attribute base on (Custom-)Type and Text.
        """
        if not attr_text:
            return None

        attr = Attribute()
        attr.set_type((attr_type, attr_cust))
        attr.set_value(attr_text)

        return attr

    def __create_event_and_ref(self, type_, desc=None, date=None, place=None,
                               citation=None, note_text=None,
                               attr_text=None, attr_type=None, attr_cust=None):
        """
        Finds or creates an Event based on the Type, Description, Date, Place,
        Citation, Note and Time.
        """
        event = Event()
        event.set_type(EventType(type_))
        self.__add_tag('event', event)   # add tag to 'Event'

        if desc:
            event.set_description(desc)
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if citation:
            event.add_citation(citation.handle)

        attr = self.__create_attribute(attr_text, attr_type, attr_cust)
        if attr:
            event.add_attribute(attr)

        note = self.__create_note(note_text, NoteType.CUSTOM, "Info")
        if note and note.handle:
            event.add_note(note.handle)

        self.dbase.add_event(event, self.trans)   # add & commit ...

        # add info for import statistic
        self.info.add('new-object', EVENT_KEY, None)

        event_ref = EventRef()
        event_ref.set_reference_handle(event.get_handle())

        return event, event_ref

    __date_pat1 = re.compile(r'(?P<day>\d{1,2}) (.|-|=) (?P<month>\d{1,2}) (.|-|=) (?P<year>\d{2,4})',
                             re.VERBOSE)
    __date_pat2 = re.compile(r'(?P<month>\d{1,2}) (.|-|=) (?P<year>\d{4})',
                             re.VERBOSE)
    __date_pat3 = re.compile(r'(?P<year>\d{3,4})', re.VERBOSE)
    __date_pat4_de = re.compile(r'(v|vor|n|nach|ca|circa|etwa|in|um|±) (\.|\s)* (?P<year>\d{3,4})',
                                re.VERBOSE)
    __date_pat4_en = re.compile(r'(b|before|a|after|ab|about|between|±) (\.|\s)* (?P<year>\d{3,4})',
                                re.VERBOSE)
    __date_pat4_nl = re.compile(r'(v|voor|vóór|na|ca|circa|rond|±) (\.|\s)* (?P<year>\d{3,4})',
                                re.VERBOSE)
    __date_pat5 = re.compile(r'(oo|OO) (-|=) (oo|OO) (-|=) (?P<year>\d{2,4})',
                             re.VERBOSE)
    __date_pat6 = re.compile(r'(?P<month>(%s)) (\.|\s)* (?P<year>\d{3,4})' % \
                             '|'.join(list(MONTHES.keys())),
                             re.VERBOSE | re.IGNORECASE)

    def __create_date_from_text(self, date_text, diag_msg=None):
        """
        Finds or creates a Date based on Text, an Offset and a Message.
        """
        # Pro-Gen has a text field for the date.
        # It can be anything (it should be dd-mm-yyyy), but we have seen:
        # yyyy
        # mm-yyyy
        # before yyyy
        # dd=mm-yyyy  (typo I guess)
        # 00-00-yyyy
        # oo-oo-yyyy
        # dd-mm-00 (does this mean we do not know about the year?)

        # Function tries to parse the text and create a proper Gramps Date()
        # object. If all else fails create a MOD_TEXTONLY Date() object.

        dte_txt = date_text == _("Unknown")
        if not (dte_txt or date_text) or date_text == '??':
            return None

        date = Date()

        # dd-mm-yyyy
        dte_mtch = self.__date_pat1.match(date_text)
        if dte_mtch:
            day = int(dte_mtch.group('day'))
            month = int(dte_mtch.group('month'))
            if month > 12:
                month %= 12
            year = int(dte_mtch.group('year'))
            if day and month and year:
                date.set_yr_mon_day(year, month, day)
            else:
                date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                         (day, month, year, 0))
            return date

        # mm-yyyy
        dte_mtch = self.__date_pat2.match(date_text)
        if dte_mtch:
            month = int(dte_mtch.group('month'))
            year = int(dte_mtch.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                     (0, month, year, 0))
            return date

        # yyy or yyyy
        dte_mtch = self.__date_pat3.match(date_text)
        if dte_mtch:
            year = int(dte_mtch.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                     (0, 0, year, 0))
            return date

        # before|after|... yyyy
        if self.language == 0:   # 'de' language
            dte_mtch = self.__date_pat4_de.match(date_text)
        elif self.language == 1:   # 'en' language
            dte_mtch = self.__date_pat4_en.match(date_text)
        elif self.language == 2:   # 'nl' language
            dte_mtch = self.__date_pat4_nl.match(date_text)
        if dte_mtch:
            year = int(dte_mtch.group('year'))
            if dte_mtch.group(1) == 'v' or dte_mtch.group(1) == 'vor' or \
                dte_mtch.group(1) == 'before' or \
                dte_mtch.group(1) == 'voor' or dte_mtch.group(1) == 'vóór':
                date.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN,
                         (0, 0, year, 0))
            elif dte_mtch.group(1) == 'n' or dte_mtch.group(1) == 'nach' or \
                dte_mtch.group(1) == 'after' or \
                dte_mtch.group(1) == 'na':
                date.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN,
                         (0, 0, year, 0))
            else:
                date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                         (0, 0, year, 0))
            return date

        # oo-oo-yyyy
        dte_mtch = self.__date_pat5.match(date_text)
        if dte_mtch:
            year = int(dte_mtch.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                     (0, 0, year, 0))
            return date

        # mmm yyyy (textual month)
        dte_mtch = self.__date_pat6.match(date_text)
        if dte_mtch:
            year = int(dte_mtch.group('year'))
            month = MONTHES.get(dte_mtch.group('month'), 0)
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN,
                     (0, month, year, 0))
            return date

        # Hmmm. Just use the plain text.
        LOG.warning(_("Date did not match: '%(text)s' (%(msg)s)"), \
                {'text' : date_text.encode('utf-8'), 'msg' : diag_msg or ''})
        date.set_as_text(date_text)

        return date

    def __create_desc_from_text(self, desc_txt):
        """
        Creates a variation of a description depending on language
        """
        desc = None
        if desc_txt:
            if self.language == 0:   # 'de' language
                desc = desc_txt + ' Uhr'
            else:
                desc = _('Time: %s') % desc_txt

        return desc

    def __display_message(self, gui_mesg, txt_mesg=None, gui_max=None):
        """
        Display messaging depending of GUI / TXT.
        """
        if self.uistate:
            if gui_max: self.progress.set_pass(gui_mesg, gui_max)
            else: self.progress.set_pass(gui_mesg)
        else:
            if txt_mesg: self.set_text(txt_mesg)
            else: self.set_text(gui_mesg)

    def create_tags(self):
        """
        Creates tags to objects (if provide)
        """
        for tagobj in TAGOBJECTS:
            tagname = 'tag_%s' % tagobj
            if self.option[tagname]:
                # process tagname (substitute string directives)
                tagname = '%s %s' % (_(tagobj).capitalize(), \
                                     self.option[tagname])
                tag = self.dbase.get_tag_from_name(tagname)
                if not tag:
                    tag = Tag()
                    tag.set_name(tagname)
                    self.dbase.add_tag(tag, self.trans)

                    # add info for import statistic
                    self.info.add('new-object', TAG_KEY, None)

                self.tagobject_list[tagobj] = tag

    __rel_pat = re.compile(r'(r|w|)', re.VERBOSE)
    def create_persons(self):
        """
        Method to import Persons
        """
        table = self.def_['Table_1']
        LOG.info(table.get_field_names())

        # We'll start with F02: Person last change
        # Note: We like this to be computed just once.
        person_ix = [0, 0]
        for count in range(2, len(self.person_identifier)):
            # We have seen some case insensitivity in DEF files ...
            pid = self.person_identifier[count][self.language].lower()
            pix = table.get_record_field_index(pid)
            person_ix.append(pix)

        # start feedback about import progress (GUI/TXT)
        self.__display_message(_('Importing persons.'), gui_max=len(self.pers))

        # Male / Female symbols
        male_sym = self.def_.tables['Genealogical'].parms['male']
        female_sym = self.def_.tables['Genealogical'].parms['female']

        ind_id = 0
        for i, rec in enumerate(self.pers):
            # Update at the begin
            self.progress.step() if self.uistate else self.update()

            recflds = table.convert_record_to_list(rec, self.mems)

            # Option: Original Individuals IDs
            if self.option['opt_person-ident']:
                ind_id = int(recflds[person_ix[1]])   # F01: INDI RFN
            else:
                ind_id += 1
            # print(("Ind ID %d " % ind_id) + " ".join(("%s" % r) for r in rec))

            person = self.__find_or_create_person(ind_id)

            # process F03 Given Name, F07 Call Name
            name = Name()
            name.set_type(NameType.BIRTH)

            first_name = recflds[person_ix[3]]   # F03: TBD
            if first_name:
                # replace if necessary separators with ' '
                first_name = re.sub(r'[,;]', ' ', first_name)
            else:
                # default first name 'Nomen nominandum'
                first_name = 'N.N.'
            name.set_first_name(first_name)

            # process F04 Last Name
            sur_prefix, sur_name = '', ''
            if recflds[person_ix[4]]:
                # F04: INDI NAME
                sur_prefix, sur_name = _split_surname(recflds[person_ix[4]])
            if not sur_name:
                # default surname 'Nomen nominandum'
                sur_name = 'N.N.'
            surname = Surname()
            surname.set_surname(sur_name)
            if sur_prefix:
                surname.set_prefix(sur_prefix)
            name.add_surname(surname)

            # process F06 Patronym
            patronym = recflds[person_ix[6]]   # F06: INDI _PATR
            if patronym:
                patronym_name = Surname()
                patronym_name.set_surname(patronym)
                patronym_name.set_origintype(NameOriginType.PATRONYMIC)
                name.add_surname(patronym_name)

            # process F10 - F12 Title(s)
            title1 = recflds[person_ix[10]]   # F10: INDI TITL
            title2 = recflds[person_ix[11]]   # F11: INDI _TITL2
            title3 = recflds[person_ix[12]]   # F12: INDI _TITL3
            title = [_f for _f in [title1, title2, title3] if _f]
            if title:
                name.set_title(", ".join(title))

            # General config: addtional individual citation
            if self.option['imp_source_title']:
                # Original individual ID from source
                pageref = '[ID: I%06d] %s, %s' % (i +1, sur_name, first_name)
                citation = self.__get_or_create_citation \
                    (self.option['imp_source_title'],
                     recflds[person_ix[2]],   # F02: INDI CHAN DATE
                     self.option['imp_citation_page'], pageref)
                if citation and citation.handle:
                    person.add_citation(citation.handle)
                    name.add_citation(citation.handle)

            # add tag to 'Person'
            self.__add_tag('person', person)

            # create diagnose message
            diag_msg = "%s: %s %s" % (person.gramps_id,
                                      first_name.encode('utf-8'),
                                      sur_name.encode('utf-8'))

            # prcesss F25 Birth Date
            birth_date = self.__create_date_from_text \
                            (recflds[person_ix[25]], diag_msg)   # F25: ... DATE

            # process F07 Call Name
            if recflds[person_ix[7]]:
                # F07: INDI NAME NICK/INDI NAME ALIA/INDI CHR NICK
                name.set_call_name(recflds[person_ix[7]])
            else:
                nick_name = first_name.split(' ')
                if birth_date and len(nick_name) > 1:   # Two or more firstnames
                    number = 0   # Firstname number
                    if birth_date.dateval[2] < 1900:   # 1900: Common edge date
                        number = 1
                    name.set_call_name(nick_name[number])

            # set the Person in database
            person.set_primary_name(name)

            # process F05 Gender
            gender = recflds[person_ix[5]]  # F05: INDI SEX
            if gender == male_sym:
                gender = Person.MALE
            elif gender == female_sym:
                gender = Person.FEMALE
            else:
                gender = Person.UNKNOWN
            person.set_gender(gender)

            # process F08 Alias
            # F08: INDI NAME _ALIA / INDI NAME COMM
            alias = recflds[person_ix[8]]
            if alias:
                # expand separator with ' '
                alias = re.sub(r'\.', '. ', alias)
                alias_text = alias.split()
                # two ways: Attribute-Nickname or AKA-Name
                if len(alias_text) == 1:
                    attr = self.__create_attribute(alias,
                                                   AttributeType.NICKNAME)
                    if attr:
                        person.add_attribute(attr)
                else:
                    self.__add_name(
                        person, citation.handle if citation else None,
                        NameType.AKA, ' '.join(alias_text[0:-1]),
                        '', alias_text[-1], '')

            # process F09 Person Code
            refn_code = recflds[person_ix[9]]   # F09: INDI REFN/INDI CODE
            if refn_code:
                # We have seen some artefacts ...
                rel_cde = self.__rel_pat.match(refn_code)
                # Option: Reference code contains one/two letters
                if self.option['opt_refn-code'] and rel_cde:
                    attr = self.__create_attribute(refn_code,
                                                   AttributeType.CUSTOM,
                                                   "REFN")
                    if attr:
                        person.add_attribute(attr)

            # process F15 Occupation
            occupation = recflds[person_ix[15]]   # F15: INDI OCCU
            if occupation:
                dummy, event_ref = self.__create_event_and_ref \
                    (EventType.OCCUPATION, occupation)
                if event_ref:
                    person.add_event_ref(event_ref)

            # process F16 Person Comment, F17 Person Note
            comm = recflds[person_ix[16]]   # F16: INDI _COMM / INDI COMM
            note = recflds[person_ix[17]]   # F17: INDI NOTE
            note_text = [_f for _f in [comm, note] if _f]
            note = self.__create_note(note_text, NoteType.PERSON)
            if note and note.handle:
                person.add_note(note.handle)

            # process F18 - F24 Address Date, Place, Street, ZIP, Country,
            #                   Phone, Info
            # GEDCOM symbols: INDI RESI ...
            date = self.__create_date_from_text \
                (recflds[person_ix[18]], diag_msg)   # F18: ... DATE
            street = recflds[person_ix[19]]   # F19: ... ADDR
            # F20: ... ADDR POST/INDI RESI POST
            postal_code = recflds[person_ix[20]]
            # F21: ... ADDR CITY/INDI RESI PLAC
            place = self.__get_or_create_place(recflds[person_ix[21]])
            # F22: ... ADDR CTRY/INDI RESI CTRY
            country = recflds[person_ix[22]]
            # F23: ... PHON/INDI PHON
            phone = recflds[person_ix[23]]
            # F24: I... NOTE / INDI ADDR
            info = recflds[person_ix[24]]

            address = None
            if street or postal_code or country or phone:
                # Create address
                address = Address()
                if date:
                    address.set_date_object(date)
                if street:
                    address.set_street(street)
                if recflds[person_ix[21]]:
                    address.set_city(recflds[person_ix[21]])
                if postal_code:            # Debugging!
                    address.set_postal_code(postal_code)
                if country:
                    address.set_country(country)
                if phone:
                    address.set_phone(phone)

                # Option 1: add Notes to Address
                note = self.__create_note(info, NoteType.ADDRESS)
                if note and note.handle:
                    address.add_note(note.handle)
                    info = None

                person.add_address(address)

            if place:
                desc = ''
                if address and date:
                    desc = _('see address on ')
                    desc += displayer.display(date)
                elif address:
                    desc = _('see also address')
                dummy, resi_ref = self.__create_event_and_ref \
                    (EventType.RESIDENCE, desc, date, place, '', info)
                if resi_ref:
                    person.add_event_ref(resi_ref)

            # process F25 - F31 Birth Date, Place, Time, Source, Reference,
            #                   Text, Info
            # GEDCOM symbols: INDI BIRT ...
            # date = self.__create_date_from_text \ # Birth Date processed above
            #     (recflds[person_ix[25]], diag_msg)   # F25: ... DATE
            place = self.__get_or_create_place \
                (recflds[person_ix[26]])   # F26: ... PLAC
            birth_time = recflds[person_ix[27]]   # F27: ... TIME
            source = recflds[person_ix[28]]   # F28: ... SOUR / ... SOUR TITL
            source_refn = recflds[person_ix[29]]   # F29: ... SOUR REFN
            source_text = recflds[person_ix[30]]   # F30: ... SOUR TEXT
            info = recflds[person_ix[31]]   # F31: INDI ... NOTE
            citation = self.__get_or_create_citation \
                (source, recflds[person_ix[25]], source_refn)

            if birth_date or place or info or citation:
                desc = source_text
                # Option: Birth time in description
                if self.option['opt_birth-date']:
                    time_text = self.__create_desc_from_text(birth_time)
                    desc += '; %s' % time_text
                dummy, birth_ref = self.__create_event_and_ref \
                    (EventType.BIRTH, desc, birth_date, place, citation, info,
                     birth_time, AttributeType.TIME)
                if birth_ref:
                    person.set_birth_ref(birth_ref)

            # process F32 - F37 Baptism / Christening Date, Place, Religion,
            #                   Source, Reference, Text, Info
            # GEDCOM symbols: INDI CHR ...
            date = self.__create_date_from_text \
                (recflds[person_ix[32]], diag_msg)   # F32: ... DATE
            place = self.__get_or_create_place \
                (recflds[person_ix[33]])   # F33: ... PLAC
            religion = recflds[person_ix[36]]   # F34: ... RELI / INDI RELI
            witness = recflds[person_ix[35]]   # F35: ... _WITN / ... WITN
            source = recflds[person_ix[36]]   # F36: ... SOUR / ... SOUR TITL
            source_refn = recflds[person_ix[37]]   # F37: ... SOUR REFN
            source_text = recflds[person_ix[38]]   # F38: ... SOUR TEXT
            info = recflds[person_ix[39]]   # F39: ... NOTE
            citation = self.__get_or_create_citation \
                (source, recflds[person_ix[32]], source_refn)

            if date or place or info or citation:
                dummy, chris_ref = self.__create_event_and_ref \
                    (EventType.CHRISTEN, source_text, date, place, citation,
                     info, witness, AttributeType.CUSTOM, _("Godfather"))
                if chris_ref:
                    person.add_event_ref(chris_ref)

            # process F34 Religion
            if religion:
                citation = None
                if source != religion:
                    citation = self.__get_or_create_citation \
                        (religion, recflds[person_ix[32]], source_refn)
                dummy, reli_ref = self.__create_event_and_ref \
                    (EventType.RELIGION, '', date, '', citation)
                if reli_ref:
                    person.add_event_ref(reli_ref)

            # process F40 - F46 Death Date, Place, Time, Source, Reference,
            #                   Text, Info
            # GEDCOM symbols: INDI DEAT ...
            date = self.__create_date_from_text \
                (recflds[person_ix[40]], diag_msg)   # F40: ... DATE
            place = self.__get_or_create_place \
                (recflds[person_ix[41]])   # F41: ... PLAC
            death_time = recflds[person_ix[42]]   # F42: ... TIME
            source = recflds[person_ix[43]]   # F43: ... SOUR / ... SOUR TITL
            source_refn = recflds[person_ix[44]]   # F44: ... SOUR REFN
            source_text = recflds[person_ix[45]]   # F45: ... SOUR TEXT
            info = recflds[person_ix[46]]   # F46: ... NOTE
            citation = self.__get_or_create_citation \
                (source, recflds[person_ix[40]], source_refn)

            if date or place or info or citation:
                desc = source_text
                # Option: Death time in description
                if self.option['opt_death-date']:
                    time_text = self.__create_desc_from_text(death_time)
                    desc += '; %s' % time_text
                if not self.option['opt_death-cause']:
                    desc += ' (%s)' % info
                dummy, death_ref = self.__create_event_and_ref \
                    (EventType.DEATH, desc, date, place, citation, None,
                     death_time, AttributeType.TIME)
                if death_ref:
                    person.set_death_ref(death_ref)

            # Option: Death info to Death cause
            if source_text or (self.option['opt_death-cause'] and info):
                desc = [_f for _f in [source_text, info] if _f]
                desc = desc and '; '.join(desc) or None
                if _('Death cause') in desc:
                    desc = desc[13:].strip()

                dummy, event_ref = self.__create_event_and_ref \
                    (EventType.CAUSE_DEATH, desc)
                if event_ref:
                    person.add_event_ref(event_ref)

            # process F47 - F52 Cremation Date, Place, Source, Reference,
            #                   Text, Info
            # GEDCOM symbols: INDI CREM ...
            date = self.__create_date_from_text \
                (recflds[person_ix[47]], diag_msg)   # F47: ... DATE
            place = self.__get_or_create_place \
                (recflds[person_ix[48]])   # F48: ... PLAC
            source = recflds[person_ix[49]]   # F49: ... SOUR / ... SOUR TITL
            source_refn = recflds[person_ix[50]]   # F50: ... SOUR REFN
            source_text = recflds[person_ix[51]]   # F51: ... SOUR TEXT
            info = recflds[person_ix[52]]   # F52: ... INFO
            citation = self.__get_or_create_citation \
                (source, recflds[person_ix[47]], source_refn)

            if date or place or info or citation:
                dummy, cremation_ref = self.__create_event_and_ref \
                    (EventType.CREMATION, source_text, date, place, citation,
                     info)
                if cremation_ref:
                    person.add_event_ref(cremation_ref)

            # process F53 Burial Date, F54 Burial Place, F55 Burial Source,
            # F56 Burial Reference, F57 Burial Text, F58 Burial Info
            # GEDCOM symbols: INDI BURI ...
            date = self.__create_date_from_text \
                (recflds[person_ix[53]], diag_msg)   # F53: ... DATE
            place = self.__get_or_create_place \
                (recflds[person_ix[54]])   # F54: ... PLAC
            source = recflds[person_ix[55]]   # F49: ... SOUR / ... SOUR TITL
            source_refn = recflds[person_ix[56]]   # F50: ... SOUR REFN
            source_text = recflds[person_ix[57]]   # F51: ... SOUR TEXT
            info = recflds[person_ix[58]]   # F58: ... INFO
            citation = self.__get_or_create_citation \
                (source, recflds[person_ix[53]], source_refn)

            if date or place or info or citation:
                dummy, buri_ref = self.__create_event_and_ref \
                    (EventType.BURIAL, source_text, date, place, citation, info)
                if buri_ref:
                    person.add_event_ref(buri_ref)

            # commit the Person
            self.dbase.commit_person(person, self.trans)

    def create_families(self):
        """
        Method to import Families
        """
        table = self.def_['Table_2']
        LOG.info(table.get_field_names())

        # We'll start with F03: Husband
        # Note: We like this to be computed just once.
        family_ix = [0, 0]
        for count in range(2, len(self.family_identifier)):
            # We've seen some case insensitivity in DEF files ...
            fid = self.family_identifier[count][self.language].lower()
            fix = table.get_record_field_index(fid)
            family_ix.append(fix)

        # start feedback about import progress (GUI/TXT)
        self.__display_message(_('Importing families.'), gui_max=len(self.rels))

        fam_id = 0
        for i, rec in enumerate(self.rels):
            # Update at the begin
            self.progress.step() if self.uistate else self.update()

            husband = rec[family_ix[3]]   # F03: FAM HUSB
            wife = rec[family_ix[4]]   # F04: FAM WIFE

            if husband > 0 or wife > 0:
                recflds = table.convert_record_to_list(rec, self.mems)

                # Option: Original family IDs
                if self.option['opt_family-ident']:
                    fam_id = int(recflds[family_ix[1]])   # F01: FAM RFN
                else:
                    fam_id += 1

                self.high_fam_id = fam_id
                family = self.__find_or_create_family(fam_id)

                # process F03 / F04 Husband / Wife
                husband_handle = None
                if husband > 0:
                    husband_handle = self.__find_person_handle(husband)
                    family.set_father_handle(husband_handle)
                    husband_person = self.dbase.get_person_from_handle(husband_handle)
                    husband_person.add_family_handle(family.get_handle())
                    self.dbase.commit_person(husband_person, self.trans)
                wife_handle = None
                if wife > 0:
                    wife_handle = self.__find_person_handle(wife)
                    family.set_mother_handle(wife_handle)
                    wife_person = self.dbase.get_person_from_handle(wife_handle)
                    wife_person.add_family_handle(family.get_handle())
                    self.dbase.commit_person(wife_person, self.trans)

                # Optional: Husband changes Surname (e.g. marriage)
                if (husband > 0) and self.option['opt_surname-male']:
                    citation_handle = wife_person.get_citation_list()[0] \
                        if husband_person.citation_list else None
                    self.__add_name(husband_person, citation_handle,
                        NameType.MARRIED,
                        husband_person.primary_name.get_first_name(),
                        husband_person.primary_name.surname_list[0].prefix,
                        wife_person.primary_name.get_surname(),
                        husband_person.primary_name.get_suffix())
                    # commit the Person
                    self.dbase.commit_person(husband_person, self.trans)

                # Optional: Wife changes Surname (e.g. marriage)
                if (wife > 0) and self.option['opt_surname-female']:
                    citation_handle = wife_person.get_citation_list()[0] \
                        if wife_person.citation_list else None
                    self.__add_name(wife_person, citation_handle,
                        NameType.MARRIED,
                        wife_person.primary_name.get_first_name(),
                        wife_person.primary_name.surname_list[0].prefix,
                        husband_person.primary_name.get_surname(),
                        wife_person.primary_name.get_suffix())
                    # commit the Person
                    self.dbase.commit_person(wife_person, self.trans)

                self.fm2fam[husband_handle, wife_handle] = family
                diag_msg = "%s: %s %s" % \
                    (family.gramps_id,
                     husband_person.gramps_id if husband_handle else "",
                     wife_person.gramps_id if wife_handle else "")

                # Option: Addtional family citation
                if self.option['imp_source_title']:
                    husband_name = husband_person.get_primary_name()
                    husband_name = husband_name.get_surname()
                    wife_name = wife_person.get_primary_name()
                    wife_name = wife_name.get_surname()
                    # Original family ID from source
                    pageref = '[ID: F%05d] %s -- %s' % \
                        (i +1, husband_name, wife_name)
                    citation = self.__get_or_create_citation \
                        (self.option['imp_source_title'],
                         recflds[family_ix[2]],   # F02: FAM CHAN DATE
                         self.option['imp_citation_page'], pageref)
                    if citation and citation.handle:
                        family.add_citation(citation.handle)

                # add tag to 'Family'
                self.__add_tag('family', family)

                # process F08 - F13 Civil Union Date, Place, Source,
                #                   Reference, Text, Info
                # GEDCOM symbols: FAM _LIV ...
                date = self.__create_date_from_text \
                    (recflds[family_ix[8]], diag_msg)   # F08: ... DATE
                place = self.__get_or_create_place \
                    (recflds[family_ix[9]])   # F09: ... PLAC
                # F10: ... SOUR/FAM _LIV SOUR TITL
                source = recflds[family_ix[10]]
                source_refn = recflds[family_ix[11]]   # F11: ... SOUR REFN
                source_text = recflds[family_ix[12]]   # F12: ... SOUR TEXT
                info = recflds[family_ix[13]]   # F13: ... NOTE
                citation = self.__get_or_create_citation \
                    (source, recflds[family_ix[8]], source_refn)

                if date or place or info or citation:
                    evt_type = _('Civil union')
                    event, civu_ref = self.__create_event_and_ref \
                        (EventType.UNKNOWN, source_text, date, place, citation,
                         info)
                    event.set_type((EventType.CUSTOM, evt_type))
                    if civu_ref:
                        family.add_event_ref(civu_ref)

                    # Type of relation
                    famreltype = FamilyRelType.CIVIL_UNION
                    family.set_relationship(FamilyRelType(famreltype))

                # process F14 - F20 Marriage License Date, Place, Witness,
                #                   Source, Reference, Text, Info
                # GEDCOM symbols: FAM MARB ...
                # F14: ... DATE/FAM REGS DATE
                date = self.__create_date_from_text \
                    (recflds[family_ix[14]], diag_msg)
                # F15: ... PLAC/FAM REGS PLAC
                place = self.__get_or_create_place(recflds[family_ix[15]])
                # F16: ... _WITN/FAM MARB WITN
                witness = recflds[family_ix[16]]
                # F17: ... SOUR/FAM MARB SOUR TITL/FAM REGS SOUR
                source = recflds[family_ix[17]]
                # F18: ... SOUR REFN/FAM REGS SOUR REFN
                source_refn = recflds[family_ix[18]]
                # F19: ... SOUR TEXT
                source_text = recflds[family_ix[19]]
                # F20: ... NOTE
                info = recflds[family_ix[20]]
                citation = self.__get_or_create_citation \
                    (source, recflds[family_ix[14]], source_refn)

                if date or place or info or citation:
                    desc = source_text
                    desc = [_f for _f in [source_text, info] if _f]
                    desc = desc and '; '.join(desc) or None
                    dummy, marl_ref = self.__create_event_and_ref \
                        (EventType.MARR_BANNS, desc, date, place, citation, '',
                         witness, AttributeType.WITNESS)
                    if marl_ref:
                        family.add_event_ref(marl_ref)

                # process F21 - F27 Civil Marriage Date, Place, Witness,
                #                   Source, Reference, Text, Info
                # GEDCOM symbols: FAM MARR(Civil) ...
                # F21: ... DATE/FAM MARR DATE
                date = self.__create_date_from_text \
                    (recflds[family_ix[21]], diag_msg)
                # F22: ... PLAC/FAM MARR PLAC
                place = self.__get_or_create_place(recflds[family_ix[22]])
                # F23: ... _WITN/FAM MARR _WITN/FAM MARR WITN/FAM WITN
                witness = recflds[family_ix[23]]
                # F24: ... SOUR/FAM MARR SOUR/FAM MARR SOUR TITL
                source = recflds[family_ix[24]]
                # F25: ... SOUR REFN/FAM MARR SOUR REFN
                source_refn = recflds[family_ix[25]]
                # F26: ... SOUR TEXT/FAM MARR SOUR TEXT
                source_text = recflds[family_ix[26]]
                info = recflds[family_ix[27]]   # F27: ... NOTE
                citation = self.__get_or_create_citation \
                    (source, recflds[family_ix[21]], source_refn)

                if date or place or info or citation:
                    desc = source_text
                    if not desc:
                        # 'Civil' is widely accepted and language independent
                        desc = "Civil"
                    dummy, mar_ref = self.__create_event_and_ref \
                        (EventType.MARRIAGE, desc, date, place, citation, info,
                         witness, AttributeType.WITNESS)
                    if mar_ref:
                        family.add_event_ref(mar_ref)

                    # Type of relation
                    famreltype = FamilyRelType.MARRIED
                    family.set_relationship(FamilyRelType(famreltype))

                # process F28 - F35 Church Wedding Date, Place, Church, Witness,
                #                   Source, Reference, Text, Info
                # GEDCOM symbols: FAM MARR(Church) ...
                # F28: ... DATE / FAM ORDI DATE
                wedding_date = self.__create_date_from_text \
                    (recflds[family_ix[28]], diag_msg)
                # F29: ... DATE / FAM ORDI PLACE
                place = self.__get_or_create_place(recflds[family_ix[29]])
                # F30: ... _CHUR / FAM ORDI _CHUR / FAM ORDI RELI
                church = recflds[family_ix[30]]
                # F31: ... _WITN / FAM ORDI _WITN / FAM ORDI WITN
                witness = recflds[family_ix[31]]
                # F32: ... SOUR / FAM ORDI SOUR / FAM ORDI SOUR TITL
                source = recflds[family_ix[32]]
                # F33: ... SOUR REFN / FAM ORDI SOUR REFN
                source_refn = recflds[family_ix[33]]
                # F34: ... SOUR TEXT / FAM ORDI SOUR TEXT
                source_text = recflds[family_ix[34]]
                # F35 ... INFO
                info = recflds[family_ix[35]]
                citation = self.__get_or_create_citation \
                    (source, recflds[family_ix[28]], source_refn)

                if wedding_date or place or info or citation:
                    desc = [_f for _f in [church, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    if not desc:
                        desc = _('Wedding')
                    dummy, marc_ref = self.__create_event_and_ref \
                        (EventType.MARRIAGE, desc, wedding_date, place,
                         citation, info, witness, AttributeType.WITNESS)
                    if marc_ref:
                        family.add_event_ref(marc_ref)

                    # Type of relation
                    famreltype = FamilyRelType.MARRIED
                    family.set_relationship(FamilyRelType(famreltype))

                # process F05 - F07 Relation Code, Note, Info
                refn_code = recflds[family_ix[5]]   # F05: FAM REFN / FAM CODE
                if refn_code:
                    # We have seen some artefacts ...
                    rel_cde = self.__rel_pat.match(refn_code)
                    # Option: Reference code contains one/two letters
                    if self.option['opt_refn-code'] and rel_cde:
                        attr = self.__create_attribute(refn_code,
                                                       AttributeType.CUSTOM,
                                                       "REFN")
                        if attr:
                            family.add_attribute(attr)

                comm = recflds[family_ix[6]]   # F06: FAM _COMM/FAM COMM
                note = recflds[family_ix[7]]   # F07: FAM NOTE
                note_text = [_f for _f in [comm, note] if _f]
                if note_text:
                    cnt = None
                    if len(note_text) > 0:
                        note_cont = (' '.join(note_text)).split(' ')
                    else:
                        note_cont = note_text.split(' ')
                    if note_cont[0] == _('Residence'):
                        cnt = 1
                    elif note_cont[0] == _('future') and \
                         note_cont[1] == _('Residence'):
                        cnt = 2
                    else:
                        note = self.__create_note(note_text, NoteType.FAMILY)
                        if note and note.handle:
                            family.add_note(note.handle)

                    if cnt:
                        if wedding_date:
                            date_text = _('after') + ' ' + \
                                str(wedding_date.dateval[2])   # Wedding Year
                            # F28: ... DATE / FAM ORDI DATE
                            date = self.__create_date_from_text \
                                (date_text, diag_msg)
                        place_text = ''
                        # Add all elements of Note Content
                        for i in range(cnt, len(note_cont)):
                            place_text += note_cont[i] + ' '
                        place_text = place_text.rstrip()   # Strip whitespace
                        place = self.__get_or_create_place(place_text)
                        dummy, place_ref = self.__create_event_and_ref \
                            (EventType.RESIDENCE, None, date, place, citation)
                        if place_ref:
                            family.add_event_ref(place_ref)

                # process F36 - F41 Divorce Date, Place, Source, Text,
                #                   Reference, Info
                # GEDCOM symbols: FAM DIV ...
                # F36: ... DATE / FAM DIVO DATE
                date = self.__create_date_from_text \
                    (recflds[family_ix[36]], diag_msg)
                # F37: ... PLAC / FAM DIVO PlAC
                place = self.__get_or_create_place(recflds[family_ix[37]])
                # F38: ... SOUR / FAM DIV SOUR TITL
                source = recflds[family_ix[38]]
                # F39: ... SOUR REFN
                source_refn = recflds[family_ix[39]]
                # F40: ... SOUR TEXT
                source_text = recflds[family_ix[40]]
                # F41: ... INFO
                info = recflds[family_ix[41]]
                citation = self.__get_or_create_citation \
                    (source, recflds[family_ix[36]], source_refn)

                if date or place or info or citation:
                    desc = source_text
                    dummy, div_ref = self.__create_event_and_ref \
                        (EventType.DIVORCE, desc, date, place, citation, info)
                    if div_ref:
                        family.add_event_ref(div_ref)

                # commit the Family
                self.dbase.commit_family(family, self.trans)

                # add info for import statistic
                self.info.add('new-object', FAMILY_KEY, None)

    def add_children(self):
        """
        Method to add Children.
        """
        # Once more to record the father and mother
        table = self.def_['Table_1']

        # We have seen some case insensitivity in DEF files ...
        person_F13 = table.get_record_field_index \
            (self.person_identifier[13][self.language].lower())   # F13: Father
        person_F14 = table.get_record_field_index \
            (self.person_identifier[14][self.language].lower())   # F14: Mother

        # start feedback about import progress (GUI/TXT)
        self.__display_message(_('Adding children.'),
                               gui_max=len(self.pers) *0.6)

        ind_id = 0
        for dummy, rec in enumerate(self.pers):
            # Update at the begin
            self.progress.step() if self.uistate else self.update()

            father = rec[person_F13]   # F13: Father
            mother = rec[person_F14]   # F14: Mother
            if father > 0 or mother > 0:
                recflds = table.convert_record_to_list(rec, self.mems)

                # Option: Original Individuals IDs
                if self.option['opt_person-ident']:
                    ind_id = int(recflds[0])   # F01: INDI RFN
                else:
                    ind_id += 1

                # Find the family with this Father and Mother
                child_handle = self.__find_person_handle(ind_id)
                father_handle = father > 0 and \
                    self.__find_person_handle(father) or None
                mother_handle = mother > 0 and \
                    self.__find_person_handle(mother) or None
                if father > 0 and not father_handle:
                    LOG.warning(_("Cannot find father for I%(person)s (Father=%(father))"), \
                                {'person':ind_id, 'father':father})
                elif mother > 0 and not mother_handle:
                    LOG.warning(_("Cannot find mother for I%(person)s (Mother=%(mother))"), \
                                {'person':ind_id, 'mother':mother})
                else:
                    family = self.fm2fam.get((father_handle, mother_handle), None)
                    if not family:
                        # Family not present in REL. Create a new one.
                        self.high_fam_id += 1
                        fam_id = self.high_fam_id
                        family = self.__find_or_create_family(fam_id)

                        if father_handle:
                            family.set_father_handle(father_handle)
                            try:
                                father_person = self.dbase.get_person_from_handle \
                                    (father_handle)
                                father_person.add_family_handle(family.get_handle())
                                # commit the Father
                                self.dbase.commit_person(father_person, self.trans)
                            except HandleError:
                                LOG.warning("Failed to add father %s to child %s", \
                                            father, ind_id)

                        if mother_handle:
                            family.set_mother_handle(mother_handle)
                            try:
                                mother_person = self.dbase.get_person_from_handle \
                                    (mother_handle)
                                mother_person.add_family_handle(family.get_handle())
                                # commit the Mother
                                self.dbase.commit_person(mother_person, self.trans)
                            except HandleError:
                                LOG.warning("Failed to add mother %s to child %s", \
                                            mother, ind_id)

                if family:
                    childref = ChildRef()
                    childref.set_reference_handle(child_handle)
                    if childref:
                        family.add_child_ref(childref)
                        # commit the Family
                        self.dbase.commit_family(family, self.trans)

                    try:
                        child = self.dbase.get_person_from_handle(child_handle)
                        if child:
                            child.add_parent_family_handle(family.get_handle())
                            # commit the Child
                            self.dbase.commit_person(child, self.trans)
                    except HandleError:
                        LOG.warning("Failed to add child %s to family", ind_id)
