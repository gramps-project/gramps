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

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import sys
import sets
import shutil
from xml.parsers.expat import ExpatError, ParserCreate
from gettext import gettext as _
import re

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ReadXML")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from QuestionDialog import ErrorDialog
import Mime
import RelLib
import const
import Utils
import DateHandler
from BasicUtils import NameDisplay
from GrampsDb._GrampsDbConst import \
     PERSON_KEY,FAMILY_KEY,SOURCE_KEY,EVENT_KEY,\
     MEDIA_KEY,PLACE_KEY,REPOSITORY_KEY,NOTE_KEY
from BasicUtils import UpdateCallback

#-------------------------------------------------------------------------
#
# Try to detect the presence of gzip
#
#-------------------------------------------------------------------------
try:
    import gzip
    gzip_ok = 1
except:
    gzip_ok = 0

personRE = re.compile(r"\s*\<person\s(.*)$")

crel_map = {
    "Birth"     : RelLib.ChildRefType(RelLib.ChildRefType.BIRTH),
    "Adopted"   : RelLib.ChildRefType(RelLib.ChildRefType.ADOPTED),
    "Stepchild" : RelLib.ChildRefType(RelLib.ChildRefType.STEPCHILD),
    "Sponsored" : RelLib.ChildRefType(RelLib.ChildRefType.SPONSORED),
    "Foster"    : RelLib.ChildRefType(RelLib.ChildRefType.FOSTER),
    "Unknown"   : RelLib.ChildRefType(RelLib.ChildRefType.UNKNOWN),
    }

_event_family_str = _("%(event_name)s of %(family)s")
_event_person_str = _("%(event_name)s of %(person)s")

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
# Must takes care of renaming media files according to their new IDs.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None,cl=0,use_trans=False):

    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    change = os.path.getmtime(filename)
    parser = GrampsParser(database,callback,basefile,change,filename)

    linecounter = LineParser(filename)
    lc = linecounter.get_count()
    pc = linecounter.get_person_count()
    
    ro = database.readonly
    database.readonly = False

    if gzip_ok:
        use_gzip = 1
        try:
            f = gzip.open(filename,"r")
            f.read(1)
            f.close()
        except IOError,msg:
            use_gzip = 0
        except ValueError, msg:
            use_gzip = 1
    else:
        use_gzip = 0

    try:
        if use_gzip:
            xml_file = gzip.open(filename,"rb")
        else:
            xml_file = open(filename,"r")
    except IOError,msg:
        if cl:
            print "Error: %s could not be opened Exiting." % filename
            print msg
            sys.exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename,str(msg))
            return
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
            sys.exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename)
            return
    try:
        parser.parse(xml_file,use_trans,lc,pc)
    except IOError,msg:
        if cl:
            print "Error reading %s" % filename
            print msg
            import traceback
            traceback.print_exc()
            sys.exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,str(msg))
            import traceback
            traceback.print_exc()
            return
    except ExpatError, msg:
        if cl:
            print "Error reading %s" % filename
            print "The file is probably either corrupt or not a valid GRAMPS database."
            sys.exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,
                        _("The file is probably either corrupt or not a valid GRAMPS database."))
            return

    xml_file.close()

    database.readonly = ro

    # copy all local images into <database>.images directory
    db_dir = os.path.abspath(os.path.dirname(database.get_save_path()))
    db_base = os.path.basename(database.get_save_path())
    img_dir = os.path.join(db_dir,db_base)
    first = not os.path.exists(img_dir)
    
    for m_id in database.get_media_object_handles():
        mobject = database.get_object_from_handle(m_id)
        oldfile = mobject.get_path()
        if oldfile and not os.path.isabs(oldfile):
            if first:
                os.mkdir(img_dir)
                first = 0
            newfile = os.path.join(img_dir,oldfile)

            try:
                oldfilename = os.path.join(basefile,oldfile)
                shutil.copyfile(oldfilename,newfile)
                try:
                    shutil.copystat(oldfilename,newfile)
                except:
                    pass
                mobject.set_path(newfile)
                database.commit_media_object(mobject,None,change)
            except (IOError,OSError),msg:
                ErrorDialog(_('Could not copy file'),str(msg))

#-------------------------------------------------------------------------
#
# Remove extraneous spaces
#
#-------------------------------------------------------------------------

def rs(text):
    return ' '.join(text.split())

def fix_spaces(text_list):
    return '\n'.join(map(rs,text_list))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class LineParser:
    def __init__(self, filename):

        self.count = 0
        self.person_count = 0

        if gzip_ok:
            use_gzip = 1
            try:
                f = gzip.open(filename,"r")
                f.read(1)
                f.close()
            except IOError,msg:
                use_gzip = 0
            except ValueError, msg:
                use_gzip = 1
        else:
            use_gzip = 0

        try:
            if use_gzip:
                f = gzip.open(filename,"rb")
            else:
                f = open(filename,"r")

            for line in f:
                self.count += 1
                if personRE.match(line):
                    self.person_count += 1

            f.close()
        except:
            self.count = 0
            self.person_count = 0

    def get_count(self):
        return self.count

    def get_person_count(self):
        return self.person_count

#-------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
#-------------------------------------------------------------------------
class GrampsParser(UpdateCallback):

    def __init__(self,database,callback,base,change,filename):
        UpdateCallback.__init__(self,callback)
        self.filename = filename
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []
        self.tlist = []
        self.conf = 2
        self.gid2id = {}
        self.gid2fid = {}
        self.gid2eid = {}
        self.gid2pid = {}
        self.gid2oid = {}
        self.gid2sid = {}
        self.gid2rid = {}
        self.gid2nid = {}
        self.childref_map = {}
        self.change = change
        self.dp = DateHandler.parser
        self.place_names = sets.Set()
        cursor = database.get_place_cursor()
        data = cursor.next()
        while data:
            (handle,val) = data
            self.place_names.add(val[2])
            data = cursor.next()
        cursor.close()
        
        self.ord = None
        self.objref = None
        self.object = None
        self.repo = None
        self.reporef = None
        self.pref = None
        self.use_p = 0
        self.in_note = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.in_witness = False
        self.db = database
        self.base = base
        self.photo = None
        self.person = None
        self.family = None
        self.address = None
        self.source = None
        self.source_ref = None
        self.attribute = None
        self.placeobj = None
        self.locations = 0
        self.place_map = {}

        self.resname = ""
        self.resaddr = "" 
        self.rescity = ""
        self.resstate = ""
        self.rescon = "" 
        self.respos = ""
        self.resphone = ""
        self.resemail = ""

        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.lmap = {}
        self.media_file_map = {}

        # List of new name formats and a dict for remapping them
        self.name_formats  = []
        self.name_formats_map = {}
        self.taken_name_format_numbers = [num for (num,name,fmt_str,active)
                                          in self.db.name_formats]
        
        self.event = None
        self.eventref = None
        self.childref = None
        self.personref = None
        self.name = None
        self.tempDefault = None
        self.home = None
        self.owner = RelLib.Researcher()
        self.func_list = [None]*50
        self.func_index = 0
        self.func = None
        self.witness_comment = ""
        self.idswap = {}
        self.fidswap = {}
        self.eidswap = {}
        self.sidswap = {}
        self.pidswap = {}
        self.oidswap = {}
        self.ridswap = {}
        self.nidswap = {}
        self.eidswap = {}

        self.func_map = {
            "address"    : (self.start_address, self.stop_address),
            "addresses"  : (None,None),
            "childlist"  : (None,None),
            "aka"        : (self.start_name, self.stop_aka),
            "attribute"  : (self.start_attribute, self.stop_attribute),
            "attr_type"  : (None,self.stop_attr_type),
            "attr_value" : (None,self.stop_attr_value),
            "bookmark"   : (self.start_bmark, None),
            "bookmarks"  : (None, None),
            "format"     : (self.start_format, None),
            "name-formats"  : (None, None),
            "child"      : (self.start_child,None),
            "childof"    : (self.start_childof,None),
            "childref"   : (self.start_childref,self.stop_childref),
            "personref"  : (self.start_personref,self.stop_personref),
            "city"       : (None, self.stop_city),
            "county"     : (None, self.stop_county),
            "country"    : (None, self.stop_country),
            "comment"    : (None, self.stop_comment),
            "created"    : (self.start_created, None),
            "ref"        : (None, self.stop_ref),
            "database"   : (self.start_database, self.stop_database),
            "phone"      : (None, self.stop_phone),
            "date"       : (None, self.stop_date),
            "cause"      : (None, self.stop_cause),
            "description": (None, self.stop_description),
            "event"      : (self.start_event, self.stop_event),
            "type"       : (None, self.stop_type),
            "witness"    : (self.start_witness,self.stop_witness),
            "eventref"   : (self.start_eventref,self.stop_eventref),
            "data_item"  : (self.start_data_item, None),
            "families"   : (None, self.stop_families),
            "family"     : (self.start_family, self.stop_family),
            "rel"        : (self.start_rel, None),
            "father"     : (self.start_father, None),
            "first"      : (None, self.stop_first),
            "call"       : (None, self.stop_call),
            "gender"     : (None, self.stop_gender),
            "header"     : (None, None),
            "last"       : (self.start_last, self.stop_last),
            "mother"     : (self.start_mother,None),
            "name"       : (self.start_name, self.stop_name),
            "nick"       : (None, self.stop_nick),
            "note"       : (self.start_note, self.stop_note),
            "noteref"    : (self.start_noteref,None),
            "p"          : (None, self.stop_ptag),
            "parentin"   : (self.start_parentin,None),
            "people"     : (self.start_people, self.stop_people),
            "person"     : (self.start_person, self.stop_person),
            "img"        : (self.start_photo, self.stop_photo),
            "objref"     : (self.start_objref, self.stop_objref),
            "object"     : (self.start_object, self.stop_object),
            "file"       : (self.start_file, None),
            "place"      : (self.start_place, self.stop_place),
            "dateval"    : (self.start_dateval, None),
            "daterange"  : (self.start_daterange, None),
            "datestr"    : (self.start_datestr, None),
            "places"     : (None, self.stop_places),
            "placeobj"   : (self.start_placeobj,self.stop_placeobj),
            "ptitle"     : (None,self.stop_ptitle),
            "location"   : (self.start_location,None),
            "lds_ord"    : (self.start_lds_ord, self.stop_lds_ord),
            "temple"     : (self.start_temple, None),
            "status"     : (self.start_status, None),
            "sealed_to"  : (self.start_sealed_to, None),
            "coord"      : (self.start_coord,None),
            "patronymic" : (None, self.stop_patronymic),
            "pos"        : (self.start_pos, None),
            "postal"     : (None, self.stop_postal),
            "researcher" : (None, self.stop_research),
            "resname"    : (None, self.stop_resname ),
            "resaddr"    : (None, self.stop_resaddr ),
            "rescity"    : (None, self.stop_rescity ),
            "resstate"   : (None, self.stop_resstate ),
            "rescountry" : (None, self.stop_rescountry),
            "respostal"  : (None, self.stop_respostal),
            "resphone"   : (None, self.stop_resphone),
            "resemail"   : (None, self.stop_resemail),
            "sauthor"    : (None, self.stop_sauthor),
            "sabbrev"    : (None, self.stop_sabbrev),
            "scomments"  : (None, self.stop_scomments),
            "source"     : (self.start_source, self.stop_source),
            "sourceref"  : (self.start_sourceref, self.stop_sourceref),
            "sources"    : (None, None),
            "spage"      : (None, self.stop_spage),
            "spubinfo"   : (None, self.stop_spubinfo),
            "state"      : (None, self.stop_state),
            "stext"      : (None, self.stop_stext),
            "stitle"     : (None, self.stop_stitle),
            "street"     : (None, self.stop_street),
            "suffix"     : (None, self.stop_suffix),
            "title"      : (None, self.stop_title),
            "url"        : (self.start_url, None),
            "repository" : (self.start_repo,self.stop_repo),
            "reporef"    : (self.start_reporef,self.stop_reporef),
            "rname"      : (None, self.stop_rname),
            }

    def find_person_by_gramps_id(self,gramps_id):
        intid = self.gid2id.get(gramps_id)
        if intid:
            person = self.db.get_person_from_handle(intid)
        else:
            intid = Utils.create_id()
            person = RelLib.Person()
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)
            self.db.add_person(person,self.trans)
            self.gid2id[gramps_id] = intid
        return person

    def find_family_by_gramps_id(self,gramps_id):
        intid = self.gid2fid.get(gramps_id)
        if intid:
            family = self.db.get_family_from_handle(intid)
        else:
            intid = Utils.create_id()
            family = RelLib.Family()
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)
            self.db.add_family(family,self.trans)
            self.gid2fid[gramps_id] = intid
        return family

    def find_event_by_gramps_id(self,gramps_id):
        intid = self.gid2eid.get(gramps_id)
        if intid:
            event = self.db.get_event_from_handle(intid)
        else:
            intid = Utils.create_id()
            event = RelLib.Event()
            event.set_handle(intid)
            event.set_gramps_id(gramps_id)
            self.db.add_event(event,self.trans)
            self.gid2eid[gramps_id] = intid
        return event

    def find_place_by_gramps_id(self,gramps_id):
        intid = self.gid2pid.get(gramps_id)
        if intid:
            place = self.db.get_place_from_handle(intid)
        else:
            intid = Utils.create_id()
            place = RelLib.Place()
            place.set_handle(intid)
            place.set_gramps_id(gramps_id)
            self.db.add_place(place,self.trans)
            self.gid2pid[gramps_id] = intid
        return place

    def find_source_by_gramps_id(self,gramps_id):
        intid = self.gid2sid.get(gramps_id)
        if intid:
            source = self.db.get_source_from_handle(intid)
        else:
            intid = Utils.create_id()
            source = RelLib.Source()
            source.set_handle(intid)
            source.set_gramps_id(gramps_id)
            self.db.add_source(source,self.trans)
            self.gid2sid[gramps_id] = intid
        return source

    def find_object_by_gramps_id(self,gramps_id):
        intid = self.gid2oid.get(gramps_id)
        if intid:
            obj = self.db.get_object_from_handle(intid)
        else:
            intid = Utils.create_id()
            obj = RelLib.MediaObject()
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
            self.db.add_object(obj,self.trans)
            self.gid2oid[gramps_id] = intid
        return obj

    def find_repository_by_gramps_id(self,gramps_id):
        intid = self.gid2rid.get(gramps_id)
        if intid:
            repo = self.db.get_repository_from_handle(intid)
        else:
            intid = Utils.create_id()
            repo = RelLib.Repository()
            repo.set_handle(intid)
            repo.set_gramps_id(gramps_id)
            self.db.add_repository(repo,self.trans)
            self.gid2rid[gramps_id] = intid
        return repo

    def find_note_by_gramps_id(self,gramps_id):
        intid = self.gid2nid.get(gramps_id)
        if intid:
            note = self.db.get_note_from_handle(intid)
        else:
            intid = Utils.create_id()
            note = RelLib.Note()
            note.set_handle(intid)
            note.set_gramps_id(gramps_id)
            self.db.add_note(note,self.trans)
            self.gid2nid[gramps_id] = intid
        return note

    def map_gid(self,gramps_id):
        if not self.idswap.get(gramps_id):
            if self.db.has_gramps_id(PERSON_KEY,gramps_id):
                self.idswap[gramps_id] = self.db.find_next_person_gramps_id()
            else:
                self.idswap[gramps_id] = gramps_id
        return self.idswap[gramps_id]

    def map_fid(self,gramps_id):
        if not self.fidswap.get(gramps_id):
            if self.db.has_gramps_id(FAMILY_KEY,gramps_id):
                self.fidswap[gramps_id] = self.db.find_next_family_gramps_id()
            else:
                self.fidswap[gramps_id] = gramps_id
        return self.fidswap[gramps_id]

    def map_eid(self,gramps_id):
        if not self.eidswap.get(gramps_id):
            if self.db.has_gramps_id(EVENT_KEY,gramps_id):
                self.eidswap[gramps_id] = self.db.find_next_event_gramps_id()
            else:
                self.eidswap[gramps_id] = gramps_id
        return self.eidswap[gramps_id]

    def map_pid(self,gramps_id):
        if not self.pidswap.get(gramps_id):
            if self.db.has_gramps_id(PLACE_KEY,gramps_id):
                self.pidswap[gramps_id] = self.db.find_next_place_gramps_id()
            else:
                self.pidswap[gramps_id] = gramps_id
        return self.pidswap[gramps_id]

    def map_sid(self,gramps_id):
        if not self.sidswap.get(gramps_id):
            if self.db.has_gramps_id(SOURCE_KEY,gramps_id):
                self.sidswap[gramps_id] = self.db.find_next_source_gramps_id()
            else:
                self.sidswap[gramps_id] = gramps_id
        return self.sidswap[gramps_id]

    def map_oid(self,gramps_id):
        if not self.oidswap.get(gramps_id):
            if self.db.has_gramps_id(MEDIA_KEY,gramps_id):
                self.oidswap[gramps_id] = self.db.find_next_object_gramps_id()
            else:
                self.oidswap[gramps_id] = gramps_id
        return self.oidswap[gramps_id]

    def map_rid(self,gramps_id):
        if not self.ridswap.get(gramps_id):
            if self.db.has_gramps_id(REPOSITORY_KEY,gramps_id):
                self.ridswap[gramps_id] = self.db.find_next_repository_gramps_id()
            else:
                self.ridswap[gramps_id] = gramps_id
        return self.ridswap[gramps_id]

    def map_nid(self,gramps_id):
        if not self.nidswap.get(gramps_id):
            if self.db.has_gramps_id(NOTE_KEY,gramps_id):
                self.nidswap[gramps_id] = self.db.find_next_note_gramps_id()
            else:
                self.nidswap[gramps_id] = gramps_id
        return self.nidswap[gramps_id]

    def parse(self,file,use_trans=False,linecount=0,personcount=0):
        if personcount < 1000:
            no_magic = True
        else:
            no_magic = False
        self.trans = self.db.transaction_begin("",batch=True,no_magic=no_magic)
        self.set_total(linecount)

        self.db.disable_signals()

        self.p = ParserCreate()
        self.p.StartElementHandler = self.startElement
        self.p.EndElementHandler = self.endElement
        self.p.CharacterDataHandler = self.characters
        self.p.ParseFile(file)

        if len(self.name_formats) > 0:
            # add new name formats to the existing table
            self.db.name_formats += self.name_formats
            # Register new formats
            NameDisplay.displayer.set_name_format(self.db.name_formats)

        self.db.set_researcher(self.owner)
        if self.home != None:
            person = self.db.find_person_from_handle(self.home,self.trans)
            self.db.set_default_person_handle(person.handle)
        if self.tempDefault != None:
            gramps_id = self.map_gid(self.tempDefault)
            person = self.find_person_by_gramps_id(gramps_id)
            if person:
                self.db.set_default_person_handle(person.handle)

        for key in self.func_map.keys():
            del self.func_map[key]
        del self.func_map
        del self.func_list
        del self.p
        self.db.transaction_commit(self.trans,_("GRAMPS XML import"))
        self.db.enable_signals()
        self.db.request_rebuild()

    def start_lds_ord(self,attrs):
        self.ord = RelLib.LdsOrd()
        self.ord.set_type_from_xml(attrs['type'])
        if self.person:
            self.person.lds_ord_list.append(self.ord)
        elif self.family:
            self.family.lds_ord_list.append(self.ord)

    def start_temple(self,attrs):
        self.ord.set_temple(attrs['val'])

    def start_data_item(self,attrs):
        self.source.set_data_item(attrs['key'],attrs['value'])

    def start_status(self,attrs):
        try:
            # old xml with integer statuses
            self.ord.set_status(int(attrs['val']))
        except ValueError:
            # string
            self.ord.set_status_from_xml(attrs['val'])

    def start_sealed_to(self,attrs):
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_family_from_handle(handle,self.trans)
        except KeyError:
            gramps_id = self.map_fid(attrs['ref'])
            family = self.find_family_by_gramps_id(gramps_id)
            handle = family.handle
        self.ord.set_family_handle(handle)
        
    def start_place(self,attrs):
        try:
            self.placeobj = self.db.find_place_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            gramps_id = self.map_pid(attrs['ref'])
            self.placeobj = self.find_place_by_gramps_id(gramps_id)
        
    def start_placeobj(self,attrs):
        gramps_id = self.map_pid(attrs['id'])
        try:
            self.placeobj = self.db.find_place_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.placeobj.set_gramps_id(gramps_id)
        except KeyError:
            self.placeobj = self.find_place_by_gramps_id(gramps_id)
        # GRAMPS LEGACY: title in the placeobj tag
        self.placeobj.title = attrs.get('title','')
        self.locations = 0
        self.update(self.p.CurrentLineNumber)
            
    def start_location(self,attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""
        
        loc = RelLib.Location()
        loc.phone = attrs.get('phone','')
        loc.postal = attrs.get('postal','')
        loc.city = attrs.get('city','')
        loc.street = attrs.get('street','')
        loc.parish = attrs.get('parish','')
        loc.state = attrs.get('state','')
        loc.county = attrs.get('county','')
        loc.country = attrs.get('country','')
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
            self.locations = self.locations + 1

    def start_witness(self,attrs):
        # Parse witnesses created by older gramps
        self.in_witness = True
        self.witness_comment = ""
        if attrs.has_key('name'):
            note = RelLib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness name: %s") % attrs['name'])
            self.db.add_note(note,self.trans)
            self.event.add_note(note.handle)
            return

        try:
            handle = attrs['hlink'].replace('_','')
            person = self.db.find_person_from_handle(handle,self.trans)
        except KeyError:
            if attrs.has_key('ref'):
                person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            else:
                person = None

        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        if person:
            event_ref = RelLib.EventRef()
            event_ref.ref = self.event.handle
            event_ref.role.set(RelLib.EventRoleType.WITNESS)
            person.event_ref_list.append(event_ref)
            self.db.commit_person(person,self.trans,self.change)
        
    def start_coord(self,attrs):
        self.placeobj.lat = attrs.get('lat','')
        self.placeobj.long = attrs.get('long','')

    def start_event(self,attrs):
        if self.person or self.family:
            # GRAMPS LEGACY: old events that were written inside
            # person or family objects.
            self.event = RelLib.Event()
            self.event.handle = Utils.create_id()
            self.event.type = RelLib.EventType()
            self.event.type.set_from_xml_str(attrs['type'])
            self.db.add_event(self.event,self.trans)
        else:
            # This is new event, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            gramps_id = self.map_eid(attrs["id"])
            try:
                self.event = self.db.find_event_from_handle(
                    attrs['handle'].replace('_',''),self.trans)
                self.event.gramps_id = gramps_id
            except KeyError:
                self.event = self.find_event_by_gramps_id(gramps_id)
            self.event.private = bool(attrs.get("priv"))

    def start_eventref(self,attrs):
        self.eventref = RelLib.EventRef()
        self.eventref.ref = attrs['hlink'].replace('_','')
        self.eventref.private = bool(attrs.get('priv'))
        if attrs.has_key('role'):
            self.eventref.role.set_from_xml_str(attrs['role'])

        # We count here on events being already parsed prior to parsing
        # people or families. This code will fail if this is not true.
        event = self.db.get_event_from_handle(self.eventref.ref)
        if not event:
            return
        
        if self.family:
            event.personal = False
            self.family.add_event_ref(self.eventref)
        elif self.person:
            event.personal = True
            if (event.type == RelLib.EventType.BIRTH) \
                   and (self.eventref.role == RelLib.EventRoleType.PRIMARY) \
                   and (self.person.get_birth_ref() == None):
                self.person.set_birth_ref(self.eventref)
            elif (event.type == RelLib.EventType.DEATH) \
                     and (self.eventref.role == RelLib.EventRoleType.PRIMARY) \
                     and (self.person.get_death_ref() == None):
                self.person.set_death_ref(self.eventref)
            else:
                self.person.add_event_ref(self.eventref)

    def start_attribute(self,attrs):
        self.attribute = RelLib.Attribute()
        self.attribute.private = bool(attrs.get("priv"))
        self.attribute.type = RelLib.AttributeType()
        if attrs.has_key('type'):
            self.attribute.type.set_from_xml_str(attrs["type"])
        self.attribute.value = attrs.get("value",'')
        if self.photo:
            self.photo.add_attribute(self.attribute)
        elif self.object:
            self.object.add_attribute(self.attribute)
        elif self.objref:
            self.objref.add_attribute(self.attribute)
        elif self.event:
            self.event.add_attribute(self.attribute)
        elif self.eventref:
            self.eventref.add_attribute(self.attribute)
        elif self.person:
            self.person.add_attribute(self.attribute)
        elif self.family:
            self.family.add_attribute(self.attribute)

    def start_address(self,attrs):
        self.address = RelLib.Address()
        self.address.private = bool(attrs.get("priv"))

    def start_bmark(self,attrs):
        target = attrs.get('target')
        if not target:
            # Old XML. Can be either handle or id reference
            # and this is guaranteed to be a person bookmark
            try:
                handle = attrs['hlink'].replace('_','')
                self.db.check_person_from_handle(handle,self.trans)
            except KeyError:
                gramps_id = self.map_gid(attrs["ref"])
                person = self.find_person_by_gramps_id(gramps_id)
                handle = person.handle
            self.db.bookmarks.append(handle)
            return

        # This is new XML, so we are guaranteed to have a handle ref
        handle = attrs['hlink'].replace('_','')
        if target == 'person':
            self.db.check_person_from_handle(handle,self.trans)
            self.db.bookmarks.append(handle)
        elif target == 'family':
            self.db.check_family_from_handle(handle,self.trans)
            self.db.family_bookmarks.append(handle)
        elif target == 'event':
            self.db.check_event_from_handle(handle,self.trans)
            self.db.event_bookmarks.append(handle)
        elif target == 'source':
            self.db.check_source_from_handle(handle,self.trans)
            self.db.source_bookmarks.append(handle)
        elif target == 'place':
            self.db.check_place_from_handle(handle,self.trans)
            self.db.place_bookmarks.append(handle)
        elif target == 'media':
            self.db.check_object_from_handle(handle,self.trans)
            self.db.media_bookmarks.append(handle)
        elif target == 'repository':
            self.db.check_repository_from_handle(handle,self.trans)
            self.db.repo_bookmarks.append(handle)
        elif target == 'note':
            self.db.check_note_from_handle(handle,self.trans)
            self.db.note_bookmarks.append(handle)

    def start_format(self,attrs):
        number = int(attrs['number'])
        name = attrs['name']
        fmt_str = attrs['fmt_str']
        active = bool(attrs.get('active',True))

        if number in self.taken_name_format_numbers:
            number = self.remap_name_format(number)

        self.name_formats.append((number,name,fmt_str,active))

    def remap_name_format(self,old_number):
        if self.name_formats_map.has_key(old_number): # This should not happen
            return self.name_formats_map[old_number]
        # Find the lowest new number not taken yet:
        new_number = -1
        while new_number in self.taken_name_format_numbers:
            new_number -= 1
        # Add this to the taken list
        self.taken_name_format_numbers.append(new_number)
        # Set up the mapping entry
        self.name_formats_map[old_number] = new_number
        # Return new number
        return new_number
        
    def start_person(self,attrs):
        self.update(self.p.CurrentLineNumber)
        new_id = self.map_gid(attrs['id'])
        try:
            self.person = self.db.find_person_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.person.set_gramps_id(new_id)
        except KeyError:
            self.person = self.find_person_by_gramps_id(new_id)

        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.person.marker.set(RelLib.MarkerType.COMPLETE)
        else:
            self.person.marker.set_from_xml_str(attrs.get("marker",''))

    def start_people(self,attrs):
        if attrs.has_key('home'):
            self.home = attrs['home'].replace('_','')
        elif attrs.has_key("default"):
            self.tempDefault = attrs["default"]

    def start_father(self,attrs):
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_person_from_handle(handle,self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle
        self.family.set_father_handle(handle)

    def start_mother(self,attrs):
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_person_from_handle(handle,self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle
        self.family.set_mother_handle(handle)
    
    def start_child(self,attrs):
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_person_from_handle(handle,self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle

        # Here we are handling the old XML, in which
        # frel and mrel belonged to the "childof" tag
        # If that were the case then childref_map has the childref ready
        if self.childref_map.has_key((self.family.handle,handle)):
            self.family.add_child_ref(
                self.childref_map[(self.family.handle,handle)])

    def start_childref(self,attrs):
        # Here we are handling the new XML, in which frel and mrel
        # belong to the "child" tag under family.
        self.childref = RelLib.ChildRef()
        self.childref.ref = attrs['hlink'].replace('_','')
        self.childref.private = bool(attrs.get('priv'))

        mrel = RelLib.ChildRefType()
        if attrs.get('mrel'):
            mrel.set_from_xml_str(attrs['mrel'])
        frel = RelLib.ChildRefType()
        if attrs.get('frel'):
            frel.set_from_xml_str(attrs['frel'])

        if not mrel.is_default():
            self.childref.set_mother_relation(mrel)
        if not frel.is_default():
            self.childref.set_father_relation(frel)
        self.family.add_child_ref(self.childref)

    def start_personref(self,attrs):
        self.personref = RelLib.PersonRef()
        self.personref.ref = attrs['hlink'].replace('_','')
        self.personref.private = bool(attrs.get('priv'))
        self.personref.rel = attrs['rel']
        self.person.add_person_ref(self.personref)

    def start_url(self,attrs):
        if not attrs.has_key("href"):
            return
        url = RelLib.Url()
        url.path = attrs["href"]
        url.set_description(attrs.get("description",''))
        url.privacy = bool(attrs.get('priv'))
        url.type.set_from_xml_str(attrs['type'])
        if self.person:
            self.person.add_url(url)
        elif self.placeobj:
            self.placeobj.add_url(url)
        elif self.repo:
            self.repo.add_url(url)

    def start_family(self,attrs):
        self.update(self.p.CurrentLineNumber)
        gramps_id = self.map_fid(attrs["id"])
        try:
            self.family = self.db.find_family_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.family.set_gramps_id(gramps_id)
        except KeyError:
            self.family = self.find_family_by_gramps_id(gramps_id)
        # GRAMPS LEGACY: the type now belongs to <rel> tag
        # Here we need to support old format of <family type="Married">
        if attrs.has_key('type'):
            self.family.type.set_from_xml_str(attrs["type"])
                
        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.family.marker.set(RelLib.MarkerType.COMPLETE)
        else:
            self.family.marker.set_from_xml_str(attrs.get("marker",''))

    def start_rel(self,attrs):
        if attrs.has_key('type'):
            self.family.type.set_from_xml_str(attrs["type"])

    def start_file(self,attrs):
        self.object.mime = attrs['mime']
        if attrs.has_key('description'):
            self.object.desc = attrs['description']
        else:
            self.object.desc = ""
        drive,src = os.path.splitdrive(attrs["src"])
        if src:
            if not drive and not os.path.isabs(src):
                fullpath = os.path.abspath(self.filename)
                src = os.path.join(os.path.dirname(fullpath),src)
            self.object.path = src

    def start_childof(self,attrs):
        try:
            handle = attrs["hlink"].replace('_','')
            self.db.check_family_from_handle(handle,self.trans)
        except KeyError:
            family = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
            handle = family.handle

        # Here we are handling the old XML, in which
        # frel and mrel belonged to the "childof" tag
        mrel = RelLib.ChildRefType()
        frel = RelLib.ChildRefType()
        if attrs.has_key('mrel'):
            mrel.set_from_xml_str(attrs['mrel'])
        if attrs.has_key('frel'):
            frel.set_from_xml_str(attrs['frel'])

        childref = RelLib.ChildRef()
        childref.ref = self.person.handle
        if not mrel.is_default():
            childref.set_mother_relation(mrel)
        if not frel.is_default():
            childref.set_father_relation(frel)
        self.childref_map[(handle,self.person.handle)] = childref
        self.person.add_parent_family_handle(handle)

    def start_parentin(self,attrs):
        try:
            handle = attrs["hlink"].replace('_','')
            self.db.check_family_from_handle(handle,self.trans)
        except KeyError:
            family = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
            handle = family.handle
        self.person.add_family_handle(handle)

    def start_name(self,attrs):
        if not self.in_witness:
            self.name = RelLib.Name()
            name_type = attrs['type']
            # Mapping "Other Name" from gramps 2.0.x to Unknown
            if (self.version_string=='1.0.0') and (name_type=='Other Name'):
                self.name.set_type(RelLib.NameType.UNKNOWN)
            else:
                self.name.type.set_from_xml_str(name_type)
            self.name.set_private = bool(attrs.get("priv"))
            self.alt_name = bool(attrs.get("alt"))
            try:
                sort_as = int(attrs["sort"])
                display_as = int(attrs["display"])

                # check if these pointers need to be remapped
                # and set the name attributes
                if self.name_formats_map.has_key(sort_as):
                    self.name.sort_as = self.name_formats_map[sort_as]
                else:
                    self.name.sort_as = sort_as
                if self.name_formats_map.has_key(display_as):
                    self.name.sort_as = self.name_formats_map[display_as]
                else:
                    self.name_display_as = display_as
            except KeyError:
                pass

    def start_last(self,attrs):
        self.name.prefix = attrs.get('prefix','')
        self.name.group_as = attrs.get('group','')
        
    def start_note(self,attrs):
        self.in_note = 0
        if 'handle' in attrs:
            # This is new note, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            gramps_id = self.map_nid(attrs["id"])
            try:
                self.note = self.db.find_note_from_handle(
                    attrs['handle'].replace('_',''),self.trans)
                self.note.gramps_id = gramps_id
            except KeyError:
                self.note = self.find_note_by_gramps_id(gramps_id)
            self.note.private = bool(attrs.get("priv"))
            self.note.format = int(attrs.get('format',RelLib.Note.FLOWED))
            self.note.type.set_from_xml_str(attrs['type'])
        else:
            # GRAMPS LEGACY: old notes that were written inside other objects
            # We need to create a top-level note.
            # On stop_note the reference to this note will be added
            self.note = RelLib.Note()
            self.note.handle = Utils.create_id()
            self.note.format = int(attrs.get('format',RelLib.Note.FLOWED))
            self.db.add_note(self.note,self.trans)

    def start_noteref(self,attrs):
        handle = attrs['hlink'].replace('_','')
        self.db.check_note_from_handle(handle,self.trans)

        if self.source_ref:
            self.source_ref.add_note(handle)
        elif self.address:
            self.address.add_note(handle)
        elif self.ord:
            self.ord.add_note(handle)
        elif self.attribute:
            self.attribute.add_note(handle)
        elif self.object:
            self.object.add_note(handle)
        elif self.objref:
            self.objref.add_note(handle)
        elif self.photo:
            self.photo.add_note(handle)
        elif self.name:
            self.name.add_note(handle)
        elif self.source:
            self.source.add_note(handle)
        elif self.event:
            self.event.add_note(handle)
        elif self.personref:
            self.personref.add_note(handle)
        elif self.person:
            self.person.add_note(handle)
        elif self.childref:
            self.childref.add_note(handle)
        elif self.family:
            self.family.add_note(handle)
        elif self.placeobj:
            self.placeobj.add_note(handle)
        elif self.eventref:
            self.eventref.add_note(handle)
        elif self.repo:
            self.repo.add_note(handle)
        elif self.reporef:
            self.reporef.add_note(handle)

    def start_sourceref(self,attrs):
        self.source_ref = RelLib.SourceRef()
        try:
            handle = attrs["hlink"].replace('_','')
            self.db.check_source_from_handle(handle,self.trans)
        except KeyError:
            source = self.find_source_by_gramps_id(self.map_sid(attrs["ref"]))
            handle = source.handle

        self.source_ref.ref = handle
        self.source_ref.confidence = int(attrs.get("conf",self.conf))
        if self.photo:
            self.photo.add_source_reference(self.source_ref)
        elif self.ord:
            self.ord.add_source_reference(self.source_ref)
        elif self.attribute:
            self.attribute.add_source_reference(self.source_ref)
        elif self.object:
            self.object.add_source_reference(self.source_ref)
        elif self.objref:
            self.objref.add_source_reference(self.source_ref)
        elif self.event:
            self.event.add_source_reference(self.source_ref)
        elif self.address:
            self.address.add_source_reference(self.source_ref)
        elif self.name:
            self.name.add_source_reference(self.source_ref)
        elif self.placeobj:
            self.placeobj.add_source_reference(self.source_ref)
        elif self.childref:
            self.childref.add_source_reference(self.source_ref)
        elif self.family:
            self.family.add_source_reference(self.source_ref)
        elif self.personref:
            self.personref.add_source_reference(self.source_ref)
        elif self.person:
            self.person.add_source_reference(self.source_ref)

    def start_source(self,attrs):
        self.update(self.p.CurrentLineNumber)
        gramps_id = self.map_sid(attrs["id"])
        try:
            self.source = self.db.find_source_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.source.set_gramps_id(gramps_id)
        except KeyError:
            self.source = self.find_source_by_gramps_id(gramps_id)

    def start_reporef(self,attrs):
        self.reporef = RelLib.RepoRef()
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_repository_from_handle(handle,self.trans)
        except KeyError:
            repo = self.find_repo_by_gramps_id(self.map_rid(attrs['ref']))
            handle = repo.handle
        
        self.reporef.ref = handle
        self.reporef.call_number = attrs.get('callno','')
        self.reporef.media_type.set_from_xml_str(attrs['medium'])
        # we count here on self.source being available
        # reporefs can only be found within source
        self.source.add_repo_reference(self.reporef)

    def start_objref(self,attrs):
        self.objref = RelLib.MediaRef()
        try:
            handle = attrs['hlink'].replace('_','')
            self.db.check_object_from_handle(handle,self.trans)
        except KeyError:
            obj = self.find_object_by_gramps_id(self.map_oid(attrs['ref']))
            handle = obj.handle
            
        self.objref.ref = handle
        self.objref.private = bool(attrs.get('priv'))
        if self.event:
            self.event.add_media_reference(self.objref)
        elif self.family:
            self.family.add_media_reference(self.objref)
        elif self.source:
            self.source.add_media_reference(self.objref)
        elif self.person:
            self.person.add_media_reference(self.objref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.objref)

    def start_object(self,attrs):
        gramps_id = self.map_oid(attrs['id'])
        try:
            self.object = self.db.find_object_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.object.set_gramps_id(gramps_id)
        except KeyError:
            self.object = self.find_object_by_gramps_id(gramps_id)

        # GRAMPS LEGACY: src, mime, and description attributes
        # now belong to the <file> tag. Here we are supporting
        # the old format of <object src="blah"...>
        self.object.mime = attrs.get('mime','')
        self.object.desc = attrs.get('description','')
        src = attrs.get("src",'')
        if src:
            if not os.path.isabs(src):
                fullpath = os.path.abspath(self.filename)
                src = os.path.join(os.path.dirname(fullpath),src)
            self.object.path = src

    def start_repo(self,attrs):
        gramps_id = self.map_rid(attrs['id'])
        try:
            self.repo = self.db.find_repository_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.repo.set_gramps_id(gramps_id)
        except KeyError:
            self.repo = self.find_repository_by_gramps_id(gramps_id)

    def stop_people(self,*tag):
        pass

    def stop_database(self,*tag):
        self.update(self.p.CurrentLineNumber)

    def stop_object(self,*tag):
        self.db.commit_media_object(self.object,self.trans,self.change)
        self.object = None

    def stop_objref(self,*tag):
        self.objref = None
        
    def stop_repo(self,*tag):
        self.db.commit_repository(self.repo,self.trans,self.change)
        self.repo = None

    def stop_reporef(self,*tag):
        self.reporef = None
        
    def start_photo(self,attrs):
        self.photo = RelLib.MediaObject()
        self.pref = RelLib.MediaRef()
        self.pref.set_reference_handle(self.photo.get_handle())
        
        for key in attrs.keys():
            if key == "descrip" or key == "description":
                self.photo.set_description(attrs[key])
            elif key == "priv":
                self.pref.set_privacy(int(attrs[key]))
            elif key == "src":
                src = attrs["src"]
                if not os.path.isabs(src):
                    self.photo.set_path(os.path.join(self.base,src))
                else:
                    self.photo.set_path(src)
            else:
                a = RelLib.Attribute()
                a.set_type(key)
                a.set_value(attrs[key])
                self.photo.add_attribute(a)
        self.photo.set_mime_type(Mime.get_type(self.photo.get_path()))
        self.db.add_object(self.photo)
        if self.family:
            self.family.add_media_reference(self.pref)
        elif self.source:
            self.source.add_media_reference(self.pref)
        elif self.person:
            self.person.add_media_reference(self.pref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.pref)

    def start_daterange(self,attrs):
        if self.source_ref:
            dv = self.source_ref.get_date_object()
        elif self.ord:
            dv = self.ord.get_date_object()
        elif self.object:
            dv = self.object.get_date_object()
        elif self.address:
            dv = self.address.get_date_object()
        elif self.name:
            dv = self.name.get_date_object()
        else:
            dv = self.event.get_date_object()

        start = attrs['start'].split('-')
        stop  = attrs['stop'].split('-')

        try:
            y = int(start[0])
        except ValueError:
            y = 0

        try:
            m = int(start[1])
        except:
            m = 0

        try:
            d = int(start[2])
        except:
            d = 0

        try:
            ry = int(stop[0])
        except:
            ry = 0

        try:
            rm = int(stop[1])
        except:
            rm = 0

        try:
            rd = int(stop[2])
        except:
            rd = 0

        if attrs.has_key("cformat"):
            cal = RelLib.Date.calendar.index(attrs['calendar'])
        else:
            cal = RelLib.Date.CAL_GREGORIAN

        if attrs.has_key('quality'):
            val = attrs['quality']
            if val == 'estimated':
                qual = RelLib.Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = RelLib.Date.QUAL_CALCULATED
            else:
                qual = RelLib.Date.QUAL_NONE
        else:
            qual = RelLib.Date.QUAL_NONE
        
        dv.set(qual,RelLib.Date.MOD_RANGE,cal,(d,m,y,False,rd,rm,ry,False))

    def start_dateval(self,attrs):
        if self.source_ref:
            dv = self.source_ref.get_date_object()
        elif self.ord:
            dv = self.ord.get_date_object()
        elif self.object:
            dv = self.object.get_date_object()
        elif self.address:
            dv = self.address.get_date_object()
        elif self.name:
            dv = self.name.get_date_object()
        else:
            dv = self.event.get_date_object()

        bc = 1
        val = attrs['val']
        if val[0] == '-':
            bc = -1
            val = val[1:]
        start = val.split('-')
        try:
            y = int(start[0])*bc
        except:
            y = 0

        try:
            m = int(start[1])
        except:
            m = 0

        try:
            d = int(start[2])
        except:
            d = 0

        if attrs.has_key("cformat"):
            cal = RelLib.Date.calendar_names.index(attrs['cformat'])
        else:
            cal = RelLib.Date.CAL_GREGORIAN

        if attrs.has_key('type'):
            val = attrs['type']
            if val == "about":
                mod = RelLib.Date.MOD_ABOUT
            elif val == "after":
                mod = RelLib.Date.MOD_AFTER
            else:
                mod = RelLib.Date.MOD_BEFORE
        else:
            mod = RelLib.Date.MOD_NONE

        if attrs.has_key('quality'):
            val = attrs['quality']
            if val == 'estimated':
                qual = RelLib.Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = RelLib.Date.QUAL_CALCULATED
            else:
                qual = RelLib.Date.QUAL_NONE
        else:
            qual = RelLib.Date.QUAL_NONE
        
        dv.set(qual,mod,cal,(d,m,y,False))

    def start_datestr(self,attrs):
        if self.source_ref:
            dv = self.source_ref.get_date_object()
        elif self.ord:
            dv = self.ord.get_date_object()
        elif self.object:
            dv = self.object.get_date_object()
        elif self.address:
            dv = self.address.get_date_object()
        elif self.name:
            dv = self.name.get_date_object()
        else:
            dv = self.event.get_date_object()

        dv.set_as_text(attrs['val'])

    def start_created(self,attrs):
        if attrs.has_key('sources'):
            self.num_srcs = int(attrs['sources'])
        else:
            self.num_srcs = 0
        if attrs.has_key('places'):
            self.num_places = int(attrs['places'])
        else:
            self.num_places = 0

    def start_database(self,attrs):
        try:
            # This is a proper way to get the XML version
            xmlns = attrs.get('xmlns')
            self.version_string = xmlns.split('/')[4]
        except:
            # Before we had a proper DTD, the version was hard to determine
            # so we're setting it to 1.0.0
            self.version_string = '1.0.0'

    def start_pos(self,attrs):
        self.person.position = (int(attrs["x"]), int(attrs["y"]))

    def stop_attribute(self,*tag):
        self.attribute = None

    def stop_comment(self,tag):
        # Parse witnesses created by older gramps
        if tag.strip():
            self.witness_comment = tag
        else:
            self.witness_comment = ""

    def stop_witness(self,tag):
        # Parse witnesses created by older gramps
        if self.witness_comment:
            text = self.witness_comment
        elif tag.strip():
            text = tag
        else:
            text = None

        if text != None:
            note = RelLib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness comment: %s") % text)
            self.db.add_note(note,self.trans)
            self.event.add_note(note.handle)
        self.in_witness = False

    def stop_attr_type(self,tag):
        self.attribute.set_type(tag)

    def stop_attr_value(self,tag):
        self.attribute.set_value(tag)

    def stop_address(self,*tag):
        if self.person:
            self.person.add_address(self.address)
        elif self.repo:
            self.repo.add_address(self.address)
        self.address = None
        
    def stop_places(self,*tag):
        self.placeobj = None

    def stop_photo(self,*tag):
        self.photo = None

    def stop_ptitle(self,tag):
        self.placeobj.title = tag

    def stop_placeobj(self,*tag):
        if self.placeobj.title == "":
            loc = self.placeobj.get_main_location()
            self.placeobj.title = build_place_title(loc)

        if self.placeobj.title in self.place_names:
            self.placeobj.title += " [%s]" % self.placeobj.gramps_id

        self.db.commit_place(self.placeobj,self.trans,self.change)
        self.placeobj = None

    def stop_family(self,*tag):
        self.db.commit_family(self.family,self.trans,self.change)
        self.family = None
        
    def stop_type(self,tag):
        if self.event:
            # Event type
            self.event.type.set_from_xml_str(tag)
        elif self.repo:
            # Repository type
            self.repo.type.set_from_xml_str(tag)

    def stop_childref(self,tag):
        self.childref = None

    def stop_personref(self,tag):
        self.personref = None

    def stop_eventref(self,tag):
        self.eventref = None

    def stop_event(self,*tag):
        if self.family:
            ref = RelLib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(RelLib.EventRoleType.FAMILY)
            self.family.add_event_ref(ref)
        elif self.person:
            ref = RelLib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(RelLib.EventRoleType.PRIMARY)
            if (self.event.type == RelLib.EventType.BIRTH) \
                   and (self.person.get_birth_ref() == None):
                self.person.set_birth_ref(ref)
            elif (self.event.type == RelLib.EventType.DEATH) \
                     and (self.person.get_death_ref() == None):
                self.person.set_death_ref(ref)
            else:
                self.person.add_event_ref(ref)

        if self.event.get_description() == "" and \
               self.event.get_type() != RelLib.EventType.CUSTOM:
            if self.family:
                text = _event_family_str % {
                    'event_name' : str(self.event.get_type()),
                    'family' : Utils.family_name(self.family,self.db),
                    }
            elif self.person:
                text = _event_person_str % {
                    'event_name' : str(self.event.get_type()),
                    'person' : NameDisplay.displayer.display(self.person),
                    }
            else:
                text = u''
            self.event.set_description(text)

        self.db.commit_event(self.event,self.trans,self.change)
        self.event = None

    def stop_name(self,tag):
        if self.in_witness:
            # Parse witnesses created by older gramps
            note = RelLib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness name: %s") % tag)
            self.db.add_note(note,self.trans)
            self.event.add_note(note.handle)
        elif self.alt_name:
            # former aka tag -- alternate name
            if self.name.get_type() == "":
                self.name.set_type(RelLib.NameType.AKA)
            self.person.add_alternate_name(self.name)
        else:
            if self.name.get_type() == "":
                self.name.set_type(RelLib.NameType.BIRTH)
            self.person.set_primary_name (self.name)
        self.name = None

    def stop_rname(self,tag):
        # Repository name
        self.repo.name = tag

    def stop_ref(self,tag):
        # Parse witnesses created by older gramps
        person = self.find_person_by_gramps_id(self.map_gid(tag))
        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        event_ref = RelLib.EventRef()
        event_ref.ref = self.event.handle
        event_ref.role.set(RelLib.EventRoleType.WITNESS)
        person.event_ref_list.append(event_ref)
        self.db.commit_person(person,self.trans,self.change)

    def stop_place(self,tag):
        if self.placeobj == None:
            if self.place_map.has_key(tag):
                self.placeobj = self.place_map[tag]
            else:
                self.placeobj = RelLib.Place()
                self.placeobj.set_title(tag)
        if self.ord:
            self.ord.set_place_handle(self.placeobj.get_handle())
        elif self.object:
            self.object.set_place_handle(self.placeobj.get_handle())
        else:
            self.event.set_place_handle(self.placeobj.get_handle())
        self.db.commit_place(self.placeobj,self.trans,self.change)
        self.placeobj = None
        
    def stop_date(self,tag):
        if tag:
            if self.address:
                DateHandler.set_date(self.address,tag)
            else:
                DateHandler.set_date(self.event,tag)

    def stop_first(self,tag):
        self.name.set_first_name(tag)

    def stop_call(self,tag):
        self.name.set_call_name(tag)

    def stop_families(self,*tag):
        self.family = None

    def stop_person(self,*tag):
        self.db.commit_person(self.person,self.trans,self.change)
        self.person = None

    def stop_description(self,tag):
        self.event.description = tag

    def stop_cause(self,tag):
        # The old event's cause is now an attribute
        attr = RelLib.Attribute()
        attr.set_type(RelLib.AttributeType.CAUSE)
        attr.set_value(tag)
        self.event.add_attribute(attr)

    def stop_gender(self,tag):
        t = tag
        if t == "M":
            self.person.set_gender (RelLib.Person.MALE)
        elif t == "F":
            self.person.set_gender (RelLib.Person.FEMALE)
        else:
            self.person.set_gender (RelLib.Person.UNKNOWN)

    def stop_stitle(self,tag):
        self.source.title = tag

    def stop_sourceref(self,*tag):
        self.source_ref = None

    def stop_source(self,*tag):
        self.db.commit_source(self.source,self.trans,self.change)
        self.source = None

    def stop_sauthor(self,tag):
        self.source.author = tag

    def stop_phone(self,tag):
        self.address.phone = tag

    def stop_street(self,tag):
        self.address.street = tag

    def stop_city(self,tag):
        self.address.city = tag

    def stop_county(self,tag):
        self.address.county = tag

    def stop_state(self,tag):
        self.address.state = tag
        
    def stop_country(self,tag):
        self.address.country = tag

    def stop_postal(self,tag):
        self.address.set_postal_code(tag)

    def stop_spage(self,tag):
        self.source_ref.set_page(tag)

    def stop_lds_ord(self,*tag):
        self.ord = None

    def stop_spubinfo(self,tag):
        self.source.set_publication_info(tag)

    def stop_sabbrev(self,tag):
        self.source.set_abbreviation(tag)
        
    def stop_stext(self,tag):
        if self.use_p:
            self.use_p = 0
            note = fix_spaces(self.stext_list)
        else:
            note = tag
        self.source_ref.set_text(note)

    def stop_scomments(self,tag):
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.scomments_list)
        else:
            text = tag
        note = RelLib.Note()
        note.handle = Utils.create_id()
        note.set(text)
        self.db.add_note(note,self.trans)
        self.source_ref.add_note(note.handle)

    def stop_last(self,tag):
        if self.name:
            self.name.set_surname(tag)

    def stop_suffix(self,tag):
        if self.name:
            self.name.set_suffix(tag)

    def stop_patronymic(self,tag):
        if self.name:
            self.name.set_patronymic(tag)

    def stop_title(self,tag):
        if self.name:
            self.name.set_title(tag)

    def stop_nick(self,tag):
        if self.person:
            attr = RelLib.Attribute()
            attr.set_type(RelLib.AttributeType.NICKNAME)
            attr.set_value(tag)
            self.person.add_attribute(attr)

    def stop_note(self,tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.note_list)
        else:
            text = tag
        self.note.set(text)

        if self.address:
            self.address.add_note(self.note.handle)
        elif self.ord:
            self.ord.add_note(self.note.handle)
        elif self.attribute:
            self.attribute.add_note(self.note.handle)
        elif self.object:
            self.object.add_note(self.note.handle)
        elif self.objref:
            self.objref.add_note(self.note.handle)
        elif self.photo:
            self.photo.add_note(self.note.handle)
        elif self.name:
            self.name.add_note(self.note.handle)
        elif self.source:
            self.source.add_note(self.note.handle)
        elif self.event:
            self.event.add_note(self.note.handle)
        elif self.personref:
            self.personref.add_note(self.note.handle)
        elif self.person:
            self.person.add_note(self.note.handle)
        elif self.childref:
            self.childref.add_note(self.note.handle)
        elif self.family:
            self.family.add_note(self.note.handle)
        elif self.placeobj:
            self.placeobj.add_note(self.note.handle)
        elif self.eventref:
            self.eventref.add_note(self.note.handle)
        elif self.repo:
            self.repo.add_note(self.note.handle)
        elif self.reporef:
            self.reporef.add_note(self.note.handle)

        self.db.commit_note(self.note,self.trans,self.change)
        self.note = None

    def stop_research(self,tag):
        self.owner.set(self.resname, self.resaddr, self.rescity, self.resstate,
                       self.rescon, self.respos, self.resphone, self.resemail)

    def stop_resname(self,tag):
        self.resname = tag

    def stop_resaddr(self,tag):
        self.resaddr = tag

    def stop_rescity(self,tag):
        self.rescity = tag

    def stop_resstate(self,tag):
        self.resstate = tag

    def stop_rescountry(self,tag):
        self.rescon = tag

    def stop_respostal(self,tag):
        self.respos = tag

    def stop_resphone(self,tag):
        self.resphone = tag

    def stop_resemail(self,tag):
        self.resemail = tag

    def stop_ptag(self,tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(tag)
        elif self.in_stext:
            self.stext_list.append(tag)
        elif self.in_scomments:
            self.scomments_list.append(tag)

    def stop_aka(self,tag):
        self.person.add_alternate_name(self.name)
        if self.name.get_type() == "":
            self.name.set_type(RelLib.NameType.AKA)
        self.name = None

    def startElement(self,tag,attrs):
        self.func_list[self.func_index] = (self.func,self.tlist)
        self.func_index += 1
        self.tlist = []

        try:
            f,self.func = self.func_map[tag]
            if f:
                f(attrs)
        except KeyError:
            self.func_map[tag] = (None,None)
            self.func = None

    def endElement(self,tag):
        if self.func:
            self.func(''.join(self.tlist))
        self.func_index -= 1    
        self.func,self.tlist = self.func_list[self.func_index]
        
    def characters(self, data):
        if self.func:
            self.tlist.append(data)


def append_value(orig,val):
    if orig:
        return "%s, %s" % (orig,val)
    else:
        return val

def build_place_title(loc):
    "Builds a title from a location"
    value = ""
    if loc.parish:
        value = loc.parish
    if loc.city:
        value = append_value(value,loc.city)
    if loc.county:
        value = append_value(value,loc.county)
    if loc.state:
        value = append_value(value,loc.state)
    if loc.country:
        value = append_value(value,loc.country)
    return value

if __name__ == "__main__":
    import sys
    import hotshot#, hotshot.stats
    from GrampsDb import gramps_db_factory

    def callback(val):
        print val

    codeset = None

    db_class = gramps_db_factory(const.app_gramps)
    database = db_class()
    database.load("test.grdb",lambda x: None, mode="w")

    filename = os.path.normpath(sys.argv[1])
    basefile = os.path.dirname(filename)
    change = os.path.getmtime(filename)

    parser = GrampsParser(database,callback,basefile,change,filename)

    linecounter = LineParser(filename)
    lc = linecounter.get_count()

    xml_file = gzip.open(filename,"rb")

    if True:
        pr = hotshot.Profile('mystats.profile')
        print "Start"
        pr.runcall(parser.parse,xml_file,False,lc)
        print "Finished"
        pr.close()
##         print "Loading profile"
##         stats = hotshot.stats.load('mystats.profile')
##         print "done"
##         stats.strip_dirs()
##         stats.sort_stats('time','calls')
##         stats.print_stats(100)
    else:
        import time
        t = time.time()
        parser.parse(xml_file,False,lc)
        print time.time() - t

    xml_file.close()
