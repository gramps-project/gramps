#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Note class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject

#-------------------------------------------------------------------------
#
# Class for notes used throughout the majority of GRAMPS objects
#
#-------------------------------------------------------------------------
class Note(SecondaryObject):
    """
    Introduction
    ============
    The Note class defines a text note. The note may be preformatted
    or 'flowed', which indicates that it text string is considered
    to be in paragraphs, separated by newlines.
    """
    
    def __init__(self, text = ""):
        """
        Creates a new Note object, initializing from the passed string.
        """
        SecondaryObject.__init__(self)
        self.text = text
        self.format = 0

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (self.text, self.format)

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        if data:
            (self.text, self.format) = data
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.text]

    def set(self, text):
        """
        Sets the text associated with the note to the passed string.

        @param text: Text string defining the note contents.
        @type text: str
        """
        self.text = text

    def get(self):
        """
        Return the text string associated with the note.
        @returns: Returns the text string defining the note contents.
        @rtype: str
        """
        return self.text

    def append(self, text):
        """
        Appends the specified text to the text associated with the note.

        @param text: Text string to be appended to the note.
        @type text: str
        """
        self.text = self.text + text

    def set_format(self, format):
        """
        Sets the format of the note to the passed value. The value can
        either indicate Flowed or Preformatted.

        @param format: 0 indicates Flowed, 1 indicates Preformated
        @type format: int
        """
        self.format = format

    def get_format(self):
        """
        Returns the format of the note. The value can either indicate
        Flowed or Preformatted.

        @returns: 0 indicates Flowed, 1 indicates Preformated
        @rtype: int
        """
        return self.format

