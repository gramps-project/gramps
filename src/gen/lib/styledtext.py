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

"Handling formatted ('rich text') strings"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.styledtexttag import StyledTextTag

#-------------------------------------------------------------------------
#
# StyledText class
#
#-------------------------------------------------------------------------
class StyledText(object):
    """Helper class to enable character based text formatting.
    
    
    @ivar string: The clear text part.
    @type string: str
    @ivar tags: Text tags holding formatting information for the string.
    @type tags: list of L{StyledTextTag}

    @cvar POS_TEXT: Position of I{string} attribute in the serialized format of
    an instance.
    @type POS_TEXT: int
    @cvar POS_TAGS: Position of I{tags} attribute in the serialized format of
    an instance.
    @type POS_TAGS: int

    @attention: The POS_<x> class variables reflect the serialized object, they
    have to be updated in case the data structure or the L{serialize} method
    changes!
      
    """
    ##StyledText provides interface 
    ##Provide interface for:
    ##- tag manipulation for editor access:
      ##. get_tags
      ##. set_tags
    ##- explicit formatting for reports; at the moment:
      ##. start_bold() - end_bold()
      ##. start_superscript() - end_superscript()

    (POS_TEXT, POS_TAGS) = range(2)
    
    def __init__(self, text="", tags=None):
        """Setup initial instance variable values."""
        self._string = text
        # TODO we might want to make simple sanity check first
        if tags:
            self._tags = tags
        else:
            self._tags = []

    # special methods
    
    def __str__(self): return self._string.__str__()
    def __repr__(self): return self._string.__repr__()

    def __add__(self, other):
        if isinstance(other, StyledText):
            # FIXME merging tags missing
            return self.__class__("".join([self._string, other.string]))
        elif isinstance(other, basestring):
            # in this case tags remain the same, only text becomes longer
            return self.__class__("".join([self._string, other]))
        else:
            return self.__class__("".join([self._string, str(other)]))

    # string methods in alphabetical order:

    def join(self, seq):
        # FIXME handling tags missing
        return self.__class__(self._string.join(seq))
    
    def replace(self, old, new, maxsplit=-1):
        # FIXME handling tags missing
        return self.__class__(self._string.replace(old, new, maxsplit))
    
    def split(self, sep=None, maxsplit=-1):
        # FIXME handling tags missing
        string_list = self._string.split(sep, maxsplit)
        return [self.__class__(string) for string in string_list]

    # other public methods
    
    def serialize(self):
        """Convert the object to a serialized tuple of data.
        
        @returns: Serialized format of the instance.
        @returntype: tuple
        
        """
        if self._tags:
            the_tags = [tag.serialize() for tag in self._tags]
        else:
            the_tags = []
            
        return (self._string, the_tags)
    
    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.
        
        @param data: Serialized format of instance variables.
        @type data: tuple
        
        """
        (self._string, the_tags) = data
        
        # I really wonder why this doesn't work... it does for all other types
        #self._tags = [StyledTextTag().unserialize(tag) for tag in the_tags]
        for tag in the_tags:
            gtt = StyledTextTag()
            gtt.unserialize(tag)
            self._tags.append(gtt)
    
    def get_tags(self):
        """Return the list of formatting tags.
        
        @returns: The formatting tags applied on the text.
        @returntype: list of 0 or more L{StyledTextTag} instances.
        
        """
        return self._tags
    
    ##def set_tags(self, tags):
        ##"""Set all the formatting tags at once.
        
        ##@param tags: The formatting tags to be applied on the text.
        ##@type tags: list of 0 or more StyledTextTag instances.
        
        ##"""
        ### TODO we might want to make simple sanity check first
        ##self._tags = tags
        

if __name__ == '__main__':
    GT = StyledText("asbcde")
    print GT