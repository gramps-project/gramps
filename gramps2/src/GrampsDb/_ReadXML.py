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

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import sets
import shutil
from xml.parsers.expat import ExpatError, ParserCreate
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK+ Modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from QuestionDialog import ErrorDialog, WarningDialog, MissingMediaDialog
import Date
import GrampsMime
import RelLib
import const
import Utils
import DateHandler
import NameDisplay
import _ConstXML

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

_FAMILY_TRANS = {
    'Married'     : RelLib.Family.MARRIED,
    'Unmarried'   : RelLib.Family.UNMARRIED,
    'Partners'    : RelLib.Family.UNMARRIED,
    'Civil Union' : RelLib.Family.CIVIL_UNION,
    'Unknown'     : RelLib.Family.UNKNOWN,
    'Other'       : RelLib.Family.CUSTOM,
    }

_NAME_TRANS = {
    "Unknown"       : RelLib.Name.UNKNOWN,
    "Custom"        : RelLib.Name.CUSTOM,
    "Also Known As" : RelLib.Name.AKA,
    "Birth Name"    : RelLib.Name.BIRTH,
    "Married Name"  : RelLib.Name.MARRIED,
    }

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
# Must takes care of renaming media files according to their new IDs.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None,cl=0,use_trans=True):

    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    change = os.path.getmtime(filename)
    parser = GrampsParser(database,callback,basefile,change,filename)

    linecounter = LineParser(filename)
    lc = linecounter.get_count()
    
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
            os._exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename,str(msg))
            return
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
            os._exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename)
            return
    try:
        parser.parse(xml_file,use_trans,lc)
    except IOError,msg:
        if cl:
            print "Error reading %s" % filename
            print msg
            import traceback
            traceback.print_exc()
            os._exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,str(msg))
            import traceback
            traceback.print_exc()
            return
    except ExpatError, msg:
        if cl:
            print "Error reading %s" % filename
            print "The file is probably either corrupt or not a valid GRAMPS database."
            os._exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,
                        _("The file is probably either corrupt or not a valid GRAMPS database."))
            return
    except:
        if cl:
            import traceback
            traceback.print_exc()
            os._exit(1)
        else:
            import DisplayTrace
            DisplayTrace.DisplayTrace()
            return

    xml_file.close()

    database.readonly = ro

    # copy all local images into <database>.images directory
    db_dir = os.path.abspath(os.path.dirname(database.get_save_path()))
    db_base = os.path.basename(database.get_save_path())
    img_dir = "%s/%s.images" % (db_dir,db_base)
    first = not os.path.exists(img_dir)
    
    for m_id in database.get_media_object_handles():
        mobject = database.get_object_from_handle(m_id)
        oldfile = mobject.get_path()
        if oldfile and oldfile[0] != '/':
            if first:
                os.mkdir(img_dir)
                first = 0
            newfile = "%s/%s" % (img_dir,oldfile)

            try:
                oldfilename = "%s/%s" % (basefile,oldfile)
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

            self.count = len(f.readlines())
            f.close()
        except:
            self.count = 0

    def get_count(self):
        return self.count

#-------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
#-------------------------------------------------------------------------
class GrampsParser:

    def __init__(self,database,callback,base,change,filename):
        self.filename = filename
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []
        self.oldval = 0
        self.tlist = []
        self.conf = 2
        self.gid2id = {}
        self.gid2fid = {}
        self.gid2pid = {}
        self.gid2oid = {}
        self.gid2sid = {}
        self.change = change
        self.dp = DateHandler.parser
        self.child_relmap = {
            "None"      : RelLib.Person.CHILD_NONE,
            "Birth"     : RelLib.Person.CHILD_BIRTH,
            "Adopted"   : RelLib.Person.CHILD_ADOPTED,
            "Stepchild" : RelLib.Person.CHILD_STEPCHILD,
            "Sponsored" : RelLib.Person.CHILD_SPONSORED,
            "Foster"    : RelLib.Person.CHILD_FOSTER,
            "Unknown"   : RelLib.Person.CHILD_UNKNOWN,
            }
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
        self.pref = None
        self.use_p = 0
        self.in_note = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.in_witness = 0
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
        
        self.callback = callback
        self.increment = 100
        self.event = None
        self.eventref = None
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
        self.sidswap = {}
        self.pidswap = {}
        self.oidswap = {}
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
            "child"      : (self.start_child,None),
            "childof"    : (self.start_childof,None),
            "city"       : (None, self.stop_city),
            "country"    : (None, self.stop_country),
            "comment"    : (None, self.stop_comment),
            "created"    : (self.start_created, None),
            "ref"        : (None, self.stop_ref),
            "database"   : (None, self.stop_database),
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
            "gender"     : (None, self.stop_gender),
            "header"     : (None, None),
            "last"       : (self.start_last, self.stop_last),
            "mother"     : (self.start_mother,None),
            "name"       : (self.start_name, self.stop_name),
            "nick"       : (None, self.stop_nick),
            "note"       : (self.start_note, self.stop_note),
            "p"          : (None, self.stop_ptag),
            "parentin"   : (self.start_parentin,None),
            "people"     : (self.start_people, self.stop_people),
            "person"     : (self.start_person, self.stop_person),
            "img"        : (self.start_photo, self.stop_photo),
            "objref"     : (self.start_objref, self.stop_objref),
            "object"     : (self.start_object, self.stop_object),
            "file"       : (self.start_file, self.stop_file),
            "place"      : (self.start_place, self.stop_place),
            "dateval"    : (self.start_dateval, None),
            "daterange"  : (self.start_daterange, None),
            "datestr"    : (self.start_datestr, None),
            "places"     : (None, self.stop_places),
            "placeobj"   : (self.start_placeobj,self.stop_placeobj),
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
            "url"        : (self.start_url, None)
            }

        self.save_attr = {
            "Unknown" : RelLib.Attribute.UNKNOWN,
            "Custom" : RelLib.Attribute.CUSTOM,
            "Caste" : RelLib.Attribute.CASTE,
            "Description" : RelLib.Attribute.DESCRIPTION,
            "Identification Number" : RelLib.Attribute.ID,
            "National Origin" : RelLib.Attribute.NATIONAL,
            "Number of Children" : RelLib.Attribute.NUM_CHILD,
            "Social Security Number" : RelLib.Attribute.SSN,
            "Number of Children" : RelLib.Attribute.NUM_CHILD,
            }

        self.save_event = {
            "Unknown" : RelLib.Event.UNKNOWN,
            "Custom" : RelLib.Event.CUSTOM,
            "Marriage" : RelLib.Event.MARRIAGE,
            "Marriage Settlement" : RelLib.Event.MARR_SETTL,
            "Marriage License" : RelLib.Event.MARR_LIC,
            "Marriage Contract" : RelLib.Event.MARR_CONTR,
            "Marriage Banns" : RelLib.Event.MARR_BANNS,
            "Engagement" : RelLib.Event.ENGAGEMENT,
            "Divorce" : RelLib.Event.DIVORCE,
            "Divorce Filing" : RelLib.Event.DIV_FILING,
            "Annulment" : RelLib.Event.ANNULMENT,
            "Alternate Marriage" : RelLib.Event.MARR_ALT,
            "Adopted" : RelLib.Event.ADOPT,
            "Birth" : RelLib.Event.BIRTH,
            "Death" : RelLib.Event.DEATH,
            "Adult Christening" : RelLib.Event.ADULT_CHRISTEN,
            "Baptism" : RelLib.Event.BAPTISM,
            "Bar Mitzvah" : RelLib.Event.BAR_MITZVAH,
            "Bas Mitzvah" : RelLib.Event.BAS_MITZVAH,
            "Blessing" : RelLib.Event.BLESS,
            "Burial" : RelLib.Event.BURIAL,
            "Cause Of Death" : RelLib.Event.CAUSE_DEATH,
            "Census" : RelLib.Event.CENSUS,
            "Christening" : RelLib.Event.CHRISTEN,
            "Confirmation" : RelLib.Event.CONFIRMATION,
            "Cremation" : RelLib.Event.CREMATION,
            "Degree" : RelLib.Event.DEGREE,
            "Divorce Filing" : RelLib.Event.DIV_FILING,
            "Education" : RelLib.Event.EDUCATION,
            "Elected" : RelLib.Event.ELECTED,
            "Emigration" : RelLib.Event.EMIGRATION,
            "First Communion" : RelLib.Event.FIRST_COMMUN,
            "Immigration" : RelLib.Event.IMMIGRATION,
            "Graduation" : RelLib.Event.GRADUATION,
            "Medical Information" : RelLib.Event.MED_INFO,
            "Military Service" : RelLib.Event.MILITARY_SERV,
            "Naturalization" : RelLib.Event.NATURALIZATION,
            "Nobility Title" : RelLib.Event.NOB_TITLE,
            "Number of Marriages" : RelLib.Event.NUM_MARRIAGES,
            "Occupation" : RelLib.Event.OCCUPATION,
            "Ordination" : RelLib.Event.ORDINATION,
            "Probate" : RelLib.Event.PROBATE,
            "Property" : RelLib.Event.PROPERTY,
            "Religion" : RelLib.Event.RELIGION,
            "Residence" : RelLib.Event.RESIDENCE,
            "Retirement" : RelLib.Event.RETIREMENT,
            "Will" : RelLib.Event.WILL,
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

    def map_gid(self,handle):
        if not self.idswap.get(handle):
            if self.db.get_person_from_gramps_id(handle):
                self.idswap[handle] = self.db.find_next_person_gramps_id()
            else:
                self.idswap[handle] = handle
        return self.idswap[handle]

    def map_fid(self,handle):
        if not self.fidswap.get(handle):
            if self.db.get_family_from_gramps_id(handle):
                self.fidswap[handle] = self.db.find_next_family_gramps_id()
            else:
                self.fidswap[handle] = handle
        return self.fidswap[handle]

    def map_pid(self,handle):
        if not self.pidswap.get(handle):
            if self.db.get_place_from_gramps_id(handle):
                self.pidswap[handle] = self.db.find_next_place_gramps_id()
            else:
                self.pidswap[handle] = handle
        return self.pidswap[handle]

    def map_sid(self,handle):
        if not self.sidswap.get(handle):
            if self.db.get_source_from_gramps_id(handle):
                self.sidswap[handle] = self.db.find_next_source_gramps_id()
            else:
                self.sidswap[handle] = handle
        return self.sidswap[handle]

    def map_oid(self,handle):
        if not self.oidswap.get(handle):
            if self.db.get_object_from_gramps_id(handle):
                self.oidswap[handle] = self.db.find_next_object_gramps_id()
            else:
                self.oidswap[handle] = handle
        return self.oidswap[handle]

    def parse(self,file,use_trans=True,linecount=0):

        self.trans = self.db.transaction_begin("",batch=True)
        self.linecount = linecount

        self.db.disable_signals()

        self.p = ParserCreate()
        self.p.StartElementHandler = self.startElement
        self.p.EndElementHandler = self.endElement
        self.p.CharacterDataHandler = self.characters
        self.p.ParseFile(file)
            
        self.db.set_researcher(self.owner)
        if self.home != None:
            person = self.db.find_person_from_handle(self.home,self.trans)
            self.db.set_default_person_handle(person.get_handle())
        if self.tempDefault != None:
            handle = self.map_gid(self.tempDefault)
            person = self.find_person_by_gramps_id(handle)
            if person:
                self.db.set_default_person_handle(person.get_handle())

        for key in self.func_map.keys():
            del self.func_map[key]
        del self.func_map
        del self.func_list
        del self.p
        if use_trans:
            self.db.transaction_commit(self.trans,_("GRAMPS XML import"))
        self.db.enable_signals()
        self.db.request_rebuild()

    def start_lds_ord(self,attrs):
        atype = attrs['type']
        self.ord = RelLib.LdsOrd()
        if self.person:
            if atype == "baptism":
                self.person.set_lds_baptism(self.ord)
            elif atype == "endowment":
                self.person.set_lds_endowment(self.ord)
            elif atype == "sealed_to_parents":
                self.person.set_lds_sealing(self.ord)
        elif self.family:
            if atype == "sealed_to_spouse":
                self.family.set_lds_sealing(self.ord)

    def start_temple(self,attrs):
        self.ord.set_temple(attrs['val'])

    def start_data_item(self,attrs):
        self.source.set_data_item(attrs['key'],attrs['value'])

    def start_status(self,attrs):
        self.ord.set_status(int(attrs['val']))

    def start_sealed_to(self,attrs):
        try:
            family = self.db.find_family_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            handle = self.map_fid(attrs['ref'])
            family = self.find_family_by_gramps_id(handle)
        self.ord.set_family_handle(family.get_handle())
        
    def start_place(self,attrs):
        try:
            self.placeobj = self.db.find_place_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            handle = self.map_pid(attrs['ref'])
            self.placeobj = self.find_place_by_gramps_id(handle)
        
    def start_placeobj(self,attrs):
        handle = self.map_pid(attrs['id'])
        try:
            self.placeobj = self.db.find_place_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.placeobj.set_gramps_id(handle)
        except KeyError:
            self.placeobj = self.find_place_by_gramps_id(handle)
        title = attrs['title']
        if title == "":
            title = attrs['id']

        self.placeobj.set_title(title)
        self.locations = 0

        self.update()
            
    def start_location(self,attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""
        
        loc = RelLib.Location()
        loc.phone = attrs.get('phone','')
        loc.postal = attrs.get('postal','')
        loc.city = attrs.get('city','')
        loc.parish = attrs.get('parish','')
        loc.state = attrs.bet('state','')
        loc.county = attrs.get('county','')
        loc.country = attrs.get('country','')
        if self.locations > 0:
            self.placeobj.add_alternate_locations(loc)
        else:
            self.placeobj.set_main_location(loc)
            self.locations = self.locations + 1

    def start_witness(self,attrs):
        # Parse witnesses created by older gramps
        self.in_witness = 1
        self.witness_comment = ""
        print "in start_witness"
        if attrs.has_key('name'):
            note_text = self.event.get_note() + "\n" + \
                        _("Witness name: %s") % attrs['name']
            self.event.set_note(note_text)
            return

        if attrs.has_key('hlink'):
            person = self.db.find_person_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        elif attrs.has_key('ref'):
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        event_ref = RelLib.EventRef()
        event_ref.ref = self.event.handle
        event_ref.role = (RelLib.EventRef.WITNESS,'')
        person.event_ref_list.append(event_ref)
        self.db.commit_person(person,self.trans,self.change)
        
    def start_coord(self,attrs):
        #if attrs.has_key('lat'):
        self.placeobj.lat = attrs.get('lat','')
        #if attrs.has_key('long'):
        self.placeobj.long = attrs.get('long','')

    def start_event(self,attrs):
        self.event = RelLib.Event()
        if self.person or self.family:
            # GRAMPS LEGACY: old events that were written inside
            # person or family objects.
            self.event.handle = Utils.create_id()
            self.event.type = _ConstXML.tuple_from_xml(_ConstXML.events,
                                                       attrs['type'])
        else:
            # This is new event, with handle already existing
            self.event.handle = attrs['handle'].replace('_','')
            self.event.conf = int(attrs.get("conf",2))
            self.event.private = bool(attrs.get("priv"))
        self.db.add_event(self.event,self.trans)

    def start_eventref(self,attrs):
        self.eventref = RelLib.EventRef()
        self.eventref.ref = attrs['hlink'].replace('_','')
        self.eventref.private = bool(attrs.get('priv'))
        self.eventref.role = _ConstXML.tuple_from_xml(_ConstXML.event_roles,
                                            attrs.get('role',''))
        if self.family:
            self.family.add_event_ref(self.eventref)
        elif self.person:
            # We count here on events being already parsed prior
            # to parsing people. This will fail if this is not true.
            event = self.db.get_event_from_handle(self.eventref.ref)
            print self.eventref.ref
            print "event", event
            if event.type[0] == RelLib.Event.BIRTH:
                self.person.birth_ref = self.eventref
            elif event.type[0] == RelLib.Event.DEATH:
                self.person.death_ref = self.eventref
            else:
                self.person.add_event_ref(self.eventref)

    def start_attribute(self,attrs):
        self.attribute = RelLib.Attribute()
        self.attribute.conf = int(attrs.get("conf",2))
        self.attribute.private = bool(attrs.get("priv"))
        self.attribute.type = _ConstXML.tuple_from_xml(_ConstXML.attributes,
                                                       attrs.get("type",''))
        self.attribute.value = attrs.get("value",'')
        if self.photo:
            self.photo.add_attribute(self.attribute)
        elif self.object:
            self.object.add_attribute(self.attribute)
        elif self.objref:
            self.objref.add_attribute(self.attribute)
        elif self.person:
            self.person.add_attribute(self.attribute)
        elif self.family:
            self.family.add_attribute(self.attribute)

    def start_address(self,attrs):
        self.address = RelLib.Address()
        self.person.add_address(self.address)
        self.address.conf = int(attrs.get("conf",2))
        self.address.private = bool(attrs.get("priv"))

    def start_bmark(self,attrs):
        try:
            person = self.db.find_person_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            handle = self.map_gid(attrs["ref"])
            person = self.find_person_by_gramps_id(handle)
        self.db.bookmarks.append(person.get_handle())

    def start_person(self,attrs):
        self.update()
        new_id = self.map_gid(attrs['id'])
        try:
            self.person = self.db.find_person_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.person.set_gramps_id(new_id)
        except KeyError:
            self.person = self.find_person_by_gramps_id(new_id)

        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.person.marker = (RelLib.PrimaryObject.MARKER_COMPLETE,"")
        else:
            self.person.marker = _ConstXML.tuple_from_xml(
                _ConstXML.marker_types,attrs.get("marker",''))

    def start_people(self,attrs):
        if attrs.has_key('home'):
            self.home = attrs['home'].replace('_','')
        elif attrs.has_key("default"):
            self.tempDefault = attrs["default"]

    def start_father(self,attrs):
        try:
            person = self.db.find_person_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
        self.family.set_father_handle(person.get_handle())

    def start_mother(self,attrs):
        try:
            person = self.db.find_person_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
        self.family.set_mother_handle(person.get_handle())
    
    def start_child(self,attrs):
        try:
            person = self.db.find_person_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            person = self.find_person_by_gramps_id(self.map_gid(attrs["ref"]))
        self.family.add_child_handle(person.get_handle())

    def start_url(self,attrs):
        if not attrs.has_key("href"):
            return
        url = RelLib.Url()
        url.path = attrs["href"]
        url.description = attrs.get("description",'')
        url.privacy = bool(attrs.get('priv'))
        if self.person:
            self.person.add_url(url)
        elif self.placeobj:
            self.placeobj.add_url(url)

    def start_family(self,attrs):
        self.update()
        handle = self.map_fid(attrs["id"])
        try:
            self.family = self.db.find_family_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.family.set_gramps_id(handle)
        except KeyError:
            self.family = self.find_family_by_gramps_id(handle)
        # GRAMPS LEGACY: the type now belongs to <rel> tag
        # Here we need to support old format of <family type="Married">
        self.family.type = _ConstXML.tuple_from_xml(
            _ConstXML.family_relations,attrs.get("type",'Unknown'))
                
        # Old and new markers: complete=1 and marker=word both have to work
        if attrs.get('complete'): # this is only true for complete=1
            self.family.marker = (RelLib.PrimaryObject.MARKER_COMPLETE,"")
        else:
            self.family.marker = _ConstXML.tuple_from_xml(
                _ConstXML.marker_types,attrs.get("marker",''))

    def start_rel(self,attrs):
        pass

    def start_file(self,attrs):
        pass

    def stop_file(self,tag):
        pass

    def start_childof(self,attrs):
        try:
            family = self.db.find_family_from_handle(
                attrs["hlink"].replace('_',''),self.trans)
        except KeyError:
            family = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
            
        mrel = _ConstXML.tuple_from_xml(_ConstXML.child_relations,
                                        attrs.get('mrel','Birth'))
        frel = _ConstXML.tuple_from_xml(_ConstXML.child_relations,
                                        attrs.get('frel','Birth'))
        self.person.add_parent_family_handle(family.handle,mrel,frel)

    def start_parentin(self,attrs):
        try:
            family = self.db.find_family_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            family = self.find_family_by_gramps_id(self.map_fid(attrs["ref"]))
        self.person.add_family_handle(family.handle)

    def start_name(self,attrs):
        if not self.in_witness:
            self.name = RelLib.Name()
            self.name.type =_ConstXML.tuple_from_xml(
                _ConstXML.name_types,attrs.get('type','Birth Name'))
            self.name.sort_as = int(attrs.get("sort",RelLib.Name.DEF))
            self.name.display_as = int(attrs.get("display",RelLib.Name.DEF))
            self.name.conf = int(attrs.get("conf",2))
            self.name.set_private = bool(attrs.get("priv"))
            self.alt_name = bool(attrs.get("alt"))

    def start_last(self,attrs):
        self.name.prefix = attrs.get('prefix','')
        self.name.group_as = attrs.get('group','')
        
    def start_note(self,attrs):
        self.in_note = 1
        self.note = RelLib.Note()
        self.note.format = int(attrs.get('format',0))

    def start_sourceref(self,attrs):
        self.source_ref = RelLib.SourceRef()
        try:
            source = self.db.find_source_from_handle(
                attrs["hlink"].replace('_',''),self.trans)
        except KeyError:
            source = self.find_source_by_gramps_id(self.map_sid(attrs["ref"]))
            
        self.source_ref.confidence = int(attrs.get("conf",self.conf))
        self.source_ref.ref = source.handle
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
        elif self.family:
            self.family.add_source_reference(self.source_ref)
        elif self.person:
            self.person.add_source_reference(self.source_ref)

    def start_source(self,attrs):
        self.update()
        handle = self.map_sid(attrs["id"])
        try:
            self.source = self.db.find_source_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.source.set_gramps_id(handle)
        except KeyError:
            self.source = self.find_source_by_gramps_id(handle)

    def start_objref(self,attrs):
        self.objref = RelLib.MediaRef()
        try:
            obj = self.db.find_object_from_handle(
                attrs['hlink'].replace('_',''),self.trans)
        except KeyError:
            obj = self.find_object_by_gramps_id(self.map_oid(attrs['ref']))
            
        self.objref.ref = obj.handle
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
        handle = self.map_oid(attrs['id'])
        try:
            self.object = self.db.find_object_from_handle(
                attrs['handle'].replace('_',''),self.trans)
            self.object.set_gramps_id(handle)
        except KeyError:
            self.object = self.find_object_by_gramps_id(handle)

        # GRAMPS LEGACY: src, mime, and description attributes
        # now belong to the <file> tag. Here we are supporting
        # the old format of <object src="blah"...>
        self.object.mime = attrs['mime']
        self.object.desc = attrs['description']
        src = attrs["src"]
        if src:
            if src[0] != '/':
                fullpath = os.path.abspath(self.filename)
                src = os.path.dirname(fullpath) + '/' + src
            self.object.path = src

    def stop_people(self,*tag):
        pass

    def stop_database(self,*tag):
        self.update()

    def stop_object(self,*tag):
        self.db.commit_media_object(self.object,self.trans,self.change)
        self.object = None

    def stop_objref(self,*tag):
        self.objref = None
        
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
                if src[0] != '/':
                    self.photo.set_path("%s/%s" % (self.base,src))
                else:
                    self.photo.set_path(src)
            else:
                a = RelLib.Attribute()
                a.set_type(key)
                a.set_value(attrs[key])
                self.photo.add_attribute(a)
        self.photo.set_mime_type(GrampsMime.get_type(self.photo.get_path()))
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
            cal = Date.Date.calendar.index(attrs['calendar'])
        else:
            cal = Date.CAL_GREGORIAN

        if attrs.has_key('quality'):
            val = attrs['quality']
            if val == 'estimated':
                qual = Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = Date.QUAL_CALCULATED
            else:
                qual = Date.QUAL_NONE
        else:
            qual = Date.QUAL_NONE
        
        dv.set(qual,Date.MOD_RANGE,cal,(d,m,y,False,rd,rm,ry,False))

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
            cal = Date.Date.calendar_names.index(attrs['cformat'])
        else:
            cal = Date.CAL_GREGORIAN

        if attrs.has_key('type'):
            val = attrs['type']
            if val == "about":
                mod = Date.MOD_ABOUT
            elif val == "after":
                mod = Date.MOD_AFTER
            else:
                mod = Date.MOD_BEFORE
        else:
            mod = Date.MOD_NONE

        if attrs.has_key('quality'):
            val = attrs['quality']
            if val == 'estimated':
                qual = Date.QUAL_ESTIMATED
            elif val == 'calculated':
                qual = Date.QUAL_CALCULATED
            else:
                qual = Date.QUAL_NONE
        else:
            qual = Date.QUAL_NONE
        
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
            note_text = self.event.get_note() + "\n" + \
                        _("Witness comment: %s") % self.witness_comment
            self.event.set_note(note_text)
        elif tag.strip():
            note_text = self.event.get_note() + "\n" + \
                        _("Witness comment: %s") % tag
            self.event.set_note(note_text)
        self.in_witness = 0

    def stop_attr_type(self,tag):
        self.attribute.set_type(tag)

    def stop_attr_value(self,tag):
        self.attribute.set_value(tag)

    def stop_address(self,*tag):
        self.address = None
        
    def stop_places(self,*tag):
        self.placeobj = None

    def stop_photo(self,*tag):
        self.photo = None

    def stop_placeobj(self,*tag):
        if self.placeobj.get_title() == "":
            loc = self.placeobj.get_main_location()
            self.placeobj.set_title(build_place_title(loc))

        title = self.placeobj.get_title()
        if title in self.place_names:
            self.placeobj.set_title(title + " [%s]" % self.placeobj.get_gramps_id())

        self.db.commit_place(self.placeobj,self.trans,self.change)
        self.placeobj = None

    def stop_family(self,*tag):
        self.db.commit_family(self.family,self.trans,self.change)
        self.family = None
        while gtk.events_pending():
            gtk.main_iteration()
        
    def stop_type(self,tag):
        # Event type
        self.event.type = _ConstXML.tuple_from_xml(_ConstXML.events,tag)

    def stop_eventref(self,tag):
        self.eventref = None

    def stop_event(self,*tag):
        if self.family:
            ref = RelLib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role = (RelLib.EventRef.FAMILY,'')
            self.family.add_event_ref(ref)
        elif self.person:
            ref = RelLib.EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role = (RelLib.EventRef.PRIMARY,'')
            if self.event.type[0] == RelLib.Event.BIRTH:
                self.person.birth_ref = ref
            elif self.event.type[0] == RelLib.Event.DEATH:
                self.person.death_ref = ref
            else:
                self.person.add_event_ref(ref)
        self.db.commit_event(self.event,self.trans,self.change)
        self.event = None

    def stop_name(self,tag):
        # Parse witnesses created by older gramps
        if self.in_witness:
            note_text = self.event.get_note() + "\n" + \
                        _("Witness name: %s") % tag
            self.event.set_note(note_text)
        elif self.alt_name:
            # former aka tag -- alternate name
            if self.name.get_type() == "":
                self.name.set_type("Also Known As")
            self.person.add_alternate_name(self.name)
        else:
            if self.name.get_type() == "":
                self.name.set_type("Birth Name")
            self.person.set_primary_name (self.name)
            self.person.get_primary_name().build_sort_name()
        self.name = None

    def stop_ref(self,tag):
        # Parse witnesses created by older gramps
        person = self.find_person_by_gramps_id(self.map_gid(tag))
        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        event_ref = RelLib.EventRef()
        event_ref.ref = self.event.handle
        event_ref.role = (RelLib.EventRef.WITNESS,'')
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
        while gtk.events_pending():
            gtk.main_iteration()
        
    def stop_date(self,tag):
        if tag:
            if self.address:
                DateHandler.set_date(self.address,tag)
            else:
                DateHandler.set_date(self.event,tag)

    def stop_first(self,tag):
        self.name.set_first_name(tag)

    def stop_families(self,*tag):
        self.family = None

    def stop_person(self,*tag):
        self.db.commit_person(self.person,self.trans,self.change)
        self.person = None
        while gtk.events_pending():
            gtk.main_iteration()

    def stop_description(self,tag):
        self.event.description = tag

    def stop_cause(self,tag):
        self.event.cause = tag

    def stop_gender(self,tag):
        t = tag
        if t == "M":
            self.person.set_gender (RelLib.Person.MALE)
        elif t == "F":
            self.person.set_gender (RelLib.Person.FEMALE)
        else:
            self.person.set_gender (RelLib.Person.UNKNOWN)

    def stop_stitle(self,tag):
        self.source.set_title(tag)

    def stop_sourceref(self,*tag):
        self.source_ref = None

    def stop_source(self,*tag):
        self.db.commit_source(self.source,self.trans,self.change)
        self.source = None

    def stop_sauthor(self,tag):
        self.source.set_author(tag)

    def stop_phone(self,tag):
        self.address.set_phone(tag)

    def stop_street(self,tag):
        self.address.set_street(tag)

    def stop_city(self,tag):
        self.address.set_city(tag)

    def stop_state(self,tag):
        self.address.set_state(tag)
        
    def stop_country(self,tag):
        self.address.set_country(tag)

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
            note = fix_spaces(self.scomments_list)
        else:
            note = tag
        self.source_ref.set_note(note)

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
            self.person.set_nick_name(tag)

    def stop_note(self,tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.note_list)
        else:
            text = tag
        self.note.set(text)

        if self.address:
            self.address.set_note_object(self.note)
        elif self.ord:
            self.ord.set_note_object(self.note)
        elif self.attribute:
            self.attribute.set_note_object(self.note)
        elif self.object:
            self.object.set_note_object(self.note)
        elif self.objref:
            self.objref.set_note_object(self.note)
        elif self.photo:
            self.photo.set_note_object(self.note)
        elif self.name:
            self.name.set_note_object(self.note)
        elif self.source:
            self.source.set_note_object(self.note)
        elif self.event:
            self.event.set_note_object(self.note)
        elif self.person:
            self.person.set_note_object(self.note)
        elif self.family:
            self.family.set_note_object(self.note)
        elif self.placeobj:
            self.placeobj.set_note_object(self.note)
        elif self.eventref:
            self.eventref.set_note_object(self.note)

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
            self.name.set_type("Also Known As")
        self.name = None

    def startElement(self,tag,attrs):

        self.func_list[self.func_index] = (self.func,self.tlist)
        self.func_index = self.func_index + 1
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
        self.func_index = self.func_index - 1    
        self.func,self.tlist = self.func_list[self.func_index]

    def characters(self, data):
        if self.func:
            self.tlist.append(data)

    def update(self):
        line = self.p.CurrentLineNumber
        newval = int(100*line/self.linecount)
        if newval != self.oldval:
            self.callback(newval)
            self.oldval = newval

def append_value(orig,val):
    if orig:
        return "%s, %s" % (orig,val)
    else:
        return val

def build_place_title(loc):
    "Builds a title from a location"
    city = loc.get_city()
    state = loc.get_state()
    country = loc.get_country()
    county = loc.get_county()
    parish = loc.get_parish()
    
    value = ""

    if parish:
        value = parish
    if city:
        value = append_value(value,city)
    if county:
        value = append_value(value,county)
    if state:
        value = append_value(value,state)
    if country:
        value = append_value(value,country)
    return value
