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
        for item in self.recent_files:
            if item.get_uri() == item2add.get_uri():
                item.set_time(item2add.get_time())
                return
        self.recent_files.insert(0,item2add)

    def save(self):
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
        xml_file = file(os.path.expanduser(FILENAME))
        fcntl.lockf(xml_file,fcntl.LOCK_SH)

        self.recent_files = None

        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.ParseFile(xml_file)

        fcntl.lockf(xml_file,fcntl.LOCK_UN)
        xml_file.close()

    def get(self):
        return self.recent_files

    def startElement(self,tag,attrs):
        """
        Loads the dictionary when an XML tag of 'template' is found. The format
        XML tag is <template title=\"name\" file=\"path\">
        """

        self.tlist = []
        if tag == "RecentFiles":
            self.recent_files = []
        elif tag == "RecentItem":
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
