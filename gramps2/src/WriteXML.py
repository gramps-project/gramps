#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"""
Contains the interface to allow a database to get written using
GRAMPS' XML file format.
"""

#-------------------------------------------------------------------------
#
# load standard python libraries
#
#-------------------------------------------------------------------------
import string
import time
import shutil
import os
import codecs

#-------------------------------------------------------------------------
#
# load gtk libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------
import const
import RelLib 
import Date

from gettext import gettext as _
from QuestionDialog import ErrorDialog

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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, person, callback=None):
    ret = 0
    if os.path.isfile(filename):
        try:
            shutil.copyfile(filename, filename + ".bak")
            shutil.copystat(filename, filename + ".bak")
        except:
            pass

    compress = _gzip_ok == 1

    try:
        g = XmlWriter(database,callback,0,compress)
        ret = g.write(filename)
    except:
        import DisplayTrace

        DisplayTrace.DisplayTrace() 
        ErrorDialog(_("Failure writing %s") % filename,
                    _("An attempt is being made to recover the original file"))
        shutil.copyfile(filename + ".bak", filename)
        try:
            shutil.copystat(filename + ".bak", filename)
        except:
            pass
    
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def quick_write(database, filename,callback=None):
    g = XmlWriter(database,callback,0,1)
    g.write(filename)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class XmlWriter:
    """
    Writes a database to the XML file.
    """

    def __init__(self,db,callback,strip_photos,compress=1):
        """
        Initializes, but does not write, an XML file.

        db - database to write
        callback - function to provide progress indication
        strip_photos - remove full paths off of media object paths
        compress - attempt to compress the database
        """
        self.compress = compress
        self.db = db
        self.callback = callback
        self.strip_photos = strip_photos
        
    def write(self,filename):
        """
        Write the database to the specified file.
        """
        base = os.path.dirname(filename)
        if os.path.isdir(base):
            if not os.access(base,os.W_OK) or not os.access(base,os.R_OK):
                ErrorDialog(_('Failure writing %s') % filename,
                            _("The database cannot be saved because you do not "
                              "have permission to write to the directory. "
                              "Please make sure you have write access to the "
                              "directory and try again."))
                return 0
            
        if os.path.exists(filename):
            if not os.access(filename,os.W_OK):
                ErrorDialog(_('Failure writing %s') % filename,
                            _("The database cannot be saved because you do not "
                              "have permission to write to the file. "
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
            ErrorDialog(_('Failure writing %s') % filename,msg)
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
            
    def write_xml_data(self):

        date = string.split(time.ctime(time.time()))
        owner = self.db.get_researcher()
        person_len = self.db.get_number_of_people()
        family_len = len(self.db.get_family_handles())
        source_len = len(self.db.get_source_handles())
        place_len = len(self.db.get_place_handles())
        objList = self.db.get_media_object_handles()
        
        total = person_len + family_len + place_len + source_len

        self.g.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.g.write('<!DOCTYPE database SYSTEM "gramps.dtd" []>\n')
        self.g.write("<database xmlns=\"http://gramps.sourceforge.net/database\">\n")
        self.g.write("  <header>\n")
        self.g.write("    <created date=\"%s %s %s\"" % \
                     (date[2],string.upper(date[1]),date[4]))
        self.g.write(" version=\"" + const.version + "\"")
        self.g.write(" people=\"%d\"" % person_len)
        self.g.write(" families=\"%d\"" % family_len)
        self.g.write(" sources=\"%d\"" % source_len)
        self.g.write(" places=\"%d\"/>\n" % place_len)
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

        count = 0
        delta = max(int(total/50),1)

        if person_len > 0:
            self.g.write("  <people")
            person = self.db.get_default_person()
            if person:
                self.g.write(' default="%s" home="%s"' %
                             (person.get_gramps_id (),
                              person.get_handle()))
            self.g.write(">\n")

            keys = self.db.get_person_handles(sort_handles=False)
            sorted_keys = []
            for key in keys:
                person = self.db.get_person_from_handle (key)
                value = (person.get_gramps_id (), person)
                sorted_keys.append (value)

            sorted_keys.sort ()
            for (gramps_id, person) in sorted_keys:
                if self.callback and count % delta == 0:
                    self.callback(float(count)/float(total))
                count += 1
            
                self.write_id("person",person,2)
                if person.get_gender() == RelLib.Person.male:
                    self.write_line("gender","M",3)
                elif person.get_gender() == RelLib.Person.female:
                    self.write_line("gender","F",3)
                else:
                    self.write_line("gender","U",3)
                self.dump_name("name",person.get_primary_name(),3)
                for name in person.get_alternate_names():
                    self.dump_name("aka",name,3)
            
                self.write_line("nick",person.get_nick_name(),3)
                birth = self.db.get_event_from_handle(person.get_birth_handle())
                death = self.db.get_event_from_handle(person.get_death_handle())
                self.dump_my_event("Birth",birth,3)
                self.dump_my_event("Death",death,3)
                for event_handle in person.get_event_list():
                    event = self.db.get_event_from_handle(event_handle)
                    self.dump_event(event,3)
                
                self.dump_ordinance("baptism",person.get_lds_baptism(),3)
                self.dump_ordinance("endowment",person.get_lds_endowment(),3)
                self.dump_ordinance("sealed_to_parents",person.get_lds_sealing(),3)

                self.write_media_list(person.get_media_list())

                if len(person.get_address_list()) > 0:
                    for address in person.get_address_list():
                        self.g.write('      <address%s>\n' % conf_priv(address))
                        self.write_date(address.get_date_object(),4)
                        self.write_line("street",address.get_street(),4)
                        self.write_line("city",address.get_city(),4)
                        self.write_line("state",address.get_state(),4)
                        self.write_line("country",address.get_country(),4)
                        self.write_line("postal",address.get_postal_code(),4)
                        self.write_line("phone",address.get_phone(),4)
                        if address.get_note() != "":
                            self.write_note("note",address.get_note_object(),4)
                        for s in address.get_source_references():
                            self.dump_source_ref(s,4)
                        self.g.write('      </address>\n')

                self.write_attribute_list(person.get_attribute_list())
                self.write_url_list(person.get_url_list())

                for alt in person.get_parent_family_handle_list():
                    if alt[1] != "Birth":
                        mrel=' mrel="%s"' % alt[1]
                    else:
                        mrel=''
                    if alt[2] != "Birth":
                        frel=' frel="%s"' % alt[2]
                    else:
                        frel=''
                    parent_family = self.db.get_family_from_handle (alt[0])
                    self.g.write("      <childof hlink=\"%s\"%s%s/>\n" % \
                            (parent_family.get_handle(), mrel, frel))

                for family_handle in person.get_family_handle_list():
                    family = self.db.get_family_from_handle (family_handle)
                    self.write_ref("parentin",family.get_handle(),3)

                self.write_note("note",person.get_note_object(),3)
                for s in person.get_source_references():
                    self.dump_source_ref(s,4)

                self.g.write("    </person>\n")
            self.g.write("  </people>\n")

        if family_len > 0:
            self.g.write("  <families>\n")

            keys = self.db.get_family_handles()
            sorted_keys = []
            for key in keys:
                 family = self.db.get_family_from_handle(key)
                 value = (family.get_gramps_id (), family)
                 sorted_keys.append (value)

            sorted_keys.sort ()
            for (gramps_id, family) in sorted_keys:
                if self.callback and count % delta == 0:
                    self.callback(float(count)/float(total))
                count = count + 1
            
                self.write_family_handle(family,2)
                fhandle = family.get_father_handle()
                mhandle = family.get_mother_handle()
                if fhandle:
                    fid = self.db.get_person_from_handle (fhandle).get_handle()
                    self.write_ref("father",fid,3)
                if mhandle:
                    mid = self.db.get_person_from_handle (mhandle).get_handle()
                    self.write_ref("mother",mid,3)
                for event_handle in family.get_event_list():
                    event = self.db.get_event_from_handle(event_handle)
                    self.dump_event(event,3)
                self.dump_ordinance("sealed_to_spouse",family.get_lds_sealing(),3)

                self.write_media_list(family.get_media_list())

                if len(family.get_child_handle_list()) > 0:
                    for person_handle in family.get_child_handle_list():
                        person = self.db.get_person_from_handle (person_handle)
                        self.write_ref("child",person.get_handle(),3)
                self.write_attribute_list(family.get_attribute_list())
                self.write_note("note",family.get_note_object(),3)
                for s in family.get_source_references():
                    self.dump_source_ref(s,3)
                self.g.write("    </family>\n")
            self.g.write("  </families>\n")

        if source_len > 0:
            self.g.write("  <sources>\n")
            keys = self.db.get_source_handles ()
            keys.sort ()
            for key in keys:
                source = self.db.get_source_from_handle(key)
                if self.callback and count % delta == 0:
                    self.callback(float(count)/float(total))
                count = count + 1
                self.g.write("    <source id=\"%s\" handle=\"%s\" change=\"%d\">\n" %
                             (source.get_gramps_id(), source.get_handle(), source.get_change_time()))
                self.write_force_line("stitle",source.get_title(),3)
                self.write_line("sauthor",source.get_author(),3)
                self.write_line("spubinfo",source.get_publication_info(),3)
                self.write_line("sabbrev",source.get_abbreviation(),3)
                if source.get_note() != "":
                    self.write_note("note",source.get_note_object(),3)
                self.write_media_list(source.get_media_list())
                self.g.write("    </source>\n")
            self.g.write("  </sources>\n")

        if place_len > 0:
            self.g.write("  <places>\n")
            keys = self.db.get_place_handles()
            keys.sort ()
            for key in keys:
                try:
                    place = self.db.get_place_from_handle(key)
                    if self.callback and count % delta == 0:
                        self.callback(float(count)/float(total))
                    self.write_place_obj(place)
                except:
                    print "Could not find place %s" % key
                count = count + 1
                    
            self.g.write("  </places>\n")

        if len(objList) > 0:
            self.g.write("  <objects>\n")
            keys = self.db.get_media_object_handles()
            sorted_keys = []
            for key in keys:
                obj = self.db.get_object_from_handle (key)
                value = (obj.get_gramps_id (), obj)
                sorted_keys.append (value)

            sorted_keys.sort ()
            for (gramps_id, obj) in sorted_keys:
                self.write_object(obj)
            self.g.write("  </objects>\n")

        if len(self.db.get_bookmarks()) > 0:
            self.g.write("  <bookmarks>\n")
            for person_handle in self.db.get_bookmarks():
                self.g.write('    <bookmark hlink="%s"/>\n' % person_handle)
            self.g.write("  </bookmarks>\n")

        if len(self.db.name_group) > 0:
            self.g.write('  <groups>\n')
            for key in self.db.name_group.keys():
                self.g.write('    <group_map name="%s" group="%s"/>\n' %
                             (key,self.db.name_group[key]))
            self.g.write('  </groups>\n')

        self.g.write("</database>\n")

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def write_note(self,val,noteobj,indent=0):
        if not noteobj:
            return
        text = noteobj.get()
        if not text:
            return
        if indent != 0:
            self.g.write("  " * indent)
        
        format = noteobj.get_format()
        if format:
            self.g.write('<%s format="%d">' % (val,format))
        else:
            self.g.write('<%s>' % val)
        self.g.write(self.fix(string.rstrip(text)))
        self.g.write("</%s>\n" % val)

    def write_text(self,val,text,indent=0):
        if not text:
            return
        if indent != 0:
            self.g.write("  " * indent)
        
        self.g.write('<%s>' % val)
        self.g.write(self.fix(string.rstrip(text)))
        self.g.write("</%s>\n" % val)

    def dump_event(self,event,index=1):
        if event:
            self.dump_my_event(event.get_name(),event,index)

    def write_witness(self,witness_list,index):
        if not witness_list:
            return
        for w in witness_list:
            sp = "  "*index
            com = self.fix(w.get_comment())
            if w.get_type() == RelLib.Event.ID:
                self.g.write('%s<witness>\n' % sp)
                self.g.write('  %s<ref>%s</ref>\n' % (sp,w.get_value()))
                if com:
                    self.g.write('  %s<comment>%s</comment>\n' % (sp,com))
                self.g.write('%s</witness>\n' % sp)
            else:
                nm = self.fix(w.get_value())
                self.g.write('%s<witness>\n' % sp)
                self.g.write('  %s<name>%s</name>\n' % (sp,nm))
                if com:
                    self.g.write('  %s<comment>%s</comment>\n' % (sp,com))
                self.g.write('%s</witness>\n' % sp)

    def dump_my_event(self,name,event,index=1):
        if not event or event.is_empty():
            return

        sp = "  " * index
        name = const.save_event(name) 
        self.g.write('%s<event type="%s"%s>\n' % (sp,self.fix(name),conf_priv(event)))
        self.write_date(event.get_date_object(),index+1)

        self.write_witness(event.get_witness_list(),index+1)
        self.write_ref("place",event.get_place_handle(),index+1)
        self.write_line("cause",event.get_cause(),index+1)
        self.write_line("description",event.get_description(),index+1)
        if event.get_note():
            self.write_note("note",event.get_note_object(),index+1)
            
        for s in event.get_source_references():
            self.dump_source_ref(s,index+1)
        self.write_media_list(event.get_media_list(),index+1)
        self.g.write("%s</event>\n" % sp)

    def dump_ordinance(self,name,ord,index=1):
        if not ord:
            return

        sp = "  " * index
        sp2 = "  " * (index+1)
        self.g.write('%s<lds_ord type="%s">\n' % (sp,self.fix(name)))
        dateobj = ord.get_date_object()
        if dateobj != None and not dateobj.is_empty():
            self.write_date(dateobj,index+1)
        if ord.get_temple():
            self.g.write('%s<temple val="%s"/>\n' % (sp2,self.fix(ord.get_temple())))
        self.write_ref("place",ord.get_place_handle(),index+1)
        if ord.get_status() != 0:
            self.g.write('%s<status val="%d"/>\n' % (sp2,ord.get_status()))
        if ord.get_family_handle():
            self.g.write('%s<sealed_to hlink="%s"/>\n' % \
                         (sp2,self.fix(ord.get_family_handle().get_handle())))
        if ord.get_note() != "":
            self.write_note("note",ord.get_note_object(),index+1)
        for s in ord.get_source_references():
            self.dump_source_ref(s,index+1)
        self.g.write('%s</lds_ord>\n' % sp)
    
    def dump_source_ref(self,source_ref,index=1):
        source = self.db.get_source_from_handle(source_ref.get_base_handle())
        if source:
            p = source_ref.get_page()
            c = source_ref.get_comments()
            t = source_ref.get_text()
            d = source_ref.get_date()
            q = source_ref.get_confidence_level()
            self.g.write("  " * index)
            if p == "" and c == "" and t == "" and d.is_empty() and q == 2:
                self.g.write('<sourceref hlink="%s"/>\n' % source.get_handle())
            else:
                if q == 2:
                    self.g.write('<sourceref hlink="%s">\n' % source.get_handle())
                else:
                    self.g.write('<sourceref hlink="%s" conf="%d">\n' % (source.get_handle(),q))
                self.write_line("spage",p,index+1)
                self.write_text("scomments",c,index+1)
                self.write_text("stext",t,index+1)
                self.write_date(d,index+1)
                self.g.write("%s</sourceref>\n" % ("  " * index))

    def write_ref(self,label,gid,index=1):
        if gid:
            self.g.write('%s<%s hlink="%s"/>\n' % ("  "*index,label,gid))

    def write_id(self,label,person,index=1):
        if person:
            self.g.write('%s<%s id="%s" handle="%s" change="%d"' %
                         ("  "*index,label,person.get_gramps_id(),person.get_handle(),
                          person.get_change_time()))
            comp = person.get_complete_flag()
            if comp:
                self.g.write(' complete="1"')
            self.g.write('>\n')

    def write_family_handle(self,family,index=1):
        if family:
            rel = family.get_relationship()
            comp = family.get_complete_flag()
            sp = "  " * index
            self.g.write('%s<family id="%s" handle="%s" change="%d"' %
                         (sp,family.get_gramps_id(),family.get_handle(),family.get_change_time()))
            if comp:
                self.g.write(' complete="1"')
            if rel != "":
                self.g.write(' type="%s">\n' % const.save_frel(rel))
            else:
                self.g.write('>\n')

    def write_last(self,name,indent=1):
        p = name.get_surname_prefix()
        n = name.get_surname()
        g = name.get_group_as()
        self.g.write('%s<last' % ('  '*indent))
        if p:
            self.g.write(' prefix="%s"' % p)
        if g:
            self.g.write(' group="%s"' % g)
        self.g.write('>%s</last>\n' % self.fix(n))

    def write_line(self,label,value,indent=1):
        if value:
            self.g.write('%s<%s>%s</%s>\n' % ('  '*indent,label,self.fix(value),label))

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
        return "%s%s%s" % (y,m,d)

    def write_date(self,date,indent=1):
        sp = '  '*indent

        cal= date.get_calendar()
        if cal != Date.CAL_GREGORIAN:
            calstr = ' cformat="%s"' % Date.Date.calendar_names[cal]
        else:
            calstr = ''

        mode = date.get_modifier()
        
        if date.is_compound():
            d1 = self.get_iso_date(date.get_start_date())
            d2 = self.get_iso_date(date.get_stop_date())
            self.g.write('%s<daterange start="%s" stop="%s"%s/>\n' % (sp,d1,d2,calstr))
        elif mode != Date.MOD_TEXTONLY:
            dstr = self.get_iso_date(date.get_start_date())
            
            if mode == Date.MOD_BEFORE:
                pref = ' type="before"'
            elif mode == Date.MOD_AFTER:
                pref = ' type="after"'
            elif mode == Date.MOD_ABOUT:
                pref = ' type="about"'
            else:
                pref = ""
            
            self.g.write('%s<dateval val="%s"%s%s/>\n' % (sp,dstr,pref,calstr))
        else:
            self.g.write('%s<datestr val="%s"/>\n' %(sp,self.fix(date.get_text())))

    def write_force_line(self,label,value,indent=1):
        if value != None:
            self.g.write('%s<%s>%s</%s>\n' % ('  '*indent,label,self.fix(value),label))

    def dump_name(self,label,name,index=1):
        sp = "  "*index
        name_type = name.get_type()
        self.g.write('%s<%s' % (sp,label))
        if name_type:
            self.g.write(' type="%s"' % name_type)
        if name.get_privacy() != 0:
            self.g.write(' priv="%d"' % name.get_privacy())
        if name.get_sort_as() != 0:
            self.g.write(' sort="%d"' % name.get_sort_as())
        if name.get_display_as() != 0:
            self.g.write(' display="%d"' % name.get_display_as())
        self.g.write('>\n')
        self.write_line("first",name.get_first_name(),index+1)
        self.write_last(name,index+1)
        self.write_line("suffix",name.get_suffix(),index+1)
        self.write_line("patronymic",name.get_patronymic(),index+1)
        self.write_line("title",name.get_title(),index+1)
        if name.get_note() != "":
            self.write_note("note",name.get_note_object(),index+1)
        for s in name.get_source_references():
            self.dump_source_ref(s,index+1)
    
        self.g.write('%s</%s>\n' % (sp,label))

    def append_value(self,orig,val):
        if orig:
            return "%s, %s" % (orig,val)
        else:
            return val

    def build_place_title(self,loc):
        "Builds a title from a location"
        city = self.fix(loc.get_city())
        parish = self.fix(loc.get_parish())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())
        county = self.fix(loc.get_county())

        value = ""

        if city:
            value = city
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
        city = self.fix(loc.get_city())
        parish = self.fix(loc.get_parish())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())
        county = self.fix(loc.get_county())
        zip_code = self.fix(loc.get_postal_code())
        phone = self.fix(loc.get_phone())
        
        self.g.write('      <location')
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
                         (sp,conf_priv(attr),const.save_attr(attr.get_type()),
                         self.fix(attr.get_value())))
            slist = attr.get_source_references()
            note = attr.get_note()
            if note == "" and len(slist) == 0:
                self.g.write('/>\n')
            else:
                self.g.write('>\n')
                for s in attr.get_source_references():
                    self.dump_source_ref(s,indent+1)
                self.write_note("note",attr.get_note_object(),4)
                self.g.write('%s</attribute>\n' % sp)

    def write_media_list(self,list,indent=3):
        sp = '  '*indent
        for photo in list:
            mobj_id = photo.get_reference_handle()
            self.g.write('%s<objref hlink="%s"' % (sp,mobj_id))
            if photo.get_privacy():
                self.g.write(' priv="1"')
            proplist = photo.get_attribute_list()
            refslist = photo.get_source_references()
            if len(proplist) == 0 and len(refslist) == 0 \
                                    and photo.get_note() == "":
                self.g.write("/>\n")
            else:
                self.g.write(">\n")
                self.write_attribute_list(proplist,indent+1)
                for ref in refslist:
                    self.dump_source_ref(ref,indent+1)
                self.write_note("note",photo.get_note_object(),indent+1)
                self.g.write('%s</objref>\n' % sp)

    def write_url_list(self,list):
        for url in list:
            self.g.write('      <url priv="%d" href="%s"' % \
                         (url.get_privacy(),self.fix(url.get_path())))
            if url.get_description() != "":
                self.g.write(' description="%s"' % self.fix(url.get_description()))
            self.g.write('/>\n')

    def write_place_obj(self,place):
        title = self.fix(place.get_title())
        longitude = self.fix(place.get_longitude())
        lat = self.fix(place.get_latitude())
        handle = place.get_gramps_id()
        main_loc = place.get_main_location()
        llen = len(place.get_alternate_locations()) + len(place.get_url_list()) + \
               len(place.get_media_list()) + len(place.get_source_references())
                                                      
        ml_empty = main_loc.is_empty()
        note = place.get_note()

        if title == "":
            title = self.fix(self.build_place_title(place.get_main_location()))
    
        self.g.write('    <placeobj id="%s" handle="%s" change="%d" title="%s"' %
                     (handle,place.get_handle(),place.get_change_time(),title))

        if longitude or lat or not ml_empty or llen > 0 or note:
            self.g.write('>\n')
        else:
            self.g.write('/>\n')
            return
    
        if longitude or lat:
            self.g.write('      <coord long="%s" lat="%s"/>\n' % (longitude,lat))

        self.dump_location(main_loc)
        for loc in place.get_alternate_locations():
            self.dump_location(loc)
        self.write_media_list(place.get_media_list())
        self.write_url_list(place.get_url_list())
        if note != "":
            self.write_note("note",place.get_note_object(),3)
        for s in place.get_source_references():
            self.dump_source_ref(s,3)
        self.g.write("    </placeobj>\n")

    def write_object(self,obj):
        handle = obj.get_gramps_id()
        mime_type = obj.get_mime_type()
        path = obj.get_path()
        if self.strip_photos:
            path = os.path.basename(path)
        else:
            l = len(self.fileroot)
            if len(path) >= l:
                if self.fileroot == path[0:l]:
                    path = path[l+1:]
        self.g.write('    <object id="%s" handle="%s" change="%d" src="%s" mime="%s"' %
                     (handle,obj.get_handle(),obj.get_change_time(),path,mime_type))
        self.g.write(' description="%s"' % self.fix(obj.get_description()))
        alist = obj.get_attribute_list()
        note = obj.get_note()
        slist = obj.get_source_references()
        if len(alist) == 0 and len(slist) == 0 and note == "":
            self.g.write('/>\n')
        else:
            self.g.write('>\n')
            self.write_attribute_list(alist)
            if note != "":
                self.write_note("note",obj.get_note_object(),3)
            for s in slist:
                self.dump_source_ref(s,3)
            self.g.write("    </object>\n")

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

from Plugins import register_export
register_export(exportData,_title,_description,_config,_filename)
