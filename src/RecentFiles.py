#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import time
from  xml.parsers.expat import ParserCreate

try:
    import fcntl
    use_lock = True
except:
    use_lock = False

import const

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GRAMPS_FILENAME = os.path.join(const.home_dir,"recent-files.xml")
MAX_GRAMPS_ITEMS = 10

#-------------------------------------------------------------------------
#
# RecentItem
#
#-------------------------------------------------------------------------
class RecentItem:
    """
    Interface to a single GRAMPS recent-items item
    """

    def __init__(self,p="",n="",t=0):
        self.path = p
        self.name = n
        self.time = t

    def set_path(self,val):
        self.path = val

    def get_path(self):
        return self.path

    def set_name(self,val):
        self.name = val

    def get_name(self):
        return self.name

    def set_time(self,val):
        self.time = int(val)

    def get_time(self):
        return self.time

    def __cmp__(self,other_item):
        return cmp(self.time,other_item.time)

#-------------------------------------------------------------------------
#
# RecentFiles
#
#-------------------------------------------------------------------------
class RecentFiles:
    """
    Interface to a RecentFiles collection
    """

    def __init__(self):
        gramps_parser = RecentParser()
        self.gramps_recent_files = gramps_parser.get()

    def add(self,item2add):
        # First we need to walk the existing items to see 
        # if our item is already there
        for item in self.gramps_recent_files:
            if item.get_path() == item2add.get_path():
                # Found it -- modify timestamp and add all groups 
                # to the item's groups
                item.set_time(item2add.get_time())
                return
        # At this point we walked the items and not found one,
        # so simply inserting a new item in the beginning
        self.gramps_recent_files.insert(0,item2add)

    def remove_filename(self,filename):
        # First we need to walk the existing items to see 
        # if our item is already there
        found = False
        for index in range(len(self.gramps_recent_files)):
            if self.gramps_recent_files[index].get_path() == filename:
                # Found it -- break here and pop that item
                found = True
                break
        if found:
            self.gramps_recent_files.pop(index)

    def save(self):
        """
        Attempt saving into XML.
        The trick is not to fail under any circumstances.
        """
        try:
            self.do_save()
        except:
            pass

    def do_save(self):
        """
        Saves the current GRAMPS RecentFiles collection to the associated file.
        """
        xml_file = file(os.path.expanduser(GRAMPS_FILENAME),'w')
        if use_lock:
            fcntl.lockf(xml_file,fcntl.LOCK_EX)
        xml_file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        xml_file.write('<RecentFiles>\n')
        index = 0
        for item in self.gramps_recent_files:
            index = index + 1
            if index > MAX_GRAMPS_ITEMS:
                break
            xml_file.write('  <RecentItem>\n')
            xml_file.write('    <Path>%s</Path>\n' % item.get_path())
            xml_file.write('    <Name>%s</Name>\n' % item.get_name())
            xml_file.write('    <Timestamp>%d</Timestamp>\n' % item.get_time())
            xml_file.write('  </RecentItem>\n')
        xml_file.write('</RecentFiles>\n')
        if use_lock:
            fcntl.lockf(xml_file,fcntl.LOCK_UN)
        xml_file.close()

#-------------------------------------------------------------------------
#
# RecentParser
#
#-------------------------------------------------------------------------
class RecentParser:
    """
    Parsing class for the RecentFiles collection.
    """
    
    def __init__(self):
        self.recent_files = []

        try:
            xml_file = open(os.path.expanduser(GRAMPS_FILENAME))
            if use_lock:
                fcntl.lockf(xml_file,fcntl.LOCK_SH)

            p = ParserCreate()
            p.StartElementHandler = self.startElement
            p.EndElementHandler = self.endElement
            p.CharacterDataHandler = self.characters
            p.ParseFile(xml_file)

            if use_lock:
                fcntl.lockf(xml_file,fcntl.LOCK_UN)
            xml_file.close()
        except:
            pass

    def get(self):
        print "1", self.recent_files
        return self.recent_files

    def startElement(self,tag,attrs):
        self.tlist = []
        if tag == "RecentItem":
            self.item = RecentItem()

    def endElement(self,tag):

        text = ''.join(self.tlist)

        if tag == "RecentItem":
            if os.path.isdir(self.item.get_path()):
                self.recent_files.append(self.item)
        elif tag == "Path":
            self.item.set_path(text)
        elif tag == "Name":
            self.item.set_name(text)
        elif tag == "Timestamp":
            self.item.set_time(int(text))

    def characters(self, data):
        self.tlist.append(data)

#-------------------------------------------------------------------------
#
# Helper functions
#
#-------------------------------------------------------------------------
def recent_files(filename,name):
    """
    Add an entry to both GNOME and GRAMPS recent-items storages.
    """

    the_time = int(time.time())
    gramps_rf = RecentFiles()
    gramps_item = RecentItem(
        p=filename,
        n=name,
        t=the_time)
    gramps_rf.add(gramps_item)
    gramps_rf.save()

def remove_filename(filename):
    gramps_rf = RecentFiles()
    gramps_rf.remove_filename(filename)
    gramps_rf.save()
