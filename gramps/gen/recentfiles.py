#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2013       Vassilii Khachaturov
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import time
import io
import logging
from xml.parsers.expat import ParserCreate

try:
    import fcntl
    use_lock = True
except:
    use_lock = False

from gramps.gen.const import HOME_DIR, GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GRAMPS_FILENAME = os.path.join(HOME_DIR,"recent-files-gramps.xml")
MAX_GRAMPS_ITEMS = 10

#-------------------------------------------------------------------------
#
# RecentItem
#
#-------------------------------------------------------------------------
class RecentItem(object):
    """
    Interface to a single Gramps recent-items item
    """

    def __init__(self,p="", n="",t=0):
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

    def __eq__(self, other_item):
        return self.time == other_item.time

    def __ne__(self, other_item):
        return self.time != other_item.time

    def __lt__(self, other_item):
        return self.time < other_item.time

    def __gt__(self, other_item):
        return self.time > other_item.time

    def __le__(self, other_item):
        return self.time <= other_item.time

    def __ge__(self, other_item):
        return self.time >= other_item.time

##    Python 3, no __cmp__
##    def __cmp__(self, other_item):
##        return cmp(self.time, other_item.time)

#-------------------------------------------------------------------------
#
# RecentFiles
#
#-------------------------------------------------------------------------
class RecentFiles(object):
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



    def rename_filename(self,filename, new_filename):
        # First we need to walk the existing items to see
        # if our item is already there
        found = False
        for index in range(len(self.gramps_recent_files)):
            if self.gramps_recent_files[index].get_name() == filename:
                # Found it -- break here and change that item
                found = True
                break
        if found:
            self.gramps_recent_files[index].set_name(new_filename)

    def remove_filename(self,filename):
        # First we need to walk the existing items to see
        # if our item is already there
        found = False
        for index in range(len(self.gramps_recent_files)):
            if self.gramps_recent_files[index].get_name() == filename:
                # Found it -- break here and pop that item
                found = True
                break
        if found:
            self.gramps_recent_files.pop(index)


    def check_if_recent(self,filename):
        # First we need to walk the existing items to see
        # if our item is already there
        found = False
        for index in range(len(self.gramps_recent_files)):
            if self.gramps_recent_files[index].get_name() == filename:
                # Found it -- break here and pop that item
                found = True
                break
        return found

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
        Saves the current Gramps RecentFiles collection to the associated file.
        """
        with open(os.path.expanduser(GRAMPS_FILENAME), 'w', encoding='utf8') \
            as xml_file:
            if use_lock:
                fcntl.lockf(xml_file,fcntl.LOCK_EX)
            xml_file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            xml_file.write('<RecentFiles>\n')
            index = 0
            for item in self.gramps_recent_files:
                index += 1
                if index > MAX_GRAMPS_ITEMS:
                    break
                xml_file.write('  <RecentItem>\n')
                xml_file.write('    <Path><![CDATA[%s]]></Path>\n' % item.get_path())
                xml_file.write('    <Name><![CDATA[%s]]></Name>\n' % item.get_name())
                xml_file.write('    <Timestamp>%d</Timestamp>\n' % item.get_time())
                xml_file.write('  </RecentItem>\n')
            xml_file.write('</RecentFiles>\n')

        # all advisory locks on a file are released on close

#-------------------------------------------------------------------------
#
# RecentParser
#
#-------------------------------------------------------------------------
class RecentParser(object):
    """
    Parsing class for the RecentFiles collection.
    """

    def __init__(self):
        self.recent_files = []

        fname = os.path.expanduser(GRAMPS_FILENAME)
        if not os.path.exists(fname):
            return # it's the first time gramps has ever been run

        try:
            with open(fname, "rb") as xml_file:
                if use_lock:
                    fcntl.lockf(xml_file,fcntl.LOCK_SH)

                p = ParserCreate()
                p.StartElementHandler = self.startElement
                p.EndElementHandler = self.endElement
                p.CharacterDataHandler = self.characters
                p.ParseFile(xml_file)
            # all advisory locks on a file are released on close
        except IOError as err:
            logging.warning(
                    _("Unable to open list of recent DBs file {fname}: {error}"
                        ).format(fname=fname, error=err))
        except Exception as err:
            logging.error(
                    _("Error parsing list of recent DBs from file {fname}: {error}.\n"
                        "This might indicate a damage to your files.\n"
                        "If you're sure there is no problem with other files, "
                        "delete it, and restart Gramps."
                        ).format(fname=fname, error=err))

    def get(self):
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
def recent_files(filename, name):
    """
    Add an entry to both GNOME and Gramps recent-items storages.
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

def rename_filename(filename, new_filename):
    gramps_rf = RecentFiles()
    gramps_rf.rename_filename(filename, new_filename)
    gramps_rf.save()

def check_if_recent(filename):
    gramps_rf = RecentFiles()
    return gramps_rf.check_if_recent(filename)

