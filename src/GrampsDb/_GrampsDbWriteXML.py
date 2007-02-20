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

# $Id: _WriteXML.py 8081 2007-02-10 23:40:48Z zfoldvar $

"""
Contains the interface to allow a database to get written using
GRAMPS' XML file format.
"""

#-------------------------------------------------------------------------
#
# load standard python libraries
#
#-------------------------------------------------------------------------
import time
import shutil
import os
import codecs
from xml.sax.saxutils import escape
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WriteXML")

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------

import RelLib 
from _GrampsDbConst import \
     PERSON_KEY,FAMILY_KEY,SOURCE_KEY,EVENT_KEY,\
     MEDIA_KEY,PLACE_KEY,REPOSITORY_KEY,NOTE_KEY
 
from _GrampsDbExceptions import *
from _LongOpStatus import LongOpStatus

#-------------------------------------------------------------------------
#
# Attempt to load the GZIP library. Some version of python do not seem
# to be compiled with this available.
#
#-------------------------------------------------------------------------
try:
    import gzip
    _gzip_ok = 1
except:
    _gzip_ok = 0


_xml_version = "1.1.4"

# table for skipping control chars from XML
strip_dict = dict.fromkeys(range(9)+range(12,20))


def escxml(d):
    return escape(d, { '"' : '&quot;' } )

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, person, version="unknown"):
    ret = 0
    if os.path.isfile(filename):
        try:
            shutil.copyfile(filename, filename + ".bak")
            shutil.copystat(filename, filename + ".bak")
        except:
            pass

    compress = _gzip_ok == 1

    g = GrampsDbXmlWriter(database,0,compress,version)
    ret = g.write(filename)
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def quick_write(database, filename, version="unknown"):
    g = GrampsDbXmlWriter(database,0,1,version)
    g.write(filename)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GrampsDbXmlWriter(object):
    """
    Writes a database to the XML file.
    """

    def __init__(self,db,strip_photos,compress=1,version="unknown"):
        """
        Initializes, but does not write, an XML file.

        db - database to write
        strip_photos - remove paths off of media object paths
        >              0: do not touch the paths
        >              1: remove everything expect the filename
        >              2: remove leading slash
        compress - attempt to compress the database
        """
        self.compress = compress
        self.db = db
        self.strip_photos = strip_photos
        self.version = version

        self.status = None

    def write(self,filename):
        """
        Write the database to the specified file.
        """
        base = os.path.dirname(filename)
        if os.path.isdir(base):
            if not os.access(base,os.W_OK) or not os.access(base,os.R_OK):
                raise GrampsDbWriteFailure,\
                        (_('Failure writing %s') % filename,
                         _("The database cannot be saved because you do "
                           "not have permission to write to the directory. "
                           "Please make sure you have write access to the "
                            "directory and try again."))
                return 0
            
        if os.path.exists(filename):
            if not os.access(filename,os.W_OK):
                raise GrampsDbWriteFailure, \
                        (_('Failure writing %s') % filename,
                         _("The database cannot be saved because you do "
                           "not have permission to write to the file. "
                           "Please make sure you have write access to the "
                           "file and try again."))
                return 0
        
        self.fileroot = os.path.dirname(filename)
        try:
            if self.compress:
                try:
                    g = gzip.open(filename,"wb")
                except:
                    g = open(filename,"w")
            else:
                g = open(filename,"w")
        except IOError,msg:
            raise GrampsDbWriteFailure((_('Failure writing %s') % filename,msg))
            return 0

        self.g = codecs.getwriter("utf8")(g)

        self.write_xml_data()
        g.close()
        return 1

    def write_handle(self,handle):
        """
        Write the database to the specified file handle.
        """

        if self.compress:
            try:
                g = gzip.GzipFile(mode="wb",fileobj=handle)
            except:
                g = handle
        else:
            g = handle

        self.g = codecs.getwriter("utf8")(g)

        self.write_xml_data()
        g.close()
        return 1
            
    def write_xml_data(self):

        date = time.localtime(time.time())
        owner = self.db.get_researcher()

        person_len = self.db.get_number_of_people()
        family_len = self.db.get_number_of_families()
        event_len = self.db.get_number_of_events()
        source_len = self.db.get_number_of_sources()
        place_len = self.db.get_number_of_places()
        repo_len = self.db.get_number_of_repositories()
        obj_len = self.db.get_number_of_media_objects()
        note_len = self.db.get_number_of_notes()        
        
        total_steps = person_len + family_len + event_len + source_len \
                      + place_len + repo_len + obj_len + note_len
                       
        self.status = LongOpStatus(_("Writing XML ..."),
                                   total_steps=total_steps,
                                   interval=total_steps/10,
                                   can_cancel=False)
        self.db.emit('long-op-start', (self.status,))
        
        self.g.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.g.write('<!DOCTYPE database '
                     'PUBLIC "-//GRAMPS//DTD GRAMPS XML %s//EN"\n'
                     '"http://gramps-project.org/xml/%s/grampsxml.dtd">\n'
                     % (_xml_version,_xml_version))
        self.g.write('<database xmlns="http://gramps-project.org/xml/%s/">\n'
                     % _xml_version)
        self.g.write("  <header>\n")
        self.g.write('    <created date="%04d-%02d-%02d\"' %
                     (date[0],date[1],date[2]) )
        self.g.write(" version=\"" + self.version + "\"")
        self.g.write("/>\n")
        self.g.write("    <researcher>\n")
        self.write_line("resname",owner.get_name(),3)
        self.write_line("resaddr",owner.get_address(),3)
        self.write_line("rescity",owner.get_city(),3)
        self.write_line("resstate",owner.get_state(),3)
        self.write_line("rescountry",owner.get_country(),3)
        self.write_line("respostal",owner.get_postal_code(),3)
        self.write_line("resphone",owner.get_phone(),3)
        self.write_line("resemail",owner.get_email(),3)
        self.g.write("    </researcher>\n")
        self.g.write("  </header>\n")

        # First write name formats: we need to know all formats
        # by the time we get to person's names
        self.write_name_formats()

        if note_len > 0:
            self.g.write("  <notes>\n")
            sorted_keys = self.db.get_gramps_ids(NOTE_KEY)
            sorted_keys.sort()
            for gramps_id in sorted_keys:
                note = self.db.get_note_from_gramps_id(gramps_id)
                self.write_note(note,2)
                self.status.heartbeat()
            self.g.write("  </notes>\n")

        if event_len > 0:
            self.g.write("  <events>\n")
            sorted_keys = self.db.get_gramps_ids(EVENT_KEY)
            sorted_keys.sort ()
            for gramps_id in sorted_keys:
                event = self.db.get_event_from_gramps_id(gramps_id)
                self.write_event(event,2)
                self.status.heartbeat()
            self.g.write("  </events>\n")

        if person_len > 0:
            self.g.write("  <people")
            person = self.db.get_default_person()
            if person:
                self.g.write(' default="%s" home="_%s"' %
                             (person.gramps_id,person.handle))
            self.g.write('>\n')

            sorted_keys = self.db.get_gramps_ids(PERSON_KEY)
            sorted_keys.sort()

            for gramps_id in sorted_keys:
                person = self.db.get_person_from_gramps_id(gramps_id)
                self.write_person(person,2)
                self.status.heartbeat()
            self.g.write("  </people>\n")

        if family_len > 0:
            self.g.write("  <families>\n")
            sorted_keys = self.db.get_gramps_ids(FAMILY_KEY)
            sorted_keys.sort ()
            for gramps_id in sorted_keys:
                family = self.db.get_family_from_gramps_id(gramps_id)
                self.write_family(family,2)
                self.status.heartbeat()
            self.g.write("  </families>\n")

        if source_len > 0:
            self.g.write("  <sources>\n")
            keys = self.db.get_gramps_ids(SOURCE_KEY)
            keys.sort ()
            for key in keys:
                source = self.db.get_source_from_gramps_id(key)
                self.write_source(source,2)
            self.g.write("  </sources>\n")

        if place_len > 0:
            self.g.write("  <places>\n")
            keys = self.db.get_gramps_ids(PLACE_KEY)
            keys.sort ()
            for key in keys:
                # try:
                place = self.db.get_place_from_gramps_id(key)
                self.write_place_obj(place,2)
                self.status.heartbeat()
            self.g.write("  </places>\n")

        if obj_len > 0:
            self.g.write("  <objects>\n")
            sorted_keys = self.db.get_gramps_ids(MEDIA_KEY)
            sorted_keys.sort ()
            for gramps_id in sorted_keys:
                obj = self.db.get_object_from_gramps_id(gramps_id)
                self.write_object(obj,2)
                self.status.heartbeat()
            self.g.write("  </objects>\n")

        if repo_len > 0:
            self.g.write("  <repositories>\n")
            keys = self.db.get_gramps_ids(REPOSITORY_KEY)
            keys.sort ()
            for key in keys:
                repo = self.db.get_repository_from_gramps_id(key)
                self.write_repository(repo,2)
                self.status.heartbeat()
            self.g.write("  </repositories>\n")

        # Data is written, now write bookmarks.
        self.write_bookmarks()

        self.g.write("</database>\n")
        
        self.status.end()
        self.status = None

    def write_bookmarks(self):
        bm_person_len = len(self.db.bookmarks.get())
        bm_family_len = len(self.db.family_bookmarks.get())
        bm_event_len = len(self.db.event_bookmarks.get())
        bm_source_len = len(self.db.source_bookmarks.get())
        bm_place_len = len(self.db.place_bookmarks.get())
        bm_repo_len = len(self.db.repo_bookmarks.get())
        bm_obj_len = len(self.db.media_bookmarks.get())

        bm_len = bm_person_len + bm_family_len + bm_event_len \
                 + bm_source_len + bm_place_len + bm_repo_len + bm_obj_len
        
        if bm_len > 0:
            self.g.write("  <bookmarks>\n")

            for handle in self.db.get_bookmarks().get():
                self.g.write('    <bookmark target="person" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_family_bookmarks().get():
                self.g.write('    <bookmark target="family" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_event_bookmarks().get():
                self.g.write('    <bookmark target="event" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_source_bookmarks().get():
                self.g.write('    <bookmark target="source" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_place_bookmarks().get():
                self.g.write('    <bookmark target="place" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_media_bookmarks().get():
                self.g.write('    <bookmark target="media" hlink="_%s"/>\n'
                             % handle )
            for handle in self.db.get_repo_bookmarks().get():
                self.g.write('    <bookmark target="repository" hlink="_%s"/>\n'
                             % handle )
            self.g.write("  </bookmarks>\n")

    def write_name_formats(self):
        if len(self.db.name_formats) > 0:
            self.g.write("  <name-formats>\n")
            for number,name,fmt_str,active in self.db.name_formats:
                self.g.write('%s<format number="%d" name="%s" '
                             'fmt_str="%s" active="%d"/>\n'
                             % ('    ',number,name,fmt_str,int(active)) )
            self.g.write("  </name-formats>\n")

    def fix(self,line):
        try:
            l = unicode(line)
        except:
            l = unicode(str(line),errors='replace')
        l = l.strip().translate(strip_dict)
        return escxml(l)

    def write_note_list(self,note_list,indent=0):
        for handle in note_list:
            self.write_ref("noteref",handle,indent)

    def write_note(self,note,index=1):
        if not note:
            return

        self.write_primary_tag("note",note,2,close=False)

        ntype = escxml(note.get_type().xml_str())
        format = note.get_format()
        text = note.get(markup=True)

        self.g.write(' type="%s"' % ntype)
        if format != note.FLOWED:
            self.g.write(' format="%d"' % format)
        self.g.write('>')

        self.g.write(self.fix(text.rstrip()))
        self.g.write("</note>\n")

    def write_text(self,val,text,indent=0):
        if not text:
            return
        if indent != 0:
            self.g.write("  " * indent)
        
        self.g.write('<%s>' % val)
        self.g.write(self.fix(text.rstrip()))
        self.g.write("</%s>\n" % val)

    def write_person(self,person,index=1):
        sp = "  "*index
        self.write_primary_tag("person",person,index)
        if person.get_gender() == RelLib.Person.MALE:
            self.write_line("gender","M",index+1)
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.write_line("gender","F",index+1)
        else:
            self.write_line("gender","U",index+1)
        self.dump_name(person.get_primary_name(),False,index+1)
        for name in person.get_alternate_names():
            self.dump_name(name,True,index+1)

        #self.dump_event_ref(person.get_birth_ref(),index+1)
        #self.dump_event_ref(person.get_death_ref(),index+1)
        for event_ref in person.get_event_ref_list():
            self.dump_event_ref(event_ref,index+1)

        for lds_ord in person.lds_ord_list:
            self.dump_ordinance(lds_ord,index+1)

        self.write_media_list(person.get_media_list(),index+1)

        self.write_address_list(person,index+1)
        self.write_attribute_list(person.get_attribute_list())
        self.write_url_list(person.get_url_list(),index+1)

        for family_handle in person.get_parent_family_handle_list():
            self.write_ref("childof",family_handle,index+1)

        for family_handle in person.get_family_handle_list():
            self.write_ref("parentin",family_handle,index+1)

        for person_ref in person.get_person_ref_list():
            self.dump_person_ref(person_ref,index+1)

        self.write_note_list(person.get_note_list(),index+1)

        for s in person.get_source_references():
            self.dump_source_ref(s,index+2)
        self.g.write("%s</person>\n" % sp)

    def write_family(self,family,index=1):
        sp = "  "*index
        self.write_family_handle(family,index)
        fhandle = family.get_father_handle()
        mhandle = family.get_mother_handle()
        if fhandle:
            self.write_ref("father",fhandle,index+1)
        if mhandle:
            self.write_ref("mother",mhandle,index+1)
        for event_ref in family.get_event_ref_list():
            self.dump_event_ref(event_ref,3)
        for lds_ord in family.lds_ord_list:
            self.dump_ordinance(lds_ord,index+1)

        self.write_media_list(family.get_media_list(),index+1)

        for child_ref in family.get_child_ref_list():
            self.dump_child_ref(child_ref,index+1)
        self.write_attribute_list(family.get_attribute_list())
        self.write_note_list(family.get_note_list(),index+1)
        for s in family.get_source_references():
            self.dump_source_ref(s,index+1)
        self.g.write("%s</family>\n" % sp)

    def write_source(self,source,index=1):
        sp = "  "*index
        self.write_primary_tag("source",source,index)
        self.write_force_line("stitle",source.get_title(),index+1)
        self.write_line("sauthor",source.get_author(),index+1)
        self.write_line("spubinfo",source.get_publication_info(),index+1)
        self.write_line("sabbrev",source.get_abbreviation(),index+1)
        self.write_note_list(source.get_note_list(),index+1)
        self.write_media_list(source.get_media_list(),index+1)
        self.write_data_map(source.get_data_map())
        self.write_reporef_list(source.get_reporef_list(),index+1)
        self.g.write("%s</source>\n" % sp)

    def write_repository(self,repo,index=1):
        sp = "  "*index
        self.write_primary_tag("repository",repo,index)
        #name
        self.write_line('rname',repo.name,index+1)
        rtype = repo.type.xml_str()
        if rtype:
            self.write_line('type',rtype,index+1)
        #address list
        self.write_address_list(repo,index+1)
        # url list
        self.write_url_list(repo.get_url_list(),index+1)
        self.write_note_list(repo.get_note_list(),index+1)
        self.g.write("%s</repository>\n" % sp)

    def write_address_list(self,obj,index=1):
        if len(obj.get_address_list()) == 0:
            return
        sp = "  "*index
        for address in obj.get_address_list():
            self.g.write('%s<address%s>\n' % (sp,conf_priv(address)))
            self.write_date(address.get_date_object(),index+2)
            self.write_line("street",address.get_street(),index+2)
            self.write_line("city",address.get_city(),index+2)
            self.write_line("county",address.get_county(),index+2)
            self.write_line("state",address.get_state(),index+2)
            self.write_line("country",address.get_country(),index+2)
            self.write_line("postal",address.get_postal_code(),index+2)
            self.write_line("phone",address.get_phone(),index+2)
            self.write_note_list(address.get_note_list(),index+1)
            for s in address.get_source_references():
                self.dump_source_ref(s,index+2)
            self.g.write('%s</address>\n' % sp)

    def dump_person_ref(self,personref,index=1):
        if not personref or not personref.ref:
            return
        sp = "  "*index
        priv_text = conf_priv(personref)
        rel_text = ' rel="%s"' % escxml(personref.get_relation())

        sreflist = personref.get_source_references()
        nreflist = personref.get_note_list()
        if (len(sreflist) + len(nreflist) == 0):
            self.write_ref('personref',personref.ref,index,close=True,
                           extra_text=priv_text+rel_text)
        else:
            self.write_ref('personref',personref.ref,index,close=False,
                           extra_text=priv_text+rel_text)
            for sref in sreflist:
                self.dump_source_ref(sref,index+1)
            self.write_note_list(nreflist,index+1)
            self.g.write('%s</personref>\n' % sp)

    def dump_child_ref(self,childref,index=1):
        if not childref or not childref.ref:
            return
        sp = "  "*index
        priv_text = conf_priv(childref)
        if childref.frel.is_default():
            frel_text = ''
        else:
            frel_text = ' frel="%s"' % escxml(childref.frel.xml_str())
        if childref.mrel.is_default():
            mrel_text = ''
        else:
            mrel_text = ' mrel="%s"' % escxml(childref.mrel.xml_str())
        sreflist = childref.get_source_references()
        nreflist = childref.get_note_list()
        if (len(sreflist)+len(nreflist) == 0):
            self.write_ref('childref',childref.ref,index,close=True,
                           extra_text=priv_text+mrel_text+frel_text)
        else:
            self.write_ref('childref',childref.ref,index,close=False,
                           extra_text=priv_text+mrel_text+frel_text)
            for sref in sreflist:
                self.dump_source_ref(sref,index+1)
            self.write_note_list(nreflist,index+1)
            self.g.write('%s</childref>\n' % sp)
        
    def dump_event_ref(self,eventref,index=1):
        if not eventref or not eventref.ref:
            return
        sp = "  "*index
        priv_text = conf_priv(eventref)
        role = escxml(eventref.role.xml_str())
        if role:
            role_text = ' role="%s"' % role
        else:
            role_text = ''

        attribute_list = eventref.get_attribute_list()
        note_list = eventref.get_note_list()
        if (len(attribute_list) + len(note_list) == 0):
            self.write_ref('eventref',eventref.ref,index,
                           close=True,extra_text=priv_text+role_text)
        else:
            self.write_ref('eventref',eventref.ref,index,
                           close=False,extra_text=priv_text+role_text)
            self.write_attribute_list(attribute_list,index+1)
            self.write_note_list(note_list,index+1)
            self.g.write('%s</eventref>\n' % sp)

    def write_event(self,event,index=1):
        if not event:
            return

        self.write_primary_tag("event",event,2)

        sp = "  " * index
        etype = event.get_type().xml_str()
        self.g.write('  %s<type>%s</type>\n' % (sp,self.fix(etype)) )
        self.write_date(event.get_date_object(),index+1)
        self.write_ref("place",event.get_place_handle(),index+1)
        self.write_line("description",event.get_description(),index+1)
        self.write_attribute_list(event.get_attribute_list(),index+1)
        self.write_note_list(event.get_note_list(),index+1)
            
        for s in event.get_source_references():
            self.dump_source_ref(s,index+1)
        self.write_media_list(event.get_media_list(),index+1)
        self.g.write("%s</event>\n" % sp)

    def dump_ordinance(self,ord,index=1):

        name = ord.type2xml()

        sp = "  " * index
        sp2 = "  " * (index+1)
        self.g.write('%s<lds_ord type="%s">\n' % (sp,name))
        dateobj = ord.get_date_object()
        if dateobj and not dateobj.is_empty():
            self.write_date(dateobj,index+1)
        if ord.get_temple():
            self.g.write('%s<temple val="%s"/>\n'
                         % (sp2,self.fix(ord.get_temple())))
        self.write_ref("place",ord.get_place_handle(),index+1)
        if ord.get_status() != 0:
            self.g.write('%s<status val="%s"/>\n' % (sp2,ord.status2xml()))
        if ord.get_family_handle():
            self.g.write('%s<sealed_to hlink="%s"/>\n' % 
                         (sp2,"_"+ord.get_family_handle()))
        self.write_note_list(ord.get_note_list(),index+1)
        for s in ord.get_source_references():
            self.dump_source_ref(s,index+1)
        self.g.write('%s</lds_ord>\n' % sp)
    
    def dump_source_ref(self,source_ref,index=1):
        source = self.db.get_source_from_handle(
            source_ref.get_reference_handle())
        if source:
            p = source_ref.get_page()
            n = source_ref.get_note_list()
            t = source_ref.get_text()
            d = source_ref.get_date_object()
            q = source_ref.get_confidence_level()
            self.g.write("  " * index)
            if p == "" and n == [] and t == "" and d.is_empty() and q == 2:
                self.g.write('<sourceref hlink="%s"/>\n' % ("_"+source.get_handle()))
            else:
                if q == 2:
                    self.g.write('<sourceref hlink="%s">\n' % ("_"+source.get_handle()))
                else:
                    self.g.write('<sourceref hlink="%s" conf="%d">\n' % ("_"+source.get_handle(),q))
                self.write_line("spage",p,index+1)
                # FIXME: Do we really need scomments? One or many?
                # Gedcom standard seems to allow normal notes in sourcerefs:
# http://homepages.rootsweb.com/~pmcbride/gedcom/55gcch2.htm#SOURCE_CITATION
                self.write_note_list(n,index+1)
                # for handle in n:
                #     self.write_ref("scomments",handle,index+1)
                self.write_text("stext",t,index+1)
                self.write_date(d,index+1)
                self.g.write("%s</sourceref>\n" % ("  " * index))

    def write_ref(self,tagname,handle,index=1,close=True,extra_text=''):
        if handle:
            if close:
                close_tag = "/"
            else:
                close_tag = ""
            sp = "  "*index
            self.g.write('%s<%s hlink="_%s"%s%s>\n'
                         % (sp,tagname,handle,extra_text,close_tag))

    def write_primary_tag(self,tagname,obj,index=1,close=True):
        if not obj:
            return
        sp = "  "*index
        marker = obj.get_marker().xml_str()
        if marker:
            marker_text = ' marker="%s"' % escxml(marker)
        else:
            marker_text = ''
        priv_text = conf_priv(obj)
        change_text = ' change="%d"' % obj.get_change_time()
        handle_id_text = ' id="%s" handle="_%s"' % (obj.gramps_id,obj.handle)
        obj_text = '%s<%s' % (sp,tagname)

        self.g.write(obj_text + handle_id_text + priv_text + marker_text +
                     change_text)
        if close:
            self.g.write('>\n')

    def write_family_handle(self,family,index=1):
        sp = "  "*index
        self.write_primary_tag('family',family,index)
        if family:
            rel = escxml(family.get_relationship().xml_str())
            if rel != "":
                self.g.write('  %s<rel type="%s"/>\n' % (sp,rel) )

    def write_last(self,name,indent=1):
        p = name.get_surname_prefix()
        n = name.get_surname()
        g = name.get_group_as()
        self.g.write('%s<last' % ('  '*indent))
        if p:
            self.g.write(' prefix="%s"' % escxml(p))
        if g:
            self.g.write(' group="%s"' % escxml(g))
        self.g.write('>%s</last>\n' % self.fix(n))

    def write_line(self,tagname,value,indent=1):
        if value:
            self.g.write('%s<%s>%s</%s>\n' %
                         ('  '*indent,tagname,self.fix(value),tagname))

    def get_iso_date(self,date):
        if date[2] == 0:
            y = "????"
        else:
            y = "%04d" % date[2]
            
        if date[1] == 0:
            if date[0] == 0:
                m = ""
            else:
                m = "-??"
        else:
            m = "-%02d" % (date[1])
        if date[0] == 0:
            d = ''
        else:
            d = "-%02d" % date[0]
        ret = "%s%s%s" % (y,m,d)
        # If the result does not contain anything beyond dashes
        # and question marks then it's as good as empty
        if ret.replace('-','').replace('?','') == '':
            ret = ''
        return ret

    def write_date(self,date,indent=1):
        sp = '  '*indent

        cal= date.get_calendar()
        if cal != RelLib.Date.CAL_GREGORIAN:
            calstr = ' cformat="%s"' % RelLib.Date.calendar_names[cal]
        else:
            calstr = ''

        qual = date.get_quality()
        if qual == RelLib.Date.QUAL_ESTIMATED:
            qual_str = ' quality="estimated"'
        elif qual == RelLib.Date.QUAL_CALCULATED:
            qual_str = ' quality="calculated"'
        else:
            qual_str = ""
            
        mode = date.get_modifier()
        
        if date.is_compound():
            d1 = self.get_iso_date(date.get_start_date())
            d2 = self.get_iso_date(date.get_stop_date())
            if d1 != "" or d2 != "":
                self.g.write('%s<daterange start="%s" stop="%s"%s%s/>\n'
                             % (sp,d1,d2,qual_str,calstr))
        elif mode != RelLib.Date.MOD_TEXTONLY:
            date_str = self.get_iso_date(date.get_start_date())
            if date_str == "":
                return
            
            if mode == RelLib.Date.MOD_BEFORE:
                mode_str = ' type="before"'
            elif mode == RelLib.Date.MOD_AFTER:
                mode_str = ' type="after"'
            elif mode == RelLib.Date.MOD_ABOUT:
                mode_str = ' type="about"'
            else:
                mode_str = ""

            self.g.write('%s<dateval val="%s"%s%s%s/>\n'
                         % (sp,date_str,mode_str,qual_str,calstr))
        else:
            self.g.write('%s<datestr val="%s"/>\n'
                         %(sp,self.fix(date.get_text())))

    def write_force_line(self,label,value,indent=1):
        if value != None:
            self.g.write('%s<%s>%s</%s>\n' % ('  '*indent,label,self.fix(value),label))

    def dump_name(self,name,alternative=False,index=1):
        sp = "  "*index
        name_type = name.get_type().xml_str()
        self.g.write('%s<name' % sp)
        if alternative:
            self.g.write(' alt="1"')
        if name_type:
            self.g.write(' type="%s"' % escxml(name_type))
        if name.get_privacy() != 0:
            self.g.write(' priv="%d"' % name.get_privacy())
        if name.get_sort_as() != 0:
            self.g.write(' sort="%d"' % name.get_sort_as())
        if name.get_display_as() != 0:
            self.g.write(' display="%d"' % name.get_display_as())
        self.g.write('>\n')
        self.write_line("first",name.get_first_name(),index+1)
        self.write_line("call",name.get_call_name(),index+1)
        self.write_last(name,index+1)
        self.write_line("suffix",name.get_suffix(),index+1)
        self.write_line("patronymic",name.get_patronymic(),index+1)
        self.write_line("title",name.get_title(),index+1)
        if name.date:
            self.write_date(name.date,4)
        self.write_note_list(name.get_note_list(),index+1)
        for s in name.get_source_references():
            self.dump_source_ref(s,index+1)
    
        self.g.write('%s</name>\n' % sp)

    def append_value(self,orig,val):
        if orig:
            return "%s, %s" % (orig,val)
        else:
            return val

    def build_place_title(self,loc):
        "Builds a title from a location"
        city = self.fix(loc.get_city())
        street = self.fix(loc.get_street())
        parish = self.fix(loc.get_parish())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())
        county = self.fix(loc.get_county())

        value = ""

        if street:
            value = street
        if city:
            value = self.append_value(value,city)
        if parish:
            value = self.append_value(value,parish)
        if county:
            value = self.append_value(value,county)
        if state:
            value = self.append_value(value,state)
        if country:
            value = self.append_value(value,country)
        return value

    def dump_location(self,loc):
        "Writes the location information to the output file"
        if loc.is_empty():
            return
        city = self.fix(loc.get_city())
        parish = self.fix(loc.get_parish())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())
        county = self.fix(loc.get_county())
        zip_code = self.fix(loc.get_postal_code())
        phone = self.fix(loc.get_phone())
        street = self.fix(loc.get_street())
        
        self.g.write('      <location')
        if street:
            self.g.write(' street="%s"' % street)
        if city:
            self.g.write(' city="%s"' % city)
        if parish:
            self.g.write(' parish="%s"' % parish)
        if county:
            self.g.write(' county="%s"' % county)
        if state:
            self.g.write(' state="%s"' % state)
        if country:
            self.g.write(' country="%s"' % country)
        if zip_code:
            self.g.write(' postal="%s"' % zip_code)
        if phone:
            self.g.write(' phone="%s"' % phone)
        self.g.write('/>\n')

    def write_attribute_list(self, list, indent=3):
        sp = '  ' * indent
        for attr in list:
            self.g.write('%s<attribute%s type="%s" value="%s"' % \
                         (sp,conf_priv(attr),escxml(attr.get_type().xml_str()),
                         self.fix(attr.get_value())))
            slist = attr.get_source_references()
            nlist = attr.get_note_list()
            if (len(nlist)+len(slist)) == 0:
                self.g.write('/>\n')
            else:
                self.g.write('>\n')
                for s in attr.get_source_references():
                    self.dump_source_ref(s,indent+1)
                self.write_note_list(attr.get_note_list(),indent+1)
                self.g.write('%s</attribute>\n' % sp)

    def write_media_list(self,list,indent=3):
        sp = '  '*indent
        for photo in list:
            mobj_id = photo.get_reference_handle()
            self.g.write('%s<objref hlink="%s"' % (sp,"_"+mobj_id))
            if photo.get_privacy():
                self.g.write(' priv="1"')
            proplist = photo.get_attribute_list()
            refslist = photo.get_source_references()
            nreflist = photo.get_note_list()
            if (len(proplist) + len(nreflist) + len(refslist)) == 0:
                self.g.write("/>\n")
            else:
                self.g.write(">\n")
                self.write_attribute_list(proplist,indent+1)
                for ref in refslist:
                    self.dump_source_ref(ref,indent+1)
                self.write_note_list(nreflist,index+1)
                self.g.write('%s</objref>\n' % sp)

    def write_data_map(self,datamap,indent=3):
        if len(datamap) == 0:
            return
        
        sp = '  '*indent
        for key in datamap.keys():
            self.g.write('%s<data_item key="%s" value="%s"/>\n' %
                         (sp,self.fix(key),self.fix(datamap[key])))

    def write_reporef_list(self,rrlist,index=1):
        for reporef in rrlist:
            if not reporef or not reporef.ref:
                continue

            if reporef.call_number == "":
                callno_text = ''
            else:
                callno_text = ' callno="%s"' % escxml(reporef.call_number)
                
            mtype = reporef.media_type.xml_str()
            if mtype:
                type_text = ' medium="%s"' % escxml(mtype)
            else:
                type_text = ''

            note_list = reporef.get_note_list()
            if  len(note_list) == 0:
                self.write_ref('reporef',reporef.ref,index,
                               close=True,extra_text=callno_text+type_text)
            else:
                self.write_ref('reporef',reporef.ref,index,
                               close=False,extra_text=callno_text+type_text)
                self.write_note_list(note_list,index+1)
                sp = "  "*index
                self.g.write('%s</reporef>\n' % sp)            
            
    def write_url_list(self,list,index=1):
        sp = "  "*index
        for url in list:
            url_type = url.get_type().xml_str()
            if url_type:
                type_text = ' type="%s"' % escxml(url_type)
            else:
                type_text = ''
            priv_text = conf_priv(url)
            if url.get_description() != "":
                desc_text = ' description="%s"' % self.fix(
                    url.get_description())
            else:
                desc_text = ''
            path_text = '  href="%s"' % self.fix(url.get_path())
            self.g.write('%s<url%s%s%s%s/>\n' % \
                         (sp,priv_text,path_text,type_text,desc_text))

    def write_place_obj(self,place,index=1):
        self.write_primary_tag("placeobj",place,index)

        title = self.fix(place.get_title())
        longitude = self.fix(place.get_longitude())
        lat = self.fix(place.get_latitude())
        handle = place.get_gramps_id()
        main_loc = place.get_main_location()
        llen = len(place.get_alternate_locations()) \
               + len(place.get_url_list()) + \
               len(place.get_media_list()) + \
               len(place.get_source_references())
                                                      
        ml_empty = main_loc.is_empty()

        if title == "":
            title = self.fix(self.build_place_title(place.get_main_location()))
        self.write_line("ptitle",title,index+1)
    
        if longitude or lat:
            self.g.write('%s<coord long="%s" lat="%s"/>\n'
                         % ("  "*(index+1),longitude,lat))
        self.dump_location(main_loc)
        for loc in place.get_alternate_locations():
            self.dump_location(loc)
        self.write_media_list(place.get_media_list(),index+1)
        self.write_url_list(place.get_url_list())
        self.write_note_list(place.get_note_list(),index+1)
        for s in place.get_source_references():
            self.dump_source_ref(s,index+1)
        self.g.write("%s</placeobj>\n" % ("  "*index))

    def write_object(self,obj,index=1):
        self.write_primary_tag("object",obj,index)
        handle = obj.get_gramps_id()
        mime_type = obj.get_mime_type()
        path = obj.get_path()
        desc = obj.get_description()
        if desc:
            desc_text = ' description="%s"' % self.fix(desc)
        else:
            desc_text = ''
        if self.strip_photos == 1:
            path = os.path.basename(path)
        elif self.strip_photos == 2 and (len(path)>0 and os.path.isabs(path)):
            drive,path = os.path.splitdrive(path)
            path = path[1:]
                
        self.g.write('%s<file src="%s" mime="%s"%s/>\n'
                     % ("  "*(index+1),self.fix(path),mime_type,desc_text))
        self.write_attribute_list(obj.get_attribute_list())
        self.write_note_list(obj.get_note_list(),index+1)
        dval = obj.get_date_object()
        if not dval.is_empty():
            self.write_date(dval,index+1)
        for s in obj.get_source_references():
            self.dump_source_ref(s,index+1)
        self.g.write("%s</object>\n" % ("  "*index))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sortById(first,second):
    fid = first.get_gramps_id()
    sid = second.get_gramps_id()

    if fid < sid:
        return -1
    else:
        return fid != sid

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def conf_priv(obj):
    if obj.get_privacy() != 0:
        return ' priv="%d"' % obj.get_privacy()
    else:
        return ''

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('GRAMPS _XML database')
_description = _('The GRAMPS XML database is a format used by older '
                'versions of GRAMPS. It is read-write compatible with '
                'the present GRAMPS database format.')
_config = None
_filename = 'gramps'

from PluginUtils import register_export
register_export(exportData,_title,_description,_config,_filename)
