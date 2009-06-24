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
Note class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.primaryobj import BasicPrimaryObject
from gen.lib.notetype import NoteType
from gen.lib.markertype import MarkerType
from gen.lib.styledtext import StyledText

#-------------------------------------------------------------------------
#
# Class for notes used throughout the majority of GRAMPS objects
#
#-------------------------------------------------------------------------
class Note(BasicPrimaryObject):
    """Define a text note.
    
    Starting from GRAMPS 3.1 Note object stores the text in :class:`gen.lib.styledtext.StyledText`
    instance, thus it can have text formatting information.

    To get and set only the clear text of the note use the 
    :meth:`~gen.lib.note.Note.get` and :meth:`~gen.lib.note.Note.set` methods.
    
    To get and set the formatted version of the Note's text use the
    :meth:`~gen.lib.note.Note.get_styledtext` and 
    :meth:`~gen.lib.note.Note.set_styledtext` methods.
    
    The note may be 'preformatted' or 'flowed', which indicates that the
    text string is considered to be in paragraphs, separated by newlines.
    
    :cvar FLOWED: indicates flowed format
    :cvar FORMATTED: indicates formatted format (respecting whitespace needed)
    :cvar POS_<x>: (int) Position of <x> attribute in the serialized format of
        an instance.

    :attention: The POS_<x> class variables reflect the serialized object, they
        have to be updated in case the data structure or the 
        :meth:`~gen.lib.note.Note.serialize` method changes!
    
    """
    (FLOWED, FORMATTED) = range(2)
    
    (POS_HANDLE,
     POS_ID,
     POS_TEXT,
     POS_FORMAT,
     POS_TYPE,
     POS_CHANGE,
     POS_MARKER,
     POS_PRIVATE,) = range(8)

    def __init__(self, text=""):
        """Create a new Note object, initializing from the passed string."""
        BasicPrimaryObject.__init__(self)
        self.text = StyledText(text)
        self.format = Note.FLOWED
        self.type = NoteType()

    def serialize(self):
        """Convert the object to a serialized tuple of data.
        
        :returns: The serialized format of the instance.
        :rtype: tuple
        
        """
        return (self.handle, self.gramps_id, self.text.serialize(), self.format,
                self.type.serialize(), self.change, self.marker.serialize(),
                self.private)

    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.
        
        :param data: The serialized format of a Note.
        :type: data: tuple
        
        """
        (self.handle, self.gramps_id, the_text, self.format,
         the_type, self.change, the_marker, self.private) = data

        self.text = StyledText()
        self.text.unserialize(the_text)
        self.marker = MarkerType()
        self.marker.unserialize(the_marker)
        self.type = NoteType()
        self.type.unserialize(the_type)

    def get_text_data_list(self):
        """Return the list of all textual attributes of the object.

        :returns: The list of all textual attributes of the object.
        :rtype: list
        
        """
        return [str(self.text)]

    def set(self, text):
        """Set the text associated with the note to the passed string.

        :param text: The *clear* text defining the note contents.
        :type text: str
        
        """
        self.text = StyledText(text)

    def get(self):
        """Return the text string associated with the note.

        :returns: The *clear* text of the note contents.
        :rtype: str
        
        """
        return str(self.text)

    def set_styledtext(self, text):
        """Set the text associated with the note to the passed string.

        :param text: The *formatted* text defining the note contents.
        :type text: :class:`gen.lib.styledtext.StyledText`
        
        """
        self.text = text
        
    def get_styledtext(self):
        """Return the text string associated with the note.

        :returns: The *formatted* text of the note contents.
        :rtype: :class:`gen.lib.styledtext.StyledText`
        
        """
        return self.text
    
    def append(self, text):
        """Append the specified text to the text associated with the note.

        :param text: Text string to be appended to the note.
        :type text: str or :class:`gen.lib.styledtext.StyledText`
        
        """
        self.text = self.text + text

    def set_format(self, format):
        """Set the format of the note to the passed value. 
        
        :param format: The value can either indicate Flowed or Preformatted.
        :type format: int
        
        """
        self.format = format

    def get_format(self):
        """Return the format of the note. 
        
        The value can either indicate Flowed or Preformatted.

        :returns: 0 indicates Flowed, 1 indicates Preformated
        :rtype: int

        """
        return self.format

    def set_type(self, the_type):
        """Set descriptive type of the Note.
        
        :param the_type: descriptive type of the Note
        :type the_type: str

        """
        self.type.set(the_type)

    def get_type(self):
        """Get descriptive type of the Note.
        
        :returns: the descriptive type of the Note
        :rtype: str

        """
        return self.type
