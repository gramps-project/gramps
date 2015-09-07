#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
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

"""
Source Attribute class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .privacybase import PrivacyBase
from .citationbase import CitationBase
from .notebase import NoteBase
from .attribute import AttributeRoot
from .srcattrtype import SrcAttributeType
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Attribute for Source/Citation
#
#-------------------------------------------------------------------------
class SrcAttribute(AttributeRoot):
    """
    Provide a simple key/value pair for describing properties.
    Used to store descriptive information.
    """

    def __init__(self, source=None):
        """
        Create a new Attribute object, copying from the source if provided.
        """
        AttributeRoot.__init__(self, source)

        if source:
            self.type = SrcAttributeType(source.type)
            self.value = source.value
        else:
            self.type = SrcAttributeType()
            self.value = ""


    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        sat = SrcAttributeType()
        if self.type == sat.SRCTYPE:
            #we convert to the native language if possible
            if self.value and self.value in sat.E2I_SRCTYPEMAP:
                return [sat.I2S_SRCTYPEMAP[sat.E2I_SRCTYPEMAP[self.value]]]
        return [self.value]

