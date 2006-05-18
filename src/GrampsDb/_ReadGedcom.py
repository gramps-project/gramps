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

"Import from GEDCOM"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import re
import string
import const
import lds
import time

from gettext import gettext as _

# and module sets for earlier pythons
try:
    set()
except NameError:
    from sets import Set as set

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GedcomImport")

#-------------------------------------------------------------------------
#
# GTK/GNOME Modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import RelLib
from DateHandler._DateParser import DateParser
import NameDisplay
import Utils
import Mime

from ansel_utf8 import ansel_to_utf8
from bsddb import db
from _GedcomInfo import *
from _GedTokens import *
from QuestionDialog import ErrorDialog, WarningDialog
from _GrampsDbBase import EVENT_KEY
from BasicUtils import UpdateCallback

addr_re  = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)\s+(\d+)\s*(.*)')
addr2_re = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)\s+(\d+)')
addr3_re = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)')

#-------------------------------------------------------------------------
#
# latin/utf8 conversions
#
#-------------------------------------------------------------------------

_place_field = []
_place_match = {
    'city'   : RelLib.Location.set_city,
    'county' : RelLib.Location.set_county,
    'country': RelLib.Location.set_country,
    'state'  : RelLib.Location.set_state,
    }

def _empty_func(a,b):
    return

def utf8_to_latin(s):
    return s.encode('iso-8859-1','replace')

def latin_to_utf8(s):
    if type(s) == unicode:
        return s
    else:
        return unicode(s,'iso-8859-1')

def nocnv(s):
    return unicode(s)

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
ANSEL = 1
UNICODE = 2
UPDATE = 25

_TYPE_BIRTH  = RelLib.ChildRefType()
_TYPE_ADOPT  = RelLib.ChildRefType(RelLib.ChildRefType.ADOPTED)
_TYPE_FOSTER = RelLib.ChildRefType(RelLib.ChildRefType.FOSTER)

file_systems = {
    'VFAT'    : _('Windows 9x file system'),
    'FAT'     : _('Windows 9x file system'),
    "NTFS"    : _('Windows NT file system'),
    "ISO9660" : _('CD ROM'),
    "SMBFS"   : _('Networked Windows file system')
    }

rel_types = (RelLib.ChildRefType.BIRTH,
             RelLib.ChildRefType.UNKNOWN,
             RelLib.ChildRefType.NONE,
             )

pedi_type = {
    'birth'  : RelLib.ChildRefType(),
    'natural': RelLib.ChildRefType(),
    'step'   : _TYPE_ADOPT,
    'adopted': _TYPE_ADOPT,
    'foster' : _TYPE_FOSTER,
    }

lds_status = {
    "BIC"      : RelLib.LdsOrd.STATUS_BIC,
    "CANCELED" : RelLib.LdsOrd.STATUS_CANCELED,
    "CHILD"    : RelLib.LdsOrd.STATUS_CHILD,
    "CLEARED"  : RelLib.LdsOrd.STATUS_CLEARED,
    "COMPLETED": RelLib.LdsOrd.STATUS_COMPLETED,
    "DNS"      : RelLib.LdsOrd.STATUS_DNS,
    "INFANT"   : RelLib.LdsOrd.STATUS_INFANT,
    "PRE-1970" : RelLib.LdsOrd.STATUS_PRE_1970,
    "QUALIFIED": RelLib.LdsOrd.STATUS_QUALIFIED,
    "DNS/CAN"  : RelLib.LdsOrd.STATUS_DNS_CAN,
    "STILLBORN": RelLib.LdsOrd.STATUS_STILLBORN,
    "SUBMITTED": RelLib.LdsOrd.STATUS_SUBMITTED,
    "UNCLEARED": RelLib.LdsOrd.STATUS_UNCLEARED,
    }


_event_family_str = _("%(event_name)s of %(family)s")
_event_person_str = _("%(event_name)s of %(person)s")

_transtable = string.maketrans('','')
_delc = _transtable[0:31]
_transtable2 = _transtable[0:128] + ('?' * 128)

#-------------------------------------------------------------------------
#
# GEDCOM events to GRAMPS events conversion
#
#-------------------------------------------------------------------------
ged2gramps = {}
for _val in Utils.personalConstantEvents.keys():
    _key = Utils.personalConstantEvents[_val]
    if _key != "":
        ged2gramps[_key] = _val

ged2fam = {}
for _val in Utils.familyConstantEvents.keys():
    _key = Utils.familyConstantEvents[_val]
    if _key != "":
        ged2fam[_key] = _val

ged2fam_custom = {}

#-------------------------------------------------------------------------
#
# regular expressions
#
#-------------------------------------------------------------------------
intRE = re.compile(r"\s*(\d+)\s*$")
nameRegexp= re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
snameRegexp= re.compile(r"/([^/]*)/([^/]*)")
calRegexp = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D([^@]+)@\s*(.*)$")
rangeRegexp = re.compile(r"\s*BET\s+@#D([^@]+)@\s*(.*)\s+AND\s+@#D([^@]+)@\s*(.*)$")
spanRegexp = re.compile(r"\s*FROM\s+@#D([^@]+)@\s*(.*)\s+TO\s+@#D([^@]+)@\s*(.*)$")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None, use_trans=False):

    f = open(filename,"r")

    ansel = False
    gramps = False
    for index in range(50):
        line = f.readline().split()
        if len(line) == 0:
            break
        if len(line) > 2 and line[1][0:4] == 'CHAR' and line[2] == "ANSEL":
            ansel = True
        if len(line) > 2 and line[1][0:4] == 'SOUR' and line[2] == "GRAMPS":
            gramps = True
    f.close()

    if not gramps and ansel:
        glade_file = "%s/gedcomimport.glade" % os.path.dirname(__file__)
        top = gtk.glade.XML(glade_file,'encoding','gramps')
        code = top.get_widget('codeset')
        code.set_active(0)
        dialog = top.get_widget('encoding')
        dialog.run()
        codeset = code.get_active()
        dialog.destroy()
    else:
        codeset = None
    import2(database, filename, callback, codeset, use_trans)
        

def import2(database, filename, callback, codeset, use_trans):
    # add some checking here
    try:
        np = NoteParser(filename, False, codeset)
        g = GedcomParser(database,filename, callback, codeset, np.get_map(),
                         np.get_lines(),np.get_persons())
    except IOError,msg:
        ErrorDialog(_("%s could not be opened\n") % filename,str(msg))
        return

    if database.get_number_of_people() == 0:
        use_trans = False

    try:
        close = g.parse_gedcom_file(use_trans)
    except IOError,msg:
        errmsg = _("%s could not be opened\n") % filename
        ErrorDialog(errmsg,str(msg))
        return
    except Errors.GedcomError, val:
        (m1,m2) = val.messages()
        ErrorDialog(m1,m2)
        return
    except db.DBSecondaryBadError, msg:
        WarningDialog(_('Database corruption detected'),
                      _('A problem was detected with the database. Please '
                        'run the Check and Repair Database tool to fix the '
                        'problem.'))
        return


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateStruct:
    def __init__(self):
        self.date = ""
        self.time = ""

class GedcomDateParser(DateParser):

    month_to_int = {
        'jan' : 1,  'feb' : 2,  'mar' : 3,  'apr' : 4,
        'may' : 5,  'jun' : 6,  'jul' : 7,  'aug' : 8,
        'sep' : 9,  'oct' : 10, 'nov' : 11, 'dec' : 12,
        }

class IdFinder:

    def __init__(self,keys,prefix):
        self.ids = set(keys)
        self.index = 0
        self.prefix = prefix

    def find_next(self):
        """
        Returns the next available GRAMPS' ID for a Event object based
        off the person ID prefix.
        """
        index = self.prefix % self.index
        while str(index) in self.ids:
            self.index += 1
            index = self.prefix % self.index
        self.ids.add(index)
        self.index += 1
        return index
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
noteRE = re.compile(r"\s*\d+\s+\@(\S+)\@\s+NOTE(.*)$")
contRE = re.compile(r"\s*\d+\s+CONT\s(.*)$")
concRE = re.compile(r"\s*\d+\s+CONC\s(.*)$")
personRE = re.compile(r"\s*\d+\s+\@(\S+)\@\s+INDI(.*)$")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class CurrentState:

    def __init__(self):
        self.note = ""
        self.name_cnt = 0
        self.person = None

    def add_to_note(self,text):
        self.note += text

    def get_text(self):
        return self.note

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class NoteParser:
    def __init__(self, filename,broken,override):
       if override:
           if override == 1:
               self.cnv = ansel_to_utf8
           elif override == 2:
               self.cnv = latin_to_utf8
           else:
               self.cnv = nocnv
       else:
           f = open(filename,"rU")
           for index in range(50):
               line = f.readline().split()
               if len(line) > 2 and line[1] == 'CHAR':
                   if line[2] == "ANSEL":
                       self.cnv = ansel_to_utf8
                   elif line[2] in ["UNICODE","UTF-8","UTF8"]:
                       self.cnv = nocnv
                   else:
                       self.cnv = latin_to_utf8
           f.close()

       self.name_map = {}

       self.count = 0
       self.person_count = 0
       f = open(filename,"rU")
       innote = False
        
       for line in f:
           try:
               text = string.translate(line,_transtable,_delc)
           except:
               text = line

           try:
               text = self.cnv(text)
           except:
               text = string.translate(text,_transtable2)

           self.count += 1
           if innote:
               match = contRE.match(text)
               if match:
                   noteobj.append("\n" + match.groups()[0])
                   continue

               match = concRE.match(text)
               if match:
                   if broken:
                       noteobj.append(" " + match.groups()[0])
                   else:
                       noteobj.append(match.groups()[0])
                   continue
               # Here we have finished parsing CONT/CONC tags for the NOTE
               # and ignored the rest of the tags (SOUR,CHAN,REFN,RIN).
               innote = False
           match = noteRE.match(text)
           if match:
               data = match.groups()[0]
               noteobj = RelLib.Note()
               self.name_map["@%s@" % data] = noteobj
               noteobj.append(match.groups()[1])
               innote = True
           elif personRE.match(line):
               self.person_count += 1
               
       f.close()

    def get_map(self):
        return self.name_map

    def get_lines(self):
        return self.count

    def get_persons(self):
        return self.person_count

#-------------------------------------------------------------------------
#
# Reader - serves as the lexical analysis engine
#
#-------------------------------------------------------------------------
class Reader:

    def __init__(self,name):
        self.f = open(name,'rU')
        self.current_list = []
        self.eof = False
        self.cnv = lambda s: unicode(s)
        self.broken_conc = False
        self.cnt = 0
        self.index = 0

    def set_charset_fn(self,cnv):
        self.cnv = cnv

    def set_broken_conc(self,broken):
        self.broken_conc = broken

    def read(self):
        if len(self.current_list) <= 1 and not self.eof:
            self.readahead()
        try:
            self.current = self.current_list.pop()
            return self.current
        except:
            return None

    def readahead(self):
        while len(self.current_list) < 5:
            old_line = self.f.readline()
            self.index += 1
            line = old_line.strip('\r\n')
            if line == "" and line != old_line:
                continue
            if line == "":
                self.f.close()
                self.eof = True
                break
            line = line.split(None,2) + ['']

            val = line[2].translate(_transtable,_delc)
            try:
                val = self.cnv(val)
            except:
                val = self.cnv(val.translate(_transtable2))

            try:
                level = int(line[0])
            except:
                level = 0

            data = (level,tokens.get(line[1],TOKEN_UNKNOWN),val,
                    self.cnv(line[1]),self.index)

            if data[1] == TOKEN_CONT:
                l = self.current_list[0]
                self.current_list[0] = (l[0],l[1],l[2]+'\n'+data[2],l[3],l[4])
            elif data[1] == TOKEN_CONC:
                l = self.current_list[0]
                if self.broken_conc:
                    new_value = u"%s %s" % (l[2],data[2])
                else:
                    new_value = l[2] + data[2]
                self.current_list[0] = (l[0],l[1],new_value,l[3],l[4])
            else:
                self.current_list.insert(0,data)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GedcomParser(UpdateCallback):

    SyntaxError = "Syntax Error"
    BadFile = "Not a GEDCOM file"

    def __init__(self,dbase,filename,callback,codeset,note_map,lines,people):
        UpdateCallback.__init__(self,callback)
        self.set_total(lines)

        self.maxpeople = people
        self.dp = GedcomDateParser()
        self.db = dbase
        self.emapper = IdFinder(dbase.get_gramps_ids(EVENT_KEY),
                                dbase.eprefix)
        
        self.person = None
        self.inline_srcs = {}
        self.media_map = {}
        self.fmap = {}
        self.smap = {}
        self.note_map = note_map
        self.refn = {}
        self.added = set()
        self.gedmap = GedcomInfoDB()
        self.gedsource = self.gedmap.get_from_source_tag('GEDCOM 5.5')
        self.def_src = RelLib.Source()
        fname = os.path.basename(filename).split('\\')[-1]
        self.def_src.set_title(_("Import from %s") % unicode(fname))
        self.dir_path = os.path.dirname(filename)
        self.localref = 0
        self.placemap = {}
        self.broken_conc_list = [ 'FamilyOrigins', 'FTW' ]
        self.is_ftw = 0
        self.idswap = {}
        self.gid2id = {}
        self.sid2id = {}
        self.lid2id = {}
        self.fid2id = {}
        self.rid2id = {}

        self.repo_func = {
            TOKEN_NAME   : self.func_repo_name,
            TOKEN_ADDR   : self.func_repo_addr,
            }

        self.name_func = {
            TOKEN_ALIA   : self.func_name_alia,
            TOKEN_NPFX   : self.func_name_npfx,
            TOKEN_GIVN   : self.func_name_givn,
            TOKEN_SPFX   : self.func_name_spfx,
            TOKEN_SURN   : self.func_name_surn,
            TOKEN__MARNM : self.func_name_marnm,
            TOKEN_TITL   : self.func_name_titl,
            TOKEN_NSFX   : self.func_name_nsfx,
            TOKEN_NICK   : self.func_name_nick,
            TOKEN__AKA   : self.func_name_aka,
            TOKEN_SOUR   : self.func_name_sour,
            TOKEN_NOTE   : self.func_name_note,
            }

        self.person_func = {
            TOKEN_NAME  : self.func_person_name,
            TOKEN_ALIA  : self.func_person_alt_name,
            TOKEN_OBJE  : self.func_person_object,
            TOKEN_NOTE  : self.func_person_note,
            TOKEN__COMM : self.func_person_note,
            TOKEN_SEX   : self.func_person_sex,
            TOKEN_BAPL  : self.func_person_bapl,
            TOKEN_ENDL  : self.func_person_endl,
            TOKEN_SLGC  : self.func_person_slgc,
            TOKEN_FAMS  : self.func_person_fams,
            TOKEN_FAMC  : self.func_person_famc,
            TOKEN_RESI  : self.func_person_resi,
            TOKEN_ADDR  : self.func_person_addr,
            TOKEN_PHON  : self.func_person_phon,
            TOKEN_BIRT  : self.func_person_birt,
            TOKEN_ADOP  : self.func_person_adop,
            TOKEN_DEAT  : self.func_person_deat,
            TOKEN_EVEN  : self.func_person_even,
            TOKEN_SOUR  : self.func_person_sour,
            TOKEN_REFN  : self.func_person_refn,
            TOKEN_AFN   : self.func_person_attr,
            TOKEN_RFN   : self.func_person_attr,
            TOKEN__UID  : self.func_person_attr,
            TOKEN_CHAN  : self.skip_record,
            TOKEN_ASSO  : self.func_person_asso,
            TOKEN_ANCI  : self.skip_record,
            TOKEN_DESI  : self.skip_record,
            TOKEN_RIN   : self.skip_record,
            TOKEN__TODO : self.skip_record,
            }

        self.place_names = set()
        cursor = dbase.get_place_cursor()
        data = cursor.next()
        while data:
            (handle,val) = data
            self.place_names.add(val[2])
            data = cursor.next()
        cursor.close()

        self.lexer = Reader(filename)
        self.filename = filename
        self.backoff = False
        self.override = codeset

        if self.db.get_number_of_people() == 0:
            self.map_gid = self.map_gid_empty
        else:
            self.map_gid = self.map_gid_not_empty

        if self.override != 0:
            if self.override == 1:
                self.lexer.set_charset_fn(ansel_to_utf8)
            elif self.override == 2:
                self.lexer.set_charset_fn(latin_to_utf8)

        self.geddir = os.path.dirname(os.path.normpath(os.path.abspath(filename)))
    
        self.error_count = 0
        amap = Utils.personalConstantAttributes
        
        self.attrs = amap.values()
        self.gedattr = {}
        for val in amap.keys():
            self.gedattr[amap[val]] = val

        self.search_paths = []

        try:
            mypaths = []
            f = open("/proc/mounts","r")

            for line in f:
                paths = line.split()
                ftype = paths[2].upper()
                if ftype in file_systems.keys():
                    mypaths.append((paths[1],file_systems[ftype]))
                    self.search_paths.append(paths[1])
            f.close()
        except:
            pass

    def errmsg(self,msg):
        log.warning(msg)

    def infomsg(self,msg):
        log.warning(msg)

    def find_file(self,fullname,altpath):
        tries = []
        fullname = fullname.replace('\\','/')
        tries.append(fullname)
        
        if os.path.isfile(fullname):
            return (1,fullname)
        other = os.path.join(altpath,fullname)
        tries.append(other)
        if os.path.isfile(other):
            return (1,other)
        other = os.path.join(altpath,os.path.basename(fullname))
        tries.append(other)
        if os.path.isfile(other):
            return (1,other)
        if len(fullname) > 3:
            if fullname[1] == ':':
                fullname = fullname[2:]
                for path in self.search_paths:
                    other = os.path.normpath("%s/%s" % (path,fullname))
                    tries.append(other)
                    if os.path.isfile(other):
                        return (1,other)
            return (0,tries)
        else:
            return (0,tries)

    def get_next(self):
        if not self.backoff:
            self.groups = self.lexer.read()
            self.update()
            
            # EOF ?
            if not self.groups:
                self.text = "";
                self.backoff = False
                msg = _("Premature end of file at line %d.\n") % self.groups[4]
                self.errmsg(msg)
                self.error_count += 1
                self.groups = (-1, TOKEN_UNKNOWN, "","")
                return self.groups

        self.backoff = False
        return self.groups
            
    def barf(self,level):
        msg = _("Line %d was not understood, so it was ignored.") % self.groups[4]
        self.errmsg(msg)
        self.error_count += 1
        self.ignore_sub_junk(level)

    def warn(self,msg):
        self.errmsg(msg)
        self.error_count += 1

    def backup(self):
        self.backoff = True

    def parse_gedcom_file(self,use_trans=False):
        if self.maxpeople < 1000:
            no_magic = True
        else:
            no_magic = False
        self.trans = self.db.transaction_begin("",not use_trans,no_magic)

        self.db.disable_signals()
        self.fam_count = 0
        self.indi_count = 0
        self.repo_count = 0
        self.source_count = 0
        try:
            self.parse_header()
            self.parse_submitter()
            self.db.add_source(self.def_src,self.trans)
            self.parse_record()
            self.parse_trailer()
        except Errors.GedcomError, err:
            self.errmsg(str(err))
            
        for value in self.inline_srcs.keys():
            title,note = value
            handle = self.inline_srcs[value]
            src = RelLib.Source()
            src.set_handle(handle)
            src.set_title(title)
            if note:
                src.set_note(note)
            self.db.add_source(src,self.trans)
            
        self.db.transaction_commit(self.trans,_("GEDCOM import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        
    def parse_trailer(self):
        matches = self.get_next()
        if matches[0] >= 0 and matches[1] != TOKEN_TRLR:
            self.barf(0)
        
    def parse_header(self):
        self.parse_header_head()
        self.parse_header_source()

    def parse_submitter(self):
        matches = self.get_next()
        if matches[2] != "SUBM":
            self.backup()
            return
        else:
            self.parse_submitter_data(1)

    def parse_submitter_data(self,level):
        while(1):
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_NAME:
                self.def_src.set_author(matches[2])
            elif matches[1] == TOKEN_ADDR:
                self.ignore_sub_junk(level+1)

    def parse_source(self,name,level):
        self.source = self.find_or_create_source(name[1:-1])
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                if not self.source.get_title():
                    self.source.set_title("No title - ID %s" % self.source.get_gramps_id())
                self.db.commit_source(self.source, self.trans)
                self.backup()
                return
            elif matches[1] == TOKEN_TITL:
                title = matches[2]
                title = title.replace('\n',' ')
                self.source.set_title(title)
            elif matches[1] in (TOKEN_TAXT,TOKEN_PERI): # EasyTree Sierra On-Line
                if self.source.get_title() == "":
                    title = matches[2]
                    title = title.replace('\n',' ')
                    self.source.set_title(title)
            elif matches[1] == TOKEN_AUTH:
                self.source.set_author(matches[2])
            elif matches[1] == TOKEN_PUBL:
                self.source.set_publication_info(matches[2])
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,self.source,level+1,note)
                self.source.set_note(note)
            elif matches[1] == TOKEN_TEXT:
                note = self.source.get_note()
                self.source.set_note(note.strip())
            elif matches[1] == TOKEN_ABBR:
                self.source.set_abbreviation(matches[2])
            elif matches[1] == TOKEN_REPO:
                repo_ref = RelLib.RepoRef()
                repo = self.find_or_create_repository(matches[2][1:-1])
                repo_ref.set_reference_handle(repo.handle)
                self.parse_repo_ref(matches,repo_ref,level+1)
                self.source.add_repo_reference(repo_ref)
            elif matches[1] in (TOKEN_OBJE,TOKEN_CHAN,TOKEN_IGNORE):
                self.ignore_sub_junk(2)
            else:
                note = self.source.get_note()
                if note:
                    note = "%s\n%s %s" % (note,matches[3],matches[2])
                else:
                    note = "%s %s" % (matches[3],matches[2])
                self.source.set_note(note.strip())

    def parse_record(self):
        while True:
            matches = self.get_next()
            if matches[2] == "FAM":
                self.fam_count = self.fam_count + 1
                self.family = self.find_or_create_family(matches[3][1:-1])
                self.parse_family()
                if self.addr != None:
                    father_handle = self.family.get_father_handle()
                    father = self.db.get_person_from_handle(father_handle)
                    if father:
                        father.add_address(self.addr)
                        self.db.commit_person(father, self.trans)
                    mother_handle = self.family.get_mother_handle()
                    mother = self.db.get_person_from_handle(mother_handle)
                    if mother:
                        mother.add_address(self.addr)
                        self.db.commit_person(mother, self.trans)
                    for child_ref in self.family.get_child_ref_list():
                        child_handle = child_ref.ref
                        child = self.db.get_person_from_handle(child_handle)
                        if child:
                            child.add_address(self.addr)
                            self.db.commit_person(child, self.trans)
                if len(self.family.get_source_references()) == 0:
                    sref = RelLib.SourceRef()
                    sref.set_base_handle(self.def_src.handle)
                    self.family.add_source_reference(sref)
                self.db.commit_family(self.family, self.trans)
                del self.family
            elif matches[2] == "INDI":
                self.indi_count = self.indi_count + 1
                gid = matches[3]
                gid = gid[1:-1]
                self.person = self.find_or_create_person(self.map_gid(gid))
                self.added.add(self.person.handle)
                self.parse_individual(self.person)
                if len(self.person.get_source_references()) == 0:
                    sref = RelLib.SourceRef()
                    sref.set_base_handle(self.def_src.handle)
                    self.person.add_source_reference(sref)
                self.db.commit_person(self.person, self.trans)
                del self.person
            elif matches[2] == "REPO":
                self.repo_count = self.repo_count + 1
                self.repo = self.find_or_create_repository(matches[3][1:-1])
                self.repo.set_type((RelLib.Repository.UNKNOWN,""))
                self.added.add(self.repo.handle)
                self.parse_repository(self.repo)
                self.db.commit_repository(self.repo, self.trans)
                del self.repo
            elif matches[2] in ("SUBM","SUBN"):
                self.ignore_sub_junk(1)
            elif matches[1] in (TOKEN_SUBM,TOKEN_SUBN,TOKEN_OBJE,TOKEN_IGNORE):
                self.ignore_sub_junk(1)
            elif matches[2] == "SOUR":
                self.parse_source(matches[3],1)
            elif matches[2].startswith("SOUR "):
                # A source formatted in a single line, for example:
                # 0 @S62@ SOUR This is the title of the source
                source = self.find_or_create_source(matches[3][1:-1])
                source.set_title( matches[2][5:])
                self.db.commit_source(source, self.trans)
            elif matches[2][0:4] == "NOTE":
                self.ignore_sub_junk(1)
            elif matches[2] == "_LOC":
                # TODO: Add support for extended Locations.
                # See: http://en.wiki.genealogy.net/index.php/Gedcom_5.5EL
                self.ignore_sub_junk(1)
            elif matches[0] < 0 or matches[1] == TOKEN_TRLR:
                self.backup()
                return
            else:
                self.barf(1)

    def map_gid_empty(self,gid):
        return gid

    def map_gid_not_empty(self,gid):
        if self.idswap.get(gid):
            return self.idswap[gid]
        else:
            if self.db.id_trans.get(str(gid)):
                self.idswap[gid] = self.db.find_next_person_gramps_id()
            else:
                self.idswap[gid] = gid
            return self.idswap[gid]

    def find_or_create_person(self,gramps_id):
        person = RelLib.Person()
        intid = self.gid2id.get(gramps_id)
        if self.db.has_person_handle(intid):
            person.unserialize(self.db.get_raw_person_data(intid))
        else:
            intid = self.find_person_handle(gramps_id)
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)
        return person

    def find_person_handle(self,gramps_id):
        intid = self.gid2id.get(gramps_id)
        if not intid:
            intid = create_id()
            self.gid2id[gramps_id] = intid
        return intid

    def find_or_create_family(self,gramps_id):
        family = RelLib.Family()
        intid = self.fid2id.get(gramps_id)
        if self.db.has_family_handle(intid):
            family.unserialize(self.db.get_raw_family_data(intid))
        else:
            intid = self.find_family_handle(gramps_id)
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)
        return family

    def find_or_create_repository(self,gramps_id):
        repository = RelLib.Repository()
        intid = self.rid2id.get(gramps_id)
        if self.db.has_repository_handle(intid):
            repository.unserialize(self.db.get_raw_repository_data(intid))
        else:
            intid = self.find_repository_handle(gramps_id)
            repository.set_handle(intid)
            repository.set_gramps_id(gramps_id)
        return repository

    def find_repository_handle(self,gramps_id):
        intid = self.rid2id.get(gramps_id)
        if not intid:
            intid = create_id()
            self.rid2id[gramps_id] = intid
        return intid

    def find_family_handle(self,gramps_id):
        intid = self.fid2id.get(gramps_id)
        if not intid:
            intid = create_id()
            self.fid2id[gramps_id] = intid
        return intid

    def find_or_create_source(self,gramps_id):
        source = RelLib.Source()
        intid = self.sid2id.get(gramps_id)
        if self.db.has_source_handle(intid):
            source.unserialize(self.db.get_raw_source_data(intid))
        else:
            intid = create_id()
            source.set_handle(intid)
            source.set_gramps_id(gramps_id)
            self.db.add_source(source,self.trans)
            self.sid2id[gramps_id] = intid
        return source

    def find_or_create_place(self,title):
        place = RelLib.Place()

        # check to see if we've encountered this name before
        # if we haven't we need to get a new GRAMPS ID
        intid = self.lid2id.get(title)
        if intid == None:
            new_id = self.db.find_next_place_gramps_id()
        else:
            new_id = None

        # check to see if the name already existed in the database
        # if it does, create a new name by appending the GRAMPS ID.
        # generate a GRAMPS ID if needed
        
        if title in self.place_names:
            if not new_id:
                new_id = self.db.find_next_place_gramps_id()
            pname = "%s [%s]" % (title,new_id)
        else:
            pname = title
            
        if self.db.has_place_handle(intid):
            place.unserialize(self.db.get_raw_place_data(intid))
        else:
            intid = create_id()
            place.set_handle(intid)
            place.set_title(pname)
            load_place_values(place,pname)
            place.set_gramps_id(new_id)
            self.db.add_place(place,self.trans)
            self.lid2id[title] = intid
        return place

    def parse_cause(self,event,level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_SOUR:
                event.add_source_reference(self.handle_source(matches,level+1))
            else:
                self.barf(1)
                
    def parse_repo_caln(self, matches, repo, level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_CALN:
                repo.set_call_number(matches[2])
                #self.parse_repo_caln(matches, repo. level+1)
            elif matches[1] == TOKEN_NOTE:
                repo.set_note(matches[2])
            else:
                self.barf(1)

    def parse_repo_ref(self, matches, repo_ref, level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_CALN:
                repo_ref.set_call_number(matches[2])
                self.parse_repo_ref_caln(repo_ref, level+1)
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,repo_ref,level+1,"")
                repo_ref.set_note(note)
            else:
                self.barf(1)

    def parse_repo_ref_caln(self, reporef, level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_MEDI:
                reporef.media_type.set(matches[2])
            else:
                self.barf(1)
                
    def parse_note_data(self,level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] in (TOKEN_SOUR,TOKEN_CHAN,TOKEN_REFN):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_RIN:
                pass
            else:
                self.barf(level+1)

    def parse_ftw_relations(self,level):
        mrel = RelLib.ChildRefType()
        frel = RelLib.ChildRefType()
        
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return (mrel,frel)
            # FTW
            elif matches[1] == TOKEN__FREL:
                frel = pedi_type.get(matches[2].lower(),_TYPE_BIRTH)
            # FTW
            elif matches[1] == TOKEN__MREL:
                mrel = pedi_type.get(matches[2].lower(),_TYPE_BIRTH)
            elif matches[1] == TOKEN_ADOP:
                mrel = _TYPE_ADOPT
                frel = _TYPE_ADOPT
            # Legacy
            elif matches[1] == TOKEN__STAT:
                mrel = _TYPE_BIRTH
                frel = _TYPE_BIRTH
            # Legacy _PREF
            elif matches[1] and matches[1][0] == TOKEN_UNKNOWN:
                pass
            else:
                self.barf(level+1)
        return None
    
    def parse_family(self):
        self.addr = None
        note = ""
        while True:
            matches = self.get_next()

            if int(matches[0]) < 1:
                self.backup()
                return
            elif matches[1] == TOKEN_HUSB:
                gid = matches[2]
                handle = self.find_person_handle(self.map_gid(gid[1:-1]))
                self.family.set_father_handle(handle)
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_WIFE:
                gid = matches[2]
                handle = self.find_person_handle(self.map_gid(gid[1:-1]))
                self.family.set_mother_handle(handle)
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_SLGS:
                lds_ord = RelLib.LdsOrd()
                lds_ord.set_type(RelLib.LdsOrd.SEAL_TO_SPOUSE)
                self.family.lds_ord_list.append(lds_ord)
                self.parse_ord(lds_ord,2)
            elif matches[1] == TOKEN_ADDR:
                self.addr = RelLib.Address()
                self.addr.set_street(matches[2])
                self.parse_address(self.addr,2)
            elif matches[1] == TOKEN_CHIL:
                mrel,frel = self.parse_ftw_relations(2)
                gid = matches[2]
                child = self.find_or_create_person(self.map_gid(gid[1:-1]))

                ref = RelLib.ChildRef()
                ref.ref = child.handle
                ref.set_father_relation(frel)
                ref.set_mother_relation(mrel)
                self.family.add_child_ref(ref)
            elif matches[1] == TOKEN_NCHI:
                a = RelLib.Attribute()
                a.set_type(RelLib.Attribute.NUM_CHILD)
                a.set_value(matches[2])
                self.family.add_attribute(a)
            elif matches[1] == TOKEN_SOUR:
                source_ref = self.handle_source(matches,2)
                self.family.add_source_reference(source_ref)
            elif matches[1] in (TOKEN_RIN, TOKEN_SUBM, TOKEN_REFN,TOKEN_CHAN):
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_OBJE:
                if matches[2] and matches[2][0] == '@':
                    self.barf(2)
                else:
                    self.parse_family_object(2)
            elif matches[1] == TOKEN__COMM:
                note = matches[2]
                self.family.set_note(note)
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,self.family,1,note)
            else:
                event = RelLib.Event()
                event.set_gramps_id(self.emapper.find_next())
                try:
                    event.set_type(RelLib.EventType(ged2fam[matches[3]]))
                except:
                    if ged2fam_custom.has_key(matches[3]):
                        event.set_type(RelLib.EventType((RelLib.EventType.CUSTOM,ged2fam_custom[matches[3]])))
                    elif matches[3]:
                        event.set_type(RelLib.EventType((RelLib.EventType.CUSTOM,matches[3])))
                    else:
                        event.set_type((RelLib.EventType(RelLib.EventType.UNKNOWN)))
                    if matches[2] and not event.get_description():
                        event.set_description(matches[2])
                self.parse_family_event(event,2)
                if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                    self.family.type.set(RelLib.FamilyRelType.MARRIED)
                if int(event.get_type()) != RelLib.EventType.CUSTOM:
                    if not event.get_description():
                        text = _event_family_str % {
                            'event_name' : str(event.get_type()),
                            'family' : Utils.family_name(self.family,self.db),
                            }
                        event.set_description(text)
                self.db.add_event(event,self.trans)

                event_ref = RelLib.EventRef()
                event_ref.set_reference_handle(event.handle)
                event_ref.set_role(RelLib.EventRoleType.FAMILY)
                self.family.add_event_ref(event_ref)
                del event

    def parse_note_base(self,matches,obj,level,old_note,task):
        # reference to a named note defined elsewhere
        if matches[2] and matches[2][0] == "@":
            note_obj = self.note_map.get(matches[2])
            if note_obj:
                new_note = note_obj.get()
            else:
                new_note = u""
        else:
            new_note = matches[2]
            self.ignore_sub_junk(level+1)
        if old_note:
            note = u"%s\n%s" % (old_note,matches[2])
        else:
            note = new_note
        task(note)
        return note
        
    def parse_note(self,matches,obj,level,old_note):
        return self.parse_note_base(matches,obj,level,old_note,obj.set_note)

    def parse_comment(self,matches,obj,level,old_note):
        return self.parse_note_base(matches,obj,level,old_note,obj.set_note)

    def parse_individual(self,person):
        state = CurrentState()
        state.person = person

        while True:
            matches = self.get_next()
            
            if int(matches[0]) < 1:
                self.backup()
                if state.get_text():
                    state.person.set_note(state.get_text())
                return
            else:
                func = self.person_func.get(matches[1],self.func_person_event)
                func(matches,state)
                
    def parse_optional_note(self,level):
        note = ""
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return note
            elif matches[1] == TOKEN_NOTE:
                if not matches[2].strip() or matches[2] and matches[2][0] != "@":
                    note = matches[2]
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
                self.barf(level+1)
        return None
        
    def parse_famc_type(self,level,person):
        ftype = _TYPE_BIRTH
        note = ""
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return (ftype,note)
            elif matches[1] == TOKEN_PEDI:
                ftype = pedi_type.get(matches[2],RelLib.Person.UNKNOWN)
            elif matches[1] == TOKEN_SOUR:
                source_ref = self.handle_source(matches,level+1)
                person.primary_name.add_source_reference(source_ref)
            elif matches[1] == TOKEN__PRIMARY:
                pass #type = matches[1]
            elif matches[1] == TOKEN_NOTE:
                if not matches[2].strip() or matches[2] and matches[2][0] != "@":
                    note = matches[2]
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
                self.barf(level+1)
        return None
    
    def parse_person_object(self,level,state):
        form = ""
        filename = ""
        title = "no title"
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == TOKEN_FORM:
                form = matches[2].lower()
            elif matches[1] == TOKEN_TITL:
                title = matches[2]
            elif matches[1] == TOKEN_FILE:
                filename = matches[2]
            elif matches[1] == TOKEN_NOTE:
                note = matches[2]
            elif matches[1] == TOKEN_UNKNOWN:
                self.ignore_sub_junk(level+1)
            else:
                self.barf(level+1)

        if form == "url":
            url = RelLib.Url()
            url.set_path(filename)
            url.set_description(title)
            state.person.add_url(url)
        else:
            (ok,path) = self.find_file(filename,self.dir_path)
            if not ok:
                self.warn(_("Could not import %s") % filename)
                path = filename.replace('\\','/')
            photo_handle = self.media_map.get(path)
            if photo_handle == None:
                photo = RelLib.MediaObject()
                photo.set_path(path)
                photo.set_description(title)
                photo.set_mime_type(Mime.get_type(os.path.abspath(path)))
                self.db.add_object(photo, self.trans)
                self.media_map[path] = photo.handle
            else:
                photo = self.db.get_object_from_handle(photo_handle)
            oref = RelLib.MediaRef()
            oref.set_reference_handle(photo.handle)
            oref.set_note(note)
            state.person.add_media_reference(oref)

    def parse_family_object(self,level):
        form = ""
        filename = ""
        title = ""
        note = ""
        while True:
            matches = self.get_next()
            if matches[1] == TOKEN_FORM:
                form = matches[2].lower()
            elif matches[1] == TOKEN_TITL:
                title = matches[2]
            elif matches[1] == TOKEN_FILE:
                filename = matches[2]
            elif matches[1] == TOKEN_NOTE:
                note = matches[2]
            elif int(matches[0]) < level:
                self.backup()
                break
            else:
                self.barf(level+1)
                
        if form:
            (ok,path) = self.find_file(filename,self.dir_path)
            if not ok:
                self.warn(_("Could not import %s") % filename)
                path = filename.replace('\\','/')
            photo_handle = self.media_map.get(path)
            if photo_handle == None:
                photo = RelLib.MediaObject()
                photo.set_path(path)
                photo.set_description(title)
                photo.set_mime_type(Mime.get_type(os.path.abspath(path)))
                self.db.add_object(photo, self.trans)
                self.media_map[path] = photo.handle
            else:
                photo = self.db.get_object_from_handle(photo_handle)
            oref = RelLib.MediaRef()
            oref.set_reference_handle(photo.handle)
            oref.set_note(note)
            self.family.add_media_reference(oref)

    def parse_residence(self,address,level):
        note = ""
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return 
            elif matches[1] == TOKEN_DATE:
                address.set_date_object(self.extract_date(matches[2]))
            elif matches[1] == TOKEN_ADDR:
                address.set_street(matches[2])
                self.parse_address(address,level+1)
            elif matches[1] in (TOKEN_IGNORE,TOKEN_CAUS,TOKEN_STAT,
                                TOKEN_TEMP,TOKEN_OBJE,TOKEN_TYPE):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_SOUR:
                address.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_PLAC:
                address.set_street(matches[2])
                self.parse_address(address,level+1)
            elif matches[1] == TOKEN_PHON:
                address.set_street("Unknown")
                address.set_phone(matches[2])
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,address,level+1,note)
            else:
                self.barf(level+1)

    def parse_address(self,address,level):
        first = 0
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                if matches[1] == TOKEN_PHON:
                    address.set_phone(matches[2])
                else:
                    self.backup()
                return
            elif matches[1] in (TOKEN_ADDR, TOKEN_ADR1, TOKEN_ADR2):
                val = address.get_street()
                if first == 0:
                    val = matches[2]
                    first = 1
                else:
                    val = "%s,%s" % (val,matches[2])
                address.set_street(val)
            elif matches[1] == TOKEN_CITY:
                address.set_city(matches[2])
            elif matches[1] == TOKEN_STAE:
                address.set_state(matches[2])
            elif matches[1] == TOKEN_POST:
                address.set_postal_code(matches[2])
            elif matches[1] == TOKEN_CTRY:
                address.set_country(matches[2])
            elif matches[1] == TOKEN_PHON:
                address.set_phone(matches[2])
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,address,level+1,note)
            elif matches[1] == TOKEN__LOC:
                pass    # ignore unsupported extended location syntax
            elif matches[1] == TOKEN__NAME:
                pass    # ignore
            else:
                self.barf(level+1)

    def parse_ord(self,lds_ord,level):
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == TOKEN_TEMP:
                value = self.extract_temple(matches)
                if value:
                    lds_ord.set_temple(value)
            elif matches[1] == TOKEN_DATE:
                lds_ord.set_date_object(self.extract_date(matches[2]))
            elif matches[1] == TOKEN_FAMC:
                lds_ord.set_family_handle(self.find_family_handle(matches[2][1:-1]))
            elif matches[1] == TOKEN_PLAC:
              try:
                place = self.find_or_create_place(matches[2])
                place.set_title(matches[2])
                load_place_values(place,matches[2])
                place_handle = place.handle
                lds_ord.set_place_handle(place_handle)
                self.ignore_sub_junk(level+1)
              except NameError:
                  pass
            elif matches[1] == TOKEN_SOUR:
                lds_ord.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,lds_ord,level+1,note)
            elif matches[1] == TOKEN_STAT:
                lds_ord.set_status(lds_status.get(matches[2],RelLib.LdsOrd.STATUS_NONE))
            else:
                self.barf(level+1)

    def parse_person_event(self,event,level):
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                if note:
                    event.set_note(note)
                self.backup()
                break
            elif matches[1] == TOKEN_TYPE:
                if event.get_type().is_custom():
                    if ged2gramps.has_key(matches[2]):
                        name = RelLib.EventType(ged2gramps[matches[2]])
                    else:
                        val = self.gedsource.tag2gramps(matches[2])
                        if val:
                            name = RelLib.EventType((RelLib.EventType.CUSTOM,val))
                        else:
                            name = RelLib.EventType((RelLib.EventType.CUSTOM,matches[3]))
                    event.set_type(name)
                else:
                    event.set_description(matches[2])
            elif matches[1] == TOKEN__PRIV and  matches[2] == "Y":
                event.set_privacy(True)
            elif matches[1] == TOKEN_DATE:
                event.set_date_object(self.extract_date(matches[2]))
            elif matches[1] == TOKEN_SOUR:
                event.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_PLAC:
                val = matches[2]
                n = event.get_type()
                if self.is_ftw and int(n) in [RelLib.EventType.OCCUPATION,RelLib.EventType.DEGREE]:
                    event.set_description(val)
                    self.ignore_sub_junk(level+1)
                else:
                    place = self.find_or_create_place(val)
                    place_handle = place.handle
                    place.set_title(matches[2])
                    load_place_values(place,matches[2])
                    event.set_place_handle(place_handle)
                    self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_CAUS:
                info = matches[2]
                event.set_cause(info)
                self.parse_cause(event,level+1)
            elif matches[1] in (TOKEN_NOTE,TOKEN_OFFI):
                info = self.parse_note(matches,event,level+1,note)
                if note == "":
                    note = info
                else:
                    note = "\n%s" % info
            elif matches[1] in (TOKEN__GODP, TOKEN__WITN, TOKEN__WTN):
#                if matches[2][0] == "@":
#                    witness_handle = self.find_person_handle(self.map_gid(matches[2][1:-1]))
#                    witness = RelLib.Witness(RelLib.Event.ID,witness_handle)
#                else:
#                    witness = RelLib.Witness(RelLib.Event.NAME,matches[2])
#                event.add_witness(witness)
                self.ignore_sub_junk(level+1)
            elif matches[1] in (TOKEN_RELI, TOKEN_TIME, TOKEN_ADDR,TOKEN_IGNORE,
                                TOKEN_STAT,TOKEN_TEMP,TOKEN_OBJE):
                self.ignore_sub_junk(level+1)
            else:
                self.barf(level+1)

    def parse_adopt_event(self,event,level):
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                if note != "":
                    event.set_note(note)
                self.backup()
                break
            elif matches[1] == TOKEN_DATE:
                event.set_date_object(self.extract_date(matches[2]))
            elif matches[1] in (TOKEN_TIME,TOKEN_ADDR,TOKEN_IGNORE,
                                TOKEN_STAT,TOKEN_TEMP,TOKEN_OBJE):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_SOUR:
                event.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_FAMC:
                handle = self.find_family_handle(matches[2][1:-1])
                mrel,frel = self.parse_adopt_famc(level+1);
                if self.person.get_main_parents_family_handle() == handle:
                    self.person.set_main_parent_family_handle(None)
                self.person.add_parent_family_handle(handle)
                if mrel != RelLib.ChildRefType.BIRTH or frel != RelLib.ChildRefType.BIRTH:
                    print "NOT FIXED YET"
            elif matches[1] == TOKEN_PLAC:
                val = matches[2]
                place = self.find_or_create_place(val)
                place_handle = place.handle
                place.set_title(matches[2])
                load_place_values(place,matches[2])
                event.set_place_handle(place_handle)
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_TYPE:
                # eventually do something intelligent here
                pass
            elif matches[1] == TOKEN_CAUS:
                info = matches[2]
                event.set_cause(info)
                self.parse_cause(event,level+1)
            elif matches[1] == TOKEN_NOTE:
                info = self.parse_note(matches,event,level+1,note)
                if note == "":
                    note = info
                else:
                    note = "\n%s" % info
            else:
                self.barf(level+1)

    def parse_adopt_famc(self,level):
        mrel = _TYPE_ADOPT
        frel = _TYPE_ADOPT
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return (mrel,frel)
            elif matches[1] == TOKEN_ADOP:
                if matches[2] == "HUSB":
                    mrel = _TYPE_BIRTH
                elif matches[2] == "WIFE":
                    frel = _TYPE_BIRTH
            else:
                self.barf(level+1)
        return None
    
    def parse_person_attr(self,attr,level):
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                break
            elif matches[1] == TOKEN_TYPE:
                if attr.get_type() == "":
                    if ged2gramps.has_key(matches[2]):
                        name = ged2gramps[matches[2]]
                    else:
                        val = self.gedsource.tag2gramps(matches[2])
                        if val:
                            name = val
                        else:
                            name = matches[2]
                    attr.set_type(name)
            elif matches[1] in (TOKEN_CAUS,TOKEN_DATE,TOKEN_TIME,TOKEN_ADDR,
                                TOKEN_IGNORE,TOKEN_STAT,TOKEN_TEMP,TOKEN_OBJE):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_SOUR:
                attr.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_PLAC:
                val = matches[2]
                if attr.get_value() == "":
                    attr.set_value(val)
                    self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_DATE:
                note = "%s\n\n" % ("Date : %s" % matches[2])
            elif matches[1] == TOKEN_NOTE:
                info = self.parse_note(matches,attr,level+1,note)
                if note == "":
                    note = info
                else:
                    note = "%s\n\n%s" % (note,info)
            else:
                self.barf(level+1)
        if note != "":
            attr.set_note(note)

    def parse_family_event(self,event,level):
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                if note:
                    event.set_note(note)
                self.backup()
                break
            elif matches[1] == TOKEN_TYPE:
                etype = event.get_type()
                if etype.is_custom() == RelLib.EventType.CUSTOM:
                    event.set_type(RelLib.EventType((RelLib.EventType.CUSTOM,matches[2])))
                else:
                    note = 'Status = %s\n' % matches[2]
            elif matches[1] == TOKEN_DATE:
                event.set_date_object(self.extract_date(matches[2]))
            elif matches[1] == TOKEN_CAUS:
                info = matches[2]
                event.set_cause(info)
                self.parse_cause(event,level+1)
            elif matches[1] in (TOKEN_TIME,TOKEN_IGNORE,TOKEN_ADDR,TOKEN_STAT,
                                TOKEN_TEMP,TOKEN_HUSB,TOKEN_WIFE,TOKEN_OBJE):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_SOUR:
                event.add_source_reference(self.handle_source(matches,level+1))
            elif matches[1] == TOKEN_PLAC:
                val = matches[2]
                place = self.find_or_create_place(val)
                place_handle = place.handle
                place.set_title(matches[2])
                load_place_values(place,matches[2])
                event.set_place_handle(place_handle)
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_OFFI:
                if note == "":
                    note = matches[2]
                else:
                    note = note + "\n" + matches[2]
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,event,level+1,note)
            elif matches[1] in (TOKEN__WITN, TOKEN__WTN):
                pass
#                if matches[2][0] == "@":
#                    witness_handle = self.find_person_handle(self.map_gid(matches[2][1:-1]))
#                    witness = RelLib.Witness(RelLib.Event.ID,witness_handle)
#                else:
#                    witness = RelLib.Witness(RelLib.Event.NAME,matches[2])
#                event.add_witness(witness)
                self.ignore_sub_junk(level+1)
            else:
                self.barf(level+1)

    def parse_source_reference(self,source,level):
        """Reads the data associated with a SOUR reference"""
        note = ""
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                source.set_note(note)
                self.backup()
                return
            elif matches[1] == TOKEN_PAGE:
                source.set_page(matches[2])
            elif matches[1] == TOKEN_DATE:
                source.set_date_object(self.extract_date(matches[2]))
            elif matches[1] == TOKEN_DATA:
                date,text = self.parse_source_data(level+1)
                if date:
                    d = self.dp.parse(date)
                    source.set_date_object(d)
                source.set_text(text)
            elif matches[1] in (TOKEN_OBJE,TOKEN_REFN):
                self.ignore_sub_junk(level+1)
            elif matches[1] == TOKEN_QUAY:
                try:
                    val = int(matches[2])
                except ValueError:
                    return
                if val > 1:
                    source.set_confidence_level(val+1)
                else:
                    source.set_confidence_level(val)
            elif matches[1] in (TOKEN_NOTE,TOKEN_TEXT):
                note = self.parse_comment(matches,source,level+1,note)
            else:
                self.barf(level+1)
        
    def parse_source_data(self,level):
        """Parses the source data"""
        date = ""
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return (date,note)
            elif matches[1] == TOKEN_DATE:
                date = matches[2]
            elif matches[1] == TOKEN_TEXT:
                note = matches[2]
            else:
                self.barf(level+1)
        return None
    
    def parse_marnm(self,person,text):
        data = text.split()
        if len(data) == 1:
            name = RelLib.Name(person.primary_name)
            name.set_surname(data[0])
            name.set_type(RelLib.NameType.MARRIED)
            person.add_alternate_name(name)
        elif len(data) > 1:
            name = RelLib.Name()
            name.set_surname(data[-1])
            name.set_first_name(' '.join(data[0:-1]))
            name.set_type(RelLib.NameType.MARRIED)
            person.add_alternate_name(name)

    def parse_header_head(self):
        """validiates that this is a valid GEDCOM file"""
        line = self.lexer.read()
        if line[1] != TOKEN_HEAD:
            raise Errors.GedcomError("%s is not a GEDCOM file" % self.filename)

    def parse_header_source(self):
        genby = ""
        note = ""
        while True:
            matches = self.get_next()
            if int(matches[0]) < 1:
                self.backup()
                return
            elif matches[1] == TOKEN_SOUR:
                self.gedsource = self.gedmap.get_from_source_tag(matches[2])
                self.lexer.set_broken_conc(self.gedsource.get_conc())
                if matches[2] == "FTW":
                    self.is_ftw = 1
                genby = matches[2]
            elif matches[1] == TOKEN_NAME:
                pass
            elif matches[1] == TOKEN_VERS:
                self.def_src.set_data_item('Generated by',"%s %s" %
                                                  (genby,matches[2]))
                pass
            elif matches[1] == TOKEN_FILE:
                filename = os.path.basename(matches[2]).split('\\')[-1]
                self.def_src.set_title(_("Import from %s") % filename)
            elif matches[1] == TOKEN_COPR:
                self.def_src.set_publication_info(matches[2])
            elif matches[1] ==  TOKEN_SUBM:
                self.parse_subm(2)
            elif matches[1] in (TOKEN_CORP,TOKEN_DATA,TOKEN_SUBN,TOKEN_LANG):
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_DEST:
                if genby == "GRAMPS":
                    self.gedsource = self.gedmap.get_from_source_tag(matches[2])
                    self.lexer.set_broken_conc(self.gedsource.get_conc())
            elif matches[1] == TOKEN_CHAR and not self.override:
                if matches[2] == "ANSEL":
                    self.lexer.set_charset_fn(ansel_to_utf8)
                elif matches[2] not in ("UNICODE","UTF-8","UTF8"):
                    self.lexer.set_charset_fn(latin_to_utf8)
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN_GEDC:
                self.ignore_sub_junk(2)
            elif matches[1] == TOKEN__SCHEMA:
                self.parse_ftw_schema(2)
            elif matches[1] == TOKEN_PLAC:
                self.parse_place_form(2)
            elif matches[1] == TOKEN_DATE:
                date = self.parse_date(2)
                date.date = matches[2]
                self.def_src.set_data_item('Creation date',matches[2])
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,self.def_src,2,note)
            elif matches[1] == TOKEN_UNKNOWN:
                self.ignore_sub_junk(2)
            else:
                self.barf(2)

    def parse_subm(self, level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_NAME:
                self.def_src.set_author(matches[2])
            else:
                self.ignore_sub_junk(2)

    def parse_ftw_schema(self,level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_INDI:
                self.parse_ftw_indi_schema(level+1)
            elif matches[1] == TOKEN_FAM:
                self.parse_ftw_fam_schema(level+1)
            else:
                self.barf(2)

    def parse_ftw_indi_schema(self,level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            else:
                label = self.parse_label(level+1)
                ged2gramps[matches[1]] = label

    def parse_label(self,level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_LABL:
                return matches[2]
            else:
                self.barf(2)
        return None
    
    def parse_ftw_fam_schema(self,level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            else:
                label = self.parse_label(level+1)
                ged2fam_custom[matches[3]] = label
        return None
    
    def ignore_sub_junk(self,level):
        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                self.backup()
                return
        return
    
    def ignore_change_data(self,level):
        matches = self.get_next()
        if matches[1] == TOKEN_CHAN:
            self.ignore_sub_junk(level+1)
        else:
            self.backup()

    def parse_place_form(self,level):
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return
            elif matches[1] == TOKEN_FORM:
                for item in matches[2].split(','):
                    item = item.lower().strip()
                    fcn = _place_match.get(item,_empty_func)
                    _place_field.append(fcn)
            else:
                self.barf(level+1)
    
    def parse_date(self,level):
        date = DateStruct()
        while True:
            matches = self.get_next()

            if int(matches[0]) < level:
                self.backup()
                return date
            elif matches[1] == TOKEN_TIME:
                date.time = matches[2]
            else:
                self.barf(level+1)
        return None

    def extract_date(self,text):
        dateobj = RelLib.Date()
        try:
            match = rangeRegexp.match(text)
            if match:
                (cal1,data1,cal2,data2) = match.groups()
                if cal1 != cal2:
                    pass
                
                if cal1 == "FRENCH R":
                    cal = RelLib.Date.CAL_FRENCH
                elif cal1 == "JULIAN":
                    cal = RelLib.Date.CAL_JULIAN
                elif cal1 == "HEBREW":
                    cal = RelLib.Date.CAL_HEBREW
                else:
                    cal = RelLib.Date.CAL_GREGORIAN
                    
                start = self.dp.parse(data1)
                stop =  self.dp.parse(data2)
                dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_RANGE, cal,
                            start.get_start_date() + stop.get_start_date())
                return dateobj

            match = spanRegexp.match(text)
            if match:
                (cal1,data1,cal2,data2) = match.groups()
                if cal1 != cal2:
                    pass
                
                if cal1 == "FRENCH R":
                    cal = RelLib.Date.CAL_FRENCH
                elif cal1 == "JULIAN":
                    cal = RelLib.Date.CAL_JULIAN
                elif cal1 == "HEBREW":
                    cal = RelLib.Date.CAL_HEBREW
                else:
                    cal = RelLib.Date.CAL_GREGORIAN
                    
                start = self.dp.parse(data1)
                stop =  self.dp.parse(data2)
                dateobj.set(RelLib.Date.QUAL_NONE, RelLib.Date.MOD_SPAN, cal,
                            start.get_start_date() + stop.get_start_date())
                return dateobj
        
            match = calRegexp.match(text)
            if match:
                (abt,cal,data) = match.groups()
                dateobj = self.dp.parse("%s %s" % (abt, data))
                if cal == "FRENCH R":
                    dateobj.set_calendar(RelLib.Date.CAL_FRENCH)
                elif cal == "JULIAN":
                    dateobj.set_calendar(RelLib.Date.CAL_JULIAN)
                elif cal == "HEBREW":
                    dateobj.set_calendar(RelLib.Date.CAL_HEBREW)
                return dateobj
            else:
                dval = self.dp.parse(text)
                return dval
        except IOError:
            return self.dp.set_text(text)

    def handle_source(self,matches,level):
        source_ref = RelLib.SourceRef()
        if matches[2] and matches[2][0] != "@":
            title = matches[2]
            note = ''
            handle = self.inline_srcs.get((title,note),Utils.create_id())
            self.inline_srcs[(title,note)] = handle
            self.ignore_sub_junk(level+1)
        else:
            handle = self.find_or_create_source(matches[2][1:-1]).handle
            self.parse_source_reference(source_ref,level)
        source_ref.set_base_handle(handle)
        return source_ref

    def resolve_refns(self):
        return
    
        prefix = self.db.iprefix
        index = 0
        new_pmax = self.db.pmap_index
        for pid in self.added:
            index = index + 1
            if self.refn.has_key(pid):
                val = self.refn[pid]
                new_key = prefix % val
                new_pmax = max(new_pmax,val)

                person = self.db.get_person_from_handle(pid,self.trans)

                # new ID is not used
                if not self.db.has_person_handle(new_key):
                    self.db.remove_person(pid,self.trans)
                    person.set_handle(new_key)
                    person.set_gramps_id(new_key)
                    self.db.add_person(person,self.trans)
                else:
                    tp = self.db.get_person_from_handle(new_key,self.trans)
                    # same person, just change it
                    if person == tp:
                        self.db.remove_person(pid,self.trans)
                        person.set_handle(new_key)
                        person.set_gramps_id(new_key)
                        self.db.add_person(person,self.trans)
                    # give up trying to use the refn as a key
                    else:
                        pass

        self.db.pmap_index = new_pmax

    def invert_year(self,subdate):
        return (subdate[0],subdate[1],-subdate[2],subdate[3])

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def func_person_name(self,matches,state):
        name = RelLib.Name()
        m = snameRegexp.match(matches[2])
        if m:
            (n,n2) = m.groups()
            names = (n2,'',n,'','')
        else:
            try:
                names = nameRegexp.match(matches[2]).groups()
            except:
                names = (matches[2],"","","","")
        if names[0]:
            name.set_first_name(names[0].strip())
        if names[2]:
            name.set_surname(names[2].strip())
        if names[4]:
            name.set_suffix(names[4].strip())
        if state.name_cnt == 0:
            state.person.set_primary_name(name)
        else:
            state.person.add_alternate_name(name)
        state.name_cnt += 1
        self.parse_name(name,2,state)

    def func_person_asso(self, matches, state):
        gid = matches[2]
        handle = self.find_person_handle(self.map_gid(gid[1:-1]))
        ref = RelLib.PersonRef()
        ref.ref = handle

        self.person.add_person_ref(ref)
        
        while True:
            matches = self.get_next()

            if int(matches[0]) < 2:
                self.backup()
                return
            elif matches[1] == TOKEN_RELA:
                ref.rel = matches[2]
            elif matches[1] == TOKEN_SOUR:
                ref.add_source_reference(self.handle_source(matches,2))
            elif matches[1] == TOKEN_NOTE:
                note = self.parse_note(matches,ref,2,"")
                ref.set_note(note)
            else:
                self.barf(2)

    def func_person_alt_name(self,matches,state):
        aka = RelLib.Name()
        try:
            names = nameRegexp.match(matches[2]).groups()
        except:
            names = (matches[2],"","","","")
        if names[0]:
            aka.set_first_name(names[0])
        if names[2]:
            aka.set_surname(names[2])
        if names[4]:
            aka.set_suffix(names[4])
        state.person.add_alternate_name(aka)

    def func_person_object(self,matches,state):
        if matches[2] and matches[2][0] == '@':
            self.barf(2)
        else:
            self.parse_person_object(2,state)

    def func_person_note(self,matches,state):
        self.note = self.parse_note(matches,self.person,1,state.note)

    def func_person_sex(self,matches,state):
        if matches[2] == '':
            state.person.set_gender(RelLib.Person.UNKNOWN)
        elif matches[2][0] == "M":
            state.person.set_gender(RelLib.Person.MALE)
        elif matches[2][0] == "F":
            state.person.set_gender(RelLib.Person.FEMALE)
        else:
            state.person.set_gender(RelLib.Person.UNKNOWN)

    def func_person_bapl(self,matches,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.BAPTISM)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_endl(self,matches,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.ENDOWMENT)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_slgc(self,matches,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.SEAL_TO_PARENTS)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_fams(self,matches,state):
        handle = self.find_family_handle(matches[2][1:-1])
        state.person.add_family_handle(handle)
        state.add_to_note(self.parse_optional_note(2))

    def func_person_famc(self,matches,state):
        ftype,famc_note = self.parse_famc_type(2,state.person)
        handle = self.find_family_handle(matches[2][1:-1])
                
        for f in self.person.get_parent_family_handle_list():
            if f[0] == handle:
                break
        else:
            if int(ftype) in rel_types:
                state.person.add_parent_family_handle(handle)
            else:
                if state.person.get_main_parents_family_handle() == handle:
                    state.person.set_main_parent_family_handle(None)
                state.person.add_parent_family_handle(handle)
                print "NEED TO CHANGE CHILDREF TO",ftype,ftype

    def func_person_resi(self,matches,state):
        addr = RelLib.Address()
        state.person.add_address(addr)
        self.parse_residence(addr,2)

    def func_person_addr(self,matches,state):
        addr = RelLib.Address()
        addr.set_street(matches[2])
        self.parse_address(addr,2)
        state.person.add_address(addr)

    def func_person_phon(self,matches,state):
        addr = RelLib.Address()
        addr.set_street("Unknown")
        addr.set_phone(matches[2])
        state.person.add_address(addr)

    def func_person_birt(self,matches,state):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        if matches[2]:
            event.set_description(matches[2])
        event.set_type(RelLib.EventType((RelLib.EventType.BIRTH,"")))
        self.parse_person_event(event,2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event.handle)

        if state.person.get_birth_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_birth_ref(event_ref)

    def func_person_adop(self,matches,state):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(RelLib.EventType(RelLib.EventType.ADOPT))
        self.parse_adopt_event(event,2)
        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event.handle)
        state.person.add_event_ref(event_ref)

    def func_person_deat(self,matches,state):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        if matches[2]:
            event.set_description(matches[2])
        event.type.set(RelLib.EventType.DEATH)
        self.parse_person_event(event,2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event.handle)

        if state.person.get_death_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_death_ref(event_ref)

    def func_person_even(self,matches,state):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        if matches[2]:
            event.set_description(matches[2])
        self.parse_person_event(event,2)
        the_type = event.get_type()
        if int(the_type) == RelLib.EventType.CUSTOM \
               and str(the_type) in self.attrs:
            attr = RelLib.Attribute()
            attr.set_type((RelLib.EventType.CUSTOM,self.gedattr[matches[2]]))
            attr.set_value(event.get_description())
            state.person.add_attribute(attr)
        else:
            self.db.add_event(event, self.trans)
            event_ref = RelLib.EventRef()
            event_ref.set_reference_handle(event.handle)
            state.person.add_event_ref(event_ref)

    def func_person_sour(self,matches,state):
        source_ref = self.handle_source(matches,2)
        state.person.add_source_reference(source_ref)

    def func_person_refn(self,matches,state):
        if intRE.match(matches[2]):
            try:
                self.refn[self.person.handle] = int(matches[2])
            except:
                pass

    def func_person_attr(self,matches,state):
        attr = RelLib.Attribute()
        n = matches[3]
        atype = self.gedattr.get(n,RelLib.AttributeType.CUSTOM)
        if atype == RelLib.AttributeType.CUSTOM:
            attr.set_type((atype,n))
        else:
            attr.set_type(atype)

        attr.set_value(matches[2])
        state.person.add_attribute(attr)

    def func_person_event(self,matches,state):
        n = matches[3].strip()
        if self.gedattr.has_key(n):
            attr = RelLib.Attribute()
            attr.set_type((self.gedattr[n],''))
            attr.set_value(matches[2])
            state.person.add_attribute(attr)
            self.parse_person_attr(attr,2)
            return
        elif ged2gramps.has_key(n):
            event = RelLib.Event()
            event.set_gramps_id(self.emapper.find_next())
            event.set_type((ged2gramps[n],''))
        else:
            event = RelLib.Event()
            event.set_gramps_id(self.emapper.find_next())
            val = self.gedsource.tag2gramps(n)
            if val:
                event.set_type(RelLib.EventType((RelLib.EventType.CUSTOM,val)))
            else:
                event.set_type(RelLib.EventType((RelLib.EventType.CUSTOM,n)))
                
        self.parse_person_event(event,2)
        if matches[2]:
            event.set_description(matches[2])
        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event.handle)
        state.person.add_event_ref(event_ref)

    #-------------------------------------------------------------------------
    #
    # 
    #
    #-------------------------------------------------------------------------
    def parse_name(self,name,level,state):
        """Parses the person's name information"""

        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = level

        while True:
            matches = self.get_next()
            if int(matches[0]) < level:
                name.set_note(sub_state.get_text())
                self.backup()
                return
            else:
                func = self.name_func.get(matches[1],self.func_name_undefined)
                func(matches,sub_state)

    def func_name_undefined(self,matches,state):
        self.barf(state.level+1)

    def func_name_note(self,matches,state):
        state.add_to_note(self.parse_note(matches,state.name,
                                          state.level+1,state.note))

    def func_name_alia(self,matches,state):
        aka = RelLib.Name()
        try:
            names = nameRegexp.match(matches[2]).groups()
        except:
            names = (matches[2],"","","","")
        if names[0]:
            aka.set_first_name(names[0])
        if names[2]:
            aka.set_surname(names[2])
        if names[4]:
            aka.set_suffix(names[4])
        state.person.add_alternate_name(aka)

    def func_name_npfx(self,matches,state):
        state.name.set_title(matches[2])

    def func_name_givn(self,matches,state):
        state.name.set_first_name(matches[2])

    def func_name_spfx(self,matches,state):
        state.name.set_surname_prefix(matches[2])

    def func_name_surn(self,matches,state):
        state.name.set_surname(matches[2])

    def func_name_marnm(self,matches,state):
        self.parse_marnm(state.person,matches[2].strip())

    def func_name_titl(self,matches,state):
        state.name.set_suffix(matches[2])

    def func_name_nsfx(self,matches,state):
        if state.name.get_suffix() == "":
            state.name.set_suffix(matches[2])

    def func_name_nick(self,matches,state):
        attr = RelLib.Attribute()
        attr.set_type(RelLib.AttributeType.NICKNAME)
        attr.set_value(matches[2])
        state.person.add_attribute(attr)

    def func_name_aka(self,matches,state):
        lname = matches[2].split()
        l = len(lname)
        if l == 1:
            attr = RelLib.Attribute()
            attr.set_type(RelLib.AttributeType.NICKNAME)
            attr.set_value(matches[2])
            state.person.add_attribute(attr)
        else:
            name = RelLib.Name()
            name.set_surname(lname[-1])
            name.set_first_name(' '.join(lname[0:l-1]))
            state.person.add_alternate_name(name)

    def func_name_sour(self,matches,state):
        sref = self.handle_source(matches,state.level+1)
        state.name.add_source_reference(sref)

    def parse_repository(self,repo):
        state = CurrentState()
        state.repo = repo

        while True:
            matches = self.get_next()
            
            if int(matches[0]) < 1:
                self.backup()
                if state.get_text():
                    state.repo.set_note(state.get_text())
                return
            else:
                func = self.repo_func.get(matches[1],self.skip_record)
                func(matches,state)

    def func_repo_name(self,matches,state):
        state.repo.set_name(matches[2])

    def func_repo_addr(self,matches,state):
        addr = RelLib.Address()
        matched = False
        
        match = addr_re.match(matches[2])
        if match:
            groups = match.groups()
            addr.set_street(groups[0].strip())
            addr.set_city(groups[2].strip())
            addr.set_state(groups[3].strip())
            addr.set_postal_code(groups[4].strip())
            addr.set_country(groups[5].strip())
            matched = True
            
        match = addr2_re.match(matches[2])
        if match:
            groups = match.groups()
            addr.set_street(groups[0].strip())
            addr.set_city(groups[2].strip())
            addr.set_state(groups[3].strip())
            addr.set_postal_code(groups[4].strip())
            matched = True

        match = addr3_re.match(matches[2])
        if match:
            groups = match.groups()
            addr.set_street(groups[0].strip())
            addr.set_city(groups[2].strip())
            addr.set_state(groups[3].strip())
            matched = True

        if not matched:
            addr.set_street(matches[2])
        state.repo.add_address(addr)

    def skip_record(self,matches,state):
        self.ignore_sub_junk(2)

    def extract_temple(self, matches):
        def get_code(code):
            if lds.temple_to_abrev.has_key(code):
                return code
            elif lds.temple_codes.has_key(code):
                return lds.temple_codes[code]
        
        c = get_code(matches[2])
        if c: return c
        
        ## Not sure why we do this. Kind of ugly.
        c = get_code(matches[2].split()[0])
        if c: return c

        ## Okay we have no clue which temple this is.
        ## We should tell the user and store it anyway.
        self.warn("Invalid temple code '%s'" % (matches[2],))
        return matches[2]

def person_event_name(event,person):
    if event.get_type().is_custom():
        if not event.get_description():
            text = _event_person_str % {
                'event_name' : str(event.get_type()),
                'person' : NameDisplay.displayer.display(person),
                }
            event.set_description(text)

def load_place_values(place,text):
    items = text.split(',')
    if len(items) != len(_place_field):
        return
    loc = place.get_main_location()
    index = 0
    for item in items:
        _place_field[index](loc,item.strip())
        index += 1
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def create_id():
    return Utils.create_id()


if __name__ == "__main__":
    import sys
    import hotshot#, hotshot.stats
    from GrampsDb import gramps_db_factory, gramps_db_reader_factory

    def callback(val):
        print val

    codeset = None

    db_class = gramps_db_factory(const.app_gramps)
    database = db_class()
    database.load("test.grdb",lambda x: None, mode="w")
    np = NoteParser(sys.argv[1],False)
    g = GedcomParser(database,sys.argv[1],callback, codeset, np.get_map(),np.get_lines(),np.get_persons())

    if False:
        pr = hotshot.Profile('mystats.profile')
        print "Start"
        pr.runcall(g.parse_gedcom_file,False)
        print "Finished"
        pr.close()
##         print "Loading profile"
##         stats = hotshot.stats.load('mystats.profile')
##         print "done"
##         stats.strip_dirs()
##         stats.sort_stats('time','calls')
##         stats.print_stats(100)
    else:
        t = time.time()
        g.parse_gedcom_file(False)
        print time.time() - t
