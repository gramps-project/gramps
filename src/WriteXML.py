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
def writeNote(g,val,note):
    if not note:
        return
    g.write("<" + val + ">")
    g.write(fix(note))
    g.write("</" + val + ">\n")
			
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_event(g,event):
    if event:
        dump_my_event(g,event.getName(),event)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_my_event(g,name,event):
    if not event:
        return
    
    date = event.getSaveDate()
    place = event.getPlace()
    description = event.getDescription()
    if not name and not date and not place and not description:
        return
    
    g.write("<event type=\"" + fix(name) + "\">\n")
    write_line(g,"date",date)
    write_line(g,"place",place)
    write_line(g,"description",description)
    if event.getNote() != "":
        writeNote(g,"note",event.getNote())

    dump_source_ref(g,event.getSourceRef())
    g.write("</event>\n")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_source_ref(g,source_ref):
    if source_ref:
        source = source_ref.getBase()
        if source:
            p = source_ref.getPage()
            c = source_ref.getComments()
            t = source_ref.getText()
            d = source_ref.getDate().getSaveDate()
            if p == "" and c == "" and t == "" and d == "":
                g.write("<sourceref ref=\"%d\"/>\n" % source.getId())
            else:
                g.write("<sourceref ref=\"%d\">\n" % source.getId())
                write_line(g,"spage",p)
                writeNote(g,"scomments",c)
                writeNote(g,"stext",t)
                write_line(g,"sdate",d)
                g.write("</sourceref>\n")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_ref(g,label,person):
    if person:
        g.write('<%s ref="%s"/>\n' % (label,str(person.getId())))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_id(g,label,person):
    if person:
        g.write('<%s id="%s">\n' % (label,str(person.getId())))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_family_id(g,family):
    if family:
        rel = family.getRelationship()
        if rel != "":
            g.write('<family id="%s" type="%s">\n' % (str(family.getId()),rel))
        else:
            g.write('<family id="%s">\n' % str(family.getId()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_line(g,label,value):
    if value:
        g.write('<%s>%s</%s>\n' % (label,fix(value),label))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def dump_name(g,label,name):
    g.write('<%s>\n' % label)
    write_line(g,"first",name.getFirstName())
    write_line(g,"last",name.getSurname())
    write_line(g,"suffix",name.getSuffix())
    write_line(g,"title",name.getTitle())
    g.write('</%s>\n' % label)

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
        
    g = gzip.open(filename,"wb")

    g.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
    g.write("<database>\n")
    g.write("<header>\n")
    g.write("<created date=\"%s %s %s\"" % (date[2],string.upper(date[1]),date[4]))
    g.write(" version=\"" + const.version + "\"")
    g.write(" people=\"%d\"" % (len(database.getPersonMap().values())))
    g.write(" families=\"%d\"/>\n" % len(database.getFamilyMap().values()))
    g.write("<researcher>\n")
    write_line(g,"resname",owner.getName())
    write_line(g,"resaddr",owner.getAddress())
    write_line(g,"rescity",owner.getCity())
    write_line(g,"resstate",owner.getState())
    write_line(g,"rescountry",owner.getCountry())
    write_line(g,"respostal",owner.getPostalCode())
    write_line(g,"resphone",owner.getPhone())
    write_line(g,"resemail",owner.getEmail())
    g.write("</researcher>\n")
    g.write("</header>\n")

    g.write("<people")
    person = database.getDefaultPerson()
    if person:
        g.write(" default=\"" + str(person.getId()) + "\"")
    g.write(">\n")

    total = len(personList) + len(familyList)
    delta = max(int(total/50),1)

    count = 0
    for person in personList:
        if count % delta == 0:
            callback(float(count)/float(total))
        count = count + 1
            
        write_id(g,"person",person)
        if person.getGender() == Person.male:
            write_line(g,"gender","M")
        else:
            write_line(g,"gender","F")
        dump_name(g,"name",person.getPrimaryName())
        for name in person.getAlternateNames():
            dump_name(g,"aka",name)
            
        write_line(g,"uid",person.getPafUid())
        write_line(g,"nick",person.getNickName())
        dump_my_event(g,"Birth",person.getBirth())
        dump_my_event(g,"Death",person.getDeath())
        for event in person.getEventList():
            dump_event(g,event)

        for photo in person.getPhotoList():
            path = photo.getPath()
            if os.path.dirname(path) == fileroot:
                path = os.path.basename(path)
            g.write("<img src=\"" + fix(path) + "\"")
            g.write(" descrip=\""  + fix(photo.getDescription()) + "\"/>\n")

        if len(person.getAddressList()) > 0:
            g.write("<addresses>\n")
            for address in person.getAddressList():
                g.write('<address>\n')
                write_line(g,"date",address.getDateObj().getSaveDate())
                write_line(g,"street",address.getStreet())
                write_line(g,"city",address.getCity())
                write_line(g,"state",address.getState())
                write_line(g,"country",address.getCountry())
                write_line(g,"postal",address.getPostal())
                if address.getNote() != "":
                    writeNote(g,"note",address.getNote())
                dump_source_ref(g,address.getSourceRef())
                g.write('</address>\n')
            g.write('</addresses>\n')

        if len(person.getAttributeList()) > 0:
            g.write("<attributes>\n")
            for attr in person.getAttributeList():
                if attr.getSourceRef() or attr.getNote():
                    g.write('<attribute>\n')
                    write_line(g,"attr_type",attr.getType())
                    write_line(g,"attr_value",attr.getValue())
                    dump_source_ref(g,attr.getSourceRef())
                    writeNote(g,"note",attr.getNote())
                    g.write('</attribute>\n')
                else:
                    g.write('<attribute type="%s">' % attr.getType())
                    g.write(fix(attr.getValue()))
                    g.write('</attribute>\n')
            g.write('</attributes>\n')

        if len(person.getUrlList()) > 0:
            g.write("<urls>\n")
            for url in person.getUrlList():
                g.write('<url href="' + url.get_path() + '"')
                if url.get_description() != "":
                    g.write(' description="' + url.get_description() + '"')
                g.write('/>\n')
            g.write('</urls>\n')

        write_ref(g,"childof",person.getMainFamily())
        for alt in person.getAltFamilyList():
            g.write("<childof ref=\"" + str(alt[0].getId()))
            g.write("\" type=\"" + alt[1] + "\"/>\n")

        for family in person.getFamilyList():
            write_ref(g,"parentin",family)

        writeNote(g,"note",person.getNote())

        g.write("</person>\n")
    g.write("</people>\n")
    g.write("<families>\n")
            
    for family in familyList:
        if count % delta == 0:
            callback(float(count)/float(total))
        count = count + 1
            
        write_family_id(g,family)
        write_ref(g,"father",family.getFather())
        write_ref(g,"mother",family.getMother())

        dump_event(g,family.getMarriage())
        dump_event(g,family.getDivorce())
        for event in family.getEventList():
            dump_event(g,event)

        for photo in family.getPhotoList():
            path = photo.getPath()
            if os.path.dirname(path) == fileroot:
                path = os.path.basename(path)
            g.write("<img src=\"" + fix(path) + "\"")
            g.write(" descrip=\""  + fix(photo.getDescription()) + "\"/>\n")

        if len(family.getChildList()) > 0:
            g.write("<childlist>\n")
            for person in family.getChildList():
                write_ref(g,"child",person)
            g.write("</childlist>\n")
        writeNote(g,"note",family.getNote())
        g.write("</family>\n")
    g.write("</families>\n")

    if len(sourceList) > 0:
        g.write("<sources>\n")
        for source in sourceList:
            g.write("<source id=\"" + str(source.getId()) + "\">\n")
            write_line(g,"stitle",source.getTitle())
            write_line(g,"sauthor",source.getAuthor())
            write_line(g,"spubinfo",source.getPubInfo())
            write_line(g,"scallno",source.getCallNumber())
            if source.getNote() != "":
                writeNote(g,"note",source.getNote())
            for photo in source.getPhotoList():
                path = photo.getPath()
                if os.path.dirname(path) == fileroot:
                    path = os.path.basename(path)
                    g.write("<img src=\"" + fix(path) + "\"")
                    g.write(" descrip=\""  + fix(photo.getDescription()) + "\"/>\n")
            g.write("</source>\n")
        g.write("</sources>\n")

    if len(db.getBookmarks()) > 0:
        g.write("<bookmarks>\n")
        for person in db.getBookmarks():
            g.write("<bookmark ref=\"" + str(person.getId()) + "\"/>\n")
        g.write("</bookmarks>\n")

    g.write("</database>\n")
    g.close()
	
    





