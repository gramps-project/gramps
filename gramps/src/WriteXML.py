#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

from RelLib import *
import const

import string
import Config
import time
import shutil
import os
from Date import SingleDate

try:
    import gzip
    gzip_ok = 1
except:
    gzip_ok = 0

fileroot = ""
strip_photo = 0

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sortById(first,second):
    fid = first.getId()
    sid = second.getId()

    if fid < sid:
        return -1
    else:
        return fid != sid

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fix(line):
    l = string.strip(line)
    l = string.replace(l,'&','&amp;')
    l = string.replace(l,'>','&gt;')
    l = string.replace(l,'<','&lt;')
    return string.replace(l,'"','&quot;')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_note(g,val,note,indent=0):
    if not note:
        return
    if indent != 0:
        g.write("  " * indent)
        
    g.write("<" + val + ">")
    g.write(fix(string.rstrip(note)))
    g.write("</" + val + ">\n")
			
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_event(g,event,index=1):
    if event:
        dump_my_event(g,event.getName(),event,index)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def conf_priv(obj):
    if obj.getPrivacy() != 0:
        return ' priv="%d"' % obj.getPrivacy()
    else:
        return ''

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_my_event(g,name,event,index=1):
    if not event:
        return
    
    date = event.getSaveDate()
    place = event.getPlace()
    description = event.getDescription()
    cause = event.getCause()
    if (not name or name == "Birth" or name == "Death") and \
       not date and not place and not description:
        return

    sp = "  " * index
    g.write('%s<event type="%s"%s>\n' % (sp,fix(name),conf_priv(event)))
    write_date(g,event.getDateObj(),index+1)
    write_ref(g,"place",place,index+1)
    write_line(g,"cause",cause,index+1)
    write_line(g,"description",description,index+1)
    if event.getNote() != "":
        write_note(g,"note",event.getNote(),index+1)

    for s in event.getSourceRefList():
        dump_source_ref(g,s,index+1)
    g.write("%s</event>\n" % sp)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_source_ref(g,source_ref,index=1):
    source = source_ref.getBase()
    if source:
        p = source_ref.getPage()
        c = source_ref.getComments()
        t = source_ref.getText()
        d = source_ref.getDate().getSaveDate()
        q = source_ref.getConfidence()
        g.write("  " * index)
        if p == "" and c == "" and t == "" and d == "" and q == 2:
            g.write('<sourceref ref="%s"/>\n' % source.getId())
        else:
            if q == 2:
                g.write('<sourceref ref="%s">\n' % source.getId())
            else:
                g.write('<sourceref ref="%s" conf="%d">\n' % (source.getId(),q))
            write_line(g,"spage",p,index+1)
            write_note(g,"scomments",c,index+1)
            write_note(g,"stext",t,index+1)
            write_line(g,"sdate",d,index+1)
            g.write("%s</sourceref>\n" % ("  " * index))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_ref(g,label,person,index=1):
    if person:
        g.write('%s<%s ref="%s"/>\n' % ("  "*index,label,person.getId()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_id(g,label,person,index=1):
    if person:
        g.write('%s<%s id="%s">\n' % ("  "*index,label,person.getId()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_family_id(g,family,index=1):
    if family:
        rel = family.getRelationship()
        sp = "  " * index
        if rel != "":
            g.write('%s<family id="%s" type="%s">\n' % (sp,family.getId(),rel))
        else:
            g.write('%s<family id="%s">\n' % (sp,family.getId()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_line(g,label,value,indent=1):
    if value:
        g.write('%s<%s>%s</%s>\n' % ('  '*indent,label,fix(value),label))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_date(g,date,indent=1):
    sp = '  '*indent
    if date.isEmpty():
        return

    cal = date.get_calendar()
    if cal != 0:
        calstr = ' calendar="%s"' % fix(str(cal))
    else:
        calstr = ''

    if date.isRange():
        d1 = date.get_start_date().getIsoDate()
        d2 = date.get_stop_date().getIsoDate()
        g.write('%s<daterange start="%s" stop="%s"%s/>\n' % (sp,d1,d2,calstr))
    elif date.isValid():
        d1 = date.get_start_date()
        mode = d1.getModeVal()
        dstr = d1.getIsoDate()

        if mode == SingleDate.before:
            pref = ' type="before"'
        elif mode == SingleDate.after:
            pref = ' type="after"'
        elif mode == SingleDate.about:
            pref = ' type="about"'
        else:
            pref = ""
            
        g.write('%s<dateval val="%s"%s%s/>\n' % (sp,dstr,pref,calstr))
    else:
        g.write('%s<datestr val="%s"/>\n' %(sp,date.getText()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_force_line(g,label,value,indent=1):
    if value != None:
        g.write('%s<%s>%s</%s>\n' % ('  '*indent,label,fix(value),label))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_name(g,label,name,index=1):
    sp = "  "*index
    g.write('%s<%s%s>\n' % (sp,label,conf_priv(name)))
    write_line(g,"first",name.getFirstName(),index+1)
    write_line(g,"last",name.getSurname(),index+1)
    write_line(g,"suffix",name.getSuffix(),index+1)
    write_line(g,"title",name.getTitle(),index+1)
    if name.getNote() != "":
        write_note(g,"note",name.getNote(),index+1)
    for s in name.getSourceRefList():
        dump_source_ref(g,s,index+1)
    
    g.write('%s</%s>\n' % (sp,label))


def append_value(orig,val):
    if orig:
        return "%s, %s" % (orig,val)
    else:
        return val

def build_place_title(loc):
    "Builds a title from a location"
    city = fix(loc.get_city())
    parish = fix(loc.get_parish())
    state = fix(loc.get_state())
    country = fix(loc.get_country())
    county = fix(loc.get_county())

    value = ""

    if city:
        value = city
    if parish:
        value = append_value(value,parish)
    if county:
        value = append_value(value,county)
    if state:
        value = append_value(value,state)
    if country:
        value = append_value(value,country)
    return value

def dump_location(g,loc):
    "Writes the location information to the output file"
    city = fix(loc.get_city())
    parish = fix(loc.get_parish())
    state = fix(loc.get_state())
    country = fix(loc.get_country())
    county = fix(loc.get_county())

    if not city and not state and not parish and not county and not country:
        return
    
    g.write('      <location')
    if city:
        g.write(' city="%s"' % city)
    if parish:
        g.write(' parish="%s"' % parish)
    if county:
        g.write(' county="%s"' % county)
    if state:
        g.write(' state="%s"' % state)
    if country:
        g.write(' country="%s"' % country)
    g.write('/>\n')


def write_attribute_list(g, list, indent=3):
    sp = '  ' * indent
    for attr in list:
        g.write('%s<attribute%s type="%s" value="%s"' % \
                (sp,conf_priv(attr),attr.getType(),fix(attr.getValue())))
        slist = attr.getSourceRefList()
        note = attr.getNote()
        if note == "" and len(slist) == 0:
            g.write('/>\n')
        else:
            g.write('>\n')
            for s in attr.getSourceRefList():
                dump_source_ref(g,s,indent+1)
            write_note(g,"note",attr.getNote(),4)
            g.write('%s</attribute>\n' % sp)

def write_photo_list(g,list,indent=3):
    sp = '  '*indent
    for photo in list:
        mobj = photo.getReference()
        g.write('%s<objref ref="%s"' % (sp,mobj.getId()))
        if photo.getPrivacy():
            g.write(' priv="1"')
        proplist = photo.getAttributeList()
        if len(proplist) == 0 and photo.getNote() == "":
            g.write("/>\n")
        else:
            g.write(">\n")
            write_attribute_list(g,proplist,indent+1)
            write_note(g,"note",photo.getNote(),indent+1)
            g.write('%s</objref>\n' % sp)

def write_url_list(g, list):
    for url in list:
        g.write('      <url priv="%d" href="%s"' % \
                (url.getPrivacy(),fix(url.get_path())))
        if url.get_description() != "":
            g.write(' description="%s"' % fix(url.get_description()))
        g.write('/>\n')

def write_place_obj(g,place):
    title = fix(place.get_title())
    long = place.get_longitude()
    lat = place.get_latitude()
    id = place.getId()
    main_loc = place.get_main_location()
    llen = len(place.get_alternate_locations()) + len(place.getUrlList()) + \
           len(place.getPhotoList()) + len(place.getSourceRefList())
                                                      
    ml_empty = main_loc.is_empty()
    note = place.getNote()

    if title == "":
        title = fix(build_place_title(place.get_main_location()))
    
    g.write('    <placeobj id="%s" title="%s"' % (id,title))

    if long or lat or not ml_empty or llen > 0 or note:
        g.write('>\n')
    else:
        g.write('/>\n')
        return
    
    if long or lat:
        g.write('      <coord long="%s" lat=%s"/>\n' % (fix(long),fix(lat)))

    dump_location(g,main_loc)
    for loc in place.get_alternate_locations():
        dump_location(g,loc)
    write_photo_list(g,place.getPhotoList())
    write_url_list(g, place.getUrlList())
    if note != "":
        write_note(g,"note",note,3)
    for s in place.getSourceRefList():
        dump_source_ref(g,s,3)
    g.write("    </placeobj>\n")

def write_object(g,object):
    id = object.getId()
    type = object.getMimeType()
    path = object.getPath()
    if strip_photo:
        path = os.path.basename(path)
    else:
        l = len(fileroot)
        if len(path) >= l:
            if fileroot == path[0:l]:
                path = path[l+1:]
    g.write('    <object id="%s" src="%s" mime="%s"' % (id,path,type))
    g.write(' description="%s"' % fix(object.getDescription()))
    alist = object.getAttributeList()
    note = object.getNote()
    slist = object.getSourceRefList()
    if len(alist) == 0 and len(slist) == 0 and note == "":
        g.write('/>\n')
    else:
        g.write('>\n')
        write_attribute_list(g,alist)
        if note != "":
            write_note(g,"note",note,3)
        for s in slist:
            dump_source_ref(g,s,3)
        g.write("    </object>\n")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def exportData(database, filename, callback):
    global fileroot

    fileroot = os.path.dirname(filename)
    if os.path.isfile(filename):
        shutil.copy(filename, filename + ".bak")

    if Config.uncompress ==0 and gzip_ok == 1:
        try:
            g = gzip.open(filename,"wb")
        except:
            g = open(filename,"w")
    else:
        g = open(filename,"w")

    write_xml_data(database, g, callback, 0)
    g.close()

def write_xml_data(database, g, callback, sp):

    global strip_photo

    strip_photo = sp
    
    date = string.split(time.ctime(time.time()))
    owner = database.getResearcher()
    personList = database.getPersonMap().values()
    personList.sort(sortById)
    familyList = database.getFamilyMap().values()
    familyList.sort(sortById)
    sourceList = database.getSourceMap().values()
    placeList = database.getPlaceMap().values()
    placeList.sort(sortById)
    objList = database.getObjectMap().values()
    objList.sort(sortById)

    total = len(personList) + len(familyList)

    g.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')
    g.write('<!DOCTYPE database SYSTEM "gramps.dtd" []>\n')
    g.write("<database>\n")
    g.write("  <header>\n")
    g.write("    <created date=\"%s %s %s\"" % (date[2],string.upper(date[1]),date[4]))
    g.write(" version=\"" + const.version + "\"")
    g.write(" people=\"%d\"" % (len(database.getPersonMap().values())))
    g.write(" families=\"%d\"/>\n" % len(database.getFamilyMap().values()))
    g.write("    <researcher>\n")
    write_line(g,"resname",owner.getName(),3)
    write_line(g,"resaddr",owner.getAddress(),3)
    write_line(g,"rescity",owner.getCity(),3)
    write_line(g,"resstate",owner.getState(),3)
    write_line(g,"rescountry",owner.getCountry(),3)
    write_line(g,"respostal",owner.getPostalCode(),3)
    write_line(g,"resphone",owner.getPhone(),3)
    write_line(g,"resemail",owner.getEmail(),3)
    g.write("    </researcher>\n")
    g.write("  </header>\n")

    if len(personList) > 0:
        g.write("  <people")
        person = database.getDefaultPerson()
        if person:
            g.write(' default="%s"' % person.getId())
        g.write(">\n")

        total = len(personList) + len(familyList)
        delta = max(int(total/50),1)

        count = 0
        for person in personList:
            if count % delta == 0:
                callback(float(count)/float(total))
            count = count + 1
            
            write_id(g,"person",person,2)
            if person.getGender() == Person.male:
                write_line(g,"gender","M",3)
            elif person.getGender() == Person.female:
                write_line(g,"gender","F",3)
            else:
                write_line(g,"gender","U",3)
            dump_name(g,"name",person.getPrimaryName(),3)
            for name in person.getAlternateNames():
                dump_name(g,"aka",name,3)
            
            write_line(g,"uid",person.getPafUid(),3)
            write_line(g,"nick",person.getNickName(),3)
            pos = person.getPosition()
            if pos != None:
               g.write('      <pos x="%d" y="%d"/>\n'% pos)
            dump_my_event(g,"Birth",person.getBirth(),3)
            dump_my_event(g,"Death",person.getDeath(),3)
            for event in person.getEventList():
                dump_event(g,event,3)

            write_photo_list(g,person.getPhotoList())

            if len(person.getAddressList()) > 0:
                for address in person.getAddressList():
                    g.write('      <address%s>\n' % conf_priv(address))
                    write_date(g,address.getDateObj(),4)
#                    write_line(g,"date",address.getDateObj().getSaveDate(),4)
                    write_line(g,"street",address.getStreet(),4)
                    write_line(g,"city",address.getCity(),4)
                    write_line(g,"state",address.getState(),4)
                    write_line(g,"country",address.getCountry(),4)
                    write_line(g,"postal",address.getPostal(),4)
                    if address.getNote() != "":
                        write_note(g,"note",address.getNote(),4)
                    for s in address.getSourceRefList():
                        dump_source_ref(g,s,4)
                    g.write('      </address>\n')

            write_attribute_list(g,person.getAttributeList())
            write_url_list(g,person.getUrlList())

            write_ref(g,"childof",person.getMainFamily(),3)
            for alt in person.getAltFamilyList():
                if alt[1] != "":
                    mrel=' mrel="%s"' % alt[1]
                else:
                    mrel=''
                if alt[2] != "":
                    frel=' frel="%s"' % alt[2]
                else:
                    frel=''
                g.write("      <childof ref=\"%s\"%s%s/>\n" % \
                        (alt[0].getId(), mrel, frel))

            for family in person.getFamilyList():
                write_ref(g,"parentin",family,3)

            write_note(g,"note",person.getNote(),3)

            g.write("    </person>\n")
        g.write("  </people>\n")

    if len(familyList) > 0:
        g.write("  <families>\n")
            
        for family in familyList:
            if count % delta == 0:
                callback(float(count)/float(total))
            count = count + 1
            
            write_family_id(g,family,2)
            write_ref(g,"father",family.getFather(),3)
            write_ref(g,"mother",family.getMother(),3)
            pos = family.getPosition()
            if pos != None:
               g.write('      <pos x="%d" y="%d"/>\n'% pos)

            for event in family.getEventList():
                dump_event(g,event,3)

            write_photo_list(g,family.getPhotoList())

            if len(family.getChildList()) > 0:
                for person in family.getChildList():
                    write_ref(g,"child",person,3)
            write_attribute_list(g,family.getAttributeList())
            write_note(g,"note",family.getNote(),3)
            g.write("    </family>\n")
        g.write("  </families>\n")

    if len(sourceList) > 0:
        g.write("  <sources>\n")
        for source in sourceList:
            g.write("    <source id=\"" + source.getId() + "\">\n")
            write_force_line(g,"stitle",source.getTitle(),3)
            write_line(g,"sauthor",source.getAuthor(),3)
            write_line(g,"spubinfo",source.getPubInfo(),3)
            write_line(g,"scallno",source.getCallNumber(),3)
            if source.getNote() != "":
                write_note(g,"note",source.getNote(),3)
            write_photo_list(g,source.getPhotoList())
            g.write("    </source>\n")
        g.write("  </sources>\n")

    if len(placeList) > 0:
        g.write("  <places>\n")
        for place in placeList:
            write_place_obj(g,place)
        g.write("  </places>\n")

    if len(objList) > 0:
        g.write("  <objects>\n")
        for object in objList:
            write_object(g,object)
        g.write("  </objects>\n")

    if len(database.getBookmarks()) > 0:
        g.write("  <bookmarks>\n")
        for person in database.getBookmarks():
            g.write('    <bookmark ref="%s"/>\n' % person.getId())
        g.write("  </bookmarks>\n")

    g.write("</database>\n")

