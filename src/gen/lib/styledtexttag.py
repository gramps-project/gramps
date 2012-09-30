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
from styledtexttagtype import StyledTextTagType

#-------------------------------------------------------------------------
#
# StyledTextTag class
#
#-------------------------------------------------------------------------
class StyledTextTag(object):
    """Hold formatting information for StyledText.
    
    StyledTextTag is a container class, it's attributes are directly accessed.
    
    @ivar name: Type (or name) of the tag instance. E.g. 'bold', etc.
    :type name: :class:`~gen.lib.styledtexttagtype.StyledTextTagType` instace
    @ivar value: Value of the tag. E.g. color hex string for font color, etc.
    :type value: str or None
    @ivar ranges: Pointer pairs into the string, where the tag applies.
    :type ranges: list of (int(start), int(end)) tuples.
    
    """
    def __init__(self, name=None, value=None, ranges=None):
        """Setup initial instance variable values.
        
        @note: Since :class:`~gen.lib.grampstype.GrampsType` supports the instance initialization
        with several different base types, please note that C{name} parameter
        can be int, str, unicode, tuple, or even another L{StyledTextTagType}
        instance.
        
        """
        self.name = StyledTextTagType(name)
        self.value = value
        if ranges is None:
            self.ranges = []
        else:
            # Current use of StyledTextTag is such that a shallow copy suffices.
            self.ranges = ranges

    def serialize(self):
        """Convert the object to a serialized tuple of data.
       
        :returns: Serialized format of the instance.
        :returnstype: tuple
        
        """
        return (self.name.serialize(), self.value, self.ranges)
    
    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"name": self.name.to_struct(), 
                "value": self.value, 
                "ranges": self.ranges}
    
    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.
       
        :param data: Serialized format of instance variables.
        :type data: tuple
        
        """
        (the_name, self.value, self.ranges) = data
        
        self.name = StyledTextTagType()
        self.name.unserialize(the_name)
        return self
