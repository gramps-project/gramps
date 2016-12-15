# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008-2011  Kees Bakker
# Copyright (C) 2008       Brian G. Matherly
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
import re
import os
import struct
import sys

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger('.ImportProGen')

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.utils.id import create_id
from gramps.gui.utils import ProgressMeter
from gramps.gen.lib import (Attribute, AttributeType, ChildRef, Date, Event, 
                            EventRef, EventType, Family, FamilyRelType, Name, 
                            NameType, Note, NoteType, Person, Place, Source, 
                            SrcAttribute, Surname, Citation, Location, NameOriginType)
from gramps.gen.db import DbTxn
from gramps.gen.utils.libformatting import ImportInfo

class ProgenError(Exception):
    """Error used to report Progen errors."""
    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value


def _importData(database, filename, user):

    try:
        g = ProgenParser(database, filename)
    except IOError as msg:
        user.notify_error(_("%s could not be opened") % filename, str(msg))
        return

    try:
        status = g.parse_progen_file()
    except ProgenError as msg:
        user.notify_error(_("Pro-Gen data error"), str(msg))
        return
    except IOError as msg:
        user.notify_error(_("%s could not be opened") % filename, str(msg))
        return
    return ImportInfo({_("Results"): _("done")})


def _find_from_handle(progen_id, table):
    """
    Find a handle corresponding to the specified Pro-Gen ID. 
    
    The passed table contains the mapping. If the value is found, we return 
    it, otherwise we create a new handle, store it, and return it.
    
    """
    intid = table.get(progen_id)
    if not intid:
        intid = create_id()
        table[progen_id] = intid
    return intid


def _read_mem(bname):
    '''
    Each record is 32 bytes. First a 4 byte reference to the next record
    followed by 28 bytes of text.
    The information forms a chain of records, that stops when a reference is 0
    or smaller.
    There are two special sequences:
    <ESC> <CR> hard return
    <ESC> <^Z> end of the memo field
    '''
    if os.path.exists(bname + '.MEM'):
        fname = bname + '.MEM'
    else:
        fname = bname + '.mem'
    f = open(fname, "rb")
    log.debug("The current system is %s-endian" % sys.byteorder)
    # The input file comes from [what was originally] a DOS machine so will
    # be little-endian, regardless of the 'native' byte order of the host
    # system
    recfmt = "<i28s"
    reclen = struct.calcsize( str(recfmt) )
    #print("# reclen = %d" % reclen)

    mems = []
    while 1:
        buf = f.read(reclen)
        if not buf:
            break
        (recno, text) = struct.unpack(recfmt, buf)
        mems.append([recno, text])
    return mems


def _read_recs(table, bname):
    'Read records from .PER or .REL file.'
    if os.path.exists(bname + table.fileext):
        fname = bname + table.fileext
    else:
        fname = bname + table.fileext.lower()
    f = open(fname, "rb")
    recfmt = table.recfmt
    log.info("# %s - recfmt = %s" % (table['name1'], recfmt))
    reclen = struct.calcsize(str(recfmt))
    log.info("# %s - reclen = %d" % (table['name1'], reclen))

    recs = []
    while 1:
        buf = f.read(reclen)
        if not buf:
            break
        tups = struct.unpack(recfmt, buf)
        recs.append(tups)

    log.info("# length %s.recs[] = %d" % (table['name1'], len(recs)))
    return recs


def _get_defname(fname):
    """
    Get the name of the PG30 DEF file by looking at the user DEF file. And return
    the name of the DEF file. fname is expected to be somewhere in the PG30 tree.

    Contents of <fname> is something like:
        => \\0
        => C:\\PG30\\NL\\PG30-1.DEF

    We will strip the C: and convert the rest to a native pathname. Next, this pathname
    is compared with <fname>.
    """
    lines = open(fname).readlines()
    if not lines[0].startswith(r'\0') or len(lines) < 2:
        raise ProgenError(_("Not a Pro-Gen file"))
        return None, '?'

    defname = lines[1]
    defname = defname.strip()
    # Strip drive, if any
    defname = re.sub( r'^\w:', '', defname )
    defname = defname.replace('\\', os.sep)
    # Strip leading slash, if any.
    if defname.startswith(os.sep):
        defname = defname[1:]
    #log.warning('_get_defname: fname=%(fname)s => defname=%(defname)s' % vars())

    # Using the directory of <fname>, go to the parent directory until
    # the DEF is found.
    dir_, f = os.path.split(os.path.abspath(fname))
    while dir_ and dir_ != os.sep:
        #log.warning('_get_defname: dir=%(dir_)s => defname=%(defname)s' % vars())
        newdefname = os.path.join(dir_, defname)

        if os.path.exists(newdefname):
            return newdefname, defname
        newdefname = newdefname.lower()
        if os.path.exists(newdefname):
            return newdefname, defname

        # One level up
        dir_, f = os.path.split(dir_)

    return None, defname


esc_ctrlz_pat = re.compile(r'\033\032.*')
def _get_mem_text(mems, i):
    'Notice that Pro-Gen starts the mem numbering at 1.'
    if i <= 0:
        return ''

    i -= 1
    recno = mems[i][0]
    text = mems[i][1].decode('cp850')
    if recno != 0:
        text += _get_mem_text(mems, recno)
    # ESC-^M is newline
    text = text.replace('\033\r', '\n')
    # ESC-^Z is end of string
    text = esc_ctrlz_pat.sub('', text)

    # There can be nul bytes. Remove them.
    text = text.replace('\0', '')

    # Strip leading/trailing whitespace
    text = text.strip()

    #print(text)
    return text

month_values = {
    'jan' : 1,
    'feb' : 2,
    'febr' : 2,
    'maa' : 3,
    'mar' : 3,
    'march' : 3,
    'mrt' : 3,
    'maart' : 3,
    'apr' : 4,
    'april' : 4,
    'mei' : 5,
    'may' : 5,
    'jun' : 6,
    'juni' : 6,
    'jul' : 7,
    'juli' : 7,
    'aug' : 8,
    'sep' : 9,
    'sept' : 9,
    'ok' : 10,
    'okt' : 10,
    'oct' : 10,
    'nov' : 11,
    'dec' : 12,
}
def _cnv_month_to_int(m):
    return month_values.get(m, 0)


# Split "van", "de" prefixes
_surname_prefixes = [
    "'t ",
    'den ',
    'der ',
    'de ',
    'het ',
    'in den ',
    'ten ',
    'ter ',
    'te ',
    'van den ',
    'van der ',
    'van de ',
    'van ',
]
def _split_surname(surname):
    for p in _surname_prefixes:
        if surname.startswith(p):
            return p.strip(), surname[len(p):].strip()
    return '', surname

# Example field:
# ['Voornaam', '47', '64', '4', '2', '15', '""', '""']
# item 0
# item 1 is a number indicating the fieldtype
# item 2
# item 3 is the size of the field
class PG30_Def_Table_Field:
    'This class represents a field in one of the tables in the DEF file.'
    def __init__(self, name, value):
        self.fieldname = name
        self.fields = value.split(',')
        self.fields = [p.strip() for p in self.fields]
        self.name = self.fields[0]
        self.type_ = int(self.fields[1])
        self.size = int(self.fields[3])

    def __repr__(self):
        return self.fieldname + ' -> ' + ', '.join(self.fields)


class PG30_Def_Table:
    'This class represents a table in the DEF file.'
    def __init__(self, name, lines):
        self.name = name
        self.parms = {}
        self.recfmt = None
        # Example line:
        #f02=Persoon gewijzigd   ,32,10,10, 1,68,"","INDI CHAN DATE"
        line_pat = re.compile(r'(\w+) = (.*)', re.VERBOSE)
        for l in lines:
            #print(l)
            m = line_pat.match(l)
            if m:
                # TODO. Catch duplicates?
                self.parms[m.group(1)] = m.group(2)

        self.fileext = self.parms.get('fileext', None)
        #self.name1 = self.parms.get('name1', None)

        # If there is a n_fields entry then this is a table that
        # has details about the record format of another file (PER or REL).
        if 'n_fields' in self.parms:
            self.get_fields()
            self.recfmt = self.get_recfmt()
            self.nam2fld = {}
            self.nam2idx = {}
            self.recflds = []                          # list of fields that use up space in a record
            j = 0
            for i, f in enumerate(self.flds):
                #print("# field %s" % f)
                nam = f.name
                self.nam2fld[nam] = f
                if f.size != 0:
                    self.nam2idx[nam] = j
                    #print("#       %s <= %d" % (f.fieldname, j))
                    self.recflds.append(f)
                    j = j + 1

    def __getitem__(self, i):
        return self.parms.get(i, None)

    def get_recfmt(self):
        'Get the record format for struct.unpack'
        # Example field:
        # ['Voornaam', '47', '64', '4', '2', '15', '""', '""']
        # item 0
        # item 1 is a number indicating the fieldtype
        # item 2
        # item 3 is the size of the field
        # ...
        flds = self.flds
        # The input file comes from [what was originally] a DOS machine so will
        # be little-endian, regardless of the 'native' byte order of the host
        # system
        fmt = '<'
        for f in flds:
            fldtyp = f.type_
            if fldtyp == 2 or fldtyp == 3 or fldtyp == 22 or fldtyp == 23:
                fmt += 'i'
            elif fldtyp == 31:
                pass
            elif fldtyp == 32 or fldtyp == 44 or fldtyp == 45:
                fmt += '%ds' % f.size
            elif fldtyp == 41:
                fmt += 'h'
            elif fldtyp == 42 or fldtyp == 43 or fldtyp == 46 or fldtyp == 47:
                fmt += 'i'
            else:
                pass                    # ???? Do we want to know?
        return fmt

    def get_fields(self):
        # For example from pg30-1.def
        #n_fields=58
        #f01=Persoon record      ,31, 6, 0, 1,17,"","INDI RFN"
        #f02=Persoon gewijzigd   ,32,10,10, 1,68,"","INDI CHAN DATE"
        #f03=Voornaam            ,47,64, 4, 2,15,"",""

        n_fields = int(self.parms['n_fields'])
        flds = []
        for i in range(n_fields):
            fld_name = 'f%02d' % (i+1)
            fld = self.parms.get(fld_name, None)
            flds.append(PG30_Def_Table_Field(fld_name, fld))
        self.flds = flds

    def get_record_field_index(self, fldname):
        'Return the index number in the record tuple, based on the name.'
        if not fldname in self.nam2idx:
            raise ProgenError(_("Field '%(fldname)s' not found") % locals())
        return self.nam2idx[fldname]

    def convert_record_to_list(self, rec, mems):
        flds = []
        for i in range(len(rec)):
            if self.field_ix_is_record_number(i):
                flds.append("%d" % rec[i])
            elif self.field_ix_is_mem_type(i):
                flds.append(_get_mem_text(mems, rec[i]))
            else:
                # Not a record number, not a mem number. It must be just text.
                fld = rec[i].strip()
                # Convert to unicode
                fld = fld.decode('cp850')
                flds.append(fld)
        #print(', '.join(flds))
        return flds

    def get_field_names(self):
        ret = []
        for f in self.flds:
            if f.size != 0:
                ret.append(f.name)
        return ret

    def field_is_mem_type(self, fldname):
        if not fldname in self.nam2fld:
            return None
        typ = self.nam2fld[fldname].type_
        if typ == 46 or typ == 47:
            return True
        return False

    # TODO. Integrate this into field_is_mem_type()
    def field_ix_is_mem_type(self, ix):
        typ = self.recflds[ix].type_
        if typ == 46 or typ == 47:
            return True
        return False

    def field_ix_is_record_number(self, ix):
        typ = self.recflds[ix].type_
        if typ == 2 or typ == 3 or typ == 22 or typ == 23:
            return True
        return False

    def diag(self):
        txt = self.name + '\n'
        if 'n_fields' in self.parms:
            txt += 'n_fields = %s\n' % self.parms['n_fields']
            # Just grab a field
            f = self.flds[1]
            txt += '"%s"\n' % f
            txt += 'recfmt = %s (length=%d)' % (self.recfmt,
                                                struct.calcsize(str(self.recfmt)))
        return txt


class PG30_Def:
    '''
    Utility class to read PG30-1.DEF and to get certain information
    from it.

    The contents of the DEF file is separated in sections that start
    with [<section name>]. For example:
    [general]
    dateformat=DD-MM-YYYY
    pointerlength=4
    tables=2

    '''
    def __init__(self, fname):
        #print fname
        fname, deffname = _get_defname(fname)
        if not fname:
            raise ProgenError(_("Cannot find DEF file: %(deffname)s") % locals())

        # This can throw a IOError
        import io
        lines = None
        with io.open(fname, buffering=1,
                     encoding='cp437', errors='strict') as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        content = '\n'.join(lines).encode('utf-8')
        parts = re.split(r'\n(?=\[)', content)
        self.parts = {}
        self.tables = {}
        for p in parts:
            lines = p.splitlines()
            # Get section name
            k = re.sub(r'\[(.*)\]', r'\1', lines[0])
            # Store section contents in a hashtable using that section name
            self.parts[k] = lines[1:]
            self.tables[k] = PG30_Def_Table(k, self.parts[k])

        # Some sections are special: Table_1 and Table_2

    def __getitem__(self, i):
        return self.tables.get(i, None)

    # TODO. Maybe rename to __repr__
    def diag(self):
        return '\n\n'.join([self.tables[t].diag() for t in self.tables])


class ProgenParser(object):
    def __init__(self, dbase, file_):
        self.bname, ext = os.path.splitext(file_)
        if ext.lower() in ('.per', '.rel', '.mem'):
            file_ = self.bname + '.def'
        self.db = dbase
        self.fname = file_

        self.gid2id = {}                # Maps person id
        self.fid2id = {}                # Maps family id
        self.fm2fam = {}
        self.pkeys = {}                 # Caching place handles
        self.skeys = {}                 # Caching source handles

    def parse_progen_file(self):
        self.def_ = PG30_Def(self.fname)
        #print self.def_.diag()
        self.progress = ProgressMeter(_("Import from Pro-Gen"), '')

        self.mems = _read_mem(self.bname)
        self.pers = _read_recs(self.def_['Table_1'], self.bname)
        self.rels = _read_recs(self.def_['Table_2'], self.bname)

        with DbTxn(_("Pro-Gen import"), self.db, batch=True) as self.trans:
            self.db.disable_signals()

            self.create_persons()
            self.create_families()
            self.add_children()

        self.db.enable_signals()
        self.db.request_rebuild()
        self.progress.close()


    def __find_person_handle(self, progen_id):
        """
        Return the database handle associated with the person's Pro-Gen ID
        """
        return _find_from_handle(progen_id, self.gid2id)

    def __find_family_handle(self, progen_id):
        """
        Return the database handle associated with the family's Pro-Gen ID
        """
        return _find_from_handle(progen_id, self.fid2id)

    def __find_or_create_person(self, progen_id):
        """
        Finds or creates a person based on the Pro-Gen ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new person, assign the handle and GRAMPS ID.
        """
        person = Person()
        intid = self.gid2id.get(progen_id)
        if self.db.has_person_handle(intid):
            person.unserialize(self.db.get_raw_person_data(intid))
        else:
            gramps_id = self.db.id2user_format("I%d" % progen_id)
            if self.db.id_trans.get(gramps_id):
                gramps_id = self.db.find_next_person_gramps_id()
            intid = _find_from_handle(progen_id, self.gid2id)
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)
        return person

    def __find_or_create_family(self, progen_id):
        """
        Finds or creates a family based on the Pro-Gen ID. If the ID is
        already used (is in the db), we return the item in the db. Otherwise, 
        we create a new family, assign the handle and GRAMPS ID.
        """
        family = Family()
        intid = self.fid2id.get(progen_id)
        if self.db.has_family_handle(intid):
            family.unserialize(self.db.get_raw_family_data(intid))
        else:
            gramps_id = self.db.fid2user_format("F%d" % progen_id)
            if self.db.id_trans.get(gramps_id):
                gramps_id = self.db.find_next_family_gramps_id()
            intid = _find_from_handle(progen_id, self.fid2id)
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)
        return family

    def __get_or_create_place(self, place_name):
        if not place_name:
            return None
        place = None
        if place_name in self.pkeys:
            place = self.db.get_place_from_handle(self.pkeys[place_name])
        else:
            # Create a new Place
            place = Place()
            place.set_title(place_name)
            self.db.add_place(place, self.trans)
            self.db.commit_place(place, self.trans)
            self.pkeys[place_name] = place.get_handle()
        return place

    def __get_or_create_citation(self, source_name, aktenr=None,
                                 source_text=None):
        if not source_name:
            return None

        # Aktenr is something very special and it belongs with the source_name
        if aktenr:
            source_name = "%(source_name)s, aktenr: %(aktenr)s" % locals()

        if source_name in self.skeys:
            source = self.db.get_source_from_handle(self.skeys[source_name])
        else:
            # Create a new Source
            source = Source()
            source.set_title(source_name)
            self.db.add_source(source, self.trans)
            self.db.commit_source(source, self.trans)
            self.skeys[source_name] = source.get_handle()
            
        citation = Citation()
        citation.set_reference_handle(source.get_handle())
        if aktenr:
            sattr = SrcAttribute()
            sattr.set_type("REFN")
            sattr.set_value(aktenr)
            citation.add_attribute(sattr)
        if source_text:
            note = Note()
            note_type = NoteType()
            note_type.set((NoteType.CUSTOM, "Brontekst"))
            note.set_type(note_type)
            note.set(source_text)
            self.db.add_note(note, self.trans)
            citation.add_note(note.handle)
        self.db.add_citation(citation, self.trans)
        self.db.commit_citation(citation, self.trans)

        return citation

    def __create_event_and_ref(self, type_, desc=None, date=None, place=None,
                               citation=None, note_text=None, time=None):
        event = Event()
        event.set_type(EventType(type_))
        if desc:
            event.set_description(desc)
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if citation:
            event.add_citation(citation.handle)
        if time:
            attr = Attribute()
            attr.set_type(AttributeType.TIME)
            attr.set_value(time)
            event.add_attribute(attr)
        if note_text:
            note = Note()
            note_type = NoteType()
            note_type.set((NoteType.CUSTOM, "Info"))
            note.set_type(note_type)
            note.set(note_text)
            self.db.add_note(note, self.trans)
            event.add_note(note.handle)
            
        self.db.add_event(event, self.trans)
        self.db.commit_event(event, self.trans)
        event_ref = EventRef()
        event_ref.set_reference_handle(event.get_handle())
        return event, event_ref

    __date_pat1 = re.compile(r'(?P<day>\d{1,2}) (-|=) (?P<month>\d{1,2}) (-|=) (?P<year>\d{2,4})', re.VERBOSE)
    __date_pat2 = re.compile(r'(?P<month>\d{1,2}) (-|=) (?P<year>\d{4})', re.VERBOSE)
    __date_pat3 = re.compile(r'(?P<year>\d{3,4})', re.VERBOSE)
    __date_pat4 = re.compile(r'(v|vóór|voor|na|circa|ca|rond|±) (\.|\s)* (?P<year>\d{3,4})', re.VERBOSE)
    __date_pat5 = re.compile(r'(oo|OO) (-|=) (oo|OO) (-|=) (?P<year>\d{2,4})', re.VERBOSE)
    __date_pat6 = re.compile(r'(?P<month>(%s)) (\.|\s)* (?P<year>\d{3,4})' % '|'.join(list(month_values.keys())), re.VERBOSE | re.IGNORECASE)
    def __create_date_from_text(self, txt, diag_msg=None):
        '''
        Pro-Gen has a text field for the date. It can be anything. Mostly it will be dd-mm-yyyy,
        but we have seen:
        yyyy
        mm-yyyy
        voor yyyy
        dd=mm-yyyy  (typo I guess)
        00-00-yyyy
        oo-oo-yyyy
        dd-mm-00 (does this mean we do not know about the year?)

        This function tries to parse the text and create a proper Gramps Date() object.
        If all else fails we create a MOD_TEXTONLY Date() object.
        '''

        if not txt or txt == 'onbekend' or txt == '??':
            return None

        date = Date()

        # dd-mm-yyyy
        m = self.__date_pat1.match(txt)
        if m:
            day = int(m.group('day'))
            month = int(m.group('month'))
            year = int(m.group('year'))
            if day and month and year:
                date.set_yr_mon_day(year, month, day)
            else:
                date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (day, month, year, None))
            return date

        # mm-yyyy
        m = self.__date_pat2.match(txt)
        if m:
            month = int(m.group('month'))
            year = int(m.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, month, year, None))
            return date

        # yyy or yyyy
        m = self.__date_pat3.match(txt)
        if m:
            year = int(m.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, year, None))
            return date

        # voor|na|... yyyy
        m = self.__date_pat4.match(txt)
        if m:
            year = int(m.group('year'))
            if m.group(1) == 'voor' or m.group(1) == 'v' or m.group(1) == 'vóór':
                date.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, year, None))
            elif m.group(1) == 'na':
                date.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, year, None))
            else:
                date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, year, None))
            return date

        # oo-oo-yyyy
        m = self.__date_pat5.match(txt)
        if m:
            year = int(m.group('year'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, year, None))
            return date

        # mmm yyyy (textual month)
        m = self.__date_pat6.match(txt)
        if m:
            year = int(m.group('year'))
            month = _cnv_month_to_int(m.group('month'))
            date.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, month, year, None))
            return date

        log.warning(_("date did not match: '%(text)s' (%(msg)s)") % {
            'text' : txt.encode('utf-8'), 'msg' : diag_msg or '' } )
        # Hmmm. Just use the plain text.
        date.set_as_text(txt)
        return date

    def create_persons(self):
        table = self.def_['Table_1']

        # Records in the PER file using PG30-1.DEF contain the following fields:
        # (Note. We want this to be computed just once.

        #log.info(table.get_field_names())

        # I'm sure I can find a better way to do this through the local() dict)
        first_name_ix = table.get_record_field_index('Voornaam')
        surname_ix = table.get_record_field_index('Achternaam')
        gender_ix = table.get_record_field_index('Geslacht')
        patron_ix = table.get_record_field_index('Patroniem')
        call_name_ix = table.get_record_field_index('Roepnaam')
        alias_ix = table.get_record_field_index('Alias')
        per_code_ix = table.get_record_field_index('Persoon code')
        title1_ix = table.get_record_field_index('Titel1')
        title2_ix = table.get_record_field_index('Titel2')
        title3_ix = table.get_record_field_index('Titel3')
        father_ix = table.get_record_field_index('Vader')
        mother_ix = table.get_record_field_index('Moeder')
        occu_ix = table.get_record_field_index('Beroep')

        per_klad_ix = table.get_record_field_index('Persoon klad')
        per_info_ix = table.get_record_field_index('Persoon info')

        addr_date_ix = table.get_record_field_index('Adres datum')
        addr_street_ix = table.get_record_field_index('Adres straat')
        addr_postal_ix = table.get_record_field_index('Adres postcode')
        addr_place_ix = table.get_record_field_index('Adres plaats')
        addr_country_ix = table.get_record_field_index('Adres land')
        addr_telno_ix = table.get_record_field_index('Adres telefoon')
        addr_info_ix = table.get_record_field_index('Adres info')

        birth_date_ix = table.get_record_field_index('Geboorte datum')
        birth_place_ix = table.get_record_field_index('Geboorte plaats')
        birth_time_ix = table.get_record_field_index('Geboorte tijd')
        birth_source_ix = table.get_record_field_index('Geboorte bron')
        birth_aktenr_ix = table.get_record_field_index('Geboorte akte')
        birth_source_text_ix = table.get_record_field_index('Geboorte brontekst')
        birth_info_ix = table.get_record_field_index('Geboorte info')

        bapt_date_ix = table.get_record_field_index('Doop datum')
        bapt_place_ix = table.get_record_field_index('Doop plaats')
        bapt_reli_ix = table.get_record_field_index('Gezindte')
        bapt_witn_ix = table.get_record_field_index('Doop getuigen')
        bapt_source_ix = table.get_record_field_index('Doop bron')
        bapt_aktenr_ix = table.get_record_field_index('Doop akte')
        bapt_source_text_ix = table.get_record_field_index('Doop brontekst')
        bapt_info_ix = table.get_record_field_index('Doop info')

        death_date_ix = table.get_record_field_index('Overlijden datum')
        death_place_ix = table.get_record_field_index('Overlijden plaats')
        death_time_ix = table.get_record_field_index('Overlijden tijd')
        death_source_ix = table.get_record_field_index('Overlijden bron')
        death_aktenr_ix = table.get_record_field_index('Overlijden akte')
        death_source_text_ix = table.get_record_field_index('Overlijden brontekst')
        death_info_ix = table.get_record_field_index('Overlijden info')

        crem_date_ix = table.get_record_field_index('Crematie datum')
        crem_place_ix = table.get_record_field_index('Crematie plaats')
        crem_source_ix = table.get_record_field_index('Crematie bron')
        crem_aktenr_ix = table.get_record_field_index('Crematie akte')
        crem_source_text_ix = table.get_record_field_index('Crematie brontekst')
        crem_info_ix = table.get_record_field_index('Crematie info')

        bur_date_ix = table.get_record_field_index('Begrafenis datum')
        bur_place_ix = table.get_record_field_index('Begrafenis plaats')
        bur_source_ix = table.get_record_field_index('Begrafenis bron')
        bur_aktenr_ix = table.get_record_field_index('Begrafenis akte')
        bur_source_text_ix = table.get_record_field_index('Begrafenis brontekst')
        bur_info_ix = table.get_record_field_index('Begrafenis info')

        # The records are numbered 1..N
        self.progress.set_pass(_('Importing individuals'), len(self.pers))
        for i, rec in enumerate(self.pers):
            pers_id = i + 1
            log.debug(("Person id %d  " % pers_id) + " ".join(("%s" % r) for r in rec))
            father = rec[father_ix]
            mother = rec[mother_ix]
            if father >= 0 and mother >= 0:
                recflds = table.convert_record_to_list(rec, self.mems)

                gender = recflds[gender_ix]
                if gender == 'M':
                    gender = Person.MALE
                elif gender == 'V':
                    gender = Person.FEMALE
                else:
                    gender = Person.UNKNOWN

                person = self.__find_or_create_person(pers_id)

                first_name = recflds[first_name_ix]
                surname_prefix, surname = _split_surname(recflds[surname_ix])
                patronym = recflds[patron_ix]       # INDI _PATR
                alias = recflds[alias_ix]           # INDI NAME _ALIA/INDI NAME COMM 
                title1 = recflds[title1_ix]         # INDI TITL
                title2 = recflds[title2_ix]         # INDI _TITL2
                title3 = recflds[title3_ix]         # INDI _TITL3

                diag_msg = "%s: %s %s" % (person.gramps_id, first_name.encode('utf-8'), surname.encode('utf-8'))

                # process the name/given name
                name = Name()
                name.set_type(NameType.BIRTH)
                name.set_first_name(first_name)
                if recflds[call_name_ix]:
                    name.set_call_name(recflds[call_name_ix])
                title = [_f for _f in [title1, title2, title3] if _f]
                if title:
                    name.set_title(", ".join(title))
                # process the normal surname
                sname = Surname()
                sname.set_surname(surname)
                if surname_prefix:
                    sname.set_prefix(surname_prefix)
                name.add_surname(sname)
                # process the Patronymic
                if patronym:
                    pname = Surname()
                    pname.set_surname(patronym)
                    pname.set_origintype(NameOriginType.PATRONYMIC)
                    name.add_surname(pname)

                person.set_primary_name(name)
                person.set_gender(gender)

                per_code = recflds[per_code_ix]     # INDI REFN
                if per_code:
                    attr = Attribute()
                    attr.set_type((AttributeType.CUSTOM, "REFN"))
                    attr.set_value(per_code)
                    person.add_attribute(attr)

                per_klad = recflds[per_klad_ix]     # INDI _COMM/INDI COMM
                per_info = recflds[per_info_ix]     # INDI NOTE

                note_txt = [_f for _f in [per_info, per_klad] if _f]
                if note_txt:
                    note = Note()
                    note.set('\n'.join(note_txt))
                    note.set_type(NoteType.PERSON)
                    self.db.add_note(note, self.trans)
                    person.add_note(note.handle)

                # Alias. Two possibilities: extra Name, or Attribute
                if alias:
                    aname = alias.split()
                    if len(aname) == 1:
                        attr = Attribute()
                        attr.set_type(AttributeType.NICKNAME)
                        attr.set_value(alias)
                        person.add_attribute(attr)
                    else:
                        # ???? Don't know if this is OK.
                        name = Name()
                        sname = Surname()
                        sname.set_surname(aname[-1].strip())
                        name.add_surname(sname)
                        name.set_first_name(' '.join(aname[0:-1]))
                        name.set_type(NameType.AKA)
                        person.add_alternate_name(name)                    

                if recflds[occu_ix]:
                    event, event_ref = self.__create_event_and_ref(EventType.OCCUPATION, recflds[occu_ix])
                    person.add_event_ref(event_ref)

                # Birth
                date = self.__create_date_from_text(recflds[birth_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[birth_place_ix])
                time = recflds[birth_time_ix]
                if time:
                    time_text = "tijd: " + time
                else:
                    time_text = None
                source_title  = recflds[birth_source_ix]
                source_refn = recflds[birth_aktenr_ix]
                source_text = recflds[birth_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[birth_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, time_text, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, birth_ref = self.__create_event_and_ref(EventType.BIRTH, desc, date, place, citation, info, time)
                    person.set_birth_ref(birth_ref)

                # Baptism
                date = self.__create_date_from_text(recflds[bapt_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[bapt_place_ix])
                reli = recflds[bapt_reli_ix]
                witness = recflds[bapt_witn_ix]
                source_title  = recflds[bapt_source_ix]
                source_refn = recflds[bapt_aktenr_ix]
                source_text = recflds[bapt_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[bapt_info_ix]
                if date or place or info or citation or reli or witness:
                    desc = [_f for _f in [reli, info, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, bapt_ref = self.__create_event_and_ref(EventType.BAPTISM, desc, date, place, citation, info)
                    person.add_event_ref(bapt_ref)
                    if witness:
                        attr = Attribute()
                        attr.set_type(AttributeType.WITNESS)
                        attr.set_value(witness)
                        event.add_attribute(attr)

                # Death
                date = self.__create_date_from_text(recflds[death_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[death_place_ix])
                time = recflds[death_time_ix]
                if time:
                    time = "tijd: " + time
                source_title  = recflds[death_source_ix]
                source_refn = recflds[death_aktenr_ix]
                source_text = recflds[death_source_text_ix]
                info = recflds[death_info_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                if date or place or info or citation:
                    desc = [_f for _f in [info, time, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, death_ref = self.__create_event_and_ref(EventType.DEATH, desc, date, place, citation, info, time)
                    person.set_death_ref(death_ref)

                # Burial
                date = self.__create_date_from_text(recflds[bur_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[bur_place_ix])
                source_title  = recflds[bur_source_ix]
                source_refn = recflds[bur_aktenr_ix]
                source_text = recflds[bur_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[bur_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, burial_ref = self.__create_event_and_ref(EventType.BURIAL, desc, date, place, citation, info)
                    person.add_event_ref(burial_ref)

                # Cremation
                date = self.__create_date_from_text(recflds[crem_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[crem_place_ix])
                source_title  = recflds[crem_source_ix]
                source_refn = recflds[crem_aktenr_ix]
                source_text = recflds[crem_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[crem_info_ix]
                if date or place or info or citation:
                    # TODO. Check that not both burial and cremation took place.
                    desc = [_f for _f in [info, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, cremation_ref = self.__create_event_and_ref(EventType.CREMATION, desc, date, place, citation)
                    person.add_event_ref(cremation_ref)

                # TODO. Address
                date = self.__create_date_from_text(recflds[addr_date_ix], diag_msg)
                street = recflds[addr_street_ix]
                postal = recflds[addr_postal_ix]
                place = self.__get_or_create_place(recflds[addr_place_ix])
                country = recflds[addr_country_ix]
                telno = recflds[addr_telno_ix]
                info = recflds[addr_info_ix]          # INDI RESI NOTE/INDI ADDR
                if place:
                    loc = Location()
                    loc.set_street(street)
                    loc.set_postal_code(postal)
                    loc.set_country(country)
                    loc.set_phone(telno)
                    place.set_main_location(loc)
                    self.db.commit_place(place, self.trans)
                    desc = info or None
                    event, resi_ref = self.__create_event_and_ref(EventType.RESIDENCE, desc, date, place)
                    if info:
                        note = Note()
                        note.set(info)
                        note.set_type(NoteType.EVENT)
                        self.db.add_note(note, self.trans)
                        event.add_note(note.handle)
                        self.db.commit_event(event, self.trans)
                    person.add_event_ref(resi_ref)

                self.db.commit_person(person, self.trans)
            self.progress.step()

    def create_families(self):
        table = self.def_['Table_2']

        # Records in the REL file using PG30-1.DEF contain the following fields:
        # (Note. We want this to be computed just once.

        #log.info(table.get_field_names())

        man_ix = table.get_record_field_index('Man')
        vrouw_ix = table.get_record_field_index('Vrouw')

        rel_code_ix = table.get_record_field_index('Relatie code')
        rel_klad_ix = table.get_record_field_index('Relatie klad')
        rel_info_ix = table.get_record_field_index('Relatie info')

        civu_date_ix = table.get_record_field_index('Samenwonen datum')
        civu_place_ix = table.get_record_field_index('Samenwonen plaats')
        civu_source_ix = table.get_record_field_index('Samenwonen bron')
        civu_aktenr_ix = table.get_record_field_index('Samenwonen akte')
        civu_source_text_ix = table.get_record_field_index('Samenwonen brontekst')
        civu_info_ix = table.get_record_field_index('Samenwonen info')

        marl_date_ix = table.get_record_field_index('Ondertrouw datum')
        marl_place_ix = table.get_record_field_index('Ondertrouw plaats')
        marl_witn_ix = table.get_record_field_index('Ondertrouw getuigen')
        marl_source_ix = table.get_record_field_index('Ondertrouw bron')
        marl_aktenr_ix = table.get_record_field_index('Ondertrouw akte')
        marl_source_text_ix = table.get_record_field_index('Ondertrouw brontekst')
        marl_info_ix = table.get_record_field_index('Ondertrouw info')

        mar_date_ix = table.get_record_field_index('Wettelijk datum')
        mar_place_ix = table.get_record_field_index('Wettelijk plaats')
        mar_witn_ix = table.get_record_field_index('Wettelijk getuigen')
        mar_source_ix = table.get_record_field_index('Wettelijk bron')
        mar_aktenr_ix = table.get_record_field_index('Wettelijk akte')
        mar_source_text_ix = table.get_record_field_index('Wettelijk brontekst')
        mar_info_ix = table.get_record_field_index('Wettelijk info')

        marc_date_ix = table.get_record_field_index('Kerkelijk datum')
        marc_place_ix = table.get_record_field_index('Kerkelijk plaats')
        marc_reli_ix = table.get_record_field_index('Kerk')
        marc_witn_ix = table.get_record_field_index('Kerkelijk getuigen')
        marc_source_ix = table.get_record_field_index('Kerkelijk bron')
        marc_aktenr_ix = table.get_record_field_index('Kerkelijk akte')
        marc_source_text_ix = table.get_record_field_index('Kerkelijk brontekst')
        marc_info_ix = table.get_record_field_index('Kerkelijk info')

        div_date_ix = table.get_record_field_index('Scheiding datum')
        div_place_ix = table.get_record_field_index('Scheiding plaats')
        div_source_ix = table.get_record_field_index('Scheiding bron')
        div_aktenr_ix = table.get_record_field_index('Scheiding akte')
        div_source_text_ix = table.get_record_field_index('Scheiding brontekst')
        div_info_ix = table.get_record_field_index('Scheiding info')

        # The records are numbered 1..N
        self.progress.set_pass(_('Importing families'), len(self.rels))
        for i, rec in enumerate(self.rels):
            fam_id = i + 1
            husband = rec[man_ix]
            wife = rec[vrouw_ix]
            if husband > 0 or wife > 0:
                recflds = table.convert_record_to_list(rec, self.mems)
                self.highest_fam_id = fam_id

                fam = self.__find_or_create_family(fam_id)
                husband_handle = None
                if husband > 0:
                    husband_handle = self.__find_person_handle(husband)
                    fam.set_father_handle(husband_handle)
                    husband_person = self.db.get_person_from_handle(husband_handle)
                    husband_person.add_family_handle(fam.get_handle())
                    self.db.commit_person(husband_person, self.trans)
                wife_handle = None
                if wife > 0:
                    wife_handle = self.__find_person_handle(wife)
                    fam.set_mother_handle(wife_handle)
                    wife_person = self.db.get_person_from_handle(wife_handle)
                    wife_person.add_family_handle(fam.get_handle())
                    self.db.commit_person(wife_person, self.trans)
                diag_msg = "%s: %s %s" % (fam.gramps_id,
                            husband_person.gramps_id if husband_handle else "",
                            wife_person.gramps_id if wife_handle else "")
                self.fm2fam[husband_handle, wife_handle] = fam

                rel_code = recflds[rel_code_ix]
                rel_klad = recflds[rel_klad_ix]
                rel_info = recflds[rel_info_ix]

                note_txt = [_f for _f in [rel_info, rel_klad] if _f]
                if note_txt:
                    note = Note()
                    note.set('\n'.join(note_txt))
                    note.set_type(NoteType.FAMILY)
                    self.db.add_note(note, self.trans)
                    fam.add_note(note.handle)

                if rel_code:
                    attr = Attribute()
                    attr.set_type((AttributeType.CUSTOM, "REFN"))
                    attr.set_value(rel_code)
                    fam.add_attribute(attr)

                # Wettelijk => Marriage
                date = self.__create_date_from_text(recflds[mar_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[mar_place_ix])
                witness = recflds[mar_witn_ix]
                citation = self.__get_or_create_citation(recflds[mar_source_ix], recflds[mar_aktenr_ix])
                source_title  = recflds[mar_source_ix]
                source_refn = recflds[mar_aktenr_ix]
                source_text = recflds[mar_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[mar_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, mar_ref = self.__create_event_and_ref(EventType.MARRIAGE, desc, date, place, citation, info)
                    fam.add_event_ref(mar_ref)
                    if witness:
                        attr = Attribute()
                        attr.set_type(AttributeType.WITNESS)
                        attr.set_value(witness)
                        event.add_attribute(attr)
                        self.db.commit_event(event, self.trans)

                    # Type of relation
                    fam.set_relationship(FamilyRelType(FamilyRelType.MARRIED))

                # Kerkelijk => Marriage
                date = self.__create_date_from_text(recflds[marc_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[marc_place_ix])
                reli = recflds[marc_reli_ix]
                witness = recflds[marc_witn_ix]
                citation = self.__get_or_create_citation(recflds[marc_source_ix], recflds[marc_aktenr_ix])
                source_title  = recflds[marc_source_ix]
                source_refn = recflds[marc_aktenr_ix]
                source_text = recflds[marc_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[marc_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [reli, info, source_text] if _f]
                    desc.insert(0, 'Kerkelijk huwelijk')
                    desc = desc and '; '.join(desc) or None
                    event, marc_ref = self.__create_event_and_ref(EventType.MARRIAGE, desc, date, place, citation, info)
                    fam.add_event_ref(marc_ref)
                    if witness:
                        attr = Attribute()
                        attr.set_type(AttributeType.WITNESS)
                        attr.set_value(witness)
                        event.add_attribute(attr)
                        self.db.commit_event(event, self.trans)

                    # Type of relation
                    fam.set_relationship(FamilyRelType(FamilyRelType.MARRIED))

                # Ondertrouw => Marriage License
                date = self.__create_date_from_text(recflds[marl_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[marl_place_ix])
                witness = recflds[marl_witn_ix]
                citation = self.__get_or_create_citation(recflds[marl_source_ix], recflds[marl_aktenr_ix])
                source_title  = recflds[marl_source_ix]
                source_refn = recflds[marl_aktenr_ix]
                source_text = recflds[marl_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[marl_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, source_text] if _f]
                    desc.insert(0, 'Ondertrouw')
                    desc = desc and '; '.join(desc) or None
                    event, marl_ref = self.__create_event_and_ref(EventType.MARR_LIC, desc, date, place, citation, info)
                    fam.add_event_ref(marl_ref)
                    if witness:
                        attr = Attribute()
                        attr.set_type(AttributeType.WITNESS)
                        attr.set_value(witness)
                        event.add_attribute(attr)
                        self.db.commit_event(event, self.trans)

                # Samenwonen => Civil Union
                date = self.__create_date_from_text(recflds[civu_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[civu_place_ix])
                citation = self.__get_or_create_citation(recflds[civu_source_ix], recflds[civu_aktenr_ix])
                source_title  = recflds[civu_source_ix]
                source_refn = recflds[civu_aktenr_ix]
                source_text = recflds[civu_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[civu_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, source_text] if _f]
                    desc.insert(0, 'Samenwonen')
                    desc = desc and '; '.join(desc) or None
                    event, civu_ref = self.__create_event_and_ref(EventType.UNKNOWN, desc, date, place, citation, info)
                    fam.add_event_ref(civu_ref)
                    # Type of relation
                    fam.set_relationship(FamilyRelType(FamilyRelType.CIVIL_UNION))

                # Scheiding => Divorce
                date = self.__create_date_from_text(recflds[div_date_ix], diag_msg)
                place = self.__get_or_create_place(recflds[div_place_ix])
                citation = self.__get_or_create_citation(recflds[div_source_ix], recflds[div_aktenr_ix])
                source_title  = recflds[div_source_ix]
                source_refn = recflds[div_aktenr_ix]
                source_text = recflds[div_source_text_ix]
                citation = self.__get_or_create_citation(source_title,
                                                         source_refn,
                                                         source_text)
                info = recflds[div_info_ix]
                if date or place or info or citation:
                    desc = [_f for _f in [info, source_text] if _f]
                    desc = desc and '; '.join(desc) or None
                    event, div_ref = self.__create_event_and_ref(EventType.DIVORCE, desc, date, place, citation, info)
                    fam.add_event_ref(div_ref)

                self.db.commit_family(fam, self.trans)

            self.progress.step()

    def add_children(self):
        # Once more to record the father and mother
        table = self.def_['Table_1']

        father_ix = table.get_record_field_index('Vader')
        mother_ix = table.get_record_field_index('Moeder')

        # The records are numbered 1..N
        self.progress.set_pass(_('Adding children'), len(self.pers))
        for i, rec in enumerate(self.pers):
            pers_id = i + 1
            father = rec[father_ix]
            mother = rec[mother_ix]
            if father > 0 or mother > 0:
                # Find the family with this father and mother
                person_handle = self.__find_person_handle(pers_id)
                father_handle = father > 0 and self.__find_person_handle(father) or None
                mother_handle = mother > 0 and self.__find_person_handle(mother) or None
                if father > 0 and not father_handle:
                    log.warning(_("cannot find father for I%(person)s (father=%(id)d)") % {
                        'person' : pers_id, 'id' : father } )
                elif mother > 0 and not mother_handle:
                    log.warning(_("cannot find mother for I%(person)s (mother=%(mother)d)") % {
                        'person' : pers_id, 'mother' : mother } )
                else:
                    fam = self.fm2fam.get((father_handle, mother_handle), None)
                    if not fam:
                        # Family not present in REL. Create a new one.
                        self.highest_fam_id = self.highest_fam_id + 1
                        fam_id = self.highest_fam_id
                        fam = self.__find_or_create_family(fam_id)
                        if father_handle:
                            fam.set_father_handle(father_handle)
                            father_person = self.db.get_person_from_handle(father_handle)
                            father_person.add_family_handle(fam.get_handle())
                            self.db.commit_person(father_person, self.trans)
                        if mother_handle:
                            fam.set_mother_handle(mother_handle)
                            mother_person = self.db.get_person_from_handle(mother_handle)
                            mother_person.add_family_handle(fam.get_handle())
                            self.db.commit_person(mother_person, self.trans)

                if fam:
                    childref = ChildRef()
                    childref.set_reference_handle(person_handle)
                    fam.add_child_ref(childref)
                    self.db.commit_family(fam, self.trans)
                    person = self.db.get_person_from_handle(person_handle)
                    person.add_parent_family_handle(fam.get_handle())
                    self.db.commit_person(person, self.trans)
            self.progress.step()
