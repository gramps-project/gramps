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
from Researcher import *
import const

import string
import Config
import time
import gzip
import shutil
import os

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
def writeNote(g,val,note,indent=0):
    if not note:
        return
    if indent != 0:
        g.write("  " * indent)
        
    g.write("<" + val + ">")
    g.write(fix(note))
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
    if obj.getConfidence() != 2:
        cnf = ' conf="%d" ' % obj.getConfidence()
    else:
        cnf = ''
    if obj.getPrivacy() != 0:
        priv = ' priv="%d"' % obj.getPrivacy()
    else:
        priv = ''
    return "%s%s" % (cnf,priv)

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
    if (not name or name == "Birth" or name == "Death") and \
       not date and not place and not description:
        return

    sp = "  " * index
    g.write('%s<event type="%s"%s>\n' % (sp,fix(name),conf_priv(event)))
    write_line(g,"date",date,index+1)
    write_line(g,"place",place,index+1)
    write_line(g,"description",description,index+1)
    if event.getNote() != "":
        writeNote(g,"note",event.getNote(),index+1)

    dump_source_ref(g,event.getSourceRef(),index+1)
    g.write("%s</event>\n" % sp)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_source_ref(g,source_ref,index=1):
    if source_ref:
        source = source_ref.getBase()
        if source:
            p = source_ref.getPage()
            c = source_ref.getComments()
            t = source_ref.getText()
            d = source_ref.getDate().getSaveDate()
            g.write("  " * index)
            if p == "" and c == "" and t == "" and d == "":
                g.write('<sourceref ref="%s"/>\n' % source.getId())
            else:
                g.write('<sourceref ref="%s">\n' % source.getId())
                write_line(g,"spage",p,index+1)
                writeNote(g,"scomments",c,index+1)
                writeNote(g,"stext",t,index+1)
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
        writeNote(g,"note",name.getNote(),index+1)
    dump_source_ref(g,name.getSourceRef(),index+1)
    
    g.write('%s</%s>\n' % (sp,label))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def exportData(database, filename, callback):
    global db
    db = database
    
    date = string.split(time.ctime(time.time()))
    fileroot = os.path.dirname(filename)
    owner = database.getResearcher()
    personList = database.getPersonMap().values()
    personList.sort(sortById)
    familyList = database.getFamilyMap().values()
    familyList.sort(sortById)
    sourceList = database.getSourceMap().values()
    sourceList.sort(sortById)

    total = len(personList) + len(familyList)

    if os.path.isfile(filename):
        shutil.copy(filename, filename + ".bak")

    if Config.uncompress:
        g = open(filename,"w")
    else:
        g = gzip.open(filename,"wb")

    g.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
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
        else:
            write_line(g,"gender","F",3)
        dump_name(g,"name",person.getPrimaryName(),3)
        for name in person.getAlternateNames():
            dump_name(g,"aka",name,3)
            
        write_line(g,"uid",person.getPafUid(),3)
        write_line(g,"nick",person.getNickName(),3)
        dump_my_event(g,"Birth",person.getBirth(),3)
        dump_my_event(g,"Death",person.getDeath(),3)
        for event in person.getEventList():
            dump_event(g,event,3)

        for photo in person.getPhotoList():
            path = photo.getPath()
            if os.path.dirname(path) == fileroot:
                path = os.path.basename(path)
            g.write('      <img src="%s"' % fix(path) )
            g.write(' descrip="%s"' % fix(photo.getDescription()))
            proplist = photo.getPropertyList()
            if proplist:
                for key in proplist.keys():
                    g.write(' %s="%s"' % (key,proplist[key]))
            g.write("/>\n")

        if len(person.getAddressList()) > 0:
            g.write("      <addresses>\n")
            for address in person.getAddressList():
                g.write('        <address%s">\n' % conf_priv(address))
                write_line(g,"date",address.getDateObj().getSaveDate(),5)
                write_line(g,"street",address.getStreet(),5)
                write_line(g,"city",address.getCity(),5)
                write_line(g,"state",address.getState(),5)
                write_line(g,"country",address.getCountry(),5)
                write_line(g,"postal",address.getPostal(),5)
                if address.getNote() != "":
                    writeNote(g,"note",address.getNote(),5)
                dump_source_ref(g,address.getSourceRef(),5)
                g.write('        </address>\n')
            g.write('      </addresses>\n')

        if len(person.getAttributeList()) > 0:
            g.write("      <attributes>\n")
            for attr in person.getAttributeList():
                if attr.getSourceRef() or attr.getNote():
                    g.write('        <attribute%s>\n' % conf_priv(attr))
                    write_line(g,"attr_type",attr.getType(),5)
                    write_line(g,"attr_value",attr.getValue(),5)
                    dump_source_ref(g,attr.getSourceRef(),5)
                    writeNote(g,"note",attr.getNote(),5)
                    g.write('        </attribute>\n')
                else:
                    g.write('        <attribute type="%s">' % attr.getType())
                    g.write(fix(attr.getValue()))
                    g.write('</attribute>\n')
            g.write('      </attributes>\n')

        if len(person.getUrlList()) > 0:
            g.write("      <urls>\n")
            for url in person.getUrlList():
                g.write('        <url priv="%d" href="%s"' % \
                        (url.getPrivacy(),url.get_path()))
                if url.get_description() != "":
                    g.write(' description="' + url.get_description() + '"')
                g.write('/>\n')
            g.write('      </urls>\n')

        write_ref(g,"childof",person.getMainFamily(),3)
        for alt in person.getAltFamilyList():
            g.write("      <childof ref=\"%s\" mrel=\"%s\" frel=\"%s\"/>\n" % \
                    (alt[0].getId(), alt[1], alt[2]))

        for family in person.getFamilyList():
            write_ref(g,"parentin",family,3)

        writeNote(g,"note",person.getNote(),3)

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

            dump_event(g,family.getMarriage(),3)
            dump_event(g,family.getDivorce(),3)
            for event in family.getEventList():
                dump_event(g,event,3)

            for photo in family.getPhotoList():
                path = photo.getPath()
                if os.path.dirname(path) == fileroot:
                    path = os.path.basename(path)
                g.write("      <img src=\"" + fix(path) + "\"")
                g.write(" descrip=\""  + fix(photo.getDescription()) + "\"")
                proplist = photo.getPropertyList()
                if proplist:
                    for key in proplist.keys():
                        g.write(' %s="%s"' % (key,proplist[key]))
                g.write("/>\n")

            if len(family.getChildList()) > 0:
                g.write("      <childlist>\n")
                for person in family.getChildList():
                    write_ref(g,"child",person,4)
                g.write("      </childlist>\n")
            if len(family.getAttributeList()) > 0:
                g.write("      <attributes>\n")
                for attr in family.getAttributeList():
                    g.write('        <attribute>\n')
                    write_line(g,"attr_type",attr.getType(),5)
                    write_line(g,"attr_value",attr.getValue(),5)
                    dump_source_ref(g,attr.getSourceRef(),5)
                    writeNote(g,"note",attr.getNote(),5)
                    g.write('        </attribute>\n')
                g.write('      </attributes>\n')
            writeNote(g,"note",family.getNote(),3)
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
                writeNote(g,"note",source.getNote(),3)
            for photo in source.getPhotoList():
                path = photo.getPath()
                if os.path.dirname(path) == fileroot:
                    path = os.path.basename(path)
                    g.write("      <img src=\"" + fix(path) + "\"")
                    g.write(" descrip=\""  + fix(photo.getDescription()) + "\"")
                    proplist = photo.getPropertyList()
                    if proplist:
                        for key in proplist.keys():
                            g.write(' %s="%s"' % (key,proplist[key]))
            g.write("    </source>\n")
        g.write("  </sources>\n")

    if len(db.getBookmarks()) > 0:
        g.write("  <bookmarks>\n")
        for person in db.getBookmarks():
            g.write('    <bookmark ref="%s"/>\n' % person.getId())
        g.write("  </bookmarks>\n")

    g.write("</database>\n")
    g.close()
	
    





