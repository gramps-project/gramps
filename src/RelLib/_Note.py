#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------
import re
import new

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BasicPrimaryObject import BasicPrimaryObject
from _NoteType import NoteType
from MarkupText import ROOT_START_TAG, LEN_ROOT_START_TAG
from _MarkerType import MarkerType

#-------------------------------------------------------------------------
#
# Class for notes used throughout the majority of GRAMPS objects
#
#-------------------------------------------------------------------------
class Note(BasicPrimaryObject):
    """
    Introduction
    ============
    The Note class defines a text note. The note may be preformatted
    or 'flowed', which indicates that it text string is considered
    to be in paragraphs, separated by newlines.
    """
    
    FLOWED    = 0
    FORMATTED = 1

    def __init__(self, text = ""):
        """
        Creates a new Note object, initializing from the passed string.
        """
        BasicPrimaryObject.__init__(self)
        self.text = text
        self.format = Note.FLOWED
        self.type = NoteType()

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (self.handle, self.gramps_id, self.text, self.format,
                self.type.serialize(), self.change, self.marker.serialize(),
                self.private)

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (self.handle, self.gramps_id, self.text, self.format,
         the_type, self.change, the_marker, self.private) = data

        self.marker = new.instance(MarkerType, None)
        self.marker.unserialize(the_marker)
        self.type = new.instance(NoteType, None)
        self.type.unserialize(the_type)

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.delete_tags(self.text)]

    def set(self, text):
        """
        Sets the text associated with the note to the passed string.

        @param text: Text string defining the note contents.
        @type text: str
        """
        self.text = text

    def get(self, markup=False):
        """
        Return the text string associated with the note.

        @param markup: If note should be returned with markup or plain text
        @type markup: boolean
        @returns: Returns the text string defining the note contents.
        @rtype: str
        """
        text = self.text

        if not markup and text[0:LEN_ROOT_START_TAG] == ROOT_START_TAG:
            text = self.delete_tags(text)
        
        return text
            
    def delete_tags(self, markup_text):
        """
        Creates a plain text version of the note text by removing all 
        pango markup tags.

        @param markup_text: Pango style markup text
        @type markup_text: str
        @return: Plain text
        @rtype: str
        """
        text = re.sub(r'(<.*?>)', '', markup_text)
        
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text

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

    def set_type(self, the_type):
        """
        @param the_type: descriptive type of the Note
        @type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        @returns: the descriptive type of the Note
        @rtype: str
        """
        return self.type

if __name__ == "__main__":
    import hotshot
    prof = hotshot.Profile("note.profile")

    f = open("notetest3_10.txt")
    note = Note(f.read())

    for i in range(100000):
        prof.runcall(note.get)
    prof.close()
