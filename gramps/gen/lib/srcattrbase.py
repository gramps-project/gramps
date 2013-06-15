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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
SrcAttributeBase class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .attrbase import AttributeRootBase
from .srcattribute import SrcAttribute
from .srcattrtype import SrcAttributeType

#-------------------------------------------------------------------------
#
#  SrcAttributeBase class
#
#-------------------------------------------------------------------------

class SrcAttributeBase(AttributeRootBase):
    _CLASS = SrcAttribute

    #------------------------------------------------------------------------
    #
    # Logical methods
    #
    #------------------------------------------------------------------------
    def get_source_template(self):
        """
        Return the source template of the source/citation
        This is the value of the first source template in the attribute list
        If not known UNKNOWN is returned as key, which is integer. Other keys
        will be str.
        :rtype tuple: (index, description, string_key_as stored)
        """
        #no template is UNKNOWN!
        templ = SrcAttributeType.UNKNOWN  
        for attr in self.attribute_list:
            if int(attr.get_type()) == SrcAttributeType.SRCTEMPLATE:
                val = attr.get_value()
                try:
                    templ = SrcAttributeType.K2I_SRCTEMPLATEMAP[val]
                except KeyError:
                    # a template not in the predefined list. convert to unknown
                    print ('SrcAttributeBase: Keyerror "', val,
                           '"for now UNKNOWN taken, later custom templates?')
                break
        try:
            retval = (templ, SrcAttributeType.I2S_SRCTEMPLATEMAP[templ], 
                       SrcAttributeType.I2K_SRCTEMPLATEMAP[templ])
        except KeyError:
            #templ is not present, return the default GEDCOM value as actual
            #template
            templ = SrcAttributeType.UNKNOWN
            retval = (templ, 
                      SrcAttributeType.I2S_SRCTEMPLATEMAP[SrcAttributeType.UNKNOWN], 
                      SrcAttributeType.I2K_SRCTEMPLATEMAP[SrcAttributeType.UNKNOWN])
        return retval

    def set_source_template(self, tempindex, tempcustom_str):
        """
        Set the source template of the source/citation
        This is the value of the first source template in the attribute list
        If tempindex is UNKNOWN, the template is removed.
        If tempindex is not CUSTOM, string value of tempindex is stored.
        Otherwise, the user given string value tempcustom_str is stored
        :param tempindex: integer template key
        :param tempcustom_str: string of a custom key to use as value for 
            template
        """
        attrtemp = None
        for attr in self.attribute_list:
            if int(attr.get_type()) == SrcAttributeType.SRCTEMPLATE:
                #we update the existing template
                attrtemp = attr
                break
        if attrtemp is None:
            #we create a new attribute and add it
            attrtemp = SrcAttribute()
            self.add_attribute(attrtemp)
        if tempindex == SrcAttributeType.UNKNOWN or \
        (tempindex == SrcAttributeType.CUSTOM and tempcustom_str.strip() == ''):
            self.remove_attribute(attrtemp)
        elif not (tempindex == SrcAttributeType.CUSTOM):
            attrtemp.set_value(SrcAttributeType.I2K_SRCTEMPLATEMAP[tempindex])
        else:
            #custom key, store string as is
            attrtemp.set_value(tempindex)
