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

# -------------------------------------------------------------------------
#
# Standard Python Modules
#
# -------------------------------------------------------------------------
import os
import time
import logging
from xml.parsers.expat import ParserCreate, ExpatError

try:
    import fcntl

    USE_LOCK = True
except ImportError:
    USE_LOCK = False

from .const import USER_DATA, GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
GRAMPS_FILENAME = os.path.join(USER_DATA, "recent-files-gramps.xml")
MAX_GRAMPS_ITEMS = 10


# -------------------------------------------------------------------------
#
# RecentItem
#
# -------------------------------------------------------------------------
class RecentItem:
    """
    Interface to a single Gramps recent-items item
    """

    def __init__(self, p="", n="", t=0):
        self.path = p
        self.name = n
        self.time = t

    def set_path(self, val):
        """
        Set the file path.
        """
        self.path = val

    def get_path(self):
        """
        Get the file path.
        """
        return self.path

    def set_name(self, val):
        """
        Set the file name.
        """
        self.name = val

    def get_name(self):
        """
        Get the file name.
        """
        return self.name

    def set_time(self, val):
        """
        Set the file timestamp.
        """
        self.time = int(val)

    def get_time(self):
        """
        Get the file timestamp.
        """
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


# -------------------------------------------------------------------------
#
# RecentFiles
#
# -------------------------------------------------------------------------
class RecentFiles:
    """
    Interface to a RecentFiles collection
    """

    def __init__(self):
        gramps_parser = RecentParser()
        self.gramps_recent_files = gramps_parser.get()

    def add(self, item2add):
        """
        Add a file to the recent files list.
        """
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
        self.gramps_recent_files.insert(0, item2add)

    def rename_filename(self, filename, new_filename):
        """
        Rename a file in the recent files list.
        """
        for recent_file in self.gramps_recent_files:
            if recent_file.get_name() == filename:
                recent_file.set_name(new_filename)
                return

    def remove_filename(self, filename):
        """
        Remove a file from the recent files list.
        """
        for index, recent_file in enumerate(self.gramps_recent_files):
            if recent_file.get_name() == filename:
                self.gramps_recent_files.pop(index)
                return

    def check_if_recent(self, filename):
        """
        Check if a file is present in the recent files list.
        """
        return any(
            filename == recent_file.get_name()
            for recent_file in self.gramps_recent_files
        )

    def save(self):
        """
        Attempt saving into XML.
        The trick is not to fail under any circumstances.
        """
        fname = os.path.expanduser(GRAMPS_FILENAME)
        try:
            self.do_save(fname)
        except IOError as err:
            logging.warning(
                _("Unable to save list of recent DBs file {fname}: {error}").format(
                    fname=fname, error=err
                )
            )

    def do_save(self, fname):
        """
        Saves the current Gramps RecentFiles collection to the associated file.
        """
        with open(fname, "w", encoding="utf8") as xml_file:
            if USE_LOCK:
                fcntl.lockf(xml_file, fcntl.LOCK_EX)
            xml_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            xml_file.write("<RecentFiles>\n")
            for index, item in enumerate(self.gramps_recent_files):
                if index > MAX_GRAMPS_ITEMS:
                    break
                xml_file.write("  <RecentItem>\n")
                xml_file.write("    <Path><![CDATA[%s]]></Path>\n" % item.get_path())
                xml_file.write("    <Name><![CDATA[%s]]></Name>\n" % item.get_name())
                xml_file.write("    <Timestamp>%d</Timestamp>\n" % item.get_time())
                xml_file.write("  </RecentItem>\n")
            xml_file.write("</RecentFiles>\n")

        # all advisory locks on a file are released on close


# -------------------------------------------------------------------------
#
# RecentParser
#
# -------------------------------------------------------------------------
class RecentParser:
    """
    Parsing class for the RecentFiles collection.
    """

    def __init__(self):
        self.recent_files = []
        self.tlist = []
        self.item = None

        fname = os.path.expanduser(GRAMPS_FILENAME)
        if not os.path.exists(fname):
            return  # it's the first time gramps has ever been run

        try:
            with open(fname, "rb") as xml_file:
                if USE_LOCK:
                    fcntl.lockf(xml_file, fcntl.LOCK_SH)

                parser = ParserCreate()
                parser.StartElementHandler = self.start_element
                parser.EndElementHandler = self.end_element
                parser.CharacterDataHandler = self.characters
                parser.ParseFile(xml_file)
            # all advisory locks on a file are released on close
        except IOError as err:
            logging.warning(
                _("Unable to open list of recent DBs file {fname}: {error}").format(
                    fname=fname, error=err
                )
            )
        except ExpatError as err:
            logging.error(
                _(
                    "Error parsing list of recent DBs from file {fname}: "
                    "{error}.\nThis might indicate a damage to your files.\n"
                    "If you're sure there is no problem with other files, "
                    "delete it, and restart Gramps."
                ).format(fname=fname, error=err)
            )

    def get(self):
        """
        Return a list of recent files.
        """
        return self.recent_files

    def start_element(self, tag, attrs):
        """
        Handler for XML start element.
        """
        self.tlist = []
        if tag == "RecentItem":
            self.item = RecentItem()

    def end_element(self, tag):
        """
        Handler for XML end element.
        """
        text = "".join(self.tlist)

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
        """
        Handler for XML character data.
        """
        self.tlist.append(data)


# -------------------------------------------------------------------------
#
# Helper functions
#
# -------------------------------------------------------------------------
def recent_files(filename, name):
    """
    Add an entry to the Gramps recent items list.
    """
    the_time = int(time.time())
    gramps_rf = RecentFiles()
    gramps_item = RecentItem(p=filename, n=name, t=the_time)
    gramps_rf.add(gramps_item)
    gramps_rf.save()


def remove_filename(filename):
    """
    Remove an entry from the Gramps recent items list.
    """
    gramps_rf = RecentFiles()
    gramps_rf.remove_filename(filename)
    gramps_rf.save()


def rename_filename(filename, new_filename):
    """
    Rename an entry in the Gramps recent items list.
    """
    gramps_rf = RecentFiles()
    gramps_rf.rename_filename(filename, new_filename)
    gramps_rf.save()


def check_if_recent(filename):
    """
    Check if an entry is present in Gramps recent items list.
    """
    gramps_rf = RecentFiles()
    return gramps_rf.check_if_recent(filename)
