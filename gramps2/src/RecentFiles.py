#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Donald N. Allingham
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
import fcntl
import time
import xml.parsers.expat

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
FILENAME    = "~/.recently-used"
MAX_ITEMS = 500

#-------------------------------------------------------------------------
#
# RecentItem
#
#-------------------------------------------------------------------------
class RecentItem:
    """
    Interface to a single recent-items item
    """

    def __init__(self,u="",m="",t="",p=False,g=[]):
        self.uri = u
        self.mime = m
        self.time = t
        self.private = p
        self.groups = g

    def set_uri(self,val):
        self.uri = val

    def get_uri(self):
        return self.uri

    def set_mime(self,val):
        self.mime = val

    def get_mime(self):
        return self.mime

    def set_time(self,val):
        self.time = int(val)

    def get_time(self):
        return self.time

    def set_private(self,val):
        self.private = val

    def get_private(self):
        return self.private

    def set_groups(self,val):
        self.groups = val[:]

    def get_groups(self):
        return self.groups[:]

    def add_group(self,group):
        if group not in self.groups:
            self.groups.append(group)

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
        parser = RecentParser()
        self.recent_files = parser.get()

    def add(self,item2add):
        # First we need to walk the existing items to see 
        # if our item is already there
        for item in self.recent_files:
            if item.get_uri() == item2add.get_uri():
                # Found it -- modify timestamp and add all groups 
                # to the item's groups
                item.set_time(item2add.get_time())
                for group in item2add.get_groups():
                    item.add_group(group)
                return
        # At this point we walked the items and not found one,
        # so simply inserting a new item in the beginning
        self.recent_files.insert(0,item2add)

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
        Saves the current RecentFiles collection to the associated file.
        """
        xml_file = file(os.path.expanduser(FILENAME),'w')
        fcntl.lockf(xml_file,fcntl.LOCK_EX)
        xml_file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        xml_file.write('<RecentFiles>\n')
        index = 0
        for item in self.recent_files:
            if index > MAX_ITEMS:
                break
            xml_file.write('  <RecentItem>\n')
            xml_file.write('    <URI>%s</URI>\n' % item.get_uri())
            xml_file.write('    <Mime-Type>%s</Mime-Type>\n' % item.get_mime())
            xml_file.write('    <Timestamp>%d</Timestamp>\n' % item.get_time())
            if item.get_private():
                xml_file.write('    <Private/>\n')
            xml_file.write('    <Groups>\n')
            for g in item.get_groups():
                xml_file.write('      <Group>%s</Group>\n' % g)
            xml_file.write('    </Groups>\n')
            xml_file.write('  </RecentItem>\n')
        xml_file.write('</RecentFiles>\n')
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
            xml_file = open(os.path.expanduser(FILENAME))
            fcntl.lockf(xml_file,fcntl.LOCK_SH)

            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = self.startElement
            p.EndElementHandler = self.endElement
            p.CharacterDataHandler = self.characters
            p.ParseFile(xml_file)

            fcntl.lockf(xml_file,fcntl.LOCK_UN)
            xml_file.close()
        except:
            pass

    def get(self):
        return self.recent_files

    def startElement(self,tag,attrs):
        self.tlist = []
        if tag == "RecentItem":
            self.item = RecentItem()
        elif tag == "Groups":
            self.groups = []

    def endElement(self,tag):

        text = ''.join(self.tlist)

        if tag == "RecentItem":
            self.recent_files.append(self.item)
        elif tag == "URI":
            self.item.set_uri(text)
        elif tag == "Mime-Type":
            self.item.set_mime(text)
        elif tag == "Timestamp":
            self.item.set_time(int(text))
        elif tag == "Private":
            self.item.set_private(True)
        elif tag == "Groups":
            self.item.set_groups(self.groups)
        elif tag == "Group":
            self.groups.append(text)

    def characters(self, data):
        self.tlist.append(data)
