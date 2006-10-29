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
Url class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _PrivacyBase import PrivacyBase
from _UrlType import UrlType

#-------------------------------------------------------------------------
#
# Url for Person/Place/Repository
#
#-------------------------------------------------------------------------
class Url(SecondaryObject,PrivacyBase):
    """Contains information related to internet Uniform Resource Locators,
    allowing gramps to store information about internet resources"""

    def __init__(self,source=None):
        """creates a new URL instance, copying from the source if present"""
        SecondaryObject.__init__(self)
        PrivacyBase.__init__(self,source)
        if source:
            self.path = source.path
            self.desc = source.desc
            self.type = source.type
        else:
            self.path = ""
            self.desc = ""
            self.type = UrlType()

    def serialize(self):
        return (self.private,self.path,self.desc,self.type.serialize())

    def unserialize(self,data):
        (self.private,self.path,self.desc,type_value) = data
        self.type.unserialize(type_value)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.path,self.desc]

    def set_path(self,path):
        """sets the URL path"""
        self.path = path

    def get_path(self):
        """returns the URL path"""
        return self.path

    def set_description(self,description):
        """sets the description of the URL"""
        self.desc = description

    def get_description(self):
        """returns the description of the URL"""
        return self.desc

    def set_type(self,the_type):
        """
        @param the_type: descriptive type of the Url
        @type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        @returns: the descriptive type of the Url
        @rtype: str
        """
        return self.type

    def are_equal(self,other):
        warn( "Use is_equal instead of are_equal", DeprecationWarning, 2)
        return self.is_equal(other)
