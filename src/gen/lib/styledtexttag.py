#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"Provide formatting tag definition for StyledText."

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.styledtexttagtype import StyledTextTagType

#-------------------------------------------------------------------------
#
# StyledTextTag class
#
#-------------------------------------------------------------------------
class StyledTextTag(object):
    """Hold formatting information for StyledText.
    
    StyledTextTag is a container class, it's attributes are directly accessed.
    
    @ivar name: Type (or name) of the tag instance. E.g. 'bold', etc.
    @type name: L{gen.lib.StyledTextTagType} instace
    @ivar value: Value of the tag. E.g. color hex string for font color, etc.
    @type value: str or None
    @ivar ranges: Pointer pairs into the string, where the tag applies.
    @type ranges: list of (int(start), int(end)) tuples.
    
    """
    def __init__(self, name=None, value=None, ranges=None):
        """Setup initial instance variable values.
        
        @note: Since L{GrampsType} supports the instance initialization
        with several different base types, please note that C{name} parameter
        can be int, str, unicode, tuple, or even another L{StyledTextTagType}
        instance.
        
        """
        self.name = StyledTextTagType(name)
        self.value = value
        if ranges is None:
            self.ranges = []
        else:
            self.ranges = ranges

    def serialize(self):
        """Convert the object to a serialized tuple of data.
       
        @returns: Serialized format of the instance.
        @returntype: tuple
        
        """
        return (self.name.serialize(), self.value, self.ranges)
    
    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.
       
        @param data: Serialized format of instance variables.
        @type data: tuple
        
        """
        (the_name, self.value, self.ranges) = data
        
        self.name = StyledTextTagType()
        self.name.unserialize(the_name)
