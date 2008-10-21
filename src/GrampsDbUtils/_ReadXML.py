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
from xml.parsers.expat import ExpatError, ParserCreate
from gettext import gettext as _
import re

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from QuestionDialog import ErrorDialog
import Mime
import gen.lib
import Utils
import DateHandler
from BasicUtils import name_displayer
from gen.db.dbconst import (PERSON_KEY, FAMILY_KEY, SOURCE_KEY, EVENT_KEY, 
                            MEDIA_KEY, PLACE_KEY, REPOSITORY_KEY, NOTE_KEY)
from BasicUtils import UpdateCallback
import _GrampsDbWriteXML
import const

#-------------------------------------------------------------------------
#
# Try to detect the presence of gzip
#
#-------------------------------------------------------------------------
try:
    import gzip
    GZIP_OK = True
except:
    GZIP_OK = False

PERSON_RE = re.compile(r"\s*\<person\s(.*)$")

CHILD_REL_MAP = {
    "Birth"     : gen.lib.ChildRefType(gen.lib.ChildRefType.BIRTH), 
    "Adopted"   : gen.lib.ChildRefType(gen.lib.ChildRefType.ADOPTED), 
    "Stepchild" : gen.lib.ChildRefType(gen.lib.ChildRefType.STEPCHILD), 
    "Sponsored" : gen.lib.ChildRefType(gen.lib.ChildRefType.SPONSORED), 
    "Foster"    : gen.lib.ChildRefType(gen.lib.ChildRefType.FOSTER), 
    "Unknown"   : gen.lib.ChildRefType(gen.lib.ChildRefType.UNKNOWN), 
    }

EVENT_FAMILY_STR = _("%(event_name)s of %(family)s")
EVENT_PERSON_STR = _("%(event_name)s of %(person)s")

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
# Must takes care of renaming media files according to their new IDs.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None, cl=0):

    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    change = os.path.getmtime(filename)
    parser = GrampsParser(database, callback, change)

    linecounter = LineParser(filename)
    line_cnt = linecounter.get_count()
    person_cnt = linecounter.get_person_count()
    
    read_only = database.readonly
    database.readonly = False
    
    xml_file = open_file(filename, cl)

    if xml_file is None or \
       version_is_valid(xml_file, cl) is False:
        if cl:
            sys.exit(1)
        else:
            return
        
    try:
        xml_file.seek(0)
        info = parser.parse(xml_file, line_cnt, person_cnt)
    except IOError, msg:
        if cl:
            print "Error reading %s" % filename
            print msg
            import traceback
            traceback.print_exc()
            sys.exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename, str(msg))
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

    database.readonly = read_only
    
    return info

##  TODO - WITH MEDIA PATH, IS THIS STILL NEEDED? 
##         BETTER LEAVE ALL RELATIVE TO NEW RELATIVE PATH
##   save_path is in .gramps/dbbase, no good place !
##    # copy all local images into <database>.images directory
##    db_dir = os.path.abspath(os.path.dirname(database.get_save_path()))
##    db_base = os.path.basename(database.get_save_path())
##    img_dir = os.path.join(db_dir, db_base)
##    first = not os.path.exists(img_dir)
##    
##    for m_id in database.get_media_object_handles():
##        mobject = database.get_object_from_handle(m_id)
##        oldfile = mobject.get_path()
##        if oldfile and not os.path.isabs(oldfile):
##            if first:
##                os.mkdir(img_dir)
##                first = 0
##            newfile = os.path.join(img_dir, oldfile)
##
##            try:
##                oldfilename = os.path.join(basefile, oldfile)
##                shutil.copyfile(oldfilename, newfile)
##                try:
##                    shutil.copystat(oldfilename, newfile)
##                except:
##                    pass
##                mobject.set_path(newfile)
##                database.commit_media_object(mobject, None, change)
##            except (IOError, OSError), msg:
##                ErrorDialog(_('Could not copy file'), str(msg))

#-------------------------------------------------------------------------
#
# Remove extraneous spaces
#
#-------------------------------------------------------------------------

def rs(text):
    return ' '.join(text.split())

def fix_spaces(text_list):
    return '\n'.join(map(rs, text_list))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------

class ImportInfo:
    """
    Class object that can hold information about the import
    """
    keyorder = [PERSON_KEY, FAMILY_KEY, SOURCE_KEY, EVENT_KEY, MEDIA_KEY, 
                PLACE_KEY, REPOSITORY_KEY, NOTE_KEY]
    key2data = {
            PERSON_KEY : 0,
            FAMILY_KEY : 1,
            SOURCE_KEY: 2, 
            EVENT_KEY: 3, 
            MEDIA_KEY: 4, 
            PLACE_KEY: 5, 
            REPOSITORY_KEY: 6, 
            NOTE_KEY: 7
            }
    
    def __init__(self):
        """
        Init of the import class.
        
        This creates the datastructures to hold info
        """
        self.data_mergeoverwrite = [{},{},{},{},{},{},{},{}]
        self.data_newobject = [0,0,0,0,0,0,0,0]
        self.data_relpath = False
        

    def add(self, category, key, obj):
        """
        Add info of a certain category. Key is one of the predefined keys,
        while obj is an object of which information will be extracted
        """
        if category == 'merge-overwrite':
            self.data_mergeoverwrite[self.key2data[key]][obj.handle] = \
                    self._extract_mergeinfo(key, obj)
        elif category == 'new-object':
            self.data_newobject[self.key2data[key]] += 1
        elif category == 'relative-path':
            self.data_relpath = True

    def _extract_mergeinfo(self, key, obj):
        """
        Extract info from obj about 'merge-overwrite', Key is one of the 
        predefined keys.
        """
        if key == PERSON_KEY:
            return _("  %(id)s - %(text)s\n") % {'id': obj.gramps_id, 
                        'text' : name_displayer.display(obj)
                        }
        elif key == FAMILY_KEY :
            return _("  Family %(id)s\n") % {'id': obj.gramps_id}
        elif key ==SOURCE_KEY:
            return _("  Source %(id)s\n") % {'id': obj.gramps_id}
        elif key == EVENT_KEY:
            return _("  Event %(id)s\n") % {'id': obj.gramps_id}
        elif key == MEDIA_KEY:
            return _("  Media Object %(id)s\n") % {'id': obj.gramps_id}
        elif key == PLACE_KEY:
            return _("  Place %(id)s\n") % {'id': obj.gramps_id}
        elif key == REPOSITORY_KEY:
            return _("  Repository %(id)s\n") % {'id': obj.gramps_id}
        elif key == NOTE_KEY:
            return _("  Note %(id)s\n") % {'id': obj.gramps_id}

    def info_text(self):
        """
        Construct an info message from the data in the class.
        """
        key2string = {
            PERSON_KEY      : _('  People: %d\n'),
            FAMILY_KEY      : _('  Families: %d\n'),
            SOURCE_KEY      : _('  Sources: %d\n'),
            EVENT_KEY       : _('  Events: %d\n'),
            MEDIA_KEY       : _('  Media Objects: %d\n'),
            PLACE_KEY       : _('  Places: %d\n'),
            REPOSITORY_KEY  : _('  Repositories: %d\n'),
            NOTE_KEY        : _('  Notes: %d\n'),
            }
        txt = _("Number of new objects imported:\n")
        for key in self.keyorder:
            txt += key2string[key] % self.data_newobject[self.key2data[key]]
        merged = False
        for key in self.keyorder:
            if self.data_mergeoverwrite[self.key2data[key]]:
                merged = True
                break
        if merged:
            txt += _("\n\nObjects merged-overwritten on import:\n")
            for key in self.keyorder:
                datakey = self.key2data[key]
                for handle in self.data_mergeoverwrite[datakey].keys():
                    txt += self.data_mergeoverwrite[datakey][handle]
        if self.data_relpath:
            txt += _("\nMedia objects with relative paths have been\n"
                     "imported. These paths are considered relative to\n"
                     "the media directory you can set in the preferences,\n"
                     "or, if not set, relative to the user's directory.\n"
                    )
        return txt

class LineParser:
    def __init__(self, filename):

        self.count = 0
        self.person_count = 0

        if GZIP_OK:
            use_gzip = 1
            try:
                f = gzip.open(filename, "r")
                f.read(1)
                f.close()
            except IOError, msg:
                use_gzip = 0
            except ValueError, msg:
                use_gzip = 1
        else:
            use_gzip = 0

        try:
            if use_gzip:
                ofile = gzip.open(filename, "rb")
            else:
                ofile = open(filename, "r")

            for line in ofile:
                self.count += 1
                if PERSON_RE.match(line):
                    self.person_count += 1

            ofile.close()
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

    def __init__(self, database, callback, change):
        UpdateCallback.__init__(self, callback)
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
        self.info = ImportInfo()
        self.all_abs = True
        cursor = database.get_place_cursor()
        data = cursor.next()
        while data:
            (handle, val) = data
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
        self.note_text = None
        self.note_tags = []
        self.in_witness = False
        self.db = database
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

        self.mediapath = ""

        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.lmap = {}
        self.media_file_map = {}

        # List of new name formats and a dict for remapping them
        self.name_formats  = []
        self.name_formats_map = {}
        self.taken_name_format_numbers = [num[0] 
                                          for num in self.db.name_formats]
        
        self.event = None
        self.eventref = None
        self.childref = None
        self.personref = None
        self.name = None
        self.home = None
        self.owner = gen.lib.Researcher()
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
            "address": (self.start_address, self.stop_address), 
            "addresses": (None, None), 
            "childlist": (None, None), 
            "aka": (self.start_name, self.stop_aka), 
            "attribute": (self.start_attribute, self.stop_attribute), 
            "attr_type": (None, self.stop_attr_type), 
            "attr_value": (None, self.stop_attr_value), 
            "bookmark": (self.start_bmark, None), 
            "bookmarks": (None, None), 
            "format": (self.start_format, None), 
            "name-formats": (None, None), 
            "child": (self.start_child, None), 
            "childof": (self.start_childof, None), 
            "childref": (self.start_childref, self.stop_childref), 
            "personref": (self.start_personref, self.stop_personref), 
            "city": (None, self.stop_city), 
            "county": (None, self.stop_county), 
            "country": (None, self.stop_country), 
            "comment": (None, self.stop_comment), 
            "created": (self.start_created, None), 
            "ref": (None, self.stop_ref), 
            "database": (self.start_database, self.stop_database), 
            "phone": (None, self.stop_phone), 
            "date": (None, self.stop_date), 
            "cause": (None, self.stop_cause), 
            "description": (None, self.stop_description), 
            "event": (self.start_event, self.stop_event), 
            "type": (None, self.stop_type), 
            "witness": (self.start_witness, self.stop_witness), 
            "eventref": (self.start_eventref, self.stop_eventref), 
            "data_item": (self.start_data_item, None), 
            "families": (None, self.stop_families), 
            "family": (self.start_family, self.stop_family), 
            "rel": (self.start_rel, None), 
            "region": (self.start_region, None),
            "father": (self.start_father, None), 
            "first": (None, self.stop_first), 
            "call": (None, self.stop_call), 
            "gender": (None, self.stop_gender), 
            "header": (None, None), 
            "last": (self.start_last, self.stop_last),
            "map": (self.start_namemap, None),
            "mediapath": (None, self.stop_mediapath),
            "mother": (self.start_mother, None), 
            "name": (self.start_name, self.stop_name),
            "namemaps": (None, None),
            "nick": (None, self.stop_nick), 
            "note": (self.start_note, self.stop_note), 
            "noteref": (self.start_noteref, None), 
            "p": (None, self.stop_ptag), 
            "parentin": (self.start_parentin, None), 
            "people": (self.start_people, self.stop_people), 
            "person": (self.start_person, self.stop_person), 
            "img": (self.start_photo, self.stop_photo), 
            "objref": (self.start_objref, self.stop_objref), 
            "object": (self.start_object, self.stop_object), 
            "file": (self.start_file, None), 
            "place": (self.start_place, self.stop_place), 
            "dateval": (self.start_dateval, None), 
            "daterange": (self.start_daterange, None), 
            "datespan": (self.start_datespan, None), 
            "datestr": (self.start_datestr, None), 
            "places": (None, self.stop_places), 
            "placeobj": (self.start_placeobj, self.stop_placeobj), 
            "ptitle": (None, self.stop_ptitle), 
            "location": (self.start_location, None), 
            "lds_ord": (self.start_lds_ord, self.stop_lds_ord), 
            "temple": (self.start_temple, None), 
            "status": (self.start_status, None), 
            "sealed_to": (self.start_sealed_to, None), 
            "coord": (self.start_coord, None), 
            "patronymic": (None, self.stop_patronymic), 
            "pos": (self.start_pos, None), 
            "postal": (None, self.stop_postal),
            "range": (self.start_range, None),
            "researcher": (None, self.stop_research), 
            "resname": (None, self.stop_resname ), 
            "resaddr": (None, self.stop_resaddr ), 
            "rescity": (None, self.stop_rescity ), 
            "resstate": (None, self.stop_resstate ), 
            "rescountry": (None, self.stop_rescountry), 
            "respostal": (None, self.stop_respostal), 
            "resphone": (None, self.stop_resphone), 
            "resemail": (None, self.stop_resemail), 
            "sauthor": (None, self.stop_sauthor), 
            "sabbrev": (None, self.stop_sabbrev), 
            "scomments": (None, self.stop_scomments), 
            "source": (self.start_source, self.stop_source), 
            "sourceref": (self.start_sourceref, self.stop_sourceref), 
            "sources": (None, None), 
            "spage": (None, self.stop_spage), 
            "spubinfo": (None, self.stop_spubinfo), 
            "state": (None, self.stop_state), 
            "stext": (None, self.stop_stext), 
            "stitle": (None, self.stop_stitle), 
            "street": (None, self.stop_street), 
            "suffix": (None, self.stop_suffix),
            "tag": (self.start_tag, None),
            "text": (None, self.stop_text),
            "title": (None, self.stop_title), 
            "url": (self.start_url, None), 
            "repository": (self.start_repo, self.stop_repo), 
            "reporef": (self.start_reporef, self.stop_reporef), 
            "rname": (None, self.stop_rname), 
        }

    def find_person_by_gramps_id(self, gramps_id):
        intid = self.gid2id.get(gramps_id)
        new = True
        if intid:
            person = self.db.get_person_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            person = gen.lib.Person()
            person.set_handle(intid)
            person.set_gramps_id(gramps_id)
            self.db.add_person(person, self.trans)
            #set correct change time
            self.db.commit_person(person, self.trans, self.change)
            self.gid2id[gramps_id] = intid
        return person, new

    def find_family_by_gramps_id(self, gramps_id):
        intid = self.gid2fid.get(gramps_id)
        new = True
        if intid:
            family = self.db.get_family_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            family = gen.lib.Family()
            family.set_handle(intid)
            family.set_gramps_id(gramps_id)
            self.db.add_family(family, self.trans)
            self.db.commit_family(family, self.trans, self.change)
            self.gid2fid[gramps_id] = intid
        return family, new

    def find_event_by_gramps_id(self, gramps_id):
        intid = self.gid2eid.get(gramps_id)
        new = True
        if intid:
            event = self.db.get_event_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            event = gen.lib.Event()
            event.set_handle(intid)
            event.set_gramps_id(gramps_id)
            self.db.add_event(event, self.trans)
            self.db.commit_event(event, self.trans, self.change)
            self.gid2eid[gramps_id] = intid
        return event, new

    def find_place_by_gramps_id(self, gramps_id):
        intid = self.gid2pid.get(gramps_id)
        new = True
        if intid:
            place = self.db.get_place_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            place = gen.lib.Place()
            place.set_handle(intid)
            place.set_gramps_id(gramps_id)
            self.db.add_place(place, self.trans)
            self.db.commit_place(place, self.trans, self.change)
            self.gid2pid[gramps_id] = intid
        return place, new

    def find_source_by_gramps_id(self, gramps_id):
        intid = self.gid2sid.get(gramps_id)
        new = True
        if intid:
            source = self.db.get_source_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            source = gen.lib.Source()
            source.set_handle(intid)
            source.set_gramps_id(gramps_id)
            self.db.add_source(source, self.trans)
            self.db.commit_source(source, self.trans, self.change)
            self.gid2sid[gramps_id] = intid
        return source, new

    def find_object_by_gramps_id(self, gramps_id):
        intid = self.gid2oid.get(gramps_id)
        new = True
        if intid:
            obj = self.db.get_object_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            obj = gen.lib.MediaObject()
            obj.set_handle(intid)
            obj.set_gramps_id(gramps_id)
            self.db.add_object(obj, self.trans)
            self.db.commit_media_object(obj, self.trans, self.change)
            self.gid2oid[gramps_id] = intid
        return obj, new

    def find_repository_by_gramps_id(self, gramps_id):
        intid = self.gid2rid.get(gramps_id)
        new = True
        if intid:
            repo = self.db.get_repository_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            repo = gen.lib.Repository()
            repo.set_handle(intid)
            repo.set_gramps_id(gramps_id)
            self.db.add_repository(repo, self.trans)
            self.db.commit_repository(repo, self.trans, self.change)
            self.gid2rid[gramps_id] = intid
        return repo, new

    def find_note_by_gramps_id(self, gramps_id):
        intid = self.gid2nid.get(gramps_id)
        new = True
        if intid:
            note = self.db.get_note_from_handle(intid)
            new = False
        else:
            intid = Utils.create_id()
            note = gen.lib.Note()
            note.set_handle(intid)
            note.set_gramps_id(gramps_id)
            self.db.add_note(note, self.trans)
            self.db.commit_note(note, self.trans, self.change)
            self.gid2nid[gramps_id] = intid
        return note, new

    def map_gid(self, gramps_id):
        if not self.idswap.get(gramps_id):
            if self.db.has_gramps_id(PERSON_KEY, gramps_id):
                self.idswap[gramps_id] = self.db.find_next_person_gramps_id()
            else:
                self.idswap[gramps_id] = gramps_id
        return self.idswap[gramps_id]

    def map_fid(self, gramps_id):
        if not self.fidswap.get(gramps_id):
            if self.db.has_gramps_id(FAMILY_KEY, gramps_id):
                self.fidswap[gramps_id] = self.db.find_next_family_gramps_id()
            else:
                self.fidswap[gramps_id] = gramps_id
        return self.fidswap[gramps_id]

    def map_eid(self, gramps_id):
        if not self.eidswap.get(gramps_id):
            if self.db.has_gramps_id(EVENT_KEY, gramps_id):
                self.eidswap[gramps_id] = self.db.find_next_event_gramps_id()
            else:
                self.eidswap[gramps_id] = gramps_id
        return self.eidswap[gramps_id]

    def map_pid(self, gramps_id):
        if not self.pidswap.get(gramps_id):
            if self.db.has_gramps_id(PLACE_KEY, gramps_id):
                self.pidswap[gramps_id] = self.db.find_next_place_gramps_id()
            else:
                self.pidswap[gramps_id] = gramps_id
        return self.pidswap[gramps_id]

    def map_sid(self, gramps_id):
        if not self.sidswap.get(gramps_id):
            if self.db.has_gramps_id(SOURCE_KEY, gramps_id):
                self.sidswap[gramps_id] = self.db.find_next_source_gramps_id()
            else:
                self.sidswap[gramps_id] = gramps_id
        return self.sidswap[gramps_id]

    def map_oid(self, gramps_id):
        if not self.oidswap.get(gramps_id):
            if self.db.has_gramps_id(MEDIA_KEY, gramps_id):
                self.oidswap[gramps_id] = self.db.find_next_object_gramps_id()
            else:
                self.oidswap[gramps_id] = gramps_id
        return self.oidswap[gramps_id]

    def map_rid(self, gramps_id):
        if not self.ridswap.get(gramps_id):
            if self.db.has_gramps_id(REPOSITORY_KEY, gramps_id):
                self.ridswap[gramps_id] = self.db.find_next_repository_gramps_id()
            else:
                self.ridswap[gramps_id] = gramps_id
        return self.ridswap[gramps_id]

    def map_nid(self, gramps_id):
        if not self.nidswap.get(gramps_id):
            if self.db.has_gramps_id(NOTE_KEY, gramps_id):
                self.nidswap[gramps_id] = self.db.find_next_note_gramps_id()
            else:
                self.nidswap[gramps_id] = gramps_id
        return self.nidswap[gramps_id]

    def parse(self, ifile, linecount=0, personcount=0):
        if personcount < 1000:
            no_magic = True
        else:
            no_magic = False
        self.trans = self.db.transaction_begin("", batch=True, no_magic=no_magic)
        self.set_total(linecount)

        self.db.disable_signals()

        self.p = ParserCreate()
        self.p.StartElementHandler = self.startElement
        self.p.EndElementHandler = self.endElement
        self.p.CharacterDataHandler = self.characters
        self.p.ParseFile(ifile)

        if len(self.name_formats) > 0:
            # add new name formats to the existing table
            self.db.name_formats += self.name_formats
            # Register new formats
            name_displayer.set_name_format(self.db.name_formats)

        self.db.set_researcher(self.owner)
        if self.home is not None:
            person = self.db.get_person_from_handle(self.home)
            self.db.set_default_person_handle(person.handle)

        #set media path, this should really do some parsing to convert eg
        # windows path to unix ?
        if self.mediapath:
            oldpath = self.db.get_mediapath()
            if not oldpath:
                self.db.set_mediapath(self.mediapath)
            elif not oldpath == self.mediapath:
                ErrorDialog(_("Could not change media path"), 
                    _("The opened file has media path %s, which conflicts with"
                      " the media path of the family tree you import into. "
                      "The original media path has been retained. Copy the "
                      "files to a correct directory or change the media "
                      "path in the Preferences."
                     ) % self.mediapath )

        for key in self.func_map.keys():
            del self.func_map[key]
        del self.func_map
        del self.func_list
        del self.p
        self.db.transaction_commit(self.trans, _("GRAMPS XML import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        return self.info

    def start_lds_ord(self, attrs):
        self.ord = gen.lib.LdsOrd()
        self.ord.set_type_from_xml(attrs['type'])
        self.ord.private = bool(attrs.get("priv"))
        if self.person:
            self.person.lds_ord_list.append(self.ord)
        elif self.family:
            self.family.lds_ord_list.append(self.ord)

    def start_temple(self, attrs):
        self.ord.set_temple(attrs['val'])

    def start_data_item(self, attrs):
        self.source.set_data_item(attrs['key'], attrs['value'])

    def start_status(self, attrs):
        try:
            # old xml with integer statuses
            self.ord.set_status(int(attrs['val']))
        except ValueError:
            # string
            self.ord.set_status_from_xml(attrs['val'])

    def start_sealed_to(self, attrs):
        try:
            handle = attrs['hlink'].replace('_', '')
            self.db.check_family_from_handle(handle, self.trans)
        except KeyError:
            gramps_id = self.map_fid(attrs['ref'])
            family = self.find_family_by_gramps_id(gramps_id)
            handle = family.handle
        self.ord.set_family_handle(handle)
        
    def start_place(self, attrs):
        """A reference to a place in an object: event or lds_ord
        """
        try:
            handle = attrs['hlink'].replace('_', '')
            self.db.check_place_from_handle(handle, self.trans, 
                                            set_gid = False)
        except KeyError:
            #legacy, before  hlink there was ref
            gramps_id = self.map_pid(attrs['ref'])
            place, new = self.find_place_by_gramps_id(gramps_id)
            handle = place.handle
        
        if self.ord:
            self.ord.set_place_handle(handle)
        elif self.object:
            self.object.set_place_handle(handle)
        else:
            self.event.set_place_handle(handle)
        
    def start_placeobj(self, attrs):
        gramps_id = self.map_pid(attrs['id'])
        try:
            self.placeobj, new = self.db.find_place_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.placeobj.set_gramps_id(gramps_id)
        except KeyError:
            self.placeobj, new = self.find_place_by_gramps_id(gramps_id)
            
        self.placeobj.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.placeobj.change = int(attrs.get('change',self.change))
            self.info.add('new-object', PLACE_KEY, self.placeobj)
        else:
            self.placeobj.change = self.change
            self.info.add('merge-overwrite', PLACE_KEY, self.placeobj)
        
        # GRAMPS LEGACY: title in the placeobj tag
        self.placeobj.title = attrs.get('title', '')
        self.locations = 0
        self.update(self.p.CurrentLineNumber)
            
    def start_location(self, attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""
        
        loc = gen.lib.Location()
        loc.phone = attrs.get('phone', '')
        loc.postal = attrs.get('postal', '')
        loc.city = attrs.get('city', '')
        loc.street = attrs.get('street', '')
        loc.parish = attrs.get('parish', '')
        loc.state = attrs.get('state', '')
        loc.county = attrs.get('county', '')
        loc.country = attrs.get('country', '')
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
            self.locations = self.locations + 1

    def start_witness(self, attrs):
        # Parse witnesses created by older gramps
        self.in_witness = True
        self.witness_comment = ""
        if 'name' in attrs:
            note = gen.lib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness name: %s") % attrs['name'])
            note.type.set(gen.lib.NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            #set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add('new-object', NOTE_KEY, note)
            self.event.add_note(note.handle)
            return

        try:
            handle = attrs['hlink'].replace('_', '')
            person, new = self.db.find_person_from_handle(handle, self.trans)
        except KeyError:
            if 'ref' in attrs:
                person, new = self.find_person_by_gramps_id(
                                    self.map_gid(attrs["ref"]))
            else:
                person = None

        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        if person:
            event_ref = gen.lib.EventRef()
            event_ref.ref = self.event.handle
            event_ref.role.set(gen.lib.EventRoleType.WITNESS)
            person.event_ref_list.append(event_ref)
            self.db.commit_person(person, self.trans, self.change)
        
    def start_coord(self, attrs):
        self.placeobj.lat = attrs.get('lat', '')
        self.placeobj.long = attrs.get('long', '')

    def start_event(self, attrs):
        if self.person or self.family:
            # GRAMPS LEGACY: old events that were written inside
            # person or family objects.
            self.event = gen.lib.Event()
            self.event.handle = Utils.create_id()
            self.event.type = gen.lib.EventType()
            self.event.type.set_from_xml_str(attrs['type'])
            self.db.add_event(self.event, self.trans)
            #set correct change time
            self.db.commit_event(self.event, self.trans, self.change)
            self.info.add('new-object', EVENT_KEY, self.event)
        else:
            # This is new event, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            gramps_id = self.map_eid(attrs["id"])
            try:
                self.event, new = self.db.find_event_from_handle(
                    attrs['handle'].replace('_', ''), self.trans)
                self.event.gramps_id = gramps_id
            except KeyError:
                self.event, new = self.find_event_by_gramps_id(gramps_id)
            self.event.private = bool(attrs.get("priv"))
            if new:
                #keep change time from xml file
                self.event.change = int(attrs.get('change',self.change))
                self.info.add('new-object', EVENT_KEY, self.event)
            else:
                self.event.change = self.change
                self.info.add('merge-overwrite', EVENT_KEY, self.event)

    def start_eventref(self, attrs):
        self.eventref = gen.lib.EventRef()
        self.eventref.ref = attrs['hlink'].replace('_', '')
        self.eventref.private = bool(attrs.get('priv'))
        if 'role' in attrs:
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
            if (event.type == gen.lib.EventType.BIRTH) \
                   and (self.eventref.role == gen.lib.EventRoleType.PRIMARY) \
                   and (self.person.get_birth_ref() is None):
                self.person.set_birth_ref(self.eventref)
            elif (event.type == gen.lib.EventType.DEATH) \
                     and (self.eventref.role == gen.lib.EventRoleType.PRIMARY) \
                     and (self.person.get_death_ref() is None):
                self.person.set_death_ref(self.eventref)
            else:
                self.person.add_event_ref(self.eventref)

    def start_attribute(self, attrs):
        self.attribute = gen.lib.Attribute()
        self.attribute.private = bool(attrs.get("priv"))
        self.attribute.type = gen.lib.AttributeType()
        if 'type' in attrs:
            self.attribute.type.set_from_xml_str(attrs["type"])
        self.attribute.value = attrs.get("value", '')
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

    def start_address(self, attrs):
        self.address = gen.lib.Address()
        self.address.private = bool(attrs.get("priv"))

    def start_bmark(self, attrs):
        target = attrs.get('target')
        if not target:
            # Old XML. Can be either handle or id reference
            # and this is guaranteed to be a person bookmark
            try:
                handle = attrs['hlink'].replace('_', '')
                self.db.check_person_from_handle(handle, self.trans)
            except KeyError:
                gramps_id = self.map_gid(attrs["ref"])
                person, new = self.find_person_by_gramps_id(gramps_id)
                handle = person.handle
            self.db.bookmarks.append(handle)
            return

        # This is new XML, so we are guaranteed to have a handle ref
        handle = attrs['hlink'].replace('_', '')
        # Due to pre 2.2.9 bug, bookmarks might be handle of other object
        # Make sure those are filtered out.
        # Bookmarks are at end, so all handle must exist before we do bookmrks
        if target == 'person':
            if (self.db.get_person_from_handle(handle) is not None
                    and handle not in self.db.bookmarks.get() ):
                self.db.bookmarks.append(handle)
        elif target == 'family':
            if (self.db.get_family_from_handle(handle) is not None
                    and handle not in self.db.family_bookmarks.get() ):
                self.db.family_bookmarks.append(handle)
        elif target == 'event':
            if (self.db.get_event_from_handle(handle) is not None
                    and handle not in self.db.event_bookmarks.get() ):
                self.db.event_bookmarks.append(handle)
        elif target == 'source':
            if (self.db.get_source_from_handle(handle) is not None
                    and handle not in self.db.source_bookmarks.get() ):
                self.db.source_bookmarks.append(handle)
        elif target == 'place':
            if (self.db.get_place_from_handle(handle) is not None
                    and handle not in self.db.place_bookmarks.get() ):
                self.db.place_bookmarks.append(handle)
        elif target == 'media':
            if (self.db.get_object_from_handle(handle) is not None
                    and handle not in self.db.media_bookmarks.get() ):
                self.db.media_bookmarks.append(handle)
        elif target == 'repository':
            if (self.db.get_repository_from_handle(handle) 
                    is not None and handle not in self.db.repo_bookmarks.get()):
                self.db.repo_bookmarks.append(handle)
        elif target == 'note':
            if (self.db.get_note_from_handle(handle) is not None
                    and handle not in self.db.note_bookmarks.get() ):
                self.db.note_bookmarks.append(handle)

    def start_format(self, attrs):
        number = int(attrs['number'])
        name = attrs['name']
        fmt_str = attrs['fmt_str']
        active = bool(attrs.get('active', True))

        if number in self.taken_name_format_numbers:
            number = self.remap_name_format(number)

        self.name_formats.append((number, name, fmt_str, active))

    def remap_name_format(self, old_number):
        if old_number in self.name_formats_map: # This should not happen
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
        
    def start_person(self, attrs):
        self.update(self.p.CurrentLineNumber)
        new_id = self.map_gid(attrs['id'])
        try:
            self.person, new = self.db.find_person_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.person.set_gramps_id(new_id)
        except KeyError:
            self.person, new = self.find_person_by_gramps_id(new_id)

        self.person.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.person.change = int(attrs.get('change',self.change))
            self.info.add('new-object', PERSON_KEY, self.person)
        else:
            self.person.change = self.change
            self.info.add('merge-overwrite', PERSON_KEY, self.person)
        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.person.marker.set(gen.lib.MarkerType.COMPLETE)
        else:
            self.person.marker.set_from_xml_str(attrs.get("marker", ''))

    def start_people(self, attrs):
        if 'home' in attrs:
            self.home = attrs['home'].replace('_', '')

    def start_father(self, attrs):
        try:
            handle = attrs['hlink'].replace('_', '')
            #all persons exist before father tag is encountered
            self.db.check_person_from_handle(handle, self.trans)
        except KeyError:
            person, new = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle
        self.family.set_father_handle(handle)

    def start_mother(self, attrs):
        try:
            handle = attrs['hlink'].replace('_', '')
            #all persons exist before mother tag is encountered
            self.db.check_person_from_handle(handle, self.trans)
        except KeyError:
            person, new = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle
        self.family.set_mother_handle(handle)
    
    def start_child(self, attrs):
        try:
            handle = attrs['hlink'].replace('_', '')
            #all persons exist before child tag is encountered
            self.db.check_person_from_handle(handle, self.trans)
        except KeyError:
            person, new = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
            handle = person.handle

        # Here we are handling the old XML, in which
        # frel and mrel belonged to the "childof" tag
        # If that were the case then childref_map has the childref ready
        if (self.family.handle, handle) in self.childref_map:
            self.family.add_child_ref(
                self.childref_map[(self.family.handle, handle)])

    def start_childref(self, attrs):
        # Here we are handling the new XML, in which frel and mrel
        # belong to the "childref" tag under family.
        self.childref = gen.lib.ChildRef()
        self.childref.ref = attrs['hlink'].replace('_', '')
        self.childref.private = bool(attrs.get('priv'))

        mrel = gen.lib.ChildRefType()
        if attrs.get('mrel'):
            mrel.set_from_xml_str(attrs['mrel'])
        frel = gen.lib.ChildRefType()
        if attrs.get('frel'):
            frel.set_from_xml_str(attrs['frel'])

        if not mrel.is_default():
            self.childref.set_mother_relation(mrel)
        if not frel.is_default():
            self.childref.set_father_relation(frel)
        self.family.add_child_ref(self.childref)

    def start_personref(self, attrs):
        self.personref = gen.lib.PersonRef()
        self.personref.ref = attrs['hlink'].replace('_', '')
        self.personref.private = bool(attrs.get('priv'))
        self.personref.rel = attrs['rel']
        self.person.add_person_ref(self.personref)

    def start_url(self, attrs):
        if "href" not in attrs:
            return
        url = gen.lib.Url()
        url.path = attrs["href"]
        url.set_description(attrs.get("description", ''))
        url.private = bool(attrs.get('priv'))
        url.type.set_from_xml_str(attrs.get('type', ''))
        if self.person:
            self.person.add_url(url)
        elif self.placeobj:
            self.placeobj.add_url(url)
        elif self.repo:
            self.repo.add_url(url)

    def start_family(self, attrs):
        self.update(self.p.CurrentLineNumber)
        gramps_id = self.map_fid(attrs["id"])
        try:
            self.family, new = self.db.find_family_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.family.set_gramps_id(gramps_id)
        except KeyError:
            self.family, new = self.find_family_by_gramps_id(gramps_id)
        
        self.family.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.family.change = int(attrs.get('change',self.change))
            self.info.add('new-object', FAMILY_KEY, self.family)
        else:
            self.family.change = self.change
            self.info.add('merge-overwrite', FAMILY_KEY, self.family)
        
        # GRAMPS LEGACY: the type now belongs to <rel> tag
        # Here we need to support old format of <family type="Married">
        if 'type' in attrs:
            self.family.type.set_from_xml_str(attrs["type"])
                
        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.family.marker.set(gen.lib.MarkerType.COMPLETE)
        else:
            self.family.marker.set_from_xml_str(attrs.get("marker", ''))

    def start_rel(self, attrs):
        if 'type' in attrs:
            self.family.type.set_from_xml_str(attrs["type"])

    def start_file(self, attrs):
        self.object.mime = attrs['mime']
        if 'description' in attrs:
            self.object.desc = attrs['description']
        else:
            self.object.desc = ""
        #keep value of path, no longer make absolute paths on import
        src = attrs["src"]
        if src:
            self.object.path = src
            if self.all_abs and not os.path.isabs(src):
                self.all_abs = False
                self.info.add('relative-path', None, None)

    def start_childof(self, attrs):
        try:
            handle = attrs["hlink"].replace('_', '')
            self.db.check_family_from_handle(handle, self.trans,
                                             set_gid = False)
        except KeyError:
            family, new = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
            handle = family.handle

        # Here we are handling the old XML, in which
        # frel and mrel belonged to the "childof" tag
        mrel = gen.lib.ChildRefType()
        frel = gen.lib.ChildRefType()
        if 'mrel' in attrs:
            mrel.set_from_xml_str(attrs['mrel'])
        if 'frel' in attrs:
            frel.set_from_xml_str(attrs['frel'])

        childref = gen.lib.ChildRef()
        childref.ref = self.person.handle
        if not mrel.is_default():
            childref.set_mother_relation(mrel)
        if not frel.is_default():
            childref.set_father_relation(frel)
        self.childref_map[(handle, self.person.handle)] = childref
        self.person.add_parent_family_handle(handle)

    def start_parentin(self, attrs):
        try:
            handle = attrs["hlink"].replace('_', '')
            self.db.check_family_from_handle(handle, self.trans,
                                             set_gid = False)
        except KeyError:
            family, new = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
            handle = family.handle
        self.person.add_family_handle(handle)

    def start_name(self, attrs):
        if not self.in_witness:
            self.name = gen.lib.Name()
            name_type = attrs['type']
            # Mapping "Other Name" from gramps 2.0.x to Unknown
            if (self.version_string=='1.0.0') and (name_type=='Other Name'):
                self.name.set_type(gen.lib.NameType.UNKNOWN)
            else:
                self.name.type.set_from_xml_str(name_type)
            self.name.private = bool(attrs.get("priv"))
            self.alt_name = bool(attrs.get("alt"))
            try:
                sort_as = int(attrs["sort"])
                display_as = int(attrs["display"])

                # check if these pointers need to be remapped
                # and set the name attributes
                if sort_as in self.name_formats_map:
                    self.name.sort_as = self.name_formats_map[sort_as]
                else:
                    self.name.sort_as = sort_as
                if display_as in self.name_formats_map:
                    self.name.sort_as = self.name_formats_map[display_as]
                else:
                    self.name_display_as = display_as
            except KeyError:
                pass

    def start_namemap(self, attrs):
        type = attrs.get('type')
        key = attrs['key']
        value = attrs['value']
        if type == 'group_as':
            if self.db.has_name_group_key(key) :
                present = self.db.get_name_group_mapping(key)
                if not value == present:
                    msg = _("Your family tree groups name %s together"
                            " with %s, did not change this grouping to %s") % (
                                                        key, present, value)
                    self.errmsg(msg)
            else:
                self.db.set_name_group_mapping(key, value)

    def start_last(self, attrs):
        self.name.prefix = attrs.get('prefix', '')
        self.name.group_as = attrs.get('group', '')
        
    def start_tag(self, attrs):
        tagtype = gen.lib.StyledTextTagType()
        tagtype.set_from_xml_str(attrs['name'])
        
        try:
            val = attrs['value']
            tagvalue = gen.lib.StyledTextTagType.STYLE_TYPE[int(tagtype)](val)
        except KeyError:
            tagvalue = None
        except ValueError:
            return
        
        self.note_tags.append(gen.lib.StyledTextTag(tagtype, tagvalue))
    
    def start_range(self, attrs):
        self.note_tags[-1].ranges.append((int(attrs['start']),
                                          int(attrs['end'])))
        
    def start_note(self, attrs):
        self.in_note = 0
        if 'handle' in attrs:
            # This is new note, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            gramps_id = self.map_nid(attrs["id"])
            try:
                self.note, new = self.db.find_note_from_handle(
                    attrs['handle'].replace('_', ''), self.trans)
                self.note.gramps_id = gramps_id
            except KeyError:
                self.note, new = self.find_note_by_gramps_id(gramps_id)
            self.note.private = bool(attrs.get("priv"))
            if new:
                #keep change time from xml file
                self.note.change = int(attrs.get('change',self.change))
                self.info.add('new-object', NOTE_KEY, self.note)
            else:
                self.note.change = self.change
                self.info.add('merge-overwrite', NOTE_KEY, self.note)
            self.note.format = int(attrs.get('format', gen.lib.Note.FLOWED))
            self.note.type.set_from_xml_str(attrs['type'])
            
            # Since StyledText was introduced (XML v1.3.0) the clear text
            # part of the note is moved between <text></text> tags.
            # To catch the different versions here we reset the note_text
            # variable. It will be checked in stop_note() then.
            self.note_text = None
            self.note_tags = []
        else:
            # GRAMPS LEGACY: old notes that were written inside other objects
            # We need to create a top-level note, it's type depends on 
            #   the caller object, and inherits privacy from caller object
            # On stop_note the reference to this note will be added
            self.note = gen.lib.Note()
            self.note.handle = Utils.create_id()
            self.note.format = int(attrs.get('format', gen.lib.Note.FLOWED))
            # The order in this long if-then statement should reflect the
            # DTD: most deeply nested elements come first.
            if self.source_ref:
                self.note.type.set(gen.lib.NoteType.SOURCEREF)
                self.note.private = self.source_ref.private
            elif self.address:
                self.note.type.set(gen.lib.NoteType.ADDRESS)
                self.note.private = self.address.private
            elif self.ord:
                self.note.type.set(gen.lib.NoteType.LDS)
                self.note.private = self.ord.private
            elif self.attribute:
                self.note.type.set(gen.lib.NoteType.ATTRIBUTE)
                self.note.private = self.attribute.private
            elif self.object:
                self.note.type.set(gen.lib.NoteType.MEDIA)
                self.note.private = self.object.private
            elif self.objref:
                self.note.type.set(gen.lib.NoteType.MEDIAREF)
                self.note.private = self.objref.private
            elif self.photo:
                self.note.type.set(gen.lib.NoteType.MEDIA)
                self.note.private = self.photo.private
            elif self.name:
                self.note.type.set(gen.lib.NoteType.PERSONNAME)
                self.note.private = self.name.private
            elif self.eventref:
                self.note.type.set(gen.lib.NoteType.EVENTREF)
                self.note.private = self.eventref.private
            elif self.reporef:
                self.note.type.set(gen.lib.NoteType.REPOREF)
                self.note.private = self.reporef.private
            elif self.source:
                self.note.type.set(gen.lib.NoteType.SOURCE)
                self.note.private = self.source.private
            elif self.event:
                self.note.type.set(gen.lib.NoteType.EVENT)
                self.note.private = self.event.private
            elif self.personref:
                self.note.type.set(gen.lib.NoteType.ASSOCIATION)
                self.note.private = self.personref.private
            elif self.person:
                self.note.type.set(gen.lib.NoteType.PERSON)
                self.note.private = self.person.private
            elif self.childref:
                self.note.type.set(gen.lib.NoteType.CHILDREF)
                self.note.private = self.childref.private
            elif self.family:
                self.note.type.set(gen.lib.NoteType.FAMILY)
                self.note.private = self.family.private
            elif self.placeobj:
                self.note.type.set(gen.lib.NoteType.PLACE)
                self.note.private = self.placeobj.private
            elif self.repo:
                self.note.type.set(gen.lib.NoteType.REPO)
                self.note.private = self.repo.private
 
            self.db.add_note(self.note, self.trans)
            #set correct change time
            self.db.commit_note(self.note, self.trans, self.change)
            self.info.add('new-object', NOTE_KEY, self.note)

    def start_noteref(self, attrs):
        handle = attrs['hlink'].replace('_', '')
        self.db.check_note_from_handle(handle, self.trans, set_gid = False)

        # The order in this long if-then statement should reflect the
        # DTD: most deeply nested elements come first.
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
        elif self.eventref:
            self.eventref.add_note(handle)
        elif self.reporef:
            self.reporef.add_note(handle)
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
        elif self.repo:
            self.repo.add_note(handle)

    def start_sourceref(self, attrs):
        self.source_ref = gen.lib.SourceRef()
        try:
            handle = attrs["hlink"].replace('_', '')
            #create source object to obtain handle, gid is set in start_source
            self.db.check_source_from_handle(handle, self.trans,
                                             set_gid = False)
        except KeyError:
            source, new = self.find_source_by_gramps_id(self.map_sid(attrs["ref"]))
            handle = source.handle

        self.source_ref.ref = handle
        self.source_ref.confidence = int(attrs.get("conf", self.conf))
        self.source_ref.private = bool(attrs.get("priv"))
        
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

    def start_source(self, attrs):
        self.update(self.p.CurrentLineNumber)
        gramps_id = self.map_sid(attrs["id"]) #avoid double id's on import
        try:
            self.source, new = self.db.find_source_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.source.set_gramps_id(gramps_id)
        except KeyError:
            self.source, new = self.find_source_by_gramps_id(gramps_id)
        self.source.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.source.change = int(attrs.get('change',self.change))
            self.info.add('new-object', SOURCE_KEY, self.source)
        else:
            self.source.change = self.change
            self.info.add('merge-overwrite', SOURCE_KEY, self.source)

    def start_reporef(self, attrs):
        self.reporef = gen.lib.RepoRef()
        try:
            handle = attrs['hlink'].replace('_', '')
            self.db.check_repository_from_handle(handle, self.trans,
                                                 set_gid = False)
        except KeyError:
            repo, new = self.find_repository_by_gramps_id(self.map_rid(attrs['ref']))
            handle = repo.handle
        
        self.reporef.ref = handle
        self.reporef.call_number = attrs.get('callno', '')
        self.reporef.media_type.set_from_xml_str(attrs['medium'])
        self.reporef.private = bool(attrs.get("priv"))
        # we count here on self.source being available
        # reporefs can only be found within source
        self.source.add_repo_reference(self.reporef)

    def start_objref(self, attrs):
        self.objref = gen.lib.MediaRef()
        try:
            handle = attrs['hlink'].replace('_', '')
            self.db.check_object_from_handle(handle, self.trans,
                                             set_gid = False)
        except KeyError:
            obj, new = self.find_object_by_gramps_id(self.map_oid(attrs['ref']))
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

    def start_region(self,attrs):
        rect = (int(attrs.get('corner1_x')),
                int(attrs.get('corner1_y')),
                int(attrs.get('corner2_x')),
                int(attrs.get('corner2_y')) )
        self.objref.set_rectangle(rect)

    def start_object(self, attrs):
        gramps_id = self.map_oid(attrs['id'])
        try:
            self.object, new = self.db.find_object_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.object.set_gramps_id(gramps_id)
        except KeyError:
            self.object, new = self.find_object_by_gramps_id(gramps_id)

        self.object.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.object.change = int(attrs.get('change',self.change))
            self.info.add('new-object', MEDIA_KEY, self.object)
        else:
            self.object.change = self.change
            self.info.add('merge-overwrite', MEDIA_KEY, self.object)

        # GRAMPS LEGACY: src, mime, and description attributes
        # now belong to the <file> tag. Here we are supporting
        # the old format of <object src="blah"...>
        self.object.mime = attrs.get('mime', '')
        self.object.desc = attrs.get('description', '')
        src = attrs.get("src", '')
        if src:
            self.object.path = src

    def start_repo(self, attrs):
        gramps_id = self.map_rid(attrs['id'])
        try:
            self.repo, new = self.db.find_repository_from_handle(
                attrs['handle'].replace('_', ''), self.trans)
            self.repo.set_gramps_id(gramps_id)
        except KeyError:
            self.repo, new = self.find_repository_by_gramps_id(gramps_id)
        
        self.repo.private = bool(attrs.get("priv"))
        if new:
            #keep change time from xml file
            self.repo.change = int(attrs.get('change',self.change))
            self.info.add('new-object', REPOSITORY_KEY, self.repo)
        else:
            self.repo.change = self.change
            self.info.add('merge-overwrite', REPOSITORY_KEY, self.repo)

    def stop_people(self, *tag):
        pass

    def stop_database(self, *tag):
        self.update(self.p.CurrentLineNumber)

    def stop_object(self, *tag):
        self.db.commit_media_object(self.object, self.trans, 
                                    self.object.get_change_time())
        self.object = None

    def stop_objref(self, *tag):
        self.objref = None
        
    def stop_repo(self, *tag):
        self.db.commit_repository(self.repo, self.trans, 
                                  self.repo.get_change_time())
        self.repo = None

    def stop_reporef(self, *tag):
        self.reporef = None
        
    def start_photo(self, attrs):
        self.photo = gen.lib.MediaObject()
        self.pref = gen.lib.MediaRef()
        self.pref.set_reference_handle(self.photo.get_handle())
        
        for key in attrs.keys():
            if key == "descrip" or key == "description":
                self.photo.set_description(attrs[key])
            elif key == "priv":
                self.pref.set_privacy(int(attrs[key]))
                self.photo.set_privacy(int(attrs[key]))
            elif key == "src":
                src = attrs["src"]
                self.photo.set_path(src)
            else:
                attr = gen.lib.Attribute()
                attr.set_type(key)
                attr.set_value(attrs[key])
                self.photo.add_attribute(attr)
        self.photo.set_mime_type(Mime.get_type(self.photo.get_path()))
        self.db.add_object(self.photo, self.trans)
        #set correct change time
        self.db.commit_media_object(self.photo, self.trans, self.change)
        self.info.add('new-object', MEDIA_KEY, self.photo)
        if self.family:
            self.family.add_media_reference(self.pref)
        elif self.source:
            self.source.add_media_reference(self.pref)
        elif self.person:
            self.person.add_media_reference(self.pref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.pref)

    def start_daterange(self, attrs):
        self.start_compound_date(attrs, gen.lib.Date.MOD_RANGE)

    def start_datespan(self, attrs):
        self.start_compound_date(attrs, gen.lib.Date.MOD_SPAN)

    def start_compound_date(self, attrs, mode):
        if self.source_ref:
            date_value = self.source_ref.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        else:
            date_value = self.event.get_date_object()

        start = attrs['start'].split('-')
        stop  = attrs['stop'].split('-')

        try:
            year = int(start[0])
        except ValueError:
            year = 0

        try:
            month = int(start[1])
        except:
            month = 0

        try:
            day = int(start[2])
        except:
            day = 0

        try:
            rng_year = int(stop[0])
        except:
            rng_year = 0

        try:
            rng_month = int(stop[1])
        except:
            rng_month = 0

        try:
            rng_day = int(stop[2])
        except:
            rng_day = 0

        if "cformat" in attrs:
            cal = gen.lib.Date.calendar_names.index(attrs['calendar'])
        else:
            cal = gen.lib.Date.CAL_GREGORIAN

        if 'quality' in attrs:
            val = attrs['quality']
            if val == 'estimated':
                qual = gen.lib.Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = gen.lib.Date.QUAL_CALCULATED
            else:
                qual = gen.lib.Date.QUAL_NONE
        else:
            qual = gen.lib.Date.QUAL_NONE
        
        date_value.set(qual, mode, cal, 
                       (day, month, year, False, rng_day, 
                        rng_month, rng_year, False))

    def start_dateval(self, attrs):
        if self.source_ref:
            date_value = self.source_ref.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        else:
            date_value = self.event.get_date_object()

        bce = 1
        val = attrs['val']
        if val[0] == '-':
            bce = -1
            val = val[1:]
        start = val.split('-')
        try:
            year = int(start[0])*bce
        except:
            year = 0

        try:
            month = int(start[1])
        except:
            month = 0

        try:
            day = int(start[2])
        except:
            day = 0

        if "cformat" in attrs:
            cal = gen.lib.Date.calendar_names.index(attrs['cformat'])
        else:
            cal = gen.lib.Date.CAL_GREGORIAN

        if 'type' in attrs:
            val = attrs['type']
            if val == "about":
                mod = gen.lib.Date.MOD_ABOUT
            elif val == "after":
                mod = gen.lib.Date.MOD_AFTER
            else:
                mod = gen.lib.Date.MOD_BEFORE
        else:
            mod = gen.lib.Date.MOD_NONE

        if 'quality' in attrs:
            val = attrs['quality']
            if val == 'estimated':
                qual = gen.lib.Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = gen.lib.Date.QUAL_CALCULATED
            else:
                qual = gen.lib.Date.QUAL_NONE
        else:
            qual = gen.lib.Date.QUAL_NONE
        
        date_value.set(qual, mod, cal, (day, month, year, False))

    def start_datestr(self, attrs):
        if self.source_ref:
            date_value = self.source_ref.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        else:
            date_value = self.event.get_date_object()

        date_value.set_as_text(attrs['val'])

    def start_created(self, attrs):
        if 'sources' in attrs:
            self.num_srcs = int(attrs['sources'])
        else:
            self.num_srcs = 0
        if 'places' in attrs:
            self.num_places = int(attrs['places'])
        else:
            self.num_places = 0

    def start_database(self, attrs):
        try:
            # This is a proper way to get the XML version
            xmlns = attrs.get('xmlns')
            self.version_string = xmlns.split('/')[4]
        except:
            # Before we had a proper DTD, the version was hard to determine
            # so we're setting it to 1.0.0
            self.version_string = '1.0.0'

    def start_pos(self, attrs):
        self.person.position = (int(attrs["x"]), int(attrs["y"]))

    def stop_attribute(self, *tag):
        self.attribute = None

    def stop_comment(self, tag):
        # Parse witnesses created by older gramps
        if tag.strip():
            self.witness_comment = tag
        else:
            self.witness_comment = ""

    def stop_witness(self, tag):
        # Parse witnesses created by older gramps
        if self.witness_comment:
            text = self.witness_comment
        elif tag.strip():
            text = tag
        else:
            text = None

        if text is not None:
            note = gen.lib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness comment: %s") % text)
            note.type.set(gen.lib.NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            #set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add('new-object', NOTE_KEY, note)
            self.event.add_note(note.handle)
        self.in_witness = False

    def stop_attr_type(self, tag):
        self.attribute.set_type(tag)

    def stop_attr_value(self, tag):
        self.attribute.set_value(tag)

    def stop_address(self, *tag):
        if self.person:
            self.person.add_address(self.address)
        elif self.repo:
            self.repo.add_address(self.address)
        self.address = None
        
    def stop_places(self, *tag):
        self.placeobj = None

    def stop_photo(self, *tag):
        self.photo = None

    def stop_ptitle(self, tag):
        self.placeobj.title = tag

    def stop_placeobj(self, *tag):
        if self.placeobj.title == "":
            loc = self.placeobj.get_main_location()
            self.placeobj.title = build_place_title(loc)

        # if self.placeobj.title in self.place_names:
        #    self.placeobj.title += " [%s]" % self.placeobj.gramps_id

        self.db.commit_place(self.placeobj, self.trans, 
                             self.placeobj.get_change_time())
        self.placeobj = None

    def stop_family(self, *tag):
        self.db.commit_family(self.family, self.trans,
                              self.family.get_change_time())
        self.family = None
        
    def stop_type(self, tag):
        if self.event:
            # Event type
            self.event.type.set_from_xml_str(tag)
        elif self.repo:
            # Repository type
            self.repo.type.set_from_xml_str(tag)

    def stop_childref(self, tag):
        self.childref = None

    def stop_personref(self, tag):
        self.personref = None

    def stop_eventref(self, tag):
        self.eventref = None

    def stop_event(self, *tag):
        if self.family:
            ref = gen.lib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(gen.lib.EventRoleType.FAMILY)
            self.family.add_event_ref(ref)
        elif self.person:
            ref = gen.lib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(gen.lib.EventRoleType.PRIMARY)
            if (self.event.type == gen.lib.EventType.BIRTH) \
                   and (self.person.get_birth_ref() is None):
                self.person.set_birth_ref(ref)
            elif (self.event.type == gen.lib.EventType.DEATH) \
                     and (self.person.get_death_ref() is None):
                self.person.set_death_ref(ref)
            else:
                self.person.add_event_ref(ref)

        if self.event.get_description() == "" and \
               self.event.get_type() != gen.lib.EventType.CUSTOM:
            if self.family:
                text = EVENT_FAMILY_STR % {
                    'event_name' : str(self.event.get_type()), 
                    'family' : Utils.family_name(self.family, self.db), 
                    }
            elif self.person:
                text = EVENT_PERSON_STR % {
                    'event_name' : str(self.event.get_type()), 
                    'person' : name_displayer.display(self.person), 
                    }
            else:
                text = u''
            self.event.set_description(text)

        self.db.commit_event(self.event, self.trans,
                             self.event.get_change_time())
        self.event = None

    def stop_name(self, tag):
        if self.in_witness:
            # Parse witnesses created by older gramps
            note = gen.lib.Note()
            note.handle = Utils.create_id()
            note.set(_("Witness name: %s") % tag)
            note.type.set(gen.lib.NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            #set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add('new-object', NOTE_KEY, note)
            self.event.add_note(note.handle)
        elif self.alt_name:
            # former aka tag -- alternate name
            if self.name.get_type() == "":
                self.name.set_type(gen.lib.NameType.AKA)
            self.person.add_alternate_name(self.name)
        else:
            if self.name.get_type() == "":
                self.name.set_type(gen.lib.NameType.BIRTH)
            self.person.set_primary_name (self.name)
        self.name = None

    def stop_rname(self, tag):
        # Repository name
        self.repo.name = tag

    def stop_ref(self, tag):
        # Parse witnesses created by older gramps
        person, new = self.find_person_by_gramps_id(self.map_gid(tag))
        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        event_ref = gen.lib.EventRef()
        event_ref.ref = self.event.handle
        event_ref.role.set(gen.lib.EventRoleType.WITNESS)
        person.event_ref_list.append(event_ref)
        self.db.commit_person(person, self.trans, self.change)

    def stop_place(self, tag):
        """end of a reference to place, should do nothing ...
           Note, if we encounter <place>blabla</place> this method is called
                with tag='blabla
        """
        ##place = None
        ##handle = None
        ##if self.place_ref is None:  #todo, add place_ref in start and init
        ##    #legacy cody? I see no reason for this, but it was present
        ##    if tag in self.place_map:
        ##        place = self.place_map[tag]
        ##        handle = place.get_handle()
        ##        place = None
        ##    else:
        ##        place = RelLib.Place()
        ##        place.set_title(tag)
        ##        handle = place.get_handle()
        ##    if self.ord:
        ##        self.ord.set_place_handle(handle)
        ##    elif self.object:
        ##        self.object.set_place_handle(handle)
        ##    else:
        ##        self.event.set_place_handle(handle)
        ##    if place :
        ##        self.db.commit_place(self.placeobj,self.trans,self.change)
        ##self.place_ref = None
        pass
        
    def stop_date(self, tag):
        if tag:
            if self.address:
                DateHandler.set_date(self.address, tag)
            else:
                DateHandler.set_date(self.event, tag)

    def stop_first(self, tag):
        self.name.set_first_name(tag)

    def stop_call(self, tag):
        self.name.set_call_name(tag)

    def stop_families(self, *tag):
        self.family = None

    def stop_person(self, *tag):
        self.db.commit_person(self.person, self.trans,
                              self.person.get_change_time())
        self.person = None

    def stop_description(self, tag):
        self.event.set_description(tag)

    def stop_cause(self, tag):
        # The old event's cause is now an attribute
        attr = gen.lib.Attribute()
        attr.set_type(gen.lib.AttributeType.CAUSE)
        attr.set_value(tag)
        self.event.add_attribute(attr)

    def stop_gender(self, tag):
        t = tag
        if t == "M":
            self.person.set_gender (gen.lib.Person.MALE)
        elif t == "F":
            self.person.set_gender (gen.lib.Person.FEMALE)
        else:
            self.person.set_gender (gen.lib.Person.UNKNOWN)

    def stop_stitle(self, tag):
        self.source.title = tag

    def stop_sourceref(self, *tag):
        self.source_ref = None

    def stop_source(self, *tag):
        self.db.commit_source(self.source, self.trans,
                              self.source.get_change_time())
        self.source = None

    def stop_sauthor(self, tag):
        self.source.author = tag

    def stop_phone(self, tag):
        self.address.phone = tag

    def stop_street(self, tag):
        self.address.street = tag

    def stop_city(self, tag):
        self.address.city = tag

    def stop_county(self, tag):
        self.address.county = tag

    def stop_state(self, tag):
        self.address.state = tag
        
    def stop_country(self, tag):
        self.address.country = tag

    def stop_postal(self, tag):
        self.address.set_postal_code(tag)

    def stop_spage(self, tag):
        self.source_ref.set_page(tag)

    def stop_lds_ord(self, *tag):
        self.ord = None

    def stop_spubinfo(self, tag):
        self.source.set_publication_info(tag)

    def stop_sabbrev(self, tag):
        self.source.set_abbreviation(tag)
        
    def stop_stext(self, tag):
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.stext_list)
        else:
            text = tag
        # This is old XML. We no longer have "text" attribute in soure_ref.
        # So we create a new note, commit, and add the handle to note list.
        note = gen.lib.Note()
        note.handle = Utils.create_id()
        note.private = self.source_ref.private
        note.set(text)
        note.type.set(gen.lib.NoteType.SOURCE_TEXT)
        self.db.add_note(note, self.trans)   
        #set correct change time
        self.db.commit_note(note, self.trans, self.change)
        self.info.add('new-object', NOTE_KEY, note) 
        self.source_ref.add_note(note.handle)

    def stop_scomments(self, tag):
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.scomments_list)
        else:
            text = tag
        note = gen.lib.Note()
        note.handle = Utils.create_id()
        note.private = self.source_ref.private
        note.set(text)
        note.type.set(gen.lib.NoteType.SOURCEREF)
        self.db.add_note(note, self.trans)
        #set correct change time
        self.db.commit_note(note, self.trans, self.change)
        self.info.add('new-object', NOTE_KEY, note)
        self.source_ref.add_note(note.handle)

    def stop_last(self, tag):
        if self.name:
            self.name.set_surname(tag)

    def stop_suffix(self, tag):
        if self.name:
            self.name.set_suffix(tag)

    def stop_patronymic(self, tag):
        if self.name:
            self.name.set_patronymic(tag)

    def stop_title(self, tag):
        if self.name:
            self.name.set_title(tag)

    def stop_nick(self, tag):
        if self.person:
            attr = gen.lib.Attribute()
            attr.set_type(gen.lib.AttributeType.NICKNAME)
            attr.set_value(tag)
            self.person.add_attribute(attr)

    def stop_text(self, tag):
        self.note_text = tag
        
    def stop_note(self, tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.note_list)
        elif self.note_text is not None:
            text = self.note_text
        else:
            text = tag
            
        self.note.set_styledtext(gen.lib.StyledText(text, self.note_tags))

        # The order in this long if-then statement should reflect the
        # DTD: most deeply nested elements come first.
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
        elif self.eventref:
            self.eventref.add_note(self.note.handle)
        elif self.reporef:
            self.reporef.add_note(self.note.handle)
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
        elif self.repo:
            self.repo.add_note(self.note.handle)

        self.db.commit_note(self.note, self.trans, self.note.get_change_time())
        self.note = None

    def stop_research(self, tag):
        self.owner.set_name(self.resname)
        self.owner.set_address(self.resaddr)
        self.owner.set_city(self.rescity)
        self.owner.set_state(self.resstate)
        self.owner.set_country(self.rescon)
        self.owner.set_postal_code(self.respos)
        self.owner.set_phone(self.resphone)
        self.owner.set_email(self.resemail)

    def stop_resname(self, tag):
        self.resname = tag

    def stop_resaddr(self, tag):
        self.resaddr = tag

    def stop_rescity(self, tag):
        self.rescity = tag

    def stop_resstate(self, tag):
        self.resstate = tag

    def stop_rescountry(self, tag):
        self.rescon = tag

    def stop_respostal(self, tag):
        self.respos = tag

    def stop_resphone(self, tag):
        self.resphone = tag

    def stop_resemail(self, tag):
        self.resemail = tag

    def stop_mediapath(self, tag):
        self.mediapath = tag

    def stop_ptag(self, tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(tag)
        elif self.in_stext:
            self.stext_list.append(tag)
        elif self.in_scomments:
            self.scomments_list.append(tag)

    def stop_aka(self, tag):
        self.person.add_alternate_name(self.name)
        if self.name.get_type() == "":
            self.name.set_type(gen.lib.NameType.AKA)
        self.name = None

    def startElement(self, tag, attrs):
        self.func_list[self.func_index] = (self.func, self.tlist)
        self.func_index += 1
        self.tlist = []

        try:
            f, self.func = self.func_map[tag]
            if f:
                f(attrs)
        except KeyError:
            self.func_map[tag] = (None, None)
            self.func = None

    def endElement(self, tag):
        if self.func:
            self.func(''.join(self.tlist))
        self.func_index -= 1    
        self.func, self.tlist = self.func_list[self.func_index]
        
    def characters(self, data):
        if self.func:
            self.tlist.append(data)


def append_value(orig, val):
    if orig:
        return "%s, %s" % (orig, val)
    else:
        return val

def build_place_title(loc):
    "Builds a title from a location"
    value = ""
    if loc.parish:
        value = loc.parish
    if loc.city:
        value = append_value(value, loc.city)
    if loc.county:
        value = append_value(value, loc.county)
    if loc.state:
        value = append_value(value, loc.state)
    if loc.country:
        value = append_value(value, loc.country)
    return value

#-------------------------------------------------------------------------
#
# VersionParser
#
#-------------------------------------------------------------------------
class VersionParser:
    """
    Utility class to quickly get the versions from an XML file.
    """
    def __init__(self, xml_file):
        """
        xml_file must be a file object that is already open.
        """
        self.__p = ParserCreate()
        self.__p.StartElementHandler = self.__element_handler
        self.__gramps_version = 'unknown'
        self.__xml_version = '1.0.0'
        
        xml_file.seek(0)
        self.__p.ParseFile(xml_file)
        
    def __element_handler(self, tag, attrs):
        " Handle XML elements "
        if tag == "database" and 'xmlns' in attrs:
            xmlns = attrs.get('xmlns')
            self.__xml_version = xmlns.split('/')[4]
        elif tag == "created" and 'version' in attrs:
            self.__gramps_version = attrs.get('version')

    def get_xmlns_version(self):
        " Get the namespace version of the file "
        return self.__xml_version
    
    def get_gramps_version(self):
        " Get the version of Gramps that created the file "
        return self.__gramps_version

def open_file(filename, cli):
    """ 
    Open the xml file.
    Return a valid file handle if the file opened sucessfully.
    Return None if the file was not able to be opened.
    """
    if GZIP_OK:
        use_gzip = True
        try:
            ofile = gzip.open(filename, "r")
            ofile.read(1)
            ofile.close()
        except IOError, msg:
            use_gzip = False
        except ValueError, msg:
            use_gzip = True
    else:
        use_gzip = False

    try:
        if use_gzip:
            xml_file = gzip.open(filename, "rb")
        else:
            xml_file = open(filename, "r")
    except IOError, msg:
        if cli:
            print "Error: %s could not be opened Exiting." % filename
            print msg
        else:
            ErrorDialog(_("%s could not be opened") % filename, str(msg))
        xml_file = None
    except:
        if cli:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        xml_file = None
        
    return xml_file
    
def version_is_valid(filename, cli):
    """ 
    Validate the xml version.
    """
    parser = VersionParser(filename)
    
    if parser.get_xmlns_version() > _GrampsDbWriteXML.XML_VERSION:
        msg = _("The .gramps file you are importing was made by version %s of "
                "GRAMPS, while you are running an older version %s. "
                "The file will not be imported. Please upgrade to the latest "
                "version of GRAMPS and try again." 
                ) % (parser.get_gramps_version(), const.VERSION)
        if cli:
            print msg
            return False
        else:
            ErrorDialog(msg)
            return False
            
    return True
