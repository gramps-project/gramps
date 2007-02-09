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

# $Id: _ReadGedcom.py 8032 2007-02-03 17:11:05Z hippy $

"Import from GEDCOM"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import re
import string
import time
from bsddb import db
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GedcomImport")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Errors
import RelLib
from DateHandler._DateParser import DateParser
import NameDisplay
import Utils
import Mime
import LdsUtils
from ansel_utf8 import ansel_to_utf8

from _GedcomInfo import *
from _GedTokens import *
from QuestionDialog import ErrorDialog, WarningDialog
from GrampsDb._GrampsDbConst  import EVENT_KEY
from BasicUtils import UpdateCallback
from _GedcomLex import Reader

try:
    import Config
    DEFAULT_SOURCE = Config.get(Config.DEFAULT_SOURCE)
except:
    log.warn("No Config module available using defaults.")
    DEFAULT_SOURCE = False
    
#-------------------------------------------------------------------------
#
# Address/Place constants
#
#-------------------------------------------------------------------------
addr_re  = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)\s+(\d+)\s*(.*)')
addr2_re = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)\s+(\d+)')
addr3_re = re.compile('(.+)([\n\r]+)(.+)\s*,(.+)')

_place_field = []
_place_match = {
    'addr'        : RelLib.Location.set_street,
    'subdivision' : RelLib.Location.set_street,
    'addr1'       : RelLib.Location.set_street,
    'adr1'        : RelLib.Location.set_street,
    'city'        : RelLib.Location.set_city,
    'town'        : RelLib.Location.set_city,
    'village'     : RelLib.Location.set_city,
    'county'      : RelLib.Location.set_county,
    'country'     : RelLib.Location.set_country,
    'state'       : RelLib.Location.set_state,
    'region'      : RelLib.Location.set_state,
    'province'    : RelLib.Location.set_state,
    'area code'   : RelLib.Location.set_postal_code,
    }

#-------------------------------------------------------------------------
#
# latin/utf8 conversions
#
#-------------------------------------------------------------------------

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

mime_map = {
    'jpeg' : 'image/jpeg',   'jpg'  : 'image/jpeg',
    'rtf'  : 'text/rtf',     'pdf'  : 'application/pdf',
    'mpeg' : 'video/mpeg',   'mpg'  : 'video/mpeg',
    'gif'  : 'image/gif',    'bmp'  : 'image/x-ms-bmp',
    'tiff' : 'image/tiff',   'aif'  : 'audio/x-aiff',
    'text' : 'text/plain',   'w8bn' : 'application/msword',
    'wav'  : 'audio/x-wav',  'mov'  : 'video/quicktime',
    }
    

_event_family_str = _("%(event_name)s of %(family)s")
_event_person_str = _("%(event_name)s of %(person)s")

_transtable = string.maketrans('','')
_delc = _transtable[0:8] + _transtable[10:31]
_transtable2 = _transtable[0:128] + ('?' * 128)

#-------------------------------------------------------------------------
#
# GEDCOM events to GRAMPS events conversion
#
#-------------------------------------------------------------------------
ged2gramps = {}
for _val in personalConstantEvents.keys():
    _key = personalConstantEvents[_val]
    if _key != "":
        ged2gramps[_key] = _val

ged2fam = {}
for _val in familyConstantEvents.keys():
    _key = familyConstantEvents[_val]
    if _key != "":
        ged2fam[_key] = _val

ged2fam_custom = {}

#-------------------------------------------------------------------------
#
# regular expressions
#
#-------------------------------------------------------------------------
intRE       = re.compile(r"\s*(\d+)\s*$")
nameRegexp  = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
snameRegexp = re.compile(r"/([^/]*)/([^/]*)")
modRegexp   = re.compile(r"\s*(EST|CAL)\s+(.*)$")
calRegexp   = re.compile(r"\s*(ABT|BEF|AFT)?\s*@#D([^@]+)@\s*(.*)$")
rangeRegexp = re.compile(r"\s*BET\s+@#D([^@]+)@\s*(.*)\s+AND\s+@#D([^@]+)@\s*(.*)$")
spanRegexp  = re.compile(r"\s*FROM\s+@#D([^@]+)@\s*(.*)\s+TO\s+@#D([^@]+)@\s*(.*)$")
intRegexp   = re.compile(r"\s*INT\s+([^(]+)\((.*)\)$")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None, use_trans=False):

    try:
        f = open(filename,"r")
    except IOError:
        return

    ansel = False
    gramps = False
    for index in range(50):
        line = f.readline().split()
        if len(line) == 0:
            break
        if len(line) > 2 and line[1][0:4] == 'CHAR' and line.data == "ANSEL":
            ansel = True
        if len(line) > 2 and line[1][0:4] == 'SOUR' and line.data == "GRAMPS":
            gramps = True
    f.close()

    if not gramps and ansel:
        import gtk
        
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
        ro = database.readonly
        database.readonly = False
        close = g.parse_gedcom_file(use_trans)
        database.readonly = ro
    except IOError,msg:
        errmsg = _("%s could not be opened\n") % filename
        ErrorDialog(errmsg,str(msg))
        return
    except db.DBSecondaryBadError, msg:
        WarningDialog(_('Database corruption detected'),
                      _('A problem was detected with the database. Please '
                        'run the Check and Repair Database tool to fix the '
                        'problem.'))
        return
    except Errors.GedcomError, msg:
        ErrorDialog(_('Error reading GEDCOM file'), str(msg))
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
contRE = re.compile(r"\s*\d+\s+CONT\s?(.*)$")
concRE = re.compile(r"\s*\d+\s+CONC\s?(.*)$")
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
        self.level =0

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
#
#
#-------------------------------------------------------------------------
class GedcomParser(UpdateCallback):

    SyntaxError = "Syntax Error"
    BadFile = "Not a GEDCOM file"

    def __init__(self,dbase,filename,callback,codeset,note_map,lines,people):
        UpdateCallback.__init__(self,callback)
        self.set_total(lines)

        self.repo2id = {}
        self.maxpeople = people
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
        self.use_def_src = DEFAULT_SOURCE
        if self.use_def_src:
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
        self.oid2id = {}
        self.sid2id = {}
        self.lid2id = {}
        self.fid2id = {}
        self.rid2id = {}

        self.repo_func = {
            TOKEN_NAME   : self.func_repo_name,
            TOKEN_ADDR   : self.func_repo_addr,
            TOKEN_RIN    : self.func_repo_ignore,
            }

        self.name_func = {
            TOKEN_ALIA   : self.func_name_alia,
            TOKEN_NPFX   : self.func_name_npfx,
            TOKEN_GIVN   : self.func_name_givn,
            TOKEN_SPFX   : self.func_name_spfx,
            TOKEN_SURN   : self.func_name_surn,
            TOKEN__MARNM : self.func_name_marnm,
            TOKEN_NSFX   : self.func_name_nsfx,
            TOKEN_NICK   : self.func_name_nick,
            TOKEN__AKA   : self.func_name_aka,
            TOKEN_SOUR   : self.func_name_sour,
            TOKEN_NOTE   : self.func_name_note,
            }

        self.generic_event_map = {
            TOKEN_TYPE   : self.func_event_type,
            TOKEN__PRIV  : self.func_event_privacy,
            TOKEN_DATE   : self.func_event_date,
            TOKEN_SOUR   : self.func_event_source,
            TOKEN_PLAC   : self.func_event_place,
            TOKEN_ADDR   : self.func_event_addr,
            TOKEN_CAUS   : self.func_event_cause,
            TOKEN_AGNC   : self.func_event_agnc,
            TOKEN_AGE    : self.func_event_age,
            TOKEN_NOTE   : self.func_event_note,
            TOKEN_OFFI   : self.func_event_note,
            TOKEN_PHON   : self.func_event_ignore,
            TOKEN__GODP  : self.func_event_ignore,
            TOKEN__WITN  : self.func_event_ignore,
            TOKEN__WTN   : self.func_event_ignore,
            TOKEN_RELI   : self.func_event_ignore,
            TOKEN_TIME   : self.func_event_ignore,
            TOKEN_ASSO   : self.func_event_ignore,
            TOKEN_IGNORE : self.func_event_ignore,
            TOKEN_STAT   : self.func_event_ignore,
            TOKEN_TEMP   : self.func_event_ignore,
            TOKEN_HUSB   : self.func_event_husb,
            TOKEN_WIFE   : self.func_event_wife,
            TOKEN_OBJE   : self.func_event_object,
            TOKEN_FAMC   : self.func_person_birth_famc,
            }

        self.person_adopt_map = {
            TOKEN_TYPE   : self.func_event_type,
            TOKEN__PRIV  : self.func_event_privacy,
            TOKEN_DATE   : self.func_event_date,
            TOKEN_SOUR   : self.func_event_source,
            TOKEN_PLAC   : self.func_event_place,
            TOKEN_ADDR   : self.func_event_addr,
            TOKEN_CAUS   : self.func_event_cause,
            TOKEN_AGNC   : self.func_event_agnc,
            TOKEN_AGE    : self.func_event_age,
            TOKEN_NOTE   : self.func_event_note,
            TOKEN_OFFI   : self.func_event_note,
            TOKEN__GODP  : self.func_event_ignore,
            TOKEN__WITN  : self.func_event_ignore,
            TOKEN__WTN   : self.func_event_ignore,
            TOKEN_RELI   : self.func_event_ignore,
            TOKEN_TIME   : self.func_event_ignore,
            TOKEN_ASSO   : self.func_event_ignore,
            TOKEN_IGNORE : self.func_event_ignore,
            TOKEN_STAT   : self.func_event_ignore,
            TOKEN_TEMP   : self.func_event_ignore,
            TOKEN_OBJE   : self.func_event_object,
            TOKEN_FAMC   : self.func_person_adopt_famc,
            }

        self.person_func = {
            TOKEN_NAME  : self.func_person_name,
            TOKEN_ALIA  : self.func_person_alt_name,
            TOKEN_OBJE  : self.func_person_object,
            TOKEN_NOTE  : self.func_person_note,
            TOKEN_RNOTE : self.func_person_rnote,
            TOKEN__COMM : self.func_person_note,
            TOKEN_SEX   : self.func_person_sex,
            TOKEN_BAPL  : self.func_person_bapl,
            TOKEN_CONL  : self.func_person_conl,
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
            TOKEN_RESN  : self.func_person_resn,
            TOKEN_AFN   : self.func_person_attr,
            TOKEN_RFN   : self.func_person_attr,
            TOKEN__UID  : self.func_person_attr,
            TOKEN_ASSO  : self.func_person_asso,
            TOKEN_ANCI  : self.skip_record,
            TOKEN_SUBM  : self.skip_record,
            TOKEN_DESI  : self.skip_record,
            TOKEN_RIN   : self.skip_record,
            TOKEN__TODO : self.skip_record,
            TOKEN_CHAN  : self.func_person_chan,
            TOKEN_TITL  : self.func_person_titl,
            TOKEN_GEVENT: self.func_person_std_event,
            TOKEN_ATTR  : self.func_person_std_attr,
            }

        self.person_attr = {
            TOKEN_TYPE  : self.func_person_attr_type,
            TOKEN_CAUS  : self.func_person_attr_ignore,
            TOKEN_DATE  : self.func_person_attr_ignore,
            TOKEN_TIME  : self.func_person_attr_ignore,
            TOKEN_ADDR  : self.func_person_attr_ignore,
            TOKEN_IGNORE: self.func_person_attr_ignore,
            TOKEN_STAT  : self.func_person_attr_ignore,
            TOKEN_TEMP  : self.func_person_attr_ignore,
            TOKEN_OBJE  : self.func_person_attr_ignore,
            TOKEN_SOUR  : self.func_person_attr_source,
            TOKEN_PLAC  : self.func_person_attr_place,
            TOKEN_NOTE  : self.func_person_attr_note,
            }

        self.family_func = {
            TOKEN_HUSB  : self.func_family_husb,
            TOKEN_WIFE  : self.func_family_wife,
            TOKEN_SLGS  : self.func_family_slgs,
            TOKEN_ADDR  : self.func_family_addr,
            TOKEN_CHIL  : self.func_family_chil,
            TOKEN_NCHI  : self.func_family_nchil,
            TOKEN_SOUR  : self.func_family_source,
            TOKEN_RIN   : self.func_family_ignore, 
            TOKEN_SUBM  : self.func_family_ignore,
            TOKEN_REFN  : self.func_family_ignore,
            TOKEN_OBJE  : self.func_family_object,
            TOKEN__COMM : self.func_family_comm,
            TOKEN_NOTE  : self.func_family_note,
            TOKEN_CHAN  : self.func_family_chan,
            TOKEN_GEVENT: self.func_family_std_event,
            }

        self.source_func = {
            TOKEN_TITL  : self.func_source_title,
            TOKEN_TAXT  : self.func_source_taxt_peri,
            TOKEN_PERI  : self.func_source_taxt_peri,
            TOKEN_AUTH  : self.func_source_auth,
            TOKEN_PUBL  : self.func_source_publ,
            TOKEN_NOTE  : self.func_source_note,
            TOKEN_TEXT  : self.func_source_text,
            TOKEN_ABBR  : self.func_source_abbr,
            TOKEN_REFN  : self.func_source_ignore,
            TOKEN_RIN   : self.func_source_ignore,
            TOKEN_REPO  : self.func_source_repo,
            TOKEN_OBJE  : self.func_source_object,
            TOKEN_CHAN  : self.func_source_chan,
            TOKEN_DATA  : self.func_source_ignore,
            TOKEN_IGNORE: self.func_source_ignore,
        }

        self.obje_func = {
            TOKEN_FORM  : self.func_obje_form,
            TOKEN_TITL  : self.func_obje_title,
            TOKEN_FILE  : self.func_obje_file,
            TOKEN_NOTE  : self.func_obje_note,
            TOKEN_BLOB  : self.func_obje_blob,
            TOKEN_REFN  : self.func_obje_refn,
            TOKEN_TYPE  : self.func_obje_type,
            TOKEN_RIN   : self.func_obje_rin,
            TOKEN_CHAN  : self.func_obje_chan,
            }

        self.place_names = {}
        cursor = dbase.get_place_cursor()
        data = cursor.next()
        while data:
            (handle,val) = data
            self.place_names[val[2]] = handle
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
        amap = personalConstantAttributes
        
        self.attrs = amap.values()
        self.gedattr = {}
        for val in amap.keys():
            self.gedattr[amap[val]] = val
        self.search_paths = []

    def errmsg(self,msg):
        log.warning(msg)

    def infomsg(self,msg):
        log.warning(msg)

    def find_file(self,fullname,altpath):
        tries = []
        fullname = fullname.replace('\\',os.path.sep)
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

    def level_is_finished(self, text, level):
        """
        Check to see if the level has been completed, indicated by finding
        a level indiciated by the passed level value. If the level is finished,
        then make sure to call self.backup to reset the text pointer.
        """
        done = text.level < level
        if done:
            self.backup()
        return done

    def parse_name_personal(self, text):
        name = RelLib.Name()

        # parse the substrings into a format of (Given, Surname, Suffix)

        m = snameRegexp.match(text)
        if m:
            names = m.groups()
            name.set_first_name(names[1].strip())
            name.set_surname(names[0].strip())
        else:
            try:
                names = nameRegexp.match(text).groups()
                name.set_first_name(names[0].strip())
                name.set_surname(names[2].strip())
                name.set_suffix(names[4].strip())
            except:
                name.set_first_name(text.strip())

        return name

    def get_next(self):
        if not self.backoff:
            self.groups = self.lexer.readline()
            self.update()
            
            # EOF ?
            if not self.groups:
                self.text = "";
                self.backoff = False
                msg = _("Your GEDCOM file is corrupted. It appears to have been truncated.")
                self.errmsg(msg)
                self.error_count += 1
                self.groups = None
                raise Errors.GedcomError(msg)

        self.backoff = False
        return self.groups
            
    def not_recognized(self, level):
        msg = _("Line %d was not understood, so it was ignored.") % self.groups.line
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
        self.parse_header()
        self.parse_submitter()
        if self.use_def_src:
            self.db.add_source(self.def_src,self.trans)
        self.parse_record()
        self.parse_trailer()
            
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
        try:
            line =self.get_next()
            if line and line.token != TOKEN_TRLR:
                self.not_recognized(0)
        except TypeError:
            pass
        
    def parse_header(self):
        self.parse_header_head()
        self.parse_header_source()

    def parse_submitter(self):
        line = self.get_next()
        if line.data != "SUBM":
            self.backup()
            return
        else:
            self.parse_submitter_data(1)

    def parse_submitter_data(self,level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line,level):
                break
            elif line.token == TOKEN_NAME:
                if self.use_def_src:
                    self.def_src.set_author(line.data)
            elif line.token == TOKEN_ADDR:
                self.ignore_sub_junk(level+1)

    def parse_source(self, name, level):
        """
          n @<XREF:SOUR>@ SOUR {1:1}
          +1 DATA {0:1}
          +2 EVEN <EVENTS_RECORDED> {0:M}
          +3 DATE <DATE_PERIOD> {0:1} 
          +3 PLAC <SOURCE_JURISDICTION_PLACE> {0:1}
          +2 AGNC <RESPONSIBLE_AGENCY> {0:1}
          +2 <<NOTE_STRUCTURE>> {0:M}
          +1 AUTH <SOURCE_ORIGINATOR> {0:1}
          +1 TITL <SOURCE_DESCRIPTIVE_TITLE> {0:1}
          +1 ABBR <SOURCE_FILED_BY_ENTRY> {0:1}
          +1 PUBL <SOURCE_PUBLICATION_FACTS> {0:1}
          +1 TEXT <TEXT_FROM_SOURCE> {0:1}
          +1 <<SOURCE_REPOSITORY_CITATION>> {0:1} 
          +1 <<MULTIMEDIA_LINK>> {0:M} 
          +1 <<NOTE_STRUCTURE>> {0:M}
          +1 REFN <USER_REFERENCE_NUMBER> {0:M}
          +2 TYPE <USER_REFERENCE_TYPE> {0:1}
          +1 RIN <AUTOMATED_RECORD_ID> {0:1}
          +1 <<CHANGE_DATE>> {0:1}
        
        """

        self.source = self.find_or_create_source(name[1:-1])
        self.source.set_title("No title - ID %s" % self.source.get_gramps_id())

        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            else:
                func = self.source_func.get(line.token, self.func_source_undef)
                func(line, self.source, level)

        self.db.commit_source(self.source, self.trans)

    def func_source_undef(self, line, source, level):
        self.not_recognized(level+1)

    def func_source_ignore(self, line, source, level):
        self.ignore_sub_junk(level+1)

    def func_source_repo(self, line, source, level):
        if line.data and line.data[0] == '@':
            gid = line.data.strip()[1:-1]
            repo = self.find_or_create_repository(gid)
        else:
            gid = self.repo2id.get(line.data)
            repo = self.find_or_create_repository(gid)
            self.repo2id[line.data] = repo.get_gramps_id()
            repo.set_name(line.data)
            self.db.commit_repository(repo, self.trans)
        repo_ref = RelLib.RepoRef()
        repo_ref.set_reference_handle(repo.handle)
        self.parse_repo_ref(line,repo_ref,level+1)
        source.add_repo_reference(repo_ref)

    def func_source_abbr(self, line, source, level):
        source.set_abbreviation(line.data)

    def func_source_agnc(self, line, source, level):
        a = RelLib.Attribute()
        a.set_type(RelLib.AttributeType.AGENCY)
        a.set_value(line.data)
        source.add_attribute(a)

    def func_source_text(self, line, source, level):
        source.set_note(line.data)

    def func_source_note(self, line, source, level):
        note = self.parse_note(line, source, level+1, '')
        source.set_note(note)

    def func_source_auth(self, line, source, level):
        source.set_author(line.data)

    def func_source_publ(self, line, source, level):
        source.set_publication_info(line.data)

    def func_source_title(self, line, source, level):
        title = line.data
        title = title.replace('\n',' ')
        source.set_title(title)

    def func_source_taxt_peri(self, line, source, level):
        if source.get_title() == "":
            source.set_title(line.data.replace('\n',' '))

    def func_obje_form(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_file(self, line, media, level):
        (ok, filename) = self.find_file(line.data, self.dir_path)
        if not ok:
            self.warn(_("Could not import %s") % filename[0])
        path = filename[0].replace('\\',os.path.sep)
        media.set_path(path)
        media.set_mime_type(Mime.get_type(path))
        if not media.get_description():
            media.set_description(path)

    def func_obje_ignore(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_title(self, line, media, level):
        media.set_description(line.data)

    def func_obje_note(self, line, media, level):
        note = self.parse_note(line, media, level+1, '')
        media.set_note(note)

    def func_obje_blob(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_refn(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_type(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_rin(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def func_obje_chan(self, line, media, level):
        self.ignore_sub_junk(level+1)

    def parse_record(self):
        while True:
            line = self.get_next()
            key = line.data
            if not line or line.token == TOKEN_TRLR:
		self.backup()
                break
            if key in ("FAM","FAMILY"):
                self.parse_FAM(line)
            elif key in ("INDI","INDIVIDUAL"):
                self.parse_INDI(line)
            elif key in ("OBJE","OBJECT"):
                self.parse_OBJE(line)
            elif key in ("REPO","REPOSITORY"):
                self.parse_REPO(line)
            elif key in ("SUBM", "SUBN", "SUBMITTER"):
                print line
                self.ignore_sub_junk(1)
            elif line.token in (TOKEN_SUBM, TOKEN_SUBN, TOKEN_IGNORE):
                self.ignore_sub_junk(1)
            elif key in ("SOUR","SOURCE"):
                self.parse_source(line.token_text, 1)
            elif line.data.startswith("SOUR ") or line.data.startswith("SOURCE "):
                print line
                # A source formatted in a single line, for example:
                # 0 @S62@ SOUR This is the title of the source
                source = self.find_or_create_source(line[3][1:-1])
                source.set_title( line.data[5:])
                self.db.commit_source(source, self.trans)
            elif key[0:4] == "NOTE":
                self.ignore_sub_junk(1)
            elif key in ("_LOC") :
                print line
                self.ignore_sub_junk(1)
            elif key in ("_EVENT_DEFN") :
                print line
                self.ignore_sub_junk(1)
            else:
                self.not_recognized(1)

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

    def find_object_handle(self,gramps_id):
        intid = self.oid2id.get(gramps_id)
        if not intid:
            intid = create_id()
            self.oid2id[gramps_id] = intid
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
        if not gramps_id:
            need_commit = True
            gramps_id = self.db.find_next_repository_gramps_id()
        else:
            need_commit = False

        intid = self.rid2id.get(gramps_id)
        if self.db.has_repository_handle(intid):
            repository.unserialize(self.db.get_raw_repository_data(intid))
        else:
            intid = self.find_repository_handle(gramps_id)
            repository.set_handle(intid)
            repository.set_gramps_id(gramps_id)
        if need_commit:
            self.db.commit_repository(repository, self.trans)
        return repository

    def find_or_create_object(self, gramps_id):
        obj = RelLib.MediaObject()
        intid = self.oid2id.get(gramps_id)
        if self.db.has_object_handle(intid):
            obj.unserialize(self.db.get_raw_object_data(intid))
        else:
            intid = self.find_object_handle(gramps_id)
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
        return obj

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
        
        intid = self.place_names.get(title)
        if intid == None:
            intid = self.lid2id.get(title)
            if intid == None:
                new_id = self.db.find_next_place_gramps_id()
            else:
                new_id = None
        else:
            new_id = None

        # check to see if the name already existed in the database
        # if it does, create a new name by appending the GRAMPS ID.
        # generate a GRAMPS ID if needed
        
        if self.db.has_place_handle(intid):
            place.unserialize(self.db.get_raw_place_data(intid))
        else:
            intid = create_id()
            place.set_handle(intid)
            place.set_title(title)
            load_place_values(place,title,_place_field)
            place.set_gramps_id(new_id)
            self.db.add_place(place,self.trans)
            self.lid2id[title] = intid
        return place

    def parse_cause(self,event,level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_SOUR:
                event.add_source_reference(self.handle_source(line,level+1))
            else:
                self.not_recognized(1)
                
    def parse_repo_caln(self, line, repo, level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_CALN:
                repo.set_call_number(line.data)
                #self.parse_repo_caln(line, repo. level+1)
            elif line.token == TOKEN_NOTE:
                repo.set_note(line.data)
            else:
                self.not_recognized(1)

    def parse_repo_ref(self, line, repo_ref, level):
        
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_CALN:
                repo_ref.set_call_number(line.data)
                self.parse_repo_ref_caln(repo_ref, level+1)
            elif line.token == TOKEN_NOTE:
                note = self.parse_note(line,repo_ref,level+1,"")
                repo_ref.set_note(note)
            else:
                self.not_recognized(1)

    def parse_repo_ref_caln(self, reporef, level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_MEDI:
                reporef.media_type.set(line.data)
            else:
                self.not_recognized(1)
                
    def parse_note_data(self,level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token in (TOKEN_SOUR, TOKEN_CHAN, TOKEN_REFN,
                                TOKEN_IGNORE):
                self.ignore_sub_junk(level+1)
            elif line.token == TOKEN_RIN:
                pass
            else:
                self.not_recognized(level+1)

    def parse_ftw_relations(self,level):
        mrel = RelLib.ChildRefType()
        frel = RelLib.ChildRefType()

        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            # FTW
            elif line.token == TOKEN__FREL:
                frel = pedi_type.get(line.data.lower(),_TYPE_BIRTH)
            # FTW
            elif line.token == TOKEN__MREL:
                mrel = pedi_type.get(line.data.lower(),_TYPE_BIRTH)
            elif line.token == TOKEN_ADOP:
                mrel = _TYPE_ADOPT
                frel = _TYPE_ADOPT
                # Legacy
            elif line.token == TOKEN__STAT:
                mrel = _TYPE_BIRTH
                frel = _TYPE_BIRTH
                # Legacy _PREF
            elif line.token == TOKEN__PRIMARY:
                pass
            else:
                self.not_recognized(level+1)
        return (mrel,frel)

    def parse_FAM(self, line):
        # create a family
        
        self.fam_count += 1
        self.family = self.find_or_create_family(line.token_text)

        # parse the family

        self.addr = None
        while True:
            line = self.get_next()

            if self.level_is_finished(line, 1):
                break
            if line.token == TOKEN__UID:
                a = RelLib.Attribute()
                a.set_type((RelLib.AttributeType.CUSTOM, line[3]))
                a.set_value(line.data)
                self.family.add_attribute(a)
            else:
		if line.token not in (TOKEN_ENDL, TOKEN_BAPL, TOKEN_CONL):
		    func = self.family_func.get(line.token, self.func_family_event)
		    func(self.family, line, 2)

        # handle addresses attached to families
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

        # add default reference if no reference exists
        if self.use_def_src and len(self.family.get_source_references()) == 0:
            sref = RelLib.SourceRef()
            sref.set_reference_handle(self.def_src.handle)
            self.family.add_source_reference(sref)

        # commit family to database
        if self.family.change:
            self.db.commit_family(self.family, self.trans,
                                  change_time=self.family.change)
        else:
            self.db.commit_family(self.family, self.trans)

        del self.family
    
    def func_family_husb(self, family, line, level):
        gid = line.data.strip()
        handle = self.find_person_handle(self.map_gid(gid[1:-1]))
        self.family.set_father_handle(handle)

    def func_family_wife(self, family, line, level):
        gid = line.data.strip()
        handle = self.find_person_handle(self.map_gid(gid[1:-1]))
        self.family.set_mother_handle(handle)

    def func_family_slgs(self, family, line, level):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.SEAL_TO_SPOUSE)
        self.family.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_family_addr(self, family, line, level):
        self.addr = RelLib.Address()
        self.addr.set_street(line.data)
        self.parse_address(self.addr, level)

    def func_family_chil(self, family, line, level):
        mrel,frel = self.parse_ftw_relations(2)
        gid = line.data.strip()
        child = self.find_or_create_person(self.map_gid(gid[1:-1]))

        reflist = [ ref for ref in self.family.get_child_ref_list() \
                    if ref.ref == child.handle ]
        if reflist:
            ref = reflist[0]
            if mrel != RelLib.ChildRefType.BIRTH or \
               frel != RelLib.ChildRefType.BIRTH:
                ref.set_father_relation(frel)
                ref.set_mother_relation(mrel)
        else:
            ref = RelLib.ChildRef()
            ref.ref = child.handle
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
            family.add_child_ref(ref)

    def func_family_nchil(self, family, line, level):
        a = RelLib.Attribute()
        a.set_type(RelLib.AttributeType.NUM_CHILD)
        a.set_value(line.data)
        self.family.add_attribute(a)

    def func_family_source(self, family, line, level):
        source_ref = self.handle_source(line,2)
        self.family.add_source_reference(source_ref)

    def func_family_ignore(self, family, line, level):
        self.ignore_sub_junk(2)

    def func_family_object(self, family, line, level):
        if line.data and line.data[0] == '@':
            self.not_recognized(level)
        else:
            (form, filename, title, note) = self.parse_obje(level)
            self.build_media_object(self.family, form, filename, title, note)

    def func_event_object(self, line, event_ref, event, level):
        if line.data and line.data[0] == '@':
            self.not_recognized(level)
        else:
            (form, filename, title, note) = self.parse_obje(level)
            self.build_media_object(event, form, filename, title, note)

    def func_place_object(self, line, place, level):
        if line.data and line.data[0] == '@':
            self.not_recognized(level)
        else:
            (form, filename, title, note) = self.parse_obje(level)
            self.build_media_object(place, form, filename, title, note)

    def func_source_object(self, line, source, level):
        if line.data and line.data[0] == '@':
            self.not_recognized(level)
        else:
            (form, filename, title, note) = self.parse_obje(level+1)
            self.build_media_object(source, form, filename, title, note)

    def parse_obje(self, level):
        """
          n  OBJE {1:1}
          +1 FORM <MULTIMEDIA_FORMAT> {1:1}
          +1 TITL <DESCRIPTIVE_TITLE> {0:1}
          +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
          +1 <<NOTE_STRUCTURE>> {0:M} 
        """
        form = ""
        filename = ""
        title = ""
        note = ""
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_FORM:
                form = line.data
            elif line.token == TOKEN_TITL:
                title = line.data
            elif line.token == TOKEN_FILE:
                filename = line.data
            elif line.token == TOKEN_NOTE:
                note = line.data
            elif line.token == TOKEN_IGNORE:
                self.ignore_sub_junk(level+1)
            else:
                self.not_recognized(level+1)
                
        return (form, filename, title, note)

    def func_family_comm(self, family, line, level):
        note = line.data
        self.family.set_note(note)
        self.ignore_sub_junk(2)

    def func_family_note(self, family, line, level):
        self.parse_note(line, self.family, 1, '')

    def func_family_std_event(self, family, line, level):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(line.data)

        event_ref = RelLib.EventRef()
        self.parse_event(event_ref, event, self.generic_event_map, level)
        self.db.add_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)
        event_ref.set_role(RelLib.EventRoleType.FAMILY)
        self.family.add_event_ref(event_ref)

    def func_family_event(self, family, line, level):
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        try:
            event.set_type(RelLib.EventType(ged2fam[line[3]]))
        except:
            if ged2fam_custom.has_key(line[3]):
                event.set_type((RelLib.EventType.CUSTOM,
                                ged2fam_custom[line[3]]))
            elif line[3]:
                event.set_type((RelLib.EventType.CUSTOM,
                                line[3]))
            else:
                event.set_type(RelLib.EventType.UNKNOWN)

        if line.data and not event.get_description() and \
               line.data != 'Y':
            event.set_description(line.data)
                
        event_ref = RelLib.EventRef()

        self.parse_event(event_ref, event, self.generic_event_map, 2)

        if int(event.get_type()) == RelLib.EventType.MARRIAGE:

            descr = event.get_description()
            if descr == "Civil Union":
                self.family.type.set(RelLib.FamilyRelType.CIVIL_UNION)
                event.set_description('')
            elif descr == "Unmarried":
                self.family.type.set(RelLib.FamilyRelType.UNMARRIED)
                event.set_description('')
            else:
                self.family.type.set(RelLib.FamilyRelType.MARRIED)

        if int(event.get_type()) != RelLib.EventType.CUSTOM:
            if not event.get_description():
                text = _event_family_str % {
                    'event_name' : str(event.get_type()),
                    'family' : Utils.family_name(self.family,self.db),
                    }
                event.set_description(text)

        self.db.add_event(event,self.trans)

        event_ref.set_reference_handle(event.handle)
        event_ref.set_role(RelLib.EventRoleType.FAMILY)
        self.family.add_event_ref(event_ref)
        del event

    def parse_note_base(self,line,obj,level,old_note,task):
        # reference to a named note defined elsewhere
        if line.token == TOKEN_RNOTE:
            note_obj = self.note_map.get(line.data)
            if note_obj:
                new_note = note_obj.get()
            else:
                new_note = u""
        else:
            new_note = line.data
            self.ignore_sub_junk(level+1)
        if old_note:
            note = u"%s\n%s" % (old_note,line.data)
        else:
            note = new_note
        task(note)
        return note

    def parse_note_simple(self, line, level):
        # reference to a named note defined elsewhere
        if line.data and line.data[0] == "@":
            note_obj = self.note_map.get(line.data)
	    note = note_obj.get()
        else:
            note = line.data
            self.ignore_sub_junk(level+1)
        return note
        
    def parse_note(self,line,obj,level,old_note):
        return self.parse_note_base(line,obj,level,old_note,obj.set_note)

    def parse_comment(self,line,obj,level,old_note):
        return self.parse_note_base(line,obj,level,old_note,obj.set_note)

    def extract_gramps_id(self, value):
        """
        Extracts a value to use for the GRAMPS ID value from the GEDCOM
        reference token. The value should be in the form of @XXX@, and the
        returned value will be XXX
        """
        return value[1:-1]

    def parse_OBJE(self, line):
        """
           n  @XREF:OBJE@ OBJE {1:1}
           +1 FORM <MULTIMEDIA_FORMAT> {1:1} p.*
           +1 TITL <DESCRIPTIVE_TITLE> {0:1} p.*
           +1 <<NOTE_STRUCTURE>> {0:M} p.*
           +1 BLOB {1:1}
           +2 CONT <ENCODED_MULTIMEDIA_LINE> {1:M} p.*
           +1 OBJE @<XREF:OBJE>@ /* chain to continued object */ {0:1} p.*
           +1 REFN <USER_REFERENCE_NUMBER> {0:M} p.*
           +2 TYPE <USER_REFERENCE_TYPE> {0:1} p.*
           +1 RIN <AUTOMATED_RECORD_ID> {0:1} p.*
           +1 <<CHANGE_DATE>> {0:1} p.*
        """
        gid = self.extract_gramps_id(line.data.strip())
        self.media = self.find_or_create_object(self.map_gid(gid[1:-1]))

        while True:
            line =self.get_next()
            
            if self.level_is_finished(line, 1):
                break
            else:
                func = self.obje_func.get(line.token, self.func_obje_ignore)
                func(line, self.media, 1)

        # Add the default reference if no source has found
        
        if self.use_def_src and len(self.media.get_source_references()) == 0:
            sref = RelLib.SourceRef()
            sref.set_reference_handle(self.def_src.handle)
            self.media.add_source_reference(sref)

        # commit the person to the database
        if self.media.change:
            self.db.commit_media_object(self.media, self.trans,
                                        change_time=self.media.change)
        else:
            self.db.commit_media_object(self.media, self.trans)
        del self.media

    #----------------------------------------------------------------------
    #
    # REPO parsing
    #
    #----------------------------------------------------------------------
    def parse_REPO(self, line):
        self.repo_count += 1
        self.repo = self.find_or_create_repository(line.token_text)
        self.added.add(self.repo.handle)
        self.parse_repository(self.repo)
        self.db.commit_repository(self.repo, self.trans)
        del self.repo

    #----------------------------------------------------------------------
    #
    # INDI parsing
    #
    #----------------------------------------------------------------------
    def parse_INDI(self, line):
        """
        Handling of the GEDCOM INDI tag.

        n  @XREF:INDI@ INDI {1:1}
        +1 RESN <RESTRICTION_NOTICE> {0:1}
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
        +1 <<MULTIMEDIA_LINK>> {0:M}
        +1 <<NOTE_STRUCTURE>> {0:M} 
        +1 RFN <PERMANENT_RECORD_FILE_NUMBER> {0:1}
        +1 AFN <ANCESTRAL_FILE_NUMBER> {0:1}
        +1 REFN <USER_REFERENCE_NUMBER> {0:M}
        +2 TYPE <USER_REFERENCE_TYPE> {0:1}
        +1 RIN <AUTOMATED_RECORD_ID> {0:1}
        +1 <<CHANGE_DATE>> {0:1}
        """

        # find the person
        self.indi_count += 1
        gid = line.token_text.strip()
        self.person = self.find_or_create_person(self.map_gid(gid))
        self.added.add(self.person.handle)

        # do the actual parsing

        state = CurrentState()
        state.person = self.person
        state.level = 1

        while True:
            line = self.get_next()
            if self.level_is_finished(line, 1):
                if state.get_text():
                    state.person.set_note(state.get_text())
                break
            else:
                func = self.person_func.get(line.token, self.func_person_event)
                func(line, state)

        # Add the default reference if no source has found
        if self.use_def_src and len(self.person.get_source_references()) == 0:
            sref = RelLib.SourceRef()
            sref.set_reference_handle(self.def_src.handle)
            self.person.add_source_reference(sref)

        # commit the person to the database
        if self.person.change:
            self.db.commit_person(self.person, self.trans,
                                  change_time=state.person.change)
        else:
            self.db.commit_person(self.person, self.trans)
        del self.person

    def parse_optional_note(self,level):
        note = ""
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                return note
            elif line.token == TOKEN_NOTE:
                if not line.data.strip() or line.data and line.data[0] != "@":
                    note = line.data
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
                self.not_recognized(level+1)
        return None
        
    def parse_famc_type(self,level,person):
        ftype = _TYPE_BIRTH
        note = ""
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_PEDI:
                ftype = pedi_type.get(line.data.lower(),RelLib.ChildRefType.UNKNOWN)
            elif line.token == TOKEN_SOUR:
                source_ref = self.handle_source(line,level+1)
                person.primary_name.add_source_reference(source_ref)
            elif line.token == TOKEN__PRIMARY:
                pass #type = line.token
            elif line.token == TOKEN_NOTE:
                if not line.data.strip() or line.data and line.data[0] != "@":
                    note = line.data
                    self.parse_note_data(level+1)
                else:
                    self.ignore_sub_junk(level+1)
            else:
                self.not_recognized(level+1)
        return (ftype,note)

    def parse_address(self,address,level):
        first = 0
        note = ""
        while True:
            line =self.get_next()
            if line.level < level:
                if line.token == TOKEN_PHON:
                    address.set_phone(line.data)
                else:
                    self.backup()
                break
            elif line.token in (TOKEN_ADDR, TOKEN_ADR1, TOKEN_ADR2):
                val = address.get_street()
                if first == 0:
                    val = line.data
                    first = 1
                else:
                    val = "%s,%s" % (val,line.data)
                address.set_street(val)
            elif line.token == TOKEN_DATE:
                address.set_date_object(self.extract_date(line.data))
            elif line.token == TOKEN_CITY:
                address.set_city(line.data)
            elif line.token == TOKEN_STAE:
                address.set_state(line.data)
            elif line.token == TOKEN_POST:
                address.set_postal_code(line.data)
            elif line.token == TOKEN_CTRY:
                address.set_country(line.data)
            elif line.token == TOKEN_PHON:
                address.set_phone(line.data)
            elif line.token == TOKEN_SOUR:
                address.add_source_reference(self.handle_source(line,level+1))
            elif line.token == TOKEN_NOTE:
                note = self.parse_note(line,address,level+1,'')
            elif line.token in (TOKEN__LOC, TOKEN__NAME):
                pass    # ignore unsupported extended location syntax
            elif line.token in (TOKEN_IGNORE, TOKEN_TYPE, TOKEN_CAUS):
                self.ignore_sub_junk(level+1)
            else:
                self.not_recognized(level+1)

    def parse_place_as_address(self, street, level):
        note = None

        location = RelLib.Location()
        if street:
            location.set_street(street)
            added = True
        else:
            added = False
            
        while True:
            line =self.get_next()
            if self.level_is_finished(line,level):
                break
            elif line.token in (TOKEN_ADDR, TOKEN_ADR1, TOKEN_ADR2):
                val = location.get_street()
                if val:
                    val = "%s, %s" % (val, line.data.strip())
                else:
                    val = line.data.strip()
                location.set_street(val.replace('\n',' '))
                added = True
            elif line.token == TOKEN_DATE:
                location.set_date_object(self.extract_date(line.data))
                added = True
            elif line.token == TOKEN_CITY:
                location.set_city(line.data)
                added = True
            elif line.token == TOKEN_STAE:
                location.set_state(line.data)
                added = True
            elif line.token == TOKEN_POST:
                location.set_postal_code(line.data)
                added = True
            elif line.token == TOKEN_CTRY:
                location.set_country(line.data)
                added = True
            elif line.token == TOKEN_NOTE:
                note = self.parse_note_simple(line, level+1)
                added = True
            elif line.token in (TOKEN__LOC, TOKEN__NAME, TOKEN_PHON):
                pass    # ignore unsupported extended location syntax
            else:
                self.not_recognized(level+1)
        if added:
            return (location, note)
        else:
            return (None, None)

    def parse_ord(self,lds_ord,level):
        note = ""
        pf = _place_field
        place = None

        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                if place:
                    load_place_values(place,place.get_title(),pf)
                break
            elif line.token == TOKEN_TEMP:
                value = self.extract_temple(line)
                if value:
                    lds_ord.set_temple(value)
            elif line.token == TOKEN_DATE:
                lds_ord.set_date_object(self.extract_date(line.data))
            elif line.token == TOKEN_FAMC:
                gid = line.data.strip()[1:-1]
                lds_ord.set_family_handle(self.find_family_handle(gid))
            elif line.token == TOKEN_FORM:
                pf = self.parse_place_form_line(line)
            elif line.token == TOKEN_PLAC:
              try:
                place = self.find_or_create_place(line.data)
                place.set_title(line.data)
                place_handle = place.handle
                lds_ord.set_place_handle(place_handle)
                self.ignore_sub_junk(level+1)
              except NameError:
                  pass
            elif line.token == TOKEN_SOUR:
                lds_ord.add_source_reference(
                    self.handle_source(line,level+1))
            elif line.token == TOKEN_NOTE:
                note = self.parse_note(line,lds_ord,level+1,'')
            elif line.token == TOKEN_STAT:
                lds_ord.set_status(
                    lds_status.get(line.data,RelLib.LdsOrd.STATUS_NONE))
            else:
                self.not_recognized(level+1)

    def parse_event(self, event_ref, event, func_map, level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line,level):
                break
            else:
                func = func_map.get(line.token, self.func_event_undef)
                func(line, event_ref, event, level+1) 

    def func_event_ignore(self, line, event_ref, event, level):
        self.ignore_sub_junk(level)

    def func_event_undef(self, line, event_ref, event, level):
        self.not_recognized(level)

    def func_event_type(self, line, event_ref, event, level):
        if event.get_type().is_custom():
            if ged2gramps.has_key(line.data):
                name = RelLib.EventType(ged2gramps[line.data])
            else:
                val = self.gedsource.tag2gramps(line.data)
                if val:
                    name = RelLib.EventType((RelLib.EventType.CUSTOM,val))
                else:
                    name = RelLib.EventType((RelLib.EventType.CUSTOM,line[3]))
            event.set_type(name)
        else:
            try:
                if not ged2gramps.has_key(line.data) and \
                       not ged2fam.has_key(line.data) and \
                       line.data[0] != 'Y':
                    event.set_description(line.data)
            except IndexError:
                pass
                
    def func_event_privacy(self, line, event_ref, event, level):
        event.set_privacy(True)

    def func_person_adopt_famc(self, line, event_ref, event, level):
        gid = line.data.strip()[1:-1]
        handle = self.find_family_handle(gid)
        family = self.find_or_create_family(gid)

        mrel,frel = self.parse_adopt_famc(level);

        if self.person.get_main_parents_family_handle() == handle:
            self.person.set_main_parent_family_handle(None)
        self.person.add_parent_family_handle(handle)
        
        reflist = [ ref for ref in family.get_child_ref_list() \
                        if ref.ref == self.person.handle ]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
        else:
            ref = RelLib.ChildRef()
            ref.ref = self.person.handle
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
            family.add_child_ref(ref)
            self.db.commit_family(family, self.trans)

    def func_person_birth_famc(self, line, event_ref, event, level):
        handle = self.find_family_handle(line.data.strip()[1:-1])

        if self.person.get_main_parents_family_handle() == handle:
            self.person.set_main_parent_family_handle(None)
        self.person.add_parent_family_handle(handle)
        
        frel = mrel = RelLib.ChildRefType.BIRTH

        family = self.db.find_family_from_handle(handle, self.trans)
        reflist = [ ref for ref in family.get_child_ref_list() \
                        if ref.ref == self.person.handle ]
        if reflist:
            ref = reflist[0]
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
        else:
            ref = RelLib.ChildRef()
            ref.ref = self.person.handle
            ref.set_father_relation(frel)
            ref.set_mother_relation(mrel)
            family.add_child_ref(ref)
            self.db.commit_family(family, self.trans)

    def func_event_note(self, line, event_ref, event, level):
        self.parse_note(line,event,level+1,'')
        
    def func_event_date(self, line, event_ref, event, level):
        event.set_date_object(line.data)
        
    def func_event_source(self, line, event_ref, event, level):
        event.add_source_reference(self.handle_source(line,level))

    def func_event_addr(self, line, event_ref, event, level):
        (location, note) = self.parse_place_as_address(line.data, level)
        if location:
            index = line.data + location.get_street()
        else:
            index = line.data

        place_handle = event.get_place_handle()
        if place_handle:
            place = self.db.get_place_from_handle(place_handle)
            main_loc = place.get_main_location()
            if main_loc and main_loc.get_street() != location.get_street():
                old_title = place.get_title()
                place = self.find_or_create_place(index)
                place.set_title(old_title)
                place_handle = place.handle
        else:
            place = self.find_or_create_place(index)
            place.set_title(line.data)
            place_handle = place.handle
                
        load_place_values(place,line.data)
        if location:
            place.set_main_location(location)
        if note:
            place.set_note(note)

        event.set_place_handle(place_handle)
        self.db.commit_place(place, self.trans)

    def func_event_place(self, line, event_ref, event, level):
        """
         n  PLAC <PLACE_VALUE> {1:1}
         +1 FORM <PLACE_HIERARCHY> {0:1}
         +1 <<SOURCE_CITATION>> {0:M}
         +1 <<NOTE_STRUCTURE>> {0:M}
        """

        val = line.data
        n = event.get_type()
        if self.is_ftw and int(n) in [RelLib.EventType.OCCUPATION,
                                      RelLib.EventType.DEGREE]:
            event.set_description(val)
        else:
            place = self.find_or_create_place(val)
            place_handle = place.handle
            place.set_title(val)
            event.set_place_handle(place_handle)
            pf = _place_field

            while True:
                line = self.get_next()
                if self.level_is_finished(line, level):
                    load_place_values(place,place.get_title(),pf)
                    break
                elif line.token == TOKEN_NOTE:
                    note = self.parse_note(line, place, level+1, '')
                    place.set_note(note)
                elif line.token == TOKEN_FORM:
                    pf = self.parse_place_form_line(line)
                elif line.token == TOKEN_OBJE:
                    self.func_place_object(line, place, level+1)
                elif line.token == TOKEN_SOUR:
                    place.add_source_reference(
                        self.handle_source(line, level+1))
            self.db.commit_place(place, self.trans)

    def func_event_cause(self, line, event_ref, event, level):
        a = RelLib.Attribute()
        a.set_type(RelLib.AttributeType.CAUSE)
        a.set_value(line.data)
        event.add_attribute(a)
        self.parse_cause(a,level+1)

    def func_event_age(self, line, event_ref, event, level):
        a = RelLib.Attribute()
        a.set_type(RelLib.AttributeType.AGE)
        a.set_value(line.data)
        event_ref.add_attribute(a)

    def func_event_husb(self, line, event_ref, event, level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_AGE:
                a = RelLib.Attribute()
                a.set_type(RelLib.AttributeType.FATHER_AGE)
                a.set_value(line.data)
                event_ref.add_attribute(a)

    def func_event_wife(self, line, event_ref, event, level):
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_AGE:
                a = RelLib.Attribute()
                a.set_type(RelLib.AttributeType.MOTHER_AGE)
                a.set_value(line.data)
                event_ref.add_attribute(a)

    def func_event_agnc(self, line, event_ref, event, level):
        a = RelLib.Attribute()
        a.set_type(RelLib.AttributeType.AGENCY)
        a.set_value(line.data)
        event.add_attribute(a)

    def parse_adopt_famc(self,level):
        mrel = _TYPE_BIRTH
        frel = _TYPE_BIRTH
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_ADOP:
                if line.data == "HUSB":
                    frel = _TYPE_ADOPT
                elif line.data == "WIFE":
                    mrel = _TYPE_ADOPT
            else:
                self.not_recognized(level+1)
        return (mrel,frel)
    
    def parse_person_attr(self,attr,level):
        """
        GRAMPS uses an Attribute to store some information. Technically,
        GEDCOM does not make a distinction between Attributes and Events,
        so what GRAMPS considers to be an Attribute can have more information
        than what we allow. 
        """
        while True:
            line =self.get_next()
            if self.level_is_finished(line,level):
                break
            else:
                func = self.person_attr.get(line.token,
                                            self.func_person_attr_undef)
                func(attr, line, level+1) 

    def func_person_attr_undef(self, attr, line, level):
        """
        Called when an undefined token is found
        """
        self.not_recognized(level)

    def func_person_attr_ignore(self, attr, line, level):
        """
        Called when an attribute is found that we know we want to ignore
        """
        self.ignore_sub_junk(level)

    def func_person_attr_type(self, attr, line, level):
        if attr.get_type() == "":
            if ged2gramps.has_key(line.data):
                name = ged2gramps[line.data]
            else:
                val = self.gedsource.tag2gramps(line.data)
                if val:
                    name = val
                else:
                    name = line.data
            attr.set_type(name)

    def func_person_attr_source(self, attr, line, level):
        attr.add_source_reference(self.handle_source(line,level))

    def func_person_attr_place(self, attr, line, level):
        val = line.data
        if attr.get_value() == "":
            attr.set_value(val)
        self.ignore_sub_junk(level)

    def func_person_attr_note(self, attr, line, level):
        info = self.parse_note(line, attr, level+1, '')
        attr.set_note(info)

    def parse_source_reference(self, source, level, handle):
        """Reads the data associated with a SOUR reference"""
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_PAGE:
                source.set_page(line.data)
            elif line.token == TOKEN_DATE:
                source.set_date_object(self.extract_date(line.data))
            elif line.token == TOKEN_DATA:
                date,text = self.parse_source_data(level+1)
                if date:
                    d = self.dp.parse(date)
                    source.set_date_object(d)
                source.set_text(text)
            elif line.token == TOKEN_OBJE:
                if line.data and line.data[0] == '@':
                    self.not_recognized(level)
                else:
                    src = self.db.get_source_from_handle(handle)
                    (form, filename, title, note) = self.parse_obje(level)
                    self.build_media_object(src, form, filename,
                                            title, note)
                    self.db.commit_source(src, self.trans)
            elif line.token in (TOKEN_REFN, TOKEN_EVEN,
                                TOKEN_IGNORE, TOKEN__LKD):
                self.ignore_sub_junk(level+1)
            elif line.token == TOKEN_QUAY:
                try:
                    val = int(line.data)
                except ValueError:
                    return
                # If value is greater than 3, cap at 3
                val = min(val,3)
                if val > 1:
                    source.set_confidence_level(val+1)
                else:
                    source.set_confidence_level(val)
            elif line.token == TOKEN_NOTE:
                note = self.parse_comment(line,source,level+1,'')
                source.set_note(note)
            elif line.token == TOKEN_TEXT:
                note = self.parse_comment(line,source,level+1,'')
                source.set_text(note)
            else:
                self.not_recognized(level+1)
        
    def parse_source_data(self,level):
        """Parses the source data"""
        date = ""
        note = ""
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_DATE:
                date = line.data
            elif line.token == TOKEN_TEXT:
                note = line.data
            else:
                self.not_recognized(level+1)
        return (date,note)
    
    def parse_marnm(self,person,text):
        data = text.split()
        if len(data) == 1:
            name = RelLib.Name(person.primary_name)
            name.set_surname(data[0].strip())
            name.set_type(RelLib.NameType.MARRIED)
            person.add_alternate_name(name)
        elif len(data) > 1:
            name = RelLib.Name()
            name.set_surname(data[-1].strip())
            name.set_first_name(' '.join(data[0:-1]))
            name.set_type(RelLib.NameType.MARRIED)
            person.add_alternate_name(name)

    def parse_header_head(self):
        """validiates that this is a valid GEDCOM file"""
        line = self.lexer.readline()
        if line.token != TOKEN_HEAD:
            raise Errors.GedcomError("%s is not a GEDCOM file" % self.filename)

    def parse_header_source(self):
        genby = ""
        note = ""
        while True:
            line = self.get_next()
            if self.level_is_finished(line, 1):
                return
            elif line.token == TOKEN_SOUR:
                self.gedsource = self.gedmap.get_from_source_tag(line.data)
                self.lexer.set_broken_conc(self.gedsource.get_conc())
                if line.data == "FTW":
                    self.is_ftw = 1
                genby = line.data
            elif line.token == TOKEN_NAME:
                pass
            elif line.token == TOKEN_VERS:
                if self.use_def_src:
                    self.def_src.set_data_item('Generated by',"%s %s" %
                                               (genby,line.data))
            elif line.token == TOKEN_FILE:
                if self.use_def_src:
                    filename = os.path.basename(line.data).split('\\')[-1]
                    self.def_src.set_title(_("Import from %s") % filename)
            elif line.token == TOKEN_COPR:
                if self.use_def_src:
                    self.def_src.set_publication_info(line.data)
            elif line.token ==  TOKEN_SUBM:
                self.parse_subm(2)
            elif line.token in (TOKEN_CORP, TOKEN_DATA, TOKEN_SUBN,
                                TOKEN_LANG, TOKEN_TIME):
                self.ignore_sub_junk(2)
            elif line.token == TOKEN_DEST:
                if genby == "GRAMPS":
                    self.gedsource = self.gedmap.get_from_source_tag(line.data)
                    self.lexer.set_broken_conc(self.gedsource.get_conc())
            elif line.token == TOKEN_CHAR and not self.override:
                if line.data == "ANSEL":
                    self.lexer.set_charset_fn(ansel_to_utf8)
                elif line.data not in ("UNICODE","UTF-8","UTF8"):
                    self.lexer.set_charset_fn(latin_to_utf8)
                self.ignore_sub_junk(2)
            elif line.token == TOKEN_GEDC:
                self.ignore_sub_junk(2)
            elif line.token == TOKEN__SCHEMA:
                self.parse_ftw_schema(2)
            elif line.token == TOKEN_PLAC:
                self.parse_place_form(2)
            elif line.token == TOKEN_DATE:
                date = self.parse_date(2)
                date.date = line.data
                if self.use_def_src:
                    self.def_src.set_data_item('Creation date',line.data)
            elif line.token == TOKEN_NOTE:
                if self.use_def_src:
                    note = self.parse_note(line,self.def_src,2,'')
            elif line.token == TOKEN_UNKNOWN:
                self.ignore_sub_junk(2)
            else:
                self.not_recognized(2)

    def parse_subm(self, level):
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_NAME:
                if self.use_def_src:
                    self.def_src.set_author(line.data)
            else:
                self.ignore_sub_junk(2)

    def parse_ftw_schema(self,level):
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_INDI:
                self.parse_ftw_indi_schema(level+1)
            elif line.token == TOKEN_FAM:
                self.parse_ftw_fam_schema(level+1)
            else:
                self.not_recognized(2)

    def parse_ftw_indi_schema(self,level):
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            else:
                ged2gramps[line.token] = self.parse_label(level+1)

    def parse_label(self,level):
        value = None
        
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_LABL:
                value = line.data
            else:
                self.not_recognized(2)
        return value
    
    def parse_ftw_fam_schema(self,level):
        while True:
            line = self.get_next()

            if self.level_is_finished(line, level):
                break
            else:
                ged2fam_custom[line.token_text] = self.parse_label(level+1)
    
    def ignore_sub_junk(self, level):
        while True:
            line = self.get_next()
            if self.level_is_finished(line, level):
                break
    
    def ignore_change_data(self,level):
        line =self.get_next()
        if line.token == TOKEN_CHAN:
            self.ignore_sub_junk(level+1)
        else:
            self.backup()

    def parse_place_form(self, level):
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_FORM:
                global _place_field
                _place_field = self.parse_place_form_line(line)
            else:
                self.not_recognized(level+1)

    def parse_place_form_line(self, line):
        pf = []
        for item in line.data.split(','):
            item = item.lower().strip()
            fcn = _place_match.get(item,_empty_func)
            pf.append(fcn)
        return pf
    
    def parse_date(self,level):
        date = DateStruct()
        while True:
            line =self.get_next()

            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_TIME:
                date.time = line.data
            else:
                self.not_recognized(level+1)
        return date

    def extract_date(self,text):
        dateobj = RelLib.Date()
        try:
            match = intRegexp.match(text)
            if match:
                int_val = True
                text, comment = match.groups()
            else:
                int_val = False
            
            match = modRegexp.match(text)
            if match:
                (mod, text) = match.groups()
                if mod == "CAL":
                    dateobj.set_quality(RelLib.Date.QUAL_CALCULATED)
                elif mod == "EST":
                    dateobj.set_quality(RelLib.Date.QUAL_ESTIMATED)

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
                if int_val:
                    dateobj.set_text_value(comment)
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
                if int_val:
                    dateobj.set_text_value(comment)
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
                if int_val:
                    dateobj.set_text_value(comment)
                return dval
        except IOError:
            return self.dp.set_text(text)

    def handle_source(self,line,level):
        source_ref = RelLib.SourceRef()
        if line.data and line.data[0] != "@":
            title = line.data
            note = ''
            handle = self.inline_srcs.get((title,note),Utils.create_id())
            self.inline_srcs[(title,note)] = handle
            self.parse_source_reference(source_ref, level, handle)
        else:
            handle = self.find_or_create_source(line.data[1:-1]).handle
            self.parse_source_reference(source_ref,level, handle)
        source_ref.set_reference_handle(handle)
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
    def func_person_name(self, line, state):
        """
        Parsers the NAME token in a GEDCOM file. The text is in the format
        of (according to the GEDCOM Spec):
        >   <TEXT>|/<TEXT>/|<TEXT>/<TEXT>/|/<TEXT>/<TEXT>|<TEXT>/<TEXT>/<TEXT>
        We have encountered some variations that use:
        >   <TEXT>/

        The basic Name structure is:

        >   n  NAME <NAME_PERSONAL> {1:1}
        >   +1 NPFX <NAME_PIECE_PREFIX> {0:1}
        >   +1 GIVN <NAME_PIECE_GIVEN> {0:1}
        >   +1 NICK <NAME_PIECE_NICKNAME> {0:1}
        >   +1 SPFX <NAME_PIECE_SURNAME_PREFIX {0:1}
        >   +1 SURN <NAME_PIECE_SURNAME> {0:1}
        >   +1 NSFX <NAME_PIECE_SUFFIX> {0:1}
        >   +1 <<SOURCE_CITATION>> {0:M}
        >   +1 <<NOTE_STRUCTURE>> {0:M}
        """

        # build a RelLib.Name structure from the text
        
        name = self.parse_name_personal(line.data)

        # Add the name as the primary name if this is the first one that
        # we have encountered for this person. Assume that if this is the
        # first name, that it is a birth name. Otherwise, label it as an
        # "Also Known As (AKA)". GEDCOM does not seem to have the concept
        # of different name types
        
        if state.name_cnt == 0:
            name.set_type(RelLib.NameType.BIRTH)
            state.person.set_primary_name(name)
        else:
            name.set_type(RelLib.NameType.AKA)
            state.person.add_alternate_name(name)
        state.name_cnt += 1

        #
        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = 2

        while True:
            line =self.get_next()
            if self.level_is_finished(line,2):
                name.set_note(sub_state.get_text())
                break
            else:
                func = self.name_func.get(line.token, self.func_name_undefined)
                func(line, sub_state)

    def func_person_chan(self, line, state):
        self.parse_change(line, state.person, state.level+1)

    def func_family_chan(self, family, line, level):
        self.parse_change(line, family, level)

    def func_source_chan(self, line, source, level):
        self.parse_change(line, source, level+1)
        
    def parse_change(self, line, obj, level):
        """
        CHANGE_DATE:=

        >  n CHAN {1:1}
        >  +1 DATE <CHANGE_DATE> {1:1}
        >  +2 TIME <TIME_VALUE> {0:1}
        >  +1 <<NOTE_STRUCTURE>> {0:M}

        The Note structure is ignored, since we have nothing
        corresponding in GRAMPS.

        Based on the values calculated, attempt to convert to a valid
        change time using time.strptime. If this fails (and it shouldn't
        unless the value is meaningless and doesn't conform to the GEDCOM
        spec), the value is ignored.
        """
        tstr = None
        dstr = None
        
        while True:
            line =self.get_next()
            if self.level_is_finished(line, level):
                break
            elif line.token == TOKEN_TIME:
                tstr = line.data
            elif line.token == TOKEN_DATE:
                dstr = line.data
            elif line.token == TOKEN_NOTE:
                self.ignore_sub_junk(level+1)
            else:
                self.not_recognized(level+1)

        # Attempt to convert the values to a valid change time
        if tstr:
            try:
                if dstr:
                    tstruct = time.strptime("%s %s" % (dstr, tstr),
                                            "%d %b %Y %H:%M:%S")
                else:
                    tstruct = time.strptime(tstr, "%d %b %Y")
                val = time.mktime(tstruct)
                obj.change = val
            except ValueError:
                # parse of time structure failed, so ignore
                pass
        

    def func_person_asso(self, line, state):
        """
        Parse the ASSO tag, add the the referenced person to the person we
        are currently parsing. The GEDCOM spec indicates that valid ASSOC tag
        is:
        
        >   n ASSO @<XREF:INDI>@ {0:M}
           
        And the the sub tags are:
        
        >   ASSOCIATION_STRUCTURE:=
        >     +1 TYPE <RECORD_TYPE> {1:1}
        >     +1 RELA <RELATION_IS_DESCRIPTOR> {1:1}
        >     +1 <<NOTE_STRUCTURE>> {0:M}
        >     +1 <<SOURCE_CITATION>> {0:M}

        GRAMPS only supports ASSO records to people, so if the TYPE is
        something other than INDI, the record is ignored.
        """

        # find the id and person that we are referencing
        gid = self.extract_gramps_id(line.data.strip())
        handle = self.find_person_handle(self.map_gid(gid))

        # create a new PersonRef, and assign the handle, add the
        # PersonRef to the active person
        
        ref = RelLib.PersonRef()
        ref.ref = handle
        ignore = False
        while True:
            line =self.get_next()
            if self.level_is_finished(line,2):
                if not ignore:
                    state.person.add_person_ref(ref)
                break
            elif line.token == TOKEN_TYPE:
                if line.data != "INDI":
                    ignore = True
            elif line.token == TOKEN_RELA:
                ref.rel = line.data
            elif line.token == TOKEN_SOUR:
                ref.add_source_reference(self.handle_source(line,2))
            elif line.token == TOKEN_NOTE:
                note = self.parse_note(line,ref,2,"")
                ref.set_note(note)
            else:
                self.not_recognized(2)

    def func_person_alt_name(self,line,state):
        """
        Parse a altername name, usually indicated by a AKA or _AKA
        tag. This is not valid GEDCOM, but several programs will add
        this just to make life interesting. Odd, since GEDCOM supports
        multiple NAME indicators, which is the correct way of handling
        multiple names.
        """
        name = self.parse_name_personal(line.data)
        name.set_type(RelLib.NameType.AKA)
        state.person.add_alternate_name(name)

        #
        # Create a new state, and parse the remainder of the NAME level
        sub_state = CurrentState()
        sub_state.person = state.person
        sub_state.name = name
        sub_state.level = 2

        while True:
            line =self.get_next()
            if self.level_is_finished(line,2):
                name.set_note(sub_state.get_text())
                break
            else:
                func = self.name_func.get(line.token,self.func_name_undefined)
                func(line,sub_state)

    def func_person_object(self, line, state):
        """
        Currently, the embedded form is not supported
        
        Embedded form
        
        >   n OBJE @<XREF:OBJE>@ {1:1}

        Linked form
         
        >   n OBJE {1:1}
        >   +1 FORM <MULTIMEDIA_FORMAT> {1:1}
        >   +1 TITL <DESCRIPTIVE_TITLE> {0:1}
        >   +1 FILE <MULTIMEDIA_FILE_REFERENCE> {1:1}
        >   +1 <<NOTE_STRUCTURE>> {0:M}
        """
        if line.data and line.data[0] == '@':
            ref = RelLib.MediaRef()
            handle = self.find_object_handle(line.data[1:-1])
            ref.set_reference_handle(handle)
            self.person.add_media_reference(ref)
        else:
            (form, filename, title, note) = self.parse_obje(state.level+1)
            self.build_media_object(state.person, form, filename, title, note)

    def build_media_object(self, obj, form, filename, title, note):
        if form == "url":
            url = RelLib.Url()
            url.set_path(filename)
            url.set_description(title)
            obj.add_url(url)
        else:
            (ok,path) = self.find_file(filename,self.dir_path)
            if not ok:
                self.warn(_("Could not import %s") % filename)
                path = filename.replace('\\',os.path.sep)
            photo_handle = self.media_map.get(path)
            if photo_handle == None:
                photo = RelLib.MediaObject()
                photo.set_path(path)
                photo.set_description(title)
                full_path = os.path.abspath(path)
                if os.path.isfile(full_path):
                    photo.set_mime_type(Mime.get_type(full_path))
                else:
                    photo.set_mime_type(mime_map.get(form.lower(),'unknown'))
                self.db.add_object(photo, self.trans)
                self.media_map[path] = photo.handle
            else:
                photo = self.db.get_object_from_handle(photo_handle)
            oref = RelLib.MediaRef()
            oref.set_reference_handle(photo.handle)
            oref.set_note(note)
            obj.add_media_reference(oref)

    def func_person_note(self,line,state):
        self.note = self.parse_note(line,self.person,1,state.note)

    def func_person_rnote(self,line,state):
        self.note = self.parse_note(line,self.person,1,state.note)

    def func_person_sex(self,line,state):
        """
        >   +1 SEX <SEX_VALUE> {0:1}

        Valid values for <SEX_VALUE> are:

        >   M = Male
        >   F = Female
        """
        state.person.set_gender(line.data)

    def func_person_bapl(self,line,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.BAPTISM)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_conl(self,line,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.CONFIRMATION)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_endl(self,line,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.ENDOWMENT)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_slgc(self,line,state):
        lds_ord = RelLib.LdsOrd()
        lds_ord.set_type(RelLib.LdsOrd.SEAL_TO_PARENTS)
        state.person.lds_ord_list.append(lds_ord)
        self.parse_ord(lds_ord,2)

    def func_person_fams(self,line,state):
        handle = self.find_family_handle(line.data.strip()[1:-1])
        state.person.add_family_handle(handle)
        state.add_to_note(self.parse_optional_note(2))

    def func_person_famc(self,line,state):
        ftype,famc_note = self.parse_famc_type(2,state.person)
        gid = line.data.strip()[1:-1]
        handle = self.find_family_handle(gid)
                
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

                # search childrefs
                family = self.db.find_family_from_handle(handle, self.trans)
                print ">", gid
                family.set_gramps_id(gid)
                
                for ref in family.get_child_ref_list():
                    if ref.ref == state.person.handle:
                        ref.set_mother_relation(ftype)
                        ref.set_father_relation(ftype)
                        break
                else:
                    ref = RelLib.ChildRef()
                    ref.ref = state.person.handle
                    ref.set_mother_relation(ftype)
                    ref.set_father_relation(ftype)
                    family.add_child_ref(ref)
                self.db.commit_family(family, self.trans)

    def func_person_resi(self,line,state):
        """
        The RESI tag follows the EVENT_DETAIL structure, which is:

        >   n TYPE <EVENT_DESCRIPTOR> {0:1}
        >   n DATE <DATE_VALUE> {0:1}
        >   n <<PLACE_STRUCTURE>> {0:1}
        >   n <<ADDRESS_STRUCTURE>> {0:1}
        >   n AGE <AGE_AT_EVENT> {0:1}
        >   n AGNC <RESPONSIBLE_AGENCY> {0:1}
        >   n CAUS <CAUSE_OF_EVENT> {0:1}
        >   n <<SOURCE_CITATION>> {0:M}
        >   n <<MULTIMEDIA_LINK>> {0:M}
        >   n <<NOTE_STRUCTURE>> {0:M}

        Currently, the TYPE, AGE, CAUSE, STAT, and other tags which
        do not apply to an address are ignored.
        """

        addr = RelLib.Address()
        state.person.add_address(addr)

        note = ""
        while True:
            line =self.get_next()
            if self.level_is_finished(line, state.level+1):
                break
            elif line.token == TOKEN_DATE:
                addr.set_date_object(line.data)
            elif line.token == TOKEN_ADDR:
                addr.set_street(line.data)
                self.parse_address(addr, state.level+1)
            elif line.token == TOKEN_SOUR:
                addr.add_source_reference(self.handle_source(line,
                                                             state.level+1))
            elif line.token == TOKEN_PLAC:
                addr.set_street(line.data)
                self.parse_address(addr, state.level+1)
            elif line.token == TOKEN_PHON:
                if addr.get_street() == "":
                    addr.set_street("Unknown")
                addr.set_phone(line.data)
            elif line.token == TOKEN_NOTE:
                note = self.parse_note(line, addr, state.level+1, '')
            elif line.token in (TOKEN_IGNORE, TOKEN_CAUS, TOKEN_STAT,
                                TOKEN_TEMP, TOKEN_OBJE, TOKEN_TYPE):
                self.ignore_sub_junk(state.level+2)
            else:
                self.not_recognized(state.level+1)

    def func_person_addr(self,line,state):
        """
        Parses the Address structure by calling parse_address.
        """
        addr = RelLib.Address()
        addr.set_street(line.data)
        self.parse_address(addr,2)
        state.person.add_address(addr)

    def func_person_phon(self,line,state):
        addr = RelLib.Address()
        addr.set_street("Unknown")
        addr.set_phone(line.data)
        state.person.add_address(addr)

    def func_person_titl(self, line, state):
        event = RelLib.Event()
        event_ref = RelLib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(RelLib.EventType.NOB_TITLE)
        self.parse_event(event_ref, event, self.generic_event_map, 2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

    def func_person_std_event(self, line, state):
        event = RelLib.Event()
        event_ref = RelLib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(line.data)
        self.parse_event(event_ref, event, self.generic_event_map, 2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

    def func_person_std_attr(self, line, state):
        a = RelLib.Attribute()
        a.set_type(line.data)
        a.set_value(line.data)
        state.person.add_attribute(a)

    def func_person_birt(self,line,state):
        """
        >   n  BIRT [Y|<NULL>] {1:1}
        >   +1 <<EVENT_DETAIL>> {0:1} p.*
        >   +1 FAMC @<XREF:FAM>@ {0:1} p.*

        I'm not sure what value the FAMC actually offers here, since
        the FAMC record should handle this. Why it is a valid sub value
        is beyond me.
        """
        event = RelLib.Event()
        event_ref = RelLib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(RelLib.EventType.BIRTH)
        self.parse_event(event_ref, event, self.generic_event_map, 2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)

        if state.person.get_birth_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_birth_ref(event_ref)

    def func_person_adop(self,line,state):
        """
           n  BIRT [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*
           +1 FAMC @<XREF:FAM>@ {0:1} p.*
           +2 ADOP <ADOPTED_BY_WHICH_PARENT> {0:1}
        """
        event = RelLib.Event()
        event.set_gramps_id(self.emapper.find_next())
        event.set_type(RelLib.EventType.ADOPT)
        event_ref = RelLib.EventRef()

        self.parse_event(event_ref, event, self.person_adopt_map, 2)
        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)
        state.person.add_event_ref(event_ref)

    def func_person_deat(self,line,state):
        """
           n  DEAT [Y|<NULL>] {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*
        """
        event = RelLib.Event()
        event_ref = RelLib.EventRef()
        event.set_gramps_id(self.emapper.find_next())
        if line.data and line.data != 'Y':
            event.set_description(line.data)
        event.type.set(RelLib.EventType.DEATH)
        self.parse_event(event_ref, event, self.generic_event_map, 2)

        person_event_name(event,state.person)
        self.db.add_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)

        if state.person.get_death_ref():
            state.person.add_event_ref(event_ref)
        else:
            state.person.set_death_ref(event_ref)

    def func_person_even(self,line,state):
        """
           n  <<EVENT_TYPE>> {1:1}
           +1 <<EVENT_DETAIL>> {0:1} p.*
        """
        event = RelLib.Event()
        event_ref = RelLib.EventRef()
        event.set_type((RelLib.EventType.CUSTOM,""))
        event.set_gramps_id(self.emapper.find_next())
        if line.data and line.data != 'Y':
            event.set_description(line.data)
        self.parse_event(event_ref, event, self.generic_event_map, 2)
        
        the_type = event.get_type()

        if int(the_type) == RelLib.EventType.CUSTOM \
               and str(the_type) in self.attrs:
            attr = RelLib.Attribute()

            new_type = self.gedattr.get(str(the_type),RelLib.AttributeType.CUSTOM)
            attr.set_type(new_type)
            attr.set_value(event.get_description())
            state.person.add_attribute(attr)
        else:
            self.db.add_event(event, self.trans)
            event_ref.set_reference_handle(event.handle)
            state.person.add_event_ref(event_ref)

    def func_person_sour(self,line,state):
        source_ref = self.handle_source(line,2)
        state.person.add_source_reference(source_ref)

    def func_person_refn(self,line,state):
        if intRE.match(line.data):
            try:
                self.refn[self.person.handle] = int(line.data)
            except:
                pass

    def func_person_attr(self,line,state):
        attr = RelLib.Attribute()
        n = line[3]
        atype = self.gedattr.get(n,RelLib.AttributeType.CUSTOM)
        if atype == RelLib.AttributeType.CUSTOM:
            attr.set_type((atype,n))
        else:
            attr.set_type(atype)

        attr.set_value(line.data)
        state.person.add_attribute(attr)

    def func_person_resn(self,line,state):
        attr = RelLib.Attribute()
        attr.set_type((RelLib.AttributeType.CUSTOM, 'RESN'))
        state.person.add_attribute(attr)

    def func_person_event(self, line, state):
        n = line[3].strip()
        if self.gedattr.has_key(n):
            attr = RelLib.Attribute()
            attr.set_type((self.gedattr[n],''))
            attr.set_value(line.data)
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
                event.set_type((RelLib.EventType.CUSTOM,val))
            else:
                event.set_type((RelLib.EventType.CUSTOM,n))
                
        event_ref = RelLib.EventRef()
        self.parse_event(event_ref, event, self.generic_event_map, 2)
        if line.data and line.data != 'Y':
            event.set_description(line.data)
        person_event_name(event,state.person)

        self.db.add_event(event, self.trans)

        event_ref.set_reference_handle(event.handle)
        state.person.add_event_ref(event_ref)

    #-------------------------------------------------------------------------
    #
    # 
    #
    #-------------------------------------------------------------------------
    def func_name_undefined(self,line,state):
        self.not_recognized(state.level+1)

    def func_name_note(self,line,state):
        state.add_to_note(self.parse_note(line,state.name,
                                          state.level+1,state.note))

    def func_name_alia(self,line,state):
        """
        The ALIA tag is supposed to cross reference another person.
        However, we do not support this.

        Some systems use the ALIA tag as an alternate NAME tag, which
        is not legal in GEDCOM, but oddly enough, is easy to support.
        """
        if line.data[0] == '@':
            aka = RelLib.Name()
            try:
                names = nameRegexp.match(line.data).groups()
            except:
                names = (line.data,"","","","")
            if names[0]:
                aka.set_first_name(names[0].strip())
            if names[2]:
                aka.set_surname(names[2].strip())
            if names[4]:
                aka.set_suffix(names[4].strip())
            state.person.add_alternate_name(aka)
        else:
            pass

    def func_name_npfx(self,line,state):
        state.name.set_title(line.data.strip())

    def func_name_givn(self,line,state):
        state.name.set_first_name(line.data.strip())

    def func_name_spfx(self,line,state):
        state.name.set_surname_prefix(line.data.strip())

    def func_name_surn(self,line,state):
        state.name.set_surname(line.data.strip())

    def func_name_marnm(self,line,state):
        self.parse_marnm(state.person,line.data.strip())

    def func_name_nsfx(self,line,state):
        if state.name.get_suffix() == "":
            state.name.set_suffix(line.data)

    def func_name_nick(self,line,state):
        attr = RelLib.Attribute()
        attr.set_type(RelLib.AttributeType.NICKNAME)
        attr.set_value(line.data)
        state.person.add_attribute(attr)

    def func_name_aka(self, line, state):
        
        lname = line.data.split()
        l = len(lname)
        if l == 1:
            attr = RelLib.Attribute()
            attr.set_type(RelLib.AttributeType.NICKNAME)
            attr.set_value(line.data)
            state.person.add_attribute(attr)
        else:
            name = RelLib.Name()
            name.set_surname(lname[-1].strip())
            name.set_first_name(' '.join(lname[0:l-1]))
            state.person.add_alternate_name(name)

    def func_name_sour(self, line, state):
        sref = self.handle_source(line,state.level+1)
        state.name.add_source_reference(sref)

    def parse_repository(self,repo):
        state = CurrentState()
        state.repo = repo

        while True:
            line = self.get_next()
            
            if self.level_is_finished(line, 1):
                break
            else:
                func = self.repo_func.get(line.token,self.func_repo_ignore)
                func(line, repo, 1)

    def func_repo_name(self, line, repo, level):
        repo.set_name(line.data)

    def func_repo_ignore(self, line, repo, level):
        self.ignore_sub_junk(level)

    def func_repo_addr(self, line, repo, level):
        """
        n ADDR <ADDRESS_LINE> {0:1} 
        +1 CONT <ADDRESS_LINE> {0:M}
        +1 ADR1 <ADDRESS_LINE1> {0:1}
        +1 ADR2 <ADDRESS_LINE2> {0:1}
        +1 CITY <ADDRESS_CITY> {0:1}
        +1 STAE <ADDRESS_STATE> {0:1}
        +1 POST <ADDRESS_POSTAL_CODE> {0:1}
        +1 CTRY <ADDRESS_COUNTRY> {0:1}
        n PHON <PHONE_NUMBER> {0:3}

        Some repositories do not try to break up the address,
        instead they put everything on a single line. Try to determine
        if this happened, and try to fix it.
        
        """

        addr = RelLib.Address()
        matched = False

        addr.set_street(line.data)
        self.parse_address(addr, 2)

        text = addr.get_street()
        if not addr.get_city() and not addr.get_state() and \
           not addr.get_postal_code() and not addr.get_country():
        
            match = addr_re.match(text)
            if match:
                groups = match.groups()
                addr.set_street(groups[0].strip())
                addr.set_city(groups[2].strip())
                addr.set_state(groups[3].strip())
                addr.set_postal_code(groups[4].strip())
                addr.set_country(groups[5].strip())
                matched = True
            
            match = addr2_re.match(text)
            if match:
                groups = match.groups()
                addr.set_street(groups[0].strip())
                addr.set_city(groups[2].strip())
                addr.set_state(groups[3].strip())
                addr.set_postal_code(groups[4].strip())
                matched = True

            match = addr3_re.match(text)
            if match:
                groups = match.groups()
                addr.set_street(groups[0].strip())
                addr.set_city(groups[2].strip())
                addr.set_state(groups[3].strip())
                matched = True

        repo.add_address(addr)

    def skip_record(self,line,state):
        self.ignore_sub_junk(2)

    def extract_temple(self, line):
        def get_code(code):
            if LdsUtils.temple_to_abrev.has_key(code):
                return code
            elif LdsUtils.temple_codes.has_key(code):
                return LdsUtils.temple_codes[code]
        
        c = get_code(line.data)
        if c: return c
        
        ## Not sure why we do this. Kind of ugly.
        c = get_code(line.data.split()[0])
        if c: return c

        ## Okay we have no clue which temple this is.
        ## We should tell the user and store it anyway.
        self.warn("Invalid temple code '%s'" % (line.data,))
        return line.data

def person_event_name(event,person):
    if event.get_type().is_custom():
        if not event.get_description():
            text = _event_person_str % {
                'event_name' : str(event.get_type()),
                'person' : NameDisplay.displayer.display(person),
                }
            event.set_description(text)

def load_place_values(place,text,pf=None):
    items = [item.strip() for item in text.split(',')]
    if not pf:
        pf = _place_field

    if len(items) != len(pf):
        return
    loc = place.get_main_location()
    index = 0
    for item in items:
        pf[index](loc,item)
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
    from GrampsDb import gramps_db_factory

    def callback(val):
        pass


    form = logging.Formatter(fmt="%(levelname)s: %(filename)s: line %(lineno)d: %(message)s")
    
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # Setup the base level logger, this one gets
    # everything.
    l = logging.getLogger()
    l.setLevel(logging.DEBUG)
    l.addHandler(stderrh)

    codeset = None

    db_class = gramps_db_factory(const.app_gramps)
    database = db_class()
    database.load("test.grdb",lambda x: None, mode="w")
    np = NoteParser(sys.argv[1], False, 0)
    g = GedcomParser(database,sys.argv[1],callback, codeset, np.get_map(),
                     np.get_lines(),np.get_persons())
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
    print "Closing", database
    database.close()
